# Shared Systems

Machinery that appears in more than one plugin, documented once here so each
plugin page can point at it instead of repeating the same explanation. If you
grabbed a single plugin, grab this page too — between the two you have
everything that plugin does.

Each plugin page still lists **its own** exact targets, slider ranges, and
period unit (they differ per plugin). This page explains **how the controls
work**; the plugin page tells you **what its targets are**.

*Designed by Rozaya — Developed with Claude (Anthropic). Public domain (CC0).*

---

## Contents

- [Drift](#drift) — organic wandering of a parameter
- [Speed Ramp](#speed-ramp) — a one-time ride of a parameter from A to B (called **Ramp** in the Spectral Vowel Morpher)
- Pan Modes — *still documented inside each plugin page; consolidation here is pending*
- Rate Mode (Hz / Seconds / BPM) — *still per-plugin; pending*
- Start Delay — *still per-plugin; pending*
- Play / Rest gate — *still per-plugin; pending*

---

## Drift

Drift adds slow, organic wandering to a parameter, so a fixed value doesn't feel mechanical over a long stretch — a real heart speeds up and slows a little, a filter sweep breathes. Drift is the "it's alive" texture. Every rate-bearing plugin carries its own self-contained Drift block; there is no separate modulator plugin and no cross-plugin routing. You set drift per plugin, and it's guaranteed to work with nothing to patch.

### The nested-selector pattern

Drift can wander **many targets at once** (heart rate, a filter edge, a pan rate, a per-voice level, etc.), but it only ever shows **one target's settings at a time**, so the control surface stays small. It works like this:

1. **Drift target** — a selector. Turn it to the parameter you want to set drift for.
2. The drift sliders below it (**up amount / down amount / period / shape**) now edit **that** target. Switching the selector saves what you just set into that target's memory and loads the next target's saved settings in.
3. **Every configured target drifts in parallel** — the selector only chooses which one you're *editing*, not which one is *active*. All of them run at once. Configurations persist across project save/load.

So "wander the heart rate a little AND wander the S1–S2 gap on a different period" is: set target = Heart BPM, dial its up/down/period; switch target = S1–S2 gap, dial its up/down/period. Both wander together.

### The drift sliders

- **Drift up amount** — how far it wanders **above** the center value. **Positive number.**
- **Drift down amount** — how far it wanders **below** the center value. **Positive number**, set independently from up. The up/down split lets the wander be asymmetric (e.g. up 0.2 / down 0.05 = "occasional surges" rather than an even sway). Both in the selected target's own units.
- **Drift period** — how long one wander cycle takes. **The unit depends on the plugin** — the plugin's own cycles, beats, or wall-clock seconds (see the table below). Some plugins (Resonance Bank) add a **Drift period mode** slider so you pick BPM / Hz / Seconds.
- **Drift shape** — **Sine** (smoothest, the safe default) / **Triangle** (linear rises, a defined corner at peak/trough) / **Random** (value-noise — picks a random target within range and slews smoothly toward it, then picks again; unrepeating).

**Defaults are off.** Every up/down amount defaults to 0; set at least one to a non-zero value to engage a target. With both at 0 that target does nothing regardless of period or shape.

**Drift period unit, per plugin:**

| Plugin | Drift period unit |
|---|---|
| Heartbeat Generator | heartbeats |
| Breath Generator | breath cycles |
| Womb Sound Generator v3 | heartbeats or breath cycles |
| Rhythm Track | beats |
| Shepard Scale Generator | beats |
| Shepard Tone Generator | cycles |
| Polyrhythm Phase | cycles |
| Melody Phase | cycles |
| Full Feature Tremolo | cycles |
| Resonant Sweeping Filter | cycles |
| Sweep Dwell Filter | cycles |
| Resonance Bank | BPM / Hz / Seconds (via a **Drift period mode** slider) |
| Spectral Vowel Morpher | seconds (plus a **Drift restart**: Restart on play / Free-running) |

### On transport

On every transport play press, the drift **cycle** restarts (each target's phase → 0, offset 0 at the first sample, wandering out from there), while the drift **configuration** (your up/down/period/shape per target) is preserved across stop/play and project save/load. This makes Sine and Triangle renders deterministic; Random is non-deterministic by design.

### A note on per-voice plugins

**Polyrhythm Phase** and **Shepard Tone Generator** *also* have older per-voice "Drift / Rate" sliders (one per voice), which are separate from this nested-selector Drift block. See those two plugin pages for how their per-voice controls interact with the drift selector.

---

## Speed Ramp

Where Drift *wanders* a parameter, **Speed Ramp** *rides* it once — a single move from its current value to a new one over a set duration, then it stays there. It's the in-plugin substitute for DAW automation (which isn't screen-reader-friendly): "over the next 30 minutes, wind the heart rate down and lengthen the exhale." **The Spectral Vowel Morpher calls this feature just "Ramp"** (Ramp target / Ramp by / Ramp duration / Ramp engage / Ramp start delay); everywhere else it's "Speed ramp."

It uses the same nested-selector shape as Drift — one target selector, its settings below, all configured targets ride in parallel.

### The ramp sliders

- **Speed ramp target** — selector; pick the parameter to ride.
- **Speed ramp by** — the amount to move, **in the selected target's own units**. This one is **signed**: **positive ramps the value up, negative ramps it down.** (That's the difference from Drift's two positive sliders — here one signed slider carries direction.) The range is wide and varies per plugin (see table); 0 = no move, so engaging at 0 does nothing.
- **Speed ramp duration (minutes)** — how long the ride from start value to start + `by` takes. A target with duration 0 doesn't ramp.
- **Speed ramp engage** (Off / On) — arms the ramp. It's a **freeze/resume gate, not a restart trigger**: while On the ramp advances; while Off it freezes where it is and resumes from there. The **only** thing that resets a ramp back to the start is a transport play press.
- **Speed ramp start delay (minutes)** — wait this many minutes after engage before this target starts moving. Stagger targets by giving them different delays ("let me fall asleep first, then begin the wind-down").

**`by` range, per plugin** (all signed; units match the selected target):

| Plugin | Speed ramp `by` range | Notes |
|---|---|---|
| Breath Generator | ±20 | |
| Heartbeat Generator | ±400 | |
| Womb Sound Generator v3 | ±2000 | |
| Rhythm Track | ±300 | |
| Shepard Scale Generator | ±300 | |
| Shepard Tone Generator | ±1000 | |
| Polyrhythm Phase | ±1000 | |
| Melody Phase | ±1000 | |
| Full Feature Tremolo | ±1000 | |
| Resonant Sweeping Filter | ±5000 | covers ±5 kHz frequency rides |
| Sweep Dwell Filter | ±60 | |
| Spectral Vowel Morpher | ±300 | called **Ramp by** |
| Resonance Bank | — | **no Speed Ramp** (Drift only) |

### Mode-direction caveat

For plugins whose rate slider has Hz / Seconds / BPM modes (Shepard Tone, Full Feature Tremolo, Sweeping Filter, Polyrhythm Phase, Melody Phase): in **BPM and Hz** modes, a negative `by` = slower (intuitive). In **Seconds** mode (where the rate is a *period* in seconds), a **positive** `by` = longer period = slower (flipped). Know which mode you're in.

---

*Part of the Rozaya JSFX plugin suite. Designed by Rozaya — Developed with Claude (Anthropic).*
