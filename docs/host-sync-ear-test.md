# Host x ear-test checklist

Written 2026-08-11. Five tests, roughly fifteen minutes. If tests 1–3 pass, the
mechanism is sound and the remaining plugins are the same idea in different
houses.

**Still current, and still the thing to do.** The branch it was written for is
long merged, but **tests 3, 4 and 5 have never been heard on any plugin**, and
tests 1 and 2 have only been heard on the two plugins they name. Checked against
the source 2026-09-04; the control names below are the ones in the plugins today.

**Two things changed underneath it since it was written, neither of which breaks
a test:**

- **`Speed ramp` is now just `Ramp`** on every control (2026-08-31). Test 3 is
  updated to match.
- **`Rate Value` in Host x means BEATS PER CYCLE in EVERY plugin now**, not a
  tempo multiplier. That finished on 2026-09-04 (R13-revised): thirteen plugins,
  and **all three used below are among them**. An earlier version of this note
  said four plugins and that none of the test subjects were affected — true when
  written, false since.

  **Bigger is now SLOWER in Host x.** `4` is one cycle every four beats. `0.5` is
  two cycles a beat. Where a step below says `1`, that still means one cycle per
  beat and reads the same as it always did — which is why the numbers in tests 1,
  2 and 5 did not need changing.

- **Every `Host ratio` picker is retired and hidden.** It was a menu that wrote a
  multiplier for you; there is no multiplier left to write. Test 1 step 7 used
  it and has been rewritten to type the number instead.

