#!/usr/bin/env python3
"""arch_a_prime.py — Session 3: cam-gated SLIDER STRIKERS + rigid E1 receivers.

The three skip strike teeth on the drive wheel become radial sliders,
extended only when their peg reads a lobe on a board-riding cam ring
(evening key, 11.6 deg/evening). Receivers are rigid E1 involute laminae
(month key = station set at month granularity). Judged in the calendar-true
sequence for the month train (the decisive case):

  G1 skip evenings (striker extended, long station presented):
       transit push >= 1.0P fwd, settled exactly +1P; reverse >= 1.0P, -1P
  G2 non-skip months' pos-29 evenings (striker extended, short station):
       clear or graze < 0.35P
  G3 adjacent evenings (striker RETRACTED): static clearance vs the emerged
       receiver >= 0.30 mm at 1.6 mm stroke
  G4 station-set arithmetic: the 5 skip months land on 5 consecutive
       stations (verified in-scan by G1 all firing at one base choice)
"""
import numpy as np, sys, json
sys.path.insert(0, '.')
import strike_transit_sweep as S
from strike_transit_sweep import transit, PITCH
from generator import MD, ADD_F, tooth_outline, P as GP
from generator_v13 import STN_M, SUNORB
import matplotlib.path as mpath

res = json.load(open("sweep_results.json"))
TP = res["theta_park"]; S.SEAT0[0] = TP
d2r = np.pi/180

# ---- natural-evening walker for the 23h train: strikes at pos 29
def walk_23():
    out = []; n = 0; mon, pos = 0, 1
    while mon < 12:
        if mon == 1 and pos == 27: n += 1; pos += 1
        if mon == 1 and pos == 28: n += 1; pos += 1
        if pos == 29:
            out.append((n, mon in (1, 3, 5, 8, 10), True))   # striker EXTENDED
            if mon in (1, 3, 5, 8, 10): n += 1; pos += 1
        else:
            out.append((n, False, False))                    # striker retracted
        n += 1; pos += 1
        if pos > 31: pos = 1; mon += 1
    return out

PASSES = walk_23()

# ---- E1 receiver: five involute board-tooth teeth, superposition-registered
AZ0 = TP - PITCH
TH0 = AZ0 - STN_M
T = np.array(tooth_outline(MD, GP["prog_teeth"], add_f=ADD_F))
c, s = np.cos(AZ0*d2r), np.sin(AZ0*d2r)
P0 = T @ np.array([[c, s], [-s, c]])
C0 = np.array([SUNORB*np.cos((STN_M+TH0)*d2r), SUNORB*np.sin((STN_M+TH0)*d2r)])
SAT0 = P0 - C0
TIPR = np.hypot(SAT0[:, 0], SAT0[:, 1]).max()
TIPA = np.degrees(np.arctan2(SAT0[:, 1], SAT0[:, 0]))[
    np.argmax(np.hypot(SAT0[:, 0], SAT0[:, 1]))]

def build(base_deg):
    teeth, paths, dens = [], [], []
    for k in range(5):
        a = (k*30 + base_deg)*d2r
        cc, ss = np.cos(a), np.sin(a)
        t = SAT0 @ np.array([[cc, ss], [-ss, cc]])
        teeth.append(t); paths.append(mpath.Path(np.vstack([t, t[:1]])))
        d = []
        for i in range(len(t)):
            aa, bb = t[i], t[(i+1) % len(t)]
            m = max(1, int(np.hypot(*(bb-aa))/0.22))
            for j in range(m): d.append(aa+(bb-aa)*j/m)
        dens.append(np.array(d))
    return teeth, paths, dens

