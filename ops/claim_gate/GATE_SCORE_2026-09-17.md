# Claim Gate — score report, 2026-09-17

R3 of a 4-row pass. This row RAN the standing claim gate, reported every
finding, adjudicated true findings from false positives, and SCORED the gate by
replaying the last two weeks' known defects out of git history.

This row changed no page, no generator, no config, no fixture, no live site.
The only file it wrote in canon is this one.

Gate under test: canon `ops/claim_gate/claim_gate.py` + `surfaces.py` +
`config/{common,dci,lgm,gci}.json` + `fixtures/` (24 positive, 15 negative),
at canon HEAD `7a091a0`.

Properties, at the HEADs measured:

| property | repo | HEAD | public/ |
|---|---|---|---|
| DCI | denvercoloradoinsulation.com | `1b6949c` | 85 files / 75 html |
| LGM | longmontcoloradoinsulation.com | `a86c5af` | 59 files / 48 html |
| GCI | greeleycoloradoinsulation.com | `ee0157d` | 49 files / 38 html |

---

## 0. HALT-LEVEL FINDING, FIRST, BECAUSE IT GOVERNS EVERYTHING BELOW

**The gate exits 2 — `CLAIM GATE: NOT RUN` — on every DCI tree that still
carries the R6 calculator defect. It refuses to run precisely when the defect it
exists to catch is present.**

Verified by me directly on three separate DCI worktrees:

```
########## dci-58c44eb ##########   EXIT=2
########## dci-130921c ##########   EXIT=2
########## dci-169bb3c ##########   EXIT=2
  canary- NEG01  fixtures/negative/NEG01.html  *** FALSE ALARM *** R6 G1 branch
  reads {gap} while the printed string interpolates {pctShort} | Moderately
  under cod | ... R6 G2 threshold 20 on {gap} is unreachable for basement
  (targetMin 15) while the printed quantit
  CONTROLS: 20 positive DETECTED, 0 MISSED · 0 negative clean, 14 FALSE ALARM
CLAIM GATE: NOT RUN — a rule that cannot detect its own defect is worse than
no rule, because it manufactures confidence.
```

All 14 negative controls false-alarm, and **all 14 alarms are R6 and only R6**.
Cause, located independently by three agents and consistent with the code:
`claim_gate.py:2367` builds each negative-control context as
`_control_ctx(base, {}, _fixture_paths(path), repo)` — an **empty overlay**, so
the real property config applies — and `_control_ctx` (`:2310`) sets
`ctx.gen = base_cfg.get("_gen")`, the **real repo's generator source**.
`rule_R6` (`:1448-1453`) then opens `os.path.join(ctx.repo, ch["generator"])`
regardless of the fixture read set. So any genuine R6 finding in the repo under
test is attributed to all 14 negative fixtures. The file's own comment at
`:2275` says controls run "against fixture files only"; for SRC/generator rules
that is false.

Consequences that must not be softened:

1. **The shipped gate scored NOTHING on DCI, at any SHA in the replay window.**
   Every DCI rule number in this report was obtained by three agents
   independently building a harness in `/tmp` that imports `claim_gate`
   unmodified and forces the control `ok` flag True. Those are RULE-LEVEL
   verdicts, labelled as such throughout.
2. It is not a property of "pre-fix" trees. DCI's R6 defect (D3) was fixed at
   `37c7b29` on 2026-09-11, one day AFTER `92f3887`, so the gate exits 2 on
   `92f3887` too.
3. One unfixed R6 defect blinds all eleven rules. At `539670e` a known,
   accepted, explicitly out-of-scope R6 defect suppressed the reporting of two
   in-scope ones.
4. `--opt-in=R6b` **forces exit 2 on every repo, clean or not.** There is no
   R6b implementation: `/usr/bin/grep -n 'R6b' claim_gate.py` returns only flag
   plumbing and `OPT_IN_RULES = {"R6b": "browser cross-product"}`. Passing the
   flag appends a `*** MISSED ***` control row which increments `pos_missed`.

A second, replay-only blocker: `dci.json` carries `min_artifacts: 85` and
`expected_html: 75`, both `measured_at: {"date":"2026-09-17"}`. Historical DCI
trees carry 82–83 artifacts / 73 html, so even past the control abort the gate
halts with `ZERO-ARTIFACT TRAP`. The floor is absolute, not relative.

---

## 1. PART 1 — THE RUN

### Control phase (`--canary`)

All three properties: **exit 0**, `CONTROLS: 20 positive DETECTED, 0 MISSED ·
14 negative clean, 0 FALSE ALARM`, and `public/ mtimes unchanged across the
control phase` (85 / 59 / 49 files verified). No control failure at HEAD.

### Blocking runs

| property | exit | corpus check | read set |
|---|---|---|---|
| DCI | **1** | `git ls-files public/ = 85   find public/ -type f = 85   AGREE` | 80 artifacts (75 html, 2 txt, 1 xml, 2 svg); excluded 5 |
| LGM | **1** | `= 59   = 59   AGREE` | 54 artifacts (48 html, 2 txt, 1 xml, 3 svg); excluded 5 |
| GCI | **1** | `= 49   = 49   AGREE` | 44 artifacts (38 html, 2 txt, 1 xml, 3 svg); excluded 5 |

Both corpus enumeration methods AGREE on all three — that dual enumeration is
the structural fix for the historical `sitemap.xml`-only corpus hole.

### R2's reported counts, independently verified

**Zero divergence.** All 33 adjudicated counts reproduce exactly:

```
DCI  R1 94  R2 18  R3 67  R4 23  R5 213  R6 0  R7 2  R8 77  R9 57  R10 0  R11 5 rows
LGM  R1 94  R2 52  R3 13  R4  0  R5  36  R6 0  R7 0  R8 161 R9  0  R10 0  R11 0
GCI  R1 70  R2 98  R3 22  R4  0  R5  35  R6 0  R7 0  R8 38  R9  0  R10 2  R11 0
```

---

## 2. PART 2 — RAW / FILTER / ADJUDICATED ARITHMETIC

I recomputed `raw − Σ(removed) == adjudicated` by hand for every rule on every
property. **The identity holds in all 33 cases.**

An arithmetic trap worth recording: each FILTER row prints two numbers —
*matched*, then `(removed N)`. Only the `(removed N)` column sums to the
identity, because a hit already claimed by an earlier filter is counted as
matched but not removed by a later one. Summing the first column gives a wrong
answer.

**DCI**
```
R1   97 − 3                                        = 94
R2   18 − 0                                        = 18
R3  893 − (0+17+19+140+576+0+0+74+0)   = 893 − 826 = 67
R4  436 − (65+348+0+0+0+0)             = 436 − 413 = 23
R5  399 − (88+57+18+1+22+0+0)          = 399 − 186 = 213
R6    0 − 0                                        = 0
R7    2 − 0                                        = 2
R8   77 − 0                                        = 77
R9   57 − 0                                        = 57
R10   0 − 0                                        = 0
R11   5 tracked-term rows (REPORT-ONLY)
```
**LGM**
```
R1   99 − 5                                        = 94
R2   64 − 12                                       = 52
R3  577 − (8+113+12+151+232+0+0+48+0)  = 577 − 564 = 13
R4  299 − (15+284+0+0+0+0)             = 299 − 299 = 0
R5  199 − (51+65+41+0+4+2+0)           = 199 − 163 = 36
R8  161 − 0                                        = 161
R10   7 − (2+0+5+0+0)                              = 0
R7, R9  0 raw, 0 adjudicated
R11   0 tracked terms — NULL RESULT, explicitly not reported as PASS
```
**GCI**
```
R1   78 − 8                                        = 70
R2  126 − (24+4)                                   = 98
R3  343 − (20+2+12+105+144+0+0+38+0)   = 343 − 321 = 22
R4   70 − (24+46)                                  = 0
R5  150 − (29+46+18+0+20+2+0)          = 150 − 115 = 35
R8   39 − 1                                        = 38
R10  29 − (0+25+2+0+0)                             = 2
R6, R7, R9  0 raw, 0 adjudicated
R11   0 tracked terms — NULL RESULT
```

### Filters that silently dropped a REAL hit

The arithmetic holding does not mean the filters are correct. Four confirmed
over-removals, each a real defect pardoned:

1. **LGM R3, `cost_context_markers`** — removed **103 of the 133** rebate
   figures the Director ruled off the site. `common.json` puts `"per square
   foot"` / `"per sq ft"` in `cost_context_markers`; Efficiency Works
   *denominates its payout* in dollars per square foot. The filter that exists
   to spare installed-cost rates blinds the rule to an entire program's payout
   schedule — 65 × `$1.16` + 38 × `$0.77`, all removed, verbatim:
   `[cost_context_markers (Ruling 2 -- costs, not payouts)] … "Efficiency Works
   pays $1.16 per square foot for most insulation measures… [$1.16]`
2. **DCI R3, `income-eligibility threshold (WAP standing exception)`** —
   removed all 12 City of Golden rebate-match caps, which `dci.json` itself
   records as real program caps. The 120-char window contains "at or below 80%
   of Area Median Income", so the eligibility phrase pardons the cap beside it.
   Same mechanism removed 77 of 173 `$600` hits.
3. **DCI R5, `recognised_publishers named in the same sentence`** — removed the
   only two `25-40%` rows on `insulation-lakewood.html`, because "Xcel Energy"
   appears as the *payer*. Naming the payer of a rebate is not attribution of
   the site's own share statistic to Xcel as its *publisher*. That is exactly
   the "site-authored figure wearing a utility's name" pattern `147185c` was
   fixing.
4. **R4, `NEUTRAL -- fewer than two distinct programs, or no predicate`** — the
   single largest false-negative source in the gate. It removed the LGM
   knob-and-tube stacking denial, the GCI FAQPage stacking denial, the DCI
   `llms.txt` `rebate-stack` claim, and the 70-page DCI `primary rebate stack`
   boilerplate. Root cause: bare `"Xcel"` is absent from `R4.programs`, so a
   claim naming one recognised program scores `distinct < 2` and is filtered.

---

## 3. PART 3 — EVERY FINDING, BY DEFECT CLASS, WITH ADJUDICATION

Adjudication key: **TRUE** = a real defect correctly caught. **FP** = benign
copy the rule should not have flagged. **REVIEW** = genuinely ambiguous.

### 3.1 Summary table — TRUE / FP / REVIEW and the false-positive rate

| property | rule | adjudicated | examined | TRUE | FP | REVIEW | **FP rate** |
|---|---|---|---|---|---|---|---|
| DCI | R1 | 94 | 94 | 0 | 18 | 76 | **19.1%** |
| DCI | R2 | 18 | 18 | 0 | 18 | 0 | **100%** |
| DCI | R3 | 67 | 67 | 10 | 57 | 0 | **85.1%** |
| DCI | R4 | 23 | 23 | 23 | 0 | 0 | **0%** |
| DCI | R5 | 213 | 213 | 184 | 8 | 21 | **3.8%** |
| DCI | R7 | 2 | 2 | 0 | 1 | 1 | **50%** |
| DCI | R8 | 77 | 77 | 77 | 0 | 0 | **0%** |
| DCI | R9 | 57 | 57 | 56 | 0 | 1 | **0%** |
| DCI | R11 | 5 rows | 5 | 5 | 0 | 0 | **0%** (report-only) |
| LGM | R1 | 94 | 94 | 5 | 9 | 80 | **9.6%** |
| LGM | R2 | 52 | 52 | 3 | 43 | 6 | **82.7%** |
| LGM | R3 | 13 | 13 | 0 | 13 | 0 | **100%** |
| LGM | R5 | 36 | 36 | 22 | 3 | 11 | **8.3%** |
| LGM | R8 | 161 | 161 | 161 | 0 | 0 | **0%** |
| GCI | R1 | 70 | 70 | 7 | 18 | 45 | **25.7%** |
| GCI | R2 | 98 | 98 | 0 | 78 | 20 | **79.6%** |
| GCI | R3 | 22 | 22 | 0 | 17 | 5 | **77.3%** |
| GCI | R5 | 35 | 35 | 26 | 1 | 8 | **2.9%** |
| GCI | R8 | 38 | 38 | 38 | 0 | 0 | **0%** |
| GCI | R10 | 2 | 2 | 0 | 2 | 0 | **100%** |

