# Planned features

Captured from a design session on 2026-05-25. Not yet implemented.
Pick this up when ready to code; all design decisions are settled.

---

## Polyrhythm Phase

### 1. Direction + Reverse Type

Two new sliders (at END of file per the slider-ID convention):

- **Direction** `[Forward | Reverse | Both]`
- **Reverse Type** `[Permute | Time]` — only matters when Direction != Forward

Five distinct behaviors:

| Direction | Reverse Type | Behavior |
|-----------|--------------|----------|
| Forward | (ignored) | Current behavior, 8 voices |
| Reverse | Permute | 8 voices, all per-voice settings internally swapped V1↔V8, V2↔V7, etc. — full permute, not just drift/rate |
| Reverse | Time | 8 voices, tremolo phase decrements instead of incrementing — whole soundscape plays in reverse time |
| Both | Permute | 16 voices: forward 8 + permute-reverse 8, layered |
| Both | Time | 16 voices: forward 8 + time-reverse 8, layered |

In Both mode:
- 16 voices total — memory layout already sized for 16 slots per bank per existing comments in `@init`; just need to use slots 8-15
- Reverse layer uses the same slider values as forward (no separate config — the whole point is "no manual adjustment")
- Pan uses same settings for both layers
- Mix at unity, no balance knob (existing Depth dB handles overall volume)

### 2. Start delay

One new slider:

- **Start delay** — units match Rate Mode (BPM beats / Seconds / Hz cycles)

Behavior:
- Plugin sits silent for N units after playback starts, then begins normally
- Re-arms on each transport stop/start — detect via `play_state` transitions
- Doesn't affect per-voice phase logic — just gates output

### 3. Play/Rest gating

Two new sliders:

- **Play for** — units match Rate Mode
- **Rest for** — units match Rate Mode

Behavior:
- Voices play normally for `Play for` duration
- Then output silent for `Rest for` duration
- Then voices resume EXACTLY where they were — phase counters frozen during rest, not reset
- Repeats forever
- During rest: audio output = 0, voice phase counters do NOT advance, all other state preserved
- When Play for=0 or Rest for=0: feature disabled, plugin plays continuously as today

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

- **Start delay on other rhythm plugins** — Shepard Scale, Shepard Tone, Full Feature Tremolo, Full Feature Sweeping Filter, Sweep Dwell Filter, Heartbeat Generator, Breath Generator, Womb Sound Generator. Add later when there's a concrete need; mechanically straightforward addition using the same pattern as polyrhythm/melody/rhythm-track.

- **"Rest between voices" macro for Melody Phase** — a pan-mode-style global mode + per-voice increment for automatic rest distribution across voices. The existing per-voice "Note rings for" + "Next voice in" sliders already cover the underlying mechanism (set Note rings for < Next voice in to get silence between voices); the macro would be a shortcut for setting up uniform rest patterns without going voice-by-voice. Needs its own design pass — what modes, override semantics, etc.

---

## Conventions to honor while implementing

- **All new sliders added at END of each .jsfx file** — preserves user slider state on existing plugin instances per CLAUDE.md's "primary keys" rule.
- **New sliders will appear at the bottom of the plugin UI panel** as a result — accept this UX trade for the project-stability it buys.
- **Per-plugin Start delay** could be implementable as a small shared pattern if multiple plugins gain it later (the deferred ones included).
- **Reverse Type and Bounce-variant labels** should hide when not applicable, similar to how existing conditional sliders work (e.g. Pan slider hiding when Pan Enabled = Off).
