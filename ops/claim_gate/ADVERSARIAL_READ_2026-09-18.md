# Adversarial read of the claim gate and the three properties — 2026-09-18

Sixth adversarial pass. Zero inherited context: every instrument below was built
from scratch in `/tmp/gate-close/r6/`, and every number was measured, not read
out of a prior document. Nothing in canon or in the three properties was edited.

**State found, and left.** The brief named canon `f8fe33a`, DCI `bdf6701`,
LGM `4211b8d`, GCI `3a1357f`. Those were each one commit stale by the time the
first command ran — a concurrent session landed `Release lane
gate-close-findings-2026-09-18-*` in all four repos at `17:11` and pushed canon.
Actual heads under review:

```
calibrated-design-canon         58e98a0   main   clean   0 0
denvercoloradoinsulation.com    65383a7   main   clean   0 0
longmontcoloradoinsulation.com  95c93d1   main   clean   0 0
greeleycoloradoinsulation.com   34adbf4   main   clean   0 0
```

The three release-lane commits touch `docs/lanes.md` only; **zero files under
`public/` differ** between the briefed SHAs and the actual heads, so every
verdict holds at either. Canon was momentarily `0 1` (one unpushed lane commit)
when first measured and is `0 0` now.

---

## 0. THE SINGLE MOST SEVERE FINDING

**The gate manufactures the evidence it then adjudicates.**

`build_claim_set` (`claim_gate.py:1296-1303`) splices text out of the citation
registry and attaches it to an artifact as a synthetic `CITE` surface. `S_CITE`
is in `POOL_KEYS` (`claim_gate.py:915`), so every proposition rule reads it as
though it were on the page. Two defects in that splice mean it routinely
attaches the **wrong** text to the **wrong** artifact — and then blocks on it.

**Defect one: a one-character normalization asymmetry blocks DCI on nine
sentences that appear on none of the nine pages named.**

`Ctx.key_for_cited_stat` (`claim_gate.py:1236-1248`) binds a page's rendered
cited-stat block to a registry key **by URL alone**; the label is only a
tiebreaker, and on tiebreak failure it takes `best = best or k` — the
alphabetically first key sharing that URL.

```python
1244	            label = S.collapse(str(e.get("determiner") or "") +
1245	                               str(e.get("source") or ""))
1246	            if label and cs["label"] and S.collapse(cs["label"]) == label:
1247	                return k
1248	            best = best or k
```

The page-side label is `dec()`-normalized when stored (`surfaces.py:708`); the
registry side at line 1244-1245 gets `collapse()` only, **no `dec()`**. Measured
directly against the live registry:

```
registry entries sharing the Xcel insulation-air-sealing URL:
    XCEL_BLOWER_DOOR             source= Xcel Energy's residential rebate summary
    XCEL_WHOLE_HOME_EFFICIENCY   source= Xcel Energy's 2025–2026 Colorado residential rebate summary

registry label dash codepoint: ['0x2013']          <- EN DASH
page     label dash codepoint: none (ASCII)        <- dec() folded it
collapse(page) == collapse(registry)           ->  False
collapse(dec(page)) == collapse(dec(registry)) ->  True
```

`XCEL_WHOLE_HOME_EFFICIENCY` can therefore **never** match by label, and every
page citing that URL falls through to `XCEL_BLOWER_DOOR`, whose `stat` is the
CFM 50 sentence. That sentence is then spliced onto the page and adjudicated by
R5 as an uncited statistic. Result: **9 of DCI's 46 blocking R5 findings name a
file that does not contain the quoted sentence** — not merely the sentence, but
the substring `CFM` does not occur at all on any of the nine:

```
FILE                                              Denver  CFM(any)  cited-stat
public/attic-insulation-cost-denver.html          37      0         8
public/blown-in-insulation-cost-denver.html       39      0         7
public/hear-rebate-status-colorado.html           27      0         8
public/index.html                                 57      0         8
public/insulation-project-timeline-denver.html    31      0         8
public/power-ahead-colorado-insulation.html       24      0         7
public/resources.html                             69      0         7
public/spray-foam-vs-blown-in-comparator.html     34      0         7
public/xcel-rebate-eligibility-checker.html       32      0         7
```

The text being flagged as an *uncited statistic* is itself a citation-registry
entry — it carries `source` and `url` by construction. R5 is failing a citation
for lacking a citation.

**Defect two: the same splice carries the repo-under-test into the control
fixtures, and the gate then refuses to run.** `run_controls`
(`claim_gate.py:4594`) does `base["_gen"] = gen`, and `_control_ctx`
(`claim_gate.py:4549`) pins it onto every control context — four lines below a
comment reading *"A control must never open the repo under test."* Proven live,
not inferred: adding two entries to a scratch GCI's `_shared_components.py`
`CITED_SOURCES` — **generator source only, `public/` never regenerated** —
reproduced both failure modes on innocent canon fixtures:

```
$ git status   ->   M _shared_components.py          (public/ untouched)
$ probe string present in public/?   ->   NOT PRESENT

EXIT=2
  canary~ R9-N2  fixtures/repaired/R9_cross_surface_contradiction *** FIRES ON REPAIRED *** 1 hit(s) on sub N2
  canary- NEG05  fixtures/negative/NEG05.html *** FALSE ALARM *** R4 ASSERTS combin,combine,combined,on top,on top of,stack
  CLAIM GATE: NOT RUN — a rule that cannot detect its own defect is worse than no rule
```

`isolation_breach` (`claim_gate.py:4561-4573`) does not catch it: it checks the
hit's `rel`, and the contaminated hits carry the *fixture's* rel. The
contamination arrives as injected surfaces **on** the fixture, so the isolation
check is watching the wrong axis.

**Why this is the most severe thing here.** Both halves are the same design
flaw, and it is the one failure mode that invalidates every other number the
tool prints: a verification tool that synthesizes claim surfaces and attributes
them to artifacts that do not contain them cannot be used to adjudicate what an
artifact says. It blocks DCI on fabricated attributions today, and on LGM and
GCI — where this pass wired the gate into `regen_all.sh` under `set -e` — an
ordinary content edit that adds a citation whose URL collides with one in a
fixture turns the build red with `CLAIM GATE: NOT RUN`. Worst of all, its
direction is inverted: a repo that acquires a genuine contradiction can, through
the same channel, silence the control that would have caught it, so **the gate
refuses to run precisely when the defect it exists for is present.**

