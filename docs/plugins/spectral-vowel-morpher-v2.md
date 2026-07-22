# Spectral Vowel Morpher v2

**Designed by Rozaya — Developed with Claude (Anthropic)**

> **This is v2**, a separate plugin from
> [Spectral Vowel Morpher](spectral-vowel-morpher.md) so the original keeps
> working untouched in projects that already use it. Both can be installed at
> once. Two things differ:
>
> **1. Short grains work.** The synthesis FFT is sized to the grain rather than
> fixed at maximum, so the low end of **Wash grain** is usable. On the original
> it drops out.
>
> **2. Each slot holds for its own length of time, in seconds.** The single
> global *Auto-morph time* is gone. Every slot now carries its own **Slot
> linger**, and the cycle is simply its steps added up. Adding a slot makes the
> cycle longer instead of squeezing the existing steps, and — the point of it —
> the steps can differ from each other.
>
> **3. Every setting that describes a capture is per slot.** Voice level,
> Texture, Spread, Pitch, Stereo width, Low cut and Denoise all belong to the
> selected slot rather than being one global setting flattening every capture.
> The morph crossfades them along with the spectra, so moving between two slots
> moves between their settings too. Input level stays global (the dry signal is
> the track's, not a capture's), and so does Wash grain (it rebuilds a window
> rather than scaling a value, so it cannot be crossfaded per grain).
>
> Controls are also grouped by what they belong to rather than by when they were
> added, so everything owned by the selected slot — **Capture point**, **Slot
> linger**, and the seven above — is reached through **Capture slot**.

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

*Per slot.* Belongs to whichever **Capture slot** is selected; the morph crossfades it between slots along with the sound itself.

**Texture** `0 to 100, default 50`
Crossfades 0 = Voice (harmonic, keeps the vowel) to 100 = Wash (spectral, breathy bed). The middle layers both — vowel plus air.

*Per slot.* Belongs to whichever **Capture slot** is selected; the morph crossfades it between slots along with the sound itself.

**Wash grain (ms)** `5 to 680, default 150`
The wash's grain length: short = rougher and grainier, long = glassier and
smoother. Affects only the wash; cheap and safe to automate. The unit is
**milliseconds**, so 300 is about a third of a second per grain — not a fraction
of one.

**CPU is roughly flat across the whole range in v2.** In the original the
synthesis FFT was a fixed size no matter how short the grain, while grains fire
on a hop of a quarter of the grain length — so shortening the grain multiplied
the work without making any individual grain cheaper, and the bottom of the
range dropped out on most machines (evenly-spaced gaps, which is real-time
underrun rather than a windowing artifact). v2 sizes the FFT to the grain, which
is all a grain can carry anyway: short grains fire often but each is small, long
grains are large but rare, and the two cancel.

**Spread (Hz)** `0 to 150, default 0`
Blurs the spectrum across frequency — diffuses a narrow capture into a wider noise bed.

*Per slot.* Belongs to whichever **Capture slot** is selected; the morph crossfades it between slots along with the sound itself.

**Pitch (semitones)** `-24 to +24, default 0`
Transposes both engines, tape-style (formants move with pitch), so one capture covers a range of "body sizes."

*Per slot.* Belongs to whichever **Capture slot** is selected; the morph crossfades it between slots along with the sound itself.

**Stereo width** `0 to 100, default 50`
Spreads the stereo image of *both* engines. In the wash it decorrelates L/R phase (mono-safe). In the voice it runs a slightly-detuned copy on the right channel (up to ~14 cents at 100), so the two sides beat slowly against each other — real width plus a shimmer that softens the robotic edge of the pure harmonics. At 0 the voice is exactly mono (unchanged from older projects). The detuned voice is only computed when the voice is actually audible (Texture below full wash), so living on the wash costs nothing.

*Per slot.* Belongs to whichever **Capture slot** is selected; the morph crossfades it between slots along with the sound itself.

**Low cut (Hz)** `0 to 500, default 0`
Removes low rumble from the resynth.

*Per slot.* Belongs to whichever **Capture slot** is selected; the morph crossfades it between slots along with the sound itself.

**Denoise** `0 to 100, default 0`
Spectral subtraction — raise to thin toward the strongest partials (more tonal, more gated).

*Per slot.* Belongs to whichever **Capture slot** is selected; the morph crossfades it between slots along with the sound itself.

**Audition** `Focused slot / Morph, default Morph`
*Focused slot* plays exactly the Capture-slot, ignoring Morph (so you can hear each grab as you build it). *Morph* plays the morph blend.

**Morph** `0 to 100, default 0`
Crossfades across the captured slots. Pitch-preserving — each slot plays at its own pitch, so there is no portamento glide.

