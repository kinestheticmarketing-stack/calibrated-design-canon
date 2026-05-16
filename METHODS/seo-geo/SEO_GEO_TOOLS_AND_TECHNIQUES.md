# SEO_GEO_TOOLS_AND_TECHNIQUES.md

*Implementation toolkit for SEO/GEO audit and intervention work.*
*Free-tier and paid-tier patterns. Each technique pairs with one or more audit dimensions.*

═══════════════════════════════════════════════════════════════
T1 — GOOGLE SEARCH OPERATORS FOR ANOMALY DISCOVERY
═══════════════════════════════════════════════════════════════

Free, no tooling required. Surfaces issues that crawlers miss because crawlers walk from the homepage outward via internal links, while Google's index reveals pages it found regardless of internal linking.

**Caveat:** Google's `site:` operator returns a sample, not the complete index. These techniques are diagnostic surface-finders, not exhaustive audits.

### T1.1 — Find pages on a domain
```
site:example.com
```

### T1.2 — Find non-HTTPS pages
```
site:example.com -inurl:https
```

### T1.3 — Find non-www pages
```
site:example.com -inurl:https -inurl:www
```

### T1.4 — Find pages without brand-suffix title
```
site:example.com -intitle:"Brand Name"
```

### T1.5 — Find pages with brand-suffix title (when most don't have it)
```
site:example.com intitle:"Brand Name"
```

### T1.6 — Find index-file URLs
```
site:example.com inurl:index
site:example.com inurl:index.php
site:example.com inurl:index.html
```

### T1.7 — Find stale year-stamped content
```
site:example.com intitle:[previous_year] -intitle:[current_year]
```

### T1.8 — Find title-tag/H1 desyncs (run with current-year date filter via Google Tools)
```
site:example.com intitle:[previous_year]
```

### T1.9 — Phrase search for duplicate content discovery
```
"distinctive sentence from candidate page"
```

**Source:** Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lessons 5, 6, 7, 8.

═══════════════════════════════════════════════════════════════
T2 — REGEX PATTERNS FOR URL AUDITS
═══════════════════════════════════════════════════════════════

For use in Screaming Frog (URL Address search field), Sitebulb, Google Sheets (Ctrl+F with regex enabled), or command-line `grep -E`.

### T2.1 — URLs ending with trailing slash
```
[\/]$
```

### T2.2 — URLs NOT ending with trailing slash
```
[^\/]$
```

### T2.3 — URLs containing uppercase letters
```
[A-Z]
```

### T2.4 — URLs containing query parameters
```
\?
```

### T2.5 — URLs ending in .php
```
\.php$
```

### T2.6 — URLs ending in .html
```
\.html$
```

**Source:** Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lesson 12.

═══════════════════════════════════════════════════════════════
T3 — REGEX PATTERNS FOR TITLE-TAG AUDITS
═══════════════════════════════════════════════════════════════

For use in Screaming Frog (Page Titles tab) or Google Sheets (Ctrl+F).

### T3.1 — Any repeated word (lenient)
```
\b(\w+)\b.*\b\1\b
```

### T3.2 — Repeated words of 4+ characters (filters short connectors)
```
\b(\w{4,})\b.*\b\1\b
```

### T3.3 — Adjacent duplicate words ("marketing marketing")
```
\b(\w+)\s+\1\b
```

### T3.4 — Repeated capitalized words only
```
\b([A-Z]\w+)\b.*\b\1\b
```

**Source:** Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lesson 13.

═══════════════════════════════════════════════════════════════
T4 — GOOGLE SHEETS IMPORTXML FOR ON-PAGE EXTRACTION
═══════════════════════════════════════════════════════════════

Free-tier alternative to paid crawlers for small-to-medium audits.

### T4.1 — Extract title tag
```
=IMPORTXML(A2, "//title")
```

### T4.2 — Extract meta description
```
=IMPORTXML(A2, "//meta[@name='description']/@content")
```

### T4.3 — Extract canonical URL
```
=IMPORTXML(A2, "//link[@rel='canonical']/@href")
```

### T4.4 — Extract H1 heading
```
=IMPORTXML(A2, "//h1")
```

### T4.5 — Extract robots meta directive
```
=IMPORTXML(A2, "//meta[@name='robots']/@content")
```

