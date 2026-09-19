# Independent adjudication of DCI's R5 and R9 findings — 2026-09-18

Written by an independent reviewer row with no inherited context, against
DCI `ba2fc22` / canon `c660a1d`. Every classification below was reached and
written down BEFORE the other row's artifacts were opened; the comparison
section at the end was added afterwards. Nothing in any property repo was
changed by this pass: all mutation ran in `/tmp/r4pass/r3` mirrors.

Reviewer row: R3. Zero inherited context. /tmp/r4pass/r2 NOT read at time of writing.
Bench: /tmp/r4pass/r3/dci (rsync mirror of DCI @ ba2fc22), canon mirrors:
  canon      = c660a1d (HEAD, shipped)
  canon_pre  = c5ff426 tree (= c660a1d's parent), NEG16 moved aside
  canon_pre5 = 86b4ffd tree (= c5ff426's parent), NEG15/NEG16 moved aside
  canon_alt  = my alternative narrower R9 fix (slot-pattern qualified, no context guard)

## MEASURED BASELINE (run by me, DCI real repo, HEAD ba2fc22)
./ops/claim_gate.sh --report ... -> EXIT=1
  R5 UNCITED STATISTIC  RAW 532  ADJ 31  FAIL
  R9 INTERNAL CONTRADICTION RAW 1 ADJ 1 FAIL
  blocking failures: 2 (R5, R9); report-only: R3 120, R11 8
Scratch mirror reproduces byte-for-byte on the summary.
git status --porcelain in DCI after the run: 0 lines (gate wrote nothing).

## TASK 2 — GATE COMMIT AUDIT (measured)

### c660a1d — R9 whe_audit_precondition `context` guard
VERDICT: REPAIR of a genuine defect, but OVER-NARROW — a demonstrated silent miss,
and a strictly better fix existed and is measured below.

The underlying finding WAS false. I verified the flagged sentence myself:
  public/vermiculite-removal-cost-denver.html:1028
  "If you haven't confirmed what's in your attic yet, the <a href=...>identification
   guide</a> is the prerequisite step — this page picks up once testing is done or
   already scheduled."
  /usr/bin/grep -oIr 'is the prerequisite step' public/ | wc -l  ->  1
  That sentence says nothing about an audit, the WHE Bonus, or a rebate condition.
  Binding it to "an audit is a precondition of the WHE Bonus" is a false weld. AGREE it was FALSE.

SILENT MISS, PROVEN:
  Probe A (must fire): injected into scratch vermiculite page, replacing the above:
    "An energy audit is a prerequisite for the Whole Home Efficiency Bonus, and Xcel
     will not pay the bonus without one."
    -> canon (c660a1d):  R9 RAW 2 ADJ 2 FAIL   STILL FIRES. Guard does not blind the rule.
  Probe B (same proposition, ordinary synonyms):
    "An energy assessment is a prerequisite for the bonus, and Xcel will not pay it
     without one."
    -> canon (c660a1d):     R9 RAW 1 ADJ 1   MISSED
    -> canon_pre (c5ff426): R9 RAW 2 ADJ 2   CAUGHT
  So the guard, not anything else, causes the miss. The commit message's claim that
  "a sentence genuinely about the WHE audit precondition necessarily passes it" is
  FALSE AS STATED: "energy assessment ... prerequisite for the bonus" is genuinely
  about it and does not pass.

STRICTLY BETTER FIX EXISTED (canon_alt, measured): drop the `context` guard entirely
and qualify the one slot pattern that carries none of its own subject —
  required: "is the prerequisite step"  ->  "audit is the prerequisite step"
  -> real DCI copy:      R9 RAW 1 ADJ 1   (false positive dead, same as shipped)
  -> Probe B injected:   R9 RAW 2 ADJ 2   (still caught — shipped fix misses it)
That is the same cure with no loss of coverage.

### c5ff426 — R5 src_dup probe normalization
VERDICT: REPAIR in kind (the alphabet mismatch was real), but it ENLARGES a
pre-existing 48-character-prefix blind spot into a live silent miss.

The mechanism is genuine: rendered_index() is built from a.txt (tags stripped, dashes
folded); the probe was S.collapse(hit.sentence) off the raw generator byte string.
Normalizing the probe the same way is correct and is not an allowlist.

SILENT MISS, PROVEN. Injected into scratch _shared_components.py a generator string
that renders on NO page and carries a brand-new uncited magnitude:
  COLLIDE   '<p>Loose-fill cellulose settles 10 to 20 percent; rebate paperwork cuts
             your bill by 47% in the first year.</p>'
    -> canon (c660a1d):      R5 RAW 533 ADJ 31 — probe appears under the src_dup FILTER. MISSED.
    -> canon_pre5 (86b4ffd): R5 RAW 533 ADJ 38 — probe ADJUDICATED. CAUGHT.
  Same string without markup, prefix still colliding:
    -> canon: R5 RAW 533 ADJ 31, filtered. MISSED. (collision hole predates the fix)
  POSITIVE CONTROL, no prefix collision:
    'Zebra paperwork throughput for quokka invoicing cuts your bill by 47% in the first year.'
    -> canon: R5 RAW 533 ADJ 32, ADJUDICATED. Instrument fires; the zero above is real.
So: before c5ff426 a markup-bearing generator string was immune to the collision;
after it, it is not. The right completion is the same normalization compared on the
FULL normalized sentence, not a 48-char prefix.

### 86b4ffd — R4 URL masking + no cross-sentence program-name carry
VERDICT: REPAIR of two genuine defects. Both halves are load-bearing (proved below).
BUT it also creates a silent miss on ordinary pronominal anaphora.

FOUR CONTROLS, verified BY MY OWN METHOD (each fixture injected as a real page,
public/404.html, in the scratch DCI mirror, then the full gate run and R4's
enumeration read — NOT the gate's --canary self-report):
  1 predicate genuinely in prose        R4e firing    -> 1 ASSERTS row. FIRES.
      row: public/404.html:VIS ASSERTS same measure,stack | programs=Combo Bonus,
      Whole Home Efficiency Bonus (URL text masked before matching; the tokens above
      are from prose only) | "The Whole Home Efficiency Bonus and the Combo Bonus
      stack on the same measure..."
  2 same predicate only inside a URL    R4e repaired  -> 0 rows. DOES NOT FIRE.
  3 two programs in one sentence        R4f firing    -> 1 ASSERTS row. FIRES.
  4 second program in adjacent sentence R4f repaired  -> 0 rows. DOES NOT FIRE.

ATTACK — can a repaired fixture pass while the defect it names is still present?
NO. Ran the identical four against the PRE-fix gate (canon_pre4 = 03af70f):
  R4e repaired -> 2 rows, one of them
     "stack,stacking | ... and both sets of conditions sit at https://..."
     i.e. the token came from the URL alone. Post-fix: 0. Masking IS load-bearing.
  R4f repaired -> 1 row "(carried from the previous sentence: Combo Bonus)".
     Post-fix: 0. Carry removal IS load-bearing.
Both repaired halves therefore fail without the fix and pass with it. Not blindfolds.

SIDE OBSERVATION: on the PRE-fix gate both R4e halves also fired a SECOND row on the
fixture's own explanatory paragraph ("This is the FIRING half: ..."). A fixture's
commentary is a claim surface. Harmless today, a trap tomorrow.

SILENT MISS, PROVEN (probe injected as public/404.html in the scratch mirror):
  P1  "The Whole Home Efficiency Bonus and the Combo Bonus are both live in 2026.
       They stack on the same measure, so one job earns both."
        canon (86b4ffd+): 0 rows   MISSED
        canon_pre4:       1 ASSERTS row   CAUGHT
  P2 (positive control) both names repeated inside the predicate sentence
        canon: 1 row. canon_pre4: 1 row. Instrument fires; P1's zero is real.
  P3  "Both programs stack on the same measure"  -> canon: 1 ASSERTS-SET row.
        So program_set_anaphora covers the set-noun form; the residual hole is the
        BARE PRONOUN ("They", "It"), which is ordinary English and now invisible.

## TASK 1 — R5: 31 adjudicated rows, 20 distinct (file,sentence) claims
Method: for each row I read the flagged page, extracted every <p class="cited-stat">
block, and computed f_instat's own predicate (figure present in a block AND >=5 shared
content words, stoplist and [a-z]{3,} tokenizer copied from claim_gate.py).

FALSE — 22 rows. TRUE — 4 rows. AMBIGUOUS — 5 rows. DIRECTOR — 0.
R5 false-positive rate by my count: 22/31 = 71.0%.

[A] FALSE x17 — the figure IS attributed by a cited-stat on the same page that
covers exactly that figure and subject. Blocked only by f_instat's 5-shared-content-
word threshold (the comment at claim_gate.py:3083 records raising it from 3 to 5).
Measured overlaps below; threshold is 5.
  A1 blown-in-insulation-cost-denver.html LD+VIS (2 rows) "Loose-fill cellulose
     settles 10 to 20 percent, and reputable installers blow extra depth..."
     covering block: 'According to the Building America Solution Center, "loose-fill
     cellulose will settle from 10 to 20 percent over time due to gravity and
     vibration."'  overlap 4.
  A2 cellulose-vs-fiberglass LOWVIS+VIS (2) "Loose-fill cellulose settles 10 to 20
     percent; reputable installers blow extra depth..." same block, overlap 4.
  A3 cellulose-vs-fiberglass VIS (1) "Settling: loose-fill cellulose settles 10 to 20
     percent, which sounds alarming and mostly isn't." same block, overlap 4.
  A4 is-my-attic LD+VIS (2) "Blown-in cellulose loses 10 to 20 percent to settling
     over 25-30 years." same block, overlap 3.
  A5 hear-rebate-status LOWVIS+VIS (2) "Live in Denver in 2026: Xcel's insulation and
     air sealing rebate, the 25% Whole Home Efficiency Bonus, the Combo Bonus..."
     covering block: "According to Xcel Energy's 2025-2026 Colorado residential rebate
     summary, customers can receive ... a 25% bonus on all standard rebates when they
     install three or more measures within two years of enrolling."  overlap 4.
  A6 hear-rebate-status VIS (1) "...the standard rebate, the 25% WHE Bonus where the
     sequencing fits..."  same Xcel block, overlap 3.
  A7 insulation-blower-door-test LD+LOWVIS+VIS (3) "What happens if the after test
     does not reach a 20% CFM50 reduction?"  covering block: "According to Xcel
     Energy's residential rebate summary, the qualifying minimum standard for the air
     sealing rebate is a 20% reduction in CFM 50..."  overlap 4.
  A8 insulation-blower-door-test VIS (1) "...but reducing CFM50 by 20% is..."
     same Xcel CFM50 block, overlap 3.
  A9 insulation-blower-door-test VIS (1) "A blower door or infrared audit is also how
     many homeowners identify their third qualifying measure, which is where the extra
     25% on all standard rebates comes from."  Xcel 25% block, overlap 3.
  A10 whole-home-efficiency-bonus-stacking VIS (1) "...the trio unlocks the 25%
     bonus..."  Xcel 25% block, overlap 3.
  A11 upstairs-hot-summer-cold-winter VIS (1) "ENERGY STAR estimates these losses at
     roughly 20 to 30 percent."  covering block: 'According to ENERGY STAR's duct
     sealing guidance, "In a typical house, however, about 20 to 30 percent of the air
     that moves through the duct system is lost due to leaks, holes, and poorly
     connected ducts."'  overlap 3. DOUBLY false: publisher also named in-sentence.
  Rubric: A5-A10 are additionally a PROGRAM'S OWN PUBLISHED TERM (Xcel's 25% WHE bonus,
  Xcel's 20% CFM50 air-sealing condition), not a finding about the world.

[B] FALSE x2 — attributed IN THE SENTENCE; the gate cannot see it because
"estimates" is not in R1.attribution_verbs.
  B1 is-my-attic LD+VIS (2) "ENERGY STAR estimates a 15% heating-and-cooling cost
     reduction from adequate insulation plus air sealing."
     MEASURED: pubs in sentence = ['ENERGY STAR']; attribution verbs in sentence = [].
     /usr/bin/grep -n 'estimates' common.json returns 2 lines, both in OTHER rules'
     marker lists ("estimates to roughly", "estimates the project cost"); it is absent
     from R1.attribution_verbs. f_pub requires a verb before it will honour a named
     publisher, so the attribution is invisible.
     CAVEAT RECORDED, NOT WAVED: this page carries NO cited-stat for the 15% figure,
     while three sister pages (cellulose-vs-fiberglass, hear-rebate-status,
     insulation-blower-door-test, upstairs-hot) all carry the full ENERGY STAR Seal-and-
     Insulate block for it. That is an R11 attribution-debt item, not an R5 blocker.

[C] FALSE x2 — llms.txt; A PROGRAM'S OWN PUBLISHED TERM, not a finding about the world.
  C1 llms.txt:19 "- [Blower Door Testing](https://denvercoloradoinsulation.com/
     insulation-blower-door-test.html): How a blower door test measures air leakage as
     CFM50 ... and the before-and-after 20% CFM50 reduction Xcel's air sealing rebate
     requires."  Names Xcel in the same sentence as the owner of the condition.
  C2 llms.txt:83 "- [WHE Bonus Guide](...whole-home-efficiency-bonus-stacking-
     denver.html): The 25% bonus turns on one condition: three or more qualifying
     measures completed within two years of enrolling."
  MEASURED on llms.txt: 88 lines; 'Denver' 35 (positive control); 'According to' 0;
  'Xcel' 18. So llms.txt carries no cited-stat convention at all — page-scoped
  attribution is structurally unavailable there, for every figure, forever.

