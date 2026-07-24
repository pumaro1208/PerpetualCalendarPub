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
