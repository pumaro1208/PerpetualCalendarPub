# Making a Chewy-style name keychain with Claude Code

The easiest path: put the included `make_keychain.py` in a folder, open Claude Code there, and paste the prompt below. The script already encodes everything reverse-engineered from the original Federico model, so Claude Code only needs to set up dependencies and run it.

## Prompt to paste into Claude Code

```
I have a script make_keychain.py in this folder that generates a 3D-printable
name keychain (bubble-letter style, Chewy font). Please:

1. Install its Python dependencies:
   pip install numpy shapely trimesh matplotlib manifold3d mapbox_earcut rtree fonttools brotli
2. Get the Chewy font as chewy.ttf in this folder. If Google Fonts or GitHub
   is unreachable, use npm:
     npm install @fontsource/chewy
     python3 -c "from fontTools.ttLib import TTFont; f=TTFont('node_modules/@fontsource/chewy/files/chewy-latin-400-normal.woff2'); f.flavor=None; f.save('chewy.ttf')"
3. Run: python3 make_keychain.py <NAME>
4. Confirm the output says "watertight, 1 body(ies)" and give me the
   <NAME>.stl and <NAME>.3mf files.

Make one for the name: Taashvi
```

## What the script does (the design spec, if you ever want it rebuilt from scratch)

The style is a clone of the MakerWorld "Portachiavi Nome Parametrico Personalizzabile" (Stampa 3D AV Studio), reverse-engineered from an exported 3MF:

- **Font**: Chewy (Google Fonts), rendered at 0.305 mm per unit of a size-100 TextPath (≈17 mm cap height).
- **Letter layout**: each glyph advances 0.80× its normal advance width, so adjacent letters overlap. Any pair that still overlaps by less than 2.5 mm² is nudged closer in 0.1 mm steps until it does — this is what fuses the word into one printable piece.
- **Heights**: letters alternate — 1st, 3rd, 5th… extrude to 6.5 mm; 2nd, 4th… to 4.5 mm. All start at z = 0.
- **Keyring loop**: annulus, 10.14 mm outer diameter, 5 mm hole, 4.5 mm thick, vertically centered 1.5 mm below the word's midline, slid rightward until it overlaps the first letter by ≥ 4 mm² while keeping the hole clear.
- **Dots on i/j**: lowered until they overlap their stem by ≥ 1.5 mm² so the model is a single body (the original leaves them floating as separate pieces).
- **Output**: boolean union via manifold3d, centered on a 256 mm plate, exported as STL + 3MF. Sanity checks: mesh watertight, exactly 1 body.

## Printing notes

- No supports needed; prints flat side down.
- Any color; the original used a single filament. The 2 mm height difference between alternating letters lets you do a filament swap at z = 4.5 mm for a two-tone effect.
