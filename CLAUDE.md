# Rozaya JSFX plugin suite

A small collection of Reaper JSFX plugins for ambient, sleep, and entrainment audio. Public domain (CC0). Designed by Rozaya, developed iteratively with Claude.

## Layout

- `src/*.jsfx` — plugin source files (one per plugin).
- `docs/rozaya_jsfx_manual.md` — user-facing reference for every plugin and its parameters. **Update this whenever you change a slider or add a feature** — modders and players read it instead of the source.
- `LICENSE` — CC0.
- `README.md` — top-level overview.

## Active plugin under heaviest development

`src/polyrhythm_phase.jsfx` — drone synth, not a playable instrument. Up to 8 simultaneous voices, polyrhythmic tremolo with attack/release envelope, optional binaural beat, four pan modes (Tremolo / Increment / Spread / Spread Reversed), twelve waveforms, Direction & Reverse (5 modes), Start Delay, and Play/Rest gating (per-voice cycle counts, depth-floor cancel on final release for clean rest entry). Currently at v2 — see the `desc:` line in the file. Slider IDs 1-62 are bit-identical to v1; v2 added sliders 63 / 64 (Play for / Rest for) at the end with defaults of 0 (gate off), so any v1 project still opens unchanged.

## Project values to preserve

- **Public domain (CC0)** — no proprietary code, no copying from licensed sources. Original implementations only.
- **Gentle by default** — these plugins target sleep / ambient / entrainment use. Avoid harsh transients, aggressive transients, or designs that produce mono-cancellation artifacts on speakers. Mono compatibility matters because users play these on HomePods, phone speakers, etc.
- **Hand-editable text and JSON** — every slider has a sensible default in the spec; every text pool is plain-text with one entry per line. Modders are first-class users.
- **No new dependencies** — pure JSFX (eel2 syntax). No external libraries, no Reaper extensions.

## JSFX gotchas baked in from past sessions

