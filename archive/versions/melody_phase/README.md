# Melody Phase v2 — archived 2026-09-02

Frozen. Not maintained, not in the release, not in `docs/plugins/README.md`.

## Why it is here

Zero projects, ever. It is the *better-looking* design — forty flat per-voice
sliders collapsed behind one Voice selector — and it could never gain a user,
because its per-voice data lives in a `@serialize` blob with no path across from
v1's slider line. It is the case CLAUDE.md's versioning rule exists to prevent:
shipping a version without a migration does not create a successor, it creates a
second thing to maintain.

Rozaya, 2026-08-31, on the nested selector: *"that was my fault because I got
overeager one day."*

## What was rescued from it, and what was wrong with it

Its one good idea was the **note-name picker** — C2..C6 instead of a count of
semitones above a root. That idea moved to v1 on 2026-09-02.

The IMPLEMENTATION did not, and could not, because it is broken here. v2 draws
the picker but never changed the pitch conversion underneath: `slider23` still
reaches `semitones_to_hz(base_note, center_octave, v_semitones[i])`, which reads
the index as semitones-above-root. Pick "C4" on a default setup and you get
**C6** — two octaves out. Nobody noticed because nobody ever ran it.

v1 does it properly: the index converts to semitones about C4 (`index - 24`),
and `Root note` / `Center octave` were replaced by `Transpose (half steps)` and
`Octave shift`, which is the pair Polyrhythm v3 uses. A picker that names a note
while another control silently moves it is a label that lies, which is exactly
what this file shipped.

## Opening an old project that used it

Nothing does. If one ever turns up, copy this file back into `src/` temporarily;
it is unchanged from the day it was archived.