[D] FALSE x1 — the flagged string IS the citation.
  D1 src:_shared_components.py:SRC "in Climate Zone 5, estimated annual utility bill
     savings from home sealing and insulating are 16% for heating and cooling only,
     and 12% for the total house"
     It is the `stat=` value of a citation-registry dict at _shared_components.py:456
     whose adjacent keys are  source='ENERGY STAR'  and
     url='https://www.energystar.gov/saveathome/seal_insulate/methodology'.
     R5's SRC scan reads the string literal without the sibling keys of its own dict.
     ALSO measured: it renders on no page — '16% for heating and cooling only' 0
     occurrences in public/, '16%' 0 occurrences in public/, positive control
     'Climate Zone 5' 473 occurrences in public/.

[E] TRUE x4 — real uncited statistics, live, presented as findings about the world.
  E1 is-my-attic-insulation-failing.html LD+VIS (2 rows)
     "Air sealing typically delivers 10-15% bill reduction even on homes that already
     have adequate insulation."
     MEASURED: page has 3 "According to" blocks (IECC R-60; Building America cellulose
     settling; ENERGY STAR R60/R49 retrofit levels). NONE contains 15% or 10-15%
     (f_instat instat=False, 0 covering blocks). No publisher named in the sentence.
     Positive controls on that page: 'Denver' 41, 'According to' 3, '10-15%' 2.
  E2 vermiculite-insulation-denver.html LD+VIS (2 rows)
     "The Libby, Montana mine that supplied over 70% of the U.S. market closed in 1990,
     and its deposit was naturally contaminated with tremolite asbestos."
     MEASURED: page has 3 "According to" blocks (EPA assume-Libby/treat-as-asbestos;
     CEO HEAR closure; IECC R-60). None carries the 70% market-share figure
     (0 covering blocks). No publisher in the sentence. The adjacent "EPA guidance:
     assume contamination until accredited lab testing proves otherwise" attributes a
     DIFFERENT proposition. Positive controls: 'Denver' 38, 'According to' 3,
     '70%' 3, 'EPA' 8.
     NOTE: the figure occurs 3 times on the page; R5 caught 2. The body <p> "The mine
     operated from 1919 to 1990 and supplied an estimated over 70% of the U.S. market
     during that period." was NOT flagged — no magnitude_word substring in it. Same
     claim, more prominent placement, invisible to the rule.

