# Card conventions (board hygiene)

## The shape

- One card = one FILE: `docs/board/<column>/<id>.md`. Column membership IS the directory, so a move is a file move and there is no status field to desync.
- The filename stem is the card's durable id and equals `id:` in the frontmatter. Editing a card never renames it; a rename is a deliberate, rare act.
- The one-line rule retires for BODIES and survives for TITLES: `# <title>` alone must say what the card is, because a column listing shows nothing else. Bodies run as long as the card genuinely needs; append updates at the bottom with dates.
- Real specs still live in `docs/*.md`. Point at them with `doc:`, do not paste them into the card.

## Frontmatter

```yaml
id: example-card-id          # equals the filename stem
owner: director               # director | architect | executor | auditor -- see "Owner set" below
type: bug                    # OPTIONAL: bug | feature | decision | idea | chore | watch
created: 2026-01-01
retriage: 2026-01-08          # REQUIRED -- re-triage date, no exceptions (Rule 10c):
                               # 7d out for a live defect, 14d for a Director-decision
                               # ruling, 30d for everything else (chores, later/,
                               # deferred-pending-data, architecture questions). An
                               # expired date is a halt-level finding (Rule 10d), not
                               # a note.
size: S                      # OPTIONAL: XS | S | M | L
lane: area/subarea           # OPTIONAL
priority: 20                 # sparse int, lower sorts higher; Ready only
tags: [parallel-safe, verify-prod, time-gated, discussion]
after: [some-other-card-id]  # OPTIONAL dependency ids
doc: docs/some-spec-2026-01-01.md
```

- `retriage` is the only frontmatter field that is never optional. A card
  with no re-triage date never expires and never gets reviewed -- see
  METHODS/ARCHITECT_DISCIPLINE.md Rule 10c-10d.
- `type` is optional and is OMITTED when unclear. A guessed type is worse than no type.
- Only the keys above are known; anything else is a note wearing a costume, so put it in the body. If the project has installed the board-doctor test (`src/__tests__/board-registry.test.ts` or equivalent), it enforces this, plus unique ids, a title line, and the owner/type enums.

### Owner set (adapted for this portfolio)

- **`director`** — the human. Rules on policy, ratifies decisions, holds the
  one authorization boundary for destructive/external ops.
- **`architect`** — drafts kickoffs, designs unit ledgers, decomposes waves.
- **`executor`** — Claude Code, the session that splices, verifies, commits.
- **`auditor`** — a separate adversarial chat that reviews the executor's
  work. Not the same session as the executor, by design — an auditor card
  reviewed by the session that produced the work is not an audit.

A card's `owner:` is who acts next, not who cares about it. A `type: decision`
card owned by `director` is correctly placed even while an `architect` or
`executor` did all the drafting work — the deliverable left to produce is the
ruling, not more analysis.

## Working rules

- Waiting-on-owner cards must name the EXACT unblocking action or word. A column move is never authorization for destructive or external-facing operations.
- Intake captures move to Ready only when defined enough for a cold start; otherwise add a "needs: ..." note and move to Waiting on owner.
- `type: decision` = the deliverable is a decision, not code. A session may prepare the proposal; the owner makes the call. Column placement signals urgency, the type signals the deliverable.
- Ready is the only column where ORDER is signal: `priority` carries the groom sequence, sparse (10, 20, 30) so one card can be re-slotted without renumbering the column.
- Done keeps roughly the last 10 cards; the rest rotate to `docs/board/archive/<YYYY-MM>/`.
- Stale-card sweep: whenever a card lands in Done, scan Ready/Later for cards the work just superseded and close them with a "CLOSED as stale" note.
- Another agent's cards are read-only. With one file per card that is a path-level fact (`owner:` plus the file's own git history), not a habit.

## PROJECT RULE — a Done card is not done without a verification command

**Every card moved to `done/` must carry two things in its body: the commit
hash that shipped it, and the exact command — a `grep`, a SQL query, a
`curl`, whatever actually proves it — that a cold session can re-run to
confirm the fix still holds.** No exceptions, no "obviously fixed" shortcut.

**Why this rule exists, with dates, not as a hypothetical:**

- **2026-08-17.** RECEIPTS.md recorded "six validators installed in
  `_postbuild_check.py`." The real number was five. The figure came from a
  kickoff and was transcribed into canon without anyone running
  `grep -c "^def check_" _postbuild_check.py` — the one command that would
  have caught it in one second. It stood as a canon fact for a full day.
- **2026-08-17 → 2026-08-19.** A DCI STATE_OF_PROJECT.md entry carried
  "8 service pages" for days while the live count was 18 — the file was
  never re-verified against `SERVICE_PAGES` after several sessions had
  expanded it.
- **2026-08-17.** Longmont's `STATE_OF_PROJECT.md` and
  `DEPLOYMENT_RUNBOOK.md` both asserted a reconciliation and a deploy block
  were closed, when a later audit found neither had ever existed to close —
  the "closed" claim was written from memory of what should have happened,
  not from a check of what had.
- **2026-08-19.** This same board-seeding pass found a defect
  (`_generate_calculator_pages.py`'s `*1.25` bonus-cap bug) that a prior
  wave's own carryforward note had named at **two** line numbers. The wave
  fixed one and reported the item closed. The second instance shipped live,
  unfixed, for two days, because nothing re-checked the claim against the
  second line number before marking it done.

Every one of these is the same failure: **state remembered rather than
read.** A verification command turns "I believe this is fixed" into
something the next session — or the next agent, or a Director skimming
`done/` — can re-run in five seconds instead of re-trusting. A Done card
with no command is a claim wearing the shape of a closure.

## Reading the board

Surgically, never whole:

```bash
cat docs/board/ground-truth.md docs/board/in-flight/*.md   # what a cold session needs
ls docs/board/ready | wc -l                                # column size
grep -rl <topic> docs/board/ready/                          # find your area
npm run board:index                                         # one-file snapshot, on demand, never committed
```
