# Veil -- the amount units (R26) and the same things (R27)

**PROPOSED 2026-09-13, not yet agreed with Rozaya. Nothing built.** The first plugin of the
amount-unit sweep. One layout, one migration: everything Veil gains is here.

Checked in `src/veil.jsfx` 2026-09-13: 22 sliders; no plugin-wide Start delay, Play for or
Rest for (it has only the Drift and Ramp versions); Veil filters incoming sound (`@sample`
reads `spl0`/`spl1`), so `Output at rest` means something here. Saved copies outside
backups: ONE, in `finished/test-projects/claude-testing002-bridge.RPP`. Blob magic
`3300000 + N_TARGETS` (3300005), banks 16 wide at fixed addresses from 4096.

## The layout, 22 -> 30

| new | control | from | seeded to |
|---|---|---|---|
| 1-4 | Left cutoff (Hz), Right cutoff (Hz), Left resonance, Right resonance | 1-4 | as saved |
| 5 | Slope (dB/oct) | 5 | as saved |
| 6 | Output (dB) | 6 | as saved |
| 7 | **Start delay (seconds / beats)** | new | 0 |
| 8 | **Play for (seconds / beats, 0 = always)** | new | 0 |
| 9 | **Rest for (seconds / beats, 0 = always)** | new | 0 |
| 10 | **Transport unit** `{Seconds, Beats}` | new | 0 Seconds |
| 11 | **Rest mode** `{Walk through, Freeze in place}` | new | 0 |
| 12 | **Output at rest** `{Pass-through, Silence}` | new | 0 |
| 13 | Drift target | 7 | as saved |
| 14-15 | Drift up amount, Drift down amount (per target, in the Drift amount unit) | 8-9 | as saved |
| 16 | **Drift amount unit (per target, Target default where it cannot fit)** | new | 0 |
| 17 | Drift period (per target, 0 = off) | 10 | as saved |
| 18 | Drift period unit (all targets) | 11 | as saved |
| 19 | Drift shape (per target) | 12 | as saved |
| 20-21 | Drift play for, Drift rest for (per target) | 13-14 | as saved |
| 22 | Ramp target | 15 | as saved |
| 23 | Ramp by (per target, in the Ramp by unit) | 16 | as saved |
| 24 | **Ramp by unit (per target, Target default where it cannot fit)** | new | 0 |
| 25 | Ramp time unit (all targets) | 17 | as saved |
| 26 | Ramp duration (per target, in ramp time units) | 18 | as saved |
| 27-28 | Ramp play for, Ramp rest for (per target) | 19-20 | as saved |
| 29 | Ramp engage (all targets) | 21 | as saved |
| 30 | Ramp start delay (per target, in ramp time units) | 22 | as saved |

Order: Part 2 (identity, output, transport, Drift, Ramp); a unit picker directly after what
it modifies (Drift amount unit after the amounts, Ramp by unit after Ramp by). Every new
control is off or on its old meaning, so the saved copy sounds the same.

**The Transport unit takes the units Veil's Drift period already has, `{Seconds, Beats}`.**
Rozaya: *"play/rest for should have the same units as drift does"*, *"Just for that thing.
that's literally all I meant, that thing has drift already"*. **Mine, unquoted:** Rest mode
is what the Drift and Ramp clocks do while resting. Labels follow Passage's.

## Targets, 5 -> 7

`{Left cutoff, Right cutoff, Left resonance, Right resonance, Output, Play for, Rest for}` --
Play for and Rest for appended, which is also control order (R18, R24; as Passage). Old saves
keep their indices.

Amount units by target kind (the Morpher's and Passage's `au_*`): the cutoffs are frequencies
(Semitones and Cents move them by an interval, floor 20 Hz); resonance is a 0-1 value and
output is dB, so both take every amount as it stands; Play for and Rest for are lengths in the
Transport unit.

## Save format

Magic `3300000 + N_TARGETS` becomes 3300007. Two new banks, `target_drift_unit` and
`ramp_by_unit`, at 4448 and 4464 (after `sr_pr_accum_mem`, 4432), APPENDED at the end of the
stream and read only from a blob that wrote them. A 3300005 blob reads its five and the new
entries keep their defaults.

## Measured before install (the gate)

- Old build on the snapshot == new build on the migrated copy, bit-identical, noise in.
- Each new control does what it says: Start delay, Play/Rest in Seconds and Beats, Rest mode,
  Output at rest; units on a cutoff (Semitones, Cents) against worked answers.
- Save and reopen; `jsfx_map impact` with no unanswered question; the REAPER round trip with
  REAPER in front. Page `docs/plugins/veil.md` updated with the controls.
