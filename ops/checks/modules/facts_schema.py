"""facts_schema -- the property's facts registry is not a valid registry.

Gap: schema/registry validity (the substrate the K02/K03/K04/K08/K22
facts_* modules read; they skip malformed fields, this module reports them).
Wraps ops/facts/validate_facts.py:
validate() checks facts/registry.json against ops/facts/schema.json plus the
checks a schema cannot express (duplicate keys, territory/territory_evidence
town pairing, UNKNOWN needs absence_reason, real calendar dates,
retrieved.fingerprint == fingerprint(quote.text)). One finding per validator
error string; page = the registry path, message = the error.

Data keys: facts_registry (path to facts/registry.json). An unreadable
registry (missing, not JSON, top level not an array) raises FactsUnreadable:
the module cannot judge, so the run exits 2.

NOT ENABLED on any site unless that site's manifest names it.
"""

import importlib.util
from pathlib import Path

_VF_PATH = Path(__file__).resolve().parents[2] / "facts" / "validate_facts.py"
_spec = importlib.util.spec_from_file_location("_facts_schema_validate_facts", _VF_PATH)
validate_facts = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate_facts)

NAME = "facts_schema"
DESCRIPTION = ("facts/registry.json fails ops/facts/validate_facts.py (schema, "
               "duplicate key, territory pairing, dates, fingerprint).")
REQUIRES = {
    "facts_registry": "the property's facts registry (facts/registry.json)",
}


def check(ctx):
    path = ctx.data["facts_registry"]
    return [ctx.finding(path, err) for err in validate_facts.validate(path)]
