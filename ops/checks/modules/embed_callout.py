"""embed_callout -- every calculator page renders exactly one "take this
calculator" embed callout, and its button points at a real file.
Sources: DCI _postbuild_check.py:check_embed_locks (L1); LGM
_postbuild_check.py:check_embed_callout; GCI _postbuild_check.py:check_k15_lock (c).

The three sites diverged; this port runs ALL THREE matchers on every listed
page and a page must satisfy each one (union of findings = strictest):
  dci  the heading occurs exactly once in raw HTML AND the DCI regex
       (<div style> -> <p><strong>heading</strong></p> ... <a class="btn"
       href="X">button text</a> ... </div>) matches exactly once; X must start
       with '/' and be a file in public/ (taken literally, as DCI does).
  lgm  exactly one <div> whose style carries callout_style has an element span
       containing <a class="btn" href="X">button text</a>. With option
       button_href set, X must equal it (LGM pins its href); unset, any href.
  gci  html.parser: exactly one <div> whose style carries callout_style and
       contains an <a class="btn"> whose collapsed text is the button text;
       every such href (query/fragment stripped) must start with '/' and be a
       file in public/.
Plus: every listed page must exist; option expected_page_count (GCI: 4) pins
the size of the page list.

  data.pages      .py file read with ast (never imported) or a one-per-line
                  list; entries are page paths or (path, label) tuples.
  data.pages_var  literal: assignment name in the .py file.
"""

import ast
import re
from html.parser import HTMLParser
from pathlib import Path

NAME = "embed_callout"
DESCRIPTION = ("Each calculator page renders exactly one embed callout whose "
               "'Get the embed code' button resolves (DCI+LGM+GCI matchers).")
REQUIRES = {
    "pages": "file holding the calculator page list (.py read via ast, or one path per line)",
    "pages_var": "literal: assignment name holding the page list in a .py pages file",
}
LITERAL_KEYS = {"pages_var"}
OPTIONS = {
    "heading": "Want this calculator on your own website? Take it.",
    "button_text": "Get the embed code",
    "callout_style": "border:2px solid var(--primary)",
    "button_href": None,          # LGM: pinned href; None = any href
    "expected_page_count": None,  # GCI: 4
}

_WRAPPERS = {"frozenset", "set", "tuple", "list", "sorted"}


def _collapse(s):
    return re.sub(r"\s+", " ", s).strip()


def _literal(node):
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in _WRAPPERS and len(node.args) <= 1 and not node.keywords):
        return list(_literal(node.args[0])) if node.args else []
    return ast.literal_eval(node)


def _pages_from_py(path, var):
    tree = ast.parse(Path(path).read_text(encoding="utf-8"), filename=str(path))
    value = None
    for node in tree.body:
        targets, val = [], None
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            val = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value:
            targets, val = [node.target.id], node.value
        if var in targets:
            value = val  # last top-level assignment wins, as at import time
    if value is None:
        raise ValueError("%s: no top-level assignment %r" % (path, var))
    out = []
    for e in _literal(value):
        if isinstance(e, (tuple, list)) and e and isinstance(e[0], str):
            e = e[0]
        if not isinstance(e, str):
            raise ValueError("%s: %r entry %r is not a page path" % (path, var, e))
        out.append(e)
    return out


def _load_pages(ctx):
    path = Path(ctx.data["pages"])
    if path.suffix == ".py":
        pages = _pages_from_py(path, ctx.data["pages_var"])
    else:
        pages = [ln.strip() for ln in ctx.read_text(path).splitlines()
                 if ln.strip() and not ln.strip().startswith("#")]
    return [p.lstrip("/") for p in pages]


def _element_span(text, start):
    """LGM _element_span: outer HTML of the element opening at `start`,
    depth-counted over same-named tags."""
    m = re.match(r"<([a-zA-Z][\w-]*)", text[start:])
    if not m:
        return ""
    tag = m.group(1)
    open_re = re.compile(r"<%s\b" % re.escape(tag), re.I)
    close_re = re.compile(r"</%s\s*>" % re.escape(tag), re.I)
    depth, i = 0, start
    while i < len(text):
        o = open_re.search(text, i)
        c = close_re.search(text, i)
        if c is None:
            return text[start:]
        if o is not None and o.start() < c.start():
            depth += 1
            i = o.end()
            continue
        depth -= 1
        i = c.end()
        if depth == 0:
            return text[start:i]
    return text[start:]


