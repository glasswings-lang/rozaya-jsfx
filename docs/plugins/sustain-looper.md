# Sustain Looper

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Sustain Looper turns a section of a loaded sound into an endless, seamless pad — the sampler "sustain loop" (choir pads, string pads, sustained breath) made accessible. It loads a WAV directly (no live recording, no transport timing), loops a chosen region with a crossfade that hides the seam, and can stack a detuned ensemble for lushness and width.

The crossfade is the accessibility win. A normal sampler loop needs its loop points matched precisely — by eye, on a waveform — or it clicks. The crossfade smears the seam so the loop points do NOT have to match: set the region roughly by ear, then raise the crossfade until the repeat is seamless. No waveform, no hunting.

It outputs the loop only (its audio input is ignored). Drop it on a track and run the transport (or arm the track and monitor) for it to sound.

---

## Loading samples

Put `.wav` files in REAPER's resource folder under `Data\glasswings_samples\`, then pick one from the Sample dropdown (it reads as a list in a screen reader, like any other option slider).

**Use WAV.** JSFX reliably reads WAV and OGG; FLAC and MP3 are not guaranteed. Keep loop-sources short — seconds, not minutes. A JSFX instance holds roughly 80 seconds of 48 kHz stereo audio by default, and a loop source only needs a few seconds of steady sustain anyway. (Keep your big finished renders as FLAC; just don't try to load them here.)

---

## Signal Architecture

### Crossfade loop

A read head plays the chosen region and wraps back to its start. Near the end of the region it crossfades into the material *just before* the start, so the wrap is continuous in the source — seamless regardless of where the loop points fall. A larger crossfade hides more.

### Detuned ensemble

With Voices above 0, additional copies of the loop play at once — each a different amount sharp and flat (fanned across the Spread range, slowly drifting on independent LFOs) and panned across the stereo field. They beat against the main voice the way a choir or string section does. It is true detune (no delay), so there is no comb-filter coloration, and it masks any residual loop repetition. Voices = 0 is a single clean loop.

---

## Parameters

**Sample** `dropdown of WAVs in Data\glasswings_samples\`
The loaded sound. See "Loading samples."

**Loop position (%)** `0 to 100, default 50`
Where in the file the loop sits — 0 = start, 100 = end. Scrub to the part you want to sustain (a steady held stretch, not a swell).

**Loop length (ms)** `5 to 4000, default 500`
Size of the looped chunk. Small lengths become a tone; longer lengths sustain a fuller slice as a pad.

**Crossfade (% of loop)** `0 to 100, default 40`
How much of the loop end crossfades into the start. Raise until the seam is inaudible. Broadband sources (breath) need very little; tonal sources need more.

**Pitch (semitones)** `-24 to +24, default 0`
Transposes playback, tape-style (pitch and formants move together). The file's own sample rate is auto-corrected so it plays at its true pitch at 0.

**Output (dB)** `-24 to +12, default 0`
Final output level.

**Voices (ensemble)** `0 to 12, default 6`
Number of detuned ensemble voices stacked on the loop. 0 = a single clean loop; higher = a thicker section.

**Spread (detune amount)** `0 to 100, default 50`
How far the ensemble voices detune apart and drift. Low = tight and subtle; high = wide and lush (very high goes warbly).

---

## Usage Notes

- **Loop steady material.** The loop is invisible when the region has nothing distinctive happening — a held, steady sustain. If the source has vibrato or a swell baked in, looping a chunk repeats that wiggle obviously. Loop the held middle and add movement at playback with the ensemble instead.
- **Crossfade is your loop-point substitute.** You never place exact loop points. Set position and length roughly by ear, then raise Crossfade until the seam disappears.
- **Broadband sources are easiest.** Breath and noise loop seamlessly with almost no crossfade, because noise has no repeating events. Pure tones are the hardest, and want the ensemble for life.
- **The render-and-loop pipeline.** Pair it with Harmonic Sculptor (or noise through Resonance Bank for breath): design a timbre → render to a WAV in the samples folder → load here → sustain. Pitch-shifting one vowel sample also slides it through neighbouring vowels (the formants move with the pitch), so a few base samples cover a continuum.
- **Transport must be moving** for it to sound — it is a generator, and REAPER only runs it while audio is flowing. Loop the transport, or arm the track and monitor.

---

*Sustain Looper is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

