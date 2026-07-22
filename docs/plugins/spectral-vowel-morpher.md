# Spectral Vowel Morpher

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

A capture-based instrument. You play audio into it, capture a few moments, and it resynthesizes them — as a recognizable voice, an evolving wash, or any blend between — and morphs between the captured moments. It is built for sustaining and looping vocal material, but it freezes any source.

Unlike Sustain Looper (which loops a region of a *loaded* file), the Morpher feeds on **live audio playing into it** — drop a WAV on the track or send another track in, play it, and hit Capture when you hear a moment you want. Captures persist across project save and reopen.

It is a generator: it only sounds with the transport rolling (or the track armed and monitored).

---

## Signal Architecture

Every capture is analyzed two ways at once, and the **Texture** knob crossfades between them.

### Voice (harmonic) — Texture 0

Detects the pitch and rebuilds the sound from 64 harmonics placed at the exact fundamental. Phase-coherent, so it keeps the vowel and pitch cleanly — a sustained vowel or choir. It reproduces only the *harmonic* part, so it has no breath or air, and it only makes sense on clearly pitched material.

### Wash (spectral) — Texture 100

PaulStretch-style phase randomization: it keeps the magnitude spectrum and discards phase, turning every partial into a narrow noise band. Smooth, breathy, evolving — it turns any source into texture. On a voice it deliberately reads as softly "denoised" (that is the operation, not a fault) — ideal for pads and beds.

### Capture

Capture grabs the most recent ~0.68 seconds of input (a fixed sample count, so the *duration* shrinks at higher sample rates) and stores that whole window. The analysis looks at one slice inside it, positioned by **Capture point** — and each slot remembers its own Capture point, so you tune every capture to its own moment independently. Both engines re-derive from the stored raw audio, so you can re-analyze (sweep Capture point, change the wash grain) without re-capturing, and the captures survive a project reload.

---

## Parameters

**Capture slot** `1 to 8, default 1`
Which of the eight slots the next Capture writes to, which slot Audition monitors in Focused mode, and — since each slot has its own **Capture point** — which slot's saved point the Capture point slider shows and edits. Switching slots swaps the Capture point display to that slot's stored value.

**Capture spectrum** `Off / Capture now`
Grab the current moment into the selected slot. It captures *whatever audio is reaching the track at that instant* — so if you fire it while nothing is playing (transport stopped, or no source feeding the track), you'll bank an **empty slot**, and the morph will fade to silence whenever it reaches that slot.

**Capture now disarms itself after each capture** — it returns to Off the moment it fires, so you can never leave it armed by accident. A reloaded project always opens with it parked Off and can't silently re-fire over one of your slots on load. (If a slot ever goes unexpectedly silent and the morph fades out when it reaches it, the cause was almost always Capture left armed; this behavior is what prevents it.)

**Capture point** `0 to 100, default 0` — *per slot*
*Where* in the captured ~0.68 s to analyze — 0 = earliest, 100 = the instant you pressed. Defaults to earliest because, by the time you react and press, the sound is already a beat in the past; the press-moment tends to catch the breathy release. Re-analyzes live, so sweep it by ear to land on the vowel. Set-once — not an automation target (it re-runs the full analysis).

**Each slot keeps its own Capture point.** When you capture a slot it remembers where you scrubbed to, and scrubbing one slot no longer re-tunes the others. Switching **Capture slot** shows that slot's saved point on the slider, so you can bank several captures and tune each one to its own vowel independently. Saved points persist across reload. (Older projects made before this change open with every slot on the single point they shared; re-scrub any slot to give it its own.)

**Input level (dry, dB)** `-60 to +12, default 0`
The source passed straight through. −60 = silent.

**Voice level (dB)** `-60 to +12, default 0`
The resynthesized output. −60 = silent.

**Texture** `0 to 100, default 50`
Crossfades 0 = Voice (harmonic, keeps the vowel) to 100 = Wash (spectral, breathy bed). The middle layers both — vowel plus air.

**Wash grain (ms)** `5 to 680, default 150`
The wash's grain length: short = rougher and grainier, long = glassier and smoother. Affects only the wash; cheap and safe to automate.

**Spread (Hz)** `0 to 150, default 0`
Blurs the spectrum across frequency — diffuses a narrow capture into a wider noise bed.

**Pitch (semitones)** `-24 to +24, default 0`
Transposes both engines, tape-style (formants move with pitch), so one capture covers a range of "body sizes."

**Stereo width** `0 to 100, default 50`
Spreads the stereo image of *both* engines. In the wash it decorrelates L/R phase (mono-safe). In the voice it runs a slightly-detuned copy on the right channel (up to ~14 cents at 100), so the two sides beat slowly against each other — real width plus a shimmer that softens the robotic edge of the pure harmonics. At 0 the voice is exactly mono (unchanged from older projects). The detuned voice is only computed when the voice is actually audible (Texture below full wash), so living on the wash costs nothing.

