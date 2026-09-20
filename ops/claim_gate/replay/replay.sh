#!/usr/bin/env bash
# Git-replay defect score. Committed so the verification command in
# GATE_SCORE_RERUN_2026-09-19.md can actually be run: an earlier revision of
# that document cited score.py / score_base.py, which existed in no commit.
#
#   ops/claim_gate/replay/prepare.sh   builds $REPLAY_CANON from a canon SHA
#   ops/claim_gate/replay/replay.sh    runs all 20 pre-fix trees
#   ops/claim_gate/replay/score.py     scores the 25 defect instances
#
# Original method: One detached worktree per pre-fix SHA in the scratch
# dir, --today set to the fixing commit's date, canon = the scratch copy whose
# only difference is min_artifacts/expected_html = 10 (both are floors).
set -uo pipefail
export PYTHONDONTWRITEBYTECODE=1
S="${REPLAY_SCRATCH:-/tmp/claim-gate-replay}"
CANON="${REPLAY_CANON:-$S/canon}"
WT=$S/wt
OUT=$S/replay
mkdir -p "$WT" "$OUT"

declare -a ROWS=(
  "dci|130921c|2026-09-07"
  "dci|f08bb9f|2026-09-07"
  "dci|2a59a97|2026-09-07"
  "dci|169bb3c|2026-09-10"
  "dci|58c44eb|2026-09-11"
  "dci|bcb64a3|2026-09-07"
  "dci|dd88de3|2026-09-07"
  "dci|b5635c9|2026-09-07"
  "dci|d1b6078|2026-09-08"
  "dci|4cf7a52|2026-08-24"
  "dci|539670e|2026-09-10"
  "dci|cb675ab|2026-09-02"
  "lgm|8b0f1a9|2026-09-06"
  "lgm|a2ba5a6|2026-09-07"
  "lgm|604d052|2026-09-10"
  "lgm|2563a56|2026-09-07"
  "gci|e912eee|2026-09-08"
  "gci|236c464|2026-09-10"
  "gci|e994484|2026-09-10"
  "gci|12dfcbf|2026-09-09"
)

repo_path() {
  case "$1" in
    dci) echo "$HOME/code/denvercoloradoinsulation.com" ;;
    lgm) echo "$HOME/code/longmontcoloradoinsulation.com" ;;
    gci) echo "$HOME/code/greeleycoloradoinsulation.com" ;;
  esac
}

for row in "${ROWS[@]}"; do
  IFS='|' read -r key sha today <<< "$row"
  src="$(repo_path "$key")"
  wt="$WT/$key-$sha"
  if [ ! -d "$wt" ]; then
    git -C "$src" worktree add --detach "$wt" "$sha" >/dev/null 2>&1 \
      || { echo "$key-$sha WORKTREE FAILED"; continue; }
  fi
  python3 "$CANON/ops/claim_gate/claim_gate.py" \
    --config "$CANON/ops/claim_gate/config/$key.json" \
    --repo "$wt" --today "$today" \
    > "$OUT/$key-$sha.txt" 2>&1
  echo "$key-$sha exit=$?  today=$today"
done
