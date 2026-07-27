#!/usr/bin/env python3
"""qc_sweep.py -- ASSEMBLY INTERFERENCE GATE (finding 88's generalization)
For every ROTATING part, compute its swept annulus (per z-band, about its
axis) from the ACTUAL MESH, then probe every other part's vertices for
intrusion. Parts in the same rotating group don't conflict; declared mesh
pairs are reported as intended contact, not violations.
Usage: python3 qc_sweep.py   (manifest below; edit per assembly)"""
import struct, sys
import numpy as np

PROG=(-36.75,0.0); DRIVE=(36.75,0.0)
MARGIN=0.35          # required clearance, mm
ZSTEP=0.6            # z discretisation

# name, file, axis(None=static), z-offset(print->assembly), group, notes
MANIFEST=[
 ("fixture_r5","49_fixture_r5_v16.stl",None,0.0,"frame",""),
 ("detent_arm","47_detent_arm_v16.stl",None,2.5,"frame","flex: +1.6 margin"),
 ("star_ring","50_detent_star_v16.stl",PROG,5.0,"board","emitted top-down: assembly z = 5.0 - print z"),
 ("board","02_program_wheel.stl",PROG,5.0,"board",""),
 ("drive_wheel","10_drive_wheel.stl",DRIVE,5.0,"wheel",""),
 ("sun","42_sun_v16.stl",PROG,9.5,"frame","static column"),
]
MESH_PAIRS={("board","drive_wheel"),("drive_wheel","board")}  # intended contact
FLIP={"star_ring"}   # emitted in print orientation: assembly z = zoff - z

def load(fn,zoff,flip):
    try: f=open(fn,'rb')
    except FileNotFoundError:
        for p in ("/mnt/project/stl_v13/","/mnt/project/stl/","/home/claude/pc-stl/parts/stl_v13/"):
            try: f=open(p+fn,'rb'); break
            except FileNotFoundError: continue
        else: return None
    f.read(80); n=struct.unpack('<I',f.read(4))[0]
    V=np.zeros((n*3,3))
    for i in range(n):
        d=struct.unpack('<12fH',f.read(50))
        V[i*3],V[i*3+1],V[i*3+2]=d[3:6],d[6:9],d[9:12]
    f.close()
    V[:,2]=(zoff-V[:,2]) if flip else (V[:,2]+zoff)
    return V

parts={}
for name,fn,axis,zoff,grp,note in MANIFEST:
    V=load(fn,zoff,name in FLIP)
    if V is None: print(f"  [skip] {name}: {fn} not found"); continue
    parts[name]=(V,axis,grp,note)

print("=== QC SWEEP: assembly interference gate ===\n")
violations=0
for name,(V,axis,grp,note) in parts.items():
    if axis is None: continue
    ax,ay=axis
    r=np.hypot(V[:,0]-ax,V[:,1]-ay); z=V[:,2]
    zlo,zhi=z.min(),z.max()
    bands=[]
    zz=zlo
    while zz<zhi:
        m=(z>=zz)&(z<zz+ZSTEP)
        if m.sum(): bands.append((zz,zz+ZSTEP,r[m].min(),r[m].max()))
        zz+=ZSTEP
    for oname,(OV,oaxis,ogrp,onote) in parts.items():
        if oname==name or ogrp==grp: continue
        pair=(name,oname) in MESH_PAIRS or (oname,name) in MESH_PAIRS
        orr=np.hypot(OV[:,0]-ax,OV[:,1]-ay); oz=OV[:,2]
        extra=1.6 if "flex" in onote else 0.0
        worst=None
        for z0,z1,r0,r1 in bands:
            m=(oz>z0-0.05)&(oz<z1+0.05)&(orr>r0-MARGIN-extra)&(orr<r1+MARGIN+extra)
            if m.sum():
                clr=min(abs(orr[m]-r1).min(),abs(orr[m]-r0).min())
                if worst is None or clr<worst[0]: worst=(clr,z0,z1)
        if worst:
            tag="MESH (intended)" if pair else "*** VIOLATION ***"
            if not pair: violations+=1
            print(f"  {name} (sweeps) vs {oname}: intrusion at z{worst[1]:.1f}-{worst[2]:.1f}, clearance {worst[0]:.2f}  {tag}")
print(f"\nRESULT: {'PASS -- no unintended intrusions' if violations==0 else f'{violations} VIOLATION(S)'}")
