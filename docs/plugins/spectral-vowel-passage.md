# Spectral Vowel Passage

**Designed by Rozaya — Developed with Claude (Anthropic)**

> **Spectral Vowel Passage is a sibling of
> [Spectral Vowel Morpher](spectral-vowel-morpher.md)** — the same capture-and-
> resynthesis engine, but a different instrument to play. Morpher is a *field you
> sit inside*: one continuous morph that never quite settles. Passage is a *route
> with stops*: you set each captured moment's timing deliberately — how it fades
> in, how long it holds, how it hands over — and the piece walks through them.
> Both are worth keeping installed, and the shared "Spectral Vowel" prefix keeps
> them together in the plugin list. *(Passage began as "Morpher v2"; the per-slot
> timing redesign made it its own instrument, so it earned its own name.)*
>
> What Passage does that Morpher doesn't:
>
> **1. Each slot owns its whole leg of time, in seconds.** The single global
> *Auto-morph time* is gone. Every slot carries its own **fade in**, **hold**,
> and **fade out**, an optional **gap** of silence after it, and a **crossfade
> into next** toggle — so the cycle is simply its slots' legs added up. Adding a
> slot makes the cycle longer instead of squeezing the existing steps, and — the
> point of it — every slot's timing can differ from every other's. Each number
> is the seconds you hear: four seconds of hold means typing four, four seconds
> of silence means a gap of four. Nothing about one slot's timing lives on a
> different slot.
>
> **2. Every setting that describes a capture is per slot.** Voice level,
> Texture, Spread, Pitch, Stereo width, Low cut and Denoise all belong to the
> selected slot rather than being one global setting flattening every capture.
> The morph crossfades them along with the spectra, so moving between two slots
> moves between their settings too. Input level stays global (the dry signal is
> the track's, not a capture's), and so does Wash grain (it rebuilds a window
> rather than scaling a value, so it cannot be crossfaded per grain).
>
> **3. The synthesis FFT is sized to the grain** rather than fixed at maximum — a
> CPU saving on wash-heavy projects. (This was *meant* to also cure the
> short-grain crackle; by ear it didn't, so that stays a known limitation — see
> the note under **Wash grain**. The sizing is kept for the CPU win.)
>
> Controls are also grouped by what they belong to rather than by when they were
> added, so everything owned by the selected slot — **Capture point**, **Capture
> average**, the timing controls, and the seven above — is reached through
> **Capture slot**.

---

## Overview

A capture-based instrument. You play audio into it, capture a few moments, and it resynthesizes them — as a recognizable voice, an evolving wash, or any blend between — and morphs between the captured moments. It is built for sustaining and looping vocal material, but it freezes any source.

Unlike Sustain Looper (which loops a region of a *loaded* file), Passage feeds on **live audio playing into it** — drop a WAV on the track or send another track in, play it, and hit Capture when you hear a moment you want. Captures persist across project save and reopen.

It is a generator: it only sounds with the transport rolling (or the track armed and monitored).

---

## Signal Architecture

Every capture is analyzed two ways at once, and the **Texture** knob crossfades between them.

### Voice (harmonic) — Texture 0

Detects the pitch and rebuilds the sound from 64 harmonics placed at the exact fundamental. Phase-coherent, so it keeps the vowel and pitch cleanly — a sustained vowel or choir. It reproduces only the *harmonic* part, so it has no breath or air, and it only makes sense on clearly pitched material.

### Wash (spectral) — Texture 100

PaulStretch-style phase randomization: it keeps the magnitude spectrum and discards phase, turning every partial into a narrow noise band. Smooth, breathy, evolving — it turns any source into texture. On a voice it deliberately reads as softly "denoised" (that is the operation, not a fault) — ideal for pads and beds.

### Capture

**Your captures can be taken out as WAV files, and files can be put back in** — see [Getting your captures out](../getting-your-captures-out.md) for a step-by-step walkthrough. Useful for reusing a good vowel elsewhere, backing captures up on their own, or listing what is in your eight slots without auditioning each one.

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

**Capture average** `1 to 6, default 1` — *per slot*
*How much* of the grab the wash analysis looks at, as against Capture point's
*where*. At 1 it reads a single instant — the original behaviour, and right for
natural voice. Turn it up and it reads several overlapping slices around the
capture point and averages them.

