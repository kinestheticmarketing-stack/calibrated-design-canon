# Competitor On-Page Audit — IMPORTXML template

*seo-geo skill · templates · source: Glen Allsopp On-Site Blueprint L14 (titles/metas) + L15 (title-vs-H1), consolidated and extended.*

## When to reach for this

Pulling on-page signals (title, H1, meta, canonical, robots) off a **list of competitor URLs** in one pass, to read how they're positioning and where they're sloppy. Google Sheets + `IMPORTXML` fetches each URL's **served HTML** and extracts the nodes you ask for.

**Scope discipline — this is a COMPETITOR tool, not an own-site tool.** Our sites are generated from a single source of truth, so own-site titles/H1s/canonicals are diffed at the generator, not scraped from live HTML. Reach for this when auditing sites we don't control. (Exception: a quick own-site spot-check that the *served* HTML matches what the generator intends — useful precisely because it reads served HTML, see the caveat below.)

## The template

One row per URL. Paste URLs into column A; the formulas fill the rest. Row 2 shown — fill down.

| Col | Header | Formula (in row 2) |
|-----|--------|--------------------|
| A | URL | *(paste competitor URL)* |
| B | Title | `=IFERROR(IMPORTXML(A2,"(//title)[1]"),"—")` |
| C | H1 | `=IFERROR(IMPORTXML(A2,"(//h1)[1]"),"—")` |
| D | Title vs H1 | `=IF(EXACT(B2,C2),"Same","Different")` |
| E | Meta description | `=IFERROR(IMPORTXML(A2,"//meta[@name='description']/@content"),"—")` |
| F | Canonical | `=IFERROR(IMPORTXML(A2,"//link[@rel='canonical']/@href"),"—")` |
| G | Robots | `=IFERROR(IMPORTXML(A2,"//meta[@name='robots']/@content"),"— (none = default index,follow)")` |

`IFERROR(...,"—")` keeps misses clean instead of spraying `#N/A`. The `[1]` index on title/H1 returns the first node so multi-node pages don't error.

### Optional extra columns (add when relevant)
| Signal | XPath |
|--------|-------|
| og:title | `//meta[@property='og:title']/@content` |
| Word count proxy (H2 count) | `=COUNTA(IFERROR(IMPORTXML(A2,"//h2"),""))` |
| Schema present? | `=IF(IFERROR(IMPORTXML(A2,"//script[@type='application/ld+json']"),"")="","no","yes")` |

## How to read each column (the point of the audit)

- **Title** — their primary keyword targeting for that page. Generic/un-targeted title = a ranking gap you can take.
- **H1 vs Title (D)** — "Same" everywhere can be lazy duplication; "Different" can be intentional (title for SERP, H1 for humans). Read it against whether they rank.
- **Meta description** — their hook / pitch in their own words. Free positioning intel.
- **Canonical (F)** — self-referencing = healthy. Pointing at a *different* URL = they're consolidating (or misconfigured, telling Google not to rank the page you're looking at). Blank = no canonical, duplicate-URL exposure.
- **Robots (G)** — what they're choosing *not* to index. `noindex` on a page that should rank = an opening.

## Caveats (don't skip)

- **IMPORTXML reads served HTML — same as `curl`, no JavaScript.** If a competitor is a client-rendered SPA with JS-injected `<title>`/meta, those columns come back blank. **A blank is itself a finding:** their pages are invisible to non-JS crawlers and AI engines — the exact defect we fixed on kinestheticmarketing.com (shell titles served to crawlers while the real content was JS-only). So "—" can mean *no data* OR *they have the bug*. Confirm with a manual `curl -s URL | grep -i '<title>'` before concluding.
- **Sheets throttles `IMPORTXML`.** Large lists (hundreds of URLs) rate-limit and return transient errors. Batch ~50–100 at a time, or let it settle and re-pull.
- **Some sites block Google's fetcher / cloak by user-agent** → persistent `#N/A`. Not your error; note and move on.
- **`#N/A` ≠ no description.** It can be a fetch miss. Re-run a single suspect cell before trusting it.
- **One-time snapshot.** `IMPORTXML` recalcs on open/edit — values drift as competitors change pages. Copy-paste-as-values to freeze an audit you want to keep.

## 30-second setup

1. New Google Sheet. Row 1 headers: `URL · Title · H1 · Title vs H1 · Meta · Canonical · Robots`.
2. Paste the seven formulas above into B2:G2 (A2 = first URL).
3. Paste your competitor URL list into column A.
4. Select B2:G2, fill down to the last URL.
5. Let it resolve. Freeze with Copy → Paste-values-only if archiving.

*(Lessons 18/19/45 — bulk URL extraction + Link Clump — are how you assemble the column-A list fast from a SERP or a directory like the FT 1000 / Inc 5000.)*
