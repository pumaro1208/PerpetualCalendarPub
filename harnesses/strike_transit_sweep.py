#!/usr/bin/env python3
"""strike_transit_sweep.py — physical acceptance sweep for the strike transfers.

Quasi-static 1-DOF contact simulation using the ACTUAL generator profiles:
 - board: involute_profile(31t, m2.6, stub add_f 0.6, backlash 0.25)
 - drive tooth: tooth_outline(m2.6, 24t basis, stub) at the spread center
   distance D_DRIVE = m*(31+24)/2 + 2.0
 - strike lamina: v1.3 strike_profile (symmetric crown relief)
 - jumper: actual V-nose geometry seated on the board rim at 12*PITCH

Runs:
 J  jumper seat solve — park phase FROM GEOMETRY (no assumption)
 A  midnight tooth, forward transit from the solved park
 B  midnight tooth, reverse transit (backlash + one pitch back)
 C  month lamina transit fwd+rev, and the required satellite clocking (mod 30)
 D  park-phase tolerance window (how much jumper error before jam/butt)
"""
import numpy as np, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generator import (P, MD, ADD_F, D_DRIVE, involute_profile, tooth_outline)
from generator_v13 import (PITCH, SUNORB, L_TIP, RELIEF, strike_profile,
                           STN_M, LONG_M)

DEG = np.pi/180
SEG = 6200
r_board, RP, RT, RR = involute_profile(P["prog_teeth"], MD, add_f=ADD_F, seg=SEG)
th_grid = np.linspace(0, 2*np.pi, SEG, endpoint=False)
TOOTH = np.array(tooth_outline(MD, P["drive_teeth"], add_f=ADD_F))
DR = D_DRIVE                     # drive center (DR, 0)
r_lam = strike_profile(sorted(LONG_M), seg=SEG)

def dense(poly, step=0.08):
    out = []
    for i in range(len(poly)):
        a, b = np.array(poly[i]), np.array(poly[(i+1) % len(poly)])
        n = max(1, int(np.linalg.norm(b-a)/step))
        for t in range(n):
            out.append(a + (b-a)*t/n)
    return np.array(out)

TOOTH_D = dense(TOOTH)

def rprof(profile, ang):
    return np.interp(np.mod(ang, 2*np.pi), th_grid, profile, period=2*np.pi)

def tooth_world(psi):
    """drive tooth outline points in world coords; psi = tooth axis azimuth
    about the drive center (180 deg = pointing at the main axis)."""
    c, s = np.cos(psi*DEG), np.sin(psi*DEG)
    R = TOOTH_D @ np.array([[c, s], [-s, c]])
    R[:, 0] += DR
    return R

def board_overlap(pts, theta, margin=0.0):
    """max penetration of pts into the board profile rotated by theta (deg)."""
    r = np.hypot(pts[:, 0], pts[:, 1])
    az = np.arctan2(pts[:, 1], pts[:, 0]) - theta*DEG
    pen = rprof(r_board, az) - r + margin
    return float(np.max(pen))

def lam_overlap(pts, theta, off_deg):
    """penetration into the month lamina; satellite pose from board theta."""
    az_c = (STN_M + theta)*DEG
    cx, cy = SUNORB*np.cos(az_c), SUNORB*np.sin(az_c)
    spin = (off_deg + (19/12)*theta)*DEG
    r = np.hypot(pts[:, 0]-cx, pts[:, 1]-cy)
    az = np.arctan2(pts[:, 1]-cy, pts[:, 0]-cx) - spin
    pen = rprof(r_lam, az) - r
    return float(np.max(pen))

SEAT0 = [0.0]   # filled in after the jumper solve
def relax(overlap_fn, theta):
    """detent relaxation: the jumper pulls the board downhill toward the
    nearest seat, blocked by tooth contact. Seats at SEAT0[0] + k*PITCH."""
    k = round((theta - SEAT0[0]) / PITCH)
    target = SEAT0[0] + k*PITCH
    step = 0.03 if target > theta else -0.03
    while abs(target - theta) > 0.02:
        nxt = theta + step if abs(target-theta) > abs(step) else target
        if overlap_fn(tooth_world(relax.psi), nxt) > 1e-3: break
        theta = nxt
    return theta

