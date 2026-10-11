"""intra_similarity -- no two pages WITHIN one property share their authored
copy: 5-word-shingle Jaccard >= 0.30 between any pair fails.

Source: DCI/LGM/GCI _intra_similarity_check.py:main (byte-identical in all
three sites). Ported faithfully:
  - pages = top-level public/*.html only (os.listdir, not recursive), sorted,
    minus EXCLUDE;
  - text = raw page with STRIP_PATTERNS removed (regex, re.S|re.I), tags
    dropped, entities unescaped, lowercased, [^a-z0-9$%. ]+ -> space;
  - 5-word shingle sets; any shingle on >= max(2, int(n * 0.25)) pages is
    boilerplate and removed (the AUTHORED verdict -- the site's RAW number is
    informational only and is not ported);
  - every pair (itertools.combinations) with Jaccard >= threshold is a finding.
The site check returns 2 (cannot judge) when public/ is missing or fewer than
2 pages are scoreable; this module raises in that case.

Site-specific values are OPTIONS whose defaults are the (identical) site
constants: threshold, exclude, strip_patterns, shingle_n, boilerplate_fraction.
"""

import html
import itertools
import os
import re
from collections import Counter

NAME = "intra_similarity"
DESCRIPTION = ("No two pages in one property share authored copy: 5-word-shingle "
               "Jaccard >= 0.30 after removing site-wide boilerplate shingles.")
REQUIRES = {}
OPTIONS = {
    "threshold": 0.30,                      # THRESHOLD
    "shingle_n": 5,                         # SHINGLE_N
    "boilerplate_fraction": 0.25,           # BOILERPLATE_PAGE_FRACTION
    "exclude": ["404.html", "privacy.html", "contact.html", "about.html"],
    "strip_patterns": [                     # STRIP_PATTERNS
        r'<header class="site-nav".*?</header>',
        r'<footer.*?</footer>',
        r'<form[^>]*id="lead-form".*?</form>',
        r'<section[^>]*class="[^"]*form[^"]*".*?</section>',
        r'<aside class="risk-reversal".*?</aside>',
        r'<script.*?</script>',
        r'<style.*?</style>',
        r'<nav class="breadcrumb".*?</nav>',
    ],
}


def _text(path, strip_patterns):
    with open(path, encoding="utf-8") as f:
        s = f.read()
    for pat in strip_patterns:
        s = re.sub(pat, " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s).lower()
    s = re.sub(r"[^a-z0-9$%. ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _shingles(text, n):
    w = text.split()
    return {" ".join(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}


def _jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def check(ctx):
    opt = ctx.options
    threshold = float(opt["threshold"])
    n = int(opt["shingle_n"])
    exclude = set(opt["exclude"])
    public = str(ctx.public_dir)
    if not os.path.isdir(public):
        raise RuntimeError("public dir not found: %s" % public)

    pages = {}
    for name in sorted(os.listdir(public)):
        if not name.endswith(".html") or name in exclude:
            continue
        pages[name] = os.path.join(public, name)
    if len(pages) < 2:
        raise RuntimeError("fewer than 2 scoreable pages in %s" % public)

    raw = {k: _shingles(_text(p, opt["strip_patterns"]), n) for k, p in pages.items()}
    df = Counter()
    for sh in raw.values():
        df.update(sh)
    cutoff = max(2, int(len(pages) * float(opt["boilerplate_fraction"])))
    boiler = {s for s, c in df.items() if c >= cutoff}
    authored = {k: (sh - boiler) for k, sh in raw.items()}

    rows = []
    for a, b in itertools.combinations(sorted(authored), 2):
        j = _jaccard(authored[a], authored[b])
        if j >= threshold:
            rows.append((j, a, b))
    rows.sort(reverse=True)

    findings = []
    for j, a, b in rows:
        shared = sorted(authored[a] & authored[b])
        findings.append(ctx.finding(
            a,
            "authored-copy Jaccard %.4f >= %s with %s (%d shared %d-word shingles)"
            % (j, threshold, b, len(shared), n),
            shared[0] if shared else ""))
    return findings
