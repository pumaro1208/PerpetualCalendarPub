#!/usr/bin/env python3
"""Chewy-font name keychain generator.

Reconstructed from the design spec in claude-code-instructions.md — a clone of the
MakerWorld "Portachiavi Nome Parametrico Personalizzabile" (Stampa 3D AV Studio),
reverse-engineered from the Federico export.

Usage:  python3 make_keychain.py <NAME>
Needs:  chewy.ttf in the same folder, plus
        numpy shapely trimesh matplotlib manifold3d mapbox_earcut rtree fonttools brotli
Output: <NAME>.stl and <NAME>.3mf ; must report "watertight, 1 body".
"""
import sys
from functools import reduce

import numpy as np
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from shapely.geometry import Polygon, Point
from shapely.affinity import translate, scale
from shapely.ops import unary_union
from fontTools.ttLib import TTFont
import trimesh

FONT = "chewy.ttf"
SIZE = 100          # TextPath render size
MM = 0.305          # mm per TextPath unit  (=> ~17 mm cap height)
H_TALL, H_SHORT = 6.5, 4.5        # alternating letter heights
LOOP_OD, LOOP_HOLE, LOOP_TH = 10.14, 5.0, 4.5
OVL_LETTER = 2.5    # mm^2 min overlap between adjacent letters
OVL_LOOP = 4.0      # mm^2 min overlap loop <-> first letter
OVL_DOT = 1.5       # mm^2 min overlap i/j dot <-> its stem
ADV = 0.80          # advance multiplier (letters overlap)

_tt = TTFont(FONT)
_UPM = _tt["head"].unitsPerEm
_CMAP = _tt.getBestCmap()
_HMTX = _tt["hmtx"]
_FP = FontProperties(fname=FONT)


def advance_mm(ch):
    gn = _CMAP.get(ord(ch))
    aw = _HMTX[gn][0] if (gn and gn in _HMTX.metrics) else _UPM * 0.5
    return aw * (SIZE / _UPM) * MM


def glyph_geom(ch):
    """Even-odd filled shapely geometry for a glyph, scaled to mm, its left edge at x=0."""
    tp = TextPath((0, 0), ch, size=SIZE, prop=_FP)
    rings = [Polygon(c) for c in tp.to_polygons() if len(c) >= 3]
    rings = [r if r.is_valid else r.buffer(0) for r in rings]
    rings = [r for r in rings if not r.is_empty]
    if not rings:
        return None
    geom = reduce(lambda a, b: a.symmetric_difference(b), rings)
    geom = scale(geom, xfact=MM, yfact=MM, origin=(0, 0))
    # shift so the glyph's left extent sits at x=0
    minx = geom.bounds[0]
    return translate(geom, xoff=-minx)


def fuse_dot(geom):
    """If a glyph has a disjoint island above the stem (i/j dot), lower it to fuse."""
    if geom.geom_type != "MultiPolygon":
        return geom
    parts = sorted(geom.geoms, key=lambda p: -p.area)
    main = parts[0]
    out = [main]
    for d in parts[1:]:
        if d.centroid.y > main.centroid.y and d.intersection(main).area < OVL_DOT:
            moved = d
            for _ in range(600):
                moved = translate(moved, yoff=-0.1)
                if moved.intersection(main).area >= OVL_DOT:
                    break
            d = moved
        out.append(d)
    return unary_union(out)


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "Name"

    # --- place + fuse dots ---
    raw = []
    x = 0.0
    for ch in name:
        g = glyph_geom(ch)
        if g is None:
            x += advance_mm(ch) * ADV
            continue
        raw.append([fuse_dot(translate(g, xoff=x)), ch])
        x += advance_mm(ch) * ADV

    # --- nudge letters closer until adjacent overlap >= OVL_LETTER (moves this + all after) ---
    for i in range(1, len(raw)):
        while raw[i][0].intersection(raw[i - 1][0]).area < OVL_LETTER:
            for j in range(i, len(raw)):
                raw[j][0] = translate(raw[j][0], xoff=-0.1)
            if raw[i][0].bounds[0] < raw[i - 1][0].bounds[0] - 5:
                break  # safety

    # --- extrude letters with alternating heights ---
    meshes = []
    for idx, (geom, ch) in enumerate(raw):
        h = H_TALL if idx % 2 == 0 else H_SHORT
        polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
        for p in polys:
            meshes.append(trimesh.creation.extrude_polygon(p, h))

    # --- keyring loop: annulus, 1.5mm below word midline, slid right to overlap 1st letter ---
    ys = [g.bounds for g, _ in raw]
    word_mid = (min(b[1] for b in ys) + max(b[3] for b in ys)) / 2.0
    cy = word_mid - 1.5
    first = raw[0][0]
    lx = first.bounds[0] - LOOP_OD / 2.0        # start left of the first letter
    def annulus(cx):
        outer = Point(cx, cy).buffer(LOOP_OD / 2.0, resolution=64)
        hole = Point(cx, cy).buffer(LOOP_HOLE / 2.0, resolution=64)
        return outer.difference(hole)
    for _ in range(400):
        ring = annulus(lx)
        if ring.intersection(first).area >= OVL_LOOP:
            break
        lx += 0.1
    ring = annulus(lx)
    meshes.append(trimesh.creation.extrude_polygon(ring, LOOP_TH))

    # --- union everything into one solid ---
    body = trimesh.boolean.union(meshes, engine="manifold")
    body.merge_vertices()

    # --- center on a 256 plate ---
    body.apply_translation([128 - body.centroid[0], 128 - body.centroid[1], -body.bounds[0][2]])

    nbodies = len(body.split(only_watertight=False))
    print("%s: %.1f x %.1f x %.1f mm, watertight=%s, %d body(ies)"
          % (name, *(body.bounds[1] - body.bounds[0]), body.is_watertight, nbodies))
    body.export(name + ".stl")
    body.export(name + ".3mf")
    print("wrote %s.stl and %s.3mf" % (name, name))


if __name__ == "__main__":
    main()
