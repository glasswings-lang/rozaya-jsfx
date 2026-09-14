"""jsfx_map.py -- see what else leans on the part of a plugin you are changing.

A plugin is ~2,900 lines; reading it whole every time fills a session, and even
read whole, nobody holds it all in mind. This reports the whole file so a change
can be made reading only the part it touches. Pure text analysis: it compiles and
runs nothing. It APPLIES nothing either -- it only reports, and says why it lists
each thing, so a wrong guess shows.

  python tools/jsfx_map.py map    FILE              sections, functions, memory table
  python tools/jsfx_map.py uses   FILE NAME [NAME..] every line touching those names
  python tools/jsfx_map.py impact OLD NEW           what a change leans on (two files)
  python tools/jsfx_map.py impact --git REV FILE    the same, for commit REV (REV^ -> REV)
  python tools/jsfx_map.py impact --git REV FILE --json   (for tests)

`impact` is the one to run after an edit, before measuring. It reports:
  1. Groups: arrays the change treats alike (passed to one function, or given the
     same kind of new line), and the other arrays in their FAMILY the change did
     NOT treat. A family is a shared name prefix (lay_semi, lay_hph -> "lay").
     An untreated sibling is not a bug by itself; it is a question.
  2. Order-sensitive: every rand() and @serialize use touching a name the change
     touched or an untreated sibling. rand() is one stream, so moving what an
     array means without moving what the stream wrote into it changes the sound.
  3. Memory: allocations added, removed, resized or reordered.
Built 2026-09-13 after stage 3 of the Morpher pitch layout reordered five layer
banks but not the layers' random starting phases (tests/jsfx_map_test.py).
"""
import difflib, json, re, subprocess, sys, collections

IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_.]*")
KEYWORDS = set("""loop while function local instance static globals this abs min max floor ceil
sqrt sin cos tan atan atan2 exp log log10 pow rand sign memset memcpy freembuf file_var file_mem
file_avail file_string spl slider sliderchange slider_automate strlen sprintf printf time_precise
invsqrt stack_push stack_pop midisend midirecv srate samplesblock tempo play_state play_position
beat_position ts_num ts_denom num_ch pdc_delay pdc_bot_ch pdc_top_ch ext_noinit ext_nodenorm
spl0 spl1 freemem""".split())


def strip_comments(text):
    """Blank comments but keep every newline, so line numbers stay true."""
    text = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.S)
    return [re.sub(r"//.*$", "", ln) for ln in text.split("\n")]


