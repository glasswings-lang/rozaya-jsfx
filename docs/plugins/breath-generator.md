# Breath Generator

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Breath Generator is a synthesized breathing sound source. It produces a continuous, looping breath cycle — inhale, pause, exhale, pause — with independent control over the duration, tone, and envelope shape of each phase. The output is stereo, with the left and right channels using slightly offset filter frequencies to create a naturally decorrelated image.

The plugin generates no audio from an input signal. It is a pure synthesizer and should be placed on an empty FX chain or a track with no audio source.

---

## Signal Architecture

Each inhale and exhale phase is produced by passing independent white noise through a state-variable resonant lowpass filter — a separate filter instance per channel. The L and R channels use different noise seeds, so their noise is naturally decorrelated before filtering. The Stereo Width parameter then spreads the filter cutoffs slightly apart between channels, widening the image further.

The lowpass topology gives the filtered noise its broadband "whoosh" character — content from DC up to the cutoff, with a slight resonant peak at cutoff. The 2026-06-08 rebuild raised the cutoff defaults from ~144 Hz (the original Breath Generator default) up to 800/600 Hz so the breath has spectral energy in the range where breath actually lives, while keeping the original lowpass topology that gives breath its broadband whoosh.

The envelope applied to each phase is a simple amplitude shape — fade in from silence, hold at full level, fade out to silence — with the fade proportions and curve shape set per phase. During the top and bottom pause states, the output is silence.

---

## Parameters

### Rate

The breath has **no rate mode**, unlike every other plugin in the suite, and that
is deliberate: its rate is *emergent* from the four segments below, so there is
no rate value for a mode to qualify.

**Breath rate (per minute, or beats per breath)** `0-1000, default 6.977`
A live, **two-way** control, not a one-shot. It always shows the rate the breath
actually has: move any of the four segments below and this follows, and type a
rate here and the four segments rescale to it, keeping their ratio. In Seconds it
reads as breaths per minute; in Beats it is already beats per breath. It never
writes itself back to zero — a control that destroys its own value leaves the
plugin and REAPER disagreeing about what it holds, and REAPER wins.

**Breath unit** `{Seconds, Beats}, default Seconds`
What the four segments are counted in. Beats follows the project tempo, so the
breath rides a tempo change instead of ignoring it.

---

### Timing

The four segments are absolute durations, and **their sum is the breath cycle** --
which is why halving the inhale genuinely shortens the breath rather than just
giving the pauses a bigger share.

**Inhale (in breath units)** `0.001-1000, default 4.0`
Length of the inhale phase. The breath cycle advances through inhale → top pause → exhale → bottom pause in sequence, then loops. Changing this value mid-cycle takes effect at the next state transition; if the new duration is shorter than the current position, the position is immediately clamped to the end of the state.

**Top pause (in breath units)** `0-1000, default 0.3`
Silence between the end of inhale and the start of exhale. Simulates the natural breath hold at the top of a breath. Set to 0 for an immediate inhale-to-exhale transition.

**Exhale (in breath units)** `0.001-1000, default 4.0`
Length of the exhale phase.

**Bottom pause (in breath units)** `0-1000, default 0.3`
Silence between the end of exhale and the start of the next inhale. Simulates the natural rest at the bottom of a breath. Set to 0 for an immediate exhale-to-inhale transition.

---

### Pitch

The two filter centres -- the inhale's and the exhale's -- sit behind **one**
pitch block rather than having a control each. Pick which one you are editing
with `Pitch target`, or pick `All` to move both together.

They are filter centres rather than generated tones, and they still get notes:
tuning a breath to a note is a real musical act, and the point is musicality
integrated with the rest of the suite rather than kept separate from it.

**Pitch target** `{All, Inhale, Exhale}, default All`
Which centre the five controls below are editing. On `All` they read back the
inhale's values, and moving any of them writes to **both**. A control that has
not moved is never written, so parking on `All` is safe.

**Pitch mode** `{Hz, Semitones, Cents}, default Hz`
What `Pitch value` means. It comes FIRST, before the value, because it decides
whether the note readout means anything -- the one place in the suite where mode
precedes value, and deliberately so.

