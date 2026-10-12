"""superlative_scan -- a ranking superlative the site has ruled out renders on
any of eight published surfaces.

Sources: DCI ops/superlative_scan.py:scan_dir run as `--retired` (regen_all.sh
:244; HTMLParser surfaces, pattern RETIRED_PATTERNS); GCI
ops/superlative_scan.py:scan (regex surfaces, list PATTERNS; exists, not wired
into its build). LGM has no such check.

Surfaces (both sites): BODY (visible text), TITLE, META (meta name=, not og/
twitter), OG, TW (twitter:*), JSONLD, ALT (img alt), LLMS (public/llms.txt
whole). HTML comments are not a surface on either site.

The two extractors differ (DCI: HTMLParser, skips noscript/svg text, META =
every named meta, TW from name or property; GCI: regexes, body keeps noscript/
svg text and the <title> text, META = name="description*" only). Neither is a
superset, so this module runs BOTH extractors and takes the multiset union per
(page, surface, matched text): the larger count wins. Each surface's chunks are
joined with a space and whitespace-collapsed before matching (GCI flattens; DCI
joins with newlines, which a collapsed haystack also matches). Recursive over
public/ (sites list public/ top level only; identical on today's flat trees).

Patterns: the default list (RETIRED_PATTERNS in ops/checks/
superlative_default.py) always applies. A site `patterns` file is ADDED to it
(union, deduped by regex source, default first), never a replacement. For a
site .py file, `patterns_var` names a top-level assignment, read with ast (no
import/exec): `NAME = re.compile("<regex>", ...)` -> one pattern, or a literal
list of regex strings or (name, regex) pairs. Any other file: one regex per
line, '#' comments and blanks skipped. Matching is case-insensitive (both
sites). An absent or empty site list does not disable the scan (default only);
an empty default list raises (a scan that looks for nothing tests nothing).
"""

import ast
import html
import re
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

NAME = "superlative_scan"
DESCRIPTION = ("A ruled-out ranking superlative (default list + site list) "
               "renders on any of 8 surfaces: body, title, meta, og, "
               "twitter, JSON-LD, img alt, llms.txt.")
REQUIRES = {
    "patterns": "file of site superlative regexes (.py read via ast, or one "
                "regex per line), added to the default list; absent, null or "
                "\"\" = default list only",
}
# Passed raw so null / "" can mean "default only"; check() resolves the path.
LITERAL_KEYS = {"patterns"}
OPTIONAL_KEYS = {"patterns"}
DEFAULT_PATH = Path(__file__).resolve().parent.parent / "superlative_default.py"
DEFAULT_VAR = "RETIRED_PATTERNS"
OPTIONS = {
    # Top-level assignment to read when `patterns` is a .py file.
    "patterns_var": None,
    "ignorecase": True,
    # Whole-file surface, relative to the public dir (both sites: llms.txt).
    "extra_files": ["llms.txt"],
}

# ---------------------------------------------------------------- patterns

def _call_name(node):
    f = node.func
    return f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")


def _load_patterns(path, var, text):
    if str(path).endswith(".py"):
        if not var:
            raise ValueError("superlative_scan: option patterns_var is required "
                             "when patterns is a .py file")
        tree = ast.parse(text, filename=str(path))
        value = None
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == var for t in node.targets):
                value = node.value
        if value is None:
            raise ValueError("superlative_scan: no top-level %r in %s" % (var, path))
        if isinstance(value, ast.Call) and _call_name(value) == "compile":
            arg = value.args[0] if value.args else None
            if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
                raise ValueError("superlative_scan: %s first arg is not a "
                                 "string literal" % var)
            pats = [(var, arg.value)]
        else:
            lit = ast.literal_eval(value)
            if isinstance(lit, str):
                lit = [lit]
            pats = []
            for i, item in enumerate(lit):
                if isinstance(item, str):
                    pats.append(("%s[%d]" % (var, i), item))
                else:
                    pats.append((str(item[0]), str(item[1])))
    else:
        pats = [("line%d" % n, ln.strip())
                for n, ln in enumerate(text.splitlines(), 1)
                if ln.strip() and not ln.strip().startswith("#")]
    return pats


def _all_patterns(ctx):
    """Default list, then the site list (if any); deduped by regex source."""
    pats = [("default:%s" % n, p) for n, p in _load_patterns(
        DEFAULT_PATH, DEFAULT_VAR, ctx.read_text(DEFAULT_PATH))]
    if not pats:
        raise ValueError("superlative_scan: empty default pattern set in %s"
                         % DEFAULT_PATH)
    raw = ctx.data.get("patterns")
    if raw in (None, "", []):
        site = []
    elif isinstance(raw, str):
        path = ctx.resolve(raw)
        if not path.exists():
            raise ValueError("CONFIG ERROR: superlative_scan: patterns path "
                             "does not exist: %s" % path)
        site = _load_patterns(path, ctx.options.get("patterns_var"),
                              ctx.read_text(path))
    else:
        raise ValueError("CONFIG ERROR: superlative_scan: patterns must be a "
                         "path string, null or \"\", got %r" % (raw,))
    seen, out = set(), []
    for n, p in pats + site:
        if p not in seen:
            seen.add(p)
            out.append((n, p))
    return out


