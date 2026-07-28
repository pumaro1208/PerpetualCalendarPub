import struct, numpy as np
PROG=(-36.75,0.0); DRIVE=(36.75,0.0); FLUSH=0.12; ZBAND=0.5
def load(fn,zoff,flip,dx,dy):
    for p in ("parts/stl/","parts/stl_v13/","stl_v13/",""):
        try: f=open(p+fn,'rb'); break
        except FileNotFoundError: continue
    else: return None
    f.read(80); n=struct.unpack('<I',f.read(4))[0]; V=np.zeros((n*3,3))
    for i in range(n):
        d=struct.unpack('<12fH',f.read(50)); V[i*3],V[i*3+1],V[i*3+2]=d[3:6],d[6:9],d[9:12]
    f.close(); V[:,0]+=dx; V[:,1]+=dy; V[:,2]=(zoff-V[:,2]) if flip else V[:,2]+zoff
    return V
MANIFEST=[
 ("fixture","49_fixture_r57_v16.stl",0.0,False,0,0,None,"frame"),
 ("bridge","51_bridge_arm_v16.stl",2.5,False,PROG[0],PROG[1],None,"frame"),
 ("board","02e_board_bigbore_v16.stl",5.0,False,PROG[0],PROG[1],PROG,"board"),
 ("star","50d_star_hub_v16.stl",3.3,False,PROG[0],PROG[1],PROG,"board"),
 ("wheel","10_drive_wheel.stl",5.0,False,DRIVE[0],DRIVE[1],DRIVE,"wheel"),
 ("sun","42_sun_v16.stl",9.5,False,PROG[0],PROG[1],None,"frame"),
]
WL={("star","bridge"),("board","wheel"),("board","fixture"),("star","fixture"),
    ("wheel","fixture"),("board","bridge")}
parts={}
for name,fn,zoff,flip,dx,dy,axis,grp in MANIFEST:
    V=load(fn,zoff,flip,dx,dy)
    if V is None: print("  [skip]",name); continue
    parts[name]=(V,axis,grp)
viol=0
print("=== QC SWEEP (flag-free central press-fit) ===")
for name,(V,axis,grp) in parts.items():
    if axis is None: continue
    ax,ay=axis; r=np.hypot(V[:,0]-ax,V[:,1]-ay); z=V[:,2]; zz=z.min()
    while zz<z.max():
        m=(z>=zz)&(z<zz+ZBAND)
        if m.sum():
            r0,r1=r[m].min(),r[m].max()
            for on,(OV,oax,ogrp) in parts.items():
                if on==name or ogrp==grp: continue
                orr=np.hypot(OV[:,0]-ax,OV[:,1]-ay)
                mm=(OV[:,2]>zz+FLUSH)&(OV[:,2]<zz+ZBAND-FLUSH)&(orr>r0+FLUSH)&(orr<r1-FLUSH)
                if mm.sum():
                    if not((name,on) in WL or (on,name) in WL):
                        viol+=1; print(f"  {name} vs {on} z{zz:.1f} r{r0:.1f}-{r1:.1f} *** VIOLATION ***")
        zz+=ZBAND
print("RESULT:", "CLEAN" if viol==0 else f"{viol} VIOLATION(S)")
# explicit engagement checks
S=load("50d_star_hub_v16.stl",3.3,False,0,0); rs=np.hypot(S[:,0],S[:,1])
print("star tube: r %.2f-%.2f, z %.1f-%.1f (rides post, presses board bore 5.45)"%(
      rs[(S[:,2]>5.0)].min(),rs[(S[:,2]>5.0)].max(),S[S[:,2]>5.0][:,2].min(),S[:,2].max()))
