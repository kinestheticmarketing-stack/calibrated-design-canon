# SEO_GEO_PRINCIPLES.md

*Operational discipline for SEO/GEO work across all Calibrated Stack projects.*

These principles govern *how* SEO/GEO work is done, separately from *what* directives the playbook prescribes. They are durable, vertical-agnostic, and apply regardless of project type.

═══════════════════════════════════════════════════════════════
P1 — AUDIT FIRST, IMPLEMENT LATER
═══════════════════════════════════════════════════════════════

Never fix issues as they're discovered during an audit. Sweep the full site first, compile the complete list of findings, prioritize, then implement in batches.

**Why:** Bias-to-action breaks attribution. When traffic moves after multiple simultaneous changes, you can't identify which change caused which effect. Audit-first preserves the diagnostic capacity for future ranking shifts.

**Source:** Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lesson 2.

═══════════════════════════════════════════════════════════════
P2 — INCREMENTAL ROLLOUT (THE 5% RULE)
═══════════════════════════════════════════════════════════════

When fixing an issue that affects many pages, fix 5% of affected pages first. Observe Google's response over a defined window. Then roll out to the remaining pages in further increments.

**Why:** Sitewide changes carry sitewide risk. The 5% rule preserves rollback feasibility and surfaces problems before they propagate.

**Applies to:** Title-tag rewrites, canonical-tag changes, URL structure migrations, internal-link refactors, schema additions, any change affecting >50 pages.

**Source:** Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lesson 4.

═══════════════════════════════════════════════════════════════
P3 — CHANGE-BUNDLING PROHIBITION
═══════════════════════════════════════════════════════════════

Never fix multiple issue types simultaneously on the same surface. Don't fix redirects, title tags, header navigation, and H1 tags in the same release. Sequence them. Wait between releases.

**Why:** When traffic moves, attribution requires isolation. Bundled changes make it impossible to identify which change caused which effect.

**Source:** Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lesson 4.

═══════════════════════════════════════════════════════════════
P4 — LEAVE-WELL-ENOUGH-ALONE
═══════════════════════════════════════════════════════════════

Pages currently ranking well are excluded from "technically perfect" cleanup work. Even if their title tag is suboptimal, even if their date display is dated, even if their URL is ugly — they don't get touched. The risk of breaking what's working exceeds the upside of incremental optimization.

**Why:** The cleanest URL isn't always the right URL. The most optimized title isn't always the best title. The page's *ranking* is the evidence that the current state works; that evidence outweighs theoretical "best practice."

**Exceptions:** Clear technical errors that affect indexing or canonical signals (broken canonicals, parameter explosions, indexing-blocking misconfigurations).

**Source:** Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lesson 4. Reinforced in Lessons 10, 11, 13.

═══════════════════════════════════════════════════════════════
P5 — FORWARD-ONLY FOR ESTABLISHED SITES
═══════════════════════════════════════════════════════════════

When changing URL conventions, title-tag templates, or other site-wide patterns on established sites: apply the new convention to *future* content only. Don't retroactively change established URLs that already rank.

**Exception:** New sites with no established rankings — be bold, change everything, build it right from the start.

**Why:** Mass URL or convention changes risk rankings even with proper 301s. Forward-only changes carry zero risk and gradually migrate the site to better conventions over months.

**Source:** Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lessons 10, 11.

═══════════════════════════════════════════════════════════════
P6 — DESERVE-TO-RANK AS PRECONDITION
═══════════════════════════════════════════════════════════════

Before any technical audit fires on a site that has lost rankings, evaluate the site as an outsider:
- Does it reveal who's behind it?
- Is it updated with current insights?
- Does it work on mobile and tablet?
- Does it satisfy searcher intent?
- Is content hidden behind popups, ads, notification requests?

If the site fails this filter, no amount of technical SEO will save it. The content/UX work comes first.

**Source:** Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lesson 3.

═══════════════════════════════════════════════════════════════
P7 — SITE-LEVEL CAUSE FOR PAGE-LEVEL SYMPTOMS
═══════════════════════════════════════════════════════════════

Most page-level traffic losses are not page-level problems. They're symptoms of how Google sees the *site* — thin content elsewhere, low-quality pages indexed, content-quality drift, link profile changes.

When auditing a stubborn page, also audit the site as a whole. Fixing only the affected page often misses the actual cause.

**Source:** Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lessons 3, 9.

═══════════════════════════════════════════════════════════════
P8 — NO-SINGLE-CAUSE FRAMING
═══════════════════════════════════════════════════════════════

There is no one thing Google changed that can be reverse-engineered to restore rankings. Search is a multi-factor system. The mental model of "what's the one fix" is wrong.

Audit findings should be presented as a portfolio of issues to address, not as a search for the magic switch.

**Source:** Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lesson 3.

═══════════════════════════════════════════════════════════════
P9 — REACTIVITY DISCIPLINE
═══════════════════════════════════════════════════════════════

Don't react to daily or weekly ranking data. Search trends, seasonality, and SERP volatility create temporary movements that resolve without intervention.

Wait for clear patterns over months before triggering a recovery audit. Halloween costume pages losing traffic in November is not a problem to solve.

Google ships approximately 9 production changes per day (~654,000 experiments / 3,234 shipped improvements per year per their 2018 documentation). Volatility without a clear cause is the default state.

**Source:** Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lessons 3, 9.

═══════════════════════════════════════════════════════════════
P10 — FIELD-TESTED OVER THEORY-TESTED
═══════════════════════════════════════════════════════════════

Every directive in the playbook is labeled by evidence tier:
- **CANONICAL** — direct from Google/Bing/Schema.org/AI engine documentation, or from named patent/research/leaked documentation.
- **EMPIRICAL** — backed by data, studies, or case studies from credible practitioners.
- **EMERGING** — recent, plausible, evidence-thin, worth monitoring.
- **SPECULATIVE** — claimed but not backed by data shown in source.

Directives without at least EMERGING-tier evidence are excluded from the playbook.

**Source:** Cross-cutting principle, reinforced throughout extracted sources.

═══════════════════════════════════════════════════════════════
P11 — VERIFICATION REQUIRED ON BINARY OUTPUTS
═══════════════════════════════════════════════════════════════

Inherited from the Calibrated Stack canon: SEO work that produces binary outputs (generated pages, sitemaps, schema blocks, redirect rules) includes explicit verification:
- MD5 hashes on generated files (catch silent regeneration failures).
- Determinism checks (regenerate twice, hashes match).
- Smoke tests after deploy.
- Human eye-check on visual output.

Silent failure is the enemy. Inherited from [The Calibrated Stack](../the-calibrated-stack.md).

═══════════════════════════════════════════════════════════════
END OF PRINCIPLES
═══════════════════════════════════════════════════════════════

These principles are durable. They apply regardless of which tactical directives the playbook prescribes. When a new directive enters the playbook, it must be compatible with these principles — or the principle gets explicitly amended, never silently overridden.