class Plugin:
    def __init__(self, text):
        self.raw = text.split("\n")
        self.code = strip_comments(text)
        self.sections = []           # (name, first line, last line), 1-based
        self.functions = []          # (name, first line, last line)
        self.alloc = collections.OrderedDict()   # name -> (size expression, line)
        cur = None
        for i, ln in enumerate(self.code, 1):
            m = re.match(r"^(@\w+)", ln)
            if m:
                if cur:
                    self.sections.append((cur[0], cur[1], i - 1))
                cur = (m.group(1), i)
            a = re.match(r"^\s*([A-Za-z_]\w*)\s*=\s*freemem\s*;\s*freemem\s*\+=\s*([^;]+);", ln)
            if a:
                self.alloc[a.group(1)] = (re.sub(r"\s+", "", a.group(2)), i)
        if cur:
            self.sections.append((cur[0], cur[1], len(self.code)))
        self._find_functions()
        self._fixed_allocs()

    def _fixed_allocs(self):
        # The other allocation style: a fixed address, `target_drift_up = 8224;`. Only a
        # name that is indexed somewhere (name[...]) counts as an array, so a plain
        # setting like `host_bpm = 120;` is not one. Size is the gap to the next address.
        indexed = set(re.findall(r"(?<![\w.])([A-Za-z_]\w*)\s*\[", "\n".join(self.code)))
        init = set(self.section_lines("@init")) or set(range(1, len(self.code) + 1))
        infn = {l for f, a, b in self.functions for l in range(a, b + 1)}   # parameters are not allocations
        top = [i for i in sorted(init) if i not in infn]
        literal = {}      # scalar base -> number, e.g. db = 8192;
        for i in top:
            for m in re.finditer(r"(?<![\w.])([A-Za-z_]\w*)\s*=\s*(\d+)\s*;", self.code[i - 1]):
                literal.setdefault(m.group(1), int(m.group(2)))
        fixed, relative = {}, collections.OrderedDict()
        for i in top:
            # a third style: an offset from a named start, `drift_up_mem = db + 144;`
            for m in re.finditer(r"(?<![\w.])([A-Za-z_]\w*)\s*=\s*(\d+|[A-Za-z_]\w*)\s*(\+\s*([^;]+?))?\s*;",
                                 self.code[i - 1]):
                n, base, off = m.group(1), m.group(2), (m.group(4) or "").strip()
                if n not in indexed or n in self.alloc or n in fixed or n in relative:
                    continue
                if base == "freemem" or not re.fullmatch(r"[\w\s*+()]*", off):
                    continue
                expr = base + (" + " + off if off else "")
                addr = self._resolve(expr, literal)
                if addr is not None:
                    fixed[n] = (addr, i)      # 8224; db + 144 with db = 8192; 8192 + 13*SDB with SDB = 64
                else:
                    relative[n] = ("=" + re.sub(r"\s+", "", expr), i)
        order = sorted(fixed.items(), key=lambda kv: kv[1][0])
        for k, (n, (addr, ln)) in enumerate(order):
            gap = order[k + 1][1][0] - addr if k + 1 < len(order) else None
            self.alloc[n] = (f"@{addr}" + (f"(gap{gap})" if gap is not None else "(last)"), ln)
        for n, v in relative.items():
            self.alloc[n] = v
    def _find_functions(self):
        # functions: from "function name(" to the line where parens balance again
        i = 0
        while i < len(self.code):
            m = re.search(r"\bfunction\s+([A-Za-z_]\w*)\s*\(", self.code[i])
            if m:
                depth, j, started = 0, i, False
                while j < len(self.code):
                    seg = self.code[j][m.start():] if j == i else self.code[j]
                    for ch in seg:
                        if ch == "(":
                            depth += 1; started = True
                        elif ch == ")":
                            depth -= 1
                    # a function is "name(args) local(..) ( body )": done when the body closes
                    if started and depth == 0 and self._body_opened(i, j, m.start()):
                        break
                    j += 1
                self.functions.append((m.group(1), i + 1, j + 1))
                i = j + 1
                continue
            i += 1

    @staticmethod
    def _resolve(expr, literal):
        """A number when every name in expr has a plain numeric value in @init, else None."""
        names = re.findall(r"[A-Za-z_]\w*", expr)
        if any(n not in literal for n in names):
            return None
        text = re.sub(r"[A-Za-z_]\w*", lambda m: str(literal[m.group(0)]), expr)
        if not re.fullmatch(r"[\d\s*+()]+", text):
            return None
        return int(eval(text, {"__builtins__": {}}))

    def _body_opened(self, i, j, col):
        text = " ".join([self.code[i][col:]] + self.code[i + 1:j + 1])
        text = re.sub(r"^function\s+\w+\s*\([^)]*\)", "", text.strip())
        text = re.sub(r"^\s*(local|instance|static|globals)\s*\([^)]*\)", "", text)
        text = re.sub(r"^\s*(local|instance|static|globals)\s*\([^)]*\)", "", text)
        return "(" in text

    def where(self, line):
        """'@block' or '@init > function mo_q' for a 1-based line."""
        sec = next((s for s, a, b in self.sections if a <= line <= b), "(header)")
        fn = next((f for f, a, b in self.functions if a <= line <= b), None)
        return sec + (" > " + fn + "()" if fn else "")

    def names_on(self, line):
        return {n for n in IDENT.findall(self.code[line - 1])
                if n.lower() not in KEYWORDS and not re.match(r"slider\d+$", n)}

    def uses(self, name):
        pat = re.compile(r"(?<![A-Za-z0-9_.])" + re.escape(name) + r"(?![A-Za-z0-9_])")
        return [i for i, ln in enumerate(self.code, 1) if pat.search(ln)]

    def section_lines(self, sec):
        return [i for s, a, b in self.sections if s == sec for i in range(a, b + 1)]


def family(name):
    return name.split("_")[0] if "_" in name else None


def kind_of_line(line_text, name):
    """How a line touches an array: 'fn:NAME' when passed to a function, else 'write'/'read'."""
    for m in re.finditer(r"([A-Za-z_]\w*)\s*\(([^()]*)\)", line_text):
        args = [a.strip() for a in m.group(2).split(",")]
        if name in args and m.group(1) not in ("loop", "while"):
            return "fn:" + m.group(1)
    if re.search(r"(?<![\w.])" + re.escape(name) + r"\s*\[[^\]]*\]\s*=(?!=)", line_text):
        return "write"
    return "read"


ASSIGN = re.compile(r"(?<![\w.])([A-Za-z_]\w*)\s*(\[[^\]]*\])?\s*(?<![<>!=])=(?!=)")