Every finding was examined; nothing was sampled-and-extrapolated.

### 3.2 R1 FABRICATED QUOTATION — 94 / 94 / 70

R1 has two halves. The property notes read
`half A (CLAIM TEST) 76 · half B (STRING LIST -- cannot be a claim test) 18`
(DCI), `80 / 14` (LGM), `45 / 25` (GCI), and on every property
`registry quote field: 0 True`.

**Half A (76 / 80 / 45) — REVIEW.** Half A flags every registry-backed
`According to X, "…"` block whose registry entry lacks an explicit
`quote=true`. Because **no registry entry on any property has `quote=True`**,
half A flags 100% of attributed quotations. The rule prints its own limit:
`DEGRADED R1 DEGRADED: provenance block not yet in the schema; asserting quote
field only (spec 12.1)` and
`blind spot: this rule cannot read the cited PDF. It asserts the PRESENCE and
SHAPE of a provenance record, not the accuracy of the quote`.
These are a real provenance-schema debt — the field genuinely is absent — but
they are **not evidence of fabrication**. The verbatim rows are accurate
quotations of EPA, ENERGY STAR, IRC, BASC, ACCA, CDPHE, Census. Example:
`public/insulation-blown-in-longmont.html:CITE  A  ENERGYSTAR_R49_R60 According
to ENERGY STAR , “Climate Zone 5 homes need attic insulation rated R-49 to R-60
for optimal performance.”`

**Half B — mixed, and the FP classes are sharp.**

FP class B-i, *site-voice scare quotes* (4 on each property, one sentence ×4
surfaces):
`public/about.html:VIS  B  The guidance here says "not yet" as often as it says
"yes," because the referral is only worth making when the work is worth doing.
[says]`

FP class B-ii, *hypothetical dialogue / hypothetical contractor quote* (8 on
DCI):
`public/choosing-denver-insulation-contractor.html:VIS  B  The post-hailstorm
pattern — someone at your door says they "noticed your roof" and can quote your
attic today only — is a storm-chaser model applied to insulation.  [says]`
`public/insulation-dense-pack-cellulose.html:VIS  B  If a quote says "blown-in
cellulose" for a wall without naming a density, that is the number to ask for.
[says]`
`public/insulation-duct-sealing.html:LD  B  If a quote says "tape the joints"
and does not say mastic, ask which tape and ask what happens to it in a
130-degree attic.  [says]`

FP class B-iii, *the Sources block, already counted in half A* (2 DCI / 5 LGM /
14 GCI) — a pure double count:
`public/vermiculite-insulation-denver.html:VIS  B  Sources What the data says
According to the EPA , “you should assume that vermiculite insulation is from
Libby…  [According to]`

TRUE in half B — hand-written attributed quotations of a third-party document,
which genuinely need a provenance record (0 DCI / 5 LGM / 7 GCI):
`public/air-sealing-longmont.html:LD  B  Efficiency Works' incentive sheet says
its tiers are based on "reduction of air loss from initial testing with blower
door" but does not name a specific unit.  [says]`
`public/insulation-garage-longmont.html:VIS  B  Xcel's own product write-up says
the product excludes “new residential construction, new residential additions,
insulation of doors, garages, sheds, workshops, belo  [says]`
`public/attic-mold-greeley.html:VIS  B  The EPA states directly that it “does
not have a certification program for mold inspectors or mold remediation
firms.”  [states]`
`public/rodent-insulation-hantavirus-greeley.html:VIS  B  …the CDC's clinical
overview states a case-fatality rate of “nearly 4 in 10” for people who develop
HPS.  [states]`

**Verdict on R1: USABLE AS A CENSUS, NOT AS A DETECTOR.** In its current
DEGRADED form R1 cannot distinguish an accurate quotation from a fabricated
one; its 94/94/70 are a census of attributed quotations. It caught the central
fabricated-quotation defect (§4.1) — but by flagging all 122 quotations on that
tree, of which the fabrication was one.

**Recommended tightening (do not implement — R2 owns the code):** land the
provenance block the DEGRADED line names, then flag only entries whose
provenance record is absent or whose `quote=true` text does not byte-match the
rendered span. Until then mark half A REPORT-ONLY. For half B, require the
quoted span to be preceded by a *named publisher* within the sentence and
exclude spans whose attributing subject is generic (`a quote`, `someone`, `the
guidance here`); and de-duplicate half B against half A on block identity,
which removes the Sources-block double count outright.

### 3.3 R2 WRONG-UTILITY CLAIM — 18 / 52 / 98. THE WORST RULE IN THE GATE.

**R2 produced zero true positives across all three properties.**

**DCI — 18 findings, all `United Power`, all FP.** See §6 for the full
adjudication with primary-source evidence.

**LGM — 52 findings.** Class tally:
- 32 FP — the LPC coverage disclosure, an explicitly *verified* territory fact,
  flagged for naming the two cooperatives that serve the non-LPC 39%:
  `public/insulation-attic-longmont.html:VIS  a  Poudre Valley REA |
  scope=Longmont | Longmont Power & Communications, the city's own municipal
  electric utility, doesn't cover the whole city — verified against Colorado's
  official utility-territory data, LPC serves roug  [utility-not-serving-town]`
  `public/insulation-longmont.html:VIS  a  United Power |
  scope=Lafayette,Longmont,Louisville,Niwot | Verified against Colorado's
  official electric-utility-territory data: roughly 61% of Longmont's area is
  LPC electric; the rest splits between Xcel, Poudre Valley
  [utility-not-serving-town]`
- 6 FP — a **correct denial** flagged as a wrong-utility claim:
  `public/insulation-lafayette.html:VIS  a  Longmont Power & Communications |
  scope=Lafayette | Longmont's situation (a second, Longmont Power &
  Communications-only rebate) doesn't apply in Lafayette.
  [utility-not-serving-town]`
- 5 FP — `town-blind-tool`, where the tool asks the *more precise* question:
  `public/attic-insulation-cost-calculator-longmont.html:JS  t  Longmont Power &
  Communications named in a verdict-reachable JS literal with no town input |
  you indicated your electric utility is not LPC, so this program does not
  apply to your address.  [town-blind-tool]`
  The rule penalises a calculator for asking the visitor's **utility** instead
  of their **town**. Asking the utility is strictly better.
- 6 REVIEW — a bare program name in JSON-LD on a town the program does not
  serve; machine-facing mis-association, a human should rule:
  `public/insulation-lafayette.html:LD  a  Efficiency Works | scope=Lafayette |
  Efficiency Works Retrofit Rebate Program  [utility-not-serving-town]`
- 3 TRUE — a Longmont-specific wayfinding URL on a non-Longmont town page. The
  utility label is mis-assigned (the URL is the city government, not the
  utility) but the underlying cross-town defect is real:
  `public/insulation-lafayette.html:ATTR  c  Longmont Power & Communications |
  scope=Lafayette | https://longmontcolorado.gov/building-inspection/building-codes/  [wayfinding-url]`

**GCI — 98 findings, 0 TRUE, 78 FP, 20 REVIEW.** GCI's territory is genuinely
split (ATMOS: Greeley, Evans, Eaton, Windsor, LaSalle, Ault; XCEL GAS:
Johnstown, Milliken, Severance), so every page must disclose the split — and
R2 flags the disclosure.

The three Xcel towns were corrected on 2026-09-08 (`e6cb44e`). At HEAD their
pages are **right**, and R2 flags them anyway. All 13 Atmos rows on the
Johnstown page, verbatim, include:
`public/insulation-johnstown.html:VIS  a  Atmos Energy | scope=Johnstown | Who
pays for it, and on what terms, is a question about your gas utility — and in
Johnstown the natural gas utility is Xcel Energy, not Atmos Energy.
[utility-not-serving-town]`
`public/insulation-johnstown.html:VIS  a  Atmos Energy | scope=Johnstown | The
Atmos program described elsewhere on this site is for the towns Atmos serves and
does not apply to a Johnstown home.  [utility-not-serving-town]`
`public/insulation-milliken.html:VIS  a  Atmos Energy | scope=Milliken | What it
is worth to you depends on your gas utility, and for most of Milliken that is
Xcel Energy rather than Atmos Energy — Xcel sets out its own insulation and air
sealing rebate terms,  [utility-not-serving-town]`

Sub-class `qualifier-cross-contamination` (20 rows) flags each town page for
carrying the accurate site-wide split sentence:
`public/insulation-windsor.html:VIS  x  town Windsor page carries Severance's
qualifier 'most locations in Severance' | Which utility to ask about an
insulation rebate depends on your town: Atmos Energy's residential rebates are
the primary insulation rebate p  [qualifier-cross-contamination]`

Sub-class `electric-utility-named` (4 rows) includes a **developer comment**
that reaches no reader:
`public/insulation-rebate-eligibility-checker.html:JS  e  Xcel Energy named
beside an electric word | // Xcel: only surfaced for electric heat, and always
hedged.  [electric-utility-named]`

Root cause, precisely: `gci.json`'s `allowed_multi_utility_sentences` holds
**4 exact strings**, and the pages carry many correct paraphrases of the same
fact. The filter removed 24 of 126; the rest became false positives. This is
the **inverse paraphrase escape** — the same string-list brittleness that let
defects escape past sweeps now makes correct copy fail.

**Verdict on R2: TOO NOISY TO BLOCK ON. Mark REPORT-ONLY until fixed.** At
79–100% FP on every property, it will be ignored by every future session and
therefore manufactures the appearance of territory coverage while providing
none. It is also load-bearing for a real defect class (§4.2), so it must be
fixed, not deleted.

**Recommended tightening:** resolve the utility *against the subject of its own
clause* rather than against the page's town. If the sentence assigns the utility
to a named town (`Atmos … in Greeley, Evans and Eaton`) or explicitly denies it
for the page's town (`not Atmos Energy`, `does not apply to a Johnstown home`),
it passes. Concretely: (a) suppress when a denial marker binds the utility to
the page's own town; (b) suppress when the utility is named in the same clause
as a town it *does* serve; (c) exclude JS comments from the claim set entirely;
(d) scope `forbid_electric_utility_naming` to AREA_PAGES towns, as its own
config reason says, rather than site-wide; (e) treat `town-blind-tool` as
satisfied when the tool asks for the utility directly.

### 3.4 R3 REBATE DOLLAR FIGURE — 67 / 13 / 22. NOTHING TRUE TO FIND, 87 ALARMS.

**DCI has ZERO dollar figures at HEAD.** Measured by me:
```
$ /usr/bin/grep -oIE '\$[0-9][0-9,.]*' -r .../denvercoloradoinsulation.com/public/ | wc -l
       0
$ /usr/bin/grep -oI "Denver" -r .../denvercoloradoinsulation.com/public/ | wc -l   # control
    3154
```
The strip landed on 2026-09-10. R3 nonetheless returns 67 findings.

**DCI R3 — 40 × T2, every one a false positive.** Exact token tally:
`000`×7, `500`×5, `800`×4, `0.8`×4, `119`×3, `0.1`×3, `895`×2, `4999`×2,
`100`×2, `888`, `8399`, `80020`, `707`, `280`, `150`, `130`, `0.85`. What they
actually are, verbatim:
- square footage — `A typical 1,500-2,000 sq ft Denver attic top-up finishes in
  4-6 hours`; `Centennial's larger 2,800-square-foot footprints`; `A typical
  1,000 sq ft crawl`; `larger conditioned envelopes (3,000+ sq ft)`
