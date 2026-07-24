# EP1351104B1 — Full-Text Review Against the Demonstrator (2026-07-08)

Source: granted patent, Oechslin/Ulysse Nardin, filed 2002-04-02, expired.
PDF (for Ron's Fig. 2/3 visual check):
https://patentimages.storage.googleapis.com/26/68/4c/864f0bb55c982e/EP1351104B1.pdf
Embodiment 1 (Figs. 2-3) is our machine. Embodiment 2 (Figs. 4-9) is a
different two-program-wheel date-disc design — instructive, see section 5.

## 1. Element map — Fig. 2/3 vs our v1.3/v1.5 engine

| Patent | Ours | Verdict |
|---|---|---|
| fixed wheel 203, seven teeth, both levels | 7t sun tower | faithful |
| board 204, 31 teeth 205 | program wheel, 31t | faithful |
| 24h wheel 13: 23 short teeth + one long tooth 208 (only 208 reaches the board; daily step at midnight) | drive wheel, one board-level tooth | faithful |
| strike teeth 241/242/243: elevated, same length as 208, superposed over the three wheel-13 teeth PRECEDING 208 -> act at ~21h/22h/23h before 208 at midnight | four rim teeth at 45/30/15/0 deg, hour ladder | faithful (the ladder is the patent's) |
| month wheel 210: 12t on stud 214, 7 short + 5 long teeth 217 | month satellite, LONG_M five teeth | faithful |
| feb wheel 211: 12t on stud 218 integral with 214, smaller, circumferentially offset | stepped-stud feb satellite | faithful |
| leap element 212: SLIDING PLATE ON THE BOARD, tooth 221, 3 guide studs, springless | v1.3 moved it onto the satellite chain | DIVERGED (see 4) |
| command 213: satellites 228(12t)+229(1 tooth/2 recesses/blocking arc)+230(8t, locked)+231(8t cam, 3 long teeth at 90 deg) driving the plate edge | v1.5 cam-programmer + follower + slider | diverged in parts, same function |

Kinematics check: the patent states the sun-meshing wheels make 7/12 turn per
board revolution (carrier frame) = our 19/12 fixed-frame — identical epicyclic.
Annual repeat (seven laps/year) confirmed on both sides.

## 2. Two corrections to my previous readings (both matter)

(a) The Geneva-lock (229's tooth-between-recesses + blocking arc, 230 locked)
is the LEAP COMMAND ONLY: it steps the cam wheel 231 a quarter turn seven
times a year so 231's three long teeth hold the sliding plate active three
Februaries in four. It is NOT a general second gating key for the skips.
(b) The "teeth short enough not to emerge" clause applies to the four COMMAND
satellites 228-231 — the month and feb wheels DO present their long teeth
directly at the periphery from continuously-spinning satellites, exactly like
ours. The patent contains NO indexing lock between satellite spin and month
tooth presentation. My session-1 hypothesis is withdrawn.

## 3. What the patent DOES prescribe that we quietly dropped — the S7 lead

The retractable teeth are constrained two ways we did not honor:
  - active position SUPERPOSED ON a board tooth 205 (claims 5, 7; description:
    emergence is over a tooth of the board, and the elements retract inward
    because their wheel diameter is smaller than the board's);
  - SAME PROFILE as the board teeth (stated as preferred).
Consequence: every skip engagement in the patent is a geometric COPY of the
daily board mesh — conjugate involute tooth caught by a copy of the daily
long tooth, at a board-lattice station. Our lamina teeth are crowned wedges
with a ~±9.5 deg angular footprint, roughly double an involute board tooth's,
and are NOT registered to the board lattice. That is the sharpest concrete
divergence bearing on S7's eve-of-skip false strikes: a patent-literal
receiver is ~half as wide and sits exactly where the proven daily mesh puts
teeth. Whether that clears the 6.8 deg/evening pointing crawl is precisely
what the sequence harness can answer.

## 4. What the patent does NOT answer

  - Evening selectivity is never discussed. No mechanism beyond emergence
    geometry guards the eve-of-skip; either the tooth form suffices at these
    proportions (testable, section 6) or the issue is latent in the patent too.
  - Bidirectionality is never claimed for embodiment 1. The board is held by
    a conventional jumper; skip strikes are single-tooth pushes -> by our R1
    rule they are detent-completed and forward-only in the patent as well.
    Full bidirectionality is OUR design law, not the patent's promise. Our
    R1 solution (pin-slot class) is still on us.
  - The leap plate is board-mounted in the patent and works because its cam
    command (231) holds it through the strike; our v1.2 board-mounted attempt
    failed under OUR cam-support kinematics — v1.3's satellite-borne slider
    plus the v1.5 live-read follower is a legitimate re-solution of the same
    requirement (springless, positive, no stored state) and reads BETTER
    against time-reversal than the patent's own arrangement.

## 5. Embodiment 2 (Figs. 4-9) — worth stealing from later
A one-year program wheel whose OUTPUT toothing has teeth/recesses per month
and arc shoulders that BLOCK the driven pinion between steps — positive
indexing with no jumper spring at all (per CH 688671). Its leap element is a
sliding single tooth positioned by two 8t satellites acting on opposite edges
— springless, and its false presentations between leap years are harmless
because they occur when the output pinion is elsewhere. Architectural lesson:
selectivity by BLOCKED OUTPUT rather than gated input. If the patent-literal
receiver test fails, this is the pattern to adapt (it is also the strongest
prior art for our board-mask idea: gate where the output is read).

## 6. Session-2 experiment list (in order)
E1. Patent-literal receiver: replace the crowned lamina teeth with involute
    board-tooth profiles, superposition-registered; rerun sequence sweep.
    Settles whether S7 was our tooth form or the architecture.
E2. If E1 clears selectivity forward: marry with the twin-flank/pin-slot
    receiver for R1 (reverse), re-judge.
E3. If E1 fails: blocked-output gating per embodiment 2 / board-mask.
Leap train: keep v1.5 live-read follower either way; re-spec the slider to
carry whatever receiver E1/E2 selects.

## 7. ADDENDUM — E1 push measurement (the party-trick question, answered)
Single-pair transit of the patent-literal receiver (involute BOARD-TOOTH
profile, superposition-registered to the board lattice) against the strike
tooth, detent-coupled, both directions:

  station -5.83 (tooth below the mesh):
    FORWARD  push 1.129 pitch, settled +1.000 exactly
    REVERSE  push 1.328 pitch, settled -1.000 exactly
  station +5.78: forward-dead (0.331P), reverse-capable -> the -5.83 station
    is the design point; assembly clocking must register the emerged tooth
    there (witness-mark spec follows directly).

CONCLUSION: the patent-literal fork (E1) supports full bidirectionality.
A single involute tooth pair at this geometry carries 1.1-1.3 pitch of
conjugate contact — tooth-completed both ways, no detent completion, no
one-way ratchet. My S4 rule ("single-tooth receivers max ~0.75P") was an
artifact of OUR crowned-wedge lamina and is hereby narrowed: it applies to
non-conjugate receivers. EP1351104 never CLAIMS backward setting, but the
claim-5 prescription (same profile as the board teeth + superposition on a
board tooth) ENCODES it: every skip engagement becomes a copy of the daily
board mesh, which is bidirectional by the same conjugate action our S2
sweep certified. Excursion margin also improves: 1.13P peak vs the 1.5P
crest = 0.37P margin (4x the daily drive's own S3 margin).

Remaining gate before E1 is adopted: eve-of-skip SELECTIVITY in the
sequence harness (the involute receiver's ~half-width footprint vs the
wedge should clear the 6.8 deg/evening crawl — to be verified, Session 2
first action). If green: v1.6 = involute receivers on all three satellites
+ leap slider re-headed with the same profile (0.507P armed margin
dissolves to ~1.1P) + witness marks. The pin-slot (E2) remains the fallback
if selectivity fails.
