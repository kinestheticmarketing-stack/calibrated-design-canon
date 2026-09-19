# Claim gate — git-replay re-score, 2026-09-19

R1 of a 4-row pass. This row repaired six things in R5 and the shared SRC
surface, and re-ran the git-replay defect score to prove none of them removed
real detection. It changed no page, no copy, no generator and nothing in any
property repo.

Gate under test: canon `ops/claim_gate/` at the head of this row's work.
Comparison point: canon `9dc1277`, this lane's base, i.e. the gate exactly as
it stood before this pass.

Method, identical to `GATE_CLOSE_2026-09-18.md`: 20 detached worktrees under
`/tmp/r5pass/r1/wt`, one per pre-fix SHA; `--today` set to each fixing commit's
date; a scratch copy of `ops/claim_gate/` whose ONLY difference from canon is
`min_artifacts` / `expected_html` set to `10` on all three configs (both are
floors, so the empty-corpus trap is preserved while smaller historical trees
can run at all). All 20 worktrees removed and pruned afterwards; `git worktree
list` on all four repos shows none remaining.

**All 20 trees run and exit 1. None exits 2.** The `dci-4cf7a52` exit-2 that
`GATE_CLOSE_2026-09-18.md` reported as a live control-contamination defect is
gone — that tree now exits 1.

---

## THE RESULT

### **20 CAUGHT · 3 PARTIAL · 2 MISSED — and the same 20 / 3 / 2 at canon `9dc1277`.**

```
$ diff <(python3 score_base.py) <(python3 score.py)
IDENTICAL: every one of the 25 rows scores the same before and after this pass
```

**Not one of the 25 rows changed verdict, changed its evidence line, or changed
a single count between canon `9dc1277` and this pass's head.** The six repairs
in this pass removed no detection anywhere in the replay.

Row-by-row, at this pass's head (identical at `9dc1277`):

| # | defect | repo @ pre-fix SHA | verdict | evidence |
|---|---|---|---|---|
| 1 | Fabricated quotation, 11 pages | lgm `8b0f1a9` | CAUGHT | 11 `XCEL_BLOWER_DOOR` adjudicated rows |
| 2a | Wrong utility, prose | gci `e912eee` | CAUGHT | 26 Atmos / `scope=Severance` rows |
| 2b | Wrong utility, `og:image` | gci `e912eee` | MISSED | 0 adjudicated `og-image.svg` rows; 1 raised and enumerated in the removed list |
| 3a | Retired eligibility, Lafayette | lgm `a2ba5a6` | CAUGHT | 2 `whe_audit_entry_path_begin_with` rows |
| 3b | Retired eligibility, prerequisite | dci `130921c` | CAUGHT | 7 `air_sealing_is_a_prerequisite` rows |
| 4a | Invented pathways, long form | dci `f08bb9f` | CAUGHT | 104 `installed_and_invoiced_by_dec_31_2026` rows |
| 4b | Short-form `Dec. 31, 2026` | dci `2a59a97` | CAUGHT | R7 adjudicated 4, one carrying `Dec. 31` |
| 4c | The invented fifth Xcel program | dci `f08bb9f` | CAUGHT | 227 `forbidden-program-name` rows |
| 5a | 198 rebate dollar figures | dci `169bb3c` | CAUGHT | `T1 $-anchored 222` |
| 5b | 133 rebate dollar figures | lgm `604d052` | PARTIAL | `$1.16` 75 rows, `$0.77` 43 rows, R3 ADJ 127 |
| 5c | 206 rebate dollar figures | gci `236c464` | PARTIAL | 7 distinct `$` figures across 16 files; `T1 $-anchored 179` |
| 5d | Bare-digit cap `1550 / 0.75` | gci `e994484` | CAUGHT | 2 rows carrying `1550` |
| 6 | Self-contradicting calculator | dci `58c44eb` | CAUGHT | R6 adjudicated 15 |
| 7a | Stacking, 70 of 72 pages | dci `bcb64a3` | CAUGHT | R4 adjudicated 444 |
| 7b | Stacking | dci `dd88de3` | CAUGHT | R4 adjudicated 53 |
| 7c | Stacking | dci `b5635c9` | CAUGHT | R4 adjudicated 73 |
| 7d | FAQPage stacking denial | gci `e994484` | CAUGHT | 5 `insulation-rebate-hub.html` rows, R4 ADJ 81 |
| 7e | Knob-and-tube stacking denial | lgm `2563a56` | CAUGHT | 2 knob-and-tube rows, R4 ADJ 7 |
| 7f | `llms.txt` rebate-stack | dci `d1b6078` | CAUGHT | 1 `llms.txt` row, R4 ADJ 34 |
| 8 | Uncited `25-40%` on 16 pages | dci `4cf7a52` | PARTIAL | 15 of 16 distinct pages |
| 9a | Review date before the page existed | dci `539670e` | CAUGHT | 16 `precedes-creation` rows |
| 9b | `contact.html` date disagreement | gci `12dfcbf` | CAUGHT | 1 `surfaces-disagree` row |
| 10 | Hidden `calc_output` | dci `cb675ab` | MISSED | 0 `N3b` rows |
| 11 | Dangling promise | gci `e994484` | CAUGHT | 2 `insulation-johnstown` rows, R10 ADJ 4 |
| 12 | Embed frame / `llms.txt` corpus hole | dci `539670e` | CAUGHT | embed frame line present, embed artifact in the read set |

