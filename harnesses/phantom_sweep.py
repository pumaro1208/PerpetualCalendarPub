#!/usr/bin/env python3
"""phantom_sweep.py — the complement of the strike-transit sweep.

Verifies WATERSHED GATING on the real profiles: over a FULL YEAR of board
parks (372 steps), every drive-tooth pass that should NOT strike must clear
its lamina by a printable margin. Enumerates:
 P1 month lamina (5 teeth) vs the 23h tooth — all passes, all park evenings
 P2 feb lamina (1 tooth)  vs the 22h tooth — incl. the 30-deg phase-cycle
    phantoms (the presentation phase advances 210 deg per monthly pass)
 P3 leap slider vs the 21h tooth — ARMED must reach, RETRACTED must clear,
    swept across cam travel values (v1.5 follower stroke = 1.6 mm)
Also derives the assembly clocking windows (OFF specs) for feb and leap:
exactly ONE strike-capable pass per year, all others gated.
"""
import numpy as np, sys, json
sys.path.insert(0, '.')
import strike_transit_sweep as S
from strike_transit_sweep import (transit, tooth_world, dense, rprof,
                                  th_grid, PITCH)
from generator_v13 import STN_M, STN_F, STN_L, LONG_M, L_TIP, RELIEF, SUNORB
import matplotlib.path as mpath

res = json.load(open("sweep_results.json"))
TP = res["theta_park"]; S.SEAT0[0] = TP
YEAR = 372                                   # board steps per year (12 x 31)

def lam_profile(long_ks, seg=6200):
    th = np.linspace(0, 2*np.pi, seg, endpoint=False); hub = 8.0
    r = np.full(seg, hub)
    for k in long_ks:
        c = k*np.pi/6; d = np.angle(np.exp(1j*(th-c)))
        half, ramp = np.deg2rad(5.0), np.deg2rad(4.5)
        u = (np.abs(d)-half)/ramp; w = np.clip(1-u, 0, 1); w = w*w*(3-2*w)
        tip = np.full(seg, L_TIP)
        frac = np.clip((np.abs(d)-half*0.25)/(half*0.75), 0, 1)
        tip -= RELIEF*frac
        r = np.maximum(r, hub + (tip-hub)*w)
    return r

def clearance_polar(prof, stn, off, theta, psis):
    """min clearance (+) / max penetration (-) of the drive tooth path vs a
    polar lamina, board FIXED at theta (phantom rule: no yielding)."""
    az_c = (stn+theta)*np.pi/180
    cx, cy = SUNORB*np.cos(az_c), SUNORB*np.sin(az_c)
    spin = (off + (19/12)*theta)*np.pi/180
    worst = 1e9
    for psi in psis:
        p = tooth_world(psi)
        r = np.hypot(p[:, 0]-cx, p[:, 1]-cy)
        az = np.arctan2(p[:, 1]-cy, p[:, 0]-cx) - spin
        gap = r - rprof(prof, az)
        worst = min(worst, float(np.min(gap)))
    return worst

PSIS = np.linspace(196, 164, 65)

def year_scan(prof, stn, off, label, expect_strikes):
    """clearance at every park of the year where the satellite is near the
    mesh; classify strike-capable vs gated passes."""
    contacts, worst_clear, worst_at = [], 1e9, None
    for n in range(YEAR):
        theta = TP + n*PITCH
        az = (stn + theta + 180) % 360 - 180
        if abs(az) > 26: continue
        c = clearance_polar(prof, stn, off, theta, PSIS)
        if c < 0.02: contacts.append((n, az, c))
        elif c < worst_clear: worst_clear, worst_at = c, (n, az)
    print(f"  {label}: {len(contacts)} contact pass(es)/yr "
          f"(expect {expect_strikes}); tightest GATED clearance "
          f"{worst_clear:.3f} mm at sat az {worst_at[1]:+.1f} deg" if worst_at
          else f"  {label}: {len(contacts)} contact pass(es), no near misses")
    return contacts, worst_clear

print("P1: month lamina (5 teeth) vs the 23h tooth — full-year phantom scan")
prof_m = lam_profile(sorted(LONG_M))
cm, wc_m = year_scan(prof_m, STN_M, 9.75, "month, OFF=9.75", "5")

print("P2: feb lamina (1 tooth) vs the 22h tooth — OFF spec + phantoms")
prof_f = lam_profile({0})
cands = []
for off in np.linspace(0, 360, 241):
    contacts = 0; wc = 1e9
    for n in range(YEAR):
        theta = TP + n*PITCH
        az = (STN_F + theta + 180) % 360 - 180
        if abs(az) > 26: continue
        c = clearance_polar(prof_f, STN_F, off, theta, PSIS[::4])
        if c < 0.02: contacts += 1
        else: wc = min(wc, c)
    if contacts == 1: cands.append((off, wc))
if cands:
    offs = [c[0] for c in cands]
    best = max(cands, key=lambda c: c[1])
    print(f"  OFF windows with exactly 1 strike/yr: {len(cands)} of 241 sampled")
    print(f"  best OFF={best[0]:.1f}: tightest gated clearance {best[1]:.3f} mm")
    cf, wc_f = year_scan(prof_f, STN_F, best[0], f"feb, OFF={best[0]:.1f}", "1")
else:
    print("  *** no OFF yields exactly one strike/yr ***"); wc_f = -1

print("P3: leap slider vs the 21h tooth — armed reach / retracted clearance")
NOSE = [(16.2, -2.0), (17.91, -1.0), (18.11, 0.6), (16.2, 2.0)]
def leap_clearance(theta, off, retract, psis):
    az_c = (STN_L+theta)*np.pi/180
    cx, cy = SUNORB*np.cos(az_c), SUNORB*np.sin(az_c)
    spin = (off + (19/12)*theta)*np.pi/180
    c, s = np.cos(spin), np.sin(spin)
    pts = np.array([(x-retract, y) for x, y in NOSE])
    W = pts @ np.array([[c, s], [-s, c]]); W[:, 0] += cx; W[:, 1] += cy
    nose_d = dense(W.tolist(), 0.05)
    path = mpath.Path(np.vstack([W, W[:1]]))
    worst = 1e9
    for psi in psis:
        p = tooth_world(psi)
        d = np.sqrt(((p[:, None, :]-nose_d[None, :, :])**2).sum(-1)).min()
        if path.contains_points(p).any(): d = -d
        worst = min(worst, float(d))
    return worst
# find the leap strike park + a strike-capable OFF (armed)
best_l = None
for off in np.linspace(0, 360, 121):
    for n in range(YEAR):
        theta = TP + n*PITCH
        az = (STN_L + theta + 180) % 360 - 180
        if abs(az) > 8: continue
        c = leap_clearance(theta, off, 0.0, PSIS[::4])
        if c < -0.6:
            if best_l is None: best_l = (off, theta, az, c)
for label, rt in (("armed (0.0)", 0.0), ("retract 1.2", 1.2),
                  ("retract 1.6", 1.6), ("retract 2.0", 2.0)):
    if best_l is None: break
    off, theta, az, _ = best_l
    c = leap_clearance(theta, off, rt, PSIS)
    kind = "ENGAGES" if c < 0 else "clears by"
    print(f"  {label} mm at the strike park (sat az {az:+.1f}): {kind} {abs(c):.3f} mm")

json.dump(dict(month_gated=wc_m, feb_gated=wc_f), open("phantom_results.json", "w"))
print("\nphantom sweep complete")