The pass observed the `_gen` symptom and recorded it in
`GATE_CLOSE_2026-09-18.md` §"A NEW GATE DEFECT" — and then wired the gate into
two production builds anyway. It observed the nine-misattributed-findings
symptom in §4(a) and explicitly declined to root-cause it ("that mechanism is
inference"). Neither the shared cause nor the one-character fix was found.

---

## (a) The 86-vector re-run

Rebuilt byte-exact from §(b) and §SECOND-SECTION-1 of
`ADVERSARIAL_READ_2026-09-17.md`. Harness: `/tmp/gate-close/r6/harness.py` and
`vectors.py`. Each vector is a throwaway git repo carrying the vector page plus
a benign `index.html`/`robots.txt`/`llms.txt`, driven through the REAL gate with
`--config <scratch>` where the scratch config is
`{"extends": "<real property>.json", "min_artifacts": 1, "expected_html": 1}`
and nothing else overridden, `--today 2026-09-17`. Every positive control
reproduced the prior read's result exactly, so the instrument is calibrated.

### **11 of 86 miss now, against a prior 12 (13 by the prior read's own arithmetic)**

| rule | vectors | prior (final) | **now** | delta |
|---|---|---|---|---|
| R1 | 7 | 1 | **1** | — |
| R2 | 18 | 3 | **2** | B8 newly caught |
| R3 | 20 | 3 | **3** | — |
| R4 | 9 | 0 | **0** | — |
| R5 | 8 | 0 | **0** | — |
| R6 | 6 | 0 | **0** | — |
| R7 | 8 | 1 | **1** | — |
| R8 | 6 | 3 | **2** | H6 newly caught |
| R9 | 2 | 1 | **1** | — |
| R10 | 2 | 1 | **1** | — |
| **total** | **86** | **12 stated / 13 summed** | **11** | **2 fixed, 0 regressions** |

**The prior read's headline number does not match its own table.** Its per-rule
breakdown sums to 13, not the 12 it states, and its round-4 column sums to 17,
not 15. Verified:

```
col        stated  actual-sum  ok
vectors        86         86   OK
R1(rd1)        59         59   OK
R2(rd2)        29         29   OK
R3(rd3)        17         17   OK
R4(rd4)        15         17   *** MISMATCH ***
R5(final)      12         13   *** MISMATCH ***
```

The eleven still missing, each re-measured:

| vector | result now | why |
|---|---|---|
| **R1-A3** anaphoric attribution | `RAW 0 ADJ 0 PASS` | source named three sentences earlier; declared hole |
| **R2-B2** no `attribution_words` | `RAW 0 ADJ 0 PASS` | sentence carries none of the 21 words, so R2 never looks for a utility |
| **R2-B15** unreferenced `og-image.svg` | `RAW 1 ADJ 0 PASS` | raised, then cleared by `sitewide-no-town-in-clause` |
| **R3-C3** figure spelled in words | `RAW 0 ADJ 0 REPORT` | no numeral to anchor on; declared |
| **R3-C16** `pays the most` | `RAW 0 ADJ 0 REPORT` | not in `rank_words`; declared |
| **R3-C17** bare `1550`, no money word | `RAW 0 ADJ 0 REPORT` | 120-char window carries no `money_words` entry |
| **R7-G6** `pre&#8209;requisite` | `RAW 0 ADJ 0 PASS` | entity folds to `pre-requisite`; config string is `prerequisite` |
| **R8-H3** impossible date on `privacy.html` | `RAW 2 ADJ 0 PASS` | `own_effective_date_pages`; raised and cleared |
| **R8-H4** impossible date on `404.html` | `RAW 2 ADJ 0 PASS` | `exempt_pages`; raised and cleared |
| **R9-I1** contradiction paraphrased | `RAW 0 ADJ 0 PASS` | outside configured `value_slots`; declared |
| **R10-J1** promise outside the patterns | `RAW 0 ADJ 0 PASS` | outside the 14 `promise_patterns` |

**The two newly caught, each checked rather than credited.**

- **R8-H6** (`<time datetime="2026&#45;08&#45;24">`) is a **genuine fix**. The
  entity-encoded hyphens are now decoded and the date is parsed — the gate
  prints `time[datetime] = 2026-08-24`, where previously the page contributed no
  dates at all. Isolated from my harness's own git dates by re-running with a
  future value: `2027&#45;01&#45;01` → `RAW 2 ADJ 2 exit 1`.
- **R2-B8** (runtime string concatenation) is **caught by a sub-test that cannot
  discriminate, and I do not credit it.** The hit reads
  `public/insulation-johnstown.html:JS t Atmos Energy named in a
  verdict-reachable JS literal with no town input [town-blind-tool]`. Sub-test
  `t` fires on any utility name in a JS literal with no town in the same
  literal — including the **correct** one:

```
t-blanket: CORRECT util in one JS literal      RAW 0  ADJ 0  exit 0
t-blanket: 'Atmos Energy sponsors the county fair.'  RAW 1  ADJ 1  exit 1  <- not a territory claim at all
t-blanket: concat of the CORRECT utility       RAW 1  ADJ 1  exit 1  <- Xcel IS Johnstown's gas utility
B8 baseline (concat of the wrong utility)      RAW 1  ADJ 1  exit 1
```

  A property whose JS assembles a utility name across a concatenation boundary
  **correctly** fails R2. The vector's flip to CAUGHT is a false positive that
  happens to point the right way. **Honest count: 12 of 86 still miss in
  substance.**

### NEW EVASIONS OPENED BY THIS PASS'S FIXES

The brief flagged that each Unicode fix opened the next hole three rounds
running. **That pattern did not repeat among the 86: zero vectors went
CAUGHT → MISS.** I then probed this pass's specific changes for holes the fixed
86 cannot reach.

**NEW-22 (moderate) — R2 sub-test `t` is a false-positive blanket**, as measured
above. It fires on correct attributions and on non-attributions. It is latent on
all three properties today (all show R2 `ADJ 0`), and live for anyone who writes
a concatenated utility name.

**The splitter fix opened no pardon — tested and clean.** `7be4641` stopped the
sentence splitter breaking at an abbreviation period, which is what let R7-G1
finally fire. The obvious new hole is that a longer sentence lets an allowlisted
phrase pardon a defect joined to it across the abbreviation. It does not:

```
baseline: defect alone                               RAW 1 ADJ 1 exit 1  CAUGHT
baseline: allowlist sentence then defect sentence    RAW 1 ADJ 1 exit 1  CAUGHT
allowlist + "Sec."     + defect                      RAW 1 ADJ 1 exit 1  CAUGHT
allowlist + "Dec."     + defect                      RAW 1 ADJ 1 exit 1  CAUGHT
allowlist + "No."      + defect                      RAW 1 ADJ 1 exit 1  CAUGHT
allowlist + "Corp."    + defect                      RAW 1 ADJ 1 exit 1  CAUGHT
allowlist + "Inc."     + defect                      RAW 1 ADJ 1 exit 1  CAUGHT
allowlist + "approx."  + defect                      RAW 1 ADJ 1 exit 1  CAUGHT
allowlist + "Colo."    + defect                      RAW 1 ADJ 1 exit 1  CAUGHT
allowlist + "Ave."/"Mr."/"vs." + defect              RAW 1 ADJ 1 exit 1  CAUGHT
```

**The R4 anaphora class (`8ff3a55`) does not over-sweep — tested and clean.**
Every legitimate use the brief protects is raised and cleared through a *named*
filter rather than silently dropped, and a real denial still fires:

```
stack effect (building science)   RAW 1 ADJ 0  [legitimate_uses (stack effect, plumbing stack, can lights)]
plumbing stack                    RAW 1 ADJ 0  [legitimate_uses ...]
how your home stacks up           RAW 1 ADJ 0  [legitimate_uses ...]
new insulation on top of the old  RAW 1 ADJ 0  [legitimate_uses ...]
neutral "These programs are administered separately."   RAW 0 ADJ 0
neutral "Both programs require a licensed contractor."  RAW 1 ADJ 0  [NEUTRAL -- fewer than two distinct programs]
DENIAL "...cannot be combined on the same measure."     RAW 1 ADJ 1  <<< FIRES
```

**Two prior-round R2 escapes are now CLOSED** — genuine improvements, verified
on the fixture bytes:

```
NEW-21 A6  wrong attribution as a trailing and-clause   RAW 1 ADJ 1 exit 1  CAUGHT (was PASS)
NEW-20 inversion joined by em dash U+2014               RAW 2 ADJ 2 exit 1  CAUGHT (was PASS)
NEW-20 inversion joined by en dash U+2013               RAW 2 ADJ 2 exit 1  CAUGHT (was PASS)
NEW-20 inversion joined by ASCII hyphen                 RAW 2 ADJ 2 exit 1  CAUGHT (was PASS)
control: inversion joined by ", and"                    RAW 2 ADJ 2 exit 1  CAUGHT
```

**NEW-23 (severe, enforcement not detection) — R3's demotion silently removed
20 of the 86 vectors from the blocking set.** `b00e3b1` made R3 report-only on
its measured 68.1% false-positive rate. 17 of the 20 R3 vectors are still
DETECTED, and **every one of them now exits 0**. A rebate dollar figure —
the defect class that produced 545 live instances and the owner's ban — can no
longer stop a release on its own. Scored as "caught" by the same arithmetic as
before, the number is unchanged; as a release gate, R3 is off.

---

## (b) Every positive control, and every attack on the repair phase

Counts reproduced independently on a mirror at
`/tmp/gate-close/r6/mirror/canon`: **29 positive, 29 repair, 14 negative**, and
the baseline is `29 positive DETECTED, 0 MISSED · 14 negative clean, 0 FALSE
ALARM · 29 repaired-clean`, exit 1 on DCI.

### The decisive test: all 29 controls stop firing when the defect is removed

I substituted every repaired fixture in place of its original — 26 files and
directories — and re-ran. If a control still fired, it would be detecting
something other than the defect it names.

```
substituted 26 fixtures with their repaired form
EXIT 2
   CONTROLS: 0 positive DETECTED, 29 MISSED · 14 negative clean, 0 FALSE ALARM
   CLAIM GATE: NOT RUN — a rule that cannot detect its own defect is worse than no rule

STOPPED FIRING (correct): 29
STILL FIRING on repaired content (SUSPECT): 0
```

**29 of 29 survived. Zero controls are detecting something else.**

### Are the 29 repaired fixtures genuine repairs?

I diffed all 26 against their originals. Every one changes the defect and its
immediate surroundings and nothing more; the R6 repair flips `gap >= 20` to
`pctShort >= 50` and `gap >= 8` to `pctShort >= 20`, which is exactly the
defect; the R8 repairs move only the date values.

**One fixture is byte-identical to its repaired form** —
`R2b_wrong_utility_no_string.html`, confirmed with `cmp`. That is legitimate,
not a hole: R2b is a two-file unit, the defect lives in the companion
`R2b_og-image.svg` (`Atmos rebates explained` → `Rebates explained`), and the
html merely carries the `og:image`/`twitter:image` references. Attack A5 below
proves the pair is live.

### Attacks on the repair phase — 6 of 7 routes closed

| attack | result |
|---|---|
| **A1** zero-byte repaired fixture | **exit 2** · `*** REPAIRED FIXTURE TOO THIN *** 0 bytes, under the 120-byte floor; 0 bytes against the original's 866 (0%)` |
| **A2** empty-page repaired fixture | **exit 2** · `*** REPAIRED FIXTURE TOO THIN *** 96 bytes … (11%)` |
| **A3** repaired fixture = the original | **exit 2** · `*** FIRES ON REPAIRED *** 5 hit(s) on sub ASSERTS` |
| **A4** repaired fixture deleted | **exit 2** · `*** REPAIR FIXTURE MISSING *** a control whose repair test cannot run is not a control` |
| **A5** defect re-inserted into R2b's SVG | **exit 2** · `*** FIRES ON REPAIRED *** 2 hit(s) on sub a` |
| **A8** whole `repaired/` directory deleted | **exit 2** · `REPAIR FIXTURE MISSING` on all 29 |
| **A7** unrelated filler over the 120-byte floor | **exit 2** · `*** REPAIRED FIXTURE TOO THIN *** shares only 27% of the original's word tokens (floor 30%) -- padding is not s…` |

The three routes prior rounds found — gutting, padding, deletion — are all still
closed, and the token-overlap floor added since catches the padding variant too.

**The one route still open: NEW-18, a word salad built from the original's own
vocabulary.** Confirmed still open, exactly as the prior read recorded and the
implementing row declined to fix:

```
NEW-18 word salad from the ORIGINAL vocabulary   exit 1  (891 bytes vs original 866)
   REPAIR TESTS: 29 repaired-clean, 0 FIRE ON REPAIRED, 0 NOT TESTED
   CLAIM GATE: FAIL
```

A bag of the original's words, in no order, with no markup and no defect,
satisfies R4b's repair test silently. Exploiting it requires write access to
`fixtures/repaired/`, which is the access that would let you edit the rule — I
agree with the prior read that this is hardening, not a live hole.

**A finding about what actually defends the rules.** Emptying a live config list
(`R5.magnitude_words` → `[]`) leaves the dead-config audit reporting `0 OWED`,
green. What stops it is the canary:

```
exit=2
  canary+ R5  fixtures/R5_uncited_statistic.html  *** MISSED *** (0 hits on the sub-test this control proves: mag)
  CONTROLS: 28 positive DETECTED, 1 MISSED · 14 negative clean, 0 FALSE ALARM
```

The OWED audit is a tidiness report. **The control fixtures are the defence.**
That is worth stating because §(k) shows the audit has three holes and the
controls do not.

---

## (c) Every exception added this pass, and whether its justification is TRUE

Config commits this pass: `8ff3a55 … eafada2`, 24 of them. The exception-adding
ones are enumerated below with the assertion each makes and my test of it.

### R1 `quotation_allowlist` — 13 entries across three properties

*(Externally-sourced entries were fetched against their named publishers; the
verbatim results are in §(c2). Summary: every factual assertion — hashes, URLs,
dates, byte counts, line numbers, verbatim text — checks out. One piece of
reasoning is false, and it errs permissively.)*

The **four DCI entries** and **one GCI entry** assert something testable without
a network: that the quoted span is **not a quotation at all** — a scare quote or
reported hypothetical speech whose speaker is a common noun, not a publisher.

| entry | asserted page | assertion |
|---|---|---|
| `The guidance here says "not yet" as often as it says "yes,"` | DCI + GCI `about.html` | speaker is "the guidance here" — the site's own editorial stance |
| `someone at your door says they "noticed your roof"` | DCI `choosing-denver-insulation-contractor.html` | speaker is an unnamed hypothetical storm-chaser |
| `If a quote says "blown-in cellulose"` | DCI `insulation-dense-pack-cellulose.html` | "a quote" is a contractor's written estimate — a noun collision |
| `If a quote says "tape the joints"` | DCI `insulation-duct-sealing.html` | same noun collision |

Each carries, verbatim, the same self-indictment: *"THE STRUCTURAL FIX IS OWED
AND THIS IS NOT IT: R1 half B should require a RECOGNISED PUBLISHER inside the
same 40-character lookback before it fires … Allowlisted narrowly, per sentence,
until the engine change lands; then delete these four entries."* The GCI twin
says *"THIS ENTRY IS A STOPGAP, NOT THE CAUSE FIX … WHEN THAT LANDS, DELETE THIS
ENTRY AND RE-MEASURE — it should become redundant, and leaving a redundant
allowlist entry in place is how a real future defect gets cleared by accident."*

**The justifications are true on their face and the entries are honestly
labelled. The engine change they are waiting for has not landed, so five
stopgaps are live with no expiry mechanism, and the config itself names that as
the hazard.** Both configs say another row was applying the cause fix to
`common.json`; it is not there.

### R4 `legitimate_uses` — five LGM additions

Asserted: four are building science (`thermal layer`, `insulation layer`,
`flash layer`, `only layer between`) and "none can express two programs
combining"; the fifth (`does publish a combined figure alongside`) is a
Director-licensed attributed description held in an **unrendered** record.

**TRUE, and tested two ways.** First, the four building-science phrases are
physical-material descriptions and none names a program — the same class as
`stack effect`. Second, the whole `legitimate_uses` mechanism was probed for
over-sweep and is clean: every protected use is raised and cleared through a
named filter (output quoted in §(a)), and a real denial still fires. The fifth
entry's "renders nowhere" claim is checkable and the commit states its own
verification: `render_alive_rebates_html()` emits only name+summary+status and
has zero call sites.

One structural note the commit is right about and worth repeating: `_deep_merge`
**replaces** a list rather than unioning it, which is why each property list is
restated in full. That is a real trap — dropping one inherited entry while
copying silently un-declares a portfolio-wide legitimate use.

### R5 `recognised_publishers` — three LGM additions

Asserted: `Colorado Geospatial Portal`, `U.S. Census Bureau`, `Census Bureau`
are bodies LGM already cites BY NAME in its own registry
(`LONGMONT_LPC_PARTIAL_ELECTRIC_TERRITORY`, `CENSUS_ACS5_PLACE_HOUSING`), and
`f_pub` still requires an attribution verb and the publisher within 80
characters of the figure, so this is not a loosening.

**TRUE as to the registry entries and as to the mechanism.** This is the
narrowest possible form of the change: it widens *who counts as a publisher*,
not *what counts as attribution*. Note, though, that `f_pub` is the filter the
prior read found exempts a sentence that merely **names** a publisher regardless
of whether that publisher is the source (vector R5-E3) — and `1bcc0b7` this pass
removed R5's blanket `recognised_publishers` exemption, which is what flipped
DCI's `insulation-lakewood.html`. The two changes pull in opposite directions
and both are defensible; the net is not measured anywhere.

### R5 `magnitude_words` — `"lose"` → `" lose"` (leading space)

Asserted: `lose` is matched as a raw substring with `word=False` and collides
with `cellu-lose` and `c-lose to`, producing 16 of 59 R5 findings, and every
genuine use still matches because `has_any()` is case-insensitive.

**TRUE and it is a narrowing, not an exemption** — but it is a fragile one. A
leading space is not a word boundary: it fails on a sentence-initial "Lose", on
`>Lose`, and after any tag or punctuation that is not a space. The correct fix
is `word=True`. The commit's own verification only confirms one positive case
still fires.

### R3 `allowed_figures` / `allowed_thresholds` / `allowed_structure_percentages`

Tested exhaustively in §(e). **All the `allowed_thresholds` justifications test
TRUE.** `allowed_structure_percentages` does **not** describe thresholds — see
§(e) for the governing-ruling conflict it sits inside.

### R8 `pinned_pages` — GCI, 11 new pins (13 total)

Asserted, verbatim: *"13 pinned pages as of 2026-09-18, up from 2 … Each entry
carries expected_footer and expected_sitemap, so a pin whose page drifts fires
pin-drifted instead of silently exempting it."* Each of the 11 asserts its page's
only diff was *"the sitewide organization_schema()/person_schema() knowsAbout
neutralisation … MEASURED, not assumed."*

**SUBSTANTIVELY TRUE — and I tested it on the merits, not on the note.**
Independent derivation, built without reference to the config: **24 GCI pages
changed visibly on 2026-09-18; 14 did not. All 13 pinned pages have
`last_visible ≠ 2026-09-18`. Zero pinned pages visibly changed.** Mechanical
check of the `8a5616c` diff for all 11: changed lines that are neither a date
line nor `knowsAbout`/schema = **0 for every one**. Representative full diff for
`insulation-ault.html` — every changed line is inside `ld+json` or is the review
date:

```diff
-  "dateModified": "2026-09-09"          +  "dateModified": "2026-09-10"
-    "Atmos Energy Residential Insulation and Air Sealing Rebates",
+    "Natural gas utility residential insulation and air sealing rebate programs",
-        … Last reviewed: <time datetime="2026-09-09">September 9, 2026</time>.
+        … Last reviewed: <time datetime="2026-09-10">September 10, 2026</time>.
```

**Three bookkeeping assertions in the note are FALSE, and one pin is
substantively wrong:**

1. **"13 pinned" and "13 that did not change" are different sets sharing a
   number.** Only 11 of the 13 carry the JSON-LD-only justification;
   `about.html` and `404.html` are pinned for older, unrelated reasons.
2. **The count is 14, not 13.** 24 changed + 14 unchanged = 38. The note's own
   arithmetic, 24 + 13 = 37, is one short of the corpus. The 14th is
   `privacy.html`, handled by `own_effective_date_pages`.
3. **"Each entry carries expected_footer and expected_sitemap" is false.**
   `404.html`'s entry carries only `reason` — no `expected_footer`, no
   `expected_sitemap`. The drift guarantee the note advertises universally does
   not cover it, **and that is the one entry that has drifted.**

### R8 `today` — per-property as-of override on all three properties

Asserted (GCI, verbatim): *"common.json pins R8.today to 2026-09-17 and the
calendar rolled over, so the gate was measuring GCI as-of YESTERDAY. R8 part (b)
fails any published date LATER than the as-of, which means a page carrying a
truthful date of today reads as publishing a date in the future — and, worse, a
genuinely invented future date becomes indistinguishable from a correct one."*

**The diagnosis is exactly right and the fix re-commits the defect it
describes.** The gate never reads the system clock:

```
claim_gate.py:932   self.today = cfg.get("R8", {}).get("today", "2026-09-17")
claim_gate.py:4966  asof = cfg.get("R8", {}).get("today", "2026-09-17")
$ /usr/bin/grep -n 'date.today()\|datetime.now\|utcnow' claim_gate.py
  (only time.time() for the duration timer — no calendar read anywhere)
```

Three property configs were set to the literal string `"2026-09-18"`;
`common.json` remains `"2026-09-17"`; the hardcoded fallback in code is
`"2026-09-17"`. Proven by run — a page truthfully dated one day past the pin
fails, and there is no mechanism that will ever notice:

```
page dated 2026-09-18  ->  R8 RAW 0  ADJ 0  exit 0
page dated 2026-09-19  ->  R8 RAW 2  ADJ 2  exit 1
         public/a.html:ld:dateModified  b  ld:dateModified = 2026-09-19 is after today (2026-09-18)  [future-date]
         public/a.html:time[datetime]   b  time[datetime] = 2026-09-19 is after today (2026-09-18)  [future-date]
page dated 2026-09-20  ->  R8 RAW 2  ADJ 2  exit 1
```

The generators stamp hardcoded date constants rather than `datetime.now()`
(`_generate_llms_txt.py:37` says so explicitly), so this does not fire on a
calendar tick alone. **It fires on the next content pass that sets a truthful
date after 2026-09-18** — on two properties where the gate is now wired to halt
the build. `dci.json` records the same override under `today_note` rather than
`today_reason`, so the three properties do not even agree on the key name.

### `documentation_only_keys` — 56 entries in `common.json`

**Eight of the 56 are declared documentation-only but ARE present in the
implementation as quoted literals.** Five are genuinely read by rules
(`allowed_structure_percentages` at `claim_gate.py:2334,2757`;
`allowed_thresholds` at `2758`; `elevation_anchor` at `2312`; `domain` at `3925`;
`repo` at `316`) — their own justifications say so, so the declarations are
redundant and misleading rather than deceptive: they advertise as documentation
something the gate enforces. Three (`allowlist`, `and_the_figures_are_still_banned`,
`measured_at`) are read by **nothing** and are exempted from the OWED count only
because their names appear inside the audit's own bookkeeping tables
(`claim_gate.py:365`, `389`, `478`). The remaining 48 are correctly classified.

---

## (c2) The allowlisted quotations, against the sources they name

Every externally-sourced allowlist entry was fetched against its named publisher,
to a **file**, then grepped in both the raw HTML and a tag-stripped rendering —
because the question is byte-exact verbatim presence, and a quoted sentence can
be split by markup. Every fetch carries a positive control; a fetch whose control
returned zero was retried, not reported.

**Eleven entries tested. Every factual assertion — hashes, URLs, dates, byte
counts, line numbers, verbatim text — checks out. One piece of REASONING is
false, and it is wrong in the permissive direction.**

| entry | verdict |
|---|---|
| GCI-1 EPA sampling sentence, three named locations | **TRUE** |
| GCI-2 EPA no-certification sentence + page date 2026-01-14 | **TRUE**; the "exactly once across 54 docs" claim **NOT FULLY TESTED** |
| GCI-3 EPA mycotoxins sentence + the "in some cases" hedge | **TRUE** |
| GCI-4 CDC `…people who are infected`, 403, 2026-05-08, third denominator, empty parent | **TRUE, all four sub-assertions** |
| LGM-1 Xcel PDF sha256, lines 143-145, verbatim, garages | **PARTIALLY TRUE — the truncation rationale is FALSE and inverted** |
| DCI-1…DCI-4 scare quotes / reported hypothetical speech | **TRUE**, one page each |
| GCI-5 `The guidance here says` + its own deletion condition | entry **TRUE**; the engine change has **NOT landed** |
| LGM-3 `Sources What the data says According to the EPA` duplicate | **TRUE** |

### GCI-1 / GCI-2 / GCI-3 — the EPA quotations

All three EPA pages fetched **HTTP 200**, each with a passing `mold` control.

```
/usr/bin/grep -c "In most cases, if visible mold growth is present, sampling is unnecessary." epa_*.txt
epa_sampling.txt:1   epa_briefguide.txt:1   epa_schools_ch3.txt:1     (11 other EPA files: 0)
/usr/bin/grep -c "EPA does not have a certification program for mold inspectors or mold remediation firms." epa_*.txt
epa_who.txt:1                                                        (13 others: 0)
/usr/bin/grep -c "Molds produce allergens (substances that can cause allergic reactions), irritants, and in some cases, potentially toxic substances (mycotoxins)." epa_*.txt
epa_health.txt:1   epa_briefguide.txt:1                              (all others: 0)
```

Byte sizes and controls: `samplingtesting-mold-necessary` 56,711 raw / 3,612
stripped, 91 `mold`; `brief-guide` 79,311 / 17,676, 152; `schools…chapter-3`
101,393 / 35,959, 194; `who-can-test…` 57,106 / 3,863, 89;
`can-mold-cause-health-problems` 56,398 / 3,798, 37.

The sampling sentence **is** the first sentence of the answer on all three pages,
which is more than the config claimed (it claimed it only for the FAQ page).
Surrounding paragraph, verbatim: *"In most cases, if visible mold growth is
present, sampling is unnecessary. Since no EPA or other federal limits have been
set for mold or mold spores, sampling cannot be used to check a building's
compliance with federal mold standards."* The no-certification page reads `Last
updated on January 14, 2026` — the asserted date. The mycotoxins hedge `in some
cases, potentially toxic` is present verbatim.

**`exactly once across 54 EPA mold documents` — NOT FULLY TESTED.** I did not
replicate the 54-document sweep. **10 other EPA mold pages were checked, all
HTTP 200, each with a passing `mold` control (27–194 hits), and the sentence
appears on none of them.** Nothing contradicts the claim; my sample does not
prove it. Two URLs returned **HTTP 404** and were correctly identified as failed
fetches rather than counted as zeros.

### GCI-4 — the CDC hantavirus denominators, all four sub-assertions TRUE

**The 403 is real.** `curl` with a browser UA against
`https://www.cdc.gov/hantavirus/hcp/clinical-overview/hps.html` → **HTTP 403**,
426-byte body; parent → **403**, 414 bytes. The config's stated reason for going
through Wayback is accurate.

Wayback capture **20260917053034**, **HTTP 200, 58,893 bytes**, positive control
**116** `hantavirus`. *(First attempt failed its own control at `hantavirus=0`
because the body was gzip without `--compressed`; retried rather than reporting
the zero.)* Searching **numerically first** as the trap demands, then reading
every hit's full sentence:

```
raw / stripped:  '4 in 10' 1/1 · 'nearly 4' 1/1 · 'fatal' 3/3 · 'percent' 1/1 · '38' 1/0
```

> `It's important for people with HPS to begin treatment as early as possible to improve their chances of recovery.` **`HPS is fatal in nearly 4 in 10 people who are infected.`**

Verbatim, with the word **infected**. The other `fatal`/`percent` hits are
unrelated (`Autopsies performed on fatal cases…`, an `80 percent survival rate`
for ECMO). Page metadata: `cdc:last_published" content="2026-05-08T17:53:16Z"` —
the asserted date.

**The third, narrower denominator exists, verbatim**, on
`cdc.gov/hantavirus/about/index.html` (Wayback 20260918033010, HTTP 200, 53,277
bytes, control 107 `hantavirus`): *"HPS can be deadly. **Thirty-eight percent of
people who develop respiratory symptoms may die from the disease.**"* So all
three denominators genuinely differ — *infected* (brief), *develop respiratory
symptoms* (About), *develop HPS* (the site's own, now removed).

**The parent page carries no fatality figure — TRUE.** Wayback 20260726180547,
HTTP 200, 49,721 bytes, control 102 `hantavirus`, 5,065 stripped characters read
in full: `4 in 10`=0, `Thirty-eight`=0, `38`=0, `percent`=0, `%`=0, `fatal`=0,
`mortality`=0, `die`=0.

**The correction landed cleanly on the property**, checked against the recorded
trap (a sweep for `who develop HPS` once missed the same claim with the disease
spelled out):

```
GCI public/:  '4 in 10' -> 1 file | 'who are infected' -> 1 file
              'who develop HPS' -> 0 | 'Thirty-eight' / '38%' / '38 percent' -> 0
```

All five occurrences on `rodent-insulation-hantavirus-greeley.html` read `people
who are infected`, including the spelled-out-disease variants. No residual
wrong-denominator phrasing survives under any spelling.

**But an unsupported attribution sits inside the same registry entry, uncleared.**
`CDC_HPS_CLINICAL_OVERVIEW` (`greeleycoloradoinsulation.com/_shared_components.py:1102`)
welds two propositions and attributes both to the clinician brief:

```python
stat='the deer mouse (Peromyscus maniculatus) is the primary U.S. reservoir for the Sin Nombre
      strain of hantavirus responsible for Hantavirus Pulmonary Syndrome, and HPS is fatal in
      nearly 4 in 10 people who are infected',
```

The second clause is verbatim CDC. **The first is not on the cited page.** Counts
in the brief's stripped text: `Peromyscus`=0, `Sin Nombre`=0, `reservoir`=0,
`deer mouse`=1. What CDC actually says is *"Each hantavirus has one primary
rodent that carries the disease. The most common hantavirus that causes HPS in
the U.S. is spread by the deer mouse."* The strain name, the Latin binomial and
the word "reservoir" are the site's additions. A live body sentence still reads
*"The CDC's clinical overview identifies Peromyscus maniculatus as the primary
United States reservoir for the Sin Nombre strain"* — pointing at the **parent**
page, which contains `Peromyscus`=0 and `deer mouse`=0. `quote=False` keeps R1
silent on it, so this is not a false allowlist justification — **it is an
unsourced attribution living inside the entry the config declares clean, and the
pass's source-label correction reached the Sources block and the FAQ but not that
body sentence.**

### LGM-1 — the Xcel PDF: everything factual checks out, the reasoning does not

**The hash matches exactly. The source has not moved under the citation.**

```
HTTP 200, content-type: application/pdf, 125,996 bytes, PDF 1.7, 5 pages
$ shasum -a 256 xcel_insulation.pdf
1e683803bbddd998b1c988132583ddea3415d0bba55086bc7fe080cf20a2c271     <- identical to the recorded artifact
$ pdftotext -layout  ->  14,045 bytes, 214 lines          <- byte count matches the provenance record exactly
$ /usr/bin/grep -n "This product excludes" xcel_layout.txt
143:This product excludes new residential construction, new residential additions, insulation of
144:doors, garages, sheds, workshops, below-ground basements, mobile homes, projects with pre-
145:improvement R-values of R-16 or greater, and residential properties with more than four units.
```

Lines 143-145 as asserted; joining them yields a byte-exact match to the config
string (`EXACT MATCH: True`); `garages` is on line 144. The page quotation
(`insulation-garage-longmont.html`, the only page carrying it, on three surfaces)
is a **verbatim prefix** of the source, truncating after `mobile homes`.

**The two dropped exclusions:** `projects with pre-improvement R-values of R-16
or greater`, and `residential properties with more than four units`.

**The config's stated reason is false and inverted.** It asserts the truncation
*"can only make the list more permissive, never more flattering to the reader's
eligibility."* Those two halves contradict each other, and the second is wrong.
Dropping items from a printed **exclusion** list makes the list shorter, so fewer
readers find themselves on it. A homeowner whose attic already sits at R-16 or
better, or who owns a five-unit building, reads the truncated quotation, does not
see their situation named, and concludes they may qualify — when Xcel's write-up
excludes them by name. **A more permissive-looking exclusion list IS more
flattering to eligibility; that is the same direction, not the opposite one.**

Stated fairly: the page's own claim — that garages are excluded — is fully
supported, `garages` sits inside the retained prefix, and the ellipsis is visible
rather than silent. The quotation is not misleading about what the page asserts.
**The defect is in the allowlist's reason, which tells a future reviewer that
this truncation is structurally safe in a direction it is not** — and anyone
relying on that sentence to wave through a longer truncation of the same list
would be relying on an inverted rule.

### DCI-1…DCI-4 and GCI-5 — the scare quotes

All four DCI entries are on the file each names, and **each appears on exactly
one page** — so no entry is broader than its justification.

| entry | file | bytes | pages |
|---|---|---|---|
| `The guidance here says "not yet" as often as it says "yes,"` | `public/about.html` | 54,553 | **1** |
| `someone at your door says they "noticed your roof"` | `public/choosing-denver-insulation-contractor.html` | 80,366 | **1** |
| `If a quote says "blown-in cellulose"` | `public/insulation-dense-pack-cellulose.html` | 108,724 | **1** |
| `If a quote says "tape the joints"` | `public/insulation-duct-sealing.html` | 114,441 | **1** |

Full sentences, verbatim: *"A referral service that routes everyone regardless is
a lead mill. The guidance here says 'not yet' as often as it says 'yes,' because
the referral is only worth making when the work is worth doing."* · *"The
post-hailstorm pattern — someone at your door says they 'noticed your roof' and
can quote your attic today only — is a storm-chaser model applied to
insulation."* · *"If a quote says 'blown-in cellulose' for a wall without naming
a density, that is the number to ask for."* · *"Ducts get sealed with mastic …
If a quote says 'tape the joints' and does not say mastic, ask which tape…"*

**No named publisher appears in any of the four.** DCI-3/DCI-4 are a genuine noun
collision — `quote` meaning *price estimate*, not *quotation*. The assertions
hold. GCI-5 is the same sentence on GCI `about.html`, 1 file, 52,405 bytes, same
verdict.

**GCI-5's own deletion condition is NOT met — do not delete it.** The config says
to delete the entry when R1 half B starts requiring a recognised publisher.
That change has not landed. `claim_gate.py:1449-1461`, R1 half B in full:

```python
        for skey, loc, sent in ctx.pool(art):
            for m in qre.finditer(sent):
                pre = sent[max(0, m.start() - 40):m.start()]
                v = which_any(pre, verbs, ci=True, word=False)
                if not v:
                    continue
```

**There is no publisher test** — the only gate is an attribution verb inside a
40-character lookback, exactly the behaviour the config calls defective.
Corroborating: `common.json`'s `R1` carries no `recognised_publishers` and no
`requires_publisher_named`, and `SENTENCE_SCOPED_KEYS["R1"]`
(`claim_gate.py:361`) is still `("attribution_verbs", "quotation_allowlist",
"correction_markers")` — R1's schema does not even admit a publisher key.
`recognised_publishers` is registered for **R5** only. What did land is a
different change: the `seen_b` de-duplication at `1437-1448`, whose comment names
this exact GCI sentence as having produced four character-identical findings.
That collapses 4→1; it does not clear the hit. **And the stated blocker is gone**
— the config says the engine fix was skipped because `claim_gate.py` had
uncommitted changes from another session; it is now clean in git, so the reason
no longer applies and the fix was simply never made.

### LGM-3 — the duplicate EPA hit

**TRUE.** The string does not exist in the raw HTML at all (0 files) — it is
manufactured by tag-stripping, and in the stripped text it matches **exactly one
page** in the whole tree. The markup:

```html
    <p class="eyebrow">Sources</p>
    <h2>What the data says</h2>
    <p class="cited-stat">According to <a href="https://www.epa.gov/asbestos/protect-your-family-asbestos-contaminated-vermiculite-insulation" ...>the EPA</a>, &ldquo;you should assume that vermiculite insulation is from Libby and treat the material as if it contained asbestos…&rdquo;</p>
    <p class="cited-stat">According to <a href="https://cdphe.colorado.gov/apcd-asbestos-support" ...>the Colorado Department of Public Health and Environment…</a>, Colorado Air Quality Control Commission Regulation 8, Part B sets requirements…</p>
```

There is exactly **one** quoted span in the block; the second `cited-stat` is an
unquoted paraphrase carrying no quote glyph, so half B never fires on it. The
mechanism is confirmed in code — `f_inside` (`claim_gate.py:1479-1485`) tests
`h.sentence[:60] in t`, and here that prefix begins `Sources What the data says
According to the EPA , "you shoul`, which is not a substring of the cited-stat
text. The half-A hit resolves to `EPA_ZONOLITE`, `quote=True` with a complete
four-field provenance record. **One rendered quotation counted twice, correctly
scoped to the heading prefix.**

---

## (d) Review dates: my own derivation against what each site publishes

Derivation built from scratch (`/tmp/gate-close/r6/dates/`): for every
`public/*.html`, walk `git log -- <path>` newest to oldest and compare
**consecutive blob versions** with `git cat-file -p`, so the introducing commit
is exact. Three measures — **M1** normalises ISO and long-form dates out of both
sides; **M2** additionally drops JSON-LD, `<style>`, and comments but keeps JS
string literals; **M3** strips scripts and styles entirely and compares body text
only. All three normalise the review-date **label** as well as its value.

**That last point was load-bearing.** `f3768f5` renamed LGM's footer marker
`Last reviewed:` → `Last updated:` on all 48 pages *in the same commit that set
the dates*. Normalising only the date value left all 48 LGM pages looking
content-changed on 2026-09-18 — **the date justifying itself**, the exact failure
this derivation exists to avoid. Normalising the label too drops LGM to 42, and
those 42 trace to genuine content commits.

The four surfaces were found by reading samples, not assumed: visible footer
(`Last reviewed:` on DCI 74/75 and GCI 38/38, `Last updated:` on LGM 48/48),
`<time datetime>`, JSON-LD `dateModified`/`datePublished`, and sitemap
`<lastmod>`. Coverage: footer present on 160/161 pages; sitemap entries DCI 73,
LGM 47, GCI 37.

| | DCI | LGM | GCI |
|---|---|---|---|
| html pages | 75 | 48 | 38 |
| **A.** published date precedes first git appearance | **0** | **0** | **0** |
| **B.** published date later than 2026-09-18 | **0** | **0** | **0** |
| **C.** the four surfaces disagree | **0** | **0** | **0** |
| **D.** dated today but not changed today (reader-facing) | **0** | **4** | **0** |
| **E.** published date older than true content change | **0** | **0** | **2** |
| **B-ext.** impossible `datePublished` (gate cannot see) | **9** | **0** | **1** |
| reported R8 | RAW 1 ADJ 0 PASS | RAW 1 ADJ 0 PASS | RAW 14 ADJ 0 PASS |

**LGM's 31 impossible dates: confirmed exactly, and CLOSED.** LGM's first commit
is 2026-08-11 (`5b50dbd`); 2026-08-05 is six days earlier. My first grep returned
0 and I suspected the pattern before the content — correctly, the marker had been
renamed:

```
$ git grep -o -h 'datetime="[0-9-]*"' f3768f5^ -- 'public/*.html' | sort | uniq -c | sort -rn
  31 datetime="2026-08-05"     <- exactly the 31 reported
  15 datetime="2026-08-11"
   2 datetime="2026-09-01"
   1 datetime="2026-08-23"
$ git grep -o -h 'datetime="[0-9-]*"' HEAD -- 'public/*.html' | sort | uniq -c | sort -rn
  47 datetime="2026-09-18"
   1 datetime="2026-09-02"
   1 datetime="2026-08-23"
```

**Zero remain. This was the pass's largest correction and it is real.**

**Positive controls, because these zeros need denominators.** The tightest A
margins are three pages at exactly **+0 days** (DCI `r-value-needed-calculator-embed-code.html`,
GCI `404.html`, GCI `about.html`) — pressed against the boundary, none negative.
For B, the maximum date value anywhere across all 161 pages and all surfaces is
exactly `2026-09-18` — a real ceiling, not a vacuous one. For C, perturbing one
surface to `1999-01-01` and re-running the same comparison flags 69/44/34 pages
(dateModified) and 73/47/37 (sitemap): the test is not inert.

### The disagreements

**DCI 9 + GCI 1 impossible `datePublished`, structurally invisible to R8.**
`claim_gate.py:3581` reads
`claimed = [(k, v) for k, v in sorted(dates.items()) if k != "ld:datePublished"]`,
and parts (a), (b) and (c) all iterate `claimed`. Nine DCI pages publish
`datePublished` of 2026-05-05/06 — **35–36 days before the repo's first commit
(2026-06-10)**: `attic-mold-denver`, `freeze-thaw-cycles-denver-insulation`,
`front-range-wind-insulation-denver`, `ice-dams-denver` (2026-05-05),
`is-my-attic-insulation-failing`, `knob-and-tube-insulation-denver`,
`r-value-altitude-denver`, `upstairs-hot-summer-cold-winter-denver`,
`vermiculite-insulation-denver`; GCI `knob-and-tube-insulation-greeley.html`
publishes 2026-08-31 against a first appearance of 2026-09-01. **This also closes
`dci.json`'s open anomaly** recorded as `{"page": "unidentified", "date":
"2026-05-05"}` — it is `public/ice-dams-denver.html`, line 41 at HEAD.

**LGM's 4 over-dated pages, and R8 has no sub-test that can ever see them.**
`cellulose-vs-fiberglass-insulation-longmont.html`, `contact.html` and
`privacy.html` (true last reader-facing change 2026-09-02) and
`insulation-garage-longmont.html` (2026-09-10) all publish 2026-09-18 on every
surface. `contact.html` is the clean proof — its **entire** diff under `f3768f5`:

```diff
-        … Last reviewed: <time datetime="2026-08-05">August 5, 2026</time>.
+        … Last updated: <time datetime="2026-09-18">September 18, 2026</time>.
```

and its only other 2026-09-18 commit touches nothing but JSON-LD `knowsAbout`
strings. **This is the exact situation GCI pinned 11 pages to avoid, and LGM
stamped instead. The two properties are running opposite doctrines on identical
facts.** R8's four parts test impossible, future, disagreeing and stale — there
is **no over-dating sub-test**, so a page may claim today's date with zero
content change and pass cleanly. LGM has no `pinned_pages`, so nothing flagged.

**GCI's 2 genuinely stale pages, raised and then suppressed.**

| page | published | last **prose** change | gap | suppressed by |
|---|---|---|---|---|
| `public/404.html` | 2026-08-05 | **2026-08-17** (`f59ce90`) | 12d | `exempt_pages` |
| `public/about.html` | 2026-08-07 | **2026-08-27** (`8756d8f`) | 20d | `pinned_pages` |

Both are reader-visible `<p>` prose, not schema, not comments, not JS:

```diff
# f59ce90 -> 404.html
-          A Greeley and Weld County referral service … Family operated, locally focused.
+          A Greeley and Weld County referral service that connects homeowners with local insulation contractors.
# 8756d8f -> about.html
-    form hands your project to a local pro who does retrofit work in your area.
+    form sends your details to us and to a local pro who does retrofit work.
```

The `about.html` line is a **material disclosure change — where the visitor's
data is sent** — and the page has published 2026-08-07 ever since. The config's
own standing instruction covers it: *"If a future pass changes any of these
pages' VISIBLE copy, REMOVE its pin and move its date — do not extend the pin to
cover it."* Both changes already happened.

### DCI's R8 hold note is stale and printed into every run

The gate prints, every run: *"KNOWN-OPEN hold in force: DCI-D-003 … Debt measured
at 70 of 72 pages; sitemap shows 70 x 2026-08-24 while content was corrected
through 2026-09-11."* Measured at HEAD:

```
$ /usr/bin/grep -o '<lastmod>2026-08-24</lastmod>' public/sitemap.xml | wc -l
       0                                    # of 73 total lastmod entries
$ /usr/bin/grep -o '<lastmod>[0-9-]*</lastmod>' public/sitemap.xml | sed 's/<[^>]*>//g' | sort -u
2026-09-10
2026-09-18                                  # distinct values: 2
```

It **was** exactly true at `4b10e05^` (`70 2026-08-24`, verified) and was closed
the same day. **DCI's dates are not substantially wrong and R8 is not blind on
DCI** — I will not say so, because I measured otherwise: 73 of 73 DCI sitemap
entries are at or after the page's last prose change. `R8 RAW 1 / ADJ 0 PASS` is
substantively correct. The defect is that a reader is told DCI has 70 stale
sitemap entries when it has zero.

### Two further gate bugs in R8, found while deriving

1. **`time[datetime]` takes the first `<time>` in document order.** Each
   `privacy.html` carries two — a policy *Effective date* and the review date —
   and the gate reads the effective date as the review surface. That is the sole
   source of DCI's and LGM's only RAW finding: both `privacy.html` pages are in
   fact internally consistent. **DCI RAW 1 and LGM RAW 1 are false positives**,
   cleared to ADJ 0 by the right outcome through the wrong mechanism.
2. **`R8.footer_marker` is configured `"Last reviewed:"` and LGM emits `"Last
   updated:"` on all 48 pages.** Measured:

```
LGM   "Last reviewed:"  0    "Last updated:" 49   [control "Longmont" 2424]
GCI   "Last reviewed:" 38    "Last updated:"  1
DCI   "Last reviewed:" 74    "Last updated:"  0
```

   `footer_marker` is the code path that catches a plain-text review date with no
   `<time>` element (vector R8-H1). On LGM that path is **dead**. Inert today
   because LGM carries `<time>` everywhere — live the moment one page does not.

---

## (e) Rebate figures, and the GCI Weatherization limits

### The standing exception survives, exactly

Positive control: `Greeley` = 1584 occurrences in GCI `public/`.

```
RAW $70,000 occurrences (all file types, public/)   = 10
RAW $99,920 occurrences                             = 10
preceded-by-digit check for 70,000 (substring trap) =  0
anchored word-boundary count for $70,000            = 10
anchored word-boundary count for $99,920            = 10
```

| file | count (each figure) |
|---|---|
| `public/insulation-rebate-hub.html` | 3 |
| `public/index.html` | 2 |
| `public/insulation-cost-calculator-greeley.html` | 2 |
| `public/insulation-greeley.html` | 2 |
| `public/insulation-rebate-eligibility-checker.html` | 1 |

**Exactly 10 each, as reported.** Both co-occur on the same 10 lines. Context,
verbatim, `insulation-rebate-hub.html:1003`:

> "Eligibility runs to the highest of 60% of state median income, 80% of area
> median income, or 200% of the federal poverty level. On the Colorado Energy
> Office's own WAP income eligibility chart that currently works out to
> **$70,000 for a single-person Weld County household** and **$99,920 for a
> household of four** (checked September 10, 2026)."

and `insulation-greeley.html:1139`: *"The state Weatherization Assistance Program
does attic, floor, and wall insulation **at no cost** for income-qualified
households…"* All 10 are income-eligibility thresholds for a free government
program; **zero describe a payout**, and the copy explicitly contrasts the
program with rebates. The four JSON-LD `FAQPage` instances are **included in** the
10, not additional. Non-HTML surfaces carry zero (`llms.txt` 0, `sitemap.xml` 0,
`robots.txt` 0; positive control `insulation` in `llms.txt` = 95). Both figures
appear **10 times each in the generator source** (`_generate_calculator_pages.py`,
`_generate_rebate_hub.py`, `_area_pages.py`, `_generate_homepage.py`,
`_shared_components.py`), so a regen restores rather than strips them.

### No rebate payout DOLLAR figure anywhere

| property | positive control (`insulation`) | RAW `$` amounts | adjudication |
|---|---|---|---|
| DCI | 14237 | **0** | 5 bare `$` chars, all non-numeric placeholders (`"Insulate attic — $X"`, `cost ($)`, `'$' + Math.round(n)`) |
| LGM | 8643 | **8** | `$1.50`×3, `$3.50`×2, `$3.00`, `$300`, `$1,200` — all **install cost rates** in one JS comment block documenting their own removal |
| GCI | 5365 | **20** | the standing exception, above |

Alternative encodings are zero on all three: `&#36;`, `&dollar;`, `&#x24;`,
`$`, `USD` = 0.

**LGM's named regressions are all clear.** Positive control `Efficiency Works` =
793 in `public/`:

```
$1.16 in public/: 0    bare 1.16: 0
$0.77 in public/: 0    bare 0.77: 0
$2,000 in public/: 0   bare 2,000: 0
```

The per-square-foot payout schedule and the Boulder County EnergySmart cap are
gone from output. They survive in `_shared_components.py` **only inside Python
comments and docstrings recording their removal** (lines 508, 516, 592, 614,
2155), which cannot reach HTML. **Not one regen away from returning.** One
substring trap caught and reported: `_area_pages.py:88` matched `0.77` but reads
`pre1990_share=0.779`, a census share.

Bare-digit sweep, independent of the `$`-anchored pattern (DCI 52 distinct
non-year numerals in rebate sentences, LGM 36, GCI 35): all benign — square
footages, the Xcel phone number `800-895-4999`, Public Law 119-21, CSS gradient
stops, CFM50 qualifying thresholds. **No bare-digit payout on any property.**

### What IS live: percentage-of-cost payouts, and a ruling conflict

The dollar sweep is clean. **Percentages stating what a program pays are
pervasive**, in output and in generator source:

- **GCI `75%` — 114 occurrences across 19 files**, every one a rebate
  percentage-of-cost. *"Atmos Energy **pays 75% of project cost** on attic
  insulation where existing insulation starts below R-20"*; a rendered table at
  `insulation-rebate-hub.html:996` reads `<td>75% of project cost, capped</td>`.
- **DCI `25%` — 159 occurrences**, all the Whole Home Efficiency Bonus: *"a **25%
  bonus on all standard rebates** when three qualifying measures…"*
- **LGM — 5**: *"capped at 100% of project cost"*, *"50% of project cost up to an
  annual cap the county publishes"*.

**Two rulings are in force and they do not agree.** The repo's own recorded
Director ruling, at `greeleycoloradoinsulation.com/_shared_components.py:462-478`,
verbatim:

> "no per-measure rebate **DOLLAR AMOUNT** may enter any page from any program —
> no cap, maximum, flat amount, total, range or 'up to'. … **WHAT IS NOT COVERED
> BY THIS BAN**, and must not be stripped by a future sweep reading only the
> headline: … **the 75%/50% structure percentages WHERE THEY ALREADY APPEAR —
> those may stay, but a new one may never be added.**"

The brief given to this review states the ban more broadly — "any figure stating
what a rebate, incentive or bonus pays". **The repo's ruling is the retrievable
primary source, it is dated and specific, and it explicitly anticipates and
forbids exactly the sweep the broader phrasing would license.** On that reading
the portfolio is clean and `allowed_structure_percentages` correctly encodes it.
I am recording the conflict rather than resolving it, with one exception that is
a defect under **either** reading:

**DCI's 159 × "25% bonus on all standard rebates" is exempted by nothing.**
`dci.json`'s `allowed_structure_percentages` lists `75%`, `50% of project cost`,
`capped at 100% of project cost`, `30% of project cost` — and DCI's `public/`
contains **`75%` = 0 and `30% of project cost` = 0**. The allowlist exempts three
figures that do not exist on the property while the one that exists 159 times is
registered only as an *expected claim cluster* (`dci.json:442-456`,
`"id": "whe_25pct"`), tracked for attribution and never tested as a payout.

### `allowed_thresholds` justifications, each tested

| entry | stated reason | TRUE? |
|---|---|---|
| GCI `$70,000` / `$99,920` | eligibility thresholds, free program, not payouts | **TRUE** — verified above; the config's stated occurrence counts of 10/10 match my measurement exactly |
| LGM `$1.50/$3.00/$3.50/$300/$1,200` | installed cost rates, 8 occurrences, all in JS comments | **TRUE** — count of 8 matches exactly; read at `attic-insulation-cost-calculator-longmont.html:1395-1403` |
| LGM `15% / 25% / 33% / 50%` | Efficiency Works air-sealing tier thresholds, measured reduction not amounts | **TRUE** — output reads *"Efficiency Works publishes the current amount for each on its own rebates page"* |
| GCI `20%` / `20 percent` | CFM(50)/CFM(25) blower-door qualifying condition | **TRUE** |
| all three `allowed_structure_percentages` | "structure percentages kept under Ruling 2" | **NOT a threshold claim** — these state what a rebate pays; they are licensed by the Director ruling quoted above, not by being thresholds |

### A gate blind spot the repo documented against itself

`common.json`'s R3 `dollar_pattern` is `\$[0-9][0-9,.]*` — `$`-anchored. GCI's
`insulation-cost-calculator-greeley.html:1411-1416` carries a shipped JS comment
saying so: *"It survived the 2026-09-10 rebate-figure strip because the
acceptance gate is anchored on '$' and these were bare digits."* I swept bare
digits manually and found nothing live. The gate still cannot.

---

## (f) The GCI territory split and LGM's restriction copy

**Both recorded traps reproduced before anything was measured:**

```
naive  /usr/bin/grep -roiI 'ault'  = 334      <- default/fault contamination (+175)
corr.  /usr/bin/grep -rowI 'Ault'  = 159      <- the locality
'La Salle' = 0  (FALSE ABSENCE)   |  'LaSalle' = 159
```

Positive controls: GCI `Greeley` = 1584 occurrences / 42 files; LGM `Longmont` =
2424 / 52; a nonsense token returns 0 in both.

**Two further traps hit and recorded so the next pass does not pay for them:**
LGM's corpus spells the ampersand **both ways** — `Longmont Power & Communications`
= 195 and `Longmont Power &amp; Communications` = 195 (raw `&` inside JSON-LD,
entity in HTML body); four restriction probes returned 0 purely from this.
And `grep -oE '.{90}X.{90}'` returns **nothing** when fewer than 90 characters
follow the match on the line — three probes looked like absences until re-run
with `.{0,120}`.

### GCI: no Atmos attribution on the three Xcel-gas towns — CONFIRMED

Raw line-level co-occurrence of Atmos with Johnstown/Milliken/Severance: **148
lines across 38 files**. At the correct unit — the sentence — **87 instances / 35
distinct texts**, all read:

- **18 distinct** are contrastive split sentences (Atmos → Greeley/Evans/Eaton,
  Xcel → the three). Correct.
- **14 distinct** are explicit negations: *"Xcel Energy is the natural gas utility
  in Johnstown, not Atmos Energy."* (`insulation-johnstown.html:986, 1020`);
  *"Not Atmos Energy."* (`insulation-severance.html:29, 1138`); *"Atmos does not
  serve Johnstown, Milliken or Severance."*
- **3 distinct** are shipped JS/HTML comments narrating the 2026-09-08 correction.

**Zero sentences attribute Atmos to any of the three.** JSON-LD checked at
**object** level, not sentence level, because sentence splitting cannot see
across a JSON boundary: 240 `ld+json` blocks, 0 parse failures, 78 co-occurring
objects reducing to 9 distinct texts, all clean; 71 of the 78 are the sitewide
`Organization.description`, which splits territory correctly. Every `areaServed`
object enumerated: the 9-town lists are service-area lists and **no `Service`
object names any utility at all** (17 Service objects, all clean).

### The qualifiers, exact

**Johnstown carries NO qualifier — CONFIRMED.** Every probe zero, against a live
instrument (the same grep style returns 145 and 144 for the other two towns):

```
most of Johnstown 0 | most locations in Johnstown 0 | parts of Johnstown 0
portions of Johnstown 0 | most areas of Johnstown 0 | much of Johnstown 0
```

An exhaustive 1-to-4-word left-context histogram over all 307 Johnstown
occurrences leads with `natural gas utility in Johnstown` (84) and `is Xcel
Energy in Johnstown` (43): no territorial qualifier anywhere. The absence is
deliberate and sourced — `insulation-johnstown.html:1029`: *"According to the
Town of Johnstown utility service provider list, the natural gas provider listed
for Johnstown is Xcel Energy, **with no service-area qualifier attached to the
gas row.**"*

**Milliken is exactly `most of Milliken` — CONFIRMED, 145, zero variants.**

```
most of Milliken 145 | most of the Milliken 0 | most areas of Milliken 0
most locations in Milliken 0 | parts of Milliken 0 | portions of Milliken 0
```

**Severance is exactly `most locations in Severance` — CONFIRMED, 144, zero
variants.** The single `For most Severance` is *"For most Severance
**homeowners** no insulation work is warranted yet"* — about people, not
territory.

### The Windsor/LaSalle/Ault hedge retains both halves — CONFIRMED

There are **two** hedge forms, both on all three pages. Verbatim, HEDGE A
(`insulation-windsor.html:986`, `insulation-lasalle.html:986`,
`insulation-ault.html:986`):

> **Where Atmos Energy serves the home,** it rebates attic insulation at 75% of
> project cost where existing insulation starts below R-20, and rebates air
> sealing that documents a 20% leakage reduction, with Atmos publishing what each
> measure currently pays on its own rebate page — **Atmos service is not
> confirmed for every town in this area, so check your own utility before
> counting on it.**

Opening condition = `Where Atmos Energy serves the home,`. Closing
non-confirmation = `Atmos service is not confirmed for every town in this area,
so check your own utility before counting on it.` HEDGE B (line 1020 on all
three) closes with: *"Atmos gas service is confirmed for some towns in this area
and not formally confirmed for others, so verify your own service before
counting on the rebate."*

The XOR test, which is the actual question:

```
A_open  'Where Atmos Energy serves the home'                       -> 3 files
A_close 'Atmos service is not confirmed for every town in this...' -> 3 files
B_close 'Atmos gas service is confirmed for some towns...'         -> 3 files
comm -3 A_open A_close  ->  (empty)      # no page carries one half only
```

**Pages carrying the full hedge: 3. Pages carrying only one half: 0.** The prior
pass's "missing clause" does not reproduce — it was a pattern artifact, as
warned. One note for the owner: HEDGE B's opening is a *framing* sentence, not a
grammatical condition, and its rebate assertion stands bare for four sentences
before the non-confirmation lands. Both halves present; not adjacent.

### A discrepancy between the brief and the property

The brief states Atmos serves **Greeley, Evans, Eaton, Windsor, LaSalle, Ault**.
The site does not assert that. Measured:

| town | briefed | sentences w/town | co-occurring with Atmos (files) |
|---|---|---|---|
| Greeley | ATMOS | 1290 | 180 (38) |
| Evans | ATMOS | 305 | 142 (38) |
| Eaton | ATMOS | 301 | 143 (38) |
| **Windsor** | ATMOS | 167 | **0 (0)** |
| **LaSalle** | ATMOS | 158 | **1 (1)** |
| **Ault** | ATMOS | 158 | **1 (1)** |

The property affirms Atmos for Greeley/Evans/Eaton only and covers
Windsor/LaSalle/Ault **exclusively through the conditional hedge, which never
names them**. The site is more conservative than the brief. That is a
Director-level reconciliation, not a defect I can adjudicate — but a reviewer
told to confirm "Atmos serves six towns" against this property would find three.

### LGM: the Efficiency Works restriction is intact — CONFIRMED

The sitewide form, **91 occurrences across 47 files**:

> A separate program, Efficiency Works, pays its own rebate to electric customers
> of Longmont Power & Communications, the city's own municipal utility —
> **available only on the portion of Longmont LPC actually serves, not
> citywide.**

54 distinct restriction sentences total. The strongest,
`spray-foam-vs-blown-in-comparator-longmont.html:1380`:

> Xcel Energy is the gas utility across all four towns this site covers;
> **Efficiency Works is open only to residential electric customers of Longmont
> Power &amp; Communications, which is part of Longmont and not Lafayette,
> Louisville or Niwot.**

and `index.html:974`: *"applies only to residential electric customers of
Longmont Power & Communications — … roughly 61% of Longmont by area, **and none
of Lafayette, Louisville, or Niwot, which are confirmed Xcel-electric.**"*

**The decisive coverage test:**

```
files mentioning Efficiency Works              : 48
files carrying an LPC-electric-only restriction: 48
comm -23 ew_files ew_union  ->  (empty)
```

**There is no file anywhere in LGM that mentions Efficiency Works without a
restriction attached.** Nothing was partially swept. The "only LPC electric"
half is on 48 files; the explicit three-town exclusion is on 2
(`index.html`, `spray-foam-vs-blown-in-comparator-longmont.html`).

### Lafayette / Louisville / Niwot carry no EW attribution — CONFIRMED, with one false claim

Denominators: Lafayette 448 occurrences / 50 files; Louisville 453 / 50; Niwot
462 / 50. Sentence-level EW × town co-occurrence: 51 instances / 8 distinct, all
read; seven are exclusions or restrictions and one is a splitter artifact across
a JSON object boundary, confirmed separate by the object walker.

**The three town pages do contain the string, twice each:**

```
file                          total  ld+json  other_js  comment  VISIBLE_BODY
insulation-lafayette.html         2        2         0        0            0
insulation-louisville.html        2        2         0        0            0
insulation-niwot.html             2        2         0        0            0
```

Both instances on each page are the sitewide `Organization.description` inside
`ld+json`, which carries its own restriction rider inline. Visible body = 0;
titles and meta name only Xcel. **No attribution to the three towns on any
surface.**

**But `index.html:1127` states, verbatim:** *"Lafayette, Louisville, and Niwot are
confirmed Xcel-electric, so their pages use the single-utility Xcel rebate shape
— **Efficiency Works isn't mentioned on those pages because it doesn't apply
there.**"* It **is** mentioned on those pages, twice each, in JSON-LD — invisible
to readers, visible to crawlers and LLM ingest. The substance is safe
(self-restricting boilerplate); the sentence is false as written, and **no gate
rule catches it** (LGM scores R2/R4/R9 all ADJ 0, PASS).

---

## (g) Stacking, body and JSON-LD, all three properties

Surface-split occurrence counts (body / `ld+json` / other JS / HTML comments):

| term | GCI | LGM | DCI |
|---|---|---|---|
| stack | 9/2/0/0 | 3/1/0/0 | 43/8/0/0 |
| stacked | 0/0/1/0 | 0/0/0/0 | 3/0/0/0 |
| stacking | 0/0/0/0 | 0/0/0/0 | 12/5/0/0 |
| combined | 0/0/0/0 | 31/11/1/0 | 2/1/0/0 |
| combining | 0/0/0/0 | 1/0/0/0 | 1/1/0/0 |
| on top of | 9/5/1/0 | 10/4/0/0 | 24/5/0/0 |
| both programs | 0/0/0/0 | 21/4/0/0 | 1/1/0/0 |
| either program | 0/0/0/0 | 30/9/0/0 | 0/0/0/0 |
| **cannot / may not / can be combined** | **0/0/0/0** | **0/0/0/0** | **0/0/0/0** |
| **double dip** | **0/0/0/0** | **0/0/0/0** | **0/0/0/0** |

**21 denial probes across all three properties. Total hits: 3**, all LGM, all
`mutually exclusive`, all about **materials** not programs
(`insulation-radiant-barrier-longmont.html:134, 1057, 1223` — radiant barrier at
the rafters versus mass insulation on the attic floor). **Zero rebate-stacking
denials anywhere. Silence holds on the denial side, which is the compliant
state.**

**GCI**: all 30 distinct combination sentences read; all legitimate (stack
effect, passive vent stack, insulation over old insulation, *"no altitude
multiplier to apply on top of it"*). Zero assertions, zero denials. Gate agrees:
R4 RAW 119 → ADJ 0.

**LGM**: 63 distinct combination sentences read. LGM's treatment is the
strongest of the three — it attributes rather than asserts.
`air-sealing-longmont.html:1074`: *"**Whether a single project can claim both is
unconfirmed:** Efficiency Works' own table pairs an Xcel figure with its own and
totals them, but that Xcel figure doesn't match any Xcel per-measure cap we've
independently verified…"* "Unconfirmed" is neither assertion nor denial — the
compliant middle. Zero of each. Gate agrees: R4 RAW 455 → ADJ 0.

### Legitimate uses — all still present, nothing collaterally swept

| use | GCI | LGM | DCI |
|---|---|---|---|
| stack effect / stack-effect | 9 (1 file) | 4 (1) | **42 (14 files)** |
| plumbing stack | 0 | 1 | 1 |
| "stacks up" | 0 | 0 | 1 |
| vent stack | 2 | 0 | radon 56 |
| new insulation on top of old | 3 | 0 (see below) | 4 |
| hot-stacked lifts | 0 | 0 | 2 |

One instance of each, quoted. **stack effect** (GCI
`upstairs-hot-cold-greeley.html:986`): *"An upstairs that runs hot in summer and
cold in winter is usually demonstrating the stack effect: warm air rises and
escapes through gaps in the ceiling, drawing replacement air in low."*
**plumbing stack** (DCI): *"…the furnace flue and plumbing-stack chases, bath-fan
housings, wiring penetrations…"* **stacks up** (DCI
`r-value-altitude-denver.html:1003`): *"Curious where your Denver home stacks up
against R-60?"* **insulation on top of the old** (GCI
`insulation-attic-greeley.html:1180`): *"Can new insulation go on top of the
old?"* — *"Usually, and it is the normal approach when the existing material is
dry, intact, and not vermiculite."*

