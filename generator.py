#!/usr/bin/env python3
"""
Oechslin Program Wheel Demonstrator — v1
Based on EP 1351104 (expired), Embodiment 1 (monthly program wheel).
Generates printable STLs. All parts print flat, no supports intended.

Units: mm. Z=0 is the print bed for each part's own STL.
Assembly Z-stack (from base):
  L0  base plate               z 0..4     (posts integral)
  LP  program wheel board      z 5..9     (31 drive teeth at this level)
  LA  month-wheel level        z 9.5..12.5  (sun tower serves LA+LB)
  LB  february-wheel level     z 13..16
  LC  slider / leap level      z 16.5..19.5
Drive wheel carries: locking disc + drive pin at LP, finger arms at LA/LB/LC.
"""

import numpy as np, struct, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")
os.makedirs(OUT, exist_ok=True)

# ---------------- parameters ----------------
P = dict(
    # sun / satellite mesh (simple rounded-trapezoid teeth, logic demo)
    m_sun=2.5,            # module for sun/satellite mesh
    sun_teeth=7,
    sat_teeth=12,
    leap_sat_teeth=12,    # satellite 228 (carries geneva pin)
    long_extra=3.5,       # extra radial length of "long" (retractable) teeth
    backlash=0.45,        # generous, printed plastic
    # program wheel
    prog_teeth=31,
    prog_root_r=39.0,
    prog_tip_r=43.5,
    # drive wheel
    lock_r=24.0,          # locking disc radius
    pin_r=2.0,            # drive pin radius
    finger_clear_r=42.8,  # fingers' closest approach to main axis
    # posts / bores
    post_d=8.0, bore_clr=0.35,
    sat_post_d=5.0,
    plate_t=4.0, wheel_t=4.0, level_t=3.0, gap=0.5,
    # geneva leap train
    geneva_stations=28,
    geneva_r=11.0,        # geneva wheel pitch radius (slot circle)
    cam_lo_r=10.0, cam_hi_r=13.0,   # cam valley / lobe radii
    seg=1440,             # polar resolution
)

M = P["m_sun"]
SUN_ORBIT = M * (P["sun_teeth"] + P["sat_teeth"]) / 2.0   # satellite center orbit radius
SAT_TIP   = M * P["sat_teeth"] / 2.0 + M                   # short-tooth tip radius
SAT_ROOT  = M * P["sat_teeth"] / 2.0 - 1.25 * M
SUN_TIP   = M * P["sun_teeth"] / 2.0 + M
SUN_ROOT  = M * P["sun_teeth"] / 2.0 - 1.25 * M
LONG_TIP  = SAT_TIP + P["long_extra"]
D_DRIVE   = P["prog_tip_r"] + P["lock_r"] + 0.3            # main axis -> drive axis
FINGER_R  = D_DRIVE - P["finger_clear_r"]                  # finger tip radius about drive axis
PIN_ORBIT = D_DRIVE - (P["prog_root_r"] + 1.5)             # drive pin orbit radius

# assembly Z levels (for the assembly-check report only; parts print at z=0)
Z = dict(LP=(5.0, 9.0), LA=(9.5, 12.5), LB=(13.0, 16.0), LC=(16.5, 19.5))

# ---------------- mesh helpers ----------------
def _stitch(outer_pts, inner_pts, z0, z1):
    """Watertight solid between an outer and inner closed polyline (same length),
    both CCW, from z0 to z1. Returns list of triangles (n,3,3)."""
    n = len(outer_pts)
    tris = []
    for i in range(n):
        j = (i + 1) % n
        o0 = np.array([*outer_pts[i], z0]); o1 = np.array([*outer_pts[j], z0])
        o2 = np.array([*outer_pts[i], z1]); o3 = np.array([*outer_pts[j], z1])
        i0 = np.array([*inner_pts[i], z0]); i1 = np.array([*inner_pts[j], z0])
        i2 = np.array([*inner_pts[i], z1]); i3 = np.array([*inner_pts[j], z1])
        # outer wall (normal out)
        tris += [(o0, o1, o3), (o0, o3, o2)]
        # inner wall (normal in)
        tris += [(i1, i0, i2), (i1, i2, i3)]
        # bottom annulus (normal -z)
        tris += [(o0, i0, i1), (o0, i1, o1)]
        # top annulus (normal +z)
        tris += [(o2, o3, i3), (o2, i3, i2)]
    return tris

