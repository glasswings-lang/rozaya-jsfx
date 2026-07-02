# Planned features

Captured from a design session on 2026-05-25. Not yet implemented.
Pick this up when ready to code; all design decisions are settled.

## Slider budget per plugin

Modern Reaper JSFX supports `slider1` through `slider256`, so 64 isn't a hard limit — but staying at or under 64 keeps the slider IDs simple and matches the project's habit. After the additions below:

| Plugin | Pre-change | Landed | Remaining | Final total |
|---|---|---|---|---|
| polyrhythm_phase | 59 (highest `slider59`) | 5 (slider60 Direction & Reverse, slider61 Reverse Drift Offset, slider62 Start Delay, slider63 Play for, slider64 Rest for) | 0 | **64** (right at the line) |
| melody_phase | 61 (highest `slider61`) | 2 (slider62 Start Delay, slider63 Direction) | 0 | 63 |
| rhythm-track | 13 | 1 (slider14 Start Delay) | 0 | 14 |

The polyrhythm_phase budget is why Direction and Reverse Type were collapsed into a single 5-option slider (`Direction & Reverse`) rather than two — see section 1 below.

---

## Polyrhythm Phase

### 1. Direction & Reverse (single combined slider)

Originally drafted as two sliders (Direction = Forward/Reverse/Both, Reverse Type = Permute/Time, with Reverse Type hidden when Direction = Forward). Collapsed into one 5-option slider so the only valid combinations are the only options — no conditional hiding, and the slider budget stays at 64.

One new slider at END of file:

- **Direction & Reverse** `[Forward | Reverse — permute | Reverse — time | Both — permute | Both — time]`

Five behaviors:

| Option | Behavior |
|--------|----------|
| Forward | Current behavior, 8 voices |
| Reverse — permute | 8 voices. **Drift values** mirrored V1↔V8, V2↔V7, V3↔V6, V4↔V5. Notes, gains, phase offsets, active flags stay in place. |
| Reverse — time | 8 voices, tremolo phase decrements instead of incrementing — asymmetric envelopes play backwards |
| Both — permute | 16 voices: forward 8 (slots 0-7) + drift-mirrored reverse 8 (slots 8-15). Each note plays at two different cadences across the two layers. |
| Both — time | 16 voices: forward 8 (slots 0-7) + time-reverse 8 with same drift (slots 8-15). With asymmetric envelopes the reverse layer fills in the gaps of the forward layer's pulses, creating a drone. |

**Why "permute" mirrors only drift, not all settings.** The naive design (swap V1↔V8 across every per-voice slider together) is a mathematical no-op on the audio output: the audio sum is commutative across voice slots, so relabeling which slot holds which voice produces an identical waveform. Realised mid-implementation (May 2026) after the user A/B tested it and reported "permute sounds identical to forward." The user's mental model from the start was "swap just the cadence assignments" — which is what the code does now. Mirroring just `v_dr` makes the swap audible (V1's note now fires at V8's cadence and vice versa) and matches the user's diamonds.RPP workflow where drift palettes were the differentiator between paired tracks.

In Both modes:
- 16 voices total — memory layout already sized for 16 slots per bank per existing comments in `@init`; just need to use slots 8-15
- Reverse layer derives its per-voice settings from the forward layer (no separate config — the whole point is "no manual adjustment")
- Pan uses same settings for both layers
- Mix at unity, no balance knob (existing Depth dB handles overall volume)

### 1b. Reverse Drift Offset — LANDED

Slider 61. `<-1000, 1000, 0.001>` default `0`. Visible only when Direction & Reverse is set to a Both mode (`slider_show(slider61, is_both)`).

Adds a constant to every value in the reverse layer's Drift / Rate palette. Applied in @slider after the optional drift mirror, before the v_trem_freq computation. With offset = 0 the two layers run at matched cadences (mirrored in Both — permute, identical in Both — time). Non-zero values shift the reverse layer's drift range away from the forward layer's, breaking the lockstep.

**Why this exists.** Validated against `E:\reaper\diamonds (0.5).RPP` (2026-05-25), where the user stacks four polyrhythm_phase tracks per scene: each pair shares notes, octave, waveform, tuning, binaural, gain, and per-voice semitones — the ONLY difference between the two tracks of a pair is the drift palette range. Track 1's drift is 0.00 → 0.35 (ascending, +0.05 step); track 3's drift is 1.55 → 1.20 (descending, −0.05 step). The descending pattern is the drift values mirrored (V1↔V8 in drift only) plus a +1.20 offset. Same math collapses the descending1 pair with offset 0.40.

