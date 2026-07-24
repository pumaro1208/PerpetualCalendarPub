#!/usr/bin/env python3
"""v1.5.1 PATCH (rev B) — audit-driven corrections, 2026-07-07 pass.
Regenerates: 01 base, 07 follower, 11 cap_main, 17 bridge, 23 programmer,
24 century, 25 platform, 26 idler, 28 shaft.

FIXED:
 F1  east bridge post off the weekday-pin orbit: (60,-22)->(60,-34); base
     support lobe added; bridge east boss on a south tab; the continuous TOP
     RAIL terminates at local x 84.0 (pin orbit crosses it at 86.1..88.0).
 F3  annual Geneva rebuilt textbook (C 43.55, R 30.8): the receiver is a HUB
     on a coaxial TUBE integral with the programmer, carrying four twin-rail
     slotted spokes (continuous 2.6 mm slot from r11.4 to the rim), raised
     jaws at the mouths, and a stiffening hoop ABOVE the pin's top. Slot
     length 22.0 mm >= required 18.05. Riser-column concept abandoned (any
     column crosses the century ring's swept annulus).
 F4  annual shaft bored 4.4 deep (stud 4.2).
 F5  Gregorian z-stack re-datumed TOP-relative; platform deck seats on the
     sun-tower top (29.0). Band table verified closed (see acceptance).
 F6  bridge bosses bored r3.35.
 F7  idler TOP witness dot; I2 installs INVERTED (README).
 F2* century auto-advance removed (coaxial pin cannot index a coaxial ring —
     the same impossibility as the abandoned satellite-pin annual drive).
     Century ring is MANUAL-SET alpha: bore 6.55 riding the programmer tube
     (ring-on-ring, the proven year-stack bearing), friction-held by the
     platform leaf, 100 ticks + century labels, OD knurls. Lobes unchanged in
     function, now in their OWN band (32.6..33.6) below the body — they and
     the cam are vertically superimposed radial cams; the follower foot reads
     the max, as designed. Auto-advance proposal in the report.
OPEN (design session, NOT patched): F8 — display-bay vertical budget and the
rotating pin-ring keep-out annulus (r26.7..32.1 from origin). See report.
ASSEMBLY CLOCKING (new dots): shaft-arm dot aligns to the programmer's slot-0
jaw at the parked position (standard Geneva entry clocking).
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generator_v13 import (write_stl, polar_prof_solid, dflat_profile, TOP,
                           POST_R)
from generator import (P, cylinder, box, _poly_prism, polar_solid, _stitch,
                       D_DRIVE, MD)
from glyphs import G as GLYPHS

# ---------- Gregorian z-stack, TOP-relative (F5); all values ABSOLUTE ----------
DECK0, DECK1 = TOP, TOP+1.6            # 29.0..30.6 platform deck
RING0, RING1 = DECK1, DECK1+1.8        # 30.6..32.4 programmer body
CAM0         = RING1-1.0               # cam read band 31.4..32.4
TUBE1        = RING1+5.0               # programmer tube top 37.4
LOBE0, LOBE1 = RING1+0.2, RING1+1.2    # century lobe band 32.6..33.6
CENT0, CENT1 = LOBE1, LOBE1+1.0        # century body 33.6..34.6 (features to 35.2)
ARM0,  ARM1  = CENT1+1.0, CENT1+2.4    # shaft arm 35.6..37.0
RAIL0, RAIL1 = TUBE1, TUBE1+1.6        # rails 37.4..39.0
JAW1         = RAIL1+1.4               # jaw tops 40.4
PIN1         = JAW1-0.4                # geneva pin top 40.0
HOOP0, HOOP1 = JAW1, JAW1+1.2          # hoop 40.4..41.6
SPIG1        = RAIL1                   # post spigot to 39.0
R_LONG, R_SHORT = 12.9, 11.3
TUBE_RI, TUBE_RO = 5.6, 6.4
CENT_BORE, CENT_OD = 6.55, 15.1
SLOT_HW, SLOT_IN = 1.3, 11.4
C_GEN = float(np.hypot(10.35, 42.3))   # 43.55
R_GEN = 30.8
SHAFT = (10.35, -42.3)

def _ticks(tris, r0, r1, n, z0, z1, w=0.35):
    for k in range(n):
        a = 2*np.pi*k/n
        ux, uy = np.cos(a), np.sin(a); px, py = -uy, ux
        tris += _poly_prism([(r0*ux+w/2*px, r0*uy+w/2*py),
                             (r1*ux+w/2*px, r1*uy+w/2*py),
                             (r1*ux-w/2*px, r1*uy-w/2*py),
                             (r0*ux-w/2*px, r0*uy-w/2*py)], z0, z1)

def _emboss(tris, txt, r_mid, h, ang, z0, z1, stroke=0.5):
    wg = h*0.62; total = len(txt)*wg*1.25
    for i, ch in enumerate(txt):
        if ch not in GLYPHS: continue
        xoff = -total/2 + i*wg*1.25
        for (x1, y1, x2, y2) in GLYPHS[ch]:
            pts = []
            for gx, gy in ((x1, y1), (x2, y2)):
                t_ = xoff + gx*wg
                rr = r_mid - h/2 + gy*h
                a = ang - t_/r_mid
                pts.append((rr*np.cos(a), rr*np.sin(a)))
            (xa, ya), (xb, yb) = pts
            dx, dy = xb-xa, yb-ya; L = max((dx*dx+dy*dy)**.5, 1e-6)
            nx, ny = -dy/L*stroke/2, dx/L*stroke/2
            ex, ey = dx/L*stroke/2, dy/L*stroke/2
            tris += _poly_prism([(xa-nx-ex, ya-ny-ey), (xb-nx+ex, yb-ny+ey),
                                 (xb+nx+ex, yb+ny+ey), (xa+nx-ex, ya+ny-ey)], z0, z1)

# ================= 01 base plate (F1, spigot extension) =================
def part_base_v151():
    t = 4.0; tris = []
    tris += cylinder(0, 0, 58, 0, t, seg=256)
    tris += cylinder(D_DRIVE, 0, 34, 0, t, seg=192)
    tris += box(D_DRIVE/2, 0, D_DRIVE, 62, 0, t)
    tris += cylinder(0, 0, POST_R, t, 8.5, seg=64)
    tris += _poly_prism(dflat_profile(POST_R, 1.8), 8.5, TOP + 4.6)
    tris += cylinder(0, 0, 3.1, TOP + 4.6, SPIG1, seg=48)      # spigot to 39.0
    tris += cylinder(D_DRIVE, 0, POST_R, t, TOP + 1.0, seg=64)
    tris += cylinder(D_DRIVE, 0, POST_R - 0.9, TOP + 1.0, TOP + 3.5, seg=48)
    for a in (0.4, 2.5, 4.6):
        tris += cylinder(14*np.cos(a), 14*np.sin(a), 4.0, t, t + 3.9, seg=32)
    tris += box(0, 51.5, 3, 9, 0, t + 2.0)
    for sx_, sy_, sr in ((-29.75, -22, 2.2), (-9.59, -22, 2.2),
                          (D_DRIVE-20.42, -22, 2.2), (13.4, -22, 2.2)):
        tris += cylinder(sx_, sy_, sr, t, t + 3.4, seg=32)
        tris += cylinder(sx_, sy_, sr - 0.8, t + 3.4, t + 5.2, seg=24)
    for ix_, iy_ in ((-9.59, -33.0), (0.38, -37.65)):
        tris += cylinder(ix_, iy_, 2.2, t, t + 3.4, seg=32)
        tris += cylinder(ix_, iy_, 1.4, t + 3.4, t + 5.2, seg=24)
    tris += cylinder(*SHAFT, 2.4, t, t + 4.2, seg=32)
    tris += cylinder(-44.0, -22, 3.0, t, t + 5.6, seg=32)      # west post
    tris += cylinder( 60.0, -34, 3.0, t, t + 5.6, seg=32)      # east post MOVED (F1)
    tris += cylinder(60.0, -34, 7.0, 0, t, seg=48)             # base support lobe
    tris += box(63.0, -29.5, 14.0, 12.0, 0, t)                 # blend to drive disc
    ja = np.deg2rad(12*(360/31)); jr = 62.0
    for off in (-6.0, 6.0):
        px = jr*np.cos(ja) - off*np.sin(ja)
        py = jr*np.sin(ja) + off*np.cos(ja)
        tris += cylinder(px, py, 2.0, t, t + 8.0, seg=24)
    write_stl("01_base_plate.stl", tris)

# ================= 11 cap_main (retainer above the rails hub) =================
def part_cap_main_v151():
    seg = 96; th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    op = [(6.8*np.cos(a), 6.8*np.sin(a)) for a in th]
    ip = [(3.18*np.cos(a), 3.18*np.sin(a)) for a in th]
    write_stl("11_cap_main.stl", _stitch(op, ip, 0, 2.4))

# ================= 17 rail bridge (F1, F6) =================
def part_rail_bridge_v151():
    """local x from the date stud: hubs 0 / 20.16 / 43.15 / 82.83.
    F6: bosses bored r3.35. F1: east boss on a south tab at local (89.75,-12);
    top rail ends at local 84.0 (weekday pin orbit crosses 86.1..88.0)."""
    tris = []
    t0, t1 = 0, 2.2
    hubs = [0.0, 20.16, 43.15, 82.83]
    wins = [(1.8, 13.4), (22.66, 30.16), (45.35, 58.75), (85.33, 94.03)]
    xs = [-46] + [w for p in wins for w in p] + [92]
    for i in range(0, len(xs)-1, 2):
        xa, xb = xs[i], xs[i+1]
        tris += box((xa+xb)/2, 0, xb-xa, 12, t0, t1)
    tris += box(19.0, 5.2, 130.0, 1.8, t0, t1)   # top rail -46..84.0 ONLY (F1)
    tris += box(23.0, -5.2, 138.0, 1.8, t0, t1)  # bottom rail full (orbit can't reach)
    seg = 96; th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    def bored_boss(bx, by):
        op = [(bx+4.2*np.cos(a), by+4.2*np.sin(a)) for a in th]
        ip = [(bx+3.35*np.cos(a), by+3.35*np.sin(a)) for a in th]
        return _stitch(op, ip, t0, t1+2.0)
    tris += bored_boss(-14.25, 0.0)
    tris += bored_boss(89.75, -12.0)
    tris += box(88.6, -8.55, 7.0, 6.9, t0, t1)   # south tab bar->boss
    for h in hubs:
        tris += box(h, -8.6, 1.2, 7.0, t0, t1)
        tris += box(h, -12.6, 3.4, 2.4, t0, t1)
    write_stl("17_rail_bridge.stl", tris)

# ================= 25 platform (F5, century sleeve removed) =================
def part_platform_v151():
    """LOCAL z, print flat; seats on the sun-tower top. Deck 0..1.6, programmer
    sleeve 1.6..3.4. Century sleeve DELETED (century rides the programmer tube).
    Century friction leaf raised to press the century OD at abs 33.6..34.6."""
    tris = []
    seg = 192; th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    dfl = dflat_profile(POST_R+0.15, 1.8-0.15, seg)
    tris += _stitch([(9.2*np.cos(a), 9.2*np.sin(a)) for a in th], dfl, 0, 1.6)
    tris += _stitch([(5.3*np.cos(a), 5.3*np.sin(a)) for a in th], dfl, 1.6, 3.4)
    tris += box(-7.6, 6.5, 6.0, 1.1, 1.6, 3.2)   # programmer detent leaf (watershed)
    tris += box(-10.2, 6.5, 1.4, 2.6, 1.6, 3.2)
    tris += box(-6.2, -7.4, 5.2, 1.1, 4.6, 5.8)  # century friction leaf, raised
    tris += box(-8.4, -7.4, 1.3, 2.4, 1.6, 5.8)  # its riser post from the deck
    write_stl("25_platform.stl", tris)

# ================= 23 programmer ring (F3 tube architecture, F2*) =================
def part_programmer_ring_v151():
    """LOCAL z0 = RING0 (abs 30.6). Body 0..1.8 with cam band in the top 1.0
    (faces 11.3/12.9, short notch +-38 deg at ring-0). Coaxial TUBE r5.6..6.4
    rises 1.8..6.8 (abs 32.4..37.4); the century ring bears on its OD. Rails
    HUB at 6.8..8.4: solid annulus 5.6..9.4, solid yoke to r11.4, then four
    twin-rail spokes (slot half-width 1.3) out to r33.4; jaws 8.4..9.8 at the
    mouths (r28.2..33.4); stiffening hoop r33.8..34.6 at 9.8..11.0, ABOVE the
    pin top. Century takeoff pin REMOVED (F2). Slot-0 carries the clocking
    witness notch on its jaw."""
    tris = []
    seg = 1440; th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    zb1 = RING1-RING0; zc0 = CAM0-RING0                # body 0..1.8, cam 0.8..1.8
    zt1 = TUBE1-RING0                                  # tube to 6.8
    zr0, zr1 = RAIL0-RING0, RAIL1-RING0                # rails 6.8..8.4
    zj1 = JAW1-RING0                                   # jaws to 9.8
    zh0, zh1 = HOOP0-RING0, HOOP1-RING0                # hoop 9.8..11.0
    tris += polar_solid(R_SHORT-0.4, 0, zc0, r_inner=5.45)
    r = np.full(seg, R_LONG)
    m = np.abs(np.angle(np.exp(1j*th))) < np.deg2rad(38)
    r[m] = R_SHORT
    op = [(rr*np.cos(t), rr*np.sin(t)) for rr, t in zip(r, th)]
    ip = [(5.45*np.cos(t), 5.45*np.sin(t)) for t in th]
    tris += _stitch(op, ip, zc0, zb1)
    for k in range(4):                                 # detent bumps (watershed)
        a = np.deg2rad(45+90*k)
        tris += cylinder((R_SHORT-0.4)*np.cos(a), (R_SHORT-0.4)*np.sin(a), 0.7,
                         0, zc0, seg=12)
    th2 = np.linspace(0, 2*np.pi, 128, endpoint=False)
    tris += _stitch([(TUBE_RO*np.cos(a), TUBE_RO*np.sin(a)) for a in th2],
                    [(TUBE_RI*np.cos(a), TUBE_RI*np.sin(a)) for a in th2],
                    zb1, zt1)                          # the TUBE
    tris += _stitch([(9.4*np.cos(a), 9.4*np.sin(a)) for a in th2],
                    [(TUBE_RI*np.cos(a), TUBE_RI*np.sin(a)) for a in th2],
                    zr0, zr1)                          # rails hub
    for k in range(4):
        a2 = np.deg2rad(45+90*k)
        ux, uy = np.cos(a2), np.sin(a2); px, py = -uy, ux
        yoke = [(9.0*ux+3.1*px, 9.0*uy+3.1*py), (SLOT_IN*ux+3.1*px, SLOT_IN*uy+3.1*py),
                (SLOT_IN*ux-3.1*px, SLOT_IN*uy-3.1*py), (9.0*ux-3.1*px, 9.0*uy-3.1*py)]
        tris += _poly_prism(yoke, zr0, zr1)            # solid yoke to the slot floor
        for sd in (-1, 1):
            e0, e1 = SLOT_HW, SLOT_HW+1.8
            rail = [(SLOT_IN*ux+sd*e0*px, SLOT_IN*uy+sd*e0*py),
                    ((R_GEN+2.6)*ux+sd*e0*px, (R_GEN+2.6)*uy+sd*e0*py),
                    ((R_GEN+2.6)*ux+sd*e1*px, (R_GEN+2.6)*uy+sd*e1*py),
                    (SLOT_IN*ux+sd*e1*px, SLOT_IN*uy+sd*e1*py)]
            tris += _poly_prism(rail, zr0, zr1)
            jaw = [((R_GEN-2.6)*ux+sd*e0*px, (R_GEN-2.6)*uy+sd*e0*py),
                   ((R_GEN+2.6)*ux+sd*e0*px, (R_GEN+2.6)*uy+sd*e0*py),
                   ((R_GEN+2.6)*ux+sd*e1*px, (R_GEN+2.6)*uy+sd*e1*py),
                   ((R_GEN-2.6)*ux+sd*e1*px, (R_GEN-2.6)*uy+sd*e1*py)]
            tris += _poly_prism(jaw, zr1, zj1)
    hp = np.linspace(0, 2*np.pi, 256, endpoint=False)
    tris += _stitch([(34.6*np.cos(a), 34.6*np.sin(a)) for a in hp],
                    [(33.8*np.cos(a), 33.8*np.sin(a)) for a in hp],
                    zh0, zh1)                          # hoop above the pin top
    a0 = np.deg2rad(45)                                # clocking witness on slot-0 jaw
    tris += cylinder(32.4*np.cos(a0)+2.9*np.sin(a0), 32.4*np.sin(a0)-2.9*np.cos(a0),
                     0.8, zj1, zj1+0.6, seg=12)
    write_stl("23_programmer_ring.stl", tris)

# ================= 24 century ring (F2 manual-set alpha) =================
def part_century_ring_v151():
    """LOCAL z0 = LOBE0 (abs 32.6): lobe band 0..1.0, body 1.0..2.0, features
    2.0..2.6. Bore 6.55 riding the programmer tube OD 6.4. Lobes at stations
    25/50/75 (r11.6..12.9) in their OWN band under the body — the follower
    foot spans cam band + lobe band and reads the max. Manual-set: platform
    leaf friction on the knurled OD; 100 ticks; labels 24/21/22/23."""
    tris = []
    zl1 = LOBE1-LOBE0; zb1 = CENT1-LOBE0
    tris += polar_solid(CENT_OD, zl1, zb1, r_inner=CENT_BORE)
    for st in (25, 50, 75):                            # masking lobes, own band
        a0 = 2*np.pi*st/100
        arc = [(R_LONG*np.cos(t), R_LONG*np.sin(t))
               for t in np.linspace(a0-0.032, a0+0.032, 10)]
        arc += [((R_LONG-1.3)*np.cos(t), (R_LONG-1.3)*np.sin(t))
                for t in np.linspace(a0+0.032, a0-0.032, 10)]
        tris += _poly_prism(arc, 0, zl1)
    _ticks(tris, R_LONG+0.4, R_LONG+1.9, 100, zb1, zb1+0.5)
    for st, lab in ((0, "24"), (25, "21"), (50, "22"), (75, "23")):
        _emboss(tris, lab, 9.6, 1.9, 2*np.pi*st/100, zb1, zb1+0.6)
    for k in range(40):
        a = 2*np.pi*(k+0.5)/40
        tris += cylinder(CENT_OD*np.cos(a), CENT_OD*np.sin(a), 0.45, zl1, zb1, seg=8)
    write_stl("24_century_ring.stl", tris)

# ================= 26 annual idler (F7) =================
def part_annual_idler_v151():
    tris = []
    seg = 1080; th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    r = np.full(seg, 6.4)
    for k in range(10):
        d = np.abs(np.angle(np.exp(1j*(th-2*np.pi*k/10))))*6.4
        m = d < 1.3
        r[m] = np.minimum(r[m], 6.4-np.sqrt(np.maximum(1.3**2-d[m]**2, 0)))
    tris += polar_prof_solid(r, 0, 1.5, bore=2.5)
    for k in range(10):
        a2 = 2*np.pi*(k+0.5)/10
        tris += cylinder(5.5*np.cos(a2), 5.5*np.sin(a2), 0.8, 1.5, 3.3, seg=12)
    tris += cylinder(4.0, 0, 0.8, 3.3, 3.9, seg=12)    # F7 TOP witness dot (peg side)
    write_stl("26_annual_idler.stl", tris)

# ================= 28 annual shaft (F3, F4) =================
def part_annual_shaft_v151():
    """PRINT LYING DOWN; assembly z0 = base top (4.0). Star 0..1.5 bored r2.5,
    bore continues to 4.4 (stud 4.2, F4). Arm at abs 35.6..37.0; pin root
    confined to the arm band; pin r1.05 rises to abs 40.0 (under the hoop);
    clocking dot on the arm top."""
    tris = []
    A0, A1 = ARM0-4.0, ARM1-4.0                       # local 31.6..33.0
    Ptop   = PIN1-4.0                                  # local 36.0
    seg = 720; th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    r = np.full(seg, 6.4)
    for k in range(10):
        d = np.abs(np.angle(np.exp(1j*(th-2*np.pi*k/10))))*6.4
        m = d < 1.3
        r[m] = np.minimum(r[m], 6.4-np.sqrt(np.maximum(1.3**2-d[m]**2, 0)))
    tris += _stitch([(rr*np.cos(t), rr*np.sin(t)) for rr, t in zip(r, th)],
                    [(2.5*np.cos(t), 2.5*np.sin(t)) for t in th], 0, 1.5)
    th2 = np.linspace(0, 2*np.pi, 64, endpoint=False)
    tris += _stitch([(3.2*np.cos(t), 3.2*np.sin(t)) for t in th2],
                    [(2.5*np.cos(t), 2.5*np.sin(t)) for t in th2], 1.5, 4.4)  # F4
    tris += cylinder(0, 0, 3.2, 4.4, A1, seg=64)
    tris += box(15.4, 0, 30.8, 4.4, A0, A1)
    tris += cylinder(30.8, 0, 1.9, A0, A1, seg=18)     # root inside the arm band
    tris += cylinder(30.8, 0, 1.05, A1, Ptop, seg=18)  # pin into the slot band
    tris += cylinder(26.0, 0, 0.8, A1, A1+0.6, seg=12) # clocking dot on the arm
    write_stl("28_annual_shaft.stl", tris)

# ================= 07 follower shuttle (F5 rebase) =================
def part_follower_shuttle_v151():
    """post spans abs 28.7..33.3: reads the cam band (31.4..32.4) and the lobe
    band (32.6..33.3), 0.3 under the century body."""
    tris = []
    t = 1.7
    for s in (-1, 1):
        tris += box(2.6, s*4.0, 27.0, 1.2, 0, t)
    tris += box(-9.6, 0, 2.6, 9.2, 0, t)
    tris += box(15.4, 0, 2.6, 9.2, 0, t)
    nose = [(16.4, -1.9), (17.91, -0.95), (18.11, 0.55), (16.4, 1.9)]
    tris += _poly_prism(nose, 0, t)
    tris += cylinder(-10.4, 0, 1.3, t, t+2.4, seg=20)
    tris += cylinder(-10.4, 0, 1.0, t, t+4.6, seg=20)  # tip abs 33.3
    write_stl("07_follower_shuttle.stl", tris)

if __name__ == "__main__":
    print("generating v1.5.1 rev B parts...")
    part_base_v151(); part_cap_main_v151(); part_rail_bridge_v151()
    part_platform_v151(); part_programmer_ring_v151(); part_century_ring_v151()
    part_annual_idler_v151(); part_annual_shaft_v151(); part_follower_shuttle_v151()
    print(f"\nabs bands: ring {RING0}-{RING1} | cam {CAM0}-{RING1} | lobes "
          f"{LOBE0}-{LOBE1} | century {CENT0}-{CENT1} | arm {ARM0}-{ARM1} | "
          f"rails {RAIL0}-{RAIL1} | jaws->{JAW1} | pin->{PIN1} | hoop {HOOP0}-{HOOP1}")
    print("v1.5.1 rev B done")
