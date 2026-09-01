# Melody Phase — authored layout

Written by hand 2026-08-31, not generated. Per the tooling boundary in
`suite-consistency-plan.md`: the permutation is authored, a script only applies it.

**Status: reading order APPROVED by Rozaya 2026-08-31. Nothing built yet.**

## What changes, and why each one

Melody Phase v1 is already one of the better-ordered plugins. Four real problems:

1. **`Host ratio` sits at 77**, sixty sliders from the `Rate Mode` it belongs to.
2. **`Direction` at 63 splits the transport block** (Start Delay 62, Play for 64).
3. **Attack/Release are separated from their shapes** — 10, 11, 12, 13 is
   Attack%, Release%, Attack shape, Release shape; a modifier belongs next to
   what it modifies.
4. **`Master Gain dB` is at 8**, in the middle of the sound controls rather than
   at the end of them.

5. **`Loop` is renamed `Loop sequence`.** The position was right — the code
   settles it, since `loop_enabled` is read *inside* the direction-stepping
   logic: it decides whether Up wraps back to the start or stops, and it bounds
   the bounce count in the Up-Down modes. It is welded to Direction, not merely
   near it. So the three read as one sentence: how many steps (Sequence length),
   in what order (Direction), and does it go round again (Loop sequence).

   But the NAME was the actual problem. In REAPER "loop" already means the
   transport loop over a time selection, so a plugin slider called just `Loop`
   is ambiguous — loop what? Sitting among the sound controls at 7, it read as
   though it might loop a sample or an envelope. Rozaya: *"loop is a fuzzy one
   for us."* The fuzziness was the name, not the position, and renaming is free.

Plus the two things this bump carries:

- **`Vn Semitones from root` becomes `Vn Note`** — note names C2..C6, matching
  Polyrhythm v3 exactly. A global **`Transpose (half steps)`** comes with it, so
  moving the whole sequence stays one control (also copied from v3).
- **The R13 rate block**: `Rate mode` drops `Host x` and keeps the units; a
  separate `Sync to host` switch, then the R11 sync target and `Every N beats`.
  Melody has two syncable rates — the sequencer and the pan — so the selector
  has real work.
- **R16 naming**: `Speed ramp *` becomes `Ramp *`; `Ramp by` becomes `Ramp to`
  per R14.

## The order

| new | control | from |
|---|---|---|
| 1 | Rate value | 2 |
| 2 | Rate mode (BPM / Seconds / Hz) | 1, minus Host x |
| 3 | Sync to host | NEW |
| 4 | Host sync target (Rate value / Pan base rate) | NEW (replaces 77) |
| 5 | Every N beats | NEW |
| 6 | Waveform | 3 |
| 7 | Pulse width (%, 50 = square) | 78, added 2026-09-01 with the Square/Pulse waveforms |
| 8 | Tuning reference (Hz) | 4 |
| 9 | Root note | 5 |
| 10 | Center octave | 6 |
| 11 | Transpose (half steps) | NEW |
| 12 | Binaural beat (Hz, L/R offset) | 9 |
| 13 | Attack (% of note duration) | 10 |
| 14 | Attack shape | 12 |
| 15 | Release (% of note duration) | 11 |
| 16 | Release shape | 13 |
| 17 | Glide time (seconds; 0 = off) | 20 |
| 18 | Legato glide | 21 |
| 19 | Pan enabled | 15 |
| 20 | Pan mode | 16 |
| 21 | Pan spread (%) | 17 |
| 22 | Pan base rate (Tremolo / Increment modes) | 18 |
| 23 | Pan increment per voice (Increment mode) | 19 |
| 24 | Sequence length | 14 |
| 25 | Direction | 63 |
| 26 | Loop sequence | 7, renamed |
| 27–66 | V1..V8: Note, Next voice in, Note duration, Gain dB, Active | 22–61 |
| 67 | Master gain (dB) | 8 |
| 68 | Start delay (in rate mode units) | 62 |
| 69 | Play for (steps) | 64 |
| 70 | Rest for (steps) | 65 |
| 71 | Rest mode | 66 |
| 72 | Drift target | 72 |
| 73 | Drift up amount | 73 |
| 74 | Drift down amount | 74 |
| 75 | Drift period (cycles) | 75 |
| 76 | Drift shape | 76 |
| 77 | Ramp target | 67 |
| 78 | Ramp to | 68 |
| 79 | Ramp duration (minutes) | 69 |
| 80 | Ramp engage | 70 |
| 81 | Ramp start delay (minutes) | 71 |

81 sliders, from 78: `Transpose`, `Sync to host` and `Every N beats` are added,
`Host ratio` is replaced by the sync target. `Pulse width` is already in the file --
it arrived with the Square and Pulse waveforms on 2026-09-01, appended at 78 -- and
this layout is where it stops being appended and goes next to the Waveform slider it
belongs to.

## Migration — five projects on v1, zero on v2

Two independent changes, both handled in one pass:

- **Positions.** Authored permutation above, applied to the `.RPP` slider line by
  token position. Snapshot the projects first; afterwards diff and assert only
  the intended tokens moved.
- **Values.** `Vn Semitones from root` becomes an absolute note index:
  `note_index = (Center octave x 12 + Root note + Semitones) - 24`, clamped to
  0..48 (C2..C6). Exact arithmetic, and the plugin can do it to itself on load
  from the blob magic — the same self-migration that converted Womb's heart from
  a tempo multiplier to BPM.
- **Seed `Transpose` to 0** and `Sync to host` to On only where the old
  `Rate Mode` was `Host x`, taking the unit from what the value last meant.

## And Melody Phase v2 is archived in the same commit

Zero projects, and its nested Voice selector is the design Rozaya has since
called overkill for this plugin (2026-08-31: *"that was my fault because I got
overeager one day"*). Its one good idea — the note-name picker — moves to v1
here, which is where the five projects are. Moves to `archive/versions/melody_phase/`,
out of `src/` and out of `docs/plugins/README.md`, per the versioning rule.
