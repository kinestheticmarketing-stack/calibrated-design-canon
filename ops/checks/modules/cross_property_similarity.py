"""cross_property_similarity -- a page that copies its counterpart on a peer
property. Source: GCI _similarity_check.py:main (GCI only; no build runs it).

For each (local page, peer page, label) pair: strip the shared chrome
(STRIP_PATTERNS), take the remaining text lowercased and normalised, build the
set of N-word shingles and compute Jaccard similarity. PASS is strictly below
THRESHOLD. A missing local or peer page is a finding (the site check exits 1
on LOCAL MISSING / CONTROL MISSING too).

Every site-specific value is read from the site by declared paths:
  data.peer_public  the peer property's built public dir (read only). A
                    relative path that stays inside the site's checkout
                    resolves within it; one that leaves it resolves against
                    the MAIN checkout root (parent of git --git-common-dir),
                    so it works from a git worktree; absolute and canon:
                    values are used as given.
  data.peer_publics OPTIONAL list of further peer public dirs, each resolved
                    exactly like peer_public. Read only when the option
                    all_peers is True.
  data.config       the site's .py check file (top-level literal assignments
                    PAIRS, STRIP_PATTERNS, THRESHOLD, SHINGLE_N, extracted with
                    ast.literal_eval; site code is never imported or executed)
                    or a JSON object with those keys.
Assignment names are options, so a site with different names can map them.

Option all_peers (default False):
  False  only peer_public is compared; peer_publics is ignored and output is
         exactly the single-peer form.
  True   every pair is compared against peer_public and each peer_publics
         entry (deduplicated by resolved path, order preserved; peer_publics
         absent means peer_public only). Each CONTROL MISSING / Jaccard
         finding names the peer (its manifest path string).
"""

import ast
import html
import json
import re
import subprocess
from pathlib import Path

NAME = "cross_property_similarity"
DESCRIPTION = ("Shingle-Jaccard similarity of each listed page against its "
               "peer-property counterpart must stay below the site threshold.")
REQUIRES = {
    "peer_public": "the peer property's built public dir; absolute, canon:, "
                   "or relative: a relative path that stays inside the site's "
                   "checkout resolves within it; one that leaves it resolves "
                   "against the MAIN checkout root; read only",
    "peer_publics": "OPTIONAL list of further peer public dirs, each resolved "
                    "like peer_public; compared only when option all_peers "
                    "is True",
    "config": "file holding PAIRS, STRIP_PATTERNS, THRESHOLD, SHINGLE_N: a .py "
              "file (literal top-level assignments, read with ast.literal_eval) "
              "or a JSON object with those keys",
}
LITERAL_KEYS = {"peer_public", "peer_publics"}
OPTIONAL_KEYS = {"peer_publics"}
OPTIONS = {
    "all_peers": False,
    "pairs_name": "PAIRS",
    "strip_name": "STRIP_PATTERNS",
    "threshold_name": "THRESHOLD",
    "shingle_name": "SHINGLE_N",
}


def _git(root, *args):
    r = subprocess.run(["git", "-C", str(root), "rev-parse", *args],
                       capture_output=True, text=True, check=False)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def _resolve_peer(ctx, raw, key="peer_public"):
    """canon:/absolute via ctx.resolve. A relative path that stays inside the
    site's checkout resolves within it; one that leaves it resolves against
    the MAIN checkout root."""
    if not isinstance(raw, str) or not raw:
        raise ValueError("CONFIG ERROR: %s must be a non-empty path "
                         "string, got %r" % (key, raw))
    if raw.startswith("canon:") or Path(raw).expanduser().is_absolute():
        return ctx.resolve(raw)
    site = Path(ctx.site_root).resolve()
    rel = Path(raw).expanduser()
    top = _git(site, "--show-toplevel")
    common = _git(site, "--path-format=absolute", "--git-common-dir")
    if top and common:
        top = Path(top).resolve()
        candidate = (site / rel).resolve()
        if candidate.is_relative_to(top):
            return candidate
        base = Path(common).parent / site.relative_to(top)
        return (base / rel).resolve()
    return (site / rel).resolve()


