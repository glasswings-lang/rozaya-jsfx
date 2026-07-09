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

### Timing

**Inhale Duration (sec)** `0.5-20.0 sec, default 4.0`
Length of the inhale phase. The breath cycle advances through inhale → top pause → exhale → bottom pause in sequence, then loops. Changing this value mid-cycle takes effect at the next state transition; if the new duration is shorter than the current position, the position is immediately clamped to the end of the state.

**Top Pause (sec)** `0.0-5.0 sec, default 0.3`
Silence between the end of inhale and the start of exhale. Simulates the natural breath hold at the top of a breath. Set to 0 for an immediate inhale-to-exhale transition.

**Exhale Duration (sec)** `0.5-20.0 sec, default 4.0`
Length of the exhale phase.

**Bottom Pause (sec)** `0.0-5.0 sec, default 0.3`
Silence between the end of exhale and the start of the next inhale. Simulates the natural rest at the bottom of a breath. Set to 0 for an immediate exhale-to-inhale transition.

---

### Tone

**Inhale Frequency Hz** `50-2000 Hz, default 800`
Cutoff frequency of the lowpass filter applied during the inhale phase. Broadband noise content passes through from below; rolloff above the cutoff with a slight resonant peak at cutoff. Inhale defaults sit higher than exhale to match the sharper-turbulence character of inflow (air entering through the nose/mouth has higher-frequency hiss content than the cavity-colored exhale). Lower values produce a deeper, body-heavy rush; higher values add more upper-frequency hiss. Note: due to sinusoidal frequency-to-coefficient mapping, the effective cutoff tracks lower than the displayed value at higher settings, increasingly so above ~1500 Hz.

**Exhale Frequency Hz** `50-2000 Hz, default 600`
Cutoff frequency of the lowpass filter applied during the exhale phase. Typically set lower than inhale for the cavity-colored character of exhalation. The same frequency mapping caveat applies.

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

**Start Delay (seconds)** `0–1000, default 0`

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

### Speed Ramp

Nested-selector pattern matching Womb v3. Pick a target — Inhale, Top pause, Exhale, Bottom pause, or Breaths/min — and set a signed `by` amount (seconds for the four segments, breaths/min for the aggregate); that target ramps from its baseline toward `baseline + by` over the duration. All five targets ramp in parallel; the selector just changes which target's `by` you're currently editing.

*(v2.14 reorg: the Speed Ramp block is now a contiguous selector-first group at sliders **30–34** — target 30, by 31, duration 32, engage 33, start-delay 34. Old IDs 17–20 + 29 are retired; Speed Ramp configs reset on upgrade.)*

**Speed ramp target (slider 30)** `Inhale / Top pause / Exhale / Bottom pause / Breaths/min, default Inhale`
The 5-option selector (v2.14 adds **Breaths/min**). Switching saves the current target's `by` + duration + start delay to its memory slot and loads the new target's saved values. All 5 targets ramp regardless of which one is selected — selector switching never stops a ramp. The **Breaths/min** target is a proportional scale across all four segments in lockstep (preserving the I:E ratio), in breaths per minute — the whole-breath-rate wind-down, distinct from the per-segment targets it composes with. Its `by` is read as breaths/min rather than seconds (negative = slower breath).

**Speed ramp duration (slider 32)** `0–60 minutes, default 0` — **per-target** (v2.14): how long the *selected* target takes to travel from baseline to baseline + `by`. Each target has its own; a target with duration 0 doesn't ramp.

**Speed ramp engage (slider 33)** `Off / On, default Off` — **global**: one switch arms every configured target, each riding its own duration after its own start delay. Freeze/resume gate — while On each target's clock advances; while Off all freeze and resume on re-engage. Engage does NOT reset the ramps — only transport play does.

**Speed ramp by (slider 31)** `-20 to +20 sec, step 0.1, default 0`
Signed delta in seconds for the selected target. **0** = no change. **Negative** = shorten that segment (faster breath if Inhale/Exhale; tighter cycle if Top/Bottom). **Positive** = lengthen (slower / more spacious). Examples: Inhale target with `by` +4 ramps inhale from 4 sec → 8 sec over the duration; Bottom Pause target with `by` -0.2 shortens bottom pause toward minimum. Each target stores its own amount independently.

