# Running the acceptance gates repo-side

The parts/ generators and gates were authored in the design-office container;
this bundle makes the repo self-contained so they run here too.

## One-time setup
1. `pip3 install numpy shapely trimesh`   (user-level install is fine)
2. `cd parts && ln -sfn stl stl_v13`
   The generators' write_stl() and every gate read/write a directory named
   `stl_v13` next to the scripts; the repo keeps STLs in `parts/stl`. The
   symlink makes them the same place — regenerated STLs land directly in the
   committed tree.

## Support modules (this bundle)
generator.py, generator_v13.py, generator_v16.py, weld.py — the import closure
for every parts/ script. Also two v16 geometry-source STLs the gates slice:
131_month_widesquare_v16.stl (receiver mesh form) and 50e_star_hub_v16.stl
(the retired hub, sliced by board_hub_v17's condemnation gate).

## Gate run order for the #167 commit
1. `python3 fixture_r64_v17.py`   (regenerates 168 + runs the r64 gate, 20 checks)
2. `python3 drive_v17.py`         (regenerates 158-161 + 169, runs the seated-stack
                                   gate incl. rev B condemnation, 10 checks)
Both exit 0 on pass. Regenerated STLs should be byte-stable; if git shows STL
diffs after a run, that is itself a finding — report it, don't commit silently.

Optional full suite: detent_v17.py, detent_accept_v17.py, board_hub_v17.py,
mesh_accept_v17.py, assembly_gate_v17.py.
