# Heartbeat Generator

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Heartbeat Generator is a synthesized cardiac sound source. It produces a stereo binaural heartbeat using two resonant filter voices — a "near" and a "far" — shaped with independent attack and decay envelopes and mixed to create a sense of three-dimensional depth. The two heart sounds (S1 and S2, the "lub" and the "dub") have independently controllable pitch, volume, and decay, with a configurable systole interval between them.

Heart rate variability is modeled in two layers — a sine-wave breath modulation and a randomized low-frequency drift — giving the output an organic, living quality rather than a mechanical loop.

The plugin generates no audio from an input signal. It is a pure synthesizer and should be placed on an empty FX chain or a track with no audio source.

---

## Signal Architecture

Each heartbeat cycle produces two events: S1 and S2, separated by the systole interval. Both sounds are synthesized through the same architecture but with different parameters:

Each sound runs through two parallel resonant filter voices. The **near** voice is prominent and direct, with tighter resonance. The **far** voice uses slightly higher center frequencies, looser Q, and a slight frequency offset (S1 at ×1.003, S2 at ×0.997) to add natural detuning. Each voice's exciter blends a sine oscillator with white noise — S1 is weighted toward the oscillator (80/20), S2 toward noise (50/50), giving S2 a softer, more diffuse character.

Each voice passes through a double-cascaded lowpass after the resonant filter to smooth the output. The near and far voices are then routed to opposite output channels, with an inter-aural delay between them set by the Stereo Width parameter.

---

## Parameters

### Timing

**BPM** `20-200, default 70`
Base heart rate in beats per minute. This sets the cycle length before HRV modulation is applied. When HRV is active, the actual beat timing fluctuates around this value.

**Systole ms (S1→S2 gap)** `50-400 ms, default 120`
The delay between the S1 and S2 events within each cycle. Shorter values produce a tighter, faster lub-dub; longer values spread the sounds further apart. At very short values the sounds may overlap depending on decay settings.

---

### S1 — First Heart Sound ("Lub")

**S1 Volume** `0.0-1.0, default 1.0`
Output level for S1, applied after envelope shaping and independently of S2.

**S1 Decay ms** `10-200 ms, default 60`
How quickly S1 fades after its attack peak. Longer values produce a sustained, resonant thud; shorter values a sharper knock.

**S1 Frequency Hz** `20-120 Hz, default 45`
Base frequency of the S1 resonant filter. The near voice center is derived at ×1.1 and the far at ×1.28, so this value is the lower anchor of the frequency cluster. Lower values produce a deeper, more subsonic thump.

---

### S2 — Second Heart Sound ("Dub")

**S2 Volume** `0.0-1.0, default 0.7`
Output level for S2, independently of S1. S2 is typically quieter than S1 physiologically; the default reflects this.

**S2 Decay ms** `5-100 ms, default 25`
How quickly S2 fades. S2 is naturally shorter-lived than S1. Values under 10 ms produce a sharp click; 20-40 ms gives a natural dub character.

**S2 Frequency Hz** `60-300 Hz, default 80`
Base frequency for the S2 resonant filter. The near voice center is derived at ×1.15 and far at ×1.25.

---

### Tone

**Brightness** `0.0-1.0, default 0.3`
Controls the cutoff of the post-resonator lowpass applied to both voices. At 0.0 the filter sits around 200 Hz (near) / 175 Hz (far), keeping the sound very deep and muffled. At 1.0 it opens to approximately 450 Hz (near) / 395 Hz (far). Affects overall tonal character without changing the fundamental resonant frequencies.

---

### Stereo / Binaural

**Stereo Width ms (neg = heart right)** `-15.0–+15.0 ms, default 3.0`
The inter-aural delay between the near and far voices, creating a sense of spatial depth and positioning. Positive values place the near (prominent) voice on the left, which is anatomically correct for a heart positioned on the left side of the chest. Negative values flip this. Larger magnitudes create a stronger binaural effect. Crossing zero resets all filter states and clears the delay buffer to prevent artifacts.

---

### Heart Rate Variability

Both HRV systems modulate the cycle length in real time and operate additively.

**Breath Cycle Seconds** `1.0-30.0 sec, default 12.0`
The period of a sinusoidal breath modulation applied to heart rate, mimicking respiratory sinus arrhythmia — the natural tendency for heart rate to rise during inhale and fall during exhale. The modulation depth is set by Breath HRV Depth.

**Breath HRV Depth** `0.0-0.25, default 0.08`
How much the breath sine wave shifts the BPM. A value of 0.08 produces approximately ±8% variation around the base rate. At 0.25 the swing is ±25%. At 0.0 breath HRV is disabled.

**Random HRV Depth** `0.0-0.08, default 0.02`
Adds a slowly wandering random offset to heart rate on top of the breath modulation. The random target updates approximately every 5 seconds and slews toward the new value over ~3 seconds, preventing the breath modulation from feeling too regular. At 0.0 random HRV is disabled.

