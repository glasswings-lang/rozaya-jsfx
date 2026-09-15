#!/usr/bin/env python3
"""Repair Tensor's shepard.RPP: 8 Shepard Tone instances saved by the FIRST RELEASE.

WHY: the 2026-09-10 pitch rebuild said no project used Shepard Tone, so it had no
migration, and the Solo migration that evening then padded these lines as if they
were on the rebuilt layout. They were saved on 2026-04-09 by the first release
(d19873f, 58 sliders, no @serialize): scored against every layout in the plugin's
history, only d19873f takes all 464 stored values in range. Open bug 4.

WHAT: reads the Shepard Tone lines from the pre-Solo snapshot (untouched first-release
values), maps them BY THE AUTHORED TABLE BELOW onto today's 97-slider layout, and
replaces only those 8 slider lines in the live file. Every other line of the live file
is kept, including the Tremolo and Sweeping Filter lines migrated since.

REFUSES rather than guessing: not exactly 8 instances in either file; a snapshot line
that is not 58 values plus padding; a live line that is not the 98-value line found on
2026-09-15; a voice in Independent mode (its rate-0 meaning changed in 4da88e2).

Dry run by default: writes a trial copy to --out. --apply also snapshots the live file
to backups/snapshots/_pre-tensor-shepard-repair-20260915/ and writes it. Run once.
"""
import argparse, os, re, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpp_sliders import parse_line, render_line

SNAP = "E:/reaper/finished/backups/snapshots/_pre-solo-20260910/tensor's-rpp-projects__shepard.RPP"
LIVE = "E:/tensor's-rpp-projects/shepard.RPP"
BACKUP_DIR = "E:/reaper/finished/backups/snapshots/_pre-tensor-shepard-repair-20260915"
JS = re.compile(r'^\s*<JS\s+(?:"([^"]+)"|(\S+))')
LIVE_HEAD = ['0', '1', '1000', '8', '3', '50', '50', '0', '0', '440']   # what 2026-09-15 found

# ---- The authored table: first release (d19873f) -> today (97 sliders) ----------------
# Globals. Old slider -> new slider; None = a control the first release did not have,
# set to the value that reproduces first-release behaviour.
GLOBAL = [
    (1, 1),     # Drift Mode {Synced, Independent}      -> Drift mode, same indices
    (3, 2),     # Rate Value                            -> Rate value
    (2, 3),     # Rate Mode {BPM, Seconds, Hz}          -> Rate mode, same first three indices
    (4, 4),     # Octave Count
    (5, 5),     # Center Octave
    (6, 6),     # Fade In %
    (7, 7),     # Fade Out %
    (8, 8),     # Waveform: first release's six are today's first six, same order
    (9, 10),    # Binaural Beat Hz                      -> Binaural beat (Hz)
    (10, 12),   # Tuning Reference Hz                   -> Tuning reference (Hz)
]
NEW_GLOBAL = {
    9: "25",    # Pulse width: not in the first release; its default, and unused by these waveforms
    11: "0",    # Root note C: the first release's voice note was absolute; C adds nothing
    13: "2",    # Fine tune unit = Cents: the first release's Synced detune was cents
}
# The first release had no pan: each voice went to both sides at full level. Today a
# centred voice goes to each side at cos(45 degrees), 3.0103 dB lower -- measured on all 8
# instances as exactly that. Rozaya, asked whether the repair should put it back so the
# project sounds as saved: "Yes".
CENTRE_PAN_DB = 3.0103
# Per voice v = 0..7. Old base 11 + 6v: Note, Octave, Direction, Drift/Rate, Gain dB, Active.
# New base 14 + 8v: note, fine tune, direction, rate, gain, pan, active, solo.
# Old Octave has no new slider: the first release moved every root into the pitch window
# by whole octaves, so the octave never reached the sound.
def voice(old, v, synced):
    ob, nb = 11 + 6 * v, 14 + 8 * v
    drift = old[ob + 3]
    return {
        nb:     old[ob],                     # note
        nb + 1: drift if synced else "0",    # Synced: Drift was cents -> fine tune (in Cents)
        nb + 2: old[ob + 2],                 # direction
        nb + 3: "0" if synced else drift,    # Independent: Drift was the rate (refused below)
        nb + 4: "%.4f" % (float(old[ob + 4]) + CENTRE_PAN_DB),   # gain dB, see CENTRE_PAN_DB
        nb + 5: "0",                         # pan: centre (the first release had none)
        nb + 6: old[ob + 5],                 # active
        nb + 7: "0",                         # solo off
    }
