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

**Drift period mode** `BPM / Hz / Seconds / Host x, default Seconds`

**Host x** follows the project tempo: Drift period becomes a multiplier of it, so 1 is one drift cycle per beat and 2 is two per beat. *(This is the last plugin still using the multiplier form — the rest of the suite is moving to a plain beat count, where you type the number of beats instead. See R13 in the consistency plan.)*
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

