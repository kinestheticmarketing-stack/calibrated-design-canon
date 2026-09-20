"""Score the 20 replayed pre-fix trees against the 25 documented defect
instances, using the evidence line each row was scored on in
GATE_SCORE_2026-09-17.md and GATE_CLOSE_2026-09-18.md."""
import os
import re
import sys

OUT = os.environ.get("REPLAY_OUT",
                     os.path.join(os.environ.get("REPLAY_SCRATCH",
                                                 "/tmp/claim-gate-replay"),
                                  "replay"))

RULE_HEAD = re.compile(r"^━━━ (R\d+[a-z]?)\s")


def sections(path):
    """rule id -> {'all': text, 'adj': [hit lines], 'removed': [lines]}"""
    txt = open(path, encoding="utf-8", errors="replace").read()
    lines = txt.split("\n")
    out, cur, mode = {}, None, None
    for ln in lines:
        m = RULE_HEAD.match(ln.strip()) or RULE_HEAD.match(ln)
        if ln.strip().startswith("━━━"):
            mm = re.match(r"━━━\s+(R\d+)\s", ln.strip())
            cur = mm.group(1) if mm else None
            if cur:
                out[cur] = {"all": [], "adj": [], "removed": []}
            mode = None
            continue
        if cur is None:
            continue
        out[cur]["all"].append(ln)
        if re.search(r"--- \d+ hits, enumerated ---", ln):
            mode = "adj"
            continue
        if re.search(r"--- \d+ items the filters removed", ln):
            mode = "removed"
            continue
        if mode:
            out[cur][mode].append(ln)
    return txt, out


def adj_count(sec, rid):
    for ln in sec.get(rid, {}).get("all", []):
        m = re.search(r"ADJUDICATED\s+.*?\s(\d+)\s*$", ln.strip())
        if m:
            return int(m.group(1))
    return 0


# The gate prints a literal `  (none)` INSIDE the enumeration when a rule has
# no adjudicated hits, so the raw `adj` list is one element long for an EMPTY
# rule and `hits()` was truthy on nothing at all. No row misscored on it today,
# because every row counts needles rather than testing the list -- but a future
# row written `"CAUGHT" if hits(s, rid)` would have scored CAUGHT on a rule that
# found nothing, which is the exact shape of the row-12 defect. Dropped here
# rather than left for that row to be written.
_PLACEHOLDER = frozenset(("(none)",))
# `  <rel>:<surface>  <sub>  <text>` -- the locator is everything before the
# first double space. Needed because a hit's TEXT can contain a filename that
# the hit is not ON: `llms.txt` appears inside llms.txt's own rendered lines,
# and an R4 row quoting a URL is not a finding on that URL.
LOC_RE = re.compile(r"^\s{2}(\S+?):(\S+?)\s\s")


def hits(sec, rid):
    return [l for l in sec.get(rid, {}).get("adj", [])
            if l.strip() and l.strip() not in _PLACEHOLDER]


def locator(line):
    m = LOC_RE.match(line)
    return m.group(1) if m else ""


def n(sec, rid, *needles):
    return len([l for l in hits(sec, rid)
                if all(x in l for x in needles)])


def n_loc(sec, rid, *needles):
    """Like n(), but the needles must be in the hit's LOCATOR."""
    return len([l for l in hits(sec, rid)
                if all(x in locator(l) for x in needles)])


def on_artifact(sec, needle):
    """Adjudicated rows, ACROSS EVERY RULE, whose locator names `needle`."""
    out = []
    for rid in sec:
        out += [l for l in hits(sec, rid) if needle in locator(l)]
    return out


ROWS = []


def row(num, label, key, sha, fn):
    ROWS.append((num, label, key, sha, fn))


row("1", "Fabricated quotation (11 pages) LGM R1", "lgm", "8b0f1a9",
    lambda t, s: ("CAUGHT" if n(s, "R1", "XCEL_BLOWER_DOOR") >= 11 else
                  "PARTIAL" if n(s, "R1", "XCEL_BLOWER_DOOR") else "MISSED",
                  "%d XCEL_BLOWER_DOOR adjudicated rows"
                  % n(s, "R1", "XCEL_BLOWER_DOOR")))
