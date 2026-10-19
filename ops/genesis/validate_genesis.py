"""validate_genesis -- cross-validate a property's intake, market pack and facts registry.

Usage: python3 ops/genesis/validate_genesis.py <intake.json> <market_pack.json> <registry.json>
Exit 0 valid / 1 invalid (one line per error) / 2 unreadable (a file cannot be
read, is not JSON, or has the wrong top-level type).

What it validates:
  1. intake against ops/genesis/intake.schema.json, market pack against
     ops/genesis/market_pack.schema.json (both with the schema interpreter of
     ops/facts/validate_facts.py, no second engine), and the registry with
     validate_facts.validate (each error prefixed "registry: ").
  2. every facts key the market pack uses exists in the registry (including
     a town's code_facts.facts_keys).
  3. every intake service_area_towns entry has a market pack town of that name.
  4. every program towns_served entry is a market pack town name.
  5. a town carries one territory shape: territory_state OR territory_states,
     never both. Each town is read as {electric, gas}; a single territory_state
     is the same state for both. Single form: territory_state equals the state
     in the territory_evidence of every registry fact it cites. Per-key form:
     each cited fact's evidence state equals the state for that fact's utility
     kind (electric when the fact's territory entry for the town names only an
     electric_utility, gas when it names only a gas_utility); when the kind
     cannot be told, it equals one of the two per-key states. Either form: at
     least one cited fact carries evidence.
  6. no string value in the intake or market pack is shaped like a secret (the
     error names only the file and JSON path, never the value). Secret-shaped
     means: contains "-----BEGIN", an SG. key, AC + 32 hex, a 32+ hex run, or
     a 40+ char run of [A-Za-z0-9+/_=-] that mixes upper, lower AND digits
     (token entropy), so lowercase URL paths and slugs pass. A lead_destination
     in server-copy reference form (server-copy:<CODE>:LEAD_TO) is a pointer,
     not a value, and is never flagged.
  7. the intake's property_code is not listed in its own sibling_properties.
  8. a server-copy lead_destination names the intake's own property_code.
One error per defect. Cross-reference rules skip any part the schema already
rejected, so a structural error does not cascade.

Where the files live: a REAL property keeps them in its private site repo as
ops/intake.json, ops/market_pack.json and facts/registry.json (with
facts/snapshots/). They never live in canon; canon holds only the fictional
FIXTURE under ops/genesis/fixtures/exampleton/.
"""

import importlib.util
import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_VF_PATH = Path(__file__).resolve().parents[1] / "facts" / "validate_facts.py"
_spec = importlib.util.spec_from_file_location("_genesis_validate_facts", _VF_PATH)
_vf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_vf)

INTAKE_SCHEMA_PATH = _HERE / "intake.schema.json"
MARKET_PACK_SCHEMA_PATH = _HERE / "market_pack.schema.json"

_STATES = ("NAMED", "SPLIT", "UNKNOWN")
_SECRET_RES = (
    re.compile(r"-----BEGIN"),
    re.compile(r"\bSG\.[A-Za-z0-9_-]{8,}"),
    re.compile(r"\bAC[0-9a-fA-F]{32}\b"),
    re.compile(r"\b[0-9a-fA-F]{32,}\b"),
)
# Long-run rule: a 40+ char run of token characters is secret-shaped only if
# that run holds at least one uppercase letter, one lowercase letter and one
# digit. Plain lowercase URL paths and slugs pass; base64/API tokens fail.
_LONG_RUN_RE = re.compile(r"[A-Za-z0-9+/_=-]{40,}")
# lead_destination reference form: the real destination lives only in the server copy.
_SERVER_COPY_RE = re.compile(r"^server-copy:([A-Z]{3}):LEAD_TO\Z")


class GenesisUnreadable(ValueError):
    """An input file is unreadable, not JSON, or has the wrong top-level type."""


def _load_object(path, label):
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise GenesisUnreadable(f"{label}: {path}: cannot read: {e}") from None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise GenesisUnreadable(f"{label}: {path}: not JSON: {e}") from None
    if not isinstance(data, dict):
        raise GenesisUnreadable(
            f"{label}: {path}: top level is {_vf._jtype(data)}, expected a JSON object")
    return data


def _secret_shaped(s):
    if any(r.search(s) for r in _SECRET_RES):
        return True
    return any(re.search(r"[A-Z]", run) and re.search(r"[a-z]", run)
               and re.search(r"[0-9]", run)
               for run in _LONG_RUN_RE.findall(s))


def _at(doc, path):
    for p in path:
        if isinstance(p, int):
            if not isinstance(doc, list) or p >= len(doc):
                return None
        elif not isinstance(doc, dict) or p not in doc:
            return None
        doc = doc[p]
    return doc


