# Veil — the R26 / R27 layout

**Authored 2026-09-15, before any code was touched.** Nothing here is built yet. The rule
this file exists for: author the whole layout, then write ONE migration for it. A migration
written before its layout is a migration you will write again.

**Written plainly on purpose.** The first version of this file was deleted by Rozaya:
*"We need to redo this. and you need to make it so I can read it."* The shape below was
agreed in conversation, not by handing them a document.

## Why Veil goes first, and what it costs

Veil is in **one** project on the machine — the bridge test project. Everything else that
matches is inside a backup snapshot. Searched: all of `E:/reaper` and
`E:/tensor's-rpp-projects`, and REAPER's own ProjectTemplates and TrackTemplates.

So the migration is nearly free, which is exactly why Veil is the plugin to learn this on.

## What Rozaya decided, in their words

- On doing the cutoff block at the same time: *"I think we should try it. worst that
  happens is I don't use it"* (2026-09-15).
- On the group's word: *"I'd go with filter as well in case this thing expands"*.
- The two rest switches, 2026-09-13: `Rest mode (for Drift)` and `Rest mode (for Ramp)`,
  each sitting IN the block it freezes — *"Otherwise we get slider scatter stuff"*.
- Transport unit offers `{Seconds, Beats}`, because Veil has no turn of its own to count.

## The order — 35 controls, up from 22

New controls are marked NEW. Everything else exists today and moves.

```
THE FILTER                      (the group's word is at the FRONT: tap F to reach it)
 1  Filter side                 NEW   {All, Left, Right}
 2  Filter pitch mode           NEW   {Hz, Semitones, Cents}
 3  Filter note name            NEW   C-1 .. G9
 4  Filter cutoff                     was Left cutoff / Right cutoff
 5  Filter fine tune unit       NEW   {Hz, Semitones, Cents}
 6  Filter fine tune            NEW
 7  Filter resonance                  was Left resonance / Right resonance
 8  Tuning reference (Hz, all sides)  NEW
 9  Slope (dB/oct, all sides)

OUTPUT
10  Output (dB)

TRANSPORT                       all NEW; Veil has none today
11  Transport unit              {Seconds, Beats}
12  Start delay
13  Play for
14  Rest for
15  Output at rest              {Pass-through, Silence}

DRIFT
16  Drift target
17  Drift amount unit           NEW   the R26 control
18  Drift up amount
19  Drift down amount
20  Drift period unit (all targets)
21  Drift period
22  Drift shape
23  Drift play for
24  Drift rest for
25  Rest mode (for Drift)       NEW   {Walk through, Freeze in place}

RAMP
26  Ramp target
27  Ramp by unit                NEW   the R26 control
28  Ramp by
29  Ramp time unit (all targets)
30  Ramp duration
31  Ramp play for
32  Ramp rest for
33  Rest mode (for Ramp)        NEW   {Walk through, Freeze in place}
34  Ramp engage (all targets)
35  Ramp start delay
```

Why that order: it is Part 2's, top to bottom — what the plugin IS, then its output, then
transport, then drift, then ramp. A unit or mode sits immediately BEFORE the value it
qualifies; a shape selector sits AFTER its value.

## The targets — 13, up from 5, in control order

```
0  Cutoff (all sides)      5  Right fine tune       10  Tuning reference
1  Left cutoff             6  Resonance (all sides) 11  Output
2  Right cutoff            7  Left resonance        12  Play for
3  Fine tune (all sides)   8  Right resonance
4  Left fine tune          9  Slope is NOT a target -- it is a shape picker
```
...and 13 is `Rest for`. Drift and Ramp share this one list.

The per-target banks are 16 wide today and 13 targets fit, but **widen them to 32** in the
same change: the next target added would otherwise be a second migration.

## The migration

- `@serialize` magic goes from `3300000 + N_TARGETS` to a new base, so a 3300005 save is
  read at its own width of five and remapped. Old target 0-3 were Left cutoff, Right
  cutoff, Left resonance, Right resonance and 4 was Output; they become 1, 2, 7, 8 and 11.
- The slider line of the one live project is rewritten by a script built on
  `tools/rpp_sliders.py`, old position to new: 1 and 2 both become 4 (one per side, via the
  side picker's banks), 3 and 4 become 7, 5 becomes 9, 6 becomes 10, and everything from
  the old 7 upward shifts into the new drift and ramp positions above.
- **The check before it is called done:** old plugin on the old project and new plugin on
  the migrated project must render bit-identical, since nothing here is meant to change the
  sound. `jsfx_run --csv`.
