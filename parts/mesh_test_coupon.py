#!/usr/bin/env python3
"""#115 mesh-test coupon — spin the new INVOLUTE sun<->sat mesh by hand.

Self-contained: a base with two posts at the true center distance (23.75), a 7t
profile-shifted involute sun on one, a 12t involute gear (with a grip pin) on the
other. Drop both on, mesh them, and turn the 12t by its pin — you're feeling the
new flank form (should roll smooth) against the old trapezoid you've been fighting.
Posts are the won r2.65 fit; bores 2.70. Print the two gears loose + the base.
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generator import cylinder, box
from generator_v13 import write_stl, polar_prof_solid
import mesh_involute as MI

BL = 0.55
CD = MI.CD                      # 23.75
SX = CD/2.0                     # posts at +-11.875

def part_base():
    tris=[]
    tris += box(0,0, 66, 42, 0.0, 3.0)                       # base slab
    for sx in (-SX, +SX):
        tris += cylinder(sx,0, 3.5, 3.0, 3.5, seg=32)        # seat shoulder r3.5
        tris += cylinder(sx,0, 2.65, 3.0, 8.0, seg=48)       # won r2.65 bearing post
    write_stl("115_meshtest_base_v16.stl", tris)

def part_sun():
    """MATCHED to the engine: the real multi-level sun's month section in involute
    form -- one FULL involute band (z0-1.5, the mesh) + its SLIM core (z1.5-4.5, where
    the receiver's fingers sweep past). Round bore 2.70 here so it spins free on the
    coupon (the engine's is square/fixed). Seats at z3.5 -> full band 3.5-5.0."""
    from generator import _stitch, P
    SUN_ROOT, SUN_TIP, CORE_R = 7.4, 9.55, 4.7
    seg = P["seg"]; th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    full = MI.inv_shift_profile(MI.N_SUN, x=0.0, tip_cap=SUN_TIP, root_r=SUN_ROOT, backlash=BL, seg=seg)
    slim = np.full(seg, CORE_R)
    ri = np.full(seg, 2.70)
    inner = list(np.stack([ri*np.cos(th), ri*np.sin(th)], 1))
    def band(prof, z0, z1):
        return _stitch(list(np.stack([prof*np.cos(th), prof*np.sin(th)],1)), inner, z0, z1)
    # #117: full band shortened 1.5 -> 1.0 so its TOP drops 0.5mm below the receiver
    # finger bottom -> vertical clearance for the finger (was zero-margin = the collision).
    # x dropped to 0 too (the shift fattened the tooth and bound — finding #116).
    tris  = band(full, 0.0, 1.0)      # full involute band (meshes) — shorter, on the bed
    tris += band(slim, 1.0, 4.5)      # slim core starts 0.5mm lower: finger clearance
    write_stl("115_meshtest_sun_piece_inv_v16.stl", tris)

def part_sat():
    """MATCHED: the real compact receiver in involute form -- involute mesh lamina
    (z0-1.5) + hub + solid finger bars (z1.5-3.0), bore 2.70. Seats at z3.5 -> mesh
    lamina 3.5-5.0 (meets the sun full band); fingers 5.0-6.5 face the sun slim core."""
    from generator import polar_solid, _poly_prism, P
    from generator_v16 import rbox, E1_BASE, d2r
    seg = P["seg"]; ZM, ZS = 1.5, 3.0; TIP_R = 18.3
    prof = MI.inv_shift_profile(MI.N_SAT, x=0.0, tip_cap=MI.SAT_TIP_CAP, root_r=MI.SAT_ROOT, backlash=BL, seg=seg)
    tris  = polar_prof_solid(prof, 0.0, ZM, bore=2.70)                    # involute mesh lamina
    tris += polar_solid(np.full(seg, 4.0), ZM, ZS, r_inner=2.70)         # hub
    for k in range(MI.N_SAT // 2):                                        # solid finger bars (every 30 deg)
        a = (E1_BASE + k*30.0)*d2r; ad = np.degrees(a)
        # #117: inner finger (r4->16) full-height, backed by the mesh lamina to r15.8 (no droop).
        rmid = (4.0+16.0)/2
        tris += rbox(rmid*np.cos(a), rmid*np.sin(a), ad, 16.0-4.0, 4.5, ZM, ZS)
        # overhanging TIP (r15.5->18.3) raised to z2.2 so its unsupported bridge droops well
        # clear of the sun full band instead of onto it.
        rmt = (15.5+TIP_R)/2
        tris += rbox(rmt*np.cos(a), rmt*np.sin(a), ad, TIP_R-15.5, 4.5, 2.2, ZS)
    ag = (E1_BASE + 15.0)*d2r                                             # grip pin in a finger gap
    tris += cylinder(10.0*np.cos(ag), 10.0*np.sin(ag), 2.5, ZM, 7.5, seg=24)
    write_stl("115_meshtest_receiver_inv_v16.stl", tris)

if __name__=="__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    part_base(); part_sun(); part_sat()
    print("  wrote mesh-test coupon (base + 7t sun + 12t sat), CD 23.75, posts r2.65 bore 2.70")
