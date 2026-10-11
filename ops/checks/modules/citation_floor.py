"""citation_floor -- every content page carries >= 2 inline citations, and
service pages plus the homepage carry >= 3.

Source: DCI/LGM/GCI _postbuild_check.py:check_citation_floor (sitewide floor,
identical on all three) + DCI's SERVICE_PAGE_CITATION_MIN /
SERVICE_PAGES_AND_HOMEPAGE / SERVICE_CITATION_FLOOR_EXEMPT (COPY_VOICE.md:122).

Divergence (README "strictest choice"): only DCI enforced the service floor;
this module enforces it on every site. The service-page set is NOT hardcoded:
it is read from the site's own SERVICE_PAGES registry (a named assignment in a
.py file, extracted with ast.literal_eval -- the site code is never imported or
executed; or a JSON list), plus the homepage.

Counting is the site check's own: occurrences of the literal
class="cited-stat" in the raw page, over top-level public/*.html only (the
site checks glob public/*.html, not recursively).
"""

import ast
import json
import os

NAME = "citation_floor"
DESCRIPTION = ("Content pages need >= 2 inline citations (class=\"cited-stat\"); "
               "service pages and the homepage need >= 3.")
REQUIRES = {
    "service_pages": "file holding the site's service-page registry: a .py "
                     "file with a SERVICE_PAGES assignment (list of (url, name) "
                     "tuples or urls), or a .json list of the same",
}
OPTIONS = {
    "service_pages_var": "SERVICE_PAGES",   # assignment name in the .py file
    "citation_min": 2,                      # sitewide floor (CITATION_MIN)
    "service_citation_min": 3,              # SERVICE_PAGE_CITATION_MIN
    "homepage": "index.html",               # added to the service-floor set
    "exempt": ["404.html", "about.html", "contact.html", "privacy.html"],
    "service_floor_exempt": [],             # e.g. DCI's insulation-removal.html
    "marker": 'class="cited-stat"',         # what one citation renders as
}


def _literal_assignment(path, var):
    tree = ast.parse(open(path, encoding="utf-8").read(), filename=str(path))
    for node in tree.body:
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
        for t in targets:
            if isinstance(t, ast.Name) and t.id == var:
                return ast.literal_eval(node.value)
    raise ValueError("%s: no literal assignment %s found" % (path, var))


def _service_basenames(path, var):
    if str(path).endswith(".json"):
        entries = json.loads(open(path, encoding="utf-8").read())
    else:
        entries = _literal_assignment(path, var)
    names = set()
    for e in entries:
        url = e[0] if isinstance(e, (list, tuple)) else e
        if not isinstance(url, str) or not url:
            raise ValueError("service_pages entry is not a url: %r" % (e,))
        names.add(os.path.basename(url.split("#")[0].split("?")[0]))
    if not names:
        raise ValueError("service_pages registry %s is empty" % path)
    return names


def check(ctx):
    o = ctx.options
    marker = o["marker"]
    floor, svc_floor = int(o["citation_min"]), int(o["service_citation_min"])
    exempt = set(o["exempt"])
    svc = _service_basenames(ctx.data["service_pages"], o["service_pages_var"])
    svc.add(o["homepage"])
    svc -= set(o["service_floor_exempt"])

    findings = []
    pages = sorted(p for p in ctx.public_dir.glob("*.html") if p.is_file())
    for p in pages:
        base = p.name
        if base in exempt:
            continue
        n = ctx.read_text(p).count(marker)
        if n < floor:
            findings.append(ctx.finding(
                p, "CITATION-FLOOR: %d external citation(s), at least %d "
                   "required on every content page" % (n, floor),
                "%s has %d citation(s)" % (base, n)))
            continue
        if base in svc and n < svc_floor:
            findings.append(ctx.finding(
                p, "CITATION-FLOOR-SERVICE: %d external citation(s), at least "
                   "%d required on service pages and the homepage"
                   % (n, svc_floor),
                "%s has %d citation(s)" % (base, n)))
    return findings
