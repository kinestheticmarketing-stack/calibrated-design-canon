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
