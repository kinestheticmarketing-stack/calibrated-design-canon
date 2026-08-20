# SEO_GEO_TACTICS_STATUS_TRACKER.md

*Living document. Tracks the current durability of each named tactic in the playbook.*

═══════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════

SEO and GEO tactics shift faster than canon documents. A tactic that's durable today may be killed by a Google update next quarter. This tracker is the living layer that ages between canon-doc revisions.

Each tactic gets a status review approximately quarterly, or whenever a named algorithm update or enforcement announcement affects its viability.

═══════════════════════════════════════════════════════════════
STATUS DEFINITIONS
═══════════════════════════════════════════════════════════════

- **DURABLE** — Currently works, low penalty risk, stable. Continue to use if part of canon.
- **FRONTIER** — Currently works but engines actively hunting or recently announced enforcement. Increased risk; monitor closely.
- **DEAD** — Used to work, doesn't now. Don't use. Listed for historical reference and to flag still-being-sold tactics.

═══════════════════════════════════════════════════════════════
LAST FULL REVIEW
═══════════════════════════════════════════════════════════════

**Date:** [TBD — pending first full review after extraction phase complete]

═══════════════════════════════════════════════════════════════
TRACKER TABLE
═══════════════════════════════════════════════════════════════

**[IN PROGRESS]** — Tracker entries to be populated as gray-hat reference completes.

Format for each entry:

| Tactic | Status | Last Reviewed | Enforcement Event | Notes |
|--------|--------|---------------|-------------------|-------|

═══════════════════════════════════════════════════════════════
RECENT ENFORCEMENT EVENTS
═══════════════════════════════════════════════════════════════

Major enforcement events that have shifted tactic durability:

- **May 2024** — Google launches Site Reputation Abuse policy. Third-party parasite SEO on rented authority subdomains: FRONTIER → DEAD.
- **March 2024** — Google API documentation leak. Confirms NavBoost, Chrome user data feeding ranking, site-wide authority metrics. Doesn't directly change tactic durability but informs strategy.
- **September 2023 → ongoing** — Helpful Content Updates continue. Mass AI content: DEAD. Thin programmatic content (without real differentiation): DEAD.
- **April 2024** — Google updates spam policies to explicitly target scaled content abuse, site reputation abuse, expired domain abuse.

═══════════════════════════════════════════════════════════════
MONITORING SOURCES
═══════════════════════════════════════════════════════════════

For each quarterly review, check:
- Google Search Status Dashboard (status.search.google.com)
- Search Engine Land / Search Engine Journal (named-update tracking)
- Glenn Gabe's algorithm update analysis
- Lily Ray's E-E-A-T and algorithm coverage
- Mike King's iPullRank technical analyses



═══════════════════════════════════════════════════════════════
LLS — LUTHER LANDRO, *THE LOCAL SEO CHECKLIST* (2024 ed.)
ADMISSIBILITY SCREEN — SCHEMA EXTENSION
═══════════════════════════════════════════════════════════════

**Screened:** 2026-08-20. **Corpus:** `sources/luther-landro-local-seo-checklist/`,
110 tactics LLS-01..LLS-110, contiguous, zero gaps, zero duplicates (re-verified).
**Screened against:** DCI (Denver, 73 pp.), LGM (Longmont, 47 pp.), GCI (Greeley,
34 pp.) — live, revenue-generating insulation-referral properties.
**Full working record:** `/tmp/lls_phaseA_screen.md`. **Gate:**
`sources/luther-landro-local-seo-checklist/SKILL_GATE.md`.

**SCHEMA NOTE — read before using this section.** The tracker's existing `Status`
column is a **durability** axis (DURABLE / FRONTIER / DEAD): does the tactic still
work against current engine behavior. The `Disposition` column added below is an
**admissibility** axis (ADMITTED / BLOCKED / SKIP): may it be executed on a live
revenue property. **These are orthogonal.** A tactic can be DURABLE and still
BLOCKED (LLS-33, Google Analytics, works fine and is blocked on a published-privacy
ground), and a tactic can be DEAD and still ADMITTED as a standing prohibition
(LLS-45, article marketing). Do not collapse one into the other.