[F] AMBIGUOUS x5 — r-value-altitude-denver.html, the 17% atmospheric-pressure figure.
  Rows: LOWVIS x2, VIS x3. Four sentence variants, all 17%.
  MEASURED: page has 4 cited-stat blocks (IECC R-60; ENERGY STAR R60/R49; CEO HEAR;
  Building America cellulose). NONE mentions atmospheric pressure (0 covering blocks).
  No publisher in any of the sentences.
  Reading 1 (TRUE): a quantified magnitude asserted as a fact about the world with no
  source on the page. A reader cannot check it. That is exactly what R5 asserts.
  Reading 2 (FALSE): it is a DERIVABLE PHYSICAL CONSTANT, not a statistic. ICAO
  standard atmosphere P/P0 = (1 - 2.25577e-5 h)^5.25588 at h = 1609.3 m gives 0.8234,
  i.e. 17.7% lower — I recomputed this independently and it agrees. There is no
  publisher to cite, only a formula.
  My position: under the rule AS WRITTEN this is a true positive, and the cure is one
  citation line (ICAO/NOAA standard atmosphere), not a copy decision. I do NOT accept
  the config note's characterisation of it as "a REVIEW, not a true positive".

## TASK 1 — R9: 1 adjudicated row
  public/r-value-needed-calculator.html:JS  N3  "tool payload field(s)
  ['lf-calc-inputs', 'lf-calc-output'] not found in the page; visible/hidden agreement
  cannot be established"  [N3-unverifiable]