**This is the fix for the wobble on already-processed material.** A single
analysis frame freezes that instant's fine detail and the wash then replays the
same frozen detail on every grain, hundreds of times a second. On a natural
sustained vowel that's harmless — one instant looks much like the next, so the
frozen frame is a fair description of the sound. On something that has *already*
been through a spectral process the fine detail is irregular, and hearing the
identical irregularity repeat is what you register as a wobble. Averaging lets
the roughness cancel out while the actual shape of the sound, which every frame
agrees on, survives.

So: **capturing a render that has been through Passage (or any spectral
processing) before? Raise this until the wobble goes, and no further.** Two or
three is usually enough.

Raising **Spread** also eases the wobble, and until now that was the only lever —
but Spread only blurs the frozen detail rather than removing it, and blurs
everything else along with it. With Capture average doing the job properly,
Spread is free to go back to whatever you actually want it at for character, and
you get the definition back that you were spending on it.

The cost is time-smear: the frames cover a stretch rather than an instant, so a
vowel that *moves* gets blended across that stretch. That's why it's a dial and
not automatic — on moving material, keep it low. Like Capture point it re-analyzes
live, so step it by ear; and like Capture point it's set-once, not an automation
target. **Each slot keeps its own**, because it describes the material in *that*
slot — one slot holding natural voice can sit at 1 while its neighbour holding a
re-spectralised wash sits at 4.

Nothing needs re-capturing to benefit. The stored raw audio is what gets
re-analyzed, so every capture you already have — in this project or any older one
— can simply be re-read at a higher frame count.

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

**Known limitation: short Wash grain still produces evenly-spaced crackling.**
Passage sizes the synthesis FFT to the grain (instead of always
using the maximum size), on the theory that shorter grains were firing
constant-cost FFTs many times per second and that was what caused the
dropouts. That theory was tested by ear and the crackle *did not go away*.
Which means either the CPU-per-grain wasn't the bottleneck, or something
else about grain boundaries at short lengths is producing the clicks. Real
diagnosis is a next-session task; do not trust "short grain works now" —
if you need short grain, expect crackle until this is properly fixed. The
FFT-sizing change itself is kept because it does reduce CPU on wash-heavy
projects even if it did not solve the crackle problem.

The Spread control is separately faster than before regardless — the
running-sum optimisation is mathematically equivalent to the original, and
verified numerically. That is a real perf win. But it does not touch the
short-grain crackle.

**Spread (Hz)** `0 to 150, default 0`
Blurs the spectrum across frequency — diffuses a narrow capture into a wider noise bed.

*Per slot.* Belongs to whichever **Capture slot** is selected; the morph crossfades it between slots along with the sound itself.

**Pitch (semitones)** `-96 to +96, default 0`

Drift and Ramp are applied ON TOP of this and are **not** clipped back to the
slider range, so modulation can carry the pitch beyond +/-96. Previously it was
pinned there, which meant a wide Drift flattened against the edge: the
modulation carried on moving while the sound stopped changing.
Transposes both engines, tape-style (formants move with pitch), so one capture covers a range of "body sizes."

*Per slot — and the one value that does **not** blend.* It belongs to whichever **Capture slot** is selected, like the others, but it is never averaged between two slots. Averaging two pitches doesn't produce an in-between sound, it produces a glide. Both engines transpose each slot at its own pitch — the voice sounds each slot's harmonics at that slot's tuning, and the wash transposes each slot's spectrum before the two are blended — so the morph crossfades in level only, with no sliding between differently-tuned slots.

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
Crossfades across the captured slots. Pitch-preserving in both engines — each slot is sounded at its own pitch, so there is no portamento glide however far apart two slots are tuned.

**Auto-morph** `Off / Sweep / Glide once / Shuffle, default Off`
In-plugin morph motion — Sweep = endless back-and-forth; Glide once = slot 1 to the last, one time; Shuffle = like Sweep, but in *random* order: it glides through all your captured slots visiting each once, then reshuffles and goes again. Every mode is timed the same way: each step lasts the full leg of the slot it is leaving — its fade in, hold, fade out, and any gap — so a pass is however long its slots' legs add up to, just a different order (and a different order each time you open the project). Shuffle only moves *where* the morph is sitting (it never introduces a new pitch), so it is exactly as clash-safe as moving the Morph slider by hand — safe on chordal captures at different pitches. *(This mode was called "Drift" before; renamed to Shuffle so it isn't confused with the suite-wide Drift feature below, which is a different thing.)*

