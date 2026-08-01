#!/usr/bin/env python3
"""#141 ASSEMBLY GATE — the check that should have existed before plate-43 shipped.

plate-43 and plate-44 were each verified on their own and each passed. The
collision was BETWEEN them: the receivers' 6mm hub bosses drove 2.8mm through the
carrier arms. Per-part gates cannot catch that. This one builds the whole z-stack
from the emitted STLs and tests every pair that shares an altitude.

It reads the real triangles — nothing here is a number I typed twice.
"""
import numpy as np, struct, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generator_v13 import SUNORB, STN_M, STN_F, STN_L

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl_v13")
BAND_PITCH = 5.0
BAND       = {"month": 9.5, "feb": 14.5, "leap": 19.5}
PAD_H      = 0.5

def tris(fn):
    d = open(os.path.join(D, fn), "rb").read()
    n = struct.unpack("<I", d[80:84])[0]
    T = np.empty((n, 3, 3))
    for i in range(n):
        o = 84 + i*50
        v = struct.unpack("<12f", d[o:o+48]); T[i] = [v[3:6], v[6:9], v[9:12]]
    return T

def bands(fn, cx=0.0, cy=0.0):
    """[(z0, z1, rmax)] per distinct z-slab, radius measured about (cx,cy).

    Radius comes from the SIDE WALLS of that slab only. Measuring every vertex in
    the z-window instead reports the slab below's top face as if it were this
    slab's radius — that artifact is what once made a r4.70 slim core read 9.80."""
    T = tris(fn)
    V = T.reshape(-1, 3)
    zs = np.unique(V[:,2].round(3))
    out = []
    for a, b in zip(zs[:-1], zs[1:]):
        zmin = T[:,:,2].min(1); zmax = T[:,:,2].max(1)
        wall = (zmin >= a-1e-4) & (zmax <= b+1e-4) & (zmax - zmin > 1e-4)
        if wall.any():
            W = T[wall].reshape(-1,3)
            rmax = np.hypot(W[:,0]-cx, W[:,1]-cy).max()
        else:                                   # zero-height slab: fall back to faces
            m = np.abs(V[:,2]-a) < 1e-4
            rmax = np.hypot(V[m,0]-cx, V[m,1]-cy).max()
        out.append((a, b, rmax))
    return out

def stn(s):
    a = np.deg2rad(s); return SUNORB*np.cos(a), SUNORB*np.sin(a)

FAILS = []
def gate(ok, msg):
    print(f"  [{'PASS' if ok else 'FAIL'}] {msg}")
    if not ok: FAILS.append(msg)

def overlap(a0, a1, b0, b1):
    return min(a1, b1) - max(a0, b0)

print("ASSEMBLY GATE v17 — full z-stack from emitted STLs\n")

# ---- 1. sun tower: piece height must equal the band pitch ----
sp = bands("140_sun_tower_piece_v17.stl")
piece_h = max(b for _, b, _ in sp)
band_h  = sp[0][1]
slim_r  = sp[-1][2]
print(f"  sun piece {piece_h:.2f} tall — ball band 0..{band_h:.2f} (r{sp[0][2]:.2f}), "
      f"slim core {band_h:.2f}..{piece_h:.2f} (r{slim_r:.2f})")
gate(abs(piece_h - BAND_PITCH) < 1e-6,
     f"sun piece height {piece_h:.2f} == band pitch {BAND_PITCH} "
     f"(if not, every band above the first is misaligned)")

# ---- 2. receivers: heights, and mesh lamina onto its sun band ----
REC = {"month": "141_receiver_month_v17.stl",
       "feb":   "142_receiver_feb_v17.stl",
       "leap":  "143_receiver_leap_v17.stl"}
occ = {}
print()
for k, fn in REC.items():
    b = bands(fn); h = max(x[1] for x in b)
    z0 = BAND[k]; occ[k] = (z0, z0+h)
    mesh_top = z0 + b[0][1]
    sun_band_top = z0 + band_h            # its own sun band starts at the same z
    print(f"  {k:5s} {h:.2f} tall, seated {z0:.1f}..{z0+h:.1f}   "
          f"mesh lamina {z0:.2f}..{mesh_top:.2f}")
    gate(abs(mesh_top - sun_band_top) < 1e-6,
         f"{k} mesh lamina coplanar with its sun ball band")

