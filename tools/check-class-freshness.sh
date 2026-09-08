#!/usr/bin/env bash
# Is TBP-C-B's vendored bylaws.cls still the class this skill documents?
#
# Three repositories are in play and two of them hold a copy of the same file:
#
#   tbpmig/latex-c-b   the class, canonical
#   tbpmig/TBP-C-B     a vendored copy, which is what MI-G's documents actually build against
#   this repository    references/latex-conventions.md, which documents the class's behaviour
#
# If the vendored copy drifts, the skill documents a class nobody is using. Worse, the
# drift is silent: LaTeX will happily build against whatever bylaws.cls it finds.
#
# "Differs" is not a useful verdict on its own, because the two directions mean
# opposite things:
#
#   BEHIND    the vendored copy matches an older commit of the class. Routine — someone
#             released the class and MI-G has not pulled yet. Pull when convenient.
#
#   DIVERGED  the vendored copy matches no version the class repository has ever had.
#             Someone patched MI-G's copy directly. This is exactly how the 2014
#             upstream ended up stranded with a locally-patched fork nobody could
#             benefit from, and it is the case worth interrupting someone over.
#
# Exit: 0 in sync, 1 behind, 2 diverged, 3 could not check.

set -uo pipefail

CLASS_REPO="${CLASS_REPO:-https://github.com/tbpmig/latex-c-b.git}"
DOCS_REPO="${DOCS_REPO:-https://github.com/tbpmig/TBP-C-B.git}"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

say() { printf '%s\n' "$*"; }

# The class repository needs full history: identifying "behind" means asking whether the
# vendored copy matches any version this file has ever had.
git clone --quiet "$CLASS_REPO" "$WORK/class" 2>/dev/null || {
  say "could not clone the class repository ($CLASS_REPO)"; exit 3; }
git clone --quiet --depth 1 "$DOCS_REPO" "$WORK/docs" 2>/dev/null || {
  say "could not clone the documents repository ($DOCS_REPO)"; exit 3; }

CLASS_FILE="$WORK/class/bylaws.cls"
DOCS_FILE="$WORK/docs/bylaws.cls"
for f in "$CLASS_FILE" "$DOCS_FILE"; do
  [ -f "$f" ] || { say "bylaws.cls not found at $f"; exit 3; }
done

version_of() { grep -m1 'ProvidesClass' "$1" | sed 's/.*\[\(.*\)\].*/\1/' ; }
CLASS_V=$(version_of "$CLASS_FILE"); DOCS_V=$(version_of "$DOCS_FILE")

# git hash-object gives the same blob id git itself uses, so historical versions can be
# compared without checking each one out.
CLASS_H=$(git -C "$WORK/class" hash-object bylaws.cls)
DOCS_H=$(git -C "$WORK/docs" hash-object bylaws.cls)

say "class repository : $(git -C "$WORK/class" log --oneline -1)"
say "                   declares: $CLASS_V"
say "documents repo   : $(git -C "$WORK/docs" log --oneline -1)"
say "                   declares: $DOCS_V"
say ""

if [ "$CLASS_H" = "$DOCS_H" ]; then
  say "IN SYNC — TBP-C-B's vendored bylaws.cls is byte-identical to the class repository."
  exit 0
fi

# Has the vendored copy ever been a released version of the class?
MATCH=""
while read -r sha; do
  [ -n "$sha" ] || continue
  blob=$(git -C "$WORK/class" rev-parse "$sha:bylaws.cls" 2>/dev/null) || continue
  if [ "$blob" = "$DOCS_H" ]; then MATCH="$sha"; break; fi
done < <(git -C "$WORK/class" log --format=%H -- bylaws.cls)

say "DRIFT — the vendored copy and the class repository differ."
say ""
say "what changed (class repository -> vendored copy):"
diff -u "$CLASS_FILE" "$DOCS_FILE" | sed -n '3,40p' | sed 's/^/    /'
say ""

if [ -n "$MATCH" ]; then
  say "VERDICT: BEHIND."
  say "TBP-C-B's copy matches class commit $(git -C "$WORK/class" log --oneline -1 "$MATCH")."
  say "The class has moved on since. Copy bylaws.cls from the class repository into"
  say "TBP-C-B when convenient, rebuild all three documents, and confirm the rendered"
  say "text is unchanged before committing — a class change can move type."
  exit 1
fi

say "VERDICT: DIVERGED."
say "TBP-C-B's copy matches no version the class repository has ever had, so it has been"
say "edited directly. Whatever that change was, the class repository does not have it and"
say "no other chapter can benefit from it."
say ""
say "Port the change into tbpmig/latex-c-b, release it, then re-vendor into TBP-C-B."
say "Leaving it here is how the 2014 upstream ended up stranded."
exit 2
