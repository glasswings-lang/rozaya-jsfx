# Sustain Looper — authored target layout

**Status: BUILT, MIGRATED AND INSTALLED 2026-09-10. NOT HEARD.** All four
instances render bit-identical to the old plugin with the sample loaded. Moving
loop position or length measured a 0.63 sample step before and 0.12 after,
against 0.10 with nothing moved. Source C4 plus Target G4 renders identically to
7 semitones and to 700 cents.

Decided by Star, 2026-09-10:

- The pitch block is Bubbler's shift form, because the looper plays a file whose
  pitch it does not know.
- Drift and Ramp reach every control that shapes the sound (R24).
- Moving loop position or loop length must not jump the playhead. *"the playhead
  thing sounds like it needs a fix anyway."*

8 sliders become 30. One project, `finished/energy healing vol. 2.RPP`, holds
four instances. Backup: `E:/reaper/finished/backups/snapshots/_pre-looper-pitch-20260910/`.

## The order

| # | control | from |
|---|---|---|
| 1 | `Sample` | 1 |
| 2 | `Loop position (%)` | 2 |
| 3 | `Loop length (ms)` | 3 |
| 4 | `Crossfade (% of loop)` | 4 |
| 5 | `Source note (where zero is)` `{None, C-1 … G9}` | new, default None |
| 6 | `Target note` `{C-1 … G9}` | new, default C4; shown only when Source note is set and the unit is Semitones |
| 7 | `Transpose value (Hz / semitones / cents)` | 5 `Pitch (semitones)` |
| 8 | `Transpose unit` `{Hz, Semitones, Cents}` | new, migrated as Semitones |
| 9 | `Fine tune` | new, default 0 |
| 10 | `Fine tune unit` `{Hz, Semitones, Cents}` | new, default Cents |
| 11 | `Tuning reference (Hz)` | new, default 440 |
| 12 | `Voices (ensemble)` | 7 |
| 13 | `Spread (%)` | 8 `Spread (detune amount)`, renamed per R17 |
| 14 | `Output (dB)` | 6, moved to sit last before Drift |
| 15 | `Drift target` | new |
| 16 | `Drift up amount (units match target)` | new |
| 17 | `Drift down amount (units match target)` | new |
| 18 | `Drift period (0 = off)` | new |
| 19 | `Drift period unit` `{Seconds, Beats}` | new; no Cycles, the looper has no rate |
| 20 | `Drift shape` `{Sine, Triangle, Random}` | new |
| 21 | `Drift play for (periods, 0 = always)` | new |
| 22 | `Drift rest for (periods, 0 = always)` | new |
| 23 | `Ramp target` | new |
| 24 | `Ramp by (units match target)` | new |
| 25 | `Ramp time unit` `{Seconds, Minutes, Beats}` | new, default Minutes |
| 26 | `Ramp duration (in ramp time units)` | new |
| 27 | `Ramp play for (0 = smooth)` | new |
| 28 | `Ramp rest for (0 = smooth)` | new |
| 29 | `Ramp engage` `{Off, On}` | new |
| 30 | `Ramp start delay (in ramp time units)` | new |

## Drift and Ramp targets

One list for both, in the order the controls appear:
`Loop position, Loop length, Crossfade, Transpose, Fine tune, Tuning reference,
Spread, Output`. Voices is a count and is not a target. None of them step; all
move continuously.

## The playhead

When the loop region moves so a playhead falls outside it, the playhead moves to
its new place under a short crossfade from where it was, for the main loop and
every ensemble voice. It never cuts.

## Migration

Per instance: 1–4 unchanged; old 5 → 7 with 8 = Semitones; old 6 → 14; old 7 →
12; old 8 → 13. Everything else takes its default. The four instances hold
pitches 6.5, 4.5, −0.5 and −7.5.

Verify: the old plugin on the backed-up project against the new plugin on the
migrated project, bit-identical, with the sample actually loaded and sounding.
