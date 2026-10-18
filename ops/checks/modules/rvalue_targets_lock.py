"""rvalue_targets_lock -- the R-value calculator's TARGETS equal the site's code facts.

Source: DCI _postbuild_check.py:check_rvalue_targets_lock (LOCK L6). The
calculator's TARGETS rows are typed values; this lock holds the attic, floor,
crawl-vented and crawl-encap rows equal to the jurisdiction's confirmed values
on every listed rendered page (DCI: the page and its embed frame). Expected
values are read from the site's code-facts dict (DCI: CODE_FACTS['denver'] in
_shared_components.py), never typed here.

The site's facts file is Python source; it is parsed with ast and only the
named top-level assignment is evaluated, by a literal-only evaluator that also
accepts dict(key=literal, ...) calls. No site code is imported or executed.

Option rows_from_market (default False): when true, a row whose source market
fact (ceiling for attic; floor for floor and crawl-vented; crawl1 for
crawl-encap) is missing from the facts dict or is None is NOT APPLICABLE: not
compared, never a finding, not counted as a pass. Supplied rows are checked
exactly as with the option off. Each run with the option on prints one line:
  rvalue_targets_lock: rows_from_market checked=<n> not_applicable=<k> [<names>|none]
With the option off, behaviour and output are unchanged.
"""

import ast
import re

NAME = "rvalue_targets_lock"
DESCRIPTION = ("R-value calculator TARGETS rows (attic, floor, crawl-vented, "
               "crawl-encap) equal the site's code facts on every listed page.")
REQUIRES = {
    "code_facts": "Python file holding the code-facts dict assignment "
                  "(DCI: _shared_components.py); read with ast, never imported",
    "facts_key": "literal: key of the jurisdiction in the code-facts dict (DCI: 'denver')",
    "pages": "literal: list of rendered calculator pages, relative to the public dir",
}
LITERAL_KEYS = {"facts_key", "pages"}
OPTIONS = {"facts_var": "CODE_FACTS", "rows_from_market": False}

ROW = re.compile(r"'(?P<area>[a-z-]+)':\s*\{label:'[^']*', target:'(?P<target>[^']*)', "
                 r"targetMin:(?P<min>\d+), targetRec:(?P<rec>\d+)\}")


def _lit(node):
    """ast.literal_eval plus dict(k=literal, ...) calls."""
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "dict" and not node.args
            and all(k.arg is not None for k in node.keywords)):
        return {k.arg: _lit(k.value) for k in node.keywords}
    if isinstance(node, ast.Dict):
        if any(k is None for k in node.keys):
            raise ValueError("dict unpacking not supported")
        return {_lit(k): _lit(v) for k, v in zip(node.keys, node.values)}
    if isinstance(node, (ast.List, ast.Tuple)):
        vals = [_lit(e) for e in node.elts]
        return vals if isinstance(node, ast.List) else tuple(vals)
    return ast.literal_eval(node)


def _load_facts(ctx):
    src = ctx.read_text(ctx.data["code_facts"])
    var = ctx.options["facts_var"]
    found = None
    for node in ast.parse(src).body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name) and node.targets[0].id == var):
            found = node.value
    if found is None:
        raise ValueError("no top-level assignment %s in %s" % (var, ctx.data["code_facts"]))
    return _lit(found)


SOURCES = (("attic", "ceiling"), ("floor", "floor"),
           ("crawl-vented", "floor"), ("crawl-encap", "crawl1"))


def expected_rows(d, rows_from_market=False):
    """(expected, not_applicable): expected maps area -> (target, n); with
    rows_from_market, areas whose source fact is absent or None are left out
    of expected and named, in row order, in not_applicable."""
    na = [a for a, k in SOURCES if d.get(k) is None] if rows_from_market else []
    rows = {}
    if "crawl-encap" not in na:
        crawl_n = int(re.search(r"\d+", d["crawl1"]).group(0))
        rows["crawl-encap"] = ("%s walls" % d["crawl1"], crawl_n)
    if "attic" not in na:
        rows["attic"] = ("R-%s" % d["ceiling"], d["ceiling"])
    if "floor" not in na:
        rows["floor"] = ("R-%s" % d["floor"], d["floor"])
        rows["crawl-vented"] = ("R-%s floor" % d["floor"], d["floor"])
    return {a: rows[a] for a, _ in SOURCES if a in rows}, na


def check(ctx):
    facts = _load_facts(ctx)
    d = facts[ctx.data["facts_key"]]
    from_market = bool(ctx.options.get("rows_from_market"))
    expected, not_applicable = expected_rows(d, from_market)
    if from_market:
        print("%s: rows_from_market checked=%d not_applicable=%d [%s]" % (
            NAME, len(expected), len(not_applicable),
            ", ".join(not_applicable) or "none"))
    pages = ctx.data["pages"]
    if isinstance(pages, str):
        pages = [pages]
    findings = []
    for name in pages:
        p = ctx.public_dir / name
        text = ctx.read_text(p) if p.exists() else ""
        rows = {m.group("area"): m for m in ROW.finditer(text)}
        for area, (target, n) in expected.items():
            m = rows.get(area)
            if not m:
                findings.append(ctx.finding(name, "area %r not found in TARGETS" % area, ""))
                continue
            got = (m.group("target"), int(m.group("min")), int(m.group("rec")))
            if got != (target, n, n):
                findings.append(ctx.finding(
                    name, "area %r is %s; code facts say %s" % (area, got, (target, n, n)),
                    m.group(0)))
    return findings
