#!/usr/bin/env python3
"""#141 — WELD: turn a triangle soup of overlapping shells into one watertight solid.

Most parts here are authored as a pile of primitives (a slot is 24 overlapping
cylinders; the sun piece is a band shell abutting a core shell). That soup slices
fine, but it is not a manifold, so the watertight gate cannot say anything true
about it — and a gate that cannot fail is not a gate. Welding makes the whole
convention meaningful again: every emitted part is one closed solid or it fails.

Boolean union via manifold3d.
"""
import numpy as np, trimesh

def to_mesh(tris):
    V = np.asarray(tris, dtype=float).reshape(-1, 3)
    F = np.arange(len(V)).reshape(-1, 3)
    m = trimesh.Trimesh(vertices=V, faces=F, process=True)
    m.merge_vertices()
    m.update_faces(m.nondegenerate_faces())
    m.update_faces(m.unique_faces())
    return m

def to_tris(m):
    return [tuple(np.array(v) for v in m.vertices[f]) for f in m.faces]

def stack(slabs, allow_multi=False):
    """[(z0, z1, shapely polygon)] -> one watertight solid.

    Preferred over welding a soup of primitives: each slab is authored as a single
    2D union (cheap, exact, in the plane where the design intent lives) and only
    the vertical abutments go through the boolean. Overlapping-primitive soups make
    manifold do the hard case for no reason, and it sometimes hands back two bodies.
    """
    from shapely.geometry import Polygon, MultiPolygon
    ms = []
    for z0, z1, poly in slabs:
        if z1 - z0 <= 0 or poly.is_empty: continue
        geoms = list(poly.geoms) if isinstance(poly, MultiPolygon) else [poly]
        if len(geoms) > 1:
            # loose material in a slab is nearly always a mistake, not a feature
            areas = sorted((g.area for g in geoms), reverse=True)
            print(f"    ! slab {z0:.2f}-{z1:.2f} is {len(geoms)} disconnected pieces, "
                  f"areas {[round(a,3) for a in areas]}")
        for g in geoms:
            # 1 micron simplify: shapely unions leave duplicate/collinear vertices
            # that extrude into zero-area triangles, and the result reads as
            # "not a volume" even though it looks right. Well under print resolution.
            # Progressive cleanup. A shapely union leaves duplicate and collinear
            # vertices that extrude into zero-area triangles, and the result reads as
            # "not a volume" while looking perfectly correct. simplify clears most of
            # it; a tiny open-close clears the rest (self-touching rings). Both are
            # far under print resolution.
            m = None
            for clean in (lambda q: q.buffer(0).simplify(1e-3),
                          lambda q: q.buffer(0.002, 8).buffer(-0.002, 8).simplify(1e-4),
                          lambda q: q.buffer(0.01, 12).buffer(-0.01, 12)):
                try:
                    g2 = clean(g)
                    if g2.geom_type != "Polygon" or g2.is_empty: continue
                    p = Polygon(g2.exterior.coords, [r.coords for r in g2.interiors])
                    cand = trimesh.creation.extrude_polygon(p, z1-z0)
                    cand.apply_translation((0, 0, z0))
                    if cand.is_volume: m = cand; break
                except Exception:
                    continue
            if m is None:
                raise ValueError(f"slab {z0:.2f}-{z1:.2f} piece area {g.area:.4f} "
                                 f"({len(g.exterior.coords)} pts, {len(g.interiors)} holes) "
                                 f"will not extrude to a volume")
            ms.append(m)
    if len(ms) == 1 and not allow_multi:
        ms[0].fix_normals(); return to_tris(ms[0])
    u = trimesh.boolean.union(ms) if len(ms) > 1 else ms[0]
    if allow_multi:
        # a two-colour filler is legitimately many separate glyphs — the
        # one-solid rule is about parts, not about ink
        u = _clean(u); u.fix_normals(); return to_tris(u)
    return to_tris(_solid(u))

def _clean(m):
    """Drop zero-area (collinear) faces. manifold hands a few back on coincident
    slab walls; they are invisible in a render but they are what makes a part
    read as several bodies, so the watertight gate stays red until they go."""
    m.merge_vertices()
    keep = m.area_faces > 1e-9
    if not keep.all(): m.update_faces(keep)
    m.remove_unreferenced_vertices()
    return m

def _solid(u):
    u = _clean(u)
    """Keep the one real body; drop the zero-volume sheets manifold leaves behind
    on coincident faces. Anything with actual volume is NOT swept up quietly —
    two solid bodies in one part means the part is genuinely in two pieces."""
    parts = u.split(only_watertight=False)
    if len(parts) > 1:
        # A real body has POSITIVE volume. Below 1e-3mm^3 (a 0.1mm cube) it is a
        # boolean artifact; a NEGATIVE volume is an inverted shell manifold left
        # behind, which is also an artifact — but say so rather than swallowing it,
        # because a big negative body would mean the union genuinely went wrong.
        neg = [p for p in parts if p.volume < -1e-3]
        if neg:
            print(f"    ! dropped {len(neg)} inverted shell(s), volumes "
                  f"{[round(p.volume,2) for p in neg]}")
            if min(p.volume for p in neg) < -5.0:
                raise ValueError("a large inverted body means the union failed, "
                                 f"volumes {[round(p.volume,2) for p in neg]}")
        real = [p for p in parts if p.volume > 1e-3]
        if len(real) > 1:
            raise ValueError(f"part is {len(real)} disconnected solids, "
                             f"volumes {[round(p.volume,2) for p in real]}")
        u = real[0]
    u.fix_normals()
    return u

def weld(tris):
    """Union every disjoint shell in the soup into a single manifold."""
    m = to_mesh(tris)
    parts = m.split(only_watertight=False)
    if len(parts) <= 1:
        m.fix_normals(); return to_tris(m)
    return to_tris(_solid(trimesh.boolean.union(list(parts))))