VERDICT: FALSE. There is no contradiction; the rule is blocking on the gate's own
declared blind spot.
MECHANISM, measured:
  id="lf-calc-inputs" in public/r-value-needed-calculator.html : 0
  id="lf-calc-output" in public/r-value-needed-calculator.html : 0
  id="lf-calc-inputs" across ALL of public/                    : 0
  files REFERENCING the id in public/                          : 6
  positive controls on that page: 'Denver' 38, id="lf-source" 1, id="calcOutput" 1
The two fields are created AT RUNTIME by the form bootstrap:
  if (document.getElementById('calcTool')) {
    ['calc_inputs','calc_output'].forEach(function (n) {
      var h = document.createElement('input'); h.type='hidden'; h.name=n;
      h.id = 'lf-' + n.replace('_','-'); form.appendChild(h); }); }
and id="calcTool" IS present exactly once on each of the six calculator pages
(measured on all six). So the ids exist in the DOM and never in static markup.
The gate's own header states the hole: "no JS execution outside opt-in R6b".
R9's dci.json `tools.hidden` therefore names element ids that BY CONSTRUCTION can
never appear in a static scan, so N3 reports N3-unverifiable on every run, and that
unverifiable is ADJUDICATED and BLOCKS. DCI cannot go green while that config stands.
R5 false-positive rate 22/31 = 71.0%.  R9 false-positive rate 1/1 = 100%.

