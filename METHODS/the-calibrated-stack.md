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

### Verification

- Final Report sections in every kickoff, lettered (a, b, c) for
  consistency.
- MD5 hashes on binary outputs to catch silent failures.
- Smoke tests after every deploy.
- Human eye-check on visual output.

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
