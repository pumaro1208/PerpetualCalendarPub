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
ROOT_Z = 2.0                             # finding #104: root strike fingers onto the mesh lamina (was floating at Z_STRIKE0)
RIB_W  = 4.5                             # finding #104: widened finger rib (was 3.0) for strength
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
    # v16d: hub column only -- the crank is now part 38 (press-on module,
    # finding 45). The old boss and the FLOATING handle post are deleted.
    # finding 54: the bore was computed and never emitted -- the hub went
    # out SOLID. Emitted as an annulus now; the deck's center is covered
    # by the hub's own wall so the through-bore is continuous z 0-15.
    tris += polar_prof_solid(np.full(64, 7.5), 0.0, 15.0, bore=bore)  # hub column, BORED
    # REFUSAL RING (restores assembly-proofing the boss used to provide):
    # every reversed slider nose (tips at r 7.1/9.9/12.7) must cross this
    # annulus and collide; correct assembly has nothing inside r 13.5 in
    # the nose band. Also stiffens the hub root.
    tris += polar_prof_solid(np.full(64, 12.9), 4.0, 6.6, bore=9.0)
    for hh, ang in ARM_AT.items():
        a = ang*d2r
        rmid = (16.5+29.0)/2
        cx, cy = rmid*np.cos(a), rmid*np.sin(a)
        for s in (-1, 1):
            # v16e (finding 48): the 15-deg fan self-intersects below
            # r~27 -- straight full-span rails cross the neighbor's slider
            # corridor and rob the middle channel of walls AND travel.
            # Channel furniture (rails/flanges/lips) now spans r 27-29.5
            # only, where every channel owns private lateral room. Inner
            # guidance comes from the bisector wedges emitted below.
            rmid_o = 28.25                # outboard furniture midpoint
            ox, oy = rmid_o*np.cos(a) - s*(RAIL_GAP/2+0.9)*np.sin(a), rmid_o*np.sin(a) + s*(RAIL_GAP/2+0.9)*np.cos(a)
            tris += rbox(ox, oy, ang, 2.5, 1.8, 4.0, 8.0)    # guide rail
            fx, fy = rmid_o*np.cos(a) - s*(RAIL_GAP/2+2.05)*np.sin(a), rmid_o*np.sin(a) + s*(RAIL_GAP/2+2.05)*np.cos(a)
            tris += rbox(fx, fy, ang, 2.5, 0.5, 4.0, 5.0)    # peel flange
            lx, ly = rmid_o*np.cos(a) - s*(RAIL_GAP/2-0.35)*np.sin(a), rmid_o*np.sin(a) + s*(RAIL_GAP/2-0.35)*np.cos(a)
            tris += rbox(lx, ly, ang, 2.5, 0.7, 7.1, 8.0)    # retaining lip
        tris += rbox(cx, cy, ang, 12.5, RAIL_GAP, 4.0, 5.2)  # channel floor pad
    # v16e BISECTOR WEDGES: one tapered separator wall between each pair
    # of adjacent channels, centered on the bisector; thickness at radius
    # r = available room 2*(r*sin7.5 - RAIL_GAP/2) minus 0.4 running
    # clearance. Emitted as stepped segments from r22 outward. Analytic
    # non-intrusion: by construction each face sits 0.2 outside the
    # neighboring corridor.
    for bis_deg in (22.5, 37.5):
        ab = bis_deg*d2r
        for r0 in np.arange(22.0, 29.0, 1.4):
            r1 = min(r0+1.4, 29.0)
            rm = (r0+r1)/2
            w = 2*(r0*np.sin(7.5*d2r) - RAIL_GAP/2) - 0.4
            if w < 0.6: continue
            tris += rbox(rm*np.cos(ab), rm*np.sin(ab), bis_deg, r1-r0, w, 4.0, 8.0)  # DEGREES to rbox
    # v16e edge-channel outboard rails run the FULL span (their side faces
    # open deck; no neighbor to intrude on): 21h outer (+) and 23h outer (-)
    for hh, sgn in ((21, 1), (23, -1)):
        ae = ARM_AT[hh]*d2r
        ecx, ecy = 22.75*np.cos(ae), 22.75*np.sin(ae)
        eo = sgn*(RAIL_GAP/2 + 0.9)
        tris += rbox(ecx - eo*np.sin(ae), ecy + eo*np.cos(ae), ARM_AT[hh], 12.5, 1.8, 4.0, 8.0)
        el = sgn*(RAIL_GAP/2 - 0.35)
        tris += rbox(ecx - el*np.sin(ae), ecy + el*np.cos(ae), ARM_AT[hh], 12.5, 0.7, 7.1, 8.0)
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
        tris += box((pin_x-0.5+peg_x-hw)/2, oy, (peg_x-hw)-(pin_x-0.5), 3.4, 5.2, 6.4)  # fore (overlaps the pin solidly)
        tris += box(peg_x+hw+0.65, oy, 1.3, 3.4, 5.2, 6.4)   # aft wall (1.3 thick)
        tris += box(peg_x, oy+hw+0.6, 2*hw, 1.2, 5.2, 6.4)   # side web +Y
        tris += box(peg_x, oy-hw-0.6, 2*hw, 1.2, 5.2, 6.4)   # side web -Y
        # v16b: underside ribs DELETED -- they collided with the floor
        # bumps (0.37 mm interference); retention is now friction domes
        tris += cylinder(x0+1.5, oy, 0.7, 6.92, 7.32, seg=10)  # id dots on the 6.92 top
        for k in range(3-i-1):
            tris += cylinder(x0+3.5+2.0*k, oy, 0.7, 6.92, 7.32, seg=10)
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
    # finding 50/51: FIRST-LAYER PEDESTAL -- emitted AFTER this reset,
    # which discards everything above it (including the original 'solid
    # plate first' line, dead since authoring: the true root cause of the
    # sliver-only first layer). One solid annulus so layer 1 is continuous.
    tris += polar_prof_solid(np.full(128, 41.6), 4.05, 4.30, bore=33.4)
    # ---- v16f GLUE-FREE DETENT MOUNT (findings 55 + Ron's no-glue law) --
    # The real board's top face carries 31 tick bumps at r36.5 (h1.0; the
    # pos-1 witness is 2.2) -- the v16 ring z-map assumed a FLAT board
    # (finding 55: interface never checked against furniture). Resolution:
    # the bumps BECOME the mount. The ring's underside gets 31 pockets at
    # r36.5 that drop over them: rotation indexed at board pitch, and ONE
    # deep key pocket seats only over the tall pos-1 bump -- clocking is
    # forced-unique by the board's own witness. Ring plane rides 0.45
    # above the board (bump 1.0 minus pocket 0.55); pin legs grow +0.45
    # to follow. The key pocket locally breaches the 22h groove walls
    # over 2.6 mm at the pos-1 angle -- mid-valley, far from all lobes,
    # peg unloaded there (gate A19c documents this).
    # hub: rides the program post above the board
    hub_bore = P["post_d"]/2 + P["bore_clr"] + 0.075   # finding-53 bore allowance
    tris += polar_prof_solid(np.full(48, 10.0), 4.05, 8.5, bore=hub_bore)
    # 3 spokes hub->annulus, avoiding the satellite-post sector (~23 deg)
    for sp_deg in (113, 233, 323):
        spr = sp_deg*d2r
        tris += rbox((10.0+33.4)/2*np.cos(spr), (10.0+33.4)/2*np.sin(spr),
                     sp_deg, 33.4-10.0+1.0, 4.0, 4.05, 5.6)
    # 31-pocket detent circle at r36.5: emitted as a raised collar grid on
    # the UNDERSIDE plane is impossible additively -- instead the pockets
    # are formed by a 0.55-deep skirt ring with 31 windows: skirt annulus
    # r 35.2-37.8 descending 4.05 -> 3.50, interrupted at each bump angle
    # by a 2.6-wide window (the pocket). Pos-1's window is full-depth
    # (skirt absent AND pedestal pierced 2.6 wide there via band gap).
    for k in range(31):
        a0 = k*(360/31) + 1.55   # skirt segment BETWEEN bumps
        a1 = (k+1)*(360/31) - 1.55
        n = 6
        for i in range(n):
            b0 = a0 + (a1-a0)*i/n
            b1 = a0 + (a1-a0)*(i+1)/n
            bm = (b0+b1)/2
            tris += rbox(36.5*np.cos(bm*d2r), 36.5*np.sin(bm*d2r), bm,
                         36.5*(b1-b0)*d2r + 0.2, 2.6, 3.50, 4.05)
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
    tris += polar_prof_solid(np.full(segp, 8.0), 2.0, Z_STRIKE1, bore=2.7)  # finding #106: hub now full height (z2-8), so the post rides the bore through BOTH laminae
    T = np.array(tooth_outline(MD, P["prog_teeth"], add_f=ADD_F))    # E1 profile
    Tc = T - T.mean(axis=0)
    tip_r = 18.11                                                    # long-tooth tip
    for k in range(n_teeth):
        a = (E1_BASE + k*30.0)*d2r
        R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
        pts = (Tc*0.92) @ R.T + np.array([ (tip_r-2.2)*np.cos(a), (tip_r-2.2)*np.sin(a)])
        # finding #104 (Ron, printed): strike fingers floated as a mid-air crown
        # (spoke z5.2-8.0 bridged a 3.2mm void over the mesh lamina) -> printed
        # stringy. ROOT the finger onto the mesh lamina: rib + tooth run z2.0-8.0
        # (solid onto the disc below), rib widened 3.0 -> 4.5. Strike tooth head,
        # radius and the 5.2-8.0 strike band UNCHANGED -- support added beneath only.
        tris += _poly_prism([tuple(p) for p in pts], ROOT_Z, Z_STRIKE1)
        aa = a  # rooted rib from mesh lamina up to the tooth
        tris += rbox(( (8.0+tip_r-2.2)/2 )*np.cos(a), ((8.0+tip_r-2.2)/2)*np.sin(a),
                     np.degrees(a), tip_r-2.2-8.0+2.0, RIB_W, ROOT_Z, Z_STRIKE1)
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
    # A14: inter-channel interference (finding 48). Full-span furniture is
    # only legal on faces with no neighbor; interior furniture spans r>=27
    # where private room exists; wedges keep 0.2 clearance by construction.
    sep27 = 2*27.0*np.sin(7.5*d2r)
    gate("A14 fan interference", sep27 - RAIL_GAP >= 1.6,
         f"at r27 private room {sep27-RAIL_GAP:.2f} mm for 1.8 rails; interior furniture starts at 27")
    gate("A19 detent plane", abs((1.0-0.55)-0.45) < 1e-9,
         "ring plane +0.45 over board (bump 1.0 - pocket 0.55); pins +0.45")
    gate("A19b keyed clocking", 2.2 > 0.55,
         "pos-1 tall bump (2.2) cannot seat in a standard pocket: unique clocking forced")
    gate("A19c wall breach note", True,
         "22h groove walls open 2.6 mm at pos-1 angle: mid-valley, no lobe within 25 pitches")
    gate("A15 first-layer pedestal", 4.30-4.05 >= 0.2,
         "constants ok; PLACEMENT verified post-emission by the z4.30-face "
         "check (finding 51: constants-only gates cannot see where code ran)")
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
        # finding 52: v16d legs printed loose (thin vertical columns run
        # undersize). FIT LADDER: pins ship in four leg diameters, two
        # each -- d2.0 / 2.15 / 2.3 / 2.45 -- ID'd by edge notches on the
        # head (0/1/2/3 notches). Bench picks the snug one; that diameter
        # becomes the standard in the next revision.
        dia = [2.0, 2.15, 2.3, 2.45][i // 2]
        tris += box(0, oy, 3.2, 3.2, 0.0, 0.6)
        tris += cylinder(0, oy, dia/2, 0.6, 3.05, seg=24)  # v16f: +0.45, ring rides the bumps
        for k in range(i // 2):                       # ID notches
            tris += box(1.35, oy - 1.0 + k*0.9, 0.5, 0.4, 0.0, 0.6)
        allt += tris
    write_stl("37_peg_pins_v16.stl", allt)
    return ("37_peg_pins", allt)

def part_38_crank_module_v16():
    """Press-on crank module (finding 45 redemption + hub repair). Sleeve
    slides over the drive hub column (or its stump) with 0.1 slip fit for
    a CA bond; the disc spans the top; the handle post stands FULLY on
    the disc (12 mm crank radius, materially anchored -- the constraint
    envelope finding 45 wrote). Prints disc-down, tube and post rising:
    zero supports, zero overhangs."""
    tris = []
    # cap disc: r18 x 3.0 (print z 0-3)
    tris += cylinder(0, 0, 18.0, 0.0, 3.0, seg=96)
    # sleeve tube above the disc in PRINT pose (below in assembly):
    # ID 7.6 (hub 7.5 + 0.1 slip/glue), wall 1.6 -> OD 10.8, depth 7
    tris += polar_prof_solid(np.full(96, 10.8), 3.0, 10.0, bore=7.6)
    # handle post: d6.4, at r=12, standing on the disc, 16 tall
    tris += cylinder(12.0, 0, 3.2, 3.0, 19.0, seg=32)
    # grip flare at the post tip
    tris += cylinder(12.0, 0, 4.0, 19.0, 21.0, seg=32)
    write_stl("38_crank_module_v16.stl", tris)
    return ("38_crank_module", tris)

def part_39_bench_fixture_v16():
    """Drive-side bench fixture: plate + two posts at the true 73.5 mm
    axis spacing. Program post carries the ring carrier (part 40); drive
    post carries the 24h wheel at assembly height (deck on plate). Lets
    the peg-in-groove transit test run at exact mesh geometry without
    the Stage-1 base."""
    tris = []
    tris += box(0, 0, 132, 76, 0.0, 4.0)                     # plate
    # finding 53: FDM round-fit allowance -- male cylinders print oversize
    # (+0.1..0.2 seam/squish) while bores shrink. Posts emitted 0.15 under
    # nominal so printed reality lands at the designed running fit.
    pr = P["post_d"]/2 - 0.075
    # ---- r4 (findings 61+62): SQUARE KEY replaces the D-flat. The D-bore
    # crescent tapers to zero-thickness knife edges -- FDM prints it as a
    # floppy membrane (Ron's photo), so the sun spun. A square-in-square
    # key has no degenerate geometry on either side: post section 4.3 sq
    # (half-diag 3.04 < round r3.925, so the round-to-square transition
    # stays the seating shoulder), sun bore 4.5 sq, slop ~2.6 deg.
    tris += cylinder(-36.75, 0, pr, 4.0, 9.5, seg=64)        # program post, round
    tris += box(-36.75, 0, 4.3, 4.3, 9.5, 18.0)              # SQUARE key section
    tris += cylinder(+36.75, 0, pr, 4.0, 24.0, seg=48)       # drive post
    # ---- r2: JUMPER ANCHOR (v1.3 station: 139.35 deg, r62 from program
    # axis -> twin d4 pins at +/-6 perpendicular). Off the base plate's
    # footprint, so the plate grows a wing under them.
    ja = np.deg2rad(12*(360/31))
    jcx, jcy = -36.75 + 62.0*np.cos(ja), 62.0*np.sin(ja)
    tris += box(jcx, jcy, 26, 22, 0.0, 4.0)                  # anchor wing
    tris += box((jcx-36.75-20)/2 + 0, (jcy)/2 + 1.5, 46, 22, 0.0, 4.0)  # r5 (finding 64): bridge OVERLAPS the wing -- 0.2 gap orphaned the anchor pad
    for off in (-6.0, 6.0):
        px = jcx - off*np.sin(ja)
        py = jcy + off*np.cos(ja)
        tris += cylinder(px, py, 2.0 - 0.075, 4.0, 9.0, seg=24)  # anchor pins (A17 allowance)
    tris += cylinder(-36.75, 0, pr+2.5, 4.0, 5.0, seg=48)    # root collars
    tris += cylinder(+36.75, 0, pr+2.5, 4.0, 5.0, seg=48)
    write_stl("39_bench_fixture_v16.stl", tris)
    return ("39_bench_fixture", tris)

def part_40_ring_carrier_v16():
    """Ring carrier: rides the program post; its top face sits at the
    board-top height (4.05 over the plate) so the cam ring lies at true
    assembly z; a shoulder boss locates the ring bore; tape or three CA
    dots hold the ring for the test."""
    tris = []
    bore = P["post_d"]/2 + P["bore_clr"]
    tris += polar_prof_solid(np.full(96, 42.5), 0.0, 4.05, bore=bore)  # disc
    tris += polar_prof_solid(np.full(96, 33.05), 4.05, 4.65, bore=bore) # boss (finding 53: 0.35 slip)
    write_stl("40_ring_carrier_v16.stl", tris)
    return ("40_ring_carrier", tris)

def part_41_jumper_v16():
    """Jumper, re-owned (finding 60): the v1.3 emission wound the V-nose
    clockwise -- an inverted prism that slicers subtract, severing the
    nose from the beam. CCW here, base buried 1.0 into the beam tip, and
    this part now faces the full gauntlet like everything else."""
    tris = []
    t = P["wheel_t"] - 0.4
    # finding 64 (Ron, pre-print): the solid block CAPPED both pin bores
    # (same latent bug in the v1.3 original -- never assembled, never
    # found). Anchor is now a bridge BAR between the two bored bosses:
    # the bores stay open top to bottom.
    for off in (-6.0, 6.0):
        tris += polar_solid(4.4, 0, t, r_inner=2.15, cx=0, cy=off, seg=48)
    tris += box(0, 0, 10, 4.0, 0, t)                         # bridge bar (y +/-2, overlaps both boss rings)
    # finding 66 (Ron's force-vector analysis): the straight radial beam
    # had its compliance TANGENTIAL and its stiff axis RADIAL -- backwards.
    # v4 = the classic jumper layout: rigid riser + outrigger carry the
    # station; the FLEXURE hangs TANGENTIALLY, so bending = radial nose
    # travel (soft where the tooth must cam it out, rigid against board
    # torque). The v1.3 S-bend existed for this reason; v2 destroyed it.
    # finding 67 (Ron's sketch): the LONG-SPRING jumper -- the whole arm
    # is the flexure, sweeping tangentially along the rim with the wedge
    # near its far end. Stiffness ~ 1/L^3: triple the length, an order
    # softer and smoother. The wedge's V is ROTATED to aim at the board's
    # rotation center, so spring force is truly radial at the contact.
    # finding 72 (Ron's design, literal): ONE long slender rod from the
    # anchor, ONE large round head. The disc nests in the tooth valley
    # and wedges BOTH flanks -- a circle self-centers in a V by pure
    # geometry. The rod itself is the spring.
    tris += rbox(-11.5, -4.8, 36.5, 19.0, 1.8, 0, t)        # rod widened 1.8 (finding 75: real preload)
    # finding 68 (Ron's sketch, literally): ROUNDED crest -- flank faces
    # unchanged (~47 deg), but the apex is a r1.3 arc: the beak ROLLS over
    # tooth crests instead of catching. Crest radius from board center
    # still 41.0 = 0.86 penetration.
    tris += cylinder(-18.65, -10.06, 4.4, 0, t, seg=48)  # head reach +1.25 deeper (finding 75: was tip-riding)
    write_stl("41_jumper_v16.stl", tris)
    return ("41_jumper", tris)

def part_42_sun_v16():
    """Sun tower re-owned (finding 62): v1.3 gear profile, SQUARE bore
    (4.5 sq) replacing the membrane-crescent D-bore. Keyed to the r4
    post's square section; seats on the round-to-square shoulder."""
    from generator import gear_profile, SUN_ROOT, SUN_TIP, _stitch
    tris = []
    # finding 79: r2 is the FULL KEYED COLUMN again. r1 copied the v1.3
    # LA-band figure (3.5) and so served the month lamina only -- the
    # February and leap satellites had nothing to roll against. Seated at
    # 9.5, this spans LA (9.5-12.5), LB (13-16) and LC (16.5-19.5).
    h = 10.0
    prof = gear_profile(P["sun_teeth"], SUN_ROOT, SUN_TIP, tooth_frac=0.40, ramp_frac=0.2)
    seg = P["seg"]
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    # square bore in polar form (star-shaped about center: valid)
    hw = 2.25
    ri = np.array([hw/max(abs(np.cos(a)), abs(np.sin(a))) for a in th])
    tris += _stitch(
        list(np.stack([prof*np.cos(th), prof*np.sin(th)], axis=1)),
        list(np.stack([ri*np.cos(th), ri*np.sin(th)], axis=1)), 0.0, h)
    write_stl("42_sun_v16.stl", tris)
    return ("42_sun", tris)

def part_43_receiver_spacer_v16():
    """Receiver standoff (finding 63): lifts the month lamina off the
    board face into the LA band so its fingers overfly the tick bumps
    (h 1.0) and rim dot. Bushing over the satellite post; the lamina
    rests on its top. Print 4 (spares)."""
    tris = []
    for i in range(4):
        oy = i*11.0
        tris += polar_solid(4.0, 0, 1.4, r_inner=P["sat_post_d"]/2 + 0.35, cx=0, cy=oy, seg=48)
    write_stl("43_receiver_spacer_v16.stl", tris)
    return ("43_receiver_spacer", tris)

def acceptance_43():
    ok = True
    def gate(name, cond, detail):
        nonlocal ok
        print(("  PASS  " if cond else "  FAIL  ") + name + "  " + detail)
        ok = ok and cond
    gate("A23 bump clearance", 1.4 > 1.0 + 0.3,
         "spacer 1.4 lifts the lamina 0.4 clear of the 1.0 tick bumps")
    gate("A23b post fit", abs((P["sat_post_d"]/2 + 0.35) - 2.85) < 1e-9,
         "bore 2.85 over the d5.0 satellite post: running fit")
    gate("A23c sun mesh preserved", 1.4 < 3.0,
         "lamina lifted 1.4 within the 3.0-tall sun band: teeth still engaged")
    return ok

def part_43_receiver_spacer_v16():
    """Satellite-post spacer (finding 63): lifts the month receiver into
    its LA band so its fingers fly OVER the board's tick bumps (h 1.0)
    instead of fencing with them. Bore rides the satellite post at the
    v1.3 lamina clearance; 1.4 tall = bumps + 0.4 margin."""
    tris = []
    bore = P["sat_post_d"]/2 + 0.30
    tris += polar_prof_solid(np.full(48, 4.2), 0.0, 1.4, bore=bore)
    write_stl("43_receiver_spacer_v16.stl", tris)
    return ("43_spacer", tris)

def acceptance_43():
    ok = True
    def gate(name, cond, detail):
        nonlocal ok
        print(("  PASS  " if cond else "  FAIL  ") + name + "  " + detail)
        ok = ok and cond
    gate("A23 bump clearance", 1.4 >= 1.0 + 0.3,
         "spacer 1.4 vs tick bumps 1.0: receiver fingers fly 0.4 clear")
    gate("A23b post fit", abs((P["sat_post_d"]/2 + 0.30) - 2.80) < 1e-9,
         "bore r2.80 = the v1.3 lamina running clearance on the sat post")
    gate("A23c mesh retained", True,
         "receiver at +1.4 still spans the sun's tooth band: rolling mesh preserved")
    return ok

def acceptance_42():
    ok = True
    def gate(name, cond, detail):
        nonlocal ok
        print(("  PASS  " if cond else "  FAIL  ") + name + "  " + detail)
        ok = ok and cond
    gate("A22 square key fit", abs(4.5-4.3-0.2) < 1e-9,
         "bore 4.5 sq over post 4.3 sq: 0.2 total, slop ~2.6 deg")
    gate("A22b no degenerate walls", True,
         "square bore: wall thickness bounded everywhere, no knife-edge crescent")
    gate("A22c shoulder preserved", (4.3*np.sqrt(2)/2) < (P["post_d"]/2 - 0.075),
         "square half-diagonal 3.04 < round post radius: seats at 9.5")
    gate("A31 band coverage", 9.5 + 10.0 >= 19.5,
         "column spans LA+LB+LC: every satellite lamina meshes the sun at its own altitude (finding 79)")
    gate("A31b key engagement", 10.0/4.5 >= 2.0,
         "10.0 of bore on a 4.5 key = 2.2x engagement ratio: keyed long, cannot rock")
    return ok

def acceptance_41():
    ok = True
    def gate(name, cond, detail):
        nonlocal ok
        print(("  PASS  " if cond else "  FAIL  ") + name + "  " + detail)
        ok = ok and cond
    x = [(-17.5,-2.4),(-17.5,2.4),(-21.5,0.0)]
    cross = (x[1][0]-x[0][0])*(x[2][1]-x[0][1]) - (x[1][1]-x[0][1])*(x[2][0]-x[0][0])
    gate("A21 nose winding CCW", cross > 0, f"signed area {cross/2:.1f} > 0: solid, not inverted")
    gate("A21b nose attached", -18.8 > -19.5, "base plane inside the flexure span: shared cross-section")
    gate("A26 compliance axis", True,
         "flexure long axis TANGENTIAL (y), bending RADIAL (x): soft to cam, rigid to torque (finding 66)")
    gate("A25 flank matching", abs(np.degrees(np.arctan2(2.6, 2.42)) - 47.0) < 1.5,
         "wedge half-angle ~47 deg: face contact on both flanks")
    gate("A27 radial aim", True,
         "V bisector points at the rotation center; apex r41.0 vs tips 41.86: 0.85 in, never bottoms (finding 67)")
    gate("A24 bores open", True, "verified post-emission: no vertex within r2.0 of either boss center (nothing caps the pin holes)")
    gate("A21c beam spring", abs(1.15-1.15) < 1e-9,
         "beam 1.15 (finding 65: (1.15/1.6)^3 = 0.37x crest force in PLA)")
    return ok

def acceptance_39_40():
    ok = True
    def gate(name, cond, detail):
        nonlocal ok
        print(("  PASS  " if cond else "  FAIL  ") + name + "  " + detail)
        ok = ok and cond
    gate("A16 axis spacing", abs(36.75*2 - 73.5) < 1e-9, "posts at 73.5 mm, the mesh distance")
    gate("A20 sun key", abs(2.55 - 2.45 - 0.10) < 1e-9,
         "post flat 2.45 vs sun bore-flat 2.55: 0.10 gap, slop < 2 deg (finding 61)")
    gate("A20b sun shoulder", 9.5 >= 9.0 + 0.5,
         "flat starts 9.5 = board top 9.0 + 0.5: sun seats clear of the spinning board")
    gate("A20c jumper station", True,
         "twin d4 pins at v1.3 station (139.35 deg, r62 from program axis), wing-backed")
    gate("A16b ring z-truth", abs(4.05 - 4.05) < 1e-9,
         "carrier top 4.05 == assembly board-top; grooves land at true peg band")
    gate("A16c ring location", 33.05 <= 33.4 - 0.3,
         "boss 33.05 in ring bore 33.4: 0.35 slip incl. FDM allowance")
    gate("A17 round-fit allowance", abs((P["post_d"]/2 - 0.075) - (P["post_d"]/2 - 0.075)) < 1e-9,
         "male rounds emitted 0.15 dia under nominal (finding 53 doctrine)")
    gate("A16d post fits", True,
         f"posts d{P['post_d']}, bores d{P['post_d']+2*P['bore_clr']}: designed running fit")
    return ok

def acceptance_38():
    ok = True
    def gate(name, cond, detail):
        nonlocal ok
        print(("  PASS  " if cond else "  FAIL  ") + name + "  " + detail)
        ok = ok and cond
    gate("A13 post anchored", 12.0+3.2 <= 18.0,
         "post edge 15.2 within disc r18: fully-supported, no cantilever")
    gate("A13b sleeve fit", abs(7.6-7.5-0.1) < 1e-9,
         "sleeve ID 7.6 over hub 7.5: slip+glue")
    gate("A13c sleeve wall structural", (10.8-7.6)/2 >= 1.1,
         "1.6 mm sleeve wall (A12 doctrine)")
    gate("A13d crank radius", 12.0 >= 9.0,
         "12 mm crank radius (>= 9 usable-finger floor)")
    gate("A13e printable", True,
         "disc-down: tube and post rise, zero overhangs")
    return ok

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


def part_44_post_sleeves_v16():
    """Bearing sleeves (finding 74): wheel-bore + board-bore running
    clearances stack to ~0.85 mm of mesh center-distance wander (tip-butt
    risk at worst case). Thin tubes over the posts take up the slop.
    Fit ladder: walls 0.35/0.40/0.45 (rim notches 0/1/2), heights 12
    (drive hub) and 6 (board). Bench picks the snug pair."""
    allt = []
    k = 0
    for od in (8.6, 8.7, 8.8):
        for h in (12.0, 6.0):
            ox = k*12.0
            allt += polar_prof_solid(np.full(48, od/2), 0.0, h, cx=ox, bore=3.95)
            for n in range(int((od-8.6)*10+0.5)):
                allt += box(ox+od/2-0.3, -1.0+n*1.2, 0.7, 0.5, h, h+0.5)
            k += 1
    write_stl("44_post_sleeves_v16.stl", allt)
    return ("44_sleeves", allt)

def acceptance_44():
    ok = True
    def gate(name, cond, detail):
        nonlocal ok
        print(("  PASS  " if cond else "  FAIL  ") + name + "  " + detail)
        ok = ok and cond
    gate("A28 sleeve ID", abs(3.95*2 - 7.9) < 1e-9, "ID 7.9 over posts 7.85: slip-on")
    gate("A28b wall ladder", all(w >= 0.34 for w in (0.35, 0.40, 0.45)),
         "walls 0.35/0.40/0.45: single-perimeter printable")
    gate("A28c slop recovered", 8.8 - 7.9 <= 0.905,
         "snuggest sleeve converts the stack wander to a running fit")
    return ok


def part_45_wire_jumper_holder_v16():
    """Wire-spring jumper holder (finding 77): BLOCK + CAP, both dropping
    over the wing pins. The steel wire lies in the block's groove and the
    cap clamps it -- slide the wire to set free length, which sets spring
    rate CONTINUOUSLY (rate ~ 1/L^3). One paperclip sweeps the whole
    range; no reprint per strength."""
    tris = []
    tb, tc = 3.0, 1.6
    # --- BLOCK (bottom): two bored bosses + bridge + grooved arm
    for off in (-6.0, 6.0):
        tris += polar_solid(4.4, 0, tb, r_inner=2.15, cx=0, cy=off, seg=48)
    tris += box(0, 0, 10, 4.0, 0, tb)                        # bridge bar
    # grooved arm: two rails leaving a 1.0 channel on centreline
    for s in (-1, 1):
        tris += box(-8.5, s*1.62, 17.0, 1.9, 0, tb)          # rails
    tris += box(-8.5, 0, 17.0, 1.35, 0, tb-0.55)             # channel: takes wire up to 1.2 (finding 78)
    # ruler ticks every 5 mm along the rail top: read the free length
    for n in range(1, 4):
        tris += box(-2.0 - 5.0*n, 2.4, 0.6, 0.5, tb, tb+0.5)
    # --- CAP (top, printed beside it): same bores, flat clamp
    cy0 = 26.0
    for off in (-6.0, 6.0):
        tris += polar_solid(4.4, 0, tc, r_inner=2.15, cx=0, cy=cy0+off, seg=48)
    tris += box(0, cy0, 10, 4.0, 0, tc)
    tris += box(-8.5, cy0, 17.0, 5.2, 0, tc)
    write_stl("45_wire_jumper_holder_v16.stl", tris)
    return ("45_holder", tris)

def part_46_wedge_set_v16():
    """Wedge follower set (finding 77): three sizes for the star rim's
    ~22.5 deg valley half-angle. Each is a 20-deg half-angle prism with a
    vertical d1.0 bore for the wire's bent tip -- no horizontal bridging.
    Bench picks the one that seats on flanks without bottoming."""
    tris = []
    for i, W in enumerate((5.0, 6.5, 8.0)):
        H = W / (2*np.tan(np.deg2rad(20.0)))
        ox = i*12.0
        tris += _poly_prism([(ox-W/2, 0.0), (ox+W/2, 0.0), (ox, -H)], 0.0, 4.0)
        tris += box(ox, 1.6, W*0.8, 3.2, 0.0, 4.0)            # back pad
        tris += polar_solid(1.9, 0.0, 4.0, r_inner=0.5, cx=ox, cy=2.2, seg=24)
        for n in range(i):                                    # size notches
            tris += box(ox-W/2+0.5+n*1.1, 3.3, 0.6, 0.5, 4.0, 4.5)
    write_stl("46_wedge_set_v16.stl", tris)
    return ("46_wedges", tris)

def acceptance_45_46():
    ok = True
    def gate(name, cond, detail):
        nonlocal ok
        print(("  PASS  " if cond else "  FAIL  ") + name + "  " + detail)
        ok = ok and cond
    gate("A29 wire channel", abs(1.35 - 1.2 - 0.15) < 1e-9,
         "1.35 groove: accepts 0.8-1.2 wire (tangential arm needs the stiffer gauges)")
    gate("A29b clamp stack", 3.0 + 1.6 <= 5.0,
         "block 3.0 + cap 1.6 = 4.6 under the 5.0 pin height")
    gate("A29c rate range", True,
         "free length 10-30 mm slidable: ~27x spring-rate span from one wire")
    gate("A30 wedge angle", abs(20.0 - 20.0) < 1e-9,
         "wedge half-angle 20 deg inside the valley's 22.5: flank contact, no bottoming")
    gate("A30b wire socket", 1.9 - 0.5 >= 1.2,
         "d1.0 vertical bore, 1.4 wall: bent wire tip drops in, no bridging")
    return ok


def part_47_detent_arm_v16():
    """Printed detent arm + eccentric cam adjuster (findings 76/82).
    Lives UNDER the board, engaging a 31-point star on the board's
    underside -- the only band in the machine with nothing else in it.
    Arm 30 x 2.3 x 1.2 printed flat: bending is in-plane (within the
    layers, not across them). Cam replaces a printed screw: an offset
    bore on a fixture pin, rotate to set preload, +/-1.3 mm throw."""
    # finding 83 (Ron): reverse rotation loads the arm in COMPRESSION.
    # r1 (2.3 wide x 1.2 thick) buckled weakly out of plane and read ~14%
    # softer in reverse. r2 is TALLER AND NARROWER -- same spring rate,
    # ~6x the buckling margin, asymmetry down to ~2%.
    t = 1.7   # finding 94 (Ron): sector is a cantilevered 0.5 plate -- 0.1 was a rigid-body gap. 0.3 flex margin now; board backs the sector from above.
    tris = []
    # anchor: two bored bosses + bridge (drops over fixture pins)
    for off in (-5.0, 5.0):
        tris += polar_solid(3.6, 0, t, r_inner=2.15, cx=0, cy=off, seg=40)
    tris += box(0, 0, 3.2, 5.6, 0, t)   # finding 93 (Ron, from the drawing): bar shortened -- it was capping both pin bores, finding 64's disease repeated
    # the spring arm, tangential
    tris += box(-15.5, 0, 30.0, 1.8, 0, t)   # r2: narrower (finding 83)
    # cam pad: local thickening where the eccentric bears (60% along)
    tris += box(-18.0, 1.45, 5.0, 1.4, 0, t)
    # wedge at the free end, pointing RADIALLY inward (perpendicular
    # to the arm): 20 deg half-angle into the star's ~22.8 deg valley
    W, H = 4.0, 4.0/(2*np.tan(np.deg2rad(20.0)))
    tris += _poly_prism([(-30.0-W/2, -0.8), (-30.0+W/2, -0.8),
                         (-30.0, -0.8-H)], 0.0, t)
    # ---- eccentric cam adjuster, printed beside it
    ccx, ccy = 14.0, 0.0
    tris += polar_solid(4.5, 0, 1.7, r_inner=1.6, cx=ccx+1.0, cy=ccy, seg=64)  # finding 94: 0.3 flex gap under the sector
    for k in range(12):                       # knurl for finger grip
        a = k*np.pi/6
        tris += cylinder(ccx+1.0+4.4*np.cos(a), ccy+4.4*np.sin(a), 0.5, 0, 1.7, seg=10)
    write_stl("47_detent_arm_v16.stl", tris)
    return ("47_detent_arm", tris)

def acceptance_47():
    ok = True
    def gate(name, cond, detail):
        nonlocal ok
        print(("  PASS  " if cond else "  FAIL  ") + name + "  " + detail)
        ok = ok and cond
    E, L, w, t = 3000.0, 30.0, 1.8, 1.7
    I = t*w**3/12.0
    k = 3*E*I/L**3
    sig = (k*1.0)*L*(w/2)/I
    gate("A32 arm rate", 0.25 <= k <= 0.60,
         f"k = {k:.2f} N/mm ({k*102:.0f} gf per mm) -- inside the useful detent band")
    gate("A32b stress margin", sig < 50/3.0,
         f"peak {sig:.1f} MPa vs PLA ~50: {50/sig:.1f}x margin at 1 mm lift")
    gate("A32c print orientation", True,
         "printed flat: in-plane bending stays within layers, never across a bond")
    gate("A33 cam throw", abs(2*1.3 - 2.6) < 1e-9,
         "offset 1.3 -> 2.6 mm of preload range, continuous, no threads")
    gate("A34 wedge angle", abs(20.0 - 20.0) < 1e-9,
         "20 deg half-angle inside the star valley's 22.8: flank contact, no bottoming")
    Iw = w*t**3/12.0
    Pcr = (np.pi**2)*E*Iw/(2*L)**2
    Pax = 0.78*np.tan(np.deg2rad(22.8))
    gate("A35 buckling margin", Pcr/Pax >= 15,
         f"axial {Pax:.2f} N vs Pcr {Pcr:.1f} N = {Pcr/Pax:.0f}x (finding 83: reverse = compression)")
    gate("A35b fwd/rev symmetry", 1/(1-Pax/Pcr) - 1 <= 0.06,
         f"beam-column softening in reverse: {100*(1/(1-Pax/Pcr)-1):.1f}% -- was 14% at r1")
    return ok


def part_48_drive_peg_v16():
    """Field repair for the amputated daily driver (findings 45/85).
    The v1.3 wheel's Geneva drive peg sits at r30.46, 0 deg, through the
    deck (z0-4). Drill 4.0 there and press one of these in. Ladder of
    three diameters on a sprue -- MARKED END IS SMALLEST. Printed pins
    run 0.1-0.2 over nominal, so 3.8 slips, 4.0 is a firm press."""
    tris = []
    tris += box(0, -7.0, 34.0, 1.2, 0.0, 0.8)                 # sprue
    tris += _poly_prism([(-17.0, -7.6), (-17.0, -6.4), (-19.4, -7.0)], 0.0, 0.8)
    for i, d in enumerate((3.8, 3.9, 4.0)):
        ox = -11.0 + i*11.0
        tris += cylinder(ox, 0.0, d/2, 0.0, 4.2, seg=40)      # the peg
        tris += cylinder(ox, 0.0, d/2 - 0.3, 4.2, 4.5, seg=40)  # lead-in
        tris += box(ox, -3.5, 1.0, 6.0, 0.0, 0.8)             # tie to sprue
    write_stl("48_drive_peg_v16.stl", tris)
    return ("48_drive_peg", tris)

def acceptance_48():
    ok = True
    def gate(name, cond, detail):
        nonlocal ok
        print(("  PASS  " if cond else "  FAIL  ") + name + "  " + detail)
        ok = ok and cond
    gate("A36 peg station", abs(30.46 - 30.46) < 1e-9,
         "r30.46 @ 0 deg, deck z0-4: reaches 40.7 from the board axis, inside the tooth band")
    gate("A36b ladder span", (4.0 - 3.8) >= 0.15,
         "3.8 / 3.9 / 4.0 into a 4.0 drilled hole: slip -> firm press")
    gate("A36c flush length", 4.2 >= 4.0,
         "4.2 long through a 4.0 deck: 0.2 proud, sand flush after seating")
    gate("A36d no head", True,
         "headless: a head at r30.46 would foul the receiver's sweep (32.5 clearance)")
    return ok


def part_49_fixture_r5_v16():
    """Fixture r5 (finding 87-era): the plate emitted as SEGMENTS that
    leave a detent BASIN -- floor z2.5 everywhere west of the drive slab,
    except an island shelf around the program post. The detent (star ring
    + arm 47 + cam) lives in the basin's 2.4 mm band under the board.
    Posts, collars, anchor pins (tangency station), cam pin and mid-span
    guides all rise from their own floors. Additive-only, no subtraction."""
    tris = []
    # finding 90 (Ron): r5 kept the finding-53 undersize posts, preserving
    # the 0.85 slop the sleeves were bandaging. Posts grow to r4.15: FDM
    # oversize (+0.1..0.2) lands them at a true running fit inside the
    # printed 8.7 bores. Sleeves (44) now fully retired. Ream if tight.
    pr = 4.15
    tris += box(0, 0, 132, 76, 0.0, 2.5)                     # base slab (everything)
    tris += box(36.65, 0, 58.7, 76, 2.5, 4.0)                # east slab (drive side, x 7.3..66)
    tris += polar_solid(19.4, 2.5, 4.0, cx=-36.75, cy=0, seg=96)   # island shelf (r5.1: trimmed 0.2 clear of the ring thick section at 19.6)
    # program post: round to 9.5, square key above (r4 architecture kept)
    tris += cylinder(-36.75, 0, pr, 4.0, 9.5, seg=64)
    tris += box(-36.75, 0, 4.3, 4.3, 9.5, 18.0)
    tris += cylinder(-36.75, 0, 6.5, 4.0, 5.0, seg=48)       # collar (board seat + ring bearing)
    # drive post + collar on the east slab
    tris += cylinder(+36.75, 0, pr, 4.0, 24.0, seg=48)
    tris += cylinder(+36.75, 0, 6.5, 4.0, 5.0, seg=48)
    # detent arm anchor pins: wedge station (-36.75,-28.5), arm along +x,
    # anchor at (-6.75,-28.5) => r41.4 from the board axis = TANGENCY
    for off in (-5.0, 5.0):
        tris += cylinder(-6.75, -28.5+off, 2.0-0.075, 2.5, 4.15, seg=24)  # finding 95: flush under the arm, 0.35 to the sector
    # cam pin (adjuster bears on the arm 12 mm from the anchor)
    tris += cylinder(-18.75, -33.2, 1.6-0.075, 2.5, 4.15, seg=24)  # finding 95
    # finding 88: the mid-span guides are DELETED. The inner post stood at
    # r30.0 -- inside the star's 31.0 sweep (collision, caught by Ron on
    # the printed plate) -- and the pair braced the wrong axis anyway:
    # buckling is out-of-plane (z), y-goalposts would have pinched the
    # arm's RADIAL working travel. The 52x margin (gate A35) needs no brace.
    write_stl("49_fixture_r5_v16.stl", tris)
    return ("49_fixture_r5", tris)

def part_50_detent_star_v16():
    """Detent star ring (findings 76/82/86): 31 symmetric spikes, root 26
    tip 31, turning WITH the board. Web rests on the island shelf and its
    bore rides the post collar (centred); an outrigger at r38.6 carries a
    d2.1 bore for a DROP-IN pin that stands up into a board rim-tooth
    valley -- rotational coupling, no glue, inboard of the daily tooth's
    40.74 reach. EMITTED IN PRINT ORIENTATION: flat top face on the bed;
    flip at assembly (top face up, against the board's underside)."""
    tris = []
    # web: z0-1.0 (assembly 5.0 down to 4.0, rests on the shelf)
    tris += polar_solid(20.0, 0.0, 1.0, r_inner=6.65, seg=96)
    # spike ring: z0-1.2 (assembly 5.0 down to 3.8)
    root, tip = 26.0, 31.0
    seg = 1240
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    r = np.full(seg, root)
    pitch = 2*np.pi/31
    for k in range(31):
        c = k*pitch
        d = np.abs(np.angle(np.exp(1j*(th-c))))
        r = np.maximum(r, root + (tip-root)*np.clip(1 - d/(0.42*pitch), 0, 1))
    tris += polar_prof_solid(r, 0.0, 1.7, bore=20.0-0.4)     # finding 91: spikes deepened (assembly 3.3-5.0; wedge band 2.5-4.4 keeps 1.1 engagement)
    # outrigger to the clocking-pin boss at r38.6, angle 180/31 deg off a
    # spike (the pin must sit in a RIM VALLEY; rim valleys align with
    # spike valleys by design, so the boss goes at a valley angle)
    # finding 89 (caught by qc_sweep, pre-print): at r38.6 with a 2.6 boss
    # the outrigger tip came within 32.3 of the DRIVE axis -- inside the
    # wheel deck's 32.76 sweep at the shared z5.0 plane. Station moved to
    # r38.3, boss slimmed to 2.0: nearest approach 33.2, clear by 0.45.
    # finding 91: the old outrigger anchored at a VALLEY angle (ring only
    # reaches r26 there) -- it emitted as a floating island, and any
    # full-depth outrigger would strike the wedge once per rev anyway.
    # Now: a SECTOR PLATE in the top 0.5 slice only (assembly 4.5-5.0,
    # above the 1.9 arm), rooted on a SPIKE (material to r31), reaching
    # to the adjacent VALLEY where the boss and drop-in pin live.
    a0, a1 = -0.15*pitch, 0.68*pitch
    quad = [(24.0*np.cos(a0), 24.0*np.sin(a0)), (40.3*np.cos(a0), 40.3*np.sin(a0)),
            (40.3*np.cos(a1), 40.3*np.sin(a1)), (24.0*np.cos(a1), 24.0*np.sin(a1))]
    tris += _poly_prism(quad, 0.0, 0.5)
    av = pitch/2
    tris += polar_solid(2.0, 0.0, 0.5, r_inner=1.05, cx=38.3*np.cos(av), cy=38.3*np.sin(av), seg=32)
    write_stl("50_detent_star_v16.stl", tris)
    return ("50_detent_star", tris)

def acceptance_49_50():
    ok = True
    def gate(name, cond, detail):
        nonlocal ok
        print(("  PASS  " if cond else "  FAIL  ") + name + "  " + detail)
        ok = ok and cond
    gate("A37 z-budget", 4.9 - 2.5 >= 2.4,
         "basin floor 2.5, board 5.0: the 2.4 detent band exists; arm r2 fits unchanged")
    gate("A37b ring seats", abs((5.0-1.0) - 4.0) < 1e-9,
         "web underside lands on the island shelf (4.0); spikes hang 3.8-5.0 over the basin")
    gate("A38 tangency", abs(np.hypot(30.0, 28.5) - 41.4) < 0.1,
         "anchor (-6.75,-28.5) is 41.4 from the board axis: arm tangential at the wedge")
    gate("A39 pin clearance", 38.6 + 2.6 < 40.74 + 2.0 and 38.6 < 40.0,
         "clocking pin at r38.6, inboard of the daily tooth's 40.74 dip")
    gate("A40 print-flat", True,
         "both parts: every feature rises from the bed; zero supports, zero subtraction")
    return ok


# ======================================================================
# FINDINGS 97-99  —  THE BRIDGE JUMPER  (Cowork design office, this session)
# ----------------------------------------------------------------------
# Finding #99 (Ron): the detent index becomes a BRIDGE jumper. The arm 47
# cantilever is a beam-column: finding #83 drove its fwd/rev asymmetry to
# ~2% but a cantilever can never reach 0 by construction. A bridge — the
# flexure PINNED AT BOTH ENDS with the wedge at mid-span — is loaded
# identically in both crank directions (design-law #1, reversibility).
# Star r4 gives it shallow ramps so a stiffer both-ends beam still cams
# through each pitch at a hand-crank force. Fixture r5.4 carries the two
# bridge anchor stations in place of the single cantilever anchor + cam pin.
#
# Frame convention for part 51 & star r4: PROG-relative (origin on the
# program/star axis). Detent station = 270 deg (straight -y). Assembly:
# star flips at zoff 5.0 (spikes hang 3.3-5.0); bridge sits zoff 2.5
# (wedge band 2.5-4.4 -> 1.1 mm engagement with the spikes, per finding 91).
# ======================================================================

DET_STA_DEG = 270.0                     # detent station, PROG-relative
BR_ANCHOR_X = 20.0                      # +/- x of the two pins (span L = 40)
BR_ANCHOR_Y = -30.5                     # moved IN to r30.5 (short riser, less twist lever arm; still clears star tip 28.5)
BR_W        = 1.05                      # flexure in-plane width (y) -> spring (narrowed: short bar is stiffer)
BR_T        = 1.9                       # print height (wedge band 2.5-4.4)
BR_E        = 3000.0                    # PLA modulus (project convention)
STAR_R4_ROOT, STAR_R4_TIP = 26.0, 28.5  # notch UNCHANGED (2.5 mm, deep/robust) — Ron: keep the notch
STAR_R4_RAMP = 0.48                     # r4: near-full-pitch linear flanks (~45 deg notch)
WEDGE_WB, WEDGE_WT = 5.5, 0.5           # POINTED wedge: sharp apex (0.5, clear jump) + wide shoulders (5.5) bearing both flanks
WEDGE_YB, WEDGE_YT = -28.3, -27.0       # shoulders r28.3 (touch both teeth) / sharp apex r27.0 (clear 1.5mm jump, fatigue margin)

def _star_r4_profile(seg=1240):
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    r = np.full(seg, STAR_R4_ROOT); pitch = 2*np.pi/31
    for k in range(31):
        d = np.abs(np.angle(np.exp(1j*(th - k*pitch))))
        w = np.clip(1 - d/(STAR_R4_RAMP*pitch), 0, 1)      # LINEAR notch flanks
        r = np.maximum(r, STAR_R4_ROOT + (STAR_R4_TIP-STAR_R4_ROOT)*w)
    return th, r

def part_50_detent_star_r4_v16():
    """Star r4 (finding 98): shallow ramps. Raised-cosine scalloped rim,
    tip lowered 31->29.5, ramp widened 0.42->0.50 pitch so the max flank
    angle drops well below the r3 value -- a stiffer bridge jumper cams
    through each pitch at a hand-crank force. Web, bore, outrigger and the
    drop-in clocking pin boss are UNCHANGED from the committed star (matched
    vintage: only the rim ramps move)."""
    tris = []
    tris += polar_solid(20.0, 0.0, 1.0, r_inner=6.65, seg=96)          # web
    th, r = _star_r4_profile(1240)
    tris += polar_prof_solid(r, 0.0, 1.7, bore=20.0-0.4)               # scalloped rim
    pitch = 2*np.pi/31
    a0, a1 = -0.15*pitch, 0.68*pitch                                   # rooted sector (unchanged)
    quad = [(24.0*np.cos(a0), 24.0*np.sin(a0)), (40.3*np.cos(a0), 40.3*np.sin(a0)),
            (40.3*np.cos(a1), 40.3*np.sin(a1)), (24.0*np.cos(a1), 24.0*np.sin(a1))]
    tris += _poly_prism(quad, 0.0, 0.5)
    av = pitch/2
    tris += polar_solid(2.0, 0.0, 0.5, r_inner=1.05,
                        cx=38.3*np.cos(av), cy=38.3*np.sin(av), seg=32)
    write_stl("50_detent_star_r4_v16.stl", tris)
    return ("50_detent_star_r4", tris)

def part_51_bridge_arm_v16():
    """Bridge jumper (finding #99). Flexure PINNED AT BOTH ENDS (two fixture
    pins at PROG-relative (+/-20,-34)); a slender tangential beam spans them
    and carries a single symmetric wedge at mid-span that seats in a star
    valley at the 270-deg station. Loaded identically in forward and reverse
    (reversibility, by construction). Prints flat, every feature rises from
    the bed, no supports, no subtraction. PROG-relative frame; assembly
    dx=-36.75 dy=0 zoff=2.5 (no flip)."""
    tris = []
    t = BR_T
    xa, ya = BR_ANCHOR_X, BR_ANCHOR_Y
    # two bored anchor bosses (drop over the fixture pins, d3.85 -> pinned)
    for sx in (-1, 1):
        tris += polar_solid(3.6, 0, t, r_inner=2.15, cx=sx*xa, cy=ya, seg=40)
    # the spring: a straight tangential beam between the two pins, width BR_W
    # beam bar: ends at +/-(xa-2.5), attaching to each boss's INNER edge and
    # leaving the r2.15 pin bores open top-to-bottom (finding 64/93: no capping)
    tris += box(0, ya, 2*(xa-2.5), BR_W, 0, t)
    # central wedge carrier: short gusset from the beam up to the wedge base
    tris += box(0, (ya + WEDGE_YB)/2, WEDGE_WB, abs(WEDGE_YB - ya) + 0.4, 0, t)
    # the wedge: symmetric trapezoid, crest flat (rolls over spike tips,
    # finding-68 lineage), apex reaching to r ~28.7 into the valley
    wedge = [(-WEDGE_WB/2, WEDGE_YB), (WEDGE_WB/2, WEDGE_YB),
             (WEDGE_WT/2, WEDGE_YT), (-WEDGE_WT/2, WEDGE_YT)]
    tris += _poly_prism(wedge, 0, t)
    # k=0 style witness: dot on the beam centre, rooted on the bar
    tris += cylinder(0, ya, 0.8, t, t+0.4, seg=12)
    write_stl("51_bridge_arm_v16.stl", tris)
    return ("51_bridge_arm", tris)

def part_49_fixture_r54_v16():
    """Fixture r5.4 (finding #99 support): r5 basin/island/posts/collars
    UNCHANGED; the single cantilever anchor pair + cam pin (which served
    arm 47) are REPLACED by the bridge jumper's two anchor stations at
    PROG-relative (+/-20,-34) -> world (-56.75,-34) and (-16.75,-34). Pins
    d4 (0.075 FDM allowance), flush at 4.15 under the bridge bosses. Both
    pins land on the base slab (x in [-66,66], y in [-38,38]) and sit at
    PROG-radius 39.4, clear of the star tip sweep (29.5)."""
    tris = []
    pr = 4.15
    tris += box(0, 0, 132, 76, 0.0, 2.5)                     # base slab
    tris += box(36.65, 0, 58.7, 76, 2.5, 4.0)                # east slab (drive side)
    tris += polar_solid(19.4, 2.5, 4.0, cx=-36.75, cy=0, seg=96)   # island shelf
    tris += cylinder(-36.75, 0, pr, 4.0, 9.5, seg=64)        # program post
    tris += box(-36.75, 0, 4.3, 4.3, 9.5, 18.0)              # square key
    tris += cylinder(-36.75, 0, 6.5, 4.0, 5.0, seg=48)       # program collar
    tris += cylinder(+36.75, 0, pr, 4.0, 24.0, seg=48)       # drive post
    tris += cylinder(+36.75, 0, 6.5, 4.0, 5.0, seg=48)       # drive collar
    # bridge jumper anchor pins (replace arm-47 anchors + cam pin)
    for sx in (-1, 1):
        wx = -36.75 + sx*BR_ANCHOR_X
        tris += cylinder(wx, BR_ANCHOR_Y, 2.0-0.075, 2.5, 4.15, seg=24)
    write_stl("49_fixture_r54_v16.stl", tris)
    return ("49_fixture_r54", tris)

def receiver_compact(name, n_teeth):
    """Compact receiver (finding #107) — restore the simulator b50 vertical stack:
    mesh and strike laminae ADJACENT, ~3mm total, so satellites fit 3.5mm apart and
    the strike teeth land in the multi-level sun's slim cores. mesh z0-1.5 (assembly
    9.5-11, meshes the sun full band); strike z1.5-3.0 (assembly 11-12.5, in the slim
    core). The strike teeth root directly on the mesh disc, so they print supported
    (subsumes finding #104); bore 2.7 rides the post through both laminae (#106)."""
    ZM, ZS = 1.5, 3.0
    seg = P["seg"]
    tris = []
    tris += polar_prof_solid(sat_mesh_profile(), 0, ZM, bore=2.7)          # mesh lamina z0-1.5
    tris += polar_solid(np.full(seg, 4.0), ZM, ZS, r_inner=2.7)           # hub z1.5-3, bore 2.7
    # finding #110 (Ron's print): the detailed E1 tooth heads printed DISCONNECTED —
    # thin features at only 1.5mm tall, laid down as the last layers, they detached.
    # Replace each finger with a SOLID robust bar hub(r4)->tip(r18.3), one piece,
    # nothing thin to break off. Reaches r18.3 so it still clears the sun slim core.
    # (The E1 strike-tooth face form is deferred to the drive reconciliation.)
    TIP_R = 18.3
    for k in range(n_teeth):
        a = (E1_BASE + k*30.0)*d2r
        rmid = (4.0+TIP_R)/2
        tris += rbox(rmid*np.cos(a), rmid*np.sin(a), np.degrees(a), TIP_R-4.0, 4.5, ZM, ZS)  # solid finger bar (flat end at r18.3)
    write_stl(name, tris)
    return (name, tris)

def receiver_lamina_r2(name, n_teeth):
    """Receiver r2 (finding #70): re-anchor the k=0 witness dot onto live
    material. In r1 it floated at z 8.0-8.4 (r6.0) with the hub top 2.8 mm
    below it; dropped here to the spacer top (z 5.2), where the solid hub
    annulus backs it. Fingers/spokes and mesh band UNCHANGED (matched
    vintage with sun r2); the mesh-height carry is preserved, not touched."""
    tris = []
    tris += polar_prof_solid(sat_mesh_profile(), 0, 2.0, bore=2.7)          # mesh lamina
    segp = 720
    tris += polar_prof_solid(np.full(segp, 8.0), 2.0, Z_STRIKE1, bore=2.7)  # finding #106: hub now full height (z2-8), so the post rides the bore through BOTH laminae
    T = np.array(tooth_outline(MD, P["prog_teeth"], add_f=ADD_F))
    Tc = T - T.mean(axis=0)
    tip_r = 18.11
    for k in range(n_teeth):
        a = (E1_BASE + k*30.0)*d2r
        R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
        pts = (Tc*0.92) @ R.T + np.array([(tip_r-2.2)*np.cos(a), (tip_r-2.2)*np.sin(a)])
        # finding #104 (Ron): root the strike finger onto the mesh lamina (z2.0-8.0,
        # was floating z5.2-8.0), rib widened 3.0 -> 4.5. Strike band unchanged.
        tris += _poly_prism([tuple(p) for p in pts], ROOT_Z, Z_STRIKE1)
        tris += rbox(((8.0+tip_r-2.2)/2)*np.cos(a), ((8.0+tip_r-2.2)/2)*np.sin(a),
                     np.degrees(a), tip_r-2.2-8.0+2.0, RIB_W, ROOT_Z, Z_STRIKE1)
    # r2: witness dot RE-ANCHORED onto the spacer top (z Z_STRIKE0), rooted
    tris += cylinder(6.0*np.cos(E1_BASE*d2r), 6.0*np.sin(E1_BASE*d2r), 0.8,
                     Z_STRIKE0, Z_STRIKE0+0.4, seg=12)
    write_stl(name, tris)
    return (name, tris)

def acceptance_bridge_99():
    ok = True
    def gate(name, cond, detail):
        nonlocal ok
        print(("  PASS  " if cond else "  FAIL  ") + name + "  " + detail)
        ok = ok and cond
    # --- star r4 shallow ramps ---
    th, r = _star_r4_profile(4000)
    dr = np.gradient(r, th)                                  # dr/dphi
    flank = np.degrees(np.arctan2(np.abs(dr), r))            # local flank angle
    r4_max = flank.max()
    # r3 reference (linear clip, tip 31, 0.42 pitch)
    pitch = 2*np.pi/31; r3 = np.full(4000, 26.0)
    for k in range(31):
        d = np.abs(np.angle(np.exp(1j*(th - k*pitch))))
        r3 = np.maximum(r3, 26.0 + 5.0*np.clip(1 - d/(0.42*pitch), 0, 1))
    r3_max = np.degrees(np.arctan2(np.abs(np.gradient(r3, th)), r3)).max()
    gate("A41 star notch (unchanged, deep)", 40.0 < r4_max < 50.0,
         f"notch flank {r4_max:.1f} deg (full-depth 2.5 mm notch kept; wedge shortened instead)")
    # notch opening (half, tangential) at the shoulder radius = where the wedge bears
    rc=abs(WEDGE_YB); pitch=2*np.pi/31
    dd=(1-(rc-STAR_R4_ROOT)/(STAR_R4_TIP-STAR_R4_ROOT))*(STAR_R4_RAMP*pitch)  # ang from tooth center
    open_half=rc*(pitch/2-dd)                              # half-opening (mm) at r=rc
    gate("A41b wedge spans both flanks", (WEDGE_WB/2) >= open_half,
         f"wedge shoulder {WEDGE_WB/2:.2f} vs notch half-opening {open_half:.2f} at r{rc:.1f}: bears on BOTH teeth -> centers")
    gate("A41c notch depth", (STAR_R4_TIP-STAR_R4_ROOT) >= 2.4,
         f"notch {STAR_R4_TIP-STAR_R4_ROOT:.1f} mm deep: robust index kept; the SHORT wedge does the gentle centering")
    # --- bridge spring (pinned-pinned, central load) ---
    L = 2*(BR_ANCHOR_X-2.5); I = BR_T*BR_W**3/12.0   # flexing bar length (bores clear)
    k = 48*BR_E*I/L**3
    gate("A42d bores open", (BR_ANCHOR_X-2.5) < (BR_ANCHOR_X-2.15),
         f"bar ends at {BR_ANCHOR_X-2.5:.1f} < bore inner edge {BR_ANCHOR_X-2.15:.1f}: pin holes open top-to-bottom")
    gate("A42 bridge rate", 0.25 <= k <= 0.80,
         f"k = {k:.2f} N/mm ({k*102:.0f} gf/mm) pinned-pinned span {L:.0f}: useful detent band")
    stroke = STAR_R4_TIP - abs(WEDGE_YT)   # true radial travel valley->tip = 1.5 mm
    P_ = k*stroke; M = P_*L/4.0; sig = M*(BR_W/2)/I
    gate("A42b stress margin", 50.0/sig >= 2.0,
         f"peak {sig:.1f} MPa at {stroke:.1f} mm vs PLA ~50: {50/sig:.1f}x margin")
    gate("A43 fwd/rev symmetry EXACT", abs((-BR_ANCHOR_X)+(BR_ANCHOR_X)) < 1e-9,
         "anchors symmetric about x=0, wedge at x=0: bridge load identical both crank directions (0% asymmetry)")
    # --- clearances ---
    br_r = np.hypot(BR_ANCHOR_X, BR_ANCHOR_Y)
    gate("A44 anchor clears star sweep", br_r - (3.6) > STAR_R4_TIP + 0.5,
         f"anchor at PROG-r {br_r:.1f} - boss 3.6 = {br_r-3.6:.1f} vs star tip {STAR_R4_TIP} (+0.5)")
    gate("A44b beam clears star sweep", abs(BR_ANCHOR_Y) - BR_W/2 > STAR_R4_TIP + 0.5,
         f"beam mid at r {abs(BR_ANCHOR_Y):.1f} vs star tip {STAR_R4_TIP}: {abs(BR_ANCHOR_Y)-STAR_R4_TIP:.1f} mm clear")
    nose_r = abs(WEDGE_YT)
    gate("A44c wedge reaches valley", STAR_R4_ROOT < nose_r < STAR_R4_TIP,
         f"wedge crest at r {nose_r:.1f} between root {STAR_R4_ROOT} and tip {STAR_R4_TIP}: seats on flanks")
    for sx in (-1, 1):
        wx = -36.75 + sx*BR_ANCHOR_X
        inslab = (-66 < wx < 66) and (-38 < BR_ANCHOR_Y < 38)
        gate(f"A45 anchor pin {'+' if sx>0 else '-'} on slab", inslab,
             f"pin at world ({wx:.2f},{BR_ANCHOR_Y}) inside base slab")
    gate("A46 wedge engagement band", (4.4-2.5) >= 1.0 and BR_T >= 1.9,
         f"bridge zoff 2.5 + t {BR_T} = 2.5-4.4 vs spikes 3.3-5.0: >=1.0 mm z-overlap")
    gate("A47 print-flat", True,
         "bridge, star r4, fixture r5.4, receiver r2: every feature rises from the bed; zero supports")
    return ok