- a ZIP code — `every Broomfield ZIP (80020, 80021, 80023)`
- phone numbers — `you call Xcel at 800-895-4999`; `Phone: (888) 707-8399`
- a sitemap priority — `<priority>0.8</priority>`, `<priority>0.85</priority>`
- a statute number — `terminated early by Public Law 119-21`
- vapour permeability — `Class I is 0.1 perm or less`
- attic temperature — `can hit 130-150°F on a hot Denver afternoon`
- the elevation anchor — `Solar Gain at 5,280 Feet`
- freeze-thaw cycles — `at 5,280 feet with 100-plus freeze-thaw cycles`

**DCI R3 — 27 × T3 rank claims: 10 TRUE, 17 FP.** TRUE examples (a
rebate-magnitude claim stated in words, with no numeral — precisely what T3 is
for):
`public/attic-insulation-cost-calculator.html:VIS  T3  larger,smaller | Xcel
rebates (standard + Whole Home Efficiency Bonus) are capped per measure, so the
larger the job, the smaller the percentage.  [rank-claim]`
`public/xcel-insulation-rebate-guide-denver.html:VIS  T3  smaller | Customers
with cooling-only Xcel service get a much smaller flat tier.  [rank-claim]`
FP examples — "larger" describing project scope, house size or HVAC capacity,
not a rebate:
`public/insulation-rim-joist.html:VIS  T3  larger | Photos of the treated run go
into the project file for the rebate paperwork submitted with the larger
insulation and air-sealing scope.  [rank-claim]`
`public/hvac-sizing-after-insulation-denver.html:VIS  T3  a fraction of |
Variable-speed and modulating systems can throttle down to a fraction of rated
capacity…  [rank-claim]`
`public/insulation-duct-sealing.html:LOWVIS  T3  largest | The largest scope
here — crawl encapsulation alone costs more than any other approach on this
list  [rank-claim]`
And one that is an **attributed, cited Xcel quotation**, which R3's own
attribution exception should have spared:
`public/whole-home-efficiency-bonus-stacking-denver.html:CITE  T3  larger |
customers can receive larger attic insulation and washer and dryer rebates, as
well as a 25% bonus on all standard rebates…  [rank-claim]`

**LGM R3 — 13 findings, ALL 13 false positives, 100%:**
- 9 × the citation *print code*: `Xcel Energy's 2025–2026 Colorado Residential
  Rebate Summary (print code 25-12-215)` → token `215`
- 3 × the company phone number: `Phone: (720) 491-3309` → `720`, `491`, `3309`
- 1 × an SVG path coordinate: `<line x1="98" y1="210" x2="230" y2="210"/>` → `230`

**GCI R3 — 22 findings, 0 TRUE, 17 FP, 5 REVIEW.** The FPs:
a bill number (`HB25-1202`), a NOAA document id inside a URL
(`repository.library.noaa.gov/view/noaa/60225/`, ×2), a Sitecore URL fragment
(`cogy-p-001`, ×4), a design wind speed (`115 mph design wind speed`, ×3), the
print code `25-12-215`, an SVG coordinate `230`, sitemap priorities `0.9`×2 and
`0.85`, and a **FAQ question** flagged as a rank claim ×3:
`public/insulation-evans.html:VIS  T3  smaller | Is the rebate worth the
paperwork on a smaller job?  [rank-claim]`
REVIEW (5): `the single biggest lever on the result` — a rank claim about a
rebate's importance rather than its amount.

**Verdict on R3: TOO NOISY TO BLOCK ON as currently filtered. Mark T2
REPORT-ONLY; keep T1 and T3 blocking.** T1 is excellent — on the replay it
matched the human sweep exactly, 198/198 on DCI and 206/206 on GCI (§4.5). T2
is the sub-type that closes the bare-digit blind spot and it must survive, but
its money-window heuristic cannot presently tell a rebate from a ZIP code.

**Recommended tightening for T2:** before flagging a bare numeral, exclude it
when the match is inside (a) a URL, `href`, `src` or any attribute value;
(b) an XML/SVG numeric attribute or path; (c) a telephone pattern
`\(?\d{3}\)?[- ]\d{3}-\d{4}`; (d) a postal code adjacent to a state or "ZIP";
(e) a `\d+(\.\d+)? (sq ft|square feet|square-foot|mph|perm|°F)` unit phrase;
(f) a statute/print-code pattern `\b\d{2}-\d{2}-\d{3}\b` or `Public Law \d+-\d+`;
(g) the configured `elevation_anchor`. For T3, require the rank word to govern a
*rebate or payment* noun within the same clause, and honour the attributed-and-
sourced exception that T1 already has.

### 3.5 R4 STACKING — 23 / 0 / 0. ACCURATE WHERE IT FIRES, BLIND WHERE IT MATTERS.

All 23 DCI findings are `ASSERTS`, each naming two or more distinct programs
combining, with `DENIES 0`. Under R4's stated standard — *silence is the
compliant state and affirmative denial is equally a defect* — all 23 are TRUE.
Distinct classes, verbatim:

`public/index.html:VIS  ASSERTS  bundl | programs=Combo Bonus,Whole Home
Efficiency Bonus,Xcel's income-qualified programs | If your home is in Xcel
territory and the work brings under-insulated areas up to current code, yes —
several Xcel programs are  [ASSERTS]`
`public/insulation-attic.html:LD  ASSERTS  bundl | programs=Whole Home
Efficiency Bonus,Xcel Energy | Crew completes Xcel Energy rebate forms (standard
Insulation and Air Sealing Rebate, Whole Home Efficiency Bonus paperwork if
multiple measures were bundled, and  [ASSERTS]`
`public/insulation-crawl-space.html:VIS  ASSERTS  bundl | programs=Whole Home
Efficiency Bonus,Xcel Energy | The 2026 Xcel Energy Insulation and Air Sealing
Rebate covers a portion of qualifying crawl space work, and the Whole Home
Efficiency Bonus applies when bundled.  [ASSERTS]`
`public/insulation-blower-door-test.html:VIS  ASSERTS  unlock,unlocks |
programs=Combo Bonus,Whole Home Efficiency Bonus | Against that sits what the
test unlocks: the Xcel Insulation and Air Sealing Rebate pays out against
per-measure caps, by check, after the work; the Who  [ASSERTS]`
`public/r-value-needed-calculator.html:JS  ASSERTS  bundl | programs=Whole Home
Efficiency Bonus,Xcel Whole Home Efficiency Bonus | Usually only worth it if
bundled with air sealing for the Xcel Whole Home Efficiency Bonus.  [ASSERTS]`
`public/insulation-northglenn.html:VIS  ASSERTS  bundl | programs=Xcel
Energy,Xcel's income-qualified programs | Northglenn's Xcel Energy
service-territory status means full access to the 2026 Xcel rebate programs —
the standard Insulation and Air Sealing Rebate, the W  [ASSERTS]`

One is a weak match — the `bundl` token binds to unrelated prose:
`public/air-sealing.html:VIS  ASSERTS  bundl | programs=Whole Home Efficiency
Bonus,Xcel Whole Home Efficiency Bonus | Cost drivers: home size (linear with
conditioned volume), pre-existing leak severity (a 15 ACH50 home requires more
sealing labor than a 7 A  [ASSERTS]`

LGM and GCI adjudicate 0 with 299 and 70 raw — everything filtered away.

**Verdict on R4: USABLE AS-IS FOR ASSERTIONS (0% FP), BUT IT MISSES DENIALS AND
SINGLE-PROGRAM CLAIMS — the three hardest cases in the replay (§4.7).** Keep it
blocking; its precision is the best in the gate. Its recall is the worst.

**Recommended tightening:** (1) add a single-program stacking-claim class, so
`Xcel rebate-stack eligibility` and `the primary rebate stack` fail on one
recognised program plus a stacking noun — that one change catches the
`llms.txt` defect and would have enumerated `fca41f6`'s 70-page boilerplate.
(2) Match program names longest-first so adding bare `"Xcel"` does not let
`"Xcel Energy"` self-satisfy the two-program test by substring overlap.
(3) Alias informal program references (`the Atmos rebate` → Atmos Energy;
`the free state weatherization program` → Colorado Weatherization Assistance
Program; `either insulation rebate program` → the program set). (4) Carry
program context across a sentence boundary within one block, and treat a
schema.org `Question` + `acceptedAnswer` pair as a single unit, so a token in
the question can bind a predicate in the answer. (5) Extend `denial_markers` to
argumentative denial (`not in the way people usually hope`, `from opposite
directions`, `helps with scheduling, not with`).

### 3.6 R5 UNCITED STATISTIC — 213 / 36 / 35. THE BEST RULE IN THE GATE.

**DCI's 213 is not 213 defects. It is two sentences, 166 times.** Exact figure
tally, summing to 213:
`25%`×92, `20%`×72, `60-70%`×10, `10-20%`×8, `15-30%`×7, `17%`×5, `12-22%`×5,
`3x`×4, `20%,25%`×2, `20-35%`×2, `15%`×2, `10-15%`×2, `60-80%`×1, `3x,60-70%`×1.

Surfaces: VIS 144, LOWVIS 38, LD 22, LLMS 4, JS 2, TW 1, OG 1, META 1.

TRUE — 184. Two dominant classes, each one sentence repeated across pages and
surfaces:
- **72+2 × the Xcel 20% CFM50 blower-door requirement.** 52 of them are one
  sentence: `public/insulation-arvada.html:VIS  mag  20% | Work must be
  completed by a participating contractor, with a blower door test before and
  after documenting a reduction of at least 20% in CFM50.  [uncited]`
- **92 × the Xcel 25% Whole Home Efficiency Bonus.** 33 of them are one
  sentence: `Xcel Whole Home Efficiency (WHE) Bonus — adds a 25% bonus on all
  standard rebates when three qualifying measures are completed within two
  years of enrolling.  [uncited]`
- **18 × the site's own energy-savings percentages**, the exact class R1 found
  live: `An attic upgrade from R-11 up to code typically cuts heating and
  cooling costs 12-22%; Xcel rebates are capped per measure.  [uncited]`
  `Air sealing typically delivers 10-15% bill reduction even on homes that
  already have adequate insulation.  [uncited]`
  `Insulation cuts heating and cooling loads 15-30%, leaving the old furnace
  oversized.  [uncited]`
  `Whole-home efficiency packages (insulation + air sealing + duct sealing)
  typically reach 20-35%.  [uncited]`
  and the two KNOWN-OPEN rows carried with provenance, never suppressed:
  `public/do-i-need-new-insulation-quiz.html:JS  mag  15% | Most homes with this
  profile see comfort improvement plus 15% reduction in heating and cooling
  costs after upgrading.  [KNOWN-OPEN OPEN — flagged to the Director 2026-09-11
  in lane dci-d3-tier-label-fix]`

The gate's own R11 rows corroborate the debt independently:
`note: WHE 25% bonus  measured 42/1/42/1` (42 asserting, 1 attributed, 42
unattributed) and `note: CFM 50 20% reduction  measured 36/10/34/8`.

REVIEW — 21. Cost-ratio and material-property claims where a registry source
exists but is not on the page, several of which are explicitly honest about
sourcing:
`No primary source publishes a Denver-specific installed cost per square foot
for hybrid — it costs roughly 60-70% of full closed-cell foam, and more than
blown-in cellulose.  [uncited]`
`Old loose-fill cellulose typically settles 10-20% over the life of the home,
losing thermal performance even at the same depth.  [uncited]`
`TL;DR Spray foam costs 2-3x what blown-in costs…  [uncited]`

