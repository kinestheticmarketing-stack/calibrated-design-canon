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

## Superseded

Superseded 2026-09-28: partially fixed — GCI's scan was run read-only and
measured at 708 raw hits (exit 1), so per the kickoff's own branch it was NOT
wired into the gate and no copy was changed; remaining items listed in the
FIX FOUR report for the Director.

Row U2 of the FIX FOUR pass. The card's premise turned out to be wrong in a
way that matters: GCI's `ops/superlative_scan.py` is not a variant of DCI's.
It has no `--retired` flag and **no retired-pattern concept at all** — it is a
deliberately wide, human-adjudicated net (its own docstring: noisy on purpose,
`honest`/`latest`/`interest`/`request` all land in it). Its self-test passes
8/8 surfaces, so the 708 is a real reading, not blindness. Wiring it would
produce a permanently red build — which GCI's own `regen_all.sh` forbids in
writing: *"a gate wired into a build it fails is a red build nobody can act
on."* No unsourced business-ranking claim was among the hits.

**Verification:**

```bash
cd ~/code/greeleycoloradoinsulation.com && python3 ops/superlative_scan.py; echo "EXIT=$?"
grep -c RETIRED_PATTERNS ops/superlative_scan.py   # 0 — the concept is absent
grep -c superlative regen_all.sh                   # 0 — deliberately not wired
```

No commit — measuring row. Lane `close-down-rev2-2026-09-28`.

## Superseded (final)

Superseded 2026-09-28: closed — GCI's scan is a human-review net by design, not a build gate; 708 hits contain no unsourced business-ranking claim. Its self-test was corrected in the same pass so it cannot pass while blind to body text.

Row K7 of the FINISH rev 2 pass, resolving what row U2 above deferred to the
Director. U2 measured honestly but rested on one thing that was not true: the
self-test it cited as proof that 708 was a real reading was itself defective.
`surfaces()` builds the `body` stream by stripping tags, which leaves
`<title>` text inside it — so the title plant satisfied the body control, and
`SELF_TEST=PASS (8 surfaces planted, 8 caught)` printed while the scanner was
blind to the body surface, 403 of the 708 hits. `d268765` tags each plant with
its own surface, so every control must now see its own plant in its own
stream. Real detection is unchanged: `RAW_HITS=708`, exit 1.

The card's proposed fix — port DCI's `--retired` mode and wire it into
`regen_all.sh` — stays not-done, and that is the ruling rather than an
omission. GCI's scan is not a variant of DCI's; it has no retired-pattern
concept because it is a different instrument, a deliberately noisy net for
human adjudication (`honest`/`latest`/`interest`/`request` all land in it).
Wiring it would produce exactly the permanently red build GCI's own
`regen_all.sh` forbids in writing. `grep -c superlative regen_all.sh`
returning 0 is the intended state here, not the defect.

**Verification:**

```bash
cd ~/code/greeleycoloradoinsulation.com
git log --oneline -1 d268765                            # the self-test correction
python3 ops/superlative_scan.py --self-test | tail -1   # SELF_TEST=PASS (8 surfaces planted, 8 caught)
python3 ops/superlative_scan.py > /tmp/sup.txt; echo "EXIT=$?"   # EXIT=1
grep -c 'RAW_HITS=708' /tmp/sup.txt                     # 1
awk -F'\t' '$2=="body"' /tmp/sup.txt | wc -l            # 403 — the surface the old self-test was blind to
grep -c superlative regen_all.sh                        # 0 — not wired, by design
```

Commit: `d268765` (GCI `main`). Row K7, FINISH rev 2 pass.
