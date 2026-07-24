# ROADMAP — DEMONSTRATOR -> CLOCK -> WATCH
(adopted 2026-07-19; extends PROJECT-BRIEF. The calendar engine is common
to all three stages; every stage drives through the strike train.)

## Stage A — hand-cranked demonstrator (current)
The machine as designed: crank = time. Print Stage 1 + v1.6 skip train,
run the bench list. NEW BENCH ITEM (feeds Stage B): MEASURE CRANK TORQUE —
steady-day turning torque AND peak torque through a full cascade evening
(21h+22h+23h+daily in sequence, both directions). These two numbers size
the Stage-B motor. Add the tier-1 FRICTION-SET HOUR RING to the build
(press-fit indicator ring on the crank hub) — costs one part now, becomes
the hand-restore after any fast catch-up forever after.

## Stage B — motorized clock
Gate to enter: Stage A bench passes; torque numbers in hand.
- DRIVE: motor replaces the hand at the SAME shaft (the 24h wheel input).
  Nothing downstream changes — the design laws guarantee the mechanism
  cannot tell a motor from a hand. Geared 1 rev/24 h continuous.
- MOTOR CLASS: stepper + driver + RTC preferred over a synchronous clock
  motor, because it buys the killer feature for free: CATCH-UP MODE.
  After any stoppage (power loss, transport), the controller compares RTC
  time to mechanism state and fast-runs the motor THROUGH the strike
  train to the present. This is the UN-32's date-pull, implemented in
  software — the drawer scenario, self-healing. Requires a state
  reference: one index sensor (optical flag on the 24h wheel at midnight)
  + the controller counting days; or absolute state entered at power-up.
- TORQUE: motor + gearing must clear the measured cascade PEAK with
  margin (strikes are torque spikes at 21/22/23/24h); a small flywheel or
  compliant coupling smooths them. Backward catch-up is allowed by the
  mechanism; the controller may use whichever direction is shorter.
- MANUAL OVERRIDE: keep the crank on a simple friction/dog coupling to
  the motor shaft — demonstration mode must survive motorization.

## Stage C — spring-driven watch (per PROJECT-BRIEF: ST2525 lineage)
Gate to enter: Stage B clock runs a month unattended incl. one cascade.
- Spring barrel + escapement = real horology; the calendar engine
  miniaturizes per the long-term brief goal (month-advance logic into
  Ron's Seagull ST2525 big-date).
- THE DATE-PULL BECOMES MANDATORY (Ron's call, correct): a stopped watch
  has no controller to self-heal; recovery is human, through the crown.
  The tier-2 design seeds the keyless works: two-position dog clutch on
  the input axis — position 1 drives hands + calendar (normal), position
  2 (pulled) drives the STRIKE TRAIN ONLY, hands stationary; weekday
  takeoff rides the striker side so weekday stays married to the date.
  Push-in re-couples = the user's declaration of current time.
- ACCEPTANCE TEST (the drawer protocol): run the watch; stop it; let
  calendar-weeks pass on paper; recover using ONLY the crown: pull to 2,
  spin the date forward through at least one month end (verify skips
  execute), overshoot deliberately, back up (verify bidirectional
  recovery), push in, set hands. The mechanism must land calendar-true
  with zero disassembly and zero forbidden hours.

## The through-line
One strike train, three drivers: a hand, a motor, a mainspring. The
design laws exist so that none of the three can ever ask the calendar a
question it can't answer.