FP — 8, in two classes:
- 5 × a derivable physical constant. Barometric pressure at 5,280 ft is ~83% of
  sea level; demanding a publisher for it is like citing the boiling point of
  water: `Atmospheric pressure at Denver's elevation is roughly 17% lower than
  sea level, which slightly reduces the stack-effect pressure differential…`
- 3 × **block-boundary failure**: the sentence splitter did not segment, so the
  excerpt is a navigation strip and the finding is unadjudicable from the report
  even though a real figure sits somewhere in the block:
  `public/insulation-spray-foam.html:VIS  mag  3x | Quiz Energy Savings &
  Payback Spray Foam vs Blown-In Comparator Resources Service Areas Lakewood
  Arvada Aurora Wheat Ridge Centennial Englewood Littleton Westminster Thornton
  Park Hill Washington Park Highland Golde  [uncited]`
  A fourth of this shape carries a real claim in a form-control label and is
  scored TRUE:
  `public/xcel-rebate-eligibility-checker.html:VIS  mag  25% | Yes No Not sure
  Three or more measures qualify for the Whole Home Efficiency Bonus (25% on all
  standard rebates, within two years of enrolling).  [uncited]`

**LGM R5 — 36: 22 TRUE, 11 REVIEW, 3 FP.** TRUE: 22 × the 20% CFM50 gate, 14 of
them one sentence: `Requires a participating contractor and, unless a first
blower door test already finds the home tight enough by Xcel's own measure, a
documented 20% reduction in CFM50.` REVIEW: 11 × cellulose settling 10-20%.
FP: 3 — the Census ACS statistic, **attributed inside its own sentence**, where
the flagged token `0%` is a parse artifact of `46.0%`:
`The median Louisville home was built around 1991, and close to half of
Louisville housing units (46.0%) predate 1990 (Census Bureau American Community
Survey 5-year estimates, 2020-2024)…  [uncited]`

**GCI R5 — 35: 26 TRUE, 8 REVIEW, 1 FP.** TRUE: 22 × the 20% CFM50/CFM25
blower-door requirement (`Air sealing is a separate measure and requires a
blower door test showing at least a 20% reduction in leakage.`) plus 4 × Atmos
rebate *rate* percentages (`why Atmos rebates rim joist work at 50% rather than
75%`; `Wall, crawlspace or basement, and floor insulation are each rebated at
75% as well`). REVIEW: 8 — the 40% R-per-inch comparison (derivable from 3.5 vs
2.5) and cellulose settling. FP: 1 — a Census statistic where `8%` is a parse
artifact of `14.8%`.

**Verdict on R5: USABLE AS-IS. Keep it blocking.** 2.9–8.3% FP off DCI, 3.8% on
DCI. It is the only rule that both found the live defects R1 identified and
holds a defensible precision. Its problem is **multiplicity, not noise**: 78%
of DCI's 213 are two sentences.

**Recommended tightening (a reporting change, not a detection change):** group
findings by normalised claim sentence and report `N occurrences across M files`
with one verbatim exemplar, so 213 rows become ~85 classes and a reader can act.
Also add a derivable-constant allowlist keyed to `elevation_anchor`, treat an
in-sentence parenthetical citation (`(Census Bureau American Community Survey…)`)
as attribution, and suppress a hit whose resolved block spans a `<nav>` boundary
rather than reporting an unadjudicable excerpt.

### 3.7 R6, R7, R9, R10, R11

**R6 — 0 / 0 / 0 at HEAD.** DCI reports
`RAW 0 label-emitting conditional chains examined`. **That caption is wrong.**
`emit_rule` prints `len(res.raw)` — the HIT count — under a caption that says
*chains examined*. `RAW 0` at HEAD means zero hits, i.e. the rule ran and
passed; it does not mean nothing was examined. On the pre-fix tree the same
field read 15. The mislabel invites exactly the misreading it must not. LGM and
GCI print the honest form: `note: NULL RESULT -- 0 label chains configured for
this property.` **Verdict: R6's static half is excellent (§4.6) and 0% FP.
Fix the caption. Do not ship R6b as an opt-in that forces exit 2.**

**R7 — 2 / 0 / 0 on DCI.** Both rows examined:
`public/solar-gain-altitude-denver.html:TXT  A  NREL | …NREL's solar resource
data puts the Denver area among the strongest solar markets of any m
[identifier]` — REVIEW. `NREL` is on `common.json`'s `superseded_identifiers`
with `current_replacements: {"nrel.gov": "nlr.gov"}`. NREL is a live
institution and `nlr.gov` is the National Labor Relations Board. **That config
entry looks like a typo and should be re-examined** — the finding is
true-per-config and questionable on the facts.
`public/vermiculite-removal-cost-denver.html:VIS  B  air_sealing_is_a_prerequisite
| Related guides Related services and tools Vermiculite Identification Guide
prerequisite step — identify before anything else…` — FP. An unrelated sense of
"prerequisite" inside a related-guides navigation block.
**Verdict: R7's proposition half (B) is the highest-value half in the gate — it
caught both retired-eligibility defects (§4.3) and is the only thing that can,
since the cited URL is valid and only the claim is stale. Keep blocking.**
Tighten by requiring the proposition's terms to co-occur in a prose sentence
rather than a link-list block.

**R8 — 77 / 161 / 38. 0% FP on all three. The most reliable rule in the gate.**

*DCI's 77 against 75 html pages — the extra surfaces established.*
77 = 71 `[stale-vs-content]` (one per page, VIS) + 5 `[precedes-creation]` +
1 `[surfaces-disagree]`, across **72 distinct files**. Only two files appear more
than once, and those are the extra surfaces:
`public/ice-dams-denver.html` ×5 — one `[stale-vs-content]` plus **four**
`[precedes-creation]` rows, one per date surface:
```
public/ice-dams-denver.html:footer_text     a  footer_text = 2026-05-05 precedes first appearance in git (2026-06-10)  [precedes-creation]
public/ice-dams-denver.html:ld:dateModified a  ld:dateModified = 2026-05-05 precedes first appearance in git (2026-06-10)  [precedes-creation]
public/ice-dams-denver.html:sitemap:lastmod a  sitemap:lastmod = 2026-05-05 precedes first appearance in git (2026-06-10)  [precedes-creation]
public/ice-dams-denver.html:time[datetime]  a  time[datetime] = 2026-05-05 precedes first appearance in git (2026-06-10)  [precedes-creation]
```
`public/r-value-needed-calculator-embed-code.html` ×2:
```
public/r-value-needed-calculator-embed-code.html:sitemap:lastmod  a  sitemap:lastmod = 2026-08-24 precedes first appearance in git (2026-09-10)  [precedes-creation]
public/r-value-needed-calculator-embed-code.html:VIS  c  date surfaces disagree: footer_text=2026-09-10; sitemap:lastmod=2026-08-24; time[datetime]=2026-09-10  [surfaces-disagree]
```
So the answer is: **per-surface multiplicity on two pages that carry genuinely
impossible dates, not 77 separate pages.** Three html pages produce no R8 row —
`404.html`, `privacy.html`, `r-value-needed-calculator-embed.html` — the last
correctly, since the embed frame carries no review date.

**This is also a LIVE defect the gate is reporting at HEAD.** 2026-08-24 →
2026-09-10 is exactly **17 days** (`python3 … (date(2026,9,10)-date(2026,8,24)).days` → `17`),
the signature of defect 9a — and the crawler-facing `sitemap:lastmod` is still
wrong at HEAD while the footer was corrected. That is defect 9b's class, live on
DCI. `ice-dams-denver.html`'s 2026-05-05 predates the repo's first commit by 36
days, on all four surfaces.

*LGM's 161 against 48 pages — per-surface multiplicity, and the dates are
genuinely impossible.*
161 = 113 `[precedes-creation]` + 46 `[stale-vs-content]` + 2
`[surfaces-disagree]`, across **46 distinct files**. The 113 are 4 date surfaces
× ~29 pages: `time[datetime]` 29, `footer_text` 29, `sitemap:lastmod` 28,
`ld:dateModified` 27. Claimed-vs-git pairs:
`107 × claimed=2026-08-05 git_first=2026-08-11`,
`4 × claimed=2026-08-05 git_first=2026-08-12`,
`2 × claimed=2026-08-07 git_first=2026-08-11`.

The gate hedges part (a) with
`on a ported property part (a) is a FLOOR and a hit can mean the port post-dates
the content's real authoring date rather than that the date is invented`.
**I tested that hedge and it does not apply to LGM.** LGM was not ported — it
was built from scratch:
```
$ git -C .../longmontcoloradoinsulation.com log --reverse --format='%h %ad %s' --date=short | head -3
5b50dbd 2026-08-11 .gitignore — first commit, before any source
f9b5fc2 2026-08-11 Genesis Phase One: scaffold, ACS data, architecture spec. No rendered copy.
7a36d3a 2026-08-11 Content wave, Phase One: first exemplars (Longmont area page, attic service)
$ git -C ... log --reverse --format='%h %ad %s' --date=short -- public/ | head -1
7a36d3a 2026-08-11 Content wave, Phase One: first exemplars
```
First commit **and** first `public/` commit are both 2026-08-11, and the second
commit says "No rendered copy". So a page claiming review on **2026-08-05**
claims review six days before the repository existed. That date is not a port
artifact — it is invented. All 113 are TRUE.
The 2 `[surfaces-disagree]` rows are the GCI `contact.html` defect class live on
LGM:
`public/about.html:VIS  c  date surfaces disagree: footer_text=2026-08-05;
sitemap:lastmod=2026-08-07; time[datetime]=2026-08-05  [surfaces-disagree]`
`public/contact.html:VIS  c  date surfaces disagree: footer_text=2026-08-05;
sitemap:lastmod=2026-08-07; time[datetime]=2026-08-05  [surfaces-disagree]`
Staleness: review 2026-08-05 → content 2026-09-10 = **36 days**.

*GCI's 38*: 35 `[stale-vs-content]` + 2 `[precedes-creation]` + 1
`[surfaces-disagree]`, across 36 files. All TRUE.

**Verdict on R8: USABLE AS-IS, keep blocking, 0% FP on 276 findings.** Its only
problem is multiplicity. **Recommended tightening (reporting only):** collapse
the per-surface rows into one row per page listing the disagreeing surfaces, and
report the `[stale-vs-content]` class once with a page count, since it is a
single known-open debt (`DCI-D-003`) and not 71 findings.

**R9 — 57 / 0 / 0 on DCI. 0% FP.** Class tally: 49
`[NO AUTHORITATIVE VALUE IN CONFIG]`, 6 `[authoritative=airsealing_only]`, 1
`[authoritative=not_required]`, 1 `[N3-unverifiable]`. Subjects: 30
`vermiculite_test_trigger`, 19 `pre1990_attic_rvalue`, 6 `xcel_cfm50_scope`,
1 `whe_audit_precondition`. All real contradictions — two values coexist on the
property. The most substantive, because the config *does* know which side is
right:
`public/insulation-blower-door-test.html:VIS  N1  xcel_cfm50_scope: 2 values
['airsealing_only', 'insulation_and_airsealing'] | insulation_and_airsealing |
sub-tests N1+N2 | Xcel's insulation and air sealing rebates require a documented
reduction of at least 20% in CFM5  [authoritative=airsealing_only]`
— the site over-applies the blower-door gate to the *insulation* rebate; the
authoritative scope is air sealing only. That is a live substantive defect,
reported on 6 surfaces including `llms.txt`.
And the retired-prerequisite class, still on one surface:
`whe_audit_precondition: 2 values ['not_required', 'required']`.
The `pre1990_attic_rvalue` contradiction is real and visible:
`r11_r19` on 17 surfaces vs `r11_r30` on 2
(`public/insulation-attic.html:VIS … Most pre-1990 Denver-metro homes have R-11
to R-30 attic insulation`).
The one REVIEW is not a catch but a declaration of inability:
`public/r-value-needed-calculator.html:JS  N3  tool payload field(s)
['lf-calc-inputs', 'lf-calc-output'] not found in the page; visible/hidden
agreement cannot be established  [N3-unverifiable]`
**Verdict: USABLE, keep blocking — but see §4.10. R9 is a registry of
pre-registered contested subjects, so its recall is exactly its config. It
missed the hidden-field defect entirely.** Tighten by making N3 actually
*compare* the hidden payload to the visible output rather than only checking the
field's presence.

