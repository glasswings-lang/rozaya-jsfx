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

**Rate Mode** `BPM / Seconds / Hz / Host x` (default Seconds)
How to interpret Rate Value. **Seconds** = seconds per cycle; with Rate Value = 1 (also the default), one cycle equals one second, so the per-voice "Next voice in" and "Note duration" numbers behave as raw seconds. This is the easiest way to work in plain time — set a voice to 2 and it plays for 2 seconds. **BPM** = beats per minute; Rate Value becomes the tempo, and the per-voice numbers become beats. Useful if you want a polyrhythmic feel where every voice is in a sensible ratio of a common tempo. **Hz** = cycles per second; Rate Value is the cycle frequency. Useful for very slow ambient pacing (Rate = 0.05 Hz means one cycle every 20 seconds). **Host x** = follow the project tempo; see below.

**Rate Value** `0.001 – 1000`
The global rate. Meaning depends on Rate Mode (see above). Default 1, which in the default Seconds mode means "each per-voice cycle is one second."

### Host x — following the project tempo

In the first three modes each instance holds its own absolute rate, and nothing
in the plugin knows that two instances are related. That's fine until you want
to change the speed of a whole arrangement: nudging every instance by hand
changes the *relationships* between them, not just the pace, and layers that
used to nest start scattering.

**Host x** makes Rate Value a **multiplier of the project tempo** instead of an
absolute rate. x1 = one cycle per beat, x2 = twice as fast, x0.5 = half. Higher
is faster, same as BPM and Hz (only Seconds inverts). Move the project tempo and
every instance moves with it, in proportion.

This is **not** quantising. Rate Value stays continuous, so unlocked
relationships are as available as locked ones — and they survive a tempo change
too:

| Layer | Multiplier | Tempo 40 | Tempo 45 |
|---|---|---|---|
| Fast | x1 | 40 | 45 |
| Mid | x0.5 | 20 | 22.5 |
| Slow | x0.25 | 10 | 11.25 |

…nests forever, while `x1 / x0.618 / x0.25` never resolves — and keeps not
resolving in the same way at any tempo.

Tempo changes take effect live, including mid-playback. Voice and envelope
proportions are untouched; the melody just runs faster or slower.

**Host ratio (writes Rate Value)** `Free / 1/8 / 1/4 / 1/3 / 1/2 / phi down (0.618) / 2/3 / 3/4 / 1 / 4/3 / 3/2 / phi up (1.618) / 2 / 3 / 4 / 8` (default Free)
A convenience picker, shown only in Host x mode. Choosing an entry writes that
multiplier into Rate Value and then gets out of the way — it does not hold Rate
Value afterwards, so you can still type or automate any value you like. **Free**
never writes anything. The list carries the two phi ratios alongside the tidy
ones because deliberately-unlocked relationships are first-class here.

**Waveform** `Sine / Triangle / Saw / Golden TS / Golden SG / Golden GS / Bell / Wavefold / Half-sine / Phi-cascade / Phi Triangle / Phi Sine`
Same set as Polyrhythm Phase — see that plugin's Waveform section for descriptions, including the back-compat note on the Golden / Phi family. Note that Half-sine sounds an octave higher than the others at the same note + Center Octave setting (full-wave-rectified spectrum has no fundamental).

**Tuning Reference Hz** `400 – 480`
Frequency of A4. Standard concert pitch is 440.

**Root Note** `C / C# / D / D# / E / F / F# / G / G# / A / A# / B`
The base note. Each voice's Semitones field is relative to this.

**Center Octave** `0 – 8`
Octave of the root note. With Root Note = A and Center Octave = 4, the base frequency is A4 = 440 Hz (at default tuning).

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

### Pan (sliders 15-19)

Mirrors Polyrhythm Phase's pan section. When enabled, each voice gets independently-positioned L and R amplitudes — the binaural beat is preserved across the pan because each channel keeps its own oscillator. Pan Mode picks one of four behaviors.

