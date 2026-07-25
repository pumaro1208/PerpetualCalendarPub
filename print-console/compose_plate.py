"""Programmatic plate composition for Bambu Studio.

Builds a valid Bambu Studio project 3MF from STLs + a plate spec (JSON):
meshes embedded inline, per-part transforms, and the full machine/process/
filament configuration flattened from the Studio system presets and written
to Metadata/project_settings.config — so the CLI slices from embedded
presets, never external config JSONs.

After slicing, audit_sliced() parses the .gcode.3mf's embedded config and
refuses to stage on any mismatch with the spec.

Spec format (paths relative to the spec file):
{
  "name": "plate-01-drive-sliders",
  "machine":  "Bambu Lab P1S 0.4 nozzle",
  "process":  "0.20mm Standard @BBL X1C",
  "filament": "Bambu PLA Matte @BBL P1S 0.4 nozzle",
  "filament_colour": "#000000",
  "bed_type": "Textured PEI Plate",
  "overrides": {"wall_loops": "3", "sparse_infill_density": "25%"},
  "parts": [
    {"stl": "...", "position": "center-right"},
    {"stl": "...", "rotate_x": 180, "z_offset": -0.45,
     "position": "center-left"}
  ]
}
position: "center-left" | "center-right" | "center" | [x, y] (mm, plate
coords, 256x256 bed). Parts are dropped so min-Z sits on the bed, then
z_offset is applied.
"""

import hashlib
import json
import math
import struct
import subprocess
import tempfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

PROFILES = Path("/Applications/BambuStudio.app/Contents/Resources/profiles/BBL")
BAMBU_STUDIO = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
CACHE_DIR = Path(__file__).resolve().parent / "cache"
BED = 256.0
GAP = 12.0            # clearance between parts placed left/right of center

# watertight 10mm cube, outward winding — probe model for the preset merge
_CUBE_TRIS = [
    ((0, 0, 0), (0, 10, 0), (10, 10, 0)), ((0, 0, 0), (10, 10, 0), (10, 0, 0)),
    ((0, 0, 10), (10, 0, 10), (10, 10, 10)), ((0, 0, 10), (10, 10, 10), (0, 10, 10)),
    ((0, 0, 0), (10, 0, 0), (10, 0, 10)), ((0, 0, 0), (10, 0, 10), (0, 0, 10)),
    ((10, 10, 0), (0, 10, 0), (0, 10, 10)), ((10, 10, 0), (0, 10, 10), (10, 10, 10)),
    ((0, 10, 0), (0, 0, 0), (0, 0, 10)), ((0, 10, 0), (0, 0, 10), (0, 10, 10)),
    ((10, 0, 0), (10, 10, 0), (10, 10, 10)), ((10, 0, 0), (10, 10, 10), (10, 0, 10)),
]
def _facet_normal(a, b, c):
    u = [b[i] - a[i] for i in range(3)]
    v = [c[i] - a[i] for i in range(3)]
    n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2],
         u[0] * v[1] - u[1] * v[0]]
    l = math.sqrt(sum(x * x for x in n)) or 1.0
    return [x / l for x in n]


# Studio's loader rejects facets with zero normals
TINY_STL = (b"\0" * 80 + struct.pack("<I", len(_CUBE_TRIS))
            + b"".join(struct.pack("<12fH", *_facet_normal(*tri),
                                   *(c for v in tri for c in v), 0)
                       for tri in _CUBE_TRIS))


# ------------------------------------------------------------------ presets

def _preset_path(kind: str, name: str) -> Path:
    p = PROFILES / kind / f"{name}.json"
    if not p.is_file():
        raise FileNotFoundError(f"No system {kind} preset named {name!r} "
                                f"({p})")
    return p


