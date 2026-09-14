"""suite_status_test.py -- does suite_status still say what the plugins say?

  python tools/suite_status_test.py

Every expectation below was read by hand from src/ on 2026-09-13. If a plugin changes, an
expectation here may go out of date -- that is the point: fix the expectation from the plugin.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import suite_status as ss

fails = []


def check(label, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + label + ("" if ok else f" -- {detail}"))
    if not ok:
        fails.append(label)


files = {ss.name(f): f for f in ss.plugins(False)}
check("reads all 19 plugins", len(files) == 19, sorted(files))
S = {n: ss.sliders(f) for n, f in files.items()}
has = lambda plugin, block: bool(ss.find(S[plugin], dict(ss.BLOCKS + ss.WATCH)[block]))

check("Veil has 22 controls", len(S["veil"]) == 22, len(S["veil"]))
check("Veil lacks a plugin-wide Start delay", not has("veil", "start_delay"))
check("Veil's Ramp start delay is not counted as Start delay",
      any(s["label"].startswith("Ramp start delay") for s in S["veil"]))
check("the Morpher has Drift amount unit and Ramp by unit",
      has("spectral_vowel_morpher", "drift_amount_unit") and has("spectral_vowel_morpher", "ramp_by_unit"))
check("Tremolo lacks Drift amount unit", not has("Full_Feature_Tremolo", "drift_amount_unit"))
check("Womb's per-layer Play for counts (HB: Play for)", has("womb_sound_generator_v3", "play_for"))
check("Resonance Bank's Drift period MODE counts as a period unit", has("resonance_bank", "drift_period_unit"))
check("Melody has no control named Voice", not any(s["label"] == "Voice" for s in S["melody_phase"]))
check("Heartbeat has a pitch block (Pitch target)", has("heartbeat gen", "pitch_block"))
check("Passage's Transport unit is found", has("spectral_vowel_passage", "transport_unit"))
check("Sweep Dwell's Start delay mode is a transport unit, not a Start delay",
      has("sweep-dwell-filter", "transport_unit") and
      all("mode" not in s["label"].lower() for s in ss.find(S["sweep-dwell-filter"], dict(ss.BLOCKS)["start_delay"])))
bub = ss.find(S["bubbler"], dict(ss.WATCH)["spread"])
check("Bubbler's Pitch spread reads in semitones", any("(semitones)" in s["label"] for s in bub), bub)
tr = ss.find(S["Full_Feature_Tremolo"], dict(ss.WATCH)["rate_mode"])
check("Tremolo's Rate Mode options are the R20 five",
      tr and tr[0]["options"] == ["BPM", "Seconds", "Hz", "Every N beats", "N per beat"], tr)

print(f"\n{'ALL PASS' if not fails else str(len(fails)) + ' FAILED'}")
sys.exit(1 if fails else 0)
