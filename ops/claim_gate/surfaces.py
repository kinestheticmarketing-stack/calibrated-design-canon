"""surfaces.py -- the text_of() / surface extractor for the claim gate.

RULES_SPEC.md sections 2 and 3 are this module's specification. It answers the
open question canon's METHODS/CANDIDATE-do-not-scope-with-grep-over-html.md put
to the Director: the correct method is now the cheapest one, because the helper
ships.

python3 STDLIB ONLY. No pip, no lxml, no bs4 (spec 1).

Public surface, and nothing else:

  NORM_RAW / NORM_DEC / NORM_TXT / NORM_SRC   the four normalizations (spec 3)
  dec(s) / txt(s) / collapse(s)               the normalizers themselves
  sentences(s)                                sentence split over TXT
  Artifact                                    one parsed generated file
  parse_artifact(rel, path)                   parse ONE artifact into every surface
  GeneratorFacts                              CITED_SOURCES + constants + SRC text
  read_generators(repo, names)                tokenize-based generator reader

Every collection this module returns is sorted or insertion-stable, because the
gate must be byte-deterministic across runs (spec 4).
"""

import html
import io
import json
import re
import tokenize
import unicodedata
from html.parser import HTMLParser

# ---------------------------------------------------------------------------
# The four normalizations (spec 3)
# ---------------------------------------------------------------------------

NORM_RAW = "RAW"
NORM_DEC = "DEC"
NORM_TXT = "TXT"
NORM_SRC = "SRC"
NORMALIZATIONS = (NORM_RAW, NORM_DEC, NORM_TXT)

_WS = re.compile(r"\s+")
_SCRIPT_STYLE = re.compile(
    r"<(script|style)\b[^>]*>.*?</\1\s*>", re.IGNORECASE | re.DOTALL
)
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_TAG = re.compile(r"<[^>]+>")


def collapse(s):
    """All whitespace runs -> one space. The single most load-bearing line in
    this file: three separate recorded false zeroes came from a phrase that
    wrapped a source line break (spec 3, TXT)."""
    return _WS.sub(" ", s).strip()


def dec(s):
    """RAW with HTML entities decoded and Unicode normalised to NFC.
    `&amp;` is not what you typed; a raw substring count inflates by 4 per
    ampersand (spec 3, DEC)."""
    return unicodedata.normalize("NFC", html.unescape(s))


def txt(s):
    """DEC with script/style bodies removed, remaining tags stripped, and all
    whitespace runs collapsed (spec 3, TXT)."""
    s = _COMMENT.sub(" ", s)
    s = _SCRIPT_STYLE.sub(" ", s)
    s = _TAG.sub(" ", s)
    return collapse(dec(s))


_SENT = re.compile(r"(?<=[.!?…])\s+")


def sentences(s):
    """Sentence split over a TXT-normalized string. Deliberately simple and
    deterministic; a rule that needs a window instead of a sentence asks for a
    window."""
    out = []
    for part in _SENT.split(s):
        part = part.strip()
        if part:
            out.append(part)
    return out


# ---------------------------------------------------------------------------
# Surfaces (spec 3)
# ---------------------------------------------------------------------------

S_VIS = "VIS"
S_TITLE = "TITLE"
S_META = "META"
S_OG = "OG"
S_TW = "TW"
S_LD = "LD"
S_JS = "JS"
S_CSS = "CSS"
S_LOWVIS = "LOWVIS"
S_ATTR = "ATTR"
S_LLMS = "LLMS"
S_ROBOTS = "ROBOTS"
S_SITEMAP = "SITEMAP"
S_SVGTEXT = "SVGTEXT"
S_CITE = "CITE"      # claim-set: a resolved CITED_SOURCES entry's own text
S_CONST = "CONST"    # claim-set: a territorially-scoped shared constant

ALL_SURFACES = (
    S_VIS, S_TITLE, S_META, S_OG, S_TW, S_LD, S_JS, S_CSS, S_LOWVIS,
    S_ATTR, S_LLMS, S_ROBOTS, S_SITEMAP, S_SVGTEXT, S_CITE, S_CONST,
)

# LOWVIS: the tags three of the last five defects lived in (spec 3).
_LOWVIS_TAGS = frozenset(
    ("td", "th", "li", "summary", "option", "small", "caption",
     "figcaption", "button", "label", "a")
)
_ATTR_KEYS = ("alt", "title", "aria-label", "href", "content", "datetime")


