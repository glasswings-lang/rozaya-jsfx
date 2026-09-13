# tools

Small utility scripts that support the suite but aren't JSFX plugins.

Every one runs from a terminal and prints its full flag list with `--help`.

**New to this?** [docs/getting-your-captures-out.md](../docs/getting-your-captures-out.md) walks through the two capture tools from scratch — installing Python, opening a
terminal, and reading the output — assuming no prior experience. This page is the
reference; that one is the tutorial.
`rate_calc.py`, `morpher_to_passage.py` and `passage_migrate_sliders.py` need
nothing installed; `loop_finder.py` needs two packages (noted below).

| Tool | For |
|---|---|
| [`rate_calc.py`](#rate_calcpy) | base rate for a second instance, so a chosen voice lands where you want it |
| [`loop_finder.py`](#loop_finderpy) | pulling clean looping samples out of a recording |
| [`morpher_to_passage.py`](#morpher_to_passagepy) | moving a Spectral Vowel Morpher project onto its sibling Passage, captures and all |
| [`passage_migrate_sliders.py`](#passage_migrate_sliderspy) | repairing older projects after Passage gained a control mid-list |
| [`passage_captures.py`](#passage_capturespy) | reading and extracting the captures stored inside a project |
| [`passage_inject.py`](#passage_injectpy) | putting a WAV back *into* a capture slot |
| [`passage_set_capture_average.py`](#passage_set_capture_averagepy) | turning Capture average up across a whole folder of projects |

## rate_calc.py

Works out what base rate to dial into a **second instance** of a plugin so that
one of its voices lands exactly where you want it, relative to a voice in the
first instance.

```
python tools/rate_calc.py --base 30 --aim 8 --offset -0.05
```

**Why it exists.** Voices inside an instance stack *upward* from the base rate.
So putting a high-numbered voice *below* something means cancelling that stack
**and** applying the shift — two subtractions pulling opposite ways, held at
once. That's bookkeeping, not music, and it's the exact profile in
[docs/dyscalculia-accessibility-sweep.md](../docs/dyscalculia-accessibility-sweep.md).

This can't be a plugin control: **instance 2 has no idea instance 1 exists.**
Nothing you add to a JSFX can see another copy of itself, so cross-instance
relationships have to be solved out here.

It prints the answer **and the working** — target, the stack it subtracted, the
resulting base — then the full voice table and a verification line. The chain is
there so you can *check* the result by reading rather than trust it.

| Flag | Default | What it does |
|---|---|---|
| `--base BPM` | `30` | base rate of the **first** instance |
| `--step BPM` | `0.05` | how much faster each voice runs than the one before |
| `--voices N` | `8` | voices per instance |
| `--aim N` | `8` | which voice of the **second** instance you're placing |
| `--against N` | `1` | which voice of the **first** instance to place it against |
| `--offset BPM` | `-0.05` | how far off that voice you want it (negative = slower) |
| `--inspect BPM` | off | **reverse mode** — you already set instance 2 to this; report what offset that actually gave you |
| `--show` | off | just list one instance's voices and stop |
| `--merged` | off | also list every voice from both instances together, slowest first, with the gap between each |
| `--decimals N` | `3` | decimal places to show |

### Examples

```
# 8th voice of instance 2, one step below instance 1's first voice
python tools/rate_calc.py --base 30 --aim 8 --offset -0.05

# land it against instance 1's voice 4 instead
python tools/rate_calc.py --base 30 --aim 8 --against 4 --offset -0.05

# what is one instance actually doing?
python tools/rate_calc.py --base 30 --show

# I already set instance 2 to 29.6 -- what did that give me?
python tools/rate_calc.py --base 30 --inspect 29.6 --aim 8

# hear how the whole thing spaces out once both are running
python tools/rate_calc.py --base 30 --aim 8 --offset -0.05 --merged
```

## loop_finder.py

Finds loop-ready material in any recording so you don't have to hunt for loop
points by eye. It scans for distinct sound events (skipping junk transients
like mic-bangs), trims each to its loud core, **flattens the level** so it
loops without pumping, and writes one loop-ready WAV per event — labeled by
shape (`steady` held texture / `shaped` gesture that swelled & faded) and
brightness (`dark` / `mid` / `airy`). Drop the output straight into the
**Sustain Looper**'s crossfade loop.

Requires `numpy` and `soundfile` (`pip install numpy soundfile`).

```
python tools/loop_finder.py <input.wav> [flags]
```

By default clips land in the input file's own folder — so if the source is in
`<REAPER resource>/Data/glasswings_samples/`, they appear in the Sustain Looper
dropdown automatically.

### Everything is a flag (no code editing)

All behaviour is controlled by the flags below; `python tools/loop_finder.py --help`
prints the same list. **Recommended workflow:** run with `--list` first to
*preview* what it would grab, adjust flags, then run for real.

| Flag | Default | What it does |
|---|---|---|
| `--list` | off | **Preview only** — print what would be extracted, write no files. Use this to tune the flags before committing. |
| `--sensitivity DB` | `4` | How far below the typical level still counts as sound. **Raise** to catch quieter breaths/sounds, **lower** to ignore them. |
| `--gap SEC` | `0.08` | Bridge silences shorter than this within one event. **Raise** to keep a swelly breath whole; **lower** to split into more, shorter clips. |
| `--min-dur SEC` | `0.5` | Shortest clip to keep. |
| `--core-db DB` | `10` | Trim each event to within this many dB of its own peak. **Lower** = tighter, steadier core (drops the quiet onset/tail). |
| `--bang-jump DB` | `15` | A sudden level jump this big flags a junk transient (mic bang) to skip. **Raise** to be less aggressive about skipping. |
| `--keep-junk` | off | Don't skip loud transients at all (keep everything). |
| `--max-clips N` | `12` | Keep at most this many, longest first. |
| `--peak-db DB` | `-3` | Normalize each clip to this peak level (dBFS). |
| `--fade-ms MS` | `6` | Edge fade length, to avoid clicks at the clip boundaries. |
| `--no-flatten` | off | Keep the natural level shape — do **not** flatten the swell (use when you want the gesture intact, not loop-flat). |
| `--as-float` | off | Write 32-bit float WAV instead of 16-bit PCM. |
| `--flat-db DB` | `2` | Internal wobble under this dB is labeled `steady`, else `shaped` (labeling only). |
| `--outdir DIR` | input's folder | Where to write clips. |
| `--prefix NAME` | from filename | Filename prefix for the clips. |

### Examples

```
# preview what's in a breath recording, tune before writing
python tools/loop_finder.py breath.wav --list

# catch quieter material and split breaths finer
python tools/loop_finder.py breath.wav --sensitivity 8 --gap 0.04

# keep the gestures un-flattened (natural swell), fewer/longer clips
python tools/loop_finder.py phrase.wav --no-flatten --min-dur 1.0 --max-clips 6
```

**Why it exists:** finding loop points is a visual task. This does it by
ear-proxy — the same "find a flat bit and grab it" pass done by hand to turn a
real breath recording into a clean looping sample. Steady textures loop as-is;
gestures are flattened so they loop too.

## morpher_to_passage.py

Copies a REAPER project that uses **Spectral Vowel Morpher** so the copy uses its
sibling **Spectral Vowel Passage**, keeping the captures and every setting.

```
python tools/morpher_to_passage.py "path/to/project.rpp"
```

Writes `project_passage.rpp` beside the original. **Your project is never
modified**, so you can open one, then the other, and compare.

**Why it exists.** Passage groups its controls by what they belong to, which
renumbered the sliders, and it replaced Morpher's single global Auto-morph time
with a per-slot timing cluster (fade in / hold / fade out / gap / crossfade
toggle). Repointing a project at Passage by hand shifts every value out of place,
so Texture lands on the wrong control, Pitch on another, and so on — it *loads*,
it just sounds nothing like it did.

This maps controls **by name**, read live from both `.jsfx` files, so it stays
right even if either layout is renumbered again. It reads each instance's slot
count out of its own capture data, so the per-slot fade-out it works out
reproduces the morph timing the project already had (Morpher's whole-pass time
spread across the slots, still a continuous crossfade). Then it reads both files
back and compares them label for label, and **refuses to report success** if
anything failed to line up.

**Convert from a saved project.** It reads what is on disk, so if the project is
open in REAPER with unsaved changes, the copy is built from the older state —
which is exactly the mistake that prompted this to be written down as a tool
rather than done by hand.

## passage_migrate_sliders.py

Fixes projects that were saved before **Spectral Vowel Passage** gained a control
in the middle of its list.

```
python tools/passage_migrate_sliders.py "path/to/project.rpp"
```

**The symptom.** You open an older project and everything above a certain point
is wrong — Wash grain's 150 showing up as Voice level, Auto-morph sitting on
Audition, Texture on something else again. It isn't corruption. REAPER stores
plugin settings by slider *position*, so inserting a control at slider 4 pushes
everything above it along by one, and each value lands on its neighbour.

**Your captures are never at risk.** They're stored separately from the settings,
in a form that has no idea slider numbers exist, so they come through any
renumber untouched. Only the control values move — which is why this is
repairable at all, and repairable as a text edit rather than a re-capture.

**What it does.** Rewrites each instance's settings into their new positions and
fills in the new controls with whatever reproduces how that project *already*
sounded — Linear fades, and a Capture average of 1 — rather than the plugin's
current defaults. A project should still sound like itself after a repair;
adopting the new defaults is a choice you make afterwards, not something a
migration should decide for you.

It handles as many layout changes as a project is behind, in one run, so it
doesn't matter how old the project is.

**It also repoints projects that use the old plugin filename.** Passage was
called `spectral_vowel_morpher_v2.jsfx` before it was named. Those projects
still open — that file may still be sitting in your Effects folder — but they're
silently running code from before the rename, missing every fix since. Their
slider layout is identical to Passage's own 32-slider layout, so the tool
switches them over and then migrates them the rest of the way in the same pass.

**Controls added at the END never need migrating.** REAPER just gives the
missing trailing ones their defaults, so a project saved before Overtone existed
is already fine. Only controls inserted mid-list move anything, and those are
the only ones this tool touches.

| Flag | What it does |
|---|---|
| `--dry-run` | **Preview only** — report what would change, write nothing |
| `--out FILE` | write the result to a new file and leave the original alone (one project at a time) |

Several projects at once is fine — just list them.

### Before you run it

**Close the project in REAPER first.** REAPER keeps its own copy in memory and
writes it back over yours on the next save, so a migration applied underneath an
open project is silently undone.

In-place runs leave a `.pre-slider-migrate-bak` copy beside each project, and
refuse to start if one is already there rather than overwriting your safety net.
Running it twice is harmless — anything already current is left alone.

### Examples

```
# look before you leap
python tools/passage_migrate_sliders.py "E:/reaper/nightfall.RPP" --dry-run

# repair several projects, backups kept automatically
python tools/passage_migrate_sliders.py project-a.RPP project-b.RPP project-c.RPP

# keep the original untouched and write a repaired copy instead
python tools/passage_migrate_sliders.py old.RPP --out repaired.RPP
```

**Why it exists.** Passage's controls are grouped by what they belong to, and
twice now a new control has belonged in the middle rather than at the end — Fade
in/out shape with the timing cluster, Capture average with the other
capture-analysis controls. Appending them instead would have kept every project
working, but at the cost of a control list that reads in the order things were
built rather than the order you use them. This exists so that trade can go the
other way.

## passage_captures.py

Lists what's in every **Spectral Vowel Passage** / **Morpher** slot in a project,
and can write each one out as a WAV. **It only ever reads** — your project is
never modified.

```
python tools/passage_captures.py "path/to/project.rpp"
python tools/passage_captures.py "path/to/project.rpp" --settings
python tools/passage_captures.py "path/to/project.rpp" --extract captures/
```

### ⚠ The WAVs are the raw grab, not the sound you shaped

This has caught someone out, so it's worth saying before anything else.

`--extract` writes the audio **as captured** — before the fade times, the
texture, the pitch, the spread, the denoise. Those aren't stored anywhere as
audio, because they aren't audio: they're a transformation applied while sound
passes through the plugin. **The only place the shaped version exists is a
render.** If what you want is the sound you made, render it from REAPER; no
tool can lift it out of the project, because it isn't in there.

That is *not* your settings being lost. They're all still in the project, and
`--settings` reads them straight back out.

**Why it exists.** A capture only exists inside the project that made it. You
can't reuse a good vowel in another piece, back one up on its own, feed one to
Sustain Looper, or hand one to anybody else. And you can't tell your eight slots
apart without playing all eight — which, with no waveform to look at, means
auditioning every one of them every time.

But the audio is right there. Both plugins store the **raw captured audio** in
their saved state (which is why scrubbing Capture point re-tunes a slot without
re-recording it), and that's plain enough to read straight out of the project
file.

### The listing

One line per slot: how loud it is, how long the real signal lasts, and its pitch
**as a note name**. Enough to tell slots apart, find the one you want, and spot
the empty ones — by reading rather than by ear.

```
08  (spectral_vowel_passage, line 136) -- 8 slot(s), 48000 Hz
   slot 1   0.68 s  peak   -6.8 dB  rms  -15.9 dB  F#2   -43 cents    90.2 Hz
   slot 3   0.68 s  peak   -6.2 dB  rms  -16.3 dB  unpitched
```

**"unpitched"** means the pitch detector wasn't confident — usually a breath, a
consonant, or a moment too noisy to have one clear note. It's honest rather than
guessing, and it's a useful signal in itself: those are the slots the *voice*
engine will struggle with and the *wash* will like.

### `--settings` — what you dialled in

Reads your settings back out of the project, in words, **showing only what you
changed** from the starting values:

```
slot 1
   Fade in: 3.5 seconds
   Hold: 3.5 seconds
   Fade out: 3.5 seconds
   Texture: 0  (0 is voice, 100 is wash)
   Pitch: +0.5 semitones
   Stereo width: 100
```

Seventeen settings across eight slots is a hundred and thirty-six numbers, and
handed over all at once that's a wall — which is what the plugin's own UI
already does to you. Only what you touched is worth reading. Add
`--all-settings` if you do want every one.

With `--extract`, the same thing is written beside the WAVs as
**`settings.txt`**, so your setup survives the project too and can be read
without opening a DAW. Identical duplicated tracks are written once, not
twenty times.

**Morpher** keeps most of these as global sliders rather than per slot, so only
Capture point appears for it. Missing isn't the same as unchanged, so anything
the plugin doesn't store is left out rather than reported as a default.

**"empty — captured silence"** is the classic mistake of firing Capture with
nothing playing. Now you can see it in a list instead of discovering it when the
morph fades out.

### Extracting

`--extract DIR` writes one WAV per non-empty slot at the project's own sample
rate (add `--unique` if the project has duplicated tracks — they share
their captures, so twenty copies of one instance means twenty copies of the same
eight sounds, and the default says so when it spots them), named by project, track and slot. Put them in
`<REAPER resource>/Data/glasswings_samples/` and they show up in Sustain Looper's
dropdown; or run them through [`loop_finder.py`](#loop_finderpy); or just keep
them — a capture that exists only inside one `.RPP` is one bad save from gone.

| Flag | What it does |
|---|---|
| `--extract DIR` | write one WAV per non-empty slot into DIR |
| `--float` | 32-bit float WAVs instead of 16-bit (exact, but 16-bit loads everywhere — including JSFX, which does not guarantee float) |
| `--no-pitch` | skip pitch detection (faster on projects with many instances) |
| `--unique` | write each distinct capture once, skipping identical copies |

Several projects at once is fine — just list them.

### A note on safety

The saved state leads with a number identifying its layout, and this tool
**refuses to read anything it doesn't recognise** rather than guessing. A
mis-parsed blob wouldn't error, it would produce plausible-sounding garbage, so
the check matters more than it looks. Extraction itself works on every version
ever shipped, because the raw audio has never moved from the front.

## passage_inject.py

The other direction from [`passage_captures.py`](#passage_capturespy): writes a
WAV **into** a Passage / Morpher capture slot.

```
python tools/passage_inject.py "project.rpp" --set 3=vowel.wav
python tools/passage_inject.py "project.rpp" --set 3=a.wav --set 5=b.wav
```

By default it writes a **new project beside the original** and leaves yours
alone.

**Why it works.** The saved state holds only the raw audio — the wash spectrum
and the harmonic analysis aren't in there, they're worked out fresh from that
audio every time the project loads. So this doesn't have to compute anything:
put audio in and the plugin analyses it itself, exactly as if you'd captured it.

**What that means in practice: a capture no longer has to come from a
performance.** Anything you can put in a WAV can become a slot — one lifted out
of another project, a clip from [`loop_finder.py`](#loop_finderpy), or a
generated source. You can assemble a bank of eight deliberately instead of
catching eight moments live.

### What it does to your audio

A slot is exactly 32768 samples — about 0.68 s at 48 kHz — mono, at the
project's own sample rate.

**Sample rate has to match, and this is the one that would bite you silently.**
Nothing inside the project records what rate a capture was made at; it just plays
at whatever the project runs at. So a 44.1k file dropped into a 48k project comes
out sharp and short, with no error anywhere and a result that sounds *plausible*.
A mismatch is refused outright unless you pass `--resample`.

**Stereo is summed to mono**, because the capture buffer is mono — your stereo
placement arrives centred.

**Long files are trimmed** to their loudest 0.68 s, which on a held note lands on
the sustained middle rather than the attack. `--from SECONDS` picks the spot
yourself.

**Short files are centred and padded**, and the slot's **Capture point is set for
you** so the analysis lands on the audio instead of on the padding. Without that,
a short file analyses as silence and the slot plays nothing — which would look
like the injection had failed.

| Flag | What it does |
|---|---|
| `--set SLOT=FILE` | put FILE into slot SLOT (1–8). Repeatable. |
| `--instance N` | which plugin instance, when the project has more than one (it lists them if you don't say) |
| `--from SECONDS` | where in a long file to take the slot from |
| `--resample` | allow a rate mismatch, converting to the project's rate |
| `--in-place` | edit the project itself, keeping a `.pre-inject-bak` |
| `--out FILE` | write somewhere specific |

### Safety

Every run **re-reads and re-decodes what it wrote** before letting it stand, and
checks two things: that the slots you asked for actually landed, and that every
other slot is byte-identical to what it was. If either fails it says so and
doesn't pretend the run succeeded.

Writing into a slot the project has never used also fills in any slots skipped
over, with silence — so asking for slot 6 in a project that only used two won't
leave a hole.

**Close the project in REAPER first.** REAPER keeps its own copy in memory and
writes it back over yours on the next save.

## passage_set_capture_average.py

Sets **Capture average** on every Passage / Morpher instance in a project, so a
backlog of finished pieces can be re-rendered with the multi-frame analysis
without opening each one and hunting for the control.

```
python tools/passage_set_capture_average.py "E:
eaper	o-be-re-rendered\*.RPP" --value 6 --in-place
```

**What it touches.** One line of plain text per instance — the slider line. It
does not go near your captures.

That's enough because of how each plugin restores the setting — and the two now
differ, so it's worth knowing which you're editing.

**Morpher** — Capture average is one **global** control. The slider is the whole
truth: on load the plugin stamps it onto all eight slots every time, whatever the
saved project holds. Writing the slider here always takes, so this tool is just
the way to do it across a folder without opening each project in REAPER.

**Passage** — Capture average is still **per slot**, on purpose: each stop on the
route has its own character. Writing the slider reaches a project that *predates*
the control — it has no such field, so on load the plugin seeds every slot from
the visible slider, the same migration the per-slot Capture point already uses. A
Passage project saved *since* the control existed carries its own per-slot values,
and those win, because somebody chose them. Change those in the plugin.

Older projects may not have the slider at all — Morpher's Capture average is
slider 28, and a project from its 16-slider days stops well short. The missing
positions are filled with each slider's real default, read live out of the `.jsfx`
rather than guessed, so nothing else moves.

| Flag | What it does |
|---|---|
| `--value N` | 1–6 (default 6) |
| `--in-place` | edit the projects themselves, keeping a `.pre-capavg-bak` each |
| `--dry-run` | report what would change, write nothing |

Close the projects in REAPER first. Wildcards are fine — quote them so the script
expands them rather than the shell.

## Slider-layout repair (2026-09-02)

A mid-list slider insert shifts every saved value one place, silently, because
REAPER restores by POSITION. Four tools came out of the 2026-09-02 diagnosis:

- **`scan_slider_ranges.py`** — range-checks every stored value in every project
  against the INSTALLED plugin. The cheapest detector for a shifted map, and the
  one that actually found the bug after a day of reasoning had not. Start here.
  `python tools/scan_slider_ranges.py E:/reaper/finished`

  **It walks subfolders, and `E:/reaper/finished` contains `backups/` and
  `backups/snapshots/`.** Those hold PRE-migration copies by design, so checking
  them against a post-migration build reports every shifted value as out of
  range — 283 files' worth on 2026-09-06, which reads as a catastrophe and is
  the tool working correctly. **Point it at the live project files** when you
  want to know whether a migration was clean, and read the paths on any hit
  before believing it.
- **`migrate_speedramp_insert.py`** — repairs the 2026-07-02 `Speed ramp target`
  insert across the six plugins it hit. Table-driven, gated on the `@serialize`
  magic, idempotent, dry-run by default.
- **`melody_migrate_drift_shift.py`** — the Melody-specific form of the same
  repair, kept because it is the one that was verified line by line.
- **`melody_verify_drift_shift.py`** — verifies the OUTPUT against a snapshot AND
  against each instance's untouched `@serialize` blob. Verify the result, never
  the exit code: the first run of the migration exited cleanly while silently
  eating one line per instance.
- **`breathgen_promote_20260909.py`** — the 32→40-slider Breath Generator move,
  four instances across three projects. Every instance's forty values are written
  out in full rather than mapped by rule, because the pitch could not survive a
  rule: it left the slider line for per-target banks inside the `@serialize`
  blob, so each instance also gets a freshly written 96-float blob (two of the
  four had no `<JS_SER>` at all). Verified by loading each migrated project back
  into the real plugin with `jsfx_run --list --rpp`, and by an old-on-old against
  new-on-migrated render that is bit-identical over 40 seconds.
- **`melody_migrate_r20.py`** — the 2026-09-06 R20/R21 conversion: retires
  Melody's `Sync to host` / `Host sync target` / `Every N beats` trio, folds a
  synced instance's beat count into `Rate value` with `Rate mode` = *Every N
  beats*, brings `Pan glide` and `Cycle steps` back into the pan block, and opens
  the gaps for the seven new controls. Reads the snapshot and writes the live
  project, so it is idempotent; dry-run by default. **Refuses rather than
  guessing** on a pan-synced instance, a quoted token, or a value above the old
  slider count.
- **`melody_verify_r20.py`** — the check for it, and it deliberately does NOT
  import the migration's table. It reads the OLD slider names out of `git show`
  and the NEW ones out of the working tree, decodes both sides by CONTROL NAME,
  and compares. Renames are declared explicitly so a rename can never read as a
  deletion plus an addition — which is the fingerprint of a mid-list insert. It
  also recomputes each synced instance's cycle length from first principles to
  prove the fold changed no speed, and range-checks every value against its
  slider's declared min/max. **Run it before committing the source**, since it
  reads the pre-migration layout from `HEAD`.

## Polyrhythm Phase v3 — the 2026-09-07 voices-behind-a-selector rebuild

- **`polyv3_migrate_layout_20260907.py`** — 90 sliders to 56, applying the
  layout authored in `docs/layouts/polyrhythm-phase-v3.md`. Most of it is a
  reorder, but **this is the first migration in the repo that REWRITES THE
  BLOB**: V2–V8's forty-two per-voice values leave the slider line entirely and
  become twelve `@serialize` banks, alongside four new drift/ramp play-rest
  banks and a magic bump 2100024 → 2200024. It also writes two values that
  cannot be left to a declared default — `Pan rate mode` takes the instance's
  own tremolo Rate Mode (the pan used to borrow it), and `Voice` is seeded to 1
  rather than `All`, so one stray nudge on a migrated instance cannot write
  across all eight configured voices. Reads the snapshot and writes the live
  project, so it is idempotent; dry-run by default. **Refuses rather than
  guessing** on a quoted token, a missing `<JS_SER>`, a value above the old
  slider count, an unmapped slider, or an instance count other than 8.
- **`polyv3_verify_layout_20260907.py`** — the check for it, and it deliberately
  does NOT import the migration's table. It reads the OLD slider names out of
  `git show` at a **pinned commit hash** (never `HEAD~n`, which goes stale the
  moment anything else is committed) and the NEW ones out of the working tree,
  matches controls BY NAME, and checks four things: every shared control holds
  the same value; every per-voice value reappears in the blob under its old
  name; every migrated value fits its new slider's declared min/max; and the
  line endings and instance counts survived. A value that was ALREADY out of
  range before is reported separately from one this migration caused — mixing
  the two buries the real signal. 1176 checks, 0 failures.
- **`polyv3_migrate_r22r24_20260910.py`** — 56 sliders to 59, applying
  `docs/layouts/polyrhythm-phase-v3-r22-r24.md`: the visible voice's note index
  gains 36 into Note name and Pitch value, Pitch mode is written Semitones and
  Fine tune unit Cents, and both target selectors are remapped from 24 targets to
  88. Slider line only; the plugin migrates a 2200024 blob itself. Skips a line
  already storing slider 57+, dry-run by default. Verified by rendering the old
  plugin on the snapshot against the new plugin on every migrated instance: 8 of
  8 bit-identical, plus a crafted old save with drift and ramp on the four shared
  envelope targets.

## Polyrhythm Phase v1 → v3 — the 2026-09-10 crossing

- **`polyv1_to_v3_crossing_20260910.py`** — applies
  `docs/layouts/polyrhythm-v1-to-v3-crossing.md` to the files it is GIVEN (the
  scope is authored, never searched for): renames the `<JS>` line, writes a
  59-slider v3 line, and writes a native 2300088 blob, creating `<JS_SER>` where
  an instance had none. Each voice becomes its absolute MIDI note; a voice
  between notes becomes the nearest note plus cents. Unstored v1 sliders take
  v1's defaults. Reproduces v1's no-blob load, where the visible Drift and Ramp
  values land on target 0. Refuses on a quoted token, an unknown blob or a
  line-count surprise.
- **`polyv1_to_v3_verify_20260910.py`** — renders every instance three ways (old
  plugin on the snapshot; old plugin with bank-bound values rounded to float32;
  new plugin on the converted file) and requires the last two byte-identical.
  `--jobs N` runs in parallel; `--skip-log` resumes, keyed by FULL path, because
  Tensor's files share names with Rozaya's. 144 of 144 identical; the float32
  rounding itself measured at most 1.5e-08.

## Solo in every plugin with voices or bands — 2026-09-10

`docs/layouts/solo-propagation-20260910.md`. Three slider-line migrations, each
applying that authored table to the files it is given:

- **`melody_solo_migrate_20260910.py`** — 105 sliders to 113; a Vn Solo after each
  Vn Active. 73 instances.
- **`shepard_tone_solo_migrate_20260910.py`** — 89 to 97, the same shape. Reads
  Tensor's hand-written lines (extra dashes, no marker) when the ids are
  unambiguous. 10 instances.
- **`resonance_bank_solo_migrate_20260910.py`** — 27 to 28; Band solo at 10. 1
  instance; the plugin reads the old blob with nothing soloed.

**None of the three is safe to re-run over a short line.** "Already done" means a
value stored above the old count, and a line an older build saved at 64 values
has none even after migrating. A second run shifted Tensor's `shepard.RPP` twice;
it was restored from the snapshot and migrated once. To redo, restore first.

## tuning_ref_check.py — does the Tuning reference really move the pitch?

`python tools/tuning_ref_check.py [name ...]`. Twelve plugins, measured with
jsfx_run. The test is an equivalence, not a pitch reading: reference 880 on a
note must render **bit-identical** to reference 440 an octave up, from the start
and when moved while playing, and in plain Hz the reference must change nothing.
A spectrum reading could not see a two-semitone change in Dapple's noise; the
equivalence can. The Shepards, with no note to raise, keep a spectrum reading.

Proven able to fail: a Dapple copy reading `tuning_ref = 440` fails three of four.
All twelve pass as of 2026-09-10. Heartbeat's case uses notes 57/69 because at
note 45 the "All" target leaves S2's value at 120, a note near 8.4 kHz, and
Heartbeat blows up above about 5 kHz in any mode — a separate bug.

## source_note_check.py — does every Source note behave the same?

`python tools/source_note_check.py [plugin ...] [--rev GITREV]`. Bubbler, Sustain
Looper and Passage: correcting Source note must leave the sound bit-identical AND
re-read the Target note (proved by re-picking the old Target equalling Transpose 2).
Built 2026-09-11 when Passage did this and the other two did not. `--rev 45350c6`
fails Bubbler and Sustain Looper, so it can fail. Add the Morpher when its pitch
block is built.

## jsfx_renumber.py — renumber sliders from an authored map

`apply FILE "55:11, 11-54:+1"` rewrites every `sliderN` token in one pass.
`verify OLD NEW MAP` checks three ways: the text is the mapped old file (lines in
any order), declarations match through the map, and two render passes with every
slider nudged are bit-identical. **The text check is the one that matters for a
pure renumber**: a single code line pointed at the wrong slider passed both
render passes on 2026-09-10 and failed the text check. A file that is renumbered
AND edited can only be verified against real projects.

## The Sweeping Filter pitch blocks — 2026-09-10

`docs/layouts/sweeping-filter-r22-r24.md`. 45 sliders to 54; 17 targets.

- **`swf_migrate_r22_20260910.py`** — reads the snapshot
  `_pre-swf-r22-20260910/`, writes the live projects. Which layout each file holds
  is an authored per-file list: Rozaya's 45-control lines, and Tensor's never-
  migrated April lines (23 and 22 values), which take every step since. The
  honest-Hz step is loaded from git (`bf81d1d`, the FINAL version, which also
  rewrites Resonance), not retyped.
- **`swf_verify_r22_20260910.py`** — old build on snapshot against new build on
  migrated project, bit-identical; every instance decoded by control NAME from
  each era's own declarations; Tensor's organic-movement against Rozaya's copy.
- **`swf_blob_remap_test.py`** — synthetic old saves using the three old targets
  no real project used (Pan Sweep Rate, Resonance, Wet/Dry), both old magics,
  drift and ramp. Each must load bit-identically after migration AND differ from
  the same project with no drift, or the comparison proves nothing.
- **`swf_target_test.py`** — each of the 17 targets must change the sound and
  stay stable. Runs the sweep at 120 BPM: at the default 2 BPM an 8-second render
  sits at the top of its sweep, and the Low targets looked broken.

## Sweep Dwell's segments — 2026-09-10

`docs/layouts/sweep-dwell.md`. Four times, three cycle controls and a picker
became a Segment selector with a length mode and value per segment.

- **`sdf_migrate_segments_20260910.py`** — the installed 46-control line to 45,
  and a NEW blob (2500016) carrying the segment banks, since those are no longer
  sliders. Tensor's two instances are skipped: they point at
  `filters/sweep-dwell-filter.jsfx`, which does not exist, so they never loaded.
- **`sdf_segment_test.py`** — the selector checked against the OLD plugin as the
  oracle: each segment edit, All segments, and every length mode must render
  bit-identically to the same thing typed into the old controls.
- **`sdf_migrate_test.py`** — synthetic old projects with drift, ramp, Linked
  Sweep and both host-sync cycle modes, which surges does not use.
- **`sdf_target_test.py`** — each of the 16 targets changes the sound, stable.
  The cycle is shortened so the Low dwell is actually heard.
- **`sdf_transport_test.py`** — beat modes under a MOVING transport: the bar lock
  (a mid-cycle start lines up with a beat-0 start; Seconds must not), parity with
  the old Host x cycle, a live tempo change, and one segment in beats at 60 BPM.
  Needs the runner's `--transport` options; see `jsfx_run/README.md`.

## Resonance Bank's pitch per band — 2026-09-11

`docs/layouts/resonance-bank-r22-r24.md`. 28 sliders to 35; 5 targets to 10.

- **`resonance_bank_migrate_r22r24_20260911.py`** — slider line only; the plugin
  remaps its own old blob. Idempotent by an exact gate: slider 3 of 20 or more is
  Tuning reference, so the line is already done.
- **`resonance_bank_verify_r22r24_20260911.py`** — old build (a993f0f) on each
  snapshot against new on a temp migration, bit-identical, decoded by name;
  synthetic v1/v2/v3 saves with drift and ramp on every old target, both modes;
  each of the 10 targets moves the sound; a whole-plugin target is one setting;
  A4 and the width units by equivalence. **It caught a real fault**: extra
  `rand()` draws in `@init` shift every later Random drift.

## The small R24 batch — 2026-09-11

`docs/layouts/r24-small-batch-20260911.md`. Veil, Bubbler, Dapple and Tremolo put
their targets in control order; each plugin remaps its own old saves.

- **`r24_batch_migrate_20260911.py`** — reads the snapshot, writes the live file,
  refuses a file changed since. Carries Tensor's first-release Tremolos, the
  `custom-polyrhythm` template and `scattered`'s 32-control Dapples through every
  step they missed; rewrites `knocking`'s Tremolo blob. `--bridge` for the test
  project once it is closed in REAPER.
- **`r24_batch_verify_20260911.py`** — every current copy old against new (and new
  on the unchanged snapshot); synthetic saves in every old format; each new target
  moves the sound; the broken copies against the last build that read their layout
  (705ee29, 272a438), by name, and Tensor's playing-around against Rozaya's copy.

## Breath Generator's eighteen targets — 2026-09-11

`docs/layouts/breath-gen-r24-20260911.md`. No index moves, so current copies need
nothing written.

- **`breathgen_tensor_migrate_20260911.py`** — Tensor's seven first-release lines
  (13 values, no blob) to the 41-control line and a 2500007 blob, by the same rule
  Rozaya's copies of those lines got on 2026-09-09. Snapshot in, live out.
- **`breathgen_r24_verify_20260911.py`** — current copies old against new; synthetic
  saves in three old formats; the eleven new targets; Tensor's seven against the
  last build that read their line (0ae0c75), by name, and against Rozaya's copies
  value for value, blob for blob and in sound.

## Heartbeat's eighteen targets — 2026-09-11

`docs/layouts/heartbeat-r24-20260911.md`. The plugin remaps an old four-target save.

- **`heartbeat_r24_migrate_20260911.py`** — moves `transformation.RPP`'s `<JS_SER>`
  out of its `<JS>` block to where REAPER writes it (content unchanged), and
  carries Tensor's first-release `transformation` over by the rule Rozaya's copy
  got. Snapshot in, live out.
- **`heartbeat_r24_verify_20260911.py`** — current copies old against new; synthetic
  saves in four old formats; the fourteen new targets; Tensor's copy against
  9d33c5b by name and against Rozaya's copy value for value, blob and sound.
- **Trap:** `jsfx_run` finds a `<JS_SER>` inside the `<JS>` block as readily as
  after it, so a misplaced blob passes every render check. Look at the file.

## Rhythm Track's sixteen targets and Drift movement — 2026-09-11

`docs/layouts/rhythm-track-r24-20260911.md`. Drift movement inserted at 36.

- **`rhythm_r24_migrate_20260911.py`** — the bridge copy's line (36-39 to 37-40,
  selectors 1 to 2), and Tensor's two first-release lines by name with a new 2500016
  blob. Snapshot in, live out.
- **`rhythm_r24_verify_20260911.py`** — the bridge old against new; synthetic saves in
  four old formats; each new target; Drift movement; a bar edit waiting for the
  downbeat, against the old build that did not; Tensor's two against e09eec7.
- **Trap met:** a 1 s sine read on 0.5 s beats or 2 s bars sits on its zero
  crossings, so "drift changes nothing" was the test. Use a period that is not whole.

## Womb's forty-nine targets — 2026-09-11

`docs/layouts/womb-r24-20260911.md`. No slider moves; the plugin remaps old blobs.

- **`womb_r24_migrate_20260911.py`** — every line's two selectors remapped (two copies
  have unversioned blobs the plugin cannot remap from); `scattered`, never carried
  over, taken 70 -> 88 by the two 2026-09-09 scripts' own imported rules; `womb-and-
  baby`'s Breath rate drift converted only with `--convert-womb-and-baby`.
- **`womb_r24_verify_20260911.py`** — works on temp copies, so it runs before anything
  is written; `applied` then compares the live files. Old against new for all ten
  (scattered against 92effbe), four old save formats, the names, all 38 new targets,
  Breath rate against segments typed by hand, Drift movement.
- **Traps met:** a 1.3 s wave read by a three-beat gate at 70 BPM (2.57 s) aliased,
  so three gates "changed nothing"; and a breath-hump counter that could not count a
  one-second breath. Measure the period instead.

## The Morpher's fifty-five targets — 2026-09-11

`docs/layouts/spectral-vowel-morpher-r24-20260911.md`. No slider moves.

- **`morpher_r24_migrate_20260911.py`** — the two selectors (35, 44) of all 123 lines,
  from the 24-target list to the 55. Snapshot in, live out.
- **`morpher_r24_verify_20260911.py`** — **pins the plugin's per-load `time_precise()`
  rand scramble in test copies of both builds**; without it two renders of one build
  never match. All 123 old against new; real 24- and 7-target blobs with drift and
  ramp on every old target; the 31 new targets; an "all layers" entry reaching past its
  first member; names. `--jobs N` runs in parallel; Morpher renders are slow.

## bridge_ui_test.py — what only REAPER can show

Drives the real plugins in REAPER through `kin_bridge.lua`, in
`E:/reaper/finished/test-projects/claude-testing002-bridge.RPP` (18 plugins, one per
track, volume at zero -- NOT muted, in case REAPER skips muted tracks). `drive`
checks every Drift/Ramp target selector, every note-name mirror, and the per-item
selectors (Polyrhythm Voice, the pitch targets, Resonance Bank Band, Morpher Layer,
Passage Capture slot), leaving distinct values; after Rozaya saves and reopens,
`verify` re-selects each and reads it back. Compares normalized positions against
src's declared ranges, so display rounding cannot hide a wrong value.
2026-09-11: 116 live checks and 86 after reopen, all pass. Traps met: the board is
rewritten every 0.4 s and a read can land mid-write; a target list may hold only
two entries (Rhythm Track), and index 2 then silently means 1. A path with a space
must be quoted in an RPP (`<JS "glasswings/heartbeat gen.jsfx" ""`).

## R25 — which kind a control is, measured and written into its name (2026-09-12)

Rule and history: `docs/suite-consistency-plan.md` R25, `docs/history/R25.md`. The list:
`docs/layouts/r25-labels-20260912.md` (260 rows, 18 plugins; Passage waits for its rebuild).

- **`selector_scope_probe.py`** — live in REAPER through the bridge, in claude test: set a
  control on option 0, switch the selector, read, set, switch back, read. PER / ALL / `?`.
  Judge by what option 0 shows on return; option 1 may hold the test value by chance. A
  plugin with no claude test track needs a temporary one, played and stopped once first.
- **`r25_names.py`** — `base(name)` strips the kind, so tools match a control by name before
  and after; `bridge_ui_test.py` would otherwise have skipped its Drift movement checks.
- **`r25_build_list.py`** — measured report + track-to-file map to list rows; refuses to guess.
- **`r25_rename_apply.py`** — applies the list: exact old label on the exact slider, already
  applied counts as done, anything else refuses; re-reads every file after writing.
- **`r25_pages_apply.py`** — carries each kind onto the plugin pages' entry lines, from the
  list only; selectors and "A / B" entries handled; refuses what it cannot match.
- **`hidden_limit_audit_20260913.py`** (+ `_controls.json`) — LISTENS for controls the code
  stops short of: each range-sweep control at half its old ceiling, the old ceiling, halfway
  and the new top, in up to three saved copies. Found Low cut (500) in Passage and the
  Morpher; "couldn't judge" means not heard, never clean. Ids are 2026-09-13's -- re-match.
- **Traps met:** a byte-order mark on a PowerShell-joined report dropped its first line; a
  file name with a space dropped a whole plugin; backticks and quotes in inline
  `python -c` broke two checks -- put checks in files. The traps that were caught were
  caught by scans independent of any list, and by reading the list by hand.

## morpher_cold_load_check_20260912.py — no silence on project load

A Morpher saved on Capture point 0 and Capture average 1 never analysed its captures until
the first play, so a project opened stopped was silent. Every live instance, old build
against new, rand pinned: playing bit-identical; stopped sounds wherever playing does; and
the old build silent stopped on the copies on both defaults (the can-fail). **Render with
SILENT input**: the Morpher passes input through, and a -60 dB noise in made silent copies
read as sounding. Passage's version is the `coldload` section of its verify tool.

## reaper_bridge.py and probes/ — driving REAPER itself (2026-09-12)

`kin_bridge.lua` (in REAPER's Scripts folder, not this repo) now drives REAPER as well as
controls: transport, cursor, loops, tempo, tracks, effects, any action, `eval`/`evalfile`
for anything else. Its grammar is at the top of the script. `reaper_bridge.py` sends one
command and waits for its answer (`send`), or parses the manifest (`board`):
`python tools/reaper_bridge.py "state"`. **Send non-idempotent commands once** — a retried
tab close closed the wrong tab. Test inside `claude-testing002-bridge.RPP` on a temporary
track; never open or close tabs. `probes/position_probe.jsfx` (installed in
`Effects/claude-test-tools/`) reports play_state, positions, @init runs and blocks as
sliders, so the manifest shows what REAPER tells a plugin. Findings: `docs/planned-features.md`,
"Pause is not stop".

## lock_test.py — does a tempo-synced plugin lock to the SONG?

A render starting a few beats into the song must line up with one starting at beat
0, shifted by those beats; the same plugin at the same speed in a free mode is the
control and must NOT line up. Effects compare samples (sine input, whole cycles
over the shift); Rhythm Track and Shepard Scale compare loudness envelopes;
Melody compares the PITCH in each 100 ms window with three voices on, because it
restarts the landed note by design and one voice hides everything.
2026-09-11: Sweeping Filter, Tremolo, Stereo Phaser, Rhythm Track and Shepard Scale
lock. **Melody does not**: its placement runs in the first sample and is
overwritten two blocks later when the settle hold releases the first note to
voice 1. **Fixed 2026-09-11 at Rozaya's request**, with the condition that it must
not force playing the project to hear anything (the reverted `dcfeead` did): the
placement now waits for the same settle hold, and never touches the stopped
transport. This is a different symptom from `docs/open-bugs.md` entry 1 (instances
scattering on project open with the transport stopped), which stays CLOSED by
Rozaya's decision; nothing here reopens it.

## melody_placement_test.py — the Melody placement fix, four checks

Old build (8ad5da1) against new. 1: transport STOPPED, bit-identical and audible.
2: all 27 saved beat-mode instances played from the top, 60 s -- 25 bit-identical,
and the 2 that differ (instance 9 of `simple-sequence` and `-check`, Play for 8 /
Rest for 8) must equal the same instance in a free-running mode, which never places:
the old build fitted 7 notes into the first play period, the new fits 8. 3: song
starting at beat 2 lands on voice 3. 4: a seek while playing lands right (the runner
does not re-run `@init` on a locate, so 3 is the check for REAPER's play path).

## Earlier 2026-09-10 migrations, indexed late

- **`looper_migrate_pitchblock_20260910.py`** — Sustain Looper, 8 sliders to 30,
  per `docs/layouts/sustain-looper.md`. Idempotent: skips a line storing slider 14.
- **`melody_migrate_r22r24_20260910.py`** — Melody Phase, 96 to 105, per
  `docs/layouts/melody-phase-r22-r24.md`. Line only; the plugin remaps its own
  blob from 28 targets to 55. Idempotent: skips a line storing anything above 96.
- **The ysfx fork** that `jsfx_run` builds against (Joep Vanlier's, 256 sliders)
  is documented in `tools/jsfx_run/README.md`, with the build commands.

## doc_budget.py

Checks the docs a session actually reads against a line budget, and exits 1 if
one is over.

```bash
python tools/doc_budget.py
```

**Run it before committing any change to `CLAUDE.md` or under `docs/`.**

It exists because `CLAUDE.md` was cut from 824 lines to 451 on 2026-09-03, from
1298 to 784 on 2026-09-06, and was back at 1043 by 2026-09-08 — growing about
fifteen lines per commit and never once shrinking in between. Three separate
sessions tidied it; it grew back every time. The same thing was happening to the
other docs: the consistency plan went from 704 lines to 2742 in nine days, the
session log from 475 to 1998 in four.

Tidying is not the fix, because the growth is structural — every session writes
down what it learned so the next one does not repeat it, and nothing ever
deletes. A ceiling is the fix, and a ceiling only holds if something checks it.
The rules that have held in this repo are the ones a script enforces.

**When it says OVER, do not raise the number.** Delete something, or move it to
the file where it belongs and leave a one-line pointer. One home per fact.

`docs/session-log.md` is deliberately unbudgeted — it is append-only history and
capping it would mean rewriting what happened. It gets rotation instead; the
note at the bottom of the script says how.
