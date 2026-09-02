# calibrated-design-canon

## Project board

- `docs/board/` is THE board and single source of truth for all work: one
  markdown file per card, column membership = directory. Read
  `docs/board/ground-truth.md` in full every session (settled decisions; if
  your context disagrees with it, your context is stale), then
  `docs/board/in-flight/*.md` in full. Read the other columns surgically:
  `ls docs/board/ready | wc -l`, `grep -rl <topic> docs/board/ready/` — not
  whole; `node scripts/kanban-board.mjs --index` renders a one-file snapshot
  on demand if you ever want the whole thing in one read. `docs/backlog.md`
  is a short pointer, not the board. (This repo has no `package.json`, so
  the board runs via direct `node` invocation, not `npm run`.)
- Open the board from the Claude preview panel (the `board` server) or run
  `node scripts/kanban-board.mjs` for a browser tab. It grabs the next free
  port automatically (preferred 4400), so check the preview list / console
  for the actual URL.
- Work from Ready cards; capture new ideas as new files in
  `docs/board/intake/`; write dated outcome notes in the card body when you
  move something to Done.
- Card conventions live in `docs/board/conventions.md`. One card = one
  file; the one-line rule is for the TITLE, bodies can run long, real specs
  live in `docs/*.md` behind the card's `doc:` field. **A Done card must
  carry a verification command — the grep, query, or curl that proves it's
  actually closed — plus the commit hash. See conventions.md's Project Rule
  for why.**
- "Waiting on owner" cards name exactly one unblocking action. A column
  move is never authorization for destructive or external-facing
  operations.
- Capture freely (fragments are fine); run `/groom-board` to consolidate,
  right-size, and sequence the board. Do not edit cards in the board UI.
  A card is a debt, not a destination (METHODS/ARCHITECT_DISCIPLINE.md
  Rule 10): fix what a pass can fix in the same pass, carry a re-triage
  date on everything else, and report the repo's open card count before
  and after any pass that touches it.


## Working model

Parallel sessions are supported. **One session = one lane worktree**; two
sessions never share a checkout. Claim before you code: register in
`docs/lanes.md` and move your card to `docs/board/in-flight/`, and commit that
claim before touching code. Land from the lane on green gates.

**Never leave uncommitted work in the main checkout, and never sweep another
session's uncommitted work into your commit.** If you find foreign changes,
identify them, leave them, and ask that session to commit its own. Committing
it "helpfully" destroys attribution and has destroyed content.

This repo is docs-only: there is **no build gate and no test gate**. Stated plainly rather than inventing one. What replaces it: every factual claim added to canon must carry the command that verifies it (the board's Project Rule), and a figure asserted in a kickoff is not a verified figure.

**The ORCHESTRATOR role is ASSIGNED, NEVER INFERRED. Default is NO.** You are
orchestrating only if (a) the owner told you to in your own conversation, (b) a
departing orchestrator handed you the role explicitly, or (c) the owner asked
you to take the integrator lane. If none of those happened, you are a builder
or an ordinary session: do not hold the main checkout, do not dispatch other
sessions, do not review another lane's work uninvited. Two sessions both
believing they orchestrate is a collision, not redundancy. Role details in
`docs/orchestrator-role.md`; roles for this portfolio (director / architect /
executor / auditor) in `docs/lanes.md`.

**This portfolio runs WITHOUT cmux.** Pane observation and control are inert;
role claims use `--mode headless` and preflight uses `--allow-no-cmux`.
Coordination runs on committed dispatch briefs, `docs/lanes.md` as the lock,
and messaging. Because there is no eye, a builder must explicitly report its
worktree, branch, gate exit codes, and an explicit "done" — `ListAgents` shows
`idle` for both "finished" and "still thinking".

**The orchestrator reads `docs/board/` before it proposes anything.** That is
the whole reason `/orchestrate` exists here: on 2026-08-19 the board was
installed and the planning session, having no filesystem access, still answered
"where were we" from conversation memory instead of from the cards.
