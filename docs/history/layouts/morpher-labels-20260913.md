# Spectral Vowel Morpher's labels, 2026-09-13 -- the authored list

**Status: APPLIED 2026-09-13 (`1582542`), measured (scope 28/28). A record, not a plan.**

The renames stage of the Morpher's pitch layout (`docs/history/layouts/spectral-vowel-morpher.md`,
THE PITCH LAYOUT). Names come from that table, settled with Rozaya 2026-09-11, with R25's
kind added to every control behind a selector. Shared controls read as Passage's do where
the table allows it (`docs/history/layouts/passage-labels-20260913.md`).

**Where every kind comes from:** `tools/morpher_verify_20260913.py scope`, through jsfx_run
(set on one option, switch, read, switch back, read), measured before these are applied.
The live probe (`tools/selector_scope_probe.py --only morpher`) repeats it after install.

**Mine, unquoted:**
- "units match target" becomes "in the Drift amount unit" / "in the Ramp by unit", as on
  Passage: the amount is in whatever unit the picker names, Target default among them.
- The layer controls say `(per layer)`; the unit, where one is already in parentheses, comes
  first, as in `Ramp start delay (per target, in ramp time units)`.
- Capture average is global in this plugin (its source comment says why) and sits in the
  Capture slot block, so it says `(all slots)`.
- `Rate Mode` keeps its capital: nine plugins spell it that way, three `Rate mode`. The
  layout table's lower case was not a rename decision.
- Capture now is an action, not a value, and is left as it is, as on Passage.

Applied by `tools/r25_rename_apply.py --list docs/history/layouts/morpher-labels-20260913.md`
(exact old label on the exact slider, or refusal). A rename moves no saved value.

| file | slider | old label | new label |
|---|---|---|---|
| src/spectral_vowel_morpher.jsfx | 4 | Capture average (frames, 1 = one frame) | Capture average (frames, all slots, 1 = one frame) |
| src/spectral_vowel_morpher.jsfx | 23 | Denoise (%) | Denoise (%, wash only) |
| src/spectral_vowel_morpher.jsfx | 30 | Layer active | Layer active (per layer) |
| src/spectral_vowel_morpher.jsfx | 31 | Layer pitch value (Hz / semitones / cents) | Layer pitch value (Hz / semitones / cents, per layer) |
| src/spectral_vowel_morpher.jsfx | 32 | Layer pitch unit | Layer pitch unit (per layer) |
| src/spectral_vowel_morpher.jsfx | 33 | Layer fine tune | Layer fine tune (per layer) |
| src/spectral_vowel_morpher.jsfx | 34 | Layer fine tune unit | Layer fine tune unit (per layer) |
| src/spectral_vowel_morpher.jsfx | 35 | Layer level (dB, -60 = off) | Layer level (dB, per layer, -60 = off) |
| src/spectral_vowel_morpher.jsfx | 36 | Layer solo | Layer solo (per layer) |
| src/spectral_vowel_morpher.jsfx | 37 | Layer harmonics (0 = full) | Layer harmonics (per layer, 0 = full) |
| src/spectral_vowel_morpher.jsfx | 38 | Layer overtone harmonic (-1 = follow the global) | Layer overtone harmonic (per layer, -1 = follow the global) |
| src/spectral_vowel_morpher.jsfx | 47 | Drift up amount (per target, units match target) | Drift up amount (per target, in the Drift amount unit) |
| src/spectral_vowel_morpher.jsfx | 48 | Drift down amount (per target, units match target) | Drift down amount (per target, in the Drift amount unit) |
| src/spectral_vowel_morpher.jsfx | 57 | Ramp by (per target, units match target) | Ramp by (per target, in the Ramp by unit) |
