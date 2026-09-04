# Versioning: when to fork a plugin, when to archive it

Agreed 2026-08-22 (Rozaya raised it; the suite had drifted into parallel
versions nobody had decided to keep). The point of the rule is that **two live
versions of one plugin is a permanent maintenance cost, and it is almost always
avoidable** — so forking is the last resort, not the reflex.

`CLAUDE.md` carries the short form. This is the full standard, including the
migration mechanics and the hard-won details.

## 1. Default: edit in place

Append sliders at the END, default them to the old behaviour, ship one file.
This covers the overwhelming majority of changes, including large ones — the
Morpher grew fifteen layers, Solo, High cut and an octave ladder this way
without ever forking.

## 2. A new version must ship with a migration, or it does not ship

This is the rule with teeth, and `melody_phase_v2.jsfx` is the proof that it
matters. **It was archived on 2026-09-02** to `archive/versions/melody_phase/`;
what follows is why. It was the *better-looking* design (forty flat per-voice sliders collapsed
behind one selector), it has **zero** projects, and it can never gain any,
because its per-voice data lives in a `@serialize` blob with no path across from
v1. Shipping a version without a migration does not create a successor. It
creates a second thing to maintain, forever.

**Deciding which kind of migration you need is mechanical — ask where the value
lives:**

| Where the value lives | Who migrates it | Cost |
|---|---|---|
| `@serialize` blob | the plugin, on load | a version magic + a transform per hop |
| the slider line (`sliderN` values) | an `.RPP` script in `tools/` | ~150 lines, reusable shape |
| both | both, and they must agree | see below |

A blob migration is close to free and needs nobody to run anything: lead the
stream with a version magic, and on read, walk the blob forward through every
hop it still needs. `spectral_vowel_morpher.jsfx` chains 7700001 → 7700008 this
way. Because it is walked in order, a project several layouts behind migrates
straight through in one load.

A slider-line migration cannot be done from inside the plugin — `@serialize`
cannot reach the slider values — so it needs a script. Worked examples:
`tools/morpher_migrate_layer_order.py` (enum indices) and
`tools/sweepfilter_migrate_hz.py` (recalibrated values). Both were written in an
afternoon; this is not the barrier it looks like.

**Hard-won details, all of them from migrations that nearly went wrong:**

- **Index the slider line by TOKEN position, never by "values with the `-`
  padding stripped".** REAPER writes `-` for slots it has nothing to say about,
  and those can appear BETWEEN real values, not only as trailing padding.
  Filtering them shifts every slider after the gap and rewrites the wrong
  controls, silently.
- **Gate on something that actually distinguishes migrated from un-migrated.**
  The slider COUNT usually does not change, so it cannot tell you. The blob's
  version magic can — read it from the project (first float32 of `<JS_SER>`).
- **Do not require sliders that only exist on newer layouts.** A project from
  before the drift sweep has fewer sliders and is still migratable; only demand
  the ones you actually read.
- **Seed a new slider to whatever reproduces the OLD behaviour**, not to the
  plugin's default. The project should still sound like itself.
- **When the migration preserves a SOUND rather than a number, match the feature
  the ear uses, not the one the textbook names.** Migrating the sweeping filters
  off their old core, I matched the -3 dB corner, which is the textbook
  definition of a cutoff. At high Resonance that filter's audible feature is its
  resonant PEAK, which sat at 0.32x the set frequency -- a different place
  entirely. Every high-resonance project landed half an octave out and 8 dB
  quiet, and it was obvious in one listen. Measure what the old thing actually
  did across the range first; the salient feature may not be the named one.
- **And solve for the target instead of assuming the control is linear.**
  Setting Resonance to `wanted_dB / max_dB` left everything ~3 dB short, because
  what a filter delivers is not what its control asks for. Measure the new
  thing's response, then invert it.
- **Snapshot the whole projects first**, into their own folder, before any
  in-place edit. Per-file `.bak` copies are the second line, not the first.
- **Verify afterwards that only the intended tokens moved.** Diff the backup
  against the result and assert the changed token positions are the ones you
  meant. This caught real bugs twice.

## 3. Archive when the grep is zero — never on the assumption of supersession

```bash
grep -rl <plugin>.jsfx --include=*.RPP /e/reaper
```

Melody Phase v1 was archived because v2 existed, while **five projects were
sitting on it and zero were on v2**; it had to be brought back out. A successor
existing is not evidence that anyone crossed over. Run the grep.

## 4. Public is not the same as local

A file that still has local users but no public future belongs in
`archive/versions/`, frozen and annotated — out of `src/`, out of the release,
out of `docs/plugins/README.md`. Legacy that one person needs to open an old
project should not become a product other people are told about.

## Standing backlog this produces

Re-measure with the grep above before acting; these were the counts on
2026-08-22.

- **Melody Phase — RESOLVED 2026-09-02.** v2 is archived to
  `archive/versions/melody_phase/`. It had zero projects, ever, and could never
  gain one: its per-voice data lived in a `@serialize` blob with no path across
  from v1's slider line. Its one good idea — the note-name **picker** — moved to
  v1; its *implementation* did not and could not, because v2 drew the picker but
  never changed the pitch conversion underneath, so picking "C4" gave you C6.
  Nobody had ever noticed, because nobody had ever run it. **That is the
  strongest argument in this whole section: an unmigratable version is not a
  second option, it is unrun code that looks like one.**
- **Polyrhythm Phase — the one still open.** v1 18 projects, v3 5. Both genuinely live, so this one
  is permanent until someone writes the migration. This is the case rule 2
  exists to prevent. **Direction: v1 migrates UP to v3, then v1 retires.**
  (Confirmed by Rozaya 2026-09-02.) So **v3 is where a new feature gets built
  and judged; v1 gets only what keeps it working** until its projects cross
  over. Defaulting to v1 because it has more instances is backwards — that
  count is the migration backlog, not a vote.
- **Everything else** is single-version and fine.

