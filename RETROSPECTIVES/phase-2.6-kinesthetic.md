# Phase 2.6 Retrospective — Calibrated Stack in Practice

**Project:** Kinesthetic Marketing Funnel (kinestheticmarketing.com)  
**Phase:** 2.6 Retroactive Audit + Step 1 Remediation + Step 2 Build  
**Duration:** Multi-session, completed 2026-05-11  
**Methodology:** Four-role Calibrated Stack (Director / Architect / Executor / Auditor)  
**Audience:** Canon evolution stakeholders, future Architects in fresh sessions

---

## Executive summary

Phase 2.6 was the first full deployment of the four-role Calibrated Stack on a high-stakes, multi-surface phase boundary. The phase covered: retroactive Auditor pass on four already-shipped customer-facing surfaces; surgical Step 1 remediation; Step 2 build of a new public-facing tool surface (Meta Description Builder) with frontend infrastructure additions; three post-fix hardening commits; full closeout re-verification.

**Outcome: zero critical issues at any audit gate. Phase formally closed.**

The methodology earned its keep. The Auditor caught real things at every gate — none were minor. Several would have shipped without it, including a copy-paste-broken HTML tag that would have actively failed the educate-to-empower closeout for less technical visitors. Every catch saved a Claude Code retry cycle. Every retry cycle saved means real dollars saved.

But the phase also surfaced concrete friction patterns the canon doesn't yet address. Documented below with proposed canon additions.

---

## The numbers

### Audit gate counts

Total Auditor gates: 9. Verdicts: 2 FAILs, 4 PASS-WITH-FLAGS, 3 PASS. Zero PASS verdicts on first audit of any high-stakes artifact. Every artifact required at least one iteration cycle.

Per-artifact breakdown:
- Step 1 four-surface remediation kickoff: 3 audits (FAIL → PASS-WITH-FLAGS → PASS) — cheap iteration in chat, no Claude Code retries
- Step 1 post-fix re-verification: 1 audit (PASS-WITH-FLAGS) — 3 deferred items to Director
- Meta Description Builder copy pre-audit: 2 audits (FAIL → PASS) — locked v2 source-of-truth
- Step 2 kickoff pre-fire audit: 1 audit (PASS-WITH-FLAGS) — 4 Director adjudications, 3 inline fixes
- Step 2 post-fix re-verification: 1 audit (PASS-WITH-FLAGS) — 3 flags to Director
- Phase 2.6 closeout final confirmation: 1 audit (PASS) — full closure

### Director adjudication load

