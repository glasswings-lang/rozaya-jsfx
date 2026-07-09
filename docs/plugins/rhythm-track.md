# Rhythm Track

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Rhythm Track is a synthesized metronome with configurable tone, swing, and stereo pan distribution. It produces a continuous click track with a distinct strong beat on the downbeat and weak beats on all remaining beats in the bar. Both the strong and weak ticks are synthesized using filtered noise with exponential decay, giving them a pitched percussive quality rather than a raw click. Pan mode options distribute the beats across the stereo field in various patterns, from simple alternation to converging and diverging sequences.

The plugin generates no audio from an input signal. It is a pure synthesizer and should be placed on an empty FX chain or a track with no audio source.

---

## Signal Architecture

Each tick is pre-rendered into a buffer whenever a relevant parameter changes. The rendering process passes a short burst of noise through a resonant bandpass filter (a lowpass followed by a four-stage cascaded highpass) tuned to the tick's frequency, with a short linear attack and an exponential decay. The rendered buffer is then peak-normalized to the configured gain level.

At playback time the plugin advances a beat phase counter. When the phase crosses a cycle boundary, the appropriate tick buffer is triggered and plays back sample-by-sample, panned to the position calculated for that beat index. Only one tick plays at a time — if a new beat fires before the previous tick has finished, the previous tick is cut off.

Swing is applied by offsetting the beat phase at each cycle boundary, advancing or retarding even-numbered beats relative to odd-numbered ones.

---

## Parameters

### Timing

**Tempo (BPM)** `10-300 BPM, default 120`
The tempo of the beat track in beats per minute. Range matches Shepard Scale's BPM slider for consistency across the suite's BPM-style rate controls. Internal floors clamp at 10 BPM at every consumption site so a heavy Drift down or Speed Ramp delta can't drive tempo below the slider's stated minimum.

**Beats per bar** `1-20, default 4`
The number of beats in each bar. Beat index 0 is the strong (accented) beat; all others are weak beats. With a value of 1, every beat is a strong beat.

**Swing amount** `-1.0–+1.0, default 0`
Applies a swing feel to the beat by offsetting the timing of alternating beats. Positive values push even-numbered beats later (forward swing — the common jazz feel). Negative values push them earlier (reverse swing). The offset is applied as a fraction of one third of the beat duration, consistent with triplet-based swing. At 0 the rhythm is straight.

---

### Tone

Both the strong and weak beats use the same filter architecture, with independent frequency, gain, and decay settings.

**Strong beat frequency (Hz)** `20-2000 Hz, default 880`
The center frequency of the strong beat tick. The resonant bandpass is tuned to this value, giving the tick its pitched character. Higher values produce a brighter, more cutting click; lower values produce a deeper, more thuddy accent.

**Weak beat frequency (Hz)** `20-2000 Hz, default 440`
The center frequency of the weak beat tick. Typically set lower than the strong beat to create a clear hierarchy between accented and unaccented beats.

**Tone resonance (Q)** `0.5-8.0, default 1.5`
The Q of the resonant bandpass filter applied to both ticks. Higher values produce a more pitched, ringing quality with a narrower frequency peak. Lower values produce a broader, more noise-like sound. Both ticks share the same Q value.

**Strong beat volume** `0.0-1.0, default 0.75`
Peak output level of the strong beat tick after normalization.

**Weak beat volume** `0.0-1.0, default 0.5`
Peak output level of the weak beat tick after normalization.

**Strong beat decay (seconds)** `0.001-1.0 sec, default 0.04`
How long the strong beat tick rings before fading to silence. Longer values produce a more sustained, resonant tone; shorter values a sharper transient.

**Weak beat decay (seconds)** `0.001-1.0 sec, default 0.02`
How long the weak beat tick rings. Typically set shorter than the strong beat.

> **Note:** Tick sounds are pre-rendered into buffers whenever any parameter changes, not recalculated per-sample. Changes take effect immediately on the next beat trigger.

---

### Pan

**Pan spread (0=mono, 1=full L/R)** `0.0-1.0, default 1.0`
Scales the width of all pan positions. At 1.0 pan modes reach hard left and right. At 0.0 all modes produce center regardless of Pan mode selection.

**Pan mode** `Mono / Accent L / Weak R / Alternating / Distributed / Converging / Diverging`
Controls how beats are distributed across the stereo field. Positions are calculated per beat index within the bar, not per cycle.

- **Mono** — all beats play centered.
- **Accent L / Weak R** — the strong beat (index 0) plays hard left; all weak beats play hard right.
- **Alternating** — beats alternate hard left / hard right on each successive beat, starting with left on the strong beat.
- **Distributed** — beats are evenly spaced from hard left to hard right across the full bar. With 4 beats per bar: beat 0 hard left, beat 1 slightly left of center, beat 2 slightly right of center, beat 3 hard right.
- **Converging** — beat 0 starts hard left, then each successive pair of beats approaches center from opposite sides, converging inward across the bar.
- **Diverging** — beat 0 starts center, then each successive pair of beats moves outward symmetrically toward the extremes.

