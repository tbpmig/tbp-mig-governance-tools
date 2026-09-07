---
name: tbp-governing-docs
description: >-
  Edit the Tau Beta Pi Michigan Gamma governing documents — constitution, bylaws,
  appendices, and financial policy — in the TBP-C-B LaTeX repository, with the rigor
  an amendment going to a vote requires. Use this skill whenever the user wants to
  propose, draft, redline, revise, or finalize a change to a chapter governing
  document; whenever they mention the constitution, the bylaws, an appendix, a chair
  or officer position, the financial policy, TBP-C-B, bylaws.cls, or the
  \added / \removed / \changed redline macros; whenever they ask for a redline or
  before/after PDF for a chapter or Officer Corps vote; and whenever they need a
  LaTeX toolchain or git set up so these documents will build. Use it even when the
  request sounds trivial ("just change X to Y in the bylaws", "strike the IM Sports
  Chair", "fix a typo in Appendix F") — the scope and audit discipline applies to
  every edit regardless of size, and a one-word change to a governing document is
  still an amendment.
---

# TBP Michigan Gamma governing documents

These are the operative governing documents of a real organization. People vote on
them, and the text that gets adopted is the text that appears in the redline PDF put
in front of them. That is the whole reason this skill exists and why it is strict
about scope: an edit that quietly reflows a paragraph, renumbers a section, or
"improves" a sentence nobody moved to change is a defect, not a bonus. The chapter
authorized a specific change; the diff should contain that change and nothing else.

## Two modes, and never both at once

**Propose** (the default). Wrap intended changes in the redline macros so the
document builds into a marked-up PDF showing old and new text together. The source
still contains both versions. Nothing is destroyed. This is what goes to a vote.

**Finalize** (only when the user explicitly asks). Resolve the redline markup into
plain adopted text: keep what was added, drop what was removed. Only do this after
the user says the change passed and says to finalize. Never strip redline markup as
a cleanup gesture while a vote may still be pending — an in-flight proposal that
silently becomes plain text is indistinguishable from a change nobody approved.

If the user's request is ambiguous about which mode they want, assume Propose and say
so in one line.

## Locating the repository

Officers keep this repository in different places — some work from a clone, some from
a shared Dropbox folder — so **do not assume a path.** Identify it by its shape: a
directory containing `bylaws.cls` at the root alongside `bylaws/`, `constitution/`, and
`financialpolicy/` subdirectories.

If the working directory is not obviously it, search rather than guess:

```bash
find ~ -name bylaws.cls -not -path '*/.git/*' 2>/dev/null | head
```

If that finds nothing, or finds several, ask the user which one rather than picking.
Editing the wrong copy of a governing document is worse than asking.

Once you have the path, check whether it sits under a sync folder — `Dropbox`,
`CloudStorage`, `OneDrive`, `Google Drive`. If it does, two hazards apply that produce
confusing failures rather than clean errors:

- **Online-only placeholders.** Files not downloaded locally read as empty or missing
  even though the directory lists them. If a `.tex` file appears absent or
  zero-length, ask the user to make the folder available offline rather than
  concluding the file is gone.
- **git contention.** `git status` may fail with `Resource deadlock avoided` or bus
  errors, especially over a remote file bridge. That is the sync layer, not repository
  corruption. Work on the files directly and tell the user git operations need a local
  terminal, rather than retrying.

Neither applies to an ordinary clone. Do not raise them unless the path says to.

## The discipline: ledger, edit, audit

This sequence is what makes the skill trustworthy. Do not compress it.

### 1. Restate scope and get sign-off before touching anything

Write out every intended edit as a ledger and stop for the user's confirmation. One
row per change:

| # | File | Location | Current text | Proposed text |
|---|------|----------|--------------|---------------|
| 1 | `bylaws/appendices.tex` | Ch. Chairs → Current Chair Positions → IM Sports Chair | *(full item text)* | *(removed)* |

Quote the current text exactly as it appears in the source, not paraphrased. The
point of the ledger is that the user can catch a misread before it becomes a diff —
if you have misidentified which section they meant, this is where it surfaces
cheaply. Ask about anything genuinely ambiguous rather than picking the more likely
reading.

If the requested change implies consequential edits the user did not name — a
removed section that other text cross-references, a defined term used elsewhere,
a count like "two External Vice Presidents" that a change would falsify — list those
as **proposed additional rows** and ask. Do not fold them in silently, and do not
skip mentioning them either. The user decides whether the amendment covers them.

### 2. Make exactly the sanctioned edits

Edit only the lines the ledger covers. Concretely, this means:

- **Match the line style of the file you are in; never convert it.** Two conventions
  coexist in this repository — see "Line style" below. Whichever file you are editing,
  keep its shape. Converting a paragraph as a side effect of an amendment is how a
  restyle gets smuggled into something people are voting on, and it turns a three-word
  change into an unreviewable hunk either way.
- Do not normalize whitespace, tabs, or blank lines you did not otherwise touch.
- Do not renumber, reorder, or retitle anything not in the ledger.
- Do not "fix" spelling, grammar, or inconsistent markup you notice in passing.
  Mention it to the user afterward instead — it may be deliberate, and it is not
  what was moved.

### Line style: two conventions coexist

`bylaws/` and `constitution/` are **one sentence per line** — a sentence break starts a
new source line, nothing else does, and long sentences stay long on one line.
Sectioning commands sit on their own line with the body beneath. Median live line is 70
characters, p90 is 172.

`financialpolicy/` was deliberately left out of that conversion and still runs an entire
section onto one line, up to 1,084 characters.

Both are current on `main`. Neither is going to change under you, but **do not assume
which one you are in — look at the file**, because the two directories genuinely differ
and a future conversion of the financial policy would flip it:

```bash
awk 'length > 250 && $0 !~ /^ *%/ {n++} END {print FILENAME": "n+0" very long lines"}' <file>
```

Near zero means one sentence per line; several means the old style. Then match what you
find. In a converted file an amendment that changes one sentence should touch one line.
In the financial policy the same amendment touches the whole section line, and that is
correct — leave it.

Two things hold in both: a comment goes on the line **before** the text it describes,
never trailing — there are zero trailing comments on live lines anywhere in the
repository; and commented-out archive blocks keep whatever internal shape they already
have, because they exist to be compared against live text if the position is revived.
The longest line in the repository sits inside one of those blocks, not in live text.

If the user asks you to convert a file's style, that is its own task with its own
ledger, run on its own and proved render-identical with `pdftotext` before and after.
It is never part of an amendment.

### 3. Audit the diff before reporting done

Run the bundled audit and read it:

```bash
python3 scripts/audit.py --repo <repo-root> --allow bylaws/appendices.tex
```

`--allow` takes the files the ledger sanctioned; anything else that changed is
flagged. The script reports the full diff plus the hazards a script can catch
objectively: whitespace-only and reflow hunks, files outside the allowed set, brace
imbalance in edited files, redline macro counts, and labels that were removed while
references to them survive.

The script cannot judge semantics. You do that: walk each hunk and match it to a
ledger row. If a hunk has no row, either it was a mistake — revert it — or the ledger
was incomplete, in which case go back to the user rather than quietly accepting it.

Then read `AUDIT: adopted text delta` in the output. That section shows what the
governing text would actually say if the proposal passed, with markup resolved. It
catches the failure mode a raw diff hides: markup that compiles cleanly and looks
right in the source but leaves the adopted text saying something nobody voted for.

## Redline macros

Currently defined inline in each of the three main `.tex` files (not in the class):

```latex
\added{new text}              % green, changebar in margin
\removed{old text}            % red, changebar in margin
\changed{new text}{old text}  % both, new first
\addedfragile{...}            % same colors, no changebar, safe in titles
\removedfragile{...}
```

All three main `.tex` files currently define these inline, in three identical copies
that predate `\texorpdfstring`. That duplication is worth consolidating into
`bylaws.cls` — but **not as part of an amendment**. Consolidating means editing
`bylaws.cls` plus all three main files, so a request to strike one chair position
would end up modifying the constitution and the financial policy. That blast radius is
precisely what this skill exists to prevent, and no reviewer looking at the diff for a
chair position expects to see the constitution in it. Mention it as a separate piece
of work the user may want to schedule, and move on.

When you need a fragile variant in a title before that consolidation happens, wrap the
call site. It costs one line, inside the line you are already changing:

```latex
\section{\texorpdfstring{\addedfragile{Tracking of Status}\removedfragile{Tracking Status}}{Tracking of Status}}
\item{\texorpdfstring{\removedfragile{Apparel Chair}}{Apparel Chair}}
```

Without the wrapper the printed page looks perfect while the PDF bookmark reads
`green!50!blackTracking of Status` or `redApparel Chair`, and hyperref logs
`Token not allowed in a PDF string` somewhere nobody looks. The second argument is the
plain text the bookmark should show — normally the new title, since a bookmark is
navigation rather than part of the redline.

This applies to `\item{}` titles just as much as `\section{}`. That is not obvious and
it has been got wrong: inside `enumsubsection`, `\item{}` is the class's
`\subsectionitem`, which pushes its argument through
`\addcontentsline{toc}{subsection}`, and `tocdepth` is 3, so those titles become
**level-3 PDF bookmarks**. Do not reason from bookmark nesting about whether the
wrapper is needed and then remove it as dead markup — check the bookmark itself:

```bash
pdftk <file>.pdf dump_data | grep BookmarkTitle
```

`\protect` is not a substitute. It defers expansion but the colour specification still
lands in the PDF string, producing the same polluted bookmark.

Three things about these are easy to get wrong and hard to notice:

**`\changed` takes new text first, old text second.** This reads backwards to most
people, who expect old-then-new. Getting it inverted produces a document that
compiles fine and tells the voters the exact opposite of the intent. Check it every
time.

**The macros insert no separator.** `\changed{Chapter Development Officer}{Membership
Officer}` renders as `Chapter Development OfficerMembership Officer` run together.
That is the established house appearance and colour distinguishes them, so do not
invent a separator unilaterally — but do put any punctuation or spacing the sentence
needs *inside* the braces, the way `\added{, and Appendix \ref{sec:awards} (Awards)}`
does in the existing source.

**Put the closing brace before any trailing `%` comment.** Lines here very often end
in one (`% Amended W26`, `% Added F23`). A closing brace placed after it is inside the
comment and never closes the group, and the resulting error is reported against the
`\input` line in the main file rather than the line you edited. The audit's brace
check catches this before the build does.

**Use the `fragile` variants inside moving arguments.** `\added` and `\removed` use
changebar's `\cbstart`/`\cbend`, which cannot survive being written to the `.toc`
file. Putting them inside `\section{}`, `\chapter{}`, or an `\item{}` title breaks
the build with errors like `Argument of \ttl@assign@i has an extra }` and
`Paragraph ended before \contentsline was complete` — errors that point at the table
of contents machinery rather than at your edit, so they are genuinely confusing if
you do not know the cause. The fragile variants give the colours without the bars and
compile cleanly.

**In the converted style a unit spans several lines, so it needs several macros.** A
chair position is now a title line plus one line per sentence of its description. Wrap
each of them. Wrapping only the title and leaving `\removed{}` empty compiles cleanly
and renders plausibly, while the text you meant to strike stays fully operative — and
the adopted-text delta is where that shows up. The audit flags an empty redline
argument for exactly this reason.

To redline a whole section, split it: fragile in the title, normal in the body.

```latex
\section{\removedfragile{Benefits of Active Status}}\removed{Active status may be
designated on some chapter documents ... relating to standard meetings and socials.}
```

## Building

Always use `scripts/build.sh`, or `latexmk` if you build by hand. **Never judge a
build from a single `pdflatex` run, and never report a diagnostic from anywhere but
the final pass.**

```bash
scripts/build.sh <repo-root>/bylaws/tbp-mig-bylaws.tex --proposal
```

### Four passes, and the first three are not the truth

From a clean tree this document needs four `pdflatex` passes. Cross-references resolve
on pass 2; change bars only converge on pass 4. Pass 1 reports **68 undefined
references** and a page count four pages short — not because anything is wrong, but
because the `.aux` and `.toc` files do not exist yet and there is nothing to resolve
against.

Those pass-1 warnings are noise, every single build, forever. Reporting them tells the
user their bylaws have 68 broken cross-references when they have none, and it spends
the credibility you need on the one occasion a reference really is broken. Say nothing
about them.

`latexmk` runs the passes and stops when the document is stable, which is why repeated
`pdflatex` is not a substitute: it never converges the changebar `.cb`/`.cb2` handoff,
so the PDF comes out with correct red and green text but **no margin bars** — plausible
enough to circulate for a vote unnoticed.

### Which log is honest

`latexmk`'s stdout concatenates all four passes, so it contains all of pass 1's noise —
69 "undefined" lines on a build where the finished document has none. The `.log` file
left on disk is written by the **final** pass only, and had zero.

Read `<basename>.log` for errors and unresolved references. Use latexmk's stdout only
for its end-of-run summary, `Latex failed to resolve N reference(s)`. `build.sh` does
this for you and stays silent on a clean build; if you ever grep a build log yourself,
do not grep latexmk's stdout for `Reference .* undefined`.

An unresolved reference reported by the final pass is real — it means a `\ref` points at
a `\label` that no longer exists and the PDF shows `??`. `scripts/audit.py` names which
label went missing and what still points at it.

### Proposal or final

The `--proposal` / `--final` flags set the class option in the main `.tex`:

- `proposal` stamps a DRAFT watermark on page one, a DRAFT running header, and
  "Draft revised: \today". Correct for anything going to a vote — a redlined PDF
  without DRAFT marking can be mistaken for the operative document.
- `final` prints the adoption and revision dates instead. Correct only after a change
  is adopted and finalized. Switching to `final` requires the title-page dates to be
  present or the class raises a `\ClassError`, so the option flip and the date update
  belong in the same edit and the same ledger row.

Read `references/latex-conventions.md` before writing new markup — it documents the
sectioning macros, the `enumsubsection`/`enumsubsubsection` environments, the starred
vs unstarred `\item` distinction, and the cross-reference conventions, all of which
are specific to this class and not guessable from general LaTeX knowledge.

## Finalizing an adopted change

Only on explicit instruction. Use the bundled resolver rather than editing by hand —
brace matching across multi-paragraph `\removed{}` blocks is exactly where hand
editing goes wrong.

```bash
python3 scripts/redlines.py --list bylaws/appendices.tex        # inventory first
python3 scripts/redlines.py --accept --in-place bylaws/appendices.tex
```

Two rules govern what happens to removed text, and they differ by what is being
removed:

- **Severable structural units** — a chair position, an officer position, a
  committee, an appendix entry that stands as its own `\item` or `\section` — get
  **commented out**, not deleted, and carry a history comment on the line above. The
  chapter revives and re-creates these positions on a cycle, and the commented-out
  text is what the next officer corps starts from. `--accept` leaves them for you:
  comment out every line of the block with a leading `%`, preserving the text, and add
  the history line above it.
- **Ordinary prose** — a clause, a sentence, a phrase, a changed number — is
  **deleted outright**. Git history is the record. Commenting out every deleted comma
  would make the source unreadable for no benefit.

### The history comment

A commented-out block gets one comment line directly above it recording the terms in
which the unit was added and removed, oldest first:

```latex
% Added W22, removed F22, added back F23, removed W26
%\item{New Initiatives Chair} The New Initiatives Chair will assist with coordinating
%the Chapter's New Initiatives meetings, including identifying topics, chairing the
%meeting, obtaining food, and summarizing discussion.
```

One line above the whole block, not one per line. The chronology **accumulates** —
when a revived position is struck again, extend the existing line rather than
replacing it, so the full cycle stays visible in one place. That cycle is the point:
a position on its fourth revival is telling the next officer corps something a single
`% Removed W26` cannot.

With no establishable prior history it degrades to what you actually know:

```latex
% Removed W26
```

Two things have to be true before you write this line, and neither is safe to assume.

**The term code.** Derive it from the adoption date the user gave you — a chapter
voting meeting on 12 March 2026 is W26 — then *state the derivation and get it
confirmed* before writing. Michigan Gamma runs Fall and Winter terms, so
January–April is W and September–December is F; an adoption date in May–August maps to
neither cleanly, and there you must ask rather than guess. A wrong term code is a
false statement in the operative record that will outlive everyone who could correct
it, and it is invisible in the rendered PDF because it lives in a comment.

**The prior history.** Read the history line above the block if one is there and
extend it. If there is not one, record only the removal you are actually performing —
`% Removed W26` — and say so. Most retired items have no recoverable history: of the
42 commented-out entries in `appendices.tex`, 35 carry no date of any kind. Do not
manufacture a chronology to fill the gap; a guess promoted into a comment reads as
established fact to everyone after you. If a legacy trailing comment nearby suggests
history (`% Added F23 Removed W25`), mention it to the user and let them decide
whether it belongs in the line — do not fold it in yourself, and do not edit or move
the trailing comment.

Converting the repository's existing scattered trailing comments into this format is a
worthwhile one-time pass, but it is **separate work**, like the redline-macro
consolidation. It touches dozens of lines across the appendices for zero rendered
change, and bundling it into an amendment buries the amendment. Raise it; do not fold
it in.

Do not add any *other* provenance comments (`% W25 struck Cataloguer` on a live line).
The history line above a commented-out block is the one exception, and it exists
because the block is an archive rather than operative text. Leave existing trailing
comments exactly where they are — they are part of the document's history, and
stripping or reformatting them is an unsanctioned change even when one of them is what
told you a position had earlier history.

Audit the finalize diff exactly as you would a proposal diff.

## Git

Branch and commit; never push, never open a PR. The user handles anything that
reaches a remote.

```bash
git checkout -b amend/<short-slug>
git add <only the sanctioned files>
git commit
```

`git add -A` is the wrong instinct here — the build leaves `.aux`, `.log`, `.toc`,
`.out`, `.synctex.gz`, `.cb`, `.cb2` litter, and while `.gitignore` covers most of it,
generated PDFs are tracked. Stage the files in the ledger explicitly.

Write the commit message as a description of the amendment: what changed, in which
document, and whether it is proposed or adopted. Do not include term codes or
attribute the change to a body unless the user gave you that information.

## Environment setup

When the user asks to set up their environment, or when a build fails because a tool
is missing, run the check first and only install what is actually absent:

```bash
scripts/check_env.sh              # report only
scripts/check_env.sh --install    # install what is missing
```

The preference is the smallest footprint that builds these documents: **BasicTeX**
plus `tlmgr` for the specific packages, not full MacTeX, and never a second TeX
distribution alongside an existing one. Details and the package list are in
`references/environment-setup.md`; read it before installing anything.

## Files in this repository

All three main files use `bylaws.cls` — the financial policy adds an `officerdoc`
class option, which makes its chapters "Policy N" and its title page carry a single
"Last revised" date. Nothing in this repository is a standalone LaTeX document.

All three currently build clean with zero unresolved references. If a build reports an
unresolved reference, you introduced it. Do not trust a remembered baseline of
"one known bad reference" — that was true of an earlier state of the repository and
is not true now. This is a live repository; check the tree rather than assuming.

One trap worth knowing before you switch anything to `final`: the class raises a
`\ClassError` when a `final` build lacks a date its title page needs
(`\chapteramendmentdate` and `\appendixamendmentdate` for the bylaws,
`\lastreviseddate` and `\officerdocumenttitle` for an `officerdoc`). The class-option
flip and the date update therefore belong in the same edit and the same ledger row.

## Which body amends what

The documents specify their own amendment procedures, and the bodies differ by *file
and by section*, not by document. Getting this wrong is not a typesetting problem: a
redline circulated to a body that cannot adopt it wastes a meeting, and an edit adopted
by the wrong body is not validly adopted at all.

Every specific body, threshold and clause citation lives in
`references/amendment-authority.md` — the file is organised as one section per
governing instrument plus a summary table, and it is the only place chapter-specific
governance facts are written down. Read it before you flag anything, so the flag quotes
the source rather than a recollection.

### The table is a cache; the tree is the authority

`references/amendment-authority.md` and the table above are *derived* from clauses
that are themselves amendable. They go stale two ways: someone amends an authority
clause outside this skill, or the amendment you are drafting right now changes one.
A flag quoted from a stale table is a confident false statement about who may adopt
something — worse than having said nothing.

So confirm before you quote. One command compares every verbatim quote in the summary
against the clauses as they currently stand:

```bash
python3 scripts/authority.py --repo <repo-root> --check
```

It exits 0 when they all match and 1 when any has drifted, naming the reference line,
where the quote stops matching, and what the tree says instead. Run it before quoting a
clause in a flag. If it reports drift, the tree wins: correct
`references/amendment-authority.md` and tell the user which entries moved — a changed
amendment clause is news, not a typo fix.

To read the clauses in full rather than just check them, drop `--check`.

And check whether your own edit disturbs them:

```bash
python3 scripts/authority.py --repo <repo-root> --touched <each file in your ledger>
```

Exit 1 means a file you are editing defines authority. When that happens: say plainly
which table entries the change would move, treat that as a consequential effect the
user should confirm rather than a detail, and rebuild
`references/amendment-authority.md` before anything downstream relies on it. Watch for
this especially on `bylaws/amendment.tex` § Appendix Amendment — the parked proposal
adding the Awards appendix to the Officer-Corps-discretion list would, if adopted,
move a whole appendix from one adopting body to another. And remember that amending
`bylaws/amendment.tex` at all escalates to constitutional thresholds, so an amendment
that changes the authority table is rarely a routine one.

If a clause cannot be read at all — the script reports a Dropbox placeholder or a
retitled section it can no longer match — do not fall back on the summary. Say the
clause is unreadable and skip the flag. Silence is recoverable; a wrong citation is
not.

`references/amendment-authority.md` carries the clauses verbatim — read it before
quoting one, so a flag cites the text instead of paraphrasing it, and re-derive it
whenever the script says it is stale.

### Flagging a wrong body

Do not recite thresholds, notice periods, or quorum rules unprompted — the user runs
this organization and does not need the lecture.

Do say something, in **one sentence**, when the body the user named cannot adopt what
they are editing, or when one amendment spans sections with different bodies. Name the
mismatch and the clause, then carry on and produce what they asked for. Examples of
the register:

> Worth noting: Appendix H is Officer Corps discretion under Bylaw IX.3, and chair
> removal is a 2/3 vote of the officers under Bylaw I § Chairs — a chapter vote is a
> heavier route than the text specifies. Redline is below either way.

> Heads up: the financial policies are amended by 5/7 of the Advisory Board
> (`bylaws/records.tex` § Spending Authority), so an officers' review won't adopt this.

This is a flag, never a refusal and never a gate. Build the redline they asked for.
They may have reasons — a chapter vote confers legitimacy the text does not require,
and an officer review before an Advisory Board vote is ordinary practice. Your job is
to make sure the mismatch was chosen rather than overlooked.

If the user's request does not name a body at all, infer nothing and say nothing. A
plain "strike the Apparel Chair" needs no governance commentary.
