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
