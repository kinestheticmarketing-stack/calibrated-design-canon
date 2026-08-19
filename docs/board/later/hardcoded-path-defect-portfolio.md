---
id: hardcoded-path-defect-portfolio
owner: executor
type: bug
created: 2026-08-17
size: L
lane: infra
---
# 36-file hardcoded-output-path defect, all three properties — owed before Fort Collins clones

DCI 12 files, LGM 10, GCI 16 — 38 assignments in 36 files, all resolving
output paths via `os.path.expanduser('~/code/{property}/...')` instead of
deriving from the script's own location. `_similarity_check.py` additionally
hardcodes a sibling repo's path on two of the three properties. Recorded as
a genesis-checklist rule in `METHODS/PROPERTY_GENESIS.md` so a *new*
property won't add instances — the 36 existing files are untouched.
Recommend one scoped wave across all three parents before Fort Collins
genesis begins: mechanical, uniform, provable by two-run regen determinism
plus a `public/` hash. Matching cards exist on each property's own board;
this card is the portfolio-level tracking point so the three don't get
fixed independently and inconsistently.
