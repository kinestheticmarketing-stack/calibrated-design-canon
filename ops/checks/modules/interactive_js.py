"""interactive_js -- every interactive tool page ships inline tool JS that parses.

Source (identical in all three sites): _postbuild_check.py:check_interactive_js
(DCI :52, LGM :50, GCI :49), check C1 "INTERACTIVE-JS".

Ported faithfully:
- pages are the TOP-LEVEL public/*.html only (the sites glob '*.html', not
  recursively), selected by basename regex calculator|checker|comparator (re.I);
- inline scripts = <script> without src=, non-blank bodies;
- no inline script -> finding; none containing 'addEventListener' -> finding;
- every addEventListener script is fed to `node --check -` on stdin; a non-zero
  exit -> finding with node's first stderr line;
- zero matching pages -> one finding ("the pattern is stale").

Shells out to the local `node` binary (no network). If node is absent the
module raises: it cannot judge, so the run exits 2 rather than reading as a pass.
"""

import re
import subprocess

NAME = "interactive_js"
DESCRIPTION = ("Interactive tool pages (calculator/checker/comparator) must ship "
               "inline JS that wires addEventListener and parses under node --check.")
REQUIRES = {}
OPTIONS = {
    "pattern": r"calculator|checker|comparator",  # basename regex, case-insensitive
    "node": "node",                               # node executable
}

_SCRIPT = re.compile(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', re.S)


def _top_level_pages(ctx):
    return sorted(p for p in ctx.public_dir.glob("*.html") if p.is_file())


def check(ctx):
    findings = []
    interactive = re.compile(ctx.options["pattern"], re.I)
    node = ctx.options["node"]
    found = 0
    for p in _top_level_pages(ctx):
        base = p.name
        if not interactive.search(base):
            continue
        found += 1
        src = ctx.read_text(p)
        inline = [s for s in _SCRIPT.findall(src) if s.strip()]
        if not inline:
            findings.append(ctx.finding(p, "no inline <script> at all",
                                        "%s: no inline <script> at all" % base))
            continue
        tool = [s for s in inline if "addEventListener" in s]
        if not tool:
            msg = ("has %d inline script(s) but none calls addEventListener -- "
                   "the tool JS is missing, the page is inert" % len(inline))
            findings.append(ctx.finding(p, msg, "%s: %s" % (base, msg)))
            continue
        for i, s in enumerate(tool):
            r = subprocess.run([node, "--check", "-"], input=s,
                               capture_output=True, text=True)
            if r.returncode != 0:
                first = (r.stderr.strip().splitlines() or ["?"])[0]
                findings.append(ctx.finding(
                    p, "tool script #%d does not parse" % i,
                    "%s: tool script #%d does not parse -- %s" % (base, i, first)))
    if found == 0:
        findings.append(ctx.finding(
            "(site)", "no interactive pages matched; the pattern is stale",
            "no interactive pages matched /%s/ in top-level %s/*.html"
            % (ctx.options["pattern"], ctx.public_dir.name)))
    return findings