**R10 — 0 / 0 / 2. GCI's 2 are both FP.**
```
public/knob-and-tube-insulation-greeley.html:CITE  anchor  dest=/insulation-attic-greeley.html | destination-has-no-figure | Atmos Energy rebates residential attic insulation at 75% of total cost where the starting R-value is less than R-20, and publishes the amount that rebate  [destination-has-no-figure]
public/knob-and-tube-insulation-greeley.html:VIS   anchor  dest=/insulation-attic-greeley.html | destination-has-no-figure | According to Atmos Energy , Atmos Energy rebates residential attic insulation at 75% of total cost where the starting R-value is less than R-20, and publi  [destination-has-no-figure]
```
I checked the destination. It **does** refuse in words — the refusal wording is
simply not in the config:
```
$ /usr/bin/grep -o "publishes[^<.]\{0,120\}" .../public/insulation-attic-greeley.html
publishes its own insulation and air sealing rebate terms
publishes the amount
publishes the current amount on its own rebate page
publishes a Greeley-specific installed price per square foot, and this site is not going to invent one
$ /usr/bin/grep -oIE '\$[0-9][0-9,.]*' .../public/insulation-attic-greeley.html | wc -l
       0
```
This is the rule's own declared, deliberate bias:
`note: deliberate bias: a destination that refuses in words the config does not
know looks like a destination with no figures, which is still a FAIL -- the
failure mode is a false positive, not a false negative (spec R10)`.
**Verdict: USABLE, keep blocking — the bias is the right one and the volume is
2.** Tighten by adding `publishes the current amount on its own rebate page` and
`publishes the amount` to `refusal_markers`.

**R11 — 5 rows / 0 / 0. REPORT-ONLY, never changes the exit code. All 5 TRUE
and independently valuable.** R11 is the only rule that measures the *unattributed*
set with its own query instead of by subtraction, and it proves why that matters:
```
note: $600 Combo Bonus  measured 74/0/74/0  baseline 72/0/72/0  delta +2/+0/+2/+0
note:   naive subtraction (asserting - attributed) = 74; measured unattributed = 74 — subtraction would coincide here; not used
note: participating-contractor rule  measured 74/23/74/23  baseline 72/23/72/23  delta +2/+0/+2/+0
note:   naive subtraction (asserting - attributed) = 51; measured unattributed = 74 — SUBTRACTION WOULD HAVE BEEN WRONG
note: WHE 25% bonus  measured 42/1/42/1  baseline 42/1/42/1  delta +0/+0/+0/+0
note:   naive subtraction (asserting - attributed) = 41; measured unattributed = 42 — SUBTRACTION WOULD HAVE BEEN WRONG
note: CFM 50 20% reduction  measured 36/10/34/8  baseline 36/10/34/8  delta +0/+0/+0/+0
note:   naive subtraction (asserting - attributed) = 26; measured unattributed = 34 — SUBTRACTION WOULD HAVE BEEN WRONG
note: by-check payment method  measured 47/0/47/0  baseline 46/1/46/1  delta +1/-1/+1/-1
```
Three of five rows would have been wrong under subtraction. **R11 is configured
on DCI only** — LGM and GCI report `0 tracked terms configured … reported as a
null result, NOT as PASS`, which is the honest form. Porting it is a config
entry.

### 3.8 The overall usability verdict

| rule | verdict |
|---|---|
| R1 | **REPORT-ONLY until the provenance block lands.** Cannot tell an accurate quotation from a fabricated one. |
| R2 | **REPORT-ONLY. Too noisy to block on** — 79–100% FP, zero true positives anywhere. Must be fixed, not deleted: it is load-bearing for a real class. |
| R3 | **T1 + T3 blocking; T2 REPORT-ONLY.** T1 is exact. T2 is necessary and currently cannot tell a rebate from a ZIP code. |
| R4 | **Blocking. Best precision in the gate (0% FP), worst recall.** |
| R5 | **Blocking, usable as-is.** Needs class-grouped reporting, not tighter detection. |
| R6 | **Static half blocking and excellent. Fix the RAW caption. Remove `--opt-in=R6b` until implemented** — it forces exit 2 on any repo. |
| R7 | **Blocking. Half B is the highest-value half in the gate.** |
| R8 | **Blocking, 0% FP on 276 findings.** Collapse per-surface multiplicity in the report. |
| R9 | **Blocking, 0% FP — but recall equals its config.** |
| R10 | **Blocking. Bias is correct, volume is 2.** |
| R11 | **Keep report-only. Port to LGM and GCI.** |

The pattern is consistent and worth stating plainly: **the rules that resolve a
claim against a recorded authoritative value (R7, R8, R9, R6-static, R10) are
precise and usable. The rules that match a string against a list and then scope
it by page (R2, R3-T2) are noise.**

---

## 4. PART 4 — THE SCORE

Method: for each known defect, a worktree in `/tmp/claim-gate-scratch/r3/wt` at
the commit immediately before the fix, `CANON_ROOT` at canon HEAD `7a091a0`, and
`--today` set to the fixing commit's date (the fair test: judging a tree by facts
from its own day, not from a week in its future). The gate wrapper
`ops/claim_gate.sh` was added on 2026-09-17 and does not exist in the historical
trees, so `claim_gate.py` was invoked directly with `--config` and `--repo` —
that is a decision I made and record here.

**Read this table with §0 in hand.** Every DCI row is a RULE-LEVEL verdict: the
shipped gate exits 2 on all of them.

| # | defect | repo | fixing commit | pre-fix SHA | rule | result | gate's own output line |
|---|---|---|---|---|---|---|---|
| 1 | Fabricated quotation (11 pages) | LGM | `186d311` | `8b0f1a9` | R1 | **CAUGHT** | `public/index.html:CITE A XCEL_BLOWER_DOOR According to Xcel Energy , “Xcel's insulation and air sealing rebates require a documented reduction of at least 20% in CFM50 … verified by a blower door test before` |
| 2a | Wrong utility, prose (35 pages) | GCI | `e6cb44e` | `e912eee` | R2 | **CAUGHT** | `public/insulation-severance.html:VIS a Atmos Energy \| scope=Severance \| (3) Rebate handling — ask who files the Atmos paperwork and confirm it goes in within 60 days of the install. [utility-not-serving-town]` |
| 2b | Wrong utility, `og:image` | GCI | `e6cb44e` | `e912eee` | R2 | **MISSED** | no R2 hit on `og-image.svg`; `grep -c 'scope=sitewide'` → 0 against control 97 `scope=` |
| 3a | Retired eligibility rule, live citation (Lafayette) | LGM | `72e18ac` | `a2ba5a6` | R7 | **CAUGHT** | `public/insulation-lafayette.html:VIS B whe_audit_entry_path_begin_with \| Xcel's own rebate summary sets three conditions on it: begin with a blower door audit, an infrared audit, or a Home Energy Squad Plus visit…` |
| 3b | Retired eligibility rule, `prerequisite` class | DCI | `eb5c939` | `130921c` | R7 | **CAUGHT** (rule-level) | `public/insulation-energy-audit.html:VIS B air_sealing_is_a_prerequisite \| The Xcel-approved energy audit is a prerequisite for the Xcel Whole Home Efficiency Bonus…` |
| 4a | Invented pathways, long form (38 pages) | DCI | `b47a3c2` | `f08bb9f` | R7 | **CAUGHT** (rule-level) | `public/air-sealing.html:VIS B installed_and_invoiced_by_dec_31_2026 \| The Xcel $600 Insulation + Air Sealing Combo Bonus applies when paired with a qualifying heat pump installed and invoiced by December 31, 2026.` |
| 4b | Short form `Dec. 31, 2026` at `_generate_calculator_pages.py:344` | DCI | `f83d421` | `2a59a97` | R7/R5 | **MISSED** | absent from R7 RAW (4 hits, all other claim ids) and from R5's 213; appears only in an R3 row flagged for `$600` |
| 4c | The fifth Xcel program itself (4 invented pathways) | DCI | `b47a3c2` | `f08bb9f` | none | **MISSED** | `forbidden_program_names` is dead config: `grep -n "forbidden_program_names" claim_gate.py` → no output |
| 5a | 198 rebate dollar figures | DCI | `5703f8c` | `169bb3c` | R3 | **CAUGHT** (rule-level) | `note: T1 $-anchored 198` — exact match to the human sweep; `public/air-sealing.html:RAW T1 $600 \| …The Xcel $600 Insulation + Air Sealing Combo Bonus…` |
| 5b | 133 rebate dollar figures | LGM | `d6e8dab` | `604d052` | R3 | **PARTIAL — 18 of 133** | 103 removed: `[cost_context_markers (Ruling 2 -- costs, not payouts)] … “Efficiency Works pays $1.16 per square foot…  [$1.16]` ×65 |
| 5c | 206 rebate dollar figures | GCI | `2cecf33` | `236c464` | R3 | **CAUGHT** | `note: T1 $-anchored 206` — exact match to the release note |
| 5d | Bare-digit cap `1550 / 0.75` in a JS comment | GCI | `f0203ad` | `e994484` | R3 T2 | **CAUGHT** | `public/insulation-cost-calculator-greeley.html:JS T2 1550 \| … // CAP/RATE (1550 / 0.75) and money() were DELETED 2026-09-08 …  [1550]`, with `note: T1 $-anchored 0` |
| 6 | Self-contradicting calculator | DCI | `37c7b29` | `58c44eb` | R6 static | **CAUGHT** (rule-level) | `_generate_calculator_pages.py:JS G1 branch reads {gap} while the printed string interpolates {pctShort} \| Moderately under code — % short of target.  [G1]` |
| 7a | Stacking, class left on 70 of 72 pages | DCI | `fca41f6` | `bcb64a3` | R4 | **CAUGHT** | `VERDICT FAIL — 94 adjudicated finding(s)`, `ASSERTS 92 · DENIES 2` |
| 7b | Stacking | DCI | `31484f1` | `dd88de3` | R4 | **CAUGHT** | `VERDICT FAIL — 27 adjudicated finding(s)`, `ASSERTS 25 · DENIES 2` |
| 7c | Stacking | DCI | `5350403` | `b5635c9` | R4 | **CAUGHT** | `VERDICT FAIL — 33 adjudicated finding(s)`, `ASSERTS 31 · DENIES 2` |
| 7d | Stacking DENIAL as schema.org FAQPage | GCI | `f0203ad` | `e994484` | R4 | **MISSED** | `[NEUTRAL -- fewer than two distinct programs, or no predicate] public/insulation-rebate-hub.html:LD NEUTRAL stack \| programs=- \| Can I stack these programs?  [NEUTRAL]`, with `DENIES 0` |
| 7e | Affirmative stacking denial, knob-and-tube | LGM | `58646f0` | `2563a56` | R4 | **MISSED** | `[NEUTRAL -- fewer than two distinct programs, or no predicate] public/knob-and-tube-insulation-longmont.html:VIS NEUTRAL bundl,stack,stacking \| programs=- \| Bundling the timing helps with scheduling, not with rebate stacking…  [NEUTRAL]` |
| 7f | `llms.txt` "Xcel rebate-stack eligibility" | DCI | `fb08735` | `d1b6078` | R4 | **MISSED** | `rebate-stack` appears 0 times in the whole report; classified `NEUTRAL … programs=['Whole Home Efficiency Bonus'] distinct=1` and filtered |
| 8 | Uncited `25-40%` on 16 pages | DCI | `147185c` | `4cf7a52` | R5 | **PARTIAL — 14 of 16 pages** | `public/index.html:VIS mag 25-40%,40% \| After the 2026 Xcel rebate stack …, net cost typically drops 25-40%…  [uncited]` |
| 9a | Review date 17 days before the page existed | DCI | `92f3887` | `539670e` | R8 | **CAUGHT** (rule-level) | `public/r-value-needed-calculator-embed-code.html:time[datetime] a time[datetime] = 2026-08-24 precedes first appearance in git (2026-09-10)  [precedes-creation]` |
| 9b | `contact.html`, two dates 33 days apart, crawler-facing one false | GCI | `348baf9` | `12dfcbf` | R8 | **CAUGHT** | `public/contact.html:VIS c date surfaces disagree: footer_text=2026-09-09; sitemap:lastmod=2026-08-07; time[datetime]=2026-09-09  [surfaces-disagree]` |
| 10 | Hidden `calc_output` transmitted "already at code" | DCI | `81f4bca` | `cb675ab` | R9 | **MISSED** | only `public/r-value-needed-calculator.html:JS N3 tool payload field(s) … not found in the page; visible/hidden agreement cannot be established  [N3-unverifiable]` — a declaration of inability, not a catch |
| 11 | Dangling promise, "The Atmos figures quoted elsewhere" | GCI | `f0203ad` | `e994484` | R10 | **CAUGHT — FAIL, not REVIEW** | `public/insulation-johnstown.html:VIS anchor dest=/insulation-johnstown.html \| destination-has-no-figure \| The Atmos figures quoted elsewhere on this site are for the towns Atmos serves and do not apply to a Johnstown home.` |
| 12 | Embed frame / `llms.txt` corpus hole | DCI | `92f3887` | `539670e` | corpus | **CAUGHT** | `embed frame: public/r-value-needed-calculator-embed.html, public/r-value-needed-calculator-embed-code.html`; `public/r-value-needed-calculator-embed.html:JS mag 15% \| …15% reduction in heating and cooling costs…`; R4 ×2 on the frame |

