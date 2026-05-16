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

Methodology metrics:
- METRICS.md — multi-vertical methodology metrics tracking; per-
  vertical breakdown with aggregate roll-up; failure-mode-class
  attribution (Architect drafting / Architect spec-drift / Senior
  catch / Auditor catch / Builder catch); active-phase running
  tallies plus closed-phase finals

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
