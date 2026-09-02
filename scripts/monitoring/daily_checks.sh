#!/usr/bin/env bash
# Bundles the heavier, less time-sensitive checks into one daily run:
# deploy drift (~40s, scp's public/ per property), TLS expiry (safety net,
# certbot already renews automatically), every-page-200 (~38s, wraps
# ops/live_token_check.sh), ops drift (added 2026-08-31, ~5s, one
# directory not per-property -- does canon's ops/ match the VPS's
# /root/ops/scripts/, the shared alerting layer this whole monitoring
# directory depends on), and rules drift (added 2026-09-02, ~2s, one file
# pair not per-property -- does ~/.claude/context/rules.md still match
# canon's METHODS/ARCHITECT_DISCIPLINE.md, and is the local canon checkout
# itself current with origin/main). Uptime is scheduled separately, far
# more frequently, since it's cheap (a handful of curls) and time-sensitive
# in a way these five aren't.
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$DIR/deploy_drift_check.sh"
"$DIR/tls_expiry_check.sh"
"$DIR/page200_check.sh"
"$DIR/ops_drift_check.sh"
"$DIR/rules_drift_check.sh"
