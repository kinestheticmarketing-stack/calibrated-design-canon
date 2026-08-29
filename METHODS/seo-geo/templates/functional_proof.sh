#!/usr/bin/env bash
# ops/functional_proof.sh — LAUNCH GATE. Proves the deployed site actually works.
#
# Usage: ops/functional_proof.sh <domain-or-base-url> <repo-path>
#   ops/functional_proof.sh denvercoloradoinsulation.com /Users/you/code/denvercoloradoinsulation.com
#   ops/functional_proof.sh http://127.0.0.1:8911        /Users/you/code/denvercoloradoinsulation.com
#
# Exits 0 ONLY if every check passes. Nonzero on ANY failure.
#
# Judge this gate by its EXIT CODE, never by reading its output, and never
# through a pipe: a pipeline's status is the LAST command's, so
# `functional_proof.sh ... | tail` reports tail's success and the failure sails
# through. Run it, then read $?.
#
# All parsing happens in the embedded python3 below, deliberately. An earlier
# pure-shell attempt at this gate reported a false "0/1 status 000" because a
# shell loop handed every URL to a single curl invocation. python3 + urllib +
# ThreadPoolExecutor fetches each URL individually and reports each status.
set -uo pipefail

domain="${1:?usage: functional_proof.sh <domain-or-base-url> <repo-path>}"
repo="${2:?usage: functional_proof.sh <domain-or-base-url> <repo-path>}"

[ -d "$repo" ] || { echo "FAIL: repo path is not a directory: $repo"; exit 2; }
command -v python3 >/dev/null 2>&1 || { echo "FAIL: python3 not on PATH"; exit 2; }

# node --check must run from INSIDE the repo: node's module resolution walks up
# from the file's directory, and a scratch file in /tmp resolves against the
# wrong tree (or none at all).
scratch="$repo/.functional_proof_tmp"
rm -rf "$scratch" && mkdir -p "$scratch" || { echo "FAIL: cannot create $scratch"; exit 2; }
trap 'rm -rf "$scratch"' EXIT

python3 - "$domain" "$repo" "$scratch" <<'PYEOF'
import json, os, re, shutil, subprocess, sys
import urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

RAW, REPO, SCRATCH = sys.argv[1], sys.argv[2], sys.argv[3]

# Accept a bare host (assume https) or a full base URL — the latter lets the
# negative control, and any local smoke run, point the gate at a throwaway
# server. Same convention as ops/live_token_check.sh.
BASE = RAW.rstrip("/") if RAW.startswith(("http://", "https://")) else "https://" + RAW.rstrip("/")
_sp = urllib.parse.urlsplit(BASE)
BASE_HOST = _sp.hostname or ""
APEX = BASE_HOST[4:] if BASE_HOST.startswith("www.") else BASE_HOST

_IP = re.compile(r"\A\d{1,3}(\.\d{1,3}){3}\Z")
LOCAL_MODE = BASE_HOST in {"localhost", "0.0.0.0", "::1"} or bool(_IP.match(BASE_HOST))

UA = "functional-proof/1.0 (launch-gate)"
TIMEOUT = 30
WORKERS = 12


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_strict = urllib.request.build_opener(_NoRedirect)   # surfaces 3xx as-is
_follow = urllib.request.build_opener()              # follows 3xx


def fetch(url, follow=False):
    """-> (status, headers dict, body bytes). status 0 == transport error."""
    opener = _follow if follow else _strict
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with opener.open(req, timeout=TIMEOUT) as r:
            return r.status, {k.lower(): v for k, v in r.headers.items()}, r.read()
    except urllib.error.HTTPError as e:
        try:
            body = e.read()
        except Exception:
            body = b""
        hdrs = {k.lower(): v for k, v in (e.headers or {}).items()}
        return e.code, hdrs, body
    except Exception as e:
        return 0, {"x-error": "%s: %s" % (type(e).__name__, e)}, b""


def text(b):
    return b.decode("utf-8", "replace")


# ---------------------------------------------------------------- reporting --
CHECKS = []   # (n, title, ok, note)


def record(n, title, ok, note=""):
    CHECKS.append((n, title, ok, note))
    print("%-5s [%d/7] %s%s" % ("PASS" if ok else "FAIL", n, title, ("  — " + note) if note else ""))
    sys.stdout.flush()


def detail(line):
    print("        " + line)


print("=" * 78)
print("FUNCTIONAL PROOF — launch gate")
print("  base : %s%s" % (BASE, "   [local base URL]" if LOCAL_MODE else ""))
print("  repo : %s" % REPO)
print("=" * 78)

