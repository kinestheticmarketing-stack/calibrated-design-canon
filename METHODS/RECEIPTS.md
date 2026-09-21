# RECEIPTS.md

*A method-level specification under [Calibrated Vibe Coding](../CVC.md).*
*Source-of-truth ledger of measurable outcomes across all Calibrated Stack projects — numbers, not narrative.*

═══════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════

A portfolio says "I built this." A receipt says "here is what it did."

This document is the single source of truth for every measurable outcome
the Calibrated Stack has produced. It exists because outcomes accrue
faster than they get recorded, and an unrecorded number is a lost asset.

Receipts feed three things at once:
  1. Case studies for the done-for-you funnel service (proof, not promises)
  2. Positioning — the /about-class credibility that converts
  3. Exit valuation — a business with documented outcomes sells; a founder's
     story does not.

Every receipt logged here compounds into all three.

═══════════════════════════════════════════════════════════════
THE RECEIPT LADDER (log every rung, know which rung you're on)
═══════════════════════════════════════════════════════════════

CAPABILITY   — "I built X solo with AI." True, but everyone claims it.
PERFORMANCE  — "X ranks / is cited / was built in N days." Proof the
               method works technically.
REVENUE      — "X produced N leads / $N/month / closed $N." Proof the
               method produces business outcomes and income.

Revenue receipts are worth the most and are the easiest to lose. Capture
them the moment they surface.

═══════════════════════════════════════════════════════════════
CAPTURE DISCIPLINE (this is a paperwork-close line item)
═══════════════════════════════════════════════════════════════

The receipts log is not a separate ritual. It closes with the rest of the
paperwork — alongside STATE_OF_PROJECT updates, canon pushes, and lessons.

At every SESSION-CLOSE, ask:
  "Did any receipt-worthy number surface this session?"
    - A build completed → log time-to-build (CAPABILITY/PERFORMANCE)
    - A citation count, ranking, or metric → log it (PERFORMANCE)
    - A lead, rent check, close, or ticket size → log it (REVENUE)

If yes, add the row before the session closes. A number reconstructed
later from chat history is a number half-lost.

Rules:
  - Real numbers only. No projections in the ledger body — projections
    live in the PROJECTIONS section, clearly separated, and graduate into
    the ledger when they become real.
  - Every receipt gets a date and a source (which property, which tool,
    which dashboard the number came from).
  - Never inflate. A receipt's whole value is that it's true. An
    overstated receipt is worse than none.

═══════════════════════════════════════════════════════════════
LEDGER — VERIFIED RECEIPTS
═══════════════════════════════════════════════════════════════

Format: [DATE] · [ASSET] · [RUNG] · [RECEIPT] · [SOURCE]

───────────────────────────────────────────────────────────────
DCI — denvercoloradoinsulation.com (flagship, only revenue asset)
───────────────────────────────────────────────────────────────

- ~2026-06 · DCI · CAPABILITY · Built solo with AI from partial state to
  30-page production property with full SEO/GEO infrastructure, 6-calc
  tool suite. · build record

- 2026-08 · DCI · PERFORMANCE · Grown to 59 pages live via SEO harvest
  waves. · repo / STATE_OF_PROJECT

- 2026-08 · DCI · PERFORMANCE · 11 AI citations on Bing AI Performance
  tracker. Distribution: 5 attic cost calculator, 4 R-value calculator,
  2 blown-in hub. Engines cite the TOOLS — validates the citable-source
  design bet. · Bing Webmaster Tools, AI Performance

- 2026-08 · DCI · PERFORMANCE · First-page ranking on one mainstream term
  (Google) + one mainstream term (Bing), within months of content-complete.
  · Google / Bing SERP

- 2026-08 · DCI · REVENUE · First lead produced and handed to contractor
  (Rob, Simple Home Energy Solutions), commission basis. $0 ad spend —
  pure organic + AI. [2nd lead reported by Director — confirm + log
  separately with date/source.] · lead record
  **[SUPERSEDED 2026-08-19 — now traceable to specific rows, see the
  lead-inventory entry below. This entry's "lead record" citation was
  uncitable for eleven days; it is now closed with ids and timestamps.]**

- 2026-08-19 · Portfolio (all three) · REVENUE · **Lead inventory, queried
  directly from production Postgres** (`porter-db-1`, `WHERE canary = false`),
  replacing the previously-uncitable "lead record" claim above with row ids
  and dates. **DCI — 8 non-canary rows, of which 3 are genuine third-party
  submissions:** id 5 Shaylin Muhonen, 2026-07-25, from
  `/insulation-westminster.html`; id 6 Jason Podolnick, 2026-08-05, from
  `/insulation-removal.html`; id 8 "Jason", 2026-08-08, from
  `/vermiculite-insulation-denver.html` — **all three `delivered = true`.**
  The remaining five are internal: ids 1-2 launch tests (2026-05-05), ids 3,
  4, 7 operator submissions. **DCI id 1 is `delivered = false` — a
  pre-SendGrid test row, not a delivery failure**; id 2 the same day is
  `delivered = true`, which dates SendGrid being wired between the two.
  **GCI — 3 non-canary rows, 1 third-party:** id 3 "Pranab", 2026-08-08, from
  `/` — the templated-pitch spam that triggered the Lead 3 hardening, external
  and non-test but not a customer. ids 1-2 are operator submissions.
  **LGM — 0 non-canary rows. No human has ever submitted that form.** ·
  production DB query, all three databases

- 2026-08-19 · Portfolio (all three) · PERFORMANCE · Browser-path canary
  shipped (`ops/browser_canary.js`, `browser-canary.timer`, weekly Mon 10:30
  America/Denver), closing the gap the same day's canary-validity audit
  named: the daily canary POSTs from Node and cannot prove the form renders or
  the client JS runs. Drives real headless Chrome against each live page,
  asserts the thank-you state, then **independently re-queries Postgres —
  because three backend branches silently discard a lead while still
  answering `{success:true}`**. Proven by three deliberate breakages, each
  confirmed to fire, none touching a live property; the DB-verification proof
  is the load-bearing one — the DOM showed success and the canary refused to
  pass. First clean run green on all three: DCI ids 22/23, GCI 16/17, **LGM
  9/10 — the first time Longmont's form has ever been shown to work end to
  end.** · repo `ops/browser_canary.js`, journald `browser-canary.service`

- 2026-08-10 · DCI · PERFORMANCE · Xcel blower-door claim corrected to the
  ~~NACH50~~ **"20% Reduction in CFM 50"** metric (was a vaguer "air leakage" framing) and re-cited to EFI,
  Xcel's rebate fulfillment administrator — the requirement lives there,
  not on Xcel's consumer page. Sharpened across 11 pages. Renter-eligibility
  FAQ reversed in the same pass: Xcel's program does cover rental
  properties (previously shipped as "Xcel is silent on this"). · repo /
  commit 40d2571
  **[CORRECTED 2026-09-02 — "NACH50" was never a real Xcel metric; there is
  no such standard and the string "NACH" appears nowhere in Xcel's source
  documentation. Xcel's actual first-party figure is "20% Reduction in CFM
  50." First caught at the `METHODS/PROPERTY_GENESIS.md` surface (commit
  `5265f69`); this receipt and the one below were two of the three
  remaining false-metric surfaces (the third, `RETROSPECTIVES/
  2026-08-10-citation-integrity.md`, was corrected 2026-09-02 by a prior
  pass this same day). This correction does not change what the
  underlying fix accomplished — the sourcing and page-sharpening work
  described above is real and unaffected; only the metric's name was
  wrong.]**

