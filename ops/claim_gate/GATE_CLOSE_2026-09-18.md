# Claim gate — wiring and release record, 2026-09-18

R5 of a 6-row pass. This row re-scored the gate, wired it into the builds that
pass it, and shipped all three properties. It was the only row authorised to
deploy. It changed no page, no copy and no generator.

Gate under test: canon `ops/claim_gate/` at canon HEAD `eafada2`.

---

## 0. THE RE-SCORE — 21 of 25, up from 16 of 25

The gate was previously scored (`GATE_SCORE_2026-09-17.md`, canon `7a091a0`) by
replaying 25 known defect instances out of git at the commit immediately before
each fix: **16 CAUGHT, 2 PARTIAL, 7 MISSED**. That replay was repeated with the
current gate at canon `eafada2`, same method — 20 detached worktrees in scratch,
`--today` set to each fixing commit's date, all 20 removed and pruned afterwards.

### **21 of 25 CAUGHT · 2 PARTIAL · 2 MISSED**

**Five of the seven misses flipped to CAUGHT. Nothing regressed. Both PARTIALs
improved.**

**The prior score's governing finding is fixed.** §0 of `GATE_SCORE_2026-09-17.md`
recorded that the gate exited 2 — `CLAIM GATE: NOT RUN` — on *every* DCI tree,
because one real R6 finding in the repo under test false-alarmed all 14 negative
controls, so no DCI row could be scored at gate level at all. **11 of the 12 DCI
pre-fix trees now run and exit 1.** Those verdicts are real gate verdicts now,
not harness results.

### The five flips, each with the change that moved it

| # | defect | repo | moved by |
|---|---|---|---|
| **4b** | short-form `Dec. 31, 2026` (DCI) | DCI | `7be4641` — the sentence splitter broke at the abbreviation period, so two shipped R7 patterns containing "Dec." could never fire. The gate had reproduced, inside itself, the exact trap the defect describes. |
| **4c** | the invented fifth Xcel program | DCI | `57421dc` / `32b1ec1` — `forbidden_program_names` was dead config read by no code path; now wired as R2 sub-class `p`, firing 287 hits across 72 files |
| **7d** | FAQPage stacking denial | GCI | `8ff3a55` + `da6663d` — new `ASSERTS-SET` class for programs named anaphorically ("these programs"), where the phrase supplies the count and never a name |
| **7e** | knob-and-tube stacking denial | LGM | `8ff3a55` — same anaphora class, on "either insulation rebate program" |
| **7f** | `llms.txt` "Xcel rebate-stack eligibility" | DCI | `da6663d` — bare `"Xcel"` added to `R4.programs`, span-consuming `names_in()` so `"Xcel Energy"` cannot self-satisfy the two-program test, plus the single-program `ASSERTS-1P`/`DENIES-1P` class |

### The two that still miss

**2b — GCI `og-image.svg`.** Verdict unchanged; cause completely changed. The
prior diagnosis was structural — *"an artifact with no town scope produces zero
R2 hits by construction"*. `47a50c8` closed that: the SVG is now read on a
`SVGTEXT` surface and **does** produce an R2 hit, which is then filtered, raised
and enumerated rather than dropped silently:
`[sitewide artifact, no town named in the clause … (raised and enumerated, never dropped silently)] public/og-image.svg:SVGTEXT  a  Atmos Energy | no town bound in the clause, no town scope on the page | Atmos rebates explained · Local contractors · Existing-home retrofits  [sitewide-no-town-in-clause]`
Scored MISSED because it does not block. The blindness the prior score named is
gone; what remains is a visible ruling.

**10 — DCI hidden `calc_output`.** Verdict unchanged; diagnosis now sharp enough
to act on. `d8be8fd` implemented R9's N3b half and its positive control fires
(`canary+ R9-N3b … DETECTED (1 N3b: N3b)`). **The rule works; the config is one
page short.** `dci.json`'s `R9.tools` lists only
`public/r-value-needed-calculator.html`, while on the tree where the defect is
live the string sits on `public/attic-insulation-cost-calculator.html`. Adding
one `R9.tools` entry closes it.

### Both partials improved