def polar_solid(r_outer, z0, z1, r_inner=None, cx=0.0, cy=0.0, seg=None):
    """Solid of revolution-ish: outer radius profile r_outer(θ) (array len seg),
    optional inner profile (scalar or array). Centered at (cx,cy)."""
    seg = seg or P["seg"]
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    ro = np.broadcast_to(np.asarray(r_outer, float), th.shape).copy() if np.ndim(r_outer) else np.full(seg, float(r_outer))
    if np.ndim(r_outer) == 1:
        ro = np.asarray(r_outer, float)
        assert len(ro) == seg
    if r_inner is None:
        ri = np.full(seg, 0.001)          # degenerate tiny core -> effectively solid
    else:
        ri = np.asarray(r_inner, float)
        ri = np.full(seg, float(r_inner)) if ri.ndim == 0 else ri
    op = np.stack([cx + ro*np.cos(th), cy + ro*np.sin(th)], axis=1)
    ip = np.stack([cx + ri*np.cos(th), cy + ri*np.sin(th)], axis=1)
    return _stitch(list(op), list(ip), z0, z1)

def cylinder(cx, cy, r, z0, z1, seg=96):
    return polar_solid(r, z0, z1, r_inner=None, cx=cx, cy=cy, seg=seg)

def sector_prism(cx, cy, r1, r2, th1, th2, z0, z1, seg=64):
    """Annular sector solid (a curved 'box')."""
    th = np.linspace(th1, th2, seg)
    outer = [(cx + r2*np.cos(t), cy + r2*np.sin(t)) for t in th]
    inner = [(cx + r1*np.cos(t), cy + r1*np.sin(t)) for t in th]
    ring = outer + inner[::-1]
    return _poly_prism(ring, z0, z1)

def box(cx, cy, w, h, z0, z1, ang=0.0):
    dx, dy = w/2, h/2
    c, s = np.cos(ang), np.sin(ang)
    pts = [(-dx,-dy),(dx,-dy),(dx,dy),(-dx,dy)]
    pts = [(cx + x*c - y*s, cy + x*s + y*c) for x,y in pts]
    return _poly_prism(pts, z0, z1)

def _poly_prism(pts, z0, z1):
    """Extrude a simple CCW polygon (fan-triangulated caps: polygon must be
    star-shaped about its centroid — true for all shapes we use)."""
    n = len(pts)
    cx = sum(p[0] for p in pts)/n; cy = sum(p[1] for p in pts)/n
    # ensure CCW
    area = sum(pts[i][0]*pts[(i+1)%n][1]-pts[(i+1)%n][0]*pts[i][1] for i in range(n))
    if area < 0: pts = pts[::-1]
    tris = []
    C0 = np.array([cx, cy, z0]); C1 = np.array([cx, cy, z1])
    for i in range(n):
        j = (i+1) % n
        a0 = np.array([*pts[i], z0]); b0 = np.array([*pts[j], z0])
        a1 = np.array([*pts[i], z1]); b1 = np.array([*pts[j], z1])
        tris += [(a0, b0, b1), (a0, b1, a1)]      # wall
        tris += [(C0, b0, a0)]                      # bottom
        tris += [(C1, a1, b1)]                      # top
    return tris

def write_stl(name, tris):
    path = os.path.join(OUT, name)
    with open(path, "wb") as f:
        f.write(b"OechslinV1".ljust(80, b"\0"))
        f.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            n = np.cross(b - a, c - a)
            l = np.linalg.norm(n); n = n/l if l > 0 else n
            f.write(struct.pack("<3f", *n))
            for v in (a, b, c):
                f.write(struct.pack("<3f", *v))
            f.write(b"\0\0")
    print(f"  wrote {name:36s} {len(tris):7d} tris")

