# SEO_GEO_PLAYBOOK.md

*A method-level specification under [Calibrated Vibe Coding](../../CVC.md).*
*Source-of-truth document for SEO and GEO discipline across all Calibrated Stack projects.*

═══════════════════════════════════════════════════════════════
STATUS
═══════════════════════════════════════════════════════════════

**Build phase:** Phase 1 — extraction in progress.

This document is the canon-level playbook. It synthesizes directives from primary sources documented in `sources/`. The skeleton below outlines the eventual structure; sections marked **[IN PROGRESS]** are still being built from source extractions.

═══════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════

The SEO/GEO Playbook is the canonical reference for search visibility work across all Calibrated Stack projects — lead-gen sites, info-product funnels, parked-domain showcases, one-page holding sites, web apps, and SaaS.

It defines:
- Technical SEO foundation requirements (Layer 1)
- GEO / AI search optimization requirements (Layer 2)
- Engagement and conversion infrastructure requirements (Layer 3)
- Parked-domain minimum tier (the universal floor)
- Audit dimensions for each layer
- Operational discipline (how to make changes safely)
- Substance discipline (what is forbidden regardless of effectiveness)

═══════════════════════════════════════════════════════════════
SCOPE
═══════════════════════════════════════════════════════════════

**In scope:**
- Technical on-page SEO (titles, meta, canonicals, URL structure, schema, sitemaps, robots.txt, redirects, indexation, crawl optimization)
- GEO / AI search optimization (atomic answers, llms.txt, AI crawler handling, entity association, citation engineering, FAQ schema, Speakable)
- On-page content patterns (question-form H2s, atomic answer blocks, topical clustering, internal linking, page templates, content depth)
- Link acquisition strategy (white-hat, gray-hat reference, forbidden)
- Local SEO (NAP, GBP, citations, service-area considerations, review velocity)
- Off-page brand and entity building
- Programmatic and content-scale patterns
- Measurement, diagnostics, server log analytics

**Out of scope:**
- Paid advertising (Google Ads, Meta Ads, etc.)
- Social media organic strategy
- Email marketing / drip sequences
- Conversion rate optimization beyond what schema and atomic answers provide
- Generic content marketing for non-search-driven contexts

═══════════════════════════════════════════════════════════════
THE THREE-LAYER STRUCTURE
═══════════════════════════════════════════════════════════════

**[IN PROGRESS]** — Full directive content to be added as extractions complete.

**Layer 1: Technical SEO Foundation**

The substrate. What makes a site crawlable, indexable, and understandable by search engines and AI engines alike. Schema markup, canonicals, robots.txt, sitemaps, meta tags, semantic HTML, URL structure, Core Web Vitals.

**Layer 2: GEO / AI Search Optimization**

The signal layer. What makes a site discoverable, citable, and preferred by AI search engines (ChatGPT, Claude, Perplexity, Google AI Overviews) and traditional search engines that increasingly use AI in their result generation. Atomic answer blocks, question-form H2s, FAQ schema, llms.txt, entity association, citation engineering, Speakable targeting.

**Layer 3: Engagement and Conversion Infrastructure**

The conversion layer. What turns visibility into outcome. FAQ accordions, TOC anchors, email capture, interactive widgets, trust signals, content freshness, CTR optimization.

═══════════════════════════════════════════════════════════════
THE PARKED-DOMAIN MINIMUM TIER
═══════════════════════════════════════════════════════════════

**[IN PROGRESS]** — Definition to be locked after extraction.

Every project, regardless of surface type or scope, satisfies a minimum tier. Even a one-page holding site gets:
- Full Organization + WebSite schema
- OpenGraph + Twitter Card meta
- llms.txt
- robots.txt with AI crawler allow-list
- sitemap.xml
- Canonical tag
- Descriptive title and meta description

The parked-domain minimum is the spine. Every additional surface type (lead-gen suburb pages, info-product funnel steps, calculator pages, SaaS landing pages) adds requirements on top of the minimum.

═══════════════════════════════════════════════════════════════
VOICE AND SUBSTANCE DISCIPLINE
═══════════════════════════════════════════════════════════════

**Forbidden by canon:**

