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
    arm 2      : plate 17.7-19.0 pressed on the feb post, riser at the LEAP station

ALTITUDES (#141, corrected) — the sun tower piece is 5.0mm tall (band 1.5 + slim
3.5), so stacking three puts the mesh bands 5.0mm apart: satellites at assy
9.5 / 14.5 / 19.5.

The 5.0 came from a real budget, not a round number. Between one satellite's top
and the next satellite's bottom the arm needs FOUR things, not one:
    0.20  running clearance over the satellite below (it spins, the arm doesn't)
    1.30  arm plate
    0.50  pivot pad at the far station
    ----
    2.00  + 3.00 satellite = 5.00 band pitch
The pad is the piece the first cut forgot. Without it the satellite above seats
directly on the plate's top face and rubs it across the whole r17 lamina overlap —
friction at the worst possible radius. With it, the satellite is lifted clear and
bears only on a r3.5 collar right at its own pivot.
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generator import involute_profile, MD, ADD_F, cylinder, polar_solid, _poly_prism
from generator_v13 import SUNORB, STN_M, STN_F, STN_L, polar_prof_solid, write_stl
from shapely.geometry import Point, LineString, Polygon
from weld import weld, stack
BORE_PRESS = 2.60          # press onto a design-2.70 post (prints 2.64) -> 0.04 interference
POST_R     = 2.70          # #136 design-at-bore law
SEAT_R     = 3.50
PAD_CLR    = 0.30          # keeps the pivot pad off the press-fit bore (#146)
PAD_H      = 0.50          # pivot pad / thrust collar under each satellite
BOARD_BORE = 5.45          # RADIUS, on the star hub's r5.53 tube (#137 press)
BAND       = (9.5, 16.0, 22.5)   # month / feb / leap mesh-band altitudes (#147)
PLATE_H    = 2.80          # arm plate = the grip. 6.50 pitch - 3.00 sat - 0.20 clr - 0.50 pad
POST_TOP   = 10.5          # board month post, LOCAL z (assy 15.5 = arm 1 plate top)
def stn_xy(s): 
    a=np.deg2rad(s); return SUNORB*np.cos(a), SUNORB*np.sin(a)

def part_02j_board():
    """Board 02j = 02h with the month post EXTENDED to assy 14.0 (local 9.0) so the
    feb carrier arm can seat on it at 12.7. Safe now: the feb satellite has moved up
    to 14.0, so the taller post no longer fouls it (that was the #107 constraint)."""
    t=4.0
    prof,_,_,_=involute_profile(31,MD,add_f=ADD_F)
    th=np.linspace(0,2*np.pi,len(prof),endpoint=False)
    # BORE r5.45 — a RADIUS. polar_prof_solid(bore=) takes a radius, and the board
    # presses onto the star hub's r5.53 tube for the #137 0.08 interference. Writing
    # 5.45/2 here (as the first cut of this rewrite did) gives r2.725 and the board
    # will not go over the hub at all.
    gear=Polygon(np.stack([prof*np.cos(th),prof*np.sin(th)],1)).difference(Point(0,0).buffer(BOARD_BORE,64))
    cx,cy=stn_xy(STN_M)
    write_stl("144_board_02j_v17.stl", stack([
        (0.0,  t,        gear),
        (t,    t+PAD_H,  Point(cx,cy).buffer(SEAT_R,32)),   # month pivot pad (assy 9.0-9.5)
        (t+PAD_H, POST_TOP, Point(cx,cy).buffer(POST_R,48)),  # post to assy 15.5
    ]))

def carrier_arm(name, from_stn, to_stn, z_bot, z_top, riser_top):
    """Plate spanning two stations + a riser at the far one. z are ASSEMBLY heights;
    the part prints from 0 (plate bottom on the bed). The pivot PAD sits on top of
    the plate at the far station: it is what the next satellite up actually rests
    on, so that satellite's mesh lamina lands at z_top+PAD_H — which must equal its
    sun band. Verified by the assembly gate, not by eye."""
    fx,fy=stn_xy(from_stn); tx,ty=stn_xy(to_stn)
    h=z_top-z_bot
    # plate = capsule between the stations, MINUS the press-fit bore.
    # It was previously 24 overlapping solid cylinders swept along the line plus a
    # separate annulus at the from-station — but the sweep's first cylinder is solid
    # and sits exactly there, so the union filled the bore back in and the arm had
    # no hole to press onto the post at all. Authoring the plate as one plane
    # polygon with a real interior ring is what makes that impossible to repeat.
    plate = LineString([(fx,fy),(tx,ty)]).buffer(4.6, 32) \
                .difference(Point(fx,fy).buffer(BORE_PRESS, 48))
    # #146, Ron's eye: the pad must be CLIPPED clear of the bore. The stations are
    # only 4.81mm apart while the pad is r3.50 and the bore r2.60 — 6.10 of feature
    # in 4.81 of space — so a full-circle pad overhung the bore mouth by 1.29mm
    # across 120 deg of its rim. Two ways that bites: the lip prints unsupported
    # over the hole and droops exactly where the satellite bears, and if the post
    # below comes out even slightly long it fouls the lip and the arm never seats.
    # Clipping costs some thrust area and keeps ~296 deg of contact at the
    # satellite's bore edge, which is plenty for a hand-cranked demonstrator.
    pad = Point(tx,ty).buffer(SEAT_R, 48).difference(
              Point(fx,fy).buffer(BORE_PRESS + PAD_CLR, 48))
    write_stl(name, stack([
        (0.0,   h,             plate),
        (h,     h+PAD_H,       pad),                               # pivot pad, clipped
        (h+PAD_H, h+(riser_top-z_top), Point(tx,ty).buffer(POST_R, 48)),
    ]))

def sun_spacer(h=1.0, r=5.30, sq_hw=2.25, name="147_sun_spacer_1mm_v17.stl"):
    """Base shim under the sun tower — and Ron's "the sun gear is low" in one part.

    The tower bottoms on the fixture's round-post top face at z8.5 (the square bore
    cannot pass the r4.17 post), so band 1 lands at 8.5-10.0. The month satellite
    seats on the board's 0.5mm pivot pad at 9.5. Without this shim the sun band and
    the mesh lamina overlap by only 0.5 of their 1.5mm height. 1.0mm exactly closes it.

    OD 5.30, NOT 6.00 (#142). It spans z8.5-9.5 and the board runs to z9.0 with a
    r5.45 bore, so a r6.00 shim buries 0.5mm of itself in the board. 5.30 nests in
    the bore with 0.15 clearance.

    Square-bored so it keys on the same K4 column as the tower pieces — a round-bored
    shim could rotate, and that is one more way to lose the clock. Emitted from the
    generator now; it was hand-built for plate-44 rev A with no source at all."""
    sq=[(sq_hw,sq_hw),(-sq_hw,sq_hw),(-sq_hw,-sq_hw),(sq_hw,-sq_hw)]
    p=Polygon(Point(0,0).buffer(r,64).exterior.coords,[sq])
    write_stl(name, stack([(0.0, h, Point(0,0).buffer(r,64).difference(Polygon(sq)))]))

if __name__=="__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    part_02j_board()
    #                                          plate_bot plate_top riser_top
    carrier_arm("145_carrier_feb_v17.stl",  STN_M, STN_F, 12.7, 15.5, 22.0)
    carrier_arm("146_carrier_leap_v17.stl", STN_F, STN_L, 19.2, 22.0, 27.0)
    sun_spacer()
    print("  carrier chain: board 02j + feb arm + leap arm + base spacer")
