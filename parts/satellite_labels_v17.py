#!/usr/bin/env python3
"""#145 SATELLITE LABELS — month names on the month wheel, 1-12 on feb and leap.

Ron: "white hour numbers on the satellites so I know how to set them."

WHICH TOOTH IS WHICH MONTH is derived from the simulator's calendar engine, not
assumed. At 23:00 on date 30 the 23h arm sweeps the month wheel and finds either a
long tooth (the month ends at 30) or a short one (it passes). Whichever tooth is on
the strike line at that instant IS that month's tooth — and that is true for all
twelve, not just the five that fire. Measured over 14 simulated years, single-valued
for every month:

    tooth  0  1  2  3  4  5  6  7  8  9 10 11
    month Aug Jan Jun Nov Apr Sep Feb Jul Dec May Oct Mar
                   ^^^^^^^^^^^^^^^^^^^ the five LONG teeth

The long set is five CONSECUTIVE positions and its months are exactly February plus
the four 30-day ones — September, April, June and November. That is the check that
says the mapping is right, and Ron can verify it on the printed part by eye.

An earlier algebraic shortcut (+7 teeth per month) got this wrong: one month is 31
board steps = 19 satellite teeth, but the tooth INDEX runs against the spin, so the
step is -7, not +7. The engine caught it. Hence: measure, do not extrapolate.

POSITION -> ANGLE. The finger bars sit at 6 + 30j in the part frame on all three
receivers (only the mesh lamina carries the per-satellite ALPHA clocking — correct,
because each satellite strikes when its OWN station reaches the strike line, so the
bars must agree in the part frame while the mesh phase varies with station angle).
Index increases with part-frame angle, so bar j carries tooth (2+j) mod 12.

WHY IT IS SAFE TO ENGRAVE THE BARS. The bars are the strike teeth — they take the
24h arm's push, the force that advances the board. A 2.2 x 0.5mm groove drops the
section modulus to 64% of solid, but it sits at r10.85 where the bending moment is
only 37% of the root's. Peak stress there works out at 58% of the root's, so the
critical section stays at the root and the groove is not the new failure point.
Placing the label further inboard would have inverted that.
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union
from shapely import affinity
from generator_v13 import write_stl
from weld import stack
import generator_engine_v17 as E

CAP, STROKE, CH_W, KERN = 2.60, 0.42, 1.45, 0.75
# #153 STROKE 0.45 -> 0.42: one whole outer-wall bead at a 0.4 nozzle. Between 1 and 2
# beads the slicer must choose either a single fat bead or two starved ones, and it can
# switch between them along a curve — that inconsistency is most of what makes a stroke
# font look ragged. 0.42 is exactly one bead; the next clean value up is 0.84.
# KERN must exceed STROKE or adjacent letters fuse: the gap between one glyph's
# right stroke edge and the next's left edge is KERN - STROKE, and at 0.40 vs 0.55
# that is negative. The first cut read as 18 blobs instead of 36 letters.
R_MID   = 10.85          # label centre radius — see the section note above
REC     = 0.40           # engraving depth — #153. 0.50 is TWO AND A HALF layers at 0.20,
                         # so it rounded to 0.4 or 0.6 unpredictably and the letter depth
                         # varied across the wheel. Went DOWN to 0.40 (two whole layers)
                         # rather than up to 0.60, on strength: the groove sits in a
                         # 1.5mm bar that takes the drive impulse, and 0.60 would have
                         # left 0.90 of section where 0.40 leaves 1.10 — about 19% more
                         # bending capacity for no loss of legibility, because the
                         # contrast here comes from the WHITE FILAMENT, not from depth.
Z_BAR   = 3.00           # top of a finger bar
Z_LAM   = 1.50           # top of the mesh lamina
ID_R    = 6.00           # identity ring: inside the label ring (8.05) and outside the hub
ID_CAP, ID_STK, ID_W, ID_K = 2.00, 0.42, 1.10, 0.70   # #153: one bead
WHEEL   = {"month": ("1", "MONTH"), "feb": ("2", "FEB"), "leap": ("3", "LEAP")}

TOOTH_MONTH = {0:'AUG', 1:'JAN', 2:'JUN', 3:'NOV', 4:'APR', 5:'SEP',
               6:'FEB', 7:'JUL', 8:'DEC', 9:'MAY', 10:'OCT', 11:'MAR'}

G = dict(E.__dict__.get("_G", {}))
G.update({
 '0':[(0,0,1,0),(1,0,1,1),(1,1,0,1),(0,1,0,0)],
 '1':[(.5,0,.5,1),(.2,.75,.5,1),(.2,0,.8,0)],
 '2':[(0,1,1,1),(1,1,1,.5),(1,.5,0,0),(0,0,1,0)],
 '3':[(0,1,1,1),(1,1,1,0),(1,0,0,0),(.3,.5,1,.5)],
 # '4' and 'A' are drawn OPEN. Their closed counters are inherently tiny in a
 # stroke font — small triangles that fill in with any printable stroke, at any
 # cap height that still fits between the hub and the mesh root. Scaling does not
 # rescue them; the letterform has to change. These are the stencil variants.
 '4':[(0,1,0,.35),(0,.35,1,.35),(.75,1,.75,0)],
 '5':[(1,1,0,1),(0,1,0,.55),(0,.55,1,.55),(1,.55,1,0),(1,0,0,0)],
 '6':[(1,1,0,.6),(0,.6,0,0),(0,0,1,0),(1,0,1,.5),(1,.5,0,.5)],
 '7':[(0,1,1,1),(1,1,.35,0)],
 '8':[(0,0,1,0),(1,0,1,1),(1,1,0,1),(0,1,0,0),(0,.5,1,.5)],
 '9':[(1,.4,0,.4),(0,.4,0,1),(0,1,1,1),(1,1,1,0),(1,0,0,0)],
 'A':[(0,0,.45,.95),(.55,.95,1,0),(.2,.42,.8,.42)],
 'B':[(0,0,0,1),(0,1,.9,1),(.9,1,.9,.55),(.9,.55,0,.5),(0,.5,1,.45),(1,.45,1,0),(1,0,0,0)],
 'C':[(1,1,0,1),(0,1,0,0),(0,0,1,0)],
 'D':[(0,0,0,1),(0,1,.7,1),(.7,1,1,.7),(1,.7,1,.3),(1,.3,.7,0),(.7,0,0,0)],
 'E':[(1,1,0,1),(0,1,0,0),(0,0,1,0),(0,.5,.8,.5)],
 'F':[(1,1,0,1),(0,1,0,0),(0,.5,.8,.5)],
 'G':[(1,1,0,1),(0,1,0,0),(0,0,1,0),(1,0,1,.45),(1,.45,.5,.45)],
 'H':[(0,0,0,1),(1,0,1,1),(0,.5,1,.5)],
 'J':[(1,1,1,.2),(1,.2,.6,0),(.6,0,.2,0),(.2,0,0,.25)],
 'L':[(0,1,0,0),(0,0,1,0)],
 'M':[(0,0,0,1),(0,1,.5,.45),(.5,.45,1,1),(1,1,1,0)],
 'N':[(0,0,0,1),(0,1,1,0),(1,0,1,1)],
 'O':[(0,0,1,0),(1,0,1,1),(1,1,0,1),(0,1,0,0)],
 'P':[(0,0,0,1),(0,1,1,1),(1,1,1,.5),(1,.5,0,.45)],
 'R':[(0,0,0,1),(0,1,1,1),(1,1,1,.55),(1,.55,0,.5),(.4,.5,1,0)],
 'S':[(1,1,0,1),(0,1,0,.55),(0,.55,1,.5),(1,.5,1,0),(1,0,0,0)],
 'T':[(0,1,1,1),(.5,1,.5,0)],
 'U':[(0,1,0,.15),(0,.15,.3,0),(.3,0,.7,0),(.7,0,1,.15),(1,.15,1,1)],
 'V':[(0,1,.5,0),(.5,0,1,1)],
 'Y':[(0,1,.5,.5),(1,1,.5,.5),(.5,.5,.5,0)],
})

def text_poly(txt):
    """Text centred on (0,0), reading along +x with +y up."""
    w = len(txt)*CH_W + (len(txt)-1)*KERN
    parts = []
    for i, ch in enumerate(txt):
        segs = [LineString([(x0*CH_W + i*(CH_W+KERN) - w/2, y0*CAP - CAP/2),
                            (x1*CH_W + i*(CH_W+KERN) - w/2, y1*CAP - CAP/2)])
                for x0, y0, x1, y1 in G[ch]]
        parts += [s.buffer(STROKE/2, cap_style=2, join_style=1) for s in segs]
    return unary_union(parts)

def labels_for(sat, n_fingers):
    """-> {z_surface: polygon}. Reading RADIALLY OUTWARD at each of the 12
    positions; whichever surface is uppermost there carries the engraving."""
    out = {Z_BAR: [], Z_LAM: []}
    for j in range(12):
        a = E.E1_BASE[sat] + 30.0*j
        txt = TOOTH_MONTH[(2 + j) % 12] if sat == "month" else str(j + 1)
        p = affinity.rotate(text_poly(txt), a, origin=(0, 0))
        p = affinity.translate(p, R_MID*np.cos(np.deg2rad(a)), R_MID*np.sin(np.deg2rad(a)))
        out[Z_BAR if j < n_fingers else Z_LAM].append(p)
    return {z: unary_union(v) for z, v in out.items() if v}

def arc_text(txt, radius, cap, stk, chw, kern, bearing, mirror=False):
    """Text set along an arc at `radius`, each character upright-radially-outward,
    centred on `bearing`. Used for the wheel identity, which has to live inside the
    label ring (r8.05) and outside the hub (r4.0) — a straight line of text does not
    fit that annulus, an arc does."""
    step = np.degrees((chw + kern)/radius)
    a0 = bearing + step*(len(txt)-1)/2
    parts = []
    for i, ch in enumerate(txt):
        a = a0 - i*step
        if ch == ' ':                      # advance the arc, emit nothing
            continue
        g = []
        for x0,y0,x1,y1 in G[ch]:
            g.append(LineString([((x0-0.5)*chw, (y0-0.5)*cap),
                                 ((x1-0.5)*chw, (y1-0.5)*cap)])
                     .buffer(stk/2, cap_style=2, join_style=1))
        c = unary_union(g)
        if mirror: c = affinity.scale(c, -1, 1, origin=(0,0))
        c = affinity.rotate(c, a - 90, origin=(0,0))
        parts.append(affinity.translate(c, radius*np.cos(np.deg2rad(a)),
                                            radius*np.sin(np.deg2rad(a))))
    return unary_union(parts)

def identity(sat, n_fingers):
    """(underside full identity, top-face numeral). Order and name so a wheel can be
    told apart in the hand; the numeral repeats on top so the assembled stack reads
    1-2-3 from below without dismantling it."""
    num, name = WHEEL[sat]
    txt = f"{num} {name}"
    # underside: mirrored in X so it reads correctly when the wheel is turned over
    under = arc_text(txt, ID_R, ID_CAP, ID_STK, ID_W, ID_K, 180.0, mirror=True)
    under = affinity.scale(under, -1, 1, origin=(0,0))
    # top numeral: in a gap BETWEEN strike bars, never on one — engraving a bar here
    # would sit at r6 where the bending moment is 71% of the root's, not 37%
    gap = E.E1_BASE[sat] + 15.0
    top = arc_text(num, ID_R, 2.6, 0.5, 1.45, 0.75, gap)
    return under, top

def build(sat, n_fingers, base_no, white_no, boss_h=0.0):
    mon = affinity.rotate(E._slice("131_month_widesquare_v16.stl", 1.5),
                          E.ALPHA[sat], origin=(0, 0))
    bore = Point(0, 0).buffer(E.BORE, 48)
    hub = Point(0, 0).buffer(4.0, 64)
    bars = [E._bar((E.E1_BASE[sat] + k*30.0)*E.d2r, 2.0, 16.0, 4.5) for k in range(n_fingers)]
    tips = [E._bar((E.E1_BASE[sat] + k*30.0)*E.d2r, 15.5, E.TIP_R, 4.5) for k in range(n_fingers)]
    lab = labels_for(sat, n_fingers)
    lam_cut, bar_cut = lab.get(Z_LAM), lab.get(Z_BAR)
    under, topnum = identity(sat, n_fingers)
    lam_cut = unary_union([lam_cut, topnum]) if lam_cut is not None else topnum

    body_lam = unary_union([hub] + bars).difference(bore)
    top_lam  = unary_union([hub] + bars + tips).difference(bore)
    slabs = [(0.0, REC, mon.simplify(0.02).difference(bore).difference(under)),
             (REC, Z_LAM-REC, mon.simplify(0.02).difference(bore))]
    # mesh-lamina engraving sits in the top REC of the lamina
    slabs.append((Z_LAM-REC, Z_LAM,
                  mon.simplify(0.02).difference(bore).difference(lam_cut)
                  if lam_cut else mon.simplify(0.02).difference(bore)))
    slabs.append((Z_LAM, 2.2, body_lam))
    slabs.append((2.2, E.ZS-REC, top_lam))
    slabs.append((E.ZS-REC, E.ZS, top_lam.difference(bar_cut) if bar_cut else top_lam))
    if boss_h > 0:
        slabs.append((E.ZS, E.ZS+boss_h, Point(0,0).buffer(4.5,48).difference(bore)))
    write_stl(base_no, stack(slabs))

    ink = [(0.0, REC, under)]
    if lam_cut is not None: ink.append((Z_LAM-REC, Z_LAM, lam_cut))
    if bar_cut: ink.append((E.ZS-REC, E.ZS, bar_cut))
    write_stl(white_no, stack(ink, allow_multi=True))

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    build("month", 5, "151_receiver_month_lab_v17.stl", "154_sat_ink_month_v17.stl")
    build("feb",   1, "152_receiver_feb_lab_v17.stl",   "155_sat_ink_feb_v17.stl")
    build("leap",  1, "153_receiver_leap_lab_v17.stl",  "156_sat_ink_leap_v17.stl", boss_h=1.2)
    for k in ("month","feb","leap"):
        print(f"  {k:5s} strike bars at {E.E1_BASE[k]:6.3f} + 30k deg   "
              f"(#148: was a single 6.000 for all three)")
    print("  month wheel bars read: "
          + ", ".join(TOOTH_MONTH[(2+j) % 12] for j in range(5))
          + "   <- Feb + the four 30-day months")
    print("  wheel identity: " + " | ".join(f"{v[0]} {v[1]}" for v in WHEEL.values())
          + "   (underside, plus the numeral on top)")
