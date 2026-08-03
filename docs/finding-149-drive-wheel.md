# #149 — THE DRIVE WHEEL (24h, with arms reaching 21h / 22h / 23h)

Ron, at the bench: *"I need the correct 24 hr wheel printed that can hit the 21,22,23 hours."*

This was the part that had been blocking everything — there was nothing to crank. The
old `30_drive_v16` is 15 mm tall overall and was cut for the 3.5 mm band spacing; the
v17 stack at 6.5 pitch needs the 21h arm up at 24.70–25.50, which that wheel cannot
reach.

## Geometry — taken from the simulator, not invented

Drive axis 73.50 from the board axis along the strike line; body r29.20; arm tip orbit
r32.76. The board tooth tip and every satellite strike tip stand at 41.86, so each arm
engages by 41.86 − 40.74 = **1.12 mm** — the same drive window every clocking number in
this project is quoted against. The body clears the board teeth by 2.44 and the
satellites by 3.36.

Angles: the wheel turns once per day, so an hour is 15°. Arms sit at 180 − off with
off = 0/15/30/45 for 24h/23h/22h/21h. All four were *checked* to land on world 180° at
their own hour, not assumed to.

Altitudes, each clearing the mesh lamina 0.70 mm below it — an arm coplanar with a
lamina fouls the gear instead of striking it:

| arm | z | target |
|---|---|---|
| 24h | 5.00 – 9.00 | board teeth |
| 23h | 11.70 – 12.50 | month strike tip (mesh ends 11.00) |
| 22h | 18.20 – 19.00 | feb strike tip (mesh ends 17.50) |
| 21h | 24.70 – 25.50 | leap strike tip (mesh ends 24.00) |

## Why four stacked pieces and not one wheel

A single body would be an r29.2 cylinder 20.5 mm tall with four small tabs whose
undersides are all unsupported cantilevers. Split at each arm and every piece prints
**arm down on the bed**: no overhang anywhere, no supports, a quarter of the material.
Same idiom as the sun tower, and it is why the tower prints clean. Each piece carries
its arm pre-rotated, so a plain square key clocks all four — exactly how the receivers
carry their ALPHA.

## The sleeve is not the sun tower's K4

K4 is 4.42 across and the fixture's drive post is r4.17 = Ø8.34 — bigger than the whole
key. The first cut had the bore eat the key and leave four corner slivers; the weld gate
caught it as *"4 disconnected solids"*. The sleeve wraps the post instead: round r4.17
bore, square 11.50 across outside, 1.58 mm wall. The post must stay round, because this
wheel is the crank and has to turn.

## Emitted / gated

`158_drive_24h` · `159_drive_23h` · `160_drive_22h` · `161_drive_21h` ·
`162_drive_sleeve` — all single watertight solids, 65.7 cm³ solid, ≈31 g at 3 walls /
15 % infill. Plate spec `plate-48-drive-wheel.json`: five objects, single colour, flat,
no supports, xy-comp −0.06, quiet.

Gate section 10 (DRIVE WHEEL) in `assembly_gate_v17.py`: every arm reaches r32.76 and
engages at 1.12 of the 1.12 window, every arm sits exactly on its target strike tip,
every arm clears its mesh lamina by 0.70, every arm points at world 180.0 at its hour,
body clearances 2.44 / 3.36, sleeve wall 1.58. All pass.

**Assembly order on the drive post:** sleeve first, then 24h, 23h, 22h, 21h bottom to
top. All four square bores go on the sleeve one way only.

## Also fixed here

The grip gate's failure message printed `MIN_GRIP_DIA/2` — it tested against 0.80
diameters but told you it needed 0.40, so the report contradicted itself. A gate that
misreports its own threshold is worse than no gate.
