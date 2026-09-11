# Melody Phase

**Designed by Rozaya — Developed with Claude (Anthropic)**

## Overview

A step-sequencer melody synth, sibling to Polyrhythm Phase. Up to 8 voices participate in a sequence; each voice plays a single note (a configurable number of semitones from the root) for its own *Next voice in* duration, then hands off to the next active voice. Each voice has its own *Note duration* duration controlling how long its note actually sounds — when "Note duration" is longer than "Next voice in," the voice's release continues in parallel with the next voice's attack (overlap / phrasing). When "Note duration" is shorter than "Next voice in," there's a rest before the next voice enters. When they're equal, the handoff is clean and sequential.

Inactive voices are skipped in the sequence entirely. To insert a rest in the sequence (a silent step), leave a voice Active and set its "Note duration" to 0 — the voice contributes silence for its "Next voice in" duration, then hands off, with no click on entry or exit.

Beyond the core sequencer:

- **Per-voice pan** with four modes (Tremolo, Increment, Spread, Spread Reversed) — Spread is especially useful for melody since each active voice gets a fixed position across the stereo field, making the line easy to track spatially.
- **Glide / portamento** — pitch slides between voices over a configurable duration. Independent of all other timing.
- **Legato glide** — when on, the whole sequence becomes one continuous tone whose pitch slides between voices, with no attack / release ceremony at the boundaries. The pan smoother also slows to match the glide time so pitch and pan transition as one coherent slide.

The waveform list (10 options), envelope shapes, tuning math, binaural beat, and pan section are all carried over directly from Polyrhythm Phase. Both per-voice timing sliders are expressed in cycles of the global rate, so rhythmic relationships line up — V1 set to 2 cycles, V2 set to 1 cycle, V3 set to 0.5 cycles will line up cleanly against the same rate.

## Signal Architecture

Each voice runs two oscillators (one for L, one for R). The R oscillator's frequency is offset from the L oscillator's by the binaural beat value (in Hz). When binaural beat is 0, L and R are identical and the voice sums to mono.

A sequencer index tracks which voice is currently "in its step." When that voice's *Next voice in* elapses, the index advances to the next active voice and triggers its envelope attack. The outgoing voice's envelope keeps running through its own (longer or shorter) *Note duration* independently — that's where overlap comes from. Up to 8 voices can be in non-silent states simultaneously during overlapping phrasing.

The envelope is a four-segment state machine: attack → sustain → release → silent. Each segment respects the voice's *Note duration*: Attack % and Release % set how much of the note duration is attack and release; sustain fills the middle. If Attack% + Release% would exceed 100%, both are scaled proportionally to fit. The output amplitude passes through a one-pole exponential smoother (~3ms time constant) before reaching the oscillator, so even instantaneous envelope transitions (attack% = 0 or release% = 0) come out click-free.

When Glide time > 0, each new voice's frequency starts at the previous voice's target and slides toward its own target via a one-pole smoother. Multiple voices can be in different sliding states simultaneously during overlap.

When Legato glide is on, the sustain → release transition is suppressed — each voice rings continuously from its trigger until the sequencer's next hand-off silences it via inheritance. The new voice inherits the previous voice's envelope value, oscillator phase, and pan position, so amplitude, waveform, and stereo position are all literally continuous across the boundary — only the pitch slides via glide. The first note still attacks normally; the last note (when Loop = Off and the sequence ends) releases normally. The pan smoother slows to match the glide time so pitch and pan transition together.

When Loop is on, the sequence wraps from the last active voice back to the first. When off, the sequence plays through once and stops.

## Parameters

### Global

**Rate value** `0.001 – 1000` · **Rate mode** `BPM / Seconds / Hz / Every N beats / N per beat` (default Seconds)

Two controls, side by side: a number, and what the number means. That is the same
rate block every other plugin in the suite has, and Melody joined it on
2026-09-06.

**Seconds** — seconds per cycle. With Rate value 1 (the default) one cycle is one
second, so the per-voice *Next voice in* and *Note duration* numbers behave as
raw seconds. Set a voice to 2 and it plays for 2 seconds.
**BPM** — beats per minute. Rate value becomes the tempo and the per-voice
numbers become beats.
**Hz** — cycles per second. Rate value is the cycle frequency; 0.05 Hz is one
cycle every 20 seconds, which is the useful end for slow ambient pacing.
**Every N beats** — follow the project tempo, one cycle every N beats. Bigger is
slower: `4` is one cycle per bar in 4/4, `1` is one per beat.
**N per beat** — follow the project tempo, N cycles per beat. Bigger is faster:
`3` is a triplet feel, `8` is eight notes a beat.

The last two are the same thing said from opposite ends, and both are here on
purpose. They are reciprocals, so with only the slow one you would have to type
`0.125` to get eight notes a beat — arithmetic, which is exactly what this suite
exists to remove. Pick whichever end of your music you already have a number for.

### Following the project tempo

> **Melody used to do this with three separate controls** — a `Sync to host`
> switch, a `Host sync target` selector and an `Every N beats` slider. They were
> retired on 2026-09-06 and replaced by the two host entries in Rate mode above.
> Saved projects were migrated: a synced instance's beat count moved into Rate
> value with Rate mode set to `Every N beats`, so nothing changed speed.
>
> The selector existed so you could aim the sync at either the sequencer or the
> pan. The real gap was simply that the pan had no rate mode of its own; it now
> has one (see **Pan rate mode**), so both rates can sync independently and
> nothing has to reach across.

In the three free modes each instance holds its own absolute rate, and nothing in
the plugin knows that two instances are related. That's fine until you want to
change the speed of a whole arrangement: nudging every instance by hand changes
the *relationships* between them, not just the pace, and layers that used to nest
start scattering.

