# Planned features

Captured from a design session on 2026-05-25. Not yet implemented.
Pick this up when ready to code; all design decisions are settled.

## Slider budget per plugin

Modern Reaper JSFX supports `slider1` through `slider256`, so 64 isn't a hard limit — but staying at or under 64 keeps the slider IDs simple and matches the project's habit. After the additions below:

| Plugin | Pre-change | Landed | Remaining | Final total |
|---|---|---|---|---|
| polyrhythm_phase | 59 (highest `slider59`) | 3 (slider60 Direction & Reverse, slider61 Reverse Drift Offset, slider62 Start Delay) | 0 | 62 |
| polyrhythm_phase_loops | 62 (forked from polyrhythm_phase) | 2 (slider63 Play for, slider64 Rest for) | 0 | **64** (right at the line) |
| melody_phase | 61 (highest `slider61`) | 2 (slider62 Start Delay, slider63 Direction) | 0 | 63 |
| rhythm-track | 13 | 1 (slider14 Start Delay) | 0 | 14 |

The polyrhythm_phase budget is why Direction and Reverse Type were collapsed into a single 5-option slider (`Direction & Reverse`) rather than two — see section 1 below.

Play/Rest gating lives in `polyrhythm_phase_loops.jsfx` rather than the main plugin so the experimental gate work doesn't risk the stable polyrhythm_phase. The new file is a verbatim copy of polyrhythm_phase plus the gate sliders; both stay in sync as the engine evolves.

---

## Polyrhythm Phase

### 1. Direction & Reverse (single combined slider)

Originally drafted as two sliders (Direction = Forward/Reverse/Both, Reverse Type = Permute/Time, with Reverse Type hidden when Direction = Forward). Collapsed into one 5-option slider so the only valid combinations are the only options — no conditional hiding, and the slider budget stays at 64.

One new slider at END of file:

- **Direction & Reverse** `[Forward | Reverse — permute | Reverse — time | Both — permute | Both — time]`

Five behaviors:

| Option | Behavior |
|--------|----------|
| Forward | Current behavior, 8 voices |
| Reverse — permute | 8 voices. **Drift values** mirrored V1↔V8, V2↔V7, V3↔V6, V4↔V5. Notes, gains, phase offsets, active flags stay in place. |
| Reverse — time | 8 voices, tremolo phase decrements instead of incrementing — asymmetric envelopes play backwards |
| Both — permute | 16 voices: forward 8 (slots 0-7) + drift-mirrored reverse 8 (slots 8-15). Each note plays at two different cadences across the two layers. |
| Both — time | 16 voices: forward 8 (slots 0-7) + time-reverse 8 with same drift (slots 8-15). With asymmetric envelopes the reverse layer fills in the gaps of the forward layer's pulses, creating a drone. |

**Why "permute" mirrors only drift, not all settings.** The naive design (swap V1↔V8 across every per-voice slider together) is a mathematical no-op on the audio output: the audio sum is commutative across voice slots, so relabeling which slot holds which voice produces an identical waveform. Realised mid-implementation (May 2026) after the user A/B tested it and reported "permute sounds identical to forward." The user's mental model from the start was "swap just the cadence assignments" — which is what the code does now. Mirroring just `v_dr` makes the swap audible (V1's note now fires at V8's cadence and vice versa) and matches the user's diamonds.RPP workflow where drift palettes were the differentiator between paired tracks.

In Both modes:
- 16 voices total — memory layout already sized for 16 slots per bank per existing comments in `@init`; just need to use slots 8-15
- Reverse layer derives its per-voice settings from the forward layer (no separate config — the whole point is "no manual adjustment")
- Pan uses same settings for both layers
- Mix at unity, no balance knob (existing Depth dB handles overall volume)

### 1b. Reverse Drift Offset — LANDED

Slider 61. `<-1000, 1000, 0.001>` default `0`. Visible only when Direction & Reverse is set to a Both mode (`slider_show(slider61, is_both)`).

Adds a constant to every value in the reverse layer's Drift / Rate palette. Applied in @slider after the optional drift mirror, before the v_trem_freq computation. With offset = 0 the two layers run at matched cadences (mirrored in Both — permute, identical in Both — time). Non-zero values shift the reverse layer's drift range away from the forward layer's, breaking the lockstep.

**Why this exists.** Validated against `E:\reaper\diamonds (0.5).RPP` (2026-05-25), where the user stacks four polyrhythm_phase tracks per scene: each pair shares notes, octave, waveform, tuning, binaural, gain, and per-voice semitones — the ONLY difference between the two tracks of a pair is the drift palette range. Track 1's drift is 0.00 → 0.35 (ascending, +0.05 step); track 3's drift is 1.55 → 1.20 (descending, −0.05 step). The descending pattern is the drift values mirrored (V1↔V8 in drift only) plus a +1.20 offset. Same math collapses the descending1 pair with offset 0.40.

