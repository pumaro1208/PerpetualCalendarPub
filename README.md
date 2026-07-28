# v1.6 PATCH — architecture A' (cam-gated slider strikers + E1 receivers)
Authorized by Ron 2026-07-09. Sim b40 is the functional spec of record.

## Parts (print all in PLA Matte Charcoal — rotating)
- 30_drive_v16 — drive wheel re-head: body + long tooth + hub/crank + THREE
  radial slider channels at 15/30/45 deg (rails z4.0-8.0, lips 7.1-8.0,
  floor pads 4.0-5.2, detent bumps at both seats). Witness dot = 23h channel.
- 31_sliders_v16 — three sliders on one plate. ID dots: 3=23h, 2=22h, 1=21h.
  DISTINCT NOSE LENGTHS: each slider reaches only its own cam track —
  cross-assembly is physically impossible. Strike pin r1.6, band 5.2-8.0.
- 32_camring_v16 — board-top ring (z 4.05-4.75, OD 41.6): three blind groove
  tracks at world r 34.6/37.4/40.2 (23h/22h/21h), lobes (1.6 mm inward) at
  board positions 30/29/28, dwell 1.35 pitch, cosine ramps. Witness dot =
  pos-1 at the OD. Mount: seat on board top, clock the dot to the mesh line
  with the board at Jan 1 (pos 1); thin CA at three points. Registration
  tolerance +/-3 deg (harness G4) — witness clocking suffices.
- 33_receiver_month_v16 — month satellite lamina: mesh profile + spacer hub +
  FIVE E1 involute strike teeth (patent claim 5 form) at 30-deg stations,
  base 6 deg. Witness dot marks station k=0.
- 34_receiver_feb_v16 — single-tooth E1 lamina, same construction.
- 35_leap_shuttle_v16 — the v1.5 leap shuttle re-headed with the E1 tooth;
  the Geneva year key is unchanged (follower pin preserved).

## The cam law (normative, sim-derived)
Striker extended ONLY on its strike evening. Lobe map (400-yr engine sweep):
21h->pos 28, 22h->pos 29, 23h->pos 30 — one lobe per track; the cascade
itself walks the board through the positions, arming each striker in turn.
Stroke 1.6 mm; retracted adjacency clearance 2.54 mm emitted (harness 1.23).

## Acceptance (all 19 gates PASS; all 6 parts watertight, 0 open edges)
Fit: channel gap 5.4 / slider 5.0; lip retention 0.5/side; peg d2.4 in
groove 2.7 (0.35 mm wall engagement). Register: extended pin = FINGER_R
30.70 exact, peg valley/lobe = track radii exact, lobes verified at the pos
lattice and flat elsewhere. Keep-outs: ring OD 41.6 vs pin sweep 42.8;
nose-over-ring 0.45 mm; strike bands identical by construction (5.2-8.0).
Harness lineage: stroke, E1 profile, and station base are the EXACT
parameters judged in arch_a_prime.py (G1 1.13P/1.33P bidirectional, G2
silent, G3 1.23 mm, G4 +/-3 deg) — the emitted parts and the judged
mechanism share one parameter set.

## Bench items on first assembly (Stage 1.5)
1. Slider slide-fit after printing (scrape lips if needed; PTFE dry lube).
2. Detent click at both seats; peg engagement depth 0.35 (verify no lift-out).
3. The characterized 23:15 tight passage: midnight finger entry clearance
   against the mid-push board (from the sim's grind log).
4. Reverse un-skips: park -> pickup -> push, per sim b40.

## Receiver clocking table (harness-judged, 2026-07-09)
Each lamina's witness dot clocks to its satellite per this table. The base
window is the selectivity margin; center it.
| train    | satellite | station (carrier) | judged base | passing window |
|----------|-----------|-------------------|-------------|----------------|
| month 23h| 210       | STN_M (reference) | 180.0 deg   | (session 3)    |
| feb 22h  | 211       | STN_M + 1 pitch   | 315.0 deg   | 310.0-320.0    |
| leap 21h | 212       | STN_M + 2 pitches | 335.0 deg   | 327.5-340.0    |
The station offsets are the natural carrier positions of satellites 211/212
(one and two cascade steps ahead of 210) — the harness confirms the
assignment; no new posts required.

## Part 36 — friction-set hour ring (roadmap tier 1, added 2026-07-19)
Press-fit indicator ring on the drive hub: three printed flex fingers grip
the hub column at 0.15 mm interference each (the cannon-pinion principle,
in PLA); the pointer flag reads the displayed hour. USE: after any fast
catch-up cranking (the drawer scenario), twist the ring by hand to restore
the true hour — date advanced, displayed time preserved, the outcome of
the UN-32's date position with one part and zero mechanism. Rides z
8.6-11.6, 0.6 mm above the channel tops; only the fingers touch the hub.
BENCH: verify twist friction is firm but hand-turnable; if too tight,
scrape one finger; if loose, a strip of tape on the hub shims it.
STAGE-C NOTE: the true date-ONLY drive (hands stationary while the
calendar advances) is the keyless-works dog clutch — deliberately deferred
to the watch stage per ROADMAP-clock-watch.md.

# FLAG-FREE DETENT SET (findings 97–99 + coupling redesign, 2026-07-28)
The machine's sole index. The daily drive advances the board; this detent settles
it onto each day's position and holds it. Reversibility is preserved (flexure, not
ratchet). All parts PLA (rotating parts black), print FLAT, no supports.
Regenerate the whole set with `parts/emit_final.py`; gate is `qc_sweep_central.py`.

