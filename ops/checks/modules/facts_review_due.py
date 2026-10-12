"""facts_review_due -- a facts registry record is past its next_review date.

Gap K02. Every record in <site>/facts/registry.json carries next_review
(YYYY-MM-DD): the date by which the claim must be re-checked against its
source. A record whose next_review is strictly before `today` is overdue and
is one finding (key, next_review, days overdue). next_review == today passes.

Data keys:
  facts_registry  path to the property's facts/registry.json
Options:
  today           ISO date string "YYYY-MM-DD", or None (default) = the UTC
                  date at run time. Any other value -> ValueError (the module
                  cannot judge; a real run exits 2).

Records are read with validate_facts.load(); an unreadable registry raises
FactsUnreadable (exit 2). A record that is not an object, or whose next_review
is missing or not a real calendar date, is skipped silently: facts_schema
reports it. Canon code only; no site code is imported.

NOT ENABLED unless a site manifest names it.
"""

import importlib.util
import re
from datetime import date, datetime, timezone
from pathlib import Path

_VF_PATH = Path(__file__).resolve().parents[2] / "facts" / "validate_facts.py"
_spec = importlib.util.spec_from_file_location("_facts_validate_facts", _VF_PATH)
validate_facts = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate_facts)

NAME = "facts_review_due"
DESCRIPTION = ("Facts registry record whose next_review date is before today "
               "(claim overdue for re-checking against its source).")
REQUIRES = {
    "facts_registry": "path to the property's facts/registry.json",
}
OPTIONS = {"today": None}

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _parse_date(value):
    """date for a real YYYY-MM-DD string, else None."""
    if not isinstance(value, str) or not _DATE_RE.match(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _today(opt):
    if opt is None:
        return datetime.now(timezone.utc).date()
    d = _parse_date(opt)
    if d is None:
        raise ValueError("facts_review_due: option today must be an ISO date "
                         "'YYYY-MM-DD' or null, got %r" % (opt,))
    return d


def check(ctx):
    today = _today(ctx.options.get("today"))
    reg = ctx.data["facts_registry"]
    records = validate_facts.load(reg)
    findings = []
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            continue
        due = _parse_date(rec.get("next_review"))
        if due is None or not due < today:
            continue
        key = rec.get("key") if isinstance(rec.get("key"), str) else "#%d" % i
        days = (today - due).days
        claim = rec.get("claim") if isinstance(rec.get("claim"), str) else ""
        findings.append(ctx.finding(
            Path(reg),
            "%s: next_review %s is %d day%s overdue (today %s)"
            % (key, due.isoformat(), days, "" if days == 1 else "s",
               today.isoformat()),
            claim))
    return findings
