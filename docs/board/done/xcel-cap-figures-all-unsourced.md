---
id: xcel-cap-figures-all-unsourced
owner: director
type: decision
created: 2026-08-21
priority: 10
retriage: 2026-09-16
classification: ALREADY-DONE
---
**Classification reasoning (2026-09-02):** Both flagged DCI-incomplete items are resolved — the "worked calculations" class was closed by the Director ruling recorded ~12 minutes later the same day in `removed-cap-reasoning-passages.md` (same three pages, same commit range), and the card's own text marks the missed `$400` variant "now fixed"; LGM is already marked complete.

# $400, $500 and $350 are all unsourced — all removed, restoration is a separate wave

## The finding

All three Xcel per-measure cap figures traced to **the same removed
royalcomforths.com document** — a Denver HVAC contractor's website carrying a
PDF, cited under anchor text reading "According to Xcel Energy." When R1
removed that citation as a false attribution, **every figure it sourced became
unsourced**, not just the one the wave happened to enumerate.

**B6 does not distinguish figures by which one a wave noticed.**

- **$400** (air sealing) — removed under R3. Xcel's own sheet states **$200**.
- **$500** (attic) — same document, never independently sourced.
- **$350** (wall) — same document, never independently sourced.

$500 was **live in production on LGM** in quick-facts and calculator output as
"30%-of-cost-capped-at-$500" until 2026-08-21.

## What shipped instead (Option 2)

The claim the repo can support: *the program exists, pays 30% of project cost
against per-measure caps, by check after application.* No figure asserted, no
enumeration to truncate.

## LGM — complete, commit 25c82b7

$400/$500/$350 as rebate figures: **0 rendered**. Cost ranges retained and
distinguished ($300-$1,200 air sealing install, $200-$500 audit).

## DCI — INCOMPLETE, halted for a ruling

Enumerations removed. **Two classes remain and are NOT enumerations:**

1. **Worked calculations that reason with the cap** — `insulation-hybrid-flash-batt`
   ("the $500 attic cap is reached on essentially every hybrid project, so the
   rebate is effectively a flat $500 rather than 30% of a larger number"),
   `xcel-insulation-rebate-guide-denver` ("A $3,000 attic top-up runs 30% to
   $900 on paper, but the attic cap stops it at $500"),
   `whole-home-efficiency-bonus-stacking-denver` ("the attic measure typically
   hits its $500 ceiling … for an estimated $590-$860").
   Deleting the figure guts the reasoning and leaves an ALTERED claim; deleting
   the whole passage removes several paragraphs of genuine explanatory content.

2. **A $400 instance R3 missed entirely** — now fixed, but worth recording:
   `xcel-insulation-rebate-guide-denver` phrased it *"air sealing at 30% up to
   $400"*, which the needle `$400 for air sealing` never matched. **R3 was
   needle-scoped and a variant phrasing escaped it.** The earlier "V3 DCI = 0"
   was true of the needle, not of the figure.

## If figures are later sourced from Xcel's own PDF

Restoring them is a **separate voice-gated wave**. Xcel's program pages return
empty SPA shells to a fetcher; the PDFs are the working path.

## R2 outcome note — 2026-09-02

Re-verified independently. The card's own DCI-INCOMPLETE section names two
open classes; both are closed:

1. **Worked calculations that reason with the cap** — resolved by the same
   Director ruling (M3 Option 2) recorded in DCI commit `83d4795`
   ("Remove the unsourced cap figures and the arguments built on them",
   2026-08-21 15:53:31 -0600), which removed all three passages this
   card's class 1 names (`insulation-hybrid-flash-batt`,
   `xcel-insulation-rebate-guide-denver`,
   `whole-home-efficiency-bonus-stacking-denver`) whole. This is also the
   ruling closing the sibling card `removed-cap-reasoning-passages.md`
   (same commit, same three pages) — confirmed by cross-reading both cards
   against the same DCI commit range, not by trusting either card's text
   alone.
2. **The missed `$400` variant phrasing** — the card's own text already
   marks this "now fixed"; folded into the same `83d4795` removal.
3. **LGM** — the card already records this complete at commit `25c82b7`.
   Re-verified directly: `25c82b7`'s message states "Director ruling M3
   Option 2," and no `$400`/`$500`/`$350` rebate-cap figure is present in
   LGM's current rendered `public/*.html`.

No open DCI or LGM work remains under this card. GCI is out of scope for
this card (it never had the porting exposure — see `ported-xcel-content-audit.md`).

**Verify:**
```bash
cd /Users/vongimbel/code/denvercoloradoinsulation.com
git show -s --format=%B 83d4795 | grep -q "Director ruling M3 Option 2" && echo RULING_CONFIRMED
cd /Users/vongimbel/code/longmontcoloradoinsulation.com
git show -s --format=%B 25c82b7 | grep -q "Director ruling M3 Option 2" && echo RULING_CONFIRMED
grep -rc "effectively a flat \$500\|30%-of-cost-capped-at-\$500" public/*.html | grep -v ':0$'
# no output = zero rendered occurrences of the retired cap phrasing on LGM
```
