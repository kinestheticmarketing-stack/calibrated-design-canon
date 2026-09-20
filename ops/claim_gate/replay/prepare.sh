#!/usr/bin/env bash
# Build the scratch canon the replay runs against.
#
# The ONLY difference from the canon SHA given is min_artifacts /
# expected_html forced to 10 on all three configs. Both are FLOORS, so the
# empty-corpus trap is preserved while historical trees -- which carry fewer
# artifacts than today's -- can run at all. Same override the 2026-09-17 and
# 2026-09-18 scores used, recorded in both.
#
#   ./prepare.sh              # scratch canon from the working tree
#   ./prepare.sh 9dc1277      # scratch canon from a SHA, for a before/after
set -euo pipefail
SHA="${1:-}"
S="${REPLAY_SCRATCH:-/tmp/claim-gate-replay}"
CANON="${REPLAY_CANON:-$S/canon}"
SRC="$(cd "$(dirname "$0")/../../.." && pwd)"

# $SRC is the REAL canon repo. The happy path below already removes the
# scratch worktree, but `set -e` means any failure between `worktree add` and
# that removal -- a failed `cp -R`, a Ctrl-C -- left the registration behind
# in canon, invisible to `git status --porcelain`. The trap closes that
# window. Only the path this run added is touched; canon's lane worktrees
# under ~/code/canon-wt/ are never candidates.
PREPARE_WT=""
_prepare_cleanup() {
  status=$?
  trap - EXIT INT TERM
  set +e  # a cleanup failure must never mask the real exit code
  if [ -n "$PREPARE_WT" ]; then
    if ! git -C "$SRC" worktree remove --force "$PREPARE_WT" >/dev/null 2>&1; then
      if [ -e "$PREPARE_WT" ]; then
        rm -rf "$PREPARE_WT"
      fi
      git -C "$SRC" worktree prune >/dev/null 2>&1
    fi
    PREPARE_WT=""
  fi
  exit "$status"
}
trap _prepare_cleanup EXIT INT TERM

rm -rf "$CANON"; mkdir -p "$CANON/ops"
if [ -n "$SHA" ]; then
  WT="$S/_canon_wt_$SHA"
  # Record before the add so an interrupt mid-add is still cleaned up.
  PREPARE_WT="$WT"
  git -C "$SRC" worktree add --detach "$WT" "$SHA" >/dev/null 2>&1 || true
  cp -R "$WT/ops/claim_gate" "$CANON/ops/claim_gate"
  git -C "$SRC" worktree remove --force "$WT" >/dev/null 2>&1 || true
  PREPARE_WT=""
else
  cp -R "$SRC/ops/claim_gate" "$CANON/ops/claim_gate"
fi
rm -rf "$CANON/ops/claim_gate/__pycache__"
python3 - "$CANON" <<'PY'
import io, json, os, sys
for k in ("dci", "lgm", "gci"):
    p = os.path.join(sys.argv[1], "ops/claim_gate/config/%s.json" % k)
    d = json.load(io.open(p, encoding="utf-8"))
    d["min_artifacts"] = 10
    d["expected_html"] = 10
    io.open(p, "w", encoding="utf-8").write(
        json.dumps(d, indent=2, ensure_ascii=False) + "\n")
print("scratch canon ready at", sys.argv[1])
PY
