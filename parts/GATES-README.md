# Running the acceptance gates repo-side

The parts/ generators and gates were authored in the design-office container;
this bundle makes the repo self-contained so they run here too.

## One-time setup
1. `pip3 install numpy shapely trimesh mapbox-earcut manifold3d networkx scipy`
   (user-level install is fine)

   The first three are not sufficient. trimesh needs a triangulation backend or
   every extrude fails with "will not extrude to a volume", and it needs a graph
   engine or `split()` fails with "no graph engines available!". Versions
   verified working repo-side 2026-08-11:

       numpy 2.0.2      shapely 2.0.7    trimesh 4.12.2
       mapbox_earcut    manifold3d       networkx 3.2.1   scipy 1.13.1

   Pin these if byte-stable STLs matter to you — see the epilogue below for why
   they usually do not.
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


## Gate-run epilogue (required)

A repo-side gate run is **verification, not authorship**. The committed STLs are
canon: they are the exact bytes the design-office gates measured and the plates
slice, and `gate -> bundle -> repo -> slicer` is the provenance of every printed
part. So after any gate run, check the regenerated STLs against the committed
ones before doing anything else.

For each rewritten STL compare, committed vs regenerated:

| check | pass condition |
|---|---|
| watertight | true before **and** after |
| Δbbox | `0.000000` mm on every bound |
| Δvolume | `< 0.01` mm³ |
| Δarea | negligible alongside the above |

**All pass → environment noise.** Different triangulation backends split the
same polygon into different triangles; triangle counts will move. Run
`git restore parts/stl`, keep the committed bytes, and carry on. No ceremony, no
commit, no log entry — this is expected.

**Any check fails → stop and report.** That is environment-dependent *geometry*,
which is a real finding. Do not commit over it.

Worked example, #167 on 2026-08-11 — all six equivalent, all six restored:

    part                tris          d-volume     d-area      d-bbox
    158_drive_24h       3450 -> 3424  +0.0006 mm3  -0.0019 mm2  0.000000
    159_drive_23h       3306 -> 3280  +0.0013 mm3  -0.0018 mm2  0.000000
    160_drive_22h       3346 -> 3324  +0.0013 mm3  -0.0015 mm2  0.000000
    161_drive_21h       3550 -> 3542  +0.0010 mm3  -0.0006 mm2  0.000000
    168_fixture_r64     1680 -> 1684   0.0000 mm3   0.0000 mm2  0.000000
    169_sleeve_revC     1040 -> 1040   0.0000 mm3   0.0000 mm2  0.000000
