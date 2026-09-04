# Polyrhythm Phase — the v1/v3 fork, and how it closes

Written 2026-08-31. **Status: decision evidenced, layout not yet authored, nothing built.**

## The decision: migrate v1's projects up to v3, then archive v1

CLAUDE.md has carried this fork as "permanent until someone writes the migration."
It is not permanent, and the migration is much cheaper than assumed. Every claim
below is measured, not estimated.

### 1. The 18-vs-6 project count is a backlog, not a preference

Rozaya's hypothesis, 2026-08-31: *"I suspect they're using v1 because they predate v3,
or because of sheer habit."* Correct. v3 was created **2026-07-23**.

- **14 of the 17 real v1 projects were last touched before v3 existed** — most in
  April and May. They are not chosen; they have not been opened.
- Only three v1 projects have been touched since: `rain-sound` (07-30),
  `you-can-rest-now` (08-02), `Eeeee` (08-10). Two are in `finished/`, so they read as
  old pieces reopened rather than new work begun on v1.
- **Every project started since v3 shipped went to v3** — five in a month.

**One confound, and it was mine.** `surges` showed 2026-08-22, which looks like recent
v1 use. That is the date `sweepfilter_migrate_hz.py` rewrote it. Its last human edit was
07-20. Checking the `_pre-hz-migration` snapshot folder (now under
`E:/reaper/finished/backups/snapshots/`) is what caught it — without that,
my own script would have counted as evidence about Rozaya's habits. **Any future
date-based argument has to exclude files a migration touched.**

### 2. v3 is a strict superset of what the projects actually use

The worry was that v3's note picker (49 entries, C2..C6, integer semitones) could not
hold what v1's `Vn Semitones` (`-1000..1000`, step **0.1**) allowed. Measured across all
**84 v1 plugin instances** in the library:

- **No microtonal values anywhere.** Every semitone value in every project is a whole
  number. Even `experiment-3-microtonal.RPP` uses only 0 and 12 — its microtonality comes
  from Tuning Reference Hz, not from semitones.
- **No instance spans more than 29 semitones**, against the 48 v3's note list covers.
  0 of 84 fail to fit.
- Absolute pitches range MIDI 24..131. v3 reaches all of it: its note window is MIDI
  36..84, shifted by `Octave shift` (±4 octaves) and `Transpose` (±12).
- **v3 is finer, not coarser.** It has a per-voice `Fine tune (cents)` at ±100 in 1-cent
  steps. v1's 0.1-semitone step is 10 cents. v3 is ten times more precise microtonally.

Indexing was validated before any of this was trusted: token 12 must be Base Note (0–11)
and token 13 Center Octave (0–8) — **84/84 instances aligned.**

### 3. The `@serialize` blob is byte-identical between the two

Both are `N_TARGETS = 24` with the same magic and the same payload, field for field:
drift up/down/period/shape, the selector, the Speed Ramp by/duration/delay banks, the
ramp selector. **Diffed: identical.**

So **every drift and Speed Ramp configuration crosses untouched**, with nothing to
translate. This was the largest risk in the whole idea and it is simply absent.

## What the migration has to do

1. **Repoint the project** — `polyrhythm_phase.jsfx` → `polyrhythm_phase_v3.jsfx`.
2. **Convert pitch.** v1 is `(octave+1)*12 + base_note + semitones`; v3 is
   `(4 + octave_shift + 1)*12 + transpose + (note_index - 24)`. Per instance, pick an
   `octave_shift` that brings the whole voice set inside 0..48, then
   `note_index = (octave+1)*12 + base + semitones - 36 - 12*octave_shift`. Exact.
3. **Permute the rest of the slider line.** v3's per-voice block is 6 sliders where v1's
   is 5 (Fine tune is new), so everything after the first voice shifts. **Still to be
   authored by hand**, as a table, before anything runs.
4. **The blob is copied verbatim.** Nothing to do.

## Order of work

v3 also needs its own reorder under the plan. Do them **together** — one migration, not
two, per the governing constraint. So Polyrhythm's layout file gets authored for **v3**,
and the v1→v3 conversion rides in the same pass.

## Open

- The full v1→v3 slider mapping is not authored yet. That is the remaining work here.
- Verify afterwards that only intended tokens moved, per the tooling boundary.
- `templates/complexity (template).RPP` and `templates/breathscapes.RPP` are templates —
  migrate them too or new projects will keep being born on v1.