class Surface(object):
    """One extracted span. `locator` is stable and printable."""

    __slots__ = ("key", "locator", "text")

    def __init__(self, key, locator, text):
        self.key = key
        self.locator = locator
        self.text = text

    def __repr__(self):  # pragma: no cover - debugging aid
        return "Surface(%r, %r, %r)" % (self.key, self.locator, self.text[:40])


class _HTMLSurfaces(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=False)
        self.stack = []
        self.surfaces = []
        self.ld_raw = []
        self.js_bodies = []
        self.css_bodies = []
        self.time_elements = []   # (datetime attr, inner text)
        self.image_refs = []      # every referenced image URL
        self.hrefs = []
        self.ids = []
        self._cur_script_type = None
        self._buf = []
        self._n = 0
        self._time_open = None

    # -- helpers ----------------------------------------------------------
    def _emit(self, key, text, hint=""):
        if not text or not text.strip():
            return
        self._n += 1
        loc = "%s#%d" % (key, self._n)
        if hint:
            loc = "%s#%d(%s)" % (key, self._n, hint)
        self.surfaces.append(Surface(key, loc, collapse(dec(text))))

    def _in(self, tags):
        for t in reversed(self.stack):
            if t in tags:
                return True
        return False

    # -- HTMLParser hooks -------------------------------------------------
    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        a = {}
        for k, v in attrs:
            if v is not None:
                a[k.lower()] = v
        self.stack.append(tag)

        if tag == "meta":
            name = a.get("name", "").lower()
            prop = a.get("property", "").lower()
            content = a.get("content", "")
            if name == "description":
                self._emit(S_META, content, "meta[description]")
            elif prop.startswith("og:"):
                self._emit(S_OG, content, prop)
                if prop == "og:image":
                    self.image_refs.append(content)
            elif name.startswith("twitter:"):
                self._emit(S_TW, content, name)
                if name == "twitter:image":
                    self.image_refs.append(content)
            elif name or prop:
                self._emit(S_ATTR, content, "meta[%s]" % (name or prop))
        elif tag == "script":
            self._cur_script_type = a.get("type", "").lower()
            self._buf = []
        elif tag == "style":
            self._cur_script_type = "text/css"
            self._buf = []
        elif tag == "img":
            if a.get("src"):
                self.image_refs.append(a["src"])
        elif tag == "time":
            self._time_open = (a.get("datetime", ""), [])

        if a.get("id"):
            self.ids.append(a["id"])
        if a.get("href"):
            self.hrefs.append(a["href"])
        for k in _ATTR_KEYS:
            if k in a and k != "content":
                self._emit(S_ATTR, a[k], "%s[%s]" % (tag, k))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "script":
            body = "".join(self._buf)
            if "ld+json" in (self._cur_script_type or ""):
                self.ld_raw.append(body)
            else:
                self.js_bodies.append(body)
            self._buf = []
            self._cur_script_type = None
        elif tag == "style":
            self.css_bodies.append("".join(self._buf))
            self._buf = []
            self._cur_script_type = None
        elif tag == "time" and self._time_open is not None:
            dt, parts = self._time_open
            self.time_elements.append((dt, collapse(dec("".join(parts)))))
            self._time_open = None
        # pop to the matching open tag if present
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self.stack and self.stack[-1] in ("script", "style"):
            self._buf.append(data)
            return
        if self._time_open is not None:
            self._time_open[1].append(data)
        if self._in(("title",)):
            self._emit(S_TITLE, data, "title")
        elif self._in(("head",)) and not self._in(("body",)):
            return
        elif self._in(_LOWVIS_TAGS):
            self._emit(S_LOWVIS, data, self.stack[-1])
        else:
            self._emit(S_VIS, data, self.stack[-1] if self.stack else "-")

    def handle_entityref(self, name):
        self.handle_data("&%s;" % name)

    def handle_charref(self, name):
        self.handle_data("&#%s;" % name)