With Both — permute + offset 1.20 (or 0.40 for the other pair), one plugin instance produces what two stacked tracks used to. The descending2 and descending1 pairs in diamonds still need separate instances because they differ in notes / octaves / gain ramps — those are genuinely independent and Both mode doesn't collapse them.

**Why hidden in single-layer modes.** In Forward / Reverse — permute / Reverse — time there's only one layer, so adding a constant to every drift value is mathematically identical to nudging the global Rate Value slider. A duplicate control would just confuse — hiding is the right call.

### 2. Start delay

One new slider:

- **Start delay** — units match Rate Mode (BPM beats / Seconds / Hz cycles)

Behavior:
- Plugin sits silent for N units after playback starts, then begins normally
- Re-arms on each transport stop/start — detect via `play_state` transitions
- Doesn't affect per-voice phase logic — just gates output

### 3. Play/Rest gating — moved to `polyrhythm_phase_loops.jsfx`

The Play/Rest feature has been spun out into a sibling plugin to keep `polyrhythm_phase.jsfx` stable while the gate design is still being refined. See the new section below.

---

## Polyrhythm Phase Loops (sibling plugin — IN PROGRESS)

`src/polyrhythm_phase_loops.jsfx` — full fork of polyrhythm_phase plus a Play/Rest gate. Two sliders at the end of the file:

- **Play for (cycles)** — slider63
- **Rest for (cycles)** — slider64

Sliders are integers (step 1) interpreted as **per-voice cycle counts**. Each voice counts its OWN cycles, so V8 (high drift) hits its play threshold sooner in real time than V1 (drift 0) and enters rest first. The rest counter advances at the same per-voice rate, so V8 also wakes first — preserving per-voice cadence symmetry through both halves of the loop. Disabled when either slider is 0.

**Implementation notes (landed):**

- Per-voice counter at memory slot 304 (`v_pr_cycle[i]`) advances at `v_trem_freq[i] / srate`. Same value drives both play and rest thresholds.
- Normalizer divides by precomputed `total_active` (set in `@slider`) rather than the per-sample currently-audible count — keeps surviving voices' level steady when other voices enter rest. (Was a pre-existing latent bug; only became audible once voices started dropping in/out of rest.)
- **Depth-floor cancel on the final release.** On the final cycle of every play period, the always-on Depth term (`amount`) is dropped from the gain formula during the release portion of the LFO. So during that final release, gain = `lfo_val * (sc + amount)` instead of `lfo_val * sc + amount` — it starts at the same peak (when `lfo_val = 1`) but decays all the way to 0 (when `lfo_val = 0`) instead of bottoming at the Depth floor. The voice glides to actual silence before the rest freeze regardless of the user's Depth setting. Cycles 1 through (Play for - 1) play with the normal formula — only the final release shape changes.
- **Conventional transport.** No `ext_noinit`, no transport-edge reset logic, no "loops paused" freeze. `@init` runs on every transport play (Reaper default), which re-zeros voice phases, gain smoothers, Start Delay counter, per-voice cycle counters, and resting flags. Stop/play gives a clean restart — the gate begins a fresh play period from voice cycle 0 on every press. Same behavior as polyrhythm_phase.

**Caveat — Release = 0%.** The Depth-floor cancel only fires during the release portion of the LFO. With Release = 0% there is no release portion (zero width), so the override never fires and you get a sharp cutoff at the rest boundary. For a clean rest entry, use a non-zero Release setting.

**Wake side is intentionally untouched.** On wake from rest, the voice resumes a fresh ring from wherever its frozen `trem_phase` left off (typically near `on_frac` after the depth-floor-cancel release brought it to silence). With Attack = 0% the first ring after wake re-attacks at full peak — depending on settings, this can be heard as an attack click. Not addressed yet; revisit if it bothers in practice.

**Rejected alternatives:**

1. **Slower rest-fade smoother.** Bolt a longer time-constant onto the smoother for rest entry. Felt like a band-aid — cushioned the drop without addressing the underlying "LFO doesn't reach silence" issue.
2. **Settings-only (Depth = 0 + Attack > 0 + On Duration < 100%).** Discarded as primary fix because it pushed the burden onto user settings. Still valid as a sound-design tip in the manual.
3. **Per-cycle fade shoulders.** First-cycle fade-in + last-cycle fade-out applied as a multiplier on top of the normal LFO. Tried briefly (commit `080f505`, since reverted). Ate two full cycles of the user's `Play for` count for fades and didn't match the "voice rings, then rests" mental model the user described.

Earlier worry about "drift collapse" from waiting for the cycle end turned out not to apply with per-voice rest counters: voices wake at different wall-clock times because V8's counter advances faster than V1's, so the polyrhythm cadence lives in the wake-time differences rather than in relative freeze phases.

---

## Melody Phase

### 1. Direction

One new slider (at END of file):

