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

---

## OUTCOME — 2026-09-28, lane `harness-hardening-2026-09-28`, row R4

**Closed.** Option 1 was taken (map a worktree to its parent repo), but **not**
by rewriting `repo_root_for`, which would have broken something load-bearing.

### Why not one resolver

`gate_tracker.sh` deliberately depends on a worktree **not** resolving to its
main repo: a gate run in a worktree is not evidence that the *main checkout*
was gated, and it refuses to log one so H2 fails closed. Making the single
resolver worktree-aware would have converted that refusal into an approval
path for a real deploy of an ungated tree. So `~/.claude/hooks/_lib.sh` now
carries **three** resolvers:

| resolver | question it answers | a worktree resolves to |
|---|---|---|
| `repo_root_for` | physical checkout identity, prefix only — **unchanged** | nothing |
| `governed_repo_for` | jurisdiction: whose rules apply? | its main repo |
| `checkout_root_for` | which checkout is this file in? | the worktree |

`in_scope_repo` uses `governed_repo_for`, which re-arms H1, H3, H4, H5, H6,
H7, H8, H9, H10, H11, H12, H14, H15, H19 and `backup_tracker.sh` inside lane
worktrees. H9/H19 use it on **both** cwd and target (they must match, or a
lane could not write to itself). H10/H11/H12 use `checkout_root_for`, whose
subject is a file on disk. H2's cwd fallback and `gate_tracker.sh` stay
physical, the latter with a comment at the line telling the next pass not to
"fix" it.

### Measured cost

The `git` call only runs when the cheap prefix test misses. 20 iterations,
mean: main-repo cwd **0.880 ms** (unchanged baseline 0.888 ms), worktree cwd
**11.5 ms**, ungoverned cwd **10.8 ms**. Whole-hook cost for an ungoverned
cwd goes 13.6 → 23.6 ms.

### Also landed in the same row

- **The harness is now under version control.** `~/.claude` is a git repo,
  **local-only, no remote, and none may ever be added** — it holds session
  transcripts and credentials. Deny-by-default `.gitignore`; only authored
  material is tracked. This is what made the change testable at all; the card
  itself named "no VCS there" as the reason it was deferred.
- **The `CROSS_REPO_AUTHORIZED` marker file is no longer an authorization
  path** in H9 or H19, and both deny messages stopped instructing the reader
  to create one. Env var `CLAUDE_KICKOFF_CROSS_REPO=1` only, per the standing
  ruling in all four `docs/lanes.md`.

### Verification

```bash
# 1. THE CARD'S OWN TWO CASES. First must DENY (it used to ALLOW); second must
#    still ALLOW -- a lane has to be able to write to itself.
env -u CLAUDE_KICKOFF_CROSS_REPO bash -c 'printf "{\"cwd\":\"/Users/vongimbel/code/canon-wt/rule-10-canon\",\"tool_name\":\"Bash\",\"session_id\":\"t\",\"tool_input\":{\"command\":\"echo x > /Users/vongimbel/code/denvercoloradoinsulation.com/zz.txt\"}}" | bash ~/.claude/hooks/h19_lane_guard_shell.sh'
# -> {"hookSpecificOutput":{... "permissionDecision":"deny" ...}}

env -u CLAUDE_KICKOFF_CROSS_REPO bash -c 'printf "{\"cwd\":\"/Users/vongimbel/code/canon-wt/rule-10-canon\",\"tool_name\":\"Bash\",\"session_id\":\"t\",\"tool_input\":{\"command\":\"echo x > /Users/vongimbel/code/canon-wt/rule-10-canon/zz.txt\"}}" | bash ~/.claude/hooks/h19_lane_guard_shell.sh'
# -> no output, exit 0  == ALLOW

# 2. The resolvers do the three different jobs they are supposed to do.
bash -c 'source ~/.claude/hooks/_lib.sh
  governed_repo_for /Users/vongimbel/code/canon-wt/rule-10-canon   # -> .../calibrated-design-canon
  checkout_root_for /Users/vongimbel/code/canon-wt/rule-10-canon   # -> .../canon-wt/rule-10-canon
  repo_root_for     /Users/vongimbel/code/canon-wt/rule-10-canon   # -> (nothing) MUST stay empty'

# 3. gate_tracker.sh still refuses to attribute a worktree gate run to the
#    main checkout -- the constraint that forced three resolvers.
grep -n 'DO NOT "FIX" THIS TO USE governed_repo_for' ~/.claude/hooks/gate_tracker.sh

# 4. The marker file is dead in both halves of the guard.
grep -n 'CROSS_REPO_AUTHORIZED' ~/.claude/hooks/h09_lane_guard.sh ~/.claude/hooks/h19_lane_guard_shell.sh
# -> no non-comment occurrences

# 5. The harness is versioned and has NO REMOTE.
git -C ~/.claude log --oneline | head -6
git -C ~/.claude remote -v          # -> must print nothing
```

### Test results

The 108-assertion matrix the card points at **did not exist as an executable
harness** — `H19_KNOWN_LIMITATIONS.md` recorded a results table, not a script.
It was reconstructed as a runnable suite covering every row of that table plus
H9's 8 `Edit|Write` cases, and additionally run from a lane-worktree cwd,
which the original could not meaningfully do.

- **124 assertions: before 105 pass / 19 fail, after 124 / 0.** All 19
  failures were at the worktree cwd.
- **28-cell fire/allow matrix** over H2, H5, H9, H10, H11, H13, H19, at a
  main-repo cwd and a `~/code/canon-wt` worktree cwd, both polarities: 10 of
  the 14 worktree cells were SILENT (not evaluated) before; all 28 correct
  after.

### Commits

- Fix (in `~/.claude`, **not** canon — separate repo): baseline `fc7269c`,
  worktree scope fix **`b00f9ca`**, marker removal `d1afa55`.
- Card closure (canon): see the commit that moves this file to `done/`.

### Found and NOT fixed here

`h11_locked_strings.sh` joins **every** blockquote line under **every**
heading containing "locked" into one string. `denvercoloradoinsulation.com`
has two such headings, so H11 searches for a 260-character concatenation of
two unrelated quotes that appears in no file — it enforces nothing there.
`longmontcoloradoinsulation.com` has **zero** "locked" headings (H11 warns and
enforces nothing); `greeleycoloradoinsulation.com` has one with no blockquote.
Separate defect, separate card.
