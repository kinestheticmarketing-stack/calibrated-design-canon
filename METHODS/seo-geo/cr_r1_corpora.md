# R1 — CORPORA LOAD AND VERIFY (gate for R2–R10)
Date: 2026-08-19 · Canon branch feat/seo-geo-scaffold

## PRE-FLIGHT DISCREPANCY — kickoff hashes
None of the four hashes named in the kickoff exist in any repo:
  DCI 9a0e93a · LGM 41f6bc5 · GCI 9e04a17 · CANON 08de56b  -> `git cat-file -e` fails on all four.
Real HEADs at wave start: DCI 0f95413 · LGM 5ccb2e8 · GCI 2a7e43d · CANON fd4b2fb.
All four trees clean. Proceeding on real HEADs.

## CORPUS SECURITY DEFECT — FOUND AND FIXED (canon c08a2db)
Every EXTRACTION_LOG states "sources/ is gitignored — local-only, never
committed, never public, never free." FALSE as configuration: sources/ was
merely untracked. `git add -A --dry-run` at canon root staged **342 files**
of paid, watermarked course material — including Floate SITE_DATABASE.md
(106 publications, contact emails, 2023 rate cards).
Fixed: METHODS/seo-geo/sources/ added to .gitignore. Re-ran dry-run: 0 staged.

## CENSUS — verified by walking the files, not read from the logs

### Allsopp — glen-allsopp-seo-blueprint-3 · 197 files · 289 minted IDs
| module | dir | prefix | n | contiguity |
|---|---|---|---|---|
| On-Site SEO | on-site-blueprint/ | T31..T58 (13 per-lesson prefixes) | 68 | contiguous within each lesson |
| Local SEO | local-seo-blueprint/ | TLO | 73 | TLO-01..73 contiguous |
| Link Building | link-building-blueprint/ | TLB | 38 | TLB-01..38 contiguous |
| Superpixels | superpixels/ | TSP | 36 | TSP-01..36 contiguous |
| Keyword Research | keyword-research-blueprint/ | TKR | 29 | TKR-01..29 contiguous |
| Super Content | super-content-blueprint/ | TSC | 22 | TSC-01..22 contiguous |
| Experts | experts-blueprint/ | TEB | 14 | TEB-01..14 contiguous |
| Playbook | playbook/ | TPB | 9 | TPB-01..09 contiguous |

**COUNT DEFECT — the EXTRACTION_LOG's prefix list is incomplete.** It names
TSP/TLO/TSC/TEB/TPB/TKR. It omits **TLB** (38 tactics) entirely, and it does
not disclose that the On-Site module — the single most relevant module to this
portfolio — does not use one module prefix at all. On-Site mints per-lesson IDs
(T31-01, T39-05, T58-10 …) for **only 13 of its 58 lessons**; the other 45
lessons carry tactics as named `### <Tactic Name>` headings under `## TACTICS`
with no ID. So "289 minted IDs" understates On-Site's true tactic count.
Proceeding on the real numbers.

### Vahe — vahe-arabian-publisher-seo · 55 files · 240 minted IDs
PIN 3 · PTE 77 · PCO 52 · PTA 30 · PPI 22 · PRA 26 · PCD 30. All contiguous,
no gaps, no duplicates. **Matches its EXTRACTION_LOG exactly.** Clean corpus.

### Floate — charles-floate-parasite-seo · 10 files · 54 minted IDs
PAR-01..54, contiguous. Matches its log ("course-wide census: 54 tactics").

## ADMIT vs SKILL_GATE
Only Floate carries a SKILL_GATE.md. Its split, made once by the Architect:
**39 BLOCKED / 15 ADMIT.** Test: BLOCKED if the tactic depends on placing
content on a property the Director does not own (the mechanism Google's site
reputation abuse policy dismantled 2024-25). ADMIT = works unchanged on an
owned property.
ADMIT set: PAR-18,19,20,21,22,24,26,27,28,32,42,44,47,48,50.
Allsopp and Vahe have **no SKILL_GATE file** — no ADMIT/BLOCKED split exists
for them. Their whole corpus is nominally admissible; the build-order
exclusion is the only filter, applied here per tactic.

## PRIOR AUDITS ON DISK — the diff baseline
All nine last committed 2026-08-18. **They are not the same instrument.**

| property | Allsopp (MODULE_ALIGNMENT_AUDIT) | Vahe | Floate |
|---|---|---|---|
| DCI | 186 ln — **module-level narrative, 9 modules, NO per-tactic verdicts**. Header DATE 2026-08-12, body says "Audit complete 2026-07-08" | 301 ln — no verdict tokens | 542 ln — 6 N/A, 1 NOT-APPLIED, 5 PARTIAL (12 scored) |
| LGM | 118 ln — 4 APPLIED, 15 APPLIED-UNTRACKED, 2 N/A, 8 NOT-APPLIED (29) | 107 ln — 6/16/13/17 (52) | 115 ln — 8/5/14/16 +1 PARTIAL (44) |
| GCI | 249 ln — 4/11/3/4 +1 PARTIAL (23) | 318 ln — 5/34/13/14 (66) | 213 ln — 8/6/13/13 +6 PARTIAL (46) |

**BASELINE DEFECT.** DCI's Allsopp and Vahe audits carry no per-tactic
verdicts at all — DCI's Allsopp audit is a module-level summary written at a
different grain from LGM's and GCI's. There is therefore **no per-tactic DCI
baseline to diff against for Allsopp or Vahe**. Report section (l) diffs what
exists and states plainly where no baseline exists rather than inventing one.
DCI's audit also self-reports two different dates in its own header/body.

Corroboration found in DCI's Allsopp audit, M1: "www->apex 301 canonicalization
SHIPPED (commit 5f12c91)" — independently confirmed live this session (all
three properties 301 to apex).

## BUILD-ORDER EXCLUSION — modules removed from scoring, silently, not carded
Allsopp link-building-blueprint (TLB 38) and local-seo-blueprint (TLO 73) are
GBP / citation / directory / outreach modules. Keyword-research (TKR 29) is
predominantly paid-rank-tooling. These are not evaluated, not scored, not
counted. Floate: of its 15 ADMIT, the link-profile and paid-tool tactics
(PAR-18,19,20,21,24,32,47,48) fall under the same exclusion.

## GATE: R1 PASSES. R2–R10 may proceed on the verified numbers above.