- **5b — LGM's 133 rebate figures: 18 → 109 of 133.** The `cost_context_markers`
  over-removal that pardoned the entire Efficiency Works per-square-foot payout
  schedule is substantially closed: `$1.16` 0 → 63 adjudicated rows, `$0.77`
  0 → 31. Still removed: `$2,000` ×2, the Boulder County EnergySmart cap, by the
  same filter.
- **8 — DCI's `25-40%`: 14 → 15 of 16 pages.** `1bcc0b7` removed R5's blanket
  `recognised_publishers` exemption, which had pardoned `insulation-lakewood.html`
  because Xcel was named as the *payer*. The one remaining miss is unchanged in
  cause: `air-sealing.html`'s sentence never enters R5 RAW because its verbs
  ("covers", "drops") are not in `magnitude_words`.

### The one thing that got worse

**R3 no longer blocks.** `b00e3b1` demoted it to report-only on its own measured
68.1% false-positive rate. Rows 5a, 5b, 5c and 5d — all four rebate-dollar-figure
defects, 537 figures between them — are still **DETECTED** but no longer
**BLOCK**. Detection held or improved in every case (5a `T1 $-anchored 222`;
5c 9 of 9 distinct figures across 24 of 24 files). Every one of those trees still
exits 1 on other rules, so no release would have shipped — but if R3 were the
only failing rule, it would now pass.

### Anachronism, stated per row rather than scored silently

- **4b and 4c are anachronism-dependent.** `common.json` ships the literal
  pattern `"invoiced by Dec. 31, 2026"`, whose own `why` field names the defect
  being scored; `forbidden_program_names` carries the literal "Xcel IQ Program"
  and cites commits from the same day as the tree. In both cases what genuinely
  moved is the **machinery** — the splitter fix is general, and the key being
  *wired at all* is the advance, since its contents were previously irrelevant.
  Neither is evidence of forward detection.
- **7e / 7f partially.** `program_set_anaphora`'s first entry is the exact LGM
  phrase and `R4.programs`' note names the llms.txt line, but both sit inside
  genuinely general mechanisms (a 14-phrase list of ordinary English anaphora; a
  single-program class; span-consuming name matching). **7d rests on the generic
  "these programs"** and is clean.
- **Carried forward unchanged:** 3a/3b/4a's R7 entries still name the commits
  being scored; `gci.json` still encodes post-fix Johnstown/Milliken/Severance
  territory (2a); `printed_var: "pctShort"` still describes post-fix code
  (6, G1 only — G2 is clean); R9's `tools` config still flips N3 between trees.
- **New this pass:** `gci.json` now pins 13 pages measured at 2026-09-18 HEAD,
  up from 2. Checked: they do not suppress row 9b — both `about.html` and
  `contact.html` `surfaces-disagree` rows still fire on `12dfcbf`.

### A NEW GATE DEFECT, found by the replay and reported not fixed

One tree, `dci-4cf7a52`, still exits 2 — the same control-contamination class the
R6 fix closed, surviving one layer over. `run_controls` (`claim_gate.py:4594`)
does `base["_gen"] = gen` where `gen` is **the repo-under-test's own generator
source**, and hands it to every control context. `_control_ctx`'s own docstring
says *"A control must never open the repo under test"* and it correctly points
`ctx.repo` at a nonexistent path — but `_gen` is still the real tree, so R9's
repair control picks up the repo's genuine `xcel_cfm50_scope` contradiction and
reports `*** FIRES ON REPAIRED ***` against an innocent fixture. Bisected
empirically: with generators emptied the control is clean, with the citation
registry emptied it still fires. **It does not bite the three properties at their
current HEADs** — all three show `0 FALSE ALARM` — but it is live, not a replay
artifact.

### Replay method and its one config override

`min_artifacts` and `expected_html` were set to `10` on all three configs for the
replay, and nothing else — verified programmatically that those are the only two
keys differing from canon's. Real values are DCI 85/75, LGM 59/48, GCI 49/38, and
both are floors, so `10` preserves the empty-corpus trap while letting smaller
historical trees run at all.

**NOT TESTED in the replay:** `--opt-in=R6b` (the prior score found it forces
exit 2 on any repo; whether `429b82c` changed that was not re-tested), and
`--peer`, so R9's cross-property half ran on none of the 25 rows — the same as
the prior score's method, and no row depends on it. False-positive rates were not
re-adjudicated; this was a defect-recall re-score only.

---

## 1. Gate verdicts at the new heads

