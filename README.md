# TBP Michigan Gamma governance

Edits the chapter's governing documents — constitution, bylaws, appendices and
financial policy — with the rigor an amendment going to a vote requires.

## What it does

The documents live in the `TBP-C-B` LaTeX repository, and the diff is what people vote
on. This plugin makes Claude treat every edit as an amendment rather than a text
change:

- **Restates scope first.** Produces a ledger quoting the current text of every line it
  intends to change, and stops for your sign-off before editing.
- **Redlines rather than overwrites.** Wraps changes in the repository's own
  `\added` / `\removed` / `\changed` macros and builds a DRAFT-marked PDF for the vote.
  Resolving markup into adopted text is a separate step you have to ask for.
- **Audits its own diff.** Catches unsanctioned files, whitespace and line-style churn,
  stray blank lines that silently re-break a paragraph, unbalanced braces, empty redline
  macros, deleted labels that something still references, and — most usefully — shows
  what the governing text would actually say if the proposal passed.
- **Flags the wrong body.** Reads the amendment clauses out of the tree and says so, in
  one sentence, when the body you named cannot adopt what you are editing. It flags;
  it never blocks.
- **Keeps its own citations honest.** The clause quotations it cites are a cache of
  text that is itself amendable. A single command re-checks every quote against the
  repository and names any that have drifted, so an amendment to an amendment clause
  cannot leave Claude quoting repealed wording.

## Installing

Accept the plugin from the file card in Cowork. Nothing else is required — the skill
loads on its own when you mention the constitution, the bylaws, an appendix, a chair or
officer position, the financial policy, or a redline.

## What you need

A LaTeX toolchain and git. If either is missing, ask Claude to set up your environment
and it will check what is present and install only what is absent — BasicTeX plus the
specific packages on macOS, rather than the full 6 GB MacTeX.

The plugin finds the repository by looking for `bylaws.cls`, so a clone anywhere works.
If you keep it in Dropbox, Claude will warn you about online-only placeholders and git
contention; if you use a plain clone, it won't.

## Using it

Just describe the change. "Strike the Apparel Chair and give me the PDF for the vote."
"Rename Bylaw VIII Section 3 and swap the responsible officer." "The chapter approved
this on 12 March — finalize it."

Claude will come back with a ledger before it edits anything. Read it: that is where a
misidentified section surfaces cheaply, before it becomes a diff.

## What it deliberately will not do

- Reformat, rewrap, or tidy anything you did not ask it to change, even when invited.
  Cosmetic churn buries the amendment.
- Convert a file's line style during an amendment. The bylaws and constitution are
  one sentence per line; the financial policy is not. The skill matches whichever the
  file uses and never converts as a side effect.
- Fix typos or defects it notices in adopted text. It reports them so they can go to a
  vote as their own amendment.
- Push, or open a pull request. It branches and commits; the remote is yours.

## Chapter specificity

Everything specific to Michigan Gamma — the bodies, thresholds, appendix labels and
clause citations — is confined to `references/amendment-authority.md`. Another chapter
adopting this would rewrite that one file, plus the repository-layout section of
`references/latex-conventions.md`. The skill body itself is chapter-neutral.

Those governance facts are a cache of clauses that are themselves amendable, so the
skill re-reads them from the tree before quoting, and warns when an edit touches a
clause that would move them.

## How this repository stays honest

The skill quotes the chapter's amendment clauses verbatim, so that when it tells an
officer which body may adopt something it cites real text. Those clauses live in
[tbpmig/TBP-C-B](https://github.com/tbpmig/TBP-C-B) and are themselves amendable, so
the quotes go stale silently — and a stale quote is worse than no quote, because it
cites repealed wording with full confidence. That has already happened once.

A workflow guards it. On every push and pull request, and weekly on Mondays, CI clones
the governing documents and checks two things:

- that every verbatim quote still matches the tree, and
- that every clause can still be located where the skill says it is, which catches a
  section being renamed or moved while its wording stays put.

The dependency points one way. TBP-C-B knows nothing about this repository and needs
no configuration, no token and no workflow of its own. Nobody has to remember anything:
an amendment to a quoted clause turns this repository's build red within a week.

When it goes red, the tree is authoritative and this repository is the cache. Update
`skills/tbp-governing-docs/references/amendment-authority.md` to match — and say which
entries moved. A changed amendment clause is news, not a typo fix: it may mean a
different body now adopts something.

## Building the plugin file

```bash
tools/package.sh          # writes dist/tbp-mig-governance.plugin
```

Every green CI run also uploads that file as a build artifact, so a future officer can
download a known-good build from any passing run rather than hunting for something
someone sent in chat.

## Releasing a new version

1. Make the change and update `version` in `.claude-plugin/plugin.json` (semver).
2. Open a PR. CI checks the clause quotes.
3. Merge, then tag: `git tag v0.1.5 && git push --tags`.
4. Attach `dist/tbp-mig-governance.plugin` to a GitHub Release so officers have a
   stable download.

Officers install by accepting the `.plugin` file in Cowork. They do not need to clone
this repository, and cloning it does not install anything.
