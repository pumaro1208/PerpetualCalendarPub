# Oechslin Program Wheel Demonstrator — v1
Printable homage to EP 1351104 Embodiment 1 (Ludwig Oechslin / Ulysse Nardin, expired 2022).
Hand-cranked: **one crank revolution = one day.** The program wheel makes one revolution per month, advancing 1–4 steps at month end exactly as the UN32 does.

## What v1 demonstrates
- 31-step program wheel advanced daily by a drive pin with springless locking-disc indexing
- Month satellite (12t, teeth 7–11 long) — one extra skip at the end of Feb/Apr/Jun/Sep/Nov
- February satellite (12t, tooth 7 long) — the second February skip
- Leap slider + 28-station Geneva cam — the third February skip, withheld every 4th year
- The staged 21:00 / 22:00 / 23:00 / 24:00 engagement sequence, visible in slow motion

## Print settings
- **Material:** PETG for all gears, satellites, geneva/cam, slider, drive wheel. PLA fine for base plate and caps.
- 0.2mm layers, 3 walls, 25% infill, no supports.
- **09_drive_wheel prints UPSIDE-DOWN** (finger side on the bed) — it is modeled that way? No: it is modeled assembly-up; flip it in the slicer (Rotate 180° about X) so the widest finger level sits on the plate.
- Everything else prints in the orientation modeled (flat face down).
- Print 4 copies of `10_cap_sat` (three satellite posts + cam post).

## Assembly (staged — test each stage before adding the next)

### Stage 1 — Date-only
1. Base plate flat; drop the **program wheel** over the central post (tick bumps up). It rests on the three thrust pads.
2. Fit the **drive wheel** over the drive post, pin at program-tooth level. Cap it.
3. Crank: each revolution should index the program wheel exactly one tooth, and the locking disc should hold it between steps. **Tune here first** — if indexing binds, scale the drive wheel 1–2% down in the slicer or ease `finger_clear_r`/pin size in `generator.py`. Nothing downstream works until Stage 1 is smooth.

### Stage 2 — Month logic (30/31)
4. Key the **sun tower** onto the central post D-flat. It must NOT rotate.
5. **Month wheel** onto its post (station at the alignment dot; long teeth are the 5 consecutive ones), meshing the sun's lower band. Cap it.
6. **Phasing:** set the program wheel to "1" (tall tick at the base-plate pointer). Rotate the month wheel on its mesh so that its *first long tooth (index 7)* will arrive at the drive-finger zone at the end of the second month from now — i.e., treat "now" as January 1. Simplest method: temporarily set the program wheel to Feb 28 position (tick 28), and clock the month wheel so long tooth 7 projects into the finger sweep path; then wind back to 1.
7. Crank through a month: 30 cranks, then watch the 23:00 finger pick up the long tooth and the midnight pin complete the advance.

### Stage 3 — February
8. **February wheel** onto its post at the LB level (same phasing method: its single long tooth presents only at the February month-end). Cap it.

### Stage 4 — Leap train (experimental)
9. **Leap satellite** (gear + pin + locking disc) onto its post at LA level.
10. **Geneva cam** onto the cam post: geneva slots at LB level engaging the leap satellite's pin, cam ring at LC level. Cap it.
11. **Slider** into the LC rails: follower foot toward the cam, tooth outward. Clock the cam so the *valley quadrant marker* faces the slider follower on the year you want to be the leap year.
12. In years 1–3 a cam lobe holds the slider OUT (tooth projecting); the 21:00 finger strikes it at Feb-end for the third skip, and the strike itself pushes the slider back only if the cam permits — with a lobe underneath it stays out and simply transmits the push to the program wheel. In year 4 the valley lets the 21:00 finger sweep past a retracted tooth: February gets 29 days.

## The month-length arithmetic (sanity check while cranking)
| Month end | Fingers that fire | Steps | Days shown |
|---|---|---|---|
| 31-day | midnight pin only | 1 | 31 |
| 30-day | 23:00 + midnight | 2 | 30 |
| Feb (common) | 21:00 + 22:00 + 23:00 + midnight | 4 | 28 |
| Feb (leap) | 22:00 + 23:00 + midnight | 3 | 29 |

## Known v1 risks / tuning knobs (in `generator.py`)
1. **Finger ↔ long-tooth engagement depth** — the whole game. `long_extra` (default 3.5) and `finger_clear_r` (42.8) set the overlap at ~2mm. If fingers graze, raise `long_extra` to 4.0; if they jam, drop to 3.0.
2. **Locking-disc indexing** (Stage 1) — relief-notch width is hand-tuned; watch for over-rotation on the daily step.
3. **Geneva slot fit** — 28 stations at r=11 means fine features; if slots print tight, scale `geneva_r` up and reprint just part 07.
4. **Satellite mesh backlash** — 7t/12t rounded-trapezoid teeth are deliberately sloppy (`backlash` 0.45). They only need to *index*, not transmit power smoothly.
5. Rails/slider fit — sand the slider edges; it should slide under finger pressure but hold position by detent friction.

## Relationship to the ST2525 project
Stage 2 is the part to study: a long tooth presenting once per month at a fixed angular window, struck by a dedicated finger one hour before the daily advance. That is exactly the pickup architecture you need to graft onto the ST2525 — the question it answers physically is how much angular window and radial overlap a reliable once-per-month engagement needs.

## Files
| File | Qty | Notes |
|---|---|---|
| 01_base_plate | 1 | posts integral |
| 02_program_wheel | 1 | posts + rails integral |
| 03_sun_tower | 1 | D-keyed, must not rotate |
| 04_month_wheel | 1 | 5 consecutive long teeth |
| 05_february_wheel | 1 | 1 long tooth |
| 06_leap_satellite | 1 | gear + geneva pin + lock |
| 07_geneva_cam | 1 | 28 stations + 3-lobe cam |
| 08_leap_slider | 1 | PETG, sand to slide |
| 09_drive_wheel | 1 | **flip in slicer** |
| 10_cap_sat | 4 | posts |
| 10_cap_main / 10_cap_drive | 1 ea | |

Generated parametrically — `generator.py` is included; edit parameters at the top and rerun (`python3 generator.py`) to regenerate all STLs.
