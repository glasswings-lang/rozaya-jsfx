# Polyrhythm Phase v1 → v3 — the crossing

**Status: DONE 2026-09-10.** 144 instances converted in 31 files and verified by
render: all 144 byte-identical against the old plugin fed float32-rounded values,
and that rounding measured at most 1.5e-08 against the untouched old plugin. The
one silent instance (Tensor's `singing-bowl`) is silent in the old plugin too.
The old plugin (the one its manual calls v2) is archived at
`archive/versions/polyrhythm_phase/v2.jsfx` and removed from REAPER.

## Decided with Rozaya, 2026-09-10

- Do the crossing now: *"We should try with the 84, then I can finally put that
  old version into archived where it belongs."*
- Tensor's folder is included: *"Go ahead with Tensor's, it'd probably appreciate
  it."*
- Every voice gets its real note name: *"do it your way, that'll be easier to
  figure out later"*. Transpose and Octave shift start at 0.

## Scope — 144 instances, 31 files, backups and `.RPP-bak` excluded

| where | files | instances |
|---|---|---|
| `E:/reaper` (finished, templates, to-play-with-later, claude-experiments) | 17 | 84 |
| REAPER `TrackTemplates` | 4 | 12 |
| `E:/tensor's-rpp-projects` | 10 | 48 |

One Tensor line (`tensor-polyrhythm-drift-20260507-023000`) has 65 tokens: 59
values and six dashes. REAPER did not write it; the 59 are unambiguous.

## What the old saves hold (read 2026-09-10)

- 11 of the 84 carry a `2100024` blob; 2 of those have a ramp `by`, none has
  drift. Every other instance has no blob at all.
- 69 of the 84 store only sliders 1–59; everything above runs on v1's declared
  defaults, so **the conversion writes v1's defaults, never v3's**.
- Every active voice's semitones is a whole number. Absolute notes run MIDI 24
  to 131: `Star-sequence` has voices up to 131, about 15.8 kHz, above the note
  list's G9. Pitch value holds 131; Note name shows G9.

## Slider line, v1 → v3 (59 sliders)

| v3 | control | from v1 |
|---|---|---|
| 1 | Tremolo Mode | 1 |
| 2 | Rate Value | 3 |
| 3 | Rate Mode | 2 |
| 4, 5 | Attack / Release Shape | 8, 9 |
| 6 | Tuning Reference | 11 |
| 7, 8 | Transpose, Octave shift | **0, 0** |
| 9 | Binaural Beat | 4 |
| 10 | Pulse Width | 73 |
| 11–14 | Tone, Edge, Movement, Body | 69–72 |
| 15 | Voice | **1**, as on 2026-09-07 |
| 16–30 | voice 1's pitch block and controls | from the banks below |
| 31, 32, 33, 34 | Pan Enabled, Mode, Spread, Base Rate | 15, 16, 17, 18 |
| 35 | Pan rate mode | **v1's Rate Mode (2)** — the pan borrowed it |
| 36 | Pan Increment | 19 |
| 37 | Cycle Steps | 86 |
| 38 | Pan Glide | 85 |
| 39–43 | Direction, Reverse offset, Start delay, Play for, Rest for | 60–64 |
| 44–51 | Drift target (remapped), up, down, period, **unit Cycles**, shape, play 0, rest 0 | 74–78 |
| 52–59 | Ramp target (remapped), by, **unit Minutes**, duration, play 0, rest 0, engage, start delay | 79–83 |

v1's `Host ratio` (84) is dead and dropped.

## Per voice (the banks)

- **Pitch value** = 60 + (Center Octave − 4) × 12 + Base Note + the voice's
  Semitones. **Pitch mode** Semitones, **Fine tune** 0, **Fine tune unit**
  Cents, **Note name** the same number held to 0..127. All integers, so the
  frequency is bit-exact.
- Gain, Drift / Rate, Phase Offset, Active: the voice's own v1 sliders.
- Waveform, Tremolo amount, On Duration, Attack %, Release %: v1's global
  sliders 14, 10, 5, 6, 7, into every voice. Solo off.

## Drift and Ramp banks

- **With a `2100024` blob:** each of its 24 targets goes through v3's old-to-new
  table; the four shared envelope targets copy into all eight voices. Selectors
  from the blob.
- **Without one:** exactly what v1 does on load. Its selector starts at 0, so the
  first `@slider` saves the visible Drift and Ramp values into target 0 and loads
  the saved target's defaults. The conversion reproduces that.
- Written as a native `2300088` blob; instances without a `<JS_SER>` gain one.

## Verify

Per instance: the old plugin on the snapshot, the old plugin on a copy whose
bank-bound values are rounded to float32 (what a blob can hold), and the new
plugin on the converted file. **Rounded old against new must be bit-identical**;
original against rounded is reported as the size of the rounding.
