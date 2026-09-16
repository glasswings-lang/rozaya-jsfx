#!/usr/bin/env python3
"""Spectral Vowel Morpher, R26/R27: 64 sliders -> 79, in ONE migration.
docs/layouts/spectral-vowel-morpher-r26r27.md holds the agreed order and the build log.

BUILT IN STAGES alongside the plugin; the live projects are migrated ONCE, when every stage
is in. Until then this file only offers `convert_line`, which the stage checks use on temp
copies. Live files are never written by anything here yet.

THE MAP IS AUTHORED (the layout doc's table, and the map tools/jsfx_renumber.py applied to
src); nothing is inferred. Every new control is seeded to what reproduces the old sound.
"""
import math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from rpp_sliders import parse_line, render_line

N_OLD, N_NEW = 64, 79

# old id -> new id
MAP = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 9: 8, 8: 9, 10: 10, 11: 11, 13: 12, 15: 13,
       14: 14, 16: 15, 18: 16, 17: 17, 20: 18, 19: 19, 21: 20, 12: 22, 22: 25, 23: 26, 24: 29,
       25: 34, 26: 37, 27: 38, 28: 39, 29: 40, 30: 41, 32: 42, 31: 43, 34: 44, 33: 45, 35: 46,
       36: 47, 37: 48, 38: 49, 39: 50, 40: 51, 41: 53, 42: 54, 43: 55, 44: 56, 45: 57, 46: 58,
       49: 59, 47: 60, 48: 61, 51: 62, 50: 63, 52: 65, 53: 66, 54: 67, 55: 69, 56: 70, 58: 71,
       57: 72, 59: 73, 60: 74, 61: 75, 62: 76, 63: 78, 64: 79}
assert len(MAP) == N_OLD and len(set(MAP.values())) == N_OLD


# The 87-target list -> the 107 (Wash grain, 3, has no place; a picker parked there lands on
# Morph). Must agree with t107_o2n in the plugin.
def _t107(o):
    if o <= 2: return o
    if o == 3: return None
    if o == 4: return 7
    if o <= 7: return o - 1
    if o <= 10: return o + 1
    if o == 11: return 13
    if o <= 65: return o + 3
    return o + 20
T107 = {o: _t107(o) for o in range(87)}
T107 = {o: (n if n is not None else 0) for o, n in T107.items()}
assert sorted(n for o, n in T107.items() if o != 3) == sorted(set(n for o, n in T107.items() if o != 3))


def num(tok, dflt):
    try:
        return float(tok)
    except (TypeError, ValueError):
        return dflt


def cut_note(hz, ref):
    """The plugin's cut_note in Hz mode: 0 Off, else 1 + the nearest note number."""
    if hz <= 0:
        return 0
    m = 69 + 12 * math.log(max(hz, 0.000001) / max(ref, 0.001)) / math.log(2)
    return 1 + max(0, min(127, math.floor(m + 0.5)))


def convert_line(line):
    """A 64-slider Morpher line -> the 79-slider one. Stages not yet built leave their new
    slots unset ('-'), which the plugin reads as its declared default."""
    old = parse_line(line)
    new = {}
    for o, n in MAP.items():
        new[n] = old.get(o)
    # Stage 3: Transport unit. The three times counted beats when the old Rate mode (slider 9)
    # was Every N beats (3) or N per beat (4), else seconds.
    new[52] = "2" if num(old.get(9), 1) >= 3 else "0"
    # Stage 5: the Drift and Ramp target pickers (old 46, 56 -> 58, 70) move to the 107 list.
    for o, n in ((46, 58), (56, 70)):
        t = T107.get(int(num(old.get(o), 0)), 0)
        new[n] = str(t)
    # Stage 6: Spread is a pitch block; saved copies stay in Hz with no fine tune.
    new[21], new[23], new[24] = "0", "2", "0"
    # Stage 7: Low cut and High cut are pitch blocks, in Hz as saved, with the note name that
    # value shows (the plugin's cut_note at the saved Tuning reference, old slider 21). 0 is off
    # for both now; High cut's old off was 20000.
    ref = num(old.get(21), 440.0)
    lc = num(old.get(24), 0.0)
    hc = num(old.get(25), 20000.0)
    if hc >= 20000:
        hc = 0.0
    new[27], new[30], new[31] = "0", "2", "0"
    new[32], new[35], new[36] = "0", "2", "0"
    new[29] = "%g" % lc if lc > 0 else "0"
    new[34] = "%g" % hc if hc > 0 else "0"
    new[28] = str(cut_note(lc, ref))
    new[33] = str(cut_note(hc, ref))
    # Drift movement mode, Drift rest mode, Ramp rest mode: With the target, Walk through.
    new[64], new[68], new[77] = "0", "0", "0"
    return render_line(line, new, n_sliders=N_NEW)


