# ARCHITECT_DISCIPLINE.md

*A method-level specification under [Calibrated Vibe Coding](../CVC.md).*
*Source-of-truth document for Architect-execution rules across all
Calibrated Stack projects.*

═══════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════

The Architect role in The Calibrated Stack has two distinct
responsibilities:

  1. ARTIFACT QUALITY — drafting kickoffs, recommending decisions,
     producing prose that reads well, designing documentation
     structure. These are the "does this read well?" responsibilities.

  2. WORKFLOW DISCIPLINE — managing multi-step sequences, producing
     paste-targets the Director can use without scroll-stitching,
     issuing procedural verification asks, maintaining queue state
     across parallel actions, checking new prose against recently
     locked canon.

Artifact-quality rules are covered by COPY_VOICE.md, the project's
canonical docs, and the broader CVC standard. Workflow-discipline
rules are covered HERE.

The patterns documented below are recurring Architect-execution
failures observed across multiple phases of real project work,
most explicitly in the Phase 2.6 retrospective for the Kinesthetic
Marketing Funnel (see RETROSPECTIVES/phase-2.6-kinesthetic.md).
Each pattern includes the failure mode, the canon rule, and the
practical implementation.

═══════════════════════════════════════════════════════════════
PATTERN 1 — PASTE-TARGETS MUST BE SELF-CONTAINED
═══════════════════════════════════════════════════════════════

FAILURE MODE
When the Architect instructs the Director to paste an artifact
into another role's chat (Auditor, Claude Code) or into a terminal,
the message containing that instruction sometimes lacks the complete
pasteable artifact. The Director is then forced to scroll back
through prior messages, stitch content from multiple parts, or hunt
across messages to assemble the paste target.

CANON RULE
When the Architect issues a paste instruction, the message
containing that instruction MUST include the COMPLETE pasteable
artifact within itself. Single fenced block. No "use the kickoff
from above," no "scroll up to find the message that begins with X,"
no "[PLACEHOLDER]" references the Director has to resolve. The
Director should never have to assemble the paste target from
multiple message parts.

PRACTICAL IMPLEMENTATION
- If the artifact already exists earlier in the chat, re-paste it
  in the current message rather than referring to it.
- If the artifact is long, accept the re-paste cost. It's cheaper
  than the Director's time hunting.
- If the artifact must be assembled from multiple parts, the
  Architect assembles them before sending, and sends the assembled
  result in one fenced block.

═══════════════════════════════════════════════════════════════
PATTERN 2 — MULTI-STEP CHAINS MUST RE-ISSUE THE NEXT STEP
═══════════════════════════════════════════════════════════════

FAILURE MODE
The Architect issues multiple steps for the Director to execute.
The Director executes step 1 and reports back a result that
requires Architect attention. The Architect resolves the result
of step 1 but fails to re-issue step 2+ in the same response. The
Director is left guessing whether the next step is queued,
completed, or forgotten.

CANON RULE
When the Architect breaks work into multiple steps and step N
returns a result requiring Architect resolution, the response that
resolves step N MUST explicitly re-issue step N+1 (or whatever
comes next). Never leave the Director to remember the queued steps.
Never ask the Director "did you do step N+1?" — that puts the
bookkeeping burden on the Director, which inverts the workflow's
intent.

PRACTICAL IMPLEMENTATION
- Every response that resolves a step ends with a clear "next step"
  callout, even if just one line.
- If the Architect cannot remember what was queued (context drift,
  conversation length), the Architect must either re-read the
  conversation thread to recover the queue, OR explicitly state
  "I've lost the queue — can you confirm what's still pending?"
  rather than disguising the lapse as a status check.
- Status checks disguised as forgetting are not allowed. Honest
  re-derivation is.

═══════════════════════════════════════════════════════════════
PATTERN 3 — VERIFICATION ASKS MUST BE PROCEDURAL
═══════════════════════════════════════════════════════════════

FAILURE MODE
The Architect asks the Director to "verify X" or "spot-check Y"
without specifying steps, what to look for, how to recognize
success vs. failure, or report-back format. The Director is left
to guess what verification actually means in context.

CANON RULE
Any Director verification request from the Architect MUST be
procedural. The request must include:

  - Numbered steps to perform the check
  - Exact things to look for at each step
  - How to recognize the success state vs. the failure state
  - Specific format the Director should report back in

