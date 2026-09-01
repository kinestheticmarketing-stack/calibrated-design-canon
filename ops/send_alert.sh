#!/usr/bin/env bash
# /root/ops/scripts/send_alert.sh — real sender, replaces R2's testing stub.
# Interface UNCHANGED from the stub: <property_key> <subject> <body>
# (3 positional args). R2's own check scripts already implement their own
# per-day suppression/recovery state before deciding to call this, so this
# bridges straight to send_alert.js's --force mode (send unconditionally
# when called, still record state for send_alert.js's own callers/belt-and-
# braces layer, but never double-suppress against R2's already-decided call).
set -euo pipefail
PROP="$1"; SUBJECT="$2"; BODY="$3"
exec node /root/ops/scripts/send_alert.js "$PROP" "$SUBJECT" "$BODY" "$SUBJECT" --force
