"""facts_caveat_distance -- a registered claim renders without its hedge
close by, or a listed page drops the claim's safety caveat.

Gap K22. Reads <site>/facts/registry.json (a JSON array of records).

Hedge: for every record with a non-null hedge {text, max_words}, every
public *.html page is scanned (listed pages and any other page where the
claim shows up). For each occurrence of normalize(claim) in the page's body
text, the occurrence's innermost block ancestor (p, li, td, th, dd, dt,
blockquote, figcaption, h1-h6, div, section, article, aside, header, footer,
main, nav; <body> when there is none) must contain normalize(hedge.text)
with at most max_words words between the claim and the hedge, on either
side. One finding per occurrence that fails.

Safety caveat: for every record with a non-null safety_caveat, one finding
per listed page path whose text lacks normalize(safety_caveat). Text is the
body surface for .html, the whole file otherwise (llms.txt). A listed page
that does not exist is one finding (it cannot carry the caveat).

Body (K50 spec "Surfaces"): visible text of <body> excluding script, style,
template, noscript, svg, and every subtree whose element has a class
starting "embed-". Block boundaries and <br> separate words; inline tags do
not. Matching is validate_facts.normalize(needle) in normalize(text),
case-sensitive.

Data keys:
  facts_registry  path to the property's facts/registry.json

Records are read with validate_facts.load(); an unreadable registry raises
FactsUnreadable (exit 2). Malformed fields (claim, hedge, safety_caveat,
pages) are skipped silently: facts_schema reports them.

NOT ENABLED unless a site manifest names it.
"""

import importlib.util
from html.parser import HTMLParser
from pathlib import Path

_VF_PATH = Path(__file__).resolve().parents[2] / "facts" / "validate_facts.py"
_spec = importlib.util.spec_from_file_location("_facts_validate_facts", _VF_PATH)
validate_facts = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate_facts)
normalize = validate_facts.normalize

NAME = "facts_caveat_distance"
DESCRIPTION = ("Registered claim whose hedge is not within max_words in the "
               "same block, or listed page missing the claim's safety caveat.")
REQUIRES = {
    "facts_registry": "path to the property's facts/registry.json",
}

BLOCKS = {"p", "li", "td", "th", "dd", "dt", "blockquote", "figcaption",
          "h1", "h2", "h3", "h4", "h5", "h6", "div", "section", "article",
          "aside", "header", "footer", "main", "nav"}
SKIP = {"script", "style", "template", "noscript", "svg"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}
# tags that break words visually without being one of the listed blocks
BREAKS = {"br", "hr", "tr", "ul", "ol", "dl", "table", "figure", "form",
          "body", "html", "head"}


