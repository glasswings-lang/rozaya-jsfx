# Shepard Scale Generator

**Designed by Rozaya — Developed with Claude (Anthropic)**

---

## Overview

Shepard Scale Generator is a step sequencer that produces the Shepard scale auditory illusion — a chromatic sequence in which each successive note sounds higher than the last, yet after twelve steps the sequence arrives back where it started with no sense of having moved. Each note in the sequence triggers a stack of octave-spaced oscillators shaped by a bell-curve amplitude window, so the pitch class is clearly defined but no single octave dominates.

The plugin generates no audio from an input signal. It is a pure synthesizer.

---

## Signal Architecture

The sequencer steps through up to twelve chromatic notes (C through B) at a rate set by the BPM parameter. On each beat, the active note's oscillator stack is triggered with an envelope shaped by the Attack, Release, and Note Length parameters. Each note has twelve oscillator slots, one per possible octave layer. The number of active layers is set by Octave Count, and their amplitude is shaped by a cosine bell curve centered on Center Octave — oscillators near the center are loud, oscillators near the edges fade toward silence. This bell shaping is what creates the illusion: the ear perceives the pitch class clearly but cannot anchor to a specific octave.

All active notes are summed and normalized by the oscillator count each sample.

---

## Parameters

### Global Controls

**BPM** `10-300 BPM, default 120`
The tempo of the sequence in beats per minute.

**Direction** `Asc / Desc`
The order in which notes are stepped through. Ascending moves C → C# → D → ... → B → C. Descending moves in reverse.

**Inactive Notes** `Skip / Rest`
Determines how notes with Active set to Off are handled.
- **Skip** — inactive notes are skipped entirely; the sequencer advances to the next active note immediately.
- **Rest** — inactive notes hold silence for their full beat duration before advancing.

**Attack %** `0-100%, default 10`
The fraction of each beat spent fading the note in from silence. At 0% the note begins at full amplitude immediately.

**Release %** `0-100%, default 10`
The fraction of each beat spent fading the note out. At 0% the note cuts off at the end of its on-time without fading.

> If Attack % + Release % exceeds 100%, both are scaled down proportionally to fit.

**Note Length %** `1-100%, default 100`
The fraction of each beat during which the note is present. At 100% the note occupies the full beat. At 50% the note plays for the first half of the beat then falls silent for the second half.

**Octave Count** `2-12, default 8`
The number of oscillator layers stacked per note, and the width of the pitch window in octaves. Higher values produce a richer, more ambiguous pitch quality; lower values sound thinner but more distinct.

**Center Octave** `0-8, default 4`
The octave at the center of the amplitude bell curve. Oscillators nearest this octave are loudest; those further away fade toward silence at the window edges. Adjusting this shifts the perceived register of the entire sequence.

**Waveform** `Sine / Triangle / Saw / Golden TS / Golden SG / Golden GS / Bell / Wavefold / Half-sine / Phi-cascade / Phi Triangle / Phi Sine`
The oscillator waveform used by all notes simultaneously. Sine is the cleanest choice for the Shepard illusion — additional harmonics can muddy the perceived register-wrap. The richer waveforms (Bell, Phi-cascade, etc.) are still available if you want the illusion to sit inside a more textured tone. See Polyrhythm Phase for waveform descriptions, including the back-compat note on the Golden / Phi family.

**Binaural Beat Hz** `0-100 Hz, default 0`
Offsets the right channel oscillator frequencies by this many Hz, adding a binaural beat across all notes simultaneously.

**Tuning Reference Hz** `400-480 Hz, default 440`
The A4 reference frequency used to calculate all note pitches.

---

### Per-Note Controls (C through B)

Each of the twelve chromatic notes has three parameters.

**Active** `Off / On`
Enables or disables this note in the sequence. When off, behavior depends on the Inactive Notes setting. The gain and pan controls for this note are hidden when inactive.

**Gain dB** `-60–+6 dB, default 0`
Volume of this note relative to the others. Allows individual notes to be emphasized or de-emphasized within the sequence. Hidden when the note is inactive.

**Pan** `-100–+100, default 0`
Stereo position of this note. Negative values place it left, positive values right, 0 is center. Uses constant-power panning. Hidden when the note is inactive.

### Start Delay

