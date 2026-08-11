#!/usr/bin/env python3
"""Oechslin demonstrator v1.3 — superimposed-teeth architecture.
(Trimmed to the helpers/constants imported by generator_v16: write_stl,
polar_prof_solid, sat_mesh_profile, PITCH, TOP, dflat_profile. Faithful to
the project-knowledge source.)"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generator import (P, polar_solid, cylinder, box, _poly_prism, _stitch,
                       sector_prism, involute_profile, tooth_outline,
                       D_DRIVE, PROG_TIP, PROG_ROOT, ADD_F, MD)
import generator as G
import struct

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl_v13")
os.makedirs(OUT, exist_ok=True)
def write_stl(name, tris):
    G.OUT_BAK = None
    path = os.path.join(OUT, name)
    with open(path, "wb") as f:
        f.write(b"OechslinV13".ljust(80, b"\0"))
        f.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            n = np.cross(b - a, c - a); l = np.linalg.norm(n)
            f.write(struct.pack("<3f", *(n/l if l > 0 else n)))
            for v in (a, b, c): f.write(struct.pack("<3f", *v))
            f.write(b"\0\0")
    print(f"  wrote {name:34s} {len(tris):7d} tris")

# ---------------- v1.3 parameters ----------------
PITCH   = 360/31
SUNORB  = 23.75
S_TIP, S_ROOT = 15.8, 13.4          # satellite mesh lamina (short teeth)
MESH_ROOT = S_ROOT                   # finding #105 REVERTED: the multi-level sun (tip 9.55, not 11.25)
                                     # clears the original 13.4 root by 0.80mm, so no valley-deepening needed
L_TIP   = 18.11                     # strike lamina reach (world 41.86 on-line)
RELIEF  = 0.65                      # corner relief on the +theta flank corner
CORE_R  = 5.0                       # slim sun core at strike laminae
SUN_TIP, SUN_ROOT = 9.55, 7.4       # full sun laminae
STN_M, STN_F, STN_L = (360-29*PITCH, 360-28*PITCH, 360-27*PITCH)
LONG_M  = {0, 8, 9, 10, 11}         # audited long set
DTIP, DBODY = MD*(P["drive_teeth"]/2 + ADD_F), 29.2
POST_R  = P["post_d"]/2             # 4.0
PIV_R   = 2.4                       # carrier pivot radius
# Z stack (absolute, base top = 4)
LIFT = 3.0                            # display bay under the board (z 4..8)
Z = dict(board=(8, 12),
         Am=(13, 15), As=(15, 17),
         g1=(17, 19),
         Bm=(19, 21), Bs=(21, 23),
         g2=(23, 25),
         Cm=(25, 27), Cs=(27, 29))
TOP = 29.0

def dflat_profile(r, flat_off, seg=96):
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    x = np.minimum(r*np.cos(th), r - flat_off)
    y = r*np.sin(th)
    return list(np.stack([x, y], 1))

def polar_prof_solid(prof_r, z0, z1, bore=None, cx=0, cy=0):
    seg = len(prof_r)
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    op = np.stack([cx + prof_r*np.cos(th), cy + prof_r*np.sin(th)], 1)
    br = np.full(seg, bore if bore else 0.001)
    ipn = np.stack([cx + br*np.cos(th), cy + br*np.sin(th)], 1)
    return _stitch(list(op), list(ipn), z0, z1)

def sat_mesh_profile(seg=1440):
    """12 short trapezoid teeth (mesh lamina)."""
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    r = np.full(seg, MESH_ROOT)                       # finding #105: deeper valley for sun-tip clearance
    for k in range(12):
        c = k*np.pi/6
        d = np.angle(np.exp(1j*(th - c)))
        half, ramp = np.deg2rad(6.5), np.deg2rad(5.0)
        u = (np.abs(d) - half)/ramp
        w = np.clip(1 - u, 0, 1); w = w*w*(3 - 2*w)
        r = np.maximum(r, MESH_ROOT + (S_TIP - MESH_ROOT)*w)   # teeth still peak at S_TIP 15.8
    return r
