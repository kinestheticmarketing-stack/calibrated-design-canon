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
it never deploys. It writes nothing except an explicit `--report` path.**

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
| `--canary` | run **only** the control phase and exit with its result. Independently checkable by hand or in CI. |
| `--brief` | suppress the per-hit and per-removed-item enumerations. Prints `ENUMERATION SUPPRESSED BY --brief` in their place, so a brief run can never be mistaken for a full one. |
| `--opt-in=R6b` | register the browser cross-product rule. See the note below. |
| `--peer <repo>` | supply a second property for R9's cross-property half. Without it the gate prints `R9 CROSS-PROPERTY HALF SKIPPED: no --peer given`. |
| `--report <path>` | also write the output to a file. The only path the gate writes. |
| `--today YYYY-MM-DD` | override the as-of date (default: the config's `R8.today`). |

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
| R3 | REBATE DOLLAR FIGURE | CLAIM TEST for T3; STRING+WINDOW LIST for T1/T2/T4, declared | yes |
| R4 | STACKING ASSERTION OR DENIAL | CLAIM TEST | yes |
| R5 | UNCITED STATISTIC | CLAIM TEST | yes |
| R6 | SELF-CONTRADICTING OUTPUT | CLAIM TEST (G1 branch/print identity, G2 monotonicity) | yes |
| R7 | SUPERSEDED-SOURCE CLAIM | CLAIM TEST for the proposition half; STRING LIST for the identifier half, declared | yes |
| R8 | STALE REVIEW DATE | CLAIM TEST | yes |
| R9 | INTERNAL CONTRADICTION | CLAIM TEST | yes |
| R10 | DANGLING PROMISE | CLAIM TEST | yes |
| R11 | ATTRIBUTION DEBT | CLAIM TEST | **no — REPORT only, never changes the exit code** |

R1 and R7 print **DEGRADED** on every run until the two schema additions
`RULES_SPEC.md` §12.1 names land: a `provenance` block on quotable
`CITED_SOURCES` entries (R1), and `superseded_by` on citation-registry entries
(R7). Until then R1 asserts the `quote` field only and R7 runs off a config
list, and both say so rather than silently passing.

R6's **R6b** (the browser cross-product) is opt-in and is never silently
dropped: when not run the summary prints
`OPT-IN NOT RUN: R6b (browser cross-product). Run with --opt-in=R6b.`
When you do pass `--opt-in=R6b` the gate registers it, its control **cannot**
fire, and the gate exits **2** naming the missing prerequisite — R6b needs a
Chrome binary this gate cannot assume (`RULES_SPEC.md` §6, §7.3), and the gate
makes no outbound request and executes no page JavaScript. That refusal is the
honest outcome: a rule that silently passed without running would be the exact
failure the control-first contract exists to prevent.

## Adding or changing a rule

1. **A rule with no positive-control fixture cannot register.** The loader
   refuses it and exits 2. So does an empty `blind spot` field.
2. Controls run against **fixture files only**, never the repo, and the gate
   asserts `public/` mtimes are unchanged across the control phase.
3. Controls run against the fixture's own **config overlay** merged over the
   property config (`*_CONTROL_OVERLAY` in `claim_gate.py`), so a control proves
   the RULE can detect its defect regardless of which property's territory,
   figures or label chains happen to be loaded. Control tallies are therefore
   identical on all three properties.
4. Every collection is sorted before printing. The gate is byte-deterministic:
   run it twice and diff. The as-of date comes from the config, not the wall
   clock, for exactly this reason.
5. **Values go in the config. Rules go in the implementation.** If a rule cannot
   be expressed without a property name inside `claim_gate.py`, the rule is
   wrong.

## Adding a property

1. Copy an existing `config/<key>.json`, keep `"extends": "common.json"`, and
   fill in `key`, `repo`, `domain`, `min_artifacts`, `expected_html`,
   `key_files_excluded`, `embed_artifacts` (or the null-result note), and the
   `R2.towns` territory model.
2. Drop the wrapper into the new repo's `ops/claim_gate.sh`, changing only the
   config filename.
3. Run `./ops/claim_gate.sh --canary`. All positive controls must report
   DETECTED and all negatives clean before you trust a single rule result.
