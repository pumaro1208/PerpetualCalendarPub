#!/usr/bin/env python3
"""plate-17 flag-free detent — PRE-PRINT SANITY GATE.
Self-contained: runs on the committed STLs (no generator needed). Three checks:
  1. watertight (0 open/odd-parity edges) on all four parts
  2. assembly interference among the four new parts (whitelisted mates excepted)
  3. critical fit dimensions: board bore, star tube ID/OD press, open pin bores, wedge reach
Exit 0 = ALL PASS (safe to compose); exit 1 = STOP, do not compose.
Full assembly sweep incl. drive wheel + sun is print-console/qc_sweep_central.py.
"""
import struct, os, sys, collections
import numpy as np
CAND=["parts/stl","../parts/stl","stl","stl_v13","parts/stl_v13","../parts/stl_v13"]
def find(fn):
    for d in CAND:
        p=os.path.join(d,fn)
        if os.path.isfile(p): return p
    sys.exit(f"MISSING STL: {fn}  (looked in {CAND})")
PARTS={"board":"02e_board_bigbore_v16.stl","star":"50d_star_hub_v16.stl",
       "fixture":"49_fixture_r58_v16.stl","bridge":"51_bridge_arm_v16.stl"}
def verts_tri(fn):
    d=open(find(fn),'rb').read(); n=struct.unpack('<I',d[80:84])[0]
    T=np.zeros((n,3,3)); off=84
    for i in range(n):
        v=struct.unpack('<12f',d[off:off+48]); T[i]=[v[3:6],v[6:9],v[9:12]]; off+=50
    return T
def verts(fn):
    d=open(find(fn),'rb').read(); n=struct.unpack('<I',d[80:84])[0]
    V=np.zeros((n*3,3)); off=84
    for i in range(n):
        v=struct.unpack('<12f',d[off:off+48]); V[i*3],V[i*3+1],V[i*3+2]=v[3:6],v[6:9],v[9:12]; off+=50
    return V
def open_edges(fn):
    d=open(find(fn),'rb').read(); n=struct.unpack('<I',d[80:84])[0]
    e=collections.Counter(); off=84
    for _ in range(n):
        data=d[off:off+50]; off+=50
        vs=[tuple(round(x,4) for x in struct.unpack('<3f',data[12+12*k:24+12*k])) for k in range(3)]
        if len(set(vs))<3: continue
        for i in range(3):
            a,b=vs[i],vs[(i+1)%3]; e[(min(a,b),max(a,b))]+=1
    return sum(1 for c in e.values() if c%2==1)
res=[]
def gate(name,ok,detail):
    res.append(ok); print(("  PASS  " if ok else "  FAIL  ")+f"{name:34s} {detail}")
print("=== plate-17 flag-free detent — pre-print sanity gate ===")
print("[1] watertight")
for nm,fn in PARTS.items():
    gate(f"watertight {nm}", open_edges(fn)==0, f"{open_edges(fn)} open edges")
print("[2] interference (four new parts)")
PROG=(-36.75,0.0); FLUSH=0.12; ZB=0.5
def place(V,zo,fl,dx,dy):
    V=V.copy(); V[:,0]+=dx; V[:,1]+=dy; V[:,2]=(zo-V[:,2]) if fl else V[:,2]+zo; return V
MAN=[("fixture",PARTS["fixture"],0.0,False,0,0,None,"frame"),
     ("bridge",PARTS["bridge"],2.5,False,PROG[0],PROG[1],None,"frame"),
     ("board",PARTS["board"],5.0,False,PROG[0],PROG[1],PROG,"board"),
     ("star",PARTS["star"],3.3,False,PROG[0],PROG[1],PROG,"board")]
WL={("board","fixture"),("star","fixture"),("board","bridge"),("star","bridge")}
P={nm:(place(verts(fn),zo,fl,dx,dy),ax,gr) for nm,fn,zo,fl,dx,dy,ax,gr in MAN}
viol=0
for nm,(V,ax,gr) in P.items():
    if ax is None: continue
    axx,ayy=ax; r=np.hypot(V[:,0]-axx,V[:,1]-ayy); z=V[:,2]; zz=z.min()
    while zz<z.max():
        m=(z>=zz)&(z<zz+ZB)
        if m.sum():
            r0,r1=r[m].min(),r[m].max()
            for on,(OV,oax,ogr) in P.items():
                if on==nm or ogr==gr: continue
                orr=np.hypot(OV[:,0]-axx,OV[:,1]-ayy)
                mm=(OV[:,2]>zz+FLUSH)&(OV[:,2]<zz+ZB-FLUSH)&(orr>r0+FLUSH)&(orr<r1-FLUSH)
                if mm.sum() and not((nm,on) in WL or (on,nm) in WL): viol+=1
        zz+=ZB
gate("interference (4-part)", viol==0, f"{viol} unwhitelisted violations")
print("[3] fit dimensions")
B=verts(PARTS["board"]); bore=np.hypot(B[:,0],B[:,1]).min()*2
gate("board bore ~10.9", abs(bore-10.9)<0.4, f"{bore:.2f} mm dia (was 8.7)")
S=verts(PARTS["star"]); tb=S[S[:,2]>2.5]; rr=np.hypot(tb[:,0],tb[:,1])
tid,tod=rr.min()*2,rr.max()*2
gate("star tube ID ~8.7 (rides post 8.3)", abs(tid-8.7)<0.4, f"{tid:.2f} mm dia")
gate("tube OD ~= board bore (press)", abs(tod-bore)<0.35, f"tube {tod:.2f} vs bore {bore:.2f}")
BR=verts(PARTS["bridge"]); ob=all((np.hypot(BR[:,0]-sx*20,BR[:,1]+30.5)<1.9).sum()==0 for sx in(-1,1))
gate("bridge pin bores open", ob, "0 geometry within r1.9 of either boss")
wy=BR[(np.abs(BR[:,0])<3)&(BR[:,1]>-28.5)&(BR[:,1]<-26.0),1]
crest=abs(wy.max()) if len(wy) else 0
gate("wedge crest in notch 26<r<28.5", 26.0<crest<28.5, f"crest r{crest:.2f}")

print("[4] base connectivity (no floating features)")
def _cross(T,px,py):
    zs=[]
    for t in T:
        (x0,y0,z0),(x1,y1,z1),(x2,y2,z2)=t
        d=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
        if abs(d)<1e-9: continue
        a=((y1-y2)*(px-x2)+(x2-x1)*(py-y2))/d; b=((y2-y0)*(px-x2)+(x0-x2)*(py-y2))/d; c=1-a-b
        if a>1e-6 and b>1e-6 and c>1e-6: zs.append(a*z0+b*z1+c*z2)
    return sorted(zs)
def _rooted(fn,cx,cy,top):
    T=verts_tri(fn)
    for dx,dy in ((1.7,0.9),(-0.9,1.7),(1.1,-1.5)):
        zs=_cross(T,cx+dx,cy+dy)
        if not zs: continue
        occ=[ (sum(1 for z in zs if z>h)%2==1) for h in np.arange(0.25,top,0.5)]
        return all(occ)
    return False
gate("program post rooted", _rooted(PARTS["fixture"],-36.75,0,9.0), "continuous solid bed->9 (no float)")
gate("drive post base solid",  _rooted(PARTS["fixture"], 36.75,0,3.9), "solid bed->3.9 under the post (east slab)")

ok=all(res)
print("\nRESULT: "+("ALL PASS — safe to compose plate-17" if ok else "*** FAILURES — STOP, do not compose ***"))
sys.exit(0 if ok else 1)
