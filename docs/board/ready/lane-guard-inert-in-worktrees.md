---
id: lane-guard-inert-in-worktrees
owner: executor
type: defect
created: 2026-09-27
retriage: 2026-10-04
size: M
severity: high
---
# The lane guard is inert in exactly the mode this portfolio works in

Both halves of the cross-repo lane guard — H9 (`Edit|Write`) and the new H19
(`Bash`, added 2026-09-27) — begin with the same test:

```bash
if ! in_scope_repo "$CWD"; then exit 0; fi
```

`in_scope_repo` resolves against four hard-coded paths in
`~/.claude/hooks/_lib.sh`:

```
/Users/vongimbel/code/denvercoloradoinsulation.com
/Users/vongimbel/code/longmontcoloradoinsulation.com
/Users/vongimbel/code/greeleycoloradoinsulation.com
/Users/vongimbel/code/calibrated-design-canon
```

**Lane worktrees are not under any of them.** Measured 2026-09-27:

```
$ git -C ~/code/calibrated-design-canon worktree list
/Users/vongimbel/code/canon-wt/rule-10-canon     4596d99 [lane/rule-10-canon]
/Users/vongimbel/code/canon-wt/rule-11-canon     9493d7d [lane/rule-11-canon]
/Users/vongimbel/code/canon-wt/seo-geo-scaffold  1f282fa [feat/seo-geo-scaffold]
```

So a session working a lane — **the documented normal case**, since every
repo's `CLAUDE.md` says *"One session = one lane worktree; two sessions never
share a checkout"* — switches the entire lane guard off. Proven, not argued:

```bash
$ printf '{"cwd":"/Users/vongimbel/code/canon-wt/rule-10-canon","tool_name":"Bash",
  "session_id":"t","tool_input":{"command":"echo x > /Users/vongimbel/code/denvercoloradoinsulation.com/zz.txt"}}' \
  | bash ~/.claude/hooks/h19_lane_guard_shell.sh
# -> no output, exit 0  == ALLOW, not evaluated
```

The same holds for H9 on the `Edit|Write` path.

## Why this was not fixed in the pass that found it

The 2026-09-27 close-out pass carried an explicit **ADDITIVE ONLY** constraint
on the guard row: *"Never remove or loosen an existing rule."* Closing this
means changing `REPO_ROOTS` or the cwd test in `_lib.sh`, which is shared by
**H2 (deploy), H5 (destructive-without-backup), H9, H10 (worktree collision),
H11 (locked strings), H13 (post-deploy verify) and H19**. That is a
portfolio-wide behaviour change to a harness with **no version control**
(`git -C ~/.claude rev-parse --is-inside-work-tree` -> `fatal: not a git
repository`), landing at the end of a long pass. The blast radius is wider
than the row's scope and wider than could be tested responsibly in the same
sitting.

This is not deferral of something a pass could have closed — it is a
different, larger change than the one that was authorized.

## The fix, when someone takes it

Two options, in preference order:

1. **Map a worktree to its parent repo.** `git -C "$CWD" rev-parse
   --git-common-dir` returns the main checkout's `.git` for a worktree; its
   parent is the real repo root. This is correct for arbitrary worktree
   locations and needs no list maintenance. Costs one `git` call per hook
   invocation — measure it, because these hooks run on every tool call.
2. **Add the worktree parents to `REPO_ROOTS`** (`canon-wt/`, `dci-wt/`,
   `lgm-wt/`, `gci-wt/`). Simpler, but it is a list that will rot the first
   time someone puts a worktree somewhere else.

Either way the change is a **tightening** (more protected roots, never fewer),
so it does not conflict with the additive-only rule that deferred it — that
rule blocked changing H9's behaviour mid-pass, not tightening it deliberately.

## Verification when done

```bash
# Must DENY (currently ALLOWs):
printf '{"cwd":"/Users/vongimbel/code/canon-wt/rule-10-canon","tool_name":"Bash",
  "session_id":"t","tool_input":{"command":"echo x > /Users/vongimbel/code/denvercoloradoinsulation.com/zz.txt"}}' \
  | bash ~/.claude/hooks/h19_lane_guard_shell.sh
# Must still ALLOW (write stays inside the worktree's own repo):
printf '{"cwd":"/Users/vongimbel/code/canon-wt/rule-10-canon","tool_name":"Bash",
  "session_id":"t","tool_input":{"command":"echo x > /Users/vongimbel/code/canon-wt/rule-10-canon/zz.txt"}}' \
  | bash ~/.claude/hooks/h19_lane_guard_shell.sh
```
Re-run H19's own 108-assertion matrix and H9's 8-case Edit|Write baseline
afterwards; both are described in `~/.claude/hooks/H19_KNOWN_LIMITATIONS.md`.

**Back up `~/.claude/hooks/` and `settings.json` first — there is no VCS
there.** The convention is `<file>.bak-pre-<change>-<YYYY-MM-DD>`.

## Source

Found by the R5 harness row of the 2026-09-27 close-out pass while closing a
different gap (H9 was blind to shell-redirect writes; H19 closed that). The
row reported this one rather than silently widening its own scope, and the
orchestrator confirmed it independently.
