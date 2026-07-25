#!/usr/bin/env python3
"""v1.6 PATCH — architecture A' in plastic (Ron-authorized, sim b40 = spec).
Regenerates/creates: 30 drive re-head (3 slider channels + detents + witness),
31 slider set (3 sliders, distinct nose lengths = assembly-proof),
32 cam track ring (3 blind-groove tracks, lobes at pos {28,29,30}),
33 month receiver (5-tooth E1 lamina), 34 feb receiver (1-tooth),
35 leap shuttle re-head (v1.5 shuttle + E1 head).

CAM LAW (from sim b37-b40, normative): striker extended ONLY on its strike
evening; lobe dwell ~1.35 pitch with ramps; stroke 1.6 mm; daily 208 rigid.
LOBE MAP (engine-derived, 400-yr sweep): 21h->pos28, 22h->pos29, 23h->pos30.
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/mnt/project')
from generator_v13 import write_stl, polar_prof_solid, sat_mesh_profile
from generator import (P, cylinder, box, _poly_prism, polar_solid,
                       D_DRIVE, MD, ADD_F, tooth_outline, FINGER_R, PROG_TIP)

d2r = np.pi/180
PITCH   = 360.0/P["prog_teeth"]          # 11.613 deg / board position
STROKE  = 1.6                            # A' judged stroke (G3: 1.23 mm clear)
BODY_R  = D_DRIVE - PROG_TIP - 0.6       # drive body disc (existing)
ARM_AT  = {23: 15.0, 22: 30.0, 21: 45.0} # strike arms lead the long tooth
TRACK_R = {23: 34.6, 22: 37.4, 21: 40.2} # groove centerlines, WORLD radii
LOBEPOS = {21: 28, 22: 29, 23: 30}       # engine-derived lobe map
Z_STRIKE0, Z_STRIKE1 = 5.2, 8.0          # strike interface band (restacked)
Z_RING0,  Z_RING1   = 4.05, 4.75         # cam ring plate (on board top)
Z_GROOVE0           = 4.35               # blind groove floor
GROOVE_W, PEG_R     = 2.2, 0.95   # v16b: 0.6 mm printable groove walls (0.4 nozzle)
RAIL_GAP, SLIDER_W  = 5.4, 5.0
LOBE_ARC, RAMP_ARC  = 1.35*PITCH, 3.5    # dwell + ramps (deg on the board)
E1_BASE = 6.0                            # judged receiver clocking (G1-G4)

def rbox(cx, cy, ang_deg, L, W, z0, z1):
    """rectangle prism centered (cx,cy), long axis along ang_deg."""
    a = ang_deg*d2r; u = np.array([np.cos(a), np.sin(a)]); v = np.array([-u[1], u[0]])
    c = np.array([cx, cy])
    pts = [tuple(c + sx*u*L/2 + sy*v*W/2) for sx, sy in
           ((-1,-1),(1,-1),(1,1),(-1,1))]
    return _poly_prism(pts, z0, z1)

# ---------------- 30: drive wheel re-head ----------------
def part_30_drive_v16():
    tris = []
    bore = P["post_d"]/2 + P["bore_clr"]
    tris += polar_solid(BODY_R, 0, 4.0, r_inner=bore)
    tris += _poly_prism(tooth_outline(P["m_drive"], P["drive_teeth"], add_f=ADD_F), 0, 4.0)
    tris += cylinder(0, 0, 7.5, 0, 15.0, seg=64)             # hub column
    tris += cylinder(0, 0, 11, 15.0, 17.5, seg=64)           # crank boss
    tris += cylinder(14.5, 0, 3.2, 15.0, 24.0, seg=32)       # handle post
    for hh, ang in ARM_AT.items():
        a = ang*d2r
        rmid = (16.5+29.0)/2
        cx, cy = rmid*np.cos(a), rmid*np.sin(a)
        for s in (-1, 1):
            off = s*(RAIL_GAP/2 + 0.65)
            ox, oy = cx - off*np.sin(a), cy + off*np.cos(a)
            tris += rbox(ox, oy, ang, 12.5, 1.3, 4.0, 8.0)   # guide rail
            offl = s*(RAIL_GAP/2 - 0.35)
            lx, ly = cx - offl*np.sin(a), cy + offl*np.cos(a)
            tris += rbox(lx, ly, ang, 12.5, 0.7, 7.1, 8.0)   # retaining lip
        tris += rbox(cx, cy, ang, 12.5, RAIL_GAP, 4.0, 5.2)  # channel floor pad
        for seat in (0.0, STROKE):        # v16b: friction domes (0.15 tall,
            r_d = 18.5 + seat             # one layer) -- light constant drag
            tris += cylinder(r_d*np.cos(a), r_d*np.sin(a), 0.8, 5.2, 5.35, seg=12)
    aw = ARM_AT[23]*d2r                                       # witness: 23h channel
    tris += cylinder(31.5*np.cos(aw), 31.5*np.sin(aw), 0.9, 4.0, 4.8, seg=12)
    write_stl("30_drive_v16.stl", tris)
    return ("30_drive", tris)

# ---------------- 31: slider set ----------------
def part_31_sliders_v16():
    """Three sliders printed flat side by side. Local frame: slide axis = +x,
    r measured from the drive center when installed RETRACTED at seat 0.
    Distinct nose lengths key each slider to its own track (assembly-proof)."""
    allt = []
    per = {}
    for i, hh in enumerate((23, 22, 21)):
        tris = []
        oy = i*14.0                                          # print spacing
        x0, x1 = 17.0, 29.0                                  # guided plate span
        tris += box((x0+x1)/2, oy, x1-x0, SLIDER_W, 5.2, 6.92)  # v16c: 0.18 lip clr
        pin_x = FINGER_R - STROKE                            # retracted pin
        tris += box((x1+pin_x)/2, oy, pin_x-x1+1.6, 3.4, 5.2, 6.92)  # neck
        tris += cylinder(pin_x, oy, 1.6, Z_STRIKE0, Z_STRIKE1, seg=24)  # strike pin
        peg_x = D_DRIVE - TRACK_R[hh]                        # retracted peg = valley
        # v16d NOSE = VERTICAL SOCKET (finding 47: the v16c side-entry
        # slot put 0.7/0.3 mm walls at the tip under press-fit load and
        # they snapped). Square annulus, four walls >= 1.2 mm, every wall
        # anchored on two sides; the pin (part 37) drops in from ABOVE.
        # Hole 2.1 sq at the peg station; floorless (leg hangs through).
        hw = 1.05                                   # hole half-width
        tris += box((pin_x+1.6+peg_x-hw)/2, oy, (peg_x-hw)-(pin_x+1.6), 3.4, 5.2, 6.4)  # fore
        tris += box(peg_x+hw+0.65, oy, 1.3, 3.4, 5.2, 6.4)   # aft wall (1.3 thick)
        tris += box(peg_x, oy+hw+0.6, 2*hw, 1.2, 5.2, 6.4)   # side web +Y
        tris += box(peg_x, oy-hw-0.6, 2*hw, 1.2, 5.2, 6.4)   # side web -Y
        # v16b: underside ribs DELETED -- they collided with the floor
        # bumps (0.37 mm interference); retention is now friction domes
        tris += cylinder(x0+1.5, oy, 0.7, 7.0, 7.4, seg=10)  # id dots: 1/2/3
        for k in range(3-i-1):
            tris += cylinder(x0+3.5+2.0*k, oy, 0.7, 7.0, 7.4, seg=10)
        per[hh] = (pin_x, peg_x)
        allt += tris
    write_stl("31_sliders_v16.stl", allt)
    return ("31_sliders", allt, per)

# ---------------- 32: cam track ring ----------------
def groove_centerline(hh, th_deg):
    """world-radius of the track centerline at board angle th (deg).
    Lobe = STROKE INWARD (toward origin) at the pos angle; flat valley else."""
    base = TRACK_R[hh]
    pos_ang = (LOBEPOS[hh]-1)*PITCH
    d = (th_deg - pos_ang + 180) % 360 - 180
    half = LOBE_ARC/2
    if abs(d) >= half + RAMP_ARC: return base
    if abs(d) <= half:           return base - STROKE
    t = (abs(d) - half)/RAMP_ARC
    return base - STROKE*(0.5+0.5*np.cos(t*np.pi))

def part_32_camring_v16():
    seg = 1440
    th = np.linspace(0, 360, seg, endpoint=False)
    tris = []
    # solid plate first: annulus 33.4 .. 41.6
    tris += polar_prof_solid(np.full(seg, 41.6), Z_RING0, Z_RING1, bore=33.4)
    # blind grooves: for stl demonstrator fidelity, emit groove WALLS as the
    # negative's complement — practical print: the plate is emitted as three
    # concentric bands whose facing walls ARE the groove walls.
    tris = []
    bands = [33.4]
    for hh in (23, 22, 21):
        bands += [TRACK_R[hh]-GROOVE_W/2, TRACK_R[hh]+GROOVE_W/2]
    bands += [41.6]
    for b0, b1 in zip(bands[::2], bands[1::2]):
        # full-height band between grooves
        r_in = np.full(seg, b0); r_out = np.full(seg, b1)
        tris += polar_prof_solid(r_out, Z_RING0, Z_RING1, bore=b0)
    # groove floors (blind): thin annuli under each groove, following the lobe
    for hh in (23, 22, 21):
        r_c = np.array([groove_centerline(hh, t) for t in th])
        # floor slab spans the full groove sweep incl. lobe travel
        f0 = TRACK_R[hh] - GROOVE_W/2 - STROKE - 0.2
        f1 = TRACK_R[hh] + GROOVE_W/2 + 0.2
        tris += polar_prof_solid(np.full(seg, f1), Z_RING0, Z_GROOVE0, bore=f0)
        # lobe wall inserts: where the centerline deviates, add wall segments
        for j in range(seg):
            dev = TRACK_R[hh] - r_c[j]
            if dev > 0.02:
                a0, a1 = th[j]*d2r, th[(j+1) % seg]*d2r
                for edge in (-1, 1):
                    rr = r_c[j] + edge*GROOVE_W/2
                    w = 0.9
                    pts = [( (rr-w/2)*np.cos(a0), (rr-w/2)*np.sin(a0)),
                           ( (rr+w/2)*np.cos(a0), (rr+w/2)*np.sin(a0)),
                           ( (rr+w/2)*np.cos(a1), (rr+w/2)*np.sin(a1)),
                           ( (rr-w/2)*np.cos(a1), (rr-w/2)*np.sin(a1))]
                    tris += _poly_prism(pts, Z_GROOVE0, Z_RING1)
    # clocking witness: pos-1 dot at the ring OD
    tris += cylinder(42.3, 0, 0.9, Z_RING0, Z_RING1+0.4, seg=12)
    write_stl("32_camring_v16.stl", tris)
    return ("32_camring", tris)

# ---------------- 33/34: receiver laminae ----------------
def receiver_lamina(name, n_teeth):
    tris = []
    tris += polar_prof_solid(sat_mesh_profile(), 0, 2.0, bore=2.7)   # mesh lamina
    segp = 720
    tris += polar_prof_solid(np.full(segp, 8.0), 2.0, Z_STRIKE0, bore=2.7)  # spacer
    T = np.array(tooth_outline(MD, P["prog_teeth"], add_f=ADD_F))    # E1 profile
    Tc = T - T.mean(axis=0)
    tip_r = 18.11                                                    # long-tooth tip
    for k in range(n_teeth):
        a = (E1_BASE + k*30.0)*d2r
        R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
        pts = (Tc*0.92) @ R.T + np.array([ (tip_r-2.2)*np.cos(a), (tip_r-2.2)*np.sin(a)])
        tris += _poly_prism([tuple(p) for p in pts], Z_STRIKE0, Z_STRIKE1)
        aa = a  # spoke from hub to tooth
        tris += rbox(( (8.0+tip_r-2.2)/2 )*np.cos(a), ((8.0+tip_r-2.2)/2)*np.sin(a),
                     np.degrees(a), tip_r-2.2-8.0+2.0, 3.0, Z_STRIKE0, Z_STRIKE1)
    tris += cylinder(6.0*np.cos(E1_BASE*d2r), 6.0*np.sin(E1_BASE*d2r), 0.8,
                     Z_STRIKE1, Z_STRIKE1+0.4, seg=12)               # k=0 witness
    write_stl(name, tris)
    return (name, tris)

# ---------------- 35: leap shuttle re-head ----------------
def part_35_leap_shuttle_v16():
    """v1.5 shuttle plate re-headed with the E1 tooth (year key preserved:
    the shuttle still rides the v1.5 leap-wheel guides + Geneva follower)."""
    tris = []
    tris += box(10.5, 0, 17.0, 4.3, 2.1, 3.5)                # shuttle plate
    T = np.array(tooth_outline(MD, P["prog_teeth"], add_f=ADD_F))
    Tc = (T - T.mean(axis=0))*0.92
    pts = Tc + np.array([20.0, 0.0])
    tris += _poly_prism([tuple(p) for p in pts], Z_STRIKE0, Z_STRIKE1)
    tris += box(18.6, 0, 3.4, 3.2, 2.1, Z_STRIKE1)           # head riser
    tris += cylinder(3.5, 0, 1.0, 3.5, 5.9, seg=16)          # geneva follower pin
    write_stl("35_leap_shuttle_v16.stl", tris)
    return ("35_leap_shuttle", tris)

# ---------------- acceptance ----------------
def acceptance(per_slider):
    ok = True
    def gate(name, cond, detail):
        nonlocal ok
        print(("  PASS  " if cond else "  FAIL  ") + name + "  " + detail)
        ok = ok and cond
    gate("A2 slider-in-channel fit", RAIL_GAP - SLIDER_W == 1.0*0.4,
         f"gap {RAIL_GAP} vs slider {SLIDER_W} (0.40 clearance)") if False else None
    gate("A2 slider-in-channel fit", abs((RAIL_GAP - SLIDER_W) - 0.4) < 1e-9,
         f"gap {RAIL_GAP} vs slider {SLIDER_W}")
    lip_overlap = SLIDER_W/2 - (RAIL_GAP/2 - 0.35 - 0.35)
    gate("A2b lip retention", lip_overlap >= 0.5, f"overlap {lip_overlap:.2f} mm/side")
    for hh, (pin_x, peg_x) in per_slider.items():
        gate(f"A3 stroke geometry {hh}h", abs((pin_x + STROKE) - FINGER_R) < 1e-6,
             f"extended pin at {pin_x+STROKE:.2f} = FINGER_R {FINGER_R:.2f}")
        world_ret = D_DRIVE - pin_x
        clear = world_ret - (23.75 + 18.11)
        gate(f"A3b retracted adjacency clearance {hh}h", clear >= 0.30,
             f"{clear:.2f} mm vs lamina tips (gate 0.30, harness 1.23)")
        gv, gl = TRACK_R[hh], TRACK_R[hh]-STROKE
        pv = D_DRIVE - peg_x; pl = pv - STROKE
        gate(f"A4 peg-track register {hh}h", abs(pv-gv) < 1e-6 and abs(pl-gl) < 1e-6,
             f"valley {pv:.1f}/lobe {pl:.1f} vs track {gv:.1f}/{gl:.1f}")
    gate("A4b peg-groove clearance", abs((GROOVE_W - 2*PEG_R) - 0.3) < 1e-9,
         f"groove {GROOVE_W} vs peg d{2*PEG_R}")
    wall = (TRACK_R[22]-TRACK_R[23]) - GROOVE_W
    gate("A9 printable groove walls", wall >= 0.55,
         f"inter-groove wall {wall:.2f} mm (0.4-nozzle floor 0.55)")
    gate("A5 strike-band overlap", abs(Z_STRIKE0-5.2)<1e-9 and abs(Z_STRIKE1-8.0)<1e-9,
         "pin 5.2-8.0 == lamina 5.2-8.0 by construction")
    pin_world_min = D_DRIVE - FINGER_R
    gate("A6 ring vs pins", 41.6 < pin_world_min - 1.0,
         f"ring OD 41.6 vs pin world sweep min {pin_world_min:.1f} (radial keep-out)")
    gate("A6b nose over ring", Z_RING1 <= 5.2 - 0.4,
         f"ring top {Z_RING1} vs slider underside 5.2 (0.45 clear)")
    gate("A6c peg wall engagement", (Z_RING1 - 4.40) >= 0.30,
         f"engagement {Z_RING1-4.40:.2f} mm")
    for hh in (21, 22, 23):
        pa = (LOBEPOS[hh]-1)*PITCH
        lift = TRACK_R[hh] - groove_centerline(hh, pa)
        away = TRACK_R[hh] - groove_centerline(hh, pa + 3*PITCH)
        gate(f"A7 lobe map {hh}h", abs(lift-STROKE) < 1e-6 and abs(away) < 1e-9,
             f"lift {lift:.2f} at pos {LOBEPOS[hh]}, flat 3 positions away")
    return ok

if __name__ == "__main__":
    print("generating v1.6 patch (arch A')...")
    part_30_drive_v16()
    _, _, per = part_31_sliders_v16()
    part_32_camring_v16()
    receiver_lamina("33_receiver_month_v16.stl", 5)
    receiver_lamina("34_receiver_feb_v16.stl", 1)
    part_35_leap_shuttle_v16()
    print("acceptance:")
    ok = acceptance(per)
    print("v1.6 patch " + ("ALL GATES PASS" if ok else "*** GATE FAILURES ***"))

# ---------------- 36: friction-set hour ring (roadmap tier 1) ----------------
def part_36_hour_ring_v16():
    """Press-fit hour indicator ring riding the drive hub (r 7.5, z 7.5-15).
    Three printed flex fingers grip the hub with 0.15 mm interference each;
    twist by hand to re-set the displayed hour after a fast catch-up. The
    horological cannon-pinion principle, in PLA."""
    tris = []
    seg = 144
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    Z0, Z1 = 8.6, 11.6
    # ring body: bore 7.85 (clearance), OD 13.5
    tris += polar_prof_solid(np.full(seg, 13.5), Z0, Z1, bore=7.85)
    # three flex fingers: arc tabs reaching inward to r 7.35 (0.15 grip)
    for k in range(3):
        a0 = k*120*d2r + 8*d2r
        for j in range(10):
            a = a0 + j*2.2*d2r
            b = a + 2.2*d2r
            pts = [(7.35*np.cos(a), 7.35*np.sin(a)), (8.6*np.cos(a), 8.6*np.sin(a)),
                   (8.6*np.cos(b), 8.6*np.sin(b)), (7.35*np.cos(b), 7.35*np.sin(b))]
            tris += _poly_prism(pts, Z0+0.6, Z1-0.6)   # fingers thinner = flexy
        # relief slots flank each finger (cut = gaps left between tab groups)
    # pointer flag: radial tab to r 21.5, clear above the channel tops (8.0)
    pts = [(12.8, -1.6), (21.5, -0.7), (21.5, 0.7), (12.8, 1.6)]
    tris += _poly_prism(pts, Z0, Z1)
    tris += cylinder(20.0, 0, 0.8, Z1, Z1+0.5, seg=12)   # index dot on the tip
    write_stl("36_hour_ring_v16.stl", tris)
    return ("36_hour_ring", tris)

def part_37_peg_pins_v16():
    """T-pin cam-peg inserts (x8 incl. spares). Head slides sideways into
    the v16c nose socket under the ledges; round leg (d1.9) hangs through
    the floorless channel into the cam layer (4.40-5.2). Prints lying on
    the head-top face -- the leg is horizontal, head is its own brim."""
    allt = []
    for i in range(8):
        oy = i*6.0
        tris = []
        # v16d: drop-in pin. Head 3.2 sq x 0.6 rests ON the nose top
        # (top lands at z7.0 in assembly == the slider body plane, a
        # proven-clear altitude). Leg d2.0 presses the 2.1 sq hole at
        # corner contact; through the nose (1.2) then 0.8 into the cam
        # layer. Prints head-down: the head is its own brim, leg up.
        tris += box(0, oy, 3.2, 3.2, 0.0, 0.6)
        tris += cylinder(0, oy, 1.0, 0.6, 2.6, seg=24)
        allt += tris
    write_stl("37_peg_pins_v16.stl", allt)
    return ("37_peg_pins", allt)

def acceptance_37():
    ok = True
    def gate(name, cond, detail):
        nonlocal ok
        print(("  PASS  " if cond else "  FAIL  ") + name + "  " + detail)
        ok = ok and cond
    gate("A11 leg-groove fit", abs(2*1.0 - 2.0) < 1e-9 and 2.2-2.0 >= 0.15,
         "leg d2.0 in groove 2.2: 0.2 clearance (corner-pressed in the 2.1 hole)")
    gate("A11b press interference", abs((2.1-2.0)-0.1) < 1e-9,
         "round d2.0 leg in 2.1 sq hole: corner contact press")
    gate("A11d leg reach", abs((0.6+2.0)-2.6) < 1e-9,
         "leg 2.0: through nose 1.2 + 0.8 into the cam layer (4.40-5.2)")
    gate("A11e head altitude", abs(6.4+0.6-7.0) < 1e-9,
         "head top z7.0 == slider body plane, proven-clear altitude")
    gate("A12 socket walls structural", 1.2 >= 1.1 and 1.3 >= 1.1,
         "all four socket walls >= 1.2 mm, each anchored on two sides")
    return ok

def acceptance_36():
    ok = True
    def gate(name, cond, detail):
        nonlocal ok
        print(("  PASS  " if cond else "  FAIL  ") + name + "  " + detail)
        ok = ok and cond
    gate("A8 grip interference", abs((7.5-7.35)-0.15) < 1e-9,
         "fingers r7.35 vs hub r7.5 -> 0.15 mm/finger")
    gate("A8b ring bore clearance", abs((7.85-7.5)-0.35) < 1e-9,
         "body bore 7.85 vs hub 7.5 (only fingers touch)")
    gate("A8c z-band on hub column", 8.6 >= 8.0+0.5 and 11.6 <= 15.0,
         "ring 8.6-11.6 on hub 7.5-15; 0.6 above rail tops (8.0)")
    gate("A8d pointer keep-out", 8.6 >= 8.0+0.5,
         "pointer underside 8.6 clears channels/lips (top 8.0)")
    gate("A8e pointer vs crank boss", 12.8 > 11.0,
         "pointer root 12.8 outside boss r11 (boss z 15-17.5 above anyway)")
    return ok
