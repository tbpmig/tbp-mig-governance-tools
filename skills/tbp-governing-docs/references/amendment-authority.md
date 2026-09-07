# Who may amend what

Verbatim clause text, so a flag you raise can quote the source rather than paraphrase
it.

**This file is a cache, not the authority.** Every clause below is transcribed from
the `.tex` files, and those clauses are themselves amendable — including by the very
amendment you may be drafting. If a quote here disagrees with the tree, the tree is
right and this file is stale.

Confirm before quoting, and re-check after editing:

```bash
python3 scripts/authority.py --repo <repo-root> --check    # do these quotes still match?
python3 scripts/authority.py --repo <repo-root>            # print the current clauses
python3 scripts/authority.py --repo <repo-root> --touched <ledger files>
```

The second form exits 1 when a file you are editing is one of the sources below, which
is your signal to rebuild this file and to tell the user which entries moved.

**Sources this file is derived from** — edit any of these and this summary needs
rebuilding:

- `constitution/amendments.tex` — the whole chapter
- `constitution/government.tex` — Chapter Voting Meetings → Bylaws
- `bylaws/amendment.tex` — the whole file
- `bylaws/government.tex` — Chairs; `sec:AdHocCreation`; `sec:AdHocCommitteeCreation`
- `bylaws/records.tex` — Spending Authority

One live example of why this matters: `bylaws/amendment.tex` currently carries a
commented-out parked proposal, `% \added{, and Appendix \ref{sec:awards} (Awards)}`.
If that is ever adopted, the Awards appendix moves from the ordinary bylaws process to
Officer Corps discretion, and every table below that mentions appendix authority is
wrong until rebuilt.

## Contents