**Pan direction** `Normal / Flipped`
Inverts all pan positions. In Normal mode beat 0 anchors to the left in directional modes; in Flipped mode it anchors to the right. Applies as a global sign flip to all pan calculations.

### Start Delay

**Start Delay (beats)** `0–1000, default 0`

How long the metronome sits silent at the start of playback before ticks begin. Counted in beats at the current Tempo (so at 120 BPM, "4 beats" = 2 seconds). 0 disables the delay entirely.

During the delay the beat phase stays frozen, so when the delay elapses the metronome begins cleanly from the downbeat. Re-arms on every transport stop/start.

### Play / Rest Gating (v2.1)

**Play for (beats)** `0–1000, default 0`
**Rest for (beats)** `0–1000, default 0`

A per-beat cyclic gate. The metronome plays for **Play for** beats, sits silent for **Rest for** beats, then resumes — the pattern repeats forever. Useful as a practice tool: "play 4 beats, then 4 beats of silence to internalize the pulse, then 4 more beats."

The feature is **disabled when either slider is 0** (the default). With both at 0, the metronome behaves as before.

**Tick tails finish naturally.** The gate suppresses new tick triggers — it doesn't cut off any tick that's already playing. So if the last beat of a play period was a strong beat with a long decay, its decay tail continues into the rest period.

**The bar grid keeps marching during rest.** Beat index (which determines accent placement, pan position, and which beat is the "strong" one) advances on every potential beat, even silent ones. This keeps the accent locked to "every Beats per bar beats" regardless of where the rest periods fall. With `Play for = 3` and `Beats per bar = 4`, the strong beat (beat 0 of the bar) walks through different positions in successive play periods — period 1 starts with a strong beat, period 2 starts mid-bar, etc. If you want the accent to always land on the first beat of every play period, set `Play for` to a multiple of `Beats per bar`.

**Swing still works.** Swing offsets are applied based on beat index, which advances during rest. So when rest ends and play resumes, the swing alignment is exactly where it would have been if the rest hadn't happened.

**Transport behavior**: conventional. Stop silences; play re-initializes everything (beat phase back to 1.0 for the immediate downbeat, period counter, rest state) and starts fresh from beat 1.

### Speed Ramp (v2.14 nested-selector)

In-plugin one-time morph over time, without automation envelopes. As of v2.14 Speed Ramp is nested-selector (same shape as Drift) and reaches **both** targets — Tempo BPM and Swing amount — matching Drift's target set. Both targets ramp in parallel; the selector only chooses which one the `by` slider is currently editing.

**Speed ramp target (slider 17)** `Tempo BPM / Swing amount, default Tempo BPM`
Picks which target the `by` amount applies to. Switching the selector saves slider 18 into the old target's memory slot, then loads the new target's stored `by`. This selector sits at the top of the Speed Ramp block (above the controls it governs) — a v2.14 reorganization; see the migration note below.

**Speed ramp by (slider 18)** `-300 to +300, step 0.1, default 0` (units match the selected target)
Signed delta in the selected target's own unit. **0** = no change (safe default — engaging at 0 produces no effect).
- **Target = Tempo BPM:** the delta is in BPM. `-60` ramps Tempo from 120 → 60 over the duration; positive speeds up. (The wide ±300 range is here for BPM.)
- **Target = Swing amount:** the delta is in the same **swing fraction** as the Swing amount slider (−1…+1, where 0 = straight and ±1 = full triplet shuffle). So a `by` of `+0.8` gradually swings the groove from wherever it starts toward heavily swung; `-0.5` gradually straightens it. Only roughly ±2 of the slider's range is meaningful for this target (swing is clamped to ±1 at the consumer); the rest of the range is just headroom shared with the BPM target.

**Speed ramp duration (slider 19)** `0–60 minutes, default 0` — **per-target** (as of v2.14): how long the *selected* target takes to travel from baseline to baseline + `by`. Each target has its own; a target with duration 0 doesn't ramp. · **Speed ramp start delay (slider 21)** `0–60 minutes, default 0` — **per-target**: wait this many minutes after engage before *this* target begins moving. · **Speed ramp engage (slider 20)** `Off / On, default Off` — **global**: one switch arms both targets, each then riding its own duration after its own delay. (Duration and start delay are saved/loaded per target by the selector, exactly like `by`.)

Engage is a freeze/resume gate (NOT a restart edge): while On, each target's clock advances 0 → 1 over its duration; while Off, all clocks freeze and resume on re-engage.

