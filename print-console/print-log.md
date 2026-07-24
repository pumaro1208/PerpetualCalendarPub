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
- 2026-07-24 14:41 · plate-01-drive-sliders.gcode.3mf · plate-01-drive-sliders · v16b · started (outcome pending)
