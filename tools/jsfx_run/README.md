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

```bash
git clone --depth 1 --recurse-submodules https://github.com/jpcima/ysfx.git C:/git-src/ysfx
cd C:/git-src/ysfx
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

## What it CANNOT tell you — read this before trusting a clean result

- **Filter FREQUENCY, for anything noise-based — and this is bigger than it
  sounds.** Measured on breath_gen 2026-09-09: moving a filter centre from 300 Hz
  to 1200 Hz changes the output by 2.4e-07. Four times the frequency, and the
  runner sees essentially nothing, because the degenerate noise rails the filter
  to DC and the DC level barely depends on the cutoff. **Anything about pitch,
  cutoff or resonance in a noise-based plugin is INVISIBLE here.** A clean result
  means nothing; it is an ear test.
- **Nested selectors bite the command line exactly as they bite a user.**
  `--slider 25=5 --slider 26=30` does NOT drift target 5 by 30. Setting the
  selector makes @slider save the visible values to the OLD target and load the
  new one's, so the amount lands on the previous target and is then overwritten.
  Set the selector with `--slider` and the values with `--set-after`, which is
  also the order a person does it in. This produced a false PASS on 2026-09-09
  that was committed before it was caught.
  The cause: ysfx's EEL2 handles the `%` in this suite's Park-Miller noise
  generators differently from REAPER's, so the noise degenerates. **Envelope and
  timing stay perfectly readable** — that half is genuinely reliable and caught
  three real bugs the same day.
- **A PROJECT LINE OVER 64 SLIDERS IS SILENTLY TRUNCATED, and this is the worst
  thing in this file.** It does not refuse and it does not warn. `--rpp` applies
  only the values at or below slider 64 and drops the rest; the "N sliders"
  it prints is the count it actually applied, so `61 sliders` from a line holding
  87 values is the tell. **Any comparison of a >64-slider plugin is therefore a
  comparison of a SUBSET**, and if a migration moves values across the boundary,
  the two runs are made from different settings and will differ for no musical
  reason. Measured 2026-09-09 on `melody_phase` and `womb_sound_generator_v3`.
  Exposed today: `melody_phase` (96), `womb_sound_generator_v3` (88),
  `polyrhythm_phase` (86), `shepard-tone` (75). Under the line and therefore
  trustworthy: Bubbler (37), Dapple (38), Heartbeat (40), Rhythm Track (39),
  Breath Generator (41).
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
