"""suite_status.py -- what each plugin HAS, read from the plugin files. No doc involved.

The docs kept a copy of this and the copy went stale: on 2026-09-13 a 590-line backlog said
Melody still needed a voice selector (it deliberately has none) and listed built work as owed.
The plugin is the truth. Ask it.

  python tools/suite_status.py                  every plugin: which suite blocks it has
  python tools/suite_status.py lacks BLOCK      which plugins lack a block (names below)
  python tools/suite_status.py controls NAME    one plugin's every control, range and options
  python tools/suite_status.py --installed ...  read REAPER's installed copies instead of src/

Every answer prints the control labels it matched, so a wrong match shows. It reads slider
declarations only: it says a control EXISTS, never that it works (measure that with jsfx_run).
"""
import glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALLED = os.path.join(os.environ.get("APPDATA", ""), "REAPER", "Effects", "glasswings")

# block name -> label pattern (case-insensitive, matched from the start of the label)
BLOCKS = [
    # "HB play for" (Womb's per-layer transport; "HB: Play for" until 2026-09-14), never Drift's or Ramp's own
    ("start_delay",       r"(?!drift |ramp )(\w+:? )?start delay(?! mode)"),
    ("play_for",          r"(?!drift |ramp )(\w+:? )?play for"),
    ("rest_for",          r"(?!drift |ramp )(\w+:? )?rest for"),
    ("transport_unit",    r"transport unit|start delay mode"),
    ("rest_mode",         r"rest mode|lfo at rest|modulation at rest"),
    ("output_at_rest",    r"output at rest"),
    ("drift_target",      r"drift target"),
    ("drift_amount_unit", r"drift amount unit"),
    ("drift_period_unit", r"drift period (unit|mode)"),
    ("drift_play_rest",   r"drift (play|rest) for"),
    ("drift_movement",    r"drift movement"),
    ("ramp_target",       r"ramp target"),
    ("ramp_by_unit",      r"ramp by unit"),
    ("ramp_time_unit",    r"ramp time unit"),
    ("ramp_play_rest",    r"ramp (play|rest) for"),
    ("pitch_block",       r".*(transpose unit|pitch mode|pitch unit|pitch target|tuning reference)"),
    ("solo",              r".*\bsolo\b"),
]
WATCH = [("spread", r".*spread"), ("pan_mode", r"(?!.*rate).*\bpan\b.*mode"),
         ("rate_mode", r"(?!start delay).*rate mode")]


def plugins(installed):
    base = INSTALLED if installed else os.path.join(ROOT, "src")
    return sorted(glob.glob(os.path.join(base, "*.jsfx")))


def sliders(path):
    out = []
    for line in open(path, encoding="utf-8", errors="replace"):
        m = re.match(r"^slider(\d+):([^<]*)<([^>]*)>(.*)$", line.rstrip("\r\n"))
        if not m:
            continue
        rng = m.group(3)
        opts = re.search(r"\{([^}]*)\}", rng)
        out.append({"n": int(m.group(1)), "default": m.group(2), "label": m.group(4).strip(),
                    "range": re.sub(r"\{[^}]*\}", "", rng).strip(","),
                    "options": opts.group(1).split(",") if opts else None})
    return out


def find(ss, pattern):
    return [s for s in ss if re.match(pattern, s["label"], re.I)]


def name(path):
    return os.path.basename(path)[:-5]


def main(argv):
    installed = "--installed" in argv
    args = [a for a in argv[1:] if a != "--installed"]
    files = plugins(installed)
    if not files:
        print("no plugins found"); return 1
    if args[:1] == ["controls"]:
        want = " ".join(args[1:]).lower()
        hits = [f for f in files if want in name(f).lower()]
        if len(hits) != 1:
            print(f"'{want}' matches {[name(f) for f in hits] or 'nothing'}"); return 1
        ss = sliders(hits[0])
        print(f"{name(hits[0])}: {len(ss)} controls")
        for s in ss:
            extra = "{" + ", ".join(s["options"]) + "}" if s["options"] else s["range"]
            print(f"  {s['n']:>3}  {s['label']}  [{extra}] default {s['default']}")
        return 0
    if args[:1] == ["lacks"]:
        block = args[1] if len(args) > 1 else ""
        pat = dict(BLOCKS + WATCH).get(block)
        if not pat:
            print("blocks:", ", ".join(b for b, _ in BLOCKS + WATCH)); return 1
        lacking = [name(f) for f in files if not find(sliders(f), pat)]
        print(f"{len(lacking)} of {len(files)} lack {block}: {', '.join(lacking) or 'none'}")
        return 0
    for f in files:
        ss = sliders(f)
        missing = [b for b, p in BLOCKS if not find(ss, p)]
        print(f"{name(f)} ({len(ss)} controls)")
        print(f"  lacks: {', '.join(missing) or 'nothing listed'}")
        for w, p in WATCH:
            for s in find(ss, p):
                o = " {" + ", ".join(s["options"]) + "}" if s["options"] else f" [{s['range']}]"
                print(f"  {w}: s{s['n']} {s['label']}{o}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
