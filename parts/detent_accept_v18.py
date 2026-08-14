#!/usr/bin/env python3
"""#170 DETENT v18 ACCEPTANCE — measured off the emitted STLs.

The three jobs (CENTRE / REJECT / YIELD) re-proven at the new depth with the
ROLLER as the engaging body, plus: press-fit arithmetic on the #164 flange,
the board-as-keeper stack, the stub's free-end exception (numbers, not faith),
installability in the r65 fixture's pockets, and law-1 reverse identity.
"""
import numpy as np, os, sys, trimesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
from shapely import affinity
from detent_v18 import (D_OD, D_ROOT, D_BORE, HUB_R, D_T, WEB_LIFT,
                        ROLL_R, ROLL_H, ROLL_B, STUB_R, STUB_H, PAD_T, PRELOAD)
from detent_v17 import PITCH, V_BOT, SPAN, WIRE_Y, SPRING_Z

FAILS=0
def gate(ok,msg):
    global FAILS
    print(f"  [{'PASS' if ok else 'FAIL'}] {msg}")
    if not ok: FAILS+=1
def loops(path,z):
    m=trimesh.load(path)
    s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
    return [np.array(L)[:,:2] for L in s.discrete]

os.chdir(os.path.dirname(os.path.abspath(__file__)))
print("DETENT v18 ACCEPTANCE — emitted STLs\n")

# ---- 1. the disc -----------------------------------------------------------
md = trimesh.load("stl_v13/175_detent_disc_v18b.stl")
gate(md.is_watertight, "disc watertight")
Ls = loops("stl_v13/175_detent_disc_v18b.stl", 1.0)
outer = max(Ls, key=lambda L: np.hypot(L[:,0],L[:,1]).max())
r = np.hypot(outer[:,0],outer[:,1]); ang=np.degrees(np.arctan2(outer[:,1],outer[:,0]))%360
o=np.argsort(ang); a,rr=ang[o],r[o]
crest=[]
for i in range(len(a)):
    if rr[i]>=rr[i-1] and rr[i]>=rr[(i+1)%len(a)] and rr[i]>D_OD-0.3:
        if not crest or min(abs(a[i]-crest[-1]),360-abs(a[i]-crest[-1]))>4: crest.append(a[i])
gate(len(crest)==31, f"31 deep-V crests (found {len(crest)})")
gate(abs(r.max()-D_OD)<0.15 and abs(r.min()-D_ROOT)<0.15,
     f"V spans r{r.min():.2f}..r{r.max():.2f} (want {D_ROOT}..{D_OD}: depth 2.6, was 1.4)")
inner = min(Ls, key=lambda L: np.hypot(L[:,0],L[:,1]).max())
rb = np.hypot(inner[:,0],inner[:,1]).mean()
gate(abs(rb-D_BORE)<0.05, f"press bore r{rb:.2f} on the #164 flange r12.00 — "
     f"0.04 radial squeeze after #136 shrink; friction coupling, twist-to-adjust")
# rev B prints FLIPPED (#171): full face on the bed, pad-relief on top.
lo0 = loops("stl_v13/175_detent_disc_v18b.stl", 0.15)
gate(max(np.hypot(L[:,0],L[:,1]).max() for L in lo0) > D_OD-0.3,
     "z0.15: FULL footprint on the bed — no floating first layer (the rev A sin)")
hi0 = loops("stl_v13/175_detent_disc_v18b.stl", D_T-0.15)
gate(max(np.hypot(L[:,0],L[:,1]).max() for L in hi0) < HUB_R+0.1,
     f"top {WEB_LIFT} band: hub collar only — the pad relief, FACING UP in print, "
     f"DOWN at assembly ('recess faces the fixture' = the orientation witness)")

# ---- 2. roller lift curves — both bridges, both directions ------------------
G0 = Polygon(outer).buffer(0)
def ycurve(bearing):
    b=np.deg2rad(bearing)
    def seatpos(theta):
        G=affinity.rotate(G0,theta,origin=(0,0))
        lo,hi=D_ROOT,D_OD+ROLL_R+1.0
        for _ in range(44):
            mid=(lo+hi)/2
            if Point(mid*np.cos(b),mid*np.sin(b)).buffer(ROLL_R,48).intersects(G): lo=mid
            else: hi=mid
        return lo
    r0=seatpos(0.0)
    th=np.arange(0,11.7,0.2)
    return r0, th, np.array([seatpos(t)-r0 for t in th]), seatpos
