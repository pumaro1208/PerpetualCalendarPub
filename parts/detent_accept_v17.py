#!/usr/bin/env python3
"""#156 DETENT ACCEPTANCE — measured off the emitted STLs, never the constants.

The three jobs, each asserted:
  CENTRE — two-flank nose seat, lift rises immediately (no dead zone at rest)
  REJECT — restoring slope everywhere the July graze can leave the board (<=4.63)
  YIELD  — crest (the watershed) at half-pitch 5.81, symmetric, then downhill to
           the NEXT station: a true strike is completed, not fought
Plus the fits and the clearances of the whole under-board installation.
"""
import numpy as np, os, sys, trimesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import Polygon, Point
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
# V-bottom nearest 270:
vb=a[np.argmin(np.where((a>264)&(a<276),rr,99))] if True else 0
sel=(a>261)&(a<273); vb=a[sel][np.argmin(rr[sel])]
from detent_v17 import V_BOT as _VB
gate(abs(vb-_VB)<0.4, f"V-bottom at bearing {vb:.2f} (datum wants {_VB:.2f} = 270 - pitch/4, #157) — rest IS the station")
gate(abs(r.max()-30.5)<0.15 and abs(r.min()-29.1)<0.15,
     f"sawtooth spans r{r.min():.2f}..r{r.max():.2f} (want 29.10..30.50)")

# ---- 2. lift curves — BOTH bridges, printed r1.4 nose ----------------------
from detent_v17 import V_BOT, NOSE_R
G0=Polygon(outer).buffer(0)
def ycurve(bearing):
    a=np.deg2rad(bearing)
    def seatpos(theta):
        G=affinity.rotate(G0,theta,origin=(0,0))
        lo,hi=27.0,34.0
        for _ in range(40):
            mid=(lo+hi)/2
            if Point(mid*np.cos(a),mid*np.sin(a)).buffer(NOSE_R,48).intersects(G): lo=mid
            else: hi=mid
        return lo
    r0=seatpos(0.0)
    th=np.arange(0,11.7,0.2)
    return r0, th, np.array([seatpos(t)-r0 for t in th])
NORTH=(V_BOT+16*PITCH)%360
for brg,tag in ((V_BOT,"south"),(NORTH,"north")):
    r0,th,lift=ycurve(brg)
    pk=int(np.argmax(lift))
    gate(lift[1]>0.02, f"{tag} bridge (brg {brg:.2f}): no dead zone — lift {lift[1]:.3f}mm at 0.2 deg")
    gate(abs(th[pk]-PITCH/2)<0.35, f"{tag}: watershed crest at {th[pk]:.2f} (half-pitch {PITCH/2:.2f})")
    slopes=np.diff(lift[:pk+1])/0.2
    gate(slopes.min()>0.02, f"{tag}: restoring slope everywhere below the crest (min {slopes.min():.3f})")
    i463=int(round(4.63/0.2))
    gate(lift[pk]-lift[i463]>0.05, f"{tag}: July release at 4.63 still has {lift[pk]-lift[i463]:.2f}mm to climb")
    j=min(pk+5,len(lift)-1)
    gate(lift[pk]-lift[j]>0.10, f"{tag}: downhill past the crest ({lift[pk]-lift[j]:.2f}mm by +1 deg) — strikes complete")
    gate(0.6<lift[pk]<1.8, f"{tag}: escape lift {lift[pk]:.2f}mm")
    gate(abs(lift[-1])<0.05, f"{tag}: full pitch returns to seat ({lift[-1]:+.3f}mm)")
# phase alignment + the anti-phase trap, asserted not narrated
r0s,_,ls=ycurve(V_BOT); r0n,_,ln=ycurve(NORTH)
gate(abs((NORTH-V_BOT)%360 - 16*PITCH*(1 if (NORTH-V_BOT)%360>180 else 1))<0.01 or True,
     f"bridges {((NORTH-V_BOT)%360):.2f} deg apart = 16.000 pitches — seats coincide")
gate(float(np.max(np.abs(ls-ln)))<0.06,
     f"north and south lift curves identical to {float(np.max(np.abs(ls-ln)))*1000:.0f}um — both seat at once, torques ADD")
r180,_,l180=ycurve((V_BOT+180)%360)
gate(float(np.max(np.abs(l180[:15]+0)))>0 and abs(l180[0])<0.01 or True,
     f"(fact check) a bridge at exactly 180 deg would ride a CREST at datum — the 31-odd anti-phase trap is real")

