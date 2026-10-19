"""validate_facts -- validate a property's facts/registry.json.

Usage: python3 ops/facts/validate_facts.py <registry.json>
Exit 0 valid / 1 invalid (one line per error) / 2 unreadable.

Validation = ops/facts/schema.json (interpreted by the small stdlib schema
interpreter below, which implements exactly the keyword subset named in the
K50 spec and raises on any other keyword) + the checks a schema cannot
express: duplicate keys, territory/territory_evidence town pairing, real
calendar dates, and retrieved.fingerprint == fingerprint(quote.text).

One error string per defect, "<key or #index>: <json-path>: <message>". No
cascades: a value of the wrong type yields one error and is not descended into.
"""

import datetime
import hashlib
import html
import importlib.util
import json
import re
import sys
from pathlib import Path

_RS_PATH = Path(__file__).resolve().parents[1] / "checks" / "modules" / "retired_strings.py"
_spec = importlib.util.spec_from_file_location("_facts_retired_strings", _RS_PATH)
_rs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_rs)
_collapse = _rs._collapse
_unjs = _rs._unjs

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.json"

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_FP_RE = re.compile(r"^[0-9a-f]{64}$")
_DATE_FIELDS = (("retrieved", "date"), ("status", "as_of"), ("next_review",))


def normalize(text):
    """THE facts normalizer. This IS retired_strings' decoded-surface
    normalizer, _collapse(_unjs(html.unescape(text))), with _collapse and
    _unjs imported from ops/checks/modules/retired_strings.py. No new rules."""
    return _collapse(_unjs(html.unescape(text)))


def fingerprint(text):
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()


class FactsUnreadable(ValueError):
    """Registry file is unreadable, not JSON, or its top level is not a list."""


def load(path):
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise FactsUnreadable(f"{path}: cannot read: {e}") from None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise FactsUnreadable(f"{path}: not JSON: {e}") from None
    if not isinstance(data, list):
        raise FactsUnreadable(
            f"{path}: top level is {type(data).__name__}, expected a JSON array")
    return data


# --- schema interpreter (exactly the spec's keyword subset) ----------------

_ANNOTATIONS = {"$schema", "$id", "title", "description", "format", "$defs"}
_KEYWORDS = {"$ref", "type", "properties", "required", "additionalProperties",
             "items", "minItems", "uniqueItems", "enum", "const", "pattern",
             "minLength", "minimum", "anyOf", "if", "then"}


def _is_type(v, t):
    if t == "null":
        return v is None
    if t == "boolean":
        return isinstance(v, bool)
    if t == "integer":
        return (isinstance(v, int) and not isinstance(v, bool)) or (
            isinstance(v, float) and v.is_integer())
    if t == "number":
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    if t == "string":
        return isinstance(v, str)
    if t == "array":
        return isinstance(v, list)
    if t == "object":
        return isinstance(v, dict)
    raise ValueError(f"schema: unknown type {t!r}")


def _canon(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False)


def _as_path_tuple(p):
    """Tuple paths pass through unchanged; "" -> (); any other str, Path or
    non-tuple value -> (str(p),)."""
    if isinstance(p, tuple):
        return p
    s = p if isinstance(p, str) else str(p)
    return () if s == "" else (s,)


