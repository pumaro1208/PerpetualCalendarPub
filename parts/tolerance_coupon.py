#!/usr/bin/env python3
"""Post tolerance-ladder coupon (finding #113, Ron's core print).

Ron's photo: the satellite receiver has visible slop on its round pivot post, and
that slop lets the gear cock/drift so the mesh alternately jams and skips. On FDM
the hole prints undersize and the post prints oversize by ~the clearance we're
chasing, so the right diameter can't be guessed — it must be printed and felt.

This coupon carries FOUR stub posts at radii 2.50 / 2.55 / 2.60 / 2.65 (bore stays
r2.70), each with the board's exact seat shoulder (r3.5, 0.5mm) and 3mm bearing
length — identical geometry to board 02h's post, only the diameter varies. Drop the
existing receiver on each: pick the one that spins free with the least play, then
lock that radius into part_02h_board_v16 (POST_R). Labels are the post radius in
hundredths of a mm (50 = r2.50, etc.), embossed 0.6mm proud.
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generator import cylinder, box, _poly_prism
from generator_v13 import write_stl

# stroke font (minimal caps in a 0..1 box) — the digits we need
G = {
'0':[(0,0,1,0),(1,0,1,1),(1,1,0,1),(0,1,0,0),(0,0,1,1)],
'2':[(0,1,1,1),(1,1,1,.5),(1,.5,0,0),(0,0,1,0)],
'5':[(1,1,0,1),(0,1,0,.55),(0,.55,1,.55),(1,.55,1,0),(1,0,0,0)],
'6':[(1,1,0,.6),(0,.6,0,0),(0,0,1,0),(1,0,1,.5),(1,.5,0,.5)],
'r':[(0,0,0,.7),(0,.55,.5,.7),(.5,.7,.9,.55)],   # small 'r' marker
}

def stroke_bar(x0,y0,x1,y1,w,z0,z1):
    """A thin oriented rectangular prism from (x0,y0)->(x1,y1), width w."""
    dx,dy=x1-x0,y1-y0; L=np.hypot(dx,dy)
    if L<1e-9:  # a dot
        ux,uy,px,py=1,0,0,1
    else:
        ux,uy=dx/L,dy/L; px,py=-uy,ux
    hw=w/2
    corners=[(x0-px*hw,y0-py*hw),(x1-px*hw,y1-py*hw),
             (x1+px*hw,y1+py*hw),(x0+px*hw,y0+py*hw)]
    return _poly_prism(corners,z0,z1)

def emboss(text,ox,oy,cap=6.0,wg=3.6,gap=1.6,stroke=0.9,z0=3.0,z1=3.6):
    tris=[]; x=ox
    for ch in text:
        for (a,b,c,d) in G.get(ch,[]):
            tris+=stroke_bar(x+a*wg,oy+b*cap,x+c*wg,oy+d*cap,stroke,z0,z1)
        x+=wg+gap
    return tris

def part_113_post_tolerance_coupon():
    tris=[]
    SLAB=3.0
    tris += box(0,0,86,26,0.0,SLAB)              # base slab
    radii=[2.50,2.55,2.60,2.65]
    xs=[-31.5,-10.5,10.5,31.5]
    for r,x in zip(radii,xs):
        # seat shoulder r3.5 (0.5mm) then bearing post radius r (3.0mm) — board 02h geometry
        tris += cylinder(x,5.0,3.5,SLAB,SLAB+0.5,seg=32)
        tris += cylinder(x,5.0,r ,SLAB,SLAB+3.5,seg=48)
        lbl=f"{int(round(r*100))}"                # 250->'250'? no: r2.50 -> label '50'
        lbl=f"{int(round((r-2.0)*100)):02d}"      # 2.50 -> 50, 2.65 -> 65
        tris += emboss(lbl, x-4.4, -9.5, cap=5.5, wg=3.4, gap=1.4)
    # a small 'r2.xx' hint isn't needed; two-digit = post radius hundredths (bore r2.70)
    write_stl("113_post_tolerance_coupon_v16.stl", tris)
    print(f"  radii {radii} bore r2.70  -> radial clearances "
          f"{[round(2.70-r,3) for r in radii]} mm")

if __name__=="__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    part_113_post_tolerance_coupon()
