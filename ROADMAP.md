# ROADMAP.md

*The meta-canon for [Calibrated Vibe Coding](CVC.md). Tracks what's
shipped, what's being built, and what's planned next.*

═══════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════

The Calibrated Stack canon evolves continuously as the methodology
ships across more verticals and surfaces more failure modes. This
document is the running status board for what's in canon, what's
being drafted, and what's queued.

Every Architect chat working on Calibrated Stack projects should
familiarize itself with this roadmap before proposing canon work.
Recommendations that build toward the roadmap are preferred.
Recommendations that fall outside the roadmap should be flagged
as out-of-roadmap and confirmed with Director before proceeding.

═══════════════════════════════════════════════════════════════
SHIPPED CANON
═══════════════════════════════════════════════════════════════

Core philosophy and standards:
- MANIFESTO.md — the philosophical position
- CVC.md — the Calibrated Vibe Coding standard
- NAMING.md — naming conventions for projects and methods

Method specifications (METHODS/):
- the-calibrated-stack.md — the practitioner's method (four-role
  architecture)
- AUDITOR_PROTOCOL.md — Auditor role specification
- AUDITOR_PRIMING_TEMPLATE.md — universal Layer 1 priming for the
  Auditor
- ARCHITECT_DISCIPLINE.md — Architect workflow-discipline rules
  (patterns 1-5 currently canonized)
- RELATIONSHIP_DISCIPLINE.md — solo-operator network-building as
  canonized sales discipline; four mechanisms (substantive
  engagement, public canon, useful introductions, shared ideas);
  20% time budget
- GIVE_FIRST_DISCIPLINE.md — giving as explicit sales discipline;
  3:1 give-to-promote ratio; conversion mechanism for solo
  operators without paid distribution

Retrospectives (RETROSPECTIVES/):
- phase-2.6-kinesthetic.md — first full deployment of four-role
  Calibrated Stack on the Kinesthetic Marketing Funnel; 9 audit
  gates; 20-60x ROI on API-equivalent cost math; 5 friction patterns
  surfaced

═══════════════════════════════════════════════════════════════
IN-PROGRESS CANON
═══════════════════════════════════════════════════════════════

Queued for upcoming infrastructure-focused working sessions. Order
reflects priority, not strict dependency.

Architect-discipline pattern formalization:
- ARCHITECT_DISCIPLINE.md — formal canonization of patterns 6, 7,
  and 8 (currently canon-active in chats but not yet in the file):
  - Pattern 6: Design philosophy explicit BEFORE first execution
    kickoff
  - Pattern 7: Feedback-translation discipline
  - Pattern 8: Architect spec-drift as measured failure mode

Architect-discipline candidate patterns (surfaced from /names/
thread C session, pending canonization):
- Pattern 9 candidate: Stakes-escalation-crossing-thread-boundary
- Pattern 10 candidate: Voice-vs-Builder lane discipline scales to
  non-prose surfaces (JSON-LD, taxonomy labels, schema descriptions)
- Pattern 11 candidate: Strategic-intent vs technical-spec drift
  (sub-class of Pattern 8)
- Senior-review checkpoint between Step 0.5 and Step 1 on
  stakes-bearing infrastructure work

Methodology playbooks (METHODS/):
- SEO_GEO_PLAYBOOK.md — universal SEO/GEO discipline; three-layer
  structure (technical SEO foundation / GEO AI-search optimization /
  engagement and conversion infrastructure); applies to all projects
  from parked domains through full content sites
- SECURITY_PLAYBOOK.md — universal security discipline; five-layer
  structure (auth and authorization / payment and subscription state /
  secrets and credentials / error handling and observability /
  common vulnerability classes)
- SLASH_COMMAND_LIBRARY.md — catalog of reusable Claude Code slash
  commands for routine kickoff types
- CUSTOM_AGENTS_REGISTRY.md — catalog of named specialist agents
  (auditor, voice-checker, schema-validator, geo-auditor, etc.)
- PARALLEL_AUDIT_PROTOCOL.md — Claude Code subagent fan-out for
  parallel audit work (peer to AUDITOR_PROTOCOL.md for routine
  audits; chat-side Auditor remains for stakes-bearing audits)
- POLISH_PROTOCOL.md — Auditor-findings-to-fixes workflow codified
  as a reusable kickoff template
