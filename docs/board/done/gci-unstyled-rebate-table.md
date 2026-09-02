---
id: gci-unstyled-rebate-table
owner: executor
type: defect
created: 2026-08-21
priority: 50
---
# GCI's rebate table renders unstyled on the property's core commercial asset

`class="cmp"` is emitted with no `.cmp` rule anywhere; `CSS_TABLE` defines
`.compare` and is never emitted. Live, on the money page.

Surfaced during LLS Wave 1 and again in the 2026-08-21 content-defect wave.
CSS/visual is out of scope in both. **Card only — do not fix without a ruling.**

## Closed 2026-09-02 — ALREADY-DONE

Already fixed in the GCI repo (not touched today) by pre-existing commit
`0192f01` ("GCI fix pass 1: the citation apparatus, the unstyled money-page
table, a logic bug"), which predates this session.

Verification, run directly against the GCI repo:

    grep -c '\.compare {' public/insulation-rebate-hub.html   # -> 1
    grep -o 'class="compare[^"]*"' public/insulation-rebate-hub.html | sort -u
    # -> class="compare"
    # -> class="compare-wrap"
    grep -rn 'class="cmp"' public/ _shared_components.py _generate_rebate_hub.py
    # -> no matches anywhere

`.compare`/`.compare-wrap` classes and their CSS rules are live in
generated output; `class="cmp"` does not exist anywhere in the codebase.
No canon or GCI code changed as part of this closure — the ruling this
card asked for was effectively already applied, just never carded closed.
