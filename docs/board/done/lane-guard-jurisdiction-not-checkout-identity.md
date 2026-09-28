---
id: lane-guard-jurisdiction-not-checkout-identity
owner: director
type: design-decision
created: 2026-09-28
retriage: 2026-10-28
size: M
severity: medium
---
# The lane guard enforces jurisdiction, not checkout identity, so two CLAUDE.md rules are unenforced

**Unblocking action: the Director decides whether the lane guard should
enforce CHECKOUT IDENTITY in addition to jurisdiction — and if so, how the
integrator lane is exempted.**

Surfaced 2026-09-28 by the adversarial verification reader on the harness
hardening pass, and verified before this card was written. Not a bug in the
code as written; a consequence of the model that nobody had written down.

## What the guard actually asks

Both halves of the lane guard — H9 (`Edit`/`Write`) and H19 (shell commands) —
ask exactly one question:

> Does the write target fall under the same *governed repo's jurisdiction* as
> the session's cwd?

They answer it with `governed_repo_for` in `~/.claude/hooks/_lib.sh`, which
**deliberately resolves a git worktree back to its main checkout**. That
resolver is right for the question, and it is what stopped the lane guard
being inert inside a worktree (closed 2026-09-27,
[[lane-guard-inert-in-worktrees]]).

But **"same jurisdiction" is strictly weaker than "same checkout."** Two
writes therefore ALLOW that this portfolio's own `CLAUDE.md` forbids.

## Gap 1 — a lane worktree may write to the MAIN checkout

`CLAUDE.md`: *"Never leave uncommitted work in the main checkout."*

A session in `~/code/canon-wt/<lane>` writing to
`~/code/calibrated-design-canon/<anything>` resolves **both** sides to
`calibrated-design-canon`. The guard sees an intra-repo write and allows it.

## Gap 2 — lane A may write into lane B's worktree

`CLAUDE.md`: *"never sweep another session's uncommitted work into your commit
… Committing it 'helpfully' destroys attribution and has destroyed content."*

`~/code/canon-wt/rule-10-canon` writing to `~/code/canon-wt/rule-11-canon/…`
also resolves both sides to `calibrated-design-canon`. Same jurisdiction, so:
allow. This is the exact failure `CLAUDE.md` records as having already
destroyed content, and the guard is structurally unable to see it.

## Verification command

```bash
bash ~/.claude/hooks/tests/test_jurisdiction.sh
# -> cases: 10 passed, 0 failed
```

Ten cases. The four gap cases assert **ALLOW on purpose** — the suite is a
tripwire on documented behaviour, so closing either gap fails the suite and
forces the docs to be updated rather than going stale. The other six are
controls proving the guard is not simply off: a cross-*jurisdiction* write
still denies from a lane cwd, from a main cwd, through both H9 and H19; a lane
writing to its own tree allows; and `CLAUDE_KICKOFF_CROSS_REPO=1` still
re-opens the denied case.

> The suite unsets `CLAUDE_KICKOFF_CROSS_REPO` per hook invocation. Its first
> run reported all three cross-repo controls as ALLOW because the authoring
> session legitimately held the grant. A suite that inherits the ambient
> environment measures the environment, not the guard.

## The design question, stated plainly

**Should the lane guard compare checkouts (`checkout_root_for` on both sides)
as well as jurisdictions (`governed_repo_for`)? And if it should, what
authorizes the integrator?**

That is why this was not patched in the pass that found it. A lane writing to
its own main checkout is *not always wrong*: it is precisely what the
**integrator** lane does when it lands work, and `docs/orchestrator-role.md`
hands the orchestrator the main checkout on purpose. A naive both-sides
`checkout_root_for` comparison would deny the integrator's normal, authorized
landing path — bricking the way work reaches `main`, which is a worse outcome
than the gap.

So the real choice is between:

1. **Enforce checkout identity, with an explicit integrator exemption.** Needs
   a decision on what carries the exemption. `CLAUDE_KICKOFF_CROSS_REPO=1` is
   the wrong lever — it grants cross-*repo* work, which is a different and
   broader thing than "this session holds the main checkout". A new,
   narrower grant (e.g. `CLAUDE_INTEGRATOR_LANE=1`) is one option; reading the
   claim out of `docs/lanes.md` is another, and would need no env var at all
   since the lane registry already names who holds what.
2. **Enforce checkout identity only for lane→lane, not lane→main.** Gap 2 has
   no legitimate counterpart at all — no role in `docs/lanes.md` is supposed
   to write into another session's worktree — so it can be denied outright
   with no exemption machinery. This closes the gap that `CLAUDE.md` says has
   already destroyed content, and leaves Gap 1 open and documented.
3. **Leave both open and rely on the documented convention.** Cheapest, and
   defensible while the portfolio is one operator; it stops being defensible
   as soon as two sessions run concurrently, which is the documented working
   model.

Option 2 is the cheapest thing that addresses the harm `CLAUDE.md` actually
records. It is a recommendation, not a decision.

## Already done (do not redo)

The gaps are documented, so no one has to rediscover them:

- `~/.claude/hooks/H19_KNOWN_LIMITATIONS.md` — section "THE JURISDICTION MODEL
  LEAVES TWO CLAUDE.md RULES UNENFORCED", naming both rules.
- `~/.claude/hooks/h09_lane_guard.sh` and `h19_lane_guard_shell.sh` — header
  comments, each naming the `CLAUDE.md` rule it leaves unenforced and pointing
  at this card.
- `~/.claude/hooks/tests/test_jurisdiction.sh` — the runnable proof above.

Related: [[lane-guard-inert-in-worktrees]] (the worktree scope fix whose
resolver created this consequence).

## Closed

Closed by Director ruling 2026-09-28: won't do; single-operator portfolio,
jurisdiction guard suffices.

**Verification:**

```bash
grep -A5 "^## Closed" docs/board/done/lane-guard-jurisdiction-not-checkout-identity.md
```

Commit: <FILL-IN-AFTER-COMMIT>
