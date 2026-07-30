#!/usr/bin/env python3
"""Central-bearing sleeve ladder (finding #114, Ron's core bind).

Ron: the gear post is fixed (#113 r2.65) but we still bind, and the BOARD post
has play. Correct — the board rides the star-hub tube over the fixture program
post (r4.15), and that tube bore is 4.35 -> 0.20mm radial slack (double the gear
post). The fixed sun + orbiting satellites mean any board-center slop walks every
satellite in/out of the sun mesh = the residual bind.

A naked sleeve over the post would be a 0.2mm wall (unprintable at 0.4 nozzle), so
the printable 'sleeve' is a tighter version of the tube that rides the post — i.e.
a drop-in replacement star hub. FDM makes the exact bore unguessable, so print a
LADDER: three drop-in hubs at tube bore 4.27 / 4.22 / 4.17 (radial clearance on the
r4.15 post: 0.12 / 0.07 / 0.02). Each presses into the board bore identically
(OD 5.45 unchanged) and seats the board on its flange the same height; only the
post-riding bore varies. Swap each into the board, find the one that runs tight but
still spins/reverses free with the bind gone, lock that bore into the star hub.
Plain r14 flange (not the 57mm detent scallop — irrelevant to this bearing test);
covers the thrust pad r6.5-13 and sets board height exactly. Label = bore hundredths.
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generator_v13 import write_stl, polar_prof_solid
from generator import polar_solid
import central_hub as C

TUBE_OD = C.TUBE_OD          # 5.45 — press-fit into the board bore (unchanged)
FLANGE_R = 14.0              # covers the thrust pad (r6.5-13) + margin; seats the board

G = {
'1':[(.5,0,.5,1),(.2,.75,.5,1),(.2,0,.8,0)],
'2':[(0,1,1,1),(1,1,1,.5),(1,.5,0,0),(0,0,1,0)],
'4':[(.8,0,.8,1),(.8,1,0,.35),(0,.35,1,.35)],
'7':[(0,1,1,1),(1,1,.35,0)],
}
def stroke_bar(x0,y0,x1,y1,w,z0,z1):
    dx,dy=x1-x0,y1-y0; L=np.hypot(dx,dy)
    if L<1e-9: px,py=0,1
    else: px,py=-dy/L,dx/L
    hw=w/2
    c=[(x0-px*hw,y0-py*hw),(x1-px*hw,y1-py*hw),(x1+px*hw,y1+py*hw),(x0+px*hw,y0+py*hw)]
    return C._poly_prism(c,z0,z1)
def emboss(text,ox,oy,cap=4.5,wg=3.0,gap=1.4,stroke=0.85,z0=1.8,z1=2.5):
    tris=[]; x=ox
    for ch in text:
        for (a,b,cc,d) in G.get(ch,[]):
            tris+=stroke_bar(x+a*wg,oy+b*cap,x+cc*wg,oy+d*cap,stroke,z0,z1)
        x+=wg+gap
    return tris

def hub(tube_id, label, fname):
    tris=[]
    # solid flange plate r14, z0-1.8, central bore = tube_id (the running bore)
    tris += polar_prof_solid(np.full(400, FLANGE_R), 0.0, 1.8, bore=tube_id)
    # press-tube rises z1.7-3.7 (0.1 overlap into plate), OD 5.45, bore = tube_id
    tris += polar_solid(TUBE_OD, 1.7, 3.7, r_inner=tube_id, seg=64)
    # label on the flange top
    tris += emboss(label, -3.4, 7.0)
    write_stl(fname, tris)
    return fname

if __name__=="__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    specs=[(4.27,"27"),(4.22,"22"),(4.17,"17")]
    for tid,lab in specs:
        f=hub(tid, lab, f"114_central_sleeve_id{lab}_v16.stl")
        print(f"  {f}: tube bore r{tid:.2f}  radial clearance on r4.15 post = {tid-4.15:.2f}mm")