def canonical_config(machine: str, process: str, filament: str) -> dict:
    """Full merged config for the preset triple, produced by the Bambu
    Studio CLI itself (so every key has the exact type the CLI expects).
    Cached per triple in cache/."""
    key = hashlib.sha1(f"{machine}|{process}|{filament}".encode()).hexdigest()[:16]
    cached = CACHE_DIR / f"canonical-{key}.json"
    if cached.is_file():
        return json.loads(cached.read_text())

    m, pr, f = (_preset_path("machine", machine),
                _preset_path("process", process),
                _preset_path("filament", filament))
    with tempfile.TemporaryDirectory(prefix="canon-") as td:
        stl = Path(td) / "probe.stl"
        stl.write_bytes(TINY_STL)
        out = Path(td) / "canon.3mf"
        proc = subprocess.run(
            [BAMBU_STUDIO,
             "--load-settings", f"{m};{pr}",
             "--load-filaments", str(f),
             "--export-3mf", out.name,
             "--outputdir", td,
             str(stl)],
            capture_output=True, text=True, timeout=300)
        if proc.returncode != 0 or not out.is_file():
            tail = "\n".join((proc.stdout + proc.stderr).splitlines()[-8:])
            raise RuntimeError(
                f"CLI preset merge failed (exit {proc.returncode}):\n{tail}")
        with zipfile.ZipFile(out) as z:
            cfg = json.loads(z.read("Metadata/project_settings.config"))

    # sanity: the CLI must actually have applied the named presets
    for label, got, want in (
            ("machine", cfg.get("printer_settings_id"), machine),
            ("process", cfg.get("print_settings_id"), process),
            ("filament", (cfg.get("filament_settings_id") or [None])[0],
             filament)):
        if got != want:
            raise RuntimeError(f"CLI ignored the {label} preset: merged "
                               f"config has {got!r}, wanted {want!r}")

    # The CLI merge resolves neither `inherits` chains nor the machine
    # preset's `include` directives; overlay both ourselves. Filament only:
    # blanket-overlaying machine/process trips the CLI's compatibility
    # check, and the print-critical gap is the filament chain (bed temps —
    # the CLI defaulted textured_plate_temp to 45 instead of PLA's 55).
    n = _overlay_flattened(cfg, "filament", filament)
    print(f"  (filament inheritance overlay corrected {n} keys)")
    _merge_included_gcode(cfg, machine)
    if "M620" not in cfg.get("machine_start_gcode", ""):
        raise RuntimeError("machine_start_gcode still lacks the AMS load "
                           "block (M620) after include resolution")

    CACHE_DIR.mkdir(exist_ok=True)
    cached.write_text(json.dumps(cfg, indent=2, sort_keys=True))
    return cfg


_META_KEYS = {"name", "inherits", "from", "instantiation", "setting_id",
              "type", "include", "info", "description",
              "compatible_printers", "compatible_printers_condition",
              "compatible_prints", "compatible_prints_condition",
              "upward_compatible_machine"}


def _flatten_chain(kind: str, name: str) -> dict:
    """Resolve a preset's `inherits` chain ourselves (child wins). The CLI's
    --load-settings/--load-filaments does NOT do this — it backfills generic
    defaults (e.g. textured_plate_temp 45 instead of PLA's 55)."""
    chain, cur, seen = [], name, set()
    while cur and cur not in seen:
        seen.add(cur)
        p = PROFILES / kind / f"{cur}.json"
        if not p.is_file():
            break
        d = json.loads(p.read_text())
        chain.append(d)
        cur = d.get("inherits")
    flat = {}
    for d in reversed(chain):
        flat.update(d)
    return {k: v for k, v in flat.items() if k not in _META_KEYS}


def _overlay_flattened(cfg: dict, kind: str, name: str) -> int:
    """Overlay true preset values onto the canonical config, coerced to the
    canonical shape per key. Returns count of changed keys."""
    changed = 0
    for k, v in _flatten_chain(kind, name).items():
        if k not in cfg:
            continue
        cur = cfg[k]
        if isinstance(cur, list):
            vv = v if isinstance(v, list) else [v]
            vv = (vv + vv * len(cur))[:len(cur)]      # broadcast/truncate
        else:
            vv = v[0] if isinstance(v, list) and v else v
        if vv != cur:
            cfg[k] = vv
            changed += 1
    return changed


