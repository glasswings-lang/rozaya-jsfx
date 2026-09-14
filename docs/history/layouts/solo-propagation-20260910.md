# Solo in every plugin that has voices or bands — authored 2026-09-10

**Status: BUILT, MIGRATED AND INSTALLED 2026-09-10. NOT HEARD.** Measured with
`jsfx_run`, per plugin: nothing soloed renders identical to the morning's build;
a soloed switched-off voice is heard (Polyrhythm at exactly 440 Hz; Shepard Tone
identical to that voice alone; Melody only on its own note and only in its own
turns); soloing two hears both; levels do not jump. Resonance Bank: soloing a
3000 Hz band leaves 400 Hz at 0.3%, a soloed band at -60 is silent. Migrations:
Melody 73 of 73, Shepard Tone 10 of 10 (Tensor's), Resonance Bank 1 of 1, all
identical old-on-snapshot against new-on-migrated; Tensor's two silent Shepard
files checked by control name instead, 89 of 89 equal. Snapshot
`_pre-solo-20260910/`.

## Decided with Rozaya, 2026-09-10

Rozaya: *"The solow one worries me"*, then *"I say we go for it"*, and on the three
calls below, *"Then I say we do it your suggested way, that's what I would have
asked for anyway."*

- **Solo overrides Active, everywhere.** A soloed voice is heard even when its
  Active is off — the Morpher's rule. A level of −60 still sounds silent, because
  that is a level, not a switch (also the Morpher's rule).
- **Melody and Shepard Tone:** a Solo switch in each voice's row, directly after
  Active. Several can be soloed at once.
- **Resonance Bank:** one `Band solo`, per band, behind its Band selector.
- **Polyrhythm v3** changes to match, and says so on the control.
- **Melody:** a switched-off voice is not part of the sequence, and soloing one
  JOINS it to the pattern while soloed. Rozaya: *"Sollowing things that are
  switched off should bring them on anyway, that's the point of sollow"*.

Not soloed voices stay silent but keep their place: nothing about timing moves.

## Polyrhythm v3 — no layout change

`Solo this voice` becomes `Solo this voice (heard even when Active is off)`. The
audibility test becomes `any_solo ? solo : active` in the voice loop, the level
normaliser and Spread ranking. **No saved instance has a voice soloed** (all 152
read 2026-09-10), so nothing saved changes.

## Shepard Tone — 89 sliders become 97

| new | control | old |
|---|---|---|
| 1–13 | unchanged | 1–13 |
| 14 + 8v … 20 + 8v | Vn Note, Fine tune, Direction, Rate, Gain, Pan, Active | 14 + 7v … 20 + 7v |
| 21 + 8v | `Vn Solo (heard even when Active is off)` | new, Off |
| 78–97 | Start delay … Ramp start delay | 70–89 |

v is 0 for V1 through 7 for V8. The voice read is `slider(base + k)` with
`base = 14 + 7i`, so it becomes `14 + 8i` — a renumber alone would miss it. A
voice's controls show when Active **or** Solo is on. The level count follows what
sounds. Blob format unchanged; magic `2300040 → 2400040` as the layout witness,
old accepted. **No instances in Rozaya's projects; 10 in 3 of Tensor's files.**

## Melody Phase — 105 sliders become 113

| new | control | old |
|---|---|---|
| 1–27 | unchanged | 1–27 |
| 28 + 8v … 34 + 8v | Vn Note, Pitch, Fine tune, Next voice in, Note duration, Gain, Active | 28 + 7v … 34 + 7v |
| 35 + 8v | `Vn Solo (heard even when Active is off)` | new, Off |
| 92–113 | Master gain … Ramp start delay | 84–105 |

Blob format unchanged; magic `2500055 → 2600055`, old accepted. Over 64 sliders
before and after, so the `""` marker applies at both ends. **73 instances, 7
projects.**

## Resonance Bank — 27 sliders become 28

| new | control | old |
|---|---|---|
| 1–9 | Input gain, Mode, Band selector, Frequency … Order | 1–9 |
| 10 | `Band solo` | new, Off |
| 11–28 | Wet/dry … Ramp start delay | 10–27 |

A 16-slot `band_solo` bank joins the blob: magic `2016005 → 3016005`; a v1 or v2
save reads with every band unsoloed. The band's audibility becomes
`any_solo ? solo : 1` on top of its gain. **1 instance.**

## Verify, each plugin

Nothing soloed: old and new render identical on a fresh instance and on every
migrated instance. Soloing a switched-off voice or band is audible and silences
the rest; soloing two hears both; the level of what is left does not jump. The
voice or band read back after a save and reload.