Durability was **not** assessed in this pass and is recorded as `—` except where the
corpus supplies unambiguous evidence. A durability review of LLS is still owed.

**DISPOSITION DEFINITIONS**

- **ADMITTED** — executable on a live revenue property as-is, or under the single
  stated adaptation in the Notes column.
- **BLOCKED** — would put a live revenue property at risk. Permanent. Never executed
  under any framing, reframing, or light version. Every block carries its reason
  here so a later wave does not re-litigate it.
- **SKIP** — build-order. Requires Google Business Profile, link building, directory
  submission, local citations, review generation/solicitation, or paid rank tooling.
  Out of scope for this phase; not a judgment on the merits.

**PRECEDENCE RULE APPLIED:** safety outranks scope. A tactic that is both
out-of-scope-now and unsafe-whenever is BLOCKED, not SKIPPED, so it cannot re-enter
when build order opens. This is why LLS-62, LLS-63, LLS-108 and LLS-109 are blocked
rather than skipped.

**RESULT:** 79 ADMITTED / 13 BLOCKED / 18 SKIP. Blocked ratio on the scored set
(excluding SKIPs) = 13/92 = **14.1%**, against the Floate reference of 39/54 =
72.2%. The divergence is corpus composition, not threshold drift: 69 of Landro's
110 tactics (63%) are on-site work on an owned property, a mechanism that never
died, and a further 11 are prohibitions that admit by construction. Floate's core
mechanism — placement on rented authority — was killed outright by the May 2024
site reputation abuse policy. Full reasoning in `/tmp/lls_phaseA_screen.md`.


### BLOCKED — 13 tactics. Never executed on DCI / LGM / GCI.

Each row carries its block reason. A blocked tactic does not enter the skill and is not executed under any reframing.