**Fixed: a click at slot changes.** Up to and including the build shipped
2026-07-25, every step from one slot to the next put a small click in the voice
engine — in all three Auto-morph modes, and when the Morph slider was dragged
past a slot boundary by hand. The voice runs two banks of oscillators and hands
the outgoing slot from one bank to the other at the step; the banks were at
unrelated points in their cycles, so the waveform jumped. Its loudness depended
on where the two banks happened to be, which is why it popped on some changes
and not others and felt random rather than "once per slot". The handover now
carries the phase across, so the sound runs straight through the step. Nothing
about it is adjustable and no setting worked around it — if you have an older
render with ticks at the slot changes, that was this.

**It was voice-engine only.** The voice is scaled by an equal-power crossfade
against Texture, so the click tracked how much voice was in the mix: full at
**Texture 0**, and *absent* at **Texture 100**, where the voice contributes
nothing at all. A pure-wash patch never had it; anything with voice in it did.

All five timing controls belong to whichever **Capture slot** is selected: pick
a slot, set its timing, pick the next, set that one. Each slot remembers its own
and they save with the project. Every value is the seconds you hear — no
arithmetic, no allowance for a fade bleeding in from a neighbour, nothing about
one slot's timing living on another slot.

**Slot fade in (sec)** `0 to 300, default 1` — *per slot*
How long this slot takes to rise from silence when it arrives. You hear it at
the very start of a pass, and any time a slot arrives *out of silence* — after a
**gap**, or after the previous slot faded out with its crossfade **Off**. When
the previous slot **crossfades into** this one instead, the crossfade has already
raised it to full, so its own fade-in is skipped (nothing fades in twice, and the
boundary stays click-safe either way). Fade in 2 = a two-second rise.

**Slot hold (sec)** `0 to 300, default 4` — *per slot*
How long the slot stays up at full, alone, once it has arrived. **The number you
type is the number of seconds.** Hold 4 on every slot and each holds four
seconds; hold 4 on one and 8 on another and their holds differ, which is what an
uneven cycle (like a real breath) needs. Hold 0 means no steady part — the slot
rises and immediately begins to fall.

**Slot fade out (sec)** `0 to 300, default 1` — *per slot*
How long the slot takes to fall at the end of its hold. What the fall *is*
depends on the crossfade toggle below:

- **Crossfade into next = On** — the fade-out *is* the **crossfade** into the
  next slot: this one falls as the next rises, the two overlapping. (The gap is
  unused in this mode.)
- **Crossfade into next = Off** — the fade-out falls all the way to **silence**;
  then the gap (if any) plays; then the next slot fades in on its own.

Fade out 0 is a hard edge — an instant switch to the next slot with crossfade on,
or a hard cut to silence with it off (which can click on sharp-edged captures;
soft-edged captures like breath cut cleanly).

**Fade in shape (all slots)** / **Fade out shape (all slots)** `Linear / Cosine / Logarithmic / Exponential, default Cosine` — *global*
The *curve* of the leg fades, as distinct from their length above. **Cosine** (the
default) is a smooth, eased fade at both ends — a slot rises out of silence and
settles back into it with no hard edge, which is usually what you want for placed,
breathing material. **Linear** is a straight-line ramp — the plugin's original
behaviour, and the one that can feel abrupt right at the top of a fade-in or the
bottom of a fade-out; reach for it only if you want that edge. **Logarithmic**
rises fast then eases; **Exponential** starts slow then accelerates. These are the
same four shapes, by the same names, that the sweeping filters use for their
Attack/Release.

The shape is **global** — one curve for every slot's fades, a house style rather
than a per-moment setting (the fade *times* stay per slot). **Fade out shape**
governs the crossfade-**Off** fall to silence; with crossfade **On** the handover
is the spectral crossfade, which these curves don't touch.

**Older projects need migrating.** These two shapes were added as sliders 10 and
11, and **Capture average** later as slider 4 — and REAPER restores plugin values
by slider *position*, so a project saved before either one opens with everything
above the insert shifted along: Wash grain's 150 arriving as Voice level,
Auto-morph landing on Audition, and so on. Your captures are safe regardless —
they're stored separately and have no idea what a slider number is — so it is
only the control values that move. Run `tools/passage_migrate_sliders.py` over any
project saved before this build; it applies whichever shifts that project still
needs, setting the fade shapes to **Linear** and Capture average to **1**, which
is what those projects actually were. Change them afterwards if you want the new
defaults. It keeps a `.pre-slider-migrate-bak` copy and is safe to run twice.

