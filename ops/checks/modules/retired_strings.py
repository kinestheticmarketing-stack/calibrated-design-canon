"""retired_strings -- a string retired from the site renders again.

Sources: DCI _postbuild_check.py:check_retired_strings_lock (L7, four decoded
surfaces); LGM _postbuild_check.py:check_retired_strings (raw bytes, newlines
collapsed); GCI _postbuild_check.py:check_k15_lock part (a) (three decoded
haystacks + JSON-LD string values). Parts (b)/(c) of GCI's K15 lock (Greeley
clause, embed callout) are not this module.

The sites diverge on which surfaces they search; this module searches the
UNION of all three sites' surfaces, and tests each entry both in its raw form
(LGM) and whitespace-collapsed form (DCI/GCI). A hit on any surface is a
finding. Matching is exact and case-sensitive everywhere.

List file format (all three sites): UTF-8, one rendered string per line, '#'
comment lines and blank lines skipped. A missing llms.txt, or an empty list,
is a finding (all three sites fail it: a lock that reads nothing tests
nothing).
"""

import html
import json
import re

NAME = "retired_strings"
DESCRIPTION = ("A retired string (ops/retired_strings.txt) renders anywhere in "
               "public/*.html or public/llms.txt, on any decoded surface.")
REQUIRES = {
    "retired": "the site's retired-strings list (ops/retired_strings.txt)",
}
OPTIONS = {
    # Also scan these files (relative to the public dir); a missing one is a
    # finding. All three sites scan llms.txt.
    "extra_files": ["llms.txt"],
    # Recurse into public/ subdirectories. The sites glob public/*.html only;
    # recursion is the strict superset (identical on today's flat public/).
    "recursive": True,
}

_TAG = re.compile(r"<[^>]+>")
_STYLE = re.compile(r"<style[^>]*>.*?</style>", re.S)
_SCRIPT = re.compile(r"<script[^>]*>.*?</script>", re.S)
_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.S)
_META = re.compile(r'<meta[^>]*\bcontent="([^"]*)"')
# GCI's regex (attributes allowed around type=) is a superset of DCI's.
_JSONLD = re.compile(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S)


def _collapse(t):
    return re.sub(r"\s+", " ", t).strip()


def _unjs(t):  # DCI: JS-escaped forms inside JSON-LD / inline script
    return t.replace("\\u2014", "—").replace("\\'", "'").replace('\\"', '"')


def _strings(obj, out):
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            _strings(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _strings(v, out)


def _surfaces(raw):
    """Every haystack any site searches, for one file."""
    out = [re.sub(r"[\r\n]+", " ", raw)]                  # LGM: raw bytes
    out.append(_collapse(raw))                            # DCI non-HTML form
    src = html.unescape(raw)                              # DCI (d) / GCI (1)
    out += [_collapse(src), _collapse(_unjs(src))]
    for sep in (" ", ""):
        out.append(_collapse(html.unescape(_TAG.sub(sep, raw))))   # GCI (2)(3)
        body = _SCRIPT.sub(" ", _STYLE.sub(" ", raw))
        out.append(_collapse(html.unescape(_TAG.sub(sep, body))))  # DCI (a)
    head = _TITLE.findall(raw) + _META.findall(raw)       # DCI (b)
    out += [_collapse(html.unescape(h)) for h in head]
    for blk in _JSONLD.findall(raw):                      # DCI (c) / GCI (4)
        out.append(_collapse(html.unescape(_unjs(blk))))
        try:
            data = json.loads(blk)
        except Exception:
            continue
        vals = []
        _strings(data, vals)
        out += [_collapse(html.unescape(v)) for v in vals]
    return out


def _entries(text):
    """(raw, collapsed) pairs. A comment is a line starting '#' at column 0
    (LGM's rule, the narrowest comment rule, so the most entries)."""
    out = []
    for ln in text.splitlines():
        raw = ln.rstrip("\r\n")
        if not raw.strip() or raw.startswith("#"):
            continue
        out.append((raw, _collapse(raw)))
    return out


def check(ctx):
    findings = []
    lst = ctx.data["retired"]
    entries = _entries(ctx.read_text(lst))
    if not entries:
        return [ctx.finding(lst, "retired-strings list has zero entries -- "
                                 "the lock reads nothing")]
    if ctx.options.get("recursive", True):
        files = list(ctx.iter_html())
    else:
        files = sorted(p for p in ctx.public_dir.glob("*.html") if p.is_file())
    for name in ctx.options.get("extra_files") or []:
        p = ctx.public_dir / name
        if not p.is_file():
            findings.append(ctx.finding(name, "%s missing -- cannot scan" % name))
            continue
        files.append(p)
    for p in files:
        hs = _surfaces(ctx.read_text(p))
        for raw, col in entries:
            if any(raw in h or (col and col in h) for h in hs):
                findings.append(ctx.finding(
                    p, "retired string renders", col[:120]))
    return findings
