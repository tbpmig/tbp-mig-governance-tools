#!/usr/bin/env python3
"""Print the amendment-authority clauses as they currently stand in the repository.

`references/amendment-authority.md` is a *derived* summary of clauses that are
themselves amendable. It can go stale in two ways: someone amends an authority clause
outside this skill, or the very amendment you are drafting changes one. Either way a
flag quoted from a stale table is a confident false statement about who may adopt
something — worse than saying nothing.

So: run this before quoting the table, and again after any edit that touches one of
the source locations below. It reads the tree, not the summary.

Usage:
  authority.py --repo /path/to/TBP-C-B            print every authority clause
  authority.py --repo . --check                   verify the shipped summary's verbatim
                                                  quotes still match the tree; exit 1 if
                                                  any has gone stale
  authority.py --repo . --touched bylaws/amendment.tex [...]
        exit 1 if any named file is authority-defining, so a diff audit can gate on it
"""

import argparse
import os
import re
import sys

# (file, human label, regex selecting the clause text)
CLAUSES = [
    ("constitution/amendments.tex", "Constitution — Proposal / Notice / Adoption / Review",
     r"\\section\{(?:Proposal|Notice|Adoption|Review|Ratification)\}.*?(?=\\section|\\chapter|\Z)"),
    ("constitution/government.tex", "Constitution — enacting and amending Bylaws",
     r"\\item\{Bylaws\}.*?(?=\\item|\\end\{enumsubsection\}|\Z)"),
    ("bylaws/amendment.tex", "Bylaws — Enactment / Amendment / Appendix Amendment",
     r"\\section\{(?:Enactment|Amendment|Appendix Amendment)\}.*?(?=\\section|\Z)"),
    ("bylaws/government.tex", "Bylaws — ad hoc officer creation",
     r"\\item\*?\{Creation of Ad Hoc Officer Positions\}.*?(?=\\item\*?\{|\Z)"),
    ("bylaws/government.tex", "Bylaws — ad hoc committee creation",
     r"\\item\{Ad Hoc Committees\}.*?(?=\\item\{|\\end\{enumsubsection\}|\Z)"),
    ("bylaws/government.tex", "Bylaws — chair creation / dissolution",
     r"\\item\{(?:Creation|Dissolution and Removal)\}.*?(?=\\item\{|\\end\{enumsubsection\}|\Z)"),
    ("bylaws/records.tex", "Bylaws — financial policy approval authority",
     r"\\section\{Spending Authority\}.*?(?=\\section|\Z)"),
]

AUTHORITY_FILES = sorted({c[0] for c in CLAUSES})


def strip_comments(text):
    out = []
    for line in text.split("\n"):
        i, buf = 0, ""
        while i < len(line):
            if line[i] == "\\" and i + 1 < len(line):
                buf += line[i:i + 2]; i += 2; continue
            if line[i] == "%":
                break
            buf += line[i]; i += 1
        out.append(buf)
    return "\n".join(out)


def extract(repo):
    found, missing = [], []
    for path, label, pattern in CLAUSES:
        full = os.path.join(repo, path)
        if not os.path.exists(full):
            missing.append((path, label, "file not found (Dropbox placeholder?)"))
            continue
        body = strip_comments(open(full, encoding="utf-8", errors="replace").read())
        hits = [re.sub(r"\s+", " ", m.group(0)).strip()
                for m in re.finditer(pattern, body, re.S)]
        if hits:
            found.append((path, label, hits))
        else:
            missing.append((path, label, "clause not matched — it may have been retitled or moved"))
    return found, missing


# --- Comparing the shipped summary against the tree -------------------------
#
# references/amendment-authority.md quotes these clauses verbatim so a wrong-body
# flag can cite exact adopted text. Those clauses are themselves amendable, so the
# quotes go stale silently — and a stale quote is worse than no quote: it cites
# repealed wording with full confidence. --check compares the two.
#
# The reference deliberately renders some LaTeX as prose for readability
# (\nicefrac{5}{7} as "5/7", \ref{...} dropped), so both sides are normalised
# through the same filter before comparison. Getting this wrong in either
# direction produces confident nonsense, so the normaliser is shared, not
# duplicated.

