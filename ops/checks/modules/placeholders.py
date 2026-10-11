"""placeholders -- no unsubstituted placeholder token reaches a reader.

Source (C2 check_placeholders in each site's _postbuild_check.py):
  DCI _postbuild_check.py:163, LGM :140, GCI :168.

All three share the same base TOKEN alternation (__TOKEN__, REPLACE_WITH_X,
YOUR_X_HERE, AUTHORING_REQUIRED, {{ handlebars }}, %TOKEN%, CHANGE_ME, FIXME,
Lorem ipsum). They diverge in two ways, resolved here by taking the strictest
(union) behaviour -- see the K44 divergence row:

  * Scope of the base TOKEN: DCI scans the RAW page (script/style included);
    LGM and GCI scan markup only. Raw is a superset, so raw is used.
  * Bracket and call-shaped leaks ([[CITE:KEY]], {sc.cite_inline('KEY')}):
    every site scans these over MARKUP ONLY (script/style bodies stripped),
    but with three different regexes. All three regexes are applied (union),
    over markup only, exactly as each site does.

Like the site checks, only top-level public/*.html is scanned by default
(option recursive=true widens to public/**/*.html). One finding per page,
quote = the sorted distinct hits.
"""

import re

NAME = "placeholders"
DESCRIPTION = ("No unsubstituted placeholder token (__X__, REPLACE_WITH_X, "
               "{{x}}, [[CITE:K]], {f(x)}, ...) in built HTML.")
REQUIRES = {}
OPTIONS = {"recursive": False}

# Base alternation: byte-identical in DCI/LGM/GCI. Scanned over RAW text (DCI).
TOKEN = re.compile(
    r'__[A-Z][A-Z0-9_]*__'                      # __LEGACY_TOKEN__
    r'|REPLACE[_-]WITH[_-][A-Z0-9_]{3,}'        # REPLACE_WITH_SOMETHING
    r'|YOUR[_-][A-Z0-9_]{2,}[_-]HERE'           # YOUR_TOKEN_HERE
    r'|AUTHORING[_-]?REQUIRED'
    r'|\{\{\s*[A-Za-z_][A-Za-z0-9_.]*\s*\}\}'   # {{ handlebars }}
    r'|%[A-Z][A-Z0-9_]{2,}%'                    # %TOKEN%
    r'|CHANGE[_-]ME\b'
    r'|\bFIXME\b'
    r'|(?i:\bLorem ipsum\b)')                   # the one case-blind marker

# Markup-only shapes: each site's own regexes, applied as a union.
MARKUP_SHAPES = (
    # DCI CALL_SHAPE
    re.compile(r'\{[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*'
               r'\([^{}\n]*\)\}'),
    # DCI CITE_BRACKET
    re.compile(r'\[\[\s*[A-Za-z_][A-Za-z0-9_]*\s*:[^\]\n]*\]\]'),
    # LGM bracket + call alternatives
    re.compile(r'\[\[[A-Z][A-Z0-9_]*:[^\]\n]+\]\]'),
    re.compile(r'(?<!\$)\{[A-Za-z_][A-Za-z0-9_.]*\([^{}\n]*\)\}'),
    # GCI bracket + call alternatives
    re.compile(r'\[\[[A-Z][A-Z0-9_]*(?::[A-Za-z0-9_]+)?\]\]'),
    re.compile(r'\{[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?'
               r'\([^{}()]*\)\}'),
)


def _strip_script_style(html_text):
    """Markup only: drop <style>/<script> bodies (identical in all three)."""
    t = re.sub(r'<style[^>]*>.*?</style>', ' ', html_text, flags=re.S)
    t = re.sub(r'<script[^>]*>.*?</script>', ' ', t, flags=re.S)
    return t


def _pages(ctx):
    if ctx.options.get("recursive"):
        return ctx.iter_html()
    return sorted(p for p in ctx.public_dir.glob("*.html") if p.is_file())


def check(ctx):
    findings = []
    for page in _pages(ctx):
        text = ctx.read_text(page)
        hits = {m.group(0) for m in TOKEN.finditer(text)}
        markup = _strip_script_style(text)
        for rx in MARKUP_SHAPES:
            hits |= {m.group(0) for m in rx.finditer(markup)}
        if hits:
            findings.append(ctx.finding(
                page, "%d unsubstituted placeholder token(s)" % len(hits),
                " ".join(sorted(hits))))
    return findings