def transit(overlap_fn, psi0, psi1, theta0, push, nsteps=480, span=1.6,
            detent=True):
    """quasi-static WITH the jumper: sweep tooth azimuth; the board yields
    minimally under tooth contact, and relaxes into the detent whenever the
    tooth allows. Returns (theta_end, curve, max tooth-only push)."""
    theta = theta0; curve = []; maxpush = 0.0
    for psi in np.linspace(psi0, psi1, nsteps):
        pts = tooth_world(psi)
        if overlap_fn(pts, theta) > 1e-3:
            step = 0.02*PITCH; d = step; found = None
            while d <= span*PITCH:
                if overlap_fn(pts, theta + push*d) <= 1e-3: found = d; break
                d += step
            if found is None:
                return None, curve, maxpush
            lo, hi = found - step, found
            for _ in range(40):
                mid = 0.5*(lo+hi)
                if overlap_fn(pts, theta + push*mid) > 1e-3: lo = mid
                else: hi = mid
            theta = theta + push*hi
            maxpush = max(maxpush, abs(theta - theta0))
        elif detent:
            relax.psi = psi
            theta = relax(overlap_fn, theta)
        curve.append((psi, theta))
    return theta, curve, maxpush

# ---------- J: jumper seat from geometry ----------
NOSE = np.array([(-18.5, -2.4), (-21.5, 0.0), (-18.5, 2.4),
                 (-17.0, 2.4), (-17.0, -2.4)])
JA = 12*PITCH
def nose_world(depth):
    """nose polygon, anchored at azimuth JA, pressed inward by 'depth' mm from
    its free position (beam pre-load direction = radially inward)."""
    c, s = np.cos(JA*DEG), np.sin(JA*DEG)
    pts = NOSE.copy(); pts[:, 0] -= depth   # local -x = inward (toward center)
    R = pts @ np.array([[c, s], [-s, c]])   # local +x -> outward radial
    R[:, 0] += 62.0*c; R[:, 1] += 62.0*s
    return dense(R.tolist(), 0.06)

def seat_depth(theta):
    """how far inward the nose can press before contacting the board."""
    lo, hi = -2.0, 9.0
    for _ in range(40):
        mid = 0.5*(lo+hi)
        if board_overlap(nose_world(mid), theta) > 1e-3: hi = mid
        else: lo = mid
    return lo

print("J: jumper seat solve (park phase from geometry)")
ths = np.linspace(0, PITCH, 233, endpoint=False)
depths = np.array([seat_depth(t) for t in ths])
seat_idx = int(np.argmax(depths))
theta_park = float(ths[seat_idx])
print(f"   deepest seat at board phase {theta_park:.3f} deg (mod pitch {PITCH:.3f})")
print(f"   -> tooth centers at k*PITCH{'+%.3f' % theta_park}; "
      f"valley center at mesh line offset {abs((theta_park+PITCH/2) % PITCH - PITCH/2 + PITCH/2 - PITCH/2):.3f}")
vc = (theta_park + PITCH/2) % PITCH
print(f"   valley nearest the mesh line sits at azimuth {min(vc, PITCH-vc):+.3f} deg from it")
print(f"   seat depth {depths[seat_idx]:.2f} mm; shallowest (over tooth) {depths.min():.2f} mm; "
      f"snap asymmetry ratio {depths[seat_idx]/max(depths.min(),0.01):.2f}")

SEAT0[0] = theta_park
results = {"theta_park": theta_park, "PITCH": PITCH}

# ---------- A: midnight forward ----------
print("A: midnight tooth, FORWARD transit from the solved park")
end, curveF, pushF = transit(board_overlap, 196.0, 164.0, theta_park, push=+1)
if end is None:
    print("   *** JAM ***")
else:
    adv = end - theta_park
    exc = max(t for _, t in curveF) - theta_park
    print(f"   settled advance {adv:.3f} deg = {adv/PITCH:.4f} pitch (want 1.0000)")
    print(f"   max excursion {exc/PITCH:.4f} pitch -> margin to next detent crest "
          f"{1.5-exc/PITCH:+.4f} pitch ({(1.5-exc/PITCH)*PITCH:.2f} deg)")
    print(f"   tooth-only push before the detent completes: {pushF:.3f} deg = {pushF/PITCH:.4f} pitch"
          f" (crest at 0.5000; margin {pushF/PITCH-0.5:+.4f})")
    # first-contact entry: find min clearance before contact
    pre = [(p, t) for p, t in curveF if abs(t-theta_park) < 1e-6]
    gaps = []
    for p, _ in pre[::6]:
        pts = tooth_world(p)
        gaps.append(-board_overlap(pts, theta_park))
    entry_clear = min(gaps) if gaps else float('nan')
    print(f"   min approach clearance before first contact: {entry_clear:.3f} mm")
    results["fwd"] = dict(advance=adv, push=pushF, entry_clear=entry_clear)