- Fabricated reviews or testimonials of any kind.
- AggregateRating schema without verified, real reviews to back it.
- False Person schema (claimed contributors, authors, or experts who don't exist or who didn't contribute).
- Invented quotes attributed to real people.
- References to dead, expired, or non-current rebate / regulation / pricing programs as if they're active (except in explicitly date-stamped historical context).
- Schema markup that misrepresents the nature, location, or operations of the business.

These rules apply absolutely. The Calibrated Stack canon does not compromise on truth claims. Operators who choose otherwise are operating outside the canon.

═══════════════════════════════════════════════════════════════
CONSERVATIVE-BY-DEFAULT, AGGRESSIVE-PATH-DOCUMENTED
═══════════════════════════════════════════════════════════════

Where tactics carry real risk of penalty, de-indexing, or business consequences, the playbook leans toward the conservative path while documenting the higher-leverage alternative honestly.

For each risk-bearing tactic, the playbook surfaces:
- The conservative path (what we recommend)
- The aggressive path (the higher-leverage alternative)
- What you're risking if you choose the aggressive path
- What to monitor if you choose the aggressive path (is the tactic currently being hunted by enforcement?)

Operators are adults. The playbook gives them what they need to decide; they decide.

═══════════════════════════════════════════════════════════════
HANDLING DISAGREEMENT
═══════════════════════════════════════════════════════════════

When sources disagree on a tactic or principle, the playbook surfaces the disagreement explicitly rather than picking a side prematurely. For each disagreement:
- Position A (with source attribution)
- Position B (with source attribution)
- Reasoning for each
- Evidence shown (or absence of evidence)
- The playbook's position — picked, unsettled, or context-dependent

This posture exists because most SEO content pretends there's one right answer when there isn't. Sophisticated readers see through false confidence. Honest documentation of disagreement is more credible than fabricated consensus.

═══════════════════════════════════════════════════════════════
KEYWORD-SELECTION DISCIPLINE (MODULE 3: L01, L07)
═══════════════════════════════════════════════════════════════

Two standing process rules from the Keyword Research Blueprint module, adopted
as canon. Both fire on every page build, not just once.

### Rule 1 — Keyword-Selection Lens (L01)

Before building any new page or content brief, the brief MUST state:
- The single PRIMARY target query the page is built to rank for.
- The search INTENT behind it (informational / commercial / transactional / navigational).
- A SERP-REWARD CHECK: someone has eyeballed the live SERP for that query to confirm the page
  TYPE being built (roundup / service page / guide / calculator / atomic-answer) matches what
  Google already rewards there. If the SERP shows listicles and you're building a service page,
  that's a mismatch — flag it before building.

No page gets built without these three stated. Missing them = build halts until supplied.

### Rule 2 — Stick-to-the-Wall Testing (L07)

Before generalizing a NEW page-type across the generator/site at scale, TEST one instance
against a proven competitor pattern first:
- Identify a competitor page already ranking for the target query-type.
- Model the new page-type on what's demonstrably working (structure, depth, format).
- Ship ONE, verify it holds up / ranks, THEN roll the pattern out.

Never mass-generate a brand-new page-type on assumption. One proven instance gates the rollout.

═══════════════════════════════════════════════════════════════
RELATED DOCUMENTS
═══════════════════════════════════════════════════════════════

- `SEO_GEO_AUDIT_DIMENSIONS.md` — checkable dimensions used in audits
- `SEO_GEO_TOOLS_AND_TECHNIQUES.md` — implementation patterns (search operators, regex, IMPORTXML, etc.)
- Competitor on-page scrape (titles, H1, meta, canonical, robots via IMPORTXML) → `templates/competitor-onpage-audit.md`
- `SEO_GEO_PRINCIPLES.md` — operational discipline (5% rule, change-bundling rules, leave-well-enough-alone rule, etc.)
- `SEO_GEO_SOURCES.md` — source tier tracking and attribution
- `SEO_GEO_GRAY_HAT_REFERENCE.md` — gray-hat tactics, documented for informed operator decisions
- `SEO_GEO_TACTICS_STATUS_TRACKER.md` — living document tracking which tactics are currently durable, frontier, or dead
- `sources/` — primary source extractions

═══════════════════════════════════════════════════════════════
END OF SKELETON
═══════════════════════════════════════════════════════════════

Full directive content under each layer is being built from source extractions. See `sources/` and the `EXTRACTION_LOG.md` files for what has been captured.
