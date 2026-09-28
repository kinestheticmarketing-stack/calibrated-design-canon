---
id: gate-tracker-logs-gate-pass-on-a-mere-mention
owner: executor
type: defect
created: 2026-09-28
retriage: 2026-10-05
size: M
severity: high
---
# `cat _check_links.py` logs a GATE_LINKS PASS — deploy evidence can be fabricated by accident

`~/.claude/hooks/gate_tracker.sh` decides a gate ran by matching the script
name **anywhere** in a successful command:

```bash
if echo "$CMD" | grep -qE "${BOUND}_check_links\\.py([[:space:]]|\$)"; then
  log_decision "GATE_LINKS" "PostToolUse" "Bash" "PASS" "$GATE_REASON" "$SESSION_ID"
fi
```

So **reading** a gate script logs that the gate **passed**. H2 then accepts
those lines as proof the repo was gated and authorizes a real deploy.

Measured 2026-09-28, driving the production hook directly (cwd =
`denvercoloradoinsulation.com`):

| command | logged |
|---|---|
| `bash regen_all.sh && python3 _postbuild_check.py && python3 _check_links.py` | GATE_REGEN GATE_POSTBUILD GATE_LINKS — correct |
| `echo 'run: bash regen_all.sh && python3 _postbuild_check.py && …'` | **GATE_REGEN GATE_POSTBUILD** |
| `grep -n def _postbuild_check.py \| head` | **GATE_POSTBUILD** |
| `cat _check_links.py` | **GATE_LINKS** |
| `git commit -m 'note: run bash regen_all.sh before deploying'` | **GATE_REGEN** |

Standing evidence in `~/.claude/hooks/hook.log`:

```bash
awk -F'\t' '$3 ~ /^GATE_/ && $7 ~ /calibrated-design-canon/' ~/.claude/hooks/hook.log | wc -l
# -> 745
find ~/code/calibrated-design-canon -name 'regen_all.sh' -o -name '_postbuild_check.py' \
     -o -name '_check_links.py' -not -path '*/.git/*' | wc -l
# -> 0
```

**745 gate PASS lines are attributed to a repo that contains none of the three
gate scripts.** `gate_tracker.sh`'s own header blames the older cwd-attribution
bug for 714 of them, and ROW F fixed the attribution — but the count has kept
growing, because the *detection* is still a substring match. Every session that
merely discusses the gates manufactures more.

## Why this is worse after 2026-09-28

H2 now compares a **source-tree content hash** recorded on each PASS line. A
false PASS records the hash of the tree **as it is at mention time**, so if the
source has not changed since, the hash matches and the false PASS satisfies
H2 exactly as a real one would. The hash fixed the stale-against-own-output
defect; it does not and cannot detect a gate that never ran.

## The fix, when someone takes it

`_lib.sh` already has `invokes_script()` (added 2026-09-28), which answers
"is this name in command-word position" and is what H2, H3 and H13 now use.
**It cannot be reused as-is here**: the gates are invoked through an
interpreter — `bash regen_all.sh`, `python3 _postbuild_check.py` — so the
command word is `bash`/`python3`, not the script, and `invokes_script` would
report *no gate ran* and block every deploy.

What is needed is a sibling predicate: the name counts when it is in
command-word position **or** is the first non-flag argument of an interpreter
(`bash`, `sh`, `zsh`, `python`, `python3`, `perl`, `ruby`, `node`) that is
itself in command-word position.

**BLAST RADIUS — the reason this was carded rather than folded into the
2026-09-28 harness pass.** Get this wrong in the strict direction and gates
are never recorded, so H2 blocks every deploy of every property. Every
genuine invocation shape must be proven to still log before it lands:

```
bash regen_all.sh
./regen_all.sh
python3 _postbuild_check.py
cd <repo> && bash regen_all.sh
ssh host '... regen_all.sh'          # the quoted-remote shape gate_tracker
                                      # explicitly supports today
bash regen_all.sh && python3 _postbuild_check.py && python3 _check_links.py
```

Consider also whether the 745 historical canon-attributed lines should be
pruned from `hook.log`, or left with a note. They are inert for H2 today (it
matches on session id, and those sessions are gone) but they poison any audit
of the log.

## Verification when done

```bash
# Must log NOTHING:
for c in "cat _check_links.py" \
         "grep -n def _postbuild_check.py | head" \
         "echo 'run: bash regen_all.sh'" \
         "git commit -m 'note: run bash regen_all.sh before deploying'"; do
  jq -nc --arg r /Users/vongimbel/code/denvercoloradoinsulation.com --arg cmd "$c" \
    '{cwd:$r,tool_name:"Bash",session_id:"t",tool_input:{command:$cmd}}' \
    | bash ~/.claude/hooks/gate_tracker.sh
done
# Must still log all three (run from a real gate run, or drive the hook directly):
#   bash regen_all.sh && python3 _postbuild_check.py && python3 _check_links.py
```

## Source

Found 2026-09-28 by row R4 of the `harness-hardening-2026-09-28` lane. The
row's own commit message — which quoted `run: bash regen_all.sh && python3
_postbuild_check.py && python3 _check_links.py` from H2's deny text — logged
GATE_POSTBUILD and GATE_LINKS PASS against calibrated-design-canon, and H2
then cited those very lines back when refusing the next commit. Same defect
class as the H2/H3/H13 prose-mention false positives fixed in that row, but
in the opposite direction: those denied correct work, this **manufactures
authorization**. Fixing it needs a different predicate and carries
deploy-blocking blast radius, so it was reported rather than folded in.
`~/.claude` is now a git repository, so the change is revertible.
