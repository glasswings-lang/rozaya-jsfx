"""page_controls.py -- does each plugin page describe the controls its plugin really has?

page_slider_numbers.py checks the slider NUMBERS a page writes. This checks the rest: on
2026-09-13 Passage's page still said Transpose value was -96 to +96 after the plugin said
-20000 to 20000, and pages still gave ranges the 2026-09-06 range sweep had widened.

  python tools/page_controls.py              every page: counts, then each finding
  python tools/page_controls.py womb         one page

Findings, each naming the page entry and the plugin's declaration:
  MISMATCH range/default/options  a page's `range`, default or {options} differs from the plugin
  NOT IN PLUGIN   a control entry (**Name** followed by `range`) matching no declared control
  NAME STYLE      an entry matching a control only once units and case are ignored
                  ("Dry/Wet %" for "Dry/wet (%)") -- the page predates a rename
  NOT ON PAGE     a declared control whose name appears nowhere on the page, even in prose
                  (per-voice/per-note names count when the page writes them once, "Vn Note")
It reads text: a finding is a question for whoever edits the page, not a verdict. The plugin
is read with tools/suite_status.py; the page->plugin map is page_slider_numbers.py's.
"""
import ast, glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import suite_status as ss

_src = open(os.path.join(HERE, "page_slider_numbers.py"), encoding="utf-8").read()
PAGES = ast.literal_eval(re.search(r"PAGES\s*=\s*(\{.*?\})\n", _src, re.S).group(1))

PREFIX = re.compile(r"^(v[1-8]|[a-g]#?|hb:|breath:|bloodflow:|s[12]:?)\s+", re.I)
ENTRY = re.compile(r"\*\*([^*\n]{2,90})\*\*\s*`([^`\n]+)`")


def norm(s):
    return re.sub(r"\s+", " ", s.replace("−", "-")).strip().lower()


def base(label):
    return norm(re.sub(r"\s*\(.*$", "", label))


def loose(name):
    """Ignore units, punctuation and case: 'Dry/Wet %' and 'Dry/wet (%)' agree."""
    s = norm(re.sub(r"\(.*?\)", " ", name))
    s = re.sub(r"(%|\bdb\b|\bhz\b|\bsec(onds)?\b|\bms\b|,?\s*slider \d+)", " ", s)
    return re.sub(r"[^a-z0-9#]+", " ", s).strip()


def num(s):
    try:
        return float(s.replace(",", "").replace("+", "").replace("−", "-"))
    except (ValueError, AttributeError):
        return None


def looks_like_spec(spec):
    """A control's `...` gives a range, a default or an option list; prose code does not."""
    s = spec.replace("−", "-")
    return bool(re.search(r"default|^\s*\{|^\s*[+-]?\d[\d.,]*\s*(to|–|—|\.\.|-)\s*[+-]?\d|\S\s+/\s+\S", s))


def parse_spec(spec):
    spec = spec.replace("−", "-")
    body, _, dflt = spec.partition(", default")
    dflt = dflt.strip().rstrip(",;.") or None
    if body.strip().startswith("{"):
        return ("options", [o.strip() for o in body.strip().strip("{}").split(",")], dflt)
    if " / " in body and not re.search(r"\d", body):
        return ("options", [o.strip() for o in body.split("/")], dflt)
    m = re.match(r"^\s*([+-]?\d[\d.,]*)\s*(?:to|–|—|\.\.|-)\s*([+-]?\d[\d.,]*)", body)
    return ("range", (num(m.group(1)), num(m.group(2))), dflt) if m else None


def same_at_page_rounding(page_value, declared):
    p, d = num(page_value), num(declared)
    if p is None or d is None:
        return True
    decimals = len(page_value.split(".")[1]) if "." in page_value else 0
    return abs(round(d, decimals) - p) < 1e-9


