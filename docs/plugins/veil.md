# Veil

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Veil muffles a **mono voice** the way the womb does — a steep lowpass around
~500 Hz, *"like speech from behind a heavy curtain."* Real prenatal hearing works
this way: tissue and fluid attenuate everything above ~600 Hz, and newborns
actually *prefer* a low-pass-filtered version of their mother's voice over a clean
one. Veil is that curtain — a thin thing you hear *through*.

It's an **effect**: put it on a mono voice track (recorded, TTS, sung — anything).

**Why Veil and not the [Resonant Sweeping Filter](sweeping-filter.md)?** They're
different tools even though both are resonant lowpass filters:

- Veil gives you a **still, wide muffle** — stereo width from *fixed, independent*
  Left/Right cutoffs, sitting perfectly still. The Sweeping Filter's stereo comes
  from a *moving* sweep; stop the motion and its width collapses. Veil's doesn't.
- Veil cascades up to **−48 dB/oct** — a far deeper muffle than the Sweeping
  Filter's fixed −12 dB/oct.
- Veil's two channels are **independent**, so their drifts can wander apart and
  together — the *width itself breathes*. The Sweeping Filter shares one band
  across the stereo field, so it can't.

Short version: reach for the Sweeping Filter when you want *movement*; reach for
Veil when you want a *still, deep, wide muffle* (that can then breathe). They also
**stack** — Veil for the character, Sweeping Filter after it for motion.

## Signal Architecture

- **Mono sum in.** The input is summed to mono, then fed to two independent filter
  chains — so a mono voice becomes stereo. (A lowpass alone can't do that; the
  width is *manufactured* by making the two channels differ.)
- **Two independent lowpass chains (L / R).** Each is a cascade of 1–6
  two-pole state-variable lowpass stages (Slope), with its own cutoff and its
  own resonance. The sections are zero-delay-feedback (TPT) rather than the
  older Chamberlin form, which is what keeps a six-stage cascade stable — its
  last section sits at Q 3.83 before Resonance touches it at all.
- **Width = the cutoff difference.** Left at 480 and Right at 520 gives a gentle
  spread; pull them apart for more. Because the channels differ only in *spectral
  rolloff* (no phase or delay tricks), a mono sum just averages the two rolloffs —
  **no comb-notch cancellation, safe on a single speaker / phone / HomePod.**
- **Per-channel Drift + Ramp** on both cutoffs and both resonances, so the
  muffle can move (see below).

## Parameters

**Filter side** `Both (keeps the gap) / Left / Right, default Both (keeps the gap)` — which side
the six controls below are editing. Both sides are always live; this only chooses
the view.

**`Both` is not the usual `All`.** Everywhere else in the suite, a picker on All
writes the same value to every option. Veil's stereo width IS the gap between the
two cutoffs and it has no other stereo mechanism, so that would take it mono on
the first nudge. Instead Both shows the midpoint and applies your CHANGE to both
sides, holding the offset — nudge it up 20 and 480/520 become 500/540. At the end
of the range it stops rather than letting the two squeeze together.

**Filter pitch mode** `Hz / Semitones / Cents, default Hz`

**Filter note name** `C-1 to G9, default B4` — a real control in every mode, and
it reads back from the value both ways.

**Filter cutoff (Hz / semitones / cents)** `0–20000, default 500` — the muffle
point for the selected side. Left opens at 480 and Right at 520, and **the
difference between them is the stereo width** — together = mono, apart = wide.

**Filter fine tune unit** `Hz / Semitones / Cents, default Cents`

**Filter fine tune** `-1000 to 1000, default 0`

**Filter resonance (%)** `0–100, default 15` — emphasis at that side's cutoff. Low = a
plain soft muffle; higher = a resonant "throat" around the corner.

**Tuning reference (Hz, all sides)** `20–2000, default 440` — what the note names
are counted from. One for the plugin.

**Slope (dB/oct, all sides)** `−12 / −24 / −36 / −48 / −60 / −72, default −12` — how many
lowpass stages cascade (1–6 two-pole sections). Steeper = more muffled, closer to
the womb's real deep rolloff. −12 is closest to a plain stock lowpass; −72 is a
wall — past the corner almost nothing survives.

Two things hold true at every slope, which is not automatic and took some care:

- **The cutoff number is the actual corner.** It's −3 dB at the frequency you
  set, at −12 and at −72 alike. Cascading identical filter stages — the obvious
  way to build this — drags the real corner *below* the number as you get
  steeper (at six stages, a cutoff set to 480 Hz would really corner near 168).
  Each stage instead gets its own Butterworth Q, which is what keeps the corner
  where you put it.