### Start Delay

**Start Delay (beats)** `0–1000, default 0`

Silent for N heartbeats after playback starts, then the heartbeat begins normally. Beats are counted at the current BPM (the same slider that sets the heart rate) — at 60 BPM, "4 beats" is 4 seconds; at 120 BPM it's 2 seconds. Internal state (cycle phase, breath modulation, HRV smoothing) stays frozen during the delay so the first beat lands cleanly at delay-end rather than mid-cycle. Re-arms on every transport stop/start. 0 disables the delay.

### Play / Rest Gating (v2.1)

**Play for (beats)** `0–1000, default 0`
**Rest for (beats)** `0–1000, default 0`

A per-beat cyclic gate. Heartbeats fire normally for **Play for** beats, then no new beats trigger for **Rest for** beats' worth of time, then beats resume — the pattern repeats indefinitely. With Play for = 4 and Rest for = 4, you hear four heartbeats followed by four-beats-of-silence followed by four heartbeats, and so on.

The feature is **disabled when either slider is 0** (the default). With both at 0, the plugin behaves exactly as before — no gating, no behavior change.

**What "rest" means here.** The gate sits at the trigger level — when a new beat would fire, it's suppressed. The previous beat's S1 and S2 envelopes are still decaying through their natural release tail, so you don't hear an abrupt cutoff at the boundary; the last beat fades into the rest period naturally. Rest is "don't trigger new beats," not "instantly silence the plugin."

**Beat counting** is in heartbeats at the current BPM, same unit as Start Delay. At 60 BPM, "4 beats" is roughly 4 seconds (with some HRV jitter). Both sliders are integers — fractional beats don't make sense here.

**Transport behavior**: conventional. Stop silences; play re-initializes everything (cycle phase, period counter, resting state) and starts a fresh play period from beat 1.

### Speed Ramp

Nested-selector pattern matching Womb v3. Pick one of 4 targets (Heart BPM, S1-S2 gap, Breath HRV depth, Random HRV depth) on slider 29, then set a signed `by` amount on slider 30. All 4 targets ramp in parallel; the selector just changes which one you're editing.

*(v2.14 reorg: the Speed Ramp block is now a contiguous selector-first group at sliders **29–33** — target 29, by 30, duration 31, engage 32, start-delay 33 — so it tabs together. Old IDs 17–20 + 28 are retired; Speed Ramp configs reset on upgrade.)*

**Speed ramp target (slider 29)** `Heart BPM / S1-S2 gap / Breath HRV depth / Random HRV depth, default Heart BPM`
The 4-option selector. Switching saves the current target's `by` + duration + start delay to its memory slot and loads the new target's saved values. All 4 targets ramp regardless of which one is selected.

**Speed ramp duration (slider 31)** `0–60 minutes, default 0` — **per-target** (v2.14): how long the *selected* target takes to travel from baseline to baseline + `by`; a target with duration 0 doesn't ramp. · **Speed ramp engage (slider 32)** `Off / On, default Off` — **global**: one switch arms every configured target, each riding its own duration after its own start delay.

Engage is a freeze/resume gate (NOT a restart edge): while On, each target's clock advances 0 → 1 over its own duration; while Off, all clocks freeze and resume on re-engage. Only transport play resets the ramps.

**Speed ramp by (slider 30)** `-400 to +400, step 0.01, default 0`
Signed delta in the selected target's natural unit. **0** = no change. Examples:
- Heart BPM target, by -35: heart ramps from 70 → 35 BPM over the duration.
- S1-S2 gap target, by +50: systole stretches from 120 → 170 ms.
- Breath HRV depth target, by +0.05: breath-coupled HRV grows from baseline by 0.05.
- Random HRV depth target, by -0.01: random HRV shrinks by 0.01 toward 0.

Slider range is intentionally wide (-400 to +400) to span every target's natural range. Step is 0.01 to give fine control on the HRV targets (which have natural step 0.005-0.01). For BPM/ms targets you'd type a coarser value (e.g. -35 for BPM); for HRV targets you'd type something like 0.05.

**Speed ramp start delay (slider 33)** `0–60 minutes, default 0` — **per-target** (v2.14): wait this many minutes after engage before *this* target begins moving (stagger targets by giving them different delays). Part of the contiguous 29–33 block. Saved/loaded per target by the selector, like `by` and duration.

A small ~100 ms smoother sits between the BPM slider and the audio, so manual BPM tweaks don't click. This is always on.

**Transport behavior:** speed_ramp_t resets to 0 on every transport play edge — the ONLY thing that resets ramp progress. Slider changes (selector switch, engage toggle, anything) don't restart it.

**Migration history.** *v2.7:* the old single "Speed ramp" multiplier (0.1–4.0) on slider 17 became a target selector with a signed `by` amount (additive, not a multiplier). *v2.14:* the whole block was renumbered into the contiguous selector-first group at sliders **29–33** (old IDs 17–20 + 28 retired). Speed Ramp configs reset to defaults on upgrade — reconfigure after loading.

