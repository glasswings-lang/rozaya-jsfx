# Veil -- the amount units (R26) and the same things (R27)

**PROPOSED 2026-09-13, not yet agreed with Rozaya. Nothing built.** The first plugin of the
amount-unit sweep. One layout, one migration: everything Veil gains is here.

**NOT YET WHOLE: the eight ramps (`docs/layouts/multi-ramp.md`) are missing.** Veil has a Ramp,
so it gets them, and building this first would move Veil's saved copies twice. That design still
has open items. Asked whether Veil waits for them, Rozaya 2026-09-13: *"Yes, we need to take
this plugin by plugin anyway."* So the eight ramps are settled, then added here. Also open
once they land: one `Rest mode (for Ramp)` for all eight, or one per ramp.

Checked in `src/veil.jsfx` 2026-09-13: 22 sliders; no plugin-wide Start delay, Play for or
Rest for (it has only the Drift and Ramp versions); Veil filters incoming sound (`@sample`
reads `spl0`/`spl1`), so `Output at rest` means something here. Saved copies outside
backups: ONE, in `finished/test-projects/claude-testing002-bridge.RPP`. Blob magic
`3300000 + N_TARGETS` (3300005), banks 16 wide at fixed addresses from 4096.

## The layout, 22 -> 31

| new | control | from | seeded to |
|---|---|---|---|
| 1-4 | Left cutoff (Hz), Right cutoff (Hz), Left resonance, Right resonance | 1-4 | as saved |
| 5 | Slope (dB/oct) | 5 | as saved |
| 6 | Output (dB) | 6 | as saved |
| 7 | **Start delay (seconds / beats)** | new | 0 |
| 8 | **Play for (seconds / beats, 0 = always)** | new | 0 |
| 9 | **Rest for (seconds / beats, 0 = always)** | new | 0 |
| 10 | **Transport unit** `{Seconds, Beats}` | new | 0 Seconds |
| 11 | **Rest mode (for Drift)** `{Walk through, Freeze in place}` | new | 0 |
| 12 | **Rest mode (for Ramp)** `{Walk through, Freeze in place}` | new | 0 |
| 13 | **Output at rest** `{Pass-through, Silence}` | new | 0 |
| 14 | Drift target | 7 | as saved |
| 15-16 | Drift up amount, Drift down amount (per target, in the Drift amount unit) | 8-9 | as saved |
| 17 | **Drift amount unit (per target, Target default where it cannot fit)** | new | 0 |
| 18 | Drift period (per target, 0 = off) | 10 | as saved |
| 19 | Drift period unit (all targets) | 11 | as saved |
| 20 | Drift shape (per target) | 12 | as saved |
| 21-22 | Drift play for, Drift rest for (per target) | 13-14 | as saved |
| 23 | Ramp target | 15 | as saved |
| 24 | Ramp by (per target, in the Ramp by unit) | 16 | as saved |
| 25 | **Ramp by unit (per target, Target default where it cannot fit)** | new | 0 |
| 26 | Ramp time unit (all targets) | 17 | as saved |
| 27 | Ramp duration (per target, in ramp time units) | 18 | as saved |
| 28-29 | Ramp play for, Ramp rest for (per target) | 19-20 | as saved |
| 30 | Ramp engage (all targets) | 21 | as saved |
| 31 | Ramp start delay (per target, in ramp time units) | 22 | as saved |

Order: Part 2 (identity, output, transport, Drift, Ramp); a unit picker directly after what
it modifies (Drift amount unit after the amounts, Ramp by unit after Ramp by). Every new
control is off or on its old meaning, so the saved copy sounds the same.

**The Transport unit takes the units Veil's Drift period already has, `{Seconds, Beats}`.**
Rozaya: *"play/rest for should have the same units as drift does"*, *"Just for that thing.
that's literally all I meant, that thing has drift already"*. **Mine, unquoted:** Rest mode
is what the Drift and Ramp clocks do while resting. Labels follow Passage's.

**Walk or freeze: TWO switches, decided 2026-09-13.** Veil has nothing that moves on its own
(read `src/veil.jsfx`: no LFO, no walk; only Drift and Ramp), while every other walk-or-freeze
switch freezes the plugin's own motion and leaves Drift and Ramp running. Offered one switch,
`Rest mode (for Drift and Ramp)`, Rozaya: *"drift and/or ramp. if it's gonna be like that it needs
both as distinct shit"*, then *"Drift is its own thing. ramp is its own thing. when the 8 ramps
come in, the distinction is going to be even more important"*. So `Rest mode (for Drift)` and
`Rest mode (for Ramp)`, each on its own.
The `(for X)` naming follows Rozaya's own idea for the LFO plugins (`docs/backlog.md`). Veil is
the first plugin where a rest can freeze Drift or Ramp. **Mine, unquoted:** both in the transport
block, Walk through by default (what every plugin does today); Freeze holds that clock's phase,
its random steps and its ramp progress, and resumes where it stopped.

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
- Each new control does what it says: Start delay, Play/Rest in Seconds and Beats, both Rest
  modes each on its own (Drift frozen with Ramp walking, and the reverse), Output at rest; units on a cutoff (Semitones, Cents) against worked answers.
- Save and reopen; `jsfx_map impact` with no unanswered question; the REAPER round trip with
  REAPER in front. Page `docs/plugins/veil.md` updated with the controls.
