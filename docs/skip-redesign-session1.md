# Skip-Transfer Redesign — Session 1 Findings (2026-07-08)

## Candidate tested: pin-and-slot (drive strike teeth -> pins; lamina teeth
## -> twin-rail slots), judged in the calendar-true sequence harness.

R1 SOLVED by the candidate: strike pushes 1.2-1.6 pitch, tooth-completed,
with reverse engagement available by the same slot geometry — the Geneva
pattern delivers bidirectionality exactly as predicted.

R2 UNSOLVABLE by ANY satellite-borne receiver — the decisive measurement:
the satellite's presentation POINTING phase advances only 6.8 deg per
evening (18.39 deg spin minus 11.61 deg orbit). Any physical receiving
feature at r~18 subtends 10-15 deg, so it inevitably presents across 2-4
consecutive evenings. The sequence autopsy confirms: eve-of-skip false
engagements (1.6-2.3 pitch — worse than the tooth, since a rail drives
harder than a crowned tooth corner) at EVERY clocking, plus one strike
evening served a day early. This also retro-explains S7: the original
crowned tooth was a partial-selectivity compromise that failed both ways.

## The architectural conclusion
Skip gating needs a SECOND key whose phase moves a full station per evening.
The machine already owns one: the BOARD advances 11.61 deg per evening.

PROPOSAL for Session 2 — board-position masking:
A thin MASK lamina riding the board at each strike band (or one ring serving
all three), carrying a single APERTURE at the pos-30 (pos-29/28 for feb/
leap) angular station. The drive pin physically reaches the satellite slot
only THROUGH the aperture: on any other evening the mask blanks the pin at
full board-pitch discrimination (11.6 deg/evening — crisp), while the
satellite slot provides WHICH-month gating exactly as the presence concept
intends. Two keys, two questions: the mask answers "is tonight a skip
night?", the satellite answers "is this a skip month?". Both must say yes.
Design notes: masks ride the board (rotation parity preserved — nested,
no inversion); apertures are passive (no springs, no stored state — state
read at moment of use); pin length/z unchanged; adds 1-3 thin laminae to
the board stack and ~1.5 mm of z per band to thread the pin through.
Leap keeps the v1.5 slider (retract spec verified: 1.6 mm stroke, 0.65 mm
clearance) — the slider now retracts the SLOT, and the armed-margin problem
dissolves because the pin-slot push is 1.2P+, not 0.507P.

## Session 2 agenda
1. Parametrize mask ring + aperture + pin z-threading; extend the harness's
   overlap model with the mask (one more polar profile per band).
2. Judge in the sequence harness: all four R's, forward AND reverse, all
   three satellites, plus mask-edge graze checks (the new phantom class).
3. If green: v1.6 patch — regenerate drive wheel (pins), satellites (slots),
   board (+mask laminae), sun tower (band heights); full pipeline;
   witness-mark spec for satellite clocking.
Stage 1 split unchanged: skip train on hold; the rest of the engine prints.