# --------------------------------------------- CHECK 1: sitemap URLs all 200 --
sm_status, _, sm_body = fetch(BASE + "/sitemap.xml")
if sm_status != 200:
    record(1, "every sitemap URL returns 200", False, "sitemap.xml itself returned %d" % sm_status)
    print("\nABORT: no sitemap, nothing else can be proven.")
    print("RESULT: FAIL")
    sys.exit(1)

seen, LOCS = set(), []
for u in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", text(sm_body)):
    if u not in seen:
        seen.add(u)
        LOCS.append(u)

with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    PAGES = dict(zip(LOCS, ex.map(fetch, LOCS)))

bad = [(u, PAGES[u][0]) for u in LOCS if PAGES[u][0] != 200]
for u, st in bad[:25]:
    detail("HTTP %-3s %s" % (st or "ERR", u))
record(1, "every sitemap URL returns 200", not bad,
       "%d/%d URLs returned 200" % (len(LOCS) - len(bad), len(LOCS)))

# ------------------------------------------ CHECK 2: internal links resolve --
HREF = re.compile(r"""<a\b[^>]*?\bhref\s*=\s*("([^"]*)"|'([^']*)')""", re.I | re.S)


def normalise(href, page_url):
    """Resolve, drop off-host/non-http, strip #frag and ?query, / -> index.html,
    append .html when the last segment has no extension."""
    href = href.strip()
    if not href or href.startswith("#"):
        return None
    absu = urllib.parse.urljoin(page_url, href)
    sp = urllib.parse.urlsplit(absu)
    if sp.scheme not in ("http", "https"):
        return None
    if (sp.hostname or "") != BASE_HOST:
        return None
    path = sp.path or "/"
    if path.endswith("/"):
        path += "index.html"
    if "." not in path.rsplit("/", 1)[-1]:
        path += ".html"
    return urllib.parse.urlunsplit((sp.scheme, sp.netloc, path, "", ""))


targets = {}   # normalised target -> example source page
for page, (st, _, body) in PAGES.items():
    if st != 200:
        continue
    for m in HREF.finditer(text(body)):
        t = normalise(m.group(2) if m.group(2) is not None else m.group(3), page)
        if t:
            targets.setdefault(t, page)

known = {}
for u, (st, _, _) in PAGES.items():
    n = normalise(u, BASE + "/")
    if n:
        known[n] = st

todo = sorted(t for t in targets if t not in known)
if todo:
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for t, (st, _, _) in zip(todo, ex.map(lambda u: fetch(u, follow=True), todo)):
            known[t] = st

broken = sorted((t, known.get(t, 0)) for t in targets if known.get(t) != 200)
for t, st in broken[:25]:
    detail("HTTP %-3s %s   (linked from %s)" % (st or "ERR", t, targets[t]))
record(2, "every internal link resolves, zero 404s", not broken,
       "%d distinct internal targets, %d broken" % (len(targets), len(broken)))

# ----------------------------------------------- CHECK 3: calculators load --
TOOL_SLUG = re.compile(r"calculator|quiz|comparator|checker|payback|r-value", re.I)
SCRIPT = re.compile(r"<script\b([^>]*)>(.*?)</script>", re.I | re.S)
HAS_SRC = re.compile(r"\bsrc\s*=", re.I)
IS_DATA = re.compile(r"""\btype\s*=\s*["']?(application/(ld\+)?json|application/json)""", re.I)

# A tool page is not a slug match. `r-value-altitude-*` are educational pages
# whose slug contains "r-value"; counting them inflated the launch record from
# 14 calculators to 16 on the 2026-08-19 reference run. The structural test is
# what actually distinguishes them: a calculator carries its own input controls
# OUTSIDE the lead-capture form (the real ones carry 7 inputs + 3 selects; the
# educational pages carry zero). Slug narrows the candidates; controls decide.
FORM_BLOCK = re.compile(r"<form\b.*?</form>", re.I | re.S)
CONTROL = re.compile(r"<(input|select)\b", re.I)

def is_tool_page(url, body):
    if not TOOL_SLUG.search(urllib.parse.urlsplit(url).path):
        return False
    if body is None:
        return False
    outside = FORM_BLOCK.sub("", body)
    return bool(CONTROL.search(outside))

def _tool_body(u):
    st, _, body = PAGES.get(u, (0, {}, b""))
    return text(body) if st == 200 else None

tools = [u for u in LOCS if is_tool_page(u, _tool_body(u))]
NODE = shutil.which("node")
tool_fail, listener_report = [], []