def _merge_included_gcode(cfg: dict, machine: str) -> None:
    """Resolve `include` template files along the machine preset's
    inheritance chain (parent first, child wins) and overlay their keys
    (machine_start_gcode, machine_end_gcode, change_filament_gcode, …)."""
    chain, current, seen = [], machine, set()
    while current and current not in seen:
        seen.add(current)
        p = PROFILES / "machine" / f"{current}.json"
        if not p.is_file():
            break
        d = json.loads(p.read_text())
        chain.append(d)
        current = d.get("inherits")
    for d in reversed(chain):
        for inc in d.get("include", []):
            t = PROFILES / "machine" / f"{inc}.json"
            if not t.is_file():
                continue
            for k, v in json.loads(t.read_text()).items():
                if k not in ("name", "instantiation"):
                    cfg[k] = v


def build_project_settings(spec: dict) -> dict:
    cfg = canonical_config(spec["machine"], spec["process"],
                           spec["filament"])
    cfg["curr_bed_type"] = spec["bed_type"]
    cfg["filament_colour"] = [spec.get("filament_colour", "#000000")]
    for k, v in spec.get("overrides", {}).items():
        want = v if isinstance(v, str) else str(v)
        # preserve the canonical type for this key
        cfg[k] = [want] if isinstance(cfg.get(k), list) else want
    return cfg


# -------------------------------------------------------------------- mesh

def load_stl(path: Path):
    """Return (vertices [[x,y,z]...], triangles [[a,b,c]...])."""
    raw = path.read_bytes()
    tris = []
    if raw[:5].lower() == b"solid" and b"facet" in raw[:400]:
        cur = []
        for line in raw.decode(errors="replace").splitlines():
            line = line.strip()
            if line.startswith("vertex"):
                cur.append(tuple(float(t) for t in line.split()[1:4]))
                if len(cur) == 3:
                    tris.append(cur)
                    cur = []
    else:
        (n,) = struct.unpack_from("<I", raw, 80)
        off = 84
        for _ in range(n):
            v = struct.unpack_from("<12f", raw, off)
            tris.append([tuple(v[3:6]), tuple(v[6:9]), tuple(v[9:12])])
            off += 50
    verts, idx, faces = [], {}, []
    for tri in tris:
        face = []
        for p in tri:
            key = (round(p[0], 5), round(p[1], 5), round(p[2], 5))
            i = idx.get(key)
            if i is None:
                i = idx[key] = len(verts)
                verts.append(key)
            face.append(i)
        if face[0] != face[1] != face[2] != face[0]:
            faces.append(face)
    return verts, faces


def rot_matrix(rx=0.0, ry=0.0, rz=0.0):
    """Rotation matrix applying X, then Y, then Z (degrees)."""
    def rx_m(a): c, s = math.cos(a), math.sin(a); return [[1, 0, 0], [0, c, -s], [0, s, c]]
    def ry_m(a): c, s = math.cos(a), math.sin(a); return [[c, 0, s], [0, 1, 0], [-s, 0, c]]
    def rz_m(a): c, s = math.cos(a), math.sin(a); return [[c, -s, 0], [s, c, 0], [0, 0, 1]]
    def mul(a, b):
        return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)]
                for i in range(3)]
    m = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    for deg, f in ((rx, rx_m), (ry, ry_m), (rz, rz_m)):
        if deg:
            m = mul(f(math.radians(deg)), m)
    return m


def apply_m(m, p):
    return tuple(sum(m[i][k] * p[k] for k in range(3)) for i in range(3))


