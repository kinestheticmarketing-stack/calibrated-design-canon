# CANDIDATE PRINCIPLE — a commit message is a claim and carries the same burden

**Drafted 2026-08-24. NOT merged into `PROPERTY_GENESIS.md`.**

## The principle

**A commit message asserting a fix is a claim, and carries the same burden of
proof as any other claim.**

An unverified assertion in the permanent record is **worse** than one in prose,
because a future session reads `git log` as settled history. Prose gets
questioned. A commit message gets cited.

## The evidence

In one sweep on 2026-08-24, **three of eight defect classes shipped with a false
statement in the commit that fixed them**:

1. *"the tool no longer scores a homeowner as 'at code' at R-49"* — it still
   did, in the hidden lead payload. The commit changed the two visible lines.
2. *"recovered exactly"* — 63 lines of whitespace damage remained.
3. *"residue fixed at the template"* — fixed in one template of three.

**None was caught by a gate.** The gates were working: a credential checker
blocked a bad phrasing, and an atomic-answer word-count gate blocked an
over-long edit. Both were right. **Neither had any opinion about whether the
commit message was true**, because no gate reads it.

All three were caught by a **reader who was not the writer**, days of work
later, after the false claims had already been cited downstream.

## The proposed step

Any commit message asserting that something is fixed must **name the
verification command that proves it**, and that command must be **run and its
exit code recorded** before the commit lands.

```
Fixes: <one-line claim>
Verify: <command>
Result: exit 0 at <sha-or-tree>
```

The command must test the **claim**, not a proxy for it. Two failures from the
same sweep show how easily this degrades:
- a check tested for **zero** citations when the documented floor was **three**;
- a check for a removed string returned **zero** while the claim survived in
  prose that never used the string.

**A verification that passes vacuously is worse than none**, because it reads as
coverage.

## Where this bites hardest

Claims about **absence** — "removed sitewide", "no page still says X", "the
class is closed". Absence cannot be shown by a grep returning zero; see the
companion candidate on scoping with grep over rendered HTML. Pair the two: this
one demands a verification, that one constrains what counts as one.

## Open question for the Director
Whether to enforce this with a `commit-msg` hook, or leave it a discipline. A
hook can require the `Verify:` line to be present; it cannot check that the line
is honest. The hook buys the habit, not the truth.