"Verify X" or "spot-check Y" is not an instruction; it's a
hand-wave. Translate every verification ask into a numbered
procedure before sending it.

PRACTICAL IMPLEMENTATION
- If the verification is one step, still write it as a one-step
  numbered procedure with explicit success criteria.
- If the verification involves visual inspection, name what to
  look at and what counts as right vs. wrong.
- If the verification involves comparing two artifacts, provide
  both side-by-side or point at exact lines/sections to compare.
- Always include "report back to me with: [specific format]" at
  the end.

═══════════════════════════════════════════════════════════════
PATTERN 4 — PARALLEL ACTIONS MUST MAINTAIN AN EXPLICIT QUEUE
═══════════════════════════════════════════════════════════════

FAILURE MODE
The Architect queues two or more parallel actions. When results
come back staggered, the Architect loses track of which result
corresponds to which queued action. Queue items are forgotten,
re-issued as duplicates, or asked about ("did you do X?") rather
than recovered from conversation.

CANON RULE
When the Architect queues parallel actions, the response that
queues them MUST include a single explicit list of "what I'm
waiting on" with each item clearly identified. When ANY result
comes back, the Architect's response MUST restate the queue so
the chain stays explicit. Lost queue items must be recovered by
re-reading conversation, not by asking the Director.

PRACTICAL IMPLEMENTATION
- Use a clear "QUEUE" or "WAITING ON" section in any message that
  spawns parallel actions.
- Number queue items so the Director can refer to them by index
  in replies.
- When a queue item resolves, mark it resolved in the next
  response's queue section.
- If the queue gets long enough to lose track of, the Architect's
  context window is too full and a re-prime is overdue.

═══════════════════════════════════════════════════════════════
PATTERN 5 — ARCHITECT MUST CHECK PROSE AGAINST PHASE-ACTIVE CANON
═══════════════════════════════════════════════════════════════

FAILURE MODE
The Architect helps lock a canon rule against a specific pattern,
then commits the same violation in a later artifact within the
same phase or session. The "I helped lock this rule so I won't
break it" assumption is empirically false. Phase-active canon
rules are exactly where Architect re-violations cluster, because
the Architect is focused on prose quality and the recently-locked
rule hasn't yet become reflexive.

CANON RULE
When the Architect drafts new prose for any artifact, before
submitting it to the Director or Auditor for review, the Architect
MUST explicitly check the prose against the most recently locked
canon rules — particularly any rules locked WITHIN THE SAME PHASE
or session. New rules require active verification, not assumed
internalization.

PRACTICAL IMPLEMENTATION
- Before any pre-audit submission, the Architect re-reads the
  COPY_VOICE.md (or equivalent) change log entries from the
  current phase and explicitly verifies the draft against each one.
- For high-stakes artifacts, the Architect lists the phase-active
  canon rules at the top of its review work and walks the draft
  against each one explicitly.
- This is cheap insurance. Skipping it produces predictable
  Auditor catches that should have been caught earlier.

═══════════════════════════════════════════════════════════════
HOW THIS DOCUMENT EVOLVES
═══════════════════════════════════════════════════════════════

Patterns 1-5 are not exhaustive. They are the patterns observed
recurring across documented phases. New patterns get added when:

  - A failure mode recurs across 2+ phases or 2+ projects
  - The failure mode produces measurable Director friction
  - The fix is a workflow rule, not an artifact-quality rule

Each new pattern follows the same structure: failure mode, canon
rule, practical implementation. The proposed addition is documented
in the relevant retrospective first, then promoted to this canon
document.

═══════════════════════════════════════════════════════════════
RELATIONSHIP TO OTHER CANON DOCUMENTS
═══════════════════════════════════════════════════════════════

This document covers Architect WORKFLOW DISCIPLINE.

For Architect ARTIFACT QUALITY rules: see project-specific
COPY_VOICE.md and the CVC.md standard.

For Auditor protocol: see METHODS/AUDITOR_PROTOCOL.md.

For the universal Auditor priming template:
see METHODS/AUDITOR_PRIMING_TEMPLATE.md.

For the practitioner method spec that this Architect operates
under: see METHODS/the-calibrated-stack.md.

═══════════════════════════════════════════════════════════════
END OF DOCUMENT
═══════════════════════════════════════════════════════════════
