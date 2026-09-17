# Womb — the mechanical half of its turn, authored 2026-09-17

Rozaya, asked whether to start with breath-and-sigh (a design conversation) or the rest:
*"Start with the half that doesn't need a giant design convo lol"*. So this layout is everything
owed that needs no new decision. **Breath and sigh, and breath catches, are NOT in it** and keep
their place in `docs/planned-features.md`.

Saved copies: **10, one in each of 10 projects** -- the tenth is `scattered.rpp`, whose extension is
lowercase, which every earlier count of this plugin had missed. Six different saved formats between
them, including two the plugin never read (see the migration).

## The one thing that changes the sound

**The Breath high-pass gets a proper filter.** Rozaya, 2026-09-13: *"We need a better filter."*
Today it is one pole of `2*sin(pi*f/sr)` capped at 0.98, which stops moving near 7200 Hz of the
20000 the control offers — the cap IS the ceiling Rozaya heard. It becomes the TPT one-pole the
sweeping filters use, which is accurate to the top of the range.

Agreed condition, 2026-09-13: **measure every saved Womb copy old against new before installing,
and say how big any difference is.** At the default 80 Hz the two are close but not identical, so
the number goes to Rozaya rather than being called "no change".

## What it gains, none of it changing a saved sound

1. `Drift amount unit` and `Ramp by unit`, per target (R26) — the 13-entry list.
2. NOT the two rest switches (R27). Womb has no plugin-wide rest for them to gate -- its three
   Play/Rest pairs each rest their own part -- so a switch would have nothing to freeze. Left out
   rather than given an invented meaning; it belongs with breath-and-sigh if Womb ever gains one.
3. `Drift period unit` and `Ramp time unit` become per target (the `(all targets)` mark comes off).
4. `Start delay` gains a `Transport unit` {Seconds, Beats}, defaulting to Beats, which is what it
   counts today. The three Play/Rest pairs stay as they are: each already counts its own part's
   own pulse (heartbeats, breaths, heartbeats), which is what the suite's rule asks for.
5. R9, no control counting in fractions of one. **Volumes become dB, -60 (off) to +24**: S1 volume,
   S2 volume, HB master volume, Breath volume, Bloodflow volume. **Everything else becomes a
   percent, 0..100**: Brightness, the four breath fades, Breath stereo width, Bloodflow attack,
   Bloodflow decay, Bloodflow dicrotic level, Bloodflow resonance, Bloodflow stereo width.
   Every one is a value migration, and drift and ramp amounts aimed at them are converted too.
6. A pitch block for each of the three frequencies that has none — Breath high-pass, Breath
   post-filter, Bloodflow filter — each `mode, note name, value, fine tune unit, fine tune`, placed
   beside its own part. Rozaya on the pairing: *"We can try it; I won't know until I see it."*
7. Every unit switch keeps the thing and converts the number, as both filters got today.
8. The page: the stale sigh line is corrected and the forty controls it never wrote up are written
   up. One finding is left, and it is a real defect rather than a page fault -- `Fade mode` is
   declared `<1,4,1>` with four options, one-based where every other picker is zero-based, so tools
   read its default one off. Its own small migration is in the backlog.

## Control order

Everything keeps its place; the new controls sit with what they belong to. In numbers, the blocks
that grow are: the breath filters (45-47 become five-control blocks each), the bloodflow filter
(58-59 likewise), Start delay gains its unit above it, and the Drift and Ramp blocks gain their
amount unit after the amounts and their rest mode after play/rest -- the shape Sweep Dwell and the
Sweeping Filter now have. `Ramp time unit` sits under `Ramp duration`, as it does in both filters
since today.

## The migration (`tools/womb_migrate_mechanical_20260917.py`)

Blob magic bumped; every saved copy rewritten, old formats not read by the plugin.

- The slider line: every control to its new number, with the R9 conversions applied
  (volume 0..1 -> dB via `20*log10(v)`, with 0 becoming -60; everything else x100).
- Drift and ramp amounts aimed at a converted target are converted the same way; a dB target's
  amount becomes a dB amount, which is what `Target default` now means for it.
- The new per-target banks are seeded from the one shared value (period unit, ramp time unit) and
  the amount units to `Target default`.
- Six saved formats exist. 2600049, 2400011 and 2100010 are read as the plugin reads them and
  remapped onto the 49 targets. TWO copies hold an UNVERSIONED blob the plugin skips entirely, and
  measuring the old build on them showed what that means: the first @slider pass reads the saved
  selector as a switch, so a copy showing target 0 keeps its drift or ramp and a copy showing any
  other target lost it long ago. The migration carries across exactly that, per selector.

## Checks before installing

- `tools/womb_checks/unit_switches.py` — every unit switch converts, selectors leave numbers alone.
- `tools/womb_checks/sound_checks.py` — each new control changes the sound; the new pitch blocks
  reach the frequencies their old controls did.
- `tools/womb_checks/verify_live.py` — all 10 copies, old build against new, level within 0.5 dB
  and every control in place. Measured 2026-09-17: every copy within 0.01 dB, so the new filter
  changes nothing audible at the settings actually saved. What it DOES change, measured on the
  breath alone with the post-filter opened to 4000 Hz: at a 4000 Hz high-pass old -54.8 dB against
  new -48.0, at 7000 old -79.4 against new -53.3, at 12000 and 18000 old -86.3 both times (it had
  stopped) against new -59.7 and -69.0. At the default 80 Hz, 0.1 dB apart.
- `tools/page_controls.py` — 0 findings for Womb afterwards.
