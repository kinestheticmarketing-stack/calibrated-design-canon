# Claim gate — wiring and release record, 2026-09-18

R5 of a 6-row pass. This row re-scored the gate, wired it into the builds that
pass it, and shipped all three properties. It was the only row authorised to
deploy. It changed no page, no copy and no generator.

Gate under test: canon `ops/claim_gate/` at canon HEAD `eafada2`.

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