**LGM's zero for "on top of the old" is NOT a sweep casualty.**
`git log -S 'on top of the old' -- public/` over all history returns **nothing** —
the phrase never existed there. LGM expresses the concept as "top-up", present
4+ times.

### DCI's 2 findings — and NO, 2 is not the whole of what remains

```
R4  STACKING ASSERTION OR DENIAL     RAW 661    ADJ 2     FAIL
```

Filters: generator-SRC restatement −203, `legitimate_uses` −71, NEUTRAL −385.
The two:

1. **`public/llms.txt:83`** [LLMS, ASSERTS] — *"- [WHE Bonus Guide](…/whole-home-efficiency-bonus-stacking-denver.html): The 25% bonus turns on one condition: three or more qualifying measures completed within two years of enrolling."* The `stacking` token comes **purely from the URL slug**, and the second program name is carried across a line boundary from line 82's unrelated list item. **A gate false positive.**
2. **`src:_educational_pages.py:6382`** [SRC, ASSERTS] — real in substance
   (*"…the Whole Home Efficiency Bonus **adding a 25% bonus on all standard
   rebates**, and the Combo Bonus…"*) and it **does render**, at
   `public/hear-rebate-status-colorado.html:1028`. The gate booked it against the
   generator rather than the public artifact.

On the slug page itself, `stacking` appears **6 times, all in the URL**
(canonical, og:url, JSON-LD, breadcrumb, sitemap) and **never in prose**.

**The material finding — an independent sweep found a class the gate cannot
see:**

```
'bonus on all standard rebates'  total=132  files=45  | BODY=120  LD+JSON=11  other_js=1
```

**139 sentence-instances / 49 distinct sentences across 45 of DCI's 75 pages**
assert that one incentive applies on top of others — including a second, stronger
class at `hear-rebate-status-colorado.html`: *"the City of Golden Rebate Match
adds a city match … **on projects that receive a matching Xcel rebate**"*, a
cross-**agency** combination claim.

**Why R4 cannot see any of it.** R4 resolves sentences by 25 `stacking_tokens`:
`stack, stacks, stacked, stacking, combin, combined, combine, on top of, on top,
alongside, layer, layers, bundl, unlock, unlocks, add-on, plus the, in addition
to, together with, both programs, either program, cumulative, at once,
concurrently, same measure`. Tested against the five canonical sentences:

```
gate stacking_tokens: 25
  tokens_found = NONE -> INVISIBLE TO R4    (x5, all five sentences)
```

`adds a 25% bonus on all standard rebates` contains **no tracked token** —
`adds a` is not `add-on`; `on all` is not `on top`. The only reason finding #2
surfaced is that its paragraph happens to contain an `href` whose slug says
`stacking`. **Fix the phrasing on one page and the gate goes quiet while 45 pages
keep asserting.**

**Adjudication caveat, stated honestly.** Whether these 139 are *defects* turns
on a reading the config already knows is open. `dci.json` R4 `director_desk`:
*"whole-home-efficiency-bonus-stacking-denver.html was KEPT and attributed on the
narrow reading. A stricter reading deletes the page. Deleting a ranking page is
the Director's call and is OPEN."* Under the narrow reading (the WHE Bonus is a
tier inside one Xcel program, so describing its own published mechanics is not
"stacking two programs") the 139 are licensed and 2 is the whole. Under the
strict reading they are 139 live assertions on 45 pages, and the Golden/Xcel pair
is unambiguously two independent agencies. **The gate's 2 is the whole only if
the narrow reading is the ruling one — but the detector gap is real either way,
and it will not close by fixing the 2 reported findings.**

