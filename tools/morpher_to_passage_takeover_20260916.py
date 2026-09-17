#!/usr/bin/env python3
"""Carry every live Spectral Vowel Morpher copy into Spectral Vowel Passage, in place (2026-09-16).

docs/layouts/spectral-vowel-passage-takeover.md, "The Morpher carry-over", holds the decisions:
replace in place (Rozaya: "replace them."), and layer levels read what was HEARD (Layer 1 at 0 dB,
each other layer relative to it; Rozaya: "Yeah, go for the first.").

THE MAPS ARE AUTHORED here, id for id, from both plugins' agreed layouts; nothing is inferred.

Per copy:
  1. READ through the Morpher itself (src, the installed build), so every older save format is
     converted by the code that wrote it: a probe copy dumps n_used, the captures, the per-slot
     capture points and averages, every Drift/Ramp bank and every layer bank as audio samples, and
     then auditions each captured slot alone to read what the Morpher's wash auto-gain gave it.
  2. PACK a carry blob (magic 7799001, a layout defined only here and in the reader) and the
     Passage slider line.
  3. RESEAL through a throwaway Passage whose @serialize reads the carry blob, and save: the result
     is an ordinary 7700009 Passage state.
  4. The project's <JS line names Passage; its slider line and blob are the resealed ones.
tools/passage_takeover_checks/verify_morpher_carry.py measures every copy before `apply` writes.
"""
import base64, hashlib, json, math, os, re, shutil, struct, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from rpp_sliders import parse_line, render_line
import morpher_migrate_r26r27_20260916 as mm
import passage_migrate_takeover_20260916 as pm

EXE = pm.EXE
NSLOTS, MAXFFT, NLAY = 8, 32768, 16
M_TARGETS, P_TARGETS, P_STRIDE = 107, 111, 128
CARRY_MAGIC = 7799001
SNAP = "E:/reaper/finished/backups/snapshots/morpher-to-passage-20260916"

# Morpher slider id -> Passage slider id (both agreed layouts, 2026-09-16).
M2P = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 9, 9: 10, 10: 20, 11: 21, 12: 22, 13: 23, 14: 24,
       15: 25, 16: 26, 17: 27, 18: 28, 19: 29, 20: 30, 21: 31, 22: 32, 23: 33, 24: 34, 25: 35, 26: 36,
       27: 37, 28: 38, 29: 39, 30: 40, 31: 41, 32: 42, 33: 43, 34: 44, 35: 45, 36: 46, 37: 47, 38: 48,
       39: 49, 40: 50, 41: 51, 42: 52, 43: 53, 44: 54, 45: 55, 46: 56, 47: 57, 48: 58, 49: 59, 50: 60,
       51: 61, 52: 62, 53: 63, 54: 64, 55: 65, 56: 66, 57: 67, 58: 68, 59: 69, 60: 70, 61: 71, 62: 72,
       63: 73, 64: 74, 65: 75, 66: 76, 67: 77, 68: 78, 69: 79, 70: 80, 71: 81, 72: 82, 73: 83, 74: 84,
       75: 85, 76: 86, 77: 87, 78: 88, 79: 89}
assert len(M2P) == 79 and len(set(M2P.values())) == 79
# Passage-only controls and what a carried copy gets: Auto-morph timing on Rate (the Morpher's motion).
P_NEW = {8: "1"}
# Passage's per-slot controls, filled into all eight slots from the Morpher's one global value.
PER_SLOT_SLIDERS = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 32, 33, 34, 35, 36, 37, 39, 40, 41, 42, 44, 45, 46, 47, 48, 61]


def t_m2p(t):
    """Morpher target (107 list) -> Passage target (111 list): the slot timings sit at 2-5 in Passage."""
    return t if t <= 1 else t + 4


def p_glob(t):
    return t <= 1 or t == 10 or 21 <= t <= 107 or t >= 109


