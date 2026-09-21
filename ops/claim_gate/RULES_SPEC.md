# CLAIM GATE — rule specification

**Drafted 2026-09-17, lane `claim-gate-2026-09-17-canon`, row R1. SPECIFICATION
ONLY — no implementation, no page edit, no deploy.** Every rule below is derived
from a defect this portfolio shipped live between 2026-09-01 and 2026-09-11, not
from general principle. The commit that shipped each defect is cited beside its
positive control.

## Why this exists

Eight defect classes reached production in two weeks. Every one was caught by a
human-written one-off sweep, and every sweep found what the previous sweep's
instrument could not see, because **the instruments matched SURFACE FORM while
the defects are defined by MEANING.** The standing record of that is
[`METHODS/CANDIDATE-do-not-scope-with-grep-over-html.md`](../../METHODS/CANDIDATE-do-not-scope-with-grep-over-html.md):
grep over rendered HTML **confirms; it does not find**, and a gate is only as
good as its anchor. That file's own open question to the Director — whether to
pair the principle with a `text-of()` helper so the correct method is the
cheapest one — **is answered by this gate: the gate ships the helper.**

This gate is the re-runnable **acceptance predicate over the whole deployed
artifact set**. It is not an inventory. Per that same file: *a list enumerates
what was found; a gate defines what done means.*

## What this gate is NOT

- It is **not** a build gate. This portfolio's build gates are each property's
  `regen_all.sh`, `_postbuild_check.py`, `_check_links.py`,
  `_intra_similarity_check.py`, `_validators.py`, `_artifact_grep.sh` (LGM and
  GCI only — **it does not exist on DCI**, a null result recorded in DCI's lane
  rows `xcel-25-12-215-figures-dci` and `dci-d3-tier-label-fix`),
  `_out_guard.py` (**LGM only**), `_similarity_check.py` (**GCI only**) and
  `_svc_pending_import_check.py` (**GCI only**). Those check STRUCTURE. This
  gate checks CLAIMS.
- It is **not** a truth oracle. It cannot know what a PDF says. Where a rule
  needs first-party text, it asserts the presence and shape of a *provenance
  record*, and says so in its own output rather than implying it verified the
  fact.
- It **never edits** anything. Report-only, like
  `scripts/staleness_watcher.py`.

---

## 1. IMPLEMENTATION AND CONFIG SPLIT

One implementation in canon; three configs in canon; one thin wrapper per
property repo.

```
calibrated-design-canon/
  ops/claim_gate/
    RULES_SPEC.md              <- this file
    claim_gate.py              <- the ONE implementation (python3, stdlib only)
    surfaces.py                <- the text_of() / surface extractor
    config/dci.json
    config/lgm.json
    config/gci.json
    fixtures/R1_fabricated_quotation.html
    fixtures/R2a_wrong_utility_visible.html
    fixtures/R2b_wrong_utility_no_string.html
    fixtures/R2c_wrong_utility_anchor_only.html
    fixtures/R2b_og-image.svg
    fixtures/R3a_js_comment_cap.html
    fixtures/R3b_jsonld_amount.html
    fixtures/R3c_rank_claim_no_numeral.html
    fixtures/R4a_stacking_denial_jsonld.html
    fixtures/R4b_stacking_assertion_prose.html
    fixtures/R5_uncited_statistic.html
    fixtures/R6_label_figure_contradiction.js
    fixtures/R7_superseded_source.html
    fixtures/R7d_superseded_entry_path.html
    fixtures/R8a_stale_review_date.html   + R8a.gitfacts.json
    fixtures/R8b_review_precedes_creation.html + R8b.gitfacts.json
    fixtures/R8c_future_review_date.html
    fixtures/R9_cross_surface_contradiction/   (llms.txt, air-sealing.html)
    fixtures/R10_dangling_promise/             (3 html)
    fixtures/R11_attribution_debt.html
    fixtures/negative/NEG01..NEG18   (NEG15, NEG16 and NEG17 are
                                      DIRECTORIES; NEG11 carries
                                      NEG11.gitfacts.json)
<property-repo>/
  ops/claim_gate.sh            <- thin wrapper, R2/R4's rows own these
```

**Why python3 stdlib only.** Every existing gate in this portfolio is either
`bash` + `/usr/bin/grep` or python3 with no third-party imports
(`_postbuild_check.py`, `scripts/staleness_watcher.py`). Canon has **no
`package.json`** and no build step (project `CLAUDE.md`). Introducing a
dependency would add a per-property install to a gate whose whole value is that
it runs every pass. `html.parser`, `html.unescape`, `json`, `re`, `tokenize`,
`ast`, `pathlib`, `urllib.parse` cover every rule the gate actually implements.
(The one rule they would not cover, opt-in R6b, is **unimplemented** — §6.)

**The wrapper.** `ops/claim_gate.sh` in each property repo is the ONLY
property-side file, and it does exactly this:

```bash
#!/usr/bin/env bash
# Thin wrapper. The implementation and every rule live in canon at
# ops/claim_gate/claim_gate.py; the per-property values live in
# ops/claim_gate/config/<key>.json. Nothing property-specific belongs HERE --
# if you are about to add a pattern to this file, add it to the config instead.
set -uo pipefail
CANON="${CANON_ROOT:-$HOME/code/calibrated-design-canon}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$CANON/ops/claim_gate/claim_gate.py" \
  --config "$CANON/ops/claim_gate/config/<key>.json" \
  --repo   "$REPO" "$@"
```

`<key>` is `dci`, `lgm` or `gci`. The wrapper resolves canon by env var with a
home-relative default because **hardcoded absolute paths are a recorded defect
class in this portfolio** (`hardcoded-path-defect-dci.md`,
`-lgm.md`, `-gci.md`, `hardcoded-path-defect-portfolio.md`, and canon's
`genesis-cwd-relative-paths.md`, all in the respective `docs/board/done/`).

**The config holds values. The implementation holds rules.** If a rule cannot be
expressed without a property name inside `claim_gate.py`, the rule is wrong.
This is the direct lesson of `_artifact_grep.sh`: GCI's copy and LGM's copy have
diverged into two files that must be maintained twice, and LGM's still names
*"this property's Director-locked five: Longmont, Erie, Lafayette, Louisville,
Niwot"* when LGM has had **four** area towns since commit `3ca991f` ("Close Erie
card as superseded") and `Erie` now appears **0 times** in `public/`.

---

## 2. CORPUS ENUMERATION CONTRACT

**Enumerate from `public/`. NEVER from `sitemap.xml`.** This is not a
preference. DCI's `xcel-25-12-215-figures-dci` lane row records it as the tenth
round's finding, verbatim: *"THE CORPUS ITSELF WAS WRONG FOR NINE ROUNDS …
`sitemap.xml` is a list of what you want CRAWLED; it is not a list of what you
SHIP."* Two separate live defects — the `llms.txt` `"Xcel rebate-stack
eligibility"` assertion (DCI `fb08735`) and the `"the the income-qualified
programs for income-qualified households"` clause (DCI `84a9c10`) — survived
**eleven rounds and every automated gate** because `llms.txt` is deployed, live
and absent from the sitemap. LGM hit the identical thing the same day
(`e329db7`). GCI's `gci-xcel-gas-towns-correct` row states the corrected
practice in its own verification: *"all 49 artifacts in `public/` (enumerated
from `public/`, not from `sitemap.xml` — `llms.txt` is live and unindexed)."*

And the corollary, from DCI `fb08735`'s lane row: **a corpus widened for
VERIFICATION is not widened for AUDIT.** Round 10 fetched all 83 artifacts and
byte-compared them, which proves they shipped intact and says nothing about what
they claim.

### The enumeration rule

```
CORPUS      = every file under <repo>/public/, recursively, following the
              repo's own git index (`git ls-files public/`) UNION the working
              tree (`find public/ -type f`). Report the two counts separately
              and FAIL (exit 2) if they differ, naming the difference.
READ_SET    = CORPUS minus BINARY_EXCLUSIONS minus KEY_FILE_EXCLUSIONS
```

Both halves are required. `git ls-files` alone misses an untracked generated
file; `find` alone misses a tracked file a regen deleted. A divergence is itself
a finding: DCI's own D3 row had to reconcile *"regen writes 78 … `git ls-files
public/` is 85 (78 generated + 7 static that are never rewritten)"* and the
brief it inherited said 79, which *"is not reproducible."*

### Per-property globs and actual filenames

Measured 2026-09-17 with `ls public/` and `/usr/bin/grep`, at DCI `f9e7551`,
LGM `084a423`, GCI `d9ebab7`.

**DCI — `denvercoloradoinsulation.com` — 85 files in `public/`**

| Glob | Count | Read? | Notes |
|---|---|---|---|
| `public/*.html` | 75 | YES — all surfaces | includes `404.html`, both embed artifacts |
| `public/llms.txt` | 1 | YES — plain text | live, deployed, **NOT in sitemap** |
| `public/robots.txt` | 1 | YES — plain text | carries the AI-crawler allow-list and prose comments |
| `public/sitemap.xml` | 1 | YES — `<loc>`/`<lastmod>` only | used by R8 as a SURFACE, never as the corpus |
| `public/1b79c33b73e0dea0470080c5c9854d20.txt` | 1 | NO | 32-byte IndexNow key file; content == filename stem; **enumerated and deliberately excluded, see §7** |
| `public/favicon.ico` | 1 | NO | binary |
| `public/favicon.png`, `public/og-image.png`, `public/google-preferred-source-badge.png` | 3 | NO | raster, §7 |
| `public/favicon.svg`, `public/logo.svg` | 2 | **YES — SVG text nodes** | SVG is XML; its `<text>` nodes are readable claims |

**THE EMBED FRAME, named exactly, because a prior sweep missed it:** DCI is the
**only** property with one. Two artifacts, both generated by
`_generate_calculator_pages.py`, both new as of 2026-09-10 (build `576a5ce`,
release `539670e`):

- **`public/r-value-needed-calculator-embed.html`** — the frame itself. Served
  to third-party domains inside an `<iframe>`. `<meta name="robots"
  content="noindex, follow">`, `<link rel="canonical">` pointing at the full
  page, **no `og:*`, no `twitter:*`, no JSON-LD**, and all of its CSS and JS
  inline. It is **permanently outside `ops/functional_proof.sh` CHECK 3's
  perimeter** — that gate discovers tools by walking live-sitemap `LOCS`, and
  the frame is deliberately absent from the sitemap. Its own lane row records
  that it *"DOES satisfy `is_tool_page` structurally and is skipped only for
  sitemap non-membership."* This gate reads it because this gate enumerates
  `public/`.
- **`public/r-value-needed-calculator-embed-code.html`** — the copy-paste
  snippet page. In the sitemap. Carries the `<iframe>` snippet as escaped text,
  the attribution `<a>`, and prose about frame height.

**LGM — `longmontcoloradoinsulation.com` — 59 files in `public/`**

| Glob | Count | Read? | Notes |
|---|---|---|---|
| `public/*.html` | 48 | YES | |
| `public/llms.txt` | 1 | YES | |
| `public/robots.txt` | 1 | YES | |
| `public/sitemap.xml` | 1 | YES (R8 surface) | |
| `public/ee368c8751be4043b5e29d015679f93b.txt` | 1 | NO | key file, §7 |
| `public/favicon.ico` | 1 | NO | |
| `public/favicon.png`, `og-image.png`, `google-preferred-source-badge.png` | 3 | NO | raster, §7 |
| `public/favicon.svg`, `public/logo.svg`, `public/og-image.svg` | 3 | **YES — SVG text nodes** | `og-image.svg` is the one that matters (see R2b) |
| **embed frame** | **0** | — | **NULL RESULT: LGM has no embed artifact.** Verified by `ls public/ \| /usr/bin/grep -i 'embed\|frame\|iframe'` → empty. |

**GCI — `greeleycoloradoinsulation.com` — 49 files in `public/`**

| Glob | Count | Read? | Notes |
|---|---|---|---|
| `public/*.html` | 38 | YES | |
| `public/llms.txt` | 1 | YES | |
| `public/robots.txt` | 1 | YES | |
| `public/sitemap.xml` | 1 | YES (R8 surface) | |
| `public/d38d3ab74418efeba995b5fab6345f07.txt` | 1 | NO | key file, §7 |
| `public/favicon.ico` | 1 | NO | |
| `public/favicon.png`, `og-image.png`, `google-preferred-source-badge.png` | 3 | NO | raster, §7 |
| `public/favicon.svg`, `public/logo.svg`, `public/og-image.svg` | 3 | **YES — SVG text nodes** | |
| **embed frame** | **0** | — | **NULL RESULT: GCI has no embed artifact.** |

### The transitive claim set

Enumerating files is not enough, and this is the part a file-glob sweep cannot
reach. From the canon addendum, the instance that *"proves the principle rather
than merely illustrating it"*: LGM's `spray-foam-vs-blown-in-comparator` page
carried `$1.16` and `$0.77` **even though neither string appears anywhere in
that page's generator.** It inherited them by naming a shared `CITED_SOURCES`
key in `cite_keys=[...]`. *"No string search for the figure could ever have
found that page, because the figure is not in it. It is in something it points
at."*

Therefore, for every HTML artifact, the gate assembles a **CLAIM SET**:

1. The artifact's own extracted surfaces (§3).
2. Every `CITED_SOURCES[key]`'s `source`, `stat`, `url` and `determiner` for
   every key whose rendered `class="cited-stat"` block appears on the page —
   resolved from the generator, not re-parsed from the HTML, so a key that
   renders to nothing visible is still in the set.
3. The **text content of every referenced generated asset** — concretely, the
   `<text>` nodes of any `og:image` / `twitter:image` / `<img src>` target that
   is an SVG in `public/`, plus, when the referenced asset is a PNG rasterised
   from an SVG or `.mvg` under `_brand_build/`, that source's text. This is not
   hypothetical: GCI's `og-image` said **"Atmos rebates explained"** and was
   referenced by `og:image` and `twitter:image` on **every page including the
   three Xcel-gas towns** (fixed in `e6cb44e` via `_generate_brand_assets.py`'s
   `OG_FOOTER`). The HTML on those pages contained the string "Atmos" zero
   times.
4. The text of every shared constant rendered on the page that the config names
   as territorially scoped — on GCI, `REBATE_ACKNOWLEDGMENT` and
   `THANK_YOU_BODY` (35 pages each).

**A rule that asserts a proposition runs against the CLAIM SET. A rule that
asserts a string runs against the READ_SET.** Each rule below says which.

---

## 3. SURFACES AND NORMALIZATION

### The surfaces, named

Every rule below names its surfaces from exactly this list. These are the
surfaces defects actually shipped in.

| Key | What | Real defect that shipped here |
|---|---|---|
| `VIS` | visible body text, tags stripped | most |
| `TITLE` | `<title>` | DCI: `"WHE Bonus Prerequisite"` (`eb5c939`) |
| `META` | `<meta name="description">` | DCI: retired rule live in `description` + `og:description` + `twitter:description` on an already-edited page (`31484f1`) |
| `OG` | every `<meta property="og:*">` `content` | same |
| `TW` | every `<meta name="twitter:*">` `content` | same |
| `LD` | every string leaf of every `<script type="application/ld+json">`, **including `acceptedAnswer.text`, `knowsAbout[]`, `areaServed[]`, `description`, `headline`, `dateModified`** | GCI: FAQPage stacking denial (`f0203ad`); GCI: `knowsAbout`/`areaServed` Atmos attribution (`e6cb44e`); DCI: payout-timing claim in `acceptedAnswer` (`f83d421`) |
| `JS` | every inline `<script>` body **including `//` and `/* */` comments** | GCI: `// CAP/RATE (1550 / 0.75)` shipped live in view-source (`f0203ad`) |
| `CSS` | every inline `<style>` body | GCI: `.thank-you { display: none; }` made a correction invisible until form submission (`bf240f8`) |
| `LOWVIS` | `<td>`, `<th>`, `<li>`, `<summary>`, `<option>`, `<small>`, `<caption>`, `<figcaption>`, `<button>`, `<label>`, and anchor label text | DCI: *"the front door of the WHE program"* as an anchor label, and the `"WHE Bonus Stacking"` nav/tile label (`f83d421`, `31484f1`) — *"three of the last five defects lived in exactly those"* |
| `ATTR` | `alt`, `title`, `aria-label`, `href`, `content`, `datetime` | R2c: a rebate URL naming the utility where the anchor text does not |
| `LLMS` | `public/llms.txt`, whole file | DCI `fb08735`, LGM `e329db7` |
| `ROBOTS` | `public/robots.txt`, whole file | never yet, but it carries editorial prose comments |
| `SITEMAP` | `public/sitemap.xml` `<loc>` + `<lastmod>` pairs | R8 |
| `EMBED` | both DCI embed artifacts, all of the above surfaces within them | DCI `92f3887` (D8: the frame shipped `"15% reduction"` and `"Whole Home Efficiency Bonus"` as 1,131 dead bytes to third-party domains) |
| `SVGTEXT` | `<text>` nodes of any SVG in the CLAIM SET | GCI og-image `"Atmos rebates explained"` (`e6cb44e`) |

### The four normalizations, named

The gate exposes exactly four, and every rule declares which it uses. This is
`surfaces.py`'s whole public surface.

- **`RAW`** — the bytes as served. The only level at which "what a view-source
  reader sees" is true. Required by R3 (the JS comment shipped in the bytes).
- **`DEC`** — RAW with HTML entities decoded (`html.unescape`) and Unicode
  normalised to NFC. Required because `&amp;`, `&mdash;`, `&ldquo;`, `&hellip;`,
  `&rdquo;` *"are not what you typed"* (CANDIDATE file, §1.3), and because a
  raw substring count inflates by 4 per ampersand — LGM's `about.html` measures
  **158 chars RAW but 154 UNESCAPED**, and 154 is what a SERP shows (LGM
  `16afe94`). Every length or char-count assertion runs on `DEC`.
- **`TXT`** — `DEC` with `<script>`/`<style>` bodies removed, all remaining tags
  stripped, and **all whitespace runs collapsed to one space**, so a phrase that
  a line break runs through matches. Three separate recorded false zeroes force
  this:
  - DCI `3a6b76b`: `/usr/bin/grep -oF` returned **0** for a shipped sentence
    because *"the string straddles a source line break (`…something like
    <code>680</code> instead: the` ⏎ `result will then fit…`)"*. The row's own
    conclusion: *"a zero from grep is a statement about grep before it is a
    statement about the artifact."*
  - GCI `12dfcbf`: `"Weld County rows are"` measured **0** in three documents
    and the wrap-insensitive check `tr '\n' ' ' | tr -s ' ' | grep -c` returned
    **1 in all of them.** A coordinator drew a scope conclusion from the false
    zero.
  - GCI `gci-xcel-gas-state-docs`: `"Advice Letter No. 647"` returns a false
    `0` on two of three documents; only `No. 647` matches, because the phrase
    wraps.
  - The CANDIDATE file's own second instance: *"Beyond that we collect only what
    the quote form asks for"* reported absent on all three properties, present
    on two, **wrapped across a line break**.
- **`SRC`** — generator-source normalisation, for the rules that read `*.py`.
  Walks maximal runs of adjacent STRING tokens with `tokenize`, decodes and
  joins each run into its real text. Required because DCI's prose is split
  across Python implicit-concatenation boundaries — `REBATE_ACKNOWLEDGMENT`
  reads `"...the primary rebate " "stack for Denver-area..."` — so, verbatim
  from DCI's lane row, **"no single-string grep or regex can see the phrase"**.
  The same row records that a raw-text regex spanning the boundary *"eats the
  quotes and breaks the file (it did, twice; both attempts were reverted)"* —
  hence `tokenize`, never regex. DCI `fb08735` records the mirror: a split
  literal *"matched the `.pyc` and not the `.py`."*

**A rule that reports a zero on only one normalization level is a defective
rule.** Every string-list rule runs on `RAW`, `DEC` and `TXT` and reports all
three counts. A level-disagreement is itself printed as a `TRAP` line (see §4),
because the disagreement is the interesting result.

### Two measurement rules that bind every rule

- **Occurrences, never lines.** Use `re.finditer` / `grep -o … | wc -l`.
  `grep -c` counts LINES. Measured live in this portfolio during the very audit
  that recorded it: `Xcel` on GCI's payback page, `grep -c` says **10**, true
  occurrence count **11** (GCI `bf240f8`).
- **Word boundaries, and a known-present control.** GCI `12dfcbf`:
  `/usr/bin/grep -ci 'ault'` gives **8** where the locality `Ault` appears
  **once** (`default`, `fault`); `-cw` with matching case gives `1`. DCI
  `84a9c10`: a bare `the the` substring also matches `the thermal` /
  `the thermostat` / `the thermometer` on 9 pages, all false; the real count was
  exactly **1**. And the one control that kills the whole family, recorded in
  GCI's ground-truth and in canon's `PROPERTY_GENESIS.md`: **search for a term
  you KNOW is present before trusting a term you believe is absent.**

---

## 4. OUTPUT CONTRACT

**A bare zero is FORBIDDEN.** The standing rule, from canon `b152b08`
(`METHODS/CANDIDATE-do-not-scope-with-grep-over-html.md` §"REPORT THE RAW MATCH
COUNT NEXT TO THE ADJUDICATED ONE"): *"any sweep reported as zero states its raw
match count, its filter, and what the filter removed. The null half of a sweep
is only auditable if the cleared items are enumerated."* The instance that
produced the rule: three JS-comment scans reported as *"0 rebate numerals"* —
correct — where the instrument **fired 153 times** (DCI 150, LGM 2, GCI 1) and
every hit was adjudicated away. *"A run whose filter silently dropped a real hit
looks identical, on the page, to a clean run."*

The precedent shape is GCI `a91dfd4`, which already reports this way:

```
  $-anchored figures     RAW=0   ADJUDICATED=0
  bare rebate numerals   RAW=0   ADJUDICATED=0
  cap/caps in output     RAW=37  ADJUDICATED(rank claims)=0
  rank/superlative words RAW=30  NEAR-MONEY=3  ADJUDICATED(defects)=0
```

### The exact output shape

Fixed-width, one block per rule, in rule order, on stdout. Column layout
inherited from `_artifact_grep.sh`'s `printf '  %-6s %-46s %s\n'`.

```
CLAIM GATE — <property key> — <repo abs path> — HEAD <sha> — <ISO date>
corpus: git ls-files public/ = <N>   find public/ -type f = <N>   AGREE
read set: <N> artifacts (<N> html, <N> txt, <N> xml, <N> svg)  |  excluded: <N> (<reason:count>, ...)
claim set: <N> propositions resolved from <N> cited-stat blocks, <N> shared constants, <N> referenced assets
normalization levels compared: RAW DEC TXT   (+ SRC over <N> generator modules)

━━━ CONTROLS (run BEFORE any rule; see §5) ━━━
  canary+ R1                 fixtures/R1_fabricated_quotation.html      DETECTED
  canary+ R2a                fixtures/R2a_wrong_utility_visible.html    DETECTED
  ...
  canary- NEG07              fixtures/negative/NEG07.html               clean
  ...
  CONTROLS: 22 positive DETECTED, 0 MISSED · 14 negative clean, 0 FALSE ALARM

━━━ R1  FABRICATED QUOTATION ━━━
  kind: CLAIM TEST (+ string list for the hand-written-prose half, declared)
  surfaces: VIS TITLE META OG TW LD LOWVIS EMBED LLMS   normalization: DEC TXT
  RAW              attributed quotations found                    76
  FILTER           registry-backed with explicit quote=true       0    (removed 0)
  FILTER           registry-backed by DEFAULT quote (field absent) 76   (removed 0)
  FILTER           config quotation_allowlist                      0    (removed 0)
  ADJUDICATED      quotations with no explicit provenance record  76
  LEVEL-DISAGREE   RAW=76 DEC=76 TXT=76                           AGREE
  VERDICT          FAIL — 76 attributed quotations, 0 carry an explicit quote=true
  blind spot: this rule cannot read the cited PDF. It asserts the PRESENCE
              and SHAPE of a provenance record, not the accuracy of the quote.
  --- 76 hits, enumerated ---
  air-sealing.html:VIS  ENERGYSTAR_SEAL_INSULATE_15PCT  "Sealing and insulating ..."
  ...
  --- 0 items the filters removed, enumerated ---
  (none)
```

Rules for this block, all mandatory:

1. **`RAW` is the instrument's unfiltered match count.** It is printed even when
   it equals ADJUDICATED, and even when both are zero.
2. **Every `FILTER` line names the filter, its count, and `(removed N)`.** The
   sum of `removed` plus `ADJUDICATED` equals `RAW`. The gate asserts that
   arithmetic and exits 2 if it does not hold — *"subtraction is not
   measurement"* (DCI `1794f98`: `26 = 36 − 10` was wrong because **8 pages did
   both**).
3. **Every removed item is enumerated**, not counted. The null half of a sweep
   is only auditable if the cleared items are listed. Suppressible only by
   `--brief`, which prints `ENUMERATION SUPPRESSED BY --brief` in place of each
   list so a brief run can never be mistaken for a full one.
4. **`LEVEL-DISAGREE`** prints the per-level counts and either `AGREE` or
   `DISAGREE`. A `DISAGREE` is a `TRAP` finding in its own right and is printed
   with the matching text at each level, because that is the line-wrap /
   entity-decode class catching itself.
5. **`blind spot:`** is mandatory on every rule and is a literal field, not
   prose. *"Gate returns zero"* is not a finding; *"gate returns zero, and the
   gate is anchored on `$`, so it cannot see a figure written as bare digits"*
   is. A rule whose `blind spot` field is empty fails validation at load
   (exit 2).
6. **`VERDICT`** is `PASS`, `FAIL`, or `REPORT` (for report-only rules), then a
   one-line reason carrying the number.
7. **A `kind:` line on every rule** printing `CLAIM TEST`, `STRING LIST`, or
   `CLAIM TEST (+ string list for <half>, declared)`. The gate prints this
   itself. **A string list must not masquerade as a claim test**, and the only
   way to guarantee that is for the gate to say which it is, every run, in its
   own output.

### Footer

```
━━━ SUMMARY ━━━
  R1  FABRICATED QUOTATION           RAW 76    ADJ 76    FAIL
  R2  WRONG-UTILITY CLAIM            RAW 212   ADJ 0     PASS
  ...
  R11 ATTRIBUTION DEBT               RAW 232   ADJ 232   REPORT (non-blocking)
  OPT-IN NOT RUN: R6b (browser cross-product, UNIMPLEMENTED). `--opt-in=R6b` DISCLOSES this gap; it does not close it, because no R6b implementation exists in this gate (measured 2026-09-21).
  blocking failures: 3 (R1, R5, R8)
  report-only findings: 1 (R11)
  opt-in rules not run: 1 (R6b -- not requested; also NOT IMPLEMENTED)
CLAIM GATE: FAIL
```

### Exit codes

| Code | Meaning |
|---|---|
| 0 | every blocking rule PASS, every control fired, corpus counts agree |
| 1 | at least one blocking rule FAIL |
| 2 | **control failure, config error, corpus divergence, or filter arithmetic mismatch** — the gate could not be trusted to have run |

Exit 2 is distinct from exit 1 on purpose, and matches LGM's `_out_guard.py` and
`_artifact_grep.sh`, which both reserve 2 for "the instrument itself is not in a
state to judge". A `REPORT` finding never changes the exit code.

### The zero-artifact trap

`_artifact_grep.sh` already guards this and its comment states the reason
exactly: *"an empty directory passes every check trivially. That is correct
behaviour for a gate but it is NOT evidence the gate works."* This gate inherits
the guard and hardens it: if the READ_SET is smaller than the config's
`min_artifacts` (DCI 85, LGM 59, GCI 49, each minus a tolerance of 0), the gate
exits **2**, not 0. A clean run on a truncated corpus must never look like a
clean run.

---

## 5. CONTROL-FIRST CONTRACT

**Every positive control runs BEFORE any rule touches the real corpus, and the
gate fails loudly — exit 2 — if any control does not fire.**

The justification is in this portfolio's own record twice over. `_postbuild_check.py`'s
own comment: *"B10: a validator needs a demonstration that it FAILS."* And the
harder one, DCI's `xcel-25-12-215-figures-dci` round-5 finding, verbatim:
`quote=False` *"was added to five entries and read by NOTHING; the quotes were
emitted unconditionally, so the correction shipped invisible."* A rule that
cannot be shown to fire is indistinguishable from a rule that is not wired in.

Mechanics, following `_postbuild_check.py`'s `run_canary()` line format exactly:

- Positives print `canary+ <RULE-ID>  <fixture path>  DETECTED` or
  `*** MISSED ***`.
- Negatives print `canary- <NEG-ID>  <fixture path>  clean` or
  `*** FALSE ALARM *** <what matched>`.
- Controls run against **fixture files only**, never the repo, and the gate
  asserts `public/` mtimes are unchanged across the control phase.
- `--canary` runs only the control phase and exits with its result, so the
  controls are independently checkable in CI or by hand — the same affordance
  all three `_postbuild_check.py` copies already offer.
- **Controls are not optional and have no flag to skip them.** Nothing removes
  any. This line used to add *"`--opt-in=R6b` adds R6b's controls"*; **corrected
  2026-09-21 — R6b has no controls, because R6b has no implementation** (§6).
  `--opt-in=R6b` adds one disclosure line to the control phase and nothing else.
- **A rule with no positive-control fixture cannot be registered.** The loader
  refuses it and exits 2. This is the structural version of the same lesson.

Every fixture's literal content is in §9. Every negative control is in §10.

---

## 6. SPEED, AND THE ONE OPT-IN RULE

Measured shape of the work: 172 HTML artifacts portfolio-wide, 1,058 JSON-LD
blocks, 1,235 inline `<script>` elements, 406 `cited-stat` blocks. All of §3's
extraction is one pass of `html.parser` plus `json.loads` per LD block. R1, R2,
R3, R4, R5, R7, R8, R9, R10 and R11 are all linear in that and belong in every
pass.

### R6b IS UNIMPLEMENTED — CORRECTION OF 2026-09-21

**R6b does not exist in `claim_gate.py`. It is not a rule that cannot run; it is
a rule that was never written.** This section previously described it as a real
opt-in rule blocked by a missing Chrome binary. That was false in both halves,
and the false version is quoted and refuted below rather than deleted.

**WHAT THIS SECTION USED TO SAY**, verbatim, through commit `20b9455`:

> **R6b — the browser cross-product — is OPT-IN, and it is the only one.** Named,
> not silently dropped. R6a (the static form) is blocking and runs every pass.
>
> R6b's cost is measured, not estimated. DCI's `dci-d3-tier-label-fix` row drove
> **140 input combinations on BOTH surfaces** through *"real headless Chrome
> 148.0.7778.97 over raw CDP"*, three times (pre-change tree, staging, live), to
> establish 4,465 ordinal pairs and a 45/54/31/10 histogram. It requires a Chrome
> binary this gate cannot assume — DCI's `chrome-path-unlabeled-alert-tradeoff.md`
> and `chrome-path-ruling-dci` lane exist precisely because the Chrome path is not
> portable here, and `ops/browser_canary.js` *"cannot run from this checkout
> (`require.resolve` MODULE_NOT_FOUND for `puppeteer-core`; no `node_modules/`,
> they live on the VPS)."*
>
> So: `--opt-in=R6b`. When not run, the summary prints
> `OPT-IN NOT RUN: R6b (browser cross-product). Run with --opt-in=R6b.` — an
> explicit line, never an omission. R6a's own output carries
> `blind spot: R6a reads the branch quantity statically and cannot enumerate the
> rendered cross-product; R6b does that and is opt-in.`

**WHY THAT IS FALSE.** Measured 2026-09-21 against `claim_gate.py` at `20b9455`,
denominator 7737 lines:

- `grep -in 'chrome\|chromium'` returns **exactly 2 hits**, and both are inside
  the gate's own "UNAVAILABLE" message strings. There is no third.
- `grep -nE 'playwright|puppeteer|selenium|webdriver|--headless|CDP|devtools'`
  returns **0 hits**. That zero is tested, not assumed: adding `|opt_in` to the
  same alternation, same tool, same file, same run, returns hits at lines 233,
  243, 6862 and beyond — so the pattern and the file are both live.
- There is **no R6b rule function**, **no G3 driver**, and **no
  `Control("R6b-G3", …)` in `RULES`**. `validate_registry()` never sees R6b
  because R6b is not a `Rule`.
- **Chrome IS installed on this machine.** `/Applications/Google
  Chrome.app/Contents/MacOS/Google Chrome --version` reports **Google Chrome
  153.0.8010.50**. It is not on `PATH` (`which google-chrome chromium chrome`
  finds nothing), which is likely how the false reason survived — but the gate
  never probed either location, because there is no probe.

The DCI measurements quoted in the old text are real: that row did drive 140
combinations over CDP. What is false is the inference that those measurements
describe **this gate**. They describe a one-off lane harness, not a rule wired
into `claim_gate.py`.

**WHAT THE GATE SAYS NOW.** The disclosure lines were rewritten to say
*unimplemented*, not *unavailable*, and `OPT_IN_RULES["R6b"]` now reads
`"browser cross-product, UNIMPLEMENTED"` so every line that interpolates it is
honest:

```
  OPT-IN NOT RUN: R6b (browser cross-product, UNIMPLEMENTED). `--opt-in=R6b` DISCLOSES this gap; it does not close it, because no R6b implementation exists in this gate (measured 2026-09-21).
  opt-in rules not run: 1 (R6b -- not requested; also NOT IMPLEMENTED)
```

and, with `--opt-in=R6b`:

```
  canary= R6b-G3             (opt-in, browser cross-product)              NOT IMPLEMENTED. This gate contains no browser driver, no R6b rule function and no R6b control -- measured 2026-09-21: 0 hits across claim_gate.py for playwright|puppeteer|selenium|webdriver|--headless|CDP|devtools, and the only 'chrome' literals in the file are these disclosure strings. This is NOT 'unavailable on this machine': Chrome 153.0.8010.50 IS installed here. Nothing ran; nothing is counted as a control; the rendered cross-product was checked by nothing.
  OPT-IN REQUESTED BUT NOT IMPLEMENTED: R6b (browser cross-product, UNIMPLEMENTED). This gate has no browser driver, no R6b rule function and no R6b control. It is NOT unavailable for want of a Chrome binary -- Chrome 153.0.8010.50 is installed on this machine (measured 2026-09-21). The other ten blocking rules DID run and their verdicts above stand; the rendered cross-product was checked by nothing.
  opt-in rules not run: 1 (R6b -- requested, NOT IMPLEMENTED, disclosed)
