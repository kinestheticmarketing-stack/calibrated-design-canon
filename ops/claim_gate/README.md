# The standing claim gate

A re-runnable acceptance predicate over the whole deployed artifact set of each
static-site property. It checks **CLAIMS**, not structure. The existing build
gates (`regen_all.sh`, `_postbuild_check.py`, `_check_links.py`,
`_intra_similarity_check.py`, `_validators.py`, `_artifact_grep.sh`,
`_out_guard.py`, `_similarity_check.py`) check structure, and nine claim defects
once passed all seven `functional_proof.sh` checks, both canary-proven
validators and a 79/79 byte sweep.

The rule specification is [`RULES_SPEC.md`](RULES_SPEC.md) — 3,146 lines, every
rule derived from a defect this portfolio shipped live between 2026-09-01 and
2026-09-11. Read it before changing a rule.

**The gate is READ-ONLY on content. It edits no page, no copy, no generator, and
it never deploys. It writes nothing except an explicit `--report` path** — the
wrappers export `PYTHONDONTWRITEBYTECODE=1`, because setting
`sys.dont_write_bytecode` in the module body is too late when something
*imports* `claim_gate.py`.

**The SRC normalization is real and scoped.** `config.src_rules` names which
rules read the generators' tokenize-joined string runs — today `R2`, `R3-T3`,
`R4`, `R5`, `R7` — and the header prints the list every run, including
`READ BY: NO RULE -- SRC is computed and unused` if it is ever emptied. R3's
T1/T2 numeral halves deliberately do **not** read SRC: the generators embed the
citation registry's own deliberately-kept dollar figures. An SRC finding whose
text already renders in `public/` is cleared through a named filter, because
double-counting one claim is not coverage.

## How to run it

From inside a property repo:

```bash
cd ~/code/denvercoloradoinsulation.com   && ./ops/claim_gate.sh
cd ~/code/longmontcoloradoinsulation.com && ./ops/claim_gate.sh
cd ~/code/greeleycoloradoinsulation.com  && ./ops/claim_gate.sh
```

That is the whole interface. The wrapper is three lines of real work: it finds
canon, passes the property key and the repo path, and forwards the exit code.
Nothing property-specific lives in the wrapper — that is what the config is for.

If canon is not checked out at `$HOME/code/calibrated-design-canon`, set
`CANON_ROOT`:

```bash
CANON_ROOT=/path/to/calibrated-design-canon ./ops/claim_gate.sh
```

Without it the wrapper exits **2** with the path it expected.

## Exit codes

| Code | Meaning |
|---|---|
| **0** | every blocking rule PASS, every control fired, corpus counts agree |
| **1** | at least one blocking rule FAIL — the gate ran and found something |
| **2** | **the gate could not be trusted to have run**: a control did not fire, a negative control false-alarmed, the config is malformed, `git ls-files public/` and the working tree disagree, the read set is smaller than `min_artifacts`, or a rule's filter arithmetic (`raw − removed == adjudicated`) did not hold |

Exit 2 is deliberately distinct from exit 1, matching LGM's `_out_guard.py` and
`_artifact_grep.sh`, which both reserve 2 for "the instrument itself is not in a
state to judge". A `REPORT` finding (R11) never changes the exit code.

## Flags