# ---- 3. carrier arms vs everything that shares their altitude ----
ARM = [("145_carrier_feb_v17.stl",  STN_M, STN_F, 12.7, "month", "feb"),
       ("146_carrier_leap_v17.stl", STN_F, STN_L, 17.7, "feb",   "leap")]
print()
for fn, fs, ts, zbot, below, above in ARM:
    fx, fy = stn(fs); tx, ty = stn(ts)
    b = bands(fn, fx, fy)
    plate_h = b[0][1]
    pad_top = None; top = max(x[1] for x in b)
    for a, bb, _ in b:
        if abs(bb - (plate_h + PAD_H)) < 1e-6: pad_top = bb
    print(f"  {fn.split('_')[1]:5s} plate {zbot:.1f}..{zbot+plate_h:.1f}  "
          f"pad top {zbot+plate_h+PAD_H:.1f}  post top {zbot+top:.1f}")
    # a. clears the satellite spinning underneath it
    c = zbot - occ[below][1]
    gate(c > 0.05, f"arm clears the rotating {below} satellite below by {c:.2f}mm")
    # b. the satellite above seats on the PAD, not on the plate face
    seat = zbot + plate_h + PAD_H
    gate(abs(seat - BAND[above]) < 1e-6,
         f"{above} seats on the pad at {seat:.2f} == its band {BAND[above]:.2f}")
    gate(BAND[above] - (zbot + plate_h) >= PAD_H - 1e-6,
         f"{above} lamina rides {BAND[above]-(zbot+plate_h):.2f}mm clear of the arm's top face")
    # c. the post is long enough to actually bear the satellite + whatever presses on it
    gate(zbot + top >= occ[above][1],
         f"post top {zbot+top:.2f} reaches past the {above} satellite top {occ[above][1]:.2f}")

# ---- 4. arm 2 must have real post to press onto ----
print()
b1 = bands("145_carrier_feb_v17.stl", *stn(STN_F))
post_span = (12.7 + b1[0][1], 12.7 + max(x[1] for x in b1))
grip = overlap(17.7, 19.0, *post_span)
gate(grip > 1.0, f"arm2 grips {grip:.2f}mm of arm1's post (press fit needs real length)")

# ---- 5. fingers must sweep inside the sun's SLIM core, never the ball band ----
print()
for k, fn in REC.items():
    b = bands(fn); z0 = BAND[k]
    fz = [(z0+a, z0+bb) for a, bb, _ in b if bb <= 3.0+1e-6 and a >= 2.0]
    if not fz: continue
    f0, f1 = fz[0][0], fz[-1][1]
    slim0, slim1 = z0 + band_h, z0 + piece_h
    gate(f0 >= slim0-1e-6 and f1 <= slim1+1e-6,
         f"{k} finger band {f0:.2f}..{f1:.2f} inside sun slim core {slim0:.2f}..{slim1:.2f}")
    # radial: the finger tip swings toward the sun axis — it must miss the slim core
    reach = max(x[2] for x in b if x[1] <= 3.0+1e-6 and x[0] >= 2.0)
    clear = (SUNORB - reach) - slim_r
    gate(clear > 0.2, f"{k} finger tip passes the slim core with {clear:.2f}mm "
                      f"(tip reaches sun-axis radius {SUNORB-reach:.2f} vs core {slim_r:.2f})")

# ---- 6. nothing anywhere overlaps in z AND in space ----
print()
solids = [(k, occ[k][0], occ[k][1], stn({'month':STN_M,'feb':STN_F,'leap':STN_L}[k]))
          for k in REC]
for i in range(len(solids)):
    for j in range(i+1, len(solids)):
        ka, a0, a1, pa = solids[i]; kb, b0, b1, pb = solids[j]
        ov = overlap(a0, a1, b0, b1)
        d = np.hypot(pa[0]-pb[0], pa[1]-pb[1])
        gate(ov <= 0 or d > 2*17.19,
             f"{ka}/{kb} do not share altitude (z overlap {ov:+.2f}, centres {d:.2f}mm apart)")

print("\n" + ("  *** GATE FAILED: " + str(len(FAILS)) + " ***" if FAILS else "  ALL GATES PASS"))
sys.exit(1 if FAILS else 0)
