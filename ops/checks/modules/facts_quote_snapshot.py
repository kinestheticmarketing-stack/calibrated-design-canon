"""facts_quote_snapshot -- a registry quote no longer matches its stored source.

Gap K03 (script half). Every facts/registry.json record carries quote.text
(the words the claim rests on) and retrieved.fingerprint (sha256 of the
normalized quote at retrieval). The stored source text lives at
<facts_snapshots>/<key>.txt. This module catches a quote that drifted away
from its source or from its own fingerprint:

  * snapshot file missing                               -> 1 finding
    (the substring check is then skipped for that record)
  * normalize(quote.text) not in normalize(snapshot)    -> 1 finding
  * retrieved.fingerprint != fingerprint(quote.text)    -> 1 finding
    (independent of the snapshot; both quote modes)

Matching uses validate_facts.normalize (THE facts normalizer) and
validate_facts.fingerprint. Malformed fields are skipped silently
(facts_schema reports them); an unreadable registry raises FactsUnreadable
(the run exits 2).

Data keys: facts_registry (path to facts/registry.json), facts_snapshots
(path to the facts/snapshots directory). No options.

NOT ENABLED unless a site manifest names it.
"""

import importlib.util
import re
from pathlib import Path

_VF_PATH = Path(__file__).resolve().parents[2] / "facts" / "validate_facts.py"
_spec = importlib.util.spec_from_file_location("_facts_validate_facts", _VF_PATH)
validate_facts = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate_facts)

NAME = "facts_quote_snapshot"
DESCRIPTION = ("A facts registry quote is absent from its stored source "
               "snapshot (or the snapshot is missing), or its "
               "retrieved.fingerprint does not match the quote.")
REQUIRES = {
    "facts_registry": "the property's facts registry (facts/registry.json)",
    "facts_snapshots": "the stored source snapshots directory (facts/snapshots)",
}

_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def check(ctx):
    findings = []
    reg_path = ctx.data["facts_registry"]
    snap_dir = Path(ctx.data["facts_snapshots"])
    records = validate_facts.load(reg_path)
    for rec in records:
        if not isinstance(rec, dict):
            continue
        key = rec.get("key")
        quote = rec.get("quote")
        text = quote.get("text") if isinstance(quote, dict) else None
        if not isinstance(text, str) or not text:
            continue
        label = key if isinstance(key, str) else "?"

        if isinstance(key, str) and _KEY_RE.match(key):
            snap = snap_dir / (key + ".txt")
            if not snap.is_file():
                findings.append(ctx.finding(
                    snap, "%s: snapshot file missing" % key, text))
            elif validate_facts.normalize(text) not in \
                    validate_facts.normalize(ctx.read_text(snap)):
                findings.append(ctx.finding(
                    snap, "%s: quote.text not found in its source snapshot"
                    % key, text))

        retrieved = rec.get("retrieved")
        fp = retrieved.get("fingerprint") if isinstance(retrieved, dict) else None
        if isinstance(fp, str) and fp != validate_facts.fingerprint(text):
            findings.append(ctx.finding(
                reg_path, "%s: retrieved.fingerprint does not match "
                "fingerprint(quote.text)" % label, text))
    return findings