# Everything from 78 up (transport, Drift, Ramp) did not exist: today's declared defaults,
# read from the plugin below, reproduce "not there" -- no delay, no gate, no drift, no ramp.
N_NEW = 97

def declared_defaults(path):
    d = {}
    for ln in open(path, encoding="utf-8"):
        m = re.match(r"slider(\d+):([^<]*)<", ln.strip())
        if m: d[int(m.group(1))] = m.group(2).strip()
    return d

def js_lines(lines):
    return [i + 1 for i, ln in enumerate(lines)
            if JS.match(ln) and "shepard-tone" in (JS.match(ln).group(1) or JS.match(ln).group(2))]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="trial copy to write")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    plugin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "shepard-tone.jsfx")
    defaults = declared_defaults(plugin)
    assert len(defaults) == N_NEW, "today's plugin has %d sliders, table expects %d" % (len(defaults), N_NEW)

    snap = open(SNAP, encoding="utf-8", errors="surrogateescape", newline="").read().splitlines(keepends=True)
    live = open(LIVE, encoding="utf-8", errors="surrogateescape", newline="").read().splitlines(keepends=True)
    si, li = js_lines(snap), js_lines(live)
    if len(si) != 8 or len(li) != 8: sys.exit("REFUSED: expected 8 Shepard Tone lines, snapshot %d, live %d" % (len(si), len(li)))

    out = list(live)
    for k, (s_idx, l_idx) in enumerate(zip(si, li)):
        toks = snap[s_idx].split()
        if len(toks) != 64 or any(t != "-" for t in toks[58:]) or "-" in toks[:58]:
            sys.exit("REFUSED: snapshot instance %d is not 58 values plus padding" % (k + 1))
        if len(live[l_idx].split()) != 98 or live[l_idx].split()[:10] != LIVE_HEAD:
            sys.exit("REFUSED: live instance %d is not the line found on 2026-09-15" % (k + 1))
        old = parse_line(snap[s_idx])
        synced = old[1] == "0"
        if not synced: sys.exit("REFUSED: instance %d is Independent; its rate-0 meaning changed" % (k + 1))
        new = dict(defaults)
        for o, n in GLOBAL: new[n] = old[o]
        new.update(NEW_GLOBAL)
        for v in range(8): new.update(voice(old, v, synced))
        assert sorted(new) == list(range(1, N_NEW + 1))
        out[l_idx] = render_line(live[l_idx], new, n_sliders=N_NEW)
        back = parse_line(out[l_idx])
        assert all(back[s] == new[s] for s in new), "instance %d did not render back" % (k + 1)

    changed = [i for i in range(len(live)) if live[i] != out[i]]
    assert changed == li, "changed lines %s are not exactly the 8 Shepard Tone slider lines" % changed
    open(a.out, "w", encoding="utf-8", errors="surrogateescape", newline="").write("".join(out))
    print("trial copy written: %s (%d lines changed, all Shepard Tone slider lines)" % (a.out, len(changed)))
    if a.apply:
        if os.path.exists(BACKUP_DIR): sys.exit("REFUSED: %s exists -- this repair has been run" % BACKUP_DIR)
        os.makedirs(BACKUP_DIR)
        shutil.copy2(LIVE, os.path.join(BACKUP_DIR, "shepard.RPP"))
        open(LIVE, "w", encoding="utf-8", errors="surrogateescape", newline="").write("".join(out))
        print("APPLIED: live file written; the file before is in", BACKUP_DIR)

if __name__ == "__main__":
    main()