REF_RELATIVE = os.path.join("..", "references", "amendment-authority.md")


def normalise(text):
    """Reduce LaTeX source and transcribed prose to a comparable common form."""
    text = strip_comments(text)
    text = re.sub(r"\\href\{[^}]*\}\{([^}]*)\}", r"\1", text)   # keep the link text
    text = re.sub(r"\\nicefrac\{([^}]*)\}\{([^}]*)\}", r"\1/\2", text)
    text = re.sub(r"\$?\\frac\{([^}]*)\}\{([^}]*)\}\$?", r"\1/\2", text)
    text = re.sub(r"\\(?:ref|label|autoref|pageref|nameref)\{[^}]*\}", "", text)
    text = text.replace("~", " ")
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = re.sub(r"\\[a-zA-Z@]+\*?", "", text)                    # any remaining macro
    text = text.replace("{", "").replace("}", "").replace("$", "")
    return re.sub(r"\s+", " ", text).strip()


def reference_quotes(ref_path):
    """Yield (line_number, quoted_text) for each verbatim segment in the reference.

    Blockquote lines are joined into contiguous blocks. A bold lead-in
    (`**Creation.**`) is an editorial label rather than source text and splits the
    block; `[bracketed]` inserts are editorial too and are dropped.
    """
    out, cur, start = [], [], None
    lines = open(ref_path, encoding="utf-8", errors="replace").read().split("\n")
    for i, line in enumerate(lines, 1):
        if line.startswith(">"):
            if not cur:
                start = i
            cur.append(line[1:].strip())
        elif cur:
            out.append((start, " ".join(cur)))
            cur = []
    if cur:
        out.append((start, " ".join(cur)))

    segments = []
    for lineno, block in out:
        for seg in re.split(r"\*\*[^*]+\*\*", block):
            seg = re.sub(r"\[[^\]]*\]", "", seg)
            if len(normalise(seg)) >= 45:          # ignore fragments too short to pin
                segments.append((lineno, seg))
    return segments


def diverge(probe, tree):
    """Locate where a quote stops matching the tree, and show both continuations.

    Printing the whole quote twice tells the reader nothing. What they need is the
    first point of difference and what the tree says there instead.
    """
    lo, hi = 0, len(probe)
    while lo < hi:                                  # longest prefix still present
        mid = (lo + hi + 1) // 2
        if probe[:mid] in tree:
            lo = mid
        else:
            hi = mid - 1
    at = lo
    ref_tail = probe[at:at + 60] + ("\u2026" if len(probe) > at + 60 else "")
    # A short prefix will anchor almost anywhere and produce a confidently wrong
    # "tree says" line, so demand enough context to be sure it is the same passage.
    anchor = probe[max(0, at - 45):at]
    if at < 20 or tree.count(anchor) != 1:
        tree_tail = ("(diverges too early to locate \u2014 the clause was probably "
                     "reworded, retitled or moved)")
    else:
        pos = tree.find(anchor) + len(anchor)
        tail = tree[pos:pos + 60]
        tail = tail.split("\u00b6\u00b6")[0].rstrip()      # stop at the file boundary
        tree_tail = tail + ("\u2026" if len(tree[pos:pos + 60]) == 60 and "\u00b6" not in tree[pos:pos + 60] else "")
    return at, ref_tail, tree_tail



