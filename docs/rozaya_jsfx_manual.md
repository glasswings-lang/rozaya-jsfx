# Rozaya JSFX Plugin Suite
## User Manual

*Designed by Rozaya â€” Developed with Claude (Anthropic)*

---

## Table of Contents

- [Acknowledgements](#acknowledgements)

**Synthesizers**
- [Heartbeat Generator](#heartbeat-generator)
- [Breath Generator](#breath-generator)
- [Womb Sound Generator](#womb-sound-generator)
- [Polyrhythm Phase](#polyrhythm-phase)
- [Melody Phase](#melody-phase)

**Effects**
- [Resonant Sweeping Filter](#full-feature-sweeping-filter)
- [Sweep Dwell Filter](#sweep-dwell-filter)
- [Full Feature Tremolo](#full-feature-tremolo)

**Utilities**
- [Rhythm Track](#rhythm-track)
- [Shepard Scale Generator](#shepard-scale-generator)
- [Shepard Tone Generator](#shepard-tone-generator)

---

# Acknowledgements

## Authorship

All plugins in this suite were designed by Rozaya. Code was written by Claude (Anthropic) under Rozaya's direction. Rozaya determined the concept, feature set, signal architecture, parameter design, and all creative and functional decisions for each plugin. Claude implemented those decisions in JSFX.

## Inspirations and Prior Art

Several plugins in this suite were developed with reference to existing implementations in common DAW tools. In all cases, the code was written independently â€” no source code was copied or derived from any external implementation. The conceptual influence is acknowledged here:

- **Rhythm Track** â€” rhythmic metronome generation concepts drawn from existing DAW metronome implementations.
- **Resonant Sweeping Filter** and **Sweep Dwell Filter** â€” filter sweep concepts informed by resonant lowpass filter implementations found in standard DAW effect libraries.
- **Full Feature Tremolo** â€” tremolo concepts informed by existing DAW tremolo implementations, substantially expanded with shaped envelopes, stereo phase control, and pan modulation.

The **Heartbeat Generator**, **Womb Sound Generator**, **Breath Generator**, **Polyrhythm Phase**, **Shepard Tone Generator**, and **Shepard Scale Generator** plugins are original concepts with no direct external inspiration for their architecture or feature sets.

## Technical Notes

The Cockos state-variable resonant lowpass filter topology used in several plugins is a well-known open implementation documented in the REAPER JSFX ecosystem. Its use here follows standard practice for the platform.


---

# Heartbeat Generator

**Designed by Rozaya â€” Developed with Claude (Anthropic)**

---

## Overview

Heartbeat Generator is a synthesized cardiac sound source. It produces a stereo binaural heartbeat using two resonant filter voices â€” a "near" and a "far" â€” shaped with independent attack and decay envelopes and mixed to create a sense of three-dimensional depth. The two heart sounds (S1 and S2, the "lub" and the "dub") have independently controllable pitch, volume, and decay, with a configurable systole interval between them.

Heart rate variability is modeled in two layers â€” a sine-wave breath modulation and a randomized low-frequency drift â€” giving the output an organic, living quality rather than a mechanical loop.

The plugin generates no audio from an input signal. It is a pure synthesizer and should be placed on an empty FX chain or a track with no audio source.

---

## Signal Architecture

Each heartbeat cycle produces two events: S1 and S2, separated by the systole interval. Both sounds are synthesized through the same architecture but with different parameters:

Each sound runs through two parallel resonant filter voices. The **near** voice is prominent and direct, with tighter resonance. The **far** voice uses slightly higher center frequencies, looser Q, and a slight frequency offset (S1 at Ã—1.003, S2 at Ã—0.997) to add natural detuning. Each voice's exciter blends a sine oscillator with white noise â€” S1 is weighted toward the oscillator (80/20), S2 toward noise (50/50), giving S2 a softer, more diffuse character.

Each voice passes through a double-cascaded lowpass after the resonant filter to smooth the output. The near and far voices are then routed to opposite output channels, with an inter-aural delay between them set by the Stereo Width parameter.

---

## Parameters

### Timing

**BPM** `20-200, default 70`
Base heart rate in beats per minute. This sets the cycle length before HRV modulation is applied. When HRV is active, the actual beat timing fluctuates around this value.

**Systole ms (S1â†’S2 gap)** `50-400 ms, default 120`
The delay between the S1 and S2 events within each cycle. Shorter values produce a tighter, faster lub-dub; longer values spread the sounds further apart. At very short values the sounds may overlap depending on decay settings.

---

### S1 â€” First Heart Sound ("Lub")

**S1 Volume** `0.0-1.0, default 1.0`
Output level for S1, applied after envelope shaping and independently of S2.

**S1 Decay ms** `10-200 ms, default 60`
How quickly S1 fades after its attack peak. Longer values produce a sustained, resonant thud; shorter values a sharper knock.

**S1 Frequency Hz** `20-120 Hz, default 45`
Base frequency of the S1 resonant filter. The near voice center is derived at Ã—1.1 and the far at Ã—1.28, so this value is the lower anchor of the frequency cluster. Lower values produce a deeper, more subsonic thump.

---

### S2 â€” Second Heart Sound ("Dub")

**S2 Volume** `0.0-1.0, default 0.7`
Output level for S2, independently of S1. S2 is typically quieter than S1 physiologically; the default reflects this.

**S2 Decay ms** `5-100 ms, default 25`
How quickly S2 fades. S2 is naturally shorter-lived than S1. Values under 10 ms produce a sharp click; 20-40 ms gives a natural dub character.

**S2 Frequency Hz** `60-300 Hz, default 80`
Base frequency for the S2 resonant filter. The near voice center is derived at Ã—1.15 and far at Ã—1.25.

---

### Tone

**Brightness** `0.0-1.0, default 0.3`
Controls the cutoff of the post-resonator lowpass applied to both voices. At 0.0 the filter sits around 200 Hz (near) / 175 Hz (far), keeping the sound very deep and muffled. At 1.0 it opens to approximately 450 Hz (near) / 395 Hz (far). Affects overall tonal character without changing the fundamental resonant frequencies.

---

### Stereo / Binaural

**Stereo Width ms (neg = heart right)** `-15.0â€“+15.0 ms, default 3.0`
The inter-aural delay between the near and far voices, creating a sense of spatial depth and positioning. Positive values place the near (prominent) voice on the left, which is anatomically correct for a heart positioned on the left side of the chest. Negative values flip this. Larger magnitudes create a stronger binaural effect. Crossing zero resets all filter states and clears the delay buffer to prevent artifacts.

---

### Heart Rate Variability

Both HRV systems modulate the cycle length in real time and operate additively.

**Breath Cycle Seconds** `1.0-30.0 sec, default 12.0`
The period of a sinusoidal breath modulation applied to heart rate, mimicking respiratory sinus arrhythmia â€” the natural tendency for heart rate to rise during inhale and fall during exhale. The modulation depth is set by Breath HRV Depth.

**Breath HRV Depth** `0.0-0.25, default 0.08`
How much the breath sine wave shifts the BPM. A value of 0.08 produces approximately Â±8% variation around the base rate. At 0.25 the swing is Â±25%. At 0.0 breath HRV is disabled.

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

### Speed Ramp (new)

In-plugin slowdown / speedup over time, designed for sleep use without needing automation envelopes.

**Speed ramp target (multiplier)** `0.1–4.0, default 1.0`
The multiplier the ramp moves toward. **0.5** = half speed (BPM slider 70 → effective 35), **2.0** = double speed (70 → 140), **1.0** = no change. Always relative to the current BPM slider, so adjusting BPM mid-ramp scales the target accordingly.

**Speed ramp duration (minutes)** `0–60, default 0`
How long the ramp takes from start to target. **0** disables the ramp entirely — the multiplier stays wherever it currently is.

**Speed ramp engage** `Off / On, default Off`
Off = ramp is not advancing. On = ramp advances from its current position toward the target over the duration.

**How it behaves.** Flipping engage Off → On captures the current multiplier as the ramp's starting point and begins easing toward the target over the duration. When it reaches the target it stays there until you change something. Flipping engage On → Off **freezes** the multiplier at its current position — it does NOT snap back to 1.0. To return to normal speed, set target = 1.0 and re-engage.

A small ~100 ms smoother also sits between the BPM slider and the audio, so manual BPM tweaks no longer click. This is always on; you don't have to do anything to get it.

**Transport behavior**: resets on stop/play just like Start Delay and Play/Rest. The multiplier returns to 1.0 and the ramp clock restarts on every play press. If you want the ramp to begin from a non-1.0 starting point on play, set the BPM slider to the value you want at start and use the multiplier to ramp away from 1.0; the multiplier's "1.0 = current BPM" anchor means the BPM slider IS your starting rate.

---

## Usage Notes

- **Near and far voices are always both active.** The stereo output is the near voice on one channel and the delayed far voice on the other. There is no mono sum option â€” summing to mono will produce some comb filtering.
- **BPM is a base rate, not a locked tempo.** When HRV is active the beat timing will not align to a DAW grid. For grid-locked output, set both HRV depth parameters to 0.
- **S1 and S2 can overlap** if Systole ms is very short relative to S1 Decay ms. This produces a compressed, tachycardic character.
- **Crossing zero on Stereo Width** resets all filter states and clears the delay buffer. There will be a brief silence on the transition.

---

*Heartbeat Generator is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya â€” Developed with Claude (Anthropic)*


---

# Breath Generator

**Designed by Rozaya â€” Developed with Claude (Anthropic)**

---

## Overview

Breath Generator is a synthesized breathing sound source. It produces a continuous, looping breath cycle â€” inhale, pause, exhale, pause â€” with independent control over the duration, tone, and envelope shape of each phase. The output is stereo, with the left and right channels using slightly offset filter frequencies to create a naturally decorrelated image.

The plugin generates no audio from an input signal. It is a pure synthesizer and should be placed on an empty FX chain or a track with no audio source.

---

## Signal Architecture

Each inhale and exhale phase is produced by passing independent white noise through a state-variable lowpass filter â€” a separate filter instance per channel. The L and R channels use different noise seeds, so their noise is naturally decorrelated before filtering. The Stereo Width parameter then spreads the filter frequencies slightly apart between channels, widening the image further.

The envelope applied to each phase is a simple amplitude shape â€” fade in from silence, hold at full level, fade out to silence â€” with the fade proportions and curve shape set per phase. During the top and bottom pause states, the output is silence.

---

## Parameters

### Timing

**Inhale Duration (sec)** `0.5-20.0 sec, default 4.0`
Length of the inhale phase. The breath cycle advances through inhale â†’ top pause â†’ exhale â†’ bottom pause in sequence, then loops. Changing this value mid-cycle takes effect at the next state transition; if the new duration is shorter than the current position, the position is immediately clamped to the end of the state.

**Top Pause (sec)** `0.0-5.0 sec, default 0.5`
Silence between the end of inhale and the start of exhale. Simulates the natural breath hold at the top of a breath. Set to 0 for an immediate inhale-to-exhale transition.

**Exhale Duration (sec)** `0.5-20.0 sec, default 4.0`
Length of the exhale phase.

**Bottom Pause (sec)** `0.0-5.0 sec, default 1.5`
Silence between the end of exhale and the start of the next inhale. Simulates the natural rest at the bottom of a breath. Set to 0 for an immediate exhale-to-inhale transition.

---

### Tone

**Inhale Frequency Hz** `50-2000 Hz, default 144`
Center frequency of the lowpass filter applied during the inhale phase. Controls the tonal brightness of the inhale â€” lower values produce a deep, body-heavy rush; higher values add more upper-frequency hiss. Note: due to sinusoidal frequency-to-coefficient mapping, the effective cutoff tracks lower than the displayed value at higher settings, increasingly so above ~500 Hz.

**Exhale Frequency Hz** `50-2000 Hz, default 96`
Center frequency of the lowpass filter applied during the exhale phase. Exhale is typically set lower than inhale, giving a slightly darker, softer outward breath. The same frequency mapping caveat applies.

---

### Envelope

All four fade parameters are expressed as a proportion of the phase duration â€” a value of 0.3 means 30% of that phase's total duration is spent in that fade region. The fade-in and fade-out proportions for a given phase are not independently clamped, but if their sum exceeds 1.0 the middle hold region disappears and the sound goes directly from fading in to fading out.

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

- **Linear** â€” straight ramp. Equal amplitude change per unit time.
- **Cosine** â€” S-curve. Gentle at the edges, faster through the middle. Generally sounds smooth and natural for breath.
- **Exponential** â€” squared curve. Slow start, fast finish on fade-in; fast start, slow finish on fade-out. More aggressive.
- **Natural** â€” sine-based curve. Similar in character to Cosine but with a slightly different arc. Often the most perceptually even-sounding option.

---

### Stereo

**Stereo Width** `0.0-1.0, default 0.5`
Spreads the filter frequencies between L and R channels. At 0.0, both channels use the same filter frequency (the noise is still decorrelated, but the tonal color is identical). At 1.0, the inhale filter is spread Â±15% between channels, and the exhale filter Â±12%. This creates a gentle, natural-sounding stereo image without hard panning.

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

### Speed Ramp (new)

In-plugin slowdown / speedup over time. Lets you wind breaths down toward sleep tempo (or up toward waking) without needing automation envelopes.

**Speed ramp target (multiplier)** `0.1–4.0, default 1.0`
The target multiplier. **0.5** = half speed, so a 4-second inhale becomes ~8 seconds; **2.0** = double speed (4s inhale → ~2s); **1.0** = no change. The multiplier applies to **all four phase durations and the rest period** so the cycle stretches/compresses as a whole — your Play/Rest ratio stays the same.

**Speed ramp duration (minutes)** `0–60, default 0`
How long the ramp takes from start to target. **0** disables the ramp.

**Speed ramp engage** `Off / On, default Off`
Off = ramp not advancing. On = ramp advances from its current position toward the target.

**How it behaves.** Off → On captures the current multiplier as the starting point and ramps toward the target over the duration. On → Off freezes the multiplier at its current position — it does NOT snap back to 1.0. Set target = 1.0 and re-engage to return to normal speed.

**Filter timbre is unchanged.** The speed ramp scales the state machine's *time*, not the filter coefficients — so a slow breath sounds exactly like a fast breath, just stretched. No re-tuning artifacts.

**Transport behavior**: resets to 1.0 on every play press.

---

## Usage Notes

- **The breath cycle is not tempo-synced.** Duration values are in absolute seconds. The cycle length is the sum of all four phase durations.
- **Pause phases are true silence.** No signal is passed, processed, or leaked during top and bottom pauses.
- **Filter state persists through pauses.** The filter is only active during inhale and exhale phases, so state doesn't accumulate during silence â€” but it also isn't reset between cycles, which allows for a smooth continuation rather than a click at the start of each new phase.
- **L and R are independently filtered with independent noise.** This means the stereo image is genuinely decorrelated at the source, not a mono signal that has been panned or delayed. Summing to mono will produce a slightly different sound than either channel alone.

---

*Breath Generator is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya â€” Developed with Claude (Anthropic)*


---

# Womb Sound Generator

**Designed by Rozaya â€” Developed with Claude (Anthropic)**

---

## Overview

Womb Sound Generator is a multi-layered intrauterine soundscape synthesizer. It combines three independently controllable sound sources â€” Heartbeat, Breath, and Bloodflow â€” into a single unified output. Each source can be soloed for monitoring and balanced independently. Heart rate variability is modeled across two dimensions â€” breath-coupled and random â€” and the bloodflow layer is phase-locked to the heartbeat cycle, producing a coherent physiological simulation rather than independent noise sources running in parallel.

The plugin generates no audio from an input signal. It is a pure synthesizer and should be placed on an empty FX chain or a track with no audio source.

---

## Signal Architecture

### Heartbeat
The heartbeat engine produces two events per cycle â€” S1 ("lub") and S2 ("dub") â€” separated by the systole interval. Each event is synthesized through two parallel resonant filter voices: a "near" voice (prominent, direct) and a "far" voice (slightly detuned, softer). Both voices blend a sine oscillator with white noise as their exciter, pass through a double-cascaded lowpass, and are routed to opposite output channels via an inter-aural delay. The master volume and individual S1/S2 volumes are applied before the three sources are summed.

### Breath
The breath engine runs a four-state cycle: inhale â†’ top pause â†’ exhale â†’ bottom pause. During inhale and exhale, white noise passes through a highpass filter followed by a state-variable lowpass per channel (with slight frequency offsets between L and R for width), then shaped by a fade-in/fade-out envelope. A secondary lowpass post-filter is applied to the full breath signal after mixing.

### Bloodflow
The bloodflow engine produces a continuously sweeping filtered noise texture. The filter cutoff is phase-locked to the heartbeat cycle â€” at each cycle start it sweeps from a low resting frequency up to a high peak frequency (simulating the pressure wave of a heartbeat moving through vessels), holds briefly, then returns to the resting frequency. The sweep tracks heart rate automatically.

### HRV
Heart rate variability modulates the heartbeat cycle length in real time using two additive layers. The breath-coupled layer derives its timing from the actual breath engine state â€” heart rate rises during inhale and falls during exhale. The random layer adds a slow, independently wandering offset. Both affect the heartbeat timing and the bloodflow sweep simultaneously, since the bloodflow LFO is tied to the heartbeat phase.

---

## Parameters

### Global

**BPM** `20-200, default 70`
Base heart rate in beats per minute. Affects both heartbeat timing and the bloodflow sweep, which is locked to it. Actual BPM fluctuates around this value when HRV is active.

**Master Stereo Flip** `Normal / Flipped`
Swaps the left and right output channels. Useful for adjusting anatomical orientation when using headphones â€” the prominent (near) heartbeat voice is on the left by default. Flipping reverses this for the full mix without changing internal routing.

---

### Heartbeat

**HB Master Volume** `0.0-1.0, default 1.0`
Overall output level for the entire heartbeat signal. Applied after all heartbeat synthesis and before the three-source mix.

**Heartbeat Solo** `Off / Solo`
Mutes Breath and Bloodflow. Solo is exclusive â€” enabling a second solo mutes the others.

**Systole ms (S1â†’S2 gap)** `50-400 ms, default 120`
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
Base resonant frequency for S1. The near voice center is derived at Ã—1.1 and the far at Ã—1.28.

**S2 Frequency Hz** `60-300 Hz, default 80`
Base resonant frequency for S2. The near voice center is derived at Ã—1.15 and the far at Ã—1.25.

**HB Stereo Width ms (neg = heart right)** `-15.0â€“+15.0 ms, default 3.0`
Inter-aural delay between the near and far heartbeat voices. Positive values place the near (prominent) voice on the left â€” anatomically correct for a heart on the left side. Negative values flip this. Crossing zero resets filter states to prevent artifacts.

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

**Inhale Frequency Hz** `50-2000 Hz, default 144`
Center frequency of the lowpass filter applied during the inhale phase. Lower values produce a deeper, body-heavy rush; higher values a brighter, airier sound. Due to sinusoidal frequency-to-coefficient mapping, effective cutoff tracks lower than the displayed value above ~500 Hz.

**Exhale Frequency Hz** `50-2000 Hz, default 96`
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
- **Linear** â€” straight ramp.
- **Cosine** â€” S-curve, gentle at both ends.
- **Exponential** â€” squared curve, aggressive.
- **Natural** â€” sine-based curve, typically the most perceptually smooth.

**Breath Stereo Width** `0.0-1.0, default 0.5`
Spreads the inhale and exhale filter frequencies between L and R. At 0.0 both channels use identical frequencies. At 1.0 the spread is Â±15% for inhale and Â±12% for exhale.

---

### Bloodflow

**Bloodflow Volume** `0.0-1.0, default 0.5`
Overall output level for the bloodflow signal.

**Bloodflow Solo** `Off / Solo`
Mutes Heartbeat and Breath.

**Bloodflow Low Frequency Hz** `20-2000 Hz, default 20`
Filter cutoff at the resting state between heartbeats â€” the floor of the sweep.

**Bloodflow High Frequency Hz** `20-4000 Hz, default 80`
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

Both HRV parameters operate additively. They affect the heartbeat timing and, because the bloodflow LFO is phase-locked to the heartbeat, the bloodflow sweep rate as well.

**Breath HRV Depth** `0.0-0.25, default 0.08`
Depth of breath-coupled heart rate modulation. The HRV modulation in this plugin is derived from the actual breath engine state â€” not a separate oscillator â€” so the timing is governed by the Inhale/Exhale/Pause duration settings. Heart rate increases during inhale and decreases during exhale. A value of 0.08 produces approximately Â±8% variation around the base BPM.

**Random HRV Depth** `0.0-0.08, default 0.02`
Adds a slowly wandering random offset to heart rate. The random target updates approximately every 5 seconds and slews toward it over ~3 seconds. At 0.0 random HRV is disabled.

---

### Breath Post-Filter

A lowpass filter applied to the full breath signal after the inhale/exhale synthesis, operating on the mixed breath output.

**Breath Post-filter Hz** `50-4000 Hz, default 600`
Cutoff frequency of the post-filter. Lowering this darkens the entire breath layer. Acts as a global brightness control independent of the per-phase frequency settings.

**Breath Post-filter Q** `0.5-8.0, default 1.5`
Resonance of the post-filter. Higher slider values produce lower resonance â€” this parameter is implemented internally as `1/Q`. Lower slider values produce a more resonant peak at the cutoff frequency.

### Start Delay

**Start Delay (beats)** `0–1000, default 0`

Silent for N heartbeats after playback starts, then the full womb soundscape (heartbeat, breath, bloodflow) begins normally. Beats are counted at the Heartbeat BPM — at 60 BPM, "4 beats" is 4 seconds; at 120 BPM it's 2 seconds. All internal state (heartbeat cycle phase, breath state machine, bloodflow LFO, post-filter buffers) stays frozen during the delay so everything begins cleanly at delay-end. Re-arms on every transport stop/start. 0 disables the delay.

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

---

## Usage Notes

- **Bloodflow is phase-locked to the heartbeat.** Changing BPM immediately changes the bloodflow sweep rate. The two cannot be decoupled within this plugin.
- **Breath HRV is coupled to the breath engine state.** The HRV timing is determined by the Inhale/Exhale/Pause duration settings, not by a separate rate control. Breath and HRV are genuinely synchronized.
- **The Breath Post-filter Q slider is inverted** relative to conventional filter labeling â€” higher slider values produce lower resonance.
- **Solo is exclusive.** Any active solo mutes the other two sources. Solo sliders are independent booleans and do not stack.
- **Frequency display for breath parameters reflects nominal Hz.** Sinusoidal coefficient mapping means effective cutoff tracks lower than the displayed value above ~500 Hz, consistently across all filters in the breath section.

---

*Womb Sound Generator is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya â€” Developed with Claude (Anthropic)*


---

# Polyrhythm Phase

**Designed by Rozaya â€” Developed with Claude (Anthropic)**

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

- **Drift** â€” all voices share a single global rate (set by Rate Value and Rate Mode), with each voice adding its own Drift / Rate value as an offset. A voice with a drift of +5 runs slightly faster than the global rate; one with -5 runs slightly slower. This creates organic polyrhythmic drift from a common tempo anchor.
- **Independent** â€” the global Rate Value is hidden. Each voice's Drift / Rate slider sets that voice's tremolo rate directly in the units selected by Rate Mode. Voices can run at entirely different rates with no shared reference.

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
Proportion of the on-time spent in the release ramp, fading from full amplitude back to silence. The default of 100% with 0% attack produces a ramp-down envelope â€” each voice fades out across its full on-time with no hold. Adjusting both attack and release creates a shaped pulse.

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

**Pan Increment per Voice** `-1000â€“+1000, default 0`
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
*Designed by Rozaya â€” Developed with Claude (Anthropic)*


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

### Speed Ramp (new)

In-plugin melody-tempo morph over time, without automation envelopes.

**Speed ramp target (multiplier)** `0.1–4.0, default 1.0` · **Speed ramp duration (minutes)** `0–60, default 0` · **Speed ramp engage** `Off / On, default Off`

Scales the effective dt (time-per-sample) the sequencer + voice envelopes see. **0.5** = the whole melody plays at half tempo (notes twice as long, glide stretches with them); **2.0** = double tempo. The Rate Value slider and per-voice cycle counts stay where they are; the ramp morphs effective tempo on top.

Voice envelope proportions (Attack %, Release %, Note duration) stay intact because they're percentages of the stretched step. Pan modulation also scales, so the whole melody timeline including pan motion morphs as one piece. Resets on every play press.

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

# Full Feature Sweeping Filter

**Designed by Rozaya â€” Developed with Claude (Anthropic)**

---

## Overview

Full Feature Sweeping Filter is a resonant lowpass filter with a shaped LFO sweep, stereo phase control, wet/dry mixing, and an optional pan modulation system. The filter cutoff is driven by a gated LFO envelope with independently shaped attack and release curves â€” the same envelope architecture used in the Full Feature Tremolo â€” giving precise control over how the cutoff moves through the frequency range on each cycle. A wet/dry mix allows the effect to be blended with the dry signal.

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
The cutoff frequency at the bottom of the sweep â€” where the filter sits when the LFO is at its minimum. If set higher than Frequency High, the two values are automatically swapped.

**Frequency High Hz** `20-20000 Hz, default 5000`
The cutoff frequency at the top of the sweep â€” where the filter sits when the LFO is at its peak.

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
- **Hz** â€” cycles per second.
- **Seconds** â€” period of one full cycle.
- **BPM** â€” cycles per minute.

**LFO Start Phase (degrees)** `-180 to +180, default 0`
Sets the initial phase position of the LFO when the plugin is first loaded or when this slider is moved. At 0, the LFO starts at the beginning of the cycle. This is a set-once control â€” adjusting it repositions both channel phases immediately, after which they run freely from that point. Useful for aligning the filter sweep to a specific position relative to other material or other instances of this plugin.

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
- **Linear** â€” straight ramp.
- **Cosine** â€” S-curve, gentle at both ends.
- **Logarithmic** â€” fast initial rise, slow finish.
- **Exponential** â€” slow initial rise, fast finish.

**Release Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve applied to the release ramp. Same options as Attack Shape.

---

### Stereo

**R Channel Phase Offset degrees** `-180â€“+180Â°, default 0`
When Phase Mode is set to Offset from L, this controls the phase difference between the left and right channel LFOs. At 180Â°, the channels are in opposition â€” when the left filter is fully open the right is fully closed. At 0Â° both channels move in unison.

**Phase Mode** `Independent L+R / Offset from L`
- **Independent L+R** â€” both LFO phases advance freely and in sync.
- **Offset from L** â€” the right channel phase is continuously derived as the left phase plus the R Channel Phase Offset. Use this mode when a stable stereo phase relationship is needed.

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
Pan sweeps in sync with the filter LFO at a speed multiplied by the Filter Speed Multiplier. At 1Ã—, one full pan sweep per filter cycle. At 2Ã—, two sweeps per cycle.

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

**Filter Speed Multiplier (Linked Sweep)** `0.125-8Ã—, default 1Ã—`
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

### Speed Ramp (new)

In-plugin sweep-rate morph over time. Set a target multiplier, set a duration in minutes, flip engage on — the filter sweep eases toward target without needing automation envelopes.

**Speed ramp target (multiplier)** `0.1–4.0, default 1.0` · **Speed ramp duration (minutes)** `0–60, default 0` · **Speed ramp engage** `Off / On, default Off`

The multiplier scales the effective sweep frequency on top of the Rate slider. **0.5** = half sweep rate (slower cutoff movement); **2.0** = double. Off → On captures the current multiplier and ramps fresh; On → Off freezes at the in-flight value. Set target = 1.0 and re-engage to return.

A ~100 ms smoother sits between the Rate slider and the audio so manual Rate tweaks no longer click.

The ramp also scales the Linked Sweep pan mode (12), since that mode derives its rate from the sweep frequency. The two Pan Sweep modes (10, 11) have their own independent rate slider and are NOT scaled. Resets on every play press.

---

## Usage Notes

- **Attack and Release are proportions of on-time, not cycle time.** A 50% Attack with 50% On Duration means the attack ramp takes 25% of the total cycle.
- **Depth % scales symmetrically around the center frequency.** At 50% depth with Low=200 Hz and High=2000 Hz, the sweep covers 700-1300 Hz â€” not 200-1100 Hz.
- **The filter coefficient uses linear frequency mapping** (`freq * 2 / srate`), unlike the sinusoidal mapping in the synthesizer plugins. Displayed Hz values correspond directly to standard filter behavior.
- **Phase Offset only takes effect in Offset from L mode.** In Independent L+R mode the offset slider has no effect on behavior.

---

*Full Feature Sweeping Filter is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya â€” Developed with Claude (Anthropic)*


---

# Sweep Dwell Filter

**Designed by Rozaya â€” Developed with Claude (Anthropic)**

---

## Overview

Sweep Dwell Filter is a resonant lowpass filter driven by an LFO with four time-based phases: hold at high frequency, sweep down to low, hold at low frequency, and sweep back up. Unlike a rate-based LFO, the cycle duration is determined entirely by the four phase times â€” each phase has its own duration in seconds, and the total cycle length is their sum. The fade transitions have independently selectable curve shapes. A wet/dry mix and an optional pan modulation system complete the feature set.

The plugin processes incoming stereo audio.

---

## Signal Architecture

The LFO phase advances continuously. At any point in the phase, the plugin calculates the current position within the hold-high, sweep-down, hold-low, and sweep-up sequence, and outputs a value between 0 (low cutoff) and 1 (high cutoff) accordingly. The fade transitions use configurable curve shapes. The LFO output is mapped linearly to the frequency range, smoothed with a 3 ms lag, and fed into a two-pole resonant lowpass filter per channel. The wet output is blended with the dry signal.

Left and right channels have independent LFO phases. In **Independent L+R** mode both advance at the same rate, staying in sync. In **Offset from L** mode the right channel phase is continuously derived from the left plus the stereo offset, keeping a stable phase relationship.

---

## Parameters

### Filter Range

**Frequency Low Hz** `20-20000 Hz, default 500`
The cutoff frequency during the low-dwell segment â€” the resting state of the filter. If set higher than Frequency High, the two values are automatically swapped.

**Frequency High Hz** `20-20000 Hz, default 5000`
The cutoff frequency during the high-dwell segment â€” the open state of the filter.

**Resonance** `0.0-1.0, default 0.7`
Resonance of the lowpass filter. Higher values add a pronounced peak at the cutoff frequency, accentuating the frequencies at each point in the sweep. Values approaching 1.0 can produce self-oscillation.

**Wet/Dry Mix** `0.0-1.0, default 1.0`
Blend between the filtered signal and the unprocessed input. At 1.0 the output is fully filtered; at 0.0 the filter has no effect.

---

### Dwell and Transition Times

The LFO cycle consists of four phases in sequence: hold high â†’ sweep down â†’ hold low â†’ sweep up â†’ repeat. The total cycle length is the sum of all four phase durations.

**High Dwell sec** `0.001-60 sec, default 4`
Duration of the segment where the filter holds at the high cutoff frequency.

**Low Dwell sec** `0.001-60 sec, default 6`
Duration of the segment where the filter holds at the low cutoff frequency.

**Fade Down sec** `0.001-30 sec, default 1`
Duration of the transition from the high cutoff frequency to the low cutoff frequency.

**Fade Down Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve shape applied to the fade-down transition.
- **Linear** â€” constant rate of frequency change.
- **Cosine** â€” S-curve, slow at both ends, faster in the middle.
- **Logarithmic** â€” fast initial drop, slow finish. The filter closes quickly then lingers near the low frequency.
- **Exponential** â€” slow initial drop, fast finish. The filter holds near the high frequency before closing sharply.

**Fade Up sec** `0.001-30 sec, default 1`
Duration of the transition from the low cutoff frequency back to the high cutoff frequency.

**Fade Up Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve shape applied to the fade-up transition. Same options as Fade Down Shape. Asymmetric shapes between fade down and fade up create distinct opening and closing characters.

---

### Stereo

**Stereo Phase Offset degrees** `-180â€“+180Â°, default 0`
When Phase Mode is Offset from L, this controls the phase difference between the left and right LFOs. At 180Â° the channels are in opposition â€” when the left filter is at its high cutoff the right is at its low cutoff. At 0Â° both channels move identically.

**Phase Mode** `Independent L+R / Offset from L`
- **Independent L+R** â€” both LFO phases advance freely at the same rate, staying in sync.
- **Offset from L** â€” the right channel phase is derived continuously as the left phase plus the Stereo Phase Offset. Use this mode to maintain a stable stereo phase relationship.

---

### Pan Block

**Pan Enabled** `Off / On`
Enables pan modulation. When on, the post-filter signal is summed to mono and repositioned in the stereo field. When off, all pan sliders are hidden.

> **Note:** Enabling pan sums the output to mono before panning. Stereo content of the filtered signal is collapsed.

---

#### Per-Cycle Pan Modes

Pan position updates once per LFO cycle. **Cycle Steps** controls the sequence length.

**Mono** â€” signal stays centered.

**Alternating** â€” alternates hard left and hard right each cycle.

**Alternating (Flipped)** â€” same as Alternating, starting from the right.

**Distributed** â€” steps evenly from left to right across the cycle count, then wraps.

**Distributed (Flipped)** â€” steps evenly from right to left, then wraps.

**Distributed (Ping-pong)** â€” steps left to right then reverses, bouncing between extremes.

**Converging** â€” starts hard left, alternates left/right positions stepping progressively toward center.

**Converging (Ping-pong)** â€” converges to center then reverses back outward, bouncing.

**Diverging** â€” starts center, alternates left/right positions stepping progressively outward.

**Diverging (Ping-pong)** â€” diverges to extremes then reverses back inward, bouncing.

---

#### Continuous Pan Modes

**Pan Sweep** â€” continuous left-to-right sweep at the rate set by Pan Sweep Rate.

**Pan Sweep (Flipped)** â€” continuous right-to-left sweep.

**Linked Sweep** â€” pan sweeps in proportion to the filter cycle rate, scaled by Filter Speed Multiplier. At 1Ã—, one full pan sweep per filter cycle.

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

**Filter Speed Multiplier (Linked Sweep)** `0.125-8Ã—, default 1Ã—`
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

### Speed Ramp (new)

In-plugin sweep-pattern slowdown/speedup over time, without automation envelopes.

**Speed ramp target (multiplier)** `0.1–4.0, default 1.0` · **Speed ramp duration (minutes)** `0–60, default 0` · **Speed ramp engage** `Off / On, default Off`

The multiplier scales the whole dwell pattern's frequency. **0.5** = the entire pattern (high dwell + fade down + low dwell + fade up) takes twice as long; **2.0** = half the time. All four timing sliders stay where they are; the ramp is layered on top. Off → On captures the in-flight multiplier; On → Off freezes at the current position.

The existing ~3 ms cutoff smoother handles any per-sample step change cleanly, so manual dwell-slider tweaks are already click-free. Resets on every play press.

---

## Usage Notes

- **Cycle length is the sum of all four phase durations.** Unlike rate-based LFOs there is no single BPM or Hz value â€” the tempo of the sweep is a consequence of the four phase times combined.
- **Adjusting any phase duration takes effect immediately.** The LFO phase is a running 0-1 counter; changing phase durations changes how that counter maps to filter positions without resetting it. This means a duration change mid-cycle may cause a jump to a different point in the sweep.
- **The frequency mapping is linear.** Displayed Hz values correspond directly to filter behavior â€” the same linear mapping used in the other filter plugins in this suite.
- **Phase Offset only takes effect in Offset from L mode.** In Independent L+R mode the offset slider has no audible effect.

---

*Sweep Dwell Filter is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya â€” Developed with Claude (Anthropic)*


---

# Full Feature Tremolo

**Designed by Rozaya â€” Developed with Claude (Anthropic)**

---

## Overview

Full Feature Tremolo is an amplitude modulation effect with a fully configurable LFO envelope and an optional pan modulation system. The tremolo LFO is not a simple sine wave â€” it is a gated envelope with independently shaped attack and release curves, a configurable on-time within each cycle, and a hold-high region between them. This allows the plugin to produce anything from a smooth, sine-like tremolo to a hard gate with slow attack, fast release, or any combination in between.

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
- **Hz** â€” cycles per second.
- **Seconds** â€” period of one full cycle.
- **BPM** â€” cycles per minute.

**On Duration % of Cycle** `0-100%, default 50`
The proportion of each cycle during which the tremolo is in its active (non-silent) state â€” including attack and release time. At 50%, the signal is present for half the cycle and absent for the other half. At 100%, the tremolo never fully closes. At 0%, the output is silence.

**Depth dB** `-60-0 dB, default -6`
How far the signal drops at the bottom of the tremolo cycle. At 0 dB there is no depth and the output is unaffected. At -60 dB the signal is effectively silenced at the trough. The depth is converted internally to a linear gain multiplier.

**Attack %** `0-100%, default 0`
Proportion of the on-time spent fading in from silence to full level. At 0%, the tremolo opens instantly at the start of each on-period. Attack and Release proportions are expressed relative to the on-time, not the full cycle â€” so an Attack of 50% means the first half of the on-duration is the attack ramp. If Attack % + Release % exceeds 100% of the on-time, both are scaled down proportionally.

**Release %** `0-100%, default 0`
Proportion of the on-time spent fading from full level back to silence. At 0%, the tremolo closes instantly at the end of each on-period.

**Attack Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve applied to the attack ramp.
- **Linear** â€” straight ramp.
- **Cosine** â€” S-curve, gentle at both ends.
- **Logarithmic** â€” fast initial rise, slow finish. Perceived loudness increases quickly.
- **Exponential** â€” slow initial rise, fast finish. Builds tension before arrival.

**Release Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve applied to the release ramp. Same options as Attack Shape. Mixing attack and release shapes â€” e.g., Logarithmic attack with Exponential release â€” can produce organic, asymmetric tremolo characters.

**Stereo Phase Offset (degrees)** `-180â€“+180Â°, default 0`
When Phase Mode is set to Offset from L, this controls how far ahead or behind the right channel's LFO is relative to the left. At 180Â° or -180Â°, the channels are in perfect opposition â€” when left is at its peak, right is at its trough. At 0Â°, the offset is zero and both channels move in unison regardless of mode (equivalent to Independent L+R for most purposes).

**Phase Mode** `Independent L+R / Offset from L`
- **Independent L+R** â€” left and right LFO phases advance independently. Both start at zero and run freely. In practice they stay in sync unless rates diverge, which they don't in this plugin â€” so this mode produces synchronized stereo tremolo.
- **Offset from L** â€” the right channel phase is continuously derived as the left phase plus the Stereo Phase Offset. This keeps the offset locked regardless of where in the cycle each channel is, and is the correct mode to use when you want a stable stereo phase relationship.

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
Pan position sweeps in sync with the tremolo LFO, but at a speed multiplied by the Filter Speed Multiplier. At 1Ã—, the pan completes one full sweep per tremolo cycle. At 2Ã—, it sweeps twice per cycle. At 0.5Ã—, it sweeps once every two cycles.

---

#### Pan Parameters

**Pan Spread** `0.0-1.0, default 1.0`
Scales the pan range. At 1.0, pan positions reach hard left and hard right. At 0.5, the maximum excursion is halfway to each side. At 0.0, all pan modes produce center regardless of their position calculations.

**Pan Glide ms** `0-100 ms, default 5`
Smoothing time applied to pan position changes. At 0 ms, pan position jumps immediately to each new value â€” appropriate for hard-cut effects but can produce clicks on per-cycle modes at slow tempos. Higher values smooth the transition, trading sharpness for click-free movement.

**Cycle Steps (per-cycle modes)** `2-32 steps, default 8`
Number of steps in the pan sequence for per-cycle modes (Alternating through Diverging Ping-pong). Hidden when a continuous pan mode is active.

**Pan Sweep Rate** `0.001-1000, default 2`
Rate of the continuous pan sweep for Pan Sweep and Pan Sweep (Flipped) modes. Hidden for other modes.

**Pan Sweep Rate Unit** `Hz / Seconds / BPM`
Unit for Pan Sweep Rate. Hidden for modes that don't use it.

**Filter Speed Multiplier (Linked Sweep)** `0.125-8Ã—, default 2Ã—`
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

### Speed Ramp (new)

In-plugin tremolo-rate morph over time. Set a target multiplier, set a duration in minutes, flip engage on — the tremolo rate eases toward target without needing automation envelopes.

**Speed ramp target (multiplier)** `0.1–4.0, default 1.0` · **Speed ramp duration (minutes)** `0–60, default 0` · **Speed ramp engage** `Off / On, default Off`

The multiplier scales the effective tremolo frequency on top of the Rate slider. **0.5** = half tremolo rate (slower modulation cycle); **2.0** = double. Off → On captures the current multiplier and ramps fresh toward the target; On → Off freezes at the in-flight value. Set target = 1.0 and re-engage to return.

A ~100 ms smoother also sits between the Rate slider and the effective frequency, so manual Rate tweaks no longer click. Always on.

The ramp also scales the linked-sweep pan rate (Pan Mode 11), since that mode derives its rate from the tremolo frequency. Pan Sweep modes 9 and 10 have their own independent rate slider and are NOT scaled by the speed ramp — they stay at whatever Pan Sweep Rate is set to. (Same with Cycle Steps / Pan Glide; those are positional / smoothing controls, not rate.)

Resets on every play press.

---

## Usage Notes

- **Pan block sums to mono before panning.** This is intentional â€” pan modulation is applied to a unified signal. If the source is stereo, the two channels are averaged before any pan position is applied.
- **Attack and Release are proportions of on-time, not cycle time.** A 50% Attack with a 50% On Duration means the attack ramp takes 25% of the total cycle.
- **Phase Offset only takes effect in Offset from L mode.** In Independent L+R mode the offset slider has no effect.
- **Per-cycle pan modes update at LFO phase reset.** The pan position does not glide to a new value mid-cycle â€” it jumps (subject to Pan Glide smoothing) at the moment the tremolo cycle wraps.

---

*Full Feature Tremolo is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya â€” Developed with Claude (Anthropic)*


---

# Rhythm Track

**Designed by Rozaya â€” Developed with Claude (Anthropic)**

---

## Overview

Rhythm Track is a synthesized metronome with configurable tone, swing, and stereo pan distribution. It produces a continuous click track with a distinct strong beat on the downbeat and weak beats on all remaining beats in the bar. Both the strong and weak ticks are synthesized using filtered noise with exponential decay, giving them a pitched percussive quality rather than a raw click. Pan mode options distribute the beats across the stereo field in various patterns, from simple alternation to converging and diverging sequences.

The plugin generates no audio from an input signal. It is a pure synthesizer and should be placed on an empty FX chain or a track with no audio source.

---

## Signal Architecture

Each tick is pre-rendered into a buffer whenever a relevant parameter changes. The rendering process passes a short burst of noise through a resonant bandpass filter (a lowpass followed by a four-stage cascaded highpass) tuned to the tick's frequency, with a short linear attack and an exponential decay. The rendered buffer is then peak-normalized to the configured gain level.

At playback time the plugin advances a beat phase counter. When the phase crosses a cycle boundary, the appropriate tick buffer is triggered and plays back sample-by-sample, panned to the position calculated for that beat index. Only one tick plays at a time â€” if a new beat fires before the previous tick has finished, the previous tick is cut off.

Swing is applied by offsetting the beat phase at each cycle boundary, advancing or retarding even-numbered beats relative to odd-numbered ones.

---

## Parameters

### Timing

**Tempo (BPM)** `30-300 BPM, default 120`
The tempo of the beat track in beats per minute.

**Beats per bar** `1-20, default 4`
The number of beats in each bar. Beat index 0 is the strong (accented) beat; all others are weak beats. With a value of 1, every beat is a strong beat.

**Swing amount** `-1.0â€“+1.0, default 0`
Applies a swing feel to the beat by offsetting the timing of alternating beats. Positive values push even-numbered beats later (forward swing â€” the common jazz feel). Negative values push them earlier (reverse swing). The offset is applied as a fraction of one third of the beat duration, consistent with triplet-based swing. At 0 the rhythm is straight.

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

- **Mono** â€” all beats play centered.
- **Accent L / Weak R** â€” the strong beat (index 0) plays hard left; all weak beats play hard right.
- **Alternating** â€” beats alternate hard left / hard right on each successive beat, starting with left on the strong beat.
- **Distributed** â€” beats are evenly spaced from hard left to hard right across the full bar. With 4 beats per bar: beat 0 hard left, beat 1 slightly left of center, beat 2 slightly right of center, beat 3 hard right.
- **Converging** â€” beat 0 starts hard left, then each successive pair of beats approaches center from opposite sides, converging inward across the bar.
- **Diverging** â€” beat 0 starts center, then each successive pair of beats moves outward symmetrically toward the extremes.

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

### Speed Ramp (new)

In-plugin tempo morph over time, without automation envelopes.

**Speed ramp target (multiplier)** `0.1–4.0, default 1.0` · **Speed ramp duration (minutes)** `0–60, default 0` · **Speed ramp engage** `Off / On, default Off`

Engage = ramp advances from the current multiplier toward target over the duration. **0.5** halves effective tempo (120 BPM → 60), **2.0** doubles it. The Tempo slider stays where it is; the ramp is layered on top. Off → On captures the in-flight multiplier and starts a fresh ramp; On → Off freezes at the current position. Set target = 1.0 and re-engage to return to slider tempo.

The accent grid and swing follow effective tempo automatically — the bar still feels right at any speed. Resets to 1.0 on every play press.

---

## Usage Notes

- **Only one tick plays at a time.** If a beat fires before the previous tick finishes decaying, the previous tick is cut off immediately. At fast tempos with long decay settings, ticks will be truncated â€” reduce decay times accordingly.
- **All tick parameters trigger a re-render.** Moving any slider recalculates the full tick buffer for both strong and weak beats. This is instantaneous but means the sound updates on the next beat rather than mid-tick.
- **Swing is triplet-based.** The maximum swing offset is one third of a beat duration. At Â±1.0 the affected beats are shifted by a full triplet subdivision.
- **Pan positions are fixed per beat index within the bar.** Changing Beats per bar will recalculate all pan positions. Pan spread scales all positions uniformly.

---

*Rhythm Track is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya â€” Developed with Claude (Anthropic)*






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

### Speed Ramp (new)

In-plugin tempo morph over time, without automation envelopes.

**Speed ramp target (multiplier)** `0.1–4.0, default 1.0` · **Speed ramp duration (minutes)** `0–60, default 0` · **Speed ramp engage** `Off / On, default Off`

Scales the scale's tempo on top of the BPM slider. **0.5** = notes take twice as long each (half tempo); **2.0** = notes fire twice as fast. Both halves of the Play/Rest gate scale together so the gate stays internally consistent at any speed. Off → On captures the in-flight multiplier; On → Off freezes at the current position. Resets on every play press.

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

### Speed Ramp (new)

In-plugin sweep-rate morph over time. Lets you slow the glissando illusion down (or speed it up) without touching automation.

**Speed ramp target (multiplier)** `0.1–4.0, default 1.0` · **Speed ramp duration (minutes)** `0–60, default 0` · **Speed ramp engage** `Off / On, default Off`

Scales the sweep rate on top of the Rate slider. **0.5** = sweep takes twice as long to complete; **2.0** = half the time. The audible pitch of any oscillator is NOT scaled — only the rate at which oscillators sweep through the pitch window. The Play/Rest cycle counter scales with the ramp too, so the cycle gate stays aligned with the actual sweep.

Off → On captures the in-flight multiplier; On → Off freezes at the current position. Set target = 1.0 and re-engage to return. Resets on every play press.

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
