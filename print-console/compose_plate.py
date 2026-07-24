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

    CACHE_DIR.mkdir(exist_ok=True)
    cached.write_text(json.dumps(cfg, indent=2, sort_keys=True))
    return cfg


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


# -------------------------------------------------------------------- audit

def audit_sliced(sliced: Path, spec: dict) -> list:
    """Compare the sliced file's embedded config against the spec.
    Returns a list of mismatch strings (empty = pass)."""
    with zipfile.ZipFile(sliced) as z:
        cfg = json.loads(z.read("Metadata/project_settings.config"))

    problems = []

    def expect(label, got, want):
        if got != want:
            problems.append(f"{label}: sliced file has {got!r}, "
                            f"spec requires {want!r}")

    expect("machine preset", cfg.get("printer_settings_id"), spec["machine"])
    expect("process preset", cfg.get("print_settings_id"), spec["process"])
    expect("plate type", cfg.get("curr_bed_type"), spec["bed_type"])
    fils = cfg.get("filament_settings_id", [])
    expect("filament preset", fils[0] if fils else None, spec["filament"])
    cols = cfg.get("filament_colour", [])
    want_col = spec.get("filament_colour", "#000000").upper()
    got_col = (cols[0] if cols else "").upper()
    if got_col != want_col:
        problems.append(f"filament colour: sliced file has {got_col!r}, "
                        f"spec requires {want_col!r}")
    for k, want in spec.get("overrides", {}).items():
        expect(f"override {k}", cfg.get(k),
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
