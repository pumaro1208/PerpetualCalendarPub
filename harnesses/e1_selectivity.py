#!/usr/bin/env python3
"""e1_selectivity.py — Session 2 gate: patent-literal involute receivers in
the calendar-true sequence, strikes re-clocked to the mechanism's natural
evenings (satellite center at -5.83 deg; skips at pos 27/28/29).

Receiver model: five involute BOARD-TOOTH-profile teeth on the month
satellite at consecutive stations, superposition-registered (the engaged
tooth, when its station points radially at a park, coincides with a board
tooth of the lattice). Poses rigidly with the satellite (orbit + 19/12 spin).

Gate per the requirement set:
  fires    -> push >= 1.0 pitch, settled exactly +1 (E1-grade, bidirectional
              class per the addendum measurement)
  visited non-fires -> no contact, or graze push < 0.35 pitch
Scans assembly clocking: 12 station choices x fine registration offset.
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

# ---- natural-evening walker: skips at pos 27 (leap), 28 (feb), 29 (month)
def walk_natural():
    out = []; n = 0; mon, pos = 0, 1
    while mon < 12:
        if mon == 1 and pos == 27: n += 1; pos += 1            # leap (common yr)
        if mon == 1 and pos == 28: n += 1; pos += 1            # feb
        if pos == 29 and mon in (1, 3, 5, 8, 10):
            out.append((n, True)); n += 1; pos += 1            # month 23h
        else:
            out.append((n, False))
        n += 1; pos += 1                                       # midnight
        if pos > 31: pos = 1; mon += 1
    return out, n

MINE, NY = walk_natural()
assert NY == 372, NY

# ---- receiver: engaged tooth built by superposition at az -5.83, park th0
AZ0 = TP - PITCH                      # -5.831: the board tooth below the mesh
TH0 = AZ0 - STN_M                     # park with the satellite radial at AZ0
T = np.array(tooth_outline(MD, GP["prog_teeth"], add_f=ADD_F))
c, s = np.cos(AZ0*d2r), np.sin(AZ0*d2r)
P0 = T @ np.array([[c, s], [-s, c]])                     # world @ park
C0 = np.array([SUNORB*np.cos((STN_M+TH0)*d2r), SUNORB*np.sin((STN_M+TH0)*d2r)])
SAT0 = P0 - C0                                           # satellite frame, spin ref

def sat_teeth(spin_extra):
    """five consecutive-station teeth (k=0..4) in the satellite frame,
    rotated by spin_extra (assembly clocking fine offset)."""
    out = []
    for k in range(5):
        a = (k*30 + spin_extra)*d2r
        cc, ss = np.cos(a), np.sin(a)
        out.append(SAT0 @ np.array([[cc, ss], [-ss, cc]]))
    return out

def tip_candidates(t, off_fine):
    """cheap: which teeth could reach the swept annulus at this pose."""
    ct = np.array([SUNORB*np.cos((STN_M+t)*d2r), SUNORB*np.sin((STN_M+t)*d2r)])
    ds = (19/12)*(t-TH0)
    out = []
    tipr = np.hypot(SAT0[:,0], SAT0[:,1]).max()
    tipa = np.degrees(np.arctan2(SAT0[:,1], SAT0[:,0]))[np.argmax(np.hypot(SAT0[:,0],SAT0[:,1]))]
    for k in range(5):
        a = (tipa + k*30 + off_fine + ds)*d2r
        tip = ct + tipr*np.array([np.cos(a), np.sin(a)])
        r, az = np.hypot(*tip), np.degrees(np.arctan2(tip[1], tip[0]))
        if r > 39.8 and abs((az+180)%360-180) < 16: out.append(k)
    return out

def make_fn(off_fine):
    teeth = sat_teeth(off_fine)
    paths = [mpath.Path(np.vstack([t, t[:1]])) for t in teeth]
    dens = []
    for t in teeth:
        d = []
        for i in range(len(t)):
            a, b = t[i], t[(i+1) % len(t)]
            m = max(1, int(np.hypot(*(b-a))/0.22))
            for j in range(m): d.append(a+(b-a)*j/m)
        dens.append(np.array(d))
    rlo = np.hypot(SAT0[:,0], SAT0[:,1]).min() - 1.0
    def fn(p, t):
        ks = tip_candidates(t, off_fine)
        if not ks: return -9.9
        ct = np.array([SUNORB*np.cos((STN_M+t)*d2r), SUNORB*np.sin((STN_M+t)*d2r)])
        ds = (19/12)*(t-TH0)*d2r
        cc, ss = np.cos(-ds), np.sin(-ds)
        q = (p[::2]-ct) @ np.array([[cc, ss], [-ss, cc]])   # satellite frame
        q = q[np.hypot(q[:,0], q[:,1]) > rlo]               # radial band filter
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
    return fn

QP = np.linspace(194, 166, 15)
def judge(base_rot, off_fine, report=False):
    fn = make_fn(base_rot*30 + off_fine)
    pushes, worst_graze = [], 0.0
    for n, fires in MINE:
        theta = TP + n*PITCH
        az = (STN_M + theta + 180) % 360 - 180
        if abs(az) > 22:
            if fires: return None
            continue
        if not tip_candidates(theta, base_rot*30 + off_fine) if False else False:
            pass
        if not any(fn(S.tooth_world(psi), theta) > -0.05 for psi in QP):
            if fires: return None
            continue
        e, _, mp = transit(fn, 196.0, 164.0, theta, +1, nsteps=75)
        if fires:
            if e is None or abs((e-theta)-PITCH) > 0.06*PITCH or mp/PITCH < 1.0:
                if report: print(f"    n={n} FIRES: "
                                 + ("JAM" if e is None else
                                    f"push {mp/PITCH:.2f}P settled {(e-theta)/PITCH:+.2f}P"))
                return None
            pushes.append(mp/PITCH)
        else:
            if e is None or mp/PITCH >= 0.35:
                if report: print(f"    n={n} visited: "
                                 + ("JAM" if e is None else f"push {mp/PITCH:.2f}P"))
                return None
            worst_graze = max(worst_graze, mp/PITCH)
    if len(pushes) != 5: return None
    return min(pushes), worst_graze

print("E1 SELECTIVITY GATE — involute receivers, natural strike evenings")
wins = []
import time
for base in range(12):
    t0 = time.time()
    r = judge(base, 0.0)
    print(f"  base {base}: {'PASS %.3fP/%.3fP' % (r[0], r[1]) if r else 'fail'}"
          f"  ({time.time()-t0:.0f}s)", flush=True)
    if r: wins.append((base, 0.0, *r))
if not wins:
    print("  coarse scan: no station assignment passes at fine=0; autopsy of base 0:")
    judge(0, 0.0, report=True)
else:
    b0 = wins[0][0]
    fine_ok = []
    for f in np.linspace(-3, 3, 13):
        r = judge(b0, f)
        if r: fine_ok.append(f)
    if fine_ok:
        print(f"  registration tolerance at base {b0}: "
              f"{min(fine_ok):+.1f} .. {max(fine_ok):+.1f} deg")
    json.dump(dict(wins=[(w[0], w[2], w[3]) for w in wins],
                   fine_lo=min(fine_ok) if fine_ok else None,
                   fine_hi=max(fine_ok) if fine_ok else None),
              open("e1_selectivity.json", "w"), indent=1)
