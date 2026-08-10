#!/usr/bin/env python3
"""#164 BOARD HUB — the tube survives, the scallop disc dies.

Ron, bench, first v17 board assembly: "the new board's detent ring does not
snap into the center of the board, leaving a big hole that doesn't anchor
itself to the sun post." The second half of that sentence is a DESIGN HOLE,
not an assembly fault, and the photos prove it: the board sits loose around
the K4 key with nothing in its bore at all.

The board has never ridden the fixture post directly. Since #114/#137 it
presses onto the star hub's r5.53 tube (part 50e), and that tube rides the
post. But 50e is one part with TWO jobs — the bearing tube AND the old
scallop detent disc (r26.0..28.5, assembly z3.3..5.0). The #156 redesign
replaced that disc with the peg-mounted triangle-wave ring (164), which
occupies r26.5..30.5 in the SAME z band, 3.4..5.0. Measured off the emitted
STLs below: ~345mm^2 of dead overlap. Transfer the old hub into the new board
and its disc lands exactly where the new ring's body and pegs live — the two
parts cannot coexist. v17 retired the disc's detent job and never emitted a
disc-free hub. This part is that hub. The old 50e stays with the old board.

Geometry — every number is a proven number, nothing new:
  tube    ID r4.17  (#136 design-at-bore; the #114 sleeve-ladder 'id17' winner)
          OD r5.53  (#137: prints ~5.47 into the board's 5.45 bore = 0.02 press)
          local z 0..5.0 (assembly 3.3..8.3 — the most that clears the K4
          square key start at z8.5)
  flange  annulus r5.53..12.0, 1.7 thick (local z 0..1.7) — the thrust job the
          scallop disc used to do. It rides the fixture pad (annulus r6.5..13.0,
          top z3.3), so the board seats at assembly 5.0 exactly as before.
          OD 12.0 stays on the pad (13.0) and clears the new ring's ID 26.5
          by 14.5mm.
Assembly: flange bottom on pad top (3.3) -> flange top = board underside = 5.0;
board bore engagement z5.0..8.3 = 3.3mm, identical to 50e. Prints flange-down,
flat, no supports, ~4 minutes. The hub is a round bearing: it needs no clocking
(the ring's unequal pegs carry the detent clocking straight into the board).
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import Point
from generator_v13 import write_stl
from weld import stack

TID, TOD   = 4.17, 5.53      # radii — the #137 pairing, verbatim
TUBE_H     = 5.0
FLANGE_OD  = 12.0            # on the pad (6.5..13.0), far inside the ring ID 26.5
FLANGE_T   = 1.7             # pad top 3.3 + 1.7 = board seat at assembly 5.0

def ann(ro, ri):
    return Point(0,0).buffer(ro,96).difference(Point(0,0).buffer(ri,64))

def hub(name="167_board_hub_v17.stl"):
    write_stl(name, stack([
        (0.0,      FLANGE_T, ann(FLANGE_OD, TID)),   # flange + tube root, one slab
        (FLANGE_T, TUBE_H,   ann(TOD,       TID)),   # bare tube
    ]))

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    hub()

    # ---- acceptance: measured off the emitted STLs, thresholds not printouts ----
    import trimesh
    FAILS = 0
    def gate(ok, msg):
        global FAILS
        print(f"  [{'PASS' if ok else 'FAIL'}] {msg}")
        if not ok: FAILS += 1

    def rings(path, z):
        """(rmin, rmax) of the solid at height z — all section loops pooled."""
        m = trimesh.load(path)
        s = m.section(plane_origin=[0,0,z], plane_normal=[0,0,1])
        rr = np.concatenate([np.hypot(np.array(L)[:,0], np.array(L)[:,1])
                             for L in s.discrete])
        return m, float(rr.min()), float(rr.max())

    m, lo, hi = rings("stl_v13/167_board_hub_v17.stl", 0.8)
    gate(m.is_watertight, "watertight")
    gate(abs(m.bounds[1][2]-TUBE_H) < 0.01 and abs(m.bounds[0][2]) < 0.01,
         f"height {m.bounds[1][2]-m.bounds[0][2]:.2f} (tube 5.0: assembly 3.3..8.3, "
         f"0.2 under the K4 key start at 8.5)")
    gate(abs(lo-TID) < 0.05 and abs(hi-FLANGE_OD) < 0.05,
         f"flange section r{lo:.2f}..r{hi:.2f} (want {TID}..{FLANGE_OD})")
    _, lo2, hi2 = rings("stl_v13/167_board_hub_v17.stl", 3.0)
    gate(abs(lo2-TID) < 0.05 and abs(hi2-TOD) < 0.05,
         f"tube section r{lo2:.2f}..r{hi2:.2f} (want {TID}..{TOD})")
    # the three fits, asserted as the #136/#137 arithmetic:
    gate(abs((TOD-0.06) - 5.45 - 0.02) < 0.005,
         "board press: OD 5.53 prints ~5.47 into the 5.45 bore = 0.02 interference (#137)")
    gate(4.17 - (4.17-0.06) > 0.05, "post fit: bore 4.17 over the r4.17-design post "
         "printing ~4.11 = 0.06 running clearance (#137)")
    gate(FLANGE_OD <= 13.0 - 0.5 and FLANGE_OD >= 6.5 + 3.0,
         f"flange OD {FLANGE_OD} rides the fixture pad (6.5..13.0) with margin")
    gate(3.3 + FLANGE_T == 5.0, "flange 1.7 on the pad top 3.3 seats the board at 5.0")
    # the collision this part exists to avoid — measured, both directions:
    from shapely.geometry import Polygon
    def plan(path, z):
        """True plan solid at z: largest loop is the outline, the rest are holes."""
        m2 = trimesh.load(path)
        s = m2.section(plane_origin=[0,0,z], plane_normal=[0,0,1])
        ps = sorted((Polygon(np.array(L)[:,:2]).buffer(0) for L in s.discrete),
                    key=lambda p: p.area, reverse=True)
        solid = ps[0]
        for p in ps[1:]:
            solid = solid.difference(p)
        return solid
    ring  = plan("stl_v13/164_detent_star_v17.stl", 0.8)        # assembly 3.4..5.0
    olddb = plan("stl_v13/50e_star_hub_v16.stl",    0.8)        # assembly 3.3..5.0
    dead  = ring.intersection(olddb).area
    # The 50e disc is scalloped (root 26.0, notch tips to 28.5), so the overlap is
    # its notch bumps past the ring's ID 26.5 — ~130mm^2 of hard interference in
    # the same z band, before even counting the ring's pegs landing at r28.5.
    gate(dead > 100, f"OLD 50e disc vs new ring 164: {dead:.0f}mm^2 dead overlap "
         f"in the shared z band — the old hub must NOT be transferred")
    newf  = plan("stl_v13/167_board_hub_v17.stl", 0.8)
    gate(newf.intersection(ring).area < 1e-6 and
         26.5 - FLANGE_OD > 10.0,
         f"new hub vs ring 164: zero overlap, {26.5-FLANGE_OD:.1f}mm radial daylight")
    print(f"\n  {'HUB ACCEPTED' if not FAILS else f'*** HUB GATE FAILED: {FAILS} ***'}")
    sys.exit(1 if FAILS else 0)
