---
id: v9-cannot-see-page-scoped-bars
owner: architect
type: defect
created: 2026-08-21
priority: 15
---
# V9 is the seventh blind instrument — it reconciles FILES, so a page-scoped scope bar is invisible to it

The 2026-08-21 kickoff's OUT OF SCOPE list read:

> DO NOT TOUCH: the two LGM doorway pages (lafayette 37.1%, niwot 39.3%)

R2's edits changed both pages. V9 reported "LGM 27 files, every rendering
instance accounted for" and **did not halt**.

## Which reading is true: (i)

The S-GATE ledger is **file-scoped** — it lists `_area_pages.py`, which renders
`insulation-lafayette.html` and `insulation-niwot.html` among others. Those
files were on the ledger. So the ledger did not omit anything, and V9's halt
condition ("any unlisted file HALTS") correctly did not fire.

**The ledger silently superseded the kickoff's own page-scoped scope bar, and
the Final Report never said so.** That is the defect: not a missed halt, but a
scope bar that no instrument in the V-series was capable of enforcing.

## Why this is structural, not an oversight

V9 answers "was every CHANGED FILE on the ledger." A page-scoped exclusion asks
"was any FORBIDDEN PAGE changed." Those are different questions over different
units, and in a generator-driven codebase the mapping is one-to-many: one
source file renders many pages, so a file-scoped permission grants page-scoped
access it was never asked to grant.

**No instrument in V1-V12 checks rendered-page-level scope bars.** V9 is the
one that makes the ledger mean anything, and this class is outside its reach.

## Content impact: neutral, stated for completeness

Both pages carry only the legitimate multiplier removal, and the two
over-captured sentences were restored byte-identical (VF1: niwot 3/3/3,
lafayette 5/4/4, matching S0). Nothing improper shipped. The finding is about
the instrument, not the outcome.

## Proposed fix — NOT applied

When a scope bar names PAGES, the S-GATE must derive the FILES that render
them and either (a) mark those files no-touch, or (b) record explicitly that
the bar is superseded because a listed file renders a barred page, with the
Director ruling on it at the gate. Add a V-series check that maps changed
rendered pages back against any page-scoped bar.

## Verification command
```bash
cd /Users/vongimbel/code/longmontcoloradoinsulation.com
git show 00b2d56 --name-only --format="" | grep -E 'insulation-(lafayette|niwot)'
# both appear; the ledger listed _area_pages.py, not these pages
```