- **Slider IDs are primary keys.** Reaper preserves slider VALUES by ID across file edits. Renumbering existing sliders scrambles user state — V1 Active ends up holding V2 Gain dB's value, which clamps to a different range and silently breaks things. **Always add new sliders at the END of the slider range, never in the middle.** If a player reports "everything is wrong after the update," the fix is usually `git status` + re-add the plugin instance for clean defaults.
- **Phase wrap discontinuity.** Any modulator computed as `sin(2π · k · phase)` where `k` is a non-integer (golden ratio, 2.4, 4.5, etc.) creates a discontinuity each time the carrier phase wraps. This shows up as a click at the fundamental rate. To use non-integer harmonics cleanly, you'd need a separate phase counter for the modulator (extra memory bank slot). For new waveforms, prefer integer harmonic multipliers (1, 2, 3, ...) unless you're willing to add the extra state.
- **The Golden TS / SG slots are NOT what the names suggest** — and this is deliberate now. Polyrhythm Phase originally shipped with slot 3 ("Golden TS") as a phi-warped *sine* (not triangle, despite the name), and slot 4 ("Golden SG") with an extra sine pre-warp before the phi-warp. Melody Phase initially implemented them strictly per their names (warp → triangle, clean warp → sine), which made the two plugins SOUND DIFFERENT for the same slot. Reconciled 2026-05-24: all four oscillator plugins (Polyrhythm Phase, Melody Phase, Shepard Scale Generator, Shepard Tone Generator) now offer the same 12-waveform palette at the same slot indices. Slots 3 / 4 / 5 match Polyrhythm Phase's original behavior (preserves existing project files); slots 10 ("Phi Triangle") and 11 ("Phi Sine") are the strict / manual-correct versions. Don't "fix" slot 3 to output a triangle — there are projects built on the sine sound. Shepard Scale + Tone gained the new slots 6–11 (Bell, Wavefold, Half-sine, Phi-cascade, Phi Triangle, Phi Sine) in this same change — they previously stopped at slot 5. **Convention going forward: any new waveform added to Polyrhythm Phase or Melody Phase should land in all four plugins at the same slot index.** Diverging waveform palettes between sibling oscillator plugins is exactly the inconsistency this sweep cleaned up.
- **Stop-sequence-style behaviors** don't apply here (no language model). What does apply: stay below 90° static L/R phase offset to avoid mono-cancellation on speakers; static phase offsets read as **lateralization** to the listener (ITD cue), not as width. True width without binaural beating requires either a) multi-voice unison with detune, b) chorus/ensemble effects with modulated delay lines, or c) all-pass filter networks. There's a session log of attempting (b) inside the plugin and reverting to "use Reaper's stock chorus AFTER the synth" — see git log around the pan-modes merge for context.
- **`@init` re-runs on every transport start by default.** This silently re-zeros all plugin memory (variables, arrays, oscillator phases, smoother states) on every press of the Reaper play button. Usually you WANT that (conventional Reaper "fresh start on play"), but if you ever need state to persist across stop/play (drift relationships, gate progression, accumulated phase positions), set `ext_noinit = 1;` at the top of `@init`. With that flag, `@init` only runs on actual plugin load and Reaper leaves memory intact at transport boundaries. Polyrhythm Phase v2 deliberately does NOT set this flag — the gate begins a fresh play period on every play press, matching v1 behavior. Documented at [reaper.fm vars.php](https://www.reaper.fm/sdk/js/vars.php).
- **`play_state` enumeration** (verbatim from official docs): `0 = stopped, <0 = error, 1 = playing, 2 = paused, 5 = recording, 6 = record paused`. There's no `3` or `4`. Common pitfall: `play_state == 0` alone misses the pause case — use `play_state == 0 || play_state == 2` if you want to gate "transport is not advancing." For "transport is actively moving" (regardless of mode) use `play_state == 1 || play_state == 5`. Transport-edge detection via `play_state != last_play_state` is more robust than the `play_state > 0 && last_play_state == 0` pattern (which only catches stop→play, not pause→play or play→pause).
- **Transport-edge detection belongs in `@block`, not `@sample`.** `play_state` updates per block, never mid-block, so polling in `@sample` is wasted work. Audio behavior is the same; it's a code-quality / performance note. (Polyrhythm Phase v2 doesn't currently poll play_state at all — `@init` running per-play covers the reset case without explicit edge detection. Noted here for future plugins that might.)
- **The active-voice normalizer is per-sample, and it bites you when voices drop out.** Polyrhythm Phase divides its summed output by the count of currently-audible voices each sample. When voices come and go (Play/Rest gate, future per-voice mutes, anything that silences some voices but not others) the divisor shrinks and the surviving voices get LOUDER — up to +18 dB when only one voice is still audible. Fix: divide by `total_active` (precomputed in `@slider` from `v_active` toggles), so the divisor is stable across runtime voice silencing. Polyrhythm Phase v2 has the fix; the Play/Rest gate exposes it, but the fix is correct for the engine generally and should be the pattern for any future plugin that can silence voices at runtime.
- **Empty `()` from a comment-only conditional branch breaks compilation silently.** JSFX strips comments at compile time, so this:

  ```
  pr_resting ? (
    // stay where we are
  ) : (
    breath_state = 0;
    state_len = inhale_len;
  );
  ```

  ...becomes `pr_resting ? ( ) : (...)` to the eel2 parser. Empty paren block is a syntax error. The plugin fails to compile, but Reaper doesn't always pop a visible error — symptom is just "no sound." Discovered 2026-05-26 while adding Play/Rest to Breath Generator (commit `a546fce` is the fix). **Workarounds:** either invert the conditional to a one-armed form (`!pr_resting ? (...);` — only the populated case runs), or put a no-op like `0;` inside the empty branch. Whenever you write a `cond ? (...) : (...)` where one branch is "do nothing," prefer the one-armed inverted form so the parser never sees an empty block.