**Note name** `C-1 to G9, default G5 (inhale) / D5 (exhale)`
The same pitch said as a note. It works **both ways**: pick C4 or type 60 into
`Pitch value`, whichever costs you less, and the other follows. Only meaningful
in `Semitones` mode, where semitones and note positions are the same axis.

**Pitch value (Hz / semitones / cents)** `0-20000, default 800 (inhale) / 600 (exhale)`
**The pitch itself**, not an offset from anything. In `Hz` it is the frequency;
in `Semitones` it is the MIDI note number, so 60 is middle C; in `Cents` it is
that same axis times 100.

**Fine tune** `-1000 to 1000, default 0`
The **one** fine tune, in the unit below. There is exactly one, so nudging by ear
never turns into two controls doing the same job.

**Fine tune unit** `{Hz, Semitones, Cents}, default Cents`

**Tuning reference (Hz)** `20-2000, default 440`
What A4 is worth. One per plugin.

The inhale defaults sit higher than the exhale to match the sharper-turbulence
character of inflow. Because of the sinusoidal frequency-to-coefficient mapping
in the filter, the effective cutoff tracks lower than the stated value at higher
settings, increasingly so above ~1500 Hz.

---

### Envelope

All four fade parameters are expressed as a proportion of the phase duration — a value of 0.3 means 30% of that phase's total duration is spent in that fade region. The fade-in and fade-out proportions for a given phase are not independently clamped, but if their sum exceeds 1.0 the middle hold region disappears and the sound goes directly from fading in to fading out.

**Inhale Fade In** `0.0-1.0, default 0.3`
Proportion of the inhale duration spent fading up from silence.

**Inhale Fade Out** `0.0-1.0, default 0.2`
Proportion of the inhale duration spent fading back to silence at the end.

**Exhale Fade In** `0.0-1.0, default 0.2`
Proportion of the exhale duration spent fading up from silence.

**Exhale Fade Out** `0.0-1.0, default 0.3`
Proportion of the exhale duration spent fading back to silence at the end.

**Fade Mode** `Linear / Cosine / Exponential / Natural`
Curve shape applied to all four fade regions.

- **Linear** — straight ramp. Equal amplitude change per unit time.
- **Cosine** — S-curve. Gentle at the edges, faster through the middle. Generally sounds smooth and natural for breath.
- **Exponential** — squared curve. Slow start, fast finish on fade-in; fast start, slow finish on fade-out. More aggressive.
- **Natural** — sine-based curve. Similar in character to Cosine but with a slightly different arc. Often the most perceptually even-sounding option.

---

### Stereo

**Stereo Width** `0.0-1.0, default 0.5`
Spreads the filter frequencies between L and R channels. At 0.0, both channels use the same filter frequency (the noise is still decorrelated, but the tonal color is identical). At 1.0, the inhale filter is spread ±15% between channels, and the exhale filter ±12%. This creates a gentle, natural-sounding stereo image without hard panning.

**Stereo Flip** `Normal / Flipped`
Swaps the left and right output channels. Useful for adjusting orientation when the breath image needs to be reversed without reconfiguring other routing.

### Start Delay

**Start delay (seconds)** `0–1000, default 0`

Silent for N seconds after playback starts, then the breath cycle begins normally. State machine and filter state stay frozen during the delay so the inhale starts cleanly at delay-end rather than mid-cycle. Re-arms on every transport stop/start. 0 disables the delay.

### Play / Rest Gating (v2.1)

**Play for (breaths)** `0–1000, default 0`
**Rest for (breaths)** `0–1000, default 0`

A per-breath cyclic gate. The plugin breathes normally for **Play for** breath cycles, then sits silent for **Rest for** breath cycles' worth of time, then resumes — the pattern repeats forever. With Play for = 4 and Rest for = 4, you hear four breaths in / breaths out, then about four breaths' worth of quiet (an extended bottom pause), then four more breaths, and so on.

The feature is **disabled when either slider is 0** (the default). With both at 0, the plugin behaves exactly as before.

