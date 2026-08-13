# The Calibrated Stack

*A registered method under [Calibrated Vibe Coding](../CVC.md).*

The Calibrated Stack is the Kinesthetic Marketing implementation of
CVC. Specific workflow, tools, and cadences that implement the five
CVC principles for solo development on web and mobile products.

## Architecture

A human director, plus three AI roles:

- **Director (human):** Holds context across sessions, exercises
  taste, gates ship decisions, verifies output, owns the project,
  adjudicates disagreements between Architect and Auditor.
- **Architect (chat AI):** Brainstorms, researches, drafts kickoffs,
  makes architectural recommendations, writes documentation. Does
  not execute code.
- **Executor (Claude Code):** Receives kickoffs, executes the work,
  runs tests, reports back. Does not make architectural decisions
  unilaterally.
- **Auditor (chat AI):** Performs adversarial review of kickoffs
  before they fire and Final Reports after they return. Operates
  in isolation from the Architect's context. Does not modify
  artifacts. The Auditor is the external reference point that
  verifies the Architect's calibration. Invoked selectively — see
  METHODS/AUDITOR_PROTOCOL.md for invocation criteria.

The architect and executor are intentionally separated. Mixing them
causes the executor to drift into architecture decisions and the
architect to drift into premature execution.

The four-role architecture is what distinguishes Calibrated Vibe
Coding from casual AI-paired development: a calibrated practitioner
does not trust their own design without an external check.

## Workflow rules

These are tooling-level practices that implement the CVC principles
for this method.

### Cadence

- Brainstorm before execution (CVC principle 2). Multiple turns of
  back-and-forth in chat before any kickoff is fired at Claude Code.
- Single fenced block per task or kickoff. One copy, one paste.
- Bold terminal label before every command (Mac terminal:, VPS
  terminal:, Claude Code:) — even when same as previous.

### Editing

- Full file replacement, never line-by-line edits.
- For files >50 lines, sed surgical commands; for smaller, full block.
- Mistakes corrected fully on first response, not iteratively.
- **RENDER-FORCED GRAMMAR REPAIRS ARE DISCLOSED EXECUTOR SCOPE.** When
  a Director-approved string cannot be applied literally because the
  renderer transforms it — a template appending its own punctuation,
  an article that must agree with a substituted noun — the Executor
  repairs the input to produce the approved output and discloses the
  repair with before and after. Approval attaches to what ships, not
  to the literal input. Anything touching meaning halts instead.
  Evidence: 2026-08-12, a banked citation stat whose renderer appends
  its own period would have shipped a visible double period to two
  live pages; and "a certified lab" → "an accredited lab" required the
  article to change.

### Verification

- Final Report sections in every kickoff, lettered (a, b, c) for
  consistency.
- MD5 hashes on binary outputs to catch silent failures.
- Smoke tests after every deploy.
- Human eye-check on visual output.
- **REGEN EXIT 0 IS A COMMIT PRECONDITION.** No commit may create a
  state where the project's regeneration script fails. Evidence: on
  2026-08-12 a DCI commit added two URLs to `SERVICE_PAGES`; the
  homepage generator hard-fails when a `SERVICE_PAGES` URL has no
  matching tile, so `regen_all.sh` exited 1 on a committed state and
  no generator pass succeeded until a follow-up wave. The invariant
  is committed = regenerable. The check is free — the wave already
  runs regen; the sequencing just moves ahead of the commit boundary.

### Documentation

- Running docs updated end of each session: STATE_OF_PROJECT,
  DECISIONS, CHANGELOG.
- DECISIONS.md is append-only. Never rewrite history.
- Each kickoff is self-contained — Claude Code has no memory across
  sessions.

### Subagents (Claude Code)

Auto-invoke when relevant:
- `/superpowers` — brainstorm-first / cheaper compute exploration
- `/front-end-design` — UI work
- `/simplify-code` — periodic cleanup passes

### Source control

- GitHub-first: repo created before first commit.
- Private repos default; public when ready.
- Deploy via git pull on VPS, not scp.

## What this method optimizes for

- Solo development with AI as multiplier
- Long-term maintainability of products built fast
- Audit trail strong enough that future-self trusts past-self
- Multi-session, multi-project consistency

## What this method does NOT optimize for

- Team collaboration (single director assumed)
- High-frequency CI/CD deploys (manual gate is the default)
- Throwaway prototypes (overkill for sub-day experiments)
