# Shepard Tone and Shepard Scale — pitch that works live, and full drift targets

**Status: BUILT AND INSTALLED 2026-09-10. NOT HEARD.** Zero projects use either,
so no migration. Measured, all sliders loaded: both render bit-identical to the
old plugins at defaults. Tone: old Synced detune -500 equals new Fine tune -500,
old Independent rate 0.3 equals new Rate 0.3, and gain, pan and a second voice's
detune match on their new sliders. Scale: gain, pan, a note switched off, attack,
binaural, tuning, pulse width, play/rest and an attack drift all match on their
new sliders. Note, fine tune and tuning reference changes now act while playing,
and every added drift target changes the render. A Scale fine tune set at load
differs from the old plugin by design: the old one also moved the octave fade.

Decided by Star, 2026-09-10:

- Tone's per-voice `Drift (Synced: cents) / Rate (Indep)` splits into a Rate and a
  Fine tune, keeping all three of its jobs: a voice's own speed, a voice that
  holds still at rate 0, and a pitch offset of up to ±1000 cents that moves the
  pitch without moving the octave fade.
- Scale's fine tunes move into their note groups.
- Note and fine tune changes take effect while playing.
- Logical order; every sound-shaping control plus Play for and Rest for is a
  Drift and Ramp target. No Hz/semitones/cents mode: a Shepard voice is its note
  in every octave at once.

## Shepard Tone: 81 sliders -> 89

| new | control | old |
|---|---|---|
| 1 | Drift Mode | 1 |
| 2 | Rate Value | 3 |
| 3 | Rate Mode | 2 |
| 4–8 | Octave Count, Center Octave, Fade In %, Fade Out %, Waveform | 4–8 |
| 9 | Pulse width | 81 |
| 10–12 | Binaural Beat, Root Note, Tuning Reference | 9–11 |
| 13 | `Fine tune unit (for every voice)` | new, default Cents |
| 14 + 7v | Vn Note | 12 + 6v |
| 15 + 7v | `Vn Fine tune (in fine tune units)` | the Synced half of 15 + 6v |
| 16 + 7v | Vn Direction | 14 + 6v |
| 17 + 7v | `Vn Rate (in rate mode units; 0 = holds still)`, Independent only | the Independent half of 15 + 6v |
| 18 + 7v | Vn Gain dB | 16 + 6v |
| 19 + 7v | Vn Pan | 13 + 6v |
| 20 + 7v | Vn Active | 17 + 6v |
| 70–73 | Start delay, Play for, Rest for, Rest mode | 60–63 |
| 74–81 | Drift block | 72–79 |
| 82–89 | Ramp block | 64–71 |

Host ratio (retired, 80) is removed.

Targets, 40: Rate value, Fade in, Fade out, Pulse width, Binaural beat, Tuning
reference; then per voice Fine tune, Rate, Gain, Pan (6 + 4v); then Play for,
Rest for.

## Shepard Scale: 83 sliders -> 82

| new | control | old |
|---|---|---|
| 1–10 | Rate value … Waveform | 1–10 |
| 11 | Pulse width | 70 |
| 12–13 | Binaural Beat, Tuning Reference | 11–12 |
| 14 | `Fine tune unit (for every note)` | 71 |
| 15 + 4n | note Active | 13 + 3n |
| 16 + 4n | note Gain dB | 14 + 3n |
| 17 + 4n | note Pan | 15 + 3n |
| 18 + 4n | `note Fine tune (in fine tune units)` | 72 + n |
| 63–66 | Start delay, Play for, Rest for, Rest mode | 49–52 |
| 67–74 | Drift block | 61–68 |
| 75–82 | Ramp block | 53–60 |

Host ratio (retired, 69) is removed. The note groups' show/hide used slider
numbers as bitmasks, which hid the wrong controls; it uses the sliders themselves.

Targets, 45: Rate value, Attack, Release, Note length, Pulse width, Binaural beat,
Tuning reference; then per note Gain, Pan, Fine tune (7 + 3n); then Play for, Rest
for.

## How pitch goes live

- Fine tune and a drifting Tuning reference are applied when each oscillator is
  read, so they act at once and leave the octave fade where it is.
- A Tone voice's note change multiplies its oscillators by the interval and wraps
  them into the window, the same set a fresh start at the new note would place.
  A Tuning reference change scales every oscillator.
