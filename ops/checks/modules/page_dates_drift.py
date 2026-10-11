"""page_dates_drift -- the site's published "Last updated" map disagrees with git.

Source: LGM _postbuild_check.py:check_page_dates -> _derive_page_dates.py --check.

Port of `_derive_page_dates.py --check`. The derivation is NOT reimplemented:
like the site script, this module loads canon's own
ops/claim_gate/claim_gate.py and calls GitFacts.last_visible_text_change, the
exact method claim gate R8 part (d) reads, so the published date and the gate's
measurement cannot drift apart. Canon code only; no site code is imported.

Site-specific values are data/options:
  data.shared        the .py file holding the date map (LGM _shared_components.py)
  options.map_name   the assignment name (default PAGE_MODIFIED_ISO), read with
                     ast.literal_eval of that one assignment (no import/exec)
  options.cap        GitFacts commit cap (40, the same cap R8 uses)
  options.recursive  False = public/*.html only, as the site script lists it

Semantics, as the site's --check: keys = map keys UNION derived filenames;
a key whose map value != derived value is one finding (STALE). A page with no
visible-text change in the examined window derives None and therefore counts
as stale if the map holds a value, exactly as the site script does.

Git history unavailable (not a repo, git missing) -> RuntimeError: the module
could not judge (the site script exits 2 there too).

Option git_snapshot (canary only, same pattern as claim_gate): copy site_root to
a temp dir outside both repos, `git init`, one local commit with a fixed
committer date (options.snapshot_date), and measure the copy. Real sites leave
it false.
"""

import ast
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from checklib import CANON_ROOT

NAME = "page_dates_drift"
DESCRIPTION = ("Published page-date map (e.g. PAGE_MODIFIED_ISO) disagrees with "
               "git's last visible-text change per page (canon GitFacts).")
REQUIRES = {
    "shared": "the site .py file holding the page-date map assignment "
              "(LGM: _shared_components.py)",
}
OPTIONS = {
    "map_name": "PAGE_MODIFIED_ISO",
    "cap": 40,
    "recursive": False,
    "git_snapshot": False,
    "snapshot_date": "2000-01-02T12:00:00+00:00",
}

GATE = CANON_ROOT / "ops" / "claim_gate" / "claim_gate.py"


def _load_gate():
    mod = sys.modules.get("claim_gate")
    if mod is not None and getattr(mod, "__file__", None) and \
            Path(mod.__file__).resolve() == GATE.resolve():
        return mod
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("claim_gate", str(GATE))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["claim_gate"] = mod
    spec.loader.exec_module(mod)
    return mod


def _read_map(path, name):
    tree = ast.parse(Path(path).read_text(encoding="utf-8"), filename=str(path))
    found = None
    for node in tree.body:
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
        if any(isinstance(t, ast.Name) and t.id == name for t in targets):
            found = node.value
    if found is None:
        raise RuntimeError("%s assignment not found in %s" % (name, path))
    m = ast.literal_eval(found)
    if not isinstance(m, dict):
        raise RuntimeError("%s in %s is not a dict" % (name, path))
    return {str(k): (None if v is None else str(v)) for k, v in m.items()}


def _snapshot(src, tmp, date):
    dst = Path(tmp) / "site"
    shutil.copytree(src, dst, symlinks=True)
    g = ["git", "-c", "init.defaultBranch=main", "-c", "core.hooksPath=/dev/null",
         "-c", "commit.gpgsign=false", "-c", "user.name=canary",
         "-c", "user.email=canary@localhost"]
    env = dict(os.environ, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "canary"]):
        subprocess.run(g + cmd, cwd=dst, check=True, env=env,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return dst


def _derive(gate, repo, public_rel, rels_html, cap):
    gf = gate.GitFacts(repo=str(repo), cap=cap)
    gf.load(str(repo), rels_html)
    if not gf.available:
        raise RuntimeError("git history unavailable at site root")
    out = {}
    try:
        for rel in rels_html:
            out[rel[len(public_rel) + 1:]] = gf.last_visible_text_change(rel)
    finally:
        gf.close()
    return out, sorted(gf.capped)


def check(ctx):
    opts = ctx.options
    public_rel = ctx.public_dir.resolve().relative_to(
        ctx.site_root.resolve()).as_posix()
    if public_rel != "public":
        # GitFacts.load logs `-- public/` (hardcoded in canon); anything else
        # would derive None everywhere and report noise, not drift.
        raise RuntimeError("page_dates_drift requires public_dir 'public' "
                           "(canon GitFacts.load reads public/ only); got %r"
                           % public_rel)
    got = _read_map(ctx.data["shared"], opts["map_name"])
    gate = _load_gate()
    env_keep = os.environ.get("GIT_OPTIONAL_LOCKS")
    os.environ["GIT_OPTIONAL_LOCKS"] = "0"
    try:
        with tempfile.TemporaryDirectory(prefix="k44_page_dates_") as tmp:
            repo = (_snapshot(ctx.site_root, tmp, opts["snapshot_date"])
                    if opts["git_snapshot"] else ctx.site_root)
            pub = Path(repo) / public_rel
            files = sorted(pub.rglob("*.html") if opts["recursive"]
                           else pub.glob("*.html"))
            rels = [public_rel + "/" + p.relative_to(pub).as_posix()
                    for p in files if p.is_file()]
            derived, _capped = _derive(gate, repo, public_rel, rels,
                                       int(opts["cap"]))
    finally:
        if env_keep is None:
            os.environ.pop("GIT_OPTIONAL_LOCKS", None)
        else:
            os.environ["GIT_OPTIONAL_LOCKS"] = env_keep
    findings = []
    for k in sorted(set(got) | set(derived)):
        if got.get(k) != derived.get(k):
            # page label relative to public/; a map key with no page -> map file
            page = k if k in derived else ctx.rel(ctx.data["shared"])
            findings.append(ctx.finding(
                page,
                "STALE: %s map=%s git=%s (re-run the site's page-date "
                "derivation with --write after committing)"
                % (opts["map_name"], got.get(k), derived.get(k)),
                "%s map=%s git=%s" % (k, got.get(k), derived.get(k))))
    return findings
