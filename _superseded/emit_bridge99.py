#!/usr/bin/env python3
"""Emit the findings 97-99 bridge-jumper set + run acceptance.
Run from parts/ with generator.py + generator_v13.py importable (or /mnt/project).
Parts: 50_detent_star_r4, 51_bridge_arm, 49_fixture_r54, 33_receiver_month_r2."""
import generator_v16 as G
G.part_50_detent_star_r4_v16()
G.part_51_bridge_arm_v16()
G.part_49_fixture_r54_v16()
G.receiver_lamina_r2("33_receiver_month_r2_v16.stl", 5)
ok = G.acceptance_bridge_99()
print("BRIDGE SET " + ("ALL GATES PASS" if ok else "*** GATE FAILURES ***"))
