---
id: functional-proof-skip-policy-inconsistent
owner: architect
type: defect
created: 2026-08-20
priority: 40
---
# functional_proof.sh gives two different answers to "what does a skipped check score"

Same script, two skip policies:

- **`:365`** — in LOCAL_MODE, check 7 (www->apex) is skipped and recorded
  **PASS**.
- **`:215-217`** — when `node` is unavailable, check 3 is skipped and recorded
  **FAIL**, with the reasoning that a skipped check leaves the gate's
  completeness unproven.

Both cannot be right. The `:186-190` reasoning is the correct one and is
already written down: an unrun check is not a passed check, and scoring it PASS
makes the summary line claim coverage the run does not have.

The practical risk is a LOCAL_MODE run reporting **7/7 PASS** while having
actually executed six checks — which is precisely the "green means nothing"
failure this gate exists to prevent.

**Proposed fix (not applied):** introduce a third outcome, `SKIP`, that is
neither PASS nor FAIL, print it distinctly, and make the summary state
`N passed / M skipped` rather than folding skips into either bucket. Exit
non-zero only on real failures, but never let a skip read as coverage.

## Verification command
```bash
sed -n '210,220p;360,368p' /Users/vongimbel/code/denvercoloradoinsulation.com/ops/functional_proof.sh
# compare the two skip branches: one records PASS, the other FAIL
```