def cmd_check(repo, ref_path):
    if not os.path.exists(ref_path):
        print("check: cannot find %s" % ref_path, file=sys.stderr)
        return 2
    corpus = []
    for root, _dirs, files in os.walk(repo):
        if ".git" in root:
            continue
        for fn in sorted(files):
            if fn.endswith(".tex"):
                corpus.append(open(os.path.join(root, fn), encoding="utf-8",
                                   errors="replace").read())
                # A separator no quote can span, so a "tree says" continuation cannot
                # bleed from the end of one file into the start of the next.
                corpus.append(" \u00b6\u00b6 ")
    if not corpus:
        print("check: no .tex files under %s — is this the repository?" % repo, file=sys.stderr)
        return 2
    tree = normalise(" ".join(corpus))

    # Quotes matching is not sufficient. A clause can keep its wording while being
    # retitled or moved to another file, which leaves every quote intact and every
    # citation in the reference wrong. Locate each clause by its CLAUSES pattern too.
    _found, missing = extract(repo)
    if missing:
        print("CLAUSE(S) COULD NOT BE LOCATED IN THE TREE:\n")
        for path, label, why in missing:
            print("  %-38s %s" % (path, label))
            print("      %s" % why)
        print("\nThe wording may be unchanged, but the citation is not. A section was")
        print("renamed or moved: update the CLAUSES table in this script, and the file and")
        print("section names quoted in the reference, before relying on either.")
        return 2

    segments = reference_quotes(ref_path)
    stale = []
    for lineno, seg in segments:
        q = normalise(seg)
        # An ellipsis marks an elided quote: check the pieces around it instead.
        parts = [p.strip() for p in re.split(r"\.\.\.|\u2026", q) if len(p.strip()) >= 30]
        probes = parts if parts else [q]
        if not all(p in tree for p in probes):
            stale.append((lineno, q, [p for p in probes if p not in tree]))

    print("Checked %d verbatim quote(s) in %s" % (len(segments), os.path.basename(ref_path)))
    if not stale:
        print("All match the current tree.")
        return 0
    print("\n%d QUOTE(S) NO LONGER MATCH THE TREE:\n" % len(stale))
    for lineno, q, misses in stale:
        print("  %s line %d" % (os.path.basename(ref_path), lineno))
        for m in misses:
            at, ref_tail, tree_tail = diverge(m, tree)
            print("    matches for %d chars, then diverges:" % at)
            print("      \u2026%s" % m[max(0, at - 45):at])
            print("      reference: %s" % ref_tail)
            print("      tree:      %s" % tree_tail)
        print()
    print("The tree is authoritative. Update the reference to match, and tell the user")
    print("which entries moved — a changed amendment clause is news, not a typo fix.")
    return 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--check", action="store_true",
                    help="compare the shipped summary's verbatim quotes against the tree")
    ap.add_argument("--reference", default=None,
                    help="path to amendment-authority.md (default: alongside this script)")
    ap.add_argument("--touched", nargs="*", default=None,
                    help="repo-relative paths; exit 1 if any is authority-defining")
    args = ap.parse_args()
    repo = os.path.abspath(args.repo)

    if args.touched is not None:
        hits = [p for p in args.touched if p in AUTHORITY_FILES]
        if hits:
            print("AUTHORITY-DEFINING FILES TOUCHED:")
            for h in hits:
                print("  %s" % h)
            print("\nThis edit may change who may adopt what. Re-read the clauses")
            print("(authority.py --repo %s), tell the user which entries move, and" % args.repo)
            print("rebuild references/amendment-authority.md before relying on it.")
            return 1
        print("No authority-defining file touched; the summary table still applies.")
        return 0

    if args.check:
        ref = args.reference or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                             REF_RELATIVE)
        return cmd_check(repo, os.path.normpath(ref))

    found, missing = extract(repo)
    for path, label, hits in found:
        print("=" * 78)
        print("%s\n  [%s]" % (label, path))
        print("=" * 78)
        for h in hits:
            print("  " + h[:1400] + ("…" if len(h) > 1400 else ""))
            print()
    if missing:
        print("!" * 78)
        print("COULD NOT READ THESE CLAUSES — do not quote the summary for them:")
        for path, label, why in missing:
            print("  %-38s %s  (%s)" % (path, label, why))
        print("!" * 78)
        return 2
    print("All %d authority clauses read from the tree." % len(found))
    print("To verify the shipped summary still quotes them correctly, run the same")
    print("command with --check rather than comparing by eye.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
