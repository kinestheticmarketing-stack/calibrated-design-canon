"""jsonld_parse -- every <script type="application/ld+json"> block must parse as JSON.

Source (identical in all three sites): _postbuild_check.py:check_jsonld in
DCI, LGM and GCI (C5). Ported faithfully: same regex (exact attribute string,
DOTALL, non-greedy), json.loads per block, one finding per unparseable block.
The sites scan only top-level public/*.html; that is the default here, with
option `recursive` to widen to public/**/*.html.
"""

import json
import re

NAME = "jsonld_parse"
DESCRIPTION = "Every JSON-LD <script> block in built HTML parses as JSON."
REQUIRES = {}
OPTIONS = {"recursive": False}

JSONLD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def check(ctx):
    if ctx.options.get("recursive"):
        pages = ctx.iter_html()
    else:
        pages = sorted(p for p in ctx.public_dir.glob("*.html") if p.is_file())
    findings = []
    for p in pages:
        for i, blk in enumerate(JSONLD_RE.findall(ctx.read_text(p))):
            try:
                json.loads(blk)
            except Exception as e:  # same breadth as the site check
                findings.append(ctx.finding(
                    p, "JSON-LD block %d does not parse -- %s" % (i, e),
                    blk.strip()[:120]))
    return findings
