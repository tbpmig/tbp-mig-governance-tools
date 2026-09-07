# Adapting this plugin to another Tau Beta Pi chapter

Built for Michigan Gamma. The skill body is chapter-neutral; the chapter-specific
material is deliberately isolated so another chapter can adopt it without rewriting the
workflow.

## What is chapter-specific

| File | What would change |
|---|---|
| `references/amendment-authority.md` | Everything. Bodies, thresholds, which appendices are officer-discretion, and every clause quotation. This is the main job. |
| `references/latex-conventions.md` — "Repository layout" and "Class options" | File names, the `officerdoc` option, the class's date macros, whether your class defines the redline macros. |
| `references/latex-conventions.md` — "Line style" | Only if your source uses a different convention. |
| `SKILL.md` — "Files in this repository" | The per-document summary and the note on build state. |
| `scripts/authority.py` — the `CLAUSES` table | The file paths and section names your amendment clauses live under. |

## What is not

`scripts/audit.py`, `scripts/redlines.py`, `scripts/build.sh` and `scripts/check_env.sh`
assume only that you use LaTeX with `changebar` and redline macros named
`\added` / `\removed` / `\changed`. The ledger-edit-audit discipline, the propose vs
finalize split, and the wrong-body flagging rule are all chapter-neutral.

## Suggested order

1. Rewrite `references/amendment-authority.md` from your own amendment clauses, quoting
   them verbatim. Do not paraphrase — the skill quotes this text back to officers.
2. Update the `CLAUSES` table in `scripts/authority.py` to point at those clauses, then
   run `authority.py --repo <your repo>` and confirm it extracts all of them.
3. Update the repository layout and class options in `references/latex-conventions.md`.
4. Run a proposal end to end and read the audit output before trusting it.