- **Polyrhythm Phase voice memory layout** (16 slots each):
  - 0  osc_phase_l
  - 16 osc_phase_r
  - 32 trem_phase
  - 48 gain_l
  - 64 gain_r
  - 80 v_freq_l
  - 96 v_freq_r
  - 112 v_trem_freq
  - 128 v_active
  - 144 v_semitones
  - 160 v_dr (drift in Drift mode / rate in Independent mode)
  - 176 pan_phase
  - 192 pan_smooth
  - 208 v_pan_freq
  - 224 v_gain
  - 240 v_phase_off (last-known per-voice offset slider value)
  - 256 v_phase_off_last
  - 272 v_pan_static (target pan position for Spread / Spread Reversed modes)
  - 288 v_resting (per-voice Play/Rest flag: 1 = silent during rest, 0 = playing)
  - 304 v_pr_cycle (per-voice Play/Rest cycle counter, advances at the voice's own v_trem_freq)
  - 320 onward: free for new arrays.

## Adding a new waveform to Polyrhythm Phase

1. Update `slider14`'s option list at the top of the file. Range becomes `0,N,1` where N+1 is the new option count.
2. Add a new `: waveform == K ? (...)` branch in the `@sample` voice loop's waveform chain. Compute `osc_l` from `osc_phase_l[i]` and `osc_r` from `osc_phase_r[i]`. Multiply by `gain_l[i] * v_gain[i]` (and `gain_r[i]` for R).
3. Update `docs/rozaya_jsfx_manual.md` Waveform section with a one-line description.

## Adding a new slider to Polyrhythm Phase (or any plugin)

- Pick the next free slider ID at the end of the range (don't insert mid-list).
- Read it in `@slider` after the existing reads.
- Use `slider_show(sliderN, condition)` to hide it conditionally based on related sliders.
- If it persists state, decide whether it's a runtime tunable (don't persist) or saved per-instance.
- Document in the manual.

## Branches

- `master` — stable. Releases tag from here.
- `feature/*` — work in progress. Merge with `--ff-only` when ready (see git log for past examples).
- Don't work directly on master — use a branch and merge when validated by ear.

## Recent session notes worth knowing

- **Speed Ramp sweep across the suite** (2026-05-30, on `feature/rate-morph`, unmerged at time of writing). Every plugin gained an in-plugin slowdown/speedup feature designed for sleep wind-down — the user reported difficulty using REAPER automation envelopes via OSARA, and that manual rate-slider adjustments clicked on several plugins. Three new sliders per plugin (always at the end of the existing range): **Speed ramp target (multiplier)**, **Speed ramp duration (minutes)**, **Speed ramp engage (Off/On)**. Off → On captures the current `speed_scale_current` and ramps fresh toward target over duration; On → Off freezes at the in-flight position (does not reset to 1.0). Resets on transport play, like Start Delay + Play/Rest. Per-plugin implementation strategies vary because the rate semantics do:
  - **Frequency-like rate** (Heartbeat, Womb, Tremolo, Sweeping Filter, Sweep Dwell, Rhythm Track): multiply the effective frequency by `speed_scale_current` at the per-sample use site (`freq * speed_scale_current` or `samples_per_beat / speed_scale_current` etc.). Heartbeat, Tremolo, Sweeping Filter, and Womb additionally got a ~100 ms one-pole smoother between the rate slider and the audio to kill clicks on manual adjustment (`rate_smoother_coeff` + `freq_smoothed` / `bpm_smoothed`). Smoothed values are seeded from current slider values in @init so the first sample after transport-start uses the saved rate, not a default — important because @init re-runs on play.
  - **Period-like rate / state-machine plugins** (Breath, Womb's breath layer, Melody Phase, Shepard Scale): scale the state-pos increment by `speed_scale_current` (was `state_pos += 1`, now `state_pos += speed_scale_current`). For Melody Phase, `dt = speed_scale_current / srate` scales every per-sample time accumulation — sequencer + voice envelopes + pan modulation all stretch together so Attack %, Release %, Note duration proportions stay intact. For plugins with a Freeze-mode rest timer (Shepard Scale, Melody Phase, Womb breath), `pr_rest_elapsed += speed_scale_current` too so rest duration tracks effective tempo.
  - **Multi-voice / polyrhythmic** (Polyrhythm Phase, Shepard Tone): multiply each voice's per-sample phase advance and cycle counter by `speed_scale_current` at the use site. Single multiplier preserves the rate RELATIONSHIPS between voices — V1 at 60 BPM and V2 at 60.5 BPM both halve at scale=0.5, so the slow beat between them halves too.
  - **Womb scales ALL THREE LAYERS** (HB BPM, breath state, bloodflow which is locked to HB) from one Speed Ramp control — keeps the physiological coherence the plugin is built around.
  - **Audible pitch / tuning is never scaled.** Only modulation / sequencer / envelope rates. Oscillator frequencies, filter resonance centers, binaural beat, tuning reference all stay where the user set them.
  - **One commit per plugin.** Each commit message names the slider IDs it added and the implementation strategy in shorthand. Manual updated alongside the code (every plugin's section in `docs/rozaya_jsfx_manual.md` got a `### Speed Ramp (new)` subsection).
  - **Open work**: branch unmerged. Decisions before shipping: (a) merge to master with `--ff-only`, (b) tag (probably `v2.2`), (c) `gh release create` with the same note style as v2.0/v2.1. User to test by ear across all 11 plugins; per-plugin tweaks (different smoother time constants, different multiplier ranges if 0.1–4.0 isn't right, etc.) before merge.
  - **Pattern to reuse**: the universal Speed Ramp UI (3 sliders, identical names + semantics + behavior across the suite) is now a convention. New plugins added to the suite should include it.


- **Pan modes feature** added Spread + Spread Reversed (commit `b60e635`) — static pan positions ranking active voices across the stereo field. Bonus discovery: running two tracks of the synth, one with Spread + one with Spread Reversed at slightly different Tuning Reference Hz, produces a surprisingly rich stereo width effect via composition rather than DSP. Documented in the Pan section of the manual.
- **Per-voice docs fix** (commit `fb6199a`) — the manual previously listed Vn Note and Vn Octave as per-voice sliders; the actual sliders are Gain dB / Semitones / Drift-Rate / Phase Offset / Active. Also default Gain dB is -6 for V1 and -60 for V2-V8 (manual previously claimed default 0 for all).
- **Polyrhythm Phase v2 — Play/Rest gating** (2026-05-25, merged on `feature/polyrhythm-loops`). v2 adds sliders 63 (Play for) and 64 (Rest for), per-voice cycle counting (V8 paces ahead of V1), and a depth-floor cancel on the final cycle's release so the voice glides to actual silence before the rest freeze regardless of Depth dB setting. Iteration went through three approaches before landing: in-place edits to polyrhythm_phase (parked on `feature/play-rest-gating`, abandoned), a sibling plugin `polyrhythm_phase_loops.jsfx` while the cutoff thud was being worked out, then consolidated back into polyrhythm_phase.jsfx once the depth-floor-cancel approach proved solid in user testing. v1 project files open unchanged in v2 — the new sliders default to 0 which keeps the gate off, and slider IDs 1-62 are bit-identical. Also folded in: the `total_active` normalizer fix (latent bug in v1, exposed by the gate but correct for the engine generally).
- **v2.1 sweep — Play/Rest gating across the rest of the suite** (2026-05-26, on `feature/play-rest-everywhere`, unmerged at time of writing). Every plugin in the suite that has Start Delay now also has Play/Rest gating. Per-plugin commits in the branch log; consistent slider IDs / labels per family. Three different gate semantics by plugin type:
  - **Event-triggered synths** (Heartbeat, Breath, Rhythm Track): just `Play for` / `Rest for`. Gate at the event trigger site (don't fire new beats / ticks / breath-cycles while resting). Existing envelopes finish naturally.
  - **Sequencer synths** (Melody Phase, Shepard Scale): `Play for` / `Rest for` + `Rest mode` (Walk through / Freeze in place). Walk mode lets the sequencer walk through voices silently during rest; Freeze pauses the sequencer entirely and resumes from the frozen voice. Melody Phase Freeze uses a `simulate_rest_duration_seconds()` function to match Walk mode's wall-clock duration when voices have varied "Next voice in" timings (so the slider value means the same wall-clock time in both modes). Shepard Tone uses the same pattern but the unit naturally matches (single global rate).
  - **Effects** (Full Feature Tremolo, Resonant Sweeping Filter, Sweep Dwell Filter): `Play for` / `Rest for` + two orthogonal mode sliders — `LFO at rest` (Walk through / Freeze in place) and `Output at rest` (Pass-through / Silence). Four combinations of rest behavior. "Rest" doesn't silence the input by default (matches Start Delay's pass-through-during-delay convention for effects) but Silence mode is available when you want a hard mute. effect_mix smoother (3 ms) blends play-mode output with the rest target.
  - **Womb Sound Generator**: per-layer gates (six sliders, two per layer: Heartbeat / Breath / Bloodflow). Each layer's gate mirrors the design of its standalone sibling plugin. Bloodflow's gate uses `hb_phase` wraps as its tick (since BF is locked to HB), even when HB itself is gating beats out — so BF's counter advances on the underlying heartbeat clock, not the audible-beats clock. **Open question for next session**: whether to add per-layer Rest mode (Walk/Freeze) to Womb, or whether to change Bloodflow's tick semantic to "count only audible heartbeats." Both are reasonable; user chose simpler at v2.1 time.
- **JSFX gotcha — empty `()` from comment-only conditional branches** (commit `a546fce`, lessons-learned). Discovered while adding Play/Rest to Breath Generator: a `cond ? (...) : (...)` where one branch contains only comments resolves to an empty `( )` after comment stripping, which eel2 rejects. Symptom is "the plugin loads but produces no sound" — Reaper doesn't always pop a visible error. Workaround: invert to a one-armed conditional so the parser never sees an empty block. Also documented in the JSFX gotchas section above.
- **Open work after the v2.1 sweep** (as of `feature/play-rest-everywhere` tip):
  - Branch is unmerged. Decisions before shipping: (a) merge to master with `--ff-only`, (b) tag (probably `v2.1`), (c) `gh release create` with the same note style as v2.0.
  - The `feature/play-rest-gating` branch (Polyrhythm Phase v2's in-place attempt, abandoned) and `feature/polyrhythm-loops` (intermediate sibling plugin, since merged) are parked. Can be deleted whenever — they're historical records, no forward work expected on them.
  - Womb's open question above (per-layer Rest mode? change BF tick semantic?).
  - Per-cycle fade shoulders on Polyrhythm Phase (commit `080f505` on `feature/polyrhythm-loops`, reverted): if you ever want to revisit the "fade in / fade out around rest" idea for the polyrhythm plugin specifically (different from the depth-cancel approach that landed), the design is documented in `docs/planned-features.md` under "Polyrhythm Phase Loops" → "Rejected alternatives."