row("2a", "Wrong utility, prose (35 pages) GCI R2", "gci", "e912eee",
    lambda t, s: ("CAUGHT" if n(s, "R2", "Atmos Energy", "scope=Severance")
                  else "MISSED",
                  "%d Atmos/scope=Severance adjudicated rows"
                  % n(s, "R2", "Atmos Energy", "scope=Severance")))
row("2b", "Wrong utility, og:image GCI R2", "gci", "e912eee",
    lambda t, s: ("CAUGHT" if n(s, "R2", "og-image.svg") else "MISSED",
                  "%d adjudicated og-image.svg rows (raised+enumerated in the "
                  "removed list: %d)"
                  % (n(s, "R2", "og-image.svg"),
                     len([l for l in s.get("R2", {}).get("removed", [])
                          if "og-image.svg" in l]))))
row("3a", "Retired eligibility, Lafayette LGM R7", "lgm", "a2ba5a6",
    lambda t, s: ("CAUGHT" if n(s, "R7", "whe_audit_entry_path_begin_with")
                  else "MISSED",
                  "%d whe_audit_entry_path_begin_with rows"
                  % n(s, "R7", "whe_audit_entry_path_begin_with")))
row("3b", "Retired eligibility, prerequisite DCI R7", "dci", "130921c",
    lambda t, s: ("CAUGHT" if n(s, "R7", "air_sealing_is_a_prerequisite")
                  else "MISSED",
                  "%d air_sealing_is_a_prerequisite rows"
                  % n(s, "R7", "air_sealing_is_a_prerequisite")))
row("4a", "Invented pathways, long form DCI R7", "dci", "f08bb9f",
    lambda t, s: ("CAUGHT" if n(s, "R7", "installed_and_invoiced_by_dec_31_2026")
                  else "MISSED",
                  "%d installed_and_invoiced_by_dec_31_2026 rows"
                  % n(s, "R7", "installed_and_invoiced_by_dec_31_2026")))
row("4b", "Short form 'Dec. 31, 2026' in the generator DCI R7/R5", "dci",
    "2a59a97",
    lambda t, s: ("CAUGHT" if n(s, "R7", "src:") or
                  len([l for l in hits(s, "R7") if "Dec. 31" in l]) else
                  "MISSED",
                  "R7 adjudicated %d, of which SRC %d; 'Dec. 31' rows %d"
                  % (adj_count(s, "R7"), n(s, "R7", "src:"),
                     len([l for l in hits(s, "R7") if "Dec. 31" in l]))))
row("4c", "The invented fifth Xcel program DCI R2 sub p", "dci", "f08bb9f",
    lambda t, s: ("CAUGHT" if n(s, "R2", "forbidden-program-name") or
                  n(s, "R2", "Xcel IQ") else "MISSED",
                  "%d forbidden-program-name rows"
                  % max(n(s, "R2", "forbidden-program-name"),
                        n(s, "R2", "Xcel IQ"))))
row("5a", "198 rebate dollar figures DCI R3", "dci", "169bb3c",
    lambda t, s: ("CAUGHT" if _t1(s) >= 198 else
                  "PARTIAL" if _t1(s) else "MISSED",
                  "T1 adjudicated %d (was scored off the RAW pre-filter note "
                  "until 2026-09-20)" % _t1(s)))
row("5b", "133 rebate dollar figures LGM R3", "lgm", "604d052",
    lambda t, s: (_p116(s), "$1.16 adjudicated %d, $0.77 adjudicated %d, "
                            "R3 ADJ %d"
                  % (n(s, "R3", "$1.16"), n(s, "R3", "$0.77"),
                     adj_count(s, "R3"))))
row("5c", "206 rebate dollar figures GCI R3", "gci", "236c464",
    lambda t, s: _figs_files(s))
row("5d", "Bare-digit cap 1550/0.75 in a JS comment GCI R3 T2", "gci",
    "e994484",
    lambda t, s: ("CAUGHT" if n(s, "R3", "1550") else "MISSED",
                  "%d rows carrying 1550" % n(s, "R3", "1550")))
row("6", "Self-contradicting calculator DCI R6", "dci", "58c44eb",
    lambda t, s: ("CAUGHT" if adj_count(s, "R6") else "MISSED",
                  "R6 adjudicated %d" % adj_count(s, "R6")))
