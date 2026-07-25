#!/usr/bin/env python3
"""Milestone snapshot monitor: while a print runs, save a chamber-camera
frame at first-layer completion, 25%, 50%, 75%, and at FINISH/FAILED,
into snapshots/. Exits when the job ends."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console import connect, take_snapshot  # noqa: E402

MILESTONES = (25, 50, 75)


def main():
    link = connect()
    fired = set()
    try:
        while True:
            pd = link.print_data()
            state = str(pd.get("gcode_state", "")).upper()
            layer = pd.get("layer_num") or 0
            pct = pd.get("mc_percent") or 0

            def snap(tag):
                try:
                    print(f"snap: {tag} →", take_snapshot(tag))
                except Exception as e:
                    print(f"snap: {tag} FAILED ({e}) — continuing")

            if "first-layer" not in fired and layer >= 2:
                fired.add("first-layer")
                snap("first-layer")
            for m in MILESTONES:
                if m not in fired and pct >= m and layer >= 2:
                    fired.add(m)
                    snap(f"{m}pct")
            if state in ("FINISH", "FAILED"):
                snap(state.lower())
                return
            time.sleep(15)
    except KeyboardInterrupt:
        pass
    finally:
        link.close()


if __name__ == "__main__":
    main()