def _gci_callouts(raw, style, button_text):
    """GCI _embed_callouts: one href list per closed callout div."""

    class P(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.divs, self.anchor, self.found = [], None, []

        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if tag == "div":
                self.divs.append([style in (a.get("style") or ""), []])
            elif tag == "a" and "btn" in (a.get("class") or "").split():
                self.anchor = [a.get("href") or "", []]

        def handle_data(self, data):
            if self.anchor is not None:
                self.anchor[1].append(data)

        def handle_endtag(self, tag):
            if tag == "a" and self.anchor is not None:
                if _collapse("".join(self.anchor[1])) == button_text:
                    for d in self.divs:
                        if d[0]:
                            d[1].append(self.anchor[0])
                self.anchor = None
            elif tag == "div" and self.divs:
                is_callout, hrefs = self.divs.pop()
                if is_callout and hrefs:
                    self.found.append(hrefs)

    p = P()
    p.feed(raw)
    p.close()
    return p.found


def _resolves(ctx, href):
    return href.startswith("/") and (ctx.public_dir / href.lstrip("/")).is_file()


def check(ctx):
    o = ctx.options
    heading, btn, style, pin = (o["heading"], o["button_text"],
                                o["callout_style"], o["button_href"])
    if not btn or not style:
        raise ValueError("button_text and callout_style must be non-empty")
    pages = _load_pages(ctx)
    if not pages:
        raise ValueError("calculator page list is empty; nothing to judge")
    findings = []
    exp = o["expected_page_count"]
    if exp is not None and len(pages) != int(exp):
        findings.append(ctx.finding(ctx.data["pages"], "page list has %d pages, expected %s"
                                    % (len(pages), exp), ctx.data["pages_var"]))
    dci_re = None
    if heading:
        dci_re = re.compile(
            r'<div style="[^"]*">\s*<p><strong>' + re.escape(heading) +
            r'</strong></p>.*?<a class="btn" href="([^"]+)">' + re.escape(btn) +
            r'</a>.*?</div>', re.S)
    box_re = re.compile(r'<div\b[^>]*\bstyle="[^"]*' + re.escape(style) + r'[^"]*"[^>]*>')
    if pin:
        lgm_btn = re.compile(re.escape('<a class="btn" href="%s">%s</a>' % (pin, btn)))
    else:
        lgm_btn = re.compile(r'<a class="btn" href="[^"]*">' + re.escape(btn) + r'</a>')

    for name in pages:
        p = ctx.public_dir / name
        if not p.is_file():
            findings.append(ctx.finding(name, "calculator page missing from public/"))
            continue
        doc = ctx.read_text(p)
        # dci matcher
        if dci_re is not None:
            n = doc.count(heading)
            hrefs = dci_re.findall(doc)
            if n != 1 or len(hrefs) != 1:
                findings.append(ctx.finding(p, "[dci] %d callout heading(s), %d with a %r "
                                            "button; expected exactly 1" % (n, len(hrefs), btn),
                                            heading))
            elif not _resolves(ctx, hrefs[0]):
                findings.append(ctx.finding(p, "[dci] callout href %r does not resolve "
                                            "to a file in public/" % hrefs[0], hrefs[0]))
        # lgm matcher
        n = sum(1 for m in box_re.finditer(doc)
                if lgm_btn.search(_element_span(doc, m.start())))
        if n != 1:
            findings.append(ctx.finding(p, "[lgm] bordered callout box with %s button "
                                        "found %d time(s), expected exactly 1"
                                        % ("href %r" % pin if pin else "a", n), btn))
        # gci matcher
        found = _gci_callouts(doc, style, btn)
        if len(found) != 1:
            findings.append(ctx.finding(p, "[gci] %d embed callout(s), expected exactly 1"
                                        % len(found), btn))
        else:
            for href in found[0]:
                path = href.split("#")[0].split("?")[0]
                if not _resolves(ctx, path):
                    findings.append(ctx.finding(p, "[gci] callout href %r does not resolve "
                                                "to a file in public/" % href, href))
    return findings
