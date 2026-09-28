---
id: h11-locked-strings-inert-on-multi-section-repos
owner: executor
type: defect
created: 2026-09-28
retriage: 2026-10-12
size: S
severity: medium
---
# H11 enforces nothing on two of the three property repos

`~/.claude/hooks/h11_locked_strings.sh` collects locked strings by scanning
the block under **any** heading whose text contains "locked", then joining
**all** blockquote lines it found — across **all** such headings — into a
single string with `paste -sd' '`.

`denvercoloradoinsulation.com/COPY_VOICE.md` has **two** locked headings:

- `## Locked homepage H1 (Director-approved 2026-09-27)` — one blockquote
- `### Locked acknowledgment line` — one blockquote

So the string H11 actually guards is the two quotes concatenated with a space,
about 260 characters, which appears in no file in the repo. `check_violation`
therefore never matches and H11 returns "no locked-string violation detected"
for **every** edit, including one that deletes the Director-approved homepage
H1 outright. Measured 2026-09-28, during the harness-hardening pass:

```bash
# The locked block, as H11 parses it, and what it collapses to:
awk 'BEGIN{i=0}/^#+[[:space:]]/{if(i){i=0;next} h=$0;sub(/^#+[[:space:]]*/,"",h);
  if(tolower(h)~/locked/){i=1}; next} i' \
  ~/code/denvercoloradoinsulation.com/COPY_VOICE.md \
  | grep -E '^>[[:space:]]?' | sed -E 's/^>[[:space:]]?//' | paste -sd' ' -
# -> one 260-char line that is two unrelated quotes glued together
```

State of all three property repos, same date:

| repo | headings containing "locked" | blockquote lines | H11 behaviour |
|---|---|---|---|
| denvercoloradoinsulation.com | 2 | 2 | joins both -> matches nothing, silent ALLOW |
| longmontcoloradoinsulation.com | 0 | 0 | WARN "no heading containing 'locked'", enforces nothing |
| greeleycoloradoinsulation.com | 1 | 0 | falls back to guarding the whole block as one string |

Canon Pattern 24 again: the instrument runs, returns clean, and is not pointed
at what it claims to check.

## The fix, when someone takes it

Treat each "locked" heading as its **own** section and each **contiguous**
blockquote as its **own** locked string, instead of globally joining every
quote line in the file. Bullets are already collected per-item; quotes should
be too.

**This is a TIGHTENING and needs care**: H11 currently denies nothing on DCI,
so the fix will start denying edits that pass today. Verify against real
pending edits before landing, and check LGM's missing section is a content
gap (add the heading) rather than a parser gap.

## Verification when done

```bash
# Must DENY: an edit that drops the Director-approved homepage H1.
jq -nc --arg c /Users/vongimbel/code/denvercoloradoinsulation.com \
  '{cwd:$c,tool_name:"Edit",session_id:"t",tool_input:{
     file_path:($c+"/_generate_homepage.py"),
     old_string:"h1: Denver Insulation That Stops You Heating the Attic All Winter.",
     new_string:"h1: Something Else"}}' \
  | bash ~/.claude/hooks/h11_locked_strings.sh
# today: no deny (defect).  after the fix: permissionDecision "deny"

# Must still ALLOW: an edit that preserves it verbatim.
# (same payload, new_string keeps the H1 unchanged)
```

## Source

Found 2026-09-28 by row R4 of the `harness-hardening-2026-09-28` lane while
building the before/after fire-and-allow matrix for the worktree scope fix
(card `lane-guard-inert-in-worktrees`). H11's deny case would not fire even at
a main-repo cwd, which is how the defect surfaced. Out of that row's scope —
it is a change to H11's matching semantics, not to repo scope — so it was
reported rather than folded in. Note `~/.claude` is now a git repository, so
this change is revertible.