Across the phase, the Director made 19 adjudication decisions:
- 9 Auditor-recommendation rubber-stamps (Director picked the Auditor's recommended option) — fast, low-cost decisions
- 6 contested decisions where Director's pick differed from Auditor's recommendation — high-value Director taste calls
- 4 procedural sign-offs (timeframe pattern, segmentation backlog, etc.) — captured for audit trail

The 6 contested decisions are where Director taste genuinely shaped the artifact beyond what Auditor + Architect would have produced. Examples:
- Threading "four emails" before the §17 canonical phrase instead of after (one-off variant rather than formalized pattern)
- Adding the "how to install it" educate-to-empower closeout (Auditor flagged as Director's call; Director chose to add it)
- Routing the "GET THE 5-STEP PLAYBOOK →" CTA to /playbook instead of /scan

### Catches by stage

What the Auditor caught at each gate that would have shipped without it:

**Step 1 kickoff (3 audits):**
- First FAIL: 12 issues including unsourced stats, em-dash count drift, prose-marker test gaps
- Second PASS-WITH-FLAGS: 4 remaining items requiring Director adjudication
- Third PASS: clean

**Builder copy pre-audit (2 audits):**
- FAIL: em-dash count miscount (Architect counted 4, actually 7), §17 canonical partial-rewrite in two places, three CTAs shipped in sentence case instead of canonical ALL CAPS, \$400 unsourced specificity, P1/P2 logical seam
- PASS: clean v2

**Step 2 kickoff pre-fire (1 audit):**
- PASS-WITH-FLAGS: 7 flags including Tools Index NEW prose bypassing standalone pre-audit (re-committed the same §17 partial-rewrite the Builder v1 audit caught), secondary CTA destination mismatch (label promised playbook, destination was diagnostic), "90-second" asymmetry between body prose and CTA button

**Step 2 post-fix (1 audit):**
- PASS-WITH-FLAGS: 7 flags including curly-quote drift in Builder implementation (visual layer; source ASCII → rendered Unicode curly), coverage gap on Tools Index §17 phrase regression test

**Phase 2.6 final confirmation (1 audit):**
- PASS: all flags resolved or appropriately punted to Phase 3 readiness

### The Architect-failure rate

Worth being specific: across 9 Auditor gates, the Architect produced FAIL or substantive PASS-WITH-FLAGS verdicts on every single high-stakes artifact. The Auditor never returned a clean first-pass PASS on customer-facing copy.

This isn't a methodology problem. This is the methodology working exactly as designed — the Architect optimizes for "does this read well?" and the Auditor cold-reads for "does this comply with canon?" The two roles catch different things by construction. The Architect-as-first-drafter being wrong-on-first-pass is the EXPECTED state.

What would NOT be okay: Architect FAIL rates approaching 100% on routine adjustments after canon stabilizes. Phase 2.6's FAIL rate is partly because the canon itself was actively evolving during the phase (§17 variant approval, §3 scope clarification, §22-26 strategic frameworks all locked DURING the work). Later phases on stable canon should see Architect first-pass quality improve.

---

## Cost / ROI estimation

Rough best-estimate framing with assumptions called out.

### Auditor cycle costs (per gate)

A single Auditor cycle is one chat exchange. The Auditor reads the artifact, returns a verdict in protocol format. Both directions are bounded.

- Average tokens per Auditor gate: ~15-30K tokens (artifact in + verdict out)
- At Sonnet 4.6 pricing: ~\$0.06-0.12 per gate
- At Opus 4.7 pricing (likely closer to actual Auditor model): ~\$0.45-0.90 per gate

**Phase 2.6 total Auditor cost: 9 gates × ~\$0.75 avg = ~\$7.** Marginal at the dollar level.

### Saved-vs-retry framing

The relevant comparison is "what would each Auditor catch have cost in Claude Code rework if it had shipped?"

**Catch: curly-quote drift in install hint <meta> tag.**
- Without catch: visitor copies broken HTML, install fails, support time + reputation cost. Estimate: 30 min Director triage + 1-2 hr Claude Code remediation + ~30 min Director re-review.
- Rework cost: ~\$30-80 in Claude Code time, ~1 hour Director attention.
- Auditor + Director-spot-check cost to catch: ~\$2 + 5 min Director time.
- ROI: ~15-40x.

**Catch: §17 canonical partial-rewrite in Tools Index intro (re-committed pattern Builder v1 caught).**
- Without catch: drift propagates into next surface that copies the Tools Index pattern, doubles the cleanup cost.
- Rework cost: ~\$15-30 in Claude Code time, plus the meta-cost of canon-discipline erosion.
- Auditor cost to catch: ~\$1.
- ROI: ~15-30x. Meta-ROI on canon discipline: harder to quantify but plausibly larger.

**Catch: em-dash count miscount (Architect had 4, Auditor counted 7).**
- Without catch: PASS verdict given on copy that violates §3 cap by ~75%. Future audit gates downstream of this would inherit the bad count.
- Rework cost: full Builder copy re-iteration cycle, ~\$15-30 Claude Code if shipped + multi-step rework.
- Auditor cost: ~\$1.
- ROI: ~15-30x.

**Aggregate phase ROI estimate:** ~\$7 in Auditor costs prevented an estimated ~\$150-400 in Claude Code rework + multiple hours of Director attention recovery. Net ROI in the 20-60x range, consistent with the canon's 80-300x framing on individual catches at the high end.

### Where the methodology runs efficient

The cheap-iteration-in-chat pattern is the unsung win. When the Builder copy went FAIL → PASS-WITH-FLAGS → PASS across three Auditor cycles, each cycle was ~\$1-2. The alternative — firing FAIL-quality copy at Claude Code, getting back a broken build, doing remediation, refiring — would have cost ~\$30-80 per cycle. The methodology turns expensive sequential Claude Code retries into cheap parallel Auditor + Architect chat iterations.

### Where the methodology runs less efficient

Multi-stage adjudication accumulation. When an audit returns PASS-WITH-FLAGS with 4+ flags, each flag requires a Director adjudication round-trip. Phase 2.6's Step 2 kickoff PASS-WITH-FLAGS had 4 adjudications. Each is bounded but they stack — the kickoff revision phase ran ~2 hours of Director attention across the adjudication loop.

Future canon work could address this by formalizing "Auditor's recommendation is the default unless Director objects" patterns, reducing the rubber-stamp adjudications.

---

## Friction patterns — canon gaps documented

These are Architect-execution failures that recurred across the phase. Documented as patterns the canon should explicitly prevent rather than rely on Architect discipline.

### Pattern 1: Paste-targets that aren't self-contained

**Failure mode:** Architect tells Director "paste this into [Auditor / Claude Code]" but the message doesn't contain the complete pasteable artifact. Director scroll-stitches content from multiple parts of a message, or worse, hunts across messages.

**Frequency in Phase 2.6:** 2 documented instances, both flagged by Director, both required correction-and-redraft cycles.

**Already in PROJECT_LESSONS.md as locked lesson.** Worth promoting to calibrated-design-canon as cross-project rule.

**Proposed canon addition:** When the Architect instructs the Director to paste an artifact into another role's chat, the message containing that instruction must include the COMPLETE pasteable artifact within itself. Single-fenced-block discipline. No "use the copy from above" or "fill in [PLACEHOLDER]" references. The Director should never have to assemble the paste target from multiple message parts.

### Pattern 2: Multi-step chain breaks at the Architect's end

**Failure mode:** Architect issues multiple steps for the Director to execute. Director executes step 1 and reports back a result requiring Architect attention. Architect resolves step 1 but fails to re-issue step 2+ in the same response. Director is left guessing whether the next step is queued, completed, or forgotten.

**Frequency in Phase 2.6:** 1 documented instance during the curly-quote spot-check + TEST 7M parallel sequence. Director had to explicitly call out the broken chain.

**Proposed canon addition:** When the Architect breaks work into multiple steps and step N returns a result requiring Architect resolution, the response that resolves step N MUST explicitly re-issue step N+1 (or whatever comes next). Never leave the Director to remember the queued steps. Never ask the Director "did you do step N+1?" — that puts the bookkeeping burden on the Director, which inverts the workflow's intent.

If the Architect cannot remember what was queued (context drift, conversation length), the Architect must either re-read the conversation thread to recover the queue, OR explicitly state "I've lost the queue — can you confirm what's still pending?" rather than disguising the lapse as a status check.

### Pattern 3: Verification asks that aren't procedural

**Failure mode:** Architect asks Director to "verify X" or "spot-check Y" without specifying steps, what to look for, how to recognize success/failure, or report-back format.

**Frequency in Phase 2.6:** 1 documented instance (curly-quote spot-check). Director called it out explicitly: "You don't just tell me to go do something. You tell me how to do it step by step."

**Proposed canon addition:** Any Director verification request from the Architect must be procedural. The request must include:
- Numbered steps to perform the check
- Exact things to look for at each step
- How to recognize the success state vs. the failure state
- Specific format the Director should report back in

"Verify X" or "spot-check Y" is not an instruction; it's a hand-wave. Translate every verification ask into a numbered procedure before sending it.

### Pattern 4: Parallel-action confusion

**Failure mode:** Architect queues two parallel actions. When results come back staggered, Architect loses track of which result corresponds to which queued action.

**Frequency in Phase 2.6:** Multiple instances during the closeout phase. TEST 7M kickoff was lost in the queue and ended up re-issued as a duplicate; Claude Code caught it and returned "Skip — work already shipped" rather than duplicating.

**Proposed canon addition:** When the Architect queues parallel actions, the response that queues them must include a single explicit list of "what I'm waiting on" with each item clearly identified. When ANY result comes back, the Architect's response must restate the queue so the chain stays explicit. Lost queue items must be recovered by re-reading conversation, not by asking the Director.

### Pattern 5: Architect re-committing locked-canon violations

**Failure mode:** Architect helps lock a canon rule against a specific pattern, then commits the same violation in a later artifact while focused on prose quality.

**Frequency in Phase 2.6:** 1 documented instance (Tools Index intro paragraph). Auditor caught it at Step 2 kickoff pre-fire audit.

This is a real methodology gap. The Architect role optimizes for "does this read well?" The Auditor role catches canon violations. But the Architect SHOULD have caught its own canon violation here because the rule had been locked one kickoff prior.

**Proposed canon addition:** When the Architect drafts new prose for any artifact, before submitting it to the Director or Auditor for review, the Architect must explicitly check the prose against the most recently locked canon rules — particularly any rules locked WITHIN THE SAME PHASE or session. The "I helped lock this rule so I won't break it" assumption is empirically false; phase-active canon rules are exactly where Architect re-violations cluster.

Practical implementation: before any pre-audit submission, the Architect reads the COPY_VOICE.md change log entries from the current phase and explicitly verifies the draft against each one.

---

## Strategic frameworks landed during phase

Phase 2.6 also locked five strategic frameworks in COPY_VOICE.md §22-26. These weren't audit catches; they were brainstorming output captured as canon:

- §22 — Educate-to-empower discipline (every customer-facing micro-copy beat carries a WHY + example + assertion pattern)
- §23 — Audit-before-fire-audit-after-fix protocol (formalized the Auditor's two-pass discipline)
- §24 — Paste-target self-containment (locked lesson, see Pattern 1 above)
- §25 — Rebate-program acknowledgment scoping (HEAR Region 1 / Section 25C)
- §26 — Funnel-as-portfolio aesthetic (every customer-facing surface must silently demonstrate the methodology being sold)

The §22 educate-to-empower framework was the Auditor's most-cited canon section across the phase. The Builder's field-by-field microcopy was repeatedly flagged as "canon-quality work" per §22.

---

## What this phase tells us about the methodology

### Confirmed working

1. **Audit-before-fire prevents expensive rework.** Every Auditor catch on a kickoff was a prevented Claude Code retry. Aggregate ROI in the 20-60x range matches canon framing.

2. **Audit-after-fix catches drift between approved-spec and shipped-implementation.** Curly-quote drift would not have been caught by source-level review of the kickoff alone; the post-fix audit + Director spot-check caught it at the rendered-output layer.

3. **Cheap chat iteration beats expensive sequential Claude Code retries.** FAIL → PASS-WITH-FLAGS → PASS cycles at ~\$1-2 each are vastly cheaper than the Claude Code retry equivalents.

4. **Director adjudication on contested flags is high-value Director time.** The 6 contested adjudications shaped the artifact in ways neither Auditor nor Architect would have produced alone.

5. **The methodology scales to high-stakes phase boundaries.** Step 2 was a new public-facing surface, frontend infrastructure additions, multiple file changes, three customer-facing surfaces dependent on the tool existing. Methodology held.

### Confirmed needing canon work

1. **Architect-side workflow discipline needs explicit rules.** Patterns 1-5 above suggest the canon should include Architect-execution rules, not just artifact-quality rules.

2. **Multi-stage adjudication accumulation has friction cost.** Future work: formalize "Auditor recommendation is default unless Director objects" patterns to reduce rubber-stamp adjudications.

3. **Auditor recommendations on procedural items (test additions, coverage gaps) accumulate as backlog faster than they're addressed.** Phase 2.6 closed with several deferred items punted to Phase 3 readiness. Worth tracking deferral velocity.

### Open questions for canon evolution

1. Should the Auditor be allowed to PASS-WITH-FLAGS only N times before forcing a FAIL? Phase 2.6's Step 2 ran 2 consecutive PASS-WITH-FLAGS gates (kickoff pre-fire + post-fix), each with 4-7 flags. Director adjudication load was high.

2. Should the Architect's first-pass quality on canon-stable artifacts be measured as a discipline metric? If FAIL rates stay near 100% after canon stabilizes, that's a signal the methodology has a gap.

3. Should "Auditor pre-approval of prose patterns" exist for re-used surface structures? Phase 2.6 introduced the Tools Index pattern as new; Phase 4+ tool builds will re-use the structure. Worth pre-approving the structural pattern so each new tool's index card doesn't require fresh audit on the same structure.

---

## For canon evolution stakeholders

This retro is offered to support canon evolution work. Five proposed canon additions are documented in the Friction patterns section above. They emerged from observed failure modes in this phase, not from theoretical concerns.

The methodology's high-level architecture is working as designed. The gaps are in the Architect-execution layer — specifically around workflow discipline rules that the current canon assumes the Architect role will internalize automatically. Empirically, that assumption doesn't hold under context-pressure on long phases.

The proposed canon additions are bounded — they don't require methodology redesign, just rule additions in the existing Architect-role section.

---

**End of retrospective.**
