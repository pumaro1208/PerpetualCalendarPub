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
    # program wheel (31t involute) / driver (24t involute, one long tooth)
    prog_teeth=31,
    drive_teeth=24,
    m_drive=2.6,
    # drive wheel
    lock_r=24.0,          # locking disc radius
    pin_r=1.7,            # drive pin radius
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
MD        = P["m_drive"]
ADD_F     = 0.6                                             # stub teeth: brief shallow engagement
PROG_TIP  = MD*(P["prog_teeth"]/2 + ADD_F)
PROG_ROOT = MD*(P["prog_teeth"]/2 - 1.25)
D_DRIVE   = MD*(P["prog_teeth"] + P["drive_teeth"])/2.0 + 2.0   # spread mesh (patent-style relief)
FINGER_R  = D_DRIVE - P["finger_clear_r"]                  # finger tip radius about drive axis
DRIVE_TIP = MD*(P["drive_teeth"]/2 + ADD_F)                 # long stub tooth tip orbit

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

# ---------------- involute profile ----------------
def involute_profile(n_teeth, module, pa_deg=20.0, seg=None, phase=0.0,
                     add_f=1.0, ded_f=1.25, backlash=0.25):
    """Polar r(theta) of an involute spur gear. Tooth 0 centered at phase."""
    seg = seg or P["seg"]
    rp = module*n_teeth/2.0
    rb = rp*np.cos(np.deg2rad(pa_deg))
    rt = rp + add_f*module
    rr = rp - ded_f*module
    # involute flank: angle offset vs radius
    rs = np.linspace(max(rb, rr), rt, 40)
    alpha = np.arccos(np.clip(rb/rs, -1, 1))
    inv = np.tan(alpha) - alpha
    inv_p = np.tan(np.arccos(rb/rp)) - np.arccos(rb/rp)
    half_tooth_p = (np.pi/(2*n_teeth)) - backlash/ (2*rp)
    flank_ang = half_tooth_p + inv_p - inv          # half-width angle at radius rs
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    r = np.full(seg, rr)
    pitch = 2*np.pi/n_teeth
    for k in range(n_teeth):
        c = phase + k*pitch
        d = np.abs(np.angle(np.exp(1j*(th - c))))
        # for each theta near tooth, find max radius on flank with flank_ang >= d
        inside = d <= flank_ang[0]
        r[inside] = np.maximum(r[inside], rt*0 + np.interp(d[inside], flank_ang[::-1], rs[::-1]))
        tip = d <= flank_ang[-1]
        r[tip] = rt
    return r, rp, rt, rr

def tooth_outline(module, n_teeth, pa_deg=20.0, backlash=0.25, add_f=1.0):
    """Closed 2D outline of ONE involute tooth (for the drive wheel's long tooth),
    local coords: tooth centered on +x axis, gear center at origin."""
    rp = module*n_teeth/2.0
    rb = rp*np.cos(np.deg2rad(pa_deg))
    rt = rp + add_f*module
    rr = rp - 1.25*module
    rs = np.linspace(max(rb, rr), rt, 24)
    alpha = np.arccos(np.clip(rb/rs, -1, 1))
    inv = np.tan(alpha) - alpha
    inv_p = np.tan(np.arccos(rb/rp)) - np.arccos(rb/rp)
    half_p = (np.pi/(2*n_teeth)) - backlash/(2*rp)
    ang = half_p + inv_p - inv
    up = [(r*np.cos(+a), r*np.sin(+a)) for r, a in zip(rs, ang)]
    dn = [(r*np.cos(-a), r*np.sin(-a)) for r, a in zip(rs, ang)]
    root_in = [(rr*0.98*np.cos(a), rr*0.98*np.sin(a)) for a in
               np.linspace(-half_p*1.6, half_p*1.6, 8)]
    return root_in + dn + up[::-1]

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

# ---------------- v1.2 station geometry ----------------
# A satellite's center must be ON the drive line (world angle 0) at its strike
# hour. phi = (pos-1)*pitch mod 360, so the month wheel (strikes at pos 30)
# gets station 360 - 29*pitch. Discovered via the interactive model review.
PITCH_DEG = 360.0/31
STN_MONTH = np.deg2rad(360 - 29*PITCH_DEG)      # 23.226 deg

