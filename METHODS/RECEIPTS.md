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

- 2026-08-10 · DCI · PERFORMANCE · Xcel blower-door claim corrected to the
  NACH50 metric (was a vaguer "air leakage" framing) and re-cited to EFI,
  Xcel's rebate fulfillment administrator — the requirement lives there,
  not on Xcel's consumer page. Sharpened across 11 pages. Renter-eligibility
  FAQ reversed in the same pass: Xcel's program does cover rental
  properties (previously shipped as "Xcel is silent on this"). · repo /
  commit 40d2571

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
  pages' rebate bullet sharpened with the NACH50 metric. · repo / commit
  40b7245

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
- Rob lead dispositions — did any DCI lead close? Ticket size? That's the
  highest-value REVENUE receipt available right now (proves the lead → job
  → money chain, not just lead generation).
- Porter / Don's Garage — revenue terms, go-live date, any usage metrics.

═══════════════════════════════════════════════════════════════
END OF RECEIPTS LEDGER
═══════════════════════════════════════════════════════════════
