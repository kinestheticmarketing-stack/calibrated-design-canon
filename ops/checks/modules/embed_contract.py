"""embed_contract -- the static half of the calculator-embed behaviour contracts.

Source: DCI ops/embed_contract_check.js (four suites, run in local headless
Chrome via ops/cdp.js; not wired into any build today). This module ports the
parts of each suite that are decidable from the built bytes alone. Every
case table (pages, frames, button ids, authored defaults, verified heights,
lead-form counts) is site data and comes from the manifest literal key
`contract`; nothing site-specific is hardcoded here.

Ported (static):
  S1 bare load   -- the AUTHORED default state of each full page's controls
                    (checked radios/checkboxes, input value=, selected option)
                    equals the contract's defaults.
  S2 round trip  -- each frame has its calculate button and result container;
                    every CTA anchor literal (class calc-cta) in the frame
                    carries target="_blank" rel="noopener"; the frame source
                    contains the absolute deeplink base site_url + page; and
                    every value a frame control can emit (select options,
                    checkbox values, number min/max) is a value the full page
                    has a control for (a frame value the page cannot represent
                    is the static shape of defect 1, a deeplink the page
                    rejects).
  S3 lead path   -- #leadForm control / hidden / required counts (including
                    the hidden fields the page script injects when the tool
                    container exists), the honeypot present and unfocusable,
                    the quote anchor, thank-you, submit button and calculate
                    button present, and the POST endpoint marker in the source.
  S4 host embed  -- every published <iframe> snippet (entity-decoded) whose
                    src ends in a contract frame has height= and CSS height
                    both >= the height the browser check verified, and the
                    frame carries the attribution link that suite measures.

Dropped (need a browser or a server; stay in the site's JS check):
  S1 every query-string case (valid/partial/hostile/over-length/duplicate/
     case/whitespace deeplinks) and whether page script preserves defaults on
     a bare load -- needs JS execution.
  S2 clicking the frame CTA and asserting the page renders a result.
  S3 the populated calc_inputs/calc_output values after a click; the
     offsetParent computation (approximated statically, see _unfocusable).
  S4 the rendered clearance measurement at a 320px host (layout engine and a
     loopback HTTP server).
"""

import html as _html
import re
from html.parser import HTMLParser

NAME = "embed_contract"
DESCRIPTION = ("Static half of the calculator-embed contracts: authored "
               "defaults, frame->page value coverage and CTA attributes, lead "
               "form shape, published frame heights >= verified heights.")
REQUIRES = {
    "contract": "literal object: site_url, frames {frame: {page, button}}, "
                "host_heights {frame: px}, lead_pages {page: button}, "
                "lead_form {form_id, controls, hidden, required, honeypot, "
                "injected_hidden, tool_id, ids, endpoint_marker}, result_id, "
                "attrib_class, bare_defaults {page: {'#id'|'name': value}}",
}
LITERAL_KEYS = {"contract"}
OPTIONS = {}

_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
         "meta", "param", "source", "track", "wbr"}
_CONTROLS = ("input", "select", "textarea", "button")


