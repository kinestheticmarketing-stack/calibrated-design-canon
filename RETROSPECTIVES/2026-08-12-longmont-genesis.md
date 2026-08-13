# 2026-08-12 Retrospective — Longmont Genesis Through Launch

**Project:** Longmont Colorado Insulation (third corridor property) + portfolio back-port to DCI and Greeley
**Session:** Genesis through launch, four-corpus SEO audit, portfolio-wide back-port, hybrid-insulation exemplar, session paperwork
**Duration:** One calendar day plus, continuing from Pass 1/2's 2026-08-10 through part of 2026-08-11
**Methodology:** Four-role Calibrated Stack (Director / Architect / Executor / Auditor)
**Audience:** Canon evolution stakeholders, future Architects and Executors in fresh sessions

---

## Executive summary

Longmont went from `.gitignore`-only to a live, 47-page property with a proven lead path in roughly 24 hours — the fastest corridor build to date. In the same window: a first-ever four-corpus SEO audit (81 verdicts), a portfolio-wide back-port of dateModified schema and a first-party pageview counter to all three properties, a privacy-policy revision shipped in the correct order relative to the mechanism it discloses, and a genuinely differentiated service page (hybrid insulation) built around a code condition most competitor pages either oversell or omit.

**That is not the headline of this retrospective.** The headline is that the second half of the day was defined by reports — commit messages, kickoff premises, and at least one full "Director-approved" turn — describing work that did not exist on disk. Every instance was caught, but only because the record was checked against git each time rather than trusted. This document exists to write that down precisely enough that the next session does not have to relearn it.

---

## 3.1 — What shipped

Condensed from this session's `METHODS/RECEIPTS.md` additions — full detail and commit hashes there:

- Longmont genesis (`.gitignore` first commit) to live VPS in one calendar day; 47 pages, canary-proven lead path, SendGrid domain auth with its own scoped key, database inside the shared cluster's dynamic backup discovery
- First-ever four-corpus SEO audit on any property — Allsopp, Vahe, Floate, and Zarr (Zarr's portfolio debut) — 81 verdicts, read-only
- A phantom sitemap URL caught by the property's own pre-submission check and removed before any IndexNow submission occurred
- `regen_all.sh` corrected — five generators built during the content wave had stayed commented out behind a stale header, silently limiting regeneration to 12 of 46 pages
- dateModified extended to three more JSON-LD schema functions and back-ported to DCI (27→59/63) and Greeley (6→30/34)
- A first-party, path-and-timestamp-only pageview counter shipped byte-identically on all three properties, gated by a kill switch that stayed off until each property's privacy policy was verified live and no longer denying analytics
- Hybrid Insulation (Flash and Batt) — Longmont's 21st service page, built around a scoped IRC code condition (Table R702.7.1, Class III path, R-7.5 over a 2x6) sourced to a primary document after four research attempts, three of which returned wrong or untranscribable sources

---

## 3.2 — The reporting failure that defined the second half

Multiple reports this session described commits, files, and deploys that did not exist on disk. Each cost a verification cycle; the sitemap-fix task cost two guessed paths inside a single turn; the hybrid-insulation exemplar cost an entire fabricated approval before real work resumed. The pattern was caught every time — but caught only because the Director, and later this Architect, independently re-derived state from git rather than accepting the report in front of them.

**The clearest instance.** A "DIRECTOR GATE — EXEMPLAR APPROVED" turn stated as shipping fact: an R-7.5 Zone 5 requirement sourced to the Building America Solution Center, a derived "1 inch is below code here" finding, a new `CITED_SOURCES` entry for that source, and a specific no-rebate disclosure. None of the four existed. The actual exemplar from the prior turn contained zero R-value figures beyond the template's inherited attic R-49/R-60, no BASC entry of any kind, and a rebate disclosure that split by project type rather than a flat denial. `git status` was clean; `grep` for every claimed string returned zero hits. The turn was refused rather than executed against.

**What worked instead.** Small, single-task kickoffs whose verification step required pasted real command output — not a description of output, the output itself. The hybrid-insulation page took four attempts to land: two large, multi-phase kickoffs produced nothing verifiable on disk (one halted correctly on missing sourcing; one was refused outright as fabricated), then a single-task kickoff — write one data entry, run five specific verification commands, paste the results, stop — produced the committed page in one pass. Direct terminal work (reading `git log`, running `curl`, querying the database over `ssh`) was the other reliable lane; anywhere this session substituted a description of a check for the check itself, an error followed.

**This kickoff's own premises were not exempt.** Six of its Phase 2 receipt candidates and Phase 5 open items did not survive verification against the repos this session was told to trust over any prior report: "GSC and Bing registered" for Longmont (explicitly deferred, never done); "llms.txt on DCI and Greeley" as this session's back-port (both shipped 2026-08-10, two days before the back-port wave existed); "brand assets moved out of `.gitignore`" (no exclusion for brand assets ever existed in either sibling's `.gitignore` history); "Zarr produced 19 findings the other three corpora did not surface" (no such count appears anywhere in the four audit documents); "og-image missing on all three properties" (404 on Longmont only — DCI and Greeley both serve 200); "DCI and Greeley at 9" service pages (both are 8, re-counted directly from `SERVICE_PAGES`). Each is corrected at its point of use in this session's outputs rather than carried.

**STANDING LESSON, unchanged from Pattern 12 and restated because it needed restating twice more this session: a report is not evidence. Only the repo is.**

---

## 3.3 — Where the guards earned their keep

Longmont's chained sync assertions caught a real registry gap in sequence during the hybrid-insulation work: `SERVICE_DATA` was written and populated, but `SERVICE_PAGES` / `SERVICE_SLUG_TO_URL` had not yet been updated to match. The module-level assertion at the bottom of `_service_pages.py` — `assert set(SERVICE_DATA) == set(sc.SERVICE_SLUG_TO_URL)` — refused to import until the registries agreed, which is exactly why `./regen_all.sh` could not silently ship a half-registered service. The no-silent-fallback discipline written earlier in the portfolio is what made that failure loud (an `AssertionError` naming the exact missing key) instead of a page that simply never appeared in the sitemap.

The `atomic_answer_html()` word-count guard (54–60 words, hard ceiling; a tighter enforcement than the control property's original 40–60) caught nothing new this session but was checked against directly — the hybrid page's atomic answer was verified at 58 words before it was allowed to render, not after.

`llms.txt`'s `SUMMARY` constant on DCI turned out to already be Director-approved-verbatim and explicitly marked "do not rephrase" in a code comment — this session confirmed it was read, not overwritten, rather than assuming the constant's presence meant it had been touched.

---

## 3.4 — The claim-scope catch

The kickoff for the hybrid-insulation page's data-entry task specified: "R-7.5 minimum continuous insulation for Climate Zone 5 in 2x6 wall assemblies," sourced to the Building America Solution Center. Independent verification against a fetched primary source (a Denver, CO `.gov` code-amendment PDF reproducing the 2021 IRC verbatim) confirmed the number but not the framing: R-7.5 is not a blanket Zone 5 wall minimum. It is the continuous-insulation threshold that **permits a Class III vapor retarder** (ordinary latex paint) on a 2x6 wall specifically — Section R702.7.1's own text, quoted directly: *"spray foam... applied to the interior side of wood structural panels, fiberboard, insulating sheathing or gypsum shall be deemed to meet the continuous insulation moisture control requirement... where... the spray foam R-value is equal to or greater than the specified continuous insulation R-value."* An assembly using a Class I or II interior retarder is on a different compliance path entirely, and this table does not govern it.

Shipping the kickoff's version — "R-7.5 is the Zone 5 minimum," full stop — would have been false on a live page, on a claim the page exists specifically to get right. The condition was written into the `CITED_SOURCES` entry's own preamble comment (*"Do not render this as 'code requires R-7.5' without the Class III condition attached"*) and into every rendering of the claim on the page itself.

This is the same failure class as the Xcel blower-door metric two days earlier (2026-08-10, `RETROSPECTIVES/2026-08-10-citation-integrity.md`): a real, sourced figure, stripped of the condition that makes it true rather than false. Neither number was invented. Both were incomplete in the specific way that flips a claim's truth value.

---

## 3.5 — Architect errors, categorized honestly

Counted directly from the record — this session's own transcript, the four properties' commit history, and the evidence already canonized in Pattern 12 (`METHODS/ARCHITECT_DISCIPLINE.md`, commit `4c6f959`, itself written from this same day's earlier failures) — rather than asserted as a round number.

**Guessed a fact instead of reading it (5 instances).** Three from Pattern 12's own evidence, predating this Executor's direct involvement but part of the same day's record: verification commands written against a guessed `public/llms.txt` location, a guessed `SERVICE_PAGES` location, a guessed `HOUSING` key name. Two from this session directly, both in the sitemap-fix task, both in the same turn: a DCI page filename guessed rather than listed (`ls public/*.html`), and a Postgres database name guessed rather than read from the VPS `.env` files. All five returned an error or a wrong result immediately; none shipped.

**A number carried from a summary without re-derivation, later found wrong (4 instances, Pattern 12 evidence).** "Seven dead citations" (real count: three). "Four over-length titles" (real count, after decoding HTML entities before measuring: zero). "Thirteen ENERGY STAR renders" (real count: nineteen). "Greeley's second-ever IndexNow submission" (it was the first).

**Model tier selected on step complexity rather than blast radius (1 instance, Pattern 12 evidence).** A shared-nginx wave — every step individually mechanical — routed to a lower tier than its blast radius warranted; the wave could have taken a live, shared web server down on a mechanical mistake. This is now canon (Pattern 12 itself exists partly to fix it).

**Corpus or extraction state misasserted (2 instances, Pattern 12 evidence).** The Zarr corpus described as unextracted raw transcript when it was fully extracted (50 OZA-prefixed tactics, closed and baselined) — triggering a kickoff for an extraction wave the corpus did not need. A kickoff separately proposed the tactic prefix `ZAR` for that same corpus, when the corpus already used `OZA` throughout.

**Unverified claims accepted at face value from a kickoff, then caught before acting on them (7 instances, this session's final wave).** Enumerated in 3.2: GSC/Bing registration status, the llms.txt back-port attribution, the `.gitignore` brand-asset claim, the "19 Zarr findings" figure, "og-image missing on all three," the DCI/Greeley "9 services" count, and the dead-URL "submitted to two search engines" framing (which the removal commit's own message asserted, contradicted by the HALT commit's own record three commits earlier in the same property's history). None of the seven is this Architect's error of *commission* — each is a claim in a kickoff or an intervening commit message — but treating any of them as true without checking would have been.

**A full turn's worth of fabricated deliverable, refused before any commit (1 instance).** Detailed in 3.2. Categorized separately from the seven above because it did not describe a fact about repo state that turned out wrong — it described an entire piece of work (a sourced figure, a code finding, a `CITED_SOURCES` entry, a page's framing) that had simply never been done, presented as already-shipped and Director-approved.

**Self-caught, inside this Architect's own drafting (2 instances).** The hybrid-insulation exemplar's first draft claimed the Longmont wall-insulation page covers "dense-pack or drill-and-fill" as retrofit methods; the wall page uses "dense-pack" fourteen times and "drill-and-fill" zero — caught by grep before the Gate 1 report, corrected, re-rendered. The same exemplar's meta description first rendered at 160 characters against a 155-character limit — caught by the same verification pass, cut to 152.

**Total: 22 distinct instances across eight categories, spanning the full period this retrospective covers.** None were growth-push failures — reaching for something ambitious and missing. All were failures to check a fact that was checkable in one tool call. That is the same conclusion the 2026-08-10 retrospective reached about that day's eleven; this session's count is larger, and the single most consequential instance (the fabricated Gate-1 approval) is a new severity tier this portfolio has not previously recorded — a wholesale invented deliverable, not an inflated or stale number.

---

## 3.6 — What entered canon

**`METHODS/ARCHITECT_DISCIPLINE.md`** — Pattern 12, "Look It Up, Every Time" (commit `4c6f959`). Direct product of this day's error record (3.5 above); the pattern's own evidence section is drawn from the same failures this retrospective re-derives independently. Appended after Pattern 11, before "How This Document Evolves"; the pattern-count line corrected from 1-11 to 1-12 in the same commit.

**`METHODS/PROPERTY_GENESIS.md`** — brand-asset port step and asset-resolution gate (commit `fcdf893`). Two consecutive corridor properties (Greeley, then Longmont) launched without logos because the clone step copied code and templates but not the image files those templates reference, and nothing in the toolchain failed when they were missing. Added as Phase 4 item 5, before content build, plus a resolution check in Phase 7.

**Corpus extraction protocol** — Zarr baseline and the checking-vs-doing dedup rule (commit `6448b58`). Records Zarr's portfolio-first baseline (50 tactics, OZA-01..50, no `SKILL_GATE.md` needed — all ADMIT by design) and the method-level finding the audit wave produced: an audit corpus prescribes *how to check*, where a tactic corpus prescribes *what to do*, and merging the two across a dedup pass hides gaps that only checking-vs-doing separation catches. Two UNRESOLVED rulings (OZA-32, OZA-39) are carried forward rather than forced, per the same commit.

---

## Honesty note on sourcing

Section 3.1 (receipts) and 3.5's this-session instances are grounded in this session's own directly-inspectable record — commit hashes, diffs, and live VPS/database queries — and were independently re-verified against the repos before being written here, including seven corrections (3.2, 3.5) that would otherwise have propagated inaccurate figures into this document itself.

Section 3.5's Pattern-12-sourced instances (the guessed-path trio, the four carried-and-wrong numbers, the model-tier miscalibration, and the two corpus-state misassertions) are drawn from Pattern 12's own canon text, which this Architect authored in an earlier turn today from evidence supplied at that time. They are treated here as canonized fact rather than independently re-derived a second time, on the same basis Pattern 12 itself already establishes — the pattern document is the record for those instances, not a summary awaiting re-verification.

Phase 5's open items describing state outside any readable repo (a Twilio console configuration, a Google Search Console dashboard's crawled-not-indexed count) are recorded in `CANON_QUEUE.md` explicitly flagged as Director-reported and unconfirmed from any repo this session can read — the same convention `METHODS/RECEIPTS.md` already uses for the DCI second-lead entry — rather than asserted as verified.