row("7a", "Stacking, 70 of 72 pages DCI R4", "dci", "bcb64a3",
    lambda t, s: ("CAUGHT" if adj_count(s, "R4") else "MISSED",
                  "R4 adjudicated %d" % adj_count(s, "R4")))
row("7b", "Stacking DCI R4", "dci", "dd88de3",
    lambda t, s: ("CAUGHT" if adj_count(s, "R4") else "MISSED",
                  "R4 adjudicated %d" % adj_count(s, "R4")))
row("7c", "Stacking DCI R4", "dci", "b5635c9",
    lambda t, s: ("CAUGHT" if adj_count(s, "R4") else "MISSED",
                  "R4 adjudicated %d" % adj_count(s, "R4")))
row("7d", "Stacking DENIAL as schema.org FAQPage GCI R4", "gci", "e994484",
    lambda t, s: ("CAUGHT" if n(s, "R4", "insulation-rebate-hub.html")
                  else "MISSED",
                  "%d insulation-rebate-hub.html R4 rows; R4 ADJ %d"
                  % (n(s, "R4", "insulation-rebate-hub.html"),
                     adj_count(s, "R4"))))
row("7e", "Knob-and-tube stacking denial LGM R4", "lgm", "2563a56",
    lambda t, s: ("CAUGHT" if n(s, "R4", "knob-and-tube") else "MISSED",
                  "%d knob-and-tube R4 rows; R4 ADJ %d"
                  % (n(s, "R4", "knob-and-tube"), adj_count(s, "R4"))))
row("7f", "llms.txt 'Xcel rebate-stack eligibility' DCI R4", "dci", "d1b6078",
    lambda t, s: ("CAUGHT" if n(s, "R4", "llms.txt") else "MISSED",
                  "%d llms.txt R4 rows; R4 ADJ %d"
                  % (n(s, "R4", "llms.txt"), adj_count(s, "R4"))))
row("8", "Uncited 25-40% on 16 pages DCI R5", "dci", "4cf7a52",
    lambda t, s: (_pages2540(s)[0], _pages2540(s)[1]))
row("9a", "Review date 17 days before the page existed DCI R8", "dci",
    "539670e",
    lambda t, s: ("CAUGHT" if n(s, "R8", "precedes-creation") else "MISSED",
                  "%d precedes-creation rows" % n(s, "R8",
                                                  "precedes-creation")))
row("9b", "contact.html two dates 33 days apart GCI R8", "gci", "12dfcbf",
    lambda t, s: ("CAUGHT" if n(s, "R8", "contact.html", "surfaces-disagree")
                  else "MISSED",
                  "%d contact.html surfaces-disagree rows"
                  % n(s, "R8", "contact.html", "surfaces-disagree")))
row("10", "Hidden calc_output 'already at code' DCI R9", "dci", "cb675ab",
    lambda t, s: ("CAUGHT" if n(s, "R9", "N3b") else "MISSED",
                  "%d N3b rows; R9 ADJ %d (N3-unverifiable rows %d)"
                  % (n(s, "R9", "N3b"), adj_count(s, "R9"),
                     n(s, "R9", "N3-unverifiable"))))
row("11", "Dangling promise 'The Atmos figures quoted elsewhere' GCI R10",
    "gci", "e994484",
    lambda t, s: ("CAUGHT" if n(s, "R10", "insulation-johnstown.html")
                  else "MISSED",
                  "%d insulation-johnstown R10 rows; R10 ADJ %d"
                  % (n(s, "R10", "insulation-johnstown.html"),
                     adj_count(s, "R10"))))
row("12", "Embed frame / llms.txt corpus hole DCI", "dci", "539670e",
    lambda t, s: _corpus_hole(s))