Put Rate mode into `Every N beats` or `N per beat` and the project tempo drives
the instance instead. Move the tempo and every synced instance moves with it, in
proportion.

This is **not** quantising. The beat count is continuous, so unlocked
relationships are as available as locked ones — and they survive a tempo change
too:

| Layer | Rate value in `Every N beats` | Cycles/min at tempo 40 | at tempo 45 |
|---|---|---|---|
| Fast | 1 | 40 | 45 |
| Mid | 2 | 20 | 22.5 |
| Slow | 4 | 10 | 11.25 |

…nests forever, while `1 / 1.618 / 4` never resolves — and keeps not resolving in
the same way at any tempo. That is the whole reason the beat count is a free
number rather than a menu: *every 5 beats of a 4/4 bar* is exactly as reachable
as *every 4*, and this suite is phase music.

Tempo changes take effect live, including mid-playback. Voice and envelope
proportions are untouched; the melody just runs faster or slower.

> **Start Delay is counted in cycles of the rate**, so when synced it is cycles of
> the tempo-scaled rate — a delay of 8 stays 8 cycles when you move the tempo,
> rather than drifting against the notes.

**Starting partway into the song lands on the right note (fixed 2026-09-11).**
When synced, pressing play at bar 40 — or jumping there while playing — starts on
the voice that belongs at bar 40, not on voice 1. The note restarts from its
attack rather than joining halfway. This was meant to work before, but the
placement was undone two audio buffers after every play press. The transport
stopped is unchanged: Melody sounds straight away, exactly as before.

One thing the fix corrected along the way: with **Play for** / **Rest for** set, a
synced sequence played from the top used to fit one note fewer into its first play
period (Play for 8 gave 7). It now gives 8, the same as an unsynced sequence at the
same speed. In the library this changes the first rest of instance 9 in
`simple-sequence` and `simple-sequence-check`; everything else played from the top
is bit-identical.


**Waveform** `Sine / Triangle / Saw / Golden TS / Golden SG / Golden GS / Bell / Wavefold / Half-sine / Phi-cascade / Phi Triangle / Phi Sine / Square / Pulse`
Same set as Polyrhythm Phase — see that plugin's Waveform section for descriptions, including the back-compat note on the Golden / Phi family. Note that Half-sine sounds an octave higher than the others at the same note + Center Octave setting (full-wave-rectified spectrum has no fundamental).

**Pulse width (%, 50 = square)** `1 – 99, step 0.1, default 25`
Duty cycle for the **Pulse** waveform — the fraction of each cycle the wave spends high before snapping low. 50 is a square wave and sounds identical to the Square slot. Narrower values get thinner and more nasal; wider values mirror the same character back the other way, so 25 and 75 sound alike. The default of 25 is deliberately off-square so Pulse sounds distinct from Square the moment you select it. The range stops short of 0 and 100, which would be silence and DC respectively.

Only meaningful when Waveform is set to **Pulse**, and hidden from the parameter list entirely on every other waveform.

**Tuning reference (Hz)** `20 – 2000, default 440`
Frequency of A4. Standard concert pitch is 440.

**Fine tune unit (for every voice)** `Hz / Semitones / Cents, default Cents`
What every voice's *Fine tune* is counted in — one unit for all eight, not one per
voice. Change it and all eight fine tunes are read in the new unit. Each voice's
fine tune says `(in fine tune units)` so you can tell, from the voice itself,
where its unit is set. Renamed 2026-09-10; the old label said neither.

**Pitch mode** `Hz / Semitones / Cents, default Semitones`
What every voice's *Pitch* value means. **Semitones:** the MIDI note number, 60
is middle C, and each voice's Note name follows it both ways. **Hz:** the
frequency itself. **Cents:** the MIDI note times 100, so 6950 is a quarter tone
above A4.

**Transpose (semitones)** `-12 – 12` · **Octave shift** `-4 – 4`
Move every voice together. The intervals between voices stay the same. At 0 and 0
the note names on the voices are literally true.

**Loop** `Off / On`
When on, the sequence wraps from the last active voice back to the first. When off, the sequence plays one full pass and stops.

**Master Gain dB** `-60 – 0`
Output level for the whole plugin.

**Binaural Beat Hz** `0 – 100`
Hz offset added to the right-channel oscillator only. 0 disables the effect and the plugin sums to mono. Same shape as Polyrhythm Phase's binaural beat.

**Attack % of Note duration** `0 – 100`
What fraction of each voice's *Note duration* is taken up by the attack ramp.

**Release % of Note duration** `0 – 100`
What fraction of each voice's *Note duration* is taken up by the release ramp. If Attack% + Release% exceeds 100%, both are scaled proportionally to fit the note duration.

**Attack Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve of the attack ramp. Cosine is the smoothest perceptually; Linear is the most "musical-instrument-like."

**Release Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve of the release ramp.

**Sequence Length** `All Active / 1 / 2 / 3 / 4 / 5 / 6 / 7 / 8`
How many voice slots participate. "All Active" walks all 8 slots, skipping any with Active = Off. A numeric setting truncates the sequence to the first N voice slots (still skipping any inactive within that range). Useful for shortening a sequence without having to flip Active toggles.

### Pan

Mirrors Polyrhythm Phase's pan section. When enabled, each voice gets independently-positioned L and R amplitudes — the binaural beat is preserved across the pan because each channel keeps its own oscillator. Pan Mode picks one of four behaviors.

**Pan Enabled** `Off / On`
Toggles the whole pan group. When off, voices sum straight to mono (and the sub-sliders below are hidden in Reaper). Default Off.

