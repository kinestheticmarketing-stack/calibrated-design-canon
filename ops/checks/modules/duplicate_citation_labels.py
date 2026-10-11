"""duplicate_citation_labels -- two cited-stat blocks on one page whose visible
link labels are identical (case/whitespace-insensitive), so a reader cannot
tell the sources apart. Ported verbatim from check_duplicate_labels (C3,
'DUP-LABEL') in DCI, LGM and GCI _postbuild_check.py (identical in all three).

Port note: the site checks glob public/*.html (top level only); this module
uses ctx.iter_html() (recursive), a superset. All three sites currently ship
no nested HTML, so findings are identical today.
"""

import re

NAME = "duplicate_citation_labels"
DESCRIPTION = "Duplicate visible citation label among class=\"cited-stat\" blocks on one page."
REQUIRES = {}
OPTIONS = {}

_BLOCK = re.compile(r'class="cited-stat"[^>]*>(.*?)</p>', re.S)
_LINK = re.compile(r'<a [^>]*>(.*?)</a>', re.S)


def _labels(html):
    labels = []
    for block in _BLOCK.findall(html):
        m = _LINK.search(block)
        if m:
            labels.append(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(1))).strip().lower())
    return labels


def check(ctx):
    findings = []
    for page in ctx.iter_html():
        labels = _labels(ctx.read_text(page))
        dupes = sorted({x for x in labels if labels.count(x) > 1})
        for d in dupes:
            findings.append(ctx.finding(
                page, "DUP-LABEL: cited-stat label appears %d times" % labels.count(d), d))
    return findings
