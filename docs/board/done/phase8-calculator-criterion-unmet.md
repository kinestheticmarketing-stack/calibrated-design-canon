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

## Outcome — 2026-09-03 — CLOSED, Option 2 executed

**Wording changed (`METHODS/PROPERTY_GENESIS.md`, canon commit below).**
The PHASE 8 calculator bullet no longer claims the launch gate proves a
computed figure. It now opens "Every calculator loads, ships parseable
JavaScript, and binds its listeners — proven from production by
`ops/functional_proof.sh` CHECK 3: the page returns 200, every inline
script parses under `node --check`, and `addEventListener > 0`," states
that this is exactly what the gate proves and no more, and assigns the
figure-on-default-inputs-with-the-figure-recorded claim to the browser
canary (`ops/browser_canary.js`, weekly, all three properties). The
"200 vs works" reasoning, the Greeley incident, and the "identify tool
pages structurally, never by slug" content are all kept. The Rule-10
"live instance inside this document" paragraph is kept as the record and
now ends with a dated resolution sentence.

**Code changed (`denvercoloradoinsulation.com` commit `3254647`).**
`ops/browser_canary.js` gained `runCalculators()` — tool pages identified
structurally (sitemap slug narrows, out-of-form `<input>`/`<select>`
controls decide, exactly as `functional_proof.sh` does), trigger = the
out-of-form button nearest the controls, result = the innermost `[id]`
element whose text the click changed, figure = numeric tokens in it.
Statuses `ok` / `verdict` (qualitative tool, all defaults set) /
`needs-input` (the page's own validation asked for input); anything else
is `calculator-no-figure` and alerts like every other step. Figures are
logged per page and as one JSON `[browser-canary] figures {...}` line.

**Proven in the real execution path (canon Pattern 14), 2026-09-03.**
Deployed to `/root/denvercoloradoinsulation.com/ops/browser_canary.js`
(md5 `1d2262ca1146247400aaf86366d503e4` local == VPS, backup
`browser_canary.js.bak.20260903-pre-phase8` left beside it),
`systemctl start browser-canary.service` exit 0, `ExecMainStatus=0`.
Recorded: DCI 6 tools (4 figures, 1 verdict, 1 needs-input — the rebate
checker requires a service to be ticked), Greeley 4 tools (all
needs-input — every Greeley tool opens on an empty placeholder option;
confirmed by reading their JS), Longmont 4 tools (2 figures, 2 verdicts).
The failure branch fired for real during local testing (before the
`verdict` status existed it flagged the quiz), so it is known to alert.

**Verification commands**
```bash
grep -c 'runCalculators' /Users/vongimbel/code/denvercoloradoinsulation.com/ops/browser_canary.js   # -> 3
grep -c 'figure' /Users/vongimbel/code/denvercoloradoinsulation.com/ops/browser_canary.js           # -> 20 or more
grep -n 'binds its' /Users/vongimbel/code/calibrated-design-canon/METHODS/PROPERTY_GENESIS.md      # -> the PHASE 8 bullet, one hit
grep -n 'Resolved 2026-09-03 via Option 2' /Users/vongimbel/code/calibrated-design-canon/METHODS/PROPERTY_GENESIS.md   # -> the live-instance paragraph
ssh root@74.208.181.10 'journalctl -u browser-canary.service --since 2026-09-03 --no-pager | grep -c "calculator "'   # -> 14 per run
```

**Commits.** DCI `3254647` (canary). Canon: this card's move and the
PROPERTY_GENESIS edit land together in the commit recorded in
`docs/lanes.md` row `board-drain-2026-09-03-canon`.