if not NODE:
    for u in tools:
        detail("SKIP %s — `node` is not on PATH" % u)
    record(3, "every calculator loads, ships parseable JS, fires listeners", False,
           "SKIP: node unavailable — %d calculator pages UNVERIFIED. A skipped check "
           "is a hole in the gate, not a pass." % len(tools))
else:
    for i, u in enumerate(tools):
        st, _, body = PAGES.get(u, (0, {}, b""))
        slug = urllib.parse.urlsplit(u).path.lstrip("/") or "index.html"
        if st != 200:
            tool_fail.append((u, "HTTP %s" % (st or "ERR")))
            detail("FAIL %-52s HTTP %s" % (slug, st or "ERR"))
            continue
        page = text(body)
        bodies = [(a, s) for a, s in SCRIPT.findall(page)
                  if s.strip() and not HAS_SRC.search(a) and not IS_DATA.search(a)]
        errs = []
        for j, (_attrs, src) in enumerate(bodies):
            ok, msg = False, ""
            for ext in (".js", ".mjs"):           # CommonJS first, then ESM
                p = os.path.join(SCRATCH, "fp_%d_%d%s" % (i, j, ext))
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(src)
                r = subprocess.run([NODE, "--check", p], capture_output=True, text=True)
                if r.returncode == 0:
                    ok = True
                    break
                if not msg:
                    msg = (r.stderr or "").strip().splitlines()
                    msg = " | ".join(msg[:4]) if msg else "node --check exit %d" % r.returncode
            if not ok:
                errs.append("script #%d: %s" % (j + 1, msg))
        listeners = len(re.findall(r"addEventListener", page))
        if listeners == 0:
            errs.append("no addEventListener found — page is inert")
        listener_report.append((slug, len(bodies), listeners))
        if errs:
            tool_fail.append((u, "; ".join(errs)))
            detail("FAIL %-52s scripts=%-2d listeners=%-3d" % (slug, len(bodies), listeners))
            for e in errs:
                detail("       %s" % e)
        else:
            detail("ok   %-52s scripts=%-2d listeners=%-3d" % (slug, len(bodies), listeners))
    record(3, "every calculator loads, ships parseable JS, fires listeners", not tool_fail,
           "%d/%d calculator pages clean (listener counts printed above)"
           % (len(tools) - len(tool_fail), len(tools)))
    detail("NOTE: this proves the calculator PARSES and binds listeners. Actually")
    detail("      computing a figure from default inputs requires a real DOM —")
    detail("      that half is exercised by ops/browser_canary.js.")

# ------------------------------------------------- CHECK 4: forms render ----
FORM = re.compile(r"<form\b[^>]*>", re.I)
REQUIRED_FIELD = re.compile(r"<(input|select|textarea)\b[^>]*\brequired\b[^>]*>", re.I)
NAME_ATTR = re.compile(r"""\bname\s*=\s*["']([^"']+)["']""", re.I)

home = next((u for u in LOCS if urllib.parse.urlsplit(u).path in ("", "/", "/index.html")), BASE + "/")
contacts = [u for u in LOCS if "contact" in urllib.parse.urlsplit(u).path.lower()]
form_targets = [("homepage", home)] + [("contact", c) for c in contacts]
if not contacts:
    form_targets.append(("contact", BASE + "/contact.html"))

form_fail = []
for label, u in form_targets:
    st, _, body = PAGES.get(u, (None, None, None))
    if st is None:
        st, _, body = fetch(u)
    page = text(body or b"")
    if st != 200:
        form_fail.append((u, "HTTP %s" % (st or "ERR")))
        detail("FAIL %-10s %s  HTTP %s" % (label, u, st or "ERR"))
        continue
    forms = FORM.findall(page)
    req = REQUIRED_FIELD.findall(page)
    names = []
    for m in re.finditer(r"<(?:input|select|textarea)\b[^>]*\brequired\b[^>]*>", page, re.I):
        nm = NAME_ATTR.search(m.group(0))
        if nm:
            names.append(nm.group(1))
    if not forms:
        form_fail.append((u, "no <form> element"))
        detail("FAIL %-10s %s  — no <form> element" % (label, u))
    elif not req:
        form_fail.append((u, "<form> present but no required fields render"))
        detail("FAIL %-10s %s  — <form> present, zero required fields" % (label, u))
    else:
        detail("ok   %-10s %s  forms=%d required-fields=%d %s"
               % (label, u, len(forms), len(req), names or ""))

record(4, "every form renders with its required fields", not form_fail,
       "%d/%d form pages render" % (len(form_targets) - len(form_fail), len(form_targets)))

