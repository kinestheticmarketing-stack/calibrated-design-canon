---
id: atomic-answer-band-portfolio
owner: director
type: decision
created: 2026-08-17
tags: [discussion]
---
# DIRECTOR: standardize the portfolio atomic-answer word-count band?

DCI enforces 40-60 words; LGM and GCI enforce 54-60. No ruling exists on
whether to standardize. Matching card exists on DCI's board with the full
context.

**Unblocking action:** one band for all three, or DCI stays a documented
exception.

---

## Closed — 2026-08-19

**Commit:** `(Ruling 1)`

**Director Ruling 1, canon copy.** The atomic-answer band is deliberately NOT
unified across the portfolio: Denver 40-60, Longmont and Greeley 54-60.

Canon principle established: **working code is not rewritten to match a
document.** The document is corrected to describe what the code enforces. Each
property's `COPY_VOICE.md` already did this correctly.

Ruled and closed. Not to be re-opened.

**Verification command:**
```bash
grep -rn 'NOT unified portfolio-wide' /Users/vongimbel/code/*coloradoinsulation.com/docs/board/ground-truth.md   # expect 3 hits
```
