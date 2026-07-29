# Full calendar-engine gate (pre-print, 2026-07-28)

Ron: "print the rest of the calendar gearing." Gate run before any plate.

## Result: GREEN — cleared to print.

### Watertight (0 odd-parity open edges) — all 14 engine parts
42 sun · 33 month · 34 feb · 35 leap · 40 carrier · 43 spacer · 44 sleeves ·
30 drive · 31 sliders · 32 camring · 37 peg pins · 36 hour ring · 38 crank ·
(board 02f already printed).

### Board 02f engine sweep (parts/engine_sweep.py) — CLEAR
Disc-about-fixed-pivot, frame self-checked vs the sun<->month mesh (MESH
CONFIRMED before any "clear" is trusted). Board 02f presents zero raised
obstacles to any satellite disc — the pegless face the campaign was waiting on.

### Acceptance gates — ALL PASS (they encode the cross-part clearances)
- Drive/sliders/camring: A2 channel fit, A3 stroke=FINGER_R exact, A3b retracted
  adjacency 2.54 mm vs lamina tips, A4 peg-track register exact, A6 ring OD 41.6
  vs pin sweep 42.8 keep-out, A6b nose-over-ring 0.45, A7 lobe map (21h@28/22h@29/
  23h@30), A14 fan interference.
- Sun 42: A31 column spans LA+LB+LC (every satellite meshes at its own altitude,
  finding 79) — this is the inter-satellite vertical stacking, gate-owned.
- Spacer 43: A23 lifts month lamina 0.4 clear of the (now-removed) bumps.
- Fixture/carrier/seat: A16 axis 73.5 = mesh distance, A20b sun seats clear of the
  spinning board (top 9.0), A16b carrier top = assembly board-top.
- Peg pins 37, hour ring 36, crank 38, sleeves 44: all PASS.

### Scope note
Per-tooth mesh kinematics and the cam law are owned by the acceptance gates above
and the authoritative simulator (oechslin-v151-simulator.html); this gate confirms
watertightness, the board-02f clearance that changed, and the assembly-level
keep-outs. It does not re-derive the tooth geometry the sim already validates.

## Plates (all black PLA Matte, Stage-1 first per the brief)
- plate-19-calendar-core: 42 sun, 33 month, 34 feb, 35 leap, 40 carrier, 43 spacer
- plate-20-drive-train:   30 drive, 32 camring, 31 sliders, 37 peg pins
- plate-21-accessories:   38 crank, 36 hour ring, 44 post sleeves
