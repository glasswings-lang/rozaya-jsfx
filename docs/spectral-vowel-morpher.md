# Spectral Vowel Morpher

Prototype: `src/spectral_vowel_probe.jsfx`. (Folds into `rozaya_jsfx_manual.md`
when it graduates / gets a final name.)

A **capture-based instrument**. You play audio into it, capture a few moments,
and it resynthesizes them — either as a recognizable voice, an evolving wash, or
any blend — and morphs between the captured moments. Captures persist across
project save/reopen.

## The two engines (the Texture knob)

Every capture is analyzed two ways at once. **Texture** crossfades between them:

- **Texture 0 — Voice (harmonic).** Detects the pitch (YIN) and rebuilds the
  sound from 64 harmonics. Keeps the vowel/pitch; phase-coherent, so it's clean
  and recognizable. Trade-off: it reproduces only the *harmonic* part — no breath
  or air (additive synthesis has none). Only meaningful on clearly **pitched**
  material; on unpitched sources it produces a tone.
- **Texture 100 — Wash (spectral).** PaulStretch-style phase randomization: keeps
  the magnitude spectrum, throws away phase, so every partial becomes a narrow
  noise band. Smooth, breathy, evolving — turns *anything* into texture. On a
  voice it deliberately sounds "de-voiced / like spectral denoising" (that's the
  operation, not a fault) — great for pads, ghostly beds.
- **In between** layers both: harmonic vowel + spectral air.

Equal-power crossfade, so the middle doesn't dip in level.

## Quick start

1. Put audio on the track (a media item, or send another track in). Or arm +
   monitor to capture a live mic/instrument.
2. **Input level** up, **Voice level** down → you hear the source.
3. When you hear a moment you want, hit **Capture** (set **Capture slot** first
   to bank several).
4. Pull **Input level** down, **Voice level** up.
5. Set **Texture**, and **Morph** between slots. Sweep **Capture point** by ear
   to land exactly on the moment you wanted.

It's a generator: it only sounds with the **transport rolling** (or the track
armed + monitored). Render to commit a result.

## Sliders

**Capture**
- **Capture slot** (1–4) — which slot the next Capture writes to / Audition monitors.
- **Capture** (Off / Capture now) — grab the current moment into the slot.
- **Capture point** (earliest .. at press) — *where in the captured ~0.68 s to
  analyze* (see "How capture works"). Re-analyzes live (no re-capture); it's a
  **set-once / by-ear** control — heavy to recompute, so **don't automate it**.

**Levels**
- **Input level (dry)** — the source passed straight through. −60 dB = silent.
- **Voice level** — the resynthesized output. −60 dB = silent.

**Character & tone**
- **Texture** (0 voice .. 100 wash) — the crossfade above.
- **Window size (ms)** — *synthesis grain length* for the wash: short =
  rougher/grainier, long = glassier/smoother. Cheap to change and **safe to
  automate** — it no longer re-analyzes (that's decoupled to a fixed analysis
  window + Capture point), so it won't drop out under an envelope.
- **Spread (Hz)** — blurs the spectrum across frequency: diffuses a narrow
  capture into a wider noise bed.
- **Pitch (semitones)** — transpose. Tape-style: formants move with pitch, so one
  capture covers a range of "body sizes." Drives both engines.
- **Stereo width** — decorrelates L/R in the wash for width (mono-safe).
- **Low cut (Hz)** — removes low rumble from the resynth.
- **Denoise** — spectral subtraction: thins toward the strongest partials (more
  tonal / gated as you raise it).

**Playback**
- **Audition** (Focused slot / Morph) — *Focused slot* plays exactly the Capture
  slot (hear each grab as you build them, ignoring Morph); *Morph* plays the
  morph blend.
- **Morph** (0–100) — crossfade across captured slots (pitch-preserving: each
  slot plays at its own pitch, no portamento).
- **Auto-morph** (Off / Sweep / Glide once) — in-plugin morph motion (Sweep =
  endless back-and-forth, Glide once = slot 1 → last one time).
- **Auto-morph time (sec)** — duration of one auto-morph pass.