def rand_consumers(p):
    """Arrays whose values come from the rand() stream, with the lines that write them.

    Scope is the innermost loop( ) around each rand() call, or its own line when
    there is none. Inside that scope, walking statements in order, a value is from
    the stream when its right-hand side calls rand() or reads something already
    from the stream in that scope (j = rand(..); a[i] = a[j] -- a shuffle; or a
    right channel copied from a random left one). Arrays only.
    """
    flat = "\n".join(p.code)
    starts = [0]
    for ln in p.code:
        starts.append(starts[-1] + len(ln) + 1)

    def line_of(off):
        lo, hi = 0, len(starts) - 1
        while lo < hi - 1:
            mid = (lo + hi) // 2
            if starts[mid] <= off:
                lo = mid
            else:
                hi = mid
        return lo + 1

    scopes = set()
    for m in re.finditer(r"\brand\s*\(", flat):
        depth, s, k = 0, None, m.start() - 1
        while k >= 0 and flat[k] != "@":
            ch = flat[k]
            if ch == ")":
                depth += 1
            elif ch == "(":
                if depth == 0:
                    if re.search(r"\bloop\s*$", flat[max(0, k - 12):k]):
                        s = k
                        break
                else:
                    depth -= 1
            k -= 1
        if s is None:
            a = flat.rfind("\n", 0, m.start()) + 1
            b = flat.find("\n", m.start())
            scopes.add((a, b if b >= 0 else len(flat)))
            continue
        depth, e = 0, s
        while e < len(flat):
            depth += (flat[e] == "(") - (flat[e] == ")")
            if depth == 0:
                break
            e += 1
        scopes.add((s + 1, e))

    out = collections.defaultdict(list)
    for a, b in sorted(scopes):
        tainted = set()
        pos = a
        for chunk in re.split(r"(;)", flat[a:b]):
            if chunk != ";":
                ms = list(ASSIGN.finditer(chunk))
                if ms:
                    last = ms[-1]
                    rhs = chunk[last.end():]
                    if re.search(r"\brand\s*\(", rhs) or any(
                            re.search(r"(?<![\w.])" + re.escape(t) + r"(?!\w)", rhs) for t in tainted):
                        name = last.group(1)
                        tainted.add(name)
                        ln = line_of(pos + last.start())
                        if name in p.alloc and ln not in out[name]:
                            out[name].append(ln)
            pos += len(chunk)
    return out


def changed_lines(old, new):
    """1-based NEW lines added or changed, and OLD lines removed (code only, comments blanked)."""
    sm = difflib.SequenceMatcher(None, [l.strip() for l in old.code], [l.strip() for l in new.code], autojunk=False)
    added, removed = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("replace", "insert"):
            added += [j + 1 for j in range(j1, j2) if new.code[j].strip()]
        if tag in ("replace", "delete"):
            removed += [i + 1 for i in range(i1, i2) if old.code[i].strip()]
    return added, removed


def impact(old, new):
    added, removed = changed_lines(old, new)
    arrays = set(new.alloc)
    # 1. groups: arrays given the same treatment on added lines
    treat = collections.defaultdict(set)
    touched = set()
    for ln in added:
        for n in new.names_on(ln):
            touched.add(n)
            if n in arrays:
                k = kind_of_line(new.code[ln - 1], n)
                if k.startswith("fn:"):
                    treat[k].add(n)
    for ln in removed:
        touched |= {n for n in old.names_on(ln)}
    groups = []
    for k, members in sorted(treat.items()):
        fams = collections.Counter(family(m) for m in members if family(m))
        for fam, cnt in fams.items():
            if cnt < 2:
                continue
            siblings = sorted(a for a in arrays if family(a) == fam and a not in members)
            groups.append({"treatment": k[3:] + "()", "family": fam,
                           "treated": sorted(m for m in members if family(m) == fam),
                           "untreated": siblings})
    untreated = {s for g in groups for s in g["untreated"]}
    # 2. order-sensitive uses
    rc = rand_consumers(new)
    ser = set(new.section_lines("@serialize"))
    order = []
    for n in sorted(touched | untreated):
        if n in rc:
            why = "untreated sibling" if n in untreated else "touched by the change"
            # @init draws are a starting identity (a layer's phases); later draws happen during play
            when = "start" if all(new.where(l).startswith("@init") for l in rc[n]) else "play"
            order.append({"name": n, "what": "filled from rand()", "lines": rc[n], "why": why, "when": when})
        s = [l for l in new.uses(n) if l in ser]
        if s and n in arrays:
            why = "untreated sibling" if n in untreated else "touched by the change"
            order.append({"name": n, "what": "saved in @serialize", "lines": s, "why": why})
    # 3. memory
    oa, na = list(old.alloc), list(new.alloc)
    mem = {"added": [n for n in na if n not in old.alloc],
           "removed": [n for n in oa if n not in new.alloc],
           "resized": [(n, old.alloc[n][0], new.alloc[n][0]) for n in na
                       if n in old.alloc and old.alloc[n][0] != new.alloc[n][0]]}
    common = [n for n in na if n in old.alloc]
    old_order = [n for n in oa if n in new.alloc]
    mem["reordered"] = common != old_order
    return {"added_lines": len(added), "removed_lines": len(removed),
            "groups": groups, "order_sensitive": order, "memory": mem}


