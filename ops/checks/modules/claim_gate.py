"""claim_gate -- adapter that runs canon ops/claim_gate/claim_gate.py.

Runs `claim_gate.py --config <data.config> --repo <site_root> --brief` in a
subprocess (sys.executable, PYTHONDONTWRITEBYTECODE=1, GIT_OPTIONAL_LOCKS=0).
claim_gate.py writes NOTHING unless --report is given (its _finish() writes
only args.report); this adapter never passes --report, so nothing lands in the
site. Exit 0 -> no findings. Exit 1 -> one Finding per blocking rule whose
SUMMARY row reads FAIL (--brief suppresses per-hit lines, so page is
"public/"). Exit 2 or anything else -> RuntimeError: the gate could not judge,
which the runner reports as a crash, never as a pass.

Option git_snapshot: claim_gate.py requires `git ls-files public/` to agree
with the working tree. The canary fixture is not its own git repo, so with
git_snapshot=true the site root is copied to a temp dir outside both repos,
`git init` + one local commit are made there, and the gate runs on the copy.
Real sites leave it false (they are git repos already).
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from checklib import CANON_ROOT, Finding

NAME = "claim_gate"
DESCRIPTION = ("Standing claim gate (canon ops/claim_gate); one finding per "
               "blocking rule that FAILs.")
REQUIRES = {
    "config": "claim gate config JSON; 'canon:ops/claim_gate/config/<site>.json', "
              "an absolute path, or a path relative to the site root",
}
OPTIONS = {"git_snapshot": False, "timeout_s": 1800}

GATE = CANON_ROOT / "ops" / "claim_gate" / "claim_gate.py"
SUMMARY_ROW = re.compile(
    r"^\s+(R\d+\w*)\s+(.+?)\s+RAW\s+(\d+)\s+ADJ\s+(\d+)\s+FAIL\s*$")


def _snapshot(src: Path, tmp: str) -> Path:
    dst = Path(tmp) / "site"
    shutil.copytree(src, dst, symlinks=True)
    g = ["git", "-c", "init.defaultBranch=main", "-c", "core.hooksPath=/dev/null",
         "-c", "commit.gpgsign=false", "-c", "user.name=canary",
         "-c", "user.email=canary@localhost"]
    for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "canary"]):
        subprocess.run(g + cmd, cwd=dst, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return dst


def check(ctx):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", GIT_OPTIONAL_LOCKS="0")
    with tempfile.TemporaryDirectory(prefix="k44_claim_gate_") as tmp:
        repo = _snapshot(ctx.site_root, tmp) if ctx.options["git_snapshot"] \
            else ctx.site_root
        p = subprocess.run(
            [sys.executable, str(GATE), "--config", str(ctx.data["config"]),
             "--repo", str(repo), "--brief"],
            cwd=tmp, env=env, capture_output=True, text=True,
            timeout=ctx.options["timeout_s"])
    lines = p.stdout.splitlines()
    if p.returncode == 0:
        return []
    if p.returncode != 1:
        why = [l.strip() for l in lines
               if re.search(r"ERROR|NOT RUN|CRASHED|TRAP:|MISMATCH", l)][:5]
        raise RuntimeError("claim_gate.py exit %d (could not judge): %s"
                           % (p.returncode, " / ".join(why) or p.stderr.strip()[-300:]))
    out = []
    for l in lines:
        m = SUMMARY_ROW.match(l)
        if m:
            rid, name, raw, adj = m.groups()
            out.append(Finding(NAME, "public/",
                               "claim gate %s %s: %s blocking finding(s); for "
                               "the hits run from the canon root: python3 "
                               "ops/claim_gate/claim_gate.py --config <config> "
                               "--repo <site>"
                               % (rid, name.strip(), adj), l.strip()))
    if not out:
        out.append(Finding(NAME, "public/", "claim gate exit 1 but no FAIL "
                           "row parsed from its SUMMARY", "CLAIM GATE: FAIL"))
    return out