- HISTORY_AUDIT_TECHNIQUE.md — canonized diagnostic practice of
  periodically asking an agent to analyze prior conversation
  history and quantify failure modes by category with real counts
  (not "how do you think you did" — actual measured stats).
  Cross-model comparison when applicable. Run at phase boundaries,
  before canon-tidy sessions, and when a specific failure mode
  keeps recurring. Findings fold into canon updates: patterns get
  added to ARCHITECT_DISCIPLINE, corrections get added to
  userPreferences, incidents get memorialized in retros. Insight
  source: Theo (T3) 2026-10 workflow demo.
- DIAGNOSTIC_QUESTIONING.md — formalized practice of asking agents
  why they made specific decisions when unexpected output ships or
  canon violations happen. Standard questions: "what gave you
  indication that direction was right?", "which instructions did
  you follow?", "which instructions did you interpret as
  overridable?" Answers fold into canon updates that prevent
  misreads and priming templates that prevent re-occurrence.
  Insight source: Theo (T3) 2026-10 workflow demo.

Tooling conventions:
- SKILL_AUTHORING_CONVENTIONS.md — governance doc for how every
  future skill in the ecosystem gets written. Rules include:
  description is trigger-keyword list (not what-it-does),
  bad-example + good-example pairs are worth the space, metadata
  for scoping (which projects/roles/contexts should load this
  skill), one skill per specific job (not one super-skill).
  Prerequisite for SLASH_COMMAND_LIBRARY.md and
  CUSTOM_AGENTS_REGISTRY.md — ship this before those. Insight
  source: Theo (T3) 2026-10 workflow demo.

Methodology metrics:
- METRICS.md — multi-vertical methodology metrics tracking; per-
  vertical breakdown with aggregate roll-up; failure-mode-class
  attribution (Architect drafting / Architect spec-drift / Senior
  catch / Auditor catch / Builder catch); active-phase running
  tallies plus closed-phase finals

Methodology experiments:
- CROSS_MODEL_AUDITOR_EXPERIMENT.md — evaluate whether running the
  Auditor role on a different foundation model than the Architect
  (Claude Architect + GPT-5 Auditor, or Claude Architect + Gemini
  3.6 Auditor) catches distinct failure modes that same-model
  Auditor misses. Insight source: LLM Council pattern (Karpathy
  2026-01) plus Apple reinforced-agents paper (2026-05) both
  recommend different models for reviewer role. Formalize as
  canon if experiment shows measurable catch-quality improvement
  across 5-10 Auditor cycles.
- DECISION_COUNCIL_PROTOCOL.md — multi-model parallel deliberation
  for strategic-decision-shaped questions where sycophancy is the
  primary risk (course positioning, pricing tiers, strategic
  pivots, product-line calls). Peer to AUDITOR_PROTOCOL.md but for
  a different question class. Auditor reviews shipping-shaped work
  against canon; Decision Council reviews decision-shaped
  questions against cross-model consensus. Distinct tools for
  distinct problems.

Publishing infrastructure:
- NEWSLETTER_FORMAT.md — locked structure for the CVC publication;
  4 weekly field notes + 1 monthly synthesis cycle; feeds off
  structured artifacts from session-close discipline
- NEWSLETTER_VOICE.md — DR-newsletter voice canon; peer to
  COPY_VOICE.md but tuned for editorial register rather than sales
  register
- SESSION_CLOSE_PROTOCOL.md — canon rule that every working session
  produces or updates at least one structured artifact; prerequisite
  substrate for newsletter agent automation and metrics tracking

Meta-canon on the practice itself:
- THE_DIRECTOR_ROLE.md — explicit definition of the Director role as
  "the person who knows what completeness looks like"; not defined by
  title or ownership but by domain knowledge of what all the pieces
  are that must exist for the artifact to be real rather than a
  surface simulation
- CONVERSATIONAL_ARCHITECTURE.md — extended structured conversation
  as the current form of prompt engineering; documents why rigid
  prompt structures died (reasoning models internalized them) and
  what replaced them; names the practice the Calibrated Stack
  methodology is built on

Retrospectives (RETROSPECTIVES/):
- phase-2.7-kinesthetic.md — Phase 2.7 retro covering 5 surfaces
  shipped through Auditor; cycle compression hypothesis confirmed at
  6 data points
- names-thread-c.md — /names/ thread C retro covering the most
  complex single stakes-bearing kickoff in the methodology to date;
  13:1 Auditor-caught to Architect-self-caught ratio; baseline for
  future stakes-bearing kickoffs