| Flag | Effect |
|---|---|
| `--canary` | run **only** the control phase and exit with its result. Independently checkable by hand or in CI. The zero-artifact trap runs **before** this returns, so a green canary is not available on a gutted corpus. |
| `--brief` | suppress the per-hit and per-removed-item enumerations. Prints `ENUMERATION SUPPRESSED BY --brief` in their place, so a brief run can never be mistaken for a full one. |
| `--opt-in=R6b` | request the browser cross-product rule. It is **UNAVAILABLE** — it needs a Chrome binary this gate cannot assume — so the gate discloses that and **runs the other ten blocking rules normally**. It does not abort. |
| `--peer <repo>` | supply a second property for R9's cross-property half. The path is validated (no `public/` → exit 2), the peer corpus is enumerated, parsed and indexed with the same predicates, and subject value sets are compared across the two properties, skipping `deliberate_divergence`. The summary discloses the outcome **either way** — `R9 CROSS-PROPERTY HALF SKIPPED: no --peer given` or `R9 CROSS-PROPERTY HALF RAN against <path>`. Passing the flag can never make the gate stop saying whether the half ran. |
| `--report <path>` | also write the output to a file. The only path the gate writes. |
| `--today YYYY-MM-DD` | override the as-of date (default: the config's `R8.today`). Validated: a non-ISO or impossible calendar date exits 2, because R8 compares dates as strings and an unparseable value would silently disable the future-date test. Control fixtures are pinned to their own reference date, so `--today` cannot turn a fixture's own date into a false alarm. |

**There is no flag that skips the controls.** A rule that cannot be shown to
fire is indistinguishable from a rule that is not wired in, and it manufactures
confidence.

## What a run prints

```
CLAIM GATE — <key> — <repo abs path> — HEAD <sha> — as-of <date>
corpus:    git ls-files public/ = N   find public/ -type f = N   AGREE
read set:  N artifacts (N html, N txt, N xml, N svg)  |  excluded: N (reason:count, …)
claim set: N propositions resolved from N cited-stat blocks, N shared constants, N referenced assets
normalization levels compared: RAW DEC TXT   (+ SRC over N generator modules)
KNOWN HOLES, stated up front …
embed frame: …

━━━ CONTROLS (run BEFORE any rule) ━━━
  canary+ <RULE>  <fixture>  DETECTED | *** MISSED ***
  canary- <NEG>   <fixture>  clean    | *** FALSE ALARM *** …
  public/ mtimes unchanged across the control phase: N files verified
  CONTROLS: N positive DETECTED, N MISSED · N negative clean, N FALSE ALARM

━━━ R1  FABRICATED QUOTATION ━━━
  kind: CLAIM TEST | STRING LIST | CLAIM TEST (+ string list for <half>, declared)
  surfaces: …   normalization: …
  RAW              <what the instrument matched>              N
  FILTER           <named filter>                             N    (removed N)
  ADJUDICATED      <what survives>                            N
  LEVEL-DISAGREE   RAW=N DEC=N TXT=N                          AGREE | DISAGREE
  DEGRADED         <reason>                                        (when degraded)
  TRAP: …                                                          (when tripped)
  note: …
  VERDICT          PASS | FAIL | REPORT — <reason carrying the number>
  blind spot: <what this rule structurally cannot see>
  --- N hits, enumerated ---
  --- N items the filters removed, enumerated ---

━━━ SUMMARY ━━━
  R1  FABRICATED QUOTATION   RAW N   ADJ N   FAIL
  …
  OPT-IN NOT RUN: R6b (browser cross-product). Run with --opt-in=R6b.
  blocking failures: N (…)
  report-only findings: N (…)
  opt-in rules not run: N
CLAIM GATE: PASS | FAIL
```

### R2's REVIEW classes, declared

Two R2 outcomes are reported and enumerated but never fail the gate. Both are
loosenings and both are named here, to the same standard as the paraphrase hole
below.

**SPLIT DISCLOSURE.** A sentence is first split into independent clauses on its
coordinating conjunctions (`;`, `, while`, `whereas`, `, but`, `rather than`,
`, however`) and each clause is resolved on its own, with its own utility and
its own town. `X is the gas utility in A, while Y is the gas utility in B` has
unambiguous structure and is judged, not pardoned: the correct sentence PASSES
and its inversion FAILS with both attributions named. Only a clause that STILL
carries two or more utilities AND two or more towns after splitting is reported
as REVIEW, because there word order rather than meaning decides which utility a
town binds to. That residue is small and is printed with a count every run —
measured 2026-09-17: DCI 0, LGM 3, GCI 13, down from GCI 289 when the whole
sentence shape was pardoned.

**SITEWIDE, NO TOWN IN THE CLAUSE.** An artifact with no resolvable town scope
— `llms.txt`, `robots.txt`, `sitemap.xml`, a bare `.svg` — that names a utility
with no town anywhere in its clause asserts nothing against a town, because the
utility serves somewhere in the configured territory. Raised, counted and
enumerated rather than skipped, so it can never be mistaken for a clean run.

### PARAPHRASE IS A KNOWN HOLE, and this instrument cannot close it

This gate matches **strings, configured predicates and structure**. It does not
understand language. A claim rewritten into words the config does not contain is
invisible to it, and no amount of list-widening changes that — each round of
widening only moves the defect one word sideways, which is the failure mode
`METHODS/CANDIDATE-do-not-scope-with-grep-over-html.md` records as "a grep
shaped like the last defect cannot see the next one".

Measured examples that remain **MISSED** and are expected to:

- R4: *"are cumulative on the same measure"*, *"claim … at once"*, *"run
  concurrently and pay for the same measure"* were added to the config and now
  fire; the next three phrasings will not.
- R5: *"forty percent"* spelled out and *"by a third"* were added; *"cuts the
  bill to two-thirds of what it was"* will not fire.
- R3: a dollar figure written entirely in words, and *"pays the most"* as a rank
  claim outside `rank_words`.
- R1: the anaphoric form — a quotation attributed in the previous sentence.
- R7: a superseded proposition restated in new words.

What the gate DOES close is the mechanical evasion beneath paraphrase: entity
encoding, template literals, HTML comments, invisible format characters and
homoglyphs, line wrapping, abbreviation-driven sentence splits and class-list
membership. Those are normalization failures and they are fixable. Paraphrase is
not, and a rule list that implied otherwise would be the "manufactures
confidence" failure this gate exists to prevent.

### The control counts, reconciled

`RULES_SPEC.md` §4's sample footer says `22 positive DETECTED, 14 negative
clean`. The gate prints **24 positive controls, 24 repair tests and 14 negative
controls**. Both are right about different things, and I cannot edit
`RULES_SPEC.md`, so the reconciliation lives here:

- **22 is a fixture-DOCUMENT count.** `fixtures/` holds 24 files outside
  `negative/`; two are the `.gitfacts.json` sidecars for R8a and R8b, which are
  input data rather than fixtures. 24 − 2 = 22 positive-control fixture
  documents, exactly as §1's manifest and §8/§9 declare.
- **24 is the CONTROL count**, i.e. the number of `canary+` lines. It differs
  from 22 in both directions: R9's two files are one directory driving two
  sub-tests and R10's three files are one directory driving two, which pushes
  the control count *down*; and R1, R7, R8c and R10 each gained a second
  control when every control was bound to a single sub-test, which pushes it
  *up*. R6b is requested-and-unavailable and is **not** counted as a control.
- **24 repair tests**, one per control, under `fixtures/repaired/`.
- **14 negative controls** agrees exactly: 14 `NEG*.html` documents plus one
  `NEG11.gitfacts.json` sidecar = 15 files.

Commands:
```
find ops/claim_gate/fixtures -type f -not -path '*/repaired/*' -not -path '*/negative/*' | wc -l   -> 24
find ops/claim_gate/fixtures/negative -name '*.html' | wc -l                                       -> 14
```

**UPDATED 2026-09-18: the control count is now 29, the repair-test count 29,
and the negative count is unchanged at 14.** Five controls were added, each
bound to a sub-test that previously had none, each with a repaired counterpart:

| control | sub | what it proves |
|---|---|---|
| `R2d` | `a` | the EXACT INVERSION of the property's gas-split fact FAILS while the correct fact PASSES, in the same sentence shape with the same two utilities and the same six towns |
| `R4c` | `DENIES` | a stacking denial whose two programmes are named INFORMALLY ("the free state weatherization program", "the Atmos rebate") resolves through `program_aliases` |
| `R4d` | `DENIES-SET` | a stacking denial whose programmes are named ANAPHORICALLY ("either insulation rebate program") is judged on its predicate |
| `R7-REG` | `A-reg` | R7's identifier half is driven by `docs/citation-registry.json`, not only by the gate's own config list |
| `R9-N3b` | `N3b` | a hidden lead-form field that can transmit a verdict the visible output can never show is FOUND, not merely counted |

### A bare zero is FORBIDDEN

Every rule prints its **raw** match count, every **filter** with what that
filter removed, and the **adjudicated** result — even when all three are zero,
and even when raw equals adjudicated. The gate asserts `raw − removed ==
adjudicated` and exits **2** if that identity fails, because subtraction is not
measurement (DCI `1794f98`: `26 = 36 − 10` was wrong because 8 pages did both).
Every removed item is **enumerated**, not counted: the null half of a sweep is
only auditable if the cleared items are listed. A run whose filter silently
dropped a real hit must not look identical to a clean run.

### `kind:` is printed by the gate, every run

A string list must not masquerade as a claim test, and the only way to guarantee
that is for the gate to say which it is, in its own output, every time.

### KNOWN-OPEN hits are never filtered

`config.<rule>.known_uncited` carries provenance so the gate can print
`KNOWN-OPEN` beside a hit. It does **not** suppress it. No filter may remove a
KNOWN-OPEN hit.

## Files

```
ops/claim_gate/
  RULES_SPEC.md          the specification (row R1 of the 2026-09-17 pass owns it)
  claim_gate.py          the ONE implementation: the eleven rules, the controls,
                         the output contract, the CLI
  surfaces.py            the text_of() / surface extractor and the four
                         normalizations
  config/common.json     shared VALUES: no property name, no territory
  config/dci.json        per-property values; each `extends: common.json`
  config/lgm.json
  config/gci.json
  fixtures/              one positive-control fixture per rule sub-test
  fixtures/negative/     NEG01..NEG14, all derived from copy that is live and
                         correct right now, or from a recorded false positive
  README.md              this file
<property-repo>/
  ops/claim_gate.sh      thin wrapper, three lines of real work
```

`config/common.json` exists because `_artifact_grep.sh` is the recorded
counter-example: GCI's copy and LGM's copy diverged into two files that must be
maintained twice, and LGM's still names a five-town Director lock where the
property has had four towns since `3ca991f`. `common.json` holds only values that
are genuinely shared and names no property; territory, figures and locked strings
live in the per-property file.

## The eleven rules

| ID | Name | kind | blocking |
|---|---|---|---|
| R1 | FABRICATED QUOTATION | CLAIM TEST (+ string list for the hand-written-prose half, declared) | yes |
| R2 | WRONG-UTILITY CLAIM | CLAIM TEST | yes |
| R2 sub-tests | `a` attribution · `b` inherited cite key · `c` wayfinding URL · `e` electric naming · `h` hedge halves · `q` town qualifier · `x` qualifier cross-contamination · `t` town-blind tool · `p` forbidden program name · `r` locked restriction | | |
| R3 | REBATE DOLLAR FIGURE | CLAIM TEST for T3; STRING+WINDOW LIST for T1/T2/T4, declared | yes |
| R4 | STACKING ASSERTION OR DENIAL | CLAIM TEST | yes |
| R5 | UNCITED STATISTIC | CLAIM TEST | yes |
| R6 | SELF-CONTRADICTING OUTPUT | CLAIM TEST (G1 branch/print identity, G2 strict monotonicity, G2-DUP two labels at one value, UNPARSEABLE) | yes |
| R7 | SUPERSEDED-SOURCE CLAIM | CLAIM TEST for the proposition half; STRING LIST for the identifier half, declared | yes |
| R8 | STALE REVIEW DATE | CLAIM TEST | yes |
| R9 | INTERNAL CONTRADICTION | CLAIM TEST | yes |
| R10 | DANGLING PROMISE | CLAIM TEST | yes |
| R11 | ATTRIBUTION DEBT | CLAIM TEST | **no — REPORT only, never changes the exit code** |

### REPORT-ONLY BY MEASUREMENT

`config.false_positive_measurements` demotes any rule measured above
`demote_above_pct` (25) false positives: it stops affecting the exit code and
**prints its measured rate, its counts and its verbatim false-positive classes
inside its own block, every run**. The measurement is DATA, so the next pass
RE-TAKES it rather than inheriting it; deleting the entry re-arms the rule.

Measured exhaustively on 2026-09-18 — every finding on every property, nothing
sampled:

| rule | examined | TRUE | FP | REVIEW | rate | outcome |
|---|---|---|---|---|---|---|
| R2 | 198 (DCI 22, LGM 78, GCI 98) | 20 | 175 | 3 | 88.4% | **fixed at the cause, not demoted** — now 0% |
| R3 | 47 (DCI 33, GCI 14, LGM 0) | 9 | 32 | 6 | **68.1%** | **REPORT-ONLY** |

R2 is the reason the threshold is not applied mechanically: its false positives
all had *causes* — a town served by two utilities, a restriction stated in the
page's own words, a clause splitter cutting a town list, nearest-distance
binding running backwards — and fixing them took it to 0% with true positives
for the first time. R3's are a rank word governing something that is not a
rebate, which is a rule-shape problem, not a config gap.

**What the R3 demotion costs, stated rather than buried:** R3's T1 half, the
`$`-anchored figure scan, is EXACT — 198/198 on DCI and 206/206 on GCI against
the human sweep in the 2026-09-17 replay. Demoting R3 wholesale takes T1's
blocking power with it. The right next step is a per-sub-type verdict so T1 can
block while T3 reports.

**The two schema debts `RULES_SPEC.md` §12.1 records are PAID (2026-09-18),
and R1 and R7 no longer print `DEGRADED` on any property.** Both messages are
still in the source and both still fire when the debt is unpaid — the
conditions are now real tests, not deletions:

- **R1** — `provenance` = `{retrieved, artifact, extraction, verbatim_line}` on
  every `CITED_SOURCES` entry whose `quote` is True. R1 is DEGRADED when no
  entry carries a provenance block at all, when any `quote=True` entry's record
  is missing or malformed (it names them), or when a property has ZERO
  `quote=True` entries — because a property with nothing to quote has not paid
  a debt, it has nothing to pay, and R1's claim-test half is asserting nothing
  there. `surfaces.provenance_complete()` requires all four fields present,
  non-empty, with `retrieved` an ISO date.
- **R7** — `superseded_by` = `{id, on, reason}` on entries in each property's
  `docs/citation-registry.json`, plus a top-level
  `schema.supersession_declared` flag so an ABSENT `superseded_by` is a
  positive statement ("reviewed on this date, current") rather than silence.
  R7 reads the registry and merges its declared `identifiers` into half A,
  additively to the config list. It is DEGRADED when the registry is absent,
  unparseable, or does not declare. Sub-test **`A-reg`** tags a hit whose
  identifier ONLY the registry knows, and control `R7-REG` is bound to it —
  without that split, "the debt is paid" would rest on a message no longer
  printing.

`quote` is now EXPLICIT on all 87 entries portfolio-wide (23 True, all with a
provenance block; 64 False). It used to default to True through
`src.get('quote', True)`, so 52 entries published their `stat` inside curly
quotation marks as the named source's own words because nobody had said
otherwise.

R6's **R6b** (the browser cross-product) is opt-in and is never silently
dropped. When not requested the summary prints
`OPT-IN NOT RUN: R6b (browser cross-product). Run with --opt-in=R6b.`
When you pass `--opt-in=R6b` the gate prints
`canary= R6b-G3 ... UNAVAILABLE: requires a Chrome binary this gate cannot
assume (spec 6, 7.3). No browser, no outbound request. Disclosed, not run, not
counted as a control.` and **runs the other ten blocking rules normally**. It
does not abort and it is not a control failure. Disclosure is what §6 requires;
aborting all eleven rules converted a documented flag into a permanent red and
denied the operator the ten rules that do work. The gate makes no outbound
request and executes no page JavaScript.

R6 also prints a real **DENOMINATOR** every run — chains examined, JS texts
read, conditions located, label assignments found, branches bound to a
condition — so a `RAW 0` can never mean both "clean" and "blind". A chain whose
labels are present but cannot be bound to conditions (a ternary, a
`switch (true)`) is a loud `UNPARSEABLE` finding, and two labels reachable at
the same printed value is `G2-DUP` — which is the named defect class R6 exists
for.

## Adding or changing a rule

1. **A rule with no positive-control fixture cannot register.** The loader
   refuses it and exits 2. So does an empty `blind spot` field.
2. **Controls cannot reach the repo under test.** `ctx.repo` points at a path
   that does not exist, rules refuse filesystem reads when `ctx.control`, and
   `isolation_breach()` fails any control whose findings name a repo artifact.
   The gate also asserts `public/` mtimes are unchanged across the control
   phase. Before this was true, `rule_R6` read the real generator from inside a
   negative-control context, so on a tree carrying the R6 defect all 14
   negative fixtures false-alarmed and the gate exited 2 `NOT RUN` instead of 1
   `R6 FAILED` — it refused to run precisely when the defect was present.
3. Controls run against the fixture's own **config overlay** merged over the
   property config (`*_CONTROL_OVERLAY` in `claim_gate.py`). The overlay
   **merges, it does not replace**, so a property value can still reach a
   control; the overlay only guarantees that the values a given control depends
   on are the ones it declares. In practice the DETECTED/MISSED and
   clean/FALSE-ALARM tallies are identical on all three properties and the
   per-control hit counts in parentheses vary. Do not read this as "the control
   is property-independent"; read it as "the control's own inputs are pinned".
4. **Every control is bound to the ONE sub-test it proves** (`sub=` on the
   `Control`). Without that binding a hit from any sub-test satisfied the
   control, and R1's claim-test half and R2's wrong-utility half each ended up
   with no control at all — each was satisfied by a different half of the same
   fixture.
5. **Every control has a REPAIR counterpart** under `fixtures/repaired/` in
   which the defect is fixed, and the rule must return zero hits on that
   control's sub-test against it. A control that still fires on a repaired
   fixture is a control failure and exits 2. That is Ruling 6 made mechanical,
   and it caught two regressions while this round was being written.
6. Control fixtures are pinned to their own as-of date, so `--today` cannot
   turn a fixture's own hardcoded date into a false alarm.
7. Every collection is sorted before printing. The gate is byte-deterministic:
   run it twice and `cmp`. The as-of date comes from the config, not the wall
   clock, for exactly this reason.
8. **Values go in the config. Rules go in the implementation.** If a rule cannot
   be expressed without a property name inside `claim_gate.py`, the rule is
   wrong. And a config key that no code path reads is a rule that silently does
   not exist: wire it up or delete it.

## Adding a property

1. Copy an existing `config/<key>.json`, keep `"extends": "common.json"`, and
   fill in `key`, `repo`, `domain`, `min_artifacts`, `expected_html`,
   `key_files_excluded`, `embed_artifacts` (or the null-result note), and the
   `R2.towns` territory model.
2. Drop the wrapper into the new repo's `ops/claim_gate.sh`, changing only the
   config filename.
3. Run `./ops/claim_gate.sh --canary`. All positive controls must report
   DETECTED and all negatives clean before you trust a single rule result.
