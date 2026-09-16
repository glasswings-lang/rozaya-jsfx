#!/usr/bin/env python3
"""R24 audit."""
# R24 audit: list every slider in every plugin and say whether it is named in the
# plugin's Drift target list. It CLASSIFIES NOTHING -- it prints the two lists side
# by side so a human reads them. (CLAUDE.md: a script may APPLY an authored list;
# it may never INFER one.)
import re, glob, os, sys

SLIDER = re.compile(r'^slider(\d+):([^<]*)<([^>]*)>(.*)$')

def parse(path):
    sliders = []          # (num, name, options_or_None)
    targets = None
    for line in open(path, encoding='utf-8', errors='replace'):
        m = SLIDER.match(line.rstrip('\n'))
        if not m:
            continue
        num, _default, spec, name = m.groups()
        name = name.strip()
        opts = None
        if '{' in spec:
            opts = spec[spec.index('{')+1:spec.rindex('}')].split(',')
            opts = [o.strip() for o in opts]
        sliders.append((int(num), name, opts))
        if name.startswith('Drift target') and opts:
            targets = opts
    return sliders, targets

def base(n):
    # strip the R25 "(per target)" / unit parentheses so names compare
    return re.sub(r'\s*\([^)]*\)\s*$', '', n).strip()

for path in sorted(glob.glob('src/*.jsfx')):
    sliders, targets = parse(path)
    if targets is None:
        print('== %s -- NO DRIFT TARGET LIST' % os.path.basename(path)); continue
    tset = set(t.lower() for t in targets)
    print('== %s  (%d sliders, %d targets)' % (os.path.basename(path), len(sliders), len(targets)))
    for num, name, opts in sliders:
        b = base(name)
        if b.lower().startswith(('drift ', 'ramp ')):
            continue
        hit = b.lower() in tset
        kind = 'LIST' if opts else 'num '
        print('   %-5s %-5s s%-4d %s' % ('target' if hit else '  --  ', kind, num, name))
    orphan = [t for t in targets if t.lower() not in set(base(n).lower() for _, n, _ in sliders)]
    if orphan:
        print('   !! target options with no slider of that name: %s' % ', '.join(orphan))
    print()
