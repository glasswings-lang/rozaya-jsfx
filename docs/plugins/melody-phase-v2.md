# Melody Phase v2

**Designed by Rozaya — Developed with Claude (Anthropic)**

> **Melody Phase v2 replaces the original Melody Phase.** Same instrument and
> the same engine — a step-sequencer melody synth — but the per-voice controls
> are reorganised. v1 laid all eight voices out as forty flat sliders (V1–V8 ×
> five controls each), a long wall to walk. v2 collapses them behind a single
> **Voice** selector: pick a voice, and five controls below show and edit *that*
> voice. **All eight voices still play** — the selector is an editing cursor,
> not a mute. Everything else — rate, waveforms, pan, glide, legato, direction,
> play/rest gating, Speed Ramp and Drift — is carried over unchanged. (The flat-slider version is still
> maintained as `melody_phase.jsfx` — see [melody-phase.md](melody-phase.md).
> It came back out of the archive on 2026-08-11 because every project on disk
> uses it and none use v2.)

## Overview

A step-sequencer melody synth, sibling to Polyrhythm Phase. Up to 8 voices participate in a sequence; each voice plays a single note for its own *Next voice in* duration, then hands off to the next active voice. Each voice has its own *Note duration* controlling how long its note actually sounds — when "Note duration" is longer than "Next voice in," the voice's release continues in parallel with the next voice's attack (overlap / phrasing). When "Note duration" is shorter, there's a rest before the next voice enters. When they're equal, the handoff is clean and sequential.

Inactive voices are skipped in the sequence entirely. To insert a rest (a silent step), leave a voice Active and set its "Note duration" to 0 — the voice contributes silence for its "Next voice in" duration, then hands off, with no click on entry or exit.

The one thing to learn coming from v1: **the per-voice controls live behind the Voice selector.** Set the **Voice** slider to 1, dial that voice's Note / timing / gain / active state, move the selector to 2, dial that one, and so on. Each voice keeps its own settings, they persist with the project, and every voice plays regardless of which one the selector is currently showing.

Beyond the core sequencer:

- **Per-voice pan** with four modes (Tremolo, Increment, Spread, Spread Reversed) — Spread is especially useful for melody, giving each active voice a fixed position across the stereo field so the line is easy to track spatially.
- **Glide / portamento** — pitch slides between voices over a configurable duration, independent of all other timing.
- **Legato glide** — the whole sequence becomes one continuous tone whose pitch slides between voices, with no attack / release at the boundaries.

The waveform list (10+ options), envelope shapes, tuning math, binaural beat, and pan section are carried over directly from Polyrhythm Phase. Both per-voice timing values are expressed in cycles of the global rate, so rhythmic relationships line up — Voice 1 at 2 cycles, Voice 2 at 1 cycle, Voice 3 at 0.5 cycles will line up cleanly against the same rate.

## Signal Architecture

Each voice runs two oscillators (one for L, one for R). The R oscillator's frequency is offset from the L oscillator's by the binaural beat value (in Hz). When binaural beat is 0, L and R are identical and the voice sums to mono.

A sequencer index tracks which voice is currently "in its step." When that voice's *Next voice in* elapses, the index advances to the next active voice and triggers its envelope attack. The outgoing voice's envelope keeps running through its own (longer or shorter) *Note duration* independently — that's where overlap comes from. Up to 8 voices can be sounding at once during overlapping phrasing.

The envelope is a four-segment state machine: attack → sustain → release → silent. Attack % and Release % set how much of each note's duration is attack and release; sustain fills the middle. If Attack% + Release% would exceed 100%, both are scaled proportionally to fit. The output amplitude passes through a one-pole exponential smoother (~3 ms) before the oscillator, so even instantaneous transitions (attack% = 0 or release% = 0) come out click-free.

