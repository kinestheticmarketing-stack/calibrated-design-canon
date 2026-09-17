# Adversarial read of the claim gate — 2026-09-17

Reviewer: an adversarial session with zero inherited context. Target: the
tooling at `ops/claim_gate/`, not the websites it inspects. Mandate: assume it
is blind somewhere and find where. **Nothing in the implementation, the config,
the fixtures, the spec, any page, any generator or any `public/` was edited.**
This file is the only thing this pass wrote into canon.

State at the start of the pass, measured:

```
$ git -C ~/code/denvercoloradoinsulation.com   rev-parse HEAD   1b6949c0ade3a7b7825e0d36916e9f38d5b0da62   main   clean   0 0 vs origin
$ git -C ~/code/longmontcoloradoinsulation.com rev-parse HEAD   a86c5afac76e23d05ebc261fdfbda9c4a33eee0c   main   clean   0 0 vs origin
$ git -C ~/code/greeleycoloradoinsulation.com  rev-parse HEAD   ee0157d7fee1a46cdc9d9e3da0e18f37bcf23fe7   main   clean   0 0 vs origin
$ git -C ~/code/calibrated-design-canon        rev-parse HEAD   4bf5373b6e8deebd8237329843343462f7f58e5c   main   clean   0 1 vs origin (one unpushed commit, not mine)
```

Baseline runs, as the gate reported them:

| property | exit | blocking failures |
|---|---|---|
| DCI | 1 | 8 — R1 R2 R3 R4 R5 R7 R8 R9 |
| LGM | 1 | 5 — R1 R2 R3 R5 R8 |
| GCI | 1 | 6 — R1 R2 R3 R5 R8 R10 |

All three properties FAIL the gate today. R6 reports `RAW 0 ADJ 0 PASS` on all
three.

---

## 0. THE SINGLE MOST SEVERE FINDING

**R6 — the only rule that exists to catch "a calculator printing two different
severity words beside the same percentage" — reports `RAW 0 / ADJUDICATED 0 /
PASS`, byte for byte identically, whether its scanner found a clean chain, found
nothing at all, or was staring straight at the defect. Four distinct forms of the
exact named defect are invisible to it, and in every one of those four cases the
printed R6 block is IDENTICAL to a genuinely clean run.**

Measured, with a chain configured, its `surfaces` present, and a clean generator
so the rule block actually ran (`/tmp/claim-gate-scratch/r4/vectors_r6.py` and
the follow-up `adv-r6c` config):

| variant | R6 RAW | R6 ADJ | verdict | exit |
|---|---|---|---|---|
| branches read `gap`, print interpolates `pctShort` (the real pre-2026-09-11 DCI form) | 5 | 5 | FAIL | 1 |
| the repaired form (branches read `pctShort`) | 0 | 0 | PASS | 0 |
| the SAME defect minified onto one line | 0 | 0 | PASS | 0 |
| the SAME defect as a nested ternary | 0 | 0 | PASS | 0 |
| the SAME defect as `switch (true) { case ... }` | 0 | 0 | PASS | 0 |
| **two severity words beside the same percentage** (duplicate `pctShort >= 50` branches) | 0 | 0 | PASS | 0 |

`difflib.unified_diff` of the printed R6 block, repaired-form versus each of the
four misses: `*** IDENTICAL, BYTE FOR BYTE ***` in all four cases.

R6 prints no denominator. There is no "chains examined: 1", no "label-emitting
assignments found: 4", no filter row, nothing. `RAW 0` is the only number, and
it means both "I looked and it is clean" and "I could not see it". That is the
precise failure mode Ruling 5 exists to forbid, sitting on the rule for the
defect class the gate was built after.

### Honest overall verdict

**Would this gate have stopped the six defects named in the brief?**

| defect | would the gate have caught it |
|---|---|
| paraphrase inside quotation marks as a named utility's own words, 11 pages | **Only in one exact spelling.** Caught with `&ldquo;` inside `<p class="cited-stat">`. MISSED with `&#8220;`, `&#x201C;`, `«»`, `class="cited-stat footnote"`, an HTML comment, a JS template literal, or the source named three sentences earlier. |
| three towns credited to the wrong gas utility for two years | **Only on the town's own page, only with an attribution word, only in the exact case.** MISSED on every page that is not in a town's `page_slugs` — which is most of the property. |
| a retired eligibility rule published as current, 35 pages | **Partly.** Caught for most configured propositions. MISSED for the two `Dec. 31` short forms — and the config's own note records that the short form is what survived four prior sweeps. |
| an invented rebate program with four invented eligibility pathways, 72 pages | **NOT TESTED as such.** No rule asserts "this program exists". R7 catches only propositions someone has already written into the config, i.e. only after the defect has been found by other means. |
| 545 banned rebate dollar figures | **Mostly yes, and this is the gate's strongest rule.** `$`-anchored on RAW catches JS comments, JSON-LD, `<head>`, `llms.txt`, `robots.txt`, line-wrapped numbers. MISSED: entity-encoded `$` with a 1–2 digit amount, the figure in words, a bare numeral with no money word in the window, a bare `2000` (eaten by the year filter), and a figure rendered through CSS `content:` (explicitly filtered out). |
| a calculator printing two different severity words beside the same percentage | **NO.** See above. |

So: four of six partially, one not at all, one not addressed as a claim.

The gate is a real and substantial improvement on the one-off sweeps it
replaces — the corpus contract is correct and verified, the read surface is
genuinely wide, the output is byte-deterministic, it writes nothing, and it
declares its own string-list halves. But it is still, in its load-bearing rules,
**a better-organised string list with a claim-test label on it**, and its
control phase cannot tell the difference. Three of its twenty positive controls
survive on a repaired fixture. Its own "a bare zero is FORBIDDEN" guarantee is
satisfied in letter and broken in substance in at least two provable places. Its
`raw − removed == adjudicated` assertion is structurally unreachable. `SRC`,
which it advertises on every run and in six of eleven rules, is computed and
never read.

**What it is still blind to, stated plainly:** meaning. Every rule that matters
resolves to a configured string list scanned over a sentence pool, and the pool
excludes whole-JS-body text, inline CSS, `sitemap.xml` prose and HTML comments.
A claim paraphrased, anaphorically split, case-shifted, soft-hyphenated,
confusable-substituted, runtime-assembled, or placed in a template literal
passes. On the wrong-utility rule — the one Ruling 7 calls load-bearing — a
page with no configured town is exempt outright, and the exemption leaves no
trace in any count.

---

## (a) Every positive control, and whether it survived the repair test

Method. The canon fixtures may not be edited, and a repair test cannot be done
without writing a fixture, so the whole of `ops/claim_gate/` was mirrored to
`/tmp/claim-gate-scratch/r4/canon/ops/claim_gate` and driven through the
property wrappers' documented `CANON_ROOT=` hook. Parity was established before
any mutation: `--canary` output from the mirror is identical to the real tree
apart from the stderr wall-clock line (`2.19s` vs `2.15s`). Harness:
`/tmp/claim-gate-scratch/r4/repair.py`, which restores every fixture from canon
before each case.

Pristine canary, all three properties, `diff`ed against each other and identical:
`CONTROLS: 20 positive DETECTED, 0 MISSED · 14 negative clean, 0 FALSE ALARM`.
There are 20 positive controls (not 11) and 14 negative controls (`NEGATIVES =
["NEG%02d" % i for i in range(1, 15)]`; the fifteenth file in
`fixtures/negative/` is `NEG11.gitfacts.json`, a sidecar).

| control | mutation applied | row after mutation | survived? |
|---|---|---|---|
| **R1** | half A only: strip the quotation marks from the cited-stat paraphrase, attribution kept | `DETECTED  (2: B)` | **NO — NOT A REAL CONTROL** |
| R1 | full: every quotation mark removed from every surface | `*** MISSED ***` | (stops firing only when both halves are repaired) |
| **R2a** | every `Atmos` replaced by Severance's real utility, `Xcel Energy` | `DETECTED  (1: q)` | **NO — NOT A REAL CONTROL** |
| R2a | the above, plus the missing per-town qualifier supplied | `*** MISSED ***` | (stops firing only when a second, unrelated defect is also repaired) |
| R2b | og-image SVG text `Atmos rebates explained` → `Rebates explained` | `*** MISSED ***` | YES |
| R2c | `atmosenergy.com` href → `xcelenergy.com` | `*** MISSED ***` | YES |
| R3a | the figures `1550 / 0.75` removed from the JS comment | `*** MISSED ***` | YES |
| R3b | every dollar figure removed from meta + both JSON-LD blocks | `*** MISSED ***` | YES |
| R3c | every rank/superlative word removed | `*** MISSED ***` | YES |
| R4a | the stacking denial replaced by silence in prose, JSON-LD and the trailing line | `*** MISSED ***` | YES |
| R4b | every stacking assertion and denial removed; both programs still named | `*** MISSED ***` | YES |
| R5 | both uncited magnitude figures removed, prose otherwise intact | `*** MISSED ***` | YES |
| R6a-G1 | branches re-read `pctShort` (the real 2026-09-11 D3 fix) | `*** MISSED ***` | YES |
| R6a-G2 | same mutation | `*** MISSED ***` | YES |
| R7 | superseded identifiers, URLs and every superseded proposition removed | `*** MISSED ***` | YES |
| R8a | review date advanced to the sidecar's `last_visible_change` 2026-09-11 | `*** MISSED ***` | YES |
| R8b | review date moved to the sidecar's `first_seen` 2026-09-10 | `*** MISSED ***` | YES |
| R8c | future `datetime` and out-of-order `datePublished` corrected | `*** MISSED ***` | YES |
| R9-N1 | `llms.txt` made to agree with the page (removes the cross-FILE contradiction only) | `*** MISSED ***` | YES |
| R9-N2 | the within-file front-door contradiction removed only | `*** MISSED ***` | YES |
| R10 | every promise sentence replaced by a refusal-free non-promise | `*** MISSED ***` | YES |
| **R11** | both control-overlay tracked terms removed from the page | `DETECTED  (2: row)` | **NO — NOT A REAL CONTROL** |
| **R11** | fixture reduced to `<p>Nothing.</p>` — no tracked term anywhere | `DETECTED  (2: row)` | **NO — VACUOUS** |

Correction to my own first pass, recorded because the brief forbids inferring:
my initial R9 mutation removed a redundant instance rather than the
contradiction, and R9-N1 correctly kept firing on the surviving cross-surface
disagreement. Re-tested in `/tmp/claim-gate-scratch/r4/repair9.py` with three
precise variants — llms-only repair (N1 stops, N2 still fires), page-only repair
(N2 stops, N1 still fires), both (both stop). **R9-N1 and R9-N2 are genuine
controls.**

### The three controls that are not controls

1. **R1** — the `Control` object carries no `sub`, so a hit from EITHER half
   satisfies it. Half B is self-declared in the gate's own output as
   `half B (STRING LIST -- cannot be a claim test)`. Repair half A — the claim
   test, the registry-provenance assertion — and the control still reports
   `DETECTED (2: B)`. **R1's claim-test half has no positive control at all.**

2. **R2a** — fires on two sub-tests at once (`a` = utility-not-serving-town,
   `q` = qualifier-absent). Repair the wrong-utility claim completely and it
   still reports `DETECTED (1: q)` off a missing qualifier string. **R2a does
   not prove R2's wrong-utility half works.** R2b and R2c do prove their own
   sub-tests, so R2 is not uncontrolled — but the control named for the visible
   wrong-utility case is not testing it.