# ---------------- gear profile ----------------
def gear_profile(n_teeth, root_r, tip_r, long_set=(), long_tip=None,
                 tooth_frac=0.42, ramp_frac=0.14, seg=None, phase=0.0):
    """Rounded-trapezoid polar gear profile. long_set: tooth indices with
    extended tips. phase: rotates tooth 0 center to given angle (rad)."""
    seg = seg or P["seg"]
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    r = np.full(seg, root_r)
    pitch = 2*np.pi / n_teeth
    for k in range(n_teeth):
        tipr = long_tip if (k in long_set and long_tip) else tip_r
        c = (phase + k * pitch) % (2*np.pi)
        d = np.angle(np.exp(1j*(th - c)))          # signed angular distance
        half_top = tooth_frac * pitch / 2
        ramp = ramp_frac * pitch
        # smooth trapezoid: 1 on top, ramps down to 0
        u = (np.abs(d) - half_top) / ramp
        w = np.clip(1 - u, 0, 1)
        w = w*w*(3-2*w)                              # smoothstep
        r = np.maximum(r, root_r + (tipr - root_r) * w)
    return r

# ---------------- parts ----------------
def part_base_plate():
    tris = []
    t = P["plate_t"]
    # main plate: rounded bar spanning both axes
    tris += cylinder(0, 0, 58, 0, t, seg=256)
    tris += cylinder(D_DRIVE, 0, 34, 0, t, seg=192)
    tris += box(D_DRIVE/2, 0, D_DRIVE, 62, 0, t)
    # central post: round base, D-flat key section for sun tower, cap spigot
    ph = P["post_d"]/2
    tris += cylinder(0, 0, ph, t, t + 5.5, seg=64)                     # under program wheel
    # D-flat section (sun key), z from program top to top of LB
    dflat = []
    thd = np.linspace(0, 2*np.pi, 64, endpoint=False)
    for a in thd:
        x, y = ph*np.cos(a), ph*np.sin(a)
        x = min(x, ph - 1.8)   # flat
        dflat.append((x, y))
    tris += _poly_prism(dflat, t + 5.5, t + 12.5)
    tris += cylinder(0, 0, ph - 0.8, t + 12.5, t + 17.5, seg=48)       # cap spigot (slider level clearance)
    # drive post
    tris += cylinder(D_DRIVE, 0, ph, t, t + 15.0, seg=64)
    tris += cylinder(D_DRIVE, 0, ph - 0.8, t + 15.0, t + 18.0, seg=48)
    # program-wheel thrust pads (3 small ring pads)
    for a in (0.4, 2.5, 4.6):
        tris += cylinder(14*np.cos(a), 14*np.sin(a), 4.0, t, t + 0.9, seg=32)
    # date pointer nub at 12 o'clock relative to program wheel tick ring
    tris += box(0, 51.5, 3, 9, 0, t + 2.0)
    write_stl("01_base_plate.stl", tris)