When Glide time > 0, each new voice's frequency starts at the previous voice's target and slides toward its own via a one-pole smoother. When Legato glide is on, the sustain → release transition is suppressed — each voice rings continuously until the sequencer's next hand-off inherits its envelope, phase, and pan, so only pitch slides across the boundary. When Loop is on, the sequence wraps from the last active voice back to the first; when off, it plays once and stops.

## Parameters

### Global

**Rate Mode** `BPM / Seconds / Hz / Host x` (default Seconds)
How to interpret Rate Value. **Seconds** = seconds per cycle; with Rate Value = 1, one cycle is one second, so the per-voice "Next voice in" and "Note duration" numbers behave as raw seconds. **BPM** = beats per minute; the per-voice numbers become beats. **Hz** = cycles per second (Rate = 0.05 Hz means one cycle every 20 seconds — good for very slow ambient pacing). **Host x** = follow the project tempo; see below.

**Rate Value** `0.001 – 1000` (default 1)
The global rate; meaning depends on Rate Mode.

### Host x — following the project tempo

In the first three modes each instance holds its own absolute rate, and nothing
in the plugin knows that two instances are related. That's fine until you want
to change the speed of a whole arrangement: nudging every instance by hand
changes the *relationships* between them, not just the pace, and layers that
used to nest start scattering.

**Host x** fixes that by making Rate Value a **multiplier of the project
tempo** instead of an absolute rate. x1 = one cycle per beat, x2 = twice as
fast, x0.5 = half. Higher is faster, same as BPM and Hz (only Seconds inverts).
Move the project tempo and every instance moves with it, in proportion.

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

**Host ratio (writes Rate Value)** `Free / every 8 beats / every 4 beats / every 3 beats / every 2 beats / phi slow / 2 per 3 beats / 3 per 4 beats / 1 per beat / 4 per 3 beats / 3 per 2 beats / phi fast / 2 per beat / 3 per beat / 4 per beat / 8 per beat` (default Free)
A convenience picker, shown only in Host x mode. Choosing an entry writes that
multiplier into Rate Value and then gets out of the way — it does not hold Rate
Value afterwards, so you can still type or automate any value you like. **Free**
never writes anything. The list carries the two phi ratios alongside the tidy
ones because deliberately-unlocked relationships are first-class here.

Entries are named for what you HEAR, not as note values. "every 4 beats" means
one cycle spread across four beats (multiplier 0.25) — deliberately *not*
written `1/4`, which everywhere else means a quarter NOTE and would sit at the
opposite end of the scale. "phi slow" is x0.618, "phi fast" is x1.618.

**Waveform** `Sine / Triangle / Saw / Golden TS / Golden SG / Golden GS / Bell / Wavefold / Half-sine / Phi-cascade / Phi Triangle / Phi Sine`
Same set as Polyrhythm Phase — see that plugin's Waveform section for descriptions. Half-sine sounds an octave higher than the others at the same note (its full-wave-rectified spectrum has no fundamental).

**Tuning Reference Hz** `400 – 480` (default 440)
Frequency of A4. Standard concert pitch is 440.

**Root Note** `C / C# / D / D# / E / F / F# / G / G# / A / A# / B` (default C)
The base note the whole instrument is built on. **This transposes every voice's Note together.** The per-voice Note picker (below) shows note *names*, and those names are literal only when Root Note is **C** and Center Octave is **4** — the picker is really a semitone offset from Root + Center dressed up as a note name (the same pitch system v1 used, just displayed more readably). Move Root Note to D and every voice shifts up two semitones from what its label says.

**Center Octave** `0 – 8` (default 4)
Octave of the root. With Root Note C + Center Octave 4, the picker's "C4" plays a true C4 (at default tuning). Raising Center Octave shifts every voice up an octave, and so on.

**Loop** `Off / On`
On wraps from the last active voice back to the first; off plays one pass and stops.

**Master Gain dB** `-60 – 0`
Output level for the whole plugin.

**Binaural Beat Hz** `0 – 100`
Hz offset added to the right-channel oscillator only. 0 disables it and the plugin sums to mono.

