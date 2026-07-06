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

### 1. More capture slots — DONE 2026-07-05 (`NSLOTS` now 8)
`NSLOTS` raised 4 → 8; `slider1` "Capture slot" range is now 1–8. Two things landed with it:
- **Memory map re-laid as a running allocator** (`freemem = 0; buf = freemem; freemem += size;`) instead of hand-picked addresses. The old fixed offsets collided the moment `NSLOTS` went past 4 (`slotraw` ran straight into `slot_norm`). Now every buffer derives from the constants, so the slot count is a free one-number dial — raise `NSLOTS` again anytime, no address surgery.
- **`@serialize` change turned out simpler than the versioning sketch below.** Instead of encoding the slot count into the magic, it now saves/restores `n_used*MAXFFT` (only the slots actually captured) rather than the full `NSLOTS*MAXFFT`. This is inherently backward-compatible: an old 4-slot save wrote the full block but `n_used` always told the truth about how many were real, and slots are stored contiguously from slot 0 — so reading `n_used*MAXFFT` restores exactly the real captures and never scrambles, at any `NSLOTS`. Bonus: project files no longer carry empty tail slots.
- **Bundled the play-start crackle fix** (unrelated to slot count but same file): the play-edge used to re-analyze *every* slot on *every* transport start — N heavy FFT+YIN passes crammed into one block. Now re-analysis is (a) conditional on the analysis actually being stale (normal capture-then-play does zero re-derive) and (b) de-spiked across blocks (one slot per block) when it is needed. This also stopped the crackle from getting *worse* as slot count rose.

### 2. Random motion — split into two, only ONE of which is safe for this user's music

The original "random slot mode" idea turned out to be two different things, and the 2026-07-05 design conversation with Rozaya separated them:

**2a. Drift (smooth random walk of the morph POSITION) — DONE 2026-07-05.** Added as a 4th Auto-morph mode (`slider15` now `{Off,Sweep,Glide once,Drift (random)}`). It eases the morph position toward a random target at the Auto-morph time rate, and on arrival picks a new target — an unrepeating organic wander. Crucially it only moves *where* the morph sits, so it only ever blends the two neighbouring captures, exactly like sliding Morph by hand. **Clash-safe by construction**, including on chordal captures. Reused the existing `auto_time` slider for pace (no new sliders). `drift_target` state; re-seeded on mode entry.

**2b. Scatter (per-grain random SLOT pick in the wash) — RULED OUT for Rozaya's material.** The idea was: each wash grain pulls from a random captured slot, blooming the bed into a cloud of all captures at once. **This does not work for her music and won't be built for it.** Why: (i) the wash is *not* pitchless — it retains each capture's pitch in the shape of the frozen magnitude spectrum (the peak spacing), which is exactly why cranking Texture to wash still yields a *voice*. (ii) Rozaya's captures are **chords at different pitches** (she works chordally, and the harmonic/voice engine is monophonic — single-f0 YIN detect — so the wash is the only engine that preserves a chord at all). So scattering random captures = stacking different chords at different pitches = dissonant mud, not density. (iii) The "pitch-lock the scattered grains" rescue **cannot apply to chords** — there is no single pitch to lock; re-pitching would transpose whole chords around. Scatter would only be safe for *same-pitch, monophonic* captures, which is not this user. Left here as a documented dead-end so it isn't re-proposed.

**Clash-proof density (the real future path, if wanted): thicken IN PLACE.** More body from the capture you're *already on* — increased grain overlap, wider stereo decorrelation, subtle detuned layers of the *same* spectrum. Cannot clash because it never introduces a foreign capture/chord. This is the direction to take "fuller from one instance" for chordal work; not yet built. (Pairs with the separate mono-voice / de-robot detune fix noted below.)

