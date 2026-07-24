# Print console — Bambu Lab P1S (Oechslin perpetual calendar build)

LAN-mode print console: MQTT status + FTPS upload via `bambulabs_api`,
headless re-slicing via Bambu Studio's CLI.

## Setup

Fill in `.env` with the printer's LAN Mode values (IP, access code, serial).
The venv is already built (`.venv/`, Python 3.12).

## Commands

```
./pc status                      # state, temps, AMS slots, job progress
./pc upload plate.gcode.3mf      # send to printer storage over FTPS
./pc start plate.gcode.3mf --version-tag "plate-01 · v16b"
./pc watch                       # follow active job, layer milestones
./pc reslice project.3mf --xy-compensation -0.05
```

## Standing rules

1. **No print ever starts without an explicit "yes" from Ron in that
   conversation.** `start` prompts interactively; `--yes` exists only for
   after that confirmation has been given.
2. Every job is appended to `print-log.md` (timestamp · filename ·
   part version · outcome). `watch` records finished/failed outcomes.
3. The access code lives only in `.env` (git-ignored).
4. If the printer is unreachable, commands fail plainly — no silent retries.

## Re-slicing notes

- Only saved `.3mf` **project files with embedded presets** are accepted —
  never raw STLs with external config JSONs (the CLI applies external
  presets unreliably).
- `--xy-compensation N` patches `xy_contour_compensation` *inside* a working
  copy of the project's embedded settings, then slices that — the tweak
  always takes effect.
- Slicer: `/Applications/BambuStudio.app/Contents/MacOS/BambuStudio`
  (override with `BAMBU_STUDIO_BIN`), `--mstpp 300` timeout, JSON progress
  via `--pipe`. Output lands in `sliced/`.
