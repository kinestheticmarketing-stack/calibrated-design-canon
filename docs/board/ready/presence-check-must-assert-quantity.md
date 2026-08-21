---
id: presence-check-must-assert-quantity
owner: architect
type: defect
created: 2026-08-21
priority: 10
---
# V4 is the sixth blind instrument — a presence check that counts pages, not occurrences

V4 was added specifically to catch content that vanishes beside a removal
target. It was blind to exactly that.

**What it reported:** `CFM50  S0=17  now=17  OK`, all three properties.

**What was true at that moment:** three LGM area pages had lost two-thirds of
their occurrences —

| page | CFM50 | participating contractor | reduced tier |
|---|---|---|---|
| `insulation-lafayette` | 5 -> 3 | 4 -> 2 | 4 -> 2 |
| `insulation-louisville` | 3 -> 1 | 3 -> 1 | 3 -> 1 |
| `insulation-niwot` | 3 -> 1 | 3 -> 1 | 3 -> 1 |

No page dropped to zero, so no page left the "contains the anchor" set, so V4
saw 17 both times and passed.

**The instrument asserted the wrong quantity.** It protected *presence
somewhere on the page* while the thing at risk was *how much of it survived*.

Caught instead by an occurrence-level sentence-inventory diff, which the
Auditor demanded after the count in the report failed to move.

## Proposed principle — PROPERTY_GENESIS candidate, third of three

**A presence check must assert the QUANTITY it is protecting, not merely
non-zero presence.** If the risk is partial loss, page-level membership is the
wrong unit. Count occurrences, compare against the pre-change snapshot, and
fail on any decrease that is not an enumerated target.

Corollary, and the reason this keeps recurring: **an instrument added to catch
a specific failure must be canary-proved against that failure**, not against
its own happy path. V4 had a positive canary (delete an anchor entirely, prove
it flags). It never had one for partial loss, which is the case it existed for.

Fold into `documented-standard-with-no-validator` as principle 3.

## Verification command
```bash
cd /Users/vongimbel/code/longmontcoloradoinsulation.com
for p in insulation-lafayette insulation-louisville insulation-niwot; do
  printf '%s S0=%s now=%s\n' "$p" \
    "$(grep -c CFM50 /tmp/predefect_LGM/$p.html)" "$(grep -c CFM50 public/$p.html)"
done   # must match; page-level presence would pass either way
```
