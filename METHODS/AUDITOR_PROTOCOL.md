# AUDITOR_PROTOCOL.md

*A method-level specification under [Calibrated Vibe Coding](../CVC.md).*
*Source-of-truth document for the Auditor role across all Calibrated
Stack projects.*

═══════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════

The Auditor is the fourth role in The Calibrated Stack — Director,
Architect, Executor, Auditor. The Auditor exists to break the 
Architect's self-blindness. An author cannot fully audit their own 
output. The Auditor is the external reference point that verifies 
calibration.

This document defines what the Auditor role is, when to invoke it, 
how to prime it, how to use its output, and how the Director 
adjudicates Auditor-vs-Architect disagreements.

═══════════════════════════════════════════════════════════════
WHAT THE AUDITOR IS
═══════════════════════════════════════════════════════════════

A dedicated Claude.ai chat session, separate from the project's 
Architect chat, primed to perform adversarial review of:

  - Kickoffs before they fire at Claude Code (Executor)
  - Final Reports after the Executor returns
  - Adversarial user simulations (optional, on Director request)

The Auditor has its own context window, isolated from the Architect's
chat history. It sees only what the Director pastes to it. This 
isolation is the point — the Auditor's value depends on seeing 
artifacts cold, without the optimism the Architect accumulated while 
designing them.

═══════════════════════════════════════════════════════════════
WHAT THE AUDITOR IS NOT
═══════════════════════════════════════════════════════════════

- NOT a second Architect. Does not draft kickoffs.
- NOT a brainstorming partner. Does not suggest features.
- NOT a code editor. Does not modify artifacts.
- NOT a final authority. The Director decides.
- NOT a permanent reviewer of every action. Invoked selectively.

═══════════════════════════════════════════════════════════════
WHEN TO INVOKE THE AUDITOR
═══════════════════════════════════════════════════════════════

INVOKE for:
  - Public-facing pages or copy going live
  - Backend infrastructure changes
  - Irreversible actions (DB migrations, deploys, payment flows)
  - Email or message sequences firing at real recipients
  - Schema work or anything touching SEO/GEO infrastructure
  - High-stakes refactors where silent failure costs money or trust
  - Phase-boundary closeouts and any work bundled into them
  - Pre-deploy Final Reports

SKIP for:
  - CSS tweaks and visual nudges
  - Copy edits within an already-audited surface
  - Internal documentation updates
  - Generator dry-runs and local-only experiments
  - Anything reversible in under two minutes

The Auditor adds real production tax — a second chat session, priming 
time, audit round-trips. Use it where the cost is justified by the 
stakes. Calibration is the goal, not coverage.

═══════════════════════════════════════════════════════════════
PER-PROJECT INSTANTIATION
═══════════════════════════════════════════════════════════════

One Auditor chat per project. Not shared across projects.

Same context-purity logic as Architect chats. The Auditor must hold 
the specific project's canonical docs tightly to catch subtle 
project-specific violations. Cross-project context bleed dilutes the 
audit quality.

Priming structure is two-layer:

  Layer 1 (universal):  METHODS/AUDITOR_PRIMING_TEMPLATE.md in the
                        canon repo. Role definition, output format, 
                        engagement rules, universal audit dimensions.
  
  Layer 2 (project):    AUDITOR_PRIMING.md in each project repo. 
                        Project identity, canonical doc placeholders,
                        project-specific audit dimensions.

At prime time, paste Layer 1 first, then Layer 2, then the project's
canonical docs as specified by Layer 2's placeholders. The Auditor
stitches them into one operating frame at session start.

A project without a custom Layer 2 file can still run a generic 
Auditor with Layer 1 + canonical docs alone — useful for low-stakes
projects that don't need bespoke dimensions yet.

When project canon changes materially, re-prime with the updated 
docs. When the universal template changes, re-prime affected 
projects to pick up the new shared rules. When a project's specific
priming needs structural change, edit Layer 2 in repo first.

═══════════════════════════════════════════════════════════════
AUDIT OUTPUT FORMAT
═══════════════════════════════════════════════════════════════

Every audit returns this format. Predictable, parseable, fast for the 
Director to act on.

AUDIT: [Artifact identifier]

VERDICT: [PASS / PASS-WITH-FLAGS / FAIL]

CRITICAL ISSUES (must fix before firing or deploying):
  1. [specific issue, with section reference]
  (none — if none)

FLAGS (worth considering, not blocking):
  1. [...]
  (none — if none)

MISSING VERIFICATION:
  1. [what isn't being checked that should be]
  (none — if none)

SILENT FAILURE MODES:
  1. [what could go wrong without producing an error]
  (none — if none)

VOICE NOTES (only if voice work was in scope):
  1. [drift, banned phrase, locked-string violation, register slip]
  (none — if none)

DIMENSIONS NOT APPLICABLE:
  - [list]

VERDICT MEANINGS:
  PASS              = Fire it / deploy it.
  PASS-WITH-FLAGS   = Fire it, but read flags first. Director's call.
  FAIL              = Do not fire. Revise the artifact first.

═══════════════════════════════════════════════════════════════
HOW THE DIRECTOR USES AUDITS
═══════════════════════════════════════════════════════════════

FAIL verdict:
  - Return artifact to Architect with the audit attached.
  - Architect revises addressing critical issues.
  - Re-submit to Auditor for a second audit pass.
  - Loop until PASS or PASS-WITH-FLAGS.

PASS-WITH-FLAGS verdict:
  - Director reads the flags.
  - For each flag: judge whether to revise or ship as-is.
  - If revising: small Architect turn, no re-audit needed unless 
    revisions are non-trivial.
  - If shipping: fire and move on, log flags in STATE_OF_PROJECT.md 
    if they represent technical debt.

PASS verdict:
  - Fire the kickoff or deploy the Final Report's work.

═══════════════════════════════════════════════════════════════
ADJUDICATING AUDITOR-VS-ARCHITECT DISAGREEMENTS
═══════════════════════════════════════════════════════════════

The Auditor and Architect WILL disagree. This is a feature, not a 
bug — the two roles are designed to produce different perspectives.

The Director is the tiebreaker. Three principles:

(1) Look at the specific claim, not the source.
    The Auditor is not always right. The Architect is not always 
    wrong. Each disagreement is evaluated on its merits.

(2) Default to the more conservative path when stakes are high.
    For irreversible actions (deploys, payment flows, mass emails),
    if the Auditor flags something and the Architect dismisses it,
    investigate before firing.

(3) Default to the Architect's call when stakes are low.
    For reversible work, if the Auditor's concern represents a small 
    fraction of users or a non-critical edge case, the Architect's 
    "ship it" is usually right.

The Director's calibration — knowing when to side with which role — 
is the discipline. Both AI roles produce inputs. The Director 
produces the decision.

═══════════════════════════════════════════════════════════════
CONTEXT BUDGET CONSIDERATIONS
═══════════════════════════════════════════════════════════════

The Auditor priming + canonical docs consumes significant context at 
session start. Expect to re-prime an Auditor chat every 1-2 weeks of 
active use, or whenever you notice it drifting from the canon.

When re-priming, paste the latest canonical doc versions. The Auditor 
cannot know what changed in canon since its last priming — the 
Director ensures freshness.

A fresh Auditor chat with stale canon will catch artifacts against 
the wrong rules. A stale Auditor chat with fresh canon will miss 
new violations because it doesn't know the new rules exist. Both 
fail modes are recoverable but cost time. Re-priming is cheap. Use it.

═══════════════════════════════════════════════════════════════
END OF PROTOCOL
═══════════════════════════════════════════════════════════════
