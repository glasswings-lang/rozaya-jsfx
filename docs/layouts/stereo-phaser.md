# Stereo Phaser — the R26 / R27 layout

**Authored 2026-09-16, before any code.** Agreed in conversation, not by handing Rozaya a
document. Second plugin of the unit pass; Veil was first
(`docs/history/layouts/veil.md`), and almost everything here is Veil's shape again.

## What Rozaya decided, in their words

- The sweep's two ends become ONE block behind a picker, not two blocks: *"I like your idea.
  I highly suspect the older one was me + claude on a me tired day heh"*. The reasoning
  offered, and accepted: the gap between 300 Hz and 1500 Hz IS the sweep -- how far the
  notch travels -- so the thing you reach for is usually the whole sweep, not one end.
- Going ahead at all: *"Go ahead"*.

## What it costs

Four live instances, counted 2026-09-16 across all of `E:/reaper` and
`E:/tensor's-rpp-projects` plus REAPER's ProjectTemplates and TrackTemplates, ignoring
backup snapshots.

## The order — 38 controls, up from 25

`Host ratio` (old slider 3) is DELETED. It was retired on 2026-09-04, hidden since, and
its code sits behind a literal `0 ? (` so it does nothing at all. The source already says
*"It gets deleted in this plugin's own reorder pass"* -- this is that pass.

```
THE SWEEP                      the group's word is at the FRONT: tap R to reach it
 1  Range end               NEW   {Both (keeps the gap), Bottom, Top}
 2  Range pitch mode        NEW   {Hz, Semitones, Cents}
 3  Range note name         NEW
 4  Range frequency               was Range min (Hz) / Range max (Hz)
 5  Range fine tune unit    NEW   {Hz, Semitones, Cents}
 6  Range fine tune         NEW
 7  Tuning reference (Hz, all ends)   NEW
 8  Feedback
 9  Stages                        a structural count, so not a target

ITS RATE                       the mode comes BEFORE the value (Part 2)
10  Rate mode
11  Rate value                    was plain `Rate`

STEREO
12  Stereo spread (degrees)

OUTPUT
13  Wet/dry mix

TRANSPORT                      all NEW; the Phaser has none today
14  Transport unit          {Cycles, Seconds, Beats} -- Cycles, because it HAS a turn
15  Start delay
16  Play for
17  Rest for
18  Output at rest          {Pass-through, Silence}

DRIFT
19  Drift target            20  Drift amount unit   NEW
21  Drift up amount         22  Drift down amount
23  Drift period unit (all targets)                 24  Drift period
25  Drift shape             26  Drift play for      27  Drift rest for
28  Rest mode (for Drift)   NEW

RAMP
29  Ramp target             30  Ramp by unit        NEW
31  Ramp by                 32  Ramp time unit (all targets)
33  Ramp duration           34  Ramp play for       35  Ramp rest for
36  Rest mode (for Ramp)    NEW
37  Ramp engage (all targets)                       38  Ramp start delay
```

## `Both (keeps the gap)`, again

Same as Veil's, and for the same reason: option 0 shows the MIDPOINT of the two ends and
applies your CHANGE to both, clamped so neither end runs off its range and squeezes the
gap. Moving it slides the whole sweep up or down at a fixed width. `Bottom` and `Top` edit
one end each, and both ends are always live.

## The targets — 13, up from 6, in control order

```
0  Range frequency (both ends)   5  Top fine tune        10  Wet/dry mix
1  Bottom frequency              6  Tuning reference     11  Play for
2  Top frequency                 7  Feedback             12  Rest for
3  Range fine tune (both ends)   8  Rate value
4  Bottom fine tune              9  Stereo spread
```

`Stages` stays out: R24 excludes structural counts. Per-target banks widen from their
current width to 32, so the next target added is not a second migration.

## The migration

- `@serialize` magic bumps; an older save is read at its own width and its six targets
  remapped into the new thirteen: Rate 0 -> 8, Range min 1 -> 1, Range max 2 -> 2,
  Feedback 3 -> 7, Stereo spread 4 -> 9, Wet/dry 5 -> 10.
- The slider line of each of the four instances is rewritten old position to new by a
  script built on `tools/rpp_sliders.py`. Old 4 and 5 (the two ends) become per-end banks
  and the visible control takes their midpoint, exactly as Veil's cutoffs did.
- **The check before it is called done:** old plugin on the old project and new plugin on
  the migrated project must render bit-identical with the drift amounts at zero. With a
  drift running they will NOT match, and that is not a fault -- the drift's starting phase
  is seeded from `rand()` per target, is never serialized, and is redrawn on every play.
  Veil proved that on 2026-09-15.
