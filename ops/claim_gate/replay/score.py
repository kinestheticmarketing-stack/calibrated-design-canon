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


def hits(sec, rid):
    return [l for l in sec.get(rid, {}).get("adj", []) if l.strip()]


def n(sec, rid, *needles):
    return len([l for l in hits(sec, rid)
                if all(x in l for x in needles)])


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
                  "T1 $-anchored %d" % _t1(s)))
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
    lambda t, s: ("CAUGHT" if ("r-value-needed-calculator-embed.html" in t
                               and "embed frame:" in t) else "MISSED",
                  "embed frame line present: %s; embed artifact in read set: %s"
                  % ("embed frame:" in t,
                     "r-value-needed-calculator-embed.html" in t)))


def _figs_files(s):
    import re as _re
    figs, files = set(), set()
    for ln in hits(s, "R3"):
        m = _re.match(r"\s*(\S+?):", ln)
        for f in _re.findall(r"\$[0-9][0-9,.]*", ln):
            figs.add(f)
            if m:
                files.add(m.group(1))
    v = "CAUGHT" if (len(figs) >= 9 and len(files) >= 24) else (
        "PARTIAL" if figs else "MISSED")
    return (v, "%d distinct $ figures across %d distinct files (T1 $-anchored "
               "%d); figures: %s"
            % (len(figs), len(files), _t1(s), ", ".join(sorted(figs))))


def _t1(s):
    for ln in s.get("R3", {}).get("all", []):
        m = re.search(r"T1 \$-anchored (\d+)", ln)
        if m:
            return int(m.group(1))
    return 0


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
print("PRIOR: 21 CAUGHT / 2 PARTIAL / 2 MISSED   (of 25)")
if changed:
    print("\nROWS THAT CHANGED VERDICT:")
    for c in changed:
        print("  %s %s: %s -> %s   (%s)" % c)
else:
    print("\nNO ROW CHANGED VERDICT.")
