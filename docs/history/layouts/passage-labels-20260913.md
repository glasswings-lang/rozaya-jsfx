# Spectral Vowel Passage's labels, 2026-09-13 -- the authored list

**Status: APPLIED 2026-09-13 (`34160de`). A record, not a plan.**

The renames stage of Passage's layout (`docs/history/layouts/spectral-vowel-passage.md`). Names
come from THE LAYOUT's table, settled with Rozaya 2026-09-11, with R25's kind added to
every control behind a selector. Shared controls read as the Morpher's do where the table
allows it.

**Where every kind comes from:** `tools/passage_verify_20260911.py scope`, through jsfx_run
(set on Slot 1 or target 0, switch, read, switch back, read) -- Passage was not installed.
The live probe (`tools/selector_scope_probe.py --only passage`) repeats it after install.

**Mine, unquoted:**
- "units match target" becomes "in the Drift amount unit" / "in the Ramp by unit": with the
  picker built, the amount is in whatever unit it names, and Target default is one of them.
- The two amount-unit pickers say they fall back. Rozaya asked for that: the picker's name
  must say it falls back (layout doc, "Settled by Rozaya").
- The Drift and Ramp controls say `(per slot and target)`. The six whole-plugin targets
  (Tuning reference to Rest for) do not change with the slot; their names in the target
  list, and the plugin page, carry that.
- Rozaya's settled wording for Source fine tune and Target note is kept whole, with
  `per slot,` put in front of it.

Applied by `tools/r25_rename_apply.py --list docs/history/layouts/passage-labels-20260913.md`
(exact old label on the exact slider, or refusal). A rename moves no saved value.

| file | slider | old label | new label |
|---|---|---|---|
| src/spectral_vowel_passage.jsfx | 2 | Capture spectrum | Capture now |
| src/spectral_vowel_passage.jsfx | 3 | Capture point (per slot: earliest .. at press) | Capture point (%, per slot: earliest .. at press) |
| src/spectral_vowel_passage.jsfx | 4 | Capture average (per slot: 1 = one frame, higher = smoother) | Capture average (frames, per slot, 1 = one frame) |
| src/spectral_vowel_passage.jsfx | 6 | Source fine tune (only with a Source note, in Semitones) | Source fine tune (per slot, only with a Source note, in Semitones) |
| src/spectral_vowel_passage.jsfx | 7 | Source fine tune unit | Source fine tune unit (per slot) |
| src/spectral_vowel_passage.jsfx | 8 | Target note (only with a Source note, in Semitones) | Target note (per slot, only with a Source note, in Semitones) |
| src/spectral_vowel_passage.jsfx | 9 | Pitch (semitones) | Transpose value (Hz / semitones / cents, per slot) |
| src/spectral_vowel_passage.jsfx | 10 | Transpose unit | Transpose unit (per slot) |
| src/spectral_vowel_passage.jsfx | 12 | Fine tune unit | Fine tune unit (per slot) |
| src/spectral_vowel_passage.jsfx | 13 | Texture (0 voice, 100 wash) | Texture (% wash, per slot) |
| src/spectral_vowel_passage.jsfx | 14 | Wash grain (ms) | Wash grain (ms, per slot) |
| src/spectral_vowel_passage.jsfx | 15 | Spread (Hz) | Spread (Hz, per slot) |
| src/spectral_vowel_passage.jsfx | 16 | Denoise | Denoise (%, wash only, per slot) |
| src/spectral_vowel_passage.jsfx | 17 | Low cut (Hz) | Low cut (Hz, per slot) |
| src/spectral_vowel_passage.jsfx | 19 | Overtone harmonic (per slot: 0 = off, 1 = fundamental) | Overtone harmonic (per slot, 0 = off, 1 = fundamental) |
| src/spectral_vowel_passage.jsfx | 20 | Overtone lift (per slot: dB the chosen harmonic rises by) | Overtone lift (per slot, dB the chosen harmonic rises by) |
| src/spectral_vowel_passage.jsfx | 21 | Slot fade in (sec) (per slot: how long this slot takes to rise) | Slot fade in (seconds / Hz / beats, per slot) |
| src/spectral_vowel_passage.jsfx | 22 | Slot hold (sec) (per slot: how long it stays up, at full) | Slot hold (seconds / Hz / beats, per slot) |
| src/spectral_vowel_passage.jsfx | 23 | Slot fade out (sec) (per slot: how long this slot takes to fall) | Slot fade out (seconds / Hz / beats, per slot) |
| src/spectral_vowel_passage.jsfx | 24 | Slot gap after (sec) (per slot: silence before the next slot begins) | Slot gap after (seconds / Hz / beats, per slot) |
| src/spectral_vowel_passage.jsfx | 27 | Slot mute (per slot: skip in morph) | Slot mute (per slot, skipped in the morph) |
| src/spectral_vowel_passage.jsfx | 28 | Stereo width | Stereo width (%, per slot) |
| src/spectral_vowel_passage.jsfx | 33 | Overtone width (all slots: harmonics either side) | Overtone width (all slots, harmonics either side) |
| src/spectral_vowel_passage.jsfx | 34 | Morph (across captured slots) | Morph (% across captured slots) |
| src/spectral_vowel_passage.jsfx | 45 | Drift up amount (units match target) | Drift up amount (per slot and target, in the Drift amount unit) |
| src/spectral_vowel_passage.jsfx | 46 | Drift down amount (units match target) | Drift down amount (per slot and target, in the Drift amount unit) |
| src/spectral_vowel_passage.jsfx | 47 | Drift amount unit | Drift amount unit (per slot and target, Target default where it cannot fit) |
| src/spectral_vowel_passage.jsfx | 48 | Drift period (seconds, 0 = off) | Drift period (per slot and target, in drift period units, 0 = off) |
| src/spectral_vowel_passage.jsfx | 49 | Drift period unit | Drift period unit (all targets) |
| src/spectral_vowel_passage.jsfx | 50 | Drift movement | Drift movement (per slot and target) |
| src/spectral_vowel_passage.jsfx | 51 | Drift shape | Drift shape (per slot and target) |
| src/spectral_vowel_passage.jsfx | 52 | Drift play for (periods, 0 = always) | Drift play for (per slot and target, periods, 0 = always) |
| src/spectral_vowel_passage.jsfx | 53 | Drift rest for (periods, 0 = always) | Drift rest for (per slot and target, periods, 0 = always) |
| src/spectral_vowel_passage.jsfx | 54 | Drift restart | Drift restart (all targets) |
| src/spectral_vowel_passage.jsfx | 56 | Ramp by (units match target) | Ramp by (per slot and target, in the Ramp by unit) |
| src/spectral_vowel_passage.jsfx | 57 | Ramp by unit | Ramp by unit (per slot and target, Target default where it cannot fit) |
| src/spectral_vowel_passage.jsfx | 58 | Ramp time unit | Ramp time unit (all targets) |
| src/spectral_vowel_passage.jsfx | 59 | Ramp duration (minutes) | Ramp duration (per slot and target, in ramp time units) |
| src/spectral_vowel_passage.jsfx | 60 | Ramp play for (0 = smooth) | Ramp play for (per slot and target, 0 = smooth) |
| src/spectral_vowel_passage.jsfx | 61 | Ramp rest for (0 = smooth) | Ramp rest for (per slot and target, 0 = smooth) |
| src/spectral_vowel_passage.jsfx | 62 | Ramp engage | Ramp engage (all targets) |
| src/spectral_vowel_passage.jsfx | 63 | Ramp start delay (minutes) | Ramp start delay (per slot and target, in ramp time units) |