═══════════════════════════════════════════════════════════════
PLANNED CANON
═══════════════════════════════════════════════════════════════

Lower priority than in-progress. Built when foundational pieces above
have shipped.

Project-type scaffolds:
- TEMPLATES/new-leadgen-site/ — bootstrap structure for new lead-gen
  sites following the Hermes Insulation pattern
- TEMPLATES/new-funnel-site/ — bootstrap structure for info product
  funnels following the Kinesthetic pattern
- TEMPLATES/new-multi-tenant-saas/ — bootstrap structure for
  multi-tenant SaaS following the Porter pattern

Specialist priming templates (for cross-project consistency):
- AUDITOR_PRIMING_SEO.md — Layer 2 priming for SEO/GEO audits
- AUDITOR_PRIMING_SECURITY.md — Layer 2 priming for security audits
- DATA_TRACKING_PRIMING.md — priming for the Data Tracking chat role

Workflow infrastructure:
- DRIVE_SCRATCHPAD_PROTOCOL.md — cross-chat coordination via shared
  Google Drive doc
- HANDOFF_TEMPLATE.md — locked structure for Vertical Architect →
  Senior Architect → Data Tracking handoffs

═══════════════════════════════════════════════════════════════
SEQUENCING RATIONALE
═══════════════════════════════════════════════════════════════

Why this order:

1. Architect-discipline patterns 6-11 get canonized first because
   they're already active in chats — formalization is paperwork, not
   new work. Cheap to ship.

2. SEO_GEO_PLAYBOOK.md and SECURITY_PLAYBOOK.md come next because
   they're high-leverage universal discipline docs that apply to
   every project. Each unlocks downstream products (Web Development
   Bundle, security tripwire, course modules).

3. SLASH_COMMAND_LIBRARY.md and CUSTOM_AGENTS_REGISTRY.md come after
   the playbooks because the playbooks are the source material the
   commands and agents operationalize. Build the doc, then build the
   tool that enforces it.

4. METRICS.md becomes more valuable as more verticals produce data.
   Building it earlier risks a thin schema that gets refactored.
   Building it after several phases have shipped means the schema
   reflects real data needs.

5. PARALLEL_AUDIT_PROTOCOL.md and POLISH_PROTOCOL.md are workflow
   accelerators that depend on the prior pieces existing. They graft
   on top of the established canon.

6. Project-type scaffolds and specialist priming templates are
   lower priority because they're consolidation work, not new
   capability. Ship them when there's time, not before.

7. Meta-canon on the practice itself (THE_DIRECTOR_ROLE.md,
   CONVERSATIONAL_ARCHITECTURE.md) captures the philosophical
   position that makes the methodology defensible against
   "just use ChatGPT" competition. Not urgent, but worth
   locking while the framing is fresh from recent sessions.

8. Methodology experiments (CROSS_MODEL_AUDITOR_EXPERIMENT,
   DECISION_COUNCIL_PROTOCOL) queue at lower priority than
   playbook canon. They refine the methodology at the margins;
   playbook canon establishes the methodology's substantive
   scope. Ship playbooks first, run experiments on top of
   proven foundations.

9. SKILL_AUTHORING_CONVENTIONS.md must ship BEFORE
   SLASH_COMMAND_LIBRARY.md and CUSTOM_AGENTS_REGISTRY.md
   because the conventions govern how those catalogs get
   authored. Shipping the catalogs first without conventions
   locked would produce inconsistent skill quality that has
   to be retrofitted later. HISTORY_AUDIT_TECHNIQUE.md and
   DIAGNOSTIC_QUESTIONING.md have no strict dependencies and
   can ship whenever there's bandwidth — they're peer
   methodology tools alongside AUDITOR_PROTOCOL.

═══════════════════════════════════════════════════════════════
UPDATE PROTOCOL
═══════════════════════════════════════════════════════════════

This roadmap updates at two natural trigger points:

1. After every canon-tidy session — shipped items move from
   "in-progress" to "shipped."

2. After every working session that surfaces new canon needs — new
   candidates get added to "planned" or promoted to "in-progress"
   based on Director's priority call.

The roadmap is meta-canon. Keeping it current is part of canon
maintenance. Stale roadmaps fail the methodology they document.

═══════════════════════════════════════════════════════════════
END OF DOCUMENT
═══════════════════════════════════════════════════════════════
