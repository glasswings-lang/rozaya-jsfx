# Rozaya JSFX Plugin Suite
## User Manual

*Designed by Rozaya — Developed with Claude (Anthropic)*

---

## Table of Contents

- [Acknowledgements](#acknowledgements)

**Synthesizers**
- [Heartbeat Generator](#heartbeat-generator)
- [Breath Generator](#breath-generator)
- [Womb Sound Generator](#womb-sound-generator)
- [Womb Sound Generator v2](#womb-sound-generator-v2)
- [Womb Sound Generator v3](#womb-sound-generator-v3)
- [Polyrhythm Phase](#polyrhythm-phase)
- [Melody Phase](#melody-phase)

**Universal Features**
- [Per-Plugin Drift](#per-plugin-drift)

**Effects**
- [Resonant Sweeping Filter](#full-feature-sweeping-filter)
- [Sweep Dwell Filter](#sweep-dwell-filter)
- [Full Feature Tremolo](#full-feature-tremolo)
- [Resonance Bank](#resonance-bank)

**Utilities**
- [Rhythm Track](#rhythm-track)
- [Shepard Scale Generator](#shepard-scale-generator)
- [Shepard Tone Generator](#shepard-tone-generator)

---

# Acknowledgements

## Authorship

All plugins in this suite were designed by Rozaya. Code was written by Claude (Anthropic) under Rozaya's direction. Rozaya determined the concept, feature set, signal architecture, parameter design, and all creative and functional decisions for each plugin. Claude implemented those decisions in JSFX.

## Inspirations and Prior Art

Several plugins in this suite were developed with reference to existing implementations in common DAW tools. In all cases, the code was written independently — no source code was copied or derived from any external implementation. The conceptual influence is acknowledged here:

- **Rhythm Track** — rhythmic metronome generation concepts drawn from existing DAW metronome implementations.
- **Resonant Sweeping Filter** and **Sweep Dwell Filter** — filter sweep concepts informed by resonant lowpass filter implementations found in standard DAW effect libraries.
- **Full Feature Tremolo** — tremolo concepts informed by existing DAW tremolo implementations, substantially expanded with shaped envelopes, stereo phase control, and pan modulation.

The **Heartbeat Generator**, **Womb Sound Generator**, **Breath Generator**, **Polyrhythm Phase**, **Shepard Tone Generator**, and **Shepard Scale Generator** plugins are original concepts with no direct external inspiration for their architecture or feature sets.

## Technical Notes

The Cockos state-variable resonant lowpass filter topology used in several plugins is a well-known open implementation documented in the REAPER JSFX ecosystem. Its use here follows standard practice for the platform.


---

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

Nested-selector pattern matching Womb v3. Pick one of 4 targets (Heart BPM, S1-S2 gap, Breath HRV depth, Random HRV depth) on slider 17, then set a signed `by` amount on slider 20. All 4 targets ramp in parallel; the selector just changes which one you're editing.

**Speed ramp target (slider 17)** `Heart BPM / S1-S2 gap / Breath HRV depth / Random HRV depth, default Heart BPM`
The 4-option selector. Switching saves the current slider 20 amount to the old target's memory slot and loads the new target's saved amount. All 4 targets ramp regardless of which one is selected.

**Speed ramp duration (slider 18)** `0–60 minutes, default 0` · **Speed ramp engage (slider 19)** `Off / On, default Off`

Engage is a freeze/resume gate (NOT a restart edge): while On, ramp_t advances 0 → 1 over the duration; while Off, ramp_t freezes wherever it is and resumes from there on re-engage. Only transport play resets the ramp.

**Speed ramp by (slider 20)** `-400 to +400, step 0.01, default 0`
Signed delta in the selected target's natural unit. **0** = no change. Examples:
- Heart BPM target, by -35: heart ramps from 70 → 35 BPM over the duration.
- S1-S2 gap target, by +50: systole stretches from 120 → 170 ms.
- Breath HRV depth target, by +0.05: breath-coupled HRV grows from baseline by 0.05.
- Random HRV depth target, by -0.01: random HRV shrinks by 0.01 toward 0.

Slider range is intentionally wide (-400 to +400) to span every target's natural range. Step is 0.01 to give fine control on the HRV targets (which have natural step 0.005-0.01). For BPM/ms targets you'd type a coarser value (e.g. -35 for BPM); for HRV targets you'd type something like 0.05.

**Speed ramp start delay (slider 28)** `0–60 minutes, default 0`
Wait this many minutes after engage before ramp_t starts advancing. Lives at slider 28 (after the drift block) because the gap at slider 20 went to the new `by` slider.

A small ~100 ms smoother sits between the BPM slider and the audio, so manual BPM tweaks don't click. This is always on.

**Transport behavior:** speed_ramp_t resets to 0 on every transport play edge — the ONLY thing that resets ramp progress. Slider changes (selector switch, engage toggle, anything) don't restart it.

**Migration from v2.7:** slider 17 changed from multiplier (0.1–4.0) to a 4-option selector. Existing projects' multiplier value rounds down to a target index, and slider 20 (the new amount) defaults to 0 — so Speed Ramp produces no effect on reload until reconfigured.

### Drift

Slow organic wander applied to BPM on top of Speed Ramp. The heartbeat speeds up and slows down a little instead of locking to one fixed rate. See [Per-Plugin Drift](#per-plugin-drift) for the architecture; the seven sliders below configure it for this plugin.

**Musical Period (heartbeats)** `1–256, default 32`
Period of the musical drift source, measured in heartbeats of the kin's own cycle. Scales with Speed Ramp — if the heartbeat slows down, this period stretches with it.

**Musical Up by** `0.0–1.0, default 0`
How far above the center BPM the musical drift wanders at its peak, as a multiplier amplitude. 0.1 = up to +10% above the slider BPM.

**Musical Down by** `0.0–1.0, default 0`
How far below the center BPM the musical drift wanders at its trough. Independent from Up by — asymmetric drift wanders further one direction than the other.

**Slow Period (minutes)** `0.1–60, default 5`
Period of the slow drift source, measured in wall-clock minutes. Does NOT scale with Speed Ramp.

**Slow Up by** `0.0–1.0, default 0`
Above-center amplitude for the slow drift source.

**Slow Down by** `0.0–1.0, default 0`
Below-center amplitude for the slow drift source.

**Shape** `Sine / Triangle / Random, default Sine`
Wander shape applied to both sources. Sine is smoothest; Triangle has a defined peak corner; Random wanders smoothly between random targets.

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

**Top Pause (sec)** `0.0-5.0 sec, default 0.5`
Silence between the end of inhale and the start of exhale. Simulates the natural breath hold at the top of a breath. Set to 0 for an immediate inhale-to-exhale transition.

**Exhale Duration (sec)** `0.5-20.0 sec, default 4.0`
Length of the exhale phase.

**Bottom Pause (sec)** `0.0-5.0 sec, default 1.5`
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

Nested-selector pattern matching Womb v3. Pick a target — Inhale, Top pause, Exhale, or Bottom pause — and set a signed `by` amount in seconds; that segment's length ramps from its baseline toward `baseline + by` over the duration. All four targets ramp in parallel; the selector just changes which target's `by` you're currently editing.

**Speed ramp target (slider 17)** `Inhale / Top pause / Exhale / Bottom pause, default Inhale`
The 4-option selector. Switching saves the current slider 20 amount to the old target's memory slot and loads the new target's saved amount. All 4 targets ramp regardless of which one is selected — selector switching never stops a ramp.

**Speed ramp duration (slider 18)** `0–60 minutes, default 0`
How long the ramp takes (ramp_t advances 0 → 1 over this many minutes). **0** disables the ramp.

**Speed ramp engage (slider 19)** `Off / On, default Off`
Freeze/resume gate. When On, ramp_t advances; when Off, it freezes wherever it is and resumes from there on re-engage. Engage does NOT reset the ramp — only transport play does.

**Speed ramp by (slider 20)** `-20 to +20 sec, step 0.1, default 0`
Signed delta in seconds for the selected target. **0** = no change. **Negative** = shorten that segment (faster breath if Inhale/Exhale; tighter cycle if Top/Bottom). **Positive** = lengthen (slower / more spacious). Examples: Inhale target with `by` +4 ramps inhale from 4 sec → 8 sec over the duration; Bottom Pause target with `by` -0.2 shortens bottom pause toward minimum. Each target stores its own amount independently.

**Speed ramp start delay (slider 29)** `0–60 minutes, default 0`
Wait this many minutes after engage before ramp_t actually starts advancing. Useful for "fall asleep first, then begin the wind-down."

**Migrating from v2.7:** slider 17 changed from a multiplier (0.1–4.0) to a 4-option target selector (0–3 integer). Existing projects loading the new plugin will see slider 17's old multiplier value rounded down to a target index, and slider 20 (the new amount) defaulting to 0 — so Speed Ramp produces no effect on reload until you re-configure. The audio path changed too: Speed Ramp's effect now lives in per-segment length adjustments (additive) rather than as a global rate multiplier, so it composes additively with Drift instead of multiplicatively.

**Filter timbre is unchanged.** Speed Ramp adjusts segment lengths, not filter coefficients — a longer inhale sounds exactly like a normal inhale, just stretched.

**Transport behavior:** speed_ramp_t resets to 0 on every transport play edge. This is the ONLY thing that resets the ramp — slider changes (selector switch, engage toggle, anything) don't restart it.

### Drift

Slow organic wander applied to the breath cycle rate on top of Speed Ramp. Breaths get slightly longer or shorter cycle to cycle instead of all being identical. See [Per-Plugin Drift](#per-plugin-drift) for the architecture; the seven sliders below configure it for this plugin.

**Musical Period (breaths)** `1–256, default 8`
Period of the musical drift source, measured in breath cycles. Scales with Speed Ramp.

**Musical Up by** `0.0–1.0, default 0`
How far above the center cycle rate the musical drift wanders at its peak, as a multiplier amplitude. 0.1 = breaths up to 10% faster at the peak.

**Musical Down by** `0.0–1.0, default 0`
How far below the center cycle rate the musical drift wanders at its trough. Independent from Up by.

**Slow Period (minutes)** `0.1–60, default 5`
Period of the slow drift source, measured in wall-clock minutes. Does NOT scale with Speed Ramp.

**Slow Up by** `0.0–1.0, default 0`
Above-center amplitude for the slow drift source.

**Slow Down by** `0.0–1.0, default 0`
Below-center amplitude for the slow drift source.

**Shape** `Sine / Triangle / Random, default Sine`
Wander shape applied to both sources.

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

# Womb Sound Generator

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Womb Sound Generator is a multi-layered intrauterine soundscape synthesizer **designed from the baby's perspective inside the womb**. It combines three independently controllable sound sources — Heartbeat, Breath, and Bloodflow — into a single unified output. Each source can be soloed for monitoring and balanced independently. Heart rate variability is modeled across two dimensions — breath-coupled and random — and the bloodflow layer is phase-locked to the heartbeat cycle, producing a coherent physiological simulation rather than independent noise sources running in parallel.

Womb v1 ships with the original breath and bloodflow architectures from the suite's early days. Womb v2 retunes both layers for an intrauterine-listening perspective (muffled lowpass, lower cutoffs, continuous floors, amplitude-modulated bloodflow) — see the Womb v2 section for those v2-specific parameters. Use v1 for projects built on the original sound; v2 is the recommended starting point for new projects.

The plugin generates no audio from an input signal. It is a pure synthesizer and should be placed on an empty FX chain or a track with no audio source.

---

## Signal Architecture

### Heartbeat
The heartbeat engine produces two events per cycle — S1 ("lub") and S2 ("dub") — separated by the systole interval. Each event is synthesized through two parallel resonant filter voices: a "near" voice (prominent, direct) and a "far" voice (slightly detuned, softer). Both voices blend a sine oscillator with white noise as their exciter, pass through a double-cascaded lowpass, and are routed to opposite output channels via an inter-aural delay. The master volume and individual S1/S2 volumes are applied before the three sources are summed.

### Breath
The breath engine runs a four-state cycle: inhale → top pause → exhale → bottom pause. During inhale and exhale, white noise passes through a highpass filter followed by a state-variable lowpass per channel (with slight frequency offsets between L and R for width), then shaped by a fade-in/fade-out envelope. A secondary lowpass post-filter is applied to the full breath signal after mixing. (Womb v2 adds a continuous breath floor and lower intrauterine-perspective defaults — see the Womb v2 section for v2-specific breath parameters.)

### Bloodflow
The bloodflow engine produces a continuously sweeping filtered noise texture. The filter cutoff is phase-locked to the heartbeat cycle — at each cycle start it sweeps from a low resting frequency up to a high peak frequency (simulating the pressure wave of a heartbeat moving through vessels), holds briefly, then returns to the resting frequency. The sweep tracks heart rate automatically. (Womb v2 uses a different bloodflow architecture — amplitude-modulated noise with a cardiac pressure envelope and continuous floor — better matching real intrauterine vasculature recordings. The frequency-sweep design here stays in Womb v1 for back-compat with projects built on it.)

### HRV
Heart rate variability modulates the heartbeat cycle length in real time using two additive layers. The breath-coupled layer derives its timing from the actual breath engine state — heart rate rises during inhale and falls during exhale. The random layer adds a slow, independently wandering offset. Both affect the heartbeat timing and the bloodflow sweep simultaneously, since the bloodflow LFO is tied to the heartbeat phase.

---

## Parameters

### Global

**BPM** `20-200, default 70`
Base heart rate in beats per minute. Affects both heartbeat timing and the bloodflow pulse rate, which is locked to it. Actual BPM fluctuates around this value when HRV is active.

**Master Stereo Flip** `Normal / Flipped`
Swaps the left and right output channels. Useful for adjusting anatomical orientation when using headphones — the prominent (near) heartbeat voice is on the left by default. Flipping reverses this for the full mix without changing internal routing.

---

### Heartbeat

**HB Master Volume** `0.0-1.0, default 1.0`
Overall output level for the entire heartbeat signal. Applied after all heartbeat synthesis and before the three-source mix.

**Heartbeat Solo** `Off / Solo`
Mutes Breath and Bloodflow. Solo is exclusive — enabling a second solo mutes the others.

**Systole ms (S1→S2 gap)** `50-400 ms, default 120`
Delay between the S1 and S2 events within each heartbeat cycle. Shorter values produce a tighter lub-dub; longer values spread the sounds further apart. At very short values the sounds may overlap depending on decay settings.

**S1 Volume** `0.0-1.0, default 1.0`
Output level for the S1 (first heart sound, "lub") event, independent of S2.

**S2 Volume** `0.0-1.0, default 0.7`
Output level for the S2 (second heart sound, "dub") event, independent of S1. S2 is typically quieter than S1 physiologically; the default reflects this.

**Brightness** `0.0-1.0, default 0.3`
Cutoff of the post-resonator lowpass applied to both heartbeat voices. At 0.0 the filter sits around 200 Hz (near) / 175 Hz (far). At 1.0 it opens to approximately 450 Hz (near) / 395 Hz (far).

**S1 Decay ms** `10-200 ms, default 60`
How quickly S1 fades after its attack peak. Longer values produce a sustained thud; shorter values a sharper knock.

**S2 Decay ms** `5-100 ms, default 25`
How quickly S2 fades. S2 is naturally shorter-lived than S1.

**S1 Frequency Hz** `20-120 Hz, default 45`
Base resonant frequency for S1. The near voice center is derived at ×1.1 and the far at ×1.28.

**S2 Frequency Hz** `60-300 Hz, default 80`
Base resonant frequency for S2. The near voice center is derived at ×1.15 and the far at ×1.25.

**HB Stereo Width ms (neg = heart right)** `-15.0–+15.0 ms, default 3.0`
Inter-aural delay between the near and far heartbeat voices. Positive values place the near (prominent) voice on the left — anatomically correct for a heart on the left side. Negative values flip this. Crossing zero resets filter states to prevent artifacts.

---

### Breath

**Breath Volume** `0.0-1.0, default 0.8`
Overall output level for the breath signal.

**Breath Solo** `Off / Solo`
Mutes Heartbeat and Bloodflow.

**Inhale Duration sec** `0.5-20.0 sec, default 4.0`
Length of the inhale phase.

**Top Pause sec** `0.0-5.0 sec, default 0.5`
Silence between inhale and exhale. Set to 0 for an immediate inhale-to-exhale transition.

**Exhale Duration sec** `0.5-20.0 sec, default 4.0`
Length of the exhale phase.

**Bottom Pause sec** `0.0-5.0 sec, default 1.5`
Silence between exhale and the next inhale.

**Inhale Frequency Hz** `50-2000 Hz, default 300`
Center frequency of the lowpass filter applied during the inhale phase. Lower values produce a deeper, body-heavy rush; higher values a brighter, airier sound. Due to sinusoidal frequency-to-coefficient mapping, effective cutoff tracks lower than the displayed value above ~500 Hz.

**Exhale Frequency Hz** `50-2000 Hz, default 180`
Center frequency of the lowpass filter during the exhale phase. Typically set lower than the inhale frequency for a softer outward breath character.

**Breath High-pass Hz** `20-800 Hz, default 150`
High-pass filter applied to the noise before the inhale/exhale lowpass. Removes low-frequency rumble. Raising this value thins the breath toward an airier hiss.

**Inhale Fade In** `0.0-1.0, default 0.3`
Proportion of the inhale duration spent fading up from silence.

**Inhale Fade Out** `0.0-1.0, default 0.2`
Proportion of the inhale duration spent fading back to silence at the end.

**Exhale Fade In** `0.0-1.0, default 0.2`
Proportion of the exhale duration spent fading up from silence.

**Exhale Fade Out** `0.0-1.0, default 0.3`
Proportion of the exhale duration spent fading back to silence.

**Fade Mode** `Linear / Cosine / Exponential / Natural`
Curve shape applied to all four breath fade regions.
- **Linear** — straight ramp.
- **Cosine** — S-curve, gentle at both ends.
- **Exponential** — squared curve, aggressive.
- **Natural** — sine-based curve, typically the most perceptually smooth.

**Breath Stereo Width** `0.0-1.0, default 0.5`
Spreads the inhale and exhale filter frequencies between L and R. At 0.0 both channels use identical frequencies. At 1.0 the spread is ±15% for inhale and ±12% for exhale.

---

### Bloodflow

Womb v1 uses the original frequency-sweep bloodflow design. Womb v2 uses an amplitude-modulated bloodflow with a cardiac pressure envelope and continuous floor — see the [Womb v2](#womb-sound-generator-v2) section below for v2-specific bloodflow parameters.

**Bloodflow Volume** `0.0-1.0, default 0.5`
Overall output level for the bloodflow signal.

**Bloodflow Solo** `Off / Solo`
Mutes Heartbeat and Breath.

**Bloodflow Low Frequency Hz** `20-2000 Hz, default 150`
Filter cutoff at the resting state between heartbeats — the floor of the sweep.

**Bloodflow High Frequency Hz** `20-4000 Hz, default 600`
Filter cutoff at the peak of the sweep, immediately after each heartbeat. If set lower than the Low Frequency value, the two are automatically swapped.

**Bloodflow Resonance** `0.0-0.95, default 0.2`
Resonance of the sweeping bloodflow filter. Higher values make the sweep more tonal and whistling. Values above 0.7 can produce self-oscillation artifacts.

**Bloodflow Fade In** `0.0-1.0, default 0.15`
Proportion of each heartbeat cycle spent sweeping up from low to high frequency. Shorter values produce a sharper, more percussive onset.

**Bloodflow Fade Out** `0.0-1.0, default 0.15`
Proportion of each heartbeat cycle spent returning from high to low frequency. If Fade In + Fade Out exceed 1.0, both are proportionally normalized.

**Bloodflow Stereo Width** `0.0-1.0, default 0.5`
Spreads the bloodflow filter cutoff between L and R. At 1.0 the L channel cutoff is approximately 8% higher than R at any given point in the sweep.

---

### Heart Rate Variability

Both HRV parameters operate additively. They affect the heartbeat timing and, because the bloodflow envelope is phase-locked to the heartbeat, the bloodflow pulse rate as well.

**Breath HRV Depth** `0.0-0.25, default 0.08`
Depth of breath-coupled heart rate modulation. The HRV modulation in this plugin is derived from the actual breath engine state — not a separate oscillator — so the timing is governed by the Inhale/Exhale/Pause duration settings. Heart rate increases during inhale and decreases during exhale. A value of 0.08 produces approximately ±8% variation around the base BPM.

**Random HRV Depth** `0.0-0.08, default 0.02`
Adds a slowly wandering random offset to heart rate. The random target updates approximately every 5 seconds and slews toward it over ~3 seconds. At 0.0 random HRV is disabled.

---

### Breath Post-Filter

A lowpass filter applied to the full breath signal after the inhale/exhale synthesis, operating on the mixed breath output.

**Breath Post-filter Hz** `50-4000 Hz, default 600`
Cutoff frequency of the post-filter. Lowering this darkens the entire breath layer. Acts as a global brightness control independent of the per-phase frequency settings.

**Breath Post-filter Q** `0.5-8.0, default 1.5`
Resonance of the post-filter. Higher slider values produce lower resonance — this parameter is implemented internally as `1/Q`. Lower slider values produce a more resonant peak at the cutoff frequency.

### Start Delay

**Start Delay (beats)** `0–1000, default 0`

Silent for N heartbeats after playback starts, then the full womb soundscape (heartbeat, breath, bloodflow) begins normally. Beats are counted at the Heartbeat BPM — at 60 BPM, "4 beats" is 4 seconds; at 120 BPM it's 2 seconds. All internal state (heartbeat cycle phase, breath state machine, bloodflow filter, post-filter buffers) stays frozen during the delay so everything begins cleanly at delay-end. Re-arms on every transport stop/start. 0 disables the delay.

### Play / Rest Gating (v2.1) — independent per layer

Each of the three layers has its own Play/Rest gate, so you can run e.g. continuous bloodflow + breathing under a heartbeat that pulses in patterns. Six sliders total — two per layer:

**HB: Play for / Rest for (beats)** `0–1000, default 0`
**Breath: Play for / Rest for (breaths)** `0–1000, default 0`
**Bloodflow: Play for / Rest for (heartbeats)** `0–1000, default 0`

Each gate engages only when BOTH of its sliders are > 0. Layers with disabled gates run continuously as before.

**Heartbeat gate** — counts heartbeats at the Heartbeat BPM. Skips the next beat trigger when resting; the previously-fired S1/S2 envelopes finish naturally so the gate sounds like "drop a beat" rather than a hard cut. Same mechanism as the standalone Heartbeat Generator.

**Breath gate** — counts breath cycles (one full inhale → top pause → exhale → bottom pause). At rest entry the state machine pauses on the bottom pause (which is silent anyway), so rest is just an extended bottom pause. A sample-counted timer (`Rest for × total breath duration`) decides when to exit rest and start a fresh inhale. Same as the standalone Breath Generator.

**Bloodflow gate** — counts heartbeats (since bloodflow is phase-locked to the heartbeat cycle, "one bloodflow cycle" = "one heartbeat cycle"). Fades the bloodflow output to 0 via a smooth ~3 ms ramp on rest entry; filter state keeps running so the filter is "warm" and re-engages cleanly on rest exit. Note that bloodflow's gate uses its OWN beat counter independent of the Heartbeat gate's — you can have HB resting while Bloodflow is still in its play period, or vice versa.

**Interactions worth knowing:**
- HB and Bloodflow both tick on `hb_phase` wraps. So even if HB is gating beats out, `hb_phase` keeps advancing (no audible beats but the underlying clock runs) — Bloodflow's counter advances at the same rate as if HB were playing.
- Breath uses its own state-machine clock, which is unrelated to Heartbeat BPM. Breath's timing is governed by the four phase-duration sliders.

**Transport behavior**: conventional. Stop silences; play re-initializes all per-layer gate state and starts each gate fresh in its play period.

### Speed Ramp (new)

A single in-plugin slowdown / speedup that takes **all three layers down together** — heartbeat, breath, and bloodflow (locked to heartbeat). Designed for sleep use without needing automation envelopes.

**Speed ramp target (multiplier)** `0.1–4.0, default 1.0` · **Speed ramp duration (minutes)** `0–60, default 0` · **Speed ramp engage** `Off / On, default Off`

The multiplier scales the heartbeat BPM and the breath state machine's advance rate simultaneously. **0.5** = the whole womb at half tempo (HB drops from 70 → 35 BPM, breaths take twice as long, bloodflow follows HB as always); **2.0** = double. The HB Stereo Width delay is unaffected, so the spatial relationship between near/far heart sounds doesn't change as the speed ramps.

Off → On captures the in-flight multiplier; On → Off freezes at the current position. Set target = 1.0 and re-engage to return. Resets on every play press.

A ~100 ms smoother also sits between the BPM slider and the audio so manual BPM tweaks no longer click. Always on.

### Drift

Slow organic wander applied to **all three layers together** — heartbeat, breath, and bloodflow — so the womb wanders as a coherent organism rather than three independent recordings. Sits on top of Speed Ramp. This is the layer that makes Womb feel like something alive instead of a loop. See [Per-Plugin Drift](#per-plugin-drift) for the architecture; the seven sliders below configure it for this plugin.

**Musical Period (heartbeats)** `1–256, default 32`
Period of the musical drift source, measured in heartbeats. Scales with Speed Ramp.

**Musical Up by** `0.0–1.0, default 0`
How far above the center rate the musical drift wanders at its peak, as a multiplier amplitude. Applied uniformly to heartbeat BPM and the breath state machine's advance rate.

**Musical Down by** `0.0–1.0, default 0`
How far below the center rate the musical drift wanders at its trough. Independent from Up by.

**Slow Period (minutes)** `0.1–60, default 5`
Period of the slow drift source, measured in wall-clock minutes. Does NOT scale with Speed Ramp.

**Slow Up by** `0.0–1.0, default 0`
Above-center amplitude for the slow drift source.

**Slow Down by** `0.0–1.0, default 0`
Below-center amplitude for the slow drift source.

**Shape** `Sine / Triangle / Random, default Sine`
Wander shape applied to both sources.

---

## Usage Notes

- **Bloodflow is phase-locked to the heartbeat.** Changing BPM immediately changes the bloodflow pulse rate. The two cannot be decoupled within this plugin.
- **Breath HRV is coupled to the breath engine state.** The HRV timing is determined by the Inhale/Exhale/Pause duration settings, not by a separate rate control. Breath and HRV are genuinely synchronized.
- **The Breath Post-filter Q slider is inverted** relative to conventional filter labeling — higher slider values produce lower resonance.
- **Solo is exclusive.** Any active solo mutes the other two sources. Solo sliders are independent booleans and do not stack.
- **Frequency display for breath parameters reflects nominal Hz.** Sinusoidal coefficient mapping means effective cutoff tracks lower than the displayed value above ~500 Hz, consistently across all filters in the breath section.

---

*Womb Sound Generator is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

# Womb Sound Generator v2

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Womb Sound Generator v2 is a Womb variant with a different breath-rate and HRV/drift architecture. It ships **alongside** the original Womb (both files live in the same plugin folder); choose whichever fits your project. v2 is the recommended version going forward; v1 remains available for projects already built on it.

What's different from v1:

- **Heart Rate Variability is now bidirectional and expressed in concrete BPM.** Heart rate rises during inhale, peaks at top pause, descends past baseline during exhale, and dwells at the trough during bottom pause for 1–2 beats before climbing again — matching real RSA physiology. v1's "Breath HRV Depth" was an abstract 0–0.25 scaler that only modulated above baseline; v2 replaces it with **Heart with breath (BPM peak-to-peak)**, a single slider expressing the full swing in audible BPM.
- **Breath rate has an optional master rate slider.** Default is 0 (inert — the four duration sliders 16–19 control the breath rate directly, same as v1). Set to nonzero and the four durations rescale once to match the implied total. Subsequent duration edits don't update BPM back — this is a one-way rescale tool, not a bidirectional sync, matching Reaper's per-track Timebase semantics and consumer breathing-app conventions.
- **Heart drift and breath drift are independent.** Real physiology has heart rate variability and respiratory rate variability that drift on their own timescales, not in lockstep. v2 gives heart and breath separate Up/Down/Period sliders rather than sharing a single drift wave across both. This is a deliberate divergence from the suite-wide canonical per-plugin drift (Musical + Slow); other plugins don't have the same physiological constraint.
- **The v1 "Random HRV Depth" slider is gone.** Random heart-rate wander is now covered by Heart drift in shape=Random mode.

Sliders 1–51 follow Womb v1's layout for Heartbeat, Start Delay, Play/Rest Gating, and Speed Ramp — see the [Womb Sound Generator](#womb-sound-generator) section above for those parameters. The differences in v2 are:

- **Bloodflow architecture** is different in v2 — same slider IDs (29–36), different semantics (amplitude-modulated envelope rather than frequency sweep). See "Bloodflow (v2)" below.
- **Breath** has different defaults and an added continuous floor in v2 — same slider IDs (14, 20-22, 39), different default values and an extra always-on background. See "Breath (v2)" below.
- **Breath HRV** sliders 37/38 are removed in favor of explicit Heart drift / RSA / Breath drift controls at the end of the slider range.
- **Breath-rate-and-drift block** at sliders 52–60 is v2-specific.

### Breath (v2)

v2 retunes the breath layer for an intrauterine-listening perspective: the per-phase filter cutoffs sit substantially lower (Inhale 250 Hz, Exhale 170 Hz vs v1's 300 / 180 — also lower than the standalone Breath Generator's 800 / 600 Hz "natural breath at the source" defaults), and the breath envelope rides on a continuous floor of about 15% of peak rather than dropping to silence during pauses. Both per-phase filters run continuously in v2 (rather than only the currently-active one as in v1) so pauses can output the most-recently-active filter's character at floor level without producing a click on state transitions. Matches what intrauterine recording literature shows: baby hears continuous low-level body noise even between maternal breaths, dominated by content below ~200 Hz.

**Breath Volume default 0.5** (v1: 0.8)
Lower because intrauterine recordings show breath is one of the quieter components of the fetal sound environment — below maternal vasculature and GI activity in loudness.

**Inhale Frequency Hz default 250** (v1: 300)
Cutoff sits at the spectral boundary above which the amniotic medium attenuates almost everything.

**Exhale Frequency Hz default 170** (v1: 180)
Slightly lower than Inhale, same convention as v1.

**Breath High-pass Hz default 80** (v1: 150)
Lower because the per-phase lowpass cutoffs are lower in v2; a tighter HP would chop the deep-body content.

**Breath Post-filter Hz default 500** (v1: 600)
Provides additional womb-medium attenuation on top of the per-phase lowpasses.

**Continuous floor** (internal, hardcoded at 0.15 of peak)
The breath envelope rides on a continuous floor. Pauses (top, bottom) and fade-in / fade-out tails sit at floor level rather than silence so the cycle's endpoints don't produce extended silent gaps. Top pause inherits the inhale filter's character; bottom pause inherits the exhale filter's.

### Bloodflow (v2)

v2 replaces v1's frequency-sweep bloodflow with an amplitude-modulated approach: the noise filter cutoff is FIXED at a single center frequency; what shapes the per-beat sound is loudness, modulated by a cardiac pressure envelope (cosine upstroke during systole, cosine decay through diastole) with a faint dicrotic notch in the decay tail and a continuous floor between beats. Matches the continuous-flow-with-pulse character of actual intrauterine vasculature recordings rather than the wah-pedal character the freq sweep produces.

**Bloodflow Volume** `0.0-1.0, default 0.7`
Higher default than v1 (0.5) — intrauterine literature says vasculature is the loudest layer in the womb mix.

**Bloodflow Filter Hz** `20-2000 Hz, default 250`
Fixed center frequency of the bloodflow noise filter (replaces v1's Low/High Frequency Hz pair). Default sits at the upper end of the womb-perspective deep-rumble range.

**Bloodflow Dicrotic Level** `0.0-1.0, default 0.1`
Strength of the dicrotic notch — secondary pulse from aortic-valve closure reflecting back through the arterial tree. Womb medium attenuates this heavily so default is low; raise toward 0.3-0.4 for more articulated double-pulse.

**Bloodflow Resonance** `0.0-0.95, default 0.2`
Filter resonance (same semantic as v1).

**Bloodflow Attack (proportion of cycle)** `0.005-0.5, default 0.15`
Cosine upstroke duration as fraction of cycle. Replaces v1's Fade In.

**Bloodflow Decay (proportion of cycle)** `0.05-0.95, default 0.85`
Cosine decay duration. Default 0.85 covers nearly the entire post-attack cycle — continuous-modulating whoosh rather than sharp-pulse-with-silence. Replaces v1's Fade Out. If Attack + Decay exceeds 1.0 both are proportionally normalized.

**Bloodflow Stereo Width** `0.0-1.0, default 0.5`
Same semantic as v1 — L/R cutoff offset for decorrelation.

**Continuous floor** (internal, hardcoded at 0.25 of peak)
The envelope rides on a continuous floor. Between maternal heartbeats the bloodflow noise doesn't fall to silence, it drops to floor level — models the placental whoosh baby hears continuously. With default Attack + Decay = 1.0 the envelope is barely at floor; the floor mainly matters when Attack + Decay are dialed below 1.0 leaving an idle tail.

---

## Parameters (v2-specific block, sliders 52–60)

### Breaths per minute

**Breaths per minute** `0–30, default 0 = inert`

Optional one-way master rate control for the breath cycle. At 0 the slider is inert — the four phase duration sliders (Inhale / Top Pause / Exhale / Bottom Pause) control the breath rate directly, identical to v1 behavior. Set to a nonzero value and the four durations rescale proportionally to fit a total cycle of 60 / BPM seconds, preserving their inhale/exhale/pause ratios.

After the rescale, you can keep adjusting the duration sliders directly — those edits don't update BPM back. Each new BPM value you set triggers a fresh rescale of the current durations, so you can sweep the breath cycle longer or shorter by sliding BPM while keeping the shape proportions. Return BPM to 0 to "release" the durations back to manual control.

Behaves like Reaper's per-track Timebase: a top-level convenience knob that affects subordinate controls, not a source of truth that overrides them.

### Heart drift

Slow organic wander of heart rate around its baseline. Asymmetric up/down amplitudes match the bio-feel convention from the suite-wide per-plugin drift (real heart rate variability is famously asymmetric around its mean). Heart drift is independent of Breath drift below — they represent two real biological rates that drift on their own timescales.

**Heart drift: Up by (BPM)** `0–50, default 0`
How many BPM above baseline the heart rate can wander at the drift peak.

**Heart drift: Down by (BPM)** `0–50, default 0`
How many BPM below baseline the heart rate can wander at the drift trough.

**Heart drift: Period (heartbeats)** `1–1000, default 8`
How many heartbeats per one drift cycle. Scales with Speed Ramp.

Set both Up by and Down by to 0 to disable Heart drift entirely. Use Drift shape (slider 60) to pick wave shape.

### Heart with breath (RSA)

**Heart with breath (BPM peak-to-peak)** `0–30, default 0`

Respiratory sinus arrhythmia in concrete BPM. A value of 6 means the heart rate climbs ~3 BPM above baseline at the top of inhale, descends ~3 BPM below baseline at the bottom of exhale, with linear ramps in between and the natural top-pause/bottom-pause durations giving the peak and trough their dwell time.

This replaces v1's "Breath HRV Depth" abstract scaler. Setting matches real RSA physiology: real bodies show 1–2 beats of slowing at the bottom of breath before climbing back — slider 56 set to anything nonzero produces that observable behavior.

Heart with breath is additive on top of Heart drift — when both are active the heart rate gets both the slow wander (Heart drift) and the breath-coupled swing (Heart with breath) layered together. Set to 0 to disable RSA modulation entirely.

### Breath drift

Slow organic wander of breath rate, independent of Heart drift above. Unit is breaths/min, parallel to Heart drift's BPM. Set both Up by and Down by to 0 to disable.

**Breath drift: Up by (breaths/min)** `0–15, default 0`
How many breaths/min above baseline the breath rate can wander at the drift peak.

**Breath drift: Down by (breaths/min)** `0–15, default 0`
How many breaths/min below baseline the breath rate can wander at the drift trough.

**Breath drift: Period (breath cycles)** `1–1000, default 8`
How many breath cycles per one drift cycle. Scales with Speed Ramp.

Breath drift's baseline reads from slider 52 (Breaths per minute) when that's set to nonzero, otherwise from the four duration sliders summed — so Breath drift works correctly regardless of whether you're driving the breath rate from BPM or from durations directly.

### Drift shape

**Drift shape** `Sine / Triangle / Random, default Sine`

Wave shape shared by both Heart drift and Breath drift. Heart with breath (RSA) has its own shape — coupled to the breath state machine — and is not affected by this setting.

- **Sine** — smooth continuous wander.
- **Triangle** — linear ramps with turnaround points.
- **Random** — value-noise that interpolates smoothly between random targets at each period boundary.

---

## Usage Notes (v2-specific)

- **The Heart with breath modulation has the right shape automatically.** Because it's coupled to the breath state machine (not an independent oscillator), the dwell at top and bottom of breath comes for free from the breath cycle's own pause durations. You don't need to tune the peak or trough hold separately.
- **BPM at 0 is the default and the most flexible mode.** Most operators tune the breath cycle by setting the four duration sliders directly. BPM is there for when you want to quickly take the breath cycle from "7 BPM" to "5 BPM" without recalculating the durations. Both modes work fine; BPM is the convenience.
- **Heart drift and Breath drift are deliberately not linked.** Setting them both with similar amplitudes and periods gives a coherent organism feel; setting them differently gives you a body where the breath and heart wander on their own schedules. Both shapes are physiologically reasonable.
- **Per-plugin Drift suite convention does NOT apply to Womb v2.** Other rate-bearing plugins in the suite (Polyrhythm Phase, Heartbeat, Tremolo, etc.) use the canonical per-plugin drift sliders (Musical drift Up/Down/Period + Slow drift Up/Down/Period + Shape). Womb v2 diverges intentionally — heart and breath drift independently because real physiology has two independent rate systems. If you're used to the canonical suite drift, the slider names and structure will feel different.
- **All other Womb v1 usage notes apply** — Bloodflow phase-locked to heartbeat, Breath Post-filter Q inverted, Solo exclusive, frequency display reflects nominal Hz.

---

*Womb Sound Generator v2 is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

# Womb Sound Generator v3

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Womb Sound Generator v3 is a Womb variant with the same three-layer architecture as v2 (heartbeat / breath / bloodflow) and most of the same controls. The headline change is the **drift system**: v2 had separate Heart drift and Breath drift slider blocks covering 2 wander targets. v3 collapses to a single target-selector pattern (same shape Resonance Bank uses) that covers **7 wander targets** with **fewer total sliders**: Heart BPM, S1-S2 gap, Inhale Duration, Top Pause, Exhale Duration, Bottom Pause, and RSA depth. All seven wanders run in parallel; you configure them one at a time via the selector.

v3 also adds a **periodic sigh** mechanism — every ~N minutes a single breath's inhale stretches by a configurable depth multiplier, modeling the real sleep-breathing pattern of occasional deep breaths between regular cycles.

v3 ships **alongside** v1 and v2 (all three files live in the same plugin folder). v2 stays available unchanged for projects already built on it. v3 is the recommended version going forward for new projects.

The audio architecture (heartbeat sound generation, breath filters, bloodflow envelope, post-filter, Solo logic, Speed Ramp, Start Delay, Play/Rest gates per layer, BPM rescale, Heart-with-breath RSA) is identical to v2 — those parts of the design are mature and didn't need changes.

---

## What's different from v2

| Concern | v2 | v3 |
|---|---|---|
| Drift targets | Heart BPM + Breath rate (2 total) | Heart BPM + S1-S2 gap + Inhale + Top pause + Exhale + Bottom pause + RSA depth (7 total) |
| Drift sliders | 6 (Heart up/down/period + Breath up/down/period) + 1 shape = 7 | 5 (target + up + down + period + shape) |
| Sighs | none | Yes (interval + depth multiplier, multiplier scales ALL four segments) |
| Heart-with-breath baseline | slider 56 | slider 59 (moved to make room for the new drift block) |
| Drift configs persist across save/load | n/a (per-slider) | Yes (via `@serialize`; all 7 targets' configs preserved) |
| Speed ramp shape | one scope (scales all 3 layers together via a multiplier) | **nested-selector pattern: pick which target to ramp, set a signed amount.** Every target is additive — each ramp affects only its own parameter. |
| Speed ramp amount semantics | multiplier 0.1-4.0 (destination scaling) | signed delta in target's natural units (0 = no change, negative = decrease, positive = increase) |
| Speed ramp behavior on transport play | resets implicitly via @init re-run | resets explicitly via play-edge detection (so drift state stays continuous while ramp restarts cleanly) |
| Audio sliders (1-47) | unchanged | unchanged |
| Speed ramp sliders | 48-51 (multiplier / duration / engage / start delay) | 48-52 (target / amount / duration / engage / start delay — note: amount is NEW) |

Migration from v2: the audio-shaping sliders 1-47 keep their meaning, so the heart sound, breath sound, bloodflow, and per-layer gates all carry over unchanged. Everything from slider 48 onward needs to be re-entered — v3 changed the layout substantially (Speed Ramp added an amount slider and switched to signed-delta semantics; BPM rescale shifted from slider 52 to slider 53; the drift block is now nested-selector at sliders 54-58; RSA moved to slider 59; sighs are new at sliders 60-61).

---

## Signal Architecture

Identical to v2 for the three audio layers (see [Womb Sound Generator v2 → Signal Architecture](#womb-sound-generator-v2) for the full description). The change is in **how the drift modulations are computed and applied**:

Each of the 7 drift targets has its own phase counter advancing per sample. The phase advance scales with Speed Ramp so all drifts slow together when Speed Ramp engages. Per-target up amount, down amount, period, and shape are stored in a per-instance memory bank — the slider 55-57 values you see at any moment reflect whichever target is currently selected.

Target indices and units:

| Target | Index | Up/Down units | Period units |
|---|---|---|---|
| Heart BPM | 0 | BPM | heartbeats |
| S1-S2 gap | 1 | ms | heartbeats |
| Inhale | 2 | seconds | breath cycles |
| Top pause | 3 | seconds | breath cycles |
| Exhale | 4 | seconds | breath cycles |
| Bottom pause | 5 | seconds | breath cycles |
| RSA depth | 6 | BPM peak-to-peak | breath cycles |

Each drift offset is added to the target's baseline slider value per sample. For example: with Heart BPM target's up/down at 5/5 and a period of 8 heartbeats with Sine shape, the effective BPM each beat wanders within ±5 of the baseline slider 1 value, completing one full sine over 8 beats.

---

## Parameters

### Global Controls

Sliders 1-47: identical to [Womb Sound Generator v2](#womb-sound-generator-v2). See that section for full descriptions of BPM, the three layer Volume / Solo sliders, heartbeat sound parameters (Systole ms, S1/S2 Frequency Hz, Decay ms, Brightness, Stereo Width ms), breath sound parameters (Inhale/Top Pause/Exhale/Bottom Pause durations, Frequencies, Fade In/Out, Stereo Width, Post-filter), bloodflow parameters (Filter Hz, Dicrotic Level, Resonance, Attack, Decay, Stereo Width), Start Delay, and per-layer Play/Rest gates.

Sliders 48-52 are the Speed Ramp block, sliders 54-58 are the Drift block, slider 53 is BPM rescale, slider 59 is Heart-with-breath / RSA depth, sliders 60-61 are the Sigh mechanism — all described below.

### Drift target selector (slider 54)

`Drift target` — pick which parameter the drift sliders 55-58 are currently configuring. Options: **Heart BPM**, **S1-S2 gap**, **Inhale**, **Top pause**, **Exhale**, **Bottom pause**, **RSA depth**.

Switching the selector saves the current values of sliders 55-58 to the previously-selected target's memory slot, then loads the newly-selected target's saved values into the sliders. So you never lose any target's configuration — it just gets hidden when you switch to another target. **All seven configured drifts run in parallel** regardless of which one you're currently editing.

### Drift up amount (slider 55)

`Drift up amount (units match target)` — peak amplitude the current target wanders ABOVE its baseline. Range 0-50 step 0.1; the unit depends on the target (BPM for Heart BPM and RSA depth, ms for S1-S2 gap, seconds for breath segments). 0 disables the upward swing.

### Drift down amount (slider 56)

`Drift down amount (units match target)` — peak amplitude the current target wanders BELOW its baseline. Same range and unit-by-target as Up. Setting Up and Down to different values gives biological-feel asymmetry around the baseline. Setting both to 0 disables drift for this target entirely.

### Drift period (slider 57)

`Drift period (heartbeats or breath cycles)` — how many parent-rhythm cycles one full drift wave takes. Range 1-1000 step 1. The unit auto-matches the target: heartbeats for Heart BPM and S1-S2 gap, breath cycles for the four breath segments and RSA depth.

Period 1 with Random shape gives beat-to-beat (or breath-to-breath) jitter — each cycle gets a fresh random value within the up/down range.

### Drift shape (slider 58)

`Drift shape` — wave shape for the drift modulation. Options:

- **Sine** — smooth continuous wander, equal time on either side of baseline.
- **Triangle** — linear ramps with turnaround points at the peaks.
- **Random** — value noise that interpolates smoothly between random targets at each period boundary. Random targets are independent per-target (each of the 7 wander-targets has its own random state).

### Heart with breath (slider 59)

`Heart with breath (BPM peak-to-peak)` — baseline RSA coupling depth. Identical semantics to v2's slider 56 (moved to slider 59 in v3 because the drift block needed those slots). 0 = no RSA. A value of 6 means HR climbs ~3 above baseline at the peak (top of inhale) and descends ~3 below at the trough (bottom of exhale).

When drift target 6 (RSA depth) has nonzero up/down values, this baseline depth wanders too — the up/down amplitudes are in the same BPM peak-to-peak units.

### Speed Ramp (sliders 48-52)

Speed Ramp in v3 uses the nested-selector pattern (same shape as Drift) and all five Speed Ramp sliders live in one place. Pick a target on slider 48, set the amount on slider 49, set the duration and engage. The targets and their natural units:

| Selector | Target | Amount unit |
|---|---|---|
| 0 | Heart BPM | BPM |
| 1 | S1-S2 gap | ms |
| 2 | Inhale Duration | seconds |
| 3 | Top Pause | seconds |
| 4 | Exhale Duration | seconds |
| 5 | Bottom Pause | seconds |
| 6 | RSA depth | BPM peak-to-peak |

**Amount is a signed delta, not a destination.** 0 means no ramp (safe default — engaging while at 0 does nothing). Negative means decrease this parameter — slower heart, shorter inhale, less RSA swing. Positive means increase — faster heart, longer inhale, more swing. Whatever you type is how far the parameter moves from its current value over the duration. To slow heart from 70 to 35, set Heart BPM target and an amount of -35. To stretch inhale from 4 sec to 8 sec, set Inhale target and +4.

**All targets are additive — they ramp only their specific parameter.** Speed Ramp is for independent fine-tuning, not organism-wide scaling. Selecting Heart BPM with amount -35 ramps just the heart down by 35 BPM; the breath cycle stays at its base rate, top/bottom pauses stay at their base, RSA depth stays where you left it. Bloodflow follows the heart automatically (it's phase-locked by design), so a Heart BPM ramp does also slow bloodflow — but breath does NOT auto-slow.

If you want the v2-style "whole womb winds down together" feel where everything slows in coordinated lockstep: configure a `by` amount on each target you want to ramp (Heart BPM and the breath segments most likely), then engage. All 7 targets' ramps run in parallel over the same duration, so configuring multiple targets gives you a coordinated multi-parameter wind-down. The selector is just for editing — switching it does NOT stop ramps already running on other targets (same model as drift).

#### Sliders

- **slider 48 — Speed ramp target** — the 7-option selector. Changing it saves the current slider 49 amount to the previous target's memory slot, then loads the new target's saved amount into slider 49. So you can configure multiple targets in sequence and switch between them without losing settings.

  **All 7 ramps run in parallel** (same model as drift). The selector is just for editing — switching it does NOT stop a ramp already running on another target. If you set Heart BPM `by` -35 and Inhale `by` +4 and engage, both ramp together over the same duration. Targets you haven't configured stay at amount 0, which is a no-op.

- **slider 49 — Speed ramp by** — signed delta in the selected target's natural units. Range -300 to +300, step 0.1. **0 = no change, negative = decrease, positive = increase.** Reads as a sentence with the selector: *"Speed ramp by -35, target Heart BPM."* Examples:
    - Heart BPM target, amount -35: heart ramps DOWN 35 BPM from wherever it started (70 → 35).
    - Inhale target, amount +4: inhale ramps from 4 sec → 8 sec.
    - Bottom Pause target, amount +2: bottom pause stretches by 2 seconds.
    - RSA depth target, amount +6: RSA swing grows by 6 BPM peak-to-peak.

  Each target stores its own amount, so configuring an amount for Heart BPM, switching to Inhale, configuring there, and switching back to Heart BPM brings back the original Heart BPM amount.

- **slider 50 — Speed ramp duration (minutes)** — how long the ramp takes. Range 0-60 minutes. 0 means no ramping (the ramp is effectively disabled).

- **slider 51 — Speed ramp engage** — Off/On. Acts as a freeze/resume gate: when On, ramp progress advances; when Off, ramp progress freezes wherever it is and resumes from there when you flip On again. Engage does NOT reset the ramp — the only thing that does is transport play (so each play press starts a fresh ramp from 0). This means you can switch the target selector mid-ramp without affecting the running ramp, and you can adjust other sliders without the ramp restarting.

- **slider 52 — Speed ramp start delay (minutes)** — wait this many minutes after engage before the ramp actually starts. Range 0-60. Useful for "let me fall asleep for 10 minutes, then begin the wind-down."

#### How ramp_t works

While engaged and past the start delay, `ramp_t` advances from 0 to 1 over the configured duration. At any moment, the offset applied to the selected target is `ramp_t × amount`. So:

- ramp_t = 0 → offset = 0 → no change to the target's value
- ramp_t = 1 → offset = amount → target's effective value = baseline + amount
- in between → linear interpolation

When disengaged, ramp_t freezes at its current value — the system holds the partial ramp. Re-engaging resumes from the frozen value (engage is a gate, not a restart). The only thing that resets ramp_t to 0 is a transport play edge.

#### Speed Ramp + Drift + Sighs

Speed Ramp, Drift, and Sighs all compose at the parameter consumption sites:

```
effective_inhale_sec = baseline_slider16 + drift_offset[2] + speed_ramp_inhale_offset
```

Drift wanders the segment cycle-to-cycle. Speed Ramp adds a one-way movement (the amount, scaled by ramp_t) on top. Sigh multiplies the resulting (drifted + ramped) length by the sigh multiplier when a sigh is in progress. All three layers stack independently — drift continues during a ramp, sigh continues during a ramp, the underlying physiology stays alive.

For Heart BPM specifically: drift, RSA, and Speed Ramp heart offsets all add to the smoothed BPM in raw BPM units. So a Heart BPM ramp of -35 BPM still has drift wandering ±5 BPM around the trajectory, and RSA still modulates ±3 BPM around that, all the way through the ramp. Organic at every moment — the drift's absolute size doesn't change as the ramp progresses (whereas in a multiplicative design, drift would scale with the ramped rate, making it feel different at the endpoint vs the start).

#### Migration from v2's Speed Ramp

v2 had one Speed Ramp scope that scaled all 3 layers proportionally (target = multiplier 0.1-4.0). v3 splits that into 7 explicit additive targets — there is no longer a "scale everything together" mode. The closest equivalent of v2's "ramp everything to 50% over 10 minutes" is to configure Speed Ramp on Heart BPM AND independently set breath drift / Speed Ramp on the breath segments to slow them too. The slow-down isn't automatically propagated because Speed Ramp's intent in v3 is independent fine-tuning, not organism-wide scaling.

This is a deliberate departure from v2. If the v2 "whole organism wind-down" feel is what you actually want, the workflow is: ramp Heart BPM via Speed Ramp, AND set drift on each breath segment so they wander into longer values over time. Or — simpler — for a coherent wind-down, leave breath drift off and just ramp Heart BPM; the heart slows while breath stays at its natural rate. Real physiology actually does this: breath and heart DON'T always slow together; they're separate rhythms with their own variability.

---

### Sigh interval (slider 60)

`Sigh interval (minutes, 0=off)` — average minutes between sighs. Range 0-30 step 0.1. 0 disables sighs entirely (no event ever fires).

When the timer reaches the configured interval, the NEXT breath transition (state 3 → state 0, end of bottom pause → start of new inhale) flags that breath as a sigh. The flag stays set through the entire sigh breath — inhale, top pause, exhale, bottom pause — and clears at the next 3→0 transition (where a new sigh may fire immediately if the timer crossed threshold again).

The timer scales with Speed Ramp — so when Speed Ramp slows the whole womb down, sigh interval slows along with it. (Specifically: every sample, `sigh_time_since_last += (1/srate) * speed_scale_current`.)

### Sigh depth multiplier (slider 61)

`Sigh depth multiplier` — how much longer each segment of the sigh breath is, compared to a normal breath. Range 1.0-3.0 step 0.05. 1.0 = no stretch (effectively disables sighs even with a nonzero interval); 1.5 = sigh breath is 1.5× longer in every segment; 3.0 = 3× longer. Default 1.5.

**All four segments stretch uniformly** — inhale, top pause, exhale, and bottom pause all get multiplied by the same value. The whole sigh breath is "more breath" — same shape as a normal breath, just longer and consequently deeper (the inhale envelope rises higher under the same fade curves applied over a longer span). I:E and pause ratios are preserved during the sigh, which matches the observed shape of real sighs (the entire breath cycle elongates, not just one phase).

**Drift continues to apply through the sigh.** Each segment's length at state entry is `(current drifted length) × slider61` — so a sigh that fires during a "longer inhale" portion of the breath-drift wander is even longer, while a sigh during a "shorter inhale" portion is correspondingly shorter. The sigh inherits the live drift state; it doesn't lock to a snapshot.

---

## Workflow tips

### Configuring drift across multiple targets

1. Set slider 54 to the target you want to drift first (e.g. Heart BPM).
2. Set sliders 55-58 (up amount, down amount, period, shape) for THAT target.
3. Change slider 54 to the next target. Sliders 55-58 will snap to fresh values (defaults for an unconfigured target, or whatever you set previously if you've already touched that target).
4. Set 55-58 for the new target. The previous target's values are saved automatically.
5. Repeat for as many targets as you want. They all run in parallel.

If you ever want to **disable** a target's drift without losing its configuration: select it, set Up amount AND Down amount to 0. The target is now effectively muted but its period and shape are still remembered for later.

### Sigh + drift together

Sighs and drift compose multiplicatively. The drift system wanders each segment's length per sample; when a sigh starts (state 3 → 0 transition), each subsequent state's length is set as `(current drifted length) × slider61`. So a sigh that fires when breath drift has the inhale at its peak makes for a particularly long inhale; a sigh that fires when drift has the inhale at its trough is correspondingly shorter. The sigh isn't a frozen island — it inherits whatever organic wander is current.

Heart drifts (Heart BPM, S1-S2 gap, RSA depth) are independent of sigh state and continue running normally through the sigh breath. The heart wanders even while a sigh is in progress.

### Period 1 + Random for beat-to-beat jitter

Want each heartbeat to be ±5ms off from a metronome? Configure: Heart BPM target, Up 0, Down 0, Period 1, Random shape — except that wouldn't do anything with up=0 down=0. Pick: Heart BPM target, Up 5, Down 5, Period 1, Random. Each heartbeat gets a fresh random value in the ±5 range, interpolated within that single beat's duration.

Same trick works for S1-S2 gap (beat-to-beat systole length jitter), or for any of the breath segments (cycle-to-cycle pause-length jitter etc.).

### RSA depth wander

To make the RSA coupling itself feel alive rather than mechanically constant, set slider 54 to RSA depth (target 6), give it a small up amount (e.g. 2 BPM) and a long period (e.g. 20 breath cycles). The RSA depth slowly wanders over the course of ~20 breaths, deepening and shallowing — matches real physiology where RSA strength rises with relaxation and decreases with tension.

---

## Notes worth knowing

- **Drift configurations persist across project save/load** via `@serialize`. All 7 targets' configs are written into the project file (about 30 numeric values total — negligible storage). Reopening a project restores every target's drift settings, not just the last-edited one.
- **`ext_noinit = 1`** at the top of `@init` keeps the drift memory banks alive across transport play, so configured drifts don't reset every time you press the play button.
- **Drift phases have small random offsets at @init** so the 7 drift waves don't all start at zero crossings in sync — first-listen feel is more organic.
- **The selector counts as a slider edit** in REAPER's automation sense. If you change target via slider 54, sliders 55-58 will fire `slider_automate` callbacks as their values change. This is intended — it lets the slider state stay accurate for save/restore.
- **Heart BPM drift modulates effective BPM**, which means it interacts with Speed Ramp (multiplied together for the heart's final rate) and with RSA (added together). The display BPM remains your slider 1 value; the drift offset is applied at the audio path layer.
- **Solo and Volume affect drift output the same way they affect normal output** — drift doesn't bypass any layer mixing.

---

## Limitations and known behavior

- **A single Shape per target.** Each target's shape (Sine / Triangle / Random) is stored independently, but within a target you pick ONE shape. There's no "Sine on Up, Triangle on Down" combo — the same shape governs the full wave.
- **Drift up/down range is 0-50.** This covers Heart BPM (BPM), S1-S2 gap (ms), RSA depth (BPM), and breath segments (seconds) comfortably. The unit changes per target — the range stays the same. If a target genuinely needs more than 50 units of swing, the slider's range cap won't allow it; this is a deliberate tradeoff for keeping a single slider definition that fits every target.
- **Sigh and drift compose multiplicatively, not as separate visible layers.** Drift wanders the segment lengths; sigh multiplies the current drifted lengths by slider61 at state entry. There's no separate "sigh wave" you can examine independently — sigh is just "this breath gets bigger." If you want to test sigh shape in isolation, set all drift up/down to 0 first so only the baseline segment values are scaled by the sigh.
- **First-load defaults.** Targets that haven't been configured yet hold zeros (no drift). This means the first time you open v3, all seven targets show 0 up / 0 down / period 8 / shape Sine — nothing wanders until you start configuring.

---

*Womb Sound Generator v3 is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

# Polyrhythm Phase

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Polyrhythm Phase is a binaural oscillator with up to eight simultaneous voices, each tuned to a specific musical pitch. Each voice generates a stereo pair of oscillators with a slight frequency offset between the left and right channels — the binaural beat — producing entrainment tones that shift in perceived frequency as the beat interacts with the listener's auditory system. A shared tremolo envelope modulates the amplitude of all voices, with per-voice drift or independent rate options creating polyrhythmic relationships between them. A pan modulation system adds either continuous spatial movement (Tremolo / Increment) or static spread positions (Spread / Spread Reversed) per voice.

The plugin generates no audio from an input signal. It is a pure synthesizer.

---

## Signal Architecture

Each active voice runs two oscillators — one for the left channel at the voice's base frequency, one for the right channel at the base frequency plus the binaural beat offset. Both oscillators use the same waveform. The tremolo LFO modulates their shared amplitude using a gated envelope with configurable attack and release shapes. Per-voice gain is applied before the voice's contribution is summed into the output.

All active voices are summed and normalized by the active voice count, keeping the output level consistent regardless of how many voices are enabled.

When pan is enabled, each voice's left and right oscillator outputs are panned independently using separate amplitude multipliers, preserving the binaural beat relationship between channels. The left channel signal is scaled by the cosine of the pan position and the right by the sine, maintaining constant power across the field.

---

## Parameters

### Global Controls

**Tremolo Mode** `Drift / Independent`
Sets how each voice's tremolo rate is determined.

- **Drift** — all voices share a single global rate (set by Rate Value and Rate Mode), with each voice adding its own Drift / Rate value as an offset. A voice with a drift of +5 runs slightly faster than the global rate; one with -5 runs slightly slower. This creates organic polyrhythmic drift from a common tempo anchor.
- **Independent** — the global Rate Value is hidden. Each voice's Drift / Rate slider sets that voice's tremolo rate directly in the units selected by Rate Mode. Voices can run at entirely different rates with no shared reference.

**Rate Mode** `BPM / Seconds / Hz`
Unit for interpreting rate values, both global and per-voice.

**Rate Value (Drift only)** `0.001-1000, default 60`
The global base tremolo rate, in the units set by Rate Mode. Only visible in Drift mode. Individual voice drift values are added to this.

**Binaural Beat Hz (L/R offset)** `0-100 Hz, default 4`
The frequency difference between each voice's left and right oscillators. At 4 Hz, the left oscillator runs at the voice's base pitch and the right runs 4 Hz higher, creating a 4 Hz binaural beat when heard on headphones. This value is the same for all voices simultaneously.

**On Duration % of Cycle** `0-100%, default 100`
The proportion of each tremolo cycle during which each voice is in its active state (including attack and release). At 100% the tremolo never fully closes. At 50% each voice is present for half its cycle.

**Attack % of Cycle** `0-100%, default 0`
Proportion of the on-time spent in the attack ramp, fading from silence to full amplitude.

**Release % of Cycle** `0-100%, default 100`
Proportion of the on-time spent in the release ramp, fading from full amplitude back to silence. The default of 100% with 0% attack produces a ramp-down envelope — each voice fades out across its full on-time with no hold. Adjusting both attack and release creates a shaped pulse.

> If Attack % + Release % exceeds 100% of the on-time, both are scaled down proportionally so their sum fits within the on-duration.

**Attack Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve shape applied to the attack ramp.

**Release Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve shape applied to the release ramp.

**Depth dB** `-60-0 dB, default -6`
How far each voice drops in amplitude at the bottom of its tremolo cycle. At 0 dB there is no tremolo depth. At -60 dB voices are effectively silenced at the trough.

**Tuning Reference Hz** `400-480 Hz, default 440`
The reference pitch used to calculate all voice frequencies. At 440 Hz, A4 = 440 Hz and all other pitches follow standard equal temperament from that anchor. Adjusting this shifts all voices simultaneously without changing their relative intervals.

---

### Per-Voice Controls (Voices 1-8)

Each voice has five parameters. By default V1 is audible (Gain -6 dB, Active On), V2 is active but silent (Gain -60 dB, Active On — counted in normalization but contributes nothing audibly until you raise its gain), and V3-V8 are inactive (Active Off — bypassed entirely with no CPU cost).

**Vn Gain dB** `-60 to +6 dB, default -6 for V1 and -60 for V2-V8`
Per-voice output level applied before the voice is summed into the mix. -60 dB is effectively silent. Use this to balance voices relative to one another. To fully cut a voice with no CPU cost, prefer Vn Active = Off rather than gain at -60.

**Vn Semitones** `-1000 to +1000, default 0`
The voice's pitch offset in semitones from the global Base Note + Center Octave anchor. 0 plays the anchor pitch; +12 plays one octave up; -7 plays a fifth down. The left oscillator runs at this resulting frequency; the right oscillator runs at the same frequency plus the Binaural Beat Hz offset.

**Vn Drift / Rate** `-1000 to +1000, default 0`
In Drift mode: an offset added to the global Rate Value to determine this voice's tremolo rate. Positive values make the voice run faster than the global rate; negative values slower. 0 means the voice runs at exactly the global rate.
In Independent mode: this voice's tremolo rate directly, in the units set by Rate Mode.

**Vn Phase Offset** `-1000 to +1000, default 0`
When this voice becomes audible within its tremolo cycle, in the units set by Rate Mode (BPM = beats, Seconds = seconds, Hz = cycles). Offset 0 fires the voice immediately at playback start; offset 8 in Seconds mode means the voice waits 8 seconds before becoming audible. Values wrap freely — there is no clamping.

**Vn Active** `Off / On, default On for V1 and V2, Off for V3-V8`
Enables or disables the voice. Off bypasses oscillator computation entirely (no CPU cost) and excludes the voice from the active-voice normalization count.

---

### Waveform

**Waveform** `Sine / Triangle / Saw / Golden TS / Golden SG / Golden GS / Bell / Wavefold / Half-sine / Phi-cascade / Phi Triangle / Phi Sine`
The oscillator waveform used by all voices simultaneously.

> **A note on the Golden / Phi family.** Polyrhythm Phase shipped with three "Golden" waveforms whose audible behavior didn't match the names a strict reading would expect — slot 3 ("Golden TS") was a phi-warped sine, not a phi-warped triangle; slot 4 ("Golden SG") added an extra sine pre-warp before the phi-warp. Those sounds are preserved here as Golden TS / SG for back-compat with existing projects. The two **Phi Triangle / Phi Sine** slots at the end of the list are the strict-reading versions (phi-warp into triangle, and phi-warp into clean sine with no pre-warp) — pick those if you want the cleaner interpretations.

- **Sine** — pure sinusoidal tone. Cleanest binaural beat interaction, no harmonics.
- **Triangle** — bipolar triangle wave with odd harmonics, softer than saw.
- **Saw** — sawtooth wave with a full harmonic series. Rich and bright.
- **Golden TS** — a sine wave whose phase is warped using the golden ratio (φ ≈ 1.618): phase split at the 1/φ point, each segment remapped to half a cycle. Produces an asymmetric sine with a slight kink at the warp point. (For the triangle-output reading of the same warp, see Phi Triangle.)
- **Golden SG** — a sine wave whose phase is first remapped through a cosine-shaped pre-warp, then passed through the same golden-ratio warp as Golden TS, then taken through sine. The double pass adds harmonic content the no-prewarp version doesn't have — brighter and more textured. (For the no-prewarp version, see Phi Sine.)
- **Golden GS** — the oscillator phase is self-modulated: the phase is offset by `(1/φ) · sin(phase) / 2π` before the sine function is applied. Creates a continuously self-warping waveform whose harmonic content shifts subtly with frequency.
- **Bell** — additive partials at integer harmonics (1×, 2×, 3×, 4×, 6×) with bell-leaning amplitude weights. Produces a tonal-rich, slightly metallic voice that shimmers under tremolo. Not a true singing-bowl (those use inharmonic partials, which would create discontinuities at each phase wrap), but bell-flavoured in spirit.
- **Wavefold** — sine-of-sine with index 2: `sin(2 · sin(phase))`. A gentle wavefolder — the sine "warms" without any harsh edges, adding mild harmonic content. Stays in the [-1, +1] range naturally; no clipping artifacts. Good when Sine feels too pure.
- **Half-sine** — full-wave rectified sine remapped to bipolar (`2 · |sin(phase)| − 1`). Even-harmonic-only character, hollow and vaguely reedy. Distinct from any of the other waveforms here. **Sounds an octave higher than the same note + Center Octave setting would on any other waveform in this list.** This isn't a tuning bug — full-wave rectification produces a spectrum with no fundamental and its lowest partial at 2× the carrier frequency, so the perceived pitch is one octave up by design. To match the pitch you'd hear on Sine / Triangle / etc., drop the Center Octave by 1 (or each per-voice Semitones by 12). To stack a Half-sine drone an octave above another waveform, run this plugin on a second track with a different Waveform selection — Polyrhythm Phase plays one global waveform per instance, so cross-waveform stacking is a multi-track move, not a per-voice one. Also carries a small DC offset (mean ≈ 0.27) which speakers don't reproduce; tremolo and pan attenuate it further.
- **Phi-cascade** — additive harmonics with golden-ratio-decreasing amplitudes: `fundamental + (1/φ)·2nd + (1/φ²)·3rd`. On theme with the Golden TS/SG/GS family but uses pure additive synthesis rather than phase warping. Gives a brighter, more "stacked" character than the phase-warped Goldens.
- **Phi Triangle** — golden-ratio phase warp (same as Golden TS) fed into a TRIANGLE output instead of a sine. Brighter and harmonically richer than Golden TS — triangles carry odd harmonics that the sine-output version smooths over.
- **Phi Sine** — golden-ratio phase warp (same as Golden TS) fed into a clean sine output, with **no** sine pre-warp. The minimalist version of Golden SG: same warp shape, no added prewarp brightness.

---

### Pan

**Pan Enabled** `Off / On`
Enables per-voice pan modulation. When on, each voice is panned independently using a sine LFO before being summed into the output. When off, all pan controls are hidden and voices sum directly to their L/R oscillator channels.

**Pan Mode** `Tremolo / Increment / Spread / Spread Reversed`
- **Tremolo** — each voice's pan LFO runs at the same rate as that voice's tremolo LFO. The pan and amplitude modulation are locked in phase.
- **Increment** — all voices use a shared Pan Base Rate as their pan foundation, with each voice's rate offset by Pan Increment × voice index. Voice 1 pans at the base rate, voice 2 at base + 1×increment, voice 3 at base + 2×increment, and so on.
- **Spread** — *static* positions, no LFO motion. Active voices are ranked and placed evenly across the stereo field. With four active voices you get four evenly spaced positions; with two active voices, hard left and hard right (scaled by Pan Spread %); with one active voice, dead center. The lowest-numbered active voice goes leftmost. Pan Base Rate and Pan Increment have no effect.
- **Spread Reversed** — same as Spread but with the order flipped: the lowest-numbered active voice goes rightmost.

**Pan Spread %** `0-100%, default 100`
Scales the width of pan movement (or for Spread / Spread Reversed, the maximum distance from center). At 100% panning reaches hard left and hard right. At 0% all voices remain centered regardless of mode.

**Pan Base Rate** `0.001-1000, default 60`
Base rate for pan movement in Increment mode, in the units set by Rate Mode.

**Pan Increment per Voice** `-1000–+1000, default 0`
The per-voice rate offset in Increment mode. Each successive voice's pan rate is offset by this amount from the previous. Setting a positive value spreads voices across different pan speeds; a negative value reverses the direction of the spread.

### Direction & Reverse

**Direction & Reverse** `Forward / Reverse — permute / Reverse — time / Both — permute / Both — time`

Selects how the eight-voice palette is read.

- **Forward** — default. 8 voices play in their natural order, tremolo phase advancing forward.
- **Reverse — permute** — 8 voices with **drift values mirrored** V1↔V8, V2↔V7, V3↔V6, V4↔V5. Notes, gains, phase offsets, and active flags stay where you put them — only the cadences swap. With drift values that increment linearly (e.g. 0.00 → 0.35 ascending), this turns the cadence into 0.35 → 0.00 descending: the low note now fires at the high cadence and the high note fires at the low cadence. Swapping the *entire* voice identity together would be a mathematical no-op (the audio sum doesn't care which slot a voice lives in), which is why this slider mirrors just the drift values — that's what produces an audible reordering.
- **Reverse — time** — 8 voices. Voice settings unchanged; tremolo phase decrements instead of incrementing. For symmetric envelopes (equal attack and release) the audible result is the same as Forward. For asymmetric envelopes the gate "breathes" the opposite way — attack 0% / release 100% becomes a slow fade-in into an abrupt cut-off.
- **Both — permute** — 16 voices. Forward layer (slots 0–7) plays unchanged. A second layer (slots 8–15) plays the same notes/gains/offsets with drift values mirrored. Each note now fires at **two different cadences across the two layers** — at the fast end you get harmonic pairs pulsing together, at the slow end you get single notes spaced apart.
- **Both — time** — 16 voices. Forward layer (slots 0–7) plays unchanged. A second layer (slots 8–15) plays the same V1..V8 settings but with tremolo phase decrementing. With an asymmetric envelope (attack 0 / release 100), the reverse layer fades *in* exactly when the forward layer fades *out* — the pulses cancel into a continuous drone with no silent gaps.

In any Both mode, Pan Mode = Spread or Spread Reversed ranks all 16 active voices across the stereo field rather than 8 + 8 stacked, so you hear a wider distribution. Pan Mode = Increment continues the per-voice pan-rate ramp past slot 7 into slots 8–15.

**Reverse Drift Offset** `-1000–+1000, default 0`

Visible only when Direction & Reverse is set to a Both mode. Adds a constant to every drift value in the reverse layer (slots 8–15) before tremolo rates are computed. With offset = 0 the reverse layer's per-voice cadences match the forward layer's exactly (mirrored in Both — permute, identical in Both — time), so the two layers run roughly in lockstep. Non-zero values shift the reverse layer's drift range away from the forward layer's, breaking the lockstep and giving each layer its own polyrhythmic palette from a single plugin instance.

In single-layer modes the slider hides because adding a constant to every drift value would be mathematically identical to adjusting the global Rate Value — a duplicate control would just confuse.

**Replacing multi-track stacks.** If you previously layered two tracks of this plugin with shared notes but different drift palettes (e.g. one track with drift values 0.00 → 0.35 ascending and a second track with 1.55 → 1.20 descending), one instance with Direction & Reverse = Both — permute and Reverse Drift Offset = 1.20 produces the same audible result from a single track. The mirror brings the descending pattern; the offset brings the rate range. Use Both — time when you want parallel-ascending pairing instead (both layers ascending in drift, one playing forward and one backward in time).

### Start Delay

**Start Delay** `0–1000, default 0`

How long the plugin sits silent at the start of playback before voices begin. Units match Rate Mode: BPM mode counts in tremolo cycles of the global Rate Value (so 4 with Rate Value = 60 BPM = 4 cycles = 4 seconds), Seconds mode is literal seconds, Hz mode counts in cycles of the global Rate Value. 0 disables the delay entirely.

During the delay window the voice loop is skipped — phases stay frozen at their play-start reset positions. When the delay elapses, voices begin from phase 0 (or their per-voice Phase Offsets) rather than from a mid-cycle position. So if you set V1 Phase Offset = 2 seconds and Start Delay = 4 seconds, V1 first fires at t = 6 seconds (4 seconds of silence, then V1's own 2-second wait counted from there).

Re-arms on every transport stop/start, so each playback run begins with a fresh silent window.

### Play / Rest Gating (v2)

**Play for (cycles)** `0–1000, default 0`
**Rest for (cycles)** `0–1000, default 0`

A per-voice cyclic gate. Each voice plays for **Play for** cycles of its own tremolo rate (global rate + per-voice Drift), then goes silent for **Rest for** cycles of the same per-voice rate, then resumes. Because counting is per-voice, voices with different Drift settings enter and leave rest at different real-time moments — V8 at Drift 3.5 reaches its 4-cycle play threshold in less wall-clock time than V1 at Drift 0, and V8 wakes earlier from rest for the same reason. The "loop" lives in each voice's own cadence; the rhythmic identity you hear comes from how the voices' independent play/rest cycles interlock.

The feature is **disabled when either slider is 0** (the default). With both at 0, polyrhythm_phase behaves exactly like v1 — no gating, no behavior change.

**The release of the final cycle reaches actual silence.** Normally the Depth dB slider sets an always-on floor under the tremolo — at the default -6 dB, the LFO modulates between roughly 50% and 75% gain and never goes quiet. That floor would make the gate's rest entry sound like a soft thud (50% → 0% in ~15 ms). The gate's final cycle drops that floor during the release portion of the LFO, so the release tail decays all the way to 0 and the rest freeze lands on actual silence. Cycles 1 through (Play for − 1) keep the normal Depth-floored shape; only the last release changes.

**Use a non-zero Release setting** for the clean rest entry this feature is designed for. Release = 0% has zero release-zone width, so the depth-floor override never fires and you get a sharp cutoff at the rest boundary instead of a glide to silence.

**Wake from rest is handled by the same 3 ms gain smoother** that prevents Attack = 0% from clicking at normal cycle starts. When a voice's rest counter expires, target gain jumps from 0 back to whatever the LFO says, and the smoother ramps gain_l/gain_r over ~3 ms — perceptually a clean attack, not a click. No special wake-side logic needed.

**Transport behavior** is conventional: pressing stop silences the plugin, pressing play re-initializes everything (voice phases, Start Delay counter, per-voice cycle counters, resting flags). Every play press starts a fresh play period from voice cycle 0. Same behavior as without the gate engaged.

### Speed Ramp

In-plugin slowdown/speedup over time. User-facing form: a signed `by` amount on the base Rate Value slider 3 (in the rate's currently-displayed unit). Internally, that delta is converted to a multiplicative ratio that scales **every voice's tremolo + pan + cycle-counter advance** — so the whole polyrhythm stretches or compresses while preserving the rate RELATIONSHIPS between voices.

**Speed ramp by (slider 65)** `-1000 to +1000, step 0.001, default 0`
Signed delta on the base rate (slider 3). **0** = no change. The delta is interpreted in the rate's currently-displayed unit (BPM / Seconds / Hz). Example: at slider 3 = 60 BPM, `by -30` ramps slider 3's effective value from 60 → 30. All voices scale by the same ratio (0.5), so V2's 60.5 ramps to 30.25, etc. The slow beat between them slows proportionally — the polyrhythm feel is preserved.

In BPM/Hz modes, negative `by` = slower. In Seconds mode (period), positive `by` = slower (longer period).

**Independent mode note:** slider 3 isn't used for audio in Independent mode (each voice has its own rate), but it's still used as the reference for `by` interpretation. Set slider 3 to a sensible reference value if you're in Independent mode — the resulting ratio applies to all voices.

**Speed ramp duration (slider 66)** `0–60 minutes, default 0` · **Speed ramp engage (slider 67)** `Off / On, default Off` · **Speed ramp start delay (slider 68)** `0–60 minutes, default 0`

Engage is a freeze/resume gate (NOT a restart edge): while On, ramp_t advances 0 → 1 over the duration; while Off, ramp_t freezes and resumes from there on re-engage.

**Tuning and binaural beat are unaffected** — only the modulation rates scale, not the audible pitch.

**Transport behavior:** every play press re-initializes everything (voice phases, Speed Ramp progress, etc.). This is the ONLY thing that resets ramp_t — slider changes don't.

**Migration from v2.7:** slider 65 changed from multiplier (0.1–4.0) to signed delta. Old projects' multiplier value interprets as a tiny delta — Speed Ramp effectively "off" until reconfigured.

### Drift

Slow organic wander applied polyrhythm-wide on top of Speed Ramp — every voice's tremolo speeds up and slows down in step, preserving the rate relationships between voices while the underlying pulse breathes. See [Per-Plugin Drift](#per-plugin-drift) for the architecture; the seven sliders below configure it for this plugin.

**Musical Period (cycles)** `1–256, default 32`
Period of the musical drift source, measured in cycles of the global Rate Value. Scales with Speed Ramp.

**Musical Up by** `0.0–1.0, default 0`
How far above the center rate the musical drift wanders at its peak, as a multiplier amplitude applied to every voice's tremolo together.

**Musical Down by** `0.0–1.0, default 0`
How far below the center rate the musical drift wanders at its trough. Independent from Up by.

**Slow Period (minutes)** `0.1–60, default 5`
Period of the slow drift source, measured in wall-clock minutes. Does NOT scale with Speed Ramp.

**Slow Up by** `0.0–1.0, default 0`
Above-center amplitude for the slow drift source.

**Slow Down by** `0.0–1.0, default 0`
Below-center amplitude for the slow drift source.

**Shape** `Sine / Triangle / Random, default Sine`
Wander shape applied to both sources.

---

## Usage Notes

- **Active voice count determines normalization.** The output is divided by the number of active voices each sample, keeping overall level consistent. Enabling or disabling voices mid-playback will change the level slightly as the normalization adjusts.
- **Binaural Beat Hz applies to all voices uniformly.** All voices have the same L/R frequency offset. There is no per-voice binaural beat amount.
- **Playback start resets all phases.** Oscillator phases, tremolo phases, and pan phases all reset to zero when playback begins from a stopped state. This ensures consistent behavior from the same starting point.
- **Rate Mode applies to both tremolo and pan rates.** Both the voice tremolo rates and the Increment mode pan rates are interpreted in whatever unit Rate Mode specifies.
- **Phase Offset means "when does this voice become audible," not a raw phase shift.** An offset of 8 on a 16-second cycle means the voice fires at second 8. An offset of 0 fires immediately. Offsets wrap freely — an offset of 16 on a 16-second cycle is the same as 0.
- **On Duration % and voice count must be coordinated to avoid overlap.** On Duration sets how much of each cycle a voice is present. With multiple voices spaced across a shared cycle, each voice needs enough room to fit without overlapping its neighbors. The safe maximum On Duration for evenly-spaced voices is `100 ÷ number of active voices` percent. For example: 2 voices = 50% max, 3 voices = 33% max, 4 voices = 25% max. Exceeding this will cause voices to overlap at the boundaries regardless of how offsets are set. To space voices evenly, divide the cycle length by the number of voices and use that as the offset step — e.g. 3 voices on a 12-second cycle: offsets of 0, 4, and 8.
- **Offsets don't have to be perfectly even — spacing voices closer together creates overlap, spacing them further apart creates silence between them. Both are valid creative choices.** In Seconds mode this is especially concrete: with a 16-second cycle, On Duration 50%, and two voices, an offset of 8 produces a clean handoff — V1 plays seconds 0–8, V2 plays seconds 8–16. An offset of 7 causes one second of overlap at the boundary. An offset of 9 leaves a one-second gap of silence between them. The relationship is direct: offset in seconds is exactly when V2 becomes audible.
- **When building sequential voice patterns, set Rate Value to `voice duration × number of voices`.** This ensures the cycle fills exactly with no gaps or overlap. For example: 4 voices each lasting 4 seconds requires a rate of 16 seconds, with offsets at 0, 4, 8, and 12. 4 voices each lasting 6 seconds requires a rate of 24 seconds, with offsets at 0, 6, 12, and 18. On Duration % should be set to `100 ÷ number of voices` to match.
- **Spread and Spread Reversed are static, not modulated.** Voices stay locked to their assigned positions across the stereo field for as long as the active set doesn't change. Toggling a voice's Active state will redistribute the positions of the others (the rank-among-active is recalculated each time). Pan Spread % scales how far from center those positions extend.

---

*Polyrhythm Phase is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

# Melody Phase

**Designed by Rozaya — Developed with Claude (Anthropic)**

## Overview

A step-sequencer melody synth, sibling to Polyrhythm Phase. Up to 8 voices participate in a sequence; each voice plays a single note (a configurable number of semitones from the root) for its own *Next voice in* duration, then hands off to the next active voice. Each voice has its own *Note duration* duration controlling how long its note actually sounds — when "Note duration" is longer than "Next voice in," the voice's release continues in parallel with the next voice's attack (overlap / phrasing). When "Note duration" is shorter than "Next voice in," there's a rest before the next voice enters. When they're equal, the handoff is clean and sequential.

Inactive voices are skipped in the sequence entirely. To insert a rest in the sequence (a silent step), leave a voice Active and set its "Note duration" to 0 — the voice contributes silence for its "Next voice in" duration, then hands off, with no click on entry or exit.

Beyond the core sequencer:

- **Per-voice pan** with four modes (Tremolo, Increment, Spread, Spread Reversed) — Spread is especially useful for melody since each active voice gets a fixed position across the stereo field, making the line easy to track spatially.
- **Glide / portamento** — pitch slides between voices over a configurable duration. Independent of all other timing.
- **Legato glide** — when on, the whole sequence becomes one continuous tone whose pitch slides between voices, with no attack / release ceremony at the boundaries. The pan smoother also slows to match the glide time so pitch and pan transition as one coherent slide.

The waveform list (10 options), envelope shapes, tuning math, binaural beat, and pan section are all carried over directly from Polyrhythm Phase. Both per-voice timing sliders are expressed in cycles of the global rate, so rhythmic relationships line up — V1 set to 2 cycles, V2 set to 1 cycle, V3 set to 0.5 cycles will line up cleanly against the same rate.

## Signal Architecture

Each voice runs two oscillators (one for L, one for R). The R oscillator's frequency is offset from the L oscillator's by the binaural beat value (in Hz). When binaural beat is 0, L and R are identical and the voice sums to mono.

A sequencer index tracks which voice is currently "in its step." When that voice's *Next voice in* elapses, the index advances to the next active voice and triggers its envelope attack. The outgoing voice's envelope keeps running through its own (longer or shorter) *Note duration* independently — that's where overlap comes from. Up to 8 voices can be in non-silent states simultaneously during overlapping phrasing.

The envelope is a four-segment state machine: attack → sustain → release → silent. Each segment respects the voice's *Note duration*: Attack % and Release % set how much of the note duration is attack and release; sustain fills the middle. If Attack% + Release% would exceed 100%, both are scaled proportionally to fit. The output amplitude passes through a one-pole exponential smoother (~3ms time constant) before reaching the oscillator, so even instantaneous envelope transitions (attack% = 0 or release% = 0) come out click-free.

When Glide time > 0, each new voice's frequency starts at the previous voice's target and slides toward its own target via a one-pole smoother. Multiple voices can be in different sliding states simultaneously during overlap.

When Legato glide is on, the sustain → release transition is suppressed — each voice rings continuously from its trigger until the sequencer's next hand-off silences it via inheritance. The new voice inherits the previous voice's envelope value, oscillator phase, and pan position, so amplitude, waveform, and stereo position are all literally continuous across the boundary — only the pitch slides via glide. The first note still attacks normally; the last note (when Loop = Off and the sequence ends) releases normally. The pan smoother slows to match the glide time so pitch and pan transition together.

When Loop is on, the sequence wraps from the last active voice back to the first. When off, the sequence plays through once and stops.

## Parameters

### Global

**Rate Mode** `BPM / Seconds / Hz` (default Seconds)
How to interpret Rate Value. **Seconds** = seconds per cycle; with Rate Value = 1 (also the default), one cycle equals one second, so the per-voice "Next voice in" and "Note duration" numbers behave as raw seconds. This is the easiest way to work in plain time — set a voice to 2 and it plays for 2 seconds. **BPM** = beats per minute; Rate Value becomes the tempo, and the per-voice numbers become beats. Useful if you want a polyrhythmic feel where every voice is in a sensible ratio of a common tempo. **Hz** = cycles per second; Rate Value is the cycle frequency. Useful for very slow ambient pacing (Rate = 0.05 Hz means one cycle every 20 seconds).

**Rate Value** `0.001 – 1000`
The global rate. Meaning depends on Rate Mode (see above). Default 1, which in the default Seconds mode means "each per-voice cycle is one second."

**Waveform** `Sine / Triangle / Saw / Golden TS / Golden SG / Golden GS / Bell / Wavefold / Half-sine / Phi-cascade / Phi Triangle / Phi Sine`
Same set as Polyrhythm Phase — see that plugin's Waveform section for descriptions, including the back-compat note on the Golden / Phi family. Note that Half-sine sounds an octave higher than the others at the same note + Center Octave setting (full-wave-rectified spectrum has no fundamental).

**Tuning Reference Hz** `400 – 480`
Frequency of A4. Standard concert pitch is 440.

**Root Note** `C / C# / D / D# / E / F / F# / G / G# / A / A# / B`
The base note. Each voice's Semitones field is relative to this.

**Center Octave** `0 – 8`
Octave of the root note. With Root Note = A and Center Octave = 4, the base frequency is A4 = 440 Hz (at default tuning).

**Loop** `Off / On`
When on, the sequence wraps from the last active voice back to the first. When off, the sequence plays one full pass and stops.

**Master Gain dB** `-60 – 0`
Output level for the whole plugin.

**Binaural Beat Hz** `0 – 100`
Hz offset added to the right-channel oscillator only. 0 disables the effect and the plugin sums to mono. Same shape as Polyrhythm Phase's binaural beat.

**Attack % of Note duration** `0 – 100`
What fraction of each voice's *Note duration* is taken up by the attack ramp.

**Release % of Note duration** `0 – 100`
What fraction of each voice's *Note duration* is taken up by the release ramp. If Attack% + Release% exceeds 100%, both are scaled proportionally to fit the note duration.

**Attack Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve of the attack ramp. Cosine is the smoothest perceptually; Linear is the most "musical-instrument-like."

**Release Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve of the release ramp.

**Sequence Length** `All Active / 1 / 2 / 3 / 4 / 5 / 6 / 7 / 8`
How many voice slots participate. "All Active" walks all 8 slots, skipping any with Active = Off. A numeric setting truncates the sequence to the first N voice slots (still skipping any inactive within that range). Useful for shortening a sequence without having to flip Active toggles.

### Pan (sliders 15-19)

Mirrors Polyrhythm Phase's pan section. When enabled, each voice gets independently-positioned L and R amplitudes — the binaural beat is preserved across the pan because each channel keeps its own oscillator. Pan Mode picks one of four behaviors.

**Pan Enabled** `Off / On`
Toggles the whole pan group. When off, voices sum straight to mono (and the sub-sliders below are hidden in Reaper). Default Off.

**Pan Mode** `Tremolo / Increment / Spread / Spread Reversed` (default Spread)
- **Tremolo** — each voice's pan position oscillates over time at Pan Base Rate. All voices share the same rate.
- **Increment** — each voice's pan rate is Pan Base Rate + (voice index × Pan Increment), so V1, V2, V3… all pan at slightly different rates and drift in and out of phase.
- **Spread** — voices get static pan positions ranked across the stereo field. V1 sits at one end, V8 at the other, the rest spread evenly between. Active voices only; inactive ones are skipped in the ranking. **Most useful for melodies** — each note in the sequence lives in a distinct spatial position, which makes the line easy to follow.
- **Spread Reversed** — same as Spread but flipped. Pairs nicely with another instance set to Spread for compositional stereo width.

**Pan Spread %** `0 – 100`
How wide the pan moves. 100 = full stereo. 0 = collapses to center (effectively defeats pan).

**Pan Base Rate** `0.001 – 1000` (Tremolo / Increment modes only)
Pan LFO rate, in the same units as the global Rate Mode. Hidden when pan is off or when Pan Mode is Spread / Spread Reversed.

**Pan Increment per Voice** `-1000 – 1000` (Increment mode only)
How much each successive voice's pan rate increases over the previous voice's. Hidden in other modes.

### Glide / portamento (sliders 20-21)

**Glide time (seconds; 0 = off)** `0 – 5`
When > 0, each new voice's pitch starts at the previous voice's target frequency and slides to its own target over this many seconds. 0 = no glide; voices jump directly to their pitch. Independent of all other timing — set Glide to 0.05 and notes will slide quickly into pitch from wherever the last one was, regardless of *Next voice in* or *Note duration*.

**Legato glide** `Off / On`
- **Off** (default) — each voice has its own attack and release. Glide bends the pitch *during* each note; you hear each voice as a distinct envelope event at the hand-off (attack ramp on the new note, release ramp on the old). Good for plucky / articulated melodies where each note should feel separately spoken.
- **On** — the whole sequence becomes one continuous tone whose pitch slides between voices. The first note attacks normally; every subsequent hand-off skips the attack and inherits both the envelope value and the oscillator phase from the previous voice; pitch slides via glide. The previous voice's "Note duration" is effectively ignored — voices ring continuously until the next one takes over (which silences the previous one). The last note (when Loop = Off and the sequence ends) releases normally. **Rests still work** — a voice with Note duration = 0 doesn't trigger a hand-off, so the previously-ringing voice keeps holding through the rest's step time (which is what "continuous tone with no rest" sounds like in this mode — if you want actual silences in Legato mode, use Active = Off to skip a voice slot entirely).

Good for legato / flowing melodies where you want one bending tone instead of articulated steps. Set Glide time > 0 to actually hear the pitch slide; with Glide = 0 + Legato On, the pitch jumps between targets but there's still no attack ceremony.

### Per Voice (V1–V8)

**Vn Semitones from root** `-24 – 24`
This voice's note, in semitones above (positive) or below (negative) the global Root Note + Center Octave.

**Vn Next voice in (cycles)** `0.01 – 16`
How long until the sequencer hands off from this voice to the next active one, in cycles of the global rate. Controls *sequence timing* — when does V[n+1] start? Vn's own note may continue ringing past this handoff (overlap) or end before it (rest), depending on the "Note duration" slider below.

**Vn Note duration (cycles; 0 = silent)** `0 – 16`
How long this voice's note actually sounds, in cycles. Controls *sound timing* — independent from sequence timing. The relationship between this and "Next voice in" is what gives the plugin its phrasing range:
- **Note duration < Next voice in** → there's silence between Vn ending and the next voice entering (rest in the sequence).
- **Note duration = Next voice in** → clean sequential handoff, no overlap, no rest.
- **Note duration > Next voice in** → Vn's release continues while the next voice plays (overlap / phrasing).
- **Note duration = 0** → Vn is a silent step (rest) of duration "Next voice in." Silent on entry and exit, no click.

**Vn Gain dB** `-60 – 6`
Per-voice level.

**Vn Active** `Off / On`
Off = this voice is skipped in the sequence entirely (not just silent — the sequence pretends it doesn't exist). On = voice participates per the Sequence Length rule above.

### Start Delay

**Start Delay** `0–1000, default 0`

How long the plugin sits silent at the start of playback before the sequencer begins. Units match Rate Mode: BPM mode counts cycles of the global Rate Value (so 4 with Rate Value = 60 BPM = 4 beats = 4 seconds), Seconds mode is literal seconds, Hz mode counts cycles of Rate Value. 0 disables the delay entirely.

During the delay the sequencer state stays frozen — when the delay elapses, the sequence begins cleanly from V1 (or the first active voice) rather than mid-step. Re-arms on every transport stop/start.

### Direction

**Direction** `Up / Down / Up-Down (repeat) / Up-Down (no repeat) / Down-Up (repeat) / Down-Up (no repeat)` (default Up)

Walk order through the active voices in the pool. The "pool" is the first *Sequence Length* slots; inactive voices within the pool are skipped in all directions.

- **Up** — voices play in slot order V1, V2, V3, ..., loop back to V1. (Default, matches the original behavior.)
- **Down** — voices play in reverse slot order V8, V7, V6, ..., loop back to V8. (With *Sequence Length* = 4, plays V4, V3, V2, V1, V4, V3, ...)
- **Up-Down (repeat)** — walks up to the highest active voice, plays it twice (the "repeat" at the turnaround), walks back down, plays V1 twice, repeats. With 4 voices: 1, 2, 3, 4, 4, 3, 2, 1, 1, 2, 3, 4, 4, ...
- **Up-Down (no repeat)** — same bounce pattern but the boundary voices play just once. With 4 voices: 1, 2, 3, 4, 3, 2, 1, 2, 3, 4, 3, ...
- **Down-Up (repeat)** — bounce starting at the top. With 4 voices: 4, 3, 2, 1, 1, 2, 3, 4, 4, 3, 2, 1, 1, ...
- **Down-Up (no repeat)** — bounce starting at the top, no repeat at edges. With 4 voices: 4, 3, 2, 1, 2, 3, 4, 3, 2, 1, 2, 3, ...

**Loop = Off interactions.** Up or Down play one full pass through the pool and stop. Bounce modes play one complete bounce cycle (start edge → other edge → back to start edge) and stop. With 4 voices, Loop=Off + Up-Down (repeat) plays 1, 2, 3, 4, 4, 3, 2, 1 and stops; Up-Down (no repeat) plays 1, 2, 3, 4, 3, 2, 1 and stops.

**Glide and Legato interactions.** Glide bends between consecutive voices in whatever direction they're going — no glide-specific changes were needed. Legato mode (no re-attack at hand-offs) works the same: each voice rings until the next one takes over, regardless of walk direction.

**Switching direction mid-playback.** Toggling between Up and Down flips the walk immediately at the next hand-off. Toggling into or out of a bounce mode picks up with the current seq_dir at the next hand-off (no glitch).

### Play / Rest Gating (v2.1)

**Play for (steps)** `0–1000, default 0`
**Rest for (steps)** `0–1000, default 0`
**Rest mode** `Walk through / Freeze in place, default Walk through`

A per-step cyclic gate. The sequencer fires **Play for** notes normally, then sits in silence for some number of steps determined by **Rest for** + **Rest mode**, then resumes — the pattern repeats forever. Useful for phrase-and-pause melodies: "play 4 notes, sit silent for 4 notes' worth of time, play 4 more."

The feature is **disabled when either of Play for / Rest for is 0** (the default). With both at 0, the sequencer behaves as before; Rest mode has no effect when the gate is off.

**Rest mode** picks one of two fundamentally different behaviors for what the sequencer does during the rest period:

- **Walk through** (default): the sequencer keeps advancing through voice handoffs during rest. Each rest step consumes that voice's *Next voice in* duration silently. The total cycle is `Play for + Rest for` steps of the underlying sequencer grid. If `Play + Rest` doesn't divide evenly into your active voice count, the starting voice of each play period walks across the melody — `Play=5, Rest=4` with 8 active voices means you hear V1–V5, walk through V6–V8+V1 silently, then V2–V6, walk through V7+V8+V1+V2, etc. Notes get "skipped" in the literal sense and reappear in subsequent play periods at different positions. Good for **abstract / drone-friendly use** where the melody loops as a backdrop and play/rest is a rhythmic gate over it.

- **Freeze in place**: the sequencer **pauses** at the voice that would have fired when rest began. Rest duration is `Rest for × that frozen voice's "Next voice in"` seconds, timed by a sample counter rather than a step count. When rest ends, the frozen voice fires and the sequence picks up from there — **no notes lost, every voice plays in order across multiple cycles, just with pauses between phrases**. Good for **melodic / phrasal use** where the sequence is meant to be heard in full and the rest is just punctuation.

**What counts as a step (Walk mode).** Each handoff between voices is one step, regardless of whether the voice produces sound. Programmed rests (a voice with Note duration = 0) still count as steps — they consume their Next voice in time and tick the step counter. "Play for = 4" plays exactly 4 sequence positions, which may include programmed rests within them.

**Rest duration is the same wall-clock time in both modes.** Because each voice has its own Next voice in, the rest period's duration depends on which voices the sequencer would have walked through during the silent stretch. Walk mode sums those naturally; Freeze mode simulates the same walk at rest entry to compute its sample-timed rest window. So `Rest for = 4` means the same wall-clock duration whether you're in Walk or Freeze, even when voices have different per-step timings. With evenly-timed voices it's just `Rest for × that duration`; with varied timings the rest length varies between cycles (because different voices get walked-through in each cycle), but Walk and Freeze stay in lock-step on the same per-cycle value.

**Tails finish naturally — except in Legato mode where we force release.** When PR transitions to rest, the previously-firing voice continues:
- **Non-Legato mode**: the voice's sustain → release happens automatically based on its own Note duration, so it tails out naturally during the start of the rest period.
- **Legato mode**: a sustaining voice doesn't auto-release (it normally only releases when the next voice's Legato handoff inherits it). To prevent the voice ringing forever during rest, it's forced into release at the rest-entry moment — same trick used when a Loop=Off sequence walks off the end. This applies in both Walk and Freeze modes.

**Glide across rest.** When the play period resumes, the new note's glide source is whatever the last triggered voice's target frequency was — same as a normal handoff. The pitch slides from the last played note into the first note of the new play period.

**Transport behavior**: conventional. Stop silences; play re-initializes everything (sequencer index, step counter, rest state) and starts fresh from the first active voice.

**Changing Rest mode mid-rest** is an edge case the code handles defensively but not gracefully — the safest move is to flip the slider while the gate is in its play period, or to press stop/play to reset cleanly. The plugin won't crash but the current rest period may stretch or compress unpredictably.

### Speed Ramp

In-plugin melody-tempo morph over time, without automation envelopes. User-facing form: a signed `by` amount on the Rate Value slider 2 (in the rate's currently-displayed unit). Internally that delta is converted to a multiplicative ratio that scales the effective dt — so the whole melody timeline stretches or compresses while voice envelope proportions (Attack %, Release %, Note duration) stay intact.

**Speed ramp by (slider 67)** `-1000 to +1000, step 0.001, default 0`
Signed delta added to the Rate Value over the duration. **0** = no change. The delta is in **the rate's currently-displayed unit** — BPM if Rate Mode is BPM, Seconds (period) if Seconds, Hz if Hz. In BPM/Hz modes negative `by` = slower melody; in Seconds mode positive `by` = slower (longer period).

**Speed ramp duration (slider 68)** `0–60 minutes, default 0` · **Speed ramp engage (slider 69)** `Off / On, default Off` · **Speed ramp start delay (slider 70)** `0–60 minutes, default 0`

Engage is a freeze/resume gate (NOT a restart edge): while On, ramp_t advances 0 → 1 over the duration; while Off, ramp_t freezes and resumes from there on re-engage.

Pan modulation also scales, so the whole melody timeline including pan motion morphs as one piece.

**Transport behavior:** speed_ramp_t resets to 0 on every transport play edge. This is the ONLY thing that resets the ramp — slider changes don't.

**Migration from v2.7:** slider 67 changed from multiplier (0.1–4.0) to signed delta in rate-units. Old projects' multiplier value interprets as a tiny delta — Speed Ramp effectively "off" until reconfigured.

### Drift

Slow organic wander applied to the melody's effective tempo on top of Speed Ramp — sequencer, voice envelopes, and pan motion all stretch together, like an unforced live player rather than a metronomic loop. See [Per-Plugin Drift](#per-plugin-drift) for the architecture; the seven sliders below configure it for this plugin.

**Musical Period (cycles)** `1–256, default 32`
Period of the musical drift source, measured in cycles of the global Rate Value. Scales with Speed Ramp.

**Musical Up by** `0.0–1.0, default 0`
How far above the center tempo the musical drift wanders at its peak, as a multiplier amplitude.

**Musical Down by** `0.0–1.0, default 0`
How far below the center tempo the musical drift wanders at its trough. Independent from Up by.

**Slow Period (minutes)** `0.1–60, default 5`
Period of the slow drift source, measured in wall-clock minutes. Does NOT scale with Speed Ramp.

**Slow Up by** `0.0–1.0, default 0`
Above-center amplitude for the slow drift source.

**Slow Down by** `0.0–1.0, default 0`
Below-center amplitude for the slow drift source.

**Shape** `Sine / Triangle / Random, default Sine`
Wander shape applied to both sources.

## Usage Notes

**Building a melody.** Start with all 8 voices set Active, give each a different Semitones value (the default spec gives a rough C major arpeggio), keep "Next voice in" = "Note duration" = 1 cycle for a clean walk. Adjust "Next voice in" per voice for rhythmic variation, "Note duration" for phrasing.

**Adding rests.** Set a voice's "Note duration" to 0. The voice still "takes up" its "Next voice in" duration in the sequence — that's the rest length. The rest is true silence: no envelope ramp, no click on entry or exit.

**Overlap for sustain.** Set "Note duration" to a value greater than "Next voice in." When the sequencer moves to the next voice, the previous voice's note keeps ringing through its release. With Release Shape = Cosine and a long Release %, this gives a gentle decaying tail under the new note.

**Click-free envelope on instant transitions.** Even when you set Attack % or Release % to 0 (sharp gate on or off), the plugin's output amplitude is passed through a one-pole exponential smoother with a ~3 millisecond time constant before reaching the oscillator — same trick Polyrhythm Phase uses. The state machine's raw envelope value can step instantly from 0 to 1 or vice versa, but what reaches the speakers ramps over a few milliseconds, which the ear hears as a clean transition rather than a click. Your user-set attack / release percentages aren't silently rewritten — if you ask for 0% you get a sharp envelope, just one that's perceptually click-free. Same applies to rest steps (Note duration = 0): the smoother fades any tail from the previous voice gracefully.

**Looping vs one-shot.** Loop = On for ambient / sleep loops where the sequence cycles indefinitely. Loop = Off for a one-shot melodic phrase that plays once on plugin activate / playback start, then goes silent.

**Pairing with Polyrhythm Phase.** Run both on separate tracks at the same Tuning Reference — Polyrhythm Phase as the sustained drone bed, Melody Phase as the melodic figure on top. Match Root Notes for consonance, or detune Melody Phase slightly for movement.

**Glide for pitch bends within notes.** With Glide time > 0 and Legato glide Off (the default), each note retains its own attack / release ceremony and the pitch bends *during* the note — you hear distinct voices that each slide pitch-wise. Useful for articulated melodies where the pitch movement is the ornament, not the structure.

**Legato glide for one continuous bending tone.** Turn Legato glide On (and set Glide time > 0) for the classic monosynth portamento sound — one ongoing tone whose pitch slides smoothly between targets, with no attack / release events at the note boundaries. Voices ring continuously (the per-voice "Note duration" is effectively ignored in Legato mode — the voice always rings until the next one takes over). The first note still attacks normally, the last note still releases normally, and rests (Note duration = 0) extend the previous voice's hold time. Works regardless of how the voices' timing sliders are set — just turn it on and the sequence becomes a smooth bending tone.

**Spread pan for melodic clarity.** With Pan enabled and Mode = Spread, each voice in the sequence gets a fixed position across the stereo field. The ear easily tracks which voice is which — V1 might be far left, V8 might be far right — and the melody feels spatially organised even if the notes themselves overlap or sit close in pitch. Pair with a second instance set to Spread Reversed (and slightly different timing) for a wider, more enveloping result.

**Pan transition follows Glide in Legato mode.** Pan position uses a one-pole smoother to slide between positions (~10ms by default — fast enough to feel snappy, slow enough to be click-free). When Legato glide is on AND Glide time > 0, the pan smoother slows down to match the Glide time — so pitch and pan transition at the same perceived speed and feel like one coherent slide. Without this, the pan finishes its 10ms slide while the pitch is still gliding for hundreds of ms, which the ear hears as a sharper-than-expected position change on top of a slow pitch bend.

---

*Melody Phase is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

# Per-Plugin Drift

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Drift adds slow, organic wandering to a plugin's rate — heartbeat, breath, tremolo, filter sweep, metronome, melody tempo, any rate-bearing plugin in the suite. A heartbeat at a perfectly fixed BPM feels mechanical over a long stretch; a real heart speeds up and slows down a little. Drift is the "it's alive" texture.

Every rate-bearing plugin in the suite carries its own Drift block — there is no separate modulator plugin, no shared mailbox, no cross-plugin routing. Each plugin's drift is self-contained: it lives in the plugin, runs in the plugin, and only affects that plugin. The trade is that you set drift per plugin instead of broadcasting one wobble to everything; the gain is that drift is guaranteed to work, with no patching to set up and nothing to forget.

(This replaces the v2.3-prototype Wobble Modulator, which used global gmem mailboxes to broadcast a single drift value to listening plugins. The mailbox approach was clever in principle but fragile in practice — wrong plugin loaded, wrong slot number, leftover values from a removed modulator. Per-plugin drift is boring and reliable.)

## How it works

Each plugin's Drift block stacks **two independent drift sources** that both modulate the same rate at the same time. They were given different time scales on purpose so they can shape the rate at two layers at once without fighting:

- **Musical drift** — its period is measured in the plugin's own cycles (heartbeats, breaths, tremolo cycles, etc.). This means musical drift **scales with the Speed Ramp** automatically — if the plugin is at half speed, a musical-drift cycle takes twice as long in wall-clock time, so the drift stays musically locked to the underlying tempo. Best for "wander that breathes with the music."
- **Slow drift** — its period is measured in wall-clock minutes. This means slow drift **does not scale with the Speed Ramp** — five minutes is five minutes regardless of what the plugin tempo is doing. Best for "long arc that doesn't care about the music," for example a 20-minute wander across a sleep session.

Each source is independent — you can set one and leave the other at 0, or run both stacked.

## Asymmetric amplitudes

Each source has separate **Up by** and **Down by** amplitudes, so the drift can wander further above the center than below, or vice versa. With Up by = 0.2 and Down by = 0.05, a heartbeat at 60 BPM wanders up to 72 BPM at the peak but only down to 57 BPM at the trough — useful when you want the wander to feel like "occasional surges" rather than "even sway."

Symmetric drift (Up by = Down by = 0.1) wanders equally either way, like a sine around the center.

## Shape options

A single Shape control sits across both drift sources:

- **Sine** — smoothest. Continuous rounded wander, no corners. The safe default.
- **Triangle** — same envelope as Sine but with linear rises and a defined peak/trough corner. Feels slightly more deliberate; subtle distinction at slow periods.
- **Random** — value-noise. The drift picks a random target within the amplitude range and slews smoothly toward it, then picks a new random target, then slews. The result is a slow, unrepeating, smooth wander rather than a clean periodic shape. Good when periodic wobble starts to feel predictable on long sessions.

## Defaults are off

Every Drift amplitude slider defaults to 0. Drift is **opt-in** — set Up by and/or Down by on at least one source to a non-zero value to engage it. With Up by = 0 and Down by = 0 the source does nothing, regardless of period or shape.

Set both sources' Up by and Down by to 0 to turn drift off entirely.

## Where to find it

Every rate-bearing plugin in the suite has a **Drift** subsection in its own parameters. See the per-plugin sections below for the seven sliders in each plugin's Drift block. The slider names, defaults, and behavior are identical from plugin to plugin — only the rate being modulated differs.

---

*Per-Plugin Drift is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

# Full Feature Sweeping Filter

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Full Feature Sweeping Filter is a resonant lowpass filter with a shaped LFO sweep, stereo phase control, wet/dry mixing, and an optional pan modulation system. The filter cutoff is driven by a gated LFO envelope with independently shaped attack and release curves — the same envelope architecture used in the Full Feature Tremolo — giving precise control over how the cutoff moves through the frequency range on each cycle. A wet/dry mix allows the effect to be blended with the dry signal.

The plugin processes incoming stereo audio.

---

## Signal Architecture

The LFO runs as a normalized phase per channel. Each cycle, the LFO output moves through an attack ramp, a hold-high region, a release ramp, and a hold-low region, all with configurable proportions and curve shapes. The LFO output (0-1) is mapped to the frequency range, then scaled by the Depth % parameter around the center frequency, so at less than 100% depth the sweep covers a narrower band centered between Low and High.

The resulting target frequency is converted to a filter coefficient using a linear mapping (`freq * 2 / srate`) and smoothed with a 3 ms lag before being applied to a two-pole resonant lowpass filter on each channel independently. The wet output is then blended with the pre-filter dry signal according to the Wet/Dry Mix.

Left and right channels have independent LFO phase counters. In **Independent L+R** mode both advance freely. In **Offset from L** mode the right channel phase is continuously derived from the left plus the phase offset.

---

## Parameters

### Filter Range

**Frequency Low Hz** `20-20000 Hz, default 500`
The cutoff frequency at the bottom of the sweep — where the filter sits when the LFO is at its minimum. If set higher than Frequency High, the two values are automatically swapped.

**Frequency High Hz** `20-20000 Hz, default 5000`
The cutoff frequency at the top of the sweep — where the filter sits when the LFO is at its peak.

**Resonance** `0.0-1.0, default 0.7`
Resonance of the lowpass filter. Higher values add a pronounced peak at the cutoff frequency, making the sweep more tonally distinctive. Values above 0.9 can produce self-oscillation on some material.

**Wet/Dry Mix** `0.0-1.0, default 1.0`
Blend between the filtered signal (wet) and the original unprocessed signal (dry). At 1.0 the output is fully filtered. At 0.0 the filter has no effect. At 0.5 both are equally present.

---

### LFO Rate

**Rate Value** `0.001-1000, default 2`
The sweep rate in the units set by Rate Mode.

**Rate Mode** `Hz / Seconds / BPM`
How Rate Value is interpreted.
- **Hz** — cycles per second.
- **Seconds** — period of one full cycle.
- **BPM** — cycles per minute.

**LFO Start Phase (degrees)** `-180 to +180, default 0`
Sets the initial phase position of the LFO when the plugin is first loaded or when this slider is moved. At 0, the LFO starts at the beginning of the cycle. This is a set-once control — adjusting it repositions both channel phases immediately, after which they run freely from that point. Useful for aligning the filter sweep to a specific position relative to other material or other instances of this plugin.

---

### Sweep Shape

**On Duration % of Cycle** `0-100%, default 50`
The proportion of each cycle during which the LFO is in its active (non-minimum) state, including attack and release time. At 50%, the filter sweeps up and back during the first half of the cycle and sits at the low frequency for the second half. At 100%, the sweep never rests at the low frequency.

**Depth %** `0-100%, default 100`
How much of the frequency range the sweep covers. At 100%, the sweep moves fully between Frequency Low and Frequency High. At 50%, it sweeps only the inner half of that range, centered between the two values. At 0%, the filter stays fixed at the center frequency with no movement.

**Attack %** `0-100%, default 0`
Proportion of the on-time spent in the attack ramp, where the cutoff rises from the low to the high frequency. At 0%, the filter opens instantly.

**Release %** `0-100%, default 0`
Proportion of the on-time spent in the release ramp, where the cutoff falls from high to low. At 0%, the filter closes instantly. If Attack % + Release % exceeds 100% of the on-time, both are scaled down proportionally.

**Attack Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve applied to the attack ramp.
- **Linear** — straight ramp.
- **Cosine** — S-curve, gentle at both ends.
- **Logarithmic** — fast initial rise, slow finish.
- **Exponential** — slow initial rise, fast finish.

**Release Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve applied to the release ramp. Same options as Attack Shape.

---

### Stereo

**R Channel Phase Offset degrees** `-180–+180°, default 0`
When Phase Mode is set to Offset from L, this controls the phase difference between the left and right channel LFOs. At 180°, the channels are in opposition — when the left filter is fully open the right is fully closed. At 0° both channels move in unison.

**Phase Mode** `Independent L+R / Offset from L`
- **Independent L+R** — both LFO phases advance freely and in sync.
- **Offset from L** — the right channel phase is continuously derived as the left phase plus the R Channel Phase Offset. Use this mode when a stable stereo phase relationship is needed.

---

### Pan Block

**Pan Enabled** `Off / On`
Enables pan modulation. When on, the post-filter signal is summed to mono and repositioned in the stereo field according to the active pan mode. When off, all pan sliders are hidden.

> **Note:** Enabling pan converts the output to mono before panning. The stereo content of the filtered signal is collapsed. Place this plugin accordingly in your signal chain.

---

#### Per-Cycle Pan Modes

These modes update the pan position once per LFO cycle. **Cycle Steps** controls the sequence length.

**Mono**
No panning. Signal stays centered.

**Alternating**
Alternates hard left and hard right each cycle.

**Alternating (Flipped)**
Same as Alternating but starting from the right.

**Distributed**
Steps evenly from left to right across the cycle count, then wraps back to the left.

**Distributed (Flipped)**
Steps evenly from right to left, then wraps.

**Distributed (Ping-pong)**
Steps left to right then reverses, bouncing between the extremes.

**Converging**
Starts at hard left, then alternates left and right positions stepping progressively toward center with each cycle.

**Converging (Ping-pong)**
Same converging pattern but reverses back outward after reaching center, then converges again.

**Diverging**
Starts at center, then alternates left and right positions stepping progressively outward toward the extremes.

**Diverging (Ping-pong)**
Same diverging pattern but reverses back inward after reaching the extremes.

---

#### Continuous Pan Modes

**Pan Sweep**
Pan position sweeps continuously from left to right at the rate set by Pan Sweep Rate and Pan Sweep Rate Unit, independently of the filter LFO rate.

**Pan Sweep (Flipped)**
Same as Pan Sweep but sweeping right to left.

**Linked Sweep**
Pan sweeps in sync with the filter LFO at a speed multiplied by the Filter Speed Multiplier. At 1×, one full pan sweep per filter cycle. At 2×, two sweeps per cycle.

---

#### Pan Parameters

**Pan Spread** `0.0-1.0, default 1.0`
Scales the pan range. At 1.0 positions reach hard left and right. At 0.0 all modes produce center.

**Pan Glide ms** `0-100 ms, default 5`
Smoothing time for pan position changes. Higher values trade sharpness for click-free transitions.

**Cycle Steps (per-cycle modes)** `2-32, default 8`
Number of steps in the pan sequence for per-cycle modes. Hidden for continuous modes.

**Pan Sweep Rate** `0.001-1000, default 2`
Rate of continuous pan sweep for Pan Sweep and Pan Sweep (Flipped) modes.

**Pan Sweep Rate Unit** `Hz / Seconds / BPM`
Unit for Pan Sweep Rate.

**Filter Speed Multiplier (Linked Sweep)** `0.125-8×, default 1×`
Speed of pan sweep relative to filter LFO rate, for Linked Sweep only.

### Start Delay

**Start Delay** `0–1000, default 0`

Pass-through for N units after playback starts, then applies the filter sweep + pan effect normally. Units match Rate Mode: BPM mode counts cycles of the LFO Rate Value, Seconds is literal seconds, Hz mode counts cycles of Rate Value. The dry signal flows through unchanged during the delay — silencing the output would mute the dry track too, which is rarely what you want for an effect. Filter and LFO state stay frozen during the delay so the sweep begins cleanly at delay-end. Re-arms on every transport stop/start. 0 disables the delay.

### Play / Rest Gating (v2.1)

**Play for (cycles)** `0–1000, default 0`
**Rest for (cycles)** `0–1000, default 0`
**LFO at rest** `Walk through / Freeze in place, default Walk through`
**Output at rest** `Pass-through / Silence, default Pass-through`

A cyclic gate over the filter sweep + pan effect. The effect is applied normally for **Play for** cycles, then enters its rest period for **Rest for** cycles, then resumes — the pattern repeats forever. Useful for rhythmic on/off of the filter: "filter sweep for 4 bars, dry for 4 bars, repeat."

Cycle unit matches Start Delay: Rate Mode units measured against Rate Value.

The feature is **disabled when either of Play for / Rest for is 0** (the default). With both at 0, the plugin behaves as before; the LFO at rest / Output at rest sliders have no effect when the gate is off.

**Click-free transitions.** The effect smoothly fades out on rest entry (and back in on exit) using the same ~3 ms smoother that handles the cutoff sweep. The filter coefficients and resonance state keep running through the rest period so the filter is "warm" and ready to re-engage cleanly — no transient when the effect comes back.

Two independent sliders shape what happens during rest:

**LFO at rest** — what the filter sweep + pan LFOs do during rest:

- **Walk through** (default): LFOs keep cycling during rest. When the effect resumes, the filter cutoff has swept to a different position — you hear the filter come back in at wherever the LFO landed.
- **Freeze in place**: LFO phases pause, frozen at their values at rest entry. When the effect resumes, the cutoff picks up from the same position. The rhythmic sweep pauses and resumes in lockstep with the gate.

**Output at rest** — what the audio output does during rest:

- **Pass-through** (default): dry signal passes through unchanged. Matches Start Delay's behavior on this plugin — silencing the input would mute the upstream track in the FX chain.
- **Silence**: wet+dry mix smooths to 0 over ~3 ms; the audio fades into silence rather than passing dry. Useful when you want the gate to act like a hard mute rather than a filter bypass.

The two sliders are orthogonal — all four combinations work. Walk + Silence keeps the filter sweeping internally while the audio drops out; Freeze + Silence pauses everything; Walk + Pass-through and Freeze + Pass-through are the two "filter bypass" flavors.

**Filter resonance state and cutoff smoother keep running across all four combinations.** Only the LFO phase advancement is frozen in Freeze — the actual filter math continues processing the input throughout rest. This avoids transients on rest exit, at the cost of the filter potentially having settled to a slightly different cutoff position than at rest entry (because the smoother chases the frozen cutoff target). For long rests with a slow smoother this matters little; for short rests the difference is imperceptible.

**Transport behavior**: conventional. Stop passes through dry; play re-initializes everything and starts fresh in its play period from cycle 0.

### Speed Ramp

In-plugin sweep-rate morph over time. Set a signed `by` amount in the rate's currently-displayed unit, a duration, flip engage on — the filter sweep eases toward `Rate Value + by` without needing automation envelopes.

**Speed ramp by (slider 29)** `-1000 to +1000, step 0.001, default 0`
Signed delta added to the Rate Value over the duration. **0** = no change. The delta is in **the rate's currently-displayed unit** — Hz if Rate Mode is Hz, Seconds (period) if Seconds, BPM if BPM. In BPM/Hz modes negative `by` = slower sweep; in Seconds mode positive `by` = slower (longer period).

**Speed ramp duration (slider 30)** `0–60 minutes, default 0` · **Speed ramp engage (slider 31)** `Off / On, default Off` · **Speed ramp start delay (slider 32)** `0–60 minutes, default 0`

Engage is a freeze/resume gate (NOT a restart edge): while On, ramp_t advances 0 → 1 over the duration; while Off, ramp_t freezes and resumes from there on re-engage.

A ~100 ms smoother sits between the Rate slider and the audio so manual Rate tweaks don't click.

The ramp also affects the Linked Sweep pan mode (12), since that mode derives its rate from the sweep frequency. The two Pan Sweep modes (10, 11) have their own independent rate slider and are NOT affected by the speed ramp.

**Transport behavior:** speed_ramp_t resets to 0 on every transport play edge. This is the ONLY thing that resets the ramp — slider changes don't.

**Migration from v2.7:** slider 29 changed from multiplier (0.1–4.0) to signed delta in rate-units. Old projects' multiplier value interprets as a tiny delta — Speed Ramp effectively "off" until reconfigured.

### Drift

Slow organic wander applied to the sweep rate on top of Speed Ramp — the cutoff still moves through the same Low and High frequencies, but the pace breathes instead of locking to one rate. See [Per-Plugin Drift](#per-plugin-drift) for the architecture; the seven sliders below configure it for this plugin.

**Musical Period (cycles)** `1–256, default 32`
Period of the musical drift source, measured in LFO cycles of the Rate Value. Scales with Speed Ramp.

**Musical Up by** `0.0–1.0, default 0`
How far above the center sweep rate the musical drift wanders at its peak, as a multiplier amplitude.

**Musical Down by** `0.0–1.0, default 0`
How far below the center sweep rate the musical drift wanders at its trough. Independent from Up by.

**Slow Period (minutes)** `0.1–60, default 5`
Period of the slow drift source, measured in wall-clock minutes. Does NOT scale with Speed Ramp.

**Slow Up by** `0.0–1.0, default 0`
Above-center amplitude for the slow drift source.

**Slow Down by** `0.0–1.0, default 0`
Below-center amplitude for the slow drift source.

**Shape** `Sine / Triangle / Random, default Sine`
Wander shape applied to both sources.

---

## Usage Notes

- **Attack and Release are proportions of on-time, not cycle time.** A 50% Attack with 50% On Duration means the attack ramp takes 25% of the total cycle.
- **Depth % scales symmetrically around the center frequency.** At 50% depth with Low=200 Hz and High=2000 Hz, the sweep covers 700-1300 Hz — not 200-1100 Hz.
- **The filter coefficient uses linear frequency mapping** (`freq * 2 / srate`), unlike the sinusoidal mapping in the synthesizer plugins. Displayed Hz values correspond directly to standard filter behavior.
- **Phase Offset only takes effect in Offset from L mode.** In Independent L+R mode the offset slider has no effect on behavior.

---

*Full Feature Sweeping Filter is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

# Sweep Dwell Filter

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Sweep Dwell Filter is a resonant lowpass filter driven by an LFO with four time-based phases: hold at high frequency, sweep down to low, hold at low frequency, and sweep back up. Unlike a rate-based LFO, the cycle duration is determined entirely by the four phase times — each phase has its own duration in seconds, and the total cycle length is their sum. The fade transitions have independently selectable curve shapes. A wet/dry mix and an optional pan modulation system complete the feature set.

The plugin processes incoming stereo audio.

---

## Signal Architecture

The LFO phase advances continuously. At any point in the phase, the plugin calculates the current position within the hold-high, sweep-down, hold-low, and sweep-up sequence, and outputs a value between 0 (low cutoff) and 1 (high cutoff) accordingly. The fade transitions use configurable curve shapes. The LFO output is mapped linearly to the frequency range, smoothed with a 3 ms lag, and fed into a two-pole resonant lowpass filter per channel. The wet output is blended with the dry signal.

Left and right channels have independent LFO phases. In **Independent L+R** mode both advance at the same rate, staying in sync. In **Offset from L** mode the right channel phase is continuously derived from the left plus the stereo offset, keeping a stable phase relationship.

---

## Parameters

### Filter Range

**Frequency Low Hz** `20-20000 Hz, default 500`
The cutoff frequency during the low-dwell segment — the resting state of the filter. If set higher than Frequency High, the two values are automatically swapped.

**Frequency High Hz** `20-20000 Hz, default 5000`
The cutoff frequency during the high-dwell segment — the open state of the filter.

**Resonance** `0.0-1.0, default 0.7`
Resonance of the lowpass filter. Higher values add a pronounced peak at the cutoff frequency, accentuating the frequencies at each point in the sweep. Values approaching 1.0 can produce self-oscillation.

**Wet/Dry Mix** `0.0-1.0, default 1.0`
Blend between the filtered signal and the unprocessed input. At 1.0 the output is fully filtered; at 0.0 the filter has no effect.

---

### Dwell and Transition Times

The LFO cycle consists of four phases in sequence: hold high → sweep down → hold low → sweep up → repeat. The total cycle length is the sum of all four phase durations.

**High Dwell sec** `0.001-60 sec, default 4`
Duration of the segment where the filter holds at the high cutoff frequency.

**Low Dwell sec** `0.001-60 sec, default 6`
Duration of the segment where the filter holds at the low cutoff frequency.

**Fade Down sec** `0.001-30 sec, default 1`
Duration of the transition from the high cutoff frequency to the low cutoff frequency.

**Fade Down Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve shape applied to the fade-down transition.
- **Linear** — constant rate of frequency change.
- **Cosine** — S-curve, slow at both ends, faster in the middle.
- **Logarithmic** — fast initial drop, slow finish. The filter closes quickly then lingers near the low frequency.
- **Exponential** — slow initial drop, fast finish. The filter holds near the high frequency before closing sharply.

**Fade Up sec** `0.001-30 sec, default 1`
Duration of the transition from the low cutoff frequency back to the high cutoff frequency.

**Fade Up Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve shape applied to the fade-up transition. Same options as Fade Down Shape. Asymmetric shapes between fade down and fade up create distinct opening and closing characters.

---

### Stereo

**Stereo Phase Offset degrees** `-180–+180°, default 0`
When Phase Mode is Offset from L, this controls the phase difference between the left and right LFOs. At 180° the channels are in opposition — when the left filter is at its high cutoff the right is at its low cutoff. At 0° both channels move identically.

**Phase Mode** `Independent L+R / Offset from L`
- **Independent L+R** — both LFO phases advance freely at the same rate, staying in sync.
- **Offset from L** — the right channel phase is derived continuously as the left phase plus the Stereo Phase Offset. Use this mode to maintain a stable stereo phase relationship.

---

### Pan Block

**Pan Enabled** `Off / On`
Enables pan modulation. When on, the post-filter signal is summed to mono and repositioned in the stereo field. When off, all pan sliders are hidden.

> **Note:** Enabling pan sums the output to mono before panning. Stereo content of the filtered signal is collapsed.

---

#### Per-Cycle Pan Modes

Pan position updates once per LFO cycle. **Cycle Steps** controls the sequence length.

**Mono** — signal stays centered.

**Alternating** — alternates hard left and hard right each cycle.

**Alternating (Flipped)** — same as Alternating, starting from the right.

**Distributed** — steps evenly from left to right across the cycle count, then wraps.

**Distributed (Flipped)** — steps evenly from right to left, then wraps.

**Distributed (Ping-pong)** — steps left to right then reverses, bouncing between extremes.

**Converging** — starts hard left, alternates left/right positions stepping progressively toward center.

**Converging (Ping-pong)** — converges to center then reverses back outward, bouncing.

**Diverging** — starts center, alternates left/right positions stepping progressively outward.

**Diverging (Ping-pong)** — diverges to extremes then reverses back inward, bouncing.

---

#### Continuous Pan Modes

**Pan Sweep** — continuous left-to-right sweep at the rate set by Pan Sweep Rate.

**Pan Sweep (Flipped)** — continuous right-to-left sweep.

**Linked Sweep** — pan sweeps in proportion to the filter cycle rate, scaled by Filter Speed Multiplier. At 1×, one full pan sweep per filter cycle.

---

#### Pan Parameters

**Pan Spread** `0.0-1.0, default 1.0`
Scales the pan range. At 0.0 all modes produce center.

**Pan Glide ms** `0-100 ms, default 5`
Smoothing time for pan position changes.

**Cycle Steps (per-cycle modes)** `2-32, default 8`
Sequence length for per-cycle modes.

**Pan Sweep Rate** `0.001-1000, default 2`
Rate for Pan Sweep and Pan Sweep (Flipped) modes.

**Pan Sweep Rate Unit** `Hz / Seconds / BPM`
Unit for Pan Sweep Rate.

**Filter Speed Multiplier (Linked Sweep)** `0.125-8×, default 1×`
Pan sweep speed relative to filter cycle, for Linked Sweep only.

### Start Delay

**Start Delay (seconds)** `0–1000, default 0`

Pass-through for N seconds after playback starts, then applies the sweep-dwell filter + pan effect normally. The dry signal flows through unchanged during the delay — silencing the output would mute the dry track too, which is rarely what you want for an effect. Sweep state and filter buffers stay frozen during the delay so the sweep begins cleanly at delay-end. Re-arms on every transport stop/start. 0 disables the delay.

### Play / Rest Gating (v2.1)

**Play for (cycles)** `0–1000, default 0`
**Rest for (cycles)** `0–1000, default 0`
**LFO at rest** `Walk through / Freeze in place, default Walk through`
**Output at rest** `Pass-through / Silence, default Pass-through`

A cyclic gate over the filter + pan effect. The effect is applied normally for **Play for** cycles, then enters its rest period for **Rest for** cycles, then resumes — the pattern repeats forever.

One "cycle" here is one full dwell pattern: **High Dwell + Fade Down + Low Dwell + Fade Up**. So with the default settings (4 + 1 + 6 + 1 = 12 sec/cycle), `Play for = 4` plays 48 seconds of the sweep before entering rest, and `Rest for = 2` rests for 24 seconds. Cycle counts at this plugin can produce long play / rest periods because the dwell pattern itself is long — adjust the dwell + fade sliders if you want shorter cycles.

The feature is **disabled when either of Play for / Rest for is 0** (the default). With both at 0, the plugin behaves as before; the two "at rest" sliders have no effect when the gate is off.

**Click-free transitions.** The effect smoothly fades out on rest entry (and back in on exit) using the same ~3 ms smoother that handles the cutoff sweep. The filter coefficients and resonance state keep running through the rest period so the filter is "warm" and ready to re-engage cleanly.

Two independent sliders shape what happens during rest:

**LFO at rest** — what the dwell-pattern LFO and pan LFOs do during rest:

- **Walk through** (default): LFOs keep cycling during rest. When the effect resumes, the dwell pattern has advanced to a different position — you might hear it resume mid-fade-down or mid-low-dwell rather than at the start of a fresh high dwell.
- **Freeze in place**: LFO phases pause, frozen at their values at rest entry. When the effect resumes, the dwell pattern picks up from the same position. Useful when you want predictable phase relationships across multiple play/rest cycles.

**Output at rest** — what the audio output does during rest:

- **Pass-through** (default): dry signal passes through unchanged. Matches Start Delay's behavior.
- **Silence**: wet+dry mix smooths to 0 over ~3 ms; the audio fades into silence rather than passing dry. Useful when you want the gate to act like a hard mute rather than a filter bypass.

The two sliders are orthogonal — all four combinations work and produce distinct behavior.

**Filter resonance state and cutoff smoother keep running across all four combinations.** Only the LFO phase advancement is frozen in Freeze — the actual filter math continues processing the input throughout rest. This avoids transients on rest exit, at the cost of the filter potentially having settled to a slightly different cutoff position than at rest entry.

**Transport behavior**: conventional. Stop passes through dry; play re-initializes everything and starts fresh in its play period from cycle 0.

### Speed Ramp

Nested-selector pattern matching Womb v3 / breath_gen. Pick one of the 4 dwell sliders (High dwell / Fade down / Low dwell / Fade up) and set a signed `by` amount in seconds. That dwell phase's length ramps from its baseline toward `baseline + by` over the duration. All 4 targets ramp in parallel; the selector just changes which one you're editing.

**Speed ramp target (slider 26)** `High dwell / Fade down / Low dwell / Fade up, default High dwell`
The 4-option selector. Switching saves the current slider 29 amount to the old target's memory slot and loads the new target's saved amount. All 4 targets ramp regardless of which one is selected.

**Speed ramp duration (slider 27)** `0–60 minutes, default 0` · **Speed ramp engage (slider 28)** `Off / On, default Off`

Engage is a freeze/resume gate (NOT a restart edge): while On, ramp_t advances 0 → 1 over the duration; while Off, ramp_t freezes and resumes from there on re-engage.

**Speed ramp by (slider 29)** `-60 to +60 seconds, step 0.001, default 0`
Signed delta in seconds for the selected dwell phase. **0** = no change. **Negative** = shorten that phase (shorter cycle if that's High/Low dwell; quicker fade if that's a fade phase). **Positive** = lengthen. Example: target High dwell with `by +4` stretches high dwell from 4 sec → 8 sec over the duration; combined with target Low dwell with `by +2`, both phases ramp together as a coordinated wind-down.

**Speed ramp start delay (slider 37)** `0–60 minutes, default 0`
Wait this many minutes after engage before ramp_t starts advancing. Lives at slider 37 (after the drift block) because slider 29 was claimed by the new `by` amount.

**Transport behavior:** speed_ramp_t resets to 0 on every transport play edge. The existing ~3 ms cutoff smoother absorbs any per-sample step changes, so manual dwell-slider tweaks remain click-free.

**Migration from v2.7:** slider 26 changed from multiplier (0.1–4.0) to a 4-option selector. Existing projects' multiplier value rounds down to a target index, and slider 29 (the new amount) defaults to 0 — Speed Ramp produces no effect on reload until reconfigured.

### Drift

Slow organic wander applied to the dwell pattern's overall pace on top of Speed Ramp — high dwells become a little longer or shorter as the drift evolves, instead of being identical every cycle. See [Per-Plugin Drift](#per-plugin-drift) for the architecture; the seven sliders below configure it for this plugin.

**Musical Period (cycles)** `1–256, default 32`
Period of the musical drift source, measured in dwell cycles (one full high dwell + fade down + low dwell + fade up). Scales with Speed Ramp.

**Musical Up by** `0.0–1.0, default 0`
How far above the center pace the musical drift wanders at its peak, as a multiplier amplitude.

**Musical Down by** `0.0–1.0, default 0`
How far below the center pace the musical drift wanders at its trough. Independent from Up by.

**Slow Period (minutes)** `0.1–60, default 5`
Period of the slow drift source, measured in wall-clock minutes. Does NOT scale with Speed Ramp.

**Slow Up by** `0.0–1.0, default 0`
Above-center amplitude for the slow drift source.

**Slow Down by** `0.0–1.0, default 0`
Below-center amplitude for the slow drift source.

**Shape** `Sine / Triangle / Random, default Sine`
Wander shape applied to both sources.

---

## Usage Notes

- **Cycle length is the sum of all four phase durations.** Unlike rate-based LFOs there is no single BPM or Hz value — the tempo of the sweep is a consequence of the four phase times combined.
- **Adjusting any phase duration takes effect immediately.** The LFO phase is a running 0-1 counter; changing phase durations changes how that counter maps to filter positions without resetting it. This means a duration change mid-cycle may cause a jump to a different point in the sweep.
- **The frequency mapping is linear.** Displayed Hz values correspond directly to filter behavior — the same linear mapping used in the other filter plugins in this suite.
- **Phase Offset only takes effect in Offset from L mode.** In Independent L+R mode the offset slider has no audible effect.

---

*Sweep Dwell Filter is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

# Full Feature Tremolo

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Full Feature Tremolo is an amplitude modulation effect with a fully configurable LFO envelope and an optional pan modulation system. The tremolo LFO is not a simple sine wave — it is a gated envelope with independently shaped attack and release curves, a configurable on-time within each cycle, and a hold-high region between them. This allows the plugin to produce anything from a smooth, sine-like tremolo to a hard gate with slow attack, fast release, or any combination in between.

The pan block, when enabled, moves the signal through the stereo field in sync with or independently of the tremolo cycle, with twelve pan modes ranging from simple alternation to continuous sweeps.

The plugin processes incoming stereo audio.

---

## Signal Architecture

### Tremolo

The LFO runs as a normalized phase (0-1 per cycle). Each sample, the phase advances by `freq / srate`. The LFO envelope is computed from the phase position relative to the on-time, attack, and release durations. The resulting gain value (between the depth floor and 1.0) is smoothed with a 3 ms lag to prevent zipper noise on abrupt transitions, then applied as a multiplier to each channel.

Left and right channels have independent phase counters. In **Independent L+R** mode they both advance freely at the same rate. In **Offset from L** mode the right channel phase is derived as the left channel phase plus the stereo offset, keeping them locked in relative position.

### Pan

When the pan block is enabled, the post-tremolo signal is summed to mono, then redistributed to L and R using constant-power panning. The pan position is smoothed by the glide coefficient before being applied, preventing clicks on sudden position changes.

---

## Parameters

### Tremolo

**Rate Value** `0.001-1000, default 2`
The tremolo rate in the units set by Rate Mode.

**Rate Mode** `Hz / Seconds / BPM`
How Rate Value is interpreted.
- **Hz** — cycles per second.
- **Seconds** — period of one full cycle.
- **BPM** — cycles per minute.

**On Duration % of Cycle** `0-100%, default 50`
The proportion of each cycle during which the tremolo is in its active (non-silent) state — including attack and release time. At 50%, the signal is present for half the cycle and absent for the other half. At 100%, the tremolo never fully closes. At 0%, the output is silence.

**Depth dB** `-60-0 dB, default -6`
How far the signal drops at the bottom of the tremolo cycle. At 0 dB there is no depth and the output is unaffected. At -60 dB the signal is effectively silenced at the trough. The depth is converted internally to a linear gain multiplier.

**Attack %** `0-100%, default 0`
Proportion of the on-time spent fading in from silence to full level. At 0%, the tremolo opens instantly at the start of each on-period. Attack and Release proportions are expressed relative to the on-time, not the full cycle — so an Attack of 50% means the first half of the on-duration is the attack ramp. If Attack % + Release % exceeds 100% of the on-time, both are scaled down proportionally.

**Release %** `0-100%, default 0`
Proportion of the on-time spent fading from full level back to silence. At 0%, the tremolo closes instantly at the end of each on-period.

**Attack Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve applied to the attack ramp.
- **Linear** — straight ramp.
- **Cosine** — S-curve, gentle at both ends.
- **Logarithmic** — fast initial rise, slow finish. Perceived loudness increases quickly.
- **Exponential** — slow initial rise, fast finish. Builds tension before arrival.

**Release Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve applied to the release ramp. Same options as Attack Shape. Mixing attack and release shapes — e.g., Logarithmic attack with Exponential release — can produce organic, asymmetric tremolo characters.

**Stereo Phase Offset (degrees)** `-180–+180°, default 0`
When Phase Mode is set to Offset from L, this controls how far ahead or behind the right channel's LFO is relative to the left. At 180° or -180°, the channels are in perfect opposition — when left is at its peak, right is at its trough. At 0°, the offset is zero and both channels move in unison regardless of mode (equivalent to Independent L+R for most purposes).

**Phase Mode** `Independent L+R / Offset from L`
- **Independent L+R** — left and right LFO phases advance independently. Both start at zero and run freely. In practice they stay in sync unless rates diverge, which they don't in this plugin — so this mode produces synchronized stereo tremolo.
- **Offset from L** — the right channel phase is continuously derived as the left phase plus the Stereo Phase Offset. This keeps the offset locked regardless of where in the cycle each channel is, and is the correct mode to use when you want a stable stereo phase relationship.

---

### Pan Block

**Pan Enabled** `Off / On`
Enables the pan modulation system. When off, all pan-related sliders are hidden and the signal passes through the tremolo section unaffected by panning. When on, the post-tremolo signal is summed to mono and panned according to the active pan mode.

> **Note:** Enabling pan converts the output to mono before panning. If your source is stereo and you want to preserve its stereo image, use Pan Enabled only when the mono sum is acceptable, or place the tremolo before stereo-sensitive processing.

---

#### Per-Cycle Pan Modes

These modes update the pan position once per tremolo cycle, at the moment the LFO phase resets. The **Cycle Steps** parameter controls how many steps the sequence runs before repeating (where applicable).

**Mono**
No panning. Signal stays centered regardless of Cycle Steps.

**Alternating**
Jumps between hard left and hard right on each cycle. Step count does not affect this mode.

**Distributed**
Steps evenly from left to right across the cycle count, then repeats from the left. At 8 steps: hard left, then incrementally right, reaching hard right on step 8, then back to hard left.

**Distributed (Flipped)**
Same as Distributed but starting from the right and stepping left.

**Distributed (Ping-pong)**
Steps left to right then reverses back right to left, bouncing between the extremes.

**Converging**
Starts at hard left, then alternates left and right positions that step progressively toward center. Each pair of positions is closer to center than the last.

**Converging (Ping-pong)**
Same pattern as Converging but bounces back outward after reaching center, then converges again.

**Diverging**
Starts at center, then alternates left and right positions stepping progressively outward toward the extremes.

**Diverging (Ping-pong)**
Same as Diverging but bounces back inward after reaching the extremes.

---

#### Continuous Pan Modes

**Pan Sweep**
Pan position sweeps continuously from left to right using a linear ramp at the rate set by Pan Sweep Rate and Pan Sweep Rate Unit, independently of the tremolo rate. When the pan reaches the right extreme it wraps back to the left.

**Pan Sweep (Flipped)**
Same as Pan Sweep but sweeping from right to left.

**Linked Sweep**
Pan position sweeps in sync with the tremolo LFO, but at a speed multiplied by the Filter Speed Multiplier. At 1×, the pan completes one full sweep per tremolo cycle. At 2×, it sweeps twice per cycle. At 0.5×, it sweeps once every two cycles.

---

#### Pan Parameters

**Pan Spread** `0.0-1.0, default 1.0`
Scales the pan range. At 1.0, pan positions reach hard left and hard right. At 0.5, the maximum excursion is halfway to each side. At 0.0, all pan modes produce center regardless of their position calculations.

**Pan Glide ms** `0-100 ms, default 5`
Smoothing time applied to pan position changes. At 0 ms, pan position jumps immediately to each new value — appropriate for hard-cut effects but can produce clicks on per-cycle modes at slow tempos. Higher values smooth the transition, trading sharpness for click-free movement.

**Cycle Steps (per-cycle modes)** `2-32 steps, default 8`
Number of steps in the pan sequence for per-cycle modes (Alternating through Diverging Ping-pong). Hidden when a continuous pan mode is active.

**Pan Sweep Rate** `0.001-1000, default 2`
Rate of the continuous pan sweep for Pan Sweep and Pan Sweep (Flipped) modes. Hidden for other modes.

**Pan Sweep Rate Unit** `Hz / Seconds / BPM`
Unit for Pan Sweep Rate. Hidden for modes that don't use it.

**Filter Speed Multiplier (Linked Sweep)** `0.125-8×, default 2×`
Speed of the pan sweep relative to the tremolo rate, for Linked Sweep mode only. Hidden for other modes.

### Start Delay

**Start Delay** `0–1000, default 0`

Pass-through for N units after playback starts, then applies the tremolo + pan effect normally. Units match Rate Mode: BPM mode counts cycles of the tremolo Rate Value, Seconds is literal seconds, Hz mode counts cycles of Rate Value. The dry signal flows through unchanged during the delay — silencing the output would mute the dry track too, which is rarely what you want for an effect. Phase counters and gain smoothing stay frozen during the delay so the tremolo begins cleanly at delay-end. Re-arms on every transport stop/start. 0 disables the delay.

### Play / Rest Gating (v2.1)

**Play for (cycles)** `0–1000, default 0`
**Rest for (cycles)** `0–1000, default 0`
**LFO at rest** `Walk through / Freeze in place, default Walk through`
**Output at rest** `Pass-through / Silence, default Pass-through`

A cyclic gate over the tremolo + pan effect. The effect is applied normally for **Play for** cycles, then enters its rest period for **Rest for** cycles, then resumes — the pattern repeats forever. Useful for rhythmic on/off of the modulation: "tremolo for 4 bars, no tremolo for 4 bars, repeat."

Cycle unit is the same as Start Delay: Rate Mode units measured against Rate Value. At the default Rate Value = 2 in Hz mode, "4 cycles" = 2 seconds.

The feature is **disabled when either of Play for / Rest for is 0** (the default). With both at 0, the plugin behaves as before; the LFO at rest / Output at rest sliders have no effect when the gate is off.

**Click-free transitions.** When entering rest, the relevant target (dry pass-through or silence, depending on Output at rest) is smoothly faded toward over ~3 ms. On rest exit, the same fade brings the effect back in. The gate sounds like a soft swell rather than an abrupt switch.

Two independent sliders shape what happens during rest:

**LFO at rest** — what the tremolo + pan LFOs do during rest:

- **Walk through** (default): LFOs keep cycling during rest. When the effect resumes, the LFOs are at new phase positions reflecting wall-clock time passed. The rhythmic cycle keeps running even when you can't hear it.
- **Freeze in place**: LFO phases pause during rest, frozen at their values at rest entry. When the effect resumes, the LFOs pick up from the same phase. The rhythmic cycle pauses and resumes in lockstep with the gate.

**Output at rest** — what the audio output does during rest:

- **Pass-through** (default): dry signal passes through unchanged. Effect plugins normally don't silence their input — silencing would mute whatever's upstream in the FX chain. Matches Start Delay's pass-through-during-delay behavior on this plugin.
- **Silence**: gain target smooths to 0 over ~3 ms; the audio fades into silence rather than passing dry. Useful when you want the gate to act like a hard mute rather than an effect bypass — e.g., for rhythmic drop-outs in an arrangement.

The two sliders are orthogonal — all four combinations work and produce distinct behavior. Walk + Silence keeps the rhythm running internally while the audio drops out; Freeze + Silence pauses everything (audio AND rhythm); Walk + Pass-through and Freeze + Pass-through are the two "effect bypass" flavors.

**Transport behavior**: conventional. Stop passes through dry; play re-initializes everything (LFO phases, rest state, cycle counter) and starts fresh in its play period from cycle 0.

### Speed Ramp

In-plugin tremolo-rate morph over time.

**Speed ramp by (slider 24)** `-1000 to +1000, step 0.001, default 0`
Signed delta added to the Rate Value over the duration. **0** = no change. The delta is in **the rate's currently-displayed unit** — Hz if Rate Mode is Hz, Seconds (period) if Seconds, BPM if BPM. In BPM/Hz modes, negative `by` = slower tremolo; in Seconds mode, positive `by` = slower (longer period).

**Speed ramp duration (slider 25)** `0–60 minutes, default 0` · **Speed ramp engage (slider 26)** `Off / On, default Off` · **Speed ramp start delay (slider 27)** `0–60 minutes, default 0`

Engage is a freeze/resume gate (NOT a restart edge): while On, ramp_t advances 0 → 1 over the duration; while Off, ramp_t freezes and resumes from there on re-engage.

A ~100 ms smoother sits between the Rate slider and the effective frequency, so manual Rate tweaks don't click.

The ramp also affects the linked-sweep pan rate (Pan Mode 11), since that mode derives its rate from the tremolo frequency. Pan Sweep modes 9 and 10 have their own independent rate slider and are NOT scaled by the speed ramp.

**Transport behavior:** speed_ramp_t resets to 0 on every transport play edge. This is the ONLY thing that resets the ramp — slider changes don't.

**Migration from v2.7:** slider 24 changed from a multiplier (0.1–4.0) to a signed delta in rate-units. Old projects' multiplier value will be interpreted as a tiny delta — Speed Ramp effectively "off" until reconfigured.

### Drift

Slow organic wander applied to the tremolo rate on top of Speed Ramp — useful when you want the modulation pulse to feel breathing rather than metronomic. See [Per-Plugin Drift](#per-plugin-drift) for the architecture; the seven sliders below configure it for this plugin.

**Musical Period (cycles)** `1–256, default 32`
Period of the musical drift source, measured in tremolo cycles. Scales with Speed Ramp.

**Musical Up by** `0.0–1.0, default 0`
How far above the center rate the musical drift wanders at its peak, as a multiplier amplitude.

**Musical Down by** `0.0–1.0, default 0`
How far below the center rate the musical drift wanders at its trough. Independent from Up by.

**Slow Period (minutes)** `0.1–60, default 5`
Period of the slow drift source, measured in wall-clock minutes. Does NOT scale with Speed Ramp.

**Slow Up by** `0.0–1.0, default 0`
Above-center amplitude for the slow drift source.

**Slow Down by** `0.0–1.0, default 0`
Below-center amplitude for the slow drift source.

**Shape** `Sine / Triangle / Random, default Sine`
Wander shape applied to both sources.

---

## Usage Notes

- **Pan block sums to mono before panning.** This is intentional — pan modulation is applied to a unified signal. If the source is stereo, the two channels are averaged before any pan position is applied.
- **Attack and Release are proportions of on-time, not cycle time.** A 50% Attack with a 50% On Duration means the attack ramp takes 25% of the total cycle.
- **Phase Offset only takes effect in Offset from L mode.** In Independent L+R mode the offset slider has no effect.
- **Per-cycle pan modes update at LFO phase reset.** The pan position does not glide to a new value mid-cycle — it jumps (subject to Pan Glide smoothing) at the moment the tremolo cycle wraps.

---

*Full Feature Tremolo is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

# Resonance Bank

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Resonance Bank is a 16-band effect with two modes — parallel bandpass or serial peaking EQ — per-band multi-target drift modulation, cascade-order rolloff control, and a selector-pattern interface that keeps the slider count manageable regardless of how many bands are active. Use it for vowel-flavored breath shaping, dynamic windscapes, evolving noise textures, frequency emphasis curves, or any task where you want multiple independently configurable resonant peaks shaping an input signal.

Configuration uses a nested selector pattern. A Band selector picks which of the 16 bands you are currently editing; a Drift target selector (nested within each band) picks which of that band's parameters the drift sliders are currently configuring. All 16 bands run simultaneously regardless of which one is being edited; all configured drift targets on a band run simultaneously regardless of which target is currently visible on the editing sliders.

The plugin processes incoming stereo audio with the input's stereo image preserved through each band.

---

## Signal Architecture

### Two modes

**Parallel bandpass** — each band's bandpass filter receives the full input, and the bands' outputs sum into the wet path. Frequencies not within any band's range are absent from the wet sum. Good for windscape voices, formant constructions on breath sources, vocoder-like noise textures, anywhere you want each band to be a discrete "voice" or "presence" rather than a shaping of the whole spectrum.

**Serial peaking EQ** — each band is a peaking EQ filter applied to the running signal in series. All frequencies pass through; only the chosen bands get boosted or cut. Good for tonal correction, formant emphasis on tonal sources, "make this region brighter / darker" work.

The Mode slider chooses between the two. Default is Parallel bandpass.

### Per-band cascade order (parallel mode only)

In parallel mode, each band can cascade 1, 2, 4, or 8 SVF bandpass stages. Each cascade step doubles the asymptotic rolloff slope on both sides of the band:

- Order 1: -6 dB/octave (gentle, broadband bleed-through past the band's edges)
- Order 2: -12 dB/octave
- Order 4: -24 dB/octave (focused)
- Order 8: -48 dB/octave (near brick-wall isolation)

Higher orders use proportionally more CPU per band. Each band has its own Order setting via the per-band selector.

Cascade narrows the effective bandwidth somewhat compared to a single stage — compensate by widening the Width sliders if needed.

### Per-band multi-target drift

Each band can configure independent drift modulation on up to five target parameters simultaneously:

- Frequency: band's center pitch wanders
- Width up: bandwidth above center breathes wider and narrower
- Width down: bandwidth below center breathes
- Gain: band's level pulses (tremolo)
- Pan: band wanders in the stereo image

Each drift target has its own Drift up / Drift down / Drift period / Drift period mode / Drift shape, stored independently per (band, target). Drift phases are initialized randomly on plugin load so multiple bands or multiple drift targets on the same band do not synchronize unless deliberately configured to.

This is the windscape engine: configure one band with simultaneous drifts on Frequency, Gain, and Pan at different periods (e.g., 47s, 13s, 23s). The single voice wanders in pitch, brightens and dims, and sweeps in stereo space — all uncorrelated. A handful of such bands at different center frequencies produce dense evolving texture without any global rhythm.

---

## Parameters

### Global

**Input Gain (dB)** `-24.0 to +24.0, default 0.0`
Pre-gain applied to the input signal before any band processing.

**Mode** `Parallel bandpass / Serial peaking EQ, default Parallel bandpass`
Choose the filter topology. See Signal Architecture.

**Wet/Dry mix** `0 to 1, default 0.5`
Blend between the original input and the band-processed signal. At 0 the input passes through unchanged; at 1 only the processed signal is heard.

**Output Volume** `0 to 1, default 0.5`
Final output level.

### Band selector

**Band selector** `0 to 15`
Picks which band the per-band sliders are currently editing. Moving the selector causes all per-band sliders to snap to that band's stored values. All 16 bands continue running regardless of which is being edited.

### Per-band sliders

The following sliders show the SELECTED band's values. Changes are stored to that band's slot when no selector has just moved.

**Frequency (Hz)** `0 to 20000, default 500`
Center frequency of the band. At very low Frequency the SVF coefficient becomes tiny and the band naturally fades to silence — sub-audible frequency sweeps that cross 0 work gracefully. Internally clamped to 1 Hz minimum and srate × 0.45 maximum for filter stability.

**Width up (Hz above center)** `1 to 5000, default 250`
How far above the center frequency the band extends.

**Width down (Hz below center)** `1 to 5000, default 250`
How far below the center frequency the band extends.

Symmetric widths keep the user's Frequency value as the actual filter center. Asymmetric widths shift the filter center toward the wider side while keeping Frequency as the reference. Narrow widths produce peaky resonant character; wide widths produce broad emphasis. Resonance is implicit in narrowness — there is no separate sharpness or Q knob.

**Gain (dB)** `-60 to +24, default -60 (off)`
The band's level. -60 dB is treated as "off" — the band's filter computation is skipped entirely to save CPU and the band contributes nothing.

In Parallel mode, Gain is converted to a linear multiplier on the bandpass output: 0 dB = full filter output level, +6 dB = double, -6 dB = half.

In Serial mode, Gain is the peaking EQ's dB gain at center: 0 dB = transparent (band has no effect), +6 dB = +6 dB boost at center, -12 dB = -12 dB cut.

**Pan** `-1.0 to +1.0, default 0`
Stereo balance for this band. At 0 the input's stereo image passes through the band unchanged (L filtered to L, R filtered to R). At -1 the band sits fully on the left side; at +1 fully on the right.

**Order (parallel mode only)** `1 / 2 / 4 / 8, default 1`
Cascade depth controlling rolloff steepness. See Signal Architecture. Ignored in Serial peaking EQ mode (the biquad has its own fixed shape).

### Per-band drift sliders (nested within band selector)

The Drift target slider picks which of the band's parameters the drift up/down/period/mode/shape sliders are currently editing. Each band remembers its last selected drift target across band selector changes.

When the drift target changes within a band, the previous target's drift continues to run with its stored settings; the drift sliders now show the new target's stored settings (or zero defaults if that target has not yet been configured for this band).

**Drift target** `Frequency / Width up / Width down / Gain / Pan, default Frequency`
Which parameter the drift modulates for the currently selected band.

**Drift up amount** `0 to 1000, default 0`
Maximum upward excursion of the drift, in the target parameter's natural units (Hz for Frequency, Width up, Width down; dB for Gain; -1 to +1 scale for Pan). Typical values: 50–500 for frequency / width drift, 3–12 for gain drift, 0.2–1.0 for pan drift.

**Drift down amount** `0 to 1000, default 0`
Maximum downward excursion. Asymmetric Up vs Down lets the drift sit slightly off-center for a biological-feel rather than purely symmetric.

**Drift period** `0 to 1000, default 0`
Length of one drift cycle, interpreted by Drift period mode. **A period of 0 disables this drift target for this band**, even if Drift up and Drift down are non-zero.

**Drift period mode** `BPM / Hz / Seconds, default Seconds`
- BPM — Drift period is in beats per minute; cycles per second = period / 60.
- Hz — Drift period is in Hz; cycles per second = period.
- Seconds — Drift period is in seconds; cycles per second = 1 / period.

**Drift shape** `Sine / Triangle / Random, default Sine`
Wander waveform. Sine is smooth continuous wander; Triangle has linear ramps with turnaround points; Random picks new value-noise targets at each cycle boundary and interpolates smoothly between them (not white noise — still smooth, just unpredictable in direction).

---

## Usage Notes

- **Bands default to off.** On plugin load every band has Gain at -60 dB and contributes nothing. Configure bands one at a time via the selector pattern; raise Gain above -60 dB to activate. The plugin output equals the input × Wet/Dry mix when no bands are active.
- **The selector pattern keeps the slider count constant regardless of band count.** Each band's parameters appear on the same fixed set of sliders rather than expanding the slider count linearly with band count. This matters for screen-reader navigation and is the reason the plugin can have 16 bands × 5 drift targets without an unmanageable slider list.
- **Multi-target drift on a single band is the windscape technique.** Configure one band with simultaneous drifts on Frequency, Gain, and Pan at different periods. The resulting voice wanders in pitch, brightens and dims, and sweeps in stereo space — all uncorrelated. A few such bands at different center frequencies produce dense evolving texture without any global rhythm.
- **Cascade order is the rolloff fix.** If you set narrow widths and still hear broadband content behind the band's ring, the issue is rolloff steepness (single-stage SVF has -6 dB/oct skirts that let plenty of noise through). Raise Order. Order 8 with narrow widths gives genuine isolation; Order 1 is appropriate for textural windscape voices where you want some bleed.
- **Stereo image preservation.** Each band runs L and R bandpass filters independently with shared parameters. The dry input's stereo image survives the wet path naturally; per-band Pan then shifts each band's balance from the preserved-image starting point.
- **Drift on Width up and Width down breathes the band.** With Drift target = Width up and a slow Drift period, the band's upper edge expands and contracts over time. Combined with a Drift on Width down, both edges wander, making the band's bandwidth itself wander. The center stays static but the band breathes wider and narrower.
- **Drift periods are per-band-per-target.** Three drifts on the same band at periods 47s, 13s, 23s never align exactly into a global rhythm — each cycles on its own schedule.
- **Mode swap during playback is safe.** Filter states for Parallel and Serial are maintained independently and stay warm even when the corresponding mode isn't active, so switching modes does not click.

---

*Resonance Bank is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

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

**Tempo (BPM)** `30-300 BPM, default 120`
The tempo of the beat track in beats per minute.

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

### Speed Ramp

In-plugin tempo morph over time, without automation envelopes. Single-target plugin (Tempo BPM is the only ramp target), so no selector — slider 17 is directly the signed `by` amount in BPM.

**Speed ramp by (BPM) (slider 17)** `-270 to +180, step 0.1, default 0`
Signed BPM delta. **0** = no change (safe default — engaging at 0 produces no effect). **Negative** = slow down (`-60` ramps Tempo from 120 → 60 BPM over the duration). **Positive** = speed up.

**Speed ramp duration (slider 18)** `0–60 minutes, default 0` · **Speed ramp engage (slider 19)** `Off / On, default Off` · **Speed ramp start delay (slider 20)** `0–60 minutes, default 0`

Engage is a freeze/resume gate (NOT a restart edge): while On, ramp_t advances 0 → 1 over the duration; while Off, it freezes wherever it is and resumes from there on re-engage. Start delay waits N minutes after engage before ramp_t starts advancing.

**Transport behavior:** speed_ramp_t resets to 0 on every transport play edge. This is the ONLY thing that resets the ramp — slider changes (engage toggle, anything) don't restart it. The accent grid, swing, and drift wave all follow the effective tempo automatically.

**Migration from v2.7:** slider 17 changed from multiplier (0.1–4.0) to signed BPM delta. Existing projects' multiplier value gets interpreted as a tiny BPM delta — effectively Speed Ramp "off" until reconfigured.

### Drift

Slow organic wander applied to the tempo on top of Speed Ramp, giving the metronome a slightly human-feeling drift rather than a perfectly fixed click. See [Per-Plugin Drift](#per-plugin-drift) for the architecture; the seven sliders below configure it for this plugin.

**Musical Period (beats)** `1–256, default 32`
Period of the musical drift source, measured in beats at the current Tempo. Scales with Speed Ramp.

**Musical Up by** `0.0–1.0, default 0`
How far above the center tempo the musical drift wanders at its peak, as a multiplier amplitude.

**Musical Down by** `0.0–1.0, default 0`
How far below the center tempo the musical drift wanders at its trough. Independent from Up by.

**Slow Period (minutes)** `0.1–60, default 5`
Period of the slow drift source, measured in wall-clock minutes. Does NOT scale with Speed Ramp.

**Slow Up by** `0.0–1.0, default 0`
Above-center amplitude for the slow drift source.

**Slow Down by** `0.0–1.0, default 0`
Below-center amplitude for the slow drift source.

**Shape** `Sine / Triangle / Random, default Sine`
Wander shape applied to both sources.

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

# Shepard Scale Generator

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Shepard Scale Generator is a step sequencer that produces the Shepard scale auditory illusion — a chromatic sequence in which each successive note sounds higher than the last, yet after twelve steps the sequence arrives back where it started with no sense of having moved. Each note in the sequence triggers a stack of octave-spaced oscillators shaped by a bell-curve amplitude window, so the pitch class is clearly defined but no single octave dominates.

The plugin generates no audio from an input signal. It is a pure synthesizer.

---

## Signal Architecture

The sequencer steps through up to twelve chromatic notes (C through B) at a rate set by the BPM parameter. On each beat, the active note's oscillator stack is triggered with an envelope shaped by the Attack, Release, and Note Length parameters. Each note has twelve oscillator slots, one per possible octave layer. The number of active layers is set by Octave Count, and their amplitude is shaped by a cosine bell curve centered on Center Octave — oscillators near the center are loud, oscillators near the edges fade toward silence. This bell shaping is what creates the illusion: the ear perceives the pitch class clearly but cannot anchor to a specific octave.

All active notes are summed and normalized by the oscillator count each sample.

---

## Parameters

### Global Controls

**BPM** `10-300 BPM, default 120`
The tempo of the sequence in beats per minute.

**Direction** `Asc / Desc`
The order in which notes are stepped through. Ascending moves C → C# → D → ... → B → C. Descending moves in reverse.

**Inactive Notes** `Skip / Rest`
Determines how notes with Active set to Off are handled.
- **Skip** — inactive notes are skipped entirely; the sequencer advances to the next active note immediately.
- **Rest** — inactive notes hold silence for their full beat duration before advancing.

**Attack %** `0-100%, default 10`
The fraction of each beat spent fading the note in from silence. At 0% the note begins at full amplitude immediately.

**Release %** `0-100%, default 10`
The fraction of each beat spent fading the note out. At 0% the note cuts off at the end of its on-time without fading.

> If Attack % + Release % exceeds 100%, both are scaled down proportionally to fit.

**Note Length %** `1-100%, default 100`
The fraction of each beat during which the note is present. At 100% the note occupies the full beat. At 50% the note plays for the first half of the beat then falls silent for the second half.

**Octave Count** `2-12, default 8`
The number of oscillator layers stacked per note, and the width of the pitch window in octaves. Higher values produce a richer, more ambiguous pitch quality; lower values sound thinner but more distinct.

**Center Octave** `0-8, default 4`
The octave at the center of the amplitude bell curve. Oscillators nearest this octave are loudest; those further away fade toward silence at the window edges. Adjusting this shifts the perceived register of the entire sequence.

**Waveform** `Sine / Triangle / Saw / Golden TS / Golden SG / Golden GS / Bell / Wavefold / Half-sine / Phi-cascade / Phi Triangle / Phi Sine`
The oscillator waveform used by all notes simultaneously. Sine is the cleanest choice for the Shepard illusion — additional harmonics can muddy the perceived register-wrap. The richer waveforms (Bell, Phi-cascade, etc.) are still available if you want the illusion to sit inside a more textured tone. See Polyrhythm Phase for waveform descriptions, including the back-compat note on the Golden / Phi family.

**Binaural Beat Hz** `0-100 Hz, default 0`
Offsets the right channel oscillator frequencies by this many Hz, adding a binaural beat across all notes simultaneously.

**Tuning Reference Hz** `400-480 Hz, default 440`
The A4 reference frequency used to calculate all note pitches.

---

### Per-Note Controls (C through B)

Each of the twelve chromatic notes has three parameters.

**Active** `Off / On`
Enables or disables this note in the sequence. When off, behavior depends on the Inactive Notes setting. The gain and pan controls for this note are hidden when inactive.

**Gain dB** `-60–+6 dB, default 0`
Volume of this note relative to the others. Allows individual notes to be emphasized or de-emphasized within the sequence. Hidden when the note is inactive.

**Pan** `-100–+100, default 0`
Stereo position of this note. Negative values place it left, positive values right, 0 is center. Uses constant-power panning. Hidden when the note is inactive.

### Start Delay

**Start Delay (beats)** `0–1000, default 0`

Silent for N beats after playback starts, then the scale begins normally. Beats are counted at the BPM slider (the same slider that sets the note pacing) — at 60 BPM, "4 beats" is 4 seconds; at 120 BPM it's 2 seconds. Oscillator phases and note-step state stay frozen during the delay so the first note of the scale lands cleanly at delay-end. Re-arms on every transport stop/start. 0 disables the delay.

### Play / Rest Gating (v2.1)

**Play for (beats)** `0–1000, default 0`
**Rest for (beats)** `0–1000, default 0`
**Rest mode** `Walk through / Freeze in place, default Walk through`

A per-beat cyclic gate. The scale fires **Play for** notes normally, then sits silent for some number of beats determined by **Rest for** + **Rest mode**, then resumes — the pattern repeats forever. Useful for phrase-and-pause scale playback or contemplative gaps between rising / descending phrases.

The feature is **disabled when either of Play for / Rest for is 0** (the default). With both at 0, the scale behaves as before; Rest mode has no effect when the gate is off.

**Rest mode** picks one of two fundamentally different behaviors for what the sequencer does during the rest period:

- **Walk through** (default): the sequencer keeps advancing through notes during rest. Each rest beat moves the current note forward silently. If `Play + Rest` doesn't divide evenly into your active-note count, the starting note of each play period walks across the scale — `Play=4, Rest=4` with all 12 notes active means cycle 1 plays C–D#, cycle 2 plays G#–B, cycle 3 plays E–G, and you return to C after three cycles. Notes get "skipped" in the literal sense (the sequencer walks past them silently); they reappear in subsequent play periods at different positions. Good for **abstract / pattern-shifting use** where the walking-start effect is part of the appeal.
- **Freeze in place**: the sequencer pauses on the note that would have fired when rest began. Rest duration is `Rest for × one beat (60/BPM seconds)`, timed by a sample counter rather than a beat count. When rest ends, the frozen note fires and the scale continues from there — **every note plays in order across multiple cycles, just with pauses between phrases**. Good for **complete-scale-with-rests use** where you want to hear every step of the Shepard illusion in order.

**Tails finish naturally.** When PR transitions to rest, the previously-firing note's beat envelope continues to decay via the per-note smoother (the same one that already smooths the crossfade between notes). No special anti-click logic is needed — the existing envelope smoothing handles the transition.

**Inactive Notes + Play/Rest interaction.** In **Skip mode** (the default for Inactive Notes), inactive notes are jumped past, so "one beat" always equals "one active-note step." In **Rest mode** for Inactive Notes, inactive notes consume their full beat silently — they still count as a Play/Rest step. So with Inactive Notes = Rest and some notes inactive, Play for = 4 may include a couple of silent-anyway beats within the audible 4-note phrase.

**Transport behavior**: conventional. Stop silences; play re-initializes everything (sequence position, beat phase, period counter, rest state) and starts fresh from the first beat of seq_pos = 0 (C).

**Changing Rest mode mid-rest** is handled defensively but not gracefully — the safest move is to flip the slider while the gate is in its play period, or to press stop/play to reset cleanly. The plugin won't crash but the current rest period may stretch or compress unexpectedly.

### Speed Ramp

In-plugin tempo morph over time, without automation envelopes. Single-target plugin (BPM is the only ramp target), so no selector — slider 52 is directly the signed `by` amount in BPM.

**Speed ramp by (BPM) (slider 52)** `-290 to +180, step 0.1, default 0`
Signed BPM delta. **0** = no change. **Negative** = slow down (`-60` ramps BPM from 120 → 60 over the duration). **Positive** = speed up.

**Speed ramp duration (slider 53)** `0–60 minutes, default 0` · **Speed ramp engage (slider 54)** `Off / On, default Off` · **Speed ramp start delay (slider 55)** `0–60 minutes, default 0`

Engage is a freeze/resume gate (NOT a restart edge): while On, ramp_t advances 0 → 1 over the duration; while Off, it freezes wherever it is and resumes from there on re-engage. The Freeze-mode Play/Rest rest timer also scales with Speed Ramp so the rest duration tracks the same effective tempo as the play period.

**Transport behavior:** speed_ramp_t resets to 0 on every transport play edge. This is the ONLY thing that resets the ramp — slider changes don't.

**Migration from v2.7:** slider 52 changed from multiplier (0.1–4.0) to signed BPM delta. Old projects' multiplier value gets interpreted as a tiny BPM delta — Speed Ramp effectively "off" until reconfigured.

### Drift

Slow organic wander applied to the scale's pace on top of Speed Ramp — the rising or descending illusion still works, just with the pace drifting up and down instead of running at one fixed rate. See [Per-Plugin Drift](#per-plugin-drift) for the architecture; the seven sliders below configure it for this plugin.

**Musical Period (beats)** `1–256, default 32`
Period of the musical drift source, measured in scale beats at the current BPM. Scales with Speed Ramp.

**Musical Up by** `0.0–1.0, default 0`
How far above the center tempo the musical drift wanders at its peak, as a multiplier amplitude.

**Musical Down by** `0.0–1.0, default 0`
How far below the center tempo the musical drift wanders at its trough. Independent from Up by.

**Slow Period (minutes)** `0.1–60, default 5`
Period of the slow drift source, measured in wall-clock minutes. Does NOT scale with Speed Ramp.

**Slow Up by** `0.0–1.0, default 0`
Above-center amplitude for the slow drift source.

**Slow Down by** `0.0–1.0, default 0`
Below-center amplitude for the slow drift source.

**Shape** `Sine / Triangle / Random, default Sine`
Wander shape applied to both sources.

---

## Usage Notes

- **The illusion depends on Octave Count and the bell window.** Too few layers (2-3) and individual octave jumps become audible. Eight or more layers produce the smoothest illusion.
- **Center Octave shifts register without changing pitch classes.** Lowering it pushes the perceived center of the sequence down; raising it pushes it up. The illusion remains intact.
- **Attack and Release are proportions of Note Length, not the full beat.** With Note Length at 50%, an Attack of 20% means the note spends 20% of its 50% window fading in — 10% of the total beat.
- **Binaural beat applies uniformly across all notes.** There is no per-note binaural amount. For entrainment use, keep the value consistent with your target beat frequency.
- **Skip vs Rest affects rhythmic feel significantly.** With many inactive notes, Skip produces a sparse irregular rhythm; Rest maintains the underlying pulse with silences in place of notes.

---

*Shepard Scale Generator is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

# Shepard Tone Generator

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Shepard Tone Generator produces the Shepard-Risset glissando — a continuous auditory illusion of pitch that sweeps endlessly upward or downward without ever actually arriving anywhere. Unlike the Shepard Scale, which steps through discrete notes, this plugin sweeps continuously, producing a tone that feels like it is perpetually rising (or falling) through pitch space.

Up to eight simultaneous voices allow complex chord textures, counterpoint (voices moving in opposite directions), or polyrhythmic drift patterns. Each voice is an independent continuous sweep, rooted on a different pitch class.

The plugin generates no audio from an input signal. It is a pure synthesizer.

---

## Signal Architecture

Each voice maintains a stack of oscillators spread across a pitch window exactly as wide as the Octave Count setting. All oscillators in a voice sweep continuously in the same direction — upward or downward — at a rate determined by the Rate parameters. Each oscillator's amplitude is shaped by a fade-in / fade-out window: loud near the center of the pitch range, silent at the edges. When an oscillator sweeps out of the top of the window it wraps silently to the bottom and begins fading in again. Because the window width equals the oscillator spacing (always exactly one octave), wraps are always seamless.

All active voices are summed and normalized by active voice count and oscillator count each sample.

---

## Parameters

### Global Controls

**Drift Mode** `Synced / Independent`
Sets how per-voice sweep rates are determined.
- **Synced** — all voices share the global Rate Value as their sweep speed. Each voice's Drift slider adds a cents offset to its oscillators, creating subtle detuning without changing the underlying rate.
- **Independent** — the global Rate Value is ignored. Each voice's Drift / Rate slider sets that voice's sweep rate directly, in the units set by Rate Mode. Voices can sweep at entirely different speeds.

**Rate Mode** `BPM / Seconds / Hz`
Unit for interpreting rate values.

**Rate Value** `0.001-1000, default 0.5 BPM`
The global sweep rate, in the units set by Rate Mode. Only used in Synced mode. At 0.5 BPM, one full sweep cycle takes two minutes — appropriate for slow ambient use.

**Octave Count** `2-16, default 8`
The number of oscillator layers per voice and the width of the pitch window in octaves. Higher values produce a richer, denser texture. Also controls the spacing — oscillators are always exactly one octave apart regardless of count.

**Center Octave** `0-8, default 3`
The octave at the center of the pitch window. All voices sweep through a range centered here. Lower values produce a deeper, more bass-heavy texture.

**Fade In %** `0-100%, default 20`
The fraction of each sweep cycle spent fading in at the bottom of the pitch window. Lower values produce a sharper entry; higher values a longer crossfade.

**Fade Out %** `0-100%, default 20`
The fraction of each sweep cycle spent fading out at the top of the pitch window. Fade In and Fade Out together determine how much of the window is at full volume.

> If Fade In % + Fade Out % exceeds 100%, both are scaled down proportionally.

**Waveform** `Sine / Triangle / Saw / Golden TS / Golden SG / Golden GS / Bell / Wavefold / Half-sine / Phi-cascade / Phi Triangle / Phi Sine`
The oscillator waveform used by all voices simultaneously. Sine produces the purest Shepard illusion — fewer harmonics means a cleaner register-wrap. The richer waveforms (Bell, Phi-cascade, etc.) are available if you want the illusion to sit inside a more textured tone. See Polyrhythm Phase for waveform descriptions, including the back-compat note on the Golden / Phi family.

**Binaural Beat Hz** `0-100 Hz, default 0`
Offsets the right channel oscillator frequencies by this many Hz, adding a binaural beat across all voices and oscillators simultaneously.

**Root Note** `C / C# / D / D# / E / F / F# / G / G# / A / A# / B, default C`
The global tonic. Per-voice Note sliders are interpreted as offsets from this value. Setting Root Note to D and a voice Note to E produces F# (D + a major second).

**Tuning Reference Hz** `400-480 Hz, default 440`
The A4 reference frequency used to calculate all oscillator pitches.

---

### Per-Voice Controls (Voices 1-8)

Each voice has five parameters. Voice 1 is active by default; Voices 2-8 are inactive.

**Vn Note** `C / C# / D / D# / E / F / F# / G / G# / A / A# / B`
The pitch class of this voice, relative to Root Note. Combined with Root Note, this determines the interval relationship between voices.

**Vn Pan** `-100–+100, default 0`
Stereo position of this voice. Negative values place it left, positive values right, 0 is center. Uses constant-power panning. Pan and binaural beats can be used simultaneously — the binaural beat is preserved across the pan field.

**Vn Direction** `Asc / Desc`
Whether this voice sweeps upward or downward. Setting two voices to opposite directions creates counterpoint — one pitch class continuously rising, another continuously falling.

**Vn Drift / Rate** `-1000–+1000, default 0`
In Synced mode: a cents offset applied to all of this voice's oscillators. Positive values pitch the voice slightly sharp; negative values slightly flat. Creates subtle beating between voices without changing their sweep rates.
In Independent mode: this voice's sweep rate directly, in the units set by Rate Mode.

**Vn Gain dB** `-60–+6 dB, default 0`
Per-voice output level, applied before the voice is summed into the mix.

**Vn Active** `Off / On`
Enables or disables the voice. Inactive voices contribute nothing to the output and are excluded from normalization.

### Start Delay

**Start Delay** `0–1000, default 0`

Silent for N units after playback starts, then the Shepard tone(s) begin normally. Units match Rate Mode (BPM beats / Seconds / Hz cycles), interpreted against Rate Value. Oscillator phases stay frozen during the delay so the illusion begins cleanly at delay-end rather than mid-sweep. Re-arms on every transport stop/start. 0 disables the delay.

### Play / Rest Gating (v2.1)

**Play for (cycles)** `0–1000, default 0`
**Rest for (cycles)** `0–1000, default 0`
**Rest mode** `Walk through / Freeze in place, default Walk through`

A cyclic gate over the continuous glissando. Voices play normally for **Play for** cycles, sit silent for **Rest for** cycles, then resume — the pattern repeats forever. Useful for breathing-room ambient where the sweep illusion is interrupted by silences.

The cycle unit is the same as Start Delay: Rate Mode units measured against Rate Value. At Rate Value = 0.5 Hz, "4 cycles" = 8 seconds; at 120 BPM, "4 cycles" = 2 seconds; at Rate Value = 2 in Seconds mode, "4 cycles" = 8 seconds.

The feature is **disabled when either of Play for / Rest for is 0** (the default). With both at 0, the plugin behaves as before; Rest mode has no effect when the gate is off.

**Rest mode** picks one of two behaviors for what the oscillators do during rest:

- **Walk through** (default): oscillators keep sweeping during rest, just silently. When rest ends, you hear the tone wherever the sweep happened to be — the position has shifted during the silent stretch. Preserves the "the glissando is always running, the gate just controls output" feel. Each play period starts at a different point in the sweep, so the resumed harmonic content varies cycle-to-cycle.
- **Freeze in place**: oscillators stop sweeping during rest, frozen at their current frequencies and phases. When rest ends, the tone resumes from exactly where it left off. Preserves the "pause and resume continuous motion" feel. Each play period starts where the previous one ended.

For short rests with slow sweep rates the difference between modes is subtle (small position shift). For long rests with fast sweep rates the difference is clearly audible — Walk re-positions the harmonics each cycle, Freeze always resumes at the pre-rest position.

**Anti-click**: the existing 8 ms per-oscillator gain smoother handles all rest entry / exit transitions. When rest starts, `target_gain` is forced to 0 and the smoother decays each oscillator's audio output to silence over ~40 ms. When rest ends, target_gain returns to its window-based value and the smoother ramps gain back up. Same mechanism that prevents clicks during normal sweep wraps.

**Independent drift mode**: the Play/Rest counter uses base_rate_hz (from the Rate Value slider) as its clock, regardless of drift_mode. So in Independent mode where each voice has its own rate, the gate still fires at the global Rate Value cadence — voices all gate on and off together even though their individual sweeps are at different rates. This matches Start Delay's behavior on this plugin.

**Transport behavior**: conventional. Stop silences; play re-initializes everything (oscillator positions, rest state, cycle counter) and starts fresh in its play period from cycle 0.

### Speed Ramp

In-plugin sweep-rate morph over time. Lets you slow the glissando illusion down (or speed it up) without touching automation.

**Speed ramp by (slider 64)** `-1000 to +1000, step 0.001, default 0`
Signed delta added to the Rate Value over the duration. **0** = no change (safe default). The delta is interpreted in **the rate's currently-displayed unit** — so:

- If Rate Mode is **BPM** and Rate Value is 60, setting `by -30` ramps the sweep from 60 BPM → 30 BPM (slower).
- If Rate Mode is **Hz** and Rate Value is 0.5, setting `by -0.25` ramps from 0.5 Hz → 0.25 Hz (slower).
- If Rate Mode is **Seconds** (period) and Rate Value is 2, setting `by +1` stretches the period from 2 sec → 3 sec (slower).

In BPM and Hz modes, **negative = slower**. In Seconds mode, **positive = slower** (longer period). The audible pitch of any oscillator is NOT scaled — only the rate at which oscillators sweep through the pitch window. The Play/Rest cycle counter scales with the ramp too.

**Speed ramp duration (slider 65)** `0–60 minutes, default 0` · **Speed ramp engage (slider 66)** `Off / On, default Off` · **Speed ramp start delay (slider 67)** `0–60 minutes, default 0`

Engage is a freeze/resume gate (NOT a restart edge): while On, ramp_t advances 0 → 1 over the duration; while Off, ramp_t freezes wherever it is and resumes from there on re-engage. Start delay waits N minutes after engage before ramp_t actually starts advancing.

**Transport behavior:** speed_ramp_t resets to 0 on every transport play edge. This is the ONLY thing that resets the ramp — slider changes don't.

**Migration from v2.7:** slider 64 changed from a multiplier (0.1–4.0) to a signed delta in rate-units. Old projects' multiplier value will be interpreted as a tiny delta — Speed Ramp effectively "off" until reconfigured.

### Drift

Slow organic wander applied to the glissando sweep rate on top of Speed Ramp — the rising/falling illusion still feels endless, but the pace breathes rather than running at one fixed speed. See [Per-Plugin Drift](#per-plugin-drift) for the architecture; the seven sliders below configure it for this plugin.

**Musical Period (cycles)** `1–256, default 32`
Period of the musical drift source, measured in sweep cycles of the global Rate Value. Scales with Speed Ramp.

**Musical Up by** `0.0–1.0, default 0`
How far above the center sweep rate the musical drift wanders at its peak, as a multiplier amplitude.

**Musical Down by** `0.0–1.0, default 0`
How far below the center sweep rate the musical drift wanders at its trough. Independent from Up by.

**Slow Period (minutes)** `0.1–60, default 5`
Period of the slow drift source, measured in wall-clock minutes. Does NOT scale with Speed Ramp.

**Slow Up by** `0.0–1.0, default 0`
Above-center amplitude for the slow drift source.

**Slow Down by** `0.0–1.0, default 0`
Below-center amplitude for the slow drift source.

**Shape** `Sine / Triangle / Random, default Sine`
Wander shape applied to both sources.

---

## Usage Notes

- **The illusion works because no single octave dominates.** The bell-shaped amplitude window ensures that as one oscillator fades out at the window edge, an identical one is fading in at the other edge. The listener perceives continuous directional motion with no anchor point.
- **Fade In and Fade Out control the crossfade quality.** At 20%/20%, the middle 60% of the window plays at full volume with 20% ramps at each edge. At 50%/50%, the entire window is one continuous crossfade — no hold at full volume, maximum smoothness.
- **Multiple voices create Shepard chords.** Enabling voices on different note intervals (e.g. C, E, G for a major triad) produces a sweeping chord where all voices move in parallel. Each voice can be panned independently for spatial spread.
- **Independent mode with different rates creates polyrhythmic sweep textures.** One voice sweeping at 0.3 BPM and another at 0.5 BPM will periodically converge and diverge in unpredictable ways.
- **Pan and binaural beats are complementary.** Unlike some other plugins in this suite, Shepard Tone's pan implementation preserves the binaural beat when voices are panned — the L/R frequency difference is maintained across the stereo field.
- **Root Note transposes the entire plugin at once.** Changing Root Note shifts all voices simultaneously by the same interval, making it suitable for automation-based key changes.

---

*Shepard Tone Generator is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*
*Designed by Rozaya — Developed with Claude (Anthropic)*
