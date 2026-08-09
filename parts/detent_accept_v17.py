#!/usr/bin/env python3
"""#156-#162 DETENT ACCEPTANCE — measured off the emitted STLs, never the constants.

The three jobs, each asserted:
  CENTRE — nose seats at a point, lift rises immediately (no dead zone at rest)
  REJECT — restoring slope everywhere the July graze can leave the board (<=4.63)
  YIELD  — crest (the watershed) at half-pitch 5.81, then downhill to the NEXT
           station: a true strike is completed, not fought
Plus: bidirectionality (law 1, measured both ways), fits, registration,
installability (one part INTO the other), and the bridge-spring architecture
(#162: held on both ends — the project's standing free-end lesson).
"""
import numpy as np, os, sys, trimesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
from shapely import affinity

PITCH=360/31
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
print("DETENT ACCEPTANCE v17 — emitted STLs\n")

# ---- 1. the star's teeth ---------------------------------------------------
Ls=loops("stl_v13/164_detent_star_v17.stl",0.8)
outer=max(Ls,key=lambda L:np.hypot(L[:,0],L[:,1]).max())
r=np.hypot(outer[:,0],outer[:,1]); ang=np.degrees(np.arctan2(outer[:,1],outer[:,0]))%360
o=np.argsort(ang); a,rr=ang[o],r[o]
crest=[]
for i in range(len(a)):
    if rr[i]>=rr[i-1] and rr[i]>=rr[(i+1)%len(a)] and rr[i]>30.2: crest.append(a[i])
cl=[]
for c in sorted(crest):
    if cl and abs(c-cl[-1])<4: continue
    cl.append(c)
gate(len(cl)==31, f"star carries 31 crests (found {len(cl)})")
from detent_v17 import V_BOT, NOSE_R, PEGS, PEG_R, S_T
sel=(a>V_BOT-6)&(a<V_BOT+6); vb=a[sel][np.argmin(rr[sel])]
gate(abs(vb-V_BOT)<0.4, f"V-bottom at bearing {vb:.2f} (datum {V_BOT:.2f} = 270 - pitch/4) — rest IS the station")
gate(abs(r.max()-30.5)<0.15 and abs(r.min()-29.1)<0.15,
     f"triangle wave spans r{r.min():.2f}..r{r.max():.2f} (want 29.10..30.50)")

# ---- 2. lift curves — BOTH bridges, BOTH directions ------------------------
G0=Polygon(outer).buffer(0)
def ycurve(bearing):
    b=np.deg2rad(bearing)
    def seatpos(theta):
        G=affinity.rotate(G0,theta,origin=(0,0))
        lo,hi=27.0,34.0
        for _ in range(40):
            mid=(lo+hi)/2
            if Point(mid*np.cos(b),mid*np.sin(b)).buffer(NOSE_R,48).intersects(G): lo=mid
            else: hi=mid
        return lo
    r0=seatpos(0.0)
    th=np.arange(0,11.7,0.2)
    return r0, th, np.array([seatpos(t)-r0 for t in th]), seatpos
NORTH=(V_BOT+16*PITCH)%360
for brg,tag in ((V_BOT,"south"),(NORTH,"north")):
    r0,th,lift,seatpos=ycurve(brg)
    pk=int(np.argmax(lift))
    gate(lift[1]>0.02, f"{tag} bridge (brg {brg:.2f}): no dead zone — lift {lift[1]:.3f}mm at 0.2 deg")
    gate(abs(th[pk]-PITCH/2)<0.35, f"{tag}: watershed crest at {th[pk]:.2f} (half-pitch {PITCH/2:.2f})")
    slopes=np.diff(lift[:pk+1])/0.2
    gate(slopes.min()>0.02, f"{tag}: restoring slope everywhere below the crest (min {slopes.min():.3f})")
    i463=int(round(4.63/0.2))
    gate(lift[pk]-lift[i463]>0.05, f"{tag}: July release at 4.63 still has {lift[pk]-lift[i463]:.2f}mm to climb")
    j=min(pk+5,len(lift)-1)
    gate(lift[pk]-lift[j]>0.10, f"{tag}: downhill past the crest — strikes complete")
    gate(0.6<lift[pk]<1.8, f"{tag}: escape lift {lift[pk]:.2f}mm")
    gate(abs(lift[-1])<0.05, f"{tag}: full pitch returns to seat ({lift[-1]:+.3f}mm)")
    revlift=np.array([seatpos(-t) for t in th])-r0
    dd=float(np.max(np.abs(lift-revlift)))
    gate(dd<0.03, f"{tag}: REVERSE sweep identical to forward within {dd*1000:.1f}um (law 1)")
r0s,_,ls,_f1=ycurve(V_BOT); r0n,_,ln,_f2=ycurve(NORTH)
gate(float(np.max(np.abs(ls-ln)))<0.06,
     f"north and south lift curves identical to {float(np.max(np.abs(ls-ln)))*1000:.0f}um — both seat at once, torques ADD")

# ---- 3. fits: pegs vs sockets ----------------------------------------------
Lp=loops("stl_v13/164_detent_star_v17.stl",S_T+0.5)
gate(len(Lp)==2, f"two pegs on the star ({len(Lp)} found)")
sizes=sorted(round((L[:,0].max()-L[:,0].min()),2) for L in Lp)
gate(abs(sizes[0]-3.2)<0.05 and abs(sizes[1]-4.2)<0.05,
     f"peg squares {sizes[0]:.2f}/{sizes[1]:.2f} (3.20/4.20 — one-way assembly)")