Command, per property: `cd ~/code/<repo> && ./ops/claim_gate.sh`

All three: `CONTROLS: 29 positive DETECTED, 0 MISSED · 14 negative clean, 0
FALSE ALARM`, and both corpus enumerations AGREE
(`git ls-files public/` == `find public/ -type f`): DCI 85, LGM 59, GCI 49.

| property | HEAD | exit |
|---|---|---|
| DCI | `33f8244` (measured), `bdf6701` (after this row's commit) | **1** |
| LGM | `f3768f5` (measured), `4211b8d` (after this row's commit) | **0** |
| GCI | `0bc24ca` (measured), `3a1357f` (after this row's commit) | **0** |

This row's own commits touch `regen_all.sh` only; `public/` is byte-identical
across them, so the verdicts hold at both SHAs.

**DCI**
```
  R1  FABRICATED QUOTATION             RAW 91     ADJ 0      PASS
  R2  WRONG-UTILITY CLAIM              RAW 664    ADJ 0      PASS
  R3  REBATE DOLLAR FIGURE             RAW 1066   ADJ 87     REPORT (non-blocking)
  R4  STACKING ASSERTION OR DENIAL     RAW 661    ADJ 2      FAIL
  R5  UNCITED STATISTIC                RAW 541    ADJ 46     FAIL
  R6  SELF-CONTRADICTING OUTPUT        RAW 0      ADJ 0      PASS
  R7  SUPERSEDED-SOURCE CLAIM          RAW 0      ADJ 0      PASS
  R8  STALE REVIEW DATE                RAW 1      ADJ 0      PASS
  R9  INTERNAL CONTRADICTION           RAW 2      ADJ 2      FAIL
  R10 DANGLING PROMISE                 RAW 0      ADJ 0      PASS
  R11 ATTRIBUTION DEBT                 RAW 8      ADJ 8      REPORT (non-blocking)
  blocking failures: 3 (R4, R5, R9)
CLAIM GATE: FAIL
```
**LGM**
```
  R1  RAW 64    ADJ 0  PASS    R2  RAW 1012  ADJ 0  PASS
  R3  RAW 582   ADJ 0  REPORT  R4  RAW 455   ADJ 0  PASS
  R5  RAW 228   ADJ 0  PASS    R6  RAW 0     ADJ 0  PASS
  R7  RAW 0     ADJ 0  PASS    R8  RAW 1     ADJ 0  PASS
  R9  RAW 0     ADJ 0  PASS    R10 RAW 7     ADJ 0  PASS
  R11 RAW 0     ADJ 0  REPORT
  blocking failures: 0
CLAIM GATE: PASS
```
**GCI**
```
  R1  RAW 35    ADJ 0  PASS    R2  RAW 359   ADJ 0  PASS
  R3  RAW 345   ADJ 10 REPORT  R4  RAW 119   ADJ 0  PASS
  R5  RAW 203   ADJ 0  PASS    R6  RAW 0     ADJ 0  PASS
  R7  RAW 0     ADJ 0  PASS    R8  RAW 14    ADJ 0  PASS
  R9  RAW 0     ADJ 0  PASS    R10 RAW 29    ADJ 0  PASS
  R11 RAW 0     ADJ 0  REPORT
  blocking failures: 0
CLAIM GATE: PASS
```

---

## 2. What was wired, and what was deliberately not

**Wired: LGM (`4211b8d`) and GCI (`3a1357f`).** Both exit 0, which was the
pre-stated condition. The gate runs last in `regen_all.sh`, after the
intra-property duplication gate, following each repo's existing convention for
its other checks (`"$(dirname "$0")/<check>"` under the file's `set -e`), so a
non-zero gate exit halts the build.

**`--brief` was chosen, and that was this row's decision, not a pre-stated
one.** It suppresses the per-hit enumerations — roughly 2,700 lines per build —
while still printing every `VERDICT` line and the whole `SUMMARY` block, so a
failure is legible in the build log and the full detail is one command away
(`./ops/claim_gate.sh`). A build log that buries every other check's output is a
log nobody reads.

`./regen_all.sh` end to end, after wiring:

| property | exit | gate in chain | `public/` changed by the run |
|---|---|---|---|
| LGM | **0** | `CLAIM GATE: PASS`, blocking failures 0 | none — only `regen_all.sh` was dirty |
| GCI | **0** | `CLAIM GATE: PASS`, blocking failures 0 | none — only `regen_all.sh` was dirty |

**NOT wired: DCI.** It exits 1. A gate wired into a build it fails is a red
build nobody can act on. DCI's `regen_all.sh` instead carries a commented block
(`bdf6701`) recording that the omission is a decision rather than an oversight,
and stating the mechanical condition for reversing it: run `./ops/claim_gate.sh`,
and when it exits 0, delete the comment markers. The block explicitly forbids
wiring it in behind a `|| true`, which would recreate a green build over a
failing gate.

---

## 3. Release — two hops, staged and verified before promotion

Production before this release was NOT the previous HEAD. Each live tree was
identified by exhaustive byte comparison against every commit that touched
`public/` in the last 60:

| property | live tree before release == | dated |
|---|---|---|
| DCI | `37c7b29` | 2026-09-11 |
| LGM | `d6e8dab` | 2026-09-10 |
| GCI | `25cb16b` | 2026-09-10 |

Running the CURRENT gate against those three production trees gives the
baseline this release is measured against — same gate, same configs, so every
delta below is a content delta:

| rule | DCI prod → new | LGM prod → new | GCI prod → new |
|---|---|---|---|
| R1 | 76 → **0** (FAIL→PASS) | 83 → **0** (FAIL→PASS) | 47 → **0** (FAIL→PASS) |
| R2 | 0 → 0 | 16 → **0** (FAIL→PASS) | 7 → **0** (FAIL→PASS) |
| R3 (report-only) | 35 → 87 | 0 → 0 | 10 → 10 |
| R4 | 41 → **2** | 25 → **0** (FAIL→PASS) | 0 → 0 |
| R5 | 260 → **46** | 45 → **0** (FAIL→PASS) | 12 → **0** (FAIL→PASS) |
| R7 | 1 → **0** (FAIL→PASS) | 0 → 0 | 0 → 0 |
| R8 | 77 → **0** (FAIL→PASS) | 161 → **0** (FAIL→PASS) | 39 → **0** (FAIL→PASS) |
| R9 | 57 → **2** | 0 → 0 | 0 → 0 |
| **blocking failures** | **6 → 3** | **5 → 0** | **4 → 0** |

No blocking rule rose on any property. The single rising number is DCI's
report-only R3, 35 → 87, and its cause is measured, not guessed: this pass
propagated an ATTRIBUTED Xcel-summary sentence from 1 page to 45
(`/usr/bin/grep -roI "customers can receive larger attic insulation"` →
production 1, new 45; control `Denver` → 3,153). Those rows carry the rank word
"larger" inside a citation, so R5 (uncited) fell while R3-T3 (rank claim) rose.
R3 is non-blocking and carries a measured 68.1% false-positive rate.

Staging verification, per property, run BEFORE promotion:
1. `ops/push-to-staging.sh <full-domain>` (hop 1), rsync exit 0.
2. Staged bytes pulled back off the VPS and compared to the repo at HEAD with
   `diff -r -q` — **identical, exit 0, all three** (85 / 59 / 49 files).
3. The gate run against a worktree whose `public/` IS the staged bytes —
   reproduced the HEAD verdicts exactly: DCI exit 1 (R4 2, R5 46, R9 2),
   LGM exit 0, GCI exit 0.
4. `deploy.sh --dry-run` (hop 2 plan): 0 deletions, staging and live html
   counts equal, snapshot planned. Only then hop 2.

Promotion, hop 2, all exit 0, all `deleted: 0 file(s)`, each with a restore
snapshot on the VPS:
```
/root/backups/longmontcoloradoinsulation.com-20260918-165140   48 html
/root/backups/greeleycoloradoinsulation.com-20260918-165145    38 html
/root/backups/denvercoloradoinsulation.com-20260918-165150     75 html
```

Live verification after promotion — every file curled to disk and compared with
`cmp` (never `$(curl ...)`, which strips trailing newlines and manufactures
false mismatches):

| property | URLs fetched | non-200 | `cmp` mismatches vs repo HEAD |
|---|---|---|---|
| DCI | 85 | 0 | **0** |
| LGM | 59 | 1 (see below) | **0** |
| GCI | 49 | 0 | **0** |

LGM's `/index.html` returns `301 → /`, and `/` returns 200 with bytes identical
to `public/index.html`. That is deliberate canonicalisation on LGM only; DCI and
GCI serve `/index.html` as 200. Recorded so the next release does not read it as
a failure.

---

## 4. Findings recorded, NOT fixed — the fixing rows had finished

**(a) Nine of DCI's 46 blocking R5 findings name a file that does not contain
the quoted sentence.** All nine are CITE-surface rows quoting *"the qualifying
minimum standard for the air sealing rebate is a 20% reduction in CFM 50…"*.
Measured:
```
$ /usr/bin/grep -lI 'qualifying minimum standard for the air sealing rebate' public/index.html
  (no match)
$ /usr/bin/grep -o 'CFM'    public/index.html | wc -l        ->  0
$ /usr/bin/grep -o 'Denver' public/index.html | wc -l        ->  57   # control
$ /usr/bin/grep -rlI 'qualifying minimum standard for the air sealing rebate' public/ | wc -l
  36        # and index.html is not among them
```
Checked individually, **all nine named files are ABSENT the phrase**:
`attic-insulation-cost-denver`, `blown-in-insulation-cost-denver`,
`hear-rebate-status-colorado`, `index`, `insulation-project-timeline-denver`,
`power-ahead-colorado-insulation`, `resources`,
`spray-foam-vs-blown-in-comparator`, `xcel-rebate-eligibility-checker`.
The header line `claim set: 762 propositions resolved from 227 cited-stat
blocks, 140 shared constants, 148 referenced assets` is consistent with CITE
rows being attributed to every page that REFERENCES a proposition rather than to
the page whose bytes carry it — that mechanism is inference; the absence is
measurement. Either way a reader sent to `index.html` will not find the sentence,
and ~20% of DCI's remaining blocking count sits in this class.

**(b) DCI R9's `N3-unverifiable` row is a declaration of inability, not a
content defect, and it is blocking.** The row reads `tool payload field(s)
['lf-calc-inputs', 'lf-calc-output'] not found in the page`. Measured: both
strings occur exactly once each on `public/r-value-needed-calculator.html`, and
in both cases only inside
`var i=document.getElementById('lf-calc-inputs'), o=document.getElementById('lf-calc-output');`
— there is no static `id="lf-calc-inputs"` in the markup
(`/usr/bin/grep -o 'id="lf-calc-[a-z]*"'` → 0; control, all `id=` attributes → 29).
This is the same state `GATE_SCORE_2026-09-17.md` §4.1 MISS 7 recorded at
`cb675ab`: the ids are created at runtime, so R9's presence check cannot see
them. Half of DCI's R9 blocking count is this row.

**(c) `ops/hooks/commit-msg` is installed on DCI only.** Measured:
```
denvercoloradoinsulation.com      core.hooksPath=ops/hooks   hook file present
longmontcoloradoinsulation.com    core.hooksPath=NONE        hook file ABSENT
greeleycoloradoinsulation.com     core.hooksPath=NONE        hook file ABSENT
```
The verification-trailer ruling is enforced on one of three properties. Not
fixed here: installing a hook is an infrastructure change outside this row's
scope, and doing it mid-release would have changed the commit path of the very
commits being verified.

**(d) GCI's gate reports one OWED config key**, `R3.t3_adjudication_2026_09_18`
in `config/gci.json:318`. It is a long documentation string recording why T3 was
deliberately not narrowed, but it does not carry the documentation-only marker
the other 34 such keys carry, so the gate's own "a rule that silently does not
exist" check flags it. It does not affect GCI's exit 0. Not fixed here: editing
the config would desync it from the artifact already verified and shipped.

---

## 5. State of the checkouts

Six worktrees were created under `/tmp/gate-close/r5/` (three pinned to the
production commits, three carrying the staged bytes) and all six removed. No
main working tree was ever checked out to a different commit. Pre-existing
worktrees under `~/code/canon-wt/` belong to other sessions and were not touched.

```
calibrated-design-canon         eafada2   clean   0 0
denvercoloradoinsulation.com    bdf6701   clean   0 0
longmontcoloradoinsulation.com  4211b8d   clean   0 0
greeleycoloradoinsulation.com   3a1357f   clean   0 0
```

Canon board open cards: **0 before, 0 after** (intake 0, ready 0, in-flight 0;
done 16). This row created no card and edited no lane.