| Tactic | Disposition | Status | Last Reviewed | Enforcement Event | Notes |
|---|---|---|---|---|---|
| LLS-09 — Every page carries ≥500 words | BLOCKED | DEAD | 2026-08-20 | Sep 2023→ Helpful Content; thin/padded content | A universal word-count quota across 154 live pages forces padding on pages whose intent is served short. 500 words has never been a Google threshold at any point; mechanically inflating a live page set to hit a self-invented floor is the scaled-thin-content pattern the Helpful Content Updates target. The thin-page *detection* use survives at LLS-08 and LLS-73. |
| LLS-26 — Image alt attributes and filenames contain city and state | BLOCKED | DEAD | 2026-08-20 | Keyword stuffing; never Tier 1 supported | Geo-injecting every alt attribute and filename across an image library is keyword stuffing in a low-value field. The corpus itself records this as author-assertion-only with no Tier 1 convergence. On a live public property it degrades screen-reader output — a real accessibility regression bought for a ranking effect no source supports. |
| LLS-32 — Generate local schema and include it | BLOCKED | — | 2026-08-20 | — | As written this prescribes generator-produced LocalBusiness markup asserting the site *is* the local business. These are referral properties, not the contractor — that markup is a false entity claim, which is structured-data spam and manual-action exposure, and it asserts an identity for a contractor the site does not own (B12). Schema on types the property can truthfully claim (WebPage, Article, FAQPage, BreadcrumbList, Organization for the referral entity) is legitimate, already shipped, and is *not* what LLS-32 says. |
| LLS-33 — Google Analytics installed | BLOCKED | — | 2026-08-20 | — | These properties run first-party pageview counting behind a kill switch, with a privacy page that was deliberately revised to disclose exactly that. Installing Google Analytics adds third-party tracking the live published disclosure does not cover — a published-policy contradiction on a revenue property. The measurement need is met by LLS-34/35 plus the existing first-party counter. |
| LLS-40 — Social sharing buttons present (Facebook, Twitter, Yelp, Foursquare) | BLOCKED | — | 2026-08-20 | — | The source concedes no ranking input. On these properties the buttons are third-party scripts that inject tracking the live privacy disclosure does not cover — the same contradiction as LLS-33 — plus render-blocking weight, and two of the four named targets are inert for local purposes. Zero demonstrated upside against a real privacy and performance cost. |
| LLS-53 — Use the disavow tool to neutralize inherited links | BLOCKED | — | 2026-08-20 | — | Disavow is a destructive, effectively irreversible instrument. Google's current position is that the great majority of sites should never touch it — it is for manual-action recovery and known paid-link liability, not routine hygiene. Filing one on a live revenue property removes links that may be helping with no undo on any useful timescale. Superseded within the same course by LLS-94, which is admitted. |
| LLS-62 — Donate to local charities that publish and link to sponsors | BLOCKED | DEAD | 2026-08-20 | Google link-scheme policy — paid links | Money paid, link received, charitable purpose incidental to the motive: this is a paid link under Google's link-scheme policy regardless of the wrapper. It contradicts LLS-51 in the same course, and the corpus records that it fails the author's own earned-versus-acquired test. Blocked rather than skipped so it cannot re-enter when build order opens. |
| LLS-63 — Use press releases for content syndication (as a backlink source) | BLOCKED | DEAD | 2026-08-20 | Google link-scheme policy — unmarked syndicated links | Links carried inside syndicated press releases are treated as a link scheme unless nofollow/sponsored-marked, and the source lists this under backlink sources. Commissioning release distribution also sprays near-duplicate copy about a live referral property across low-quality outlets. The implied link value has not held for over a decade. |
| LLS-96 — Screenshot the failure as the artifact that carries the conversation | BLOCKED | — | 2026-08-20 | — | **Primary ground: NEVER-FABRICATE (Director ruling 2026-08-20, R5).** Blocked as a dependent of LLS-97: this artifact exists to carry LLS-97's revenue-lost claim, and that claim is fabricated because it rests on period statistics the corpus forbids carrying forward. The artifact cannot be honest while the number it delivers is not. **Secondary ground: B12** — the artifact is also a characterization of a named contractor's competence, and these properties are rented to the very trades it would be built against. There is no light version; the artifact *is* both the fabrication vehicle and the characterization. |
| LLS-97 — Frame the mobile deficit in customers and revenue lost | BLOCKED | — | 2026-08-20 | — | **Primary ground: NEVER-FABRICATE (Director ruling 2026-08-20, R5).** The tactic requires asserting a specific revenue-and-customers-lost figure for a named business. That figure is built on period mobile statistics keyed to a 2015 crossover projection the corpus explicitly instructs must not be carried forward — so the number would be fabricated at the point of use, every time, with no sourcing path that fixes it. This is the root block; 96 and 99 fall as its dependents. **Secondary ground: B12** — it also asserts a named business is losing customers through its own deficiency. |
| LLS-99 — Audit-to-offer ladder: mobile rebuild → SEO → content → email | BLOCKED | — | 2026-08-20 | — | **Primary ground: NEVER-FABRICATE (Director ruling 2026-08-20, R5).** Blocked as a dependent of LLS-97: the ladder's entry rung is the LLS-96 artifact carrying LLS-97's fabricated revenue-lost figure. Productizing a fabricated number into a service sequence inherits the fabrication; nothing above the first rung survives without it. **Secondary ground: B12** — the same entry rung is a competence characterization. |
| LLS-108 — Charity sponsor listings: donate small, take the listing | BLOCKED | DEAD | 2026-08-20 | Google link-scheme policy — paid links | Identical mechanism to LLS-62 — money for a link with a charitable wrapper. Blocked on the same grounds and blocked rather than skipped so build order cannot revive it. The corpus records the author raising this contradiction against his own LLS-51 and never resolving it. |
| LLS-109 — Press releases as link attractors; resell at a markup | BLOCKED | DEAD | 2026-08-20 | Google link-scheme policy — unmarked syndicated links | Same grounds as LLS-63. The author's correction (the release is not the backlink) is honest, but the tactic still commissions syndicated distribution of near-duplicate copy carrying unmarked links about a live revenue property, which is a link scheme. The resale-at-markup half is agency business with no SEO payload. |

### ADMITTED — 79 tactics. Eligible, with the stated adaptation where given.

