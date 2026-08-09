#!/usr/bin/env python3
"""#156 DETENT v17 — the board's rest position, defined at last.

Ron: "while the detent notches the board each day there is plenty of backlash …
we want it to eliminate that backlash so it stops in the same place each day."

He is right, and the requirement is stricter than comfort: rest slop spends from
the SAME 1.12mm drive window as mesh lash (#134), and the July phantom-graze
restoration (#155: 4.63 deg push vs 5.81 half-step) assumes the board STARTS each
evening centred. The detent has three jobs: CENTRE (zero-backlash rest), REJECT
(restore the board from any sub-half-step displacement after an arm releases it),
and YIELD (a true strike must cross to the next station and be completed, not
fought).

WHY NOT THE BOARD'S OWN TEETH. Measured off the emitted board (144/149): a wire
nose wedged in the involute valleys centres beautifully at rest, but the tooth
tips carry a wide flat land — the lift curve has a ZERO-SLOPE PLATEAU from 3.4 to
7.4 deg at EVERY nose radius (0.5..4.0 tried). 4.63 sits dead centre of it: a
July release would strand the board mid-tooth with no restoring force at all.
The gear is a gear; it cannot also be the star.

THE STAR. A separate ring under the board: sawtooth on its outer cylindrical
face, 31 notches of FULL-PITCH V — adjacent V's share crests, no flat anywhere,
so d(lift)/d(theta) != 0 everywhere except the crest, and the crest (the
watershed) is at half-pitch 5.806 deg BY CONSTRUCTION, not by tuning.
    OD 30.5 / root 29.1 (V depth 1.4) / ID 26.5 / plate 1.6 thick.
It hangs from the board underside on two press pegs at r28.5 — DIFFERENT sizes
(3.2 and 4.2 sq into 3.0 and 4.0 sockets, #136 comp arithmetic -> ~0.04 slip
each) so it can only assemble one way, and it is clocked so a V-BOTTOM sits at
world bearing 270 when the board is at its datum: rest positions ARE the
stations the strike clocking assumes. In the stack it spans z3.4..5.0 — 0.9
above the fixture plate, flush under the board. The underside day numbers live
at r31.9..35.1, outboard of the ring: still readable.

THE JUMPER. 1.0mm music wire in a printed holder south of the fixture plate:
straight run along x at y=-44 (outside the board rim, so the holder's posts can
stand full height), one 90 deg bend, and a 15mm finger reaching in at bearing
270 to rest its END (r0.5 nose) in a V. Nose-in-V is two-flank contact
converging to a point: ONE rest angle, zero play, held by ~0.6mm of preload.
Slots in the posts are open-top drop-ins; free length post-to-bend ~34mm gives
~0.75 N/mm, ~1.5 N at full escape — a crisp daily click, not a fight.

The holder BUTTS the fixture plate edge (locates +y) and is taped or clamped to
the bench at its south end (the reaction is ~1.5 N; this is the alpha mount —
a clamping mount can follow once the geometry is bench-proven).

WIRE BENCH SPEC (music wire, 1.0 mm):
    total ~75 mm; one 90 deg bend 15 mm from an end (the finger).
    Thread the long run through both post slots, finger pointing at the board
    axis, tip in a star notch. Slide until the elbow sits ~15 mm south of the
    star face. The finger tip should visibly deflect ~0.5 mm when seated.
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from generator_v13 import write_stl
from weld import stack

PITCH   = 360/31
S_OD, S_ROOT, S_ID = 30.5, 29.1, 26.5      # sawtooth outer / root / ring bore
S_T     = 1.6                               # star plate thickness (assy 3.4..5.0)
PEG_H   = 1.0                               # into 1.0-deep board sockets
PEGS    = [(30.0, 3.2, 3.0), (210.0, 4.2, 4.0)]   # bearing, peg sq, socket sq
PEG_R   = 28.5              # ON the ring plate (26.5..30.5); r20 floated in the bore
V_BOT   = 270.0                             # V-bottom bearing at board datum

def _sq(cx, cy, half):
    return Polygon([(cx-half,cy-half),(cx+half,cy-half),(cx+half,cy+half),(cx-half,cy+half)])

def sawtooth_ring():
    """Full-pitch triangle wave on the OD: r(th) = ROOT + depth*tri(th), tri=0 at
    each V-bottom, 1 at each crest; V-bottoms every PITCH starting at V_BOT."""
    th = np.linspace(0, 2*np.pi, 31*40, endpoint=False)
    deg = np.degrees(th)
    frac = ((deg - V_BOT)/PITCH + 0.5) % 1.0
    tri = 2*np.abs(frac - 0.5)
    r = S_ROOT + (S_OD - S_ROOT)*tri
    outer = Polygon(np.stack([r*np.cos(th), r*np.sin(th)], 1))
    return outer.difference(Point(0,0).buffer(S_ID, 128))

def star(name="164_detent_star_v17.stl"):
    ring = sawtooth_ring()
    pegs = []
    for brg, psq, _ in PEGS:
        a = np.deg2rad(brg)
        pegs.append(_sq(PEG_R*np.cos(a), PEG_R*np.sin(a), psq/2))
    write_stl(name, stack([
        (0.0, S_T, ring),
        (S_T, S_T+PEG_H, unary_union(pegs)),
    ]))

def board_sockets():
    """The cutters the board generators subtract (depth 1.0 from the underside).
    Shared here so board and star can never disagree."""
    out = []
    for brg, _, ssq in PEGS:
        a = np.deg2rad(brg)
        out.append(_sq(PEG_R*np.cos(a), PEG_R*np.sin(a), ssq/2))
    return unary_union(out)

# ---- holder ----------------------------------------------------------------
HX0, HX1   = 8.0, 56.0        # body x span
HY_S, HY_N = -52.0, -38.6     # body y span (north face butts the plate edge -38)
BASE_T     = 2.5
POSTS      = [34.0, 48.0]     # post centres (x), at the wire line
WIRE_Y     = -44.0            # main-run centreline
WIRE_Z     = 4.1              # run/finger plane: under board (5.0), over plate (2.5)
POST_W     = 6.0
POST_H     = 6.0
SLOT_W     = 1.05             # drop-in for 1.0 wire

def holder(name="163_detent_holder_v17.stl"):
    base = Polygon([(HX0,HY_S),(HX1,HY_S),(HX1,HY_N),(HX0,HY_N)])
    posts, slots = [], []
    for px in POSTS:
        posts.append(_sq(px, WIRE_Y, POST_W/2))
        slots.append(Polygon([(px-POST_W/2-0.1, WIRE_Y-SLOT_W/2),
                              (px+POST_W/2+0.1, WIRE_Y-SLOT_W/2),
                              (px+POST_W/2+0.1, WIRE_Y+SLOT_W/2),
                              (px-POST_W/2-0.1, WIRE_Y+SLOT_W/2)]))
    post_u = unary_union(posts); slot_u = unary_union(slots)
    write_stl(name, stack([
        (0.0, BASE_T, unary_union([base, post_u])),
        (BASE_T, WIRE_Z-0.5, post_u),                    # solid post up to slot floor
        (WIRE_Z-0.5, POST_H, post_u.difference(slot_u)), # slotted above: wire drops in
    ]))

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    star(); holder()
    print(f"  164 star: 31 full-pitch V, OD {S_OD}/root {S_ROOT}, V-bottom at {V_BOT} deg,"
          f" pegs {PEGS[0][1]}/{PEGS[1][1]} sq at r{PEG_R}")
    print(f"  163 holder: run y{WIRE_Y} z{WIRE_Z}, posts x{POSTS}, slot {SLOT_W}")
    print(f"  wire: 1.0 music wire, ~75mm, one 90deg bend, 15mm finger — see docstring")
