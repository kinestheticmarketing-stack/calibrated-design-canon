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
EXPERT REFINEMENTS (extracted signal, hype stripped)
═══════════════════════════════════════════════════════════════

**Source #1:** Caleb Ulku (YouTube @calebulku) — 10-yr local-SEO agency owner,
critique-breakdown of a viral vibe-coded diesel-mechanic site. Extracted 2026-07-02.

**Method:** experts leak finite, load-bearing details inside critiques — the specifics
their tool or service does that a free-prompt AI misses. Apply the trivium to every
expert source before banking anything: separate what's SAID (the claim) from whether
it FOLLOWS (the logic) from WHY it's framed that way (the rhetoric / sales motive).
Extract the load-bearing technique; discard the marketing hyperfocus.

**Filing principle:** this SEO skill is CAPABILITY-FIRST and SOURCE-AGNOSTIC. Glen
Allsopp's Blueprint modules are the current spine because that course was the first
big complete input and got structured in first — NOT because Glen is the authority.
Every source (Glen, Caleb Ulku, future local-SEO / parasite-SEO / link-building
courses) is a TEST SUBJECT graded by what demonstrably improves results, then filed
onto the module-shelf(s) it deepens. The spine can be reorganized if a better
structure emerges; results are load-bearing, no single source is. Each refinement
below is tagged with the module-shelf(s) it sharpens.

**Governing correction for this source** (a 10-year local-SEO agency owner critiquing
a viral vibe-coded diesel-mechanic site): the expert's own framing — "the website
doesn't matter, GBP is everything" — is rhetoric that contradicts his own tactics,
every one of which depends on the website existing and being correct. The corrected
model: **the website is the qualifying base layer.** It substantiates the entity
claims the GBP makes — GBP is the claim, the website is the evidence Google
corroborates it against. Build order stays locked: on-site foundation first (fully in
your control, now) → GBP / entity layer (outside your control but directly workable,
next tier) → outreach / links (long-shot, last tier). The five refinements below
STRENGTHEN the base layer and the tiers above it — none of them invert that order.

### Refinement 1 — Structured Internal Linking (mirror the category tree, not "what seems relevant")

The sharpest detail in the source. AI systems and Google build their picture of a
site from its INTERNAL LINK STRUCTURE, not its URL structure. Default AI-assisted
internal linking free-associates ("these pages feel related") — that's the wrong
model. Links must deliberately follow the category → service tree: for local
properties, that tree is the GBP category/service hierarchy; for non-local
properties, it's the site's own service taxonomy. This is the concrete fix for the
internal-linking blind spot flagged in earlier audits. Free, on-site, do-now.
Applies to ALL properties — only the source of the tree differs (local vs.
non-local).

**Module-shelf:** Module 1 (On-Site) primary + Module 5 (Local SEO) overlay. NOTE:
Module 1 audit treated internal links as crawl-plumbing only; this ADDS the
authority/entity-structure dimension it missed.

### Refinement 2 — Entity/Category Research Axis (a second research axis, local properties)

Not a replacement for keyword research — keywords stay in the process, neutral-to-
helpful, no penalty for continuing to do them. This is an ADDITION: for local
properties, research the GBP primary category, secondary categories, and services
that the ranking competitors actually use, then complete your own profile to match.
That research drives three things: (a) GBP setup itself, (b) which pages the site
needs (a page per category/service the competitors are winning with), and (c) the
internal-link structure in Refinement 1. This is a research input for the Ahrefs
blitz month. Applies to LOCAL properties (DCI, Denver trades, mechanic sites, Don's
Garage). Non-local properties stay keyword-first, unchanged.

**Module-shelf:** Module 5 (Local SEO), feeds the Ahrefs blitz research. LOCAL
properties only.

### Refinement 3 — Hyper-Local Means Local Eccentricities, Not Landmark Trivia

Listing nearby landmarks ("we serve customers near the old clock tower") is geo
trivia — weak, doesn't signal real local expertise. Writing about problems SPECIFIC
to the area's actual conditions is real entity relevance. Source example: lead
main drain lines in old Boston housing stock vs. newer California construction —
a genuine regional difference a local expert would know and a generic writer
wouldn't. For DCI: Denver-specific insulation realities (altitude, old-Denver
housing stock, climate loads) beat generic "insulation in [suburb]" copy. This
sharpens content that's already being written — no new content type, just a test
before publishing it. Applies to LOCAL properties.

**Module-shelf:** Module 5 (Local SEO) for the local-relevance principle + Module 4
(Super Content) for the deep-content craft. LOCAL properties.

### Refinement 4 — Rank-Grid Measurement for Local (a measurement method, later tier)

Don't judge local ranking from a single search — proximity means rank varies across
a geographic mesh around the business. The correct measurement method is a rank
grid: check position across a grid of points, then target the cells sitting at
position 4-7 to push into the top 3. Single-point checks (like the L09 SERP
spot-check) are directionally useful but insufficient as the measurement method once
a property reaches the GBP/local-pack tier. Applies to LOCAL properties, at the
GBP/measurement tier — not a base-layer concern.

**Module-shelf:** Module 5 (Local SEO) + Module 9 (Audits Blueprint) for measurement
method. LOCAL properties, GBP/measurement tier.

### Refinement 5 — GBP Categories Are a Fixed Dropdown; AI Hallucinates Them

A concrete setup gotcha: asking an AI "what GBP category should I use" produces
invented categories that don't exist in Google's actual, fixed category list. GBP
category selection must be picked from the real dropdown, never AI-generated —
verify any AI-suggested category against Google's current category list before
using it. Prevents a real setup error at the GBP tier. Applies to LOCAL properties,
GBP-setup tier.

**Module-shelf:** Module 5 (Local SEO), GBP-setup tier. LOCAL properties.

**Extraction pattern is repeatable** — future expert sources get mined the same way
(trivium filter: claim / logic / rhetoric → extract the load-bearing detail, discard
the hype) and banked here.

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
