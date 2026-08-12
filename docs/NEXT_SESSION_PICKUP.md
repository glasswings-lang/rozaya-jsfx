# Next session pickup notes — updated 2026-08-12

Living handoff notes. The Host x sweep is **done and largely ear-tested**. What
remains is a short list of unheard plugins and the two older Passage threads.

## Branch state

All on **`feature/host-tempo-sync`**, unmerged, ~30 commits ahead of `master`
(which is itself 4 ahead of `origin/master` — the whole 2026-07 run is
unpushed). Merge is a clean `--ff-only` whenever the remaining ear-tests pass.

Installed copies in `<REAPER resource>/Effects/glasswings/` are current.
**Originals are in `C:\Users\solst\pre-hostsinc`** — copy one back and rename
`<name>.jsfx.pre-hostsync.bak` to `<name>.jsfx` to revert a single plugin.

## What Host x is, in two parts

The word "sync" was doing two jobs all session, and separating them is the
thing to carry forward:

1. **Following the tempo.** Every ported plugin does this. The rate slider
   becomes a MULTIPLIER of the project tempo — deliberately, not a note grid,
   so any ratio survives a tempo change.
2. **Agreeing with the bar.** Only things that HAVE a bar to agree with get
   this: a metronome, a filter sweep, a melody. Drones don't.

## Confirmed by ear ✓

- `rhythm-track` — locks to REAPER's click, from the top and from a mid-song
  start.
- `sweep-dwell-filter` — cycle length, position lock, and the pan block
  (including the new `Host x` Pan Sweep Rate unit and the per-cycle modes
  riding the dwell cycle).
- **Host x landing** — switching mode selects "1 per beat" and hides the raw
  multiplier, across all twelve plugins with a picker.
- `melody_phase` — sequence placement from any position, every direction mode,
  Loop on and off, and the Play/Rest gate in both Walk and Freeze. Plus the
  first note firing normally in plain BPM mode (a regression that briefly
  killed it in every non-Host-x mode).

## NOT yet heard

- **`Full_Feature_Tremolo` and `full-feature-sweeping-filter`.** These carry
  the drift fix (drift on the rate was 60x too small in Host x — inaudible)
  and the position lock. Rozaya believes an earlier pass covered these, but
  that pass predates the drift fix, so the drift step specifically is unheard.
  Test: Drift target Rate Value, up 20, period 4 — the rate should audibly
  wander. "I can hear it moving" is the whole result.
- **`stereo-phaser`** — position lock, never heard.
- **`shepard-scale`** — sequence placement, never heard. Note the Skip-mode
  walk: with inactive notes, "40 beats in" is not note 40.
- **`melody_phase_v2`** — got every change v1 did, but v1 is what was tested.
- Everything else in the sweep is a rate-follow only and lower risk.

## Rules the session settled, worth not re-deriving

- **Drift and Speed Ramp amounts are BPM in every mode, Host x included.** The
  plugin converts (D BPM = D/tempo in multiplier terms); the user never does.
  Tried the multiplier form twice and it fails: at 0.1 slider steps the value
  you want isn't reachable, and where the step is fine it still forces
  arithmetic to hit a musical destination.
- **Lock what's constant, accumulate what's modulated.** Position-locking
  answers "where would this be if it had run at this rate all along", which
  stops being the right question the moment drift or a ramp moves the rate.
- **Effects lock per sample; sequencers place once.** A sequencer that
  recomputed its position constantly would jump mid-note.
- **Before changing a control's units, ask what the user holds in their head
  when setting it** — a figure they know (5 BPM of HRV) or a feel they're
  dialling for. Neither the code nor the label can tell you.

## Older threads — BOTH CLOSED 2026-08-12

- **Passage fade curves — passed.** Cosine default, tested against Linear.
  Installed copy verified byte-identical to source first, so it was genuinely
  the current build being heard.
- **Passage short-grain crackle — GONE.** Tested at Wash grain **5** with Wash
  at **100**, i.e. the worst case the plugin offers: no crackle. This thread
  had been open since 25 July.

  **Nobody fixed it deliberately, and that's the lesson.** It was last
  confirmed present on 07-25. Three things landed on 07-27 while chasing a
  different bug (the click at slot handoffs): the voice phase handover,
  `flush_accum_pending` replacing a 131072-slot clear performed inside a single
  sample, and moving the harmonic phase advance inside the audibility guard —
  which also stopped an out-of-range read past the end of the sine table.
  Any of those could plausibly do it; the table overrun is the best candidate,
  since it produces actual wrong samples rather than merely load.

  Nobody re-tested the crackle after 07-27, so it sat on the books as an open
  mystery for two weeks while probably already being fixed.

  **Carry forward: when a fix lands near an open bug, re-test the open bug.**
  The cost of the check is a minute; the cost of not checking was two weeks of
  a false open thread, and a diagnostic plan written for a problem that no
  longer existed.
