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

THE JUMPER — ALL PRINTED (Ron: "do not use wire in any part of this build").
A separate flat PLA leaf spring that plugs into the holder: anchor tab, 40mm
leaf, elbow, finger, and a r1.4 nose, all one 2.0mm-thick piece printed flat —
bending is in-plane, the strongest orientation, and the part takes 5 minutes.

PLA CREEP is the honest objection to a printed spring, and the design answers
it three ways. (1) LOW RESTING STRAIN: the leaf holds only ~0.35mm of preload,
~0.10% fiber strain — creep at that stress is negligible; the real deflection
(~1.3mm escape, ~0.4% strain) lasts only the moment of a step. (2) CONSUMABLE:
the spring presses into an open-top pocket; if it ever relaxes, print another.
(3) THREE STIFFNESSES emitted (leaf 2.6 / 3.0 / 3.4 wide -> ~0.35 / 0.51 /
0.72 N/mm): pick the click by feel — the printed equivalent of sliding a wire.

The holder is a base + one pocket block: the spring's 8.3mm tab presses down
into an 8.0 pocket (prints 8.18 into 8.12 — 0.06 interference, #136), floor at
z2.7 so the spring plane is 2.7..4.7: engaging the star band 3.4..5.0 over
1.3mm, clearing the fixture plate 2.5 by 0.2 and the board 5.0 by 0.3.
The pocket is placed so the natural nose position sits 0.35mm past the seat —
the preload is in the GEOMETRY, computed here from the star profile itself.

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
V_BOT   = 270.0 - PITCH/4    # #157 second bridge: quarter-pitch re-clock makes the two
                             # engagement bearings flip-symmetric about the x-axis AND
                             # exactly 16 pitches apart (185.81 deg). 180.00 would be
                             # 15.5 pitches - HALF a pitch out of phase - and two ideal
                             # sawtooth detents in anti-phase sum to a FLAT potential:
                             # zero net centering, double friction. 31 is odd; the
                             # opposite of a valley is always a crest.

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

# ---- holder (rev B: pocket, no slots) + printed springs -------------------
HX0, HX1   = 8.0, 56.0
HY_S, HY_N = -52.0, -38.6     # north face butts the fixture plate edge (-38)
BASE_T     = 2.5
POCKET_X   = 44.0             # pocket centre (anchor of the leaf)
TAB        = (10.0, 8.3)      # spring tab x,y  (pocket y = 8.0 -> 0.06 press)
POCKET_FLOOR, POCKET_TOP = 2.7, 6.0
SPRING_Z   = 2.0              # leaf/finger/nose thickness (use z 2.7..4.7)
LEAF_L     = 40.0             # elbow x=0 .. anchor
NOSE_R     = 1.4
FINGER_W   = 3.6
WIRE_Y     = -44.0            # leaf centreline (kept name for the gate)

def _seat_y(nr=NOSE_R):
    """Self-calibrate: nose-centre y (on the V_BOT bearing line) when seated."""
    ring = sawtooth_ring()
    a = np.deg2rad(V_BOT)
    lo, hi = 34.0, 27.0   # radial distance search, bracketing the sawtooth band
    lo, hi = 27.0, 34.0
    good=34.0
    for _ in range(40):
        mid=(lo+hi)/2
        if Point(mid*np.cos(a), mid*np.sin(a)).buffer(nr,48).intersects(ring): lo=mid
        else: hi=mid; good=mid
    return -good   # kept sign convention: south seat has negative y-ish magnitude

def holder(name="163_detent_holder_v17.stl"):
    base = Polygon([(HX0,HY_S),(HX1,HY_S),(HX1,HY_N),(HX0,HY_N)])
    # block CLIPPED at the butt face: a full square at the pocket straddled the
    # plate edge and collided with the fixture plate (gate caught it at y-37)
    blk  = Polygon([(POCKET_X-7,HY_S),(POCKET_X+7,HY_S),(POCKET_X+7,HY_N),(POCKET_X-7,HY_N)])
    pocket = Polygon([(POCKET_X-TAB[0]/2, WIRE_Y-4.0),
                      (POCKET_X+TAB[0]/2, WIRE_Y-4.0),
                      (POCKET_X+TAB[0]/2, WIRE_Y+4.0),
                      (POCKET_X-TAB[0]/2, WIRE_Y+4.0)])
    write_stl(name, stack([
        (0.0, BASE_T, unary_union([base, blk])),
        (BASE_T, POCKET_FLOOR, blk),
        (POCKET_FLOOR, POCKET_TOP, blk.difference(pocket)),
    ]))

def spring(width, tag):
    """Flat plug-in leaf: tab | leaf | elbow | finger | nose. Printed flat, 2.0
    thick. The finger sits at X_N (the engagement bearing's x), so the SAME part
    flipped over serves the north bridge: flipping about x negates y, mapping
    bearing 267.10 -> 92.90 = exactly the north seat. Preload is geometric:
    natural nose tip = seat + 0.35 toward the board."""
    seat_r = -_seat_y()                    # radial seat distance (measured)
    a = np.deg2rad(V_BOT)
    xn, seat_y = seat_r*np.cos(a), seat_r*np.sin(a)   # south seat centre
    tipy = seat_y + 0.35                   # natural (unloaded) nose centre
    tab   = _sq(POCKET_X, WIRE_Y, TAB[0]/2).buffer(0)
    tab   = Polygon([(POCKET_X-TAB[0]/2, WIRE_Y-TAB[1]/2),
                     (POCKET_X+TAB[0]/2, WIRE_Y-TAB[1]/2),
                     (POCKET_X+TAB[0]/2, WIRE_Y+TAB[1]/2),
                     (POCKET_X-TAB[0]/2, WIRE_Y+TAB[1]/2)])
    leaf  = Polygon([(0.0, WIRE_Y-width/2),(POCKET_X-TAB[0]/2+1, WIRE_Y-width/2),
                     (POCKET_X-TAB[0]/2+1, WIRE_Y+width/2),(0.0, WIRE_Y+width/2)])
    fing  = Polygon([(xn-FINGER_W/2, WIRE_Y),(xn+FINGER_W/2, WIRE_Y),
                     (xn+FINGER_W/2, tipy-NOSE_R+0.6),(xn-FINGER_W/2, tipy-NOSE_R+0.6)])
    nose  = Point(xn, tipy).buffer(NOSE_R, 64)
    body  = unary_union([tab, leaf, fing, nose])
    write_stl(f"165_detent_spring_{tag}_v17.stl", stack([(0.0, SPRING_Z, body)]))
    E=2400.0; I=width**3*SPRING_Z/12.0; k=3*E*I/LEAF_L**3
    return k

def holder_north(name="166_detent_holder_north_v17.stl"):
    """#157: the second bridge. Mirror of 163 about the x-axis — butts the NORTH
    plate edge (+38). Takes the same springs, flipped over."""
    base = Polygon([(HX0,-HY_S),(HX1,-HY_S),(HX1,-HY_N),(HX0,-HY_N)])
    blk  = Polygon([(POCKET_X-7,-HY_S),(POCKET_X+7,-HY_S),(POCKET_X+7,-HY_N),(POCKET_X-7,-HY_N)])
    pocket = Polygon([(POCKET_X-TAB[0]/2, -WIRE_Y-4.0),
                      (POCKET_X+TAB[0]/2, -WIRE_Y-4.0),
                      (POCKET_X+TAB[0]/2, -WIRE_Y+4.0),
                      (POCKET_X-TAB[0]/2, -WIRE_Y+4.0)])
    write_stl(name, stack([
        (0.0, BASE_T, unary_union([base, blk])),
        (BASE_T, POCKET_FLOOR, blk),
        (POCKET_FLOOR, POCKET_TOP, blk.difference(pocket)),
    ]))

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    star(); holder(); holder_north()
    ks={}
    for w,tag in ((2.6,"soft"),(3.0,"med"),(3.4,"firm")):
        ks[tag]=spring(w,tag)
    seat=_seat_y()
    print(f"  164 star: 31 full-pitch V, V-bottom 270, pegs {PEGS[0][1]}/{PEGS[1][1]} sq at r{PEG_R}")
    print(f"  163 holder rev B: pocket at x{POCKET_X}, floor {POCKET_FLOOR} (spring plane 2.7..4.7)")
    print(f"  165 springs (all printed, no wire): nose r{NOSE_R} seats at y{seat:.2f}, preload 0.35")
    for tag,k in ks.items():
        print(f"      {tag:4s}: k {k:.2f} N/mm -> ~{k*1.7:.2f} N at full escape")