class _Body(HTMLParser):
    """Collects body text as segments (text, chain) where chain is the tuple
    of open block ids (outermost first). Skipped subtrees contribute nothing.
    Block boundaries and BREAKS contribute a separator (None text)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # [tag, block_id or None, skips]
        self.skip = 0
        self.next_id = 0
        self.in_head = False
        self.saw_body = False
        self.segs = []           # (text or None, chain, in_body_tag)
        self.in_body = False

    def _chain(self):
        return tuple(e[1] for e in self.stack if e[1] is not None)

    def _sep(self):
        if not self.skip:
            self.segs.append((None, self._chain(), self.in_body))

    def _close(self, i):
        while len(self.stack) > i:
            tag, bid, skips = self.stack.pop()
            if skips:
                self.skip -= 1
            if bid is not None or tag in BREAKS:
                self._sep()

    def handle_starttag(self, tag, attrs):
        if tag == "head":
            self.in_head = True
        elif tag == "body":
            self.in_head = False
            self.in_body = self.saw_body = True
        if tag in BLOCKS or tag == "li":
            # implied ends: a block closes an open <p>; <li> closes an open <li>
            for i in range(len(self.stack) - 1, -1, -1):
                t = self.stack[i][0]
                if t == "p" or (tag == "li" and t == "li"):
                    self._close(i)
                    break
                if t in BLOCKS or t in ("ul", "ol", "table"):
                    break
        if tag in VOID:
            if tag in BREAKS:
                self._sep()
            return
        cls = ""
        for k, v in attrs:
            if k == "class" and v:
                cls = v
        skips = tag in SKIP or any(c.startswith("embed-") for c in cls.split())
        bid = None
        if tag in BLOCKS:
            bid = self.next_id
            self.next_id += 1
        if bid is not None or tag in BREAKS:
            self._sep()
        self.stack.append([tag, bid, skips])
        if skips:
            self.skip += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False
        elif tag == "body":
            self.in_body = False
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                self._close(i)
                return

    def handle_data(self, data):
        if self.skip or self.in_head:
            return
        if self.stack and self.stack[-1][0] == "title":
            return
        self.segs.append((data, self._chain(), self.in_body))


def _common(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return a[:n]


def body_text(src):
    """(text, owners): normalized body text and, per character, the chain of
    block ids it sits in. A separator space owns the common ancestor chain of
    its neighbours, so a claim straddling two blocks belongs to their
    common block."""
    p = _Body()
    p.feed(src)
    p.close()
    segs = [(t, c) for t, c, b in p.segs if b or not p.saw_body]
    chars, owners = [], []
    pending = None              # chain owed a space, or None
    for text, chain in segs:
        if text is None:
            pending = chain if pending is None else _common(pending, chain)
            continue
        n = normalize(text)
        if not n:
            if text:
                pending = chain if pending is None else _common(pending, chain)
            continue
        if text[:1].isspace():
            pending = chain if pending is None else _common(pending, chain)
        if pending is not None and chars:
            prev = owners[-1]
            chars.append(" ")
            owners.append(_common(_common(prev, chain), pending))
        pending = None
        for ch in n:
            chars.append(ch)
            owners.append(chain)
        if text[-1:].isspace():
            pending = chain
    return "".join(chars), owners


def _finds(hay, needle, lo=0, hi=None):
    hi = len(hay) if hi is None else hi
    out, i = [], hay.find(needle, lo, hi)
    while i >= 0:
        out.append(i)
        i = hay.find(needle, i + len(needle), hi)
    return out


def _words(s):
    return len(s.split())


def _region(owners, chain, start, end):
    """[lo, hi) of the contiguous run around [start, end) whose owner chains
    all begin with `chain` (the block's subtree)."""
    k = len(chain)
    lo, hi = start, end
    while lo > 0 and owners[lo - 1][:k] == chain:
        lo -= 1
    while hi < len(owners) and owners[hi][:k] == chain:
        hi += 1
    return lo, hi


def _hedge_findings(ctx, page, text, owners, key, claim, hedge, max_words):
    out = []
    for s in _finds(text, claim):
        e = s + len(claim)
        chain = owners[s]
        for o in owners[s:e]:
            chain = _common(chain, o)
        lo, hi = _region(owners, chain, s, e)
        best = None
        for h in _finds(text, hedge, lo, hi):
            he = h + len(hedge)
            if he <= s:
                gap = _words(text[he:s])
            elif h >= e:
                gap = _words(text[e:h])
            else:
                gap = 0
            best = gap if best is None else min(best, gap)
        if best is not None and best <= max_words:
            continue
        why = ("not in the claim's block" if best is None else
               "%d words from the claim" % best)
        out.append(ctx.finding(
            page, "%s: hedge %r %s (max %d words)"
            % (key, hedge, why, max_words), text[lo:hi]))
    return out


def check(ctx):
    reg = ctx.data["facts_registry"]
    records = validate_facts.load(reg)
    findings = []
    pages = {}

    def page_text(path):
        if path not in pages:
            src = ctx.read_text(path)
            pages[path] = body_text(src) if path.suffix == ".html" \
                else (normalize(src), None)
        return pages[path]

    html_pages = list(ctx.iter_html())
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            continue
        key = rec.get("key") if isinstance(rec.get("key"), str) else "#%d" % i
        claim = rec.get("claim")
        claim = normalize(claim) if isinstance(claim, str) else ""
        hedge = rec.get("hedge")
        if claim and isinstance(hedge, dict):
            ht, mw = hedge.get("text"), hedge.get("max_words")
            ht = normalize(ht) if isinstance(ht, str) else ""
            if ht and isinstance(mw, int) and not isinstance(mw, bool) \
                    and mw >= 1:
                for page in html_pages:
                    text, owners = page_text(page)
                    findings += _hedge_findings(ctx, page, text, owners, key,
                                                claim, ht, mw)
        cav = rec.get("safety_caveat")
        cav = normalize(cav) if isinstance(cav, str) else ""
        plist = rec.get("pages")
        if not cav or not isinstance(plist, list):
            continue
        for entry in plist:
            rel = entry.get("path") if isinstance(entry, dict) else None
            if not isinstance(rel, str) or not rel:
                continue
            path = ctx.public_dir / rel
            if not path.is_file():
                findings.append(ctx.finding(
                    rel, "%s: listed page missing; safety caveat absent" % key,
                    cav))
                continue
            if cav not in page_text(path)[0]:
                findings.append(ctx.finding(
                    path, "%s: listed page lacks the safety caveat" % key, cav))
    return findings