**Pan Enabled** `Off / On`
Toggles the whole pan group. When off, voices sum straight to mono (and the sub-sliders below are hidden in Reaper). Default Off.

**Pan Mode** `Tremolo / Increment / Spread / Spread Reversed` (default Spread)
- **Tremolo** — each voice's pan position oscillates over time at Pan Base Rate. All voices share the same rate.
- **Increment** — each voice's pan rate is Pan Base Rate + (voice index × Pan Increment), so V1, V2, V3… all pan at slightly different rates and drift in and out of phase.
- **Spread** — voices get static pan positions ranked across the stereo field. V1 sits at one end, V8 at the other, the rest spread evenly between. Active voices only; inactive ones are skipped in the ranking. **Most useful for melodies** — each note in the sequence lives in a distinct spatial position, which makes the line easy to follow.
- **Spread Reversed** — same as Spread but flipped. Pairs nicely with another instance set to Spread for compositional stereo width.

**Pan Spread %** `0 – 100`
How wide the pan moves. 100 = full stereo. 0 = collapses to center (effectively defeats pan).

**Pan Base Rate** `0.001 – 1000` (Tremolo / Increment modes only)
Pan LFO rate, in the same units as the global Rate Mode. Hidden when pan is off or when Pan Mode is Spread / Spread Reversed.

**Pan Increment per Voice** `-1000 – 1000` (Increment mode only)
How much each successive voice's pan rate increases over the previous voice's. Hidden in other modes.

### Glide / portamento (sliders 20-21)

**Glide time (seconds; 0 = off)** `0 – 5`
When > 0, each new voice's pitch starts at the previous voice's target frequency and slides to its own target over this many seconds. 0 = no glide; voices jump directly to their pitch. Independent of all other timing — set Glide to 0.05 and notes will slide quickly into pitch from wherever the last one was, regardless of *Next voice in* or *Note duration*.

**Legato glide** `Off / On`
- **Off** (default) — each voice has its own attack and release. Glide bends the pitch *during* each note; you hear each voice as a distinct envelope event at the hand-off (attack ramp on the new note, release ramp on the old). Good for plucky / articulated melodies where each note should feel separately spoken.
- **On** — the whole sequence becomes one continuous tone whose pitch slides between voices. The first note attacks normally; every subsequent hand-off skips the attack and inherits both the envelope value and the oscillator phase from the previous voice; pitch slides via glide. The previous voice's "Note duration" is effectively ignored — voices ring continuously until the next one takes over (which silences the previous one). The last note (when Loop = Off and the sequence ends) releases normally. **Rests still work** — a voice with Note duration = 0 doesn't trigger a hand-off, so the previously-ringing voice keeps holding through the rest's step time (which is what "continuous tone with no rest" sounds like in this mode — if you want actual silences in Legato mode, use Active = Off to skip a voice slot entirely).

Good for legato / flowing melodies where you want one bending tone instead of articulated steps. Set Glide time > 0 to actually hear the pitch slide; with Glide = 0 + Legato On, the pitch jumps between targets but there's still no attack ceremony.

### Per Voice (V1–V8)

**Vn Semitones from root** `-24 – 24`
This voice's note, in semitones above (positive) or below (negative) the global Root Note + Center Octave.

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

### Start Delay

**Start Delay** `0–1000, default 0`

How long the plugin sits silent at the start of playback before the sequencer begins. Units match Rate Mode: BPM mode counts cycles of the global Rate Value (so 4 with Rate Value = 60 BPM = 4 beats = 4 seconds), Seconds mode is literal seconds, Hz mode counts cycles of Rate Value. 0 disables the delay entirely.

During the delay the sequencer state stays frozen — when the delay elapses, the sequence begins cleanly from V1 (or the first active voice) rather than mid-step. Re-arms on every transport stop/start.

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

### Speed Ramp (v2.14 multi-target, selector-first)