# ------------------------------------------------- extractor 1: DCI parser

_SKIP = {"script", "style", "template", "noscript", "svg"}


class _DciSurfaces(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.s = defaultdict(list)
        self._skip = 0
        self._in_title = False
        self._in_jsonld = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in _SKIP:
            self._skip += 1
            if tag == "script" and (a.get("type") or "").strip() == "application/ld+json":
                self._in_jsonld = True
        if tag == "title":
            self._in_title = True
        if tag == "img" and a.get("alt"):
            self.s["ALT"].append(a["alt"])
        if tag == "meta":
            name = (a.get("name") or "").lower()
            prop = (a.get("property") or "").lower()
            content = a.get("content") or ""
            if not content:
                return
            key = prop or name
            if key.startswith("og:"):
                self.s["OG"].append(content)
            elif key.startswith("twitter:"):
                self.s["TW"].append(content)
            elif name:
                self.s["META"].append(content)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag in _SKIP and self._skip:
            self._skip -= 1
            if tag == "script":
                self._in_jsonld = False
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_jsonld:
            self.s["JSONLD"].append(data)
        elif self._skip:
            return
        elif self._in_title:
            self.s["TITLE"].append(data)
        elif data.strip():
            self.s["BODY"].append(data)


def _dci_surfaces(raw):
    p = _DciSurfaces()
    p.feed(raw)
    p.close()
    return {k: [" ".join(v)] for k, v in p.s.items()}


# ------------------------------------------------- extractor 2: GCI regexes

_SCRIPT_STYLE = re.compile(r"<(script|style|template)\b[^>]*>.*?</\1>", re.S | re.I)
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_TAG = re.compile(r"<[^>]+>")
_JSONLD = re.compile(
    r"<script[^>]+type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.S | re.I)
_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)
_TAG_META = re.compile(r"<meta\b[^>]*>", re.I)
_TAG_IMG = re.compile(r"<img\b[^>]*>", re.I)
_ATTR = re.compile(r"([\w:.-]+)\s*=\s*(?:\"([^\"]*)\"|'([^']*)')", re.S)


def _attrs(tag):
    return [(m.group(1).lower(), m.group(2) if m.group(2) is not None else m.group(3))
            for m in _ATTR.finditer(tag)]


def _meta_contents(raw, key, prefix):
    found = []
    for tag in _TAG_META.findall(raw):
        attrs = _attrs(tag)
        if any(k == key and v.lower().startswith(prefix) for k, v in attrs):
            found += [v for k, v in attrs if k == "content"]
    return found


def _gci_surfaces(raw):
    alts = []
    for tag in _TAG_IMG.findall(raw):
        alts += [v for k, v in _attrs(tag) if k == "alt"]
    un = html.unescape
    out = {
        "TITLE": [un(m) for m in _TITLE.findall(raw)],
        "META": [un(m) for m in _meta_contents(raw, "name", "description")],
        "OG": [un(m) for m in _meta_contents(raw, "property", "og:")],
        "TW": [un(m) for m in _meta_contents(raw, "name", "twitter:")],
        "JSONLD": [un(m) for m in _JSONLD.findall(raw)],
        "ALT": [un(m) for m in alts],
    }
    body = _TAG.sub(" ", _SCRIPT_STYLE.sub(" ", _COMMENT.sub(" ", raw)))
    out["BODY"] = [un(body)]
    return out


# ------------------------------------------------------------------- scan

def _hits(surfaces, pats):
    """-> {(surface, matched.lower()): [(pname, matched, context), ...]}"""
    out = defaultdict(list)
    for surface, chunks in surfaces.items():
        for chunk in chunks:
            flat = " ".join(chunk.split())
            for pname, rx in pats:
                for m in rx.finditer(flat):
                    lo, hi = max(0, m.start() - 70), min(len(flat), m.end() + 70)
                    out[(surface, m.group(0).lower())].append(
                        (pname, m.group(0), flat[lo:hi]))
    return out


def check(ctx):
    flags = re.I if ctx.options.get("ignorecase", True) else 0
    pats = [(n, re.compile(p, flags)) for n, p in _all_patterns(ctx)]
    findings = []

    def emit(page, merged):
        for (surface, _tok), hits in sorted(merged.items()):
            for pname, tok, context in hits:
                findings.append(ctx.finding(
                    page, "superlative pattern hit %r [%s] (pattern %s)"
                    % (tok, surface, pname), context))

    for page in ctx.iter_html():
        raw = ctx.read_text(page)
        a, b = _hits(_dci_surfaces(raw), pats), _hits(_gci_surfaces(raw), pats)
        merged = {k: max(a.get(k, []), b.get(k, []), key=len)
                  for k in set(a) | set(b)}
        emit(page, merged)
    for rel in ctx.options.get("extra_files") or []:
        f = ctx.public_dir / rel
        if f.is_file():
            emit(f, _hits({"LLMS": [ctx.read_text(f)]}, pats))
    return findings
