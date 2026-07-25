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
- 2026-07-25 06:20 · plate-01d-v16d · finished OK, then SUPERSEDED — ran to 100% (105 layers, clean) before the v16d full-set drop landed; parts are from the interim generation. Superseded by plate-02-v16d-set (reinforced-rail wheel + revised 31/37/38).
