---
id: needle-scoped-verification
owner: architect
type: defect
created: 2026-08-21
priority: 1
---
# A check built from the same pattern as the edit measures the edit's assumptions, not the world

**The wave's worst defect. It survived six Auditor gates.**

R3 removed the false `$400` air-sealing rebate figure using the needle
`$400 for air sealing`. V3 then verified the removal using **the same needle**
and reported `DCI $400 = 0`.

That result was **true of the needle and false of the figure.**
`xcel-insulation-rebate-guide-denver.html` phrased it:

> "…the base program covers three measures for customers who heat with Xcel
> service: attic insulation at 30% of project cost up to **$500**, wall
> insulation at 30% up to **$350**, and air sealing at 30% up to **$400**."

A complete, correct enumeration — carrying the false figure in a phrasing the
needle never matched. It was live through every prior gate, and every gate
reported clean, because the check inherited the edit's blind spot exactly.

**A check constructed from the edit's own matcher cannot find what the edit
missed. It is not measuring the world; it is measuring the edit's assumptions
back to itself, and returning them as confirmation.**

## Why the other instruments could not catch it either

- **Complement-scoped occurrence diff (D3)** hunts content that DECREASED. This
  content never changed — it was never touched.
- **Positive-presence (V4)** asserts anchors survive. This survived; that was
  the problem.
- **Ledger reconciliation (V9)** checks changed files. The file was never changed.
- **Grammar certification (V11)** never saw it.

Every instrument was scoped to the change set. This defect lived in the
complement of the change set *and did not move* — invisible to a diff by
construction.

## The rule — Principle 9

**A verification instrument must be constructed INDEPENDENTLY of the edit
instrument.** If the check and the edit share a pattern, the check confirms the
edit's assumptions rather than the world's state.

**Derive the check from the TARGET CONCEPT, never from the edit's matcher.**
Here the concept is *"a dollar figure asserted as a rebate amount"* — so the
correct check sweeps for **bare `$400`, `$500`, `$350` in any phrasing** and
classifies each occurrence as rebate-figure or cost-range, rather than
searching for the string the edit happened to target.

Run that way, the same corpus that reported `0` reported **9 surviving figure
instances on DCI**, including three malformed sentences the removals themselves
had produced.

## Corollary

The edit's matcher and the check's matcher should be written by different
reasoning, ideally at different times. An instrument authored immediately after
an edit, by the same reasoning that produced it, is co-extensive with that
edit's blast radius — the same failure Principle 7 names for exclusions, here
applied to the matcher itself.

## Verification command
```bash
cd /Users/vongimbel/code/denvercoloradoinsulation.com
# concept-derived, not needle-derived: every bare figure, classified
python3 - <<'PY'
import os,re
for f in sorted(os.listdir('public')):
    if not f.endswith('.html'): continue
    x=re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',open('public/'+f,errors='ignore').read()))
    for fig in ('400','500','350'):
        for m in re.finditer(r'\$'+fig+r'\b',x):
            rng=re.search(r'\$'+fig+r'\s*(?:to|-|–)\s*\$',x[m.start():m.start()+30])
            if not rng: print(fig,f,x[max(0,m.start()-70):m.end()+70])
PY
# expect: only the "$400 audit" cost on insulation-energy-audit.html
```
