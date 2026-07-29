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

def part_02f_board_v16():
    """Board 02f = 02e with the 31 perimeter day-tick pegs (r33.5) AND the
    three station witness dots (r35.05) REMOVED. These were cosmetic witness
    marks; the engine sweep showed the tall pos-1 peg (+0.8) and the dots
    (+0.2) poked up into the month satellite's mesh-lamina band even with the
    finding-63 spacer. Removing them clears the orbit. UNCHANGED: 31-tooth
    involute rim, enlarged 10.9 bore, satellite pivot post + D-key at STN_M."""
    tris=[]; t=4.0
    prof,_,_,_=involute_profile(31,MD,add_f=ADD_F)
    tris += polar_prof_solid(prof,0,t,bore=BORE)
    # (31 day-tick pegs REMOVED — were cosmetic, fouled the month lamina)
    ang=np.deg2rad(STN_M); cx,cy=SUNORB*np.cos(ang),SUNORB*np.sin(ang)
    tris += cylinder(cx,cy,PIV_R,t,12.3,seg=48)
    kx=dflat_profile(PIV_R-0.2,1.2)
    tris += _poly_prism([(cx+p[0],cy+p[1]) for p in kx],9.3,12.0)
    # (3 station witness dots REMOVED — were cosmetic, fouled the month lamina)
    write_stl("02f_board_v16.stl",tris)

def part_02g_board_v16():
    """Board 02g = 02f with the satellite pivot post EXTENDED (finding #106):
    the receiver bore now rides the post through both laminae (z0-8 local ->
    assembly 10.4-18.4 on the 1.4 spacer), so the post must reach that height to
    support the full two-lamina receiver instead of ending 1.1mm short and letting
    it tilt. Post local top 12.3 -> 14.0 (assembly 17.3 -> 19.0). Everything else
    identical to 02f (pegless rim, 10.9 bore). The old D-key stub is a no-op (r2.2
    buried inside the r2.4 post) and is dropped; the post is a clean round bearing."""
    tris=[]; t=4.0
    prof,_,_,_=involute_profile(31,MD,add_f=ADD_F)
    tris += polar_prof_solid(prof,0,t,bore=BORE)
    ang=np.deg2rad(STN_M); cx,cy=SUNORB*np.cos(ang),SUNORB*np.sin(ang)
    tris += cylinder(cx,cy,PIV_R,t,14.0,seg=48)          # extended bearing post (was 12.3)
    write_stl("02g_board_v16.stl",tris)

def part_50d_star_hub_v16():
    """Star, flag-free: shallow-triangle scallop disc + integral upward press-tube.
    Disc z0-1.7 (assembly 3.3-5.0); tube z0-3.7 (assembly 3.3-7.0) rides the post
    and press-fits the board bore over z5-7. No outrigger, no peg."""
    tris=[]
    th,r=_star_r4_profile(1240)
    tris += polar_prof_solid(r,0.0,1.7,bore=TUBE_OD)              # scallop disc (bore = tube OD)
    tris += polar_solid(TUBE_OD,0.0,3.7,r_inner=TUBE_ID,seg=64)  # integral press-tube
    write_stl("50d_star_hub_v16.stl",tris)

def part_49_fixture_r58_v16():
    """Fixture r5.6: r5.5 with the program collar replaced by a THRUST PAD (annulus
    r6.5-13) the wide central star disc spins on -- clears the tube; the board
    seats on the star-disc top. Post, square key, drive collar, bridge pins kept."""
    tris=[]; pr=4.15
    tris += box(0,0,132,76,0.0,2.5)
    tris += box(36.65,0,58.7,76,2.5,4.0)
    tris += cylinder(-36.75,0,pr,2.5,9.5,seg=64)
    tris += box(-36.75,0,4.3,4.3,9.5,18.0)
    tris += polar_solid(13.0,2.5,3.3,r_inner=6.5,cx=-36.75,cy=0,seg=64)   # thrust pad
    tris += cylinder(+36.75,0,pr,4.0,24.0,seg=48)
    tris += cylinder(+36.75,0,6.5,4.0,5.0,seg=48)
    for sx in (-1,1):
        tris += cylinder(-36.75+sx*20.0,-30.5,2.0-0.075,2.5,4.15,seg=24)  # bridge pins moved IN
    write_stl("49_fixture_r58_v16.stl",tris)