print()
print("!" * 78)
print("!!  NOT PROVEN BY THIS SCRIPT: the form submit -> DATABASE round trip.")
print("!!")
print("!!  This check proves only that the <form> and its required fields RENDER.")
print("!!  It deliberately does NOT submit: the gate must be safe to run over and")
print("!!  over, and a submitting gate would write junk rows on every run.")
print("!!")
print("!!  You cannot infer the round trip from the DOM. The backend returns a")
print("!!  SUCCESS response on its discard branches, so the on-page success state")
print("!!  is NOT evidence that a row was written. A green form here is consistent")
print("!!  with a silently discarded lead.")
print("!!")
print("!!  Run the round trip separately:   node ops/browser_canary.js")
print("!!  It drives real headless Chrome, submits, and then INDEPENDENTLY")
print("!!  re-queries Postgres for the row. That query is the only proof.")
print("!" * 78)
print()

# ---------------------------------------------- CHECK 5: JSON-LD parses -----
LDJSON = re.compile(r"""<script\b[^>]*\btype\s*=\s*["']application/ld\+json["'][^>]*>(.*?)</script>""",
                    re.I | re.S)
SCANNED = [u for u in LOCS if PAGES[u][0] == 200]   # only pages we actually got
ld_total, ld_bad = 0, []
for u in SCANNED:
    st, _, body = PAGES[u]
    for blk in LDJSON.findall(text(body)):
        ld_total += 1
        try:
            json.loads(blk)
        except Exception as e:
            ld_bad.append((u, str(e)))
for u, e in ld_bad[:25]:
    detail("%s — %s" % (u, e))
record(5, "every JSON-LD block parses", not ld_bad,
       "%d blocks across %d fetched pages, %d unparseable" % (ld_total, len(SCANNED), len(ld_bad)))

# ------------------------------------------ CHECK 6: no live placeholders ---
# Regex and exclusion rule lifted verbatim from ops/live_token_check.sh, which
# is already proven in production. The trailing filter drops CSS/JS declaration
# braces like "{color:" that would otherwise read as {token}.
TOKEN = re.compile(r"\{\{?[A-Za-z_][A-Za-z0-9_.]*\}?\}|%[A-Z_]{3,}%|__[A-Z_]{3,}__|AUTHORING_REQUIRED|PLACEHOLDER")
CSSISH = re.compile(r"\A\{[a-z-]+:")

tok_hits = []
for u in SCANNED:
    st, _, body = PAGES[u]
    hits = sorted({m for m in TOKEN.findall(text(body)) if not CSSISH.match(m)})
    if hits:
        tok_hits.append((u, hits))
for u, hits in tok_hits[:25]:
    detail("%s" % u)
    for h in hits[:10]:
        detail("    %s" % h)
record(6, "no unsubstituted placeholder token in the served bytes", not tok_hits,
       "%d/%d fetched pages clean" % (len(SCANNED) - len(tok_hits), len(SCANNED)))

# --------------------------------------------- CHECK 7: www 301s to apex ----
if LOCAL_MODE:
    detail("base URL is a local/IP host — there is no www vhost to redirect")
    record(7, "www 301s to apex (SKIPPED, local base URL)", True, "not applicable off production")
else:
    wst, whd, _ = fetch("https://www.%s/" % APEX)
    loc = whd.get("location", "")
    lhost = urllib.parse.urlsplit(urllib.parse.urljoin("https://www.%s/" % APEX, loc)).hostname or ""
    ok = wst == 301 and lhost == APEX
    detail("https://www.%s/ -> HTTP %s  Location: %s" % (APEX, wst or "ERR", loc or "(none)"))
    record(7, "www 301s to apex", ok,
           "status %s, redirect host %s (want 301 -> %s)" % (wst or "ERR", lhost or "(none)", APEX))

# ------------------------------------------------------------- summary ------
failed = [c for c in CHECKS if not c[2]]
print()
print("=" * 78)
print("SUMMARY  %s" % BASE)
for n, title, ok, note in CHECKS:
    print("  [%d] %-4s %s" % (n, "PASS" if ok else "FAIL", title))
print("-" * 78)
print("  sitemap URLs .... %d" % len(LOCS))
print("  internal targets  %d" % len(targets))
print("  calculators ..... %d" % len(tools))
print("  JSON-LD blocks .. %d" % ld_total)
print("  checks passed ... %d/%d" % (len(CHECKS) - len(failed), len(CHECKS)))
print("=" * 78)
if failed:
    print("RESULT: FAIL — %s" % ", ".join("check %d" % c[0] for c in failed))
    sys.exit(1)
print("RESULT: PASS — launch gate green")
sys.exit(0)
PYEOF
