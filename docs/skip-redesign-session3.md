# Skip-Transfer Redesign — Session 3 VERDICT (2026-07-08)

## Architecture A' — cam-gated SLIDER STRIKERS + rigid E1 receivers: PASSES

The inversion that made it buildable: gate the STRIKERS, not the receivers.
The three skip strike teeth on the 24h wheel become radial sliders (three
sliders total, all on one part), extended only when their peg reads a lobe
on a board-riding cam ring. Strike load is tangential, slider travel is
radial — orthogonal, so drive force cannot back-drive the gate (the leap
slider's own proof). Cam contact is a smooth track — no false-step torque
(the v1.5 follower's own proof). Receivers are rigid involute laminae in
the E1 patent-claim-5 form. Two keys: the board-riding cam answers "is
tonight the skip evening?" at 11.6 deg/evening; the satellite station set
answers "is this a skip month?" at 150 deg/month. Both passive, springless,
read at moment of use.

## Sequence-harness judgment, month train (the decisive case), base 6:
  G1  all 5 skip evenings: forward push >= 1.125 P, reverse >= 1.327 P,
      settled EXACTLY +/-1.000 pitch — BIDIRECTIONAL skips in the
      calendar-true sequence. The party trick, end to end.
  G2  non-skip months' extended evenings: 0.000 P — perfectly silent.
      The 5-consecutive-station set lands the 5 skip months exactly
      (stations walk +5/month, 5 and 12 coprime; verified in-scan).
  G3  adjacent evenings, striker retracted at the leap-proven 1.6 mm
      stroke: minimum clearance 1.23 mm (gate 0.30). At 2.0 mm: 1.60 mm.
      (First run reported -0.13 mm from a sign error in the retraction
      model — the harness extended instead of retracting; fixed, re-run.)
  G4  registration tolerance: passes at least +/-3 deg of satellite
      clocking error — assembly-friendly; witness marks suffice.

## Requirement scorecard (R1-R4 from the strike/phantom/sequence sweeps)
  R1 bidirectional tooth-completed push  ....... PASS (1.13/1.33 P)
  R2 evening selectivity ....................... PASS (cam gate, G2+G3)
  R3 healthy margins ........................... PASS (0.37P crest margin;
                                                  1.23 mm retract clear)
  R4 all other visited passes gated ............ PASS (zero contact)

## Remaining before v1.6 geometry
  1. Feb and leap trains through the same harness (single-station cases,
     geometry class identical; leap keeps the v1.5 follower for the year
     key, its striker gains the 21h slider like the others).
  2. Natural-evening re-clocking note: skips land at pos 27/28/29 with the
     serving satellite at -5.83 deg — display mapping shifts one pitch;
     witness-mark spec at base-6 registration.
  3. v1.6 patch: drive wheel (3 slider strikers + pegs + detent bumps),
     board cam ring (3 lobes/tracks), satellite laminae (E1 involute
     receivers), leap slider re-headed, witness marks. Full pipeline:
     regenerate -> watertight -> acceptance sims -> sequence harness ->
     package. Awaiting Ron's approval of A' and his Fig. 3 read on the
     patent's stud-guidance pattern for the slider details.