Where the Notes column states an adaptation, the adaptation is binding — the tactic is admitted in its adapted form, not as written.

| Tactic | Disposition | Status | Last Reviewed | Enforcement Event | Notes |
|---|---|---|---|---|---|
| LLS-01 — Seed set = niche descriptor + location | ADMITTED | — | 2026-08-20 | — | As-is. |
| LLS-02 — Verify each candidate returns local results before adopting | ADMITTED | — | 2026-08-20 | — | Qualify on local *organic* presence; these properties have no map-pack surface until build order. |
| LLS-03 — Harvest Google suggested/related terms into the seed list | ADMITTED | — | 2026-08-20 | — | Related-searches block restructured; harvest People Also Ask / People Also Search For instead. |
| LLS-04 — Run seed list through a keyword planner for volume | ADMITTED | — | 2026-08-20 | — | Substitute Search Console query data plus free SERP surfaces for the ad-account-gated planner; Keywords Everywhere is now paid-credit. |
| LLS-05 — Run the search scoped to the service area, not nationally | ADMITTED | — | 2026-08-20 | — | As-is. |
| LLS-06 — Generate variations rather than stopping at the seed phrase | ADMITTED | — | 2026-08-20 | — | As-is. |
| LLS-07 — Prioritize highest-volume terms within the qualified set | ADMITTED | — | 2026-08-20 | — | Intent first, volume second — LLS-72 corrects this item and the video position wins. |
| LLS-08 — Homepage carries ≥500 words including the keywords | ADMITTED | — | 2026-08-20 | — | Read as a thin-page smoke test on one page, not a quota. |
| LLS-10 — No misspellings or grammar errors | ADMITTED | — | 2026-08-20 | — | As-is. |
| LLS-11 — Primary keyword in the page URL | ADMITTED | — | 2026-08-20 | — | New URLs only. Never rewrite a live revenue URL for keyword cosmetics. |
| LLS-12 — Privacy statement and required disclosures exist | ADMITTED | — | 2026-08-20 | — | Must name the real data controller and reflect actual behavior — GCI's privacy page already discloses first-party pageview counting. Never regress to generator output. |
| LLS-13 — No duplicate content findable online | ADMITTED | — | 2026-08-20 | — | The live risk is cross-property duplication across DCI/LGM/GCI — three sibling sites in one vertical. Remedy is canonical selection and genuine per-city differentiation, not deletion. |
| LLS-14 — Title tags ≤65 characters | ADMITTED | — | 2026-08-20 | — | Truncation is pixel-width, not character count; ~60 chars is the practical read. Advisory, not a gate. |
| LLS-15 — Meta descriptions 90–155 characters | ADMITTED | — | 2026-08-20 | — | Same pixel-width caveat. Advisory. |
| LLS-16 — Internal links on every page, Wikipedia-style density | ADMITTED | — | 2026-08-20 | — | Contextual body links to genuinely related pages. Density is not the target; relevance is. |
| LLS-17 — Synonyms and variants of the head keyword throughout | ADMITTED | — | 2026-08-20 | — | Guarded by LLS-49. |
| LLS-18 — Target keyword present in titles | ADMITTED | — | 2026-08-20 | — | As-is. |
| LLS-19 — City and state in the title tag | ADMITTED | — | 2026-08-20 | — | Four-surface geo model — apply only to pages with genuinely distinct content. See doorway ceiling below. |
| LLS-20 — City and state in the headline | ADMITTED | — | 2026-08-20 | — | Same doorway guard. |
| LLS-21 — City and state in the page content | ADMITTED | — | 2026-08-20 | — | Same doorway guard. |
| LLS-22 — City and state in the page URL | ADMITTED | — | 2026-08-20 | — | New URLs only; same doorway guard. |
| LLS-23 — CSS and JS loaded externally, not inline | ADMITTED | — | 2026-08-20 | — | Critical inline CSS for LCP is now correct practice; the live rule is no large inline blocks. |
| LLS-24 — Minimize the count of CSS/JS documents | ADMITTED | — | 2026-08-20 | — | Blanket concatenation predates HTTP/2 multiplexing. Target total bytes and render-blocking, not file count. |
| LLS-25 — Image alt attributes and filenames contain target keywords | ADMITTED | — | 2026-08-20 | — | Alt text is accessibility copy first; keyword inclusion only where it is also an accurate description. |
| LLS-27 — Headlines use H1 tags | ADMITTED | — | 2026-08-20 | — | As-is. |
| LLS-28 — Header tags in hierarchical order | ADMITTED | — | 2026-08-20 | — | As-is. |
| LLS-29 — XML sitemap exists | ADMITTED | — | 2026-08-20 | — | As-is. |
| LLS-30 — robots.txt exists | ADMITTED | — | 2026-08-20 | — | As-is. |
| LLS-31 — All text on the site is searchable | ADMITTED | — | 2026-08-20 | — | Flash is EOL (Dec 2020); the live failure modes are text baked into images and content rendered only by client-side JS. |
| LLS-34 — Search Console property installed and verified | ADMITTED | — | 2026-08-20 | — | Free, first-party, owned-property instrumentation. Current naming is Search Console. |
| LLS-35 — Bing Webmaster Tools installed | ADMITTED | — | 2026-08-20 | — | Same class. |
| LLS-36 — Both webmaster properties checked for reported errors | ADMITTED | — | 2026-08-20 | — | Standing recurring check, not a one-time pass. |
| LLS-37 — Site resolves on both www and non-www | ADMITTED | — | 2026-08-20 | — | One canonical host serving 200; the other 301-redirects. Both serving 200 is the duplicate-host defect, not the fix. |
| LLS-38 — Site has a blog | ADMITTED | — | 2026-08-20 | — | Only with a quality floor: each post answers a real homeowner question with something the property can truthfully say and source (B13/B14 apply). An unfed or padded blog is worse than none — see LLS-91 and LLS-101. |
| LLS-39 — Site passes Google's mobile-friendly assessment | ADMITTED | — | 2026-08-20 | — | Standalone tool retired; assessment now lives in Search Console and Lighthouse. |
| LLS-41 — Site is not generating duplicate content internally | ADMITTED | — | 2026-08-20 | — | Remedy is canonicalization and parameter handling, which the source never supplies. |
| LLS-42 — Broken-link scan run | ADMITTED | — | 2026-08-20 | — | The repo already carries `_check_links.py` as a committed gate. Use it, judged by exit code — not the abandoned Windows freeware the source names. |
| LLS-43 — Speed test through Google's tooling | ADMITTED | — | 2026-08-20 | — | PageSpeed Insights plus a Core Web Vitals field-data read, which the source predates entirely. |
| LLS-44 — Speed test through a second independent tool | ADMITTED | — | 2026-08-20 | — | As-is; the named product has changed. |
| LLS-45 — Do not use article marketing | ADMITTED | DEAD | 2026-08-20 | Link schemes / mass directory syndication | Standing prohibition. Vocabulary is period; the underlying prohibition on mass directory syndication holds and has hardened. |
| LLS-46 — Do not repeat the same exact-match anchor across backlinks | ADMITTED | — | 2026-08-20 | — | Carried as a standing prohibition. The in-scope application on an owned property is internal anchors — vary internal anchor text rather than repeating one exact-match geo string sitewide. |
| LLS-47 — Do not use spun content | ADMITTED | DEAD | 2026-08-20 | Sep 2023→ Helpful Content; Apr 2024 scaled content abuse | Standing prohibition. The live form is unreviewed mass AI output, DEAD per the tracker's enforcement log. |
| LLS-48 — Do not use scrapers or automated content generators | ADMITTED | DEAD | 2026-08-20 | Sep 2023→ Helpful Content; mass AI content DEAD | Load-bearing distinction: this prohibits automatic generation of page *text*. It does not prohibit the build system — `regen_all.sh` templating that assembles human-authored content is not what this rules out. |
| LLS-49 — Do not over-stuff pages with keywords | ADMITTED | — | 2026-08-20 | — | Standing prohibition; it is the guard on LLS-17 through LLS-25. |
| LLS-50 — Do not use private blog networks | ADMITTED | DEAD | 2026-08-20 | Google link-scheme policy | Standing prohibition. |
| LLS-51 — Do not pay for backlinks | ADMITTED | DEAD | 2026-08-20 | Google link-scheme policy | Standing prohibition. This is the rule that blocks LLS-62 and LLS-108 in the same course. |
| LLS-52 — Do not use automated or mass-submission backlinking services | ADMITTED | DEAD | 2026-08-20 | Google link-scheme policy | Standing prohibition. |
| LLS-66 — Content-first premise: content attracts links and visitors | ADMITTED | — | 2026-08-20 | — | Holds only where the content answers a query the property can actually rank for. The course has no distribution model at all — content-first is not a substitute for distribution. |
| LLS-67 — Declared out-of-scope: PBNs, spun content, paid mass backlinks | ADMITTED | DEAD | 2026-08-20 | Apr 2024 scaled content abuse / link-scheme policy | Standing scope-exclusion rule. Restates LLS-47/50/51 as a business decision; the de-indexing mechanism claimed is wrong (current mechanism is non-ranking under scaled-content-abuse policy) but the exclusion is right. |
| LLS-68 — Research pipeline: SERP related terms → sheet → planner → sort → export | ADMITTED | — | 2026-08-20 | — | Substitute PAA/PASF for the retired related-search block and Search Console query export for the ad-gated planner. Pipeline shape survives; every interface shown has moved. |
| LLS-69 — Multi-target geographic scoping — several municipalities at once | ADMITTED | — | 2026-08-20 | — | The single most transferable item in the corpus for a Denver/Longmont/Greeley corridor portfolio. Note the source never answers how to split resulting terms across suburb pages versus consolidating — that decision is ours and is where the doorway ceiling binds. |
| LLS-70 — Problem-phrased query mining alongside service-name terms | ADMITTED | — | 2026-08-20 | — | High value here — homeowner phrasings ("cold floors over the garage", "upstairs won't cool") rather than trade vocabulary. |
| LLS-71 — Re-run surviving high-volume terms to confirm local results at term level | ADMITTED | — | 2026-08-20 | — | As-is. Closes the gate the written checklist leaves open at research time only. |
| LLS-72 — Volume does not qualify a term on its own; intent read required | ADMITTED | — | 2026-08-20 | — | As-is. This is the corrective on LLS-07 and the most valuable sentence in the lesson. |
| LLS-73 — Word-count verification by paste-into-counter | ADMITTED | — | 2026-08-20 | — | As a thin-page detector, not against the blocked 500-word quota at LLS-09. |
| LLS-74 — Grammar and spelling pass via spell-check | ADMITTED | — | 2026-08-20 | — | As-is. |
| LLS-75 — Header logo links to the homepage | ADMITTED | — | 2026-08-20 | — | As-is. |
| LLS-76 — Brand-name domain versus search reality | ADMITTED | — | 2026-08-20 | — | Already embodied — the properties run geo+service exact-match domains rather than brand names. |
| LLS-77 — Duplicate content check by submitting the live URL to a detection service | ADMITTED | — | 2026-08-20 | — | The live application is cross-property: check DCI/LGM/GCI against each other, not just against the open web. Remedy is canonical selection, which the source omits. |
| LLS-78 — View-source audit of title, description, and the legacy keywords field | ADMITTED | DEAD | 2026-08-20 | Keywords meta ignored by Google since 2009 | Audit title and description in source. The keywords meta field has been ignored by Google since 2009 — do not add one, do not curate one to a "two to three term ceiling", and do not treat an existing one as a penalty. The source's stated mechanism is wrong; the "unsophisticated site" signal reading is fair. |
| LLS-79 — Character-count the meta description | ADMITTED | — | 2026-08-20 | — | Pixel-width caveat per LLS-15. |
| LLS-80 — Internal link depth check past the nav menu | ADMITTED | — | 2026-08-20 | — | As-is. |
| LLS-81 — Four-surface geo audit executed live (title / headline / body / URL) | ADMITTED | — | 2026-08-20 | — | Audit form of LLS-19..22. Same doorway guard: a page that passes all four surfaces on a template swap and nothing else is a doorway page, not an optimized page. |
| LLS-82 — Detect inline CSS and JavaScript in the page source | ADMITTED | — | 2026-08-20 | — | Deliberate critical-CSS inlining is correct practice and is not a finding. |
| LLS-83 — Minification check on each script | ADMITTED | — | 2026-08-20 | — | Minify in the build. Never paste a live property's JS into a third-party online compressor and redeploy the output. |
| LLS-84 — Image filename and alt audit via inspect-element | ADMITTED | — | 2026-08-20 | — | Audit for descriptive accuracy and hyphenated filenames — the source prefers underscores, which is backwards; Google reads hyphens as word separators. Do **not** inject city and state into every alt: that half is blocked at LLS-26. |
| LLS-85 — Header tag audit via inspect-element | ADMITTED | — | 2026-08-20 | — | As-is. Missing H1 with CSS-class visual headings is a structural failure, correctly called. |
| LLS-86 — robots.txt and sitemap verification at the domain root | ADMITTED | — | 2026-08-20 | — | Confirm the sitemap referenced in robots.txt actually resolves and parses. Standing check. |
| LLS-87 — Flash and SWF check via source search | ADMITTED | DEAD | 2026-08-20 | Adobe Flash EOL 2020-12-31 | Inert as written — Flash is EOL Dec 2020 and cannot appear in a static build. The live equivalent of the check is content rendered only by client-side JS, which this lesson never addresses. Admitted as harmless with the check redirected; see borderline notes. |
| LLS-88 — Structured-data presence check via a rich-results testing tool | ADMITTED | — | 2026-08-20 | — | The endpoint used is retired; current equivalents are the Rich Results Test and the Schema.org validator. These properties already emit `dateModified` on three schema types — run this as a standing regression check, not a one-time pass. |
| LLS-89 — Analytics presence check by searching source for the tracking-ID prefix | ADMITTED | — | 2026-08-20 | — | **Director ruling 2026-08-20 (R4) — corpus fidelity correction.** As written, this tactic audits for the PRESENCE of third-party analytics. Admissible (it carries no risk), but it resolves **NOT-APPLICABLE** in property scoring on the same ground as the LLS-33 block: these properties run first-party pageview counting and publish a privacy disclosure saying so, and third-party analytics would contradict it. An earlier draft of this row inverted the tactic into a negative-control scan for third-party tracking IDs; that inversion **overreached and is withdrawn** — Landro did not prescribe it, and the tracker must not claim he did. The negative-control scan is a **separate proposed validator**, tracked outside this corpus, not an LLS verdict. The source's UA-format prefix would not match GA4 in any case. |
| LLS-90 — Confirm the site resolves on both www and non-www | ADMITTED | — | 2026-08-20 | — | Audit form of LLS-37; same redirect caveat. |
| LLS-91 — Blog presence and recency check | ADMITTED | — | 2026-08-20 | — | As-is. A blog publishing images with no indexable text is worth nothing to search — correctly called, and it is the guard on LLS-38. |
| LLS-92 — Page load time check | ADMITTED | — | 2026-08-20 | — | As-is; the mobile-abandonment reasoning holds. The cited period statistics do not — carry no figure forward. |
| LLS-94 — Disavow only with cause; default is to leave the profile alone | ADMITTED | — | 2026-08-20 | — | Standing prohibition protecting an owned property, not build-order. Never file a disavow on DCI/LGM/GCI absent an identified manual action. This is the video position that supersedes LLS-53, which is blocked. |
| LLS-95 — Run the mobile-friendly test down a live local result list | ADMITTED | — | 2026-08-20 | — | Strip the prospecting use entirely. Retained only as a competitor-set technical read on the local SERP for our target terms — no output about any named business leaves the analysis. |
| LLS-98 — A tool pass is not a UX pass — load the URL on a real device | ADMITTED | — | 2026-08-20 | — | As-is. Correct standing rule; supersedes the binary mobile-friendly checkbox at LLS-39. |
| LLS-104 — Content outsourcing economics — do not buy cheap content | ADMITTED | — | 2026-08-20 | — | The live form of "cheap content" is unreviewed AI output. The floor for these properties is that every claim on the page is independently verifiable against a live primary source, under B13 and B14. |
| LLS-105 — Client-first sequencing — never buy capacity before revenue is collected | ADMITTED | — | 2026-08-20 | — | Reframed as portfolio budgeting: content spend on DCI/LGM/GCI is funded from collected referral revenue, not anticipated revenue. Business-operations rule, not an SEO mechanism — see borderline notes. |

