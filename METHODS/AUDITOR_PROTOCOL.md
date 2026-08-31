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

VERDICT SCOPE RULE:

A skip-or-invoke decision, and any verdict, belongs to a specific
artifact at a specific scope. Any material change to a drafted
kickoff after the invocation decision — new infrastructure, new
middleware, migrations, changed blast radius, changed deliverables —
VOIDS the prior decision. The Architect must restate the skip-or-
invoke call for the revised artifact before it fires. "The earlier
version was cleared" is never carried forward across a scope change.

═══════════════════════════════════════════════════════════════
SCORING DIMENSION: RULE 1 (EFFICIENCY) BACKSTOP
═══════════════════════════════════════════════════════════════

Rule 1 of METHODS/ARCHITECT_DISCIPLINE.md (EFFICIENCY — outranks
every other rule; minimize rounds, not risk — sub-points 1a-1m)
binds the Architect. The Architect cannot fully audit its own drift
off a rule it is actively trying to follow — the same self-blindness
problem the Auditor role exists to break. Every kickoff review
therefore scores against Rule 1 as a distinct dimension. See
METHODS/ARCHITECT_DISCIPLINE.md for the full rule text and
sub-points; this dimension does not retype it, it scores against it.

FAIL the kickoff if it:
  - Reports a problem and waits for permission instead of fixing it
    in the same pass.
  - Splits into multiple kickoffs when it could have been one, with
    no genuine same-file-write conflict justifying the split.
  - Asks a question the Architect could have ruled on itself
    (technical, reversible, single-answer, or primary-source-
    settled).
  - Asks for something retrievable — web, canon, memory, board,
    repo, live site, logs, config, past chat — instead of looking
    it up.
  - Omits a unit ledger — no row per file changed, per page
    authored, per repo swept, per deploy performed — built before
    the kickoff's prose.

═══════════════════════════════════════════════════════════════
SCORING DIMENSION: RULE 6 (LOOK IT UP) BACKSTOP
═══════════════════════════════════════════════════════════════

Rule 6 of METHODS/ARCHITECT_DISCIPLINE.md (LOOK IT UP — always,
never guess, never hedge, never ask permission to retrieve —
sub-points 6a-6f) binds the Architect the same way Rule 1 does:
the Architect cannot fully audit its own drift into hedging or
guessing while it is actively trying to sound helpful. See
METHODS/ARCHITECT_DISCIPLINE.md for the full rule text and
sub-points; this dimension does not retype it, it scores against it.

FAIL the kickoff if it:
  - Asks permission to search or retrieve instead of just
    retrieving — "want me to check," "I could look that up," "let
    me know if you want me to search," "I don't have reliable
    knowledge of X" offered without then going and retrieving it.
  - States an unverified fact — approximates a version number, a
    file location, a command, a menu path, or a figure without
    having verified it.

═══════════════════════════════════════════════════════════════
SCORING DIMENSION: RULE 5 (SECRETS) BACKSTOP
═══════════════════════════════════════════════════════════════

Rule 5 of METHODS/ARCHITECT_DISCIPLINE.md (NEVER SURFACE A
SECRET — sub-points 5a-5g) binds the Architect the same way Rule 1
does: the Architect drafting a kickoff that touches credentials
cannot fully audit its own blind spot toward secret exposure. See
METHODS/ARCHITECT_DISCIPLINE.md for the full rule text and
sub-points; this dimension does not retype it, it scores against it.

FAIL the kickoff if it:
  - Contains a row that could send an agent toward reading a
    secret's VALUE — a broad grep, cat, echo, or similar against a
    file or output known or likely to hold credentials, without
    constraining the check to a presence/name/hash test (5a, 5b, 5c).
  - Touches secrets in any way (reading, printing, rotating,
    entering, or surfacing one in a report) and is delivered with no
    warning ABOVE the fenced block naming the secret, the row, and
    the exposure risk (5g).

═══════════════════════════════════════════════════════════════
SCORING DIMENSION: RULE 7 (PAPERWORK) BACKSTOP
═══════════════════════════════════════════════════════════════

Rule 7 of METHODS/ARCHITECT_DISCIPLINE.md (PAPERWORK FIRES ON STATE
CHANGE, NOT AT SESSION END — sub-points 7a-7f) binds the Architect
the same way Rule 1 does: the Architect cannot fully audit its own
blind spot toward undocumented state change while it is mid-pass and
moving fast. See METHODS/ARCHITECT_DISCIPLINE.md for the full rule
text and sub-points; this dimension does not retype it, it scores
against it.

FAIL the kickoff if it:
  - Creates schedulable infrastructure, a new tool, or a standing
    ruling without a documentation row in the same pass (7a, 7b).

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
                        Public, fetchable.
  
  Layer 2 (project):    AUDITOR_PRIMING.md in each project repo. 
                        Project identity, canonical doc placeholders,
                        project-specific audit dimensions. Lives in
                        the project repo (typically private).

Priming workflow (preferred — fetch-based):

  1. Spin up a new Claude.ai chat. Name it "[Project] — Auditor."

  2. First message instructs the Auditor to fetch Layer 1 from the
     canon repo URL and tells it that Layer 2 and canon docs follow.

  3. Second message pastes the project's AUDITOR_PRIMING.md (Layer 2)
     content.

  4. Third message pastes the project's canonical docs as requested
     by Layer 2.

  5. Auditor acknowledges and stands by.

Fetch URL for Layer 1 (public canon, main branch):

  https://raw.githubusercontent.com/kinestheticmarketing-stack/calibrated-design-canon/main/METHODS/AUDITOR_PRIMING_TEMPLATE.md

Priming workflow (fallback — paste-based):

  If the Auditor chat lacks web_fetch capability or the canon repo
  is temporarily unreachable, paste the full Layer 1 template
  content as the first message instead of having the Auditor fetch
  it. Layer 2 and canon docs follow as in steps 3-4 above.

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

  THE FAIL LOOP IS CLOSED. From the moment a FAIL verdict lands
  until the Auditor returns PASS or PASS-WITH-FLAGS on the revised
  artifact, NOTHING in that thread fires at the Executor. The
  revision artifact itself — including any revision kickoff — goes
  to the Auditor pre-fire. Architect skip discretion is suspended
  inside an active FAIL loop; there are no low-stakes exceptions,
  no "the output goes back to audit anyway" reasoning, no urgency
  override. The Director does not police this gate — the Architect
  holds it. An Architect that hands the Director an Executor-
  addressed block during an active FAIL loop has produced a defect.

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