**Start Delay (beats)** `0–1000, default 0`

Silent for N beats after playback starts, then the scale begins normally. Beats are counted at the BPM slider (the same slider that sets the note pacing) — at 60 BPM, "4 beats" is 4 seconds; at 120 BPM it's 2 seconds. Oscillator phases and note-step state stay frozen during the delay so the first note of the scale lands cleanly at delay-end. Re-arms on every transport stop/start. 0 disables the delay.

### Play / Rest Gating (v2.1)

**Play for (beats)** `0–1000, default 0`
**Rest for (beats)** `0–1000, default 0`
**Rest mode** `Walk through / Freeze in place, default Walk through`

A per-beat cyclic gate. The scale fires **Play for** notes normally, then sits silent for some number of beats determined by **Rest for** + **Rest mode**, then resumes — the pattern repeats forever. Useful for phrase-and-pause scale playback or contemplative gaps between rising / descending phrases.

The feature is **disabled when either of Play for / Rest for is 0** (the default). With both at 0, the scale behaves as before; Rest mode has no effect when the gate is off.

**Rest mode** picks one of two fundamentally different behaviors for what the sequencer does during the rest period:

- **Walk through** (default): the sequencer keeps advancing through notes during rest. Each rest beat moves the current note forward silently. If `Play + Rest` doesn't divide evenly into your active-note count, the starting note of each play period walks across the scale — `Play=4, Rest=4` with all 12 notes active means cycle 1 plays C–D#, cycle 2 plays G#–B, cycle 3 plays E–G, and you return to C after three cycles. Notes get "skipped" in the literal sense (the sequencer walks past them silently); they reappear in subsequent play periods at different positions. Good for **abstract / pattern-shifting use** where the walking-start effect is part of the appeal.
- **Freeze in place**: the sequencer pauses on the note that would have fired when rest began. Rest duration is `Rest for × one beat (60/BPM seconds)`, timed by a sample counter rather than a beat count. When rest ends, the frozen note fires and the scale continues from there — **every note plays in order across multiple cycles, just with pauses between phrases**. Good for **complete-scale-with-rests use** where you want to hear every step of the Shepard illusion in order.

**Tails finish naturally.** When PR transitions to rest, the previously-firing note's beat envelope continues to decay via the per-note smoother (the same one that already smooths the crossfade between notes). No special anti-click logic is needed — the existing envelope smoothing handles the transition.

**Inactive Notes + Play/Rest interaction.** In **Skip mode** (the default for Inactive Notes), inactive notes are jumped past, so "one beat" always equals "one active-note step." In **Rest mode** for Inactive Notes, inactive notes consume their full beat silently — they still count as a Play/Rest step. So with Inactive Notes = Rest and some notes inactive, Play for = 4 may include a couple of silent-anyway beats within the audible 4-note phrase.

**Transport behavior**: conventional. Stop silences; play re-initializes everything (sequence position, beat phase, period counter, rest state) and starts fresh from the first beat of seq_pos = 0 (C).

**Changing Rest mode mid-rest** is handled defensively but not gracefully — the safest move is to flip the slider while the gate is in its play period, or to press stop/play to reset cleanly. The plugin won't crash but the current rest period may stretch or compress unexpectedly.

### Ramp (v2.14 nested-selector)

In-plugin one-time morph over time, without automation envelopes. As of v2.14 Ramp is nested-selector (same shape as Drift) and reaches the **same four targets as Drift** — BPM, Note Length %, Attack %, Release %. It is **fully per-target**: each target has its own `by`, its own duration, and its own start delay, so different targets can wind down over different timelines from a single engage. Only **engage** is global.

**Ramp target (slider 52)** `Tempo / Note Length % / Attack % / Release %, default Tempo`
Picks which target the `by`, duration, and start delay sliders are currently editing. Switching the selector saves those three into the old target's memory slot, then loads the new target's stored values. Sits at the top of the Ramp block (above the controls it governs) — a v2.14 reorganization; see the migration note below.

**Ramp by (slider 53)** `-300 to +300, step 0.1, default 0` (units match the selected target)
Signed delta in the selected target's own unit, applied over that target's duration. **0** = no change (safe default). For **Note Length / Attack / Release** it's in percentage points. The wide ±300 range is headroom shared across targets — only the target's own sensible span is meaningful (e.g. a note-length ramp beyond ±100 is clamped).

