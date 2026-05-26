# Rozaya JSFX plugin suite

A small collection of Reaper JSFX plugins for ambient, sleep, and entrainment audio. Public domain (CC0). Designed by Rozaya, developed iteratively with Claude.

## Layout

- `src/*.jsfx` — plugin source files (one per plugin).
- `docs/rozaya_jsfx_manual.md` — user-facing reference for every plugin and its parameters. **Update this whenever you change a slider or add a feature** — modders and players read it instead of the source.
- `LICENSE` — CC0.
- `README.md` — top-level overview.

## Active plugin under heaviest development

`src/polyrhythm_phase.jsfx` — drone synth, not a playable instrument. Up to 8 simultaneous voices, polyrhythmic tremolo with attack/release envelope, optional binaural beat, four pan modes (Tremolo / Increment / Spread / Spread Reversed), now ten waveforms (the original 6 + Bell, Wavefold, Half-sine, Phi-cascade as of `feature/new-waveforms`).

`src/polyrhythm_phase_loops.jsfx` — experimental sibling. Verbatim fork of polyrhythm_phase plus a Play/Rest gate (sliders 63, 64) that turns the synth into a series of paused loops. Has its own design rough edges (see "Play/Rest gating — IN PROGRESS" in `docs/planned-features.md`). When the engine is updated, both files need the same change — they share everything except the gate. Spun out of `feature/play-rest-gating` to keep the stable polyrhythm_phase risk-free.

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
- **`@init` re-runs on every transport start by default.** This silently re-zeros all plugin memory (variables, arrays, oscillator phases, smoother states) on every press of the Reaper play button — which breaks any feature that wants state to persist across stop/play (drift relationships, gate progression, accumulated phase positions). To preserve state, set `ext_noinit = 1;` at the top of `@init`. With that flag, `@init` only runs on actual plugin load and Reaper leaves memory intact at transport boundaries. Discovered 2026-05-25 while building polyrhythm_phase_loops's Play/Rest gating — the "loops paused" semantic was impossible without it. Documented at [reaper.fm vars.php](https://www.reaper.fm/sdk/js/vars.php).
- **`play_state` enumeration** (verbatim from official docs): `0 = stopped, <0 = error, 1 = playing, 2 = paused, 5 = recording, 6 = record paused`. There's no `3` or `4`. Common pitfall: `play_state == 0` alone misses the pause case — use `play_state == 0 || play_state == 2` if you want to gate "transport is not advancing." For "transport is actively moving" (regardless of mode) use `play_state == 1 || play_state == 5`. Transport-edge detection via `play_state != last_play_state` is more robust than the `play_state > 0 && last_play_state == 0` pattern (which only catches stop→play, not pause→play or play→pause).
- **Transport-edge detection belongs in `@block`, not `@sample`.** `play_state` updates per block, never mid-block, so polling in `@sample` is wasted work. The audio behavior is the same; it's a code-quality / performance note. The current polyrhythm_phase_loops code polls in `@sample` and it works — defer the refactor until there's a reason to touch that section anyway.
- **The active-voice normalizer is per-sample, and it bites you when voices drop out.** Polyrhythm Phase divides its summed output by the count of currently-audible voices each sample. When voices come and go (Play/Rest gate, future per-voice mutes, anything that silences some voices but not others) the divisor shrinks and the surviving voices get LOUDER — up to +18 dB when only one voice is still audible. Fix is to divide by `total_active` (precomputed in `@slider` from `v_active` toggles), so the divisor is stable across runtime voice silencing. polyrhythm_phase_loops has the fix; polyrhythm_phase still has the latent issue but never exhibits it because no runtime path silences voices.
- **Polyrhythm Phase voice memory layout** (16 slots each, shared between polyrhythm_phase and polyrhythm_phase_loops):
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
  - 288 v_resting (polyrhythm_phase_loops only — per-voice Play/Rest flag: 1 = frozen in rest, 0 = playing)
  - 304 v_pr_cycle (polyrhythm_phase_loops only — per-voice Play/Rest cycle counter, advances at the voice's own v_trem_freq)
  - 320 onward: free for new arrays. (`polyrhythm_phase` itself only uses up through slot 272 — slots 288/304 are reserved for the loops sibling so the two layouts stay aligned if the engines ever need to share state via a shared header.)

## Adding a new waveform to Polyrhythm Phase

1. Update `slider14`'s option list at the top of the file. Range becomes `0,N,1` where N+1 is the new option count.
2. Add a new `: waveform == K ? (...)` branch in the `@sample` voice loop's waveform chain. Compute `osc_l` from `osc_phase_l[i]` and `osc_r` from `osc_phase_r[i]`. Multiply by `gain_l[i] * v_gain[i]` (and `gain_r[i]` for R).
3. Update `docs/rozaya_jsfx_manual.md` Waveform section with a one-line description.
4. **Also update `src/polyrhythm_phase_loops.jsfx`** with the same slider14 change and the same `@sample` branch — the two plugins share an engine and the waveform palettes need to stay in sync.

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

- **Pan modes feature** added Spread + Spread Reversed (commit `b60e635`) — static pan positions ranking active voices across the stereo field. Bonus discovery: running two tracks of the synth, one with Spread + one with Spread Reversed at slightly different Tuning Reference Hz, produces a surprisingly rich stereo width effect via composition rather than DSP. Documented in the Pan section of the manual.
- **Per-voice docs fix** (commit `fb6199a`) — the manual previously listed Vn Note and Vn Octave as per-voice sliders; the actual sliders are Gain dB / Semitones / Drift-Rate / Phase Offset / Active. Also default Gain dB is -6 for V1 and -60 for V2-V8 (manual previously claimed default 0 for all).
- **Play/Rest spun out of polyrhythm_phase** (2026-05-25) — the gate work started on `feature/play-rest-gating` as in-place edits to polyrhythm_phase.jsfx. Per-voice cycle counting works; the level-jump-on-rest is fixed (was the active-voice normalizer dividing by per-sample audible count). The remaining cutoff-thud rough edge is design-level, not a bug — see `docs/planned-features.md` "Polyrhythm Phase Loops" section for the three candidate fixes. To keep polyrhythm_phase stable while the gate design is still being refined, the work was forked into `src/polyrhythm_phase_loops.jsfx` on `feature/polyrhythm-loops` (this branch). The original `feature/play-rest-gating` branch is parked as a historical record; treat it as abandoned for forward work.