## TASK 4 — LGM and GCI (run by me, real repos)
  LGM /Users/vongimbel/code/longmontcoloradoinsulation.com HEAD 95c93d1
      ./ops/claim_gate.sh --brief -> EXIT 0, blocking failures: 0, CLAIM GATE: PASS
      R5 RAW 228 ADJ 0 PASS · R9 RAW 0 ADJ 0 PASS · R4 RAW 455 ADJ 0 PASS
      porcelain after the run: 0 lines
  GCI /Users/vongimbel/code/greeleycoloradoinsulation.com HEAD 34adbf4
      ./ops/claim_gate.sh --brief -> EXIT 0, blocking failures: 0, CLAIM GATE: PASS
      R5 RAW 203 ADJ 0 PASS · R9 RAW 0 ADJ 0 PASS · R3 ADJ 9 report-only
      porcelain after the run: 0 lines
  No regression from the three gate commits on either property.

## TASK 5 — NOTHING CHANGED
Repos at the SHAs the brief named, all clean:
  DCI ba2fc22, LGM 95c93d1, GCI 34adbf4, canon c660a1d; porcelain 0 lines each.
LIVE SITE, method: curl -sS --compressed -o <file> <url>, then cmp <file> <repo path>.
Command substitution was not used to capture any fetched body.
  https://denvercoloradoinsulation.com/is-my-attic-insulation-failing.html         200 IDENTICAL
  https://denvercoloradoinsulation.com/vermiculite-insulation-denver.html          200 IDENTICAL
  https://denvercoloradoinsulation.com/r-value-altitude-denver.html                200 IDENTICAL
  https://denvercoloradoinsulation.com/whole-home-efficiency-bonus-stacking-denver.html 200 IDENTICAL
  https://denvercoloradoinsulation.com/insulation-blower-door-test.html            200 IDENTICAL
  https://denvercoloradoinsulation.com/r-value-needed-calculator.html              200 IDENTICAL
  https://denvercoloradoinsulation.com/llms.txt                                    200 IDENTICAL
  https://denvercoloradoinsulation.com/                                            200 IDENTICAL
  https://longmontcoloradoinsulation.com/  and /llms.txt                           200 IDENTICAL x2
  https://greeleycoloradoinsulation.com/   and /llms.txt                           200 IDENTICAL x2
12 of 12 live artifacts byte-identical to the repo. Nothing was deployed.
All my mutation work ran in /tmp/r4pass/r3 mirrors; every mutated file was restored
and cmp'd byte-identical against the real repo before moving on.

## TASK 6 — ALL FOUR REPOS
  denvercoloradoinsulation.com   ba2fc22  porcelain 0  origin 0 0
  longmontcoloradoinsulation.com 95c93d1  porcelain 0  origin 0 0
  greeleycoloradoinsulation.com  34adbf4  porcelain 0  origin 0 0
  calibrated-design-canon        c660a1d  porcelain 0  origin 0 0