def bbox(verts):
    xs, ys, zs = zip(*verts)
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def check_grounded(verts, faces, tol=0.25):
    """Return descriptions of components that neither touch the bed nor
    rest on material below (gaps under `tol` — sub-layer-height — count
    as resting: the slicer squishes them onto the surface)."""
    parent = list(range(len(verts)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for f in faces:
        parent[find(f[0])] = find(f[1])
        parent[find(f[1])] = find(f[2])
    comp = {}
    for i in range(len(verts)):
        comp.setdefault(find(i), []).append(verts[i])
    z_floor = min(v[2] for v in verts)
    boxes = []
    for vs in comp.values():
        xs = [p[0] for p in vs]
        ys = [p[1] for p in vs]
        zs = [p[2] - z_floor for p in vs]
        boxes.append((min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
    problems = []
    for b in boxes:
        if b[4] <= 0.01:
            continue
        cov = 0.0
        for o in boxes:
            if o is b or o[5] < b[4] - tol or o[4] >= b[4]:
                continue
            ox = max(0.0, min(b[1], o[1]) - max(b[0], o[0]))
            oy = max(0.0, min(b[3], o[3]) - max(b[2], o[2]))
            cov = max(cov, ox * oy
                      / max((b[1] - b[0]) * (b[3] - b[2]), 1e-9))
        if cov < 0.5:
            problems.append(f"component at z {b[4]:.2f}..{b[5]:.2f} "
                            f"(x {b[0]:.1f}..{b[1]:.1f}) floats mid-air "
                            f"({cov:.0%} rests on material below)")
    return problems


def drop_midair_components(verts, faces):
    """Remove connected components that float in mid-air (no part material
    beneath them) — e.g. features modeled at assembly height. Returns
    (verts, faces, dropped_descriptions). Stacked-on-body pieces are kept."""
    parent = list(range(len(verts)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for f in faces:
        parent[find(f[0])] = find(f[1])
        parent[find(f[1])] = find(f[2])
    comp_ids = {}
    for i in range(len(verts)):
        comp_ids.setdefault(find(i), []).append(i)

    z_floor = min(v[2] for v in verts)
    boxes = {}
    for root, idxs in comp_ids.items():
        xs = [verts[i][0] for i in idxs]
        ys = [verts[i][1] for i in idxs]
        zs = [verts[i][2] - z_floor for i in idxs]
        boxes[root] = (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))

    def coverage(a, others):
        ax0, ax1, ay0, ay1, az0, _ = a
        area = (ax1 - ax0) * (ay1 - ay0)
        if not area:
            return 1.0
        best = 0.0
        for b in others:
            bx0, bx1, by0, by1, bz0, bz1 = b
            if bz1 < az0 - 0.05 or bz0 >= az0:
                continue
            ox = max(0.0, min(ax1, bx1) - max(ax0, bx0))
            oy = max(0.0, min(ay1, by1) - max(ay0, by0))
            best = max(best, ox * oy / area)
        return best

    dropped_roots, dropped_desc = set(), []
    for root, box in boxes.items():
        if box[4] <= 0.01:
            continue
        others = [b for r, b in boxes.items() if r != root]
        if coverage(box, others) < 0.3:
            dropped_roots.add(root)
            dropped_desc.append(
                f"z {box[4]:.1f}..{box[5]:.1f} at x {box[0]:.1f}..{box[1]:.1f}"
                f" y {box[2]:.1f}..{box[3]:.1f}")
    if not dropped_roots:
        return verts, faces, []

    keep = [i for r, idxs in comp_ids.items() if r not in dropped_roots
            for i in idxs]
    remap = {old: new for new, old in enumerate(sorted(keep))}
    new_verts = [verts[i] for i in sorted(keep)]
    new_faces = [[remap[a], remap[b], remap[c]] for a, b, c in faces
                 if a in remap and b in remap and c in remap]
    return new_verts, new_faces, dropped_desc


# ------------------------------------------------------------------ compose

def compose(spec_path: Path, out_path: Path) -> Path:
    spec = json.loads(spec_path.read_text())
    base = spec_path.parent

    parts = []
    for part in spec["parts"]:
        stl = (base / part["stl"]).resolve()
        verts, faces = load_stl(stl)
        m = rot_matrix(part.get("rotate_x", 0), part.get("rotate_y", 0),
                       part.get("rotate_z", 0))
        verts = [apply_m(m, v) for v in verts]
        if part.get("drop_midair"):
            verts, faces, dropped = drop_midair_components(verts, faces)
            for d in dropped:
                print(f"  dropped mid-air component from {stl.name}: {d}")
        elif (not part.get("allow_midair")
              and spec.get("overrides", {}).get("enable_support") != "1"):
            grounded_problems = check_grounded(verts, faces)
            if grounded_problems:
                raise SystemExit(
                    f"REFUSING to compose: {stl.name} has unprintable "
                    "mid-air geometry (supports not spec'd):\n  "
                    + "\n  ".join(grounded_problems)
                    + "\nFix the model, spec supports, or set "
                    "drop_midair/allow_midair on the part.")
        parts.append({"name": stl.name, "verts": verts, "faces": faces,
                      "spec": part})

    # placement: bake transforms into vertices, identity build items
    widths = {}
    for p in parts:
        lo, hi = bbox(p["verts"])
        widths[id(p)] = (lo, hi)
    for p in parts:
        lo, hi = widths[id(p)]
        w = hi[0] - lo[0]
        pos = p["spec"].get("position", "center")
        if pos == "center-right":
            cx = BED / 2 + GAP / 2 + w / 2
        elif pos == "center-left":
            cx = BED / 2 - GAP / 2 - w / 2
        elif pos == "center":
            cx = BED / 2
        else:
            cx = float(pos[0])
        cy = BED / 2 if isinstance(pos, str) else float(pos[1])
        dx = cx - (lo[0] + hi[0]) / 2
        dy = cy - (lo[1] + hi[1]) / 2
        dz = -lo[2] + float(p["spec"].get("z_offset", 0.0))
        p["verts"] = [(v[0] + dx, v[1] + dy, v[2] + dz) for v in p["verts"]]

    # 3D/3dmodel.model
    obj_xml, items, ms_objects, ms_instances, ms_assemble = [], [], [], [], []
    for i, p in enumerate(parts, start=1):
        vs = "".join(f'<vertex x="{v[0]:.5f}" y="{v[1]:.5f}" z="{v[2]:.5f}"/>'
                     for v in p["verts"])
        ts = "".join(f'<triangle v1="{f[0]}" v2="{f[1]}" v3="{f[2]}"/>'
                     for f in p["faces"])
        obj_xml.append(
            f'<object id="{i}" type="model" name="{escape(p["name"])}">'
            f'<mesh><vertices>{vs}</vertices>'
            f'<triangles>{ts}</triangles></mesh></object>')
        items.append(f'<item objectid="{i}" '
                     f'transform="1 0 0 0 1 0 0 0 1 0 0 0" printable="1"/>')
        slot = p["spec"].get("extruder", 1)
        ms_objects.append(
            f'  <object id="{i}"><metadata key="name" '
            f'value="{escape(p["name"])}"/>'
            f'<metadata key="extruder" value="{slot}"/></object>')
        ms_instances.append(
            f'    <model_instance>\n'
            f'      <metadata key="object_id" value="{i}"/>\n'
            f'      <metadata key="instance_id" value="0"/>\n'
            f'      <metadata key="identify_id" value="{100 + i}"/>\n'
            f'    </model_instance>')
        ms_assemble.append(
            f'   <assemble_item object_id="{i}" instance_id="0" '
            f'transform="1 0 0 0 1 0 0 0 1 0 0 0" offset="0 0 0" />')

    model = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
        'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021">'
        '<metadata name="Application">BambuStudio-02.07.01.62</metadata>'
        '<metadata name="BambuStudio:3mfVersion">1</metadata>'
        f'<resources>{"".join(obj_xml)}</resources>'
        f'<build>{"".join(items)}</build></model>')

    model_settings = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n'
        + "\n".join(ms_objects) + "\n"
        '  <plate>\n'
        '    <metadata key="plater_id" value="1"/>\n'
        '    <metadata key="plater_name" value=""/>\n'
        '    <metadata key="locked" value="false"/>\n'
        + "\n".join(ms_instances) + "\n"
        '  </plate>\n'
        '  <assemble>\n' + "\n".join(ms_assemble) + "\n  </assemble>\n"
        '</config>\n')

    content_types = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/'
        'content-types">'
        '<Default Extension="rels" ContentType="application/vnd.'
        'openxmlformats-package.relationships+xml"/>'
        '<Default Extension="model" ContentType="application/vnd.ms-package.'
        '3dmanufacturing-3dmodel+xml"/></Types>')
    rels = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/'
        '2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel-1" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/'
        '3dmodel"/></Relationships>')

    cfg = build_project_settings(spec)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)
        z.writestr("Metadata/model_settings.config", model_settings)
        z.writestr("Metadata/project_settings.config",
                   json.dumps(cfg, indent=4, sort_keys=True))
    return out_path