- 2026-08-10 · DCI · PERFORMANCE · Cellulose settling claim (10-20%)
  re-sourced from a DOE page deleted in DOE's ~2026-07-03 mass removal to
  the Building America Solution Center (PNNL, DOE contract
  DE-AC05-076RL01830) — found TRUE, not false as first suspected. ~23 prose
  instances corrected. Insulation ROI claim re-sourced from the same
  deleted page to ENERGY STAR's own page (15% national average). One DOE
  claim and one BPI claim cut as unsourceable; a third BPI claim
  de-attributed and retained as the site's own operational
  characterization, not a citation. · repo / commit 40b7245

- 2026-08-10 · DCI · PERFORMANCE · LevelUp Insulation Co. removed from the
  best-companies roundup (domain now redirects to a different business) —
  count corrected 9→8 across meta tags, JSON-LD, and body copy. Seven
  pages backfilled to hold the 2-citation floor (six suburb pages plus one
  page discovered mid-wave carrying two simultaneous cuts at once). 23
  pages' rebate bullet sharpened with the ~~NACH50~~ **"20% Reduction in
  CFM 50"** metric. · repo / commit 40b7245
  **[CORRECTED 2026-09-02 — see the correction note on the "Xcel
  blower-door claim corrected" entry above (same date, same commit wave):
  "NACH50" was never a real Xcel metric; the real figure is "20%
  Reduction in CFM 50."]**

- 2026-08-10 · DCI · PERFORMANCE · Citation rendering template fixed: a
  hardcoded "the " before every source name (wrong for brand names like
  ENERGY STAR) replaced with a required per-key determiner field — missing
  the field now fails generation loudly instead of silently defaulting.
  6 of 20 keys changed, 61 of 162 rendered citation sentences. · repo /
  commit 340a9a5

- 2026-08-10 · DCI · PERFORMANCE · ROI calculator (waste-multiplier)
  re-anchored from the retired DOE 10-20% range to ENERGY STAR's Climate
  Zone 5 figure (16% — Denver's actual zone, not the sitewide 15% national
  average). The calculator's spread declared as house-to-house modeling
  variance in rendered copy, never left to impersonate source variance. ·
  repo / commit 90efa47

- 2026-08-10 · DCI · PERFORMANCE · robots.txt converted from a hand-placed
  file (untouched since the initial commit) to generator-emitted, gaining
  three AI-crawler allow blocks it lacked — OAI-SearchBot, Claude-Web,
  Applebot-Extended — with zero existing directives removed (diff-verified
  line by line). llms.txt created and generator-emitted: 56 URLs, every
  one link-checked live, zero 404s. · repo / commit 9595987

- 2026-08-10 · DCI · PERFORMANCE · Dead ENERGY STAR citation
  (`ENERGYSTAR_R49_R60`, `.../methodology/recommended_levels`, live 404)
  swapped to a working replacement URL stating the same Climate Zone 5
  R-49/R-60 figures, verified live post-deploy — 19 rendered pages, zero
  remaining occurrences of the dead URL sitewide. Same key, same swap
  applied to Greeley (shared `CITED_SOURCES` render). · repo / commit
  e8d0e0a, deployed and live-verified same session

- 2026-08-10 · DCI · PERFORMANCE · Audit-document accuracy correction:
  eight verdict lines across VAHE_ALIGNMENT_AUDIT.md and
  FLOATE_ALIGNMENT_AUDIT.md described tactics (PTE-47, PTE-40/51, PCO-03,
  PCO-13, PTA-27, PAR-22, PAR-44, PAR-50) as open when the fixes had
  already shipped to `main` weeks earlier. `vahe-batch-2` re-verified
  fully merged (`git log main..vahe-batch-2` empty) — it was a stale
  branch *label* on already-merged work, never an unmerged branch. A
  downstream audit that read the stale lines had concluded DCI was behind
  its own Greeley clone; it was not — see the GCI entry below for the
  matching correction on that side. Same wave, PCO-13 title-length
  re-measured with HTML entities decoded: **zero** DCI pages exceed 60
  characters sitewide (63 pages checked), correcting a 2026-08-10 interim
  check that had flagged 4 pages (62/62/61/64 raw-byte counts, where
  `&amp;` counted as 5 characters instead of the 1 it renders as) — a
  measurement artifact, not a regression. · repo / commit e8d0e0a

- 2026-08-11 · DCI · PERFORMANCE · AI citations risen 11 → 16. Top cited
  pages: attic-insulation-cost-calculator.html 5, r-value-needed-
  calculator.html 4, xcel-rebate-eligibility-checker.html 3,
  insulation-wall.html 2, insulation-blown-in.html 2. Three calculators
  account for 12 of the 16 citations — 75% — with prose service pages
  accounting for the remainder: tools are the dominant citation surface
  on this property. · Director-supplied, 2026-08-11, from a search
  console or analytics surface — the specific surface, measurement
  method, engine(s) counted, and date range are NOT recorded here and
  are unknown from what was supplied. PROVENANCE NOTE: the prior
  11-citation figure above carries a recorded source (Bing Webmaster
  Tools, AI Performance tracker); this 16 figure carries no equivalent
  record. Comparability between 11 and 16 is **UNVERIFIED** — this may
  or may not be the same measurement method, engine, or date range as
  the prior figure.

  Observation (interpretation, not measurement — kept distinct from the
  receipt above): the three cited calculators are the cost calculator,
  the R-value calculator, and the Xcel rebate checker. The cost
  calculator (attic-insulation-cost-calculator.html) was recalibrated
  the day before this figure was supplied — commit 90efa47 (2026-08-10,
  ROI/waste-multiplier re-anchor to ENERGY STAR Climate Zone 5) and its
  same-day addendum commit 5b437d1 — maintenance on the property's
  single most-cited asset, though that connection was not known at the
  time the recalibration was made. Of DCI's six calculators
  (attic-insulation-cost-calculator, r-value-needed-calculator,
  xcel-rebate-eligibility-checker, do-i-need-new-insulation-quiz,
  energy-savings-payback-calculator, spray-foam-vs-blown-in-comparator —
  per `_generate_calculator_pages.py`), three do not appear in the top
  five: do-i-need-new-insulation-quiz.html,
  energy-savings-payback-calculator.html,
  spray-foam-vs-blown-in-comparator.html. [Kickoff framing assumed two
  uncited calculators; repo verification finds three — the top five
  contains two prose service pages, not four calculators, so only 3 of
  DCI's 6 calculators land in it.] Citation is not uniform across
  tools. OPEN QUESTION (not a recommendation — one measurement is not a
  trend): whether calculator depth belongs alongside service-page depth
  in a future portfolio improvements pass.

───────────────────────────────────────────────────────────────
GCI — greeleycoloradoinsulation.com (corridor property #2)
───────────────────────────────────────────────────────────────

- 2026-08 · GCI · PERFORMANCE · **Clone speed: the ~2-month DCI build
  reproduced in ~2–3 days.** ~20x+ velocity gain on a proven template.
  The single strongest AI-build receipt in the portfolio. · build record

- 2026-08 · GCI · CAPABILITY · Full property launched: 39 files, own VPS
  (port 3005), own primary-source-verified rebate landscape (Atmos 75% up
  to $1,550 attic — a stronger rebate story than DCI's Xcel base). Clone
  re-verifies facts per market, not a dumb copy. · repo / commit e2ec524

- 2026-08-10 · GCI · PERFORMANCE · Same citation-remediation pass as DCI:
  ROI claim re-sourced to ENERGY STAR (15%), cellulose settling re-sourced
  to BASC, ~10 prose instances corrected. One DOE claim and one BPI claim
  cut as unsourceable; one further BPI claim de-attributed. Own IndexNow
  key, key file, and submit script built (mechanism only — commit message
  states not yet submitted as of this commit). · repo / commit 9b9e7e2

- 2026-08-10 · GCI · PERFORMANCE · Citation rendering template fixed, same
  rule as DCI, COPY_VOICE.md documentation byte-identical to the control
  property's. 7 of 23 keys changed, 37 of 90 rendered citation sentences. ·
  repo / commit 03ae395

- 2026-08-10 · GCI · PERFORMANCE · Payback calculator (CEILING_SHARE)
  re-anchored to ENERGY STAR's Climate Zone 5 figure (16%), same rule and
  same declared-variance treatment as DCI's calculator. · repo / commit
  b5cdca2

- 2026-08-10 · GCI · PERFORMANCE · llms.txt created and generator-emitted:
  27 URLs, every one link-checked live, zero 404s. · repo / commit e13a438

- ~~2026-08-10 · GCI · PERFORMANCE · First-ever IndexNow submission for
  this property: 1 URL (the payback calculator page), HTTP 200 — the
  mechanism built earlier the same day (commit 9b9e7e2, above) had shipped
  unused; this is its first real call. · repo / commit e13a438 + live
  submission, this session~~ — **CORRECTED 2026-08-10: this receipt does
  not hold up and is retracted.** Commit e13a438's own message covers only
  the llms.txt/sitemap wave and makes no mention of an IndexNow call.
  Greeley's STATE_OF_PROJECT.md recorded the mechanism as "not yet
  deployed or submitted" from the moment it was built (commit 9b9e7e2) and
  was never updated to say otherwise. The next wave to touch this gap
  (commit 69b56d5, same property) states plainly: "confirmed live via
  direct GET, HTTP 200, content matches. Closed, **no submission made**."
  No corroborating evidence of a prior submission exists anywhere in the
  record — not in either commit message, not in STATE_OF_PROJECT.md, not
  on the VPS. The real first submission is recorded below.

- 2026-08-10 · GCI · PERFORMANCE · Greeley's first three SEO-corpus
  alignment audits written and committed: Allsopp SB3 (9 modules),
  Arabian Publisher SEO (7 modules / 240 tactic IDs), Floate Parasite (15
  ADMIT tactics; the 39 BLOCKED tactics excluded per the corpus gate).
  Five-verdict vocabulary used, including an APPLIED-UNTRACKED verdict
  this property needed that the control property's own audits never
  used. Found and recorded (not fixed, outside that wave's boundary): a
  duplicate `<title>` defect — homepage and the primary money page shipped
  byte-identical titles on the market's head term. · repo / commit
  cd2880e

- 2026-08-10 · GCI · PERFORMANCE · Duplicate-title defect (found by the
  audit above) fixed: homepage `<title>`/`og:title`/`twitter:title`
  changed to a distinct string (Director-approved), the primary money
  page's transactional title left unchanged. Same wave, dead ENERGY STAR
  citation swap applied here too (see the matching DCI receipt for the
  shared key) — 4 rendered Greeley pages, zero remaining occurrences of
  the dead URL. Outbound-dead-citation count re-measured fresh at the same
  time: the "7" on file since 2026-08-09 was already stale (4 of the
  original 7 had been incidentally removed from `CITED_SOURCES` by an
  unrelated wave the day the "7" was recorded) — **3 remained**, one
  swapped (above), one confirmed live with no swap needed (NOAA), one
  queued (NREL, domain DNS-dead, no replacement source found). Three
  tactics (PCO-43/44/46) re-categorized out of BLOCKED BY BUILD ORDER into
  the internal gap list — each was unilateral analysis of this property's
  own link profile, not gated on another party's cooperation, a
  platform's approval, or third-party payment, so the BLOCKED label was a
  mis-filing, not a real external gate. · repo / commit 69b56d5, deployed
  and live-verified same session

- 2026-08-10 · GCI · PERFORMANCE · **Real first-ever IndexNow
  submission for this property:** 5 URLs (the homepage plus the four
  citation-swap pages from the gap-fix wave above), HTTP 200. Supersedes
  the retracted claim above. Derived URL count verified against the
  commit diff before submission (not assumed), matched the mechanism's
  own reported count, submitted via the documented bash-array-inside-
  bash-c pattern (the unquoted form is known to collapse to one URL and
  return HTTP 400 with success-shaped output — avoided). · repo / commit
  69b56d5 + live submission, deploy session following it

───────────────────────────────────────────────────────────────
CORRIDOR — Northern Colorado (empire infrastructure)
───────────────────────────────────────────────────────────────

- 2026-08 · Corridor · CAPABILITY · All 4 corridor domains acquired +
  DNS-pointed in a single session. Build order locked:
  Greeley → Longmont → Fort Collins → Loveland. · registrar / DNS

- Strategic lesson (earned, not read): DCI proved the method in the
  HARDEST market (Denver — capital, largest metro, most competition) and
  still ranks + cites. The corridor deliberately targets THINNER-competition
  cities where the same machine ranks FASTER. Win-anywhere proof + pick-your-
  battles deployment.

- 2026-08-11/12 · Longmont · CAPABILITY · Third corridor property built and
  launched from the unified genesis checklist rather than contributing to
  it — genesis (2026-08-11 08:55) to live VPS (2026-08-12 09:03) in one
  calendar day. 47 pages live (46 at launch, 47 after the hybrid-insulation
  page shipped same day). SendGrid domain authentication verified with its
  own restricted key (`s1._domainkey`/`s2._domainkey`/`em2787` resolving);
  `CANARY_SECRET` wired and a real end-to-end send proven (`sendgrid_result:
  accepted HTTP 202`, `leads` row `canary=t delivered=t`, `lead-canary.timer`
  active); its database (`longmont_insulation`) confirmed inside the shared
  cluster's dynamic nightly-backup discovery. **Not done, despite an earlier
  report claiming otherwise: Search Console and Bing Webmaster properties
  are NOT registered** — deliberately deferred (STATE_OF_PROJECT.md), a DNS
  TXT verification record exists but its GSC status is unconfirmed. IndexNow:
  first attempt self-halted pre-submission (phantom `insulation-rebate-hub`
  sitemap entry, live 404); once removed, 45 URLs submitted, HTTP 202. ·
  repo / commits `f9b5fc2`..`f6892f43`

- 2026-08-12 · Longmont · PERFORMANCE · First property audited against four
  SEO/GEO corpora rather than three — Allsopp (9 modules), Vahe (7 modules /
  240 tactics), Floate (15 ADMIT tactics), and Zarr (50 tactics, first use
  of this corpus anywhere in the portfolio) — 81 verdicts total (9+7+15+50,
  re-counted from the four audit tables, not carried from any summary).
  Read-only: no `public/` file, generator, or rendered string changed.
  [A prior report characterized this as "Zarr surfaced 19 findings the
  other three corpora did not" — no such count appears in any of the four
  audit documents; not carried forward as a receipt. What Zarr's own
  verdict table does state: 1 APPLIED-TRACKED, 14 APPLIED-UNTRACKED, 14
  NOT-APPLIED, 3 NOT-APPLICABLE, 18 BLOCKED BY BUILD ORDER, of 50.] · repo /
  commit `d5c40db`

- 2026-08-12 · Longmont · PERFORMANCE · regen_all.sh corrected: five
  generators the header claimed were "deliberately not ported" had actually
  been built during the 2026-08-11 content wave and stayed commented out,
  so the script silently regenerated only 12 of 46 pages. Uncommented;
  verified exit 0, 46 pages, deterministic across two runs, byte-identical
  to deployed state. One generator (`_generate_rebate_hub.py`) remains
  correctly absent — it needs a two-utility rebate architecture never
  designed, and the header now says so accurately instead of lumping it
  with the five that were simply forgotten. · repo / commit `4989baef`

- 2026-08-12 · Longmont · PERFORMANCE · Sitemap phantom-URL defect found
  and fixed: `_generate_sitemap.py` hardcoded an entry for
  `insulation-rebate-hub.html`, a page that was never built, returning a
  live 404. Caught pre-submission by the property's own IndexNow
  verification step, which halted rather than submitted. [A later commit
  message on the same fix claimed the dead URL "was submitted to Google
  and Bing before discovery" — the repo's own record contradicts this: the
  HALT commit states plainly "No IndexNow submission was made," and no
  earlier submission of any kind is recorded anywhere in this property's
  history. Not carried forward as a receipt; whether Google or Bing
  organically crawled the live sitemap before the fix is unknown and
  unverifiable from this repo.] Sitemap now lists 45 URLs, all resolving.
  · repo / commits `e62a1ec`, `0ab8ae2`

- 2026-08-12 · Longmont · PERFORMANCE · dateModified added to three JSON-LD
  schema functions (`speakable_schema`, `jsonld_faqpage`, `jsonld_howto`)
  that previously only `jsonld_article` carried; every generator now passes
  the property's `REVIEWED_ISO`, educational pages keep their own per-page
  dates. Coverage went from 6/46 to 42/46 pages (later 43/47 once the
  hybrid page shipped with it from creation). Back-ported same-day to DCI
  (27→59/63) and Greeley (6→30/34) using the identical function-level
  pattern. · repo / commits `56c232a` (Longmont), `82471b5` (DCI),
  `e221bea` (Greeley)

- 2026-08-12 · Portfolio (all three) · CAPABILITY · First-party pageview
  counter shipped identically on DCI, Greeley, and Longmont — a byte-
  identical beacon (verified by sha256 of the rendered `<script>` block)
  posts path + timestamp only to each property's own `/pv` endpoint; no
  IP, cookie, or identifier stored; three-layer bot filtering (JS-required,
  a discarded-not-stored UA check, a boot-built path allowlist). Recording
  shipped with a kill switch defaulted OFF specifically because the
  mechanism reached production (~13:02–13:08) before the privacy-policy
  disclosure that describes it did — a real ordering defect, self-caught
  and self-corrected before any real visitor was recorded (each property's
  table held exactly one synthetic test row at the time). Recording enabled
  only after each property's live privacy page was verified to no longer
  claim "no analytics." All three properties' privacy/about pages revised
  in the same wave to disclose the count plainly, without overclaiming in
  either direction. · repo / commits `36db29f`+`4830e0c`+`de1e444` (Longmont),
  `82471b5`+`b78ae27`+`e2f7fa6` (DCI), `e221bea`+`77ab453`+`3655e4b` (Greeley)

- 2026-08-12 · Longmont · CAPABILITY · Hybrid Insulation (Flash and Batt)
  service page — page 21, the property's first service page addressing a
  technique absent from all three properties' service and educational
  content. The page's central claim is a scoped code condition, not a
  blanket figure: IRC Table R702.7.1 (reproduced verbatim by the Building
  America Solution Center, PNNL/DOE contract DE-AC05-076RL01830 — same
  source class as `BASC_CELLULOSE_SETTLE`) permits a Class III vapor
  retarder in Climate Zone 5 only where continuous insulation reaches R-7.5
  over a 2x6 wall; the 1-inch flash the technique is named for falls short
  of that on the Class III path specifically, and the page states that
  condition rather than a bare "1 inch is below code." No rebate applies —
  Xcel excludes new construction, Efficiency Works requires the home be
  ≥1 year old — stated on the page rather than omitted. Four attempts to
  reach this: two large multi-phase kickoffs produced nothing verifiable
  on disk; a data-entry-only task with pasted verification output produced
  the committed page. · repo / commits `1b98143d`, `f6892f43`

  [NOTE ON EVIDENCE: two prior reports this session described this page as
  already sourced, committed, and shipped before either was true — one
  attributed a fabricated R-value and a fabricated finding to a source
  that had never actually been checked. Recorded here only after the
  commit and its cited source were independently re-verified against the
  live repo and a fetched primary source, not from either report.]

- 2026-08-17 · Portfolio (all three) · PERFORMANCE · Full-roster content
  audit across DCI, Greeley, and Longmont: 151 of 151 pages audited, twelve
  dimensions each, 518 findings (304 mechanical, 214 judgment). All 304
  mechanical findings applied, across four remediation waves. 100 distinct
  carry-forward items triaged into 15 classes: 11 settled by existing
  precedent, 14 escalated — all resolved. Five validators installed in
  `_postbuild_check.py` (check_interactive_js, check_placeholders,
  check_duplicate_labels, check_credentials, check_jsonld), every one
  canary-proven; one canary exposed a real bug in its own check. DCI service
  pages grown 8 → 18; Longmont's
  COPY_VOICE.md authored where none existed, with four dangling references
  resolved; Greeley's Atmos rebate claims narrowed to confirmed towns.
  Deployed and pushed on all three properties, each verified live. · repo /
  commits DCI `c144ad8`, LGM `795c2ef`, GCI `5b8b4cb`

- 2026-08-17 · Portfolio (all three) · PERFORMANCE · External validation on
  file: DCI 68 of 73 pages indexed, impressions roughly doubled May to
  August; Longmont 43 of 46 pages indexed five days after launch. · Search
  Console [surface and exact date range as supplied — not independently
  re-verified in this pass]

───────────────────────────────────────────────────────────────
PORTER — talktoporter.com (platform)
───────────────────────────────────────────────────────────────

- 2026-07 · Porter · CAPABILITY · Multi-tenant AI receptionist + CRM built
  solo: FastAPI/Python 3.12, Postgres 16, Docker Compose, full voice
  pipeline (Vapi/Deepgram/ElevenLabs/Twilio). · repo ~/code/porter

- 2026-07 · Porter · PERFORMANCE · Shipped complete multi-tenant refactor
  arc (MT.1→MT.2→MT.3): host-header tenant routing, genericized brain via
  templated substitution (byte-equality proof across pipelines), 4 tenants
  stood up as config-only proofs, nightly offsite backup (Backblaze B2,
  tested restore), self-owned error monitoring. Senior-engineer-grade
  infra, one person + AI. · repo / audit record

- 2026-08-09 · Porter · PERFORMANCE · VPS backup hardening: absorbed the
  host Postgres cluster into the backup regime, protecting two previously
  unprotected databases (`totefinders`, `kinestheticmarketing_com`) —
  read-only role, write-denied at grant level, TCP-connected per pg_hba.conf.
  Added a dead-man checker (`backup_heartbeat_check.sh`, systemd
  `backup-heartbeat-check.timer`, deliberately a different scheduler from
  cron so a dead cron daemon can't silence it). · repo ~/code/porter /
  commit 2ca638e

- Porter · REVENUE · Has a real external client (Don's Garage Automotive
  and Transmission, founded 1970, owner Garrett). [Log revenue terms when
  confirmed.]

───────────────────────────────────────────────────────────────
METHODOLOGY — The Calibrated Stack (meta-receipt)
───────────────────────────────────────────────────────────────

- 2026 · Calibrated Stack · CAPABILITY · A four-role AI development system
  (Director/Architect/Executor/Auditor) — built, used daily across the
  whole portfolio, AND productized for sale ($47, Gumroad). Not just using
  AI: built a repeatable governance system for it and sells it. · Gumroad

═══════════════════════════════════════════════════════════════
VERIFICATION RECEIPTS — defects our checks caught, and missed
═══════════════════════════════════════════════════════════════

What this records: every false claim, fabricated figure, or silent
failure the Calibrated Stack's own instruments caught — and every one
they missed until later. Our numbers only. No comparative claims about
anyone else's process belong in this section.

Why the misses stay in: a verification record that only lists catches
is a marketing claim. The POST-LIVE rows are what make the PRE-LIVE
rows believable, and each one produced a method rule in canon.

Format: [DATE] · [ASSET] · [CAUGHT: PRE-LIVE | POST-LIVE] · [WHAT] ·
[HOW CAUGHT] · [RULE IT PRODUCED, if any] · [SOURCE]

- 2026-07-12 · Porter · PRE-LIVE · A demonstration test captured an
  alert-email body verbatim for a worst-case error and found request-derived
  PII (a fake phone number) leaking into it, uncaught by prior review. No
  email send in this wave was ever unmocked. · Caught by a purpose-built
  PII-capture test. · Produced the Director's SCRUB ruling: alert emails
  now carry only fixed structured fields (exception_type, route, method,
  tenant_id, occurrence_count, first_seen, last_seen, distinct-error
  count) — no message text or traceback, ever. · commits `d156bfb`
  (test), `def5825` (fix)

- 2026-07-12 · Porter · PRE-LIVE · A malformed `?limit=abc` query param on
  `/internal/errors` returned 422 before the auth check ran (typed-param
  validation runs before route body/auth in the framework), revealing the
  endpoint's existence and undermining its intended 404-invisible-auth
  design. · Caught by a pre-push audit probe ("Auditor Flag 1"). ·
  Produced: limit/fingerprint parameters made untyped so auth always runs
  first, plus a permanent regression test covering all four probed
  malformed-param cases. · commit `1eae0a9`

- 2026-07-13 · Porter · POST-LIVE · A bot hit `/openapi.json` in
  production and crashed schema generation; root cause was 28 routes
  across 12 files registered with `response_class=None`. A working schema
  would have published the full route map, including `/internal/errors`
  and its auth header name, negating the prior 404-invisibility fix. ·
  First production catch by the MT.1 error catcher, which recorded the
  crash. · Produced: `openapi_url`/`docs_url`/`redoc_url` disabled
  permanently; the 28 occurrences documented as a required prerequisite
  before docs can ever be re-enabled. · commit `fabeb1c`; DECISIONS.md
  lines 58-66

- 2026-07-13 · Porter · POST-LIVE · Three real, unmocked email sends
  occurred across the MT.1 arc (exact: two in MT.1, one in MT.1.3's
  diagnostic) because a live Resend key in dev turned every forgotten
  mock into a real send. · Not caught by an automated gate — noticed on
  review, after the fact. · Produced the `PORTER_SEND_EMAILS` kill switch
  (true only in production; suppressed sends log loudly) and closed one
  bypass where the password-reset flow called the Resend client directly
  instead of through the gated helper. · DECISIONS.md lines 68-74;
  commit `b06ae13`

- 2026-08-11 · GCI · PRE-LIVE · A receipt claimed "first-ever IndexNow
  submission for this property," citing a commit that never mentions
  IndexNow; Greeley's STATE_OF_PROJECT.md recorded the mechanism as "not
  yet deployed or submitted" the whole time. The false claim was doc-only
  and was never repeated as an external submission. · Caught on review
  before being repeated further; retracted in place (struck through, not
  deleted) and replaced with the real first submission (5 URLs, HTTP
  200). · commit `cae5351`; RECEIPTS.md lines 286-295

- 2026-08-12 · DCI + Longmont + Greeley · POST-LIVE · Pageview-recording
  code reached production roughly 100 minutes before the privacy-policy
  disclosure describing it shipped, on all three properties. · Self-caught
  same day; the recording kill switch defaulted OFF, so no real visitor
  row was captured in that window (each property's table held exactly one
  synthetic test row at the time). · Produced the rule: a
  disclosure-bearing policy change ships before, or with, the behavior it
  discloses, never after. · commits `36db29f`+`4830e0c`+`de1e444` (LGM),
  `82471b5`+`b78ae27`+`e2f7fa6` (DCI), `e221bea`+`77ab453`+`3655e4b`
  (GCI); RECEIPTS.md lines 420-435

- 2026-08-12 · Longmont · PRE-LIVE · `_generate_sitemap.py` hardcoded a
  sitemap entry for `insulation-rebate-hub.html`, a page that was never
  built — a live 404. · Caught by the property's own IndexNow
  verification step, which halted rather than submitted. No IndexNow
  submission was made. · Sitemap corrected to 45 URLs, all resolving. ·
  commits `e62a1ec`, `0ab8ae2`; RECEIPTS.md lines 396-408

- 2026-08-12 · Longmont · PRE-LIVE · A later commit message on the same
  fix claimed the dead URL "was submitted to Google and Bing before
  discovery" — the repo's own record contradicts this; the halt commit
  states plainly "No IndexNow submission was made." · The claim was
  checked against the repo's own history and refused; it was never
  carried forward as a receipt. · commits `e62a1ec`, `0ab8ae2`;
  RECEIPTS.md lines 400-406

- 2026-08-12 · Canon (internal report) · PRE-LIVE · A prior report
  characterized an audit as "Zarr surfaced 19 findings the other three
  corpora did not" — no such count appears in any of the four audit
  documents. The audit's actual table: 1 APPLIED-TRACKED, 14
  APPLIED-UNTRACKED, 14 NOT-APPLIED, 3 NOT-APPLICABLE, 18 BLOCKED BY BUILD
  ORDER, of 50. · Caught on review against the source documents before
  being recorded as fact; not carried forward as a receipt. · commit
  `d5c40db`; RECEIPTS.md lines 373-384

- 2026-08-12 · DCI · PRE-LIVE · Two prior reports in the same session
  described a hybrid-insulation page's R-value citation as already
  sourced, committed, and shipped before either was true — one attributed
  a fabricated R-value and a fabricated finding to a source that had
  never actually been checked. · Caught by independently re-verifying the
  commit and its cited source against the live repo and a fetched primary
  source before logging anything as fact. · commits `1b98143d`,
  `f6892f43`; RECEIPTS.md lines 437-459

- 2026-08-17 · Greeley · POST-LIVE · Three calculators shipped live with
  no JavaScript at all, while regen exit code, two-run determinism, and
  MD5 manifest all stayed green — none of those checks verified that the
  artifact functioned, only that it was written. · Caught by a dedicated
  audit pass, the same pass that also found a credential validator whose
  canary never fired (an exempted match broke out of both loops) and a
  citation-label guard, canary-proven in a prior wave, dead behind a
  premature return the canary never exercised. · Produced Pattern 14: "a
  validator is not installed until shown to fire in the real execution
  path." · commit `d51c71c`; ground-truth.md line 41

- 2026-08-19 · Canon (RECEIPTS.md itself) · POST-LIVE · RECEIPTS.md stood
  published stating `_postbuild_check.py` runs six validators; all three
  property repos contain exactly five (`check_interactive_js`,
  `check_placeholders`, `check_duplicate_labels`, `check_credentials`,
  `check_jsonld`). The figure came from a kickoff and was transcribed
  without anyone opening the file. · Caught when the figure was checked
  directly against the code instead of taken on trust. · Produced the
  standing rule: "a figure asserted in a kickoff is not a verified
  figure." · commit `66b6336` (correction); ground-truth.md lines 14-21

- 2026-08-19 · Portfolio (DCI/GCI/LGM lead-capture forms) · PRE-LIVE · A
  browser canary re-queries Postgres rather than trusting the
  thank-you-page state, because three backend branches were shown able to
  silently discard a lead while still answering success. · Proven via
  three deliberate breakages in testing (not a live incident) — the DOM
  showed success and the canary refused to pass in all three; first clean
  run green on all three properties (DCI ids 22/23, GCI 16/17, LGM 9/10,
  including the first time Longmont's form was shown to work end to end).
  · commit `66b6336`

- 2026-08-20 · Greeley + DCI · POST-LIVE · A citation-scoring instrument
  issued verdicts (LLS-13, LLS-41, LLS-90, part of LLS-86) on surfaces it
  had never actually examined. One of its false-clean verdicts let a dead
  external citation (nrel.gov, DNS-dead) stay live on 2 DCI pages after
  the instrument reported it already gone. · Caught by an adjudication
  pass that re-checked the instrument's own coverage. Verdicts were
  retracted, not downgraded: "a verdict from a blind instrument is not a
  weaker verdict, it is not a verdict." · commit `53ec527`

- 2026-08-21 · DCI + Longmont · POST-LIVE · A needle-scoped removal check
  (`grep` for the exact phrase `$400 for air sealing`) reported the false
  figure gone while the same figure survived live in different phrasing
  on `xcel-insulation-rebate-guide-denver.html` — live through every
  prior gate, surviving six Auditor gates before catch. A related $500
  figure was live in production on LGM (quick-facts and calculator
  output) until this pass. · Caught by deriving the check from the target
  concept instead of reusing the edit's own matcher. · Produced the rule:
  a verification instrument must be constructed independently of the edit
  instrument. · docs/board/done/xcel-cap-figures-all-unsourced.md,
  docs/board/done/removed-cap-reasoning-passages.md; PROPERTY_GENESIS.md

- 2026-08-23 · Longmont · POST-LIVE · The Xcel/Longmont Power stacking
  rule was misrecorded as an outright "never stack" prohibition,
  producing false denial language on live pages — exactly 100 affirmative
  stacking-denial instances (92 occurrences across 46 pages in
  `_shared_components.py` alone, plus more in `_area_pages.py` and
  `_service_pages.py`). · Caught on audit and corrected to the rule's
  actual evidentiary form. · Produced the corrected stacking rule now
  recorded in ground-truth.md. · commits `c795a35` (removal), `98142bd`
  (rule correction); docs/board/LLS_WAVE1_LGM.md lines 84, 90, 386

- 2026-08-25 · Greeley · POST-LIVE · `cite_inline()` wrapped every
  `quote=True`-flagged citation entry in verbatim quotation marks
  regardless of whether the entry actually quoted text. Comparing 6 ICC
  code sources against a sibling property's verified entries found 12 of
  21 deviating, 5 outright fabricated (words not in the source at all):
  `ENERGYSTAR_AIR_SEALING_15PCT` (7 pages), `GREELEY_DESIGN_CRITERIA` (7
  pages), `BSC_ATTIC_VENTILATION`, `BSC_AIR_LEAKAGE_MOISTURE` (3 pages),
  `ACCA_MANUAL_J` (2 pages). · Caught by a citation audit that fetched
  the actual sources live and compared them word for word. · commit
  `c0d7d27`

- 2026-08-25 · DCI · POST-LIVE · A fabricated ENERGY STAR quotation was
  live on `attic-ventilation-vs-air-sealing-denver.html`, four deviations
  from the actual source, all favoring the site's thesis. · Caught by the
  same live source-fetch audit pattern used on Greeley the same day. ·
  commit `4c782b2`

- 2026-08-25 · DCI · POST-LIVE · `normfind.py`'s body-text scan is
  structurally unable to reach `<head>`: a word-boundary defect
  ("capssealing") was live in `meta[name=description]`,
  `og:description`, `twitter:description`, and JSON-LD
  `Article.description` on `xcel-insulation-rebate-guide-denver.html` —
  the actual SERP snippet and link-preview text. · Caught by a reader
  grepping the raw file directly, not by the scanner; a whole-corpus
  sweep then confirmed the rest clean. · Recorded as a standing method
  limit. · commit `4c782b2`; ops/claim_gate/RULES_SPEC.md line 3934

- 2026-08-25 · DCI · POST-LIVE · Three additional unsourced or
  overclaiming safety statements were live in the same sweep: an
  unsourced knob-and-tube alternative product claim, an unsourced
  "neither material increases fire risk" claim, and a vermiculite
  affirmative-denial overclaim. · Caught by the same citation audit as
  the fabricated ENERGY STAR quote above. · commit `4c782b2`

- 2026-08-27 · Greeley · PRE-LIVE · A second read-agent pass re-fetched
  sources instead of trusting the first citation audit's own summary, and
  found 4 errors in that audit — including one that would have deleted a
  true citation and one that undercounted render-sites through a
  55-character-prefix bug (making "renders on 0 pages" a floor, not a
  count). · Caught before either error shipped; revised the deviation
  count from 12/21 to 14/21. · commit `fe795cc`

- 2026-08-27 · Greeley · POST-LIVE · The fix for the fabricated-quotation
  defect above (`quote=False`) was dead data: `cite_inline()` never read
  the flag, so the "corrected" IRC text still rendered wrapped in
  quotation marks the ICC never wrote — longer than the fabrication it
  replaced. Both regen gates exited 0 on it throughout. · Caught by a
  follow-up read after the fix had already shipped and gated green. ·
  Produced the direct fix: `cite_inline()` now branches on the flag. ·
  commit `9cccf4c`

- 2026-08-27 · Greeley · POST-LIVE · The corrective fix above was itself
  incomplete: adding `quote=False` without removing the false attribution
  converted a fabricated quotation into a fabricated assertion still
  carried on the City's authority. The same pass also caught a hardcoded
  town name in JSON-LD `areaServed` on 8 area pages, and an
  asbestos-trigger-year miscue (pre-1940 stated vs. EPA's actual pre-1990
  window). · Caught on the same follow-up read as the row above. ·
  commit `b11f681`

- 2026-09-19 · DCI · POST-LIVE · A calculator's JavaScript shipped with
  Python comment syntax, live and non-functional from 2026-09-18 to
  2026-09-19. Every wired check stayed green over it — `regen_all.sh`
  doesn't invoke `functional_proof.sh`, and the claim gate has no
  JS-parse rule. · Caught by `ops/functional_proof.sh` check [3/7],
  confirmed via live `curl`. Swept portfolio-wide: 1 of 75 pages
  affected. · commit `78f5a92`

SUMMARY: 24 rows · 9 PRE-LIVE · 15 POST-LIVE · computed 2026-09-21

═══════════════════════════════════════════════════════════════
PROJECTIONS (not receipts — targets awaiting real numbers)
═══════════════════════════════════════════════════════════════

These graduate into the LEDGER the moment they become real. Kept separate
so the ledger stays honest.

- Rank-and-rent base target: 5 properties × ~$2K/month = ~$10K/month,
  mostly passive. Graduates per-property as each flips from ranking →
  renting. First real rent check = first REVENUE receipt on this line.

- Corridor bundle: Northern CO (Greeley/Longmont/Fort Collins/Loveland)
  rentable as one unit to one contractor for a premium, or split across
  2–3 contractors if traffic justifies.

- Empire coverage play: every nameable CO city big enough to rank
  (Boulder, Castle Rock, Colorado Springs, Pueblo, Trinidad, Grand
  Junction, Evergreen, +more), then potentially another state. Constraint
  is no longer build time (2–3 day clone) — it's naming cities and
  knocking them out.

═══════════════════════════════════════════════════════════════
OPEN CAPTURE ITEMS (numbers known to exist — go confirm + log)
═══════════════════════════════════════════════════════════════

- DCI 2nd lead — Director reported two leads total; only first is
  detailed in record. Confirm date + source page + disposition, log it.
- 2026-09-06 · Rob lead dispositions — did any DCI lead close? Ticket size?
  That's the highest-value REVENUE receipt available right now (proves the
  lead → job → money chain, not just lead generation). **State as of
  2026-09-06: still open, nothing confirmed, no ETA.** The three genuine
  third-party DCI leads are ids 5, 6 and 8 (2026-07-25, 2026-08-05,
  2026-08-08, all `delivered = true` — see the 2026-08-19 lead-inventory
  entry above); whether any of them became a paid job, and at what ticket
  size, is on record nowhere in this portfolio. **There is no online
  retrieval path for this one** — the answer exists only with the named
  contractor (Rob, Simple Home Energy Solutions) and has to be asked for
  directly, which is why it is a capture item and not a work item. This
  line is now the sole home of the watch: the canon board card
  `lead-to-job-receipt`, which duplicated it, was deleted 2026-09-06 as a
  duplicate of this entry — deleted, not closed, and nothing about the
  underlying question was answered.
- Porter / Don's Garage — revenue terms, go-live date, any usage metrics.
- 2026-08-11 · Re-measure DCI AI citations at a defined interval — record
  the surface, engine(s), and method at time of measurement so future
  figures are comparable to each other. The 11 → 16 comparison logged
  above is currently method-unverified.
- 2026-08-11 · Measure whether Greeley's calculators attract citations —
  Greeley launched 2026-08-06 with a different calculator set. If tools
  are the dominant citation surface, Greeley should show the same
  pattern as it matures — the test of whether the DCI pattern
  generalizes or is DCI-specific.

═══════════════════════════════════════════════════════════════
END OF RECEIPTS LEDGER
═══════════════════════════════════════════════════════════════
