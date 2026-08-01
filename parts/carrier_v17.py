#!/usr/bin/env python3
"""#140 THREE-STATION CARRIER CHAIN — gives feb and leap their pivots.

The patent carries the feb pivot on a stud integral with the month stud, offset
circumferentially (218 on 214), and the leap pivot extends the same chain. A post
rising from the board to the feb station is impossible: it would spear the rotating
month satellite (whose lamina reaches r17.19, far past the 4.81mm station spacing).
So the chain must CROSS OVER above each satellite.

Printable form: instead of one cranked stud (overhangs), the chain is a STACK of
flat pieces, exactly like the sun tower — each is a plate + one riser, prints flat,
zero supports:
    board 02j  : month post, extended to assy 14.0 so arm 1 can seat on it
    arm 1      : plate 12.7-14.0 pressed on the month post, riser at the FEB station
    arm 2      : plate 17.2-18.5 pressed on the feb post, riser at the LEAP station

ALTITUDES — the sun tower piece is 4.5mm tall (band 1.5 + slim 3.0), so stacking
three pieces puts the mesh bands 4.5mm apart. The satellite bands therefore sit at
assy 9.5 / 14.0 / 18.5 (was 9.5/13/16.5 at 3.5 spacing). That 4.5 spacing is what
makes the crossover possible: satellites are 3mm tall, leaving a 1.5mm gap for each
arm (1.3mm plate + 0.2mm running clearance over the satellite below).
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generator import involute_profile, MD, ADD_F, cylinder, polar_solid, _poly_prism
from generator_v13 import SUNORB, STN_M, STN_F, STN_L, polar_prof_solid, write_stl
BORE_PRESS = 2.60          # press onto a design-2.70 post (prints 2.64) -> 0.04 interference
POST_R     = 2.70          # #136 design-at-bore law
SEAT_R     = 3.50
def stn_xy(s): 
    a=np.deg2rad(s); return SUNORB*np.cos(a), SUNORB*np.sin(a)

def part_02j_board():
    """Board 02j = 02h with the month post EXTENDED to assy 14.0 (local 9.0) so the
    feb carrier arm can seat on it at 12.7. Safe now: the feb satellite has moved up
    to 14.0, so the taller post no longer fouls it (that was the #107 constraint)."""
    tris=[]; t=4.0
    prof,_,_,_=involute_profile(31,MD,add_f=ADD_F)
    tris += polar_prof_solid(prof,0,t,bore=5.45)
    cx,cy=stn_xy(STN_M)
    tris += cylinder(cx,cy,SEAT_R,t,t+0.5,seg=32)      # month seat shoulder (assy 9.0-9.5)
    tris += cylinder(cx,cy,POST_R,t,9.0,seg=48)        # post to assy 14.0
    write_stl("144_board_02j_v17.stl",tris)

def carrier_arm(name, from_stn, to_stn, z_bot, z_top, riser_top):
    """Plate spanning two stations + a riser at the far one. z are ASSEMBLY heights;
    the part prints from 0 (plate bottom on the bed)."""
    fx,fy=stn_xy(from_stn); tx,ty=stn_xy(to_stn)
    h=z_top-z_bot
    tris=[]
    # plate: rounded slot joining the two bosses
    n=24
    for i in range(n):
        u=i/(n-1); x=fx+(tx-fx)*u; y=fy+(ty-fy)*u
        tris += cylinder(x,y,4.6,0.0,h,seg=20)
    # bore for the post below (press fit), through the plate
    tris += polar_solid(4.6,0.0,h,r_inner=BORE_PRESS,cx=fx,cy=fy,seg=48)
    # riser at the far station: seat shoulder then post
    tris += cylinder(tx,ty,SEAT_R,h,h+0.5,seg=32)
    tris += cylinder(tx,ty,POST_R,h,h+(riser_top-z_top),seg=48)
    write_stl(name,tris)

if __name__=="__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    part_02j_board()
    carrier_arm("145_carrier_feb_v17.stl",  STN_M, STN_F, 12.7, 14.0, 18.5)
    carrier_arm("146_carrier_leap_v17.stl", STN_F, STN_L, 17.2, 18.5, 23.0)
    print("  carrier chain: board 02j + feb arm + leap arm")
