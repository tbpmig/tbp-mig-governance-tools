#!/usr/bin/env python3
"""Audit a working-tree diff in the TBP-C-B repo against a sanctioned change list.

This exists because "I only made the change you asked for" is easy to believe and
hard to verify by eye. The script cannot judge intent — that is the reviewer's job —
but it can mechanically surface the things that go wrong silently:

  * files changed that were never sanctioned
  * hunks that are only whitespace, or only a re-split of unchanged words
  * blank lines added between prose lines, which end a TeX paragraph and change the
    render while leaving every word untouched
  * unbalanced braces introduced by a \\removed{} that swallowed a closing brace
  * \\label{}s deleted while \\ref{}s to them survive (renders as ?? in the PDF)
  * a redline-macro count that does not match what was proposed
  * and, most importantly, the ADOPTED TEXT DELTA: what the governing document would
    actually say if this proposal passed, versus what it says today. Markup can be
    correct in the diff and still leave the adopted text saying the wrong thing.

Usage:
  audit.py --repo /path/to/TBP-C-B --allow bylaws/appendices.tex [--allow ...]
  audit.py --repo . --allow 'bylaws/*.tex' --against HEAD

Exit status is 1 if any hazard was flagged, 0 if clean. A clean exit does not mean
the change is right — it means nothing mechanically detectable is wrong.
"""

import argparse
import difflib
import fnmatch
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from redlines import find_macros, resolve, ACCEPT, is_commented
except ImportError:
    print("audit.py: cannot import redlines.py; keep both scripts together", file=sys.stderr)
    sys.exit(2)

RESET, BOLD, RED, YELLOW, GREEN, DIM = (
    ("\033[0m", "\033[1m", "\033[31m", "\033[33m", "\033[32m", "\033[2m")
    if sys.stdout.isatty() else ("", "", "", "", "", "")
)

findings = []


def flag(level, msg):
    findings.append((level, msg))


def git(repo, *args, check=True):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), p.stderr.strip()))
    return p.stdout


def changed_files(repo, against):
    out = git(repo, "diff", "--name-status", against)
    rows = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            rows.append((parts[0], parts[-1]))
    return rows


