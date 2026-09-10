# jsfx_run — compile and RUN a plugin, outside REAPER

**This is the tool this repo has needed for months and kept declaring impossible.**
It compiles a `.jsfx`, loads a real project's saved state, runs it, and prints
the samples that come out. Behaviour becomes something you MEASURE instead of
something you predict.

## Why it exists

On 2026-09-08 a Breath Generator rebuild passed a clean lint, a verified
migration, 238 file assertions, three careful read-throughs and a fresh-eyes
audit — and was audibly broken the moment Rozaya pressed play. Every one of
those checks read the source text. None of them had ever run a plugin.

`CLAUDE.md` said for months that JSFX could not be compiled outside REAPER.
That was never true; nobody had looked.

## Build

Needs CMake and MSVC (Build Tools 2022 is enough).

Build against **Joep Vanlier's maintained fork** of ysfx. It supports 256
sliders, as REAPER does; the original jpcima/ysfx stops at 64. Its
`ysfx_slider_set_value` takes a fourth `notify` argument, which `jsfx_run.cpp`
passes as `true`.

```bash
git clone --depth 1 --recurse-submodules --shallow-submodules https://github.com/JoepVanlier/ysfx.git C:/git-src/ysfx-joep
cd C:/git-src/ysfx-joep
cmake -S . -B build -G "Visual Studio 17 2022" -A x64 \
      -DCMAKE_BUILD_TYPE=Release -DYSFX_PORTABLE=ON \
      -DYSFX_PLUGIN=OFF -DYSFX_GFX=OFF -DYSFX_TOOLS=OFF -DYSFX_TESTS=OFF
cmake --build build --config Release --target ysfx
```

`YSFX_PORTABLE=ON` matters: without it the x64 build wants `nasm` for the EEL2
JIT. Portable mode uses the interpreter, which is slower and entirely fine here.

Then:

```bash
cd tools/jsfx_run
cmake -S . -B build -G "Visual Studio 17 2022" -A x64
cmake --build build --config Release
```

## Use

```bash
# every slider, with its real parsed range and default
jsfx_run src/breath_gen.jsfx --list

# what the plugin HOLDS after a project is restored -- the reload path
jsfx_run src/breath_gen.jsfx --rpp E:/reaper/templates/breathscapes.RPP          --fx breath_gen --list

# run a REAL project's state -- slider line AND the <JS_SER> blob
jsfx_run src/breath_gen.jsfx --rpp E:/reaper/templates/breathscapes.RPP \
         --fx breath_gen --seconds 36 --rms 500

# dump samples for comparison
jsfx_run src/breath_gen.jsfx --rpp ... --csv out.csv --quiet
```

**The check that would have caught 2026-09-08**, and which should now run before
any migration is called done:

> Run the OLD plugin on the OLD project. Run the NEW plugin on the MIGRATED
> project. If the migration was not supposed to change the sound, the two sample
> streams must be **bit-identical**. "Nothing should sound different" stops being
> a prediction and becomes a measurement.

## Feed it something — `--input`

**It used to feed silence and nothing else, and that made every EFFECT plugin
untestable while appearing to pass.** A pure filter renders 529,200 zero samples,
so old-versus-new compares bit-identical no matter what you changed, including
deleting the audio path. Added 2026-09-09 after exactly that happened.

```bash
jsfx_run src/sweep-dwell-filter.jsfx --input noise --seconds 12 --csv out.csv
jsfx_run src/veil.jsfx --input sine --input-hz 440 --input-db -6 --csv out.csv
```

`silence` (the default, unchanged), `noise`, or `sine` with `--input-hz` and
`--input-db`. **Both generators are deterministic** — a fixed-seed LCG rather than
`rand()`, which is process-global — so two runs of the same command are byte
identical and a comparison means something.

**Check for a non-zero sample before believing any effect plugin's result.**

## What it CANNOT tell you — read this before trusting a clean result

- **Noise-based plugins, on the original library only.** Its EEL2 mishandles the
  `%` in this suite's Park-Miller noise, so the noise rails to DC and filter
  frequency, cutoff and resonance are invisible. The fork build produces real
  noise: on breath_gen, moving the filter centre from 300 Hz to 1200 Hz takes the
  zero-crossing rate from 1471 to 2484 per second (2026-09-10). Measurements of
  noise-based plugins made before that date could not see frequency.
- **Nested selectors bite the command line exactly as they bite a user.**
  `--slider 25=5 --slider 26=30` does NOT drift target 5 by 30. Setting the
  selector makes @slider save the visible values to the OLD target and load the
  new one's, so the amount lands on the previous target and is then overwritten.
  Set the selector with `--slider` and the values with `--set-after`, which is
  also the order a person does it in. This produced a false PASS on 2026-09-09
  that was committed before it was caught.
- **Controls with a two-way mirror** (note name and pitch value) only capture a
  change made after the first block. Set them with `--set-after`, or the change
  is silently ignored.
- **Built against the original jpcima/ysfx, it silently drops every slider above
  64**, in `--rpp`, `--slider` and `--list`. The fork build reaches all 256.
  Still check the "N sliders" line against what the project line holds.
  **Any measurement on a plugin over 64 sliders made before 2026-09-10 was made
  on a subset.**
- **REAPER's restore ORDER.** `ysfx_load_state` applies sliders and serialized
  data in one defined order. REAPER makes no such guarantee, and the ordering
  gap between `@slider`, `@block` and `@serialize` is where several real bugs in
  this suite have lived. A clean run here does NOT prove REAPER is clean.
- **Anything needing ears.** It measures difference, never quality.

**`--list` applies `--rpp` state before listing, as of 2026-09-09.** It used to
list declared defaults only, which is why it could not see that Breath
Generator's `@serialize` was restoring the pitch block in the wrong order --
mode, note and value rotated between them on every project reload, for a filter
centre of 1 Hz. A reload bug is invisible to a tool that never reloads.

**A tool that quietly covers less than it claims is worse than none.** On
2026-09-08 this tool produced a bit-identical measurement that was completely
sound, and it was read as proving something about a scenario REAPER never
actually performs. The number was right; the scenario was invented. Check that
the run you set up is a run that can really happen.