class _Doc(HTMLParser):
    """Flat element list with ancestor chains; option elements attach to
    their select. Script/style bodies are CDATA, so JS string literals that
    look like markup never become elements."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.els = []
        self.stack = []
        self.select = None

    def handle_starttag(self, tag, attrs):
        a = {k: (v if v is not None else "") for k, v in attrs}
        el = {"tag": tag, "attrs": a, "anc": list(self.stack), "options": []}
        self.els.append(el)
        if tag == "option" and self.select is not None:
            self.select["options"].append(el)
        if tag == "select":
            self.select = el
        if tag not in _VOID:
            self.stack.append(el)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in _VOID and self.stack and self.stack[-1]["tag"] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag == "select":
            self.select = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                del self.stack[i:]
                break

    def by_id(self, i):
        for el in self.els:
            if el["attrs"].get("id") == i:
                return el
        return None

    def by_name(self, n):
        return [el for el in self.els if el["tag"] == "input"
                and el["attrs"].get("name") == n]


def _parse(src):
    d = _Doc()
    d.feed(src)
    d.close()
    return d


def _select_value(el):
    opts = el["options"]
    for o in opts:
        if "selected" in o["attrs"]:
            return o["attrs"].get("value", "")
    return opts[0]["attrs"].get("value", "") if opts else ""


def _emitted(el):
    """Values a frame control can send, or None if not enumerable."""
    if el["tag"] == "select":
        return [o["attrs"].get("value", "") for o in el["options"]]
    return None


def _unfocusable(el):
    """Static stand-in for (offsetParent === null || tabIndex === -1)."""
    a = el["attrs"]
    if a.get("tabindex", "").strip() == "-1" or a.get("type") == "hidden":
        return True
    for x in [el] + el["anc"]:
        st = re.sub(r"\s+", "", x["attrs"].get("style", "")).lower()
        if "hidden" in x["attrs"] or "display:none" in st:
            return True
    return False


def check(ctx):
    c = ctx.data["contract"]
    pub = ctx.public_dir
    out = []
    docs, srcs = {}, {}

    def load(name):
        if name not in docs:
            p = pub / name
            if not p.is_file():
                docs[name] = None
            else:
                srcs[name] = ctx.read_text(p)
                docs[name] = _parse(srcs[name])
        return docs[name]

    def f(page, msg, quote=""):
        out.append(ctx.finding(page, msg, quote))

    result_id = c.get("result_id", "calcOutput")

    # S1 -- authored defaults
    for page, want in sorted((c.get("bare_defaults") or {}).items()):
        d = load(page)
        if d is None:
            f(page, "S1: contract page missing from public/")
            continue
        for key, exp in want.items():
            if key.startswith("#"):
                el = d.by_id(key[1:])
                if el is None:
                    f(page, "S1: control %s missing" % key)
                    continue
                got = (_select_value(el) if el["tag"] == "select"
                       else el["attrs"].get("value", ""))
                if got != str(exp):
                    f(page, "S1: authored default of %s is %r, contract %r"
                      % (key, got, exp))
            else:
                els = d.by_name(key)
                if not els:
                    f(page, "S1: control name=%s missing" % key)
                    continue
                got = [e["attrs"].get("value", "") for e in els
                       if "checked" in e["attrs"]]
                expl = exp if isinstance(exp, list) else [exp]
                if got != [str(x) for x in expl]:
                    f(page, "S1: authored checked value(s) of name=%s are %r, "
                      "contract %r" % (key, got, expl))

    # S2 -- frame structure, CTA attributes, frame->page value coverage
    site_url = c.get("site_url", "")
    for frame, spec in sorted((c.get("frames") or {}).items()):
        d = load(frame)
        if d is None:
            f(frame, "S2: contract frame missing from public/")
            continue
        src = srcs[frame]
        page = spec["page"]
        for i in (spec["button"], result_id):
            if d.by_id(i) is None:
                f(frame, "S2: element #%s missing" % i)
        ctas = [m.group(0) for m in re.finditer(
            r"<a\b[^<>]*\bclass=\\?[\"']calc-cta\\?[\"'][^<>]*>", src)]
        if not ctas:
            f(frame, "S2: no calc-cta deeplink anchor in the frame source")
        for t in ctas:
            if not (re.search(r"target=\\?[\"']_blank", t)
                    and re.search(r"rel=\\?[\"']noopener", t)):
                f(frame, "S2: calc-cta anchor lacks target=_blank rel=noopener",
                  t)
        if site_url and (site_url + page) not in src:
            f(frame, "S2: frame never names the absolute deeplink base %s"
              % (site_url + page))
        pd = load(page)
        if pd is None:
            f(page, "S2: round-trip target page missing from public/")
            continue
        seen = set()
        tool = [e for e in d.els if e["tag"] in ("input", "select")
                and any(a["attrs"].get("id") == "calcTool" or
                        "calc-tool" in a["attrs"].get("class", "").split()
                        for a in e["anc"])]
        for el in tool:
            a = el["attrs"]
            key = a.get("id") if el["tag"] == "select" else (
                a.get("name") or a.get("id"))
            if not key:
                continue
            target = pd.by_id(key)
            group = pd.by_name(key)
            if target is None and not group:
                if key not in seen:
                    f(page, "S2: frame %s control %s has no counterpart on "
                      "the page" % (frame, key))
                seen.add(key)
                continue
            if target is not None and target["tag"] == "select":
                accepts = set(o["attrs"].get("value", "")
                              for o in target["options"])
            elif group and group[0]["attrs"].get("type") in ("radio",
                                                             "checkbox"):
                accepts = set(e["attrs"].get("value", "") for e in group)
            else:
                accepts = None  # free input (number/text)
            if el["tag"] == "input" and a.get("type") == "checkbox":
                vals = [a.get("value", "")]
            else:
                vals = _emitted(el)
            if accepts is not None and vals is not None:
                for v in vals:
                    if v not in accepts:
                        f(page, "S2: frame %s can emit %s=%r, which the page "
                          "has no control value for" % (frame, key, v))
            if a.get("type") == "number" and target is not None:
                ta = target["attrs"]
                for bound, worse in (("min", lambda fv, pv: fv < pv),
                                     ("max", lambda fv, pv: fv > pv)):
                    fv, pv = a.get(bound), ta.get(bound)
                    try:
                        if fv and pv and worse(float(fv), float(pv)):
                            f(page, "S2: frame %s %s %s=%s outside the page's "
                              "%s" % (frame, key, bound, fv, pv))
                    except ValueError:
                        pass

    # S3 -- lead path shape, nothing submitted
    lf = c.get("lead_form") or {}
    for page, button in sorted((c.get("lead_pages") or {}).items()):
        d = load(page)
        if d is None:
            f(page, "S3: lead page missing from public/")
            continue
        src = srcs[page]
        form = d.by_id(lf.get("form_id", "leadForm"))
        if form is None:
            f(page, "S3: no #%s" % lf.get("form_id", "leadForm"))
            continue
        ctl = [e for e in d.els if e["tag"] in _CONTROLS
               and any(x is form for x in e["anc"])]
        hidden = [e for e in ctl if e["attrs"].get("type") == "hidden"]
        required = [e for e in ctl if "required" in e["attrs"]]
        inj = list(lf.get("injected_hidden") or [])
        tool_id = lf.get("tool_id", "calcTool")
        if inj and d.by_id(tool_id) is not None and all(
                ("'%s'" % n) in src or ('"%s"' % n) in src for n in inj):
            n_inj = len(inj)
        else:
            n_inj = 0
        for label, got, key in (("controls", len(ctl) + n_inj, "controls"),
                                ("hidden", len(hidden) + n_inj, "hidden"),
                                ("required", len(required), "required")):
            if key in lf and got != lf[key]:
                f(page, "S3: lead form has %d %s (incl. %d injected), "
                  "contract %d" % (got, label, n_inj if key != "required"
                                   else 0, lf[key]))
        hp_name = lf.get("honeypot")
        if hp_name:
            hp = [e for e in ctl if e["attrs"].get("name") == hp_name]
            if not hp:
                f(page, "S3: honeypot %s missing" % hp_name)
            elif not _unfocusable(hp[0]):
                f(page, "S3: honeypot %s is focusable/visible" % hp_name)
        for i in list(lf.get("ids") or []) + [button]:
            if d.by_id(i) is None:
                f(page, "S3: element #%s missing" % i)
        marker = lf.get("endpoint_marker")
        if marker and marker not in src:
            f(page, "S3: POST endpoint marker %r not in the page" % marker)

    # S4 -- published heights vs the verified heights
    heights = c.get("host_heights") or {}
    attrib = c.get("attrib_class", "embed-attrib")
    for frame in sorted(heights):
        d = load(frame)
        if d is None:
            f(frame, "S4: contract frame missing from public/")
            continue
        if not any(e["tag"] == "a" and any(
                attrib in x["attrs"].get("class", "").split()
                for x in e["anc"]) for e in d.els):
            f(frame, "S4: no .%s a attribution link in the frame" % attrib)
    if heights:
        for p in ctx.iter_html():
            text = _html.unescape(ctx.read_text(p))
            for m in re.finditer(r"<iframe\b[^>]*>", text):
                tag = m.group(0)
                sm = re.search(r"\bsrc=[\"']([^\"']+)", tag)
                if not sm:
                    continue
                frame = sm.group(1).split("?")[0].split("#")[0]
                frame = frame.rstrip("/").rsplit("/", 1)[-1]
                if frame not in heights:
                    continue
                need = int(heights[frame])
                hm = re.search(r"\sheight=[\"']?(\d+)", tag)
                cm = re.search(r"[\"';\s]height:\s*(\d+)px", tag)
                for what, v in (("height=", hm and int(hm.group(1))),
                                ("CSS height", cm and int(cm.group(1)))):
                    if v is None:
                        f(p, "S4: published %s snippet has no %s" % (frame,
                                                                    what), tag)
                    elif v < need:
                        f(p, "S4: published %s %s %dpx is below the verified "
                          "%dpx" % (frame, what, v, need), tag)
    return out
