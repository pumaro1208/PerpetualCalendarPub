#!/usr/bin/env python3
"""qc_sweep v2 -- ASSEMBLY INTERFERENCE GATE (findings 88-96)
v2 (finding 96): the shipped v1 lacked assembly placement -- this version
IS the tool that produces the verdict. Supports per-entry translation,
sub-part isolation (crop), flush-plane tolerance, and support/mesh
whitelists. Any unwhitelisted VIOLATION = stop-and-tell."""
import struct
import numpy as np

PROG=(-36.75,0.0); DRIVE=(36.75,0.0)
FLUSH=0.12    # coincident-plane tolerance (flush is design, not crash)
ZBAND=0.5

def load(fn,zoff=0.0,flip=False,dx=0.0,dy=0.0,crop=None):
    for p in ("","/mnt/project/stl_v13/","/mnt/project/stl/","parts/stl_v13/","parts/stl/","/home/claude/pc-stl/parts/stl_v13/"):
        try: f=open(p+fn,'rb'); break
        except FileNotFoundError: continue
    else: return None
    f.read(80); n=struct.unpack('<I',f.read(4))[0]
    V=np.zeros((n*3,3))
    for i in range(n):
        d=struct.unpack('<12fH',f.read(50))
        V[i*3],V[i*3+1],V[i*3+2]=d[3:6],d[6:9],d[9:12]
    f.close()
    if crop:                                  # isolate a sub-part in LOCAL coords
        lo,hi=crop; m=(V[:,0]>=lo)&(V[:,0]<=hi); V=V[m]
    V[:,0]+=dx; V[:,1]+=dy
    V[:,2]=(zoff-V[:,2]) if flip else (V[:,2]+zoff)
    return V

# name: file, zoff, flip, dx, dy, crop(local x), axis, group
MANIFEST=[
 ("fixture","49_fixture_r5_v16.stl",0.0,False,0,0,None,None,"frame"),
 ("arm","47_detent_arm_v16.stl",2.5,False,-6.75,-28.5,(-40,8),None,"frame"),
 ("cam","47_detent_arm_v16.stl",2.5,False,-33.75,-33.2,(8,40),None,"frame"),  # cam sub-part -> its pin station
 ("star","50_detent_star_v16.stl",5.0,True,PROG[0],PROG[1],None,PROG,"board"),
 ("board","02_program_wheel.stl",5.0,False,PROG[0],PROG[1],None,PROG,"board"),
 ("wheel","10_drive_wheel.stl",5.0,False,DRIVE[0],DRIVE[1],None,DRIVE,"wheel"),
 ("sun","42_sun_v16.stl",9.5,False,PROG[0],PROG[1],None,None,"frame"),
]
# intended contacts: detent mesh, geneva mesh, bearing/support seats
WHITELIST={("star","arm"),("board","wheel"),("board","fixture"),
           ("star","fixture"),("wheel","fixture"),("star","wheel"),("star","cam")}
NOTES={"wheel":"vestigial weekday pin (amputated in print) included in mesh; flags below z5 vs frame are phantom"}

parts={}
for name,fn,zoff,flip,dx,dy,crop,axis,grp in MANIFEST:
    V=load(fn,zoff,flip,dx,dy,crop)
    if V is None or len(V)==0: print(f"  [skip] {name}"); continue
    parts[name]=(V,axis,grp)

print("=== QC SWEEP v2 ===")
viol=0
for name,(V,axis,grp) in parts.items():
    if axis is None: continue
    ax,ay=axis
    r=np.hypot(V[:,0]-ax,V[:,1]-ay); z=V[:,2]
    zz=z.min()
    while zz<z.max():
        m=(z>=zz)&(z<zz+ZBAND)
        if m.sum():
            r0,r1=r[m].min(),r[m].max()
            for on,(OV,oax,ogrp) in parts.items():
                if on==name or ogrp==grp: continue
                orr=np.hypot(OV[:,0]-ax,OV[:,1]-ay)
                mm=(OV[:,2]>zz+FLUSH)&(OV[:,2]<zz+ZBAND-FLUSH)&(orr>r0+FLUSH)&(orr<r1-FLUSH)
                if mm.sum():
                    pair=(name,on) in WHITELIST or (on,name) in WHITELIST
                    tag="intended" if pair else "*** VIOLATION ***"
                    if not pair:
                        viol+=1
                        print(f"  {name} vs {on}: z{zz:.1f}-{zz+ZBAND:.1f}  {tag}")
        zz+=ZBAND
print("RESULT: "+("CLEAN" if viol==0 else f"{viol} VIOLATION(S)"))
