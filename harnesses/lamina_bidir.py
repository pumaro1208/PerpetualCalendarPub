import numpy as np, sys, json
sys.path.insert(0,'.')
from strike_transit_sweep import (transit, lam_overlap, th_grid, PITCH,
                                  STN_M)
import strike_transit_sweep as S
res = json.load(open("sweep_results.json"))
theta_park = res["theta_park"]; S.SEAT0[0] = theta_park
ks = np.arange(-16, 16)
azs = (STN_M + theta_park + ks*PITCH + 180) % 360 - 180
th_strike = theta_park + int(ks[np.argmin(np.abs(azs))])*PITCH
print("bidirectional lamina clocking scan (OFF mod 30):")
good = []
for off in np.linspace(0, 30, 121):
    eF, _, mpF = transit(lambda p, t: lam_overlap(p, t, off),
                         190.0, 170.0, th_strike, push=+1, nsteps=90)
    if eF is None or abs((eF-th_strike)-PITCH) > 0.05*PITCH: continue
    eR, _, mpR = transit(lambda p, t: lam_overlap(p, t, off),
                         170.0, 190.0, eF, push=-1, nsteps=90)
    okR = eR is not None and abs((eF-eR)-PITCH) < 0.05*PITCH
    good.append((off, mpF/PITCH, (eF-eR)/PITCH if eR is not None else 0.0, okR))
fwd_only = [g for g in good if not g[3]]
both     = [g for g in good if g[3]]
print(f"  OFFs with clean FORWARD transit: {len(good)}")
print(f"  OFFs also clean in REVERSE:      {len(both)}")
if both:
    for off, mpF, advR, _ in both[:8]:
        print(f"    OFF={off:6.2f}: fwd push {mpF:.3f}P, rev advance {advR:.4f}P")
    lo, hi = min(b[0] for b in both), max(b[0] for b in both)
    print(f"  bidirectional clocking window: {lo:.2f} .. {hi:.2f} deg")
else:
    print("  *** NO clocking gives bidirectional lamina transit ***")
    for off, mpF, advR, _ in good[:6]:
        print(f"    fwd-only OFF={off:6.2f}: fwd push {mpF:.3f}P, rev moved {advR:.4f}P")
