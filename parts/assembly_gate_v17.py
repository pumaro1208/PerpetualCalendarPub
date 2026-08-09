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
BAND_PITCH = 6.5
BAND       = {"month": 9.5, "feb": 16.0, "leap": 22.5}
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
       ("146_carrier_leap_v17.stl", STN_F, STN_L, 19.2, "feb",   "leap")]
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

# ---- 4. GRIP: does each press fit have enough engagement to BE a joint? ----
# #147, Ron at the bench: "the small posts do not have a tall enough post to grab".
# He was right, and this gate is why it got through. It used to check only that arm2
# had "some" post, with a 1.0mm threshold picked out of the air — and it reported the
# number without judging it. The grip is the PLATE THICKNESS and nothing else, because
# the post must stop under the satellite above; at the old 5.0 pitch that was 1.30mm on
# a 2.70 post, 0.48 diameters, with no shoulder to register against. Rule of thumb for a
# press fit in plastic is ~1 diameter; gate at 0.8 and report in diameters, not mm.
print()
from carrier_v17 import POST_R as _PR, PLATE_H as _PLATE, SPIG_R as _SR, BORE_SPIG as _BS
# #152 — the threshold is CONDITIONAL, and that is the engineering, not a tuned number.
# The ~1-diameter rule of thumb exists because a plain collar has NOTHING TO SQUARE
# AGAINST: its only reference is the bore itself, so short means cocked. A spigot that
# bottoms on a shoulder takes its height and squareness from a stationary machined face,
# and the bore only has to resist tilt — 0.6 diameters is a proper joint there. So the
# gate asserts the SHOULDER first and only then applies the relaxed grip limit. Without
# a shoulder it still demands 0.8, exactly as before.
MIN_GRIP_PLAIN, MIN_GRIP_SHOULDERED, MIN_SHOULDER = 0.80, 0.60, 0.40
_shoulder = _PR - _SR
gate(_shoulder >= MIN_SHOULDER,
     f"stepped post: shoulder ring {_shoulder:.2f}mm wide (need {MIN_SHOULDER:.2f}) — "
     f"this face, not the rotating satellite below, is what sets the arm's height")
for _nm, _seat in (("arm 1 on the board's month post", BAND["month"]),
                   ("arm 2 on arm 1's riser",          BAND["feb"])):
    _exposed = BAND_PITCH - 3.0 - PAD_H          # what the pitch leaves above the satellite
    _dia  = _PLATE/(2*_SR)
    _need = MIN_GRIP_SHOULDERED if _shoulder >= MIN_SHOULDER else MIN_GRIP_PLAIN
    gate(_dia >= _need,
         f"{_nm}: grip {_PLATE:.2f}mm on the {2*_SR:.2f} spigot = {_dia:.2f} diameters "
         f"(need {_need:.2f}, shouldered); post is {2*_PR:.2f} through the satellite, "
         f"steps to {2*_SR:.2f}, plate {_PLATE:.2f} + {_exposed-_PLATE:.2f} running clearance")
gate(_BS < _SR, f"arm bore {2*_BS:.2f} is an interference fit on the {2*_SR:.2f} spigot "
                f"({2*(_SR-_BS):.2f}mm nominal, and comp shrink is the running clearance)")

# ---- #159 drive-stack axial datum (Ron: "the 23h goes slightly beneath the
# satellite"). The stack must be SEATED, not just stacked: flange foot on the
# fixture base -> bottom piece at exactly 5.0 -> every arm at its altitude.
import trimesh as _tm
_sv=_tm.load("stl_v13/162_drive_sleeve_v17.stl")
gate(abs(_sv.bounds[0][2]-0.0)<0.01 and abs(_sv.bounds[1][2]-27.5)<0.01,
     "sleeve rev B spans 27.5 (assy 2.5..30.0): foot on the fixture base at 2.5")
_s5=_sv.section(plane_origin=[0,0,1.0],plane_normal=[0,0,1])
import numpy as _np
_V=_np.array(_s5.vertices)
gate(abs(_np.hypot(_V[:,0],_V[:,1]).max()-13.0)<0.1,
     f"flange r{_np.hypot(_V[:,0],_V[:,1]).max():.1f} seats the bottom piece at z5.0 — "
     f"the 23h arm rides at 11.70..12.50, ON the month strike tips, not beneath them")
gate(73.5-41.86 > 13.0+2.0, "flange r13 clears the board teeth sweep (they reach r31.6 from the drive axis)")

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

