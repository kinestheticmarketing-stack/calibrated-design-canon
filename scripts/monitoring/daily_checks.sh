#!/usr/bin/env bash
# Bundles the three heavier, less time-sensitive checks into one daily run:
# deploy drift (~40s, scp's public/ per property), TLS expiry (safety net,
# certbot already renews automatically), and every-page-200 (~38s, wraps
# ops/live_token_check.sh). Uptime is scheduled separately, far more
# frequently, since it's cheap (a handful of curls) and time-sensitive in a
# way these three aren't.
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$DIR/deploy_drift_check.sh"
"$DIR/tls_expiry_check.sh"
"$DIR/page200_check.sh"