One thing genuinely fixed: the config's noted survivor `"Xcel rebate-stack
eligibility"` in `llms.txt` is now **0 occurrences**.

---

## (h) The DCI embed attribution link — the instrument, stated honestly

**I drove a real browser.** Headless Chrome against the live URL with an injected
probe script performing genuine `querySelector` / `contains` /
`compareDocumentPosition` / `getComputedStyle` calls — not a static parse.

First, grep as a hint only: **there is no live `<iframe>` anywhere on DCI.**

```
POSITIVE CONTROL: 'Denver' in public/  ->  78 files
'<iframe' case-sensitive               ->   0 files
iframe case-insensitive                ->   public/r-value-needed-calculator-embed-code.html  (2)
escaped &lt;iframe                      ->   1
```

The only `iframe` string in the property is HTML-escaped inside
`<pre><code id="embed-snippet">` at
`public/r-value-needed-calculator-embed-code.html:908,913` — it is the
copy-paste snippet a third-party publisher installs, so **the snippet as
installed is the artifact the requirement is about**, and that is what I drove a
browser against.

Real DOM queries:

```
COUNT document.querySelectorAll("iframe").length = 1
COUNT anchors in host                            = 1
A href (resolved) = https://denvercoloradoinsulation.com/r-value-needed-calculator.html

TREE iframe.contains(a)                     = false
TREE a.closest("iframe") === null            = true
TREE a is inside iframe DOCUMENT?            = cross-origin: contentDocument null
TREE compareDocumentPosition(iframe,a)       = 4   (FOLLOWING, not CONTAINED_BY)
TREE ownerDocument === top document          = true

CSS display = inline   visibility = visible   opacity = 1   clip = auto
RECT w x h  = 371.671875 x 17      offsetParent non-null = true
checkVisibility() = true           aria-hidden on a = null
nearest aria-hidden=true ancestor = none
rel attribute (nofollow?) = null   onclick attribute = null
JS-INJECTED? a present in raw HTML source = true
```

