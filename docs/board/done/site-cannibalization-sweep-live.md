---
id: site-cannibalization-sweep-live
owner: director
type: chore
created: 2026-08-10
priority: 10
---
# Run the live site: cannibalization sweep against all three properties

Flagged 2026-08-10, re-flagged repeatedly, still never run — this
environment cannot query the live Google index. The offline equivalent
(internal near-duplicate measurement) ran 2026-08-19 and found real
contested queries on all three properties: LGM's homepage vs its own
Longmont page (0.377 similarity, direct head-term collision), GCI's
three-way "greeley insulation" head-term contest, DCI's suburb-page
doorway-pattern cluster. The live `site:` query is the one piece the
offline method cannot substitute for.

---

## Closed — 2026-08-19

**Commit:** `(Ruling 20 — closed as not machine-executable)`

**Director Ruling 20. Closed with a manual procedure rather than a tool,
because a tool here would be theatre.**

Live query-cannibalization cannot be measured from the repo. It needs Search
Console impression/position data per query per URL — data this codebase does
not have and cannot synthesise. Any script claiming to detect it from page
text would be measuring similarity and *calling* it cannibalization.

**Similarity is not cannibalization.** The sweep established this: authored
duplication is ZERO on all three properties, yet the one genuine head-term
collision (GCI `index` vs `insulation-greeley`, Jaccard 1.00 on title intent)
scores *below* the duplication threshold on authored copy. The instrument that
finds one is blind to the other.

Procedure recorded for the next wave: pull GSC Performance filtered to a head
term, list URLs receiving impressions for it, and flag any term where two URLs
from the same property both rank. That is a human-with-GSC task.

**Verification command:**
```bash
python3 _intra_similarity_check.py   # run in each property; authored=0 is the standing baseline
```