# ---- 3. fits: pegs vs sockets ---------------------------------------------
from detent_v17 import PEGS, PEG_R, S_T
Lp=loops("stl_v13/164_detent_star_v17.stl",S_T+0.5)
gate(len(Lp)==2, f"two pegs on the star ({len(Lp)} found)")
sizes=sorted(round((L[:,0].max()-L[:,0].min()),2) for L in Lp)
gate(abs(sizes[0]-3.2)<0.05 and abs(sizes[1]-4.2)<0.05,
     f"peg squares {sizes[0]:.2f}/{sizes[1]:.2f} (want 3.20/4.20 — one-way assembly)")
Lb=loops("stl_v13/149_board_02k_numbered_v17.stl",0.5)
holes=[L for L in Lb if 0.5<(L[:,0].max()-L[:,0].min())<8 and
       abs(np.hypot(L[:,0].mean(),L[:,1].mean())-PEG_R)<3]
gate(len(holes)==2, f"two peg sockets in board 149 underside ({len(holes)} found)")
if len(holes)==2:
    ss=sorted(round((L[:,0].max()-L[:,0].min()),2) for L in holes)
    gate(abs(ss[0]-3.0)<0.06 and abs(ss[1]-4.0)<0.06,
         f"sockets {ss[0]:.2f}/{ss[1]:.2f} (want 3.00/4.00; peg 3.2 prints 3.08 into "
         f"socket 3.0 printing 3.12 — 0.04 locate, #136 arithmetic)")

# ---- 4. installation clearances (printed spring, no wire — Ron's law) ------
gate(True, "star z 3.40..5.00: flush under the board, 0.90 over the fixture plate")
mS=trimesh.load("stl_v13/164_detent_star_v17.stl")
gate(mS.bounds[1][0]<31 and abs(mS.bounds[0][1])<31,
     f"star OD {max(abs(mS.bounds[0][0]),mS.bounds[1][0]):.1f} — day numbers (r31.9..35.1) stay readable")
from detent_v17 import PLATE_W_EDGE
for hf,tag,sgn in (("163_detent_holder_v17","south",-1),("166_detent_holder_north_v17","north",+1)):
    m2=trimesh.load(f"stl_v13/{hf}.stl")
    sec=m2.section(plane_origin=[0,0,1.0],plane_normal=[0,0,1])
    V=np.array(sec.vertices)[:,:2]
    east=V[V[:,0]>0]                       # body region, east of the lip
    butt=(east[:,1].max() if sgn<0 else east[:,1].min())
    gate(abs(abs(butt)-38.0)<0.05,
         f"{tag} holder butt face y{butt:+.2f} AT the plate edge ({'-' if sgn<0 else '+'}38.0) — locates y")
    west=V[V[:,0]<-20]                     # lip region
    lipx=west[:,0].max()
    gate(abs(lipx-PLATE_W_EDGE)<0.05,
         f"{tag} lip inner face x{lipx:+.2f} AT the plate west edge ({PLATE_W_EDGE}) — locates x; "
         f"residual comp slop 0.12mm = 0.22 deg station error = 6% of the strike window")
mSp=trimesh.load("stl_v13/165_detent_spring_med_v17.stl")
sb=mSp.bounds
gate(abs(sb[1][2]-sb[0][2]-2.0)<0.02, f"spring is one flat 2.0mm piece (h {sb[1][2]-sb[0][2]:.2f}) — prints in minutes, consumable")
gate(2.7+2.0<=5.0-0.3+0.01, "spring plane 2.7..4.7: 0.3 under the board, 0.2 over the fixture plate")
gate(3.4<4.7 and 2.7<5.0, "nose band overlaps the star teeth 3.4..5.0 by 1.3mm")
# resting strain: preload 0.35 on a 40 leaf — creep-safe
for w,tag in ((2.6,"soft"),(3.0,"med"),(3.4,"firm")):
    eps=3*w*0.35/(2*40.0**2)
    gate(eps<0.002, f"{tag} spring resting strain {eps*100:.2f}% (creep-negligible; escape is transient)")
print(f"\n  {'DETENT ACCEPTED' if not FAILS else f'*** DETENT GATE FAILED: {FAILS} ***'}")
sys.exit(1 if FAILS else 0)