def part_program_wheel():
    tris = []
    t = P["wheel_t"]
    prof = gear_profile(P["prog_teeth"], P["prog_root_r"], P["prog_tip_r"],
                        tooth_frac=0.30, ramp_frac=0.22)
    bore = P["post_d"]/2 + P["bore_clr"]
    tris += polar_solid(prof, 0, t, r_inner=bore)
    # 31 tick bumps on top near rim; taller one = "1"
    for k in range(31):
        a = 2*np.pi * k / 31
        h = 2.2 if k == 0 else 1.0
        tris += cylinder(36.5*np.cos(a), 36.5*np.sin(a), 1.1, t, t + h, seg=16)
    # satellite posts (heights reach through their level + cap spigot)
    # angular stations on the wheel (chosen for clearance): month 0°, feb 120°, leap-sat 240°
    stations = dict(month=0.0, feb=2*np.pi/3, leap=4*np.pi/3)
    post_r = P["sat_post_d"]/2
    heights = dict(month=(t, t + 0.5 + 3.0 + 1.2),         # into LA
                   feb=(t, t + 0.5 + 3.0 + 0.5 + 3.0 + 1.2),  # into LB
                   leap=(t, t + 0.5 + 3.0 + 1.2))
    for k, ang in stations.items():
        cx, cy = SUN_ORBIT*np.cos(ang), SUN_ORBIT*np.sin(ang)
        z0, z1 = heights[k]
        tris += cylinder(cx, cy, post_r, z0, z1, seg=48)
        tris += cylinder(cx, cy, post_r - 0.6, z1, z1 + 2.5, seg=32)   # cap spigot
    # geneva/cam post: inward of leap satellite, station 240° + offset
    cam_orbit = 27.0
    cam_ang = 4*np.pi/3 + 0.62
    ccx, ccy = cam_orbit*np.cos(cam_ang), cam_orbit*np.sin(cam_ang)
    tris += cylinder(ccx, ccy, post_r, t, t + 0.5 + 3.0 + 0.5 + 3.0 + 0.5 + 3.2, seg=48)
    tris += cylinder(ccx, ccy, post_r - 0.6, t + 10.7, t + 13.2, seg=32)
    # slider rails at LC (station ~300° pointing radially out)
    sa = 5*np.pi/3
    ux, uy = np.cos(sa), np.sin(sa)
    railz0, railz1 = t + 0.5 + 3.0 + 0.5 + 3.0 + 0.5, t + 11.5 + 3.0
    for side in (-1, 1):
        # two rails parallel to slider travel, with inward lips
        off = side * 5.4
        rx, ry = -uy*off, ux*off
        tris += box((28.5)*ux + rx, (28.5)*uy + ry, 2.2, 17, railz0, railz1, ang=sa + np.pi/2)
        tris += box((28.5)*ux + rx - side*(-uy)*1.4, (28.5)*uy + ry - side*(ux)*1.4,
                    1.4, 17, railz1 - 0.9, railz1, ang=sa + np.pi/2)   # lip
    write_stl("02_program_wheel.stl", tris)
    return stations, (ccx, ccy), sa

def part_sun_tower():
    """Fixed 7t sun serving LA and LB as one keyed column."""
    tris = []
    h = 0.5 + 3.0 + 0.5 + 3.0          # LA + gap + LB
    prof = gear_profile(P["sun_teeth"], SUN_ROOT, SUN_TIP, tooth_frac=0.40, ramp_frac=0.2)
    # D-bore
    seg = P["seg"]
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    ph = P["post_d"]/2 + P["bore_clr"]
    xi = np.minimum(ph*np.cos(th), ph - 1.8 + P["bore_clr"])
    yi = ph*np.sin(th)
    ri = np.sqrt(xi**2 + yi**2)
    # inner profile must follow the D shape in polar form (star-shaped: OK)
    tris += _stitch(
        list(np.stack([prof*np.cos(th), prof*np.sin(th)], axis=1)),
        list(np.stack([xi, yi], axis=1)), 0, h)
    write_stl("03_sun_tower.stl", tris)

def _satellite(name, long_set, note_mark=True):
    tris = []
    t = P["level_t"]
    prof = gear_profile(P["sat_teeth"], SAT_ROOT, SAT_TIP,
                        long_set=long_set, long_tip=LONG_TIP,
                        tooth_frac=0.40, ramp_frac=0.2)
    bore = P["sat_post_d"]/2 + 0.30
    tris += polar_solid(prof, 0, t, r_inner=bore)
    if note_mark:  # alignment dot over tooth 0
        tris += cylinder((SAT_ROOT - 2.5), 0, 0.9, t, t + 0.8, seg=12)
    write_stl(name, tris)

def part_month_wheel():
    # long teeth at indices 7..11 (consecutive — falls out of the 7/12 ratio)
    _satellite("04_month_wheel.stl", long_set={7, 8, 9, 10, 11})

def part_february_wheel():
    _satellite("05_february_wheel.stl", long_set={7})

