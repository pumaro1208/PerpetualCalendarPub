# Engine clearance sweep — board 02f vs the rotating calendar stack

**Question (Ron):** will the gears rotate on top of the board, or do the pegs block
them — and is the sun tower configured so the whole perpetual stack turns without
grinding?

**Answer:** the committed board 02e has one real grind (the tall day‑1 peg and two
station dots foul the month satellite's mesh lamina even with the finding‑63
spacer). Board **02f**, with the 31 perimeter day‑tick pegs and the 3 station
witness dots removed, is **clear** — nothing on the board face enters any
satellite's swept disc. The sun tower checks out: it seats at z9.5, stands 10 mm,
and meshes the month lamina at the right radius and height.

## How the sweep works (`parts/engine_sweep.py`)

The satellites are fixed to the board — the board carries them around the fixed
sun, and each satellite spins on its own board‑fixed post. So relative to the
board a satellite's pivot never moves; it only spins. Its danger volume is a
**disc** of radius = lamina tip about that fixed pivot, over the lamina's z‑band —
not a full annulus. A board obstacle grinds only if it falls inside that disc and
overlaps the lamina's z‑band.

Board obstacles are read from the actual regenerated STL (every vertex above the
tooth rim, minus the intended satellite pivot post, which is the month satellite's
own axle). Satellite tip radii and z‑extents are measured from the actual satellite
STL — no hand numbers are trusted. Bands fill the full lamina height between prism
boundary planes, so a feature poking into the *middle* of a lamina is caught (an
earlier version sampled only where the mesh prism carried vertices and missed the
tall peg — fixed).

**Frame self‑check (guards a vacuous pass).** Before any "clear" is reported the
sweep asserts that the assembled sun and the month mesh lamina actually overlap in
radius and z — i.e. they mesh. If the stack heights were wrong they wouldn't, and
every downstream result would be meaningless. Self‑check: sun r_out 11.25,
z[9.5,19.5] vs month mesh reaching in to r7.95 at z10.4 → **mesh confirmed**.

## Assembly Z‑truth (from the generators' own seating gates)

    board top face       z 9.0        (acceptance_39_40 A20b: "board top 9.0")
    sun tower            z 9.5 .. 19.5 (part_42 / A31: seats 9.5, h10, spans LA/LB/LC)
    month mesh lamina    z 10.4 .. 12.4 (board top 9.0 + finding‑63 spacer 1.4; A23)
    feb  mesh lamina     z ~13 .. 15   (LB band, finding 79)
    leap mesh lamina     z ~16.5 ..    (LC band, finding 79)

## Findings

The month satellite is the only rotating element near the board face (its lamina
underside sits at z10.4, 1.4 mm over the board). Against board 02e:

- The **30 short day‑ticks** (h1.0, top z10.0) actually clear the lamina underside
  (z10.4) by 0.4 mm — the finding‑63 spacer is doing its job for these.
- The **tall day‑1 peg** (pos‑1, h2.2, top z11.2) pokes **+0.8 mm** up into the
  mesh lamina. It sits 15.0 mm from the month pivot, inside the 15.8 mm lamina disc.
- **Station dots M and F** (h1.6, top z10.6) poke **+0.2 mm** into the lamina;
  both lie inside the month disc. (Dot L is just outside it, at 16.2 mm.)

So the committed board would let the month satellite skim the day‑1 peg and two
dots on every pass — a real, if shallow, drag. Removing all pegs and dots (board
02f) leaves **zero** raised obstacles on the face except the pivot post itself, and
the sweep reports **CLEAR**. feb and leap ride higher (z ≥ 13), above every
obstacle top (z11.2), so they were never the issue and remain clear.

## Sun tower

Correctly configured. The self‑check confirms the sun's outer teeth (r11.25) reach
into the month mesh lamina at the shared altitude, i.e. the satellites have
something to roll against at their own height — the finding‑79 fix (full keyed
column spanning LA/LB/LC) holds in the assembled frame.

## Scope / what this does not cover

The pivot post is excluded as intended infrastructure (the month satellite's axle).
The vertical stacking of the three satellites (the LA/LB/LC altitudes and their
carrier) is governed by the carrier chain and is authoritative in the simulator;
this sweep does not re‑derive it. If you want, I can extend the check to the
inter‑satellite / post stacking against the simulator as a separate pass.

## Verification performed

Frame self‑check (sun↔month mesh) passed; before/after sweep run on regenerated
02e and 02f; both boards watertight (0 odd‑parity open edges); 02f is 02e minus the
peg loop and the dot loop with the involute rim, 10.9 bore, and satellite post +
D‑key unchanged.

**Recommendation:** print board 02f in place of 02e.
