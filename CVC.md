# Calibrated Vibe Coding

> AI-paired throughout, human-directed, never shipped without review.

Calibrated Vibe Coding (CVC) is a discipline. AI and human pair
through every phase — research, architecture, execution, and
verification. The human directs the work, exercises taste, and holds
the final ship decision. The AI surfaces options, writes the
keystrokes, runs the checks. The vibe is the speed of pairing.
The calibration is the judgment, the testing, and the documentation
that make the speed safe.

## The six principles

1. **AI surfaces, human chooses.** Architecture and approach come from
   established practice. AI researches options and tradeoffs; the
   human weighs them in context and selects. Neither makes the call
   alone.

2. **Brainstorm before execution.** Talk first. Settle the call. Then
   one clean execution. The vibe loses its safety when execution
   starts before judgment lands.

3. **Verification is shared.** Code is tested in pairing — AI runs
   automated checks and reports findings, human runs the eye-check
   that catches what automation misses. Neither owns verification
   alone.

4. **Nothing ships unreviewed.** The final ship decision is human,
   always. Reviewed, intentional, with eyes on the output. No
   exceptions, no urgency override, no auto-deploy without a human
   gate.

5. **Decisions live in writing.** Architectural choices are documented
   when made, not reconstructed later. The audit trail is what lets
   future-you trust past-you's calibration.

6. **Design is verified against itself.** A calibrated practitioner
   does not trust their own design without an external adversarial
   review. The Auditor role exists to break the Architect's
   self-blindness. See METHODS/AUDITOR_PROTOCOL.md.

## Methods

CVC defines a discipline, not a single workflow. Within the standard,
practitioners develop their own methods — specific workflows, tool
choices, and cadences that implement the principles for their context.

Methods are named, documented separately, and share the principles
above; they differ in execution.

### Registered methods

- [The Calibrated Stack](./METHODS/the-calibrated-stack.md) —
  Kinesthetic Marketing's implementation. Chat-architect + Claude Code
  executor pairing, brainstorm-first cadence, subagent review passes,
  running docs, git-pull deploys.

More methods will be documented as practitioners share their work.

## Why this exists

"Vibe coding" as a term was coined by Andrej Karpathy in early 2025
for AI-paired development that prioritizes flow over rigor.
Industry discourse has since split between casual vibe coding —
associated with insecure, unmaintained AI output — and disciplined
AI-assisted engineering. No memorable term has emerged for the
disciplined version.

Calibrated Vibe Coding fills that gap. The vibe stays. The discipline
is what gets calibrated.