def part_leap_satellite():
    """Satellite 228 (12t) + geneva drive pin + locking disc, one part."""
    tris = []
    t = P["level_t"]
    prof = gear_profile(P["leap_sat_teeth"], SAT_ROOT, SAT_TIP, tooth_frac=0.40, ramp_frac=0.2)
    bore = P["sat_post_d"]/2 + 0.30
    tris += polar_solid(prof, 0, t, r_inner=bore)
    # locking disc above (LB band) with a relief flat at the pin sector
    lock_r = 8.0
    seg = 720
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    rl = np.full(seg, lock_r)
    d = np.angle(np.exp(1j*(th - 0.0)))
    rl[np.abs(d) < 0.55] = 5.2          # relief so geneva can rotate past
    tris += _stitch(
        list(np.stack([rl*np.cos(th), rl*np.sin(th)], axis=1)),
        list(np.stack([bore*np.cos(th), bore*np.sin(th)], axis=1)),
        t + 0.5, t + 0.5 + 3.0)
    # geneva pin at angle 0 on the disc top band
    tris += cylinder(9.6, 0, 1.4, t + 0.5, t + 0.5 + 3.0, seg=24)
    write_stl("06_leap_satellite.stl", tris)

def part_geneva_cam():
    """28-station geneva wheel + 3-lobe cam ring, one part (levels LB+LC)."""
    tris = []
    seg = P["seg"]
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    ns = P["geneva_stations"]
    # geneva: outer disc with 28 pin-slots (radial notches)
    rg = np.full(seg, P["geneva_r"] + 2.2)
    for k in range(ns):
        c = 2*np.pi*k/ns
        d = np.angle(np.exp(1j*(th - c)))
        slot = np.abs(d) < (2*np.pi/ns)*0.20
        rg[slot] = P["geneva_r"] - 1.8
    bore = P["sat_post_d"]/2 + 0.30
    tris += polar_solid(rg, 0, 3.0, r_inner=bore)                      # LB band
    # cam ring above (LC band): 3 lobes of 78°, one valley quadrant
    rc = np.full(seg, P["cam_lo_r"])
    for q in range(3):
        c = np.deg2rad(90*q)
        d = np.angle(np.exp(1j*(th - c)))
        lobe = np.abs(d) < np.deg2rad(39)
        rc[lobe] = P["cam_hi_r"]
    # smooth the lobe edges
    k = 9
    rc = np.convolve(np.r_[rc[-k:], rc, rc[:k]], np.ones(2*k+1)/(2*k+1), "same")[k:-k]
    tris += polar_solid(rc, 3.5, 6.5, r_inner=bore)
    # leap-quadrant marker
    tris += cylinder((P["cam_lo_r"]-3.0)*np.cos(np.deg2rad(270)),
                     (P["cam_lo_r"]-3.0)*np.sin(np.deg2rad(270)), 1.0, 6.5, 7.3, seg=12)
    write_stl("07_geneva_cam.stl", tris)

def part_slider():
    """Leap slider: cam follower foot -> body -> retractable tooth."""
    tris = []
    t = P["level_t"] - 0.4          # slides inside LC rails
    L_in, L_out = 27.0 - P["cam_hi_r"] - 0.4, 46.0   # follower contact at cam, tooth to 46 when out
    body_w = 9.6
    tris += box((L_out + 14.5)/2, 0, L_out - 14.5, body_w, 0, t)
    # follower foot
    tris += box(15.6, 0, 3.0, 6.0, 0, t)
    # tooth (chamfered nose)
    nose = [(L_out, -2.2), (L_out + 3.2, -1.1), (L_out + 3.2, 1.1), (L_out, 2.2)]
    tris += _poly_prism(nose, 0, t)
    # detent bumps
    for s in (-1, 1):
        tris += cylinder(31.0, s*(body_w/2 - 0.3), 0.55, 0, t, seg=10)
    write_stl("08_leap_slider.stl", tris)

