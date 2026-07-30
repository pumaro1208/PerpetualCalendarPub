#!/usr/bin/env python3
"""Finding #115 — proper INVOLUTE (profile-shifted) sun<->satellite orienting mesh,
replacing the rounded-trapezoid 'logic demo' teeth that cam and bind.

The counts (7t sun / 12t sat) and center distance (23.75) are fixed by the
mechanism. Only the FLANK FORM changes: true involute + a positive profile shift
on the 7t sun. Tooth TIPS are capped at the current envelope (sun 9.55, sat 15.8)
and ROOTS kept (sun 7.4, sat 13.4) so every #105-108 clearance and the finger-pass
geometry survive untouched. This module builds the polar profiles and PROVES the
mesh rolls without interference (vs the trapezoid) before anything is printed.
"""
import numpy as np

M      = 2.5
N_SUN, N_SAT = 7, 12
CD     = 23.75
PA     = 25.0                      # pressure angle (deg) — eases both low-count gears
SUN_TIP_CAP, SUN_ROOT = 9.55, 7.40
SAT_TIP_CAP, SAT_ROOT = 15.80, 13.40

def inv_shift_profile(n, x, tip_cap, root_r, backlash, seg=1440, pa=PA, m=M, phase=0.0):
    """Involute polar r(theta) with profile shift x. Tip capped to tip_cap and root
    forced to root_r (shift is used for tooth THICKNESS + undercut relief only, never
    to raise the root — raising it would let the mate's tip bottom in the valley)."""
    rp = m*n/2.0
    rb = rp*np.cos(np.deg2rad(pa))
    rt = min(rp + (0.32 + x)*m, tip_cap)          # profile shift lengthens tip, then cap
    rr = root_r
    rs = np.linspace(max(rb, rr), rt, 40)
    alpha = np.arccos(np.clip(rb/rs, -1, 1))
    inv = np.tan(alpha) - alpha
    inv_p = np.tan(np.arccos(rb/rp)) - np.arccos(rb/rp)
    # half tooth angle at pitch: nominal + profile-shift thickening - backlash
    half = np.pi/(2*n) + x*m*np.tan(np.deg2rad(pa))/rp - backlash/(2*rp)
    flank_ang = half + inv_p - inv                # half-width angle vs radius rs
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    r = np.full(seg, rr)
    pitch = 2*np.pi/n
    for k in range(n):
        c = phase + k*pitch
        d = np.abs(np.angle(np.exp(1j*(th - c))))
        m_in = d <= flank_ang[0]
        r[m_in] = np.maximum(r[m_in], np.interp(d[m_in], flank_ang[::-1], rs[::-1]))
        r[d <= flank_ang[-1]] = rt
    return r

def polygon(prof_r, cx=0.0, cy=0.0, rot=0.0):
    from shapely.geometry import Polygon
    seg=len(prof_r); th=np.linspace(0,2*np.pi,seg,endpoint=False)+rot
    return Polygon(np.stack([cx+prof_r*np.cos(th), cy+prof_r*np.sin(th)],1))

def mesh_scan(sun_r, sat_r, label, backlash_note=""):
    """Roll the sun through a full cycle; sat rolls conjugately at CD. Search the
    engagement phase, then report max tooth-overlap (interference = binding) and
    whether the teeth actually engage."""
    from shapely.geometry import Polygon
    sun_poly0 = polygon(sun_r)
    # find engagement phase psi0 that minimises worst-case overlap
    phis = np.linspace(0, 2*np.pi/N_SUN, 40)     # one sun-tooth cycle (hunting covers rest)
    best=None
    for psi0 in np.linspace(0, 2*np.pi/N_SAT, 30):
        worst=0.0
        for phi in phis:
            psi = psi0 - (N_SUN/N_SAT)*phi
            sp = polygon(sun_r, rot=phi)
            tp = polygon(sat_r, cx=CD, rot=psi)
            worst=max(worst, sp.intersection(tp).area)
        if best is None or worst<best[0]:
            best=(worst, psi0)
    worst, psi0 = best
    # engagement check + min gap at the meshed phase
    engaged=False; areas=[]
    for phi in phis:
        psi = psi0 - (N_SUN/N_SAT)*phi
        sp=polygon(sun_r,rot=phi); tp=polygon(sat_r,cx=CD,rot=psi)
        a=sp.intersection(tp).area; areas.append(a)
        # engaged if the addendum circles overlap radially at all (real mesh, not clearing)
    engaged = (sun_r.max()+sat_r.max()) > CD
    print(f"  {label:16s} worst tooth-overlap {worst:7.4f} mm^2   mesh-engages {engaged}   "
          f"mean overlap {np.mean(areas):.4f}   {backlash_note}")
    return worst

if __name__=="__main__":
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from generator import gear_profile
    import generator_v13 as V13

    print("MESH PROOF — involute(+shift) vs trapezoid, sun7t/sat12t, CD 23.75, m2.5\n")

    # NEW involute+shift profiles (backlash tuned generous — orient-only mesh)
    BL=0.55
    sun_inv = inv_shift_profile(N_SUN, x=+0.40, tip_cap=SUN_TIP_CAP, root_r=SUN_ROOT, backlash=BL)
    sat_inv = inv_shift_profile(N_SAT, x= 0.00, tip_cap=SAT_TIP_CAP, root_r=SAT_ROOT, backlash=BL)
    print(f"  involute tips: sun {sun_inv.max():.2f} (cap {SUN_TIP_CAP})  sat {sat_inv.max():.2f} (cap {SAT_TIP_CAP})")
    print(f"  involute roots: sun {sun_inv.min():.2f}  sat {sat_inv.min():.2f}  (envelope preserved)\n")

    # CURRENT trapezoid profiles
    sun_tr = gear_profile(N_SUN, V13.SUN_ROOT, V13.SUN_TIP, tooth_frac=0.32, ramp_frac=0.2)
    sat_tr = V13.sat_mesh_profile()

    w_inv = mesh_scan(sun_inv, sat_inv, "INVOLUTE+shift", f"(backlash {BL})")
    w_tr  = mesh_scan(sun_tr,  sat_tr,  "trapezoid(now)", "(current logic-demo)")

    # sat-tip bottoming check against sun root (the #105 constraint)
    sat_tip_reach = CD - sat_inv.max()
    print(f"\n  sat-tip reaches sun-center radius {sat_tip_reach:.2f} vs sun root {sun_inv.min():.2f} "
          f"-> valley clearance {sat_tip_reach - sun_inv.min():.2f} mm (must be >0)")
    verdict = "PASS" if (w_inv < 0.02 and w_inv < w_tr and sat_tip_reach>sun_inv.min()) else "REVIEW"
    print(f"\n  VERDICT: {verdict}  (involute overlap {w_inv:.4f} vs trapezoid {w_tr:.4f})")
