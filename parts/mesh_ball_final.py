#!/usr/bin/env python3
"""#121 FINAL — the patent-form mesh pair, bench coupon edition.

Sun: 7 mushroom ball teeth (r2.0, tips at the 9.55 envelope) — Ron identified the
ball tips as the anti-binding mechanism for the climbing (epicyclic) mesh.
Month gear: mutual-envelope conjugate of the sun (sockets swept by the balls
themselves through the full 84-engagement hunting cycle, clearance 0.15), then
crests sculpted into tall rounded teeth (core 14.3, lobes r1.5) to match the drawn
month wheel 210 — material-removal-only, so the zero-overlap proof is inherited.
Sim: 0.00mm^2 overlap through the roll, free play 1.28deg (0.33mm at pitch),
wedge-proof both directions. Bores 2.80: drop on the coupon base posts (CD 23.75).
"""
import numpy as np, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity
import trimesh
from generator import cylinder
from generator_v13 import write_stl

CD=23.75; CLR=0.15
RH_S=2.0; CH_S=9.55-RH_S; CORE_S=6.3
SCULPT_CORE, SCULPT_LOBE = 14.3, 1.5
BORE=2.80; H=3.0
STEPS=700

def main_poly(g): return max(g.geoms,key=lambda p:p.area) if isinstance(g,MultiPolygon) else g

def sun_blank():
    parts=[Point(0,0).buffer(CORE_S,64)]
    for k in range(7):
        a=2*np.pi*k/7
        parts.append(Point(CH_S*np.cos(a),CH_S*np.sin(a)).buffer(RH_S,40))
    return unary_union(parts)

def build_pair():
    sb=sun_blank(); sd=sb.buffer(CLR,16).simplify(0.03)
    sweep=[]
    for phi in np.linspace(0,2*np.pi*12,STEPS,endpoint=False):
        psi=-(7/12)*phi
        w1=affinity.rotate(sd,np.degrees(phi),origin=(0,0))
        sweep.append(affinity.rotate(affinity.translate(w1,-CD,0),np.degrees(-psi),origin=(0,0)))
    sat=main_poly(Point(0,0).buffer(15.8,128).difference(unary_union(sweep)))
    sat=main_poly(sat.buffer(0.1,12).buffer(-0.1,12))
    sweep2=[]; td=sat.buffer(CLR,16).simplify(0.03)
    for psi in np.linspace(0,2*np.pi*7,STEPS,endpoint=False):
        phi=-(12/7)*psi
        w1=affinity.rotate(td,np.degrees(psi),origin=(0,0))
        sweep2.append(affinity.rotate(affinity.translate(w1,CD,0),np.degrees(-phi),origin=(0,0)))
    sun=main_poly(sb.difference(unary_union(sweep2)))
    sun=main_poly(sun.buffer(0.1,12).buffer(-0.1,12))
    # sculpt the month gear crests into tall rounded teeth (removal only)
    mask=[Point(0,0).buffer(SCULPT_CORE,96)]
    ch=15.80-SCULPT_LOBE
    for k in range(12):
        a=np.pi/12+2*np.pi*k/12
        mask.append(Point(ch*np.cos(a),ch*np.sin(a)).buffer(SCULPT_LOBE,40))
    sat=main_poly(sat.intersection(unary_union(mask)).buffer(0.08,12).buffer(-0.08,12))
    return sun, sat

def extrude(poly, h):
    p=Polygon(poly.simplify(0.02).exterior.coords,
              [list(Point(0,0).buffer(BORE,48).exterior.coords)])
    m=trimesh.creation.extrude_polygon(p,h)
    return [tuple(np.array(v) for v in m.vertices[f]) for f in m.faces]

if __name__=="__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    t0=time.time()
    sun,sat=build_pair()
    write_stl("121_ballmesh_sun_v16.stl", extrude(sun,H))
    tris = extrude(sat,H)
    tris += cylinder(10.5,0.0,2.5,H,9.0,seg=24)     # grip pin
    write_stl("121_ballmesh_month_v16.stl", tris)
    print(f"  built in {time.time()-t0:.0f}s — sun tip {max(np.hypot(*np.array(sun.exterior.xy))):.2f}, "
          f"month tip {max(np.hypot(*np.array(sat.exterior.xy))):.2f}, bores {BORE}")
