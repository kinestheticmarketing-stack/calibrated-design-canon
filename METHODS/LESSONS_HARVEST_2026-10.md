# LESSONS HARVEST — 2026-10

*Kickoff 43 · 2026-10-11 · a method-level record under [PROPERTY_GENESIS.md](PROPERTY_GENESIS.md).*

Three insulation properties (DCI, LGM, GCI) are finished. Every defect they recorded is classified here by root cause, and each class is given one verdict: does a generator default or a build-failing check already prevent it, or only a written method, or nothing. The next property (Fort Collins) must inherit every class as a DEFAULT or a GATE. This document proposes; it builds nothing.

**Sources.** 358 closed rows of canon `docs/board/OPEN_LIST.md` + 886 defects named in the site repos' `docs/audits/`, `docs/board/ground-truth.md` and `ops/retired_strings.txt`, deduplicated against the canon rows = **1244 rows**. Original classes: seed taxonomy C01-C18 plus NEW:* classes assigned by the row-extraction pass.

**Verify.** `awk '/^## Appendix/{a=1} a && /^\| [0-9]+ \|/' METHODS/LESSONS_HARVEST_2026-10.md | wc -l` must print 1244.

**Repo shorthand.** DCI = denvercoloradoinsulation.com, LGM = longmontcoloradoinsulation.com, GCI = greeleycoloradoinsulation.com, all under `~/code/`. "canon" = this repo. Line numbers are as of 2026-10-11 (DCI, LGM, GCI and canon at their HEAD of that date).

---

## H1 Defect classes

Merges are whole-class only. Five rows were then reassigned individually by the independent reader (row-level overrides, marked `(override)` in the appendix): LGM-k18-006 K09→K18 (`k18-closures.md:12` rules it "not a defect"); DCI-gE-E-8 K19→K20 (marked PRE-EXISTING, no edit caused it); GCI-verm-F2 K08→K03 (root cause is a fabricated EPA quotation); DCI-F112 K03→K15 (one-decimal payback display is a calculator defect); DCI-rs-18 K19→K16 (the retired caption promised an in-home estimate the site does not perform). The mapping table below counts rows before overrides; the final-class table counts after.

### Mapping, original class to final class

| original class | canon rows | site rows | final class |
|---|---:|---:|---|
| C01 | 3 | 24 | K01 territory-port |
| C02 | 15 | 24 | K02 stale-status |
| C03 | 120 | 263 | K03 unsourced-or-wrong-claim |
| C04 | 5 | 3 | K04 dead-or-misaimed-citation |
| C05 | 3 | 9 | K05 broken-or-orphan-internal-link |
| C06 | 1 | 8 | K06 duplicate-copy |
| C07 | 4 | 1 | K07 secret-in-tracked-file |
| C08 | 23 | 173 | K08 internal-inconsistency |
| C09 | 16 | 14 | K09 seo-markup |
| C10 | 15 | 11 | K10 template-residue |
| C11 | 11 | 5 | K11 dead-file-or-code |
| C12 | 2 | 0 | K12 generator-fragility |
| C13 | 23 | 25 | K13 record-drift |
| C14 | 17 | 5 | K14 ops-pipeline |
| C15 | 7 | 31 | K15 render-ux-a11y |
| C16 | 5 | 2 | K16 identity-misrepresentation |
| C17 | 9 | 9 | K17 fabricated-review-date |
| C18 | 54 | 183 | K18 not-a-defect |
| NEW:blind-instrument | 0 | 7 | K21 instrument-gap |
| NEW:caveat-detached | 0 | 2 | K22 caveat-gap |
| NEW:contractor-voice | 0 | 10 | K16 identity-misrepresentation |
| NEW:copy-craft | 10 | 0 | K20 prose-defect |
| NEW:edit-residue | 0 | 37 | K19 edit-residue |
| NEW:generator-fragility | 5 | 0 | K12 generator-fragility |
| NEW:malformed-prose | 0 | 26 | K20 prose-defect |
| NEW:missing-gate | 3 | 0 | K21 instrument-gap |
| NEW:omitted-safety-caveat | 0 | 2 | K22 caveat-gap |
| NEW:pending-task | 7 | 0 | K18 not-a-defect |
| NEW:template-misapplied | 0 | 11 | K23 template-misapplied |
| NEW:undisclosed-relationship | 0 | 1 | K16 identity-misrepresentation |

### Final classes

| final class | definition | canon rows | site rows | total |
|---|---|---:|---:|---:|
| K01 territory-port | A fact true in one utility, jurisdiction or town territory stated for another (utility, rebate, program, code edition, town, local service detail). | 3 | 24 | 27 |
| K02 stale-status | A time-bound status sentence went false after an outside change (program opened/closed, amount or code edition changed, dated framing aged). | 15 | 24 | 39 |
| K03 unsourced-or-wrong-claim | A figure or factual claim with no primary source, the wrong source, or contradicted by its own source. | 119 | 264 | 383 |
| K04 dead-or-misaimed-citation | An outbound citation is dead, redirected, or points at a document that does not support the sentence. | 5 | 3 | 8 |
| K05 broken-or-orphan-internal-link | Broken internal link or anchor, or a page/index entry missing from nav, body, sitemap or llms.txt. | 3 | 9 | 12 |
| K06 duplicate-copy | Duplicate or near-duplicate copy, titles or meta within a page, across pages, or across sites. | 1 | 8 | 9 |
| K07 secret-in-tracked-file | A secret, credential or server address committed to a tracked file. | 4 | 1 | 5 |
| K08 internal-inconsistency | Two surfaces of one property disagree (figures, names, counts vs lists, page vs sibling, label vs output). | 23 | 172 | 195 |
| K09 seo-markup | Title/meta length, canonical, sitemap/lastmod, robots, og/twitter, JSON-LD or title/H1 defect. | 16 | 13 | 29 |
| K10 template-residue | Placeholder, token, internal/dev note or scaffolding text visible to a reader. | 15 | 11 | 26 |
| K11 dead-file-or-code | Unused file, function, variable, config or branch left in the repo. | 11 | 5 | 16 |
| K12 generator-fragility | Generator or script depends on hand-maintained duplicates, positional reads, automatic text transforms or hardcoded environment values instead of derived constants. | 7 | 0 | 7 |
| K13 record-drift | An internal record (state doc, ledger, code comment, config pin) disagrees with the code or with reality. | 23 | 25 | 48 |
| K14 ops-pipeline | Lead form, email, monitoring, backup, deploy, dependency or server defect. | 17 | 5 | 22 |
| K15 render-ux-a11y | Rendering, layout, interactive tool logic or input handling, accessibility or mobile defect. | 8 | 31 | 39 |
| K16 identity-misrepresentation | The site misstates who it is: named persona or Person node, contractor voice on a non-contractor site, undisclosed relationship. | 5 | 14 | 19 |
| K17 fabricated-review-date | A "last reviewed / verified / effective" date not backed by a real change or review. | 9 | 9 | 18 |
| K18 not-a-defect | Closed with no content defect: premise void, ruled intentional, never applied, or a queued task recorded as a row. | 61 | 184 | 245 |
| K19 edit-residue | A deletion or bulk edit left fragments: orphaned parentheticals, doubled or welded words, headings or promises whose answer was removed. | 0 | 35 | 35 |
| K20 prose-defect | Grammar, agreement, wrong word, fragment, tautology, duplicated word or punctuation defect not caused by an edit. | 10 | 27 | 37 |
| K21 instrument-gap | A check is missing, or an existing instrument is blind to the defect it is cited for (wrong corpus, unit, predicate, or never wired). | 3 | 7 | 10 |
| K22 caveat-gap | A required hedge or safety caveat is missing, or rendered away from the claim it qualifies. | 0 | 4 | 4 |
| K23 template-misapplied | A shared block, FAQ or schema description rendered on a page type it does not fit. | 0 | 11 | 11 |
| **total** | 23 classes | **358** | **886** | **1244** |

Row total computed from the TSVs: 358 + 886 = 1244; expected 358 + 886 = 1244: MATCH.

**Merge notes (left as merged, flagged):**
- K16 absorbs NEW:contractor-voice. Some of those GCI rows (e.g. GCI-costcalc-P-04, GCI-index-F-07) are equally unsupported service promises (K03); they stay in K16 because the false part is who performs the work.
- K18 absorbs NEW:pending-task. Those seven are queued work recorded as defect rows, not void premises; both are rows that cost triage and prevented nothing.
- K12 absorbs C12 (environment hardcodes). Both are generator code that holds a value it should derive.
- K22 merges detached and omitted caveats; the Atmos verification-note rows are also K08-adjacent (one figure, four renderings, one caveat).

---

## H2 Inheritance

**Verdicts.** DEFAULT = a generator already produces it correctly. GATE = a check invoked by regen_all.sh whose failure makes regen_all.sh exit non-zero. PROCESS = only a canon METHODS line prevents it. NONE = nothing. Where protection is partial, the verdict is the strongest one that tests the class's root cause; what it misses is in the gap note.

**How GATE was verified.** All three `regen_all.sh` start with `set -e` (line 27) and call every check as a bare command (no `||`, no `if`, no `|| true`). `_postbuild_check.py`, `_check_links.py` and `_intra_similarity_check.py` exit 1 on a finding. The claim gate wrapper `ops/claim_gate.sh` (identical in all three apart from its config name) `exec`s canon `claim_gate.py`, so its exit code is the build's.

**Does `ops/claim_gate.sh --brief` block? Yes.** `args.brief` is passed only to `emit_rule()` (canon `ops/claim_gate/claim_gate.py:8237`), which uses it at `claim_gate.py:7701` only to suppress the per-hit enumeration; the exit code is set at `claim_gate.py:8295` (`exit_code = 1 if blocking_fail else 0`) regardless of `--brief`, and config/canary/corpus failures return 2. Blocking rules: R1, R2, R4-R10 (Rule default `blocking=True`). Not blocking: R11 (`blocking=False`, `claim_gate.py:7089`) and R3 (demoted by measurement, 68.1% false positives, `ops/claim_gate/config/common.json:1154`, applied at `claim_gate.py:8191-8199`). A green claim gate therefore says nothing about R3 or R11 findings.

**What a fourth property inherits.** The claim gate lives in canon and needs only a `config/<site>.json`: inherited. `_postbuild_check.py`, `_check_links.py`, `_intra_similarity_check.py` and every generator live in the site repos; canon carries no template. A GATE built on those is inherited only by copying a parent (PROPERTY_GENESIS Phase 2), and the copies already differ: DCI has 14 post-build checks, LGM 12, GCI 9; the retired-superlative scan is wired only in DCI (`regen_all.sh:244`; GCI has `ops/superlative_scan.py` unwired, LGM has none).

| class | verdict | evidence | scope | gap note |
|---|---|---|---|---|
| K01 territory-port | GATE | canon ops/claim_gate/claim_gate.py:rule_R2 (line 2230; Rule "WRONG-UTILITY CLAIM" registered blocking at :6573); invoked by denvercoloradoinsulation.com/regen_all.sh:223, longmontcoloradoinsulation.com/regen_all.sh:252, greeleycoloradoinsulation.com/regen_all.sh:178 (`ops/claim_gate.sh --brief`) | LOCAL | R2 tests utility attribution per town against config/<site>.json only; code editions, building-dept text, hours and town lists are uncovered except DCI-only denvercoloradoinsulation.com/_postbuild_check.py:check_code_citation_lock (:964). LGM-only generator default longmontcoloradoinsulation.com/_shared_components.py:AUTHORING_REQUIRED (:141) refuses unauthored market constants; not in canon. |
| K02 stale-status | PROCESS | canon METHODS/QUARTERLY_CHECK.md:9 (rebate programs) and :14 (code editions) | LOCAL | Quarterly cadence only. R7 (canon ops/claim_gate/claim_gate.py:rule_R7, :5192) blocks listed superseded identifiers only; retired-string locks are per-site and differ (DCI check_retired_strings_lock :1092, LGM check_retired_strings :711, GCI check_k15_lock :756); canon scripts/staleness_watcher.py is invoked by no build and by nothing in canon scripts/monitoring/. |
| K03 unsourced-or-wrong-claim | PROCESS | canon METHODS/PROPERTY_GENESIS.md:486 (primary source, verbatim quote, dated retrieval) | PORTABLE | Gates test citation PRESENCE, not fidelity: canon ops/claim_gate/claim_gate.py:rule_R5 (:4065, uncited statistic) and rule_R1 (:1998, fabricated quotation) block on all three; check_citation_floor (DCI :628, LGM :515, GCI :500) counts citations. No check that the source says what the sentence says. |
| K04 dead-or-misaimed-citation | PROCESS | canon METHODS/QUARTERLY_CHECK.md:21 (every outbound link returns 200 and shows the cited title) | PORTABLE | `_check_links.py --check-outbound` is opt-in and not in regen_all.sh; canon scripts/staleness_watcher.py (citation fingerprints) is invoked by no build and by nothing in canon scripts/monitoring/; nothing checks the cited document supports the sentence. |
| K05 broken-or-orphan-internal-link | GATE | _check_links.py:check_internal (DCI :42, LGM :43, GCI :43); invoked by regen_all.sh DCI:144, LGM:233, GCI:159; exits via `sys.exit(exit_code)` DCI:171, LGM:119, GCI:119 | PORTABLE | Resolves internal .html hrefs only: no orphan-page, nav, sitemap or llms.txt completeness check; blind to #fragments and JSON-LD URLs (GCI-xcut-19). |
| K06 duplicate-copy | GATE | _intra_similarity_check.py:main (all three; `return 1 if authored_rows` at :187); invoked by regen_all.sh DCI:147, LGM:236, GCI:162 | PORTABLE | Pairwise page Jaccard >= 0.30 within one property only: repeated sentences inside a page, short repeated taglines/meta, and cross-site copies are unchecked (claim gate R9 `--peer` is never passed by the build). |
| K07 secret-in-tracked-file | PROCESS | canon METHODS/ARCHITECT_DISCIPLINE.md:101 (RULE 5 — never surface a secret) | PORTABLE | No secret or server-address scanner runs on build or commit in any repo. |
| K08 internal-inconsistency | GATE | canon ops/claim_gate/claim_gate.py:rule_R9 (line 5826; "INTERNAL CONTRADICTION", blocking); invoked by denvercoloradoinsulation.com/regen_all.sh:223, longmontcoloradoinsulation.com/regen_all.sh:252, greeleycoloradoinsulation.com/regen_all.sh:178 (`ops/claim_gate.sh --brief`) | PORTABLE | R9 checks only the subjects its config names; count word vs list length, table superlatives, label vs tool output and sibling-page figure ranges are unchecked (QUARTERLY_CHECK.md:33 is process). |
| K09 seo-markup | GATE | _postbuild_check.py check_jsonld (DCI :231, LGM :204, GCI :267), check_speakable (DCI :555, LGM :466, GCI :451), check_title_meta_length (DCI :690, LGM :554, GCI :571); invoked by regen_all.sh DCI:129, LGM:218, GCI:132; exits via `sys.exit(1)` at _postbuild_check.py DCI:1135, LGM:823, GCI:843 | PORTABLE | JSON parse, speakable selector match and length only: canonical, og:image target existence, og:type per page type, duplicate @id, BreadcrumbList targets and sitemap completeness unchecked. |
| K10 template-residue | GATE | _postbuild_check.py:check_placeholders (DCI :163, LGM :140, GCI :168); invoked by regen_all.sh DCI:129, LGM:218, GCI:132; exits via `sys.exit(1)` at _postbuild_check.py DCI:1135, LGM:823, GCI:843 | PORTABLE | Catches token shapes only; referential residue ("the figures below", "read those two columns") and reader-visible internal notes in plain words pass. |
| K11 dead-file-or-code | PROCESS | canon METHODS/ARCHITECT_DISCIPLINE.md:84 (RULE 2 — no dead anything) | PORTABLE | No unused-file, unused-function or unreferenced-generator check in any build. |
| K12 generator-fragility | PROCESS | canon METHODS/PROPERTY_GENESIS.md:905 (output paths derive from the script location) | PORTABLE | regen_all.sh pre-flight (line 36, all three) checks syntax only; registry-consistency asserts exist in LGM/GCI _shared_components.py (e.g. LGM :3180, GCI :1898), not in DCI; nothing catches positional reads or case transforms. |
| K13 record-drift | PROCESS | canon METHODS/ARCHITECT_DISCIPLINE.md:1173 (state carried in prose instead of a checkable record) | PORTABLE | DCI-only denvercoloradoinsulation.com/ops/hooks/commit-msg checks Verify:/Result: trailers, is opt-in per clone (core.hooksPath) and does not read state docs or comments. |
| K14 ops-pipeline | PROCESS | canon METHODS/PROPERTY_GENESIS.md:1398 (ops/functional_proof.sh as launch gate) | PORTABLE | functional_proof.sh exists in all three ops/ but is not invoked by regen_all.sh or any ops/push-*.sh deploy script; hidden-field population, backups and dependency audits have no check. |
| K15 render-ux-a11y | PROCESS | canon METHODS/ARCHITECT_DISCIPLINE.md:1151 (functional assertion for rendered behaviour) and :1699 (two-viewport axe) | PORTABLE | Gate _postbuild_check.py:check_interactive_js (all three) proves JS present and parsed, not correct; keyboard checks are DCI check_keyboard_reachability (:824) and LGM check_scrollable_regions (:652) only; claim gate R6 reads JS source only. No input-bounds or output-sanity test. |
| K16 identity-misrepresentation | NONE | no check or canon method found | PORTABLE | Generator default exists in two of three: denvercoloradoinsulation.com/_shared_components.py:person_schema (:3814) and longmontcoloradoinsulation.com/_shared_components.py:person_schema (:5097) emit Organization; greeleycoloradoinsulation.com/_shared_components.py:person_schema (:3830) still emits "@type": "Person" (:3834). Contractor voice and relationship disclosure have nothing. |
| K17 fabricated-review-date | GATE | canon ops/claim_gate/claim_gate.py:rule_R8 (line 5442; "STALE REVIEW DATE", blocking; part (d) reads git log); invoked by denvercoloradoinsulation.com/regen_all.sh:223, longmontcoloradoinsulation.com/regen_all.sh:252, greeleycoloradoinsulation.com/regen_all.sh:178 (`ops/claim_gate.sh --brief`) | PORTABLE | Catches a date older than the last visible-text commit; cannot catch a date advanced with no review behind it ("Verified August 2026" bumped unverified). |
| K18 not-a-defect | NONE | no check or canon method found | PORTABLE | Nothing requires a row to prove its premise at intake; 245 rows in this class (237 C18 + 7 pending-task + 1 row-level override) are the triage cost. |
| K19 edit-residue | PROCESS | canon METHODS/CANDIDATE-do-not-scope-with-grep-over-html.md:160 (removal not complete until every promising sentence is found; CANDIDATE, not merged) | PORTABLE | Gate canon ops/claim_gate/claim_gate.py:rule_R10 (:6064, "DANGLING PROMISE", blocking) covers promises of figures only; doubled/welded words and orphaned fragments pass every check. |
| K20 prose-defect | NONE | no check; canon METHODS/QUARTERLY_CHECK.md:18 names rules NR1/NR2/NR4/NR7, which no canon file defines | PORTABLE | No prose read is required by any build; the quarterly read cites undefined rules. |
| K21 instrument-gap | PROCESS | canon METHODS/PROPERTY_GENESIS.md:1489 (an instrument answers a narrower question than the claim) and METHODS/ARCHITECT_DISCIPLINE.md:1147 (canary result recorded) | PORTABLE | `--canary` / `--controls` modes exist (_postbuild_check.py, _check_links.py, ops/superlative_scan.py) but no regen_all.sh invokes them; nothing fails when a check file exists that the build never calls. |
| K22 caveat-gap | NONE | no check or canon method found | PORTABLE | No registry ties a hedge or safety caveat to its claim; nothing measures caveat distance. |
| K23 template-misapplied | NONE | no portable check | PORTABLE | DCI-only needle lock denvercoloradoinsulation.com/_postbuild_check.py:check_health_safety_disqualifier (:923) covers one block on one page set; shared blocks carry no page-type applicability. |

**Counts.** DEFAULT 0 · GATE 7 · PROCESS 11 · NONE 5. PORTABLE 21 · LOCAL 2. No class is fully a generator DEFAULT; the defaults that exist (DCI/LGM Organization-typed editorial node, LGM AUTHORING_REQUIRED, `cite_inline()` raising on an unknown key) each cover a fragment of one class in some sites.

Rows by verdict of their class: GATE 316, PROCESS 612, NONE 316 (sum 1244).

---

## H3 Gap list

One item per PROCESS or NONE class. Order: PORTABLE+SCRIPT, PORTABLE+AGENT, LOCAL+SCRIPT, LOCAL+AGENT; within a group, by row count. Each item is the smallest default or check that would make the class a DEFAULT or GATE, and the planted input that must make it fail.

