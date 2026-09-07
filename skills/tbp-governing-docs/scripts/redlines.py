#!/usr/bin/env python3
"""Inventory and resolve the TBP redline macros in a .tex file.

The macros are \\added{new}, \\removed{old}, \\changed{new}{old}, plus the
\\addedfragile / \\removedfragile variants used inside sectioning commands.

Resolving them by hand is where finalize passes go wrong: a \\removed{} block can
span several paragraphs and contain nested braces, \\ref{}, and math, so a regex
substitution silently eats the wrong closing brace. This does real brace matching.

Usage:
  redlines.py --list FILE...                 inventory, with line numbers
  redlines.py --accept FILE...               adopted text (keep added, drop removed)
  redlines.py --reject FILE...               pre-amendment text (drop added, keep removed)
  redlines.py --accept --in-place FILE...    rewrite the file

Without --in-place the result goes to stdout, so it is safe to inspect first.
Commented-out lines are left completely alone under --in-place: parked proposals and
the archive of retired chair positions live in comments and must not be resolved.
"""

import argparse
import re
import sys

MACROS = {
    "added": 1,
    "addedfragile": 1,
    "removed": 1,
    "removedfragile": 1,
    "changed": 2,
}

# What each macro resolves to, as indices into its argument list ([] means drop all).
ACCEPT = {
    "added": [0], "addedfragile": [0],
    "removed": [], "removedfragile": [],
    "changed": [0],
}
REJECT = {
    "added": [], "addedfragile": [],
    "removed": [0], "removedfragile": [0],
    "changed": [1],
}


def _escaped(text, i):
    """True if the character at i is escaped by an odd run of backslashes."""
    n = 0
    j = i - 1
    while j >= 0 and text[j] == "\\":
        n += 1
        j -= 1
    return n % 2 == 1


def read_group(text, i):
    """Read a brace group starting at text[i] == '{'. Returns (content, index_after)."""
    if i >= len(text) or text[i] != "{":
        raise ValueError("expected '{'")
    depth = 0
    start = i
    while i < len(text):
        c = text[i]
        if c in "{}" and not _escaped(text, i):
            if c == "{":
                depth += 1
            else:
                depth -= 1
                if depth == 0:
                    return text[start + 1:i], i + 1
        elif c == "%" and not _escaped(text, i):
            nl = text.find("\n", i)
            i = len(text) if nl == -1 else nl
            continue
        i += 1
    raise ValueError("unbalanced braces: group opened at offset %d never closed" % start)


def find_macros(text):
    """Yield (name, start, end, [args]) for every redline macro, outermost first."""
    pattern = re.compile(r"\\(" + "|".join(sorted(MACROS, key=len, reverse=True)) + r")\s*(?=\{)")
    out = []
    for m in pattern.finditer(text):
        if _escaped(text, m.start()):
            continue
        name = m.group(1)
        i = m.end()
        args = []
        try:
            for _ in range(MACROS[name]):
                while i < len(text) and text[i] in " \t\n":
                    i += 1
                arg, i = read_group(text, i)
                args.append(arg)
        except ValueError as exc:
            raise ValueError("\\%s at offset %d: %s" % (name, m.start(), exc))
        out.append((name, m.start(), i, args))
    return out


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def is_commented(text, offset):
    """True if offset sits after an unescaped % on its own line."""
    bol = text.rfind("\n", 0, offset) + 1
    for i in range(bol, offset):
        if text[i] == "%" and not _escaped(text, i):
            return True
    return False


def resolve(text, table, skip_commented=False):
    """Rewrite text, resolving redline macros per `table`. Innermost-first."""
    while True:
        found = find_macros(text)
        if skip_commented:
            found = [f for f in found if not is_commented(text, f[1])]
        if not found:
            return text
        # Resolve the last one so earlier offsets stay valid; repeat until none left.
        name, start, end, args = found[-1]
        keep = "".join(args[k] for k in table[name])
        text = text[:start] + keep + text[end:]


def cmd_list(paths):
    total = 0
    for path in paths:
        text = open(path, encoding="utf-8").read()
        try:
            found = find_macros(text)
        except ValueError as exc:
            print("%s: PARSE ERROR: %s" % (path, exc), file=sys.stderr)
            return 2
        if not found:
            print("%s: no redline macros" % path)
            continue
        print("%s: %d redline macro(s)" % (path, len(found)))
        for name, start, _end, args in found:
            state = "commented" if is_commented(text, start) else "live"
            preview = " | ".join(
                (a[:70] + "…") if len(a) > 70 else a for a in args
            ).replace("\n", " ")
            print("  line %-6d %-16s %-9s %s" % (line_of(text, start), "\\" + name, state, preview))
        total += len(found)
    if total:
        print("\n%d total. 'commented' entries are parked proposals or archived text;" % total)
        print("--in-place leaves them untouched.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--list", action="store_true", help="inventory macros, do not modify")
    mode.add_argument("--accept", action="store_true", help="resolve to the adopted text")
    mode.add_argument("--reject", action="store_true", help="resolve to the pre-amendment text")
    ap.add_argument("--in-place", action="store_true", help="rewrite files instead of printing")
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()

    if args.list:
        return cmd_list(args.files)

    table = ACCEPT if args.accept else REJECT
    for path in args.files:
        text = open(path, encoding="utf-8").read()
        try:
            out = resolve(text, table, skip_commented=True)
        except ValueError as exc:
            print("%s: PARSE ERROR: %s" % (path, exc), file=sys.stderr)
            return 2
        if args.in_place:
            if out != text:
                open(path, "w", encoding="utf-8").write(out)
                print("rewrote %s" % path)
            else:
                print("unchanged %s" % path)
        else:
            sys.stdout.write(out)
    if args.in_place and args.accept:
        print("\nReminder: --accept DELETES removed text. Severable units — chair and")
        print("officer positions, committees — should be commented out instead, per the")
        print("skill's finalize rules. Check the diff for any that need restoring as")
        print("comments before committing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