_CITED_STAT = re.compile(
    r'<p class="cited-stat">(?P<body>.*?)</p>', re.DOTALL
)
_CITED_ANCHOR = re.compile(
    r'<a href="(?P<url>[^"]*)"[^>]*>(?P<label>.*?)</a>', re.DOTALL
)
_SVG_TEXT = re.compile(r"<text\b[^>]*>(?P<t>.*?)</text\s*>", re.DOTALL | re.I)
_LOC = re.compile(r"<loc>\s*(?P<loc>[^<]*)</loc>", re.I)
_LASTMOD = re.compile(r"<lastmod>\s*(?P<d>[^<]*)</lastmod>", re.I)
_URL_BLOCK = re.compile(r"<url>(?P<b>.*?)</url>", re.DOTALL | re.I)
_CSS_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_DISPLAY_NONE = re.compile(
    r"(?P<sel>[^{}]+)\{[^{}]*?(?:display\s*:\s*none|visibility\s*:\s*hidden)"
    r"[^{}]*\}",
    re.IGNORECASE,
)
# A JS string literal: single-quoted, double-quoted, or a BACKTICK TEMPLATE
# LITERAL. Escape-aware. The template-literal branch is the fix for the single
# highest-value blindness the adversarial read found: with no backtick branch a
# claim written `like this` reached NO rule, which defeated R1, R2, R4, R5, R7
# and R9 in one move, while the identical claim in a single-quoted literal was
# caught. Template literals may span newlines, so that branch does not exclude
# \n the way the quote branches do.
_JS_STRING = re.compile(
    r"'(?:[^'\\\n]|\\.)*'"
    r'|"(?:[^"\\\n]|\\.)*"'
    r"|`(?:[^`\\]|\\.)*`",
    re.DOTALL,
)
_JS_COMMENT = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)


LD_MAX_DEPTH = 64
LD_MAX_LEAVES = 20000


def _ld_leaves(obj, path, out, depth=0, over=None):
    """Every string leaf of a parsed JSON-LD block, with its JSON path.

    DEPTH-GUARDED. `[[[[...]]]]` nested 2000 deep is valid JSON, and the
    unguarded version raised RecursionError out of the parse loop, which exited
    1 with an empty report: a CI job reading $? saw "a rule failed" and a human
    reading the report saw nothing. Exceeding either limit is recorded and
    surfaces as a TRUNCATED note, never as silence."""
    if over is None:
        over = []
    if depth > LD_MAX_DEPTH:
        over.append("depth>%d at %s" % (LD_MAX_DEPTH, path))
        return over
    if len(out) >= LD_MAX_LEAVES:
        if not any(x.startswith("leaves>") for x in over):
            over.append("leaves>%d" % LD_MAX_LEAVES)
        return over
    if isinstance(obj, dict):
        for k in sorted(obj.keys()):
            _ld_leaves(obj[k], "%s.%s" % (path, k), out, depth + 1, over)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _ld_leaves(v, "%s[%d]" % (path, i), out, depth + 1, over)
    elif isinstance(obj, str):
        out.append((path, obj))
    elif obj is not None and not isinstance(obj, bool):
        out.append((path, str(obj)))
    return over


class Artifact(object):
    """One generated file, parsed ONCE into all of its surfaces.

    Parse once, run all eleven rules against this. Nothing re-reads a file.
    """

    def __init__(self, rel, kind, raw):
        self.rel = rel
        self.kind = kind            # html | txt | xml | svg
        self.raw = raw
        self.dec = dec(raw)
        self.doc_txt = txt(raw) if kind in ("html", "svg") else collapse(dec(raw))
        # TXT is BODY text. <title>/<meta> reach the rules through their own
        # surfaces; concatenating them into the body stream welded the title
        # onto the first body sentence and let a <title> word filter a body
        # claim, which is a false negative manufactured by normalization.
        if kind == "html":
            m = re.search(r"<body\b[^>]*>(.*)</body\s*>", raw,
                          re.DOTALL | re.IGNORECASE)
            self.txt = txt(m.group(1)) if m else self.doc_txt
        else:
            self.txt = self.doc_txt
        self.surfaces = []
        self.ld_docs = []           # (index, parsed-or-None, raw)
        self.ld_leaves = []         # (path, string)
        self.js_bodies = []
        self.js_strings = []        # (locator, decoded-ish literal text)
        self.js_comments = []       # (locator, comment text)
        self.css_bodies = []
        self.hidden_selectors = []
        self.time_elements = []
        self.image_refs = []
        self.hrefs = []
        self.ids = []
        self.cited_stats = []       # dicts: url, label, body, txt, quoted
        self.sitemap_entries = []   # (loc, lastmod)
        self.is_embed = False
        self.ld_parse_errors = []
        self.ld_truncated = []
        self.cite_keys = []         # filled by the claim-set builder

    # -- access ----------------------------------------------------------
    def stream(self, keys):
        """Every surface whose key is in `keys`, in parse order."""
        want = frozenset(keys)
        return [s for s in self.surfaces if s.key in want]

    def sentences(self):
        return sentences(self.txt)

    def level_text(self, level):
        if level == NORM_RAW:
            return self.raw
        if level == NORM_DEC:
            return self.dec
        return self.txt


