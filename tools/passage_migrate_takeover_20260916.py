#!/usr/bin/env python3
"""Spectral Vowel Passage takes over from the Morpher: 63 sliders -> 89, in ONE migration.
docs/layouts/spectral-vowel-passage-takeover.md holds the agreed order and the build log.

BUILT IN STAGES alongside the plugin; live projects are migrated ONCE, when every stage is
in. Until then this file only offers `convert_line`, which the stage checks use on temp
copies. THE MAP IS AUTHORED (the layout doc); nothing is inferred. Every new control is
seeded to what reproduces the old sound.
"""
import math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from rpp_sliders import parse_line, render_line

N_OLD, N_NEW = 63, 89

MAP_TEXT = ("1-4:+0, 36:5, 34:6, 35:7, 25:11, 21:12, 22:13, 23:14, 24:15, 31:16, 32:17, 26:18, "
            "27:19, 13:20, 14:21, 5:22, 7:23, 6:24, 8:25, 10:26, 9:27, 12:28, 11:29, 30:30, 15:32, "
            "28:35, 16:36, 17:39, 18:44, 19:47, 20:48, 33:49, 37:60, 29:61, 41:62, 38:63, 39:64, "
            "40:65, 42:66, 43:67, 44:68, 47:69, 45:70, 46:71, 49:72, 48:73, 50:74, 51:75, 52:76, "
            "53:77, 54:79, 55:80, 57:81, 56:82, 58:83, 59:84, 60:85, 61:86, 62:88, 63:89")

def _map():
    m = {}
    for part in [p.strip() for p in MAP_TEXT.split(",")]:
        a, b = part.split(":")
        if "-" in a:
            lo, hi = map(int, a.split("-"))
            for i in range(lo, hi + 1):
                m[i] = i + int(b)
        else:
            m[int(a)] = int(b)
    return m
MAP = _map()
assert len(MAP) == N_OLD and len(set(MAP.values())) == N_OLD and set(MAP) == set(range(1, 64))


def num(tok, dflt):
    try:
        return float(tok)
    except (TypeError, ValueError):
        return dflt


# Stage 8: the 22-target list -> the 111 (Wash grain, 3, left the list; a picker parked there lands
# on Morph). Must agree with t111_o2n in the plugin.
T111 = {0: 8, 1: 9, 2: 6, 3: 0, 4: 11, 5: 14, 6: 15, 7: 17, 8: 19, 9: 20, 10: 2, 11: 3, 12: 4, 13: 5,
        14: 13, 15: 108, 16: 10, 17: 21, 18: 0, 19: 107, 20: 109, 21: 110}
assert len(T111) == 22


def cut_note(hz, ref):
    """The plugin's cut_note in Hz mode: 0 Off, else 1 + the nearest note number."""
    if hz <= 0:
        return 0
    m = 69 + 12 * math.log(max(hz, 0.000001) / max(ref, 0.001)) / math.log(2)
    return 1 + max(0, min(127, math.floor(m + 0.5)))


def convert_line(line):
    """One Passage slider line, old numbering -> new. Stages add their seeds here."""
    old = parse_line(line)
    new = {MAP[i]: old.get(i) for i in range(1, N_OLD + 1)}
    # Stage 4: High cut's off was 20000 and is 0; the note names follow the values, in Hz.
    # The pitch modes and fine tunes stay unset: the plugin's defaults are Hz and 0.
    ref = num(old.get(30), 440)
    ref = ref if ref >= 20 else 440
    if old.get(18) is not None and num(old.get(18), 20000) >= 19999.5:
        new[44] = "0"
    if new.get(39) is not None:
        new[38] = str(cut_note(num(new[39], 0), ref))
    if new.get(44) is not None:
        new[43] = str(cut_note(num(new[44], 0), ref))
    # Stage 8: the Drift and Ramp target pickers.
    for sl in (68, 80):
        if new.get(sl) is not None:
            new[sl] = str(T111[int(round(num(new[sl], 0)))])
    return render_line(line, new, n_sliders=N_NEW)