### Drift (v2.9 nested-selector)

Slow organic wander applied independently to any of four targets: Heart BPM, S1-S2 gap, Breath HRV depth, or Random HRV depth. Each target can have its own drift configuration; all four drift in parallel. The selector chooses which target's drift you're currently editing — the others keep running with their last-saved configuration.

Same pattern as Womb v3's drift and the Speed Ramp block above. The 4 drift targets are intentionally the same set as the 4 Speed Ramp targets and use the same selector indices, so once you've decided "I want to wind down the heart over 30 min and wander the systole gap a bit" you can configure both blocks on the same target indices.

Switching the **Drift target** selector saves the current sliders 22-25 into the old target's memory slot, then loads the new target's saved values. All four configurations persist across project save/load.

For slow wall-clock-feel drift, set a long period (~360 heartbeats ≈ 5 min at 72 BPM). The old v2.8 "musical vs slow" split is gone — there's a single period unit (heartbeats), and you express the timescale you want with the period value.

**Drift target** `Heart BPM / S1-S2 gap / Breath HRV depth / Random HRV depth, default Heart BPM`
Picks which target's drift configuration sliders 22-25 reflect. Switching the selector saves and loads automatically — no live edits are lost.

**Drift up amount** `0.0–50.0, default 0` (units match target)
How far above the target's baseline the drift wanders at its peak. Units are BPM for Heart BPM, ms for S1-S2 gap, fractional depth (0.0-0.25 range) for Breath HRV depth, fractional depth (0.0-0.08 range) for Random HRV depth. 0 = drift off on the up side.

**Drift down amount** `0.0–50.0, default 0` (units match target)
How far below the baseline the drift wanders at its trough. Independent from Up — asymmetric biological-feel wander supported. Either non-zero activates drift for the target; both 0 = drift off.

**Drift period (heartbeats)** `1–1000, default 8`
How many heartbeats one full drift wave takes for this target. Short = jittery, long = barely-perceptible wander. Period unit is the same across all 4 targets because heartbeat rate is the kin's master clock.

**Drift shape** `Sine / Triangle / Random, default Sine`
Wander waveform. Sine = smooth, Triangle = linear ramps with turnarounds, Random = value-noise interpolating smoothly between fresh random targets at each period boundary.

#### Transport behavior (v2.9)

On every transport play press, drift cycle restarts: all 4 targets' phase counters → 0 (drift offset = 0 at the first sample, wanders out from there). Drift CONFIG (up/down/per/shape values per target) is preserved across stop/play and across project save/load. Speed Ramp progress also resets on transport play. This makes renders deterministic for Sine and Triangle shapes (Random remains non-deterministic per render by design).

#### Migration from v2.8

The old flat-drift block (musical_up/down/period, slow_up/down/period, drift_shape on sliders 21-27) was 7 sliders covering Heart BPM only. v2.9 is 5 sliders covering 4 independent targets, reusing slider IDs 21-25; sliders 26 and 27 are no longer declared. Old project values get reinterpreted (selector defaults to Heart BPM; non-zero amounts on sliders 22-23 will produce drift on the Heart BPM target). After upgrade, reset drift sliders to defaults if you'd never configured the old flat drift, or reconfigure under the new nested-selector pattern if you had.

---

## Usage Notes

- **Near and far voices are always both active.** The stereo output is the near voice on one channel and the delayed far voice on the other. There is no mono sum option — summing to mono will produce some comb filtering.
- **BPM is a base rate, not a locked tempo.** When HRV is active the beat timing will not align to a DAW grid. For grid-locked output, set both HRV depth parameters to 0.
- **S1 and S2 can overlap** if Systole ms is very short relative to S1 Decay ms. This produces a compressed, tachycardic character.
- **Crossing zero on Stereo Width** resets all filter states and clears the delay buffer. There will be a brief silence on the transition.

---

*Heartbeat Generator is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---


### Host tempo sync

**Rate Mode** `Own BPM / Host x` (default Own BPM)
**Own BPM** is the original behaviour — free-running, project tempo ignored.
**Host x** makes BPM a **multiplier of the project tempo** instead: x1 follows
it exactly, x2 is double speed, x0.5 half. Tempo changes apply live.

Only two entries rather than the four in Melody Phase / Polyrhythm, because
this plugin only ever had one unit — "Seconds" and "Hz" would be meaningless.

> **Switching modes changes what BPM means, and nothing rescales it.** Set the
> mode first, then the value — or use the picker below, which fills it in.

**Host ratio (writes BPM)** `Custom / every 8 beats / … / 8 per beat` (default Custom)
Shown only in Host x. Writes the multiplier and then gets out of the way, so you
can still type or automate anything. **Custom** never writes anything, and is
deliberately not called "Free" — in sync UI that means free-running, which Own
BPM already is. Entries are named for what you hear, not as note values.