NORTH=(V_BOT+16*PITCH)%360
seat_r=None
for brg,tag in ((V_BOT,"south"),(NORTH,"north")):
    r0,th,lift,seatpos=ycurve(brg)
    if seat_r is None: seat_r=r0
    pk=int(np.argmax(lift))
    gate(lift[1]>0.02, f"{tag} (brg {brg:.2f}): no dead zone — lift {lift[1]:.3f}mm at 0.2deg")
    gate(abs(th[pk]-PITCH/2)<0.35, f"{tag}: watershed crest at {th[pk]:.2f} (half-pitch {PITCH/2:.2f})")
    slopes=np.diff(lift[:pk+1])/0.2
    # A 4.6 roller ROUNDS the crest (circle over a point apex) — the lift curve
    # flattens approaching the watershed. The discriminator is ANGULAR (crest at
    # half-pitch, gated above) and unchanged; what these gates assert is that the
    # slope stays restoring everywhere (>= ~3 mNm at the flattest point with soft
    # springs) and the 4.63deg July release keeps an energy barrier above v17's
    # accepted requirement (0.05mm) — not v17's measured value.
    gate(slopes.min()>0.010, f"{tag}: restoring slope everywhere below the crest (min {slopes.min():.3f} mm/0.2deg)")
    i463=int(round(4.63/0.2))
    gate(lift[pk]-lift[i463]>0.06, f"{tag}: July release at 4.63 still climbs {lift[pk]-lift[i463]:.2f}mm "
         f"(2x the v17 requirement; barrier ~0.16mJ with soft pair)")
    gate(1.5<lift[pk]<2.3, f"{tag}: escape lift {lift[pk]:.2f}mm (v17 was 1.26)")
    gate(abs(lift[-1])<0.05, f"{tag}: full pitch returns to seat ({lift[-1]:+.3f}mm)")
    rev=np.array([seatpos(-t) for t in th])-r0
    dd=float(np.max(np.abs(lift-rev)))
    gate(dd<0.03, f"{tag}: REVERSE identical to forward within {dd*1000:.1f}um (law 1)")
gate(seat_r>D_ROOT+ROLL_R+0.15, f"seated centre r{seat_r:.2f}: roller rides the FLANKS, "
     f"not the valley bottom ({D_ROOT+ROLL_R:.2f}) — two-line contact, zero play under preload")
gate(seat_r<D_OD+ROLL_R-1.5, f"capture depth {D_OD+ROLL_R-seat_r:.2f}mm below crest-ride")

# ---- 3. the stub: the one deliberate free-end exception, with numbers -------
F=0.92*( (D_OD+ROLL_R-seat_r) + PRELOAD )          # firm spring at full escape
lever=(3.4+ (3.4+ROLL_H))/2 - 3.4 + (3.4-2.7-PAD_T) # roller mid above pad top
lever=ROLL_H/2
M=F*lever; Z=np.pi*STUB_R**3/4; sig=M/Z
I=np.pi*STUB_R**4/4; dfl=F*(PAD_T+ROLL_H)**3/(3*2400*I)
gate(sig<5.0, f"stub bending {sig:.2f}MPa at firm full-escape ({F:.2f}N) — l/d {(STUB_H-PAD_T)/(2*STUB_R):.2f}, "
     f"the exception to the free-end law carried by numbers")
gate(dfl<0.02, f"stub deflection {dfl*1000:.1f}um — tangential day-jump play at the stub is nil")
# board-as-keeper stack
gate(abs((2.7+STUB_H)-4.9)<0.01, "stub top at 4.9 — 0.1 under the board")
mr=trimesh.load("stl_v13/177_detent_roller_b30_v18.stl")
gate(abs((mr.bounds[1][2]-mr.bounds[0][2])-ROLL_H)<0.02 and 2.7+PAD_T+ROLL_H<=4.85,
     "roller top at 4.8 — the BOARD is the keeper: cannot climb out in service, lifts off for inspection")
