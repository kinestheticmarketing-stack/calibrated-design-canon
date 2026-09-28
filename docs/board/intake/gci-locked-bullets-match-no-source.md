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

**Unblocking action: the Director says which shipped strings GCI and LGM
actually want locked, verbatim as they appear in the generators.**

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
text and absent from its *after*. A string that appears in no generator and no
template can never be in a before text, so **none of the 9 can ever fire.**
The guard parses them, holds them, and they protect nothing.

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

## What closing this looks like

For each of GCI and LGM, the Director names the strings that are genuinely
Director-approved and must never be dropped, and each goes under a "Locked"
heading **as a blockquote holding the exact bytes the generator emits** — the
shape DCI already uses and that now works:

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

Related: [[h11-locked-strings-inert-on-multi-section-repos]] (the parser fix,
`~/.claude` `2e1d423`).
