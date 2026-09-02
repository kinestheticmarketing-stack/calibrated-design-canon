---
id: phase8-calculator-criterion-unmet
owner: architect
type: defect
created: 2026-08-20
priority: 30
doc: METHODS/PROPERTY_GENESIS.md
retriage: 2026-10-02
classification: ARCHITECT
---
**Classification reasoning (2026-09-02):** A technical, reversible choice between two implementation paths for a documentation/gate mismatch — the card itself already frames it as "Architect's call" and already carries `owner: architect`; no tradeoff requires Director judgment.

# PHASE 8's calculator criterion is not met by the gate that claims to satisfy it

`METHODS/PROPERTY_GENESIS.md` PHASE 8 requires that a calculator
**produce a correct figure on default inputs, with that figure recorded in the
launch record** — and argues explicitly that recording the number is what makes
the check falsifiable, because a tool whose script never loaded throws nothing
at all.

`ops/functional_proof.sh` CHECK 3 proves only that the page returns 200, that
its inline JS parses under `node --check`, and that `addEventListener > 0`.
It never runs a calculation and never records a figure.

So the shipped gate satisfies the weaker of the two claims PHASE 8 says must be
kept separate: it proves "the page returned 200", not "the page works".

**Not a regression** — the gate was always this. The defect is that PHASE 8 was
written asserting a criterion the gate does not implement, so a future genesis
reading PHASE 8 would believe its calculators were proven functional when only
their syntax was.

**Two honest options, Architect's call:**
1. Implement it — drive each calculator headlessly, read the computed figure
   out of the DOM, and write it into the launch record. Costs a browser
   dependency in a script that is currently pure fetch+parse.
2. Weaken PHASE 8's wording to match what the gate actually proves, and move
   the figure-recording requirement to the browser canary, which already
   drives real Chrome.

Do not close by quietly editing PHASE 8 to match the code — that is the
direction that loses information.

## Verification command
```bash
grep -n "addEventListener" /Users/vongimbel/code/denvercoloradoinsulation.com/ops/functional_proof.sh
# CHECK 3 asserts listener count only; no figure is computed or recorded
```

## R2 update — 2026-09-02 — decision made, execution blocked/deferred

**Re-verified the defect is still live.** `ops/functional_proof.sh` CHECK 3
(denvercoloradoinsulation.com, current HEAD) still only counts
`addEventListener` occurrences (lines 245-248) and never runs a calculation
or records a figure — matches the card's description exactly, unchanged.

**Found something the card doesn't say:** `METHODS/PROPERTY_GENESIS.md`
(lines 1420-1442, inside the Rule 10-family discussion) already contains a
"live instance inside this document" writeup of this exact defect,
word-for-word consistent with this card, and it explicitly ends: *"Tracked
at `docs/board/ready/phase8-calculator-criterion-unmet.md` and deliberately
left open here."* Canon's own text already refuses to resolve this by
silent doc-editing — it is cross-referencing this card by design, not an
oversight. That sentence is strong evidence this card is meant to stay open
until one option is actually implemented, not decided-and-closed on paper.

**Architect's call, decided:** **Option 2** — weaken PHASE 8's wording to
match what `functional_proof.sh` actually proves, and move the
figure-recording requirement into `ops/browser_canary.js`. Reasoning:
`browser_canary.js` is already portfolio infrastructure that "already
drives real Chrome" and exists specifically to close what a fetch+parse
canary structurally cannot see (ground-truth.md: "closing what the daily
POST canary structurally cannot see (form render, client JS execution)")
— reading a computed DOM figure is exactly a client-JS-execution concern,
so Option 2 relocates the requirement to the tool already built for this
class of check, rather than duplicating a browser dependency into a script
whose value is being pure fetch+parse (Option 1's cost). This is a
relocation, not a deletion — the requirement is not weakened into nothing,
which is what the card's "do not close by quietly editing" warning guards
against.

**Why this is not executed, and why the card is not moved to done/:**
Implementing this decision needs two edits, both out of reach this row:
1. `METHODS/PROPERTY_GENESIS.md` PHASE 8's wording (lines ~863-875) and the
   line-1420-1442 "live instance" writeup — under this row's explicit
   constraint not to touch anything under `METHODS/`.
2. `ops/browser_canary.js` in `denvercoloradoinsulation.com` — a DCI-repo
   code change, out of scope for a canon-only row and not this row's repo
   to touch (a sibling row is working DCI's own board in parallel).

Both paths block on territory this row cannot enter, not on any remaining
ambiguity in the decision itself. **Reporting as blocked/deferred per this
row's instructions rather than touching either.** Card stays in `ready/`,
`classification: ARCHITECT` unchanged, with the decision now on record so a
future row that can touch `METHODS/` and/or the DCI repo does not have to
re-derive it.
