"""payback_rate_wiring -- the payback calculator's script must compute its
result from the cited savings rate, and the page must not say it "prints no
savings". Port of DCI _postbuild_check.py:check_embed_locks, lock L3
(NEEDLE-SCOPED BY DESIGN: a lock against the calculator quietly going back to
echoing the visitor's figure, not a substitute for the claim gate).

Site facts are data keys:
  page          the payback page (path, normally under public/)
  rate_source   file holding the cited rate. A .py file is parsed with ast
                (never imported/executed); a .json file is loaded.
  rate_name     dotted path to the rate string inside rate_source, e.g.
                "CITED_SOURCES.ENERGYSTAR_SEAL_INSULATE_15PCT.stat". In a .py
                file the first segment is a top-level assignment; later
                segments index dict literals or dict(...) keyword calls.
  rate_regex    regex whose group 1 extracts the rate from that string
  needles       list of strings that must all appear in the page's bare
                <script>...</script> bodies; "{rate}" is replaced by group 1
  forbidden     list of regexes (case-insensitive) that must occur 0 times in
                the raw page source
DCI behaviour is the only behaviour (single-site check). If the page is
missing the runner stops on the missing data path (DCI's own check fails).
"""

import ast
import json
import re
from pathlib import Path

NAME = "payback_rate_wiring"
DESCRIPTION = ("Payback calculator script is wired to the cited savings rate; "
               "page carries no forbidden 'no savings' phrasing.")
REQUIRES = {
    "page": "payback calculator page, e.g. public/energy-savings-payback-calculator.html",
    "rate_source": "file holding the cited rate (.py parsed via ast, or .json)",
    "rate_name": "literal: dotted path to the rate string in rate_source",
    "rate_regex": "literal: regex; group 1 is the rate number",
    "needles": "literal: list of script strings that must be present; {rate} is substituted",
    "forbidden": "literal: list of regexes (case-insensitive) that must not occur in the page",
}
LITERAL_KEYS = {"rate_name", "rate_regex", "needles", "forbidden"}
OPTIONS = {}

_SCRIPT = re.compile(r"<script>(.*?)</script>", re.S)


def _py_lookup(src, parts):
    tree = ast.parse(src)
    node = None
    for stmt in tree.body:
        targets = []
        if isinstance(stmt, ast.Assign):
            targets, value = stmt.targets, stmt.value
        elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
            targets, value = [stmt.target], stmt.value
        if any(isinstance(t, ast.Name) and t.id == parts[0] for t in targets):
            node = value  # last assignment wins, as at import time
    if node is None:
        raise KeyError("no top-level assignment %r" % parts[0])
    for key in parts[1:]:
        nxt = None
        if isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and k.value == key:
                    nxt = v
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
              and node.func.id == "dict"):
            for kw in node.keywords:
                if kw.arg == key:
                    nxt = kw.value
        if nxt is None:
            raise KeyError("key %r not found" % key)
        node = nxt
    return ast.literal_eval(node)


def _rate_string(ctx):
    path = Path(ctx.data["rate_source"])
    parts = str(ctx.data["rate_name"]).split(".")
    src = ctx.read_text(path)
    if path.suffix == ".json":
        val = json.loads(src)
        for key in parts:
            val = val[key]
        return val
    return _py_lookup(src, parts)


def check(ctx):
    findings = []
    page = Path(ctx.data["page"])
    doc = ctx.read_text(page) if page.is_file() else ""
    m = re.search(ctx.data["rate_regex"], str(_rate_string(ctx)))
    if not m:
        findings.append(ctx.finding(
            ctx.rel(Path(ctx.data["rate_source"])),
            "%s no longer states a parseable rate" % ctx.data["rate_name"]))
    else:
        scripts = "\n".join(_SCRIPT.findall(doc))
        for needle in ctx.data["needles"]:
            needle = needle.replace("{rate}", m.group(1))
            if needle not in scripts:
                findings.append(ctx.finding(
                    page, "payback page script lacks the rate-fed result wiring",
                    needle))
    for pat in ctx.data["forbidden"]:
        hits = [h.group(0) for h in re.finditer(pat, doc, re.I)]
        if hits:
            findings.append(ctx.finding(
                page, "page matches forbidden %r %d time(s); expected 0"
                % (pat, len(hits)), hits[0]))
    return findings