# --- Building migrated copies and writing them (2026-09-16) ---------------------------------------------
# Each instance is re-saved THROUGH THE NEW PLUGIN: its slider line converted, its old blob read by
# the new @serialize (which carries every bank into the new layout), and -- in a throwaway copy of
# the plugin only -- each captured slot's Output level raised by what the removed auto-gain gave it,
# less the new fixed gain. tools/passage_takeover_checks/verify_live.py measures the result.
import base64, hashlib, json, re, shutil, struct, subprocess

EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
FX = "spectral_vowel_passage"
PRE_COMMIT = "48e3771"            # the last commit before this build began
NEW_MAGIC = 7700009
LIVE = "E:/reaper"
SNAP = "E:/reaper/finished/backups/snapshots/passage-takeover-20260916"


def unpack(b64):
    raw = base64.b64decode(b64)
    return list(struct.unpack("<%df" % (len(raw) // 4), raw))


def heads(lines):
    return [i for i, l in enumerate(lines) if "<JS" in l and FX in l and "<JS_SER" not in l]


def blob_span(lines, sl):
    j = sl + 1
    while j < len(lines) and j < sl + 4 and "<JS_SER" not in lines[j]:
        j += 1
    if j >= len(lines) or "<JS_SER" not in lines[j]:
        return None
    a = j + 1
    b = a
    while lines[b].strip() != ">":
        b += 1
    return a, b


def files():
    out = []
    for top, dirs, names in os.walk(LIVE):
        if "backup" in top.lower():
            continue
        for n in names:
            if n.lower().endswith(".rpp"):
                pth = os.path.join(top, n).replace(os.sep, "/")
                if FX in open(pth, encoding="utf-8", errors="replace").read():
                    out.append(pth)
    return sorted(out)


def wash_gain_db(src):
    m = re.search(r"WASH_GAIN = pow\(10, ([0-9.]+) / 20\);", src)
    if not m:
        raise SystemExit("could not read WASH_GAIN from the plugin")
    return float(m.group(1))


def offsets_for(survey, path, inst, gain_db):
    """dB for each captured slot's Output level: the slot's measured auto-gain minus the fixed gain.
    Slots with no wash (Texture 0) are left alone."""
    slots = survey.get(os.path.basename(path), {}).get(str(inst))
    if slots is None:
        raise SystemExit("REFUSED: %s instance %d was not measured" % (path, inst))
    return {int(k) - 1: v["boost_db"] - gain_db for k, v in slots.items() if v.get("boost_db") is not None}


def migration_plugin(src, offs, work, tag):
    """A throwaway copy of the new plugin that adds this instance's offsets as an older save loads."""
    anchor = "  // TRACK-DUPLICATE FIX"
    if src.count(anchor) != 1:
        raise SystemExit("cannot find the @serialize anchor")
    nl = "\r\n" if "\r\n" in src else "\n"
    code = "".join("    slot_voicedb[%d] > -60 ? slot_voicedb[%d] = min(24, slot_voicedb[%d] + %.4f);%s" % (k, k, k, v, nl)
                   for k, v in sorted(offs.items()))
    inj = "  (file_avail(0) >= 0 && ser_magic < 7700009) ? (" + nl + (code or "    0;" + nl) + "  );" + nl
    pth = os.path.join(work, "mig_" + tag, FX + ".jsfx")
    os.makedirs(os.path.dirname(pth), exist_ok=True)
    open(pth, "w", encoding="utf-8", newline="").write(src.replace(anchor, inj + anchor))
    return pth


def convert_file(path, survey, work):
    """The whole migrated text, and a note per instance. Live files are only read."""
    src = open(os.path.join(ROOT, "src", FX + ".jsfx"), encoding="utf-8", newline="").read()
    gain = wash_gain_db(src)
    L = open(path, encoding="utf-8", errors="replace", newline="").read().split("\n")
    notes = []
    for n, h in reversed(list(enumerate(heads(L), start=1))):
        sl = h + 1
        span = blob_span(L, sl)
        if span is None:
            raise SystemExit("REFUSED %s instance %d: no blob" % (path, n))
        a, b = span
        magic = int(round(unpack("".join(x.strip() for x in L[a:b]))[0]))
        if magic >= NEW_MAGIC:
            raise SystemExit("REFUSED %s instance %d: already %d -- has this run?" % (path, n, magic))
        offs = offsets_for(survey, path, n, gain)
        T = list(L)
        T[sl] = convert_line(T[sl])
        tag = "%s_%d" % (os.path.basename(path)[:-4].replace(" ", "_"), n)
        tmp_rpp = os.path.join(work, tag + "_in.RPP")
        open(tmp_rpp, "w", encoding="utf-8", newline="").write("\n".join(T))
        plug = migration_plugin(src, offs, work, tag)
        saved = os.path.join(work, tag + "_saved.RPP")
        if os.path.exists(saved):
            os.remove(saved)
        subprocess.run([EXE, plug, "--rpp", tmp_rpp, "--fx", FX, "--instance", str(n), "--seconds", "0.05",
                        "--quiet", "--save-rpp", saved], capture_output=True)
        S = open(saved, encoding="utf-8").read().split("\n")
        sh = [i for i, l in enumerate(S) if "<JS" in l and "<JS_SER" not in l][0]
        sa, sb = blob_span(S, sh + 1)
        new_blob = "".join(x.strip() for x in S[sa:sb])
        if int(round(unpack(new_blob)[0])) != NEW_MAGIC:
            raise SystemExit("REFUSED %s instance %d: the saved blob is not %d" % (path, n, NEW_MAGIC))
        cr = "\r" if L[sl].endswith("\r") else ""
        L[sl] = L[sl][:len(L[sl]) - len(L[sl].lstrip())] + S[sh + 1].strip() + cr
        indent = L[a][:len(L[a]) - len(L[a].lstrip())]
        width = max(16, len(L[a].strip()))
        cr = "\r" if L[a].endswith("\r") else ""
        L[a:b] = [indent + new_blob[q:q + width] + cr for q in range(0, len(new_blob), width)]
        notes.append({"instance": n, "old_magic": magic, "offsets_db": {str(k + 1): round(v, 2) for k, v in offs.items()}})
    return "\n".join(L), list(reversed(notes))


def apply(out_dir):
    """Write the VERIFIED copies over the live files. Refuses unless the check passed every instance,
    every live file is byte-identical to what was checked, and no snapshot exists yet."""
    man = json.load(open(os.path.join(out_dir, "manifest.json")))
    if man.get("fails") != 0 or not man.get("files"):
        raise SystemExit("REFUSED: the check did not pass every instance")
    if os.path.exists(SNAP):
        raise SystemExit("REFUSED: %s exists -- has this already run?" % SNAP)
    for f in man["files"]:
        if hashlib.sha1(open(f["live"], "rb").read()).hexdigest() != f["live_sha1"]:
            raise SystemExit("REFUSED: %s changed since it was checked" % f["live"])
    os.makedirs(SNAP)
    for i, f in enumerate(man["files"]):
        rel = f["live"].replace(":", "").replace("/", "__")
        shutil.copy2(f["live"], os.path.join(SNAP, "%02d_%s" % (i, rel)))
    for f in man["files"]:
        data = open(f["migrated"], "rb").read()
        open(f["live"], "wb").write(data)
        if open(f["live"], "rb").read() != data:
            raise SystemExit("WRITE MISMATCH %s -- restore from %s" % (f["live"], SNAP))
    print("%d files, %d instances migrated; originals in %s" % (len(man["files"]), man["instances"], SNAP))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "apply":
        apply(sys.argv[2])
    else:
        print(__doc__)
        print("usage: python tools/passage_migrate_takeover_20260916.py apply VERIFIED_DIR")
