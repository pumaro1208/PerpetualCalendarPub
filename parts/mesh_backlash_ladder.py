#!/usr/bin/env python3
"""#116 mesh backlash ladder — the coupon meshed but BOUND (Ron). Root cause: the
profile shift blew the sun tooth to 4.28mm at the pitch line (fatter than a full
nominal tooth 3.93), so FDM swell had no room -> jam. Fix: DROP the shift (clean
stub involute; this mesh only orients, it carries no calendar torque, so tooth
strength is irrelevant) and open backlash. FDM makes the exact printable clearance
unguessable, so ladder it: 3 mesh pairs (7t sun + 12t receiver), all clean involute
x=0, at backlash 0.5 / 0.9 / 1.3. Gear bores opened to 2.80 so post friction can't
masquerade as mesh bind. Spin each pair; the first that rolls free wins -> lock that
backlash into the real sun tower + receiver laminae. Labels 05/09/13 by each pair.
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generator import cylinder, box, _poly_prism, polar_solid
from generator_v13 import write_stl, polar_prof_solid
import mesh_involute as MI

CD = MI.CD                 # 23.75
BORE = 2.80                # opened up: isolate the mesh from post friction
PAIRS = [(0.5,"05"),(0.9,"09"),(1.3,"13")]
YS = [-38.0, 0.0, 38.0]
XSUN, XREC = -12.0, -12.0+CD

Gf = {'0':[(0,0,1,0),(1,0,1,1),(1,1,0,1),(0,1,0,0),(0,0,1,1)],
'1':[(.5,0,.5,1),(.2,.75,.5,1),(.2,0,.8,0)],
'3':[(0,1,1,1),(1,1,1,0),(1,0,0,0),(.3,.5,1,.5)],
'5':[(1,1,0,1),(0,1,0,.55),(0,.55,1,.55),(1,.55,1,0),(1,0,0,0)],
'9':[(1,.4,0,.4),(0,.4,0,1),(0,1,1,1),(1,1,1,0),(1,0,0,0)]}
def sbar(x0,y0,x1,y1,w,z0,z1):
    dx,dy=x1-x0,y1-y0; L=np.hypot(dx,dy)
    px,py=(-dy/L,dx/L) if L>1e-9 else (0,1); hw=w/2
    return _poly_prism([(x0-px*hw,y0-py*hw),(x1-px*hw,y1-py*hw),(x1+px*hw,y1+py*hw),(x0+px*hw,y0+py*hw)],z0,z1)
def emboss(txt,ox,oy,cap=5.0,wg=3.2,gap=1.4,st=0.9,z0=3.0,z1=3.6):
    tris=[]; x=ox
    for ch in txt:
        for(a,b,c,d) in Gf.get(ch,[]): tris+=sbar(x+a*wg,oy+b*cap,x+c*wg,oy+d*cap,st,z0,z1)
        x+=wg+gap
    return tris

def part_base():
    tris = box(3.0,0, 66, 96, 0.0, 3.0)         # slab centered near x=3
    for (bl,lab),y in zip(PAIRS,YS):
        for xc in (XSUN, XREC):
            tris += cylinder(xc,y, 3.5, 3.0, 3.5, seg=32)     # seat shoulder
            tris += cylinder(xc,y, 2.65, 3.0, 8.0, seg=48)    # r2.65 post
        tris += emboss(lab, XREC+10.5, y-2.5)                 # label right of each pair
    write_stl("116_meshladder_base_v16.stl", tris)

def sun(bl, lab):
    prof = MI.inv_shift_profile(MI.N_SUN, x=0.0, tip_cap=9.55, root_r=7.4, backlash=bl)
    tris = polar_prof_solid(prof, 0.0, 3.0, bore=BORE)
    tris += emboss(lab[-1], -1.1, 4.4, cap=2.6, wg=2.0, gap=1.0, st=0.7)   # distinguishing digit
    write_stl(f"116_meshladder_sun_bl{lab}_v16.stl", tris)

def rec(bl, lab):
    prof = MI.inv_shift_profile(MI.N_SAT, x=0.0, tip_cap=15.8, root_r=13.4, backlash=bl)
    tris = polar_prof_solid(prof, 0.0, 3.0, bore=BORE)
    tris += cylinder(9.0, 0.0, 2.5, 3.0, 9.0, seg=24)         # grip pin
    tris += emboss(lab, -3.4, 5.0, cap=4.0, wg=2.8, gap=1.4, st=0.8)       # full backlash label
    write_stl(f"116_meshladder_rec_bl{lab}_v16.stl", tris)

if __name__=="__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    part_base()
    for bl,lab in PAIRS: sun(bl,lab); rec(bl,lab)
    print("  wrote mesh backlash ladder: base + 3 sun/receiver pairs (bl 0.5/0.9/1.3), clean involute x=0, bore 2.80")