---

## THE ONE ROW THAT DIFFERS FROM 21/25, AND WHY IT IS NOT THIS PASS

`GATE_CLOSE_2026-09-18.md` scored **21 CAUGHT / 2 PARTIAL / 2 MISSED** at canon
`eafada2`. This re-score reads **20 / 3 / 2**. The single difference is row
**5c**, GCI's 206 rebate dollar figures, which that pass scored CAUGHT on
"9 of 9 distinct figures across 24 of 24 files" and which now measures:

```
canon 9dc1277 (BEFORE)   distinct $ figures 7 ['$1,075', '$1,150', '$1,325',
                                               '$1,550', '$125', '$575', '$663']
                         distinct files 16
canon HEAD    (AFTER)    distinct $ figures 7 ['$1,075', '$1,150', '$1,325',
                                               '$1,550', '$125', '$575', '$663']
                         distinct files 16
```

**Identical before and after this pass, so this pass did not cause it.** The
regression sits somewhere between canon `eafada2` (2026-09-18) and canon
`9dc1277` (this lane's base) and is recorded here rather than fixed, because
this row's scope is R5 and the SRC surface.

The cause is visible in the report and is a known class: on that tree R3's
`cost_context_markers` filter removes **119** `$`-bearing rows — the same
over-removal already documented for row 5b, where "per square foot" in
`cost_context_markers` pardons a payout schedule that is *denominated* per
square foot. Full removal tally for `$`-bearing R3 rows on `gci-236c464`:

```
R3 ADJ: 91
  removed 119  by  cost_context_markers (Ruling 2 -- costs, not payouts)
  removed 87   by  code_context_markers (IECC / ENERGY STAR / R-value)
  removed 56   by  structural non-money numeral (URL/attribute, XML or SVG
                   coordinate, telephone, postal code, statute or print code)
  removed 31   by  allowed_structure_percentages (Ruling 2, none added)
  removed 14   by  allowed_figures (per-property Director ruling)
  removed 3    by  generator SRC restatement of prose that already renders
  removed 2    by  four-digit 1900-2099 cleared as a YEAR
```

**OPEN, MEASURED, NOT CLOSED HERE.** Narrowing `cost_context_markers` so that a
payout *denominated* in a rate is not mistaken for an installed cost closes 5b
and 5c together.

---

## WHAT THIS PASS CHANGED, FOR THE NEXT SESSION

1. **`ctx.pool()` now refuses a generator string run that is a stylesheet or a
   script bundle**, exactly as it already refused a `<script>` / `<style>` BODY
   on a rendered artifact. Every proposition rule is affected. The gate prints
   `SRC CODE SURFACES EXCLUDED FROM THE PROPOSITION POOL` with the run count,
   the character count and every locator, so the exclusion is never silent.
   Detector: brace density >= 0.40 corroborated by five CSS declarations or
   three JavaScript markers. Measured separation over all 6,203 generator
   string runs of 40+ characters on the three properties: 6,166 at 0.00, one at
   0.074, **nothing between 0.08 and 0.67**, 36 at 0.67-1.00.
2. **`ctx.src_dup()` no longer slices to 48 characters.** The silent miss it
   carried is closed and control `R5-SRCPREFIX` holds it.
3. **`R5.derivable_constants` is wired** (`rule_R5.f_deriv`) and DCI's config
   carries the atmospheric-pressure entry with its ICAO derivation.
4. **`R5.publisher_short_forms` and `R5.subject_attribution_verbs` are new**
   config keys, read only by `_pub_subject`. `"estimates"` is deliberately NOT
   in `R1.attribution_verbs` and must not be added: that list feeds a proximity
   test that cannot tell which noun the verb belongs to.
5. **`f_instat`'s threshold is 4**, re-derived from a measured near-miss sweep,
   and its tokenizer folds morphology and letter/digit boundaries
   (`_r5_words`). The sweep is recorded in full in the comment above `f_instat`.
6. **R5 gained an interrogative guard.** A question asserts no proposition;
   factive frames ("did you know ...") are excluded from the guard.

Control count went 32 -> 40 positive controls, each with a repair counterpart
(`CONTROLS: 40 positive DETECTED, 0 MISSED · 17 negative clean, 0 FALSE ALARM`,
`REPAIR TESTS: 40 repaired-clean, 0 FIRE ON REPAIRED, 0 NOT TESTED`). The seven
added are R5-INSTAT, R5-QUESTION, R5-SUBJECT, R5-SHORTFORM, R5-DERIVABLE,
R5-SRCCODE, R5-SRCPREFIX, plus R2e for the SRC code/prose split on R2.
