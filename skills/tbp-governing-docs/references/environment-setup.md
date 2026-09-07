# Environment setup

Goal: the smallest install that builds these documents, without disturbing any TeX
distribution already present. Run `scripts/check_env.sh` first — on many machines
nothing needs installing, and installing a second TeX distribution on top of a working
one is the main way this goes wrong.

## Guiding preferences

1. **Detect before installing.** If `pdflatex`, `latexmk`, and the required packages
   already resolve, stop. Report and move on.
2. **Never install a second TeX distribution.** If `kpsewhich -var-value=TEXMFROOT`
   points at an existing tree, add missing packages to *that* tree with `tlmgr`
   rather than laying a new distribution beside it. Two distributions on one `PATH`
   produce builds that succeed or fail depending on shell startup order, which is
   miserable to debug later.
3. **Prefer BasicTeX over full MacTeX on macOS.** BasicTeX is roughly 100 MB against
   MacTeX's ~6 GB and, with the package list below, builds these documents fine. The
   tradeoff is real: BasicTeX means occasional `tlmgr install` when a document starts
   using something new. That is a good trade for a repo whose package needs have been
   stable for a decade. If the user specifically wants everything present with no
   `tlmgr` steps, full MacTeX is a legitimate choice — say so and let them pick.
4. **User-scope where the platform allows it.** `tlmgr --usermode` installs into
   `~/Library/texmf` (macOS) or `~/texmf` (Linux) without `sudo` and without touching
   the shared tree. Prefer it when the system tree is not writable.

## Required packages

Derived from an actual build log of `tbp-mig-bylaws.tex`, not from guessing at the
preamble.

| `.sty` needed | TeX Live package |
|---------------|------------------|
| `geometry.sty` | `geometry` |
| `hyperref.sty` | `hyperref` |
| `titlesec.sty`, `titletoc.sty` | `titlesec` |
| `paralist.sty` | `paralist` |
| `graphicx.sty` | `graphics` |
| `comment.sty` | `comment` |
| `nicefrac.sty` | `units` |
| `changebar.sty` | `changebar` |
| `mathpazo.sty` | `psnfss` |
| `xcolor.sty` | `xcolor` |
| `xspace.sty`, `ifthen.sty` | `tools` |
| `draftwatermark.sty` | `draftwatermark` |
| `fancyhdr.sty` | `fancyhdr` |
| `etoolbox.sty` | `etoolbox` |
| — build driver | `latexmk` |

`draftwatermark` and `fancyhdr` load only under the `proposal` class option, so a
`final`-only build can succeed while a proposal build fails. Install both regardless;
proposal builds are the common case for this skill.

## macOS

Check what is already there:

```bash
command -v pdflatex latexmk tlmgr git
ls -d /usr/local/texlive/* /Library/TeX 2>/dev/null
```

If BasicTeX is needed:

```bash
brew install --cask basictex          # or download BasicTeX.pkg from tug.org/mactex
eval "$(/usr/libexec/path_helper)"    # picks up /Library/TeX/texbin without a new shell
```

Then the packages. `tlmgr` needs its repository initialized on a fresh BasicTeX:

```bash
sudo tlmgr update --self
sudo tlmgr install latexmk titlesec paralist comment units changebar \
                   psnfss draftwatermark fancyhdr etoolbox xcolor
```

Without `sudo` rights, use user mode instead:

```bash
tlmgr init-usertree
tlmgr --usermode install latexmk titlesec paralist comment units changebar \
                         psnfss draftwatermark fancyhdr etoolbox xcolor
```

Git ships with the Xcode command line tools:

```bash
xcode-select --install     # no-op if already present
```

## Debian / Ubuntu

TeX Live from apt already carries every package above. This is the situation in most
Linux sandboxes, where nothing needs installing.

```bash
sudo apt-get update
sudo apt-get install -y texlive-latex-recommended texlive-latex-extra \
                        texlive-fonts-recommended latexmk git
```

Note that Debian's `tlmgr` cannot install into the apt-managed tree. If a package is
missing there, either install the corresponding `texlive-*` apt package or use
`tlmgr init-usertree` and `--usermode` to put it in `~/texmf`.

## Verifying

`scripts/check_env.sh` does this, but by hand:

```bash
for p in geometry hyperref titlesec titletoc paralist graphicx comment \
         nicefrac changebar mathpazo xcolor xspace ifthen draftwatermark fancyhdr; do
  kpsewhich $p.sty >/dev/null || echo "MISSING: $p.sty"
done
```

The real proof is a build. From the repo:

```bash
cd bylaws && latexmk -pdf -interaction=nonstopmode tbp-mig-bylaws.tex
```

A clean run ends with `Output written on tbp-mig-bylaws.pdf`. Overfull `\hbox`
warnings and the `document class '../bylaws'` warning are expected and not failures.

## When the repo lives in Dropbox

This repo is commonly at
`~/Library/CloudStorage/Dropbox/TBP/TBP-C-B`. Two consequences:

- **Online-only placeholders.** Files not downloaded locally appear in listings but
  read as missing or empty. Right-click the repo in Finder → "Make Available Offline"
  before building or editing. A build failing with "file not found" on a `.tex` that
  is plainly listed in the directory is almost always this.
- **git contention.** `git status` inside a syncing Dropbox folder can fail with
  `Resource deadlock avoided`, and over a remote file bridge it can produce bus
  errors. The repository is fine. Run git from a local terminal, or pause syncing for
  the duration of the work.

Building inside the Dropbox folder also means every intermediate `.aux`, `.log`, and
`.synctex.gz` syncs. `.gitignore` already excludes them from git, but if sync churn
is bothering the user, copy the tree to a scratch directory, build there, and copy
back only the PDF.