The two elements, verbatim from Chrome's `outerHTML`:

```html
<iframe src="https://denvercoloradoinsulation.com/r-value-needed-calculator-embed.html" title="R-Value Needed Calculator — Denver Colorado Insulation" height="560" loading="lazy" style="width:100%;height:560px;border:0;display:block"></iframe>
```
```html
<a href="https://denvercoloradoinsulation.com/r-value-needed-calculator.html" style="color:inherit;text-decoration:underline">R-Value Needed Calculator by Denver Colorado Insulation</a>
```

Structure is `div > (iframe, p > a)` — the anchor is the iframe's nephew, never
its descendant. HTTP resolution, no redirect chain:

```
.../r-value-needed-calculator.html            no-follow: 200   follow: final=200 hops=0 size=86998
.../r-value-needed-calculator-embed.html      200, hops=0, size=18546
.../r-value-needed-calculator-embed-code.html 200, hops=0, size=61461
```

Runtime frame injection swept and excluded: `createElement('iframe')` = **0**
occurrences across `public/`, against a control of **74** `createElement` calls.

**Every clause of the requirement is satisfied**: a plain crawlable `<a>`,
outside the iframe element, not in the iframe's document, not JS-injected, not a
`<link>`, no `onclick`, no `rel=nofollow`, visibly rendered at 371.67 × 17 px,
resolving HTTP/2 200 in one hop.