def finalize_sliced(sliced: Path, spec: dict) -> None:
    """Re-stamp filament identity into the sliced 3mf. The slicer blanks
    filament_settings_id/filament_ids/tray_info_idx because our corrected
    config no longer matches its (broken) merge of the preset — restoring
    them re-enables the printer's own AMS RFID cross-check."""
    fil_id = spec.get("filament_id") or _flatten_chain(
        "filament", spec["filament"]).get("filament_id", "")
    with zipfile.ZipFile(sliced) as z:
        members = {n: z.read(n) for n in z.namelist()}
    cfg = json.loads(members["Metadata/project_settings.config"])
    cfg["filament_settings_id"] = [spec["filament"]]
    cfg["filament_ids"] = [fil_id]
    members["Metadata/project_settings.config"] = json.dumps(
        cfg, indent=4, sort_keys=True).encode()
    si = members["Metadata/slice_info.config"].decode()
    si = si.replace('tray_info_idx=""', f'tray_info_idx="{fil_id}"')
    members["Metadata/slice_info.config"] = si.encode()
    tmp = sliced.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for n, data in members.items():
            z.writestr(n, data)
    tmp.replace(sliced)


# -------------------------------------------------------------------- audit

def audit_sliced(sliced: Path, spec: dict) -> list:
    """Compare the sliced file's embedded config against the spec.
    Returns a list of mismatch strings (empty = pass)."""
    with zipfile.ZipFile(sliced) as z:
        cfg = json.loads(z.read("Metadata/project_settings.config"))
        gcode = z.read("Metadata/plate_1.gcode").decode(errors="replace")

    problems = []

    # the print must actually load filament: AMS load block + tool select
    if "M620" not in gcode:
        problems.append("gcode has no AMS load sequence (M620) — the "
                        "machine start gcode was not applied; the print "
                        "would run dry")
    import re as _re
    if not _re.search(r"^M620 S\d+A", gcode, _re.M):
        problems.append("gcode never issues an AMS filament switch "
                        "(M620 S<n>A) — no filament would be loaded")

    # brim: Bambu's slicer silently emits no brim when supports are on
    # (support bases take its place); only gate when supports are off
    ov = spec.get("overrides", {})
    if (ov.get("brim_type", "no_brim") != "no_brim"
            and ov.get("enable_support") != "1"
            and "; FEATURE: Brim" not in gcode):
        problems.append("brim requested but gcode contains no Brim feature")
    if (ov.get("enable_support") == "1"
            and "; FEATURE: Support interface" not in gcode):
        problems.append("supports requested but gcode contains no support "
                        "features")

    # per-object first-layer extrusion: every object on the plate must
    # actually receive material on layer 1 within its own bbox
    try:
        with zipfile.ZipFile(sliced) as z:
            pj = json.loads(z.read("Metadata/plate_1.json"))
        # every spec'd part must survive to the sliced plate — Bambu's
        # slicer silently drops objects it dislikes (seen: objects placed
        # at x≳200 on a shared plate vanish without any warning)
        sliced_names = {o.get("name") for o in pj.get("bbox_objects", [])}
        for p in spec.get("parts", []):
            stem = p["stl"].rsplit("/", 1)[-1]
            if stem not in sliced_names:
                problems.append(f"object {stem}: spec'd but ABSENT from the "
                                "sliced plate — the slicer silently dropped "
                                "it (check placement)")
        layer1 = gcode.split("; CHANGE_LAYER")[1] if "; CHANGE_LAYER" in gcode else ""
        moves = _re.findall(r"G1 X([\d.]+) Y([\d.]+) E[\d.]+", layer1)
        for obj in pj.get("bbox_objects", []):
            bb = obj.get("bbox")
            if not bb or obj.get("name", "").startswith("wipe"):
                continue
            n = sum(1 for x, y in moves
                    if bb[0] - 1 <= float(x) <= bb[2] + 1
                    and bb[1] - 1 <= float(y) <= bb[3] + 1)
            if n == 0:
                problems.append(f"object {obj.get('name')}: no first-layer "
                                "extrusion inside its bbox — it would print "
                                "on nothing")
    except KeyError:
        problems.append("plate_1.json missing — cannot verify per-object "
                        "extrusion")

    # bed temperature in the gcode must match the plate-temp key for the
    # spec'd bed type (the 45-vs-55 class of failure)
    bed_key = {"Cool Plate": "cool_plate_temp",
               "Engineering Plate": "eng_plate_temp",
               "High Temp Plate": "hot_plate_temp",
               "Textured PEI Plate": "textured_plate_temp"}.get(
                   spec["bed_type"])
    want_bed = spec.get("bed_temp")
    if want_bed is None and bed_key:
        v = cfg.get(bed_key)
        want_bed = int((v[0] if isinstance(v, list) else v) or 0)
    m = _re.search(r"^M140 S(\d+)", gcode, _re.M)
    got_bed = int(m.group(1)) if m else None
    if want_bed and got_bed != want_bed:
        problems.append(f"bed temperature: gcode sets {got_bed}°C, expected "
                        f"{want_bed}°C for {spec['bed_type']}")

    def expect(label, got, want):
        if got != want:
            problems.append(f"{label}: sliced file has {got!r}, "
                            f"spec requires {want!r}")

    expect("machine preset", cfg.get("printer_settings_id"), spec["machine"])
    expect("process preset", cfg.get("print_settings_id"), spec["process"])
    expect("plate type", cfg.get("curr_bed_type"), spec["bed_type"])
    fils = cfg.get("filament_settings_id", [])
    expect("filament preset", fils[0] if fils else None, spec["filament"])
    types = cfg.get("filament_type", [])
    expect("filament type", types[0] if types else None,
           spec.get("ams_tray_type", "PLA"))
    want_id = spec.get("filament_id") or _flatten_chain(
        "filament", spec["filament"]).get("filament_id", "")
    ids = cfg.get("filament_ids", [])
    if want_id:
        expect("filament id", ids[0] if ids else None, want_id)
    cols = cfg.get("filament_colour", [])
    want_col = spec.get("filament_colour", "#000000").upper()
    got_col = (cols[0] if cols else "").upper()
    if got_col != want_col:
        problems.append(f"filament colour: sliced file has {got_col!r}, "
                        f"spec requires {want_col!r}")
    for k, want in spec.get("overrides", {}).items():
        got = cfg.get(k)
        if isinstance(got, list):
            got = got[0] if got else None
        expect(f"override {k}", got,
               want if isinstance(want, str) else str(want))
    return problems


def find_ams_slot(print_data: dict, tray_type: str, sub_brand_contains: str,
                  colour: str):
    """Locate the AMS slot holding the required filament from live MQTT
    print data. Returns (ams_id, slot_id) or None."""
    want_col = colour.lstrip("#").upper()
    for unit in print_data.get("ams", {}).get("ams", []):
        for tray in unit.get("tray", []):
            if (tray.get("tray_type") == tray_type
                    and sub_brand_contains.lower()
                    in (tray.get("tray_sub_brands") or "").lower()
                    and (tray.get("tray_color") or "").upper()
                    .startswith(want_col)):
                return int(unit.get("id", 0)), int(tray.get("id", 0))
    return None