**Slot gap after (sec)** `0 to 300, default 0` — *per slot*
Seconds of silence after this slot, before the next one begins. **This is how you
place silence now** — the quiet lives between the slots, where it is, so you no
longer capture a silent slot to make a pause. Four seconds of quiet means typing
four.

The gap only does something when **crossfade into next is Off** — a crossfade
leaves no room for silence in the middle, because the two slots are overlapping.
With crossfade on, the gap is ignored.

**Slot crossfade into next** `Off / On, default On` — *per slot*
How this slot hands over to the next.

- **On** (default) — the fades overlap: this slot's fade-out is a crossfade, the
  next slot rising as this one falls. The classic morph, and how the plugin has
  always behaved.
- **Off** — a clean handover: this slot fades out to silence, the gap (if any)
  plays, then the next slot fades in on its own.

### The four ways a handover can sound

The toggle and the gap together give four combinations, and each does something:

- **Crossfade On, no gap** — classic morph. The next rises as this one falls.
- **Crossfade Off, no gap** — clean handover. This one fades out, the next fades
  in, no overlap and no silence between.
- **Crossfade Off, gap set** — hard silence. This one fades out, that many
  seconds of nothing, then the next fades in. Silence with edges.
- **Crossfade On, gap set** — the gap does nothing (a crossfade leaves no gap to
  fill). Turn the crossfade Off to make a gap audible.

### How a slot's leg adds up

A slot's whole leg is its parts in order:

- **Crossfade on:** `fade in + hold + fade out`. The fade-in only counts on the
  first slot of a pass (or a slot arrived-at out of silence) — mid-morph, the
  crossfade from the slot before already raised it, so what you hear per slot is
  `hold + fade out`.
- **Crossfade off:** `fade in + hold + fade out + gap`. The fade-in counts every
  time, because every slot arrives from the silence the slot before left.

A cycle is just its slots' legs added together. There is no global morph time to
divide — each slot's leg is exactly the seconds you set on it. To hear slot 3
alone for 8 seconds and then blend over 2 seconds into slot 4: set slot 3's
`hold 8, fade out 2, crossfade On`. Slot 4's timing is entirely slot 4's own.

**Slot mute (Off / On)** `default Off`
When **On**, this slot is skipped by Sweep, Glide, and Shuffle. The morph
crossfades from the previous unmuted slot directly to the next unmuted slot,
with no fade to or from this one in between.

*Per slot*, edited the same way as everything else in this group: select the
slot via **Capture slot**, then toggle the mute.

**Focused slot mode ignores mute.** If you point at a muted slot in Focused
mode, you still hear it — Focused is "audition this specific slot no matter
what." So mute affects the *morph sequence*, not what a slot IS.

Its main use now is trimming which captures a pass visits: you've banked five
slots but only want a morph across three of them today, so mute the other two.

**Placing silence between two sounds no longer needs a muted silence capture** —
set the earlier slot's crossfade **Off** and give it a **gap**. That is what
gaps are for, and it is why the old "capture silence, then mute it so the morph
skips it" dance is gone. Mute is for skipping a slot; the gap is for making
quiet.

