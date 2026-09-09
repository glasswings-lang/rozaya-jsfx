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

- **Timbre, for anything noise-based.** ysfx's EEL2 handles the `%` in this
  suite's Park-Miller noise generators differently from REAPER's, so the noise
  degenerates and the filters rail to DC. Envelope, timing and filter TUNING
  stay perfectly readable; the actual sound does not. Verified on breath_gen.
- **64 sliders maximum.** `polyrhythm_phase` (86) will not load.
- **REAPER's restore ORDER.** `ysfx_load_state` applies sliders and serialized
  data in one defined order. REAPER makes no such guarantee, and the ordering
  gap between `@slider`, `@block` and `@serialize` is where several real bugs in
  this suite have lived. A clean run here does NOT prove REAPER is clean.
- **Anything needing ears.** It measures difference, never quality.

**A tool that quietly covers less than it claims is worse than none.** On
2026-09-08 this tool produced a bit-identical measurement that was completely
sound, and it was read as proving something about a scenario REAPER never
actually performs. The number was right; the scenario was invented. Check that
the run you set up is a run that can really happen.
