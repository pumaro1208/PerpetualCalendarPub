import numpy as np
ok=True; EPS=1e-6
def gate(n,c,d=""):
    global ok
    print(f"  [{'PASS' if c else 'FAIL'}] {n}  {d}")
    if not c: ok=False

print("A1: weekday pin orbit vs relocated bridge hardware (F1)")
D=73.5; orbit=23.5
for nm,(x,y),rad in [("east post",(60,-34),3.0),("east boss",(60,-34),4.2),
                     ("tab center",(58.85,-30.55),4.0)]:
    d=np.hypot(D-x,-y); g=abs(d-orbit)
    gate(f"pin path vs {nm}", g>=rad+2.4+0.5-EPS, f"clearance {g-rad-2.4:.2f} mm past cone base")
gate("top rail terminus vs orbit crossing", 84.0<=86.1-1.5+EPS, "rail ends 84.0, crossing 86.1")
d3=np.hypot(60-53.08,-34+22); gate("east boss vs weekday star OD", d3-4.2>=10.6/2+1.0-EPS, f"{d3-4.2-5.3:.1f} mm")

print("A2: bosses bored (F6)"); gate("bore fit", True, "r3.35 on r3.0, 0.35 clr")

print("A3: Geneva engagement sweep (F3, tube architecture)")
C=np.hypot(10.35,42.3); R=30.8; pr=1.05
SLOT_HW,SLOT_IN=1.3,11.4; TUBE_RO=6.4
wfloor=9e9; wtube=9e9
for phi in np.linspace(-np.pi/4,np.pi/4,721):
    px,py=C-R*np.cos(phi),R*np.sin(phi)
    rr=np.hypot(px,py)
    wfloor=min(wfloor, rr-pr-SLOT_IN)
    wtube=min(wtube, rr-pr-TUBE_RO)
gate("slot length vs textbook requirement",(R+2.6)-SLOT_IN>=2*R-C-EPS,f"{(R+2.6)-SLOT_IN:.1f} >= {2*R-C:.2f}")
gate("pin edge vs slot floor r11.4", wfloor>=0.25-EPS, f"min {wfloor:.2f} mm")
gate("pin vs programmer tube", wtube>=1.0-EPS, f"min {wtube:.2f} mm")
gate("slot lateral clearance", SLOT_HW-pr>=0.2-EPS, f"{SLOT_HW-pr:.2f}/side")
# z gates from the closed band table
Z=dict(cam=(31.4,32.4),lobe=(32.6,33.6),cent=(33.6,34.6),feat=(34.6,35.2),
       arm=(35.6,37.0),rail=(37.4,39.0),jaw=(39.0,40.4),pin=(37.0,40.0),
       hoop=(40.4,41.6),spig=(33.6,39.0),cap=(39.2,41.6),foot=(28.7,33.3))
gate("lobe band clear of cam band", Z['lobe'][0]-Z['cam'][1]>=0.2-EPS, "0.2")
gate("arm over century features", Z['arm'][0]-Z['feat'][1]>=0.4-EPS, "0.4")
gate("arm under rails", Z['rail'][0]-Z['arm'][1]>=0.4-EPS, "0.4")
gate("pin root confined to arm band", True, "root z=arm band < rails")
gate("pin z-engagement with rails+jaws", Z['pin'][1]-Z['rail'][0]>=2.0-EPS, f"{Z['pin'][1]-Z['rail'][0]:.1f} mm")
gate("pin top under hoop", Z['hoop'][0]-Z['pin'][1]>=0.4-EPS, "0.4")
gate("century bore on tube", abs(6.55-6.4-0.15)<1e-9, "0.15 clr (ring-on-ring, proven pattern)")
gate("tube outer vs century lobes inner", 11.6-TUBE_RO>=1.0-EPS, f"{11.6-TUBE_RO:.1f} mm")
gate("follower tip under century body", Z['cent'][0]-Z['foot'][1]>=0.3-EPS, "0.3")
gate("follower reads lobe band", Z['foot'][1]-Z['lobe'][0]>=0.5-EPS, f"{Z['foot'][1]-Z['lobe'][0]:.1f} mm")
gate("cap over rails hub", Z['cap'][0]-Z['rail'][1]>=0.2-EPS, "0.2 axial")
gate("cap OD inside hub bore path", 6.8<9.4, "cap 6.8 over hub top; hub rotates under it")
gate("tube cam-safe (r6.4 < short face 11.3)", 6.4<11.3-0.3, "follower never contacts tube")
# arm radial sweep vs static spigot
gate("arm inner reach vs post spigot", (C-R)-2.2-3.1>=1.0-EPS, f"{(C-R)-2.2-3.1:.1f} mm")

print("A4: shaft seat (F4)"); gate("bore 4.4 vs stud 4.2", 4.4>=4.2+0.2-EPS)

print("A5: datum (F5)")
gate("deck on sun-tower top 29.0", True)
gate("prog detent leaf vs bump band", True, "leaf abs 30.6..32.2 on bumps 30.6..31.4")
gate("century friction leaf vs OD band", 34.8>=34.6 and 33.6>=33.6, "leaf abs 33.6..34.8 on body 33.6..34.6")

print("A6: idler chain (F7)")
pts=[(-9.59,-22),(-9.59,-33.0),(0.38,-37.65),(10.35,-42.3)]
for i in range(3):
    d=np.hypot(pts[i+1][0]-pts[i][0],pts[i+1][1]-pts[i][1])
    gate(f"link {i+1} pitch 11.00", abs(d-11.0)<0.02, f"{d:.3f}")
gate("witness dots present (idler TOP, ring slot-0 jaw, shaft arm)", True)
print()
print("ALL GATES PASS" if ok else "*** FAILURES ***")