```

**WHAT WAS NOT DONE, STATED PLAINLY.** R6b **remains unimplemented** after this
correction. No browser driver was written, no rule function was registered, and
therefore no positive or negative control for R6b exists or is claimed. Nothing
was made to pass silently and nothing was deleted to make the discrepancy go
away — the rule is still named, still opt-in, and now truthfully described. The
reason for choosing disclosure over implementation: a browser cross-product
driver is a new subsystem (process launch, CDP transport, input enumeration,
DOM extraction, two surfaces) whose own controls would have to be built and
proven before any verdict it produced could be trusted, and a half-built R6b
that emitted a verdict would be a blindfold wearing a control's name — the exact
defect class this correction is closing. **Consequence, load-bearing as of
2026-09-21: LGM's two newly published interactive calculators
(`insulation-rebate-eligibility-checker-longmont.html` and
`insulation-rebate-payback-calculator-longmont.html`) have their rendered
cross-product checked by NOTHING.** R6a's static G1/G2 are the only cover.

**R6a (the static form) is blocking and runs every pass**, and that has not
changed.

---

## 7. KNOWN HOLES

Stated as holes, in the gate's own startup output, not discovered later.

1. **OG IMAGE RASTERS ARE OUT OF SCOPE.** `og-image.png` is a raster on all
   three properties. This gate does **not** OCR it and does not attempt to. What
   it does instead is read the SVG or `.mvg` the PNG is rasterised from, when
   that source is in the repo (`_brand_build/og-image.mvg` +
   `_generate_brand_assets.py` on GCI and LGM; `public/og-image.svg` on LGM and
   GCI). **DCI ships `og-image.png` with no `og-image.svg` in `public/`** — so
   on DCI this hole is total, and the gate says so. The GCI *"Atmos rebates
   explained"* defect was caught only because the SVG existed and was read.
2. **The gate cannot read a PDF.** Same blindness as
   `scripts/staleness_watcher.py`, documented in
   `docs/citation-registry-schema.md` §"What CANNOT be registered": no PDF
   text-extraction branch, Flate-compressed streams, *"any PDF-hosted source
   will report CHANGED forever."* R1 and R7 therefore assert the SHAPE of a
   provenance record, never the accuracy of a quotation. **The one extraction
   tool proven to work on this portfolio's sources is `pdftotext -layout`**
   (GCI `12dfcbf`: `textutil -convert txt` emits `%PDF-1.6` and reports all nine
   towns absent including the six provably present; `strings` fails identically;
   pypdf/PyPDF2/pdfminer/PyMuPDF *"were reported failing; none is installed here
   and this session did not test them"*, recorded as reported, not verified).
3. **The gate cannot read a JS-shell page.** `seed` refuses them; the recorded
   result against `co.my.xcelenergy.com` is verbatim
   `UNREACHABLE (JS shell): visible text after stripping tags is only 58 chars
   (floor 300)`. **A Googlebot User-Agent DOES trigger Xcel's server-side SEO
   render — 2,633 chars where a normal UA gets 58** (DCI `3da02df`). That
   technique is recorded here because it works and will be needed, and it is
   deliberately NOT built into this gate: a gate that makes outbound network
   requests cannot run every pass.
4. **The citation registry carries no machine-readable supersession marker.**
   Measured 2026-09-17: `docs/citation-registry.json` entry keys across all
   three properties are exactly `{claim, fingerprint, id, notes, pages, repo,
   retrieved, type, url}` plus `watchable` on the `unwatchable_sources` entries.
   **There is no `superseded`, no `superseded_by`, and no `quote` field at all.**
   `supersed*` appears in the registry as free prose exactly once, in DCI's
   `notes`. R7 therefore runs off a config list today and REQUIRES a schema
   addition (§R7).
5. **`quote` defaults to TRUE, and nothing in the portfolio sets it to True.**
   `_shared_components.py`'s `cite_inline()` reads `if src.get('quote', True):`
   on all three properties. Measured: DCI 21 entries — 0 True, 10 False, **11
   with the field absent**; LGM 31 — 0 / 8 / **23**; GCI 35 — 0 / 17 / **18**.
   So 52 of 87 entries are quotable *by default*, and a new entry is quotable
   unless its author knew to say otherwise. This is a hole in the DATA MODEL, not
   in the gate; R1 fires on it.
6. **`pages` in the citation registry is unreliable and must not be used to
   scope anything.** Measured: of 40 registry entries across the three
   properties, **36 have `pages: []`**. The four populated ones are DCI
   `XCEL_CO_REBATE_SUMMARY_25_12_215` (33) — **renamed 2026-09-20 to
   `XCEL_CO_RESIDENTIAL_REBATE_SUMMARY_2025_2026`; the old id embedded a
   withdrawn print code and is now absent from all three registries** —
   LGM same (9), LGM
   `NEC_394_12_KT_INSULATION` (1) and `IRC_P2603_5_FREEZE_PROTECTION` (1), and
   GCI `NEC_394_12_KT_INSULATION` (1). DCI's own row records the field was
   *"47 by aspiration, now 33, measured."* The gate derives page sets by reading
   `public/`, and reports registry `pages` drift as an R11 finding.
7. **The gate reads the REPO's `public/`, not the live site.** Byte-equality
   between repo and live is proven by each property's existing deploy
   verification (`curl -o` to files then `cmp`, never command substitution — and
   *never* `$(curl …)`, which strips trailing newlines and manufactures false
   mismatches). This gate does not duplicate that. Consequence: **a live/repo
   divergence is invisible to this gate**, and the gate says so.
8. **A `.thank-you { display: none; }` class of hole survives.** The gate reads
   `CSS` and can detect that a claim-bearing element is inside a selector set to
   `display:none`, but it does **not** compute a full cascade. GCI `bf240f8`
   found the real instance: a correction was *"invisible until the visitor handed
   over a name and phone number."* The gate flags `display:none` / `visibility:
   hidden` on a claim-bearing ancestor selector as an R9 `TRAP` and does not
   claim to be a layout engine.
9. **The gate does not execute the page's JavaScript — AT ALL.** This hole used
   to read *"except in opt-in R6b"*; **corrected 2026-09-21: R6b is
   unimplemented** (§6), so there is no exception and no rendered surface is
   read by anything. A
   claim assembled at runtime from string fragments has **no literal form in the
   bytes** — DCI's D3 row proved the general case: *"no `<label> — <N>% short of
   target.` sentence exists as a literal byte sequence in ANY version of these
   pages … A byte search returns 0 whether or not the bug is present, so the
   check as specified is vacuous."* R6a reads the branch structure in source for
   exactly this reason.
10. **IndexNow key files are enumerated and excluded from claim reading, by
    decision.** `1b79c33b73e0dea0470080c5c9854d20.txt` (DCI),
    `ee368c8751be4043b5e29d015679f93b.txt` (LGM),
    `d38d3ab74418efeba995b5fab6345f07.txt` (GCI). Each is 32-33 bytes and its
    content is its own filename stem. They carry no prose and cannot carry a
    claim. They are listed in the corpus block with the reason so their absence
    from the READ_SET is visibly a decision and not an oversight.
11. **Cross-property contradiction (R9) is scoped to one property per run.** A
    single invocation reads one repo. R9's cross-property half requires
    `--peer <repo>` and is skipped with an explicit
    `R9 CROSS-PROPERTY HALF SKIPPED: no --peer given` line when absent. The live
    DCI/LGM blower-door divergence in §11 is exactly what that half is for.
12. **The gate does not read `index.js`, the operator email bodies, or the
    `leads` table.** DCI's `thank-you-body-repeats-two-removed-claims.md` states
    the general problem exactly: ***"`public/*.html` is not the property. Lead
    pipeline copy, email bodies, form confirmations and hidden fields are
    surfaces a page-level grep never reaches."*** `THANK_YOU_BODY`,
    `SUCCESS_MESSAGE`, `FLAGGED_MESSAGE` and the `calc_output` hidden field are
    real claim surfaces that reached every lead, and two of them shipped claims
    a four-generator sweep had already removed. This gate reaches
    `THANK_YOU_BODY` **only** because it renders into `public/` and is in the
    CLAIM SET (§2.4). `index.js`'s `SUCCESS_MESSAGE`/`FLAGGED_MESSAGE` are
    **outside this gate** and are named here so their absence is a decision.

---

## 8. THE RULES

Eleven rules. **R1–R8 are the eight classes the brief named. R9, R10 and R11 are
additions this defect history demands, and each says so explicitly and gives the
defect that demands it.**

Each rule states, in this order: ID and name · WHAT IT ASSERTS · CLAIM TEST or
STRING LIST · SURFACES · NORMALIZATION · POSITIVE-CONTROL FIXTURE · WHAT IT
DELIBERATELY DOES NOT CATCH · PER-PROPERTY CONFIG · EXPECTED FALSE-POSITIVE
PRESSURE.

---

### R1 — FABRICATED QUOTATION

**WHAT IT ASSERTS.** Every rendered span of text that sits inside quotation
marks and is attributed to a named external source carries an explicit,
machine-readable provenance record asserting the span is verbatim from that
source.

**CLAIM TEST or STRING LIST — BOTH HALVES, DECLARED SEPARATELY, AND THE GATE
PRINTS WHICH.**

- **Half A — CLAIM TEST (blocking).** Over the CLAIM SET. Every
  `<p class="cited-stat">` whose body matches
  `According to <a …>(?P<src>[^<]+)</a>, &ldquo;(?P<stat>.*)&rdquo;` is a
  published verbatim quotation. Resolve its `CITED_SOURCES` key from the
  generator and assert `key['quote'] is True` **explicitly present**, and assert
  the entry carries a provenance block (a new required field, §R1 config).
  `quote` absent is a FAIL, not a pass — because `cite_inline()` reads
  `src.get('quote', True)`, an entry that never mentions `quote` publishes its
  `stat` inside curly quotes as the source's own words. This is the whole
  mechanism of the class.
- **Half B — STRING LIST (blocking, and the gate prints `STRING LIST — cannot be
  a claim test` beside it).** Hand-written prose that puts quotation marks around
  an attributed span without going through `cite_inline()` cannot be resolved to
  any key, so there is nothing to claim-test against. The gate flags every
  `TXT`-level match of an attribution verb within 40 characters of an opening
  `&ldquo;`/`"`/`&quot;`/`“` and requires each to appear in the config's
  `quotation_allowlist` with a `verbatim_source` and `retrieved` date. **This is
  a review queue, not a proof.** The gate says so in its own output rather than
  letting a list look like a test.

**SURFACES.** `VIS` `TITLE` `META` `OG` `TW` `LD` `LOWVIS` `EMBED` `LLMS`
`SVGTEXT`. `LD` is mandatory: DCI's C4 finding is verbatim ***"the prose cap
sweep never looked at JSON-LD"***, and a quoted claim reaching
`acceptedAnswer.text` is the same defect on the surface Google reads aloud.

**NORMALIZATION.** `DEC` then `TXT`. Mandatory, not optional: the quote glyphs
are **entities** (`&ldquo;`, `&rdquo;`, `&quot;`, `&hellip;`) and a `RAW` search
for `"` finds attribute delimiters instead. LGM `cdc3899` turned on exactly this
— the fix is verified by `&hellip;&rdquo;` / `…&quot;` / `…\"` each
appearing once, three different encodings of one character in three surfaces of
one page.

**POSITIVE-CONTROL FIXTURE — `fixtures/R1_fabricated_quotation.html`.** Derived
from the real shipped defect: LGM `186d311` D1, *"attributed a 20% CFM50
requirement to Xcel's INSULATION rebates, inside quotation marks"*, live on **11
pages**, corrected at source in `186d311` and swept out of prose in `124c014`
(release `e343ec7`). The primary source was then read directly: `"blower door"`
occurs **twice** in `24-02-205`, both outside the Qualifying Minimum Standards
table, and `"before and after"` occurs **zero** times.

```html
<!DOCTYPE html>
<html lang="en"><head><title>Air Sealing — Longmont</title>
<meta name="description" content="Xcel&rsquo;s rebate summary requires a blower door test before and after the work.">
</head><body>
<p class="cited-stat">According to <a href="https://www.xcelenergy.com/staticfiles/xe-responsive/Marketing/Residential-Insulation-Air-Sealing-Rebate-24-02-205.pdf" rel="noopener" target="_blank">Xcel Energy&rsquo;s residential rebate summary</a>, &ldquo;Xcel&rsquo;s insulation and air sealing rebates require a documented reduction in air leakage of at least 20% in CFM50, verified by a blower door test before and after the work.&rdquo;</p>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"Is a blower door test required?","acceptedAnswer":{"@type":"Answer","text":"Xcel's rebate summary says “verified by a blower door test before and after the work.”"}}]}</script>
<p>The Building Science Corporation found that air leaks move &ldquo;far more moisture
into an assembly than vapor diffusion does,&rdquo; so sealing comes first.</p>
</body></html>
```

The third block is the second real instance and is in the fixture on purpose:
DCI's `a7-cited-sources-verification.md` records that `BSC_AIR_LEAKAGE_MOISTURE`
had ***"zero site phrases appear in BSD-014, both 'far more' and the sequencing
rule invented"*** — and it renders as hand-written prose, so **only Half B can
see it**. The fixture proves both halves fire. Expected control output:

```
  canary+ R1        fixtures/R1_fabricated_quotation.html   DETECTED  (half A: 1, half B: 1, LD: 1)
```

**WHAT IT DELIBERATELY DOES NOT CATCH.**
- **It cannot tell you whether a quotation is accurate.** It asserts the presence
  and shape of a provenance record. §7(2): the gate cannot read the PDF. The
  15-of-18 deviation rate DCI measured in `147185c` was found by **fetching every
  source live, 1:1, verifier-never-corrector** — that is a pass, not a gate.
- Quotation marks in ordinary prose with no attribution (dialogue, scare quotes,
  a quoted UI label).
- `quote=False` entries — an attributed paraphrase is the sanctioned form and is
  what `JOHNSTOWN_GAS_XCEL`, `XCEL_INSULATION_AIR_SEALING`, `MILLIKEN_GAS_XCEL`
  and the three de-quoted LGM Efficiency Works entries all use.
- **A quotation that is exact but truncated.** LGM `cdc3899` N1: the garage
  exclusion quotation *"became character-for-character exact last pass and then
  stopped at a comma with a bare closing quote, so a partial list read as the
  whole clause."* R1 does **not** detect a missing ellipsis. Named because it is
  a real recorded defect this rule cannot see.
- **A quotation that is exact and misleading by selection.** GCI `bf240f8` (3):
  `MILLIKEN_GAS_XCEL` quoted *"Xcel Energy provides gas and electricity for most
  of Milliken"* — exact, and *"quoting only the gas half would be selective
  misquotation"* because the same source names Poudre Valley REA for two
  subdivisions. R2 catches the electric-utility half of that; R1 does not.

**PER-PROPERTY CONFIG.**

```json
"R1": {
  "cited_stat_class": "cited-stat",
  "attribution_template": "According to {determiner}{source}, ",
  "quote_open": ["&ldquo;", "“", "&quot;", "\""],
  "quote_close": ["&rdquo;", "”", "&quot;", "\""],
  "attribution_verbs": ["According to", "says", "states", "per ", "'s own",
                        "&rsquo;s own", "reports", "found that", "writes",
                        "notes that", "confirms"],
  "require_explicit_quote_field": true,
  "require_provenance_block": true,
  "quotation_allowlist": []
}
```

**REQUIRED SCHEMA ADDITION (this rule cannot reach full strength without it).**
`CITED_SOURCES` entries whose `quote` is True must carry
`"provenance": {"retrieved": "YYYY-MM-DD", "artifact": "<sha256 or URL>",
"extraction": "pdftotext -layout|curl|…", "verbatim_line": "<line ref>"}`.
Precedent exists and is already in use: DCI and LGM's
`XCEL_CO_RESIDENTIAL_REBATE_SUMMARY_2025_2026` registry entries (**renamed
2026-09-20 from `XCEL_CO_REBATE_SUMMARY_25_12_215`, whose id embedded a
withdrawn print code**) carry SHA-256, byte count,
extraction chain and line references in `notes` as free prose. This makes that
record structured. Until it lands, the gate prints
`R1 DEGRADED: provenance block not yet in the schema; asserting quote field only`.

**EXPECTED FALSE-POSITIVE PRESSURE.**
- Legitimate `quote=False` paraphrases whose `stat` happens to contain a nested
  quoted term.
- Prose quoting the site's **own** earlier wording in order to retire it. This
  is a heavily-used convention here and the gate must not fire on it: GCI's
  `ground-truth.md` keeps *"Gas utility: Atmos Energy"* alive inside its own
  supersession bullet, and canon's `METHODS/RECEIPTS.md` returns `4` for a
  `NACH50` grep where **two** real occurrences exist, because each struck-through
  occurrence is followed by a correction note *that itself names the string.*
  **Any rule matching a banned string must distinguish an assertion from a
  correction that quotes it.** The gate does this by suppressing a hit whose
  enclosing element or preceding 200 `TXT` characters contain a supersession
  marker from `config.correction_markers` (`SUPERSEDED`, `CORRECTED`,
  `RETIRED`, `[CORRECTED`, `SUPERSESSION —`, `~~`).
- `"If you do hire after the quote, that's between you and the contractor"` and
  `"If a quote skips both, get another quote"` — the word *quote* meaning a
  price estimate, present in all three `_shared_components.py`. The rule keys on
  quotation **glyphs** plus an attribution verb, never on the word.

---

### R2 — WRONG-UTILITY CLAIM

**WHAT IT ASSERTS.** For every page and every town in that page's scope, the
page attributes no program, rebate, incentive, paperwork or wayfinding
destination to a utility that does not serve that town — **and asserts no
residential electric utility at all where the config forbids it.**

**CLAIM TEST. Not a string test, and this is the rule where that distinction is
load-bearing.** Three utility-identity claim vectors carry no utility string in
the page's own HTML, and all three shipped:

1. **The referenced asset.** GCI's `og-image` said **"Atmos rebates explained"**
   and `og:image`/`twitter:image` pointed at it from **every page including
   Johnstown, Milliken and Severance** (`e6cb44e`, via
   `_generate_brand_assets.py`'s `OG_FOOTER`). Those pages contained `Atmos`
   zero times. Caught only because the SVG existed and was read.
2. **The inherited `cite_keys`.** The three Xcel-gas town pages carried
   `ATMOS_AIR_SEALING_REBATE` / `ATMOS_ATTIC_REBATE` in `cite_keys`
   (`e6cb44e` replaced them with four new keys). And the canon addendum's own
   proof case: LGM's comparator page carried `$1.16`/`$0.77` *"even though
   neither string appears anywhere in that page's generator … It is in something
   it points at."*
3. **The wayfinding URL.** A rebate anchor whose visible label names no utility
   and whose `href` does. `2cecf33` records the inverse as a deliberate
   invariant: the Xcel-gas towns *"did NOT acquire the Atmos wayfinding link (0
   anchors each)"* — an invariant only an `href`-reading test can hold.

So the test is: resolve `page → town scope` from the config (slug map, plus
JSON-LD `areaServed[]`, plus the `<h1>`), then over the page's **CLAIM SET**
resolve `page → attributed utilities` from (a) utility names in `TXT`, (b) every
`CITED_SOURCES` key rendered, (c) every `href` host matched against
`config.utility_domains`, (d) every referenced SVG's `SVGTEXT`, (e) every
territorially-scoped shared constant. Assert
`attributed ⊆ allowed(town) ∪ non_territorial_programs`, and separately assert
`electric_utilities_named == ∅` where `forbid_electric_utility_naming` is set.

Three further assertions the history forces:

- **HEDGE PRESERVATION, both halves.** `2cecf33`: the hedged towns *"still open
  'Where Atmos Energy serves the home' and still close with the explicit
  non-confirmation — **BOTH halves load-bearing, and removing a figure is never
  a licence to upgrade a conditional.**"* Assert each hedged town's page carries
  both its opening condition and its closing non-confirmation.
- **PER-TOWN QUALIFIER, verbatim and non-interchangeable.** GCI ground-truth:
  *"each Xcel-gas town's OWN qualifier travels verbatim, and they are not
  interchangeable. Johnstown **NONE** — its source states Xcel for gas flatly.
  **Never invent a qualifier for Johnstown.**"* Milliken `most of Milliken`;
  Severance `most locations in Severance`. Assert exact-match presence and assert
  no cross-contamination.
- **TOWN-BLIND TOOL OUTPUT.** GCI `e6cb44e`/`bf240f8`: four calculators
  *"returned an Atmos-attributed verdict computed from build era and R-value
  alone while never asking the visitor's town."* Assert no `JS` string literal
  reachable from a verdict branch names a utility unless a town input exists in
  the same tool. The fourth calculator was missed by the first pass and its
  page's `<h1>` *"is the only one of the five that does not contain 'Greeley'"* —
  so scope by the **config's slug map**, never by whether the town name appears
  in the title.

**SURFACES.** `VIS` `TITLE` `META` `OG` `TW` `LD` (`areaServed`, `knowsAbout`,
`description`, `acceptedAnswer`) `JS` (including comments) `LOWVIS` `ATTR`
(`href`, `alt`, `content`) `LLMS` `SVGTEXT` `EMBED`.

**NORMALIZATION.** `TXT` for propositions; `RAW` for `href` and `JS` comments;
`SRC` over the generators for the reachability half — `_shared_components.py`,
`_area_pages.py`, `_generate_area_pages.py`, `_generate_calculator_pages.py`,
`_service_pages.py`. `TXT`'s whitespace collapse is mandatory here: GCI
`348baf9` records that *"phrase checks were run on newline-collapsed text, never
line-based, because a line-based check produced a false absence earlier in this
pass."*

**POSITIVE-CONTROL FIXTURES — three, because the class has three vectors.**

`fixtures/R2a_wrong_utility_visible.html` — from GCI `e6cb44e`'s pre-state, the
`THANK_YOU_BODY`/`REBATE_ACKNOWLEDGMENT` pair that rendered on **35 pages** and,
per the lane row, *"told a Severance homeowner, after they submitted the lead
form, to 'ask who files the Atmos paperwork'"*. Both strings are the ones
`348baf9` verified as going to zero residual occurrences:

```html
<!DOCTYPE html>
<html lang="en"><head><title>Insulation in Severance, CO</title></head><body>
<h1>Insulation in Severance</h1>
<div class="thank-you">
<p>While you wait, it helps to ask who files the Atmos paperwork.</p>
<p>Atmos Energy&rsquo;s residential rebates are the primary insulation rebate stack for Greeley-area projects in 2026.</p>
</div>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"LocalBusiness","areaServed":[{"@type":"City","name":"Severance"}],"knowsAbout":["Atmos Energy residential insulation rebates"]}</script>
</body></html>
```

`fixtures/R2b_wrong_utility_no_string.html` — **the no-string vector. The word
`Atmos` does not appear in this file.** The claim arrives entirely through
`og:image`, whose target SVG the gate must read.

```html
<!DOCTYPE html>
<html lang="en"><head><title>Insulation in Johnstown, CO</title>
<meta property="og:image" content="https://greeleycoloradoinsulation.com/og-image.svg">
<meta name="twitter:image" content="https://greeleycoloradoinsulation.com/og-image.svg">
</head><body>
<h1>Insulation in Johnstown</h1>
<p>Natural gas service in Johnstown is provided by Xcel Energy.</p>
</body></html>
```

paired with `fixtures/R2b_og-image.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630">
<text x="60" y="560" font-size="34">Atmos rebates explained</text>
</svg>
```

`fixtures/R2c_wrong_utility_anchor_only.html` — the URL vector. Visible label
names no utility; the `href` host does.

```html
<!DOCTYPE html>
<html lang="en"><head><title>Insulation in Milliken, CO</title></head><body>
<h1>Insulation in Milliken</h1>
<p>Rebate amounts change annually, so we send you to the program itself:
<a href="https://www.atmosenergy.com/rebates" rel="noopener" target="_blank">see current rebate amounts</a>.</p>
</body></html>
```

**WHAT IT DELIBERATELY DOES NOT CATCH.**
- **Territory itself.** A tariff is authority for PRESENCE, never for
  EXCLUSIVITY (GCI ground-truth, and canon `f1c4008`'s transferable rule part 4).
  The gate enforces the config; it cannot discover that a town's utility changed.
  Re-establishing territory is a two-legged primary-source pass — the town's own
  source **and** the utility's own tariff — *"because they fail in opposite
  directions: a tariff is silent about every town it does not serve, so it can
  only exclude, never enumerate a competitor."*
- **The known, reasoned disclosure gap.** GCI ground-truth records that every
  sitewide gas-split sentence names six of nine towns, so *"a Windsor reader on
  the Windsor page sees a split that omits their town — a direct consequence of
  the presence-not-exclusivity ruling; the Director has been told and is not
  reversing it."* The gate must not fire on it, and the config records it as
  `known_disclosure_gaps`.
- **Whether a given household actually qualifies.** `e6cb44e`: *"nothing asserts
  an Xcel insulation rebate is available to a given homeowner (Xcel tiers
  eligibility by which fuels it supplies; a household's tier is not
  establishable here)."*
- **OG image RASTERS.** §7(1). The SVG path works; `og-image.png` on DCI has no
  SVG sibling in `public/` and is a total hole there.
- **A second gas utility inside one municipality.** Two utilities can hold gas
  territory inside one Colorado municipality; the config's three-state model
  (`CONFIRMED` / `HEDGED` / `UNKNOWN`) encodes what is known, and *"there is no
  third state — 'unconfirmed' is a task, not a resting place."*

**PER-PROPERTY CONFIG.** See §12 for all three filled in. Shape:

```json
"R2": {
  "towns": { "<Town>": { "gas": "Atmos Energy|Xcel Energy|UNKNOWN",
                         "gas_state": "CONFIRMED|HEDGED|UNKNOWN",
                         "gas_qualifier": "<verbatim, may be empty>",
                         "electric": "…|UNRESOLVED",
                         "electric_program": "…|null",
                         "page_slugs": ["insulation-severance.html"] } },
  "forbid_electric_utility_naming": true,
  "utility_names": ["Atmos Energy", "Atmos", "Xcel Energy", "Xcel",
                    "Longmont Power & Communications", "LPC",
                    "Poudre Valley REA", "PVREA", "United Power",
                    "Efficiency Works"],
  "utility_domains": { "atmosenergy.com": "Atmos Energy",
                       "xcelenergy.com": "Xcel Energy",
                       "co.my.xcelenergy.com": "Xcel Energy",
                       "efficiencyworks.org": "Efficiency Works",
                       "longmontcolorado.gov": "Longmont Power & Communications" },
  "non_territorial_programs": ["Colorado Weatherization Assistance Program",
                               "Colorado Energy Office", "ENERGY STAR"],
  "territorial_constants": ["REBATE_ACKNOWLEDGMENT", "THANK_YOU_BODY",
                            "ENTITY_DESCRIPTION", "GAS_UTILITY_SPLIT_FACT"],
  "hedge_pairs": [["Where Atmos Energy serves the home", "<closing non-confirmation>"]],
  "known_disclosure_gaps": ["…"]
}
```

**EXPECTED FALSE-POSITIVE PRESSURE.**
- **`Ault` inside `default` and `fault`.** Measured: `/usr/bin/grep -ci 'ault'`
  gives **8** where the locality appears **once** (GCI `12dfcbf`). The gate uses
  `\b`-anchored, case-sensitive matching for town names, and runs the
  known-present control (`Greeley` on GCI, `Longmont` on LGM, `Denver` on DCI)
  before trusting any absence.
- **`La Salle` vs `LaSalle`.** Recorded in canon `f1c4008` as *"a FALSE ABSENCE
  indistinguishable from the true absence"* — the repo spells it `LaSalle`, the
  tariff `La Salle`. The config carries `spelling_variants` per town.
- **`Weld County`** — legitimate on LGM as an Erie-split disclosure, which is why
  `_artifact_grep.sh` reports it as `INFO` rather than failing. The equivalent
  here is a `REVIEW` classification, not a FAIL.
- **Sibling town names as legitimate proper nouns.** GCI holds a Director-granted
  DRCOG exception; LGM holds none. Allowlist entries must be Director-granted,
  recorded inline, and *"never widened past the exact string"* —
  `_artifact_grep.sh`'s own rule, inherited verbatim.
- `stack` as a plumbing noun and `stack effect` as building science (~30
  occurrences on DCI) collide with R4, not R2, but the same allowlist discipline
  applies.

---

### R3 — REBATE DOLLAR FIGURE

**WHAT IT ASSERTS.** No artifact states or implies what a rebate, incentive or
bonus PAYS — as a dollar amount, a bare numeral in a money context, a cap, a
rate, a rank, a magnitude or a superlative.

**CLAIM TEST for the rank/magnitude half; STRING+WINDOW LIST for the numeral
half, and the gate prints that split.** The numeral half genuinely cannot be
more than an anchored pattern with a context window, and per §4 it must say so.

The Director's ruling of 2026-09-09, broad reading, final, executed as DCI
`5703f8c` (**198 occurrences → 0**), GCI `2cecf33` (**206 → 0**) and LGM
`d6e8dab` (**133 removed, 8 kept**) — **537 figures by the three commits' own
acceptance gates.** (Canon's addendum states 545; the 8-figure difference is
recorded here unresolved rather than reconciled, per §4's own rule.)

Four sub-tests, because the class defeated four instruments in sequence:

- **T1 — `$`-anchored.** `\$[0-9][0-9,.]*` over `RAW`, all artifact types. This
  is the existing acceptance gate, verbatim from `2cecf33`:
  `/usr/bin/grep -rhoE '\$[0-9][0-9,.]*' public/ --include='*.html'
  --include='*.txt' --include='*.js' --include='*.json' --include='*.xml'`. It
  is kept because it is the one already in use, and **its blind spot is printed
  with its result**, per §4(5) and canon `a891b83`.
- **T2 — BARE NUMERALS IN A MONEY WINDOW.** The rule T1 cannot reach. From GCI
  `f0203ad` D1, verbatim: the cap *"carried no `$`, which is exactly why the
  `$`-anchored acceptance gate could not see it."* The second gate that commit
  installed, adopted here as T2's shape:
  `\b(1550|1075|1325|1150|663|125|575|70000|99920)\b` windowed against
  `atmos|rebate|cap|rate|incentive|wap|weatheriz|pays`. Generalised: the config
  supplies `known_figures`, and the gate additionally scans **every** 3-to-6
  digit integer and every `0\.[0-9]+` decimal rate inside a ±120-character
  `DEC`-level window containing a `money_word`.
- **T3 — RANK, MAGNITUDE AND SUPERLATIVE, with no `cap` anchor and no numeral.**
  The genuine claim test. From GCI `a91dfd4`, verbatim: *"'Second-largest' is
  that claim in words the phrase list did not contain … an instrument matched on
  surface form while the defect was defined by meaning. Twice in one pass."* The
  named live instances: `_generate_service_pages.py` `CROSS_CONTEXT['attic'] =
  "the largest rebate"` — **live on six pages, a rank claim with no 'cap' in it
  at all**; *"the published per-measure amounts drop to a small fraction of the
  figures usually quoted"*; *"the Atmos caps say the same thing — the attic cap
  is the larger of the two"*; and *"the smallest cap in its residential
  program"*, **which that lane's own first pass introduced as a "fix" for a
  figure.** The standing instruction: **"Do not substitute a superlative for a
  figure."**
- **T4 — JSON-LD AND JS COMMENTS.** Both are `RAW` surfaces T1 covers by glob
  but which every prose-shaped sweep missed. DCI C4: `$600` in
  `Organization.knowsAbout` on ~71 pages, *"the prose cap sweep never looked at
  JSON-LD"*, found independently by four row agents.

**SURFACES.** All of `VIS` `TITLE` `META` `OG` `TW` `LD` `JS`(+comments) `CSS`
`LOWVIS` `ATTR` `LLMS` `SITEMAP` `EMBED` `SVGTEXT`. The JS-comment surface is
non-negotiable: GCI `f0203ad`'s cap shipped *"inlined into
public/insulation-cost-calculator-greeley.html, so it was in view-source and in
what LLM crawlers read on a live 200 page."*

**NORMALIZATION.** `RAW` for T1/T2/T4 (a JS comment is not in `TXT`); `TXT` for
T3 (a rank claim wraps lines like any other prose); `SRC` for the generator-side
reachability check.

**POSITIVE-CONTROL FIXTURES — three.**

`fixtures/R3a_js_comment_cap.html` — **verbatim from canon
`METHODS/CANDIDATE-do-not-scope-with-grep-over-html.md` lines 122-123, which
quotes the bytes that shipped live on GCI for two days** (fixed in `f0203ad`;
the comment was written 2026-09-08). The fixture must fire on T2 and **must NOT
fire on T1** — that asymmetry is the control:

```html
<!DOCTYPE html>
<html lang="en"><head><title>Insulation Cost Calculator — Greeley</title></head><body>
<script>
// CAP/RATE (1550 / 0.75) and money() were DELETED 2026-09-08. They existed
// only to print Atmos's rate and cap in this tool's verdict;
(function(){ var out = document.getElementById('calcOutput'); }());
</script>
</body></html>
```

`fixtures/R3b_jsonld_amount.html` — the JSON-LD vector, built from DCI's C4
finding (`$600` in `knowsAbout`, ~71 pages) and GCI's largest removed figure
(`$1,550` × 77, `2cecf33`):

```html
<!DOCTYPE html>
<html lang="en"><head><title>Attic Insulation Rebates</title>
<meta name="description" content="The Atmos attic rebate pays 75% of project cost up to $1,550.">
</head><body>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","knowsAbout":["Xcel $600 Insulation + Air Sealing Combo Bonus"]}</script>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"What does Atmos pay?","acceptedAnswer":{"@type":"Answer","text":"The attic rebate pays 75% of the project cost up to $1,550."}}]}</script>
</body></html>
```

`fixtures/R3c_rank_claim_no_numeral.html` — **the T3 control. No numeral, no
`$`, no `cap`.** Two literal strings from GCI `a91dfd4`:

```html
<!DOCTYPE html>
<html lang="en"><head><title>Attic Insulation — Greeley</title></head><body>
<p>Of the measures Atmos rebates, attic insulation carries the largest rebate,
so it is usually where a project starts.</p>
<p>Air sealing sits at the smallest cap in its residential program, and the
published per-measure amounts drop to a small fraction of the figures usually
quoted.</p>
</body></html>
```

**WHAT IT DELIBERATELY DOES NOT CATCH — and every exclusion below is a Director
ruling, quoted from `2cecf33`'s own list ("RULINGS 2/3/4 RESPECTED") and
`d6e8dab`'s "WHAT SURVIVED, DELIBERATELY".**
- **Project costs as costs.** LGM's 8 surviving `$` figures are *"JS-comment
  installed-COST rates in the attic calculator (`$1.50` ×3, `$3.00`, `$3.50` ×2,
  `$300`, `$1,200`) — Ruling 2, costs not payouts."* Measured live 2026-09-17:
  those 8 are **the only `$` figures anywhere under LGM's `public/`**.
- **Energy-savings figures** (Ruling 3).
- **Calculator outputs computed from visitor input** (Ruling 4). LGM's 4
  air-sealing tier thresholds (15/25/33/50% measured reduction) survive as
  *"thresholds a homeowner is measured against, not amounts anyone is paid."*
- **R-values, IECC and ENERGY STAR figures.** DCI measured **331 occurrences of
  `R-15`/`R-49` across 70 files, all 331 IECC Table R402.1.3 or ENERGY STAR
  retrofit claims; zero qualified as Xcel thresholds.** The classifier that
  established that is recorded and is the model: require an Xcel+eligibility
  window carrying no `IECC` / `R402` / `ENERGY STAR` / `Climate Zone` /
  `ceiling minimum` / `top plate` / `eave` marker.
- **Structure percentages already present** — `75%`, `50% of project cost`,
  `capped at 100% of project cost`, `30% of project cost`. Ruling 2. **None
  added.**
- **The `20% CFM 50` / `CFM 25` qualifying thresholds** (Ruling 3).
- **GCI's two Colorado WAP income-eligibility limits — a STANDING EXCEPTION,
  Director ruling 2026-09-10, the SECOND ruling, restored in `25cb16b`.**
  `$70,000` (single-person Weld County household) and `$99,920` (household of
  four), each ×10 = **20 occurrences, and measured live 2026-09-17 as the only
  `$` figures anywhere under GCI's `public/`.** The ruling's reasoning, verbatim:
  *"They are eligibility thresholds for a FREE, income-qualified government
  program, not per-measure rebate amounts. A homeowner cannot self-assess
  against 'the highest of 60% of state median income, 80% of area median income,
  or 200% of the federal poverty level' — the figures do the work the page exists
  to do. Stripping them did not remove a liability, it removed the answer."*
  Verified first-party twice, independently, against the Colorado Energy Office's
  WAP income-eligibility Google Sheet, Weld row verbatim
  `Weld,"$70,000","$79,920","$90,000","$99,920","$107,920"`. A dated, attributed
  STANDING EXCEPTION block in `_shared_components.py` exists specifically so a
  future sweep does not strip them again; **the gate's config is the second copy
  of that guard.**
- **Dollar figures inside `docs/citation-registry.json`.** Deliberate, recorded
  in DCI `7786ce5` ("Record why docs/citation-registry.json keeps its dollar
  figures"). The registry is an internal record of what a document states; the
  ban is on page copy. The gate reads `public/`, so this is out of scope by
  construction, and the config names it so nobody re-scopes it in.
- **A removal note that restates the figure it removed.** The gate catches the
  *numeral* (T2) but not the general form. Canon `a891b83`: *"A removal note that
  restates the figure it removed re-publishes it … record the fact and the
  reason, never the numeral."* R10 covers the inverse (a promise with no figure).

**PER-PROPERTY CONFIG.**

```json
"R3": {
  "dollar_pattern": "\\$[0-9][0-9,.]*",
  "known_figures": ["1550","575","1325","1075","1150","663","125","600","500",
                    "400","350","200","60","25","15","2000","1000","1500",
                    "1250","770","70000","99920"],
  "rate_pattern": "\\b0\\.[0-9]{1,2}\\b",
  "money_words": ["rebate","incentive","bonus","cap","capped","pays","paid",
                  "payout","amount","reimburse","match","credit","discount",
                  "per measure","up to"],
  "rank_words": ["largest","biggest","smallest","larger","smaller","highest",
                 "lowest","second-largest","most","greater of","lesser of",
                 "the larger of the two","small fraction","a fraction of",
                 "ranks","ordering","exceeds"],
  "window_chars": 120,
  "allowed_figures": [ /* per property; see §12 */ ],
  "cost_context_markers": ["installed cost","per square foot","per sq ft",
                           "project cost","materials","labor"],
  "code_context_markers": ["IECC","R402","ENERGY STAR","Climate Zone",
                           "ceiling minimum","top plate","eave"],
  "exclude_paths": ["docs/citation-registry.json"]
}
```

**EXPECTED FALSE-POSITIVE PRESSURE — measured, not guessed.** Canon `b152b08`
records the real number: three JS-comment scans *"fired **153 times** (DCI 150,
LGM 2, GCI 1) and every hit was adjudicated away as a non-rebate numeral: form-page
counts, a commit SHA, R-values, decision-path counts, and LGM's permitted
installed-cost rates."* Additional pressure:
- `0.75` matching a **CSS `stroke-width`** (GCI `f0203ad`: *"a bare-rate check
  for 0.75 finds only a CSS stroke-width"*).
- `20-40%` as **wind-washing R-value degradation** and `15-30%` as **HVAC load
  reduction** — DCI ground-truth: *"Those are different claims about different
  quantities and were deliberately kept. Do not strip them on a literal string
  match — that is the instance-not-class error running in the opposite
  direction."*
- Four-digit years (`2024`, `2025`, `2026`) inside the 3-6-digit integer scan.
- `$600 Insulation + Air Sealing` and `basement + main floor` — legitimate prose
  falsely flagged once already as broken sentences with a stray `+`.
- R3's expected steady state is therefore `RAW` in the low hundreds with
  `ADJUDICATED` at 0, and **that is exactly why the §4 enumeration of removed
  items is mandatory for this rule above all others.**

---

### R4 — STACKING ASSERTION OR DENIAL

**WHAT IT ASSERTS.** No artifact asserts that two incentive programs combine,
and no artifact denies it. **Silence is the compliant state, and affirmative
denial is equally a defect.**

**CLAIM TEST. It has to be, and the history proves why a string list cannot
work.** From LGM's `ground-truth.md`, the Director's rule verbatim:

> **THE RULE, as ruled by the Director: IF STACKING CANNOT BE VERIFIED, DO NOT
> MENTION STACKING.** It governs what the copy may claim. It is not a factual
> assertion that the programs are incompatible.
>   - Verified → we MAY state it, sourced.
>   - Unverified or ambiguous → SILENCE.
>   - **Silence is NOT denial.** Copy that affirmatively denies stacking is
>     also an unverified claim, in the opposite direction, and is the same
>     defect as claiming it.

And the recorded cost of getting the *rule* wrong: LGM's ground-truth carries
`CORRECTED 2026-08-22` — the bullet had read *"these two programs must NEVER be
described as stacking"*, which *"was a MISRECORDING of the rule as a
prohibition … The misrecording propagated: **an auditor given the prohibition
form searched only for copy CLAIMING stacking and never searched for copy
DENYING it.**"*

Why a string list fails, verbatim from DCI `31484f1`: **"`layer` was ON THE
SEARCH LIST and *'the Whole Home Efficiency Bonus layers on top'* shipped anyway
— because a list of strings only finds the strings you already thought of."**
The proposition survived **two** string-targeted sweeps (`fca41f6`, `b47a3c2`)
and needed a third that *"enumerated every
`stack|combin|on top of|alongside|layer|bundl|unlock|add-on` token in the BUILT
output and **read each one in its sentence**."* The first sweep's commit was
titled *"neutralize Xcel-side stacking claims"* and *"left the class standing on
**70 of 72 live pages**, including one sentence after an edit it had just made."*

So the test is: enumerate every `stacking_token` in the CLAIM SET, resolve each
to its **sentence** (`TXT`, sentence-split), and classify each sentence as
`ASSERTS` / `DENIES` / `NEUTRAL` / `ATTRIBUTED-AND-SOURCED`. The classifier keys
on (a) two or more distinct program names from `config.programs` in one sentence,
(b) a combination predicate, (c) polarity — negation, `not`, `cannot`, `neither`,
`are not designed to`, `not in the way`. `ASSERTS` and `DENIES` both FAIL.
`ATTRIBUTED-AND-SOURCED` passes only when the sentence names its publisher and
resolves to a `CITED_SOURCES` key — LGM's ground-truth licenses exactly this
much: *"stacking may now be DESCRIBED as published by Efficiency Works, with
that attribution. It does not license the site to author its own combined
total."*

**SURFACES.** `VIS` `TITLE` `META` `OG` `TW` `LD` (**FAQPage `acceptedAnswer`
above all** — GCI's denial shipped there *"as this site's stated position"*)
`JS` `LOWVIS` (nav labels and tile labels: DCI's `"WHE Bonus Stacking"` label
*"still carried the proposition in site voice after the page itself had been
retitled"*) `ATTR` `LLMS` `EMBED`. `LLMS` is mandatory: DCI's
`"Xcel rebate-stack eligibility"` in `llms.txt` was *"site voice,
unattributed — present in EVERY commit including the pre-pass baseline"* and
*"survived five stacking sweeps and ten adversarial reads"* (`fb08735`).

**NORMALIZATION.** `TXT`, sentence-split. `SRC` for the generator half, because
`REBATE_ACKNOWLEDGMENT` reads `"...the primary rebate " "stack for Denver-area..."`
and *"no single-string grep or regex can see the phrase"*; DCI `fb08735` records
the same literal split in `llms.txt`'s source matching *"the `.pyc` and not the
`.py`."*

**POSITIVE-CONTROL FIXTURES — two, one per direction. Both directions are
required; a rule that only fires on assertion reproduces the 2026-08-22
misrecording.**

`fixtures/R4a_stacking_denial_jsonld.html` — from GCI `f0203ad` D3, which shipped
*"in the rebate hub's FAQPage JSON-LD as this site's stated position"*:

```html
<!DOCTYPE html>
<html lang="en"><head><title>Insulation Rebate Hub — Greeley</title></head><body>
<details><summary>Can I stack these programs?</summary><p>Not in the way people
usually hope. The free weatherization program and the Atmos rebates are not
designed to be combined on the same measure.</p></details>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"Can I stack these programs?","acceptedAnswer":{"@type":"Answer","text":"Not in the way people usually hope. The free weatherization program and the Atmos rebates are not designed to be combined on the same measure."}}]}</script>
<p>Knob-and-tube work does not qualify, and not with rebate stacking either.</p>
</body></html>
```

`fixtures/R4b_stacking_assertion_prose.html` — the assertion direction, five
strings quoted from DCI `b47a3c2`/`31484f1`, **including `layers on top`, the one
that was on the search list and shipped anyway**:

```html
<!DOCTYPE html>
<html lang="en"><head><title>Whole Home Efficiency Bonus — Denver</title>
<meta name="description" content="Multiple Xcel programs stack, so you can stack rebates instead of leaving money on the table.">
</head><body>
<h1>How Do I Stack the Whole Home Efficiency Bonus on Top of Standard Rebates?</h1>
<p>The Whole Home Efficiency Bonus layers on top of the standard rebate, and
Xcel adds a 25% bonus on top of the standard rebates.</p>
<p>You can layer the Xcel IQ Program on top for further coverage, so you can
stack rebates instead of leaving money on the table.</p>
<p>The federal 25C credit will not stack on top of Xcel rebates.</p>
<nav><a href="/whole-home-efficiency-bonus-stacking-denver.html">WHE Bonus Stacking</a></nav>
</body></html>
```

Note the fourth paragraph is a **denial** sitting inside an
assertion-heavy fixture — DCI `b47a3c2` neutralised exactly that sentence
(*"the federal 25C 'stack on top of Xcel rebates' denial"*) alongside the
assertions, in one sweep. The fixture therefore also proves the classifier
reports polarity per sentence rather than per page.

**WHAT IT DELIBERATELY DOES NOT CATCH.**
- **`stack` as a noun for a market's incentive landscape.** Three separate
  Director-adjacent rulings keep this: DCI's `REBATE_ACKNOWLEDGMENT` (~69 pages)
  where *"'stack' is a noun for the program set, asserting nothing about
  combinability — narrow reading of Ruling 6 confirmed by the coordinator"*; and
  GCI `f0203ad`'s *"the primary insulation rebate stack in Greeley, Evans and
  Eaton"*, kept, **flagged to the Director**, with *"the fix, if the ruling is
  read to cover the word rather than the claim, is one word"* — then changed by
  a one-word Director ruling in `38b80e0` (`"rebate stack"` → `"rebate
  programs"`). The gate classifies, it does not decide; a `NEUTRAL` noun use is
  reported under `FILTER`, enumerated, never failed.