def part_drive_wheel():
    """Locking disc + drive pin (LP) and three finger arms (LA/LB/LC).
    PRINT UPSIDE-DOWN (finger side on bed)."""
    tris = []
    bore = P["post_d"]/2 + P["bore_clr"]
    # locking disc with relief notch around the pin sector
    seg = P["seg"]
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    rl = np.full(seg, P["lock_r"])
    d = np.angle(np.exp(1j*th))
    rl[np.abs(d) < 0.50] = PIN_ORBIT - 3.2       # relief around pin
    tris += _stitch(
        list(np.stack([rl*np.cos(th), rl*np.sin(th)], axis=1)),
        list(np.stack([bore*np.cos(th), bore*np.sin(th)], axis=1)), 0, 4.0)
    # drive pin at angle 0
    tris += cylinder(PIN_ORBIT, 0, P["pin_r"], 0, 4.0, seg=32)
    # hub column through all levels
    tris += cylinder(0, 0, 7.5, 0, 15.0, seg=64)
    # finger arms: 243 (month, LA) at -15°, 242 (feb, LB) at -30°, 241 (slider, LC) at -45°
    arms = [(-15, 4.5, 7.5), (-30, 8.0, 11.0), (-45, 11.5, 14.5)]
    for deg, z0, z1 in arms:
        a = np.deg2rad(deg)
        tris += sector_prism(0, 0, 6.5, FINGER_R, a - 0.10, a + 0.10, z0, z1)
        # rounded tip pad
        tris += cylinder(FINGER_R*np.cos(a), FINGER_R*np.sin(a), 1.6, z0, z1, seg=20)
    # crank boss + handle post on top
    tris += cylinder(0, 0, 11, 15.0, 17.5, seg=64)
    tris += cylinder(14.5, 0, 3.2, 15.0, 24.0, seg=32)
    write_stl("09_drive_wheel.stl", tris)

def part_caps():
    tris = []
    def cap(cx, spig_r):
        t = []
        t += cylinder(cx, 0, 6.5, 0, 2.4, seg=48)
        # friction bore = spigot - 0.25 press fit (printed as blind ring)
        return t, cylinder(cx, 0, spig_r - 0.25 + 0.15, 0.0, 2.4, seg=32)
    # simple flat caps with through-bores sized for press fit onto spigots
    # (bore made by polar_solid inner radius)
    for i, (name, spig) in enumerate([("cap_sat", P["sat_post_d"]/2 - 0.6),
                                       ("cap_main", P["post_d"]/2 - 0.8),
                                       ("cap_drive", P["post_d"]/2 - 0.8)]):
        t = polar_solid(6.5 if "sat" in name else 8.5, 0, 2.4,
                        r_inner=spig + 0.05)
        write_stl(f"10_{name}.stl", t)

def report():
    print("\n--- computed geometry ---")
    print(f"sun orbit (satellite centers): {SUN_ORBIT:.2f} mm")
    print(f"satellite short-tooth reach:   {SUN_ORBIT + SAT_TIP:.2f} mm")
    print(f"satellite long-tooth reach:    {SUN_ORBIT + LONG_TIP:.2f} mm")
    print(f"program wheel tip radius:      {P['prog_tip_r']:.2f} mm")
    print(f"drive axis distance D:         {D_DRIVE:.2f} mm")
    print(f"finger closest approach:       {P['finger_clear_r']:.2f} mm  (tip r {FINGER_R:.2f})")
    print(f"drive pin orbit:               {PIN_ORBIT:.2f} mm")
    ok1 = SUN_ORBIT + SAT_TIP < P["finger_clear_r"] - 0.8
    ok2 = SUN_ORBIT + LONG_TIP > P["finger_clear_r"] + 1.2
    print(f"fingers miss short teeth:      {'OK' if ok1 else '** FAIL **'}")
    print(f"fingers catch long teeth:      {'OK' if ok2 else '** FAIL **'}")
    print(f"footprint across both axes:    {D_DRIVE + 34 + 58:.0f} mm  (bed 256)")

if __name__ == "__main__":
    print("generating Oechslin v1 parts...")
    part_base_plate()
    part_program_wheel()
    part_sun_tower()
    part_month_wheel()
    part_february_wheel()
    part_leap_satellite()
    part_geneva_cam()
    part_slider()
    part_drive_wheel()
    part_caps()
    report()
