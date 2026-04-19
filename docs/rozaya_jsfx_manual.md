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

**Effects**
- [Resonant Sweeping Filter](#full-feature-sweeping-filter)
- [Sweep Dwell Filter](#sweep-dwell-filter)
- [Full Feature Tremolo](#full-feature-tremolo)

**Utilities**
- [Rhythm Track](#rhythm-track)

---

# Acknowledgements

## Authorship

All plugins in this suite were designed by Rozaya. Code was written by Claude (Anthropic) under Rozaya's direction. Rozaya determined the concept, feature set, signal architecture, parameter design, and all creative and functional decisions for each plugin. Claude implemented those decisions in JSFX.

## Inspirations and Prior Art

Several plugins in this suite were developed with reference to existing implementations in common DAW tools. In all cases, the code was written independently â€” no source code was copied or derived from any external implementation. The conceptual influence is acknowledged here:

- **Rhythm Track** â€” rhythmic metronome generation concepts drawn from existing DAW metronome implementations.
- **Resonant Sweeping Filter** and **Sweep Dwell Filter** â€” filter sweep concepts informed by resonant lowpass filter implementations found in standard DAW effect libraries.
- **Full Feature Tremolo** â€” tremolo concepts informed by existing DAW tremolo implementations, substantially expanded with shaped envelopes, stereo phase control, and pan modulation.

The **Heartbeat Generator**, **Womb Sound Generator**, **Breath Generator**, and **Polyrhythm Phase** plugins are original concepts with no direct external inspiration for their architecture or feature sets.

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

Polyrhythm Phase is a binaural oscillator with up to eight simultaneous voices, each tuned to a specific musical pitch. Each voice generates a stereo pair of oscillators with a slight frequency offset between the left and right channels â€” the binaural beat â€” producing entrainment tones that shift in perceived frequency as the beat interacts with the listener's auditory system. A shared tremolo envelope modulates the amplitude of all voices, with per-voice drift or independent rate options creating polyrhythmic relationships between them. A pan modulation system adds optional spatial movement per voice.

The plugin generates no audio from an input signal. It is a pure synthesizer.

---

## Signal Architecture

Each active voice runs two oscillators â€” one for the left channel at the voice's base frequency, one for the right channel at the base frequency plus the binaural beat offset. Both oscillators use the same waveform. The tremolo LFO modulates their shared amplitude using a gated envelope with configurable attack and release shapes. Per-voice gain is applied before the voice's contribution is summed into the output.

All active voices are summed and normalized by the active voice count, keeping the output level consistent regardless of how many voices are enabled.

When pan is enabled, each voice's contribution is summed to mono and repositioned in the stereo field independently using a sine LFO, before being added to the output mix.

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

Each voice has five parameters. Voices 3-8 are inactive by default.

**Vn Note** `C / C# / D / D# / E / F / F# / G / G# / A / A# / B`
The pitch class of the voice within its octave.

**Vn Octave** `0-8, default varies`
The octave of the voice. Combined with the note, this determines the base frequency fed to the left oscillator. The right oscillator runs at this frequency plus the Binaural Beat Hz offset.

**Vn Drift / Rate** `-1000â€“+1000, default 0`
In Drift mode: an offset added to the global Rate Value to determine this voice's tremolo rate. Positive values make the voice run faster; negative values slower. A value of 0 means the voice runs at exactly the global rate.
In Independent mode: this voice's tremolo rate directly, in the units set by Rate Mode.

**Vn Active** `Off / On`
Enables or disables the voice. Inactive voices contribute nothing to the output and are excluded from the normalization count.

**Vn Gain dB** `-60â€“+6 dB, default 0`
Per-voice output level applied before the voice is summed into the mix. Allows individual voices to be balanced relative to one another.

---

### Waveform

**Waveform** `Sine / Triangle / Saw / Golden TS / Golden SG / Golden GS`
The oscillator waveform used by all voices simultaneously.

- **Sine** â€” pure sinusoidal tone. Cleanest binaural beat interaction, no harmonics.
- **Triangle** â€” bipolar triangle wave with odd harmonics, softer than saw.
- **Saw** â€” sawtooth wave with a full harmonic series. Rich and bright.
- **Golden TS** â€” a triangle wave whose phase is warped using the golden ratio (Ï† â‰ˆ 1.618), creating an asymmetric waveform with a distinctive harmonic character. The phase is split at the 1/Ï† point and each segment is remapped.
- **Golden SG** â€” a sine wave whose input phase is mapped through the same golden ratio warping as Golden TS before the sine function is applied. Produces a sine-like tone with subtle golden ratio phase distortion.
- **Golden GS** â€” the oscillator phase is self-modulated: the phase is offset by `(1/Ï†) * sin(phase) / 2Ï€` before the sine function is applied. This creates a continuously self-warping waveform whose harmonic content shifts with frequency.

---

### Pan

**Pan Enabled** `Off / On`
Enables per-voice pan modulation. When on, each voice is panned independently using a sine LFO before being summed into the output. When off, all pan controls are hidden and voices sum directly to their L/R oscillator channels.

> **Note:** When pan is enabled, each voice's L and R oscillator outputs are summed to mono before panning. The binaural beat relationship between the voice's oscillators is collapsed â€” pan mode and binaural beats are mutually exclusive in terms of stereo function.

**Pan Mode** `Tremolo / Increment`
- **Tremolo** â€” each voice's pan LFO runs at the same rate as that voice's tremolo LFO. The pan and amplitude modulation are locked in phase.
- **Increment** â€” all voices use a shared Pan Base Rate as their pan foundation, with each voice's rate offset by Pan Increment Ã— voice index. Voice 1 pans at the base rate, voice 2 at base + 1Ã—increment, voice 3 at base + 2Ã—increment, and so on.

**Pan Spread %** `0-100%, default 100`
Scales the width of pan movement. At 100% panning reaches hard left and hard right. At 0% all voices remain centered regardless of mode.

**Pan Base Rate** `0.001-1000, default 60`
Base rate for pan movement in Increment mode, in the units set by Rate Mode.

**Pan Increment per Voice** `-1000â€“+1000, default 0`
The per-voice rate offset in Increment mode. Each successive voice's pan rate is offset by this amount from the previous. Setting a positive value spreads voices across different pan speeds; a negative value reverses the direction of the spread.

---

## Usage Notes

- **Active voice count determines normalization.** The output is divided by the number of active voices each sample, keeping overall level consistent. Enabling or disabling voices mid-playback will change the level slightly as the normalization adjusts.
- **Binaural Beat Hz applies to all voices uniformly.** All voices have the same L/R frequency offset. There is no per-voice binaural beat amount.
- **Pan mode collapses the binaural beat.** When pan is enabled, each voice's L and R signals are summed to mono before panning. For binaural entrainment use, leave pan disabled.
- **Playback start resets all phases.** Oscillator phases, tremolo phases, and pan phases all reset to zero when playback begins from a stopped state. This ensures consistent behavior from the same starting point.
- **Rate Mode applies to both tremolo and pan rates.** Both the voice tremolo rates and the Increment mode pan rates are interpreted in whatever unit Rate Mode specifies.
- **Phase Offset means "when does this voice become audible," not a raw phase shift.** An offset of 8 on a 16-second cycle means the voice fires at second 8. An offset of 0 fires immediately. Offsets wrap freely — an offset of 16 on a 16-second cycle is the same as 0.
- **On Duration % and voice count must be coordinated to avoid overlap.** On Duration sets how much of each cycle a voice is present. With multiple voices spaced across a shared cycle, each voice needs enough room to fit without overlapping its neighbors. The safe maximum On Duration for evenly-spaced voices is `100 ÷ number of active voices` percent. For example: 2 voices = 50% max, 3 voices = 33% max, 4 voices = 25% max. Exceeding this will cause voices to overlap at the boundaries regardless of how offsets are set. To space voices evenly, divide the cycle length by the number of voices and use that as the offset step — e.g. 3 voices on a 12-second cycle: offsets of 0, 4, and 8.
- **Offsets don't have to be perfectly even — spacing voices closer together creates overlap, spacing them further apart creates silence between them. Both are valid creative choices.** In Seconds mode this is especially concrete: with a 16-second cycle, On Duration 50%, and two voices, an offset of 8 produces a clean handoff — V1 plays seconds 0–8, V2 plays seconds 8–16. An offset of 7 causes one second of overlap at the boundary. An offset of 9 leaves a one-second gap of silence between them. The relationship is direct: offset in seconds is exactly when V2 becomes audible.
- **When building sequential voice patterns, set Rate Value to `voice duration × number of voices`.** This ensures the cycle fills exactly with no gaps or overlap. For example: 4 voices each lasting 4 seconds requires a rate of 16 seconds, with offsets at 0, 4, 8, and 12. 4 voices each lasting 6 seconds requires a rate of 24 seconds, with offsets at 0, 6, 12, and 18. On Duration % should be set to `100 ÷ number of voices` to match.

---

*Polyrhythm Phase is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya â€” Developed with Claude (Anthropic)*


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

---

## Usage Notes

- **Only one tick plays at a time.** If a beat fires before the previous tick finishes decaying, the previous tick is cut off immediately. At fast tempos with long decay settings, ticks will be truncated â€” reduce decay times accordingly.
- **All tick parameters trigger a re-render.** Moving any slider recalculates the full tick buffer for both strong and weak beats. This is instantaneous but means the sound updates on the next beat rather than mid-tick.
- **Swing is triplet-based.** The maximum swing offset is one third of a beat duration. At Â±1.0 the affected beats are shifted by a full triplet subdivision.
- **Pan positions are fixed per beat index within the bar.** Changing Beats per bar will recalculate all pan positions. Pan spread scales all positions uniformly.

---

*Rhythm Track is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya â€” Developed with Claude (Anthropic)*




