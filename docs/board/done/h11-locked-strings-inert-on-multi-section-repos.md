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

---

## DONE 2026-09-28 — fixed in `~/.claude` `2e1d423`; card closed in canon `9a0467c`

**Two repos, two hashes.** The fix lives in the harness repo `~/.claude` (no
remote, never pushed) at **`2e1d423`**, "H11: one locked string per
blockquote, per section, each enforced on its own". This card-closing commit
is in **calibrated-design-canon**.

Each locked heading is now its own section, and within a section each
**contiguous** run of blockquote lines is its own locked string. Bullets were
already per-item and stay that way. Every string is enforced independently,
and the deny names both the dropped string and the section it is locked
under.

### Exactly what is now enforced, per repo — and each confirmed verbatim

**denvercoloradoinsulation.com** — two locked strings where there was one
unmatched 260-character splice:

1. Under `## Locked homepage H1 (Director-approved 2026-09-27)`:
   > Denver Insulation That Stops You Heating the Attic All Winter.

   Verbatim in `_generate_homepage.py`, `STATE_OF_PROJECT.md`,
   `COPY_VOICE.md`, `docs/audits/phase-a-rows/index.html.md` (moved
   2026-09-28 from `docs/board/phase-a-rows/`, the path this card cited
   when written), and `public/index.html`.

2. Under `### Locked acknowledgment line`:
   > The federal IRA Section 25C tax credit ended December 31, 2025, and
   > Colorado's HEAR single-family program is now closed for both Region 1
   > (the Front Range) and Region 2. Xcel Energy programs are the ones still
   > paying on Denver-area insulation projects in 2026.

   Verbatim in `_shared_components.py` (`REBATE_ACKNOWLEDGMENT`),
   `_educational_pages.py`, `COPY_VOICE.md`, and **70** pages under `public/`.

**greeleycoloradoinsulation.com** — 9 bullet strings, unchanged by this fix.
`Atomic answer 54-60 words.` / `Disqualification FAQ sits
**second-to-last**.` / `Per-page `faq_h2`, `next_step_h2`, `next_step_body`
are required fields — no inherited boilerplate from another page's topic.` /
`Honeypot (`company_website`) + `form_loaded_at` on every page carrying the
form.` / `Plain `&` in escaped fields.` / `No urgency framing. No
response-time promises.` / `**Johnstown — NO QUALIFIER.** Its source states
Xcel for gas flatly. The` / `**Milliken — "most of Milliken".**` /
`**Severance — "most locations in Severance".**`

**longmontcoloradoinsulation.com** — `COPY_VOICE.md` exists but has no
heading containing "locked". H11 warns and enforces nothing, without crashing
and without false-denying. **This is a content gap, not a parser gap** —
carried forward below.

### Two corrections to this card's own table

- **GCI**: this card recorded "1 heading / 0 blockquote lines / falls back to
  guarding the whole block as one string." GCI actually has **two** locked
  headings (`## Locked conventions ...` at line 122 and `### The per-town
  qualifier rule (LOCKED, 2026-09-08)` at line 177) and **9 bullets** between
  them, so the bullet branch was already taken and the fallback never ran.
  GCI was **not** inert on this axis.
- **The real GCI gap is different and is left open**: all 9 bullet strings
  occur in exactly one file — `COPY_VOICE.md` itself. None appears in any
  generator or template, so no edit to source can ever have one in its
  "before" text, and none can be dropped. They are inert in practice. They are
  also markdown prose (`**second-to-last**`) rather than shipped copy, and the
  multi-line ones are truncated at the first physical line. **Making these
  match real code is a Director copy question, not a parser change**, so it
  was reported, not fixed. Carded as `gci-locked-bullets-match-no-source`.

### Fixed in passing

The old heading rule was `if (insec) { insec=0; next }` — a heading met while
already inside a section ended it **without being tested** for "locked", so
two adjacent locked headings silently collapsed into one. Every heading is now
tested. Sections that parse to no locked string are now `LOG`-ged by name
instead of passing in silence.

`checkout_root_for` (R4, `b00f9ca`) is preserved: `COPY_VOICE.md` is
per-branch, so a lane worktree's copy governs edits made in it.

### Verification — re-runnable cold

