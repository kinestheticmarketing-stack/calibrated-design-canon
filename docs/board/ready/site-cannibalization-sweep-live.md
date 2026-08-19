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