def _load_config(path, names):
    if str(path).endswith(".json"):
        obj = json.loads(Path(path).read_text(encoding="utf-8"))
        return {k: obj[v] for k, v in names.items()}
    tree = ast.parse(Path(path).read_text(encoding="utf-8"), filename=str(path))
    found = {}
    for node in tree.body:
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
        for t in targets:
            if isinstance(t, ast.Name):
                for k, v in names.items():
                    if t.id == v:
                        found[k] = ast.literal_eval(node.value)
    missing = [names[k] for k in names if k not in found]
    if missing:
        raise ValueError("%s: no literal assignment(s) %s" % (path, ", ".join(missing)))
    return found


def _text(path, strip):
    s = Path(path).read_text(encoding="utf-8")
    for pat in strip:
        s = re.sub(pat, " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = s.lower()
    s = re.sub(r"[^a-z0-9$%. ]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _shingles(text, n):
    w = text.split()
    return {" ".join(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}


def _jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def check(ctx):
    o = ctx.options
    cfg = _load_config(ctx.data["config"], {
        "pairs": o["pairs_name"], "strip": o["strip_name"],
        "threshold": o["threshold_name"], "n": o["shingle_name"]})
    pairs, strip = cfg["pairs"], cfg["strip"]
    threshold, n = float(cfg["threshold"]), int(cfg["n"])
    if not pairs:
        raise ValueError("config PAIRS is empty; nothing to judge")
    raw = ctx.data["peer_public"]
    peer = _resolve_peer(ctx, raw)
    if not peer.is_dir():
        raise ValueError("CONFIG ERROR: peer_public %r resolves to %s, which "
                         "is not an existing directory" % (raw, peer))
    if not isinstance(o.get("all_peers"), bool):
        raise ValueError("CONFIG ERROR: option all_peers must be true or false, "
                         "got %r" % (o.get("all_peers"),))
    if o["all_peers"]:
        return _check_all(ctx, pairs, strip, threshold, n, raw, peer)
    findings = []
    for local, control, label in pairs:
        lp, cp = ctx.public_dir / local, peer / control
        if not lp.is_file():
            findings.append(ctx.finding(local, "LOCAL MISSING (%s)" % label, local))
            continue
        if not cp.is_file():
            findings.append(ctx.finding(local, "CONTROL MISSING (%s): peer %s"
                                        % (label, control), control))
            continue
        score = _jaccard(_shingles(_text(lp, strip), n),
                         _shingles(_text(cp, strip), n))
        if score >= threshold:
            findings.append(ctx.finding(
                lp, "Jaccard %.4f >= %.2f vs peer %s (%s)"
                % (score, threshold, control, label),
                "%s vs %s: %.4f" % (local, control, score)))
    return findings


def _check_all(ctx, pairs, strip, threshold, n, raw, peer):
    """all_peers path: peer_public plus every peer_publics entry."""
    extra = ctx.data.get("peer_publics")
    if extra is None:
        extra = []
    if not isinstance(extra, list):
        raise ValueError("CONFIG ERROR: peer_publics must be a list of path "
                         "strings, got %r" % (extra,))
    peers, seen = [(raw, peer)], {peer}
    for r in extra:
        p = _resolve_peer(ctx, r, "peer_publics entry")
        if not p.is_dir():
            raise ValueError("CONFIG ERROR: peer_publics entry %r resolves to "
                             "%s, which is not an existing directory" % (r, p))
        if p not in seen:
            seen.add(p)
            peers.append((r, p))
    findings = []
    for local, control, label in pairs:
        lp = ctx.public_dir / local
        if not lp.is_file():
            findings.append(ctx.finding(local, "LOCAL MISSING (%s)" % label, local))
            continue
        local_sh = _shingles(_text(lp, strip), n)
        for pname, pdir in peers:
            cp = pdir / control
            if not cp.is_file():
                findings.append(ctx.finding(local, "CONTROL MISSING (%s): peer "
                                            "%s %s" % (label, pname, control),
                                            control))
                continue
            score = _jaccard(local_sh, _shingles(_text(cp, strip), n))
            if score >= threshold:
                findings.append(ctx.finding(
                    lp, "Jaccard %.4f >= %.2f vs peer %s %s (%s)"
                    % (score, threshold, pname, control, label),
                    "%s vs %s %s: %.4f" % (local, pname, control, score)))
    return findings
