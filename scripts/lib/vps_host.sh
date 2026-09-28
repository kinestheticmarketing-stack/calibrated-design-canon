#!/usr/bin/env bash
# scripts/lib/vps_host.sh — resolves the production VPS address at RUNTIME.
#
# WHY THIS EXISTS: calibrated-design-canon is a PUBLIC GitHub repository
# (`gh repo view ... --json visibility` -> PUBLIC). Until 2026-09-28 the
# production VPS address was written literally into 11 tracked files, so it
# was served to anyone on the internet from raw.githubusercontent.com. The
# scrub replaced every literal with `$VPS` — which is fine in prose, but a
# script that merely contains the TEXT `$VPS` without ever defining it
# expands to the empty string and runs `ssh root@`, which is the silent
# failure this portfolio keeps finding: a monitoring check that checks
# nothing and stays quiet about it. So the four live scripts resolve the
# real value here instead of carrying it.
#
# RESOLUTION ORDER:
#   1. $VPS_ADDR from the environment. First, deliberately: it is the only
#      path that works in an environment without this Mac's ~/.claude tree
#      (a CI runner, another operator's machine, or — see below — the VPS
#      itself). One-off override: `VPS_ADDR=1.2.3.4 ./scripts/...`.
#   2. ~/.claude/hooks/h04_wrong_ssh_host.sh, the unpublished source of
#      truth. ~/.claude has NO git remote and is never published, and that
#      hook must already hold the address because its whole job is to deny
#      ssh/scp to any other host. Reusing it means there is exactly one
#      unpublished copy to keep correct, not two.
#
# ON THE VPS: none of canon's four address-bearing scripts run there.
# scripts/monitoring/* run on this Mac under launchd (com.vongimbel.r2daily)
# and reach out over ssh; scripts/deploy_ops_to_vps.sh runs here too, and its
# FILES list — the only sanctioned canon->VPS copy path — ships ops/*.js and
# ops/*.sh only, never scripts/. If that ever changes, path 1 ($VPS_ADDR) is
# the supported answer there, because ~/.claude does not exist on the VPS.
#
# FAILS LOUD, NEVER SILENT: if neither path yields a dotted quad this prints
# to stderr and returns non-zero. Callers must propagate that (`|| exit 1`)
# rather than proceed with an empty host.
#
# Sourced by: scripts/monitoring/_mon_lib.sh (which every scripts/monitoring
# check sources) and scripts/deploy_ops_to_vps.sh.

resolve_vps_addr() {
  local addr="${VPS_ADDR:-}"
  local src="$HOME/.claude/hooks/h04_wrong_ssh_host.sh"

  if [ -z "$addr" ] && [ -r "$src" ]; then
    addr="$(grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' "$src" | head -1)"
  fi

  if [[ ! "$addr" =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ ]]; then
    echo "FATAL: could not resolve the production VPS address." >&2
    echo "  Tried: \$VPS_ADDR (unset or not a dotted quad), then $src" >&2
    echo "  Set VPS_ADDR in the environment, or restore that hook file." >&2
    echo "  Refusing to continue against an empty host." >&2
    return 1
  fi

  printf '%s\n' "$addr"
}