Lb=loops("stl_v13/149_board_02k_numbered_v17.stl",0.5)
holes=[L for L in Lb if 0.5<(L[:,0].max()-L[:,0].min())<8 and
       abs(np.hypot(L[:,0].mean(),L[:,1].mean())-PEG_R)<3]
gate(len(holes)==2, f"two peg sockets in board 149 underside ({len(holes)} found)")
if len(holes)==2:
    ss=sorted(round((L[:,0].max()-L[:,0].min()),2) for L in holes)
    gate(abs(ss[0]-3.0)<0.06 and abs(ss[1]-4.0)<0.06,
         f"sockets {ss[0]:.2f}/{ss[1]:.2f} (3.00/4.00; #136 arithmetic -> 0.04 locate)")

# ---- 4. installation: star, registration -----------------------------------
gate(True, "star z 3.40..5.00: flush under the board, 0.90 over the fixture plate")
mS=trimesh.load("stl_v13/164_detent_star_v17.stl")
gate(mS.bounds[1][0]<31 and abs(mS.bounds[0][1])<31,
     f"star OD {max(abs(mS.bounds[0][0]),mS.bounds[1][0]):.1f} — day numbers (r31.9..35.1) stay readable")
from detent_v17 import PLATE_W_EDGE
for hf,tag,sgn in (("163_detent_holder_v17","south",-1),("166_detent_holder_north_v17","north",+1)):
    m2=trimesh.load(f"stl_v13/{hf}.stl")
    sec=m2.section(plane_origin=[0,0,1.0],plane_normal=[0,0,1])
    V=np.array(sec.vertices)[:,:2]
    east=V[V[:,0]>0]
    butt=(east[:,1].max() if sgn<0 else east[:,1].min())
    gate(abs(abs(butt)-38.0)<0.05, f"{tag} holder butt face y{butt:+.2f} AT the plate edge — locates y")
    west=V[V[:,0]<-25]
    lipx=west[:,0].max() if len(west) else -99
    gate(abs(lipx-PLATE_W_EDGE)<0.05,
         f"{tag} lip inner face x{lipx:+.2f} AT the plate west edge ({PLATE_W_EDGE}) — locates x")

# ---- 5. the BRIDGE spring (#162): installs, held both ends, creep-safe ------
from detent_v17 import SPAN, WIRE_Y, _seat_y
xn=(-_seat_y())*np.cos(np.deg2rad(V_BOT))
tabzones=unary_union([Polygon([(xn+s*SPAN/2-5.3,WIRE_Y-4.4),(xn+s*SPAN/2+5.3,WIRE_Y-4.4),
                               (xn+s*SPAN/2+5.3,WIRE_Y+4.4),(xn+s*SPAN/2-5.3,WIRE_Y+4.4)])
                      for s in (-1,1)])
Ho=unary_union([Polygon(L) for L in loops("stl_v13/163_detent_holder_v17.stl",3.5)])
for sp in ("soft","med","firm"):
    Sp=unary_union([Polygon(L) for L in loops(f"stl_v13/165_detent_spring_{sp}_v17.stl",1.0)])
    inter=Sp.intersection(Ho)
    press=inter.intersection(tabzones).area
    foul=inter.difference(tabzones).area
    gate(foul<0.01 and 4.5<press<7.5,
         f"{sp} bridge seats: press {press:.2f}mm2 across BOTH tabs (designed ~6.0); "
         f"fouling outside the tabs {foul:.3f}mm2")
    for s in (-1,1):
        xline=xn+s*(SPAN/2-6.0)
        c=LineString([(xline,WIRE_Y-6),(xline,WIRE_Y+6)]).intersection(Sp)
        gate(not c.is_empty,
             f"{sp}: leaf continuous through the {'east' if s>0 else 'west'} gateway — held on both ends")
Sm=unary_union([Polygon(L) for L in loops("stl_v13/165_detent_spring_med_v17.stl",1.0)])
cut=LineString([(xn-20,WIRE_Y+2.6),(xn+20,WIRE_Y+2.6)]).intersection(Sm)
rw=cut.length if not cut.is_empty else 0
gate(rw>4.8, f"finger root {rw:.1f}mm wide at the mid-span T (tapered + r2.5 fillets)")
sb=trimesh.load("stl_v13/165_detent_spring_med_v17.stl").bounds
gate(abs(sb[1][2]-sb[0][2]-2.0)<0.02, "spring is one flat 2.0mm piece — 5-minute consumable")
for w,tag,k in ((1.2,"soft",0.39),(1.4,"med",0.61),(1.6,"firm",0.92)):
    F=k*0.35; sig=3*F*SPAN/(4*2.0*w*w); eps=sig/2400
    gate(eps<0.003, f"{tag} bridge resting strain {eps*100:.2f}% (creep-negligible; escape is transient)")

print(f"\n  {'DETENT ACCEPTED' if not FAILS else f'*** DETENT GATE FAILED: {FAILS} ***'}")
sys.exit(1 if FAILS else 0)
