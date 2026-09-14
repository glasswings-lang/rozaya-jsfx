# Polyrhythm Phase v3 — pitch block and full drift targets

**Status: BUILT, MIGRATED AND INSTALLED 2026-09-10. NOT HEARD.** One migration
for both halves. All 8 instances render bit-identical, old plugin on the snapshot
against new on the migrated project. A fresh instance, and a fresh instance with
notes, fine tunes, transpose, pan, character and play/rest set, match old against
new. A crafted 2200024 save with drift and ramp on the four shared envelope
targets, a voice's rate and a voice's gain renders identically. Every one of the
80 non-"all voices" targets moves the sound; A4 measures 440 Hz as Semitones 69,
Hz 440 and Cents 6900; an all-voices entry reads back from voice 5 and 8, and
parking on one while moving Tone leaves each voice's setup alone.

## Decided with Rozaya, 2026-09-10

- The pitch block is Breath Generator's, inside the per-voice controls: *"breath
  gen handled this nicely"*. Pitch mode, Note name, Pitch value, Fine tune, Fine
  tune unit.
- Each voice has its own Pitch mode and Fine tune unit: *"It should get its own,
  since in theory that would apply to the 'all' option too."*
- Every per-voice control that is a target gets an "all voices" entry that copies
  one drift or ramp setup into all eight voices, the way the Voice picker's All
  does. Rozaya: *"Same, then, we just had to figure out what each other meant."*

Carried from Star, 2026-09-10 (R24): every sound-shaping control is a target,
plus Play for and Rest for; Start delay is not; targets go in control order.

**Claude's calls, unquoted, by precedent:** Octave shift is not a target and
Transpose is (Melody). Phase Offset is not a target: moving it re-seats the
voice's tremolo phase, so drifting it would restart the voice every sample.
Switching Pitch mode does not convert the value (Breath Generator). The drift
and ramp amount for a pitch is in that voice's own pitch unit.

## The order — 56 sliders become 59

| new | control | old |
|---|---|---|
| 1–15 | unchanged, through `Voice` | 1–15 |
| 16 | `Pitch mode` `{Hz, Semitones, Cents}` | new; migrated as Semitones |
| 17 | `Note name` `{C-1 … G9}`, shown in Semitones | 16 `Note` (C2–C6), index + 36 |
| 18 | `Pitch value (Hz / semitones / cents)` | new; migrated as the MIDI note |
| 19 | `Fine tune` `-1000..1000` | 17 `Fine tune (cents)` `-100..100` |
| 20 | `Fine tune unit` `{Hz, Semitones, Cents}` | new; migrated as Cents |
| 21–30 | Drift / Rate … Solo this voice | 18–27 |
| 31–43 | Pan enabled … Rest for | 28–40 |
| 44 | `Drift target`, remapped | 41 |
| 45–51 | the rest of Drift | 42–48 |
| 52 | `Ramp target`, remapped | 49 |
| 53–59 | the rest of Ramp | 50–56 |

Note name and Pitch value follow each other both ways in Semitones, exactly as
Breath Generator binds them. Transpose and Octave shift still move every voice.

## Drift and Ramp targets — 24 become 88, in control order

| # | target |
|---|---|
| 0 | Base Rate |
| 1 | Tuning reference |
| 2 | Transpose |
| 3 | Binaural Beat |
| 4 | Pulse width |
| 5–8 | Tone, Edge, Movement, Body |
| 9 + 9c | *control* (all voices) |
| 10 + 9c … 17 + 9c | V1 … V8 *control* |
| 81 | Pan spread |
| 82 | Pan base rate |
| 83 | Pan increment |
| 84 | Pan glide |
| 85 | Reverse drift offset |
| 86 | Play for |
| 87 | Rest for |

*c* runs 0–7 over: Pitch, Fine tune, Rate, Tremolo amount, On duration, Attack,
Release, Gain.

**An "all voices" entry holds nothing of its own.** Selecting it shows voice 1's
setup; moving a control writes that control into all eight voices' targets. So
the Drift and Ramp selectors become change-detected, like the Voice selector,
with their mirrors adopted in `@block` — a wholesale capture while parked on an
all-voices entry would flatten eight voices on any stray `@slider` pass.

Old to new: 0→0; V*k* Rate (1–8)→27+*k*; Pan base rate 9→82; Pan increment
10→83; Binaural 11→3; V*k* Gain (13–20)→60+*k*. The four shared envelope targets
— On duration 12, Tremolo amount 21, Attack 22, Release 23 — are copied into all
eight voices of 45, 36, 54 and 63, and a selector sitting on one lands on that
all-voices entry. No saved instance has any of the four configured (all 8 read
2026-09-10); the copy is exact for Sine and Triangle.

## Engine

- Frequencies stay derived per block. Semitones with a Cents fine tune uses the
  old arithmetic verbatim, so a migrated voice is bit-identical, fine tune
  included (`bilateral-with-binaurals` has a voice at +100 cents).
- Tone, Edge, Movement, Body, Pulse width, Pan spread and Pan glide move from
  `@slider` to `@block` so their targets can reach them.
- Tremolo amount, On duration, Attack and Release offsets are read per voice.
- Play for and Rest for are read per sample; the gate still switches on only
  when both sliders are above zero.

## Migration

- **Memory.** The per-target banks move to 128 slots each from 9552. The old
  24-wide addresses become the scratch banks an old blob is read into.
- **Blob**, by the plugin on read: magic `2300000 + 88`. Exactly `2200024` is
  read at its old width, then every bank is remapped, each voice's note gains 36,
  Pitch value copies it, Pitch mode is Semitones and Fine tune unit is Cents.
- **Slider line**, by `tools/polyv3_migrate_r22r24_20260910.py`, 8 instances in
  5 projects, snapshot first.

## Verify

Old plugin on each backed-up project against the new plugin on the migrated
project, every instance, bit-identical. A fresh instance, old against new. A
crafted old blob with drift and ramp on the shared envelope targets, a voice's
rate and a voice's gain, old against new. Then each new target shown to move the
sound, an all-voices entry read back from voice 5, the note binding both ways,
and A4 as Semitones 69, Hz 440 and Cents 6900.
