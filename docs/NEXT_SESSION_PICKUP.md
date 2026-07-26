# Next session pickup notes — updated 2026-07-25

Living handoff notes. Most of what was open on 2026-07-22 shipped on 07-25; the
one standing technical thread is the short-grain crackle (bottom), plus one
ear-test loose end on Passage's new fade curves.

## Done 2026-07-25 — Spectral Vowel Passage

The morpher-v2 → **Spectral Vowel Passage** split shipped and passed ear-test
(sibling to Morpher, "a route with stops"): rename complete across source,
manual, plugins index, top-level README, and the migration tool
`tools/morpher_to_passage.py`. Full record in
`docs/morpher-v2-slot-timing-design.md`. (An earlier candidate name, "Loom",
was considered and dropped for Passage — noted only so the name doesn't
resurface as an open question.)

Three follow-on fixes on Passage, all committed and ear-tested:

- **Gap handoff no longer bleeds** (commit `811709f`). With crossfade OFF + a
  gap, the previous slot's wash tail was audible under the next slot's fade-in.
  Cause: the overlap-add accumulator was never emptied at a sequential handoff,
  so grains written during the fade-out/gap were read back at full as the next
  slot faded in. Fix: `clear_accum()` at the sequential leg advance —
  crossfade-ON handovers untouched, since that tail *is* the blend.
- **Fade in/out shape (curve) added** (commits `ad287a0` feature, `73f7d79`
  reposition). The leg fades were linear-amplitude ramps, which sound abrupt at
  the quiet end. Added global `Fade in shape` / `Fade out shape`
  (Linear/Cosine/Logarithmic/Exponential, default Cosine), matching the
  sweeping-filter suite's Attack/Release Shape and math (`apply_curve`). Sliders
  sit at 10/11, next to the timing cluster.
  **LOOSE END (ear-test):** confirm whether Cosine-default resolves the "fades
  sound abrupt" feel, or whether it was just too-short a fade time. Test: long
  Cosine fade — if still abrupt, look further; if smooth, done. Linear is kept
  for anyone who wants the old edge.

## Done 2026-07-25 — Melody Phase v2 is now canonical

Melody Phase v2 (per-voice controls behind a single **Voice** selector,
replacing v1's forty flat sliders) is now the shipping Melody Phase. Code
committed `d9bb07d`; the manual (`docs/plugins/melody-phase-v2.md`), v1
archiving (`archive/versions/melody_phase/v1.jsfx` + `v1.md`), and the plugins-
index repoint are the follow-up commit. Same engine and feature set as v1; the
per-voice Note picker (C2..C6) is still v1's semitone-from-root system under the
hood (`note − 24` through `semitones_to_hz`), so Root Note / Center Octave
transpose every voice — the picker's names are literal only at Root C / Center
Octave 4. The manual states that plainly.

## Thread (still open): the short-grain crackle wasn't fixed

**What was claimed:** the FFT-sizing change (GFFT sized to grain instead of
fixed at max) would eliminate the evenly-spaced crackling that appears at short
Wash grain settings. Theory: cost-per-grain was constant while grain-rate scales
inversely with length, so shortening the grain multiplied CPU. Fix: shrink the
FFT per grain.

**What actually happened:** Rozaya tested by ear. The crackle is still there,
evenly spaced, at short grain. So the theory was wrong, or at least incomplete.

**Docs status:** the "short grain works now" claim in the manual is retracted,
with an honest "known limitation" note in its place. The FFT-sizing change is
kept because it does reduce CPU on wash-heavy projects; it just wasn't what
solved the crackle.

Note: the gap-handoff `clear_accum()` added this session (Passage bleed fix) is
*unrelated* to this crackle — the crackle is continuous-play at short grain, not
a handoff artifact. It only means the accumulator is now empty at the start of a
gapped slot; it doesn't touch the per-grain seam behaviour below.

**Next-session diagnostic questions to actually ask:**

1. Is the crackle-per-second rate related to grain-rate (grains per second)? If
   yes, still a per-grain issue but not CPU. Maybe accumulator-wrap alignment,
   or gen_grain state discontinuity between consecutive grains.
2. Is the crackle-per-second rate related to hop rate (hopcount reaching HOP)?
   Same rate as grain rate since HOP = W/4, so hard to distinguish.
3. Is the crackle a phase discontinuity at grain boundaries? The sqrt-Hann
   window should cross-fade cleanly, but if two consecutive grains have very
   different random `phase[]` arrays AND overlap in the accumulator, a brief
   discontinuity at the seam could click.
4. Is it the auto-gain smoother reacting per-grain? `rms_smooth` updates per
   grain — if the update produces a discontinuous jump in `gnorm`, the next
   grain arrives at a different level than the previous grain's tail: click.
5. Is GFFT actually the right size for the grain, or is there a power-of-two
   mismatch that leaves the last few samples unwritten and causes a
   discontinuity?

**Cheap way to isolate:** capture pure sine at slot 0, silence at slot 1, set to
focused audio slot 0, sweep Wash grain from 680 down to 5, listen for where
crackle starts, note the grain length. That gives the threshold. Then look at
what changes structurally near that threshold (FFT size doubling? Hop crossing 1
sample? Something else?).

**Don't repeat the mistake:** don't confidently theorise from the code alone.
Test each hypothesis by ear with a controlled signal.

---

Audio work is safe regardless — Rozaya has breath scapes rendered as stems
(the breath-slot sources and the session folder). The plugin work is where the
loose threads (the crackle, and the Passage fade-curve ear-test) live.
