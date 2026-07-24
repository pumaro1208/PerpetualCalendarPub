# FULL PROJECT REVIEW — Oechslin Perpetual Calendar Demonstrator
## 2026-07-08 · design v1.5.1 · skip train v1.6 (arch A') proven, patch pending

## 1. SIMULATOR (spec of record) — proactively audited this session
New standing tool full_review_audit.js swept every drawn interaction class:
  P1 forward satellite contacts (leap/feb/month): edge-riding contact, no
     interpenetration, continuity <0.35 deg/min ......................... PASS
  P2 REVERSE un-skips (all three): contact + tracking + continuity ...... PASS
  P3 seams: New Year, century-2100 cascade ............................. PASS
Plus the standing suites: 400-yr drawn-contact gates, flank-push/backlash
verification (verify_push), 2100 regression — ALL GREEN.
Found & fixed proactively (Claude's eye, for once):
  #22 reverse un-skip window never mirrored -> blended fwd/rev fracS
  #23 on-boundary float-dust drew the board parked for one frame ->
      state-aware boundary resolution (dust normalize + nearB fallback)
Flaw ledger this session (all fixed, all gated): #16 strike calibration,
#17 flank-push kinematics + parking phase + contact direction + backlash
hysteresis, #18 retracted leap drawn at full reach, #19 satellite tracking
ratio (1.2524x), #20 head-on -> flank contact (+window re-time), #21
direction-flip teleport -> eased traverse (+cascade double-drive), #22, #23.
Known documented approximations: mid-push direction flip blends over ~9
crank-min (physical would dwell); satellite reverse shares tooth width.
STATUS: ready to upload to the project as spec of record (Ron's action).

## 2. PHYSICAL DESIGN STATE
v1.5.1 geometry: 31/31 watertight, 30/30 acceptance gates. Engine (daily
drive) fully verified on real profiles: S1 jumper clocking CLEARED (valley
at mesh to 0.025 deg, park window -1..+4 deg); S2 daily transfer
BIDIRECTIONAL (1.0000P both ways, backlash 24.3 deg crank); S3 margins
flagged for bench (double-step crest 1.02 deg; entry graze 0.021 mm).
Skip train: S4/S7 (forward-only + unclockable selectivity) RESOLVED by
architecture A' — cam-gated slider strikers + patent-claim-5 involute
receivers: judged in the calendar-true harness: fwd >=1.125P, rev >=1.327P,
settled exactly +-1P, selectivity 0.000P on non-skip months, retract
clearance 1.23 mm at the 1.6 mm stroke, registration +-3 deg.
Leap: retract spec healthy (1.6 mm -> 0.65 mm); armed-margin problem
dissolves under A' (pin... receiver push 1.13P vs old 0.507P).
F8 display bay: re-layout session pending (blocks Stage 2 only).
Century: manual-set alpha stands; recursed counter parked.

## 3. PATENT ALIGNMENT (EP1351104, full text reviewed)
Element map faithful (204/203/210/211/212/241-243/208/13); labels now on
the sim. Divergences understood: our receiver form (fixed by E1 adoption),
leap slider location (v1.3's satellite mounting, legitimately re-solved),
selectivity (patent silent; A' supplies the second key). Bidirectionality
is OUR law, not the patent's claim — but latent in claim 5's superposition,
measured at 1.13/1.33P. Ron's Fig. 3 read = template for A' slider guidance.

## 4. VERIFICATION INVENTORY (standing tools, all green today)
Physical: strike_transit_sweep (detent-coupled), phantom_sweep2
(push-classified watershed), sequence_sweep (calendar-true walker) — the
acceptance harness for all future skip-train geometry. Simulator:
sim_contact_gates (400-yr), verify_push (kinematics), full_review_audit
(interaction classes), repro2100. Rule: any geometry -> full pipeline; any
sim drawing change -> full suite.

## 5. QUEUE
 1. Ron: approve A'; Fig. 3 stud-guidance read; upload sim as spec.
 2. v1.6 patch session: slider strikers + pegs + cam ring + E1 receivers +
    leap re-head + witness marks; feb/leap through the harness; pipeline.
 3. P1S arrival -> Stage 1 print (engine minus skip train) + bench checks:
    jumper park phase, double-step count, entry clicks, reverse lag 1.6 h.
 4. F8 bay re-layout (with printed-part measurements in hand).
 5. Sun-mesh orbit sweep; century counter session (parked).
