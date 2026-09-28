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

---

## DONE 2026-09-28 — fixed in `~/.claude` `c9217a3`; card closed in canon `9a0467c`

**Two repos, two hashes.** The fix lives in the harness repo
`~/.claude` (no remote, never pushed) at **`c9217a3`**, "A gate counts as run
only if it was actually run". This card-closing commit is in
**calibrated-design-canon**.

`_lib.sh` gained `invokes_via_interpreter()`, the sibling predicate this card
asked for. `invokes_script()` answers "is this name in command-word position"
and could not be reused, exactly as this card said: every gate here runs
THROUGH an interpreter, so it would have reported that no gate ever ran and
blocked every deploy of every property. The new predicate counts a name in
command-word position **or** as the script argument of an interpreter that is
itself in command-word position. `invokes_script()` is left byte-identical so
H2/H3/H13 do not move.

Three things the fix does that a position test alone would not, each forced by
a shape found in the evidence rather than invented:

- **Quote-aware segmentation.** `git commit -m 'run: bash regen_all.sh &&
  python3 _postbuild_check.py'` split on the `&&` *inside* the message, reset
  to command-word position, and read the quoted text as a real invocation.
  That is how several of the 745 were minted — including, as this card notes,
  the commit that created this card's sibling.
- **Here-document bodies dropped.** `git commit -F - <<MSG ... bash
  regen_all.sh ... MSG` writes a message; it does not run a gate. The body is
  kept when the line's command word is a shell that executes it
  (`bash`/`sh`/`ssh`), and a delimiter that never recurs as a standalone line
  is ignored, so a stray `<<` cannot swallow the rest of a command.
- **Variable indirection followed.** `VERIFY='... python3
  _postbuild_check.py ...'; bash -c "$VERIFY"` was the one genuine run in the
  whole corpus that a purely literal reading missed. Expansion happens only
  on the nested-command path, so `echo "$VAR"` still does not count.

Interpreter flags meaning "do not actually run this" disqualify the match:
`-n`/`-c` for shells, `-m`/`-c` for python, `--check`/`-e`/`-p` for node.
`bash -n regen_all.sh` occurs 7 times in the transcripts and is a syntax
check, not a gate run.

### Blast radius, measured rather than argued

The shapes were **harvested, not guessed**: 1690 distinct gate-mentioning Bash
commands pulled from 709 transcripts under `~/.claude/projects`, plus the 15
`GATE_RUN` lines in `hook.log` that still carry command text. Old regex vs new
predicate over all 2694 (name, command) pairs:

| | pairs |
|---|---|
| both fire | 1273 |
| **only OLD — false passes removed** | **923** |
| **only NEW — genuine runs the old regex MISSED** | **140** |
| neither | 358 |
| **genuine invocations lost** | **0** |
| **residual false positives** | **0** |

Every one of the 13 removed pairs that pattern-matched "looks like a real run"
was hand-checked: heredoc bodies, commit messages, greps, `bash -n`,
`f=<path>` assignments. The 140 newly-caught are overwhelmingly `python3
_check_links.py; echo "EXIT=$?"` — a genuine shape the old trailing
`([[:space:]]|$)` could not match. **The fix is strictly better in both
directions, not a trade.**

`src_tree_hash` is now computed only after a gate actually matched; it walks
the whole source tree and this hook runs on every successful Bash call.

### The 745 historical lines were deliberately NOT pruned

They are the evidence of the defect, and `h02_deploy_guard.sh` matches on
session id, so lines carrying dead session ids cannot authorize any future
deploy. Deleting them would destroy the record without changing a single
decision. `hook.log` was neither rewritten nor truncated.

### Verification — re-runnable cold

```bash
# 1. Must log NOTHING. Drives the production hook, same as this card's own
#    verification block. Expect: 0
SID="verify-$(date +%s)"
for c in "cat _check_links.py" \
         "grep -n def _postbuild_check.py | head" \
         "echo 'run: bash regen_all.sh'" \
         "git commit -m 'note: run bash regen_all.sh before deploying'" \
         "git commit -m 'run: bash regen_all.sh && python3 _postbuild_check.py && python3 _check_links.py'" \
         "head -50 regen_all.sh" "wc -l _check_links.py" "ls -la regen_all.sh" \
         "python3 -m py_compile _postbuild_check.py" "sed -n '1,5p' regen_all.sh" \
         "find . -name regen_all.sh" "scp regen_all.sh host:/tmp/" "bash -n regen_all.sh"; do
  jq -nc --arg r /Users/vongimbel/code/denvercoloradoinsulation.com --arg cmd "$c" --arg s "$SID" \
    '{cwd:$r,tool_name:"Bash",session_id:$s,tool_input:{command:$cmd}}' \
    | bash ~/.claude/hooks/gate_tracker.sh
done
awk -F'\t' -v s="$SID" '$2==s && $3 ~ /^GATE_/' ~/.claude/hooks/hook.log | wc -l
# -> 0

# 2. Must still log all three. Expect: GATE_REGEN GATE_POSTBUILD GATE_LINKS
SID2="control-$(date +%s)"
jq -nc --arg r /Users/vongimbel/code/denvercoloradoinsulation.com --arg s "$SID2" \
  --arg cmd 'bash regen_all.sh && python3 _postbuild_check.py && python3 _check_links.py' \
  '{cwd:$r,tool_name:"Bash",session_id:$s,tool_input:{command:$cmd}}' \
  | bash ~/.claude/hooks/gate_tracker.sh
awk -F'\t' -v s="$SID2" '$2==s {printf "%s ", $3}' ~/.claude/hooks/hook.log; echo
# -> GATE_REGEN GATE_POSTBUILD GATE_LINKS

# 3. The predicate exists and gate_tracker uses it, not a substring regex.
grep -c 'invokes_via_interpreter' ~/.claude/hooks/_lib.sh ~/.claude/hooks/gate_tracker.sh
# -> _lib.sh:1  gate_tracker.sh:3
grep -c 'BOUND=' ~/.claude/hooks/gate_tracker.sh
# -> 0

# 4. The harness commit is present and the repo still has no remote.
git -C ~/.claude log --oneline -1 c9217a3
git -C ~/.claude remote -v | wc -l   # -> 0
```

**Live end-to-end positive control, not simulated:** a real `bash
regen_all.sh` in `longmontcoloradoinsulation.com` (clean tree, untouched by
the concurrent row) through the committed hook logged
`GATE_REGEN PASS repo=/Users/vongimbel/code/longmontcoloradoinsulation.com`
at 2026-09-28T13:32:25Z, exit 0, tree still clean afterwards.

**R4's own suite, re-run against the fixed hooks** (`/tmp/r4-gatefalse.sh`
with its hard-coded `HD=/tmp/r4-after/hooks` repointed): the genuine run still
logs all three; the echo, the grep, the cat and the commit message now log
nothing. Before the fix the same script logged `GATE_REGEN GATE_POSTBUILD`,
`GATE_POSTBUILD`, `GATE_LINKS` and `GATE_REGEN` respectively.

Closes the last open item on this card. Nothing carried forward.