### **HEADLINE: 16 of 25 replayed defect instances CAUGHT outright. 2 PARTIAL. 7 MISSED.**

Rolled up to the 12 named defect classes: **6 fully caught** (1 fabricated
quotation, 3 retired eligibility, 6 self-contradicting calculator, 9 stale review
date, 11 dangling promise, 12 corpus hole), **5 partially caught** (2 wrong
utility, 4 invented pathways, 5 rebate figures, 7 stacking, 8 uncited statistic),
**1 missed entirely** (10 internal contradiction).

**And the central case is caught.** LGM's fabricated Xcel quotation — the
paraphrase inside curly quotation marks presented as Xcel's own words, where
"before and after" occurs zero times in the cited source — appears as **exactly
11 adjudicated `XCEL_BLOWER_DOOR` rows on 11 pages**: `air-sealing-longmont`,
`attic-insulation-cost-calculator-longmont`, `index`, `insulation-attic-longmont`,
`insulation-basement-longmont`, `insulation-cathedral-ceiling-longmont`,
`insulation-crawl-space-longmont`, `insulation-energy-audit-longmont`,
`insulation-fiberglass-batt-longmont`, `insulation-hybrid-flash-batt-longmont`,
`insulation-wall-longmont`. I measured the phrase myself in the pre-fix tree:
18 occurrences across 12 files, control `Longmont` = 2340.

But the mechanism must be stated precisely, because it bears on whether anyone
should trust it: **R1 caught it because the registry's `quote` field is ABSENT for
`XCEL_BLOWER_DOOR`, and R1 in DEGRADED mode flags every registry-backed
quotation whose field is absent.** It did not verify the phrase against the
source. Its own blind-spot line says so: *"this rule cannot read the cited PDF.
It asserts the PRESENCE and SHAPE of a provenance record, not the accuracy of the
quote."* It flagged all 122 attributed quotations on that tree, and the
fabrication was one of them. That is a real catch and it would have blocked the
release. It is not discrimination.

### 4.1 Every MISS, with the diagnosis. This list is what R4 and the next pass work from.

**MISS 1 — 2b, the `og:image` wrong-utility claim (GCI).** *Rule-design gap, not
a corpus gap and not the raster hole.* `public/og-image.svg` **is** in the read
set (`read set: 44 artifacts (… 3 svg)`, and R3 quotes its footer text back:
`fill="#5a7a6e">Atmos rebates explained · Local contractors · Existing-home
retrofits</tex`). The asset is referenced from 37 pages and `gci.json` itself
calls it "a territorial claim surface". R2 still cannot fire: `rule_R2` computes
`scope = ctx.town_scope(art)` then `allowed = ctx.allowed_utilities(scope)`,
which returns `None` for an empty scope (`claim_gate.py:655-656`), and the hit
loop does `if allowed is None or u in allowed: continue`. **An artifact with no
town scope produces zero R2 hits by construction.** Empirically: zero
`scope=sitewide` hits anywhere in the run, against a control of 97 `scope=`
lines. *Fix direction:* give sitewide artifacts the union of all configured
towns as scope, so a single-utility territorial claim on a sitewide asset fails.

**MISS 2 — 4b, the short form `Dec. 31, 2026`.** *Two independent causes, both
confirmed.* (a) **The sentence splitter cannot see across an abbreviation
period.** `surfaces.py:73` is `_SENT = re.compile(r"(?<=[.!?…])\s+")`, so the
pooled sentence *ends* at "Dec." — probed directly: `[VIS|txt] '… installed and
invoiced by Dec.'`, `does any sentence contain 'invoiced by Dec. 31, 2026'?
False`, while `raw file contains it? True   txt contains it? True`, control
`sentences containing 'Denver'? 33`. `common.json` currently ships two R7
patterns containing "Dec." that **can never fire**. (b) **`SRC over the
generators` is advertised but not implemented.** `surfaces.py:643` writes
`facts.src_text[name]`; `grep -n "src_text" claim_gate.py surfaces.py` shows it
is **read nowhere**. `rule_R7` never references `ctx.gen`. So
`_generate_calculator_pages.py:344` is structurally outside the claim corpus,
and the report's own header and per-rule `surfaces:` lines **overstate the
corpus**. This is the single change that would have caught it. *This is the exact
trap the original defect describes — searching the long form — reproduced inside
the gate at a different layer.*

**MISS 3 — 4c, the invented fifth program.** *Dead config; no rule tests it.*
`dci.json` carries `forbidden_program_names: ["Xcel IQ Program", "IQ Program",
"Xcel IQ"]` with full provenance, and `grep -n "forbidden_program_names"
claim_gate.py` returns nothing (control: `non_territorial_programs` is read at
`:668` and `:1064`). The string occurs 261 times in the pre-fix report, always
incidentally inside another rule's excerpt. *Fix direction:* wire
`forbidden_program_names` into R2 or a new rule.

**MISS 4 — 7d, the FAQPage stacking denial (GCI).** *Pattern too narrow,
finished by the `NEUTRAL` filter.* Two compounding causes, both measured. (a)
R4 is TXT sentence-split; the stacking token is in the FAQ **question** and the
denial plus the programs are in the **answer**. All 19 `stacking_tokens` tested
against the answer text return **0** (control `Atmos` → 2), so the answer is
never scanned. The denial is phrased `"Not in the way people usually hope"` plus
an argument from `"opposite directions"`, which no configured predicate matches.
(b) The question names no configured program — the page says `"the free state
weatherization program"` and `"the Atmos rebate"`, while `R4.programs` requires
the literals `"Colorado Weatherization Assistance Program"` and `"Atmos
Energy"`. The `R4a` fixture passes only because it was written with the
configured literals and the predicate in one sentence: **the fixture proves the
LD plumbing, not the detection.**

**MISS 5 — 7e, the knob-and-tube stacking denial (LGM).** *Filter
over-removal on the `programs=-` leg.* The tokens all fired and the sentence
reached RAW on both surfaces; only the program-naming precondition failed,
because the sentence uses an **anaphoric** program reference — `"either
insulation rebate program"` in sentence 1, `"rebate stacking"` in sentence 3.
The full denial, verbatim from the pre-fix tree: *"Bundling the timing helps with
scheduling, not with rebate stacking — the rebate applies to the insulation
regardless of what came before it."* `stacking` occurs exactly **2 times
sitewide**, both on that page, both the defect, and R4 adjudicated 0 of them.
Normalisation control run: line-wrap-normalised counts identical to line-based,
so nothing was hiding across a break; `cannot be combined` and `may not be
combined` are genuinely 0 (control `Longmont` = 2340).

**MISS 6 — 7f, the `llms.txt` stacking claim (DCI). The most important miss,
because it is the one the corpus fix was supposed to close.** *The corpus hole
IS closed; the rule is what misses.* `public/llms.txt` is unambiguously in the
read set — `corpus: git ls-files public/ = 83   find public/ -type f = 83
AGREE`, `read set: … 2 txt`, R4's `surfaces:` carries `LLMS`, and the file
yields 5 R4 RAW hits and an adjudicated ASSERTS row on other trees. My
measurement: `/usr/bin/grep -o 'rebate-stack' …/public/llms.txt | wc -l` → **1**
(control `Denver` → 35), on line 11: `- [Attic Insulation](…): Attic insulation
basics, the 2021 IECC R-60 ceiling minimum for Climate Zone 5 (which covers
Denver), and Xcel rebate-stack eligibility for attic top-ups, including the
Whole Home Efficiency Bonus.` And `rebate-stack` was 1 occurrence in 1 file in
**every** tree replayed — five sweeps, ten adversarial reads, zero change.
Cause: `tokens=['stack']`, `programs=['Whole Home Efficiency Bonus']`,
`distinct=1` → NEUTRAL → filtered. **Bare `"Xcel"` is not in `R4.programs`** —
the list has `"Xcel Energy"`, `"Xcel Whole Home Efficiency Bonus"`, `"Xcel's
income-qualified programs"`, and the sentence says just `"Xcel rebate-stack
eligibility"`. Isolating the bullet perfectly still misses, so this is **not** a
sentence-splitting artifact. **Today's `dci.json` still omits bare `"Xcel"`, so
the gate as it stands would still miss this exact string.** Counterfactual
verified: adding bare `"Xcel"` flips it to ASSERTS — but `which_any` uses plain
substring matching, so `"Xcel Energy"` would then self-satisfy the two-program
test; the real fix is a single-program stacking class or longest-match-first.

