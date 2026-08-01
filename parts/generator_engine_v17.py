#!/usr/bin/env python3
"""ENGINE SET v17 — the winning mesh, rolled into the real machine.

Geometry basis (Ron's bench, finding #138): sun = 127_ballsun_slimcore form,
satellite mesh = 131_month_widesquare form. Cross-generation pair; it works
because both parts shrink 0.06/side when printed and that IS the backlash
(#138 law: a pair must clear AFTER shrink, not as-modelled).

NOT carved: #138's cleanup carve removed the residual graze but cost 1.9deg of
seat tightness at the strike (0.83mm lost motion vs 0.38). Per the #134 strike
law the seat matters more than the graze, so the sun ships UNCARVED, only CLOCKED.

Clocking (#134, sim-verified not derived):
  sun    — rotated so a VALLEY faces the strike line (world 0), square to the key
  month  — mesh lamina +18.07 deg     } so a seated phase coincides with each
  feb    — mesh lamina + 6.46 deg     } satellite's strike station
  leap   — mesh lamina +24.85 deg     }
Lost motion at strike 0.38mm against a 1.12mm drive window.

Fits (#136/#137): bores 2.70 on design-r2.70 posts, square bore 4.50 on the K4
key, hub boss doubling every bearing.
"""
import numpy as np, struct, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import Polygon, Point, LineString, MultiPolygon
from shapely.ops import polygonize, linemerge, unary_union
from shapely import affinity
import trimesh
from generator import cylinder, polar_solid, _poly_prism
from generator_v13 import write_stl
import generator_v13 as V13

CD = 23.75
SUN_ROT   = -19.50                     # valley -> strike line
ALPHA     = {"month": 18.07, "feb": 6.46, "leap": 24.85}
SQ_HW     = 2.25                       # square bore half-width (K4 key 4.42 design)
BORE      = 2.70                       # on the design-r2.70 satellite posts
SLIM_R    = 4.70                       # slim core at the finger altitudes
BAND_H    = 1.50                       # ball band height
PIECE_H   = 4.50                       # one tower piece (band + slim core)
ZM, ZS    = 1.50, 3.00                 # receiver mesh / strike lamina
TIP_R     = 18.30                      # finger reach
E1_BASE   = 6.0
d2r       = np.pi/180

def _slice(fn, zcut):
    with open(os.path.join("stl_v13", fn), "rb") as f:
        f.read(80); n = struct.unpack("<I", f.read(4))[0]
        T = np.zeros((n,3,3))
        for i in range(n):
            d = struct.unpack("<12fH", f.read(50)); T[i] = [d[3:6], d[6:9], d[9:12]]
    segs = []
    for tri in T:
        z = tri[:,2]
        if z.min() <= zcut <= z.max():
            pts = []
            for i in range(3):
                a, b = tri[i], tri[(i+1)%3]
                if (a[2]-zcut)*(b[2]-zcut) <= 0 and a[2] != b[2]:
                    t = (zcut-a[2])/(b[2]-a[2]); pts.append((a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])))
            if len(pts) >= 2: segs.append(pts[:2])
    return max(polygonize(linemerge([LineString(s) for s in segs])), key=lambda p: p.area)

def _extrude(poly, z0, z1, holes):
    p = Polygon(poly.simplify(0.02).exterior.coords, holes)
    m = trimesh.creation.extrude_polygon(p, z1-z0)
    return [tuple(np.array(v)+np.array([0,0,z0]) for v in m.vertices[f]) for f in m.faces]

SQ = [(SQ_HW,SQ_HW),(-SQ_HW,SQ_HW),(-SQ_HW,-SQ_HW),(SQ_HW,-SQ_HW)]
RB = list(Point(0,0).buffer(BORE,48).exterior.coords)

def sun_piece():
    """ONE tower piece: clocked ball band (on the bed, no overhang) + slim core.
    Print x3, stack keyed on the square post -> bands land at the month/feb/leap
    mesh altitudes, slim cores at the finger altitudes."""
    sun = affinity.rotate(_slice("127_ballsun_slimcore_v16.stl", 2.0), SUN_ROT, origin=(0,0))
    tris  = _extrude(sun, 0.0, BAND_H, [SQ])                          # ball band
    tris += polar_solid(SLIM_R, BAND_H, PIECE_H, r_inner=0.0, seg=64) # slim core (shrinks upward)
    # re-cut the square bore through the slim core
    tris = [t for t in tris]
    slim = Polygon(Point(0,0).buffer(SLIM_R,64).exterior.coords, [SQ])
    m = trimesh.creation.extrude_polygon(slim, PIECE_H-BAND_H)
    tris = _extrude(sun, 0.0, BAND_H, [SQ]) + \
           [tuple(np.array(v)+np.array([0,0,BAND_H]) for v in m.vertices[f]) for f in m.faces]
    write_stl("140_sun_tower_piece_v17.stl", tris)
    return sun

def receiver(name, sat_name, n_fingers):
    """Mesh lamina (winning form, CLOCKED per #134) + hub boss + solid finger bars."""
    mon = affinity.rotate(_slice("131_month_widesquare_v16.stl", 1.5), ALPHA[sat_name], origin=(0,0))
    tris  = _extrude(mon, 0.0, ZM, [RB])                              # clocked mesh lamina
    tris += polar_solid(4.0, ZM, ZS, r_inner=BORE, seg=64)            # hub
    for k in range(n_fingers):                                        # solid finger bars (#110)
        a = (E1_BASE + k*30.0)*d2r; ad = np.degrees(a)
        rmid = (4.0+16.0)/2
        tris += _rbox(rmid*np.cos(a), rmid*np.sin(a), ad, 16.0-4.0, 4.5, ZM, ZS)
        rmt = (15.5+TIP_R)/2                                          # raised tip (#117)
        tris += _rbox(rmt*np.cos(a), rmt*np.sin(a), ad, TIP_R-15.5, 4.5, 2.2, ZS)
    tris += polar_solid(4.5, ZS, ZS+3.0, r_inner=BORE, seg=48)        # hub boss: bearing 3->6mm
    write_stl(name, tris)
    return mon

def _rbox(cx, cy, ang_deg, L, W, z0, z1):
    a = ang_deg*d2r; u = np.array([np.cos(a), np.sin(a)]); v = np.array([-u[1], u[0]])
    c = np.array([cx, cy])
    pts = [tuple(c + sx*u*L/2 + sy*v*W/2) for sx, sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
    return _poly_prism(pts, z0, z1)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sun = sun_piece()
    mons = {}
    mons["month"] = receiver("141_receiver_month_v17.stl", "month", 5)
    mons["feb"]   = receiver("142_receiver_feb_v17.stl",   "feb",   1)
    mons["leap"]  = receiver("143_receiver_leap_v17.stl",  "leap",  1)
    print("  engine set v17 emitted: 1 tower piece (print x3) + 3 clocked receivers")
