---
id: similarity-gate-excludes-the-shared-pages
owner: architect
type: defect
created: 2026-08-20
priority: 10
---
# The duplication gate excludes exactly the pages where duplication lives

`_intra_similarity_check.py:67`, **byte-identical in all three property repos**:

```python
EXCLUDE = {'404.html', 'privacy.html', 'contact.html', 'about.html'}
```

Those four are the pages ported near-verbatim between siblings. The gate skips
them, then reports zero.

**Measured on AUTHORED content (B7), chrome stripped** — `privacy.html` shares a
**726-word identical run** with both siblings:

| pair | longest identical run | word counts |
|---|---|---|
| DCI ↔ LGM | 726 words | 1046 / 1031 |
| DCI ↔ GCI | 726 words | 1046 / 989 |

## Why this is a gate defect, not a content defect

The exclusion is **defensible for intra-property scoring** — a privacy page and
a contact page should not be flagged as duplicates of each other. It is
**exactly backwards for cross-property scoring**, which is the risk this
portfolio actually carries: three geo-cloned sites in one vertical.

The gate was built for one question and cited as answering the other.

## Blast radius — this is the part that matters

**"Authored duplication is ZERO on all three properties" was asserted
repeatedly, including in `docs/board/ground-truth.md` on all three properties
during the corpus re-score wave, and in the Zarr-supersession entry.** That
claim is true only of the non-excluded pages. It was never true of the corpus.

Every verdict resting on this instrument is affected. In LLS Wave 1: DCI and
GCI both scored LLS-13 and LLS-41 APPLIED from it; both are now RETRACTED.
LGM scored NOT-APPLIED because that agent stopped trusting the gate — the only
correct duplication verdict on the board, and it was correct for the right
reason.

## Proposed fix — NOT applied here

Split the exclusion by axis:
- **Intra-property run:** keep the exclusion. The rationale holds.
- **Cross-property run:** include the four, and treat a high score on them as
  expected-and-accepted (they are meant to be similar) or as a finding — but
  **measure it**, and let the number be visible rather than absent.

Add a canary per B10: plant a known duplicate pair in an excluded file and
confirm the cross-property run reports it. The current gate would report zero.

Also correct the three `ground-truth.md` files, which currently state the
unqualified zero.

## Verification command
```bash
grep -n "^EXCLUDE" /Users/vongimbel/code/*coloradoinsulation.com/_intra_similarity_check.py
# identical in all three; then measure what it skips:
python3 - <<'PY'
import re,difflib
def w(p):
    t=open(p,errors='ignore').read()
    t=re.sub(r'<(script|style)\b.*?</\1>','',t,flags=re.S|re.I)
    return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',t)).split()
a=w('/Users/vongimbel/code/denvercoloradoinsulation.com/public/privacy.html')
b=w('/Users/vongimbel/code/longmontcoloradoinsulation.com/public/privacy.html')
print('longest identical run:', difflib.SequenceMatcher(None,a,b).find_longest_match(0,len(a),0,len(b)).size)
PY
# expect 726
```
