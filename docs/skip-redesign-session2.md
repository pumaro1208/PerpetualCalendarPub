# Skip-Transfer Redesign — Session 2 (2026-07-08)

## E1 verdict: bidirectional YES, selective NO — adopted as the RECEIVER
## FORM, rejected as the complete architecture.

The patent-literal involute receiver (board-tooth profile, superposition-
registered) measured 1.13P forward / 1.33P reverse, settling exactly +-1.000
pitch — R1 solved, party-trick class, 0.37P crest margin. But the calendar-
true selectivity gate fails at ALL 12 station assignments: the day-after
evening engages at 0.77 pitch (over the 0.5 crest -> false strike). The
6.8 deg/evening pointing crawl defeats every receiver form — wedge, slot,
involute — confirming Session 1's structural conclusion with the best
possible receiver.

## Mask analysis: the naive shield is geometrically impossible
Worked through in this session; recording so it stays dead:
 - Any board-riding shield inside the striker's swept annulus (r 40.7-44.9)
   is TOUCHED BY THE STRIKER on masked evenings; a striker pressing any
   board-borne surface IS a false step. Masking the striker's path is
   self-defeating.
 - A shield inside r 40.7 (striker-safe) instead COLLIDES with the emerged
   rigid receiver (tip 41.86) on masked evenings. Rigid receivers cannot be
   masked without crashing into the mask.
Conclusion: the second key cannot be a passive wall anywhere in the
engagement annulus. It must act on a COMPLIANT receiver.

## The converged architecture — generalize the leap slider
The machine already contains the answer, proven twice over: the patent's
sliding plate 212 (springless, cam-positioned, board-guided) and our own
v1.5 live-read follower/slider for the leap. Proposal:

  ALL THREE skip receivers become SLIDING involute teeth (E1 profile) on
  their satellites, positioned by board-referenced cams — radially OUT
  (engageable) only when both keys agree:
    key 1 (which month): satellite spin aligns the slider's cam follower
      with the cam's admission window — the presence concept, now acting on
      a 1.6 mm radial stroke instead of raw tooth exposure;
    key 2 (which evening): the cam profile is indexed to the BOARD lattice
      (11.6 deg/evening discrimination — the crisp key), so the slider pops
      out only at the strike park and is positively retracted the evening
      before and after.
  Retracted clearance is a solved spec (1.6 mm stroke -> 0.65 mm, phantom
  sweep P3). Engaged, the slider presents the E1 involute tooth -> 1.1-1.3P
  bidirectional push. Springless, no stored state (cam read at moment of
  use), rotation-parity preserved. Cost: two more sliders + cam surfaces —
  the leap train's pattern replicated for month and feb.

## Decision for Ron
 (A) Three-slider architecture above (lead candidate: every element already
     exists somewhere in the machine; z-stack grows by the cam surfaces).
 (B) Embodiment-2-style blocked output (larger architectural change; strongest
     prior art for positive indexing; would touch the daily drive too).
Ron's Fig. 2/3 + Fig. 4-9 read now directly informs A vs B — the sliding
plate's stud guidance (Fig. 3) is the template for A's sliders.
Session 3: parametrize the chosen architecture; judge in the sequence
harness (all three satellites, both directions, mask-edge/cam-edge grazes);
if green -> v1.6 patch.

Stage 1 unchanged: skip train held; the rest of the engine prints.
