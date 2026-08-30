#!/usr/bin/env bash
# 2d. Every-page-200. Wraps each property's EXISTING ops/live_token_check.sh
# rather than duplicating its sitemap-walk logic — that script already
# curl -sf's every sitemap URL (failing on non-2xx) as a side effect of
# checking for unsubstituted template tokens. It was a launch-time gate only,
# never scheduled recurringly; this adds that scheduling + alerting.
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/_mon_lib.sh"

for propline in "${PROPERTIES[@]}"; do
  prop=$(prop_field "$propline" 1)
  url=$(prop_field "$propline" 2)
  repo=$(prop_field "$propline" 3)

  out=$("$repo/ops/live_token_check.sh" "$url" 2>&1)
  rc=$?

  if [ "$rc" -ne 0 ]; then
    failing=$(echo "$out" | grep '^FAIL fetch:' | sed 's/^FAIL fetch: //' | tr '\n' ',' | sed 's/,$//')
    if [ -z "$failing" ]; then
      # live_token_check.sh failed for a reason other than a non-200 page
      # (e.g. an unsubstituted template token) -- not this check's concern,
      # but still worth a distinct alert so it doesn't look like a page-200
      # failure when it's actually a content defect.
      detail="live_token_check.sh failed on $prop for a reason other than a broken page (likely an unsubstituted template token survived to production) -- see: $out"
    else
      detail="the following URL(s) did not return 200 on $prop: $failing"
    fi
    if should_alert_failure "page200" "$prop"; then
      send_alert "$prop" "Page check failed on $prop" "$detail"
      record_failure_alert "page200" "$prop"
    fi
  else
    if should_alert_recovery "page200" "$prop"; then
      send_alert "$prop" "Page check recovered on $prop" "All sitemap pages on $prop are returning 200 again."
      clear_failure_state "page200" "$prop"
    fi
  fi
done
