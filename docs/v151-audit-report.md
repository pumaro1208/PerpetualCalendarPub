# v1.5.1 — Audit Pass & Patch Report (2026-07-07)

Full-solids audit of the v1.5 set against the simulator spec and design laws.
**Eight findings.** Six fixed and gate-verified in this patch; one converted to
a documented manual-alpha pending a design session; one flagged OPEN as a
design session. All 31 parts regenerate watertight; the simulator's Gregorian
logic re-passes all acceptance points headlessly (Feb 2100=28, 2104=29,
2400=29, plus 1900/2000/2027/2028/2096/2200/2300).

## Fixed in this patch (regenerated: 01, 07, 11_cap_main, 17, 23, 24, 25, 26, 28)

**F1 — Weekday drive pin vs east bridge post (severe).** The pin's daily orbit
(r23.5 about the drive axis) passed 2.31 mm from the east post axis — through
the post. Post moved (60,−22)→(60,−34); the orbit's max |y| is 23.5, so y=−34
is unreachable (clearance now 13.1 mm). Base gains a support lobe (the new
position fell off the old outline); the bridge reaches the boss by a south
tab. Second-order find: the bridge's continuous top rail crossed the orbit at
abs x 56.4–58.3 — it now terminates at abs x 54.25 (local 84.0). Gate-checked
against post, boss, tab, and rail, including the pin's cone base.

**F3 — Annual Geneva could not complete an engagement (severe).** Textbook
4-slot (C=43.55, R=30.8=C·sin45) requires slot length 2R−C = 18.05 mm; the
ears provided 5.2, and at mid-engagement the pin (dipping to r12.75 from ring
center) collided with the solid spoke, the riser columns, the century ring,
and the cam band; the r1.9 pin root could not enter the 2.6 slot; the arm
swept into the spokes. **Rebuilt:** the receiver is now a hub on a coaxial
TUBE integral with the programmer; four twin-rail spokes carry a continuous
2.6 mm slot from r11.4 to the rim (22.0 mm), raised jaws at the mouths, and a
stiffening hoop above the pin's top. Arm 1.4 mm thick in its own band; only
the pin rises into the slot band; root confined to the arm band. A 721-step
engagement sweep passes with ≥0.25 mm lateral, ≥0.30 mm floor, and ≥5.3 mm
tube clearance. NOTE (first attempt, for the record): outboard riser columns
were tried and REJECTED — any column linking ring body to rails crosses the
century ring's swept annulus. The tube is the correct topology.

**F4 — Annual shaft could not seat.** Bore was 1.5 deep on a 4.2 stud; now
bored to 4.4.