- **Resonance means the same thing at every slope.** It's spread across the
  stages rather than applied to each, so Resonance 1 asks for about the same
  total emphasis whether that's one stage or six. Applied per stage, the peaks
  would multiply — six mild peaks stacking into a wall.

**Output (dB)** `-60 to +24, default 0` — level trim.

### Transport

New in the 2026-09-15 layout; Veil had none before.

**Transport unit** `Seconds / Beats, default Seconds` — one unit for the three
below. Veil counts in seconds because it has no turn of its own.

**Start delay (in transport units)** `0–1000, default 0` — the effect waits this long
after play: the sound passes through untouched until the delay ends, and drift and
ramp wait too.

**Play for (in transport units, 0 = always)** and **Rest for (in transport units,
0 = always)** `0–1000, default 0` — the
plugin works for one, rests for the other, and repeats. Both must be above zero
or the gate is off, which is what Veil always did.

**Output at rest** `Pass-through / Silence, default Pass-through` — what you hear
during a rest. Crossfaded over 3 ms either way, so neither edge clicks.


### Drift (nested selector)

A slow, perpetual wander on any of the four moving parameters — this is what makes
Veil feel *alive* rather than a static EQ. Pick a target, set how far it wanders,
and it wanders forever. **All targets drift in parallel**; the selector just picks
which one the amount/period/shape sliders are editing right now.

**Drift amount unit** `Target default / Hz / Semitones / Cents / Milliseconds /
Seconds / Minutes / BPM / Beats / Cycles / dB / Percent / Degrees, default Target
default` — what the two amounts below are typed in, for the selected target.
`Target default` is what the amount always meant, so nothing you have set changes.
A unit that cannot fit its target falls back to that rather than inventing a
meaning — Veil has no rate, so Cycles, BPM and Degrees fall back here.

**Drift target** `Cutoff (all sides) / Left cutoff / Right cutoff / Fine tune (all sides) / Left fine tune / Right fine tune / Resonance (all sides) / Left resonance / Right resonance / Tuning reference / Output / Play for / Rest for` —
which parameter you're configuring. *(Output joined 2026-09-11; its amount is in dB.)*

**Drift up amount / Drift down amount** `units match target` — how far it wanders
above / below the base value. Separate up and down let the wander sit off-centre.
The amount is in the **target's own unit**: Hz for a cutoff (use the big end of
the range), 0–1 for a resonance (use the small end). You tune it *by ear* — nudge
until the wander feels right.

**Drift period** `0–1000, default 20, 0 = off` — how long one full wander cycle takes, in
whatever unit **Drift period unit** is set to (below). **Give Left and Right
cutoffs *different* periods** (say 20 and 31) and the width itself breathes — the
signature Veil move.

**Drift movement mode** `With the target / On a clock, default With the target`, per target,
shown only while the Drift target is Play for or Rest for. With the target, a play or rest
stretch takes its length when it begins and keeps it; On a clock, a drift can end the
stretch you are hearing early or late.

**Drift shape** `Sine / Triangle / Random, default Sine` — Sine = smooth wander,
Triangle = linear ramps, Random = smooth wander to unpredictable targets.

**Drift period unit** `Seconds / Beats, default Seconds` — whether Drift period is
wall-clock seconds or beats at the project tempo, **for the selected target** —
each target keeps its own, since 2026-09-16. On **Beats** the wander follows the host,
so a tempo change carries the breathing with it — and two Veils at 20 and 31 beats
keep their relationship through the change, which is the whole point of the pair.

It sits directly before Drift period, the way every mode and unit in the suite
sits before the value it qualifies.

**Drift rest mode** `Walk through / Freeze in place, default Walk through`
— what the drift does during a transport rest. Drift and ramp each have their
own, because they are their own things.

### Ramp (nested selector)

A **one-time** signed ride on a parameter over N minutes — for a slow, hands-off
change while you settle. Unlike Drift (which repeats forever), the Ramp moves once
and holds. All targets ramp in parallel on their own clocks.

**Ramp by unit** `the same thirteen, default Target default` — what `Ramp by` is
typed in, for the selected target.

**Ramp target** `Cutoff (all sides) / Left cutoff / Right cutoff / Fine tune (all sides) / Left fine tune / Right fine tune / Resonance (all sides) / Left resonance / Right resonance / Tuning reference / Output / Play for / Rest for` — which parameter rides.

**Ramp by** `units match target` — the signed amount to move by. **Positive
on both cutoffs = the voice slowly CLEARING** (the muffle opening, as if the baby
were growing); negative = deepening / darkening.

**Ramp duration (in ramp time units)** `0–1000, default 0` — how long the ride takes.
`0` = off.

**Ramp rest mode** `Walk through / Freeze in place, default Walk through` —
what the ramp does during a transport rest. It sits here, in the block it
freezes, rather than up in transport.