def blob_at(repo, rev, path):
    p = subprocess.run(["git", "-C", repo, "show", "%s:%s" % (rev, path)],
                       capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None


def words(text):
    return re.findall(r"\S+", text)


def check_scope(rows, allow):
    for status, path in rows:
        if not any(fnmatch.fnmatch(path, pat) for pat in allow):
            flag("ERROR", "%s changed but is not in the sanctioned file list. "
                          "Either revert it or add it to the ledger." % path)


def check_whitespace_and_reflow(repo, against, path):
    """Flag hunks whose content is unchanged once whitespace is normalized."""
    out = git(repo, "diff", "--unified=0", against, "--", path)
    hunk, minus, plus = None, [], []

    def finish():
        if not hunk:
            return
        a, b = "\n".join(minus), "\n".join(plus)
        if a.strip() == b.strip() and a != b:
            flag("WARN", "%s %s: whitespace-only change; revert unless it was "
                         "sanctioned." % (path, hunk))
        elif words(a) == words(b) and a != b:
            flag("WARN", "%s %s: lines re-split or joined without changing any word. "
                         "Line style is a source convention that renders identically, so "
                         "changing it during an amendment is invisible in the PDF and "
                         "enormous in the diff; revert unless sanctioned." % (path, hunk))

    for line in out.splitlines():
        if line.startswith("@@"):
            finish()
            m = re.match(r"@@ [^@]+ @@", line)
            hunk, minus, plus = (m.group(0) if m else line), [], []
        elif line.startswith("-") and not line.startswith("---"):
            minus.append(line[1:])
        elif line.startswith("+") and not line.startswith("+++"):
            plus.append(line[1:])
    finish()


def check_braces(path, text):
    """Brace balance over live code only.

    Comments are skipped: this source carries a lot of commented-out markup, much of
    it deliberately truncated mid-macro, so counting braces inside comments produces
    confident nonsense.
    """
    depth, line, i, n = 0, 1, 0, len(text)
    while i < n:
        c = text[i]
        if c == "\\" and i + 1 < n:      # escaped char: \{ \} \% and friends
            i += 2
            continue
        if c == "%":                      # comment runs to end of line
            nl = text.find("\n", i)
            if nl == -1:
                break
            line += 1
            i = nl + 1
            continue
        if c == "\n":
            line += 1
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth < 0:
                flag("ERROR", "%s line %d: closing brace with no opener. A \\removed{} "
                              "or \\changed{}{} probably captured the wrong extent." % (path, line))
                return
        i += 1
    if depth:
        flag("ERROR", "%s: %d brace(s) left open at end of file. A redline macro likely "
                      "swallowed a closing brace." % (path, depth))


BLOCK_START = re.compile(r"^\\(section|subsection|subsubsection|chapter|part|item|itemnotoc|"
                         r"begin|end|input|appendix|newcommand|renewcommand|label)")


def _is_prose(line):
    """True for a line of running text — not a macro that opens or closes a block."""
    t = line.strip()
    return bool(t) and not t.startswith("%") and not BLOCK_START.match(t)


def check_blank_lines(repo, against, path):
    """Flag blank lines added or removed *between two prose lines*.

    In TeX a blank line ends the paragraph. Since the one-sentence-per-line
    conversion, prose sits on consecutive lines, so a stray blank line inserted while
    editing splits a paragraph — which is invisible in the diff's intent but plainly
    visible in the rendered PDF. The reverse, deleting a blank line, silently merges
    two paragraphs. Neither is caught by the reflow or whitespace checks, because the
    words are unchanged and the line content differs.
    """
    try:
        new_lines = open(os.path.join(repo, path), encoding="utf-8",
                         errors="replace").read().split("\n")
    except OSError:
        return
    out = git(repo, "diff", "--unified=0", against, "--", path)
    added_blank = removed_blank = 0
    for line in out.splitlines():
        if line.startswith("+") and not line.startswith("+++") and not line[1:].strip():
            added_blank += 1
        elif line.startswith("-") and not line.startswith("---") and not line[1:].strip():
            removed_blank += 1
    if not (added_blank or removed_blank):
        return

    risky = []
    for i, line in enumerate(new_lines):
        if line.strip():
            continue
        # Comment lines are invisible to TeX's paragraph logic, so look past them.
        def _neighbour(rng):
            for j in rng:
                t = new_lines[j].strip()
                if t and not t.startswith("%"):
                    return new_lines[j]
            return ""
        prev_ = _neighbour(range(i - 1, -1, -1))
        next_ = _neighbour(range(i + 1, len(new_lines)))
        if _is_prose(prev_) and _is_prose(next_):
            risky.append(i + 1)

    if added_blank and risky:
        flag("ERROR", "%s: %d blank line(s) added or moved, and %d blank line(s) now sit "
                      "between two prose lines (line%s %s). A blank line ends the paragraph "
                      "in TeX, so this changes the rendered document even though no words "
                      "changed. Verify with pdftotext before and after."
                      % (path, added_blank, len(risky), "" if len(risky) == 1 else "s",
                         ", ".join(str(r) for r in risky[:6])))
    elif added_blank or removed_blank:
        flag("WARN", "%s: %d blank line(s) added, %d removed. Blank lines end paragraphs "
                     "in TeX; confirm the render is unchanged if this was not a sanctioned "
                     "structural edit." % (path, added_blank, removed_blank))


def check_labels(repo, against, rows, allow_paths):
    """Deleted labels that something still references render as ?? in the PDF."""
    old_labels, new_labels, new_refs = set(), set(), {}
    lab = re.compile(r"\\label\{([^}]*)\}")
    ref = re.compile(r"\\(?:ref|autoref|pageref|nameref)\{([^}]*)\}")

    for _status, path in rows:
        if not path.endswith(".tex"):
            continue
        old = blob_at(repo, against, path) or ""
        old_labels |= set(lab.findall(old))

    for root, _dirs, files in os.walk(repo):
        if ".git" in root:
            continue
        for fn in files:
            if not fn.endswith(".tex"):
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, repo)
            try:
                text = open(full, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            new_labels |= set(lab.findall(text))
            for r in ref.findall(text):
                new_refs.setdefault(r, []).append(rel)

    for gone in sorted((old_labels - new_labels) & set(new_refs)):
        where = ", ".join(sorted(set(new_refs[gone])))
        flag("ERROR", "\\label{%s} was deleted but is still referenced in %s. The PDF "
                      "will show ?? there." % (gone, where))


def check_empty_redlines(path, text):
    """An empty \\added{} or \\removed{} is almost always an under-wrapped edit.

    Since the one-sentence-per-line conversion a severable unit spans several source
    lines, so wrapping "the body" means one macro per sentence line. Wrapping only the
    title and leaving \\removed{} empty compiles cleanly, renders plausibly, and leaves
    the text it was supposed to strike fully operative.
    """
    try:
        found = find_macros(text)
    except ValueError:
        return                      # check_redlines reports the parse failure
    for name, start, _end, args in found:
        if is_commented(text, start):
            continue
        if any(not a.strip() for a in args):
            flag("ERROR", "%s line %d: \\%s has an empty argument. The text meant to be "
                          "marked is probably still operative on a following line — in the "
                          "converted style each sentence needs its own macro."
                          % (path, text.count("\n", 0, start) + 1, name))


def check_redlines(path, old_text, new_text):
    def summary(text):
        try:
            found = find_macros(text)
        except ValueError as exc:
            flag("ERROR", "%s: redline macros do not parse: %s" % (path, exc))
            return None
        live = [f for f in found if not is_commented(text, f[1])]
        counts = {}
        for name, start, _e, _a in live:
            counts[name] = counts.get(name, 0) + 1
        return counts

    before, after = summary(old_text or ""), summary(new_text)
    if before is None or after is None:
        return
    delta = {k: after.get(k, 0) - before.get(k, 0)
             for k in set(before) | set(after) if after.get(k, 0) != before.get(k, 0)}
    if delta:
        parts = ", ".join("%s%+d" % ("\\" + k, v) for k, v in sorted(delta.items()))
        flag("INFO", "%s: live redline macros changed: %s. Confirm this matches the "
                     "number of changes in the ledger." % (path, parts))


def adopted_delta(repo, against, rows, allow_paths):
    """Show what the adopted text becomes, with all redline markup resolved."""
    chunks = []
    for _status, path in rows:
        if not path.endswith(".tex"):
            continue
        old = blob_at(repo, against, path)
        try:
            new = open(os.path.join(repo, path), encoding="utf-8").read()
        except OSError:
            new = ""
        try:
            old_adopted = resolve(old or "", ACCEPT, skip_commented=True)
            new_adopted = resolve(new, ACCEPT, skip_commented=True)
        except ValueError as exc:
            flag("ERROR", "%s: cannot resolve redlines for adopted-text check: %s" % (path, exc))
            continue
        if old_adopted == new_adopted:
            chunks.append("%s: adopted text identical (markup-only change)" % path)
            continue
        diff = list(difflib.unified_diff(
            old_adopted.splitlines(), new_adopted.splitlines(),
            fromfile="%s (adopted, before)" % path,
            tofile="%s (adopted, if this passes)" % path,
            lineterm="", n=1))
        chunks.append("\n".join(diff))
    return chunks


AUTHORITY_FILES = {
    "constitution/amendments.tex", "constitution/government.tex",
    "bylaws/amendment.tex", "bylaws/government.tex", "bylaws/records.tex",
}


def check_authority(repo, rows):
    """Warn when an edit touches a clause that defines who may amend what.

    references/amendment-authority.md is a cache of these clauses. Editing one can
    silently invalidate it, and a governance flag quoted from a stale cache is a
    confident false statement about who may adopt something.
    """
    touched = sorted({p for _s, p in rows} & AUTHORITY_FILES)
    if touched:
        flag("WARN", "authority-defining file(s) edited: %s. This may change who may "
                     "amend what, and may invalidate quotes in the summary. Run "
                     "scripts/authority.py --repo . --check to see which quoted clauses "
                     "drifted, tell the user which entries move, and rebuild "
                     "references/amendment-authority.md before quoting it."
                     % ", ".join(touched))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True, help="path to the TBP-C-B repository")
    ap.add_argument("--allow", action="append", default=[],
                    help="repo-relative path or glob the ledger sanctioned; repeatable")
    ap.add_argument("--against", default="HEAD", help="revision to diff against (default HEAD)")
    ap.add_argument("--no-diff", action="store_true", help="skip printing the raw diff")
    args = ap.parse_args()

    repo = os.path.abspath(args.repo)
    try:
        rows = changed_files(repo, args.against)
    except RuntimeError as exc:
        print("%sgit is not usable here%s: %s" % (RED, RESET, exc), file=sys.stderr)
        print("If this repo is inside Dropbox, 'Resource deadlock avoided' means the "
              "sync layer, not a broken repository. Run git from a local terminal.",
              file=sys.stderr)
        return 2

    if not rows:
        print("No changes against %s. Nothing to audit." % args.against)
        return 0

    print("%sAUDIT: files changed against %s%s" % (BOLD, args.against, RESET))
    for status, path in rows:
        print("  %-3s %s" % (status, path))

    if args.allow:
        check_scope(rows, args.allow)
    else:
        flag("WARN", "No --allow given, so scope was not checked. Pass the ledger's "
                     "files to make this audit meaningful.")

    for _status, path in rows:
        if not path.endswith(".tex"):
            continue
        check_whitespace_and_reflow(repo, args.against, path)
        check_blank_lines(repo, args.against, path)
        full = os.path.join(repo, path)
        if os.path.exists(full):
            text = open(full, encoding="utf-8", errors="replace").read()
            check_braces(path, text)
            check_redlines(path, blob_at(repo, args.against, path), text)
            check_empty_redlines(path, text)

    check_labels(repo, args.against, rows, args.allow)
    check_authority(repo, rows)

    if not args.no_diff:
        print("\n%sAUDIT: raw diff%s" % (BOLD, RESET))
        print(git(repo, "diff", args.against) or "(empty)")

    print("\n%sAUDIT: adopted text delta%s" % (BOLD, RESET))
    print(DIM + "What the governing document would say if this passed. Read this even "
                "when the diff looks right." + RESET)
    for chunk in adopted_delta(repo, args.against, rows, args.allow):
        print(chunk)

    print("\n%sAUDIT: findings%s" % (BOLD, RESET))
    if not findings:
        print("%sNo mechanical hazards found.%s Scope and intent still need your review: "
              "match every hunk above to a ledger row." % (GREEN, RESET))
        return 0
    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    colour = {"ERROR": RED, "WARN": YELLOW, "INFO": DIM}
    for level, msg in sorted(findings, key=lambda f: order[f[0]]):
        print("  %s%-5s%s %s" % (colour[level], level, RESET, msg))
    return 1 if any(l in ("ERROR", "WARN") for l, _ in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
