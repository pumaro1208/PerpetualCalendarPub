# Strike-Transit Sweep — Physical Acceptance Report (2026-07-08)

Quasi-static 1-DOF contact simulation of the strike transfers using the ACTUAL
generator profiles (31t stub involute board, 24t-basis stub drive tooth at the
+2.0 mm spread center distance, v1.3 strike lamina with symmetric crown, and
the real v1.2 jumper V-nose geometry, detent-coupled). Tooling:
strike_transit_sweep.py + lamina_bidir scans; results in sweep_results.json.

## S1 — CLEARED: the jumper's inherited clocking is correct
Solved from geometry, no assumptions: the V-nose's deepest seat parks the
board with a tooth VALLEY centered on the mesh line to 0.025 deg. The v1.2
jumper at 12 x PITCH is correctly clocked for the v1.3 drive. Detent snap is
strong (seat-vs-crest depth asymmetry ~270:1). Park-error tolerance window
for a clean transit: -1.0 .. +4.0 deg. The pre-print worry is retired;
the bench check remains (verify the printed park phase lands in-window).

## S2 — PASS: the daily (midnight) transfer is fully bidirectional
Forward: settled advance exactly 1.0011 pitch (solver resolution). Reverse:
exactly 1.0000 pitch back. Measured physical backlash: the board holds
through 24.3 deg of reverse crank (~1.6 h of crank time) before the reverse
push begins — this is the documented expectation for the reverse-cranking
bench test, not a defect. Bidirectionality of the daily drive comes from
MULTI-TOOTH interaction: the drive tooth itself carries the board 1.41
pitches (catching the next board tooth), so the tooth — not the detent —
completes the pitch in both directions.

## S3 — MARGIN FLAGS on the daily transfer (bench-first, geometry-second)
(a) Forward excursion reaches 1.412 pitch: only 1.02 deg (~0.75 mm of flank
position) short of the next detent crest. Past it = DOUBLE-STEP (skips a
day). (b) Nominal entry approach clearance is 0.021 mm — a graze. Both sit
inside typical FDM error. Plan: measure on the Stage 1 print first (count
double-steps over a simulated month of cranking; listen for entry clicks);
if real, the fixes are small (drive-tooth tip relief, +0.3 spread) and cheap
to regenerate. Not a print blocker by itself.

## S4 — DESIGN FLAW: all satellite strikes are FORWARD-ONLY as built
The month lamina's tooth-only push is 0.753 pitch; the JUMPER completes the
remaining 0.247. That completion is irreversible: reversing, the descending
drive tooth arrives to find the lamina a quarter-pitch beyond reach and
passes through empty space. Verified exhaustively: no satellite clocking
(121 scanned, mod 30), at either candidate strike evening (satellite at
-5.83 or +5.78 deg), with lamina reach extended up to +1.3 mm, produces a
reverse-capable transit. The feb and leap laminas share the single-tooth
geometry class: the same result applies to the 22h and 21h strikes.

Consequence: reverse-cranking through any month-end cannot un-do the skip.
The board un-steps daily but the skips stand — the calendar de-syncs. This
violates design law 1 (full bidirectionality), which the simulator's engine
assumes ("reversing: month skip undone" is real in the spec, unimplementable
in the current laminas).

THE RULE THIS EXPOSES (add to the design laws' commentary): a strike
transfer is bidirectional only if the TOOTH ITSELF pushes >= 1.0 pitch; any
completion delegated to the detent is a one-way ratchet in disguise. The
board drive satisfies it via multi-tooth contact; a single-tooth lamina
cannot (single-flank contact arc maxes near 0.75 pitch at this geometry).

Fix directions for the design session (transfer must be PROVEN before
geometry, per project protocol):
  1. Asymmetric lamina tooth: extend the reverse flank so the descending
     tooth catches it despite the detent's completion (~5-7 deg wider on one
     side); requires phantom-pass clearance checks on adjacent evenings.
  2. Twin-flank receiver: two short teeth per station forming a slot the
     drive tooth enters — contact on either flank by direction (Geneva-like,
     positive both ways).
  3. Reduce detent completion authority for skip strikes (deeper conjugate
     engagement via module/center-distance changes at the strike bands).
Option 2 is the one that satisfies the >= 1-pitch-push rule by construction.

## S5 — Satellite assembly clocking
Forward-capable clocking exists in a window around OFF ~ 9-10 deg (mod 30);
the exact witness-mark spec should be issued together with the S4 redesign
(the fix will move it). The clocking failure mode (satellite meshed one
sun-tooth off = 30 deg = silent month-end miss) stands confirmed; witness
marks on all three satellites are required in the next patch regardless.

## S6 — Housekeeping
strike_profile's docstring claims "+theta corner relief"; the code implements
a symmetric crown. Docstring stale; code is the better design. Correct the
comment in the next patch.

## Stage 1 impact
S1/S2 clear the engine's daily drive for print. S3 is bench-first. S4 means
the satellite laminas (sun tower strike bands + leap tooth) as generated are
forward-only: printing Stage 1 now yields a demonstrator whose skips work
forward and cannot be reverse-cranked through month-ends. Options: hold the
sun-tower/leap parts for the S4 session, or print the full Stage 1 as a
forward-alpha to bank assembly/bearing/detent learning while S4 is designed.
Ron's call.
