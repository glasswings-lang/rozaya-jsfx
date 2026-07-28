# tools

Small utility scripts that support the suite but aren't JSFX plugins.

Every one runs from a terminal and prints its full flag list with `--help`.
`rate_calc.py`, `morpher_to_passage.py` and `passage_migrate_sliders.py` need
nothing installed; `loop_finder.py` needs two packages (noted below).

| Tool | For |
|---|---|
| [`rate_calc.py`](#rate_calcpy) | base rate for a second instance, so a chosen voice lands where you want it |
| [`loop_finder.py`](#loop_finderpy) | pulling clean looping samples out of a recording |
| [`morpher_to_passage.py`](#morpher_to_passagepy) | moving a Spectral Vowel Morpher project onto its sibling Passage, captures and all |
| [`passage_migrate_sliders.py`](#passage_migrate_sliderspy) | repairing older projects after Passage gained a control mid-list |

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
