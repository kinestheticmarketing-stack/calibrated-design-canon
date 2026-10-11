"""keyboard_reachability -- a scroll region (overflow auto/scroll in the page's
own <style>) must be keyboard-reachable, and every <select> must have an
accessible name.

Sources, ported faithfully and run as a UNION (a page/class flagged by either
detector is a finding; see the README divergence row):
  DCI _postbuild_check.py:check_keyboard_reachability  (HTMLParser walk over
      classes from comment-stripped <style> rules; plus SELECT-NO-NAME)
  LGM _postbuild_check.py:check_scrollable_regions     (regex over <style>
      blocks + depth-counted element span + focusable-descendant regex)
GCI has no equivalent check.

Both sites scan public/*.html (top level only); option `recursive` widens it.
No site data is needed: the scrollable classes come from each page's own CSS.
"""

import html.parser
import re

NAME = "keyboard_reachability"
DESCRIPTION = ("Scroll regions declared in a page's own <style> must be "
               "keyboard-reachable; every <select> must have an accessible name.")
REQUIRES = {}
OPTIONS = {
    "recursive": False,     # sites scan public/*.html only
    "check_selects": True,  # DCI's SELECT-NO-NAME half
}

# ---------------------------------------------------------------- DCI port --
FOCUSABLE_TAGS = {'a', 'button', 'input', 'select', 'textarea', 'summary',
                  'audio', 'video', 'iframe', 'details'}
_SCROLL_DECL = re.compile(r'overflow(?:-x|-y)?\s*:\s*(?:auto|scroll)', re.I)
_STYLE_RULE = re.compile(r'([^{}]+)\{([^{}]*)\}', re.S)


def _scrolling_classes(doc_text):
    """DCI: class names the page's own stylesheet gives auto/scroll overflow.
    CSS comments are stripped first (a comment above a rule would otherwise be
    swallowed into the selector)."""
    out = set()
    for style in re.findall(r'<style[^>]*>(.*?)</style>', doc_text, re.S | re.I):
        style = re.sub(r'/\*.*?\*/', ' ', style, flags=re.S)
        for selector, body in _STYLE_RULE.findall(style):
            if not _SCROLL_DECL.search(body):
                continue
            for cls in re.findall(r'\.([A-Za-z0-9_-]+)', selector):
                out.add(cls)
    return out


class _KeyboardParser(html.parser.HTMLParser):
    """DCI: scroll-container reachability and <select> naming facts."""

    def __init__(self, scroll_classes):
        super().__init__(convert_charrefs=True)
        self.scroll_classes = scroll_classes
        self.label_fors = set()
        self.selects = []
        self.unreachable = []
        self._open_scrollers = []
        self._label_depth = 0
        self._in_style = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('style', 'script'):
            self._in_style += 1
            return
        if self._in_style:
            return
        if tag == 'label':
            self._label_depth += 1
            if a.get('for'):
                self.label_fors.add(a['for'])
        classes = set((a.get('class') or '').split())
        hit = classes & self.scroll_classes
        if hit:
            reachable = (a.get('tabindex') is not None
                         or a.get('contenteditable') in ('', 'true'))
            self._open_scrollers.append([sorted(hit)[0], reachable, tag])
        if tag in FOCUSABLE_TAGS and a.get('tabindex') != '-1':
            if tag != 'a' or a.get('href') is not None:
                for row in self._open_scrollers:
                    row[1] = True
        if tag == 'select':
            self.selects.append((a, self._label_depth > 0))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in ('style', 'script'):
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in ('style', 'script'):
            self._in_style = max(0, self._in_style - 1)
            return
        if self._in_style:
            return
        if tag == 'label':
            self._label_depth = max(0, self._label_depth - 1)
        if self._open_scrollers and self._open_scrollers[-1][2] == tag:
            cls, reachable, _ = self._open_scrollers.pop()
            if not reachable:
                self.unreachable.append(cls)


