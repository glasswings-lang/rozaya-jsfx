# tools

Small utility scripts that support the suite but aren't JSFX plugins.

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