---

## (i) Live-versus-repo byte verification

Every file curled **to disk** and compared with `cmp`. **No `$(curl ...)`
command substitution anywhere** — status and size were parsed from a log file in
a separate pass, never captured into a shell variable from curl.

**Positive control, run before concluding anything.** Two mutations, two
detections, so the zeros below are measured rather than absent:

```
Control 1 — append one byte to a copy of the fetched DCI index.html (88508 -> 88509):
   cmp pristine copy vs repo file  -> [exit 0] identical
   cmp tampered copy vs repo file  -> cmp: EOF on .../public/index.html   [exit 1]
Control 2 — flip ONE byte at offset 100 of the fetched GCI sitemap.xml:
   cmp untouched   -> [exit 0] identical
   cmp flipped     -> ctrl2.xml .../public/sitemap.xml differ: char 101, line 3   [exit 1]
   cmp -l          -> 101 132  40
```

| property | files compared | HTTP 200 | non-200 | **content mismatches** |
|---|---|---|---|---|
| DCI | **85 / 85** | 85 | 0 | **0** |
| LGM | **59 / 59** | 58 | 1 | **0** |
| GCI | **49 / 49** | 49 | 0 | **0** |
| **total** | **193 / 193** | 192 | 1 | **0** |

Enumeration cross-checked against `git ls-files public/`: identical on all three,
no untracked file in `public/`, no tracked file missing from disk.

