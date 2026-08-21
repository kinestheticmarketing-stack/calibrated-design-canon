---
id: removing-a-false-member-creates-a-false-set
owner: architect
type: defect
created: 2026-08-21
priority: 5
---
# Removing a false member from a true set creates a false set

The wave's most generalizable finding.

R3 removed `$400 for air sealing` from enumerations reading:

> "pays 30% of project cost, up to $500 for attic insulation, $350 for wall
> insulation, **and $400 for air sealing**"

The figure was false — Xcel's own sheet states $200. But **air sealing is a
covered measure**: the program is literally named the *Xcel Energy Insulation
and **Air Sealing** Rebate*, on 72 DCI pages, with 296 surviving mentions tying
air sealing to rebate eligibility.

So the corrected sentence enumerated **two** covered measures where **three**
exist. It read perfectly. Every grammar check passed. **And it asserted, by
omission, that air sealing is not covered — which is also false.**

**Removing a false figure from an enumeration can create a false enumeration.**
The removal was correct; its *effect on the set* was not evaluated, because
nothing evaluated meaning.

## Two instances that refuted themselves inside one sentence

`insulation-duct-sealing.html`:
> "…up to $500 for attic insulation and $350 for wall insulation, by check
> after application, **and its named measures are insulation and air sealing.**"

`insulation-radiant-barrier.html`:
> "…caps of $500 for attic insulation and $350 for wall insulation — **and a
> radiant barrier is not one of the measures it names.**"

The second was cleared as "RC-1 step 1, no meaning added" one turn earlier, on
a check of the anaphor's grammar. Grammar was fine. The enumeration was a lie.

## Why the instruments could not see it

Every check hunts content that **disappeared**. A truncated enumeration is
content that **remained** and became false by losing a neighbour. It is
invisible to occurrence diffs, presence checks, ledger reconciliation and
grammatical certification alike — all of which were green.

## The rule this produced — RC-8

> After any removal, the containing sentence must be evaluated for what it now
> **ASSERTS**, not merely whether it reads. If removal leaves a different claim,
> remove the whole claim. If removal drops a member from an enumeration that is
> still a member, the enumeration now lies by omission and the instance HALTS.
> **Grammar is not truth.**

## Remedy applied (Director ruling, Option 2)

Drop the enumeration, keep the program. Not "restore the true figure" — $200 is
unsourced in-repo exactly as $400 was, so that would fix a B6 violation by
committing another. Not "a separate cap for air sealing" — a phrase no source
supports. **Option 2 dissolves the truncation rather than completing it: with
no enumeration there is no omission.**

## Verification command
```bash
cd /Users/vongimbel/code/longmontcoloradoinsulation.com
grep -c "per-measure cap" public/*.html | grep -v ':0' | wc -l   # the supportable form
grep -rn 'up to \$500 for attic insulation, \$350' public/*.html  # expect none
```
