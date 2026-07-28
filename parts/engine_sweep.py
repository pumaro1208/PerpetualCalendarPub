#!/usr/bin/env python3
"""ENGINE INTERFERENCE SWEEP — does the rotating calendar stack clear the board?

Ron's question (verbatim): "Will the gears rotate on top of the board now or do
the pegs block them. Also verify that the sun tower is configured properly to
allow the entire perpetual stack to function without grinding or blocking."

Method (board frame, origin on the sun/board axis, +z up):
  * The satellites are FIXED to the board — the board carries them around the
    fixed sun, and each satellite SPINS on its board-fixed post (meshing the sun).
    So relative to the BOARD, a satellite's pivot does not move: it only spins.
    Its danger volume is therefore a DISC of radius = lamina tip about its own
    fixed pivot, over that lamina's z-band — NOT a full annulus. A board obstacle
    grinds iff it falls inside that disc AND overlaps the lamina's z-band.
  * "Obstacles" = raised board vertices EXCLUDING the intended satellite pivot
    post (the satellite's own axle). Board vertices are the ACTUAL regenerated
    STL; satellite tip radius and z extents are MEASURED from the actual STL —
    no hand numbers trusted. Bands fill the full lamina z-extent (prism-boundary
    planes), so a feature poking into the middle of a lamina is caught.

Assembly Z-truth (from the generators' own seating gates):
  board top  = 9.0            (acceptance_39_40 A20b: "board top 9.0")
  sun        = 9.5 .. 19.5    (part_42 docstring / A31: seats 9.5, h10, spans LA/LB/LC)
  month sat  mesh underside = board_top + spacer(1.4) = 10.4   (acceptance_43 A23)
  feb / leap mesh laminae at the LB / LC sun bands (finding 79): 13.0 / 16.5

Frame self-check: the assembled sun and the month mesh-lamina MUST overlap in
radius and z (they mesh). If they don't, the stack heights are wrong and every
"clear" below is vacuous — so the sweep asserts the engagement first (guards the
finding-96/-100 vacuous-pass disease).

Run from parts/ :  python3 engine_sweep.py [02e|02f]   (default: both)
"""
import struct, os, sys, numpy as np
import generator as G, generator_v13 as V13
import generator_v16 as G16, central_hub as C

SUN_ORBIT = G.SUN_ORBIT                 # 23.75
STN = {"month": V13.STN_M, "feb": V13.STN_F, "leap": V13.STN_L}   # degrees
BOARD_TOP = 9.0
BOARD_ZOFF = BOARD_TOP - 4.0            # board local top (4.0) -> assembly 9.0
SUN_ZOFF  = 9.5
# satellite mesh-lamina underside altitude in assembly (measured seatings)
SAT_ZOFF = {"month": 10.4, "feb": 13.0, "leap": 16.5}
FLUSH = 0.05                            # ignore sub-slice grazes below print resolution

CAND = ["stl_v13", "parts/stl_v13", "../parts/stl_v13",
        "stl", "parts/stl", "../parts/stl"]

def load(fn):
    for p in CAND:
        fp = os.path.join(p, fn)
        if os.path.exists(fp):
            with open(fp, "rb") as f:
                f.read(80); n = struct.unpack("<I", f.read(4))[0]
                V = np.zeros((n*3, 3))
                for i in range(n):
                    d = struct.unpack("<12fH", f.read(50))
                    V[i*3], V[i*3+1], V[i*3+2] = d[3:6], d[6:9], d[9:12]
            return V
    raise FileNotFoundError(f"{fn} not found in {CAND}")

def regen():
    C.part_02e_board_bigbore_v16(); C.part_02f_board_v16()
    G16.part_42_sun_v16()
    G16.receiver_lamina_r2("33_receiver_month_r2_v16.stl", 5)
    G16.receiver_lamina("34_receiver_feb_v16.stl", 1)

POST_R = 3.0                            # exclude the satellite pivot post (its own axle)

def lamina_bands(Vsat, zoff):
    """Fill the satellite solid into CONTINUOUS z-bands between its prism
    boundary planes; each band's tip = max pivot-radius on the two bounding
    planes (a prism spanning [z0,z1] reaches full radius at both). Returns
    (z0, z1, tip_about_pivot)."""
    z = Vsat[:, 2] + zoff
    rp = np.hypot(Vsat[:, 0], Vsat[:, 1])
    planes = np.unique(np.round(z, 2))
    bands = []
    for z0, z1 in zip(planes[:-1], planes[1:]):
        m = (np.abs(z - z0) < 1e-2) | (np.abs(z - z1) < 1e-2)
        bands.append((z0, z1, rp[m].max()))
    merged = []
    for b in bands:
        if merged and abs(merged[-1][2]-b[2]) < 1e-6 and abs(merged[-1][1]-b[0]) < 1e-6:
            merged[-1] = (merged[-1][0], b[1], b[2])
        else:
            merged.append(b)
    return merged

