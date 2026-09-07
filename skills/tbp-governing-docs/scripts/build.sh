#!/usr/bin/env bash
# Build a TBP governing document.
#
# Uses latexmk deliberately. Repeated `pdflatex` runs never converge changebar's
# .cb/.cb2 files: the log keeps saying "Changebar info has changed. Rerun to get the
# bars right" and the resulting PDF has correct red/green text but NO margin change
# bars — which looks close enough to correct that it can reach a vote unnoticed.
#
# Usage:
#   build.sh <main.tex> [--proposal|--final] [--clean] [--outdir DIR]
#
#   --proposal   switch the class option to `proposal` before building: DRAFT
#                watermark, DRAFT running header, "Draft revised: <today>". Correct
#                for anything going to a vote.
#   --final      switch to `final`: prints adoption/revision dates instead. Only
#                after a change is adopted AND the amendment dates are updated.
#   --clean      latexmk -C first, for when aux files are stale or the TOC is wrong.
#   --outdir     build in a copy under DIR instead of in place. Useful when the repo
#                is in Dropbox and you would rather not sync the aux-file churn.
#
# The class-option switch is written back into the main .tex, so it shows up in the
# diff. That is intentional — proposal/final is a substantive property of the
# document, not a build flag, and it belongs in the change ledger.

set -uo pipefail

MAIN=""; MODE=""; CLEAN=0; OUTDIR=""
while [ $# -gt 0 ]; do
  case "$1" in
    --proposal) MODE=proposal ;;
    --final)    MODE=final ;;
    --clean)    CLEAN=1 ;;
    --outdir)   shift; OUTDIR="${1:-}" ;;
    -h|--help)  sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*)         echo "build.sh: unknown option $1" >&2; exit 2 ;;
    *)          MAIN="$1" ;;
  esac
  shift
done

[ -n "$MAIN" ] || { echo "build.sh: need a main .tex file" >&2; exit 2; }
[ -f "$MAIN" ] || { echo "build.sh: no such file: $MAIN" >&2
  echo "  If this repo is in Dropbox, a file that is listed but unreadable is an" >&2
  echo "  online-only placeholder. Right-click the repo in Finder -> Make Available Offline." >&2
  exit 2; }

command -v latexmk >/dev/null || {
  echo "build.sh: latexmk not found. Run scripts/check_env.sh --install." >&2; exit 2; }

MAIN=$(cd "$(dirname "$MAIN")" && pwd)/$(basename "$MAIN")
DOCDIR=$(dirname "$MAIN")
REPO=$(dirname "$DOCDIR")

if [ -n "$OUTDIR" ]; then
  mkdir -p "$OUTDIR"
  # The class lives one level above the document dir and is referenced as ../bylaws.
  cp -R "$REPO"/. "$OUTDIR"/ 2>/dev/null || true
  DOCDIR="$OUTDIR/$(basename "$DOCDIR")"
  MAIN="$DOCDIR/$(basename "$MAIN")"
  echo "building in scratch copy: $DOCDIR"
fi

if [ -n "$MODE" ]; then
  before=$(head -1 "$MAIN")
  perl -0pi -e "s/(\\\\documentclass\[[^]]*?)\b(proposal|final)\b/\$1$MODE/" "$MAIN"
  after=$(head -1 "$MAIN")
  if [ "$before" = "$after" ]; then
    echo "note: class option already '$MODE' (or no proposal/final option present)"
  else
    echo "class option -> $MODE"
    echo "  was: $before"
    echo "  now: $after"
    echo "  This lands in the diff on purpose; add it to the change ledger."
  fi
fi

cd "$DOCDIR" || exit 2
BASE=$(basename "$MAIN" .tex)

[ "$CLEAN" -eq 1 ] && latexmk -C "$BASE" >/dev/null 2>&1

LOG=$(mktemp)
# -f keeps going past recoverable errors so the log shows everything wrong at once,
# rather than one error per build round-trip.
latexmk -pdf -f -interaction=nonstopmode "$BASE.tex" >"$LOG" 2>&1
STATUS=$?

# Which log to believe.
#
# This document needs FOUR pdflatex passes from a clean tree: references resolve on
# pass 2, and changebar's margin bars only converge on pass 4. latexmk handles that
# and $LOG is its stdout, so it concatenates every pass — including pass 1, which
# reports 68 undefined references and a page count 4 pages short purely because the
# .aux and .toc do not exist yet. None of that is a defect and none of it should ever
# reach the user.
#
# "$BASE.log" on disk is written by the LAST pdflatex run only, so it is the honest
# view. Diagnostics below read it, not $LOG.
FINAL="$BASE.log"
[ -f "$FINAL" ] || FINAL="$LOG"

echo
if grep -qE '^!' "$FINAL"; then
  echo "=== LaTeX errors (final pass) ==="
  grep -E -A3 '^!' "$FINAL" | head -40
  echo
  echo "If these mention \\ttl@assign@i, \\contentsline, or 'missing \\item', the cause"
  echo "is almost certainly a non-fragile \\added/\\removed/\\changed inside a \\section{},"
  echo "\\chapter{}, or \\item{} title. Use \\addedfragile / \\removedfragile there."
  echo
fi

# Unresolved references are only meaningful after the final pass. Reading them from
# latexmk's stdout would report every reference in the document as broken on any
# build from a clean tree.
if grep -qE "Reference .* undefined" "$FINAL" || grep -q 'failed to resolve' "$LOG"; then
  echo "=== Unresolved references (final pass) ==="
  grep -oE "Reference \`[^']+' on page [0-9]+ undefined" "$FINAL" | sort -u | head -10
  grep -E 'failed to resolve' "$LOG" | tail -1
  echo "A \\ref to a deleted \\label renders as ?? in the PDF. scripts/audit.py names"
  echo "which label went missing and what still points at it."
  echo
fi

# changebar not converging leaves the PDF with correct colours and NO margin bars,
# which looks plausible enough to circulate by mistake.
if grep -q 'Changebar info has changed' "$FINAL"; then
  echo "=== Change bars did not converge ==="
  echo "The final pass still asked for a rerun, so the margin bars in this PDF are"
  echo "unreliable even though the coloured text is correct. Re-run the build; if it"
  echo "persists, build with --clean to discard stale .cb/.cb2 files."
  echo
fi

if [ "$STATUS" -eq 0 ] && [ -f "$BASE.pdf" ]; then
  PAGES=$(grep -oE 'Output written on .* \([0-9]+ pages' "$LOG" | grep -oE '[0-9]+ pages' | tail -1)
  echo "OK: $DOCDIR/$BASE.pdf ${PAGES:+($PAGES)}"
  grep -qE '^\\documentclass\[[^]]*proposal' "$BASE.tex" \
    && echo "    built as PROPOSAL — DRAFT watermark and header present" \
    || echo "    built as FINAL — no DRAFT marking. Do not circulate this for a vote."
  echo "    full log: $LOG"
  exit 0
fi

echo "BUILD FAILED (latexmk exit $STATUS). Full log: $LOG"
exit 1