**Pan Mode** `Tremolo / Increment / Spread / Spread Reversed / Alternating / Alternating (Flipped) / Distributed / Distributed (Flipped) / Distributed (Ping-pong) / Converging / Converging (Ping-pong) / Diverging / Diverging (Ping-pong)` (default Spread)
- **Tremolo** — each voice's pan position oscillates over time at Pan Base Rate. All voices share the same rate.
- **Increment** — each voice's pan rate is Pan Base Rate + (voice index × Pan Increment), so V1, V2, V3… all pan at slightly different rates and drift in and out of phase.
- **Spread** — voices get static pan positions ranked across the stereo field. V1 sits at one end, V8 at the other, the rest spread evenly between. Active voices only; inactive ones are skipped in the ranking. **Most useful for melodies** — each note in the sequence lives in a distinct spatial position, which makes the line easy to follow.
- **Spread Reversed** — same as Spread but flipped. Pairs nicely with another instance set to Spread for compositional stereo width.

**Per-cycle pan modes** (`Alternating` through `Alternating every 8`)

Twelve modes that move the pan **one step per note** rather than on an LFO of their own. This is the same set, under the same names, that Full Feature Tremolo, the Resonant Sweeping Filter and the Sweep Dwell Filter already have — only the tick differs.

- **Alternating** — hard left, hard right, left, right.
- **Alternating (Flipped)** — the same, starting on the other side. Two instances set to opposite flips move against each other.
- **Distributed** — walks evenly across the stereo field over `Cycle Steps` positions, then jumps back.
- **Distributed (Flipped)** — the same walk, right to left.
- **Distributed (Ping-pong)** — walks across and back rather than jumping.
- **Converging** — starts hard left, then closes inward toward centre in alternating steps.
- **Converging (Ping-pong)** — the same, bouncing rather than restarting.
- **Diverging** — starts at centre and opens outward in alternating steps.
- **Diverging (Ping-pong)** — the same, bouncing.
- **Alternating every 2 / every 4 / every 8** — the same flip, but it holds each side for 2, 4 or 8 notes before crossing. This is the one to reach for when the notes themselves are fast: at 205 BPM a flip on every note is far too quick to feel bilateral, where holding for four gives a slow sway that still lands exactly on the boundaries.

**Why use these instead of a separate tremolo plugin panning alongside?** Because they cannot drift. A second plugin panning in time with this one has its own clock, no shared start, and no way to land exactly on a note transition — so it slides out of alignment and stays there. These move *because a note started*, so there is nothing to hand-match and nothing to fall out of step with.

**Cycle Steps** `2–32, default 8`
How many positions the Distributed / Converging / Diverging walks step through before the pattern repeats. This is the length of a *temporal* pattern and has nothing to do with how many voices you have running.

It matters more than it sounds: **at 2 positions every one of those modes collapses into Alternating** — a walk across two places is a flip. Eight gives Distributed a genuine sweep across the field and Converging a real closing-in. Alternating and the every-N modes ignore it, being two-sided by definition, and it hides for them.

Use **Pan Spread %** for width — at 100% Alternating is hard left/right, around 30-50% it is a sway rather than a flip, which is usually what you want for long listening. Set **Pan Glide ms** to 0 for a hard switch, or leave it at 10 ms for a short sweep between sides.
**Pan Glide ms** `0-100 ms, default 10`
How long the pan takes to travel between positions. **0 is an instant switch** — the sound cuts from one side to the other with no slide, which is what bilateral alternation is supposed to be. Anything above 0 sweeps instead. The default of 10 ms is what this plugin used to do with no way to change it; Full Feature Tremolo and both sweeping filters have had this control all along.



**Pan Spread %** `0 – 100`
How wide the pan moves. 100 = full stereo. 0 = collapses to center (effectively defeats pan).

**Pan base rate** `0.001 – 1000` (Tremolo / Increment modes only)
Pan LFO rate. Hidden when pan is off or when Pan Mode is Spread / Spread Reversed.

**Pan rate mode** `BPM / Seconds / Hz / Every N beats / N per beat` (default BPM)
What the pan rate above is measured in — the pan's **own** unit, with the same
five entries as the sequencer's Rate mode. Added 2026-09-06.

Until then the pan had no mode of its own and simply borrowed the sequencer's,
which meant the pan could not follow the tempo unless the sequencer did too.
That is exactly what the old `Host sync target` selector was working around. Now
the pan can sit in `Every N beats` while the sequencer runs free in Seconds, or
the reverse, and neither reaches across to the other.

Existing projects are unaffected: the control defaults to BPM, and every saved
instance takes that default.

**Pan Increment per Voice** `-1000 – 1000` (Increment mode only)
How much each successive voice's pan rate increases over the previous voice's. Hidden in other modes.

### Glide / portamento

These sit with the envelope controls above rather than with Pan, because glide is part of the shape of the movement from one note to the next.

**Glide time (seconds; 0 = off)** `0 – 5`
When > 0, each new voice's pitch starts at the previous voice's target frequency and slides to its own target over this many seconds. 0 = no glide; voices jump directly to their pitch. Independent of all other timing — set Glide to 0.05 and notes will slide quickly into pitch from wherever the last one was, regardless of *Next voice in* or *Note duration*.

**Legato glide** `Off / On`
- **Off** (default) — each voice has its own attack and release. Glide bends the pitch *during* each note; you hear each voice as a distinct envelope event at the hand-off (attack ramp on the new note, release ramp on the old). Good for plucky / articulated melodies where each note should feel separately spoken.
- **On** — the whole sequence becomes one continuous tone whose pitch slides between voices. The first note attacks normally; every subsequent hand-off skips the attack and inherits both the envelope value and the oscillator phase from the previous voice; pitch slides via glide. The previous voice's "Note duration" is effectively ignored — voices ring continuously until the next one takes over (which silences the previous one). The last note (when Loop = Off and the sequence ends) releases normally. **Rests still work** — a voice with Note duration = 0 doesn't trigger a hand-off, so the previously-ringing voice keeps holding through the rest's step time (which is what "continuous tone with no rest" sounds like in this mode — if you want actual silences in Legato mode, use Active = Off to skip a voice slot entirely).

