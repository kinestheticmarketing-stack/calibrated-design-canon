# ADVERSARIAL READ — 2026-09-19

Independent adversarial review of the R5-close / source / wire pass, conducted
with zero inherited context. Every instrument built by this read. No file in any
repo was edited; all fixtures were built in `/tmp/r5pass/r4` and invoked with
`--config` / `--repo` / `CANON_ROOT=`.

State at review time (measured, `git rev-parse` + `git status --porcelain`):

| repo | HEAD | branch | dirty | ahead/behind origin |
|---|---|---|---|---|
| calibrated-design-canon | `c327bab` | main | 0 | 0/0 |
| denvercoloradoinsulation.com | `0d473a5` | main | 0 | 0/0 |
| longmontcoloradoinsulation.com | `95c93d1` | main | 0 | 0/0 |
| greeleycoloradoinsulation.com | `34adbf4` | main | 0 | 0/0 |

The brief named canon `38f177c` and DCI `74e8429`. Both advanced by one lane
*release* commit during this review (canon `c327bab` 18:18:59, DCI `0d473a5`
18:19:30, both by the pass's own author). DCI's `public/` tree hash is identical
across `74e8429..0d473a5` (`3936110639f81588aec41aa981615457beccb227` both
sides), so no content finding is affected.

---

## MOST SEVERE FINDING

**`1c7b354` silently blinded three BLOCKING rules on all three live properties,
and it is a regression created inside this pass.**

`889e172` added the SRC code/prose split as a **named, counted, R5-only filter**,
with a design note saying so: *"Marked, not dropped — the removal goes through a
named filter so it is counted and enumerated like every other one."* `1c7b354`
then moved it into `ctx.pool()` as a bare `continue` (`claim_gate.py:1216`),
which deletes the surface **before any hit is raised, for every rule that reads
SRC — R2, R3-T3, R4, R5, R7.** Identical fixture bytes, three commits:

```
                 base 9dc1277        889e172 (R5-only)   HEAD c327bab
SRC-R2-CSSWRAP   RAW 1 ADJ 1 exit 1  RAW 1 ADJ 1 exit 1  RAW 0 ADJ 0 exit 0  *** NEW EVASION ***
SRC-R4-CSSWRAP   RAW 1 ADJ 1 exit 1  RAW 1 ADJ 1 exit 1  RAW 0 ADJ 0 exit 0  *** NEW EVASION ***
SRC-R7-CSSWRAP   RAW 1 ADJ 1 exit 1  RAW 1 ADJ 1 exit 1  RAW 0 ADJ 0 exit 0  *** NEW EVASION ***
SRC-R3-CSSWRAP   RAW 1 ADJ 1 REPORT  RAW 1 ADJ 1 REPORT  RAW 0 ADJ 0 REPORT  *** NEW EVASION ***
controls SRC-R2/R4/R7/R3-PROSE: CAUGHT at all three commits
```

R2 is **wrong-utility claim** — the rule that exists because this portfolio
credited three towns to the wrong gas utility for two years. R4 is **stacking
assertion or denial**. R7 is **superseded-source claim**. All three are
blocking. A wrong-utility attribution written into a generator string that also
contains a stylesheet is now invisible to the gate built to stop it, and the
exclusion is reported only as an unattributed global byte tally:

```
SRC CODE SURFACES EXCLUDED FROM THE PROPOSITION POOL: 18 run(s), 82219 chars  (DCI)
                                                       9 run(s), 58265 chars  (GCI)
                                                       8 run(s), 49501 chars  (LGM)
```

**189,985 characters across three live properties, five rules, no per-rule
accounting.** The cheapest measured blindfold is **143 characters** of
well-formed CSS. Nothing is hidden there today — every live excluded run was
audited and the only prose hits are two JavaScript developer comments — so this
is a latent hole, not a live leak. It is first because it is a *blocking*-rule
regression the pass introduced and did not declare.

### Second: R5 reached zero on DCI by being loosened, not by the pages being fixed

Both runs below use **the same DCI content at HEAD**; only canon differs:

```
              R5 RAW   R5 ADJ   verdict   gate exit
DCI base      528      24       FAIL      1
DCI HEAD      523       0       PASS      0
```

All 24 map to the four filters this pass widened, with no remainder (11
`f_instat`, 5 publisher-as-subject, 5 `derivable_constants`, 3 question guard).
Restore the single integer `_R5_INSTAT_MIN` to 5 and the flagship property does
not pass:

```
  R5  UNCITED STATISTIC   RAW 523   ADJ 5   FAIL        exit=1
```

And the loosening was selected against DCI's own finding count rather than
against a defect corpus.

Sweeping `f_instat`'s threshold across {3,4,5,6,7} on scratch copies of canon,
with the token fold on and off, produces exactly one green cell:

| | threshold 4 | threshold 5 |
|---|---|---|
| **fold ON** | **DCI ADJ 0 — PASS** | DCI ADJ 5 — FAIL |
| **fold OFF** | DCI ADJ 4 — FAIL | control failure (gate exits 2) |

The R5-INSTAT control admits both 4 and 5 and does not discriminate between
them. The only thing selecting 4 over 5 is that 4 takes DCI to zero. The pass
shipped that cell.

The cost is **18 reproduced silent misses** in R5 — sentences that fired at the
pass's base commit `9dc1277` and clear at HEAD. Among them:

- `Our crews measured a 42% reduction in attic heat loss after air sealing.`
  clears solely because the threshold moved 5 → 4.
- `Our crews measured a 42% reduction in attic heater runtime loss.` clears
  because the suffix fold collapses `heater` → `heat`, multiplying the shared-
  word overlap ×4 and carrying it over the threshold.
- Ten interrogatives that **assert** their figure clear on the question guard,
  e.g. `Why settle for less when our crews measure a 36% reduction in heating
  costs?` and `How our crews cut heating costs by 39%?` (a declarative fragment
  ending in `?`). Measured: 11 of 13 test interrogatives cleared; 10 of those 11
  assert their figure.
- The probe the pass was **explicitly forbidden to clear** —
  `ENERGY STAR estimates vary, but our crews measure a 35% …` — clears once one
  comma is deleted: `ENERGY STAR estimates vary and our crews measure a 36% …`.
  `_R5_CLAUSE_BREAK` requires the comma for coordinators.
- The 47-character laundering distance the pass refused is now **unbounded**.
  A single 376-character run with no internal punctuation clears:
  `ENERGY STAR reports on … where our own crews measure a 61% reduction in
  heating costs after one afternoon of work.`

**Immediately behind it, a standing condition the pass's "wired under `set -e`"
assurance does not cover: the deploy path never runs the gate at all.**
`regen_all.sh` genuinely halts (injection-tested, all three properties, below) —
but deployment is `ops/push-to-staging.sh`, which never invokes
`ops/claim_gate.sh` or `regen_all.sh`. Its only preconditions are that `public/`
exists and holds ≥10 HTML files. `ops/push-to-staging.sh <domain>` followed by
`ssh root@… '/root/deploy.sh <domain>'` ships a `public/` no gate has ever seen.

---

## a. THE SIX GATE CHANGES: REPAIR OR ALLOWLIST

| change | commit | verdict |
|---|---|---|
| 1a threshold 5→4 + fold + question guard | `0fdd7a9` | **ALLOWLIST** |
| 1b publisher-as-subject | `84422d4` | **ALLOWLIST** |
| 1c wire `R5.derivable_constants` | `bf3fafe` | **ALLOWLIST** |
| 1d short-form publishers | `84422d4` | **ALLOWLIST** |
| 1e SRC code/prose split | `889e172` | **REPAIR**, with a new silent-miss channel |
| `src_dup` drop 48-char slice | `1c7b354` | **REPAIR**; the bundled pool move is allowlist-shaped |

### 1a — ALLOWLIST

The commit claims the threshold was "re-derived from a measured sweep." The
sweep measures only *live hits left uncleared* — a false-**positive** count. It
structurally cannot measure false **clears**, because no labelled corpus of true
uncited figures exists. The instrument can therefore only ever argue for
lowering. The documented false-clear pair sits at overlap 3, which establishes a
lower bound of 4 and no upper bound; the pass took the loosest admissible value.

**Fixture proving a silent miss (threshold alone),
`/tmp/r5pass/r4/a1/A2_thresh4.html`:**

```html
<p class="cited-stat">According to the <a href="https://www.epa.gov/report">EPA</a>, 42% of homes
built before 1980 have attic bypasses that turn winter heat into pure loss, something EPA field
crews still find on most inspections.</p>
<p>Our crews measured a 42% reduction in attic heat loss after air sealing.</p>
```

The EPA's 42% is about housing-stock age. The site's 42% is about heat-loss
reduction. Different claims, same numeral, zero attribution. Overlap
`['attic','crews','heat','loss']` = 4.

```
$ python3 drive.py A2_thresh4.html            # canon HEAD
RAW 2   ADJUDICATED 0
  FILTER CLEARED 1 by: the figure appears in a cited-stat rendered on this page
      -> 42% | Our crews measured a 42% reduction in attic heat loss after air sealing.

$ python3 drive_pre1a.py A2_thresh4.html      # canon 9dc1277
RAW 2   ADJUDICATED 1
  FIRES: 42% | Our crews measured a 42% reduction in attic heat loss after air sealing.
```

Confirmed end-to-end on the real gate against a scratch DCI clone: unmodified
DCI is `R5 RAW 523 ADJ 0`; with 46 injected candidates it is `RAW 569 ADJ 13` —
33 cleared.

**The fold is wrong in both directions.** It over-collapses
(`heater`→`heat`, `corner`→`corn`, `batter`→`batt`) and under-collapses the
pairs R5 actually keys on (`reduce`→`reduc` vs `reduction`→`reduction`;
`lose`/`loss`/`lost` are three of R5's own `magnitude_words` and split into
three stems). `better`→`bett` while `bettered`→`better` — the base form folds
harder than its inflection. Credit where due: the fold *is* load-bearing —
`fold OFF, T=5` breaks the R5-INSTAT control — so the morphology problem was
real; the implementation does not solve it and adds collisions.

### 1b — ALLOWLIST

The letter of the prohibition was honoured. `estimates` is genuinely **not** in
`R1.attribution_verbs`; `git show 84422d4 -- config/common.json` is one hunk
adding `publisher_short_forms` and `subject_attribution_verbs` only. Positive
control: `"According to" in R1.attribution_verbs -> True`,
`"estimates" -> False`.

The spirit was not. Beyond the comma defeat and the unbounded distance already
given, `_R5_NP` allows up to four words between a possessive publisher and the
verb, and those four words become the real subject. All of these satisfy
publisher-as-subject and clear:

```
ENERGY STAR's critics say our 43% savings number is invented.
ENERGY STAR's lawyers say our 58% savings claim is actionable.
We measured a 55% reduction in heating costs which ENERGY STAR's guidance never documents.
ENERGY STAR's website says nothing about our 42% reduction in heating costs.
ENERGY STAR reports no such 44% reduction in heating costs anywhere.
```

The last two are sentences that **explicitly deny** the attribution and are read
as carrying it.

**What 1b got right,** verified on the real gate and worth recording so a future
pass does not undo it: the named pair behaves as specified (`ENERGY STAR
estimates a 15% reduction in heating costs` clears; the comma'd
`…estimates vary, but our crews measure a 35%…` fires); appositives block S1
(`The EPA, whose guidance we follow, is why our 41% savings number holds.`
fires); `informed` is correctly absent from the verb list; payer-as-publisher
stays closed (`Xcel Energy pays the rebate and our crews record a 47%…` fires);
S2's 80-character window is enforced; and **nav, footer, anchor text and image
`alt` do not satisfy subjecthood** — a page carrying `<nav>…ENERGY STAR…</nav>`
and `<footer>…Guidance from ENERGY STAR and the EPA.</footer>` still fires on
`Our crews measure a 51% reduction…`.

### 1c — ALLOWLIST

**The 17% figure itself is sound.** Independent ICAO computation
(`p/p0 = (1 − 2.25577e−5·h)^5.25588`, h = 1609.344 m):

```
p/p0    = 0.823366  -> pressure 17.66% lower
rho/rho0 = 0.854387  -> density  14.56% lower
```

All three DCI instances bind the numeral to *atmospheric pressure* (the pressure
ratio), not density and not temperature, e.g. `public/r-value-altitude-denver.html:1020`:

> Atmospheric pressure at Denver's elevation is roughly 17% lower than at sea
> level, which slightly EASES the stack-effect differential rather than
> steepening it — thinner air outside means less pressure difference pushing air
> through a leak.

Scope matches. (17.66% rounds to 18%, so "roughly 17%" is a floor-round.)

**The wiring is an allowlist.** The matcher is
`has_any(h.sentence, subject_phrases, ci=True, word=False)` — an unanchored,
case-insensitive **substring** test with no binding between phrase and figure,
and the config entry carries **no page or file field**. Three falsifications of
the commit's own "narrow by construction, three ways":

```
--- cleared ---
 [R5.derivable_constants] 17%     | Atmospheric pressure has nothing to do with it: Denver homes
                                    we treat show a 17% lower heating bill in the first winter …
 [R5.derivable_constants] 17%     | Atmospheric pressure is irrelevant here, but our crews measured
                                    a 17% reduction in air leakage on every Denver job last year.
 [R5.derivable_constants] 17%,42% | Atmospheric pressure at Denver's elevation is roughly 17% lower
                                    than sea level, and the homes we insulate save 42% on gas every winter.
```

The first is canon's **own control fixture's** sentence
(`fixtures/R5f_derivable_constant.html`), which the control asserts must fire;
prepending six words clears it. The third clears a non-derivable 42% riding
along in the same hit. And it fires on `public/deriv.html`, not
`r-value-altitude-denver.html` — the entry is property-global.

Worst of all, `derivation_note` is checked for **non-emptiness, not validity**:

```
--- removed --- 63% | Our premium crews deliver a 63% reduction in winter heating cost, every time.
    derivation_note: "Because I said so. This field is free text and nothing validates it."
```

Any figure on the property can be permanently suppressed by writing one sentence
of prose beside it. In production today it over-clears nothing (all 5 live
removals are the atmospheric-pressure sentences) — the defect is latent.

### 1d — ALLOWLIST

The brief's premise was wrong and is recorded as such: the short form is **not**
first-token derivation. `common.json` adds a hardcoded two-element list
`["Xcel's", "Xcel’s"]`. No first-token collisions exist — every plausible
first-token English word (`Energy`, `National`, `Building`, `Department`,
`Colorado`, `International`, `Efficiency`, `Atmos`, `Boulder`) still fires in an
identical sentence frame, with a `Nobody at all reports…` negative control.

But `_pub_subject` strips the possessive (`re.sub(r"(?:'s|’s)$", "", name)`) and
`_r5_subject_pat`'s possessive group is **optional**, so:

- **The bare token `Xcel` becomes a publisher.** The config note shipped in the
  same commit says *"The bare token 'Xcel' is deliberately NOT here and must
  never be added."* `Xcel reports a 44% reduction in Front Range heating costs
  last winter.` clears.
- **Payer laundering is reopened** — the exact class 1b's sibling half exists to
  close:
  ```
  --- removed --- 38% | Xcel's air sealing rebate requires work that cut our
                        customers' bills 38% last year.
  ```
  That is unambiguously the site's own unsourced measurement of its own
  customers' bills, cleared behind a utility that never made the claim.

Isolated by calling `_pub_subject` with `shorts` and with `shorts=[]`: eight
clears are `NEW_BY_1D=True`, only one of which is the intended `llms.txt` target.

### 1e — REPAIR, with a new silent-miss channel

The predicate is per-string-run, not per-file, so a single `<style>` block does
**not** blind a whole file (verified: 3 of 4 runs excluded, the fourth fired):

```python
def _src_is_code(t):
    if not t or len(t) < 40: return False
    if _src_brace_density(t) < 0.40: return False
    return (len(_SRC_CSS_DECL.findall(t)) >= 5 or len(_SRC_JS_MARK.findall(t)) >= 3)
```

But a "run" is a maximal span of adjacent Python string tokens, which is exactly
how this portfolio writes page bodies. **Prose implicit-concatenated with a
stylesheet shares one run and is excluded with it** — which contradicts the
commit's stated blind spot ("this filter can only fail to exclude, never exclude
a page claim"). The stated blind spot is backwards.

Cheapest measured blindfold: **143 characters.**

```python
CAMO = (".a{color:red;}.b{margin:0;}.c{padding:0;}.d{border:none;}"
        ".e{display:block;} "
        "{ Our crews cut heating bills 71% on every Denver attic we touch. }")
```

Scored a repair regardless, because: the exclusion is announced and counted on
every run; the mitigation is real (string literals that ship into `public/` are
re-read there as CSS/JS surfaces — verified, all three claims fire on the
rendered page); and an audit of every live excluded run (DCI 18, GCI 9, LGM 8)
found **zero marketing prose hidden today** — the only hits are two JavaScript
developer comments in `DCI/_generate_calculator_pages.py:347`.

### `src_dup` — REPAIR; the bundled pool move is allowlist-shaped

The silent-miss claim is **true**, proved at both SHAs on one fixture:

```
########## CANON=889e172 (48-char prefix probe) ##########   EXIT=1
  RAW 4   FILTER src restatement 2 (removed 2)   ADJUDICATED 0    VERDICT PASS
########## CANON=1c7b354 (full sentence) ##########          EXIT=1
  RAW 4   FILTER src restatement 1 (removed 1)   ADJUDICATED 1    VERDICT FAIL
  --- 1 hits --- mag …,47% | <p>Loose-fill cellulose settles 10 to 20 percent …
                             cuts your bill by 47% in the first year.</p>
```

A byte-identical true restatement stayed cleared under both, so the repair did
not turn `src_dup` off. New false-positive class (the safe direction): generator
strings containing a format placeholder (`{town}`) now fire where the prefix
probe cleared them.

**The pool move is the problem.** It was measured for R5 only and then applied
to every proposition rule. A real R2 wrong-utility finding present at
`1c7b354^` is silently dropped at `1c7b354`:

```
##### 889e172 #####  R2 RAW 2  ADJ 2
  src:…SRC | <p>Atmos Energy is the natural gas utility for Denver homes and pays the rebate.</p>
  src:…SRC | els.forEach(function (el) { … el.innerHTML = 'Atmos Energy is the n
##### 1c7b354 #####  R2 RAW 1  ADJ 1
  src:…SRC | <p>Atmos Energy is the natural gas utility for Denver homes and pays the rebate.</p>
```

The 143-character camouflage above blinds R2 identically. **No live adjudicated
count fell on any property** — GCI and LGM both held exit 0 with every
adjudicated count unchanged (only RAW fell: GCI R2 359→338, R4 119→116,
R5 203→199; LGM R2 1012→996, R4 455→452, R5 228→226), matching the commit
message. The risk is prospective, demonstrated only on synthetic input.

---

## b. THE 86-VECTOR RE-RUN

### Enumeration — 86 of 86 recovered, from the harness, not from prose

`ADVERSARIAL_READ_2026-09-18.md` §(a) names its own harness and it survives on
disk: `/tmp/gate-close/r6/{harness.py, vectors.py, results.json}`.
`results.json` holds **97 rows = 86 vectors + 11 non-vector rows** (10 `*-CTRL`
plus `R6-CLEAN`, a negative control). Per-rule recovery matches the 09-18 doc's
table cell for cell:

| R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | total |
|---|---|---|---|---|---|---|---|---|---|---|
| 7 | 18 | 20 | 9 | 8 | 6 | 8 | 6 | 2 | 2 | **86** |

Cross-check against the 09-17 document's prose:
`/usr/bin/grep -oE '\bR[0-9]{1,2}[a-z]?-[A-Z]?[0-9]+\b' … | sort -u | wc -l` → **81**.
That is a regex artifact, not an inventory discrepancy: 81 − 6 IDs belonging to
other sections (`R3-T3`, `R6a-G1`, `R6a-G2`, `R6b-G3`, `R9-N1`, `R9-N2`) = 75,
plus 11 the regex cannot match because a letter follows the digit (`A1x`, `B4z`,
`B4c`, `B5q`, `C1b`, `C1c`, `C4b`, `D3b`, `D4b`, `G1b`, `G2b`) = **86**. The
harness was copied to scratch, `ROOT` repointed and `CANON` parameterised by
`CANON_ROOT` so identical fixture bytes could be driven through any commit.

### How many miss now — 14 of 86 mechanically, 12 measurable, against a prior 12

Sixteen `**MISS**` lines at `c327bab`, two of which are not vectors, giving 14:

| vector | result at HEAD | construction | vs prior |
|---|---|---|---|
| R1-A3 | `RAW 0 ADJ 0` | source named three sentences before the quotation | unchanged, declared |
| R2-B2 | `RAW 0 ADJ 0` | carries none of the 21 `attribution_words` | unchanged, declared |
| **R2-B8** | `RAW 0 ADJ 0` | `var u = 'At' + 'mos ' + 'Energy'` at runtime | **was CAUGHT** |
| R2-B15 | `RAW 1 ADJ 0` | unreferenced `og-image.svg` | unchanged |
| R3-C3 | `RAW 0 ADJ 0` | "fifteen hundred and fifty dollars" — no numeral | unchanged, declared |
| R3-C16 | `RAW 0 ADJ 0` | "pays the most" — not in `rank_words` | unchanged, declared |
| R3-C17 | `RAW 0 ADJ 0` | bare `1550`, no `money_words` in window | unchanged, declared |
| **R4-D1** | `RAW 1 ADJ 0` | anaphoric stacking across three sentences | **was CAUGHT** |
| R7-G6 | `RAW 0 ADJ 0` | `pre&#8209;requisite` folds to `pre-requisite` | unchanged |
| R8-H3 | `RAW 2 ADJ 0` | impossible date on `privacy.html` | unchanged |
| R8-H4 | `RAW 2 ADJ 0` | impossible date on `404.html` | unchanged |
| R10-J1 | `RAW 0 ADJ 0` | outside the 14 `promise_patterns` | unchanged, declared |
| R9-I1 | `RAW 0 ADJ 0` | paraphrased outside `value_slots` | **NOT MEASURABLE** |
| R9-I2 | `RAW 0 ADJ 0` | contradicting half in a backtick literal | **NOT MEASURABLE** |

**The R9 instrument is dead, and the prior read scored through it.** `R9-CTRL` —
the harness's own positive control, a plain contradiction — returns
`R9 RAW 0 ADJ 0 PASS`. Its `exit 1` comes from **R5**:

```
#### R9-CTRL RAW 0 ADJ 0 PASS exit 1
    R5  UNCITED STATISTIC      RAW 1  ADJ 1  FAIL
    R9  INTERNAL CONTRADICTION RAW 0  ADJ 0  PASS
    blocking failures: 1 (R5)
```

R9's `value_slots` point at real property pages a throwaway repo does not have,
so `R9-I1`/`R9-I2` cannot be scored either way. The 09-18 headline of 11 counts
`R9-I2` as caught on an `exit 1` that R5 produced — **wrong by construction, in
the direction that flatters.**

**Both regressions PREDATE this pass**, bisected across all seven SHAs:
`R2-B8` → `55c5ca8` (deliberate and correct; the 09-18 read itself refused to
credit B8's catch and printed "Honest count: 12 of 86"). `R4-D1` → `86b4ffd`,
and **that one is a real, undeclared detection loss** still open: the hit is
raised and then pardoned — `[NEUTRAL -- fewer than two distinct programs]
public/a.html:VIS NEUTRAL on top,on top of,stack | programs=- | They stack on
top of each other.`

### NEW evasions this pass opened — 20 proven pairs on 5 of the 6 commits

**The headline null result first, because it is not reassuring.** The 86-vector
result is **byte-identical at all seven SHAs** (`9dc1277`, `0fdd7a9`, `84422d4`,
`bf3fafe`, `889e172`, `1c7b354`, `c327bab`) — same 16 rows, same RAW/ADJ on
every one of the 86. Zero fixed, zero broken. The recorded folklore ("every
Unicode fix opened the next hole") did not repeat *among the 86*.

It did not repeat because **the 86 cannot reach any of this pass's changes.**
Every hole below is outside their span. Twenty hand-built probes, each run at
`9dc1277` and `c327bab` on identical fixture bytes.

**C1 — the question guard (`0fdd7a9`): 8 evasions.** `_is_plain_question` clears
any sentence ending `?` that opens with one of 24 interrogatives and contains
none of 13 hardcoded factive frames. Loaded questions are not a subset of that.

```
Q-WHY / Q-HOW / Q-HAVE-YOU-HEARD / Q-IS-IT-NOT-TRUE /
Q-WHO-ELSE / Q-WHEN / Q-SHOULD / Q-WHAT-IF
   base RAW 1 ADJ 1 exit 1  ->  HEAD RAW 1 ADJ 0 exit 0   *** NEW EVASION ***
control Q-FACTIVE ("Did you know…?")  CAUGHT at both
control Q-CTRL-plain                  CAUGHT at both
```

`Why does X?` and `How does X?` are this portfolio's own heading idiom and both
presuppose X. The guard's comment names its blind spot, but ships 13 *idioms*
against a grammatical *class*.

**C2 — `_R5_INSTAT_MIN` 5→4 (`0fdd7a9`): 1 evasion, and it is the one that
flipped DCI's release gate.** Isolated against a scratch canon identical to HEAD
except the integer: `CAUGHT`. Control `T2-CTRL2` (same numeral, overlap 0) still
fires, so `f_instat` is not a blanket.

**C3 — suffix folding (`0fdd7a9`): 1 evasion, independent of the threshold.**
Defect is *"once the attic is **sealed**"* against the citation's *"air
**sealing**"* — unfolded overlap 4, folded 5. At the `min5` scratch canon
(threshold reverted, folding intact) it **still misses**, so folding is the
cause. Reusing a citation's vocabulary in a different part of speech now buys
attribution.

**C4 — publisher short forms (`84422d4`): 2 evasions.**

```
P-XCEL-BARE  "Xcel reports a 42% reduction in heating costs for Denver homes."
P-XCEL-POSS  base RAW 1 ADJ 1 exit 1  ->  HEAD RAW 1 ADJ 0 exit 0
```

This is the exact false clear the code's own comment says it refuses: *"`Xcel`
alone is the PAYER on almost every page in this portfolio and widening the
proximity path with it would re-open the false clear the verb requirement was
added to close."* The verb requirement did not close it, because the possessive
group is optional in S1. `P-ENERGY-BARE` and `P-NATIONAL-BARE` are clean
(CAUGHT at both); `P-EPA-BARE` misses at both — pre-existing, via `f_pub`.

**C5 — `derivable_constants` (`bf3fafe`): 2 evasions.** Control
`D-CTRL-OTHERFIG` (42% instead of 17%) CAUGHT at both, so the *figure* binding
holds; the *subject* binding does not.

**C6 — the SRC split moved into the shared pool (`1c7b354`): 6 evasions across
FOUR rules. This is the most severe finding of the read.** `889e172` added
`_src_is_code` as a **named, counted, R5-only FILTER**. `1c7b354` moved it into
`ctx.pool()` as a bare `continue` (`claim_gate.py:1216`), removing the surface
**before any hit is raised, for every rule that reads SRC — R2, R3-T3, R4, R5,
R7**:

```
                 base 9dc1277        889e172 (R5-only)   HEAD c327bab
SRC-R2-CSSWRAP   RAW 1 ADJ 1 exit 1  RAW 1 ADJ 1 exit 1  RAW 0 ADJ 0 exit 0  *** NEW ***
SRC-R4-CSSWRAP   RAW 1 ADJ 1 exit 1  RAW 1 ADJ 1 exit 1  RAW 0 ADJ 0 exit 0  *** NEW ***
SRC-R7-CSSWRAP   RAW 1 ADJ 1 exit 1  RAW 1 ADJ 1 exit 1  RAW 0 ADJ 0 exit 0  *** NEW ***
SRC-R3-CSSWRAP   RAW 1 ADJ 1 REPORT  RAW 1 ADJ 1 REPORT  RAW 0 ADJ 0 REPORT  *** NEW ***
S-CSSWRAP  (R5)  RAW 1 ADJ 1 exit 1  —                   RAW 0 ADJ 0 exit 0  *** NEW ***
S-JSWRAP   (R5)  RAW 1 ADJ 1 exit 1  —                   RAW 0 ADJ 0 exit 0  *** NEW ***
controls SRC-R2/R4/R7/R3-PROSE and S-PROSE: CAUGHT at all three commits
```

**R2 (wrong utility), R4 (stacking) and R7 (superseded source) are all BLOCKING
rules.** A wrong-utility attribution or a stacking assertion written into a
generator string that also contains a stylesheet is now invisible to the gate
that exists to stop it. The bisect is exact: `889e172` catches, `1c7b354` misses.

And the removal is **not enumerated as a filter** — R5's block shows `RAW 0` and
no removal line. It appears only as a global byte tally naming no rule and no
hit:

```
SRC CODE SURFACES EXCLUDED FROM THE PROPOSITION POOL: 18 run(s), 82219 chars  (DCI)
                                                       9 run(s), 58265 chars  (GCI)
                                                       8 run(s), 49501 chars  (LGM)
```

**189,985 characters** of generator string content dropped from the proposition
pool of five rules across three live properties, with no per-rule accounting.
`889e172`'s design note — *"Marked, not dropped — the removal goes through a
named filter so it is counted and enumerated like every other one"* — was true
at `889e172` and is **false at `c327bab`**.

**C7 — `38f177c`:** no probe found a hole. Config date only.

### The live consequence: DCI's "R5 to zero" is entirely filter-widening

Both runs use **the same DCI content at HEAD**; only canon differs:

```
              R5 RAW   R5 ADJ   verdict   gate exit
DCI base      528      24       FAIL      1
DCI HEAD      523       0       PASS      0
```

Each of the 24 base findings was mapped to the filter that removes it at HEAD.
**All 24, no remainder:**

```
 11  the figure appears in a cited-stat rendered on this page  (f_instat 5->4 + folding)
  5  recognised_publishers named in the same sentence          (publisher-as-subject + short forms)
  5  R5.derivable_constants                                    (f_deriv)
  3  the sentence is a QUESTION                                (f_question)
```

So the copy rewrites did not take R5 to zero. **After every copy fix in this
pass, the pre-pass gate still finds 24 R5 findings on today's DCI content**; the
four widened filters clear all of them. Most are defensible on inspection (the
atmospheric-pressure rows, the `What happens if…?` rows, the cellulose-settling
restatements). **But restore the single integer `_R5_INSTAT_MIN` to 5 and DCI
does not pass:**

```
$ python3 canon-min5/ops/claim_gate/claim_gate.py --config …/dci.json --repo …/denvercoloradoinsulation.com
  R5  UNCITED STATISTIC   RAW 523   ADJ 5   FAIL        exit=1
```

The five that `5→4` pardoned, live today:

```
hear-rebate-status-colorado.html:LOWVIS  25% | …Xcel's insulation and air sealing rebate, the 25% Whole Home Efficiency Bonus…
hear-rebate-status-colorado.html:VIS     25% | (same)
insulation-blower-door-test.html:VIS     25% | …which is where the extra 25% on all standard rebates comes from.
is-my-attic-insulation-failing.html:LD   10 to 20 percent | Blown-in cellulose loses 10 to 20 percent to settling over 25-30 years.
is-my-attic-insulation-failing.html:VIS  (same)
```

None of those three 25% sentences names a publisher; their whole attribution is
four shared tokens with a different sentence that happens to carry 25%.
**The flagship property's release gate flipped from exit 1 to exit 0 on one
integer.**

Note also that `0fdd7a9`'s own sweep table predicts `DCI +fold` leaves **3**
uncleared at threshold 4; the shipped run leaves **0**. The table and the engine
disagree. Which is wrong is NOT DETERMINED.

### The Unicode-confusable family, in full — 8 misses, 0 opened, 0 closed

43 fixtures, each byte-verified for the codepoint it claims via
`unicodedata.name`, run at `9dc1277` and `c327bab`.

**CAUGHT at both:** Cyrillic А U+0410, Cyrillic о U+043E, Greek Α U+0391, Greek
ο U+03BF, fullwidth letters U+FF21…, NBSP U+00A0, narrow NBSP U+202F, hair space
U+200A, figure space U+2007, soft hyphen U+00AD, ZWSP U+200B, ZWJ U+200D, ZWNJ
U+200C, word joiner U+2060, BOM U+FEFF, RTL override U+202E, LRM U+200E, math
bold 𝐀𝐭𝐦𝐨𝐬, math sans 𝖠𝗍𝗆𝗈𝗌 *(R2)*; fullwidth digits ３５, math bold digits 𝟑𝟓,
monospace digits 𝟹𝟻, superscript ³⁵, circled ③⑤, NBSP/narrow-NBSP before `%`,
ZWSP/ZWJ/soft-hyphen inside the digits, RTL override *(R5)*. Fullwidth `＄`
U+FF04 is `R3-C2`, caught.

**MISSES — all eight pre-existing, identical RAW/ADJ at base and HEAD:**

| # | vector | codepoint | construction |
|---|---|---|---|
| 1 | `U-R2-combining` | U+0301 | `Atmós Energy` — o + COMBINING ACUTE |
| 2 | `U-R2-smallcaps` | U+1D1B | `AᴛMOS Energy` — SMALL CAPITAL T |
| 3 | `U-R5-fw-pct` | U+FF05 | `35％` — ASCII digits, FULLWIDTH PERCENT |
| 4 | `U-R5-fw-both` | U+FF13/15/05 | `３５％` |
| 5 | `U-R5-small-pct` | U+FE6A | `35﹪` — SMALL PERCENT SIGN |
| 6 | `U-R5-arabic-pct` | U+066A | `35٪` — ARABIC PERCENT SIGN |
| 7 | `U-R5-combining` | U+0301 | `35́%` — combining acute between digit and `%` |
| 8 | `U-R5-devanagari` | U+0969/096B | `३५%` — DEVANAGARI DIGITS |

**The shape of the hole: the gate folds fullwidth DIGITS but not the fullwidth
PERCENT SIGN.** `３５%` is caught; `35％` is not; `３５％` is not. `dec()`
normalises no percent-sign variant at all — U+FF05, U+FE6A and U+066A are three
unguarded doors into every percentage rule. Combining marks defeat both R2 and
R5, the one family that reaches across rules.

Two probes in the suite were **not distinct** and are not counted:
`U-R2-cyr-a` (no lowercase `a` in "Atmos Energy" — byte-identical to its control)
and `U-R5-fullwidth-in-word` (a dead `if False` branch). Both NOT TESTED.

### NOT TESTED / NOT REPRODUCIBLE in this section

- `R9-I1`, `R9-I2` — unscorable in both directions; the harness's own R9 control
  does not fire.
- Folding-off at threshold 5 — the mutation makes control `R5-INSTAT` fire on
  repaired and the gate self-aborts at exit 2. (This independently corroborates
  `0fdd7a9`'s claim that the fold is load-bearing for that control.)
- `0fdd7a9`'s measured near-miss sweep was not reconstructed.
- LGM/GCI R5 removed-sets — both are ADJ 0 at base and HEAD, so the four widened
  filters are latent there; whether they pardon anything was not tested.
- `--peer`, `--opt-in=R6b`, and the R6/R11 control phases.

**Weakly grounded, flagged not asserted:** on synthetic repos the gate prints
`TRAP: KNOWN-PRESENT CONTROL FAILED: 'Denver' occurs 0 times` and still reports
`CONTROLS: 40 positive DETECTED, 0 MISSED` and `CLAIM GATE: PASS` at exit 0. A
failed known-present trap is neither counted in the CONTROLS line nor escalated
to exit 2. On a throwaway repo the trap is correctly reporting the repo's
contents, so this may be by design; the intent was not traced.

---

## c. INDEPENDENT SOURCE VERIFICATION OF THE REWRITTEN CLAIMS

**All claims verified SUPPORTED AS WRITTEN. This section includes one finding I
raised and then retracted on evidence.**

### c1. DOE air-sealing figure — SUPPORTED, verbatim

Retrieved `https://www.energy.gov/sites/default/files/2022-08/energy-saver-guide-2022.pdf`
— HTTP **200** under both a default UA and a browser UA, 3,251,105 bytes,
`application/pdf`. PDF page 10 = printed page 6, section *Weatherize Your Home →
Air Sealing*. Verbatim:

> By sealing uncontrolled air leaks, you can save 10%–20% on your heating and
> cooling bills.

The page (`public/is-my-attic-insulation-failing.html`, both surfaces) reads:

> The Department of Energy states that by sealing uncontrolled air leaks you can
> save 10-20% on your heating and cooling bills.

Intervention (air sealing alone), scope (heating and cooling bills) and
publisher (DOE) all match. The prior claim's four unsupported elements — the
10-15% band, "air sealing alone", total-bill scope, and "even on homes that
already have adequate insulation" — are all genuinely gone from `public/`.

**Tooling note recorded because it nearly produced a false finding:** my first
`grep` for the exact phrase against `pdftotext -layout` output returned **zero**.
That was a false absence caused by two-column interleaving splitting the phrase
across lines. Only `pdftotext -raw` on the isolated page recovered it.

Minor: the commit message calls the rewrite DOE "verbatim"; the shipped text
renders `10%–20%` as `10-20%` and drops the comma. Semantically identical, not
verbatim as claimed.

Corroborating the pass's own note: `https://www.energy.gov/energysaver/air-sealing-your-home`
is genuinely **404** under a browser UA while `https://www.energy.gov/` returns
**200** with the same UA — a real 404, not a block.

### c2. Libby vermiculite figure — SUPPORTED, verbatim, correct figure of three

Retrieved `https://www.epa.gov/asbestos/protect-your-family-asbestos-contaminated-vermiculite-insulation`
— HTTP **200**, 61,713 bytes. EPA states it twice:

> A mine near Libby, Montana, was the source of over 70 percent of all
> vermiculite sold in the United States from 1919 to 1990. There was also a
> deposit of asbestos at that mine, so the vermiculite from Libby was
> contaminated with asbestos.

> Since the Libby mine was estimated to be the source of over 70 percent of all
> vermiculite sold in the United States from 1919 to 1990 …

`public/vermiculite-insulation-denver.html` (JSON-LD line 63 and visible line
1158) is a near-verbatim quotation of the first. The page uses **EPA's over-70%
of US sales** figure with EPA's own scope. It does **not** conflate it with
EPA's 80%-of-world-supply figure or USGS's more-than-50%-of-world-output figure:
`80 percent of the world`, `80% of the world`, `world supply`, `world output` all
measure **0** across all three properties' `public/` and generator sources. The
only `80%` on that page (2 occurrences) are CSS gradient stops, read in context.

### c3. Xcel program terms — SUPPORTED, verbatim, against the current edition

This is the claim I attacked hardest, and the pass survives it.

The page attributes to *"Xcel Energy's 2025–2026 Colorado residential rebate
summary."* The linked URL
`https://co.my.xcelenergy.com/s/residential/home-rebates/insulation-air-sealing`
is a Salesforce SPA: HTTP 200 but the initial payload contains **zero** of the
claim terms (control: `Xcel` hits 4×, in `<title>` and CSP). Rendered with
headless Chrome (`--headless=new --virtual-time-budget=25000 --dump-dom`,
2,635 chars of text) it still contains no `CFM`, no `25%` bonus, no "three or
more measures", no "two years". Its only `20%` is *"You could be wasting up to
20% of the energy used to heat and cool your home"* — a different proposition.
Two accordions (*Eligibility Requirements*, *Additional Information*) did not
expand under `--dump-dom`; I state that as a limit on this probe.

**I initially concluded the "2025–2026" edition did not exist and was wrong.**
Filename-pattern probes for `25-…`/`26-…` 404'd and two domain-restricted
searches surfaced only 2020, 2021/22, Early-2023, 2023 and 2024 Colorado
editions. The generator's own comment names print code `25-12-215`, so I probed
that specifically and then found the document. It is real:

> **COLORADO 2025-2026 REBATE SUMMARY**
> COLORADO RESIDENTIAL ENERGY EFFICIENCY PROGRAMS
> EFFECTIVE NOV. 16, 2025

(retrieved as a mirrored PDF, HTTP 200, 2 pages, print code `25-10-417` in the
footer — same title, same effective date; the repo's `docs/citation-registry.json`
records `25-12-215`, presumably a reprint code. The edition is not in doubt; the
print code differs from the registry's by one field and is worth reconciling.)

Against that document, verbatim:

> **AIR SEALING AND INSULATION | MINIMUM QUALIFYING STANDARDS**
> Air Sealing | **20% reduction in CFM 50** | 30% of the project cost, capped at $400
> Attic Insulation | Pre-job R-value of less than 24, with a post-job R-value of 60 or greater

> Customers can receive larger attic insulation and washer and dryer rebates, as
> well as a **25% bonus on all standard rebates when they install three** or more
> measures within two years of enrolling.

The site's sentences — *"the qualifying minimum standard for the air sealing
rebate is a 20% reduction in CFM 50"* and *"a 25% bonus on all standard rebates
when they install three or more measures within two years of enrolling"* — are
both **verbatim from this table**. Supported.

*"The insulation rebates are qualified by post-job R-value, not by leakage
reduction"* is also supported by the summary's table, whose insulation rows carry
only R-value criteria.

**One residual tension worth a Director's eye, not a citation defect.** Xcel's
own DSM regulatory filing, *Insulation and Air Sealing Rebate — Product Write-up*
(`xcelenergy.com/staticfiles/…/Insulation & Air Sealing - Product Write-up.pdf`,
HTTP 200), states:

> If air sealing is required, a minimum of a 20% reduction in air leakage must be
> achieved **to qualify for insulation rebates**

> a post-improvement blower door test must be done and show a minimum
> improvement of 20% air leakage reduction, **before insulation improvements can
> qualify for the rebate.**

So the leakage threshold does gate the insulation rebate (unless the home is
already ≤0.50 NACH). The site reports what the *rebate summary* says, which is
what it cites, and is therefore not misquoting — but a homeowner reading "not by
leakage reduction" would be surprised by the filing. **LGM already states this
correctly** and DCI does not:

> unless a first blower door test already finds the home tight enough by Xcel
> Energy's own measure, a documented 20% reduction in CFM50

Neither property states a specific R-value threshold for the Xcel qualifying
standard (`post-job R-value of 49`, `R-49 or greater`, `R-value of less than 15`
all measure 0 in `public/` on all three), so nothing is an edition stale.

### c4. ENERGY STAR 15%/11% — SUPPORTED. **A finding I raised and retracted.**

I measured a misquotation across **53 live pages** (DCI 32, LGM 9, GCI 12),
rendered inside typographic quotation marks. ENERGY STAR's *methodology* page
says *"attics, floors over crawl spaces, **and accessible basement rim joists**"*
where the sites say *"and basements."*

**Retracted.** The URL the sites actually cite —
`https://www.energystar.gov/saveathome/seal_insulate/why-seal-and-insulate`,
HTTP 200 — reads verbatim:

> EPA estimates that homeowners can save an average of 15% on heating and
> cooling costs (or an average of 11% on total energy costs) by air sealing
> their homes and adding insulation in attics, floors over crawl spaces and
> basements.

Exactly as quoted, including "and basements". ENERGY STAR publishes two
different scopes on two pages; the sites quote the one they link, correctly. This
is recorded rather than deleted because it is the precise trap the discipline
warns about — I compared against the wrong page of the right publisher.

Worth knowing, not a defect: ENERGY STAR's Table 1 gives **Climate Zone 5**
(Denver) as *Heating and cooling only **16%***, while the sites use the 15%
national average. Correctly labelled as EPA's estimate either way.

### c5. GCI's Atmos figure — SUPPORTED (checked because a defect class is portfolio-wide)

GCI attributes the same 20% CFM50 term to a **different utility**. Retrieved
`https://www.atmosenergy.com/ways-save/colorado-residential-smartchoice-energy-efficiency-rebates/`,
HTTP 200. Atmos's own table:

> Air Sealing | **Minimum 20% CFM(50) Reduction Requires Blower Door Test** | $575

GCI's sentence — *"Atmos Energy's residential air-sealing rebate pays a flat
amount against a blower-door test documenting at least a 20% reduction in
CFM(50) leakage"* — is correct, including the `(50)` notation, and correctly
withholds the `$575`.

### c6. The defect class was genuinely swept

The old DOE and vermiculite claim forms measure **0** in `public/` on all three
properties. The only survivors anywhere on DCI are 3 lines inside a `#` comment
block in `_educational_pages.py` (the tombstone) — confirmed by Python
`tokenize`: count inside `STRING` tokens = 0 for all four probes, `compile()`
OK. They cannot be emitted. LGM and GCI never carried either claim.

### c7. THE GAP THIS SECTION EXPOSES

**R5 = 0 on DCI does not mean "no uncited statistics."** R5 requires both a
`magnitude_pattern` and a `magnitude_word` from
`['reduction','savings','saves','save','lower','cut','increase','improvement',
'payback','efficiency','loss','leakage','reduce','lose','lost','performance']`.
A federal statistic about market share carries none of them.

Proof, and the live defect it hides — `public/vermiculite-removal-cost-denver.html`,
a page the pass never touched, carries on **both** surfaces (visible line 1166
and JSON-LD block #1 line 63):

> A single mine near Libby, Montana supplied over 70 percent of the vermiculite
> sold in the U.S. from 1919 to 1990, and that deposit was naturally
> contaminated with asbestos.

No EPA attribution at all, and "the vermiculite" drops EPA's "**all** vermiculite".
This is the exact defect class `e158319` says it closed. The gate cannot see it:

```
$ /usr/bin/grep -ocI '70 percent' /tmp/r5pass/r4/dci_full.txt      -> 0
$ /usr/bin/grep -ocI 'mag ' /tmp/r5pass/r4/dci_full.txt            -> 523   (control: it enumerates)
$ /usr/bin/grep -ocI 'vermiculite-removal-cost' dci_full.txt       -> 10    (control: page in scope)
$ /usr/bin/grep -ocI 'Libby' dci_full.txt                          -> 8     (control: topic in scope)
$ magnitude_words present in that sentence                         -> []    count 0
```

The page and the topic are both in the report; the sentence is **never generated
as a candidate**. It is not filtered — it is invisible. 73 of the 523 R5
candidates do use spelled-out `percent`, so this is the magnitude-word gate, not
a regex gap.

Canon already recorded the companion limitation itself, in commit `55c5ca8`:
*"R2 sub-test `t` is a REVIEW class: it cannot tell a correct attribution from a
wrong one."* No rule in the gate checks quotation fidelity against a source.

---

## d. BOTH-SURFACES CONFIRMATION PER REWRITTEN CLAIM

Instrument: `python3` + `html.parser` + `json`. **490 JSON-LD blocks across 75
DCI pages parsed, 0 parse failures**, 10,265 string values extracted (controls
over extracted strings: insulation 3368, rebate 530, Xcel 768).

| claim | visible | JSON-LD | verdict |
|---|---|---|---|
| DOE air sealing (`is-my-attic-insulation-failing`) | new | new (`$.mainEntity[2].acceptedAnswer.text`) | **CONFIRMED** |
| Libby vermiculite (`vermiculite-insulation-denver`) | new | new (`$.mainEntity[0].acceptedAnswer.text`) | **CONFIRMED** |
| Xcel terms (`resources.html`, `llms.txt`) | new | new (`$.mainEntity.itemListElement[18].description`) | **CONFIRMED** |
| Xcel terms (`hear-rebate-status`, `insulation-blower-door-test`) | new | no JSON-LD twin exists (verified by parsing) | **CONFIRMED** |

**DEFECT d1 — a fourth vermiculite page was never swept, and is wrong on both
surfaces.** `public/vermiculite-removal-cost-denver.html`, quoted in c7 above.
`/usr/bin/grep -roI 'supplied over 70' public/` → **2**, both in that file, one
visible and one inside JSON-LD. `e158319`'s message claims the class was swept
and names only two extra pages.

**DEFECT d2 (lesser) — one-surface move.**
`insulation-vermiculite-abatement.html` body was corrected to the EPA scope, but
its JSON-LD block #2 still reads *"The Libby, Montana mine that supplied most of
the U.S. vermiculite **market**"* — retaining the "market" scoping the commit
condemned. Hedged to "most", so scope drift rather than a false percentage.

**Thirteen runtime-assembled percentages — CONFIRMED, exactly 13.** Enumerated
from `a636c78^`: attic `[18,28][12,22][8,15][4,9][2,5]` (5) + wall `[4,12]` +
crawl `[4,10]` + spray `[15,28][8,18]` (2) + airseal `[8,15][4,10]` (2) + whole
`[20,35]` + default `[5,12]` = 13. Gone from generator, `public/`, and JSON-LD.
`git grep -l savingsRange HEAD -- public/` → no match; control
`git grep -l pb-calc HEAD -- public/` → the page still exists.

**JavaScript syntax error — CONFIRMED, with a negative control.** Every inline
`<script>` (non-`ld+json`, no `src`) extracted from all 75 pages and run through
`node --check`:

```
AT HEAD (0d473a5):     75 files, 82 inline scripts, node --check FAILURES: 0
AT ee1e3a5 (pre-fix):  75 files, 82 inline scripts, node --check FAILURES: 1
  FAIL do-i-need-new-insulation-quiz.html script#1
       # RULING 2, 2026-09-18: numeral removed, qualitative claim kept. Same
       ^  SyntaxError: Invalid or unexpected token
```

A Python comment had been emitted into a JS block. The harness demonstrably
detects the bug it certifies absent.

---

## e. REBATE FIGURES AND GCI'S WEATHERIZATION LIMITS

**The standing exception is INTACT at exactly 10 and 10.**

```
$ cd GCI && /usr/bin/grep -rnoI '\$70,000' public/ | wc -l   ->  10
$ cd GCI && /usr/bin/grep -rnoI '\$99,920' public/ | wc -l   ->  10
positive control, same corpus: 'Greeley' -> 3039
```

All 10 read in full sentence; every one is a WAP income-eligibility threshold,
e.g. *"on the Colorado Energy Office's WAP income eligibility chart, Weld County
currently reaches $70,000 for a single-person household and $99,920 for a
household of four, checked September 10, 2026."* Zero are rebate amounts.
(Repo-wide including `docs/` the counts are 37/36; the "exactly 10" figure is a
`public/` measurement and `public/` still reads 10/10.)

**No rebate dollar figure anywhere — CONFIRMED.**

| | `public/` raw `$` | distinct | llms.txt | generator `*.py` raw |
|---|---|---|---|---|
| DCI | **0** | — | 0 | 44 (all `#` comments / docstrings) |
| LGM | 8 | `$1.50 $3.00 $3.50 $300 $1,200` | 0 | 52 |
| GCI | 20 | `$70,000 $99,920` (the exception) | 0 | 32 |

Method correction worth recording: the obvious pattern `\$[0-9][0-9,]*`
**silently truncates decimals** (`$1.50` matches as `$1`) and hid LGM's real
figures. Re-swept with `\$[0-9][0-9,]*(\.[0-9]+)?`. Encoding evasion excluded:
`&#36;`, `&dollar;`, `$` all 0 on all three. DCI's zero is real — controls
on the same directory: Denver 3157, insulation 14242, rebate 2995, 85 files.
Runtime JS assembly swept: the two `'$' + …toLocaleString()` formatters format
the visitor's own typed input, not a rebate payout. Spelled-out amounts are all
qualitative ("a few hundred dollars"). GCI's Atmos caps (`$1,550`, `$575`,
`$1,075`) measure **0**.

**DEFECT e1 — LGM ships retired cost figures inside a JS comment on a live
page.** `public/attic-insulation-cost-calculator-longmont.html:1397–1400`, from a
raw JS string (not a Python comment): *"rate this tool used to hard-code
($1.50-$3.00 base, $1.50-$3.50 removal add-on, $300-$1,200 air-sealing add-on)…"*
Cost-of-work, not a rebate payout, so not a literal violation — but GCI already
identified and fixed exactly this class, and says so in its own live guard at
`public/insulation-cost-calculator-greeley.html:1408`: *"because THIS IS A JS
COMMENT it shipped inside a `<script>` block on a live page."* **A defect class
was fixed page-scoped instead of portfolio-wide.**

**Adjudication note, ruled rather than escalated.** Percentage-of-cost rebate
phrasings exist in volume (GCI `75% of` ×97, DCI `25% bonus` ×141, LGM
`50%/100% of project cost` ×5). The standing ruling as stated bans a **dollar**
figure; GCI's own `COPY_VOICE.md` HARD RULE 3 bans amounts/caps/percentages only
for Xcel as "what any homeowner on this site gets", and
`_generate_area_pages.py:78` makes the retention deliberate. **Ruling: no
violation** — and independently, every one of these percentages is accurate to
its publisher (Xcel's 25% and Atmos's 75% both verified verbatim in section c).
The dollar caps genuinely are gone.

---

## f. GCI TERRITORY AND LGM RESTRICTION COPY

**Both recorded tooling traps reproduced before any count was trusted.**

```
polluted  /usr/bin/grep -rhoiI 'ault' public/ | wc -l   -> 334
clean     /usr/bin/grep -rhowI 'Ault' public/ | wc -l   -> 159
filter removed: preventDefault x76, default x6, fault x4, vaulted x3

LaSalle -> 159      La Salle -> 0   (a TRUE absence; the 159 is the control)
```

### GCI territory — CONFIRMED on every surface

Positive controls: `Atmos` 595, `Xcel` 250 in `public/`. Sentence-level
co-occurrence with a gas-utility name, tags stripped and entities decoded,
JSON-LD included: **Johnstown 77, Milliken 78, Severance 77** — all read, all
correct-split statements or explicit negations.

| item | measured | verdict |
|---|---|---|
| No Atmos attribution on the three Xcel-gas towns | 232 sentences read | **CONFIRMED** |
| Johnstown carries no qualifier | 9 hedge patterns = 0/0; every preceding word enumerated | **CONFIRMED** |
| Milliken exactly `most of Milliken` | public 145, `*.py` 31, llms.txt 1; 8 variants 0/0 | **CONFIRMED** |
| Severance exactly `most locations in Severance` | public 144, `*.py` 25, llms.txt 1; variants 0 | **CONFIRMED** |
| Windsor/LaSalle/Ault hedge, both halves | 3 pages, both halves present on all 3 | **CONFIRMED** |

Representative, `insulation-severance.html` JSON-LD `acceptedAnswer`:

> Which utility would rebate air sealing in Severance? **Not Atmos Energy.**
> Natural gas for most locations in Severance is supplied by Xcel Energy…

The hedge, verbatim and identical on all three pages:

> **Where Atmos Energy serves the home**, it rebates attic insulation at 75% of
> project cost where existing insulation starts below R-20, and rebates air
> sealing that documents a 20% leakage reduction, with Atmos publishing what each
> measure currently pays on its own rebate page — **Atmos service is not
> confirmed for every town in this area, so check your own utility before
> counting on it.**

**Correction to the brief's premise, recorded because acting on it would cause
harm.** The brief lists Windsor, LaSalle and Ault as Atmos-served. The property's
settled position is weaker and deliberately so:
`_shared_components.py:1523` sets `ATMOS_CONFIRMED_TOWNS = ('Greeley','Evans','Eaton')`,
and `_area_pages.py:35` records *"They are in Atmos's current tariff, but the
tariff proves Atmos serves them, not that it serves them exclusively. The hedge
stays; do NOT promote them."* Treating the brief's list as the standard would
license removing the hedge.

**DEFECT f1 (latent, not live)** — `_svc_pending_dense_pack_cellulose.py:226`
carries, inside an emitted FAQ string, an un-hedged Atmos rate two sentences from
a Severance naming: *"since Atmos rebates both at the same 75% of project cost …
which describes most of Severance."* Confirmed not live (no `dense` file in
`public/`, `describes most of Severance` = 0, no importer). If that file is ever
wired in, it reintroduces the two-year defect verbatim. Note for re-verifiers:
the rate and the town are in **adjacent** sentences, so a sentence-level sweep
returns 0 and misses it — use a paragraph window.

**DEFECT f2 (cosmetic)** — one `Lasalle` against 159 `LaSalle`, in a rendered
link on `public/insulation-rebate-hub.html:1149`.

### LGM Efficiency Works — REFUTED, four defects

`Efficiency Works` occurs **793** times in `public/` across 48 files (45 inside
tag attributes, 748 outside). Restriction markers: `Longmont Power & Communications`
390, `LPC` 193. Windowed analysis of all 748 decoded occurrences: **138 have no
`Longmont Power|LPC` within ±700 characters.** Most are benign comparatives; the
offer-shaped ones were isolated and read.

- **DEFECT f3 — three generated TL;DR blocks offer EW with no restriction.**
  `<aside class="atomic-answer">` — the featured-snippet / AI-extraction surface.
  On `insulation-basement-longmont.html`, `insulation-cathedral-ceiling-longmont.html`,
  `insulation-crawl-space-longmont.html`; nearest `LPC` 1496–1585 chars away:
  > **Efficiency Works pays a rate per square foot for basement wall insulation
  > specifically**; Xcel's rebate applies but publishes no dollar cap for this measure.

  Aggravating: the same generator file writes the crawl-space **body** copy
  correctly — *"available only to Longmont Power & Communications electric
  customers."* Repro: `/usr/bin/grep -rhoI 'Efficiency Works pays a rate per square foot' public/ | wc -l` → 3.
- **DEFECT f4** — `insulation-cellulose-longmont.html` states two EW rates
  unrestricted, nearest `LPC` 581 chars away.
- **DEFECT f5** — 10 of 15 meta descriptions mentioning EW drop the restriction.
  The pattern exists and was applied inconsistently (5 carry `(LPC-electric-only)`),
  which is what makes it a defect rather than a policy. This is the SERP surface
  served to Lafayette/Louisville/Niwot searchers.
- **DEFECT f6** — the site contradicts itself verifiably. `public/index.html`
  asserts *"Efficiency Works isn't mentioned on those pages because it doesn't
  apply there,"* while each of the three town pages mentions it twice. Mitigating:
  those 2 mentions **are** the correct restriction sentence, so no reader is
  mis-offered; what is false is the site's description of its own output.

On the three town pages themselves the copy is **correct** — both mentions are
the restriction sentence, in prose and JSON-LD, and the accuracy checks pass:
LPC correctly named as the municipal electric utility, scoped to "roughly 61% of
Longmont by area" cited to the Colorado Geospatial Portal, with 17 distinct
sentences tying Lafayette/Louisville/Niwot to Xcel-electric. **DCI and GCI carry
zero stray `Efficiency Works` mentions** (controls: DCI Xcel 2053, GCI Xcel 250)
— the class is LGM-only.

---

## g. STACKING — BODY AND JSON-LD, ALL THREE PROPERTIES

**Legitimate uses survived** (their loss would itself have been a finding):
DCI `stack effect` 12 + `stacks up` 1; LGM `stack effect` 4 + plumbing stack 1;
GCI `stack effect` 9 + vent stack 2. None swept.

**DCI — the 18 mandated stems are clean.** Of 73 raw `stack`, 16 are the URL
slug `whole-home-efficiency-bonus-stacking-denver.html`, 12 are "stack effect",
1 is "stacks up"; the remaining ~44 were read in context and are all building
science, spray-foam craft, or idiom. A broader 24-phrase denial sweep
(`cannot be stacked`, `only one rebate`, `not both`, `mutually exclusive`,
`no stacking`, …) = **0**, control `rebate` 2995. `one per` ×1 is the substring
in "any**one per**forming".

**DEFECT g1 (major) — DCI asserts additivity 75 times in vocabulary containing
zero of the 18 stems.**

```
/usr/bin/grep -roI 'adds a 25% bonus on all standard rebates' public/ | wc -l  -> 75
reconciled by parsing: 67 visible across 39 pages + 8 JSON-LD across 8 pages = 75
  occurrences containing ANY of the 18 mandated stems : 0
  visible occurrences with an Xcel attribution ±260ch : 3   (64 unattributed)
  JSON-LD occurrences carrying an Xcel attribution    : 0   (8/8 unattributed)
```

Served as FAQPage structured data on `insulation-attic.html`:

> The Whole Home Efficiency Bonus **adds a 25% bonus on all standard rebates**
> when three or more efficiency measures (e.g., attic + air sealing + duct
> sealing) are installed within two years of enrolling — **they do not have to be
> one project.**

That trailing clause is site-voice elaboration beyond the cited Xcel terms.
Commit `cd69991` asserts *"Every SENTENCE on the property is now silent on
stacking; what is left is an address."* **Refuted** — 67 visible sentences and 8
JSON-LD answers say the bonus adds on all standard rebates. DCI's own recorded
gloss (`_shared_components.py:704`) says unattributed additivity *"reads as this
site asserting Xcel's rebates combine, which is what the standing stacking
ruling forbids"*; by that rule 64/67 visible and 8/8 JSON-LD occurrences fail.

*(The underlying fact is true — verified verbatim against Xcel's 2025–2026 sheet
in section c3. The defect is the unattributed, site-voice framing, not the
figure.)*

**DEFECT g2 — DCI's own R4 verification is a phrasing-shaped grep.**
`/tmp/gate-close/r2/verify_r4b.sh` claims to verify "no page may assert or deny
that programs combine" but tests only nine literal strings **the same commit had
just deleted**. It greps for exactly what it removed, cannot fail, and did not
see the 75 occurrences above. This is the failure mode the discipline warns
about, inside the repo's own gate.

**LGM — DEFECTIVE, and in the forbidden direction (affirmative denial).**
Verified independently on both surfaces:

```
$ /usr/bin/grep -rhonI 'a single insulation rebate program to check, not two' public/ | wc -l  -> 2
$ /usr/bin/grep -rlI  'a single insulation rebate program to check, not two' public/          -> public/insulation-lafayette.html
  JSON-LD block#1: "…Xcel Energy serves both gas and electric here, so there's a single
                    insulation rebate program to check, not two."
control: 'rebate' in lafayette/louisville/niwot = 32 / 27 / 27
```

- `insulation-lafayette.html:932`: *"**One rebate program, one set of rules, one
  application.**"* — unqualified declarative count-of-one, contradicted by LGM's
  own `_shared_components.py:639`, which records Boulder County EnergySmart as
  "a third, income-qualified-only rebate as of January 1, 2026."
- The same numeric denial served as structured data on lafayette, and repeated
  on `insulation-louisville.html` and `insulation-niwot.html` (`:933/:1049`,
  `:933/:1048`, plus JSON-LD `:79` and `:71`).
- LGM has **no guard at all**: zero stacking checks in `_artifact_grep.sh`,
  `_postbuild_check.py`, `_out_guard.py`.

**GCI — COMPLIANT on the published property.** 240 JSON-LD blocks, 240 parsed, 0
failures (cross-check: `application/ld+json` = 240). Zero assertions, zero
denials in `public/`; residue all legitimate (`one per` ×5 is the substring in
"one person" in the WAP income limits). Three **non-emitted** generator comments
assert stacking as fact (`_shared_components.py:369`, `:3282`, plus unwired
`_svc_pending_*` docstrings) and should be reworded before a copy pass lifts
them; proof they don't ship: `combo`, `whole home efficiency`, `stack on` all 0
in `public/`, control `atmos` 627.

---

## h. THE DCI EMBED ATTRIBUTION LINK — CONFIRMED

**Instrument stated honestly: a real browser was driven.**
`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --headless --dump-dom`.
No `chrome`/`chromium` on `PATH`; no playwright, puppeteer or jsdom available —
Chrome.app was the one available engine and it worked. Grep was used only to
locate the file.

The embed lives on `public/r-value-needed-calculator-embed-code.html` (the only
`public/` file matching `iframe`; 0 real `<iframe>` tags, 1 `&lt;iframe` — it is
an escaped copy-paste snippet, so it was unescaped and rendered as a publisher
would). Chrome's own DOM API reported:

```
IFRAME COUNT: 1        ANCHOR COUNT: 1
ANCHOR[0] href=https://denvercoloradoinsulation.com/r-value-needed-calculator.html
ANCHOR[0] text="R-Value Needed Calculator by Denver Colorado Insulation"
ANCHOR[0] closest('iframe') = null (NOT inside an iframe)
ANCHOR[0] ancestor chain: A < P < DIV < DIV < BODY < HTML
ANCHOR[0] rel = null   display=inline   visibility=visible
```

Plain crawlable `<a>`, sibling subtree of the iframe, no `rel="nofollow"`,
visible. HTTP:

```
default UA   browser UA
200          200   /r-value-needed-calculator.html        (the attribution href)
200          200   /r-value-needed-calculator-embed.html
404          -     /definitely-not-a-real-page-zzz.html   <- negative control
```

No 403/406 encountered. Live snippet compared byte-wise to local: identical. The
generator enforces the invariant at build time
(`_generate_calculator_pages.py:1917`); five mutations were injected (anchor
inside iframe, `rel="nofollow"`, href repointed, `color:inherit` stripped, anchor
deleted) and all five fired.

**DEFECT h1 (minor, instrument only)** — the line the generator's own comment
calls *"the single most important requirement of this pass"*,
`assert 'iframe' not in ancestors`, is **unreachable dead code**: `html.parser`
treats iframe content as CDATA and never emits tags inside it. The defect is
still caught, by `assert len(w.anchors) == 1` firing with "found 0" — protection
holds, from a different line than the author believes.

---

## i. LIVE-VS-REPO BYTE VERIFICATION — CONFIRMED

Flags used, stated exactly: `curl -sS -o <file> -w '%{http_code} %{size_download}
%{content_type}\n' -A '<Chrome/125 UA>' -H 'Accept: */*' --max-time 60`.
**`--compressed` was NOT used** and no origin returned `Content-Encoding` on any
probe — bytes on the wire were identity. **`-L` was NOT used in the sweep**, so a
3xx is recorded as a 3xx. **No `$(curl …)` command substitution anywhere**;
bodies went to files via `-o` and comparison was `cmp`.

Enumerated with `/usr/bin/find <repo>/public -type f | sort`. All three
`public/` directories are flat, so URL = origin + `/` + filename.

| property | files | html | checked | identical | differs | non-200 |
|---|---|---|---|---|---|---|
| DCI | 85 | 75 | 85 | **85** | 0 | 0 |
| LGM | 59 | 48 | 59 | **58** | 0 | **1** |
| GCI | 49 | 38 | 49 | **49** | 0 | 0 |
| **total** | **193** | **161** | **193** | **192** | **0** | **1** |

Not sampled — 193 of 193. **No differing file on any property**: 192 `cmp`
invocations returned exit 0 with no output. No stale deploy, no server-side
minification, no injected analytics. **DCI is current**, including every file
touched by this pass's release commits (`last-modified: Sun, 20 Sep 2026
00:02:59 GMT` on `/`).

**Index behaviour is real, not a regression** (`--max-redirs 0`, no `-L`):

| property | `/index.html` | `location:` |
|---|---|---|
| DCI | **200** | *(none)* |
| **LGM** | **301** | **`/`** |
| GCI | **200** | *(none)* |

Exactly as reported — LGM alone 301s. Following it: `HTTPCODE=200
FINAL=https://longmontcoloradoinsulation.com/ REDIRS=1`, and `cmp
public/index.html` → exit 0, identical. That is the one non-200 in the table and
it is benign. Worth noting as infrastructure drift: the LGM 301 body is
`Moved Permanently. Redirecting to /` (35 bytes, a Go-style `http.Redirect`
body) despite a `server: nginx/1.24.0` header — a redirect layer the other two
lack.

Bare origin `/` on all three: 200 and byte-identical to `public/index.html`.
Known-missing path on all three: a true **404** status serving the repo's own
`404.html` byte-for-byte (not a soft-404). Sitemap `<loc>` sets (73/47/37, no
duplicates) cross-checked against the repo file set: **0 sitemap URLs with no
repo file** on any property. Probes for `/about`, `/.git/config`,
`/sitemap_index.xml`, `/wp-login.php` all returned the repo 404.

*NOT TESTED:* exhaustive live-file discovery (an unlinked, unsitemapped file at
an unguessed path would not be detected); `www.` and `http://` variants.

---

## j. ALL FOUR REPOS

All four on `main`, clean (`porcelain_lines=0`), `0/0` against `origin/main`, at
the SHAs recorded in the header table. Every worktree created by this review (8
across five scratch trees) was removed and pruned; `git worktree list` in all
four shows none of them. Canon retains only the three pre-existing
`~/code/canon-wt/*`. Nothing was edited, committed, pushed or deployed in any
repo except this file.

---

## k. THE FOUR "ALSO WORTH ATTACKING" ITEMS

### k1. The 20-vs-21 replay score — claim CONFIRMED, diagnosis REFUTED, and the verification command does not exist

**There is no replay harness.** `claim_gate.py` has no `--replay` mode
(`find . -name "score*.py"` → 0; positive control: 10 `*.py` exist in canon).
`GATE_SCORE_RERUN_2026-09-19.md:31` presents as its proof:

```
$ diff <(python3 score_base.py) <(python3 score.py)
IDENTICAL: every one of the 25 rows scores the same before and after this pass
```

**Neither script exists and neither was ever committed** —
`git log --all --diff-filter=A -- '*score.py' '*score_base.py'` → 0 across all
313 commits (positive control: the same query finds `claim_gate.py` at
`0e979f6`). The board's Project Rule requires a Done card to carry a
verification command; **this one cannot be run by anyone, including its author.**

The narrow claim nonetheless **holds**, reproduced by rebuilding the replay for
the moved row (5c, GCI's rebate figures at pre-fix `236c464`, `--today 2026-09-10`)
at four canon SHAs:

```
canon eafada2  EXIT=1   R3  RAW 769  ADJ 92
canon 9dc1277  EXIT=1   R3  RAW 769  ADJ 91
canon 38f177c  EXIT=1   R3  RAW 769  ADJ 91
canon c327bab  EXIT=1   R3  RAW 769  ADJ 91
distinct $ figures adjudicated: 7 at every SHA; $-bearing files: 16 at every SHA
```

Identical at `9dc1277` and HEAD, so **this pass did not cause the drop**.
Arithmetic checks: 20 CAUGHT + 3 PARTIAL + 2 MISSED = 25, and the table has
exactly 25 rows.

**But the "regression between `eafada2` and `9dc1277`" does not exist.** The
rerun never ran the replay at `eafada2`; doing so yields the same 7 figures
across the same 16 files. The entire delta is one row carrying no `$` at all — a
generator-SRC rank claim the config already files as REVIEW class. The two
documents measured different things on identical detection:

| reading | distinct `$` | `$`-bearing files | matches |
|---|---|---|---|
| adjudicated only | **7** | **16** | the RERUN's figure |
| adjudicated + filter-removed | 9 | 24 | GATE_CLOSE's figure |

The two figures adjudication drops are `$70,000` and `$99,920` — the WAP
income-eligibility limits, not rebate payouts. **So `21` was the inflated score,
not `20` the degraded one.** The rerun mis-attributes the difference to a
phantom regression and opens a debt to chase it. This is the repo's own
already-named `raw-vs-adjudicated` defect class (commit `b152b08`) recurring
inside the gate's own scorekeeping. Secondary: the prose *"Not one … changed a
single count"* is overstated — RAW counts did move (R2 337→316, R4 198→195,
R5 201→197); it should read "no adjudicated verdict changed."

### k2. Is the gate stale-by-default? — REFUTED; the hypothesis is backwards

As-of values, verbatim: `common.json:843 "2026-09-17"`, `dci.json:365
"2026-09-19"`, `gci.json:413 "2026-09-18"`, `lgm.json:370 "2026-09-18"`. No
wall-clock read anywhere (positive control: `datetime` → 6 hits in the same
file). **Exactly one code path consumes it** — `claim_gate.py:4306`, `if v >
today:` → `[future-date]`, R8 sub-test (b). Sub-tests (a), (c) and (d),
including the one named "stale review date", anchor on git history instead.

| as-of | DCI | GCI | LGM |
|---|---|---|---|
| baseline | 0 PASS | 0 PASS | 0 PASS |
| **2026-09-20 (tomorrow)** | **0 PASS** | **0 PASS** | **0 PASS** |
| 2026-09-26 | 0 PASS | 0 PASS | 0 PASS |
| 2026-10-19 | 0 PASS | 0 PASS | 0 PASS |
| 2026-09-18 (DCI pre-bump) | **1 FAIL** R8 ADJ 48 | — | — |
| 2026-09-17 (shared fallthrough) | — | **1 FAIL** R8 95 | **1 FAIL** R8 181 |

Run tomorrow with today's config, all three stay green and byte-identical.
Because the test is `v > today`, a **stale** as-of is strictly *more* sensitive —
it can only produce false positives, never false negatives. The gate cannot stop
detecting by going stale. The `38f177c` bump was genuinely load-bearing (48
`[future-date]` findings at 2026-09-18, matching the commit message).

**The real risk runs the other way.** An as-of set a month into the future is
accepted silently, renders R8(b) fully inert, and **nothing in the SUMMARY
announces it**. `--today` validates ISO format only; the config path is not
validated at all. Since the standing remedy for every recurrence is "bump the
constant," an overshooting bump is the unguarded failure mode. GCI and LGM are
correct greens today but with **zero margin** — max date on any R8 surface is
exactly 2026-09-18 on both.

### k3. The 129 report-only findings — CONFIRMED, and 7 are real defects live behind a green exit

Counts confirmed exactly by my own run (exit 0):

```
R3  REBATE DOLLAR FIGURE   RAW 1102  ADJ 121  REPORT (non-blocking)
R11 ATTRIBUTION DEBT       RAW 8     ADJ 8    REPORT (non-blocking)
blocking failures: 0      report-only findings: 2 (R3, R11)
WHAT REPORT-ONLY STATUS REMOVED FROM THE BLOCKING SET: 129 finding(s) … R3 121, R11 8.
CLAIM GATE: PASS
```

Two different demotion mechanisms: R3 by false-positive rate
(`common.json:1121 fp_rate_pct: 68.1` > `demote_above_pct: 25`); R11 not by
measurement at all — `claim_gate.py:5422` registers `blocking=False`.

**All 121 R3 findings adjudicated — exhaustive, sample size 121 of 121.**
Composition 119 T3 / 2 T2 / zero T1. **90 of 121 (74%) are one sentence** on 45
pages × 2 surfaces — the live, named, *linked* Xcel citation inside
`p.cited-stat`, on which R3 fires on the trigger word "larger", **including on
the CITE surface itself**. Unambiguous false positives.

**7 REAL of 121 (5.8%)**, 113 FP, 1 REVIEW. The real ones, live and uncited on
shipped pages — e.g. `public/xcel-insulation-rebate-guide-denver.html`:

> Within those programs, the base program covers three measures … **Customers
> with cooling-only Xcel service get a much smaller flat tier.**

No citation, no link, no `cited-stat` — an unsourced quantitative-comparative
claim about what Xcel pays. That is exactly R3's charge, and the gate exits 0.
The other real class (4 occurrences): *"capped per measure, so the larger the
job, the smaller the percentage."*

**The demotion measurement is stale.** R3's measured FP rate on DCI today is
**113/121 = 93.4%**, not the 68.1% pinned in config (taken at canon `62a09c7` on
47 findings portfolio-wide; DCI alone now has 121). The gate never re-takes it.

**SEVERE — R11 is excluded from the false-alarm sweep.** The negative-control
loop at `claim_gate.py:5773` reads `for rule in RULES: if not rule.blocking:
continue`. Proven by two-arm injection on a scratch canon:

```
ARM 1 (shipped, blocking=False):  EXIT=0  CONTROLS: 40 positive DETECTED, 0 MISSED · 17 negative clean, 0 FALSE ALARM
ARM 2 (flipped, blocking=True):   EXIT=2  CONTROLS: … 16 negative clean, 1 FALSE ALARM
  canary- NEG01 *** FALSE ALARM *** R11 row INJECT neg probe asserting 1 / attributed 1
```

The banner `17 negative clean, 0 FALSE ALARM` **does not cover R11**, whose
patterns include the very loose `"by check"`. R3 *is* covered.

GCI: R3 ADJ 9, all judged not-real (3× a FAQ *question*, 4× the config's own
REVIEW class). LGM: R3 RAW 582 → ADJ 0 via 12 enumerated filters — not a bare
zero. **GCI and LGM both have `R11.tracked_terms: []`** — zero R11 coverage,
though the gate labels this honestly as a null result rather than a PASS.

### k4. Does `regen_all.sh` halt? — CONFIRMED by injection on all three; but the halt is not on the deploy path

All three scripts carry exactly one `set` line — `27:set -e` — never unset, no
`trap`, no `pipefail` (positive control on a synthetic file returned matches, so
the zeros are measured). The gate call is byte-identical on all three and is the
last executable step:

```
166  echo "━━━ Standing claim gate ━━━"
167  "$(dirname "$0")/ops/claim_gate.sh" --brief
169  echo "━━━ Site regenerated. ━━━"
```

No pipe, no `|| true`, no `if`/`&&`/`!`, no subshell, no trailing `&`, no
captured-and-ignored `$?`. **All 8 defeat patterns absent** on all three, each
with a firing positive control. No deploy step exists inside `regen_all.sh`, so
nothing needed neutering.

Injection into the **generator** (proven necessary — a `public/` probe is wiped
by regen; a generator probe survives):

| | DCI | GCI | LGM |
|---|---|---|---|
| green build | 0 `PASS` | 0 `PASS` | 0 `PASS` |
| direct gate after injection | **1** `R5 ADJ 1 FAIL` | **1** `ADJ 1 FAIL` | **1** `ADJ 1 FAIL` |
| `regen_all.sh` exit | **1** | **1** | **1** |
| `Site regenerated` reached | **no** | **no** | **no** |

**SEVERE — the deploy path bypasses the gate entirely.** Deployment is a
separate, manually-run `ops/push-to-staging.sh` on all three properties. Read in
full: it **never** invokes `ops/claim_gate.sh` or `regen_all.sh` (it names
`regen_all.sh` only inside an error string at line 76). Its only preconditions
are that `public/` exists and holds ≥10 HTML files. `ops/push-to-staging.sh
<domain>` then `ssh root@… '/root/deploy.sh <domain>'` ships a `public/` no gate
has ever seen. `ops/hooks/` does not close it either (one file, `commit-msg`, no
gate reference). The wiring guards the build, not the ship.

**Bonus defect found during injection:** canon's own R5 canary sentence
(*"…lose 20-40% of their attic insulation performance to wind-washing at the
eaves"*), pasted onto a real DCI page, is detected and then **adjudicated away**
by `[code_context_markers]` because it contains "climate zone" and "eave".
RAW 523→524, ADJ 0, exit 0. The gate's own control sentence does not survive
contact with a real page.

**Stale comment:** GCI `regen_all.sh:143` and LGM `:163` both still assert *"so
DCI is deliberately NOT wired (it exits 1…)"* — false as of DCI `0d473a5`.

---

## l. OVERALL VERDICT

**The copy work is sound. The gate work is not.**

Every factual claim this pass rewrote or retained survived independent retrieval
against its primary source: DOE verbatim, EPA verbatim, Xcel verbatim against
the correct current edition, ENERGY STAR verbatim at the URL it cites, and — on
a property outside the pass's scope — Atmos verbatim. One suspected wrong
citation and one suspected mis-dated edition were both raised and both retracted
on evidence. That is a genuinely good result and it is the part of the pass that
matters most.

The gate work went the other way. R5 was driven from 31 findings to 0, and the
single change that closed the last of them was selected from a 2×2 in which
exactly one cell is green on DCI. Four of the six changes are allowlists wearing
a repair's clothes; two are real repairs, one of which shipped a bundled
pool-move that silently drops a rule the move was never measured against.

**What is still wrong, in severity order:**

1. **`1c7b354` blinds R2, R4 and R7 — three BLOCKING rules — plus R3, on all
   three properties**, to any claim wrapped in a code-shaped generator string.
   189,985 characters excluded with no per-rule accounting, on a 143-character
   blindfold. A regression created inside this pass: `889e172` catches these,
   `1c7b354` does not.
2. **DCI's R5 zero is filter-widening, not repair.** With the same content, the
   pre-pass gate still finds 24 R5 findings; all 24 are cleared by the four
   filters this pass widened, and restoring one integer returns the flagship
   property to `exit 1` with five live unsourced figures.
3. **The deploy path never runs the gate** (`ops/push-to-staging.sh`, all three
   properties). Every green exit reported by this pass describes the build, not
   the artifact that ships.
4. **20 proven new evasions** across five of the six commits, including 8 on the
   question guard (`Why does X?` and `How does X?` — this portfolio's own heading
   idiom — both presuppose X and both clear), the probe the pass was explicitly
   forbidden to clear (defeated by deleting one comma), and an unbounded
   laundering distance where 47 characters was previously refused.
5. **The 86 vectors no longer measure this gate.** Their result is byte-identical
   at all seven SHAs because every one of this pass's changes landed outside
   their span. 14 of 86 miss (12 measurable; two R9 vectors are unscorable
   because the harness's own R9 control does not fire — the prior read's headline
   of 11 scored one of them off an `exit 1` that R5 produced).
3. **`derivable_constants` can permanently suppress any figure on a property**
   with one sentence of unvalidated free text, clears a co-occurring unrelated
   number, and clears canon's own control fixture when six words are prepended.
4. **7 real R3 defects live on shipped pages behind a green exit**, on a
   demotion whose false-positive measurement (68.1%) is stale against today's
   actual 93.4%.
5. **`R11` is excluded from the negative-control sweep**, so its
   `0 FALSE ALARM` banner is not evidence about R11.
6. **`Xcel` as a bare token is now a recognised publisher**, contradicting the
   config note shipped in the same commit, and payer-laundering is reopened.
7. **A fourth vermiculite page was never swept** and carries the pre-correction,
   unattributed claim on both surfaces — invisible to R5 because R5 requires a
   `magnitude_word` and market-share statistics carry none.
8. **DCI asserts rebate additivity 75 times** (67 visible, 8 JSON-LD; 72
   unattributed) in vocabulary containing none of the 18 stems the standing rule
   is checked against, and **LGM affirmatively denies stacking** on three pages
   in both prose and JSON-LD.
9. **LGM offers Efficiency Works without its LPC restriction** on three TL;DR
   blocks, one cellulose page, and 10 of 15 meta descriptions.
10. **The replay score's verification command does not exist**, and its stated
    diagnosis ("a pre-existing regression between `eafada2` and `9dc1277`") is a
    raw-vs-adjudicated artifact, not a regression.

**The structural point underneath all of it:** the gate has no rule that checks
whether a citation is *correct* — canon recorded this itself in commit
`55c5ca8`. Exit 0 is evidence about form, never about truth. This pass's
sourcing held up under retrieval; that was the authors' judgement doing the
work, not the gate's.
