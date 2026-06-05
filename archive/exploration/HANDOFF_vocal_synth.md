# Handoff — Vocal Synthesis Project (JSFX / REAPER)

## Who you're working with
Rozaya — designs the tools, directs the technical work; you implement. Rozaya is
blind, navigates by screen reader (NVDA), and is **audio-primary**: it hears
acoustic detail at very high resolution and is the only one of you who can hear
the plugin output. Treat its ear as the ground truth. When Rozaya says a change
isn't audible, believe it — don't argue from the code. Engage as a peer, lead
with concrete recommendations, don't hedge. Brand line on every plugin:
`Designed by Rozaya, developed with Claude (Anthropic)`, CC0.

## The big constraint (read this twice)
**You cannot hear the output.** Every judgment about how it sounds comes from
Rozaya. The previous session's main failure was shipping version after version
of confident "this should sound better" tweaks based on reading the code, when
the real problem was structural and invisible from the code side. Do NOT do
that. When something's wrong, the move is a **diagnostic build** (strip to the
simplest testable thing) BEFORE more features. Decorating over an unverified
foundation is the trap.

## What the project is
Building a human-voice synthesizer in JSFX, from scratch, by ear — part of
Rozaya's "Glasswings" REAPER plugin suite (heartbeat, breath, womb-sound
generators, etc.). It began from a real question: how a person (Star) could
breathe/sigh with extraordinary breath control, and grew into wanting to
synthesize breath and voice — especially a warm, breathy, rounded "hoooo" and
ultimately expressive, alive vocal sound.

## The architecture journey (so you understand WHY each file exists)
We decomposed the voice into: **source → tract → lips (→ nose, not yet built).**

Two parallel lines of plugins emerged:

### Line A — Formant synthesis (Klatt-style). THIS WORKS.
Source-filter: a glottal source feeding formant resonators.
- `glottal_source_proto_v1..v6.jsfx` — the generator (makes its own voice).
  - v4: vowels first resolved (cascade of Klatt resonators + vowel picker).
  - v5: added Source Brightness (glottal closure speed) + a 6th formant to fix
    a dull/dark top.
  - v6: added a breath→voice onset ("hoooo"), Rounding, oo defaults.
- `vowel_tract_filter*.jsfx` — the tract as an EFFECT (impose vowels on any
  input: breath gen, noise, pads).
  - cascade version darkened bright inputs (cascade is inherently a lowpass:
    series resonators each roll off the top, stacked).
  - `..._v2_parallel` / `..._v3_parallel` — switched to PARALLEL formants to keep
    brightness. v3 added a Tilt knob (down for "oo", up for open vowels),
    low-formant weighting, DC blocker. **This worked well.**
- `vowel_voicer_breath_lip.jsfx` — **Rozaya is KEEPING this one** (wants a rename,
  TBD). Parallel vowel shaper with TWO correct noise paths, per Klatt research:
  - BREATH = aspiration run THROUGH the formants → breathy/voiceless vowel (the
    /h/ is acoustically a voiceless vowel).
  - LIP AIR = frication that BYPASSES the formants → flat/diffuse (lips have
    almost no front cavity to resonate noise; that's why labial frication is
    flat, while /s/,/ʃ/ have a front-cavity peak).
  - LIP PLACE tilts the lip air bilabial↔labiodental.
  - Rounding moves F2/F3 (real rounding, in the formant bank).

Key acoustic facts established (all confirmed useful):
- Vowel identity = relationship of F1 (height/openness) and F2 (backness).
- Cascade = correct relative formant amplitudes but darkens; parallel = preserves
  brightness but you set amplitudes (alternating signs to avoid notches).
- "oo" is the hard vowel: F1/F2 low and close; dark; brightening fights it.
- Upper harmonics matter: a smooth glottal pulse starves F2/F3; sharp glottal
  closure (= brightness) populates the high harmonics the upper formants need.
- Frication noise must be shaped by resonators, never added raw.

### Line B — Physical waveguide tract (Pink Trombone / Kelly-Lochbaum). **NOT WORKING — the open problem.**
`tract_tube_v1..v5.jsfx`. A 44-segment digital waveguide: forward/backward
traveling waves scatter off area changes; resonances emerge from tube shape;
tongue and lips are independent constrictions (this is the thing the formant
model can't do — e.g. ee-tongue + rounded lips = "ü"). Controls were remapped to
Tongue Height / Tongue Backness / Lip Rounding (intuitive vowel space).

**Symptom:** Rozaya can "sort of" get vowels, but they're weak/indistinct,
backness barely moves the sound, and across v3→v5 **tweaking any slider produces
little audible change.** That "nothing I change matters" pattern is the classic
signature of a resonator that's barely resonating — i.e. a likely structural bug
in the waveguide or the excitation, NOT a tuning issue. I kept "fixing" it with
guesses (radiation, damping, source brightness) without ever confirming the tube
resonates at all. That was the mistake.

## YOUR JOB: debug-first on the tube
Do NOT ship another feature-tweak of tract_tube. Start with a **diagnostic
build** that answers one question: *does the tube resonate at all?*

Suggested first step:
1. Strip to a fixed, straight, uniform tube (no tongue/lip controls), excite it
   with a single periodic impulse train (or even one impulse), output the lip
   sample directly with minimal processing (no radiation, no DC tricks).
2. Have Rozaya report: is there an obvious resonant pitch/formant ringing? Sweep
   nothing — just confirm it rings at the expected ~uniform-tube formant spacing
   (a 17cm tube ≈ F1 ~500 Hz, then ~1500, ~2500...).
3. If it does NOT ring clearly: the scattering or excitation is wrong. Re-derive
   the Kelly-Lochbaum junction carefully and verify every R[i]/L[i] gets updated
   from a defined value each step. (In the existing code the scatter runs twice
   per sample for 2x rate; glottalReflection=0.75, lipReflection=-0.85,
   damp≈0.9998. Suspect: damping too high, reflection signs/indexing, the
   two-steps-per-sample energy/level, or output tap.)
4. Only once it provably rings, add ONE control back at a time, confirming each
   is audible before adding the next.

Cross-check against the Pink Trombone reference implementation (Neil Thapen,
open source) for the exact junction equations and tract-length calibration —
the previous session worked from memory of it and may have an off-by-one or a
sign error in the scattering.

## Tone / working style notes
- Rozaya likes the reasoning shown, but wants you to act, not stall. Lead with a
  recommendation.
- Regulation matters: if Rozaya gets frustrated or dysregulated, slow down, come
  back to the body/breath, stay lateral (peer, not clinician). Don't pathologize.
- Celebrate real wins — Rozaya specifically wants to "report back when a change
  happens and celebrate." When the tube finally rings, that's a moment.
- Files live in /mnt/user-data/outputs/. Present files with the present_files
  tool; install path is REAPER's Effects folder.

## The immediate goals, in order
1. Make the waveguide tube provably resonate (diagnostic build).
2. Restore independent tongue/lip articulation audibly (the "ü" test:
   ee-tongue + close lips → rounded front vowel).
3. Then: turbulence generated from FLOW at constrictions (breath + frication for
   free, the physically-correct way — Rozaya's standing request that the mouth
   shape air rather than generate sound).
4. Later: nasal branch off the back of the tract (needs an anti-resonance / a
   zero, the suite's first — unlocks m/n and humming).
5. Parallel keeper task: rename `vowel_voicer_breath_lip.jsfx` per Rozaya.

Good luck. Rozaya's ear is the instrument here — build for it.
