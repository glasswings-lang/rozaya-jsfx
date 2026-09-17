# The Sweeping Filter — its whole turn, authored 2026-09-17

Rozaya opened it in REAPER and read every backlog item against the plugin, as with Sweep Dwell:
*"We should keep going"*. Two things came from looking at it:

- **`Ramp time unit` moves under `Ramp duration`.** Rozaya: *"Ramp's time unit is 1, in a weird spot
  and 2, effecting all of the ramp stuff, which isn't great."* Asked whether under the duration was
  right: *"That sounds right yeah."* Sweep Dwell has the same awkward spot (I built it yesterday) and
  gets the same move in the same commit.
- **`Depth (%)` says what it is a percent OF.** Rozaya: *"Yes, yes I do. because I had no idea before
  this that that's what it was for."* It becomes `Depth (% of the Low-to-High range)`.
- **Nothing else moves.** Rozaya: *"Other than that, I like the current slider order, btw"*.

Saved copies: **21 in 12 projects**, finished ones among them (strangeness, the-sound-of-a-drain x5,
life-is-worth-it, bilateral-*, infantile). Every copy is measured old-against-new before anything is
written; none of this is meant to change a saved sound.

## What it gains

1. `Drift period unit` and `Ramp time unit` per target, plus `Drift amount unit` / `Ramp by unit`
   (the 13-entry list) — R26, the shape Veil, the Phaser, Passage and Sweep Dwell have.
2. `Drift movement mode` per target (R23), and `Drift rest mode` / `Ramp rest mode` (R27).
3. `Play for` and `Rest for` as drift and ramp targets (R24), appended as targets 17 and 18, so no
   saved target selection renumbers.
4. One `Transport unit` {Cycles, Seconds, Beats} over Start delay, Play for and Rest for. Start delay
   counted in the Rate mode's units; Play for and Rest for counted LFO cycles.
5. Every unit switch keeps the thing and converts the number: Rate mode, both pitch modes and fine
   tune units, Pan sweep rate mode, Transport unit, Drift period unit, Ramp time unit. Cycles is not a
   fixed length, so to or from Cycles the number stays.
6. The note name works in every pitch unit, both ways (it only appeared on Semitones).
7. R9: `Resonance`, `Pan spread` and `Wet/dry mix` become percents, 0..100; drift and ramp amounts
   aimed at those three scale by 100 in the migration.
8. The pan block: the suite's order, `(Flipped)` retired into `Pan direction`, and the two choices it
   is owed — `Accent L / Weak R` and `Sway`. Word for word Sweep Dwell's, 2026-09-17.
9. `Pan sweep every` gains {Every N cycles, N per cycle}.
10. `LFO at rest` becomes `Rest mode (LFO)`.
11. The page is rewritten from the plugin (15 findings today).

## The order, in full (1..62; NEW or CHANGED marked)

```
 1 Low pitch mode              21 Release (% of cycle)          41 Output at rest
 2 Low note name        CHANGED 22 Release shape                42 Drift target        CHANGED (19)
 3 Low frequency               23 R channel phase offset        43 Drift up amount
 4 Low fine tune               24 Phase mode                    44 Drift down amount
 5 Low fine tune unit          25 Pan enabled                   45 Drift amount unit   NEW
 6 High pitch mode             26 Pan mode           CHANGED    46 Drift period
 7 High note name       CHANGED 27 Pan direction      NEW        47 Drift period unit   CHANGED
 8 High frequency              28 Pan spread (%)     CHANGED    48 Drift movement mode NEW
 9 High fine tune              29 Pan glide (ms)                49 Drift shape
10 High fine tune unit         30 Cycle steps                   50 Drift play for
11 Tuning reference (Hz)       31 Pan sweep rate                51 Drift rest for
12 Resonance (%)        CHANGED 32 Pan sweep rate mode           52 Drift rest mode     NEW
13 Slope (dB/oct)              33 Pan sweep every mode NEW      53 Ramp target         CHANGED (19)
14 Rate value                  34 Pan sweep every    CHANGED    54 Ramp by
15 Rate mode                   35 Wet/dry mix (%)    CHANGED    55 Ramp by unit        NEW
16 LFO start phase             36 Transport unit     NEW        56 Ramp duration
17 On duration (% of cycle)    37 Start delay                   57 Ramp time unit      MOVED
18 Depth (% of the Low-to-High range)  CHANGED                  58 Ramp play for
19 Attack (% of cycle)         38 Play for                      59 Ramp rest for
20 Attack shape                39 Rest for                      60 Ramp rest mode      NEW
                              40 Rest mode (LFO)    RENAMED    61 Ramp engage
                                                                62 Ramp start delay
```

Targets, in control order: `Low frequency, Low fine tune, High frequency, High fine tune, Tuning
reference, Resonance, Rate value, On duration, Depth, Attack, Release, R channel phase offset, Pan
spread, Pan glide, Pan sweep rate, Pan sweep every, Wet/dry mix, Play for, Rest for`.

Pan: `Mono, Alternating, Alternating every 2, Alternating every 4, Alternating every 8, Accent L /
Weak R, Distributed, Distributed (Ping-pong), Converging, Converging (Ping-pong), Diverging, Diverging
(Ping-pong), Linked Sweep, Sway, Pan Sweep`, with the old-to-new map Sweep Dwell's migration uses.

## The migration (`tools/swf_migrate_r26r27_20260917.py`)

Blob 2300017 -> 2400019; the plugin reads only the new one, and every saved copy is rewritten.

- Sliders: 1..26 keep their numbers; 27..54 move up by the insertions above (27->28, 28->29, 29->30,
  30->31, 31->32, 32->34, 33->35, 34->37, 35->38, 36->39, 37->40, 38->41, 39->42, 40->43, 41->44,
  42->46, 43->47, 44->49, 45->50, 46->51, 47->53, 48->54, **49->57** (the move), 50->56, 51->58,
  52->59, 53->61, 54->62).
- Values: Resonance, Pan spread, Wet/dry x100; drift up/down and ramp by for targets 5, 12 and 16
  x100; the pan choice and its direction; the transport unit as Sweep Dwell's does it (Start delay 0
  -> Cycles and nothing moves; a delay alone -> Seconds; both -> Seconds, Play/Rest converted with the
  saved cycle length, which is what they counted).
- Banks: the new per-target banks are seeded to what the plugin did — the one shared period unit and
  ramp time unit to every target, the amount units to `Target default`, movement mode to `On a clock`
  (its live reading), both rest modes to `Walk through` (it had no gate).

## Checks before installing

- `tools/sweeping_filter_checks/unit_switches.py` — every unit switch converts, every selector switch
  does not, the per-target settings ride with their target.
- `tools/sweeping_filter_checks/sound_checks.py` — each new control changes the sound; every pan
  choice moves and `Pan direction` mirrors it.
- `tools/sweeping_filter_checks/verify_live.py` — all 21 copies, old build against new: bit-identical.
- `tools/page_controls.py` — 0 findings for this plugin afterwards.