**Transport behavior:** every target's ramp clock resets to 0 on the transport play edge. This is the ONLY thing that resets the ramps — slider changes (engage toggle, selector switch, anything) don't restart them. The accent grid, swing, and drift wave all follow the effective values automatically.

**Migration to v2.14 (reorganization + renumber):** Speed Ramp went multi-target and the block was reorganized so the target selector reads *above* the by/duration/engage controls it governs. Because REAPER orders sliders by ID (not file position), this required renumbering the Speed Ramp block (now sliders 17–21) and the Drift block (now sliders 22–26). **Existing Rhythm Track projects lose their Speed Ramp and Drift settings on upgrade** — both are off-by-default, and the metronome sound itself (sliders 1–16: tempo, swing, tone, pan, start delay, play/rest) is untouched. Re-add the plugin instance for clean defaults, or re-enter your Speed Ramp / Drift settings. *(Older history: pre-v2.14 Speed Ramp was single-target Tempo BPM on slider 17; and pre-v2.8 it was a multiplier 0.1–4.0.)*

### Drift (v2.9 nested-selector)

Slow organic wander applied independently to Tempo BPM or Swing amount. Each target can have its own drift configuration; both drift in parallel. The selector chooses which target's drift you're currently editing — the other keeps running with its last-saved configuration.

Same pattern as Womb v3's drift and the matching block in Heartbeat / Breath Generator. Switching the **Drift target** selector saves the current sliders 23-26 into the old target's memory slot, then loads the new target's saved values. Both configurations persist across project save/load.

For slow wall-clock-feel drift, set a long period (~960 beats ≈ 8 min at 120 BPM). The old v2.8 "musical vs slow" split is gone — there's a single period unit (beats), and you express the timescale you want with the period value.

Note: as of v2.14 both Drift and Speed Ramp reach the same 2 targets (Tempo BPM, Swing amount). Wandering (or ramping) Swing while the tempo stays put is a useful musical effect on its own — it loosens the groove cycle-to-cycle without changing the beat clock.

**Drift target (slider 22)** `Tempo BPM / Swing amount, default Tempo BPM`
Picks which target's drift configuration sliders 23-26 reflect. Switching the selector saves and loads automatically — no live edits are lost.

**Drift up amount (slider 23)** `0.0–50.0, default 0` (units match target)
How far above the target's baseline the drift wanders at its peak. Units are **BPM** for Tempo BPM, and **swing fraction** (the same −1…+1 unit as the Swing amount slider, clamped to ±1.0 at the consumer) for Swing amount. 0 = drift off on the up side.

**Drift down amount (slider 24)** `0.0–50.0, default 0` (units match target)
How far below the baseline the drift wanders at its trough. Independent from Up — asymmetric wander supported. Either non-zero activates drift for the target; both 0 = drift off.

**Drift period (slider 25, beats)** `1–1000, default 8`
How many beats one full drift wave takes for this target. Short = jittery, long = barely-perceptible wander. Period scales with Speed Ramp's tempo offset so the wave-per-beat relationship stays constant under wind-down.

**Drift shape (slider 26)** `Sine / Triangle / Random, default Sine`
Wander waveform. Sine = smooth, Triangle = linear ramps with turnarounds, Random = value-noise interpolating smoothly between fresh random targets at each period boundary.

#### Transport behavior (v2.9)

On every transport play press, drift cycle restarts: both targets' phase counters → 0 (drift offset = 0 at the first sample, wanders out from there). Beat clock also resets so the downbeat fires immediately on the first sample after Start Delay. Drift CONFIG (up/down/per/shape values per target) is preserved across stop/play and across project save/load.

#### Migration from v2.8

The old flat-drift block (musical_up/down/period, slow_up/down/period, drift_shape on sliders 21-27) was 7 sliders covering Tempo only. v2.9 is 5 sliders covering 2 independent targets, reusing slider IDs 21-25; sliders 26 and 27 are no longer declared. Old project values get reinterpreted (selector defaults to Tempo BPM; non-zero amounts on sliders 22-23 will produce drift on Tempo). After upgrade, reset drift sliders to defaults if you'd never configured the old flat drift, or reconfigure under the new nested-selector pattern if you had.

---

## Usage Notes

- **Only one tick plays at a time.** If a beat fires before the previous tick finishes decaying, the previous tick is cut off immediately. At fast tempos with long decay settings, ticks will be truncated — reduce decay times accordingly.
- **All tick parameters trigger a re-render.** Moving any slider recalculates the full tick buffer for both strong and weak beats. This is instantaneous but means the sound updates on the next beat rather than mid-tick.
- **Swing is triplet-based.** The maximum swing offset is one third of a beat duration. At ±1.0 the affected beats are shifted by a full triplet subdivision.
- **Pan positions are fixed per beat index within the bar.** Changing Beats per bar will recalculate all pan positions. Pan spread scales all positions uniformly.

---

*Rhythm Track is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*






---

