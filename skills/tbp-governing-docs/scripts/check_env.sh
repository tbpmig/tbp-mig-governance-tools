#!/usr/bin/env bash
# Check (and optionally install) the toolchain needed to build the TBP governing
# documents. Reports only by default — installing a second TeX distribution beside a
# working one is the main way this goes wrong, so the default is to look first.
#
# Usage:
#   check_env.sh              report what is present and what is missing
#   check_env.sh --install    install only what is missing
#   check_env.sh --install --user   prefer tlmgr user mode (~/texmf), no sudo
#
# Preference order, per the skill: use whatever TeX is already installed; if none,
# BasicTeX on macOS (~100 MB) over full MacTeX (~6 GB); add packages with tlmgr into
# the existing tree rather than laying down a new distribution.

set -uo pipefail

INSTALL=0; USERMODE=0
for a in "$@"; do
  case "$a" in
    --install) INSTALL=1 ;;
    --user)    USERMODE=1 ;;
    -h|--help) sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "check_env.sh: unknown option $a" >&2; exit 2 ;;
  esac
done

STY="geometry hyperref titlesec titletoc paralist graphicx comment nicefrac \
changebar mathpazo xcolor xspace ifthen draftwatermark fancyhdr etoolbox"

# .sty -> TeX Live package name
tlpkg() {
  case "$1" in
    titlesec|titletoc) echo titlesec ;;
    graphicx)          echo graphics ;;
    nicefrac)          echo units ;;
    mathpazo)          echo psnfss ;;
    xspace|ifthen)     echo tools ;;
    *)                 echo "$1" ;;
  esac
}

OS=$(uname -s)
echo "platform: $OS $(uname -m)"
echo

echo "=== tools ==="
MISSING_TOOLS=""
for c in git pdflatex latexmk tlmgr kpsewhich; do
  p=$(command -v "$c" 2>/dev/null)
  if [ -n "$p" ]; then
    printf "  %-10s %s\n" "$c" "$p"
  else
    printf "  %-10s MISSING\n" "$c"
    MISSING_TOOLS="$MISSING_TOOLS $c"
  fi
done

if command -v pdflatex >/dev/null; then
  echo
  echo "  $(pdflatex --version 2>/dev/null | head -1)"
  command -v kpsewhich >/dev/null && echo "  TEXMFROOT: $(kpsewhich -var-value=TEXMFROOT 2>/dev/null)"
fi
[ "$OS" = "Darwin" ] && { echo; echo "  TeX trees present:"; ls -d /usr/local/texlive/* /Library/TeX 2>/dev/null | sed 's/^/    /' || echo "    none"; }

echo
echo "=== LaTeX packages ==="
MISSING_STY=""
if command -v kpsewhich >/dev/null; then
  for s in $STY; do
    if kpsewhich "$s.sty" >/dev/null 2>&1; then
      printf "  %-16s ok\n" "$s"
    else
      printf "  %-16s MISSING\n" "$s"
      MISSING_STY="$MISSING_STY $s"
    fi
  done
else
  echo "  (kpsewhich unavailable — install TeX first, then re-run)"
fi

MISSING_PKGS=""
for s in $MISSING_STY; do
  p=$(tlpkg "$s")
  case " $MISSING_PKGS " in *" $p "*) ;; *) MISSING_PKGS="$MISSING_PKGS $p" ;; esac
done

echo
if [ -z "$MISSING_TOOLS" ] && [ -z "$MISSING_STY" ]; then
  echo "Everything needed is present. Nothing to install."
  echo "Prove it with a real build: scripts/build.sh <repo>/bylaws/tbp-mig-bylaws.tex --proposal"
  exit 0
fi

echo "=== what is needed ==="
[ -n "$MISSING_TOOLS" ] && echo "  tools:    $MISSING_TOOLS"
[ -n "$MISSING_PKGS" ]  && echo "  packages: $MISSING_PKGS"
echo

emit_macos() {
  if ! command -v pdflatex >/dev/null; then
    cat <<EOF
  # No TeX found. Install BasicTeX (~100 MB), not full MacTeX (~6 GB):
  brew install --cask basictex
  eval "\$(/usr/libexec/path_helper)"   # picks up /Library/TeX/texbin in this shell
EOF
  fi
  case "$MISSING_TOOLS" in *git*) echo "  xcode-select --install   # provides git" ;; esac
  if [ -n "$MISSING_PKGS" ] || [ -n "$MISSING_TOOLS" ]; then
    if [ "$USERMODE" -eq 1 ]; then
      echo "  tlmgr init-usertree"
      echo "  tlmgr --usermode install latexmk$MISSING_PKGS"
    else
      echo "  sudo tlmgr update --self"
      echo "  sudo tlmgr install latexmk$MISSING_PKGS"
    fi
  fi
}

emit_linux() {
  echo "  sudo apt-get update"
  echo "  sudo apt-get install -y texlive-latex-recommended texlive-latex-extra \\"
  echo "                          texlive-fonts-recommended latexmk git"
  echo "  # Debian's tlmgr cannot write to the apt-managed tree. If something is still"
  echo "  # missing after this, use: tlmgr init-usertree && tlmgr --usermode install <pkg>"
}

echo "=== commands ==="
if [ "$OS" = "Darwin" ]; then emit_macos; else emit_linux; fi

if [ "$INSTALL" -eq 0 ]; then
  echo
  echo "Report only. Re-run with --install to execute these, or run them yourself."
  exit 1
fi

echo
echo "=== installing ==="
if [ "$OS" = "Darwin" ]; then
  if ! command -v pdflatex >/dev/null; then
    command -v brew >/dev/null || { echo "Homebrew not found. Install BasicTeX from https://tug.org/mactex/morepackages.html then re-run." >&2; exit 2; }
    brew install --cask basictex || exit 1
    eval "$(/usr/libexec/path_helper)"
  fi
  command -v git >/dev/null || xcode-select --install || true
  if [ -n "$MISSING_PKGS" ] || ! command -v latexmk >/dev/null; then
    if [ "$USERMODE" -eq 1 ]; then
      tlmgr init-usertree 2>/dev/null
      # shellcheck disable=SC2086
      tlmgr --usermode install latexmk $MISSING_PKGS || exit 1
    else
      sudo tlmgr update --self || true
      # shellcheck disable=SC2086
      sudo tlmgr install latexmk $MISSING_PKGS || exit 1
    fi
  fi
else
  sudo apt-get update || exit 1
  sudo apt-get install -y texlive-latex-recommended texlive-latex-extra \
                          texlive-fonts-recommended latexmk git || exit 1
fi

echo
echo "=== re-checking ==="
exec "$0"