**Ramp engage (all targets)** `Off / On, default Off` — a freeze/resume gate. While On the
ramp advances; flip Off and it freezes where it is; back On and it resumes (it does
*not* restart). Only pressing transport Play restarts a ramp from the beginning.

**Ramp start delay (in ramp time units)** `0–1000, default 0` — wait this long after
engaging before the ride begins. "Let me settle first, then start clearing."


#### Drift play for / Drift rest for

The drift wanders for `play` periods, then **freezes exactly where it stands**
for `rest` periods, then wanders on. Without these, drift never settles — the
only way to stop it was to switch it off, so stillness was not available as a
musical choice. Both must be above 0 or the gate is off, which is the default
and behaves exactly as it always did.

Counted in **drift periods**, so there is no second unit and no arithmetic: set
the period once, then say how many of them.

**The fraction decides where it parks, and that is the whole control.** A whole
number always stops at the same point in the wave — the neutral one — so the
pause is nearly inaudible. Add a fraction and it stops somewhere with a value:

| play | where it parks |
|---|---|
| `2` | neutral, every time — effectively invisible |
| `2.25` | the crest — drifted fully **up** |
| `2.75` | the trough — drifted fully **down** |
| `2.5` | neutral again (the other zero crossing) |

**And the park point rotates.** Each freeze lands further round the wave than
the last, so a fraction like `1.75` cycles through four positions before it
repeats, and only one of those is dramatic. `1.2` gives five positions with two
different partial parks. That rotation is why the result is hard to predict by
ear, and it is the reason to prefer an awkward fraction over a tidy one.

**Set both `up` and `down` amounts to get the full effect.** With only `down`
set, every park on the positive half of the wave lands at no-change, so half the
holds do nothing.


#### Ramp time unit

**Per target** since 2026-09-16, so one target can ramp over minutes while another
steps in beats. Until then it was one unit for every ramp, which nobody had chosen:
it came across in a port. Rozaya, 2026-09-15: *"after all the work we did to make
things per-target in ramp, why?"*

**Minutes** is wall-clock and remains the **default**, so every existing project
is bit-identical. **Seconds** is the same clock at a scale that suits a short
ramp — added 2026-09-05, because a thirty-second ramp used to mean typing `0.5`
minutes, and working that out is exactly the kind of sum this suite exists to
take off you. **Beats** reads the Ramp's four time values — duration, start
delay, play, rest — as beats, following the project tempo live.

There is no **Cycles** entry here, unlike the Tremolo and the filters: this
plugin has no rate, so there are no cycles to count, and an option that did
nothing would be worse than its absence. The list is `Seconds / Minutes / Beats`.

Beats, never bars: bars would need the time signature, so the same number would
mean different things in different meters and would shift under you if the meter
changed. Beats is what REAPER actually counts.

The time controls it governs say `(in ramp time units)` rather than naming a unit,
because the unit is whichever one the selected target is using.

#### Ramp play for / Ramp rest for

The **staircase**: the ramp climbs for `play`, holds still for `rest`, and
repeats — climb, settle, climb, settle — instead of one smooth slide. Read in
whatever `Ramp time unit` selects, so `1` is one second, one minute or one beat.

**The holds come out of the duration, they do not extend it.** A 10-minute ramp
with holds is still a 10-minute ramp; the staircase changes only *how* you get
there, never *when*. Both values must be above 0 or the ramp is smooth, which is
the default.

The last climb puts you on the **landing**, and the landing is part of the
staircase — a 32-beat ramp stepping 2 and holding 2 reaches its destination on
beat 30 and stands there for the last 2.

Note this is not the same as **Ramp engage**, which is the manual version of the
same idea: engage off freezes the ramp where it stands, engage on resumes it.

## Usage Notes

- **Feed it a mono voice.** If the source is already stereo, Veil sums it to mono
  first — it's built to *create* width, not preserve existing width.
- **Set the muffle, then the width.** Dial both cutoffs to taste (start ~500),
  pick a Slope (−12 for gentle, steeper for deep), then spread the two cutoffs
  apart until the stereo feels right.
- **Breathing width:** drift Left cutoff and Right cutoff on *different* periods.
  The gap between them wobbles, so the stereo image gently opens and closes — the
  thing the Sweeping Filter can't do.
- **The clearing:** target both cutoffs with a positive Ramp `by` over a
  long duration — the voice slowly emerges from behind the veil.
- **Pairs with** the [Womb Sound Generator](womb.md) (heartbeat / breath bed
  underneath), and [Bubbler](bubbler.md) / [Dapple](dapple.md) for fluid texture.

---

*Veil is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic).*
