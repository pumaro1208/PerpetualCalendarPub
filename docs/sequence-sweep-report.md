# Sequence-Aware Sweep — Report (2026-07-08)

Walks the engine's TRUE calendar sequence of board parks (skips included) and
evaluates every 23h/22h drive-tooth pass at the exact board angle and
satellite spin the machine will occupy. Tooling: sequence_sweep.py; the
calendar walker + per-pass push classification are the standing acceptance
harness for the skip-transfer redesign.

## Headline: NO clocking window exists for the month or feb laminas
Scanned 61 month clockings and 241 feb clockings against the full
calendar-true year. None produces the required pattern (every logical strike
engages >= 0.5 pitch; every other visited pass gated < 0.35 pitch).

The autopsy at the best candidate clocking (month, OFF = 9.75) shows WHY —
both failure classes coexist:
 - FALSE STRIKES: the eve-of-skip evenings (satellite az -5.8) engage at
   1.042 pitch on several months (n = 121, 214, 276, 338) plus stray az +5.8
   engagements on non-skip months (n = 215, 370). Each is a full extra step:
   the calendar runs FAST.
 - MISSED STRIKES: two of the five logical skip evenings get no engagement
   (n = 184) or a 0.042-pitch graze (n = 339): the calendar runs SLOW.
No clocking trades these off to zero simultaneously. Verdict supersedes the
phantom sweep's all-parks PASS (which averaged over parks the sequence never
visits and missed the visited-sequence correlations).

## Finding S7 — the skip gating as built cannot serve the calendar
The presentation-phase engagement window of the current lamina tooth form is
WIDER than one station on the approach side (hence eve-of-skip false strikes)
while the nominal-side engagement varies 0.75 -> 0.04 -> 0 pitch across
evenings the 30-deg station-lattice theory says are equivalent — the physical
engagement depends on approach geometry in a way the lattice doesn't capture.
(The lattice discrepancy itself is an open analysis item for the session; the
empirical verdict does not depend on resolving it.)

## S4 status: clocking resolution is DEAD; redesign confirmed
The hoped-for fix-by-witness-marks is closed. The skip-transfer design
session is confirmed necessary, now with the full requirement set measured:
 R1 bidirectional: tooth-completed push >= 1.0 pitch both directions
 R2 selective: presentation window narrower than one evening's phase step
    (no eve-of-skip engagement)
 R3 reliable: >= 0.65-pitch push margin at every legitimate strike (the
    leap's current 0.507 shows what 0.007 margin looks like)
 R4 gated: all other visited passes < 0.35-pitch push
The twin-flank slot receiver remains the lead candidate: a slot is engaged
positively in both directions (R1), only when entered (R2), and its
engagement depth is designable (R3). Every candidate gets judged by
sequence_sweep.py before any STL is cut.

## Stage 1 print decision (updated)
Hold: sun tower, all three satellites, leap sliding tooth (the skip train —
S4/S7 redesign scope). Clear to print: everything else in the engine — base,
board, drive wheel, jumper, carriers, caps — the daily drive is fully
verified (S1/S2), and the S3 margins are bench items on exactly these parts.
Printing the cleared set banks bearing/detent/double-step data that feeds
the redesign.
