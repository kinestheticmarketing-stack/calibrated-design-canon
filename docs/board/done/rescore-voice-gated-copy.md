---
id: rescore-voice-gated-copy
owner: director
type: decision
created: 2026-08-19
priority: 20
doc: METHODS/seo-geo/cr_voice_gated_drafts.md
retriage: 2026-09-16
classification: DIRECTOR
---
**Classification reasoning (2026-09-02):** All three items are rendered, user-facing copy/policy calls with real tradeoffs (accuracy-vs-length on live meta descriptions, whether 154 titles are worth shortening for a brand suffix, and an AI-disclosure policy gated on the still-open named-spokesperson ruling) — none is settled by a single primary-source check.

# Three copy decisions the corpus re-score surfaced and could not make

Every mechanical finding from the Allsopp/Vahe/Floate re-score is fixed and
shipped. These three are the remainder: all are rendered copy, which this
portfolio has ruled requires Director approval before it ships.

Drafts, measurements and reasoning: `METHODS/seo-geo/cr_voice_gated_drafts.md`

**1. Twenty-one over-length meta descriptions.** LGM 20, DCI 1, GCI 0. DCI's
own generator documents the contract as `<= 155 chars`. LGM is the outlier by
an order of magnitude — its worst is 241 characters. Each one carries a
specific local claim (utility name, rebate figure, R-value target) that has to
stay accurate to the page it fronts, which is why they are not mine to rewrite.

**2. No brand suffix on any of 154 titles.** Allsopp L16 and Vahe PCO-15 both
call for one; zero titles across the portfolio have one. The constraint that
makes this a decision rather than an edit: median title is already 54-56 chars
and 10 are already over 60, so a 30-character suffix means shortening 154
titles to make room — or ruling that the room is not worth it.

*Worth deciding together with Rulings 5-8*, since the four colliding titles are
exactly where a brand suffix would do real disambiguation work.

**3. AI-content supervision disclosure (Vahe PCO-05).** No policy exists. Not
drafted deliberately: it interacts with the standing product-not-people rule
and with the still-open named-spokesperson decision (Vahe PCO-02). Drafting it
before that decision lands produces copy that needs rewriting when it does.

## The one unblocking action

**Rule on the named spokesperson.** It gates item 3 here, Vahe PCO-02, and the
editorial-byline half of the author-identity gap that DCI's own module audit
has carried since 2026-07-08. One decision closes all three.

## CLOSED — 2026-09-02

All three items disposed of, none left open.

**1. Twenty-one over-length meta descriptions — ALREADY-FIXED, VERIFIED
AGAINST THE GATE PASS, not just re-asserted.** Independently re-measured
current `<meta name="description" content="...">` length on every rendered
page in all three properties' `public/*.html` (decoded HTML entities before
counting, matching each repo's own gate logic):

- GCI: 0 over 155 chars (38 pages scanned)
- DCI: 0 over 155 chars (73 pages scanned)
- LGM: 0 over 155 chars (49 pages scanned)

Zero over-length metas anywhere in the live portfolio today. The card's
original LGM 20 / DCI 1 / GCI 0 figures are stale and superseded by this
count. Also confirmed the coded gate is real, not just present in source: all
three repos carry `check_title_meta_length()` (`META_MAX = 155`,
`TITLE_MAX = 60`) wired unconditionally into `main()` in `_postbuild_check.py`
(not gated behind `--canary` or any flag), and each repo's own `--canary`
suite plants a real 156+/241-char violation and confirms `check_title_meta_length`
fires `META-LENGTH`/`TITLE-LENGTH`/`TITLE-META` — all three print
`CANARY PASS`. The gate exists and would reject a violation if one shipped.

**2. No brand suffix on 154 titles — RULED NO, per Ruling 2.** Titles win by
matching query intent nearly verbatim; that is the one pattern every top-20
page in this portfolio shares. Spending ~30 characters on a brand a homeowner
does not know costs the thing that works. No titles are shortened, no brand
suffix is added. `METHODS/seo-geo/cr_voice_gated_drafts.md`'s draft suffix
option is declined.

**3. AI-content supervision disclosure (Vahe PCO-05) — CLOSED by Ruling 1.**
Standing ruling, 2026-09-02: NO NAMED SPOKESPERSON ON RANK-AND-RENT
PROPERTIES, scoped to the rank-and-rent lead-gen portfolio (DCI, LGM, GCI, and
any future property on the same model; does not apply to agency/SaaS/any
property with a real operating business). Publisher-level attribution only.
This closes the AI-content-supervision-disclosure question, Vahe PCO-02, and
the author-identity gap in one ruling — no separate disclosure policy is
drafted, by design: a named-spokesperson disclosure would contradict the
publisher-level-only posture the ruling just adopted. Full ruling text:
`docs/board/ground-truth.md` (this repo) and
`denvercoloradoinsulation.com`/`longmontcoloradoinsulation.com`/
`greeleycoloradoinsulation.com`'s own `docs/board/ground-truth.md`.

**Verify:**
```
# Ruling 1 landed portfolio-wide:
grep -c "NO NAMED SPOKESPERSON ON RANK-AND-RENT" docs/board/ground-truth.md
# -> 1 (also 1 in each of DCI/LGM/GCI's own docs/board/ground-truth.md)

# Current over-length-meta count, zero everywhere:
for repo in greeleycoloradoinsulation.com denvercoloradoinsulation.com longmontcoloradoinsulation.com; do
  cd /Users/vongimbel/code/$repo && python3 - <<'EOF'
import re, glob, html
n=sum(1 for p in glob.glob('public/*.html')
      if len(html.unescape(re.search(r'<meta name="description" content="(.*?)"', open(p,encoding='utf-8').read(), re.S).group(1)))>155)
print(n)
EOF
done
# -> 0, 0, 0 (GCI, DCI, LGM)

# Gate is real and fires (not just present):
cd /Users/vongimbel/code/greeleycoloradoinsulation.com && python3 _postbuild_check.py --canary 2>&1 | grep "length:.*DETECTED"
cd /Users/vongimbel/code/denvercoloradoinsulation.com && python3 _postbuild_check.py --canary 2>&1 | grep -E "title-len|meta-len" | grep DETECTED
cd /Users/vongimbel/code/longmontcoloradoinsulation.com && python3 _postbuild_check.py --canary 2>&1 | grep "title-meta:.*DETECTED"
# -> each prints its planted-violation DETECTED line; all three print CANARY PASS
```
Commit: `f81dac4` (classification, prior pass) plus this pass's canon commit
landing the closure (see `docs/lanes.md` lane `director-rulings-close-r4-canon`
for the exact hash).