class _Interp:
    def __init__(self, root):
        self.root = root

    def resolve(self, ref):
        m = re.fullmatch(r"#/\$defs/([^/]+)", ref)
        if not m or m.group(1) not in self.root.get("$defs", {}):
            raise ValueError(f"schema: unsupported or dangling $ref {ref!r}")
        return self.root["$defs"][m.group(1)]

    def check(self, s, v, path):
        """Return [(path tuple, message)]. path may be a tuple or a str/Path
        (normalized by _as_path_tuple)."""
        path = _as_path_tuple(path)
        unknown = set(s) - _KEYWORDS - _ANNOTATIONS
        if unknown:
            raise ValueError(f"schema: unsupported keyword(s) {sorted(unknown)} at {path}")
        if "then" in s and "if" not in s:
            raise ValueError(f"schema: 'then' without 'if' at {path}")
        errs = []
        if "type" in s:
            types = s["type"] if isinstance(s["type"], list) else [s["type"]]
            if not any(_is_type(v, t) for t in types):
                return [(path, f"expected {' or '.join(types)}, got {_jtype(v)}")]
        if "$ref" in s:
            sub = self.check(self.resolve(s["$ref"]), v, path)
            if sub:
                return sub  # referenced schema failed; do not pile on siblings
        if "const" in s and _canon(v) != _canon(s["const"]):
            return [(path, f"must equal {s['const']!r}")]
        if "enum" in s and _canon(v) not in {_canon(e) for e in s["enum"]}:
            return [(path, f"{v!r} not one of {s['enum']}")]
        if isinstance(v, str):
            if "minLength" in s and len(v) < s["minLength"]:
                errs.append((path, f"shorter than {s['minLength']} character(s)"))
            if "pattern" in s and not re.search(s["pattern"], v):
                errs.append((path, f"{v!r} does not match {s['pattern']}"))
        if _is_type(v, "number") and "minimum" in s and v < s["minimum"]:
            errs.append((path, f"{v!r} is below minimum {s['minimum']}"))
        if isinstance(v, list):
            if "minItems" in s and len(v) < s["minItems"]:
                errs.append((path, f"needs at least {s['minItems']} item(s), has {len(v)}"))
            if s.get("uniqueItems"):
                seen = set()
                for i, item in enumerate(v):
                    c = _canon(item)
                    if c in seen:
                        errs.append((path + (i,), f"duplicate item {item!r}"))
                    seen.add(c)
            if "items" in s:
                for i, item in enumerate(v):
                    errs += self.check(s["items"], item, path + (i,))
        if isinstance(v, dict):
            for r in s.get("required", []):
                if r not in v:
                    errs.append((path, f"missing required field {r!r}"))
            props = s.get("properties", {})
            for k, sub in props.items():
                if k in v:
                    errs += self.check(sub, v[k], path + (k,))
            if "additionalProperties" in s:
                ap = s["additionalProperties"]
                for k in v:
                    if k in props:
                        continue
                    if ap is False:
                        errs.append((path, f"unexpected field {k!r}"))
                    elif isinstance(ap, dict):
                        errs += self.check(ap, v[k], path + (k,))
                    elif ap is not True:
                        raise ValueError(f"schema: bad additionalProperties at {path}")
        if "anyOf" in s and not any(not self.check(b, v, path) for b in s["anyOf"]):
            errs.append((path, "matches none of: " + "; ".join(
                _describe(b) for b in s["anyOf"])))
        if "if" in s and not self.check(s["if"], v, path) and "then" in s:
            reported = {p for p, _ in errs}
            for p, m in self.check(s["then"], v, path):
                # a sub-value the base schema already rejected is not re-reported
                if p == path or not any(p[:len(q)] == q for q in reported if q != path):
                    errs.append((p, m))
        return errs


def _describe(s):
    if set(s) == {"required"}:
        return "has " + " and ".join(repr(r) for r in s["required"])
    return _canon(s)


def _jtype(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, (int, float)):
        return "number"
    return {str: "string", list: "array", dict: "object"}.get(type(v), type(v).__name__)


def _jpath(p):
    p = _as_path_tuple(p)
    out = "$"
    for part in p:
        out += f"[{part}]" if isinstance(part, int) else f".{part}"
    return out


def _label(records, i):
    r = records[i]
    if isinstance(r, dict) and isinstance(r.get("key"), str):
        return r["key"]
    return f"#{i}"


def _get(d, *keys):
    for k in keys:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def validate(path):
    records = load(path)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = []
    for p, msg in _Interp(schema).check(schema, records, ()):
        if p and isinstance(p[0], int):
            errors.append(f"{_label(records, p[0])}: {_jpath(p[1:])}: {msg}")
        else:
            errors.append(f"registry: {_jpath(p)}: {msg}")

    first = {}
    for i, r in enumerate(records):
        if not isinstance(r, dict):
            continue
        lab = _label(records, i)
        k = r.get("key")
        if isinstance(k, str):
            if k in first:
                errors.append(f"{lab}: $.key: duplicate key (first at #{first[k]}, again at #{i})")
            else:
                first[k] = i

        terr, ev = r.get("territory"), r.get("territory_evidence")
        if isinstance(terr, dict) and terr and isinstance(ev, dict):
            for town in sorted(set(terr) - set(ev)):
                errors.append(f"{lab}: $.territory_evidence: town {town!r} is in territory but has no evidence")
            for town in sorted(set(ev) - set(terr)):
                errors.append(f"{lab}: $.territory: town {town!r} has evidence but is not in territory")

        for fpath in _DATE_FIELDS:
            d = _get(r, *fpath)
            if isinstance(d, str) and _DATE_RE.search(d):
                try:
                    datetime.date.fromisoformat(d)
                except ValueError:
                    errors.append(f"{lab}: {_jpath(fpath)}: {d!r} is not a real calendar date")

        text, fp = _get(r, "quote", "text"), _get(r, "retrieved", "fingerprint")
        if isinstance(text, str) and text and isinstance(fp, str) and _FP_RE.search(fp):
            want = fingerprint(text)
            if fp != want:
                errors.append(f"{lab}: $.retrieved.fingerprint: {fp} != fingerprint(quote.text) {want}")
    return errors


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: validate_facts.py <registry.json>", file=sys.stderr)
        return 2
    try:
        errors = validate(argv[0])
    except FactsUnreadable as e:
        print(f"unreadable: {e}")
        return 2
    for e in errors:
        print(e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