Good for legato / flowing melodies where you want one bending tone instead of articulated steps. Set Glide time > 0 to actually hear the pitch slide; with Glide = 0 + Legato On, the pitch jumps between targets but there's still no attack ceremony.

### Per Voice (V1–V8)

**Vn Note** `C-1 – G9`
This voice's note, by name. Shown in Semitones mode, where picking a name sets the Pitch and moving the Pitch moves the name.

**Vn Pitch (Hz / semitones / cents)** `0 – 20000`
This voice's pitch, in whatever *Pitch mode* says. Transpose and Octave shift move it along with every other voice.

**Vn Fine tune (in fine tune units)** `-1000 – 1000, default 0`
Nudges this voice off its note, in whatever *Fine tune unit (for every voice)* says. In Cents, 50 is a quarter tone.

**Vn Next voice in (cycles)** `0.01 – 16`
How long until the sequencer hands off from this voice to the next active one, in cycles of the global rate. Controls *sequence timing* — when does V[n+1] start? Vn's own note may continue ringing past this handoff (overlap) or end before it (rest), depending on the "Note duration" slider below.

**Vn Note duration (cycles; 0 = silent)** `0 – 16`
How long this voice's note actually sounds, in cycles. Controls *sound timing* — independent from sequence timing. The relationship between this and "Next voice in" is what gives the plugin its phrasing range:
- **Note duration < Next voice in** → there's silence between Vn ending and the next voice entering (rest in the sequence).
- **Note duration = Next voice in** → clean sequential handoff, no overlap, no rest.
- **Note duration > Next voice in** → Vn's release continues while the next voice plays (overlap / phrasing).
- **Note duration = 0** → Vn is a silent step (rest) of duration "Next voice in." Silent on entry and exit, no click.

**Vn Gain dB** `-60 – 6`
Per-voice level.

