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
  data.config       the site's .py check file (top-level literal assignments
                    PAIRS, STRIP_PATTERNS, THRESHOLD, SHINGLE_N, extracted with
                    ast.literal_eval; site code is never imported or executed)
                    or a JSON object with those keys.
Assignment names are options, so a site with different names can map them.
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
    "config": "file holding PAIRS, STRIP_PATTERNS, THRESHOLD, SHINGLE_N: a .py "
              "file (literal top-level assignments, read with ast.literal_eval) "
              "or a JSON object with those keys",
}
LITERAL_KEYS = {"peer_public"}
OPTIONS = {
    "pairs_name": "PAIRS",
    "strip_name": "STRIP_PATTERNS",
    "threshold_name": "THRESHOLD",
    "shingle_name": "SHINGLE_N",
}


def _git(root, *args):
    r = subprocess.run(["git", "-C", str(root), "rev-parse", *args],
                       capture_output=True, text=True, check=False)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def _resolve_peer(ctx, raw):
    """canon:/absolute via ctx.resolve. A relative path that stays inside the
    site's checkout resolves within it; one that leaves it resolves against
    the MAIN checkout root."""
    if not isinstance(raw, str) or not raw:
        raise ValueError("CONFIG ERROR: peer_public must be a non-empty path "
                         "string, got %r" % (raw,))
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