With Both — permute + offset 1.20 (or 0.40 for the other pair), one plugin instance produces what two stacked tracks used to. The descending2 and descending1 pairs in diamonds still need separate instances because they differ in notes / octaves / gain ramps — those are genuinely independent and Both mode doesn't collapse them.

**Why hidden in single-layer modes.** In Forward / Reverse — permute / Reverse — time there's only one layer, so adding a constant to every drift value is mathematically identical to nudging the global Rate Value slider. A duplicate control would just confuse — hiding is the right call.

### 2. Start delay

One new slider:

- **Start delay** — units match Rate Mode (BPM beats / Seconds / Hz cycles)

Behavior:
- Plugin sits silent for N units after playback starts, then begins normally
- Re-arms on each transport stop/start — detect via `play_state` transitions
- Doesn't affect per-voice phase logic — just gates output

### 3. Play/Rest gating — LANDED (v2)

Two new sliders at the end of the file:

- **Play for (cycles)** — slider63
- **Rest for (cycles)** — slider64

Integer per-voice cycle counts. Each voice counts its OWN cycles, so V8 (high drift) hits its play threshold sooner in real time than V1 (drift 0) and enters rest first. The rest counter advances at the same per-voice rate, so V8 also wakes first — per-voice symmetry through both halves of the loop. Feature disabled when either slider is 0, in which case the plugin is functionally identical to v1.

**Implementation notes (landed):**

- Per-voice counter at memory slot 304 (`v_pr_cycle[i]`) advances at `v_trem_freq[i] / srate`. Same value drives both play and rest thresholds.
- Normalizer divides by precomputed `total_active` (set in `@slider`) rather than the per-sample currently-audible count — keeps surviving voices' level steady when other voices enter rest. (Was a pre-existing latent bug in v1; only became audible once voices started dropping in/out of rest.)
- **Depth-floor cancel on the final release.** On the final cycle of every play period, the always-on Depth term (`amount`) is dropped from the gain formula during the release portion (and any silent tail) of the LFO. So during that final release, gain = `lfo_val * (sc + amount)` instead of `lfo_val * sc + amount` — same peak at `lfo_val = 1`, decays all the way to 0 at `lfo_val = 0` instead of bottoming at the Depth floor. The voice glides to actual silence before the rest freeze regardless of the user's Depth setting. Cycles 1 through (Play for - 1) play with the normal formula — only the final release shape changes.
- **Conventional transport.** No `ext_noinit`, no transport-edge reset logic, no freeze on stop. `@init` runs on every transport play (Reaper default), which re-zeros voice phases, gain smoothers, Start Delay counter, per-voice cycle counters, and resting flags. Stop/play gives a clean restart — same behavior as v1.

**Caveat — Release = 0%.** The Depth-floor cancel only fires during the release portion of the LFO. With Release = 0% there is no release portion (zero width), so the override never fires and you get a sharp cutoff at the rest boundary. For a clean rest entry, use a non-zero Release setting.

**Wake side needs no special handling.** On wake from rest, target_gain jumps from 0 to whatever the LFO says at the resumed phase (possibly full peak with Attack = 0%). The existing 3 ms `gain_l` / `gain_r` smoother — the same one that prevents Attack = 0% from clicking at normal cycle wraps — ramps gain_l from 0 to the new target over ~3 ms. Perceptually a clean attack, not a click. Same anti-click mechanism, same behavior at every gain transition.

**Rejected alternatives during iteration:**

1. **Slower rest-fade smoother.** Bolt a longer time-constant onto the smoother for rest entry. Felt like a band-aid — cushioned the drop without addressing the underlying "LFO doesn't reach silence" issue.
2. **Settings-only (Depth = 0 + Attack > 0 + On Duration < 100%).** Discarded as primary fix because it pushed the burden onto user settings. Still valid as a sound-design tip in the manual.
3. **Per-cycle fade shoulders.** First-cycle fade-in + last-cycle fade-out applied as a multiplier on top of the normal LFO. Ate two full cycles of the user's `Play for` count for fades and didn't match the "voice rings, then rests" mental model.

Earlier worry about "drift collapse" from waiting for the cycle end turned out not to apply with per-voice rest counters: voices wake at different wall-clock times because V8's counter advances faster than V1's, so the polyrhythm cadence lives in the wake-time differences rather than in relative freeze phases.

