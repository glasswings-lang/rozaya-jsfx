# Spectral Vowel Morpher

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

A capture-based instrument. You play audio into it, capture a few moments, and it resynthesizes them — as a recognizable voice, an evolving wash, or any blend between — and morphs between the captured moments. It is built for sustaining and looping vocal material, but it freezes any source.

Unlike Sustain Looper (which loops a region of a *loaded* file), the Morpher feeds on **live audio playing into it** — drop a WAV on the track or send another track in, play it, and hit Capture when you hear a moment you want. Captures persist across project save and reopen.

It is a generator: it only sounds with the transport rolling (or the track armed and monitored).

---


**Fixed 2026-07-27: a click when the morph crossed between slots.** In every
build before this, stepping from one slot to the next — a Drift step, or the
Morph slider crossing a slot boundary — put a small click in the voice engine.
The voice runs two banks of oscillators and hands the outgoing slot from one to
the other at the crossing; the banks were at unrelated points in their cycles, so
the waveform jumped. Its loudness depended on where the two banks happened to be,
which is why it popped on some crossings and not others and felt random rather
than "once per slot". The handover now carries the phase across. Nothing about it
was adjustable and no setting worked around it — if you have an older render with
ticks where the morph moves between slots, that was this. The voice is scaled by an equal-power crossfade against Texture, so the click tracked how much voice was in the mix: full at **Texture 0**, and *absent* at **Texture 100**, where the voice contributes nothing at all. A pure-wash patch never had it; anything with voice in it did. (Diagnosed and
ear-tested in the sibling plugin, [Passage](spectral-vowel-passage.md).)

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

**Capture now** `Off / Capture now`
Grab the current moment into the selected slot. It captures *whatever audio is reaching the track at that instant* — so if you fire it while nothing is playing (transport stopped, or no source feeding the track), you'll bank an **empty slot**, and the morph will fade to silence whenever it reaches that slot.

**Capture now disarms itself after each capture** — it returns to Off the moment it fires, so you can never leave it armed by accident. A reloaded project always opens with it parked Off and can't silently re-fire over one of your slots on load. (If a slot ever goes unexpectedly silent and the morph fades out when it reaches it, the cause was almost always Capture left armed; this behavior is what prevents it.)

**Capture point** `0 to 100, default 0` — *per slot*
*Where* in the captured ~0.68 s to analyze — 0 = earliest, 100 = the instant you pressed. Defaults to earliest because, by the time you react and press, the sound is already a beat in the past; the press-moment tends to catch the breathy release. Re-analyzes live, so sweep it by ear to land on the vowel. Set-once — not an automation target (it re-runs the full analysis).

**Each slot keeps its own Capture point.** When you capture a slot it remembers where you scrubbed to, and scrubbing one slot no longer re-tunes the others. Switching **Capture slot** shows that slot's saved point on the slider, so you can bank several captures and tune each one to its own vowel independently. Saved points persist across reload. (Older projects made before this change open with every slot on the single point they shared; re-scrub any slot to give it its own.)

**Capture average (frames)** `1 to 6, default 1` — *one setting for all eight slots*
How many analysis frames the **wash** spectrum is averaged over. At 1 you get the original single-frame analysis. Turn it up if a slot wobbles.

A single frame freezes that one frame's per-bin scatter and replays it on every grain. On a natural sustained voice, successive frames look alike and you'll never hear it — but on material that has *already* been through a spectral process, the scatter is irregular and its repetition becomes an audible wobble sitting centre-image. Averaging several frames lets the scatter cancel while the real spectral shape survives. The cost is time-smear: the frames span a stretch of the grab, so a vowel that *moves* gets blended across the average. That's why it's a dial and not automatic — **turn it up until the wobble goes, and no further.**

