# Print log — Oechslin perpetual calendar demonstrator

Every job: timestamp · filename · part version · outcome.

## Bench-measurements template

Copy per printed plate. Diagnose WHICH dimension ate the clearance before
choosing a fix — `--xy-compensation` is for uniform extrusion swell only;
a local defect gets a local fix or a v16c geometry change.

```
### Bench — <plate> · <version> · <date>
| Dimension          | Spec  | Measured | Δ |
|--------------------|-------|----------|---|
| Channel gap        | 5.4   |          |   |
| Slider width       | 5.0   |          |   |
| Pin                | 3.2   |          |   |
| Peg                | 1.9   |          |   |

Drag notes:
- Slider 1 (21h):
- Slider 2 (22h):
- Slider 3 (23h):
```

- 2026-07-24 13:45 · plate-01-drive-sliders.gcode.3mf · plate-01-drive-sliders · v16b · DID NOT START — printer (fw 01.10) silently drops LAN start commands in cloud mode; file staged on SD, awaiting LAN Mode + Developer Mode enable and a fresh go
- 2026-07-24 13:56 · plate-01-drive-sliders.gcode.3mf · plate-01-drive-sliders · v16b · DID NOT START — LAN Only Mode on, but start command still dropped; Developer Mode toggle still needed
- 2026-07-24 14:27 · plate-01-drive-sliders.gcode.3mf · plate-01-drive-sliders · v16b · DID NOT START — command still dropped after LAN Only Mode enable + job-clear; Developer Mode still off (or unavailable on this UI)
- 2026-07-24 14:41 · plate-01-drive-sliders.gcode.3mf · plate-01-drive-sliders · v16b · DRY RUN, no parts — gcode had no AMS load block (CLI preset merge skips the machine preset's `include` gcode templates → machine_start_gcode was a stub); AMS never fed (tray_now 255). Stopped deliberately at ~76% (error 50348044 = our cancel). Fixed: include-resolution in compose + audit now gates on M620 AMS block in gcode.
- 2026-07-24 15:08 · plate-01-drive-sliders.gcode.3mf · plate-01-drive-sliders · v16b (attempt 2, AMS fix) · FAILED at layer 15/120 — pusher finger detached from bed (Ron observed); stopped deliberately (50348044 = our cancel). Root cause: bed at 45°C on Textured PEI — the CLI preset merge also skips `inherits` chains, so textured_plate_temp fell to a generic 45 default instead of PLA's 55. Fixed: filament inheritance overlay in compose, bed-temp + filament-id audit gates, post-slice identity re-stamp (GFA01) so the printer's AMS RFID check re-arms.
- 2026-07-24 15:27 · plate-01-drive-sliders.gcode.3mf · plate-01-drive-sliders · v16b (attempt 3, bed-temp fix) · FAILED at layer 17 — sliders detached AGAIN, this time at the correct 55°C bed (50348044 = our cancel). Diagnosis: both failures sit at layers 15–17 = the sliders' final layers (sliders top out at z 3.15 ≈ layer 16); tiny footprints (~3×9 mm each) with growing nozzle drag near completion. Local problem → local fix per doctrine; drive wheel unaffected both times. Awaiting Ron's choice of fix (per-object brim / split plates / glue stick).
- 2026-07-24 15:50 · plate-01b-sliders.gcode.3mf · 31_sliders · v16b (solo plate, attempt 1) · started (outcome pending)
- 2026-07-24 15:57 · plate-01b-sliders · FINISHED with a caveat — ran to 100%, but the middle slider detached at ~layer 16/16 (Ron observed); outer two stayed down (solo plate cured the outer-slider problem from combined plates). Pattern across all attempts: sliders only ever detach at their final layers — suspect last-layer detail passes + perimeter bulge from the −0.45 sink knocking small stiff parts. Bench-verdict pending: outers' dimensions + whether the 96%-complete middle slider is usable.
- 2026-07-24 16:25 · plate-01b-sliders.gcode.3mf · 31_sliders · v16b (solo, rev3: supports) · started (outcome pending)
- 2026-07-24 16:34 · plate-01b-sliders · finished OK — rev3 (solo + plate-only supports + slow finish) ran all 17 layers clean; Ron: parts look great after support removal. First good sliders of the build. Caliper numbers → bench template above when taken.
- 2026-07-24 17:32 · plate-01a-drive.gcode.3mf · 30_drive · v16b (solo, crank grip deferred) · started (outcome pending)
- 2026-07-24 17:58 · plate-01a-drive · finished OK
- 2026-07-24 20:34 · plate-01c-sliders-pegs.gcode.3mf · 31_sliders + 37_peg_pins · v16c (flat, finding-44 fix) · started (outcome pending)
- 2026-07-24 20:44 · plate-01c-sliders-pegs · finished OK — v16c flat-print run: all 14 layers, zero interventions, no supports, no detachments. Finding-44 categorical fix validated at the printer. Bench next: peg press-fit into sliders, slider drag in drive channels, caliper numbers → template.
- 2026-07-25 · BENCH · channel rail break on 30_drive during slider fitting (finding #46) — CA-repaired and serviceable; v16d rail reinforcement pending in a future drive re-emit.
- 2026-07-25 · BENCH · hub crank breakage on 30_drive — 38_crank_module_v16 (press-on crank module) is the field repair; prints disc-down, no source in generator_v16.py (hand-authored).
- 2026-07-25 05:58 · plate-01d-v16d.gcode.3mf · v16d plate (sliders + pins + crank module) · started (outcome pending)
- 2026-07-25 · BENCH · sliders have poor sliding motion, and lose alignment as they extend — nothing guides the outboard end once the plate leaves the rails (Ron). Mesh analysis of the v16fullset wheel: changes are rail reinforcement + near-hub ring only (all within r≈29; rim at 32.8) — NO outboard guidance added; the failure mode is not addressed in the staged geometry. Needs a design-office fix (rim-side capture/guide); v16d generator still not delivered.
- 2026-07-25 06:20 · plate-01d-v16d · finished OK, then SUPERSEDED — ran to 100% (105 layers, clean) before the v16d full-set drop landed; parts are from the interim generation. Superseded by plate-02-v16d-set (reinforced-rail wheel + revised 31/37/38).
- 2026-07-25 09:16 · plate-03-camring.gcode.3mf · 32_camring · v16 (outboard guide) · started (outcome pending)
- 2026-07-25 09:28 · plate-03-camring · finished OK
- 2026-07-25 10:24 · plate-02-v16d-set.gcode.3mf · v16d full set + seat markers · started (outcome pending)
- 2026-07-25 · BENCH · finding #48: middle-channel obstruction and slop — root-caused to fan self-intersection in the channel architecture; fixed in v16e (outboard furniture, bisector wedges, gate A14). v16e r1 shipped with a degrees/radians emission bug (edge rails/lips/wedges axis-aligned; the 21h outboard lip orphaned mid-air) — caught by the console's mid-air gate, the only working detector in the pipeline that day (design office skipped its own A10 census); fixed in r2 (finding #49).
- 2026-07-25 · BENCH · over-travel note for future sessions: the slider's working envelope is the span between the two friction-dome marks; the travel STOP is the cam groove by design — an unmounted slider is a free body and will happily slide out of the channel. Not a defect; assemble the camring before judging travel.
- 2026-07-25 11:05 · plate-02-v16d-set · finished OK — full v16d set in one clean run (105 layers, no interventions): reinforced-rail wheel with seat-indicator bars, revised flat sliders, drop-in pins, spare crank module. Third consecutive zero-intervention print. Bench: full subsystem assembly with camring.
- 2026-07-25 12:26 · plate-03-wheel-camring.gcode.3mf · 30_drive v16e r2 + 32_camring (findings 48-49) · started (outcome pending)
- 2026-07-25 12:58 · plate-03-wheel-camring · finished OK — v16e r2 wheel (fan fix, outboard furniture, bisector wedges) + camring in one clean run, 75 layers, fourth consecutive zero-intervention print. Known caveat carried: camring middle-track thin rings start at layer 2 (slicer min-feature; identical to the already-benched ring). Bench: full finding-48 subsystem — v16e wheel + ring + v16d sliders/pins.
- 2026-07-25 13:31 · plate-04-fixture-carrier.gcode.3mf · 39_bench_fixture + 40_ring_carrier (bench tooling) · started (outcome pending)
- 2026-07-25 14:45 · plate-04-fixture-carrier · finished OK — bench fixture + ring carrier, 120 layers, fifth consecutive zero-intervention print. Bench tooling complete: fixture gives true axis spacing, carrier seats the camring at board-top height (also moots the ring's layer-1 caveat in use). Full v16e subsystem + tooling now printed.
- 2026-07-25 16:11 · plate-06-v16f.gcode.3mf · v16f detent mount: camring + pins +0.45 + files7 wheel (finding 55) · FAILED at layer 29/75 — camring spaghettied (Ron observed, camera-confirmed); stopped deliberately (50348044 = our cancel). Root cause: the clocking spider's ~24mm bridges at 0.55mm altitude — too low to sag-and-catch; strands dragged and destroyed the ring. The flagged bridge risk should have been a stop-and-tell, not a caveat (console doctrine updated). SALVAGE: 8 pins complete (they finish by ~layer 16) — harvest; wheel was cleanly formed at stop but incomplete. Finding for design office: the v16f spider needs a printable foundation — ≥3mm bridge altitude, legs under arm midpoints, or emit the spider as a separate flat jig.
- 2026-07-25 16:56 · plate-06a-v16f-nospider.gcode.3mf · v16f ring (spider dropped) + files7 wheel · finding 55 reprint · started (outcome pending)
- 2026-07-25 17:28 · plate-06a-v16f-nospider · ran to 100% but MIXED — wheel correct (Ron confirmed); camring spaghettied AGAIN despite spider removal. Root cause #2: the ring body overhangs the 31-segment skirt band circumferentially (inner 2.6mm / outer 4.5mm cantilevers at 0.55mm altitude) — unsupported perimeter loops droop and drag. The v16f detent architecture cannot print bare; needs a raft (or design-office wall-footed skirt). Wheel harvested.
- 2026-07-25 17:39 · plate-06b-camring-raft.gcode.3mf · 32_camring v16f solo on raft (finding 55, attempt 3) · started (outcome pending)
- 2026-07-25 · plate-07: architecture audition — patent-literal fixed fingers (v1.3) vs cam-gated sliders (v16), comparative bench trial; day-30 cross-talk is the predicted failure mode to watch for. Audit result: 02_program_wheel + 04_month_wheel clean and staged; 10_drive_wheel NOT stageable — emitted pin-down (drive pin is the lowest geometry, functional), and flipped per the v1 README its disconnected crank post (the ancestral finding-45 gap) becomes the bed contact with the body hovering 10mm. Fix path if wanted: flip + drop post + overhang fingers.
- 2026-07-25 17:54 · plate-06b-camring-raft · finished OK — v16f detent ring printed intact on the third attempt (solo + raft + spider dropped); camera shows a clean annulus, no spaghetti. The v16f skirt architecture requires a raft until the design office ships wall-footed skirt geometry (finding logged). Bench: peel raft, check detent feet, snap onto board tick bumps.
- 2026-07-25 18:42 · plate-07-audition.gcode.3mf · v1.3 audition: program wheel + month receiver (fixed-finger trial) · started (outcome pending)
- 2026-07-25 19:23 · plate-07-audition · finished OK — v1.3 program wheel (31 rim teeth verified in toolpaths) + month receiver, all 62 layers clean. Audition bench: fixed-finger trial vs v16 sliders; check the board top face for tick bumps (mesh says absent → v16f ring detent-mount compatibility question); 10_drive_wheel still held pending flip+post-drop surgery (plate-07b on request).
- 2026-07-25 · BENCH · Arm A assembled: v1.3 board + fixed-finger drive wheel meshed on the fixture; daily advance functional; full 31-position referendum crank in progress.
- 2026-07-25 · BENCH · Finding #56: the v16f spider's 0.55 mm bridge altitude — unprintable as emitted (two spaghetti failures); the console's field drop of the spider was correct. Design office owes a printable spider foundation (≥3 mm bridge altitude, mid-arm legs, or separate flat jig).
- 2026-07-25 · BENCH · Finding #57: the ring carrier's rim intrudes the daily tooth's swept circle — carrier retired from meshed service.
- 2026-07-25 · BENCH · Finding #58: the drive wheel's witness dot (0.8 proud, near the 23h arm) grazes the board's tooth tips at mesh — no mechanical function, shaved flush at the bench. Design office owes: markers relocated out of the mesh overlap band + a marker-clearance gate in the next wheel emission.
- 2026-07-25 · BENCH · Finding #59: stale-STL vintage mismatch — the audition board (stl_v13 emission) is bumpless: it predates the tick-bump code in the current generator source (console audit caught this pre-print). Arm A unaffected (rim teeth + satellite post present); Arm B's v16f detent ring indexes on those bumps. Doctrine: audition prints on trust are fine, but any part entering a fit-critical interface gets regenerated from current source and gated first.
- QUEUE (pending referendum verdict — if Arm A sweeps its 31 positions, next plates may be a different architecture entirely): v16f-r2 ring (raised plane, real key cavity, printable spider foundation per the ≥3 mm spec); #58-clean wheel emission (markers out of the mesh overlap band + marker-clearance gate); fresh 02_program_wheel regeneration from current source with the full gauntlet (finding #59) — REQUIRED before any Arm B session unless Ron confirms the originally-printed board carries the bump circle and tall pos-1 witness on its face.
- 2026-07-25 20:56 · plate-08-crank.gcode.3mf · 38_crank_module spare (referendum bench) · started (outcome pending)
- 2026-07-25 21:14 · plate-08-crank · finished OK
- 2026-07-25 21:28 · plate-07b-jumper.gcode.3mf · 12_jumper v1.3 flexure (audition pair) · started (outcome pending)
- 2026-07-25 21:36 · plate-07b-jumper · finished OK
- 2026-07-26 05:53 · plate-09-fixture-r2-arm-a.gcode.3mf · fixture r2 + Arm A hardware (surgical wheel, jumper, sun tower) · started (outcome pending)
- 2026-07-26 07:39 · plate-09-fixture-r2-arm-a · finished OK — all 138 layers: fixture r2 (sun key, shoulder, jumper wing), surgical drive wheel (no pin/post), spare jumper, sun tower. Arm A moves to real tooling.
- 2026-07-26 · BENCH · Finding #63 CLOSED + wobble doctrine: receiver rides spacer 43 above the tick bumps; gravity-seated for the audition (planar loads only — adequate); cap_sat is the designed retention, queued (inspected: one-piece, consistent winding, spigot bore open in toolpaths — render-verified).
- 2026-07-26 09:10 · plate-10-referendum-set.gcode.3mf · referendum set: fixture r4 + jumper + sun + spacer (findings 60-64) · STOPPED at layer 0 on Ron's order, still in warm-up — no material laid; file remains staged on SD for a clean restart.
- 2026-07-26 09:28 · plate-10b-referendum-set.gcode.3mf · referendum set + board (findings 60-64) · started (outcome pending)
- 2026-07-26 · DESIGN BACKUP · rotational-gear jumper (Ron): rotary positive indexing in place of the flexure — ancestors in the notes: patent Geneva-lock (patent-review.md L28), v1 springless locking-disc, and skip-redesign-session2 option (B). Constraint any rotary design must satisfy: disengage/freewheel during month-end 1-4 step cascades (the recorded reason the rigid lock was retired for the flexure). Held as backup if the PLA/PETG flexure fatigues in referendum service.
- 2026-07-26 11:03 · plate-10b-referendum-set · finished OK — all 120 layers: fixture r4, v1.3 board, open-bore jumper, square-bore sun, receiver spacer. Thermal doctrine ran live (215C body). The referendum endgame kit is printed.
- 2026-07-26 · DOCTRINE · finding 69: gear pairs are matched-vintage sets; stale receiver vs current sun = interference; meshing parts regenerate together henceforth. First application: 33_receiver_month regenerated from the files13 generator — byte-identical to the repo copy, vintage-match confirmed by regeneration rather than trust.
- 2026-07-26 · Finding #70: 33_receiver_month's witness dot floats 1.6mm above the hub top (anchored at a stale height since the original emission; ray-parity verified). Field drop for plate-11 — mark station k=0 by hand per the clocking table; design office owes a re-anchored dot.

- 2026-07-26 12:28 · plate-11-jumper6-receiver.gcode.3mf · jumper v6 + receiver (findings 67-70) · started (outcome pending)
- 2026-07-26 12:48 · plate-11-jumper6-receiver · finished OK — all 40 layers: jumper v6 (long-spring rounded beak) + receiver (dot dropped, mark station k=0 by hand). The current program is fully printed.
- 2026-07-26 · SESSION TAIL · Finding #70 (broadened; supersedes the narrower floating-dot entry above): v16 receiver fingers unrooted — features anchored at stale heights; design office owes 33 r2 next session. Findings #71–73: jumper beak iterations (long-spring V, rounded beak, culminating in Ron's rod-and-ball with the head bench-gauged to r4.4 against the actual board teeth). DOCTRINE reminder: matched-vintage pairs only — tonight's stack runs the v1.3 sun + receiver together.

- 2026-07-26 14:17 · plate-12-jumper-v9.gcode.3mf · jumper v9: rod-and-ball, bench-gauged head (findings 72-73) · started (outcome pending)
- 2026-07-26 14:27 · plate-12-jumper-v9 · finished OK — all 18 layers: rod-and-ball jumper, bench-gauged r4.4 head (findings 72-73). Ninth jumper iteration, first designed at the bench.
- 2026-07-26 · finding 74: bearing sleeves (44_post_sleeves) — mesh clearance stack; verified grounded, queued as plate-13 solo (~5 min).
- 2026-07-26 · CLEANUP LIST (next session): (1) generator carries a harmless duplicate acceptance_43 definition from an earlier edit — deduplicate; (2) receiver r2 (finding #70: re-rooted fingers + re-anchored witness dot).
- 2026-07-26 · SESSION TAIL · Finding #74: bearing clearance stack → post sleeves. Finding #75: jumper reach — head center pulled 1.25mm deeper (44.5 from board axis) to seat in the valley instead of grazing tips; rod 1.3→1.8 for real preload. Sleeve-first doctrine: fix the datum before tuning the instrument. BENCH STATE: v9 installed and tip-riding pre-sleeve; v10 is the post-sleeve contingency; matched v1.3 sun+receiver pair staged for the referendum; receiver 33 r2 and the duplicate acceptance_43 cleanup are the design office's openers next session.

- 2026-07-26 14:54 · plate-13-jumper10-sleeves.gcode.3mf · jumper v10 + post sleeves (findings 74-75) · started (outcome pending)
- 2026-07-26 15:09 · plate-13-jumper10-sleeves · finished OK — all 63 layers: jumper v10 (seating reach, 1.8 rod) + six-sleeve fit ladder. Sleeve-first doctrine ready to run at the bench.
- 2026-07-27 · HOUSEKEEPING · findings 74–86 record:
  · #74 bearing clearance stack (0.85 mm) → sleeve ladder → fitted; sleeves now being absorbed into bore lands, part 44 retires.
  · #80 the v1.3 sun cannot key on the r4 square post (1.31 mm gap) — matched gears isn't enough, the sun must match the post.
  · #83 the detent arm sees compression in reverse; taller-and-narrower section fixes buckling and cuts fwd/rev asymmetry 14% → 2%.
  · #85 WITHDRAWN — a Geneva locking disc was claimed; there is none.
  · #86 the drive wheel body clears the board tips by 2.44 mm by design — a rigid lock would block the month-end cascade, so the jumper is the machine's sole index. The plate-09 mid-air drop was correct: the amputated pin was the WEEKDAY pin, not the daily driver — the daily tooth is present and working. Do not drill the wheel; part 48 is withdrawn (archived in parts/stl for the record).
- 2026-07-27 · Repo sync notes: 02_program_wheel current-source verified (31 tick bumps + tall pos-1 witness in mesh census — finding #59 satisfied); 44 unchanged (already current); 42_sun r2 "full column" NOT yet landed (repo copy is yesterday's — awaiting drop); generator not in this drop (files17 copy stands). Printability flags for future plates: 45 and 46 carry small mid-air features (borderline heuristic; re-check at compose time).
- NEXT SESSION plate: detent star ring, roller + pin, fixture r5 (pocket, anchor, mid-span guide), arm r3, receiver 33 r2.
- 2026-07-27 · sun r2 full column landed (10.00mm verified — the wafer tripwire caught nothing this time) + current generator (gates through A36; the duplicate acceptance_43 persists — cleanup item stands). Parts 45 (wire jumper holder) and 46 (wedge set) are SUPERSEDED — the wire branch of the detent lost to the printed arm with the cam adjuster; their mid-air printability flags need no action; archived in parts/stl alongside withdrawn part 48. Nothing composes today; next session's plate stands as recorded.