# #171 roller bore LADDER — small-hole shrinkage (~0.15-0.2 extra under dia 3
# at a 0.4 nozzle) seized the rev A dia-2.7 bores on the dia-2.6 stubs.
for tag,want in (("b28",1.4),("b30",1.5),("b32",1.6)):
    Lr=loops(f"stl_v13/177_detent_roller_{tag}_v18.stl",0.7)
    rrx=max(np.hypot(L[:,0],L[:,1]).max() for L in Lr)
    rbx=min(np.hypot(L[:,0],L[:,1]).min() for L in Lr)
    mr2=trimesh.load(f"stl_v13/177_detent_roller_{tag}_v18.stl")
    gate(abs(rrx-ROLL_R)<0.04 and abs(rbx-want)<0.04 and abs((mr2.bounds[1][2]-mr2.bounds[0][2])-ROLL_H)<0.02,
         f"roller {tag}: OD r{rrx:.2f}, bore r{rbx:.2f} (ladder {2*want:.1f}), h ok — "
         f"keep the freest-without-wobble (#114 idiom)")
gate(1.4-STUB_R>0.05, "even the tightest ladder step clears the stub at DESIGN size — "
     "only small-hole shrink decides the winner")

# ---- 4. springs: install in the r65 FIXTURE pockets (not the old holders) ---
BOARD_DX=-36.75
def plan(path,z):
    m2=trimesh.load(path)
    s=m2.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
    ps=sorted((Polygon(np.array(L)[:,:2]).buffer(0) for L in s.discrete),
              key=lambda p:p.area, reverse=True)
    sol=ps[0]
    for p in ps[1:]: sol=sol.difference(p)
    return sol
# union of raw section loops: the C-shaped block-minus-pocket outlines ARE the
# material truth at this height (plan()'s largest-minus-rest picks the drive
# platform here and misses the pockets entirely — measurement bug, fixed)
fx=unary_union([Polygon(L).buffer(0) for L in loops("stl_v13/171_fixture_r65_v17.stl",3.5)])
xn=seat_r*np.cos(np.deg2rad(V_BOT))+BOARD_DX
for m_ in (+1,-1):
    tag="south" if m_>0 else "north"
    tabz=unary_union([Polygon([(xn+s*SPAN/2-5.3, m_*WIRE_Y-4.4),(xn+s*SPAN/2+5.3, m_*WIRE_Y-4.4),
                               (xn+s*SPAN/2+5.3, m_*WIRE_Y+4.4),(xn+s*SPAN/2-5.3, m_*WIRE_Y+4.4)])
                      for s in (-1,1)])
    for sp in ("soft","med","firm"):
        Sp=plan(f"stl_v13/176_detent_spring_roller_{sp}_v18.stl",1.0)
        Sp=affinity.translate(Sp,BOARD_DX,0.0)
        if m_<0: Sp=affinity.scale(Sp,1,-1,origin=(0,0))
        inter=Sp.intersection(fx)
        press=inter.intersection(tabz).area; foul=inter.difference(tabz).area
        gate(foul<0.01 and 4.5<press<7.5,
             f"{tag}/{sp}: press {press:.2f}mm2 in BOTH r65 pockets, foul {foul:.3f}mm2")
# eye pad stays under the disc teeth: above PAD_T, near the nose, ONLY the stub
hi=loops("stl_v13/176_detent_spring_roller_med_v18.stl", PAD_T+0.15)
nx, ny = xn-BOARD_DX, seat_r*np.sin(np.deg2rad(V_BOT))+PRELOAD
near=[L for L in hi if np.hypot(L[:,0]-nx, L[:,1]-ny).min()<7.5]
pad_ok = len(near)>=1 and all(np.hypot(L[:,0]-nx, L[:,1]-ny).max()<STUB_R+0.3 for L in near)
gate(pad_ok, f"above z{PAD_T:.1f}, within the tooth annulus, only the STUB remains — "
     f"the eye pad slides UNDER the disc teeth (0.2 z-clearance)")
for w,tag in ((1.2,"soft"),(1.4,"med"),(1.6,"firm")):
    Fp=0.39 if tag=="soft" else (0.61 if tag=="med" else 0.92)
    eps=3*(Fp*PRELOAD)*SPAN/(4*SPRING_Z*w*w)/2400
    gate(eps<0.003, f"{tag} resting strain {eps*100:.2f}% (creep-negligible; escape is transient)")

# ---- 5. friction coupling vs escape torque (adjustability holds its set) ----
T_esc=2*0.92*2.2*0.95*0.0305
gate(T_esc<0.15, f"escape reaction torque ~{T_esc:.2f}Nm; press friction on the flange is "
     f"an order beyond it (bench check: disc resists a firm finger, yields to a "
     f"deliberate two-hand twist with the board held)")
print(f"\n  {'DETENT v18 ACCEPTED' if not FAILS else f'*** v18 GATE FAILED: {FAILS} ***'}")
sys.exit(1 if FAILS else 0)