Changing it re-analyzes every captured slot, so expect one brief glitch when you stop moving it (it's debounced — it recomputes once when the slider settles, not on every step). It only touches the wash; the voice engine resynthesizes exact harmonics with continuous phase and has no scatter to freeze. And because captures are stored as raw audio and re-analyzed on load, this reaches captures you banked long ago — no re-capture, no re-render.

> **This is one global setting, unlike Passage, where it's per slot.** Morpher is a field you sit inside, with one setting across the morph — the same reason **Overtone** is global here. The tradeoff is that a slot that only needed 1 takes the same time-smear as the slot that needed 6; in a morph whose slots blur into one another, that costs much less than it would on Passage's separate stops. *(It was briefly per slot here after being ported over from Passage. If you open a project from that build, all eight slots flatten to whatever the slider itself shows.)*

**Audition** `Focused slot / Morph, default Morph`
*Focused slot* plays exactly the Capture-slot, ignoring Morph (so you can hear each grab as you build it). *Morph* plays the morph blend.

**Morph (% across captured slots)** `0 to 100, default 0`
Crossfades across the captured slots. Pitch-preserving — each slot plays at its own pitch, so there is no portamento glide.

**Auto-morph** `Off / Sweep / Glide once / Shuffle, default Off`
In-plugin morph motion — Sweep = endless back-and-forth; Glide once = slot 1 to the last, one time; Shuffle = like Sweep, but in *random* order: it glides through all your captured slots visiting each once, then reshuffles and goes again. One full pass takes one Auto-morph time, so each slot gets an equal share of it — same timing and same gentle crossfades as Sweep, just shuffled (and a different order each time you open the project). Shuffle only moves *where* the morph is sitting (it never introduces a new pitch), so it is exactly as clash-safe as moving the Morph slider by hand — safe on chordal captures at different pitches. *(This mode was called "Drift" before; renamed to Shuffle so it isn't confused with the suite-wide Drift feature below, which is a different thing.)*

**Sync to host** `Off / On, default Off`
Whether **Auto-morph time** below is counted in seconds or in beats of the project tempo.

Auto-morph time is a *duration*, and a duration's two honest units are seconds and beats — so this is one switch rather than a mode list. There is no ratio menu and no note-value grid: a morph every **5** beats is exactly as reachable as one every 4, which is the point in a suite about layers slipping against each other.

Flipping it doesn't change what you hear. The value converts at the current tempo, so a 20-second morph becomes however many beats that is and keeps running at the same speed — only the unit you type in changes. With it On, a tempo change carries the morph with it.

Shown only when Auto-morph is running, alongside the time it governs.

**Auto-morph time (sec / beats when synced)** `0.01 to 1000, default 20`
How fast the motion moves. For Sweep/Glide it's the duration of one pass; for Shuffle it's the duration of one full pass through *all* your slots (each slot gets an equal fraction). Lower it for quick wandering, raise it for a long, slow motion.

**Texture (% wash)** `0 to 100, default 50`
Crossfades 0 = Voice (harmonic, keeps the vowel) to 100 = Wash (spectral, breathy bed). The middle layers both — vowel plus air.

**Wash grain (ms)** `5 to 680, default 150`
The wash's grain length: short = rougher and grainier, long = glassier and smoother. Affects only the wash; cheap and safe to automate.

**Spread (Hz)** `0 to 150, default 0`
Blurs the spectrum across frequency — diffuses a narrow capture into a wider noise bed.

**Pitch (semitones)** `-96 to +96, default 0`

Drift and Ramp are applied ON TOP of this and are **not** clipped back to the
slider range, so modulation can carry the pitch beyond +/-96. Previously it was
pinned there, which meant a wide Drift flattened against the edge: the
modulation carried on moving while the sound stopped changing.
Transposes both engines, tape-style (formants move with pitch), so one capture covers a range of "body sizes."

**Stereo width (%)** `0 to 100, default 50`
Spreads the stereo image of *both* engines. In the wash it decorrelates L/R phase (mono-safe). In the voice it runs a slightly-detuned copy on the right channel (up to ~14 cents at 100), so the two sides beat slowly against each other — real width plus a shimmer that softens the robotic edge of the pure harmonics. At 0 the voice is exactly mono (unchanged from older projects). The detuned voice is only computed when the voice is actually audible (Texture below full wash), so living on the wash costs nothing.

**Denoise (%)** `0 to 100, default 0`
Spectral subtraction — raise to thin toward the strongest partials (more tonal, more gated).

**Low cut (Hz)** `0 to 500, default 0`
Removes low rumble from the resynth. It is applied to the captured spectrum *before* the pitch shift, so it **moves with Pitch** — pitch a capture down an octave and its low cut comes down with it. That is how it has always behaved and it is left alone so existing projects sound the same; High cut, below, deliberately works the other way.

**High cut (Hz)** `200 to 20000, default 20000 (off)`
The top end of the same pair — takes the fizz and hiss off the resynth. Two things make it more than a mirror of Low cut, and both matter if you use Layers:

- It sits at an **absolute** frequency, applied *after* the pitch shift. It stays where you set it while Pitch and any Layers transpose underneath it. That is what lets an octave-up Layer be tamed at all; a cut that slid up with the layer would follow the fizz instead of catching it.
- It shapes the **voice** as well as the wash. Partials fade out as they cross it (over the top fifth of the cut, so a Drifting cut sweeps rather than steps), which makes the voice engine *cheaper* the further down you bring it — the partials above the cut stop being computed at all.

At 20000 it is off, and off is exactly as if the control were not there.

## Overtone — one voice, two notes

Overtone singing (Tuvan khoomei and its relatives) sounds like a singer holding a drone and whistling a separate melody over it. There is no second voice. The singer holds **one** fundamental and narrows the vocal tract into a very sharp resonance parked on **one harmonic of that same note**, so that partial stands clear of its neighbours and the ear hears it as a pitch in its own right. The melody is that resonance walking up and down the harmonic series — which is why overtone melodies only ever land on harmonic-series intervals.

Morpher's voice engine is already a bank of 64 partials sitting at exact multiples of the detected fundamental, so it can do this directly. These three controls are the tract.

> **These work at both ends of Texture, and sound different at each.** On the voice they isolate one exact partial — a clean, near-pure tone. On the wash, where phase has already been randomized into narrow noise bands, the same window leaves a pitched *band*: breathier and airier, but still a definite note. Both run off the same controls and the same detected fundamental, so a Texture blend moves between the two characters rather than between two different overtones.

**Overtone harmonic** `0 to 64, default 0 (off)` — *global*
Which partial to bring out. 0 is off. 1 is the fundamental itself (no effect worth having — that's the drone). The usable range for a singing overtone is roughly **6 to 14**; below that the partials are too far apart to read as a melody, above it they get faint and crowded. Consecutive numbers are consecutive overtone "notes", so a melody is just a sequence of small whole numbers — 8, 9, 10, 12 — and the machine works out every frequency. It's a Drift and Ramp target, so that melody can play itself. Fractional values are deliberate: at 7.5 the emphasis hands over between partials 7 and 8, the way a real sweep does.

**Overtone lift (dB the chosen harmonic rises by)** `0 to 48, default 24` — *global*
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

**Overtone width (harmonics either side)** `0.5 to 4, default 1` — *global*
How sharp the resonance is. **1** is the classic narrow whistle. Higher values let neighbouring partials come along, which is broader, more vowel-like and less synthetic — closer to the softer end of overtone technique.

> **All three are global here, where Passage puts harmonic and depth per slot.** Passage models a singer moving through a route of separate notes; Morpher is one continuous field, so the tract holds one shape across the whole morph.

### Layers (octave stacking)

Extra copies of **the whole instrument** — voice and wash both — playing at a fixed interval from the main pitch, at the same time, from the same instance. Sixteen entries: twelve fixed intervals — four octaves each way, plus fifths and fourths — three free-interval Custom layers, and the Original itself, all behind **seven sliders**.

The point is the *lock*. Two instances of the plugin on Shuffle wander independently: one lands on your "ah" while the other is on an "oo" a fifth away, and the octaves you wanted arrive as a clash. A Layer is not another instance — it is the same capture, at the same morph position, in the same crossfade, an octave away. Every slot change, every Drift, every Shuffle step happens to all of them together, so a stack stays consonant no matter where the morph wanders. Layers ride Pitch as *offsets* from it, so pitching (or Drifting, or Ramping) the main Pitch transposes the whole stack as one.

They work the way Drift target and Capture slot do: **every layer sounds at once**, and the selector only chooses which one the sliders below are editing. The selector is a view, never a mute.

**Layer** `4, 3, 2, 1 octaves down / a fifth down / a fourth down / Original (unison) / a fourth up / a fifth up / 1, 2, 3, 4 octaves up / Custom 1-3, default Original`
Which layer you are setting. For the twelve named entries the interval is decided by the name — there is nothing to convert and nothing else to set but the level.

The list is a **pitch ladder** — four octaves down at the top, four octaves up at the bottom, and the three Custom slots trailing it because an arbitrary interval has no place in a ladder. **Original (unison)** sits in the middle, between the fourth down and the fourth up, which is exactly where your ear puts it.

The Original is the morph itself — the thing every layer stacks around. It takes Active, Level and Solo exactly like a layer does, so you can solo it to hear what the stack is built on, mute it to hear only the octaves, or pull it down and let an octave lead. It has no interval, because it *is* the interval everything else is measured from. Putting it at either *end* of the list was the same mistake twice — an entry out of musical order, just from opposite directions. Its position cost an index shift on saved projects; see the migration note at the bottom of this page.

Its level defaults to **0 dB**, not off — it's the sound.

**Layer active** `Inactive / Active, default Active`
Silences the selected layer **without losing its level**. That's the difference between this and a level of −60: −60 means "this layer is silent because that's the level I want," Inactive means "silence it and give it back to me later." Flip it off, flip it back on, and the dB you tuned is exactly where you left it. Costs the same nothing as −60 while it's off — the layer's DSP is skipped either way.

Drift and Ramp move the *level*, never this switch, so arming drift on a layer you've muted can't bring it back without you.

**Layer level (dB)** `-60 to 0, default -60 (off)`
How loud the selected layer sits under the main voice.

**The number you set is the number you get.** A level of −12 puts that layer 12 dB under the main voice and changes *nothing else*. There is no auto-balancing and no compensation moving under your hand while you set the next one — set four octaves in any order and the first three still sound the way you left them.

The cost of that honesty is that levels **add**: eleven layers at 0 dB is twelve times the amplitude, and it will clip if you let it. That is the trade, and it is the right way round — a plugin quietly re-mixing you means every adjustment is a chase against a soundscape you are also moving.

**−60 is truly off** and costs no CPU at all: the layer's DSP is skipped, not muted. Every layer's level is also its own Drift and Ramp target, which is where this gets interesting — octaves that swell in and out on their own periods, hands-free, while you do nothing.

**Layer solo** `Off / Solo, default Off`
Audition one layer alone. Anything soloed silences everything that isn't — including the Original, which is itself soloable, so "solo the thing the others stack around" works the way you'd expect. Solo more than one to hear those together.

Solo deliberately **overrides Inactive**: you solo something in order to hear it, and a solo that returns silence because the layer was also muted is a bad thirty seconds when you're working by ear. A level of −60 is still silent though, because that's a level, not a mute.

While soloing, the wash's per-grain auto-gain brings a quiet layer up to a normal listening level rather than leaving it at its mix level — which is what you want for auditioning, but means solo is not a way to judge relative balance.

**Layer pitch (semitones, Custom layers)** `-96 to +96` — *shown only on a Custom layer*
The interval by hand, for anything the selector doesn't name — a seventh, six octaves, or a fractional offset for a slow beating unison. Same eight-octave range as Pitch itself.

**Layer overtone harmonic (-1 = follow the global)** `-1 to 64, default -1` — *per layer*
Which harmonic **this** layer lifts, when you want it to differ from the global **Overtone harmonic**.

Left at −1 the layer follows the global setting, which is what every layer did before this control existed — so nothing you have already built changes.

Why it is worth having: the global overtone applies by harmonic *index*, so with it set to 8 the lift lands on the 8th partial of every layer at once — which in a stack of octaves means 8×f0 in the Original, 4×f0 an octave down, 16×f0 an octave up. Consonant, because the layers are octaves and fifths, but there was no way to say *overtone on the lead, none on the drone*, which is what a throat-singing patch actually wants. The harmonic is the melodic half of the effect (it is the Drift and Ramp target — that is how an overtone melody gets played hands-free), so it is the half that goes per layer. **Overtone lift** and **width** stay global, because they are character rather than melody.

> **This currently shapes the voice, not the wash.** The wash's overtone is applied to one shared spectrum before the layers are summed into it, so at the wash end every layer still follows the global **Overtone harmonic**. That is a limit of what has been built, not a cost decision — layers are cheap on the wash (they are extra reads inside a grain that was being built anyway, not extra transforms), so per-layer overtone belongs there too and is planned. At Texture 0 the per-layer harmonic is the whole effect today.

**Layer harmonics (0 = full)** `0 to 64, default 0`
Caps how many partials *this one layer* synthesises on the voice engine, independent of the main voice's own detail. 0 means uncapped — the layer gets whatever the source has, exactly as before this control existed, so no saved project changes sound on load. A plain count, nothing to convert: set it lower and the layer gets simpler; the plugin never lets it exceed what the source actually has, so raising it past that point does nothing further. A background/support layer usually doesn't need the same partial count as the layer you're actually listening to, so this is where to spend a CPU cut before touching High cut or Stereo width, which affect every layer and the main voice at once.

#### Cost, and how deep you can go

Near enough free on the wash — one extra spectrum read per bin, inside a grain that was being built anyway, with no second FFT. Layer harmonics doesn't apply there; wash cost doesn't scale with partial count.

On the voice each raised layer is another 64 partials, but the **upward** layers get cheaper the higher they go, because their partials cross Nyquist (or your High cut) and stop being computed at all. On a capture around 200 Hz, an octave up is 60 partials, two up is 30, three up is 15, four up is 7. The downward layers are the expensive ones — each is a full 64. Four octaves down all at once is real CPU; the same four upward is close to free. Layer harmonics is the direct lever on that: pull a downward layer's count down by hand instead of waiting for High cut to do it for every layer at once.

Four octaves each way is the usable span of a voice capture: four down is at the floor of hearing, four up is past where a captured harmonic series has much content left. Anything wider is a Custom layer — **and depth is free, but watch your meters.** The Custom range goes to eight octaves either way because nothing in the engine cares. Past about five octaves down, though, a layer is below hearing: inaudible, but still eating headroom and moving speaker cones. A subsonic layer you can't hear is still on the meter.

**Input level (dry, dB)** `-60 to +12, default 0`
The source passed straight through. −60 = silent.

**Output level (dB, everything but the dry input)** `-60 to +12, default 0`
The master level for everything the plugin *makes* — the voice, the wash, and every layer. Not the voice engine's own level, despite what it was called until now: it sits after the voice/wash crossfade and after every layer has been summed in, so it moves the whole instrument together. The dry input is the one thing it doesn't touch; that has its own **Input level**.

*(Renamed from “Voice level”. Same slider, same behaviour, same saved values — the name was simply describing one part of what it did.)*

### Drift (in-plugin automation)

Drift makes a parameter **wander on its own** — the suite's stand-in for drawing an automation envelope, so you get slow evolving motion without a mouse or an automation lane. Pick a target, set how far it wanders up and down and how long a full wander takes, and it moves by itself while the transport rolls. **Every target drifts at once** — the selector only chooses which one the four sliders below are editing right now; the others keep drifting with whatever you last set them to.

**Drift target** `Texture / Spread / Pitch / Stereo width / Low cut / Output level / Overtone harmonic / High cut / the sixteen layer levels in ladder order, default Texture`
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

Ramp is a **one-time slow ride** of a parameter — you set where to move it and over how long, arm it, and it glides there once and holds. It's the one-directional partner to Drift (Drift wanders back and forth forever; Ramp makes a single slow arc), and it's built for the sleep wind-down: e.g. **ride Texture from voice to wash over 20 minutes** as someone drifts off, or **Output level down to silence over 30 minutes** for a hands-free fade — no automation lane needed. *(This is the same feature the other plugins call "Ramp." It's just called "Ramp" here because this plugin has no rate/speed to ramp — it rides a value instead.)*

Like Drift, every target rides in parallel; the selector chooses which one the sliders are editing. Ramp and Drift stack on the same parameter (base value + Drift wander + Ramp ride).

**Ramp target** `Texture / Spread / Pitch / Stereo width / Low cut / Output level / Overtone harmonic / High cut / the sixteen layer levels in ladder order, default Texture`
Which parameter the Ramp sliders below are editing (same targets as Drift).

**Ramp by** `-300 to +300, units match the target, default 0`
How far to move the parameter, and which direction — in that parameter's own units (Texture 0–100, Pitch semitones, Low cut Hz…). Negative goes down, positive up. **0 means this target doesn't ramp**, so arming Ramp with everything at 0 safely does nothing.

**Ramp duration (minutes)** `0 to 60, default 0`
How long the ride takes. 0 = this target doesn't ramp. Set it to, say, 20 and the parameter takes twenty minutes to travel its full `by` amount, then holds.

**Ramp engage** `Off / On, default Off`
Arms every configured target at once. While On, each rides its own duration from where it is; flip Off and they freeze in place (flip back On and they resume). The ride starts fresh from the current values each time the transport begins playing. You can aim several targets at once (Texture *and* Output level *and* Low cut, each over its own time) and one Engage winds them all down together.

**Ramp start delay (minutes)** `0 to 60, default 0`
Wait this many minutes after arming before the ride begins — e.g. "let me settle for 10 minutes, *then* start winding down."

---

---

## Usage Notes

- **The capture workflow.** Put audio on the track, Input level up and Output level down so you hear the source. When you hear the moment, hit Capture (set Capture slot first to bank several). Then pull Input down, Voice up, set Texture, and Morph between slots. Sweep Capture point by ear to land exactly on the moment — and because each slot keeps its own point, you can go slot by slot and tune every capture to its own vowel without disturbing the ones you already set.
- **The voice end needs pitched material.** Texture 0 only sings on clearly pitched sources (a sustained vowel, organ, bowed note). On unpitched material it produces a tone — use the wash end (or the middle) there instead.
- **Vowel + breath is the middle.** The pure voice end has no breath; the pure wash end has breath but de-voices. A blend around Texture 30–50 gives the vowel plus air.
- **What is safe to automate:** Texture, Morph, Pitch, Spread, the levels (including every layer level), Stereo width, Low cut, High cut, Denoise, and Wash grain. Capture point and Capture are not (they re-analyze, or are momentary). Twenty-four of the automatable ones — Texture, Spread, Pitch, Stereo width, Low cut, High cut, Output level, Overtone harmonic, all fifteen layer levels and the Original's — can also be moved hands-free from *inside* the plugin with **Drift** (endless wander) and **Ramp** (a one-time slow ride), no automation lane needed.
- **Source-agnostic.** It freezes anything — synths, field recordings, strings, cymbals, even a whole mix via a track send. The wash texturizes any source.
- **Captures persist** across save and reopen (the raw audio is stored in the project; both engines rebuild on load).
- **Transport must be moving** for it to sound — it is a generator. Loop the transport, or arm the track and monitor.

See [`docs/spectral-vowel-morpher.md`](spectral-vowel-morpher.md) for deeper design notes and advanced techniques.

---

*Spectral Vowel Morpher is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---



## Migrating projects across the 2026-09 reorder

The controls were reordered so that things that belong together sit together.
**Capture average** rejoined the Capture group it had been twenty-four sliders
away from; **High cut** rejoined **Low cut**; Drift and Ramp stopped splitting the
sound controls in half and moved to the end, where every other plugin in the suite
keeps them; the two global levels moved to the end of the sound section, after
everything they scale. **Capture slot** is numbered 1-8 now, matching how the slots
are actually spoken about. Two controls were added *in their proper places* rather
than bolted onto the end — **Sync to host** beside the Auto-morph time it governs,
and **Layer overtone harmonic** with the other layer controls. 38 sliders became 40.

REAPER restores plugin values by slider POSITION, so an existing project needs its
slider line rewritten or every value above the first change lands on the wrong
control. **Your captures are not affected** — they live in the `@serialize` blob,
which has no notion of slider numbering, along with every per-layer and Drift/Ramp
bank. The whole break is one line of text per instance.

```
python tools/morpher_migrate_layout.py PROJECT.RPP --dry-run
python tools/morpher_migrate_layout.py PROJECT.RPP
```

It writes a `.pre-layout-bak` beside each project and refuses to overwrite one, so
the backup is also the record of what has already been done. Running it twice is
safe: it counts the values and skips anything already at 40. Projects saved by
older builds with fewer controls migrate too — the missing ones are filled with the
defaults REAPER was giving them.

> **One judgement call it makes, and reports.** `Capture slot` was itself
> re-indexed once before (1-8 became 0-7 in July 2026), so a small number of very
> old projects cannot be dated from their contents alone. The script uses the blob
> version and the file's save date to decide, and **names every instance where it
> chose to leave the value alone**. If it ever guesses wrong the consequence is
> that the Capture group opens pointed at the next slot along — nothing audible
> rides on it.

---

## Migrating projects across the layer-order change

The Layer selector is now a pitch ladder with the **Original** at unison, in the
middle. It previously listed the Original at one end or the other, and the Custom
slots first — so every index in the Layer selector and in the Drift/Ramp target
lists has moved.

The plugin migrates **its own `@serialize` blob** on load — per-layer levels,
mutes, solos and every Drift/Ramp bank rotate themselves, and older blobs
(7700004, 7700005, 7700006) each walk forward through the chain. Nothing there
needs you.

What it can't reach is the **slider line**: `slider33`, `slider17` and `slider23`
hold indices into those same lists and live in the project file. Without a
migration the banks are correct but the selector and the two target pickers point
one entry low. Run:

```bash
python tools/morpher_migrate_layer_order.py PROJECT.RPP
```

It touches only instances whose blob says 7700005, 7700006 or 7700007 — read from the
project, not guessed — writes a `.pre-layer-order-bak` copy first, and refuses to
clobber an existing one. **Close the project in REAPER first**, or REAPER writes
its in-memory copy back over yours. Projects older than the layer feature have
nothing to move and are skipped.
