#!/usr/bin/env python3
"""#165 FIXTURE r64 — the detent bridges move INTO the fixture (Ron's call).

Ron, bench, holding holder 163: "there does not seem to be a place to mount
this" — then: "this bridge holder must be integrated into the fixture."

He is right, and not just ergonomically. The #157b corner-wrap holder was
designed to avoid a fixture reprint, but it made the spring nose's ALTITUDE a
function of the bench: holder and fixture each referenced the tabletop, so a
mat, a tape layer, or a warped table entered the z chain of a mechanism whose
engagement band is 1.3mm tall. And in x-y it still needed tape to HOLD what the
edges LOCATED. Integrated, every detent surface is referenced inside one
printed part — placement error is retired as a category, which also closes
Ron's same-day question about ring adjustability: nothing is left to adjust.

r64 = r63 verbatim, PLUS the two bridge-holder slab sets from detent_v17
(one geometry source — holder_slabs(); the fixture and the standalone spares
can never disagree), MINUS two things:
  - the corner-wrap lip and butt-face registration (the fixture IS the datum)
  - the two r2.0 pins at (+/-20, -30.5): the old #99 bridge mounts, copy-
    carried through r59..r63 long after that bridge died. Gone.

Frames: detent geometry lives in BOARD frame; the fixture STL has the board
axis at (-36.75, 0). Slabs translate by dx=-36.75. The wings overlap the plate
slab by 2.0mm in y so they slice as one solid, not two kissing shells.

Nothing else moves: plate 132x76, board post r4.17 to z8.5, K4 key 4.42 to
z29.5, thrust pad r6.5-13 (z2.5-3.3), drive post r4.17 + collar, raised drive
platform. Springs 165 unchanged and still consumable. Standalone holders
163/166 -> spares/scrap.
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely import affinity
from generator import cylinder, box, polar_solid
from generator_v13 import write_stl
from weld import weld, stack
from detent_v17 import holder_slabs

BOARD_DX = -36.75           # board axis in fixture frame

def fixture_r64(name="168_fixture_r64_v17.stl", key_root=False):
    """key_root (#168, r65): Ron's bench — the naked K4 key cracked at its base
    (z8.5, where the square leaves the round post) and the sun heeled over ~25deg,
    taking the whole calendar's ground link with it. Mesh forces load the root at
    a ~2mm lever (harmless); a HAND on the 13mm of exposed key above the tower is
    a 21mm lever straight onto the layer lines — a handling failure waiting for a
    hand. r65 adds a 5.40-square ROOT COLLAR from 8.5 to 9.4 (2.2x the section
    modulus, stress riser moved up under the clamped zone); the sun spacer rev B
    gets a stepped bore to sit over it. Everything else identical to r64."""
    tris=[]; pr=4.17
    # ---- r63 core, verbatim (minus the dead #99 pins) ----
    tris += box(0,0,132,76,0.0,2.5)                      # plate
    tris += box(36.65,0,58.7,76,2.5,4.0)                 # raised drive platform
    tris += cylinder(BOARD_DX,0,pr,2.5,8.5,seg=64)       # board program post
    if key_root:
        tris += box(BOARD_DX,0,5.40,5.40,8.5,9.4)        # #168 root collar
        tris += box(BOARD_DX,0,4.42,4.42,9.4,29.5)       # K4 key above it
    else:
        tris += box(BOARD_DX,0,4.42,4.42,8.5,29.5)       # K4 key, full tower height
    tris += polar_solid(13.0,2.5,3.3,r_inner=6.5,cx=BOARD_DX,cy=0,seg=64)  # thrust pad
    tris += cylinder(+36.75,0,pr,4.0,26.0,seg=48)        # drive post
    tris += cylinder(+36.75,0,6.5,4.0,5.0,seg=48)        # drive collar
    # ---- #165: integrated bridge holders, south and north ----
    for m in (+1,-1):
        tris += stack([(z0, z1, affinity.translate(poly, BOARD_DX, 0.0))
                       for z0, z1, poly in holder_slabs(m, lip=False, overlap=2.0)])
    write_stl(name, weld(tris))

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    fixture_r64()

    # ---- acceptance -----------------------------------------------------------
    import trimesh
    from shapely.geometry import Polygon, Point, LineString
    from shapely.ops import unary_union
    FAILS=0
    def gate(ok,msg):
        global FAILS
        print(f"  [{'PASS' if ok else 'FAIL'}] {msg}")
        if not ok: FAILS+=1
    def plan(path,z,tx=0.0):
        m2=trimesh.load(path)
        s=m2.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
        return unary_union([Polygon(np.array(L)[:,:2]).buffer(0) for L in s.discrete]), m2

    F="stl_v13/168_fixture_r64_v17.stl"
    sol, m = plan(F, 1.0)
    gate(m.is_watertight, "watertight")
    b=m.bounds
    gate(b[1][0]-b[0][0] < 250 and b[1][1]-b[0][1] < 250,
         f"bed fit: {b[1][0]-b[0][0]:.0f} x {b[1][1]-b[0][1]:.0f}mm on a 256 bed")
    # r63 core preserved where it matters — measured against the r63 STL itself,
    # inside the old plate rectangle (wings excluded):
    old,_ = plan("stl_v13/157_fixture_r63_v17.stl", 1.0)
    win = Polygon([(-65,-37),(65,-37),(65,37),(-65,37)])
    dxor = sol.intersection(win).symmetric_difference(old.intersection(win)).area
    gate(dxor < 1.0, f"base plate identical to r63 inside the old footprint "
         f"(XOR {dxor:.2f}mm2)")
    # posts / key / pad present at height:
    s5,_  = plan(F, 5.0)
    gate(s5.contains(Point(BOARD_DX,0)), "board post present at z5")
    gate(s5.contains(Point(36.75,0)), "drive post present at z5")
    s12,_ = plan(F, 12.0)
    gate(s12.contains(Point(BOARD_DX,0)) and not s12.contains(Point(36.75+10,0)),
         "K4 key present at z12")
    s30,_ = plan(F, 3.0)
    gate(s30.contains(Point(BOARD_DX+9.5,0)) and s30.contains(Point(BOARD_DX-9.5,0)),
         "thrust pad annulus present at z3.0")
    # the dead #99 pins are GONE:
    s35,_ = plan(F, 3.6)
    pins_gone = all(not s35.intersects(Point(BOARD_DX+sx*20.0,-30.5).buffer(2.5,32))
                    for sx in (-1,1))
    gate(pins_gone, "old #99 bridge pins absent at z3.6 (dropped after 5 fixture revs)")
    # integrated pockets: same spring-installability physics as detent_accept,
    # run against the FIXTURE, spring translated into fixture frame:
    from detent_v17 import SPAN, WIRE_Y, _seat_y, V_BOT, TAB
    xn=(-_seat_y())*np.cos(np.deg2rad(V_BOT)) + BOARD_DX
    s35f,_ = plan(F, 3.5)
    for m_ in (+1,-1):
        tag = "south" if m_>0 else "north"
        tabz=unary_union([Polygon([(xn+s*SPAN/2-5.3, m_*WIRE_Y-4.4),(xn+s*SPAN/2+5.3, m_*WIRE_Y-4.4),
                                   (xn+s*SPAN/2+5.3, m_*WIRE_Y+4.4),(xn+s*SPAN/2-5.3, m_*WIRE_Y+4.4)])
                          for s in (-1,1)])
        for sp in ("soft","med","firm"):
            Sp0,_=plan(f"stl_v13/165_detent_spring_{sp}_v17.stl",1.0)
            Sp=affinity.translate(Sp0, BOARD_DX, 0.0)
            if m_<0: Sp=affinity.scale(Sp,1,-1,origin=(0,0))   # flipped part serves north
            inter=Sp.intersection(s35f)
            press=inter.intersection(tabz).area; foul=inter.difference(tabz).area
            gate(foul<0.01 and 4.5<press<7.5,
                 f"{tag}/{sp}: press {press:.2f}mm2 in BOTH tab zones, foul {foul:.3f}mm2")
        for s in (-1,1):
            xl=xn+s*(SPAN/2-6.0)
            c=LineString([(xl,m_*WIRE_Y-6),(xl,m_*WIRE_Y+6)]).intersection(
                affinity.scale(affinity.translate(plan(f"stl_v13/165_detent_spring_med_v17.stl",1.0)[0],BOARD_DX,0),1,(1 if m_>0 else -1),origin=(0,0)))
            gate(not c.is_empty, f"{tag}: leaf continuous through the {'east' if s>0 else 'west'} gateway")
    # pocket floor at 2.7 (spring plane 2.7-4.7): solid at 2.6, void at 2.8
    s26,_=plan(F,2.6); s28,_=plan(F,2.8)
    tp=Point(xn+SPAN/2, WIRE_Y)
    gate(s26.intersects(tp.buffer(1)) and not s28.contains(tp),
         "pocket floor at z2.7 - spring plane 2.7-4.7 preserved")
    # board clearance: nothing taller than the plate inside the board tooth sweep
    s55,_=plan(F,5.5)
    sweep=Point(BOARD_DX,0).buffer(41.86+0.5,128)
    enc=s55.intersection(sweep)
    ok_sweep = all(np.hypot(np.array(g.exterior.coords)[:,0]-BOARD_DX,
                            np.array(g.exterior.coords)[:,1]).min()<14
                   for g in (enc.geoms if hasattr(enc,'geoms') else [enc]))
    gate(ok_sweep, "at z5.5 nothing inside the board sweep r41.9 except the central tower")
    print(f"\n  {'FIXTURE r64 ACCEPTED' if not FAILS else f'*** r64 GATE FAILED: {FAILS} ***'}")
    sys.exit(1 if FAILS else 0)