**Attack % of Note duration** `0 – 100`
Fraction of each voice's Note duration taken by the attack ramp.

**Release % of Note duration** `0 – 100`
Fraction taken by the release ramp. If Attack% + Release% exceeds 100%, both scale proportionally to fit.

**Attack Shape / Release Shape** `Linear / Cosine / Logarithmic / Exponential`
Curve of the attack / release ramps. Cosine is smoothest perceptually; Linear is the most "musical-instrument-like."

**Sequence Length** `All Active / 1 / 2 / 3 / 4 / 5 / 6 / 7 / 8`
How many voice slots participate. "All Active" walks all 8, skipping any with Active = Off; a numeric setting truncates to the first N slots (still skipping inactive ones within that range).

### Voices — the Voice selector and the five per-voice controls

This is the block that changed in v2. Instead of forty flat sliders, there's one **Voice** selector and five controls that edit whichever voice it points at.

**Voice (which voice the controls below edit)** `1 – 8`
The editing cursor. Set it to the voice you want to work on; the five controls below then show and edit that voice's settings. Moving it to another voice banks the current one and loads the next. **It does not mute anything** — all eight voices play in the sequence regardless of which one is selected here. Each voice's five settings persist independently across project save and reload.

**Note (selected voice)** `C2 – C6` (default C4 for voice 1)
This voice's pitch, chosen by name. As noted under **Root Note** above: the names are literal at Root Note C / Center Octave 4, and Root Note + Center Octave transpose the whole set together (internally it's a semitone offset with C4 as zero — the same relative pitch system v1 called "Semitones from root," shown here as note names). The eight voices' defaults spell a C-major-ish set, matching v1's starting arpeggio.

**Next voice in (cycles) (selected voice)** `0.01 – 16`
How long until the sequencer hands off from this voice to the next active one, in cycles of the global rate. Controls *sequence timing* — when the next voice starts. This voice's own note may ring past the handoff (overlap) or end before it (rest), per Note duration below.

**Note duration (cycles; 0 = silent) (selected voice)** `0 – 16`
How long this voice's note actually sounds, in cycles — independent of sequence timing:
- **Note duration < Next voice in** → silence between this voice ending and the next entering (a rest).
- **Note duration = Next voice in** → clean sequential handoff, no overlap, no rest.
- **Note duration > Next voice in** → this voice's release continues while the next plays (overlap / phrasing).
- **Note duration = 0** → a silent step (rest) of length "Next voice in," click-free on entry and exit.

**Gain dB (selected voice)** `-60 – 6`
This voice's level.

