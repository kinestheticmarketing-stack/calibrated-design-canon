# Kickoff 37 / K14 rule: R8 part (d) ignores site chrome. Run: PYTHONDONTWRITEBYTECODE=1 python3 -m unittest ops/claim_gate/test_r8_chrome.py -v
import os
import sys
import unittest

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import claim_gate  # noqa: E402

# Test (d) of the kickoff (rebate verified-date carve-out) is not written: measured,
# the verified-date string sits inside <main> on every property, so no carve-out exists.

PAGE = """<!doctype html>
<html lang="en">
<head>
<title>{title}</title>
<meta name="description" content="{desc}">
<script>var tpl = "{script}";</script>
</head>
<body>
<header class="site-header"><a href="/">Acme Heating</a>
<nav><ul><li><a href="/services/">{topnav}</a></li><li><a href="/contact/">Contact</a></li></ul></nav>
</header>
<main>
<h1>Heat pump rebates</h1>
<p>{body}</p>
<nav aria-label="On this page"><a href="#how">{mainnav}</a></nav>
<h2 id="how">How it works</h2>
<p>Book a visit and we handle the paperwork.</p>
</main>
<footer class="site-footer">
<ul>{footer}</ul>
<p>Last reviewed <time datetime="2026-09-18">September 18, 2026</time></p>
</footer>
</body>
</html>
"""

DEFAULTS = dict(
    title="Heat Pump Rebates | Acme",
    desc="Rebates for heat pumps in Denver.",
    script="hello",
    topnav="Services",
    body="Most homeowners qualify for a rebate on a new heat pump.",
    mainnav="How it works",
    footer='<li><a href="/guides/a/">Guide A</a></li>',
)

MORE_GUIDES = ('<li><a href="/guides/a/">Guide A</a></li>'
               '<li><a href="/guides/b/">Guide B</a></li>')


def page(**kw):
    d = dict(DEFAULTS)
    d.update(kw)
    return PAGE.format(**d)


NO_MAIN = """<!doctype html>
<html><head><title>Guide</title></head>
<body>
<header><nav><a href="/">Home</a></nav></header>
<div class="content">
<h1>Guide</h1>
<p>Furnace sizing explained.</p>
<footer class="article-footer"><p>{nested}</p></footer>
</div>
<footer class="site-footer"><p>{site}</p></footer>
</body></html>
"""


def nomain(nested="Written by the Acme team.", site="Acme Heating, Denver"):
    return NO_MAIN.format(nested=nested, site=site)


def differs(a, b):
    return claim_gate._visible_text_differs("page.html", a, b)


class R8ChromeTest(unittest.TestCase):

    def test_a_footer_only_change_not_differs(self):
        self.assertFalse(differs(page(), page(footer=MORE_GUIDES)))

    def test_b_main_body_change_differs(self):
        self.assertTrue(differs(page(), page(body="Most homeowners qualify.")))

    def test_c1_title_change_differs(self):
        self.assertTrue(differs(page(), page(title="Heat Pump Rebates 2026 | Acme")))

    def test_c2_meta_description_change_preserves_pre_k37(self):
        # Measured: surfaces.visible_text never included meta[description] (it is
        # surface S_META, not TITLE or ATTR alt|title|aria-label), so part (d) never
        # named meta-only changes, before or after K37. Pre-K37 behaviour: False.
        a, b = page(), page(desc="Changed description text.")
        self.assertNotIn("Rebates for heat pumps",
                         claim_gate.visible_text_of("page.html", a))
        self.assertFalse(differs(a, b))

    def test_e_nav_inside_main_change_differs(self):
        self.assertTrue(differs(page(), page(mainnav="How the rebate works")))

    def test_f_site_header_nav_change_not_differs(self):
        self.assertFalse(differs(page(), page(topnav="Our Services")))

    def test_g1_no_main_body_child_footer_not_differs(self):
        self.assertFalse(differs(nomain(), nomain(site="Acme Heating, Boulder")))

    def test_g2_no_main_nested_footer_differs(self):
        self.assertTrue(differs(nomain(), nomain(nested="Written by J. Smith.")))

    def test_h_pin_hash_still_includes_chrome(self):
        a, b = page(), page(footer=MORE_GUIDES)
        self.assertNotEqual(claim_gate.visible_text_sha256("page.html", a),
                            claim_gate.visible_text_sha256("page.html", b))

    def test_i_footer_tag_in_script_does_not_drop_body(self):
        a = page(script="<footer>x</footer>")
        b = page(script="<footer>x</footer>", body="Most homeowners qualify.")
        self.assertTrue(differs(a, b))

    def test_i2_unclosed_chrome_tag_in_body_script_is_not_an_element(self):
        # Two script strings outside <main>, "<header>" before it and "</header>"
        # after it: read as elements they would open and close a removal span
        # that swallows <main>. The parser must see script text, not tags.
        raw = ("<html><body><script>var s = '<header>';</script>"
               "<main><p>Keep this copy.</p></main>"
               "<script>var t = '</header>';</script></body></html>")
        self.assertIn("Keep this copy.", claim_gate.strip_site_chrome(raw))

    def test_j_self_closing_non_void_tag_still_nests(self):
        # A browser ignores the slash on <div/>, so this footer is nested in the
        # div, not a direct child of <body>, and must still count.
        a = "<html><body><div/><footer>Written by J. Smith.</footer></div></body></html>"
        b = a.replace("J. Smith", "A. Jones")
        self.assertTrue(differs(a, b))


if __name__ == "__main__":
    unittest.main()
