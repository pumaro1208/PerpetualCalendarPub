#!/usr/bin/env python3
"""sequence_sweep.py — calendar-TRUE phantom/strike verification + S4 verdict.

Walks the engine's actual strike ladder (skips included) so every drive-tooth
pass is evaluated at the board angle and satellite spin the machine will
really be at. One year (372 board steps) covers all satellites (spin phase
repeats annually: (19/12)*372*PITCH = 19 full turns).

Per satellite, scans assembly clocking OFF for windows where:
  - every LOGICAL strike evening physically engages (push >= 0.5 pitch,
    settles exactly +1 pitch), and
  - every other visited pass is gated (no contact, or graze push < 0.35).
Then, at the winning OFFs, runs the REVERSE transit at each true strike
angle: the S4 verdict.
"""
import numpy as np, sys, json
sys.path.insert(0, '.')
import strike_transit_sweep as S
from strike_transit_sweep import transit, tooth_world, rprof, dense, PITCH
from generator_v13 import STN_M, STN_F, STN_L, LONG_M, L_TIP, RELIEF, SUNORB
import matplotlib.path as mpath

res = json.load(open("sweep_results.json"))
TP = res["theta_park"]; S.SEAT0[0] = TP

# ---------- calendar walker: one common year of hourly passes ----------
def walk_year(leap=False):
    """yields (hour, n_before_pass, fires) for hours 21/22/23, plus daily 24h.
    n = board steps taken since the walk origin (Jan 1, pos=1)."""
    n = 0; passes = []
    mlen = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    for mon in range(12):
        for pos_day in range(1, mlen[mon]+1):
            pass  # calendar day loop; board pos runs 1..31 regardless
    # walk by BOARD position (the machine's truth): pos cycles 1..31; the
    # skips at month ends keep the calendar aligned.
    mon, pos = 0, 1
    for _ in range(500):
        if mon == 12: break
        # evening ladder at this calendar day
        if mon == 1 and pos == 28 and not leap:
            passes.append((21, n, True)); n += 1; pos += 1
        else:
            passes.append((21, n, False))
        if mon == 1 and pos == 29:
            passes.append((22, n, True)); n += 1; pos += 1
        else:
            passes.append((22, n, False))
        if pos == 30 and mon in (1, 3, 5, 8, 10):
            passes.append((23, n, True)); n += 1; pos += 1
        else:
            passes.append((23, n, False))
        n += 1; pos += 1                     # midnight, always
        if pos > 31: pos = 1; mon += 1
    return passes, n

PASSES, NYEAR = walk_year(leap=False)
assert NYEAR == 372, NYEAR

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

def make_fn(prof, stn, off):
    def fn(p, t):
        az_c = (stn+t)*np.pi/180
        cx, cy = SUNORB*np.cos(az_c), SUNORB*np.sin(az_c)
        sp = (off + (19/12)*t)*np.pi/180
        r = np.hypot(p[:, 0]-cx, p[:, 1]-cy)
        az = np.arctan2(p[:, 1]-cy, p[:, 0]-cx) - sp
        return float(np.max(rprof(prof, az) - r))
    return fn

QUICK_PSI = np.linspace(192, 168, 25)
def quick_contact(fn, theta):
    return any(fn(tooth_world(psi), theta) > -0.05 for psi in QUICK_PSI)

def scan_off(prof, stn, hour, offs, label):
    """classify a year of this hour's passes for each OFF."""
    mine = [(n, f) for h, n, f in PASSES if h == hour]
    wins = []
    for off in offs:
        fn = make_fn(prof, stn, off)
        ok = True; pushes = []; worst_graze = 0.0
        for n, fires in mine:
            theta = TP + n*PITCH
            az = (stn + theta + 180) % 360 - 180
            if abs(az) > 9:
                if fires: ok = False; break     # logical strike out of reach
                continue
            if not quick_contact(fn, theta):
                if fires: ok = False; break
                continue
            e, _, mp = transit(fn, 194.0, 166.0, theta, +1, nsteps=80)
            if fires:
                if e is None or abs((e-theta)-PITCH) > 0.06*PITCH or mp/PITCH < 0.5:
                    ok = False; break
                pushes.append(mp/PITCH)
            else:
                if e is None or mp/PITCH >= 0.35: ok = False; break
                worst_graze = max(worst_graze, mp/PITCH)
        if ok and pushes:
            wins.append((off, min(pushes), worst_graze))
    if wins:
        lo, hi = min(w[0] for w in wins), max(w[0] for w in wins)
        best = max(wins, key=lambda w: w[1])
        print(f"  {label}: OFF window {lo:.1f}..{hi:.1f} "
              f"({len(wins)} pts); best OFF={best[0]:.1f} min strike push "
              f"{best[1]:.3f}P, worst visited graze {best[2]:.3f}P")
        return best[0], wins
    print(f"  {label}: *** no clean clocking window ***")
    return None, []

print("SEQUENCE-AWARE CLOCKING SCAN (calendar-true parks, one year)")
prof_m = lam_profile(sorted(LONG_M))
off_m, wins_m = scan_off(prof_m, STN_M, 23, np.linspace(0, 30, 61), "month (23h)")
prof_f = lam_profile({0})
off_f, wins_f = scan_off(prof_f, STN_F, 22, np.linspace(0, 360, 241), "feb (22h)")

print("S4 VERDICT: reverse transits at the TRUE strike angles")
def s4_test(prof, stn, hour, off, label):
    mine = [(n, f) for h, n, f in PASSES if h == hour and f]
    fn = make_fn(prof, stn, off)
    allrev = True
    for n, _ in mine:
        theta = TP + n*PITCH
        eF, _, mpF = transit(fn, 198.0, 162.0, theta, +1, nsteps=120)
        eR, _, mpR = transit(fn, 162.0, 198.0, eF, -1, nsteps=120) if eF else (None, None, 0)
        okR = eR is not None and abs((eF-eR)-PITCH) < 0.06*PITCH
        print(f"  {label} strike n={n}: fwd push {mpF/PITCH:.3f}P; "
              f"reverse {'OK, push %.3fP' % (mpR/PITCH) if okR else 'FAILS'}")
        allrev &= okR
    return allrev

verdict = {}
if off_m is not None:
    verdict["month_bidir"] = s4_test(prof_m, STN_M, 23, off_m, "month")
if off_f is not None:
    verdict["feb_bidir"] = s4_test(prof_f, STN_F, 22, off_f, "feb")
verdict["off_month"] = off_m; verdict["off_feb"] = off_f
json.dump(verdict, open("sequence_results.json", "w"), indent=1)
print("\nsequence sweep complete -> sequence_results.json")