Edge cases: if every slot is muted, the morph is silent. If exactly one is
active, it plays solo (no morph, since there's nothing to morph between).
Both fall out of the sequencer naturally.

## A gotcha with silent (or otherwise "empty-feeling") slots

> **First, the easy way out:** most reasons to capture silence are gone —
> to put a pause between two sounds, set the earlier slot's crossfade **Off**
> and give it a **gap**. The rest of this section only matters if you
> *deliberately* capture silence or near-silence as a slot of its own (for its
> own texture, or a held placeholder). If you use gaps for your quiet, skip
> ahead.

**Every per-slot setting belongs to the slot as captured** — including Stereo
width, Denoise, Pitch, Spread, and the rest. This is usually what you want:
each capture carries its own colour. But it means **a silent slot inherits
whatever the sliders were set to at the moment you captured it**, and if those
differ from your audio slots, the morph will crossfade the *settings* right
along with the audio — producing sweeps that seem to come from nowhere.

The classic version of this is: you capture your in-breath and out-breath at
one Stereo width, then capture a quiet slot between them at a different Stereo
width without meaning to. The plugin then dutifully sweeps width from mono to
wide as the morph passes through the silent slot, and it sounds like some hidden
LFO is animating stereo. It isn't. It's just the per-slot width doing exactly
what it says it does. (A **gap** avoids this entirely — silence between slots
carries no settings to sweep.)

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

In Morpher there is one global Stereo width, so this
couldn't happen — every slot shares the same width, and adding a silent
capture costs you nothing extra to configure. In Passage, per-slot control is the
feature, but the cost is that empty-feeling slots (silence, near-silence,
placeholder captures) need their non-audio parameters set deliberately, or
you'll hear those parameters *animating* on you during transitions.

### How the next sound gets *in* — it's the arriving slot's own fade-in now

Worth naming, because it works differently from Morpher. Under that older model
the fade into a slot belonged to the slot *before* it. Now **each slot owns its
own fade-in**,
so how a sound appears out of quiet is set right there on that sound's slot, not
on whatever came before.

Concretely, for sound → gap → sound: the first slot's **fade out** decides how it
melts away, its **gap** is the length of quiet, and the second slot's **fade in**
decides how it appears. If an arrival feels abrupt — a sudden appearance even
though the level is rising from zero — the transition window is too short for the
ear to register as "arriving": lengthen that slot's **fade in**. No hunting on a
neighbour; the control is on the slot you're hearing. (Also check **Fade in shape**
is on **Cosine**, not Linear — the eased curve softens an arrival on its own, and a
straight-line ramp is the most likely thing making a fade-in feel abrupt.)

### The auto-gain needs extra time coming out of silence

If you hear a slight bloom, level spike, or the audio "arriving louder
than it should" when a slot fades in out of a gap (or a silent slot), that is
the plugin's slow auto-gain smoother catching up. During silence, the auto-gain
sits at whatever amplification it had before the quiet began (it can't measure
loudness from a signal that has none, so it freezes). The moment audio starts
fading back in, the amplification is still cranked up from before, and the fresh
audio gets multiplied by it before the smoother has time to catch back down.

The fix is one of:

