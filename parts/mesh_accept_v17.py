#!/usr/bin/env python3
"""#141 MESH ACCEPTANCE — re-proves the sun<->satellite roll on the EMITTED v17 STLs.

The #141 rework touched z and topology, not tooth flanks, but "should not have
changed" is not evidence. This slices the real 140 sun band and the real 141/142/143
mesh laminae out of the files that will be sliced and printed, and rolls them.

EACH SATELLITE IS PLACED AT ITS OWN STATION. That is not cosmetic. The sun is one
fixed body clocked to the strike line, so the mesh phase a satellite needs depends
on where its station sits around the sun:

    alpha(beta) = beta - (SUN_ROT - beta)*(7/12)   (mod the 30 deg tooth pitch)

which reproduces the shipped ALPHA (18.07 / 6.46 / 24.85) to within 0.08 deg. Roll
the satellite at world 0 instead and you get 3.5mm^2 of overlap and a false alarm —
that is a bug in the test bench, not in the gear.

Reported:
  overlap      residual interference through the roll. Non-zero BY DESIGN: #138's
               cleanup carve would take this to zero but costs 1.9deg of seat
               tightness at the strike, and per #134 the seat wins. This is the
               wear-in graze Ron's bench pair already runs with.
  seated play  slack at the STRIKE station — the #134 number, the one eaten out of
               the 1.12mm drive window on a short-month strike.
"""
import numpy as np, struct, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import LineString
from shapely.ops import polygonize, linemerge
from shapely import affinity

CD, N_SUN, N_SAT = 23.75, 7, 12
PITCH_SAT    = 360/N_SAT
R_PITCH_SAT  = 2.5*N_SAT/2
SUN_ROT      = -19.50
DRIVE_WINDOW = 1.12
PITCH        = 360/31
STN = {"month": 360-29*PITCH, "feb": 360-28*PITCH, "leap": 360-27*PITCH}
GRAZE_MAX    = 0.20          # mm^2 — the accepted uncarved residual, not zero
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl_v13")

def sect(fn, zcut):
    d = open(os.path.join(D, fn), "rb").read()
    n = struct.unpack("<I", d[80:84])[0]; segs = []
    for i in range(n):
        o = 84 + i*50
        v = np.array(struct.unpack("<12f", d[o:o+48])[3:]).reshape(3,3); z = v[:,2]
        if z.min() <= zcut <= z.max():
            p = []
            for k in range(3):
                a, b = v[k], v[(k+1)%3]
                if (a[2]-zcut)*(b[2]-zcut) <= 0 and a[2] != b[2]:
                    t = (zcut-a[2])/(b[2]-a[2])
                    p.append((a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])))
            if len(p) >= 2: segs.append(p[:2])
    return max(polygonize(linemerge([LineString(s) for s in segs])), key=lambda q: q.area)

def main():
    sun = sect("140_sun_tower_piece_v17.stl", 0.75)
    x, y = np.array(sun.exterior.xy); r = np.hypot(x, y)
    print(f"  sun band  tip r{r.max():.2f}  root r{r.min():.2f}\n")
    fails = []
    for nm, fn in (("month","141_receiver_month_v17.stl"),
                   ("feb",  "142_receiver_feb_v17.stl"),
                   ("leap", "143_receiver_leap_v17.stl")):
        sat = sect(fn, 0.75); beta = STN[nm]
        def place(th):
            a = np.deg2rad(beta+th)
            return affinity.translate(affinity.rotate(sat, th*(1+N_SUN/N_SAT), origin=(0,0)),
                                      CD*np.cos(a), CD*np.sin(a))
        worst = max(sun.intersection(place(th)).area
                    for th in np.linspace(0, 360/N_SUN*3, 300))
        # clocking cross-check: the phase this station needs, derived independently
        want = (beta - (SUN_ROT-beta)*(N_SUN/N_SAT)) % PITCH_SAT
        # seated play at the strike station
        c = (CD*np.cos(np.deg2rad(beta)), CD*np.sin(np.deg2rad(beta))); p0 = place(0.0)
        span = []
        for sgn in (1, -1):
            a = 0.0
            while a < 20:
                a += 0.05
                if sun.intersection(affinity.rotate(p0, sgn*a, origin=c)).area > 1e-4: break
            span.append(a)
        play = sum(span); play_mm = np.deg2rad(play)*R_PITCH_SAT
        from generator_engine_v17 import ALPHA
        dphase = abs((ALPHA[nm] - want + PITCH_SAT/2) % PITCH_SAT - PITCH_SAT/2)
        ok = (worst <= GRAZE_MAX and play_mm < DRIVE_WINDOW*0.5
              and dphase*np.pi/180*R_PITCH_SAT < 0.05)   # under a tenth of print backlash
        print(f"  {nm:5s} station {beta:6.2f}deg (needs clocking {want:5.2f}deg)  "
              f"roll graze {worst:6.4f} mm^2   seated play {play:4.2f}deg = {play_mm:5.3f} mm "
              f"({100*play_mm/DRIVE_WINDOW:4.1f}% of the strike window)  "
              f"[{'PASS' if ok else 'REVIEW'}]")
        if not ok: fails.append(nm)
    print("\n  " + ("MESH ACCEPTED" if not fails else f"REVIEW: {fails}"))
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