- **Direction** `[Up | Down | Up-Down (repeat) | Up-Down (no repeat) | Down-Up (repeat) | Down-Up (no repeat)]`

Six distinct behaviors (using 4 voices for examples):

| Mode | Sequence |
|------|----------|
| Up | 1, 2, 3, 4, 1, 2, 3, 4, ... (current behavior) |
| Down | 4, 3, 2, 1, 4, 3, 2, 1, ... |
| Up-Down (repeat) | 1, 2, 3, 4, 4, 3, 2, 1, 1, 2, 3, 4, 4, ... (boundary voices double) |
| Up-Down (no repeat) | 1, 2, 3, 4, 3, 2, 1, 2, 3, 4, 3, ... |
| Down-Up (repeat) | 4, 3, 2, 1, 1, 2, 3, 4, 4, 3, 2, 1, 1, ... |
| Down-Up (no repeat) | 4, 3, 2, 1, 2, 3, 4, 3, 2, 1, 2, 3, ... |

Interaction with existing settings:

- **Active voices skipped** in all directions (existing behavior preserved). If V2 is Off in a 4-voice setup, Up plays 1→3→4→1→3→4, Down plays 4→3→1→4→3→1, etc.
- **Sequence Length** slider defines the pool of voices (first N); Direction defines walk order through that pool. So Down with SeqLen=4 plays V1-V4 in order 4,3,2,1.
- **Loop=On**: all directions loop forever (Up loops as 1...8/1...8, Down loops as 8...1/8...1, bounce modes keep bouncing).
- **Loop=Off + Up or Down**: plays once and stops (existing behavior for Up).
- **Loop=Off + Up-Down or Down-Up (either variant)**: plays one complete bounce cycle then stops.
- **"Next voice in" slider**: always means "delay from this voice firing until the next firing event." Works naturally with all directions including the doubled boundary in repeat-mode bounce (V8's "Next voice in" applies twice in a row at the turnaround: once to schedule the repeat V8, once to schedule V7).
- **Glide/Legato**: glides between consecutive voices in whatever direction they're going; existing glide code reads the previous-voice frequency at each transition, so this should work with no glide-specific changes.

### 2. Start delay

Same as polyrhythm — one slider, units match Rate Mode, re-arms on transport stop/start.

---

## Rhythm Track

### Start delay

Same as polyrhythm and melody.

(No Direction feature — Rhythm Track is a metronome, not a sequencer.)

---

## Deferred for separate planning

Mentioned in the design session but explicitly deferred to keep current scope manageable:

- **~~Start delay on other rhythm plugins~~ — LANDED.** Shepard Scale, Shepard Tone, Full Feature Tremolo, Full Feature Sweeping Filter, Sweep Dwell Filter, Heartbeat Generator, Breath Generator, Womb Sound Generator all gained a Start Delay slider at the end of their slider lists. Generators use "silence during delay" (no audio output), effects use "pass-through during delay" (dry signal flows through unchanged) so the effect plugins don't accidentally mute the dry track when chained. Same internal-state-freeze rule as the synth plugins: phases / filter buffers / LFO state don't advance during the silent window. **Units inherit each plugin's natural rate concept** — initially shipped as universal seconds, revised after user feedback ("not everyone is measuring things in seconds"): Heartbeat / Womb / Shepard Scale use beats at their respective BPM sliders; Shepard Tone / Full Feature Tremolo / Full Feature Sweeping Filter match their Rate Mode (BPM/Seconds/Hz) the same way polyrhythm and melody do; Breath Generator and Sweep Dwell Filter keep seconds because they're phase-based (each phase duration is already an explicit seconds slider, so beats/cycles would have no natural referent).

- **"Rest between voices" macro for Melody Phase** — a pan-mode-style global mode + per-voice increment for automatic rest distribution across voices. The existing per-voice "Note duration" + "Next voice in" sliders already cover the underlying mechanism (set Note duration < Next voice in to get silence between voices); the macro would be a shortcut for setting up uniform rest patterns without going voice-by-voice. Needs its own design pass — what modes, override semantics, etc.

---

## Conventions to honor while implementing

- **All new sliders added at END of each .jsfx file** — preserves user slider state on existing plugin instances per CLAUDE.md's "primary keys" rule.
- **New sliders will appear at the bottom of the plugin UI panel** as a result — accept this UX trade for the project-stability it buys.
- **Per-plugin Start delay** could be implementable as a small shared pattern if multiple plugins gain it later (the deferred ones included).
- **Bounce-variant labels** (Melody Phase Direction) read straight off the 6-option slider — no conditional hiding needed, the only invalid combinations are absent from the option list. Same principle as the collapsed Direction & Reverse slider on polyrhythm_phase.
- **Reverse Drift Offset** is visible in all modes including Forward (where it does nothing). Hiding it only when Direction = Forward is fine too if it feels cleaner during implementation — the existing `slider_show()` pattern handles the conditional cleanly.
