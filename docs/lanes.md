# Session lanes

**PARALLEL SESSIONS.** This file is the live registry and the lock: claim a lane when you start (commit the claim), release it when done. One session = one lane worktree (/Users/vongimbel/code/canon-wt/<lane>, branch `lane/<lane>`); two sessions never share a checkout. Files outside your lane's owns-list are read-only; route them through a board card.

Claims were skipped once on the origin project and sessions collided; do not skip them.

**Merge hazard:** if this file is ever set to `merge=union` in .gitattributes, a cross-lane rebase can silently DUPLICATE rows with no conflict markers. Check row counts after every rebase.

## Roles in this portfolio

`owner:` on a board card, and the role a lane claim is made under, is one of:

| Role | Who | Does |
|---|---|---|
| `director` | the human | Rules on policy, ratifies decisions, holds the one authorization boundary for destructive or external-facing operations |
| `architect` | planning session | Drafts kickoffs, designs unit ledgers, decomposes waves. **Historically a chat session with no filesystem access — which is why `/orchestrate` exists and why an Architect that cannot read the board must be handed it before drafting** |
| `executor` | Claude Code | Splices, verifies, commits, deploys. Claims lanes |
| `auditor` | a separate adversarial session | Reviews the executor's work. **Not the same session that produced it** — an audit by the author is not an audit |

The orchestrator is not a fifth role: it is an `executor` session that has been
ASSIGNED coordination duty via `/orchestrate`, holds the main checkout, and does
no feature work while it holds it.

## Current lanes

| Lane | Worktree | Owns | Status |
|---|---|---|---|
| push-canon | main checkout | push `feat/seo-geo-scaffold` to origin only, no local edits | released — pushed prior pass |
| merge-canon-main | main checkout | merge `feat/seo-geo-scaffold` into `main`, push, verify /main/ URLs | released — merged d4eb6d3, pushed, verified |
| staleness-watcher | main checkout | build citation staleness watcher (scripts/), no site-repo page edits | claimed |