**What counts as a breath.** One breath cycle is one full inhale → top pause → exhale → bottom pause. The Play counter increments at each completed cycle (at the moment the bottom pause ends and a new inhale would start). At Play for = 4, the fourth completed breath triggers rest — the breath you were in the middle of finishes naturally, then no new breath starts until the rest period elapses.

**What "rest" looks like internally.** The state machine sits paused on the bottom-pause state, which is already silent in normal operation. There's no extra fade or mute logic — the gate just doesn't start a new breath, and the bottom-pause silence extends for the rest period. The breath whose completion triggered the rest finished its exhale and bottom-pause normally before the gate fired.

**Rest length** is measured in breath cycles' worth of *time* — specifically, `Rest for × (inhale + top + exhale + bottom)` in samples. If you change any phase duration mid-rest, the remaining rest length stretches or compresses to match the new total. After rest ends, a fresh inhale starts.

**Transport behavior**: conventional. Stop silences; play re-initializes everything (breath state, period counter, rest timer) and starts fresh from an inhale.

### The seven drift and ramp targets

Both blocks below aim at the same seven targets, and the list is in the order the
plugin's own controls are in:

`Breath rate`, `Inhale`, `Top pause`, `Exhale`, `Bottom pause`, `Inhale pitch`,
`Exhale pitch`.

Pick one with the target selector and the controls under it hold **that**
target's settings; all seven run in parallel regardless of which one is on
screen. Switching the selector saves what is showing and loads the new target's
values, so nothing is lost by looking.

`Breath rate` scales all four segments in lockstep, keeping the inhale-to-exhale
ratio, so it is the whole-breath wind-down rather than one segment's. The two
pitch targets move the filter centres, in whatever unit that target's
`Pitch value` is in -- semitones drift in semitones, Hz in Hz.

**Each target takes its turn.** The five that are read once per event -- the rate
and the four segments -- step forward by one whole step when **their own**
segment begins, so a period of `4` on the inhale means four inhales, walked in
four even steps. That makes them genuinely independent of each other: drifting
the inhale every 2 and the exhale every 3 gives exactly that, where before both
were sampled off one free-running clock whose length the other targets were busy
changing. The two pitch targets are not stepped -- they are applied continuously,
so they can draw the whole curve, and they can move *within* a single breath,
which a segment length can never do.

### Ramp

A one-way journey: the target travels from where it is to `by` further on, over
the duration, once.

**Ramp target** `seven targets, default Breath rate`

**Ramp by** `-1000 to 1000, default 0`
Signed, in the target's own unit. Negative shortens a segment or slows the breath
rate; positive lengthens or speeds it. 0 means this target does not ramp.

**Ramp time unit** `{Breaths, Seconds, Minutes, Beats}, default Minutes`
One unit for the duration **and** the start delay, so they always mean the same
as each other. **Breaths** counts whole breaths -- all four segments -- at the
length *before* drift and ramp touch it, so a ramp cannot alter its own clock.
**Beats** follows the project tempo, live.

**Ramp duration** `0-1000, default 0` — per-target. How long this target takes to
arrive. 0 means it does not ramp.

**Ramp play for** `0-1000, default 0` · **Ramp rest for** `0-1000, default 0`
Per-target. Turns the smooth ride into a **staircase**: advance for `play`, hold
for `rest`, repeat. Both zero is the smooth ramp. The holds come *out of* the
duration rather than extending it, so `Ramp duration` goes on meaning "you arrive
in about this long".

**Ramp engage** `{Off, On}, default Off` — global. One switch arms every
configured target, each riding its own duration after its own start delay. It is
a freeze/resume gate, not a reset: only transport play restarts a ramp.

**Ramp start delay** `0-1000, default 0` — per-target, in ramp time units. Wait
this long after engage before *this* target starts moving, so targets can be
staggered. Useful for "fall asleep first, then begin the wind-down."

**Filter timbre is unchanged by a segment ramp.** It adjusts lengths, not filter
coefficients — a longer inhale sounds like a normal inhale, stretched.

### Drift

An endless gentle wander, rather than a journey with a destination.

