# Veil -- the amount units (R26), the same things (R27) and the eight ramps

**PROPOSED 2026-09-13, being walked through with Rozaya. Nothing built.** The first plugin of
the per-plugin work. One layout, one migration: everything Veil gains is here, the eight ramps
(`docs/layouts/multi-ramp.md`) included. Rozaya, on waiting for them: *"Yes, we need to take
this plugin by plugin anyway."*

Checked in `src/veil.jsfx` 2026-09-13: 22 sliders; no plugin-wide Start delay, Play for or
Rest for (only the Drift and Ramp versions); Veil filters incoming sound (`@sample` reads
`spl0`/`spl1`), so `Output at rest` means something here. Nothing in Veil moves on its own: no
LFO, no walk; only Drift and Ramp. Saved copies: ONE outside backups,
`E:/reaper/finished/test-projects/claude-testing002-bridge.RPP` (searched every .RPP under
`E:/reaper`); its line is `480 520 0.15 0.15 0 0 2 600 0 20 0 0 0 0 2 600 1 0 0 0 0 0` -- both
selectors on Left resonance (index 2) showing up 600 and by 600, Minutes, engage Off. Blob magic `3300000 + N_TARGETS` (3300005), banks 16
wide at fixed addresses from 4096 to 4447; SVF state below them at 0..29.

## The layout, 22 -> 34

| new | control | from | seeded to |
|---|---|---|---|
| 1-4 | Left cutoff (Hz), Right cutoff (Hz), Left resonance, Right resonance | 1-4 | as saved |
| 5 | Slope (dB/oct) | 5 | as saved |
| 6 | Output (dB) | 6 | as saved |
| 7 | **Start delay (seconds / beats)** | new | 0 |
| 8 | **Play for (seconds / beats, 0 = always)** | new | 0 |
| 9 | **Rest for (seconds / beats, 0 = always)** | new | 0 |
| 10 | **Transport unit** `{Seconds, Beats}` | new | 0 Seconds |
| 11 | **Output at rest** `{Pass-through, Silence}` | new | 0 |
| 12 | Drift target | 7 | as saved |
| 13-14 | Drift up amount, Drift down amount (per target, in the Drift amount unit) | 8-9 | as saved |
| 15 | **Drift amount unit (per target, Target default where it cannot fit)** | new | 0 |
| 16 | Drift period (per target, 0 = off) | 10 | as saved |
| 17 | Drift period unit (all targets) | 11 | as saved |
| 18 | Drift shape (per target) | 12 | as saved |
| 19-20 | Drift play for, Drift rest for (per target) | 13-14 | as saved |
| 21 | **Rest mode (for Drift)** `{Walk through, Freeze in place}` | new | 0 |
| 22 | **Ramp** `{Ramp 1 .. Ramp 8}` | new | 0 Ramp 1 |
| 23 | Ramp time unit (per ramp) | 17 | as saved |
| 24 | Ramp engage (per ramp) | 21 | as saved |
| 25 | **Rest mode (for Ramp)** (per ramp) `{Walk through, Freeze in place}` | new | 0 |
| 26 | Ramp target | 15 | as saved |
| 27 | Ramp by (per ramp and target, in the Ramp by unit) | 16 | as saved |
| 28 | **Ramp by unit (per ramp and target, Target default where it cannot fit)** | new | 0 |
| 29 | **Ramp shape (per ramp and target)** `{Linear, Cosine, Logarithmic, Exponential}` | new | 0 |
| 30 | Ramp duration (per ramp and target, in ramp time units) | 18 | as saved |
| 31-32 | Ramp play for, Ramp rest for (per ramp and target) | 19-20 | as saved |
| 33 | Ramp start delay (per ramp and target, in ramp time units) | 22 | as saved |
| 34 | **Ramp start delay counts from (per ramp and target)** `{From play start, From ramp end, From ramp end incl. play/rest for}` | new | 0 |

Every new control is off or on its old meaning, so the saved copy sounds the same: its one
ramp becomes Ramp 1, counting from play start, Linear, walking through rests.

**THE RAMP BLOCK BELOW IS WRONG, 2026-09-14 -- do not build it.** It puts the Ramp selector
above the target selector, from a note that inverted Rozaya's words (`multi-ramp.md`, first
Settled item: target list first, then ramp selector). Rozaya caught it: *"this goes against
some shit"*, *"ramps and all that shit is replacement for automation"*. Rows 22-34 are
re-authored: Ramp target, then Ramp, then every ramp setting, none shared (Rozaya, 2026-09-14,
`multi-ramp.md`: *"Why is any of that globally affecting all the ramps?"*). Labels follow
Passage's.

