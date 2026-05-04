# Rozaya JSFX plugin suite

A small collection of Reaper JSFX plugins for ambient, sleep, and entrainment audio. Public domain (CC0). Designed by Rozaya, developed iteratively with Claude.

## Layout

- `src/*.jsfx` — plugin source files (one per plugin).
- `docs/rozaya_jsfx_manual.md` — user-facing reference for every plugin and its parameters. **Update this whenever you change a slider or add a feature** — modders and players read it instead of the source.
- `LICENSE` — CC0.
- `README.md` — top-level overview.

## Active plugin under heaviest development

`src/polyrhythm_phase.jsfx` — drone synth, not a playable instrument. Up to 8 simultaneous voices, polyrhythmic tremolo with attack/release envelope, optional binaural beat, four pan modes (Tremolo / Increment / Spread / Spread Reversed), now ten waveforms (the original 6 + Bell, Wavefold, Half-sine, Phi-cascade as of `feature/new-waveforms`).

## Project values to preserve

- **Public domain (CC0)** — no proprietary code, no copying from licensed sources. Original implementations only.
- **Gentle by default** — these plugins target sleep / ambient / entrainment use. Avoid harsh transients, aggressive transients, or designs that produce mono-cancellation artifacts on speakers. Mono compatibility matters because users play these on HomePods, phone speakers, etc.
- **Hand-editable text and JSON** — every slider has a sensible default in the spec; every text pool is plain-text with one entry per line. Modders are first-class users.
- **No new dependencies** — pure JSFX (eel2 syntax). No external libraries, no Reaper extensions.

## JSFX gotchas baked in from past sessions

- **Slider IDs are primary keys.** Reaper preserves slider VALUES by ID across file edits. Renumbering existing sliders scrambles user state — V1 Active ends up holding V2 Gain dB's value, which clamps to a different range and silently breaks things. **Always add new sliders at the END of the slider range, never in the middle.** If a player reports "everything is wrong after the update," the fix is usually `git status` + re-add the plugin instance for clean defaults.
- **Phase wrap discontinuity.** Any modulator computed as `sin(2π · k · phase)` where `k` is a non-integer (golden ratio, 2.4, 4.5, etc.) creates a discontinuity each time the carrier phase wraps. This shows up as a click at the fundamental rate. To use non-integer harmonics cleanly, you'd need a separate phase counter for the modulator (extra memory bank slot). For new waveforms, prefer integer harmonic multipliers (1, 2, 3, ...) unless you're willing to add the extra state.
- **Stop-sequence-style behaviors** don't apply here (no language model). What does apply: stay below 90° static L/R phase offset to avoid mono-cancellation on speakers; static phase offsets read as **lateralization** to the listener (ITD cue), not as width. True width without binaural beating requires either a) multi-voice unison with detune, b) chorus/ensemble effects with modulated delay lines, or c) all-pass filter networks. There's a session log of attempting (b) inside the plugin and reverting to "use Reaper's stock chorus AFTER the synth" — see git log around the pan-modes merge for context.
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
  - 288 onward: free for new arrays.

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

- **Pan modes feature** added Spread + Spread Reversed (commit `b60e635`) — static pan positions ranking active voices across the stereo field. Bonus discovery: running two tracks of the synth, one with Spread + one with Spread Reversed at slightly different Tuning Reference Hz, produces a surprisingly rich stereo width effect via composition rather than DSP. Documented in the Pan section of the manual.
- **Per-voice docs fix** (commit `fb6199a`) — the manual previously listed Vn Note and Vn Octave as per-voice sliders; the actual sliders are Gain dB / Semitones / Drift-Rate / Phase Offset / Active. Also default Gain dB is -6 for V1 and -60 for V2-V8 (manual previously claimed default 0 for all).