def check_page(page_text, sliders):
    by_base = {base(s["label"]): s for s in sliders}
    by_full = {norm(s["label"]): s for s in sliders}
    by_loose = {loose(s["label"]): s for s in sliders}
    for s in sliders:                       # "V3 Gain dB" is also findable as "Vn Gain dB"
        stripped = PREFIX.sub("", s["label"])
        if stripped != s["label"]:
            by_base.setdefault(base(stripped), s)
            by_loose.setdefault(loose(stripped), s)
    text_n = norm(page_text)
    out = []
    for ln, line in enumerate(page_text.split("\n"), 1):
        for m in ENTRY.finditer(line):
            name, spec_text = m.group(1).strip(), m.group(2)
            if not looks_like_spec(spec_text):
                continue
            entry = f"**{name}** `{spec_text}`"[:100]
            clean = re.sub(r",?\s*slider \d+", "", name)
            key = PREFIX.sub("", norm(re.sub(r"^vn\s+", "v1 ", norm(clean))))
            s = by_full.get(norm(clean)) or by_base.get(base(clean)) or by_base.get(base(key))
            if s is None:
                s = by_loose.get(loose(clean)) or by_loose.get(loose(key))
                if s is None:
                    out.append(("NOT IN PLUGIN", ln, entry, ""))
                    continue
                out.append(("NAME STYLE", ln, entry, f"slider{s['n']}: {s['label']}"))
            spec = parse_spec(spec_text)
            if not spec:
                continue
            kind, val, dflt = spec
            decl = f"slider{s['n']}: {s['label']} <{s['range']}>"
            if kind == "options" and s["options"]:
                opts, page_opts = [norm(o) for o in s["options"]], [norm(o) for o in val]
                abbreviated = any(o in ("…", "...") or "…" in o or "..." in o for o in page_opts)
                if abbreviated:
                    ends = [o for o in page_opts if o not in ("…", "...")]
                    ok = bool(ends) and ends[0].split("…")[0].strip() == opts[0] and \
                        ends[-1].split("…")[-1].strip() == opts[-1]
                else:
                    ok = page_opts == opts
                if not ok:
                    out.append(("MISMATCH options", ln, entry, decl + " {" + ", ".join(s["options"]) + "}"))
                elif dflt and not abbreviated:
                    i = num(s["default"])
                    if i is not None and 0 <= int(i) < len(opts) and opts[int(i)] != norm(dflt):
                        out.append(("MISMATCH default", ln, entry, decl))
            elif kind == "range" and not s["options"]:
                rng = s["range"].split(",")
                lo, hi = (num(rng[0]), num(rng[1])) if len(rng) >= 2 else (None, None)
                if None not in (lo, hi, *val) and (abs(lo - val[0]) > 1e-9 or abs(hi - val[1]) > 1e-9):
                    out.append(("MISMATCH range", ln, entry, decl))
                elif dflt and re.fullmatch(r"[+-]?\d[\d.,]*(\s*\w+)?", dflt) and \
                        not same_at_page_rounding(dflt.split()[0], s["default"]):
                    out.append(("MISMATCH default", ln, entry, decl + f" default {s['default']}"))
    for s in sliders:
        names = {base(s["label"]), base(PREFIX.sub("", s["label"]))}
        if not any(n and n in text_n for n in names):
            out.append(("NOT ON PAGE", 0, "", f"slider{s['n']}: {s['label']}"))
    return out


def main(argv):
    want = argv[1].lower() if len(argv) > 1 else None
    total = 0
    for page in sorted(glob.glob(os.path.join(ROOT, "docs", "plugins", "*.md"))):
        key = os.path.basename(page)[:-3]
        plug = PAGES.get(key)
        if not plug or (want and want not in key):
            continue
        found = check_page(open(page, encoding="utf-8", errors="replace").read(),
                           ss.sliders(os.path.join(ROOT, "src", plug + ".jsfx")))
        total += len(found)
        kinds = {}
        for k, *_ in found:
            kinds[k] = kinds.get(k, 0) + 1
        print(f"{key}: {len(found)} findings {kinds or ''}")
        for k, ln, entry, decl in found:
            where = f"line {ln}: {entry}" if ln else ""
            print(f"   {k:<17} {where}{'  <-> ' if where and decl else ''}{decl}")
    print(f"\n{total} findings (report only; nothing is changed)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
