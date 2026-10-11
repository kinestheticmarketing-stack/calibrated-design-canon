"""speakable_selectors -- a SpeakableSpecification cssSelector whose leading
class matches no element on its page (Google: SEVERE NO_MATCHES_FOUND).

Source (identical on all three sites): _postbuild_check.py:check_speakable
(DCI :555, LGM :466, GCI :451) plus its SPEAKABLE_SEL regex. Ported verbatim:
the cssSelector array is read from the raw page (JSON-LD lives in <script>),
the class inventory from markup with <style>/<script> bodies removed. Only a
leading class selector ('.x ...') is verified; other selectors are skipped.
"""

import re

NAME = "speakable_selectors"
DESCRIPTION = ("Every speakable cssSelector's leading class exists on the "
               "same page (else Google NO_MATCHES_FOUND).")
REQUIRES = {}
# The site checks glob public/*.html (top level only); recursive=True widens it.
OPTIONS = {"recursive": False}

SPEAKABLE_SEL = re.compile(r'"cssSelector":\s*\[(.*?)\]', re.S)


def _pages(ctx):
    if ctx.options.get("recursive"):
        return ctx.iter_html()
    return sorted(p for p in ctx.public_dir.glob("*.html") if p.is_file())


def check(ctx):
    findings = []
    for p in _pages(ctx):
        html = ctx.read_text(p)
        # Markup only: CSS rule bodies and script strings are not markup.
        markup = re.sub(r'<style[^>]*>.*?</style>', ' ', html, flags=re.S)
        markup = re.sub(r'<script[^>]*>.*?</script>', ' ', markup, flags=re.S)
        classes = set()
        for attr in re.findall(r'class="([^"]*)"', markup):
            classes.update(attr.split())
        for blk in SPEAKABLE_SEL.findall(html):
            for sel in re.findall(r'"([^"]+)"', blk):
                lead = sel.split()[0]
                if not lead.startswith('.'):
                    continue  # not a class selector; nothing to verify here
                if lead.lstrip('.') not in classes:
                    findings.append(ctx.finding(
                        p,
                        'cssSelector "%s" matches no element on this page '
                        '(Google reports this as a SEVERE NO_MATCHES_FOUND)'
                        % sel,
                        sel))
    return findings