**Speed ramp start delay (slider 34)** `0–60 minutes, default 0` — **per-target** (v2.14): wait this many minutes after engage before *this* target begins moving (stagger targets by giving them different delays). Part of the contiguous 30–34 block. Useful for "fall asleep first, then begin the wind-down."

**Migration history.** *v2.7:* the old single "Speed ramp" multiplier (0.1–4.0) became a target selector, and the audio path changed to per-segment length adjustments (additive) — so Speed Ramp composes additively with Drift instead of multiplicatively. *v2.14:* the block was renumbered into the contiguous selector-first group at sliders **30–34** (old IDs 17–20 + 29 retired), and the **Breaths/min** aggregate target was added. Speed Ramp configs reset to defaults on upgrade — reconfigure after loading.

**Filter timbre is unchanged.** Speed Ramp adjusts segment lengths, not filter coefficients — a longer inhale sounds exactly like a normal inhale, just stretched.

**Transport behavior:** speed_ramp_t resets to 0 on every transport play edge. This is the ONLY thing that resets the ramp — slider changes (selector switch, engage toggle, anything) don't restart it.

### Drift (v2.9 nested-selector)

Slow organic wander applied independently to each of the four breath segment durations. Each segment can have its own drift configuration; all four drift in parallel. The selector chooses which segment's drift you're currently editing — the others keep running with their last-saved configuration.

Same pattern as Womb v3's drift and Speed Ramp. Switching the **Drift target** selector saves the current sliders 22-25 into the old target's memory slot, then loads the new target's saved values. All four configurations persist across project save/load.

For slow wall-clock-feel drift, set a long period (~100 cycles ≈ 7-10 min at typical breath rates). The old v2.8 "musical vs slow" split is gone — there's a single period unit (breath cycles), and you express the timescale you want with the period value.

**Drift target** `Inhale / Top pause / Exhale / Bottom pause / Breaths/min, default Inhale`
Picks which target's drift configuration sliders 22-25 reflect. Switching the selector saves and loads automatically — no live edits are lost. The **Breaths/min** target (v2.14) wanders the whole breath rate (all four segments in lockstep, I:E preserved) in breaths/min, rather than one segment in seconds.

**Drift up amount (seconds)** `0.0–10.0, default 0`
How many seconds above the baseline segment length the drift wanders at its peak. 0 = drift off on the up side.

**Drift down amount (seconds)** `0.0–10.0, default 0`
How many seconds below the baseline segment length the drift wanders at its trough. Independent from Up amount, so asymmetric wander is supported (biological signals don't drift symmetrically). Either being non-zero activates drift for the target; both 0 = drift off.

**Drift period (breath cycles)** `1–1000, default 8`
How many breath cycles one full drift wave takes for this target. 8 cycles = wander completes one Sine/Triangle period (or one random-target interpolation) every 8 breaths. Short = jittery, long = barely-perceptible wander.

**Drift shape** `Sine / Triangle / Random, default Sine`
Wander waveform. Sine = smooth, Triangle = linear ramps with turnarounds, Random = value-noise interpolating smoothly between fresh random targets at each period boundary.

#### Migration from v2.8

The old flat-drift block (musical_up, musical_down, musical_period, slow_up, slow_down, slow_period, drift_shape on sliders 21-27) was 7 sliders covering the whole-breath-cycle period. v2.9 is 5 sliders covering 4 independent targets, reusing slider IDs 21-25; sliders 26 and 27 are no longer declared. Old project values get reinterpreted:

- old slider21 (musical_up, default 0) → new Drift target (selector, defaults to Inhale)
- old slider22 (musical_down, default 0) → new Drift up amount (defaults 0)
- old slider23 (musical_period, default 8) → new Drift down amount — interpreted as 8 sec, which will produce strong drift on the Inhale segment
- old sliders 24–27 → silently discarded or reinterpreted

After upgrade, reset drift sliders to defaults if you'd never configured the old flat drift, or reconfigure under the new nested-selector pattern if you had. The old v2.7 → v2.8 Speed Ramp migration set the precedent of accepting drift / ramp values being reset on upgrade.

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

