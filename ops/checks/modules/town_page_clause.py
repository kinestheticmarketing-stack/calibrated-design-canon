"""town_page_clause -- a hub-only clause must not render on any town page.

Source: GCI _postbuild_check.py:check_k15_lock part (b) (K15 Unit T1): the
Greeley thank-you R-value clause (sc._THANK_YOU_RVALUE_GREELEY) must render on
none of the town pages (sc.TOWN_PAGE_FILENAMES, expected 8).

Site-agnostic port. The town list and the clause are read from the site's own
Python source by ast.literal_eval of named top-level assignments (no import,
no exec). The site's TOWN_PAGE_FILENAMES is a comprehension, not a literal, so
the module rebuilds it from the literal list it is derived from:
    {town_filename_pattern.format(slug=s) for s in <town_list_var> if s not in exclude_slugs}
where each list item is a slug string or a tuple whose first element is the slug.

Same haystacks as the source: raw entity-decoded, tags-removed, tags-to-space,
plus every string inside each JSON-LD block; all whitespace-collapsed.
"""

import ast
import html as _html
import json
import re

NAME = "town_page_clause"
DESCRIPTION = ("A clause reserved for the hub page (e.g. GCI's Greeley "
               "thank-you R-value clause) renders on none of the town pages.")
REQUIRES = {
    "components": "path to the site .py file holding the town list and the clause "
                  "(e.g. _shared_components.py); read by ast, never imported",
    "town_list_var": "literal: name of the top-level list of town slugs or "
                     "(slug, name) tuples in `components`",
    "town_filename_pattern": "literal: page filename for a slug, with {slug}",
    "exclude_slugs": "literal: list of slugs in the town list that are not town pages",
    "clause_var": "literal: name of the top-level string assignment holding the clause",
    "expected_count": "literal: integer number of town pages the site expects",
}
LITERAL_KEYS = {"town_list_var", "town_filename_pattern", "exclude_slugs",
                "clause_var", "expected_count"}
OPTIONS = {}

JSONLD_RE = re.compile(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S)


def _collapse(s):
    return re.sub(r"\s+", " ", s).strip()


def _short(s, n=90):
    return s if len(s) <= n else s[:n] + "..."


def _literal(tree, var, path):
    for node in tree.body:
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
        for t in targets:
            if isinstance(t, ast.Name) and t.id == var:
                return ast.literal_eval(node.value)
    raise ValueError("%s: no top-level literal assignment named %r" % (path, var))


def _jsonld_strings(obj, out):
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            _jsonld_strings(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _jsonld_strings(v, out)


def _haystacks(raw):
    hs = [
        _collapse(_html.unescape(raw)),
        _collapse(_html.unescape(re.sub(r"<[^>]+>", "", raw))),
        _collapse(_html.unescape(re.sub(r"<[^>]+>", " ", raw))),
    ]
    for blk in JSONLD_RE.findall(raw):
        try:
            data = json.loads(blk)
        except Exception:
            continue  # unparseable JSON-LD is another module's finding
        vals = []
        _jsonld_strings(data, vals)
        hs.extend(_collapse(_html.unescape(v)) for v in vals)
    return hs


def check(ctx):
    d = ctx.data
    src_path = d["components"]
    tree = ast.parse(ctx.read_text(src_path), filename=str(src_path))
    items = _literal(tree, d["town_list_var"], ctx.rel(src_path))
    clause = _literal(tree, d["clause_var"], ctx.rel(src_path))
    if not isinstance(clause, str) or not _collapse(clause):
        raise ValueError("%s is not a non-empty string" % d["clause_var"])
    clause = _collapse(clause)
    exclude = set(d["exclude_slugs"] or [])
    towns = set()
    for it in items:
        slug = it[0] if isinstance(it, (tuple, list)) else it
        if slug not in exclude:
            towns.add(d["town_filename_pattern"].format(slug=slug))
    towns = sorted(towns)

    findings = []
    if len(towns) != int(d["expected_count"]):
        findings.append(ctx.finding(
            ctx.rel(src_path), "town list has %d pages, expected %d"
            % (len(towns), int(d["expected_count"])), ", ".join(towns)))
    for t in towns:
        p = ctx.public_dir / t
        if not p.is_file():
            findings.append(ctx.finding(t, "town page missing from public/"))
            continue
        if any(clause in h for h in _haystacks(ctx.read_text(p))):
            findings.append(ctx.finding(
                p, "hub-only clause %s renders on a town page" % d["clause_var"],
                _short(clause)))
    return findings