def print_impact(r, new):
    print(f"Change: {r['added_lines']} code lines added or changed, {r['removed_lines']} removed.")
    print("\n1. Arrays treated alike, and family members left out")
    if not r["groups"]:
        print("   none")
    for g in r["groups"]:
        print(f"   {g['treatment']} was given {len(g['treated'])} '{g['family']}' arrays: {', '.join(g['treated'])}")
        print(f"     not given: {', '.join(g['untreated']) or 'none'}")
    print("\n2. Order-sensitive uses")
    os_ = r["order_sensitive"]
    qs = [o for o in os_ if o["why"] == "untreated sibling" and "rand" in o["what"] and o["when"] == "start"]
    print("   QUESTIONS -- left out of a group above, and given STARTING values from the rand() stream:")
    for o in qs:
        where = sorted({new.where(l) for l in o["lines"]})
        print(f"     {o['name']}: line {', '.join(map(str, o['lines'][:4]))} ({'; '.join(where)})")
    if not qs:
        print("     none")
    def names(what, why, when=None):
        return ", ".join(o["name"] for o in os_ if what in o["what"] and o["why"] == why
                         and (when is None or o.get("when") == when)) or "none"
    print(f"   left out of a group, and drawn from rand() during play (draw order matters): "
          f"{names('rand', 'untreated sibling', 'play')}")
    print(f"   touched, and filled from rand(): {names('rand', 'touched by the change')}")
    print(f"   touched, and in the save format: {names('serialize', 'touched by the change')}")
    print(f"   left out of a group, and in the save format: {names('serialize', 'untreated sibling')}")
    print("   (python tools/jsfx_map.py uses FILE NAME shows every line of any of these)")
    m = r["memory"]
    print("\n3. Memory")
    print(f"   added: {', '.join(m['added']) or 'none'}")
    print(f"   removed: {', '.join(m['removed']) or 'none'}")
    print(f"   resized or moved: {', '.join(f'{n} {a}->{b}' for n, a, b in m['resized']) or 'none'}")
    print(f"   existing allocations reordered: {'YES' if m['reordered'] else 'no'}")


def load(path):
    return Plugin(open(path, encoding="utf-8", newline="").read().replace("\r\n", "\n"))


def load_git(rev, path):
    out = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, check=True)
    return Plugin(out.stdout.decode("utf-8").replace("\r\n", "\n"))


def main(argv):
    if len(argv) < 3:
        print(__doc__); return 2
    cmd = argv[1]
    if cmd == "map":
        p = load(argv[2])
        print("Sections:")
        for s, a, b in p.sections:
            print(f"  {s:<11} lines {a}-{b}")
        print(f"Functions ({len(p.functions)}):")
        for f, a, b in p.functions:
            print(f"  {f:<22} lines {a}-{b}  in {p.where(a).split(' >')[0]}")
        print(f"Memory, in allocation order ({len(p.alloc)}):")
        for n, (size, ln) in p.alloc.items():
            print(f"  {n:<24} {size:<20} line {ln}")
        rc = rand_consumers(p)
        print("Filled from rand():", ", ".join(f"{n} (line {l[0]})" for n, l in rc.items()) or "none")
        # say what the memory table could NOT place, so an empty or short table is not read as the truth
        indexed = sorted(set(re.findall(r"(?<![\w.])([A-Za-z_]\w*)\s*\[", "\n".join(p.code))) - set(p.alloc))
        print(f"Indexed but not in the memory table ({len(indexed)}): {', '.join(indexed) or 'none'}")
        return 0
    if cmd == "uses":
        p = load(argv[2])
        for name in argv[3:]:
            lines = p.uses(name)
            print(f"{name}: {len(lines)} lines" + (f"  (memory: {p.alloc[name][0]}, line {p.alloc[name][1]})" if name in p.alloc else ""))
            for l in lines:
                print(f"  {l:>5}  {p.where(l):<28} {p.raw[l - 1].strip()[:110]}")
        return 0
    if cmd == "impact":
        args = [a for a in argv[2:] if a != "--json"]
        if args[0] == "--git":
            old, new = load_git(args[1] + "^", args[2]), load_git(args[1], args[2])
        else:
            old, new = load(args[0]), load(args[1])
        r = impact(old, new)
        if "--json" in argv:
            print(json.dumps(r))
        else:
            print_impact(r, new)
        return 0
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
