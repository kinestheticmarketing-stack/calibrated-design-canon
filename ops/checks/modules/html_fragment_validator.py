"""html_fragment_validator -- balanced-tag validation of built HTML.

Source (identical in all three sites; only a docstring example slug differs):
DCI/LGM/GCI _validators.py:validate_html_fragment (+ _FragmentValidator).

The site version runs at generation time on each data-dict HTML fragment and
raises HtmlValidationError on the first problem. This BUILD port applies the
same parser rules, unchanged, to every built page under public/: a page is the
concatenation of those fragments, so an unclosed, mismatched or stray tag in a
fragment surfaces in the page. Rules ported verbatim:
- void elements (VOID_ELEMENTS) need no close; a close tag for one is an error
- self-closing <x/> does not change balance
- every other start tag must be closed explicitly, in order (no HTML5
  optional-close leniency; OPTIONAL_CLOSE is empty in all three sites)
- stray close tag with an empty stack is an error
- tags left open at end of input are an error
Like the site version, the first problem stops validation of that input, so
there is at most one finding per page.
"""

from html.parser import HTMLParser

NAME = "html_fragment_validator"
DESCRIPTION = ("Unclosed, mismatched or stray tags, or close tags for void "
               "elements, in built HTML (port of _validators.validate_html_fragment).")
REQUIRES = {}
OPTIONS = {
    # Extra tags treated as optional-close (site OPTIONAL_CLOSE); empty in all sites.
    "optional_close": [],
    # Page paths relative to public_dir to skip (none needed today).
    "exclude": [],
}

# HTML5 void elements -- verbatim from the site _validators.py.
VOID_ELEMENTS = frozenset({
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
    'meta', 'param', 'source', 'track', 'wbr',
})


class _Problem(Exception):
    def __init__(self, msg, line, col, quote):
        super().__init__(msg)
        self.msg, self.line, self.col, self.quote = msg, line, col, quote


class _FragmentValidator(HTMLParser):
    def __init__(self, optional_close):
        super().__init__(convert_charrefs=True)
        self.optional_close = optional_close
        self.stack = []  # list of (tag, line, col)

    def _err(self, msg, quote, line=None, col=None):
        line = line if line is not None else self.getpos()[0]
        col = col if col is not None else self.getpos()[1]
        raise _Problem(msg, line, col, quote)

    def handle_starttag(self, tag, attrs):
        if tag in VOID_ELEMENTS or tag in self.optional_close:
            return
        line, col = self.getpos()
        self.stack.append((tag, line, col))

    def handle_startendtag(self, tag, attrs):
        return

    def handle_endtag(self, tag):
        q = "</%s>" % tag
        if tag in VOID_ELEMENTS:
            self._err("end tag </%s> for void element (no close tag allowed)" % tag, q)
        if tag in self.optional_close:
            return
        if not self.stack:
            self._err("stray close tag </%s> with no matching open" % tag, q)
        open_tag, open_line, open_col = self.stack[-1]
        if open_tag != tag:
            self._err("mismatched close: found </%s>, expected </%s> "
                      "(opened at line %d, col %d)" % (tag, open_tag, open_line, open_col), q)
        self.stack.pop()

    def finalize(self):
        if self.stack:
            unclosed = ', '.join('<%s> (line %d, col %d)' % t for t in self.stack)
            self._err("unclosed tags at end of fragment: %s" % unclosed,
                      ' '.join('<%s>' % t[0] for t in self.stack))


def validate(html_string, optional_close=frozenset()):
    """Return None if balanced, else (message, line, col, quote) for the first problem."""
    if not html_string:
        return None
    p = _FragmentValidator(frozenset(optional_close))
    try:
        p.feed(html_string)
        p.close()
        p.finalize()
    except _Problem as e:
        return e.msg, e.line, e.col, e.quote
    return None


def check(ctx):
    findings = []
    optional_close = frozenset(t.lower() for t in ctx.options["optional_close"])
    exclude = set(ctx.options["exclude"])
    for page in ctx.iter_html():
        if ctx.rel(page) in exclude:
            continue
        problem = validate(ctx.read_text(page), optional_close)
        if problem:
            msg, line, col, quote = problem
            findings.append(ctx.finding(
                page, "Validation failed at line %d, col %d: %s" % (line, col, msg), quote))
    return findings
