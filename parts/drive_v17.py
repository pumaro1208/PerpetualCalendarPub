#!/usr/bin/env python3
"""#149 DRIVE WHEEL v17 — the 24h wheel, with arms that reach 21h / 22h / 23h.

Ron: "I need the correct 24 hr wheel printed that can hit the 21,22,23 hours."

This is the part that has been blocking everything: without it there is nothing to
crank. The old 30_drive_v16 is only 15mm tall overall and was built for the 3.5mm
band spacing; the v17 stack at 6.5 pitch needs the 21h arm up at 24.7-25.5.

GEOMETRY, taken from the simulator, not invented:
  DDR 73.50   drive axis, from the board axis, along the strike line
  DBODY 29.2  body radius        -> reaches in to 44.30
  DTIP  32.76 arm tip orbit      -> reaches in to 40.74
Board tooth tip and satellite strike tip both stand at 41.86, so every arm engages
by 41.86 - 40.74 = 1.12mm — the drive window every clocking number is quoted against.
The body clears the board teeth by 2.44 and the satellites by 3.36.

ANGLES. The wheel turns once per day, so one hour is 15 deg. Each arm has to point
at the board (180 deg in the wheel frame) at its OWN hour, and the simulator draws
them at (180 - off) with off = 0/15/30/45 for 24h/23h/22h/21h. Verified: all four
land on world 180 at their hour.

ALTITUDES. Each arm hits a STRIKE TIP and must clear the MESH lamina 0.7mm below it:
  24h  board teeth      5.00 -  9.00
  23h  month strike    11.70 - 12.50   (month mesh ends 11.00)
  22h  feb strike      18.20 - 19.00   (feb mesh ends 17.50)
  21h  leap strike     24.70 - 25.50   (leap mesh ends 24.00)

WHY FOUR STACKED PIECES rather than one tall wheel. A single body would be a r29.2
cylinder 20.5mm tall — 55cm^3 — with four small tabs whose undersides are all
unsupported cantilevers. Split at each arm instead and every piece prints ARM DOWN
ON THE BED: no overhang anywhere, no supports, a quarter of the material. It is the
same idiom as the sun tower, and it is why the tower prints clean.

Each piece carries its arm at its own pre-rotated angle, so a plain square key
clocks all four correctly — exactly how the receivers handle their ALPHA. The key
is a sleeve (round bore on the fixture's r4.17 drive post, square outside), because
the drive post has to stay round: this wheel is the crank, it must turn.
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
from shapely import affinity
from generator_v13 import write_stl
from weld import stack

DDR, DBODY, DTIP = 73.50, 29.20, 32.76
POST_R   = 4.17          # fixture drive post — round, design-at-bore (#136)
# The drive key CANNOT be the sun tower's K4. That key is 4.42 across, and the
# fixture's drive post is r4.17 = 8.34 diameter — bigger than the whole key. A
# sleeve has to wrap the post, so the square has to enclose it plus a wall:
#   8.34 bore + 2 x 1.58 wall = 11.50 across.
# (First cut used K4 and the bore simply ate the key, leaving four corner slivers —
# the weld gate caught it as "4 disconnected solids".)
SQ_HW    = 5.75          # drive square key half-width -> 11.50 across flats
HW_BASE  = 0.075         # arm half-angle at the body (rad), from the simulator
HW_TIP   = 0.030         # ...and at the tip: the arm tapers
ARMS = [("24h", 0.0,  5.00,  9.00, "board teeth"),
        ("23h", 15.0, 11.70, 12.50, "month strike tip"),
        ("22h", 30.0, 18.20, 19.00, "feb strike tip"),
        ("21h", 45.0, 24.70, 25.50, "leap strike tip")]
PIECE_TOP = {"24h": 11.70, "23h": 18.20, "22h": 24.70, "21h": 30.00}

def arm_poly(off_deg):
    """One tapered arm, body radius out to tip, centred on (180 - off)."""
    a = np.deg2rad(180.0 - off_deg)
    pts = [(DBODY*np.cos(a-HW_BASE), DBODY*np.sin(a-HW_BASE)),
           (DTIP *np.cos(a-HW_TIP),  DTIP *np.sin(a-HW_TIP)),
           (DTIP *np.cos(a+HW_TIP),  DTIP *np.sin(a+HW_TIP)),
           (DBODY*np.cos(a+HW_BASE), DBODY*np.sin(a+HW_BASE))]
    return Polygon(pts)

def piece(nm, off, z0, z1, top, no):
    """Body disc + its arm. The arm sits at the BOTTOM so the part prints arm-down
    on the bed — that is what makes the whole wheel support-free."""
    body = Point(0,0).buffer(DBODY, 192)
    key  = Polygon([(SQ_HW,SQ_HW),(-SQ_HW,SQ_HW),(-SQ_HW,-SQ_HW),(SQ_HW,-SQ_HW)])
    arm  = arm_poly(off)
    h = top - z0
    write_stl(no, stack([
        (0.0,      z1-z0, unary_union([body, arm]).difference(key)),   # arm band
        (z1-z0,    h,     body.difference(key)),                       # body above it
    ]))
    return h

def sleeve(no="169_drive_sleeve_revC_v17.stl", length=25.0):
    """Rev C (#167) — a RETRACTION of rev B, which is scrap.

    Rev B added a flange foot "standing on the fixture base at 2.5". The fixture
    has no bare base there: since r58 the drive post carries a COLLAR, r6.5 from
    the platform (4.0) up to exactly 5.0 — and the collar top IS the axial seat
    the #149 stack was designed around. The bottom piece's square bore (11.50
    across flats) cannot pass the collar's 13.0 diameter, so the stack seats at
    5.0 with no extra part at all. Rev B's r4.17 flange bore could not swallow
    the collar either, so the flange LANDED ON IT: stack at 7.5, every arm
    +2.5mm — 24h half-engaged on the board, 23h striking the empty gap between
    month tips and feb mesh, 22h/21h missing outright (Ron: "things are not
    lining up"). #159's premise — "the stack had no z-datum" — was wrong; the
    fixture always had one. Finding #159 is retracted to that extent and the
    June low-stack observation is REOPENED (whatever caused it, it was not a
    missing datum).

    Rev C is the honest sleeve: a straight keyed tube, bottom face seating on
    the collar top at 5.0 alongside the bottom piece, top flush with the 21h
    piece at 30.0. Round r4.17 bore (this wheel is the crank); square 11.50
    outside; length 25.0."""
    sq = Polygon([(SQ_HW,SQ_HW),(-SQ_HW,SQ_HW),(-SQ_HW,-SQ_HW),(SQ_HW,-SQ_HW)])
    bore = Point(0,0).buffer(POST_R, 64)
    wall = SQ_HW - POST_R
    assert wall > 1.0, f"sleeve wall only {wall:.2f}mm"
    write_stl(no, stack([(0.0, length, sq.difference(bore))]))
    return wall

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    for i, (nm, off, z0, z1, tgt) in enumerate(ARMS):
        h = piece(nm, off, z0, z1, PIECE_TOP[nm], f"{158+i}_drive_{nm}_v17.stl")
        print(f"  {nm}: arm {180-off:5.1f}deg, z {z0:5.2f}-{z1:5.2f} -> {tgt:17s} "
              f"piece {h:5.2f} tall, prints arm-down")
    w = sleeve()
    print(f"  + sleeve rev C: straight tube, seats on the COLLAR at z5.0 (the datum the "
          f"fixture always had); square {2*SQ_HW:.2f} across, wall {w:.2f}mm")

    # ---- #167 SEATED-STACK ACCEPTANCE — the gate #159 never had ---------------
    # Measured off the fixture and part STLs: where does the stack actually come
    # to rest, and where does each arm band land? Asserted against the strike
    # targets, not printed as numbers.
    import trimesh
    FAILS = 0
    def gate(ok, msg):
        global FAILS
        print(f"  [{'PASS' if ok else 'FAIL'}] {msg}")
        if not ok: FAILS += 1
    fx = trimesh.load("stl_v13/168_fixture_r64_v17.stl")
    # collar top: highest z where material exists in the annulus r(4.5..6.4) about the drive axis
    seat = 0.0
    for z in np.arange(3.0, 8.0, 0.05):
        s = fx.section(plane_origin=[0,0,z], plane_normal=[0,0,1])
        if s is None: continue
        hit = False
        for L in s.discrete:
            L = np.array(L)[:,:2]
            d = np.hypot(L[:,0]-36.75, L[:,1])
            if 4.4 < d.max() < 6.7: hit = True   # a boundary between post r4.17 and collar r6.5
        if hit: seat = z
    gate(abs(seat-5.0) < 0.1, f"fixture collar top measured at z{seat:.2f} — THE axial seat (was always there)")
    gate(2*SQ_HW < 13.0, f"bottom piece square bore {2*SQ_HW:.2f} < collar dia 13.0 — stack CANNOT pass, seats at 5.0")
    gate(2*POST_R < 13.0, "sleeve bore r4.17 also seats on the collar — sleeve and stack share the 5.0 datum")
    # cumulative arm bands from the emitted pieces, seated at 5.0:
    zb = 5.0
    for i, (nm, off, z0, z1, tgt) in enumerate(ARMS):
        m = trimesh.load(f"stl_v13/{158+i}_drive_{nm}_v17.stl")
        ph = m.bounds[1][2] - m.bounds[0][2]
        # arm band = the z where the section reaches DTIP
        lo = hi = None
        for z in np.arange(0.05, ph, 0.1):
            s = m.section(plane_origin=[0,0,z], plane_normal=[0,0,1])
            if s is None: continue
            rmax = max(np.hypot(np.array(L)[:,0], np.array(L)[:,1]).max() for L in s.discrete)
            if rmax > DTIP - 0.1:
                if lo is None: lo = z
                hi = z
        gate(abs((zb+lo)-z0) < 0.15 and abs((zb+hi)-z1) < 0.15,
             f"{nm} arm band seated {zb+lo:.2f}..{zb+hi:.2f} (target {z0:.2f}..{z1:.2f}, {tgt})")
        zb += ph
    # rev B condemnation, measured: its flange bore cannot swallow the collar
    try:
        mb = trimesh.load("stl_v13/162_drive_sleeve_v17.stl")
        s = mb.section(plane_origin=[0,0,0.5], plane_normal=[0,0,1])
        rmin = min(np.hypot(np.array(L)[:,0], np.array(L)[:,1]).min() for L in s.discrete)
        gate(rmin < 6.5, f"rev B flange bore r{rmin:.2f} < collar r6.5 -> lands ON the collar, "
             f"stack at 7.5 (+2.5) — WHY rev B is scrap (#167)")
    except Exception:
        print("  [    ] rev B STL absent — condemnation gate skipped")
    sy = trimesh.load("stl_v13/169_drive_sleeve_revC_v17.stl")
    gate(abs((sy.bounds[1][2]-sy.bounds[0][2]) - 25.0) < 0.02,
         "rev C length 25.0: seats 5.0, top flush with the 21h piece at 30.0")
    print(f"\n  {'DRIVE STACK SEATED' if not FAILS else f'*** SEAT GATE FAILED: {FAILS} ***'}")
    sys.exit(1 if FAILS else 0)
