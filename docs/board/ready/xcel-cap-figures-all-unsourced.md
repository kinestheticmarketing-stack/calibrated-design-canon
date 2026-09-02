---
id: xcel-cap-figures-all-unsourced
owner: director
type: decision
created: 2026-08-21
priority: 10
retriage: 2026-09-16
---
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