**Drift target** `seven targets, default Breath rate`

**Drift up amount (units match target)** `0-1000, default 0`
How far above baseline the wander reaches at its peak.

**Drift down amount (units match target)** `0-1000, default 0`
How far below. Independent of up, so asymmetric wander is supported — biological
signals do not drift symmetrically. Either one above zero turns drift on for that
target; both zero is off.

**Drift period** `0-1000, default 8, 0 = off`
One full wave, counted in the unit below.

**Drift period unit** `{Breaths, Seconds, Beats}, default Breaths`
For a target set to `With the target`, `Breaths` counts **turns of that target** —
eight inhales, not eight of anything else. It is called `Breaths` rather than the
suite's usual `Cycles` because here the thing that repeats is a whole breath, and the
plugin already counts in breaths on `Play for` and `Rest for`. **Seconds** is wall
clock and **Beats** follows the project tempo.

**`With the target` in Seconds or Beats (2026-09-10).** The first unit counts turns. In Seconds or Beats the drift's clock runs in that unit only while the target's own thing is happening — an inhale during inhales, a pause during that pause, the breath rate through the whole breath — and freezes in between, picking up where it stopped at the next turn. Rozaya: *"stop mid-cycle, freeze the clock mid-whatever unit, then pick up on the next cycle from wherever the clock was last."* Until then those two units were silently ignored for such a target. So eight Seconds on an inhale is eight seconds of actual inhaling.

**Drift movement** `{With the target, On a clock}` *(new 2026-09-09)*
Whether this target's drift moves in step with its own thing, or runs continuously
underneath it. `With the target` advances the drift exactly one step each time that
target happens — an inhale's drift moves on each inhale — so it is deterministic,
independent of every other target, and unaffected by the breath length changing
underneath it. `On a clock` advances it continuously, drawing the whole curve,
which is what anything applied continuously wants.

Per target, like everything else in the block. **Defaults are what the plugin did
before this control existed**: the breath rate and the four segments arrive on
`With the target`, the two pitch targets on `On a clock`. Nothing you have saved
changed. Both are ordinary artistic choices and neither is the plugin's to make.

**Drift shape** `{Sine, Triangle, Random}, default Sine`
Sine is smooth, Triangle is linear ramps with turnarounds, Random interpolates
smoothly between fresh random targets at each period boundary.

**Drift play for** `0-1000, default 0` · **Drift rest for** `0-1000, default 0`
Makes the drift come and go. It drifts for `play` periods, **freezes exactly
where it stopped** for `rest` periods, then carries on. Both must be above zero
or the gate is off, which is what `0` means.

Freezing in place rather than returning to centre is the interesting part: **the
fraction of the play value chooses where it parks.** `x.25` parks at the crest,
`x.75` at the trough, `x.0` and `x.5` at no change at all. So a whole number
parks at neutral every time and is nearly inaudible, while an awkward fraction is
the one worth using — `1.75` cycles through four park points before repeating,
`1.2` through five. Setting only `Drift down` wastes half of them, because every
park on the positive half lands at no change.

**Transport:** stop silences; play re-initialises everything and starts fresh from
an inhale. Both blocks reset only on a transport play edge — never on a slider
move.

---

### Output

**Output (dB)** `-60 to +12, default 0`
Overall level. Added 2026-09-08 -- the plugin previously had no output control of
any kind, so the only way to set its level was on the track.

---

## Usage Notes

- **The breath cycle is not tempo-synced.** Duration values are in absolute seconds. The cycle length is the sum of all four phase durations.
- **Pause phases are true silence.** No signal is passed, processed, or leaked during top and bottom pauses.
- **Filter state persists through pauses.** The filter is only active during inhale and exhale phases, so state doesn't accumulate during silence — but it also isn't reset between cycles, which allows for a smooth continuation rather than a click at the start of each new phase.
- **L and R are independently filtered with independent noise.** This means the stereo image is genuinely decorrelated at the source, not a mono signal that has been panned or delayed. Summing to mono will produce a slightly different sound than either channel alone.

---

*Breath Generator is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

