#!/usr/bin/env python3
"""#143 BOARD DAY NUMBERS — 1-31, white-in-black, recessed into BOTH faces.

Ron: "I wanted to print white date numbers on the board ... so I know how to set them."

WHERE EACH NUMBER GOES is not a free choice — the simulator already fixes it. The
underside pin crown is the date authority: station k sits at board-frame angle
216.5 - k*PITCH, and the engaged station is always at world 216.5 (the date train's
takeoff). The sim inits steps=25 with pos=26 and steps both together, so

    date = (steps mod 31) + 1        ->  crown station k  <->  date k+1

The human reading index is placed at world 90 (12 o'clock on the fixture) because
that is where a person reads a wheel. Date d is current when the board has turned
phi = (d-1)*PITCH, so d's number must sit at board-frame

    ALPHA(d) = 90 - (d-1)*PITCH

with the digits' "up" pointing radially outward — which is exactly what makes the
number at the index upright. Any other up-vector is a constant rotation of this and
would read crooked at the index.

WHY BOTH FACES. The three satellites are carried BY the board, so their shadow is
FIXED in board frame: mesh laminae r17.19 about stations at r23.75 cover r6.6 to
r40.9 across ~81 degrees, and the board's own teeth end at r41.86. There is
therefore NO radius on the top face that clears them — whatever ring you choose,
about seven consecutive dates sit under a satellite and can never be read from
above. That is inherent to the architecture, not a placement mistake. The same ring
mirrored into the underside is always readable, because nothing overhangs there.

WHY RECESSED, NOT CUT THROUGH. Cutting clean through would also solve the shadow,
but it strands the counters of 0/4/6/8/9 as floating islands — the assembly gate
caught 26 of them — and the stencil font needed to avoid that costs real legibility
at a 3.6mm cap. A 0.8mm recess per face keeps a 2.4mm solid core, so every counter
rests on material and the digits stay whole.
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union
from shapely import affinity
from generator import involute_profile, MD, ADD_F
from generator_v13 import SUNORB, STN_M, write_stl
from weld import stack
from carrier_v17 import (stn_xy, SEAT_R, POST_R, PAD_H, BOARD_BORE, POST_TOP,
                         SPIG_R, POST_STEP)

PITCH   = 360/31
R_NUM   = 33.5          # digit-centre ring: clear of the root circle 37.05 and of
                        # the month pivot pad (r23.75 +- 3.5), >4mm either side
CAP     = 3.20
STROKE  = 0.70          # ~2 extrusions at a 0.4 nozzle
DIG_W   = 2.00
KERN    = 0.50
T       = 4.0           # board thickness
REC     = 0.80          # recess depth per face -> 2.40mm solid core between them
INDEX_W = 90.0          # world bearing of the human reading index

G = {
 '0':[(0,0,1,0),(1,0,1,1),(1,1,0,1),(0,1,0,0),(0,0,1,1)],
 '1':[(.5,0,.5,1),(.2,.75,.5,1),(.2,0,.8,0)],
 '2':[(0,1,1,1),(1,1,1,.5),(1,.5,0,0),(0,0,1,0)],
 '3':[(0,1,1,1),(1,1,1,0),(1,0,0,0),(.3,.5,1,.5)],
 '4':[(.8,0,.8,1),(.8,1,0,.35),(0,.35,1,.35)],
 '5':[(1,1,0,1),(0,1,0,.55),(0,.55,1,.55),(1,.55,1,0),(1,0,0,0)],
 '6':[(1,1,0,.6),(0,.6,0,0),(0,0,1,0),(1,0,1,.5),(1,.5,0,.5)],
 '7':[(0,1,1,1),(1,1,.35,0)],
 '8':[(0,0,1,0),(1,0,1,1),(1,1,0,1),(0,1,0,0),(0,.5,1,.5)],
 '9':[(1,.4,0,.4),(0,.4,0,1),(0,1,1,1),(1,1,1,0),(1,0,0,0)],
}

def glyph(ch):
    segs = [LineString([(x0*DIG_W, y0*CAP), (x1*DIG_W, y1*CAP)])
            for x0, y0, x1, y1 in G[ch]]
    return unary_union([s.buffer(STROKE/2, cap_style=2, join_style=1) for s in segs])

def number(txt):
    """A whole number centred on (0,0), reading left-to-right with +y up."""
    w = len(txt)*DIG_W + (len(txt)-1)*KERN
    return unary_union([affinity.translate(glyph(c), i*(DIG_W+KERN) - w/2, -CAP/2)
                        for i, c in enumerate(txt)])

def day_ring():
    """All 31 numbers in the BOARD frame + the date-1 witness notch."""
    out = []
    for d in range(1, 32):
        a = INDEX_W - (d-1)*PITCH
        p = affinity.rotate(number(str(d)), a - 90, origin=(0, 0))   # up = radially out
        out.append(affinity.translate(p, R_NUM*np.cos(np.deg2rad(a)),
                                         R_NUM*np.sin(np.deg2rad(a))))
    a1 = np.deg2rad(INDEX_W)                    # witness notch outboard of date 1:
    out.append(LineString([((R_NUM+2.7)*np.cos(a1), (R_NUM+2.7)*np.sin(a1)),
                           ((R_NUM+0.6)*np.cos(a1), (R_NUM+0.6)*np.sin(a1))])
               .buffer(0.55, cap_style=2))       # confirms the ring's clocking at a glance
    ring = unary_union(out)
    # Counters below MIN_ISLAND would leave black specks a 0.4 nozzle cannot print
    # (the gate found four at 0.02mm^2). Fill them into the ink instead — a speck of
    # white inside a glyph is invisible; a speck of unprintable black is a defect.
    return _fill_specks(ring)

MIN_ISLAND = 0.30      # mm^2

def _fill_specks(geom):
    from shapely.geometry import MultiPolygon
    gs = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
    out = []
    for g in gs:
        keep = [r for r in g.interiors if Polygon(r).area >= MIN_ISLAND]
        out.append(Polygon(g.exterior, keep))
    return unary_union(out)

def build():
    prof, _, _, _ = involute_profile(31, MD, add_f=ADD_F)
    th = np.linspace(0, 2*np.pi, len(prof), endpoint=False)
    gear = Polygon(np.stack([prof*np.cos(th), prof*np.sin(th)], 1)) \
             .difference(Point(0, 0).buffer(BOARD_BORE, 64))
    top = day_ring()
    # underside ring: mirrored in X, so flipping the fixture left-to-right (the
    # natural way to turn it over) shows the numbers upright with the index still
    # at the top. Mirroring in Y instead would put the index at the bottom.
    bot = affinity.scale(top, -1, 1, origin=(0, 0))
    cx, cy = stn_xy(STN_M)
    write_stl("149_board_02k_numbered_v17.stl", stack([
        (0.0,     REC,     gear.difference(bot)),      # underside recesses
        (REC,     T-REC,   gear),                      # 2.4mm solid core
        (T-REC,   T,       gear.difference(top)),      # top-face recesses
        (T,       T+PAD_H,   Point(cx, cy).buffer(SEAT_R, 32)),
        (T+PAD_H, POST_STEP, Point(cx, cy).buffer(POST_R, 48)),  # full 5.40 under the satellite
        (POST_STEP, POST_TOP, Point(cx, cy).buffer(SPIG_R, 48)), # #152 spigot + shoulder
    ]))
    write_stl("150_board_daynums_white_v17.stl", stack([
        (0.0,   REC, bot),
        (T-REC, T,   top),
    ], allow_multi=True))
    return gear, top, bot

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    gear, top, bot = build()
    # REGISTRATION: compose_plate centres every object on its own bbox, so the white
    # inlay only lands in its recesses if its bbox centre is placed where the board's
    # origin goes. Compute the offset rather than assume it is zero.
    import trimesh
    b = trimesh.load("stl_v13/149_board_02k_numbered_v17.stl").bounds
    w = trimesh.load("stl_v13/150_board_daynums_white_v17.stl").bounds
    bc = (b[0]+b[1])/2; wc = (w[0]+w[1])/2
    print(f"  31 day numbers + witness notch · ring r{R_NUM} · cap {CAP} · stroke {STROKE}")
    print(f"  index world {INDEX_W:.0f}deg · date d at board-frame {INDEX_W:.0f} - (d-1)x{PITCH:.3f}")
    print(f"  board  bbox centre  ({bc[0]:+.3f}, {bc[1]:+.3f})")
    print(f"  white  bbox centre  ({wc[0]:+.3f}, {wc[1]:+.3f})")
    print(f"  -> if the board sits at [X, Y], the white part must be placed at "
          f"[X{wc[0]-bc[0]:+.3f}, Y{wc[1]-bc[1]:+.3f}]")
