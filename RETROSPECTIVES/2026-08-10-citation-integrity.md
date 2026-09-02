# 2026-08-10 Retrospective — Citation Integrity

**Project:** Denver Colorado Insulation (DCI) + Greeley Colorado Insulation (GCI, corridor property #2)
**Session:** Citation-integrity remediation, ROI-calculator recalibration, static-asset wave
**Duration:** Single calendar day, five shipped waves across both properties
**Methodology:** Four-role Calibrated Stack (Director / Architect / Executor / Auditor)
**Audience:** Canon evolution stakeholders, future Architects and Executors in fresh sessions

---

## Executive summary

One day's work corrected two claims that were reported false and were actually true, cut two claims that were genuinely unsourceable, re-anchored two ROI calculators from a retired range to a current point estimate with the modeling honesty that shift required, fixed a citation-rendering template bug affecting 252 rendered sentences across both properties, converted DCI's robots.txt from a hand-placed file to a generator, shipped `llms.txt` on both properties, and closed a same-day backup-hardening gap on the shared VPS.

**Outcome: nothing shipped false. The near-misses were caught before they shipped, not after.**

The session's defining pattern isn't the individual fixes — it's that most of them share one root cause, documented below as a single error family with four faces. Two of those faces were near-misses that would have *removed true copy* from a live site if the gate hadn't caught them. That is the sharper, less comfortable framing of what "the methodology worked" actually means here: it worked by stopping the Architect from deleting something correct, not just by stopping something wrong from shipping.

---

## 2.1 — What shipped

Condensed from this session's RECEIPTS.md additions (full detail and commit hashes there):

- Xcel rebate claim corrected from an imprecise metric to NACH50, re-cited to the program source that actually states it (11 DCI pages); renter-eligibility FAQ reversed in the same pass (Xcel's program *does* cover rental properties)
- Cellulose settling claim (10-20%) re-sourced to the Building America Solution Center after DOE deleted the page that used to carry it — found TRUE, not false as first suspected
- Insulation ROI claim re-sourced to ENERGY STAR (15% national average)
- One DOE claim and one BPI claim cut as genuinely unsourceable; one further BPI claim de-attributed and retained as the site's own operational characterization, not a citation
- LevelUp Insulation Co. removed from the DCI roundup, count language corrected sitewide (9→8)
- Seven DCI pages backfilled to hold the 2-citation floor
- 23 DCI pages: rebate bullet sharpened with the NACH50 metric
- Citation template fixed on both properties: a hardcoded "the" replaced with a per-key determiner field — 61 of 162 DCI sentences and 37 of 90 GCI sentences affected
- Both properties' ROI calculators re-anchored from the retired DOE range to ENERGY STAR's Climate Zone 5 point estimate (16%), with the resulting spread declared as modeling variance in rendered copy rather than left to impersonate source variance
- GCI's IndexNow mechanism built (own key, key file, submit script); first real submission this session, 1 URL, HTTP 200
- DCI's robots.txt converted from hand-placed to generator-emitted, gaining three AI-crawler allow blocks it lacked
- `llms.txt` created and generator-emitted on both properties (DCI 56 URLs, GCI 27), structured to inherit cleanly into future corridor clones (Longmont, Fort Collins, Loveland)
- VPS backup hardening: the host Postgres cluster absorbed into the backup regime, two previously unprotected databases now backed up, a dead-man checker running on its own systemd timer

---

## 2.2 — The error family that defined the session

Four documented faces of one error: **treating one surface's state as a claim's truth value.**

**i. A presentation reword is not verification.** An earlier "Auditor Fix" pass reworded an unverifiable quote on one page without testing the underlying claim — a fix to how something read, mistaken for a fix to whether it was true. (This session independently confirmed the same failure class exists elsewhere in the codebase: the "Auditor Fix 5" comment on the BPI 2-4x-leakage figure, which shipped for months as a flagged-but-unresolved finding before it was actually cut — see COPY_VOICE.md, "A flag without a disposition is not a fix.")

**ii. A surface's silence is not a claim's falsity.** The Xcel NACH50 blower-door requirement was reported as fabricated because Xcel's consumer-facing page doesn't state it. It was true — the requirement lives in EFI's fulfillment-administrator documentation, a different surface entirely. Verified this session; see COPY_VOICE.md "Surface is not claim, in both directions."

**iii. Absence of a source in one search is not absence of the fact.** The cellulose settling claim was nearly cut as false when DOE deleted the page that stated it. A DOE-funded national laboratory (Building America Solution Center, PNNL, DOE contract DE-AC05-076RL01830) states the identical figure. Verified this session, same COPY_VOICE.md section.

**iv. Enumerating one surface is not enumerating the claim.** Citation entries were enumerated inside the formal `cite_inline()` block; prose instances riding the same claim outside that block — including inline attributions that named their own independent source — were not, until this wave's search widened. See COPY_VOICE.md "Prose-surface enumeration method, standing note."

**Both (ii) and (iii) would have removed TRUE copy from live sites.** Both were caught by a gate before commit — not by the Architect's own drafting process.

---

## 2.3 — What the gates caught

Two conditional halt-gates converted would-be defects into decision surfaces before commit: six pages known in advance to be dropping below the 2-citation floor, and the prose-surface finding that made a citation-only cut cosmetic rather than complete (face iv, above).

A seventh page — `insulation-crawl-space.html` — was **not** on the hand-derived list of six. It was found because an Executor script computed its own affected-page set (which pages actually carry which citation keys) instead of trusting an enumerated list carried over from planning. It was the only page sitewide affected by two simultaneous cuts at once, which is exactly the kind of intersection a hand-count misses and a script doesn't.

**Standing lesson:** affected-page sets are derived by script, never by enumeration. A hand-derived "the six pages that need this" list is a claim about the codebase, and claims about the codebase get verified against the codebase, not carried forward from memory.

---

## 2.4 — Architect error count

Eleven Auditor FAILs landed on Architect errors this session, categorized:

- **Arithmetic and unit drift inside halt conditions (3 instances)** — counts propagated from summaries without checking against the reports they came from. A halt check with a wrong expectation trains the Executor to explain away mismatches rather than trust the check. (This session's own Executor record shows the same failure class surfacing at the kickoff level, not just inside halt conditions — a string count stated as "26 DCI + 9 Greeley" turned out to be 29 and 21 on direct count; a prior wave stated "18 URLs, HTTP 202" for GCI's first IndexNow submission where the verifiable record showed 1 URL, HTTP 200. Neither was propagated uncorrected.)
- **Header-vs-task collisions (3 instances)** — a permissions header forbidding rendered-text changes, followed by a task instructing the Executor to author rendered text.
- **Verification steps that could only fail or only pass** — a grep whose expected values could not be produced by correct output; a range check that would have halted on the wave's own citation.
- **Surface-vs-claim collapses (2 instances)** — per 2.2 above.
- **Over-fragmentation (1 instance)** — splitting a wave where a conditional gate would have removed the round entirely.
- **Scope named in a preamble and absent from the body (1 instance).**

None were growth-push failures. All were careless. The Director's standing position is that growth-push failures — reaching for something ambitious and missing — are acceptable, and careless ones are not. This session's Architect error count is entirely the latter category.

Four of these categories are now written directly into `METHODS/ARCHITECT_DISCIPLINE.md` Pattern 9's pre-submission checklist (arithmetic/unit drift, scope-in-preamble, surface-vs-claim collapse, and over-fragmentation were already there before this session; this session's own corollary — source shape versus source meaning — was added to the same list, see 2.7 and Phase 3 of this wave).

---

## 2.5 — The consolidation experiment

One kickoff carrying four phases ran unattended for roughly 40 minutes and completed all nine internal phase-steps without halting. Round-count is a real cost to the Director — every hop requires him present, reading and routing, and a session built from many small round-trips spends that attention on bookkeeping rather than judgment.

The consolidation shape that worked: **one shipping phase fully specified** (exact values, exact strings, exact commit boundaries — nothing left for the Executor to interpret), **three research phases that stop before committing rendered text** (they can run unattended precisely because their output is a decision surface, not a live change), and **phase-level halts that do not stop unrelated phases** (a halt in the DCI-specific phase doesn't block the GCI-specific phase from completing its own work).

This is the shape to generalize: unattended time is earned by narrowing what the Executor is allowed to decide, not by trusting it more broadly.

---

## 2.6 — Executor conduct

Five consecutive waves of correct lane discipline, each traceable to a specific moment in this session's record:

- **Refusing a false premise handed to it by its own kickoff, and corroborating the refusal three ways.** The session's first wave was asked to "confirm Greeley's [ROI] constants are genuinely unrelated, as the prior wave reported." They were not — the Executor found Greeley's `CEILING_SHARE_LOW` matching the retired DOE range's low bound exactly, traced it to the same `DOE_INSULATION_ROI` citation key at introduction, and confirmed the two properties' re-sourcing commits landed one minute apart in the same wave. Three independent lines of evidence, not one assertion.
- **Refusing to verdict an unverifiable source rather than guessing.** `savingsRange()`'s payback breakpoints returned an explicit UNRESOLVABLE disposition — no derivation comment, no commit history, no math-link to any recorded figure — rather than a forced TIED or INDEPENDENT call the evidence didn't support.
- **Flagging a scope departure instead of burying it.** Extracting a hand-maintained 13-city literal into a named constant (`AREA_SERVED_CITIES`) went beyond a literal file port; it was flagged explicitly as a judgment call rather than folded silently into the commit.
- **Correcting a count in a kickoff rather than reverse-engineering a way to make it true.** Twice this session: a description-authoring string count corrected from a stated 26/9 to a verified 29/21, and — in this same paperwork wave — "two BPI claims cut" corrected to "one DOE claim and one BPI claim cut" against the actual commit record.
- **Declining to invoke IndexNow with no arguments when its default would have resubmitted an entire sitemap.** The static-asset wave's diff touched zero HTML pages on either property; rather than run the submission script and let its documented no-args behavior silently resubmit everything, the Executor submitted nothing and said so.

---

## 2.7 — What entered canon

**ARCHITECT_DISCIPLINE.md**, six recurring patterns (Patterns 1-6 through this session's history), plus this session's own addition to Pattern 9's checklist:
- A source whose shape matches the output but whose spread means something different — geographic variance cannot stand in for house-to-house variance.

**COPY_VOICE.md**, five rules added or reinforced this session, byte-identical across both properties:
1. A flag without a disposition is not a fix.
2. Two utilities, two metrics — never carry one utility's measurement into another's copy.
3. Surface is not claim, in both directions.
4. A derivation comment is a claim — it updates in the same commit as the constant it describes.
5. A calculator's source must be shaped like its output; a spread's meaning is part of its shape.

---

## Honesty note on sourcing

This retrospective draws on two different kinds of evidence, and they carry different weight.

Sections 2.1, 2.3 (the seventh-page finding), and 2.6 are grounded in this session's own directly-inspectable record — commit messages, diffs, and this Executor's own transcript — and were independently verified against the repos before being written here, including two corrections (the BPI-cut characterization and the IndexNow submission count) that would otherwise have propagated an inaccurate figure into a canon document.

Sections 2.2.i, 2.4, and 2.5 describe Auditor-gate outcomes and a specific unattended-run timing that happened in Director/Auditor review passes this Executor was not present for and has no transcript access to — by design, since the Auditor is a separate review session. Those sections are written as supplied, per this wave's own instruction that the kickoff carries its own content here. They read as consistent with everything independently verified elsewhere in this document (the "Auditor Fix" pattern, the source-shape corollary, the standing over-fragmentation concern already in canon), but they are not independently re-derived from primary sources the way the receipts ledger entries were.

---

## Addendum — the session's second half (2026-08-10)

Three more waves shipped after Pass 1 closed (commit `aed57e4`): Greeley's first SEO-corpus alignment audits, the resulting gap-fix and DCI-audit-correction wave, and their deploy. This addendum covers them, and — separately — corrects the record where Pass 1's own numbers didn't hold up.

## 3.1 — The error family gained a fifth face

Pass 1 documented four faces of one error: treating one surface's state as a claim's truth value (§2.2). The second half surfaced a fifth: **an audit document's verdict line is a surface too.**

Greeley's first alignment audit (commit `cd2880e`) read DCI's `VAHE_ALIGNMENT_AUDIT.md` and `FLOATE_ALIGNMENT_AUDIT.md`, found five tactics (PTE-47, PTE-40/51, PCO-03, PCO-13, PTA-27) recorded there as open VIOLATION/GAP items "fixed only on an unmerged branch," and concluded — reasonably, given what the surface said — that DCI was behind its own Greeley clone. The verdict lines were stale: the branch in question, `vahe-batch-2`, had been fully merged weeks earlier (independently re-verified this pass: `git log main..vahe-batch-2` returns empty, `git merge-base --is-ancestor vahe-batch-2 main` confirms). DCI's own audit documents corrected eight verdict lines total — the five above plus PAR-22/44/50, a second stale cluster — in commit `e8d0e0a`. The document was the surface; nobody had re-derived from the code it was describing until this wave did.

This is not a new species of error. It is face (ii) and (iv) from Pass 1's own list, wearing a different surface: a verdict line is exactly as capable of going stale as a vendor page or a search result, and an audit-of-an-audit inherits that staleness silently unless it re-derives.

## 3.2 — The re-derivation discipline paid for itself, repeatedly

Every number this pass was told to re-measure rather than carry turned out wrong — independently verified against git and the live repos before being written here:

- **Seven dead citations were three.** Greeley's `STATE_OF_PROJECT.md` recorded 7 dead outbound citations on 2026-08-09; by the time the gap-fix wave re-ran `_check_links.py --check-outbound` (commit `69b56d5`), 4 of the original 7 had already been removed from `CITED_SOURCES` incidentally by the unrelated citation-remediation wave. 3 remained, genuinely.
- **Four over-length titles were zero.** A 2026-08-10 interim check flagged 4 DCI pages at 62/62/61/64 characters. Those were raw HTML-entity-encoded string lengths (`&amp;` counted as 5 characters, not the 1 it renders as). Re-measured decoded, sitewide, across all 63 DCI pages (commit `e8d0e0a`): zero violations.
- **A "first-ever" IndexNow submission was a phantom.** Pass 1's own `RECEIPTS.md` recorded a first-ever Greeley IndexNow submission (1 URL, HTTP 200, tied to commit `e13a438`). Re-checked this pass: `e13a438`'s own commit message covers only the llms.txt/sitemap wave and never mentions IndexNow; Greeley's `STATE_OF_PROJECT.md` recorded the mechanism as "not yet deployed or submitted" from the moment it was built and was never updated otherwise; the next wave to touch the gap (`69b56d5`) states plainly "confirmed live via direct GET, HTTP 200, content matches. Closed, **no submission made**." No corroborating evidence exists anywhere. The receipt has been retracted in `RECEIPTS.md` (see this pass's entry there) and replaced with the real first submission — 5 URLs, HTTP 200, made during this wave's own deploy.

**One claimed fourth correction could not be substantiated and is deliberately not repeated here as fact.** This pass's kickoff asserted that "thirteen ENERGY STAR renders were nineteen" — implying some prior record stated 13 rendered pages for the `ENERGYSTAR_R49_R60` citation swap before the real count of 19 was confirmed. A full-text search of both properties' markdown docs and git history (current files and `git log --all -p`) found no occurrence of "13" attached to this citation swap, anywhere, at any point. The verified figure — 19 DCI pages, 4 Greeley pages — appears consistently everywhere it's recorded, including in commit `e8d0e0a`'s own message at the time it shipped. Rather than write a fourth "was 13, now 19" line into canon on the strength of an unverified kickoff assertion, this addendum records three verified corrections and flags the fourth as unconfirmed. This is itself an instance of the discipline in §3.2's own headline: a number arrived carried, and re-deriving it — rather than transcribing it — is what this section exists to model.

## 3.3 — The build-order law caught its first mis-filing

Three tactics (PCO-43/44/46) were labeled BLOCKED BY BUILD ORDER in Greeley's audit and re-categorized to the internal gap list in the same gap-fix wave (`69b56d5`) that fixed the citation and title defects. Each was unilateral analysis of the property's own link profile — gated on tooling, not on another party's cooperation, a platform's approval, or third-party payment — so the BLOCKED label was a mis-filing, not a real external gate.

This tracks cleanly to `ARCHITECT_DISCIPLINE.md` Pattern 11's own auditability requirement: a blocked item must name its specific external dependency in one line, and an item that cannot name one is mis-categorized. `git log` confirms Pattern 11 was committed (`f6540b7`, 2026-08-10 12:31 -0600) before the re-categorization that applied it (`69b56d5`, 2026-08-10 ~17:54 -0600 equivalent) — consistent with this being the law's first real-world catch within these two properties' history, though this addendum cannot rule out an earlier instance elsewhere in the portfolio it has no visibility into.

## 3.4 — A shared-key defect is a portfolio defect

The dead `ENERGYSTAR_R49_R60` citation was found by Greeley's own audit and gap-fix wave. The same key renders on DCI — 19 pages, independently confirmed via `git show --name-status e8d0e0a`, all 19 live-verified post-deploy with zero remaining occurrences of the dead URL. Fixing the property that found the defect without fixing the property that shares its citation pool would have left DCI — the flagship, the only revenue asset — serving a URL its own sibling property had just proven to 404.

This addendum can independently verify the outcome (both properties fixed, same wave, same key) but not the specific claim in this pass's kickoff that the fix was "originally scoped to Greeley alone" before being widened. That framing describes what would have happened at a decision point this Executor has no transcript access to, in the same category as the Auditor-gate content flagged in Pass 1's own honesty note below. The standing lesson stands regardless of how the scope got corrected: a shared-key defect found on one property is a portfolio defect, and the fix set should be derived from which properties share the key, not from which property happened to find it.

## 3.5 — Updated error count

Pass 1 recorded eleven Auditor FAILs landed on Architect errors, categorized (§2.4). This addendum cannot extend that count for the session's second half: there is no accessible record of individual Auditor FAILs from that period — no transcript, no repo file enumerating them — for the same reason Pass 1's own honesty note gives for §2.4 itself: the Auditor is a separate review session this Executor has no visibility into. Supplying a number here without one would be exactly the carried-figure failure this addendum exists to correct, not model.

What this addendum can state from the directly-inspectable record: the second half's own commit messages show zero instances of the two near-miss failure classes from §2.2 (surface-vs-claim collapses that would have removed true copy) recurring, and both live deploys this wave reported zero HALTs against their own verification gates. That is not the same claim as "zero Auditor FAILs in the second half," and should not be read as one.

---

## Honesty note on the addendum

§3.1, §3.2, and the factual core of §3.3 and §3.4 (commit contents, file counts, live-verification results, `git log`/`git merge-base` output) are independently re-derived from the repos and git history in this pass, not carried from the kickoff that requested them — including the retraction in §3.2, which corrects Pass 1's own record, and the deliberate omission in §3.2, which declines to record a claim this pass could not substantiate.

The narrower framing claims in §3.3 ("first" mis-filing, portfolio-wide) and §3.4 ("originally scoped to Greeley alone," "the Auditor caught it") describe process and decision-point history this Executor was not present for and has no transcript access to, in the same category Pass 1's own honesty note already established for its §2.2.i, §2.4, and §2.5. They are recorded because they are consistent with everything independently verified elsewhere in this addendum, not because they were independently confirmed themselves.

§3.5 records an absence rather than a number, on purpose.

---

## Correction — 2026-09-02, the NACH50 metric this retrospective treated as verified-true was itself false

This document's §2.1 (line 25: "corrected... to NACH50, re-cited to the program source that actually states it"), §2.1 (line 31: "23 DCI pages: rebate bullet sharpened with the NACH50 metric"), and §2.2.ii (line 47: "The Xcel NACH50 blower-door requirement was reported as fabricated... It was true") all name "NACH50" as the Xcel blower-door metric. There is no such metric. Xcel's actual first-party figure, confirmed against the primary source, is **"20% Reduction in CFM 50"** — a different unit entirely (a percentage reduction in cubic-feet-per-minute-at-50-pascals, not a named "NACH50" standard). The string `NACH` appears nowhere in Xcel's source documentation.

This was caught and corrected at the `METHODS/PROPERTY_GENESIS.md` surface in canon commit `5265f69`. It was not, at that time, traced back to this retrospective, where the same false metric appears in three more places (the two listed above plus this note). `METHODS/RECEIPTS.md:129,151` carries the same false metric and remains uncorrected as of this note — out of scope for the session that wrote this correction, which was not permitted to touch `METHODS/` this pass. See `denvercoloradoinsulation.com/docs/board/ready/canon-nach50-remaining-surfaces.md` for the full remaining-surfaces list.

**What does NOT survive this correction: the word "NACH50" as a real metric, everywhere it appears above.** The two rebate-copy mentions (§2.1) simply named the wrong metric string for a real, correctly-shipped rebate-copy fix; nothing about that correction's substance changes.

**What DOES survive this correction, deliberately preserved rather than retracted: the epistemic principle §2.2.ii illustrates.** The principle — "a surface's silence is not a claim's falsity," i.e., that a fact absent from one surface (Xcel's consumer-facing page) can still be true and documented elsewhere (per the original investigation, a fulfillment-administrator surface) — is a real, sound, and separately-useful methodological finding, independent of which metric name was the illustration's subject. §2.2.ii's *illustration* used a metric name that does not exist; its *point* does not depend on that name being right, and this note does not touch the point. Readers should treat "NACH50" wherever it appears above as a name error in an otherwise-real finding, not as evidence the finding itself was fabricated.

Per this document's own §2.2 framing: this is a sixth face of the same error family, and a pointed one — a document that exists specifically to document "surface is not claim, in both directions" itself carried an uncaught surface error (a wrong metric name, repeated three times, in the very passage making that argument) for over three weeks before an unrelated remaining-surfaces sweep caught it. The gate that should have caught this (checking the illustration's own factual content, not just its shape) did not exist at the time this document was written.

This correction is appended, not merged into the original prose above, consistent with this document's own established convention (see the Addendum's retraction-and-replacement of the phantom IndexNow receipt in §3.2, and the corrected-verdict-lines finding in §3.1) of recording corrections as dated additions rather than silently rewriting history that already shipped as a session record.

---

**End of retrospective.**