```bash
H11=~/.claude/hooks/h11_locked_strings.sh
DCI=/Users/vongimbel/code/denvercoloradoinsulation.com
H1='Denver Insulation That Stops You Heating the Attic All Winter.'
ACK="The federal IRA Section 25C tax credit ended December 31, 2025, and Colorado's HEAR single-family program is now closed for both Region 1 (the Front Range) and Region 2. Xcel Energy programs are the ones still paying on Denver-area insulation projects in 2026."
d() { jq -nc --arg c "$1" --arg f "$1/_generate_homepage.py" --arg o "$2" --arg n "$3" \
  '{cwd:$c,tool_name:"Edit",session_id:"v",tool_input:{file_path:$f,old_string:$o,new_string:$n}}' \
  | bash $H11 | jq -r '.hookSpecificOutput.permissionDecision // "allow"'; }

d "$DCI" "h1: $H1" "h1: Something Else"          # -> deny   (this card's headline case)
d "$DCI" "h1: $H1" "h1: $H1  # reflowed"         # -> allow
d "$DCI" "$ACK"    "Rebates changed."            # -> deny
d "$DCI" "$ACK"    "x $ACK y"                    # -> allow
# multi-string, one dropped and the other kept -- must deny and NAME the dropped one:
d "$DCI" "$H1
$ACK" "$H1
(removed)"                                        # -> deny  (names the ACK)
d "$DCI" "$H1
$ACK" "A New Headline
$ACK"                                             # -> deny  (names the H1)
d "$DCI" "$H1
$ACK" "$H1
$ACK
plus a new sentence."                             # -> allow (both kept)

# zero-heading repo must not crash or false-deny:
d /Users/vongimbel/code/longmontcoloradoinsulation.com a b   # -> allow, with a WARN on stderr

# the parser emits one string PER SECTION, not one splice. Expect 2 for DCI:
awk 'function e(s){sub(/^[[:space:]]+/,"",s);sub(/[[:space:]]+$/,"",s);if(s!="")print sec"\t"s}
     function f(){if(q!=""){e(q);q=""}}
     /^#+[[:space:]]/{f();h=$0;sub(/^#+[[:space:]]*/,"",h);
       if(tolower(h)~/locked/){insec=1;sec=h}else{insec=0;sec=""};next}
     insec{if($0~/^ {0,3}>/){l=$0;sub(/^ {0,3}>[ ]?/,"",l);q=(q==""?l:q" "l);next};f();
       if($0~/^[[:space:]]*[-*][[:space:]]/){b=$0;sub(/^[[:space:]]*[-*][[:space:]]*/,"",b);e(b)}}
     END{f()}' $DCI/COPY_VOICE.md | wc -l
# -> 2   (before the fix: 1 splice of ~260 chars matching nothing)

# each enforced DCI string really exists in the code it protects:
grep -cF -- "$H1"  $DCI/_generate_homepage.py     # -> >= 1
grep -cF -- "$ACK" $DCI/_shared_components.py     # -> >= 1

git -C ~/.claude log --oneline -1 2e1d423
git -C ~/.claude remote -v | wc -l                # -> 0
```

### Both polarities proven, at both cwd kinds

11 cases at a main-repo cwd and 7 at a worktree cwd, all as expected. The
worktree pair is the load-bearing one: with a throwaway DCI worktree's
`COPY_VOICE.md` patched to lock a sentinel string instead of the H1, the
worktree enforced **its own** sentinel and allowed dropping the main
checkout's H1, while the main checkout simultaneously still denied dropping
that same H1. Per-branch resolution is real, not assumed. The worktree was
removed; DCI left with 0 uncommitted files.

**R4's own before/after matrix re-run against the fixed hooks**
(`/tmp/r4-matrix.sh`, DCI worktree repointed to a throwaway, H10's fixture
recreated): **28/28 rows identical** to R4's recorded post-fix matrix,
including both H11 rows at both cwd kinds. Also green: `r4-cmdword` 30/30,
`r4-h19-h9` 124/124, `r4-deploy`, `r4-h13`, `r4-h13b`, `r4-h4`, `r4-h2hash`,
`r4-h2stale`.

### Carried forward, deliberately

- `gci-locked-bullets-match-no-source` (new card) — GCI's 9 locked bullets
  exist only in `COPY_VOICE.md`.
- LGM has no locked section at all. Adding one is Director copy work, and
  this card already called it a content gap. Folded into the same new card.