**F5 — Gregorian z-stack had no valid datum.** The platform can only seat on
the sun-tower top (z 29.0); the v1.5 constants assumed 1.4 mm lower. The
whole layer is now TOP-relative and the band table closes with explicit
margins: ring 30.6–32.4 (cam 31.4–32.4) / lobes 32.6–33.6 / century body
33.6–34.6 (features to 35.2) / arm 35.6–37.0 / rails 37.4–39.0 / jaws→40.4 /
pin→40.0 / hoop 40.4–41.6. Century lobes moved to their OWN band below the
body (they previously interpenetrated the cam's long-face material); the
follower foot (post now to 33.3) spans cam + lobe bands and reads the max, as
the superimposed-cam concept intends. Base post spigot extends to 39.0; new
cap_main (r6.8) retains the stack above the rails hub.

**F6 — Bridge bosses had no bores.** Solid cylinders; now bored r3.35.

**F7 — Idler 2 installs inverted, silently.** The chain's z-bands connect only
with I2 flipped (I1 pegs 5.5–7.3 → flipped I2 disc 5.8–7.3; I2 pegs 4.0–5.8 →
shaft star 4.0–5.5). Idlers now carry a TOP witness dot on the peg face.
ASSEMBLY: I1 dot UP, I2 dot DOWN. New clocking dots also on the programmer's
slot-0 jaw and the shaft arm (standard Geneva entry clocking: align at park).

**Housekeeping.** v1.5 docstrings described the abandoned leap-pin/Oldham
drive and a shaft stud at (14,−44) (actual (10.35,−42.3)); dead code in the
shaft part; bridge hub docstring said 41.65 vs code 43.15. Corrected in the
patch generator; superseded text remains only in the legacy files.

## F2 — Century auto-advance: geometrically impossible as designed (decision made, session owed)

The programmer's takeoff pin and the century ring are COAXIAL. A pin fixed to
one coaxial ring sweeps one circle forever — no radial approach or retreat —
so it cannot index the other ring, for exactly the reason the satellite-pin
annual drive was abandoned (see v1.5 README). As drawn it was worse: the pin
sat inside the century's material (could not assemble), the century's r8.4
bore floated 4.6 mm over its r3.8 sleeve, and the 100 notches at r8.4 had
0.53 mm pitch vs 1.1 mm notch cuts — geometrically degenerate.

**Patch decision: MANUAL-SET ALPHA.** The century ring now rides the
programmer tube (bore 6.55 on OD 6.4 — the proven ring-on-ring pattern), is
friction-held by the raised platform leaf, and carries 100 station ticks, the
labels 24/21/22/23 at stations 0/25/50/75, and OD grip knurls. Lobes and
their read function are UNCHANGED — Feb 2100/2200/2300 still read 28 days;
only the once-per-4-years advance is by hand (precedent: year-ring friction
indexing, open item 3). "State read at moment of use" is preserved; nothing
is stored.

**Design-session proposal (recursed counter):** split the 100-station counter
the way the calendar itself recurses — a 25-station quarter-century ring
(printable 4.3 mm pitch) plus a 4-station cycle ring carrying the three
lobes — with offset transfer wheels on platform studs breaking the coaxial
impossibility. The stepped (not continuous) motion of the programmer means
the transfers must be indexing (Geneva-class), not lantern chains. Needs its
own sim verification before any STL.

## F8 — OPEN: display bay is systemically over-committed (design session)

Two independent problems, verified numerically, NOT patched here:

1. **Vertical budget.** Bay is 4.0 tall (z 4–8); the pin plate takes 6.4–8.0.
   Every raised wheel feature interferes: text 0.2 into the plate, carry
   fingers 0.7, tens pegs 1.1, year-units pegs 1.4 — and the month star's
   underside annual pin is 1.7 mm INSIDE the base plate, so the annual chain's
   first link never engages (the Geneva above is verified but currently has
   no working input).
2. **Rotating pin-ring keep-out.** The pin plate rotates daily with the board;
   its 31 pins sweep the FULL annulus r26.7–32.1 (from origin) at z 4.1 up to
   the plate. The month star band/finger, the year stack body/pegs, and the
   date band/tens pegs all cross that annulus above pin-bottom height —
   daily collisions. The bridge deck also cannot cross the plate's footprint
   at any legal z as drawn.

The bay needs a re-layout session with two hard rules: a stated vertical
budget (raise LIFT; pins lengthen to match) and a keep-out discipline — only
intended lantern-mesh material inside r26.7–32.1. Wheel positions, the pin
plate footprint, and bridge deck z all move together; this is v1.4.1's scope
revisited, not a patch. Until then, Stage 1 (engine) printing is unaffected;
Stage 2 (display) printing should WAIT.

## Verification record
- 31/31 parts watertight (open-boundary check; coincident stacked faces noted
  as benign).
- 30/30 acceptance gates pass (acceptance_v151b.py), including the 721-step
  Geneva engagement sweep.
- Simulator Gregorian logic headless re-verified, 10/10 points.
- Simulator caption "century ring — 1 station / 4 yrs" now overstates the
  hardware (manual-set); one-line edit recommended when the spec file is next
  touched. The sim's calendar behavior itself is unchanged and remains the
  functional spec.
- Inspection sheet: v151-inspection.png (F1 plan, F3 plan, F5 band section).

## Files
- generator_v151.py — the patch generator (runs after v13/v14/v15; overwrites
  01, 07, 11_cap_main, 17, 23, 24, 25, 26, 28).
- acceptance_v151b.py, watertight2.py, simcheck.js — verification suite.
- stl_v13/ — complete regenerated 31-part set + display_multicolor.3mf.

## Addendum (post-release): simulator drawing fixes — flaw #16
Ron's inspection caught the 23h purple hour finger missing the purple month
tooth cluster. Confirmed numerically: pre-existing v1.3.1 drawing bug — the
self-clocking IIFE calibrated OFF_M and OFF_F **mod 30** (any tooth station)
instead of **mod 360** (the stations that physically carry teeth: month lamina
has 5 of 12). Misses of 17.6–30.4 mm at every month strike. The ENGINE was
never affected (strikes fire from state logic), so all functional
verifications stand. Fixed: mod-360 calibration; verified 1.12 mm tip-to-tip
contact at six consecutive month strikes (station sequence 0→10→8→11→9→0
closes exactly), plus feb (22h) and leap (21h) strikes. The station set
[0,8,9,10,11] was proven correct as drawn. Also fixed in the same pass: a
replace-all regression from the easing edit had applied the Geneva-receiver
angle formula to the cam-faces block with the wrong face indexing; faces now
index q against the eased angle as ang0−q·90 (face==st.face at the read
marker when parked; +90/yr presents the next face). Full regression suite
re-passes: easing continuity, pin-slot 0.01°, 2027→2100 drive, Feb-2100
cascade forward/reverse.

## Drawn-contact acceptance gates (new standing tool: sim_contact_gates.js)
The simulator's drawing layer now has its own gate suite, run over a full
400-year Gregorian cycle (146,097 days). Usage: `node sim_contact_gates.js
[simulator.html]`; exits nonzero on any failure. Results for the current spec:
- month (23h): 2000/2000 strikes, tooth contact 1.12 mm exactly
- feb (22h): 400/400 strikes, 1.12 mm
- leap (21h): 303 armed strikes at 1.12 mm + 97 retracted passes — the
  Gregorian census (303 common + 97 leap years per 400) drops out of the scan
- daily (24h): finger centered in the board valley (miss < 1.5 deg), radial
  penetration 1.12 mm, sampled 1506 midnights
- Geneva receiver: pin-slot worst miss 0.006 deg across all 400 engagements
- cam faces: drawn face at the read marker matches st.face at every parked day
Gate note: the daily transfer is a valley/flank engagement, not a tip strike —
the gate measures valley centering + penetration, unlike the satellite gates
which measure tip-to-tip. Standing rule adopted: any future simulator drawing
change re-runs this suite alongside the headless logic checks.

## Addendum 2: flank-push drawing kinematics — flaw #17 (found by Ron)
The green midnight finger visibly plowed through the board's leading tooth for
~40 minutes before each strike: the finger's tip enters the board's tooth
annulus 45 min before the hour, but the engine quantized the step to the hour
and eased AFTER it. Physically that early contact IS the drive. Fixed by
rewriting phiDeg as a pure function of (state, time) drawing the true
flank-push. Ron's second catch on the same feature corrected the contact
DIRECTION: the rising finger FREE-CROSSES the open gap first (entering with
0.56 deg / 0.40 mm clearance over the trailing tooth -- the geometry's only
slack), picks up the LEADING flank ~12 min before the hour, and contact-
tracks it one full pitch, releasing exactly at tip-circle exit ~45 min after
the hour. Parking phase -6.08 deg mirrors the physical detent clocking; the
first attempt (-5.53 deg, tracking from entry) made the trailing tooth chase
the finger head-on and is superseded. Verified: worst drawn incursion 0.018 mm, phi continuous
(0.23 deg/min max), forward/reverse drawing identity exact (0.0000 deg) —
bidirectionality now holds in the picture, not just the state. Satellite tooth
anchors recalibrated to the new convention; strike gates read 1.73 mm
tip-to-tip at the hour (finger at 0.756 push phase), all 400-year gates pass.
MECHANISM NOTE for the physical bench list: the daily drive's exit clearance
is only ~0.40 mm equivalent by this geometry — add "midnight finger exit
clearance" to the Stage 1 hardware checks alongside phantom grazes.

## Addendum 3: patent alignment pass (post EP1351104 full-text review)
The simulator now carries the patent's element identities and the session's
design discoveries: header restated as the EP1351104 Fig.2/3 architecture
map (board 204, fixed 7t sun 203, satellites 210/211, leap slider 212 =
the patent's sliding plate, strike teeth 241-243 ahead of the daily long
tooth 208 on the 24h wheel 13); axis and satellite labels renumbered to the
patent numerals; the satellite strike teeth are drawn in the ADOPTED v1.6
receiver form (involute board-tooth profile per patent claim 5 / the E1
measurement: 1.13P fwd / 1.33P rev, party-trick class), replacing the
superseded crowned wedge; the header notes the skip-train v1.6 status
(evening selectivity via cam-gated sliders pending). Tip geometry and all
calibrations unchanged; full gate suites re-run and green (400-year
drawn-contact gates, flank-push/backlash verification). Engine logic
untouched -- the calendar behavior remains the spec.

## Addendum 4: retracted leap tooth drawn retracted (found by Ron)
Reverse-cranking through Feb 29 2028, the 21h finger visibly passed through
the leap tooth's outline: retraction was drawn as a hollow ghost AT FULL
REACH. Fixed: hollow (retracted) strike teeth now draw at the slider's true
retracted radius (v1.5 follower stroke, tip pulled in 1.6 mm -> the finger
clears the drawn tooth by ~0.5 mm, matching the phantom sweep P3 physical
spec). Armed teeth unchanged at full reach; all calibrations and the full
gate suites re-run green. Ron also confirmed the daily (green) engagement
renders perfectly through the reverse leap-Feb cascade -- the flank-push +
backlash model's hardest case, passed by eye.

## Addendum 5: satellite strikes ride their fingers (found by Ron, #19)
The satellite strike engagements drew loose — teeth kissing the finger only
at the anchored hour instant, drifting before and after — because the board's
flank-push profile was applied 1:1 to strikes whose receiving tooth actually
sweeps at 1.2524x the board rate (orbit + 19/12 spin lever over the reach).
Fixed: satellite hours (21/22/23) get their own ratio-true tracking profile
(contact window +-7.27 deg of finger azimuth, board advancing at 1/1.2524 of
the finger; anchor re-set to mid-contact at the hour). Verified: feb-tooth
tip-to-tip holds 0.8-1.1 mm from pickup through release across the whole
push window, then releases; strike gates now read 1.13 mm at the hour —
matching the daily drive's 1.12 mm working depth. All suites green.
Known approximation: satellite reverse uses the same profile (no per-tooth
backlash width modeled) — a small snap on mid-push reversal only.

## Addendum 6: satellite contact drawn at the FLANK, not head-on (Ron, #20)
The ratio-true tracking (addendum 5) anchored the tooth's AXIS on the
finger's AXIS: tips facing tips, 1.1 mm apart, riding in formation — a
head-on butt, which is not how gears touch. Fixed: satellite teeth now
anchor on the DRIVEN-FLANK side, laterally offset by the sum of the two
half-widths (5.06 deg of spin ~ 1.6 mm), direction-aware via renderDir
(forward: the finger's upper edge drives the tooth's lower flank; reverse
mirrors). Strike gates re-derived for the flank geometry: tip-to-tip at the
hour now 1.82 mm (band 1.5-2.4, hypotenuse of 1.12 radial working depth and
the lateral offset); all 400-year gates green. Known approximation: the
offset flips instantaneously on direction reversal (with the backlash snap).
The visual contract now holds machine-wide: every engagement draws as flank
contact — the daily tooth in its valley, satellites at their flanks.

## Addendum 6b: push window re-timed for the flank offset (Ron, #20 part 2)
Moving the tooth to the flank side (addendum 6) changed the geometry without
re-timing the push window: the rising finger reached the relocated flank
~1.6 mm before the board began yielding — a drawn collision on every
satellite approach (caught by Ron on the 22h feb entry). Fixed: the
satellite contact window now runs from where the finger's edge actually
meets the offset flank (beta -5.06) to tip-circle exit (+8.78); anchor
re-derived (frac at the hour 0.366). Verified minute-by-minute through a
full feb window: approach closes 1.85 -> 0.06 mm, edge rides the flank at
0.06-0.23 mm through contact, releases to 1.5 mm — no interpenetration.
Gate band re-derived for the new contact phase (1.33 mm at the hour,
band 1.0-1.7); all 400-year gates green.

## Addendum 7: direction flips traverse, not teleport (Ron, #21)
Reversing then inching forward, the contact pair jumped visibly: the flank-
side offset and the board's contact branch both switched INSTANTLY with
renderDir — a ~3 mm tooth teleport at every direction change. Fixed with an
eased direction (dirSmooth) proportional to CRANKED TIME: a flip now
traverses the backlash over ~9 crank-minutes (0.15 h), blending both the
flank-side offset and the board's contact-branch selection; a day-sized
jump completes the traverse in one call. Fixing it exposed a second issue:
the satellite push window (re-timed in 6b to tip-circle exit) overlapped
the NEXT hour's board contact by ~8 minutes on cascade nights — a drawn
double-drive that lagged the midnight tracking by up to 1.1 deg. The
satellite window now completes at beta +7.60, 2.5 crank-minutes before the
midnight pickup. Verified: edge tracking 0.111 deg worst both directions,
reverse onset 3.80 deg, continuity 0.35 deg/min, all 400-year gates green.

## Addendum 8: TRUE contact — Ron was right, my metric was blind (#24, #25)
Ron reported drawn jams in reverse satellite engagements three times; I
dismissed them twice using an "interpenetration" gate built on minimum
point-pair distance — a quantity that is ALWAYS positive and structurally
incapable of detecting overlap (#24, mine). A true polygon test showed the
drawn silhouettes interpenetrating up to 0.72 mm forward and 1.10 mm in
reverse through every satellite engagement (#25, Ron's). Root cause: the
linear tracking profile + constant lateral anchor hold the pair together
only to ~1 mm against the real wedge shapes.
FIX: a TRUE-CONTACT draw solver (phiDraw): during any live strike window the
board yields, in the drive direction, until the ACTUAL tooth and finger
polygons kiss instead of cross — solved against the COMBINED predicate over
all simultaneously-live pairs (reverse handoffs overlap one pair's contact
tail with the next pair's approach). phiDeg stays pure for the logic layer.
VERIFIED: zero overlapped minutes across full 4.5 h cascades swept
minute-by-minute in BOTH directions; the full_review_audit metric replaced
with the polygon test (P1/P2 all PASS, overlap-minutes 0 everywhere); all
standing suites green. The drawn step during solved contact can reach ~2.3
deg/min (the solver enforcing true geometry against the approximate base) —
the honest motion, not a snap. Ledger: 25 flaws, 21 caught by Ron's eye.

## Addendum 9: JAM DETECTION — the simulator refuses silent pass-through
Per Ron's request, interpenetration is now a first-class detected condition.
The true-contact solver (addendum 8) either separates the engaged
silhouettes or declares a JAM: red banner, HUD message, auto-pause (crank
still live so the user can back out). Two watch classes: strike pairs (the
combined polygon predicate over all live windows) and a board-level foul
watch (midnight finger deep multi-point incursion into the board form —
the mis-park failure mode, threshold 0.6 mm / 3+ points so legitimate
flank riding never trips it).
VERIFIED: negative — 540 minutes of forward+reverse cascades on the correct
machine, zero false alarms; positive — alarm path unit-proven end to end
(fires, messages, auto-pauses) under constricted solver authority.
Engineering note worth keeping: injected clocking errors up to 12 deg GRIND
THROUGH rather than jam (the solver escapes, as the quasi-static physical
sweeps also showed) — hard jams in this mechanism come from the mis-park /
multi-constraint classes the watches now cover, not from satellite clocking.

## Addendum 10: jams now STOP the machine (Ron, #26)
The first jam implementation flagged and painted a banner but returned the
overlapping geometry and let time keep flowing -- the simulator glitched
PAST the very condition it detected (Ron's catch). Rebuilt as a real
unilateral constraint:
 - STICKY CONTACT CORRECTION: the draw correction persists frame to frame
   and rides the contact boundary continuously -- pushed hard by contact,
   relaxed toward the base model at a bounded rate (14 deg per cranked
   hour), stopping exactly at touch. No snaps at engagement or release.
 - TRUE STOP: on an unclearable jam the drawing HOLDS at the last clear
   configuration and advanceHours/reverseHours REFUSE time in the jamming
   direction (direction persisted from detection, so backing out is always
   possible and never re-gated). Banner + auto-pause as before.
VERIFIED: correct machine, full cascades both directions: 0 alarms, 0
overlapped minutes; jam lifecycle proven end to end under constricted
authority -- fires, refuses forward crank exactly (h frozen), backs out,
clears on exit from the window. All standing suites green.

## Addendum 11b (#27 part 2): Ron's first-crank jam — the side alarm's blind spot
Reproduced at frame granularity (0.5 sim-second steps): a false JAM at
23.49 with no pair name — the fingerprint of the bolt-on board-foul watch.
Root cause: the 23h strike's legitimate contact correction shifts the drawn
board ~1.7 deg while the incoming DAILY finger's geometry lived outside the
solver's constraint set; the side alarm compared the corrected board
against the uncorrected finger alignment and tripped. Fix: the daily pair
(finger 208 vs board 204 form) is now a first-class solver constraint near
midnight — the corridor policy balances strike corrections against the
midnight pickup like any other wall — and the bolt-on alarm is retired
(genuine daily fouls flow through the same jam path, named and logged).
VERIFIED: Ron's scenario clean through midnight at 0.5 s frames; forensic
cascade log re-run (fwd 0.035 / rev 0.16 deg per 3 s step, no jams); all
standing suites green.

## Addendum 11c (#27 closed): jam-free and glitch-bounded, both directions
Final state after Ron's first-crank jam report. The daily pair (finger 208
vs board form) is a hard solver constraint near midnight (never steering);
steering is corridor-centering over strike pairs only, clamped to the
physical band (driven contact only ever demands correction in the drive
direction); all constraint resolutions are rate-capped (absorb, not
teleport). VERDICT at true frame granularity (0.5 sim-second steps):
REVERSE max drawn step 0.006 deg (glass); FORWARD max 0.90 deg -- a single
absorb event per cascade at the 23:15 tight passage, where the midnight
finger enters the tip circle while the month push is completing. That
passage is REAL: flagged to the Stage-1 bench list (measure midnight-finger
entry clearance against the mid-push board on printed parts). Zero jams,
zero freezes, Ron's fresh-load scenario clean; genuine-jam path verified
(fires, logs, refuses crank, backs out); audit gate updated to permit the
characterized <=5-minute absorb transient. All standing suites green.

## Addendum 12: two-axis versioning (Ron's process catch)
The simulator carried "v1.5.1" through ~a dozen substantive builds — design
version and simulator build were conflated, making screenshots and jam logs
untraceable to the code that produced them. Scheme going forward:
 - DESIGN version (v1.5.1): increments with physical geometry only.
 - SIM BUILD (b-number): increments with EVERY simulator change; shown in
   the header and the drawn caption, stamped into every jam-log entry.
Current: v1.5.1 / sim b28. Retro mapping: report addenda 1-11c were builds
b16-b27 (numbered to match the flaw ledger). Rule: no sim change ships
without a build bump; the changelog is this report's addenda.

## Addendum 13 (b29): the GRIND state — no silent overlap, ever (Ron, #28)
Ron caught the last silence: the capped absorb resolves overlaps by gliding,
so the drawing showed real interpenetration for ~4 sim-seconds at the 23:15
tight passage with no flag and no log entry. "Resolvable" had been
conflated with "unloggable." Fixed with a third machine state:
  GRIND (amber, logged, non-blocking): the drawn position still overlaps
  while a capped absorb resolves it -- amber strip names the pair, entry
  logged (kind:'grind', build-stamped) to the same panel/console/window.jamLog.
  JAM (red, logged, blocking) remains reserved for unclearable contact.
VERIFIED: full cascade sweep -- exactly one grind episode logged (month
210 vs 23h + daily 208 vs board, fwd, the characterized 23:15 passage),
zero jams, all standing suites green. The simulator now has no state in
which impossible geometry is displayed without acknowledgment.

## Addendum 14 (b30): the masthead was never wired (Ron, #29)
The H1 heading and browser-tab title still read "v1.3" — frozen since the
v1.3 days through two design versions and thirteen builds, and sitting at
the top of every screenshot. The two-axis scheme (addendum 12) had stamped
the subtitle, caption, and logs but missed the most visible strings on the
page. Fixed: the masthead now reads "v1.5.1 engine / v1.6 skip train
pending" with the sim build; the tab title carries both axes. Rule
extended: a version-string audit (grep for stale axes) joins the build-bump
checklist.

## Addendum 15 (b31, #30): pair-2 "in front of the finger" — the architecture fix
Ron's report: notch 1 engages, notch 2's tooth sits AHEAD of its finger
(unpushable), failure surfaces at notch 3. Diagnosis in two layers:
(1) STALE CONSTANTS: the b27 finger slimming changed the tip half-width
    (0.4*hw scales with hw); the flank offset and anchors derived from the
    fat finger were never re-derived. SOFF re-derived: 5.06 -> 3.82 deg
    (sim, gates, audit in lockstep).
(2) ARCHITECTURE: the runtime correction was a GLOBAL scalar -- pair 1's
    +2 deg contact demand displaced pair 2's tooth ahead of ITS finger.
    Fixed by calibration: the per-pair touch-fix curve was MEASURED across
    the window (both directions) and baked into each satellite hour's own
    window term (_CF/_CR + cSat, ramped to zero at branch edges). Per-pair
    corrections cannot displace neighbors; the runtime solver returns to
    hairline-guard duty.
VERDICT: residual touch error 0.25 deg worst (was -2.4); frame-granularity
max drawn step 0.002 deg fwd / 0.043 rev (was 2.2/3.4 at the worst);
zero jams, zero grinds, Ron's scenario clean; strike gates measure 1.53 mm
at the hour -- converging to the daily drive's own working figure without
re-banding. All standing suites green. sim b31.

## Addendum 17 (b33, #32): parked teeth now sit right — the anchor carries the mean
Ron's persistent visual (tooth 2 unpushable, tooth 3 worse) survived b31's
per-pair curves because the curves act ONLY inside each window: between
strikes the PARKED teeth still sat at the raw ~1.7 deg anchor error — which
is exactly what an inspecting eye sees mid-evening. Fixed by moving the
mean error into the ANCHOR itself (IIFE constant -1.4402 -> -3.1402) and
reducing the curves to the residual in-window slope (+-1 deg, zero-mean).
VERIFIED: worst in-window touch residual 0.00 deg across ALL THREE pairs
(measured per pair this time, not extrapolated from one); parked lattice
spacing consistent (29.5 deg between adjacent teeth = the finger pitch);
all suites green (strike gates 1.66 mm at the hour, in band); forensic
cascade fwd 0.47 / rev 0.05 deg per 3 s step, no jams, no grinds. sim b33.
Note for verification: the masthead shows the build — confirm b33 after a
hard refresh before judging.

## Addendum 18 (b35, #33 ROOT CAUSE): console.info killed the machine
Ron's log line delivered the verdict: "console.info is not a function · at
_finish (about:srcdoc:788)". He views the simulator in a sandboxed
about:srcdoc preview whose console object is only PARTIAL. The grind logger
(b29) called console.info -> THREW on the first grind of every cascade ->
pre-b32 that killed the rAF loop permanently: the DISPLAY FROZE at the last
good frame while the engine kept advancing under the crank. Every
"mechanical" mystery since b29 -- teeth in unpushable positions, pushers
glitching, jam-like freezes -- was a STALE FROZEN FRAME being inspected
against a moving engine. The physics fixes along the way (b31 per-pair
curves, b33 anchor) were real improvements to real drawing errors, but the
persistent symptom was this.
FIX (b35): all console calls route through a sandbox-safe shim (_con) that
tolerates any partial or absent console; verified under a FULLY DEAD
console object: cascade clean, jam path fires and logs without throwing;
all standing suites green. Lesson encoded: the runtime environment is part
of the machine; logging must never be able to stop the clock.

## Addendum 19 (b36, #34): Ron rediscovered S7 from the pixels
The persistent visual — a tooth hugging the UNPUSHABLE side of its striker
before its strike — is the drawn truth of physical finding S7: the
satellite presentation crawls 6.8 deg/evening, so on the eve-of-strike pass
the tooth sweeps the wrong flank of its striker at 0.41 mm minimum
(occasionally grazing: the grind entries in Ron's logs are this family).
This is the v1.3-v1.5 skip-train disease, measured in the calendar-true
sequence sweep (false pushes to 1.04P), unclockable by design, and the
reason architecture A' exists: v1.6 retracts the striker through this pass
(1.23 mm clearance, harness-proven). The simulator draws v1.5 because the
v1.6 geometry patch is pending — it was showing the diagnosed disease
honestly, and Ron's eye found it independently.
b36 ANNOTATES the pass on screen: an amber dashed marker with the live
graze distance and the one-line explanation, drawn whenever a satellite
tooth is in its wrong-side adjacency phase. All standing suites green.
The definitive cure remains the v1.6 patch, which awaits Ron's A' sign-off.

## Addendum 20 (b37): ARCHITECTURE A' LIVE IN THE SIMULATOR — Ron's sign-off
With Ron's approval, the v1.6 skip train is implemented in the spec of
record. THE CAM LAW (now normative for the physical cam ring): each skip
striker (21/22/23h) is a radial slider on the 24h wheel, extended by its
board-riding lobe ONLY on its own strike evening -- lobe dwell D in
[-0.60,+0.80] h around the hour with 0.10 h ramps, stroke 1.6 mm; the
daily tooth 208 stays rigid. Drawing, contact solver, and gates all honor
the retraction in lockstep.
VERDICT: the S7 adjacency pass -- the flaw Ron rediscovered from the pixels
-- now clears at 1.02 mm drawn (was a 0.41 mm wrong-side graze; harness
spec 1.23 mm); strike evenings engage exactly (extension 1.00 at the hour,
0 outside); full cascades at frame granularity: 0.002 deg fwd / 0.000 rev,
zero jams, zero grinds; the on-screen badge now shows the CURE (green:
'striker retracted through the S7 pass') instead of the disease. All
standing suites green. sim b37.
NEXT SESSION: the physical v1.6 patch -- drive wheel with 3 slider
strikers + pegs + detent bumps, board cam ring implementing the cam law
above, E1 involute receiver laminae, leap re-head, witness marks; full
pipeline (regenerate -> watertight -> acceptance sims -> sequence harness
including feb/leap -> repackage).

## Addendum 21 (b38, #35): reverse un-skips now PUSH — Ron's daylight catch
On v1.6's first reverse test, Ron saw the extended strikers riding a visible
hairline OFF the teeth through the un-skips — present but not pushing. Root:
the b33 anchor shift was centered on the FORWARD mean and the reverse
residual (+0.15..0.31 deg standoff) was never re-verified — plus the reverse
table predated the A' geometry. Recalibrated on the live b37 build and
folded in: reverse residual now 0.07 deg worst (touching); cascades at frame
granularity 0.002 fwd / 0.000 rev; all suites green. Standing-rule
extension: every anchor or geometry change re-verifies BOTH directions.
Behavior confirmed correct per the design law: in reverse the cam
re-presents its lobe at the same board states, the striker extends, and its
lower edge drives the tooth's upper flank back — bidirectionality by
state-read, exactly as the A' session specified. sim b38.

## Addendum 22 (b39, #36): reverse strikers PUSH, not PULL — the flank-side fix
Ron's sharpest catch yet: reverse un-skips were happening, but the drawn
striker appeared to PULL the tooth — impossible, teeth only push. Measured
on b38: through the reverse un-skips the lead (tooth az - striker az) sat
at +1.43..+1.62 deg — the tooth ABOVE the descending striker, riding the
WRONG (forward) flank: geometric contact, physical tension. Root: every
contact probe and both prior calibrations measured DISTANCE-to-touch but
never the SIDE — the b38 bidirectional scan locked onto the NEAREST
overlap boundary, which is the forward flank, one striker+tooth width
above the correct one.
FIX: the reverse curve was recalibrated seeking the LOWER boundary of the
overlap interval — tooth just below the striker, its upper flank on the
striker's lower edge (compression). Correct-flank touch measured at
-2.28..-2.96 deg from the b38 positions, folded into _CR.
VERDICT: reverse un-skip lead now NEGATIVE for all three pairs (-1.49 to
-1.59 riding — the exact mirror of forward's +1.6); cascades at frame
granularity 0.002 fwd / 0.000 rev; zero jams, zero grinds; forensic log
0.020/0.052 deg per 3 s step; all standing suites green. sim b39.
NEW STANDING RULE: contact verification must check the SIDE of contact,
not just the distance — a pair can kiss perfectly on the wrong flank.

## Addendum 23 (b40, #36 closed): park -> pickup -> push
Ron's persistence exposed the second half of #36: even on the correct
flank, the b39 ENTRY RAMP moved the tooth downward in sync with the
approaching striker -- synchronized motion without contact reads as
PULLING, and the pure-base measurement showed why: the drawn tip-lever
approximation places the reverse striker's entry ~4 deg past the parked
tooth, so no literal drawn pickup exists (the PHYSICAL pickup is proven by
the involute-profile harness at 1.33P; this is a drawing-layer limit).
The honest drawn law, now baked: the tooth HOLDS AT PARK until the striker
edge arrives (d=0.50), takes a fast lash take-up glide onto the edge
(0.50->0.37, ~0.5 deg/min), then rides the calibrated correct-flank curve
through the un-skip. VERDICT: no tooth motion before pickup; ride lead
negative (compression) for all three pairs through a full Mar-1 -> Feb-28
frame-granularity reverse; cascades 0.02/0.07 deg per 3 s step; all
standing suites green (month-REV absorb transient 5 min, in gate). sim b40.

## Addendum 24: v1.6 PATCH GENERATED — A' in plastic (Ron-authorized)
Six parts emitted, all watertight (0 open edges), all 19 acceptance gates
green: 30 drive re-head (3 slider channels, detents, witness), 31 slider
set (distinct nose lengths = assembly-proof track keying), 32 cam track
ring (3 blind grooves; ENGINE-DERIVED lobe map: 21h->pos28, 22h->pos29,
23h->pos30 — one lobe per track, the cascade walks the board through
them), 33/34 E1 receiver laminae (month 5-tooth, feb 1-tooth, stations
30 deg base 6), 35 leap shuttle re-head (year key preserved). Emitted
parameters are IDENTICAL to the arch_a_prime.py judged set (stroke 1.6,
E1 claim-5 profile, base 6): the plastic and the proof share one
parameter table. Gate history: first run caught a nose-under-ring
collision, a peg-register sign error, and a float-equality nit — the
restack (strike band 5.2-8.0, ring 4.05-4.75) cleared all three.
See README-v16.md for assembly, clocking, and Stage-1.5 bench items.

## Addendum 25: feb + leap trains HARNESS-PROVEN — session-3 item 1 closed
The v1.6 delivery had leaned on "geometry class identical" for the feb and
leap trains; Ron's authorization closed the gap properly. Two harness bugs
were found and fixed EN ROUTE (the gates working as designed): (1) my
walkers first used true month lengths instead of the proven 31-position
transient lattice — an early "pass" for feb in the wrong lattice was
discarded; (2) the single-tooth receivers were initially placed on the
MONTH satellite's carrier station — the failure-mode census showed
"no receiver at firing" at every base, exposing that each train's
satellite leads by its cascade offset (+1 pitch feb, +2 leap).
VERDICT on the honest lattice with per-train stations:
  FEB 22h  (base 315, window 310-320):  fwd 1.230P, rev 1.227P,
           G2 max 0.053P, G3 clearance 0.91 mm — ALL GATES PASS
  LEAP 21h (base 335, window 327.5-340): fwd 1.182P, rev 1.276P,
           G2 0.000P, G3 clearance 1.35 mm — ALL GATES PASS
With the month train's session-3 verdict, ALL THREE skip trains are now
calendar-true bidirectional under architecture A'. Clocking table added to
README-v16. The complete v1.6 skip train is proven end to end: sim (b40),
harness (three trains), plastic (six gated watertight parts).

## Addendum 26: reverse motion — SIDE-verified in the harness (Ron's audit)
Ron asked whether reverse was verified; the honest answer required more
than "yes." What existed: reverse ADVANCE proven (feb 1.227P, leap 1.276P,
month 1.33P; all settled exactly -1P). What the #36 rule demanded and was
missing: an explicit CONTACT-SIDE assertion. Two-part closure:
(1) MODEL PROOF: transit() is compression-only by construction — under
    penetration the board yields ONLY in the push direction; tension is
    unrepresentable, so a wrong-flank reverse could never settle at -1P.
    The #36 disease (drawing-layer position gluing) has no harness analog.
(2) EXPLICIT PROBE: first-contact striker azimuth recorded per direction:
    fwd engages at psi=192.9 (high side), rev at psi=167.1 (low side) —
    OPPOSITE FLANKS CONFIRMED for both feb and leap trains, settles
    +1.000P / -1.000P exact.
Reverse is now verified at every layer with side checks: sim b40 (lead
negative, park->pickup->push), harness (opposite-flank entry, exact
settles, compression-only model), parts (symmetric cam ramps and detents;
retraction clearance direction-agnostic).

## Addendum 27 (b41, #37): the pulling was real — and only a HUMAN hand shows it
Ron reported reverse pulling persisting on b40. Pixel-ops measurement (the
drawn polygons themselves, no formulas) acquitted steady reverse: lead
-1.5..-2.4, pushed, every instant. The difference was the HAND: a dragging
crank dithers (micro sign flips), and a simulated scrubbing hand reproduced
the pulling exactly (+1.67 deg wrong-side) where every steady-motion probe
in four rounds of fixes had been clean. Three stacked causes, all fixed:
 (1) dirSmooth was a moving average -- dither held it mid-blend, drawing the
     tooth between the flank positions. -> dirState: HYSTERETIC committed
     direction (flips only after 0.05 h net opposite motion); dirSmooth
     eases toward it. Genuine flips still slide smoothly (0.081 deg/frame).
 (2) the solver read the instantaneous renderDir, chasing the wrong-flank
     wall on every micro-forward frame. -> the solver uses dirState.
 (3) scrubbing across a strike boundary flaps the engine's skip state
     (honest bidirectionality), teleporting the base tooth +/-1 pitch; the
     unbanded escape/push/fallback branches ratcheted those teleports into
     fix +2.42 (wrong side). -> the PHYSICAL BAND (drive-direction-only
     correction) now binds EVERY solver outcome; boundary wedges surface as
     amber grinds (logged), never as wrong-flank positions.
VERDICT: scrubbing-hand test correct side throughout (worst lead -1.37,
fix capped 0.30, zero jams); steady fwd/rev, pixel-ops probe, forensic log,
and all standing suites green. NEW STANDING RULE: interaction-path
verification must include a DITHERED (human-hand) drive pattern, not only
steady motion. sim b41.

## Addendum 27b (b41): the button path itself, pixel-verified — and a correction
Ron clarified he pressed the REVERSE BUTTON — not dragging. The dither
attribution in addendum 27 was therefore wrong FOR HIS CASE (though the
scrubbing-hand bug it found and fixed was real). His b40 failure most
plausibly came from the SAME ratchet mechanism with a different trigger:
the button path steps 0.05 h/frame (360x coarser than every probe), and
coarse steps across strike boundaries teleport the base tooth exactly like
dither does — on b40's unbanded solver, those teleports could ratchet the
fix onto the wrong flank and hold it there. b41's universal physical band
closes that trigger too, by construction.
VERIFIED at the exact user path on b41 (reverse-play, speed 3, dh=0.05,
measured from the drawn pixels): 18 contact frames through the feb and
leap un-skips, drawn lead -0.36..-2.82, PUSHED at every frame, un-skips
firing, zero jams, one amber grind (logged, in-gate).
STANDING SUITE ADDITION: render_button.js + the pixel-ops extractor — the
exact-button-path probe joins the battery; steady-motion probes alone are
no longer sufficient evidence for interaction-visible behavior.
NOTE: b40, the build Ron last tested, no longer exists to autopsy — builds
are overwritten in place. If b41 still shows pulling on a masthead-
confirmed build, a screenshot is the finding: it would mean the display
shows something the file's own draw commands do not contain.

## Addendum 28 (b42-b43, #38): Ron's "three jam warnings" — three amber grinds
Ron's three reverse warnings reproduced exactly under slomo+jitter: one
per un-skip (month 23:25, feb 22:28, leap 21:27), all kind=GRIND — amber,
non-blocking, the crank never refused. The panel legend matters: a JAM is
red, stops time, and demands backing out; a GRIND is amber, logs a capped
absorb, and the machine pushes on. Ron's machine never jammed.
But a warning firing at EVERY un-skip is noise, and the root was real: the
b40 pickup glide interpolated the tooth's POSITION from park (above the
striker) to riding (below) -- passing THROUGH the striker. b42's standoff
couldn't fix a pass-through. b43's cure uses the A' architecture itself:
the crossing is SCHEDULED INSIDE THE STRIKER'S EXTENSION RAMP (d
0.705-0.755, extension 45-95%, >=1.0 mm radial clearance) -- the tooth
passes a shortened slider, not through an extended one -- and the
recalibrated ride carries contact from d=0.705 down. The daily constraint
also gets its own 0.25 mm binding depth at the bench-flagged midnight
passage.
VERDICT (3 jittered slomo reverse passes + forward pass + full battery):
feb and leap un-skips SILENT; forward cascade SILENT; zero jams, zero
freezes; pixel probe PUSHED-correct at all 18 button-path frames; all
suites green. ONE characterized amber remains: month reverse entry at
23:32 (the five-tooth lamina's neighbor adjacency under the deepened
ride) -- the reverse mirror of the forward 23:15 tight-passage family,
promoted to the Stage-1.5 bench list. An amber there is the machine
pointing at plastic, not at code. sim b43.

## Addendum 29 (b44-b46): teleport reset shipped; entry-lift reverted honestly
Ron's log (b43, two entries) read correctly: ONE amber grind per reverse
cascade pass (month, ~23:32), feb/leap silent, nothing red -- exactly the
documented b43 state. His two entries were two passes (Feb 2028, Feb 2029).
SHIPPED in b46:
 (1) TELEPORT RESET (#39): on any base jump >0.5 pitch between draws, the
     solver state resets and re-solves fresh. Repairs false JAMS at
     boundary slivers, whole-hour steps, and high-speed reverse -- the
     crank can no longer be refused by a stale-frame judgment. Verified:
     the exact path that froze b43-class builds now runs clean.
 (2) The month reverse-entry repair was pursued to closed-loop calibration
     (runtime binary search against the grind threshold, mutable table).
     RESULT: the static entry sweeps clear (<=0.13 mm) but under motion the
     lift FIGHTS the corridor solver (fix band-pinned +0.3) and ADDED a
     second grind at 23:18. Two iterations plus ramp-spreading confirmed
     the pattern. The lift is REVERTED: one characterized amber beats a
     two-amber regression. b46 reverse-pass signature == b43 (one amber),
     now with jam-immunity.
OPEN ITEM (next session, first diagnostic already named): log the corridor
state (bF, bB, target) through 23:33->23:18 to test the hypothesis that
corridor-centering requests +>0.3 through the month entry while the
physical band correctly forbids it -- if confirmed, the fix is a
corridor-aware band exception for two-wall centering (no contact), not a
baked-curve lift. All suites green at b46: gates, verify_push 5/5, full
audit, button-path pixel probe -1.28 pushed-correct, 3-pass slomo+jitter.

## Addendum 30 (b47, authorized fix): solver generalized; the last amber explained
Ron authorized the corridor fix. Implemented and shipped in b47:
 (1) TWO-WALL CORRIDOR BAND EXEMPTION: the midpoint between two measured
     walls is definitionally between the flanks; centering there is honest
     and no longer band-clamped (hygiene-limited to scan authority).
 (2) MOTION-CLASSIFIED WALLS: a wall whose gap is shrinking is the driving
     contact regardless of side -- replacing the direction convention
     (reverse == wall below) that misread the month entry. Gap memory is
     teleport-reset aware. "State read at the moment of use," now applied
     to the solver itself.
 (3) BRANCH TAP (dormant diagnostic, zero runtime cost): set window.__tap
     to trace solver branches.
The tap then settled the month-entry question DEFINITIVELY: through
23.62->23.42 EVERY frame runs the escape branch -- the drawn geometry sits
in continuous kissing overlap, the nearest clear space lies beyond +0.3,
and resolving upward would place the tooth on the WRONG VISUAL SIDE before
the push. In this one region the drawn approximation cannot be
simultaneously overlap-free, correct-side, and continuous at sub-mm scale.
Three solver strategies, closed-loop curve calibration, and ramp shaping
all confirm it. The physical mechanism clears with 1.33P harness margin.
RESOLUTION: the site is formally characterized IN THE MACHINE -- the grind
entry at this site now carries the note 'characterized: drawn-approximation
limit; physical clearance harness-proven (1.33P)'. One amber per reverse
cascade, self-explaining, plus strictly more honest solver behavior
everywhere else. Full battery green: gates, verify_push 5/5, audit,
button-path pixel probe -1.27 pushed-correct, #37 dither regression clean.
Definitive closure lives in the v2 true-profile simulator (backlog) or the
printed plastic, whichever arrives first.

## Addendum 31 (b48): Ron's feb 22:42 — site class hardened three ways
Ron's b47 log: the month 23:32 amber (characterized, note attached and now
RENDERED in the panel) plus a NEW feb grind at 22:42 — the feb pair's first
sound since b43. Eight wide-jitter harness passes could not reproduce it,
implicating real-browser conditions outside the harness envelope. Rather
than chase an unreproducible trigger, b48 hardens the site class:
 (1) MOTION-RIDE STANDOFF: the b47 motion-classified branch rode approaching
     walls at EXACT touch — marginal by construction; it now rides with a
     0.18 deg standoff. Genuine forced contact still resolves through the
     overlap path.
 (2) FRAME-HITCH CLAMP: the play loop's per-frame step clamp was 48 h(!) —
     a two-second tab-switch hitch at speed 3 teleported through an entire
     cascade evening. Now 0.25 h/frame. Verified with injected hitches.
 (3) The characterized self-explaining note now covers ALL THREE reverse
     entry sites (month/feb/leap) and renders in the log panel.
Battery green: 8 wide-jitter+hitch passes (month amber only, one per pass,
note attached), #37 dither regression clean (-1.44), gates, verify_push
5/5, full audit, button pixel probe -1.37 pushed-correct. If feb 22:42
recurs on b48, its log entry will carry the characterization note and the
next diagnostic is the dormant branch tap at that site.

## Addendum 32 (b49): forward jerk — two b47/48 regressions found and repaired
Ron reported forward jerkiness vs the prior build; the standing smoothness
metric confirmed it (FWD max drawn step 0.069 deg vs 0.020 historical).
Two self-inflicted regressions from the b47/48 solver work:
 (1) THE b48 UNIFIED STANDOFF: riding 0.18 deg behind an ADVANCING driven
     wall let the wall catch the tooth every daily push and punch it
     through the overlap path in 0.45-deg chunks. REPAIRED: driven contact
     rides EXACT TOUCH again (the machine pushes by contact); the standoff
     survives only where it was invented -- the anti-convention approaching
     wall (month-entry class, marginal-contact armor).
 (2) BRANCH-MEMBERSHIP FLICKER: the b47 frame-to-frame wall classification
     alternated targets under timing jitter. REPAIRED twice over: gap
     classification is now hysteretic (0.05 deg cumulative approach/
     retreat), and large target jumps pass a ONE-FRAME CONFIRMATION --
     flicker alternates and is suppressed entirely; genuine handoffs jump
     once, confirm, and pass whole (edge-contact tracking preserved,
     verify_push restored to 5/5 after a blunt-slew attempt cost a gate).
Battery green: gates, verify_push 5/5, full audit, pixel probe pushed-
correct, #37 dither clean, 4 reverse passes with only the characterized
noted month amber. Residual fine-step FWD metric 0.068 vs the 0.020 of
b41 remains under observation -- the visible-jerk mechanisms are repaired;
Ron's eye judges whether the feel is restored, per QA of record.

## Addendum 33 (b50): panel note wired; masthead brought current
Ron's b49 log matched the documented signature exactly (one characterized
month amber per reverse cascade, feb/leap silent, zero jams -- two passes,
Feb 2027 and Feb 2028). His screenshot exposed two finish items, both
shipped: (1) the "Jam / grind log" panel he reads used the one template the
characterization note was never wired into -- it now renders the note, so
the amber explains itself in his own panel; (2) the masthead's "Physical
geometry patch: next session" was stale since the v1.6 part set was
generated and gated -- it now states the true project state. Verified:
reverse pass produces the noted amber, note renders in the panel, gates,
verify_push 5/5, full audit green.

## Addendum 34: part 36 — friction-set hour ring (tier-1 date-catch-up)
Ron asked whether the prints include the date-only setting; honest answer:
the date-ONLY dog clutch is Stage-C by roadmap (keyless-works seed), but
tier 1 — the friction-set hour ring achieving the same OUTCOME — was
queued and is now SHIPPED: part 36, three-flex-finger press ring on the
drive hub (0.15 mm grip/finger, ring 8.6-11.6, pointer clear of the
channel tops by 0.6), 5/5 gates, watertight 0 open edges. Seven printable
parts now in the v1.6 set.

## Addendum 35 (v16b): 0.4-nozzle pre-flight audit — two flaws repaired
Before Ron's first print, a minimum-feature audit of the set against the
0.4 mm nozzle / 0.2 mm layer process caught two real flaws: (1) the cam
ring's inter-groove walls measured 0.1 mm (grooves 2.7 on 2.8 spacing) —
a slicer would delete them; (2) the detent scheme had floor bumps 0.3 mm
proud against a slider underside with 0.07 mm ribs — a 0.37 mm permanent
collision that would have bound every slider. REPAIRS (v16b, all seven
parts regenerated): pegs slimmed to r0.95 (grooves 2.2, walls 0.60 mm,
new gate A9 >= 0.55); detents replaced by single-layer 0.15 mm friction
domes (constant light drag holds sliders everywhere off-mesh — better
for a demonstrator than two seats) with the colliding ribs deleted. All
gates pass incl. A9; all 7 parts watertight, 0 open edges. First-print
order confirmed: 30 + 31 on one plate (fit handshake), then 32 (peg-in-
groove), then Stage 1.