### T4.6 — Extract OpenGraph title
```
=IMPORTXML(A2, "//meta[@property='og:title']/@content")
```

### T4.7 — Extract OpenGraph description
```
=IMPORTXML(A2, "//meta[@property='og:description']/@content")
```

### T4.8 — Extract Twitter Card title
```
=IMPORTXML(A2, "//meta[@name='twitter:title']/@content")
```

### T4.9 — Extract all H2 headings
```
=IMPORTXML(A2, "//h2")
```

### T4.10 — Extract all internal/external links
```
=IMPORTXML(A2, "//a/@href")
```

### T4.11 — Extract schema.org JSON-LD blocks
```
=IMPORTXML(A2, "//script[@type='application/ld+json']")
```

**Caveat:** IMPORTXML has rate limits. Batch large URL lists. Reliability has degraded over time — for thousands of URLs, consider Apps Script or Python + BeautifulSoup.

**Source:** Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lesson 14.

═══════════════════════════════════════════════════════════════
T5 — GOOGLE SHEETS IMPORTHTML FOR LIVE TABLE EXTRACTION
═══════════════════════════════════════════════════════════════

### T5.1 — Import first HTML table from page
```
=IMPORTHTML("https://example.com/page", "table", 1)
```

### T5.2 — Import second HTML table
```
=IMPORTHTML("https://example.com/page", "table", 2)
```

### T5.3 — Import first HTML list
```
=IMPORTHTML("https://example.com/page", "list", 1)
```

**Source:** Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lesson 14.

═══════════════════════════════════════════════════════════════
T6 — GOOGLE SEARCH CONSOLE WORKFLOWS
═══════════════════════════════════════════════════════════════

### T6.1 — Identify top-30 lost-traffic pages
1. Open GSC > Performance > Search Results.
2. Set date comparison: last 3 months vs. prior 3 months (or 6 vs. 6).
3. Sort clicks by difference (descending).
4. Select top 30 pages.

### T6.2 — Identify cannibalization
1. For a target page, identify the queries that lost traffic.
2. Click on the query > Pages tab.
3. Check if other pages on the same site rank for the same query.

**Source:** Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lesson 9.

═══════════════════════════════════════════════════════════════
T7 — ARCHIVE.ORG HISTORICAL DIFF
═══════════════════════════════════════════════════════════════

For pages with traffic decline of unknown cause:
1. Open https://web.archive.org/web/*/[target-url]
2. Identify snapshots from before the decline.
3. Compare against current version.
4. Look for: title tag changes, headline changes, canonical changes, internal linking changes, content additions/deletions.

**Caveat:** Coverage is uneven. Some pages have daily snapshots, others yearly.

**Source:** Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lesson 9.

═══════════════════════════════════════════════════════════════
T8 — REDIRECT-CHAIN VERIFICATION TOOLS
═══════════════════════════════════════════════════════════════

- httpstatus.io
- redirect-checker.org

Use cases:
- Verify redirect type (301 vs. 302) on suspicious URLs.
- Identify multi-hop redirect chains.
- Identify language-routing or geolocation-based redirect divergence.

**Caveat:** Tool results vary by tool location (German-hosted tool may get redirected to .de variants). Cross-check with multiple tools.

**Source:** Glen Allsopp, SEO Blueprint 3, On-Site Blueprint Lesson 11.

═══════════════════════════════════════════════════════════════
T9 — CRAWLERS
═══════════════════════════════════════════════════════════════

### Screaming Frog SEO Spider
- Paid (~$200/year as of recording; verify current pricing).
- Supports regex search on URL Address and Page Titles.
- Standard tool for sites >500 pages.

### Sitebulb
- Paid alternative to Screaming Frog.
- Different UX, similar capabilities.

### DLC Crawler (Glen Allsopp's free tool)
- Free, distributed via SEO Blueprint 3.
- Cross-platform (Windows / Mac / Linux).
- Suitable for sites under 500 pages.
- Did not support regex search at time of course recording — verify current capability.

═══════════════════════════════════════════════════════════════
END OF TOOLS AND TECHNIQUES
═══════════════════════════════════════════════════════════════

This toolkit grows as new techniques are extracted from sources. Each technique cross-references the audit dimensions it serves and the lessons that document it.
