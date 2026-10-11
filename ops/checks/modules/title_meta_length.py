"""title_meta_length -- <title> over TITLE_MAX or meta description over META_MAX
chars, or either tag missing.

Source: _postbuild_check.py:check_title_meta_length in DCI, LGM and GCI
(all three: TITLE_MAX = 60, META_MAX = 155). The three diverge; this module
takes the strictest behaviour of each (see README "Divergence" table):
  * missing tag: LGM/GCI fail, DCI is silent -> fail.
  * length: DCI/LGM count html.unescape(); GCI reverses only &quot; &gt; &lt;
    &amp; (so other entities count at full length) -> the larger of the two.
  * tag match: DCI's meta regex allows any whitespace and no trailing '>';
    LGM/GCI's requires `<meta name="description" content="...">` -> a tag is
    present if either matches; the length judged is the larger capture.
  * GCI exempts 404.html; DCI/LGM do not -> no exemption by default
    (option exempt_basenames exists, default empty).
  * sites scan public/*.html (top level); this scans recursively (superset).
"""

import html
import re

NAME = "title_meta_length"
DESCRIPTION = ("Title tag over title_max chars or meta description over "
               "meta_max chars (entity-decoded), or either tag missing.")
REQUIRES = {
    "title_max": "literal: integer title character cap (all three sites: 60)",
    "meta_max": "literal: integer meta description character cap (all three sites: 155)",
}
LITERAL_KEYS = {"title_max", "meta_max"}
OPTIONS = {"exempt_basenames": []}

TITLE_RE = re.compile(r'<title>(.*?)</title>', re.S)
# DCI form and LGM/GCI form, ported verbatim.
META_RES = (
    re.compile(r'<meta\s+name="description"\s+content="(.*?)"', re.S),
    re.compile(r'<meta name="description" content="(.*?)">', re.S),
)


def _gci_display_len(s):
    return len(s.replace('&quot;', '"').replace('&gt;', '>')
                .replace('&lt;', '<').replace('&amp;', '&'))


def _len(s):
    return max(len(html.unescape(s)), _gci_display_len(s))


def check(ctx):
    title_max = int(ctx.data["title_max"])
    meta_max = int(ctx.data["meta_max"])
    exempt = set(ctx.options.get("exempt_basenames") or [])
    findings = []
    for page in ctx.iter_html():
        if page.name in exempt:
            continue
        text = ctx.read_text(page)
        tm = TITLE_RE.search(text)
        if not tm:
            findings.append(ctx.finding(page, "no <title> tag found"))
        else:
            n = _len(tm.group(1))
            if n > title_max:
                findings.append(ctx.finding(
                    page, "title tag is %d chars, max is %d" % (n, title_max),
                    html.unescape(tm.group(1))))
        caps = [m.group(1) for m in (r.search(text) for r in META_RES) if m]
        if not caps:
            findings.append(ctx.finding(
                page, 'no <meta name="description"> tag found'))
        else:
            cap = max(caps, key=_len)
            n = _len(cap)
            if n > meta_max:
                findings.append(ctx.finding(
                    page, "meta description is %d chars, max is %d" % (n, meta_max),
                    html.unescape(cap)))
    return findings
