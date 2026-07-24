# Phantom-Pass Sweep — Report (2026-07-08)

Push-classified watershed verification on the real profiles, full year of
board parks. The gating metric is TOOTH-PUSH, not contact: grazes are design
behavior if push < 0.35 pitch (crest 0.5); un-gated ADVANCE is failure.
Tooling: phantom_sweep2.py (+ phantom_sweep.py first pass).

## P1 — PASS: month gating works; watershed confirmed on real geometry
Over a full year the 23h tooth vs the 5-tooth month lamina (OFF=9.75)
produces engagement ONLY at the strike passes; all other passes are clean or
graze with worst push 0.042 pitch — an order of magnitude under the crest.
Zero danger-band events. The paired same-pass "strikes" (az -6 @ 1.04P and
az +6 @ 0.75P) are an enumeration artifact: a skip evening advances the board
TWICE (skip + midnight), so the running machine visits only ONE evening of
each pair — WHICH one is selected by assembly date-clocking. Note the az -6
evening's push is 1.04 pitch = TOOTH-COMPLETED (see S4 note below).

## P2 — OPEN: feb single-tooth fires twice a year in the raw scan
The feb tooth's presentation phase advances 210 deg per monthly pass, cycling
all twelve 30-deg phases annually; the raw scan shows 2 crest-crossing
engagements/yr (0.98P and 0.73P on different passes). Whether the running
machine actually VISITS both depends on the skip-inclusive kinematic
sequence and the chosen engagement parity — the same subtlety as P1's pairs,
but across passes. Needs the sequence-aware sweep (enumerate the true
calendar sequence of parks, not all parks) before declaring pass/fail.
Leap shares the single-tooth phase-cycle exposure; same follow-up.

## P3 — leap slider: one critical margin, one healthy spec
ARMED: push 0.507 pitch — 0.007 pitch (0.08 deg) past the crest. RAZOR-THIN:
FDM noise flips it and leap years silently fail to skip. This is the
sharpest margin in the machine and needs geometry attention in the S4/leap
session (deeper armed reach or wider tooth land).
RETRACTED clearance vs cam travel: 1.0 mm -> 0.060 mm (too thin);
1.2 -> 0.255; 1.6 -> 0.654 (the v1.5 follower stroke: HEALTHY, PASS);
2.0 -> 1.052. Minimum viable travel ~1.15 mm; the 1.6 mm design has ~4x
margin. The retracted-gating half of the leap watershed is confirmed.

## S4 note — resolution path upgraded
P1 found an evening whose month-skip push is 1.04 pitch: the tooth itself
completes the pitch, satisfying the bidirectionality rule from the strike
sweep. If that (evening, clocking) combination also reverses — plausible,
untested due to a board-angle/satellite-spin aliasing my quick probes hit —
then S4 is resolved by ASSEMBLY CLOCKING alone, no geometry change: the
date-clocking must place skips on the az -6 evenings and the satellite OFF
must match. The S4 design session should START with this sequence-aware
clocking search before considering the twin-flank receiver.

## Standing next steps
1. Sequence-aware sweep (calendar-true park sequence): settles P2's feb
   double-fire and executes the S4 clocking search at the exact strike
   angles. Highest priority; reuses all of this tooling.
2. Leap armed-margin geometry (with S4 session).
3. Sun-mesh orbit sweep (7t pinion undercut, continuous mesh) thereafter.