**Active (selected voice)** `Off / On`
Off = this voice is skipped in the sequence entirely (not just silent — the sequencer acts as if it isn't there). On = it participates per the Sequence Length rule.

### Pan

Mirrors Polyrhythm Phase's pan section. When enabled, each voice gets independently-positioned L and R amplitudes; the binaural beat is preserved because each channel keeps its own oscillator.

**Pan Enabled** `Off / On` (default Off) — toggles the whole group; off sums to mono.
**Pan Mode** `Tremolo / Increment / Spread / Spread Reversed` (default Spread) —
- **Tremolo** — each voice's pan oscillates over time at Pan Base Rate (shared rate).
- **Increment** — each voice's pan rate is Base Rate + (voice index × Increment), so voices drift in and out of phase.
- **Spread** — voices get static positions ranked across the field (V1 one end, V8 the other, active voices only). **Most useful for melodies** — each note lives in a distinct spatial spot.
- **Spread Reversed** — Spread, flipped; pairs with a second instance on Spread for width.

**Pan Spread %** `0 – 100` — how wide (100 = full stereo, 0 = center).
**Pan Base Rate** `0.001 – 1000` (Tremolo / Increment only) — pan LFO rate, in the global Rate Mode units.
**Pan Increment per Voice** `-1000 – 1000` (Increment only) — how much each successive voice's pan rate increases.

### Glide / portamento

**Glide time (seconds; 0 = off)** `0 – 5`
When > 0, each new voice's pitch starts at the previous voice's target and slides to its own over this many seconds. 0 = voices jump directly to pitch. Independent of all other timing.

**Legato glide** `Off / On`
- **Off** (default) — each voice has its own attack and release; glide bends pitch *during* each note. Good for plucky / articulated melodies.
- **On** — the whole sequence becomes one continuous tone whose pitch slides between voices. The first note attacks normally; every hand-off after inherits the previous voice's envelope value and oscillator phase (no re-attack), pitch sliding via glide; the last note (Loop Off) releases normally. Per-voice Note duration is effectively ignored — voices ring until the next takes over. Rests still work via Active = Off. Set Glide time > 0 to actually hear the slide.

### Start Delay

**Start Delay (in Rate Mode units)** `0 – 1000` (default 0)
How long the plugin sits silent at the start of playback before the sequencer begins. Units match Rate Mode. During the delay the sequencer stays frozen at its start position, then begins cleanly from the first active voice. Re-arms on every transport stop/start. 0 disables it.

### Direction

**Direction** `Up / Down / Up-Down (repeat) / Up-Down (no repeat) / Down-Up (repeat) / Down-Up (no repeat)` (default Up)
Walk order through the active voices in the pool (the first *Sequence Length* slots; inactive voices skipped in all directions).
- **Up** — V1, V2, …, loop to V1 (default).
- **Down** — reverse slot order, loop to the top.
- **Up-Down (repeat)** — walk up, play the top voice twice at the turnaround, walk back down, play the bottom twice, repeat.
- **Up-Down (no repeat)** — same bounce, boundary voices play once.
- **Down-Up (repeat) / (no repeat)** — the same two bounces starting from the top.

With **Loop = Off**, Up/Down play one pass and stop; bounce modes play one complete bounce cycle and stop. Glide, Legato, and mid-playback direction changes all behave as you'd expect (the flip lands at the next hand-off, no glitch).

### Play / Rest Gating

**Play for (steps)** `0 – 1000` (default 0) · **Rest for (steps)** `0 – 1000` (default 0) · **Rest mode** `Walk through / Freeze in place` (default Walk through)

A per-step cyclic gate: the sequencer fires **Play for** notes, sits silent for **Rest for** steps, then resumes — forever. Useful for phrase-and-pause melodies. **Disabled when either Play for or Rest for is 0** (the default). Each "step" is one voice's "Next voice in" period; programmed rests (Note duration 0) still count as steps.

- **Walk through** (default) — the sequencer keeps advancing silently through the rest; each rest step consumes that voice's "Next voice in." If Play + Rest doesn't divide evenly into the active-voice count, the starting voice of each play period walks across the melody. Good for abstract / drone-friendly use.
- **Freeze in place** — the sequencer pauses on the voice that would have fired when rest began; rest lasts `Rest for × that voice's "Next voice in"`, then it fires and the sequence continues. **No notes lost — every voice plays in order across cycles, just with pauses between phrases.** Good for melodic / phrasal use.

Rest duration is the same wall-clock time in both modes. Tails finish naturally (in Legato mode the sustaining voice is forced into release at the rest boundary so it doesn't ring forever). Changing Rest mode mid-rest is handled defensively but not gracefully — flip it during a play period, or stop/play to reset cleanly.

### Speed Ramp (multi-target, selector-first)

A **one-time signed-delta ride** on any target over a set duration — the in-plugin substitute for a REAPER automation envelope, the "wind down / wind up once" move (vs Drift's endless wander). Reaches all 28 targets (Rate Value, V1–V8 Timing, Pan Rate, V1–V8 Gain, V1–V8 Note dur, Attack %, Release %), each on its own timeline, via the suite's nested-selector pattern.

**Speed ramp target** — which parameter this ramp acts on (same list as Drift). Switching it saves the three per-target sliders into the old target's slot and loads the new one's; all 28 ramp in parallel.
**Speed ramp by** `-1000 – +1000` (units match target) — signed delta the target moves by over the duration, then holds. 0 = no ramp for that target.
**Speed ramp duration (minutes)** `0 – 60` · **Speed ramp start delay (minutes)** `0 – 60` — per-target; each waits its delay then rides its `by` over its duration, so different targets wind down on different timelines from one engage.
**Speed ramp engage** `Off / On` — **GLOBAL**. One switch arms every configured target; a freeze/resume gate (Off freezes each clock, On resumes). Every ramp's progress resets on the transport play edge.

Granularity mirrors Drift: rates convert to a mode-aware ratio; per-voice Timing / Gain add per sample; the articulation targets (Note dur, Attack %, Release %) sample once per note at trigger so a ringing note's length/shape stay fixed. Speed Ramp and Drift compose on the same target.

### Drift (nested-selector)

Slow organic wander applied independently to any of **28 targets** — the full expressive surface of a phrase: timing (rubato), dynamics (per-voice swell), and articulation (note length, onset/tail softness), each on its own slow schedule, the way a live player phrases rather than a loop repeats. Each target has its own config; all 28 drift in parallel; the selector chooses which one you're editing.

**Drift target** (28 options, default Rate Value) —
- **Rate Value** — wanders the global rate; stretches the whole timeline together.
- **V1–V8 Timing** — wanders each voice's step length ("Next voice in"); the rhythm breathes.
- **Pan Rate** — wanders Pan Base Rate (Tremolo / Increment only).
- **V1–V8 Gain** — wanders each voice's volume per-sample; the line swells and recedes (the core "breathing" axis).
- **V1–V8 Note dur** — wanders each voice's Note duration; articulation drifts between legato and staccato (sampled once per note).
- **Attack % / Release %** — wander onset and tail softness (sampled per note).

**Drift up / down amount** (units match target) — how far above / below baseline it wanders; asymmetric supported; either non-zero activates drift for that target.
**Drift period (cycles)** `1 – 1000` (default 8) — global rate cycles per full wander wave.
**Drift shape** `Sine / Triangle / Random` — wander waveform.

Rate, Timing, Pan Rate, and Gain drift continuously (per sample); Note dur / Attack / Release are sampled once per note at trigger so a ringing note doesn't move. On every transport play the drift phase and the whole sequencer reset; Drift config persists across stop/play and save/load.

## Usage Notes

**Building a melody.** Leave the voices Active, and walk the **Voice** selector 1→8, giving each a Note (the defaults spell a rough C-major set). Keep "Next voice in" = "Note duration" = 1 for a clean walk; vary "Next voice in" for rhythm and "Note duration" for phrasing.

**Adding rests.** Set a voice's "Note duration" to 0 — it still takes up its "Next voice in" as the rest length, silent and click-free.

**Overlap for sustain.** Set "Note duration" greater than "Next voice in"; the previous voice rings on through its release under the next note. With Release Shape = Cosine and a long Release %, that's a gentle decaying tail.

**Looping vs one-shot.** Loop = On for ambient / sleep loops; Loop = Off for a one-shot phrase that plays once and stops.

**Glide for pitch bends within notes.** Glide time > 0 with Legato Off: each note keeps its own attack/release and bends pitch during the note.

**Legato glide for one continuous bending tone.** Legato On + Glide time > 0: the classic monosynth portamento — one ongoing tone sliding smoothly between targets, no attack/release at boundaries.

**Spread pan for melodic clarity.** Pan enabled, Mode = Spread: each voice gets a fixed stereo position, so the line is easy to follow. Pair a second instance on Spread Reversed for width.

**Pairing with Polyrhythm Phase.** Both on separate tracks at the same Tuning Reference — Polyrhythm Phase as the drone bed, Melody Phase as the figure on top. Match Root Notes for consonance, or detune slightly for movement.

---

*Melody Phase v2 is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*
