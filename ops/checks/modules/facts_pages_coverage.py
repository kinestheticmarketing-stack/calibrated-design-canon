"""facts_pages_coverage -- a registered fact renders where it is not listed, is
missing where it is listed, or is quoted/not quoted against its quote mode.

Gaps K08 (claim coverage: the registry's pages list is the truth about where a
claim renders) and K19 (quote vs paraphrase: a paraphrase must never sit inside
quotation marks; a quote must).

Surfaces of an .html page (one small HTMLParser below):
  title    <title> text
  meta     content of <meta name=X>, X not starting "twitter:"
  og       content of <meta property=og:*> except og:image:alt
  og_image content of <meta property="og:image:alt">
  twitter  content of <meta name|property=twitter:*>
  jsonld   every string value of each parseable application/ld+json block
  embed    subtree text of any element with a class starting "embed-"
  body     visible <body> text minus script/style/template/noscript/svg and
           minus embed subtrees
public/llms.txt is the single surface "llms". Nothing else is scanned. All
matching is validate_facts.normalize(needle) in normalize(surface),
case-sensitive.

Finding units, per registry record:
  (a) one per listed (page, surface) whose surface lacks the claim; a missing
      page file is one finding per listed surface;
  (b) one per (page, surface) across ALL public/**/*.html + llms.txt where the
      claim renders but the pair is not listed;
  (c) quote.mode "paraphrase": one per (page, surface) anywhere where
      quote.text sits inside quotation marks (“…” or "…" around the match, or
      inside a <q>/<blockquote> element);
  (d) quote.mode "quote": one per listed (page, surface) of an existing page
      where quote.text is not found inside quotation marks.

Data keys: facts_registry (path to facts/registry.json). Malformed record
fields are skipped silently (facts_schema reports them). An unreadable
registry raises FactsUnreadable: the module cannot judge, so the run exits 2.

NOT ENABLED on any site unless that site's manifest names it.
"""

import importlib.util
import json
from html.parser import HTMLParser
from pathlib import Path

_VF_PATH = Path(__file__).resolve().parents[2] / "facts" / "validate_facts.py"
_spec = importlib.util.spec_from_file_location("_facts_pages_coverage_validate_facts",
                                               _VF_PATH)
validate_facts = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate_facts)
normalize = validate_facts.normalize

NAME = "facts_pages_coverage"
DESCRIPTION = ("A registered claim is missing from a listed (page, surface), renders "
               "on an unlisted one, or its quote.text is quoted/unquoted against "
               "quote.mode.")
REQUIRES = {
    "facts_registry": "the property's facts registry (facts/registry.json)",
}

SURFACES = ("title", "meta", "og", "og_image", "twitter", "jsonld", "embed", "body",
            "llms")
_SKIP = {"script", "style", "template", "noscript", "svg"}
_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
         "param", "source", "track", "wbr"}
_INLINE = {"a", "abbr", "b", "bdi", "bdo", "cite", "code", "data", "dfn", "em", "i",
           "kbd", "mark", "q", "s", "samp", "small", "span", "strong", "sub", "sup",
           "time", "u", "var"}


class _Extractor(HTMLParser):
    """One pass over a page: surface -> list of text segments, plus the text
    of every <q>/<blockquote> as (surface, text)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.seg = {s: [] for s in SURFACES}
        self.quoted = []            # [surface, [parts]]
        self.stack = []             # [tag, skip, embed_parts|None, quoted|None]
        self.title = None
        self.ldjson = None
        self.in_body = False

    def _skip(self):
        return any(e[1] for e in self.stack)

    def _embed(self):
        for e in self.stack:
            if e[2] is not None:
                return e[2]
        return None

    def _emit(self, text):
        if self._skip():
            return
        emb = self._embed()
        if emb is not None:
            emb.append(text)
        elif self.in_body:
            self.seg["body"].append(text)
        for e in self.stack:
            if e[3] is not None:
                e[3][1].append(text)

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "body":
            self.in_body = True
        if tag == "meta":
            self._meta(a)
        if tag not in _INLINE:
            self._emit(" ")
        if tag in _VOID:
            return
        if tag == "title":
            self.title = []
        if tag == "script" and a.get("type", "").strip().lower() == "application/ld+json":
            self.ldjson = []
        emb = None
        if not self._skip() and self._embed() is None and any(
                c.startswith("embed-") for c in a.get("class", "").split()):
            emb = []
        quoted = None
        if tag in ("q", "blockquote") and not self._skip():
            quoted = ["embed" if (emb is not None or self._embed() is not None)
                      else "body", []]
            self.quoted.append(quoted)
        self.stack.append([tag, tag in _SKIP, emb, quoted])

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in _VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == "title" and self.title is not None:
            self.seg["title"].append("".join(self.title))
            self.title = None
        if tag == "script" and self.ldjson is not None:
            try:
                out = []
                _strings(json.loads("".join(self.ldjson)), out)
                self.seg["jsonld"].extend(out)
            except ValueError:
                pass            # jsonld_parse reports unparseable blocks
            self.ldjson = None
        if not any(e[0] == tag for e in self.stack):
            return
        while self.stack:
            e = self.stack.pop()
            if e[2] is not None:
                self.seg["embed"].append("".join(e[2]))
            if e[0] == tag:
                break
        if tag not in _INLINE:
            self._emit(" ")

    def handle_data(self, data):
        if self.title is not None:
            self.title.append(data)
        if self.ldjson is not None:
            self.ldjson.append(data)
        self._emit(data)

    def _meta(self, a):
        if "content" not in a:
            return
        prop = a.get("property", "").strip().lower()
        name = a.get("name", "").strip().lower()
        if prop == "og:image:alt":
            surf = "og_image"
        elif prop.startswith("og:"):
            surf = "og"
        elif prop.startswith("twitter:") or name.startswith("twitter:"):
            surf = "twitter"
        elif name:
            surf = "meta"
        else:
            return
        self.seg[surf].append(a["content"])

    def finish(self):
        self.close()
        while self.stack:
            e = self.stack.pop()
            if e[2] is not None:
                self.seg["embed"].append("".join(e[2]))
        if self.seg["body"]:
            self.seg["body"] = ["".join(self.seg["body"])]
        return self


def _strings(obj, out):
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            _strings(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _strings(v, out)


def _page_surfaces(path, rel):
    """surface -> [normalized segments], and [(surface, normalized quoted text)]."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    if rel == "llms.txt":
        return {"llms": [normalize(text)]}, []
    p = _Extractor()
    p.feed(text)
    p.finish()
    segs = {s: [normalize(t) for t in v] for s, v in p.seg.items() if v}
    quoted = [(s, normalize("".join(parts))) for s, parts in p.quoted]
    return segs, quoted


