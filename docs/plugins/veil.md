# Veil

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Veil muffles a **mono voice** the way the womb does — a steep lowpass around
~500 Hz, *"like speech from behind a heavy curtain."* Real prenatal hearing works
this way: tissue and fluid attenuate everything above ~600 Hz, and newborns
actually *prefer* a low-pass-filtered version of their mother's voice over a clean
one. Veil is that curtain — a thin thing you hear *through*.

It's an **effect**: put it on a mono voice track (recorded, TTS, sung — anything).

**Why Veil and not the [Resonant Sweeping Filter](sweeping-filter.md)?** They're
different tools even though both are resonant lowpass filters:

- Veil gives you a **still, wide muffle** — stereo width from *fixed, independent*
  Left/Right cutoffs, sitting perfectly still. The Sweeping Filter's stereo comes
  from a *moving* sweep; stop the motion and its width collapses. Veil's doesn't.
- Veil cascades up to **−48 dB/oct** — a far deeper muffle than the Sweeping
  Filter's fixed −12 dB/oct.
- Veil's two channels are **independent**, so their drifts can wander apart and
  together — the *width itself breathes*. The Sweeping Filter shares one band
  across the stereo field, so it can't.

Short version: reach for the Sweeping Filter when you want *movement*; reach for
Veil when you want a *still, deep, wide muffle* (that can then breathe). They also
**stack** — Veil for the character, Sweeping Filter after it for motion.

## Signal Architecture

- **Mono sum in.** The input is summed to mono, then fed to two independent filter
  chains — so a mono voice becomes stereo. (A lowpass alone can't do that; the
  width is *manufactured* by making the two channels differ.)
- **Two independent lowpass chains (L / R).** Each is a cascade of 1–4
  Chamberlin state-variable lowpass stages (Slope), with its own cutoff and its
  own resonance.
- **Width = the cutoff difference.** Left at 480 and Right at 520 gives a gentle
  spread; pull them apart for more. Because the channels differ only in *spectral
  rolloff* (no phase or delay tricks), a mono sum just averages the two rolloffs —
  **no comb-notch cancellation, safe on a single speaker / phone / HomePod.**
- **Per-channel Drift + Speed Ramp** on both cutoffs and both resonances, so the
  muffle can move (see below).

## Parameters

**Left cutoff (Hz)** `100–2000, default 480` — the Left channel's muffle point.

**Right cutoff (Hz)** `100–2000, default 520` — the Right channel's muffle point.
The **difference between the two cutoffs is the stereo width** — together = mono,
apart = wide.

**Left resonance** `0–1, default 0.15` — emphasis at the Left cutoff. Low = a
plain soft muffle; higher = a resonant "throat" around the corner.

**Right resonance** `0–1, default 0.15` — same, for the Right channel.

**Slope (dB/oct)** `−12 / −24 / −36 / −48, default −12` — how many lowpass stages
cascade (1–4). Steeper = more muffled, closer to the womb's real deep rolloff.
−12 is closest to a plain stock lowpass; −48 is deeply submerged.

**Output (dB)** `−24 to +12, default 0` — level trim.

### Drift (nested selector)

A slow, perpetual wander on any of the four moving parameters — this is what makes
Veil feel *alive* rather than a static EQ. Pick a target, set how far it wanders,
and it wanders forever. **All targets drift in parallel**; the selector just picks
which one the amount/period/shape sliders are editing right now.

**Drift target** `Left cutoff / Right cutoff / Left resonance / Right resonance` —
which parameter you're configuring.

**Drift up amount / Drift down amount** `units match target` — how far it wanders
above / below the base value. Separate up and down let the wander sit off-centre.
The amount is in the **target's own unit**: Hz for a cutoff (use the big end of
the range), 0–1 for a resonance (use the small end). You tune it *by ear* — nudge
until the wander feels right.

**Drift period (seconds)** `1–600, default 20` — how long one full wander cycle
takes. **Give Left and Right cutoffs *different* periods** (say 20 s and 31 s) and
the width itself breathes — the signature Veil move.

**Drift shape** `Sine / Triangle / Random, default Sine` — Sine = smooth wander,
Triangle = linear ramps, Random = smooth wander to unpredictable targets.

### Speed Ramp (nested selector)

A **one-time** signed ride on a parameter over N minutes — for a slow, hands-off
change while you settle. Unlike Drift (which repeats forever), the Ramp moves once
and holds. All targets ramp in parallel on their own clocks.

**Speed ramp target** `Left / Right cutoff / resonance` — which parameter rides.

**Speed ramp by** `units match target` — the signed amount to move by. **Positive
on both cutoffs = the voice slowly CLEARING** (the muffle opening, as if the baby
were growing); negative = deepening / darkening.

**Speed ramp duration (minutes)** `0–60, default 0` — how long the ride takes.
`0` = off.

**Speed ramp engage** `Off / On, default Off` — a freeze/resume gate. While On the
ramp advances; flip Off and it freezes where it is; back On and it resumes (it does
*not* restart). Only pressing transport Play restarts a ramp from the beginning.

**Speed ramp start delay (minutes)** `0–60, default 0` — wait this long after
engaging before the ride begins. "Let me settle first, then start clearing."

## Usage Notes

- **Feed it a mono voice.** If the source is already stereo, Veil sums it to mono
  first — it's built to *create* width, not preserve existing width.
- **Set the muffle, then the width.** Dial both cutoffs to taste (start ~500),
  pick a Slope (−12 for gentle, steeper for deep), then spread the two cutoffs
  apart until the stereo feels right.
- **Breathing width:** drift Left cutoff and Right cutoff on *different* periods.
  The gap between them wobbles, so the stereo image gently opens and closes — the
  thing the Sweeping Filter can't do.
- **The clearing:** target both cutoffs with a positive Speed ramp `by` over a
  long duration — the voice slowly emerges from behind the veil.
- **Pairs with** the [Womb Sound Generator](womb.md) (heartbeat / breath bed
  underneath), and [Bubbler](bubbler.md) / [Dapple](dapple.md) for fluid texture.

---

*Veil is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic).*
