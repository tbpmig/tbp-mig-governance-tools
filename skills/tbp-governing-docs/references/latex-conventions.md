# TBP-C-B LaTeX conventions

Everything here is specific to `bylaws.cls`. General LaTeX intuition will lead you
wrong in several places, so read the section you need before writing markup.

## Contents

- [Repository layout](#repository-layout)
- [The `officerdoc` option](#the-officerdoc-option)
- [Title-page dates are enforced under `final`](#title-page-dates-are-enforced-under-final)
- [Class options](#class-options)
- [Sectioning: what the levels actually render as](#sectioning-what-the-levels-actually-render-as)
- [Line style: two conventions coexist](#line-style-two-conventions-coexist)
- [The enumeration environments](#the-enumeration-environments)
- [`\item` vs `\item*` vs `\itemnotoc`](#item-vs-item-vs-itemnotoc)
- [Labels and cross-references](#labels-and-cross-references)
- [Redline macros](#redline-macros)
- [Trailing comments will eat your closing brace](#trailing-comments-will-eat-your-closing-brace)
- [Prose and typographic conventions](#prose-and-typographic-conventions)
- [Comment conventions](#comment-conventions)
- [Building](#building)
- [Failure modes and what they mean](#failure-modes-and-what-they-mean)

## Repository layout

```
TBP-C-B/
├── bylaws.cls                 shared document class for the three class-based docs
├── RotatedBentwWords.pdf      title-page logo (also NewBentLogo2019.png)
├── bylaws/
│   ├── tbp-mig-bylaws.tex     main file: preamble, chapter order, \input list
│   ├── preface.tex  government.tex  election_officers.tex  election_advisors.tex
│   ├── appointment.tex  meetings.tex  member_election.tex  records.tex
│   ├── active_status.tex  amendment.tex
│   ├── appendices.tex         ~56 KB; officer/committee/chair descriptions
│   ├── nationals.tex          national association material, included after appendices
│   └── specialrules.tex       stub, currently not \input by the main file
├── constitution/
│   ├── tbp-mig-constitution.tex   main file
│   └── charter.tex  objective.tex  membership.tex  government.tex
│       officers.tex  amendments.tex  dissolution.tex
└── financialpolicy/
    └── tbp-financial-policies.tex   single self-contained file; uses bylaws.cls with
                                     the `officerdoc` option (see below)
```

All three main files use `bylaws.cls`. Nothing here is a standalone document.

In the bylaws and constitution, content files contain no preamble and no
`\begin{document}`. They are `\input` by the main file, which supplies `\chapter{}`
headings itself — so a content file typically starts directly at `\section{}`. Two
exceptions: `bylaws/appendices.tex` carries its own `\chapter{}` commands because it
is `\input` after `\appendix`, and `financialpolicy/tbp-financial-policies.tex` is a
single file containing its own preamble, chapters, and body.

### The `officerdoc` option

The financial policy is an officer document rather than a chapter-ratified one, and
`bylaws.cls` handles that with an `officerdoc` class option: chapters render as
"Policy N" instead of "Bylaw N" or "Article N", the title page shows
`\officerdocumenttitle` followed by "Policies", and the approval block prints a single
"Last revised" date rather than the bylaws' three-date block.

```latex
\documentclass[bylaws,final,10pt,withoutoptional,withoutpreface,officerdoc]{../bylaws}
\officerdocumenttitle{Financial}
\lastreviseddate{16 July 2023}
```

This was added recently. If you encounter documentation or a cached copy of the class
claiming `officerdoc` is undeclared and that the financial policy cannot build, that
is out of date — verify by building rather than by trusting the note.

### Title-page dates are enforced under `final`

The class raises a `\ClassError` at `\begin{document}` when a `final` build is missing
a date its title page needs:

| Missing | Required by |
|---------|-------------|
| `\officerdocumenttitle` | any `officerdoc` build, draft or final |
| `\lastreviseddate` | `officerdoc` + `final` |
| `\chapteramendmentdate` | bylaws + `final` |
| `\appendixamendmentdate` | bylaws + `final` |

This matters for finalize work. Switching a document from `proposal` to `final`
without supplying the dates now fails loudly instead of printing a title page with a
silent gap — which is the desired behaviour, but it means the class-option flip and
the date update belong in the same edit and the same ledger row. The error text names
the macro and gives an example; `-` is accepted where a document has never been
amended in that category.

## Class options

Set in the `\documentclass[...]` line of each main file.

| Option | Effect |
|--------|--------|
| `bylaws` / `constitution` | chapters render as "Bylaw N" or "Article N"; sets the title-page doc type |
| `proposal` / `final` | `proposal` loads `draftwatermark` + `fancyhdr`, stamps DRAFT, prints "Draft revised: \today". `final` prints adoption and revision dates. |
| `10pt` / `11pt` / `12pt` | base font size |
| `withoptional` / `withoutoptional` | includes or excludes `optionalpart` environments (e.g. the "Chapter Bylaws" `\part` divider) |
| `withpreface` / `withoutpreface` | includes or excludes `preface` environments |
| `officerdoc` | officer document: chapters become "Policy N", title page uses `\officerdocumenttitle` and `\lastreviseddate` |

Defaults if unspecified: `proposal, bylaws, 10pt, withoptional`.

Current settings:

```latex
% bylaws/tbp-mig-bylaws.tex
\documentclass[bylaws,final,10pt,withoutoptional,withoutpreface]{../bylaws}
% constitution/tbp-mig-constitution.tex
\documentclass[constitution,final,withoutpreface,withoutoptional,11pt]{../bylaws}
% financialpolicy/tbp-financial-policies.tex
\documentclass[bylaws,final,10pt,withoutoptional,withoutpreface,officerdoc]{../bylaws}
```

Note the constitution is 11pt and the other two are 10pt. Anything going to a vote
should be switched to `proposal` so the DRAFT marking is present.

Date macros live in the main file preamble and are printed on the title page under
`final`:

```latex
\adoptiondate{12 November 2013}
\chapteramendmentdate{18 February 2025}      % last chapter-approved revision
\appendixamendmentdate{6 April 2025}         % last Officer Corps appendix revision
\lastreviseddate{16 July 2023}               % officerdoc only
\officerdocumenttitle{Financial}             % officerdoc only
```

## Sectioning: what the levels actually render as

`secnumdepth` is 4 and `tocdepth` is 3.

| Command | Renders as | Numbering |
|---------|-----------|-----------|
| `\part{}` | part divider | only inside `optionalpart` |
| `\chapter{}` | centred bold "Bylaw VII" / "Article IV" / "Appendix F" — **not** on its own page | uppercase Roman |
| `\section{}` | run-in small caps, "Section VII.3." | `\thechapter.\arabic` |
| `\subsection{}` | via `enumsubsection`, label `(a)` | `\thesection.\alph` |
| `\subsubsection{}` | via `enumsubsubsection`, label `(i)` | `\thesubsection.\roman` |

`\titleclass\chapter{straight}` is why chapters do not start new pages — this is a
continuous-flow legal document, not a book.

## Line style: two conventions coexist

Both are current on `main`. Detect which one a file uses before you edit it, and match it.

### The converted style — one sentence per line

`bylaws/` and `constitution/` were converted in PR #18. A sentence break starts a new source
line; nothing else does. Long sentences stay long on a single line — there is no column
limit and no wrapping mid-sentence. Sectioning commands sit on their own line with the
body beneath:

```latex
\section{Advisors}\label{sec:advisors}
The chapter must maintain a minimum of four advisors, as stipulated in \href{...}{C-VI,7} of the Constitution of the Tau Beta Pi Association.
An advisor must be an initiated member of Tau Beta Pi.
One of the advisors must serve as the chapter's Chief Advisor.
```

Median live line in those directories is 70 characters, p90 is 172. The point is that a
sentence-level amendment becomes a one-line diff, which matters when the diff is what
people vote on.

### The old style — one line per section

`financialpolicy/` was left out of that conversion and still runs an entire section onto
one line, up to 1,084 characters:

```latex
\section{Terms of Office} The officers of this chapter hold office for one semester except for the External Vice Presidents, one K-12 Outreach Officer, ...
```

### Detecting which you are in

Do not assume which style a file uses — the two directories genuinely differ, and a
future conversion of the financial policy would flip it. Measure:

```bash
awk 'length > 250 && $0 !~ /^ *%/ {n++} END {print FILENAME": "n+0" very long lines"}' <file>
```

Many long lines means old style, near zero means converted.

### Matching, and never converting

Match what the file does. In a converted file, changing one sentence should touch one
line; in an unconverted file the same change touches the whole section line, and that
is correct. Both render identically — the run-in appearance comes from `titlesec`, not
from the source layout — so line style is purely a source convention and changing it
alters nothing a voter sees. That is exactly why converting a paragraph during an
amendment is a defect: it is invisible in the PDF and enormous in the diff.

Converting a file's style is its own task, with its own ledger, proved render-identical
with `pdftotext` before and after. Never part of an amendment.

### What held through the migration

- Comments go on the line **before** the text they describe, never trailing. There are
  now zero trailing comments on live lines anywhere in the repository.
- Mid-sentence query comments were relocated above the sentence and labelled, e.g.
  `% Open Question (faculty member): UM??` in `bylaws/government.tex`.
- Commented-out archive blocks kept their original internal line structure. They are
  not sentence-split, because they exist to be compared against live text if the
  position is revived. The longest line in the repository, 795 characters in
  `bylaws/appendices.tex`, is one of these — not a missed conversion.

### The constitution's own quirks

Beyond line style, the constitution sets `\setcounter{tocdepth}{0}` after `\maketitle`,
so only articles appear in its contents, and defines a local `tight_enumerate`
environment over `paralist`'s `compactenum`. It opens with `\chapter*{Preamble}` plus a
manual `\addcontentsline` containing a longstanding `Preamable` typo in the TOC entry.
Leave that unless fixing it is a sanctioned row — it is a visible change to the
contents page.

## The enumeration environments

`enumsubsection` and `enumsubsubsection` are custom environments that make an
`enumerate` list drive the `subsection`/`subsubsection` counters, so that lettered and
roman-numeraled items appear in the table of contents as real document structure.
Plain `enumerate` does not do this — it is used only for un-numbered inner lists that
should stay out of the TOC.

```latex
\section{Officer Corps}\label{sec:officercorps}
\begin{enumsubsection}
\item{Membership and Responsibilities} The Officer Corps consists of ...
\begin{enumsubsubsection}
\item*{Initiation Dues} Sets the level of initiation dues.
\item*{Fund Administration} Administers funds available for ...
\end{enumsubsubsection}
\end{enumsubsection}
```

Nesting order is fixed: `enumsubsection` may contain `enumsubsubsection`, which may
contain plain `enumerate`. Do not nest them any other way; the counter redefinitions
assume this hierarchy and silently misnumber otherwise.

## `\item` vs `\item*` vs `\itemnotoc`

This trips people up, and picking the wrong one produces a document that compiles
cleanly but has a wrong table of contents.

| Form | Title printed in body? | Added to TOC? |
|------|------------------------|---------------|
| `\item{Title}` | yes, small caps | yes |
| `\item*{Title}` | no | yes |
| `\itemnotoc` | n/a — no title argument | no |

`\itemnotoc` is for list items that are just enumerated prose with no heading:

```latex
\begin{enumsubsection}
\itemnotoc Seniority is measured as time spent in the current advisor term.
\itemnotoc In the event of a tie ...
\end{enumsubsection}
```

When adding an item to an existing list, match whichever form its siblings use. A
list that mixes `\item{}` and `\itemnotoc` renders inconsistently and looks like a
mistake even when it compiles.

`\officer{Name}` is a related shortcut used inside `description` environments in
`appendices.tex`; it emits a bold item and adds a TOC subsection line.

## Labels and cross-references

Naming follows `\label{sec:camelOrLowercase}` — for example `sec:officercorps`,
`sec:AdHocOfficers`, `sec:advisorLength`, `sec:ugradreqs`. There is no rigid casing
rule; match nearby labels rather than imposing one.

References use a non-breaking space so the number never wraps away from its noun:

```latex
Appendix~\ref{sec:officerreq}
Bylaw~\ref{sec:advisorLength}
Section~\ref{sec:OfficerTeams}
\textsection \ref{sec:defaultappointcomp}
Appendices~\ref{sec:AdHocOfficers}, \ref{sec:AdHocCommittees}, and~\ref{sec:Chairs}
```

External references to the national association's documents are hyperlinked:

```latex
\href{http://www.tbp.org/off/ConstBylaw.pdf}{Tau Beta Pi Association Bylaws 5.03}
\href{http://www.tbp.org/off/ConstBylaw.pdf}{C-VI,7}
```

References to the chapter constitution from within the bylaws are written inline as
`C§I.3` or `Constitution Article IV.2.b` — these are cross-*document* and therefore
plain text, not `\ref`. They will not break at compile time if the constitution
renumbers, so check them by hand when constitution structure changes.

**Removing a labelled section removes its label.** Any surviving `\ref` to it renders
as `??` and `latexmk` reports "Latex failed to resolve 1 reference(s)" — easy to miss
in a long log. `scripts/audit.py` checks this specifically.

## Redline macros

Currently defined inline, identically, in **all three** main files —
`bylaws/tbp-mig-bylaws.tex`, `constitution/tbp-mig-constitution.tex`, and
`financialpolicy/tbp-financial-policies.tex` — each alongside its own
`\usepackage[color]{changebar}` and `\cbcolor{red}`:

```latex
\newcommand{\removed}[1]{\cbstart\removedfragile{#1}\cbend{}}
\newcommand{\removedfragile}[1]{{\color{red}{#1}}{}}
\newcommand{\added}[1]{\cbstart\addedfragile{#1}\cbend{}}
\newcommand{\addedfragile}[1]{{\color{green!50!black}{#1}}{}}
\newcommand{\changed}[2]{\added{#1}\removed{#2}}
```

### The consolidation, and why it is not an amendment task

Three identical copies means a fix lands three times or not at all, so these belong in
`bylaws.cls`. The version that should end up there adds `\texorpdfstring`, which the
inline copies lack:

```latex
\RequirePackage[color]{changebar}
\RequirePackage{xcolor}
\cbcolor{red}
\newcommand{\addedfragile}[1]{\texorpdfstring{{\color{green!50!black}{#1}}}{#1}{}}
\newcommand{\removedfragile}[1]{\texorpdfstring{{\color{red}{#1}}}{#1}{}}
\newcommand{\added}[1]{\cbstart\addedfragile{#1}\cbend{}}
\newcommand{\removed}[1]{\cbstart\removedfragile{#1}\cbend{}}
\newcommand{\changed}[2]{\added{#1}\removed{#2}}
```

Doing it means touching `bylaws.cls` and deleting the inline block plus the
`changebar` / `\cbcolor` lines from all three main files — leaving even one in place
makes that document fail with `Command \added already defined`, in a document you were
not working on. Then all three need rebuilding.

That is a four-file change with a repository-wide effect, which is why it must not
ride along inside an amendment. A user who asked to strike one chair position and got
a diff containing the constitution has been badly served, however defensible the
cleanup is on its own terms. Raise it as separate work; do not fold it in.

### Trailing comments will eat your closing brace

Very many lines in this repository end in a `%` comment — `% Amended W26`,
`% Added F23`, `% Prior Language: ...`. When you wrap such a line in `\removed{...}`
or `\added{...}`, the closing brace must go **before** the comment, because everything
after an unescaped `%` is invisible to TeX:

```latex
% WRONG — the } is inside the comment and never closes the group
\removed{The Apparel Chair(s) will be responsible for ... % Amended W26}

% RIGHT
\removed{The Apparel Chair(s) will be responsible for ...} % Amended W26
```

The wrong version fails with `File ended while scanning use of \removed` and
`\begin{enumerate} ... ended by \end{document}`, reported against the `\input` line in
the main file rather than the line you edited — so the error points hundreds of lines
away from the mistake. `scripts/audit.py` catches this as a brace imbalance before you
ever run the build, which is the cheaper place to find it.

### Working with fragile variants before the consolidation

Wrap the call site. This stays inside the line you are already editing and needs no
class change:

```latex
\section{\texorpdfstring{\addedfragile{Tracking of Status}\removedfragile{Tracking Status}}{Tracking of Status}}
\item{\texorpdfstring{\removedfragile{Apparel Chair}}{Apparel Chair}}
```

The first argument is what the page shows — both versions, coloured. The second is
what the PDF bookmark shows, normally just the new title, since a bookmark is
navigation rather than part of the redline.

**`\item{}` needs this as much as `\section{}` does.** Inside `enumsubsection`,
`\item{}` resolves to the class's `\subsectionitem`, which pushes its argument through
`\addcontentsline{toc}{subsection}`. With `tocdepth` at 3, those entries become
level-3 PDF bookmarks. Omitting the wrapper on an `\item{}` title yields a bookmark
reading `redApparel Chair` while the printed page is flawless.

Do not reason about whether the bookmark tree reaches a given level and drop the
wrapper as dead markup on that basis — that inference has been made and was wrong.
Check the artifact:

```bash
pdftk <file>.pdf dump_data | grep BookmarkTitle
```

A clean result shows the plain title. A polluted one shows the xcolor spec
(`red...`, `green!50!black...`), and the build log carries
`Token not allowed in a PDF string`.

**`\protect` does not fix this.** It defers expansion, but the colour specification
still reaches the PDF string and the bookmark is polluted identically. Only
`\texorpdfstring`, which supplies a separate plain-text string, works.

## Prose and typographic conventions

- Fractions: `\nicefrac{2}{3}`, `\nicefrac{5}{7}`. Some older text uses a bare `2/3`;
  prefer `\nicefrac` for anything new but do not convert existing text unless that
  conversion is a sanctioned ledger row.
- The chapter's Greek designation: `MI-$\Gamma$`.
- Curly apostrophes (`’`) appear in some newer text and straight ones elsewhere. Match
  the surrounding paragraph rather than normalizing.
- Officer and body names are capitalized as proper nouns: Officer Corps, Advisory
  Board, Executive Committee, Chief Advisor, Events Team, Chapter Team.
- Documents refer to "the chapter", "active members", "electees", "candidates" —
  these are terms of art with defined meanings elsewhere in the document. Do not
  substitute synonyms.

## Comment conventions

Existing source uses `%` comments heavily as an informal change log
(`% W25 struck Cataloguer`, `% Added F23`, `% Prior Language: ...`). **Do not add new
ones on live text**, and leave existing ones exactly as they are — they are part of
the document's history and removing or reformatting them is an unsanctioned change.

There is exactly one comment you *do* write: the history line above a commented-out
severable unit. See below.

### Commented-out blocks and their history line

Commented-out `\item` and `\section` blocks are the chapter's archive of retired
severable units — chair positions, ad hoc officers, committees — kept because these
get revived. When an adopted amendment removes such a unit, comment it out rather
than deleting it, and put one history comment directly above the block recording the
terms it was added and removed, oldest first:

```latex
% Added W22, removed F22, added back F23, removed W26
%\item{New Initiatives Chair} The New Initiatives Chair will assist with coordinating
%the Chapter's New Initiatives meetings, including identifying topics, chairing the
%meeting, obtaining food, and summarizing discussion.
```

Rules that make this line trustworthy rather than decorative:

- **One line above the whole block**, not one per commented line.
- **Accumulate.** A revived-then-struck-again position extends the existing line;
  never replace it. The cycle count is information the next officer corps needs.
- **Derive the term code from the adoption date and confirm it before writing.**
  Fall and Winter are the chapter's terms, so January–April is W and
  September–December is F. May–August maps to neither — ask.
- **Do not manufacture history.** Extend an existing history line if there is one.
  Otherwise write only the removal you are performing: `% Removed W26`. Most retired
  items have nothing to recover — of the 42 commented-out entries in
  `appendices.tex`, 35 carry no date at all, and the other 7 use five different
  informal shapes (`% Removed in W25`, `% Struck in F23`, `% Removed during F23`,
  `% Added F23 Removed W25`, `% Added 1/15/22`). Where such a legacy note exists,
  surface it to the user and let them decide whether it belongs in the history line.
  Never edit or move the legacy comment itself.

Converting those legacy notes into history lines across the repository is a sensible
one-time pass and **separate work** — dozens of lines changed for zero rendered
output. Raise it rather than folding it into an amendment.

Ordinary prose deletions are deleted outright and get no history line.

A commented-out block wrapped in `\added{}` is a *pending* proposal parked in the
source, not an adopted change. `bylaws/amendment.tex` and the Awards chapter at the
end of `appendices.tex` are current examples. Do not uncomment or finalize these
unless the user explicitly says that proposal passed.

## Building

Use `latexmk`. Never judge a build by a single `pdflatex` run, and never read
diagnostics out of the middle of a multi-pass log.

```bash
cd <repo>/bylaws && latexmk -pdf -interaction=nonstopmode tbp-mig-bylaws.tex
```

### This document needs four passes, and the early ones lie

Measured from a clean tree, with redline markup present:

| Pass | References | Change bars | Page count |
|------|-----------|-------------|------------|
| 1 | **68 undefined** | rerun requested | 27 — wrong |
| 2 | all resolved | rerun requested | 31 — correct |
| 3 | all resolved | rerun still requested | 31 |
| 4 | all resolved | converged | 31 |

Pass 1 reports every cross-reference in the document as undefined, because the `.aux`
file does not exist yet and there is nothing to resolve against. It also reports a page
count four pages short, because the table of contents has not been sized. Both are
normal and neither is a defect. `latexmk` runs all four passes and stops when the
document is stable.

**Never report a pass-1 diagnostic to the user.** Telling someone their bylaws have 68
broken references when they have none destroys the value of the one time it is true.

### Which log to read

`latexmk`'s stdout concatenates every pass, so it contains all of pass 1's noise. The
`.log` file it leaves on disk is written by the **last** `pdflatex` run only. On the
same build: 69 "undefined" lines in latexmk's stdout, zero in `tbp-mig-bylaws.log`.

So read `<basename>.log` for errors and unresolved references, and use latexmk's
stdout only for its end-of-run summary line, `Latex failed to resolve N reference(s)`.
`scripts/build.sh` already does this — prefer it over calling `latexmk` by hand, and if
you do call `latexmk` yourself, do not grep its stdout for `Reference .* undefined`.

### Why not just run pdflatex a few times

Because change bars never converge that way. Repeated `pdflatex` keeps reporting
"Changebar info has changed. Rerun to get the bars right" indefinitely — in the
measurement above it was still asking on pass 3 — and the PDF comes out with correct
red and green text but **no margin bars**. That looks close enough to correct to
circulate for a vote. `latexmk` resolves the `.cb`/`.cb2` handoff properly.

If the final pass still says the changebar info changed, the bars in that PDF are
unreliable. Rebuild; if it persists, `latexmk -C` first to discard stale `.cb` files.

### Required packages

All standard in TeX Live and present in BasicTeX plus the list in
`references/environment-setup.md`: `geometry`, `hyperref`, `titlesec`, `titletoc`,
`paralist`, `graphicx`, `comment`, `nicefrac` (from the `units` bundle), `changebar`,
`mathpazo` (from `psnfss`), `xcolor`, `xspace`, `ifthen`, plus `draftwatermark` and
`fancyhdr` which load only under the `proposal` option.

The `\documentclass{../bylaws}` relative path emits
`LaTeX Warning: You have requested document class '../bylaws'` on every run. It is
harmless and expected; do not try to fix it.

## Failure modes and what they mean

**"Changebar info has changed. Rerun to get the bars right", forever.** Repeated
`pdflatex` runs do not converge changebar's `.cb`/`.cb2` files. The PDF still builds,
with correct colours but **no margin bars** — which looks close enough to correct to
ship by accident. `latexmk` handles the rerun logic properly. Always build with
`latexmk`.

**`Argument of \ttl@assign@i has an extra }`, `Paragraph ended before \contentsline
was complete`, `Something's wrong--perhaps a missing \item`.** A non-fragile `\added`,
`\removed`, or `\changed` inside a sectioning command or `\item` title. The errors
point at `titlesec` and the TOC machinery rather than at your edit, so they are
genuinely misleading. Switch to the `fragile` variants.

**`File '../NewBentLogo2019' not found`.** The main file's `\orglogo{}` points at a
logo in the repo root. Either the file is missing or, under Dropbox, it is an
online-only placeholder that has not been downloaded.

**`Latex failed to resolve N reference(s)`, `??` in the PDF.** A `\ref` to a label that
no longer exists, usually because a removed section took its `\label` with it. Trust
this only from the final pass — see "This document needs four passes" above. Raw
`Reference ... undefined` warnings from latexmk's stdout are pass-1 noise.

All three documents currently build with **zero** unresolved references, so any that
appear are yours. Note that `latexmk`'s log concatenates every pass, and the early
passes legitimately report dozens of undefined references before the `.aux` file is
populated — only the end-of-run `Latex failed to resolve N reference(s)` summary
means anything. Counting raw `undefined on input line` warnings will tell you the
bylaws have 57 problems when they have none.

**Overfull `\hbox` warnings.** Dozens are present in a clean build of the current
document. They are cosmetic and pre-existing. Ignore them; do not attempt to fix
line breaking.

**`Class bylaws Error: Missing \chapteramendmentdate`** (or `\appendixamendmentdate`,
`\lastreviseddate`, `\officerdocumenttitle`). A `final` build without the dates its
title page needs. Supply the date in the preamble — `-` if that category has never
been amended — and put it in the same ledger row as the class-option flip.

**`Command \added already defined`.** The redline macros exist both in `bylaws.cls`
and inline in a main `.tex`. Delete the inline copy — and check the other two main
files, since all three carried the same block.