def board_obstacles(board_fn):
    """Raised board vertices (above the tooth rim) MINUS the intended satellite
    pivot post at STN_M (the month satellite's own axle). Returns world x,y,z."""
    V = load(board_fn)
    z = V[:, 2] + BOARD_ZOFF
    x, y = V[:, 0], V[:, 1]
    pm = np.array([SUN_ORBIT*np.cos(np.deg2rad(STN["month"])),
                   SUN_ORBIT*np.sin(np.deg2rad(STN["month"]))])
    d_post = np.hypot(x - pm[0], y - pm[1])
    m = (z > BOARD_TOP + FLUSH) & (d_post > POST_R)     # raised, and not the axle post
    return x[m], y[m], z[m]

def frame_selfcheck(sun, month):
    """Sun outer teeth must overlap the month mesh-lamina in r AND z (they mesh)."""
    zs = sun[:, 2] + SUN_ZOFF; rs = np.hypot(sun[:, 0], sun[:, 1])
    zm = month[:, 2] + SAT_ZOFF["month"]
    rpm = np.hypot(month[:, 0], month[:, 1])
    # month mesh lamina (its low band) about center inner edge:
    mm = zm < SAT_ZOFF["month"] + 2.0
    center_inner = SUN_ORBIT - rpm[mm].max()       # closest the lamina reaches to center
    zov = (zs.min() <= zm[mm].max()) and (zs.max() >= zm[mm].min())
    rov = rs.max() >= center_inner
    print(f"  frame self-check: sun r_out {rs.max():.2f} z[{zs.min():.1f},{zs.max():.1f}]  "
          f"vs month mesh center-reach {center_inner:.2f} z[{zm[mm].min():.1f},{zm[mm].max():.1f}]")
    print(f"    radial overlap {rov} ({rs.max():.2f} >= {center_inner:.2f}), "
          f"z overlap {zov}  ->  {'MESH CONFIRMED' if (rov and zov) else '*** NO MESH: frame invalid ***'}")
    return rov and zov

def sweep(board_fn, sats):
    ox, oy, oz = board_obstacles(board_fn)
    orb_r = np.hypot(ox, oy)
    print(f"\n=== {board_fn}: {len(ox)} raised board obstacles (excl. the pivot post) ===")
    if len(ox):
        print(f"    obstacle span: r[{orb_r.min():.2f},{orb_r.max():.2f}] z[{oz.min():.2f},{oz.max():.2f}]")
    else:
        print("    (no raised obstacles — board face is clear except the pivot post)")
    total = 0
    for sname in ("month", "feb", "leap"):
        if sname not in sats: continue
        p = np.array([SUN_ORBIT*np.cos(np.deg2rad(STN[sname])),
                      SUN_ORBIT*np.sin(np.deg2rad(STN[sname]))])
        d = np.hypot(ox - p[0], oy - p[1])            # distance from THIS satellite's pivot
        for z0, z1, tip in lamina_bands(Vsat := sats[sname], SAT_ZOFF[sname]):
            hit = (oz > z0 + FLUSH) & (oz < z1 - FLUSH) & (d < tip - FLUSH)
            if hit.sum():
                pen = oz[hit].max() - z0
                total += 1
                print(f"  *** GRIND  {sname:5s} lamina z[{z0:.1f},{z1:.1f}] disc r<{tip:.1f} about pivot  "
                      f"<- board obstacle at r[{orb_r[hit].min():.1f},{orb_r[hit].max():.1f}] "
                      f"z<= {oz[hit].max():.1f}  (+{pen:.2f} mm into lamina)")
    print("  RESULT:", "CLEAR — no board obstacle enters any satellite disc"
          if total == 0 else f"{total} GRIND BAND(S)")
    return total

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    regen()
    sun = load("42_sun_v16.stl")
    sats = {"month": load("33_receiver_month_r2_v16.stl"),
            "feb":   load("34_receiver_feb_v16.stl")}
    # leap rides even higher (LC band); its plate is small — include if present
    try: sats["leap"] = load("35_leap_shuttle_v16.stl")
    except FileNotFoundError: pass
    assert len(sun) and all(len(v) for v in sats.values()), "empty solids — vacuous run"

    print("ENGINE INTERFERENCE SWEEP (board frame, disc-about-fixed-pivot)")
    ok = frame_selfcheck(sun, sats["month"])
    if not ok:
        print("FRAME INVALID — aborting (results would be vacuous)"); sys.exit(2)

    which = sys.argv[1:] or ["02e", "02f"]
    res = {}
    if "02e" in which:
        print("\n----- BEFORE: committed board 02e (pegs + station dots) -----")
        res["02e"] = sweep("02e_board_bigbore_v16.stl", sats)
    if "02f" in which:
        print("\n----- AFTER: board 02f (pegs + dots removed) -----")
        res["02f"] = sweep("02f_board_v16.stl", sats)
    print("\nSUMMARY:", {k: ("CLEAR" if v == 0 else f"{v} grind") for k, v in res.items()})
    sys.exit(1 if res.get("02f", 0) else 0)
