---
id: phase8-calculator-criterion-unmet
owner: architect
type: defect
created: 2026-08-20
priority: 30
doc: METHODS/PROPERTY_GENESIS.md
retriage: 2026-10-02
---
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
