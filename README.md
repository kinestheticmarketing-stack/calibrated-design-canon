# Calibrated Design Canon

> **Calibrated Vibe Coding (CVC)** is a documented method for
> building real software with AI assistance — without producing
> the "AI slop" that gives vibe coding its bad name. This is the
> public canon.

## What is this?

Most people working with AI coding assistants (Claude, Cursor,
Copilot, Lovable, etc.) produce one of two outcomes: either
they ship slop because they skip the discipline, or they avoid
AI entirely because they can't trust the output. There's a
third path — disciplined AI-assisted building, with verification
by default, multi-role separation of concerns, and an explicit
adversarial review layer.

That third path is Calibrated Vibe Coding.

This repo holds the public canon: the philosophical position
(MANIFESTO.md), the standard (CVC.md), and the method specs that
implement it (METHODS/). The method has been pressure-tested
across six production projects, including a lead-generation
funnel running in production at kinestheticmarketing.com.

CVC uses four roles:

- **Director** — the human. Owns the project, exercises taste,
  gates ship decisions.
- **Architect** — a chat AI. Drafts kickoffs, brainstorms,
  documents.
- **Executor** — a coding AI (typically Claude Code). Receives
  kickoffs, executes work, reports back.
- **Auditor** — a separate chat AI. Performs adversarial review
  of kickoffs before they fire and Final Reports after they
  return. Operates in isolation from the Architect's context.

The four-role architecture is what distinguishes CVC from casual
AI-paired development: a calibrated practitioner does not trust
their own design without an external check.

## Start here

- **New to the method?** Read [MANIFESTO.md](MANIFESTO.md),
  then [CVC.md](CVC.md).
- **Want to apply it?** Read
  [METHODS/the-calibrated-stack.md](METHODS/the-calibrated-stack.md)
  for the practitioner's method.
- **Want to add the Auditor role to your existing workflow?**
  Read [METHODS/AUDITOR_PROTOCOL.md](METHODS/AUDITOR_PROTOCOL.md)
  and
  [METHODS/AUDITOR_PRIMING_TEMPLATE.md](METHODS/AUDITOR_PRIMING_TEMPLATE.md).
- **Want to see the method in production?** Read the Phase 2.6
  retrospective at
  [RETROSPECTIVES/phase-2.6-kinesthetic.md](RETROSPECTIVES/phase-2.6-kinesthetic.md) —
  real numbers, real catches, real cost analysis.

## Canon contents

Standard and philosophy:
- [MANIFESTO.md](MANIFESTO.md) — the philosophical position
- [CVC.md](CVC.md) — the Calibrated Vibe Coding standard
- [NAMING.md](NAMING.md) — naming conventions for projects
  and methods

Method specs (METHODS/):
- [the-calibrated-stack.md](METHODS/the-calibrated-stack.md) —
  the practitioner's method
- [AUDITOR_PROTOCOL.md](METHODS/AUDITOR_PROTOCOL.md) — Auditor
  role specification
- [AUDITOR_PRIMING_TEMPLATE.md](METHODS/AUDITOR_PRIMING_TEMPLATE.md) —
  universal Layer 1 priming for the Auditor
- [ARCHITECT_DISCIPLINE.md](METHODS/ARCHITECT_DISCIPLINE.md) —
  Architect workflow-discipline rules

Retrospectives (RETROSPECTIVES/):
- [phase-2.6-kinesthetic.md](RETROSPECTIVES/phase-2.6-kinesthetic.md) —
  First full deployment of four-role Calibrated Stack on the
  Kinesthetic Marketing Funnel

## What this repo eventually powers

- calibrateddesign.com — philosophy / manifesto site
- calibrateddesignapp.com — franchise app overview
- calibratedvibecoding.com — CVC manifesto + registered methods

## Status

Private repo during initial drafting. Flips to public when websites launch.