def _schema_check(doc, schema_path, label, errors):
    """Append schema errors for doc; return the set of error paths."""
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    paths = set()
    for p, msg in _vf._Interp(schema).check(schema, doc, ()):
        v = _at(doc, p)
        if isinstance(v, str) and _secret_shaped(v):
            msg = msg.replace(repr(v), "<redacted secret-shaped value>")
        errors.append(f"{label}: {_vf._jpath(p)}: {msg}")
        paths.add(p)
    return paths


def _bad(errpaths, path):
    """True when the schema reported an error at path or anywhere below it."""
    n = len(path)
    return any(q[:n] == path for q in errpaths if len(q) >= n)


def _walk_strings(v, path=()):
    if not isinstance(path, tuple):
        # accept a str / Path / other single segment: "" -> (), else (segment,)
        path = () if path == "" else (path,)
    if isinstance(v, str):
        yield path, v
    elif isinstance(v, list):
        for i, item in enumerate(v):
            yield from _walk_strings(item, path + (i,))
    elif isinstance(v, dict):
        for k, item in v.items():
            yield from _walk_strings(item, path + (k,))


def _utility_kind(record, town):
    """'electric' / 'gas' when the fact's territory entry for town names only
    that utility; None when the kind cannot be told."""
    terr = record.get("territory")
    entry = terr.get(town) if isinstance(terr, dict) else None
    if not isinstance(entry, dict):
        return None
    elec = isinstance(entry.get("electric_utility"), str) and entry["electric_utility"].strip()
    gas = isinstance(entry.get("gas_utility"), str) and entry["gas_utility"].strip()
    if elec and not gas:
        return "electric"
    if gas and not elec:
        return "gas"
    return None


def _ok_str(doc, errpaths, path):
    v = _at(doc, path)
    return v if isinstance(v, str) and not _bad(errpaths, path) else None


def _ok_list(doc, errpaths, path):
    """The list at path, if present and the schema raised nothing AT the list itself."""
    v = _at(doc, path)
    return v if isinstance(v, list) and path not in errpaths else None


