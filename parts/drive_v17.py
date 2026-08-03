#!/usr/bin/env python3
"""#149 DRIVE WHEEL v17 — the 24h wheel, with arms that reach 21h / 22h / 23h.

Ron: "I need the correct 24 hr wheel printed that can hit the 21,22,23 hours."

This is the part that has been blocking everything: without it there is nothing to
crank. The old 30_drive_v16 is only 15mm tall overall and was built for the 3.5mm
band spacing; the v17 stack at 6.5 pitch needs the 21h arm up at 24.7-25.5.

GEOMETRY, taken from the simulator, not invented:
  DDR 73.50   drive axis, from the board axis, along the strike line
  DBODY 29.2  body radius        -> reaches in to 44.30
  DTIP  32.76 arm tip orbit      -> reaches in to 40.74
Board tooth tip and satellite strike tip both stand at 41.86, so every arm engages
by 41.86 - 40.74 = 1.12mm — the drive window every clocking number is quoted against.
The body clears the board teeth by 2.44 and the satellites by 3.36.

ANGLES. The wheel turns once per day, so one hour is 15 deg. Each arm has to point
at the board (180 deg in the wheel frame) at its OWN hour, and the simulator draws
them at (180 - off) with off = 0/15/30/45 for 24h/23h/22h/21h. Verified: all four
land on world 180 at their hour.

ALTITUDES. Each arm hits a STRIKE TIP and must clear the MESH lamina 0.7mm below it:
  24h  board teeth      5.00 -  9.00
  23h  month strike    11.70 - 12.50   (month mesh ends 11.00)
  22h  feb strike      18.20 - 19.00   (feb mesh ends 17.50)
  21h  leap strike     24.70 - 25.50   (leap mesh ends 24.00)

WHY FOUR STACKED PIECES rather than one tall wheel. A single body would be a r29.2
cylinder 20.5mm tall — 55cm^3 — with four small tabs whose undersides are all
unsupported cantilevers. Split at each arm instead and every piece prints ARM DOWN
ON THE BED: no overhang anywhere, no supports, a quarter of the material. It is the
same idiom as the sun tower, and it is why the tower prints clean.

Each piece carries its arm at its own pre-rotated angle, so a plain square key
clocks all four correctly — exactly how the receivers handle their ALPHA. The key
is a sleeve (round bore on the fixture's r4.17 drive post, square outside), because
the drive post has to stay round: this wheel is the crank, it must turn.
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
from shapely import affinity
from generator_v13 import write_stl
from weld import stack

DDR, DBODY, DTIP = 73.50, 29.20, 32.76
POST_R   = 4.17          # fixture drive post — round, design-at-bore (#136)
# The drive key CANNOT be the sun tower's K4. That key is 4.42 across, and the
# fixture's drive post is r4.17 = 8.34 diameter — bigger than the whole key. A
# sleeve has to wrap the post, so the square has to enclose it plus a wall:
#   8.34 bore + 2 x 1.58 wall = 11.50 across.
# (First cut used K4 and the bore simply ate the key, leaving four corner slivers —
# the weld gate caught it as "4 disconnected solids".)
SQ_HW    = 5.75          # drive square key half-width -> 11.50 across flats
HW_BASE  = 0.075         # arm half-angle at the body (rad), from the simulator
HW_TIP   = 0.030         # ...and at the tip: the arm tapers
ARMS = [("24h", 0.0,  5.00,  9.00, "board teeth"),
        ("23h", 15.0, 11.70, 12.50, "month strike tip"),
        ("22h", 30.0, 18.20, 19.00, "feb strike tip"),
        ("21h", 45.0, 24.70, 25.50, "leap strike tip")]
PIECE_TOP = {"24h": 11.70, "23h": 18.20, "22h": 24.70, "21h": 30.00}

def arm_poly(off_deg):
    """One tapered arm, body radius out to tip, centred on (180 - off)."""
    a = np.deg2rad(180.0 - off_deg)
    pts = [(DBODY*np.cos(a-HW_BASE), DBODY*np.sin(a-HW_BASE)),
           (DTIP *np.cos(a-HW_TIP),  DTIP *np.sin(a-HW_TIP)),
           (DTIP *np.cos(a+HW_TIP),  DTIP *np.sin(a+HW_TIP)),
           (DBODY*np.cos(a+HW_BASE), DBODY*np.sin(a+HW_BASE))]
    return Polygon(pts)

def piece(nm, off, z0, z1, top, no):
    """Body disc + its arm. The arm sits at the BOTTOM so the part prints arm-down
    on the bed — that is what makes the whole wheel support-free."""
    body = Point(0,0).buffer(DBODY, 192)
    key  = Polygon([(SQ_HW,SQ_HW),(-SQ_HW,SQ_HW),(-SQ_HW,-SQ_HW),(SQ_HW,-SQ_HW)])
    arm  = arm_poly(off)
    h = top - z0
    write_stl(no, stack([
        (0.0,      z1-z0, unary_union([body, arm]).difference(key)),   # arm band
        (z1-z0,    h,     body.difference(key)),                       # body above it
    ]))
    return h

def sleeve(no="162_drive_sleeve_v17.stl", z0=5.0, z1=30.0):
    """Round bore on the fixture's r4.17 drive post, square outside to clock the
    four pieces. The post cannot be square — the wheel is the crank and has to turn."""
    sq = Polygon([(SQ_HW,SQ_HW),(-SQ_HW,SQ_HW),(-SQ_HW,-SQ_HW),(SQ_HW,-SQ_HW)])
    wall = SQ_HW - POST_R
    assert wall > 1.0, f"sleeve wall only {wall:.2f}mm"
    write_stl(no, stack([(0.0, z1-z0, sq.difference(Point(0,0).buffer(POST_R, 64)))]))
    return wall

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    for i, (nm, off, z0, z1, tgt) in enumerate(ARMS):
        h = piece(nm, off, z0, z1, PIECE_TOP[nm], f"{158+i}_drive_{nm}_v17.stl")
        print(f"  {nm}: arm {180-off:5.1f}deg, z {z0:5.2f}-{z1:5.2f} -> {tgt:17s} "
              f"piece {h:5.2f} tall, prints arm-down")
    w = sleeve()
    print(f"  + sleeve: bore r{POST_R} on the drive post, square {2*SQ_HW:.2f} across "
          f"outside, wall {w:.2f}mm — clocks all four pieces")