**Also surfaced 2026-07-05 — the harmonic (voice) engine is MONO.** `hV` is summed identically into L and R; `stereo_width` only ever touches the wash (via `build_spectrum`'s `useR` phase-decorrelation). So the voice is dead-center at any Stereo width. Fix = detuned stereo unison (the project's own sanctioned width method — see CLAUDE.md "no static phase offset > 90°"), which doubles as a de-robotizer (pure additive harmonics sound robotic *because* they're clean/static/centered). Not yet built; would make the voice end usable instead of something to flee via full-wash.

### 3. Slot patterns via a TEXT FILE (accessible arbitrary sequences)
**Caveat added 2026-07-05:** same chord/clash limit as 2b applies — stepping a pattern between captures at *different pitches* stacks/juxtaposes different chords. Fine as *sequential* motion (like Drift/Glide, one capture at a time), NOT as simultaneous blend. The accessible-pattern mechanism itself is still sound; just frame it as sequencing the morph *target*, not layering slots.
**The accessibility wall (confirmed):** JSFX sliders are numeric / enum only — there is no text-string slider — and an `@gfx` text box has NO accessibility tree, so NVDA can't see it and it never appears in the parameter list. Typing a pattern *into the plugin* is off the table for a screen-reader user.
**The sideways fix — read the pattern from a `.txt` file.** JSFX can read text files (`file_open` + `file_string`), and a file-picker slider (`sliderN:/folder:default:Name`, the Sustain Looper idiom) IS NVDA-navigable.
- Pattern lives in a `.txt` (e.g. `1 3 2 4 1 1 3`) the user types in **Notepad** (fully accessible) and drops in a patterns folder.
- Plugin file-picks it; on change, read + parse the slot indices into an array; step through them on the clock (`0` = rest/hold).
- The user "types into a box" — just Notepad's, not the plugin's — sidestepping the string-slider wall entirely. Bonus: the kin_bridge can also inject a pattern live.

Same family as Polyrhythm Phase's per-voice sequencing. All three compose into a capture "sampler/sequencer," dyscalculia-clean: Random needs no numbers; the file-pattern is typed in an accessible editor, never dialed on a slider.

---

## Automation-replacement sweep — Drift + Speed Ramp reach *everything adjustable* (captured 2026-07-02)

**Why this exists.** Drift + Speed Ramp are the in-plugin substitute for REAPER automation — Rozaya is blind and can't drive automation envelopes through OSARA (see `project-kin-bridge-reaper-live-control`). The test that names this sweep: *"will this replace automation?"* — for every plugin, can Drift (repeating wander) + Speed Ramp (one-time ride) reach every parameter you'd realistically want to move over the course of a piece? Today the answer is **no** in three specific ways. Trigger: building a real session, Rozaya wanted **breaths-per-minute** as a Drift *and* Speed Ramp target in Womb v3 and it wasn't there — you can ramp the four breath segments individually but not the breath *rate* as one felt control.

**The audit (2026-07-02).** Current target coverage across the suite:

| Plugin | Drift targets | Speed Ramp targets | Gap |
|---|---|---|---|
| Womb v3 | 7 | 7 | timbre (already spec'd above, "Womb v3 — expand Drift + Speed Ramp target lists"); **no breaths-per-minute aggregate** |
| Breath Gen | 4 segments | 4 segments | **no breaths-per-minute aggregate**; no breath timbre (vol / filter) |
| Heartbeat | 4 | 4 | no heart timbre (S1/S2 freq·decay, vol, width) |
| Rhythm Track | 2 (Tempo, Swing) | **1 (BPM only)** | Speed Ramp missing Swing |
| Shepard Scale | 4 | **1 (BPM only)** | Speed Ramp missing Note Len / Attack / Release |
| Shepard Tone | 11 | **1 (Rate only)** | Speed Ramp missing 10 |
| Full Feature Tremolo | 6 | **1 (Rate only)** | Speed Ramp missing 5 |
| Full Feature Sweeping Filter | 6 | **1 (Rate only)** | Speed Ramp missing 5 (Freq Low/High, Reso, Wet/Dry, Pan) |
| Sweep Dwell Filter | 6 | 4 | Speed Ramp missing Pan Sweep Rate, Resonance |
| Polyrhythm Phase | 24 | 24 | parity ✓ |
| Melody Phase | 28 | **1 (Rate only)** | Speed Ramp missing 27 |
| Resonance Bank | 5 (per band) | **none** | no Speed Ramp at all |

Root cause of the biggest column of gaps: the **2026-06-12 nested-selector drift sweep** upgraded every plugin's *Drift* to multi-target, but *Speed Ramp* was mostly left at the single-target shape from the earlier (2026-05-30) Speed Ramp sweep. So on 6 plugins you can *wander* a parameter but can't *ride it down once* — and the one-time ride is the wind-down move that most directly replaces an automation envelope.

### Three jobs

**Job A — Speed Ramp → Drift parity (the bulk of the win, lowest risk).**
Port the nested-selector pattern to Speed Ramp on the 6 single-target plugins (Melody, Shepard Tone, Shepard Scale, Tremolo, Sweeping Filter, Rhythm Track), and give Resonance Bank a Speed Ramp for the first time. Reuse each plugin's *existing Drift target list verbatim* — Drift already proved the per-target consumption math and the additive-vs-ratio audio-path split (CLAUDE.md, drift sweep banner), so Speed Ramp just needs the same target enum, a per-target `by` memory bank, and the offset folded in at the same consumption sites Drift already uses. This is mechanical and category-tested.
- **Slider shape per plugin (matches Womb v3):** `Speed ramp target` (selector, enum range `(0,N,1)` = Drift's list) + `Speed ramp by` (signed delta, units match target) + `Speed ramp duration (minutes)` + `Speed ramp engage {Off,On}` + `Speed ramp start delay (minutes)`. Where a single-target Speed Ramp already has some of these, keep the IDs and only *add* the selector + per-target bank (slider IDs are primary keys — never renumber; append the selector at the end).
- **Resonance Bank** is the one that gains the whole 5-slider block from scratch, per-band like its Drift (outer band selector already exists; Speed Ramp's target selector is the inner one, same nesting as Drift).
- **Engage = freeze/resume gate, transport-only restart** — the settled semantics from the suite Speed Ramp sweep. No engage-edge detection.

**Job B — breaths-per-minute aggregate target (the trigger; a new *kind* of target).**
Breath rate isn't one slider — it's the four segment durations (Inhale, Top pause, Exhale, Bottom pause). A breaths-per-minute Drift/Ramp target is a **proportional multiplier across all four segments in lockstep**, preserving I:E ratios — *exactly the sigh-mechanism math Womb v3 already ships*, and the same category as Polyrhythm's "Base Rate" (one control scaling all 8 voices via an internal ratio). So it's a **ratio-based aggregate**, precedent-backed.
- **Append** it to both the Drift and Speed Ramp target lists (index 7+ on Womb v3, index 4+ on Breath Gen) — never insert mid-list (preserves existing per-index configs on load).
- Sits *alongside* the individual-segment targets, not replacing them: you can ramp the whole breath rate down **and** drift one segment independently. They compose at the consumption site.
- **Consumption math:** the target produces a breath-rate scale `s` (from the signed BPM delta → ratio, like polyrhythm/melody's ratio targets). Each segment's effective duration becomes `(base_segment + per-segment_drift_offset) / s` (longer period = slower rate). Compose with sigh multiplier and any Speed Ramp on the same target the usual way.
- **UX:** "Speed ramp by −4 breaths/min," signed delta in the natural unit. In BPM-style terms negative = slower (intuitive), matching the suite's mode-direction convention. Distinct from the existing one-way **Breaths per minute rescale slider** (which stays as-is — it's a setup tool that rescales the four sliders once; the new target is live modulation of the rate). Document the two side by side so they don't read as duplicates.
- Applies to **Womb v3 and Breath Generator** (both have the four-segment breath model). Heartbeat has no breath segments — n/a there.

**Job C — timbre / level targets.**
So a dysregulated→resting descent can *darken* natively, not just slow down — removes the `kin_render.lua` asterisk (see `project-womb-nervous-system-states`, `project-kin-bridge-reaper-live-control`).
- **Womb v3** — already fully spec'd above under "Womb v3 — expand Drift + Speed Ramp target lists" (~18 core timbre additions across heart / breath / bloodflow). Fold that entry into this sweep; do it in the same Womb pass as Job B.
- **Heartbeat Generator** — the standalone-sibling equivalent: S1/S2 frequency, S1/S2 decay, HB master volume, stereo width (mirror whatever Womb's heart layer exposes).
- **Breath Generator** — breath volume + breath filter params, mirroring Womb's breath-timbre set.
- Effects (Tremolo / Sweeping Filter / Sweep Dwell / Resonance Bank) largely already expose their "timbre" params (filter freq, resonance, depth, wet/dry) *as Drift targets* — Job A brings those to Speed Ramp automatically. Check each for any adjustable param still absent from both lists and append if a real use case wants it.

### Proposed ordering

1. **Womb v3 + Breath Generator** — breaths-per-minute aggregate (Job B) on both, plus Womb timbre (Job C, already spec'd), plus Breath timbre. Closes the exact wall Rozaya hit. *(Rozaya's chosen order: write this plan first, then do "the easy part" — so the mechanical Job A batch may actually run before or interleaved with this; confirm at start of the coding session.)*
2. **Speed Ramp → multi-target parity (Job A)** across Melody, Shepard Tone, Shepard Scale, Tremolo, Sweeping Filter, Rhythm Track; + Resonance Bank gains Speed Ramp. The mechanical, highest-hole-count batch.
3. **Heartbeat timbre targets (Job C tail).**

### Conventions / gotchas that bite this specific sweep

- **Version the `@serialize` stream on EVERY plugin touched.** Both the per-target Drift bank *and* the new per-target Speed Ramp `by` bank change size here. Lead each with the count-encoded magic marker so old project blobs fall through to defaults instead of scrambling (CLAUDE.md `@serialize` gotcha — this is the highest-risk part of the sweep). A mismatched blob fabricates phantom drift/ramp the user never configured.
- **Append-only target order** on Womb v3 / Breath Gen (and anywhere a list grows) — existing indices keep their meaning on load. New targets go at the end of the enum.
- **Layout convention (DECIDED 2026-07-02, Rozaya's call): selector-first, renumber accepted.** The Speed Ramp *target selector* must read ABOVE the by/duration/engage controls it governs — in the plugin UI and, critically, in NVDA's parameter-list order (a selector that comes *after* the value it governs is confusing to navigate by ear). REAPER orders sliders by ID, not file position, so achieving this means **renumbering** the Speed Ramp (and usually the adjacent Drift) block into a clean contiguous group with the selector at the lowest ID. This overrides the usual "append at END / never renumber" habit **for this sweep only** — it's a deliberate, one-time, release-boundary renumber, not an accidental mid-list insert. Cost per plugin: existing projects reset their Speed Ramp + Drift configs on upgrade (both off-by-default; the plugin's *sound* sliders are untouched). The `@serialize` version-guard already forces a drift reset anyway, so the marginal cost is small. Standard fix for users: re-add the instance for clean defaults. Document the renumber in each plugin's manual migration note. *(Prior habit, now superseded for this sweep: "add the selector at the END, don't renumber" — that produced the bad NVDA order Rozaya flagged on Rhythm Track.)*
- **Additive vs ratio audio-path split** carries over from the drift sweep unchanged: rate targets in ratio-path plugins (Shepard Tone, Tremolo, Sweeping Filter, Melody, Polyrhythm, and the new breaths-per-minute aggregate) convert the additive `by` to an internal multiplicative ratio; additive-on-value targets add in native units at the use site.
- **Nested-selector save/restore** in `@slider`: on selector change, save current visible slider values into the OLD target's bank slot, then load the NEW target's — the well-tested Womb v3 / Resonance Bank pattern. All targets ramp/drift in parallel; the selector only chooses which one is being *edited*, never which one is *running* (the bug Rozaya caught in Womb v3 — switching the selector must not stop a running ramp).
- **Cheap by design:** slider count stays at 5 per system (selector + 4) regardless of target count. Only the enum range and per-target memory banks grow. So this is almost entirely internal work, few new sliders.
- **Manual:** update each plugin's Drift + Speed Ramp target lists in `docs/rozaya_jsfx_manual.md`; document breaths-per-minute vs the one-way rescale slider explicitly.

### Progress log (this is the sweep's running changelog; user-facing notes go in the v2.14 GitHub release when cut)

- **Melody Speed Ramp → multi-target (Job A tail) — DONE, ear-tested ✓, committed `ac7f125` (2026-07-02).** Closes Job A: Melody's Speed Ramp went single-target (Rate Value only, old sliders 67–70) → nested-selector reaching all 28 Drift targets, per-target timelines (`by` + duration + start-delay per target, engage global), selector-first renumber (Speed Ramp 67–71, Drift shifted 72–76), `@serialize` version-guard bumped 1000000→2100000+N_TARGETS (adds the SR banks; old drift-only + legacy blobs fall through to defaults), and the track-duplicate force block extended to both selectors. The "most intricate conversion" turned out clean: the note-trigger-vs-per-sample split falls out for free because each target's live offset (`speed_ramp_ramp_t_mem[t]*speed_ramp_by_mem[t]`) is *read* at the same site as the matching drift offset — continuous targets (Rate Value ratio-path, per-voice Timing, Pan Rate, per-voice Gain) read per-sample; articulation targets (Note dur, Attack %, Release %) read inside `trigger_seq_voice` (once per note), exactly mirroring Melody's drift. Manual updated (Speed Ramp section rewritten multi-target, Drift renumber notes). Ear-tested by Rozaya live via kin_bridge (note-duration + timing targets; survives track-duplicate). **Ships in v2.14.**

- **Job B — breaths-per-minute aggregate target — DONE on Womb v3 (`bceeaed`) + Breath Gen (`7eb058b`), ear-tested ✓ (2026-07-02).** The trigger that named the sweep. New ratio-based aggregate target appended to BOTH Drift and Speed Ramp lists: Womb v3 index 7 (N_TARGETS 7→8), Breath Gen index 4 (N_TARGETS 4→5, N_SPEED_TARGETS 4→5). It scales all four breath segments in lockstep, preserving I:E ratio — consumption is a `breath_rate_scale` derived from `base_rate_bpm + (drift_offset[bpm] + speed_ramp_bpm_offset)`, dividing each effective segment duration (composes with the per-segment drift + ramp offsets). Both plugins: fixed the hardcoded `loop(7)`/`loop(4)` SR init/advance loops to `loop(N_TARGETS)`/`N_SPEED_TARGETS`, added the per-target SR offset extraction, bumped the enum ranges + labels, and the `@serialize` magic (`2100000+N_TARGETS`) auto-bumps so old configs reset. Kept the one-way "Breaths per minute" setup rescale slider (Womb 53) as-is and documented the two side by side (setup-rewrite vs live-modulation). Manual updated on both. Heartbeat n/a (no breath segments). Ear-tested by Rozaya live via kin_bridge (aggregate drift wander + aggregate wind-down ramp on both; plus a per-segment regression on Breath and a Heart-BPM regression on Womb — existing targets unbroken, heart layer unaffected by the breath aggregate). **Ships in v2.14.**
  - **Doc-bug fixes bundled (2026-07-02, audit-caught, committed separately as `docs:`):** a manual-vs-code audit across all 12 sweep plugins (one read-only agent per plugin) found 9 fully in sync and 3 with drift — Womb v3 overview/architecture prose still said "7 targets" (fixed with the Womb commit), Heartbeat's Speed-Ramp intro + migration note still named retired sliders 17/20 (code is 29/30), and Breath's Top/Bottom Pause defaults were wrong (0.5/1.5 vs code 0.3/0.3). Heartbeat + Breath-default fixes are doc-only, committed as a `docs:` fix.
  - **Job C — timbre/level targets — STARTED (breath frequencies slice DONE + ear-tested, 2026-07-02).** Womb v3 gained **Inhale Freq + Exhale Freq** as Drift + Speed Ramp targets (indices 8, 9; N_TARGETS 8→10) — the breath-noise filter cutoffs, i.e. the breath's brightness, so it can wander or darken/brighten over time natively. Consumption recomputes the cached in_f/ex_f filter coeffs per-sample from base+drift+ramp, gated by a `breath_freq_active` flag so unused instances pay nothing. Also **widened the shared drift up/down range 0-50→0-2000 and the Speed Ramp `by` range ±300→±2000** (Rozaya: "make the frequencies bigger") so the Hz-scale targets have real room — accepted tradeoff: coarser slider for the small-value targets. Ear-tested live via kin_bridge (big Inhale Freq drift sweep + a −200 Hz Inhale Freq darkening ramp); Exhale Freq is the untested mirror (identical code path). **STILL OPEN in Job C:** Womb heart/bloodflow timbre + breath vol/filter (the rest of the ~18); Heartbeat S1/S2 freq·decay + vol + width; Breath Gen vol + filter (+ the Inhale/Exhale Freq targets could mirror onto Breath Gen).
  - **STILL OPEN after this batch:** (a) rest of **Job C** (see the line above); (b) ear-tests — **ALL sweep plugins are now ear-tested** (Rozaya confirmed 2026-07-02: the earlier-batch plugins were heard in prior sessions, and Melody + Breath + Womb v3 were driven live via kin_bridge this session — drift wander + Speed-Ramp wind-down + a regression each; Melody survives track-duplicate; the log's earlier "untested-7" was just never updated); (c) merge to master + tag v2.14 + `gh release`.

- **Rhythm Track — DONE, ear-tested ✓ (2026-07-02, uncommitted).** Job A. Speed Ramp went single-target (Tempo BPM) → nested-selector reaching both Drift targets (Tempo BPM + Swing amount). Added per-target `speed_ramp_by_mem` bank + nested-selector save/restore; per-target offsets applied at the tempo and swing consumption sites; `@serialize` given a version-guard magic (`2000000 + N_TARGETS`) — it previously had none, so this also closes a pre-existing scramble gap. **Reorganized + renumbered per the selector-first convention above:** Speed Ramp is now sliders 17–21 (target / by / duration / engage / start-delay), Drift is 22–26 (target / up / down / period / shape). Both ramps confirmed working by ear (Tempo + Swing, parallel, selector-switch doesn't stop a running ramp). Manual updated (new slider numbers, migration note, and a swing-unit clarification — see next line). **Ships in v2.14.**
  - *Swing-unit clarity fix (same pass):* Rozaya flagged that "Speed ramp by … units match target" was meaningless when the target is Swing (a bare ±300 range with no felt referent). Not a gap in her knowledge — a labeling gap on our side. The Swing target's `by`/up/down are in the same **swing fraction** as the base Swing slider (−1…+1; 0 = straight, ±1 = full triplet shuffle; grounded in REAPER's −100…+100% swing convention). Manual now spells this out for both the Speed Ramp and Drift Swing target. (Candidate for the dyscalculia sweep later: express Swing in felt/percentage terms rather than a bare −1…1 number.)

- **Shepard Scale — DONE, ear-tested ✓ (2026-07-02, committed).** Job A, additive plugin (same shape as Rhythm Track). Speed Ramp single-target (BPM) → nested-selector reaching all 4 Drift targets (BPM, Note Length %, Attack %, Release %). Per-target `speed_ramp_by_mem` bank + nested-selector save/restore; offsets applied additively at all 4 consumption sites; `@serialize` version-guarded (`2000000 + N_TARGETS`; previously had none). Selector-first reorg + renumber: Speed Ramp now 52–56, Drift now 57–61. Rozaya ear-tested BPM + Attack + Release together (green); Note Length % left as a low-risk sanity check (structurally identical to Attack/Release). **Ships in v2.14.**

- **Shepard Tone — DONE, ear-tested ✓ (2026-07-02, uncommitted at write time).** Job A, FIRST ratio-path plugin (validated the pattern for the rest). Speed Ramp single-target (Rate Value) → nested-selector reaching all 11 Drift targets (Rate Value, V1–V8 Rate, Fade In %, Fade Out %). Key ratio-path techniques, all ear-confirmed: **(1)** rate targets add the `by` in the native unit BEFORE `rate_to_hz`, so BPM/Hz-vs-Seconds mode-direction is handled for free (Rozaya confirmed Seconds-mode positive-`by`=slower); **(2)** per-voice ramp folds into the same `voff` the per-voice drift uses → identical `rate_to_hz` ratio path (confirmed one voice peeling away); **(3)** Rate Value ramp still flows through `speed_scale_current`→`combined_scale`, unchanged audio path, just reads `by` from the bank. `speed_ramp_by_mem` at 704; `@serialize` version-guarded. Selector-first reorg: Speed Ramp now 64–68, Drift now 69–73. **Ships in v2.14. This is the reference implementation for the remaining ratio-path plugins (Tremolo, Sweeping Filter, Melody).**
  - *Correction to the audit:* **Polyrhythm Phase already has multi-target Speed Ramp parity** (24 targets on both Drift and Speed Ramp — done in an earlier session). So it does NOT need the Job A port. Its only open item is the *optional* selector-first reorg (its Speed ramp target is slider79, appended after the drift block — same bad NVDA order the reorg fixes). Renumbering Polyrhythm is higher-cost (most-used plugin, most state), so treat it as a separate decision, not part of the mechanical batch.

- **Heartbeat + Breath — per-target timelines + duplicate fix DONE (2026-07-02, committed, NOT yet ear-tested).** Both are Path A with their own SR var names (`speed_ramp_target_value_mem` / `last_speed_target`) and previously **unversioned** `@serialize` — so each got a NEW version guard (magic `2100000 + N_TARGETS`) plus the read-mode duplicate-fix force block, alongside the per-target timeline banks (dur/delay/ramp_t/delay_elapsed at 4240–4303, after the existing SR bank @4096 + drift @4112). Slider layouts kept as-is (target 17, duration 18, engage 19, by 20, start-delay 28/29 — NOT selector-first-contiguous, but functional; not worth a renumber). Also shepard-tone per-voice targets relabelled "Vn Rate/Cents".
  - **GAP FLAGGED (2026-07-02, Rozaya): Melody's Speed Ramp is still SINGLE-TARGET (Rate Value only) — it never got the Job A multi-target treatment.** When Melody came up in the rollout it was scoped as "duplicate-fix only" (its 28-target *drift* got the fix), but its Speed Ramp was left single-target, so it has no Speed-ramp-target selector while every sibling does — Rozaya noticed the missing slider. NEXT-SESSION WORK: give Melody's Speed Ramp the nested-selector multi-target treatment to match its 28 drift targets. It's the most intricate conversion in the suite — the per-note **articulation** targets (Note duration, Attack %, Release %) need the ramp offset sampled AT NOTE-TRIGGER (not per-sample), exactly mirroring how Melody's drift already samples those once per note; the continuous targets (Rate Value ratio-path, per-voice Gain, Pan Rate, per-voice Timing) ramp per-sample. Pair it with per-target timeline + the reorg conventions. Womb v3 ear-tested ✓ by Rozaya (per-target timelines pass).
  - **ALL REMAINING PLUGINS DONE (2026-07-02, committed, NOT yet ear-tested).** Sweep-Dwell, Womb v3, Polyrhythm got per-target timelines + duplicate fix; Melody + Resonance Bank got the duplicate fix on their drift selector(s). Every nested-selector plugin in the suite now has the track-duplicate fix, and every multi-target Speed Ramp is per-target-timeline. Remaining: (a) ear-test the 7 untested plugins (heartbeat, breath, sweep-dwell, womb v3, polyrhythm, melody, resonance bank) via copy→Ctrl+R; (b) **breaths-per-minute as a drift/ramp TARGET (Job B)** — still not built (Womb v3 + Breath Gen); (c) then merge to master + tag v2.14 + `gh release`.
  - **(historical) REMAINING per-target-timeline + duplicate-fix plugins:** **Sweep-Dwell** (Path A, likely same speed_ramp_target_value_mem shape as heartbeat/breath — 4 SR targets {High dwell, Fade down, Low dwell, Fade up}, drift has 6; note SR targets ⊂ drift targets so SR bank is smaller), **Womb v3** (7 SR + 7 drift; check `ext_noinit` — if set, runtime ramp-clock reset must go in its transport-edge block, NOT @init; also has the sigh mechanism + is where breaths-per-minute Job B lands), **Polyrhythm** (24 SR + 24 drift, `combined_scale`/ratio-path per-voice; check ext_noinit; biggest). **Duplicate-fix-only (drift selectors):** **Melody** (28 drift targets, single-target SR so no timeline needed — just version-guard its @serialize if not already + drift force block; melody's @serialize WAS versioned in the v2.9 sweep, confirm), **Resonance Bank** (`ext_noinit`, per-BAND nested drift = TWO nested selectors (band + drift-target); the force block must restore the visible config for the selected band AND its selected drift target — more care).
  - **Pattern reference:** the five committed sweep plugins + heartbeat/breath. Each conversion = (1) replace global `speed_ramp_t`/`speed_ramp_delay_elapsed` with per-target banks; (2) @init seed dur/delay (guarded) + reset ramp_t/delay_elapsed (runtime — @init for Path A, transport-edge block for ext_noinit); (3) @slider selector saves/loads by+duration+start-delay; (4) @sample per-target advance loop gated by global engage, consumption uses `ramp_t_mem[t]*by[t]`; (5) @serialize version-guard bump to `2100000+N_TARGETS` + duration/delay banks + read-mode force block. Test each: independent timelines from one engage + duplicate-survives, via copy→Ctrl+R (REAPER loads from `AppData/Roaming/REAPER/Effects/glasswings/` — plain copies, NOT linked to git; junction offered but not yet set up).

- **Sweep plugins finalized — Rhythm Track + Tremolo + Sweeping Filter, per-target timelines + duplicate fix (2026-07-02).** Rhythm Track got the per-target timeline added to its already-committed multi-target Speed Ramp. Tremolo + Sweeping Filter got their FIRST commit — the full package in one: multi-target Speed Ramp parity, selector-first reorg, track-duplicate fix, and per-target timelines. Tremolo ear-tested by Rozaya (Depth + Rate on independent timers, start delay staggering each independently ✓); the other two mirror the identical validated machinery. **Job A is now complete for all five sweep plugins.** Remaining: pre-existing multi-target Speed Ramp plugins (Womb v3, Heartbeat, Breath, Sweep-Dwell, Polyrhythm) need per-target timeline + duplicate fix; Melody + Resonance Bank need the duplicate fix on their drift selectors.

- **Per-target Speed Ramp TIMELINES — DONE on Shepard Scale + Shepard Tone, tested ✓ (2026-07-02).** Rozaya found the Speed Ramp `duration` (and start delay) was GLOBAL — one clock drove all targets, so you couldn't wind different targets down over different timelines. That defeats the automation-replacement goal (real automation lets each parameter move on its own schedule). **Fix (her spec: "both, and yes"):** `by`, `duration`, AND `start delay` are all now per-target (nested under the selector, saved/loaded like `by`); each target gets its own progress clock (`speed_ramp_ramp_t_mem`) and delay counter; **`engage` stays global** (one switch arms the whole wind-down, each target then rides its own duration after its own delay). Replaces the single global `speed_ramp_t` / `speed_ramp_delay_elapsed` with per-target banks. `@serialize` magic bumped `2000000` → `2100000 + N_TARGETS` (added duration + start-delay banks); duplicate-fix force block extended to duration + start delay. Validated on Shepard Scale (additive, clearest to hear — all 5 checks incl. independent timelines, selector-carries-all-three, duplicate-survives). Shepard Tone has identical machinery. **This is now part of the standard multi-target Speed Ramp pattern — every plugin in the rollout gets per-target timeline + the duplicate fix together.**

- **Track-duplicate bug in the nested-selector pattern — FOUND + FIXED (2026-07-02, ear/duplicate-tested ✓ on Shepard Tone).** Rozaya found that duplicating a track ZEROES whichever target the Speed Ramp had selected on the copy (non-selected targets survive). Root cause + fix are now a CLAUDE.md gotcha ("The nested-selector pattern … silently ZEROES the selected target on track duplicate"). Short version: slider values and `@serialize` memory restore via two independent paths in unguaranteed order, and on duplicate `@init` may not re-run; `@slider`'s load-branch clobbers the selected slider (→0) while the bank is momentarily empty, and `slider_automate` makes it stick. Fixes tried and rejected: `@init` flag (never runs on duplicate), adopt-on-first-`@slider` (consumed by an early pre-restore `@slider`). **The working fix:** in `@serialize`, on read (`file_avail(0) >= 0`), after restoring the banks, force the visible config sliders back to `bank[selected]` for each nested selector and call `sliderchange(-1)`. `@serialize` is the only section guaranteed to run on both load and duplicate, so it's authoritative. **Applied to:** shepard-tone (reference, tested), shepard-scale, rhythm-track, Full_Feature_Tremolo, full-feature-sweeping-filter (both their Speed Ramp *and* Drift selectors, in one `file_avail` block). **STILL TO DO — pre-existing latent bug in every OTHER nested-selector plugin's Drift (shipped since v2.9) + Polyrhythm/Womb v3/Heartbeat/Breath/Sweep-Dwell multi-target Speed Ramp + Resonance Bank's per-band nested drift:** breath_gen, heartbeat, sweep-dwell-filter, womb_sound_generator_v3, melody_phase (drift only — its SR is single-target), polyrhythm_phase, resonance_bank. Same one-block fix per plugin; resonance_bank's per-band nesting needs care (the visible config depends on BOTH the band selector and the inner drift-target selector).

**Cadence:** one commit per plugin (manual section bundled), ear-tested by Rozaya before/at commit — the same rhythm as the drift and Speed Ramp sweeps. Not tagged/released until the whole sweep is ear-validated.