**The one non-200, named in full: LGM `/index.html` — HTTP 301, `Location: /`.**

```
https://denvercoloradoinsulation.com/index.html         200
https://longmontcoloradoinsulation.com/index.html       301  https://longmontcoloradoinsulation.com/
https://greeleycoloradoinsulation.com/index.html        200
```

**DCI and GCI serve `/index.html` as 200, so the claim is not refuted**, and
LGM's `/` returns 200 with bytes **identical** to `public/index.html` (`cmp`
silent, exit 0). The raw `cmp` mismatch count is 1 and it is the 35-byte redirect
body being compared against the page — not a content defect:

```
0000000    M   o   v   e   d       P   e   r   m   a   n   e   n   t   l
0000020    y   .       R   e   d   i   r   e   c   t   i   n   g       t
0000040    o       /
0000043          (35 bytes; repo public/index.html is 77114 bytes)
```

Byte totals reconcile exactly: DCI 6,367,105 fetched vs 6,367,105 in repo
(delta 0); GCI 2,978,875 vs 2,978,875 (delta 0); LGM 3,668,949 vs 3,746,028,
delta **−77,079 = 77,114 − 35**, the homepage replaced by the redirect body and
nothing else. **No unexplained byte anywhere in the 193 files.** `curl` stderr
was 0 bytes on all three runs: no transport errors, no truncated transfers.

Regeneration-prone files checked individually — all 200, all exact:
`sitemap.xml` (14707 / 9738 / 7421 bytes), `robots.txt` (802 / 800 / 799),
`llms.txt` (22627 / 14958 / 8133). **No server-side regeneration is occurring.**

---

## (j) All four repos' state

```
calibrated-design-canon         58e98a0   main   clean   0 0
denvercoloradoinsulation.com    65383a7   main   clean   0 0
longmontcoloradoinsulation.com  95c93d1   main   clean   0 0
greeleycoloradoinsulation.com   34adbf4   main   clean   0 0
```

All four clean, all on `main`, all `0 0` against their local `origin/main`.
`git fetch` was deliberately not run, so origin refs are as last fetched — stated
rather than claimed as fresh. Canon measured `0 1` at the start of this review
(one unpushed `docs/lanes.md` commit) and `0 0` twenty minutes later: a
concurrent session pushed during the read. **No worktree was created by this
review**, so none needed pruning.

One unattributed observation, reported rather than suppressed:
`canon/ops/claim_gate/__pycache__/surfaces.cpython-314.pyc` carries an mtime
inside the session window. It is gitignored (`.gitignore:2:__pycache__/`) and
canon's tracked tree is clean. I tested whether my own invocation pattern writes
it — recorded the mtime, re-ran the gate exactly as before, re-read the mtime:
**unchanged**. My runs demonstrably do not produce it; a concurrent session is
the likeliest source. Flagged rather than claiming a clean bill I did not verify.

---

## (k) The five "also worth attacking" claims

### 1. Nine of DCI's 46 R5 findings name a file without the sentence — **CONFIRMED, exactly nine**

All 46 adjudicated findings extracted and tested individually. The nine are
listed in §0 with per-file positive controls. The reported list matches mine
exactly. **Root-caused** — see §0; the mechanism is the `dec()` asymmetry at
`claim_gate.py:1245` plus the `best = best or k` fallback at `1248`, and the
reproduction is in §0.

**A correction anyone re-running this needs.** A naive `grep -F` flags **12**,
not 9. Three extra are SRC rows (`src:_educational_pages.py`) where the gate's
SRC surface concatenates adjacent Python string literals, so the sentence is
contiguous in the gate's string-run representation but not in the raw file:

```
--- row 40  src:_educational_pages.py:SRC
    in gate's SRC string-run text?  True
    in raw file text?               False       (rows 42 and 43 identical)
```

**The answer is 9.** These are genuine false positives, not mislabelling: the
sentence is on none of the nine pages in any form, so there is no correct file to
re-point them at. **DCI's blocking R5 count of 46 is not defensible; 37 is the
ceiling** (30 real page-level sentences + 7 SRC rows confirmed present in their
modules). Whether each of the 37 survivors is truly unattributed on its own page
is **NOT TESTED**, and one thread suggests 37 is itself soft: rows 21 and 24 name
a recognised publisher inside the sentence while the `recognised_publishers`
filter reports `47 (removed 0)`.

**Blast radius:** any property with two or more `CITED_SOURCES` sharing a URL
where the on-page label contains a character `dec()` rewrites. GCI and LGM
**NOT TESTED** for it.

### 2. `run_controls` contaminates every control context — **CONFIRMED and PROVEN LIVE**

Code quoted and reproduction given in §0. Every consumer of `_gen` / `ctx.gen`,
traced:

| line | consumer | reached by |
|---|---|---|
| 4549 | `_control_ctx`: `ctx.gen = base_cfg.get("_gen")` | the injection point |
| 1238-1239 | `key_for_cited_stat` → `self.gen.cited_sources` | **every control** |
| 1278 | `build_claim_set` → `ctx.gen.constants` (R2 territorial constants) | **every control** |
| 1294 | `build_claim_set` → `ctx.gen.slug_cite_keys` | **every control** |
| 1298-1303 | `build_claim_set` → `ctx.gen.cited_sources`, injects `S_CITE` | **every control** |
| 1402-1419, 1466-1477, 1511-1519 | `rule_R1` provenance, filters, notes | R1 controls |
| 1895-1898 | `rule_R2` → `ctx.gen.cited_sources` | R2 controls |
| 2698 | `rule_R4` `f_noun` → `ctx.gen.constants` | R4 controls |
| 5198 | peer ctx: `pctx.gen = S.GeneratorFacts()` | deliberately blanked for `--peer` |

R3, R5, R6, R7, R8, R9, R10 and R11 contain no direct `ctx.gen` read — and are
not protected, because `build_claim_set` runs for every control context
(`claim_gate.py:4557`) and splices the repo's real `CITED_SOURCES` in as `S_CITE`
surfaces. Two binding routes: URL match (`key_for_cited_stat`) and slug match
(`1293-1295`).

**Trigger condition, precisely:** a repo `CITED_SOURCES` entry whose `url`
collides with a URL in any fixture's `p.cited-stat`, or a slug map keyed on a
fixture basename, whose text matches a `claim_subjects` slot, an R4 predicate, an
R5 magnitude, and so on. There are only three such URLs across the fixture set —
`millikenco.gov/246/New-Residents`, `buildingscience.com/documents/digests/bsd-014-air-flow-in-buildings`,
and `co.my.xcelenergy.com/s/residential/home-rebates/insulation-air-sealing`.
The collision surface is small **but it is aimed squarely at the sources these
properties actually cite.**

**Latent today, not active** — all three properties show `0 FALSE ALARM` and
`0 FIRE ON REPAIRED` at their current heads, so the pass's own characterisation
is accurate. It is live on two wired builds.

### 3. GCI's one OWED key, and whether the audit can be fooled — **CONFIRMED; the specific attack DISPROVED; three other holes CONFIRMED**

```
dci  CONFIG KEYS READ BY NO CODE PATH: 0 OWED, 26 declared documentation-only
lgm  CONFIG KEYS READ BY NO CODE PATH: 0 OWED, 31 declared documentation-only
gci  CONFIG KEYS READ BY NO CODE PATH: 1 OWED, 34 declared documentation-only
     OWED: R3.t3_adjudication_2026_09_18
```

Confirmed at `config/gci.json:318`. It is prose adjudication provenance, not a
rule — a **naming** problem (it would be exempt if named
`t3_adjudication_2026_09_18_note`, per `_DOC_PREFIXES` at `claim_gate.py:352`),
not a silently-dead rule. **The audit is report-only** and never changes the exit
code: reporting at `5079-5086` is a bare `out(...)`, in contrast to the
`unfirable_patterns` check four lines above which does `_finish(out, args, 2, t0);
return 2`. GCI exits 0 today *with* an OWED key, which proves it empirically.

**Can declaring a LIVE key documentation-only switch off a rule? NO — disproved
by run.** `documentation_only_keys` has exactly two references in the whole
5,346-line file (`claim_gate.py:483` and `513`), neither in a rule path. In a
mirror I declared `R5.magnitude_words` and `R9.claim_subjects` — both genuinely
live — documentation-only with fat justifications:

```
BEFORE: exit=1   0 OWED, 26 declared   R5 RAW 541 ADJ 46 FAIL   blocking failures: 3 (R4, R5, R9)
AFTER:  exit=1   0 OWED, 26 declared   R5 RAW 541 ADJ 46 FAIL   blocking failures: 3 (R4, R5, R9)
```

