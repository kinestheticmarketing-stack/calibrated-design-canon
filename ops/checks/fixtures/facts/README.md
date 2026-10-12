# facts fixture (K50)

Shared fixture for the six `facts_*` modules (schema, review_due, quote_snapshot,
pages_coverage, citation_registry, caveat_distance).

- `clean/` is a whole site with zero findings: `public/` (index, attic, rebates, llms.txt),
  `facts/registry.json` (4 records), `facts/snapshots/<key>.txt`, and `manifest.json`
  enabling all six modules (data paths relative to `clean/`).
- FIXED TODAY is 2026-10-12. Dates on disk are written for it: retrieved.date and
  status.as_of 2026-10-02, next_review 2026-12-31. test_facts.py rewrites every date
  relative to its own fixed `today` in a temp copy (today-10, today-10, today+80).
- `variants/<module>/` holds overlay files (full replacement copies, same relative paths
  as under `clean/`) copied over a temp copy of `clean/`, plus `variant.json`:
  `{"module", "expected", "dates": {"<key>": {"<field.path>": <day offset from today>}}, "description"}`.
  Date offsets are applied after the default rewrite. Only the named module's count is asserted.
- Fingerprints are sha256 of `normalize(quote.text)` (see ops/facts/validate_facts.py).
