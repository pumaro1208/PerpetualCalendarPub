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
    prof = MI.inv_shift_profile(MI.N_SUN, x=+0.40, tip_cap=MI.SUN_TIP_CAP, root_r=MI.SUN_ROOT, backlash=BL)
    tris = polar_prof_solid(prof, 0.0, 5.0, bore=2.70)
    write_stl("115_meshtest_sun7t_inv_v16.stl", tris)

def part_sat():
    prof = MI.inv_shift_profile(MI.N_SAT, x=0.0, tip_cap=MI.SAT_TIP_CAP, root_r=MI.SAT_ROOT, backlash=BL)
    tris = polar_prof_solid(prof, 0.0, 5.0, bore=2.70)
    tris += cylinder(9.0, 0.0, 2.5, 5.0, 11.0, seg=24)       # grip pin to turn it
    write_stl("115_meshtest_sat12t_inv_v16.stl", tris)

if __name__=="__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    part_base(); part_sun(); part_sat()
    print("  wrote mesh-test coupon (base + 7t sun + 12t sat), CD 23.75, posts r2.65 bore 2.70")