**Iteration history.** v2 went through three approaches before landing: in-place edits to polyrhythm_phase on `feature/play-rest-gating` (abandoned), a sibling plugin `polyrhythm_phase_loops.jsfx` while the rest-entry sound was being worked out, then consolidation back into polyrhythm_phase.jsfx once the depth-cancel approach proved solid in user testing. The `feature/play-rest-gating` branch is parked as a historical record.

---

## Melody Phase

### 1. Direction

One new slider (at END of file):

- **Direction** `[Up | Down | Up-Down (repeat) | Up-Down (no repeat) | Down-Up (repeat) | Down-Up (no repeat)]`

Six distinct behaviors (using 4 voices for examples):

| Mode | Sequence |
|------|----------|
| Up | 1, 2, 3, 4, 1, 2, 3, 4, ... (current behavior) |
| Down | 4, 3, 2, 1, 4, 3, 2, 1, ... |
| Up-Down (repeat) | 1, 2, 3, 4, 4, 3, 2, 1, 1, 2, 3, 4, 4, ... (boundary voices double) |
| Up-Down (no repeat) | 1, 2, 3, 4, 3, 2, 1, 2, 3, 4, 3, ... |
| Down-Up (repeat) | 4, 3, 2, 1, 1, 2, 3, 4, 4, 3, 2, 1, 1, ... |
| Down-Up (no repeat) | 4, 3, 2, 1, 2, 3, 4, 3, 2, 1, 2, 3, ... |

Interaction with existing settings:

- **Active voices skipped** in all directions (existing behavior preserved). If V2 is Off in a 4-voice setup, Up plays 1→3→4→1→3→4, Down plays 4→3→1→4→3→1, etc.
- **Sequence Length** slider defines the pool of voices (first N); Direction defines walk order through that pool. So Down with SeqLen=4 plays V1-V4 in order 4,3,2,1.
- **Loop=On**: all directions loop forever (Up loops as 1...8/1...8, Down loops as 8...1/8...1, bounce modes keep bouncing).
- **Loop=Off + Up or Down**: plays once and stops (existing behavior for Up).
- **Loop=Off + Up-Down or Down-Up (either variant)**: plays one complete bounce cycle then stops.
- **"Next voice in" slider**: always means "delay from this voice firing until the next firing event." Works naturally with all directions including the doubled boundary in repeat-mode bounce (V8's "Next voice in" applies twice in a row at the turnaround: once to schedule the repeat V8, once to schedule V7).
- **Glide/Legato**: glides between consecutive voices in whatever direction they're going; existing glide code reads the previous-voice frequency at each transition, so this should work with no glide-specific changes.

### 2. Start delay

Same as polyrhythm — one slider, units match Rate Mode, re-arms on transport stop/start.

---

## Rhythm Track

### Start delay

Same as polyrhythm and melody.

(No Direction feature — Rhythm Track is a metronome, not a sequencer.)

---

## Spectral Vowel Morpher — render-speed optimization (LANDED 2026-07-01)

**Status:** ✅ **LANDED 2026-07-01** (commit `793eebc`, pushed). The Primary fix below — wavetable the voice oscillators — shipped into `src/spectral_vowel_morpher.jsfx`. Internal only: **no sliders, no @serialize change, so existing projects open unchanged and just render faster.** Ear-verified by Rozaya as perceptually identical via an A/B (a `_wt` test build swapped into a byte-clone of a real project). The Secondary iFFT idea below was NOT needed and stays optional. Plan preserved for reference. Original diagnosis (2026-06-30): renders stacking 3 instances crawled near/below realtime; the per-sample `sin()` cost was the cause, and the wavetable removed it.

### Where the cost is

Two continuous costs, both real, multiplied by however many instances are stacked:

1. **Per-sample additive voice engine (`@sample`).** The `loop(NHARM, …)` (NHARM = 64) calls `sin()` **twice per harmonic** — voice A (`sin(hph[vn])`) and voice B (`sin(hphB[vn])`) — so ~128 `sin()` per output sample, ≈ 6 M sines/sec **per instance**, continuously while audio plays. This is the dominant ongoing cost and the best target.
2. **Wash FFTs (`gen_grain` → `build_spectrum`).** `build_spectrum()` runs **twice per grain** (L = `build_spectrum(0)`, R = `build_spectrum(1)`), each ending in `ifft(FFTSIZE = 32768)`. At Wash grain 150 ms / 48 k, HOP ≈ W/4 ≈ 1800 → ~27 grains/sec → ~54 × 32768-pt iFFTs/sec, plus the NBINS (16385) morph/spread/denoise/random-phase loops around each.

Also a one-time spike at every render start: the `@block` play-edge re-runs `compute_spectrum` + `analyze_harm` (a 32 k FFT + YIN) for every used slot.

### Primary fix: wavetable the voice oscillators

Replace the `sin()` calls in the `@sample` `NHARM` loop with a precomputed sine **wavetable** + linear interpolation. **Keep the phase accumulators (`hph[]`, `hphB[]`) and the increment math exactly as-is** — only the evaluation of `sin(phase)` changes.

Sketch (pure eel2, no new sliders, no dependencies):
- `@init`: allocate a table and fill one period plus a guard sample — `TBL = 8192; i = 0; loop(TBL+1, sintab[i] = sin(TWOPI*i/TBL); i += 1;);`
- In the loop, replace `sin(hph[vn])` with: `ph = hph[vn]; fidx = ph*(TBL/TWOPI); i0 = floor(fidx); fr = fidx - i0; s = sintab[i0]*(1-fr) + sintab[i0+1]*fr;` (same for `hphB[vn]`). The accumulators already wrap to [0, TWOPI), so the guard sample at `sintab[TBL]` covers `i0 = TBL-1`.

**Why it's audio-safe (the analysis that settled it):**
- **No pitch change.** Frequency is set by the phase *increment* (`hph[vn] += TWOPI*(vn+1)*fA/srate`), which we don't touch. The table only shapes each sine, so every harmonic stays locked to its exact `(vn+1)*f0` — no detune, no drift, no inharmonic content.
- **Only error is waveshape fidelity** → faint harmonic distortion + noise floor ~−80 to −100 dB with a decent table + linear interp. That energy is **harmonically locked** (distortion of harmonic n lands on 2n, 3n… = harmonics of the same f0 already present), so it can't create "weird"/inharmonic frequencies — just an inaudible whisper on tones already there, especially invisible under random-phase wash.
- **No compounding.** The additive engine is open-loop (sum of independent oscillators, no feedback), so per-sample error stays bounded — it can't ripple/snowball up the spectrum.
- If ever paranoid: bigger table or cubic interp → immeasurable error. Plain linear is already inaudible here.

**Why NOT a recursive oscillator** (the obvious "even cheaper" route): it has feedback (a recurrence), so amplitude/phase can **drift and accumulate** — exactly the ripple-and-compound failure mode the wavetable avoids — and the per-sample frequency changes here (Pitch slider + morph between two f0s) make recursive coefficient updates awkward. Wavetable is the safe pick.

### Secondary (lower priority, touch with care): the wash's double iFFT

`build_spectrum` runs a full 32 k iFFT per channel; the only L/R difference is the per-bin phase offset (`woff*doff[i]`, the decorrelated stereo wash). That decorrelation **is the point** of the stereo image — don't naively collapse it. There may be a cheaper way to derive R, but it's risky; the per-sample voice fix above is the bigger, safer win. Do that first, re-measure, then decide if this is even needed.

### Conventions
- No new sliders, no slider-ID changes (internal only) → existing projects open unchanged.
- Mind the eel2 case-insensitivity trap (CLAUDE.md): don't name the table var or any local a case-variant of a global it writes.
- CC0 / original implementation: a sine wavetable is bog-standard original work; nothing to copy.

---

## Deferred for separate planning

Mentioned in the design session but explicitly deferred to keep current scope manageable:

- **~~Start delay on other rhythm plugins~~ — LANDED.** Shepard Scale, Shepard Tone, Full Feature Tremolo, Full Feature Sweeping Filter, Sweep Dwell Filter, Heartbeat Generator, Breath Generator, Womb Sound Generator all gained a Start Delay slider at the end of their slider lists. Generators use "silence during delay" (no audio output), effects use "pass-through during delay" (dry signal flows through unchanged) so the effect plugins don't accidentally mute the dry track when chained. Same internal-state-freeze rule as the synth plugins: phases / filter buffers / LFO state don't advance during the silent window. **Units inherit each plugin's natural rate concept** — initially shipped as universal seconds, revised after user feedback ("not everyone is measuring things in seconds"): Heartbeat / Womb / Shepard Scale use beats at their respective BPM sliders; Shepard Tone / Full Feature Tremolo / Full Feature Sweeping Filter match their Rate Mode (BPM/Seconds/Hz) the same way polyrhythm and melody do; Breath Generator and Sweep Dwell Filter keep seconds because they're phase-based (each phase duration is already an explicit seconds slider, so beats/cycles would have no natural referent).

- **"Rest between voices" macro for Melody Phase** — a pan-mode-style global mode + per-voice increment for automatic rest distribution across voices. The existing per-voice "Note duration" + "Next voice in" sliders already cover the underlying mechanism (set Note duration < Next voice in to get silence between voices); the macro would be a shortcut for setting up uniform rest patterns without going voice-by-voice. Needs its own design pass — what modes, override semantics, etc.

- **Speed Ramp start delay — suite-wide sweep.** First implementation lives in `womb_sound_generator_v2.jsfx` (the v2 of Womb, see `feature/womb-v2`). Pattern is one extra slider in the Speed Ramp section: `Speed ramp start delay (minutes)`, range 0–60, step 0.1, default 0 (preserves current behavior — no delay). Sits beside the existing Speed Ramp engage / duration / target sliders. Implementation: when the Engage toggle flips on (the existing engage-edge detection block in each plugin), reset two counters. Each sample while Engage is on and the delay hasn't elapsed, increment `speed_ramp_delay_elapsed` against `speed_ramp_delay_samples = slider_value * 60 * srate` — Speed Ramp's `speed_ramp_t` stays frozen at 0 during this window. When `speed_ramp_delay_elapsed >= speed_ramp_delay_samples`, switch to the existing ramp loop (advance `speed_ramp_t` by `1.0 / (srate * slider_duration * 60)` per sample as before). Engage edge resets both counters. Disengage (turn Off) freezes both at their in-flight position, same as the current Speed Ramp freeze behavior. Default 0 makes the delay path a no-op so existing projects open identically. Touch the 10 other plugins that have Speed Ramp (Heartbeat, Breath, Tremolo, Sweeping Filter, Sweep Dwell, Rhythm Track, Melody Phase, Shepard Scale, Shepard Tone, Polyrhythm Phase) when the pattern has been validated by ear on Womb v2. One commit per plugin, mirroring the original Speed Ramp sweep's commit style.

---

## Conventions to honor while implementing

- **All new sliders added at END of each .jsfx file** — preserves user slider state on existing plugin instances per CLAUDE.md's "primary keys" rule.
- **New sliders will appear at the bottom of the plugin UI panel** as a result — accept this UX trade for the project-stability it buys.
- **Per-plugin Start delay** could be implementable as a small shared pattern if multiple plugins gain it later (the deferred ones included).
- **Bounce-variant labels** (Melody Phase Direction) read straight off the 6-option slider — no conditional hiding needed, the only invalid combinations are absent from the option list. Same principle as the collapsed Direction & Reverse slider on polyrhythm_phase.
- **Reverse Drift Offset** is visible in all modes including Forward (where it does nothing). Hiding it only when Direction = Forward is fine too if it feels cleaner during implementation — the existing `slider_show()` pattern handles the conditional cleanly.

---

## Harmonic Sculptor (captured 2026-07-01, live-jam session)

Two directions surfaced while playing the Sculptor live (via the kin_bridge live-control tool). Rozaya asked these be written down here rather than left as ephemeral task chips.

### 1. Note / semitone tuning (dyscalculia-accessibility)

Let the Fundamental be set by musical note, not only Hz. Currently `slider4 "Fundamental Hz"` (20–2000). Picking "A2" is far easier than dialing "110.00 Hz" — a direct fit for the dyscalculia sweep (never make the user produce a number; see `docs/dyscalculia-accessibility-sweep.md`).

- Borrow the proven pattern from `polyrhythm_phase.jsfx`: Base Note (C..B enum) + Center Octave + Tuning Reference Hz (default 440) deriving the frequency.
- Add new sliders at the END only (slider IDs are primary keys — never renumber). Add a Tuning mode toggle (Hz / Note), Base Note, Octave, Tuning Reference; `slider_show()` to hide the irrelevant set per mode. Keep the existing Fundamental Hz slider working so old projects don't break.

### 2. Vowel / formant mode (additive formant synthesis)

**Discovery this session:** the Sculptor, using ONLY its additive harmonics (resonance bank fully bypassed), produced a convincing, GENTLE vowel — "a nice relaxed ah" — by weighting harmonics that land near a voice's formants. Rozaya: "I didn't know we could get *this* with just harmonics or I would have put more effort into that plugin." This is notably gentler than the resonance-bank formant approach (no sharp resonant peaks, no drift-beating, no head-pressure), so it may be a better path for the voice / breathed-vowel goals than the real-time filter approaches that hit dead ends (Klatt / Pink-Trombone — see `archive/exploration/`).

Proven recipe (fundamental 165 Hz): base = pure Sine → set harmonics to a **−12 dB/oct** modal-voice rolloff (H_n = −12·log2(n): 0, −12, −19, −24, −28, −31, −34, −36…) → boost the harmonics nearest the target formants, and CUT the between-formant harmonics into deep valleys (the valleys carry vowel identity as much as the peaks). Peterson-Barney adult-male vowels: /ah/ F1 710 F2 1100 F3 2540; /ɔ oh/ 590 / 880; /u ooh/ 300 / 870; /i ee/ 270 / 2290 / 3010. A saw source (−6 dB/oct) is too bright/fatiguing.

**Ceiling hit live:** at a single low fundamental with sparse harmonics, ah↔ooh morphs read only as subtle tints, not clear vowel changes. The feature that breaks through:

- **Vowel selector** (ah/eh/ee/oh/oo…) that auto-weights the harmonics for the current fundamental — no hand-editing 64 levels.
- **Pitch-tracking formants** — the key one: recompute which harmonics to emphasize as the fundamental changes, so formants stay fixed in Hz across pitch. That's the difference between "synth" and "a voice that can sing different notes" (a real "ah" keeps its shape whether sung low or high).
- **Vowel-morph** control interpolating formant positions. An INTERNAL morph slider also sidesteps a limitation found this session: the plugin exposes only ONE "selected harmonic level" param externally, so nothing outside can move multiple harmonics simultaneously.
- Optional spectral-tilt control (−6 bright / −12 modal / −18 breathy) + breathy mode (filtered noise).
- Hook to load a REAL voice's measured harmonics (ties to `spectral_vowel_morpher.jsfx` live-capture + the proven vowel-harmonic-resynthesis workflow).

---

## Womb v3 — expand Drift + Speed Ramp target lists (captured 2026-07-01)

**Motivation.** Discovered while building the nervous-system-states journey (see `docs/womb-nervous-system-states.md` + memory `project-womb-nervous-system-states`): the built-in Drift and Speed Ramp only reach 7 targets (Heart BPM, S1-S2 gap, Inhale, Top pause, Exhale, Bottom pause, RSA depth), so **timbre can't evolve across the journey** using the plugin's own tools — you can slow the breath but not *darken* it, so a dysregulated→resting descent still needs external automation (`kin_render.lua`) for the timbre half. Rozaya's call: add far more targets so drift + ramp reach **everything adjustable**, making full journeys native and renderable with no external automation. "Is it a lot of targets? Yes. Is it worth it? Also yes."

**Cheap by design.** The nested-selector pattern means slider count stays at 5 per system (selector + up/down/period/shape for drift; selector + by/duration/engage/start-delay for ramp) no matter how many targets. Only the selector enum range `(0,N,1)` and the per-target memory banks grow. So this is almost entirely internal work, not new sliders.

**Proposed target additions (append to BOTH Drift and Speed Ramp, same list).** Keep existing indices 0-6 exactly as they are; **append new targets at the END** (7+) so existing project configs keep their meaning (same rule as slider IDs — never insert mid-list).

- *Heart timbre/level:* HB Master Volume, Brightness, S1 Frequency, S2 Frequency, S1 Decay, S2 Decay, HB Stereo Width (opt: S1 Vol, S2 Vol)
- *Breath timbre/level (the "breath brightness" ask):* Breath Volume, Inhale Frequency, Exhale Frequency, Breath High-pass, Breath Post-filter Hz, Breath Post-filter Q, Breath Stereo Width (opt: the 4 fades)
- *Bloodflow:* Bloodflow Volume, Bloodflow Filter Hz, Bloodflow Resonance, Bloodflow Dicrotic, Bloodflow Stereo Width (opt: BF Attack, BF Decay)

That's ~18 core additions (~25 targets total), more if the optionals go in.

**Implementation notes / gotchas (from CLAUDE.md):**
- **Version the `@serialize` stream.** Expanding the per-target memory banks changes how many values are serialized. MUST lead the stream with the count-encoded magic marker so old project blobs fall through to defaults instead of scrambling (see the `@serialize` gotcha in CLAUDE.md). This applies to BOTH the drift config bank and the speed-ramp per-target `by` bank.
- **Append-only target order** preserves existing (0-6) configs on load.
- Consumption sites: each new target's drift-offset / ramp-offset gets added at that parameter's use site (`effective_X = base + drift_offset[t] + speed_ramp_offset[t]`), same shape as the existing 7.
- Memory bank sizing: bump the per-field array spacing / bank base to fit ~25 targets (16-slot-aligned per field, plenty of room above 8192).
- Period units per target: rate-ish targets in cycles/beats; timbre targets can drift in their native unit over breath/heart cycles (document per target in the manual).
- Manual: update the Womb v3 Drift + Speed Ramp sections with the full target list.

**Payoff.** With this, the full dysregulated→activated-coherent→resting journey — heart rate, breath timing AND breath brightness, bloodflow, heart timbre, all of it — is a single armed Speed Ramp (or drift config) that plays live and renders offline, no `kin_render`/envelope step needed. It also removes the "automation-only" asterisk noted in `project-kin-bridge-reaper-live-control`.

---

## Spectral Vowel Morpher — more capture slots + slot randomization / patterns (captured 2026-07-01)

**Motivation.** Rozaya hit the 4-slot (`NSLOTS`) ceiling while working — captured several points from one source, layered a heartbeat under them, and is stacking duplicate tracks to keep the morph from getting repetitive. Wants more variation from ONE instance, plus an accessible way to sequence/randomize which capture plays.

### 1. More capture slots
`NSLOTS` is a constant (currently 4). Raising it to 8 or 16 costs only memory (16 slots = `NSLOTS*MAXFFT` = 16×32768 ≈ 524 k slots, well within the ~8 M default). `slider1` "Capture slot" range becomes 1–N.
- **Version the `@serialize` stream** (CLAUDE.md gotcha): the blob saves `NSLOTS*MAXFFT`, so changing `NSLOTS` changes its size. It already leads with a magic (`7700001`) — extend that to encode the slot count so an OLD 4-slot project loads its four into the first four slots instead of scrambling.
- Re-space the high-memory offsets that scale with `NSLOTS` (`slotmag`, `slotraw`, `slot_harm`, `slot_f0`, `slot_hnorm`, `slot_norm`) so they don't overlap at the larger count.

### 2. Random slot mode (probably the actual fix for "too repeat-y")
Add a **"Random"** option to Auto-morph (`slider15`, currently Off / Sweep / Glide once). On a clock (a rate slider), jump the shared `vsi`/`vsj` slot selection to a random slot instead of smoothly sweeping. 2–3 sliders total (mode + rate + optional smoothing/amount). Gives evolving variation from a single instance with **no pattern to type** — the accessible default, and likely what removes the need to stack tracks. Reuse the existing shared `vsi/vsj/vmfr` so voice + wash stay in agreement.

### 3. Slot patterns via a TEXT FILE (accessible arbitrary sequences)
**The accessibility wall (confirmed):** JSFX sliders are numeric / enum only — there is no text-string slider — and an `@gfx` text box has NO accessibility tree, so NVDA can't see it and it never appears in the parameter list. Typing a pattern *into the plugin* is off the table for a screen-reader user.
**The sideways fix — read the pattern from a `.txt` file.** JSFX can read text files (`file_open` + `file_string`), and a file-picker slider (`sliderN:/folder:default:Name`, the Sustain Looper idiom) IS NVDA-navigable.
- Pattern lives in a `.txt` (e.g. `1 3 2 4 1 1 3`) the user types in **Notepad** (fully accessible) and drops in a patterns folder.
- Plugin file-picks it; on change, read + parse the slot indices into an array; step through them on the clock (`0` = rest/hold).
- The user "types into a box" — just Notepad's, not the plugin's — sidestepping the string-slider wall entirely. Bonus: the kin_bridge can also inject a pattern live.

Same family as Polyrhythm Phase's per-voice sequencing. All three compose into a capture "sampler/sequencer," dyscalculia-clean: Random needs no numbers; the file-pattern is typed in an accessible editor, never dialed on a slider.