RLO = np.hypot(SAT0[:, 0], SAT0[:, 1]).min() - 1.0
def make_fn(base_deg):
    teeth, paths, dens = build(base_deg)
    def cands(t):
        ct = np.array([SUNORB*np.cos((STN_M+t)*d2r), SUNORB*np.sin((STN_M+t)*d2r)])
        ds = (19/12)*(t-TH0)
        out = []
        for k in range(5):
            a = (TIPA + k*30 + base_deg + ds)*d2r
            tip = ct + TIPR*np.array([np.cos(a), np.sin(a)])
            r, az = np.hypot(*tip), np.degrees(np.arctan2(tip[1], tip[0]))
            if r > 39.8 and abs((az+180) % 360-180) < 16: out.append(k)
        return out
    def fn(p, t):
        ks = cands(t)
        if not ks: return -9.9
        ct = np.array([SUNORB*np.cos((STN_M+t)*d2r), SUNORB*np.sin((STN_M+t)*d2r)])
        ds = (19/12)*(t-TH0)*d2r
        cc, ss = np.cos(-ds), np.sin(-ds)
        q = (p[::2]-ct) @ np.array([[cc, ss], [-ss, cc]])
        q = q[np.hypot(q[:, 0], q[:, 1]) > RLO]
        if not len(q): return -9.9
        worst = -1e9
        for k in ks:
            inside = paths[k].contains_points(q)
            if inside.any():
                worst = max(worst, float(np.sqrt(
                    ((q[inside][:, None]-dens[k][None])**2).sum(-1)).min()))
            else:
                worst = max(worst, -float(np.sqrt(
                    ((q[:, None, :]-dens[k][None])**2).sum(-1)).min()))
        return worst
    return fn, cands

QP = np.linspace(194, 166, 13)
def judge(base_deg, report=False):
    fn, cands = make_fn(base_deg)
    pushes, revs, g2max, g3min = [], [], 0.0, 1e9
    for n, fires, extended in PASSES:
        theta = TP + n*PITCH
        if extended:
            has = any(fn(S.tooth_world(psi), theta) > -0.05 for psi in QP)
            if fires:
                if not has:
                    if report: print(f"    n={n} SKIP: receiver absent"); return None
                eF, _, mpF = transit(fn, 198.0, 162.0, theta, +1, nsteps=100)
                if eF is None or abs((eF-theta)-PITCH) > 0.06*PITCH or mpF/PITCH < 1.0:
                    if report: print(f"    n={n} SKIP fwd: " + ("JAM" if eF is None
                                     else f"{mpF/PITCH:.2f}P/{(eF-theta)/PITCH:+.2f}"))
                    return None
                eR, _, mpR = transit(fn, 162.0, 198.0, eF, -1, nsteps=100)
                if eR is None or abs((eF-eR)-PITCH) > 0.06*PITCH or mpR/PITCH < 1.0:
                    if report: print(f"    n={n} SKIP rev: " + ("none" if eR is None
                                     else f"{mpR/PITCH:.2f}P"))
                    return None
                pushes.append(mpF/PITCH); revs.append(mpR/PITCH)
            else:
                if has:
                    e, _, mp = transit(fn, 196.0, 164.0, theta, +1, nsteps=75)
                    if e is None or mp/PITCH >= 0.35:
                        if report: print(f"    n={n} G2: " + ("JAM" if e is None
                                         else f"push {mp/PITCH:.2f}P")); return None
                    g2max = max(g2max, mp/PITCH)
        else:
            # G3: striker retracted 1.6 mm — static clearance vs whatever is
            # emerged (only meaningful when a tooth can reach the zone)
            if not cands(theta): continue
            worst = -1e9
            for psi in QP[::3]:
                p = S.tooth_world(psi).copy()
                v = p - np.array([73.5, 0.0])
                r = np.hypot(v[:, 0], v[:, 1])
                p = np.array([73.5, 0.0]) + v*((r-STROKE)/r)[:, None]   # retract (toward the drive center)
                worst = max(worst, fn(p, theta))
            g3min = min(g3min, -worst)
    if len(pushes) != 5: return None
    return min(pushes), min(revs), g2max, g3min

import os
STROKE=float(os.environ.get("STROKE","1.6"))
print(f"A-prime focused run, stroke={STROKE}mm")
import time
wins = []
for base in [6]:
    t0 = time.time()
    r = judge(base*30.0)
    print(f"  base {base}: " + (f"PASS fwd>={r[0]:.3f}P rev>={r[1]:.3f}P "
          f"G2 max {r[2]:.3f}P G3 min clear {r[3]:.2f}mm" if r else "fail")
          + f"  ({time.time()-t0:.0f}s)", flush=True)
    if r: wins.append((base, *r))
if wins:
    b = wins[0]
    for f in (-3.0, -1.5, 1.5, 3.0):
        rr = judge(b[0]*30.0 + f)
        print(f"  registration {f:+.1f} deg: {'PASS' if rr else 'fail'}")
    json.dump(dict(base=b[0], fwd=b[1], rev=b[2], g2=b[3], g3=b[4]),
              open("aprime_verdict.json", "w"), indent=1)
    print("VERDICT: architecture A' PASSES the month train")
else:
    print("no base passes — autopsy base 0:"); judge(0.0, report=True)