## COMPARISON WITH THE OTHER ROW
RETRIEVAL TRAIL. The brief said the other row's classifications "live in its report".
There is no such report on disk. What I searched and what came back:
  find /tmp/r4pass -maxdepth 3 -type f -name '*.md' / '*report*' / '*verdict*' /
       '*adjud*' / '*class*'
    -> no .md under /tmp/r4pass/r2 or /tmp/r4pass root at all.
       (/tmp/r4pass/r1/gate-*/ *.md are copies of canon's own docs, not a report.)
  /usr/bin/grep -rlI 'AMBIGUOUS' /tmp/r4pass/r2 /tmp/r4pass/*.txt  -> no files
  /usr/bin/grep -rlI 'DIRECTOR'  /tmp/r4pass/r2 /tmp/r4pass/*.txt  -> no files
  POSITIVE CONTROL /usr/bin/grep -rlI 'R5' /tmp/r4pass/r2 -> 15 files. The grep works.
  git log in canon: HEAD is c660a1d; no commit after it adds a findings document.
  find canon -name '*.md' -newermt '2026-09-18 12:00' -> docs/lanes.md,
    ops/claim_gate/ADVERSARIAL_READ_2026-09-18.md (last touched by 9d2daed, an
    EARLIER row), ops/claim_gate/GATE_CLOSE_2026-09-18.md (b1dd4ea, earlier row).
So the other row's only surviving written classifications are its three commit
messages. I compare against those.

STATE AGREEMENT. /tmp/r4pass/r2/dci_after2.txt matches my own run on the summary:
R5 RAW 532 ADJ 31 FAIL, R9 RAW 1 ADJ 1 FAIL, exit 1. Same corpus, same numbers,
same starting point. Their earlier runs show the trajectory I reproduced
independently: dci_run.txt R5 ADJ 37 / R9 ADJ 2, fixsim.txt R5 31 / R9 2.

DISAGREEMENT 1 — the SRC Climate Zone 5 stat.
  c5ff426: "SIX were prose that renders in public/ ... and exactly one was real
  (the ENERGY STAR Climate Zone 5 registry stat in _shared_components.py, which
  renders on no page)."
  I AGREE it renders on no page (measured: '16%' 0 occurrences in public/, positive
  control 'Climate Zone 5' 473). I DISAGREE that it is a real R5 finding. It is the
  `stat=` field of a citation-registry dict whose sibling keys, four lines apart, are
  source='ENERGY STAR' and url='https://www.energystar.gov/saveathome/seal_insulate/
  methodology'. It is a citation. Calling a citation an uncited statistic is a
  category error, and it is also DEAD (renders nowhere), so Rule 2 applies, not R5.
  I THINK I AM RIGHT: the evidence is four lines of the same dict literal.

DISAGREEMENT 2 — "a sentence genuinely about the WHE audit precondition necessarily
passes [the context guard]" (c660a1d, and the same sentence in config.context_note).
  DISPROVED BY MEASUREMENT. "An energy assessment is a prerequisite for the bonus"
  is genuinely about it and does not pass: R9 RAW 1 ADJ 1 on the shipped gate vs
  RAW 2 ADJ 2 on its parent. I THINK I AM RIGHT — I ran it both ways.

DISAGREEMENT 3 — the shape of the R9 fix.
  They chose a whole-sentence context guard. I measured a narrower fix (qualify the
  one slot pattern that carries none of its own subject) that kills the same false
  positive AND keeps the coverage theirs loses. I THINK I AM RIGHT, and this one is
  measured on both sides rather than argued.

DISAGREEMENT 4 — completeness.
  Their commits treat R5's remaining findings as out of scope ("R5 37 and R9 2 still
  stand and are not this change's scope", 86b4ffd). Nothing in the three commits
  classifies those 31. On my reading 22 of the 31 are FALSE, 17 of them for a single
  shared cause — f_instat's 5-shared-content-word threshold, raised in that same file
  to protect a live figure ("15% reduction in heating and cooling costs") that
  MEASURABLY NO LONGER EXISTS: /usr/bin/grep -oIr over public/ returns 0 occurrences
  of it, and the gate itself reports "0 are KNOWN-OPEN from config.known_uncited".
  The threshold is now costing 17 false positives to protect nothing.
  NOT A DISAGREEMENT WITH A STATED CLASSIFICATION — a gap where none was made.

NO DISAGREEMENT ON: that both original R4 findings were FALSE (I verified the
repair's four controls independently, plus the pre-fix behaviour); that the
vermiculite "is the prerequisite step" R9 instance was FALSE (I read the sentence);
that src_dup's alphabet mismatch was a genuine defect; that LGM and GCI stay at 0.