**To back out a plugin:** originals are in
`C:\Users\solst\jsfx-backups\pre-hostsync-2026-08\` as
`<name>.jsfx.pre-hostsync.bak`. Copy one back into
`<REAPER resource>\Effects\glasswings\` and drop the `.pre-hostsync.bak`.
Checked 2026-09-04 and it is there. (This used to point at
`C:\Users\solst\pre-hostsinc`, which does not exist and never did on this
machine — so the escape hatch was broken until someone tried to use it.)

**For anything changed on 2026-09-04**, the backups are the dated snapshot
folders under `E:\reaper\finished\backups\snapshots\`, one per migration,
and every plugin's previous build is in git.

**Set the project tempo to 90, not 120, before you start.** 120 is REAPER's
default *and* the fallback a broken tempo read would land on, so a bug that
ignores the project tempo entirely looks like a pass at 120.

---

## Test 1 — rhythm-track against REAPER's own click

The only unambiguous test in the suite. It's a metronome; it locks or it doesn't.

1. New project, tempo **90**. Insert **rhythm-track** on a track.
2. **Rate Mode** → `Host x`.
3. **Tempo (BPM, or beats per cycle in Host x)** → `1` (one tick per beat).
4. Turn on REAPER's metronome. Play.

**Pass:** the plugin's strong beat sits on the click and stays there for 30+
seconds. Two clicks, one position.

**Failure shapes, and what each means:**

- *Slowly separates over 20–30 seconds* — rate is slightly off. The most likely
  culprit is the nominal-60-BPM conversion.
- *Runs at half or double speed* — a mode index landed in the wrong branch.
- *Locks at 120-ish regardless of project tempo* — the tempo isn't being read,
  or is being read once and remembered.

Then, still playing:

5. **Change the project tempo to 120 mid-playback.** It should follow
   immediately and stay locked. This is the test that caught the original bug —
   a remembered reference tempo passes step 4 and fails here.
6. **Stop, play again.** Still locked. `@init` re-runs on every play and wipes
   globals, so anything that remembers across transport breaks right here.
7. **Tempo** → `0.5`. Should double — half a beat per tick is two ticks a beat.
   Then → `2`. Should halve. You type the number now; the Host ratio menu that
   used to write it for you is retired and hidden, because there is no
   multiplier left for it to translate.

---

## Test 2 — sweep-dwell-filter, the new proportions behaviour

This one's new today, so it's the least proven thing in the sweep.

1. Put **sweep-dwell-filter** on something broadband — a pad, noise, anything
   with content across the spectrum. Project tempo **60** to start.
2. Leave the dwell sliders at defaults (4 + 1 + 6 + 1 = 12 sec).
3. **Cycle mode** → `Host x`. **Cycle length (beats)** → `12`.

**Pass:** at 60 BPM, 12 beats is 12 seconds, so it should sound *exactly as it
did before you switched*. No audible change at the switch is the pass.

4. **Project tempo to 120.** The cycle should halve to 6 seconds — same shape,
   twice the speed.
5. **Now double High Dwell, 4 → 8.**

**Pass:** the cycle stays the same length; the high hold just takes a bigger
share of it and everything else shrinks to fit.
**Fail:** the cycle gets longer. That means the override isn't taking and it's
still summing the durations.

This is the part I'd most like your ear on as a *design* question, not just a
correctness one: in Host x those four sliders stop being lengths and become
shape. I think that's better than the alternative. You may not.

---

## Test 3 — Drift and Ramp under Host x (never heard, any plugin)

Use **Full_Feature_Tremolo** — it's in `simple-sequence.RPP` with 2 instances,
so you can hear it in a real project rather than a test bed.

1. **Rate Mode** → `Host x`. **Rate Value** → `1` (one tremolo cycle per beat).
   Confirm it pulses on the beat before going further.
2. **Drift target** → `Rate Value`. **Drift up amount** → `30`.
   **Drift period** → `4`.

**Pass:** the tremolo speeds up and slows down, wandering over a 4-cycle
period — and since a cycle is now a beat, that's 4 beats. Change the project
tempo and the drift period should stretch with it.

3. **Ramp target** → `Rate Value`. **Ramp by** → `-45`.
   **Ramp duration** → `1`. **Ramp engage** → `On`.

**Pass:** over a minute the tremolo slows to half speed, and stays
tempo-locked the whole way down — at the end it should be one cycle every two
beats, not merely "slower".

> **These two numbers were `0.5` and `-0.5` until 2026-09-04, and both would
> have given you a FALSE FAIL.** Drift and Ramp amounts are in **BPM**, in every
> mode, Host x included — the plugin converts, you never do. At tempo 90 with
> one cycle per beat the tremolo runs at 1.5 Hz, so a drift of `0.5` BPM moves
> it by **0.56%** and a ramp of `-0.5` BPM ends at **99%** of where it started.
> You would have heard nothing, reported a fail, and I would have gone hunting a
> bug that was not there. `30` is a third of the rate; `-45` is genuinely half
> speed. Simulated, not reasoned. The error predates the beats-per-cycle change
> — the same arithmetic held under the multiplier — so it has been sitting in
> this document since it was written.

---

## Test 4 — pan following the tempo (also never heard)

Still on Tremolo. Its pan phase rides the same scale factor as the tremolo, so
it should follow the tempo for free.

1. Turn pan on, **Pan Mode** → `Pan Sweep`. **Pan Sweep Rate** → `1`,
   **Pan Sweep Rate Unit** → `Hz`.
2. Change the project tempo and listen to the sweep speed.

**Pass:** the pan sweep speed changes with the tempo.

**But judge this one as a design call too.** The unit says Hz, and in Host x
that Hz value gets scaled by the tempo — so "1 Hz" really means "1 Hz at 60
BPM". Defensible, since you opted into tempo-following. It may also just feel
wrong. If it does, the fix is to give Tremolo's pan its own `Host x` unit
option the way sweep-dwell-filter's now has, and leave Hz meaning Hz.

---

## Test 5 — sweep-dwell-filter's pan (new today)

1. On the sweep-dwell instance from test 2, turn pan on,
   **Pan Mode** → `Pan Sweep`.
2. **Pan Sweep Rate Unit** → `Host x`. **Pan Sweep Rate** → `1`.

**Pass:** one full pan sweep per beat. (Since 2026-09-04 this is beats per
cycle here too, so `1` reads the same as before but `4` now means every four
beats rather than four per beat — bigger is slower.)
**Fail worth catching:** if it comes out 60× too fast or slow, the new enum
entry fell into the BPM branch — the exact by-index mistake that hit Tremolo
and the sweeping filter.

3. Then try **Pan Mode** → `Alternating` with Cycle mode still on Host x. It
   should step one position per dwell cycle, i.e. every 12 beats, with no pan
   rate set at all.

---

## The failure that doesn't sound like a failure

If something is *subtly* out rather than plainly wrong — two instances meant to
hand off to each other sitting slightly apart, reading as sloppiness rather
than as a bug — **suspect Start Delay first.** That's exactly how the Melody
Phase bug presented: one timing wrong by precisely the tempo ratio while
everything around it was right.

Note that sweep-dwell-filter's Start Delay is *deliberately* still in literal
seconds, so staggering two of those against a tempo is expected to need
seconds-thinking.

---

## Reporting back

Per test, the floor is which number and what it did. "3 wandered but the ramp
didn't lock at the bottom" is plenty — I can find it from that.

**And if you have a read on WHY, say that too.** An earlier version of this
section said "don't try to diagnose", which was wrong and would have cost real
time. Rozaya's diagnoses have repeatedly been right and faster than mine —
*"it's not in the start delay, it's in the passage from one note to the next"*,
*"it was using the base rate"*, *"I suspect the problem is in the rate mode
units stuff"* — and on 2026-09-04 a correction to a test's own settings caught a
**false fail** before it happened: I had specified a Depth dB that leaves almost
no tremolo, so the pan steps would have been inaudible and I would have gone
hunting a bug that was not there.

What actually went wrong in the CPU case was not that a theory was offered. It
was that I acted on the theory and never asked for the observation. **So: both.**
Say what you heard and say what you think, and I will hold them apart — the
observation as evidence, the mechanism as a lead worth checking first.
