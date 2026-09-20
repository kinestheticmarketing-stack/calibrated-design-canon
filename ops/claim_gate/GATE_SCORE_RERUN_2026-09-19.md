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
$ cd ops/claim_gate/replay
$ ./prepare.sh              # scratch canon from the working tree
$ ./replay.sh               # 20 pre-fix trees
$ python3 score.py | tail -3
SCORE: 20 CAUGHT / 3 PARTIAL / 2 MISSED   (of 25)
```

Run again with `./prepare.sh 9dc1277` for the before side and diffed:

```
$ diff <(python3 score.py)   # after
        <(python3 score.py)  # before, with REPLAY_OUT pointing at the base run
IDENTICAL: every one of the 25 rows scores the same before and after this pass
```

**CORRECTED 2026-09-19 (seventh adversarial read, k1).** The first revision of
this document cited `score_base.py` and `score.py` as its verification command
and **neither existed in any commit** — the board's Project Rule requires a
command a reader can run, and that one could not be run by anyone including its
author. The harness is now committed at `ops/claim_gate/replay/` and the
command above is the real one.

**Not one of the 25 rows changed VERDICT or evidence line between canon
`9dc1277` and this pass's head.** RAW counts did move and the first revision's
"changed a single count" was overstated; the correct statement is that no
ADJUDICATED verdict changed. The repairs in this pass removed no detection
anywhere in the replay.

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

## THE ONE ROW THAT DIFFERS FROM 21/25 — AND `21` WAS THE INFLATED NUMBER

`GATE_CLOSE_2026-09-18.md` scored **21 CAUGHT / 2 PARTIAL / 2 MISSED** at canon
`eafada2`. This re-score reads **20 / 3 / 2**. The single difference is row
**5c**, GCI's 206 rebate dollar figures, which that pass scored CAUGHT on
"9 of 9 distinct figures across 24 of 24 files" and which this document first
scored PARTIAL and then **wrongly attributed to a regression between `eafada2`
and `9dc1277`.**

**THAT REGRESSION DOES NOT EXIST. RETRACTED.** The first revision never ran the
replay at `eafada2` — it inferred the drop from the other document's prose. The
seventh adversarial read caught that, and running it settles it:

```
canon eafada2   exit 1   R3 RAW 769  ADJ 92
canon 9dc1277   exit 1   R3 RAW 769  ADJ 91
canon c327bab   exit 1   R3 RAW 769  ADJ 91

                 adjudicated only          adjudicated + filter-removed
  eafada2        7 figures / 16 files      9 figures / 25 files
  9dc1277        7 figures / 16 files      9 figures / 25 files
  c327bab        7 figures / 16 files      9 figures / 25 files
```

**Detection is identical at every SHA. The two documents counted different
things on the same output.** `GATE_CLOSE`'s "9 of 9 across 24 of 24" is the
ADJUDICATED PLUS FILTER-REMOVED set; this document's 7 across 16 is the
ADJUDICATED set. The two figures adjudication drops are `$70,000` and `$99,920`
— the WAP income-eligibility limits, which are not rebate payouts.

So **`21` was the inflated score and `20` is the correct one**, and the honest
statement of the gate's recall on this row is: it DETECTS all nine figures and
ADJUDICATES seven, with two removed by the income-eligibility filter.

This is this repo's own already-named **raw-vs-adjudicated** defect class
(commit `b152b08`) recurring inside the gate's own scorekeeping, and it cost a
false regression claim in the first revision of this file. A score row must say
which set it counted.

The remaining shortfall against "24 of 24 files" is unchanged in cause and
still open: on that tree R3's `cost_context_markers` filter removes **119**
`$`-bearing rows, the same over-removal that makes row 5b PARTIAL, where "per
square foot" pardons a payout schedule that is *denominated* per square foot.
Narrowing that one filter closes 5b and 5c together. Out of this row's scope.

---

## WHAT THIS PASS CHANGED, FOR THE NEXT SESSION

1. **The SRC code/prose split is a NAMED, COUNTED, PER-RULE FILTER on R2, R3,
   R4, R5 and R7 — never a deletion.** A revision of this pass moved it into
   `ctx.pool()` as a bare `continue` and that BLINDED THREE BLOCKING RULES; the
   seventh adversarial read measured a wrong-utility claim going RAW 1 / ADJ 1 /
   exit 1 to RAW 0 / ADJ 0 / exit 0. The run now stays in the pool, each rule
   raises and then removes it under its own filter row, and the run's QUOTED
   STRING LITERALS are judged separately under a `#strN` locator because that is
   what the rendered page reads out of the same bytes. Controls R2f, R4h, R7c
   and R5-SRCLITERAL hold it, one per affected rule.
2. **`ctx.src_dup()` no longer slices to 48 characters.** Control R5-SRCPREFIX.
3. **`R5.derivable_constants` is wired** and bound four ways: the entry must
   name the PAGES it governs, a subject phrase must sit within 60 characters of
   that occurrence of the figure, EVERY numeral in the hit must be covered, and
   `derivation_note` must carry digits and an arithmetic operator. That last
   check is STRUCTURAL, not semantic: it cannot tell a right formula from a
   wrong one and does not claim to.
4. **`R5.publisher_short_forms`, `R5.subject_attribution_verbs` and
   `R5.publisher_artifact_nouns`** are config keys read only by `_pub_subject`.
   `"estimates"` is deliberately NOT in `R1.attribution_verbs` and must not be
   added: that list feeds a proximity test that cannot tell which noun owns the
   verb. A short form is matched ONLY in possessive form — an optional
   possessive group once made the bare token `Xcel` a publisher.
5. **`f_instat` takes its overlap over the WINDOW AROUND THE NUMERAL**, not over
   the whole sentence. The threshold is 4 and the window is 110 characters.
   Whole-sentence overlap counted words earned in a different clause and produced
   a measured silent miss.
6. **The interrogative guard was REMOVED.** It cleared 11 of 13 test
   interrogatives and 10 of those assert their figure. Do not reintroduce a
   list of idioms against a grammatical class.
7. **The replay harness is committed** at `ops/claim_gate/replay/`
   (`prepare.sh`, `replay.sh`, `score.py`), because a verification command that
   exists in no commit is not a verification command.
8. **Percent-sign confusables fold** (U+FF05, U+FE6A, U+066A), as do non-ASCII
   decimal digits and a combining mark on an ASCII base. U+2030 PER MILLE is
   deliberately not folded — different quantity, not a different spelling.

Control count went 32 -> 43 positive controls, each with a repair counterpart
(`CONTROLS: 43 positive DETECTED, 0 MISSED · 17 negative clean, 0 FALSE ALARM`,
`REPAIR TESTS: 43 repaired-clean, 0 FIRE ON REPAIRED, 0 NOT TESTED`).

## STILL OPEN, MEASURED, NOT CLOSED HERE

- **R3 `cost_context_markers` over-removal** — rows 5b and 5c. One filter.
- **`U-R2-combining`** (`Atmós Energy`, o + U+0301). The other seven Unicode
  misses the read listed are closed. This one needs the fold to run on the NFD
  form BEFORE NFC composes the mark away, which changes `dec()` for every
  accented ASCII base on every surface. The blast radius could not be measured
  inside this pass, so it is recorded rather than guessed at.
- **`U-R2-smallcaps`** (`AᴛMOS`, U+1D1B). Latin small-capital letters are not in
  `_FOLD` and NFKC does not map them.
- **DCI R5 stands at 6**, re-measured after the tightening. The pass does not
  claim zero.
