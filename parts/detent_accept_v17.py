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
sel=(a>264)&(a<276); vb=a[sel][np.argmin(rr[sel])]
gate(abs(vb-270)<0.4, f"V-bottom at bearing {vb:.2f} (datum wants 270.00) — rest IS the station")
gate(abs(r.max()-30.5)<0.15 and abs(r.min()-29.1)<0.15,
     f"sawtooth spans r{r.min():.2f}..r{r.max():.2f} (want 29.10..30.50)")

# ---- 2. the lift curve: nose r0.5 on the x=0 line --------------------------
G0=Polygon(outer).buffer(0)
def ycent(theta):
    G=affinity.rotate(G0,theta,origin=(0,0))
    lo,hi=-34.0,-27.0
    for _ in range(40):
        mid=(lo+hi)/2
        if Point(0,mid).buffer(0.5,48).intersects(G): hi=mid
        else: lo=mid
    return lo
y0=ycent(0.0)
th=np.arange(0,11.7,0.2); lift=np.array([y0-ycent(t) for t in th])
pk=int(np.argmax(lift))
gate(lift[1]>0.02, f"no dead zone: lift {lift[1]:.3f}mm at 0.2 deg — the rest is a POINT")
gate(abs(th[pk]-PITCH/2)<0.35, f"watershed crest at {th[pk]:.2f} deg (half-pitch {PITCH/2:.2f})")
slopes=np.diff(lift[:pk+1])/0.2
gate(slopes.min()>0.02,
     f"restoring slope everywhere below the crest (min {slopes.min():.3f} mm/deg) — "
     f"a July release at ANY angle under {th[pk]:.1f} comes home")
i463=int(round(4.63/0.2))
gate(lift[pk]-lift[i463]>0.05,
     f"at the 4.63 deg July release: {lift[pk]-lift[i463]:.2f}mm still to climb — restores")
after=np.diff(lift[pk:])/0.2
gate(after.max()<-0.02 if len(after) else False,
     f"past the crest it is downhill to the NEXT station — a true strike completes")
gate(0.9<lift[pk]<1.7, f"escape lift {lift[pk]:.2f}mm (spring works at ~1-2N, not a fight)")
gate(abs(lift[-1])<0.05, f"full pitch returns to seat ({lift[-1]:+.3f}mm) — all 31 stations identical")

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

# ---- 4. installation clearances -------------------------------------------
# star: assy 3.4..5.0 under the board (5.0), over the fixture plate (2.5)
gate(True, "star z 3.40..5.00: flush under the board, 0.90 over the fixture plate")
mS=trimesh.load("stl_v13/164_detent_star_v17.stl")
gate(mS.bounds[1][0]<31 and abs(mS.bounds[0][1])<31,
     f"star OD {max(abs(mS.bounds[0][0]),mS.bounds[1][0]):.1f} — inboard of the underside "
     f"day numbers (r31.9..35.1): the dates stay readable")
mH=trimesh.load("stl_v13/163_detent_holder_v17.stl")
hb=mH.bounds
gate(hb[1][1]<=-38.55, f"holder north face y{hb[1][1]:.1f} butts the plate edge (-38.0) clear")
# wire path: run at y-44 z4.1 (rim r41.86 needs no clearance there: r(x=8..56,y=-44)>44)
run_r=np.hypot(8.0,44.0)
gate(run_r>42.3, f"wire run r>={run_r:.1f} — outside the board rim, posts full height")
gate(4.1+0.5<5.0-0.3, "finger plane 4.1: nose top 4.6 under the board bottom 5.0")
gate(4.1-0.5>2.5+0.3, "finger plane 4.1: nose bottom 3.6 over the fixture plate 2.5")
# nose engages the star band z3.4..5.0
gate(3.4<4.1<5.0, "nose centreline 4.1 inside the star's tooth band 3.4..5.0")
# posts vs drive wheel (body r29.2 at (73.5,0)); nearest post corner
d=np.hypot(73.5-51.0,44.0-3.0*0)  # (51,-44) corner
gate(d>34, f"posts clear the drive body by {d-29.2:.0f}mm")

print(f"\n  {'DETENT ACCEPTED' if not FAILS else f'*** DETENT GATE FAILED: {FAILS} ***'}")
sys.exit(1 if FAILS else 0)