- [Constitution](#constitution)
- [Bylaws chapters](#bylaws-chapters)
- [The amending procedure itself](#the-amending-procedure-itself)
- [Appendices](#appendices)
- [Chairs: the creation/removal asymmetry](#chairs-the-creationremoval-asymmetry)
- [Ad hoc officers and committees](#ad-hoc-officers-and-committees)
- [Financial policies](#financial-policies)
- [Two subtleties that are easy to get wrong](#two-subtleties-that-are-easy-to-get-wrong)
- [Summary table](#summary-table)

## Constitution

`constitution/amendments.tex`:

> **Proposal.** Amendments to the Constitution may be proposed by any active member of
> the chapter.
>
> **Notice.** Amendments to the Constitution must be presented to the membership at
> least 3 business days before the meeting at which a vote is to occur. Amendments may
> be amended during the meeting without violating this requirement. In the event that
> the vote is to take place at a meeting other than a regularly scheduled chapter
> voting meeting, notice of at least 2 weeks must be provided for the meeting.
>
> **Adoption.** Any proposed amendment may be adopted by the approval of at least three
> fourths of those present and entitled to vote at a chapter voting meeting and by an
> affirmative vote of 5/7 of the Advisory Board. Such votes must occur within 14 days
> of each other.

Also in that file, a standing obligation unrelated to any particular amendment:

> **Review.** This Constitution will be re-approved every five years, on years ending
> in 0 or 5, by a majority vote of the advisory board, regardless of changes.

## Bylaws chapters

`bylaws/amendment.tex`:

> **Amendment.** The Chapter Bylaws may be amended upon the affirmative vote of 2/3 of
> the total active membership and an affirmative vote of a majority of the Advisory
> Board. Such votes must occur within 14 days of each other.

**The denominators differ from the constitution's, and this is the trap.** The
constitution needs three fourths *of those present and entitled to vote*. The bylaws
need two thirds *of the total active membership* — every active member who does not
attend counts against it. The bylaws threshold is materially harder to clear despite
being the smaller fraction, and an amendment that comfortably passes a constitutional
vote can fail a bylaws vote at the same meeting.

## The amending procedure itself

`constitution/government.tex`, Chapter Voting Meetings → Bylaws:

> The chapter membership may enact Bylaws for the chapter, at any voting meeting. The
> procedure for enactment, or for amendment of the amending procedure of such Bylaws,
> must follow the same requirements for amending this Constitution.

So editing `bylaws/amendment.tex` — changing how the bylaws are amended — escalates to
the constitution's thresholds even though the file lives under `bylaws/`. Path is not
authority. Flag this if the user proposes it under bylaws thresholds.

## Appendices

`bylaws/amendment.tex`, § Appendix Amendment:

> Appendix (Electee Requirements), Appendix (Graduate Electee Requirements), Appendix
> (Alumni Electee Requirements), Appendix (Distinguished Active Status Guidelines), and
> Appendix (Prestigious Active Status Guidelines) may be modified at the discretion of
> the Officer Corps. Appendices [Ad Hoc Officers], [Ad Hoc Committees], and [Chairs]
> may be modified at the discretion of the Officer Corps per the procedures outlined in
> Bylaws [AdHocCreation], [AdHocCommitteeCreation], and [ChairCreation] respectively.

Labels, in source order: `sec:ugradreqs`, `sec:gradreqs`, `sec:alumnireqs`,
`sec:DAstatus`, `sec:PAstatus` — plain Officer Corps discretion. Then
`sec:AdHocOfficers`, `sec:AdHocCommittees`, `sec:Chairs` — Officer Corps discretion
*subject to the named bylaw procedures*, which add conditions.

**This list is exhaustive.** `bylaws/appendices.tex` also contains the Officer
Requirements and Descriptions appendix (`sec:officerreq`) and the Committees appendix
(`sec:committees`, including `sec:standingCommittees`), and neither is enumerated
above. Editing those follows the ordinary bylaws process — chapter vote plus Advisory
Board — not Officer Corps discretion. Being inside `appendices.tex` is not itself a
grant of authority.

## Chairs: the creation/removal asymmetry

`bylaws/government.tex`, § Chairs:

> **Creation.** Chair positions may be created by the officer corps or the chapter
> membership by a simple majority vote at any time. Chair positions may exist for any
> length of time, though chairs should be appointed at least semesterly.
>
> **Dissolution and Removal.** Chair positions may be removed at any time by a 2/3 vote
> of the officers. Additionally, persons serving as chairs may be removed from their
> position by a majority vote of the officers.

Creation names two possible bodies. Removal names only the officers, and sets a higher
bar than creation (2/3 rather than simple majority). Note what the text does *not* say:
it does not expressly forbid the chapter from removing a chair. Describe the mismatch
as "a heavier route than the text specifies" rather than asserting the chapter lacks
the power — that reading is available but it is an inference, not a quotation.

`sec:ChairCreation` in the same file adds the requirements a chair position must meet:
listed in the Chairs appendix, placed on the Events or Chapter Team, and reporting to a
named Officer.

## Ad hoc officers and committees

`bylaws/government.tex`, `sec:AdHocCreation`:

> May, with Advisory Board approval, create ad hoc officer positions.

with the term limits:

> May only last for two academic terms, after which time they must be approved by the
> chapter membership. This can be either as a permanent officer position, or as an
> extension of the ad hoc position. An extension of the ad hoc position requires a
> simple majority vote of the chapter membership, and may not be for longer than
> another two terms. An officer position may not exist in an ad hoc state for more than
> four consecutive terms. Any ad hoc position that has existed for four consecutive
> terms cannot be recreated as ad hoc without a gap of at least two terms.

`sec:AdHocCommitteeCreation`:

> In addition to the standing committees, the officer corps, with Advisory Board
> approval, may create ad hoc committees.

So "Officer Corps discretion" for these two appendices is not unilateral — the
Advisory Board is in the loop, and ad hoc officer positions have a shelf life that the
chapter membership must renew. If a user proposes an ad hoc position for a third
consecutive term, that needs a chapter vote, and it is worth one sentence.

## Financial policies

`bylaws/records.tex`, § Spending Authority:

> All expenditures must be made in accordance with the Chapter's Financial Policies;
> the Chapter's Financial Policies must be approved or amended by 5/7 of the Advisory
> Board.

The financial policy document contains no amendment clause of its own — the authority
is stated in the bylaws. The amending body is the **Advisory Board alone**: not the
Officer Corps, not the chapter membership, despite the document being an officer
document in its class options. A request to circulate a financial policy change "for
the officers to review" is a body mismatch worth flagging, though officer review ahead
of an Advisory Board vote is perfectly ordinary practice and not an error in itself.

## Two subtleties that are easy to get wrong

**The constitution and the bylaws count different denominators.** The constitution
needs ¾ *of those present and entitled to vote*; the bylaws need ⅔ *of the total active
membership*. The bylaws threshold is materially harder to clear despite being the
smaller fraction, because every active member who does not attend counts against it.
An amendment can comfortably pass a constitutional vote and fail a bylaws vote at the
same meeting.

**Chairs can be created by either body but removed only by the officers.** Creation:
"Chair positions may be created by the officer corps or the chapter membership by a
simple majority vote at any time." Removal: "Chair positions may be removed at any time
by a 2/3 vote of the officers." The removal clause names only the officers, and sets a
higher bar than creation. So taking a chair *removal* to a chapter vote uses a route
the text does not specify, even though a chapter vote would have been fine to create
the same position. Note what the text does not say: it does not expressly forbid the
chapter from removing a chair. Describe this as "a heavier route than the text
specifies" rather than asserting the chapter lacks the power — that reading is
available, but it is an inference, not a quotation.

## Summary table

| Editing | Adopting body | Source |
|---|---|---|
| `constitution/*.tex` | ¾ of those present **+** 5/7 Advisory Board, ≤14 days apart | `constitution/amendments.tex` |
| `bylaws/*.tex` chapters | ⅔ of total active membership **+** Advisory Board majority, ≤14 days apart | `bylaws/amendment.tex` |
| `bylaws/amendment.tex` itself | constitutional thresholds | `constitution/government.tex` |
| Appendices A–E | Officer Corps discretion | `bylaws/amendment.tex` |
| Ad hoc officers appendix | Officer Corps **+ Advisory Board approval**; chapter renewal after 2 terms | `bylaws/government.tex` |
| Ad hoc committees appendix | Officer Corps **+ Advisory Board approval** | `bylaws/government.tex` |
| Chairs appendix — create | officer corps **or** chapter membership, simple majority | `bylaws/government.tex` |
| Chairs appendix — remove | 2/3 of the officers | `bylaws/government.tex` |
| Officer Requirements / Committees appendices | ordinary bylaws process | not enumerated in § Appendix Amendment |
| `financialpolicy/*.tex` | 5/7 of the Advisory Board | `bylaws/records.tex` |
