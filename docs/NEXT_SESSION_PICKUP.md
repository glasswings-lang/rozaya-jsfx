# Next session pickup notes — 2026-07-22

Rozaya's ~9am wind-down after a long overnight. Two threads left open for
whoever picks this up (probably Rozaya, probably me/Claude, next session).

## Thread 1: Rename morpher v2 to "Spectral Vowel Loom"

**Decision made:** morpher v1 and morpher v2 are sibling tools, not
version-and-successor. v1 is the continuous-morph tool ("morph in motion,
never really settles"). v2 is the paced-arrangement tool ("each captured
moment configured deliberately, holds and crossfades set per slot"). Same
engine underneath, completely different UX and mental model. Both are
worth keeping installed.

**Chosen name:** Spectral Vowel Loom (weaving captures together, threads
into a pattern). "Morpher" is the wrong word for what v2 actually does —
it does not morph continuously, it arranges. Loom fits.

**What the rename touches:**
- `src/spectral_vowel_morpher_v2.jsfx` → `src/spectral_vowel_loom.jsfx`
- The `desc:` line inside the file (`Spectral Vowel Morpher v2` →
  `Spectral Vowel Loom`)
- `docs/plugins/spectral-vowel-morpher-v2.md` → `docs/plugins/spectral-vowel-loom.md`
- All cross-references in other manual pages
- The plugins index (`docs/plugins/README.md`)
- The top-level README
- The migration tool `tools/morpher_v1_to_v2.py`. Two paths:
  - Keep the tool as-is (v1 → old-v2-name), rename its output later
  - Rename the tool to `morpher_to_loom.py` (or similar) and update to
    output the Loom filename
  - Add a second tool `morpher_v2_to_loom.py` for anyone with existing
    v2 projects (only Rozaya, probably)
- Rozaya's existing v2 project `E:/reaper/breathing_v2.rpp` still points
  at `spectral_vowel_morpher_v2.jsfx`. Either regenerate to point at
  Loom, or leave the old-named plugin installed as a shim so old
  projects don't break. Cleanest: migration tool that rewrites the .rpp
  to point at Loom's filename and preserves the blob (blob format is
  Loom-compatible since Loom IS v2).
- A note in v1 morpher's docs pointing to Loom as the sibling ("if you
  want per-slot hold + crossfade paced arrangement, use Loom").

**Blob compatibility:** Loom reads the same magic values v2 does
(7700001 v1, 7700002 old v2, 7700003 current). So a Loom instance opening
a v2-saved project reads it correctly. Only the plugin filename changes.

## Thread 2: The short-grain crackle wasn't fixed

**What I claimed:** the FFT-sizing change (GFFT sized to grain instead of
fixed at max) would eliminate the evenly-spaced crackling that appears at
short Wash grain settings. My theory: cost-per-grain was constant while
grain-rate scales inversely with length, so shortening the grain
multiplied CPU. Fix: shrink the FFT per grain.

**What actually happened:** Rozaya tested by ear. The crackle is still
there, evenly spaced, at short grain. So my theory was wrong, or at least
incomplete.

**Docs status:** the "short grain works now" claim in the manual page is
retracted, with an honest "known limitation" note in its place. The
FFT-sizing change is kept because it does reduce CPU on wash-heavy
projects; it just wasn't what solved the crackle.

**Next-session diagnostic questions to actually ask:**

1. Is the crackle-per-second rate related to grain-rate (grains per
   second)? If yes, still a per-grain issue but not CPU. Maybe
   accumulator-wrap alignment, or gen_grain state discontinuity between
   consecutive grains.
2. Is the crackle-per-second rate related to hop rate (hopcount reaching
   HOP)? Same rate as grain rate since HOP = W/4, so hard to distinguish.
3. Is the crackle a phase discontinuity at grain boundaries? The
   sqrt-Hann window should cross-fade cleanly, but if two consecutive
   grains have very different random phase[] arrays AND overlap in the
   accumulator, brief discontinuity at the seam could click.
4. Is it the auto-gain smoother reacting per-grain? `rms_smooth` updates
   per grain — if the update produces a discontinuous jump in gnorm,
   next grain arrives at a different level than the previous grain's
   tail, click.
5. Is GFFT actually the right size for the grain, or is there a
   power-of-two mismatch that leaves the last few samples unwritten and
   causes a discontinuity?

**Cheap way to isolate:** capture pure sine at slot 0, silence at slot 1,
set to focused audio slot 0, sweep Wash grain from 680 down to 5, listen
for where crackle starts, note the grain length. That gives the
threshold. Then look at what changes structurally near that threshold
(FFT size doubling? Hop crossing 1 sample? Something else?).

**Don't repeat my mistake:** don't confidently theorise from the code
alone. Test each hypothesis by ear with a controlled signal.

---

Rozaya is at ~77% context and probably signing off shortly. She has
existing breath scapes rendered as stems (in `E:/reaper/breath_slots/`
and probably her session folder), so audio work is safe from any of
this. The plugin work is where the loose threads are.