3. **R11** — `rule_R11` appends one `Hit` per configured tracked term
   unconditionally, outside any conditional. The control therefore asserts
   `len(config.R11.tracked_terms) >= 1` and nothing else. With the fixture
   reduced to an empty page it still reports `DETECTED (2: row)`. **R11 has no
   positive control in any meaningful sense**, and R11 is also the rule whose
   `kind:` line claims `CLAIM TEST`.

### The negative controls are not isolated from the repo under test

The README states: *"Controls run against **fixture files only**, never the
repo"* and *"a control proves the RULE can detect its defect regardless of which
property's territory, figures or label chains happen to be loaded."* Both are
false. `run_controls(out, cfg, repo, opt_in, gen)` builds every control context
with `base = dict(cfg)` (the real property config), `base["_gen"] = gen` (the
real repo's parsed generators) and the real `repo` path. `rule_R6` then reads
`os.path.join(ctx.repo, chain["generator"])` off disk inside the
negative-control context.

Proved by running DCI's config against a repo that has no
`_generate_calculator_pages.py`:

```
CLAIM GATE — dci — /tmp/claim-gate-scratch/r4/adv — HEAD 44e2256 — as-of 2026-09-17
  canary- NEG01   fixtures/negative/NEG01.html   *** FALSE ALARM *** R6 UNREGISTERED chain dci-rvalue-tier: no surface or generator text found
  canary- NEG02   fixtures/negative/NEG02.html   *** FALSE ALARM *** R6 UNREGISTERED chain dci-rvalue-tier: no surface or generator text found
  CONTROLS: 20 positive DETECTED, 0 MISSED · 0 negative clean, 14 FALSE ALARM
CLAIM GATE: NOT RUN — a rule that cannot detect its own defect is worse than no rule, because it manufactures confidence.
exit 2
```

All 14 negative fixtures false-alarm on state that has nothing to do with them.
Worse, when the real generator *does* carry the R6 defect, the same thing
happens with the real finding attached:

```
  canary- NEG01  *** FALSE ALARM *** R6 G1 branch reads {gap} while the printed string interpolates {pctShort} | Moderately under cod | ...
  CONTROLS: 20 positive DETECTED, 0 MISSED · 0 negative clean, 14 FALSE ALARM
CLAIM GATE: NOT RUN
exit 2
```

A live R6 defect is reported as fourteen false alarms on innocent fixtures and
the gate exits 2 "could not be trusted to have run" instead of exit 1 "R6
FAILED". The R6 rule block never prints. DCI escapes this today only because
its chain happens to name a generator file that exists and is currently clean.
Any property that registers an R6 chain with `surfaces` but no existing
`generator` cannot complete a run at all — measured: `exit 2`, 14 FALSE ALARM,
on eight separate variants.

Also `--today`, a documented flag, breaks the control phase from the other side.
`NEG11` carries a hardcoded 2026-08-07 date:

```
$ ... --today 2026-08-01
  canary- NEG11  *** FALSE ALARM *** R8 b footer_text = 2026-08-07 is after today (2026-08-01) | R8 b time[datetime] = 2026-08-07 is after today (2026-08-01)
  CONTROLS: 20 positive DETECTED, 0 MISSED · 13 negative clean, 1 FALSE ALARM
CLAIM GATE: NOT RUN
exit 2
```

---

## (b) Every adversarial fixture, verbatim, with the gate's actual output

Harness: a purpose-made git repo at `/tmp/claim-gate-scratch/r4/adv` with a
`public/` tree, driven by `--config <scratch>/config/adv-*.json --repo
<adv>`. Each scratch config is `{"extends": "<real property>.json", "key": ...,
"min_artifacts": 1, "expected_html": 1}` — nothing else overridden, so every
vector ran against the real property's real territory, figure lists, program
lists and propositions. Each vector ran ALONE (plus a benign `index.html`,
`robots.txt`, `llms.txt`) so hits attribute cleanly. Scripts:
`vectors_r1r2.py`, `vectors_r3plus.py`, `vectors_r4plus.py`, `vectors_r6.py`.
Baseline for the benign three-artifact corpus: every rule `RAW 0 ADJ 0 PASS`,
exit 0.

### R1 — FABRICATED QUOTATION (config: gci, R1 values all live in common.json)

Positive control for my own pipeline, so absence means something:

```html
<p class="cited-stat">According to <a href="https://co.my.xcelenergy.com/s/residential/home-rebates/insulation-air-sealing" rel="noopener" target="_blank">Xcel Energy&rsquo;s residential rebate summary</a>, &ldquo;the air sealing rebate requires a 20% reduction in CFM 50.&rdquo;</p>
```
`R1 RAW 1 ADJ 1 FAIL exit 1` — **CAUGHT**. The gate's own note:
`half A (CLAIM TEST) 1 · half B (STRING LIST -- cannot be a claim test) 0`.
Hit line: `public/a.html:CITE  A  <unresolved-key> According to Xcel Energy’s residential rebate summary , “the air sealing rebate requires a 20% reduction in CFM 50.”`

| vector | fixture (the changed part, verbatim) | result |
|---|---|---|
| R1-A1 | same block, `&#8220;` … `&#8221;` instead of `&ldquo;`/`&rdquo;` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R1-A1x | same block, `&#x201C;` … `&#x201D;` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R1-A2 | same block, `class="cited-stat footnote"` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R1-A3 | `<p>Xcel Energy publishes a residential rebate summary. It is the document the program runs on. The wording that matters is this. “The air sealing rebate requires a 20% reduction in CFM 50.”</p>` | `RAW 0 ADJ 0 PASS` — **MISS** |
| R1-A4 | `<p>According to Xcel Energy, «the air sealing rebate requires a 20% reduction in CFM 50.»</p>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R1-A5 | `<script>var note = ` + backtick + `According to Xcel Energy, “the air sealing rebate requires a 20% reduction in CFM 50.”` + backtick + `;</script>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R1-A6 | `<!-- According to Xcel Energy, “the air sealing rebate requires a 20% reduction in CFM 50.” -->` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |

Seven of seven MISSED. Mechanism: half A's `quoted` flag is
`("&ldquo;" in body or "“" in body)` tested against the **raw** body, and the
block is found by the literal regex `<p class="cited-stat">`. Half B requires a
quote glyph with an attribution verb inside the preceding **40 characters of the
same sentence** — `Xcel Energy’s residential rebate summary, ` is longer than
that, so half B never fires on the real template even when the quote is visible.

R1-A1 is worth one extra line, because the gate detected its own blindness and
did nothing with it. Its `LEVEL-DISAGREE` row flipped from
`RAW=2 DEC=2 TXT=2  AGREE` (control) to `RAW=1 DEC=2 TXT=2  DISAGREE` — the gate
computed that the quotation is invisible at RAW, printed DISAGREE, and returned
`VERDICT PASS`, exit 0. Nothing in the gate consumes `DISAGREE`.

### R2 — WRONG-UTILITY CLAIM (config: gci; Johnstown is Xcel gas, so any Atmos attribution on its page is the defect)

Positive control: `public/insulation-johnstown.html` containing
`<p>Atmos Energy pays the insulation rebate in Johnstown.</p>`
→ `R2 RAW 1 ADJ 1 FAIL` exit 1 — **CAUGHT**.

| vector | fixture (verbatim) | result |
|---|---|---|
| R2-B1 | the identical sentence on `public/rebates-hub.html`, `<h1>Insulation Rebate Hub</h1>`, no `areaServed`, no town in the title | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R2-B2 | `<p>Natural gas in Johnstown is delivered by Atmos Energy.</p>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R2-B3 | `<p>atmos energy pays the insulation rebate in Johnstown.</p>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R2-B4 | `<p>At­mos Energy pays the insulation rebate in Johnstown.</p>` (U+00AD soft hyphen inside "Atmos") | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R2-B4z | `<p>Atmos​Energy pays the insulation rebate in Johnstown.</p>` (U+200B zero-width space) | `RAW 1 ADJ 1 FAIL` exit 1 — CAUGHT |
| R2-B4c | `<p>Atmоs Energy pays the insulation rebate in Johnstown.</p>` (Cyrillic о) | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R2-B5 | `<script>var verdict = `+backtick+`Atmos Energy pays the insulation rebate in Johnstown.`+backtick+`; document.body.innerHTML = verdict;</script>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R2-B5q | the same in a single-quoted JS literal (control for the backtick case) | `RAW 2 ADJ 2 FAIL` exit 1 — CAUGHT |
| R2-B6 | `<style>.payer::after{content:"Atmos Energy pays the insulation rebate in Johnstown.";}</style><p class="payer"></p>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R2-B7 | the claim in `<image:caption>` inside `public/sitemap.xml` only | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R2-B8 | `<script>var u = 'At' + 'mos ' + 'Energy'; var verdict = u + ' pays the insulation rebate in Johnstown.';</script>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R2-B9 | `<p>Atmos&nbsp;Energy pays the insulation rebate in Johnstown.</p>` | `RAW 1 ADJ 1 FAIL` exit 1 — CAUGHT |
| R2-B10 | the claim split across two `<td>`s, plus whole in `<option>`, `alt=` and `title=` | `RAW 4 ADJ 4 FAIL` exit 1 — CAUGHT |
| R2-B11 | the claim in `public/llms.txt` only | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R2-B12 | the claim in `public/robots.txt` only | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R2-B13 | `<!-- Atmos Energy pays the insulation rebate in Johnstown. -->` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R2-B14 | `<p>Which gas utility runs the insulation rebate depends on your town, and in Johnstown that utility is Atmos Energy.</p>` | `RAW 1 ADJ 0 PASS` exit 0 — **MISS (filtered)** |
| R2-B15 | `Atmos rebates explained` in `public/og-image.svg`, referenced by nothing | `R2 RAW 0 ADJ 0 PASS` — **MISS** |

Mechanisms, each traced to a line:

- **B1, B11, B12 share one root cause and it is the worst single hole in R2.**
  `ctx.town_scope(art)` resolves a page to towns by basename against
  `R2.towns[*].page_slugs`, then `areaServed` in JSON-LD, then the `<h1>`. When
  none match it returns `[]`, and `allowed_utilities([])` returns `None`, and
  every one of R2's sub-tests then reads
  `if allowed is None or u in allowed: continue`. **A page with no configured
  town is exempt from R2's proposition half, its href half and its cite-key half
  outright.** `llms.txt` and `robots.txt` are read into the sentence pool (proved
  by R3-C13/C14 below, which catch a figure in both) but can never be scoped to a
  town, so they are permanently exempt from R2.
- **B2**: `R2.attribution_words` is a 21-item list; a sentence containing none of
  them is skipped before any utility lookup.
- **B3**: `ctx.utilities_in` calls `which_any(text, names, ci=False)` — utility
  names are matched **case-sensitively**.
- **B4, B4c**: `_wb()` word boundaries over the literal name. `collapse()`
  normalises `\s+`, which in Python 3 includes U+00A0 and U+200B, so `&nbsp;`
  (B9) and the zero-width space (B4z) are absorbed. U+00AD and a Cyrillic
  homoglyph are not whitespace and are not folded by `dec()`'s NFC.
- **B5, B8**: `_JS_STRING` in `surfaces.py` matches only `'...'` and `"..."` —
  **no template literals**. And `ctx.pool()` contains
  `if s.key == S.S_JS and s.locator.endswith("body"): continue`, so the whole-JS
  body surface is excluded from every proposition rule's sentence pool. A
  backtick claim therefore reaches no rule. Runtime concatenation splits into
  three literals none of which matches.
- **B6**: `S_CSS` appears in `ALL_SURFACES` in `surfaces.py` and in
  **no rule's key set anywhere in `claim_gate.py`** (`/usr/bin/grep -n 'S_CSS'
  claim_gate.py` → no matches). Inline CSS is extracted and read by nothing.
  Ruling 2 requires inline CSS to be read; it is extracted, not asserted over.
- **B7**: `S_SITEMAP` likewise appears in no rule key set, and
  `ctx.claim_artifacts()` is `kind in ("html","txt","svg","js")` — `.xml` is
  excluded. Prose in `sitemap.xml` reaches no proposition rule.
- **B13**: `txt()` strips HTML comments before the sentence pool is built.
- **B14**: `f_locked` removes any hit whose sentence contains a string from
  `R2.allowed_multi_utility_sentences`. Embedding one of those four GCI phrases
  in a sentence buys that sentence a blanket exemption for any utility named in
  it. The filter row moves (`count 1 (removed 1)`) and the hit is enumerated
  under "items the filters removed", so Ruling 5's letter holds — but the verdict
  is PASS and the exit code is 0 with the defect live.
- **B15**: `svg_text_for` only resolves SVGs reached through `og:image`,
  `twitter:image` or `<img src>`. An unreferenced `.svg` in `public/` is parsed
  (its `SVGTEXT` surface exists — R5-E8 below catches a statistic in exactly that
  file) but is not a claim artifact for R2, which has no town scope for it.

### R3 — REBATE DOLLAR FIGURE (config: gci)

Positive control: `<p>The Atmos attic rebate pays $1,550 per home.</p>`
→ `RAW 2 ADJ 2 FAIL` exit 1 — **CAUGHT**.

| vector | fixture (verbatim) | result |
|---|---|---|
| R3-C1 | `<p>The Atmos attic rebate pays &#36;95 per window.</p>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R3-C1b | `… pays &#x24;95 per window.` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R3-C1c | `… pays &dollar;95 per window.` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R3-C2 | `… pays ＄1,550 per home.` (U+FF04 fullwidth) | `RAW 1 ADJ 1 FAIL` — CAUGHT |
| R3-C3 | `… pays fifteen hundred and fifty dollars per home.` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R3-C4b | `<title>Attic work</title>` + `<p>Atmos returns 1550 dollars for a finished attic job.</p>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R3-C17 | `<p>Atmos sends 1550 to the homeowner once the attic job is invoiced.</p>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R3-C5 | `<p>The Atmos attic rebate pays 2000 per home.</p>` | `RAW 1 ADJ 0 PASS` exit 0 — **MISS (filtered)** |
| R3-C6 | `<style>.cap::after{content:"$1,550 rebate";}</style><p class="cap"></p>` | `RAW 2 ADJ 0 PASS` exit 0 — **MISS (filtered)** |
| R3-C7 | `… pays $1,550,000 across the program.` | `RAW 3 ADJ 3 FAIL` — CAUGHT |
| R3-C8 | the figure in a backtick template literal | `RAW 2 ADJ 2 FAIL` — CAUGHT |
| R3-C9 | `<script>/* The Atmos attic rebate pays $1,550 per home. */</script>` | `RAW 2 ADJ 2 FAIL` — CAUGHT |
| R3-C10 | `<script>// The Atmos attic rebate pays $1,550 per home.</script>` | `RAW 2 ADJ 2 FAIL` — CAUGHT |
| R3-C11 | the figure only in JSON-LD `acceptedAnswer.text` | `RAW 2 ADJ 2 FAIL` — CAUGHT |
| R3-C12 | the figure only in `<head>` `<meta name="description">` | `RAW 2 ADJ 2 FAIL` — CAUGHT |
| R3-C13 | the figure only in `public/llms.txt` | `RAW 2 ADJ 2 FAIL` — CAUGHT |
| R3-C14 | the figure only in `public/robots.txt` | `RAW 2 ADJ 2 FAIL` — CAUGHT |
| R3-C15 | `<p>The Atmos attic rebate pays $1,<newline>550 per home.</p>` | `RAW 2 ADJ 2 FAIL` — CAUGHT |
| R3-C16 | `<p>Of the measures Atmos rebates, attic insulation pays the most of any single upgrade.</p>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |

Mechanisms. T1's `dollar_pattern` `\$[0-9][0-9,.]*` runs over `art.raw` only,
never over `art.dec`, so any entity-encoded `$` is invisible to T1 (C1, C1b,
C1c). T2's fallback is `\b\d{3,6}\b` over `art.dec` **with a money word required
in a 120-char window**, so a 1–2 digit amount (C1: `95`) or an amount whose
window has no word from the 15-item `money_words` list (C4b, C17) is invisible
too. C3 has no numeral at all. C16's "pays the most" is not in the 15-item
`rank_words` list. C5 is removed by `f_year`
(`re.fullmatch(r"(19|20)\d\d", h.note)`) — **any bare-digit rebate amount
between 1900 and 2099 is filtered as a four-digit year**. C6 is removed by
`f_css` (`h.surface == "CSS"`), so a figure rendered to the visitor through CSS
`content:` is deliberately cleared.

One correction to my own method, recorded: my first `R3-C4` used
`<title>Rebates</title>`, and the word "Rebates" in the title supplied the money
word inside T2's window, so it CAUGHT. I re-ran it as `R3-C4b` with a neutral
title and it MISSES. The earlier CAUGHT was my fixture leaking, not the gate
working.

### R4 — STACKING ASSERTION OR DENIAL (config: gci, whose `R4.programs` includes both names used)

Positive control:
`<p>The Atmos Energy rebates stack on top of the Colorado Weatherization Assistance Program.</p>`
→ `RAW 1 ADJ 1 FAIL` exit 1 — **CAUGHT**.

| vector | fixture (verbatim) | result |
|---|---|---|
| R4-D1 | `<p>Atmos Energy runs one rebate. The Colorado Weatherization Assistance Program runs another. They stack on top of each other.</p>` | `RAW 1 ADJ 0 PASS` exit 0 — **MISS** |
| R4-D2 | `<p>The Atmos Energy rebates and the Colorado Weatherization Assistance Program are cumulative on the same measure.</p>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R4-D3 | `<p>You may claim the Atmos Energy rebate and the Colorado Weatherization Assistance Program at once for the same job.</p>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R4-D3b | `<p>The Atmos Energy rebate and the Colorado Weatherization Assistance Program run concurrently and pay for the same measure.</p>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R4-D4 | the control sentence inside a backtick template literal | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R4-D4b | the same inside a single-quoted JS literal | `RAW 1 ADJ 1 FAIL` — CAUGHT |
| R4-D5 | the control sentence with a newline inside `Colorado Weatherization Assistance\nProgram` | `RAW 1 ADJ 1 FAIL` — CAUGHT |
| R4-D6 | the control sentence only in JSON-LD `acceptedAnswer.text` | `RAW 1 ADJ 1 FAIL` — CAUGHT |
| R4-D7 | the control sentence inside an HTML comment | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |

Mechanism. R4 classifies per sentence and requires **two distinct configured
program names in that one sentence** plus a `stacking_tokens` hit plus a
`combination_predicates` hit. D1 names them in separate sentences, so the
stacking sentence resolves to `NEUTRAL` and is cleared by `f_neutral` — RAW 1,
ADJ 0. D2/D3/D3b assert the same proposition in words absent from the 21-item
token list (`cumulative`, `claim … at once`, `run concurrently`). Program names
are matched `ci=False`.

### R5 — UNCITED STATISTIC (config: gci)

Positive control: `<p>Attic insulation delivers a 35% reduction in heating costs.</p>`
→ `RAW 1 ADJ 1 FAIL` exit 1 — **CAUGHT**.

| vector | fixture (verbatim) | result |
|---|---|---|
| R5-E1 | `<p>Attic insulation delivers a 40 percent reduction in heating costs.</p>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R5-E2 | `<p>Attic insulation cuts heating costs by a third.</p>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R5-E3 | `<p>ENERGY STAR homes differ, but our crews measure a 35% reduction in heating costs.</p>` | `RAW 1 ADJ 0 PASS` exit 0 — **MISS (filtered)** |
| R5-E4 | `<p>Attic insulation delivers a 3&#53;% reduction in heating costs.</p>` | `RAW 1 ADJ 1 FAIL` — CAUGHT |
| R5-E5 | the claim in a backtick template literal | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R5-E6 | the claim only in JSON-LD `knowsAbout[]` | `RAW 1 ADJ 1 FAIL` — CAUGHT |
| R5-E7 | the claim in an inline `<svg><text>` | `RAW 1 ADJ 1 FAIL` — CAUGHT |
| R5-E8 | the claim in a standalone unreferenced `public/chart.svg` | `RAW 1 ADJ 1 FAIL` — CAUGHT |

Mechanism. `R5.magnitude_patterns` has five regexes; `40 percent` matches none
of them (only `[0-9]+ to [0-9]+ percent` covers the spelled form). E2 has no
numeral (declared blind spot, still a live miss for the class). E3 is removed by
`f_pub` — **naming any of the 17 `recognised_publishers` anywhere in the sentence
exempts the sentence**, whether or not that publisher is the source. Note also
`f_instat`: if ANY cited-stat on the page contains the same numeral substring,
every other occurrence of that numeral on the page is cleared page-wide.

### R6 — SELF-CONTRADICTING OUTPUT

Full table in section 0 above. Fixtures were a `public/calc.html` carrying the
chain in an inline `<script>`, with a scratch config whose chain named
`printed_var: "pctShort"`, the four real labels, the real `severity_order`, the
real `at_target_label`, `targets: {basement:15, crawl-encap:15,
wall-existing:13}`, `surfaces: ["public/calc.html"]` and `generator:
"clean_gen.js"` (a clean copy at the repo root, needed only so the negative
controls would not false-alarm — see section (a)).

Positive control (`gap >=` branches, `pctShort` printed), verbatim output:

```
━━━ R6  SELF-CONTRADICTING OUTPUT ━━━
  kind: CLAIM TEST
  RAW              label-emitting conditional chains examined     5
  ADJUDICATED      chains whose branch quantity is not the printed quantity 5
  LEVEL-DISAGREE   RAW=3 DEC=3 TXT=0                              DISAGREE
  VERDICT          FAIL — 5 adjudicated finding(s) stand after 0 filter(s)
  --- 5 hits, enumerated ---
  public/calc.html:JS[0]:JS  G1  branch reads {gap} while the printed string interpolates {pctShort} | Moderately under code — % short of target.  [G1]
  public/calc.html:JS[0]:JS  G1  branch reads {gap} while the printed string interpolates {pctShort} | Significantly under code — % short of target.  [G1]
  public/calc.html:JS[0]:JS  G2  threshold 20 on {gap} is unreachable for basement (targetMin 15) while the printed quantity can reach 100  [G2]
  public/calc.html:JS[0]:JS  G2  threshold 20 on {gap} is unreachable for crawl-encap (targetMin 15) while the printed quantity can reach 100  [G2]
  public/calc.html:JS[0]:JS  G2  threshold 20 on {gap} is unreachable for wall-existing (targetMin 13) while the printed quantity can reach 100  [G2]
```

Misses, all four with a printed block byte-identical to the repaired form:

- **R6-F1, minified onto one line.** `_js_label_chain` iterates
  `js_text.splitlines()` and regex-matches `^if (...) {` / `^} else if (...) {`
  per line. One line, no match, `found == []`.
- **R6-F2, nested ternary.** No `if` statement to match.
- **R6-F4, `switch (true) { case gap >= 20: ... }`.** No `if` statement.
- **R6-F5, two severity words beside the same percentage** — duplicate
  `pctShort >= 50` branches, so a visitor at 60% short can be told
  "Significantly under code" or "Moderately under code" depending on branch
  order. G1 does not fire (the branch does read `pctShort`). G2's monotonicity
  test is `thr != sorted(thr, reverse=True)`, and `[50, 50]` is already
  reverse-sorted, so equality passes. **The named defect class has no test.**

Caught, for completeness: **R6-F3** (the `if` condition wrapped across three
lines) `RAW 3 ADJ 3 FAIL` — but by accident: the reported hits include
`G2 branch thresholds [0, 8] are not monotone decreasing`, a mis-derivation from
the broken parse, not the branch/print identity test. **R6-F6** (the label split
across a JS string-concatenation boundary, `'Significantly ' + 'under code — '`)
`RAW 5 ADJ 5 FAIL` — genuinely caught, because `_js_label_chain` joins all
string literals on the RHS before matching.

### R7 — SUPERSEDED-SOURCE CLAIM (config: gci; propositions live in common.json)

Positive control:
`<p>The heat pump must be installed and invoiced by December 31, 2026.</p>`
→ `RAW 1 ADJ 1 FAIL` exit 1 — **CAUGHT**.

| vector | fixture (verbatim) | result |
|---|---|---|
| R7-G1 | `<p>The heat pump must be installed and invoiced by Dec. 31, 2026.</p>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R7-G1b | `<p>Work must be installed and invoiced by Dec. 31 to earn the bonus.</p>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R7-G2 | `<p>Rebate terms are set out in schedule 24‑02‑205 for Colorado.</p>` (U+2011 non-breaking hyphens) | `R7 RAW 0 ADJ 0 PASS` — **MISS** |
| R7-G2b | `… schedule 24&#45;02&#45;205 …` | `RAW 1 ADJ 1 FAIL` — CAUGHT |
| R7-G3 | `Air sealing is a prerequisite for the Whole Home Efficiency bonus.` in a backtick literal | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R7-G4 | the same proposition in a `<note>` inside `public/sitemap.xml` only | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R7-G5 | the same proposition wrapped across a source line break | `RAW 1 ADJ 1 FAIL` — CAUGHT |
| R7-G6 | `Air sealing is a pre&#8209;requisite for the Whole Home Efficiency bonus.` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |

**G1 and G1b are the sharpest single finding in this section**, because the
config's own `why` field says so. `R7.superseded_propositions` entry
`installed_and_invoiced_by_dec_31_2026` lists as `any_of`:
`"invoiced by Dec. 31, 2026"` and `"installed and invoiced by Dec. 31"`, with the
note *"the short form Dec. 31, 2026 survived four further rounds because every
sweep searched the long form."* Both patterns are **unfirable**, because R7's
proposition half matches per sentence and `surfaces.sentences()` splits at
`Dec.`. Proved directly:

```
  configured R7 any_of pattern : 'invoiced by Dec. 31, 2026'
  the pattern IS present in the page text: True
  but R7 matches per SENTENCE, and the sentences are:
    'The heat pump must be installed and invoiced by Dec.'   -> contains the pattern? False
    '31, 2026.'                                              -> contains the pattern? False
  => the configured pattern can never match any sentence. UNFIRABLE.
```

The R7 positive control still reports `DETECTED (7: A,B)` because six other
propositions and the identifier half fire — another instance of a control
passing on a different sub-test than the one that is broken.

### R8 — STALE REVIEW DATE (config: gci)

Positive control:
`<p>Last reviewed: <time datetime="2027-01-01">January 1, 2027</time></p>`
→ `RAW 2 ADJ 2 FAIL` exit 1 — **CAUGHT**.

| vector | fixture (verbatim) | result |
|---|---|---|
| R8-H1 | `<p>Last reviewed: January 1, 2027</p>` (no `<time>` element) | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R8-H2 | `<time datetime="2027-01-01T00:00:00Z">January 1, 2027</time>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R8-H3 | the same impossible date on `public/privacy.html` (an `own_effective_date_pages` entry) | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R8-H4 | the same impossible date on `public/404.html` (an `exempt_pages` entry) | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R8-H5 | the same impossible date on `public/about.html` (a `pinned_pages` entry) | `RAW 2 ADJ 2 FAIL` — CAUGHT |
| R8-H6 | `<time datetime="2026&#45;08&#45;24">` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |

Mechanisms. R8 builds its date set from `art.time_elements` (requires a literal
`<time datetime>`) and JSON-LD `dateModified`/`datePublished`, gated by
`re.fullmatch(r"\d{4}-\d{2}-\d{2}", dt)` — a full ISO timestamp (H2) or
entity-encoded hyphens (H6) fail the fullmatch and the page contributes no dates
at all, then `if not dates: continue`. `R8.footer_marker` is configured as
`"Last reviewed:"` and **read by no code path**, so a plain-text review date
(H1) is invisible. H3/H4 are skipped by `if base in exempt or base in own:
continue`, which runs **before** any hit is raised — see section (d).

### R9 — INTERNAL CONTRADICTION (config: dci with `R6.label_chains` emptied, needed only to get past the R6-driven control abort)

Positive control: a page carrying both configured `value_slots` for
`xcel_cfm50_scope` → `RAW 1 ADJ 1 FAIL` exit 1 — **CAUGHT**.

| vector | fixture (verbatim, the second paragraph) | result |
|---|---|---|
| R9-I1 | `<p>Both the attic rebate and the air sealing rebate turn on the CFM 50 number.</p>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R9-I2 | `Xcel insulation and air sealing rebates require a documented 20% reduction in CFM 50.` in a backtick literal | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |

R9 is a registry of eight configured subjects with literal `value_slots`
strings. A paraphrase of a contested value is invisible. This is a declared
blind spot; it is still the reason a contradiction has to be found by a human
first.

### R10 — DANGLING PROMISE (same config)

Positive control: `<p>The <a href="/guide.html">standard rebate guide</a> covers
the base amounts.</p>` pointing at a page with no figure → `RAW 1 ADJ 1 FAIL`
exit 1 — **CAUGHT**.

| vector | fixture (verbatim) | result |
|---|---|---|
| R10-J1 | `<p>The real numbers live on the <a href="/guide.html">standard rebate guide</a>.</p>` | `RAW 0 ADJ 0 PASS` exit 0 — **MISS** |
| R10-J2 | the control promise pointing at `/missing.html`, which does not exist | `RAW 1 ADJ 0 PASS` exit 0 — **MISS (filtered)** |

J1 is outside the 14 `promise_patterns` regexes. J2 is cleared by `f_notinset`
("destination outside the read set → REVIEW, not FAIL"), so **a promise pointing
at a page that does not exist is downgraded to a pass.**

### R11 — ATTRIBUTION DEBT

Report-only, never changes the exit code, and as shown in (a) its control is
vacuous. No adversarial vector was constructed for R11 beyond the control-repair
test, because the rule emits one row per configured term unconditionally and has
nothing to evade. **Labelled NOT TESTED for evasion.**

### THE MISSES, as the headline list

Forty-two distinct adversarial vectors were run. **Thirty-one MISSED**:

R1-A1, R1-A1x, R1-A2, R1-A3, R1-A4, R1-A5, R1-A6 (7 of 7 — R1's claim-test half
sees exactly one spelling) · R2-B1, R2-B2, R2-B3, R2-B4, R2-B4c, R2-B5, R2-B6,
R2-B7, R2-B8, R2-B11, R2-B12, R2-B13, R2-B14, R2-B15 (14 of 18) · R3-C1, R3-C1b,
R3-C1c, R3-C3, R3-C4b, R3-C17, R3-C5, R3-C6, R3-C16 (9 of 19) · R4-D1, R4-D2,
R4-D3, R4-D3b, R4-D4, R4-D7 (6 of 9) · R5-E1, R5-E2, R5-E3, R5-E5 (4 of 8) ·
R6-F1, R6-F2, R6-F4, R6-F5 (4 of 7 non-control variants, including the named
defect class) · R7-G1, R7-G1b, R7-G2, R7-G3, R7-G4, R7-G6 (6 of 8) · R8-H1,
R8-H2, R8-H3, R8-H4, R8-H6 (5 of 6) · R9-I1, R9-I2 (2 of 2) · R10-J1, R10-J2
(2 of 2).

Cross-cutting causes, in order of how many rules they disable:

1. **The JS template literal.** `_JS_STRING` has no backtick branch and
   `ctx.pool()` drops the whole-JS-body surface. Defeats R1, R2, R4, R5, R7, R9
   in one move.
2. **Town scope resolving to `None`.** Exempts every non-town page from all of
   R2. Ruling 7's load-bearing rule does not apply to most of the property.
3. **Case-sensitive name matching.** `ci=False` on utility names and program
   names defeats R2 and R4.
4. **HTML comments.** Stripped by `txt()` before the pool; defeats R1, R2, R4,
   R7 while R3 (which reads RAW) still sees them.
5. **Entity-encoded delimiters.** The `$` for R3 T1, the quote glyphs for R1,
   the hyphens in a `<time datetime>` for R8.
6. **The sentence splitter.** Breaks at `Dec.`, `No.`, `Corp.`, `Inc.`, `U.S.`,
   `approx.`, `Sec.` and the ellipsis; joins across `.”`.
7. **`sitemap.xml` and inline CSS** being extracted but present in no rule's key
   set.

---

## (c) Corpus verification

My own enumeration versus the gate's, per property:

| | DCI mine | DCI gate | LGM mine | LGM gate | GCI mine | GCI gate |
|---|---|---|---|---|---|---|
| `find public -type f` | 85 | 85 | 59 | 59 | 49 | 49 |
| `git ls-files public/` | 85 | 85 | 59 | 59 | 49 | 49 |
| html | 75 | 75 | 48 | 48 | 38 | 38 |
| txt | 3 | 2 read | 3 | 2 read | 3 | 2 read |
| xml | 1 | 1 | 1 | 1 | 1 | 1 |
| svg | 2 | 2 | 3 | 3 | 3 | 3 |
| png | 3 | excluded | 3 | excluded | 3 | excluded |
| ico | 1 | excluded | 1 | excluded | 1 | excluded |
| read set | — | 80 | — | 54 | — | 44 |
| excluded | — | 5 | — | 5 | — | 5 |

The gate's own lines, verbatim:

```
corpus: git ls-files public/ = 85   find public/ -type f = 85   AGREE
read set: 80 artifacts (75 html, 2 txt, 1 xml, 2 svg)  |  excluded: 5 (binary-raster:4, indexnow-key-file:1)
corpus: git ls-files public/ = 59   find public/ -type f = 59   AGREE
read set: 54 artifacts (48 html, 2 txt, 1 xml, 3 svg)  |  excluded: 5 (binary-raster:4, indexnow-key-file:1)
corpus: git ls-files public/ = 49   find public/ -type f = 49   AGREE
read set: 44 artifacts (38 html, 2 txt, 1 xml, 3 svg)  |  excluded: 5 (binary-raster:4, indexnow-key-file:1)
```

**My enumeration agrees with the gate exactly on all three properties.**
75 + 2 + 1 + 2 = 80 read + 5 excluded = 85. Same arithmetic on LGM and GCI.

**Enumerated from `public/`, not from `sitemap.xml` — proved two ways.**
(i) DCI's `sitemap.xml` carries 73 `<loc>` entries against 75 html files in
`public/`; the pages absent from the sitemap are `404.html` and
`r-value-needed-calculator-embed.html` — and `r-value-needed-calculator-embed.html`
is named 2 times and `404.html` 3 times in the DCI report, so both are read.
The embed frame Ruling 1 names is exactly one of the two artifacts a
sitemap-driven sweep would have lost. (ii) Directly: an adversarial repo whose
`sitemap.xml` listed only `index.html` and a page that does not exist, with the
defect on an un-sitemapped `insulation-johnstown.html`, returned
`exit 1 ; R2 (1, 1, 'FAIL') ; R3 (2, 2, 'FAIL')`.

**`llms.txt` and `robots.txt` are both in the read set.** The 2 txt artifacts per
property are `llms.txt` and `robots.txt` (the third `.txt` is the IndexNow key
file, excluded by name). Independently confirmed by content: R3-C13 (figure in
`llms.txt` only) → `RAW 2 ADJ 2 FAIL`; R3-C14 (figure in `robots.txt` only) →
`RAW 2 ADJ 2 FAIL`.

**Every artifact the gate does not read, and whether the exclusion is a stated
decision:**

| unread artifact | reason | stated? |
|---|---|---|
| `public/favicon.ico` | `binary-raster` (extension) | YES — counted in the read-set line and named in KNOWN HOLES |
| `public/favicon.png` | `binary-raster` | YES |
| `public/og-image.png` | `binary-raster` | YES — DCI's config carries `og_image_raster_only: true` and the KNOWN HOLES line says "TOTAL on this property" |
| `public/google-preferred-source-badge.png` | `binary-raster` | YES |
| `public/<32-hex>.txt` (IndexNow key) | `key_files_excluded`, per property | YES |

No unstated exclusion exists on any of the three properties. Two qualifications
I would not call oversights but would not call safe either:

- The exclusion is by **file extension**, not by content sniffing. A defect
  placed in a file *named* `.png`/`.pdf`/`.webp`/`.ico` is invisible regardless
  of what is actually in it.
- `S_SITEMAP` and `S_CSS` artifacts *are* in the read set but are in **no rule's
  key set**, so the read is not an assertion. That is an implementation gap, not
  a corpus gap, and it is not stated anywhere.

**Smuggling a defect into an excluded artifact.** The string
`Atmos Energy pays the $1,550 insulation rebate in Johnstown.` placed in each
excluded class, under GCI's real config:

| host artifact | R3 RAW | R3 ADJ | exit | read-set line |
|---|---|---|---|---|
| `public/deadbeef.txt` (a `key_files_excluded` entry) | 0 | 0 | 0 | `3 artifacts … excluded: 1 (indexnow-key-file:1)` |
| `public/og-image.png` | 0 | 0 | 0 | `3 artifacts … excluded: 1 (binary-raster:1)` |
| `public/favicon.ico` | 0 | 0 | 0 | `3 artifacts … excluded: 1 (binary-raster:1)` |
| `public/hero.webp` | 0 | 0 | 0 | `3 artifacts … excluded: 1 (binary-raster:1)` |
| `public/rebate.pdf` | 0 | 0 | 0 | `3 artifacts … excluded: 1 (binary-raster:1)` |
| `public/data.json` (not excluded — control) | 2 | 2 | 1 | `4 artifacts … excluded: 0 ()` |

**Confirmed invisible in every excluded class**, with the `.json` control proving
the pipeline works. The exclusion count does move in the read-set line, so the
hole is visible to a reader who looks — it is stated, not silent.

---

## (d) The bare-zero audit, including the silently-dropped-real-hit test

Every rule block was parsed for a `RAW` row, a `FILTER` row and an
`ADJUDICATED` row.

**On a genuinely clean corpus (3 artifacts, exit 0):**

```
   R1   RAW=0  filters_printed=True   ADJ=0
   R2   RAW=0  filters_printed=True   ADJ=0
   R3   RAW=0  filters_printed=True   ADJ=0
   R4   RAW=0  filters_printed=True   ADJ=0
   R5   RAW=0  filters_printed=True   ADJ=0
   R6   RAW=0  filters_printed=False  ADJ=0    <-- NO FILTER LINE AT ALL
   R7   RAW=0  filters_printed=True   ADJ=0
   R8   RAW=0  filters_printed=True   ADJ=0
   R9   RAW=0  filters_printed=True   ADJ=0
   R10  RAW=0  filters_printed=True   ADJ=0
   R11  RAW=0  filters_printed=False  ADJ=0    <-- NO FILTER LINE AT ALL
```

**On a failing run (exit 1, R2 ADJ 1, R3 ADJ 2):** identical picture — R6 and
R11 again print no filter row.

**Rule with nothing configured.** R6 under GCI (`label_chains: []`) prints
`RAW 0`, `ADJUDICATED 0`, and
`note: NULL RESULT -- 0 label chains configured for this property. Registering
one later is a config entry.` R11 under GCI (`tracked_terms: []`) prints
`RAW 0`, `ADJUDICATED 0`, and
`note: R11: 0 tracked terms configured for gci -- reported as a null result, NOT
as PASS`. Both are honest null results and neither is a bare zero. **But when
R6 has a chain configured and the scanner finds nothing, the note disappears and
`RAW 0` is the only number printed — no chains-examined count, no
assignments-found count, no note.** That is the gap in section 0.

**Rule whose every hit was filtered.** R3-C5 (`2000`) → `RAW 1`, the year filter
row reads `count 1 (removed 1)`, `ADJUDICATED 0`, verdict PASS. R2-B14 → `RAW 1`,
`f_locked` row `count 1 (removed 1)`, `ADJUDICATED 0`. In both cases the removed
item is enumerated under "items the filters removed". **Ruling 5's letter is
met.** But the verdict is PASS and the exit code is 0, and under `--brief` only
the counts survive.

**Property missing an artifact class entirely.** A repo with no `.svg`, no
`.xml` and one `.html`: `read set: 3 artifacts (1 html, 2 txt, 0 xml, 0 svg)`.
Explicit zeroes for the missing classes. Note the breakdown only enumerates four
kinds; `kinds` also accumulates `js` and any other extension, which are counted
in the total but not in the parenthesised breakdown, so the breakdown does not
always sum to the total.

### The harder half of Ruling 5: a filter that silently drops a real hit

The README states: *"A run whose filter silently dropped a real hit must not
look identical to a clean run."* **Falsified twice.** In both cases the hit is
dropped *before* it is ever raised, so no `RAW`, no `FILTER` and no
`ADJUDICATED` number moves.

**Case 1 — an impossible review date on an exempt page.** GCI's
`R8.exempt_pages` is `["404.html"]`. Fixture:
`public/404.html` containing
`<p>Last reviewed: <time datetime="2027-01-01">January 1, 2027</time></p>` —
a date 3.5 months in the future, on a page the gate reads. The R8 block, in full:

```
━━━ R8  STALE REVIEW DATE ━━━
  kind: CLAIM TEST
  RAW              published date surfaces compared               0
  FILTER           pinned_pages (visible text unchanged; JSON-LD only) 0    (removed 0)
  FILTER           own_effective_date_pages / exempt_pages (excluded before match) 0    (removed 0)
  ADJUDICATED      dates impossible, contradicted, or preceding their content 0
  LEVEL-DISAGREE   RAW=1 DEC=1 TXT=1                              AGREE
  VERDICT          PASS — 0 adjudicated findings from 0 raw match(es) across 2 filter(s)
  --- 0 hits, enumerated ---
  (none)
  --- 0 items the filters removed, enumerated ---
  (none)
```

`exit 0`. `difflib` against the clean run's R8 block differs in **exactly one
line**: `LEVEL-DISAGREE RAW=0 DEC=0 TXT=0 AGREE` becomes `RAW=1 DEC=1 TXT=1
AGREE` — an incidental count of the strings `"Last reviewed"` and `"<lastmod>"`
that names neither the page nor the date. On the real GCI property that same
counter reads `RAW=75 DEC=75 TXT=75`, so the trace a smuggled date leaves is
`75 → 76` in a diagnostic row that says AGREE.

Worse: the filter row that names the exclusion is **dead code**.

```python
def f_known(h):
    return False
...
Filt("own_effective_date_pages / exempt_pages (excluded before match)", f_known),
```

It can only ever print `0 (removed 0)`. The gate prints a row whose label claims
to account for exempt pages and whose value asserts that nothing was excluded,
while a page was in fact excluded before any hit was raised. That row does not
reduce confidence; it manufactures it.

**Case 2 — the wrong-utility claim on a page with no configured town.** Fixture:
`public/rebates-hub.html` containing
`<h1>Insulation Rebate Hub</h1><p>Atmos Energy pays the insulation rebate in
Johnstown, Milliken and Severance.</p>` under GCI's real territory. `exit 0`.
`difflib` against the clean run's R2 block differs in **exactly one line**, again
the `LEVEL-DISAGREE` counter (`RAW=0 DEC=0 TXT=0` → `RAW=1 DEC=1 TXT=1`). All
five filter rows read `0 (removed 0)`. `RAW 0`. `ADJUDICATED 0`. `VERDICT PASS`.
On the real GCI property that counter reads `RAW=178 DEC=178 TXT=176`.

### Can the filter arithmetic be satisfied by a rule that miscounts both ways?

**The assertion is structurally unreachable.** `adjudicate()` starts
`remaining = list(raw_hits)`; each removing filter partitions `remaining` into
`removed` and `keep`; non-removing filters contribute an empty `removed`. So
`sum(len(removed)) + len(remaining) == len(raw_hits)` is an identity, not a
check. Demonstrated by calling it directly with five hits and four filters, two
of which claim all five:

```
   f-all            count=5 removed=5
   f-all-again      count=5 removed=0
   f-none           count=0 removed=0
   f-report-only    count=5 removed=0
   adjudicated=0 ; sum(removed)+adjudicated = 5 = raw 5 -> the guard cannot trip
```

The README's *"The gate asserts `raw − removed == adjudicated` and exits 2 if
that identity fails"* describes a guard that cannot fail. It also does not
constrain the printed `FILTER` counts, which are computed over **all** raw
candidates rather than the remaining set — so `f-all-again` prints `count=5
(removed 0)` and the arithmetic still holds. A reader adding the `count` column
does not get `raw`.

---

## (e) Determinism, and anything time-, order- or locale-dependent

All runs against the real GCI repo at `ee0157d`, comparing full `--report`
output with `cmp`:

| test | result |
|---|---|
| same input, run twice | `RUN1 == RUN2 byte for byte` |
| different working directory (`cd /`) | `CWD-INDEPENDENT: identical` |
| different `CANON_ROOT` (the scratch mirror) | `CANON_ROOT-INDEPENDENT: identical` |
| `PYTHONHASHSEED=0`, `=1`, `=12345` | `HASH-SEED-INDEPENDENT: all three identical` |
| `LC_ALL`/`LANG` = `C`, `en_US.UTF-8`, `tr_TR.UTF-8`, `de_DE.UTF-8` | `LOCALE-INDEPENDENT (C vs tr_TR): identical` |
| `TZ` = `UTC`, `Pacific/Kiritimati`, `Pacific/Niue` | `TZ-INDEPENDENT: identical` |

**Determinism holds on every axis tested.** `os.walk` is wrapped with
`dirs.sort()` and `sorted(files)`, the read set is `sorted(set(ls_files) |
set(found))`, `_ld_leaves` sorts dict keys, `which_any` returns
`sorted(set(...))`, and hits are printed `sorted(..., key=sortkey)`. I did not
physically re-create the filesystem in a different creation order; the sort calls
plus the hash-seed invariance are the evidence, and I am labelling the physical
re-order **NOT TESTED**.

**Wall clock.** `/usr/bin/grep -n 'time\.|datetime|date\.today|strftime|localtime|utcnow'`
over both modules finds `time.time()` in exactly two places: `t0 = time.time()`
in `main` and the stderr line `claim_gate: %.2fs, exit %d`. The as-of date comes
from `config.R8.today` or `--today`, never from the clock. **Crossing a date
boundary changes nothing.** Verified: `--today 2026-09-17` versus `--today
2026-09-18` produced a one-line diff, the header's `as-of` field, and nothing
else.

Two `--today` defects, on either side of a narrow usable window:

- **An unparseable value is accepted silently.** `--today not-a-date` →
  `exit 1`, header reads `as-of not-a-date`, `R8 RAW 39 ADJ 38 FAIL`. R8's
  part (b) compares `v > today` as strings, so with `today = "not-a-date"` no
  date is ever "after today" and the future-date test is disabled without a
  word. No validation anywhere.
- **Any value before 2026-08-07 aborts the whole gate.** `--today 2026-08-01` →
  `exit 2`, `1 FALSE ALARM` on `NEG11`, `CLAIM GATE: NOT RUN`, because the
  negative fixture carries a hardcoded 2026-08-07 date.

`--today ""` is falsy and falls back to the config — benign.

---

## (f) The read-only / writes-nothing proof

Method: `stat -f '%N %z %m %p'` (path, size, mtime, inode) over every file in
all four repos with `.git` excluded, before and after running the gate on all
three properties, plus a `find -newermt` sweep against a timestamp taken before
the runs.

```
=== running the gate on all three properties ===
dci exit 1
lgm exit 1
gci exit 1

=== diff of (path size mtime inode) over all four repos, .git excluded:
*** NO FILE ADDED, REMOVED, RESIZED, RE-INODED OR MTIME-CHANGED IN ANY OF THE FOUR REPOS ***

=== any file in any repo modified since the mark? (find -newermt):
  denvercoloradoinsulation.com: 0
  longmontcoloradoinsulation.com: 0
  greeleycoloradoinsulation.com: 0
  calibrated-design-canon: 0
```

`git status --porcelain` in each property after the runs: empty.

The gate also self-checks: `run_controls` snapshots `public/` mtimes before and
after the control phase and prints
`public/ mtimes unchanged across the control phase: 85 files verified` (49 on
GCI, 59 on LGM).

**Network.** `/usr/bin/grep -n 'urllib|requests|socket|http\.client|urlopen|curl|ssl'`
over both modules returns exactly one line — the string
`"assume (spec 6, 7.3); no browser, no outbound requests"` inside a message.
**No network module is imported or referenced anywhere.** The only external
processes are `git` (`subprocess.run(["git"] + args)`) and one long-lived
`git cat-file --batch`.

**Bytecode.** Clean-room test on a fresh copy:

```
-- before:            claim_gate.py  config  fixtures  surfaces.py
script-run exit 0
-- after a SCRIPT run: claim_gate.py  config  fixtures  surfaces.py
-- after an IMPORT:    __pycache__  claim_gate.py  config  fixtures  surfaces.py
                       __pycache__/claim_gate.cpython-314.pyc
```

**Running it as a script writes nothing** — `sys.dont_write_bytecode = True` is
set before `import surfaces`, and the comment in the source says so. **Importing
the module writes `__pycache__/claim_gate.cpython-*.pyc` next to the
implementation**, because the flag is set inside the module body, after the
import machinery has already cached the module being imported. Canon's working
tree currently contains exactly that:

```
-rw-r--r--  171472  Sep 17 13:47  ops/claim_gate/__pycache__/claim_gate.cpython-314.pyc
-rw-r--r--   39688  Sep 17 13:49  ops/claim_gate/__pycache__/surfaces.cpython-314.pyc
$ git check-ignore -v ops/claim_gate/__pycache__/
.gitignore:2:__pycache__/	ops/claim_gate/__pycache__/
```

Gitignored, so invisible to `git status`, and pre-existing before this pass
began. The docstring's *"The gate writes NOTHING into the repo it is run from or
the repo it lives in"* holds for the script entry point only.

**The `--report` path.** `--report /tmp/.../deep/a/b/c/out.txt` created the
nested directories and wrote one 4179-byte file, `exit 0`. That is the one
documented write and it behaves as documented.

---

## (g) All four repos' state, verbatim

At the start of the pass:

```
=== denvercoloradoinsulation.com ===
main
1b6949c0ade3a7b7825e0d36916e9f38d5b0da62
--- ahead/behind:
0	0
=== longmontcoloradoinsulation.com ===
main
a86c5afac76e23d05ebc261fdfbda9c4a33eee0c
--- ahead/behind:
0	0
=== greeleycoloradoinsulation.com ===
main
ee0157d7fee1a46cdc9d9e3da0e18f37bcf23fe7
--- ahead/behind:
0	0
=== calibrated-design-canon ===
main
4bf5373b6e8deebd8237329843343462f7f58e5c
--- ahead/behind:
0	1
```

`git status --porcelain` was empty in all four. The counts are
`git rev-list --left-right --count origin/main...HEAD`, i.e. left = commits only
on `origin/main`, right = commits only on `HEAD`. The three property repos are
`0 0`. **Canon is `0 1`: one commit ahead of `origin/main`, unpushed, and not
mine** — it was already there when I arrived (the session's own recent-commit
list named `b152b08` as HEAD while the live HEAD was `4bf5373`, so another agent
committed in between). I did not push it and did not touch it.

No page, generator or `public/` artifact changed anywhere — proved in (f) by a
before/after `stat` diff over all four repos that returned no differences at all.
No live site was contacted: the gate makes no outbound request and this pass ran
no `curl`, `ssh` or deploy.

I created **no git worktrees**; there are none to remove or prune. All scratch
work lives in `/tmp/claim-gate-scratch/r4`, including a mirrored copy of
`ops/claim_gate/` and a purpose-built throwaway git repo at
`/tmp/claim-gate-scratch/r4/adv`, neither of which is inside any of the four
checkouts.

---

## (h) Every crash, hang and exit-code anomaly, with its reproduction

Twenty-one malformed inputs were run against GCI's real config in the
adversarial repo.

### CRASH 1 — deeply nested JSON-LD, uncaught `RecursionError`, **exit 1**

This is the worst failure mode named in the brief: a crash that exits with the
same code the gate uses for "a blocking rule FAILED".

Reproduction — a single artifact:

```html
<!DOCTYPE html><html lang=en><head><title>Page</title></head><body>
<script type="application/ld+json">[[[[ … 2000 deep … ]]]]</script><p>x</p>
</body></html>
```

Result:

```
exit code: 1
--- last 6 lines of STDOUT:
(empty)
--- STDERR:
Traceback (most recent call last):
  File ".../claim_gate.py", line 2698, in <module>
    sys.exit(main())
  File ".../claim_gate.py", line 2552, in main
    art = S.parse_artifact(rel, p, embeds)
  File ".../surfaces.py", line 492, in parse_artifact
    _parse_html(art)
  File ".../surfaces.py", line 379, in _parse_html
    _ld_leaves(parsed, "LD[%d]" % i, leaves)
  File ".../surfaces.py", line 294, in _ld_leaves
    _ld_leaves(v, "%s[%d]" % (path, i), out)
  [Previous line repeated 993 more times]
RecursionError: maximum recursion depth exceeded
```

`json.loads` succeeds; `_ld_leaves` is unguarded recursion. The crash happens in
`main`'s parse loop **before any rule runs**, so **stdout is completely empty** —
no header, no corpus line, no `CLAIM GATE:` line — and the only signal is a
traceback on stderr. A CI job that tests `$?` reads "1 = a rule failed". A human
reading the report file sees nothing at all. Also reproduced at 4000-deep with
`{"a": …}` nesting: same `exit 1`, no `CLAIM GATE:` line.

### ANOMALY 2 — a non-ASCII filename in `public/` makes the gate refuse to run

`git ls-files` C-quotes non-ASCII paths and the gate does not use `-z` or
`-c core.quotePath=false`, so its own corpus cross-check diverges on a perfectly
consistent repo:

```
corpus: git ls-files public/ = 4   find public/ -type f = 4   DIVERGE
  corpus divergence: tracked but absent from the working tree: "public/a b\303\251\303\251.html"
  corpus divergence: in the working tree but untracked: public/a béé.html
CLAIM GATE: NOT RUN
exit 2
```

`git ls-files public/` returns `"public/a b\303\251\303\251.html"` verbatim.
Latent today: `git ls-files public/ | /usr/bin/grep -c '^"'` returns **0** on all
three properties, so no current page triggers it.

### ANOMALY 3 — `--peer` is accepted, validated nowhere, wired to nothing

`/usr/bin/grep -n 'peer' claim_gate.py` returns five lines: the
`add_argument`, two prose strings, an unconditional
`res.notes.append("R9 CROSS-PROPERTY HALF SKIPPED: no --peer given")` inside
`rule_R9` that ignores `args.peer` entirely, and `if not args.peer:` in the
summary. The peer repo is never opened.

```
$ ./ops/claim_gate.sh --peer ~/code/denvercoloradoinsulation.com --report peer.txt  ; exit 1
$ diff gci-base.txt peer.txt
1098d1097
<   R9 CROSS-PROPERTY HALF SKIPPED: no --peer given
```

**The only effect of passing `--peer` is to delete the line that discloses the
cross-property half did not run.** A nonsense path behaves identically:
`--peer /nonexistent/path` produced a file `diff -q`-identical to the valid-peer
run. R9's cross-property half does not exist, and passing the flag makes the
summary stop saying so.

### ANOMALY 4 — `--canary` bypasses `min_artifacts`

```
$ ... --config <min_artifacts 49> --repo <3-artifact repo> --canary
CLAIM GATE: CANARY OK — control phase only, no rule ran against /tmp/claim-gate-scratch/r4/adv
exit 0
```

The `ZERO-ARTIFACT TRAP` check sits **after** the `--canary` early return in
`main`, so a green canary is available on a gutted property. The README tells a
new-property operator to run `--canary` as step 3 of onboarding.

### ANOMALY 5 — `min_artifacts` is satisfiable by junk, and `expected_html` is never read

`/usr/bin/grep -n 'expected_html' claim_gate.py surfaces.py` returns exactly one
line: `for req in ("key", "repo", "min_artifacts", "expected_html"):` in
`load_config`. The key is **required to be present and never compared to
anything.** With `min_artifacts: 49, expected_html: 38` against a repo of 51
one-byte `.txt` files plus one html:

```
corpus: git ls-files public/ = 52   find public/ -type f = 52   AGREE
read set: 52 artifacts (1 html, 51 txt, 0 xml, 0 svg)  |  excluded: 0 ()
  blocking failures: 0
CLAIM GATE: PASS
exit 0
```

A property that lost 37 of its 38 pages passes the zero-artifact trap and every
rule. The trap itself does work when the total is short — 40 artifacts against
`min_artifacts: 49` gave `exit 2` and the full explanatory message — but it
counts artifacts, not pages.

### ANOMALY 6 — `--opt-in=R6b` makes every run exit 2 with no rule output

```
$ ./ops/claim_gate.sh --opt-in=R6b
  canary+ R6b-G3   (opt-in, browser cross-product)   *** MISSED *** R6b requires a Chrome binary this gate cannot assume (spec 6, 7.3); no browser, no outbound requests
  CONTROLS: 20 positive DETECTED, 1 MISSED · 14 negative clean, 0 FALSE ALARM
CLAIM GATE: NOT RUN — a rule that cannot detect its own defect is worse than no rule, because it manufactures confidence.
exit 2
```

This is honest and the README says it is deliberate. It is also
**unconditional**: `run_controls` hardcodes the MISSED row whenever `"R6b" in
opt_in`, so the flag can never produce a run, and `--canary --opt-in=R6b` also
exits 2. An operator who puts the documented flag in CI gets a permanent red
with the other ten rules never evaluated. `--opt-in=R99` is rejected cleanly:
`CONFIG ERROR: unknown --opt-in rule 'R99' (known: R6b)`, exit 2.

### Inputs that did NOT crash

| input | exit | verdict line |
|---|---|---|
| malformed JSON-LD (trailing comma, unquoted key) | 0 | `CLAIM GATE: PASS` |
| JSON-LD that is a bare number `42` | 0 | PASS |
| zero-byte `.html` | 0 | PASS |
| zero-byte `llms.txt` | 0 | PASS |
| invalid UTF-8 bytes (`\xff\xfe\x80`) in an `.html` | 1 | FAIL (decoded with `errors="replace"`, the `$1,550` beside them was still caught) |
| `<script>` that never closes | 0 | PASS |
| `<style>` that never closes | 0 | PASS |
| unbalanced / interleaved tags | 0 | PASS |
| `<time datetime="the-thirty-second-of-Octember">` | 0 | PASS |
| JSON-LD `dateModified: "soon"`, `datePublished: true` | 0 | PASS |
| a 10 MB inline `<script>` | 0 | PASS |
| a 10 MB single line of visible text | 0 | PASS |
| a nested subdirectory under `public/` | 1 | FAIL (the defect inside it was found) |
| an `.html` file whose bytes are a PNG header | 0 | PASS |
| `sitemap.xml` that is not XML at all | 0 | PASS |
| `<p class="cited-stat">` that never closes | 1 | FAIL |
| a JS string literal with an unterminated quote | 0 | PASS |
| a CSS rule with no closing brace | 0 | PASS |
| a symlink to a sibling file inside `public/` | 1 | FAIL (followed; the figure counted twice, `read set: 6 artifacts`) |
| a symlink to a file outside the repo (a DCI page) | 1 | FAIL (followed; a DCI page read as a GCI artifact) |

No hangs. The 10 MB cases completed. Config error handling is uniformly exit 2:
invalid JSON (`CONFIG ERROR: … is not valid JSON: Expecting property name…`), an
`extends` cycle (`CONFIG ERROR: config extends cycle at …`), a missing config
file (`CONFIG ERROR: config not found: …`), a `--repo` with no `public/`
(`CORPUS ERROR: no public/ directory in …`), and a `--repo` that is not a git
repo (exit 2, `HEAD unknown`).

---

## (i) Dead config and unimplemented-but-advertised behaviour, traced

### `SRC` — computed, advertised on every run, read by nothing

Traced end to end:

- `surfaces.src_string_runs()` is the `tokenize`-based walker of adjacent Python
  string tokens. Its docstring says it is *"Required because this portfolio's
  prose is split across Python implicit concatenation boundaries … so, verbatim
  from DCI's lane row, 'no single-string grep or regex can see the phrase'."*
- Its only caller is `read_generators`, which stores the result:
  `facts.src_text[name] = "\n".join(collapse(r[1]) for r in runs)`.
- `/usr/bin/grep -n 'src_text' claim_gate.py surfaces.py` returns **three
  lines, all in `surfaces.py`**: the declaration, the assignment, and a comment.
  **No rule reads `src_text`.**
- `/usr/bin/grep -n 'NORM_SRC' claim_gate.py surfaces.py` returns **two lines,
  both in `surfaces.py`**: a docstring and `NORM_SRC = "SRC"`. Nothing consumes
  it. `NORMALIZATIONS` is `(RAW, DEC, TXT)` and `level_counts` compares those
  three only.
- The gate nevertheless prints, every run:
  `normalization levels compared: RAW DEC TXT   (+ SRC over 38 generator modules)`
  and six of eleven rules advertise `SRC` in their `normalization:` line — R2
  (*"SRC over the generators"*), R3 (*"SRC for the generator reachability
  check"*), R4 (*"SRC for the generator half"*), R5 (*"SRC over the
  generators"*), R6 (*"SRC and RAW"*), R7 (*"SRC for the generator half"*).
- The only thing any rule reads off a generator is `rule_R6`'s
  `open(os.path.join(ctx.repo, chain["generator"]))` followed by a **line-based
  regex** — the exact method `src_string_runs` exists to replace — plus
  `ctx.gen.constants` and `ctx.gen.cited_sources`, which come from `ast`, not
  from SRC. (`ast` does fold implicit concatenation into one `Constant`, so
  `constants` genuinely sees concatenated prose; the SRC level is still dead.)

**Verdict: `SRC` is advertised in eight places and implemented in none of them.**

### Dead config with full provenance — a rule that silently does not exist

256 distinct key names appear across the four config files; 102 appear as a
string literal somewhere in `claim_gate.py` or `surfaces.py`. Most of the
remainder are legitimately data (town names, domain keys) or prose annotations
(`*_note`, `*_reason`, `*_README`). The behavioural keys with real provenance
that **no code path consults**:

| key | what it carries | consequence |
|---|---|---|
| `R2.locked_restriction_strings` (LGM) | four verbatim strings, *"applies only to residential electric customers of Longmont Power & Communications"*, with `locked_restriction_reach: "10 + 8 pages, measured in d6e8dab. 'The restriction is not the figure' — it survived the figure strip deliberately."* | **Ruling 7's LGM clause is not enforced.** Measured: `<p>Efficiency Works pays the insulation rebate.</p>` on Longmont's own `index.html`, with no LPC-electric restriction → `R2 RAW 0 ADJ 0 PASS exit 0`. Adding the locked restriction string changes nothing (also `RAW 0`). The same sentence on `insulation-lafayette.html` IS caught (`RAW 1 ADJ 1 FAIL`) — but only because Lafayette has no `electric_program`, not because any restriction was checked. |
| `R2.forbidden_program_names` (DCI) | `["Xcel IQ Program", "IQ Program", "Xcel IQ"]` with a four-commit provenance paragraph and a standing "do not reinstate without a first-party Xcel source" | A named, sourced, banned-string defect class that the gate cannot detect. |
| `R2.forbidden_elevations` (LGM) + `R2.elevation_anchor` (all three) | `["5,280","mile high","4,108","4,400","4,432","4,658","4,675"]` | Never read. |
| `R2.allowlist` (GCI) | `["DRCOG"]`, *"Director-granted. GCI is the only property with one."* | Never read (harmless — DRCOG is also in `non_territorial_programs`). |
| `R3.allowed_occurrences` (GCI) | `{"$70,000": 10, "$99,920": 10}` with *"MEASURED 2026-09-17: exactly 20 occurrences"* | Never read. **The figure allowlist is unbounded**: a 21st occurrence of `$70,000` passes. |
| `R3.bare_numeral_gate` (GCI) | a full `/usr/bin/grep -rnoE` command with the note *"Installed in f0203ad because the $-anchored gate structurally cannot catch a bare-digit cap"* | Recorded as prose, never executed. My R3-C4b/C17 misses are that command's job. |
| `R3.exclude_paths` | `["docs/citation-registry.json"]` | Never read (harmless — outside `public/`). |
| `R1.cited_stat_class` | `"cited-stat"` | Never read; `surfaces.py` hardcodes the regex `<p class="cited-stat">`. Renaming the class silently disables R1 half A **and** all of R11's attribution measurement. My R1-A2 miss is this key. |
| `R1.quote_close`, `R1.attribution_template`, `R1.require_explicit_quote_field` | `["&rdquo;","”","&quot;","\""]`, the template, `true` | None read. Only `quote_open` and a hardcoded `quote is True` are used. |
| `R8.footer_marker` | `"Last reviewed:"` | Never read. My R8-H1 miss is this key: a plain-text review date is invisible. |
| `R8.date_surfaces` | the five surface names | Never read; hardcoded in `rule_R8`. |
| `R8.reviewed_iso_constant`, `R8.static_page_constant`, `R8.static_page_value`, `R8.self_dated_sources`, `R8.own_effective_date_values`, `R8.pinned_pages.*.expected_sitemap`, `.expected_footer` | generator constant names and expected values | None read. `pinned_pages` is consulted only as `base in pinned`; the expected values are never compared. |
| `R10.offproperty_is_compliant` | `true` | Never read; hardcoded `ok = True`. |
| `R11.attributing_block_selector` | `"p.cited-stat"` | Never read; hardcoded `sel_open = '<p class="cited-stat">'`. |
| `R11.blocking`, `R11.report_registry_pages_drift` | `false`, `true` | Neither read; blocking is hardcoded in the `RULES` registry. |
| `R6.opt_in` | `["R6b"]` | Never read; `OPT_IN_RULES` is hardcoded. |
| `R7.current_replacements` | `{"24-02-205": "25-12-215", "No. 544": "No. 647", "nrel.gov": "nlr.gov"}` | Never read — the report never tells the reader what supersedes the thing it found. |
| `R7.deliberate_edition_divergence` | the GCI/LGM IRC-edition carve-out | Never read. |
| `R4.attributed_exception.requires_publisher_named`, `.requires_cited_source_key`, `.basis`, `.and_the_figures_are_still_banned` | the Efficiency Works carve-out contract | Not read as config; the conditions are hardcoded. Consequence: `exc.get("publisher")` is only set on LGM, so the `ATTRIBUTED-AND-SOURCED` class **cannot be assigned on DCI or GCI** at all. |
| `expected_html` | 75 / 48 / 38 | Required to be present, compared to nothing. See anomaly 5. |
| `svg_readable` | the per-property SVG list | Never read; artifact kind comes from the extension. |
| `R2.hedge_pairs` | `[]` on all three properties | Read, always empty, so R2's sub-test `h` (hedge-half-missing) can never fire anywhere. GCI's `hedge_pairs_note` states this is deliberate — a stated decision, not an oversight. |
| `R2.sibling_artifacts_forbidden` | the cross-property town lists | Not read by R2, and R2 prints a note saying so every run — a stated decision. DCI's own note records that `_artifact_grep.sh`, the gate that *is* supposed to do it, does not exist on DCI. |

### Dead code

- `rule_R8`'s `def f_known(h): return False`, wired to the `Filt` labelled
  `"own_effective_date_pages / exempt_pages (excluded before match)"`. Can only
  print `0 (removed 0)`. Analysed in (d) — it is the row that makes silent drop
  case 1 look accounted-for.
- `rule_R11`: `if c.get("forbid_subtraction") and len(both) and naive ==
  len(unattributed): pass` — a literal `pass`. The subtraction claim is printed
  as prose, not asserted.
- `rule_R11`: `res.r11_rows = rows`.
  `/usr/bin/grep -n 'r11_rows' claim_gate.py` returns one line — the assignment.
  No consumer.
- `adjudicate`'s `ArithmeticMismatch` — reachable only if a filter predicate is
  non-deterministic. Demonstrated unreachable in (d).
- `Artifact.is_embed`. `/usr/bin/grep -n 'is_embed' claim_gate.py surfaces.py`
  returns two lines, both the declaration and the assignment in `surfaces.py`.
  No rule reads it, and ten of eleven rules list `EMBED` in their `surfaces:`
  line. The embed frames *are* read — but as ordinary HTML, because they are in
  `public/`, not because `embed_artifacts` did anything. `embed_artifacts`'s only
  effect is one printed line.
- `S_CSS` and `S_SITEMAP`. `/usr/bin/grep -n 'S_SITEMAP\|S_CSS' claim_gate.py`
  returns **no matches**. Both surfaces are extracted and appear in no rule's
  key set, while R3's `surfaces:` line advertises `CSS` and `SITEMAP`.

### The sentence splitter

`_SENT = re.compile(r"(?<=[.!?…])\s+")`. Measured behaviour:

```
  INPUT : The heat pump must be installed and invoiced by Dec. 31, 2026.
    [0] The heat pump must be installed and invoiced by Dec.
    [1] 31, 2026.
  INPUT : Atmos territory is set out in Advice Letter No. 647 for Colorado.
    [0] Atmos territory is set out in Advice Letter No.
    [1] 647 for Colorado.
  INPUT : Building Science Corp. Inc. published the figure.
    [0] Building Science Corp.
    [1] Inc.
    [2] published the figure.
  INPUT : The U.S. Department of Energy recommends R-49.
    [0] The U.S.
    [1] Department of Energy recommends R-49.
  INPUT : Costs run approx. 1.50 per square foot at 3.5 inches.
    [0] Costs run approx.
    [1] 1.50 per square foot at 3.5 inches.
  INPUT : The rebate is 0.75 of the installed cost, capped at 1,550.
    [0] The rebate is 0.75 of the installed cost, capped at 1,550.
  INPUT : She said “the rebate requires 20% in CFM50.” Then she left.
    [0] She said “the rebate requires 20% in CFM50.” Then she left.
  INPUT : It was withdrawn… then reinstated in 2026.
    [0] It was withdrawn…
    [1] then reinstated in 2026.
  INPUT : Three measures qualify (see Sec. 4.2 of the sheet) within two years.
    [0] Three measures qualify (see Sec.
    [1] 4.2 of the sheet) within two years.
```

Survives: decimals (`0.75`, `1.50`, `3.5`, `1,550` — no space after the period).
Breaks at: `Dec.`, `No.`, `Corp.`, `Inc.`, `U.S.`, `approx.`, `Sec.`, and the
ellipsis `…`. **Over-joins at `.”`** — a sentence ending in a quotation mark is
welded to the next, because the character immediately before the whitespace is
`”`, not `.`. That is an under-reported second failure mode: a filter word in the
*following* sentence can clear a claim in the preceding one.

Exhaustive scan of every sentence-scoped config list, testing whether
`surfaces.sentences(pattern)` returns more than one piece:

```
=== CONFIG PATTERNS THAT THE SENTENCE SPLITTER MAKES UNFIRABLE
  common.json  R7.superseded_propositions[installed_and_invoiced_by_dec_31_2026] 'invoiced by Dec. 31, 2026'
                 splits into ['invoiced by Dec.', '31, 2026']
  common.json  R7.superseded_propositions[installed_and_invoiced_by_dec_31_2026] 'installed and invoiced by Dec. 31'
                 splits into ['installed and invoiced by Dec.', '31']
```

**Exactly two configured patterns are unfirable, and both belong to the one
claim whose own provenance note says the short form is what survived four
previous sweeps.** R9's `value_slots` and `extract` patterns and R11's
`tracked_terms` patterns were scanned too and are all single-sentence.
`R7.superseded_identifiers` contains `"Advice Letter No. 544"` and `"No. 544"`,
which are matched on RAW and TXT rather than per sentence, so those survive.

### Other advertised-but-false README claims

| README claim | status |
|---|---|
| *"Controls run against fixture files only, never the repo"* | **FALSE** — proved in (a), 14 FALSE ALARM |
| *"a control proves the RULE can detect its defect regardless of which property's territory, figures or label chains happen to be loaded"* | **FALSE** — proved in (a) |
| *"Control tallies are therefore identical on all three properties"* | **TRUE TODAY** — `diff` of the 34 canary rows, DCI vs LGM and DCI vs GCI, both identical. True by accident: all three currently satisfy the R6 preconditions. |
| *"The gate asserts `raw − removed == adjudicated` and exits 2 if that identity fails"* | **the guard is unreachable** — proved in (d) |
| *"A run whose filter silently dropped a real hit must not look identical to a clean run"* | **FALSE** — two counter-examples in (d) |
| *"`--peer <repo>` supply a second property for R9's cross-property half"* | **UNIMPLEMENTED** — anomaly 3 |
| *"It writes nothing except an explicit `--report` path"* | **TRUE for the script entry point**; an import writes a `.pyc` beside the implementation |
| *"`--brief` … so a brief run can never be mistaken for a full one"* | **TRUE** — 22 `ENUMERATION SUPPRESSED BY --brief` markers in one GCI `--brief` run |
| *"A rule with no positive-control fixture cannot register. The loader refuses it and exits 2. So does an empty `blind spot` field."* | **code confirms** `validate_registry()` checks both and `main` exits 2; all eleven rules have controls and non-empty blind spots, so the path was **NOT TESTED** by triggering it |
| *"KNOWN-OPEN hits are never filtered"* | **code confirms** — `_open(pred)` wraps every R5 filter and returns `False` for any hit whose note starts `KNOWN-OPEN`. **NOT TESTED** with a live KNOWN-OPEN hit; DCI's single `known_uncited` entry did not surface as one in the baseline run. |

---

## (j) The single most severe finding and the verdict

Stated first, at the top of this document. Repeated here so the lettered list is
complete: **R6 — the rule for the calculator-severity defect class — prints
`RAW 0 / ADJ 0 / PASS` byte-identically whether it is clean, blind, or looking
straight at the defect, including at the exact form "two different severity words
beside the same percentage"**; and the verdict is that the gate would have
caught four of the six named defects only partially, one not at all, and one not
as a claim at all, because in its load-bearing rules it is still a string list
with a claim-test label on it — and its control phase cannot tell the
difference.

---

## (k) Commit

This file, committed to `main` in canon. SHA recorded in the pass's final
report; `git status --porcelain` was checked immediately before staging and this
file was the only dirty path, staged by explicit path.

---

## (l) Decisions this brief did not pre-state

1. **Mirrored `ops/claim_gate/` into scratch and drove it through
   `CANON_ROOT=`.** The brief mandates "mutate the fixture to remove ONLY the
   defect" and forbids editing `fixtures/`. Those are only reconcilable by
   running a copy. I used the wrapper's own documented `CANON_ROOT` hook and
   established byte-parity of the mirror (`--canary` output identical except the
   stderr timing line) before trusting a single mutation result. Every mutation
   restored all fixtures from canon first.
2. **Built adversarial vectors in a purpose-made git repo** rather than in any
   property checkout, driven by `--config`/`--repo`. The scratch configs
   `extends` the real property configs and override only `min_artifacts` and
   `expected_html`, so every vector ran against real territory, real figure
   lists, real program lists and real propositions.
3. **Chose per-vector which property's config to run under**, because the
   configs are not interchangeable: GCI for R2/R3/R5/R7/R8 (only GCI has split
   territory), DCI for R4/R9/R10/R11 (only DCI configures `R4.programs` for
   Denver, `R9.tools`, `R10.page_titles`, `R11.tracked_terms`), LGM for the
   Efficiency Works restriction test.
4. **Created two further scratch configs purely to route around the R6-driven
   control abort** — `adv-dci2.json` (DCI with `R6.label_chains: []`) and
   `adv-r6c.json` (a chain whose `generator` points at a clean file) — because
   otherwise the R6, R9 and R10 rule blocks could not be exercised at all. The
   abort itself is reported as a finding rather than worked around silently.
5. **Split the R2a control repair into two stages** (defect only; defect plus
   qualifier) to separate sub-test `a` from sub-test `q`. Did the same for R9
   with three variants after my first R9 mutation proved to be mine, not the
   gate's.
6. **Tested determinism with `PYTHONHASHSEED`, `LC_ALL` and `TZ` variation**
   plus a source reading of every sort site, rather than physically re-creating
   the filesystem in a different order. The physical re-order is labelled
   NOT TESTED.
7. **Ran no worktrees at all**, so nothing needed pruning.
8. **Did not attempt R6b.** No Chrome binary was installed or invoked; the
   `--opt-in=R6b` behaviour is reported as observed (unconditional exit 2), not
   as an evaluation of a browser cross-product that does not exist.
9. **Read `--report` output rather than re-running for each analysis**, and
   verified the `--report` file matches stdout.
10. **Left canon's pre-existing one-commit-ahead state and its gitignored
    `__pycache__` exactly as found.** Both are reported, neither is touched.
11. **Reported the board count** because the project's own Rule 10i requires it:
    `docs/board/intake`, `ready`, `in-flight` and `blocked` contain **0** `.md`
    files each; `docs/board/done` contains **16**. Open card count is **0**
    before and **0** after this pass — the brief forbade creating a card, so
    every finding here lives in this file and in the pass's final report.

### Tests in my plan that did NOT get run — labelled, not inferred

- A physically re-ordered filesystem (creation-order variation). **NOT TESTED.**
- Triggering `validate_registry()`'s two refusal paths (a rule with no control,
  an empty `blind_spot`). **NOT TESTED** — both would require editing
  `claim_gate.py`'s `RULES` registry, which is forbidden.
- A live KNOWN-OPEN R5 hit, to confirm `_open()` protects it in practice.
  **NOT TESTED.**
- R11 evasion vectors. **NOT TESTED** — the rule emits unconditionally and has
  nothing to evade.
- The "invented rebate program with four invented eligibility pathways" defect
  class as a claim. **NOT TESTED as a claim**, because no rule asserts programme
  existence; I state only what the code shows, that R7 can match a proposition
  only after a human has written it into the config.
- R2's `forbid_electric_utility_naming` sub-test (`e`) in isolation. **NOT
  TESTED** — GCI's baseline `R2 ADJ 98` includes it, but I constructed no
  targeted vector for it.
- R6b's browser cross-product. **NOT TESTED** (no browser).
