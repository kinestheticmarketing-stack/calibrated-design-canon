# SEO_GEO_AUDIT_DIMENSIONS.md

*Running index of audit dimensions for SEO/GEO work.*
*Each dimension maps to a checkable, verifiable test the Auditor can run against a site or artifact.*

═══════════════════════════════════════════════════════════════
STATUS
═══════════════════════════════════════════════════════════════

**Build phase:** Phase 1 — dimensions being added as source extractions complete.

═══════════════════════════════════════════════════════════════
DIMENSION FORMAT
═══════════════════════════════════════════════════════════════

Each dimension below includes:
- **ID** — short identifier (SG-NN).
- **Name** — descriptive title.
- **Layer** — Technical Foundation / GEO / Engagement / Operational.
- **Type** — Discovery / Diagnostic / Recovery / Compliance.
- **Sub-checks** — specific things to verify.
- **Implementation** — how to run the check (manual / regex / tool / query).
- **Severity tier** — Possibly Serious / Less Likely to Be Serious (per Glen Allsopp's framing, On-Site Blueprint Lesson 4).
- **Sources** — lessons/courses that document the dimension.

═══════════════════════════════════════════════════════════════
TECHNICAL FOUNDATION DIMENSIONS (LAYER 1)
═══════════════════════════════════════════════════════════════

### SG-01 — URL Variant Consistency

**Layer:** Technical Foundation
**Type:** Discovery + Diagnostic
**Severity:** Possibly Serious

Consolidates multiple sub-types of URL variant issues:
- Trailing slash vs. no trailing slash
- HTTP vs. HTTPS
- www vs. non-www
- index.php / index.html vs. clean URL
- Uppercase vs. lowercase paths
- Parameter URLs vs. clean paths

**Sub-checks:**
1. Force the opposite variant and observe behavior (redirect / load identical / 404 / load different).
2. Confirm redirect layer: 301 from non-canonical to canonical.
3. Confirm canonical-tag layer: `<link rel="canonical">` points to one variant only.
4. Confirm internal-link layer: all internal links use the canonical variant.
5. Identify the "rewarded version" from GSC and protect it from breaking changes.
6. Plan any cleanup in stages (P2 — 5% rule applies).

**Implementation:**
- Manual spot check: load both variants in browser.
- Search operator queries: `site:domain -inurl:https`, `site:domain inurl:index`, etc.
- Crawler-based regex filtering: `[\/]$` and `[^\/]$` for trailing-slash audits.
- Cross-reference robots.txt for misconfigured Disallow rules.

**Sources:**
- Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lessons 5, 6, 8, 10, 11, 12.

---

### SG-02 — Anomalous URL Discovery

**Layer:** Technical Foundation
**Type:** Discovery
**Severity:** Possibly Serious

Find pages that exist in Google's index but shouldn't — dev sites, staging environments, CDN duplicates, abandoned subdomains, parameter-URL bloat, pages-as-images, indexed third-party-hosted content.

**Sub-checks:**
1. Run `site:domain -inurl:https` to surface non-HTTPS pages.
2. Run `site:domain -intitle:"BrandName"` to surface title-convention deviants.
3. Stack negative operators to push into long tail.
4. Investigate each anomaly: source, slug pattern, redirect behavior, indexation status.
5. Use sentence-snippet phrase searches to identify duplicate content patterns.

**Implementation:**
- Google search operators.
- Cross-reference with crawler-based audit for completeness.

**Sources:**
- Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lessons 5, 6.

---

### SG-03 — Title-Tag Over-Optimization Detection

**Layer:** Technical Foundation + On-Page Content
**Type:** Discovery + Diagnostic
**Severity:** Possibly Serious (for stubborn pages)

Identify title tags with repeated keywords or unnatural keyword density that may be hindering rather than helping rankings.

**Sub-checks:**
1. Crawl site, extract all title tags.
2. Apply regex filter for repeated words within title strings.
3. Manually triage: real over-optimization vs. incidental matches.
4. For each real case, check ranking status (P4 — leave well alone if ranking).
5. For stubborn non-ranking pages, rewrite to natural-language form.
6. Apply P2 (5% rule) when rolling out template-level rewrites.

**Implementation:**
- Screaming Frog with regex search on Page Titles tab.
- Google Sheets with IMPORTXML + Ctrl+F regex search.
- Regex pattern: `\b(\w{4,})\b.*\b\1\b` for word repetition (4+ char words).

**Sources:**
- Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lesson 13.

---

### SG-04 — Year-Stamped Content Currency

**Layer:** Engagement Infrastructure
**Type:** Discovery + Diagnostic
**Severity:** Less Likely to Be Serious (but high ROI when found)

Identify evergreen content with stale year-stamps in titles, headlines, or URLs. Identify title-tag/H1 desyncs where editorial updated the page but missed the SEO plugin's separate title-tag field.

**Sub-checks:**
1. Run `site:domain intitle:[previous year] -intitle:[current year]` to find stale-year content.
2. Run `site:domain intitle:[previous year]` with current-year date filter (Google Tools) to find H1/title-tag desyncs.
3. Triage: news content stays as-is; evergreen content is refresh candidate.
4. For each candidate, update H1, title tag, body content, stats, publish date.
5. Run annually starting Q1 month 3.

**Implementation:**
- Google search operators with date-range filter.

**Sources:**
- Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lesson 7.

---

### SG-05 — Lost-Traffic Page Recovery Audit

**Layer:** Technical Foundation + On-Page Content + Engagement
**Type:** Recovery
**Severity:** Possibly Serious

Six-check sequence for pages that have lost significant search traffic.

**Sub-checks:**
1. SERP element changes — did featured snippet, PAA, video carousel, AI Overview, or expanded coverage appear for the target queries?
2. Searcher intent match — does the page's content type match what Google now rewards for these queries?
3. Archive.org historical diff — what changed on the page recently (title, headline, canonical, internal linking)?
4. Basic on-site audit — title relevance, canonical, year-stamp, internal links from related pages, headline accuracy, content depth.
5. Freshness factor — do top results show recency dates? Is the page stale?
6. Cannibalization — has another page on the site picked up the traffic for the same queries?

**Implementation:**
- Google Search Console (3-month and 6-month comparison views).
- Manual SERP review.
- Archive.org Wayback Machine.
- GSC Pages and Queries reports.

**Sources:**
- Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lesson 9.

═══════════════════════════════════════════════════════════════
GEO / AI SEARCH DIMENSIONS (LAYER 2)
═══════════════════════════════════════════════════════════════

**[IN PROGRESS]** — Dimensions to be added as GEO-specific extractions complete.

Likely future dimensions:
- Atomic answer block presence and length validation
- Quick Facts callout structure
- Question-form H2 structure
- Schema markup coverage (Organization, WebSite, Person, BreadcrumbList, FAQPage, HowTo, Article, LocalBusiness)
- AI crawler allow-list in robots.txt (GPTBot, ClaudeBot, anthropic-ai, PerplexityBot, Google-Extended, CCBot, ChatGPT-User)
- llms.txt presence and content
- Speakable schema targeting
- Entity association strategy

═══════════════════════════════════════════════════════════════
ENGAGEMENT DIMENSIONS (LAYER 3)
═══════════════════════════════════════════════════════════════

**[IN PROGRESS]** — Dimensions to be added as engagement-layer extractions complete.

Likely future dimensions:
- FAQ accordion presence and behavior
- TOC anchor structure
- Email capture placement and conversion
- Trust signal density (reviews, ratings, certifications, named contributors)
- Internal linking depth and anchor variety

═══════════════════════════════════════════════════════════════
OPERATIONAL DIMENSIONS (CROSS-LAYER)
═══════════════════════════════════════════════════════════════

### SG-OP-01 — Documentation Hygiene

Verify that audit findings, changes made, and decisions taken are recorded in project documentation (STATE_OF_PROJECT.md, DECISIONS.md, PROJECT_LESSONS.md per project conventions).

**Sources:** Calibrated Stack canon, inherited from AUDITOR_PRIMING_TEMPLATE.md universal dimensions.

---

### SG-OP-02 — Verification Discipline

Verify that any work producing binary outputs (generators, schema blocks, sitemap files) includes:
- MD5 hash comparison across regenerations.
- Determinism check.
- Smoke test after deploy.

**Sources:** Calibrated Stack canon, inherited from CVC.md principle 3.

═══════════════════════════════════════════════════════════════
END OF DIMENSIONS
═══════════════════════════════════════════════════════════════

This index grows as new dimensions are extracted. Each new dimension is added with full sub-check decomposition and source attribution.