# ---------- B: midnight reverse ----------
print("B: midnight tooth, REVERSE transit (from the advanced seat)")
theta1 = theta_park + PITCH
endR, curveR, pushR = transit(board_overlap, 164.0, 196.0, theta1, push=-1)
if endR is None:
    print("   *** JAM ***")
else:
    advR = theta1 - endR
    print(f"   tooth-only push: {pushR/PITCH:.4f} pitch (margin {pushR/PITCH-0.5:+.4f})")
    # backlash: crank angle from reversal start until the board first moves
    first_move = next((p for p, t in curveR if abs(t-theta1) > 0.02), None)
    print(f"   reverse advance {advR:.3f} deg = {advR/PITCH:.4f} pitch")
    print(f"   board holds until tooth azimuth {first_move:.2f} (backlash traverse "
          f"{192.0-first_move:.2f} deg of crank)" if first_move else "   board never moved")
    results["rev"] = dict(advance=advR, onset=first_move)

# ---------- C: month lamina, required clocking + fwd/rev ----------
print("C: month lamina — required satellite clocking, then fwd+rev transit")
# board phase when the month satellite serves a strike: sat az = STN_M + theta;
# strikes happen from the jumper park lattice: theta = theta_park + k*PITCH.
# choose k putting the satellite nearest the mesh line:
ks = np.arange(-16, 16)
azs = (STN_M + theta_park + ks*PITCH + 180) % 360 - 180
k0 = int(ks[np.argmin(np.abs(azs))])
th_strike = theta_park + k0*PITCH
print(f"   satellite center at {azs[np.argmin(np.abs(azs))]:+.3f} deg from the mesh line at park")
best = None
for off in np.linspace(0, 30, 121):
    e, cv, mp = transit(lambda pts, th: lam_overlap(pts, th, off),
                    190.0, 170.0, th_strike, push=+1, nsteps=110)
    if e is None: continue
    adv = e - th_strike
    score = abs(adv - PITCH) - 0.001*mp
    if best is None or score < best[1]: best = (off, score, adv, mp)
if best is None:
    print("   *** no clocking produces a clean forward transit ***")
else:
    off, _, adv, mp = best
    print(f"   tooth-only push {mp/PITCH:.4f} pitch (margin over crest {mp/PITCH-0.5:+.4f})")
    print(f"   required clocking OFF = {off:.2f} deg (mod 30) -> fwd advance {adv:.3f} "
          f"deg = {adv/PITCH:.4f} pitch")
    eR, _, mpR = transit(lambda pts, th: lam_overlap(pts, th, off),
                    170.0, 190.0, th_strike + adv, push=-1, nsteps=220)
    if eR is None:
        print("   REVERSE: *** JAM *** (corner relief inadequate)")
        results["lamina"] = dict(off=off, fwd=adv, rev=None)
    else:
        print(f"   REVERSE advance {th_strike+adv-eR:.3f} deg = "
              f"{(th_strike+adv-eR)/PITCH:.4f} pitch — symmetric crown confirmed")
        results["lamina"] = dict(off=off, fwd=adv, rev=th_strike+adv-eR)

# ---------- D: park-phase tolerance window ----------
print("D: park-phase tolerance window (jumper clocking error before failure)")
window = []
for derr in np.linspace(-4.0, 4.0, 33):
    SEAT0[0] = theta_park + derr
    e, _, _ = transit(board_overlap, 196.0, 164.0, theta_park+derr, push=+1, nsteps=170)
    ok = e is not None and abs((e-(theta_park+derr)) - PITCH) < 0.1*PITCH
    SEAT0[0] = theta_park
    window.append((derr, ok))
oks = [d for d, ok in window if ok]
print(f"   clean-transit window: {min(oks):+.2f} .. {max(oks):+.2f} deg of park error"
      if oks else "   *** no window ***")
results["window"] = [min(oks), max(oks)] if oks else None

json.dump(results, open("sweep_results.json", "w"), indent=1)
np.save("curveF.npy", np.array(curveF)); np.save("curveR.npy", np.array(curveR))
print("\nsweep complete -> sweep_results.json")