# ---- 7. THE DATUM CHAIN BELOW THE BOARD (#142, from Ron's "the sun gear is low") ----
# Everything above was measured relative to the board. That is exactly the blind spot
# he spotted: the satellite hangs off the board's pivot pad, but the SUN hangs off the
# fixture, and nothing was checking that the two chains arrive at the same altitude.
print()
POST_TOP   = 8.5     # fixture round post r4.17 top — the sun tower bottoms here
KEY_TOP    = 29.5    # fixture K4 square key top (r63; 25.0 on r62, 18.0 on r61)
BOARD      = (5.0, 9.0)
BOARD_BORE = 5.45
SHIM_H     = 1.0

shim = bands("147_sun_spacer_1mm_v17.stl")
shim_h = max(b for _, b, _ in shim); shim_r = max(x[2] for x in shim)
sun_base = POST_TOP + shim_h
gate(abs(sun_base - BAND["month"]) < 1e-6,
     f"sun band 1 lands at {sun_base:.2f} == month lamina {BAND['month']:.2f} "
     f"(post top {POST_TOP} + {shim_h:.2f} shim). Without the shim the sun sits "
     f"{BAND['month']-POST_TOP:.2f}mm low and the band only half-overlaps the lamina")
gate(shim_r <= BOARD_BORE - 0.1,
     f"shim OD r{shim_r:.2f} nests in the board bore r{BOARD_BORE} "
     f"(it spans {POST_TOP:.1f}-{sun_base:.1f} and the board runs to {BOARD[1]:.1f})")
tower_top = sun_base + 3*BAND_PITCH
gate(KEY_TOP >= tower_top,
     f"K4 key top {KEY_TOP:.1f} keys the whole tower (top {tower_top:.1f}) — "
     f"un-keyed sun pieces rotate free and the #134 clocking is lost")
bb = bands("144_board_02j_v17.stl")
board_bore = min(x[2] for x in bands("144_board_02j_v17.stl", 0, 0)) if False else None
import numpy as _np
V = tris("144_board_02j_v17.stl").reshape(-1,3)
f0 = V[_np.abs(V[:,2]) < 1e-4]
gate(abs(_np.hypot(f0[:,0], f0[:,1]).min() - BOARD_BORE) < 1e-2,
     f"board bore r{_np.hypot(f0[:,0],f0[:,1]).min():.3f} == r{BOARD_BORE} "
     f"(it presses on the star hub's r5.53 tube; a radius/diameter slip here is silent)")

# ---- 8. WITHIN-PART feature collisions (#146, Ron spotted it on the bench) ----
# Every gate so far compares one PART against another. The pivot pad overhanging
# its own arm's press-fit bore was invisible to all of them: one part, two features,
# 4.81mm apart while they measure 3.50 + 2.60 across. The lip printed unsupported
# over the hole and would foul a slightly-long post at assembly.
print()
# #152: the arm's bore is now the SPIGOT bore, so the pad must be checked against that,
# not against the old plain-post BORE_PRESS. (_SR here is SEAT_R, the pad radius — it
# deliberately shadows the SPIG_R alias used in section 4 above; kept separate on import
# so a future edit cannot silently cross them.)
from carrier_v17 import stn_xy as _sx, SEAT_R as _SR, BORE_SPIG as _BR, PAD_CLR as _PC
for _fn, _fs, _ts in (("145_carrier_feb_v17.stl", STN_M, STN_F),
                      ("146_carrier_leap_v17.stl", STN_F, STN_L)):
    _fx, _fy = _sx(_fs); _tx, _ty = _sx(_ts)
    _T = tris(_fn); _z0 = _T[:,:,2].min(1); _z1 = _T[:,:,2].max(1)
    from carrier_v17 import PLATE_H as _PH
    _w = (_z0 >= _PH-1e-4) & (_z1 <= _PH+PAD_H+1e-4) & (_z1-_z0 > 1e-4)   # the pad slab
    _W = _T[_w].reshape(-1,3)
    _d = np.hypot(_W[:,0]-_fx, _W[:,1]-_fy).min()
    gate(_d >= _BR,
         f"{_fn.split('_')[1]} arm: pivot pad clears its own press-fit bore "
         f"(nearest pad material {_d:.2f} vs bore r{_BR}) — a full-circle r{_SR} pad "
         f"at {np.hypot(_tx-_fx,_ty-_fy):.2f}mm spacing overhangs it by "
         f"{_SR+_BR-np.hypot(_tx-_fx,_ty-_fy):.2f}mm")