**Low cut (Hz)** `0 to 500, default 0`
Removes low rumble from the resynth.

**Denoise** `0 to 100, default 0`
Spectral subtraction — raise to thin toward the strongest partials (more tonal, more gated).

**Audition** `Focused slot / Morph, default Morph`
*Focused slot* plays exactly the Capture-slot, ignoring Morph (so you can hear each grab as you build it). *Morph* plays the morph blend.

**Morph** `0 to 100, default 0`
Crossfades across the captured slots. Pitch-preserving — each slot plays at its own pitch, so there is no portamento glide.

**Auto-morph** `Off / Sweep / Glide once / Shuffle, default Off`
In-plugin morph motion — Sweep = endless back-and-forth; Glide once = slot 1 to the last, one time; Shuffle = like Sweep, but in *random* order: it glides through all your captured slots visiting each once, then reshuffles and goes again. One full pass takes one Auto-morph time, so each slot gets an equal share of it — same timing and same gentle crossfades as Sweep, just shuffled (and a different order each time you open the project). Shuffle only moves *where* the morph is sitting (it never introduces a new pitch), so it is exactly as clash-safe as moving the Morph slider by hand — safe on chordal captures at different pitches. *(This mode was called "Drift" before; renamed to Shuffle so it isn't confused with the suite-wide Drift feature below, which is a different thing.)*

**Auto-morph time (sec)** `1 to 600, default 20`
How fast the motion moves. For Sweep/Glide it's the duration of one pass; for Shuffle it's the duration of one full pass through *all* your slots (each slot gets an equal fraction). Lower it for quick wandering, raise it for a long, slow motion.

**Auto-morph time means** `Whole pass / Each step, default Whole pass`
How to read the Auto-morph time number.

- **Whole pass** — the original meaning: that many seconds for the *entire*
  journey across your slots. Capturing another slot therefore makes every step
  *faster*, because the same total gets divided more ways. With exactly two
  slots "whole pass" and "one step" are the same thing, which is why this only
  surprises you once you capture a third.
- **Each step** — the number is the time for *one* step. Adding a slot makes the
  cycle longer instead of quicker. This is what you want for pacing work: a
  breath does not speed up because you gave it more stages.

Left on **Whole pass** by default, so existing projects are unchanged.

**Slot dwell %** `10 to 500, default 100`
Per slot: how long the step *leaving* this slot takes, relative to the others.
100 is even — the previous behaviour. 200 makes that step twice as long as an
even one; 50 makes it half.

Like **Capture point**, this belongs to whichever **Capture slot** is selected —
select a slot, set its dwell, select another, set that one. Each slot remembers
its own, and they save with the project.

This is what makes an uneven cycle possible. A real breath is not symmetrical:
the out-breath is usually longer than the in-breath, and a hold is longer than
either. With dwell you set those proportions directly instead of accepting an
even walk. Combined with **Each step**, the Auto-morph time becomes the length
of a single even step and each slot's dwell scales its own.

Works in all three Auto-morph modes.

### Drift (in-plugin automation)

Drift makes a parameter **wander on its own** — the suite's stand-in for drawing an automation envelope, so you get slow evolving motion without a mouse or an automation lane. Pick a target, set how far it wanders up and down and how long a full wander takes, and it moves by itself while the transport rolls. **Every target drifts at once** — the selector only chooses which one the four sliders below are editing right now; the others keep drifting with whatever you last set them to.

**Drift target** `Texture / Spread / Pitch / Stereo width / Low cut / Voice level, default Texture`
Which parameter the Drift sliders below are editing. Switch it and the four sliders show *that* target's settings; anything you set on another target keeps running in the background.

**Drift up amount** / **Drift down amount** `0 to 300, units match the target, default 0`
How far it wanders above (up) and below (down) the parameter's current value, in that parameter's own units — Texture in its 0–100, Pitch in semitones, Low cut in Hz, and so on. Separate up and down let the wander sit off-centre (that's what makes it feel alive rather than mechanical); set them equal for symmetric drift. Both at 0 means this target isn't drifting.

**Drift period (seconds)** `1 to 600, default 30`
How long one full wander takes, in real seconds (this instrument has no tempo, so the period is wall-clock, not beats). 30 is a gentle sway; a few minutes is barely-there evolution.

**Drift shape** `Sine / Triangle / Random, default Sine`
The path of the wander. Sine = smooth continuous sway; Triangle = straight ramps up and down with turnarounds; Random = drifts smoothly toward a new random spot each period (still smooth, just unpredictable in direction).

**Drift restart** `Restart on play / Free-running, default Restart on play`
What the transport does to the drift — this is the choice between *synced* and *continuous*.
- **Restart on play** snaps every drift back to the start of its cycle the moment you press play from a stop. Run the plugin on several tracks with the **same period and Sine/Triangle shape**, and they all reset *together* — so their drifts stay in step instead of wandering out of phase and clashing (e.g. Pitch drifts pulling against each other). This is the mode for locking multiple tracks together.
- **Free-running** ignores the transport completely: the drift just keeps evolving. Loop a sound *under or over* it and the drift flows straight through, unbroken — no jump when the loop comes round, no jump when you press play. This is the mode for one continuous, ever-moving texture.

Either way, a loop *repeating* never restarts the drift — it always flows across loop boundaries. Only pressing play from a stop resets it, and only in **Restart on play**. Drift is separate from Auto-morph (which moves *which* slots you're between): Drift moves the *parameters*, so the two compose — Shuffle through your captures while Texture and Low cut slowly breathe underneath.

### Ramp (in-plugin slow ride)

Ramp is a **one-time slow ride** of a parameter — you set where to move it and over how long, arm it, and it glides there once and holds. It's the one-directional partner to Drift (Drift wanders back and forth forever; Ramp makes a single slow arc), and it's built for the sleep wind-down: e.g. **ride Texture from voice to wash over 20 minutes** as someone drifts off, or **Voice level down to silence over 30 minutes** for a hands-free fade — no automation lane needed. *(This is the same feature the other plugins call "Speed Ramp." It's just called "Ramp" here because this plugin has no rate/speed to ramp — it rides a value instead.)*

Like Drift, every target rides in parallel; the selector chooses which one the sliders are editing. Ramp and Drift stack on the same parameter (base value + Drift wander + Ramp ride).

**Ramp target** `Texture / Spread / Pitch / Stereo width / Low cut / Voice level, default Texture`
Which parameter the Ramp sliders below are editing (same targets as Drift).

**Ramp by** `-300 to +300, units match the target, default 0`
How far to move the parameter, and which direction — in that parameter's own units (Texture 0–100, Pitch semitones, Low cut Hz…). Negative goes down, positive up. **0 means this target doesn't ramp**, so arming Ramp with everything at 0 safely does nothing.

**Ramp duration (minutes)** `0 to 60, default 0`
How long the ride takes. 0 = this target doesn't ramp. Set it to, say, 20 and the parameter takes twenty minutes to travel its full `by` amount, then holds.

**Ramp start delay (minutes)** `0 to 60, default 0`
Wait this many minutes after arming before the ride begins — e.g. "let me settle for 10 minutes, *then* start winding down."

**Ramp engage** `Off / On, default Off`
Arms every configured target at once. While On, each rides its own duration from where it is; flip Off and they freeze in place (flip back On and they resume). The ride starts fresh from the current values each time the transport begins playing. You can aim several targets at once (Texture *and* Voice level *and* Low cut, each over its own time) and one Engage winds them all down together.

---

## Usage Notes

- **The capture workflow.** Put audio on the track, Input level up and Voice level down so you hear the source. When you hear the moment, hit Capture (set Capture slot first to bank several). Then pull Input down, Voice up, set Texture, and Morph between slots. Sweep Capture point by ear to land exactly on the moment — and because each slot keeps its own point, you can go slot by slot and tune every capture to its own vowel without disturbing the ones you already set.
- **The voice end needs pitched material.** Texture 0 only sings on clearly pitched sources (a sustained vowel, organ, bowed note). On unpitched material it produces a tone — use the wash end (or the middle) there instead.
- **Vowel + breath is the middle.** The pure voice end has no breath; the pure wash end has breath but de-voices. A blend around Texture 30–50 gives the vowel plus air.
- **What is safe to automate:** Texture, Morph, Pitch, Spread, the levels, Stereo width, Low cut, Denoise, and Wash grain. Capture point and Capture are not (they re-analyze, or are momentary). Six of the automatable ones — Texture, Spread, Pitch, Stereo width, Low cut, Voice level — can also be moved hands-free from *inside* the plugin with **Drift** (endless wander) and **Ramp** (a one-time slow ride), no automation lane needed.
- **Source-agnostic.** It freezes anything — synths, field recordings, strings, cymbals, even a whole mix via a track send. The wash texturizes any source.
- **Captures persist** across save and reopen (the raw audio is stored in the project; both engines rebuild on load).
- **Transport must be moving** for it to sound — it is a generator. Loop the transport, or arm the track and monitor.

See [`docs/spectral-vowel-morpher.md`](spectral-vowel-morpher.md) for deeper design notes and advanced techniques.

---

*Spectral Vowel Morpher is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

