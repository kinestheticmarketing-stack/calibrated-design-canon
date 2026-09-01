#!/usr/bin/env bash
# 2a. Deploy drift: compares live index.js and public/ against the local
# repo (which R2 must run from, since only the Mac has the git checkouts).
# Real file comparison via scp+cmp — never $(curl ...), which strips
# trailing newlines and produced a false mismatch in an earlier incident.
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/_mon_lib.sh"

if ! check_local_connectivity; then
  echo "$(date -Iseconds) [deploy_drift_check] SKIPPED -- local connectivity check failed, cannot trust results this run" >&2
  exit 0
fi

for propline in "${PROPERTIES[@]}"; do
  prop=$(prop_field "$propline" 1)
  repo=$(prop_field "$propline" 3)
  backend=$(prop_field "$propline" 4)
  tmp=$(mktemp -d)
  diffs=()

  # index.js
  scp -q "root@74.208.181.10:${backend}/index.js" "$tmp/index.js.live" 2>/dev/null
  if [ -f "$tmp/index.js.live" ]; then
    if ! cmp -s "$tmp/index.js.live" "$repo/index.js"; then
      diffs+=("index.js")
    fi
  else
    diffs+=("index.js (could not fetch live copy)")
  fi

  # public/ — compare every file that exists in the repo's public dir
  mkdir -p "$tmp/public_live"
  scp -rq "root@74.208.181.10:${backend}/public/." "$tmp/public_live/" 2>/dev/null
  while IFS= read -r -d '' f; do
    rel="${f#"$repo"/public/}"
    if [ ! -f "$tmp/public_live/$rel" ]; then
      diffs+=("public/$rel (missing live)")
    elif ! cmp -s "$f" "$tmp/public_live/$rel"; then
      diffs+=("public/$rel")
    fi
  done < <(find "$repo/public" -type f -print0)

  rm -rf "$tmp"

  if [ "${#diffs[@]}" -gt 0 ]; then
    handle_check_result "deploy_drift" "$prop" 1 \
      "Deploy drift on $prop: live does not match repo" \
      "The following file(s) differ between what's deployed and what's in the repo for $prop: ${diffs[*]}. This usually means a commit was made but never deployed — the live site is running older or different code than what's checked in." \
      "" ""
  else
    handle_check_result "deploy_drift" "$prop" 0 "" "" \
      "Deploy drift on $prop: resolved" \
      "Live now matches the repo again for $prop."
  fi
done
