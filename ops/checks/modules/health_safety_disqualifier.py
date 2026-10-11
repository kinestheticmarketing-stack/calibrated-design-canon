"""health_safety_disqualifier -- health/safety pages must not carry the shared
disqualifier block, and every listed page must be written.
Source: DCI _postbuild_check.py:check_health_safety_disqualifier (lock L4).

Site-agnostic port: the page set and the needle(s) come from the site.
  data.pages      path to the file holding the page set. A .py file is read
                  with ast (never imported): the top-level assignment named by
                  data.pages_var, whose value is a list/tuple/set literal or
                  frozenset({...}) / set([...]) / tuple(...) / list(...) of one.
                  Any other file: one page name per line, '#' comments ignored.
  data.pages_var  literal: assignment name (ignored for non-.py files).
  data.needles    literal: list of raw-HTML substrings that mark the block
                  (DCI: ['class="disqualifier"']). Counted in raw HTML, as the
                  source check does.
"""

import ast
from pathlib import Path

NAME = "health_safety_disqualifier"
DESCRIPTION = ("Pages in the site's health/safety set exist in public/ and "
               "contain none of the disqualifier-block needles.")
REQUIRES = {
    "pages": "file holding the health/safety page set (.py read via ast, or one name per line)",
    "pages_var": "literal: name of the assignment holding the page set in a .py pages file",
    "needles": "literal: list of raw-HTML substrings marking the disqualifier block",
}
LITERAL_KEYS = {"pages_var", "needles"}
OPTIONS = {}

_WRAPPERS = {"frozenset", "set", "tuple", "list", "sorted"}


def _literal(node):
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in _WRAPPERS and len(node.args) <= 1 and not node.keywords):
        return list(_literal(node.args[0])) if node.args else []
    return ast.literal_eval(node)


def _pages_from_py(path, var):
    tree = ast.parse(Path(path).read_text(encoding="utf-8"), filename=str(path))
    value = None
    for node in tree.body:
        targets = []
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            val = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value:
            targets = [node.target.id]
            val = node.value
        if var in targets:
            value = val  # last top-level assignment wins, as at import time
    if value is None:
        raise ValueError("%s: no top-level assignment %r" % (path, var))
    pages = _literal(value)
    if isinstance(pages, str) or not all(isinstance(p, str) for p in pages):
        raise ValueError("%s: %r is not a collection of page-name strings" % (path, var))
    return sorted(set(pages))


def _load_pages(ctx):
    path = Path(ctx.data["pages"])
    if path.suffix == ".py":
        return _pages_from_py(path, ctx.data["pages_var"])
    return sorted({ln.strip() for ln in ctx.read_text(path).splitlines()
                   if ln.strip() and not ln.strip().startswith("#")})


def check(ctx):
    needles = ctx.data["needles"]
    if isinstance(needles, str):
        needles = [needles]
    if not needles or not all(isinstance(n, str) and n for n in needles):
        raise ValueError("needles must be a non-empty list of non-empty strings")
    pages = _load_pages(ctx)
    if not pages:
        raise ValueError("health/safety page set is empty; nothing to judge")
    findings = []
    for name in pages:
        p = ctx.public_dir / name
        if not p.is_file():
            findings.append(ctx.finding(name, "listed in the health/safety page set but not written"))
            continue
        raw = ctx.read_text(p)
        for needle in needles:
            n = raw.count(needle)
            if n:
                i = raw.find(needle)
                quote = raw[max(0, i - 60): i + len(needle) + 60]
                findings.append(ctx.finding(
                    p, "contains %r %d time(s); expected 0" % (needle, n), quote))
    return findings
