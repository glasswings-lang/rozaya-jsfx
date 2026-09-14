# The Morpher's pitch layout -- stages 5 and 6, written and trialled 2026-09-13, NOT applied

`stage5_units.py` (the amount units) and `stage6_saveformat.py` (save format 7700087) each
edit `src/spectral_vowel_morpher.jsfx` in place by exact-match anchors and refuse if an
anchor is missing. Apply stage 5 before stage 6.

`stage5_trial.py` and `stage6_trial.py` are the RECORD of their trials on a scratch copy
(stage 5: lint, compile, 23 of 23 conversions; stage 6: 14 of 14 save and reopen checks).
They name the scratch folder of the session that ran them, which no longer exists: to trial
again, set `S` to any temporary folder and put the two patch scripts in it.

After applying for real, measure with `tools/morpher_verify_20260913.py` -- `units convert
current` after stage 5, `saveformat savedlive` after stage 6. The order of everything left is
in `docs/history/layouts/spectral-vowel-morpher.md`, "BUILD PROGRESS".
