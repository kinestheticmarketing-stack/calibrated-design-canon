---
id: documented-standard-with-no-validator
owner: architect
type: property-genesis-candidate
created: 2026-08-21
priority: 10
---
# PROPERTY_GENESIS candidate — two principles from five blind instruments in two days

DRAFT ONLY. Nothing written to `METHODS/PROPERTY_GENESIS.md`.

## Principle 1 — A documented standard with no validator is not a standard

Five instruments in two days returned clean, or governed behavior, while never
examining what they claimed to govern:

1. **Similarity gate** — `_intra_similarity_check.py:67` `EXCLUDE` omitted the
   four pages most likely to fail. Reported zero on a corpus with a 726-word
   identical run.
2. **GSC check** — measured the presence of a `google-site-verification` tag,
   never its validity. A `REPLACE_WITH_...` placeholder served in production
   and scored as verified.
3. **FORCE_STEP guard** — placed below `require('puppeteer-core')`, so on any
   host without that dependency it exited at MODULE_NOT_FOUND and never ran.
   Non-zero exit for the wrong reason is indistinguishable from success.
4. **Citation floor** — `COPY_VOICE.md:104` documents 2-3 per page.
   `validate_citation_set` checks duplicates only. No count check exists in any
   repo.
5. **`xcel_relevant` flag** — see Principle 2.

**Proposed rule:** every standard stated in prose must name the validator that
enforces it, or be explicitly marked UNENFORCED. A standard whose enforcement
cannot be pointed at is a preference. Each validator carries a canary proving
it fails when it should — a check that has only ever printed success is
indistinguishable from one that cannot fail.

## Principle 2 — Content presence must not be a side effect of citation bookkeeping

A new subtype: not a check that fails to look, but **rendered copy silently
gated on a data-structure side effect**.

`_generate_service_pages.py:118` read:

```python
xcel_relevant = any('XCEL' in k for k in rebate_cite_keys)
```

That made "is this page Xcel-relevant" and "does this page cite Xcel" the same
question. They are not: the first is a fact about the market's utility
structure, the second an artifact of which citation keys survive an edit.
Removing one false citation flipped the flag on 4 pages and deleted the
wayfinding sentence pointing readers at Xcel's own live page — the honest
sentence, and exactly what must survive when a stale figure is removed.

Decoupled 2026-08-21 and proven immune: stripping a different XCEL-prefixed key
from 8 services on a scratch copy left the sentence rendering on all 13 pages.

**Proposed rule:** a conditional that governs whether prose renders must read a
fact about the subject, never the membership or shape of a citation list.
Citation bookkeeping may decide whether a *citation* renders; it must never
decide whether a *sentence* does.

**Known remaining instance, carded not fixed:** `ew_relevant` at
`_generate_service_pages.py:129` is the identical pattern
(`any('EFFICIENCY_WORKS' in k for k in rebate_cite_keys)`). It was not
disturbed by this wave — no EFFICIENCY_WORKS key was removed — so it is
reported rather than changed. DCI and GCI have zero instances of the pattern;
it is LGM-only.


## Principle 3 — a presence check must assert the QUANTITY it protects

Added 2026-08-21. V4 is the sixth blind instrument: it counted PAGES CONTAINING
an anchor, not OCCURRENCES, and passed (`CFM50 17->17`) while three pages lost
two-thirds of their instances. It was the check added specifically to catch
content vanishing beside a removal target, and it was blind to exactly that.

Full detail: `presence-check-must-assert-quantity.md`.

Corollary: an instrument added to catch a specific failure must be
canary-proved AGAINST THAT FAILURE, not against its own happy path. V4 had a
positive canary for total absence and none for partial loss — the case it
existed for.
