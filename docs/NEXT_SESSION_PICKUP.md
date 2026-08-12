# Next session pickup notes — updated 2026-08-11

Living handoff notes. **Everything currently open is an ear-test, not code.**
The tempo-sync sweep is finished and unheard; the two older Passage threads are
still where they were.

## Where the work is sitting

On branch **`feature/host-tempo-sync`**, 20 commits ahead of `master`, which is
itself 4 commits ahead of `origin/master`. Nothing merged, nothing pushed.
Merge is a clean `--ff-only` whenever the ear-tests pass.

Installed copies in `<REAPER resource>/Effects/glasswings/` are current, each
backed up as `*.pre-hostsync.bak`. So you can test in REAPER right now, and
restoring a single plugin is one file copy.

## Thread 1 — the Host x sweep: 17 plugins, NONE ear-tested

Full record in `docs/planned-features.md` ("Sweep progress"). Short version: a
`Host x` rate mode that follows the project tempo as a **multiplier**, not a
note-division grid, because the suite is phase music and a multiplier preserves
any ratio — including irrational ones — through a tempo change.

**Done and heard:** `melody_phase` v1 only, on 2026-08-11 — two instances
staggered by Start Delay, handing off correctly. That's it. So the mechanism
compiles, loads, follows the tempo, and Start Delay is right *in one plugin*.

**Done and unheard:** the other 16. `melody_phase_v2`, `shepard-tone`,
`rhythm-track`, `polyrhythm_phase`, `polyrhythm_phase_v3`,
`Full_Feature_Tremolo`, `full-feature-sweeping-filter`, `shepard-scale`,
`heartbeat gen`, `womb_sound_generator_v3`, `stereo-phaser`, `bubbler`,
`dapple`, `resonance_bank`, `sweep-dwell-filter`, `veil`.

**There is a step-by-step checklist for this:
[`docs/host-sync-ear-test.md`](host-sync-ear-test.md)** — five tests, ~15
minutes, with the expected result and the failure shapes for each. Use it
rather than reconstructing the plan below from scratch.

**Where to start listening, in order:**

1. **`rhythm-track`** — the only unambiguous test in the suite. It's a
   metronome: Rate Mode to Host x, Tempo to 1, run REAPER's own click, they
   lock or they don't.
2. **`sweep-dwell-filter`** — nearly as unambiguous. Cycle mode to Host x at
   the default 12 beats; the dwell turnaround is an audible event you can place
   against a beat.
3. **`Full_Feature_Tremolo`** — it's in `simple-sequence.RPP` (2 instances), so
   it can be heard in a real project rather than a test bed.

**Do NOT gate on `shepard-tone`.** A Shepard-Risset glissando is engineered to
defeat pitch perception, so it's a poor subject for judging whether a rate is
right.

**Never heard at all, in any plugin:** Speed Ramp and Drift under Host x, and
pan following the tempo. Those are the parts most likely to be wrong, because
they don't ride `dt` and each needed the tempo factor applied by hand.

**If something is subtly out rather than plainly wrong, check Start Delay
first.** That's the bug that shipped for an hour in Melody Phase, and its
symptom is nasty precisely because it's partial: one timing wrong by exactly
the tempo ratio while everything around it is right reads as drift or
sloppiness, not as a units bug.

**Deliberately NOT retrofitted, don't helpfully fix:** `spectral_vowel_morpher`,
`spectral_vowel_passage`, `breath_gen` — all three are overdue for rewrites and
bolting Host x onto code about to be replaced is wasted work.
`harmonic_sculptor` and `sustain_looper` are out entirely (nothing in them is
pacing).

## Thread 2 — Passage fade curves: one ear-test, possibly already stale

`Fade in shape` / `Fade out shape` (Linear/Cosine/Logarithmic/Exponential,
default Cosine) were added on 2026-07-25 because the linear-amplitude leg fades
sounded abrupt at the quiet end.

**Open question:** does Cosine-default actually resolve that, or was the fade
just too *short*? Test: one long Cosine fade. Still abrupt → look further;
smooth → done. Linear is kept for anyone who wants the old edge.

This may have been answered in passing during the 07-28 session, which cleared
several other Passage items — but it was never recorded either way, so treat it
as open until it's heard on purpose.

## Thread 3 — the Passage short-grain crackle is still unexplained

**What was claimed:** sizing the FFT to the grain (instead of fixed at max)
would kill the evenly-spaced crackling at short Wash grain settings. Theory:
cost-per-grain was constant while grain-rate scales inversely with length, so
shortening the grain multiplied CPU.

**What happened:** ear-tested. The crackle is still there, evenly spaced, at
short grain. The theory was wrong or incomplete. The FFT-sizing change is kept
because it does cut CPU on wash-heavy projects; it just wasn't the fix. The
manual's "short grain works now" claim is retracted with a known-limitation
note in its place.

Two things that are **not** this bug, so they don't need re-checking: the
gap-handoff `flush_accum_pending` (a handoff artifact, this crackle is
continuous-play), and the 2026-07-10 Morpher crackle, which was muted layers
burning CPU and is fixed.

**Questions to actually ask, by ear, one at a time:**

1. Is the crackle rate tied to grain rate? If yes it's still per-grain but not
   CPU — maybe accumulator-wrap alignment or `gen_grain` state discontinuity.
2. Is it tied to hop rate? Same rate as grain rate since HOP = W/4, so hard to
   separate — design the test before trusting the answer.
3. Is it a phase discontinuity at the seam? sqrt-Hann should cross-fade
   cleanly, but consecutive grains with very different random `phase[]` arrays
   that overlap in the accumulator could click.
4. Is the auto-gain smoother reacting per-grain? `rms_smooth` updates per
   grain; a discontinuous jump in `gnorm` means the next grain starts at a
   different level than the previous one's tail.
5. Is GFFT actually the right size, or does a power-of-two mismatch leave the
   last few samples unwritten?

**Cheap isolation:** pure sine at slot 0, silence at slot 1, focus slot 0,
sweep Wash grain 680 → 5 and find where the crackle starts. Then look at what
changes structurally at that threshold (FFT size doubling? hop crossing 1
sample?).

**Don't repeat the mistake:** don't confidently theorise from the code alone.
Each hypothesis gets tested by ear with a controlled signal.

---

## Settled since the last version of this file, so it doesn't resurface

- The morpher-v2 → **Spectral Vowel Passage** split shipped and passed.
- Passage's **gap-bleed fix**, the **voice phase handover** click fix (the
  "random CPU bug" that turned out to be every slot handoff dropping its
  phases), **Capture average**, and **Overtone** — all ear-tested. Overtone was
  rejected once and rebuilt as a power-normalized *lift* rather than a duck.
- **Morpher's Capture average went global.**
- **Melody Phase v1 came back out of the archive** — five shipped projects were
  on v1 and zero on v2, so it was never actually superseded. v1 → v2 is not a
  filename swap and no migration exists.