def validate(intake_path, market_pack_path, registry_path):
    intake = _load_object(intake_path, "intake")
    mp = _load_object(market_pack_path, "market_pack")
    try:
        records = _vf.load(registry_path)
        reg_errors = _vf.validate(registry_path)
    except _vf.FactsUnreadable as e:
        raise GenesisUnreadable(f"registry: {e}") from None

    errors = []
    # 1 schemas
    ie = _schema_check(intake, INTAKE_SCHEMA_PATH, "intake", errors)
    me = _schema_check(mp, MARKET_PACK_SCHEMA_PATH, "market_pack", errors)
    errors += [f"registry: {e}" for e in reg_errors]

    # registry index; unusable if any record lacks a string key (cannot tell what is missing)
    by_key = {}
    registry_ok = True
    for r in records:
        if isinstance(r, dict) and isinstance(r.get("key"), str):
            by_key.setdefault(r["key"], []).append(r)
        else:
            registry_ok = False

    # market pack town names; unusable if any town or name is structurally broken
    towns = _ok_list(mp, me, ("towns",))
    town_names = None
    if towns is not None and towns:
        names = [_ok_str(mp, me, ("towns", i, "name")) for i in range(len(towns))]
        if all(n is not None for n in names):
            town_names = set(names)

    # 2 every market pack facts key exists in the registry
    missing = set()  # paths of keys reported missing
    if registry_ok:
        key_paths = []
        for i in range(len(towns or [])):
            fk = _ok_list(mp, me, ("towns", i, "facts_keys"))
            key_paths += [("towns", i, "facts_keys", j) for j in range(len(fk or []))]
        for i in range(len(_ok_list(mp, me, ("programs",)) or [])):
            key_paths.append(("programs", i, "facts_key"))
        for part in ("housing", "code_facts"):
            fk = _ok_list(mp, me, (part, "facts_keys"))
            key_paths += [(part, "facts_keys", j) for j in range(len(fk or []))]
        for i in range(len(towns or [])):
            fk = _ok_list(mp, me, ("towns", i, "code_facts", "facts_keys"))
            key_paths += [("towns", i, "code_facts", "facts_keys", j) for j in range(len(fk or []))]
        for p in key_paths:
            k = _ok_str(mp, me, p)
            if k is not None and k not in by_key:
                missing.add(p)
                errors.append(f"xref: market_pack {_vf._jpath(p)}: facts key {k!r} is not in the registry")

    # 3 every intake service-area town is a market pack town
    sat = _ok_list(intake, ie, ("service_area_towns",))
    if sat and town_names is not None:
        for j in range(len(sat)):
            t = _ok_str(intake, ie, ("service_area_towns", j))
            if t is not None and t not in town_names:
                errors.append(f"xref: intake $.service_area_towns[{j}]: town {t!r} has no market_pack town of that name")

    # 4 every program towns_served entry is a market pack town
    if town_names is not None:
        for i in range(len(_ok_list(mp, me, ("programs",)) or [])):
            served = _ok_list(mp, me, ("programs", i, "towns_served"))
            for j in range(len(served or [])):
                p = ("programs", i, "towns_served", j)
                t = _ok_str(mp, me, p)
                if t is not None and t not in town_names:
                    errors.append(f"xref: market_pack {_vf._jpath(p)}: town {t!r} is not a market_pack town")

    # 5 one territory shape per town; territory state(s) agree with the cited facts' territory_evidence
    if isinstance(towns, list):
        for i, t in enumerate(towns):
            if isinstance(t, dict) and "territory_state" in t and "territory_states" in t:
                errors.append(
                    f"xref: market_pack $.towns[{i}]: carries both territory_state and "
                    f"territory_states (one territory shape per town)")
    if registry_ok:
        for i in range(len(towns or [])):
            name = _ok_str(mp, me, ("towns", i, "name"))
            t = _at(mp, ("towns", i))
            per_key = isinstance(t, dict) and "territory_states" in t
            if per_key and "territory_state" in t:
                continue  # shape error reported above
            if per_key:
                states = {k: _ok_str(mp, me, ("towns", i, "territory_states", k)) for k in ("electric", "gas")}
                state = None
                if any(v not in _STATES for v in states.values()):
                    continue
            else:
                state = _ok_str(mp, me, ("towns", i, "territory_state"))
                if state not in _STATES:
                    continue
            fk = _ok_list(mp, me, ("towns", i, "facts_keys"))
            if name is None or not fk:
                continue
            kps = [("towns", i, "facts_keys", j) for j in range(len(fk))]
            if any(_ok_str(mp, me, p) is None for p in kps):
                continue
            present = [fk[j] for j, p in enumerate(kps) if p not in missing]
            any_missing = len(present) < len(kps)
            evidenced, disagree, malformed = [], [], False
            for k in present:
                for r in by_key[k]:
                    ev = r.get("territory_evidence")
                    if not isinstance(ev, dict) or name not in ev:
                        continue
                    entry = ev[name]
                    if not (isinstance(entry, dict) and entry.get("state") in _STATES):
                        malformed = True  # registry rule 1 already reports it
                        continue
                    evidenced.append(k)
                    if per_key:
                        kind = _utility_kind(r, name)
                        ok = (entry["state"] == states[kind] if kind
                              else entry["state"] in states.values())
                    else:
                        ok = entry["state"] == state
                    if not ok and k not in disagree:
                        disagree.append(k)
            if disagree:
                shape = (f"territory_states electric {states['electric']} gas {states['gas']}"
                         if per_key else f"territory_state {state}")
                errors.append(
                    f"xref: market_pack $.towns[{i}]: town {name!r} {shape} "
                    f"disagrees with territory_evidence in {', '.join(disagree)}")
            elif not evidenced and not any_missing and not malformed:
                errors.append(f"xref: market_pack $.towns[{i}]: no fact carries territory evidence for town {name!r}")

    # 6 secret-shaped values (never echo the value)
    for label, doc in (("intake", intake), ("market_pack", mp)):
        for p, s in _walk_strings(doc, ()):
            if label == "intake" and p == ("lead_destination",) and _SERVER_COPY_RE.match(s):
                continue  # a server-copy pointer, not a value
            if _secret_shaped(s):
                errors.append(f"secret: {label}:{_vf._jpath(p)}: value is shaped like a secret")

    # 7 property_code not among its own siblings
    code = _ok_str(intake, ie, ("property_code",))
    sibs = _ok_list(intake, ie, ("sibling_properties",))
    if code is not None and sibs:
        for j in range(len(sibs)):
            if _ok_str(intake, ie, ("sibling_properties", j)) == code:
                errors.append(f"xref: intake $.sibling_properties[{j}]: lists the property's own code {code!r}")

    # 8 a server-copy lead_destination names this property's code
    ld = _ok_str(intake, ie, ("lead_destination",))
    m = _SERVER_COPY_RE.match(ld) if ld is not None else None
    if m and code is not None and m.group(1) != code:
        errors.append(
            f"xref: intake $.lead_destination: server-copy code {m.group(1)!r} "
            f"does not equal property_code {code!r}")
    return errors


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 3:
        print("usage: validate_genesis.py <intake.json> <market_pack.json> <registry.json>",
              file=sys.stderr)
        return 2
    try:
        errors = validate(*argv)
    except GenesisUnreadable as e:
        print(f"unreadable: {e}")
        return 2
    for e in errors:
        print(e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
