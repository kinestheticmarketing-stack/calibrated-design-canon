"""internal_links -- every internal root-relative .html href in built HTML must resolve.

Source: _check_links.py:check_internal in DCI (:42), LGM (:43) and GCI (same
as LGM). The judging logic is identical in all three; DCI alone adds a
`public_dir` injection point and a `--canary` self-test, both of which the
runner's fixture canary replaces here. Ported faithfully: same regexes
(href="/<[a-zA-Z0-9._-]*>.html" and bare href="/"), one finding per
unresolved target occurrence, bare "/" requires public/index.html. Outbound
(--check-outbound, network) is a DEPLOY check and is not ported.
The sites scan only top-level public/*.html; that is the default here, with
option `recursive` to widen to public/**/*.html.
"""

import re

NAME = "internal_links"
DESCRIPTION = "Every internal href=\"/x.html\" (and bare href=\"/\") in built HTML resolves to a file in public/."
REQUIRES = {}
OPTIONS = {"recursive": False}

INTERNAL_HREF_RE = re.compile(r'href="(/[a-zA-Z0-9._-]*\.html)"')
ROOT_HREF_RE = re.compile(r'href="/"')


def check(ctx):
    root = ctx.public_dir
    if ctx.options.get("recursive"):
        pages = ctx.iter_html()
    else:
        pages = sorted(p for p in root.glob("*.html") if p.is_file())
    findings = []
    for p in pages:
        content = ctx.read_text(p)
        if ROOT_HREF_RE.search(content) and not (root / "index.html").is_file():
            findings.append(ctx.finding(
                p, "broken internal link -> / (index.html does not exist in public/)",
                'href="/"'))
        for m in INTERNAL_HREF_RE.finditer(content):
            target = m.group(1)
            if not (root / target.lstrip("/")).is_file():
                findings.append(ctx.finding(
                    p, "broken internal link -> %s (target does not exist in public/)" % target,
                    m.group(0)))
    return findings
