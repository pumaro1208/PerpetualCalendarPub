#!/usr/bin/env python3
"""Flag-free central press-fit (Ron: kill the flag). The star grows an integral
UPWARD tube that rides the post (ID) and press-fits the board's enlarged bore
(OD) -> concentric + rigid rotation coupling with NO outrigger/peg. Both parts
still print flat (tube rises in the star; board just gets a bigger hole).
Cost: board bore enlarged (re-print) + fixture collar -> thrust pad."""
import numpy as np
from generator import involute_profile, MD, ADD_F, PROG_ROOT, cylinder, box, _poly_prism, polar_solid, P
from generator_v13 import PIV_R, SUNORB, STN_M, STN_F, STN_L, dflat_profile, polar_prof_solid, write_stl
from generator_v16 import _star_r4_profile

TUBE_ID, TUBE_OD = 4.35, 5.45          # radii: ID rides post (8.3), OD press-fits board bore (10.9)
BORE = TUBE_OD                          # board bore enlarged to 10.9 dia

def part_02e_board_bigbore_v16():
    """Committed board, bore enlarged 8.7 -> 10.9 to accept the star tube.
    Teeth, 31 day-ticks (tall pos-1), month post + D-key all UNCHANGED."""
    tris=[]; t=4.0
    prof,_,_,_=involute_profile(31,MD,add_f=ADD_F)
    tris += polar_prof_solid(prof,0,t,bore=BORE)
    for k in range(31):
        a=2*np.pi*k/31; h=2.2 if k==0 else 1.0
        tris += cylinder(33.5*np.cos(a),33.5*np.sin(a),1.1,t,t+h,seg=16)
    ang=np.deg2rad(STN_M); cx,cy=SUNORB*np.cos(ang),SUNORB*np.sin(ang)
    tris += cylinder(cx,cy,PIV_R,t,12.3,seg=48)
    kx=dflat_profile(PIV_R-0.2,1.2)
    tris += _poly_prism([(cx+p[0],cy+p[1]) for p in kx],9.3,12.0)
    for stn in (STN_M,STN_F,STN_L):
        a=np.deg2rad(stn)
        tris += cylinder((PROG_ROOT-2.0)*np.cos(a),(PROG_ROOT-2.0)*np.sin(a),1.2,t,t+1.6,seg=12)
    write_stl("02e_board_bigbore_v16.stl",tris)

def part_50d_star_hub_v16():
    """Star, flag-free: shallow-triangle scallop disc + integral upward press-tube.
    Disc z0-1.7 (assembly 3.3-5.0); tube z0-3.7 (assembly 3.3-7.0) rides the post
    and press-fits the board bore over z5-7. No outrigger, no peg."""
    tris=[]
    th,r=_star_r4_profile(1240)
    tris += polar_prof_solid(r,0.0,1.7,bore=TUBE_OD)              # scallop disc (bore = tube OD)
    tris += polar_solid(TUBE_OD,0.0,3.7,r_inner=TUBE_ID,seg=64)  # integral press-tube
    write_stl("50d_star_hub_v16.stl",tris)

def part_49_fixture_r57_v16():
    """Fixture r5.6: r5.5 with the program collar replaced by a THRUST PAD (annulus
    r6.5-13) the wide central star disc spins on -- clears the tube; the board
    seats on the star-disc top. Post, square key, drive collar, bridge pins kept."""
    tris=[]; pr=4.15
    tris += box(0,0,132,76,0.0,2.5)
    tris += box(36.65,0,58.7,76,2.5,4.0)
    tris += cylinder(-36.75,0,pr,4.0,9.5,seg=64)
    tris += box(-36.75,0,4.3,4.3,9.5,18.0)
    tris += polar_solid(13.0,2.5,3.3,r_inner=6.5,cx=-36.75,cy=0,seg=64)   # thrust pad
    tris += cylinder(+36.75,0,pr,4.0,24.0,seg=48)
    tris += cylinder(+36.75,0,6.5,4.0,5.0,seg=48)
    for sx in (-1,1):
        tris += cylinder(-36.75+sx*20.0,-30.5,2.0-0.075,2.5,4.15,seg=24)  # bridge pins moved IN
    write_stl("49_fixture_r57_v16.stl",tris)

if __name__=="__main__":
    part_02e_board_bigbore_v16(); part_50d_star_hub_v16(); part_49_fixture_r57_v16()
    print("clearances:")
    print("  tube rides post:", 4.35>4.15, "(ID r4.35 vs post r4.15, 0.2 bearing)")
    print("  tube wall:", round(TUBE_OD-TUBE_ID,2), "mm (printable)")
    print("  disc clears post:", TUBE_OD>4.15)