def _parse_html(art):
    p = _HTMLSurfaces()
    p.feed(art.raw)
    p.close()
    art.surfaces.extend(p.surfaces)
    art.time_elements = list(p.time_elements)
    art.image_refs = list(p.image_refs)
    art.hrefs = list(p.hrefs)
    art.ids = list(p.ids)
    art.js_bodies = list(p.js_bodies)
    art.css_bodies = list(p.css_bodies)

    for i, body in enumerate(p.ld_raw):
        parsed = None
        try:
            parsed = json.loads(body)
        except Exception as exc:
            art.ld_parse_errors.append("LD[%d]: %s" % (i, exc.__class__.__name__))
        art.ld_docs.append((i, parsed, body))
        if parsed is not None:
            leaves = []
            over = _ld_leaves(parsed, "LD[%d]" % i, leaves)
            if over:
                art.ld_truncated.append("LD[%d]: %s" % (i, "; ".join(over)))
            for path, s in leaves:
                art.ld_leaves.append((path, s))
                art.surfaces.append(Surface(S_LD, path, collapse(dec(s))))
        else:
            art.surfaces.append(
                Surface(S_LD, "LD[%d](unparsed)" % i, collapse(dec(body))))

    for i, body in enumerate(art.js_bodies):
        art.surfaces.append(Surface(S_JS, "JS[%d]body" % i, collapse(body)))
        for m in _JS_COMMENT.finditer(body):
            art.js_comments.append(("JS[%d]@%d" % (i, m.start()), m.group(0)))
            art.surfaces.append(
                Surface(S_JS, "JS[%d]comment@%d" % (i, m.start()),
                        collapse(m.group(0))))
        stripped = _JS_COMMENT.sub(lambda m: " " * len(m.group(0)), body)
        for m in _JS_STRING.finditer(stripped):
            lit = m.group(0)[1:-1]
            art.js_strings.append(("JS[%d]str@%d" % (i, m.start()), lit))
            art.surfaces.append(
                Surface(S_JS, "JS[%d]str@%d" % (i, m.start()),
                        collapse(dec(txt(lit)))))

    for i, body in enumerate(art.css_bodies):
        art.surfaces.append(Surface(S_CSS, "CSS[%d]" % i, collapse(body)))
        # Comments out, at-rule preludes out. `@media (max-width: 799px)` is
        # not a selector, and a decorative /* -- Scroll-to-top -- */ banner is
        # not one either; naming them as selectors makes the TRAP line unusable
        # for the reader who has to adjudicate it.
        clean = _CSS_COMMENT.sub(" ", body)
        for m in _DISPLAY_NONE.finditer(clean):
            sel = collapse(m.group("sel"))
            sel = sel.rsplit("}", 1)[-1].rsplit("{", 1)[-1].strip()
            if not sel or sel.startswith("@"):
                continue
            art.hidden_selectors.append(sel)

    for m in _CITED_STAT.finditer(art.raw):
        body = m.group("body")
        am = _CITED_ANCHOR.search(body)
        url = am.group("url") if am else ""
        label = collapse(dec(_TAG.sub("", am.group("label")))) if am else ""
        # Look for an opening quote glyph in the TAG-STRIPPED, DECODED body.
        #
        # Testing RAW meant &#8220;, &#x201C; and the guillemets were invisible,
        # so a cited-stat publishing its stat as a verbatim quotation via a
        # numeric entity was not an R1 half-A candidate at all. But testing the
        # decoded body WITH TAGS still present walks straight into the trap the
        # spec names: a search for `"` finds href="..." and rel="noopener",
        # which made every cited-stat block read as quoted. Stripping tags
        # first removes the attribute delimiters and leaves only real
        # quotation marks, so the plain ASCII `"` (and &quot;, which decodes to
        # it) can be included honestly.
        bt = txt(body)
        quoted = any(g in bt for g in
                     ("\u201c", "\u201d", "\u00ab", "\u00bb", '"'))
        art.cited_stats.append({
            "offset": m.start(),
            "url": url,
            "label": label,
            "body": body,
            "txt": txt(body),
            "quoted": quoted,
        })
    return art


