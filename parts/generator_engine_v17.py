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
from weld import weld, stack
import generator_v13 as V13

CD = 23.75
SUN_ROT   = -19.50                     # valley -> strike line
ALPHA     = {"month": 18.07, "feb": 6.46, "leap": 24.85}
SQ_HW     = 2.25                       # square bore half-width (K4 key 4.42 design)
BORE      = 2.70                       # on the design-r2.70 satellite posts
SLIM_R    = 4.70                       # slim core at the finger altitudes
BAND_H    = 1.50                       # ball band height
PIECE_H   = 6.50                       # one tower piece (band 1.5 + slim core 5.0)
                                       # #147 (Ron, bench): the piece height IS the band
                                       # pitch, and the pitch is what feeds the carrier
                                       # arm plates. 4.5 (#139) left no room for the pivot
                                       # pad; 5.0 (#141) fitted the pad but left the plate
                                       # at 1.30mm — and the plate thickness IS the entire
                                       # grip the arm has on its post, because the post has
                                       # to stop under the satellite above. 1.30 on a 2.70
                                       # post is 0.48 diameters with no shoulder to register
                                       # against; Ron could not get the arms to hold.
                                       # 6.50 gives a 2.80 plate = 1.04 post diameters, the
                                       # textbook figure for a press fit. Budget:
                                       #   3.00 satellite + 0.20 clearance
                                       # + 2.80 plate     + 0.50 pad  = 6.50
                                       # 5.0 is taken in the sun piece itself, NOT as
                                       # a stack of 0.5mm shims: a 0.5mm shim prints
                                       # at 2.5 layers (rounds to 0.4/0.6) and that
                                       # z error would walk the mesh lamina off its band.
ZM, ZS    = 1.50, 3.00                 # receiver mesh / strike lamina
TIP_R     = 18.30                      # finger reach
# #148 (Ron, bench: "1 is not at the top at the start of the month, 30 is").
# The strike-bar bearing at phi=0, PER SATELLITE. It was a single round 6.0 for all
# three since #110 and never checked against the calendar engine — but the three
# satellites strike on different dates (month 30, feb 29, leap 28), so their strike
# teeth cannot possibly share a bearing. Derived two independent ways that agree to
# three decimals: running the engine and recording the bearing each strike demands,
# and the geometric fact that one month is 31 steps = 570deg = exactly 19 teeth, so
# satellite phase mod 30 resets monthly and depends only on the date.
# Check: psi = (19/12)*(d-1)*PITCH + E1_BASE lands on 0 mod 30 at each strike date.
# The old 6.0 left feb 10.84deg out (3.43mm at the strike face, 306% of the 1.12mm
# drive window) and leap 7.55deg out (213%) — both would simply have MISSED, so
# February would never have been shortened and the leap tooth would never have fired.
E1_BASE   = {"month": 6.774, "feb": 25.161, "leap": 13.548}
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
    key = Polygon(SQ)
    write_stl("140_sun_tower_piece_v17.stl", stack([
        (0.0,    BAND_H,  sun.simplify(0.02).difference(key)),          # ball band, on the bed
        (BAND_H, PIECE_H, Point(0,0).buffer(SLIM_R,64).difference(key)) # slim core
    ]))
    return sun

def receiver(name, sat_name, n_fingers, boss_h=0.0):
    """Mesh lamina (winning form, CLOCKED per #134) + solid finger bars.

    #141 — the hub boss is NOT free. It was added to double the bearing (3->6mm),
    but a receiver seated in a 5.0mm band gap has 3.0mm of satellite + 0.5mm pad +
    1.3mm arm + clearances: there is no headroom above month or feb, and a 6mm
    receiver drives 2.8mm straight through the carrier arm above it. Only LEAP has
    open sky (nothing stacks above it), so only leap carries a boss. Month and feb
    revert to the 3.0mm bearing — which is exactly what Ron's bench-winning
    131_month_widesquare already has, running with no bind."""
    mon = affinity.rotate(_slice("131_month_widesquare_v16.stl", 1.5), ALPHA[sat_name], origin=(0,0))
    bore = Point(0,0).buffer(BORE, 48)
    hub  = Point(0,0).buffer(4.0, 64)
    bars, tips = [], []
    for k in range(n_fingers):                                        # solid finger bars (#110)
        a = (E1_BASE[sat_name] + k*30.0)*d2r
        # bars start INSIDE the hub (2.0, not 4.0). At 4.0 they were tangent to the
        # r4.0 hub — touching at a single point, so hub and fingers were separate
        # islands in plane, hanging together only via the lamina below. #110/#117
        # were both finger-stiffness failures; this fuses them properly.
        bars.append(_bar(a, 2.0, 16.0, 4.5))
        tips.append(_bar(a, 15.5, TIP_R, 4.5))                        # raised tip (#117)
    slabs = [(0.0, ZM,  mon.simplify(0.02).difference(bore)),         # clocked mesh lamina
             (ZM,  2.2, unary_union([hub]+bars).difference(bore)),
             (2.2, ZS,  unary_union([hub]+bars+tips).difference(bore))]
    if boss_h > 0:                                                    # leap only (#141)
        slabs.append((ZS, ZS+boss_h, Point(0,0).buffer(4.5,48).difference(bore)))
    write_stl(name, stack(slabs))
    return mon

def _bar(a, r0, r1, w):
    """Radial finger bar as a plane polygon (the shape the design is actually about)."""
    u = np.array([np.cos(a), np.sin(a)]); v = np.array([-u[1], u[0]])
    return Polygon([tuple(r0*u - v*w/2), tuple(r1*u - v*w/2),
                    tuple(r1*u + v*w/2), tuple(r0*u + v*w/2)])

def _rbox(cx, cy, ang_deg, L, W, z0, z1):
    a = ang_deg*d2r; u = np.array([np.cos(a), np.sin(a)]); v = np.array([-u[1], u[0]])
    c = np.array([cx, cy])
    pts = [tuple(c + sx*u*L/2 + sy*v*W/2) for sx, sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
    return _poly_prism(pts, z0, z1)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sun = sun_piece()
    mons = {}
    mons["month"] = receiver("141_receiver_month_v17.stl", "month", 5, boss_h=0.0)
    mons["feb"]   = receiver("142_receiver_feb_v17.stl",   "feb",   1, boss_h=0.0)
    mons["leap"]  = receiver("143_receiver_leap_v17.stl",  "leap",  1, boss_h=1.2)
    print("  engine set v17 emitted: 1 tower piece (print x3) + 3 clocked receivers")
