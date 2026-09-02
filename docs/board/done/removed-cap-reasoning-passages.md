---
id: removed-cap-reasoning-passages
owner: director
type: record
created: 2026-08-21
priority: 30
retriage: 2026-10-02
classification: ALREADY-DONE
---
**Classification reasoning (2026-09-02):** The removal already shipped (Director ruling applied, word-inventory verified against the real diffs, commit range documented in-card) — the card now exists only as a preserved-text reference for a hypothetical future restoration, not open work.

# The three reasoning passages removed 2026-08-21 — full text preserved for restoration

Director ruling: these are ARGUMENTS whose load-bearing premise is an unsourced
number. Keeping them keeps the defect and makes the unsourced figure MORE
persuasive, not less — a homeowner reading "effectively a flat $500" has been
handed a conclusion to act on.

**If Xcel's own PDF later sources $500/$350/$400, restoring these is a clean
voice-gated wave.** Original text is preserved verbatim below so restoration
needs no reconstruction.

## CORRECTED 2026-08-21 — the word inventory

**The previously reported total of "420 source words removed" was wrong, and
wrong in a way that matters to a restoration card: 420 equals exactly the two
whole-section removals counted raw — 222 (`xcel-insulation-rebate-guide-denver`)
+ 198 (`whole-home-efficiency-bonus-stacking-denver`) — and therefore counted
NOTHING from `insulation-hybrid-flash-batt`.** The commit message that reported
it (83d4795, "420 source words removed across two full sections and three inline
passages") also over-claimed its own scope: the three inline passages are not in
the 420 either. One of the three pages preserved below was absent from the total
entirely.

Derived counts (range `239df21..83d4795`, i.e. both wave commits 8e6aacd and
83d4795, measured on the GENERATOR sources — the pages are regenerated output):

| page | source | gross | re-added | NET |
|---|---|---|---|---|
| `insulation-hybrid-flash-batt` | `_generate_service_pages.py` (renders) | 254 | 104 | **150** |
| `insulation-hybrid-flash-batt` | `_svc_pending_hybrid_flash_batt.py` (does NOT render) | 190 | 52 | **138** |
| `whole-home-efficiency-bonus-stacking-denver` | `_educational_pages.py` | 182 | 4 | **178** |
| `xcel-insulation-rebate-guide-denver` | `_educational_pages.py` | 406 | 141 | **265** |

**True totals — rendering generators only: 842 gross, 593 net.**
Including the non-rendering `_svc_pending_hybrid_flash_batt.py`: 1032 gross, 731 net.

Same measurement under a raw `wc -w` rule (markup and punctuation counted), for
comparability with the 420: hybrid 267/108/159 rendering + 203/56/147 pending;
whole-home 209/4/205; xcel 444/145/299. Rendering-only raw total **920 gross,
663 net**.

### Counting rule

- **Attribution.** A diff hunk counts against a page only if its PRE-IMAGE line
  range falls inside that page's `slug='…'` block in the 239df21 revision of the
  generator. `_svc_pending_hybrid_flash_batt.py` is one page whole-file, and is
  reported on its own line because it is tracked but imported by nothing — those
  words never reached a rendered page.
- **Gross** = words on `-` lines in that page's hunks. **Re-added** = words on
  `+` lines in the same hunks. **NET = gross − re-added.** Net is the honest
  answer to "how much text did the page lose", because most seams here were
  rewritten (`"up to $500 for attic work"` → `"against per-measure caps"`), not
  deleted. Gross alone overstates; the two must be quoted together.
- **A word** is a whitespace-delimited token containing at least one
  alphanumeric character, after: unescaping JSON/Python escapes (`\u2014` → em
  dash, `\"` → `"`) so no escape sequence counts as a word; stripping HTML tags
  (`<p>`, `</li>`, `<a href="…">`); and stripping Python string-literal
  delimiters and concatenation syntax. Bare em dashes, lone quotes and commas
  are therefore NOT words. The raw `wc -w` figures above apply none of this.

### Reproduce

Set `REPO` and run. Standalone, no other files needed; prints the table above.

```python
import re, subprocess
REPO, OLD, NEW = "/path/to/denvercoloradoinsulation.com", "239df21", "83d4795"
TARGETS = [("insulation-hybrid-flash-batt",
            "_generate_service_pages.py", "hybrid-flash-batt"),
           ("insulation-hybrid-flash-batt",
            "_svc_pending_hybrid_flash_batt.py", None),
           ("whole-home-efficiency-bonus-stacking-denver",
            "_educational_pages.py", "whole-home-efficiency-bonus-stacking-denver"),
           ("xcel-insulation-rebate-guide-denver",
            "_educational_pages.py", "xcel-insulation-rebate-guide-denver")]

def git(*a):
    return subprocess.run(["git", "-C", REPO, *a],
                          capture_output=True, text=True, check=True).stdout

def block(path, slug):          # 1-indexed [start, end) of a page's slug block at OLD
    if slug is None:
        return 1, 10 ** 9
    ls = git("show", OLD + ":" + path).splitlines()
    marks = [(i, m.group(1)) for i, l in enumerate(ls, 1)
             for m in [re.match(r"\s*slug='([^']+)'\s*,", l)] if m]
    for j, (st, sl) in enumerate(marks):
        if sl == slug:
            return st, (marks[j + 1][0] if j + 1 < len(marks) else len(ls) + 1)
    raise KeyError(slug)

def words(line, raw=False):     # THE COUNTING RULE
    if raw:                     # the wc -w rule: markup and punctuation included
        return len(line.split())
    t = line
    for a, b in [(chr(92) + "u2014", "\u2014"), (chr(92) + "n", " "),
                 (chr(92) + "t", " "), (chr(92) + chr(34), chr(34))]:
        t = t.replace(a, b)
    t = re.sub(r"<[^>]*>", " ", t)                          # HTML tags
    t = re.sub(r"^\s*[rfbu]*[\"']|[\"']\s*$", " ", t, flags=re.M)                      # py literal delimiters
    t = t.replace(chr(34), " ").replace("'", " ")
    return len([w for w in t.split() if re.search(r"[0-9A-Za-z]", w)])

for page, path, slug in TARGETS:
    lo, hi = block(path, slug)
    g = a = rg = ra = 0
    inside = False
    for ln in git("diff", "-U0", OLD + ".." + NEW, "--", path).splitlines():
        h = re.match(r"^@@ -(\d+)", ln)
        if h:
            inside = lo <= int(h.group(1)) < hi
        elif inside and ln.startswith("-") and not ln.startswith("---"):
            g += words(ln[1:]); rg += words(ln[1:], raw=True)
        elif inside and ln.startswith("+") and not ln.startswith("+++"):
            a += words(ln[1:]); ra += words(ln[1:], raw=True)
    print(f"{page:45s} {path:34s} prose {g:4d}/{a:4d}/{g-a:4d}  raw {rg:4d}/{ra:4d}/{rg-ra:4d}")
```

Spot check of the bad number, no script needed — these two commands are the
whole of the old 420:

```bash
cd denvercoloradoinsulation.com
git diff -U0 239df21..83d4795 -- _educational_pages.py \
  | awk '/^@@ -6195/{f=1;next} /^@@/{f=0} f&&/^-/{sub(/^-/,"");print}' | wc -w   # 222  xcel section
git diff -U0 239df21..83d4795 -- _educational_pages.py \
  | awk '/^@@ -6537/{f=1;next} /^@@/{f=0} f&&/^-/{sub(/^-/,"");print}' | wc -w   # 198  WHE section
```

## `insulation-hybrid-flash-batt.html`

**Passage 1:**

> On the rebate side, the Xcel Energy Insulation and Air Sealing Rebate pays 30% of project cost up to $500 for attic work — and on a hybrid attic project that $500 cap is reached almost immediately, so the rebate behaves as a flat $500 rather than a percentage that scales with the more expensive assembly. Here's the part most quotes won't tell you. Every winter you delay a real attic-and-air-sealing upgrade on a pre-1990 Denver home, you're heating the attic through the ceiling. Five winters of w

**Passage 2:**

> Two cautions before you count on the money. First, the $500 attic cap is reached on essentially every hybrid attic project, so the rebate behaves as a flat $500 rather than a percentage that grows with the assembly — choosing the more expensive approach does not earn a bigger check. Second, the removal step foam requires earns no direct rebate of its own; the rebate applies to the insulation and air sealing that follow it. On top of the standard rebate, the Xcel Whole Home Efficiency (WHE) Bonus

**Passage 3:**

> Worth knowing that the $500 attic cap is reached on essentially every hybrid project, so the rebate is effectively a flat $500 rather than 30% of a larger number." } }, { "@type": "Question", "name": "How long does a hybrid install take, and do I need to leave the house?", "acceptedAnswer": { "@type": "Answer", "text": "Plan on multiple days rather than one. Removal typically runs 4-8 hours on a 1,200 square foot attic, the flash coat is applied after that, and the home is vacated for a 24-hour 

## `whole-home-efficiency-bonus-stacking-denver.html`

**Passage 1:**

> Take a mid-range Denver attic scope from the deployed cost guides: roughly $3,000-$4,500 for air sealing plus a blown-in attic top-up. Standard rebates run 30% of each measure against its cap — the attic measure typically hits its $500 ceiling, air sealing at the $300-$1,200 range yields $90-$360 — for an estimated $590-$860 in standard rebates on a scope like this. Complete a third qualifying measure within two years of enrolling and the WHE bonus adds 25% of those rebates — roughly another $14

## `xcel-insulation-rebate-guide-denver.html`

**Passage 1:**

> A $3,000 attic top-up runs 30% to $900 on paper, but the attic cap stops it at $500. Air sealing at the $300-$1,200 range Denver projects typically see yields $90-$360 — under its $400 cap, so the full 30% usually survives there. The practical read: on bigger projects the effective percentage shrinks. Against the $1,500-$5,500 range most Denver attic projects land in (the attic cost guide breaks that spread down), the capped standard rebate is real money but not 30% of the invoice — bonuses are 

**Passage 2:**

> Chasing a $500 cap into a project your house doesn't need is the rebate tail wagging the dog \u2014 either way, the in-home assessment will tell you straight." } }, { "@type": "Question", "name": "How long until the rebate check arrives?", "acceptedAnswer": { "@type": "Answer", "text": "Xcel doesn't publish a guaranteed processing window, and this site won't invent one. What's knowable: the rebate is paid by check after the application is processed, complete paperwork moves faster than incomplet

## What the pages assert now

- `insulation-hybrid-flash-batt` — qualifies for the rebate on the same terms as any
  retrofit measure; one caution (the removal step earns no rebate of its own);
  requirements retained (participating contractor, blower door, 20% CFM50).
- `whole-home-efficiency-bonus-stacking-denver` — the worked-example section is gone;
  the stack, sequencing and bonus-eligibility content remain.
- `xcel-insulation-rebate-guide-denver` — the rebate-calculation section is gone; the
  program still names its three measures (attic, wall, air sealing) with no figures.

## R2 outcome note — 2026-09-02

Re-verified independently (not from R1's classification alone). Confirmed
directly in `denvercoloradoinsulation.com`'s git history:

- Commit `8e6aacd` ("Remove the unsourced $400 air-sealing rebate figure",
  2026-08-21 09:43) — R3, needle-scoped.
- Commit `83d4795` ("Remove the unsourced cap figures and the arguments
  built on them", 2026-08-21 15:53) — commit message states explicitly:
  *"Director ruling M3 Option 2 plus the Q1 passage removals... Three
  reasoning passages removed whole, not merely stripped of their figures."*
  This is the Director ruling the card text refers to, and it resolves
  exactly what the card asks (the three reasoning passages preserved above
  are the ones this commit removed).
- Confirmed live: none of the three preserved passages exist in DCI's
  current rendered output (`grep -q "attic cap is reached on essentially
  every hybrid" public/insulation-hybrid-flash-batt.html` → no match).

This card is correctly ALREADY-DONE: the removal shipped, is Director-ruled,
and the card's only remaining function is as preserved text for a future
restoration wave if Xcel's own PDF later sources $500/$350/$400 — not open
work.

**Verify:**
```bash
cd /Users/vongimbel/code/denvercoloradoinsulation.com
git show --stat 83d4795 | head -5   # commit exists, message cites "Director ruling M3 Option 2"
grep -q "attic cap is reached on essentially every hybrid" public/insulation-hybrid-flash-batt.html && echo STILL_PRESENT || echo ABSENT
# ABSENT confirms the removal held in the currently rendered page
```