## How capture works (and the ~0.68 s number)

Capture doesn't grab a single instant — it grabs a rolling buffer of the **most
recent 32768 samples** of input (the largest FFT JSFX allows) and stores that
whole chunk. The analysis looks at **one window inside that chunk**, and
**Capture point** positions that window: 0 = the start of the grab, 100 = the
press instant.

32768 samples is a fixed *sample* count, so its **duration depends on sample
rate**:

| Sample rate | Grab length |
|---|---|
| 44.1 kHz | ~0.74 s |
| 48 kHz | ~0.68 s |
| 96 kHz | ~0.34 s |
| 192 kHz | ~0.17 s |

The analysis window is a **fixed ~170 ms** (decoupled from Window size), and
Capture point slides that fixed window through the grab. It defaults to
**earliest** because of reaction latency: by the time you hear a vowel and press,
it's already a beat in the past (near the start of the grab); the press-moment
tends to catch the breathy release.

## Use cases / tips

- **Freeze / infinite sustain** — capture a moment and hold it forever: extend a
  reverb tail, sustain a chord, stretch a half-second into an endless bed.
- **Insert effect or generator** — keep Input up to blend a frozen layer under
  the live track (parallel freeze), or pull Input down for a pure drone.
- **Source-agnostic** — capture synths, field recordings, strings, cymbals, a
  whole mix via a send. Wash texturizes anything; harmonic works on pitched
  sources.
- **Automation** — every parameter is automatable; draw envelopes on Texture /
  Morph / Pitch / Spread for evolving movement (Auto-morph is the in-plugin
  substitute when you don't want to automate).
- **Stack instances** — different captures / pitches / spreads / widths layered =
  thick, wide beds (try two instances at slightly different Pitch for width).
- **Render-and-loop** — render the morph/drone to a WAV and loop it (suite
  pipeline).
- **4-point morph path** — capture four contrasting moments, Auto-morph "Glide
  once" for a one-shot sweep or "Sweep" for endless drift.
- **Capture point as a scrub** — hunt transitional timbres inside the 0.68 s grab,
  not just latency compensation.

## Technical notes / caveats

- **It's a generator** — needs the transport rolling or the track armed +
  monitored to make sound.
- **Captures persist** across save/reopen (`@serialize` stores the raw audio;
  both engines re-derive on load). Cost: ~512 KB per instance baked into the
  `.RPP` — several instances make a multi-MB project file.
- **What's safe to automate:**

  | Control | Automate? | Why |
  |---|---|---|
  | Texture, Morph, Pitch, Spread, levels, Stereo width, Low cut, Denoise | ✅ yes | applied per-sample/per-grain, no re-analysis |
  | Window size | ✅ yes | rebuilds only the cheap synthesis grain (no re-FFT, no buffer clear) |
  | Capture point | ❌ no | re-analyzes (FFT + pitch-detect); set it once by ear |
  | Capture / Capture slot | ❌ no | momentary action / selector, not continuous |

- **Capture point is debounced** — a by-ear scrub recomputes only when it settles,
  so it doesn't stutter while you move it. (Window size is *not* debounced — it's
  cheap enough to update every block.)
- **High sample rates shorten the grab** (table above) — the capture look-back
  and Capture-point range halve at 96 k, quarter at 192 k.
- **The harmonic (voice) engine is mono.** Width is a wash-end quality.
- **Pitch detection can octave-error** on the harmonic end (YIN locks to the
  octave when a harmonic is louder than the fundamental). Re-capture if a grab
  lands an octave off.

## Known limitations / future

- **Voice *with* breath isn't built yet.** The voice end (additive) has the vowel
  but no breath; the wash end has breath but de-voices. The proper fix is an
  SMS / harmonic+residual model: keep the harmonic sines and wash *only* the
  residual (spectrum with harmonic peaks notched out = the breath between
  harmonics), summed = a coherent breathy voice. Next real DSP step.
- **No manual octave-fix control** on the harmonic end yet.
- **Grab length is tied to the max FFT size.** If the look-back ever feels too
  short (e.g. at high sample rates), a longer grab ring decoupled from the FFT
  size is possible.
