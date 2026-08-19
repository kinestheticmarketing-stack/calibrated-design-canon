---
id: genesis-cwd-relative-paths
owner: architect
type: chore
created: 2026-08-19
priority: 10
lane: genesis
---
# PROPERTY_GENESIS: cwd-relative output paths are a genesis requirement, not a cleanup task

The 36-file hardcoded-output-path defect was closed portfolio-wide 2026-08-19
(DCI 12, LGM 9, GCI 16 assignments — 37 of 38, see each property's
`docs/board/done/hardcoded-path-defect-*.md`). Fort Collins must never
inherit it.

`METHODS/PROPERTY_GENESIS.md` Phase 4 item 9 already states the rule. This
card is to strengthen it from a stated rule to a **verified** one, because a
stated rule is exactly what this defect survived for months:

1. Phase 4 gains an explicit check, not just an instruction: after the
   scaffold is cloned, run the scratch-copy test before any content work.
   Copy the repo, regen in the copy, confirm the copy was written and the
   parent was not.
2. Phase 7 (pre-launch verification) gains the same test as a gate — it costs
   seconds and it is the only thing that actually proves the property.

**Why the stated rule was not enough.** `regen_all.sh` opens with
`cd "$(dirname "$0")"`, so every normal regen landed in the repo root and
masked the defect completely. It only surfaces when a generator is invoked
directly or the repo is copied. A genesis checklist that says "use
cwd-relative paths" and never tests it will pass while shipping the defect,
which is what happened three times.

**The negative control worth carrying into canon:** running the *pre-fix*
`_generate_404.py` from inside a scratch copy printed
`Wrote 404 page: /Users/vongimbel/code/denvercoloradoinsulation.com/public/404.html`
— it reached out of the copy into the live original. That one line is the
clearest statement of the defect anyone has produced; it belongs in the
genesis doc as the reason the test exists.

Also worth folding in: the correct pattern was already present in-repo the
whole time (`_check_links.py`, `_postbuild_check.py`, and two Longmont
generators). The genesis step should name that pattern rather than describing
it abstractly:

```python
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public')
```