**Auto-morph** `Off / Sweep / Glide once / Shuffle, default Off`
In-plugin morph motion — Sweep = endless back-and-forth; Glide once = slot 1 to the last, one time; Shuffle = like Sweep, but in *random* order: it glides through all your captured slots visiting each once, then reshuffles and goes again. Every mode is timed the same way: each step lasts the **Slot linger** of the slot it is leaving, so a pass is however long its steps add up to — same gentle crossfades throughout, just a different order (and a different order each time you open the project). Shuffle only moves *where* the morph is sitting (it never introduces a new pitch), so it is exactly as clash-safe as moving the Morph slider by hand — safe on chordal captures at different pitches. *(This mode was called "Drift" before; renamed to Shuffle so it isn't confused with the suite-wide Drift feature below, which is a different thing.)*

**Slot linger (sec)** `0 to 300, default 4`
**Pure hold time** for this slot — how long you hear it alone, at 100%, before
its crossfade to the next slot begins. **The number you type is the number of
seconds.** No arithmetic to figure out, no ratios of anything.

Like **Capture point**, it belongs to whichever **Capture slot** is selected:
pick a slot, set its linger, pick the next, set that one. Each slot remembers
its own and they save with the project.

There is no global morph time. A cycle is just its steps added together — each
slot contributes `linger + crossfade` seconds. Set linger 4 on every slot and
each will hold for 4 seconds. Set linger 4 on one and 8 on another and their
holds differ, which is what an uneven cycle (like a real breath) needs.

Works in all three Auto-morph modes. In **Sweep**, which walks out and back,
each slot's linger applies whenever it is the current slot.

**Setting Slot linger to 0** means "no hold, all crossfade" — the whole leg
is the crossfade to the next slot. This matches the original Morpher's
continuous-morph behaviour and is right for evolving textures where the sound
never really settles.

**Slot crossfade (sec)** `0 to 300, default 1`
The fade from this slot to the next slot, added **on top** of the linger. Total
time on this slot's leg is `linger + crossfade`.

*Per slot*, edited the same way as Slot linger: belongs to whichever **Capture
slot** is selected.

- **Crossfade 0** — hard cut from this slot to the next at the end of the hold.
  Works cleanly when captures have soft edges of their own (like breath); can
  click if edges are sharp.
- **Crossfade small (0.5–2s)** — smooth transition without dominating. Natural
  for breath, spoken phrases, or anything where each slot should be recognisable
  as itself.
- **Crossfade large** — long, gradual crossfade. When combined with `linger 0`
  this reproduces the original Morpher's continuous-morph feel.

Independent per slot: silence-slots with a long hold can sit between two short
sound-slots with brief fades, or any other shape.

### Where does a slot "begin"?

Three plausible answers depending on what you mean. For a concrete case — slot 0
with `linger 4, crossfade 2`, then slot 1:

```
time:     0                 4          6                 10        12
          |------ hold ------|-- fade -|------ hold ------|-- fade |
what:     pure slot 0        slot 0→1  pure slot 1        slot 1→2
```

Three "beginnings" of slot 1:

1. **When you first hear slot 1** — time 4. Slot 1 fades in over 2 seconds
   while slot 0 fades out. Both are audible during those 2 seconds.
2. **When slot 1 is fully alone, no blend** — time 6. Slot 0's crossfade has
   completed and slot 1 is at 100%.
3. **When slot 1's own linger starts counting** — also time 6. Its hold runs
   6→10, then its own crossfade 10→12.

The rule underneath: **each slot contributes `linger + crossfade` seconds to
the cycle. Linger is pure hold; crossfade is the transition out.** The crossfade
at the boundary between two slots **belongs entirely to the earlier slot** —
slot 1 doesn't have an "inbound fade" of its own; slot 1's own crossfade is
only its *outbound* fade to slot 2.

The mental shortcut: **the fade lives between two slots and belongs to the
earlier one.** How do you get *out* of slot 3? Look at slot 3's crossfade. How
do you get *into* slot 3? Look at slot 2's crossfade. Never slot 3's — from
slot 3's view, "getting in" was slot 2's problem.

**Practical implication:**

- To hear slot 3 alone for 8 seconds, then have it transition over 2 seconds
  to slot 4: set slot 3's `linger 8, crossfade 2`.
- Total time from "slot 3 at 100%" to "slot 4 at 100%" = 8 + 2 = 10 seconds.
- Slot 4's timing is decided by slot 4's own linger and crossfade,
  independently. Slot 4 starts fading in during slot 3's crossfade regardless
  of what slot 4 is set to.

**Slot mute (Off / On)** `default Off`
When **On**, this slot is skipped by Sweep, Glide, and Shuffle. The morph
crossfades from the previous unmuted slot directly to the next unmuted slot,
with no fade to or from this one in between.

*Per slot*, edited the same way as everything else in this group: select the
slot via **Capture slot**, then toggle the mute.

**Focused slot mode ignores mute.** If you point at a muted slot in Focused
mode, you still hear it — Focused is "audition this specific slot no matter
what." So mute affects the *morph sequence*, not what a slot IS.

The canonical use is a captured silence slot between two audio slots. In the
original Morpher, a silence slot in the middle of the sequence meant every
crossfade had to traverse silence — which read as abrupt fade-outs and
fade-ins rather than a morph, because you cannot gradually fade INTO nothing.
Mute the silence slot and Sweep/Glide/Shuffle skip it entirely, giving you
sound-to-sound crossfades. The silence capture stays in the plugin's memory
and remains audible via Focused mode if you want to render it as a stem.

Also useful when you've captured five slots but only want a morph across three
of them today: mute the two you don't want in the sequence.

Edge cases: if every slot is muted, the morph is silent. If exactly one is
active, it plays solo (no morph, since there's nothing to morph between).
Both fall out of the sequencer naturally.

## A gotcha with silent (or otherwise "empty-feeling") slots

**Every per-slot setting belongs to the slot as captured** — including Stereo
width, Denoise, Pitch, Spread, and the rest. This is usually what you want:
each capture carries its own colour. But it means **a silent slot inherits
whatever the sliders were set to at the moment you captured it**, and if those
differ from your audio slots, the morph will crossfade the *settings* right
along with the audio — producing sweeps that seem to come from nowhere.

The classic version of this is: you capture your in-breath and out-breath at
one Stereo width, then capture silence for the pause between them at a
different Stereo width without meaning to. The plugin then dutifully sweeps
width from mono to wide as the morph passes through the silent slot, and it
sounds like some hidden LFO is animating stereo. It isn't. It's just the
per-slot width doing exactly what it says it does.

The fix is one of:

- **Configure the silent slot the same as your audio slots — ALL seven per-slot
  parameters, not just the one you noticed.** Select the silent slot via
  **Capture slot** and walk down: **Voice level, Texture, Spread, Pitch, Stereo
  width, Low cut, Denoise**. Set each to match your audio slots. Silence at
  any of these values sounds the same (silence is silence), but the moment the
  morph passes through the silent slot, each mismatched parameter animates
  audibly on your audio slots. Missing even one is enough to hear it. There is
  no way to know from listening to a silent slot alone that its Denoise is
  wrong — the mismatch only surfaces mid-crossfade.
- **Mute the silent slot** with **Slot mute** so the morph skips it entirely.
  Now the crossfade goes audio-to-audio and never traverses the silent slot's
  settings. This is the reliable fix if you don't care about the silent slot's
  own settings ever mattering.

In the original Morpher (v1) there was one global Stereo width, so this
couldn't happen — every slot shared the same width, and adding a silent
capture cost you nothing extra to configure. In v2, per-slot control is the
feature, but the cost is that empty-feeling slots (silence, near-silence,
placeholder captures) need their non-audio parameters set deliberately, or
you'll hear those parameters *animating* on you during transitions.

### The silence slot's crossfade does work for the slot after it

One more thing worth naming out loud. **A silent slot's own Slot crossfade
still matters, even though silence itself needs no fading** — because it
governs how the NEXT slot's audio appears.

Concretely: audio slot → silence → audio slot. The first audio slot's
crossfade decides how the sound melts away *into* the silence. The silence
slot's crossfade decides how the next audio slot appears *out of* the
silence. Setting the silent slot's crossfade to 0 gives you a hard-arrival
next-audio, which usually sounds like an abrupt sudden appearance even
though the audio itself is fading in from zero — because the transition
window is too short for your ear to register as "arriving."

Practical rule: **a silence slot between two audio slots wants a crossfade
of at least the same length as the audio slots' crossfades**, or a little
longer, so the arrival feels as gradual as the departure. This is the "the
fade belongs to the earlier slot" rule made concrete — you might not think
of a silence slot's crossfade as doing anything (its own audio has nothing
to fade), but it's the only control that shapes how the next sound gets
in.

### The auto-gain needs extra time coming out of silence

If you hear a slight bloom, level spike, or the audio "arriving louder
than it should" when an audio slot fades in from a silent one, that is the
plugin's slow auto-gain smoother catching up. During silence, the auto-gain
sits at whatever amplification it had before silence began (it can't
measure loudness from a signal that has none, so it freezes). The moment
audio starts fading back in, the amplification is still cranked up from
before, and the fresh audio gets multiplied by it before the smoother has
time to catch back down.

The fix is one of:

- **Add about a second more crossfade** on the silence slot (its crossfade
  governs the arrival) OR on the audio slot that is arriving. Either works.
  The extra time gives the auto-gain room to settle before the audio is
  fully in.
- **Match the level of the silence-adjacent slots more carefully** — the
  bloom is worst when the audio slot is much quieter than the peak-time
  auto-gain expected. Louder captures on either side smooth this.

In practice, a second more crossfade is the simple fix and it barely
changes the cycle timing at all — a good default reflex whenever you hear
a fade-in that feels too eager.

## The per-slot rule (and what it means for every parameter, not just silence)

The silent-slot section above is the sharpest instance of a general rule
worth stating on its own:

> **Every per-slot parameter crossfades with the audio.** Any difference
> between two adjacent slots on any of the seven per-slot parameters —
> Voice level, Texture, Spread, Pitch, Stereo width, Low cut, Denoise —
> animates during the transition between them.

This is a feature. It's why v2 exists in the first place. But it means
setting different values across slots produces motion during transitions,
whether you wanted that motion or not.

**When you want the motion:** capture two spectra, set them to different
Pitch values, and Sweep between them — you get a natural pitch morph. Same
with Texture (voice-to-wash across the transition), Spread, Stereo width,
etc. This is a whole expressive dimension the original Morpher didn't
have.

**When you don't:** if you set slot 1 to Pitch −5 and slot 2 to Pitch 0
thinking each would just play at its own pitch (as v1's global Pitch would
have), the transition between them will bend pitch continuously across
the crossfade. To keep pitch constant across slots, set the parameter to
the same value on every slot that participates in the morph.

**The pattern for eliminating unwanted motion**, in general: pick the
value you want for the whole morph, then set it on every unmuted slot
via **Capture slot** → adjust → next → adjust. It is the same walk you'd
do for silent-slot configuration — because silent-slot configuration is
one specific case of this rule.

## What's global vs per-slot

Since the split doesn't always match intuition, here is the plain list.

**Per slot** (each slot carries its own; morph crossfades them):
- Capture point, Slot linger, Slot crossfade, Slot mute
- Voice level, Texture, Spread, Pitch, Stereo width, Low cut, Denoise

**Global** (one setting for the whole plugin):
- Input level, Audition, Morph, Auto-morph, Wash grain
- All Drift and Ramp settings — including the targets. Drift acts on the
  global *effective* value of a target, not per-slot: drift Texture up 20
  and every slot's Texture gets shifted 20, not just the currently-audible
  one.

The most common surprise: **Wash grain is global.** You cannot have one
slot with a grainy 5 ms texture and another with a glassy 300 ms texture
on the same instance. If you want that, use two instances of the plugin
on separate tracks with different Wash grain settings, feeding the same
or different captures.

## Focused mode is a monitor, not a preview

**Focused slot** (`Audition` = Focused slot) plays exactly the slot you
point at, at 100%, ignoring the auto-morph sequencer entirely. Which
means it also ignores:

- **Slot mute** — a focused muted slot still plays. Focused is "let me
  hear this exact slot no matter what."
- **Auto-morph timing** — no linger, no crossfade, no transitions. The
  slot just plays continuously for as long as you leave Focused on.
- **The morph slider** — manual position along the slot line is
  irrelevant in Focused mode.

Focused is for auditioning and rendering individual slots as stems. If you
want to preview what your morph will sound like, switch **Audition** to
**Morph** and let auto-morph run.

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
- **What is safe to automate:** Texture, Morph, Pitch, Spread, the levels, Stereo width, Low cut, Denoise, and Wash grain. Capture point and Capture are not (they re-analyze, or are momentary). Nine of the automatable ones — Texture, Spread, Pitch, Stereo width, Low cut, Voice level, Denoise, Morph and Input level — can also be moved hands-free from *inside* the plugin with **Drift** (endless wander) and **Ramp** (a one-time slow ride), no automation lane needed.
- **Source-agnostic.** It freezes anything — synths, field recordings, strings, cymbals, even a whole mix via a track send. The wash texturizes any source.
- **Captures persist** across save and reopen (the raw audio is stored in the project; both engines rebuild on load).
- **Transport must be moving** for it to sound — it is a generator. Loop the transport, or arm the track and monitor.

See [`docs/spectral-vowel-morpher.md`](spectral-vowel-morpher.md) for deeper design notes and advanced techniques.

---

*Spectral Vowel Morpher is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