# The Drift/Ramp banks the carry blob holds, in this order, per Passage (slot, target).
M_BANKS = ["target_drift_up", "target_drift_down", "target_drift_per", "target_drift_shape", "target_drift_play",
           "target_drift_rest", "target_drift_unit", "target_drift_punit", "drift_moves", "ramp_by_mem",
           "ramp_dur_mem", "ramp_delay_mem", "ramp_play_mem", "ramp_rest_mem", "ramp_by_unit", "ramp_tunit"]
P_BANKS = ["target_drift_up", "target_drift_down", "target_drift_per", "target_drift_shape", "target_drift_play",
           "target_drift_rest", "target_drift_unit", "target_drift_punit", "target_drift_moves", "ramp_by_mem",
           "ramp_dur_mem", "ramp_delay_mem", "ramp_play_mem", "ramp_rest_mem", "ramp_by_unit", "ramp_tunit"]
P_BANK_DEFAULT = [0, 0, 30, 0, 0, 0, 0, 1, None, 0, 0, 0, 0, 0, 0, 2]
M_LAYER = ["lay_active", "lay_semi", "lay_punit", "lay_fine", "lay_funit", "lay_db_base", "lay_solo", "lay_nharm", "lay_ot_harm"]
P_LAYER = ["lay_active", "lay_semi", "lay_punit", "lay_fine", "lay_funit", "lay_db", "lay_solo", "lay_nharm", "lay_ot_harm"]


