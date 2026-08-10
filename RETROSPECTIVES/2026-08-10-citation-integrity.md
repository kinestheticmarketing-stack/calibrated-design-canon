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

**End of retrospective.**
