#!/usr/bin/env python3
"""phantom sweep, push-classified: the watershed metric is TOOTH-PUSH, not
contact. STRIKE = push >= 0.5 pitch (advances); GRAZE = push < 0.35 pitch
(watershed holds, jumper returns the board); DANGER = 0.35..0.5 (marginal)."""
import numpy as np, sys, json
sys.path.insert(0,'.')
import strike_transit_sweep as S
from strike_transit_sweep import transit, tooth_world, dense, rprof, PITCH
from generator_v13 import STN_M, STN_F, STN_L, LONG_M, L_TIP, RELIEF, SUNORB
import matplotlib.path as mpath

res=json.load(open("sweep_results.json")); TP=res["theta_park"]; S.SEAT0[0]=TP
YEAR=372

def lam_profile(long_ks, seg=6200):
    th=np.linspace(0,2*np.pi,seg,endpoint=False); hub=8.0
    r=np.full(seg,hub)
    for k in long_ks:
        c=k*np.pi/6; d=np.angle(np.exp(1j*(th-c)))
        half,ramp=np.deg2rad(5.0),np.deg2rad(4.5)
        u=(np.abs(d)-half)/ramp; w=np.clip(1-u,0,1); w=w*w*(3-2*w)
        tip=np.full(seg,L_TIP)
        frac=np.clip((np.abs(d)-half*0.25)/(half*0.75),0,1)
        tip-=RELIEF*frac
        r=np.maximum(r,hub+(tip-hub)*w)
    return r

def classify(prof, stn, off, label):
    strikes, grazes, danger = [], [], []
    clear_min = 1e9
    for n in range(YEAR):
        theta = TP + n*PITCH
        az = (stn + theta + 180) % 360 - 180
        if abs(az) > 26: continue
        fn = lambda p,t,_o=off: (lambda cx,cy,sp:
            float(np.max(rprof(prof, np.arctan2(p[:,1]-cy,p[:,0]-cx)-sp)
                         - np.hypot(p[:,0]-cx,p[:,1]-cy))))(
            SUNORB*np.cos((stn+t)*np.pi/180), SUNORB*np.sin((stn+t)*np.pi/180),
            (_o+(19/12)*t)*np.pi/180)
        e,_,mp = transit(fn, 194.0, 166.0, theta, +1, nsteps=90)
        if e is None: danger.append((n,az,'JAM')); continue
        p = mp/PITCH
        if p >= 0.5: strikes.append((n,az,p))
        elif p >= 0.35: danger.append((n,az,p))
        elif p > 0.005: grazes.append((n,az,p))
        else:
            c = -fn(tooth_world(180.0), theta)
            clear_min = min(clear_min, c)
    print(f"  {label}:")
    print(f"    STRIKES {len(strikes)}: " + " ".join(f"day{n}(az{az:+.0f},{p:.2f}P)" for n,az,p in strikes))
    print(f"    grazes  {len(grazes)}: worst push {max((p for *_,p in grazes),default=0):.3f}P "
          f"(watershed crest 0.5P)")
    if danger: print(f"    DANGER  {len(danger)}: {danger}")
    else: print(f"    danger  0")
    return strikes, grazes, danger

print("P1: month lamina, push-classified over a full year (OFF=9.75)")
sm,gm,dm = classify(lam_profile(sorted(LONG_M)), STN_M, 9.75, "month")

print("P2: feb lamina — presentation pattern over the year (OFF aligned to pass 0)")
sf,gf,df = classify(lam_profile({0}), STN_F, 0.0, "feb OFF=0")
# The single tooth cycles all twelve 30-deg phases (spin advances 210/pass):
# whichever pass gets phase~0 is 'February' by assembly clocking.

print("P3: leap slider — armed push + retracted clearance vs cam travel")
NOSE=[(16.2,-2.0),(17.91,-1.0),(18.11,0.6),(16.2,2.0)]
def leap_fn(off, retract):
    def fn(p, t):
        az_c=(STN_L+t)*np.pi/180
        cx,cy=SUNORB*np.cos(az_c),SUNORB*np.sin(az_c)
        sp=(off+(19/12)*t)*np.pi/180
        c,s=np.cos(sp),np.sin(sp)
        pts=np.array([(x-retract,y) for x,y in NOSE])
        W=pts@np.array([[c,s],[-s,c]]); W[:,0]+=cx; W[:,1]+=cy
        path=mpath.Path(np.vstack([W,W[:1]]))
        inside=path.contains_points(p)
        if inside.any():
            nd=dense(W.tolist(),0.08)
            return float(np.sqrt(((p[inside][:,None]-nd[None])**2).sum(-1)).min())
        nd=dense(W.tolist(),0.12)
        return -float(np.sqrt(((p[:,None,:]-nd[None])**2).sum(-1)).min())
    return fn
# find the aligned strike park for OFF=0: the park nearest phase-0 presentation
best=None
for n in range(YEAR):
    theta=TP+n*PITCH
    az=(STN_L+theta+180)%360-180
    if abs(az)>8: continue
    ph=(0+(19/12)*theta)%360
    ph=min(ph,360-ph)
    if best is None or ph<best[2]: best=(n,theta,ph,az)
n0,th0,ph0,az0=best
print(f"  aligned pass: day {n0}, sat az {az0:+.1f}, tooth phase {ph0:.1f} deg")
e,_,mp = transit(leap_fn(0.0,0.0),194.0,166.0,th0,+1,nsteps=110)
print(f"  ARMED: {'JAM' if e is None else f'push {mp/PITCH:.3f}P, settled {(e-th0)/PITCH:.3f}P'}")
for rt in (1.0,1.2,1.6,2.0):
    fn=leap_fn(0.0,rt)
    worst=1e9
    for psi in np.linspace(194,166,57):
        worst=min(worst,-fn(tooth_world(psi),th0))
    print(f"  RETRACTED {rt:.1f} mm: {'PENETRATES' if worst<0 else 'clears by'} {abs(worst):.3f} mm")