def _parse_js(art):
    """A bare .js artifact: the whole file is one inline script body, so R6's
    fixture reaches the same code path as a spliced-in page script."""
    art.js_bodies = [art.raw]
    art.surfaces.append(Surface(S_JS, "JS[0]body", collapse(art.raw)))
    for m in _JS_COMMENT.finditer(art.raw):
        art.js_comments.append(("JS[0]@%d" % m.start(), m.group(0)))
        art.surfaces.append(
            Surface(S_JS, "JS[0]comment@%d" % m.start(), collapse(m.group(0))))
    stripped = _JS_COMMENT.sub(lambda m: " " * len(m.group(0)), art.raw)
    for m in _JS_STRING.finditer(stripped):
        lit = m.group(0)[1:-1]
        art.js_strings.append(("JS[0]str@%d" % m.start(), lit))
        art.surfaces.append(
            Surface(S_JS, "JS[0]str@%d" % m.start(), collapse(dec(txt(lit)))))
    return art


def _parse_svg(art):
    for i, m in enumerate(_SVG_TEXT.finditer(art.raw)):
        art.surfaces.append(
            Surface(S_SVGTEXT, "%s:text[%d]" % (art.rel, i),
                    collapse(dec(_TAG.sub("", m.group("t"))))))
    return art


def _parse_sitemap(art):
    for i, m in enumerate(_URL_BLOCK.finditer(art.raw)):
        b = m.group("b")
        lm = _LOC.search(b)
        dm = _LASTMOD.search(b)
        loc = lm.group("loc").strip() if lm else ""
        mod = dm.group("d").strip() if dm else ""
        art.sitemap_entries.append((loc, mod))
        art.surfaces.append(
            Surface(S_SITEMAP, "sitemap[%d]" % i, "%s %s" % (loc, mod)))
    return art


def parse_artifact(rel, path, embed_paths=()):
    """Parse ONE artifact into every surface it has. One read, one parse."""
    with open(path, "rb") as fh:
        data = fh.read()
    raw = data.decode("utf-8", "replace")
    low = rel.lower()
    if low.endswith(".html") or low.endswith(".htm"):
        kind = "html"
    elif low.endswith(".svg"):
        kind = "svg"
    elif low.endswith(".xml"):
        kind = "xml"
    elif low.endswith(".js"):
        kind = "js"
    else:
        kind = "txt"

    art = Artifact(rel, kind, raw)
    art.is_embed = rel in set(embed_paths)
    if kind == "html":
        _parse_html(art)
    elif kind == "svg":
        _parse_svg(art)
    elif kind == "xml":
        _parse_sitemap(art)
    elif kind == "js":
        _parse_js(art)
    else:
        base = rel.rsplit("/", 1)[-1].lower()
        key = S_LLMS if base == "llms.txt" else (
            S_ROBOTS if base == "robots.txt" else S_VIS)
        art.surfaces.append(Surface(key, rel, collapse(dec(raw))))
    return art


# ---------------------------------------------------------------------------
# SRC -- generator-source normalization (spec 3, SRC)
# ---------------------------------------------------------------------------

def src_string_runs(source_text):
    """Walk maximal runs of ADJACENT STRING tokens with `tokenize`, decode and
    join each run into its real text.

    Required because this portfolio's prose is split across Python implicit
    concatenation boundaries -- `"...the primary rebate " "stack for
    Denver-area..."` -- so, verbatim from DCI's lane row, "no single-string grep
    or regex can see the phrase". The same row records that a raw-text regex
    spanning the boundary eats the quotes and breaks the file (it did, twice).
    Hence tokenize, never regex.
    """
    runs = []
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(source_text).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return runs
    cur = []
    start = None
    for tok in toks:
        if tok.type == tokenize.STRING:
            if not cur:
                start = tok.start[0]
            try:
                cur.append(_literal_str(tok.string))
            except Exception:
                cur.append(tok.string)
        elif tok.type in (tokenize.NL, tokenize.COMMENT):
            continue
        else:
            if cur:
                runs.append((start, "".join(cur)))
                cur = []
                start = None
    if cur:
        runs.append((start, "".join(cur)))
    return runs


def _literal_str(tok):
    import ast as _ast
    v = _ast.literal_eval(tok)
    return v if isinstance(v, str) else str(v)


