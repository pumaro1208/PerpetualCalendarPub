#!/usr/bin/env python3
"""Emit the FINAL #2 detent set (flag-free central press-fit + moved bridge).
Run from parts/ with generator.py + generator_v13.py importable (or /mnt/project).
Parts: 02e board (big bore), 50d star (disc+central tube), 49 fixture r5.7,
51 bridge (moved in, open bores), 33 receiver r2."""
import generator_v16 as G
import central_hub as C
G.part_51_bridge_arm_v16()
C.part_02e_board_bigbore_v16()
C.part_50d_star_hub_v16()
C.part_49_fixture_r57_v16()
G.receiver_lamina_r2("33_receiver_month_r2_v16.stl", 5)
ok = G.acceptance_bridge_99()
print("FINAL SET " + ("ALL GATES PASS" if ok else "*** GATE FAILURES ***"))