# ---------------------------------------------------------------- LGM port --
SCROLLABLE_DECL_RE = re.compile(
    r'\.([A-Za-z][\w-]*)\s*(?:,[^{]*)?\{[^}]*?\boverflow(?:-x|-y)?\s*:\s*'
    r'(?:auto|scroll)\b', re.I | re.S)
STYLE_BLOCK_RE = re.compile(r'<style[^>]*>(.*?)</style>', re.I | re.S)
FOCUSABLE_TAG_RE = re.compile(
    r'<(?:a\s[^>]*\bhref=|button\b|select\b|textarea\b|summary\b|iframe\b|'
    r'input\b(?![^>]*\btype="hidden")|[a-z]+\s[^>]*\btabindex="(?!-)[^"]*")',
    re.I)


def _element_span(text, start):
    """LGM: outer HTML of the element whose opening tag begins at `start`,
    depth-counted over same-named tags."""
    m = re.match(r'<([a-zA-Z][\w-]*)', text[start:])
    if not m:
        return ''
    tag = m.group(1)
    open_re = re.compile(r'<%s\b' % re.escape(tag), re.I)
    close_re = re.compile(r'</%s\s*>' % re.escape(tag), re.I)
    depth = 0
    i = start
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


def _lgm_unreachable(text):
    """LGM: {class: first offending opening tag}."""
    css = '\n'.join(STYLE_BLOCK_RE.findall(text))
    scrollable = {mm.group(1) for mm in SCROLLABLE_DECL_RE.finditer(css)}
    out = {}
    for cls in sorted(scrollable):
        for m in re.finditer(
                r'<[a-zA-Z][\w-]*\s[^>]*class="[^"]*(?<![\w-])'
                + re.escape(cls) + r'(?![\w-])[^"]*"', text):
            el = _element_span(text, m.start())
            opening = el[:el.find('>') + 1]
            if re.search(r'\btabindex="(?!-)[^"]*"', opening, re.I):
                continue
            if FOCUSABLE_TAG_RE.search(el[len(opening):]):
                continue
            out.setdefault(cls, opening)
    return out


# ------------------------------------------------------------------ check --
def _pages(ctx):
    if ctx.options.get("recursive"):
        return ctx.iter_html()
    return sorted(p for p in ctx.public_dir.glob("*.html") if p.is_file())


def check(ctx):
    findings = []
    for p in _pages(ctx):
        text = ctx.read_text(p)
        flagged = {}  # class -> [detectors]
        quotes = {}
        classes = _scrolling_classes(text)
        parser = _KeyboardParser(classes)
        parser.feed(text)
        parser.close()
        for cls in sorted(set(parser.unreachable)):
            flagged.setdefault(cls, []).append("DCI")
        for cls, opening in _lgm_unreachable(text).items():
            flagged.setdefault(cls, []).append("LGM")
            quotes[cls] = opening[:160]
        for cls in sorted(flagged):
            findings.append(ctx.finding(
                p,
                "SCROLL-REGION-UNREACHABLE: .%s scrolls (overflow auto/scroll "
                "in this page's own <style>) but neither it nor anything inside "
                "it can take keyboard focus; give it tabindex=\"0\" "
                "role=\"region\" and a per-instance aria-label (detector: %s)"
                % (cls, "+".join(flagged[cls])),
                quotes.get(cls, ".%s" % cls)))
        if not ctx.options.get("check_selects", True):
            continue
        for a, wrapped in parser.selects:
            named = (
                bool((a.get('aria-label') or '').strip())
                or bool((a.get('aria-labelledby') or '').strip())
                or bool((a.get('title') or '').strip())
                or wrapped
                or (a.get('id') is not None and a['id'] in parser.label_fors)
            )
            if not named:
                findings.append(ctx.finding(
                    p,
                    "SELECT-NO-NAME: <select id=%r> has no accessible name -- "
                    "no <label for>, no wrapping <label>, no "
                    "aria-label/aria-labelledby/title" % a.get('id'),
                    "<select id=%r>" % a.get('id')))
    return findings