def _in_marks(seg, needle):
    """True when some occurrence of needle in seg has the nearest quote marks
    around it opening before and closing after (curly or straight)."""
    start = seg.find(needle)
    while start != -1:
        before, after = seg[:start], seg[start + len(needle):]
        if before.rfind("“") > before.rfind("”"):
            ro, rc = after.find("“"), after.find("”")
            if rc != -1 and (ro == -1 or rc < ro):
                return True
        if before.count('"') % 2 == 1 and '"' in after:
            return True
        start = seg.find(needle, start + 1)
    return False


def _is_quoted(needle, surf, segs, quoted):
    if any(_in_marks(s, needle) for s in segs.get(surf, [])):
        return True
    return any(qs == surf and needle in qt for qs, qt in quoted)


def check(ctx):
    records = validate_facts.load(ctx.data["facts_registry"])
    public = ctx.public_dir
    pages = {}
    for p in ctx.iter_html():
        pages[ctx.rel(p)] = p
    if (public / "llms.txt").is_file():
        pages["llms.txt"] = public / "llms.txt"
    cache = {}

    def surfaces_of(rel):
        if rel not in cache:
            cache[rel] = _page_surfaces(pages.get(rel, public / rel), rel)
        return cache[rel]

    findings = []
    for rec in records:
        if not isinstance(rec, dict):
            continue
        key = rec.get("key") if isinstance(rec.get("key"), str) else "?"
        claim = rec.get("claim")
        claim_n = normalize(claim) if isinstance(claim, str) and claim.strip() else None
        q = rec.get("quote") if isinstance(rec.get("quote"), dict) else {}
        qtext, mode = q.get("text"), q.get("mode")
        quote_n = normalize(qtext) if isinstance(qtext, str) and qtext.strip() else None

        listed = []
        for entry in rec.get("pages") if isinstance(rec.get("pages"), list) else []:
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                continue
            surfs = entry.get("surfaces")
            for s in surfs if isinstance(surfs, list) else []:
                if isinstance(s, str) and (entry["path"], s) not in listed:
                    listed.append((entry["path"], s))
        listed_set = set(listed)

        # (a) listed pair lacks the claim; (d) quote mode, listed pair unquoted
        for path, surf in listed:
            rel = Path(path).as_posix()
            if rel not in pages and not (public / rel).is_file():
                if claim_n is not None:
                    findings.append(ctx.finding(
                        rel, "%s: listed page file missing (surface %s)"
                        % (key, surf), claim))
                continue
            segs, quoted = surfaces_of(rel)
            if claim_n is not None and not any(claim_n in s for s in segs.get(surf, [])):
                findings.append(ctx.finding(
                    rel, "%s: claim absent from listed surface %s" % (key, surf),
                    claim))
            if mode == "quote" and quote_n is not None and \
                    not _is_quoted(quote_n, surf, segs, quoted):
                findings.append(ctx.finding(
                    rel, "%s: quote-mode quote.text not inside quotation marks "
                    "on surface %s" % (key, surf), qtext))

        # (b) claim on an unlisted pair; (c) paraphrase quote.text in quotes
        for rel in sorted(pages):
            segs, quoted = surfaces_of(rel)
            for surf in SURFACES:
                if claim_n is not None and (rel, surf) not in listed_set and \
                        any(claim_n in s for s in segs.get(surf, [])):
                    findings.append(ctx.finding(
                        rel, "%s: claim renders on unlisted surface %s"
                        % (key, surf), claim))
                if mode == "paraphrase" and quote_n is not None and \
                        _is_quoted(quote_n, surf, segs, quoted):
                    findings.append(ctx.finding(
                        rel, "%s: paraphrase-mode quote.text inside quotation "
                        "marks on surface %s" % (key, surf), qtext))
    return findings