1. **K18 not-a-defect** (PORTABLE, SCRIPT, 245 rows, now NONE). Intake check on OPEN_LIST: a new row must carry a reproduce command that exits non-zero on the current tree (the premise is shown before the row is accepted). *Positive control:* Add a row whose reproduce command greps public/ for a string that is not there; the intake check must reject it.
2. **K13 record-drift** (PORTABLE, SCRIPT, 48 rows, now PROCESS). Check that every `path:line`, function name and commit hash cited in docs/board/ground-truth.md and in generator comments resolves (file exists, line exists, `git cat-file -e` succeeds). *Positive control:* Add a ground-truth line citing commit `deadbee` and `_shared_components.py:99999`; the check must exit 1 on both.
3. **K15 render-ux-a11y** (PORTABLE, SCRIPT, 39 rows, now PROCESS). Headless browser test per calculator: min-1, max+1, zero, negative and blank inputs must leave no NaN, Infinity, negative headline or out-of-range result; axe at 375 px and 1280 px. *Positive control:* Remove `min` from one calculator input and enter -5; the test must fail on the negative payback headline.
4. **K19 edit-residue** (PORTABLE, SCRIPT, 35 rows, now PROCESS). Rendered-text scan over the eight published surfaces for doubled words, welded tokens (lowercase run with no space where the generator joined two strings), empty or orphaned parentheticals, and headings with no following body text. *Positive control:* Plant "the the attic" in one page body and "measureair sealing" in one meta description; the scan must exit 1 on both.
5. **K14 ops-pipeline** (PORTABLE, SCRIPT, 22 rows, now PROCESS). Deploy script refuses to finish unless `ops/functional_proof.sh` exits 0 against staging; static build check that every hidden form field posted by a form is written by that page's JS. *Positive control:* Add `<input type="hidden" name="calc_output">` to a non-calculator form with no JS writer; the static check must exit 1.
6. **K16 identity-misrepresentation** (PORTABLE, SCRIPT, 19 rows, now NONE). Eight-surface scan for JSON-LD `"@type": "Person"` and a denylist of contractor-voice phrases ("our crew", "this crew", "we install", "neighborhoods we work in", "leaves our hands"); canon carries the list, the property config adds local forms. *Positive control:* Plant `"@type": "Person"` in one JSON-LD block and "our crew will start Monday" in one FAQ answer; both must fail the build.
7. **K11 dead-file-or-code** (PORTABLE, SCRIPT, 16 rows, now PROCESS). AST pass: every `_*.py` is imported by another module or invoked by regen_all.sh, and every top-level function in `_shared_components.py` is referenced at least once. *Positive control:* Add `_generate_unused.py` and an unreferenced `def _old_helper()`; the check must exit 1 naming both.
8. **K23 template-misapplied** (PORTABLE, SCRIPT, 11 rows, now NONE). Generator default: every shared block/FAQ/schema description carries an `applies_to` page-type set; the render helper raises when called for a page type outside it. *Positive control:* Call the attic DISQUALIFIER block from the crawl-space generator; generation must raise and regen_all.sh exit non-zero.
9. **K21 instrument-gap** (PORTABLE, SCRIPT, 10 rows, now PROCESS). regen_all.sh runs every check's own canary (`_postbuild_check.py --canary`, `_check_links.py` canary, `claim_gate.sh --canary`, `superlative_scan.py --controls`) before the real run, plus a meta-check that every `_*check*.py` and `ops/*scan*.py` is invoked by regen_all.sh. *Positive control:* Make `check_placeholders` return before scanning, and add an uninvoked `_new_check.py`; the canary step must exit 1 for the first and the meta-check for the second.
10. **K04 dead-or-misaimed-citation** (PORTABLE, SCRIPT, 8 rows, now PROCESS). Offline build check: every outbound cited URL has a citation-registry entry with `retrieved` within 92 days and a fingerprint; the existing network probe (`_check_links.py --check-outbound` plus staleness_watcher.py) runs on a schedule that fails loudly. *Positive control:* Cite a URL absent from the registry, and set one entry's `retrieved` to 2026-01-01; the build check must exit 1 on both.
11. **K12 generator-fragility** (PORTABLE, SCRIPT, 7 rows, now PROCESS). Generator default: all output paths from `os.path.dirname(os.path.abspath(__file__))`; AST check rejecting `expanduser`, literal absolute paths, `.title()`/`.lower()` on authored headings, and integer-index reads into page registries. *Positive control:* Add `os.path.expanduser("~/code/x/public")` to one generator and `SERVICE_PAGES[3]` to another; the check must exit 1 on both.
12. **K07 secret-in-tracked-file** (PORTABLE, SCRIPT, 5 rows, now PROCESS). Build step scanning `git ls-files` content for credential shapes (key=value with long hex/base64 values, private-key headers, bearer tokens) and dotted-quad IPv4 literals; exit 1 on any hit outside an allowlist file. *Positive control:* Commit a fixture `docs/_canary_secret.md` containing `HEALTH_TOKEN=` followed by 32 hex characters and a dotted-quad address; the step must exit 1 naming the file.
13. **K22 caveat-gap** (PORTABLE, SCRIPT, 4 rows, now NONE). Facts registry carries `hedge` and `safety_caveat` per claim; build check finds every rendered occurrence of the claim and fails if its hedge is not within N words (same block) or its required caveat is absent from the page. *Positive control:* Render the Atmos $575 figure with its verification note moved to the page footer, and a roof-raking instruction with no power-line warning; both must fail.
14. **K03 unsourced-or-wrong-claim** (PORTABLE, AGENT, 383 rows, now PROCESS). Facts registry entry per claim with a verbatim quote and a stored source snapshot; a script fails when a cited quote is not found in its snapshot, and an agent read rules whether each sentence says no more than its quote. *Positive control:* Change one figure in a cited sentence (e.g. 20% to 25%) while leaving its quote; the agent read must flag it, and altering the quote must fail the script half.
15. **K20 prose-defect** (PORTABLE, AGENT, 37 rows, now NONE). Define NR1/NR2/NR4/NR7 in canon; a read-receipt gate fails the build when a page's visible-text SHA-256 has no matching per-page read record, so every changed page gets a prose read. *Positive control:* Change one word on one page without a read record; the build must exit 1. The read itself must flag a planted "two scopes together ... is" agreement error.
16. **K02 stale-status** (LOCAL, SCRIPT, 39 rows, now PROCESS). Facts registry carries `status` and `next_review` per time-bound claim; build fails when today is past any `next_review` or a page states a status the registry does not hold. *Positive control:* Set one program's `next_review` to yesterday; the build must exit 1.

### Facts list a new property must carry

One record per sourced claim, in a committed registry the generators render from (never prose-only). Fields:

- `claim`: exact sentence or figure as it renders, plus a registry key. *Motivated by K03, K08.*
- `source`: URL or document identifier, document title, publisher. *Motivated by K03, K04.*
- `retrieved`: retrieval date (YYYY-MM-DD) and content fingerprint (hash of the quoted span). *Motivated by K02, K04.*
- `quote`: verbatim quoted line, and whether the page quotes or paraphrases it. *Motivated by K03 (R1 fabricated quotation).*
- `territory`: gas utility and electric utility, each per town; jurisdiction; code edition per town. *Motivated by K01.*
- `territory_evidence`: per town: the town's own source AND the utility filing; state NAMED, SPLIT or UNKNOWN; for an absence, why the list would have shown it. *Motivated by K01.*
- `status`: open / closed / waitlist / launched / unconfirmed, with the date it was last true. *Motivated by K02.*
- `next_review`: re-check date; the build fails after it. *Motivated by K02, K17.*
- `hedge`: text that must travel with the claim and the maximum distance from it. *Motivated by K22.*
- `safety_caveat`: required warning when the claim tells a reader to act. *Motivated by K22.*
- `applies_to`: page types and services the claim is true for. *Motivated by K23, K01.*
- `actor`: who performs or promises the thing: the site, a contractor, a utility, a program. *Motivated by K16.*
- `pages`: every page and surface that states it (body, title, meta, og, JSON-LD, llms.txt, embed, og-image). *Motivated by K01, K08, K19.*
- `dependents`: sentences that point at it ("current amounts are on ...") and counts that include it. *Motivated by K19, K08.*
- `superseded_by`: retired wording and the replacement key, fed to the retired-string lock. *Motivated by K02.*
- `verified_by`: commit hash and verification command of the last real review. *Motivated by K17, K13.*

---

## Appendix: row-to-class ledger

Generated from the two TSVs; 1244 rows. Canon rows are cited to `docs/board/OPEN_LIST.md`; site rows to their repo file and line.

