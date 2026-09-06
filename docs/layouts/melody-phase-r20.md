# Melody Phase — the R20/R21 conversion

Written 2026-09-05. **Status: AUTHORED, awaiting review. Nothing built.**

Rozaya: *"Melody needs what daple just got I think rofl."* It does. This is the
delta from the layout that landed on 2026-09-02 (`melody-phase.md`), not a
re-listing of it.

**This is Melody's SECOND migration**, and that is knowingly spending the risk
twice. It is worth it because the alternative is Melody keeping a sync mechanism
no other plugin has, which is exactly the "a thing learned on one plugin is not
true of the others" problem the whole sweep exists to remove.

---

## What changes

### 1. The rate block becomes the suite's (R20 + R21)

**Today** Melody carries the older R11 shape — four controls:

```
1  Rate value
2  Rate mode                {BPM, Seconds, Hz}
3  Sync to host             {Off, On}
4  Host sync target         {Rate value, Pan base rate}
5  Every N beats (per sync target)
```

**After** — two controls, the same as everywhere else:

```
1  Rate value
2  Rate mode                {BPM, Seconds, Hz, Every N beats, N per beat}
```

Sliders 3, 4 and 5 are **deleted**.

### 2. The pan gets its own rate mode

`Pan base rate` currently has **no mode of its own** — it is handed the
sequencer's, at `melody_phase.jsfx:1116` and `:1492`. That is the missing control
that caused R11's target selector to be built in the first place, and R20 says
every rate carries its own complete pair.

So a **`Pan rate mode`** is added immediately after `Pan base rate`, with the
same five entries. The pan can then be synced while the sequencer runs free, or
the reverse, with no selector reaching across.

### 3. Net slider count

76 → **74**. Three deleted, one added, everything above renumbered.

---

## The measurement, taken before authoring this

**73 instances across 7 projects** — `melodic` (4), `outcoming` (19),
`slow-summer` (6), `upswing` (17), `simple-sequence` (12),
`simple-sequence-check` (12), `testing-proof of concept` (3). Four are finished
work, ear-tested 2026-09-04.

**27 are synced, 46 are free-running.** Of the 27:

| Every N beats | instances |
|---|---|
| 2 | 12 |
| 4 | 12 |
| 1 | 1 |
| 0.5 | 1 |
| 0.333333 | 1 |

**Not one of the 27 targets the pan.** Every single one is on `Rate value`, which
is the measurement that killed R11's selector in the first place — the capability
it exists for has never been used.

That `0.333333` is worth keeping in view: it is *every third of a beat*, three
cycles per beat, and no ratio menu would have offered it. It is also the instance
that will read most clearly after R21, as **`3` in `N per beat`**.

---

## The migration

**For the 27 synced instances:**

- `Rate mode` → **3** (`Every N beats`)
- `Rate value` → the stored `Every N beats` value

Their existing Rate value and Rate mode are DISCARDED, and that is correct: while
`Sync to host` is On those two are not consulted for the synced target, so they
hold whatever was last set free-running. Overwriting them is what preserves the
sound.

**For the 46 free instances:** nothing changes. Rate mode indices 0, 1 and 2 keep
their meanings exactly.

**Optional refinement, and it needs Rozaya's call:** the single `0.333333`
instance could instead become `3` in `N per beat`, which is the same speed
written honestly. It is one instance, it is the only one that reads badly as a
beat count, and converting it is the difference between a number you can read and
a number you have to trust. **Recommended, but it is a judgement about how it
reads, not about correctness.**

---

## What must be checked before building

- **The aggressive-restructuring window is CLOSED** as of 2026-09-05 — a project
  has been saved on current builds. Re-scan the project files at migration time
  rather than trusting the counts above.
- `docs/open-bugs.md` has an open entry against Melody (instances arriving out of
  alignment in `simple-sequence`). **Read it before touching this plugin**, and
  re-test that bug afterwards — a fix landing near an open bug is exactly when it
  should be re-checked.
- Melody has **more than 64 sliders**, so its `.RPP` value lines carry the `""`
  marker at index 64. `tools/rpp_sliders.py` handles it; nothing may re-derive
  the format.
- Bump the `@serialize` magic in the same commit as the renumber. That is the
  only thing that made the 2026-07-02 slider-insert repairable.
