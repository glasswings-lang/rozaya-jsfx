# Versioned plugin archive

This folder holds prior versions of plugins that have since been
replaced by a successor in `src/`. They're not currently shipped — the
file in `src/` is the canonical version — but they're preserved here
so the history is recoverable without digging through git.

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

Some plugins maintain v1 and v2 as **parallel currently-shipped versions**
with intentionally different design tradeoffs (e.g. `womb_sound_generator.jsfx`
and `womb_sound_generator_v2.jsfx` both live in `src/` and both are
supported). Those are NOT archived — they're current.

This folder is only for "v1 used to ship, v2 replaced it, here's v1 for
recovery and reference."

## Current contents

- `polyrhythm_phase/v1.jsfx` — Binaural Polyrhythm Oscillator before
  the v2 fold-in that merged Play/Rest gating into the main plugin
  (commit `70f0e2e`, May 2026). Pre-fold the gating lived in a separate
  `polyrhythm_phase_loops.jsfx` file; v2 consolidated.
