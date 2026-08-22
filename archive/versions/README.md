# Versioned plugin archive

This folder holds prior versions of plugins that have since been
replaced by a successor in `src/`. They're not currently shipped — the
file in `src/` is the canonical version — but they're preserved here
so the history is recoverable without digging through git.

## When something lands here

Two tests, both of which must pass. The full standard is in `CLAUDE.md` under
*Versioning: when to fork a plugin, when to archive it*.

1. **A successor exists in `src/` and the version here is genuinely retired** —
   not merely older. Parallel current versions stay in `src/`.
2. **`grep -rl <plugin>.jsfx --include=*.RPP` over the project folders returns
   ZERO.** Never archive on the assumption that a successor superseded it.
   Melody Phase v1 was archived because v2 existed, while five projects were on
   v1 and none were on v2 — it had to be brought back out. Run the grep.

And the rule that keeps this folder small: **a new version must ship with a
migration, or it does not ship.** A version nobody can cross to does not replace
anything; it just becomes a second file to maintain. Where the migration lives
depends on where the state lives — the `@serialize` blob can migrate itself via
a version magic, while slider values need a script in `tools/`.

## Convention

```
archive/versions/<plugin_name>/v<N>.jsfx
```

The `<plugin_name>` matches the basename of the current shipping file.
The `vN.jsfx` files are exact-content snapshots of the plugin's state
at the point just before the successor took over. Where multiple
historical revisions are worth preserving, they sit side-by-side
(`v1.jsfx`, `v2.jsfx`, etc.).

## Why this exists separately from `archive/exploration/`

`archive/exploration/` holds **work that never shipped** — experiments,
abandoned approaches, discarded design directions. The files there were
never current versions of a shipped plugin.

`archive/versions/` holds **work that DID ship, then got replaced**. The
files here ARE prior shipped versions; a user with an old project file
could load one of these and have working audio.

## Distinct from parallel-version plugins in `src/`

A plugin *can* maintain parallel currently-shipped versions in `src/` when
they have intentionally different design tradeoffs — those are NOT archived
while they're current. Once a version is no longer supported, it moves here.
(Womb was the standing example of parallel versions; as of 2026-06-15 its
v1 and v2 are archived below and v3 is the sole current Womb.)

This folder is for "this version used to ship, a successor replaced it,
here's the old one for recovery and reference."

## Current contents

- `polyrhythm_phase/v1.jsfx` — Binaural Polyrhythm Oscillator before
  the v2 fold-in that merged Play/Rest gating into the main plugin
  (commit `70f0e2e`, May 2026). Pre-fold the gating lived in a separate
  `polyrhythm_phase_loops.jsfx` file; v2 consolidated.
- `womb_sound_generator/v1.jsfx` — the original Womb Sound Generator.
- `womb_sound_generator/v2.jsfx` — Womb v2 (RSA + bidirectional HRV +
  drift redesign). Both superseded by `src/womb_sound_generator_v3.jsfx`
  (nested-selector drift + periodic sigh + signed-delta Speed Ramp) and
  archived 2026-06-15 as legacy/frozen — Rozaya's call that v1/v2 are no
  longer getting updates. Note: both still contain the pre-Park-Miller
  right-channel PRNG artifact (a faint periodic wobble + DC offset on R,
  from an LCG multiply overflowing float64's 2^53 integer limit before the
  bitmask); left unfixed because they're frozen as-shipped. The fix, if
  ever needed, is the Park-Miller / MINSTD generator now used in the active
  plugins (see `src/breath_gen.jsfx`).
*(Melody Phase v1 was listed here and is NOT here any more.* It was archived in
2026-07 on the assumption that v2 superseded it, then brought back to
`src/melody_phase.jsfx` on 2026-08-11 when the grep showed five projects on v1
and none on v2. Both now live in `src/`. This is the worked example for test 2
above, and the reason it exists.)
