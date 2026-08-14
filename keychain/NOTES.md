# Name-keychain tooling — so we never lose this again

`make_keychain.py` regenerates the MakerWorld "Parametric Model Maker" / Federico
bubble-letter name-keychain style for **any name**, as one watertight body.

## Run it
```
pip install numpy shapely trimesh matplotlib manifold3d mapbox_earcut rtree fonttools brotli lxml
# (already installed in ../print-console/.venv)
python3 make_keychain.py <NAME>   # writes <NAME>.stl and <NAME>.3mf ; must say "watertight, 1 body"
```

## Getting the Chewy font (chewy.ttf must be next to the script)
GitHub raw URLs returned HTML, not the font. What worked was the Google Fonts CSS API:
```
url=$(curl -s -A "Mozilla/5.0" "https://fonts.googleapis.com/css2?family=Chewy" | grep -oE 'https://[^ )]+\.ttf' | head -1)
curl -s -o chewy.ttf "$url"      # Font Diner "Chewy Regular"
```
Fallback: `npm install @fontsource/chewy` then convert the woff2 with fontTools.

## Design spec (encoded in the script)
Chewy at 0.305 mm/unit of a size-100 TextPath (~17 mm cap height); glyphs advance
0.80x and are nudged closer until each adjacent pair overlaps >= 2.5 mm^2 (fuses the
word); letters alternate 6.5 / 4.5 mm tall (the 2 mm step allows a filament swap at
z = 4.5 for two-tone); keyring annulus 10.14 OD / 5 hole / 4.5 thick, 1.5 mm below the
word midline, slid right until it overlaps the first letter >= 4 mm^2; i/j dots lowered
to fuse to their stems >= 1.5 mm^2; manifold3d union -> 1 watertight body.

## Validation
This reconstructed script reproduces Ron's tested `Taashvi_one_piece.stl` to within
0.7 mm (73.2 vs 73.9 mm long), same 23.8 x 6.5 mm, both 1 watertight body.

## Printing (via ../print-console)
P1S, 0.20 mm Standard, single filament, no supports, prints flat side down. For a
two-tone effect, swap filament at z = 4.5 mm. Multi-colour? Re-read the live AMS first
(never trust the stated slot layout).
