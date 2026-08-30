#!/usr/bin/env bash
# 2b. Uptime: homepage returns 200. A timeout/connection failure counts as
# a failure too, not a silent pass — curl itself is time-bounded.
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/_mon_lib.sh"

for propline in "${PROPERTIES[@]}"; do
  prop=$(prop_field "$propline" 1)
  url=$(prop_field "$propline" 2)

  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 --connect-timeout 10 "$url" 2>/dev/null)
  status=$?

  if [ "$status" -ne 0 ] || [ "$code" != "200" ]; then
    if [ "$status" -ne 0 ]; then
      detail="the site did not respond within the timeout (connection failed or timed out)"
    else
      detail="the homepage returned HTTP $code instead of 200"
    fi
    if should_alert_failure "uptime" "$prop"; then
      send_alert "$prop" "Uptime check failed: $prop is not responding normally" "$prop's homepage check failed: $detail. The site may be down or unreachable."
      record_failure_alert "uptime" "$prop"
    fi
  else
    if should_alert_recovery "uptime" "$prop"; then
      send_alert "$prop" "Uptime recovered: $prop is back up" "$prop's homepage is responding with 200 again."
      clear_failure_state "uptime" "$prop"
    fi
  fi
done
