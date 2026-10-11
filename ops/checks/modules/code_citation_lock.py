"""code_citation_lock -- needle-scoped lock against code citations drifting
back to superseded editions or values. Source: DCI _postbuild_check.py:
check_code_citation_lock (LOCK L5) with its _l5_text/_l5_quote helpers.

Site facts are not in this module. The needle lists are read from the site's
own Python source by ast.literal_eval of named module-level assignments (no
import, no exec): data key `constants` points at the file, options name the
assignments. The superseded-edition needle, the capped value and the words
that license it are literal manifest keys.

Logic, ported unchanged:
  1. every target (top-level public/*.html, plus `extra_files` such as
     llms.txt): raw-source count of each SITEWIDE needle -> finding.
  2. pages whose basename is in MOVED_PAGES: rendered text (visible text +
     meta content + JSON-LD strings) with ALLOWED_PHRASE removed must not
     contain `edition_needle`; and every sentence containing `cap_needle`
     must contain one of `cap_allow_words`.
"""

import ast
import html
import os
import re

NAME = "code_citation_lock"
DESCRIPTION = ("Superseded code editions/values: sitewide forbidden needles, and on "
               "moved-jurisdiction pages the old edition outside the allowed phrase "
               "or a capped value outside a licensed sentence.")
REQUIRES = {
    "constants": "path to the site .py file holding the lock's tuple/str assignments",
    "extra_files": "path or list of paths of non-HTML targets (e.g. public/llms.txt)",
    "edition_needle": "literal: superseded edition string forbidden on moved pages (e.g. '2021 IECC')",
    "cap_needle": "literal: value allowed only in licensed sentences on moved pages (e.g. 'R-60')",
    "cap_allow_words": "literal: list of words, one of which licenses a cap_needle sentence",
}
LITERAL_KEYS = {"edition_needle", "cap_needle", "cap_allow_words"}
OPTIONS = {
    "sitewide_var": "L5_SITEWIDE",          # name of the tuple of sitewide needles
    "moved_pages_var": "L5_MOVED_PAGES",    # name of the tuple of page basenames
    "allowed_phrase_var": "L5_DENVER_PHRASE",  # name of the str allowed to carry edition_needle
    "recursive": False,                     # DCI pages() = glob public/*.html (top level only)
}


def _assignments(path, names):
    """Return {name: literal value} for module-level `name = <literal>`."""
    tree = ast.parse(open(path, encoding="utf-8").read(), filename=str(path))
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in names:
                    out[t.id] = ast.literal_eval(node.value)
    missing = [n for n in names if n not in out]
    if missing:
        raise ValueError("%s: no literal assignment for %s" % (path, ", ".join(missing)))
    return out


def _l5_text(raw):
    t = re.sub(r'<style\b.*?</style>', ' ', raw, flags=re.S)
    t = re.sub(r'<script(?![^>]*application/ld\+json)[^>]*>.*?</script>', ' ', t, flags=re.S)
    t = re.sub(r'<meta[^>]*content="([^"]*)"[^>]*>', r' \1. ', t)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = t.replace('\\u2014', '—').replace("\\'", "'")
    return re.sub(r'\s+', ' ', t)


_L5_BLOCK = re.compile(r'</?(?:p|li|ul|ol|div|h[1-6]|td|th|tr|table|nav|header|footer|section|'
                       r'article|aside|main|br|dt|dd|summary|details|figcaption|blockquote)\b[^>]*>', re.I)


def _licensed(s, allow):
    return any(w in s for w in allow)


def _l5_quote(raw, sent, cap, allow):
    t = re.sub(r'<style\b.*?</style>', ' ', raw, flags=re.S)
    t = re.sub(r'<script(?![^>]*application/ld\+json)[^>]*>.*?</script>', ' ', t, flags=re.S)
    t = re.sub(r'<meta[^>]*content="([^"]*)"[^>]*>', r' \1. \n', t)
    t = _L5_BLOCK.sub('\n', t)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t).replace('\\u2014', '—').replace("\\'", "'")
    for block in t.split('\n'):
        for piece in re.split(r'(?<=[.;!?])\s+', re.sub(r'\s+', ' ', block).strip()):
            if cap in piece and piece in sent and not _licensed(piece, allow):
                return piece[:240]
    i = sent.find(cap)
    return sent[max(0, i - 120):i + 120]


def check(ctx):
    o = ctx.options
    names = (o["sitewide_var"], o["moved_pages_var"], o["allowed_phrase_var"])
    consts = _assignments(ctx.data["constants"], names)
    sitewide = tuple(consts[names[0]])
    moved = set(consts[names[1]])
    phrase = consts[names[2]]
    edition = ctx.data["edition_needle"]
    cap = ctx.data["cap_needle"]
    allow = list(ctx.data["cap_allow_words"])
    if not sitewide or not moved or not phrase or not edition or not cap or not allow:
        raise ValueError("code_citation_lock: an empty needle list/phrase would judge nothing")

    if o.get("recursive"):
        pages = ctx.iter_html()
    else:
        pages = sorted(p for p in ctx.public_dir.glob("*.html") if p.is_file())
    extra = ctx.data["extra_files"]
    extra = extra if isinstance(extra, list) else [extra]

    findings = []
    for p in list(pages) + list(extra):
        base = os.path.basename(str(p))
        raw = ctx.read_text(p)
        for needle in sitewide:
            n = raw.count(needle)
            if n:
                findings.append(ctx.finding(p, 'contains "%s" %d time(s)' % (needle, n), needle))
        if base in moved:
            txt = _l5_text(raw)
            n = txt.replace(phrase, '').count(edition)
            if n:
                findings.append(ctx.finding(
                    p, '"%s" outside "%s" %d time(s)' % (edition, phrase, n), edition))
            for sent in re.split(r'(?<=[.;!?])\s+', txt):
                if cap in sent and not _licensed(sent, allow):
                    findings.append(ctx.finding(
                        p, "%s outside a licensed sentence (%s)" % (cap, " / ".join(allow)),
                        _l5_quote(raw, sent, cap, allow)))
    return findings
