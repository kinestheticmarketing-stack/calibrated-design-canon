"""artifact_grep -- a sibling property's identity leaks into rendered output.

Sources: LGM _artifact_grep.sh:check (guards DCI + GCI: names, domains,
phones, -denver/-greeley href slugs, elevation framings, service-area towns,
Atmos, unverified Xcel programs); GCI _artifact_grep.sh:check (guards DCI
only, plus "'denver' outside the DRCOG allowlist"). DCI has no copy. Neither
site's build runs it today.

Port: every rule is `grep -oiE <pattern>` over the raw bytes of public/*.html,
sitemap.xml and robots.txt, expected count 0. Here a rule is an OPTION entry
{"label", "pattern", "allow"}: `pattern` is a Python regex matched
case-insensitively on the raw file text; `allow` is an optional list of exact
phrases (case-insensitive) inside which a match is not counted -- GCI's DRCOG
grant is the only one ("total minus allowlisted" there, per occurrence here).
Every sibling string comes from the manifest option `rules`; this module
hardcodes no site fact. An empty rule list, or zero files scanned, is a
finding: a gate that reads nothing proves nothing (LGM's own empty-public note).

LGM's "Weld County" line is INFO in the source (never fails) and is not ported.
Scan is recursive (the sites glob public/*.html only; recursion is the strict
superset, identical on today's flat public/). See README divergence row.
"""

import re

NAME = "artifact_grep"
DESCRIPTION = ("A sibling property's name, domain, phone, slug, elevation, "
               "town or market fact appears in public/ (rules from options).")
REQUIRES = {}
OPTIONS = {
    # [{"label": str, "pattern": regex, "allow": [exact phrase, ...]}]
    "rules": [],
    # Non-HTML files in the public dir also scanned; a missing one is skipped
    # (grep 2>/dev/null in both sites).
    "extra_files": ["sitemap.xml", "robots.txt"],
    "recursive": True,
}


def _files(ctx):
    pub = ctx.public_dir
    if ctx.options.get("recursive", True):
        out = list(ctx.iter_html())
    else:
        out = sorted(p for p in pub.glob("*.html") if p.is_file())
    for name in ctx.options.get("extra_files") or []:
        p = pub / name
        if p.is_file():
            out.append(p)
    return out


def _context(text, start, end):
    a = max(0, text.rfind("\n", 0, start) + 1, start - 80)
    b = text.find("\n", end)
    b = min(b if b != -1 else len(text), end + 80)
    return text[a:b]


def check(ctx):
    rules = ctx.options.get("rules") or []
    if not rules:
        return [ctx.finding("(site)", "no artifact_grep rules configured: "
                            "the gate would test nothing")]
    compiled = []
    for r in rules:
        allow = [re.compile(re.escape(a), re.I) for a in r.get("allow") or []]
        compiled.append((r["label"], re.compile(r["pattern"], re.I), allow))

    files = _files(ctx)
    if not any(p.suffix == ".html" for p in files):
        return [ctx.finding("(site)", "no HTML scanned in %s: a clean run on "
                            "zero files is not evidence" % ctx.rel(ctx.public_dir))]

    findings = []
    for path in files:
        text = ctx.read_text(path)
        for label, rx, allow in compiled:
            spans = [m.span() for a in allow for m in a.finditer(text)]
            hits = [m for m in rx.finditer(text)
                    if not any(s <= m.start() and m.end() <= e for s, e in spans)]
            if hits:
                m = hits[0]
                findings.append(ctx.finding(
                    path, "%s: %d occurrence(s), first %r"
                    % (label, len(hits), m.group(0)),
                    _context(text, m.start(), m.end())))
    return findings
