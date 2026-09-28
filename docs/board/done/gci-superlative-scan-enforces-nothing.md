---
id: gci-superlative-scan-enforces-nothing
owner: executor
type: defect
created: 2026-09-28
retriage: 2026-10-12
size: S
severity: medium
---
# GCI's `ops/superlative_scan.py` is report-only and unwired, so its 26 retired superlatives can silently return

DCI and GCI both carry `ops/superlative_scan.py`. They are not the same
instrument, and only one of them is a gate.

Measured 2026-09-28:

```bash
grep -c RETIRED_PATTERNS ~/code/denvercoloradoinsulation.com/ops/superlative_scan.py   # -> 3
grep -c RETIRED_PATTERNS ~/code/greeleycoloradoinsulation.com/ops/superlative_scan.py  # -> 0
grep -c superlative      ~/code/denvercoloradoinsulation.com/regen_all.sh              # -> non-zero
grep -c superlative      ~/code/greeleycoloradoinsulation.com/regen_all.sh             # -> 0
```

- **DCI** has a `RETIRED_PATTERNS` regex, a `--retired` mode that exits
  non-zero when an adjudicated string renders, and a `regen_all.sh` line that
  runs it. A retired superlative reappearing there is a build failure.
- **GCI** has `--self-test` and a deliberately noisy `--list` net, and nothing
  else. There is no `--retired` mode, no adjudicated pattern set, and no
  script invokes the file. It runs only when a session types it by hand.

GCI's own `COPY_VOICE.md` ("Ranking superlatives — standing rule and the
instrument that enforces it", added 2026-09-27) records **26 patterns
retired** on that property, the sharpest being *"the highest return per dollar
spray foam offers in a typical house"*. Nothing stops any of those 26 from
being reintroduced by the next generator edit. The section's title claims an
instrument that enforces; the instrument reports.

This is the same defect class the portfolio has now hit three times —
`_check_links.py`, `_intra_similarity_check.py` and `ops/claim_gate.sh` each
existed for weeks before any script invoked them, and each repo's
`regen_all.sh` carries a comment saying so. A gate nobody calls is a habit.

## The fix, when someone takes it

Port DCI's `RETIRED_PATTERNS` block and `--retired` mode to GCI, seeded from
the 26 patterns GCI's own `COPY_VOICE.md` already adjudicates, then wire
`python3 ops/superlative_scan.py public --retired` into `regen_all.sh`. DCI's
`regen_all.sh` states the standing precondition for wiring a gate: wire it
only where the property **exits 0 at the point of wiring**, because a gate
wired into a build it fails is a red build nobody can act on. So measure
first — run the ported `--retired` against GCI's current `public/` and fix
any hits before the wiring lands, not after.

Do **not** copy DCI's pattern list verbatim. The two properties retired
different strings, and DCI's list includes `highest residential radon`, which
is a DCI adjudication. GCI's radon sentence was **sourced**, not retired (see
`greeleycoloradoinsulation.com/COPY_VOICE.md`, "Radon — the unsourced Colorado
claim, sourced 2026-09-28"), so that pattern does not belong in GCI's list.

Check Longmont for the same asymmetry in the same pass.

## Verification when done

```bash
cd ~/code/greeleycoloradoinsulation.com
python3 ops/superlative_scan.py --self-test          # instrument fires: exit 0
python3 ops/superlative_scan.py public --retired     # exit 0 on clean tree
grep -c superlative regen_all.sh                     # -> non-zero
bash regen_all.sh; echo $?                           # -> 0
```

Then prove it can fail: reintroduce one adjudicated string into a generator,
regenerate, and confirm `regen_all.sh` exits non-zero.

## Source

Found 2026-09-28 by row R3 of the `harness-hardening-2026-09-28` lane while
correcting DCI's radon record — the row had to read both properties'
`superlative_scan.py` to decide whether GCI's radon sentence belonged in a
retired-pattern list, and found GCI has no such list to belong to. Out of that
row's scope (its remit was the radon verdict and the unsourced-radon class
sweep), and wiring a new build-failing gate needs the exits-0 precondition
measured first, so it was carded rather than folded in.

## Closed

Closed by Director ruling 2026-09-28: won't do; GCI live copy is already
clean.

**Verification:**

```bash
grep -A5 "^## Closed" docs/board/done/gci-superlative-scan-enforces-nothing.md
```

Commit: `002ca34` (row R1, lane `close-down-rev2-2026-09-28`)