| # | id | source | original class | final class |
|---:|---|---|---|---|
| 1 | DCI-F001 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C14 | K14 |
| 2 | DCI-F002 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C13 | K13 |
| 3 | DCI-F003 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C09 | K09 |
| 4 | DCI-F004 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C06 | K06 |
| 5 | DCI-F005 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 6 | DCI-F006 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C09 | K09 |
| 7 | DCI-F007 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 8 | DCI-F008 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C14 | K14 |
| 9 | DCI-F009 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C14 | K14 |
| 10 | DCI-F010 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 11 | DCI-F011 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 12 | DCI-F012 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | NEW:generator-fragility | K12 |
| 13 | DCI-F013 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 14 | DCI-F014 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C09 | K09 |
| 15 | DCI-F015 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C14 | K14 |
| 16 | DCI-F016 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C14 | K14 |
| 17 | DCI-F017 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C14 | K14 |
| 18 | DCI-F018 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C14 | K14 |
| 19 | DCI-F019 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C05 | K05 |
| 20 | DCI-F020 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 21 | DCI-F021 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C02 | K02 |
| 22 | DCI-F022 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 23 | DCI-F023 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C18 | K18 |
| 24 | DCI-F024 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C11 | K11 |
| 25 | DCI-F025 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C02 | K02 |
| 26 | DCI-F026 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C04 | K04 |
| 27 | DCI-F027 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C13 | K13 |
| 28 | DCI-F028 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C14 | K14 |
| 29 | DCI-F029 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C16 | K16 |
| 30 | DCI-F030 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C16 | K16 |
| 31 | DCI-F031 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 32 | DCI-F032 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C09 | K09 |
| 33 | DCI-F033 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 34 | DCI-F034 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 35 | DCI-F035 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C02 | K02 |
| 36 | DCI-F036 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 37 | DCI-F037 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 38 | DCI-F038 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 39 | DCI-F039 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C14 | K14 |
| 40 | DCI-F040 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 41 | DCI-F041 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C10 | K10 |
| 42 | DCI-F042 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C02 | K02 |
| 43 | DCI-F043 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 44 | DCI-F044 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 45 | DCI-F045 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C10 | K10 |
| 46 | DCI-F046 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 47 | DCI-F047 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C10 | K10 |
| 48 | DCI-F048 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 49 | DCI-F049 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 50 | DCI-F050 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C17 | K17 |
| 51 | DCI-F051 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 52 | DCI-F052 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C05 | K05 |
| 53 | DCI-F053 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C08 | K08 |
| 54 | DCI-F054 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 55 | DCI-F055 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 56 | DCI-F056 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 57 | DCI-F057 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 58 | DCI-F058 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 59 | DCI-F059 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 60 | DCI-F060 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 61 | DCI-F061 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 62 | DCI-F062 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 63 | DCI-F063 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 64 | DCI-F064 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 65 | DCI-F065 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 66 | DCI-F066 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 67 | DCI-F067 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 68 | DCI-F068 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 69 | DCI-F069 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 70 | DCI-F070 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 71 | DCI-F071 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 72 | DCI-F072 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 73 | DCI-F073 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C10 | K10 |
| 74 | DCI-F074 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 75 | DCI-F075 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 76 | DCI-F076 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 77 | DCI-F077 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 78 | DCI-F078 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 79 | DCI-F079 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 80 | DCI-F080 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 81 | DCI-F081 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 82 | DCI-F082 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 83 | DCI-F083 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C10 | K10 |
| 84 | DCI-F084 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 85 | DCI-F085 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 86 | DCI-F086 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C15 | K15 |
| 87 | DCI-F087 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C01 | K01 |
| 88 | DCI-F088 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C08 | K08 |
| 89 | DCI-F089 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C15 | K15 |
| 90 | DCI-F090 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 91 | DCI-F091 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | NEW:copy-craft | K20 |
| 92 | DCI-F092 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 93 | DCI-F093 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C11 | K11 |
| 94 | DCI-F094 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C10 | K10 |
| 95 | DCI-F095 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C08 | K08 |
| 96 | DCI-F096 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C10 | K10 |
| 97 | DCI-F097 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | NEW:copy-craft | K20 |
| 98 | DCI-F098 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 99 | DCI-F099 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C17 | K17 |
| 100 | DCI-F100 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | NEW:copy-craft | K20 |
| 101 | DCI-F101 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C10 | K10 |
| 102 | DCI-F102 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 103 | DCI-F103 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 104 | DCI-F104 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C17 | K17 |
| 105 | DCI-F105 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 106 | DCI-F106 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C02 | K02 |
| 107 | DCI-F107 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 108 | DCI-F108 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 109 | DCI-F109 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C15 | K15 |
| 110 | DCI-F110 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C08 | K08 |
| 111 | DCI-F111 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 112 | DCI-F112 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K15 | (override)
| 113 | DCI-F113 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C08 | K08 |
| 114 | DCI-F114 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C15 | K15 |
| 115 | DCI-F115 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C05 | K05 |
| 116 | DCI-F116 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C02 | K02 |
| 117 | DCI-F117 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 118 | DCI-F118 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C08 | K08 |
| 119 | DCI-F119 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | NEW:copy-craft | K20 |
| 120 | DCI-F120 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | NEW:copy-craft | K20 |
| 121 | DCI-F121 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 122 | DCI-F122 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 123 | DCI-F123 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 124 | DCI-F124 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 125 | DCI-F125 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C17 | K17 |
| 126 | DCI-F126 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 127 | DCI-F127 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C08 | K08 |
| 128 | DCI-F128 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C08 | K08 |
| 129 | DCI-F129 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C08 | K08 |
| 130 | DCI-F130 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 131 | DCI-F131 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 132 | DCI-F132 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 133 | DCI-F133 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C02 | K02 |
| 134 | DCI-F134 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 135 | DCI-F135 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 136 | DCI-F136 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C17 | K17 |
| 137 | DCI-F137 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C04 | K04 |
| 138 | DCI-F138 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 139 | DCI-F139 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C10 | K10 |
| 140 | DCI-F140 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C17 | K17 |
| 141 | DCI-F141 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 142 | DCI-F142 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C02 | K02 |
| 143 | DCI-F143 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 144 | DCI-F144 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 145 | DCI-F145 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C08 | K08 |
| 146 | DCI-F146 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C17 | K17 |
| 147 | DCI-F147 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C17 | K17 |
| 148 | DCI-F148 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C14 | K14 |
| 149 | DCI-F149 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 150 | DCI-F150 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C13 | K13 |
| 151 | LGM-F001 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C13 | K13 |
| 152 | LGM-F002 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C04 | K04 |
| 153 | LGM-F003 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C02 | K02 |
| 154 | LGM-F004 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C09 | K09 |
| 155 | LGM-F005 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C13 | K13 |
| 156 | LGM-F006 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C09 | K09 |
| 157 | LGM-F007 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C09 | K09 |
| 158 | LGM-F008 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C13 | K13 |
| 159 | LGM-F009 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C09 | K09 |
| 160 | LGM-F010 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C01 | K01 |
| 161 | LGM-F011 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C09 | K09 |
| 162 | LGM-F012 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C13 | K13 |
| 163 | LGM-F013 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C14 | K14 |
| 164 | LGM-F014 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | NEW:pending-task | K18 |
| 165 | LGM-F015 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | NEW:pending-task | K18 |
| 166 | LGM-F016 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | NEW:pending-task | K18 |
| 167 | LGM-F017 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C03 | K03 |
| 168 | LGM-F018 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C10 | K10 |
| 169 | LGM-F019 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C10 | K10 |
| 170 | LGM-F020 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | NEW:pending-task | K18 |
| 171 | LGM-F021 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C08 | K08 |
| 172 | LGM-F022 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C13 | K13 |
| 173 | LGM-F023 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | NEW:pending-task | K18 |
| 174 | LGM-F024 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C16 | K16 |
| 175 | LGM-F025 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | NEW:pending-task | K18 |
| 176 | LGM-F026 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C02 | K02 |
| 177 | LGM-F027 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C13 | K13 |
| 178 | LGM-F028 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C13 | K13 |
| 179 | GCI-F001 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C13 | K13 |
| 180 | GCI-F002 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C04 | K04 |
| 181 | GCI-F003 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C04 | K04 |
| 182 | GCI-F004 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C16 | K16 |
| 183 | GCI-F005 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C12 | K12 |
| 184 | GCI-F006 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C10 | K10 |
| 185 | GCI-F007 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C14 | K14 |
| 186 | GCI-F008 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C09 | K09 |
| 187 | GCI-F009 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C09 | K09 |
| 188 | GCI-F010 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C09 | K09 |
| 189 | GCI-F011 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C14 | K14 |
| 190 | GCI-F012 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C02 | K02 |
| 191 | GCI-F013 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C08 | K08 |
| 192 | GCI-F014 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C14 | K14 |
| 193 | GCI-F015 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C13 | K13 |
| 194 | GCI-F016 | canon docs/board/OPEN_LIST.md (GCI, NOT APPLICABLE) | C18 | K18 |
| 195 | GCI-F017 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C13 | K13 |
| 196 | GCI-010 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | NEW:pending-task | K18 |
| 197 | GCI-014 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C18 | K18 |
| 198 | GCI-016 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C18 | K18 |
| 199 | GCI-024 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C11 | K11 |
| 200 | GCI-027 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C11 | K11 |
| 201 | GCI-028 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C08 | K08 |
| 202 | GCI-030 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C13 | K13 |
| 203 | DCI-002 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C13 | K13 |
| 204 | DCI-003 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C02 | K02 |
| 205 | DCI-007 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 206 | DCI-014 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | NEW:missing-gate | K21 |
| 207 | DCI-016 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 208 | DCI-017 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C13 | K13 |
| 209 | DCI-020 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 210 | DCI-021 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 211 | DCI-023 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 212 | DCI-025 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | NEW:missing-gate | K21 |
| 213 | DCI-027 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 214 | DCI-028 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 215 | DCI-032 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | NEW:copy-craft | K20 |
| 216 | DCI-033 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C11 | K11 |
| 217 | DCI-039 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C13 | K13 |
| 218 | DCI-041 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 219 | DCI-045 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C08 | K08 |
| 220 | DCI-047 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 221 | DCI-049 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C15 | K15 |
| 222 | DCI-051 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 223 | DCI-052 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 224 | DCI-054 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 225 | DCI-055 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 226 | DCI-059 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 227 | DCI-061 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 228 | DCI-064 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 229 | DCI-065 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 230 | DCI-066 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 231 | DCI-068 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 232 | DCI-071 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 233 | DCI-073 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | NEW:copy-craft | K20 |
| 234 | DCI-074 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 235 | DCI-075 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 236 | DCI-076 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 237 | DCI-077 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C10 | K10 |
| 238 | DCI-082 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 239 | DCI-083 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C15 | K15 |
| 240 | DCI-084 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 241 | DCI-085 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C08 | K08 |
| 242 | DCI-086 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 243 | DCI-087 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 244 | DCI-088 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 245 | DCI-089 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 246 | DCI-090 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C02 | K02 |
| 247 | DCI-091 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C02 | K02 |
| 248 | DCI-092 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C02 | K02 |
| 249 | DCI-093 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | NEW:copy-craft | K20 |
| 250 | DCI-094 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 251 | DCI-097 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 252 | DCI-098 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 253 | DCI-099 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C08 | K08 |
| 254 | DCI-100 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C08 | K08 |
| 255 | DCI-101 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C08 | K08 |
| 256 | DCI-104 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 257 | DCI-105 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 258 | DCI-107 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 259 | DCI-109 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 260 | DCI-114 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 261 | DCI-115 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 262 | DCI-120 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C10 | K10 |
| 263 | DCI-121 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 264 | DCI-126 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C08 | K08 |
| 265 | DCI-128 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C13 | K13 |
| 266 | DCI-132 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C10 | K10 |
| 267 | DCI-134 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C11 | K11 |
| 268 | LGM-005 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | NEW:generator-fragility | K12 |
| 269 | LGM-010 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | NEW:missing-gate | K21 |
| 270 | LGM-013 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | NEW:copy-craft | K20 |
| 271 | LGM-014 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | NEW:generator-fragility | K12 |
| 272 | LGM-015 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C09 | K09 |
| 273 | LGM-016 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C16 | K16 |
| 274 | LGM-018 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C13 | K13 |
| 275 | LGM-024 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C11 | K11 |
| 276 | LGM-030 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C01 | K01 |
| 277 | LGM-031 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C13 | K13 |
| 278 | LGM-033 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C03 | K03 |
| 279 | LGM-036 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C08 | K08 |
| 280 | LGM-037 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C09 | K09 |
| 281 | LGM-042 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C03 | K03 |
| 282 | LGM-045 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C08 | K08 |
| 283 | DCI-008 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 284 | DCI-009 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 285 | DCI-010 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | NEW:generator-fragility | K12 |
| 286 | DCI-012 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | NEW:generator-fragility | K12 |
| 287 | DCI-013 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C11 | K11 |
| 288 | DCI-015 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C13 | K13 |
| 289 | DCI-022 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C09 | K09 |
| 290 | DCI-034 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C17 | K17 |
| 291 | DCI-035 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 292 | DCI-040 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 293 | DCI-042 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 294 | DCI-046 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 295 | DCI-048 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 296 | DCI-050 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 297 | DCI-053 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | NEW:copy-craft | K20 |
| 298 | DCI-056 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 299 | DCI-057 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 300 | DCI-058 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C08 | K08 |
| 301 | DCI-060 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 302 | DCI-067 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 303 | DCI-069 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C08 | K08 |
| 304 | DCI-070 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 305 | DCI-072 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 306 | DCI-078 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 307 | DCI-079 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 308 | DCI-080 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 309 | DCI-095 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C13 | K13 |
| 310 | DCI-096 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 311 | DCI-102 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 312 | DCI-103 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 313 | DCI-106 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 314 | DCI-108 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 315 | DCI-110 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 316 | DCI-111 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 317 | DCI-112 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 318 | DCI-113 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 319 | DCI-116 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 320 | DCI-117 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 321 | DCI-118 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 322 | DCI-119 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C09 | K09 |
| 323 | DCI-122 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C11 | K11 |
| 324 | DCI-123 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C11 | K11 |
| 325 | DCI-124 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 326 | DCI-125 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C11 | K11 |
| 327 | DCI-127 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C13 | K13 |
| 328 | DCI-024 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 329 | DCI-029 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 330 | DCI-030 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 331 | DCI-031 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 332 | DCI-036 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 333 | DCI-037 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 334 | DCI-038 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 335 | DCI-043 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 336 | DCI-044 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 337 | DCI-062 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 338 | DCI-063 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C03 | K03 |
| 339 | DCI-081 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 340 | DCI-129 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 341 | DCI-131 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C15 | K15 |
| 342 | LGM-001 | canon docs/board/OPEN_LIST.md (LGM, NOT APPLICABLE) | C18 | K18 |
| 343 | LGM-002 | canon docs/board/OPEN_LIST.md (LGM, NOT APPLICABLE) | C18 | K18 |
| 344 | LGM-008 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C14 | K14 |
| 345 | LGM-038 | canon docs/board/OPEN_LIST.md (LGM, NOT APPLICABLE) | C18 | K18 |
| 346 | LGM-039 | canon docs/board/OPEN_LIST.md (LGM, NOT APPLICABLE) | C18 | K18 |
| 347 | LGM-043 | canon docs/board/OPEN_LIST.md (LGM, NOT APPLICABLE) | C18 | K18 |
| 348 | LGM-054 | canon docs/board/OPEN_LIST.md (LGM, NOT APPLICABLE) | C18 | K18 |
| 349 | GCI-013 | canon docs/board/OPEN_LIST.md (GCI, NOT APPLICABLE) | C18 | K18 |
| 350 | GCI-032 | canon docs/board/OPEN_LIST.md (GCI, NOT APPLICABLE) | C18 | K18 |
| 351 | DCI-130 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C07 | K07 |
| 352 | DCI-133 | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C07 | K07 |
| 353 | GCI-033 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C07 | K07 |
| 354 | LGM-009 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C14 | K14 |
| 355 | LGM-044 | canon docs/board/OPEN_LIST.md (LGM, ALREADY FIXED) | C07 | K07 |
| 356 | DCI-143 | canon docs/board/OPEN_LIST.md (DCI, NOT APPLICABLE) | C18 | K18 |
| 357 | GCI-036 | canon docs/board/OPEN_LIST.md (GCI, ALREADY FIXED) | C12 | K12 |
| 358 | DCI-144A | canon docs/board/OPEN_LIST.md (DCI, ALREADY FIXED) | C14 | K14 |
| 359 | DCI-gD-D-2 | DCI docs/audits/read-2026-08-25/groupD.md:51 | NEW:edit-residue | K19 |
| 360 | DCI-gD-D-4 | DCI docs/audits/read-2026-08-25/groupD.md:168 | NEW:edit-residue | K19 |
| 361 | DCI-gD-D-5 | DCI docs/audits/read-2026-08-25/groupD.md:230 | C03 | K03 |
| 362 | DCI-gD-D-6 | DCI docs/audits/read-2026-08-25/groupD.md:301 | NEW:edit-residue | K19 |
| 363 | DCI-gD-D-7 | DCI docs/audits/read-2026-08-25/groupD.md:335 | C03 | K03 |
| 364 | DCI-gD-D-8 | DCI docs/audits/read-2026-08-25/groupD.md:354 | C08 | K08 |
| 365 | DCI-gD-D-9 | DCI docs/audits/read-2026-08-25/groupD.md:376 | C08 | K08 |
| 366 | DCI-gD-D-10 | DCI docs/audits/read-2026-08-25/groupD.md:480 | C03 | K03 |
| 367 | DCI-gD-D-11 | DCI docs/audits/read-2026-08-25/groupD.md:510 | C03 | K03 |
| 368 | DCI-gD-D-12 | DCI docs/audits/read-2026-08-25/groupD.md:562 | C01 | K01 |
| 369 | DCI-gD-D-13 | DCI docs/audits/read-2026-08-25/groupD.md:585 | C08 | K08 |
| 370 | DCI-gD-D-14 | DCI docs/audits/read-2026-08-25/groupD.md:608 | C03 | K03 |
| 371 | DCI-gD-D-16 | DCI docs/audits/read-2026-08-25/groupD.md:679 | C08 | K08 |
| 372 | DCI-gD-O-1 | DCI docs/audits/read-2026-08-25/groupD.md:747 | NEW:edit-residue | K19 |
| 373 | DCI-gE-E-2 | DCI docs/audits/read-2026-08-25/groupE.md:75 | C10 | K10 |
| 374 | DCI-gE-E-3 | DCI docs/audits/read-2026-08-25/groupE.md:95 | C08 | K08 |
| 375 | DCI-gE-E-4 | DCI docs/audits/read-2026-08-25/groupE.md:124 | C05 | K05 |
| 376 | DCI-gE-E-5 | DCI docs/audits/read-2026-08-25/groupE.md:176 | C03 | K03 |
| 377 | DCI-gE-E-6 | DCI docs/audits/read-2026-08-25/groupE.md:206 | C02 | K02 |
| 378 | DCI-gE-E-7 | DCI docs/audits/read-2026-08-25/groupE.md:233 | C08 | K08 |
| 379 | DCI-gE-E-8 | DCI docs/audits/read-2026-08-25/groupE.md:255 | NEW:edit-residue | K20 | (override)
| 380 | DCI-gE-E-9 | DCI docs/audits/read-2026-08-25/groupE.md:266 | C03 | K03 |
| 381 | DCI-gE-E-11 | DCI docs/audits/read-2026-08-25/groupE.md:363 | NEW:edit-residue | K19 |
| 382 | DCI-gE-E-13 | DCI docs/audits/read-2026-08-25/groupE.md:416 | C03 | K03 |
| 383 | DCI-gE-E-15 | DCI docs/audits/read-2026-08-25/groupE.md:461 | NEW:edit-residue | K19 |
| 384 | DCI-gE-E-16 | DCI docs/audits/read-2026-08-25/groupE.md:503 | C03 | K03 |
| 385 | DCI-gE-E-19 | DCI docs/audits/read-2026-08-25/groupE.md:577 | C03 | K03 |
| 386 | DCI-gE-E-20 | DCI docs/audits/read-2026-08-25/groupE.md:591 | C10 | K10 |
| 387 | DCI-gE-E-21 | DCI docs/audits/read-2026-08-25/groupE.md:617 | C08 | K08 |
| 388 | DCI-gE-E-22 | DCI docs/audits/read-2026-08-25/groupE.md:674 | C03 | K03 |
| 389 | DCI-gE-E-23 | DCI docs/audits/read-2026-08-25/groupE.md:692 | C08 | K08 |
| 390 | DCI-gE-E-24 | DCI docs/audits/read-2026-08-25/groupE.md:711 | C03 | K03 |
| 391 | DCI-gE-E-25 | DCI docs/audits/read-2026-08-25/groupE.md:733 | NEW:edit-residue | K19 |
| 392 | DCI-gE-E-26 | DCI docs/audits/read-2026-08-25/groupE.md:801 | C03 | K03 |
| 393 | DCI-gE-E-28 | DCI docs/audits/read-2026-08-25/groupE.md:882 | C08 | K08 |
| 394 | DCI-gE-E-29 | DCI docs/audits/read-2026-08-25/groupE.md:907 | C03 | K03 |
| 395 | DCI-gE-E-30 | DCI docs/audits/read-2026-08-25/groupE.md:1024 | C03 | K03 |
| 396 | DCI-gE-E-31 | DCI docs/audits/read-2026-08-25/groupE.md:1065 | C03 | K03 |
| 397 | DCI-gE-E-32 | DCI docs/audits/read-2026-08-25/groupE.md:1084 | C03 | K03 |
| 398 | DCI-gE-E-33 | DCI docs/audits/read-2026-08-25/groupE.md:1107 | C03 | K03 |
| 399 | DCI-gE-CC-1 | DCI docs/audits/read-2026-08-25/groupE.md:1177 | C13 | K13 |
| 400 | DCI-gF-F-2 | DCI docs/audits/read-2026-08-25/groupF.md:79 | NEW:edit-residue | K19 |
| 401 | DCI-gF-F-3 | DCI docs/audits/read-2026-08-25/groupF.md:105 | C03 | K03 |
| 402 | DCI-gF-F-5a | DCI docs/audits/read-2026-08-25/groupF.md:164 | C08 | K08 |
| 403 | DCI-gF-F-5b | DCI docs/audits/read-2026-08-25/groupF.md:164 | C10 | K10 |
| 404 | DCI-gF-F-6 | DCI docs/audits/read-2026-08-25/groupF.md:188 | C08 | K08 |
| 405 | DCI-gF-F-7 | DCI docs/audits/read-2026-08-25/groupF.md:222 | C03 | K03 |
| 406 | DCI-gF-F-8 | DCI docs/audits/read-2026-08-25/groupF.md:271 | C08 | K08 |
| 407 | DCI-gF-F-9 | DCI docs/audits/read-2026-08-25/groupF.md:302 | C08 | K08 |
| 408 | DCI-gF-F-10 | DCI docs/audits/read-2026-08-25/groupF.md:318 | C03 | K03 |
| 409 | DCI-gF-F-11 | DCI docs/audits/read-2026-08-25/groupF.md:341 | C03 | K03 |
| 410 | DCI-gF-F-12 | DCI docs/audits/read-2026-08-25/groupF.md:361 | C03 | K03 |
| 411 | DCI-gF-F-13 | DCI docs/audits/read-2026-08-25/groupF.md:412 | C03 | K03 |
| 412 | DCI-gF-F-14 | DCI docs/audits/read-2026-08-25/groupF.md:443 | C08 | K08 |
| 413 | DCI-gF-F-15 | DCI docs/audits/read-2026-08-25/groupF.md:458 | C08 | K08 |
| 414 | DCI-gF-F-16 | DCI docs/audits/read-2026-08-25/groupF.md:473 | NEW:malformed-prose | K20 |
| 415 | DCI-gF-F-17 | DCI docs/audits/read-2026-08-25/groupF.md:486 | C03 | K03 |
| 416 | DCI-gF-F-18 | DCI docs/audits/read-2026-08-25/groupF.md:501 | C03 | K03 |
| 417 | DCI-gF-F-19 | DCI docs/audits/read-2026-08-25/groupF.md:553 | NEW:edit-residue | K19 |
| 418 | DCI-gF-F-20 | DCI docs/audits/read-2026-08-25/groupF.md:578 | C08 | K08 |
| 419 | DCI-gF-F-21 | DCI docs/audits/read-2026-08-25/groupF.md:602 | C08 | K08 |
| 420 | DCI-gF-F-22 | DCI docs/audits/read-2026-08-25/groupF.md:625 | C03 | K03 |
| 421 | DCI-gF-F-23 | DCI docs/audits/read-2026-08-25/groupF.md:643 | C08 | K08 |
| 422 | DCI-gF-F-25 | DCI docs/audits/read-2026-08-25/groupF.md:743 | C08 | K08 |
| 423 | DCI-gF-F-26a | DCI docs/audits/read-2026-08-25/groupF.md:758 | C03 | K03 |
| 424 | DCI-gF-F-27 | DCI docs/audits/read-2026-08-25/groupF.md:801 | C08 | K08 |
| 425 | DCI-gF-F-28a | DCI docs/audits/read-2026-08-25/groupF.md:856 | C03 | K03 |
| 426 | DCI-gF-F-28b | DCI docs/audits/read-2026-08-25/groupF.md:856 | C08 | K08 |
| 427 | DCI-gF-F-29 | DCI docs/audits/read-2026-08-25/groupF.md:882 | C03 | K03 |
| 428 | DCI-gF-F-30 | DCI docs/audits/read-2026-08-25/groupF.md:895 | NEW:edit-residue | K19 |
| 429 | DCI-gF-F-31 | DCI docs/audits/read-2026-08-25/groupF.md:912 | NEW:template-misapplied | K23 |
| 430 | DCI-gF-F-32 | DCI docs/audits/read-2026-08-25/groupF.md:949 | C06 | K06 |
| 431 | DCI-gG-G-1 | DCI docs/audits/read-2026-08-25/groupG.md:23 | C08 | K08 |
| 432 | DCI-gG-G-2 | DCI docs/audits/read-2026-08-25/groupG.md:160 | C15 | K15 |
| 433 | DCI-gG-G-3 | DCI docs/audits/read-2026-08-25/groupG.md:193 | C08 | K08 |
| 434 | DCI-gG-G-4 | DCI docs/audits/read-2026-08-25/groupG.md:286 | C03 | K03 |
| 435 | DCI-gG-G-7 | DCI docs/audits/read-2026-08-25/groupG.md:413 | NEW:edit-residue | K19 |
| 436 | DCI-gG-G-8 | DCI docs/audits/read-2026-08-25/groupG.md:504 | C08 | K08 |
| 437 | DCI-gG-G-9 | DCI docs/audits/read-2026-08-25/groupG.md:566 | C08 | K08 |
| 438 | DCI-gG-G-10 | DCI docs/audits/read-2026-08-25/groupG.md:609 | C03 | K03 |
| 439 | DCI-gG-G-11 | DCI docs/audits/read-2026-08-25/groupG.md:698 | C03 | K03 |
| 440 | DCI-gG-G-12a | DCI docs/audits/read-2026-08-25/groupG.md:731 | C15 | K15 |
| 441 | DCI-gG-G-12b | DCI docs/audits/read-2026-08-25/groupG.md:731 | C03 | K03 |
| 442 | DCI-gG-G-14 | DCI docs/audits/read-2026-08-25/groupG.md:805 | C15 | K15 |
| 443 | DCI-gG-G-15 | DCI docs/audits/read-2026-08-25/groupG.md:843 | C15 | K15 |
| 444 | DCI-gG-G-16 | DCI docs/audits/read-2026-08-25/groupG.md:887 | C03 | K03 |
| 445 | DCI-gG-G-17 | DCI docs/audits/read-2026-08-25/groupG.md:938 | C03 | K03 |
| 446 | DCI-gG-G-18 | DCI docs/audits/read-2026-08-25/groupG.md:979 | C05 | K05 |
| 447 | DCI-gG-G-19 | DCI docs/audits/read-2026-08-25/groupG.md:1059 | C03 | K03 |
| 448 | DCI-gG-G-20 | DCI docs/audits/read-2026-08-25/groupG.md:1090 | C03 | K03 |
| 449 | DCI-gG-G-21 | DCI docs/audits/read-2026-08-25/groupG.md:1121 | C08 | K08 |
| 450 | DCI-gG-G-24 | DCI docs/audits/read-2026-08-25/groupG.md:1261 | C08 | K08 |
| 451 | DCI-gA-AS-1 | DCI docs/audits/read-2026-08-25/groupA.md:160 | C08 | K08 |
| 452 | DCI-gA-AS-2 | DCI docs/audits/read-2026-08-25/groupA.md:173 | NEW:edit-residue | K19 |
| 453 | DCI-gA-AS-3 | DCI docs/audits/read-2026-08-25/groupA.md:185 | C03 | K03 |
| 454 | DCI-gA-AS-4 | DCI docs/audits/read-2026-08-25/groupA.md:198 | C03 | K03 |
| 455 | DCI-gA-AS-5 | DCI docs/audits/read-2026-08-25/groupA.md:212 | NEW:edit-residue | K19 |
| 456 | DCI-gA-AS-6 | DCI docs/audits/read-2026-08-25/groupA.md:224 | C03 | K03 |
| 457 | DCI-gA-CC-3 | DCI docs/audits/read-2026-08-25/groupA.md:322 | NEW:template-misapplied | K23 |
| 458 | DCI-gA-AIC-1 | DCI docs/audits/read-2026-08-25/groupA.md:394 | C03 | K03 |
| 459 | DCI-gA-AM-2 | DCI docs/audits/read-2026-08-25/groupA.md:487 | C08 | K08 |
| 460 | DCI-gA-AM-4 | DCI docs/audits/read-2026-08-25/groupA.md:511 | NEW:edit-residue | K19 |
| 461 | DCI-gA-AV-3 | DCI docs/audits/read-2026-08-25/groupA.md:573 | C08 | K08 |
| 462 | DCI-gA-BI-1 | DCI docs/audits/read-2026-08-25/groupA.md:623 | C08 | K08 |
| 463 | DCI-gA-BI-2 | DCI docs/audits/read-2026-08-25/groupA.md:638 | C08 | K08 |
| 464 | DCI-gA-BI-3 | DCI docs/audits/read-2026-08-25/groupA.md:651 | C03 | K03 |
| 465 | DCI-gA-CF-1 | DCI docs/audits/read-2026-08-25/groupA.md:699 | C08 | K08 |
| 466 | DCI-gA-CF-4 | DCI docs/audits/read-2026-08-25/groupA.md:736 | C08 | K08 |
| 467 | DCI-pa-about-F13 | DCI docs/audits/phase-a-rows/about.html.md:162 | C03 | K03 |
| 468 | DCI-gH-H-1 | DCI docs/audits/read-2026-08-25/groupH.md:62 | C08 | K08 |
| 469 | DCI-gH-H-2 | DCI docs/audits/read-2026-08-25/groupH.md:92 | C03 | K03 |
| 470 | DCI-gH-H-3 | DCI docs/audits/read-2026-08-25/groupH.md:117 | C15 | K15 |
| 471 | DCI-gH-H-4 | DCI docs/audits/read-2026-08-25/groupH.md:173 | C08 | K08 |
| 472 | DCI-gH-H-7 | DCI docs/audits/read-2026-08-25/groupH.md:265 | C03 | K03 |
| 473 | DCI-gH-H-9 | DCI docs/audits/read-2026-08-25/groupH.md:351 | C08 | K08 |
| 474 | DCI-gH-H-11 | DCI docs/audits/read-2026-08-25/groupH.md:438 | C08 | K08 |
| 475 | DCI-gH-H-12 | DCI docs/audits/read-2026-08-25/groupH.md:475 | C03 | K03 |
| 476 | DCI-gH-H-13 | DCI docs/audits/read-2026-08-25/groupH.md:504 | C03 | K03 |
| 477 | DCI-gH-H-14 | DCI docs/audits/read-2026-08-25/groupH.md:529 | C08 | K08 |
| 478 | DCI-gH-H-14b | DCI docs/audits/read-2026-08-25/groupH.md:554 | C03 | K03 |
| 479 | DCI-gH-H-15 | DCI docs/audits/read-2026-08-25/groupH.md:586 | C17 | K17 |
| 480 | DCI-gH-H-16 | DCI docs/audits/read-2026-08-25/groupH.md:633 | NEW:edit-residue | K19 |
| 481 | DCI-gH-H-17 | DCI docs/audits/read-2026-08-25/groupH.md:671 | NEW:edit-residue | K19 |
| 482 | DCI-gH-H-18 | DCI docs/audits/read-2026-08-25/groupH.md:705 | C17 | K17 |
| 483 | DCI-gH-H-20 | DCI docs/audits/read-2026-08-25/groupH.md:789 | C08 | K08 |
| 484 | DCI-gH-H-22 | DCI docs/audits/read-2026-08-25/groupH.md:909 | NEW:edit-residue | K19 |
| 485 | DCI-gH-H-23 | DCI docs/audits/read-2026-08-25/groupH.md:941 | C17 | K17 |
| 486 | DCI-gH-H-24 | DCI docs/audits/read-2026-08-25/groupH.md:980 | C03 | K03 |
| 487 | DCI-gH-H-25a | DCI docs/audits/read-2026-08-25/groupH.md:1012 | NEW:edit-residue | K19 |
| 488 | DCI-gH-H-25b | DCI docs/audits/read-2026-08-25/groupH.md:1023 | C02 | K02 |
| 489 | DCI-gH-H-26 | DCI docs/audits/read-2026-08-25/groupH.md:1077 | C01 | K01 |
| 490 | DCI-gH-H-27 | DCI docs/audits/read-2026-08-25/groupH.md:1123 | C16 | K16 |
| 491 | DCI-gH-H-29 | DCI docs/audits/read-2026-08-25/groupH.md:1192 | C08 | K08 |
| 492 | DCI-gH-H-30 | DCI docs/audits/read-2026-08-25/groupH.md:1225 | NEW:malformed-prose | K20 |
| 493 | DCI-q1-1 | DCI docs/audits/quarterly-2026-10/q1-rebates.md:113 | C02 | K02 |
| 494 | DCI-q1-2 | DCI docs/audits/quarterly-2026-10/q1-rebates.md:121 | C02 | K02 |
| 495 | DCI-q1-3 | DCI docs/audits/quarterly-2026-10/q1-rebates.md:129 | C02 | K02 |
| 496 | DCI-q2-1 | DCI docs/audits/quarterly-2026-10/q2-codes.md:65 | C03 | K03 |
| 497 | DCI-q7-1 | DCI docs/audits/quarterly-2026-10/q7-search.md:91 | C05 | K05 |
| 498 | DCI-q7-2 | DCI docs/audits/quarterly-2026-10/q7-search.md:121 | C13 | K13 |
| 499 | DCI-k28-1 | DCI docs/audits/quarterly-2026-10/k28-sweep.md:38 | C02 | K02 |
| 500 | DCI-k28-2 | DCI docs/audits/quarterly-2026-10/k28-sweep.md:102 | C13 | K13 |
| 501 | DCI-gC-ICE-2 | DCI docs/audits/read-2026-08-25/groupC.md:76 | C02 | K02 |
| 502 | DCI-gC-ICE-5 | DCI docs/audits/read-2026-08-25/groupC.md:124 | NEW:malformed-prose | K20 |
| 503 | DCI-gC-IDX-1 | DCI docs/audits/read-2026-08-25/groupC.md:175 | NEW:edit-residue | K19 |
| 504 | DCI-gC-IDX-2 | DCI docs/audits/read-2026-08-25/groupC.md:205 | C08 | K08 |
| 505 | DCI-gC-IDX-3 | DCI docs/audits/read-2026-08-25/groupC.md:224 | NEW:edit-residue | K19 |
| 506 | DCI-gC-IDX-4 | DCI docs/audits/read-2026-08-25/groupC.md:240 | C03 | K03 |
| 507 | DCI-gC-SUB-1 | DCI docs/audits/read-2026-08-25/groupC.md:281 | NEW:edit-residue | K19 |
| 508 | DCI-gC-SUB-2 | DCI docs/audits/read-2026-08-25/groupC.md:314 | C03 | K03 |
| 509 | DCI-gC-SUB-3 | DCI docs/audits/read-2026-08-25/groupC.md:334 | NEW:edit-residue | K19 |
| 510 | DCI-gC-SUB-4 | DCI docs/audits/read-2026-08-25/groupC.md:352 | C08 | K08 |
| 511 | DCI-gC-SUB-5 | DCI docs/audits/read-2026-08-25/groupC.md:370 | C06 | K06 |
| 512 | DCI-gC-SUB-6 | DCI docs/audits/read-2026-08-25/groupC.md:384 | C03 | K03 |
| 513 | DCI-gC-SUB-7 | DCI docs/audits/read-2026-08-25/groupC.md:403 | C02 | K02 |
| 514 | DCI-gC-SUB-8 | DCI docs/audits/read-2026-08-25/groupC.md:420 | C10 | K10 |
| 515 | DCI-gC-SUB-9 | DCI docs/audits/read-2026-08-25/groupC.md:431 | C08 | K08 |
| 516 | DCI-gC-BDT-1 | DCI docs/audits/read-2026-08-25/groupC.md:475 | C03 | K03 |
| 517 | DCI-gC-ATT-1 | DCI docs/audits/read-2026-08-25/groupC.md:576 | NEW:edit-residue | K19 |
| 518 | DCI-gC-ATT-2 | DCI docs/audits/read-2026-08-25/groupC.md:595 | C08 | K08 |
| 519 | DCI-gC-ATT-4 | DCI docs/audits/read-2026-08-25/groupC.md:630 | C08 | K08 |
| 520 | DCI-gC-BLI-1 | DCI docs/audits/read-2026-08-25/groupC.md:679 | C08 | K08 |
| 521 | DCI-gC-BLI-2 | DCI docs/audits/read-2026-08-25/groupC.md:697 | C03 | K03 |
| 522 | DCI-gC-BLI-4 | DCI docs/audits/read-2026-08-25/groupC.md:729 | C08 | K08 |
| 523 | DCI-gC-CAT-1 | DCI docs/audits/read-2026-08-25/groupC.md:773 | C08 | K08 |
| 524 | DCI-gC-CAT-3 | DCI docs/audits/read-2026-08-25/groupC.md:819 | NEW:template-misapplied | K23 |
| 525 | DCI-gC-CAT-4 | DCI docs/audits/read-2026-08-25/groupC.md:838 | C03 | K03 |
| 526 | DCI-gC-IDX-6 | DCI docs/audits/read-2026-08-25/groupC.md:874 | C03 | K03 |
| 527 | DCI-pa-ice-A1-2 | DCI docs/audits/phase-a-rows/ice-dams-denver.html.md:107 | NEW:malformed-prose | K20 |
| 528 | DCI-pa-ice-A1-3 | DCI docs/audits/phase-a-rows/ice-dams-denver.html.md:114 | NEW:malformed-prose | K20 |
| 529 | DCI-pa-ice-A2-1 | DCI docs/audits/phase-a-rows/ice-dams-denver.html.md:133 | C03 | K03 |
| 530 | DCI-pa-ice-A2-2 | DCI docs/audits/phase-a-rows/ice-dams-denver.html.md:140 | C03 | K03 |
| 531 | DCI-pa-ice-A2-4 | DCI docs/audits/phase-a-rows/ice-dams-denver.html.md:154 | C03 | K03 |
| 532 | DCI-pa-ice-A2-5 | DCI docs/audits/phase-a-rows/ice-dams-denver.html.md:161 | C03 | K03 |
| 533 | DCI-pa-ice-A2-6 | DCI docs/audits/phase-a-rows/ice-dams-denver.html.md:168 | C03 | K03 |
| 534 | DCI-pa-ice-A2-7 | DCI docs/audits/phase-a-rows/ice-dams-denver.html.md:175 | C03 | K03 |
| 535 | DCI-pa-ice-A2-9 | DCI docs/audits/phase-a-rows/ice-dams-denver.html.md:189 | C03 | K03 |
| 536 | DCI-pa-ice-A3-1 | DCI docs/audits/phase-a-rows/ice-dams-denver.html.md:200 | C03 | K03 |
| 537 | DCI-pa-ice-A3-2 | DCI docs/audits/phase-a-rows/ice-dams-denver.html.md:207 | C08 | K08 |
| 538 | DCI-pa-index-A1-1 | DCI docs/audits/phase-a-rows/index.html.md:100 | NEW:edit-residue | K19 |
| 539 | DCI-pa-index-A1-3 | DCI docs/audits/phase-a-rows/index.html.md:115 | C06 | K06 |
| 540 | DCI-pa-index-A2-1 | DCI docs/audits/phase-a-rows/index.html.md:126 | C03 | K03 |
| 541 | DCI-pa-index-A2-3 | DCI docs/audits/phase-a-rows/index.html.md:140 | C03 | K03 |
| 542 | DCI-pa-index-A2-4 | DCI docs/audits/phase-a-rows/index.html.md:148 | C03 | K03 |
| 543 | DCI-pa-index-A2-5 | DCI docs/audits/phase-a-rows/index.html.md:155 | C03 | K03 |
| 544 | DCI-pa-index-A2-6 | DCI docs/audits/phase-a-rows/index.html.md:163 | C03 | K03 |
| 545 | DCI-pa-index-A2-7 | DCI docs/audits/phase-a-rows/index.html.md:171 | C03 | K03 |
| 546 | DCI-pa-index-A2-9 | DCI docs/audits/phase-a-rows/index.html.md:186 | C03 | K03 |
| 547 | DCI-pa-index-A2-10 | DCI docs/audits/phase-a-rows/index.html.md:193 | C03 | K03 |
| 548 | DCI-pa-index-A2-11 | DCI docs/audits/phase-a-rows/index.html.md:200 | C03 | K03 |
| 549 | DCI-pa-index-A2-12 | DCI docs/audits/phase-a-rows/index.html.md:207 | C03 | K03 |
| 550 | DCI-pa-index-A3-2 | DCI docs/audits/phase-a-rows/index.html.md:227 | C08 | K08 |
| 551 | DCI-pa-index-A3-4 | DCI docs/audits/phase-a-rows/index.html.md:244 | C08 | K08 |
| 552 | DCI-pa-index-A3-8 | DCI docs/audits/phase-a-rows/index.html.md:308 | C08 | K08 |
| 553 | DCI-pa-index-A3-9 | DCI docs/audits/phase-a-rows/index.html.md:316 | C08 | K08 |
| 554 | DCI-pa-index-A4-2 | DCI docs/audits/phase-a-rows/index.html.md:335 | C03 | K03 |
| 555 | DCI-pa-arv-A1-2 | DCI docs/audits/phase-a-rows/insulation-arvada.html.md:127 | C06 | K06 |
| 556 | DCI-pa-arv-A1-3 | DCI docs/audits/phase-a-rows/insulation-arvada.html.md:134 | C01 | K01 |
| 557 | DCI-pa-arv-A2-1 | DCI docs/audits/phase-a-rows/insulation-arvada.html.md:152 | C03 | K03 |
| 558 | DCI-pa-arv-A2-3 | DCI docs/audits/phase-a-rows/insulation-arvada.html.md:166 | C03 | K03 |
| 559 | DCI-pa-arv-A2-4 | DCI docs/audits/phase-a-rows/insulation-arvada.html.md:174 | C03 | K03 |
| 560 | DCI-pa-arv-A2-6 | DCI docs/audits/phase-a-rows/insulation-arvada.html.md:188 | C03 | K03 |
| 561 | DCI-pa-arv-A2-7 | DCI docs/audits/phase-a-rows/insulation-arvada.html.md:195 | C03 | K03 |
| 562 | DCI-pa-arv-A2-8 | DCI docs/audits/phase-a-rows/insulation-arvada.html.md:202 | C03 | K03 |
| 563 | DCI-pa-arv-A3-2 | DCI docs/audits/phase-a-rows/insulation-arvada.html.md:222 | C08 | K08 |
| 564 | DCI-pa-arv-A4-1 | DCI docs/audits/phase-a-rows/insulation-arvada.html.md:270 | NEW:edit-residue | K19 |
| 565 | DCI-pa-arv-A4-3 | DCI docs/audits/phase-a-rows/insulation-arvada.html.md:284 | C06 | K06 |
| 566 | DCI-gB-B-01 | DCI docs/audits/read-2026-08-25/groupB.md:70 | C03 | K03 |
| 567 | DCI-gB-B-03 | DCI docs/audits/read-2026-08-25/groupB.md:94 | C08 | K08 |
| 568 | DCI-gB-B-04 | DCI docs/audits/read-2026-08-25/groupB.md:175 | C08 | K08 |
| 569 | DCI-gB-B-05 | DCI docs/audits/read-2026-08-25/groupB.md:244 | C10 | K10 |
| 570 | DCI-gB-B-07 | DCI docs/audits/read-2026-08-25/groupB.md:340 | C10 | K10 |
| 571 | DCI-gB-B-08 | DCI docs/audits/read-2026-08-25/groupB.md:352 | C03 | K03 |
| 572 | DCI-gB-B-09 | DCI docs/audits/read-2026-08-25/groupB.md:364 | NEW:template-misapplied | K23 |
| 573 | DCI-gB-B-11 | DCI docs/audits/read-2026-08-25/groupB.md:439 | C08 | K08 |
| 574 | DCI-gB-B-12 | DCI docs/audits/read-2026-08-25/groupB.md:451 | C03 | K03 |
| 575 | DCI-gB-B-13 | DCI docs/audits/read-2026-08-25/groupB.md:504 | C03 | K03 |
| 576 | DCI-gB-B-14 | DCI docs/audits/read-2026-08-25/groupB.md:530 | C03 | K03 |
| 577 | DCI-gB-B-15 | DCI docs/audits/read-2026-08-25/groupB.md:542 | C08 | K08 |
| 578 | DCI-gB-B-17 | DCI docs/audits/read-2026-08-25/groupB.md:618 | C04 | K04 |
| 579 | DCI-gB-B-19 | DCI docs/audits/read-2026-08-25/groupB.md:674 | C08 | K08 |
| 580 | DCI-gB-B-20 | DCI docs/audits/read-2026-08-25/groupB.md:686 | NEW:edit-residue | K19 |
| 581 | DCI-gB-B-22 | DCI docs/audits/read-2026-08-25/groupB.md:779 | C03 | K03 |
| 582 | DCI-ct-F10 | DCI docs/audits/phase-a-rows/contact.html.md:139 | C03 | K03 |
| 583 | DCI-cs-F1 | DCI docs/audits/phase-a-rows/crawl-space-conditioning-denver.html.md:39 | C08 | K08 |
| 584 | DCI-cs-F2 | DCI docs/audits/phase-a-rows/crawl-space-conditioning-denver.html.md:60 | C03 | K03 |
| 585 | DCI-cs-F3 | DCI docs/audits/phase-a-rows/crawl-space-conditioning-denver.html.md:72 | C08 | K08 |
| 586 | DCI-cs-F4 | DCI docs/audits/phase-a-rows/crawl-space-conditioning-denver.html.md:88 | C03 | K03 |
| 587 | DCI-cs-F5 | DCI docs/audits/phase-a-rows/crawl-space-conditioning-denver.html.md:100 | C03 | K03 |
| 588 | DCI-cs-F6 | DCI docs/audits/phase-a-rows/crawl-space-conditioning-denver.html.md:114 | C03 | K03 |
| 589 | DCI-cs-F7 | DCI docs/audits/phase-a-rows/crawl-space-conditioning-denver.html.md:125 | NEW:template-misapplied | K23 |
| 590 | DCI-cs-F8 | DCI docs/audits/phase-a-rows/crawl-space-conditioning-denver.html.md:143 | C03 | K03 |
| 591 | DCI-cs-F9 | DCI docs/audits/phase-a-rows/crawl-space-conditioning-denver.html.md:158 | C03 | K03 |
| 592 | DCI-cs-F10 | DCI docs/audits/phase-a-rows/crawl-space-conditioning-denver.html.md:167 | C08 | K08 |
| 593 | DCI-cs-F11 | DCI docs/audits/phase-a-rows/crawl-space-conditioning-denver.html.md:178 | C03 | K03 |
| 594 | DCI-qz-A1-3 | DCI docs/audits/phase-a-rows/do-i-need-new-insulation-quiz.html.md:131 | NEW:malformed-prose | K20 |
| 595 | DCI-qz-A1-4 | DCI docs/audits/phase-a-rows/do-i-need-new-insulation-quiz.html.md:136 | NEW:malformed-prose | K20 |
| 596 | DCI-qz-A1-5 | DCI docs/audits/phase-a-rows/do-i-need-new-insulation-quiz.html.md:141 | NEW:malformed-prose | K20 |
| 597 | DCI-qz-A1-6 | DCI docs/audits/phase-a-rows/do-i-need-new-insulation-quiz.html.md:146 | NEW:malformed-prose | K20 |
| 598 | DCI-qz-A1-7 | DCI docs/audits/phase-a-rows/do-i-need-new-insulation-quiz.html.md:153 | NEW:edit-residue | K19 |
| 599 | DCI-qz-A1-8 | DCI docs/audits/phase-a-rows/do-i-need-new-insulation-quiz.html.md:159 | C10 | K10 |
| 600 | DCI-qz-A2-2 | DCI docs/audits/phase-a-rows/do-i-need-new-insulation-quiz.html.md:179 | C03 | K03 |
| 601 | DCI-qz-A2-3 | DCI docs/audits/phase-a-rows/do-i-need-new-insulation-quiz.html.md:186 | C03 | K03 |
| 602 | DCI-qz-A2-5 | DCI docs/audits/phase-a-rows/do-i-need-new-insulation-quiz.html.md:197 | C03 | K03 |
| 603 | DCI-qz-A2-6 | DCI docs/audits/phase-a-rows/do-i-need-new-insulation-quiz.html.md:206 | C03 | K03 |
| 604 | DCI-qz-A2-7 | DCI docs/audits/phase-a-rows/do-i-need-new-insulation-quiz.html.md:211 | C03 | K03 |
| 605 | DCI-qz-A3-1 | DCI docs/audits/phase-a-rows/do-i-need-new-insulation-quiz.html.md:224 | C08 | K08 |
| 606 | DCI-qz-A3-4 | DCI docs/audits/phase-a-rows/do-i-need-new-insulation-quiz.html.md:259 | C08 | K08 |
| 607 | DCI-qz-A3-5 | DCI docs/audits/phase-a-rows/do-i-need-new-insulation-quiz.html.md:264 | NEW:template-misapplied | K23 |
| 608 | DCI-qz-A5-1 | DCI docs/audits/phase-a-rows/do-i-need-new-insulation-quiz.html.md:297 | C15 | K15 |
| 609 | DCI-qz-A5-2 | DCI docs/audits/phase-a-rows/do-i-need-new-insulation-quiz.html.md:312 | C08 | K08 |
| 610 | DCI-qz-A5-4 | DCI docs/audits/phase-a-rows/do-i-need-new-insulation-quiz.html.md:328 | C10 | K10 |
| 611 | DCI-qz-A5-5 | DCI docs/audits/phase-a-rows/do-i-need-new-insulation-quiz.html.md:336 | C08 | K08 |
| 612 | DCI-pb-A1-1 | DCI docs/audits/phase-a-rows/energy-savings-payback-calculator.html.md:151 | C15 | K15 |
| 613 | DCI-pb-A1-2 | DCI docs/audits/phase-a-rows/energy-savings-payback-calculator.html.md:161 | C15 | K15 |
| 614 | DCI-pb-A1-3 | DCI docs/audits/phase-a-rows/energy-savings-payback-calculator.html.md:170 | C15 | K15 |
| 615 | DCI-pb-A1-4 | DCI docs/audits/phase-a-rows/energy-savings-payback-calculator.html.md:179 | C10 | K10 |
| 616 | DCI-pb-A1-5 | DCI docs/audits/phase-a-rows/energy-savings-payback-calculator.html.md:189 | C10 | K10 |
| 617 | DCI-pb-A2-1 | DCI docs/audits/phase-a-rows/energy-savings-payback-calculator.html.md:203 | C14 | K14 |
| 618 | DCI-pb-A2-2 | DCI docs/audits/phase-a-rows/energy-savings-payback-calculator.html.md:223 | C03 | K03 |
| 619 | DCI-pb-A3-3 | DCI docs/audits/phase-a-rows/energy-savings-payback-calculator.html.md:311 | C08 | K08 |
| 620 | DCI-pb-A3-4 | DCI docs/audits/phase-a-rows/energy-savings-payback-calculator.html.md:330 | C08 | K08 |
| 621 | DCI-pb-A3-6 | DCI docs/audits/phase-a-rows/energy-savings-payback-calculator.html.md:358 | C08 | K08 |
| 622 | DCI-pb-A5-4 | DCI docs/audits/phase-a-rows/energy-savings-payback-calculator.html.md:439 | C08 | K08 |
| 623 | DCI-pb-A5-5 | DCI docs/audits/phase-a-rows/energy-savings-payback-calculator.html.md:450 | C08 | K08 |
| 624 | DCI-pb-A5-6 | DCI docs/audits/phase-a-rows/energy-savings-payback-calculator.html.md:463 | C08 | K08 |
| 625 | DCI-pb-A5-7 | DCI docs/audits/phase-a-rows/energy-savings-payback-calculator.html.md:474 | C15 | K15 |
| 626 | DCI-pb-A5-8 | DCI docs/audits/phase-a-rows/energy-savings-payback-calculator.html.md:487 | C11 | K11 |
| 627 | DCI-ft-A1-1 | DCI docs/audits/phase-a-rows/freeze-thaw-cycles-denver-insulation.html.md:50 | C15 | K15 |
| 628 | DCI-ft-A1-4 | DCI docs/audits/phase-a-rows/freeze-thaw-cycles-denver-insulation.html.md:81 | NEW:malformed-prose | K20 |
| 629 | DCI-ft-A1-5 | DCI docs/audits/phase-a-rows/freeze-thaw-cycles-denver-insulation.html.md:88 | NEW:malformed-prose | K20 |
| 630 | DCI-ft-A1-6 | DCI docs/audits/phase-a-rows/freeze-thaw-cycles-denver-insulation.html.md:93 | NEW:edit-residue | K19 |
| 631 | DCI-ft-A1-7 | DCI docs/audits/phase-a-rows/freeze-thaw-cycles-denver-insulation.html.md:102 | C15 | K15 |
| 632 | DCI-ft-A2-2 | DCI docs/audits/phase-a-rows/freeze-thaw-cycles-denver-insulation.html.md:119 | C03 | K03 |
| 633 | DCI-ft-A2-3 | DCI docs/audits/phase-a-rows/freeze-thaw-cycles-denver-insulation.html.md:128 | C03 | K03 |
| 634 | DCI-ft-A2-4 | DCI docs/audits/phase-a-rows/freeze-thaw-cycles-denver-insulation.html.md:133 | C03 | K03 |
| 635 | DCI-ft-A2-5 | DCI docs/audits/phase-a-rows/freeze-thaw-cycles-denver-insulation.html.md:139 | C03 | K03 |
| 636 | DCI-ft-A2-6 | DCI docs/audits/phase-a-rows/freeze-thaw-cycles-denver-insulation.html.md:151 | C03 | K03 |
| 637 | DCI-ft-A2-7 | DCI docs/audits/phase-a-rows/freeze-thaw-cycles-denver-insulation.html.md:163 | C03 | K03 |
| 638 | DCI-ft-A2-9 | DCI docs/audits/phase-a-rows/freeze-thaw-cycles-denver-insulation.html.md:181 | C17 | K17 |
| 639 | DCI-ft-A3-1 | DCI docs/audits/phase-a-rows/freeze-thaw-cycles-denver-insulation.html.md:207 | C08 | K08 |
| 640 | DCI-ft-A3-2 | DCI docs/audits/phase-a-rows/freeze-thaw-cycles-denver-insulation.html.md:221 | C08 | K08 |
| 641 | DCI-ft-A3-3 | DCI docs/audits/phase-a-rows/freeze-thaw-cycles-denver-insulation.html.md:234 | C08 | K08 |
| 642 | DCI-ft-A3-4 | DCI docs/audits/phase-a-rows/freeze-thaw-cycles-denver-insulation.html.md:241 | C08 | K08 |
| 643 | DCI-ft-A3-6 | DCI docs/audits/phase-a-rows/freeze-thaw-cycles-denver-insulation.html.md:257 | C09 | K09 |
| 644 | DCI-ft-A3-7 | DCI docs/audits/phase-a-rows/freeze-thaw-cycles-denver-insulation.html.md:263 | C08 | K08 |
| 645 | DCI-ft-A3-8 | DCI docs/audits/phase-a-rows/freeze-thaw-cycles-denver-insulation.html.md:272 | C08 | K08 |
| 646 | DCI-fr-A1-4 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:103 | NEW:malformed-prose | K20 |
| 647 | DCI-fr-A1-5 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:111 | NEW:malformed-prose | K20 |
| 648 | DCI-fr-A1-6 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:117 | NEW:malformed-prose | K20 |
| 649 | DCI-fr-A1-7 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:122 | NEW:malformed-prose | K20 |
| 650 | DCI-fr-A1-8 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:126 | NEW:malformed-prose | K20 |
| 651 | DCI-fr-A1-9 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:132 | NEW:malformed-prose | K20 |
| 652 | DCI-fr-A2-1 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:151 | C03 | K03 |
| 653 | DCI-fr-A2-2 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:158 | C03 | K03 |
| 654 | DCI-fr-A2-3 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:164 | C03 | K03 |
| 655 | DCI-fr-A2-4 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:169 | C03 | K03 |
| 656 | DCI-fr-A2-5 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:176 | C03 | K03 |
| 657 | DCI-fr-A2-6 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:180 | C03 | K03 |
| 658 | DCI-fr-A2-7 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:185 | C03 | K03 |
| 659 | DCI-fr-A2-8 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:191 | C03 | K03 |
| 660 | DCI-fr-A2-9 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:199 | C03 | K03 |
| 661 | DCI-fr-A2-10 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:206 | C03 | K03 |
| 662 | DCI-fr-A2-12 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:228 | C04 | K04 |
| 663 | DCI-fr-A2-13 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:237 | C17 | K17 |
| 664 | DCI-fr-A3-1 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:262 | C08 | K08 |
| 665 | DCI-fr-A3-2 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:283 | C08 | K08 |
| 666 | DCI-fr-A3-3 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:293 | C08 | K08 |
| 667 | DCI-fr-A3-4 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:300 | C08 | K08 |
| 668 | DCI-fr-A3-5 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:311 | C08 | K08 |
| 669 | DCI-fr-A3-10 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:352 | C08 | K08 |
| 670 | DCI-fr-A8-1 | DCI docs/audits/phase-a-rows/front-range-wind-insulation-denver.html.md:490 | C03 | K03 |
| 671 | DCI-hr-A2-2 | DCI docs/audits/phase-a-rows/hear-rebate-status-colorado.html.md:176 | C03 | K03 |
| 672 | DCI-hr-A2-3 | DCI docs/audits/phase-a-rows/hear-rebate-status-colorado.html.md:190 | C03 | K03 |
| 673 | DCI-hr-A2-4 | DCI docs/audits/phase-a-rows/hear-rebate-status-colorado.html.md:206 | C03 | K03 |
| 674 | DCI-hr-A2-5 | DCI docs/audits/phase-a-rows/hear-rebate-status-colorado.html.md:217 | C03 | K03 |
| 675 | DCI-hr-A2-7 | DCI docs/audits/phase-a-rows/hear-rebate-status-colorado.html.md:243 | C03 | K03 |
| 676 | DCI-hr-A2-8 | DCI docs/audits/phase-a-rows/hear-rebate-status-colorado.html.md:252 | C03 | K03 |
| 677 | DCI-hr-A3-1 | DCI docs/audits/phase-a-rows/hear-rebate-status-colorado.html.md:266 | C08 | K08 |
| 678 | DCI-hr-A3-2 | DCI docs/audits/phase-a-rows/hear-rebate-status-colorado.html.md:281 | C08 | K08 |
| 679 | DCI-hr-A3-3 | DCI docs/audits/phase-a-rows/hear-rebate-status-colorado.html.md:296 | C08 | K08 |
| 680 | DCI-hr-A3-4 | DCI docs/audits/phase-a-rows/hear-rebate-status-colorado.html.md:314 | C08 | K08 |
| 681 | DCI-hr-A4-2 | DCI docs/audits/phase-a-rows/hear-rebate-status-colorado.html.md:345 | C03 | K03 |
| 682 | DCI-hr-A4-3 | DCI docs/audits/phase-a-rows/hear-rebate-status-colorado.html.md:357 | C03 | K03 |
| 683 | DCI-hr-A8-1 | DCI docs/audits/phase-a-rows/hear-rebate-status-colorado.html.md:431 | C03 | K03 |
| 684 | DCI-hr-A8-2 | DCI docs/audits/phase-a-rows/hear-rebate-status-colorado.html.md:444 | C03 | K03 |
| 685 | DCI-hr-A8-3 | DCI docs/audits/phase-a-rows/hear-rebate-status-colorado.html.md:453 | C03 | K03 |
| 686 | DCI-hr-A8-4 | DCI docs/audits/phase-a-rows/hear-rebate-status-colorado.html.md:462 | C03 | K03 |
| 687 | DCI-hv-A1-2 | DCI docs/audits/phase-a-rows/hvac-sizing-after-insulation-denver.html.md:155 | C10 | K10 |
| 688 | DCI-hv-A2-1 | DCI docs/audits/phase-a-rows/hvac-sizing-after-insulation-denver.html.md:180 | C03 | K03 |
| 689 | DCI-hv-A2-2 | DCI docs/audits/phase-a-rows/hvac-sizing-after-insulation-denver.html.md:209 | C03 | K03 |
| 690 | DCI-hv-A2-3 | DCI docs/audits/phase-a-rows/hvac-sizing-after-insulation-denver.html.md:224 | C03 | K03 |
| 691 | DCI-hv-A2-4 | DCI docs/audits/phase-a-rows/hvac-sizing-after-insulation-denver.html.md:236 | C03 | K03 |
| 692 | DCI-hv-A2-5 | DCI docs/audits/phase-a-rows/hvac-sizing-after-insulation-denver.html.md:246 | C03 | K03 |
| 693 | DCI-hv-A3-1 | DCI docs/audits/phase-a-rows/hvac-sizing-after-insulation-denver.html.md:284 | C08 | K08 |
| 694 | DCI-hv-A3-2 | DCI docs/audits/phase-a-rows/hvac-sizing-after-insulation-denver.html.md:306 | C08 | K08 |
| 695 | DCI-hv-A8-2 | DCI docs/audits/phase-a-rows/hvac-sizing-after-insulation-denver.html.md:380 | C03 | K03 |
| 696 | DCI-k13-01 | DCI docs/audits/k13-page-read-2026-10-05.md:14 | C18 | K18 |
| 697 | DCI-k13-02 | DCI docs/audits/k13-page-read-2026-10-05.md:26 | C18 | K18 |
| 698 | DCI-k13-03 | DCI docs/audits/k13-page-read-2026-10-05.md:27 | C03 | K03 |
| 699 | DCI-k13-05 | DCI docs/audits/k13-page-read-2026-10-05.md:42 | C03 | K03 |
| 700 | DCI-k13-06 | DCI docs/audits/k13-page-read-2026-10-05.md:57 | C18 | K18 |
| 701 | DCI-k13-07 | DCI docs/audits/k13-page-read-2026-10-05.md:62 | C18 | K18 |
| 702 | DCI-k13-08 | DCI docs/audits/k13-page-read-2026-10-05.md:69 | C03 | K03 |
| 703 | DCI-k13-09 | DCI docs/audits/k13-page-read-2026-10-05.md:90 | C18 | K18 |
| 704 | DCI-k13-10 | DCI docs/audits/k13-page-read-2026-10-05.md:112 | C18 | K18 |
| 705 | DCI-k13-11 | DCI docs/audits/k13-page-read-2026-10-05.md:117 | C03 | K03 |
| 706 | DCI-k13-12 | DCI docs/audits/k13-page-read-2026-10-05.md:118 | C08 | K08 |
| 707 | DCI-k13-13 | DCI docs/audits/k13-page-read-2026-10-05.md:133 | C02 | K02 |
| 708 | DCI-k13-14 | DCI docs/audits/k13-page-read-2026-10-05.md:138 | C18 | K18 |
| 709 | DCI-k13-15 | DCI docs/audits/k13-page-read-2026-10-05.md:149 | C18 | K18 |
| 710 | DCI-k13-16 | DCI docs/audits/k13-page-read-2026-10-05.md:150 | C18 | K18 |
| 711 | DCI-k13-17 | DCI docs/audits/k13-page-read-2026-10-05.md:155 | C18 | K18 |
| 712 | DCI-k13-18 | DCI docs/audits/k13-page-read-2026-10-05.md:156 | C18 | K18 |
| 713 | DCI-k13-19 | DCI docs/audits/k13-page-read-2026-10-05.md:162 | C18 | K18 |
| 714 | DCI-k13-20 | DCI docs/audits/k13-page-read-2026-10-05.md:163 | C08 | K08 |
| 715 | DCI-k13-21 | DCI docs/audits/k13-page-read-2026-10-05.md:164 | C18 | K18 |
| 716 | DCI-k13-22 | DCI docs/audits/k13-page-read-2026-10-05.md:165 | C18 | K18 |
| 717 | DCI-k13-23 | DCI docs/audits/k13-page-read-2026-10-05.md:170 | C08 | K08 |
| 718 | DCI-k13-24 | DCI docs/audits/k13-page-read-2026-10-05.md:175 | C18 | K18 |
| 719 | DCI-k13-25 | DCI docs/audits/k13-page-read-2026-10-05.md:176 | C03 | K03 |
| 720 | DCI-k13-26 | DCI docs/audits/k13-page-read-2026-10-05.md:181 | C03 | K03 |
| 721 | DCI-k13-27 | DCI docs/audits/k13-page-read-2026-10-05.md:182 | C03 | K03 |
| 722 | DCI-k13-28 | DCI docs/audits/k13-page-read-2026-10-05.md:183 | C08 | K08 |
| 723 | DCI-k13-29 | DCI docs/audits/k13-page-read-2026-10-05.md:190 | C18 | K18 |
| 724 | DCI-k13-30 | DCI docs/audits/k13-page-read-2026-10-05.md:193 | C18 | K18 |
| 725 | DCI-k13-31 | DCI docs/audits/k13-page-read-2026-10-05.md:194 | C18 | K18 |
| 726 | DCI-k13-32 | DCI docs/audits/k13-page-read-2026-10-05.md:195 | C18 | K18 |
| 727 | DCI-k13-33 | DCI docs/audits/k13-page-read-2026-10-05.md:196 | C18 | K18 |
| 728 | DCI-k13-34 | DCI docs/audits/k13-page-read-2026-10-05.md:197 | C18 | K18 |
| 729 | DCI-k13-35 | DCI docs/audits/k13-page-read-2026-10-05.md:198 | C18 | K18 |
| 730 | DCI-k13-36 | DCI docs/audits/k13-page-read-2026-10-05.md:199 | C18 | K18 |
| 731 | DCI-k13-37 | DCI docs/audits/k13-page-read-2026-10-05.md:205 | C08 | K08 |
| 732 | DCI-k13-38 | DCI docs/audits/k13-page-read-2026-10-05.md:206 | C18 | K18 |
| 733 | DCI-k13-39 | DCI docs/audits/k13-page-read-2026-10-05.md:211 | C08 | K08 |
| 734 | DCI-k13-40 | DCI docs/audits/k13-page-read-2026-10-05.md:212 | C18 | K18 |
| 735 | DCI-k13-41 | DCI docs/audits/k13-page-read-2026-10-05.md:222 | C18 | K18 |
| 736 | DCI-k13-42 | DCI docs/audits/k13-page-read-2026-10-05.md:223 | C18 | K18 |
| 737 | DCI-k13-43 | DCI docs/audits/k13-page-read-2026-10-05.md:224 | C08 | K08 |
| 738 | DCI-k13-44 | DCI docs/audits/k13-page-read-2026-10-05.md:225 | C08 | K08 |
| 739 | DCI-k13-45 | DCI docs/audits/k13-page-read-2026-10-05.md:235 | C18 | K18 |
| 740 | DCI-k13-46 | DCI docs/audits/k13-page-read-2026-10-05.md:241 | C18 | K18 |
| 741 | DCI-k13-47 | DCI docs/audits/k13-page-read-2026-10-05.md:242 | C18 | K18 |
| 742 | DCI-k13-48 | DCI docs/audits/k13-page-read-2026-10-05.md:243 | C18 | K18 |
| 743 | DCI-k13-49 | DCI docs/audits/k13-page-read-2026-10-05.md:246 | NEW:template-misapplied | K23 |
| 744 | DCI-k13-50 | DCI docs/audits/k13-page-read-2026-10-05.md:249 | C18 | K18 |
| 745 | DCI-k13-52 | DCI docs/audits/k13-page-read-2026-10-05.md:256 | C18 | K18 |
| 746 | DCI-k13-53 | DCI docs/audits/k13-page-read-2026-10-05.md:257 | C18 | K18 |
| 747 | DCI-k13-54 | DCI docs/audits/k13-page-read-2026-10-05.md:258 | C18 | K18 |
| 748 | DCI-k13-55 | DCI docs/audits/k13-page-read-2026-10-05.md:264 | C18 | K18 |
| 749 | DCI-k13-56 | DCI docs/audits/k13-page-read-2026-10-05.md:265 | C18 | K18 |
| 750 | DCI-k13-58 | DCI docs/audits/k13-page-read-2026-10-05.md:267 | C18 | K18 |
| 751 | DCI-k13-59 | DCI docs/audits/k13-page-read-2026-10-05.md:272 | C08 | K08 |
| 752 | DCI-k13-60 | DCI docs/audits/k13-page-read-2026-10-05.md:277 | C18 | K18 |
| 753 | DCI-k13-61 | DCI docs/audits/k13-page-read-2026-10-05.md:278 | C08 | K08 |
| 754 | DCI-k13-62 | DCI docs/audits/k13-page-read-2026-10-05.md:279 | C18 | K18 |
| 755 | DCI-k13-63 | DCI docs/audits/k13-page-read-2026-10-05.md:280 | C18 | K18 |
| 756 | DCI-k13-64 | DCI docs/audits/k13-page-read-2026-10-05.md:281 | C18 | K18 |
| 757 | DCI-k13-65 | DCI docs/audits/k13-page-read-2026-10-05.md:282 | C18 | K18 |
| 758 | DCI-k13-66 | DCI docs/audits/k13-page-read-2026-10-05.md:283 | C03 | K03 |
| 759 | DCI-k13-67 | DCI docs/audits/k13-page-read-2026-10-05.md:289 | C18 | K18 |
| 760 | DCI-k13-68 | DCI docs/audits/k13-page-read-2026-10-05.md:290 | C18 | K18 |
| 761 | DCI-k13-69 | DCI docs/audits/k13-page-read-2026-10-05.md:291 | C18 | K18 |
| 762 | DCI-k13-70 | DCI docs/audits/k13-page-read-2026-10-05.md:292 | C18 | K18 |
| 763 | DCI-k13-71 | DCI docs/audits/k13-page-read-2026-10-05.md:293 | C18 | K18 |
| 764 | DCI-k13-72 | DCI docs/audits/k13-page-read-2026-10-05.md:296 | C18 | K18 |
| 765 | DCI-k13-73 | DCI docs/audits/k13-page-read-2026-10-05.md:307 | C18 | K18 |
| 766 | DCI-k13-74 | DCI docs/audits/k13-page-read-2026-10-05.md:308 | C18 | K18 |
| 767 | DCI-k13-76 | DCI docs/audits/k13-page-read-2026-10-05.md:314 | C18 | K18 |
| 768 | DCI-k13-77 | DCI docs/audits/k13-page-read-2026-10-05.md:316 | C18 | K18 |
| 769 | DCI-k13-78 | DCI docs/audits/k13-page-read-2026-10-05.md:322 | C18 | K18 |
| 770 | DCI-k13-79 | DCI docs/audits/k13-page-read-2026-10-05.md:323 | C18 | K18 |
| 771 | DCI-k13-80 | DCI docs/audits/k13-page-read-2026-10-05.md:324 | C18 | K18 |
| 772 | DCI-k13-81 | DCI docs/audits/k13-page-read-2026-10-05.md:325 | C18 | K18 |
| 773 | DCI-k13-82 | DCI docs/audits/k13-page-read-2026-10-05.md:326 | C18 | K18 |
| 774 | DCI-k13-83 | DCI docs/audits/k13-page-read-2026-10-05.md:327 | C18 | K18 |
| 775 | DCI-k13-84 | DCI docs/audits/k13-page-read-2026-10-05.md:328 | C18 | K18 |
| 776 | DCI-k13-86 | DCI docs/audits/k13-page-read-2026-10-05.md:346 | C18 | K18 |
| 777 | DCI-k13-87 | DCI docs/audits/k13-page-read-2026-10-05.md:351 | C18 | K18 |
| 778 | DCI-k13-88 | DCI docs/audits/k13-page-read-2026-10-05.md:357 | C18 | K18 |
| 779 | DCI-k13-89 | DCI docs/audits/k13-page-read-2026-10-05.md:362 | C18 | K18 |
| 780 | DCI-k13-90 | DCI docs/audits/k13-page-read-2026-10-05.md:364 | C08 | K08 |
| 781 | DCI-k13-91 | DCI docs/audits/k13-page-read-2026-10-05.md:370 | C03 | K03 |
| 782 | DCI-k13-92 | DCI docs/audits/k13-page-read-2026-10-05.md:371 | C03 | K03 |
| 783 | DCI-k13-93 | DCI docs/audits/k13-page-read-2026-10-05.md:372 | C18 | K18 |
| 784 | DCI-k13-94 | DCI docs/audits/k13-page-read-2026-10-05.md:373 | C18 | K18 |
| 785 | DCI-k13-96 | DCI docs/audits/k13-page-read-2026-10-05.md:380 | C18 | K18 |
| 786 | DCI-k13-97 | DCI docs/audits/k13-page-read-2026-10-05.md:385 | C18 | K18 |
| 787 | DCI-k13-98 | DCI docs/audits/k13-page-read-2026-10-05.md:387 | C18 | K18 |
| 788 | DCI-k13-99 | DCI docs/audits/k13-page-read-2026-10-05.md:391 | NEW:template-misapplied | K23 |
| 789 | DCI-k13-100 | DCI docs/audits/k13-page-read-2026-10-05.md:400 | C18 | K18 |
| 790 | DCI-k13-101 | DCI docs/audits/k13-page-read-2026-10-05.md:401 | C18 | K18 |
| 791 | DCI-k13-102 | DCI docs/audits/k13-page-read-2026-10-05.md:402 | C18 | K18 |
| 792 | DCI-k13-103 | DCI docs/audits/k13-page-read-2026-10-05.md:408 | C18 | K18 |
| 793 | DCI-k13-104 | DCI docs/audits/k13-page-read-2026-10-05.md:409 | C18 | K18 |
| 794 | DCI-k13-105 | DCI docs/audits/k13-page-read-2026-10-05.md:410 | C18 | K18 |
| 795 | DCI-k13-107 | DCI docs/audits/k13-page-read-2026-10-05.md:417 | C18 | K18 |
| 796 | DCI-k13-108 | DCI docs/audits/k13-page-read-2026-10-05.md:418 | C18 | K18 |
| 797 | DCI-k13-110 | DCI docs/audits/k13-page-read-2026-10-05.md:424 | C18 | K18 |
| 798 | DCI-k13-111 | DCI docs/audits/k13-page-read-2026-10-05.md:425 | C03 | K03 |
| 799 | DCI-k13-112 | DCI docs/audits/k13-page-read-2026-10-05.md:435 | C18 | K18 |
| 800 | DCI-k13-114 | DCI docs/audits/k13-page-read-2026-10-05.md:443 | C18 | K18 |
| 801 | DCI-k13-117 | DCI docs/audits/k13-page-read-2026-10-05.md:451 | C18 | K18 |
| 802 | DCI-k13-119 | DCI docs/audits/k13-page-read-2026-10-05.md:453 | C18 | K18 |
| 803 | DCI-k13-121 | DCI docs/audits/k13-page-read-2026-10-05.md:490 | C18 | K18 |
| 804 | DCI-k13-122 | DCI docs/audits/k13-page-read-2026-10-05.md:491 | C02 | K02 |
| 805 | DCI-k13-123 | DCI docs/audits/k13-page-read-2026-10-05.md:492 | C18 | K18 |
| 806 | DCI-k13-124 | DCI docs/audits/k13-page-read-2026-10-05.md:493 | C18 | K18 |
| 807 | DCI-k13-125 | DCI docs/audits/k13-page-read-2026-10-05.md:522 | C18 | K18 |
| 808 | DCI-k13-126 | DCI docs/audits/k13-page-read-2026-10-05.md:532 | C18 | K18 |
| 809 | DCI-k13-127 | DCI docs/audits/k13-page-read-2026-10-05.md:533 | C18 | K18 |
| 810 | DCI-k13-130 | DCI docs/audits/k13-page-read-2026-10-05.md:557 | C18 | K18 |
| 811 | DCI-k13-134 | DCI docs/audits/k13-page-read-2026-10-05.md:574 | C18 | K18 |
| 812 | DCI-k13-135 | DCI docs/audits/k13-page-read-2026-10-05.md:575 | C18 | K18 |
| 813 | DCI-k13-136 | DCI docs/audits/k13-page-read-2026-10-05.md:576 | C18 | K18 |
| 814 | DCI-k13-137 | DCI docs/audits/k13-page-read-2026-10-05.md:577 | C02 | K02 |
| 815 | DCI-k13-138 | DCI docs/audits/k13-page-read-2026-10-05.md:580 | C18 | K18 |
| 816 | DCI-gt-01 | DCI docs/board/ground-truth.md:5 | C13 | K13 |
| 817 | DCI-gt-02 | DCI docs/board/ground-truth.md:114 | C03 | K03 |
| 818 | DCI-gt-03 | DCI docs/board/ground-truth.md:128 | C13 | K13 |
| 819 | DCI-gt-04 | DCI docs/board/ground-truth.md:177 | C03 | K03 |
| 820 | DCI-gt-05 | DCI docs/board/ground-truth.md:182 | C03 | K03 |
| 821 | DCI-gt-06 | DCI docs/board/ground-truth.md:192 | C02 | K02 |
| 822 | DCI-gt-07 | DCI docs/board/ground-truth.md:194 | C03 | K03 |
| 823 | DCI-gt-08 | DCI docs/board/ground-truth.md:202 | C09 | K09 |
| 824 | DCI-gt-09 | DCI docs/board/ground-truth.md:204 | C03 | K03 |
| 825 | DCI-gt-10 | DCI docs/board/ground-truth.md:206 | NEW:undisclosed-relationship | K16 |
| 826 | DCI-gt-11 | DCI docs/board/ground-truth.md:220 | C03 | K03 |
| 827 | DCI-gt-12 | DCI docs/board/ground-truth.md:244 | C13 | K13 |
| 828 | DCI-gt-13 | DCI docs/board/ground-truth.md:284 | C13 | K13 |
| 829 | DCI-gt-14 | DCI docs/board/ground-truth.md:311 | C13 | K13 |
| 830 | DCI-gt-15 | DCI docs/board/ground-truth.md:426 | C02 | K02 |
| 831 | DCI-gt-16 | DCI docs/board/ground-truth.md:459 | C03 | K03 |
| 832 | DCI-gt-17 | DCI docs/board/ground-truth.md:477 | C03 | K03 |
| 833 | DCI-gt-18 | DCI docs/board/ground-truth.md:486 | C03 | K03 |
| 834 | DCI-gt-19 | DCI docs/board/ground-truth.md:491 | C02 | K02 |
| 835 | DCI-gt-20 | DCI docs/board/ground-truth.md:514 | C02 | K02 |
| 836 | DCI-gt-21 | DCI docs/board/ground-truth.md:531 | C13 | K13 |
| 837 | DCI-gt-22 | DCI docs/board/ground-truth.md:542 | C11 | K11 |
| 838 | DCI-gt-23 | DCI docs/board/ground-truth.md:545 | C15 | K15 |
| 839 | DCI-rs-01 | DCI ops/retired_strings.txt:126 | C03 | K03 |
| 840 | DCI-rs-02 | DCI ops/retired_strings.txt:130 | C08 | K08 |
| 841 | DCI-rs-03 | DCI ops/retired_strings.txt:206 | C01 | K01 |
| 842 | DCI-rs-04 | DCI ops/retired_strings.txt:242 | C03 | K03 |
| 843 | DCI-rs-05 | DCI ops/retired_strings.txt:247 | C01 | K01 |
| 844 | DCI-rs-06 | DCI ops/retired_strings.txt:265 | C03 | K03 |
| 845 | DCI-rs-07 | DCI ops/retired_strings.txt:269 | NEW:edit-residue | K19 |
| 846 | DCI-rs-08 | DCI ops/retired_strings.txt:271 | NEW:edit-residue | K19 |
| 847 | DCI-rs-09 | DCI ops/retired_strings.txt:273 | NEW:edit-residue | K19 |
| 848 | DCI-rs-10 | DCI ops/retired_strings.txt:275 | NEW:edit-residue | K19 |
| 849 | DCI-rs-12 | DCI ops/retired_strings.txt:279 | C01 | K01 |
| 850 | DCI-rs-13 | DCI ops/retired_strings.txt:281 | NEW:contractor-voice | K16 |
| 851 | DCI-rs-14 | DCI ops/retired_strings.txt:283 | NEW:contractor-voice | K16 |
| 852 | DCI-rs-15 | DCI ops/retired_strings.txt:285 | NEW:contractor-voice | K16 |
| 853 | DCI-rs-18 | DCI ops/retired_strings.txt:291 | NEW:edit-residue | K16 | (override)
| 854 | DCI-rs-21 | DCI ops/retired_strings.txt:319 | NEW:edit-residue | K19 |
| 855 | DCI-rs-22 | DCI ops/retired_strings.txt:321 | C15 | K15 |
| 856 | DCI-rs-23 | DCI ops/retired_strings.txt:323 | NEW:edit-residue | K19 |
| 857 | DCI-rs-24 | DCI ops/retired_strings.txt:325 | C03 | K03 |
| 858 | DCI-rs-25 | DCI ops/retired_strings.txt:327 | NEW:contractor-voice | K16 |
| 859 | DCI-rs-27 | DCI ops/retired_strings.txt:331 | C15 | K15 |
| 860 | DCI-rs-28 | DCI ops/retired_strings.txt:334 | C01 | K01 |
| 861 | DCI-rs-29 | DCI ops/retired_strings.txt:336 | NEW:contractor-voice | K16 |
| 862 | DCI-rs-30 | DCI ops/retired_strings.txt:338 | NEW:edit-residue | K19 |
| 863 | DCI-rs-31 | DCI ops/retired_strings.txt:460 | C03 | K03 |
| 864 | LGM-k14-01 | LGM docs/audits/k14-page-read-2026-10-06.md:23 | C08 | K08 |
| 865 | LGM-k14-02 | LGM docs/audits/k14-page-read-2026-10-06.md:229 | C08 | K08 |
| 866 | LGM-k14-03 | LGM docs/audits/k14-page-read-2026-10-06.md:181 | C18 | K18 |
| 867 | LGM-k14-04 | LGM docs/audits/k14-page-read-2026-10-06.md:199 | C08 | K08 |
| 868 | LGM-k14-05 | LGM docs/audits/k14-page-read-2026-10-06.md:250 | C08 | K08 |
| 869 | LGM-k14-06 | LGM docs/audits/k14-page-read-2026-10-06.md:253 | C08 | K08 |
| 870 | LGM-k14-07 | LGM docs/audits/k14-page-read-2026-10-06.md:265 | C08 | K08 |
| 871 | LGM-k14-08 | LGM docs/audits/k14-page-read-2026-10-06.md:274 | C08 | K08 |
| 872 | LGM-k14-09 | LGM docs/audits/k14-page-read-2026-10-06.md:277 | C18 | K18 |
| 873 | LGM-k14-10 | LGM docs/audits/k14-page-read-2026-10-06.md:283 | C01 | K01 |
| 874 | LGM-k14-11 | LGM docs/audits/k14-page-read-2026-10-06.md:331 | C08 | K08 |
| 875 | LGM-k14-12 | LGM docs/audits/k14-page-read-2026-10-06.md:394 | C18 | K18 |
| 876 | LGM-k14-13 | LGM docs/audits/k14-page-read-2026-10-06.md:511 | C18 | K18 |
| 877 | LGM-k14-14 | LGM docs/audits/k14-page-read-2026-10-06.md:595 | C03 | K03 |
| 878 | LGM-k14-15 | LGM docs/audits/k14-page-read-2026-10-06.md:612 | C18 | K18 |
| 879 | LGM-k14-16 | LGM docs/audits/k14-page-read-2026-10-06.md:620 | C18 | K18 |
| 880 | LGM-k14-17 | LGM docs/audits/k14-page-read-2026-10-06.md:674 | C08 | K08 |
| 881 | LGM-k14-18 | LGM docs/audits/k14-page-read-2026-10-06.md:675 | C18 | K18 |
| 882 | LGM-k14-19 | LGM docs/audits/k14-page-read-2026-10-06.md:676 | C18 | K18 |
| 883 | LGM-k14-20 | LGM docs/audits/k14-page-read-2026-10-06.md:677 | C18 | K18 |
| 884 | LGM-k14-21 | LGM docs/audits/k14-page-read-2026-10-06.md:668 | C15 | K15 |
| 885 | LGM-k14-22 | LGM docs/audits/k14-page-read-2026-10-06.md:17 | C18 | K18 |
| 886 | LGM-k14-23 | LGM docs/audits/k14-page-read-2026-10-06.md:26 | C18 | K18 |
| 887 | LGM-k14-24 | LGM docs/audits/k14-page-read-2026-10-06.md:78 | C18 | K18 |
| 888 | LGM-k14-25 | LGM docs/audits/k14-page-read-2026-10-06.md:94 | C18 | K18 |
| 889 | LGM-k14-26 | LGM docs/audits/k14-page-read-2026-10-06.md:36 | C18 | K18 |
| 890 | LGM-k14-27 | LGM docs/audits/k14-page-read-2026-10-06.md:39 | C18 | K18 |
| 891 | LGM-k14-28 | LGM docs/audits/k14-page-read-2026-10-06.md:42 | C18 | K18 |
| 892 | LGM-k14-29 | LGM docs/audits/k14-page-read-2026-10-06.md:133 | C18 | K18 |
| 893 | LGM-k14-30 | LGM docs/audits/k14-page-read-2026-10-06.md:136 | C18 | K18 |
| 894 | LGM-k14-31 | LGM docs/audits/k14-page-read-2026-10-06.md:142 | C18 | K18 |
| 895 | LGM-k14-32 | LGM docs/audits/k14-page-read-2026-10-06.md:145 | C18 | K18 |
| 896 | LGM-k14-33 | LGM docs/audits/k14-page-read-2026-10-06.md:148 | C18 | K18 |
| 897 | LGM-k14-34 | LGM docs/audits/k14-page-read-2026-10-06.md:169 | C18 | K18 |
| 898 | LGM-k14-35 | LGM docs/audits/k14-page-read-2026-10-06.md:154 | C18 | K18 |
| 899 | LGM-k14-36 | LGM docs/audits/k14-page-read-2026-10-06.md:172 | C18 | K18 |
| 900 | LGM-k14-37 | LGM docs/audits/k14-page-read-2026-10-06.md:217 | C18 | K18 |
| 901 | LGM-k14-38 | LGM docs/audits/k14-page-read-2026-10-06.md:220 | C18 | K18 |
| 902 | LGM-k14-39 | LGM docs/audits/k14-page-read-2026-10-06.md:235 | C18 | K18 |
| 903 | LGM-k14-40 | LGM docs/audits/k14-page-read-2026-10-06.md:238 | C18 | K18 |
| 904 | LGM-k14-41 | LGM docs/audits/k14-page-read-2026-10-06.md:241 | C18 | K18 |
| 905 | LGM-k14-42 | LGM docs/audits/k14-page-read-2026-10-06.md:244 | C18 | K18 |
| 906 | LGM-k14-43 | LGM docs/audits/k14-page-read-2026-10-06.md:295 | C18 | K18 |
| 907 | LGM-k14-44 | LGM docs/audits/k14-page-read-2026-10-06.md:298 | C18 | K18 |
| 908 | LGM-k14-45 | LGM docs/audits/k14-page-read-2026-10-06.md:304 | C18 | K18 |
| 909 | LGM-k14-46 | LGM docs/audits/k14-page-read-2026-10-06.md:307 | C18 | K18 |
| 910 | LGM-k14-47 | LGM docs/audits/k14-page-read-2026-10-06.md:316 | C18 | K18 |
| 911 | LGM-k14-48 | LGM docs/audits/k14-page-read-2026-10-06.md:343 | C18 | K18 |
| 912 | LGM-k14-49 | LGM docs/audits/k14-page-read-2026-10-06.md:349 | C18 | K18 |
| 913 | LGM-k14-50 | LGM docs/audits/k14-page-read-2026-10-06.md:352 | C18 | K18 |
| 914 | LGM-k14-51 | LGM docs/audits/k14-page-read-2026-10-06.md:436 | C18 | K18 |
| 915 | LGM-k14-52 | LGM docs/audits/k14-page-read-2026-10-06.md:463 | C18 | K18 |
| 916 | LGM-k14-53 | LGM docs/audits/k14-page-read-2026-10-06.md:469 | C18 | K18 |
| 917 | LGM-k14-54 | LGM docs/audits/k14-page-read-2026-10-06.md:502 | C18 | K18 |
| 918 | LGM-k14-55 | LGM docs/audits/k14-page-read-2026-10-06.md:555 | C18 | K18 |
| 919 | LGM-k14-56 | LGM docs/audits/k14-page-read-2026-10-06.md:579 | C18 | K18 |
| 920 | LGM-k14-57 | LGM docs/audits/k14-page-read-2026-10-06.md:582 | C18 | K18 |
| 921 | LGM-k14-58 | LGM docs/audits/k14-page-read-2026-10-06.md:585 | C18 | K18 |
| 922 | LGM-k14-59 | LGM docs/audits/k14-page-read-2026-10-06.md:623 | C18 | K18 |
| 923 | LGM-k14-60 | LGM docs/audits/k14-page-read-2026-10-06.md:632 | C18 | K18 |
| 924 | LGM-k14-61 | LGM docs/audits/k14-page-read-2026-10-06.md:635 | C18 | K18 |
| 925 | LGM-k14-62 | LGM docs/audits/k14-page-read-2026-10-06.md:642 | C18 | K18 |
| 926 | LGM-k18-L2 | LGM docs/audits/k18-closures.md:25 | C08 | K08 |
| 927 | LGM-k18-L4 | LGM docs/audits/k18-closures.md:27 | C15 | K15 |
| 928 | LGM-k18-L12 | LGM docs/audits/k18-closures.md:35 | C03 | K03 |
| 929 | LGM-k18-L13 | LGM docs/audits/k18-closures.md:36 | C09 | K09 |
| 930 | LGM-k18-L17 | LGM docs/audits/k18-closures.md:40 | C03 | K03 |
| 931 | LGM-k18-004 | LGM docs/audits/k18-closures.md:11 | C05 | K05 |
| 932 | LGM-k18-006 | LGM docs/audits/k18-closures.md:12 | C09 | K18 | (override)
| 933 | LGM-rs-01 | LGM ops/retired_strings.txt:12 | C02 | K02 |
| 934 | LGM-rs-02 | LGM ops/retired_strings.txt:72 | C08 | K08 |
| 935 | LGM-rs-03 | LGM ops/retired_strings.txt:74 | C03 | K03 |
| 936 | LGM-rs-04 | LGM ops/retired_strings.txt:75 | C08 | K08 |
| 937 | LGM-rs-05 | LGM ops/retired_strings.txt:76 | C08 | K08 |
| 938 | LGM-gt-1 | LGM docs/board/ground-truth.md:18 | C13 | K13 |
| 939 | LGM-gt-2 | LGM docs/board/ground-truth.md:59 | C13 | K13 |
| 940 | LGM-gt-3 | LGM docs/board/ground-truth.md:62 | C03 | K03 |
| 941 | LGM-gt-4 | LGM docs/board/ground-truth.md:90 | NEW:blind-instrument | K21 |
| 942 | LGM-gt-5 | LGM docs/board/ground-truth.md:165 | C13 | K13 |
| 943 | LGM-gt-6 | LGM docs/board/ground-truth.md:250 | C18 | K18 |
| 944 | LGM-gt-7 | LGM docs/board/ground-truth.md:258 | C18 | K18 |
| 945 | LGM-gt-8 | LGM docs/board/ground-truth.md:258 | C18 | K18 |
| 946 | LGM-gt-9 | LGM docs/board/ground-truth.md:258 | C18 | K18 |
| 947 | LGM-gt-10 | LGM docs/board/ground-truth.md:259 | C18 | K18 |
| 948 | LGM-gt-11 | LGM docs/board/ground-truth.md:266 | C18 | K18 |
| 949 | LGM-q1-1 | LGM docs/audits/quarterly-2026-10/q1-rebates.md:142 | C18 | K18 |
| 950 | LGM-q1-2 | LGM docs/audits/quarterly-2026-10/q1-rebates.md:164 | C02 | K02 |
| 951 | LGM-q1-3 | LGM docs/audits/quarterly-2026-10/q1-rebates.md:165 | C02 | K02 |
| 952 | LGM-sum-1 | LGM docs/audits/quarterly-2026-10/SUMMARY.md:15 | C02 | K02 |
| 953 | LGM-sum-2 | LGM docs/audits/quarterly-2026-10/SUMMARY.md:21 | C14 | K14 |
| 954 | LGM-q7-1 | LGM docs/audits/quarterly-2026-10/q7-search.md:57 | C09 | K09 |
| 955 | LGM-q7-2 | LGM docs/audits/quarterly-2026-10/q7-search.md:81 | C13 | K13 |
| 956 | LGM-k29-1 | LGM docs/audits/quarterly-2026-10/k29-sweep.md:74 | C13 | K13 |
| 957 | GCI-404-F3 | GCI docs/audits/gci-read-2026-08-25/404.html.md:203 | C08 | K08 |
| 958 | GCI-about-F-02 | GCI docs/audits/gci-read-2026-08-25/about.html.md:69 | C01 | K01 |
| 959 | GCI-about-F-07 | GCI docs/audits/gci-read-2026-08-25/about.html.md:207 | NEW:malformed-prose | K20 |
| 960 | GCI-about-F-08 | GCI docs/audits/gci-read-2026-08-25/about.html.md:222 | C03 | K03 |
| 961 | GCI-about-F-09 | GCI docs/audits/gci-read-2026-08-25/about.html.md:236 | C03 | K03 |
| 962 | GCI-about-F-13 | GCI docs/audits/gci-read-2026-08-25/about.html.md:316 | C01 | K01 |
| 963 | GCI-about-F-14 | GCI docs/audits/gci-read-2026-08-25/about.html.md:358 | C03 | K03 |
| 964 | GCI-about-GEN | GCI docs/audits/gci-read-2026-08-25/about.html.md:500 | C13 | K13 |
| 965 | GCI-airseal-F-02 | GCI docs/audits/gci-read-2026-08-25/air-sealing-greeley.html.md:186 | C03 | K03 |
| 966 | GCI-airseal-F-03 | GCI docs/audits/gci-read-2026-08-25/air-sealing-greeley.html.md:230 | C03 | K03 |
| 967 | GCI-airseal-F-04 | GCI docs/audits/gci-read-2026-08-25/air-sealing-greeley.html.md:262 | C08 | K08 |
| 968 | GCI-airseal-F-10 | GCI docs/audits/gci-read-2026-08-25/air-sealing-greeley.html.md:504 | C03 | K03 |
| 969 | GCI-area8-T-2 | GCI docs/audits/gci-read-2026-08-25/area-pages-8.md:158 | C01 | K01 |
| 970 | GCI-area8-T-3 | GCI docs/audits/gci-read-2026-08-25/area-pages-8.md:195 | C11 | K11 |
| 971 | GCI-area8-T-4 | GCI docs/audits/gci-read-2026-08-25/area-pages-8.md:242 | C08 | K08 |
| 972 | GCI-area8-T-5 | GCI docs/audits/gci-read-2026-08-25/area-pages-8.md:277 | C03 | K03 |
| 973 | GCI-area8-3c | GCI docs/audits/gci-read-2026-08-25/area-pages-8.md:419 | C03 | K03 |
| 974 | GCI-area8-W-1 | GCI docs/audits/gci-read-2026-08-25/area-pages-8.md:441 | C08 | K08 |
| 975 | GCI-area8-F-A1 | GCI docs/audits/gci-read-2026-08-25/area-pages-8.md:606 | C08 | K08 |
| 976 | GCI-area8-6c | GCI docs/audits/gci-read-2026-08-25/area-pages-8.md:787 | C03 | K03 |
| 977 | GCI-area8-6e | GCI docs/audits/gci-read-2026-08-25/area-pages-8.md:841 | C03 | K03 |
| 978 | GCI-area8-F-W1 | GCI docs/audits/gci-read-2026-08-25/area-pages-8.md:888 | NEW:malformed-prose | K20 |
| 979 | GCI-area8-F-E1 | GCI docs/audits/gci-read-2026-08-25/area-pages-8.md:915 | C08 | K08 |
| 980 | GCI-area8-F-C1 | GCI docs/audits/gci-read-2026-08-25/area-pages-8.md:1033 | C01 | K01 |
| 981 | GCI-area8-8b | GCI docs/audits/gci-read-2026-08-25/area-pages-8.md:1062 | C08 | K08 |
| 982 | GCI-blownwall-B-1 | GCI docs/audits/gci-read-2026-08-25/blown-in-and-wall.md:47 | C03 | K03 |
| 983 | GCI-blownwall-B-2 | GCI docs/audits/gci-read-2026-08-25/blown-in-and-wall.md:69 | C03 | K03 |
| 984 | GCI-blownwall-B-7 | GCI docs/audits/gci-read-2026-08-25/blown-in-and-wall.md:121 | C03 | K03 |
| 985 | GCI-blownwall-W-1 | GCI docs/audits/gci-read-2026-08-25/blown-in-and-wall.md:144 | C03 | K03 |
| 986 | GCI-blownwall-W-4 | GCI docs/audits/gci-read-2026-08-25/blown-in-and-wall.md:195 | C03 | K03 |
| 987 | GCI-contact-F2 | GCI docs/audits/gci-read-2026-08-25/contact.html.md:182 | C01 | K01 |
| 988 | GCI-contact-F4 | GCI docs/audits/gci-read-2026-08-25/contact.html.md:226 | C08 | K08 |
| 989 | GCI-contact-F9b | GCI docs/audits/gci-read-2026-08-25/contact.html.md:346 | C09 | K09 |
| 990 | GCI-contact-F9c | GCI docs/audits/gci-read-2026-08-25/contact.html.md:348 | C06 | K06 |
| 991 | GCI-contact-F9e | GCI docs/audits/gci-read-2026-08-25/contact.html.md:352 | C03 | K03 |
| 992 | GCI-contact-F9f | GCI docs/audits/gci-read-2026-08-25/contact.html.md:354 | C13 | K13 |
| 993 | GCI-crawlrem-F-R2 | GCI docs/audits/gci-read-2026-08-25/crawl-space-and-removal.md:86 | C03 | K03 |
| 994 | GCI-crawlrem-F-R3 | GCI docs/audits/gci-read-2026-08-25/crawl-space-and-removal.md:109 | C08 | K08 |
| 995 | GCI-crawlrem-F-R4 | GCI docs/audits/gci-read-2026-08-25/crawl-space-and-removal.md:138 | C03 | K03 |
| 996 | GCI-crawlrem-F-R6 | GCI docs/audits/gci-read-2026-08-25/crawl-space-and-removal.md:197 | C08 | K08 |
| 997 | GCI-crawlrem-F-R7 | GCI docs/audits/gci-read-2026-08-25/crawl-space-and-removal.md:223 | C03 | K03 |
| 998 | GCI-crawlrem-F-R10 | GCI docs/audits/gci-read-2026-08-25/crawl-space-and-removal.md:285 | C08 | K08 |
| 999 | GCI-crawlrem-F-R11 | GCI docs/audits/gci-read-2026-08-25/crawl-space-and-removal.md:314 | C08 | K08 |
| 1000 | GCI-crawlrem-F-R12 | GCI docs/audits/gci-read-2026-08-25/crawl-space-and-removal.md:337 | C03 | K03 |
| 1001 | GCI-crawlrem-F-R13 | GCI docs/audits/gci-read-2026-08-25/crawl-space-and-removal.md:357 | C03 | K03 |
| 1002 | GCI-crawlrem-F-C1 | GCI docs/audits/gci-read-2026-08-25/crawl-space-and-removal.md:395 | C03 | K03 |
| 1003 | GCI-crawlrem-F-C3 | GCI docs/audits/gci-read-2026-08-25/crawl-space-and-removal.md:457 | C08 | K08 |
| 1004 | GCI-crawlrem-F-C4 | GCI docs/audits/gci-read-2026-08-25/crawl-space-and-removal.md:465 | NEW:omitted-safety-caveat | K22 |
| 1005 | GCI-crawlrem-F-C7 | GCI docs/audits/gci-read-2026-08-25/crawl-space-and-removal.md:526 | C03 | K03 |
| 1006 | GCI-crawlrem-F-B4 | GCI docs/audits/gci-read-2026-08-25/crawl-space-and-removal.md:749 | C03 | K03 |
| 1007 | GCI-crawlrem-N1 | GCI docs/audits/gci-read-2026-08-25/crawl-space-and-removal.md:1104 | C11 | K11 |
| 1008 | GCI-crawlrem-N5 | GCI docs/audits/gci-read-2026-08-25/crawl-space-and-removal.md:1233 | C03 | K03 |
| 1009 | GCI-freezethaw-F1 | GCI docs/audits/gci-read-2026-08-25/freeze-thaw-cycles-greeley.html.md:41 | C09 | K09 |
| 1010 | GCI-freezethaw-F2 | GCI docs/audits/gci-read-2026-08-25/freeze-thaw-cycles-greeley.html.md:56 | C09 | K09 |
| 1011 | GCI-freezethaw-F5 | GCI docs/audits/gci-read-2026-08-25/freeze-thaw-cycles-greeley.html.md:159 | C03 | K03 |
| 1012 | GCI-freezethaw-F6 | GCI docs/audits/gci-read-2026-08-25/freeze-thaw-cycles-greeley.html.md:191 | C03 | K03 |
| 1013 | GCI-freezethaw-F7 | GCI docs/audits/gci-read-2026-08-25/freeze-thaw-cycles-greeley.html.md:226 | C03 | K03 |
| 1014 | GCI-freezethaw-F10a | GCI docs/audits/gci-read-2026-08-25/freeze-thaw-cycles-greeley.html.md:302 | C03 | K03 |
| 1015 | GCI-icedams-F4 | GCI docs/audits/gci-read-2026-08-25/ice-dams-greeley.html.md:275 | C09 | K09 |
| 1016 | GCI-icedams-F6 | GCI docs/audits/gci-read-2026-08-25/ice-dams-greeley.html.md:341 | NEW:contractor-voice | K16 |
| 1017 | GCI-icedams-F7 | GCI docs/audits/gci-read-2026-08-25/ice-dams-greeley.html.md:377 | NEW:omitted-safety-caveat | K22 |
| 1018 | GCI-icedams-F8 | GCI docs/audits/gci-read-2026-08-25/ice-dams-greeley.html.md:424 | C03 | K03 |
| 1019 | GCI-icedams-F10 | GCI docs/audits/gci-read-2026-08-25/ice-dams-greeley.html.md:464 | C08 | K08 |
| 1020 | GCI-icedams-F11 | GCI docs/audits/gci-read-2026-08-25/ice-dams-greeley.html.md:517 | C08 | K08 |
| 1021 | GCI-index-F-03 | GCI docs/audits/gci-read-2026-08-25/index.html.md:160 | C03 | K03 |
| 1022 | GCI-index-F-07 | GCI docs/audits/gci-read-2026-08-25/index.html.md:362 | NEW:contractor-voice | K16 |
| 1023 | GCI-index-F-08 | GCI docs/audits/gci-read-2026-08-25/index.html.md:392 | NEW:contractor-voice | K16 |
| 1024 | GCI-index-F-09 | GCI docs/audits/gci-read-2026-08-25/index.html.md:482 | C03 | K03 |
| 1025 | GCI-index-F-10 | GCI docs/audits/gci-read-2026-08-25/index.html.md:528 | C03 | K03 |
| 1026 | GCI-index-F-11 | GCI docs/audits/gci-read-2026-08-25/index.html.md:569 | C08 | K08 |
| 1027 | GCI-index-F-12 | GCI docs/audits/gci-read-2026-08-25/index.html.md:616 | C08 | K08 |
| 1028 | GCI-index-F-13 | GCI docs/audits/gci-read-2026-08-25/index.html.md:643 | NEW:malformed-prose | K20 |
| 1029 | GCI-index-F-14 | GCI docs/audits/gci-read-2026-08-25/index.html.md:666 | NEW:malformed-prose | K20 |
| 1030 | GCI-index-F-15 | GCI docs/audits/gci-read-2026-08-25/index.html.md:685 | C01 | K01 |
| 1031 | GCI-index-F-16 | GCI docs/audits/gci-read-2026-08-25/index.html.md:717 | C03 | K03 |
| 1032 | GCI-attic-F-01 | GCI docs/audits/gci-read-2026-08-25/insulation-attic-greeley.html.md:38 | C03 | K03 |
| 1033 | GCI-attic-F-02 | GCI docs/audits/gci-read-2026-08-25/insulation-attic-greeley.html.md:78 | C03 | K03 |
| 1034 | GCI-attic-F-08 | GCI docs/audits/gci-read-2026-08-25/insulation-attic-greeley.html.md:305 | C08 | K08 |
| 1035 | GCI-attic-F-10 | GCI docs/audits/gci-read-2026-08-25/insulation-attic-greeley.html.md:380 | C08 | K08 |
| 1036 | GCI-attic-F-11 | GCI docs/audits/gci-read-2026-08-25/insulation-attic-greeley.html.md:422 | C03 | K03 |
| 1037 | GCI-attic-F-13 | GCI docs/audits/gci-read-2026-08-25/insulation-attic-greeley.html.md:487 | C03 | K03 |
| 1038 | GCI-attic-F-14 | GCI docs/audits/gci-read-2026-08-25/insulation-attic-greeley.html.md:527 | C01 | K01 |
| 1039 | GCI-attic-F-18 | GCI docs/audits/gci-read-2026-08-25/insulation-attic-greeley.html.md:701 | C08 | K08 |
| 1040 | GCI-costcalc-C-01 | GCI docs/audits/gci-read-2026-08-25/insulation-cost-calculator-greeley.html.md:59 | C15 | K15 |
| 1041 | GCI-costcalc-C-02 | GCI docs/audits/gci-read-2026-08-25/insulation-cost-calculator-greeley.html.md:96 | C15 | K15 |
| 1042 | GCI-costcalc-C-03 | GCI docs/audits/gci-read-2026-08-25/insulation-cost-calculator-greeley.html.md:141 | C15 | K15 |
| 1043 | GCI-costcalc-C-04 | GCI docs/audits/gci-read-2026-08-25/insulation-cost-calculator-greeley.html.md:184 | C15 | K15 |
| 1044 | GCI-costcalc-C-05 | GCI docs/audits/gci-read-2026-08-25/insulation-cost-calculator-greeley.html.md:219 | C01 | K01 |
| 1045 | GCI-costcalc-F-01 | GCI docs/audits/gci-read-2026-08-25/insulation-cost-calculator-greeley.html.md:297 | C14 | K14 |
| 1046 | GCI-costcalc-H-01 | GCI docs/audits/gci-read-2026-08-25/insulation-cost-calculator-greeley.html.md:459 | C08 | K08 |
| 1047 | GCI-costcalc-P-01 | GCI docs/audits/gci-read-2026-08-25/insulation-cost-calculator-greeley.html.md:485 | C03 | K03 |
| 1048 | GCI-costcalc-P-03 | GCI docs/audits/gci-read-2026-08-25/insulation-cost-calculator-greeley.html.md:551 | C03 | K03 |
| 1049 | GCI-costcalc-P-04 | GCI docs/audits/gci-read-2026-08-25/insulation-cost-calculator-greeley.html.md:566 | NEW:contractor-voice | K16 |
| 1050 | GCI-costcalc-P-05 | GCI docs/audits/gci-read-2026-08-25/insulation-cost-calculator-greeley.html.md:589 | C08 | K08 |
| 1051 | GCI-insgreeley-F-06 | GCI docs/audits/gci-read-2026-08-25/insulation-greeley.html.md:396 | C03 | K03 |
| 1052 | GCI-payback-F-1 | GCI docs/audits/gci-read-2026-08-25/insulation-payback-calculator-greeley.html.md:73 | C15 | K15 |
| 1053 | GCI-payback-F-2 | GCI docs/audits/gci-read-2026-08-25/insulation-payback-calculator-greeley.html.md:139 | C03 | K03 |
| 1054 | GCI-payback-F-7 | GCI docs/audits/gci-read-2026-08-25/insulation-payback-calculator-greeley.html.md:405 | C15 | K15 |
| 1055 | GCI-payback-F-9 | GCI docs/audits/gci-read-2026-08-25/insulation-payback-calculator-greeley.html.md:463 | NEW:contractor-voice | K16 |
| 1056 | GCI-payback-F-10 | GCI docs/audits/gci-read-2026-08-25/insulation-payback-calculator-greeley.html.md:486 | C03 | K03 |
| 1057 | GCI-payback-F-11 | GCI docs/audits/gci-read-2026-08-25/insulation-payback-calculator-greeley.html.md:516 | C17 | K17 |
| 1058 | GCI-payback-F-13 | GCI docs/audits/gci-read-2026-08-25/insulation-payback-calculator-greeley.html.md:563 | C09 | K09 |
| 1059 | GCI-payback-F-14 | GCI docs/audits/gci-read-2026-08-25/insulation-payback-calculator-greeley.html.md:587 | C15 | K15 |
| 1060 | GCI-checker-F1 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-eligibility-checker.html.md:85 | C15 | K15 |
| 1061 | GCI-checker-F2 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-eligibility-checker.html.md:145 | C15 | K15 |
| 1062 | GCI-checker-F3 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-eligibility-checker.html.md:175 | C01 | K01 |
| 1063 | GCI-checker-F4 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-eligibility-checker.html.md:215 | C08 | K08 |
| 1064 | GCI-checker-F5 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-eligibility-checker.html.md:264 | C03 | K03 |
| 1065 | GCI-checker-F7 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-eligibility-checker.html.md:322 | C01 | K01 |
| 1066 | GCI-checker-F8 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-eligibility-checker.html.md:353 | C08 | K08 |
| 1067 | GCI-checker-F9 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-eligibility-checker.html.md:380 | C03 | K03 |
| 1068 | GCI-checker-F11 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-eligibility-checker.html.md:596 | C03 | K03 |
| 1069 | GCI-checker-F12 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-eligibility-checker.html.md:619 | C03 | K03 |
| 1070 | GCI-checker-F13 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-eligibility-checker.html.md:637 | C03 | K03 |
| 1071 | GCI-checker-N5 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-eligibility-checker.html.md:653 | C15 | K15 |
| 1072 | GCI-hub-F1 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-hub.html.md:20 | C15 | K15 |
| 1073 | GCI-hub-F5 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-hub.html.md:297 | C08 | K08 |
| 1074 | GCI-hub-F6 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-hub.html.md:335 | C03 | K03 |
| 1075 | GCI-hub-F7 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-hub.html.md:376 | NEW:caveat-detached | K22 |
| 1076 | GCI-hub-F9 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-hub.html.md:444 | C08 | K08 |
| 1077 | GCI-hub-F11 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-hub.html.md:521 | C03 | K03 |
| 1078 | GCI-hub-F12 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-hub.html.md:557 | NEW:malformed-prose | K20 |
| 1079 | GCI-hub-F14 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-hub.html.md:608 | C08 | K08 |
| 1080 | GCI-hub-F16 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-hub.html.md:672 | C08 | K08 |
| 1081 | GCI-hub-F17 | GCI docs/audits/gci-read-2026-08-25/insulation-rebate-hub.html.md:711 | NEW:malformed-prose | K20 |
| 1082 | GCI-llms-F-03 | GCI docs/audits/gci-read-2026-08-25/llms.txt.md:159 | C14 | K14 |
| 1083 | GCI-llms-F-05b | GCI docs/audits/gci-read-2026-08-25/llms.txt.md:227 | C13 | K13 |
| 1084 | GCI-llms-F-06 | GCI docs/audits/gci-read-2026-08-25/llms.txt.md:84 | C03 | K03 |
| 1085 | GCI-llms-F-10 | GCI docs/audits/gci-read-2026-08-25/llms.txt.md:500 | C13 | K13 |
| 1086 | GCI-llms-F-12 | GCI docs/audits/gci-read-2026-08-25/llms.txt.md:524 | C03 | K03 |
| 1087 | GCI-llms-F-13 | GCI docs/audits/gci-read-2026-08-25/llms.txt.md:536 | NEW:malformed-prose | K20 |
| 1088 | GCI-llms-F-14 | GCI docs/audits/gci-read-2026-08-25/llms.txt.md:558 | NEW:malformed-prose | K20 |
| 1089 | GCI-llms-F-15 | GCI docs/audits/gci-read-2026-08-25/llms.txt.md:570 | NEW:template-misapplied | K23 |
| 1090 | GCI-llms-F-16 | GCI docs/audits/gci-read-2026-08-25/llms.txt.md:582 | NEW:template-misapplied | K23 |
| 1091 | GCI-llms-F-17 | GCI docs/audits/gci-read-2026-08-25/llms.txt.md:594 | C01 | K01 |
| 1092 | GCI-llms-F-18 | GCI docs/audits/gci-read-2026-08-25/llms.txt.md:635 | C13 | K13 |
| 1093 | GCI-llms-F-19 | GCI docs/audits/gci-read-2026-08-25/llms.txt.md:655 | C03 | K03 |
| 1094 | GCI-llms-F-21 | GCI docs/audits/gci-read-2026-08-25/llms.txt.md:681 | C13 | K13 |
| 1095 | GCI-privacy-P-1 | GCI docs/audits/gci-read-2026-08-25/privacy.html.md:188 | C03 | K03 |
| 1096 | GCI-privacy-P-2 | GCI docs/audits/gci-read-2026-08-25/privacy.html.md:278 | C08 | K08 |
| 1097 | GCI-privacy-P-3 | GCI docs/audits/gci-read-2026-08-25/privacy.html.md:475 | C08 | K08 |
| 1098 | GCI-privacy-P-6 | GCI docs/audits/gci-read-2026-08-25/privacy.html.md:398 | C03 | K03 |
| 1099 | GCI-privacy-P-7 | GCI docs/audits/gci-read-2026-08-25/privacy.html.md:311 | C17 | K17 |
| 1100 | GCI-rcalc-F-1 | GCI docs/audits/gci-read-2026-08-25/r-value-calculator-greeley.html.md:90 | C03 | K03 |
| 1101 | GCI-rcalc-F-2 | GCI docs/audits/gci-read-2026-08-25/r-value-calculator-greeley.html.md:112 | C03 | K03 |
| 1102 | GCI-rcalc-F-3 | GCI docs/audits/gci-read-2026-08-25/r-value-calculator-greeley.html.md:135 | C08 | K08 |
| 1103 | GCI-rcalc-F-5 | GCI docs/audits/gci-read-2026-08-25/r-value-calculator-greeley.html.md:172 | C08 | K08 |
| 1104 | GCI-rcalc-F-6 | GCI docs/audits/gci-read-2026-08-25/r-value-calculator-greeley.html.md:194 | C15 | K15 |
| 1105 | GCI-rcalc-F-7 | GCI docs/audits/gci-read-2026-08-25/r-value-calculator-greeley.html.md:211 | C03 | K03 |
| 1106 | GCI-rcalc-F-9 | GCI docs/audits/gci-read-2026-08-25/r-value-calculator-greeley.html.md:252 | C15 | K15 |
| 1107 | GCI-rcalc-F-10 | GCI docs/audits/gci-read-2026-08-25/r-value-calculator-greeley.html.md:270 | C15 | K15 |
| 1108 | GCI-rcalc-F-12 | GCI docs/audits/gci-read-2026-08-25/r-value-calculator-greeley.html.md:304 | C08 | K08 |
| 1109 | GCI-rcalc-F-15 | GCI docs/audits/gci-read-2026-08-25/r-value-calculator-greeley.html.md:358 | C13 | K13 |
| 1110 | GCI-res-R-01 | GCI docs/audits/gci-read-2026-08-25/resources-and-r-value-altitude.md:37 | C05 | K05 |
| 1111 | GCI-res-R-02 | GCI docs/audits/gci-read-2026-08-25/resources-and-r-value-altitude.md:103 | C05 | K05 |
| 1112 | GCI-res-R-03 | GCI docs/audits/gci-read-2026-08-25/resources-and-r-value-altitude.md:134 | C03 | K03 |
| 1113 | GCI-res-R-08 | GCI docs/audits/gci-read-2026-08-25/resources-and-r-value-altitude.md:282 | C08 | K08 |
| 1114 | GCI-res-R-09 | GCI docs/audits/gci-read-2026-08-25/resources-and-r-value-altitude.md:313 | C08 | K08 |
| 1115 | GCI-res-R-15 | GCI docs/audits/gci-read-2026-08-25/resources-and-r-value-altitude.md:445 | C03 | K03 |
| 1116 | GCI-res-RV-02 | GCI docs/audits/gci-read-2026-08-25/resources-and-r-value-altitude.md:535 | C08 | K08 |
| 1117 | GCI-res-RV-03 | GCI docs/audits/gci-read-2026-08-25/resources-and-r-value-altitude.md:584 | C08 | K08 |
| 1118 | GCI-res-RV-06 | GCI docs/audits/gci-read-2026-08-25/resources-and-r-value-altitude.md:706 | C08 | K08 |
| 1119 | GCI-res-RV-07 | GCI docs/audits/gci-read-2026-08-25/resources-and-r-value-altitude.md:738 | C03 | K03 |
| 1120 | GCI-res-RV-08 | GCI docs/audits/gci-read-2026-08-25/resources-and-r-value-altitude.md:777 | NEW:malformed-prose | K20 |
| 1121 | GCI-sfea-SF-03 | GCI docs/audits/gci-read-2026-08-25/spray-foam-and-energy-audit.md:155 | C03 | K03 |
| 1122 | GCI-sfea-SF-04 | GCI docs/audits/gci-read-2026-08-25/spray-foam-and-energy-audit.md:189 | C03 | K03 |
| 1123 | GCI-sfea-SF-05 | GCI docs/audits/gci-read-2026-08-25/spray-foam-and-energy-audit.md:225 | C03 | K03 |
| 1124 | GCI-sfea-SF-10 | GCI docs/audits/gci-read-2026-08-25/spray-foam-and-energy-audit.md:406 | C06 | K06 |
| 1125 | GCI-sfea-EA-01b | GCI docs/audits/gci-read-2026-08-25/spray-foam-and-energy-audit.md:1008 | C01 | K01 |
| 1126 | GCI-sfea-EA-02 | GCI docs/audits/gci-read-2026-08-25/spray-foam-and-energy-audit.md:568 | C03 | K03 |
| 1127 | GCI-sfea-EA-03 | GCI docs/audits/gci-read-2026-08-25/spray-foam-and-energy-audit.md:607 | C08 | K08 |
| 1128 | GCI-sfea-EA-04 | GCI docs/audits/gci-read-2026-08-25/spray-foam-and-energy-audit.md:646 | C08 | K08 |
| 1129 | GCI-sfea-EA-06 | GCI docs/audits/gci-read-2026-08-25/spray-foam-and-energy-audit.md:722 | C03 | K03 |
| 1130 | GCI-sfea-EA-07 | GCI docs/audits/gci-read-2026-08-25/spray-foam-and-energy-audit.md:757 | NEW:caveat-detached | K22 |
| 1131 | GCI-sfea-corr2 | GCI docs/audits/gci-read-2026-08-25/spray-foam-and-energy-audit.md:1081 | C09 | K09 |
| 1132 | GCI-symp-P2 | GCI docs/audits/gci-read-2026-08-25/symptom-diagnostics.md:67 | C08 | K08 |
| 1133 | GCI-symp-P6 | GCI docs/audits/gci-read-2026-08-25/symptom-diagnostics.md:159 | C08 | K08 |
| 1134 | GCI-symp-P8 | GCI docs/audits/gci-read-2026-08-25/symptom-diagnostics.md:216 | C03 | K03 |
| 1135 | GCI-symp-P9 | GCI docs/audits/gci-read-2026-08-25/symptom-diagnostics.md:258 | C03 | K03 |
| 1136 | GCI-symp-P10 | GCI docs/audits/gci-read-2026-08-25/symptom-diagnostics.md:277 | C03 | K03 |
| 1137 | GCI-symp-P11 | GCI docs/audits/gci-read-2026-08-25/symptom-diagnostics.md:301 | C03 | K03 |
| 1138 | GCI-symp-U6 | GCI docs/audits/gci-read-2026-08-25/symptom-diagnostics.md:573 | C03 | K03 |
| 1139 | GCI-symp-U7 | GCI docs/audits/gci-read-2026-08-25/symptom-diagnostics.md:606 | C08 | K08 |
| 1140 | GCI-symp-U10 | GCI docs/audits/gci-read-2026-08-25/symptom-diagnostics.md:690 | C08 | K08 |
| 1141 | GCI-verm-F2 | GCI docs/audits/gci-read-2026-08-25/vermiculite-insulation-greeley.html.md:129 | C08 | K03 | (override)
| 1142 | GCI-verm-F7 | GCI docs/audits/gci-read-2026-08-25/vermiculite-insulation-greeley.html.md:348 | C08 | K08 |
| 1143 | GCI-verm-F9 | GCI docs/audits/gci-read-2026-08-25/vermiculite-insulation-greeley.html.md:411 | C08 | K08 |
| 1144 | GCI-verm-F10 | GCI docs/audits/gci-read-2026-08-25/vermiculite-insulation-greeley.html.md:443 | C08 | K08 |
| 1145 | GCI-verm-F14 | GCI docs/audits/gci-read-2026-08-25/vermiculite-insulation-greeley.html.md:569 | C03 | K03 |
| 1146 | GCI-verm-F15 | GCI docs/audits/gci-read-2026-08-25/vermiculite-insulation-greeley.html.md:602 | C08 | K08 |
| 1147 | GCI-xcut-1 | GCI docs/audits/gci-read-2026-08-25/cross-cutting-sweep.md:83 | C05 | K05 |
| 1148 | GCI-xcut-2 | GCI docs/audits/gci-read-2026-08-25/cross-cutting-sweep.md:983 | C05 | K05 |
| 1149 | GCI-xcut-3 | GCI docs/audits/gci-read-2026-08-25/cross-cutting-sweep.md:134 | NEW:template-misapplied | K23 |
| 1150 | GCI-xcut-4 | GCI docs/audits/gci-read-2026-08-25/cross-cutting-sweep.md:151 | C17 | K17 |
| 1151 | GCI-xcut-5 | GCI docs/audits/gci-read-2026-08-25/cross-cutting-sweep.md:190 | C08 | K08 |
| 1152 | GCI-xcut-6 | GCI docs/audits/gci-read-2026-08-25/cross-cutting-sweep.md:273 | C16 | K16 |
| 1153 | GCI-xcut-7 | GCI docs/audits/gci-read-2026-08-25/cross-cutting-sweep.md:338 | C03 | K03 |
| 1154 | GCI-xcut-8 | GCI docs/audits/gci-read-2026-08-25/cross-cutting-sweep.md:344 | C08 | K08 |
| 1155 | GCI-xcut-9 | GCI docs/audits/gci-read-2026-08-25/cross-cutting-sweep.md:383 | C03 | K03 |
| 1156 | GCI-xcut-10 | GCI docs/audits/gci-read-2026-08-25/cross-cutting-sweep.md:423 | C06 | K06 |
| 1157 | GCI-xcut-12 | GCI docs/audits/gci-read-2026-08-25/cross-cutting-sweep.md:520 | C03 | K03 |
| 1158 | GCI-xcut-13 | GCI docs/audits/gci-read-2026-08-25/cross-cutting-sweep.md:672 | C03 | K03 |
| 1159 | GCI-xcut-14 | GCI docs/audits/gci-read-2026-08-25/cross-cutting-sweep.md:749 | C09 | K09 |
| 1160 | GCI-xcut-15 | GCI docs/audits/gci-read-2026-08-25/cross-cutting-sweep.md:762 | C05 | K05 |
| 1161 | GCI-xcut-16 | GCI docs/audits/gci-read-2026-08-25/cross-cutting-sweep.md:804 | C08 | K08 |
| 1162 | GCI-xcut-17 | GCI docs/audits/gci-read-2026-08-25/cross-cutting-sweep.md:812 | C17 | K17 |
| 1163 | GCI-xcut-18 | GCI docs/audits/gci-read-2026-08-25/cross-cutting-sweep.md:817 | C09 | K09 |
| 1164 | GCI-xcut-19 | GCI docs/audits/gci-read-2026-08-25/cross-cutting-sweep.md:998 | NEW:blind-instrument | K21 |
| 1165 | GCI-xcut-20 | GCI docs/audits/gci-read-2026-08-25/cross-cutting-sweep.md:1035 | C03 | K03 |
| 1166 | GCI-cit-1 | GCI docs/audits/gci-read-2026-08-25/CITATIONS_VERIFIED.md:25 | C03 | K03 |
| 1167 | GCI-cit-2 | GCI docs/audits/gci-read-2026-08-25/CITATIONS_VERIFIED.md:45 | C04 | K04 |
| 1168 | GCI-cit-3 | GCI docs/audits/gci-read-2026-08-25/CITATIONS_VERIFIED.md:56 | C03 | K03 |
| 1169 | GCI-cit-4 | GCI docs/audits/gci-read-2026-08-25/CITATIONS_VERIFIED.md:64 | C03 | K03 |
| 1170 | GCI-cit-5 | GCI docs/audits/gci-read-2026-08-25/CITATIONS_VERIFIED.md:72 | C03 | K03 |
| 1171 | GCI-cit-6 | GCI docs/audits/gci-read-2026-08-25/CITATIONS_VERIFIED.md:82 | C02 | K02 |
| 1172 | GCI-cit-7 | GCI docs/audits/gci-read-2026-08-25/CITATIONS_VERIFIED.md:94 | C03 | K03 |
| 1173 | GCI-cit-8 | GCI docs/audits/gci-read-2026-08-25/CITATIONS_VERIFIED.md:134 | C03 | K03 |
| 1174 | GCI-cit-9 | GCI docs/audits/gci-read-2026-08-25/CITATIONS_VERIFIED.md:142 | C03 | K03 |
| 1175 | GCI-cit-10 | GCI docs/audits/gci-read-2026-08-25/CITATIONS_VERIFIED.md:155 | C03 | K03 |
| 1176 | GCI-cit-11 | GCI docs/audits/gci-read-2026-08-25/CITATIONS_VERIFIED.md:195 | C03 | K03 |
| 1177 | GCI-cit-12 | GCI docs/audits/gci-read-2026-08-25/CITATIONS_VERIFIED.md:188 | C18 | K18 |
| 1178 | GCI-cit-13 | GCI docs/audits/gci-read-2026-08-25/CITATIONS_VERIFIED.md:226 | C03 | K03 |
| 1179 | GCI-cit-14 | GCI docs/audits/gci-read-2026-08-25/CITATIONS_VERIFIED.md:242 | C13 | K13 |
| 1180 | GCI-cit-15 | GCI docs/audits/gci-read-2026-08-25/CITATIONS_VERIFIED.md:238 | NEW:blind-instrument | K21 |
| 1181 | GCI-cit-16 | GCI docs/audits/gci-read-2026-08-25/CITATIONS_VERIFIED.md:246 | C03 | K03 |
| 1182 | GCI-cit-17 | GCI docs/audits/gci-read-2026-08-25/CITATIONS_VERIFIED.md:255 | NEW:blind-instrument | K21 |
| 1183 | GCI-cit-18 | GCI docs/audits/gci-read-2026-08-25/CITATIONS_VERIFIED.md:261 | C03 | K03 |
| 1184 | GCI-fix-1 | GCI docs/audits/gci-read-2026-08-25/FIX_PLAN_CITATIONS.md:103 | C03 | K03 |
| 1185 | GCI-rb-1 | GCI docs/audits/gci-read-2026-08-25/READ_BRIEF.md:127 | C18 | K18 |
| 1186 | GCI-rb-2 | GCI docs/audits/gci-read-2026-08-25/READ_BRIEF.md:131 | C18 | K18 |
| 1187 | GCI-k15c-1 | GCI docs/audits/k15-open-list-closures.md:7 | C13 | K13 |
| 1188 | GCI-k15-1 | GCI docs/audits/k15-page-read-2026-10-06.md:20 | C18 | K18 |
| 1189 | GCI-k15-2 | GCI docs/audits/k15-page-read-2026-10-06.md:30 | C18 | K18 |
| 1190 | GCI-k15-3 | GCI docs/audits/k15-page-read-2026-10-06.md:35 | C18 | K18 |
| 1191 | GCI-k15-4 | GCI docs/audits/k15-page-read-2026-10-06.md:43 | C02 | K02 |
| 1192 | GCI-k15-5 | GCI docs/audits/k15-page-read-2026-10-06.md:53 | C18 | K18 |
| 1193 | GCI-k15-6 | GCI docs/audits/k15-page-read-2026-10-06.md:54 | C18 | K18 |
| 1194 | GCI-k15-7 | GCI docs/audits/k15-page-read-2026-10-06.md:57 | C18 | K18 |
| 1195 | GCI-k15-8 | GCI docs/audits/k15-page-read-2026-10-06.md:60 | C18 | K18 |
| 1196 | GCI-k15-9 | GCI docs/audits/k15-page-read-2026-10-06.md:61 | C18 | K18 |
| 1197 | GCI-k15-10 | GCI docs/audits/k15-page-read-2026-10-06.md:62 | C18 | K18 |
| 1198 | GCI-k15-11 | GCI docs/audits/k15-page-read-2026-10-06.md:63 | C18 | K18 |
| 1199 | GCI-k15-12 | GCI docs/audits/k15-page-read-2026-10-06.md:64 | C18 | K18 |
| 1200 | GCI-k15-13 | GCI docs/audits/k15-page-read-2026-10-06.md:65 | C18 | K18 |
| 1201 | GCI-k15-14 | GCI docs/audits/k15-page-read-2026-10-06.md:68 | C08 | K08 |
| 1202 | GCI-k15-15 | GCI docs/audits/k15-page-read-2026-10-06.md:74 | C18 | K18 |
| 1203 | GCI-k15-16 | GCI docs/audits/k15-page-read-2026-10-06.md:75 | C18 | K18 |
| 1204 | GCI-k15-17 | GCI docs/audits/k15-page-read-2026-10-06.md:76 | C18 | K18 |
| 1205 | GCI-k15-18 | GCI docs/audits/k15-page-read-2026-10-06.md:79 | C18 | K18 |
| 1206 | GCI-k15-19 | GCI docs/audits/k15-page-read-2026-10-06.md:82 | C18 | K18 |
| 1207 | GCI-k15-20 | GCI docs/audits/k15-page-read-2026-10-06.md:83 | C08 | K08 |
| 1208 | GCI-k15-21 | GCI docs/audits/k15-page-read-2026-10-06.md:84 | C08 | K08 |
| 1209 | GCI-k15-22 | GCI docs/audits/k15-page-read-2026-10-06.md:87 | C18 | K18 |
| 1210 | GCI-k15-23 | GCI docs/audits/k15-page-read-2026-10-06.md:88 | C18 | K18 |
| 1211 | GCI-k15-24 | GCI docs/audits/k15-page-read-2026-10-06.md:89 | C18 | K18 |
| 1212 | GCI-k15-27 | GCI docs/audits/k15-page-read-2026-10-06.md:97 | C18 | K18 |
| 1213 | GCI-k15-28 | GCI docs/audits/k15-page-read-2026-10-06.md:98 | C18 | K18 |
| 1214 | GCI-k15-29 | GCI docs/audits/k15-page-read-2026-10-06.md:99 | C18 | K18 |
| 1215 | GCI-k15-30 | GCI docs/audits/k15-page-read-2026-10-06.md:102 | C18 | K18 |
| 1216 | GCI-k15-31 | GCI docs/audits/k15-page-read-2026-10-06.md:103 | C18 | K18 |
| 1217 | GCI-k15-33 | GCI docs/audits/k15-page-read-2026-10-06.md:109 | C18 | K18 |
| 1218 | GCI-k15-34 | GCI docs/audits/k15-page-read-2026-10-06.md:110 | C08 | K08 |
| 1219 | GCI-k15-35 | GCI docs/audits/k15-page-read-2026-10-06.md:113 | C08 | K08 |
| 1220 | GCI-k19-1 | GCI docs/audits/k19-closures.md:25 | C03 | K03 |
| 1221 | GCI-k19-2 | GCI docs/audits/k19-closures.md:27 | C18 | K18 |
| 1222 | GCI-k19-3 | GCI docs/audits/k19-closures.md:28 | C11 | K11 |
| 1223 | GCI-k19-4 | GCI docs/audits/k19-closures.md:29 | C13 | K13 |
| 1224 | GCI-k19-5 | GCI docs/audits/k19-closures.md:32 | C13 | K13 |
| 1225 | GCI-q1-1 | GCI docs/audits/quarterly-2026-10/q1-rebates.md:98 | C02 | K02 |
| 1226 | GCI-q1-2 | GCI docs/audits/quarterly-2026-10/q1-rebates.md:107 | C02 | K02 |
| 1227 | GCI-q7-1 | GCI docs/audits/quarterly-2026-10/q7-search.md:57 | C09 | K09 |
| 1228 | GCI-qs-1 | GCI docs/audits/quarterly-2026-10/SUMMARY.md:54 | C14 | K14 |
| 1229 | GCI-k30-1 | GCI docs/audits/quarterly-2026-10/k30-sweep.md:47 | C03 | K03 |
| 1230 | GCI-k30-2 | GCI docs/audits/quarterly-2026-10/k30-sweep.md:7 | NEW:blind-instrument | K21 |
| 1231 | GCI-gt-1 | GCI docs/board/ground-truth.md:5 | C01 | K01 |
| 1232 | GCI-gt-2 | GCI docs/board/ground-truth.md:79 | C03 | K03 |
| 1233 | GCI-gt-3 | GCI docs/board/ground-truth.md:96 | NEW:blind-instrument | K21 |
| 1234 | GCI-gt-4 | GCI docs/board/ground-truth.md:152 | C01 | K01 |
| 1235 | GCI-gt-5 | GCI docs/board/ground-truth.md:196 | NEW:blind-instrument | K21 |
| 1236 | GCI-gt-6 | GCI docs/board/ground-truth.md:300 | C02 | K02 |
| 1237 | GCI-gt-7 | GCI docs/board/ground-truth.md:339 | C18 | K18 |
| 1238 | GCI-gt-8 | GCI docs/board/ground-truth.md:339 | C18 | K18 |
| 1239 | GCI-gt-9 | GCI docs/board/ground-truth.md:342 | C18 | K18 |
| 1240 | GCI-gt-10 | GCI docs/board/ground-truth.md:342 | C07 | K07 |
| 1241 | GCI-rs-1 | GCI ops/retired_strings.txt:24 | C03 | K03 |
| 1242 | GCI-rs-2 | GCI ops/retired_strings.txt:27 | C03 | K03 |
| 1243 | GCI-rs-5 | GCI ops/retired_strings.txt:60 | C01 | K01 |
| 1244 | GCI-rs-6 | GCI ops/retired_strings.txt:66 | C01 | K01 |
