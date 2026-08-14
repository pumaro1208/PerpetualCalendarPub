#!/usr/bin/env python3
"""BENCH TOOL — two-angle phone stand for filming the calendar (Ron's request).

Not a calendar part; a camera rig for the bench. Two slots:
  SLOT A  20 deg recline — near-upright: low oblique close-ups of the mesh
  SLOT B  50 deg recline — looking down onto the board from behind
Slot width 15.0 — sized for Ron's iPhone 15 Pro Max in an OtterBox Symmetry
Clear (~12.5-13 cased): ~2mm of easy insertion play; a bare phone just leans
a few degrees further onto the back wall. (The first cut was 13.0 — Ron asked
before printing, and the case would have made it a press fit.) Middle third of each slot's front lip is cut away full-height:
thumb access + charging cable. Rear toe extends 18 behind the body — a
reclined phone's CG cannot tip it while the bench shakes.

PRINTS FLAT BY CONSTRUCTION: one extruded cross-section (the side profile),
so every layer is identical — no overhang anywhere, no supports (the #171
lesson applied at design time, not discovered on the bed). Extrusion 100 wide;
in use the part lies on its long edge. ~15% infill is plenty.
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import Polygon, Point, LineString, box as sbox
from shapely.ops import unary_union
from generator_v13 import write_stl
from weld import stack

W        = 100.0          # extrusion width (part "height" on the bed)
SLOT_W   = 15.0
A_DEG, B_DEG = 20.0, 50.0 # recline from vertical
NOTCH    = (32.0, 68.0)   # middle-third band carrying the lip cutouts

def _slot(floor, deg, length):
    d = np.array([-np.sin(np.deg2rad(deg)), np.cos(np.deg2rad(deg))])
    p0 = np.array(floor); p1 = p0 + d*length
    return LineString([tuple(p0), tuple(p1)]).buffer(SLOT_W/2, cap_style=2), (p0+p1)/2, d

def profile():
    body = Polygon([(-34,0),(70,0),(70,6),(60,6),(52,24),(34,42),(6,46),(-34,42)])
    base = sbox(-52,0,70,6)                       # rear toe -52..-34
    P = unary_union([body, base])
    sA, cA, dA = _slot((34,14), A_DEG, 36)
    sB, cB, dB = _slot(( 4,14), B_DEG, 46)
    return P.difference(sA).difference(sB), (sA,cA,dA), (sB,cB,dB)

def _grounded(g):
    """Keep only pieces that stand on the base — slot cuts shave off corner
    slivers and the notch strands lip remnants; anything not rooted at the
    floor would print as a loose tower."""
    from shapely.geometry import MultiPolygon
    gs = list(g.geoms) if isinstance(g, MultiPolygon) else [g]
    root = sbox(-52,0,70,8)
    return unary_union([p for p in gs if p.area>50 and p.intersects(root)])

def stand(name="180_bench_phone_stand.stl"):
    P, (sA,cA,dA), (sB,cB,dB) = profile()
    P = _grounded(P)
    # middle-third lip cutouts (full height of the remaining lip — nothing floats)
    Pn = _grounded(P.difference(sbox(34,14,60,60)).difference(sbox(-6,12,22,60)))
    write_stl(name, stack([
        (0.0,      NOTCH[0], P),
        (NOTCH[0], NOTCH[1], Pn),
        (NOTCH[1], W,        P),
    ]))
    return P, (sA,cA,dA), (sB,cB,dB)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    P,(sA,cA,dA),(sB,cB,dB) = stand()

    import trimesh
    FAILS=0
    def gate(ok,msg):
        global FAILS
        print(f"  [{'PASS' if ok else 'FAIL'}] {msg}")
        if not ok: FAILS+=1
    m=trimesh.load("stl_v13/180_bench_phone_stand.stl")
    gate(m.is_watertight, "watertight")
    b=m.bounds
    gate(abs((b[1][2]-b[0][2])-W)<0.01 and (b[1][0]-b[0][0])<130,
         f"extruded {b[1][2]-b[0][2]:.0f} wide, profile {b[1][0]-b[0][0]:.0f} x {b[1][1]-b[0][1]:.0f} — prints flat, zero overhang by construction")
    # slots: void at centre, walls both sides, measured on the FULL profile
    for tag,(s,c,d) in (("A 20deg",(sA,cA,dA)),("B 50deg",(sB,cB,dB))):
        n=np.array([d[1],-d[0]])
        gate(not P.contains(Point(c)), f"slot {tag}: open at centre")
        # wall probe LOW in the slot (near the floor) — at mid-height the front
        # wall legitimately thins as the slot emerges through the sloped top
        cl=c-d*10
        wall=all(P.contains(Point(cl+sgn*n*(SLOT_W/2+2.5))) for sgn in (1,-1))
        # measured width: walk outward from centre along the normal
        wsum=0; cm=c-d*8      # measure low in the slot, clear of the lip taper
        for sgn in (1,-1):
            t=0
            while t<12 and not P.contains(Point(cm+sgn*n*t)): t+=0.05
            wsum+=t
        gate(wall and abs(wsum-SLOT_W)<0.5, f"slot {tag}: width {wsum:.1f} (want {SLOT_W}) with solid walls both sides")
    gate(b[0][0]<-50, "rear toe reaches -52: reclined-phone tipping moment covered")
    # lip notches exist in the middle band only
    sec=m.section(plane_origin=[0,0,50],plane_normal=[0,0,1])
    a_mid=sum(abs(Polygon(np.array(L)[:,:2]).area) for L in sec.discrete)
    sec2=m.section(plane_origin=[0,0,15],plane_normal=[0,0,1])
    a_full=sum(abs(Polygon(np.array(L)[:,:2]).area) for L in sec2.discrete)
    gate(a_mid<a_full-150, f"middle band relieved ({a_full-a_mid:.0f}mm2): thumb/cable notches present")
    print(f"\n  {'STAND ACCEPTED' if not FAILS else f'*** STAND GATE FAILED: {FAILS} ***'}")
    sys.exit(1 if FAILS else 0)
