# #148 — THE STRIKE CLOCKING IS THREE RULES, NOT ONE

**The most serious fault of the v17 campaign, and every gate passed it.**

Ron, looking at an assembled board: *"it appears the location of 1 on the board is not at
the top at the start of the month — it looks like 30 is."*

## What was wrong

`E1_BASE` sets the angular bearing of a receiver's finger bars at φ = 0 — where the
strike bar stands when the board is at its datum. Since **#110** it had been a single
round **6.0** shared by all three satellites, and it was never checked against the
calendar engine.

It cannot be one number. The three satellites strike on **different dates**: month on 30,
feb on 29, leap on 28. A bar that stands on the strike line on date 30 cannot also stand
there on date 29.

Measured error against the 1.12 mm drive window:

| satellite | strike date | error | at the strike face | % of window |
|---|---|---|---|---|
| month | 30 | 0.77° | 0.24 mm | 22 % |
| **feb** | 29 | **10.84°** | **3.43 mm** | **306 %** |
| **leap** | 28 | **7.55°** | **2.39 mm** | **213 %** |

Month was close enough to work — which is exactly why it survived: the month wheel was
bench-tested and it ran. Feb and leap would have **missed entirely**. February would
never have been shortened and the leap tooth would never have fired, on a mechanism whose
entire purpose is those two events.

## The corrected values

    E1_BASE = {"month": 6.774, "feb": 25.161, "leap": 13.548}

All three now land **0.000°** from the strike line on their own date.

## Derived two independent ways

They agree to three decimals, which is the only reason to trust either.

1. **Empirical.** Run the simulator's calendar engine and record the bearing each strike
   actually demands.
2. **Geometric.** One month is 31 board steps = 570° = **exactly 19 satellite teeth**.
   So satellite phase mod 30° resets every month and depends only on the date. Check:
   `psi = (19/12)·(d−1)·PITCH + E1_BASE` lands on 0 mod 30 at each strike date.

## Do not confuse this with ALPHA

Each satellite carries **two** independent clockings and neither is shared:

- **`ALPHA`** (18.07 / 6.46 / 24.85) rotates the **mesh lamina** so a fully seated mesh
  phase coincides with the strike station.
- **`E1_BASE`** (6.774 / 25.161 / 13.548) rotates the **finger bars** so a bar is on the
  strike line on that satellite's own strike date.

## Why no gate caught it

Every dimensional gate passed. The stack was internally consistent, the parts fitted, the
mesh seated. The fault was not a contradiction between numbers — it was geometry that
described **the wrong machine**, and no gate that only compares parts to each other can
see that. Seeing it requires knowing what the mechanism is supposed to *do* on date 29.

It was also written down wrong in prose: an assembly card claimed *"the clocking is one
rule, not three — all three reference bars point the same way."* That should have been
suspicious on its face. Three satellites that fire on three different dates cannot share
a bearing, and the fact that all three came out identical was the tell.

**Gate added** (`assembly_gate_v17.py` § 9): for each satellite, roll the engine to its
strike date and assert the bar lands on the strike line, reporting the miss in **mm of
the 1.12 mm drive window** rather than in degrees — degrees hide how big 10° is.

## Consequence

Every receiver printed before this is scrap. The correction folds into the consolidated
6.5-pitch reprint together with **#147**.