# ---------------------------------------------------------------------------------------------
# The blob. Every live instance is first RESEALED through the pre-build Morpher (PRE), which
# reads whatever old format it holds and writes 7700087; that is then transcoded to 7700107
# here, mirroring the plugin's own t107 path exactly, so the idempotency check is the MAGIC.
import base64, struct, subprocess, tempfile

EXE = os.path.join(ROOT, "tools", "jsfx_run", "build", "Release", "jsfx_run.exe")
PRE_COMMIT = "a749714^"          # the last commit before this build began
FX = "spectral_vowel_morpher.jsfx"
NSLOTS, MAXFFT, NCUST, NLS = 8, 32768, 3, 16
OLD_MAGIC, NEW_MAGIC = 7700087, 7700107
LIVE = "E:/reaper"
EXTRA = ["C:/Users/solst/Dropbox/quick one.RPP"]
SNAP = "E:/reaper/finished/backups/snapshots/morpher-r26r27-20260916"


def unpack(b64):
    raw = base64.b64decode(b64)
    return list(struct.unpack("<%df" % (len(raw) // 4), raw))


def pack(vals):
    return base64.b64encode(struct.pack("<%df" % len(vals), *vals)).decode("ascii")


def parse87(v):
    p = 0
    d = {}
    def take(name, n):
        nonlocal p
        d[name] = list(v[p:p + n]); p += n
    take("magic", 1); take("have", 1); take("n_used", 1)
    take("slotraw", int(round(d["n_used"][0])) * MAXFFT)
    for b in ("d_up", "d_down", "d_per", "d_shape"): take(b, 87)
    take("last_target", 1)
    for b in ("r_by", "r_dur", "r_delay"): take(b, 87)
    take("last_ramp", 1)
    take("cappoint", NSLOTS); take("capavg", NSLOTS)
    take("lay_db", NLS); take("lay_semi_c", NCUST); take("last_lay_sel", 1)
    take("lay_active", NLS); take("lay_solo", NLS); take("lay_nharm", NLS); take("lay_ot", NLS)
    for b in ("d_play", "d_rest", "r_play", "r_rest"): take(b, 87)
    for b in ("lay_semi", "lay_punit", "lay_fine", "lay_funit"): take(b, NLS)
    take("lay_selv", 1); take("d_unit", 87); take("r_unit", 87)
    if p != len(v):
        raise ValueError("7700087 stream is %d floats, parsed %d" % (len(v), p))
    return d


def t107_bank(bank, dflt):
    out = [float(dflt)] * 107
    for o in range(87):
        if o != 3:
            out[T107[o]] = bank[o]
    return out


def transcode(vals, old_slots):
    d = parse87(vals)
    if int(round(d["magic"][0])) != OLD_MAGIC:
        raise ValueError("not a 7700087 blob")
    sel = lambda x: float(T107.get(int(max(0, min(86, int(x)))), 0))
    punit = num(old_slots.get(51), 1.0)
    tunit = num(old_slots.get(59), 2.0)
    out = [float(NEW_MAGIC)] + d["have"] + d["n_used"] + d["slotraw"]
    out += t107_bank(d["d_up"], 0) + t107_bank(d["d_down"], 0) + t107_bank(d["d_per"], 30) + t107_bank(d["d_shape"], 0)
    out += [sel(d["last_target"][0])]
    out += t107_bank(d["r_by"], 0) + t107_bank(d["r_dur"], 0) + t107_bank(d["r_delay"], 0)
    out += [sel(d["last_ramp"][0])]
    out += d["cappoint"] + d["capavg"] + d["lay_db"] + d["lay_semi_c"] + d["last_lay_sel"]
    out += d["lay_active"] + d["lay_solo"] + d["lay_nharm"] + d["lay_ot"]
    out += t107_bank(d["d_play"], 0) + t107_bank(d["d_rest"], 0) + t107_bank(d["r_play"], 0) + t107_bank(d["r_rest"], 0)
    out += d["lay_semi"] + d["lay_punit"] + d["lay_fine"] + d["lay_funit"] + d["lay_selv"]
    out += t107_bank(d["d_unit"], 0) + t107_bank(d["r_unit"], 0)
    out += [punit] * 107 + [tunit] * 107 + [0.0] * 107
    return out


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
                pth = os.path.join(top, n).replace("\\", "/")
                if FX in open(pth, encoding="utf-8", errors="replace").read():
                    out.append(pth)
    return sorted(out) + [x for x in EXTRA if os.path.exists(x)]


def pre_plugin(tmp):
    src = subprocess.run(["git", "show", PRE_COMMIT + ":src/" + FX], cwd=ROOT, capture_output=True,
                         text=True, encoding="utf-8").stdout
    if "@serialize" not in src:
        raise SystemExit("could not read the pre-build Morpher from git")
    pth = os.path.join(tmp, "pre", FX)
    os.makedirs(os.path.dirname(pth), exist_ok=True)
    open(pth, "w", encoding="utf-8", newline="").write(src)
    return pth


def reseal(pre, path, inst, tmp):
    out = os.path.join(tmp, "reseal_%d.RPP" % inst)
    subprocess.run([EXE, pre, "--rpp", path, "--fx", "spectral_vowel_morpher", "--instance", str(inst),
                    "--seconds", "0.05", "--quiet", "--save-rpp", out], capture_output=True)
    L = open(out, encoding="utf-8").read().split("\n")
    h = [i for i, l in enumerate(L) if "<JS" in l and "<JS_SER" not in l]
    a, b = blob_span(L, h[0] + 1)
    return unpack("".join(x.strip() for x in L[a:b]))


def convert_text(path, pre, tmp):
    """The whole migrated file, and one note per instance. Refuses anything unexpected."""
    L = open(path, encoding="utf-8", errors="replace").read().split("\n")
    notes = []
    hs = heads(L)
    for n, h in reversed(list(enumerate(hs, start=1))):
        sl = h + 1
        span = blob_span(L, sl)
        if span is None:
            raise SystemExit("REFUSED %s instance %d: no blob" % (path, n))
        a, b = span
        magic = int(round(unpack("".join(x.strip() for x in L[a:a + 1]))[0])) if L[a].strip() else -1
        vals = unpack("".join(x.strip() for x in L[a:b]))
        magic = int(round(vals[0]))
        if magic == NEW_MAGIC:
            raise SystemExit("REFUSED %s instance %d: already %d -- has this run?" % (path, n, NEW_MAGIC))
        old_slots = parse_line(L[sl])
        sealed = vals if magic == OLD_MAGIC else reseal(pre, path, n, tmp)
        new_vals = transcode(sealed, old_slots)
        L[sl] = convert_line(L[sl])
        indent = L[a][:len(L[a]) - len(L[a].lstrip())]
        b64 = pack(new_vals)
        L[a:b] = [indent + b64[q:q + 128] for q in range(0, len(b64), 128)]
        notes.append((n, magic))
    return "\n".join(L), list(reversed(notes))



def apply(out_dir):
    """Write the VERIFIED copies over the live files. Refuses unless verify_live.py passed every
    instance, every live file is byte-identical to what was verified, and no snapshot exists."""
    import hashlib, json, shutil
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
        print("usage: python tools/morpher_migrate_r26r27_20260916.py apply VERIFIED_DIR")