class GeneratorFacts(object):
    """Everything the gate needs from the generators: CITED_SOURCES, the
    slug->cite_keys maps, module-level string constants, and the SRC text."""

    def __init__(self):
        self.cited_sources = {}     # key -> {field: value}
        self.slug_cite_keys = {}    # slug -> sorted list of keys
        self.constants = {}         # NAME -> joined string value
        self.src_text = {}          # module rel -> SRC-joined text
        self.modules = []
        self.provenance_present = False
        self.quote_true_count = 0
        self.quote_false_count = 0
        self.quote_absent_count = 0


def _ast_str(node):
    import ast as _ast
    if isinstance(node, _ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, _ast.JoinedStr):
        parts = []
        for v in node.values:
            if isinstance(v, _ast.Constant) and isinstance(v.value, str):
                parts.append(v.value)
            else:
                parts.append("{}")
        return "".join(parts)
    if isinstance(node, _ast.BinOp) and isinstance(node.op, _ast.Add):
        a = _ast_str(node.left)
        b = _ast_str(node.right)
        if a is not None and b is not None:
            return a + b
    return None


def _entry_fields(node):
    """A CITED_SOURCES entry, whether written as dict(...) or {...}."""
    import ast as _ast
    fields = {}
    if isinstance(node, _ast.Call) and isinstance(node.func, _ast.Name) \
            and node.func.id == "dict":
        for kw in node.keywords:
            if kw.arg is None:
                continue
            fields[kw.arg] = _const(kw.value)
    elif isinstance(node, _ast.Dict):
        for k, v in zip(node.keys, node.values):
            ks = _ast_str(k) if k is not None else None
            if ks:
                fields[ks] = _const(v)
    return fields


def _const(node):
    import ast as _ast
    if isinstance(node, _ast.Constant):
        return node.value
    s = _ast_str(node)
    if s is not None:
        return s
    if isinstance(node, (_ast.List, _ast.Tuple, _ast.Set)):
        return [_const(e) for e in node.elts]
    if isinstance(node, _ast.Dict):
        out = {}
        for k, v in zip(node.keys, node.values):
            ks = _ast_str(k) if k is not None else None
            if ks:
                out[ks] = _const(v)
        return out
    return None


def read_generators(repo, module_names):
    """ast + tokenize over the property's own generators. Never imports them --
    importing a generator would run it."""
    import ast as _ast
    import os

    facts = GeneratorFacts()
    for name in sorted(module_names):
        path = os.path.join(repo, name)
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        facts.modules.append(name)
        runs = src_string_runs(text)
        facts.src_text[name] = "\n".join(collapse(r[1]) for r in runs)
        try:
            tree = _ast.parse(text)
        except SyntaxError:
            continue
        for node in _ast.walk(tree):
            if not isinstance(node, _ast.Assign):
                continue
            targets = [t.id for t in node.targets if isinstance(t, _ast.Name)]
            if not targets:
                continue
            tname = targets[0]
            if tname == "CITED_SOURCES" and isinstance(node.value, _ast.Dict):
                for k, v in zip(node.value.keys, node.value.values):
                    ks = _ast_str(k) if k is not None else None
                    if not ks:
                        continue
                    facts.cited_sources[ks] = _entry_fields(v)
                continue
            val = _const(node.value)
            if isinstance(val, str):
                facts.constants[tname] = val
            elif isinstance(val, dict):
                # slug -> [KEY, ...] maps (DCI's CITED_STATS shape)
                ok = bool(val)
                for kk, vv in val.items():
                    if not (isinstance(vv, list) and vv and
                            all(isinstance(x, str) for x in vv)):
                        ok = False
                        break
                if ok:
                    for kk, vv in val.items():
                        facts.slug_cite_keys.setdefault(kk, [])
                        facts.slug_cite_keys[kk] = sorted(
                            set(facts.slug_cite_keys[kk]) | set(vv))

    for key in sorted(facts.cited_sources):
        e = facts.cited_sources[key]
        if "provenance" in e:
            facts.provenance_present = True
        if "quote" not in e:
            facts.quote_absent_count += 1
        elif e.get("quote") is True:
            facts.quote_true_count += 1
        else:
            facts.quote_false_count += 1
    # keep only slug maps whose values are real citation keys
    known = set(facts.cited_sources)
    if known:
        facts.slug_cite_keys = {
            k: v for k, v in facts.slug_cite_keys.items()
            if v and all(x in known for x in v)
        }
    else:
        facts.slug_cite_keys = {}
    return facts