def part_02h_board_v16():
    """Board 02h (finding #107) — pegless rim like 02f, but the satellite post is
    SHORTENED, not lengthened: with the compact 3mm receiver (bore assembly
    9.5-12.5) the post only rides to z12.5, and it MUST stop below the feb band
    (z13) or it fouls the feb satellite orbiting 4.81mm away. Post: r3.5 seat
    shoulder z9-9.5 (receiver seats at 9.5), then r2.4 bearing z9-12.5 (local 4-7.5).
    Reverses 02g's taller post — the compact stack wants a shorter one."""
    tris=[]; t=4.0
    prof,_,_,_=involute_profile(31,MD,add_f=ADD_F)
    tris += polar_prof_solid(prof,0,t,bore=BORE)
    ang=np.deg2rad(STN_M); cx,cy=SUNORB*np.cos(ang),SUNORB*np.sin(ang)
    tris += cylinder(cx,cy,3.5,t,t+0.5,seg=32)        # seat shoulder (assembly 9-9.5)
    tris += cylinder(cx,cy,PIV_R,t,7.5,seg=48)         # bearing post to assembly 12.5 (local 7.5)
    write_stl("02h_board_v16.stl",tris)

def part_42_sun_multilevel(bands=None, tooth_frac=0.32):
    """Multi-level sun (finding #107; RE-TUNED #108 from Ron's core print). FULL 7t
    gear bands (root 7.4, tip 9.55) at each satellite mesh altitude; SLIM core at the
    strike-finger altitudes so fingers sweep past close to center.
    #108 changes from Ron's bench feedback:
      - SLIM cores TALLER (3.0mm vs 2.0) and full bands spaced 4.5mm apart, so the
        strike fingers have vertical room to pass between bands (they were binding).
      - SLIM radius 4.7 (was 5.0): finger reach 5.47 now clears by 0.77mm (was 0.47).
      - Sun teeth thinned (tooth_frac 0.32 vs 0.40) for real mesh BACKLASH — the
        printed gears over-engaged and bound. Pair with XY compensation on the print."""
    import numpy as np
    from generator import gear_profile, _stitch, P
    SUN_ROOT, SUN_TIP, CORE_R, HW = 7.4, 9.55, 4.7, 2.25
    if bands is None:
        # sun LOCAL z (seats at assembly 9.5). #108: full 1.5mm, slim 3.0mm, sats 4.5 apart.
        #   month full 0-1.5 / slim 1.5-4.5 ; feb full 4.5-6 / slim 6-9 ; leap full 9-10.5 / slim 10.5-13.5
        bands = [(0.0,1.5,'full'),(1.5,4.5,'slim'),(4.5,6.0,'full'),
                 (6.0,9.0,'slim'),(9.0,10.5,'full'),(10.5,13.5,'slim')]
    seg = P["seg"]
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    ri = np.array([HW/max(abs(np.cos(a)),abs(np.sin(a))) for a in th])   # square bore
    inner = list(np.stack([ri*np.cos(th), ri*np.sin(th)],1))
    full = gear_profile(P["sun_teeth"], SUN_ROOT, SUN_TIP, tooth_frac=tooth_frac, ramp_frac=0.2)
    slim = np.full(seg, CORE_R)
    tris=[]
    for z0,z1,kind in bands:
        prof = full if kind=='full' else slim
        outer = list(np.stack([prof*np.cos(th), prof*np.sin(th)],1))
        tris += _stitch(outer, inner, z0, z1)
    write_stl("42_sun_v16.stl", tris)

if __name__=="__main__":
    part_02e_board_bigbore_v16(); part_02f_board_v16()
    part_50d_star_hub_v16(); part_49_fixture_r58_v16()
    print("clearances:")
    print("  tube rides post:", 4.35>4.15, "(ID r4.35 vs post r4.15, 0.2 bearing)")
    print("  tube wall:", round(TUBE_OD-TUBE_ID,2), "mm (printable)")
    print("  disc clears post:", TUBE_OD>4.15)