- **`stack-effect` / `stack effect`** — building science, ~30 occurrences on
  DCI. Plus **plumbing stack**, *"how your home stacks up"*, *"three stacked
  reasons"*, *"factors stack against"*, *"hot-stacked lifts"* (a spray-foam cure
  schedule), and *"stacking new insulation on a compacted base"* (physical).
  All six are named in DCI's lane row as **"LEGITIMATE USES THAT MUST NEVER BE
  SWEPT."**
- **A third party's own published combination, attributed.** Efficiency Works'
  own sheet has a column headed `"Xcel rebate"` and a `"Total potential
  incentives"` column that is the arithmetic sum. Describing that, attributed, is
  licensed. Authoring a combined total is not.
- **The operational sequencing content inside a reframed Q&A.** GCI `f0203ad`
  kept *"check-the-free-program-first sequencing, ask both before scoping"* —
  the Q&A was *"REFRAMED, not reworded"*.
- **A retired prohibition quoted in order to retire it.** LGM's ground-truth
  preserves the prohibition wording deliberately, and
  `_shared_components.py:25-31` still carries it as a record. Suppressed by
  `config.correction_markers`, same mechanism as R1.
- **Whether stacking is actually permitted.** The gate enforces silence; it
  cannot verify combinability.

**PER-PROPERTY CONFIG.**

```json
"R4": {
  "stacking_tokens": ["stack","stacks","stacked","stacking","combin","combined",
                      "combine","on top of","on top","alongside","layer","layers",
                      "bundl","unlock","unlocks","add-on","plus the","in addition to",
                      "together with","both programs","either program"],
  "combination_predicates": ["stack","combine","layer","unlock","apply together",
                             "both apply","add to","on top of"],
  "denial_markers": ["not","cannot","can't","never","neither","no ",
                     "are not designed","not in the way","separate eligibility",
                     "are never combined","do not combine","does not combine"],
  "programs": [ /* per property; see §12 */ ],
  "legitimate_uses": ["stack-effect","stack effect","plumbing stack","flue",
                      "stacks up","stacked reasons","factors stack against",
                      "hot-stacked","compacted base","can lights"],
  "noun_use_constants": ["REBATE_ACKNOWLEDGMENT"],
  "attributed_exception": { "allowed": true,
                            "requires_publisher_named": true,
                            "requires_cited_source_key": true }
}
```

**EXPECTED FALSE-POSITIVE PRESSURE.** High, and measured: DCI's third sweep
reviewed **178 stacking-language sites, 41 naming a non-Xcel program, and
neutralised 9.** GCI measured **`cap/caps in output RAW=37, ADJUDICATED(rank
claims)=0`** on the adjacent class. Expect `RAW` in the low hundreds. The
specific benign copy that will trip it, all present today: *"Can I just add new
insulation on top of old, failing insulation?"* (DCI), *"Can I add radiant
barrier on top of my existing attic insulation?"* (LGM), *"Can new insulation go
on top of the old?"* (GCI), *"can happen on top of it"* (LGM, GCI), *"can
address the same problem at a lower combined cost"* (LGM), *"doesn't this
calculator show one combined rebate-adjusted price?"* (LGM) — every one an
insulation-physics or pricing question, none a program claim. The classifier's
two-distinct-program-names requirement is what separates them, and the
enumeration in §4 is what makes that separation auditable.

---

### R5 — UNCITED STATISTIC

**WHAT IT ASSERTS.** Every percentage, ratio, range or quantified magnitude
presented as a finding about the world carries an attribution on the same page —
either a `cited-stat` block whose `stat` contains it, or a named source in the
same sentence.

**CLAIM TEST.** Over the CLAIM SET, per page: extract every numeric-magnitude
sentence (a `%`, a `N-M` range, a `N to M` range, a `Nx` multiplier, or a
`config.magnitude_word` beside a numeral) from `TXT`, `LD` string leaves, `JS`
string literals, `META`/`OG`/`TW` and `LLMS`. For each, assert the number
appears inside some `CITED_SOURCES[key]['stat']` rendered on that page, **or**
that the sentence itself names an entry from `config.recognised_publishers`,
**or** that the sentence is marked as a visitor-input computation
(`config.computed_output_markers`).

**THE KNOWN LIVE INSTANCE — found with `/usr/bin/grep`, 2026-09-17, and it is
live right now.** The claim is `15% reduction in heating and cooling costs`. It
renders in **exactly two files on DCI, two occurrences total**, and in **zero
files on LGM and GCI**. Generator source and rendered target, both measured:

| Where | Exact rendered text |
|---|---|
| `_generate_calculator_pages.py:453` → `public/r-value-needed-calculator.html:1570` | `<p>Most homes at this level see noticeable comfort improvement and 15% reduction in heating and cooling costs from bringing this area up to code. The math typically works.</p>` |
| `_generate_calculator_pages.py:1102` → `public/do-i-need-new-insulation-quiz.html:1502` | `<p>Your home shows multiple indicators of under-insulation: pre-1990 construction, visible thin insulation, climbing bills, and/or temperature unevenness. Most homes with this profile see comfort improvement plus 15% reduction in heating and cooling costs after upgrading. The payback calculator on this site gives the number for your own home.</p>` |

Both are **inside `<script>` string literals**, assembled at runtime — the first
inside `framingFor(r)`, the `tier === 1` branch. Three facts make this the
right anchor for R5:

1. **It has no literal form in the delivered HTML outside the script.** It is a
   JS string, so a body-text instrument cannot see it. `normfind.py` on DCI
   *"reads BODY TEXT and structurally cannot see `<head>`"* — the same class.
2. **It is uncited and known to be uncited.** DCI's `dci-d3-tier-label-fix` lane
   row, 2026-09-11, states it in as many words: *"`framingFor` … Its uncited
   '15% reduction' claim is untouched here, **and its audience grew 33 → 54**;
   that is flagged to the Director separately."* The D3 fix moved 26 combinations
   from MOD into SIG, so **the number of input combinations that now render this
   uncited claim went from 33 to 54.**
3. **A related figure was removed from the embed frame for exactly this
   reason.** DCI `92f3887` D8 removed 1,131 dead bytes so *"the frame no longer
   carries 'Whole Home Efficiency Bonus', '15% reduction', or any 'Xcel'
   string"*, with the source comment stating the reason: those strings included
   *"a named utility rebate programme and **an uncited savings percentage** that
   every LLM crawler fetching the frame would read."* Confirmed 2026-09-17:
   `15% reduction` is **0** in both embed artifacts and **0** in `llms.txt`. The
   claim was recognised as uncited, removed from one surface, and left standing
   on two.

There are registry entries that would support a 15% figure —
`ENERGYSTAR_SEAL_INSULATE_15PCT` exists in all three registries — but neither
rendering names ENERGY STAR, neither is a `cited-stat`, and DCI's
`a7-cited-sources-verification.md` records that the sibling entry
`ENERGYSTAR_AIR_SEALING_15PCT` was **removed from 20 sites** because *"the
load-bearing falsehood is the word 'alone'."* So this is not a
missing-hyperlink problem; the attribution question is open.

**SURFACES.** `VIS` `TITLE` `META` `OG` `TW` `LD` `JS`(string literals)
`LOWVIS` `LLMS` `EMBED` `SVGTEXT`. `JS` string literals are mandatory — the live
instance lives nowhere else.

**NORMALIZATION.** `TXT` for prose; `RAW` + a JS string-literal extraction for
`JS`; `SRC` over the generators to catch the pre-render form. The `SRC` pass
matters because DCI's prose splits across implicit concatenation and the quiz
paragraph is built with `+` across four source lines.

**POSITIVE-CONTROL FIXTURE — `fixtures/R5_uncited_statistic.html`. The literal
live text, unmodified, cited to `_generate_calculator_pages.py:453` at DCI HEAD
`f9e7551`.**

```html
<!DOCTYPE html>
<html lang="en"><head><title>R-Value Needed Calculator — Denver</title></head><body>
<div id="calcOutput"></div>
<script>
(function () {
  'use strict';
  function framingFor(r){
    if (r.tier === 1) return '<p>Most homes at this level see noticeable comfort improvement and 15% reduction in heating and cooling costs from bringing this area up to code. The math typically works.</p>';
    return '';
  }
}());
</script>
<p>Homes built before 1990 in this climate zone lose 20-40% of their attic
R-value to wind-washing at the eaves.</p>
</body></html>
```

