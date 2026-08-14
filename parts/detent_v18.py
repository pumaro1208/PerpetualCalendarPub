#!/usr/bin/env python3
"""#170 DETENT v18 — press-fit deep-V disc + roller-tipped bridge (Ron's spec).

Ron, bench, after running v17: "The tabs on the new detent are better but the
longer nose creates too much angular flex and I prefer the snap on disk vs the
snap in ring as it gives me the ability to adjust the rotation so give me the
tabs, press fit detent disc and a short nose that completely engages for no
play in the day jump." Then: "the roller that fits in between the teeth seems
like a perfect detent."

Three faults of v17, each answered:
  ANGULAR FLEX — the v17 centre finger was a ~13mm cantilever: stiff radially
    (the leaf's job) but compliant tangentially — play in exactly the detent
    direction. v18 replaces it with a short rigid GUSSET carrying a free
    ROLLER: tangential loads run down the leaf's own axis (inextensible), and
    the roller sits in TWO-FLANK contact in a deep V — complete engagement,
    zero play, rolling escape instead of sliding stick-slip.
  FIXED CLOCKING — the peg-mounted ring 164 retires. The v18 disc PRESS-FITS
    over the #164 hub's r12 flange: friction holds it through every escape,
    a deliberate two-hand twist re-clocks it. The watchmaker's friction-set
    coupling; computed clocking becomes the starting point, Ron's wrench the
    trim. (Board 149's peg sockets become unused — harmless.)
  SHALLOW ENGAGEMENT — V depth 1.4 -> 2.6 (the old #99 star's honest teeth on
    the modern architecture): double the centering torque per spring newton.

Unchanged: the r65 fixture pockets (tabs identical), two bridges 16 pitches
apart (odd-31 phase law, #157), watershed force discrimination, soft/med/firm
ladder, all-printed law, full bidirectionality (symmetric V, symmetric roller).

THE ROLLER'S KEEPER IS THE BOARD: roller rides a short fat stub (l/d ~ 0.8,
gated for stress — the one deliberate exception to the free-end law, numbers
below) and its top sits 0.2 under the board's underside: in service it cannot
climb out; lift the board and it lifts off for inspection.

z map (assembly): spring plate 2.7-4.7 · gusset/eye pad 2.7-3.4 (slides UNDER
the disc teeth) · disc hub collar 3.3-5.0 on the flange · disc web+teeth
3.6-5.0 (0.3 over the fixture pad, 0.2 over the eye pad) · roller 3.4-4.8
(engages teeth 3.6-4.8) · stub top 4.9 · board 5.0.
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely import affinity
from generator_v13 import write_stl
from weld import stack
from detent_v17 import (PITCH, V_BOT, SPAN, TAB, WIRE_Y, HY_S, HY_N,
                        POCKET_FLOOR, POCKET_TOP, SPRING_Z)

# ---- disc ------------------------------------------------------------------
D_OD, D_ROOT = 30.5, 27.9          # deep V: depth 2.6 (was 1.4)
D_BORE       = 11.96               # radius; presses the #164 flange r12.00
                                   # (#136: both print -0.06 dia -> 0.08 dia squeeze)
HUB_R        = 13.2                # hub collar outer radius
D_T          = 1.7                 # hub collar height (assy 3.3-5.0)
WEB_LIFT     = 0.3                 # web+teeth start 0.3 up: clears fixture pad AND eye pad
# ---- roller prow ------------------------------------------------------------
ROLL_R   = 2.3                     # roller radius (dia 4.6): two-flank in the V
ROLL_H   = 1.4
ROLL_B   = 1.35                    # roller bore radius (2.70 dia over the 2.60 stub)
STUB_R   = 1.30                    # dia 2.60, short and fat
STUB_H   = 2.2                     # local; top at assy 4.9 = 0.1 under the board
PAD_T    = 0.7                     # eye pad thickness (assy 2.7-3.4)
PAD_R    = 3.3                     # eye pad radius around the stub
GUSS_W   = 14.0                    # gusset root width at the leaf
PRELOAD  = 0.35

def deep_v_disc_poly():
    th = np.linspace(0, 2*np.pi, 31*48, endpoint=False)
    deg = np.degrees(th)
    frac = ((deg - V_BOT)/PITCH + 0.5) % 1.0
    tri  = 2*np.abs(frac - 0.5)
    r = D_ROOT + (D_OD - D_ROOT)*tri
    return Polygon(np.stack([r*np.cos(th), r*np.sin(th)], 1))

def disc(name="175_detent_disc_v18b.stl"):
    """rev B (#171): PRINTS FLIPPED. Rev A put the 0.3 pad-relief on the DOWN
    face — the whole web annulus started 0.3 above the bed, bridging over air
    with supports off; Ron's print came out ragged wherever the first layer
    floated. The disc is functionally flippable (symmetric V, round bore), so
    rev B prints full-face-down with the relief UP; at assembly the recessed
    face goes DOWN toward the fixture pad. The recess is its own witness:
    'recess faces the fixture'."""
    hub   = Point(0,0).buffer(HUB_R, 96).difference(Point(0,0).buffer(D_BORE, 128))
    web   = deep_v_disc_poly().difference(Point(0,0).buffer(D_BORE, 128))
    write_stl(name, stack([
        (0.0, D_T,          hub),              # press collar, full height
        (0.0, D_T-WEB_LIFT, web),              # web + teeth ON THE BED; relief on top
    ]))

def _seat_center(rr=ROLL_R):
    """Radius of the roller CENTRE when seated two-flank in the V at V_BOT."""
    G = deep_v_disc_poly()
    a = np.deg2rad(V_BOT)
    lo, hi = D_ROOT, D_OD + rr + 1.0
    for _ in range(48):
        mid = (lo+hi)/2
        if Point(mid*np.cos(a), mid*np.sin(a)).buffer(rr, 64).intersects(G): lo = mid
        else: hi = mid
    return lo

def spring(width, tag):
    """Bridge: tab | leaf | rigid gusset -> eye pad + stub (roller rides it).
    Tabs/leaf identical to v17 -> drops into the r65 pockets unchanged."""
    seat = _seat_center(); a = np.deg2rad(V_BOT)
    xn, sy = seat*np.cos(a), seat*np.sin(a)
    cy = sy + PRELOAD                       # preload: stub 0.35 INTO the V
    tabs=[]
    for sgn in (-1,+1):
        cx = xn + sgn*SPAN/2
        tabs.append(Polygon([(cx-TAB[0]/2, WIRE_Y-TAB[1]/2),(cx+TAB[0]/2, WIRE_Y-TAB[1]/2),
                             (cx+TAB[0]/2, WIRE_Y+TAB[1]/2),(cx-TAB[0]/2, WIRE_Y+TAB[1]/2)]))
    leaf = Polygon([(xn-SPAN/2, WIRE_Y-width/2),(xn+SPAN/2, WIRE_Y-width/2),
                    (xn+SPAN/2, WIRE_Y+width/2),(xn-SPAN/2, WIRE_Y+width/2)])
    guss = Polygon([(xn-GUSS_W/2, WIRE_Y),(xn+GUSS_W/2, WIRE_Y),
                    (xn+1.2, cy-PAD_R+0.8),(xn-1.2, cy-PAD_R+0.8)])
    pad  = Point(xn, cy).buffer(PAD_R, 64)
    thin = unary_union([guss, pad])
    thin = thin.buffer(1.5, join_style=1).buffer(-1.5, join_style=1)
    full = unary_union(tabs+[leaf])
    full = full.buffer(2.5, join_style=1).buffer(-2.5, join_style=1)
    stub = Point(xn, cy).buffer(STUB_R, 48)
    write_stl(f"176_detent_spring_roller_{tag}_v18.stl", stack([
        (0.0, SPRING_Z, full),
        (0.0, PAD_T,    thin.difference(full.buffer(-0.01))),
        (0.0, STUB_H,   stub),
    ], allow_multi=False))
    E=2400.0; I=width**3*SPRING_Z/12.0
    return 192*E*I/SPAN**3, (xn, cy)

def roller(bore_r=ROLL_B, name="177_detent_roller_v18.stl"):
    """#171: rev A bores (dia 2.7) seized on the stubs — SMALL-HOLE SHRINKAGE:
    FDM holes under ~3mm shrink beyond the #136 constant (~0.15-0.2 extra at a
    0.4 nozzle). Rev B is a bore LADDER (2.8/3.0/3.2 design): Ron keeps the
    rollers that spin freely without wobble — the #114 idiom at escapement
    scale."""
    write_stl(name, stack([(0.0, ROLL_H,
        Point(0,0).buffer(ROLL_R,96).difference(Point(0,0).buffer(bore_r,48)))]))

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    disc()
    for b,tag in ((1.4,"b28"),(1.5,"b30"),(1.6,"b32")):
        roller(b, f"177_detent_roller_{tag}_v18.stl")
    ks={}
    for w,tag in ((1.2,"soft"),(1.4,"med"),(1.6,"firm")):
        ks[tag], nose = spring(w, tag)
    seat=_seat_center()
    print(f"  175 disc: 31 deep-V (OD {D_OD} root {D_ROOT}), press bore r{D_BORE} on flange r12")
    print(f"  176 roller bridges: seat centre r{seat:.2f}, preload {PRELOAD}, gusset {GUSS_W} root")
    print(f"  177 roller: dia {2*ROLL_R} x {ROLL_H}, bore {2*ROLL_B}")
    for tag,k in ks.items():
        print(f"      {tag:4s}: k {k:.2f} N/mm")
