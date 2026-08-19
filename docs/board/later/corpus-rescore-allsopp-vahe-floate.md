---
id: corpus-rescore-allsopp-vahe-floate
owner: auditor
type: chore
created: 2026-08-19
size: L
lane: audit
---
# Three corpora have never been re-scored since their original pass

Only Zarr got a second pass (2026-08-19) and found 7 of 50 verdicts wrong or
stale, plus a 327-line citation drift in the one prior audit with any
baseline at all. Allsopp, Vahe, and Floate were each scored once
(2026-08-09/12) and never revisited despite four remediation waves changing
every property since. Same shape as the Zarr wave — worth its own dedicated
pass, not squeezed in alongside other work.

---

## Deferred — 2026-08-19 (Ruling 18 — deferred by Director)

**Explicitly deferred. Instrument recorded so it is not re-derived:** authored-
content scoring — 5-word shingles, Jaccard, threshold 0.3, boilerplate removed
empirically at >=25%-of-pages. Never score rendered HTML.

Baseline: authored duplication is ZERO on all three properties as of
2026-08-19. Non-zero on re-score means regression *or* a reverted boilerplate
setting — verify the instrument before believing the finding.

**Card stays open. State above is verified, not assumed.**