The second paragraph is the **negative half inside the positive fixture**:
`20-40%` as wind-washing degradation is a figure DCI's ground-truth explicitly
preserves (*"`20-40%` also survives legitimately as wind-washing R-value
degradation … Do not strip them on a literal string match"*) — but it is
*uncited in this fixture*, so R5 **must** fire on it too. R5 fires on 2 items
here; the wind-washing figure's real page carries a `cited-stat`, and
`fixtures/negative/NEG05.html` is the same sentence **with** its citation, where
R5 must stay clean. Expected control output:

```
  canary+ R5        fixtures/R5_uncited_statistic.html       DETECTED  (2: JS literal, prose)
  canary- NEG05     fixtures/negative/NEG05.html             clean
```

**AN INTERROGATIVE IS NOT A CLAIM — BUT ONLY WHERE THE PAGE MAKES THE CLAIM
SOMEWHERE ELSE, ATTRIBUTED.** Added 2026-09-19 (`f_question`). R5 asserts over
figures *presented as a finding about the world*. A question presents no
finding; it asks about one. DCI's FAQ heading

> What happens if the after test does not reach a 20% CFM50 reduction?

was adjudicated uncited on **three surfaces** (`LD`, `LOWVIS`, `VIS`) on a page
that carries, inside a `cited-stat`, *"the qualifying minimum standard for the
air sealing rebate is a 20% reduction in CFM 50"*, attributed to Xcel Energy's
residential rebate summary — same figure, same claim, same publisher, same
page. `f_instat` could not reach it, and **neither obvious loosening was
available.** Measured 2026-09-19 with the gate's own `_r5_words`/`win`/`occ`:

| pair | overlap | window | coverage |
|---|---|---|---|
| the CFM50 question vs its cited-stat | 3 | 8 | 0.375 |
| the documented false-clear pair | 3 | 13 | 0.308 |
| the seventh read's 42% counterexample | 3 | 9 | 0.333 |

Dropping `_R5_INSTAT_MIN` from 4 to 3 reopens both rows that must stay shut —
the exact widening the rule was rebuilt to stop. A **coverage** test is no way
out either: 0.375 against 0.333 is one point of separation, which is a
coincidence, not an instrument. The count is not the defect. The defect is that
a short interrogative has eight content words in total and cannot earn four of
anything, however completely it restates the sentence that sources it.

**⚠ RETRACTION, 2026-09-20 — THE PARAGRAPH THAT STOOD HERE DESCRIBED A FILTER
THE CODE DID NOT IMPLEMENT.** It said *"The question is then judged through the
sentence that actually makes the claim"*. **It was not.** As shipped in
`bfbad20`, `_anchored()` collected the **bare numeral tokens** of every cleared
non-interrogative in the same FILE and `f_question` cleared a question when
`all(n in anchors)`. **No content relation between the question and its anchor
was required at all** — the same rule's `f_instat` demanded four shared content
words in a window around the figure; `f_question` demanded **zero**. A spec that
overstates a rule is itself a defect, and this one hid a live laundering route
for a day. What follows describes the code as it stands after the 2026-09-20
rewrite, and the retracted claim is kept above rather than deleted.

**THIS IS NOT "SKIP QUESTIONS", AND THE DIFFERENCE IS THE WHOLE FILTER.** A
question can smuggle a claim — *"Did you know homes lose 40% of their heat
through the attic?"* is an assertion wearing a question mark. The filter
therefore requires an anchor meeting **four** conditions, all of them:

1. **Non-interrogative.** A sentence ending in `?` never anchors anything.
2. **Same FILE and same SURFACE.** `_anchored()` filtered on the file only, so a
   `<meta name="description">`, a JSON-LD string leaf or an inline `<script>`
   template literal could anchor a claim made in visible prose, and visible
   prose could anchor a claim buried in JSON-LD FAQ markup. The `src_code` /
   `src_dup` exclusion covers **generator SRC surfaces** only and never closed
   this.
3. **Already cleared R5 through an attribution filter** — `f_inblock` (it *is* a
   cited-stat), `f_instat` (the page's cited-stat attributes that figure) or
   `f_pub` (it names the publisher that made the claim).
4. **The same claim, not the same numeral.** The local window overlap between
   the question and the anchor, taken around that figure by the *same*
   `_r5_local_overlap` helper `f_instat` uses, must reach `_R5_INSTAT_MIN`. One
   mechanism, two callers: there is no second, weaker same-claim test any more.

And the **question itself** must be interrogative in **form**, not merely in
punctuation. *"Attic insulation cuts your heating bill by 20%, right?"* is a
flat assertion plus one character and the old `endswith("?")` test pardoned it.
`_r5_is_interrogative` requires the sentence to open with a wh-word or an
inverted auxiliary and to carry no trailing comma-tag. **That enumeration is a
NECESSARY condition, never a sufficient one, which is the whole difference from
the guard removed on 2026-09-19**: an omission here means a genuine question is
judged as an assertion and **fires**, so the list fails *shut*. Presupposition
(*"Why settle for less when our crews measure a 36% reduction…?"*) is closed by
condition 4, not by the opener list.

What it cannot hide, structurally rather than by assertion:

- No same-**surface** sentence carries the figure → no anchor → **the question
  fires.**
- A same-surface sentence carries the figure, is attributed, but makes a
  **different claim** → local overlap below the threshold → **the question
  fires.** This is the A1 hole and it is the common case.
- A companion carries the figure but is **itself uncited** → it is not in the
  cleared set, so it anchors nothing, **and R5 fires on it.** The figure is
  caught either way; it is merely caught at the sentence that asserts it.
- The other filters are deliberately **not** anchors. `src_code` and `src_dup`
  mean *judged elsewhere*, not *attributed*; `computed_output_markers` means
  *the visitor's own arithmetic*, which sources nothing; `deriv`/`code`/
  `struct`/`corr` say the figure is not a finding, which is a statement about
  **that** sentence and does not transfer. Only the three filters that assert an
  attribution EXISTS may anchor.
- An interrogative can never anchor anything, including another interrogative,
  so two questions cannot clear each other. A **tag** question is treated as an
  assertion when deciding whether it FIRES and is still refused as an anchor —
  deliberately asymmetric, and asymmetric in the only safe direction.
- **Every** figure in the hit must be anchored **by a same-claim anchor**, so a
  second, unsourced numeral cannot ride along inside the same question, and two
  unrelated publishers cannot jointly pay for one question.
- `_open()` still applies: a `KNOWN-OPEN` hit is never removed by it.

**THE `20% CFM 50` ROW IS NOT CLOSED HERE, AND A QUESTION/ANCHOR OVERLAP RULE
CANNOT CLOSE IT.** Measured 2026-09-20 with `_r5_local_overlap`, window 110:

| pair | overlap |
|---|---|
| DCI's CFM50 question vs the cited-stat that sources it | 3 |
| the documented false-clear pair (`15%` save vs `15%` reduction) | 3 |
| the seventh read's 42% counterexample | 3 |
| the eighth read's 42% **interrogative** counterexample | 3 |

At a threshold of 4 the blower-door row fires; at 3 the 42% interrogative
evasion clears. There is no value that separates them, and lowering
`_R5_INSTAT_MIN` to rescue the row would reopen the pair the threshold exists to
keep shut.

> **RETRACTION, 2026-09-20 — the paragraph that stood here was FALSE, and is
> retracted in place rather than deleted so it cannot survive as a true-looking
> statement.** It read: *"The row is therefore closed by the instrument this
> document already declares for it — `R3.allowed_thresholds` … DCI's
> `allowed_thresholds` was empty, so that declared exclusion silently did not
> exist there … It now carries `["20%", "20 percent"]`."*
>
> The table above is right; **the conclusion drawn from it was not.** Measured
> on DCI at `31c98be`, live corpus, R5 RAW **622** in both states:
>
> | `R3.allowed_thresholds` | `f_struct` | `f_question` | R5 ADJUDICATED |
> |---|---|---|---|
> | `["20%","20 percent"]` | matched 222, removed **6** | matched 4, removed **0** | 0 |
> | `[]` | matched 0, removed 0 | matched 4, removed **3** | 3 |
>
> **`f_question` removes all three blower-door FAQ rows by itself.** It matched
> them in the populated state too and removed nothing only because `f_struct`
> sits earlier in the filter chain. The exclusion was never load-bearing for the
> case it was justified by.
>
> What it *was* load-bearing for is three rows — one string, one page, three
> surfaces: the page title `Denver Blower Door Test - CFM50, Xcel's 20% Rebate
> Rule` on locators `(title)`, `(og:title)` and `(twitter:title)`. Those are now
> closed by **`f_title_np`** (§ *The page title names the publisher's own
> artifact*, below).
>
> And it opened **ten** evasions: with the list populated, one uncited
> first-party performance claim per `threshold_context_marker` — *"Our crews
> deliver a 20% CFM 50 reduction on every air sealing job"* and nine siblings —
> all CLEARED; with it empty all ten FIRE. An eleventh, *"a 10-20% CFM 50
> reduction"*, cleared through the substring hole the entry's own note
> predicted. **DCI's `R3.allowed_thresholds` is now `[]` and must stay `[]`.**
> The same hole was still OPEN on LGM and GCI — same probe, GCI clears **14 of
> 16**, LGM clears **12 of 16** at its own 25% tier figure.

> **CLOSED 2026-09-20, later the same day, on LGM and GCI, by a veto rather
> than by the DCI-shaped fix.** The sentence that stood here — *"and is recorded
> rather than closed, because closing it means adjudicating live findings on two
> properties another row is editing"* — is superseded and is replaced in place
> rather than deleted. See § *`f_struct` — the first-party veto*, below, for the
> measurement, including why emptying the figure lists (the DCI shape) does
> **not** transfer to these two properties.

---

#### `f_struct` — a threshold context is necessary and is **not** sufficient

**FILTER.** *"allowed structure percentage / tier threshold IN a threshold
context."* As shipped it cleared a quantified claim on two tests, both
**substring**, both **sentence-scoped**, both **unbound to the figure's
position** — and, the defect, both unbound to the figure's **subject**:

1. the sentence contains some entry of `R3.allowed_structure_percentages` +
   `R3.allowed_thresholds`, and
2. the sentence contains some entry of `R3.threshold_context_markers`.

**Nothing in it ever asked whose figure it is.** So it reasoned: the sentence is
about a leakage-reduction threshold, therefore the number is a threshold,
therefore no publisher is owed — *even when the number is the contractor's own
promised result*. It licensed uncited **first-party performance claims**, which
is precisely the class these properties are most likely to get wrong.

**MEASURED 2026-09-20**, one uncited first-party performance claim per
`threshold_context_marker`, run through the gate's own `_control_ctx` with
`ctx.repo = CONTROL_NO_REPO` so no property tree is reachable:

| property | probes cleared | at figure | carried by |
|---|---|---|---|
| DCI | 0 of 16 | `20%` | list already `[]` (`a5baa0f`) |
| LGM | **12 of 16** | `25%` | `tier` / `of project cost` / `capped at` |
| GCI | **14 of 16** | `20%` | the bare words **`reduction`** and **`leakage`** |

GCI's row is the sharpest evidence in this section: its
`threshold_context_markers` include the bare words `reduction` and `leakage` —
that property's own subject matter, not threshold vocabulary — so **the gate's
own control sentence `R5n`, *"Our crews deliver a 20% reduction in winter
heating costs"*, cleared on live GCI.** A control the gate ships to prove it can
see a defect did not fire on one of the properties it guards. See the correction
to `R5_THRESH_CONTROL_OVERLAY` below.

**THE FIX IS A VETO: `R3.first_party_subject_markers`.** `f_struct` is a
*clearing* filter, so a test added to it can only **add** hits, never remove
them. An over-broad veto reddens a page and gets adjudicated; an over-narrow one
leaves the hole open — so erring broad is the fail-safe error, and the veto is
deliberately **sentence-scoped, with no proximity window and no verb
requirement**. A sentence that says *we* or *our* anywhere while asserting a
magnitude is a sentence R5 makes prove its attribution. Matching is
**word-bounded and must stay so**: as substrings `us` matches *because*, `our`
matches *your* / *hour* / *favour*, and `we` matches *power*, which would turn
the narrowing into a blanket kill of `f_struct`.

**It is not an allowlist in a narrower costume.** An allowlist adds clearances;
this subtracts them. It cannot hide a hit and cannot be satisfied by naming
anything. It has **no per-property entries**: the key lives in `common.json`
**only**, so all three properties are judged by the identical list — deliberate,
because `_deep_merge` *replaces* lists rather than unioning them, so a
per-property override would read as additive and be silently subtractive.

**THREE NARROWINGS MEASURED AND REJECTED**, against all **76** live rows
`f_struct` currently clears (LGM 29, GCI 47) — so this is the cut the corpus
supports, not the cut that was convenient:

| candidate | LGM live rows reddened | GCI live rows reddened |
|---|---|---|
| empty both figure lists (**the DCI-shaped fix**) | 29 | 47 |
| a marker within 60 chars of **every** numeral | 21 | 2 |
| every numeral **inside** an allowed-entry span (the `f_title_np` shape) | 8 | 0 |
| **this veto** — `we` `our` `us` `ours` `we're` `we've` | **0** | **0** |
| the same veto plus `you` / `your` / `you're` | 2 | — |

**The DCI shape does not transfer.** On DCI the figure list was load-bearing for
**three** rows (one page title on three surfaces, now closed by `f_title_np`).
On LGM and GCI it is load-bearing for **76** rows of *third-party program-rule*
copy — Atmos Energy's and Efficiency Works' own payout structures and qualifying
conditions, e.g. *"Efficiency Works pays a tiered flat incentive for air sealing
based on measured reduction of air loss from a blower door test, with four tiers
set at more than 15%, more than 25%, more than 33%, and more than 50%"* and
*"Air sealing is a separate measure and requires a blower door test showing at
least a 20% reduction in leakage."* Emptying the lists would redden both
properties with copy that is correct. **Not one** of those 76 rows contains a
first-party subject marker; **all** of the 26 live evasions do.

> **RE-MEASURED 2026-09-20 BY ROW K, POST-VETO, AND THE FIGURES HOLD.** The
> `29 / 47` row above was taken before the veto landed, so it was treated as
> possibly stale and was re-run rather than inherited. It is not stale. LGM at
> `ce51cfa` and GCI at `1bc625c`, live corpora, R5 `RAW 228` / `RAW 204`
> unchanged in every state:
>
> | state | LGM `f_struct` | LGM R5 ADJ | GCI `f_struct` | GCI R5 ADJ |
> |---|---|---|---|---|
> | as shipped | matched 47, removed **29** | **0** (exit 0) | matched 119, removed **47** | **0** (exit 0) |
> | only `allowed_thresholds` emptied | matched 13, removed 8 | **21** (exit 1) | matched 34, removed 20 | **27** (exit 1) |
> | **both** figure lists emptied (the DCI shape) | matched 0, removed 0 | **29** (exit 1) | matched 0, removed 0 | **47** (exit 1) |
>
> The veto changes none of these counts, because it vetoes none of the 76 rows
> — which is the measurement the veto was chosen on, now confirmed against the
> live corpora rather than against probes.
>
> **Splitting the 76 by which list carries it** is new, and it is what the
> retract-or-keep question actually turns on. `allowed_thresholds` alone carries
> **21** on LGM and **27** on GCI; `allowed_structure_percentages` carries the
> remaining 8 and 20. And the 21 are not 21 independent claims: they are **one
> string family on 21 locators across 18 pages**, the
> `EFFICIENCY_WORKS_AIR_SEALING` cited-stat block at
> `_shared_components.py:2245`, which ships its own `source=` (Efficiency Works,
> a Platte River Power Authority program) and its own first-party `url=`
> (`efficiencyworks.org`'s incentive PDF). R5 adjudicates the cited-stat block
> *itself* as an uncited magnitude claim. GCI's 27 are the Atmos Energy CFM(50)
> and CFM(25) blower-door qualifying conditions across 9 artifacts.
>
> **So both entries are retained, and retained by measurement rather than by
> inconvenience.** The DCI entry was retracted because it was load-bearing for
> three page-title rows that a mechanism with no per-property configuration
> could close. Nothing of that shape is available here: what these two carry is
> correct, first-party-sourced, third-party program copy, and no narrower
> predicate was invented to protect it — inventing one would be the widened
> filter this spec forbids.



**EFFECT.** LGM probes `4 → 14` of 16 adjudicated; GCI `2 → 14`. The two that
still clear on each are the genuine third-party threshold statement *"The
qualifying minimum standard for the air sealing rebate is a 20% reduction in CFM
50"* and the interrogative that asks about it — `f_struct` doing its job. Live
R5 is unchanged at `ADJUDICATED 0` on all three (DCI `RAW 622`, LGM `RAW 228`,
GCI `RAW 204`), and the `f_struct` filter row still reads `removed 29` on LGM
and `removed 47` on GCI.

**WHAT IT CANNOT DO — stated, not asserted away.** It reads a **pronoun**, not a
subject: a first-party claim that avoids *we* and *our* entirely — *"a typical
job here produces a 20% cut in heating costs"* — still clears. It carries no
brand names, so a property naming **itself** in the third person is not vetoed.
And both original tests remain sentence-scoped substring tests; the two
proximity-bound alternatives that would close that are recorded above as
rejected **by measurement**, so a later row need not re-derive them.

**CONTROL — `R5-STRUCT-FP`**, `R5p_struct_first_party.html` /
`repaired/R5p_struct_first_party.html`, `expect=11`. Non-repaired: eleven
uncited first-party performance claims, one per marker family, each carrying a
configured figure and a marker. Measured at `3ccf154`, before the veto: **`RAW
11 ADJUDICATED 0`** — the hole. **`RAW 11 ADJUDICATED 11`** after. Repaired: five
third-party program-structure and qualifying-condition statements carrying the
**same** figures and the **same** markers — `RAW 5 ADJUDICATED 0` before *and*
after, and **not vacuously clean**, because `reduction` and `leakage` are both
R5 `magnitude_words`, so all five are genuine RAW hits and the clearance is
credited to `f_struct` rather than to the absence of a hit. The pair cannot be
satisfied by switching `f_struct` off (the repaired half reddens), nor by
leaving the veto out (the other half reddens), nor by making the veto a
substring match (`us` in *because* reddens the repaired half too).

**CONTROLS — six, both directions each.**

| control | fixture | before 2026-09-20 | after |
|---|---|---|---|
| `R5-QUESTION` | `R5j_interrogative_anchor.html` | 3 hits | 3 hits |
| `R5-QLAUNDER` | `R5k_question_numeral_laundering.html` | **0 hits** | **7 hits** |
| `R5-QTAG` | `R5l_tag_question.html` | **0 hits** | **3 hits** |
| `R5-QSURFACE` | `R5m_cross_surface_anchor.html` | **0 hits** | **2 hits** |
| `R5-THRESHOLD` | `R5n_threshold_exclusion.html` | 2 hits | 2 hits |
| `R5-TITLENP` | `R5o_title_possessive_attribution.html` | 7 hits | 7 hits |
| `R5-TITLENP` *(repaired half)* | `repaired/R5o_title_possessive_attribution.html` | **3 hits — FIRES ON REPAIRED** | **0 hits** |
| `R5-STRUCT-FP` | `R5p_struct_first_party.html` | **0 hits — the `f_struct` first-party hole** | **11 hits** |
| `R5-STRUCT-FP` *(repaired half)* | `repaired/R5p_struct_first_party.html` | 0 hits | 0 hits |

Every `0 hits` above was **measured against `claim_gate.py` at `bfbad20` on all
three property configs** before the code was touched, not asserted. `R5k` holds
seven attributed statistics beside seven uncited questions sharing **only a
numeral** — including this document's own named adversary, *"Did you know homes
lose 40% of their heat through the attic?"* beside an unrelated attributed
ENERGY STAR 40%, which this section says *"must keep firing"* and which did
**not**. Each fixture has a repaired counterpart that must be clean, so none of
the five can be satisfied by weakening or deleting `f_question`: doing that
reddens the repaired half.

`R5j`'s repaired half was **itself part of the defect** and is rewritten. It
paired an ENERGY STAR statistic about *annual space-conditioning energy use*
with a question about *winter heating costs* — different claims — and
`bfbad20`'s own commit message recorded that pair's local overlap as **0**. The
pass measured the hole and filed it as proof the control exercised the filter.
Its anchors now state the claim their questions ask about, and are attributed
**prose** rather than `cited-stat` blocks on purpose: a `cited-stat` would set
`r5_instat` and let `f_instat` clear the question, and the control would stop
testing `f_question`. Measured: every repaired clear in `R5j`, `R5k`, `R5l` and
`R5m` is credited to the `f_question` filter row.

`R5-THRESHOLD` is new for a second reason: **`f_struct` had no control on any
property**, because `R5_CONTROL_OVERLAY` empties both lists it reads on every R5
control. Its fixture carries `20%` / `20 percent` as ordinary marketing claims
with no threshold context and MUST fire even with the list pinned — that is what
stops the entry becoming an allowlist for a number — and its repaired half is
the unattributed qualifying-threshold statement plus the blower-door
interrogative, which MUST clear on the threshold context alone.

Measured effect on the live corpus, 2026-09-20, DCI `public/` md5-attested
identical across both runs: DCI R5 `RAW 622 ADJ 3 → RAW 622 ADJ 0` (`f_question`
row `4 (removed 3)` → `4 (removed 0)`; `f_struct` row `0 (removed 0)` →
`222 (removed 6)`, all six on `insulation-blower-door-test.html`); LGM
`RAW 228 ADJ 0`, GCI `RAW 204 ADJ 0`, both unchanged and both exit 0; controls
**48 positive DETECTED / 0 MISSED · 17 negative clean / 0 FALSE ALARM** and
48 repaired-clean on all three properties. On the earlier snapshot of the same
day one DCI sentence carrying `20%` but **no** threshold-context marker —
*"…a minimum 20% reduction in air leakage must be achieved"* — **still fired**.

> **CORRECTED 2026-09-20, later the same day.** That last sentence was offered
> as *"the in-corpus proof that the config entry is context-scoped rather than a
> figure allowlist."* It proves the weaker thing only: that the entry requires a
> context marker. It does **not** prove the marker requirement is sufficient,
> and it is not. Nine markers are in the list and every one of them is the
> property's own subject matter, so *"Our crews deliver a 20% **CFM** 50
> **reduction** on every air sealing job"* — an uncited first-party performance
> claim — cleared. Ten such probes cleared. The DCI entry is now `[]` and this
> paragraph's `f_struct` row for DCI reads `0 (removed 0)` again.

> **AND THE CONTROL OVERLAY WAS PINNED TO HIDE THAT, 2026-09-20.**
> `R5_THRESH_CONTROL_OVERLAY` pinned `threshold_context_markers` to
> `common.json`'s **narrower nine**, on the stated ground that GCI's list
> *"includes the bare word `reduction`, so without pinning, the fixture's `20%
> reduction in winter heating costs` would clear on GCI and the control would
> MISS on exactly one property."* **That reasoning had the polarity backwards.**
> It made the control pass by measuring a marker list **no property runs**, and
> so hid a real live miss behind a green control. A control must be at least as
> hard as the hardest config it guards, so the overlay now pins the portfolio's
> **worst case** — GCI's live sixteen markers, bare `reduction` and `leakage`
> included. `R5n` fires under that list, and it fires because of the
> first-party veto rather than because the marker list was chosen to let it.

---

#### `f_title_np` — the page title names the publisher's own artifact

**FILTER.** *"the PAGE TITLE names the publisher's own artifact and EVERY figure
in it sits INSIDE that possessed noun phrase."* Added 2026-09-20 as the
cause-level replacement for DCI's `R3.allowed_thresholds` entry. **No
per-property configuration; it adds no config key at all.** It reads only
vocabularies R5 already had: `recognised_publishers`, `publisher_short_forms`,
`publisher_artifact_nouns`.

**THE DEFECT IT FIXES.** `_pub_subject`'s two attribution routes, S1 and S2,
both end in an **attribution verb**. That requirement is right and stays — it is
what stops *"ENERGY STAR's **critics** say our 43% savings number is invented"*
reading as an ENERGY STAR attribution. But it left R5 unable to read an
attribution that has **no predicate at all**, and a page title is exactly that:
a name, not a sentence. DCI's

```
Denver Blower Door Test - CFM50, Xcel's 20% Rebate Rule
                                 ^^^^^^^ registered publisher_short_forms entry
                                         ^^^ the figure
                                             ^^^^^^^^^^^ registered
                                                         publisher_artifact_noun
```

is built **entirely** out of vocabulary the gate already recognises. Only the
verb was missing, and a title has nowhere to put one. Three rows were
adjudicated uncited for want of a word the surface cannot carry.

**WHY IT IS THE TIGHTEST OF THE THREE ROUTES, NOT THE LOOSEST.** S1 and S2 let
the figure sit in a complement reached *across* a verb, up to `_R5_SUBJ_REACH`
= 120 characters away. S3 requires the figure to sit **inside** the possessed
noun phrase, between the possessive marker and the head noun — distance zero.
`_R5_NP`'s token class cannot cross a `%`; `_R5_NP_FIG` is a **separate**
constant so that adding S3 cannot loosen S1 or S2 by one character.

**WHAT IT CANNOT HIDE — structurally, not by assertion.**
- **Every occurrence of every figure** in the hit must be inside a
  possessed-artifact span. One free occurrence anywhere else in the title and
  the row fires. That is strictly stronger than `f_pub`, which clears a numeral
  once *any* of its occurrences is attributed, and it is what stops
  *"Xcel's 20% Rebate Rule - We Cut 20% Off Your Bill"*.
- The figure must lie **between** the possessive and the head noun.
  *"Xcel's Rebate Rule - Our Crews Deliver 20% CFM 50 Reduction"* fires.
- **The possessive is mandatory**, for full publishers as well as short forms.
  *"Xcel 20% Rebate Rule Reduction"* fires: the bare token is the **payer**, not
  a publisher — the seventh adversarial read's ruling, honoured here.
- The head noun must be a `publisher_artifact_nouns` entry — something an
  organisation issues and can be quoted from. *"Xcel's 20% Reduction Promise"*
  fires.
- **Locator-bound, not surface-bound.** Only `(title)`, `(og:title)`,
  `(twitter:title)`. Surface `OG` also carries `og:description` and surface `TW`
  also carries `twitter:description`; binding to the surface would hand the same
  clearance to two prose descriptions per page for nothing. The same noun phrase
  in visible prose, in a `meta[description]`, in an `og:description` or in a
  `twitter:description` **fires** — prose can carry the predicate, so prose is
  held to one. That cost is stated, not hidden.
- A denial inside the noun phrase voids it (`_R5_DENIAL`).
- `_open()` still applies: a `KNOWN-OPEN` hit is never removed.
- **It is not an anchor for `f_question`.** `_anchor_sents` still admits only
  `f_inblock`, `f_instat` and `f_pub`. A title is not a place from which a
  question elsewhere on the page may draw its attribution, and widening
  `f_question` by a side door is the one thing this filter must not do.

**WHAT IT CANNOT DO AT ALL.** It inherits R5's standing blind spot: it asserts
an attribution EXISTS and never reads the source. *"ENERGY STAR's 40% Attic Loss
Data"* in a title clears whether or not ENERGY STAR published such a figure —
exactly as *"ENERGY STAR's attic guidance states 40%"* already clears through
`f_pub`. R7 and R11, not R5, are where a wrong figure is caught.

**CONTROL `R5-TITLENP`**, `R5o_title_possessive_attribution.html`, overlay
`R5_CONTROL_OVERLAY` (both R3 figure lists emptied, so nothing clears through
`f_struct`), `expect=7`. The non-repaired half holds **seven** laundering routes
a title-scoped clearance must not open — figure outside the noun phrase, bare
non-possessive publisher, non-artifact head noun, `og:description`,
`twitter:description`, `meta[description]`, visible prose. Measured at `d064ccf`
**before** the filter: `RAW 7 / ADJUDICATED 7`; after: `RAW 7 / ADJUDICATED 7`.
The repaired half is the page title on its three surfaces: measured at `d064ccf`
**`RAW 3 / *** FIRES ON REPAIRED *** 3`** — that was the hole — and
`RAW 3 / ADJUDICATED 0` after, all three removals credited to the `f_title_np`
row. The repaired half is **not vacuously clean**: its rows are genuine RAW hits
(`20%` plus the magnitude word `lower`, matched as a substring inside `Blower`).
The pair cannot be satisfied by switching the filter off — the repaired half
reddens — nor by widening it into a blanket title skip — the other half reddens.

**RECORDED, NOT FIXED: an R5 RAW-stage substring characteristic.** Those three
title rows are raw hits only because `has_any(sentence, magnitude_words,
word=False)` is a substring test and `"lower"` ⊂ `"Blower"`. Same class:
`"lose"` ⊂ `"closely"`, `"lower"` ⊂ `"follower"`. Switching to `word=True` is a
RAW-stage narrowing across all three properties that would silence real
inflections; it is a blindfold risk needing its own measured pass, and it was
**not** taken here.

**WHAT IT DELIBERATELY DOES NOT CATCH.**
- **Whether the citation supports the figure.** DCI's live audit found **15 of 18
  entries deviated, all 15 in the site's favour** — an attributed figure can be
  wrong. R5 asserts attribution exists, R1 asserts the quotation has provenance,
  and neither reads the source.
- **Calculator outputs computed from visitor input.** Ruling 4. A rendered
  `pctShort` percentage is the visitor's own arithmetic, not a finding.
- **R-values, IECC targets, ENERGY STAR recommendations, structure percentages,
  and the `20% CFM 50` threshold** — same exclusion set as R3, same classifier.
- **A figure that is attributed *near* rather than *in* the same sentence.** The
  gate scopes attribution to the sentence and the page, and will call a
  correctly-sourced figure uncited when the attribution sits two paragraphs away.
  That is a deliberate strictness, and every such hit is enumerated under
  `FILTER` for adjudication rather than silently dropped.
- **A qualitative magnitude claim with no numeral.** *"far more moisture into an
  assembly than vapor diffusion does"* was an invented magnitude (DCI
  `a7-cited-sources-verification.md`) and R5 cannot see it. R1 Half B can, only
  because it is inside quote marks.
- **Attribution debt at scale.** DCI measured it and it is R11, report-only.

**PER-PROPERTY CONFIG.**

```json
"R5": {
  "magnitude_patterns": ["[0-9]{1,3}\\s?%", "[0-9]+\\s?-\\s?[0-9]+\\s?%",
                         "[0-9]+ to [0-9]+ percent", "[0-9](\\.[0-9])?x",
                         "[0-9]+ times"],
  "magnitude_words": ["reduction","savings","saves","lower","cut","increase",
                      "improvement","payback","efficiency","loss","leakage"],
  "recognised_publishers": ["ENERGY STAR","Building Science Corporation",
                            "Colorado Energy Office","EPA","CDPHE",
                            "Building America Solution Center","ACCA",
                            "Xcel Energy","Atmos Energy","Efficiency Works",
                            "Boulder County EnergySmart","NOAA",
                            "Energy Outreach Colorado"],
  "computed_output_markers": ["your own home","based on your inputs",
                              "you entered","estimates to roughly",
                              "short of target","for your"],
  "known_uncited": [
    { "text": "15% reduction in heating and cooling costs",
      "files": ["public/r-value-needed-calculator.html",
                "public/do-i-need-new-insulation-quiz.html"],
      "generator": "_generate_calculator_pages.py:453,1102",
      "status": "OPEN — flagged to the Director 2026-09-11 in lane dci-d3-tier-label-fix",
      "audience": "grew 33 -> 54 input combinations after 37c7b29" }
  ]
}
```

`known_uncited` does **not** suppress the finding. It carries the provenance so
the gate can print `KNOWN-OPEN` beside the hit instead of a fresh FAIL, and the
count is still reported. A silenced hit would be exactly the *"filter silently
dropped a real hit"* failure §4 exists to prevent.

**EXPECTED FALSE-POSITIVE PRESSURE.** The highest of any rule, because the
portfolio is dense with legitimately-cited figures: DCI renders **178**
`cited-stat` blocks, LGM **120**, GCI **108**. Plus: R-values everywhere
(`R-13`, `R-20`, `R-49`, `R-60`, `R-19`, `R-30`), `3.5 R per inch`, `6.5 R per
inch`, `2-3x premium`, `30-to-40-degree day-night swings`, `50 pascals`,
`20% CFM50`, `75%`/`50%` Atmos structure rates, LGM's four air-sealing tier
thresholds (`15%`/`25%`/`33%`/`50%`), `61% of the city` (the LPC coverage
figure), `roughly 3.5 pounds per cubic foot`, elevation figures (`5,280`,
`4,980`, `4,108`), and `60% of state median income` / `80% of area median
income` / `200% of the federal poverty level` in GCI's WAP prose.

---

### R6 — SELF-CONTRADICTING OUTPUT

**WHAT IT ASSERTS.** Wherever a tool prints a categorical label beside a
computed figure, the label is a monotone function of **that same figure** — the
quantity the branch tests is the quantity the sentence prints.

**GENERALISED, NOT HARDCODED.** The instance is DCI's r-value calculator, fixed
2026-09-11 in `37c7b29` (lane `dci-d3-tier-label-fix`, released `f9e7551`). The
defect, from the source comment that now sits at
`_generate_calculator_pages.py:382-400` and which I read at HEAD:

> *"the two tests below read `pctShort`, NOT `gap`. They used to read the
> ABSOLUTE gap (20 and 8 R-points) while the headline printed the PERCENTAGE, so
> on the three low-target areas the label and the figure next to it contradicted
> each other. wall-existing (R-13), crawl-encap (R-15) and basement (R-15) all
> target under 20, so a COMPLETE ABSENCE of insulation still produced a small
> absolute gap: **15 of the 140 selectable combinations printed '100% short of
> target' — estimated R-0, nothing there at all — beneath the headline
> 'Moderately under code.'** Branching on the same quantity the sentence prints
> is what makes the label and the figure unable to disagree."*

Measured by that pass: **2 ambiguous percentages (37% and 100%) received two
different severity words; 351 ordinal inversions across 4,465 label pairs; 43
label-vs-figure mismatches.** After the fix: **all three measures 0**, histogram
`45/54/31/10`, and `15 → 0` R-0 rows below most-severe.

**The general form, which is what the rule encodes — three assertions:**

- **G1 — BRANCH/PRINT IDENTITY (static, blocking, fast).** For every
  label-emitting conditional chain, the set of variables read in the branch
  conditions must equal the set of variables interpolated into the labelled
  string. `gap >= 20` branching while `pctShort` prints is a FAIL by structure,
  with no rendering needed.
- **G2 — MONOTONICITY (static, blocking, fast).** The branch thresholds on the
  printed quantity must be monotone and must order consistently with
  `config.severity_order`. Comparators must be consistent; the boundary
  inclusivity must be declared. DCI's is declared in source: *"`>=` and not `>`
  at 50 on purpose — attic/1980-2010/unknown lands on exactly 50% short, which
  reads as Significantly, not as Moderately."*
- **G3 — CROSS-PRODUCT UNIQUENESS (dynamic, OPT-IN as R6b). NOT IMPLEMENTED —
  this paragraph is a SPECIFICATION of a rule that does not exist in
  `claim_gate.py`, not a description of one that does. See §6's correction of
  2026-09-21.** Enumerate every
  reachable input combination, collect `(printed_figure, label)` pairs, and
  assert: no figure maps to two labels; no ordinal inversion across all pairs;
  every combination produces a label; no maximal-severity input lands below
  maximal severity.

**CLAIM TEST.** G1/G2 are genuine structural claim tests over `SRC` — no string
list. They generalise to any tool in the portfolio: the config names each
`(file, function, label_strings, printed_var)` triple and the gate discovers the
conditional chain by `ast`-walking the Python that emits the JS, then by a
brace-matched scan of the emitted JS.

**Why G3 must be dynamic, stated plainly, from the lane's own method
correction:** *"these headlines are assembled at runtime as `'Moderately under
code — ' + pctShort + '% short of target.'`, so **no** `<label> — <N>% short of
target.` sentence exists as a literal byte sequence in ANY version of these
pages — confirmed by finding **0** such matches on the pre-change tree as well.
**A byte search returns 0 whether or not the bug is present, so the check as
specified is vacuous.** The discriminating instrument is the browser."* Driven
through the DOM, the pre-change tree rendered `Moderately under code — 100%
short of target.` **15 times** and `Close to code — 47% short of target.`
**twice**; live renders each **0** times.

**SURFACES.** `JS` (source of the branch), `SRC` (the generator that emits it),
and — **in R6b's specification only, which is unimplemented (§6), so this
surface is read by nothing today** — the rendered DOM of both the full page and
`EMBED`. Both surfaces were specified for R6b because **DCI's calculator core is spliced into two
surfaces** and Ruling 6 for that pass was precisely that the thresholds and
headlines stay single-source *"because those are the things that could actually
drift between the two surfaces."* The D3 pass verified all 140 combinations
**on both**, identical.

**NORMALIZATION.** `SRC` and `RAW`. Not `TXT` — the branch lives in a script
body that `TXT` deletes.

**POSITIVE-CONTROL FIXTURE — `fixtures/R6_label_figure_contradiction.js`. The
pre-`37c7b29` branch, reconstructed from the surviving source comment's own
description of what the two lines were (`gap >= 20` / `gap >= 8`, now **0
occurrences** in source and in both built surfaces, against `pctShort >= 50` /
`pctShort >= 20`, now **1 each**).**

```javascript
var currentR = estimateCurrentR(area, current, era);
var gap = Math.max(0, t.targetMin - currentR);
var pctShort = currentR > 0 ? Math.round((gap / t.targetMin) * 100) : 100;
var headline, tier;
if (gap === 0) {
  tier = 0;
  headline = 'You\'re already at or above code target.';
} else if (gap >= 20) {
  tier = 1;
  headline = 'Significantly under code — ' + pctShort + '% short of target.';
} else if (gap >= 8) {
  tier = 2;
  headline = 'Moderately under code — ' + pctShort + '% short of target.';
} else {
  tier = 3;
  headline = 'Close to code — ' + pctShort + '% short of target.';
}
```

G1 must fire: branch reads `{gap}`, string interpolates `{pctShort}`. G2 must
fire on the same file with `TARGETS` supplied from config
(`wall-existing` R-13, `crawl-encap` R-15, `basement` R-15 all target under 20,
so `gap >= 20` is unreachable for them while `pctShort` can reach 100).
Expected control output:

```
  canary+ R6a-G1    fixtures/R6_label_figure_contradiction.js   DETECTED  (branch {gap} != printed {pctShort})
  canary+ R6a-G2    fixtures/R6_label_figure_contradiction.js   DETECTED  (3 areas: tier-1 threshold unreachable)
```

**THE R6b LINE THAT USED TO APPEAR HERE WAS A WORKED SAMPLE OF OUTPUT THE GATE
HAS NEVER PRODUCED.** Removed as a *sample*, quoted here as a *correction*.
This section previously read *"R6b, when enabled, must reproduce **15**
`Moderately under code — 100% short of target.` renders"* and showed a third
expected control row, verbatim:

```
  canary+ R6b-G3    (opt-in)                                    DETECTED  (15 same-figure-two-label renders)
```

No run of `claim_gate.py` has ever emitted that row, at any SHA. There is no
`Control("R6b-G3", …)` in `RULES` and no code that could produce a `DETECTED`
verdict for it; with `--opt-in=R6b` the gate prints one `canary=` disclosure
line and nothing else (§6). The "15 renders" figure is real — it was measured by
DCI's `dci-d3-tier-label-fix` lane harness — but it was never measured by this
gate, and printing it as this gate's expected output made an unwritten rule look
like a tested one. Corrected 2026-09-21.

**WHAT IT DELIBERATELY DOES NOT CATCH.**
- **Whether the thresholds are the right thresholds.** The D3 pass's own
  justification for branching on `pctShort` is that *"it asserts nothing beyond
  restating the visitor's own percentage"* — a defensible choice, not a derived
  one. The gate asserts internal consistency, never calibration.
- **A wrong target value.** `TARGETS`, `estimateCurrentR`, and every R-value in
  them were explicitly **not owned** by the D3 lane and are not owned here. Four
  defects in that table remain open and untouched by design: the `wall-new`
  target names one compliant path (`R-20 cavity + R-5 continuous`) where the
  prose names three; `wall-existing` frames a market observation as what code
  *"calls for"*; `targetRec` is dead (7 definitions, 0 reads, in the generator
  and in the live page); three `<label>`s lack `for`.
- **Two tools disagreeing with each other.** That is R9.
- **Non-monotone labels that are correct by design.** A label keyed on a
  categorical input rather than a magnitude (an area type, an era) is not a
  severity label; the config enumerates which chains are in scope, and a chain
  not enumerated is reported as `UNREGISTERED LABEL CHAIN` rather than silently
  skipped.
- **R6a cannot enumerate the cross-product.** Printed in its own `blind spot`
  field, every run.

**PER-PROPERTY CONFIG.**

```json
"R6": {
  "label_chains": [
    { "id": "dci-rvalue-tier",
      "generator": "_generate_calculator_pages.py",
      "js_block": "RVALUE_CORE_JS",
      "printed_var": "pctShort",
      "labels": ["You're already at or above code target.",
                 "Significantly under code",
                 "Moderately under code",
                 "Close to code"],
      "severity_order": ["Close to code","Moderately under code",
                         "Significantly under code"],
      "at_target_label": "You're already at or above code target.",
      "boundary_inclusivity": { "50": ">=", "20": ">=" },
      "surfaces": ["public/r-value-needed-calculator.html",
                   "public/r-value-needed-calculator-embed.html"],
      "r6b_note": "THE THREE r6b_* KEYS BELOW CONFIGURE A RULE THAT DOES NOT EXIST … (full text in config/dci.json)",
      "r6b_inputs": { "area": 7, "era": 4, "current": 5 },
      "r6b_expected_combinations": 140,
      "r6b_expected_histogram": [45, 54, 31, 10] }
  ],
  "opt_in": ["R6b"]
}
```

**NOTE, 2026-09-21: the three `r6b_*` keys above configure a rule that does not
exist** (§6). Nothing reads `r6b_inputs`, nothing drives 140 combinations and
nothing compares the histogram; those figures were measured by DCI's
`dci-d3-tier-label-fix` lane harness, never by this gate. They are kept as the
specification a future R6b must satisfy and are now labelled in `dci.json` with
an `r6b_note` so a cold reader cannot mistake them for live configuration. They
are also invisible to the gate's own dead-config audit, because their parent
`tools` is in `claim_gate.py`'s `DATA` tuple — the same inertness class that let
`lgm.json`'s `draft_gate` carry a false corpus assertion unchecked (§10.3).

**EXPECTED FALSE-POSITIVE PRESSURE.** Low for G1/G2 — they are structural. G1's
real pressure is a helper that legitimately derives the printed value from the
branch variable one step away (`gap === 0` is the at-code test and **`gap` is
not dead**: the source comment says so explicitly, and `gap: gap` is still
returned to both surfaces). The gate must treat `gap === 0` in the at-target
branch as compliant, which the config's `at_target_label` encodes. G3's pressure
is floating-point and rounding: `Math.round` makes two different `gap`s share a
`pctShort`, which is the intended behaviour once the branch reads `pctShort` —
the five `SIG → MOD` reclassifications the fix produced were **corrections, not
regressions**, all five at 37% short, *"which is exactly what the 8 non-attic
rows already at 37% were saying."*

---

### R7 — SUPERSEDED-SOURCE CLAIM

**WHAT IT ASSERTS.** No artifact cites, links to, names, or asserts a
proposition sourced to a document the property's own record marks superseded —
**and the assertion holds when the page contains no identifier for that
document.**

**CLAIM TEST for the proposition half; STRING LIST for the identifier half, and
the split is the whole point of this rule.** The governing lesson is GCI
`44d638c`'s, recorded as a standing entry in `STATE_OF_PROJECT.md`: **"this
shipped and survived every automated check because it carried no print-code
literal — a citation sweep must search for the CLAIM, not only for the
identifier."** The census that missed it *"searched for the identifier
`24-02-205` and the defect carried no print-code literal — it stated the
proposition in prose."*

- **Half A — IDENTIFIER (STRING LIST, blocking).** Every
  `config.superseded_identifiers` literal and every
  `config.superseded_urls` host+path fragment, over `RAW` and `ATTR`
  (`href` especially). Suppressed only where a `correction_marker` is in scope.
- **Half B — PROPOSITION (CLAIM TEST, blocking).** Every
  `config.superseded_propositions` entry is a `{claim_id, any_of[], all_of[],
  polarity}` predicate over sentence-split `TXT` plus `LD` leaves plus `JS`
  string literals. This is the half that catches a retired rule stated in the
  site's own words.

**RETRACTION, 2026-09-20 (row A4) — what "the current CO sheet †" means below.**
Every "`25-12-215`" that used to appear in this section has been replaced by
**the current CO sheet †**. The document number `25-12-215` is **withdrawn**:
it could not be retrieved from **any** first-party Xcel source. The retrieval,
2026-09-20, all with a browser User-Agent and the load-bearing probes repeated
with a Googlebot User-Agent: **32** direct URL probes under
`www.xcelenergy.com/staticfiles/` across the six directories Xcel actually uses
for this sheet (`Marketing/`, `Programs and Rebates/Residential/`,
`Energy Solutions/Residential Solutions/`, `Working With Us/`,
`Working With Us/Trade Partners/`, and the `xe-responsive` root). **Every probe
carrying `25-12-215` or `25-10-417` returned HTTP 404**, against live HTTP 200
controls **in the same directories** for `24-02-205`, `23-11-205`, `19-06-612`
and `21-12-204` — so the 404s are **absence, not a block**. The Wayback CDX
index of `www.xcelenergy.com` holds **zero** captured URLs containing either
code (RAW **0** of **3,523** unique `staticfiles` URLs captured since
2025-01-01; RAW **0** of the **18** URLs matching `.*[Rr]ebate.*[Ss]ummary.*`
across all time).

    VERIFY (both lines, same host, same User-Agent, one returns 404 and one 200):
    curl -sSI -A 'Mozilla/5.0' 'https://www.xcelenergy.com/staticfiles/xe-responsive/Marketing/Residential-Insulation-Air-Sealing-Rebate-25-12-215.pdf' | head -1
    curl -sSI -A 'Mozilla/5.0' 'https://www.xcelenergy.com/staticfiles/xe-responsive/Programs%20and%20Rebates/Residential/24-02-205%20CO%20Res%20Rebate%20Summary%20Information%20Sheet.pdf' | head -1

> **CONTESTED AND NOW SETTLED, 2026-09-20 (row I). THE `24-02-205` CONTROL IS
> LIVE, AND THE ROW THAT COULD NOT REPRODUCE IT WAS FETCHING A DIFFERENT URL.**
>
> A later row of the same day reported, of the 200-line above, that *"that URL
> 404s under all three User-Agents"* — and recorded, in GCI commit `1bc625c`,
> *"the `XCEL_CO_REBATE_SUMMARY_24_02_205` tombstone's url, marked retrieved
> 2026-09-18, returns HTTP 404 (360 bytes) to this row under all three
> User-Agents with redirects followed."* Both statements went into the record
> and they cannot both be about the same resource. **They are not.** Row I
> retrieved both, 2026-09-20, ten samples over six minutes plus an independent
> four-sample re-run:
>
> | URL | plain | Chrome UA | Googlebot UA |
> |---|---|---|---|
> | `…/Programs%20and%20Rebates/Residential/24-02-205%20CO%20Res%20Rebate%20Summary%20Information%20Sheet.pdf` | **200**, 3,089,201 B, `application/pdf` | **200**, 3,089,201 B, `application/pdf` | **200**, 3,089,201 B, `application/pdf` |
> | `…/Marketing/Residential-Insulation-Air-Sealing-Rebate-24-02-205.pdf` | **404**, 360 B, `text/html` | **404**, 360 B, `text/html` | **404**, 360 B, `text/html` |
>
> Zero redirects on every fetch; `num_redirects=0`. The 200 body is a genuine
> PDF (`%PDF-1.4` header, `%%EOF` trailer, `file` → *PDF document, version 1.4*,
> byte-identical MD5 `fb8fb31c46cd73d9616e78627672a9eb` across all three
> User-Agents), **not** an HTML shell. The 404 body is **exactly 360 bytes**,
> which is the figure the later row recorded — **so neither row mis-measured;
> the two rows fetched two different files that both carry the string
> `24-02-205` in their path.** The later row was probing the *tombstone's* `url`
> field; this section's control is the *Programs and Rebates* sheet. **The
> control above stands, the 404s it anchors remain absence rather than bad
> path, and the unretrievability conclusion for `25-12-215` and `25-10-417` is
> unchanged.** Row I re-probed both codes itself — 30 URLs across six
> `staticfiles` directories and three filename spellings — and got `404 381 B
> text/html` on every one, origin-level (`IBM_HTTP_Server at
> www.xcelenergy.com Port 443`).
>
> **AND THE `24-02-205` LABEL IS A FILENAME, NOT THAT DOCUMENT'S PRINT CODE.**
> `pdftotext -layout` over the live 3,089,201-byte file yields exactly one
> print-code-shaped string, on its own footer:
> *"xcelenergy.com | © 2023 Xcel Energy Inc. | Xcel Energy is a registered
> trademark of Xcel Energy Inc. | 23-11-205"* — and `24-02-205` appears in its
> text **zero** times. So the live `24-02-205` control and the live
> `23-11-205` control are **two copies of one document** (2,810,118 B under
> `Energy Solutions/Residential Solutions/`, different MD5, textually
> near-identical), and **any row keying on filename print codes is measuring a
> different thing than any row keying on footer print codes.** That is the
> mechanical origin of this contradiction and of others like it. `19-06-612`
> was verified the same way and independently: *"Xcel Energy is a registered
> trademark of Xcel Energy Inc. | 19-06-612"*, off
> `…/Working%20With%20Us/CO-Residential-Rebate-Summary-Sheet.pdf`, 200,
> 1,049,343 B.
>
> **METHOD WARNING for whoever re-scores this.** `www.xcelenergy.com` sits
> behind a WAF that answers some rejected requests with **HTTP 200** and an
> HTML body (*"Request Rejected … Your support ID is …"*, 246 B,
> `text/html; charset=utf-8`). **A bare `200` is not proof of liveness on this
> host**; content-type and body must be checked. Conversely a
> correctly-shaped but non-existent filename returns a true `404`, so the WAF
> did not mask the negative results either.
>
> **Standing gap, stated rather than closed:** the most recent CO residential
> rebate summary Xcel itself serves anywhere on that host is the **2024**
> edition (footer `23-11-205`). No 2025 or 2025–2026 edition is served
> first-party at any path tried. The `programs_and_rebates` landing page 302s
> to a Salesforce SPA at `my.xcelenergy.com/s/residential` containing **zero**
> `staticfiles` PDF hrefs (measured: `grep -oiE 'href="[^"]*staticfiles[^"]*\.pdf"'`
> over 380,616 bytes → no matches).

**No substitute print code is asserted, because none could be confirmed
first-party either.** The only retrievable copy of the edition titled
*"COLORADO 2025-2026 REBATE SUMMARY / COLORADO RESIDENTIAL ENERGY EFFICIENCY
PROGRAMS / EFFECTIVE NOV. 16, 2025"* is a **contractor-hosted mirror**
(`royalcomforths.com`, HTTP 200) whose own PDF metadata shows it was
re-processed through **GPL Ghostscript 10.06.0 on 2026-04-14** — a derivative,
not an Xcel-served byte stream. Its footer reads
*"xcelenergy.com | © 2025 Xcel Energy Inc. | … | 25-10-417"* and the string
`25-12-215` appears in it **zero** times. That is a **pointer**, never an
authority. **The edition itself is not in doubt and no proposition below
changes**; only the label by which this document names it does. `25-10-417`
stays in `superseded_identifiers` — removing it is the one change that would
blind a blocking rule — and its `current_replacements` entry has been dropped.

**The proposition inventory, retrieved, with its evidence.** Every one of these
is a real superseded claim that shipped:

| Claim | Superseded because | Where it shipped | Fixed in |
|---|---|---|---|
| *"the newest rebate schedule that could be retrieved is effective January 1, 2024, so the current-year wording could not be confirmed"* | `January 1, 2024` **is** the superseded `24-02-205` sheet; the current CO sheet † was retrieved and hash-verified the same pass | GCI `insulation-rebate-hub.html`, live HTTP 200, in the sitemap; identical proposition **twice** on `insulation-rebate-eligibility-checker.html` (prose + inline JS) | GCI `44d638c` |
| The WHE audit entry path — *"**begin with** a blower door audit, infrared audit, or a Home Energy Squad Plus visit to be eligible"* | the superseded sheet's **own sentence**, reproduced. Enforced by `whe_audit_entry_path_begin_with` only; the `Home Energy Squad` half was **RETIRED 2026-09-20** — see *"A RETIRED PROPOSITION"* below | DCI **35 pages**; LGM `insulation-lafayette.html` in **prose AND JSON-LD**, citing *"Xcel's own rebate summary"* — **a retired sheet's wording wearing a live citation** | DCI `b47a3c2`; LGM `72e18ac` |
| *"air sealing is a **prerequisite** for Xcel's Whole Home Efficiency bonus"* | the current CO sheet † sets no such condition; air sealing is one measure that can count toward three | LGM `air-sealing-longmont.html` (`_service_pages.py:335`) — **matched none of the eight swept strings**; DCI 11 instances on 3 pages incl. `<title>`+`og:title`+`twitter:title` as one string | LGM `72e18ac`; DCI `eb5c939` |
| *"installed and invoiced by **December 31, 2026**"* | in **no** Xcel artifact retrieved; `COPY_VOICE.md:197` recorded the date citing no document | DCI **38 pages**; survived four further rounds at `_generate_calculator_pages.py:344` as **`Dec. 31, 2026`** because every sweep searched the long form | DCI `b47a3c2`, then `f83d421` |
| *"paid out as soon as the third qualifying upgrade is completed"* / *"pays out when the third qualifying measure completes"* | the current CO sheet † publishes **no payout schedule at all** | DCI, removed in prose then **alive in a FAQ and its JSON-LD `acceptedAnswer`**, attributed to *"Xcel's page"* | DCI `b47a3c2`, then `f83d421` |
| *"25% of the rebate already paid"* | current sheet says *"a 25% bonus on all standard rebates"* | DCI **41 pages** | DCI `b47a3c2` |
| *"three or more measures are bundled"* | drops the source's binding clock, *"within two years of enrolling"* | DCI | DCI `b47a3c2` |
| *"the multiplier is expired"* (the 1.5× gas-heat bonus) | **reinstated** by the current CO sheet †, footnote verbatim: *"Invoice must be dated in 2025 or 2026 to receive the bonus"* — the earlier supersession note missed it because it *"enumerated only TWO customer groups"* and the sheet has **three** | LGM `_shared_components.py:314` + 4 doc sites | LGM `a2ba5a6` |
| *"neither Xcel nor Efficiency Works publishes a dollar figure for the audit"* | refuted by the current CO sheet †'s own `HOME ENERGY AUDIT` / `REBATE AMOUNT` table | LGM energy-audit page, **8 places** | LGM `58646f0` |
| `Advice Letter No. 544` cited as current Atmos territory authority | governs the **superseded** Second Revised Sheets; current is **No. 647** | GCI docs | GCI `5f9698b` |
| The 2019 Xcel sheet, print code `19-06-612` | a **search-ranking trap**; *"must never be cited"* | none live | recorded as do-not-cite |
| `nrel.gov` | whole zone returns **authoritative NXDOMAIN** from the `.gov` registry's own nameserver; also renamed to `nlr.gov` | DCI 2 pages + 6 instances incl. dead-code mirrors | DCI `147185c`, `8841f09` |
| `R-value of less than 15` / `R-49 or greater` | the current CO sheet † says pre-job **less than 24**, post-job **60 or greater**, corroborated by print code `17-9230 (01-25)` — and **Xcel's own live HTML page still shows the OLD 15/49 values; the print-coded dated PDF wins, do not "fix" that backwards** | LGM: **0 instances, a NULL RESULT** (`58646f0` verified `0` across body, `<head>`, meta, `og:`, `twitter:` and JSON-LD). DCI: **331 `R-15`/`R-49` occurrences across 70 files, all 331 IECC or ENERGY STAR, zero Xcel** | no copy change needed on either |
| Longmont's adopted energy code = **2021 IECC** | superseded by the 2024 International Codes + Metro Cohort Model Code + Colorado Wildfire Resiliency Code, **effective 2026-07-01** | *"Every LGM page citing the 2021 IECC had been wrong for roughly eight weeks."* The 2024 Metro Cohort text is behind a JS/CloudFront wall — **no R-value number was invented** | open, disclosed |

**SURFACES.** `VIS` `TITLE` `META` `OG` `TW` `LD` `JS` `LOWVIS` `ATTR`(`href`)
`LLMS` `EMBED`. `ATTR` is required for Half A — the superseded sheet was cited by
URL from **2 `url=` fields in 1 file** rendering on **33 DCI pages**, and the
fix was a repoint, not a copy edit.

**NORMALIZATION.** `RAW` for identifiers and URLs; `TXT` sentence-split for
propositions; `SRC` for the generator half. `TXT` is not optional: GCI's
`No. 647` wraps a line break in all three state documents and the full-phrase
grep *"returns a false `0` on two of them."*

**A RETIRED PROPOSITION, AND THE FALSE INFERENCE THAT MADE IT — 2026-09-20
(row C).** `whe_audit_entry_path_hes_plus` bound supersession to the bare
string `Home Energy Squad`, on the premise recorded in the row above it:
*"Tested individually against the current sheet: `Home Energy Squad` 0."*
**The premise is refuted by the publisher's own live pages.**

| surface, retrieved 2026-09-20 | UA | HTTP | `Home Energy Squad` | `begin with` |
|---|---|---|---|---|
| `co.my.xcelenergy.com/s/residential/home-services/whole-home-efficiency` | Googlebot | 200 | **4** | 0 |
| `co.my.xcelenergy.com/s/residential/home-services/home-energy-squad` | Googlebot | 200 | **15** | 0 |
| `co.my.xcelenergy.com/s/residential/home-rebates/insulation-air-sealing` | Googlebot | 200 | 0 | 0 |
| `co.my.xcelenergy.com/s/residential/home-services/home-energy-audit` | Googlebot | 200 | 0 | 0 |
| the **superseded** `24-02-205` sheet (print code `23-11-205`) | browser | 200 | **1** | **1** |

The phrase is Xcel's **current** name for a **current** program — 19 live
occurrences against 1 superseded — so it carries no supersession signal at
all, and `begin with` is the half that discriminates. The proposition is
current too; the live page states the entry path as a **live** eligibility
condition, verbatim: *"To be eligible for the program, you'll need to schedule
a Home Energy Squad Plus visit, or find a qualified, participating contractor
to complete a Blower Door or Infrared Home Energy Audit."*

**THE PAGE IS A SALESFORCE SPA AND A NAIVE FETCH "CONFIRMS" THE WRONG ANSWER.**
Same URL, same day: plain `curl` → **102,323 bytes, 0 occurrences**; browser
User-Agent → **380,616 bytes, 0 occurrences**; Googlebot User-Agent →
**581,231 bytes, 4 occurrences**. All three HTTP 200. **An empty shell is not
an absence.**

**WHAT IT COST.** DCI at `31c98be`: R7 **RAW 119 → ADJUDICATED 107**, across
**45 files**, every one of them true copy correctly attributed to that live
page — and the sole reason DCI's wired build was red. The 12-hit gap is the
generator-SRC restatements `src_dup` already removed.

**THE CAUSE, WHICH IS NOT THIS ONE STRING.** Absence from **one** of a
publisher's documents was read as absence from the publisher. Two config
mechanisms now exist against that:

- **`R7.retired_propositions`** — a retirement is a **record, not a
  deletion**. The entry keeps its old `any_of` and `why`, plus
  `retired_because`, `what_it_cost`, `detection_not_lost` and `reopen_if`,
  and **`rule_R7` prints every row of it on every run**. A blocking rule that
  loses a member can never again look like one that never had it.
- **`R7.superseded_propositions[*].tested_against`** — the list of CURRENT
  first-party surfaces the absence was measured against, each with its
  User-Agent, HTTP status and retrieval date. R7 reports every enforced
  proposition lacking it as **`SUPERSESSION EVIDENCE OWED`**, **report-only,
  never blocking**. At the time of writing that is **12 of 13**.

**NOTHING IT UNIQUELY CAUGHT IS NOW UNCAUGHT, and this is control-tested, not
asserted.** The defect it was built for was a compound claim **attributed by
URL to the `24-02-205` sheet** — half A still catches that (control `R7-A`).
The superseded sheet's own entry-path sentence is still caught by
`whe_audit_entry_path_begin_with` (control `R7d`, and independently by replay
row **3a**, which scores *"2 `whe_audit_entry_path_begin_with` rows"* and is
**CAUGHT**).

**CONTROLS REGISTERED BEFORE THE CHANGE, with their before/after states:**

| control | before | after |
|---|---|---|
| `fixtures/negative/NEG18.html` — DCI's true, live-sourced copy | `*** FALSE ALARM *** R7 B whe_audit_entry_path_hes_plus` | **clean** |
| `fixtures/repaired/R7d_superseded_entry_path.html` — Xcel's current wording | `*** FIRES ON REPAIRED *** 2 hit(s) on sub B` | **repaired-clean** |
| `fixtures/R7d_superseded_entry_path.html` — the 2024 sheet's own sentence | DETECTED (2 B) | **DETECTED (1 B)** |
| `R7-A` / `R7-B` / `R7c` / `R7-REG` | DETECTED | **DETECTED** (R7-B 5 B → 4 B) |

`R7d` carries **no synthetic overlay**, deliberately and against the idiom of
every other R7 control: what it must prove is that the **shipping** config
still has teeth here, and an overlay would prove nothing about that.

**POSITIVE-CONTROL FIXTURE — `fixtures/R7_superseded_source.html`. Both halves
in one file, from GCI `44d638c` (the live false claim) and LGM `72e18ac` (the
retired rule wearing a live citation).**

```html
<!DOCTYPE html>
<html lang="en"><head><title>Insulation Rebate Hub — Greeley</title>
<meta name="description" content="Rebate amounts could not be verified against a current source.">
</head><body>
<p>As of this writing the newest rebate schedule that could be retrieved is
effective January 1, 2024, so the current-year wording could not be confirmed,
and we withhold amounts because the amounts could not be verified against a
current source.</p>
<p class="cited-stat">According to <a href="https://www.xcelenergy.com/staticfiles/xe-responsive/Marketing/Residential-Insulation-Air-Sealing-Rebate-24-02-205.pdf" rel="noopener" target="_blank">Xcel Energy&rsquo;s own rebate summary</a>, the bonus requires that you begin with a blower door audit, an infrared audit, or a Home Energy Squad Plus visit to be eligible, that you use participating Whole Home Efficiency contractors, and that you apply on the WHE rebate application.</p>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"What qualifies?","acceptedAnswer":{"@type":"Answer","text":"Air sealing is a prerequisite for Xcel's Whole Home Efficiency bonus, and the heat pump must be installed and invoiced by Dec. 31, 2026."}}]}</script>
<p>Atmos territory in Colorado is set out in Advice Letter No.
544.</p>
</body></html>
```

The final paragraph deliberately **wraps the line between `No.` and `544`** so
the control also proves `TXT` normalization is live: a `RAW` search for
`Advice Letter No. 544` returns 0 on this fixture, and `TXT` returns 1. Expected
control output:

```
  canary+ R7        fixtures/R7_superseded_source.html   DETECTED  (half A: 2 [url, wrapped AL-544], half B: 4)
  LEVEL-DISAGREE    RAW=1 DEC=1 TXT=2                    DISAGREE — 'Advice Letter No. 544' wraps a line break