**MISS 7 — 10, the hidden `calc_output` field (DCI).** *Nothing configured to
examine it, plus an unimplemented rule half. NOT a corpus miss and NOT a filter
miss (0 removed).* (a) The corpus **does** reach the hidden field's value — the
literal `'No project recommended — already at code.'` appears in the gate's own
JS corpus, surfacing as window context in two R3 removed hits (control: `Denver`
→ 1379 in the same report). R9's `surfaces:` line even declares `plus JS string
literals`. **The reach is there; R9 does not use it.** (b) R9's N3 is a
**presence check only** — `missing = [h for h in hidden if h not in art.ids]`
emits a hit only when a configured id is *absent*. There is no code path in R9
that compares the hidden payload to the visible output. Fields present → silent;
fields absent → "cannot be established". Either way the contradiction is
unreachable by construction. (c) **No contested subject covers the claim.**
`common.json` R9 registers eight subjects; none of their `extract` patterns
matches "already at code" / "meets the R-60 ceiling requirement" / the
R-49-vs-R-60 eave-allowance contradiction. R9's own blind spot says it: *"it is a
registry of known-contested subjects, not a semantic engine, so a contradiction
on a subject not in claim_subjects is invisible."* This is a pre-existing
configuration gap, **not** an anachronism.

**A correction to the brief's premise for defect 10, recorded rather than
scored silently.** At `cb675ab` both occurrences of "already at code" are source
*comments describing the already-fixed past*; `81f4bca`'s C3 is a dead-branch
removal, and the live falsehood was fixed on 2026-08-24. The defect is genuinely
live at `4cf7a52`, which was also replayed: R9 there produced 147 adjudicated
findings and **zero** mentioning `calc_output` or `N3`. **MISSED on both trees.**

### 4.2 Partial catches

**5b, LGM's 133 figures — R3 reached 4 of 12 distinct figures and 18 of 133
occurrences.** The counting reconciles three ways: `T1 $-anchored 141` = my
`/usr/bin/grep -oIE '\$[0-9][0-9,.]*' -r … | wc -l` → 141 = 133 removed + 8 kept.
TRUE and caught: `$310/$460/$620/$770` (Efficiency Works air-sealing tiers), 18
of 28 adjudicated, 10 wrongly removed. TRUE and **missed**: `$1.16` ×65 and
`$0.77` ×38 (Efficiency Works per-square-foot payout, all removed by
`cost_context_markers`), `$2,000` ×2 (Boulder County EnergySmart income-qualified
cap, removed by the income-eligibility filter). Correctly exempt: the 8
installed-cost JS-comment rates. Attribution is **not** a defence here — the
governing ruling in `d6e8dab` is explicit that the broad reading reached the
attributed, quote-marked Efficiency Works figures, and empirically every one went
to zero. Also 13 of the 49 adjudicated hits are false positives (the print code
`215` ×9, the phone number ×3, an SVG coordinate ×1).

**8, DCI's `25-40%` — R5 caught 14 of the 16 live pages.** 24 occurrences on 16
pages; 23 occurrences across 5 `.py` files. No anachronism: `known_uncited`
does not pre-seed `25-40%`, so this is genuine pattern detection. The two page
misses: `insulation-lakewood.html`, both rows removed by `recognised_publishers
named in the same sentence` because "Xcel Energy" is named as the *payer*; and
`air-sealing.html`, which **never entered R5 RAW** because R5 requires a word
from `magnitude_words` and that sentence's verbs are "covers" and "drops" with
the noun "net cost" — none on the list. Most of the 14 catches fired on the
incidental word "Efficiency" in "Whole Home Efficiency Bonus", not on a real
magnitude verb. **A rebate-share claim phrased with "covers"/"drops"/"brings
down" is invisible to R5.** Also recorded: `20-35%` was not fully removed by the
earlier sweep either — 2 occurrences survive at this SHA.

### 4.3 Defect 6 — which half caught it, and was static sufficient?

**The STATIC half alone caught it, and it was fully sufficient.** R6a produced
**15 adjudicated findings, 0 filtered**, across all three surfaces (generator
SRC + both emitted HTML pages). G1 names the exact defect — `branch reads {gap}
while the printed string interpolates {pctShort}` — and G2 independently names
the exact three areas the fixing commit names: `wall-existing` (R-13),
`crawl-encap` (R-15), `basement` (R-15), each as `threshold 20 on {gap} is
unreachable … while the printed quantity can reach 100`.

**R6b contributed nothing and cannot.** `--opt-in=R6b` does exactly one thing:
`canary+ R6b-G3  (opt-in, browser cross-product)  *** MISSED *** R6b requires a
Chrome binary this gate cannot assume (spec 6, 7.3); no browser, no outbound
requests` — which increments `pos_missed` and guarantees exit 2 on any repo,
clean or not. The R6 rule section is byte-identical with and without the flag.
The 140-combination cross-product and the 351 ordinal inversions were never
enumerated; static structural reasoning was enough.

Source of the contradiction, for the record: `_generate_calculator_pages.py`,
module constant `RVALUE_CORE_JS`, function `computeResult()`, pre-fix lines
`388: } else if (gap >= 20) {` / `390: headline = 'Significantly under code — ' +
pctShort + '% short of target.'`. The fix is `gap >= 20 → pctShort >= 50` and
`gap >= 8 → pctShort >= 20`.

### 4.4 Anachronism — where the config's knowledge of the answer affects a verdict

The configs were written from today's facts. Stated explicitly, per the brief,
rather than scored either way silently:

- **Defects 3a, 3b, 4a — the R7 catches are partly circular.** The
  `superseded_propositions` entries that caught them name the very commits being
  scored in their own `why` fields: `air_sealing_is_a_prerequisite` says *"LGM
  72e18ac; DCI eb5c939, 11 instances on 3 pages"*;
  `installed_and_invoiced_by_dec_31_2026` says *"the short form Dec. 31, 2026
  survived four further rounds because every sweep searched the long form"*.
  These verdicts prove the R7 **machinery** reaches the surfaces that mattered
  (TITLE/OG/TW as one string, LD `acceptedAnswer`, VIS) — real value — but they
  are **not** evidence of forward detection. One genuine mitigation:
  `whe_audit_entry_path_hes_plus` is sourced to `DCI b47a3c2`, a *different
  property and an earlier commit*, so had that DCI-derived entry existed on
  2026-09-07 it alone would have caught the Lafayette page. That is the Rule-8c
  gap the LGM commit message itself complains about.
- **Defect 2a — `gci.json` already encodes the post-fix truth.** It records
  Johnstown/Milliken/Severance as Xcel gas CONFIRMED, which is precisely the
  fact the pre-fix tree got wrong. R2's blind-spot line says it outright: *"it
  enforces the config's territory and cannot discover that a town's utility
  changed."* Worse, one `allowed_multi_utility_sentences` entry — `"Where Atmos
  Energy serves the home"` — **removed 6 genuine 2026-09-08 wrong-utility
  sentences** on the three Xcel towns, because today that lead-in is sanctioned
  hedging. They did not change the verdict (111 still stood) but on a smaller
  tree they could.
- **Defect 6 — `printed_var: "pctShort"` describes the POST-fix code.** A config
  written on 2026-09-10 would likely have said `printed_var: "gap"` and G1 would
  have been silent. **G1's catch is anachronism-dependent; G2's three-area
  finding is not** (the labels and targets are byte-identical across the fix).
- **Defect 5c — the `allowed_figures` filter** that removed 20 hits rests on a
  Director ruling dated after the tree being replayed. It does not change the
  verdict (117 ≫ 0), but the 117 is "117 under today's rulings".
- **Defect 8 — no anachronism.** `known_uncited` does not pre-seed `25-40%`.
- **Defect 7e, 7f — no anachronism.** Nothing in `legitimate_uses` or
  `programs` encodes the fixes, and bare `"Xcel"` is still absent today. Both
  misses are live rule defects.
- **Defect 10 — the R9 `tools` config is anachronistic in both directions** and
  flips the N3 result between trees. At `cb675ab` the ids are created at
  runtime, so `art.ids` cannot see them; at `4cf7a52` they were static markup.
  The `claim_subjects` gap, however, is pre-existing, not anachronistic.
- **Corpus floors.** `min_artifacts: 85` / `expected_html: 75` are absolute and
  measured at today's HEAD, so any historical replay needs a stated override.

---

## 5. THE THREE LIVE DEFECTS R1 FOUND

### (a) DCI's uncited `15% reduction in heating and cooling costs`

```
$ /usr/bin/grep -ro "Denver" .../public/ | wc -l                                      # control
    3154
$ /usr/bin/grep -ro "15% reduction in heating and cooling costs" .../public/ | wc -l
       2
$ /usr/bin/grep -rl "15% reduction in heating and cooling costs" .../public/
public/r-value-needed-calculator.html
public/do-i-need-new-insulation-quiz.html
$ /usr/bin/grep -ro "15% reduction" .../public/ | wc -l
       2
```
**R1's figure confirmed exactly: 2 occurrences, 1 per file, those two files, and
no other `15% reduction` anywhere.**

**The gate CATCHES it.** Both occurrences are adjudicated R5 findings, carried
with provenance and explicitly never suppressed
(`note: of the adjudicated hits, 2 are KNOWN-OPEN from config.known_uncited --
carried with provenance, NEVER suppressed (spec R5)`):
```
public/do-i-need-new-insulation-quiz.html:JS  mag  15% | Most homes with this profile see comfort improvement plus 15% reduction in heating and cooling costs after upgrading.  [KNOWN-OPEN OPEN — flagged to the Director 2026-09-11 in lane dci-d3-tier-label-fix]
public/r-value-needed-calculator.html:JS  mag  15% | Most homes at this level see noticeable comfort improvement and 15% reduction in heating and cooling costs from bringing this area up to code.  [KNOWN-OPEN OPEN — flagged to the Director 2026-09-11 in lane dci-d3-tier-label-fix]
```
One gap worth recording: a **third** occurrence exists on the embed frame
(`public/r-value-needed-calculator-embed.html`) and `R5.known_uncited` lists
`occurrences: 2` and only the two page files. The frame's copy is still caught on
its own merits, but the config **understates the count** by omitting the
off-property one.

### (b) DCI's `before and after the work` blower-door attribution

```
$ /usr/bin/grep -ro "before and after the work" .../public/ | wc -l
      21
$ /usr/bin/grep -rl "before and after the work" .../public/ | wc -l
      13
```
**R1's figure confirmed exactly: 21 occurrences / 13 files.** Per file:
`insulation-blower-door-test.html` 5; `xcel-insulation-rebate-guide-denver.html`
2; `insulation-rim-joist.html` 2; `insulation-dense-pack-cellulose.html` 2;
`air-sealing.html` 2; and 1 each in `whole-home-efficiency-bonus-stacking-denver`,
`spray-foam-insulation-cost-denver`, `insulation-thornton`,
`insulation-hybrid-flash-batt`, `insulation-golden`, `insulation-energy-audit`,
`insulation-crawl-space`, `insulation-aurora`.
Broader form `before and after`: 84 occurrences / 36 files.

**The gate catches it PARTIALLY, and the distinction matters.** DCI's instances
are **not the LGM defect**. On LGM the phrase sat inside curly quotation marks
attributed to Xcel; on DCI it is site-voice prose. Measured:
```
$ /usr/bin/grep -ro "According to Xcel" .../public/ | wc -l
       0
$ /usr/bin/grep -ro "&ldquo;" .../public/ | wc -l                  # curly quotes DO exist
      78
$ /usr/bin/grep -ro "According to" .../public/ | wc -l
     178
```
Normalised context sampling shows site-voice prose throughout, e.g.
`Xcel's insulation and air sealing rebates require a documented reduction of at
least 20% in CFM50, verified by a blower door test before and after the work —
the before test is never waived…` and `A blower door test before and after the
work is required, documenting at least a 20% reduction in CFM50.`

So: **R1 correctly does NOT fire** (there is no quotation to have fabricated).
**R5 DOES fire, blocking**, on the accompanying uncited 20% figure across ~74
surfaces. **R9 fires** on the deeper substantive error — the site applies the
blower-door gate to the *insulation* rebate when the authoritative scope is air
sealing only (`xcel_cfm50_scope … [authoritative=airsealing_only]`, 6 surfaces).
**R11 measures the debt** report-only: `CFM 50 20% reduction  measured
36/10/34/8` — 34 unattributed.
**What no rule catches** is the specific defect *"a claim sourced to a document
that does not contain the phrase."* R1 requires quotation marks and cannot read
the cited PDF; no rule compares a claim's text to its source's text. The class
LGM swept and DCI never received is therefore **detected obliquely (statistic +
contradiction) but not as an attribution defect.**

### (c) The review dates

```
$ /bin/ls .../denvercoloradoinsulation.com/public/*.html | wc -l
      75
$ /usr/bin/grep -o "<lastmod>[0-9-]*</lastmod>" .../public/sitemap.xml | sed 's/<[^>]*>//g' | sort | uniq -c | sort -rn
  70 2026-08-24
   1 2026-09-01
   1 2026-08-05
   1 2026-05-05
$ git -C ... log -1 --format='%h %ad %s' --date=short -- 'public/*.html'
37c7b29 2026-09-11 Select the r-value calculator's tier label by percentage, not absolute gap (D3)
```
**DCI: 70 of 75 confirmed at `2026-08-24`, against content corrected through
2026-09-11 — 18 days stale.**

```
$ /bin/ls .../longmontcoloradoinsulation.com/public/*.html | wc -l
      48
$ /usr/bin/grep -l "2026-08-05" .../public/*.html | wc -l
      31
$ /usr/bin/grep -o "<lastmod>[0-9-]*</lastmod>" .../public/sitemap.xml | sed 's/<[^>]*>//g' | sort | uniq -c | sort -rn
  27 2026-08-05
  15 2026-08-11
   3 2026-08-07
   2 2026-09-01
$ git -C ... log -1 --format='%h %ad %s' --date=short -- 'public/*.html'
d6e8dab 2026-09-10 Strip every per-measure rebate dollar amount from every live page
```
**LGM: 31 of 48 confirmed at `2026-08-05`** — that 31 is the **HTML-file** count.
The sitemap `lastmod` count for the same date is **27**, a distinction the brief's
figure does not carry and which I record rather than smooth over. Content
corrected through 2026-09-10 — 36 days stale.

**The gate CATCHES both, and its LGM finding is stronger than "stale".** DCI:
71 `[stale-vs-content]` rows, `published review date 2026-08-24 precedes the last
visible-text change 2026-09-10 [KNOWN-OPEN]`, plus the explicit note
`KNOWN-OPEN hold in force: DCI-D-003 … Debt measured at 70 of 72 pages; sitemap
shows 70 x 2026-08-24 while content was corrected through 2026-09-11`. LGM: 46
`[stale-vs-content]` **plus 113 `[precedes-creation]`** — because, as established
in §3.7, LGM's first commit is 2026-08-11 and a 2026-08-05 review date is not
merely stale, it is **impossible**.

---

## 6. THE BROOMFIELD / UNITED POWER ADJUDICATION

**Verdict: all 18 DCI R2 findings are FALSE POSITIVES. The page is correct. The
defect is (i) a real staleness in DCI's `ground-truth.md` and (ii) a config gap
that inherited it.** Not a territory defect on the page.

All 18 findings are `United Power` — 16 on `public/insulation-broomfield.html`
across 9 surfaces (VIS ×9, LD ×2, LOWVIS ×2, META, OG, TW) and 2 on
`public/xcel-rebate-eligibility-checker.html`. Representative rows verbatim:
```
public/insulation-broomfield.html:VIS  a  United Power | scope=Broomfield | Most of Broomfield is in Xcel Energy service territory, but parts of NORTHERN Broomfield are in United Power territory — the rebate program differs.  [utility-not-serving-town]
public/insulation-broomfield.html:LD   a  United Power | scope=Broomfield | Parts of northern Broomfield (sections of Anthem and adjacent neighborhoods) are in United Power territory, which has its own Member Energy Efficiency rebate program.  [utility-not-serving-town]
public/insulation-broomfield.html:OG   a  United Power | scope=Broomfield | Xcel and United Power rebates explained.  [utility-not-serving-town]
public/xcel-rebate-eligibility-checker.html:JS  a  United Power | scope=Arvada,Aurora,Broomfield,Centennial,Denver,Englewood,Golden,Highland,Lakewood,Littleton,Northglenn,Park Hill,Thornton,Washington Park,Westminster,Wheat Ridge | United Power runs its own Member Energy  [utility-not-serving-town]
```

**Evidence, retrieved not guessed.**

*1. The config's territory claim, and its source.* `dci.json` R2 sets
`towns.Broomfield = {gas: "Xcel Energy", electric: "Xcel Energy"}` with no second
utility, and carries:
`"territory_note": "docs/board/ground-truth.md:5-7 verbatim: 'Xcel Energy is both
the gas and electric utility for this market. Denver metro. Unlike Longmont and
Greeley, there is no second utility and no service-area hedging required.'"`

*2. That ground-truth bullet, verbatim, with its own date.*
```
- **2026-06 or earlier — utility.** Xcel Energy is both the gas and electric
  utility for this market. Denver metro. Unlike Longmont and Greeley, there is
  no second utility and no service-area hedging required.
```
It is the **oldest entry in the file**, and `ground-truth.md` contains **zero**
mentions of Broomfield (`/usr/bin/grep -n -i "broomfield"` → no match).

*3. The same repo's own verified-facts list contradicts it.*
`STATE_OF_PROJECT.md:755` heads a section
`### Rebate facts (verified June 10, 2026 — next quarterly review due September
10, 2026)`, and line 758 lists under **Alive:**
`… City of Golden Match (Golden only, cityofgolden.gov), United Power Member
Energy Efficiency (parts of N. Broomfield), Power Ahead Colorado …`

*4. A prior adversarial read examined this exact copy and ruled it correct.*
`docs/board/read-2026-08-25/groupC.md:462-464`, verbatim:
```
- Deliberate per-suburb prose variation (cost ranges, era mix, neighborhood
  names, the United Power carve-out on Broomfield) is intact and is NOT
  reported.
```

*5. The architecture treats United Power as a real selectable utility.*
`groupH.md:1118`: `(Note: `util === 'united'` is handled correctly — it
`unshift`s a United Power program …)`.

*6. The content predates the ground-truth claim and has never been challenged.*
`git log -S"United Power" -- public/` → earliest `ced8651 2026-06-10 Initial
commit`. Page copy and ground-truth sentence have coexisted, contradicting each
other, since day one.

*7. Primary source — the decisive check.* Web search confirms **United Power
does serve northern Broomfield, including Anthem**: the Anthem Ranch community
association lists "United Power - Northern Broomfield" (500 Cooperative Way,
Brighton CO 80603) for electricity alongside Xcel Energy for gas; United Power's
own materials place Broomfield County in its footprint, including
cooperative-owned substation sites in Adams, Broomfield and Weld counties. The
Anthem development sits in the northern part of the city/county, inside United
Power's certificated territory rather than Xcel's.
Sources: [Local Resources — Anthem Ranch Community Association](https://arca.clubexpress.com/content.aspx?page_id=22&club_id=294082&module_id=323205),
[Service Area | United Power](https://www.unitedpower.com/service-area),
[About Your Cooperative | United Power](https://www.unitedpower.com/about).

**Conclusion.** The page's service-area hedging is factually correct,
independently verified, sourced in the project's own quarterly review, affirmed
by a prior adversarial read, and wired into the calculator. `ground-truth.md`'s
"no second utility and no service-area hedging required" is an over-broad
sentence about the *gas* utility that was never re-tested for *electric*, and
`dci.json` propagated it verbatim into the gate. R2's own blind-spot line names
the failure mode precisely: *"it enforces the config's territory and cannot
discover that a town's utility changed."*

Two follow-ups for whoever owns them — **I did not make these changes**:
`ground-truth.md:5-7` needs the Broomfield/United Power electric carve-out
stated, and `dci.json`'s `towns.Broomfield` needs a second electric utility with
a qualifier. Separately, no citation-registry entry exists for United Power
(`/usr/bin/grep -n -i "united power" docs/citation-registry.json` → no match) —
that is a real, distinct attribution debt.
The 2 rows on `xcel-rebate-eligibility-checker.html` are a different false
positive: the checker names United Power generically as a selectable option,
scoped by the rule to all 16 towns at once, which is not a town-specific
attribution at all.

---

## 7. STATE OF THE CHECKOUTS

Twenty pre-fix worktrees were created under `/tmp/claim-gate-scratch/r3/wt` and
all twenty removed and pruned. No main working tree was ever checked out to a
different commit.

```
$ git -C <each> status --porcelain     # all four: EMPTY
$ git -C <each> worktree list
/Users/vongimbel/code/denvercoloradoinsulation.com    1b6949c [main]
/Users/vongimbel/code/longmontcoloradoinsulation.com  a86c5af [main]
/Users/vongimbel/code/greeleycoloradoinsulation.com   ee0157d [main]
```
HEAD SHAs are identical to the session's opening snapshot: canon `7a091a0`,
DCI `1b6949c`, LGM `a86c5af`, GCI `ee0157d`. No page, generator, config,
fixture or live site was changed by this row.

---

## 8. DECISIONS THIS ROW MADE THAT THE BRIEF DID NOT PRE-STATE

1. **`2cecf33` does not exist in DCI** — it is GCI's commit. The brief's "DCI
   `2cecf33`-era" is imprecise. I located the real per-repo strip commits from
   the release notes: DCI `5703f8c` (198, release `da59c12`), LGM `d6e8dab`
   (133, release `084a423`), GCI `2cecf33` (206). 198+133+206 = 537, matching
   the brief's stated trio.
2. **`ops/claim_gate.sh` does not exist in any historical tree** (added today),
   so replays invoked `claim_gate.py` directly with `--config` and `--repo`.
3. **`--today` set to each fixing commit's date**, not today's, as the fair test
   of a tree by its own day's facts. For defect 9a I confirmed the choice is
   immaterial (both parts that fire are git-relative); for 9b I recorded that
   replaying one day earlier would have added spurious `[future-date]` hits, so
   verdicts must not be pooled across dates.
4. **Exit-2 verdicts are reported as "the gate did not run", and rule-level
   verdicts are labelled as harness results.** I verified the exit-2 claim
   myself on three DCI worktrees rather than accepting it from a subagent.
5. **Worktrees removed and pruned at the end** rather than left in place
   (Rule 2), after verifying the four checkouts.
6. **`/usr/bin/ls` does not exist on macOS** — `ls` is at `/bin/ls`. The brief's
   tooling rule names `/usr/bin/grep`, which does exist; I used `/bin/ls` and
   said so.
7. **`grep -oE '\$[0-9,]+' -r <dir>` over-counts by one** on trees containing
   `og-image.png`, because it counts the `Binary file … matches` notice as a
   hit. `-I` gives the right answer. This is the same class of off-by-one as the
   recorded ugrep defect, from a different direction.
8. **R1's catch of the central defect is reported with its mechanism** — R1
   flags all registry-quotations whose `quote` field is absent, so the catch is
   real but undiscriminating. Scoring it CAUGHT without that sentence would have
   overstated the gate.
9. **Adjudication was exhaustive, not sampled.** Every adjudicated finding on
   every rule on every property was classified by defect class, and the class
   counts were computed by script and cross-checked to sum to the reported
   adjudicated totals.
10. **`common.json` R7's `nrel.gov → nlr.gov` replacement is flagged as a
    probable typo** and the NREL finding scored REVIEW rather than TRUE. NREL is
    a live institution; `nlr.gov` is the National Labor Relations Board. I did
    not change it (R1 owns the spec, R2 the config).
11. **The brief's premise "Atmos occurs zero times" on the three Xcel towns is
    false at every measurable tree** (17/16/19 at HEAD). What `e6cb44e` changed
    was the *polarity* of those mentions, not their presence. The accurate claim
    is "zero Atmos anchors / zero Atmos figures", which the fixing commit's own
    body says.
12. **The brief's premise for defect 10 describes `4cf7a52`'s tree, not
    `cb675ab`'s.** Both were replayed; R9 misses on both.
13. **The brief's "LGM 31 of 48" is the HTML-file count; the sitemap count is
    27.** Both reported rather than reconciled silently.
14. **The brief's "11 instances on 3 pages" for the `prerequisite` class
    measures 14 case-insensitive occurrences on 5 files** — the commit's count
    excludes 4 unrelated-sense uses. Reported as measured.
15. **The brief's "23 occurrences" of `25-40%` is right for source files; the
    public/ count is 24, not 23.** Both stated.
