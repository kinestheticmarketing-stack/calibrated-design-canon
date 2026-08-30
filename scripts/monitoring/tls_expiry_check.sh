#!/usr/bin/env bash
# 2c. TLS expiry safety net. certbot.timer already renews automatically
# (confirmed active on the VPS) — this should almost never fire. It exists
# for the day renewal itself silently fails.
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/_mon_lib.sh"

for propline in "${PROPERTIES[@]}"; do
  prop=$(prop_field "$propline" 1)
  url=$(prop_field "$propline" 2)
  host="${url#https://}"; host="${host#http://}"; host="${host%%/*}"

  # NOTE: openssl s_client has no "-timeout" flag for a TLS (non-DTLS)
  # connection -- passing one made the handshake fail silently every time,
  # every property, in real testing. `timeout` (the shell command) wrapping
  # the whole invocation is the correct, portable way to bound this.
  enddate=$(echo | timeout 15 openssl s_client -servername "$host" -connect "$host:443" 2>/dev/null \
    | openssl x509 -noout -enddate 2>/dev/null | sed 's/notAfter=//')

  if [ -z "$enddate" ]; then
    if should_alert_failure "tls_expiry" "$prop"; then
      send_alert "$prop" "TLS check failed on $prop: could not read certificate" "Could not retrieve or parse the TLS certificate for $prop. This may mean the site is unreachable or the cert is malformed."
      record_failure_alert "tls_expiry" "$prop"
    fi
    continue
  fi

  exp_epoch=$(date -j -f "%b %d %T %Y %Z" "$enddate" +%s 2>/dev/null || date -d "$enddate" +%s 2>/dev/null)
  now_epoch=$(date +%s)
  days_left=$(( (exp_epoch - now_epoch) / 86400 ))

  if [ "$days_left" -le 14 ]; then
    if should_alert_failure "tls_expiry" "$prop"; then
      send_alert "$prop" "TLS certificate for $prop expires in $days_left day(s)" "$prop's TLS certificate expires in $days_left day(s) ($enddate). certbot should renew automatically — this alert means it hasn't yet, and manual attention may be needed before the site starts showing security warnings."
      record_failure_alert "tls_expiry" "$prop"
    fi
  else
    if should_alert_recovery "tls_expiry" "$prop"; then
      send_alert "$prop" "TLS expiry resolved on $prop" "$prop's certificate now has $days_left days remaining — back to a healthy margin."
      clear_failure_state "tls_expiry" "$prop"
    fi
  fi
done