## Parts
- 02e_board_bigbore — the v1.3 program board (31 involute rim teeth, tip 41.86;
  31 day-tick bumps at r33.5 with the tall pos-1 witness; month satellite post +
  D-key), UNCHANGED except the central bore opened 8.7 → 10.9 mm to take the star's
  press-tube. Prints teeth-up, flat on the bed. THE ONE PART RE-PRINTED from the
  bench (bigger bore is the only change).
- 50d_star_hub — detent star, flag-free. 31 symmetric shallow-triangle notches
  (root 26, tip 28.5 → 2.5 mm deep) on a scallop disc, plus an integral CENTRAL
  press-tube (ID rides the program post, OD press-fits the board bore) that couples
  the star rigidly and concentrically to the board — no outrigger, no drop-in pin.
  Prints scallop-down, tube rising. Rides the post; board seats on the disc top;
  the disc spins on the fixture thrust pad.
- 49_fixture_r58 — basin bench fixture: program + drive posts (square-key sun seat),
  drive collar, a central THRUST PAD the star disc spins on (replaces the program
  collar), and the two bridge-jumper anchor pins at r30.5. Wedge station = 270°.
- 51_bridge_arm — the bridge jumper (finding #99). A pinned-pinned flexure (span 35
  between the boss inner edges; both pin bores OPEN top-to-bottom, finding 64/93),
  1.05 mm wide, carrying a POINTED wedge at mid-span: a sharp apex reaching r27.0
  (clear jump into each notch) with wide shoulders that bear on BOTH tooth flanks
  (geometry centers it). Loaded identically forward and reverse. Beam pulled in to
  r30.5 so the riser is short (~2.2 mm) — the sideways tooth force has little lever
  arm to twist the wedge. k = 0.62 N/mm; peak 23 MPa (2.2× PLA) at the 1.5 mm stroke.

## Design laws honored
Reversibility — pinned-pinned flexure is symmetric fwd/rev, positive transfer, no
ratchet. Full-depth notch + short pointed wedge = a positive index with a light,
clean jump. Both press fits are interference — no glue. The gate in the repo
(qc_sweep_central.py) is the gate that cleared this plate (finding 96 doctrine).

## Bench items on first assembly
1. Star central tube → board bore: designed interference press; tune on first fit.
2. Bridge pins → anchor bores: interference; bores print open top-to-bottom.
3. Wedge drops into each notch with a clear click and self-centers on both flanks;
   verify no twist as the board sweeps its 31 positions.
4. Star disc spins freely on the thrust pad; board seats flat on the disc top.

## Board 02f — pegless/dotless (engine clearance sweep, 2026-07-28)
02f = 02e with the 31 perimeter day-tick pegs (r33.5) AND the three station witness
dots (r35.05) REMOVED. The engine interference sweep (parts/engine_sweep.py, disc-
about-fixed-pivot model, frame self-checked against the sun↔month mesh) found that
on 02e the tall day-1 peg (+0.8mm) and station dots M/F (+0.2mm) poke up into the
MONTH satellite's mesh lamina (underside z10.4) even with the finding-63 spacer —
the 30 short pegs clear by 0.4mm, but those three do not. 02f leaves zero raised
obstacles on the board face except the intended satellite pivot post; the sweep
reports CLEAR. Involute rim, 10.9 press-bore, and the month post + D-key are
UNCHANGED, so the flag-free detent press-fit (star tube -> board bore) is unaffected.
Sun tower confirmed correctly configured (spans LA/LB/LC, meshes at altitude).
02f SUPERSEDES 02e for the reprint. See docs/engine-clearance-sweep.md.