### SKIP — 18 tactics. Build-order; not adjudicated on the merits this pass.

Deferred pending build order. Recorded for completeness only; these were excluded from the admitted/blocked ratio denominator.

| Tactic | Disposition | Status | Last Reviewed | Enforcement Event | Notes |
|---|---|---|---|---|---|
| LLS-54 — Claim-and-feed profiles as a unit | SKIP | — | 2026-08-20 | — | — |
| LLS-55 — Respond to every negative review and comment | SKIP | — | 2026-08-20 | — | — |
| LLS-56 — Actively solicit honest reviews from satisfied customers | SKIP | — | 2026-08-20 | — | — |
| LLS-57 — Work the named fifteen-platform claim list | SKIP | — | 2026-08-20 | — | — |
| LLS-58 — Create every account under the exact business name (NAP) | SKIP | — | 2026-08-20 | — | — |
| LLS-59 — Answer-engine links (Quora / Stack Overflow / answers sites) | SKIP | — | 2026-08-20 | — | — |
| LLS-60 — Join the chamber of commerce, take the member listing link | SKIP | — | 2026-08-20 | — | — |
| LLS-61 — Sponsor student clubs and sports teams for .edu sponsor pages | SKIP | — | 2026-08-20 | — | — |
| LLS-64 — Journalist-sourcing services for citation and links | SKIP | — | 2026-08-20 | — | — |
| LLS-65 — Mine competitor backlink profiles for replicable sources | SKIP | — | 2026-08-20 | — | — |
| LLS-93 — Inventory the backlink profile with a link-analysis tool | SKIP | — | 2026-08-20 | — | — |
| LLS-100 — Profiles as branded-SERP ranking real estate | SKIP | — | 2026-08-20 | — | — |
| LLS-101 — The stale claimed profile as the common failure | SKIP | — | 2026-08-20 | — | — |
| LLS-102 — Review response as a productized service | SKIP | — | 2026-08-20 | — | — |
| LLS-103 — Point-of-sale review solicitation | SKIP | — | 2026-08-20 | — | — |
| LLS-106 — The four-source frame as a bounded link-acquisition set | SKIP | — | 2026-08-20 | — | — |
| LLS-107 — Q&A targeting by working backward from the customer question | SKIP | — | 2026-08-20 | — | — |
| LLS-110 — Journalist sourcing: register expertise, answer reporter queries | SKIP | — | 2026-08-20 | — | — |

**STANDING CAVEAT ON THE ADMITTED GEO SET.** LLS-17 and LLS-19 through LLS-22, plus
their audit form at LLS-81, are safe per-page and are the doorway-page mechanism when
applied as a template swap across a suburb page set. This portfolio is three
geo-cloned properties in one vertical — the highest-risk configuration for exactly
that failure. The admission is conditional on the four geo surfaces being filled on
pages that carry genuinely distinct content, never as the differentiator that makes
an otherwise-identical page distinct.

**PROPERTY-SPECIFIC BLOCKS.** LLS-33 (Google Analytics) and LLS-40 (social share
buttons) are blocked on a ground specific to these properties: they run first-party
pageview counting behind a kill switch with a privacy page deliberately revised to
disclose exactly that, and both tactics inject third-party tracking the live
disclosure does not cover. If the owner changes that privacy posture, these two —
and only these two — should be revisited on that basis.

**OPEN ITEM.** Durability (DURABLE / FRONTIER / DEAD) not assessed for LLS in this
pass except where noted. A durability review of the 79 admitted tactics is owed
before any of them enters the skill build.

═══════════════════════════════════════════════════════════════
END OF STATUS TRACKER
═══════════════════════════════════════════════════════════════