For **Tempo** the delta is in **BPM**, in every Rate Mode (`-60` ramps 120 → 60).

In **Host x** the delta stays in this plugin's own unit — it does **not** become a multiplier. That means a ramp does not stretch when the project tempo changes: `-60` is `-60 BPM` whatever the tempo does. That's a deliberate limitation. The alternative was tried and rejected: these amount sliders step in 0.1, a grain chosen for BPM, and in multiplier terms 0.1 is a 10% wander with nothing finer reachable — so the value you'd actually want stops being settable.

**Ramp duration (slider 54)** `0–60 minutes, default 0` — **per-target.** How long the *selected* target takes to travel from baseline to baseline + `by`. Each target has its own; a target with duration 0 does not ramp (set a duration for every target you want to move). · **Ramp start delay (slider 56)** `0–60 minutes, default 0` — **per-target.** Wait this many minutes after engage before *this* target begins moving (stagger targets by giving them different delays). · **Ramp engage (slider 55)** `Off / On, default Off` — **global.** One switch arms the whole wind-down; each configured target then rides its own duration after its own start delay.

Engage is a freeze/resume gate (NOT a restart edge): while On, each target's clock advances 0 → 1 over its duration; while Off, all clocks freeze and resume on re-engage. The Freeze-mode Play/Rest rest timer scales with the BPM ramp so rest duration tracks the same effective tempo as the play period.

Example (one engage): BPM `by -40`, duration 20 min, delay 0; Note Length % `by -30`, duration 5 min, delay 8 min → the tempo eases down over 20 minutes while note length holds, then shortens over its own 5-minute glide starting 8 minutes in.

**Transport behavior:** every target's ramp clock resets to 0 on the transport play edge (via `@init`). That is the ONLY thing that resets the ramps — slider changes (engage toggle, selector switch, anything) don't.

**Migration to v2.14 (reorganization + renumber):** Ramp went multi-target and the block was reorganized so the target selector reads *above* the by/duration/engage controls it governs. Because REAPER orders sliders by ID (not file position), this required renumbering the Ramp block (now sliders 52–56) and the Drift block (now sliders 57–61). **Existing Shepard Scale projects lose their Ramp and Drift settings on upgrade** — both are off-by-default, and the scale sound itself (sliders 1–51) is untouched. Re-add the plugin instance for clean defaults, or re-enter your Ramp / Drift settings. *(Older history: pre-v2.14 Ramp was single-target BPM on slider 52; and pre-v2.8 it was a multiplier 0.1–4.0.)*

### Drift (v2.9 nested-selector)

Slow organic wander applied independently to any of four targets: BPM, Note Length %, Attack %, or Release %. Each target can have its own drift configuration; all four drift in parallel. The selector chooses which target's drift you're currently editing — the others keep running with their last-saved configuration.

Same pattern as Womb v3's drift and the matching block in Heartbeat / Breath Generator. Switching the **Drift target** selector saves the current sliders 58-61 into the old target's memory slot, then loads the new target's saved values. All four configurations persist across project save/load.

For slow wall-clock-feel drift, set a long period (~960 beats ≈ 8 min at 120 BPM). The old v2.8 "musical vs slow" split is gone — there's a single period unit (beats, paced by the BPM clock), and you express the timescale you want with the period value.

**Drift target (slider 57)** `Tempo / Note Length % / Attack % / Release %, default Tempo`
Picks which target's drift configuration sliders 58-61 reflect. Switching the selector saves and loads automatically — no live edits are lost.

**Drift up amount (slider 58)** `0.0–100.0, default 0` (units match target)
How far above the target's baseline the drift wanders at its peak. Units are BPM for BPM, % for Note Length / Attack / Release. 0 = drift off on the up side. Note that going much above ±20 BPM on the BPM target will sound dramatic — typical musical use is 5–15 BPM.

**Drift down amount (slider 59)** `0.0–100.0, default 0` (units match target)
How far below the baseline the drift wanders at its trough. Independent from Up — asymmetric wander supported. Either non-zero activates drift for the target; both 0 = drift off.

