# Melody Phase — pitch block and full drift targets

**Status: BUILT, MIGRATED AND INSTALLED 2026-09-10. NOT HEARD.** All 73
instances in 7 projects render bit-identical old against new with every slider
loaded. A crafted 2400028 save with drift and ramp configured renders identically
old against new, selectors remapped to 24 and 5. A4 as Semitones 69, Hz 440 and
Cents 6900 render identically, and picking the note name matches. Pitch, fine
tune, transpose, tuning reference, pulse width and Play for drift all change the
sound reproducibly; a -12 dB Master gain ramp measures 0.2512.

**Test trap met twice here:** a stepped drift with period 2 parks at zero, and a
fresh instance runs at 1 BPM, so an 8-second render never reaches a second step.

Decided by Star, 2026-09-10:

- Logical order wins. No control and no target option is appended to save a
  migration.
- Every sound-shaping control is a Drift and Ramp target, plus Play for and Rest
  for. Start delay is not.
- A voice's pitch drift moves with the note by default. Transpose is a target.

Carried from Rozaya: no voice selector; a voice has its note, and the mode is
the plugin's. *"Why would a voice need a block each?"*

96 sliders become 105. Seven projects hold Melody.

## The order

| new | control | old |
|---|---|---|
| 1–4 | Rate value, Rate mode, Waveform, Pulse width | 1–4 |
| 5 | `Pitch mode` `{Hz, Semitones, Cents}` | new; migrated as Semitones |
| 6 | `Fine tune unit (for every voice)` | 6 |
| 7 | `Tuning reference (Hz)` | 5 |
| 8 | `Transpose (semitones)` | 7 `Transpose (half steps)` |
| 9 | `Octave shift` | 8 |
| 10 | `Binaural beat (Hz, L/R offset)` | 9 |
| 11–14 | Attack, Attack shape, Release, Release shape | 10–13 |
| 15–16 | Glide time, Legato glide | 14–15 |
| 17–24 | Pan enabled … Pan increment per voice | 16–23 |
| 25–27 | Sequence length, Direction, Loop sequence | 24–26 |
| 28 + 7v | `Vn Note` `{C-1 … G9}`, shown in Semitones mode | 27 + 6v, index + 36 |
| 29 + 7v | `Vn Pitch (Hz / semitones / cents)` | new; migrated as the MIDI note |
| 30 + 7v | `Vn Fine tune (in fine tune units)` | 28 + 6v |
| 31 + 7v | `Vn Next voice in (cycles)` | 29 + 6v |
| 32 + 7v | `Vn Note duration (cycles; 0 = silent)` | 30 + 6v |
| 33 + 7v | `Vn Gain dB` | 31 + 6v |
| 34 + 7v | `Vn Active` | 32 + 6v |
| 84 | `Master gain (dB)` | 75 |
| 85–88 | Start delay, Play for, Rest for, Rest mode | 76–79 |
| 89–97 | the Drift block | 80–88 |
| 98–105 | the Ramp block | 89–96 |

v is 0 for V1 through 7 for V8.

**The pitch value is the pitch**, as in Breath Generator: Hz is the frequency,
Semitones is the MIDI note number, Cents is that times 100. Note name and value
bind both ways in Semitones mode. Transpose and Octave shift move every voice.
The note list was C2–C6 and becomes the full MIDI range, so a stored index gains
36.

## Drift and Ramp targets, 55, in control order

| # | target | old # | moves by default |
|---|---|---|---|
| 0 | Rate value | 0 | clock |
| 1 | Pulse width | new | clock |
| 2 | Tuning reference | new | clock |
| 3 | Transpose | new | with the target (any note) |
| 4 | Binaural beat | new | clock |
| 5 | Attack | 26 | with the target (any note) |
| 6 | Release | 27 | with the target (any note) |
| 7 | Glide time | new | clock |
| 8 | Pan spread | new | clock |
| 9 | Pan glide | new | clock |
| 10 | Pan base rate | 9 | clock |
| 11 | Pan increment | new | clock |
| 12 + 5v | Vn Pitch | new | with the target (that voice) |
| 13 + 5v | Vn Fine tune | new | with the target (that voice) |
| 14 + 5v | Vn Next voice in | 1 + v | clock |
| 15 + 5v | Vn Note duration | 18 + v | with the target (that voice) |
| 16 + 5v | Vn Gain | 10 + v | clock |
| 52 | Master gain | new | clock |
| 53 | Play for | new | with the target (any note) |
| 54 | Rest for | new | with the target (any note) |

Every old default is kept: the targets that stepped before still step.

## Migration

- **Slider line**, by script: the renumber above; Pitch mode written as
  Semitones; each voice's note index + 36 into Note and into Pitch; the Drift
  and Ramp target selectors remapped through the target table.
- **Blob**, by the plugin itself on read: magic goes to `2500000 + 55`. Any older
  magic is read at its own width of 28 into scratch banks, then every bank is
  remapped through the target table, including the two remembered selectors.
- Drift banks move to 64 apart.

Verify: the old plugin on each backed-up project against the new plugin on the
migrated project, every instance, bit-identical, all 105 sliders loaded. Then a
crafted old blob with drift configured, rendered old against new.
