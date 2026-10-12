"""facts_citation_registry -- a cited-stat link whose source is not in the facts
registry, or whose registry record was retrieved too long ago.

Gap K04. Every <a href> that sits inside (or itself is) an element whose class
list contains "cited-stat", in the rendered public/**/*.html, is a citation.
Its href, with any #fragment stripped, must equal some registry record's
source.url (compared after validate_facts.normalize on both sides):
  - no record has that source.url                -> one finding for the href
  - a matching record's retrieved.date is older
    than today - 92 days (age 93+ days)          -> one finding for the href
Age 92 days passes; age 93 fails. One finding per href at most for staleness
(an href matched by several records is stale if any of them is stale; the
message names every stale key).

Data keys:
  facts_registry  path to the property's facts/registry.json
Options:
  today           ISO date string "YYYY-MM-DD", or None (default) = the UTC
                  date at run time. Any other value -> ValueError (the module
                  cannot judge; a real run exits 2).

Records are read with validate_facts.load(); an unreadable registry raises
FactsUnreadable (exit 2). A record that is not an object, or whose source.url
or retrieved.date is missing or malformed, is skipped silently for that field:
facts_schema reports it. Offline: hrefs are compared as text, never fetched.
Canon code only; no site code is imported.

NOT ENABLED unless a site manifest names it.
"""

import importlib.util
import re
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path

_VF_PATH = Path(__file__).resolve().parents[2] / "facts" / "validate_facts.py"
_spec = importlib.util.spec_from_file_location("_facts_validate_facts", _VF_PATH)
validate_facts = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate_facts)

NAME = "facts_citation_registry"
DESCRIPTION = ("cited-stat link whose URL is not a facts registry source.url, "
               "or whose record was retrieved more than 92 days ago.")
REQUIRES = {
    "facts_registry": "path to the property's facts/registry.json",
}
OPTIONS = {"today": None}

MAX_AGE_DAYS = 92
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "keygen",
         "link", "meta", "param", "source", "track", "wbr"}


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
        raise ValueError("facts_citation_registry: option today must be an ISO "
                         "date 'YYYY-MM-DD' or null, got %r" % (opt,))
    return d


def _is_cited(attrs):
    for name, value in attrs:
        if name == "class" and value and "cited-stat" in value.split():
            return True
    return False


class _CitedLinks(HTMLParser):
    """Collect hrefs of <a> elements inside (or being) a cited-stat element.
    A stack of (tag, cited) tracks nesting; void tags are never pushed; an end
    tag pops back to its matching open tag (unmatched end tags are ignored)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.depth = 0          # open cited-stat elements on the stack
        self.hrefs = []

    def _link(self, tag, attrs, cited):
        if tag != "a" or not (self.depth or cited):
            return
        for name, value in attrs:
            if name == "href" and value is not None:
                self.hrefs.append(value)
                return

    def handle_starttag(self, tag, attrs):
        cited = _is_cited(attrs)
        self._link(tag, attrs, cited)
        if tag in _VOID:
            return
        self.stack.append((tag, cited))
        if cited:
            self.depth += 1

    def handle_startendtag(self, tag, attrs):
        self._link(tag, attrs, _is_cited(attrs))

    def handle_endtag(self, tag):
        if tag in _VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                for _t, c in self.stack[i:]:
                    if c:
                        self.depth -= 1
                del self.stack[i:]
                return


def _index(records):
    """normalized source.url -> [(key, retrieved date or None)]."""
    by_url = {}
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            continue
        src = rec.get("source")
        url = src.get("url") if isinstance(src, dict) else None
        if not isinstance(url, str) or not url:
            continue
        key = rec.get("key") if isinstance(rec.get("key"), str) else "#%d" % i
        ret = rec.get("retrieved")
        when = _parse_date(ret.get("date")) if isinstance(ret, dict) else None
        by_url.setdefault(validate_facts.normalize(url), []).append((key, when))
    return by_url


def check(ctx):
    today = _today(ctx.options.get("today"))
    cutoff = today - timedelta(days=MAX_AGE_DAYS)
    by_url = _index(validate_facts.load(ctx.data["facts_registry"]))
    findings = []
    for page in ctx.iter_html():
        p = _CitedLinks()
        p.feed(ctx.read_text(page))
        p.close()
        for href in p.hrefs:
            url = href.split("#", 1)[0]
            matches = by_url.get(validate_facts.normalize(url))
            if not matches:
                findings.append(ctx.finding(
                    page, "cited-stat href is not any facts registry "
                    "source.url", href))
                continue
            stale = [(k, d) for k, d in matches if d is not None and d < cutoff]
            if stale:
                findings.append(ctx.finding(
                    page, "cited source retrieved more than %d days ago "
                    "(today %s): %s" % (MAX_AGE_DAYS, today.isoformat(), ", ".join(
                        "%s retrieved %s, %d days" % (k, d.isoformat(), (today - d).days)
                        for k, d in stale)), href))
    return findings
