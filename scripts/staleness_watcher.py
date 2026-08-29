#!/usr/bin/env python3
"""Citation staleness watcher — shared implementation for all three properties.

Registry schema (JSON, one file per site repo, e.g.
denvercoloradoinsulation.com/docs/citation-registry.json):

{
  "sources": [
    {
      "id": "IECC_2021_ADOPTION_DENVER",          # unique within the repo's registry
      "type": "adoption_state" | "document",       # see below
      "url": "https://...",
      "claim": "plain-language description of what this source is cited for",
      "repo": "denvercoloradoinsulation.com",
      "pages": ["ceiling-insulation-denver.html", ...],   # pages depending on it
      "retrieved": "2026-08-28",                    # YYYY-MM-DD, last verified
      "fingerprint": {
        "method": "anchor" | "regex",
        # anchor: extracts the text between start_anchor and end_anchor
        "start_anchor": "...", "end_anchor": "...",
        # regex: extracts group(1) if present, else the whole match
        "pattern": "...",
        "hash": "sha256:<hex>",                     # of the normalized extracted span
        "sample": "first ~200 chars of the extracted span, for human readability"
      },
      "notes": "free text, optional"
    }
  ]
}

type=document   — a specific page/PDF whose quoted text is cited (rebate amount,
                   a stat, a table value).
type=adoption_state — a jurisdiction's own code-adoption page, fingerprinted on
                   whatever text states the currently adopted code edition/year.
                   Registered because a citation can go stale WITHOUT any cited
                   document changing — the jurisdiction just adopts a new code.

Report-only. This script NEVER edits page content, generators, or the registry
itself (other than via the `seed` subcommand, which only computes and prints a
fingerprint for a human/future pass to paste into a registry entry — it does
not write any file).

Usage:
  python3 scripts/staleness_watcher.py check --registry PATH [--source ID]
  python3 scripts/staleness_watcher.py seed --url URL --method anchor \
      --start TEXT --end TEXT
  python3 scripts/staleness_watcher.py seed --url URL --method regex \
      --pattern PATTERN

Exit code on `check`: 0 if every source reported UNCHANGED, 1 if any source
reported CHANGED or UNREACHABLE (so a scheduler can alert on nonzero without
parsing output). `seed` always exits 0 on a successful fetch.
"""
import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0 Safari/537.36 "
    "CitationStalenessWatcher/1.0 (+calibrated-design-canon)"
)
FETCH_TIMEOUT = 20

# Below this many visible-text characters, treat the page as too sparse to
# trust — either a fetch went wrong or the page is a JS-rendered shell.
JS_SHELL_TEXT_FLOOR = 300
# Signature strings seen in real JS-shell responses (SPA root divs, no-JS
# notices, hydration payload markers). Presence alone isn't disqualifying —
# combined with sparse visible text, it is.
SPA_MARKERS = (
    'id="root"', 'id="app"', 'id="__next"',
    "you need to enable javascript", "__next_data__",
    "window.__initial_state__", "please enable javascript",
)


class FetchError(Exception):
    pass


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            status = resp.status
            body = resp.read()
    except urllib.error.HTTPError as e:
        raise FetchError(f"HTTP {e.code}") from e
    except urllib.error.URLError as e:
        raise FetchError(f"unreachable: {e.reason}") from e
    except TimeoutError as e:
        raise FetchError(f"timeout after {FETCH_TIMEOUT}s") from e
    if status != 200:
        raise FetchError(f"HTTP {status}")
    charset = "utf-8"
    ctype = resp.headers.get_content_charset()
    if ctype:
        charset = ctype
    try:
        return body.decode(charset, errors="replace")
    except LookupError:
        return body.decode("utf-8", errors="replace")


def strip_tags(html):
    html = re.sub(r"<script\b[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style\b[^>]*>.*?</style>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<[^>]+>", " ", html)
    return html