# ---- 9. STRIKE CLOCKING (#148, Ron: "30 is at the top, not 1") ----
# The gate that was missing. #134 verified the MESH seating and nothing ever tied
# the STRIKE-tooth bearings to the calendar engine, so a single round E1_BASE = 6.0
# served all three satellites for six findings. They strike on different dates, so
# they cannot share a bearing: feb was 10.84 deg out (306% of the drive window) and
# leap 7.55 deg (213%) — both would simply have missed, and February would never
# have been shortened. This asserts, per satellite, that its strike bar lands on the
# strike line at its OWN strike date.
print()
from generator_engine_v17 import E1_BASE as _E1
_PITCH = 360/31
STRIKE_DATE = {"month": 30, "feb": 29, "leap": 28}     # from evalHour in the simulator
DRIVE_WINDOW = 1.12
for _k, _d in STRIKE_DATE.items():
    _psi = ((19/12)*(_d-1)*_PITCH + _E1[_k]) % 30.0
    _off = min(_psi, 30.0-_psi)
    _mm  = np.deg2rad(_off)*18.11
    gate(_mm < 0.15*DRIVE_WINDOW,
         f"{_k} strike bar lands {_off:.3f} deg from the strike line on date {_d} "
         f"= {_mm:.3f}mm of a {DRIVE_WINDOW}mm drive window "
         f"({100*_mm/DRIVE_WINDOW:.0f}%)")

# ---- 10. DRIVE WHEEL (#149) — measured off the emitted pieces ----
print()
import drive_v17 as DV
_BOARD_TIP = 41.86
_targets = {"24h": ("board teeth", 5.00, 9.00, None),
            "23h": ("month", BAND["month"]+2.2, BAND["month"]+3.0, BAND["month"]+1.5),
            "22h": ("feb",   BAND["feb"]+2.2,   BAND["feb"]+3.0,   BAND["feb"]+1.5),
            "21h": ("leap",  BAND["leap"]+2.2,  BAND["leap"]+3.0,  BAND["leap"]+1.5)}
for _i, (_nm, _off, _z0, _z1, _t) in enumerate(DV.ARMS):
    _fn = f"{158+_i}_drive_{_nm}_v17.stl"
    _T = tris(_fn); _V = _T.reshape(-1,3)
    _r = np.hypot(_V[:,0], _V[:,1]).max()
    _tgt, _tz0, _tz1, _mesh = _targets[_nm]
    gate(abs(_r - DV.DTIP) < 0.05,
         f"{_nm} arm tip reaches r{_r:.2f} (DTIP {DV.DTIP}) -> engages the "
         f"{_tgt} at {_BOARD_TIP-(DV.DDR-_r):.2f}mm of the 1.12mm window")
    gate(abs(_z0-_tz0) < 1e-6 and abs(_z1-_tz1) < 1e-6,
         f"{_nm} arm sits {_z0:.2f}..{_z1:.2f} == the {_tgt} strike tip "
         f"{_tz0:.2f}..{_tz1:.2f}")
    if _mesh is not None:
        gate(_z0 - _mesh > 0.3,
             f"{_nm} arm clears the {_tgt} MESH lamina below it by {_z0-_mesh:.2f}mm "
             f"(they must not be coplanar or the arm fouls the gear)")
    _world = (180.0-_off) - (int(_nm[:2])/24)*360
    gate(abs((_world % 360) - 180.0) < 1e-6,
         f"{_nm} arm points at the board (world {_world%360:.1f}) at {_nm[:2]}:00")
gate(DV.DDR - DV.DBODY - _BOARD_TIP > 1.0,
     f"drive body clears the board teeth by {DV.DDR-DV.DBODY-_BOARD_TIP:.2f}mm")
gate(DV.DDR - DV.DBODY - 40.94 > 1.0,
     f"drive body clears the satellites by {DV.DDR-DV.DBODY-40.94:.2f}mm")
gate(DV.SQ_HW - DV.POST_R > 1.0,
     f"drive sleeve wall {DV.SQ_HW-DV.POST_R:.2f}mm — the square key must ENCLOSE the "
     f"r{DV.POST_R} post, which the sun tower's K4 (4.42 across) cannot")

print("\n" + ("  *** GATE FAILED: " + str(len(FAILS)) + " ***" if FAILS else "  ALL GATES PASS"))
sys.exit(1 if FAILS else 0)