**Drift period (slider 60, beats)** `1–1000, default 8`
How many beats one full drift wave takes for this target. Short = jittery, long = barely-perceptible wander. Period scales with Ramp's tempo offset so the wave-per-beat relationship stays constant under wind-down.

**Drift shape (slider 61)** `Sine / Triangle / Random, default Sine`
Wander waveform. Sine = smooth, Triangle = linear ramps with turnarounds, Random = value-noise interpolating smoothly between fresh random targets at each period boundary.

#### Transport behavior (v2.9)

On every transport play press, drift cycle restarts: all 4 targets' phase counters → 0 (drift offset = 0 at the first sample, wanders out from there). Sequencer also resets to first note + clean envelopes + oscillator re-init. Drift CONFIG (up/down/per/shape values per target) is preserved across stop/play and across project save/load. Ramp progress also resets on transport play. This makes renders deterministic for Sine and Triangle shapes (Random remains non-deterministic per render by design).

#### Migration from v2.8

The old flat-drift block (musical_up/down/period, slow_up/down/period, drift_shape on sliders 56-62) was 7 sliders covering BPM only. v2.9 is 5 sliders covering 4 independent targets, reusing slider IDs 56-60; sliders 61 and 62 are no longer declared. Old project values get reinterpreted (selector defaults to BPM; non-zero amounts on sliders 57-58 will produce drift on BPM). After upgrade, reset drift sliders to defaults if you'd never configured the old flat drift, or reconfigure under the new nested-selector pattern if you had.

---

## Usage Notes

- **The illusion depends on Octave Count and the bell window.** Too few layers (2-3) and individual octave jumps become audible. Eight or more layers produce the smoothest illusion.
- **Center Octave shifts register without changing pitch classes.** Lowering it pushes the perceived center of the sequence down; raising it pushes it up. The illusion remains intact.
- **Attack and Release are proportions of Note Length, not the full beat.** With Note Length at 50%, an Attack of 20% means the note spends 20% of its 50% window fading in — 10% of the total beat.
- **Binaural beat applies uniformly across all notes.** There is no per-note binaural amount. For entrainment use, keep the value consistent with your target beat frequency.
- **Skip vs Rest affects rhythmic feel significantly.** With many inactive notes, Skip produces a sparse irregular rhythm; Rest maintains the underlying pulse with silences in place of notes.

---

*Shepard Scale Generator is part of the Rozaya JSFX plugin suite.*
*Designed by Rozaya — Developed with Claude (Anthropic)*


---


### Host tempo sync

**Rate Mode** `Own BPM / Host x` (default Own BPM)
**Own BPM** is the original behaviour — free-running, project tempo ignored.
**Host x** makes BPM a **multiplier of the project tempo** instead: x1 follows
it exactly, x2 is double speed, x0.5 half. Tempo changes apply live.

Only two entries rather than the four in Melody Phase / Polyrhythm, because
this plugin only ever had one unit — "Seconds" and "Hz" would be meaningless.

> **Switching modes changes what BPM means, and nothing rescales it.** Set the
> mode first, then the value — or use the picker below, which fills it in.

**Host ratio (writes BPM)** `Custom / every 8 beats / … / 8 per beat` (default Custom)
Shown only in Host x. Writes the multiplier and then gets out of the way, so you
can still type or automate anything. **Custom** never writes anything, and is
deliberately not called "Free" — in sync UI that means free-running, which Own
BPM already is. Entries are named for what you hear, not as note values.

---

#### Host x hands you the ratio list, not a multiplier

Switching Rate Mode to **Host x** lands on **1 per beat** and hides the raw rate number. The **Host ratio** list becomes the control you use — *every 8 beats, every 4 beats, 1 per beat, 2 per beat*, and so on — so setting a rate is picking a name, never working out a number.

Set Host ratio to **Custom** and the rate value reappears, with whatever it last held. That's the way in for ratios the list doesn't cover, which is most of the point of a multiplier rather than a note grid.

Two things this fixes. The rate slider's default was chosen for its own unit, so switching mode used to hand you a speed you never asked for — in the effects, a default of 2 meant *double time* the moment you selected Host x. And the picker sits at the far end of the parameter list (slider IDs can never be renumbered without scrambling saved projects), so you met the multiplier first and the cure last.

Landing on 1 per beat only happens when *you* change the mode. Opening a saved project leaves your rate exactly as you set it.
