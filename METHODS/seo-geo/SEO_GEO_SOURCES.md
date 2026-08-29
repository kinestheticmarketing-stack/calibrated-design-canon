# SEO_GEO_SOURCES.md

*Source tier tracking and attribution for SEO/GEO directives.*

Every directive in the playbook is defensible by its source. This document tracks source tiers, named sources within each tier, and the courses/research being extracted into the canon.

═══════════════════════════════════════════════════════════════
SOURCE TIER FRAMEWORK
═══════════════════════════════════════════════════════════════

### Tier 1 — Primary sources from the engines
- Google Search Central (developers.google.com/search)
- Google Search Quality Rater Guidelines
- Schema.org
- Bing Webmaster Guidelines
- AI engine crawler docs (OpenAI GPTBot, Anthropic ClaudeBot, Perplexity PerplexityBot, Common Crawl CCBot)
- RFC 9309 (robots.txt formal spec)
- Sitemap protocol (sitemaps.org)
- OpenGraph spec (ogp.me)
- Twitter Cards docs
- llms.txt proposal (llmstxt.org)

### Tier 1.5 — The Google API Leak (March 2024)
- Mike King (iPullRank) primary analysis
- Rand Fishkin secondary analysis

### Tier 2 — Practitioner research with real data
- Ahrefs studies (Tim Soulo, Patrick Stox)
- Semrush research
- Backlinko (Brian Dean)
- Search Engine Land / Search Engine Journal

### Tier 3 — Named practitioners
- Mike King (iPullRank)
- Aleyda Solis
- Lily Ray (Amsive)
- Glenn Gabe (GSQi)
- Marie Haynes
- Bill Slawski (archived, SEO By The Sea)
- John Mueller / Martin Splitt / Gary Illyes (Google reps)
- Rand Fishkin (SparkToro)
- Cyrus Shepard
- **Glen Allsopp (Detailed)** — SEO Blueprint 3, extraction complete
- **Vahe Arabian (State of Digital Publishing)** — Publisher SEO Course, extraction complete
- Andrea Volpini (WordLift) — entity SEO

### Tier 4 — Information retrieval academic foundations
- "Introduction to Information Retrieval" (Manning, Raghavan, Schütze — Stanford)
- Google research papers (research.google)
- TREC proceedings (NIST)
- Anthropic / OpenAI / DeepMind RAG papers

### Tier 5 — GEO-specific sources
- Princeton GEO paper (Aggarwal et al., 2023)
- AI citation tracking platforms (Profound, AthenaHQ, Otterly, Peec.ai)
- Anthropic / OpenAI / Perplexity public statements on citation behavior

### Tier 6 — Noise (explicitly excluded)
- "Top 50 ranking factors" listicle content
- YouTube SEO gurus selling courses
- Pre-2018 SEO blog content
- Local SEO agencies selling directory submissions
- Anything promising specific outcomes from specific tactics
- AI-generated SEO content recycling other AI-generated SEO content

═══════════════════════════════════════════════════════════════
COURSES BEING EXTRACTED
═══════════════════════════════════════════════════════════════

### Glen Allsopp / Detailed / SEO Blueprint 3 (Tier 3)
- ✓ COMPLETE (9/9 modules + course extras). Source extraction closed 2026-06-18. Prefixes: TLB, TKR, TSC, TLO, TEB, TSP, TPB (221 tactic IDs total). See `sources/glen-allsopp-seo-blueprint-3/EXTRACTION_LOG.md`.
- On-Site Blueprint (58 lessons) — ✓ complete
- Link Building Blueprint (26 lessons) — ✓ complete
- Keyword Research Blueprint (15 lessons) — ✓ complete
- Super Content Blueprint (5 lessons) — ✓ complete
- Local SEO Blueprint (18 lessons) — ✓ complete
- Experts Blueprint (4 lessons) — ✓ complete
- Superpixels (29 lessons + 15 galleries) — ✓ complete
- SEO Blueprint 3 Playbook — ✓ complete for provided scope only; 8 report pages never supplied, re-open at TPB-10 if obtained (see README.md "Known gaps")
- Audits Blueprint (13 audits) — ✓ complete, mints no new tactic IDs

### Vahe Arabian / State of Digital Publishing / Publisher SEO Course (Tier 3)
- ✓ COMPLETE (7/7 modules + rollups). Prefixes: PIN, PTE, PCO, PTA, PPI, PRA, PCD (240 tactic IDs total). See `sources/vahe-arabian-publisher-seo/EXTRACTION_LOG.md`.
- Introduction, Technical SEO, Content SEO, Tactics, Practical Implementation, Reporting & Analytics, Content Distribution — all complete.
- Primary source for publisher-specific SEO (news sitemaps, Google Publisher Center, Bing News PubHub, crawl speed/frequency, E-E-A-T for publishers).

### SEO Jesus / One Page Websites 2025 (Tier 3, gray-hat-heavy)
- **NOT extracted.** Module folders exist (`intro/`, `01-finding-emds/`, `02-launching-sites/`, `03-niche-selection/`, `04-link-building/`) but are empty — no lesson files, no `EXTRACTION_LOG.md`, no rollups. This entry previously claimed "13 lessons already extracted"; that claim does not match the current working tree and has been corrected. See README.md "Known gaps" for detail. Extraction needs to be (re-)run before this source can be used in an audit.
- Intended as primary source for gray-hat reference documentation once extracted.
- Teaches: EMD-based rank-and-rent, citations purchased in bulk, expired domain redirects, PBNs, shared domains, paid guest posts, paid link insertions

### Kinesthetic Marketing AI Visibility Playbook (Tier 3)
- Lead-gen local-business focused, 5-step playbook
- Source for local-business AI visibility framing
- Limited depth on advanced technical SEO

### Additional courses (planned)
- 10-12 additional courses to be identified and extracted

═══════════════════════════════════════════════════════════════
EVIDENCE TIER ASSIGNMENT
═══════════════════════════════════════════════════════════════

Each playbook directive is tagged with one of:
- **CANONICAL** — direct from Tier 1 docs.
- **EMPIRICAL** — supported by Tier 2/3 studies or Tier 1.5 leak.
- **EMERGING** — Tier 5 (GEO frontier).
- **SPECULATIVE** — claimed without backing data.

Anything that doesn't fit one of these tiers is excluded from the playbook.

═══════════════════════════════════════════════════════════════
END OF SOURCES
═══════════════════════════════════════════════════════════════