Identical. The declaration is inert on live keys.

**Three holes that DO exist, each proven by run:**

- **Hole 1 — a key name in a COMMENT counts as "read by a code path."** The test
  at `claim_gate.py:502` is a substring search over source text and does not
  distinguish code from comments. Injecting one comment line retired an OWED key:
  `4 OWED → 3 OWED`. **Already live in canon**: `allowlist`,
  `and_the_figures_are_still_banned` and `measured_at` are read by nothing and
  are exempted only because their names appear in the audit's own bookkeeping
  tables at `claim_gate.py:365`, `389`, `478`.
- **Hole 2 — a declaration matches on the BARE LEAF NAME, unscoped across every
  rule.** `claim_gate.py:530` does `u.split(".")[-1] not in good`, so one
  declaration covers every path ending in that name: declaring one bare leaf took
  `R4.zz_probe_thing` and `R5.zz_probe_thing` out together. A future
  `R7.allowlist` is pre-silenced by the `allowlist` declaration written for R2.
- **Hole 3 — the audit checks key PRESENCE, never VALUE.** Emptying
  `R5.magnitude_words` to `[]` leaves it at `0 OWED`, green. **The canary catches
  it, not the audit** (output in §(b)).

### 4. `--brief` cannot be mistaken for clean — **CONFIRMED, the flag is safe**

Wiring quoted in full. LGM `regen_all.sh:171` and GCI `regen_all.sh:151` are
byte-identical: `"$(dirname "$0")/ops/claim_gate.sh" --brief` — a **bare simple
command**, no pipe, no `| tee`, no `|| true`, no `&&`, no subshell, no `set +e`.
`set -e` is at line 27 in all three. The wrapper ends in `exec`, so no
intermediate shell can lose the status.

```
dci FULL exit=1   dci BRIEF exit=1
lgm FULL exit=0   lgm BRIEF exit=0
gci FULL exit=0   gci BRIEF exit=0
forced control failure:  FULL exit=2   BRIEF exit=2
```

**`--brief` never changes the exit code, for 0, 1 or 2**, and structurally cannot:
`args.brief` is referenced at exactly one line (`claim_gate.py:5297`), the exit
code is computed independently at `5327`, and `emit_rule` returns early on
`brief` after printing everything except the enumerations, touching no shared
state. Line counts 3400 → 355, 2701 → 337, 1453 → 335, with VERDICT lines, the
SUMMARY block, the header and the CONTROLS block verified **identical** between
full and brief on all three.

On a failing run the word FAIL appears on three VERDICT lines, three SUMMARY
rows, the `blocking failures: 3 (R4, R5, R9)` line, and **the last line of
output**:

```
  R4  STACKING ASSERTION OR DENIAL     RAW 661    ADJ 2      FAIL
  R5  UNCITED STATISTIC                RAW 541    ADJ 46     FAIL
  R9  INTERNAL CONTRADICTION           RAW 2      ADJ 2      FAIL
  blocking failures: 3 (R4, R5, R9)
CLAIM GATE: FAIL
```

**And the build actually fails.** In a scratch copy of GCI, a defect injected
into the **generator source** so it survives regeneration:

```
=========== regen_all.sh exit=1 ===========
  R5  UNCITED STATISTIC                RAW 204    ADJ 1      FAIL
  blocking failures: 1 (R5)
CLAIM GATE: FAIL
-- does the log contain 'Site regenerated'?  0    (baseline: 1)
```

`set -e` halted the script at the gate. Baseline in the same scratch copy is
exit 0, so the harness is proven live.

**Two caveats.** `pipefail` is **absent from all three** `regen_all.sh` — it does
not matter today because the gate is not piped, but anyone who later adds
`| tee build.log` to that line silently disarms the gate. And the first injection
attempt did **not** fail the build: R5 RAW rose 203→204 while ADJ stayed 0,
because the sentence contained *"eaves"*, which is in `common.json`'s
`R3.code_context_markers` and R5 shares that filter. A genuinely uncited
statistic in a sentence that happens to mention an eave, a top plate or an
R-value is cleared.

**DCI's omission is correctly recorded**, at `regen_all.sh:135-152`, including
the instruction the brief asked about: *"Do NOT wire it in 'with a || true' or
any other softener — that recreates a green build over a failing gate, which is
worse than not having wired it at all."* The invocation at line 152 is commented
out.

### 5. Two properties lack the `ops/hooks/commit-msg` hook — **CONFIRMED; DCI is the one that has it**

```
denvercoloradoinsulation.com      core.hooksPath=ops/hooks   ops/hooks/commit-msg present (3477 b)
longmontcoloradoinsulation.com    core.hooksPath=NONE        ops/hooks/ DOES NOT EXIST
greeleycoloradoinsulation.com     core.hooksPath=NONE        ops/hooks/ DOES NOT EXIST
```

The verification-trailer ruling is enforced on one of three properties — and on
the *one property the gate is not wired into*, so neither enforcement mechanism
covers LGM or GCI on the commit path.

---

## (l) Verdict

**Is this pass's work sound?** In its content corrections, largely yes, and two
of them are unambiguously good. **LGM's 31 pages claiming review six days before
the repository existed are gone — zero remain**, verified against git rather than
against the pass's own report. **The GCI territory split is correct on every
surface I could reach**: no Atmos attribution on Johnstown, Milliken or Severance
in body, JSON-LD object graph, `areaServed`, llms.txt, sitemap, JS or comments;
Johnstown carries no invented qualifier; Milliken is exactly `most of Milliken`
(145, zero variants); Severance is exactly `most locations in Severance` (144,
zero variants); and the Windsor/LaSalle/Ault hedge carries both halves on all
three pages, with zero pages carrying one half only. **LGM's Efficiency Works
restriction is intact with no gap at all** — 48 files mention the programme and
48 carry a restriction. **All 193 live files are byte-identical to their repo at
HEAD**, with the single LGM `/index.html` 301 being real and deliberate. **The
gate's 29 positive controls all stop firing when their defect is removed**, and
six of seven repair-phase attack routes are closed. The 86-vector set shows
**zero regressions and two fixes**.

**What is still wrong, in severity order.**

1. **The gate fabricates claims and then adjudicates them.** §0. Nine of DCI's 46
   blocking R5 findings quote a sentence that is not on the page named — root
   cause is one missing `dec()` call at `claim_gate.py:1245` plus a silent
   `best = best or k` fallback at `1248`. The same splice carries the
   repo-under-test's generator into every control fixture, proven live to produce
   `FIRES ON REPAIRED` and `FALSE ALARM` and drive the gate to exit 2. Three
   fixes are implied and none is in any property's content: apply `dec()` to both
   sides at 1245; decline rather than guess on ambiguity at 1248; and give
   `_gen` the isolation `ctx.repo` already has.

2. **DCI's exit 1 is substantially false, and its FAIL is therefore not
   actionable.** At least **12 of its 50 blocking findings are provably not
   defects**: 9 R5 (above), and **2 of 2 R9**. R9's `N3-unverifiable` row is a
   declaration of inability that carries blocking weight — the ids
   `lf-calc-inputs`/`lf-calc-output` are built at runtime by
   `h.id = 'lf-' + n.replace('_','-')`, so no literal exists in the bytes; a
   browser confirms both are present in the rendered DOM. **No content change can
   ever clear it**, because the only way to make it green is to re-introduce the
   static markup whose removal was the 2026-08-25 lead-provenance fix. The second
   R9 row is a subject collision: `"is the prerequisite step"` in
   `whe_audit_precondition`'s slots matching a navigation sentence about
   **asbestos testing** on the vermiculite page, which mentions `front door` 0
   times and `precondition` 0 times. DCI's R4 count of 2 is 1 false positive
   (slug-derived) plus 1 real-but-misattributed finding. A build that stays red
   forever on false positives is how a real gate becomes ignored — the exact
   failure the DCI comment block was written to avoid, arriving from the other
   direction.

3. **R4 cannot see DCI's dominant stacking phrasing.** 139 instances across 45 of
   75 pages of *"adds a 25% bonus on all standard rebates"* contain **none** of
   R4's 25 tracked tokens, plus a cross-agency claim (*"the City of Golden Rebate
   Match adds a city match … on projects that receive a matching Xcel rebate"*).
   Whether they are defects is an **open Director ruling recorded in the config
   itself**; the detector gap is real under either reading.

4. **The R8 as-of is a hardcoded string that nothing refreshes and nothing
   checks.** The gate never reads the calendar. This pass diagnosed the failure
   mode precisely and then re-committed it with a new constant in three configs,
   leaving `common.json` and the code fallback at `2026-09-17`. Proven: a page
   truthfully dated 2026-09-19 fails as `[future-date]`, exit 1 — on two
   properties where the gate now halts the build.

5. **R8 has no over-dating sub-test, and the two wired properties run opposite
   doctrines.** GCI pinned 11 pages so a sitewide JSON-LD edit would not move
   their dates; **LGM stamped today's date on 4 pages whose only change was
   exactly that** (`contact.html`'s entire diff is the date line). Nothing will
   ever catch it. Separately, GCI carries **2 pages with genuinely stale review
   dates** — `about.html` published 2026-08-07 against a 2026-08-27 change to
   **where the visitor's data is sent** — raised by the gate and then cleared
   through `pinned_pages` and `exempt_pages`. And **10 impossible `datePublished`
   values** (9 DCI dated 35–36 days before the repository existed, 1 GCI) are
   invisible by construction, because `claim_gate.py:3581` excludes
   `ld:datePublished` from `claimed`. One of them identifies `dci.json`'s open
   `"unidentified"` anomaly as `public/ice-dams-denver.html`.

6. **Two live sourcing defects the allowlists do not cover.** GCI's
   `CDC_HPS_CLINICAL_OVERVIEW` registry entry attributes *"the deer mouse
   (Peromyscus maniculatus) is the primary U.S. reservoir for the Sin Nombre
   strain"* to a CDC page containing `Peromyscus`=0, `Sin Nombre`=0,
   `reservoir`=0 — and a live body sentence attributes it to the **parent** page,
   which contains `deer mouse`=0 as well. `quote=False` keeps R1 silent. The
   fatality-denominator half of that same entry was corrected this pass and
   verified verbatim; the deer-mouse half was not examined. And LGM's Xcel
   exclusion-list allowlist entry asserts its truncation *"can only make the list
   more permissive, never more flattering to the reader's eligibility"* — those
   two halves contradict each other and the second is false. Dropping
   `pre-improvement R-values of R-16 or greater` and `residential properties with
   more than four units` from a printed **exclusion** list makes more readers
   think they qualify. The page's own garage claim is sound; the rule written
   beside it is inverted, and the next pass will inherit it.

7. **Smaller, all measured.** R3's demotion silently removed 20 of the 86 vectors
   from the blocking set, so a banned rebate figure can no longer stop a release
   on its own. R2 sub-test `t` fires on **correct** attributions assembled across
   a JS concat boundary, which is why vector R2-B8 "passed" — honest count is 12
   of 86, not 11. `R8.footer_marker` is `"Last reviewed:"` while LGM emits
   `"Last updated:"` on all 48 pages, killing that code path on that property.
   `time[datetime]` takes the first `<time>` in document order, which is the sole
   source of DCI's and LGM's only RAW R8 finding — both are false positives.
   DCI's `DCI-D-003` hold note asserts 70 stale sitemap entries and is printed
   into every run; there are **0**. Five R1 allowlist stopgaps are live with no
   expiry; the config names that as the hazard and says the cause fix was skipped
   because `claim_gate.py` carried another session's uncommitted changes — that
   blocker is gone, `claim_gate.py` is clean in git, and R1 half B
   (`1449-1461`) still has no publisher test, so the fix was simply never made.
   The dead-config audit can be
   satisfied by a comment and by a bare leaf name, and three canon entries are
   already exempt through the audit's own bookkeeping tables. `pipefail` is absent
   from all three `regen_all.sh`. The `ops/hooks/commit-msg` verification hook is
   installed on DCI only — the one property the gate is *not* wired into.
   `LGM index.html:1127` states Efficiency Works "isn't mentioned on those pages",
   and it is, twice each in JSON-LD, caught by no rule. NEW-18 remains open: a
   word salad built from a fixture's own vocabulary satisfies its repair test
   silently. And the prior read's headline "12 of 86" is contradicted by its own
   per-rule table, which sums to 13.

**The honest summary.** This pass made the three properties measurably more
truthful and made the gate measurably better at the classes it already knows.
What it did not do is establish that the gate's verdicts mean what they say. On
the property it failed, the verdict is substantially built from findings the gate
invented. On the two it passed and then wired to block a build, the pass rests on
a hardcoded date, on exceptions that suppress two real defects, and on a control
phase that an ordinary content edit can turn against itself. **A gate is only
worth its exit code, and these three exit codes are not yet load-bearing.**
