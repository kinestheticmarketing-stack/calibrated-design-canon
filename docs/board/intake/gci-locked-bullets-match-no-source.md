---
id: gci-locked-bullets-match-no-source
owner: director
type: defect
created: 2026-09-28
retriage: 2026-10-19
size: S
severity: low
---
# GCI's 9 locked strings exist only in COPY_VOICE.md, and LGM has none at all

**Unblocking action: for GCI, the Director picks one of exactly two options —
(A) give GCI a real locked copy string, or (B) rule that H11 does not apply to
GCI. For LGM, the same choice, from a blank slate.**

> Re-framed 2026-09-28 after an adversarial verification reader challenged the
> original framing. This card is **not** a request to "make the 9 strings
> match", and must not be read as one. GCI's nine locked entries are **rules**
> ("Atomic answer 54-60 words.", "Disqualification FAQ sits second-to-last."),
> not copy. H11 enforces verbatim-string preservation, so it **structurally
> cannot** enforce a rule — no amount of editing makes a rule into a string a
> generator emits. The choice below is therefore binary, and one of its two
> arms is "this guard is the wrong instrument here, say so and stop."

Surfaced 2026-09-28 closing [[h11-locked-strings-inert-on-multi-section-repos]].
That card fixed H11's parser — DCI now enforces two real locked strings where
it previously enforced one 260-character splice that matched nothing. This is
the residue the parser fix cannot reach, because it is a **copy** question,
not a parsing one.

## GCI

Both locked headings parse correctly and yield 9 bullet strings. Every one of
them occurs in **exactly one file: `COPY_VOICE.md` itself.**

```bash
cd /Users/vongimbel/code/greeleycoloradoinsulation.com
for s in "Atomic answer 54-60 words." \
         "Plain \`&\` in escaped fields." \
         '**Milliken — "most of Milliken".**'; do
  printf '%2s  %s\n' "$(grep -rlF -- "$s" . 2>/dev/null | wc -l | tr -d ' ')" "$s"
done
# -> 1 for each, and the 1 is COPY_VOICE.md
```

H11 denies an edit only when a locked string is present in the edit's *before*
text and absent from its *after*. The nine appear in no generator and no
template, so **they guard no site copy whatsoever.** The guard parses them,
holds them, and not one byte of what GCI ships is protected by them.

**Precisely what is and is not true here** (the original wording of this card
said "none of the 9 can ever fire", and that overstated it):

They *can* fire — on an edit to `COPY_VOICE.md` itself. H11 is registered on
`Edit|Write` and tests the edit's `old_string`/`new_string` whatever file is
being edited, so deleting a locked bullet from `COPY_VOICE.md` is denied.
Verified:

```bash
# cwd = greeleycoloradoinsulation.com, editing COPY_VOICE.md to change
# "- Atomic answer 54-60 words." to "- Atomic answer 40 words."
# -> deny: "edit drops locked string [Atomic answer 54-60 words.] ...
#           without preserving it verbatim in the replacement"
```

So the nine are self-guarding: they protect the list of themselves. That is a
real effect, and it is not the effect a copy lock is for. **The defect is not
"they never fire" — it is that they guard the rulebook instead of the
product.**

Two reasons they cannot match, and they need different answers:

1. **They are rules, not copy.** "Atomic answer 54-60 words." and "No urgency
   framing. No response-time promises." are instructions to a writer. They are
   not strings any file ships. A string-preservation guard is the wrong
   instrument for them — `_postbuild_check.py` is.
2. **They are markdown, and truncated.** `**Milliken — "most of Milliken".**`
   carries bold markers the code does not, and the multi-line Johnstown bullet
   is cut at its first physical line (`... Xcel for gas flatly. The`). Even the
   ones that *describe* shipped copy could not match it byte for byte.

## LGM

`longmontcoloradoinsulation.com/COPY_VOICE.md` exists and has **no heading
containing "locked"**, so H11 warns and enforces nothing there. Confirmed a
content gap, not a parser gap — the parser finds two headings in GCI and two
in DCI from the same file.

```bash
grep -cE '^#+[[:space:]].*[Ll]ocked' /Users/vongimbel/code/longmontcoloradoinsulation.com/COPY_VOICE.md
# -> 0
```

## The choice — exactly two options, per repo

**Option A — give GCI a real locked copy string.** The Director names copy
that GCI actually ships and that must never be dropped, and it goes under a
"Locked" heading as a blockquote holding the exact bytes the generator emits.
H11 then guards something. The nine rules move to a heading *without* "locked"
in it, where they stay useful as conventions and stop being mistaken for
string locks.

**Option B — rule that H11 does not apply to GCI.** Entirely legitimate: GCI
may simply have no Director-approved verbatim copy worth locking. Then the
"Locked" heading is renamed so H11 finds no section, H11 warns once and
enforces nothing there, and that warning is the honest state of affairs rather
than a guard pretending to work.

What is **not** on the menu is "edit the nine until they match something".
They are rules; a string-preservation guard cannot enforce a rule at any
level of editing effort. `_postbuild_check.py` is the instrument for a rule
like "Atomic answer 54-60 words." — a card for that is a separate, later
question, not this one.

LGM faces the same two options from a blank slate, since it has no locked
heading at all.

## What Option A looks like

The Director names the strings that are genuinely Director-approved and must
never be dropped, and each goes under a "Locked" heading **as a blockquote
holding the exact bytes the generator emits** — the shape DCI already uses and
that now works:

```markdown
## Locked <what> (Director-approved <date>)

> <the exact string, copied out of the generator, no markdown inside it>

Source of truth: `_generate_x.py`, `SOME_CONST`.
```

Then prove it, the same way DCI's two were proven:

```bash
grep -cF -- "<the string>" /Users/vongimbel/code/<repo>/_generate_x.py   # -> >= 1
```

**Do not close this by deleting GCI's bullets.** They are real conventions and
belong in `COPY_VOICE.md`; they are just not string locks. Move them under a
heading *without* "locked" in it, or leave them and add a real locked section
alongside — either way H11 stops holding strings it cannot enforce.

Note the interaction with the self-guarding effect above: while the nine sit
under a "Locked" heading, H11 will **deny the very edit that moves them**.
Whoever executes the chosen option needs to either preserve each bullet
verbatim in the replacement text (H11 allows that — it checks preservation,
not location) or rename the heading first, in an edit that drops nothing.

Related: [[h11-locked-strings-inert-on-multi-section-repos]] (the parser fix,
`~/.claude` `2e1d423`).