- **Give the arriving slot about a second more fade-in.** The extra time gives
  the auto-gain room to settle before the audio is fully in. (Adding to the gap
  ahead of it doesn't help — nothing is playing to settle the gain during silence;
  it's the *rise* that needs to be longer.)
- **Match the level of the slots around the quiet more carefully** — the bloom
  is worst when the arriving slot is much quieter than the peak-time auto-gain
  expected. Louder captures on either side smooth this.

In practice, a second more fade-in is the simple fix and it barely changes the
cycle timing at all — a good default reflex whenever you hear a fade-in that
feels too eager.

## The per-slot rule (and what it means for every parameter, not just silence)

The silent-slot section above is the sharpest instance of a general rule
worth stating on its own:

> **Every per-slot parameter crossfades with the audio.** Any difference
> between two adjacent slots on any of the seven per-slot parameters —
> Voice level, Texture, Spread, Pitch, Stereo width, Low cut, Denoise —
> animates during the transition between them.

This is a feature. It's a good part of why Passage exists at all. But it means
setting different values across slots produces motion during transitions,
whether you wanted that motion or not.

**When you want the motion:** capture two spectra, set them to different
Pitch values, and Sweep between them — you get a natural pitch morph. Same
with Texture (voice-to-wash across the transition), Spread, Stereo width,
etc. This is a whole expressive dimension the original Morpher didn't
have.

**When you don't:** if you set slot 1 to Pitch −5 and slot 2 to Pitch 0
thinking each would just play at its own pitch (as Morpher's global Pitch would
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

**Per slot** (each slot carries its own):
- Capture point; the five timing controls (Slot fade in, Slot hold, Slot fade
  out, Slot gap after, Slot crossfade into next); Slot mute
- Voice level, Texture, Spread, Pitch, Stereo width, Low cut, Denoise
  *(these seven — the sound of a slot — are the ones the morph crossfades
  between slots; the timing controls and mute shape the sequence rather than
  blend)*

**Global** (one setting for the whole plugin):
- Input level, Audition, Morph, Auto-morph, Wash grain, Fade in shape, Fade out shape
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
- **Auto-morph timing** — no fade in, hold, fade out, gap or crossfade; no
  transitions at all. The slot just plays continuously, at full, for as long as
  you leave Focused on.
- **The morph slider** — manual position along the slot line is
  irrelevant in Focused mode.

Focused is for auditioning and rendering individual slots as stems. If you
want to preview what your morph will sound like, switch **Audition** to
**Morph** and let auto-morph run.

## Overtone — one voice, two notes

Overtone singing (Tuvan khoomei and its relatives) sounds like a singer holding a
drone and whistling a separate melody over it. There is no second voice. The
singer holds **one** fundamental, and narrows the vocal tract into a very sharp
resonance parked on **one harmonic of that same note**, so that partial stands
clear of its neighbours and the ear hears it as a pitch in its own right. The
melody is that resonance walking up and down the harmonic series — which is
exactly why overtone melodies only ever land on harmonic-series intervals.

Passage's voice engine is already a bank of 64 partials sitting at exact
multiples of the detected fundamental, so it can do this directly. These three
controls are the tract.

> **These work at both ends of Texture, and sound different at each.** On the
> voice they isolate one exact partial — a clean, near-pure tone. On the wash,
> where phase has already been randomised into narrow noise bands, the same
> window leaves a pitched *band*: breathier and airier, but still a definite
> note. Both are driven by the same controls and the same detected fundamental,
> so a Texture blend moves between the two characters rather than between two
> different overtones.

**Overtone harmonic** `0 to 64, default 0 (off)` — *per slot*
Which partial to bring out. 0 is off. 1 is the fundamental itself (no effect
worth having — that's the drone). The usable range for a singing overtone is
roughly **6 to 14**; below that the partials are too far apart to read as a
melody, above it they get faint and crowded. Consecutive numbers are consecutive
overtone "notes", so a melody is just a sequence of small whole numbers — 8, 9,
10, 12 — and the machine works out every frequency.

**Overtone lift (dB the chosen harmonic rises by)** `0 to 48, default 24` — *per slot*
How hard the resonance lifts the chosen partial. This is a **peak**, which is what
a narrowed vocal tract actually is: the chosen harmonic rises above where it sat,
and the rest of the voice stays roughly put.

**It still can never get louder.** After the lift, the whole harmonic bank is
scaled so the summed power is unchanged — so the effect is a redistribution, not a
boost, and on real material (which rolls off steeply) it comes out slightly
quieter than before rather than louder.

That does mean the rest of the voice recedes a little, and more so the harder you
push, because there is a fixed power budget to move around:

| Lift | chosen partial | everything else |
|---|---|---|
| 6 dB | +5.8 dB | −0.2 dB |
| 12 dB | +11.1 dB | −0.9 dB |
| 18 dB | +15.1 dB | −2.9 dB |
| 24 dB | +17.1 dB | −6.9 dB |
| 36 dB | +18.0 dB | −18.0 dB |

**Around 12–20 dB is the sweet spot** — the overtone separates into its own note
while the drone barely moves. Past roughly 30 dB you stop gaining separation (the
lift plateaus near +18 dB) and start losing the drone instead, which is a whistle
rather than overtone singing. Harmonic 1 is never lifted at any setting — it *is*
the drone half of "two notes".

**Overtone width (harmonics either side)** `0.5 to 4, default 1` — *all slots*
How sharp the resonance is. **1** is the classic narrow whistle. Higher values
let neighbouring partials come along, which is broader, more vowel-like and less
synthetic — closer to the softer end of overtone technique.

### Per slot, because that is how a singer works

**Harmonic and depth belong to the slot. Width doesn't.** A singer has one
throat, and how sharply it resonates is their technique — not something they
re-choose per note. But *which* harmonic sits under that resonance, and how
tightly it closes, are set by the shape of the mouth — and a captured moment is a
mouth shape. So each slot carries its own overtone, and the passage walks through
them.

That also means each slot can use a harmonic its own material supports. A bright,
pressed capture will hold harmonic 12; a softer one hasn't got the upper partials
and wants 7 or 8. Before, one number had to serve every slot.

**Moving between two slots slides the overtone.** This is the one place Passage
deliberately *does* blend something it refuses to blend for Pitch. Averaging two
pitches drags both slots off their own tuning — that's a glide, not a crossfade,
and it was a bug. But the overtone resonance is a physical mouth shape, and moving
between two vowels passes through every shape in between, so the emphasis really
does slide from partial to partial. That slide is the "wah" you hear between
overtone notes. A morph from a slot on harmonic 8 to one on harmonic 12 walks
through 9, 10 and 11 on the way.

**A slot with no overtone doesn't drag the note down with it.** If the next slot
is set to 0, the harmonic *stays where it is* and the depth fades to nothing — the
resonance relaxes and the overtone dissolves, which is what a singer does when
they stop. (Sliding the harmonic toward zero instead would sweep the emphasis down
the entire series on its way out: a descending whistle nobody asked for.)

### Making it sing

**The fundamental never drops, at any depth.** It's the drone half of "two notes
at once"; suppress it and you have a whistle rather than overtone singing. It's
hard-wired, not a setting.

**Texture picks the character, not whether it works.** Near 0 you get the pure
tone; near 100 you get the breathy band. Both are usable — the wash version is
closer to a whistle heard through air, which suits a bed better than a clean
partial does.

**Your capture has to be bright.** The effect isolates a partial that must
already be there. A soft, breathy vowel has almost nothing in the upper harmonics
to find; a bright, buzzy, pressed tone has plenty. If the overtone sounds thin or
absent, the source is usually why.

**Overtone harmonic is a Drift and Ramp target, and that's the melody.** Set
Drift on it with a small up/down and a slow period and the overtone wanders the
series on its own — the mouse-free version of drawing an automation lane.
Fractional positions are deliberate: at 7.5 the emphasis sits evenly across
partials 7 and 8 and hands over between them, which is what a real singer's
resonance does as it sweeps. Ramp walks it once, slowly, from wherever it starts
— an overtone rising through the series across a whole piece.

Because the partials are defined off the detected fundamental, the overtone
tracks everything the voice does for free — pitch, Pitch drift, the per-slot
tunings, the morph. It cannot go out of tune with the drone, because it *is* the
drone.

### Drift (in-plugin automation)

Drift makes a parameter **wander on its own** — the suite's stand-in for drawing an automation envelope, so you get slow evolving motion without a mouse or an automation lane. Pick a target, set how far it wanders up and down and how long a full wander takes, and it moves by itself while the transport rolls. **Every target drifts at once** — the selector only chooses which one the four sliders below are editing right now; the others keep drifting with whatever you last set them to.

**Drift target** `Texture / Spread / Pitch / Stereo width / Low cut / Voice level / Denoise / Morph / Input level / Overtone harmonic / Slot fade in / Slot hold / Slot fade out / Slot gap, default Texture`
Which parameter the Drift sliders below are editing.

**Drift is per slot, like everything else here.** The Drift sliders show the settings for *the selected Capture slot's* selected target — so slot 1's Texture can wander slowly while slot 4's barely moves, and each has its own period and shape. Two selectors reach it: **Capture slot** picks which slot, **Drift target** picks which parameter of it. Everything you configure keeps running in the background regardless of what's on screen.

**Two targets are global and ignore the slot selector: Morph and Input level.** Morph decides *which slot is playing*, so a per-slot Morph drift would be circular; Input level is the dry track signal, which isn't a capture's property. Those two show the same settings whatever slot you have selected.

**During a morph, the drift crossfades along with the value it modifies.** If slot 3's Low cut is wandering one way and slot 4's another, moving between them blends the two — the wander doesn't jump when the slot changes. **Pitch is the exception, and deliberately**: pitch is never blended between slots (averaging two frequencies is a glide, not a blend), so each slot is voiced at its own pitch with its own drift on top.

**The four slot-timing targets behave differently from the rest, on purpose.** Every other target drifts continuously — the value moves under your ear while you listen. A *duration* can't do that: if the hold time changed while a hold was already running, the finish line would move mid-leg, stretching a pause out from under you or ending a fade that was still going. So a slot-timing target is **sampled once, at the moment its leg begins**, and held for that whole leg. The cycle comes out a little different every time round instead of wobbling inside itself.

Which is what makes a breath out of slots possible: **fade in is the inhale, hold is the top pause, fade out is the exhale, gap is the bottom pause.** Give each a small drift and the breathing stops being metronomic. Results are clamped at zero, so a drift larger than the setting itself shortens the leg to nothing rather than inverting it.

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

**Ramp target** `Texture / Spread / Pitch / Stereo width / Low cut / Voice level / Denoise / Morph / Input level / Overtone harmonic / Slot fade in / Slot hold / Slot fade out / Slot gap, default Texture`
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

See [`spectral-vowel-morpher.md`](spectral-vowel-morpher.md) — its sibling — for the shared engine's deeper design notes and advanced techniques.

---

*Spectral Vowel Passage is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