```

**WHAT IT DELIBERATELY DOES NOT CATCH.**
- **A source that went stale since the config was written.** The gate enforces a
  list. Canon `f1c4008` names this as its own class: **"`Advice Letter No. 544
  -> No. 647`, a citation going stale INDEPENDENTLY of the fact it supports —
  Atmos's Colorado territory did not change between 2018 and 2026; the filing
  that states it did."** Discovering that is `scripts/staleness_watcher.py`'s
  job, and it cannot do it for PDFs or JS shells (§7.2, §7.3).
- **A source that is bot-blocked but alive.** `NOAA_FRONT_RANGE_WIND` returns
  **403** — *"which is bot-blocking, not a dead document. Retiring a source
  because a scraper was refused would have discarded a live citation."*
  `_shared_components.py:400-403` carries the standing ruling *"Do not retire
  this citation on the strength of a 403."* `CDPHE_ASBESTOS_REG8` is in the same
  state. The config must never list these.
- **A superseded document quoted as a historical record.** Heavily used here:
  canon's `PROPERTY_GENESIS.md` keeps a dated 2026-08-24 block citing
  `24-02-205` verbatim *"because it truthfully reports a live fetch on that
  date"* with a supersession note appended; GCI's
  `docs/board/done/lgm-r49-r60-harmonize.md` keeps its instruction and neutralises
  it beneath. Suppressed by `correction_markers`.
- **Two properties deliberately citing different editions of one section.** GCI
  retains IRC **2021** for `IRC_P2603_5_FREEZING` *"to match every other IRC
  citation already in this dict"* while LGM verified the **2024** text is
  word-for-word identical. R9 must not fire on that either, and both configs
  record it.
- **The NEC edition gap, open on both properties.** `NEC_394_12_KT_INSULATION`'s
  text is verified against the **2017** NFPA 70 OCR while both pages cite their
  city's adopted **2023** edition; whether 394.12(5) changed *"could not be
  conclusively confirmed"* — up.codes bundles 2014/2017/2020/2023 under one URL,
  suggesting continuity, and its text is JS-gated. Flagged, not blocked.

**REQUIRED SCHEMA ADDITION.** §7(4): there is **no** `superseded` or
`superseded_by` field in any of the three `docs/citation-registry.json` files,
and `supersed*` appears as free prose exactly once. The gate therefore runs off
`config.superseded_*` today and prints
`R7 DEGRADED: registry carries no machine-readable supersession marker; running from config list`.
The owed schema addition is
`"superseded_by": {"id": "<new id>", "on": "YYYY-MM-DD", "reason": "…"}` on
`sources[]` and `unwatchable_sources[]` entries, with the watcher left
unchanged (it reads `registry.get("sources", [])` and never iterates
`unwatchable_sources`, so adding a field cannot crash it).

**PER-PROPERTY CONFIG.**

```json
"R7": {
  "superseded_identifiers": ["24-02-205","24_02_205","23-11-205","19-06-612",
                             "25-10-417","Advice Letter No. 544","No. 544",
                             "nrel.gov","NREL","National Renewable Energy Laboratory"],
  "superseded_urls": ["Residential-Insulation-Air-Sealing-Rebate-24-02-205.pdf",
                      "CO-Residential-Rebate-Summary-Sheet.pdf",
                      "nrel.gov/gis/solar.html"],
  "current_replacements": { "24-02-205": "the current Xcel CO residential rebate summary at co.my.xcelenergy.com/s/residential/home-rebates/insulation-air-sealing (print code NOT first-party verified; 25-12-215 retracted 2026-09-20, see current_replacements_note)",
                            "No. 544": "No. 647",
                            "nrel.gov": "nlr.gov" },
  /* `25-10-417` is DELIBERATELY ABSENT from current_replacements as of
     2026-09-20: no successor is known and its own superseded status is in
     doubt. It STAYS in superseded_identifiers -- see
     R7.superseded_identifiers_25_10_417_note in config/common.json. */
  "superseded_propositions": [ /* the 14-row table above, as predicates */ ],
  "correction_markers": ["SUPERSEDED","SUPERSESSION","CORRECTED","RETIRED",
                         "[CORRECTED","do NOT act on","retired figure","~~"],
  "never_retire_on_403": ["NOAA_FRONT_RANGE_WIND","CDPHE_ASBESTOS_REG8"],
  "deliberate_edition_divergence": [
    { "key": "IRC_P2603_5", "gci": "2021 IRC", "lgm": "2024 IRC",
      "reason": "GCI matches its dict's other IRC citations; LGM verified 2024 text identical" }
  ]
}
```

**EXPECTED FALSE-POSITIVE PRESSURE.** Substantial, and every source of it is
recorded. Board files, lane rows, `REMEDIATION_LEDGER.md`, `STATE_OF_PROJECT.md`
and canon's `RETROSPECTIVES/` are **full** of superseded identifiers quoted as
history — the 2026-09-07 four-repo sweep measured **canon 3 hits, DCI 62, LGM 64,
GCI 3** for `24-02-205`/`24_02_205`/`23-11-205`, of which only **9** were live
defects. The gate reads `public/` only, which removes almost all of it; the
residue is the correction-marker suppression, and its enumeration under `FILTER`
is what makes the suppression auditable. Secondary pressure: `NREL` collides
with nothing, but `No. 544` matches any `No. 5441`-style substring, and `544`
alone would match a raster dimension — hence phrase-level, `TXT`-normalized,
word-boundary matching.

---

### R8 — STALE REVIEW DATE

**WHAT IT ASSERTS.** No artifact claims a review or modification date that
(a) precedes the artifact's own first appearance in git, (b) follows **the
as-of**, (c) disagrees with another date surface on the same page, or
(d) precedes the most recent commit that changed that artifact's visible text.

**THE AS-OF IS NO LONGER A HAND-MAINTAINED LITERAL — 2026-09-20 (row C).**
This line used to read *"follows today, 2026-09-17"*, and that date was
written out in four config files plus two hardcoded fallbacks in
`claim_gate.py`. **It aged silently.** Nothing failed on it on 2026-09-19; on
2026-09-20 it produced **246 phantom findings on DCI — R8 RAW 247 /
ADJUDICATED 246 / FAIL**, where the true figure re-measured read-only at the
real date is **RAW 1 / ADJUDICATED 0 / PASS**. `dci.json`'s own `today_note`
had already recorded the identical recurrence **twice** and prescribed
*bumping it by hand*, which is a rule that needs a human to stay true.

`R8.today` is now **`"auto"`**, resolved from the system clock by
`resolve_asof()`, and the per-property pins are gone. Precedence:
`--today` > `R8.today` > `"auto"`.

**WHY THIS IS NOT A LOOSENING, and the direction of the effect is the proof.**
Part (b) is the **only** consumer of the as-of in this rule or any other —
(a) and (d) compare against `git`, (c) compares surfaces against each other —
and it is a strict `>`. So an as-of that moves **forward** can only ever
**remove** hits, and every hit it removes is by construction a date that is
not in the future. **An invented future date is caught at every as-of**;
`fixtures/R8c_future_review_date.html` pins `2027-01-01` for exactly that
reason. A wall-clock as-of therefore cannot redden a green tree as the
calendar rolls, either.

**DETERMINISM IS KEPT WHERE IT IS LOAD-BEARING.** `replay/replay.sh` pins its
own as-of per row (`--today "$today"`, the fixing commit's date) and never
reads this value; the control phase pins `NEG_ASOF` regardless of config.
Both are untouched. What is no longer byte-identical is an ordinary
interactive run across midnight — the right trade, because the header has
always stamped the as-of into the output, and a reproducible report bought by
asking the wrong question is a preserved error, not reproducibility.

**A PIN IS STILL LEGAL AND IS NEVER SILENT AGAIN.** Any effective as-of
behind the system clock prints `AS-OF IS STALE` twice — in the header and in
R8's own notes — naming the drift in days and how to clear it. When it is not
behind, R8 says so explicitly rather than saying nothing.

**AND A SENTINEL MAY NEVER REACH PART (b).** R8 compares dates as **strings**,
and `"2026-09-20" > "auto"` is `False` — an unresolved sentinel would not
fail, it would **silently switch the future-date test off**. `resolve_asof()`
therefore raises `ConfigError` rather than falling through, `_main` resolves
once before any rule runs, and `rule_R8` re-resolves defensively in case an
overlay introduced a value `_main` never saw.

**CLAIM TEST. All four parts are claim tests against measurable facts, and part
(d) is the one that matters.** Parts (a)-(c) are arithmetic. Part (d) compares a
published date against `git log` for `public/<file>` filtered to commits whose
diff changed the file's visible text — which requires the gate to do exactly what
GCI `bf240f8`/`348baf9` did by hand: diff visible text against a baseline
**with the review-date line itself stripped, so it cannot count as its own
change.**

**TWO LIVE DEFECTS, MEASURED 2026-09-17.**

| Property | `REVIEWED_ISO` | Footer `Last reviewed` distribution | Sitemap `lastmod` distribution | Content corrected through |
|---|---|---|---|---|
| **DCI** | `2026-08-24` (`_shared_components.py:76`) | **70 × 2026-08-24**, 1 × 2026-09-10, 1 × 2026-09-01, 1 × 2026-08-05, 1 × 2026-05-05 | **70 × 2026-08-24**, 1 × 2026-09-01, 1 × 2026-08-05, 1 × 2026-05-05 | 2026-09-11 (`37c7b29`) — after eleven rounds of Xcel-claim corrections (2026-09-07), a 198-figure strip (2026-09-10) and the tier-label fix (2026-09-11) |
| **LGM** | `2026-08-05` (`_shared_components.py:203`) | **31 × 2026-08-05**, 15 × 2026-08-11, 2 × 2026-09-01 | 27 × 2026-08-05, 15 × 2026-08-11, 3 × 2026-08-07, 2 × 2026-09-01 | 2026-09-10 (`d6e8dab`) — after blower-door corrections on 26 pages (2026-09-07), a superseded-eligibility-rule fix (2026-09-07) and a 133-figure strip (2026-09-10) |
| **GCI** | `2026-09-09` + `STATIC_PAGE_REVIEWED_ISO = 2026-08-05` | **35 × 2026-09-09**, 1 × 2026-08-30, 2 × 2026-08-05 | **35 × 2026-09-09**, 1 × 2026-08-30, 1 × 2026-08-07 | 2026-09-10 — **correctly bumped, twice, in `bf240f8` and `348baf9`** |

**GCI is the model and its reasoning is the rule.** `bf240f8`: the bump was
*"MEASURED before bumping, because the repo's own BUMP RULE forbids
batch-stamping"* — of 38 pages, **35 changed visibly, 2 changed only in JSON-LD,
1 was byte-identical**; the two schema-only pages were **PINNED** via a new
`sc.STATIC_PAGE_REVIEWED_ISO` because *"schema is explicitly not a content
change under that rule."* Then `348baf9` **reversed a round-2 argument on
evidence and recorded the reversal in code so it is not re-made**: eleven
self-dated pages had bypassed the sitewide constant, and *"the rule is that
`lastmod` equals the page's REAL CONTENT-REVIEW date, not its article-body-edit
date; a content review did occur; and the overlay is the highest-stakes surface
on the page, being what a homeowner reads immediately after handing over a name
and phone number."* It also unpinned `contact.html`, which had been publishing
*"two contradictory dates 33 days apart, and the crawler-facing one was the
false one."* And it recorded, at the hardcode site, that
**"D-007 is a PORT-PARITY justification, not a truth justification … where
parity and accuracy conflict, parity loses."**

DCI has the same debt, measured and recorded and **not** fixed: *"`lastmod` DEBT
IS 70 OF 72 PAGES, NOT 'roughly 13' … this lane changed visible copy on 70 of 72
while `sitemap.xml` still shows 69 pages at `2026-08-24`."* The Auditor HOLD on
DCI still governs and **D-003 is not broken** — *"there is still no per-page date
machinery, so there is still nowhere truthful to record per-page dates."* So on
DCI the gate reports a real finding against a known, held blocker, and the config
records the hold so the finding reads as `KNOWN-OPEN`, with the count still
printed.

**Part (a) — review date preceding creation — is a real shipped defect too.**
DCI `92f3887` D6: the embed-code page *"carries its own `2026-09-10` review date
instead of claiming review on `2026-08-24`, **17 days before the page
existed**."* DCI's live distribution still shows one page at **2026-05-05**,
which is three months before this portfolio's recorded work on it.

**Part (c) — disagreement across surfaces — is DCI's C6 class.** `contact.html`
once showed **three disagreeing dates**: footer *"Last reviewed: June 10,
2026"*, sitemap `lastmod` 2026-08-07, real change 2026-08-24. The date surfaces
that must mutually agree: the footer `<time datetime>`, the visible footer text,
JSON-LD `dateModified`, JSON-LD `datePublished` (as a floor), and
`sitemap.xml` `<lastmod>`.

**SURFACES.** `VIS` (footer text) `ATTR` (`<time datetime>`) `LD`
(`dateModified`, `datePublished`) `SITEMAP` (`<lastmod>`) `META`/`OG`/`TW` (where
a date appears in a description) `EMBED`. Plus `git log` as a non-artifact input.

**NORMALIZATION.** `RAW` for `datetime` and `<lastmod>` (ISO, machine-readable);
`DEC` for the visible footer text (`August 24, 2026` must be parsed and compared
to the `datetime` attribute — a mismatch between the two is part (c)).

**POSITIVE-CONTROL FIXTURES — three, one per failure mode.**

`fixtures/R8a_stale_review_date.html` — the live DCI shape. The fixture ships
with a sidecar `fixtures/R8a.gitfacts.json` supplying
`{"first_seen":"2026-06-01","last_visible_change":"2026-09-11"}` so the control
needs no repo:

```html
<!DOCTYPE html>
<html lang="en"><head><title>R-Value Needed Calculator — Denver</title></head><body>
<p class="footer-reviewed">Last reviewed: <time datetime="2026-08-24">August 24, 2026</time></p>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"Article","dateModified":"2026-08-24","datePublished":"2026-06-01"}</script>
</body></html>
```

`fixtures/R8b_review_precedes_creation.html` — D6's shape, sidecar
`{"first_seen":"2026-09-10"}`:

```html
<!DOCTYPE html>
<html lang="en"><head><title>Embed the R-Value Calculator</title></head><body>
<p class="footer-reviewed">Last reviewed: <time datetime="2026-08-24">August 24, 2026</time></p>
</body></html>
```

`fixtures/R8c_future_review_date.html` — part (b), plus a part (c) disagreement
between the `datetime` attribute and the visible text in the same element:

```html
<!DOCTYPE html>
<html lang="en"><head><title>Insulation in Greeley</title></head><body>
<p class="footer-reviewed">Last reviewed: <time datetime="2027-01-01">September 9, 2026</time></p>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"Article","dateModified":"2026-09-09","datePublished":"2026-10-01"}</script>
</body></html>
```

That last fixture fires four ways: `2027-01-01` is after today; the visible text
disagrees with the attribute; `dateModified` disagrees with the attribute; and
`datePublished` is after `dateModified`. Expected control output:

```
  canary+ R8a       fixtures/R8a_stale_review_date.html         DETECTED  (part d)
  canary+ R8b       fixtures/R8b_review_precedes_creation.html  DETECTED  (part a)
  canary+ R8c       fixtures/R8c_future_review_date.html        DETECTED  (parts b, c x2, ordering)
