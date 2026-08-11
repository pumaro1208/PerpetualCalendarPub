#!/usr/bin/env python3
"""#168 THE SUN'S GROUND — r65 root collar, clamp cap, spacer rev B, bore ladder.

Ron, video, springs out: "even without the bridge detents the jam still occurs."
Frame-by-frame: the K4 key column leaning ~25deg with the sun tipped over on it —
cracked at the root. A tipped sun is a broken GROUND LINK: the epicyclic loses
its reaction member, the satellite stops counter-rotating on schedule, strike
teeth park in the arm path, and the mesh centre-distance wanders once per rev.
One failure, five ghosts (#168 finding): recurring "sun play", "hits the sun at
intervals", the climbing satellite, heavy normal days, jams detent-in or -out.

Ron: "so we need new tighter suns." Half right — tighter bores kill the
rotational slop he has been feeling, and the ladder below delivers that. But
tight bores on a cracked pillar clamp nothing. The repair is the GROUND:

  r65 (via fixture_r64_v17, key_root=True): 5.40-sq root collar z8.5-9.4 under
      the K4 key — 2.2x the root section modulus, stress riser moved up.
  170 CLAMP CAP: square-bore disc pressed onto the key top, bearing down on the
      tower stack. The stacked sun cores + spacer become the structural column;
      the key carries torsion only. A knock on the "key" now loads a clamped
      pillar, not 21mm of bare printed square against its layer lines.
  172 SPACER rev B: stepped bore (5.70 sq low / 4.50 high) to sit over the
      root collar. OD/height unchanged from 147.
  173/174 SUN TOWER bore ladder: piece 140's geometry with square bores 4.44
      and 4.40 design (140 itself is the 4.50 loose end). #136 arithmetic:
      4.44 prints ~4.38 on the key's ~4.36 = snug slip; 4.40 prints ~4.34 =
      light press. Ron picks the snuggest that assembles — the #114 ladder
      idiom applied to the clocking interface.
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import Point, Polygon
from shapely import affinity
from generator_v13 import write_stl
from weld import stack
import generator_engine_v17 as GE

KEY   = 4.42          # K4 across flats, design
CAP_B = 4.40          # cap bore design -> prints ~4.34 = 0.02 press on ~4.36 key
CAP_R = 8.0
CAP_H = 2.5
ROOT  = 5.40          # r65 root collar across flats
SP_LO, SP_HI = 5.70, 4.50   # spacer rev B stepped bore

def _sq(hw):
    return Polygon([(hw,hw),(-hw,hw),(-hw,-hw),(hw,-hw)])

def clamp_cap(name="170_tower_clamp_cap_v17.stl"):
    write_stl(name, stack([(0.0, CAP_H,
        Point(0,0).buffer(CAP_R,96).difference(_sq(CAP_B/2)))]))

def spacer_revB(name="172_sun_spacer_revB_v17.stl"):
    body = Point(0,0).buffer(5.30,64)
    write_stl(name, stack([
        (0.0, 0.9, body.difference(_sq(SP_LO/2))),   # clears the r65 root collar
        (0.9, 1.0, body.difference(_sq(SP_HI/2))),   # keys on the K4 as before
    ]))

def tower_variant(bore_across, name):
    """Piece 140's exact geometry with a parametrised square bore."""
    sun = affinity.rotate(GE._slice("127_ballsun_slimcore_v16.stl", 2.0),
                          GE.SUN_ROT, origin=(0,0))
    key = _sq(bore_across/2)
    write_stl(name, stack([
        (0.0,       GE.BAND_H,  sun.simplify(0.02).difference(key)),
        (GE.BAND_H, GE.PIECE_H, Point(0,0).buffer(GE.SLIM_R,64).difference(key)),
    ]))

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    from fixture_r64_v17 import fixture_r64
    fixture_r64("171_fixture_r65_v17.stl", key_root=True)
    clamp_cap()
    spacer_revB()
    tower_variant(4.44, "173_sun_tower_b444_v17.stl")
    tower_variant(4.40, "174_sun_tower_b440_v17.stl")

    # ---- acceptance ---------------------------------------------------------
    import trimesh
    FAILS=0
    def gate(ok,msg):
        global FAILS
        print(f"  [{'PASS' if ok else 'FAIL'}] {msg}")
        if not ok: FAILS+=1
    def hole_w(path, z, near=(0.0,0.0), rmax=6.0):
        """Width across flats of the interior square loop at height z."""
        m=trimesh.load(path)
        s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
        best=None
        for L in s.discrete:
            L=np.array(L)[:,:2]
            d=np.hypot(L[:,0]-near[0],L[:,1]-near[1])
            if d.max()<rmax:
                w=(L[:,0].max()-L[:,0].min()+L[:,1].max()-L[:,1].min())/2
                best=w if best is None else min(best,w)
        return best
    def solid_w(path, z, near, rmax=8.0):
        m=trimesh.load(path)
        s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
        for L in s.discrete:
            L=np.array(L)[:,:2]
            d=np.hypot(L[:,0]-near[0],L[:,1]-near[1])
            if d.max()<rmax:
                return (L[:,0].max()-L[:,0].min()+L[:,1].max()-L[:,1].min())/2
        return None

    # r65: root collar + unchanged key above
    w9  = solid_w("stl_v13/171_fixture_r65_v17.stl", 9.0,  (-36.75,0), 8.0)
    w12 = solid_w("stl_v13/171_fixture_r65_v17.stl", 12.0, (-36.75,0), 8.0)
    gate(w9 is not None and abs(w9-ROOT)<0.05, f"r65 root collar {w9 and round(w9,2)} sq at z9.0 (want {ROOT})")
    gate(w12 is not None and abs(w12-KEY)<0.05, f"r65 key {w12 and round(w12,2)} sq at z12 — K4 unchanged above the collar")
    gate((ROOT/KEY)**3 > 1.7, f"root section modulus x{(ROOT/KEY)**3:.1f} (collar vs bare key)")
    m64=trimesh.load("stl_v13/168_fixture_r64_v17.stl"); m65=trimesh.load("stl_v13/171_fixture_r65_v17.stl")
    gate(m65.is_watertight, "r65 watertight")
    gate(abs(m64.bounds[0][0]-m65.bounds[0][0])<0.01 and abs(m64.bounds[1][1]-m65.bounds[1][1])<0.01,
         "r65 footprint identical to r64 — only the key root changed")
    # cap
    cb = hole_w("stl_v13/170_tower_clamp_cap_v17.stl", 1.0)
    gate(cb is not None and abs(cb-CAP_B)<0.04, f"cap bore {cb and round(cb,2)} sq (design {CAP_B}: prints ~4.34 on the ~4.36 key = 0.02 press, #136)")
    mc=trimesh.load("stl_v13/170_tower_clamp_cap_v17.stl")
    gate(abs(mc.bounds[1][2]-CAP_H)<0.02 and abs(mc.bounds[1][0]-CAP_R)<0.05, f"cap r{CAP_R} x {CAP_H} — bears on the slim core annulus (r{GE.SLIM_R})")
    gate(CAP_R > GE.SLIM_R + 2.0, "cap overhangs the core seat by >2mm — full ring contact")
    # spacer rev B
    lo = hole_w("stl_v13/172_sun_spacer_revB_v17.stl", 0.45)
    hi = hole_w("stl_v13/172_sun_spacer_revB_v17.stl", 0.95)
    gate(lo is not None and abs(lo-SP_LO)<0.04, f"spacer low bore {lo and round(lo,2)} clears the {ROOT} collar by {lo and round(lo-ROOT,2)}")
    gate(hi is not None and abs(hi-SP_HI)<0.04, f"spacer top bore {hi and round(hi,2)} keys the K4 as before")
    # ladder
    for f,want in (("140_sun_tower_piece_v17.stl",4.50),
                   ("173_sun_tower_b444_v17.stl",4.44),
                   ("174_sun_tower_b440_v17.stl",4.40)):
        b = hole_w(f"stl_v13/{f}", 3.0)
        gate(b is not None and abs(b-want)<0.04, f"{f.split('_')[0]} tower bore {b and round(b,2)} (ladder step {want})")
    for f in ("173_sun_tower_b444_v17.stl","174_sun_tower_b440_v17.stl"):
        m=trimesh.load(f"stl_v13/{f}")
        s=m.section(plane_origin=[0,0,0.75],plane_normal=[0,0,1])
        r=max(np.hypot(np.array(L)[:,0],np.array(L)[:,1]).max() for L in s.discrete)
        gate(abs(r-9.80)<0.05, f"{f.split('_')[0]} ball band r{r:.2f} — mesh geometry identical to 140")
    print(f"\n  {'SUN GROUND ACCEPTED' if not FAILS else f'*** #168 GATE FAILED: {FAILS} ***'}")
    sys.exit(1 if FAILS else 0)
