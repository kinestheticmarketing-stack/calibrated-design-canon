---
id: instrument-lessons-2026-09-27
owner: executor
type: chore
created: 2026-09-27
retriage: 2026-10-04
size: S
lane: closeout-2026-09-27-canon
---
# Land the two 2026-09-27 instrument lessons in canon (axe viewport, `.focus()` vs Tab)

The 2026-09-27 transcript-alignment pass produced two instrument lessons that
exist only in a transcript and must reach canon:

1. **A single-viewport axe run is not an accessibility check.** axe at one
   width cannot see overflow-only violations, because whether a region
   overflows is a function of viewport width.
2. **`.focus()` is not a keyboard check.** `.focus()` cannot move focus to a
   `visibility: hidden` element, so a scripted probe false-FAILS a control a
   real user reaches by sequential Tab.

Landing sites:

- `METHODS/DESIGN_REVIEW.md` — the pre-launch/redesign checklist (added
  `fb4cf78`). Accessibility bullet gets the two-viewport + Tab rule.
- `METHODS/ARCHITECT_DISCIPLINE.md` — this canon's blind-spot catalogue
  (numbered PATTERN entries, FAILURE MODE / CANON RULE / PRACTICAL
  IMPLEMENTATION). Both lessons are the Pattern 14 class: a check that is
  green while blind to the condition it names.
- Dating ruling: `"Last updated"` publishes the last visible-text change
  date; `"Last reviewed"` is never derived. Belongs in `DESIGN_REVIEW.md`
  and in `docs/board/ground-truth.md` as a portfolio-level settled decision,
  because it governs the footer of every page on all three properties.

## Closed 2026-09-27 — all three landed

Commits: claim `47f15c8`, checklist + ground truth `a95df44`, blind-spot
catalogue `ef844ae`, this closure `<this commit>`.

The blind-spot catalogue turned out to BE `METHODS/ARCHITECT_DISCIPLINE.md`'s
numbered PATTERN series — the doc `ground-truth.md` cites for Patterns 11, 13
and 14. Both lessons landed there as one Pattern 24 with two named instances,
following Pattern 14's precedent of carrying several instances of one
mechanism, and filed as a NEW pattern rather than an extension of 14 because
14's canary cannot catch this class: a canary proves an instrument fires, not
that it was pointed at the defect. No new top-level document was created.

The dating ruling was asked for in `DESIGN_REVIEW.md` §6. §6 is "Portfolio
constraints (rank-and-rent properties)" and covers no dating at all; §4's
"Neglect signals" bullet is the one that governs stale dates, so it went
there. Reported as a mismatch rather than renumbered.

Verification, all four run from the canon repo root:

    grep -n "^PATTERN 24 " METHODS/ARCHITECT_DISCIPLINE.md
    # -> 1659:PATTERN 24 — AN INSTRUMENT SEES ONLY WHAT ITS CONFIGURATION ADMITS

    grep -c "^REPRODUCTION" METHODS/ARCHITECT_DISCIPLINE.md
    # -> 2   (one per instance, per the repo's carry-the-command rule)

    python3 -c "import re; t=re.sub(r'\s+',' ',open('METHODS/DESIGN_REVIEW.md').read()); print(t.count('Run axe at 375px AND 1280px; a single viewport misses overflow-only violations.'), t.count('publishes the last visible-text change date'))"
    # -> 1 1

    grep -c 'LAST REVIEWED" IS NEVER DERIVED' docs/board/ground-truth.md
    # -> 1

The two claims the ruling rests on are themselves verifiable in this repo:

    grep -n "A date is a claim about a human act" ops/claim_gate/RULES_SPEC.md
    # -> 2991
    grep -n "73 of 75 pages publish a 2026-09-27" ops/claim_gate/RULES_SPEC.md
    # -> 3005