def normalize(text):
    text = strip_tags(text)
    text = re.sub(r"&nbsp;|&amp;|&lt;|&gt;|&quot;|&#39;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def looks_like_js_shell(html):
    visible = normalize(html)
    if len(visible) < JS_SHELL_TEXT_FLOOR:
        return True, f"visible text after stripping tags is only {len(visible)} chars (floor {JS_SHELL_TEXT_FLOOR})"
    lower = html.lower()
    marker_hits = [m for m in SPA_MARKERS if m in lower]
    if marker_hits and len(visible) < 1000:
        return True, f"SPA marker(s) {marker_hits} present with sparse visible text ({len(visible)} chars)"
    return False, None


def extract_span(html, fp):
    """Extract on NORMALIZED (tag-stripped) text, not raw HTML.

    Real pages routinely split a cited sentence mid-word with an inline tag
    (a <a>, <b>, <span> landing between two words of the quoted provision) --
    matching raw HTML makes every fingerprint brittle to incidental markup
    that has nothing to do with the content actually being cited.
    """
    text = normalize(html)
    method = fp["method"]
    if method == "anchor":
        start = fp["start_anchor"]
        idx = text.find(start)
        if idx == -1:
            return None
        content_start = idx + len(start)
        end = fp.get("end_anchor")
        if end:
            idx_end = text.find(end, content_start)
            if idx_end == -1:
                return None
            return text[content_start:idx_end]
        return text[content_start:content_start + 2000]
    elif method == "regex":
        m = re.search(fp["pattern"], text, re.IGNORECASE | re.DOTALL)
        if not m:
            return None
        return m.group(1) if m.groups() else m.group(0)
    else:
        raise ValueError(f"unknown fingerprint method: {method!r}")


def compute_hash(span):
    return "sha256:" + hashlib.sha256(normalize(span).encode("utf-8")).hexdigest()


def check_source(entry):
    sid = entry["id"]
    url = entry["url"]
    try:
        html = fetch(url)
    except FetchError as e:
        return {"id": sid, "status": "UNREACHABLE", "reason": str(e)}

    is_shell, shell_reason = looks_like_js_shell(html)
    if is_shell:
        return {"id": sid, "status": "UNREACHABLE", "reason": shell_reason}

    span = extract_span(html, entry["fingerprint"])
    if span is None:
        return {
            "id": sid,
            "status": "CHANGED",
            "reason": "fingerprint anchor/pattern no longer found on the page "
                      "-- provision likely reworded, moved, or removed",
        }

    current_hash = compute_hash(span)
    registered_hash = entry["fingerprint"]["hash"]
    if current_hash == registered_hash:
        return {"id": sid, "status": "UNCHANGED"}
    return {
        "id": sid,
        "status": "CHANGED",
        "reason": "fingerprint hash mismatch",
        "old_hash": registered_hash,
        "new_hash": current_hash,
        "new_sample": normalize(span)[:200],
    }


def cmd_check(args):
    with open(args.registry) as f:
        registry = json.load(f)
    sources = registry.get("sources", [])
    if args.source:
        sources = [s for s in sources if s["id"] == args.source]
        if not sources:
            print(f"no source with id {args.source!r} in {args.registry}", file=sys.stderr)
            return 2

    any_bad = False
    for entry in sources:
        result = check_source(entry)
        any_bad = any_bad or result["status"] != "UNCHANGED"
        line = f"{result['status']:<12} {result['id']}"
        if result["status"] != "UNCHANGED":
            line += f"  -- {result.get('reason', '')}"
        print(line)
        if args.verbose and result["status"] == "CHANGED" and "new_sample" in result:
            print(f"             new sample: {result['new_sample']!r}")
            print(f"             old hash:   {result['old_hash']}")
            print(f"             new hash:   {result['new_hash']}")
    return 1 if any_bad else 0


def cmd_seed(args):
    fp = {"method": args.method}
    if args.method == "anchor":
        if not args.start:
            print("--start is required for --method anchor", file=sys.stderr)
            return 2
        fp["start_anchor"] = args.start
        if args.end:
            fp["end_anchor"] = args.end
    elif args.method == "regex":
        if not args.pattern:
            print("--pattern is required for --method regex", file=sys.stderr)
            return 2
        fp["pattern"] = args.pattern

    try:
        html = fetch(args.url)
    except FetchError as e:
        print(f"UNREACHABLE: {e}", file=sys.stderr)
        return 1

    is_shell, shell_reason = looks_like_js_shell(html)
    if is_shell:
        print(f"UNREACHABLE (JS shell): {shell_reason}", file=sys.stderr)
        return 1

    span = extract_span(html, fp)
    if span is None:
        print("anchor/pattern not found on this page -- refine --start/--end/--pattern", file=sys.stderr)
        return 1

    fp["hash"] = compute_hash(span)
    fp["sample"] = normalize(span)[:200]
    print(json.dumps(fp, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="run the watcher against a registry file")
    p_check.add_argument("--registry", required=True)
    p_check.add_argument("--source", help="check only this source id")
    p_check.add_argument("--verbose", action="store_true")
    p_check.set_defaults(func=cmd_check)

    p_seed = sub.add_parser("seed", help="fetch a URL and print a fingerprint block to paste into a registry entry")
    p_seed.add_argument("--url", required=True)
    p_seed.add_argument("--method", required=True, choices=["anchor", "regex"])
    p_seed.add_argument("--start", help="anchor: text marking the start of the span")
    p_seed.add_argument("--end", help="anchor: text marking the end of the span (optional; defaults to a 2000-char window)")
    p_seed.add_argument("--pattern", help="regex: pattern to search for (group 1 if present, else full match)")
    p_seed.set_defaults(func=cmd_seed)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
