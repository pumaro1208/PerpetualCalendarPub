#!/usr/bin/env python3
"""harness_feb_leap.py — session-3 remaining item 1: the feb (22h) and leap
(21h) trains through the SAME calendar-true harness that judged the month
train. Single-station receivers; walkers carry the other trains' cascade
inserts in the n-lattice. Gates: G1 fires >=1.0P fwd/rev settled +/-1P;
G2 non-firing extended evenings silent (<0.35P); G3 retracted adjacency
clearance >= 0.30 mm at the 1.6 mm stroke."""
import numpy as np, sys, json, os, time
sys.path.insert(0, '.')
import strike_transit_sweep as S
from strike_transit_sweep import transit, PITCH
from generator import MD, ADD_F, tooth_outline, P as GP
from generator_v13 import STN_M, SUNORB
import matplotlib.path as mpath

res = json.load(open("sweep_results.json"))
TP = res["theta_park"]; S.SEAT0[0] = TP
d2r = np.pi/180
STROKE = 1.6

# ---- natural-evening walkers: EXACT clones of the proven walk_23 lattice
# (31 loop-positions/month; Feb inserts at pos 27 (21h) and 28 (22h); the
# 23h decision at pos 29). Per-train roles on the same n-lattice.
def passes_for(hh):
    out = []; n = 0; mon, pos = 0, 1
    while mon < 12:
        if mon == 1 and pos == 27:
            if hh == 21: out.append((n, True, True))     # 21h FIRES (common Feb)
            n += 1; pos += 1
        if mon == 1 and pos == 28:
            if hh == 22: out.append((n, True, True))     # 22h FIRES
            n += 1; pos += 1
        if pos == 29 and hh == 23:
            skipm = mon in (1, 3, 5, 8, 10)
            out.append((n, skipm, True))
            if skipm: n += 1; pos += 1
        elif pos == 27 and hh == 21 and mon != 1:
            out.append((n, False, True))                 # extended, silent
        elif pos == 28 and hh == 22 and mon != 1:
            out.append((n, False, True))                 # extended, silent
        else:
            out.append((n, False, False))                # retracted (G3)
        n += 1; pos += 1
        if pos > 31: pos = 1; mon += 1
    return out

# ---- single-tooth E1 receiver (reuse the month train's registration)
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
RLO = np.hypot(SAT0[:, 0], SAT0[:, 1]).min() - 1.0

def make_fn_single(base_deg, stn_off=0.0):
    a = base_deg*d2r
    cc, ss = np.cos(a), np.sin(a)
    t = SAT0 @ np.array([[cc, ss], [-ss, cc]])
    path = mpath.Path(np.vstack([t, t[:1]]))
    d = []
    for i in range(len(t)):
        aa, bb = t[i], t[(i+1) % len(t)]
        m = max(1, int(np.hypot(*(bb-aa))/0.22))
        for j in range(m): d.append(aa+(bb-aa)*j/m)
    dens = np.array(d)
    def cand(tt):
        ds = (19/12)*(tt-TH0)
        a2 = (TIPA + base_deg + ds)*d2r
        ct = np.array([SUNORB*np.cos((STN_M+stn_off+tt)*d2r), SUNORB*np.sin((STN_M+stn_off+tt)*d2r)])
        tip = ct + TIPR*np.array([np.cos(a2), np.sin(a2)])
        r, az = np.hypot(*tip), np.degrees(np.arctan2(tip[1], tip[0]))
        return r > 39.8 and abs((az+180) % 360-180) < 16
    def fn(p, tt):
        if not cand(tt): return -9.9
        ct = np.array([SUNORB*np.cos((STN_M+stn_off+tt)*d2r), SUNORB*np.sin((STN_M+stn_off+tt)*d2r)])
        ds = (19/12)*(tt-TH0)*d2r
        cc2, ss2 = np.cos(-ds), np.sin(-ss*0+ -ds)
        cc2, ss2 = np.cos(-ds), np.sin(-ds)
        q = (p[::2]-ct) @ np.array([[cc2, ss2], [-ss2, cc2]])
        q = q[np.hypot(q[:, 0], q[:, 1]) > RLO]
        if not len(q): return -9.9
        inside = path.contains_points(q)
        if inside.any():
            return float(np.sqrt(((q[inside][:, None]-dens[None])**2).sum(-1)).min())
        return -float(np.sqrt(((q[:, None, :]-dens[None])**2).sum(-1)).min())
    return fn, cand

QP = np.linspace(194, 166, 13)
STN_OFF = {23: 0.0, 22: PITCH, 21: 2*PITCH}   # carrier station per train
def judge(hh, base_deg, report=False):
    fn, cand = make_fn_single(base_deg, STN_OFF[hh])
    PASSES = passes_for(hh)
    pushes, revs, g2max, g3min = [], [], 0.0, 1e9
    for n, fires, extended in PASSES:
        theta = TP + n*PITCH
        if extended:
            has = any(fn(S.tooth_world(psi), theta) > -0.05 for psi in QP)
            if fires:
                if not has: return None
                eF, _, mpF = transit(fn, 198.0, 162.0, theta, +1, nsteps=100)
                if eF is None or abs((eF-theta)-PITCH) > 0.06*PITCH or mpF/PITCH < 1.0:
                    if report: print(f"    n={n} fwd fail")
                    return None
                eR, _, mpR = transit(fn, 162.0, 198.0, eF, -1, nsteps=100)
                if eR is None or abs((eF-eR)-PITCH) > 0.06*PITCH or mpR/PITCH < 1.0:
                    if report: print(f"    n={n} rev fail")
                    return None
                pushes.append(mpF/PITCH); revs.append(mpR/PITCH)
            elif has:
                e, _, mp = transit(fn, 196.0, 164.0, theta, +1, nsteps=75)
                if e is None or mp/PITCH >= 0.35: return None
                g2max = max(g2max, mp/PITCH)
        else:
            if not cand(theta): continue
            worst = -1e9
            for psi in QP[::3]:
                p = S.tooth_world(psi).copy()
                v = p - np.array([73.5, 0.0])
                r = np.hypot(v[:, 0], v[:, 1])
                p2 = np.array([73.5, 0.0]) + v*((r-STROKE)/r)[:, None]
                worst = max(worst, fn(p2, theta))
            g3min = min(g3min, -worst)
    if len(pushes) != 1: return None
    return pushes[0], revs[0], g2max, g3min

if __name__ == "__main__":
    for hh, name in ((22, "FEB 22h"), (21, "LEAP 21h")):
        print(f"{name} train: base scan...")
        wins = []
        for b in np.arange(0, 360, 2.5):
            r = judge(hh, float(b))
            if r: wins.append((float(b), r))
        if not wins:
            print(f"  *** NO PASSING BASE — {name} FAILS the harness ***")
            continue
        # refine around the best window
        bs = [w[0] for w in wins]
        print(f"  passing bases: {bs[0]:.1f}..{bs[-1]:.1f} ({len(wins)} of 144)")
        mid = bs[len(bs)//2]
        r = judge(hh, mid, report=True)
        pF, pR, g2, g3 = r
        print(f"  JUDGED at base {mid:.1f}: fwd {pF:.3f}P, rev {pR:.3f}P, "
              f"G2 max {g2:.3f}P, G3 clearance {g3:.2f} mm")
        ok = pF >= 1.0 and pR >= 1.0 and g2 < 0.35 and g3 >= 0.30
        print(f"  {name}: " + ("ALL GATES PASS" if ok else "*** GATE FAIL ***"))
