# Working in this repo — standing rules for Claude Code

This repo drives a **Bambu Lab P1S** (LAN mode) via `print-console/` and holds the
Oechslin perpetual-calendar build plus side prints (name keychains, etc.). Read these
before doing anything with the printer.

## Pre-start checklist — do ALL of this before starting ANY print
1. **Camera-verify the bed is clear.** `./pc snap` (or the console `snap` command), look
   at the image, and confirm the plate is empty — **even if the user says it's clear.**
   The P1S camera looks down-and-forward, so the **front-center of the plate is often out
   of frame**; say so honestly rather than implying the whole bed is confirmed. Never
   start onto a possible leftover part.
2. **Live-verify the AMS.** Read the live AMS (paho `pushall`) and confirm the tray you're
   mapping to actually holds the intended filament — check type / sub-brand / colour per
   index. **Never trust a spec's or a verbal "slot N = colour" statement** — they have
   been reversed from the real trays repeatedly. Do this at pre-start, not after.
3. **Get Ron's explicit go.** Do not start a print without an explicit "yes"/"go"/"print
   it" from Ron in the conversation. `--yes` on `pc start` is only for after that.

## While/after printing
- **Log every job** to `print-console/print-log.md` (filename · version tag · outcome),
  including bench findings and any reflows or fixes.
- Report outcomes faithfully — if the camera view is inconclusive, say so; don't claim a
  clean part you can't actually see.

## Filament / AMS notes
- `--ams-slot` / `--ams-mapping` are **0-based** (index 0 = physical slot 1).
- Multi-colour: build `--ams-mapping [T0_tray, T1_tray, …]` from the **actual live tray
  colours** (T0 = spec `filament`, T1 = spec `filament_2`). The console echoes
  `ams_mapping = [...]` before the confirm prompt — verify it by eye. A reversed map
  prints the inverse colours and wastes the whole print.
- Current spools change when Ron swaps them — always re-read; don't trust any snapshot.

## Secrets
- The printer access code lives only in `print-console/.env` (git-ignored). It must never
  be committed or written into any file that leaves the machine. `git ls-files | grep -i
  env` must return nothing.

## Layout
- `print-console/` — the CLI (`pc`), `compose_plate.py` (STL+spec → sliced 3MF with
  gates), `print-log.md`, `specs/`.
- `keychain/` — reusable Chewy-font name-keychain generator (`make_keychain.py`) + notes.