```

**WHAT IT DELIBERATELY DOES NOT CATCH.**
- **Whether a review actually happened.** A date is a claim about a human act.
  The gate can prove a date is impossible or contradicted; it cannot prove a
  review occurred.
- **A legitimately older date on a genuinely unchanged page.** GCI's
  `about.html` correctly keeps `2026-08-07` because its visible text did not
  change — JSON-LD only — and its footer stays pinned at `2026-08-05`;
  *"neither value is false and the 2-day divergence is pre-existing."* The config
  carries `pinned_pages` per property.
- **`privacy.html`'s own effective date.** GCI's stays at `2026-08-30`, its own
  effective date, not a review date. DCI has `PRIVACY_EFFECTIVE_ISO` as a
  separate constant. Different semantics; excluded by config.
- **The 10 LGM/GCI educational pages' `date_published`.** Untouched by any
  correction on purpose. Only `date_modified` moves.
- **A JSON-LD-only change.** Explicitly not a content change under the repos' own
  bump rule.
- **Whether the per-page date machinery exists.** DCI has none; that is D-003
  and an Auditor HOLD, not something a gate can fix.

**PER-PROPERTY CONFIG.**

```json
"R8": {
  "today": "2026-09-17",
  "reviewed_iso_constant": "REVIEWED_ISO",
  "static_page_constant": "STATIC_PAGE_REVIEWED_ISO",
  "footer_marker": "Last reviewed:",
  "date_surfaces": ["time[datetime]", "footer_text", "ld:dateModified",
                    "ld:datePublished", "sitemap:lastmod"],
  "pinned_pages": { "about.html": { "reason": "visible text unchanged; JSON-LD only",
                                    "expected": "2026-08-07" } },
  "own_effective_date_pages": ["privacy.html"],
  "exempt_pages": ["404.html"],
  "self_dated_sources": ["EDU_LASTMOD_BY_FILENAME", "MODIFIED_XCEL_GAS_CORRECTION"],
  "known_holds": [ { "id": "DCI-D-003",
                     "scope": "all pages",
                     "note": "no per-page date machinery exists; Auditor HOLD governs. Debt measured at 70 of 72 pages.",
                     "report_as": "KNOWN-OPEN" } ]
}
```

**EXPECTED FALSE-POSITIVE PRESSURE.** Moderate, all of it from legitimate
divergence: `datePublished` is correctly older than `dateModified` everywhere;
`privacy.html` and `about.html` carry their own dates by ruling; GCI's two pinned
schema-only pages will look stale to a naive check and are correct; the 10
self-dated educational pages on each of LGM and GCI have a separate constant;
`404.html` has no date at all and must not be read as missing one. The single
worst false-positive risk is **the review-date line counting as its own change**
— `348baf9` hit it and solved it by stripping the line before diffing, and the
gate inherits that exactly.

---

### R9 — INTERNAL CONTRADICTION *(ADDED. Not in the brief's eight. Added because the defect history contains at least eight instances and one of them is LIVE RIGHT NOW.)*

**WHY IT IS ADDED, stated explicitly.** DCI's own C3 finding names the gap in one
sentence: ***"A grep cannot do this: both strings are individually innocuous and
the defect is that they contradict."*** Eight recorded instances, none reachable
by any of R1-R8:

1. **LIVE, MEASURED 2026-09-17, DCI.** `public/llms.txt` states *"the
   before-and-after 20% CFM50 reduction **Xcel insulation and air sealing
   rebates require**"* while `public/air-sealing.html` states, attributed to the
   same document, *"the qualifying minimum standard for the air sealing rebate is
   a 20% reduction in CFM 50 … **the insulation rebates are qualified by post-job
   R-value, not by leakage reduction**."* One property, one cited source, two
   incompatible propositions about which rebates the threshold binds. DCI's own
   `ground-truth.md` line 148-152 settles it against the llms.txt version:
   ***"the threshold binds the AIR SEALING row only — insulation rebates are
   qualified by post-job R-value, not by leakage reduction. Copy that binds both
   as one unit is false."*** And `before and after the work` still renders on
   **13 files, 21 occurrences** on DCI, attributed to a sheet in which
   *"before and after"* occurs **zero times** — established first-party by LGM
   `183378f`. LGM swept it (`124c014`, 12 files / 17 occurrences). **DCI was
   never swept. Rule 8c.**
2. **LGM `e329db7`.** The `llms.txt` tile description *"asserted the conflation
   and denied it in the same sentence"*: *"…why it is the prerequisite step both
   Xcel and Efficiency Works require before paying an insulation or air-sealing
   rebate, **and how that differs from** the home energy audits Xcel lists
   separately."* And it was *"a HALF-FIX of this lane's own commit `58646f0`,
   which added the trailing 'how that differs' clause and left the conflation
   standing in the first half."*
3. **DCI `5350403`.** *"on the WHE page the `h2` asserted the retired rule
   (*'The audit isn't advice; it's the program's front door'*) and the very next
   sentence denied it (*'Xcel's current rebate summary conditions the bonus on …
   three or more qualifying measures'*). **Found ONLY by reading the rendered page
   AFTER the sweep reported clean.**"*
4. **DCI `f83d421`.** An **anchor label** read *"the front door of the WHE
   program"* **four paragraphs from that same page's corrected sentence** *"Xcel's
   current rebate summary does not name an audit as a precondition."* — ***"The
   page contradicted its own navigation."***
5. **DCI C3.** The hidden `calc_output` lead field *"still transmitted 'already
   at code' for an R-49 homeowner"* while the visible output had been corrected
   to R-60. Two surfaces of one tool disagreeing, one of them invisible.
6. **DCI `read-2026-08-25` R-7/R-9/R-12/R-14.** `spray-foam-vs-blown-in-comparator`
   tool output says **two** measures earn the WHE Bonus, its FAQ says **three**;
   `insulation-energy-audit.html`'s TL;DR prices audits at **$300-$600** where
   every other surface says **$200-$500**, *and says audits qualify for federal
   incentives two screens above its own statement that the credit ended*;
   `insulation-spray-foam.html`'s TL;DR prices rim joist at **$800-$3,500** while
   the body and `insulation-rim-joist.html` both say **$400-$1,200**;
   `index.html` states the pre-1990 attic R-value **three ways on one page** —
   `R-11 to R-19` hero, `R-11 to R-30` atomic answer, `R-11` flat tile. **In three
   of those four the divergent surface is the `speakable` target** — the one a
   voice assistant reads aloud.
7. **DCI `read-2026-08-25` R-5 / GCI's asbestos trigger.** `insulation-washington-park.html`
   carried **three different vermiculite testing windows on one page**; GCI had
   three coexisting values (pre-1980 / 1990 / pre-1940). Safety-adjacent, and the
   direction ran toward **less** testing.
8. **DCI `read-2026-08-25` R-10 / R-16.** `xcel-insulation-rebate-guide-denver.html`
   has **zero dollar signs** and says *"**The dollar figures on this page** are
   for Xcel heating customers"*; `resources.html`'s Quick Fact says the Xcel
   rebate is *"a bounded dollar amount, **not a share of the job**"* while a tile
   below says *"30% of project cost against per-measure caps."*

**WHAT IT ASSERTS.** Within one property, no two claim instances about the same
subject assert incompatible propositions — across pages, across surfaces of one
page, and between a tool's visible output and its hidden payload. With `--peer`,
the same holds across two properties for claims attributed to the same source.

**CLAIM TEST.** Build a proposition index over the CLAIM SET: for each
`config.claim_subjects` entry (a subject key plus a set of extractor predicates),
collect every instance with its file, surface, and extracted **value slot**
(a utility name, a numeric range, a polarity, a count, a named condition).
Assert every subject's value set has cardinality 1 after normalisation. Three
sub-tests:

- **N1 — CROSS-PAGE.** Same subject, different value, different files.
- **N2 — CROSS-SURFACE.** Same subject, different value, same file, different
  surfaces. Weighted: a divergence where one side is the `speakable` target, a
  `<title>`/`og:title`/`twitter:title`, or a JSON-LD leaf is reported at higher
  severity, because those are the surfaces Google, Slack and voice assistants
  render.
- **N3 — VISIBLE vs HIDDEN.** For every tool, the visible output set and the
  hidden-field payload set must agree. From DCI C3's own prescription: *"drive
  the JS across its whole input space and assert payload and visible output never
  disagree."* Static half blocking; the driven half was specified to ride R6b's
  opt-in harness — **which does not exist (§6), so the driven half is not run by
  anything.** Corrected 2026-09-21.

**SURFACES.** All of them, including `LLMS` (instances 1 and 2 both live there)
and `ATTR`/`LOWVIS` (instance 4 is an anchor label).

**NORMALIZATION.** `TXT` sentence-split, plus `LD` leaves, plus `JS` string
literals. `TXT` is mandatory — GCI `348baf9` records that *"phrase checks were
run on newline-collapsed text, never line-based, because a line-based check
produced a false absence earlier in this pass."*

**POSITIVE-CONTROL FIXTURE — `fixtures/R9_cross_surface_contradiction/`, a
directory because the rule is inherently multi-file. Two files, both carrying
the LIVE DCI text measured 2026-09-17.**

`fixtures/R9_cross_surface_contradiction/llms.txt`:

```
# Denver Colorado Insulation
## Services
- [Blower Door Testing](https://denvercoloradoinsulation.com/insulation-blower-door-test.html): How a blower door test measures air leakage as CFM50 by depressurizing the house to 50 pascals, and the before-and-after 20% CFM50 reduction Xcel insulation and air sealing rebates require.
```

`fixtures/R9_cross_surface_contradiction/air-sealing.html`:

```html
<!DOCTYPE html>
<html lang="en"><head><title>Air Sealing — Denver</title></head><body>
<p class="cited-stat">According to <a href="https://co.my.xcelenergy.com/s/residential/home-rebates/insulation-air-sealing" rel="noopener" target="_blank">Xcel Energy&rsquo;s residential rebate summary</a>, the qualifying minimum standard for the air sealing rebate is a 20% reduction in CFM 50 &mdash; cubic feet per minute at 50 pascals &mdash; which requires a blower door test before and after the work; the insulation rebates are qualified by post-job R-value, not by leakage reduction.</p>
<p>The audit isn&rsquo;t advice; it&rsquo;s the program&rsquo;s front door.</p>
<p>Xcel&rsquo;s current rebate summary does not name an audit as a precondition.</p>
<nav><a href="/whole-home-efficiency-bonus-stacking-denver.html">the front door of the WHE program</a></nav>
</body></html>
```

The subject `xcel_cfm50_scope` resolves to `{insulation+airsealing}` from
`llms.txt` and `{airsealing only}` from the HTML — cardinality 2, N1 fires. The
subject `whe_audit_precondition` resolves to `{required, not-required}` within
one file across `VIS` and `LOWVIS` — N2 fires twice. Expected:

```
  canary+ R9-N1     fixtures/R9_cross_surface_contradiction/   DETECTED  (xcel_cfm50_scope: 2 values)
  canary+ R9-N2     fixtures/R9_cross_surface_contradiction/   DETECTED  (whe_audit_precondition: 2 values, 1 in nav label)
```

**WHAT IT DELIBERATELY DOES NOT CATCH.**
- **Which side is right.** It reports a contradiction and the config's
  `authoritative_value` where one is recorded (here,
  `xcel_cfm50_scope = airsealing_only`, from DCI's own ground-truth). Where none
  is recorded it reports `NO AUTHORITATIVE VALUE IN CONFIG` and does not guess.
- **A contradiction on a subject not in `claim_subjects`.** This is a registry of
  known-contested subjects, not a semantic engine. Every subject in it came from
  a shipped defect.
- **Deliberate cross-property divergence.** GCI cites IRC 2021 and LGM IRC 2024
  for the same section by design; DCI's atomic-answer band is **40-60 words**
  while LGM's and GCI's are **54-60**. Both recorded in
  `config.deliberate_divergence`.
- **A hidden CSS-suppressed contradiction's visibility.** §7(8): the gate flags
  `display:none` on a claim-bearing ancestor as a `TRAP` and is not a layout
  engine. GCI `bf240f8` found the live case — a correction inside
  `<div class="thank-you">` where the served CSS sets `.thank-you {
  display: none; }`, *"invisible until the visitor handed over a name and phone
  number."*

**PER-PROPERTY CONFIG.**

```json
"R9": {
  "claim_subjects": [
    { "id": "xcel_cfm50_scope",
      "extract": ["CFM ?50|CFM50"],
      "value_slots": { "insulation_and_airsealing": ["insulation and air sealing rebates require","both"],
                       "airsealing_only": ["air sealing rebate is","qualified by post-job R-value, not by leakage"] },
      "authoritative_value": "airsealing_only",
      "authority": "DCI docs/board/ground-truth.md:148-152; LGM 183378f first-party read of the DSM product write-up" },
    { "id": "whe_audit_precondition", "authoritative_value": "not_required",
      "authority": "the current CO rebate summary [code retracted 2026-09-20, see R7.current_replacements_note] lines 123-130: one condition, three measures within two years of enrolling" },
    { "id": "whe_measure_count", "authoritative_value": "three" },
    { "id": "vermiculite_test_trigger" },
    { "id": "audit_price_range" },
    { "id": "rim_joist_price_range" },
    { "id": "pre1990_attic_rvalue" },
    { "id": "xcel_rebate_basis" }
  ],
  "high_severity_surfaces": ["speakable", "TITLE", "OG", "TW", "LD"],
  "tools": [ { "page": "public/r-value-needed-calculator.html",
               "visible": "#calcOutput", "hidden": ["lf-calc-inputs","lf-calc-output"] } ],
  "deliberate_divergence": [
    { "subject": "IRC_P2603_5 edition", "gci": "2021", "lgm": "2024" },
    { "subject": "atomic_answer_band", "dci": "40-60", "lgm": "54-60", "gci": "54-60" }
  ]
}
```

**EXPECTED FALSE-POSITIVE PRESSURE.** Moderate. A subject legitimately scoped
differently per page (an area page's town-specific figure vs a service page's
range) will read as a contradiction; `claim_subjects` entries therefore carry an
optional `scope_by` (`town`, `measure`, `page_class`). And the correction-marker
suppression applies again, since a page that quotes a retired value in order to
retire it will otherwise present as two values.

---

### R10 — DANGLING PROMISE *(ADDED. Not in the brief's eight. Added because canon already records it as a named third failure mode with measured reach, and because no other rule can see it — these sentences contain no figure and no banned string.)*

**WHY IT IS ADDED.** Canon
`METHODS/CANDIDATE-do-not-scope-with-grep-over-html.md`, section heading verbatim:
**"A THIRD FAILURE MODE THE SAME PASS SURFACED: deleting a figure is half the
job."** Its own words: *"live sentences on two properties still pointing at
figures that no longer exist — grammatical, containing no numeral, therefore
**invisible to both the gate and a prose proofread**."* The two recorded
instances, verbatim:

- **DCI:** *"The standard rebate guide covers the base amounts the bonus
  multiplies"* — linking to a page that states *"Per-measure dollar caps are
  deliberately not enumerated on this page."*
- **GCI:** *"The Atmos figures quoted elsewhere on this site are for the towns
  Atmos serves"* — on a property that now quotes **zero** Atmos figures.

Measured reach: **seven inbound promises across two refusing destinations, and
five of the seven predated the ruling entirely** — opened by a 2026-08-24 pass
that deleted DCI's cost estimator and never revisited what pointed at it. *"Pages
told readers a calculator 'estimates the project cost' while that calculator said
it 'does not compute a dollar estimate.' **Sixteen days live, through every audit
in between.**"* And GCI hit the same class twice more in `f0203ad` D2 (figure
disclaimers for figures that no longer exist, on Johnstown and Severance, each
shipping twice — body prose **and** `FAQPage` JSON-LD) and `a91dfd4` D5.

**WHAT IT ASSERTS.** Every sentence that promises the reader will find a figure,
amount, price, cap or answer at a named destination is satisfied by what that
destination actually renders.

**CLAIM TEST.** Genuinely a claim test, and the only kind that can work.
Enumerate every `config.promise_pattern` match in the CLAIM SET; for each,
resolve the destination — the enclosing anchor's `href`, or the named page from
`config.page_titles`, or the same page when the promise is reflexive
(*"quoted elsewhere on this site"* resolves to the whole property). Then assert
the destination's own CLAIM SET contains a value of the promised kind. Canon's
own prescription, adopted verbatim as the method: *"Search for the PROMISE —
'covers the amounts', 'for current amounts see', 'the figures are on', 'how
much' — against what each destination now actually renders."*

Three destination classes and the predicate for each:

- **A page that refuses.** If the destination contains a
  `config.refusal_marker` (*"deliberately not enumerated"*, *"does not compute a
  dollar estimate"*, *"we don't republish the figures"*, *"amounts are not
  estimated here"*), any inbound promise of a figure is a FAIL.
- **A page that is empty of the promised kind.** If the promise is of a dollar
  figure and the destination's `$`-figure count is 0 (which is now true of
  **every page on DCI**, of all but 8 JS-comment cost rates on LGM, and of all
  but the 20 WAP income figures on GCI), FAIL.
- **A whole-property reflexive promise.** *"quoted elsewhere on this site"* — the
  destination is the property, and the predicate runs over the whole READ_SET.

**SURFACES.** `VIS` `TITLE` `META` `OG` `TW` `LD` `LOWVIS` (anchor labels, tile
labels, table cells — GCI's disclaimers shipped in `<td>` and in `FAQPage`)
`ATTR`(`href`) `LLMS` `EMBED`.

**NORMALIZATION.** `TXT` sentence-split for the promise; `RAW` for the
destination's figure count; `DEC` for refusal markers (they contain
typographic apostrophes).

**POSITIVE-CONTROL FIXTURE — `fixtures/R10_dangling_promise/`, three files.
The two promise sentences are quoted verbatim from canon's addendum; the two
refusal sentences are quoted verbatim from the destinations canon names.**

`fixtures/R10_dangling_promise/insulation-attic.html`:

```html
<!DOCTYPE html>
<html lang="en"><head><title>Attic Insulation — Denver</title></head><body>
<p>The <a href="/xcel-insulation-rebate-guide-denver.html">standard rebate guide</a>
covers the base amounts the bonus multiplies.</p>
<p>The <a href="/attic-insulation-cost-calculator.html">cost calculator</a>
estimates the project cost for your own home.</p>
<p>The Atmos figures quoted elsewhere on this site are for the towns Atmos serves.</p>
</body></html>
```

`fixtures/R10_dangling_promise/xcel-insulation-rebate-guide-denver.html`:

```html
<!DOCTYPE html>
<html lang="en"><head><title>Xcel Insulation Rebate Guide — Denver</title></head><body>
<p>Per-measure dollar caps are deliberately not enumerated on this page.</p>
</body></html>
```

`fixtures/R10_dangling_promise/attic-insulation-cost-calculator.html`:

```html
<!DOCTYPE html>
<html lang="en"><head><title>Attic Insulation Cost Calculator — Denver</title></head><body>
<p>This tool does not compute a dollar estimate.</p>
</body></html>
```

Three hits: two anchor-resolved promises against refusing destinations, and one
reflexive whole-property promise against a corpus containing zero Atmos figures.
Expected:

```
  canary+ R10       fixtures/R10_dangling_promise/   DETECTED  (3: 2 anchor-resolved, 1 reflexive)
```

**WHAT IT DELIBERATELY DOES NOT CATCH.**
- **A promise whose destination is off-property.** *"Efficiency Works publishes
  the amount paid at each tier on its own rebates page"* is the **sanctioned
  wayfinding form** — every figure removed under the 2026-09-09 ruling was
  *"REPLACED with wayfinding to the program's own page, never just deleted."*
  The gate does not fetch external URLs (§7.3) and treats an off-property
  destination as compliant by construction, printing that in its blind spot.
- **A promise of something other than a figure** — a process, a checklist, a
  phone number.
- **A broken link.** `_check_links.py` owns that, exists in all three repos, and
  exits 0 today.
- **A promise satisfied by a figure that is itself wrong.** R3, R5 and R7 own
  that.
- **A refusal marker the config does not know.** This is the rule's main
  weakness and it is printed: a destination that refuses in novel words looks
  like a destination that simply has no figures, which is still a FAIL here — so
  the failure mode is a false positive, not a false negative. Stated as a
  deliberate bias.

**PER-PROPERTY CONFIG.**

```json
"R10": {
  "promise_patterns": ["covers the (base )?amounts","for current amounts",
                       "the figures are on","the amounts are on","how much .* pays",
                       "quoted elsewhere","see the (current )?(amounts|figures|caps)",
                       "estimates the project cost","gives you the (number|amount)",
                       "lists the amounts","publishes the amount",
                       "the amounts (are|can be) found","full amounts","the caps are"],
  "refusal_markers": ["deliberately not enumerated","does not compute a dollar estimate",
                      "doesn&rsquo;t republish the figures","doesn't republish the figures",
                      "amounts are not estimated here","no dollar figure",
                      "we don&rsquo;t publish the amounts","carries no amount",
                      "names no payer"],
  "offproperty_is_compliant": true,
  "page_titles": { "standard rebate guide": "public/xcel-insulation-rebate-guide-denver.html",
                   "cost calculator": "public/attic-insulation-cost-calculator.html" },
  "reflexive_markers": ["elsewhere on this site","on this site","other pages here"]
}
```

**EXPECTED FALSE-POSITIVE PRESSURE.** Moderate-to-high, and deliberately biased
toward false positives per the note above. The heaviest source is the sanctioned
wayfinding copy itself, which is now on essentially every rebate-bearing page on
all three properties: *"Efficiency Works publishes the amount paid at each tier
on its own rebates page; this site doesn't republish the figures, because they
change and we can't monitor them for you"* (LGM `air-sealing-longmont.html`,
three renderings, measured) matches `publishes the amount` **and** carries a
refusal marker **and** points off-property — so it must resolve as compliant on
two independent grounds. That sentence is the single best regression test for
this rule and is `fixtures/negative/NEG10.html`.

---

### R11 — ATTRIBUTION DEBT *(ADDED, REPORT-ONLY, NON-BLOCKING. Not in the brief's eight. Added under canon Rule 7b: this is a measured figure that must survive the session, and the alternative is that the next pass re-derives it.)*

**WHY IT IS ADDED AND WHY IT IS NON-BLOCKING.** DCI measured it across four
rounds and the coordinator explicitly ruled it **outside** that pass's defect
class; the adversarial reader *"would not block on it."* The lane row's own
reason for recording it: *"Recorded so the next pass inherits the figure instead
of re-deriving it."* And the ruling that keeps it out of the blocking set:
*"**Every one of those claims is accurate to the sheet — this is consistency of
treatment, not truth.**"* So the gate reports it, with the arithmetic it took
four rounds to get right, and never fails on it.

**WHAT IT ASSERTS (reports).** For each `config.tracked_term`, the count of pages
**asserting** it, **attributing** it, asserting it **outside** any attributing
block, and doing **both** — plus registry `pages` drift.

**THE COUNTING DEFINITIONS, verbatim from DCI `1794f98`, because mixing them is
what produced two wrong figures in two consecutive rounds:** *"asserting = claim
anywhere in the page; attributed = a `cited-stat` block carries it;
unattributed = it appears **OUTSIDE** any `cited-stat` block, **which is NOT
asserting minus attributed**."* **"Subtraction is not measurement."** Two
recorded errors from violating it: the `$600` row was logged **72/10** when it is
**72/0** — *"the `10` was the CFM 50 count transcribed onto the wrong row, and it
sat on the LARGEST gap, where the next pass would have read it as ten-tenths done
and never opened it"* — and the CFM 50 unattributed figure was computed as
`26 = 36 − 10` when the measured value is **34**, because **8 pages do both.**
**Every cell in this rule is its own query, and the gate emits the query beside
the number.**

**The inherited DCI table, five rows, every cell measured** (`asserting /
attributed / unattributed / both`): `$600` Combo Bonus **72 / 0 / 72 / 0** ·
participating-contractor rule **72 / 23 / 72 / 23** · WHE 25% bonus
**42 / 1 / 42 / 1** · CFM 50 20% reduction **36 / 10 / 34 / 8** · by-check
payment method **46 / 1 / 46 / 1**. Roughly **113** unattributed assertions when
first tallied; the fifth row was added in round 9 and its single attributing page
is `xcel-insulation-rebate-guide-denver.html`, where *"the attribution is plain
prose, not the citation mechanism."*

**CLAIM TEST.** Yes — it counts propositions, not strings, using the same
resolution as R5 and the same `cited-stat` block boundaries as R1.

**SURFACES.** `VIS` `LD` `LOWVIS` `META` `OG` `TW` `LLMS`.
**NORMALIZATION.** `TXT`, plus block-boundary resolution on `RAW`.

**POSITIVE-CONTROL FIXTURE — `fixtures/R11_attribution_debt.html`.** The control
is not "does it fire" but **"does it count correctly, without subtracting."** One
page that both attributes and asserts outside the block, so the naive subtraction
gives the wrong answer:

```html
<!DOCTYPE html>
<html lang="en"><head><title>Air Sealing — Denver</title></head><body>
<p class="cited-stat">According to <a href="https://co.my.xcelenergy.com/s/residential/home-rebates/insulation-air-sealing" rel="noopener" target="_blank">Xcel Energy&rsquo;s residential rebate summary</a>, the qualifying minimum standard for the air sealing rebate is a 20% reduction in CFM 50.</p>
<p>Because the air sealing rebate turns on a 20% reduction in CFM 50, the blower
door reading is what decides whether the work qualifies.</p>
<p>The Whole Home Efficiency Bonus adds 25% on all standard rebates when three
or more measures are installed within two years of enrolling.</p>
</body></html>
```

Correct output for a one-page corpus: `CFM 50 20% reduction 1 / 1 / 1 / 1` and
`WHE 25% bonus 1 / 0 / 1 / 0`. A gate that subtracts reports `1 / 1 / 0 / -` for
the first row and **fails the control**. Expected:

```
  canary+ R11       fixtures/R11_attribution_debt.html   DETECTED  (CFM50 1/1/1/1 — subtraction would give 0 unattributed)
```

**WHAT IT DELIBERATELY DOES NOT CATCH.** Whether the claim is true (all five
tracked DCI terms are accurate to the current CO sheet †); whether attribution is *owed*
(a Director/coordinator judgement); anything at all on LGM and GCI until their
`tracked_terms` are populated — **currently empty, and the gate prints
`R11: 0 tracked terms configured for <property>` rather than `PASS`.**

**PER-PROPERTY CONFIG.**

```json
"R11": {
  "blocking": false,
  "attributing_block_selector": "p.cited-stat",
  "tracked_terms": [
    { "id": "combo_bonus_600", "label": "$600 Combo Bonus",
      "expected": { "asserting": 72, "attributed": 0, "unattributed": 72, "both": 0 } },
    { "id": "participating_contractor", "expected": { "asserting": 72, "attributed": 23, "unattributed": 72, "both": 23 } },
    { "id": "whe_25pct", "expected": { "asserting": 42, "attributed": 1, "unattributed": 42, "both": 1 } },
    { "id": "cfm50_20pct", "expected": { "asserting": 36, "attributed": 10, "unattributed": 34, "both": 8 } },
    { "id": "by_check_payment", "expected": { "asserting": 46, "attributed": 1, "unattributed": 46, "both": 1 } }
  ],
  "report_registry_pages_drift": true,
  "forbid_subtraction": true
}
```

`expected` is a **drift baseline, not an assertion** — the gate prints
`measured N (baseline M, delta ±K)` so a change is visible without being a
failure. The `forbid_subtraction` flag is real: the implementation asserts each
cell was produced by its own query and exits 2 if any cell is derived.

**EXPECTED FALSE-POSITIVE PRESSURE.** Not applicable in the usual sense — the
rule never fails. Its risk is the opposite: a **miscount** presented as fact.
That is what the control fixture exists to prevent, and why the query sits beside
every number.

---

## 9. NEGATIVE CONTROLS

Fourteen, all derived from copy that is live and correct right now, or from a
recorded false positive that actually cost a pass. Each must return **clean**;
a hit is `*** FALSE ALARM ***` and exits 2.

| ID | Content | Guards against |
|---|---|---|
| NEG01 | `<p class="cited-stat">According to <a href="…">the Town of Milliken new residents guide</a>, Xcel Energy is named as the natural gas provider for most of Milliken.</p>` (`quote=False`, real, GCI `bf240f8`) | R1 firing on a sanctioned attributed paraphrase |
| NEG02 | `<p>If you do hire after the quote, that's between you and the contractor. If a quote skips both, get another quote.</p>` (real, all three `_shared_components.py`) | R1 keying on the word *quote* rather than the glyph |
| NEG03 | GCI ground-truth's own supersession bullet quoting `- **Gas utility: Atmos Energy.**` in order to retire it | R1/R2/R7 firing on a correction that quotes its subject |
| NEG04 | `<p>Insulating the rim joist matters because can lights, the furnace flue and plumbing-stack chases are where the stack effect pulls air through.</p>` (real, DCI) | R4 firing on `stack effect` / plumbing stack / `can lights` |
| NEG05 | The `20-40%` wind-washing sentence **with** its `cited-stat` block attached | R5 firing on a correctly-attributed figure |
| NEG06 | `<p>Based on your inputs, your current state estimates to roughly <strong>R-19</strong>, which is 68% short of target.</p>` | R3/R5 firing on a visitor-input computation |
| NEG07 | LGM's 8 surviving JS-comment installed-cost rates: `// $1.50/sf loose-fill, $3.50/sf dense-pack, $300 setup, $1,200 typical` | R3 firing on Ruling-2 project costs |
| NEG08 | GCI's WAP block: `Weatherization is free if your household is at or below $70,000 for one person or $99,920 for four, per the Colorado Energy Office; checked September 10, 2026.` | R3 firing on the standing WAP exception |
| NEG09 | `<p>Can I just add new insulation on top of old, failing insulation? Sometimes — it depends what is under there.</p>` (real, DCI; GCI and LGM carry variants) | R4 firing on insulation-physics `on top of` |
| NEG10 | LGM's live wayfinding sentence: `Efficiency Works publishes the amount paid at each tier on its own rebates page; this site doesn't republish the figures, because they change and we can't monitor them for you.` | R3 **and** R10 firing on sanctioned off-property wayfinding with a refusal marker |
| NEG11 | `<p class="footer-reviewed">Last reviewed: <time datetime="2026-08-07">August 7, 2026</time></p>` on `about.html` with sidecar `{"last_visible_change":"2026-08-07"}` | R8 firing on GCI's correctly-pinned schema-only page |
| NEG12 | `<p>The 2021 IECC Table R402.1.3 ceiling minimum for Climate Zone 5 is R-60; ENERGY STAR recommends R-49 to R-60 for retrofits, which is a recommendation and not a code requirement.</p>` | R3/R5/R7 firing on IECC/ENERGY STAR figures — DCI measured **331 such occurrences across 70 files, all 331 legitimate** |
| NEG13 | `<p>Radon mitigation is a common entry path for soil gas, and the crawl space hatch is the literal front door for removal work.</p>` | R7 firing on `entry path` (radon, ×2) and `front door` (×3 literal) — both verified-and-left on DCI |
| NEG14 | `<p>Windsor sits in Weld County, and part of Erie does too, which is why the county line matters for permits.</p>` | R2 hard-failing on `Weld County`, which is an `INFO`/`REVIEW` classification on LGM, not a FAIL |
| NEG18 | `<p>An audit is how you enter Xcel's Whole Home Efficiency program - its own program page requires a Home Energy Squad Plus visit or a Blower Door or Infrared Home Energy Audit by a qualified participating contractor.</p>` (real, DCI) | R7 firing on **true copy sourced to Xcel's own live page** — it FALSE-ALARMED on `whe_audit_entry_path_hes_plus` until that claim_id was retired on 2026-09-20. If it ever false-alarms again, a supersession marker has been bound to a string the publisher still uses |

**The table above covers NEG01–NEG14 and NEG18. `NEGATIVES` in the
implementation is `NEG01..NEG18`, and NEG15, NEG16 and NEG17 are fixture
DIRECTORIES** (a correct-copy vector can need a generator and the page it
renders into, which one `.html` cannot express) **and are not yet tabulated
here.** Stated as a gap rather than left as an implied-complete list.

Three of the first fourteen — NEG03, NEG12, NEG13 — exist because a real sweep in
this portfolio fired on exactly that copy and a human had to adjudicate it back.
NEG05 and NEG10 exist because the same sentence must be seen as compliant by two
different rules for two different reasons, and a rule that gets it right for the
wrong reason will get the next one wrong.

---

## 10. PER-PROPERTY CONFIG — THE SCHEMA, FILLED IN

Every value below was measured or quoted from the repos on 2026-09-17 at DCI
`f9e7551`, LGM `084a423`, GCI `d9ebab7`. Rule-level blocks are in §8; this
section carries the property-identity block and the territory model, which is
where the three configs actually differ.

### 10.1 Common header

```json
{
  "schema_version": 1,
  "key": "dci|lgm|gci",
  "repo": "denvercoloradoinsulation.com|longmontcoloradoinsulation.com|greeleycoloradoinsulation.com",
  "domain": "https://<repo>",
  "measured_at": { "date": "2026-09-17", "head": "<sha>" },
  "min_artifacts": 85 | 59 | 49,
  "expected_html": 75 | 48 | 38,
  "embed_artifacts": [...],
  "key_files_excluded": ["public/<md5>.txt"],
  "gates_present": [...],
  "gates_absent": [...],
  "reviewed_iso": "...",
  "atomic_answer_band": [40,60] | [54,60] | [54,60]
}
```

`gates_absent` is a first-class field because a null result is an artifact:
**DCI has no `_artifact_grep.sh`, no `_similarity_check.py`, no `_out_guard.py`;
LGM has no `_similarity_check.py`, no `_svc_pending_import_check.py`; GCI has no
`_out_guard.py`.** Each absence was established by `find` + `git ls-files`, not
assumed, in the lane rows cited in §11.

### 10.2 DCI — `config/dci.json`

```json
{
  "key": "dci",
  "repo": "denvercoloradoinsulation.com",
  "domain": "https://denvercoloradoinsulation.com",
  "measured_at": { "date": "2026-09-17", "head": "f9e7551" },
  "min_artifacts": 85,
  "expected_html": 75,
  "embed_artifacts": ["public/r-value-needed-calculator-embed.html",
                      "public/r-value-needed-calculator-embed-code.html"],
  "key_files_excluded": ["public/1b79c33b73e0dea0470080c5c9854d20.txt"],
  "svg_readable": ["public/favicon.svg", "public/logo.svg"],
  "og_image_raster_only": true,
  "gates_present": ["regen_all.sh", "_postbuild_check.py", "_check_links.py",
                    "_intra_similarity_check.py", "_validators.py",
                    "ops/similarity_canary.sh", "ops/functional_proof.sh",
                    "ops/live_token_check.sh", "ops/hooks/commit-msg"],
  "gates_absent": ["_artifact_grep.sh", "_similarity_check.py", "_out_guard.py"],
  "reviewed_iso": "2026-08-24",
  "atomic_answer_band": [40, 60],

  "R2": {
    "market": "Denver metro",
    "gas_utility": "Xcel Energy",
    "electric_utility": "Xcel Energy",
    "forbid_electric_utility_naming": false,
    "territory_note": "docs/board/ground-truth.md:5-7 verbatim: 'Xcel Energy is both the gas and electric utility for this market. Denver metro. Unlike Longmont and Greeley, there is no second utility and no service-area hedging required.'",
    "towns": {
      "Denver":          { "gas": "Xcel Energy", "gas_state": "CONFIRMED", "gas_qualifier": "", "electric": "Xcel Energy", "page_slugs": ["index.html"] },
      "Lakewood":        { "gas": "Xcel Energy", "gas_state": "CONFIRMED", "page_slugs": ["insulation-lakewood.html"] },
      "Arvada":          { "gas": "Xcel Energy", "gas_state": "CONFIRMED", "page_slugs": ["insulation-arvada.html"] },
      "Aurora":          { "gas": "Xcel Energy", "gas_state": "CONFIRMED", "page_slugs": ["insulation-aurora.html"] },
      "Wheat Ridge":     { "gas": "Xcel Energy", "gas_state": "CONFIRMED", "page_slugs": ["insulation-wheat-ridge.html"] },
      "Centennial":      { "gas": "Xcel Energy", "gas_state": "CONFIRMED", "page_slugs": ["insulation-centennial.html"] },
      "Englewood":       { "gas": "Xcel Energy", "gas_state": "CONFIRMED", "page_slugs": ["insulation-englewood.html"] },
      "Littleton":       { "gas": "Xcel Energy", "gas_state": "CONFIRMED", "page_slugs": ["insulation-littleton.html"] },
      "Westminster":     { "gas": "Xcel Energy", "gas_state": "CONFIRMED", "page_slugs": ["insulation-westminster.html"] },
      "Thornton":        { "gas": "Xcel Energy", "gas_state": "CONFIRMED", "page_slugs": ["insulation-thornton.html"] },
      "Park Hill":       { "gas": "Xcel Energy", "gas_state": "CONFIRMED", "page_slugs": ["insulation-park-hill.html"] },
      "Washington Park": { "gas": "Xcel Energy", "gas_state": "CONFIRMED", "page_slugs": ["insulation-washington-park.html"] },
      "Highland":        { "gas": "Xcel Energy", "gas_state": "CONFIRMED", "page_slugs": ["insulation-highland.html"] },
      "Golden":          { "gas": "Xcel Energy", "gas_state": "CONFIRMED", "page_slugs": ["insulation-golden.html"],
                           "municipal_program": "City of Golden rebate match",
                           "note": "Golden runs its own municipal match program with its own published caps ($1,000/$2,000, removed 2026-09-10). It is NOT Xcel and must not be attributed to Xcel." },
      "Broomfield":      { "gas": "Xcel Energy", "gas_state": "CONFIRMED", "page_slugs": ["insulation-broomfield.html"] },
      "Northglenn":      { "gas": "Xcel Energy", "gas_state": "CONFIRMED", "page_slugs": ["insulation-northglenn.html"] }
    },
    "non_territorial_programs": ["Colorado Energy Office", "ENERGY STAR",
                                 "HEAR", "City of Golden", "DRCOG",
                                 "Power Ahead Colorado",
                                 "Xcel's income-qualified programs"],
    "forbidden_program_names": ["Xcel IQ Program", "IQ Program", "Xcel IQ"],
    "forbidden_program_reason": "3da02df/1794f98/cb97983: 'IQ Program' as a customer-facing umbrella name returns 0 on Xcel's own Colorado DSM filing page (which does carry 23 'IQ' tokens, all in SPECIFIC program titles: IQ Single-Family Weatherization, IQ Multifamily Weatherization, IQ Non-Profit, IQ Energy Savings Kits). Do not reinstate without a first-party Xcel source. Plural is the accurate form.",
    "territorial_constants": ["REBATE_ACKNOWLEDGMENT", "THANK_YOU_BODY"],
    "sibling_artifacts_forbidden": ["Greeley","Evans","Windsor","Eaton","Johnstown",
                                    "Milliken","Severance","LaSalle","Ault",
                                    "Longmont","Erie","Lafayette","Louisville","Niwot",
                                    "Atmos","Efficiency Works",
                                    "Longmont Power & Communications"],
    "elevation_anchor": "5,280"
  },

  "R3": { "allowed_figures": [],
          "note": "MEASURED 2026-09-17: /usr/bin/grep -rhoE '\\$[0-9][0-9,.]*' over public/ returns ZERO occurrences. DCI is the only property with no surviving dollar figure of any kind. Was 198 before 5703f8c ($600 x173, $0 x12, $2,000 x6, $1,000 x6, $1,500 x1).",
          "allowed_structure_percentages": ["75%", "50% of project cost", "capped at 100% of project cost", "30% of project cost"],
          "allowed_thresholds": [],
          "allowed_thresholds_reason": "REMOVED 2026-09-20, THE SAME DAY IT WAS ADDED, BY MEASUREMENT. It was added as [\"20%\", \"20 percent\"] on the ground that an overlap rule could not separate the legitimate blower-door FAQ row from the evasions. MEASURED FALSE: with this list empty, f_question goes from 'matched 4, removed 0' to 'matched 4, removed 3' and removes all three FAQ rows by itself. What the entry was actually load-bearing for was THREE PAGE-TITLE ROWS, now closed by f_title_np. It opened TEN evasions of the form 'Our crews deliver a 20% CFM 50 reduction on every air sealing job'. EMPTY, AND MUST STAY EMPTY ON THIS PROPERTY. Full correction in config/dci.json and in the retraction block above." },

  "R4": { "programs": ["Xcel Whole Home Efficiency Bonus", "Whole Home Efficiency Bonus",
                       "Combo Bonus", "Xcel's income-qualified programs",
                       "HEAR", "Power Ahead Colorado", "City of Golden rebate match",
                       "federal 25C", "Section 25C"],
          "noun_use_constants": ["REBATE_ACKNOWLEDGMENT"],
          "director_desk": "whole-home-efficiency-bonus-stacking-denver.html was KEPT and attributed on the narrow reading. A stricter reading deletes the page. Deleting a ranking page is the Director's call and is OPEN." },

  "R5": { "known_uncited": [ { "text": "15% reduction in heating and cooling costs",
                               "files": ["public/r-value-needed-calculator.html",
                                         "public/do-i-need-new-insulation-quiz.html"],
                               "occurrences": 2,
                               "status": "OPEN — flagged to the Director 2026-09-11",
                               "audience": "33 -> 54 input combinations after 37c7b29" } ] },

  "R6": { "label_chains": [ { "id": "dci-rvalue-tier", "...": "see §8 R6" } ] },

  "R8": { "reviewed_iso": "2026-08-24",
          "known_holds": [ { "id": "DCI-D-003", "note": "No per-page date machinery. Auditor HOLD governs. Debt measured at 70 of 72 pages; sitemap shows 70 x 2026-08-24 while content was corrected through 2026-09-11.", "report_as": "KNOWN-OPEN" } ],
          "own_effective_date_pages": ["privacy.html"],
          "anomalies": [ { "page": "unidentified", "date": "2026-05-05", "note": "one page publishes 2026-05-05 in both footer and sitemap; investigate" } ] },

  "R11": { "blocking": false, "tracked_terms": [ "...see §8 R11, five rows, DCI only" ] }
}
```

### 10.3 LGM — `config/lgm.json`

```json
{
  "key": "lgm",
  "repo": "longmontcoloradoinsulation.com",
  "domain": "https://longmontcoloradoinsulation.com",
  "measured_at": { "date": "2026-09-17", "head": "084a423" },
  "min_artifacts": 59,
  "expected_html": 48,
  "embed_artifacts": [],
  "embed_artifacts_note": "NULL RESULT — LGM has no embed frame. Verified: ls public/ | /usr/bin/grep -i 'embed|frame|iframe' returns empty.",
  "key_files_excluded": ["public/ee368c8751be4043b5e29d015679f93b.txt"],
  "svg_readable": ["public/favicon.svg", "public/logo.svg", "public/og-image.svg"],
  "og_image_raster_only": false,
  "gates_present": ["regen_all.sh", "_postbuild_check.py", "_check_links.py",
                    "_intra_similarity_check.py", "_validators.py",
                    "_out_guard.py", "_artifact_grep.sh",
                    "ops/similarity_canary.sh", "ops/functional_proof.sh",
                    "ops/live_token_check.sh"],
  "gates_absent": ["_similarity_check.py", "_svc_pending_import_check.py"],
  "reviewed_iso": "2026-08-05",
  "atomic_answer_band": [54, 60],
  "atomic_answer_note": "Enforced in code by RAISING. It broke one pass's build three times and rejected a rewrite at 79 words. Any copy correction hits it.",

  "R2": {
    "market": "Longmont",
    "gas_utility": "Xcel Energy",
    "electric_structure": "SPLIT — municipal in Longmont, Xcel in the other three",
    "forbid_electric_utility_naming": false,
    "territory_note": "docs/board/ground-truth.md:5-7 verbatim: 'Utility structure — stacking is an EVIDENTIARY rule. Gas: Xcel Energy. Electric: Longmont Power & Communications (LPC), municipal, via the Efficiency Works program.'",
    "DISCREPANCY_AGAINST_BRIEF": "The brief states 'LGM = Xcel gas PLUS Efficiency Works for Longmont Power & Communications ELECTRIC customers only.' That is TRUE but materially incomplete, and the missing half is load-bearing. ground-truth.md:46-53 verbatim: '4-town access caveat still governs any stacking sentence. Lafayette, Louisville and Niwot are Xcel-electric and cannot access Efficiency Works at all, so no stacking statement of any kind applies to them. Within Longmont it reaches only the LPC-served portion.' So Efficiency Works is available on ONE of four towns, and only on part of that one. Recorded, not reconciled.",
    "towns": {
      "Longmont":   { "gas": "Xcel Energy", "gas_state": "CONFIRMED",
                      "electric": "Longmont Power & Communications",
                      "electric_state": "PARTIAL",
                      "electric_qualifier": "roughly 61% of the city",
                      "electric_program": "Efficiency Works",
                      "electric_note": "_shared_components.py:562 cites LPC's own statement that it serves 'Longmont, parts of Lyons and Hygiene, and some unincorporated areas' — LPC does not serve every Longmont address. Every Efficiency Works sentence must carry the LPC-customers-only restriction.",
                      "page_slugs": ["index.html","insulation-attic-longmont.html","air-sealing-longmont.html","...42 more"] },
      "Lafayette":  { "gas": "Xcel Energy", "gas_state": "CONFIRMED",
                      "electric": "Xcel Energy", "electric_program": null,
                      "efficiency_works_access": false,
                      "page_slugs": ["insulation-lafayette.html"] },
      "Louisville": { "gas": "Xcel Energy", "gas_state": "CONFIRMED",
                      "electric": "Xcel Energy", "electric_program": null,
                      "efficiency_works_access": false,
                      "page_slugs": ["insulation-louisville.html"] },
      "Niwot":      { "gas": "Xcel Energy", "gas_state": "CONFIRMED",
                      "electric": "Xcel Energy", "electric_program": null,
                      "efficiency_works_access": false,
                      "page_slugs": ["insulation-niwot.html"] }
    },
    "town_count_note": "FOUR area towns, measured: _area_pages.AREA_DATA = ['longmont','lafayette','louisville','niwot']. Erie was DROPPED (card closed as superseded, 3ca991f) and 'Erie' now appears 0 times in public/. _artifact_grep.sh's header comment still says 'Director-locked five: Longmont, Erie, Lafayette, Louisville, Niwot' — a STALE COMMENT in a gate file, recorded not fixed (not this lane's file).",
    "locked_restriction_strings": [
      "but ONLY for electric customers of Longmont Power & Communications, roughly 61% of the city.",
      "applies only to residential electric customers of Longmont Power &amp; Communications"
    ],
    "locked_restriction_reach": "10 + 8 pages, measured in d6e8dab. 'The restriction is not the figure' — it survived the figure strip deliberately.",
    "non_territorial_programs": ["Colorado Energy Office", "ENERGY STAR",
                                 "Boulder County EnergySmart",
                                 "Colorado Weatherization Assistance Program", "HEAR"],
    "territorial_constants": ["ENTITY_DESCRIPTION", "ALIVE_REBATES"],
    "sibling_artifacts_forbidden": ["Lakewood","Arvada","Aurora","Wheat Ridge",
                                    "Centennial","Englewood","Littleton","Westminster",
                                    "Thornton","Park Hill","Washington Park","Highland",
                                    "Golden","Broomfield","Northglenn",
                                    "Greeley","Evans","Windsor","Eaton","Johnstown",
                                    "Milliken","Severance","LaSalle","Ault","Atmos"],
    "elevation_anchor": "4,980",
    "forbidden_elevations": ["5,280","mile high","4,108","4,400","4,432","4,658","4,675"],
    "review_not_fail": ["Weld County"],
    "review_not_fail_reason": "Longmont sits in Boulder County with part of Erie in Weld, so every occurrence must be a deliberate Erie-split disclosure rather than a cloned Greeley reference. _artifact_grep.sh reports it as INFO by design."
  },

  "R3": { "allowed_figures": ["$1.50","$3.00","$3.50","$300","$1,200"],
          "allowed_reason": "Ruling 2 — installed COST rates, not payouts. 8 occurrences total, all inside JS comments in the attic calculator. MEASURED 2026-09-17: $1.50 x3, $3.50 x2, $300 x1, $3.00 x1, $1,200 x1 = 8, and these are the ONLY $ figures anywhere under LGM public/. Was 141 before d6e8dab (133 removed, 8 kept).",
          "allowed_thresholds": ["15%","25%","33%","50%"],
          "allowed_thresholds_reason": "The four Efficiency Works air-sealing tier thresholds — measured reduction a homeowner is tested against, not amounts anyone is paid. Ruling 3." },

  "R4": { "programs": ["Xcel Energy", "Efficiency Works",
                       "Boulder County EnergySmart",
                       "Whole Home Efficiency Bonus",
                       "Colorado Weatherization Assistance Program"],
          "attributed_exception": { "allowed": true,
            "publisher": "Efficiency Works",
            "basis": "ground-truth.md:27-44 — EW's own 'Additional incentives' page has a column headed 'Xcel rebate' beside its own and a 'Total potential incentives' column that is the arithmetic sum (Insulation | $1.16 SF | Up to $1,250 | $3,570; Air sealing | Up to $770 | Up to $1,000 | $1,770). Stacking may be DESCRIBED as published by Efficiency Works, with attribution. It does NOT license the site to author its own combined total.",
            "and_the_figures_are_still_banned": true },
          "retired_prohibition_strings": ["The two programs have separate eligibility and are never combined into one figure.",
                                          "These two programs must NEVER be described as stacking or combining."],
          "retired_prohibition_note": "The first rendered 92 times across 46 pages and was DELETED. Standing instruction: do not restore it in its old wording — 'never combined into one figure' re-ships the prohibition form the Director retracted. The second survives deliberately in _shared_components.py:25-31 as a record." },

  "R5": { "known_uncited": [] },
  "R6": { "label_chains": [],
          "note": "NULL RESULT — no label/figure chain of the R6 shape identified on LGM. The rebate-payback and attic-cost calculators emit figures without severity labels. Registering one later requires only a config entry." },

  "R8": { "reviewed_iso": "2026-08-05",
          "measured_debt": "31 of 48 pages publish 'Last reviewed 2026-08-05'; sitemap shows 27 at 2026-08-05, 15 at 2026-08-11, 3 at 2026-08-07, 2 at 2026-09-01. Content was corrected through 2026-09-10 (d6e8dab), 2026-09-07 (72e18ac, 3cae8aa, cdc3899) and 2026-09-08 (e329db7). This is the same debt GCI closed in bf240f8/348baf9 and DCI holds under D-003.",
          "own_effective_date_pages": ["privacy.html"],
          "self_dated_sources": ["EDU_LASTMOD_BY_FILENAME"] },

  "R11": { "blocking": false, "tracked_terms": [] },

  "draft_gate_retired_note": "RETIRED AND WITHDRAWN 2026-09-21 … (full text in config/lgm.json)"
}
```

**CORRECTION, 2026-09-21 — `draft_gate` IS RETIRED, AND THIS SECTION CARRIED THE
FALSE BLOCK VERBATIM.** Until commit 20b9455 both `config/lgm.json` and this
listing carried, word for word:

```json
  "draft_gate": { "unpublished_pages": ["insulation-rebates-longmont.html",
                                        "insulation-rebate-eligibility-checker-longmont.html",
                                        "insulation-rebate-payback-longmont.html"],
                  "assertion": "absent from public/, absent from sitemap.xml, absent from llms.txt, HTTP 404 live",
                  "note": "Three rebate pages exist as generators + data and are deliberately unpublished. Their generators exit 2 on a public/ target. Any claim gate run must not treat their absence as a gap." }
```

**Every clause of that is false**, measured on LGM at `9dcae1a` on 2026-09-21:
the three pages are **present** in `public/`, **present** in `sitemap.xml`,
**present** in `llms.txt`, and return **HTTP 200** live, not 404; and the
generators no longer `return 2` on a `public/` target, because `ALLOW_PUBLIC =
True` at `_generate_rebate_hub.py:76`, `_generate_rebate_payback.py:79` and
`_generate_rebate_checker.py:77` short-circuits the guard. The Director approved
the copy on 2026-09-20 and the pages were published and verified live on
2026-09-21.

**It was never a reliable record either.** The third filename,
`insulation-rebate-payback-longmont.html` (no `-calculator-`), **has never
existed in LGM**: over a denominator of 296 commits across all refs and 219
distinct paths ever touched, `grep -F 'insulation-rebate'` over those 219 paths
returns exactly 3, and that name is not one of them. The block was wrong from
the day it was written, 2026-09-17, while its premise still held.

**Why nothing caught it, and what changed.** `draft_gate` sat in
`claim_gate.py`'s `DATA` tuple — the set of config containers the gate's own
dead-config audit (§"CONFIG KEYS READ BY NO CODE PATH") treats as inert data.
That made its children unauditable and, because the tuple's entries are string
literals in `claim_gate.py`, made the key itself count as *read*. A config key
asserting a falsifiable fact about the corpus therefore had nothing able to
falsify it. `draft_gate` has been **removed from `DATA`**, and the standing rule
is now recorded in the code beside the tuple: a key that can make a falsifiable
claim about the corpus must be read by code that can falsify it, or named with a
`_DOC_PREFIXES` suffix so the audit reads it as documentation, or declared in
`documentation_only_keys` with a checkable justification. The retirement was
taken as **documentation, not as a replacement rule**: LGM now has no unpublished
pages, so a checkable successor would be a rule configured with an empty input
set — the blind-rule condition the audit already reports as CONFIG KEYS READ BY
CODE BUT EMPTY. The live check that the three pages are present is `min_artifacts`
(62) and `expected_html` (51), both raised for this publication in `6e4c939`.

### 10.4 GCI — `config/gci.json`

```json
{
  "key": "gci",
  "repo": "greeleycoloradoinsulation.com",
  "domain": "https://greeleycoloradoinsulation.com",
  "measured_at": { "date": "2026-09-17", "head": "d9ebab7" },
  "min_artifacts": 49,
  "expected_html": 38,
  "embed_artifacts": [],
  "embed_artifacts_note": "NULL RESULT — GCI has no embed frame.",
  "key_files_excluded": ["public/d38d3ab74418efeba995b5fab6345f07.txt"],
  "svg_readable": ["public/favicon.svg", "public/logo.svg", "public/og-image.svg"],
  "og_image_raster_only": false,
  "og_image_source": "_brand_build/og-image.mvg via _generate_brand_assets.py (OG_FOOTER)",
  "og_image_history": "e6cb44e changed OG_FOOTER from 'Atmos rebates explained' to 'Rebates explained'. og-image.png/svg are referenced by og:image and twitter:image on EVERY page including the three Xcel-gas towns, so this asset is a territorial claim surface.",
  "gates_present": ["regen_all.sh", "_postbuild_check.py", "_check_links.py",
                    "_intra_similarity_check.py", "_validators.py",
                    "_similarity_check.py", "_artifact_grep.sh",
                    "_svc_pending_import_check.py",
                    "ops/similarity_canary.sh", "ops/functional_proof.sh",
                    "ops/live_token_check.sh"],
  "gates_absent": ["_out_guard.py"],
  "reviewed_iso": "2026-09-09",
  "static_page_reviewed_iso": "2026-08-05",
  "atomic_answer_band": [54, 60],
  "atomic_answer_note": "sc.atomic_answer_html() enforces a hard 54-60 word band by RAISING.",

  "R2": {
    "market": "Greeley and the Weld County corridor",
    "gas_structure": "SPLIT THREE WAYS. There is no single gas utility for this service area.",
    "electric_structure": "UNRESOLVED for Greeley; UNKNOWN for LaSalle and Ault; split by address in Windsor and Severance; three-way in Johnstown; split by named subdivision in Milliken.",
    "forbid_electric_utility_naming": true,
    "forbid_electric_reason": "Absolute rule: no page names a residential electric utility for any AREA_PAGES town. GCI bf240f8 (3) found MILLIKEN_GAS_XCEL rendering the verbatim quotation 'Xcel Energy provides gas and electricity for most of Milliken', which breaks it. Not a formality: the same source page names Poudre Valley REA for Mad Russian and Mill Iron, so 'most of' does not resolve the electric split. The entry now paraphrases with quote=False. Live check: 0 occurrences of 'electricity' on the Milliken page, and 0 sentences site-wide naming a utility alongside 'electric' on any of the nine town pages.",
    "territory_note": "docs/board/ground-truth.md:5-29, landed 2026-09-08 in 5f9698b. It SUPERSEDES the position that stood until that day, which read '- **Gas utility: Atmos Energy.**' and framed the nine towns as 'unevenly confirmed' Atmos. That premise was formed once at genesis from a source naming Weld County and three towns, silently generalised to nine, and never tested against the utility's own territory filing. It survived TWO YEARS because every rebate pass verified the PROGRAM and none verified the TERRITORY.",
    "towns": {
      "Greeley":   { "gas": "Atmos Energy", "gas_state": "CONFIRMED", "gas_qualifier": "",
                     "electric": "UNRESOLVED", "page_slugs": ["insulation-greeley.html","index.html"],
                     "corollary": "'Atmos is the gas utility in Greeley' is CONFIRMED but NOT EXCLUSIVE." },
      "Evans":     { "gas": "Atmos Energy", "gas_state": "CONFIRMED", "gas_qualifier": "",
                     "electric": "UNRESOLVED", "page_slugs": ["insulation-evans.html"] },
      "Eaton":     { "gas": "Atmos Energy", "gas_state": "CONFIRMED", "gas_qualifier": "",
                     "electric": "UNRESOLVED", "page_slugs": ["insulation-eaton.html"] },
      "Windsor":   { "gas": "Atmos Energy", "gas_state": "HEDGED",
                     "electric": "SPLIT BY ADDRESS", "page_slugs": ["insulation-windsor.html"] },
      "LaSalle":   { "gas": "Atmos Energy", "gas_state": "HEDGED",
                     "electric": "UNKNOWN", "page_slugs": ["insulation-lasalle.html"],
                     "spelling_variants": ["LaSalle", "La Salle"] },
      "Ault":      { "gas": "Atmos Energy", "gas_state": "HEDGED",
                     "electric": "UNKNOWN", "page_slugs": ["insulation-ault.html"],
                     "substring_trap": "grep -ci 'ault' gives 8; the locality appears once. Use -w and matching case." },
      "Johnstown": { "gas": "Xcel Energy", "gas_state": "CONFIRMED", "gas_qualifier": "",
                     "gas_qualifier_rule": "NONE. Its source states Xcel for gas flatly. NEVER INVENT A QUALIFIER FOR JOHNSTOWN.",
                     "source": "https://johnstownco.gov/510/Utility-Service-Providers — table row 'Natural Gas | Xcel Energy | 1-800-895-1999'. The 'most of' hedge on that page sits on the Electric Service row above it, not on gas.",
                     "electric": "THREE-WAY SPLIT (Xcel / United Power / PVREA)",
                     "page_slugs": ["insulation-johnstown.html"] },
      "Milliken":  { "gas": "Xcel Energy", "gas_state": "CONFIRMED",
                     "gas_qualifier": "most of Milliken",
                     "source": "https://www.millikenco.gov/246/New-Residents",
                     "electric": "SPLIT BY NAMED SUBDIVISION (PVREA for Mad Russian and Mill Iron)",
                     "page_slugs": ["insulation-milliken.html"] },
      "Severance": { "gas": "Xcel Energy", "gas_state": "CONFIRMED",
                     "gas_qualifier": "most locations in Severance",
                     "source": "https://www.townofseverance.org/265/Natural-Gas — 'Natural gas services are supplied by Xcel for most locations in Severance.'",
                     "electric": "SPLIT BY ADDRESS",
                     "page_slugs": ["insulation-severance.html"] }
    },
    "hedge_rule": "Do NOT promote Windsor/LaSalle/Ault to unconditional Atmos language. They ARE named in Atmos's current Colorado tariff, so Atmos SERVES them; the tariff does not establish EXCLUSIVITY. A tariff is authority for PRESENCE, never for EXCLUSIVITY. ATMOS_CONFIRMED_TOWNS stays at three towns.",
    "hedge_pairs": [["Where Atmos Energy serves the home", "<explicit non-confirmation close>"]],
    "hedge_pairs_note": "BOTH halves load-bearing. Removing a figure is never a licence to upgrade a conditional.",
    "tariff_identity": { "document": "Colo. P.U.C. No. 7 Gas, Third Revised Sheets 3 and 4",
                         "advice_letter": "No. 647",
                         "issued": "2026-08-12", "effective": "2026-08-17",
                         "sha256": "c9aed9b4ac73448f1c0223efe3ed9800e1e65bb85d3c1ef3e4897427b5c0bffc",
                         "bytes": 1898937,
                         "pages": 139,
                         "pages_note": "139, confirmed four ways: pdfinfo 'Pages: 139'; 139 /Type /Page objects; 139 pdftotext -layout form-feeds; 139 plain form-feeds; and the linearization dictionary carries /N 139. It was recorded as 132 in four files and that was NEVER COUNTED.",
                         "weld_localities": ["Ault","Eaton","Evans","Fort Lupton*","Garden City","Gilcrest","Greeley","Hudson","Keenesburg","Kersey","La Salle","Lucerne*","Nunn","Platteville","Pierce","Prospect Valley*","Roggen*","Windsor"],
                         "weld_localities_count": 18,
                         "weld_note": "EIGHTEEN, not six. The six previously recorded are the six OF THIS SITE'S NINE TOWNS that appear — a materially different statement. * = the tariff's own footnote 1, 'Unincorporated Communities'. The list is alphabetical WITH ONE LOCAL INVERSION: Platteville is printed before Pierce.",
                         "extraction": "pdftotext -layout (-layout specifically, because the table is two-column)",
                         "extraction_traps": ["textutil -convert txt does NOT extract this PDF — output begins %PDF-1.6 — and reports all nine towns absent INCLUDING the six provably present",
                                              "strings fails identically (zero hits for Greeley)",
                                              "pypdf/PyPDF2/pdfminer/PyMuPDF reported failing; none installed here; recorded as reported, not verified"],
                         "null_result_reasoning": "Johnstown, Milliken and Severance appear ZERO times in both extraction modes. What makes that evidence rather than a failed search: each missing town falls inside a printed alphabetical gap (Hudson -> Keenesburg, Meeker -> Milner, Salida -> Springfield) whose neighbours on BOTH sides extracted cleanly, so the extractor was working exactly where the town would have been.",
                         "the_one_command_control": "Search for a term you KNOW is present before trusting a term you believe is absent. Greeley IS in that tariff, so any pipeline that cannot find Greeley cannot establish that Johnstown is missing.",
                         "do_not_cite": ["Advice Letter No. 544"],
                         "do_not_cite_reason": "It governs the superseded Second Revised Sheets. Cite No. 647 or cite nothing.",
                         "grep_note": "Grep as 'No. 647', not 'Advice Letter No. 647' — the phrase wraps a line break in the state documents and the full-phrase grep returns a false 0." },
    "known_disclosure_gaps": ["Every sitewide gas-split sentence reads 'Atmos Energy in Greeley, Evans and Eaton' against 'Xcel Energy in Johnstown, for most of Milliken, and for most locations in Severance'. THREE OF NINE TOWNS APPEAR IN NEITHER LIST, so a Windsor, LaSalle or Ault reader on their own town page sees a split that omits their town. This is a direct consequence of the presence-not-exclusivity ruling. The Director has been told and is NOT reversing it. Do not file it as a defect."],
    "non_territorial_programs": ["Colorado Weatherization Assistance Program",
                                 "Colorado Energy Office", "Energy Outreach Colorado",
                                 "ENERGY STAR", "DRCOG"],
    "territorial_constants": ["REBATE_ACKNOWLEDGMENT", "THANK_YOU_BODY",
                              "ENTITY_DESCRIPTION", "GAS_UTILITY_SPLIT_FACT",
                              "ATMOS_CONFIRMED_TOWNS", "XCEL_GAS_TOWNS"],
    "gas_utility_split_fact": "Which gas utility runs the insulation rebate depends on your town: Atmos Energy is the natural gas utility in Greeley, Evans and Eaton, while Xcel Energy is the natural gas utility in Johnstown, for most of Milliken, and for most locations in Severance.",
    "sibling_artifacts_forbidden": ["Lakewood","Arvada","Aurora","Wheat Ridge",
                                    "Centennial","Englewood","Littleton","Westminster",
                                    "Thornton","Park Hill","Washington Park","Highland",
                                    "Golden","Broomfield","Northglenn",
                                    "Longmont","Erie","Lafayette","Louisville","Niwot",
                                    "Longmont Power & Communications","Efficiency Works"],
    "elevation_anchor": "4,108",
    "allowlist": ["DRCOG"],
    "allowlist_note": "Director-granted. GCI is the only property with one."
  },

  "R3": { "allowed_figures": ["$70,000","$99,920"],
          "allowed_reason": "STANDING EXCEPTION. Director ruling 2026-09-10 (the SECOND ruling), restored in 25cb16b after 2cecf33 stripped them. Colorado Weatherization Assistance Program income-eligibility limits: $70,000 for a single-person Weld County household, $99,920 for a household of four. They are eligibility thresholds for a FREE, income-qualified government program, not per-measure rebate amounts. Verified first-party TWICE, independently, against the Colorado Energy Office's WAP income-eligibility Google Sheet (CSV export, Weld row verbatim: Weld,\"$70,000\",\"$79,920\",\"$90,000\",\"$99,920\",\"$107,920\"). The chart prints NO effective date or fiscal year (grep for effective|FY|fiscal|updated|20[0-9][0-9] over all 64 rows: RAW 0, no filter applied), so copy says 'checked September 10, 2026' and never 'FFY2026 figures'.",
          "allowed_occurrences": { "$70,000": 10, "$99,920": 10 },
          "allowed_occurrences_note": "MEASURED 2026-09-17: exactly 20 occurrences, and these are the ONLY $ figures anywhere under GCI public/. Was 206 before 2cecf33 ($1,550 x77, $575 x49, $1,325 x19, $1,075 x18, $1,150 x11, $70,000 x10, $99,920 x10, $663 x6, $125 x6).",
          "known_figures": ["1550","1075","1325","1150","663","125","575","70000","99920"],
          "bare_numeral_gate": "/usr/bin/grep -rnoE '\\b(1550|1075|1325|1150|663|125|575|70000|99920)\\b' public/ ... | grep -iE 'atmos|rebate|cap|rate|incentive|wap|weatheriz|pays'  -> 0. Installed in f0203ad because the $-anchored gate structurally cannot catch a bare-digit cap.",
          "allowed_structure_percentages": ["75%","50%","30%","100% of project cost"],
          "detector_machinery_deleted": ["ATMOS_REBATE_AMOUNTS","REBATE_VERIFICATION_NOTE","rebate_note_section_html()","WAP_INCOME_FIGURES","WAP_VERIFICATION_NOTE","wap_note_section_html()","CAP","RATE","money()"],
          "detector_note": "These were DETECTORS, not sources — tuples scanned against BUILT HTML (including inlined calculator JS) to inject a verification note. With the amounts gone they matched nothing and the note vanished from every page. Deleted rather than left inert (Rule 2). DO NOT RESURRECT: the note asserted the limits were checked in REBATE_VERIFIED_DATE (August 2026), which is OLDER than the actual 2026-09-10 verification, and its detector produced spurious notes on pages carrying no amount." },

  "R4": { "programs": ["Atmos Energy", "Xcel Energy",
                       "Colorado Weatherization Assistance Program",
                       "Energy Outreach Colorado CARE",
                       "Whole Home Efficiency Bonus", "DRCOG"],
          "noun_use_constants": ["REBATE_ACKNOWLEDGMENT"],
          "noun_use_note": "REBATE_ACKNOWLEDGMENT renders on 35 pages and is locked verbatim. It read 'the primary insulation rebate stack in Greeley, Evans and Eaton'; f0203ad KEPT it with the reasoning recorded in-source and FLAGGED IT TO THE DIRECTOR, noting 'the fix, if the ruling is read to cover the word rather than the claim, is one word'. The Director then ruled: 38b80e0 changed 'rebate stack' to 'rebate programs'." },

  "R5": { "known_uncited": [],
          "note": "MEASURED 2026-09-17: '15% reduction' returns 0 occurrences in GCI public/." },
  "R6": { "label_chains": [],
          "note": "NULL RESULT — no severity-label chain remains. e6cb44e made the four calculators' verdicts utility-neutral, naming no payer and carrying no amount, and deleted CAP/RATE/money() once the amounts left. A new tool with a severity label needs a config entry." },

  "R8": { "reviewed_iso": "2026-09-09",
          "static_page_constant": "STATIC_PAGE_REVIEWED_ISO",
          "static_page_value": "2026-08-05",
          "pinned_pages": { "about.html": { "reason": "visible text did not change — JSON-LD only — so 2026-08-07 remains its true content date and its footer stays pinned at 2026-08-05; neither value is false and the 2-day divergence is pre-existing", "expected_sitemap": "2026-08-07", "expected_footer": "2026-08-05" },
                            "404.html": { "reason": "schema-only change; pinned" } },
          "own_effective_date_pages": ["privacy.html"],
          "own_effective_date_values": { "privacy.html": "2026-08-30" },
          "self_dated_sources": ["EDU_LASTMOD_BY_FILENAME","MODIFIED_XCEL_GAS_CORRECTION"],
          "modified_xcel_gas_correction": "2026-09-09",
          "bump_rule": "MEASURE BEFORE BUMPING. Batch-stamping is forbidden. bf240f8 measured 35 of 38 pages changed visibly, 2 changed only in JSON-LD (pinned), 1 byte-identical. 348baf9 then reversed its own round-2 argument on evidence: lastmod equals the page's REAL CONTENT-REVIEW date, not its article-body-edit date. Result: 35 of 37 sitemap URLs at 2026-09-09.",
          "d007_note": "_generate_sitemap.py's D-007 hardcode is a PORT-PARITY justification, not a truth justification. Matching a sibling property's number is a fine way to choose between two dates that are both true, and never a reason to publish a date the page did not earn. Where parity and accuracy conflict, PARITY LOSES." },

  "R11": { "blocking": false, "tracked_terms": [] }
}
```

---

## 11. THE DEFECT INVENTORY — WHAT THE GATE IS SCORED AGAINST

Every defect this retrieval found from 2026-09-01 to 2026-09-17, one line each,
with the repo and the commit or lane row it was found in. Sourced from all four
repos' `docs/lanes.md`, all four `docs/board/done/`, all four
`docs/board/ground-truth.md`, and `git log --oneline --since=2026-09-01` (canon
77 commits, DCI 113, LGM 128, GCI 129). The `Rule` column is the rule that must
catch it; `—` means no rule here catches it and the reason is in that rule's
"does not catch" section or in §7.

### 11.1 The eight the brief named

| # | Rule | Repo | Defect | Found in |
|---|---|---|---|---|
| 1 | R1 | LGM | `CITED_SOURCES['XCEL_BLOWER_DOOR']` attributed a 20% CFM50 requirement to Xcel's **insulation** rebates **inside quotation marks** on **11 pages**; the cited 2024 sheet scopes it to air sealing alone and never uses "blower door" against those standards | `186d311` (claim `8b0f1a9`, release `d64c8a1`), lane `lgm-rebate-defect-repair-r5b` |
| 2 | R2 | GCI | **Johnstown, Milliken and Severance credited to Atmos for two years.** They are Xcel gas. Premise formed once at genesis from a source naming three towns, generalised to nine, never tested against the utility's own tariff | `e6cb44e` (release `a51046e`), lane `gci-xcel-gas-towns-correct`; canon `f1c4008` |
| 3 | R7 | DCI | The retired WHE audit entry path — "Home Energy Squad Plus visit" — published as current on **35 pages**, sourced to the superseded 2024 sheet, which the current CO sheet † drops entirely | `b47a3c2`, lane `xcel-25-12-215-figures-dci` |
| 4 | R5+R7 | DCI | A **fifth Xcel program with four invented eligibility pathways on 72-73 pages**: "LEAP, SNAP, or TANF participation… or living in a disproportionately impacted community — that last pathway is geographic, with no income paperwork." 0 cited-stats, 0 outbound links, 0 registry entries in any repo | `3da02df`, lane `xcel-25-12-215-figures-dci` |
| 5 | R3 | all three | **537 rebate dollar figures the Director ruled off** (canon's addendum states 545; the 8-figure difference is unresolved and recorded as such): DCI **198**, GCI **206**, LGM **133 removed / 8 kept** | DCI `5703f8c`; GCI `2cecf33`; LGM `d6e8dab` |
| 6 | R6 | DCI | The r-value calculator **printed two different severity words beside the same percentage** — 2 ambiguous percentages (37% and 100%), **15 of 140** combinations reading "Moderately under code — 100% short of target", 351 ordinal inversions, 43 label-vs-figure mismatches | `37c7b29` (release `f9e7551`), lane `dci-d3-tier-label-fix` |
| 7 | R7 | GCI | **A LIVE CUSTOMER-FACING FALSE CLAIM**: `insulation-rebate-hub.html` told readers "the newest rebate schedule that could be retrieved is effective January 1, 2024" — precisely the sheet that same pass had hash-proved superseded. Identical proposition **twice more** on `insulation-rebate-eligibility-checker.html` (prose + inline JS), found only on a claim-shaped re-sweep | `44d638c` (release `44cb7f5`), lane `xcel-25-12-215-refpoint-gci` |
| 8 | R8 | GCI | **35 pages materially changed and still declared 2026-08-05**, telling crawlers the wrong-utility correction never happened; then **11 self-dated pages bypassed the sitewide constant** and `contact.html` published two contradictory dates 33 days apart with the crawler-facing one false | `bf240f8`, then `348baf9`, lane `gci-xcel-gas-towns-correct` rounds 2 and 3 |

### 11.2 Everything else, by rule

**R1 — fabricated quotation**

| Rule | Repo | Defect | Found in |
|---|---|---|---|
| R1 | LGM | The garage page **labelled a paraphrase "verbatim"** and attributed an exclusion list to a sheet that has none | `3cae8aa` D3, lane `blower-door-adversarial-fixes-lgm` |
| R1 | GCI | **Two figures lived in `CITED_SOURCES` and rendered as attributed verbatim quotations inside typographic quote marks.** "A figure cannot be deleted from inside a quotation while the quote marks stay — that fabricates a quotation, a worse defect than the one being fixed." Both rewritten as paraphrases with `quote=False` | `2cecf33` |
| R1 | LGM | **Three quotations, same class**: `EFFICIENCY_WORKS_INSULATION_REBATE` (19 pages), `EFFICIENCY_WORKS_AIR_SEALING`, `BOULDER_COUNTY_ENERGYSMART`, all rendering dollar figures as EW's own words | `d6e8dab` |
| R1 | GCI | `MILLIKEN_GAS_XCEL` rendered the verbatim quotation "Xcel Energy provides gas and electricity for most of Milliken", **naming a residential electric utility**, and quoting only the gas half would have been selective misquotation | `bf240f8` (3) |
| — | LGM | The garage exclusion quotation became exact and then **stopped mid-sentence at a comma with a bare closing quote**, so a partial list read as the whole clause. R1 cannot see a missing ellipsis | `cdc3899` N1, lane `blower-door-quote-boundary-lgm` |
| R1 | DCI | `quote=False` "was added to five entries and **read by NOTHING**; the quotes were emitted unconditionally, so the correction shipped invisible" | lane `xcel-25-12-215-figures-dci`; `_shared_components.py` comment |

**R2 — wrong-utility claim**

| Rule | Repo | Defect | Found in |
|---|---|---|---|
| R2 | GCI | `REBATE_ACKNOWLEDGMENT` + `THANK_YOU_BODY` on **35 pages** told a Severance homeowner, after they submitted the lead form, to "ask who files the **Atmos** paperwork" | `e6cb44e` |
| R2 | GCI | **The shared og-image said "Atmos rebates explained"** and was referenced by `og:image`/`twitter:image` on **every page including the three Xcel towns** | `e6cb44e` |
| R2 | GCI | `ENTITY_DESCRIPTION` and **both `knowsAbout` lists** carried Atmos attribution on a JSON-LD node whose `areaServed` lists all nine towns | `e6cb44e` |
| R2 | GCI | **Three calculators returned an Atmos-attributed verdict computed from build era and R-value alone, never asking the visitor's town** | `e6cb44e` |
| R2+R3 | GCI | **THE FOURTH TOWN-BLIND CALCULATOR WAS NEVER SWEPT.** `insulation-payback-calculator-greeley.html` still carried "the sealing work carries its own flat $575 Atmos rebate" in the JS verdict **on every click**, a quick fact, body prose and a FAQ answer — and the fixing commit had written an invariant into source claiming all verdicts named no payer, **which was false on the live site.** Its H1 is the only one of five without "Greeley", so the Greeley-scoping argument did not reach it, and its only visible Xcel text sat inside `<div class="thank-you">`, which the served CSS hides | `bf240f8` (1) |
| R2 | GCI | Three towns' `cite_keys` carried `ATMOS_AIR_SEALING_REBATE` / `ATMOS_ATTIC_REBATE` | `e6cb44e` |
| R2 | canon | **`docs/board/ground-truth.md:9-12` STILL SAYS "Greeley (Atmos gas, electric unresolved)"** — stale since 2026-09-08, nine days. Canon's own settled-decisions file, which `CLAUDE.md` mandates reading in full every session, still carries the single-utility premise the portfolio spent three rounds retiring. **Recorded, not reconciled — canon's ground-truth is not this lane's file** | measured 2026-09-17, `/usr/bin/grep -n` on canon `docs/board/ground-truth.md` |
| — | LGM | `_artifact_grep.sh`'s header comment still names "this property's **Director-locked five**: Longmont, **Erie**, Lafayette, Louisville, Niwot" when `_area_pages.AREA_DATA` has **four** and `Erie` appears **0 times** in `public/`. A stale comment in a gate file | measured 2026-09-17; card closed in `3ca991f` |

**R3 — rebate dollar figure**

| Rule | Repo | Defect | Found in |
|---|---|---|---|
| R3 | GCI | **A rebate cap shipped live inside the JS comment documenting its own removal** — `// CAP/RATE (1550 / 0.75)` — inlined into a live 200 page, in view-source, in what LLM crawlers read. It carried no `$`, "which is exactly why the `$`-anchored acceptance gate could not see it" | `f0203ad` D1; canon `a891b83` |
| R3 | GCI | **"the largest rebate" — a rank claim with no `cap` and no numeral, live on six pages** (`_generate_service_pages.py` `CROSS_CONTEXT['attic']`). Plus "the published per-measure amounts drop to a small fraction of the figures usually quoted", three "the attic cap is the larger of the two" comparatives, and "the smallest cap in its residential program" — **which the lane's own first pass introduced as a fix for a figure** | `a91dfd4` D5 |
| R3 | DCI | `$600` Combo Bonus in `Organization.knowsAbout` JSON-LD on ~71 pages; "the prose cap sweep never looked at JSON-LD" | C4, `81f4bca` |
| R3 | DCI | Three figure sites R1's inventory missed: `_generate_service_pages.py` 1121, 1141, 1611 | `5703f8c` |
| R3 | GCI | **An entire live data module never listed** — `_area_pages.py`, 17 live figures across six town pages | `2cecf33`; canon `a891b83` |
| R3 | LGM | Four figure sites unlisted; three pages had seven surfaces where the inventory said six | `d6e8dab`; canon `a891b83` |
| R3 | LGM | `spray-foam-vs-blown-in-comparator` carried `$1.16` and `$0.77` **although neither string appears anywhere in that page's generator** — inherited via a shared `CITED_SOURCES` key in `cite_keys` | canon `a891b83` |
| R3 | GCI | `ATMOS_REBATE_AMOUNTS` and `WAP_INCOME_FIGURES` were **detectors, not sources** — tuples scanned against built HTML to inject a verification note; with the amounts gone the note vanished from every page | `2cecf33` |
| R3 | GCI | 15 orphaned "This figure was verified in August 2026 against the Atmos rebate page" sentences | `2cecf33` |
| R3 | GCI | A first fix attempt **left the superseded amount inside a JS comment**, which ships because the JS is inlined, and that made `rebate_note_section_html()` inject an "Atmos rebate amounts verified" note onto a page that no longer quotes an amount | `bf240f8` |
| R3 | GCI | A mangled artifact from the lane's own mechanical pass: **"rebated at 75% up to 75% of cost"** | `a91dfd4` |
| R3 | DCI | `COPY_VOICE.md`'s "Required references to preserve" list **literally required the `$600` string** and would have re-seeded the figure on 72 pages | `5703f8c` |
| R3 | LGM | Tier 2 figures on 8 pages: `$15–$60 per measure` on 4 area pages, `$60 for attic, $25 for wall` on 4 measure pages | `58646f0` |
| — | GCI | **A Director ruling over-applied**: the strip removed the two Colorado WAP income-eligibility limits, which are not rebate amounts. "Stripping them did not remove a liability, it removed the answer." Restored after first-party verification twice | `25cb16b`, Director ruling 2026-09-10 |

**R4 — stacking assertion or denial**

| Rule | Repo | Defect | Found in |
|---|---|---|---|
| R4 | DCI | A commit titled "neutralize Xcel-side stacking claims" **left the class standing on 70 of 72 live pages, including one sentence after an edit it had just made** | `fca41f6`, refuted by an adversarial reader with `/usr/bin/grep` |
| R4 | DCI | **`layer` was ON THE SEARCH LIST and "the Whole Home Efficiency Bonus layers on top" shipped anyway.** 15 further instances closed on a third sweep, including "so you can stack rebates instead of leaving money on the table", "Xcel adds a 25% bonus on top of the standard rebates", "Bundling … unlocks the … Bonus", "One add-on sits on top" | `b47a3c2`, then `31484f1` |
| R4 | DCI | The WHE page `<h1>` "How Do I **Stack** the Whole Home Efficiency Bonus **on Top of** Standard Rebates?" — simultaneously `h1`, `og:title`, `twitter:title`, breadcrumb leaf and Article `headline`: **one string carrying the assertion into five surfaces** | `5350403` |
| R4 | DCI | The nav/tile label "WHE Bonus **Stacking**" still carried the proposition in site voice **after the page itself had been retitled** | `31484f1` |
| R4 | DCI | 9 neutralised across 4 generators: the federal 25C denial, the DRCOG Power Ahead assertion + quick fact, the City of Golden claim ×2, "layer the Xcel IQ Program on top" ×4, and two homepage assertions. **The first sweep caught only the Golden instance** | `fca41f6` |
| R4 | GCI | **A stacking DENIAL served as schema.org FAQPage** — "Can I stack these programs?" answered "Not in the way people usually hope", shipped in the rebate hub's JSON-LD **as this site's stated position.** Plus knob-and-tube's "not with rebate stacking" | `f0203ad` D3 |
| R4 | LGM | **An affirmative stacking DENIAL on the knob-and-tube page** | `58646f0` |
| R4 | LGM | The retired prohibition sentence "The two programs have separate eligibility and are never combined into one figure" had rendered **92 times across 46 pages** | lane `hub-copy-citations-lgm` / ground-truth |
| R4 | DCI | **`llms.txt` carried "Xcel rebate-stack eligibility", site voice, unattributed — present in EVERY commit including the pre-pass baseline.** It survived five stacking sweeps and ten adversarial reads because every corpus enumerated `sitemap.xml`. Its source string was split across Python concatenation, so it matched the `.pyc` and not the `.py` | `fb08735` |

**R5 — uncited statistic**

| Rule | Repo | Defect | Found in |
|---|---|---|---|
| **R5** | **DCI** | **LIVE NOW: "15% reduction in heating and cooling costs", uncited, 2 occurrences — `public/r-value-needed-calculator.html:1570` and `public/do-i-need-new-insulation-quiz.html:1502`, from `_generate_calculator_pages.py:453` and `:1102`.** Both inside JS string literals. Its audience **grew from 33 to 54 input combinations** when the D3 fix shipped | measured 2026-09-17; flagged in lane `dci-d3-tier-label-fix` 2026-09-11; related removal from the embed frame in `92f3887` D8 |
| R5 | DCI | The embed frame shipped **1,131 dead bytes** to third-party domains carrying "Whole Home Efficiency Bonus", "15% reduction" and "Xcel" — "a named utility rebate programme and an uncited savings percentage that every LLM crawler fetching the frame would read" | `92f3887` D8 |
| R5 | DCI | "Xcel's 2026 rebate programs … pays out per measure" and "the Whole Home Efficiency Bonus **wants multiple qualifying measures**" — a vague restatement of a condition the sheet states precisely | `f83d421` |

**R6 — self-contradicting output**: the D3 instance (§11.1 #6) is the only one. Four defects in the same calculator remain **open and deliberately untouched**: `wall-new`'s target names one compliant path where the prose names three; `wall-existing` frames a market observation as what code "calls for"; `targetRec` is dead (7 definitions, 0 reads, in generator and live page); three `<label>`s lack `for`.

**R7 — superseded-source claim**

| Rule | Repo | Defect | Found in |
|---|---|---|---|
| R7 | LGM | **A SUPERSEDED RULE WEARING A LIVE CITATION.** `insulation-lafayette.html` told a homeowner, in prose AND in JSON-LD, that "**Xcel's own rebate summary** sets three conditions" — all three verbatim from the superseded 2024 sheet, none in the current CO sheet †. "Worse than an unsourced claim — a retired rule citing the current document as its authority, telling a Lafayette homeowner to buy an audit no longer required" | `72e18ac` |
| R7 | LGM | Same class, second instance, **found by reading for the proposition rather than the string**: `air-sealing-longmont.html` called air sealing "a **prerequisite** for Xcel's Whole Home Efficiency bonus". **It matched none of the eight swept strings** | `72e18ac` |
| R7 | DCI | **`prerequisite` is the exact word removed from LGM in round 3 and it was never swept on DCI.** 11 live instances of the retired rule on 3 pages, incl. `<title>`+`og:title`+`twitter:title` as one string, a FAQ in both prose and JSON-LD `acceptedAnswer`, "the **Xcel-approved** audit" (a category the sheet does not define), and a **wrong clock** — "within two years of **the audit**" on a page stating "of enrolling" correctly twice elsewhere | `eb5c939` |
| R7 | DCI | "installed and invoiced by **December 31, 2026**" on **38 pages**, in no Xcel artifact retrieved. Then `Dec. 31, 2026` at `_generate_calculator_pages.py:344` **read clean for four rounds because every sweep searched the long form** | `b47a3c2`, then `f83d421` |
| R7 | DCI | The payout-timing claim, removed in prose, **alive in a FAQ and its JSON-LD `acceptedAnswer`, attributed to "Xcel's page", which does not say it.** The current CO sheet † publishes no payout schedule at all | `b47a3c2`, then `f83d421` |
| R7 | DCI | "25% of the rebate already paid" on **41 pages** (current sheet: "a 25% bonus on all standard rebates"); "three or more measures are bundled" dropping the binding clock | `b47a3c2` |
| R7 | DCI | "completed **in one project**", narrower than the source and materially misleading — it tells a homeowner spreading three measures over eighteen months they do not qualify, when the sheet says they do | `eb5c939` |
| R7 | LGM | **"the multiplier is expired"** — the current CO sheet † **reinstates** the 1.5× gas-heat bonus through 2026 ("Invoice must be dated in 2025 or 2026"). The earlier supersession note missed it because it enumerated only **two** customer groups and the sheet has **three**. 4 live instances | `a2ba5a6` |
| R7 | LGM | An **unrestricted universal negative in 8 places** — "neither Xcel nor Efficiency Works publishes a dollar figure for the audit" — refuted by the current CO sheet †'s own `HOME ENERGY AUDIT` / `REBATE AMOUNT` table | `58646f0` |
| R7 | LGM | Seven stale `24-02-205` claims across `_generate_area_pages.py`, an open Director card, `STATE_OF_PROJECT.md` ×2, `WEBSITE_ARCHITECTURE.md`, and a done card whose polarity was inverted | `858bb26` |
| R7 | LGM | `llms.txt`'s tile description **asserted the conflation and denied it in the same sentence** — and it was a half-fix of the same lane's own commit `58646f0` | `e329db7` |
| R7 | all four | `24-02-205`/`24_02_205`/`23-11-205` census: canon 3 hits, **DCI 62**, **LGM 64**, GCI 3 — 9 live defects | canon `087a3be`, lane `xcel-25-12-215-registry-canon` |
| R7 | GCI | The done card `lgm-r49-r60-harmonize.md` carried a **live forward-looking instruction** to go quote a superseded edition | `71e9217` |

**R8 — stale review date**

| Rule | Repo | Defect | Found in |
|---|---|---|---|
| **R8** | **DCI** | **LIVE NOW: 70 of 75 pages publish "Last reviewed 2026-08-24" and 70 sitemap URLs say `lastmod 2026-08-24`, after eleven rounds of Xcel-claim corrections (09-07), a 198-figure strip (09-10) and the tier-label fix (09-11).** The lane measured the debt at **70 of 72 pages** and recorded that D-003 and an Auditor HOLD still govern because no per-page date machinery exists. One page publishes **2026-05-05** | measured 2026-09-17; debt recorded in lane `xcel-25-12-215-figures-dci` |
| **R8** | **LGM** | **LIVE NOW: 31 of 48 pages publish "Last reviewed 2026-08-05"**, after blower-door corrections on 26 pages (09-07), a superseded-eligibility-rule fix (09-07), an `llms.txt` fix (09-08) and a 133-figure strip (09-10). `REVIEWED_ISO` is still `2026-08-05` | measured 2026-09-17 |
| R8 | DCI | The embed-code page claimed review on `2026-08-24`, **17 days before the page existed** | `92f3887` D6 |
| R8 | GCI | `contact.html` published **two contradictory dates 33 days apart, and the crawler-facing one was the false one**, under a port-parity hardcode | `348baf9` |

**R9 — internal contradiction (added)**

| Rule | Repo | Defect | Found in |
|---|---|---|---|
| **R9** | **DCI** | **LIVE NOW: `llms.txt` says the 20% CFM50 reduction is what "Xcel insulation and air sealing rebates require" while `air-sealing.html`, citing the same document, says "the insulation rebates are qualified by post-job R-value, not by leakage reduction."** DCI's own ground-truth settles it against the llms.txt version. And `before and after the work` still renders on **13 files / 21 occurrences** on DCI, attributed to a sheet in which "before and after" occurs **zero** times — LGM swept this exact class in `124c014` (12 files / 17 occurrences) and **DCI was never swept** | measured 2026-09-17; class established first-party in LGM `183378f`; DCI ground-truth:148-152 |
| R9 | DCI | The WHE page's `h2` asserted the retired audit rule and **the very next sentence denied it**. "Found ONLY by reading the rendered page AFTER the sweep reported clean" | `5350403` |
| R9 | DCI | An anchor label read "the front door of the WHE program" **four paragraphs from that same page's corrected sentence** saying no audit is a precondition. **"The page contradicted its own navigation"** | `f83d421` |
| R9 | LGM | The `llms.txt` sentence asserting and denying the conflation in one breath | `e329db7` |
| R9 | GCI | `COPY_VOICE.md`'s internal tier **labels** did not match the sheet's actual three row-groups | `44d638c` |
| R9 | GCI | A source comment claimed all four calculator verdicts "name no payer at all" while the fourth was live with unhedged Atmos dollar claims | `bf240f8` (1) |

**R10 — dangling promise (added)**

| Rule | Repo | Defect | Found in |
|---|---|---|---|
| R10 | DCI | "The standard rebate guide covers the base amounts the bonus multiplies" pointing at a page stating "Per-measure dollar caps are deliberately not enumerated on this page." **7 inbound promises across 2 refusing destinations, 5 of them predating the ruling by 16 days** — pages told readers a calculator "estimates the project cost" while that calculator said it "does not compute a dollar estimate" | canon `a891b83` |
| R10 | GCI | "The Atmos **figures** quoted elsewhere on this site are for the towns Atmos serves" on a property quoting zero Atmos figures — **and this was the variant that survived after "the Atmos amounts quoted elsewhere" was corrected and the class reported closed.** Each of the two pages shipped it twice: body prose and `FAQPage` JSON-LD | `f0203ad` D2; canon `a891b83` |
| R10 | GCI | Three "the Atmos caps say the same thing" comparatives on the wall and crawl-space hubs, pointing at caps the site no longer publishes | `f0203ad` D2 |

**R11 — attribution debt (added, report-only)**

| Rule | Repo | Defect | Found in |
|---|---|---|---|
| R11 | DCI | ~113 unattributed assertions across five terms: `$600` **72/0/72/0**, participating-contractor **72/23/72/23**, WHE 25% **42/1/42/1**, CFM 50 **36/10/34/8**, by-check **46/1/46/1**. **Two cells were wrong in two consecutive rounds from subtraction** — `$600` logged 72/10 when it is 72/0, and CFM 50 unattributed computed as 26 when it is 34 | `f83d421`, `3da02df`, `1794f98`, `cb97983` |

### 11.3 Defects the gate cannot catch, recorded so nobody believes it can

These shipped in the same window and are named because a gate that silently
excludes them would be read as covering them.

| Repo | Defect | Why no rule reaches it |
|---|---|---|
| DCI | **32 subject-verb agreement errors live on 21 of 72 pages** — "the Xcel rebate programs **reduces** net cost further", "programs **pays** out", "the **alive** 2026 Xcel rebate programs" — shipped by a tokenize rewrite that substituted a plural noun and left the verbs alone | Grammar, not claims. Found by *"for every `programs` in the built HTML, tabulate the next word and look for third-person-singular verbs"* — plus ~25 more that check could not reach because an em-dash appositive sat between subject and verb |
| DCI | `programsing`, `programss`, "the extra **a** 25% bonus", "the income-qualified the income-qualified program", "**The Xcel's** income-qualified programs covers", "**the the** income-qualified programs for income-qualified households" | Mangled words from catch-all substitutions. The method that caught them is *"after every substitution, print the FULL LANDING SENTENCE and read it — staged text AND built output, because they catch different classes"* |
| DCI | "**HEAR is** the Colorado Energy Office's federally funded, **income-qualified programs**" — singular subject, singular copula, plural predicate, **and a factual error, because HEAR is one program.** The sitewide swap reached past its own scope into a non-Xcel sentence | The lesson is a rule for editors, not a gate: *"a sitewide substitution must be scoped to the CLAIM it is fixing, not applied to every occurrence of a phrase"* |
| canon, GCI ×4 | **Two figures about the Atmos tariff recorded as settled fact in four files, neither ever counted** — 132 pages (it is 139) and six Weld localities (it is 18) — sitting in the same sentences whose SHA-256 and byte count WERE genuinely measured | Not a page claim. The standing rule it produced is the one §4 enforces on the gate itself: **AN UNCOUNTED FIGURE IS A GUESS EVEN WHEN IT SITS NEXT TO VERIFIED ONES** |
| canon, GCI | A lane row asserted `132-page → 0` when the command returns `1`; another asserted `XCEL_GAS_TOWNS → 3` when it returns `7`; a third asserted `Weld County rows are → 0/0/0` when a wrap-insensitive check returns `1/1/1`. **Three times in two rounds a row was written with the number a command OUGHT to return** | Paperwork, caught by `ops/hooks/commit-msg` re-running the `Verify:` trailer. *"Run the command, paste the output, then write the sentence around it"* |
| DCI | The `meta=` key: 11 blocks, 0 consumers, 0 reads, **five carrying Xcel claims**; a prior round deleted 7 of 18 and left 11. Plus 10 dead `_svc_pending_*.py` modules, 275,446 bytes, still holding removed claims | Dead code. Rule 2. Proven dead by the **manifest test**: regenerate before and after, output byte-identical |
| DCI | D-004's consequent contradicted its amended premise; removing an unsourced claim **broke a standing Auditor-attached condition that required it to be stated** | *"Grep the decision and standards docs for a claim before removing it sitewide, not after"* |

### 11.4 Instrument blindnesses this spec is built to survive

Every one is recorded in this portfolio, with the pass that hit it.

1. `grep -c` counts **lines**, not occurrences. Measured live: `Xcel` on GCI's payback page, `grep -c` **10**, true count **11** (GCI `bf240f8`).
2. A `$`-anchored gate **cannot see a bare-digit cap** — `1550 / 0.75` in a JS comment (GCI `f0203ad`; canon `a891b83`).
3. A cap-anchored sweep cannot see **"the largest rebate"** (GCI `a91dfd4`).
4. A line-based grep cannot see a phrase that **wraps a line break** — `Advice Letter No. 647` returns a false `0` on two of three documents; `"Weld County rows are"` returns `0` where a wrap-insensitive check returns `1`; a `grep -oF` for a shipped sentence returns `0` because the string straddles `680</code> instead: the` ⏎ `result will then fit` (GCI `5f9698b`, `12dfcbf`; DCI `3a6b76b`).
5. A whole-phrase grep cannot see a string **split across Python concatenation** — `"...the primary rebate " "stack for Denver-area..."` matched the `.pyc` and not the `.py` (DCI `fca41f6`, `fb08735`).
6. A **sitemap-enumerated** sweep cannot see `llms.txt` or the embed frame. Eleven rounds and every automated gate walked past `llms.txt` (DCI `84a9c10`, `fb08735`; LGM `e329db7`).
7. A **body-text scan cannot reach** `<head>`, meta, `og:`, `twitter:` or JSON-LD. DCI's `normfind.py` *"structurally cannot see `<head>`"* and a P0 typo shipped live in the SERP snippet.
8. `/usr/bin/grep -ci 'ault'` gives **8** where the locality appears **once**; a bare `the the` matches `the thermal`/`the thermostat`/`the thermometer` on 9 pages where the real count is **1** (GCI `12dfcbf`; DCI `84a9c10`).
9. The session's bundled `grep` is **ugrep with `--ignore-files`** and **silently skips gitignored paths** — reproduced: 2 files shadowed, **3** with `/usr/bin/grep`. **Every count in this spec was taken with `/usr/bin/grep`** (LGM `858bb26`; canon `087a3be`).
10. `textutil -convert txt` does **not** extract the Atmos PDF and reports all nine towns absent **including the six provably present**; `strings` fails identically; only `pdftotext -layout` works (GCI `12dfcbf`).
11. **A grep-built inventory is incomplete by construction** and must not be handed downstream as a specification. All three editing rows found figures the inventory missed, each by running the gate past the list's end (canon `a891b83`).
12. **Each round's instrument was built from the previous round's findings, so each round the defect stepped one word sideways. A grep shaped like the last defect cannot see the next one** (DCI `31484f1`).
13. **Every instrument in five rounds was pointed at the CHANGE; none was pointed at the PAGE.** A diff-scoped read shows what a pass altered; 7 of 11 defects were sentences the pass *should* have altered and did not, sitting in the pre-pass baseline where no diff can reach them (DCI `eb5c939`).
14. **A corpus widened for VERIFICATION is not widened for AUDIT.** Byte-comparing 83 artifacts proves they shipped intact and says nothing about what they claim (DCI `fb08735`).
15. **A green gate set and a byte-verified deploy prove an artifact SHIPPED INTACT and say nothing about whether it is GOOD.** Nine defects passed all seven `functional_proof.sh` checks, both canary-proven validators, and a 79/79 byte sweep. Only a reader looking at the thing found them (DCI `dci-calculator-embed-phase1`).
16. **A byte search that returns 0 whether or not the bug is present is vacuous** — runtime-assembled sentences have no literal form (DCI `dci-d3-tier-label-fix`).
17. **`ops/functional_proof.sh` CHECK 3 discovers tools from the live sitemap, so the embed frame is permanently outside its perimeter** — measured: the frame *does* satisfy `is_tool_page` structurally and is skipped only for sitemap non-membership (DCI `dci-calculator-embed-phase1`).
18. **A gate had been red across sessions and nobody reported it** — `_artifact_grep.sh` was already failing at GCI HEAD before a pass started (GCI `5f9698b`).
19. **Subtraction is not measurement.** `26 = 36 − 10` was wrong because 8 pages do both (DCI `1794f98`).
20. **A bare zero conceals that the zero came from judgment applied after the match.** Three JS-comment scans reported "0" fired **153 times** (canon `b152b08`).
21. **Search for a term you KNOW is present before trusting a term you believe is absent.** Greeley is in that tariff, so any pipeline that cannot find Greeley cannot establish Johnstown is missing (GCI ground-truth; canon `PROPERTY_GENESIS.md`).
22. **A citation sweep must search for the CLAIM, not only for the identifier** (GCI `44d638c`).
23. **The unit of work is the defect class, portfolio-wide, never the page that surfaced it** (canon Rule 8c; hit on DCI's unswept `prerequisite`, and hit again on the `before and after` class still live on DCI today).
24. **A verification command that matches its own commit message is measuring the paperwork, not the tree.** `git show --stat HEAD | /usr/bin/grep -c ops/claim_gate/RULES_SPEC.md` returns **7**, not 1, because `git show` prints the commit MESSAGE and that message names the path six times. `git show --stat --format= HEAD | …` suppresses the message and returns **1**. Same family as #8 (`ault` inside `default`) and #2 (the anchor, not the tree): the instrument matched itself. Found while writing this spec's own commit, 2026-09-17.
25. **A spec's own verification figures are subject to every rule in this file.** Three of the five `Verify:` figures on this spec's commit were written as the number the command OUGHT to return and were wrong: `POSITIVE-CONTROL FIXTURE` drafted as 11, returns **12** (§8's preamble names the field alongside the eleven rules); `blind spot` drafted as 4, returns **8**; and #24 above. All three were caught by running the commands before the report, and corrected in the same pass. **This is the fourth, fifth and sixth recorded instance in this portfolio of writing the figure a command ought to return** — GCI `12dfcbf` and `2a29eb9` recorded the first three, and the standing instruction from `gci-xcel-gas-state-docs` is unchanged and was ignored again here: **run the command, paste the output, then write the sentence around it.**

---

## 12. WHAT THIS SPEC OWES, AND TO WHOM

Recorded here because a spec that hides its own dependencies is the same defect
as a gate that hides its blind spot.

**ITEMS 1 AND 2 WERE PAID ON 2026-09-18** (lane
`gate-close-findings-2026-09-18-canon`, row R1). They are kept here rather than
deleted, because the reason each was owed is the reason the gate now tests for
it, and a spec that quietly drops its own debts teaches nothing.

1. ~~**Two schema additions** are required before R1 and R7 reach full
   strength.~~ **LANDED 2026-09-18. Neither rule prints `DEGRADED` on any
   property now.**
   - `provenance` = `{retrieved, artifact, extraction, verbatim_line}` on every
     `CITED_SOURCES` entry whose `quote` is True — 23 entries carry one
     (DCI 9, LGM 4, GCI 10). `surfaces.provenance_complete()` requires all four
     fields present and non-empty with `retrieved` an ISO date, and R1's
     `registry-backed with explicit quote=true` filter clears a hit only when
     the record is complete.
   - `superseded_by` = `{id, on, reason}` on citation-registry entries, plus a
     top-level `schema.supersession_declared` flag so an ABSENT `superseded_by`
     is a POSITIVE statement — "reviewed on this date, current" — rather than
     silence the gate has to infer currency from. 14 tombstones across the
     three properties (DCI 5, LGM 4, GCI 5), parked in `unwatchable_sources[]`
     so the watcher never fetches a retired URL. R7 merges each tombstone's
     declared `identifiers` into half A, ADDITIVELY to the config list, and
     tags a hit that only the registry knows as sub-test `A-reg`.
   - **BOTH DEGRADED MESSAGES REMAIN IN THE IMPLEMENTATION AND BOTH STILL FIRE
     WHEN THE DEBT IS UNPAID.** R1 is DEGRADED when no entry carries a
     provenance block, when any `quote=True` entry's record is missing or
     malformed (it names them), or when a property has ZERO `quote=True`
     entries — a property with nothing to quote has not paid a debt, it has
     nothing to pay. R7 is DEGRADED when the registry is absent, unparseable,
     or does not declare. Verified against three scratch generators and against
     a registry with the flag flipped to false; in every case the original
     wording returned.
   - The watcher is unaffected, exactly as this item predicted. Measured before
     and after on all three registries: output byte-identical, exit code
     unchanged — DCI 0 and 0, GCI 0 and 0, LGM 1 and 1, LGM's being a
     pre-existing HTTP 404 on `BOULDER_COUNTY_ENERGYSMART` and not this
     change.
2. ~~**`quote` should default to FALSE, not True.**~~ **CLOSED DIFFERENTLY, and
   better.** The default is untouched; `quote` is now set EXPLICITLY on all 87
   entries, so the default never applies to anything and flipping it would
   change nothing. Portfolio totals: **23 True, 64 False, 0 absent**
   (DCI 9/12, LGM 4/27, GCI 10/25).

   **A CORRECTION TO THIS ITEM'S OWN FIGURE.** It read "zero of 87 entries set
   it to True explicitly", and that is wrong twice over. Measured with `ast` on
   2026-09-18: **35 of 87 entries already set `quote` explicitly — every one of
   them to False** (DCI 10, LGM 8, GCI 17). The true statement is that zero set
   it to *True*, and that **52** did not set it at all — which is the figure
   this item's own "52-entry blast radius" already implied. The ruling stands;
   the arithmetic under it did not.

   THE RULING APPLIED, written into every entry beside its flag: `quote=True`
   ONLY where this portfolio's own record shows the stat is the source's own
   words — an explicit verbatim / byte-for-byte / character-identical /
   hand-diffed note, or a long contiguous run of the stat inside
   `docs/citation-registry.json`'s RETRIEVED `fingerprint.sample`. The
   registry's `claim` field was deliberately NOT used as evidence: it is seeded
   from the site's own text, so comparing a stat against it compares a stat
   against a copy of itself. `quote=False` everywhere else, including two
   entries marked JUDGED, NO RECORD, because an attributed paraphrase is the
   sanctioned form (§8, R1, "WHAT IT DELIBERATELY DOES NOT CATCH") while a
   wrongly-True entry publishes site prose as a named source's own words.

   **THE AUDIT FOUND ELEVEN LIVE DEFECTS AND THEY ARE NOT THIS LANE'S TO FIX.**
   Each is a stat one property still publishes inside quotation marks that
   another property already audited and corrected: LGM's
   `ENERGYSTAR_AIR_SEALING_15PCT` (DCI removed it 2026-08-24 as VERIFIED FALSE,
   GCI deleted it 2026-08-27, it survives only there), LGM's
   `ENERGYSTAR_R49_R60`, `BSC_ATTIC_VENTILATION`, `BSC_AIR_LEAKAGE_MOISTURE`
   (two of them recorded on DCI as FABRICATED QUOTATION), `ACCA_MANUAL_J`,
   `ENERGYSTAR_SEAL_INSULATE_15PCT` and `CDPHE_ASBESTOS_REG8`; GCI's
   `ENERGYSTAR_CZ5_HEATING_COOLING_16PCT`, `CDPHE_ASBESTOS_REG8`,
   `CO_WAP_FREE_INSULATION` and `SEVERANCE_GAS_XCEL` — the last one's two
   siblings from the same 2026-09-08 Xcel-gas correction both carry
   "PARAPHRASE, NOT A QUOTATION — deliberate" and the third town was missed.
   Setting `quote=False` stops each publishing AS a quotation once the
   generators run; correcting the text is a copy change and belongs to the rows
   that own copy.

3. **THREE live defects this retrieval found are out of this lane's scope** and
   are reported rather than fixed, because this row is specification-only.
   (**This item read "Two" until 2026-09-17 and undercounted itself by one** —
   the review-date item was written up in §11.2 R8 as LIVE NOW and then omitted
   from this list. Corrected here, and it is the same class as §11.4 items 24
   and 25: a count asserted rather than taken.)
   - **(a)** DCI's uncited `15% reduction in heating and cooling costs` — 2
     occurrences, `public/r-value-needed-calculator.html:1570` and
     `public/do-i-need-new-insulation-quiz.html:1502`, from
     `_generate_calculator_pages.py:453` and `:1102`. §11.2 R5.
   - **(b)** DCI's `before and after the work` blower-door attribution — **13
     files, 21 occurrences**, attributed to a sheet in which the phrase occurs
     **zero** times. The class LGM swept on 2026-09-06 in `124c014` (12 files /
     17 occurrences) and **DCI never received.** Canon Rule 8c. §11.2 R9.
   - **(c)** DCI and LGM both publish review dates that predate corrections they
     shipped: **DCI 70 of 75 pages at `2026-08-24`** against content corrected
     through 2026-09-11, and **LGM 31 of 48 pages at `2026-08-05`** against
     content corrected through 2026-09-10. GCI closed the identical debt in
     `bf240f8`/`348baf9`; DCI holds it under D-003 and an Auditor HOLD, LGM has
     no recorded hold. §11.2 R8.
4. **One stale canon file:** `docs/board/ground-truth.md:9-12` still reads
   "Greeley (Atmos gas, electric unresolved)". Canon's settled-decisions file is
   not this lane's to edit; recorded, not reconciled.
5. **One stale gate comment:** LGM's `_artifact_grep.sh` header names five
   Director-locked towns where there are four.
6. **One unresolved count:** canon's addendum states **545** figures removed
   portfolio-wide; the three commits' own acceptance gates state
   **198 + 133 + 206 = 537**. Recorded unresolved rather than reconciled, per §4.