def _corpus_hole(s):
    """ROW 12, REWRITTEN 2026-09-20. WHAT IT USED TO BE AND WHY THAT WAS NOT A
    TEST.

    It was the ONLY row of the 25 whose lambda read `t`, the entire gate
    output, instead of the adjudicated enumeration:

        "CAUGHT" if ("r-value-needed-calculator-embed.html" in t
                     and "embed frame:" in t) else "MISSED"

    `embed frame:` occurs EXACTLY ONCE per file -- at line 12, in the
    corpus-inventory preamble, BEFORE any rule section -- and that single
    134-character line satisfies BOTH needles at once:

        embed frame: public/r-value-needed-calculator-embed.html,
        public/r-value-needed-calculator-embed-code.html  |  IN THE READ SET:
        2 of 2

    The gate prints that line UNCONDITIONALLY on every tree, including
    `embed frame: NULL RESULT - GCI has no embed frame.` on GCI. So the row
    returned CAUGHT against any DCI tree, including one with the defect fully
    fixed, and carried NO DETECTION INFORMATION. Measured 2026-09-20: the old
    lambda returns CAUGHT on all 12 DCI replay trees without exception.

    WHAT REPLACES IT IS THE ROW'S OWN DOCUMENTED EVIDENCE, NOT A NEW
    DEFINITION. GATE_SCORE_2026-09-17.md's row 12 cites three things, and two
    of the three are ADJUDICATED FINDINGS ON THE HIDDEN ARTIFACTS:
    `public/r-value-needed-calculator-embed.html:JS mag 15% | ...15% reduction
    in heating and cooling costs...` and `R4 x2 on the frame`. The defect this
    row scores is a CORPUS HOLE -- two artifacts a sitemap-enumerated sweep
    could not see -- so the gate has caught it exactly when it PRODUCES
    FINDINGS ON THOSE ARTIFACTS, across any rule. The locator is matched, never
    the hit text: `llms.txt` appears inside llms.txt's own rendered lines and
    an R4 row quoting a URL is not a finding on that URL.

    Both halves are required because the row names both halves. One half alone
    is PARTIAL, not CAUGHT.
    """
    emb = on_artifact(s, "r-value-needed-calculator-embed")
    llm = on_artifact(s, "llms.txt")
    got = bool(emb) + bool(llm)
    return (("CAUGHT" if got == 2 else "PARTIAL" if got == 1 else "MISSED"),
            "%d adjudicated rows on the embed frame (%s); %d on llms.txt (%s)"
            % (len(emb), ",".join(sorted(set(
                   r for r in _rules_of(s, emb)))) or "-",
               len(llm), ",".join(sorted(set(
                   r for r in _rules_of(s, llm)))) or "-"))


def _rules_of(s, lines):
    want = set(lines)
    return [rid for rid in s for l in hits(s, rid) if l in want]


def _figs_files(s):
    # A FIGURE GLUED TO ITS PUNCTUATION IS THE SAME FIGURE. `\$[0-9][0-9,.]*`
    # is greedy over `,` and `.`, so `$1,075`, `$1,075,` and `$1,075.` counted
    # as THREE distinct figures. Measured on gci-236c464 2026-09-20: 17
    # "distinct" figures, 7 after the trailing separators are stripped
    # ($1,075 $1,150 $1,325 $1,550 $125 $575 $663). The inflation ran in the
    # GENEROUS direction -- toward CAUGHT -- which is the direction a defect
    # score must never drift.
    figs, files = set(), set()
    for ln in hits(s, "R3"):
        loc = locator(ln)
        for f in re.findall(r"\$[0-9][0-9,.]*", ln):
            f = f.rstrip(",.")
            if len(f) > 1:
                figs.add(f)
                if loc:
                    files.add(loc)
    v = "CAUGHT" if (len(figs) >= 9 and len(files) >= 24) else (
        "PARTIAL" if figs else "MISSED")
    return (v, "%d distinct $ figures across %d distinct files (T1 "
               "adjudicated %d); figures: %s"
            % (len(figs), len(files), _t1(s), ", ".join(sorted(figs))))


# `  <rel>:<surface>  T1  ...` -- the ADJUDICATED T1 rows.
_T1_ROW = re.compile(r"^\s{2}\S+?:\S+?\s\sT1\s\s")