A **one-time signed-delta ride** on any target over a set duration — the in-plugin substitute for a REAPER automation envelope, the "wind down / wind up once" move (vs Drift's endless wander). As of v2.14 it reaches **all 28 Drift targets** (same target set), each on its own timeline, using the same nested-selector pattern as Drift and the rest of the suite. Pick a target, set its `by` / duration / start delay; one global **engage** arms every configured target's ramp at once.

**Speed ramp target (slider 67)** `28 options, default Rate Value`
Which parameter this ramp acts on — identical list to the Drift target selector (Rate Value, V1–V8 Timing, Pan Rate, V1–V8 Gain, V1–V8 Note dur, Attack %, Release %). Switching it saves the three per-target sliders (68/69/71) into the old target's slot and loads the new target's stored values. All 28 targets ramp in parallel; the selector only chooses which one you're editing.

**Speed ramp by (slider 68)** `-1000 to +1000, step 0.001, default 0` (units match target)
Signed delta the target moves by over the duration (from 0 at the start to the full `by` at the end, then held). Units follow the target: the rate's current unit (BPM / Seconds / Hz) for Rate Value + Pan Rate, cycles for Timing + Note dur, dB for Gain, percent for Attack / Release. **0** = no ramp for this target. For Rate Value / Pan Rate the sign follows Rate Mode — in BPM/Hz modes negative `by` = slower, in Seconds mode (period) positive `by` = slower.

**Speed ramp duration (slider 69)** `0–60 minutes, default 0` · **Speed ramp start delay (slider 71)** `0–60 minutes, default 0`
Per-target. Each target waits out its own start delay, then rides its `by` over its own duration. Because both are per-target, different targets can wind down over **different timelines** from a single engage (e.g. slow the tempo over 10 minutes while softening Attack over the first 2). Duration 0 = that target's ramp is off.

**Speed ramp engage (slider 70)** `Off / On, default Off` — **GLOBAL**
One switch arms every configured target. It's a freeze/resume gate (NOT a restart edge): while On, each target's ramp clock advances toward completion; while Off, all clocks freeze and resume from where they are on re-engage.

**Granularity mirrors Drift:** Rate Value + Pan Rate convert the delta to a mode-aware ratio; per-voice Timing + Gain add per sample; the articulation targets (Note dur, Attack %, Release %) sample the ramp offset **once per note at trigger** so a ringing note's length/shape stay fixed. Speed Ramp and Drift compose at the same consumption site — you can ramp a target down once *and* drift it at the same time.

**Transport behavior:** every target's ramp progress resets to 0 on every transport play edge — the only thing that resets it. Slider changes adjust the trajectory live without resetting. Duration is wall-clock minutes (an absolute real-time ride), unlike Drift's rate-relative period.

**Migration from v2.13:** Speed Ramp was single-target (Rate Value only) on sliders 67–70. It's now 5 sliders (67–71) reaching 28 targets, and the Drift block shifted to **72–76** (selector-first renumber so the target selector reads above its controls in NVDA order). On load, old projects' Speed Ramp **and** Drift configs reset to defaults (the save-format version guard forces this) — reconfigure after upgrade. The plugin's *sound* sliders (1–66) are untouched. Re-adding the plugin instance gives clean defaults.

### Drift (v2.9 nested-selector)

Slow organic wander applied independently to any of **28 targets** — the full expressive surface of a melodic phrase. Each target can have its own drift configuration; all 28 drift in parallel. The selector chooses which target's drift you're currently editing — the others keep running with their last-saved configuration.

The target set is built to let a sequence *breathe*: timing (rubato), dynamics (per-voice volume swell), and articulation (note length, onset/tail softness) all wander on independent slow schedules, the way a live player phrases rather than a loop repeats.

Same pattern as Womb v3's drift and the rest of the v2.9 sweep. Switching the **Drift target** selector saves the current sliders 73-76 into the old target's memory slot, then loads the new target's saved values. All 28 configurations persist across project save/load. (Sliders 72–76 as of v2.14 — the block shifted up by one to make room for the Speed Ramp target selector at 67.)

**Drift target** `28 options, default Rate Value`
- **Rate Value** — wanders the global melody rate; stretches the whole timeline (sequencer + envelopes + pan together). The old single drift target.
- **V1–V8 Timing** — wanders each voice's step length ("Next voice in", in cycles). The rhythm breathes: voices fall slightly early or late against the grid on independent schedules. Wanders *when the next voice takes over*, not the ringing note's length.
- **Pan Rate** — wanders the Pan Base Rate (Tremolo / Increment pan modes only).
- **V1–V8 Gain** — wanders each voice's volume (dB), continuously per-sample, so the line swells and recedes. This is the **dynamics** axis — the core of "breathing." Each voice undulates independently.
- **V1–V8 Note dur** — wanders each voice's Note duration (cycles). **Articulation:** notes drift between overlapping (legato) and separated (staccato). Sampled once per note at trigger.
- **Attack % / Release %** — wander the global attack and release lengths (%). Onsets and tails soften and sharpen. Sampled per note at trigger.

**Drift up amount** `0.0–20.0, default 0` (units match target)
How far above the target's baseline the drift wanders at its peak. Units: the rate's current unit (BPM / Seconds / Hz) for Rate Value + Pan Rate, cycles for Timing + Note dur, dB for Gain, percent for Attack / Release. Dial small values in Seconds / Hz modes. 0 = drift off on the up side.

**Drift down amount** `0.0–20.0, default 0` (units match target)
How far below the baseline the drift wanders at its trough. Independent from Up — asymmetric wander supported. Either non-zero activates drift for the target; both 0 = drift off.

**Drift period (cycles)** `1–1000, default 8`
How many global rate cycles one full drift wave takes for this target. All 28 targets use rate cycles as their period unit, scaled by Speed Ramp so the wave-per-cycle relationship stays constant under wind-down.

**Drift shape** `Sine / Triangle / Random, default Sine`
Wander waveform. Sine = smooth, Triangle = linear ramps with turnarounds, Random = value-noise interpolating smoothly between fresh random targets at each period boundary.

#### Granularity — per-sample vs per-note (by design)

Rate Value, the per-voice Timing targets, Pan Rate, and the per-voice Gain targets drift **continuously (per sample)** — they're rates and levels that should glide smoothly. Note dur, Attack %, and Release % are sampled **once per note, at the moment it triggers** — they shape an individual note, and a note's length / envelope shouldn't move while it's still ringing. So Gain drift gives smooth volume swells; Note-dur / Attack / Release drift gives note-to-note articulation variation.

#### Notes

- **Per-voice timing drift wanders the step length** ("Next voice in"), not the note duration. The note still rings for its own (possibly separately-drifted) Note duration; only *when the next voice takes over* moves.
- **A base-rest voice stays a rest.** A voice with Note duration 0 is silent regardless of Note-dur drift — drift only adjusts the length of notes that actually fire.
- **Pan Rate drift only affects the Tremolo and Increment pan modes.** Spread / Spread Reversed are static positions.
- **Mode-direction asymmetry on Rate Value / Pan Rate:** in BPM and Hz modes a positive drift amount speeds up; in Seconds mode (period) a positive amount slows down.

#### Transport behavior (v2.9)

On every transport play press, drift cycle restarts: all 28 targets' phase counters → 0. The sequencer resets to the first voice (not yet started), every voice goes silent with cleared envelopes / oscillator phases / pan state, glide bookkeeping resets, and the Play/Rest gate resets. Drift CONFIG is preserved across stop/play and project save/load. Speed Ramp progress also resets. Renders are deterministic for Sine and Triangle shapes (Random remains non-deterministic per render by design).

#### Migration from v2.8

The old flat-drift block (musical_up/down/period, slow_up/down/period, drift_shape on sliders 71-77) was 7 sliders covering Rate Value only. v2.9 made it 5 sliders covering 28 independent targets; v2.14 shifted those IDs to **72–76** (from 71–75) so the Speed Ramp target selector could take 67. On upgrade, old projects' Drift + Speed Ramp configs reset to defaults (the save-format version guard forces this) — reconfigure under the nested-selector pattern.

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

---

*Melody Phase is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---

