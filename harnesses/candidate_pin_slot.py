#!/usr/bin/env python3
"""candidate_pin_slot.py — S4/S7 redesign candidate: pin-and-slot skip transfer.

The drive wheel's elevated strike teeth become PINS (radius r_p at drive
orbit rho_p); each lamina long tooth becomes a TWIN-RAIL SLOT the pin enters.
Judged by the calendar-true sequence harness against:
 R1 tooth-completed push >= 1.0 pitch, forward AND reverse, at every strike
 R2/R4 all other visited passes: clear or graze < 0.35 pitch
 R3 healthy margins (strike push, excursion vs detent crest)
Iterates a small parameter grid until a candidate passes or the grid is out.
"""
import numpy as np, sys, json
sys.path.insert(0, '.')
import strike_transit_sweep as S
from strike_transit_sweep import transit, rprof, PITCH
from generator_v13 import STN_M, LONG_M, SUNORB
from sequence_sweep import walk_year

res = json.load(open("sweep_results.json"))
TP = res["theta_park"]; S.SEAT0[0] = TP
DR = 73.5
PASSES, _ = walk_year(False)
MINE = [(n, f) for h, n, f in PASSES if h == 23]

def pin_world(psi, rho_p, r_p, npts=28):
    a = psi*np.pi/180
    cx, cy = DR + rho_p*np.cos(a), rho_p*np.sin(a)
    t = np.linspace(0, 2*np.pi, npts, endpoint=False)
    return np.stack([cx + r_p*np.cos(t), cy + r_p*np.sin(t)], 1)

def slot_profile(stations, r_in, r_tip, gap_half_deg, rail_deg, seg=6200):
    """polar lamina: hub + twin rails flanking a radial slot at each station."""
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    hub = 8.0
    r = np.full(seg, hub)
    for k in stations:
        c = k*np.pi/6
        d = np.degrees(np.angle(np.exp(1j*(th - c))))
        rail = (np.abs(np.abs(d) - (gap_half_deg + rail_deg/2)) < rail_deg/2)
        r[rail] = np.maximum(r[rail], r_tip)
    return r, r_in

def make_fn(prof, off, rho_p, r_p):
    def fn(p, t):
        az_c = (STN_M+t)*np.pi/180
        cx, cy = SUNORB*np.cos(az_c), SUNORB*np.sin(az_c)
        sp = (off + (19/12)*t)*np.pi/180
        rr = np.hypot(p[:, 0]-cx, p[:, 1]-cy)
        az = np.arctan2(p[:, 1]-cy, p[:, 0]-cx) - sp
        surf = rprof(prof, az)
        pen = surf - rr
        pen[rr < RIN] = -1.0            # below rail roots: rails absent there
        return float(np.max(pen))
    return fn

QP = np.linspace(196, 164, 33)
def judge(params, verbose=False):
    global RIN
    rho_p, r_p, r_in, r_tip, gh, rd = params
    RIN = r_in
    prof, _ = slot_profile(sorted(LONG_M), r_in, r_tip, gh, rd)
    S.tooth_world_saved = S.tooth_world
    tw = lambda psi: pin_world(psi, rho_p, r_p)
    S.tooth_world = tw
    best = None
    try:
        for off in np.linspace(0, 30, 61):
            fn = make_fn(prof, off, rho_p, r_p)
            ok, pushes, grazes = True, [], 0.0
            for n, fires in MINE:
                theta = TP + n*PITCH
                az = (STN_M + theta + 180) % 360 - 180
                if abs(az) > 9:
                    if fires: ok = False; break
                    continue
                if not any(fn(tw(psi), theta) > -0.05 for psi in QP[::2]):
                    if fires: ok = False; break
                    continue
                e, _, mp = transit(fn, 196.0, 164.0, theta, +1, nsteps=90)
                if fires:
                    if (e is None or abs((e-theta)-PITCH) > 0.06*PITCH
                            or mp/PITCH < 1.0):
                        ok = False; break
                    pushes.append(mp/PITCH)
                else:
                    if e is None or mp/PITCH >= 0.35: ok = False; break
                    grazes = max(grazes, mp/PITCH)
            if ok and len(pushes) == 5:
                # R1 reverse at every strike
                fn = make_fn(prof, off, rho_p, r_p)
                allrev, revs = True, []
                for n, fires in MINE:
                    if not fires: continue
                    theta = TP + n*PITCH
                    eF, _, mpF = transit(fn, 198.0, 162.0, theta, +1, nsteps=110)
                    eR, _, mpR = (transit(fn, 162.0, 198.0, eF, -1, nsteps=110)
                                  if eF is not None else (None, None, 0))
                    okR = (eR is not None and abs((eF-eR)-PITCH) < 0.06*PITCH
                           and mpR/PITCH >= 1.0)
                    allrev &= okR; revs.append(mpR/PITCH if eR else 0)
                if allrev:
                    cand = (off, min(pushes), min(revs), grazes)
                    if best is None or cand[1] > best[1]: best = cand
    finally:
        S.tooth_world = S.tooth_world_saved
    return best

grid = [
    # rho_p, r_p, r_in, r_tip, gap_half_deg, rail_deg
    (32.0, 1.4, 14.5, 19.5, 5.8, 6.0),
    (32.6, 1.4, 15.5, 19.5, 5.8, 5.0),
    (32.0, 1.2, 14.5, 19.2, 5.0, 5.5),
    (31.4, 1.4, 13.5, 19.8, 6.2, 6.0),
]
print("PIN-AND-SLOT CANDIDATE — sequence-harness judgment (month lamina)")
winner = None
for g in grid:
    b = judge(g)
    tag = (f"PASS  OFF={b[0]:.1f} fwd>= {b[1]:.2f}P rev>= {b[2]:.2f}P "
           f"worst graze {b[3]:.3f}P") if b else "fail"
    print(f"  rho_p={g[0]} r_p={g[1]} rails r{g[2]}-{g[3]} "
          f"gap±{g[4]} rail {g[5]}: {tag}")
    if b and winner is None:
        winner = (g, b)
if winner:
    json.dump(dict(params=winner[0], off=winner[1][0], fwd=winner[1][1],
                   rev=winner[1][2], graze=winner[1][3]),
              open("pinslot_winner.json", "w"), indent=1)
    print("\nWINNER recorded -> pinslot_winner.json")
else:
    print("\nno passing candidate in this grid")
