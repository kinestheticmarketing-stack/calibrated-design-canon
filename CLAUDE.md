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
