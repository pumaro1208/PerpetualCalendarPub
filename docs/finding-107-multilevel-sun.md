# Finding #107 — the sun/finger conflict resolved by restoring the multi-level sun

Ron caught (on the printed engine): the sun does not drive the receiver, and the
strike fingers cannot rotate past the sun. Root cause traced to finding #79, which
had replaced the original stepped sun (03_sun_tower) with a uniform full column.

## What the full column broke
- **Finger collision.** The strike fingers reach r18.28 about their pivot; pointing
  inward they come to 5.47mm from the sun center. The full column's r11.25 teeth sit
  right there, so a full 360° satellite rotation drives the fingers into the sun.
- **Mesh jam.** The full column's tip grew to r11.25, bottoming 0.90mm into the
  mesh-lamina root — tip-root interference (the bind Ron felt).

## The fix (authoritative heights from simulator b50 section view)
Vertical stack (assembly z): board 5-9; sun 9.5-19.5; month sat 9.5-12.5,
feb 13-16, leap 16.5-19.5; drive arms 24h@5-9 / 23h@9.5-12.5 / 22h@13-16 / 21h@16.5-19.5.

- **Multi-level sun** (part_42_sun_multilevel): FULL 7t gear bands (root7.4, tip9.55)
  at each mesh altitude (9.5-11, 13-14.5, 16.5-18); SLIM core r5.0 at each strike
  altitude (11-13, 14.5-16.5, 18-19.5). Square keyed bore unchanged. 10mm tall — the
  existing post height is fine (my earlier 25mm was from over-spacing the satellites).
- **Compact receiver** (receiver_compact): mesh + strike laminae ADJACENT, 3mm tall
  (was 8mm). Strike teeth root on the mesh disc (print supported). Matches the sim.
- **Shortened board post** (part_02h_board_v16): post to z12.5 — with the compact
  receiver and feb orbiting 4.81mm away at z13, the post must stop BELOW the feb band.

## Verified
- All three satellites' strike fingers clear the sun over a full 360°: +0.47mm each.
- Mesh drives at the full band: 1.60mm engagement, no jam.
- Stacked satellites z-separated (0.5mm gaps month/feb, feb/leap).
- Shortened post clears the feb band (top 12.5 < 13.0).
- Sun, receivers, board all watertight.

## Supersedes / reverts
Reverts #79 (full column) and #105 (mesh-valley patch). Subsumes #104 (fingers now
print supported on the mesh disc) and #106 (bore rides the post through both laminae;
the post gets SHORTER not taller). Sun tip 9.55 restores the original clean mesh.

## Remaining before the engine turns
- Drive strike arms must reach the four strike-lamina bands (24h@board, 23h@11-12.5,
  22h@14.5-16, 21h@18-19.5); the current arch-A' sliders sit at one band (5.2-8).
- Leap shuttle (part 35) to be brought to the compact height.
- Re-gate (watertight + interference) and re-plate the paused engine campaign.