**Vn Active** `Off / On`
Off = this voice is skipped in the sequence entirely (not just silent — the sequence pretends it doesn't exist). On = voice participates per the Sequence Length rule above.

**Vn Solo (heard even when Active is off)** `Off / On, default Off` *(new 2026-09-10)*
When any voice is soloed, only soloed voices make sound. The others **keep their
turns in silence**, so the timing of the pattern does not move. Solo more than one
to hear those together.

A soloed voice is heard **even if its Active is off** — Rozaya: *"Sollowing things
that are switched off should bring them on anyway, that's the point of sollow."*
A switched-off voice is not part of the sequence, so soloing one **joins it to the
pattern while it is soloed**: it takes its own turn, and the loop is that much
longer until you turn Solo off again. A voice's level is untouched by soloing.

### Start Delay

**Start Delay** `0–1000, default 0`

How long the plugin sits silent at the start of playback before the sequencer begins. Units match Rate Mode: BPM mode counts cycles of the global Rate Value (so 4 with Rate Value = 60 BPM = 4 beats = 4 seconds), Seconds mode is literal seconds, Hz mode counts cycles of Rate Value. 0 disables the delay entirely.

During the delay the sequencer state stays frozen — when the delay elapses, the sequence begins cleanly from V1 (or the first active voice) rather than mid-step. Re-arms on every transport stop/start.

**Fixed 2026-09-06 — a delayed instance used to come in slightly early.** Melody
waits a moment at the start of playback for REAPER to finish handing over its
settings, and only then starts the sequence. The Start delay counter did not
wait: it began ticking immediately, so a delayed instance burned part of its
delay during a pause the undelayed ones were still sitting in, and entered early
by however long that pause lasted. About 21 ms at a 512-sample buffer — a small
fraction of a beat, present from the first note, and it never washed out, because
the pause happens again identically on every transport play.

Both clocks now start on the same line. If you have a project with a Start delay
that you tuned by ear against this behaviour, it will sit a few milliseconds later
than it used to.

### Direction

**Direction** `Up / Down / Up-Down (repeat) / Up-Down (no repeat) / Down-Up (repeat) / Down-Up (no repeat)` (default Up)

Walk order through the active voices in the pool. The "pool" is the first *Sequence Length* slots; inactive voices within the pool are skipped in all directions.

- **Up** — voices play in slot order V1, V2, V3, ..., loop back to V1. (Default, matches the original behavior.)
- **Down** — voices play in reverse slot order V8, V7, V6, ..., loop back to V8. (With *Sequence Length* = 4, plays V4, V3, V2, V1, V4, V3, ...)
- **Up-Down (repeat)** — walks up to the highest active voice, plays it twice (the "repeat" at the turnaround), walks back down, plays V1 twice, repeats. With 4 voices: 1, 2, 3, 4, 4, 3, 2, 1, 1, 2, 3, 4, 4, ...
- **Up-Down (no repeat)** — same bounce pattern but the boundary voices play just once. With 4 voices: 1, 2, 3, 4, 3, 2, 1, 2, 3, 4, 3, ...
- **Down-Up (repeat)** — bounce starting at the top. With 4 voices: 4, 3, 2, 1, 1, 2, 3, 4, 4, 3, 2, 1, 1, ...
- **Down-Up (no repeat)** — bounce starting at the top, no repeat at edges. With 4 voices: 4, 3, 2, 1, 2, 3, 4, 3, 2, 1, 2, 3, ...

**Loop = Off interactions.** Up or Down play one full pass through the pool and stop. Bounce modes play one complete bounce cycle (start edge → other edge → back to start edge) and stop. With 4 voices, Loop=Off + Up-Down (repeat) plays 1, 2, 3, 4, 4, 3, 2, 1 and stops; Up-Down (no repeat) plays 1, 2, 3, 4, 3, 2, 1 and stops.

**Glide and Legato interactions.** Glide bends between consecutive voices in whatever direction they're going — no glide-specific changes were needed. Legato mode (no re-attack at hand-offs) works the same: each voice rings until the next one takes over, regardless of walk direction.

**Switching direction mid-playback.** Toggling between Up and Down flips the walk immediately at the next hand-off. Toggling into or out of a bounce mode picks up with the current seq_dir at the next hand-off (no glitch).

### Play / Rest Gating (v2.1)

**Play for (steps)** `0–1000, default 0`
**Rest for (steps)** `0–1000, default 0`
**Rest mode** `Walk through / Freeze in place, default Walk through`

A per-step cyclic gate. The sequencer fires **Play for** notes normally, then sits in silence for some number of steps determined by **Rest for** + **Rest mode**, then resumes — the pattern repeats forever. Useful for phrase-and-pause melodies: "play 4 notes, sit silent for 4 notes' worth of time, play 4 more."

The feature is **disabled when either of Play for / Rest for is 0** (the default). With both at 0, the sequencer behaves as before; Rest mode has no effect when the gate is off.

**Rest mode** picks one of two fundamentally different behaviors for what the sequencer does during the rest period:

- **Walk through** (default): the sequencer keeps advancing through voice handoffs during rest. Each rest step consumes that voice's *Next voice in* duration silently. The total cycle is `Play for + Rest for` steps of the underlying sequencer grid. If `Play + Rest` doesn't divide evenly into your active voice count, the starting voice of each play period walks across the melody — `Play=5, Rest=4` with 8 active voices means you hear V1–V5, walk through V6–V8+V1 silently, then V2–V6, walk through V7+V8+V1+V2, etc. Notes get "skipped" in the literal sense and reappear in subsequent play periods at different positions. Good for **abstract / drone-friendly use** where the melody loops as a backdrop and play/rest is a rhythmic gate over it.

- **Freeze in place**: the sequencer **pauses** at the voice that would have fired when rest began. Rest duration is `Rest for × that frozen voice's "Next voice in"` seconds, timed by a sample counter rather than a step count. When rest ends, the frozen voice fires and the sequence picks up from there — **no notes lost, every voice plays in order across multiple cycles, just with pauses between phrases**. Good for **melodic / phrasal use** where the sequence is meant to be heard in full and the rest is just punctuation.

**What counts as a step (Walk mode).** Each handoff between voices is one step, regardless of whether the voice produces sound. Programmed rests (a voice with Note duration = 0) still count as steps — they consume their Next voice in time and tick the step counter. "Play for = 4" plays exactly 4 sequence positions, which may include programmed rests within them.

**Rest duration is the same wall-clock time in both modes.** Because each voice has its own Next voice in, the rest period's duration depends on which voices the sequencer would have walked through during the silent stretch. Walk mode sums those naturally; Freeze mode simulates the same walk at rest entry to compute its sample-timed rest window. So `Rest for = 4` means the same wall-clock duration whether you're in Walk or Freeze, even when voices have different per-step timings. With evenly-timed voices it's just `Rest for × that duration`; with varied timings the rest length varies between cycles (because different voices get walked-through in each cycle), but Walk and Freeze stay in lock-step on the same per-cycle value.

**Tails finish naturally — except in Legato mode where we force release.** When PR transitions to rest, the previously-firing voice continues:
- **Non-Legato mode**: the voice's sustain → release happens automatically based on its own Note duration, so it tails out naturally during the start of the rest period.
- **Legato mode**: a sustaining voice doesn't auto-release (it normally only releases when the next voice's Legato handoff inherits it). To prevent the voice ringing forever during rest, it's forced into release at the rest-entry moment — same trick used when a Loop=Off sequence walks off the end. This applies in both Walk and Freeze modes.

**Glide across rest.** When the play period resumes, the new note's glide source is whatever the last triggered voice's target frequency was — same as a normal handoff. The pitch slides from the last played note into the first note of the new play period.

**Transport behavior**: conventional. Stop silences; play re-initializes everything (sequencer index, step counter, rest state) and starts fresh from the first active voice.

**Changing Rest mode mid-rest** is an edge case the code handles defensively but not gracefully — the safest move is to flip the slider while the gate is in its play period, or to press stop/play to reset cleanly. The plugin won't crash but the current rest period may stretch or compress unpredictably.

### Ramp (v2.14 multi-target, selector-first)