# ---------------- leap train geometry (v1.3, deferred) ----------------
LEAP_ANG  = 4*np.pi/3                       # leap satellite station on program wheel
CAM_ANG   = np.deg2rad(288.0)               # geneva/cam post station
CAM_ORBIT = 26.0
SLIDER_ANG = 5*np.pi/3                      # slider ray (300 deg)
_lp = np.array([SUN_ORBIT*np.cos(LEAP_ANG), SUN_ORBIT*np.sin(LEAP_ANG)])
_cp = np.array([CAM_ORBIT*np.cos(CAM_ANG), CAM_ORBIT*np.sin(CAM_ANG)])
GEN_D   = float(np.linalg.norm(_cp - _lp))  # geneva center distance
GEN_A   = GEN_D*np.sin(np.pi/4)             # driver pin orbit (4-slot geneva)
GEN_B   = GEN_D*np.cos(np.pi/4)             # geneva wheel radius
GEN_PIN = 1.4
GEN_LOCK = 0.62*GEN_A                       # driver locking disc radius
CAM_LO, CAM_HI = 8.0, 11.0                  # cam valley/lobe radii
# slider follower nub: perpendicular offset from cam post to slider ray
_pp = abs(CAM_ORBIT*np.sin(CAM_ANG - SLIDER_ANG))
NUB_RET = CAM_ORBIT*np.cos(CAM_ANG - SLIDER_ANG) + np.sqrt(CAM_LO**2 - _pp**2)
NUB_EXT = CAM_ORBIT*np.cos(CAM_ANG - SLIDER_ANG) + np.sqrt(CAM_HI**2 - _pp**2)
SLIDER_TRAVEL = NUB_EXT - NUB_RET

# ---------------- parts ----------------
def part_base_plate():
    tris = []
    t = P["plate_t"]
    tris += cylinder(0, 0, 58, 0, t, seg=256)
    tris += cylinder(D_DRIVE, 0, 34, 0, t, seg=192)
    tris += box(D_DRIVE/2, 0, D_DRIVE, 62, 0, t)
    ph = P["post_d"]/2
    tris += cylinder(0, 0, ph, t, t + 5.5, seg=64)
    dflat = []
    thd = np.linspace(0, 2*np.pi, 64, endpoint=False)
    for a in thd:
        x, y = ph*np.cos(a), ph*np.sin(a)
        x = min(x, ph - 1.8)
        dflat.append((x, y))
    tris += _poly_prism(dflat, t + 5.5, t + 12.5)
    tris += cylinder(0, 0, ph - 0.8, t + 12.5, t + 17.5, seg=48)
    tris += cylinder(D_DRIVE, 0, ph, t, t + 15.0, seg=64)
    tris += cylinder(D_DRIVE, 0, ph - 0.8, t + 15.0, t + 18.0, seg=48)
    for a in (0.4, 2.5, 4.6):
        tris += cylinder(14*np.cos(a), 14*np.sin(a), 4.0, t, t + 0.9, seg=32)
    tris += box(0, 51.5, 3, 9, 0, t + 2.0)
    ja = np.deg2rad(12*(360/31))
    jr = 62.0
    for off in (-6.0, 6.0):
        px = (jr)*np.cos(ja) - off*np.sin(ja)
        py = (jr)*np.sin(ja) + off*np.cos(ja)
        tris += cylinder(px, py, 2.0, t, t + 5.0, seg=24)
    write_stl("01_base_plate.stl", tris)

def part_program_wheel():
    tris = []
    t = P["wheel_t"]
    prof, _, _, _ = involute_profile(P["prog_teeth"], P["m_drive"], add_f=ADD_F)
    bore = P["post_d"]/2 + P["bore_clr"]
    tris += polar_solid(prof, 0, t, r_inner=bore)
    for k in range(31):
        a = 2*np.pi * k / 31
        h = 2.2 if k == 0 else 1.0
        tris += cylinder(36.5*np.cos(a), 36.5*np.sin(a), 1.1, t, t + h, seg=16)
    post_r = P["sat_post_d"]/2
    cx, cy = SUN_ORBIT*np.cos(STN_MONTH), SUN_ORBIT*np.sin(STN_MONTH)
    z1 = t + 0.5 + 3.0 + 1.2
    tris += cylinder(cx, cy, post_r, t, z1, seg=48)
    tris += cylinder(cx, cy, post_r - 0.6, z1, z1 + 2.5, seg=32)
    tris += cylinder((PROG_ROOT - 2.0)*np.cos(STN_MONTH),
                     (PROG_ROOT - 2.0)*np.sin(STN_MONTH), 1.2, t, t + 1.6, seg=12)
    write_stl("02_program_wheel.stl", tris)

def part_sun_tower():
    """Fixed 7t sun serving LA and LB as one keyed column."""
    tris = []
    h = 0.5 + 3.0
    prof = gear_profile(P["sun_teeth"], SUN_ROOT, SUN_TIP, tooth_frac=0.40, ramp_frac=0.2)
    seg = P["seg"]
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    ph = P["post_d"]/2 + P["bore_clr"]
    xi = np.minimum(ph*np.cos(th), ph - 1.8 + P["bore_clr"])
    yi = ph*np.sin(th)
    tris += _stitch(
        list(np.stack([prof*np.cos(th), prof*np.sin(th)], axis=1)),
        list(np.stack([xi, yi], axis=1)), 0, h)
    write_stl("03_sun_tower.stl", tris)

if __name__ == "__main__":
    print("generating Oechslin v1 parts...")
    part_base_plate()
    part_program_wheel()
    part_sun_tower()
    print("done")