def probe_plugin(work):
    """The Morpher with a dump appended to @sample: after one block, n_used, then the captures,
    capture points, capture averages, the 16 banks x 107 and the 9 layer banks x 16; spl1 carries
    rms_smooth throughout, for the per-slot auto-gain reading."""
    src = open(os.path.join(ROOT, "src", "spectral_vowel_morpher.jsfx"), encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in src else "\n"
    i = src.rfind(nl + "@serialize")
    body = [
        "dmp_i == 0 ? ( dmp_n = 1 + n_used*MAXFFT + NSLOTS*2 + %d*%d + %d*%d; );" % (len(M_BANKS), M_TARGETS, len(M_LAYER), NLAY),
        "dmp_i < dmp_n ? (",
        "  dmp_k = dmp_i;",
        "  dmp_k == 0 ? ( spl0 = n_used; ) : (",
        "    dmp_k -= 1;",
        "    dmp_k < n_used*MAXFFT ? ( spl0 = slotraw[dmp_k]; ) : (",
        "      dmp_k -= n_used*MAXFFT;",
        "      dmp_k < NSLOTS ? ( spl0 = slot_cappoint[dmp_k]; ) : dmp_k < 2*NSLOTS ? ( spl0 = slot_capavg[dmp_k - NSLOTS]; ) : (",
        "        dmp_k -= 2*NSLOTS;",
        "        dmp_k < %d ? (" % (len(M_BANKS) * M_TARGETS),
    ]
    for b, name in enumerate(M_BANKS):
        body.append("          floor(dmp_k / %d) == %d ? spl0 = %s[dmp_k - %d];" % (M_TARGETS, b, name, b * M_TARGETS))
    body.append("        ) : (")
    body.append("          dmp_k -= %d;" % (len(M_BANKS) * M_TARGETS))
    for b, name in enumerate(M_LAYER):
        body.append("          floor(dmp_k / %d) == %d ? spl0 = %s[dmp_k - %d];" % (NLAY, b, name, b * NLAY))
    body += ["        );", "      );", "    );", "  );", "  dmp_i += 1;", ");",
             "spl1 = 0;"]
    text = src[:i] + nl + nl.join(body) + nl + src[i:]
    pth = os.path.join(work, "morpher_probe", "spectral_vowel_morpher.jsfx")
    os.makedirs(os.path.dirname(pth), exist_ok=True)
    open(pth, "w", encoding="utf-8", newline="").write(text)
    return pth


def read_morpher(probe, rpp, inst, work, tag):
    """Everything the carry needs from one Morpher copy, read through the Morpher."""
    import numpy as np
    SEG = 2.0
    csv = os.path.join(work, tag + "_dump.csv")
    # First pass: the dump only (the Morpher as saved, one block in).
    total = 1 + NSLOTS * MAXFFT + NSLOTS * 2 + len(M_BANKS) * M_TARGETS + len(M_LAYER) * NLAY
    secs = "%.3f" % (total / 44100 + 0.1)
    if os.path.exists(csv):
        os.remove(csv)
    subprocess.run([EXE, probe, "--rpp", rpp, "--fx", "spectral_vowel_morpher", "--instance", str(inst), "--seconds", secs,
                    "--quiet", "--csv", csv], capture_output=True)
    x = np.loadtxt(csv, delimiter=",", skiprows=1, usecols=(2,))
    p = 0
    n_used = int(round(x[p])); p += 1
    raw = x[p:p + n_used * MAXFFT]; p += n_used * MAXFFT
    cappoint = x[p:p + NSLOTS]; p += NSLOTS
    capavg = x[p:p + NSLOTS]; p += NSLOTS
    banks = [x[p + b * M_TARGETS:p + (b + 1) * M_TARGETS] for b in range(len(M_BANKS))]; p += len(M_BANKS) * M_TARGETS
    layers = [x[p + b * NLAY:p + (b + 1) * NLAY] for b in range(len(M_LAYER))]; p += len(M_LAYER) * NLAY
    boosts = []
    return {"n_used": n_used, "raw": raw, "cappoint": cappoint, "capavg": capavg, "banks": banks, "layers": layers,
            "boost_db": boosts}


def passage_line(m_line, rebase_db):
    """The Passage slider line from a Morpher one: the authored id map, the pickers through t_m2p,
    Auto-morph timing on Rate, and the shown layer's level rebased when levels are rebased."""
    o = parse_line(m_line)
    n = {M2P[k]: v for k, v in o.items() if k in M2P}
    for k, v in P_NEW.items():
        n[k] = v
    for sl in (68, 80):
        if n.get(sl) is not None:
            n[sl] = str(t_m2p(int(round(pm.num(n[sl], 0)))))
    return render_line(m_line, n, n_sliders=89)


def carry_blob(md, pline, rebase_db, offsets):
    """The 7799001 carry blob: the order the reader in carry_reader() expects, and nothing else."""
    d = parse_line(pline)
    vals = [CARRY_MAGIC, 1 if md["n_used"] > 0 else 0, md["n_used"]]
    vals += list(md["raw"])
    vals += list(md["cappoint"]) + list(md["capavg"])
    # The per-slot sliders' values, in PER_SLOT_SLIDERS order, then each slot's Output level offset.
    vals += [pm.num(d.get(k), 0) for k in PER_SLOT_SLIDERS]
    vals += [offsets.get(s, 0.0) for s in range(NSLOTS)]
    # 16 banks x (8 slots x 128 targets): Morpher targets land on their Passage index, a per-slot one in
    # every slot's row, a whole-plugin one in slot 0's; everything else keeps Passage's default.
    for b in range(len(M_BANKS)):
        out = []
        for s in range(NSLOTS):
            row = [None] * P_STRIDE
            for t in range(M_TARGETS):
                pt = t_m2p(t)
                if s == 0 or not p_glob(pt):
                    row[pt] = float(md["banks"][b][t])
            for t in range(P_STRIDE):
                if row[t] is None:
                    dflt = P_BANK_DEFAULT[b]
                    row[t] = float(dflt if dflt is not None else (0 if (2 <= t <= 5 or t in (109, 110)) else 1))
            out += row
        vals += out
    lay = [list(map(float, md["layers"][b])) for b in range(len(M_LAYER))]
    if rebase_db is not None:
        db = lay[M_LAYER.index("lay_db_base")]
        lay[M_LAYER.index("lay_db_base")] = [0.0] + [(v if v <= -60 else v - rebase_db) for v in db[1:]]
    for b in range(len(M_LAYER)):
        vals += lay[b]
    return base64.b64encode(struct.pack("<%df" % len(vals), *vals)).decode("ascii")


def rebase_for(md):
    """Layer 1's dB when the levels can read what was heard (Layer 1 audible, no layer past +24), else None."""
    act, db = md["layers"][M_LAYER.index("lay_active")], md["layers"][M_LAYER.index("lay_db_base")]
    if act[0] < 0.5 or db[0] <= -60:
        return None
    if any(db[k] > -60 and db[k] - db[0] > 24 for k in range(1, NLAY)):
        return None
    return float(db[0])


def carry_reader(src):
    """A throwaway Passage that reads a 7799001 carry blob after its own @serialize block skips it."""
    nl = "\r\n" if "\r\n" in src else "\n"
    anchor = nl + "@serialize" + nl
    head = src.find(anchor)
    if head < 0:
        raise SystemExit("no @serialize")
    per = "".join("    cr_v = 0; file_var(0, cr_v); cr_sl[%d] = cr_v;%s" % (j, nl) for j in range(len(PER_SLOT_SLIDERS)))
    banks = "".join("    file_mem(0, %s, DBANK);%s" % (b, nl) for b in P_BANKS)
    lays = "".join("    file_mem(0, %s, NLAY);%s" % (b, nl) for b in P_LAYER)
    fill = []
    names = {20: "slot_texture[cs] = cr_sl[%d] * 0.01", 21: "slot_grain[cs] = cr_sl[%d]", 22: "slot_srcnote[cs] = cr_sl[%d]",
             23: "slot_srcfunit[cs] = cr_sl[%d]", 24: "slot_srcfine[cs] = cr_sl[%d]", 25: "slot_tgtnote[cs] = cr_sl[%d]",
             26: "slot_tunit[cs] = cr_sl[%d]", 27: "slot_pitch[cs] = cr_sl[%d]", 28: "slot_funit[cs] = cr_sl[%d]",
             29: "slot_fine[cs] = cr_sl[%d]", 31: "slot_spmode[cs] = cr_sl[%d]", 32: "slot_spread[cs] = cr_sl[%d]",
             33: "slot_spfunit[cs] = cr_sl[%d]", 34: "slot_spfine[cs] = cr_sl[%d]", 35: "slot_width[cs] = cr_sl[%d]",
             36: "slot_denoise[cs] = cr_sl[%d]", 37: "slot_lcmode[cs] = cr_sl[%d]", 39: "slot_lowcut[cs] = cr_sl[%d]",
             40: "slot_lcfunit[cs] = cr_sl[%d]", 41: "slot_lcfine[cs] = cr_sl[%d]", 42: "slot_hcmode[cs] = cr_sl[%d]",
             44: "slot_hicut[cs] = cr_sl[%d]", 45: "slot_hcfunit[cs] = cr_sl[%d]", 46: "slot_hcfine[cs] = cr_sl[%d]",
             47: "slot_ot_harm[cs] = cr_sl[%d]", 48: "slot_ot_depth[cs] = cr_sl[%d]",
             61: "slot_voicedb[cs] = cr_sl[%d] <= -60 ? -60 : min(24, cr_sl[%d] + cr_off[cs])"}
    for j, k in enumerate(PER_SLOT_SLIDERS):
        expr = names[k]
        fill.append("      " + (expr % (j, j) if expr.count("%d") == 2 else expr % j) + ";")
    block = nl.join([
        "",
        "// --- CARRY READER (throwaway build, tools/morpher_to_passage_takeover_20260916.py) ---",
        "(file_avail(0) >= 0 && ser_magic == %d) ? (" % CARRY_MAGIC,
        "  cr_sl = freemem + 64; cr_off = freemem + 128;   // past everything @init allocated",
        "  file_var(0, have); file_var(0, n_used);",
        "  file_mem(0, slotraw, n_used*MAXFFT);",
        "  file_mem(0, slot_cappoint, NSLOTS); file_mem(0, slot_capavg, NSLOTS);",
        per.rstrip(nl),
        "  file_mem(0, cr_off, NSLOTS);",
        banks.rstrip(nl),
        lays.rstrip(nl),
        "  cs = 0;",
        "  loop(NSLOTS,",
        nl.join(fill),
        "      slot_linger[cs] = 4; slot_xfade[cs] = 1; slot_fadein[cs] = 1; slot_gap[cs] = 0; slot_xfadeon[cs] = 1; slot_mute[cs] = 0; slot_tmunit[cs] = 0;",
        "    cs += 1;",
        "  );",
        "  seed_slots_from_sliders = 0; grain_seed = 0; units_seed = 0;",
        "  ser_magic = 7700009;",
        "  dupsel = max(0, min(NSLOTS, floor(slider1 + 0.5))); dupslot = dupsel == 0 ? 0 : dupsel - 1;",
        "  last_cap_slot = dupslot; last_cap_sel = dupsel; last_cap_all = dupsel == 0;",
        "  duptgt = max(0, min(N_TARGETS-1, slider68)); duprtgt = max(0, min(N_TARGETS-1, slider80));",
        "  last_drift_key = (tg_glob[duptgt] ? 0 : dupslot)*DSTRIDE + duptgt;",
        "  last_ramp_key  = (tg_glob[duprtgt] ? 0 : dupslot)*DSTRIDE + duprtgt;",
        "  slider61 = slot_voicedb[dupslot];",
        "  dlay = max(0, min(NLAY, floor(slider50 + 0.5))); dlay = dlay == 0 ? 0 : dlay - 1; slider56 = lay_db[dlay];",
        "  sliderchange(-1);",
        "  ps_adopt(); lay_dr_adopt(); lay_adopt(); ps_inited = 1; lay_ui_inited = 1; lay_ot_dirty = 1;",
        "  last_lay_selv = max(0, min(NLAY, floor(slider50 + 0.5)));",
        ");",
        ""])
    return src.rstrip() + nl + block


def fx_heads(lines):
    return [i for i, l in enumerate(lines) if "<JS" in l and "spectral_vowel_morpher" in l and "<JS_SER" not in l]


def level_probe(work):
    """The Morpher (rand pinned) whose wash auto-gain smoother restarts when the auditioned slot
    changes, so a slot heard alone reaches the level the Morpher settles on for it within a grain."""
    src = open(os.path.join(ROOT, "src", "spectral_vowel_morpher.jsfx"), encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in src else "\n"
    j = src.find(nl + "@sample" + nl) + len(nl + "@sample" + nl)
    text = src[:j] + "slider1 != lvp_last ? ( rms_smooth = 0; lvp_last = slider1; );" + nl + src[j:]
    text = text.replace("_tp = time_precise();", "_tp = 0.25;")
    pth = os.path.join(work, "morpher_level", "spectral_vowel_morpher.jsfx")
    os.makedirs(os.path.dirname(pth), exist_ok=True)
    open(pth, "w", encoding="utf-8", newline="").write(text)
    return pth


def slot_level(plug, rpp, fx, inst, slot, work, secs=4.0):
    """The level of one slot auditioned alone: rms from 1 s in to the end (random grain phases make a
    one-second reading wander by about half a dB)."""
    import numpy as np
    csv = os.path.join(work, "lvl.csv")
    if os.path.exists(csv):
        os.remove(csv)
    subprocess.run([EXE, plug, "--rpp", rpp, "--fx", fx, "--instance", str(inst), "--seconds", str(secs), "--quiet",
                    "--csv", csv, "--set-after", "5=0", "--set-after", "1=%d" % (slot + 1)], capture_output=True)
    if not os.path.exists(csv):
        return None
    x = np.loadtxt(csv, delimiter=",", skiprows=1)[:, 2:]
    seg = x[44100:]
    return math.sqrt((seg ** 2).mean())


def convert_file(path, work, probe, reader_plug, log=print, level_plug=None, passage_pin=None):
    """The whole migrated text and one note per copy. Live files are only read."""
    L = open(path, encoding="utf-8", errors="replace", newline="").read().split("\n")
    notes = []
    gain_db = pm.wash_gain_db(open(os.path.join(ROOT, "src", "spectral_vowel_passage.jsfx"), encoding="utf-8").read())
    for n, h in reversed(list(enumerate(fx_heads(L), start=1))):
        sl = h + 1
        span = pm.blob_span(L, sl)
        if span is None:
            raise SystemExit("REFUSED %s copy %d: no blob" % (path, n))
        a, b = span
        tag = "%s_%d" % (re.sub(r"[^A-Za-z0-9]+", "_", os.path.basename(path)[:-4]), n)
        md = read_morpher(probe, path, n, work, tag)
        rebase = rebase_for(md)
        pline = passage_line(L[sl], rebase)

        def reseal(offs, suffix):
            """A one-copy temp project pointed at the reader, saved through it: a 7700009 Passage state."""
            T = list(L)
            T[h] = T[h].replace("spectral_vowel_morpher", "spectral_vowel_passage")
            T[sl] = pline
            T[a:b] = [carry_blob(md, pline, rebase, offs)]
            tmp_rpp = os.path.join(work, tag + "_carry" + suffix + ".RPP")
            open(tmp_rpp, "w", encoding="utf-8", newline="").write("\n".join(T))
            out = os.path.join(work, tag + "_saved" + suffix + ".RPP")
            if os.path.exists(out):
                os.remove(out)
            # Its instance number among the Passage copies of THIS temp file (later copies were renamed already).
            pinst = sum(1 for i2, l2 in enumerate(T) if i2 <= h and "<JS" in l2 and "spectral_vowel_passage" in l2 and "<JS_SER" not in l2)
            subprocess.run([EXE, reader_plug, "--rpp", tmp_rpp, "--fx", "spectral_vowel_passage", "--instance", str(pinst),
                            "--seconds", "0.05", "--quiet", "--save-rpp", out], capture_output=True)
            return out

        # Pass 1 carries with no level change. Each captured slot is then heard alone through the Morpher
        # (level_plug) and through the carried Passage, and pass 2 moves that slot's Output level by the
        # difference: what the Morpher's wash auto-gain gave it, measured rather than derived.
        saved0 = reseal({}, "0")
        offs = {}
        for s_ in range(md["n_used"]):
            lm = slot_level(level_plug, path, "spectral_vowel_morpher", n, s_, work)
            lp = slot_level(passage_pin, saved0, "spectral_vowel_passage", 1, s_, work)
            if lm and lp and lm > 1e-7 and lp > 1e-7:
                offs[s_] = 20 * math.log10(lm / lp)
        saved = reseal(offs, "1")
        S = open(saved, encoding="utf-8").read().split("\n")
        sh = [i for i, l in enumerate(S) if "<JS" in l and "<JS_SER" not in l][0]
        sa, sb = pm.blob_span(S, sh + 1)
        new_blob = "".join(x.strip() for x in S[sa:sb])
        if int(round(pm.unpack(new_blob)[0])) != 7700009:
            raise SystemExit("REFUSED %s copy %d: the resealed blob is not 7700009" % (path, n))
        cr = "\r" if L[h].endswith("\r") else ""
        L[h] = L[h].replace("spectral_vowel_morpher", "spectral_vowel_passage")
        L[sl] = L[sl][:len(L[sl]) - len(L[sl].lstrip())] + S[sh + 1].strip() + ("\r" if L[sl].endswith("\r") else "")
        indent = L[a][:len(L[a]) - len(L[a].lstrip())]
        width = max(16, len(L[a].strip()))
        cr = "\r" if L[a].endswith("\r") else ""
        L[a:b] = [indent + new_blob[q:q + width] + cr for q in range(0, len(new_blob), width)]
        notes.append({"copy": n, "n_used": md["n_used"], "rebased_from_db": rebase,
                      "offsets_db": {str(s + 1): v for s, v in offs.items()}})
        log("  %s copy %d: %d slots, layer levels %s, Output level offsets %s" % (
            os.path.basename(path), n, md["n_used"],
            "as heard (Layer 1 was %.1f dB)" % rebase if rebase is not None else "as typed",
            {s + 1: round(v, 1) for s, v in offs.items()}))
    return "\n".join(L), list(reversed(notes))


def apply(out_dir):
    man = json.load(open(os.path.join(out_dir, "manifest.json")))
    if man.get("fails") != 0 or not man.get("files"):
        raise SystemExit("REFUSED: the check did not pass every copy")
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
    print("%d files, %d copies carried into Passage; originals in %s" % (len(man["files"]), man["copies"], SNAP))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "apply":
        apply(sys.argv[2])
    else:
        print(__doc__)