A **one-time signed-delta ride** on any target over a set duration — the in-plugin substitute for a REAPER automation envelope, the "wind down / wind up once" move (vs Drift's endless wander). As of v2.14 it reaches **all 28 Drift targets** (same target set), each on its own timeline, using the same nested-selector pattern as Drift and the rest of the suite. Pick a target, set its `by` / duration / start delay; one global **engage** arms every configured target's ramp at once.

**Ramp target** `55 options, default Rate value`
Which parameter this ramp acts on — the same list as Drift target. All 55 ramp in parallel; the selector only chooses which one you are editing.

**Ramp by** `-1000 to +1000, step 0.001, default 0` (units match target)
Signed delta the target moves by over the duration (from 0 at the start to the full `by` at the end, then held). Units follow the target: the rate's current unit (BPM / Seconds / Hz) for Rate Value + Pan Rate, cycles for Timing + Note dur, dB for Gain, percent for Attack / Release. **0** = no ramp for this target. For Rate Value / Pan Rate the sign follows Rate Mode — in BPM/Hz modes negative `by` = slower, in Seconds mode (period) positive `by` = slower.

**Ramp time unit** `Cycles / Seconds / Minutes / Beats, default Minutes`
What the duration and start delay below are counted in — one unit for both, so
they always mean the same thing as each other. **Minutes** is the default and is
what this block always did. **Seconds** is there so a thirty-second ramp can be
typed as `30` rather than as `0.5` minutes. **Cycles** counts this plugin's own
sequencer cycles, referenced against the rate before drift and ramp touch it, so
a ramp cannot alter its own clock. **Beats** follows the project tempo live.

**Ramp duration** `0–60, default 0` · **Ramp start delay** `0–60, default 0`
Per-target, in ramp time units. Each target waits out its own start delay, then rides its `by` over its own duration. Because both are per-target, different targets can wind down over **different timelines** from a single engage (e.g. slow the tempo over 10 minutes while softening Attack over the first 2). Duration 0 = that target's ramp is off.

**Ramp play for** `0–1000, default 0` · **Ramp rest for** `0–1000, default 0`
Per-target, in ramp time units. Turns the smooth ride into a **staircase**: the
ramp advances for `play`, holds for `rest`, and repeats. Both zero is the smooth
ramp, which is the default.

The holds come **out of** the duration rather than extending it — the advancing
steps are made proportionally faster — so Ramp duration goes on meaning "you
arrive in about this long" however you set the staircase.

**Ramp engage** `Off / On, default Off` — **GLOBAL**
One switch arms every configured target. It's a freeze/resume gate (NOT a restart edge): while On, each target's ramp clock advances toward completion; while Off, all clocks freeze and resume from where they are on re-engage.

**Granularity mirrors Drift:** Rate Value + Pan Rate convert the delta to a mode-aware ratio; per-voice Timing + Gain add per sample; the articulation targets (Note dur, Attack %, Release %) sample the ramp offset **once per note at trigger** so a ringing note's length/shape stay fixed. Ramp and Drift compose at the same consumption site — you can ramp a target down once *and* drift it at the same time.

**Transport behavior:** every target's ramp progress resets to 0 on every transport play edge — the only thing that resets it. Slider changes adjust the trajectory live without resetting.

**Migration from v2.13:** Ramp was single-target (Rate Value only). It now reaches 28 targets, and the Drift block was renumbered selector-first so the target selector reads above its controls in NVDA order. On that load, old projects' Ramp **and** Drift configs reset to defaults — reconfigure after upgrade.

### Drift (v2.9 nested-selector)

Slow organic wander applied independently to any of **28 targets** — the full expressive surface of a melodic phrase. Each target can have its own drift configuration; all 28 drift in parallel. The selector chooses which target's drift you're currently editing — the others keep running with their last-saved configuration.

The target set is built to let a sequence *breathe*: timing (rubato), dynamics (per-voice volume swell), and articulation (note length, onset/tail softness) all wander on independent slow schedules, the way a live player phrases rather than a loop repeats.

Same pattern as Womb v3's drift and the rest of the v2.9 sweep. Switching the **Drift target** selector saves the current amount / period / shape / play / rest values into the old target's memory slot, then loads the new target's saved values. All 28 configurations persist across project save/load.

**Drift target** `55 options, default Rate value`

Every control that shapes the sound, in the order the controls appear: Rate value, Pulse width, Tuning reference, Transpose, Binaural beat, Attack, Release, Glide time, Pan spread, Pan glide, Pan base rate, Pan increment; then for each voice its Pitch, Fine tune, Next voice in, Note duration and Gain; then Master gain, Play for and Rest for. Amounts are in each target's own unit. Play for and Rest for round to whole steps.

**Drift up amount** `0.0–20.0, default 0` (units match target)
How far above the target's baseline the drift wanders at its peak. Units: the rate's current unit (BPM / Seconds / Hz) for Rate Value + Pan Rate, cycles for Timing + Note dur, dB for Gain, percent for Attack / Release. Dial small values in Seconds / Hz modes. 0 = drift off on the up side.

**Drift down amount** `0.0–20.0, default 0` (units match target)
How far below the baseline the drift wanders at its trough. Independent from Up — asymmetric wander supported. Either non-zero activates drift for the target; both 0 = drift off.

### Whose turn it is (2026-09-09)

Some drift targets are read by the engine **once per event** rather than
continuously. Those now advance their wander by exactly one step of
`1 / period` at that moment, and not at all in between — so a period of 8 is
eight of that event, and it stays eight however much the other targets move.

Before this they were sampled out of a wander that never stopped spinning:
almost all the motion was thrown away, the period did not count what it said,
and the targets were not independent of each other. Rozaya found it, 2026-09-09.

**It is a switch now, not a rule (2026-09-09).** `Drift movement`, sitting with
the period controls, is per target: `With the target` or `On a clock`. Rozaya:
it *"should have been a switch from the very beginning"* -- both are ordinary
artistic choices and neither is the plugin's to make. The defaults below are
what the plugin used to decide on its own, so nothing saved changed.

**Defaults to `With the target`:** each voice's **Pitch**, **Fine tune** and **Note duration**, stepping when that voice plays; and **Transpose**, **Attack**, **Release**, **Play for** and **Rest for**, stepping on every note. Everything else defaults to `On a clock`.

The eight **Note duration** targets, plus **Attack** and **Release**, were the original stepped ones. A note's length and envelope shape are read once, when the note
fires, and are then fixed for its whole ring — so each voice's Note duration
steps when *that* voice plays, and the shared Attack/Release step on every note.

**Defaults to `On a clock`:** Rate value, the eight V Timing targets, Pan
base rate and the eight Gains. Their values are read every sample, so the wander
is fully expressed. Rate value in particular measures its period against the
rate *before* drift, so it never measures itself.

A stepped wander is a staircase with as many steps as its period has events.
Long periods sound much as they did; short ones are more obviously
event-to-event.

**Drift period** `0–1000, default 8, 0 = off`
How long one full drift wave takes for this target, counted in whatever the unit
below says.

**Drift period unit** `Cycles / Seconds / Beats, default Cycles`
**Cycles** counts this plugin's own sequencer cycles — a period of 8 means eight
cycles, and it follows the rate for free, which is what the control always did
before this unit existed. **Seconds** is wall clock, independent of the rate.
**Beats** counts the project tempo, so the wander follows the host rather than
the melody, and it follows a live tempo change.

**`With the target` in Seconds or Beats (2026-09-10).** The first unit counts turns. In Seconds or Beats the drift's clock runs in that unit only while the target's own thing is happening — a voice's own targets while that voice holds the step, the shared ones while any note does — and freezes in between, picking up where it stopped at the next turn. Rozaya: *"stop mid-cycle, freeze the clock mid-whatever unit, then pick up on the next cycle from wherever the clock was last."* Until then those two units were silently ignored for such a target.

The period is measured against the rate **before** drift and ramp touch it, so
drifting the rate cannot modulate its own drift period.

**Drift play for** `0–64 periods, default 0` · **Drift rest for** `0–64 periods, default 0`
Makes the drift come and go instead of wandering forever. It drifts for `play`
periods, then **freezes exactly where it stopped** for `rest` periods, then
carries on. Both must be above zero or the gate is off entirely — which is what
`0` means, and why the default is "always".

It freezes in place rather than returning to centre, and that is the interesting
part: **the fraction of the play value chooses where it parks.** `x.25` parks at
the crest, `x.75` at the trough, and `x.0` or `x.5` at no change at all. So a
whole number parks at neutral every single time and is nearly inaudible, while
an awkward fraction is the one worth using — each freeze lands further round the
wave than the last, so `1.75` cycles through four different park points before
repeating and `1.2` through five. Setting only `Drift down` wastes half of them,
because every park on the positive half lands at no change.

**Drift shape** `Sine / Triangle / Random, default Sine`
Wander waveform. Sine = smooth, Triangle = linear ramps with turnarounds, Random = value-noise interpolating smoothly between fresh random targets at each period boundary.

#### Granularity — per-sample vs per-note (by design)

Rate Value, the per-voice Timing targets, Pan Rate, and the per-voice Gain targets drift **continuously (per sample)** — they're rates and levels that should glide smoothly. Note dur, Attack %, and Release % are sampled **once per note, at the moment it triggers** — they shape an individual note, and a note's length / envelope shouldn't move while it's still ringing. So Gain drift gives smooth volume swells; Note-dur / Attack / Release drift gives note-to-note articulation variation.

#### Notes

- **Per-voice timing drift wanders the step length** ("Next voice in"), not the note duration. The note still rings for its own (possibly separately-drifted) Note duration; only *when the next voice takes over* moves.
- **A base-rest voice stays a rest.** A voice with Note duration 0 is silent regardless of Note-dur drift — drift only adjusts the length of notes that actually fire.
- **Pan Rate drift only affects the Tremolo and Increment pan modes.** Spread / Spread Reversed are static positions.
- **Mode-direction asymmetry on Rate Value / Pan Rate:** a positive drift amount speeds up in **BPM**, **Hz** and **N per beat**, and slows down in **Seconds** and **Every N beats**. The split is not arbitrary — the second group counts *time per cycle*, so a bigger number is a longer cycle. Whichever mode you are in, a positive amount always moves the number on the slider upward; it is the *speed* that follows the unit.

#### Transport behavior (v2.9)

On every transport play press, drift cycle restarts: all 28 targets' phase counters → 0. The sequencer resets to the first voice (not yet started), every voice goes silent with cleared envelopes / oscillator phases / pan state, glide bookkeeping resets, and the Play/Rest gate resets. Drift CONFIG is preserved across stop/play and project save/load. Ramp progress also resets. Renders are deterministic for Sine and Triangle shapes (Random remains non-deterministic per render by design).

#### Migration from v2.8

The old flat-drift block (musical_up/down/period, slow_up/down/period, drift_shape) was 7 sliders covering Rate Value only. v2.9 made it 5 sliders covering 28 independent targets, and it is 8 today with the period unit and the play/rest pair. On that upgrade, old projects' Drift and Ramp configs reset to defaults — reconfigure under the nested-selector pattern. Later changes have not reset anything: the 2026-09-06 one accepts the older save formats and simply leaves the new controls off.

## Usage Notes

**Building a melody.** Start with all 8 voices set Active, give each a different Semitones value (the default spec gives a rough C major arpeggio), keep "Next voice in" = "Note duration" = 1 cycle for a clean walk. Adjust "Next voice in" per voice for rhythmic variation, "Note duration" for phrasing.

**Adding rests.** Set a voice's "Note duration" to 0. The voice still "takes up" its "Next voice in" duration in the sequence — that's the rest length. The rest is true silence: no envelope ramp, no click on entry or exit.

**Overlap for sustain.** Set "Note duration" to a value greater than "Next voice in." When the sequencer moves to the next voice, the previous voice's note keeps ringing through its release. With Release Shape = Cosine and a long Release %, this gives a gentle decaying tail under the new note.

**Click-free envelope on instant transitions.** Even when you set Attack % or Release % to 0 (sharp gate on or off), the plugin's output amplitude is passed through a one-pole exponential smoother with a ~3 millisecond time constant before reaching the oscillator — same trick Polyrhythm Phase uses. The state machine's raw envelope value can step instantly from 0 to 1 or vice versa, but what reaches the speakers ramps over a few milliseconds, which the ear hears as a clean transition rather than a click. Your user-set attack / release percentages aren't silently rewritten — if you ask for 0% you get a sharp envelope, just one that's perceptually click-free. Same applies to rest steps (Note duration = 0): the smoother fades any tail from the previous voice gracefully.

**Looping vs one-shot.** Loop = On for ambient / sleep loops where the sequence cycles indefinitely. Loop = Off for a one-shot melodic phrase that plays once on plugin activate / playback start, then goes silent.

**Pairing with Polyrhythm Phase.** Run both on separate tracks at the same Tuning Reference — Polyrhythm Phase as the sustained drone bed, Melody Phase as the melodic figure on top. Match Root Notes for consonance, or detune Melody Phase slightly for movement.

**Glide for pitch bends within notes.** With Glide time > 0 and Legato glide Off (the default), each note retains its own attack / release ceremony and the pitch bends *during* the note — you hear distinct voices that each slide pitch-wise. Useful for articulated melodies where the pitch movement is the ornament, not the structure.

**Legato glide for one continuous bending tone.** Turn Legato glide On (and set Glide time > 0) for the classic monosynth portamento sound — one ongoing tone whose pitch slides smoothly between targets, with no attack / release events at the note boundaries. Voices ring continuously (the per-voice "Note duration" is effectively ignored in Legato mode — the voice always rings until the next one takes over). The first note still attacks normally, the last note still releases normally, and rests (Note duration = 0) extend the previous voice's hold time. Works regardless of how the voices' timing sliders are set — just turn it on and the sequence becomes a smooth bending tone.

**Spread pan for melodic clarity.** With Pan enabled and Mode = Spread, each voice in the sequence gets a fixed position across the stereo field. The ear easily tracks which voice is which — V1 might be far left, V8 might be far right — and the melody feels spatially organised even if the notes themselves overlap or sit close in pitch. Pair with a second instance set to Spread Reversed (and slightly different timing) for a wider, more enveloping result.

**Pan transition follows Glide in Legato mode.** Pan position uses a one-pole smoother to slide between positions (~10ms by default — fast enough to feel snappy, slow enough to be click-free). When Legato glide is on AND Glide time > 0, the pan smoother slows down to match the Glide time — so pitch and pan transition at the same perceived speed and feel like one coherent slide. Without this, the pan finishes its 10ms slide while the pitch is still gliding for hundreds of ms, which the ear hears as a sharper-than-expected position change on top of a slow pitch bend.


#### ~~Host x hands you the ratio list, not a multiplier~~ — HISTORICAL

> **Describes a shape Melody no longer has.** Kept because it is a dated release note and those are not rewritten, but neither the `Host x` rate mode nor the `Host ratio` picker exists in this plugin today; see *Sync to host* above for what it actually does.

Switching Rate Mode to **Host x** lands on **1 per beat** and hides the raw rate number. The **Host ratio** list becomes the control you use — *every 8 beats, every 4 beats, 1 per beat, 2 per beat*, and so on — so setting a rate is picking a name, never working out a number.

Set Host ratio to **Custom** and the rate value reappears, with whatever it last held. That's the way in for ratios the list doesn't cover, which is most of the point of a multiplier rather than a note grid.

Two things this fixes. The rate slider's default was chosen for its own unit, so switching mode used to hand you a speed you never asked for — in the effects, a default of 2 meant *double time* the moment you selected Host x. And the picker sits at the far end of the parameter list (slider IDs can never be renumbered without scrambling saved projects), so you met the multiplier first and the cure last.

Landing on 1 per beat only happens when *you* change the mode. Opening a saved project leaves your rate exactly as you set it.


#### The sequence is placed from the project

**In either host mode** and with the transport rolling, the sequencer works out which note it should be on from the project position — so starting playback at bar 40 gives you the note you'd have reached playing from the top, not the first note again.

Placed **once**, on transport start or when you move the playhead, then left to run. A sequencer that re-decided its position constantly would jump mid-note.

**Every direction mode is placed** — Up, Down, and both bounce modes, with Loop on or off. A bouncing sequence is periodic (there and back is simply a longer cycle) and Loop = Off is simpler still: the plugin walks until the sequence would have ended, and if you've started past that point, it's finished, which is the correct answer.

**The Play / Rest gate is placed too**, in both rest modes. In **Walk** the sequencer keeps stepping through rest, so the gate is just a second wrap running alongside the first. In **Freeze** the sequencer stops while the clock keeps going, so each rest injects time in which nothing advances — the plugin accounts for that, and if you land inside a rest it sits frozen on the right voice with the right amount of rest still to run.

One thing is not placed, and it starts from the top as before: **per-voice timing Drift or Ramp**. The step lengths at bar 40 aren't the ones a walk from bar 0 would have used, so placing would be a confident guess rather than an answer — the same rule the sweeping effects follow, where anything modulating the rate hands back to free-running.

Nothing is lost in that case; it behaves exactly as it always has.

On a mid-song seek, the note you land on **retriggers from the start of its envelope** rather than continuing partway through. You get the right note; it just begins again.

---

## If something sounds wrong

**Several instances come in slightly out of step when you open the project.**

Switch away from REAPER and back again — click any other window, then click back
on REAPER. Alt-Tab out and in does the same thing. They lock together straight
away.

Pressing play and then stop puts them back out of step, so do the switch *last*
if you have been using the transport.

Nothing is broken while they are out of step. Your project is fine, your
settings are fine, and renders are unaffected — it just sounds a little loose.
It happens because each instance starts counting from the moment REAPER creates
it, and REAPER creates them one after another as the project opens. There is
nothing to set and nothing to repair.

**A note runs longer than it should, and the instances never quite catch up.**

Same fix, same cause. Switch away and back.

---

*Melody Phase is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