**`Rest mode (for Drift)` at the end of the Drift block, decided.** Offered against the
transport block, next to Play for / Rest for; Rozaya, 2026-09-14: *"I'd rather have it in the
drift section. Otherwise we get slider scatter stuff"*. So each rest switch lives in the block
it freezes, which Part 2's "what happens at rest" line in the transport does not yet say.

## What Rozaya decided for Veil

- **Transport unit takes Drift's units, `{Seconds, Beats}`.** Rozaya: *"play/rest for should
  have the same units as drift does"*, *"Just for that thing. that's literally all I meant,
  that thing has drift already"*.
- **Walk or freeze: TWO switches.** Offered one, `Rest mode (for Drift and Ramp)`; Rozaya:
  *"drift and/or ramp. if it's gonna be like that it needs both as distinct shit"*, then
  *"Drift is its own thing. ramp is its own thing. when the 8 ramps come in, the distinction
  is going to be even more important"*. Every other plugin's walk-or-freeze switch freezes its
  own motion and leaves Drift and Ramp running; Veil has none, so Veil is the first where a
  rest can freeze Drift or Ramp. R27 now gives both to all 19 plugins with Drift and Ramp.
- **The eight ramps as `multi-ramp.md` settles them**, including `Rest mode (for Ramp)` per
  ramp and the three "counts from" options (Rozaya's names).

## What each new thing does (mine, to be measured)

- **Start delay** holds everything -- filter at its set values, every drift and ramp clock
  still -- and `Output at rest` decides what is heard meanwhile, as Passage's does.
- **Play for / Rest for** alternate in the Transport unit. **Freeze** holds that clock: Drift's
  phase, its random step and its own play/rest count; a ramp's progress, its start-delay count
  and its staircase count. **Walk through** runs them unheard. Output at rest as Passage's.
- **Ramp shape** bends each ride with `apply_curve`, copied from the Sweeping Filter (identical
  in the six that have it). It bends the output of progress, so the staircase invariant holds:
  a stepped ride and a smooth twin still land together (`planned-features.md`, Entry 1).
- **Counts from:** `From play start` is today's behaviour. `From ramp end` starts when the same
  target's ride in the ramp before was DUE to end; `From ramp end incl. play/rest for` waits for
  its REAL end, after rests and Engage pauses (Rozaya: *"Count it yeah"*). A ramp before that
  never moves the target is skipped back past; one never engaged keeps its place.
- **Defaults for Ramps 2-8, not yet asked:** time unit Minutes, engage Off, Walk through,
  Linear, and which "ramp end" option they count from.

## Targets, 5 -> 7

`{Left cutoff, Right cutoff, Left resonance, Right resonance, Output, Play for, Rest for}` --
Play for and Rest for appended, which is also control order (R18, R24; as Passage). Old saves
keep their indices. Drift and Ramp share the list.

Amount units by target kind (the Morpher's and Passage's `au_*`): the cutoffs are frequencies
(Semitones and Cents move them by an interval, floor 20 Hz); resonance is a 0-1 value and
output is dB, so both take every amount as it stands; Play for and Rest for are lengths in the
Transport unit.

## Save format

Magic becomes `3400000 + N_TARGETS` (3400007). Drift banks stay 16 wide and gain
`target_drift_unit`. Every per-(ramp, target) bank is 8 x 16 = 128 wide: by, duration, start
delay, play, rest, by unit, shape, counts from, and the runtime progress/delay/staircase
counters. Per-ramp banks, 8 wide: time unit, engage, rest mode. Plus `last_ramp`. Addresses
are read from the source at build (`jsfx-gotchas.md`: re-derive, never copy a map).

A 3300005 blob reads its five per-target ramp values into Ramp 1's row; 3200004 as today.

## Traps for this migration

- **The per-ramp controls on an OLD blob come from the slider line, not a bank.** Ramp 1's
  time unit and engage were saved as sliders 17 and 21. `@serialize`'s restore branch re-asserts
  visible sliders from banks; on a 3300005 read it must ADOPT sliders 23-24 into Ramp 1's banks
  instead, or it overwrites them with defaults ("migrate what was restored").
- Two nested selectors (Ramp > target) zero the selected entry on duplicate unless
  `@serialize` re-asserts them; set the Ramp selector one stage before its values in tests.
- A Beats count rescales on a tempo change, at once.

## Measured before install (the gate)

- Old build on the snapshot == new build on the migrated copy, bit-identical, noise in.
- Each new control does what it says: Start delay, Play/Rest in Seconds and Beats, both Rest
  modes each on its own (Drift frozen with Ramp walking, and the reverse), Output at rest;
  units on a cutoff (Semitones, Cents) against worked answers; each shape against
  `apply_curve`; two ramps chained under all three "counts from" options, with a rest and an
  Engage pause in ramp 1.
- Save and reopen; `jsfx_map impact` with no unanswered question; the REAPER round trip with
  REAPER in front. Page `docs/plugins/veil.md` updated with the controls.
