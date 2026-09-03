---
id: r4-free-quote-sweep-141-pages
owner: director
type: decision
created: 2026-08-21
priority: 40
retriage: 2026-09-16
classification: DIRECTOR
---
**Classification reasoning (2026-09-02):** Genuine scope/risk tradeoff (how large a voice-gated rendered-copy batch to authorize) with no single correct cap, plus the replacement copy itself is user-facing and voice-gated under standing portfolio rule — correctly Director's call.

# R4 — the quote-phrase sweep is 141 pages and needs its own wave

R4 was chartered HELD, DRAFT ONLY, with the Director capping the batch. This
card carries its EN-1 destination so it does not sit as an open finding.

## Measured scope, case-insensitive, all three properties

| literal | LGM | DCI | GCI |
|---|---|---|---|
| `free quote` / `Free Quote` (any casing) | 44 / 128 | 66 / 184 | 31 / 86 |
| `Free Quotes` (any casing) | 19 / 57 | 21 / 81 | 10 / 51 |
| `quotes are free` | 0 | 0 | 0 |
| `no-cost quote` | 0 | 0 | 0 |
| `no cost quote` | 0 | 0 | 0 |
| `complimentary quote` | 0 | 0 | 0 |
| **`free estimate` / `free estimates`** | **0** | **0** | **0** |

*(pages / occurrences)*

**141 pages** carry some quote-family phrase. That is larger than any single
remediation wave in this portfolio to date.

## Why this is a Director call, not an executor call

Every instance is **user-facing copy**. Under the standing ruling, replacement
copy is voice-gated — drafted, returned, never spliced. Drafting 141 pages of
replacements before the batch is capped produces work that is likely discarded.

**D-3 as chartered is ONE line:** `greeleycoloradoinsulation.com`
`insulation-greeley.html`'s `<title>`, which reads
`Greeley Insulation — Free Quotes, Atmos Rebates Explained`. Source:
`_area_pages.py:65` `title_tag=`. There is no CTR_TITLES shadowing on GCI, so
that field is the live one.

The other 140 pages are scope the sweep surfaced, not scope D-3 chartered.

## Per-file ledger, for whatever cap is set

- **LGM** (5 files): `_area_pages.py`, `_generate_area_pages.py`,
  `_generate_homepage.py`, `_generate_resources.py`, `_generate_service_pages.py`
- **DCI** (6 files): `_generate_suburb_pages.py` (16), `_generate_service_pages.py` (3),
  `_generate_calculator_pages.py` (2), `_generate_best_companies.py`,
  `_generate_homepage.py`, `_generate_resources.py`
- **GCI** (3 files): `_area_pages.py` (9), `_generate_homepage.py` (2),
  `_generate_resources.py`

## Related finding, recorded here

The `free estimate` family returns **zero in every casing on all three
properties**. The earlier 113-page sweep held. That result now rests on a
canary-proven instrument: S5 detects 3 occurrences in the known-present GCI
title and returns 0 on a scrubbed copy.

**Not drafted, per the charter.** Set the cap and the drafts follow.

## CLOSED — 2026-09-02 — Ruling 4: CAP AT ZERO

Director ruling: cap this batch at **zero**. "Free quote" is not false and is
not costing anything measurable — no evidence in this card or elsewhere in
the portfolio shows it costing CTR, rankings, or trust. It became a card only
because a sweep found it, not because it was flagged as broken. Drafting 141
pages of voice-gated replacement copy against a phrase that isn't demonstrably
hurting anything is not warranted; that effort is better spent on findings
with an actual defect behind them.

This closes as a **decision not to act**, not an edit. No copy changed on any
of the three properties as a result of this card. D-3 (the one line R4 was
originally chartered to fix,
`greeleycoloradoinsulation.com/insulation-greeley.html`'s `<title>`) is
included in the zero cap — it is not carved out and drafted separately, since
carving out one line while ruling the other 140 not worth drafting would
contradict the "not costing anything measurable" reasoning for the one line
that happens to be a title tag rather than body copy.

If future evidence shows "free quote" measurably underperforming an
alternative (a CTR drop, a competitor pattern, a Director-supplied test),
re-open with that evidence attached — this closure does not forbid a future
card, it just closes this one with the cap recorded.

**Verify:**
```
grep -c "CAP AT ZERO" docs/board/done/r4-free-quote-sweep-141-pages.md
# -> 1

# No property repo touched by this closure -- decision-not-to-act, no edit:
for repo in greeleycoloradoinsulation.com denvercoloradoinsulation.com longmontcoloradoinsulation.com; do
  cd /Users/vongimbel/code/$repo && git status --short -- public/ '*.py' | wc -l
done
# -> 0, 0, 0 (no generator or public/ file touched in any property by this card's closure)
```
Commit: see `docs/lanes.md` lane `director-rulings-close-r4-canon` for the
exact hash landing this closure.