def _t1(s):
    """ADJUDICATED T1 count.

    IT USED TO READ A RAW PRE-FILTER COUNT out of a rule header note:

        note: T1 $-anchored 179  .  T2 bare numeral in a money window 545  .
              T3 rank/magnitude/superlative 45

    PROOF THAT NOTE IS RAW, measured 2026-09-20 on gci-236c464: 179 + 545 + 45
    = 769, which is exactly the rule's printed `RAW ... found 769`, while the
    rule's whole ADJUDICATED total is 91. The old `_t1` therefore returned 179
    -- a number larger than the entire adjudicated population it was being
    compared against. Same proof on dci-169bb3c: 222 + 1040 + 61 = 1323 = RAW.

    True adjudicated T1: 220 on dci-169bb3c, 53 on gci-236c464. Row 5a's
    threshold is 198, so its verdict SURVIVES the correction on dci-169bb3c
    (220 >= 198) -- but it was surviving on the wrong instrument, and the
    instrument is what a defect score is.
    """
    return len([l for l in hits(s, "R3") if _T1_ROW.match(l)])


def _p116(s):
    a = n(s, "R3", "$1.16")
    b = n(s, "R3", "$0.77")
    tot = a + b
    if tot >= 94:
        return "PARTIAL"
    return "PARTIAL" if tot else "MISSED"


def _pages2540(s):
    pages = set()
    for ln in hits(s, "R5"):
        if "25-40%" in ln:
            m = re.match(r"\s*(\S+?):", ln)
            if m:
                pages.add(m.group(1))
    return (("CAUGHT" if len(pages) >= 16 else
             "PARTIAL" if pages else "MISSED"),
            "25-40%% adjudicated on %d distinct pages: %s"
            % (len(pages), ", ".join(sorted(p.split("/")[-1]
                                            for p in pages))))


PRIOR = {
    "1": "CAUGHT", "2a": "CAUGHT", "2b": "MISSED", "3a": "CAUGHT",
    "3b": "CAUGHT", "4a": "CAUGHT", "4b": "CAUGHT", "4c": "CAUGHT",
    "5a": "CAUGHT", "5b": "PARTIAL", "5c": "CAUGHT", "5d": "CAUGHT",
    "6": "CAUGHT", "7a": "CAUGHT", "7b": "CAUGHT", "7c": "CAUGHT",
    "7d": "CAUGHT", "7e": "CAUGHT", "7f": "CAUGHT", "8": "PARTIAL",
    "9a": "CAUGHT", "9b": "CAUGHT", "10": "MISSED", "11": "CAUGHT",
    "12": "CAUGHT",
}

cache = {}
tal = {"CAUGHT": 0, "PARTIAL": 0, "MISSED": 0}
changed = []
print("%-4s %-8s %-8s %s" % ("#", "PRIOR", "NOW", "evidence"))
for num, label, key, sha, fn in ROWS:
    p = os.path.join(OUT, "%s-%s.txt" % (key, sha))
    if p not in cache:
        cache[p] = sections(p)
    t, s = cache[p]
    verdict, why = fn(t, s)
    tal[verdict] = tal.get(verdict, 0) + 1
    flag = "" if PRIOR[num] == verdict else "   <<< CHANGED"
    if PRIOR[num] != verdict:
        changed.append((num, label, PRIOR[num], verdict, why))
    print("%-4s %-8s %-8s %s%s" % (num, PRIOR[num], verdict, why, flag))
    print("     %s  [%s @ %s]" % (label, key, sha))
print()
print("SCORE: %d CAUGHT / %d PARTIAL / %d MISSED   (of %d)"
      % (tal["CAUGHT"], tal["PARTIAL"], tal["MISSED"], len(ROWS)))
# DERIVED FROM THE `PRIOR` DICT, NOT A LITERAL KEPT IN SYNC BY HAND. The banner
# read "21 CAUGHT / 2 PARTIAL / 2 MISSED" as a hardcoded string, so an edit to
# one PRIOR entry could silently disagree with the banner printed beside it --
# in a file whose whole purpose is that a score not be asserted.
_pt = {}
for _v in PRIOR.values():
    _pt[_v] = _pt.get(_v, 0) + 1
print("PRIOR: %d CAUGHT / %d PARTIAL / %d MISSED   (of %d)"
      % (_pt.get("CAUGHT", 0), _pt.get("PARTIAL", 0), _pt.get("MISSED", 0),
         len(PRIOR)))
if changed:
    print("\nROWS THAT CHANGED VERDICT:")
    for c in changed:
        print("  %s %s: %s -> %s   (%s)" % c)
else:
    print("\nNO ROW CHANGED VERDICT.")
