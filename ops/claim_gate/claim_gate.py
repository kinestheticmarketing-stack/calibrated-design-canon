#!/usr/bin/env python3
"""claim_gate.py -- the ONE implementation of the standing claim gate.

Specification: ops/claim_gate/RULES_SPEC.md, in full. Every rule here is
derived from a defect this portfolio shipped live between 2026-09-01 and
2026-09-11. The gate is the re-runnable acceptance predicate over the whole
deployed artifact set; it is NOT an inventory, NOT a build gate, NOT a truth
oracle, and it NEVER edits anything.

python3 STDLIB ONLY (spec 1). Read-only on content. Writes nothing except an
explicit --report path.

Exit codes (spec 4):
  0  every blocking rule PASS, every control fired, corpus counts agree
  1  at least one blocking rule FAIL
  2  control failure, config error, corpus divergence, filter arithmetic
     mismatch, or a corpus smaller than the config's min_artifacts -- "the gate
     could not be trusted to have run"
"""

import sys

# The gate writes NOTHING into the repo it is run from or the repo it lives in.
# Importing surfaces.py would otherwise drop ops/claim_gate/__pycache__/ next
# to the implementation. Set BEFORE any first-party import.
#
# ADVERSARIAL READ, anomaly 8: setting this in the module body is too late when
# something ELSE imports claim_gate.py -- by then the import machinery has
# already written claim_gate's own .pyc. The wrapper therefore also exports
# PYTHONDONTWRITEBYTECODE=1, which is the only place that can be early enough.
sys.dont_write_bytecode = True

import argparse  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import tokenize  # noqa: E402
import ast  # noqa: E402
import time  # noqa: E402

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import surfaces as S  # noqa: E402

FIXTURES = os.path.join(_HERE, "fixtures")

# ---------------------------------------------------------------------------
# Output primitives (spec 4). Column layout inherited from _artifact_grep.sh's
# printf '  %-6s %-46s %s\n'.
# ---------------------------------------------------------------------------

BAR = "━" * 3


class Out(object):
    def __init__(self):
        self.lines = []

    def __call__(self, s=""):
        self.lines.append(s)

    def field(self, label, desc, value, tail=""):
        self("  %-16s %-46s %s%s" % (label, desc, value, tail))

    def head(self, s):
        self("%s %s %s" % (BAR, s, BAR))

    def text(self):
        return "\n".join(self.lines) + "\n"


class ConfigError(Exception):
    pass


class ArithmeticMismatch(Exception):
    pass


# ---------------------------------------------------------------------------
# Hits, filters, adjudication (spec 4.1-4.3)
# ---------------------------------------------------------------------------

class Hit(object):
    __slots__ = ("rid", "sub", "rel", "surface", "locator", "text", "note",
                 "cite_key", "sentence", "r5_inblock", "r5_instat",
                 "r8_excluded", "r2_noscope", "r2_subject_ok", "r3_kind",
                 "on_embed", "r3_w60", "r3_w40", "r3_struct", "r5_stats",
                 "r2_sitewide", "r2_binding", "r2_sentence_bound")

    def __init__(self, rid, sub, rel, surface, locator, text, note="",
                 cite_key=None, sentence=""):
        self.rid = rid
        self.sub = sub
        self.rel = rel
        self.surface = surface
        self.locator = locator
        self.text = S.collapse(text)[:220]
        self.note = note
        self.cite_key = cite_key
        self.sentence = S.collapse(sentence or text)
        self.r5_inblock = False
        self.r5_instat = False
        self.r8_excluded = ""
        self.r2_noscope = False
        self.r2_subject_ok = True
        self.r3_kind = ""
        self.on_embed = False
        self.r3_w60 = ""
        self.r3_w40 = ""
        self.r3_struct = ""
        self.r5_stats = []
        self.r2_sitewide = False
        self.r2_binding = None
        self.r2_sentence_bound = False

    def sortkey(self):
        return (self.rel, self.sub, self.surface, self.locator, self.text)

    def line(self):
        n = ("  [%s]" % self.note) if self.note else ""
        e = "  [EMBED]" if getattr(self, "on_embed", False) else ""
        return "  %s:%s  %s  %s%s%s" % (self.rel, self.surface, self.sub,
                                        self.text, n, e)


class Filt(object):
    """One named filter. `count` is taken over ALL raw candidates; `removed` is
    taken over the candidates still standing when this filter runs -- so a
    filter can report that it matched N and removed fewer, which is exactly the
    shape spec 4's sample block prints."""

    def __init__(self, label, pred, removes=True):
        self.label = label
        self.pred = pred
        self.removes = removes


def adjudicate(raw_hits, filters):
    """Partition the raw candidates through the named filters, then CROSS-CHECK
    the partition independently.

    The adversarial read was right that the old check was unreachable: it
    compared a partition against its own arithmetic, which holds by
    construction. The three checks below are independent of how the partition
    was built and each one can actually fail:

      C1  every REMOVED hit is re-tested against the filter credited with
          removing it, on a second evaluation. A predicate that is
          order-dependent, stateful or non-idempotent fails here.
      C2  every SURVIVING hit is re-tested against EVERY removing filter. A
          survivor that any filter matches means the partition leaked -- the
          adjudicated set would contain something a filter claims to have
          cleared.
      C3  the identity, recomputed from the re-tested sets rather than from the
          loop's own counters.

    Any failure raises ArithmeticMismatch and the gate exits 2.
    """
    remaining = list(raw_hits)
    rows = []
    for f in filters:
        count = 0
        for h in raw_hits:
            if f.pred(h):
                count += 1
        removed = []
        if f.removes:
            keep = []
            for h in remaining:
                if f.pred(h):
                    removed.append(h)
                else:
                    keep.append(h)
            remaining = keep
        rows.append((f.label, count, removed))

    removing = [f for f in filters if f.removes]
    by_label = {}
    for f in removing:
        by_label.setdefault(f.label, []).append(f)

    # C1 -- re-test every removal against its own credited filter
    recheck_removed = 0
    for label, count, removed in rows:
        for h in removed:
            preds = by_label.get(label) or []
            if not any(f.pred(h) for f in preds):
                raise ArithmeticMismatch(
                    "C1: hit %r was removed by filter %r but that filter does "
                    "not match it on re-evaluation (non-idempotent predicate)"
                    % (h.locator, label))
            recheck_removed += 1

    # C2 -- re-test every survivor against every removing filter
    for h in remaining:
        for f in removing:
            if f.pred(h):
                raise ArithmeticMismatch(
                    "C2: hit %r survived adjudication but filter %r matches it "
                    "on re-evaluation -- the partition leaked"
                    % (h.locator, f.label))

    # C3 -- the identity, from the re-tested counts
    if recheck_removed + len(remaining) != len(raw_hits):
        raise ArithmeticMismatch(
            "C3: raw %d - removed %d != adjudicated %d"
            % (len(raw_hits), recheck_removed, len(remaining)))
    return remaining, rows


class RuleResult(object):
    def __init__(self, rule):
        self.rule = rule
        self.raw = []
        self.rows = []
        self.adjudicated = []
        self.levels = {}
        self.level_detail = []
        self.degraded = []
        self.notes = []
        self.traps = []
        self.verdict = "PASS"
        self.reason = ""
        self.skipped = False


class Rule(object):
    def __init__(self, rid, name, kind, surf, norms, blind_spot, fn,
                 blocking=True, controls=(), opt_in=False):
        self.rid = rid
        self.name = name
        self.kind = kind
        self.surf = surf
        self.norms = norms
        self.blind_spot = blind_spot
        self.fn = fn
        self.blocking = blocking
        self.controls = list(controls)
        self.opt_in = opt_in


class Control(object):
    """A positive control, its sub-test binding, and its REPAIR counterpart.

    `sub` is mandatory in practice: without it a hit from any sub-test
    satisfied the control, which is how R1's claim-test half and R2's
    wrong-utility half ended up with no control at all -- each was satisfied by
    a different half of the same fixture.

    `repaired` names a fixture in which the defect has been FIXED. The rule must
    return zero hits on `sub` against it. A control that still fires on a
    repaired fixture is not a control, and the gate treats that as a control
    failure (exit 2), which is the mechanical form of Ruling 6.
    """

    def __init__(self, cid, rid, fixture, overlay=None, expect=1, sub=None,
                 extra=(), repaired=None, repaired_extra=()):
        self.cid = cid
        self.rid = rid
        self.fixture = fixture
        self.overlay = overlay or {}
        self.expect = expect
        self.sub = sub
        # Extra fixture files the control's corpus needs -- R2b's og-image.svg
        # is the whole point of the no-string vector: the claim is not in the
        # HTML, it is in something the HTML points at.
        self.extra = list(extra)
        self.repaired = repaired
        self.repaired_extra = list(repaired_extra)


# ---------------------------------------------------------------------------
# Config loading (spec 1: the config holds values, the implementation holds
# rules). `extends` keeps one copy of the shared VALUES; the direct lesson of
# _artifact_grep.sh, whose GCI and LGM copies diverged into two files that must
# be maintained twice.
# ---------------------------------------------------------------------------

def _deep_merge(base, over):
    out = dict(base)
    for k, v in over.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(path):
    seen = []
    cur = path
    chain = []
    while True:
        cur = os.path.abspath(cur)
        if cur in seen:
            raise ConfigError("config extends cycle at %s" % cur)
        seen.append(cur)
        if not os.path.isfile(cur):
            raise ConfigError("config not found: %s" % cur)
        with open(cur, "r", encoding="utf-8") as fh:
            try:
                doc = json.load(fh)
            except ValueError as exc:
                raise ConfigError("config %s is not valid JSON: %s" % (cur, exc))
        chain.append(doc)
        parent = doc.get("extends")
        if not parent:
            break
        cur = os.path.join(os.path.dirname(cur), parent)
    cfg = {}
    for doc in reversed(chain):
        cfg = _deep_merge(cfg, doc)
    cfg.pop("extends", None)
    for req in ("key", "repo", "min_artifacts", "expected_html"):
        if req not in cfg:
            raise ConfigError("config is missing required field %r" % req)
    return cfg


# ---------------------------------------------------------------------------
# Corpus enumeration (spec 2). Enumerate from public/, NEVER from sitemap.xml.
# ---------------------------------------------------------------------------

BINARY_EXT = (".ico", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf",
              ".woff", ".woff2", ".ttf", ".eot", ".zip", ".mp4", ".avif")


def git(repo, *args):
    try:
        p = subprocess.run(["git"] + list(args), cwd=repo,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        return None
    if p.returncode != 0:
        return None
    return p.stdout.decode("utf-8", "replace")


class Corpus(object):
    def __init__(self):
        self.ls_files = []
        self.found = []
        self.read_set = []
        self.excluded = []      # (rel, reason)
        self.agree = True
        self.divergence = []
        self.escaping_symlinks = []


_DOC_PREFIXES = ("_", "note", "reason", "basis", "source", "why")

# ---------------------------------------------------------------------------
# The gate's AS-OF (spec 8 R8). ONE resolver, used everywhere `today` is read.
# ---------------------------------------------------------------------------
# R8.today USED TO BE A HAND-MAINTAINED ISO LITERAL in four config files plus
# this module's own hardcoded fallback, and it aged silently. Nothing failed on
# it on 2026-09-19; on 2026-09-20 it produced 246 phantom findings on DCI --
# R8 RAW 247 / ADJ 246 / FAIL, re-measured read-only at the true date as RAW 1
# / ADJ 0 / PASS. dci.json's own today_note had already recorded the same
# recurrence twice ("this field goes stale every time a pass changes copy on a
# later calendar day") and prescribed bumping it by hand, which is a rule that
# needs a human to stay true.
#
# `today` has EXACTLY ONE consumer among the rules: R8 part (b), `v > today`,
# "is this published date in the FUTURE". The correct referent for "future" is
# NOW. A pin of yesterday makes part (b) ask a different and wrong question and
# turns every truthful date written today into a finding. So the default is now
# the wall clock, spelled "auto", and a fixed date is what you write when you
# MEAN a fixed date.
#
# THIS IS NOT A LOOSENING, and the direction of the effect is the proof:
# because part (b) is a strict `>`, moving the as-of FORWARD can only ever
# REMOVE hits, and every hit it removes is by construction a date that is not
# in the future. A genuinely invented future date stays caught forever --
# fixtures/R8c_future_review_date.html pins 2027-01-01 for exactly that reason.
# No other R8 part reads `today` at all: (a) and (d) compare against git, (c)
# compares surfaces against each other. So a wall-clock as-of cannot redden a
# green tree as the calendar rolls.
#
# DETERMINISM IS PRESERVED WHERE IT IS LOAD-BEARING. The replay harness pins
# its own as-of per row (`--today "$today"`, the fixing commit's date, in
# replay/replay.sh) and never reads this default; the control phase pins
# NEG_ASOF regardless of config. Both are unaffected by this change. What is
# no longer deterministic is an ordinary interactive run across midnight, and
# that is the right trade: the header has always stamped the as-of into the
# output, and a byte-identical report bought by asking the wrong question is
# not reproducibility, it is a preserved error.
ASOF_AUTO = "auto"


def resolve_asof(value):
    """Resolve an R8 as-of to an ISO date. Idempotent.

    `auto`, None or empty -> today's date from the system clock.
    An ISO date -> itself.
    Anything else -> ConfigError. It must NEVER fall through: R8 compares
    dates as STRINGS, and "2026-09-20" > "auto" is False, so an unresolved
    sentinel reaching part (b) would silently disable the future-date test
    instead of failing -- the same class of silent blinding this resolver
    exists to end.
    """
    import datetime as _dt
    if value is None or (isinstance(value, str) and not value.strip()):
        value = ASOF_AUTO
    if not isinstance(value, str):
        raise ConfigError("R8.today must be a string, got %r" % (value,))
    v = value.strip()
    if v.lower() == ASOF_AUTO:
        return _dt.date.today().isoformat()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        raise ConfigError(
            "R8.today %r is neither %r nor an ISO date (YYYY-MM-DD). R8 "
            "compares dates as STRINGS, so an unparseable value would "
            "silently disable the future-date test instead of failing."
            % (v, ASOF_AUTO))
    try:
        _dt.date(*[int(x) for x in v.split("-")])
    except ValueError as exc:
        raise ConfigError("R8.today %r is not a real calendar date (%s)"
                          % (v, exc))
    return v


def asof_staleness(resolved, source):
    """One line if the effective as-of is BEHIND the system clock, else "".

    A pin stays legal -- the replay harness needs it and a forensic re-run
    wants it -- but it may never be SILENT again. 246 findings on 2026-09-20
    were the gate mis-dating itself and nothing in its output said so.
    """
    import datetime as _dt
    wall = _dt.date.today().isoformat()
    if resolved >= wall:
        return ""
    try:
        drift = (_dt.date(*[int(x) for x in wall.split("-")])
                 - _dt.date(*[int(x) for x in resolved.split("-")])).days
    except ValueError:
        drift = -1
    return ("AS-OF IS STALE: this run is dated %s (%s) but the system clock "
            "reads %s -- %d day(s) behind. R8 part (b) fails any published "
            "date LATER than the as-of, so every page carrying a truthful "
            "date from the last %d day(s) will be reported as publishing a "
            "FUTURE date, and a genuinely invented future date becomes "
            "indistinguishable from a correct one. A pin is legitimate -- "
            "replay/replay.sh pins one per row on purpose -- but it is never "
            "silent. Set R8.today to %r, or pass --today %s."
            % (resolved, source, wall, drift, drift, ASOF_AUTO, wall))


# Config keys whose VALUES are compared against ONE SENTENCE from ctx.pool().
# Derived by reading every `for skey, loc, sent in ctx.pool(art)` loop in this
# file and following what each compares `sent` to. Deliberately over-inclusive
# on the rule side: a key wrongly listed costs nothing, a key wrongly omitted is
# the defect this check exists for.
SENTENCE_SCOPED_KEYS = {
    "R1": ("attribution_verbs", "quotation_allowlist", "correction_markers"),
    "R2": ("attribution_words", "allowed_multi_utility_sentences", "utilities",
           "programs", "non_territorial_programs", "forbidden_program_names",
           "locked_restriction_strings", "denial_markers", "qualifiers",
           "hedge_pairs", "allowlist", "electric_words",
           "tool_utility_questions"),
    "R3": ("money_words", "rank_words", "cost_context_markers",
           "code_context_markers", "allowed_figures", "attribution_words",
           "refusal_markers", "income_eligibility_markers"),
    "R4": ("stacking_tokens", "combination_predicates", "denial_markers",
           "programs", "program_aliases", "legitimate_uses"),
    "R5": ("magnitude_words", "recognised_publishers", "attribution_verbs",
           "derivable_constants", "publisher_short_forms",
           "subject_attribution_verbs", "publisher_artifact_nouns"),
    "R7": ("superseded_propositions", "superseded_identifiers",
           "correction_markers", "never_retire_on_403"),
    "R8": ("footer_marker",),
    "R9": ("claim_subjects", "value_slots", "tools"),
    "R10": ("promise_patterns", "refusal_markers", "page_titles"),
    "R11": ("tracked_terms", "patterns", "attributing_verbs"),
}
# Sub-keys inside those containers that are PROSE ANNOTATION and are never
# compared to a sentence. Without this exclusion the check reports fifteen
# `why` fields -- and a check that cries wolf on documentation hides the two
# rows that matter.
_ANNOTATION_KEYS = frozenset((
    "why", "reason", "basis", "note", "notes", "source", "comment",
    "provenance", "label", "id", "claim_id", "report_as", "polarity",
    "requires_publisher_named", "requires_cited_source_key",
    "and_the_figures_are_still_banned", "measured_at", "date",
    "verbatim_source", "retrieved", "text_note"))


def _pattern_strings(obj, path, out):
    if isinstance(obj, str):
        out.append((path, obj))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _pattern_strings(v, "%s[%d]" % (path, i), out)
    elif isinstance(obj, dict):
        for k in sorted(obj):
            if k in _ANNOTATION_KEYS or k.endswith("_note") \
                    or k.endswith("_reason") or k.endswith("_README") \
                    or k.endswith("_why"):
                continue
            _pattern_strings(obj[k], "%s.%s" % (path, k), out)


def unfirable_patterns(cfg):
    """Configured patterns a sentence-scoped rule can NEVER match.

    A rule that matches per sentence cannot fire on a pattern whose own text
    the splitter cuts in two. This is not hypothetical: `invoiced by Dec. 31,
    2026` and `installed and invoiced by Dec. 31` sat in R7's config, unfirable,
    and they are the very claim whose config note records that the SHORT form
    is what survived four earlier hand-written sweeps. The abbreviation guard
    closed those two; this check is what stops the next one being written.

    Returns (scanned, [(path, pattern, pieces), ...]).
    """
    scanned = 0
    bad = []
    seen = set()
    for rid, keys in sorted(SENTENCE_SCOPED_KEYS.items()):
        blk = cfg.get(rid) or {}
        if not isinstance(blk, dict):
            continue
        for key in keys:
            if key not in blk:
                continue
            out = []
            _pattern_strings(blk[key], "%s.%s" % (rid, key), out)
            for path, s in out:
                t = s.strip()
                scanned += 1
                if len(t) < 4 or not any(ch in t for ch in ".!?…"):
                    continue
                if t in seen:
                    continue
                pieces = S.sentences(t)
                if len(pieces) > 1:
                    seen.add(t)
                    bad.append((path, t, pieces))
    bad.sort()
    return scanned, bad


def unread_config_keys(cfg):
    """Config keys that appear NOWHERE as a literal in the implementation.

    A key with full provenance that no code path reads is a rule that silently
    does not exist -- the adversarial read counted 256 key names against 102
    actually referenced. Rather than hand-auditing that list once and letting it
    rot, the gate reads its OWN source and reports the difference every run.
    Self-maintaining: wire a key up and it leaves the list; add a key nobody
    reads and it appears.

    Keys whose name ends in a documentation suffix (_note, _reason, _basis,
    _source, _why) are provenance by construction and are not reported.
    """
    # HOLE 1: A KEY NAMED IN A COMMENT USED TO COUNT AS READ. The audit
    # substring-searched the raw source, so `# R5.derivable_constants is
    # declared and read by nothing` marked that key as read -- live for three
    # canon entries at the time this was found. An audit that a comment can
    # satisfy is an audit a comment can defeat. The implementation is now
    # TOKENIZED and only real STRING LITERALS count; COMMENT tokens are
    # discarded outright, and a literal long enough to be prose (>60 chars) is
    # discarded too, because that is a docstring, not a key lookup.
    lits = set()
    try:
        srcs = [os.path.abspath(__file__), os.path.join(_HERE, "surfaces.py")]
        for path in srcs:
            with open(path, "rb") as fh:
                for tok in tokenize.tokenize(fh.readline):
                    if tok.type != tokenize.STRING:
                        continue
                    try:
                        v = ast.literal_eval(tok.string)
                    except Exception:
                        continue
                    if isinstance(v, str) and 0 < len(v) <= 60:
                        lits.add(v)
    except OSError:
        return [], [], []
    # DATA CONTAINERS hold values keyed by town, alias, slug or document field.
    # Their DIRECT children are data, not behaviour, so reporting them would
    # name "R2.towns.Ault" as an unread rule. Everything BELOW that level is
    # behavioural again -- "R2.towns.Ault.substring_trap" is a key somebody
    # expected to do something -- so the walk RECURSES FULLY and only declines
    # to report the container's own first level.
    DATA = ("towns", "utility_aliases", "utility_domains", "program_aliases",
            "page_titles", "pinned_pages", "allowed_occurrences",
            "current_replacements", "tariff_identity", "value_slots",
            "boundary_inclusivity", "targets", "r6b_inputs", "expected",
            "measured_at", "own_effective_date_values",
            "known_holds", "label_chains", "claim_subjects",
            "superseded_propositions", "retired_propositions",
            "tracked_terms", "anomalies",
            "deliberate_divergence", "deliberate_edition_divergence",
            "tools", "draft_gate", "known_uncited", "hedge_pairs",
            "documentation_only_keys")
    unread = []
    empties = []

    def audit(node, path, in_data):
        if isinstance(node, list):
            for e in node:
                audit(e, path + "[]", in_data)
            return
        if not isinstance(node, dict):
            return
        for k in sorted(node):
            if not isinstance(k, str):
                continue
            low = k.lower()
            if k.startswith("_") or any(
                    low.endswith("_" + p) for p in _DOC_PREFIXES):
                continue
            full = "%s.%s" % (path, k) if path else k
            if not in_data:
                if k not in lits:
                    unread.append(full)
            # HOLE 3: THE AUDIT NEVER LOOKED AT VALUES. A key the code reads
            # whose value is EMPTY configures a rule that cannot fire --
            # emptying R5.magnitude_words leaves the audit green at 0 OWED
            # while the rule goes blind. Reported separately from OWED,
            # because an empty list is sometimes a deliberate null result.
            if not in_data and k in lits:
                v = node[k]
                if isinstance(v, (list, dict, str)) and len(v) == 0:
                    empties.append(full)
            audit(node[k], full, k in DATA)

    audit(cfg, "", False)
    # A DECLARATION MUST CARRY A JUSTIFICATION. As a bare LIST, naming a key
    # moved it out of OWED with no check that it is documentation, and because
    # _deep_merge REPLACES a list, one child declaration silently un-declared
    # the parent's entire set. As a DICT of {key: why}, _deep_merge UNIONS it
    # across the extends chain for free, and a declaration with an empty or
    # trivial justification does not count.
    decl = cfg.get("documentation_only_keys", {}) or {}
    if isinstance(decl, list):
        decl = dict((k, "") for k in decl)
    # A JUSTIFICATION MUST BE SOMETHING A HUMAN WROTE. A pure LENGTH test let
    # 21 characters of "xxxxxxxxxxxxxxxxxxxxx" move a behavioural key out of
    # OWED. Require several DISTINCT words of real length -- which is what the
    # genuine declarations already look like, each naming where the enforceable
    # half lives.
    def _justified(v):
        if not isinstance(v, str):
            return False
        words = re.findall(r"[A-Za-z][A-Za-z'\-]{2,}", v)
        return len(set(w.lower() for w in words)) >= 6 and len(v.strip()) >= 40

    good = set(k for k, v in decl.items() if _justified(v))
    thin = sorted(k for k, v in decl.items() if k not in good)

    # HOLE 2: A BARE-LEAF DECLARATION SILENCED EVERY RULE'S COPY OF THAT KEY.
    # `u.split(".")[-1] in good` meant declaring the leaf `refusal_markers`
    # silenced R3's AND R10's, so one justified exemption bought an unbounded
    # number of unjustified ones. A bare leaf now covers a key only when
    # EXACTLY ONE unread key carries that leaf name -- otherwise it is
    # ambiguous and the full dotted path must be written.
    leaf_count = {}
    for u in unread:
        leaf_count[u.split(".")[-1]] = leaf_count.get(u.split(".")[-1], 0) + 1

    def _declared(u):
        if u in good:
            return True
        leaf = u.split(".")[-1]
        return leaf in good and leaf_count.get(leaf, 0) == 1

    owed = sorted(set(u for u in unread if not _declared(u)))
    noted = sorted(set(u for u in unread if _declared(u)))
    # Only warn where the bare leaf is actually LOAD-BEARING: several unread
    # keys share it AND at least one of them is not declared by its own full
    # path. A leaf that happens to collide while every colliding key is
    # separately declared is not ambiguous, it is fully specified.
    ambiguous = sorted(set(
        u.split(".")[-1] for u in unread
        if u.split(".")[-1] in good
        and leaf_count.get(u.split(".")[-1], 0) > 1
        and u not in good))
    return owed, noted, thin, sorted(set(empties)), ambiguous


def enumerate_corpus(repo, cfg):
    c = Corpus()
    # -z: without it git C-QUOTES any path with a non-ASCII byte, so a
    # perfectly consistent repo DIVERGED against the working tree and the gate
    # exited 2. core.quotePath=false would also work; -z is stronger because it
    # also survives a newline in a filename.
    out = git(repo, "-c", "core.quotePath=false", "ls-files", "-z", "public/")
    if out is None:
        raise ConfigError(
            "`git ls-files public/` failed in %s -- the corpus contract "
            "(spec 2) requires both halves" % repo)
    c.ls_files = sorted(x for x in out.split("\x00") if x.strip())
    pub = os.path.join(repo, "public")
    if not os.path.isdir(pub):
        raise ConfigError("no public/ directory in %s" % repo)
    found = []
    repo_real = os.path.realpath(repo)
    for root, dirs, files in os.walk(pub, followlinks=False):
        dirs.sort()
        dirs[:] = [d for d in dirs
                   if not os.path.islink(os.path.join(root, d))]
        for f in sorted(files):
            full = os.path.join(root, f)
            rel = os.path.relpath(full, repo).replace(os.sep, "/")
            # A symlink pointing OUT of the repo is not this property's
            # artifact. One such link made a DCI page read as a GCI artifact.
            if os.path.islink(full):
                tgt = os.path.realpath(full)
                if not (tgt == repo_real or tgt.startswith(repo_real + os.sep)):
                    c.escaping_symlinks.append("%s -> %s" % (rel, tgt))
                    continue
            found.append(rel)
    c.found = sorted(found)
    only_git = sorted(set(c.ls_files) - set(c.found))
    only_tree = sorted(set(c.found) - set(c.ls_files))
    if only_git or only_tree:
        c.agree = False
        for r in only_git:
            c.divergence.append("tracked but absent from the working tree: %s" % r)
        for r in only_tree:
            c.divergence.append("in the working tree but untracked: %s" % r)

    key_excl = set(cfg.get("key_files_excluded", []))
    for rel in sorted(set(c.ls_files) | set(c.found)):
        low = rel.lower()
        if rel in key_excl:
            c.excluded.append((rel, "indexnow-key-file"))
            continue
        if low.endswith(BINARY_EXT):
            c.excluded.append((rel, "binary-raster"))
            continue
        c.read_set.append(rel)
    return c


# ---------------------------------------------------------------------------
# git facts for R8 (a non-artifact input, spec R8)
# ---------------------------------------------------------------------------

DATE_LINE_PAT = re.compile(
    r"Last reviewed|<lastmod>|datetime=\"\d{4}-\d{2}-\d{2}\""
    r"|\"dateModified\"|\"datePublished\"")


class GitFacts(object):
    """Per-file first-appearance and last VISIBLE-TEXT change, with the
    review-date line itself stripped so it cannot count as its own change --
    GCI 348baf9 hit that exact false positive and solved it this way."""

    def __init__(self, repo=None, cap=15):
        self.repo = repo
        self.cap = cap
        self.commits = {}
        self.first_seen = {}
        self._content = {}
        self._sidecar = {}
        self.available = False
        self.capped = []
        self._proc = None

    def load(self, repo, rels):
        self.repo = repo
        out = git(repo, "log", "--format=@@@%H|%cI", "--name-only", "--", "public/")
        if out is None:
            return
        self.available = True
        sha = date = None
        for line in out.splitlines():
            if line.startswith("@@@"):
                body = line[3:]
                sha, _, date = body.partition("|")
                date = date[:10]
            elif line.strip():
                self.commits.setdefault(line.strip(), []).append((sha, date))
        for rel, lst in self.commits.items():
            self.first_seen[rel] = lst[-1][1]

    def _batch(self):
        if getattr(self, "_proc", None) is None:
            try:
                self._proc = subprocess.Popen(
                    ["git", "cat-file", "--batch"], cwd=self.repo,
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL)
            except OSError:
                self._proc = False
        return self._proc

    def blob(self, sha, rel):
        """One long-lived `git cat-file --batch` instead of a subprocess per
        blob. 75 files x 2 blobs was 150 forks and most of the wall clock."""
        p = self._batch()
        if not p:
            out = git(self.repo, "show", "%s:%s" % (sha, rel))
            return out or ""
        try:
            p.stdin.write(("%s:%s\n" % (sha, rel)).encode())
            p.stdin.flush()
            header = p.stdout.readline().decode("utf-8", "replace").strip()
            if header.endswith("missing") or " " not in header:
                return ""
            parts = header.split()
            size = int(parts[-1])
            data = p.stdout.read(size)
            p.stdout.read(1)
            return data.decode("utf-8", "replace")
        except Exception:
            return ""

    def close(self):
        p = getattr(self, "_proc", None)
        if p:
            try:
                p.stdin.close()
                p.wait(timeout=5)
            except Exception:
                pass
            self._proc = None

    def last_content_change(self, rel):
        if rel in self._content:
            return self._content[rel]
        lst = self.commits.get(rel) or []
        answer = None
        for i, (sha, date) in enumerate(lst[:self.cap]):
            cur = self.blob(sha, rel)
            parent = self.blob(sha + "^", rel)
            if _differs_outside_date_lines(cur, parent):
                answer = date
                break
        if answer is None and lst:
            if len(lst) > self.cap:
                self.capped.append(rel)
            answer = lst[min(len(lst), self.cap) - 1][1]
        self._content[rel] = answer
        return answer

    # control mode: sidecar facts, so a control needs no repo
    def add_sidecar(self, rel, facts):
        self._sidecar[rel] = facts
        if "first_seen" in facts:
            self.first_seen[rel] = facts["first_seen"]
        if "last_visible_change" in facts:
            self._content[rel] = facts["last_visible_change"]
        self.available = True


def _differs_outside_date_lines(a, b):
    la = [x for x in a.splitlines() if not DATE_LINE_PAT.search(x)]
    lb = [x for x in b.splitlines() if not DATE_LINE_PAT.search(x)]
    return la != lb


# ---------------------------------------------------------------------------
# Matching primitives. Occurrences, never lines. Word boundaries, and a
# known-present control (spec 3).
# ---------------------------------------------------------------------------

def _wb(term):
    t = re.escape(term)
    lead = r"\b" if term[:1].isalnum() else ""
    tail = r"\b" if term[-1:].isalnum() else ""
    return lead + t + tail


_PAT_CACHE = {}


def _pat(term, ci, word):
    k = (term, ci, word)
    p = _PAT_CACHE.get(k)
    if p is None:
        p = re.compile(_wb(term) if word else re.escape(term),
                       re.IGNORECASE if ci else 0)
        _PAT_CACHE[k] = p
    return p


def occ(text, term, ci=True, word=True):
    return [m.start() for m in _pat(term, ci, word).finditer(text)]


def has(text, term, ci=True, word=True):
    return _pat(term, ci, word).search(text) is not None


_ANY_CACHE = {}


def _any_pat(terms, ci, word):
    """One compiled alternation per (term list, ci, word). 4.8 million
    single-term searches becomes 600 thousand alternation searches."""
    key = (tuple(terms), ci, word)
    p = _ANY_CACHE.get(key)
    if p is None:
        real = [t for t in terms if t]
        if not real:
            p = False
        else:
            real.sort(key=len, reverse=True)
            alt = "|".join(_wb(t) if word else re.escape(t) for t in real)
            p = re.compile(alt, re.IGNORECASE if ci else 0)
        _ANY_CACHE[key] = p
    return p


def has_any(text, terms, ci=True, word=True):
    p = _any_pat(terms, ci, word)
    if not p:
        return False
    return p.search(text) is not None


def which_any(text, terms, ci=True, word=True):
    out = []
    for t in terms:
        if t and has(text, t, ci, word):
            out.append(t)
    return sorted(set(out))


def win(text, pos, n):
    return text[max(0, pos - n):pos + n]


# A URL IS AN ADDRESS, NOT A PROPOSITION.
#
# A slug is chosen for search, and a word inside one asserts nothing. Both of
# DCI's two standing R4 findings (2026-09-18) were URL text read as prose:
#
#   public/llms.txt          '- [WHE Bonus Guide](https://denvercoloradoinsul
#                             ation.com/whole-home-efficiency-bonus-stacking-
#                             denver.html): The 25% bonus turns on ...'
#   src:_educational_pages.py '... the <a href="/whole-home-efficiency-bonus-
#                             stacking-denver.html">Whole Home Efficiency
#                             Bonus</a> adding a 25% bonus ...'
#
# In BOTH, the token `stacking` occurs exactly once in the sentence and that
# occurrence is inside the URL: masking the URL takes the count 1 -> 0. The
# page those URLs point at carries the same defect in its own surfaces -- on
# whole-home-efficiency-bonus-stacking-denver.html, across all 608 surfaces,
# `stack`/`stacking` appear in 0 prose surfaces and 6 url-valued ones (its own
# canonical link[href], og:url, and four JSON-LD fields: mainEntityOfPage.@id,
# url, breadcrumb itemListElement[2].item, and a second url), while `bonus`
# has 48 prose surfaces, `rebate` 42 and `Xcel` 37 on the same page.
#
# SPANS, NOT SURFACES. Dropping url-VALUED surfaces would cure the six-surface
# half and neither of the two live findings, because in both of those the URL
# is EMBEDDED in a prose sentence -- a markdown link target, and an href inside
# HTML held in generator source. Masking the span covers both: a surface whose
# whole value is a URL masks to blank, and a prose sentence keeps its prose.
#
# Replacement is spaces of the SAME LENGTH, so every offset in the masked text
# still indexes the original -- R4's single-program branch reads positions out
# of one and windows out of the other.
_URL_SPAN = re.compile(
    r"""(?xi)
      (?:https?|ftp)://[^\s"'<>()\[\]]*                  # scheme-led, absolute
    | (?:mailto|tel):[^\s"'<>()\[\]]*                    # non-slashed schemes
    | (?<![A-Za-z0-9])//[A-Za-z0-9.-]+/[^\s"'<>()\[\]]*  # protocol-relative
    | (?<=["'(])/[^\s"'<>()\[\]]*                        # quoted root-relative
    | (?<![A-Za-z0-9./?#-])
      /?[A-Za-z0-9._~%+-]+(?:/[A-Za-z0-9._~%+-]+)*
      \.(?:html?|xml|txt|svg|png|jpe?g|webp|gif|css|js)
      (?![A-Za-z0-9])                                    # bare or rooted slug
    """)


def mask_urls(text):
    """`text` with every URL span replaced by spaces of the same length.

    Length-preserving on purpose: see _URL_SPAN. Returns `text` unchanged when
    it holds no URL, so callers can test `masked is not text` cheaply.
    """
    if not text:
        return text
    return _URL_SPAN.sub(lambda m: " " * (m.end() - m.start()), text)


def names_in(text, names, aliases=None, ci=True):
    """Canonical names present in `text`, longest-first, SPAN-CONSUMING.

    Two properties this needs and `which_any` does not have:

      * case-insensitive by default. `atmos energy` in lowercase was invisible
        to R2 and `R4.programs` had the same hole (ci=False everywhere).
      * a matched span is CONSUMED, so a shorter name that overlaps a longer
        one already matched does not count again. Without this, adding bare
        "Xcel" beside "Xcel Energy" would let one mention of Xcel Energy
        satisfy R4's two-distinct-programs requirement by itself.

    Town names deliberately do NOT come through here: they stay
    word-boundary-anchored and CASE-SENSITIVE, because `grep -ci 'ault'` gives
    8 where the locality Ault appears once.
    """
    aliases = aliases or {}
    spans = []
    found = []
    # SEARCH THE ALIASES TOO, not just canonicalise with them. Until
    # 2026-09-18 this loop ran over `names` alone and used `aliases` purely as
    # a lookup for terms that were ALREADY in `names` -- so "Xcel" -> "Xcel
    # Energy" worked only because bare "Xcel" is itself in R4.programs, and an
    # alias naming something absent from the list was never searched for at
    # all. That is why GCI's FAQPage denial resolved one program instead of
    # two: the page said "the free state weatherization program" and the list
    # held only the literal "Colorado Weatherization Assistance Program".
    # Longest-first plus span-consumption still applies across the union, so a
    # canonical name always beats a shorter alias overlapping it.
    terms = set(t for t in names if t) | set(a for a in aliases if a)
    for term in sorted(terms, key=len, reverse=True):
        for m in _pat(term, ci, True).finditer(text):
            a, b = m.start(), m.end()
            if any(a < y and b > x for x, y in spans):
                continue
            spans.append((a, b))
            found.append(aliases.get(term, term))
    return sorted(set(found))


# ---------------------------------------------------------------------------
# Context: the parsed corpus plus the claim set (spec 2)
# ---------------------------------------------------------------------------

GEN_MODULES = (
    "_shared_components.py", "_area_pages.py", "_generate_area_pages.py",
    "_generate_calculator_pages.py", "_service_pages.py",
    "_generate_service_pages.py", "_educational_pages.py",
    "_generate_educational.py", "_generate_homepage.py",
    "_generate_llms_txt.py", "_generate_brand_assets.py",
    "_generate_rebate_hub.py", "_generate_resources.py",
    "_page_template.py", "_generate_suburb_pages.py",
)

CLAIM_KEYS = (S.S_VIS, S.S_TITLE, S.S_META, S.S_OG, S.S_TW, S.S_LD,
              S.S_LOWVIS, S.S_ATTR, S.S_LLMS, S.S_SVGTEXT, S.S_CITE,
              S.S_CONST, S.S_JS, S.S_COMMENT, S.S_CSS, S.S_SITEMAP)

REGISTRY_REL = "docs/citation-registry.json"


class Registry(object):
    """The property's own docs/citation-registry.json, read for R7.

    R7 printed DEGRADED on every run because the supersession record lived
    ONLY in the gate's own config: a tool asserting a list it also owns is
    not checking the property, it is checking itself. The registry now
    carries `superseded_by: {id, on, reason}` on a tombstone entry per
    retired document, and a top-level `schema.supersession_declared` flag so
    that an ABSENT superseded_by is a positive statement ("reviewed on this
    date, current") rather than silence the gate would have to guess about.

    Read-only, and never read inside a control context -- controls get the
    value pinned on the config by run_controls, exactly as ctx.gen is.
    """

    def __init__(self):
        self.path = ""
        self.present = False
        self.parse_error = ""
        self.declared = False
        self.declared_on = ""
        self.entries = 0
        self.superseded = []      # [{id, identifiers[], url, on, by, reason}]
        self.undeclared_ids = []  # entries with no superseded_by (= current)


def read_citation_registry(repo):
    reg = Registry()
    reg.path = os.path.join(repo, REGISTRY_REL)
    if not os.path.isfile(reg.path):
        return reg
    reg.present = True
    try:
        with open(reg.path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:
        reg.parse_error = "%s: %s" % (exc.__class__.__name__, exc)
        return reg
    if not isinstance(data, dict):
        reg.parse_error = "top level is %s, not an object" % type(data).__name__
        return reg
    schema = data.get("schema") or {}
    reg.declared = bool(schema.get("supersession_declared"))
    reg.declared_on = str(schema.get("supersession_declared_on") or "")
    for bucket in ("sources", "unwatchable_sources"):
        for e in data.get(bucket) or []:
            if not isinstance(e, dict):
                continue
            reg.entries += 1
            sb = e.get("superseded_by")
            if not isinstance(sb, dict):
                reg.undeclared_ids.append(str(e.get("id") or "?"))
                continue
            idents = [x for x in (e.get("identifiers") or [])
                      if isinstance(x, str) and x.strip()]
            reg.superseded.append({
                "id": str(e.get("id") or "?"),
                "identifiers": sorted(set(idents)),
                "url": str(e.get("url") or ""),
                "by": str(sb.get("id") or ""),
                "on": str(sb.get("on") or ""),
                "reason": str(sb.get("reason") or ""),
            })
    reg.superseded.sort(key=lambda d: d["id"])
    reg.undeclared_ids.sort()
    return reg

# The sentence pool every proposition rule runs over. VIS comes from the
# whole-document TXT (so a sentence that runs through <strong> or a source line
# break is ONE sentence, which is the entire point of TXT); every other surface
# contributes its own text with its own locator, because surface attribution is
# what told DCI its page contradicted its own navigation.
POOL_KEYS = (S.S_TITLE, S.S_META, S.S_OG, S.S_TW, S.S_LD, S.S_JS, S.S_ATTR,
             S.S_LLMS, S.S_ROBOTS, S.S_SVGTEXT, S.S_CITE, S.S_CONST,
             S.S_LOWVIS, S.S_COMMENT, S.S_CSS, S.S_SITEMAP, S.S_SRC)


class Ctx(object):
    def __init__(self, key, repo, cfg, control=False):
        self.key = key
        self.repo = repo
        self.cfg = cfg
        self.control = control
        self.artifacts = []
        self.by_rel = {}
        self.gen = S.GeneratorFacts()
        self.registry = Registry()
        # Cited-stat blocks whose registry key could not be resolved.
        # Reported, never guessed at: binding one to the nearest
        # candidate is what spliced the CFM 50 sentence onto nine DCI
        # pages that do not contain it.
        self.unresolved_cited_stats = []
        self.gitfacts = GitFacts()
        self.claim_extra = {}
        self.corpus = None
        # Resolved, never a raw literal: see resolve_asof(). A hardcoded
        # "2026-09-17" used to live here as the fallback, which is the same
        # silently-ageing defect the config carried.
        self.today = resolve_asof(cfg.get("R8", {}).get("today"))
        self._script_spans = {}
        self._svg_text = {}
        self._pool = {}
        self._levels_cache = {}
        self.src_artifacts = []
        self.src_code_surfaces = []   # (rel, locator, chars) code runs in pool
        self.src_code_locators = set()
        self._rendered = None
        self.peer_ctx = None

    # ---- config access
    def r(self, rid):
        return self.cfg.get(rid, {}) or {}

    # ---- artifact selection
    def read_artifacts(self):
        return self.artifacts

    def rendered_index(self):
        """One concatenated blob of everything that actually RENDERS into
        public/, used to tell a generator-side finding that adds information
        from one that merely restates a rendered page."""
        if getattr(self, "_rendered", None) is None:
            parts = []
            for a in self.artifacts:
                if a.kind == "src":
                    continue
                parts.append(a.txt)
                for _, lit in a.js_strings:
                    parts.append(S.collapse(S.dec(S.txt(lit))))
                for sf in a.surfaces:
                    parts.append(sf.text)
            self._rendered = " \u0001 ".join(parts)
        return self._rendered

    def src_dup(self, hit):
        """True when an SRC-sourced hit's text ALREADY renders in public/.

        Wiring SRC (Ruling B) immediately produced a flood on DCI R5: 107 new
        adjudicated hits, essentially all of them _educational_pages.py prose
        that renders verbatim into public/ and was therefore already counted
        once against the rendered artifact. Double-counting one claim is not
        coverage.

        What SRC is FOR is the claim that is NOT visible in the rendered
        corpus: a string split across Python implicit concatenation
        (REBATE_ACKNOWLEDGMENT reads "...the primary rebate " "stack for
        Denver-area..."), and the pre-render form of a claim a page assembles at
        runtime -- DCI's `Dec. 31, 2026` at _generate_calculator_pages.py:344,
        which stayed outside the claim corpus for four rounds. Those survive
        this filter; a restatement of rendered prose does not.
        """
        if not str(hit.rel).startswith("src:"):
            return False
        # THE PROBE MUST BE NORMALIZED THE WAY THE INDEX IS.
        # rendered_index() is built from `a.txt`, which is collapse(dec(...))
        # with script/style bodies dropped and remaining TAGS STRIPPED -- so
        # every em dash is folded to "-" and no markup survives. The probe was
        # collapse() ONLY, straight off the generator byte string. Any hit
        # whose first 48 characters contained an HTML tag or a typographic
        # dash therefore could not match a rendered page that contains the
        # sentence verbatim: the filter was comparing two different alphabets.
        # Measured on DCI at ba2fc22 -- of the seven SRC findings R5 carried,
        # SIX were prose that renders in public/ and one (the ENERGY STAR
        # Climate Zone 5 registry stat, which renders on no page) was real.
        # Portfolio-wide the unnormalized probe missed 106 distinct SRC
        # restatements. NEG15 is the control: correct copy, markup and an em
        # dash inside the first 48 characters.
        # THE 48-CHARACTER PREFIX WAS A LIVE SILENT MISS. CLOSED 2026-09-19.
        # Two generator strings sharing their first 48 normalized characters
        # were indistinguishable to this probe, so a string whose OPENING
        # matched rendered prose was cleared no matter what it went on to
        # assert. Reproduced by injecting into _shared_components.py a string
        # that renders NOWHERE and carries a fresh uncited figure:
        #     '<p>Loose-fill cellulose settles 10 to 20 percent; rebate
        #      paperwork cuts your bill by 47% in the first year.</p>'
        # whose first 48 normalized characters are DCI's real, attributed
        # settling sentence.
        #     prefix probe:        DCI R5 ADJ 31 -- CLEARED, MISSED
        #     full-sentence probe: DCI R5 ADJ 33 -- CAUGHT
        # The repair is this expression with NO SLICE. A previous pass applied
        # it and had to REVERT it, because it reddened LGM -- which is wired
        # into that property's regen_all.sh under `set -e` -- with two rows
        # that were a DIFFERENT, pre-existing R5 defect the prefix had been
        # accidentally masking: CODE READ AS PROSE on the SRC surface.
        # That defect is now fixed in its own right (see _src_is_code), so the
        # slice comes off. ORDER MATTERS AND WAS OBSERVED: the code/prose split
        # landed first, then this.
        probe = S.collapse(S.txt(hit.sentence))
        if len(probe) < 20:
            return False
        return probe in self.rendered_index()

    def src_rules(self):
        return set(self.cfg.get("src_rules", []) or [])

    def rule_artifacts(self, rid):
        """Claim artifacts, plus the generator SRC pseudo-artifacts for the
        rules config.src_rules names.

        DELIBERATELY NOT R3's T1/T2 numeral halves: the generators embed the
        citation registry's own deliberately-kept dollar figures (DCI 7786ce5
        records why the registry keeps them), so feeding SRC to a $-anchored
        or bare-numeral scan would flood it with figures that are correct
        where they sit. R3's T3 rank-claim half DOES read SRC, because
        "the largest rebate" lived in _generate_service_pages.py's
        CROSS_CONTEXT['attic'] and shipped to six pages from there.
        """
        base = self.claim_artifacts()
        if rid in self.src_rules():
            return base + self.src_artifacts
        return base

    def claim_artifacts(self):
        # .xml included: sitemap.xml is a deployed artifact and its prose and
        # comments are claim surfaces. Excluding it meant R3 advertised
        # SITEMAP in its own surfaces: line while no proposition rule could
        # reach the file.
        return [a for a in self.artifacts
                if a.kind in ("html", "txt", "svg", "js", "xml")]

    def html_artifacts(self):
        return [a for a in self.artifacts if a.kind == "html"]

    def surfaces(self, art, keys):
        out = art.stream(keys)
        for s in self.claim_extra.get(art.rel, []):
            if s.key in keys:
                out.append(s)
        return out

    def pool(self, art):
        """(surface_key, locator, sentence) for every claim-bearing surface,
        built ONCE per artifact and shared by every proposition rule."""
        if art.rel in self._pool:
            return self._pool[art.rel]
        out = []
        if art.kind == "html":
            # txt_blocks, not txt: identical bytes plus block-boundary
            # sentinels, so a <nav> cannot weld itself onto the first sentence
            # of body prose. See surfaces._BLOCK_TAGS.
            for sent in S.sentences(art.txt_blocks):
                out.append((S.S_VIS, "txt", sent))
        else:
            # A non-HTML artifact's own surfaces include S_VIS, which is NOT in
            # POOL_KEYS (it comes from art.txt for HTML). Without this, any
            # deployed .txt that is not llms.txt or robots.txt reached no
            # proposition rule at all.
            for sf in self.surfaces(art, (S.S_VIS,)):
                for sent in (S.sentences(sf.text) or [sf.text]):
                    out.append((S.S_VIS, sf.locator, sent))
        for s in self.surfaces(art, POOL_KEYS):
            if s.key in (S.S_JS, S.S_CSS) and s.locator.endswith("body"):
                continue
            # THE SAME POLICY, ON THE SRC SURFACE -- BUT NEVER AS A DELETION.
            #
            # The line above says a <script> or <style> BODY is not a
            # proposition surface on a rendered page; only the string LITERALS
            # inside it are. The SRC surface had no such rule, so a generator's
            # stylesheet and its script bundles arrived as ordinary prose and
            # every proposition rule read their numerals and their DEVELOPER
            # COMMENTS as claims. Measured, on the same bytes:
            #   public/insulation-rebate-eligibility-checker.html  R2 clean
            #   src:_generate_calculator_pages.py                  R2 FAIL
            # on one JS comment recording a wrong-utility bug FIXED on
            # 2026-09-08 -- the repair note read as the defect.
            #
            # A PREVIOUS REVISION OF THIS BLOCK DROPPED THE SURFACE HERE WITH A
            # BARE `continue`, AND THAT WAS A REGRESSION IN A BLOCKING RULE.
            # The seventh adversarial read proved it: R2 (wrong utility), R4
            # (stacking) and R7 (superseded source) all read SRC, and a claim
            # written into a generator string that also contained a stylesheet
            # went from RAW 1 / ADJ 1 / exit 1 to RAW 0 / ADJ 0 / exit 0 with no
            # finding raised and no filter row to read. 189,985 characters left
            # the pool across three live properties as an unattributed byte
            # tally naming no rule and no hit. A removal nobody can attribute is
            # indistinguishable from a rule going blind.
            #
            # SO THE SURFACE IS KEPT AND THE POOL DOES TWO THINGS INSTEAD:
            #   1. it still emits the code run's own sentences, so every rule
            #      RAISES the hit and then removes it through a NAMED, COUNTED,
            #      ENUMERATED filter of its own (see `f_srccode` in each rule);
            #   2. it ADDITIONALLY emits the QUOTED STRING LITERALS inside the
            #      run, under a distinct `#strN` locator, because that is
            #      exactly what the rendered page reads out of the same bytes.
            #      A wrong-utility claim assigned to `el.innerHTML` inside a
            #      script bundle is a claim, and it is now judged as one.
            if art.kind == "src" and _src_is_code(s.text):
                self.src_code_locators.add(s.locator)
                self.src_code_surfaces.append((art.rel, s.locator, len(s.text)))
                for sent in (S.sentences(s.text) or [s.text]):
                    out.append((s.key, s.locator, sent))
                for i, lit in enumerate(_src_code_literals(s.text)):
                    loc = "%s#str%d" % (s.locator, i)
                    for sent in (S.sentences(lit) or [lit]):
                        out.append((s.key, loc, sent))
                continue
            for sent in (S.sentences(s.text) or [s.text]):
                out.append((s.key, s.locator, sent))
        self._pool[art.rel] = out
        return out

    def src_code_hit(self, hit):
        """True when a hit was raised against a generator string run that is a
        stylesheet or a script BODY rather than prose.

        EXACT locator match on purpose: the string literals lifted out of that
        same run carry a `#strN` suffix and are NOT excluded, so the claim
        inside a bundle survives while the bundle's syntax and its developer
        comments do not."""
        return str(getattr(hit, "locator", "")) in self.src_code_locators

    def script_spans(self, art, level=S.NORM_RAW):
        """Document-level spans of <script>, <style> and CSS `content:` string
        values, per normalization level -- DEC shifts every offset after an
        entity, so the spans must be computed against the same text the rule
        scanned."""
        key = (art.rel, level)
        if key in self._script_spans:
            return self._script_spans[key]
        text = art.level_text(level)
        spans = []
        for m in re.finditer(
                r"<script\b([^>]*)>(.*?)</script\s*>", text,
                re.DOTALL | re.IGNORECASE):
            kind = "LD" if "ld+json" in m.group(1).lower() else "JS"
            spans.append((m.start(), m.end(), kind))
        for m in re.finditer(r"<style\b[^>]*>(.*?)</style\s*>", text,
                             re.DOTALL | re.IGNORECASE):
            spans.append((m.start(), m.end(), "CSS"))
            body = m.group(1)
            base = m.start(1)
            for cm in S._CSS_CONTENT.finditer(body):
                # `content:` renders TEXT to the visitor. A figure there is a
                # figure the visitor sees, so it must not share a filter with
                # a stroke-width. Position-based, because a window test let an
                # adjacent stroke-width ride in on the same window.
                spans.append((base + cm.start("v"), base + cm.end("v"),
                              "CSS-CONTENT"))
        spans.sort(key=lambda x: (x[0], -(x[1] - x[0])))
        self._script_spans[key] = spans
        return spans

    def surface_at(self, art, pos, level=S.NORM_RAW):
        hit = "RAW"
        for a, b, k in self.script_spans(art, level):
            if a <= pos < b:
                hit = k
        return hit

    # ---- town scope / utilities (R2)
    def own_towns(self, art):
        """Towns whose OWN page this is, by the config's slug map -- never by
        whether the town name appears in the title. GCI's fourth town-blind
        calculator was missed because its <h1> is the only one of five without
        'Greeley'."""
        c = self.r("R2")
        towns = c.get("towns", {}) or {}
        base = art.rel.rsplit("/", 1)[-1]
        return sorted(n for n in towns
                      if base in (towns[n].get("page_slugs") or []))

    def town_scope(self, art):
        c = self.r("R2")
        towns = c.get("towns", {}) or {}
        hit = set(self.own_towns(art))
        if hit:
            return sorted(hit)
        # JSON-LD areaServed + the <h1>
        names = set()
        for path, val in art.ld_leaves:
            if "areaServed" in path and val in towns:
                names.add(val)
        m = re.search(r"<h1\b[^>]*>(.*?)</h1\s*>", art.raw, re.DOTALL | re.I)
        h1 = S.txt(m.group(1)) if m else ""
        for name in sorted(towns):
            variants = [name] + list(towns[name].get("spelling_variants") or [])
            if any(has(h1, v, ci=False) for v in variants):
                names.add(name)
        return sorted(names)

    def canon_utility(self, name):
        c = self.r("R2")
        al = c.get("utility_aliases", {}) or {}
        return al.get(name, name)

    def utilities_in(self, text):
        """Canonical utilities named in `text`. `Xcel` and `Xcel Energy` are
        ONE utility; matching the short form and then testing it against a
        long-form allow-list is how a single-utility property manufactures
        1,859 findings about itself."""
        c = self.r("R2")
        return names_in(text, c.get("utility_names", []) or [],
                        c.get("utility_aliases", {}) or {}, ci=True)

    def programs_in(self, text):
        """Canonical R4 program names present in `text`, span-consuming."""
        c = self.r("R4")
        return names_in(text, c.get("programs", []) or [],
                        c.get("program_aliases", {}) or {}, ci=True)

    def utility_spots(self, text):
        """(canonical utility, position) for every utility MENTION in `text`,
        span-consuming and alias-aware. Positions are what clause-level
        resolution needs and utilities_in() does not give."""
        c = self.r("R2")
        names = sorted((n for n in (c.get("utility_names") or []) if n),
                       key=len, reverse=True)
        al = c.get("utility_aliases", {}) or {}
        spans = []
        out = []
        for term in names:
            for m in _pat(term, True, True).finditer(text):
                a, b = m.start(), m.end()
                if any(a < y and b > x for x, y in spans):
                    continue
                spans.append((a, b))
                out.append((al.get(term, term), a))
        return sorted(set(out), key=lambda t: (t[1], t[0]))

    def town_spots(self, text):
        """(town, position) for every town MENTION, case-sensitive and
        word-boundary, spelling_variants honoured."""
        c = self.r("R2")
        towns = c.get("towns", {}) or {}
        out = []
        for name in sorted(towns):
            for v in [name] + list(towns[name].get("spelling_variants") or []):
                for pos in occ(text, v, ci=False):
                    out.append((name, pos))
        return sorted(set(out), key=lambda t: (t[1], t[0]))

    def towns_near(self, text, pos, radius=100):
        """Towns named within `radius` characters of `pos`.

        Case-sensitive, word-boundary, spelling_variants honoured -- because
        /usr/bin/grep -ci 'ault' returns 8 where the locality Ault appears
        once.
        """
        c = self.r("R2")
        towns = c.get("towns", {}) or {}
        w = win(text, pos, radius)
        hit = set()
        for name in sorted(towns):
            variants = [name] + list(towns[name].get("spelling_variants") or [])
            for v in variants:
                if has(w, v, ci=False):
                    hit.add(name)
                    break
        return sorted(hit)

    def allowed_utilities(self, towns):
        """The utilities a page in `towns` may attribute a program to.

        `towns` EMPTY no longer means "exempt from R2". With a territory
        configured it means SITEWIDE, and a sitewide artifact may name any
        utility that serves somewhere in the territory -- but not one that
        serves nowhere in it. Returning None here (the old behaviour) exempted
        every page not listed in a town's page_slugs, which is most of each
        property and permanently included llms.txt and robots.txt.
        """
        c = self.r("R2")
        t = c.get("towns", {}) or {}
        if not t:
            return None
        if not towns:
            towns = sorted(t)
        allowed = set()
        for name in towns:
            d = t.get(name, {})
            for f in ("gas", "electric"):
                v = d.get(f)
                # A fuel may be served by MORE THAN ONE utility in one town --
                # United Power serves northern Broomfield while Xcel serves the
                # rest. Modelling one utility per fuel made the correct
                # service-area hedging on DCI's Broomfield page fail R2 22
                # times, on a page whose carve-out is verified in the repo's
                # own quarterly review, affirmed by a prior adversarial read,
                # wired into the calculator, and confirmed against United
                # Power's own service-area page. A list is accepted anywhere a
                # string is.
                for one in (v if isinstance(v, list) else [v]):
                    if one and one not in ("UNKNOWN", "UNRESOLVED") and \
                            not one.startswith(("SPLIT", "THREE-WAY")):
                        allowed.add(self.canon_utility(one))
            p = d.get("electric_program")
            if p:
                allowed.add(self.canon_utility(p))
        allowed |= set(c.get("non_territorial_programs", []) or [])
        return allowed

    # ---- cited sources (claim set)
    def key_for_cited_stat(self, art, cs):
        """Resolve a rendered cited-stat block to its CITED_SOURCES key.

        TWO DEFECTS LIVED HERE AND THEY FABRICATED EVIDENCE.

        1. THE COMPARISON WAS ASYMMETRIC. The page-side label is stored
           dec()-normalized (surfaces.py, `collapse(dec(...))`); the registry
           side got collapse() only. DCI's XCEL_WHOLE_HOME_EFFICIENCY carries
           an EN DASH (U+2013) in "2025-2026" where the rendered page carries
           an ASCII hyphen, because dec() folds it. So
           collapse(page) == collapse(registry) was False while
           collapse(dec(page)) == collapse(dec(registry)) is True, and that key
           could NEVER match by label.

        2. THE FALLBACK WAS SILENT. `best = best or k` bound the block to the
           alphabetically first key sharing the URL. With (1), every DCI page
           citing the Xcel insulation-air-sealing URL fell through to
           XCEL_BLOWER_DOOR, whose stat is the CFM 50 sentence -- and
           build_claim_set then spliced that sentence onto the page as a
           synthetic CITE surface that every proposition rule reads AS IF IT
           WERE ON THE PAGE. Result: 9 of DCI's 46 blocking R5 findings quoted
           a sentence that does not appear on the file they name. Measured
           independently: the substring `CFM` occurs 0 times on all nine,
           against `Denver` controls of 24-69.

        A verification tool that synthesizes claim surfaces and attributes them
        to artifacts that do not contain them cannot adjudicate what an
        artifact says. Both sides are now normalized identically, and a block
        that cannot be resolved returns None and is REPORTED as unresolved --
        never bound to the nearest candidate.
        """
        def norm(s):
            return S.collapse(S.dec(str(s or "")))

        page_label = norm(cs.get("label"))
        candidates = []
        for k in sorted(self.gen.cited_sources):
            e = self.gen.cited_sources[k]
            url = e.get("url")
            if not isinstance(url, str) or url != cs["url"]:
                continue
            candidates.append(k)
            label = norm(str(e.get("determiner") or "")
                         + str(e.get("source") or ""))
            if label and page_label and page_label == label:
                return k
        # Exactly one entry owns this URL: the label is redundant and binding
        # is unambiguous. More than one, and no label matched: UNRESOLVED.
        if len(candidates) == 1:
            return candidates[0]
        if candidates:
            self.unresolved_cited_stats.append(
                (art.rel, cs.get("url", ""), cs.get("label", ""),
                 tuple(candidates)))
        return None

    def svg_text_for(self, ref):
        """Text nodes of a referenced SVG in the READ_SET (spec 2.3)."""
        if not ref:
            return []
        base = ref.split("?")[0].split("#")[0].rsplit("/", 1)[-1]
        if not base.lower().endswith(".svg"):
            return []
        for rel, art in sorted(self.by_rel.items()):
            if rel.rsplit("/", 1)[-1] == base and art.kind == "svg":
                return art.stream((S.S_SVGTEXT,))
        return []


def _const_probe(value):
    """The longest placeholder-free run of a generator constant, used to decide
    whether that constant actually rendered onto a page."""
    t = S.collapse(S.txt(value))
    parts = re.split(r"\{[^{}]*\}|%[sd]|__[A-Z_]+__", t)
    parts = [p.strip() for p in parts]
    parts.sort(key=len, reverse=True)
    return parts[0] if parts and len(parts[0]) >= 25 else None


def build_claim_set(ctx):
    r2 = ctx.r("R2")
    const_names = list(r2.get("territorial_constants", []) or [])
    probes = {}
    for n in sorted(set(const_names)):
        v = ctx.gen.constants.get(n)
        if isinstance(v, str):
            p = _const_probe(v)
            if p:
                probes[n] = (p, v)

    n_cite = n_const = n_asset = n_prop = 0
    for art in ctx.html_artifacts():
        extra = []
        keys = set()
        for cs in art.cited_stats:
            k = ctx.key_for_cited_stat(art, cs)
            if k:
                keys.add(k)
        base = art.rel.rsplit("/", 1)[-1]
        for cand in (base, base[:-5] if base.endswith(".html") else base):
            for k in ctx.gen.slug_cite_keys.get(cand, []):
                keys.add(k)
        art.cite_keys = sorted(keys)
        for k in art.cite_keys:
            e = ctx.gen.cited_sources.get(k) or {}
            for f in ("source", "stat", "url", "determiner"):
                v = e.get(f)
                if isinstance(v, str) and v.strip():
                    extra.append(S.Surface(S.S_CITE, "%s:%s" % (k, f),
                                           S.collapse(S.dec(v))))
                    n_prop += 1
            n_cite += 1
        for ref in sorted(set(art.image_refs)):
            for s in ctx.svg_text_for(ref):
                extra.append(S.Surface(S.S_SVGTEXT,
                                       "%s<-%s" % (s.locator, ref), s.text))
                n_asset += 1
        for n in sorted(probes):
            probe, val = probes[n]
            if probe in art.txt:
                extra.append(S.Surface(S.S_CONST, n, S.collapse(S.txt(val))))
                n_const += 1
        ctx.claim_extra[art.rel] = extra
    ctx.claim_counts = (n_prop, n_cite, n_const, n_asset)


# ---------------------------------------------------------------------------
# Level counts (spec 3: a rule that reports a zero on only one normalization
# level is a defective rule)
# ---------------------------------------------------------------------------

def level_counts(ctx, probes, ci=True, word=True):
    """ONE alternation scan per normalization level instead of one scan per
    term per level. Same counts, and it is the difference between three
    whole-corpus passes and thirty."""
    terms = sorted(set(p for p in probes if p), key=len, reverse=True)
    if not terms:
        return {S.NORM_RAW: 0, S.NORM_DEC: 0, S.NORM_TXT: 0}, []
    key = (tuple(terms), ci, word)
    cached = ctx._levels_cache.get(key)
    if cached is not None:
        return cached
    alt = "|".join(_wb(t) if word else re.escape(t) for t in terms)
    rx = re.compile(alt, re.IGNORECASE if ci else 0)
    lut = {}
    for t in terms:
        lut[t.lower() if ci else t] = t
    counts = {S.NORM_RAW: 0, S.NORM_DEC: 0, S.NORM_TXT: 0}
    per_term = dict((t, {S.NORM_RAW: 0, S.NORM_DEC: 0, S.NORM_TXT: 0})
                    for t in terms)
    for level in (S.NORM_RAW, S.NORM_DEC, S.NORM_TXT):
        for art in ctx.artifacts:
            for m in rx.finditer(art.level_text(level)):
                g = m.group(0)
                t = lut.get(g.lower() if ci else g)
                if t is None:
                    for cand in terms:
                        if (cand.lower() if ci else cand) in \
                                (g.lower() if ci else g):
                            t = cand
                            break
                if t is None:
                    t = terms[0]
                per_term[t][level] += 1
                counts[level] += 1
    detail = []
    for t in sorted(terms):
        if len(set(per_term[t].values())) > 1:
            detail.append((t, per_term[t]))
    ctx._levels_cache[key] = (counts, detail)
    return counts, detail


# ===========================================================================
# THE RULES (spec 8)
# ===========================================================================

R1_SURF = "VIS TITLE META OG TW LD LOWVIS COMMENT EMBED LLMS SVGTEXT"
R1_KEYS = (S.S_VIS, S.S_TITLE, S.S_META, S.S_OG, S.S_TW, S.S_LD,
           S.S_LOWVIS, S.S_LLMS, S.S_SVGTEXT)


def _quote_open_re(c):
    glyphs = set()
    for q in c.get("quote_open", []) or []:
        g = S.dec(q)
        if g:
            glyphs.add(g[0])
    glyphs.discard("'")
    return re.compile("[" + re.escape("".join(sorted(glyphs))) + "]")


def rule_R1(ctx, res):
    c = ctx.r("R1")
    verbs = c.get("attribution_verbs", []) or []
    allow = c.get("quotation_allowlist", []) or []
    marks = ctx.r("R7").get("correction_markers", []) or []
    qre = _quote_open_re(c)

    # DEGRADED is CONDITIONAL on the debt being unpaid, and the test is not
    # "does any entry carry a provenance key" -- one entry with one key would
    # silence the message while 21 quotable sources still asserted nothing.
    # The debt is paid when EVERY entry that publishes its stat as the source's
    # own words (quote is True) carries a complete {retrieved, artifact,
    # extraction, verbatim_line} record, AND at least one such entry exists:
    # a property that simply has no verbatim quotations has not paid a debt,
    # it has nothing to pay, and R1's claim test is asserting nothing.
    if c.get("require_provenance_block"):
        if not ctx.gen.provenance_present:
            res.degraded.append(
                "R1 DEGRADED: provenance block not yet in the schema; "
                "asserting quote field only (spec 12.1)")
        elif ctx.gen.provenance_owed:
            res.degraded.append(
                "R1 DEGRADED: %d entr%s the stat as the source's own words "
                "(quote=True) with no complete provenance record (spec 12.1 "
                "requires retrieved + artifact + extraction + "
                "verbatim_line): %s"
                % (len(ctx.gen.provenance_owed),
                   "y publishes" if len(ctx.gen.provenance_owed) == 1
                   else "ies publish",
                   ", ".join(ctx.gen.provenance_owed)))
        elif not ctx.gen.quote_true_count:
            res.degraded.append(
                "R1 DEGRADED: the provenance schema is present but NO entry "
                "on this property sets quote=True, so R1's claim-test half "
                "asserts nothing here. That is a null result, not a pass "
                "(spec 12.1)")

    cs_index = {}
    for art in ctx.claim_artifacts():
        cs_index[art.rel] = [x["txt"] for x in art.cited_stats]

    raw = []
    for art in ctx.claim_artifacts():
        for cs in art.cited_stats:
            if not cs["quoted"]:
                continue
            k = ctx.key_for_cited_stat(art, cs)
            raw.append(Hit("R1", "A", art.rel, "CITE",
                           "cited-stat@%d" % cs["offset"],
                           "%s %s" % (k or "<unresolved-key>", cs["txt"]),
                           cite_key=k, sentence=cs["txt"]))
        # HALF B DE-DUPLICATES ON WHAT IT PRINTS.
        # It emits one hit per QUOTE GLYPH, so a sentence carrying two quoted
        # spans inside one 110-char window produced two -- and the same
        # sentence reaching the pool on more than one locator multiplied that
        # again. GCI's about.html sentence 'The guidance here says "not yet"
        # as often as it says "yes," ...' produced FOUR findings that were
        # character-identical in the report, inflating the adjudicated count
        # by three and telling a reader nothing the first line had not.
        # Two findings a human cannot tell apart are one finding. The key is
        # exactly the tuple the enumeration renders, so anything that IS
        # distinguishable on the page still counts separately.
        seen_b = set()
        for skey, loc, sent in ctx.pool(art):
            for m in qre.finditer(sent):
                pre = sent[max(0, m.start() - 40):m.start()]
                v = which_any(pre, verbs, ci=True, word=False)
                if not v:
                    continue
                text = win(sent, m.start(), 110)
                dk = (art.rel, skey, text, v[0])
                if dk in seen_b:
                    continue
                seen_b.add(dk)
                raw.append(Hit("R1", "B", art.rel, skey, str(loc),
                               text, note=v[0], sentence=sent))

    def f_explicit(h):
        if h.sub != "A" or not h.cite_key:
            return False
        e = ctx.gen.cited_sources.get(h.cite_key) or {}
        ok = e.get("quote") is True
        if c.get("require_provenance_block") and ctx.gen.provenance_present:
            # Not merely "a dict is there". The four fields are the record;
            # anything less is a shape that looks like provenance.
            ok = ok and S.provenance_complete(e.get("provenance"))
        return ok

    def f_default(h):
        if h.sub != "A" or not h.cite_key:
            return False
        return "quote" not in (ctx.gen.cited_sources.get(h.cite_key) or {})

    def f_inside(h):
        if h.sub != "B":
            return False
        for t in cs_index.get(h.rel, []):
            if h.sentence and h.sentence[:60] in t:
                return True
        return False

    def f_allow(h):
        return has_any(h.sentence, [a.get("text", "") if isinstance(a, dict)
                                    else a for a in allow], word=False)

    def f_corr(h):
        return has_any(h.sentence, marks, word=False)

    res.raw = raw
    res.adjudicated, res.rows = adjudicate(raw, [
        Filt("registry-backed with explicit quote=true", f_explicit),
        Filt("registry-backed by DEFAULT quote (field absent)", f_default,
             removes=False),
        Filt("inside a cited-stat block already counted in half A", f_inside),
        Filt("config quotation_allowlist", f_allow),
        Filt("correction marker in scope (retired wording quoted)", f_corr),
    ])
    res.levels, res.level_detail = level_counts(
        ctx, ["&ldquo;", "“", "According to"], ci=False, word=False)
    na = len([h for h in res.adjudicated if h.sub == "A"])
    nb = len([h for h in res.adjudicated if h.sub == "B"])
    res.notes.append("half A (CLAIM TEST) %d  ·  half B (STRING LIST -- "
                     "cannot be a claim test) %d" % (na, nb))
    res.notes.append("registry quote field: %d True, %d False, %d ABSENT "
                     "(absent publishes the stat as the source's own words)"
                     % (ctx.gen.quote_true_count, ctx.gen.quote_false_count,
                        ctx.gen.quote_absent_count))
    res.notes.append(
        "provenance records: %d complete {retrieved, artifact, extraction, "
        "verbatim_line} of %d quote=True entr%s%s"
        % (ctx.gen.provenance_ok, ctx.gen.quote_true_count,
           "y" if ctx.gen.quote_true_count == 1 else "ies",
           ("  ·  OWED: " + ", ".join(ctx.gen.provenance_owed))
           if ctx.gen.provenance_owed else "  ·  0 OWED"))
    return "attributed quotations found", \
           "quotations with no explicit provenance record"


R2_KEYS = (S.S_VIS, S.S_TITLE, S.S_META, S.S_OG, S.S_TW, S.S_LD, S.S_JS,
           S.S_LOWVIS, S.S_ATTR, S.S_LLMS, S.S_SVGTEXT, S.S_CITE, S.S_CONST)
ELECTRIC_WORDS = ("electric", "electricity", "electrical", "kwh", "power bill")


# Coordinating conjunctions and clause boundaries. NOT ", and" -- that is how
# a town LIST is written ("Greeley, Evans and Eaton") and splitting there would
# cut a clause in half.
_CLAUSE_SPLIT = re.compile(
    r";|\s+while\s+|\s+whilst\s+|,\s*whereas\s+|\s+whereas\s+"
    r"|,\s*but\s+|\s+but\s+|\s+although\s+|,\s*although\s+"
    r"|\s+rather than\s+|,\s*however[,]?\s+"
    r"|\s*[\u2013\u2014]\s*|\s+-\s+|\s+/\s+",
    re.IGNORECASE)
# The SPACED ASCII hyphen is in that set because two of my own fixes from one
# round cancelled each other: c6b9651 made dash folding UNCONDITIONAL (which is
# what fixes R7-G2's U+2011 print code) and 3cf3d97 added the em and en dash as
# clause boundaries (which is what fixes NEW-16). The fold runs FIRST, so by the
# time the splitter looks there is no em dash left --
# dec('Greeley \u2014 Atmos') is 'Greeley - Atmos' -- and the inverted
# territory statement joined by an em dash, an en dash or a plain hyphen all
# passed at exit 0. Recognising the POST-FOLDING form keeps both fixes: a
# SPACED hyphen is a clause boundary, an intra-word hyphen ("24-02-205",
# "knob-and-tube") is not, because it has no surrounding whitespace.
# "and"/"or" are CONDITIONAL splits: they join a town LIST far more often than
# they join two clauses.
_AND_SPLIT = re.compile(r",\s*and\s+|\s+and\s+|,\s*or\s+|\s+or\s+",
                        re.IGNORECASE)


def _clauses(sent, has_utility=None, is_town=None):
    """Split a sentence into independent clauses.

    `X is the gas utility in A, while Y is the gas utility in B` has
    UNAMBIGUOUS structure. Treating it as one span and then declaring
    nearest-binding unreliable pardoned the proposition AND its negation
    identically -- and the original two-year wrong-utility defect took exactly
    this sentence shape, in a shared component rendering sitewide. Parse the
    structure; do not pardon the shape.
    """
    parts = [p.strip() for p in _CLAUSE_SPLIT.split(sent)]
    parts = [p for p in parts if p] or [sent]
    if has_utility is None:
        return parts
    # CONDITIONAL "and"/"or". Excluding them outright was a stated design
    # choice with a real justification -- "Greeley, Evans and Eaton" is a LIST
    # -- but it made the commonest conjunction in English a guaranteed escape:
    # the same inversion passed on ", and", bare " and", an em dash, "whilst",
    # "although" and " / ". Resolve it instead of omitting it:
    #   "Atmos serves Greeley, Evans, and Eaton"  -> a LIST: the conjoined
    #      items are bare town names and only one side carries a utility.
    #   "X is the utility in A, and Y is the utility in B" -> TWO CLAUSES:
    #      each side carries its own utility.
    # Split only when BOTH sides carry a utility mention.
    out = []
    for part in parts:
        pieces, spans = [], []
        last = 0
        for m in _AND_SPLIT.finditer(part):
            pieces.append(part[last:m.start()].strip())
            spans.append((m.start(), m.end()))
            last = m.end()
        pieces.append(part[last:].strip())
        pieces = [x for x in pieces if x]
        # NEVER SPLIT INSIDE A TOWN LIST. "Atmos Energy is the natural gas
        # utility in Greeley, Evans and Eaton, and Xcel Energy is the natural
        # gas utility in Johnstown ..." has a utility on both sides of BOTH
        # conjunctions, so the old all-sides-have-a-utility test cut the list
        # at "Evans and Eaton" and left "Eaton, and Xcel Energy is ..." -- which
        # binds Xcel to Eaton and fails a sentence that is exactly right.
        # Measured: 7 findings on GCI, every one this artifact. A conjunction
        # whose immediate neighbours are both TOWN NAMES is list punctuation,
        # not a clause boundary.
        if is_town is not None and len(pieces) > 1:
            for a, b in spans:
                before = part[:a].strip().rstrip(",").split()[-2:]
                after = part[b:].strip().split()[:2]
                if before and after and is_town(" ".join(before)) \
                        and is_town(" ".join(after)):
                    out.append(part)
                    break
            else:
                if all(has_utility(x) for x in pieces):
                    out.extend(pieces)
                else:
                    out.append(part)
            continue
        if len(pieces) > 1 and all(has_utility(x) for x in pieces):
            out.extend(pieces)
        else:
            out.append(part)
    return out


def rule_R2(ctx, res):
    c = ctx.r("R2")
    names = sorted(c.get("utility_names", []) or [], key=len, reverse=True)
    domains = c.get("utility_domains", {}) or {}
    aw = c.get("attribution_words", []) or []
    locked = c.get("allowed_multi_utility_sentences", []) or []
    gaps = c.get("known_disclosure_gaps", []) or []
    review = c.get("review_not_fail", []) or []
    marks = ctx.r("R7").get("correction_markers", []) or []
    towns = c.get("towns", {}) or {}
    elec_names = c.get("electric_utility_names", []) or []
    neg_markers = c.get("corrective_disclosure_markers", []) or []
    # Clause-level DENIALS of a binding. Separate from corrective_disclosure
    # markers: those say "the site got this wrong, here is the correction",
    # while these say "this utility's programme does not reach this town",
    # which is the compliant statement R2 exists to require.
    deny_bind = c.get("clause_denial_markers", []) or []
    # Markers that a sentence is DISTINGUISHING the electric utility from
    # the gas one rather than attributing a rebate to it.
    elec_deny = c.get("electric_distinguishing_markers", []) or []

    # the known-present control (spec 3): search for a term you KNOW is
    # present before trusting a term you believe is absent
    anchor = c.get("known_present_control")
    if anchor:
        n = sum(len(occ(a.txt, anchor, ci=False)) for a in ctx.artifacts)
        res.notes.append("known-present control: %r occurs %d times in the "
                         "read set (0 would invalidate every absence below)"
                         % (anchor, n))
        if n == 0 and not ctx.control:
            res.traps.append(
                "KNOWN-PRESENT CONTROL FAILED: %r occurs 0 times" % anchor)

    # Is this market's territory uniform? On a single-utility market every
    # town resolves to the same allowed set, and a tool naming that utility
    # without asking the town is correct, not town-blind.
    per_town = [ctx.allowed_utilities([t]) or set() for t in sorted(towns)]
    uniform_allowed = set.intersection(*per_town) if per_town else set()
    union_allowed = set.union(*per_town) if per_town else set()
    uniform = bool(towns) and uniform_allowed == union_allowed
    if uniform:
        res.notes.append("territory is UNIFORM across all %d configured towns "
                         "(%s) -- the town-blind-tool sub-test is not run, "
                         "because naming the one utility that serves every "
                         "town is not a town-blind verdict"
                         % (len(towns), ", ".join(sorted(uniform_allowed))))
    raw = []
    for art in ctx.rule_artifacts("R2"):
        scope = ctx.town_scope(art)
        allowed = ctx.allowed_utilities(scope)
        scope_s = ",".join(scope) or ("sitewide(union of %d towns)"
                                      % len(towns) if towns else "sitewide")
        for skey, loc, sent in ctx.pool(art):
            if not has_any(sent, aw, word=False):
                continue
            # JS COMMENTS ARE OUT OF R2's CLAIM SET. A comment naming a utility
            # is not an attribution made to a visitor, and they were a
            # measurable share of R2's 100% false-positive rate. R3 still reads
            # them (GCI f0203ad's cap shipped in one), which is the right split.
            if skey == S.S_JS and "comment@" in str(loc):
                continue
            for clause in _clauses(
                    sent, lambda t: bool(ctx.utility_spots(t)),
                    lambda t: bool(ctx.town_spots(t))):
                # An INTERROGATIVE clause asks; it does not attribute.
                # "Does the Xcel insulation rebate apply to my Greeley
                # home?" was failed as an attribution of Xcel to Greeley,
                # on a page whose answer is no.
                if clause.rstrip().endswith("?"):
                    continue
                uspots = ctx.utility_spots(clause)
                tspots = ctx.town_spots(clause)
                bound = set()
                # REVIEW is now the RESIDUE, not the default: only a CLAUSE
                # that still carries two or more utilities AND two or more
                # towns after splitting is genuinely ambiguous.
                multi = (len(set(x[0] for x in uspots)) >= 2 and
                         len(set(t for t, _ in tspots)) >= 2)
                # DIRECTION MATTERS. "<utility> is the natural gas utility in
                # <town>" puts the town AFTER the utility, and English does
                # that overwhelmingly often. Pure nearest-distance binding read
                # "... Greeley, Evans and Eaton, and Xcel Energy is the natural
                # gas utility in Johnstown ..." as Xcel-bound-to-Eaton, because
                # Eaton is ten characters behind Xcel and Johnstown is
                # forty-four ahead. Measured: 7 findings on GCI, all false, on
                # the sentence that states the split CORRECTLY.
                # A utility that has a town AFTER it within the window binds
                # forward; only a utility with no following town falls back to
                # the nearest preceding one. This also keeps the inversion
                # failing, which is the whole point: "Xcel Energy is the
                # natural gas utility in Greeley" binds forward to Greeley,
                # which Xcel does not serve, and FAILS.
                # A utility binds forward to EVERY town in the list that
                # follows it, up to the next utility mention. "X is the gas
                # utility in A, B and C" attributes X to all three, and binding
                # only the nearest let "Atmos ... in Greeley, Evans and
                # Johnstown" pass on Greeley while Johnstown went unexamined.
                upos_sorted = sorted(p for _, p in uspots)
                fwd = {}
                for uu, up in uspots:
                    nxt = min([p for p in upos_sorted if p > up] or [10 ** 9])
                    tl = sorted(set(tn for tn, tp in tspots
                                    if up < tp < nxt and tp - up <= 160))
                    if tl:
                        fwd[(uu, up)] = tl
                tpos_of = {}
                for tn, tp in tspots:
                    tpos_of.setdefault(tn, []).append(tp)
                for (uu, up), tl in sorted(fwd.items()):
                    bound.add((uu, up))
                    for tname in tl:
                        if uu in (ctx.allowed_utilities([tname]) or set()):
                            continue
                        # A town the clause EXCLUDES is not a town the clause
                        # attributes to. LGM's index says "Longmont Power &
                        # Communications electric customers only, not every
                        # Longmont address, and not Lafayette, Louisville, or
                        # Niwot:" -- three forward bindings, all of them to
                        # towns the sentence has just ruled out.
                        if any(re.search(r"\b(?:not|nor|except|excluding)\b"
                                         r"[^.;]{0,60}$", clause[:tp])
                               for tp in tpos_of.get(tname, [])):
                            continue
                        if has_any(clause, deny_bind, word=False) or \
                                has_any(sent, deny_bind, word=False):
                            continue
                        hf = Hit(
                            "R2", "a", art.rel, skey, str(loc),
                            "%s is bound to %s, a town named AFTER it in its "
                            "own clause, which it does not serve | clause: %s"
                            % (uu, tname, clause),
                            note="utility-not-serving-town-in-clause",
                            sentence=sent)
                        hf.r2_binding = (uu, tname)
                        # DELIBERATELY NOT downgraded by `multi`. The
                        # split-disclosure REVIEW class exists because
                        # nearest-binding is decided by word order rather than
                        # meaning -- but a utility FOLLOWED BY its own town
                        # list is not ambiguous, it is the standard English
                        # construction. Downgrading it is what let the EXACT
                        # INVERSION of GCI's gas-split fact pass at exit 0,
                        # which the 2026-09-17 adversarial read recorded as the
                        # highest-value surviving hole in the whole gate.
                        raw.append(hf)
                for tname, tpos in tspots:
                    near = [(abs(tpos - up), uu, up) for uu, up in uspots
                            if abs(tpos - up) <= 100 and (uu, up) not in fwd]
                    if not near:
                        continue
                    _, uu, up = sorted(near)[0]
                    bound.add((uu, up))
                    if uu in (ctx.allowed_utilities([tname]) or set()):
                        continue
                    # A clause that DENIES the binding is the compliant form,
                    # not the defect. "Longmont's situation (a second, Longmont
                    # Power & Communications-only rebate) doesn't apply in
                    # Lafayette." says exactly what R2 wants said, and the
                    # nearest-binding resolver failed it 6 times on LGM for
                    # naming the utility and the town in one clause. A rule
                    # that returns the same verdict for a claim and its denial
                    # is not testing the claim.
                    if has_any(clause, deny_bind, word=False):
                        continue
                    lo, hi = min(up, tpos), max(up, tpos)
                    span = clause[max(0, lo - 34):hi + 40]
                    if has_any(span, neg_markers, word=False) and \
                            (set(x[0] for x in uspots) &
                             set(ctx.allowed_utilities([tname]) or set())):
                        hc = Hit("R2", "a", art.rel, skey, str(loc),
                                 "%s bound to %s | %s" % (uu, tname, clause),
                                 note="utility-not-serving-town-in-clause",
                                 sentence=sent)
                        hc.r2_subject_ok = False
                        raw.append(hc)
                        continue
                    hb = Hit(
                        "R2", "a", art.rel, skey, str(loc),
                        "%s is bound to the nearest town in its own clause, "
                        "%s, which it does not serve | clause: %s"
                        % (uu, tname, clause),
                        note="utility-not-serving-town-in-clause",
                        sentence=sent)
                    hb.r2_binding = (uu, tname)
                    if multi:
                        hb.note = "split-disclosure-review"
                    raw.append(hb)
                # THE SENTENCE BINDS BEFORE THE PAGE DOES. A clause with no
                # town of its own falls back to the PAGE's town -- which is
                # right for a standalone claim and wrong for a fragment of a
                # correct disclosure. GCI's sitewide gas-split sentence ends
                # "... the natural gas utility is Xcel Energy in Johnstown,
                # for most of Milliken, and for most locations in Severance --
                # Xcel sets out its own insulation and air sealing rebate
                # terms on its rebate page", and the splitter orphans that last
                # clause. Bound to the page, it read as "Xcel attributed to
                # Greeley" on every Atmos town: 47 findings, measured, one
                # sentence, all false. If the SENTENCE binds the utility to a
                # town it does serve, the clause asserts nothing against the
                # page's town.
                sent_towns = set(t for t, _ in ctx.town_spots(sent))
                sent_ok = set()
                for tn in sorted(sent_towns):
                    sent_ok |= (ctx.allowed_utilities([tn]) or set())
                for u, upos in uspots:
                    if (u, upos) in bound:
                        continue
                    if not tspots and sent_towns and u in sent_ok:
                        hs = Hit("R2", "a", art.rel, skey, str(loc),
                                 "%s | no town in this clause, but its own "
                                 "SENTENCE binds it to %s, which it does "
                                 "serve | %s"
                                 % (u, ",".join(sorted(
                                     t for t in sent_towns
                                     if u in (ctx.allowed_utilities([t])
                                              or set()))), clause),
                                 note="bound-by-sentence-not-page",
                                 sentence=sent)
                        hs.r2_sentence_bound = True
                        raw.append(hs)
                        continue
                    if allowed is not None and u in allowed:
                        if not scope:
                            hh = Hit("R2", "a", art.rel, skey, str(loc),
                                     "%s | no town bound in the clause, no "
                                     "town scope on the page | %s"
                                     % (u, clause),
                                     note="sitewide-no-town-in-clause",
                                     sentence=sent)
                            hh.r2_sitewide = True
                            raw.append(hh)
                        continue
                    # The same denial test the clause-binding path uses. "The
                    # Atmos program described elsewhere on this site is for the
                    # towns Atmos serves and does not apply to a Johnstown
                    # home." is the CORRECTION the 2026-09-08 Xcel-gas pass
                    # shipped, and R2 was failing the page for carrying it.
                    # Tested against the SENTENCE as well as the clause:
                    # the clause boundary is the gate's own artifact, and
                    # "The Atmos program described elsewhere on this site is
                    # for the towns Atmos serves and does not apply to a
                    # Johnstown home." puts the denial on the far side of a
                    # split from the utility mention.
                    if has_any(clause, deny_bind, word=False) or \
                            has_any(sent, deny_bind, word=False):
                        continue
                    hp = Hit("R2", "a", art.rel, skey, str(loc),
                             "%s | scope=%s | %s" % (u, scope_s, clause),
                             note=("utility-not-serving-town"
                                   if allowed is not None
                                   else "sitewide-scope-no-town-configured"),
                             sentence=sent)
                    hp.r2_noscope = (allowed is None)
                    if allowed:
                        for pos in occ(clause, u, ci=True):
                            pre = clause[max(0, pos - 34):pos]
                            if has_any(pre, neg_markers, word=False) and \
                                    (set(x[0] for x in uspots) & set(allowed)):
                                hp.r2_subject_ok = False
                                break
                    raw.append(hp)
        for h in sorted(set(art.hrefs)):
            m = re.match(r"https?://([^/]+)", h)
            if not m:
                continue
            host = m.group(1).lower()
            for dom in sorted(domains):
                if host == dom or host.endswith("." + dom):
                    u = ctx.canon_utility(domains[dom])
                    if allowed is None or u not in allowed:
                        hit = Hit("R2", "c", art.rel, "ATTR", "href:%s" % h,
                                  "%s | scope=%s | %s" % (u, scope_s, h),
                                  note=("wayfinding-url" if allowed is not None
                                        else "sitewide-scope-no-town-configured"),
                                  sentence=h)
                        hit.r2_noscope = (allowed is None)
                        raw.append(hit)
        for k in art.cite_keys:
            e = ctx.gen.cited_sources.get(k) or {}
            blob = " ".join(str(e.get(f) or "") for f in ("source", "stat", "url"))
            for u in ctx.utilities_in(k.replace("_", " ") + " " + blob):
                if allowed is None or u not in allowed:
                    h = Hit("R2", "b", art.rel, "CITE", k,
                            "%s | scope=%s | inherited cite key %s"
                            % (u, scope_s, k),
                            note=("inherited-cite-key" if allowed is not None
                                  else "sitewide-scope-no-town-configured"),
                            sentence=blob)
                    h.r2_noscope = (allowed is None)
                    raw.append(h)
        if c.get("forbid_electric_utility_naming"):
            for skey, loc, sent in ctx.pool(art):
                if not has_any(sent, ELECTRIC_WORDS, word=False):
                    continue
                # A developer comment is not an attribution made to a visitor,
                # the same exclusion R2's main path already makes.
                if skey == S.S_JS and "comment@" in str(loc):
                    continue
                # A sentence that DISTINGUISHES gas from electric, or denies
                # the electric connection, is the compliant statement -- it is
                # what the rule wants said. Measured 2026-09-18: all 10 of
                # GCI's adjudicated `e` findings are sentences of this shape,
                # e.g. "In Greeley the gas utility runs the insulation rebates,
                # NOT the electric utility", "The electrical work itself
                # doesn't qualify for the Atmos Energy insulation rebate", and
                # "The two scopes don't share a rebate program".
                if has_any(sent, deny_bind, word=False) or \
                        has_any(sent, elec_deny, word=False):
                    continue
                for u in names_in(sent, elec_names or names,
                                  c.get("utility_aliases", {}) or {},
                                  ci=True):
                    raw.append(Hit("R2", "e", art.rel, skey, str(loc),
                                   "%s named beside an electric word | %s"
                                   % (u, sent),
                                   note="electric-utility-named",
                                   sentence=sent))
        # FORBIDDEN PROGRAM NAMES. config.R2.forbidden_program_names carried
        # full provenance -- DCI's "Xcel IQ Program" returns 0 on Xcel's own
        # Colorado DSM filing page, which does carry 23 "IQ" tokens, all in
        # SPECIFIC program titles -- and NO code path read it. This is why the
        # invented-fifth-program defect scored MISSED.
        for skey, loc, sent in ctx.pool(art):
            for bad in names_in(sent, c.get("forbidden_program_names", []) or [],
                                None, ci=True):
                raw.append(Hit("R2", "p", art.rel, skey, str(loc),
                               "%s is a FORBIDDEN program name | %s | %s"
                               % (bad, c.get("forbidden_program_reason",
                                             "")[:120], sent),
                               note="forbidden-program-name", sentence=sent))

        # LOCKED RESTRICTION STRINGS. Ruling 7's LGM clause: every Efficiency
        # Works sentence must carry the LPC-electric-customers-only
        # restriction. Measured as unenforced: an Efficiency Works sentence on
        # Longmont's own index.html with no restriction gave RAW 0 ADJ 0 PASS.
        locked_req = c.get("locked_restriction_strings", []) or []
        req_for = c.get("locked_restriction_required_for", []) or []
        # The restriction may be stated in the PAGE'S OWN WORDS. Measured
        # 2026-09-18: this sub-test produced 23 adjudicated findings on LGM and
        # 22 of them are false positives, because 16 of the flagged pages carry
        # "Longmont Power & Communications electric customers may separately
        # qualify for an Efficiency Works rebate - check your bill to see which
        # utility serves your address." -- which IS the restriction, correctly
        # stated, and matches none of the four locked literals. That is the
        # inverse paraphrase escape: a string list that once let defects
        # through now makes correct copy fail. A sentence satisfies the
        # restriction if it carries a locked literal OR names the restricting
        # utility itself; and a sentence that DENIES eligibility needs no
        # restriction, because it grants nothing to restrict.
        restr_equiv = c.get("locked_restriction_equivalents", []) or []
        restr_deny = c.get("locked_restriction_denials", []) or []

        def _satisfied(text):
            return (has_any(text, locked_req, word=False)
                    or has_any(text, restr_equiv, word=False))

        if locked_req and req_for and art.kind != "src":
            named_where = []
            for skey, loc, sent in ctx.pool(art):
                if not names_in(sent, req_for, None, ci=True):
                    continue
                if has_any(sent, restr_deny, word=False):
                    continue
                if _satisfied(sent):
                    continue
                named_where.append((skey, str(loc), sent))
            if named_where:
                page_has = _satisfied(art.txt)
                # ONE finding per PAGE, not per sentence. Ruling 7's clause is
                # about the restriction travelling with the claim, and the
                # config's own locked_restriction_reach records the standing
                # state as PAGE-level ("10 + 8 pages, measured in d6e8dab").
                # Sentence granularity produced 190 + 871 rows on LGM, which
                # is a number nobody acts on.
                skey, loc, sent = named_where[0]
                raw.append(Hit(
                    "R2", "r", art.rel, skey, loc,
                    "%s named in %d unrestricted, non-denying sentence(s); "
                    "the restriction appears %s | first: %s"
                    % (",".join(names_in(sent, req_for, None, ci=True)),
                       len(named_where),
                       "elsewhere on this page but not with the claim"
                       if page_has else "NOWHERE on this page", sent),
                    note=("restriction-elsewhere-on-page" if page_has
                          else "restriction-absent"), sentence=sent))

        # hedge preservation and the per-town qualifier are assertions about
        # the town's OWN page.
        own = ctx.own_towns(art)
        for name in own:
            d = towns.get(name, {})
            if d.get("gas_state") != "HEDGED":
                continue
            for pair in (c.get("hedge_pairs") or []):
                for half in pair:
                    if half and half not in art.txt:
                        raw.append(Hit("R2", "h", art.rel, "VIS", name,
                                       "hedged town %s is missing hedge half "
                                       "%r" % (name, half),
                                       note="hedge-half-missing", sentence=half))
        # per-town qualifier, verbatim and non-interchangeable
        for name in own:
            d = towns.get(name, {})
            q = d.get("gas_qualifier") or ""
            if q and q not in art.txt:
                raw.append(Hit("R2", "q", art.rel, "VIS", name,
                               "town %s qualifier %r absent" % (name, q),
                               note="qualifier-absent", sentence=q))
            for other in sorted(towns):
                oq = towns[other].get("gas_qualifier") or ""
                if other == name or not oq or oq == q:
                    continue
                for cs in S.sentences(art.txt_blocks):
                    if oq not in cs:
                        continue
                    # A qualifier travelling WITH ITS OWN TOWN is a disclosure,
                    # not contamination. GCI's sitewide gas-split sentence
                    # names all nine towns and each town's qualifier, and every
                    # town page carries it -- correctly. Flagging Greeley's
                    # page for saying "for most of Milliken" IN A SENTENCE
                    # THAT NAMES MILLIKEN produced 20 findings, measured, all
                    # false. Contamination is the qualifier arriving WITHOUT
                    # the town it belongs to.
                    if has(cs, other, ci=True):
                        continue
                    raw.append(Hit(
                        "R2", "x", art.rel, "VIS", name,
                        "town %s page carries %s's qualifier %r, and %s is "
                        "NOT named in that sentence | %s"
                        % (name, other, oq, other, cs),
                        note="qualifier-cross-contamination",
                        sentence=cs))
        # town-blind tool output
        if art.kind == "html" and art.js_strings and not uniform:
            # Satisfied by a town input OR by the tool asking for the utility
            # DIRECTLY -- a calculator that asks "who is your gas utility" is
            # not town-blind, it is town-independent.
            has_town_input = bool(
                re.search(r"(?:id|name)=\"[^\"]*(?:town|city|municipal"
                          r"|utility|provider)", art.raw, re.I) or
                re.search(r"<label[^>]*>[^<]{0,90}(?:your town|your city|"
                          r"your (?:electric |gas )?utility|"
                          r"(?:electric|gas) utility|which utility|"
                          r"utility provider|who (?:is|provides))",
                          art.raw, re.I))
            # LGM's calculator asks "Is your electric utility Longmont Power &
            # Communications (LPC)?" through an input named `cc-lpc`. The old
            # detector looked for town/city/utility INSIDE the id or name and
            # for a short list of label phrases within 60 characters, and
            # missed both -- so a tool that asks the strictly better question
            # was reported 6 times as town-blind. Asking the utility is not
            # town-blind, it is town-INDEPENDENT.
            if not has_town_input:
                # Read the JS SURFACES, not the raw literals: a `+`
                # concatenation run is now one joined surface, and the
                # disclosure this sub-test must not fire on -- "Atmos Energy is
                # the natural gas utility in Greeley, Evans and Eaton, and Xcel
                # Energy is the natural gas utility in Johnstown ..." -- is
                # split across three literals in GCI's calculators. Judging the
                # fragments judged something the page never says.
                js_surfaces = [(sf.locator, sf.text) for sf in art.surfaces
                               if sf.key == S.S_JS
                               and "comment@" not in str(sf.locator)
                               and not str(sf.locator).endswith("body")]
                for loc, lit in js_surfaces:
                    # A literal that names the utility TOGETHER WITH a town it
                    # serves is a disclosure, not a town-blind verdict. GCI's
                    # calculators carry "gas territory here is split: Atmos
                    # Energy is the natural gas utility in Greeley, Evans and
                    # Eaton, and Xcel Energy is the natural gas utility in
                    # Johnstown ..." -- one of them says outright "which this
                    # checker does not ask about". Measured: 14 findings on
                    # GCI, every one of them the split disclosure.
                    lit_towns = set(t for t, _ in ctx.town_spots(lit))
                    lit_ok = set()
                    for tn in sorted(lit_towns):
                        lit_ok |= (ctx.allowed_utilities([tn]) or set())
                    # AN ATTRIBUTION WORD IS REQUIRED, the same precondition
                    # R2's prose path uses. Without it this fired on
                    # "Atmos Energy sponsors the county fair." -- not a
                    # territory claim at all.
                    if not has_any(lit, aw, word=False):
                        continue
                    for u in [x for x in ctx.utilities_in(lit)
                              if x not in uniform_allowed
                              and not (lit_towns and x in lit_ok)]:
                        raw.append(Hit("R2", "t", art.rel, "JS", loc,
                                       "%s named in a verdict-reachable JS "
                                       "literal with no town input | %s"
                                       % (u, S.collapse(lit)),
                                       note="town-blind-tool",
                                       sentence=S.collapse(lit)))

    refusals = ctx.r("R10").get("refusal_markers", []) or []

    def f_wayfind(h):
        return has_any(h.sentence, refusals, word=False)

    _locked_bind = {}

    def _bindings_of(text):
        """The (utility, town) bindings a locked sentence itself carries,
        resolved with the SAME clause-split and nearest-binding logic."""
        if text in _locked_bind:
            return _locked_bind[text]
        out = set()
        for cl in _clauses(text, lambda t: bool(ctx.utility_spots(t))):
            us = ctx.utility_spots(cl)
            for tn, tp in ctx.town_spots(cl):
                near = [(abs(tp - up), uu, up) for uu, up in us
                        if abs(tp - up) <= 100]
                if near:
                    out.add((sorted(near)[0][1], tn))
        _locked_bind[text] = out
        return out

    def f_gap(h):
        """known_disclosure_gaps pardons only the BINDINGS IT CARRIES.

        Same substring-passport shape as the locked allowlist, in a second
        list. MEASURED: "Atmos Energy is the natural gas utility in Greeley,
        Evans and Eaton, AND Atmos Energy is the natural gas utility in
        Severance." gave RAW 2 ADJ 0 PASS at exit 0, while the wrong clause
        ALONE gave RAW 1 ADJ 1 FAIL. Severance is an Xcel town, so that was a
        live wrong-utility claim passing because a CORRECT phrase about Greeley,
        Evans and Eaton happened to sit in front of it.

        A declared disclosure gap describes the towns it names; it says nothing
        about a town it does not name.
        """
        tb = getattr(h, "r2_binding", None)
        for gpat in gaps:
            if not gpat or gpat not in h.sentence:
                continue
            if tb is None:
                return True
            if tb in _bindings_of(gpat):
                return True
        return False

    def f_locked(h):
        """A locked sentence pardons only the BINDINGS IT ACTUALLY CARRIES.

        This matched as a SUBSTRING, so any sentence CONTAINING a locked phrase
        was pardoned whole -- including the inversion of the very fact the
        phrase exists to protect. GCI's real gas-split fact with the two
        utilities SWAPPED, keeping the twelve-word lead-in, gave RAW 5 ADJ 0
        PASS at exit 0, while the identical swapped sentence WITHOUT the
        lead-in gave RAW 5 ADJ 5 FAIL. Prefixing twelve allowlisted words to a
        fully inverted territory statement bought a sitewide pass -- the exact
        shape of the original two-year defect. The filter's own label said
        "verbatim" and the behaviour was not.

        A hit that reports a utility->town BINDING is now pardoned only when
        some locked entry both appears in the sentence AND carries that same
        binding itself. A lead-in phrase naming no utility and no town carries
        no bindings and therefore pardons nothing.
        """
        tb = getattr(h, "r2_binding", None)
        for L in locked:
            if not L or L not in h.sentence:
                continue
            if tb is None:
                return True
            if tb in _bindings_of(L):
                return True
        return False

    def f_review(h):
        return has_any(h.sentence, review, word=False)

    def f_corr(h):
        return has_any(h.sentence, marks, word=False)

    def f_nonterr(h):
        return has_any(h.sentence, c.get("non_territorial_programs", []) or [],
                       word=False) and h.sub in ("a",)

    def f_srccode(h):
        return ctx.src_code_hit(h)

    def f_srcdup(h):
        return ctx.src_dup(h)

    def f_noscope(h):
        return bool(getattr(h, "r2_noscope", False))

    def f_sitewide(h):
        return bool(getattr(h, "r2_sitewide", False))

    def f_split(h):
        return h.note == "split-disclosure-review"

    def f_sentbound(h):
        return bool(getattr(h, "r2_sentence_bound", False))

    def f_townblind(h):
        # SUB-TEST `t` IS A REVIEW CLASS, NOT A FAILURE. Measured: it fires
        # IDENTICALLY on the correct utility, on the wrong utility, and on a
        # non-attribution, because a tool with no town input cannot be judged
        # right or wrong ABOUT a town -- there is no town to be wrong about.
        # Its whole recorded history is false positives: 6 on LGM (a calculator
        # that asks the visitor's UTILITY, which is the strictly better
        # question), 14 then 10 then 1 on GCI (the correct gas-split
        # disclosure), and the sixth adversarial read declined to credit its
        # one apparent catch -- vector R2-B8, a utility assembled across a JS
        # concatenation boundary -- on exactly this ground, putting the honest
        # miss count at 12 of 86 rather than 11. Zero true positives, ever.
        # Raised, enumerated and cleared through this named filter: the design
        # observation is worth printing, and it is not worth failing a build on.
        return h.sub == "t" 

    def f_restr_elsewhere(h):
        return h.note == "restriction-elsewhere-on-page"

    def f_corrective(h):
        return not getattr(h, "r2_subject_ok", True)

    res.raw = raw
    res.adjudicated, res.rows = adjudicate(raw, [
        Filt("the generator SRC surface is a STYLESHEET or a SCRIPT BODY, not "
             "prose -- its quoted string LITERALS are judged separately "
             "under a #strN locator", f_srccode),
        Filt("generator SRC restatement of prose that already renders in public/ (counted once, against the rendered artifact)", f_srcdup),
        Filt("split disclosure -- two or more utilities AND two or more towns "
             "in one sentence, where nearest-binding is decided by word order "
             "rather than meaning: REVIEW, never FAIL", f_split),
        Filt("sitewide artifact, no town named in the clause -- the utility "
             "serves somewhere in this territory, so nothing is asserted "
             "against a town (raised and enumerated, never dropped silently)",
             f_sitewide),
        Filt("town-blind tool (sub-test t) -- REVIEW, never FAIL: a tool with "
             "no town input cannot be judged right or wrong about a town, and "
             "this sub-test fires identically on the correct utility, the "
             "wrong one, and a non-attribution. Zero true positives measured.",
             f_townblind),
        Filt("no town in the clause, but the utility's OWN SENTENCE binds it "
             "to a town it DOES serve -- a fragment of a correct disclosure, "
             "not an attribution to the page's town (raised and enumerated)",
             f_sentbound),
        Filt("corrective disclosure -- a negation or contrast marker governs "
             "the flagged utility and the sentence names one that DOES serve "
             "the scope (correct territory copy, not an attribution)",
             f_corrective),
        Filt("locked restriction present ON THE PAGE but not in the same "
             "sentence -- REVIEW, not FAIL", f_restr_elsewhere),
        Filt("no territory configured for this property -- R2 cannot scope "
             "anything (raised, then cleared here, never dropped silently)",
             f_noscope),
        Filt("sanctioned off-property wayfinding (a refusal marker binds the "
             "sentence: it names the publisher and declines to republish)",
             f_wayfind),
        Filt("locked multi-utility sentence (gas-split fact, verbatim)", f_locked),
        Filt("known_disclosure_gaps (Director told, not reversing)", f_gap),
        Filt("review_not_fail -> REVIEW classification, never FAIL", f_review),
        Filt("non_territorial_program named in the same sentence", f_nonterr),
        Filt("correction marker in scope", f_corr),
    ])
    res.levels, res.level_detail = level_counts(
        ctx, [n for n in names[:8]], ci=False)
    res.notes.append("sibling-town artifact detection is NOT in this rule: it "
                     "is _artifact_grep.sh's existing check (present on LGM "
                     "and GCI, ABSENT on DCI). R2 asserts utility attribution "
                     "and electric naming only.")
    return "utility attributions resolved against town scope", \
           "attributions to a utility that does not serve the town"


_T2_PHONE = re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b")
_T2_ZIP = re.compile(r"\b8[0-1]\d{3}\b")
# The \b before \d{2} could never match a LETTER-PREFIXED identifier: in
# "HB25-1202" there is no word boundary between "B" and "2", so Colorado bill
# numbers sailed straight past this and were reported as rebate figures. GCI
# published "A 2025 bill that would have created Colorado's first mold-provider
# registry, HB25-1202, died in a House committee vote" and the gate called
# 1202 a payout. [A-Z]{0,4}\s? covers HB/SB/HCR/SCR/HJR/SJR and leaves the bare
# forms matching exactly as before.
_T2_PRINTCODE = re.compile(r"\b\d{2}-\d{2}-\d{3}\b|\b[A-Z]{0,4}\s?\d{2}-\d{4}\b"
                           r"|\bPublic Law \d+-\d+\b|\b\d{2}-\d{4}\s*\("
                           r"\d{2}-\d{2}\)")
_T2_YEARPREP = re.compile(
    r"\b(?:built|constructed|rebuilt|homes?|houses?|dwellings?|stock|era|"
    r"since|predates?|predating|during|circa|in|after|before|from|through)\s+"
    r"(?:after\s+|before\s+|in\s+|since\s+)?(?:19|20)\d\d\b",
    re.IGNORECASE)
_T2_UNITS = ("\u00b0F", "degree", "perm", "pascal", "CFM", "sq ft",
             "square feet", "square foot", "feet", "foot", "inch", "inches",
             "BTU", "kWh", "therm", "R-value", "lb", "pound", "cubic",
             "elevation", "ZIP", "zip code", "phone", "call ", "tel:",
             "priority", "changefreq", "word", "character")
_T2_XMLATTR = re.compile(
    r"(?:\b(?:d|x|y|x1|x2|y1|y2|cx|cy|r|rx|ry|width|height|viewBox|points|"
    r"stroke-width|font-size|offset|opacity|transform|letter-spacing|"
    r"stop-opacity)\s*=\s*[\"'][^\"']*)$", re.IGNORECASE)
_T2_INURL = re.compile(r"(?:https?://|/)[^\s\"'<>]*$")


def _t2_structural(ctx, art, text, pos, matched):
    """Why a bare numeral is NOT a money figure. Returns a reason or "".

    R3-T2's measured false-positive rate was 85.1% / 100% / 77.3% while DCI
    carries ZERO $ figures at HEAD, and the hits were square footage, ZIP
    codes, phone numbers, sitemap <priority>, a statute, 0.1 perm,
    130-150 degF, 5,280 feet, a print code and an SVG path coordinate. A rule
    nobody trusts gets ignored, which is worse than no rule.
    """
    before = text[max(0, pos - 90):pos]
    after = text[pos:pos + 90]
    w = before + after
    if art.kind in ("xml", "svg") or _T2_XMLATTR.search(before):
        return "xml/svg numeric attribute or path coordinate"
    if _T2_INURL.search(before):
        return "inside a URL or path"
    if re.search(r"=\s*[\"'][^\"']{0,80}$", before):
        return "inside an attribute value"
    if _T2_PHONE.search(w):
        return "telephone number"
    if _T2_ZIP.search(matched) and "8" == matched[:1] and len(matched) == 5:
        return "Colorado postal code"
    if _T2_PRINTCODE.search(w):
        return "statute or citation print code"
    # An ISO date is a date wherever it appears. Structural, not a marker
    # list: the repaired R3a fixture reads "... were DELETED 2026-09-08" and no
    # vocabulary of date words would have covered "DELETED".
    if re.match(r"\d{4}-\d{2}-\d{2}", text[pos:pos + 10]) or \
            re.search(r"\d{4}-\d{2}-$", text[max(0, pos - 8):pos]) or \
            re.search(r"\d{4}-$", text[max(0, pos - 5):pos]):
        return "part of an ISO date"
    ea = (ctx.r("R2").get("elevation_anchor") or "")
    if ea and (matched == ea.replace(",", "") or matched in ea):
        return "configured elevation anchor"
    if has_any(w, _T2_UNITS, word=False):
        return "unit-of-measure phrase, not a payout"
    return ""


def rule_R3(ctx, res):
    c = ctx.r("R3")
    dollar = re.compile(c.get("dollar_pattern", r"\$[0-9][0-9,.]*"))
    rate = re.compile(c.get("rate_pattern", r"\b0\.[0-9]{1,2}\b"))
    money = c.get("money_words", []) or []
    ranks = c.get("rank_words", []) or []
    wchars = int(c.get("window_chars", 120))
    allowed = c.get("allowed_figures", []) or []
    costs = c.get("cost_context_markers", []) or []
    cost_units = c.get("cost_unit_markers", []) or []
    cost_nouns = c.get("cost_noun_markers", []) or []
    year_binders = c.get("year_payout_binders", []) or []
    codes = c.get("code_context_markers", []) or []
    income = c.get("income_eligibility_markers", []) or []
    structs = c.get("allowed_structure_percentages", []) or []
    computed = ctx.r("R5").get("computed_output_markers", []) or []
    marks = ctx.r("R7").get("correction_markers", []) or []
    progs = (ctx.r("R4").get("programs", []) or []) + \
            (ctx.r("R2").get("utility_names", []) or [])

    raw = []
    for art in ctx.read_artifacts():
        # T1 runs over RAW **and** DEC. RAW alone is what the existing
        # acceptance gate does and it cannot see &#36; / &#x24; / &dollar;,
        # which all decode to `$`. A DEC-only match is flagged as
        # entity-encoded so the reader can see WHY the raw gate missed it.
        seen_t1 = set()
        for level, text in ((S.NORM_RAW, art.raw), (S.NORM_DEC, art.dec)):
            for m in dollar.finditer(text):
                w = S.collapse(S.dec(win(text, m.start(), wchars)))
                # Key on a NARROW normalized window. The wide window's edges
                # differ between RAW and DEC whenever an entity sits inside it,
                # so a figure visible at both levels was counted twice
                # (RAW 4 ADJ 3, one copy tagged ENTITY-ENCODED) -- inflation,
                # not blindness, and present twice on the real GCI run.
                key = (m.group(0), S.collapse(S.dec(win(text, m.start(), 40))))
                if key in seen_t1:
                    continue
                seen_t1.add(key)
                enc = (level == S.NORM_DEC)
                _h1 = None
                raw.append(Hit("R3", "T1", art.rel,
                               ctx.surface_at(art, m.start(), level),
                               "%s@%d" % (level.lower(), m.start()),
                               "%s%s | %s"
                               % (m.group(0),
                                  " [ENTITY-ENCODED: invisible at RAW]"
                                  if enc else "", w),
                               note=m.group(0), sentence=w))
                raw[-1].r3_w60 = S.collapse(win(text, m.start(), 60))
                raw[-1].r3_w40 = S.collapse(win(text, m.start(), 40))
        for m in re.finditer(r"\b\d{3,6}\b", art.dec):
            w = S.collapse(win(art.dec, m.start(), wchars))
            if not has_any(w, money, word=False):
                continue
            raw.append(Hit("R3", "T2", art.rel,
                           ctx.surface_at(art, m.start(), S.NORM_DEC),
                           "dec@%d" % m.start(),
                           "%s | %s" % (m.group(0), w),
                           note=m.group(0), sentence=w))
            raw[-1].r3_w60 = S.collapse(win(art.dec, m.start(), 60))
            raw[-1].r3_w40 = S.collapse(win(art.dec, m.start(), 40))
            raw[-1].r3_struct = _t2_structural(ctx, art, art.dec, m.start(),
                                               m.group(0))
        for m in rate.finditer(art.dec):
            w = S.collapse(win(art.dec, m.start(), wchars))
            if not has_any(w, money, word=False):
                continue
            raw.append(Hit("R3", "T2", art.rel,
                           ctx.surface_at(art, m.start(), S.NORM_DEC),
                           "rate@%d" % m.start(),
                           "%s | %s" % (m.group(0), w),
                           note=m.group(0), sentence=w))
            raw[-1].r3_w60 = S.collapse(win(art.dec, m.start(), 60))
            raw[-1].r3_w40 = S.collapse(win(art.dec, m.start(), 40))
            raw[-1].r3_struct = _t2_structural(ctx, art, art.dec, m.start(),
                                               m.group(0))


    # T3 -- the genuine claim test -- reads the generators too, because
    # "the largest rebate" lived in _generate_service_pages.py's
    # CROSS_CONTEXT['attic'] and shipped from there to six pages. T1 and T2
    # deliberately do NOT (Ruling B): the generators embed the citation
    # registry's own deliberately-kept figures.
    for art in ctx.rule_artifacts("R3-T3"):
        for skey, loc, sent in ctx.pool(art):
            rw = which_any(sent, ranks)
            if not rw:
                continue
            if not (has_any(sent, money, word=False) or
                    has_any(sent, progs, ci=True)):
                continue
            raw.append(Hit("R3", "T3", art.rel, skey, str(loc),
                           "%s | %s" % (",".join(rw), sent),
                           note="rank-claim", sentence=sent))

    def f_srccode(h):
        return ctx.src_code_hit(h)

    def f_srcdup(h):
        return ctx.src_dup(h)

    # config.R3.allowed_occurrences was dead, so the figure allowlist was
    # UNBOUNDED: a 21st occurrence of $70,000 passed exactly like the 20
    # the Director ruled on.
    caps = c.get("allowed_occurrences", {}) or {}
    _used = {}
    for _h in sorted(raw, key=lambda x: x.sortkey()):
        k = (_h.note or "").strip()
        if k in allowed:
            _used[k] = _used.get(k, 0) + 1
            if k in caps and _used[k] > int(caps[k]):
                _h.r3_kind = "over-cap"

    def f_allowed(h):
        if getattr(h, "r3_kind", "") == "over-cap":
            return False
        return h.note in allowed or (h.note and h.note.lstrip("$") in
                                     [a.lstrip("$") for a in allowed])

    def f_nonmoney(h):
        return bool(getattr(h, "r3_struct", ""))

    def f_income(h):
        # NARROWED. The income filter matched anywhere in the 120-char window,
        # which removed ALL TWELVE City of Golden rebate caps and 77 of 173
        # $600 hits on DCI because "80% of Area Median Income" happened to sit
        # in the window. An income-eligibility threshold sits BESIDE its
        # phrase and is not a payout, so: the marker must be within 60 chars
        # AND no money word within 40.
        if not has_any(getattr(h, "r3_w60", "") or h.sentence, income,
                       word=False):
            return False
        return not has_any(getattr(h, "r3_w40", "") or "", money, word=False)

    def f_cost(h):
        # SPLIT. LGM's cost_context_markers listed "per square foot" while
        # Efficiency Works DENOMINATES ITS PAYOUT per square foot, and that
        # single marker removed 103 of the 133 banned figures -- 65 x $1.16 and
        # 38 x $0.77. A per-unit marker is no longer sufficient on its own; it
        # now needs a COST noun in the same window.
        if has_any(h.sentence, costs, word=False):
            return True
        if has_any(h.sentence, cost_units, word=False):
            return has_any(h.sentence, cost_nouns, word=False)
        return False

    def f_code(h):
        return has_any(h.sentence, codes, word=False)

    def f_year(h):
        # The old test was re.fullmatch(r"(19|20)\d\d", ...) with no context
        # at all, which silently ate ANY bare-digit rebate amount between 1900
        # and 2099. My first repair required a DATE-VOCABULARY word nearby, and
        # that was worse: DCI R3 went 68 -> 237 adjudicated, 162 of them the
        # bare year in "the 2026 Xcel rebate programs", because a year needs no
        # date word to be a year.
        #
        # This version keeps the blanket clearance but DISCLOSES its one real
        # risk and declines to take it: a four-digit number in 1900-2099 is
        # cleared as a year UNLESS a strong PAYOUT BINDER sits within 40
        # characters ("up to", "pays", "capped at", "rebate of", ...). Those
        # are the constructions in which a bare amount in the year range is
        # actually plausible, and they stay.
        if not (h.note and re.fullmatch(r"(19|20)\d\d", h.note)):
            return False
        # A YEAR PREPOSITION OUTRANKS A PAYOUT BINDER. The binder test looks
        # 40 characters wide, so an unrelated rebate word anywhere in the
        # window re-armed a plain calendar year: GCI's "My home was built
        # after 2010 - is there a rebate worth chasing?" was held because
        # "rebate" is 24 characters away, and its <title> "What Actually Pays
        # in 2026" because "Pays" is 12 away. Neither is a payout.
        # These prepositions cannot precede a MONEY amount in English -- an
        # amount takes "of", "at", "up to", none of which are listed here --
        # so clearing on them cannot hide a bare rebate figure.
        if _T2_YEARPREP.search(getattr(h, "r3_w40", "") or ""):
            return True
        if has_any(getattr(h, "r3_w40", "") or "", year_binders, word=False):
            return False
        return True

    def f_comp(h):
        return has_any(h.sentence, computed, word=False)

    def f_struct(h):
        return has_any(h.sentence, structs, word=False) and h.sub != "T1"

    def f_css(h):
        # Only the NUMERIC-PROPERTY class of CSS false positive (stroke-width,
        # dimensions, z-index). A figure rendered to the visitor through
        # `content:` is a figure the visitor sees, and GCI f0203ad's own note
        # -- "a bare-rate check for 0.75 finds only a CSS stroke-width" -- is
        # about property VALUES, not about content strings.
        return h.surface == "CSS"

    def f_corr(h):
        return has_any(h.sentence, marks, word=False)

    res.raw = raw
    res.adjudicated, res.rows = adjudicate(raw, [
        Filt("the generator SRC surface is a STYLESHEET or a SCRIPT BODY, not "
             "prose -- its quoted string LITERALS are judged separately "
             "under a #strN locator", f_srccode),
        Filt("generator SRC restatement of prose that already renders in public/ (counted once, against the rendered artifact)", f_srcdup),
        Filt("allowed_figures (per-property Director ruling)", f_allowed),
        Filt("structural non-money numeral (URL/attribute, XML or SVG "
             "coordinate, telephone, postal code, statute or print code, "
             "unit phrase, elevation anchor, ISO date)", f_nonmoney),
        Filt("income-eligibility threshold (WAP standing exception)", f_income),
        Filt("cost_context_markers (Ruling 2 -- costs, not payouts)", f_cost),
        Filt("code_context_markers (IECC / ENERGY STAR / R-value)", f_code),
        Filt("four-digit 1900-2099 cleared as a YEAR (kept when a payout "
             "binder is within 40 chars -- BLIND SPOT: a bare rebate amount "
             "in that range with no binder)", f_year),
        Filt("computed_output_markers (Ruling 4 -- visitor arithmetic)", f_comp),
        Filt("allowed_structure_percentages (Ruling 2, none added)", f_struct),
        Filt("CSS surface (stroke-width class of false positive)", f_css),
        Filt("correction marker in scope", f_corr),
    ])
    res.levels, res.level_detail = level_counts(
        ctx, ["$"] + [str(x) for x in (c.get("known_figures") or [])[:8]],
        ci=False, word=False)
    t4 = len([h for h in res.raw if h.surface in ("LD", "JS")])
    over = [h for h in res.adjudicated
            if getattr(h, "r3_kind", "") == "over-cap"]
    if over:
        res.notes.append("ALLOWLIST CAP EXCEEDED: %d occurrence(s) of an "
                         "allowed figure beyond config.allowed_occurrences -- "
                         "the Director ruled on a COUNT, not on a string: %s"
                         % (len(over),
                            ", ".join(sorted(set(h.note for h in over)))))
    if caps:
        res.notes.append("allowlist caps enforced: %s"
                         % ", ".join("%s<=%s" % (k, caps[k])
                                     for k in sorted(caps)))

    res.notes.append("T1 $-anchored %d  ·  T2 bare numeral in a money window "
                     "%d  ·  T3 rank/magnitude/superlative %d  ·  T4 (the LD "
                     "and JS-comment subset of T1+T2) %d"
                     % (len([h for h in raw if h.sub == "T1"]),
                        len([h for h in raw if h.sub == "T2"]),
                        len([h for h in raw if h.sub == "T3"]), t4))
    return "money figures, bare numerals and rank claims found", \
           "figures or rank claims stating what a rebate pays"


R4_KEYS = (S.S_VIS, S.S_TITLE, S.S_META, S.S_OG, S.S_TW, S.S_LD, S.S_JS,
           S.S_LOWVIS, S.S_ATTR, S.S_LLMS, S.S_CITE, S.S_CONST)

# Every R4 class that FAILS. Silence is the compliant state, so a denial fails
# exactly as an assertion does, and the -1P and -SET variants fail exactly as
# their two-named-program parents do. Named ONCE because it is read in three
# places -- the attributed exception, the class counter in the notes, and the
# spec -- and the three had drifted: the exception listed two of the six.
R4_FAIL_CLASSES = ("ASSERTS", "DENIES", "ASSERTS-1P", "DENIES-1P",
                   "ASSERTS-SET", "DENIES-SET")


def rule_R4(ctx, res):
    c = ctx.r("R4")
    toks = c.get("stacking_tokens", []) or []
    preds = c.get("combination_predicates", []) or []
    denials = c.get("denial_markers", []) or []
    programs = c.get("programs", []) or []
    legit = c.get("legitimate_uses", []) or []
    nouns = c.get("noun_use_constants", []) or []
    exc = c.get("attributed_exception", {}) or {}
    marks = ctx.r("R7").get("correction_markers", []) or []
    retired = c.get("retired_prohibition_strings", []) or []
    # ANAPHORIC PROGRAM-SET REFERENCES. A phrase that stands for two or more
    # programs WITHOUT naming any of them. LGM's knob-and-tube denial said
    # "either insulation rebate program" in one sentence and "rebate stacking"
    # three sentences later; every stacking token fired, the sentence reached
    # RAW on both surfaces, and it was cleared anyway with `programs=-` because
    # the two-distinct-programs precondition had nothing to count. The phrase
    # supplies the COUNT, never a name, and the enumerated hit says so.
    setanaph = c.get("program_set_anaphora", []) or []

    raw = []
    # Diagnostics for the two 2026-09-18 repairs, reported rather than silent:
    # a rule that quietly stops seeing something is indistinguishable from a
    # rule that was never wired up.
    n_url_only = 0      # sentences whose ONLY stacking token sat inside a URL
    for art in ctx.rule_artifacts("R4"):
        prev = []
        for skey, loc, src_sent in ctx.pool(art):
            # DEFECT A, 2026-09-18. URL TEXT IS NOT PROSE. See mask_urls().
            # Every match below -- token, predicate, denial, program name,
            # anaphor -- runs against the MASKED sentence; the hit still
            # reports, and the filters still judge, the sentence as written.
            sent = mask_urls(src_sent)
            tk = which_any(sent, toks, word=False)
            if not tk:
                if sent is not src_sent and \
                        has_any(src_sent, toks, word=False):
                    n_url_only += 1
                prev = (prev
                        + [(skey, which_any(sent, setanaph, word=False))])[-2:]
                continue
            named = ctx.programs_in(sent)
            # DEFECT B, 2026-09-18. NO PROGRAM NAME CROSSES A SENTENCE
            # BOUNDARY. R4 used to carry program names forward from the
            # previous two sentences of the same surface and count them toward
            # its own two-distinct-programs precondition. Both of DCI's
            # standing findings printed "(carried from the previous sentence:
            # ...)", and the first of them -- llms.txt S76 -- named exactly one
            # program, "Whole Home Efficiency Bonus", and had "Xcel Energy"
            # imported from its neighbour to reach two. A claim is made by a
            # sentence; a name in the sentence before it is not part of that
            # claim. Both programs must now be named in the flagged sentence.
            #
            # The ANAPHOR carry stays. "either insulation rebate program" is
            # not a program NAME -- it supplies a COUNT and nothing else -- and
            # control R4d exists precisely because LGM wrote the anaphor in one
            # sentence and "rebate stacking" two sentences later
            # (GATE_SCORE_2026-09-17.md MISS 5). Removing that carry would
            # delete a scored detection, which is the failure mode this repair
            # is not allowed to cause.
            carried_anaph = []
            for pk, pa in prev:
                if pk == skey:
                    carried_anaph += pa
            anaph = sorted(set(which_any(sent, setanaph, word=False))
                           | set(carried_anaph))
            prev = (prev
                    + [(skey, which_any(sent, setanaph, word=False))])[-2:]
            allnamed = sorted(set(named))
            if len(set(allnamed)) < 2 and anaph:
                # The sentence (or one within two sentences of it on the same
                # surface) refers to the program SET without naming it. That is
                # two or more programs by construction, so the claim is judged
                # on its predicate rather than pardoned for a name count it
                # could never satisfy. Classified into its OWN sub-tests, so
                # this loosening is visible in every enumeration and has a
                # control of its own rather than hiding inside DENIES/ASSERTS.
                if not has_any(sent, preds, word=False):
                    cls = "NEUTRAL"
                elif has_any(sent, denials, word=False):
                    cls = "DENIES-SET"
                else:
                    cls = "ASSERTS-SET"
            elif len(set(allnamed)) < 2:
                # SINGLE-PROGRAM STACKING CLASS. R4's two-distinct-programs
                # requirement removed the LGM knob-and-tube denial, the GCI
                # FAQPage denial, the DCI llms.txt claim and the 70-page DCI
                # boilerplate. "Xcel rebate-stack eligibility" names ONE
                # program and still asserts combinability. One program plus a
                # combination predicate within 60 chars of it is the claim.
                one = allnamed[0] if allnamed else None
                near = False
                if one and has_any(sent, preds, word=False):
                    # Look for the canonical name AND every alias that maps to
                    # it. "Xcel rebate-stack eligibility" contains the ALIAS
                    # "Xcel", never the canonical "Xcel Energy", so a lookup on
                    # the canonical name alone found no position and the
                    # single-program class never fired on the very line it was
                    # written for.
                    spots = list(occ(sent, one, ci=True))
                    for alias, canon in sorted(
                            (c.get("program_aliases", {}) or {}).items()):
                        if canon == one:
                            spots += occ(sent, alias, ci=True)
                    for pos in sorted(set(spots)):
                        if has_any(win(sent, pos, 60), preds, word=False):
                            near = True
                            break
                if near:
                    cls = ("DENIES-1P" if has_any(sent, denials, word=False)
                           else "ASSERTS-1P")
                else:
                    cls = "NEUTRAL"
            elif not has_any(sent, preds, word=False):
                cls = "NEUTRAL"
            elif has_any(sent, denials, word=False):
                cls = "DENIES"
            else:
                cls = "ASSERTS"
            pubs = exc.get("publishers") or \
                ([exc["publisher"]] if exc.get("publisher") else [])
            pub = None
            for cand in pubs:
                if has(sent, cand, ci=True):
                    pub = cand
                    break
            need_pub = exc.get("requires_publisher_named", True)
            need_key = exc.get("requires_cited_source_key", True)
            # THE EXCEPTION APPLIES TO ALL SIX FAILING CLASSES, not just the
            # two that existed when it was written.
            #
            # This read `cls in ("ASSERTS", "DENIES")`. The -1P classes landed
            # 2026-09-17 and the -SET classes 2026-09-18, and neither was wired
            # into the exception this same loop already computes for every hit,
            # so "attributed" was reachable only from the two-named-programs
            # branch. Nothing about the exception depends on how many programs
            # a sentence names: it asks whether the publisher is named in THIS
            # sentence and whether THIS artifact resolved a cite key, and both
            # questions are answered above, identically, in every branch.
            #
            # Found BY the Defect B repair, which is what makes it a real gap
            # and not a tidy-up. Dropping the cross-sentence name carry moved
            # LGM's attributed Efficiency Works hedge -- "Ask your contractor
            # or the programs directly before counting on Efficiency Works'
            # combined figure", 3 pages x 2 surfaces -- out of ASSERTS, where
            # it was licensed by lgm.json's attributed_exception (publisher
            # "Efficiency Works", basis ground-truth.md:27-44), into
            # ASSERTS-1P, where the identical attribution could not be seen.
            # Same sentence, same publisher, same resolved cite key, opposite
            # verdict -- and LGM is wired into regen_all.sh under `set -e`.
            # Held by control R4g and its repaired counterpart.
            if cls in R4_FAIL_CLASSES and exc.get("allowed", True) \
                    and (pub or not need_pub) \
                    and (art.cite_keys or not need_key):
                cls = "ATTRIBUTED-AND-SOURCED"
            # The hit REPORTS the sentence as written -- URLs and all -- so the
            # reader adjudicates the real line. `sentence=` is likewise the
            # written form, because the seven filters below are filters: they
            # only ever REMOVE a hit, and src_dup() in particular probes the
            # first 48 characters against the rendered corpus, which is the
            # written form too.
            raw.append(Hit("R4", cls, art.rel, skey, str(loc),
                           "%s | programs=%s%s%s | %s"
                           % (",".join(tk), ",".join(allnamed) or "-",
                              (" (URL text masked before matching; the tokens "
                               "above are from prose only)")
                              if sent is not src_sent else "",
                              (" (program SET named anaphorically, not by "
                               "name: %s)" % ",".join(anaph)) if anaph else "",
                              src_sent),
                           note=cls, sentence=src_sent))

    def f_srccode(h):
        return ctx.src_code_hit(h)

    def f_srcdup(h):
        return ctx.src_dup(h)

    def f_legit(h):
        return has_any(h.sentence, legit, word=False)

    def f_neutral(h):
        return h.sub == "NEUTRAL"

    def f_attr(h):
        return h.sub == "ATTRIBUTED-AND-SOURCED"

    def f_noun(h):
        for n in nouns:
            v = ctx.gen.constants.get(n)
            if isinstance(v, str):
                p = _const_probe(v)
                if p and p in h.sentence:
                    return True
        return False

    def f_retired(h):
        return has_any(h.sentence, retired, word=False)

    def f_corr(h):
        return has_any(h.sentence, marks, word=False)

    res.raw = raw
    res.adjudicated, res.rows = adjudicate(raw, [
        Filt("the generator SRC surface is a STYLESHEET or a SCRIPT BODY, not "
             "prose -- its quoted string LITERALS are judged separately "
             "under a #strN locator", f_srccode),
        Filt("generator SRC restatement of prose that already renders in public/ (counted once, against the rendered artifact)", f_srcdup),
        Filt("legitimate_uses (stack effect, plumbing stack, can lights)", f_legit),
        Filt("NEUTRAL -- fewer than two distinct programs, or no predicate",
             f_neutral),
        Filt("ATTRIBUTED-AND-SOURCED (publisher named + cite key resolved)",
             f_attr),
        Filt("noun_use_constants (a noun for the program set)", f_noun),
        Filt("retired prohibition preserved as a record", f_retired),
        Filt("correction marker in scope", f_corr),
    ])
    res.levels, res.level_detail = level_counts(
        ctx, ["stack", "on top of", "layer", "combin"], word=False)
    n = lambda s: len([h for h in res.adjudicated if h.sub == s])  # noqa: E731
    res.notes.append("%s  ·  all six FAIL: silence is the compliant state and "
                     "affirmative denial is equally a defect"
                     % "  ·  ".join("%s %d" % (s, n(s))
                                    for s in R4_FAIL_CLASSES))
    res.notes.append("-SET classes are claims whose programs are named "
                     "ANAPHORICALLY -- 'either insulation rebate program', "
                     "'both rebate programs' -- so the phrase supplies the "
                     "COUNT and never a name. Reported as their own sub-tests "
                     "because that is a loosening, and a loosening that hides "
                     "inside an existing class cannot be controlled or "
                     "measured.")
    res.notes.append("URL TEXT IS NOT PROSE (2026-09-18): %d sentence(s) "
                     "carried a stacking token ONLY inside a URL and were "
                     "dropped before classification. A slug is chosen for "
                     "search and asserts nothing; controls R4e (fires) and "
                     "repaired/R4e (must not) hold this. TIGHTENING, so it is "
                     "counted rather than silent -- a rule that quietly stops "
                     "seeing something reads exactly like a rule that was "
                     "never wired up." % n_url_only)
    res.notes.append("NO PROGRAM NAME CROSSES A SENTENCE BOUNDARY "
                     "(2026-09-18): both programs must be named in the "
                     "flagged sentence. R4 used to import names from the "
                     "previous two sentences of the same surface to reach its "
                     "own two-distinct-programs count. The ANAPHOR carry is "
                     "unaffected -- an anaphor is a count, not a name, and "
                     "control R4d depends on it. Controls R4f (fires) and "
                     "repaired/R4f (must not) hold this.")
    return "stacking tokens resolved to sentences", \
           "sentences that assert or deny that programs combine"


R5_KEYS = (S.S_VIS, S.S_TITLE, S.S_META, S.S_OG, S.S_TW, S.S_LD, S.S_JS,
           S.S_LOWVIS, S.S_LLMS, S.S_SVGTEXT)


_R5_STOP = frozenset((
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "is",
    "are", "was", "were", "be", "by", "with", "that", "this", "it", "as",
    "at", "from", "your", "you", "we", "our", "can", "will", "not", "but",
    "than", "then", "so", "if", "most", "more", "up"))

# INFLECTIONAL suffixes only. `-er` / `-ers` USED TO BE HERE AND WAS WRONG:
# it is DERIVATIONAL, so it folded `heater`->`heat`, `corner`->`corn` and
# `batter`->`batt`, and it made a base form fold harder than its own inflection
# (`better`->`bett` while `bettered`->`better`). The seventh adversarial read
# produced a live silent miss out of exactly that collision -- "a 42% reduction
# in attic HEATER runtime loss" scoring against a citation about HEAT. Removed.
_R5_SUFFIX = ("ings", "ing", "ies", "ied", "ed", "es", "s")
# The other half of the same defect: the fold UNDER-collapsed the words R5
# actually keys on. `lose` / `loss` / `lost` are three of R5's own
# magnitude_words and produced three different stems; `reduce` and `reduction`
# produced two. Suffix stripping cannot reach those, so they are declared.
# Small, closed, and confined to the vocabulary this rule is built on.
_R5_LEMMA = {
    "lose": "loss", "loses": "loss", "losing": "loss", "lost": "loss",
    "loss": "loss", "losses": "loss",
    "reduce": "reduc", "reduces": "reduc", "reduced": "reduc",
    "reducing": "reduc", "reduction": "reduc", "reductions": "reduc",
    "save": "save", "saves": "save", "saved": "save", "saving": "save",
    "savings": "save",
    "settle": "settl", "settles": "settl", "settled": "settl",
    "settling": "settl", "settlement": "settl", "settlements": "settl",
    "seal": "seal", "seals": "seal", "sealed": "seal", "sealing": "seal",
    "insulate": "insul", "insulates": "insul", "insulated": "insul",
    "insulating": "insul", "insulation": "insul",
    "cut": "cut", "cuts": "cut", "cutting": "cut",
    "increase": "increas", "increases": "increas", "increased": "increas",
    "increasing": "increas",
    "improve": "improv", "improves": "improv", "improved": "improv",
    "improving": "improv", "improvement": "improv",
    "improvements": "improv",
}
_R5_ALNUM = re.compile(r"(?<=[a-z])(?=[0-9])")
# Named, not inlined, so the before/after of any future re-derivation can be
# run without editing the predicate. See f_instat for the measured sweep.
_R5_INSTAT_MIN = 4
# Characters either side of the numeral that count toward the overlap. Wide
# enough to hold a clause, narrow enough that a second clause cannot pay for
# the first. Named so a future re-derivation can sweep it without editing the
# predicate.
_R5_INSTAT_WIN = 110
# How near the figure a derivable constant's subject phrase must sit. A
# sentence is not an allowlist key; the phrase has to govern THAT number.
_R5_DERIV_WIN = 60


def _r5_fold(w):
    if w in _R5_LEMMA:
        return _R5_LEMMA[w]
    for suf in _R5_SUFFIX:
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[:-len(suf)]
    if w.endswith("e") and len(w) >= 5:
        return w[:-1]
    return w


def _r5_words(s):
    """Content words of a sentence, folded so that the same word written two
    ways is one token.

    TWO FOLDS, EACH WITH A MEASURED ROW BEHIND IT:
      * `CFM50` splits at the letter/digit boundary, because DCI writes the
        unit as `CFM50` in prose and `CFM 50` in the quotation that sources it,
        and the unshifted tokenizer scored those as two unrelated words.
      * `settles` / `settling` / `settled` / `settle` fold to one stem, because
        DCI restates the Building America Solution Center's `will settle from
        10 to 20 percent` as `settles 10 to 20 percent` and was condemned for
        the conjugation.
    Deliberately crude: this is a same-claim test between two sentences on one
    page, not a search index. A wrong fold can only move the overlap count, and
    the threshold it feeds is measured against the one pair it must separate.
    """
    out = set()
    for w in re.findall(r"[a-z]+", _R5_ALNUM.sub(" ", s.lower())):
        if len(w) >= 3 and w not in _R5_STOP:
            out.add(_r5_fold(w))
    return out


def _r5_local_overlap(a, b, num):
    """Shared content words in the WINDOW AROUND `num` in `a` and in `b`.

    ONE MECHANISM, TWO CALLERS, ON PURPOSE. This is the body that used to sit
    inline inside `f_instat`, lifted out verbatim so that `f_question` asks the
    SAME question of a question/anchor pair that `f_instat` asks of a
    sentence/cited-stat pair. The eighth adversarial read's finding A1 was
    precisely that the two did not ask the same question: `f_instat` demanded
    four shared content words in a window and `f_question` demanded ZERO,
    matching on the bare numeral token alone. A second, weaker same-claim test
    is how an unrelated attributed figure came to license an uncited claim that
    merely shared a numeral, so there is no second test any more -- there is
    this function, and both callers compare its result against
    `_R5_INSTAT_MIN`.

    Returns the BEST overlap over every pairing of occurrences of `num`, which
    is what the inlined loop did by returning True on the first pairing to
    reach the threshold.
    """
    best = 0
    for sp in occ(a, num, ci=True, word=False):
        sw = _r5_words(win(a, sp, _R5_INSTAT_WIN))
        if not sw:
            continue
        for tp in occ(b, num, ci=True, word=False):
            n = len(sw & _r5_words(win(b, tp, _R5_INSTAT_WIN)))
            if n > best:
                best = n
    return best


# WHAT COUNTS AS AN INTERROGATIVE AT ALL -- AND WHY THIS LIST IS SAFE WHERE
# THE 2026-09-19 GUARD'S LIST WAS NOT.
#
# A TAG QUESTION IS A FLAT ASSERTION PLUS ONE CHARACTER. `f_question` tested
# `sentence.endswith("?")` and nothing else, so
#
#   "Attic insulation cuts your heating bill by 20%, right?"
#   "Homes lose 40% of their heat through the attic, right?"
#
# received the interrogative pardon while asserting their figures as flatly as
# any declarative on the site. Ending in `?` is punctuation, not grammar.
#
# THE DIRECTION OF THE TEST IS THE WHOLE DIFFERENCE FROM THE GUARD THAT WAS
# REMOVED. That guard enumerated 24 interrogatives and CLEARED anything opening
# with one; an incomplete enumeration therefore FAILED OPEN, and worse, `Why
# does X?` and `How does X?` presuppose X, so the enumeration cleared ten
# sentences that assert their figure. This list is a NECESSARY CONDITION for
# `f_question` to apply at all, never a sufficient one: a sentence that does not
# open with one of these tokens is treated as an ASSERTION and is judged by
# every other filter exactly as a declarative would be. An incomplete
# enumeration here therefore FAILS SHUT -- the cost of a missing token is a
# genuine question judged as an assertion, which fires, which is the direction
# an adversarial read cannot exploit.
#
# PRESUPPOSITION IS NOT HANDLED HERE AND DOES NOT NEED TO BE. "Why settle for
# less when our crews measure a 36% reduction in heating costs?" opens with
# `Why` and is an interrogative by this test -- and it still fires, because
# `f_question` goes on to require an ATTRIBUTED SAME-CLAIM ANCHOR that a site
# asserting its own unsourced measurement does not have. The anchor
# requirement, not the opener list, is what closes presupposition.
_R5_Q_OPENERS = frozenset((
    # wh-words
    "who", "whom", "whose", "what", "whatever", "which", "whichever",
    "when", "where", "why", "how", "howto",
    # auxiliaries and modals, inverted
    "is", "are", "was", "were", "am", "be", "been",
    "do", "does", "did", "have", "has", "had",
    "can", "could", "will", "would", "shall", "should",
    "may", "might", "must", "ought", "need", "dare",
    # the negated contractions of the same, first alpha run only
    "isn", "aren", "wasn", "weren", "don", "doesn", "didn", "hasn",
    "haven", "hadn", "can", "couldn", "won", "wouldn", "shouldn",
    "mustn", "mightn", "shan", "needn", "ain",
))
# A trailing TAG -- a comma, then a short coda, then the question mark.
# "…, right?", "…, no?", "…, correct?", "…, or not?", "…, don't you think?".
# Matched AFTER the opener test and OR-ed with it, because a sentence can open
# with an auxiliary and still end in a tag: "Does it matter that homes lose 40%
# of their heat through the attic, or not?" presupposes the 40% just as flatly.
_R5_TAG_RE = re.compile(r",\s*[A-Za-z'][A-Za-z']{0,11}"
                        r"(?:\s+[A-Za-z'][A-Za-z']{0,11}){0,2}\s*\?\s*$")


def _r5_is_interrogative(s):
    """True only for a sentence that is interrogative in FORM, not merely in
    punctuation. See `_R5_Q_OPENERS` for why this is restrictive and why an
    omission fails shut."""
    s = (s or "").strip()
    if not s.endswith("?"):
        return False
    if _R5_TAG_RE.search(s):
        return False
    m = re.match(r"[^A-Za-z]*([A-Za-z]+)", s)
    if not m:
        return False
    return m.group(1).lower() in _R5_Q_OPENERS


# ---------------------------------------------------------------------------
# R5: A STYLESHEET IS NOT PROSE AND A SCRIPT BUNDLE IS NOT A FINDING.
#
# surfaces.src_artifact() emits EVERY tokenize-joined string run of 12 or more
# characters in a generator module. That is right for R2, R3-T3, R4 and R7,
# which are looking for a program name or a dollar figure wherever it hides.
# It is wrong for R5, which asks whether a quantified magnitude PRESENTED AS A
# FINDING ABOUT THE WORLD carries an attribution -- and a generator's inline
# stylesheet and its scroll-reveal bundle are neither findings nor about the
# world:
#
#   .form-row--cw { position: absolute; left: -9999px; top: 0; width: 1px;
#                   height: 1px; overflow: hidden; }        -> 0%, 100%, 50%
#   new IntersectionObserver(..., { threshold: 0.15,
#                   rootMargin: '0px 0px -8% 0px' });       -> 8%
#
# MEASURED, not guessed. Over all 6,203 generator string runs of 40+ characters
# on the three properties, the fraction of characters lying inside a braced
# block separates cleanly and with a wide empty gap:
#
#   6,166 runs at 0.00        prose, markup, JSON-LD, copy
#       1 run  at 0.074       a citation-provenance note that quotes a regex
#      --- nothing at all between 0.08 and 0.67 ---
#      36 runs at 0.67-1.00   stylesheets and script bundles, every one of them
#
# The threshold is 0.40, in the middle of an empty gap nine times its own
# width, and it is CORROBORATED: a run must also carry at least five CSS
# declarations or at least three JavaScript markers. Density alone would be a
# single number to fool; density plus corroboration means a run has to look
# like code twice, in two unrelated ways.
#
# BLIND SPOT, STATED: a generator string that is MOSTLY prose with a small
# script tag inside it is prose to this test, so a figure inside that script
# still reads as a claim. That is the safe direction -- this filter can only
# fail to exclude, never exclude a page claim -- and control R5-SRCCODE's
# fixture half is what proves the prose direction stays open.
# ---------------------------------------------------------------------------

_SRC_CSS_DECL = re.compile(
    r"[{;]\s*[-a-zA-Z][-a-zA-Z0-9]{1,30}\s*:\s*[^;{}]{1,200};")
_SRC_JS_MARK = re.compile(
    r"\bfunction\s*\(|=>|\bvar\s+\w+\s*=|\blet\s+\w+\s*=|\bconst\s+\w+\s*=|"
    r"document\s*\.|window\s*\.|addEventListener|querySelector|"
    r"'use strict'|\"use strict\"|\breturn\b|\btypeof\b|JSON\.parse|"
    r"\.classList|\.forEach\(|\bnew [A-Z]\w+\(")
_SRC_CODE_MIN_DENSITY = 0.40


def _src_brace_density(t):
    """Fraction of characters that sit INSIDE a braced block."""
    if not t:
        return 0.0
    depth = inside = 0
    for ch in t:
        if ch == "{":
            depth += 1
        elif ch == "}":
            if depth:
                depth -= 1
        elif depth:
            inside += 1
    return inside / float(len(t))


def _src_is_code(t):
    if not t or len(t) < 40:
        return False
    if _src_brace_density(t) < _SRC_CODE_MIN_DENSITY:
        return False
    return (len(_SRC_CSS_DECL.findall(t)) >= 5
            or len(_SRC_JS_MARK.findall(t)) >= 3)


# Quoted string literals inside a code run. This is the claim-bearing half of a
# script bundle and it is NOT excluded: `el.innerHTML = 'Atmos Energy is the
# natural gas utility for Denver homes'` is a wrong-utility claim wherever it is
# written, and the rendered page reads exactly this set out of the same bytes
# (surfaces.Artifact.js_strings). A DEVELOPER COMMENT is not in this set, which
# is the whole distinction: `// Atmos does not serve three of the nine towns`
# is a note about the code, and the rendered page does not read it either.
_SRC_STRLIT = re.compile(
    r"'((?:\\.|[^'\\])*)'"
    r'|"((?:\\.|[^"\\])*)"'
    r"|`((?:\\.|[^`\\])*)`", re.DOTALL)
_SRC_LIT_MIN = 12


def _src_code_literals(t):
    out = []
    for m in _SRC_STRLIT.finditer(t or ""):
        v = (m.group(1) or m.group(2) or m.group(3) or "").strip()
        if len(v) >= _SRC_LIT_MIN and re.search(r"[A-Za-z]{3,}", v):
            out.append(S.collapse(v))
    return out


# THE INTERROGATIVE GUARD WAS REMOVED ON 2026-09-19 AND MUST NOT COME BACK IN
# THAT SHAPE. It cleared any sentence ending `?` that opened with one of 24
# interrogatives and carried none of 13 hardcoded factive frames. The seventh
# adversarial read measured it: 11 of 13 test interrogatives cleared and TEN OF
# THOSE ELEVEN ASSERT THEIR FIGURE --
#   "Why settle for less when our crews measure a 36% reduction in heating
#    costs?"          and          "How our crews cut heating costs by 39%?"
# `Why does X?` and `How does X?` PRESUPPOSE X, and that is this portfolio's own
# heading idiom. The guard shipped a list of 13 IDIOMS against a grammatical
# CLASS, and presupposition is not enumerable that way. It bought three DCI rows
# that f_instat clears on its own merits and cost eight proven evasions, so it
# is a net loss and it is gone (Rule 2: no dead anything, and no guard that
# costs more than it buys).
# ---------------------------------------------------------------------------
# R5: THE PUBLISHER AS THE FIGURE'S SUBJECT, NOT AS ITS NEIGHBOUR.
#
# f_pub cleared a hit when a recognised publisher sat within 80 characters of
# the figure AND the sentence carried a verb from R1.attribution_verbs. That
# list has no "estimates", so
#
#   "ENERGY STAR estimates a 15% heating-and-cooling cost reduction from
#    adequate insulation plus air sealing."
#
# was condemned for lacking the attribution it plainly has. Adding "estimates"
# to the verb list was PROBED AND REFUSED: it silently clears
#
#   "ENERGY STAR estimates vary, but our crews measure a 35% reduction in
#    heating costs."
#
# where the publisher sits 47 characters from the figure, well inside the
# window, and proximity launders the site's own unsourced measurement behind a
# name that never made the claim. (Measured: DCI R5 ADJ 32 -> 28 with
# "estimates" added, and that probe cleared.)
#
# What separates them is not distance and not vocabulary. It is GRAMMAR: in the
# first, the publisher is the SUBJECT of the verb and the figure is inside the
# verb's complement. In the second, "estimates" is a plural NOUN, the real
# subject of the figure's clause is "our crews", and a contrastive clause
# boundary sits between the publisher and the figure. So:
#
#   S1  publisher (optionally possessive, optionally with its own noun phrase)
#       IMMEDIATELY followed by an attributing verb, the figure AFTER that verb,
#       and NO clause boundary between the verb and the figure.
#   S2  the reduced-relative form the llms.txt index uses -- the figure, then
#       within 80 characters a POSSESSIVE publisher with its noun phrase and a
#       verb, and no clause boundary between: "the before-and-after 20% CFM50
#       reduction Xcel's air sealing rebate requires."
#
# BLIND SPOT, STATED: this is adjacency and punctuation, not a parser. A
# publisher separated from its verb by an appositive longer than four words
# reads as no attribution, and a clause boundary written without punctuation or
# a coordinator ("ENERGY STAR estimates vary our crews measure 35%") is
# invisible to it. Controls R5-SUBJECT (fires) and repaired/R5-SUBJECT (must
# not) hold both directions.
# ---------------------------------------------------------------------------

# WHERE AN ATTRIBUTION STOPS.
#
# The first version required a COMMA before a coordinator, and the seventh
# adversarial read defeated it by deleting one character:
#   "ENERGY STAR estimates vary, but our crews measure a 35% ..."  FIRES
#   "ENERGY STAR estimates vary and our crews measure a 36% ..."   CLEARED
# Making bare "and" a boundary is not the answer either -- "a 15% heating and
# cooling cost reduction" would break the attribution it is part of. What
# actually ends an attribution is a NEW SUBJECT taking over, so the coordinator
# is a boundary when a subject pronoun or a first-person possessive follows it,
# with or without the comma.
#
# A RELATIVE PRONOUN IS ALSO A BOUNDARY. That closes the payer-laundering
# sentence the read built:
#   "Xcel's air sealing rebate requires work THAT cut our customers' bills 38%"
# where the figure belongs to the relative clause, not to what Xcel requires.
_R5_NEWSUBJ = (r"(?:our|we|us|my|i|their|they|his|her|its|it|you|your|he|she|"
               r"this|these|those)")
_R5_CLAUSE_BREAK = re.compile(
    r"[;:]"
    r"|\s[-‐-―]+\s"
    r"|,\s*(?:but|and|yet|so|while|whereas|though|although|however|"
    r"nevertheless|still|then|or)\b"
    r"|\s(?:but|however|whereas|although|though|nevertheless)\s"
    r"|[,\s]\s*(?:but|and|yet|so|or|while|whereas)\s+" + _R5_NEWSUBJ + r"\b"
    r"|\s(?:that|which|who|whom|whose|where|when)\s",
    re.IGNORECASE)

# AN ATTRIBUTION THAT DENIES ITSELF IS NOT AN ATTRIBUTION. The read produced
#   "ENERGY STAR reports no such 44% reduction in heating costs anywhere."
#   "ENERGY STAR's website says nothing about our 42% reduction ..."
# and both were read as carrying the attribution they explicitly refuse.
_R5_DENIAL = re.compile(
    r"\b(?:no\s+such|nothing\s+about|never|no\s+longer|not\s+|n't\b|"
    r"denies|denied|disputes|disputed|refutes|contradicts|declines\s+to|"
    r"says\s+nothing|makes\s+no|offers\s+no|publishes\s+no|has\s+no|"
    r"without\s+any|neither|nor\b|unsupported|unsourced)", re.IGNORECASE)

# HOW FAR AN ATTRIBUTION REACHES. The read measured the shipped predicate at
# UNBOUNDED: a single 376-character run with no internal punctuation cleared.
# An attribution is a clause, not a paragraph.
_R5_SUBJ_REACH = 120
# A possessive tail: "'s <document noun phrase>" -- "ENERGY STAR's duct
# sealing guidance says", "Xcel's air sealing rebate requires".
_R5_POSS = r"(?:'s|’s|&rsquo;s|&#8217;s)"
_R5_ADV = r"(?:also\s+|further\s+|now\s+|currently\s+|separately\s+)?"
# THE NOUN PHRASE MUST END IN SOMETHING THAT CAN PUBLISH. It used to be four
# words of anything, and those four words became the real subject:
#   "ENERGY STAR's CRITICS say our 43% savings number is invented."
#   "ENERGY STAR's LAWYERS say our 58% savings claim is actionable."
# Critics and lawyers are not the publisher. The head noun is now required to
# be a document, a publication or a programme -- the kinds of thing an
# organisation issues and can therefore be quoted from. Config-driven
# (R5.publisher_artifact_nouns) because it is a vocabulary, not a rule.
_R5_NP = r"(?:[A-Za-z0-9][\w.-]*\s+){0,3}"


def _r5_alt(words):
    return "|".join(re.escape(v) for v in sorted(words, key=len, reverse=True))


def _r5_poss_np(nouns):
    """`'s <=3 words> <artifact noun>` -- the publisher's own document."""
    return r"%s\s+%s(?:%s)\b\s+" % (_R5_POSS, _R5_NP, _r5_alt(nouns))


def _r5_subject_pat(name, verbs, nouns, require_poss):
    key = ("S1", name, tuple(verbs), tuple(nouns), require_poss)
    p = _R5_SUBJ_CACHE.get(key)
    if p is None:
        # A SHORT FORM IS ONLY EVER POSSESSIVE. `_pub_subject` strips the
        # possessive off "Xcel's" so this pattern can attach its own, and while
        # the possessive group was OPTIONAL that made the BARE TOKEN `Xcel` a
        # publisher -- flatly contradicting the config note shipped beside it
        # ("the bare token 'Xcel' ... must never be added"), and reopening
        # payer laundering. For a short form the possessive is now mandatory.
        poss = _r5_poss_np(nouns)
        head = (r"%s\b\s*%s" % (re.escape(name), poss) if require_poss
                else r"%s\b\s*(?:%s)?" % (re.escape(name), poss))
        p = re.compile(r"%s%s(%s)\b" % (head, _R5_ADV, _r5_alt(verbs)),
                       re.IGNORECASE)
        _R5_SUBJ_CACHE[key] = p
    return p


def _r5_relative_pat(name, verbs, nouns):
    key = ("S2", name, tuple(verbs), tuple(nouns))
    p = _R5_SUBJ_CACHE.get(key)
    if p is None:
        p = re.compile(r"%s\s*%s(%s)\b"
                       % (re.escape(name), _r5_poss_np(nouns),
                          _r5_alt(verbs)), re.IGNORECASE)
        _R5_SUBJ_CACHE[key] = p
    return p


_R5_SUBJ_CACHE = {}


def _pub_subject(sentence, nums, pubs, shorts, verbs, nouns):
    """True when a recognised publisher is the SUBJECT that attributes one of
    `nums`, by S1 or S2 above.

    `shorts` are POSSESSIVE short forms (config R5.publisher_short_forms) and
    are usable ONLY here, ONLY in possessive form. "Xcel" alone is the PAYER on
    almost every page in this portfolio; the seventh adversarial read proved
    that an optional possessive group made the bare token a publisher and
    reopened payer laundering, so `require_poss` is set for every short form.
    """
    if not verbs or not nouns:
        return False
    positions = []
    for n in nums:
        n = (n or "").strip()
        if not n:
            continue
        positions.extend(occ(sentence, n, ci=True, word=False))
    if not positions:
        return False

    def _reaches(a, b):
        """An attribution reaches across one clause, not one paragraph, and it
        does not survive its own denial."""
        span = sentence[a:b]
        if len(span) > _R5_SUBJ_REACH:
            return False
        if _R5_CLAUSE_BREAK.search(span):
            return False
        return not _R5_DENIAL.search(span)

    # S1 -- publisher as the subject of the verb, figure in its complement.
    for name, poss_only in ([(x, False) for x in pubs]
                            + [(x, True) for x in shorts]):
        if not name:
            continue
        base = re.sub(r"(?:'s|\u2019s)$", "", name)
        for m in _r5_subject_pat(base, verbs, nouns, poss_only).finditer(
                sentence):
            v = m.end()
            # The DENIAL test also looks at the verb itself: "reports no such"
            # is one phrase and the negation follows the verb.
            for p in positions:
                if p > v and _reaches(v, p):
                    return True

    # S2 -- the figure, then the possessive publisher that requires it.
    for name in list(pubs) + list(shorts):
        if not name:
            continue
        base = re.sub(r"(?:'s|\u2019s)$", "", name)
        for m in _r5_relative_pat(base, verbs, nouns).finditer(sentence):
            st = m.start()
            for p in positions:
                if 0 < st - p <= 80 and _reaches(p, st):
                    return True
    return False


def rule_R5(ctx, res):
    c = ctx.r("R5")
    pats = [re.compile(p) for p in (c.get("magnitude_patterns") or [])]
    words = c.get("magnitude_words", []) or []
    pubs = c.get("recognised_publishers", []) or []
    shorts = c.get("publisher_short_forms", []) or []
    subj_verbs = c.get("subject_attribution_verbs", []) or []
    artifact_nouns = c.get("publisher_artifact_nouns", []) or []
    attrib_verbs = ctx.r("R1").get("attribution_verbs", []) or []
    computed = c.get("computed_output_markers", []) or []
    derivs = c.get("derivable_constants", []) or []
    known = c.get("known_uncited", []) or []
    codes = ctx.r("R3").get("code_context_markers", []) or []
    code_nouns = ctx.r("R3").get("code_noun_markers", []) or []
    structs = ctx.r("R3").get("allowed_structure_percentages", []) or []
    thresh = ctx.r("R3").get("allowed_thresholds", []) or []
    tctx = ctx.r("R3").get("threshold_context_markers", []) or []
    marks = ctx.r("R7").get("correction_markers", []) or []

    raw = []
    for art in ctx.rule_artifacts("R5"):
        stats = " || ".join(x["txt"] for x in art.cited_stats)
        cs_txt = [x["txt"] for x in art.cited_stats]
        for skey, loc, sent in ctx.pool(art):
            found = []
            for p in pats:
                for m in p.finditer(sent):
                    found.append(m.group(0).strip())
            if not found:
                continue
            if not has_any(sent, words, word=False):
                continue
            nums = sorted(set(found))
            inblock = any(sent[:60] in t for t in cs_txt)
            instat = bool(stats) and all(n in stats for n in nums)
            ko = ""
            for k in known:
                if isinstance(k, dict) and k.get("text") and \
                        k["text"] in sent:
                    ko = "KNOWN-OPEN %s" % k.get("status", "")
            h = Hit("R5", "mag", art.rel, skey, str(loc),
                    "%s | %s" % (",".join(nums), sent),
                    note=ko or "uncited", sentence=sent)
            h.r5_inblock = inblock
            h.r5_instat = instat
            h.r5_stats = [x["txt"] for x in art.cited_stats
                          if any(n in x["txt"] for n in nums)]
            raw.append(h)

    def f_srccode(h):
        return ctx.src_code_hit(h)

    def f_srcdup(h):
        return ctx.src_dup(h)

    def _open(pred):
        """No filter may remove a KNOWN-OPEN hit. config.known_uncited carries
        provenance so the gate can print KNOWN-OPEN beside the hit; it does NOT
        suppress it. A silenced hit is precisely the "filter silently dropped a
        real hit" failure spec 4 exists to prevent."""
        def f(h):
            if h.note.startswith("KNOWN-OPEN"):
                return False
            return pred(h)
        return f

    def f_inblock(h):
        return getattr(h, "r5_inblock", False)

    def f_instat(h):
        # A numeral SUBSTRING present in ANY cited-stat on the page cleared the
        # hit page-wide. That is how DCI's live uncited "15% reduction in
        # heating and cooling costs" was nearly cleared by an UNRELATED ENERGY
        # STAR 15% on the same page. The figure must therefore share content
        # words with the stat that is supposed to attribute it.
        #
        # THE THRESHOLD IS 4, AND IT IS 4 BECAUSE IT WAS MEASURED, NOT PICKED.
        # It was 3, then raised to 5 to separate "see a 15% reduction in
        # heating and cooling costs" from "save an average of 15% on heating
        # and cooling costs" -- the same numeral, a different claim, overlap
        # exactly 3. Five was too coarse in the other direction: a SHORT
        # restatement of a LONG verbatim quotation cannot reach five shared
        # words no matter how plainly the quotation attributes it.
        #
        # MEASURED NEAR-MISS SWEEP, 2026-09-19, all three properties, every
        # live hit that reaches this filter (DCI 237, LGM 49, GCI 32 -- the
        # instat-eligible raw hits not already cleared by src_dup or inblock):
        #
        #   normalization   min overlap   left uncleared at threshold 3/4/5/6
        #   DCI  shipped          3          0 /  7 / 17 / 26
        #   DCI  +fold            3          0 /  3 / 11 / 20
        #   LGM  shipped          6          0 /  0 /  0 /  0
        #   LGM  +fold            7          0 /  0 /  0 /  0
        #   GCI  shipped          3          0 /  3 /  5 /  7
        #   GCI  +fold            3          0 /  1 /  5 /  5
        #
        # NOT ONE live hit on any property scores below 3, and every hit read
        # at 3, 4 and 5 is a genuine same-page attribution of the same figure
        # by the same publisher about the same subject. So 3 is the floor the
        # corpus shows -- and 3 is exactly where the documented false clear
        # sits, which is why the threshold is 4 and not 3. Four is the smallest
        # value that keeps that pair separated. Measured on the pair itself,
        # under all three tokenizations tried: overlap 3.
        #
        # THE TOKENIZER, NOT THE THRESHOLD, WAS MOST OF THE DEFECT.
        # `settles` and `settle` were different tokens, and `CFM50` and
        # `CFM 50` were different tokens, so a restatement was penalised for
        # English morphology rather than for saying something else. Folding
        # both (see _r5_words) moves DCI's uncleared count at threshold 4 from
        # 7 to 3 and does not move the false-clear pair off 3.
        # THE COUNT ALONE WAS THE REAL DEFECT, NOT ITS VALUE.
        # An overlap taken over two WHOLE SENTENCES counts words that have
        # nothing to do with the number. The seventh adversarial read built the
        # counterexample and it is a true silent miss at any threshold this
        # instrument can justify:
        #
        #   stat : "According to the EPA, 42% of homes built before 1980 have
        #           attic bypasses that turn winter heat into pure loss,
        #           something EPA field crews still find on most inspections."
        #   site : "Our crews measured a 42% reduction in attic heat loss
        #           after air sealing."
        #
        # The EPA's 42% is about housing-stock age; the site's 42% is about
        # heat-loss reduction. Different claims, same numeral, no attribution.
        # Whole-sentence overlap is {attic, crews, heat, loss} = 4 and it
        # CLEARED. My original sweep could not see this: it measured only
        # FALSE POSITIVES -- hits left standing -- so it could structurally
        # only ever argue for loosening. That criticism is correct.
        #
        # THE FIX IS TO BIND THE SHARED VOCABULARY TO THE FIGURE. The overlap
        # is now taken over the WINDOW AROUND THE NUMERAL in each text, not
        # over the whole sentence, so words earned in a different clause do not
        # pay for this one. On the pair above the local overlap is {attic} = 1
        # and it FIRES. On the restatement it is meant to clear --
        # "Loose-fill cellulose settles 10 to 20 percent" against
        # "loose-fill cellulose will settle from 10 to 20 percent over time" --
        # the local overlap is {loose, fill, cellulose, settl, percent} = 5 and
        # it clears. On the documented false-clear pair it is 3 and stays shut.
        if not getattr(h, "r5_instat", False):
            return False
        nums = [x.strip() for x in
                (h.text.split(" | ")[0] or "").split(",") if x.strip()]
        #
        # THE LOOP THAT USED TO BE INLINE HERE IS NOW `_r5_local_overlap`, so
        # that f_question asks the identical same-claim question of its
        # question/anchor pair. Behaviour here is unchanged: the helper returns
        # the best overlap over every pairing of occurrences and this compares
        # it against the same `_R5_INSTAT_MIN`.
        for st in getattr(h, "r5_stats", []) or []:
            for n in nums:
                if _r5_local_overlap(h.sentence, st, n) >= _R5_INSTAT_MIN:
                    return True
        return False

    def f_deriv(h):
        # R5.derivable_constants WAS DECLARED IN THE KEY LIST AND READ BY NO
        # CODE PATH. A previous session wrote an entry for the atmospheric
        # pressure figure, watched no FILTER line appear, and removed it rather
        # than ship dead config -- correctly, and the gap stayed open.
        #
        # A PHYSICAL CONSTANT IS NOT A STATISTIC. R5 asks for an attribution
        # because a percentage presented as a finding about the world has a
        # publisher who found it. "Atmospheric pressure at Denver's elevation
        # is roughly 17% lower than sea level" has no publisher any more than
        # water's boiling point at altitude does: it follows from the ICAO
        # standard atmosphere, P/P0 = (1 - 2.25577e-5*h)^5.25588, which at
        # h = 1,609.3 m gives 0.8234 -- 17.66% lower.
        #
        # THE FIRST WIRING OF THIS WAS AN ALLOWLIST AND THE SEVENTH ADVERSARIAL
        # READ WAS RIGHT TO SAY SO. It ran an unanchored, page-global substring
        # test, so prepending six words to canon's OWN control fixture cleared
        # the sentence the control asserts must fire:
        #   "Atmospheric pressure has nothing to do with it: Denver homes we
        #    treat show a 17% lower heating bill in the first winter"
        # a non-derivable 42% rode along inside the same hit, and
        # `derivation_note` was checked for non-emptiness so that the literal
        # text "Because I said so" suppressed a fabricated 63%.
        #
        # FOUR BINDINGS NOW, EACH CLOSING ONE OF THOSE:
        #   1. PAGES. The entry names the artifacts it governs and is ignored
        #      without them, so it cannot be property-global.
        #   2. PROXIMITY. A subject phrase must sit within
        #      `_R5_DERIV_WIN` characters of THAT occurrence of the figure, so
        #      naming the subject somewhere else in the sentence buys nothing.
        #   3. EVERY NUMERAL. Every figure in the hit must be covered by some
        #      entry, so a non-derivable number cannot ride along with one.
        #   4. A DERIVATION THAT IS A DERIVATION. `derivation_note` must carry
        #      digits AND an arithmetic operator. That is a STRUCTURAL test,
        #      not a semantic one -- it cannot tell a right formula from a
        #      wrong one, and it is not claimed to. It does stop a sentence of
        #      prose from standing in for one.
        nums = [x.strip() for x in
                (h.text.split(" | ")[0] or "").split(",") if x.strip()]
        if not nums:
            return False
        rel = str(h.rel)
        base = rel.rsplit("/", 1)[-1]
        covered = set()
        for d in derivs:
            if not isinstance(d, dict):
                continue
            fig = (d.get("figure") or "").strip()
            phrases = [p for p in (d.get("subject_phrases") or []) if p]
            pages = [p for p in (d.get("pages") or []) if p]
            note = (d.get("derivation_note") or "").strip()
            if not fig or not phrases or not pages:
                continue
            if not (re.search(r"[0-9]", note)
                    and re.search(r"[=^*/\u00d7\u00f7]", note)):
                continue
            if not any(rel == p or base == p or rel.endswith("/" + p)
                       or base == p.rsplit("/", 1)[-1] for p in pages):
                continue
            if fig not in nums:
                continue
            # DISTANCE BETWEEN THE TWO OCCURRENCES, not a substring window: a
            # phrase that straddles a window edge is still the subject of the
            # number, and a phrase 77 characters away introducing a DIFFERENT
            # claim is not. 60 is the measured separation between DCI's three
            # real forms (gaps 4, 10 and 34) and the read's nearest
            # falsification (gap 66).
            done = False
            for pos in occ(h.sentence, fig, ci=True, word=False):
                for ph in phrases:
                    for pp in occ(h.sentence, ph, ci=True, word=False):
                        if abs(pp - pos) <= _R5_DERIV_WIN:
                            covered.add(fig)
                            done = True
                            break
                    if done:
                        break
                if done:
                    break
        return bool(covered) and all(n in covered for n in nums)

    # A PARENTHETICAL CITATION IS AN ATTRIBUTION AND HAS NO VERB.
    # f_pub below requires an attribution VERB, which is right for prose
    # ("According to X, ...") and blind to the commonest citation form in
    # existence: "... settles 10-20% over its life (Building America Solution
    # Center)." Four GCI sentences were adjudicated UNCITED while naming, in
    # parentheses immediately after the figure, a publisher already in
    # recognised_publishers -- the gate was asking for a source that was
    # already there, in the standard form for giving one.
    # Narrow by construction: the publisher must sit INSIDE parentheses, and
    # those parentheses must open within 120 characters of the figure. A
    # publisher merely mentioned in the sentence still does not qualify, so
    # the "Xcel Energy as the PAYER, not the publisher" false clear that
    # motivated the verb requirement stays closed.
    _PAREN_RE = re.compile(r"\(([^()]{0,200})\)")

    def _paren_cite(sentence, nums):
        spans = [(m.start(), m.group(1)) for m in _PAREN_RE.finditer(sentence)]
        if not spans:
            return False
        for n in nums:
            n = (n or "").strip()
            if not n:
                continue
            for pos in occ(sentence, n, ci=True, word=False):
                for start, inner in spans:
                    if abs(start - pos) <= 120 and has_any(inner, pubs, ci=True):
                        return True
        return False

    def f_pub(h):
        # A publisher named ANYWHERE in the sentence used to exempt it. That
        # removed the only two 25-40% rows on one page because "Xcel Energy"
        # appears there as the PAYER, not as the publisher of the figure. An
        # attribution needs an attribution VERB and the publisher near the
        # figure -- not merely an organisation's name somewhere in the clause.
        if _pub_subject(h.sentence,
                        (h.text.split(" | ")[0] or "").split(","),
                        pubs, shorts, subj_verbs, artifact_nouns):
            return True
        if not has_any(h.sentence, pubs, ci=True):
            return False
        if not has_any(h.sentence, attrib_verbs, word=False):
            if _paren_cite(h.sentence,
                           (h.text.split(" | ")[0] or "").split(",")):
                return True
            return False
        nums = (h.text.split(" | ")[0] or "").split(",")
        for n in nums:
            n = n.strip()
            if not n:
                continue
            for pos in occ(h.sentence, n, ci=True, word=False):
                if has_any(win(h.sentence, pos, 80), pubs, ci=True):
                    return True
        return False

    def f_comp(h):
        return has_any(h.sentence, computed, word=False)

    def f_code(h):
        # WAS: naming ENERGY STAR (or IECC, or any code marker) ANYWHERE in the
        # sentence pardoned any uncited statistic in it, through a filter whose
        # stated purpose is CODE CONTEXT. "ENERGY STAR homes differ, but our
        # crews measure a 35% reduction in heating costs" was cleared by it --
        # the same blanket-pardon shape f_pub had. NOW: the marker must be
        # within 60 chars of the figure AND a code/standard noun must be near
        # it, so the marker has to actually govern the number.
        if not has_any(h.sentence, codes, word=False):
            return False
        if not has_any(h.sentence, code_nouns, word=False):
            return False
        nums = (h.text.split(" | ")[0] or "").split(",")
        for n in nums:
            n = n.strip()
            if not n:
                continue
            for pos in occ(h.sentence, n, ci=True, word=False):
                if has_any(win(h.sentence, pos, 60), codes, word=False):
                    return True
        return False

    def f_struct(h):
        if not has_any(h.sentence, list(structs) + list(thresh), word=False):
            return False
        return has_any(h.sentence, tctx, word=False)

    def f_corr(h):
        return has_any(h.sentence, marks, word=False)

    # AN INTERROGATIVE ASSERTS NOTHING -- BUT ONLY WHERE THE PAGE ASSERTS IT
    # SOMEWHERE ELSE, ATTRIBUTED.
    #
    # R5 asserts over figures "presented as a finding about the world". A
    # question presents no finding; it asks about one. DCI's FAQ heading
    #   "What happens if the after test does not reach a 20% CFM50 reduction?"
    # was adjudicated uncited on THREE surfaces (LD, LOWVIS, VIS) on a page
    # that carries, inside a cited-stat, "the qualifying minimum standard for
    # the air sealing rebate is a 20% reduction in CFM 50", attributed to Xcel
    # Energy's residential rebate summary -- the same figure, the same claim,
    # the same publisher, on the same page.
    #
    # WHY f_instat CANNOT REACH IT, AND WHY NEITHER OBVIOUS LOOSENING IS
    # AVAILABLE. Measured 2026-09-19 with the gate's own _r5_words/win/occ:
    #
    #   pair                                     overlap  |window|  coverage
    #   the CFM50 question vs its cited-stat        3         8       0.375
    #   the documented false-clear pair             3        13       0.308
    #   the seventh read's 42% counterexample       3         9       0.333
    #
    # Dropping _R5_INSTAT_MIN from 4 to 3 reopens both rows that must stay
    # shut -- the exact widening this rule was rebuilt to stop. A COVERAGE
    # test is no way out either: 0.375 against 0.333 is one point of
    # separation, which is a coincidence, not an instrument. The count is not
    # the defect here. The defect is that a short interrogative has eight
    # content words in total and cannot earn four of anything, however
    # completely it restates the sentence that sources it.
    #
    # THIS IS NOT "SKIP QUESTIONS", AND THE DIFFERENCE IS THE WHOLE FILTER.
    # A question can smuggle a claim -- "Did you know homes lose 40% of their
    # heat through the attic?" is an assertion wearing a question mark -- so a
    # blanket interrogative skip is precisely the blindfold that must not be
    # built. This filter requires a NON-INTERROGATIVE ANCHOR that is on the
    # same FILE and the same SURFACE, that ALREADY CLEARED R5 THROUGH AN
    # ATTRIBUTION FILTER -- f_inblock (it IS a cited-stat), f_instat (the
    # page's cited-stat attributes that figure) or f_pub (it names the
    # publisher that made the claim) -- and that makes THE SAME CLAIM,
    # measured by the same window overlap f_instat uses.
    #
    # ============================================================= A1 =======
    # WHAT THE 2026-09-19 SHIPMENT OF THIS FILTER ACTUALLY DID, AND WHY IT WAS
    # A LAUNDERING ROUTE. As shipped it collected the bare NUMERAL TOKENS of
    # every cleared non-interrogative on the FILE and cleared a question when
    # `all(n in anchors)`. No content relation between the question and its
    # anchor was required at all. The same rule's f_instat demanded four shared
    # content words in a window around the figure; f_question demanded ZERO.
    # Measured 2026-09-20, every one of these cleared before this rewrite and
    # fires after it (fixtures/R5k_question_numeral_laundering.html):
    #
    #   attributed anchor (unrelated claim)      uncited question sharing only
    #                                            the numeral
    #   EPA, 42% of pre-1980 homes have attic    "Did our crews really measure a
    #   bypasses                                  42% reduction in attic heat
    #                                             loss after air sealing?"
    #   Xcel, 20% CFM 50 rebate threshold        "Did you know attic insulation
    #                                             cuts your heating bill by 20%?"
    #   Xcel, 63% call-centre wait time          63% attic moisture
    #   NOAA, 71% Front Range solar output       71% furnace efficiency
    #   ENERGY STAR, 28% duct leakage            28% whole-house heat loss
    #   EPA 34% + NOAA 57%, jointly              one two-figure question
    #   ENERGY STAR, 40% duct-sealing efficiency "Did you know homes lose 40% of
    #                                             their heat through the attic?"
    #
    # THE LAST ROW IS THIS RULE'S OWN SPEC BEING VIOLATED. RULES_SPEC.md says
    # that question "must keep firing" and that "the 40% example above fires".
    # With ONE unrelated attributed 40% anywhere on the page it did not fire.
    #
    # AND THE FIX PROOF CONTAINED THE HOLE. repaired/R5j paired an ENERGY STAR
    # statistic about ANNUAL SPACE-CONDITIONING ENERGY USE with a question about
    # WINTER HEATING COSTS -- different claims -- and bfbad20's own commit
    # message recorded that pair's local overlap as 0. The pass measured the
    # hole and recorded it as proof the control exercises the filter. That
    # fixture's anchor is rewritten here to state the claim its question asks
    # about, so the control tests a same-claim anchor rather than a numeral.
    #
    # ANCHORING WAS ALSO CROSS-SURFACE. `_anchored` filtered on h2.rel, the
    # FILE, and never on the SURFACE, so a <meta name="description">, a JSON-LD
    # string leaf or an inline <script> template literal could anchor a claim
    # made in visible prose, and visible prose could anchor a claim buried in
    # JSON-LD FAQ markup. The spec's src_code/src_dup exclusion covers GENERATOR
    # SRC surfaces only and never closed this. Both directions are measured in
    # fixtures/R5m_cross_surface_anchor.html and both now fire.
    #
    # A TAG QUESTION IS A FLAT ASSERTION PLUS ONE CHARACTER, and the old test
    # was `endswith("?")`. See _r5_is_interrogative above, and
    # fixtures/R5l_tag_question.html.
    #
    # THE THRESHOLD IS NOT NEGOTIABLE DOWNWARD AND THE BLOWER-DOOR ROW IS NOT
    # RESCUED HERE. Measured 2026-09-20 with _r5_local_overlap, window 110:
    #
    #   pair                                                        overlap
    #   DCI's CFM50 question vs the cited-stat that sources it          3
    #   the documented false-clear pair (15% save vs 15% reduction)     3
    #   the seventh read's 42% counterexample                           3
    #   the eighth read's 42% INTERROGATIVE counterexample              3
    #
    # A question/anchor overlap rule CANNOT separate them: at 4 the blower-door
    # row fires, at 3 the 42% interrogative evasion clears. That is a measured
    # conclusion, not a preference, and lowering _R5_INSTAT_MIN to rescue the
    # blower-door row would reopen the pair the threshold exists to keep shut.
    # The blower-door row is therefore closed by the instrument the spec
    # ALREADY declares for it -- R3.allowed_thresholds, per-property and
    # figure-scoped, requiring a threshold_context_marker in the same sentence
    # (f_struct above). See RULES_SPEC 10.2 and the R5 exclusion list, which
    # names "the 20% CFM 50 threshold -- same exclusion set as R3, same
    # classifier". DCI's entry was empty, which lanes.md recorded as an open
    # finding on 2026-09-19; it is filled in here.
    # ========================================================================
    #
    # WHAT IT CANNOT HIDE -- STRUCTURALLY, NOT BY ASSERTION:
    #   * No same-surface sentence carries the figure -> no anchor -> the
    #     question fires.
    #   * A same-surface sentence carries the figure, is attributed, but makes
    #     a DIFFERENT claim -> local overlap below _R5_INSTAT_MIN -> the
    #     question fires. This is the whole of A1.
    #   * A companion sentence carries the figure but is ITSELF uncited -> it
    #     is not in the cleared set, so it anchors nothing, AND R5 fires on
    #     it. The figure is caught either way; it is merely caught at the
    #     sentence that asserts it.
    #   * The anchor is on another SURFACE of the same file -> it anchors
    #     nothing. A meta description does not source visible prose and
    #     visible prose does not source JSON-LD.
    #   * The other filters are deliberately NOT anchors. src_code and
    #     src_dup mean "judged elsewhere", not "attributed";
    #     computed_output_markers means "the visitor's own arithmetic", which
    #     sources nothing; deriv/code/struct/corr say the figure is not a
    #     finding, which is a statement about THAT sentence and does not
    #     transfer. Only the three filters that assert an attribution EXISTS
    #     may anchor.
    #   * A sentence ending in `?` can never anchor anything -- including a TAG
    #     question, which this filter treats as an assertion when deciding
    #     whether it FIRES but still refuses as an anchor. Deliberately
    #     asymmetric, and asymmetric in the only safe direction: it can add
    #     hits, never remove them.
    #   * EVERY figure in the hit must be anchored BY A SAME-CLAIM ANCHOR, so a
    #     second, unsourced numeral cannot ride along inside the same question,
    #     and two unrelated publishers cannot jointly pay for one question.
    #   * _open() still applies: a KNOWN-OPEN hit is never removed by it.
    #
    # CONTROLS. R5-QUESTION fires 3x on fixtures/R5j_interrogative_anchor.html
    # BEFORE and AFTER -- one question with no anchor at all, one whose only
    # companion is uncited, plus that companion. R5-QLAUNDER, R5-QTAG and
    # R5-QSURFACE are the three A1 controls: each fixture measured 0 hits
    # before this rewrite and fires after, and each has a repaired counterpart
    # that must be clean, so none of the three can be satisfied by simply
    # switching the filter off.
    _ANCHORS = {}

    def _anchor_sents(rel, skey):
        """Attributed, non-interrogative anchors on ONE file AND ONE surface,
        as (figures, sentence) pairs -- the sentence is kept because the bare
        figure set is exactly what A1 proved insufficient."""
        key = (rel, skey)
        got = _ANCHORS.get(key)
        if got is None:
            got = []
            for h2 in raw:
                if str(h2.rel) != rel or str(h2.surface) != skey:
                    continue
                if (h2.sentence or "").strip().endswith("?"):
                    continue
                if not (f_inblock(h2) or f_instat(h2) or f_pub(h2)):
                    continue
                ns = set(n.strip() for n in
                         (h2.text.split(" | ")[0] or "").split(",")
                         if n.strip())
                if ns:
                    got.append((ns, h2.sentence or ""))
            _ANCHORS[key] = got
        return got

    def f_question(h):
        if not _r5_is_interrogative(h.sentence):
            return False
        nums = [x.strip() for x in
                (h.text.split(" | ")[0] or "").split(",") if x.strip()]
        if not nums:
            return False
        anchors = _anchor_sents(str(h.rel), str(h.surface))
        if not anchors:
            return False
        for n in nums:
            if not any(n in ns
                       and _r5_local_overlap(h.sentence, sent, n)
                       >= _R5_INSTAT_MIN
                       for ns, sent in anchors):
                return False
        return True

    res.raw = raw
    res.adjudicated, res.rows = adjudicate(raw, [
        Filt("the generator SRC surface is a STYLESHEET or a SCRIPT BODY, not "
             "prose -- its quoted string LITERALS are judged separately "
             "under a #strN locator", _open(f_srccode)),
        Filt("generator SRC restatement of prose that already renders in "
             "public/ (counted once, against the rendered artifact)",
             _open(f_srcdup)),
        Filt("the sentence IS a cited-stat block (attributed by construction)",
             _open(f_inblock)),
        Filt("R5.derivable_constants -- a physical constant with a recorded "
             "derivation, not a finding with a publisher",
             _open(f_deriv)),
        Filt("the figure appears in a cited-stat rendered on this page "
             "(attribution is PAGE-scoped here, not sentence-scoped)",
             _open(f_instat)),
        Filt("recognised_publishers named in the same sentence", _open(f_pub)),
        Filt("computed_output_markers (Ruling 4 -- visitor arithmetic)",
             _open(f_comp)),
        Filt("code_context_markers (IECC / ENERGY STAR / R-value)",
             _open(f_code)),
        Filt("allowed structure percentage / tier threshold IN a threshold "
             "context", _open(f_struct)),
        Filt("correction marker in scope", _open(f_corr)),
        Filt("the sentence is a QUESTION and the same figure is asserted, "
             "attributed, in a non-question sentence on the same page "
             "(a question presents no finding -- the assertion is judged, "
             "and an UNATTRIBUTED companion anchors nothing)",
             _open(f_question)),
    ])
    res.levels, res.level_detail = level_counts(
        ctx, ["% reduction", "15% reduction", "20-40%"], ci=False, word=False)
    nko = len([h for h in res.adjudicated if h.note.startswith("KNOWN-OPEN")])
    res.notes.append("of the adjudicated hits, %d are KNOWN-OPEN from "
                     "config.known_uncited -- carried with provenance, NEVER "
                     "suppressed (spec R5)" % nko)
    return "quantified magnitude claims found", \
           "magnitude claims with no attribution on the page"


_JS_COND = re.compile(r"\b(?:else\s+if|if)\s*\(")
_JS_ELSE = re.compile(r"\belse\s*\{")
_JS_ASSIGN = re.compile(r"([A-Za-z_$][\w$]*)\s*=\s*([^;]*)")
_JS_ANYSTR = re.compile(
    r"'((?:[^'\\]|\\.)*)'" r'|"((?:[^"\\]|\\.)*)"' r"|`((?:[^`\\]|\\.)*)`",
    re.DOTALL)
_JS_STRIPSTR = re.compile(
    r"'(?:[^'\\]|\\.)*'" r'|"(?:[^"\\]|\\.)*"' r"|`(?:[^`\\]|\\.)*`",
    re.DOTALL)


def _match_paren(s, i):
    depth = 0
    for j in range(i, len(s)):
        c = s[j]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return j
    return -1


_JS_ALIAS = re.compile(
    r"""(?:var|let|const)\s+([A-Za-z_$][\w$]*)\s*=\s*"""
    r"""document\s*\.\s*(?:getElementById\s*\(\s*['"]([^'"]+)['"]\s*\)"""
    r"""|querySelector\s*\(\s*['"]#([^'"]+)['"]\s*\))""")
_JS_VARASSIGN = re.compile(
    r"""(?:^|[;{}\n])\s*(?:var\s+|let\s+|const\s+)?"""
    r"""([A-Za-z_$][\w$]*)\s*(?:\+)?=\s*([^;]{0,4000}?);""", re.S)
_JS_SINKS = r"(?:value|textContent|innerHTML|innerText)"
_JS_STRLIT = re.compile(r"""(['"`])((?:\\.|(?!\1).)*)\1""")
_JS_IDENT = re.compile(r"[A-Za-z_$][\w$]*")


def _assigned_literals(js, ident):
    """String literals that can end up in the DOM node addressed by `ident`.

    Deliberately shallow and deterministic: resolve `var X = getElementById
    ('id')` aliases, find `X.value = RHS` / `.textContent =` / `.innerHTML =`
    / `.innerText =` and `getElementById('id').value = RHS`, then take every
    string literal in RHS plus every string literal assigned anywhere to a
    plain variable named in RHS. That covers the real shape -- a label chosen
    into a variable and then written to both the visible node and the hidden
    field -- without pretending to be an interpreter.

    It does NOT evaluate. A verdict assembled arithmetically, fetched, or
    built by a function call whose body it cannot follow is invisible to it,
    and R9's blind-spot line says so.
    """
    alias = {}
    for m in _JS_ALIAS.finditer(js):
        alias.setdefault(m.group(2) or m.group(3), set()).add(m.group(1))
    names = set(alias.get(ident, set()))
    pats = [r"document\s*\.\s*getElementById\s*\(\s*['\"]%s['\"]\s*\)\s*\.\s*%s\s*=\s*([^;\n]+)"
            % (re.escape(ident), _JS_SINKS),
            r"document\s*\.\s*querySelector\s*\(\s*['\"]#%s['\"]\s*\)\s*\.\s*%s\s*=\s*([^;\n]+)"
            % (re.escape(ident), _JS_SINKS)]
    for n in sorted(names):
        pats.append(r"\b%s\s*\.\s*%s\s*=\s*([^;\n]+)" % (re.escape(n),
                                                         _JS_SINKS))
    # Every literal reachable from a plain variable, plus one round of
    # substitution so `var html = '<p>' + headline + '</p>'` carries the
    # headline's own labels. The direction of error here is deliberate: a
    # literal wrongly ADDED to the visible set can only SUPPRESS an N3b
    # finding, never create one, so widening the resolver cannot manufacture a
    # false positive on a blocking sub-test.
    varlit, varrefs = {}, {}
    for m in _JS_VARASSIGN.finditer(js):
        name, rhs = m.group(1), m.group(2)
        for lm in _JS_STRLIT.finditer(rhs):
            if lm.group(2).strip():
                varlit.setdefault(name, set()).add(lm.group(2))
        blank = _JS_STRLIT.sub(" ", rhs)
        for im in _JS_IDENT.finditer(blank):
            if im.group(0) != name:
                varrefs.setdefault(name, set()).add(im.group(0))
    for name in sorted(varrefs):
        for ref in sorted(varrefs[name]):
            if ref in varlit:
                varlit.setdefault(name, set()).update(varlit[ref])
    out = set()
    for p in pats:
        for m in re.finditer(p, js):
            rhs = m.group(1)
            for lm in _JS_STRLIT.finditer(rhs):
                if lm.group(2).strip():
                    out.add(lm.group(2))
            blank = _JS_STRLIT.sub(" ", rhs)
            for im in _JS_IDENT.finditer(blank):
                out |= varlit.get(im.group(0), set())
    return set(x.strip() for x in out if x.strip())


def _js_label_chain(js_text, labels):
    """POSITION-based conditional-chain scanner over the emitted JS.

    Rewritten after the adversarial read: the previous version iterated
    splitlines() and anchored `^if (...)` per line, so the SAME defect minified
    onto one line produced a byte-identical clean block. Conditions are now
    located by position with real parenthesis matching, and each label
    assignment is bound to the nearest PRECEDING condition regardless of
    newlines. Backtick template literals are included.

    Returns (branches, stats) where branches is a list of
    (cond_idents, cond_numbers, cond_text, label_text, interpolated_idents,
     has_condition) and stats is a dict of real denominators.
    """
    conds = []
    for m in _JS_COND.finditer(js_text):
        o = js_text.find("(", m.start())
        if o < 0:
            continue
        c = _match_paren(js_text, o)
        if c < 0:
            continue
        conds.append((m.start(), js_text[o + 1:c]))
    for m in _JS_ELSE.finditer(js_text):
        conds.append((m.start(), ""))
    conds.sort()

    assigns = []
    for m in _JS_ASSIGN.finditer(js_text):
        rhs = m.group(2)
        parts = [a or b or c for a, b, c in _JS_ANYSTR.findall(rhs)]
        flat = "".join(parts)
        if not flat:
            continue
        if not any(lb and lb[:18] in flat for lb in labels):
            continue
        bare = _JS_STRIPSTR.sub(" ", rhs)
        idents = sorted(set(re.findall(r"[A-Za-z_$][\w$]*", bare)))
        assigns.append((m.start(), flat, idents))

    branches = []
    for pos, flat, idents in assigns:
        cond = None
        for cp, ct in conds:
            if cp < pos:
                cond = ct
            else:
                break
        if cond is None:
            branches.append(([], (), "", flat, idents, False))
            continue
        cidents = sorted(set(re.findall(r"[A-Za-z_$][\w$]*", cond))
                         - {"true", "false", "null", "undefined"})
        nums = tuple(int(x) for x in re.findall(r"\b\d+\b", cond))
        branches.append((cidents, nums, S.collapse(cond), flat, idents, True))

    labels_present = sorted(set(lb for lb in labels
                                if lb and lb[:18] in js_text))
    stats = {
        "conditions_located": len(conds),
        "label_assignments": len(assigns),
        "branches_with_condition": len([b for b in branches if b[5]]),
        "labels_present_in_text": len(labels_present),
        "ternary_present": "?" in js_text and ":" in js_text,
        "switch_present": bool(re.search(r"\bswitch\s*\(", js_text)),
    }
    return branches, stats


def rule_R6(ctx, res):
    c = ctx.r("R6")
    chains = c.get("label_chains", []) or []
    tot = {"chains": 0, "conds": 0, "assigns": 0, "branches": 0,
           "labels_seen": 0, "texts": 0}
    if not chains:
        res.notes.append("NULL RESULT -- 0 label chains configured for this "
                         "property. Registering one later is a config entry.")
        res.raw = []
        res.adjudicated, res.rows = adjudicate([], [])
        res.levels, res.level_detail = level_counts(ctx, ["short of target"],
                                                    ci=False, word=False)
        res.notes.append("DENOMINATOR  chains examined 0 · JS texts read 0 · "
                         "conditions located 0 · label assignments found 0 · "
                         "branches bound to a condition 0 -- RAW 0 here means "
                         "NOTHING WAS REGISTERED, not 'clean'")
        return "label-emitting conditional chains examined", \
               "chains whose branch quantity is not the printed quantity"

    raw = []
    for ch in chains:
        tot["chains"] += 1
        labels = ch.get("labels", []) or []
        pv = ch.get("printed_var")
        at = ch.get("at_target_label") or ""
        order = ch.get("severity_order", []) or []
        targets = ch.get("targets", {}) or {}
        cid = ch.get("id", "?")
        texts = []
        for pth in (ch.get("surfaces") or []):
            a = ctx.by_rel.get(pth) or ctx.by_rel.get(pth.rsplit("/", 1)[-1])
            if a:
                for i, body in enumerate(a.js_bodies):
                    texts.append(("%s:JS[%d]" % (a.rel, i), body))
        gen = ch.get("generator")
        if gen and not ctx.control:
            # NEVER read the repo from a control context (isolation, spec 5).
            gp = os.path.join(ctx.repo or "", gen)
            if os.path.isfile(gp):
                with open(gp, "r", encoding="utf-8", errors="replace") as fh:
                    texts.append((gen, fh.read()))
            else:
                raw.append(Hit("R6", "UNREGISTERED", cid, "SRC", cid,
                               "chain %s names generator %r which does not "
                               "exist in this repo -- the chain is registered "
                               "and unreadable" % (cid, gen),
                               note="generator-missing", sentence=cid))
        tot["texts"] += len(texts)
        if not texts:
            if ctx.control:
                # A control corpus legitimately lacks the property's surfaces.
                continue
            raw.append(Hit("R6", "UNREGISTERED", cid, "SRC", cid,
                           "chain %s: no surface or generator text found -- "
                           "registered and unreadable" % cid,
                           note="unreachable", sentence=cid))
            continue
        chain_seen = {"labels": 0, "assigns": 0, "conds": 0}
        for loc, body in texts:
            branches, st = _js_label_chain(body, labels)
            chain_seen["labels"] = max(chain_seen["labels"],
                                       st["labels_present_in_text"])
            chain_seen["assigns"] += st["label_assignments"]
            chain_seen["conds"] += st["conditions_located"]
            tot["conds"] += st["conditions_located"]
            tot["assigns"] += st["label_assignments"]
            tot["branches"] += st["branches_with_condition"]
            tot["labels_seen"] = max(tot["labels_seen"],
                                     st["labels_present_in_text"])

            if st["labels_present_in_text"] >= 2 and \
                    st["branches_with_condition"] < st["labels_present_in_text"] - 1:
                shape = []
                if st["switch_present"]:
                    shape.append("switch")
                if st["ternary_present"]:
                    shape.append("ternary")
                raw.append(Hit(
                    "R6", "UNPARSEABLE", loc, "JS", loc,
                    "chain %s: %d configured labels present in this text but "
                    "only %d branch(es) bound to a condition%s -- the gate "
                    "cannot read this chain and will not call it clean"
                    % (cid, st["labels_present_in_text"],
                       st["branches_with_condition"],
                       (" (shape: %s)" % "+".join(shape)) if shape else ""),
                    note="unparseable", sentence=loc))

            sev = [b for b in branches if not (at and at[:18] in b[3])]

            for cidents, nums, ctext, label, idents, hascond in sev:
                if pv and pv not in idents:
                    continue
                if not hascond:
                    continue
                extra = [x for x in cidents
                         if x not in (pv, "Math", "t", "true", "false")]
                if extra:
                    raw.append(Hit("R6", "G1", loc, "JS", loc,
                                   "branch reads {%s} while the printed string "
                                   "interpolates {%s} | cond: %s | %s"
                                   % (",".join(cidents), pv, ctext,
                                      label[:80]),
                                   note="G1", sentence=label))
                    for area, tmin in sorted(targets.items()):
                        for n in nums:
                            if isinstance(tmin, int) and n > tmin:
                                raw.append(Hit(
                                    "R6", "G2", loc, "JS",
                                    "%s/%s" % (loc, area),
                                    "threshold %d on {%s} is unreachable for "
                                    "%s (targetMin %d) while the printed "
                                    "quantity can reach 100"
                                    % (n, ",".join(cidents), area, tmin),
                                    note="G2", sentence=label))

            # --- the named defect class: two severity words beside the SAME
            # --- printed value. Duplicate or overlapping thresholds on the
            # --- printed quantity, and duplicate condition text.
            on_pv = [(nums, ctext, label) for cidents, nums, ctext, label,
                     idents, hascond in sev
                     if hascond and nums and (not pv or pv in cidents)]
            seen_thr = {}
            for nums, ctext, label in on_pv:
                key = nums[0]
                seen_thr.setdefault(key, []).append((ctext, label))
            for key in sorted(seen_thr):
                if len(seen_thr[key]) > 1:
                    labs = sorted(set(S.collapse(l)[:40]
                                      for _, l in seen_thr[key]))
                    raw.append(Hit(
                        "R6", "G2-DUP", loc, "JS", "%s@%s" % (loc, key),
                        "threshold %s on {%s} is tested by %d branches, so %d "
                        "different labels are reachable at the SAME printed "
                        "value: %s" % (key, pv, len(seen_thr[key]),
                                       len(labs), " | ".join(labs)),
                        note="two-labels-one-value", sentence=str(key)))
            ctexts = {}
            for nums, ctext, label in on_pv:
                ctexts.setdefault(ctext, []).append(label)
            for ct in sorted(ctexts):
                if len(ctexts[ct]) > 1:
                    raw.append(Hit(
                        "R6", "G2-DUP", loc, "JS", "%s#%s" % (loc, ct),
                        "condition %r appears on %d label-emitting branches -- "
                        "only the first is reachable and the labels disagree"
                        % (ct, len(ctexts[ct])),
                        note="duplicate-condition", sentence=ct))

            thr = [n[0][0] for n in
                   [(nums,) for nums, _, _ in on_pv] if n[0]]
            if thr and (thr != sorted(thr, reverse=True) or
                        len(set(thr)) != len(thr)):
                raw.append(Hit("R6", "G2", loc, "JS", "%s:monotone" % loc,
                               "branch thresholds %s on {%s} are not STRICTLY "
                               "monotone decreasing" % (thr, pv),
                               note="G2", sentence=str(thr)))
            labs = [b[3] for b in sev if b[5]]
            ranks = []
            for lb in labs:
                for i, o in enumerate(order):
                    if o[:18] in lb:
                        ranks.append(i)
            if ranks and ranks != sorted(ranks, reverse=True):
                raw.append(Hit("R6", "G2", loc, "JS", "%s:order" % loc,
                               "label order %s disagrees with "
                               "config.severity_order" % (labs,), note="G2",
                               sentence=str(labs)))

        # ZERO DENOMINATOR IS A FINDING, NOT A PASS -- judged ONCE PER CHAIN,
        # across all of its texts. The denominator line says in its own words
        # that this state means BLIND, and the gate was printing it beside
        # VERDICT PASS and exiting 0: renaming a calculator's four severity
        # words, an ordinary copy edit, switched R6 off silently.
        #
        # PER CHAIN, not per text. My first version judged each JS text
        # separately and fired on public/r-value-needed-calculator.html's JS[0]
        # -- an unrelated inline script that naturally contains none of the
        # chain's labels -- while JS[1] carried all of them. A page has several
        # scripts and the chain need only live in one.
        if texts and chain_seen["labels"] == 0:
            raw.append(Hit(
                "R6", "UNREGISTERED", cid, "SRC", cid,
                "chain %s: %d surface text(s) were READ (%d conditions, %d "
                "label assignments) and ZERO of its %d configured labels "
                "appear in ANY of them. Either the labels were renamed or the "
                "chain is misconfigured. A zero denominator is not a clean "
                "chain, it is an unwatched one."
                % (cid, len(texts), chain_seen["conds"],
                   chain_seen["assigns"], len(labels)),
                note="zero-denominator", sentence=cid))
        elif texts and chain_seen["assigns"] == 0:
            raw.append(Hit(
                "R6", "UNPARSEABLE", cid, "SRC", cid,
                "chain %s: %d configured label(s) appear in its surfaces but "
                "ZERO label-emitting assignments were parsed from any of them"
                % (cid, chain_seen["labels"]),
                note="no-assignments", sentence=cid))

    res.raw = raw
    res.adjudicated, res.rows = adjudicate(raw, [])
    res.levels, res.level_detail = level_counts(ctx, ["short of target"],
                                                ci=False, word=False)
    res.notes.append("DENOMINATOR  chains examined %d · JS texts read %d · "
                     "conditions located %d · label assignments found %d · "
                     "branches bound to a condition %d · configured labels "
                     "seen in text %d -- a RAW of 0 with a nonzero "
                     "denominator means CLEAN; a RAW of 0 with a zero "
                     "denominator means BLIND"
                     % (tot["chains"], tot["texts"], tot["conds"],
                        tot["assigns"], tot["branches"], tot["labels_seen"]))
    if tot["texts"] and not tot["assigns"]:
        res.traps.append("R6 read %d JS text(s) and found ZERO label "
                         "assignments matching the configured labels. Treat "
                         "this rule's PASS as unproven on this property."
                         % tot["texts"])
    return "label-emitting conditional chains examined", \
           "chains whose branch quantity is not the printed quantity"


R7_KEYS = (S.S_VIS, S.S_TITLE, S.S_META, S.S_OG, S.S_TW, S.S_LD, S.S_JS,
           S.S_LOWVIS, S.S_ATTR, S.S_LLMS, S.S_CITE, S.S_CONST)


def rule_R7(ctx, res):
    c = ctx.r("R7")
    ids = c.get("superseded_identifiers", []) or []
    urls = c.get("superseded_urls", []) or []
    props = c.get("superseded_propositions", []) or []
    marks = c.get("correction_markers", []) or []

    # ---- the registry half of the rule (spec 7.4, 12.1) -------------------
    # This rule used to print DEGRADED unconditionally, and it was right to:
    # the supersession record lived only in the gate's own config, so R7 was a
    # tool checking its own list rather than the property's record. The
    # registry now carries `superseded_by: {id, on, reason}` on a tombstone per
    # retired document plus a top-level `schema.supersession_declared` flag,
    # and R7 reads it. The DEGRADED line is conditional on the debt being
    # UNPAID -- it is not removed, and it comes back the moment a property's
    # registry stops declaring.
    reg = ctx.registry
    if not reg.present:
        res.degraded.append(
            "R7 DEGRADED: no %s in this repo; running from config list "
            "only (spec 7.4, 12.1)" % REGISTRY_REL)
    elif reg.parse_error:
        res.degraded.append(
            "R7 DEGRADED: %s could not be parsed (%s); running from config "
            "list only (spec 7.4, 12.1)" % (REGISTRY_REL, reg.parse_error))
    elif not reg.declared:
        res.degraded.append(
            "R7 DEGRADED: registry carries no machine-readable supersession "
            "marker; running from config list (spec 7.4, 12.1)")

    reg_ids, reg_urls = [], []
    reg_repl = {}
    if reg.declared and not reg.parse_error:
        for e in reg.superseded:
            # ONLY the entry's declared `identifiers` are scanned -- never its
            # `url`. A tombstone's url is often the publisher's CURRENT landing
            # page (an Xcel print code is retired while co.my.xcelenergy.com
            # stays live), and merging it turned three correct citations of the
            # current source into R7 failures the first time this ran. If a URL
            # is genuinely a banned string, its author says so by listing it in
            # `identifiers`, which is a deliberate act.
            for lit in e["identifiers"]:
                if "/" in lit or lit.lower().endswith(".pdf"):
                    reg_urls.append(lit)
                else:
                    reg_ids.append(lit)
                    if e["by"]:
                        reg_repl.setdefault(lit, e["by"])
    # The registry is ADDITIVE to the config, never a replacement for it: a
    # document the config knows about and the registry has not yet recorded
    # must not silently stop being enforced.
    cfg_ids, cfg_urls = set(ids), set(urls)
    ids = sorted(cfg_ids | set(reg_ids))
    urls = sorted(cfg_urls | set(reg_urls))
    # Sub-test A-reg exists so the REGISTRY half has a control of its own. A
    # hit on an identifier the config also knows is indistinguishable from the
    # old config-only behaviour and proves nothing about the registry; a hit on
    # an identifier ONLY the registry carries proves the registry is driving
    # the rule. Without that split, "the debt is paid" would rest on a message
    # no longer printing.
    def _sub(term):
        return "A" if term in cfg_ids or term in cfg_urls else "A-reg"
    repl_cfg = dict(c.get("current_replacements", {}) or {})
    for k, v in reg_repl.items():
        repl_cfg.setdefault(k, v)

    raw = []
    id_rx = _any_pat(ids, False, True) if ids else False
    # half A stays on the READ SET. The 2026-09-07 four-repo sweep measured
    # canon 3 / DCI 62 / LGM 64 / GCI 3 hits for the superseded print codes and
    # only NINE were live defects; the rest are history quoted in generators
    # and docs. Half B, the proposition half, is the one that reads SRC.
    for art in ctx.read_artifacts():
        for level, text in ((S.NORM_RAW, art.raw), (S.NORM_TXT, art.txt)):
            if not id_rx:
                break
            for m in id_rx.finditer(text):
                term = m.group(0)
                # A phrase that WRAPS a source line break is absent from RAW
                # and present in TXT. Count each identifier once per artifact
                # at the level that can actually see it.
                if level == S.NORM_RAW and term in art.txt:
                    continue
                p = m.start()
                repl = repl_cfg.get(term)
                raw.append(Hit(
                    "R7", _sub(term), art.rel, level,
                    "%s@%d" % (level.lower(), p),
                    "%s%s | %s"
                    % (term,
                       (" -> SUPERSEDED BY %s" % repl) if repl
                       else " -> no replacement recorded in "
                            "config.current_replacements",
                       S.collapse(win(text, p, 90))),
                    note="identifier",
                    sentence=S.collapse(win(text, p, 200))))
        for u in urls:
            for p in occ(art.raw, u, ci=False, word=False):
                raw.append(Hit("R7", _sub(u), art.rel, "ATTR", "url@%d" % p,
                               "%s | %s" % (u, S.collapse(win(art.raw, p, 60))),
                               note="superseded-url",
                               sentence=S.collapse(win(art.txt, 0, 1))))
    for art in ctx.rule_artifacts("R7"):
        for skey, loc, sent in ctx.pool(art):
            for pr in props:
                allof = pr.get("all_of") or []
                anyof = pr.get("any_of") or []
                noneof = pr.get("none_of") or []
                if allof and not all(has(sent, t, word=False) for t in allof):
                    continue
                if anyof and not has_any(sent, anyof, word=False):
                    continue
                if noneof and has_any(sent, noneof, word=False):
                    continue
                if not allof and not anyof:
                    continue
                raw.append(Hit("R7", "B", art.rel, skey, str(loc),
                               "%s | %s" % (pr.get("claim_id", "?"), sent),
                               note=pr.get("claim_id", "?"), sentence=sent))

    def f_srccode(h):
        return ctx.src_code_hit(h)

    def f_srcdup(h):
        return ctx.src_dup(h)

    def f_corr(h):
        return has_any(h.sentence, marks, word=False)

    def f_never403(h):
        return has_any(h.sentence, c.get("never_retire_on_403", []) or [],
                       word=False)

    res.raw = raw
    res.adjudicated, res.rows = adjudicate(raw, [
        Filt("the generator SRC surface is a STYLESHEET or a SCRIPT BODY, not "
             "prose -- its quoted string LITERALS are judged separately "
             "under a #strN locator", f_srccode),
        Filt("generator SRC restatement of prose that already renders in public/ (counted once, against the rendered artifact)", f_srcdup),
        Filt("correction marker in scope (quoted in order to retire it)", f_corr),
        Filt("never_retire_on_403 source named (403 is bot-blocking)", f_never403),
    ])
    res.levels, res.level_detail = level_counts(ctx, ids, ci=False)
    if not reg.present:
        res.notes.append("REGISTRY: %s absent -- identifier half runs from "
                         "config only" % REGISTRY_REL)
    elif reg.parse_error:
        res.notes.append("REGISTRY: %s unparseable (%s) -- identifier half "
                         "runs from config only"
                         % (REGISTRY_REL, reg.parse_error))
    else:
        res.notes.append(
            "REGISTRY: %s declares supersession machine-readably: %s  ·  %d "
            "entr%s reviewed, %d carry superseded_by, %d assert CURRENT by "
            "absence  ·  %d identifier(s) and %d url(s) merged into half A "
            "FROM THE REGISTRY, additive to the config list"
            % (REGISTRY_REL,
               ("declared %s" % reg.declared_on) if reg.declared
               else "NOT DECLARED",
               reg.entries, "y" if reg.entries == 1 else "ies",
               len(reg.superseded), len(reg.undeclared_ids),
               len(reg_ids), len(reg_urls)))
        for e in reg.superseded:
            res.notes.append(
                "  registry supersession: %s -> %s on %s  (identifiers: %s)"
                % (e["id"], e["by"] or "<none recorded>",
                   e["on"] or "<no date recorded>",
                   ", ".join(e["identifiers"]) or "<none>"))
    res.notes.append("half A IDENTIFIER (STRING LIST) %d from the config, %d "
                     "from the REGISTRY ONLY  ·  half B PROPOSITION (CLAIM "
                     "TEST) %d -- a citation sweep must search for the CLAIM, "
                     "not only for the identifier"
                     % (len([h for h in res.adjudicated if h.sub == "A"]),
                        len([h for h in res.adjudicated if h.sub == "A-reg"]),
                        len([h for h in res.adjudicated if h.sub == "B"])))

    # ---- what this rule is NOT testing, and why (spec 8 R7) ---------------
    # A PROPOSITION THAT WAS TAKEN OUT MUST STAY VISIBLE. `whe_audit_entry_
    # path_hes_plus` bound supersession to a phrase the publisher still uses,
    # and on 2026-09-20 that produced 107 adjudicated findings on DCI, all of
    # them true copy. Deleting the entry would have fixed the count and left
    # no evidence in any gate output that a blocking rule had lost a member.
    # Every retirement is therefore PRINTED, every run, forever.
    retired = c.get("retired_propositions", []) or []
    res.notes.append(
        "RETIRED PROPOSITIONS: %d claim_id(s) were removed from the enforced "
        "set and are recorded, not deleted -- each is printed below every run "
        "so a rule that lost a member can never look like a rule that never "
        "had one. A retirement NEVER narrows half A." % len(retired))
    for r in retired:
        res.notes.append(
            "  RETIRED %s on %s: %s"
            % (r.get("claim_id", "?"), r.get("retired_on", "<no date>"),
               r.get("retired_because", "<NO REASON RECORDED -- a retirement "
                                        "without a reason is a deletion>")))
        if r.get("detection_not_lost"):
            res.notes.append("    detection not lost: %s"
                             % r["detection_not_lost"])
        if r.get("reopen_if"):
            res.notes.append("    reopen if: %s" % r["reopen_if"])

    # ---- the CAUSE of the hes_plus defect, wired as a standing report -----
    # The refuted entry was justified by testing its phrase against ONE
    # current Xcel document, finding zero, and reading that single absence as
    # absence from the publisher. Every proposition that asserts "the current
    # source dropped this" is making the same shape of claim, so every one of
    # them owes the SET of current first-party surfaces the absence was
    # measured against. Report-only and never blocking: this is an evidence
    # audit of the config, not a finding about the property.
    untested = [p.get("claim_id", "?") for p in props
                if not (p.get("tested_against") or [])]
    res.notes.append(
        "SUPERSESSION EVIDENCE OWED: %d of %d enforced proposition(s) carry "
        "no `tested_against` -- the list of CURRENT first-party surfaces the "
        "absence was measured against, each with its User-Agent, HTTP status "
        "and retrieval date. Absence from ONE of a publisher's documents is "
        "not supersession: that exact inference is what retired "
        "whe_audit_entry_path_hes_plus on 2026-09-20, after it billed 107 "
        "true sentences on DCI as superseded-source claims. REPORT-ONLY, "
        "never blocking.%s"
        % (len(untested), len(props),
           ("  OWED: " + ", ".join(untested)) if untested else ""))
    return "superseded identifiers and propositions found", \
           "live claims sourced to a superseded document"


_MONTHS = ("January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December")


def _parse_long_date(s):
    m = re.search(r"(%s)\s+(\d{1,2}),\s*(\d{4})" % "|".join(_MONTHS), s)
    if not m:
        return None
    return "%s-%02d-%02d" % (m.group(3), _MONTHS.index(m.group(1)) + 1,
                             int(m.group(2)))


def _days_between(a, b):
    """Whole days from ISO date `a` to ISO date `b`. 0 if either is unparseable
    -- an unparseable date must never silently buy a grace."""
    import datetime as _dt
    try:
        da = _dt.date(*[int(x) for x in a.split("-")])
        db = _dt.date(*[int(x) for x in b.split("-")])
    except Exception:
        return 0
    return (db - da).days


def rule_R8(ctx, res):
    c = ctx.r("R8")
    # Resolved DEFENSIVELY even though main() has already normalised the
    # config. Part (b) is a STRING comparison and "2026-09-20" > "auto" is
    # False, so a sentinel arriving here through an overlay that main() never
    # saw would not fail -- it would quietly switch the future-date test off.
    today = resolve_asof(c.get("today", ctx.today))
    exempt = set(c.get("exempt_pages", []) or [])
    own = set(c.get("own_effective_date_pages", []) or [])
    pinned = c.get("pinned_pages", {}) or {}
    holds = c.get("known_holds", []) or []
    pub_grace = int(c.get("published_before_git_grace_days", 7))
    hold_note = holds[0].get("report_as") if holds else ""

    # THE AS-OF, STATED ON THE RULE IT GOVERNS. Part (b) is the only place in
    # R8 -- or anywhere in this gate -- that reads it, and on 2026-09-20 a
    # pinned yesterday turned 246 truthful dates into "future" findings with
    # nothing in the output naming the cause. Both branches print.
    _stale = asof_staleness(today, "the as-of in force for this run")
    if _stale:
        res.notes.append("AS-OF: %s" % _stale)
    else:
        res.notes.append(
            "AS-OF %s, and it is NOT behind the system clock. Part (b) -- "
            "'this published date is in the future' -- is the ONLY reader of "
            "the as-of in this rule or any other; parts (a) and (d) compare "
            "against git and part (c) compares surfaces against each other. "
            "Because part (b) is a strict `>`, an as-of that moves FORWARD "
            "can only ever remove hits, and every hit it removes is a date "
            "that is not in the future. An invented future date is caught at "
            "any as-of." % today)
    res.notes.append(
        "ld:datePublished IS CHECKED for impossibility (after today, and "
        "preceding the artifact's first appearance in git by more than %d "
        "day(s)) and is deliberately EXCLUDED from the surfaces-disagree "
        "test, because a publication date legitimately differs from a review "
        "date. It was previously excluded from every test, which hid 10 "
        "impossible dates." % pub_grace)
    sitemap_lastmod = {}
    for art in ctx.artifacts:
        for loc, mod in art.sitemap_entries:
            base = loc.rstrip("/").rsplit("/", 1)[-1] or "index.html"
            sitemap_lastmod[base] = mod

    raw = []
    for art in ctx.html_artifacts():
        base = art.rel.rsplit("/", 1)[-1]
        excluded_as = ""
        if base in exempt:
            excluded_as = "exempt_pages"
        elif base in own:
            excluded_as = "own_effective_date_pages"
        dates = {}
        for dt, vis in art.time_elements:
            # DECODE first, then take the ISO DATE PREFIX. The old
            # re.fullmatch(r"\d{4}-\d{2}-\d{2}", dt) rejected both
            # `2026&#45;08&#45;24` and a valid full timestamp
            # `2027-01-01T00:00:00Z`, and a page whose only date was in one of
            # those forms contributed no dates and was skipped whole.
            dtd = S.dec(dt or "").strip()
            m = re.match(r"(\d{4}-\d{2}-\d{2})", dtd)
            if m:
                dates.setdefault("time[datetime]", m.group(1))
                v = _parse_long_date(S.dec(vis or ""))
                if v:
                    dates.setdefault("footer_text", v)
        for path, val in art.ld_leaves:
            if path.endswith(".dateModified") and \
                    re.match(r"\d{4}-\d{2}-\d{2}", str(val)):
                dates.setdefault("ld:dateModified", str(val)[:10])
            if path.endswith(".datePublished") and \
                    re.match(r"\d{4}-\d{2}-\d{2}", str(val)):
                dates.setdefault("ld:datePublished", str(val)[:10])
        # config.R8.footer_marker was dead, so a plain-text
        # "Last reviewed: January 1, 2027" with no <time> element contributed
        # no date at all and the page was skipped.
        fm = c.get("footer_marker") or ""
        if fm:
            for mpos in occ(art.txt, fm, ci=True, word=False):
                tail = art.txt[mpos:mpos + 80]
                v = _parse_long_date(tail)
                if v:
                    dates.setdefault("footer_text", v)
                    break
        lm = sitemap_lastmod.get(base)
        if lm:
            dates["sitemap:lastmod"] = lm
        if not dates:
            continue
        pub = dates.get("ld:datePublished")
        # `claimed` excludes ld:datePublished from the SURFACES-DISAGREE test,
        # and rightly: a publication date legitimately differs from a review
        # date, so comparing them would fire on every correctly-dated page.
        claimed = [(k, v) for k, v in sorted(dates.items())
                   if k != "ld:datePublished"]
        # BUT IT IS STILL A PUBLISHED DATE, AND AN IMPOSSIBLE ONE IS STILL
        # IMPOSSIBLE. Excluding it from EVERY test hid 10 impossible dates --
        # 9 on DCI dated 35-36 days before that repository's first commit --
        # and is what left dci.json's long-standing "unidentified" R8 anomaly
        # unidentified. Silent exclusion is exactly how the original R8 defect
        # survived, so it is now checked for the two IMPOSSIBILITY tests
        # (after today, and preceding the artifact's first appearance in git)
        # while staying out of the consistency test.
        impossible = list(claimed)
        if pub:
            impossible.append(("ld:datePublished", pub))
        # (b) after today
        for k, v in impossible:
            if v > today:
                h = Hit("R8", "b", art.rel, k, k,
                        "%s = %s is after today (%s)" % (k, v, today),
                        note="future-date", sentence=base)
                h.r8_excluded = excluded_as
                raw.append(h)
        # (c) surfaces disagree
        vals = sorted(set(v for _, v in claimed))
        if len(vals) > 1:
            h = Hit("R8", "c", art.rel, "VIS", base,
                    "date surfaces disagree: %s"
                    % "; ".join("%s=%s" % (k, v) for k, v in claimed),
                    note="surfaces-disagree", sentence=base)
            h.r8_excluded = excluded_as
            raw.append(h)
        if pub:
            for k, v in claimed:
                if pub > v:
                    h = Hit("R8", "c", art.rel, k, k,
                            "datePublished %s is after %s %s" % (pub, k, v),
                            note="ordering", sentence=base)
                    h.r8_excluded = excluded_as
                    raw.append(h)
        # A PINNED PAGE THAT HAS DRIFTED OFF ITS STATED PIN IS A FINDING ON
        # ITS OWN. This block used to sit inside `if last:` -> `if newest <
        # last:`, so it was reachable only when the page was ALSO
        # stale-vs-content, and it never fired: at pin, footer drifted,
        # sitemap drifted and BOTH drifted all returned sub c or nothing, and
        # `grep -c pin-drifted` returned 0 on all three properties. A pin
        # states a value; if the page no longer carries it, the pin is not
        # describing reality and the exemption must not apply -- which is the
        # whole reason expected_footer and expected_sitemap were wired.
        if base in pinned:
            pin = pinned.get(base) or {}
            ef = pin.get("expected_footer")
            es = pin.get("expected_sitemap")
            got_f = dates.get("footer_text") or dates.get("time[datetime]")
            got_s = dates.get("sitemap:lastmod")
            drift = []
            if ef and got_f and got_f != ef:
                drift.append("footer %s != pinned %s" % (got_f, ef))
            if es and got_s and got_s != es:
                drift.append("sitemap %s != pinned %s" % (got_s, es))
            if drift:
                h = Hit("R8", "p", art.rel, "VIS", base,
                        "pinned page has DRIFTED off its stated pin: %s -- the "
                        "exemption describes a value the page no longer "
                        "carries" % "; ".join(drift),
                        note="pin-drifted", sentence=base)
                h.r8_excluded = excluded_as
                raw.append(h)

        first = ctx.gitfacts.first_seen.get(art.rel)
        if first:
            for k, v in impossible:
                # A PUBLICATION date legitimately precedes the commit that
                # first ships the file -- you write it, then you commit it.
                # A REVIEW or MODIFIED date does not: it claims a review
                # happened before the artifact existed. So ld:datePublished
                # gets a stated grace and nothing else does. Measured: DCI's
                # nine gaps are 35 and 36 days (2026-05-05/06 against a first
                # commit of 2026-06-10) and stay caught; GCI's single gap is
                # ONE day (2026-08-31 against 2026-09-01), which is an
                # ordinary authoring gap and is not a defect.
                if k == "ld:datePublished" and _days_between(v, first) \
                        <= pub_grace:
                    continue
                if v < first:
                    h = Hit("R8", "a", art.rel, k, k,
                            "%s = %s precedes first appearance in git (%s)"
                            % (k, v, first),
                            note="precedes-creation", sentence=base)
                    h.r8_excluded = excluded_as
                    raw.append(h)
        last = ctx.gitfacts.last_content_change(art.rel) \
            if ctx.gitfacts.available else None
        if last:
            newest = max(v for _, v in claimed)
            if newest < last:
                note = "stale-vs-content"
                if base in pinned:
                    note = "pinned"
                elif hold_note:
                    note = hold_note
                h = Hit("R8", "d", art.rel, "VIS", base,
                        "published review date %s precedes the last "
                        "visible-text change %s" % (newest, last),
                        note=note, sentence=base)
                h.r8_excluded = excluded_as
                raw.append(h)

    def f_pinned(h):
        # A DRIFTED pin does not grant the exemption.
        return h.note == "pinned"

    def f_exempt(h):
        # Was `return False` -- dead code wired to a filter row that could only
        # ever print "0 (removed 0)". A filter that cannot fire does not reduce
        # confidence, it manufactures it. An excluded page's dates are now
        # RAISED and removed HERE, with a real count and a real enumeration,
        # so an impossible 2027 date on 404.html is visible as a cleared item
        # instead of vanishing before any counter moved.
        return bool(getattr(h, "r8_excluded", ""))

    res.raw = raw
    res.adjudicated, res.rows = adjudicate(raw, [
        Filt("own_effective_date_pages / exempt_pages (raised, then cleared "
             "here -- never dropped before the count)", f_exempt),
        Filt("pinned_pages (visible text unchanged; JSON-LD only)", f_pinned),
    ])
    res.levels, res.level_detail = level_counts(
        ctx, ["Last reviewed", "<lastmod>"], ci=False, word=False)
    firsts = sorted(v for v in ctx.gitfacts.first_seen.values() if v)
    if firsts:
        res.notes.append("part (a) measures first appearance in THIS repo's "
                         "git history; the earliest public/ commit here is %s, "
                         "so on a ported property part (a) is a FLOOR and a "
                         "hit can mean the port post-dates the content's real "
                         "authoring date rather than that the date is invented"
                         % firsts[0])
    if holds:
        res.notes.append("KNOWN-OPEN hold in force: %s -- %s"
                         % (holds[0].get("id"), holds[0].get("note", "")))
    if ctx.gitfacts.capped:
        res.notes.append("part (d) history cap reached on %d file(s); the "
                         "oldest examined commit was used"
                         % len(ctx.gitfacts.capped))
    if not ctx.gitfacts.available:
        res.degraded.append("R8 DEGRADED: no git history available; parts (a) "
                            "and (d) not evaluated")
    return "published date surfaces compared", \
           "dates impossible, contradicted, or preceding their content"


def _r9_instances(ctx, subjects):
    """(slot, rel, surface, locator, sentence) for every contested-subject
    instance in `ctx`. Factored out so a --peer context can be indexed with the
    same predicates."""
    instances = {}
    for sub in subjects:
        sid = sub.get("id")
        pats = [re.compile(p, re.IGNORECASE) for p in (sub.get("extract") or [])]
        slots = sub.get("value_slots") or {}
        ctxwords = sub.get("context") or []
        noneof = sub.get("none_of") or []
        prox = int(sub.get("proximity_chars", 120))
        if not pats or not slots:
            continue
        for art in ctx.rule_artifacts("R9"):
            for skey, loc, sent in ctx.pool(art):
                spans = []
                for p in pats:
                    for m in p.finditer(sent):
                        spans.append(m.start())
                if not spans:
                    continue
                if ctxwords and not has_any(sent, ctxwords, word=False):
                    continue
                if noneof and has_any(sent, noneof, word=False):
                    continue
                for pos in spans:
                    w = win(sent, pos, prox)
                    for slot in sorted(slots):
                        if has_any(w, slots[slot], word=False):
                            instances.setdefault(sid, []).append(
                                (slot, art.rel, skey, str(loc), sent))
    return instances


def rule_R9(ctx, res):
    c = ctx.r("R9")
    subjects = c.get("claim_subjects", []) or []
    hi = set(c.get("high_severity_surfaces", []) or [])
    tools = c.get("tools", []) or []
    marks = ctx.r("R7").get("correction_markers", []) or []

    instances = _r9_instances(ctx, subjects)

    raw = []
    for sub in subjects:
        sid = sub.get("id")
        inst = sorted(set(instances.get(sid, [])))
        if not inst:
            continue
        slots_seen = sorted(set(i[0] for i in inst))
        if len(slots_seen) < 2:
            continue
        auth = sub.get("authoritative_value")
        note = "authoritative=%s" % auth if auth else \
            "NO AUTHORITATIVE VALUE IN CONFIG"
        files = sorted(set(i[1] for i in inst))
        for slot, rel, skey, loc, sent in inst:
            if auth and slot == auth:
                continue
            n1 = len(files) > 1
            per_file = sorted(set(i[0] for i in inst if i[1] == rel))
            n2 = len(per_file) > 1
            sev = "HIGH" if skey in hi else "std"
            tags = [t for t, on in (("N1", n1), ("N2", n2)) if on]
            if not tags:
                continue
            raw.append(Hit("R9", tags[0], rel, skey, loc,
                           "%s: %d values %s | %s | sub-tests %s | %s | "
                           "severity=%s" % (sid, len(slots_seen), slots_seen,
                                            slot, "+".join(tags), sent, sev),
                           note=note, sentence=sent))
    for t in tools:
        art = ctx.by_rel.get(t.get("page", ""))
        if not art:
            continue
        vis_ids = [t.get("visible", "").lstrip("#")]
        hidden = t.get("hidden", []) or []
        # `art.ids` HOLDS STATIC MARKUP IDS ONLY. A hidden field built by
        # document.createElement never appears there, and this gate does not
        # execute JS outside opt-in R6b -- it says so in its own KNOWN HOLES
        # header. So a presence check keyed on static ids cannot tell "the
        # field does not exist" from "the field is created at runtime", and
        # this one resolved that ambiguity as a BLOCKING failure.
        #
        # Measured on DCI ba2fc22. Every one of the six calculator pages
        # carries id="calcTool" exactly once, and the shared lead-form script
        # reads:
        #     if (document.getElementById('calcTool')) {
        #       ['calc_inputs','calc_output'].forEach(function (n) {
        #         var h = document.createElement('input'); h.type='hidden';
        #         h.name=n; h.id='lf-'+n.replace('_','-');
        #         form.appendChild(h); }); }
        # The fields DO exist in the DOM and NEVER in static markup. N3
        # therefore reported N3-unverifiable on every run, that unverifiable
        # was adjudicated, and it blocked: DCI could not reach exit 0 by any
        # change to any page, because no copy edit can put a runtime-created
        # id into static markup. A rule blocking a production build on its own
        # declared blind spot is a false positive with no reachable remedy.
        #
        # It was worse than noise. N3b below skips any mirror in `missing`, so
        # the same stale set ALSO disabled the one sub-test that does the real
        # comparison -- the rule R9 was named for was silently off on the only
        # property that has ever carried the defect.
        #
        # SPLIT THE VERDICT ON THE EVIDENCE:
        #   absent   -- the id is in no static markup AND is named by no JS
        #               string literal on the page. Nothing references it; the
        #               config and the page genuinely disagree. Still a
        #               finding, still blocks.
        #   runtime  -- the id is absent from static markup but the page's own
        #               JS names it as a literal. The gate has evidence the
        #               page references the field and NO evidence either way
        #               about whether it exists when the visitor sees it. That
        #               is the definition of unverifiable, and an unverifiable
        #               is raised, enumerated and filtered -- never blocked on.
        js_lits = "  ".join(
            [S.collapse(lit) for _, lit in (getattr(art, "js_strings", []) or [])]
            + list(getattr(art, "js_bodies", []) or []))
        absent, runtime = [], []
        for h in hidden:
            if h in art.ids:
                continue
            (runtime if h in js_lits else absent).append(h)
        missing = absent + runtime
        if missing and vis_ids and vis_ids[0] in art.ids:
            raw.append(Hit("R9", "N3", art.rel, "JS", art.rel,
                           "tool payload field(s) %s not found in the page; "
                           "visible/hidden agreement cannot be established"
                           % missing,
                           note=("N3-unverifiable" if absent
                                 else "N3-runtime-constructed"),
                           sentence=art.rel))
        # N3b compares what it CAN resolve. A runtime-constructed mirror is
        # still a JS identifier the static literal scan can read, so it is no
        # longer excluded -- only a genuinely absent one is.
        missing = absent
        # N3b -- THE COMPARISON THE RULE WAS NAMED FOR.
        # N3 above is a PRESENCE check: it fires when a configured id is
        # ABSENT and is silent when every id is present. Either way the
        # contradiction is unreachable by construction, which is why DCI's
        # hidden calc_output transmitting "No project recommended -- already at
        # code." for an R-49 homeowner, while the visible output said R-60,
        # scored MISSED twice (GATE_SCORE_2026-09-17.md miss 10 / this lane's
        # miss 7). A lead form is a claim surface: what it transmits about the
        # homeowner is an assertion about that homeowner.
        js = "\n".join(getattr(art, "js_bodies", []) or [])
        # Only fields the config DECLARES as mirrors of the visible verdict are
        # compared. A lead form's payload also carries the visitor's INPUTS,
        # and "attic" is not a verdict the output element should ever have
        # displayed -- comparing every hidden field produced exactly that false
        # positive on the first run. Which field is the mirror is a property
        # fact, so it lives in config, and a tool that declares none says so
        # below rather than passing silently.
        mirrors = [m for m in (t.get("hidden_mirrors_visible") or [])
                   if m in hidden]
        if not mirrors:
            res.notes.append(
                "N3b NOT RUN for %s: R9.tools entry declares no "
                "`hidden_mirrors_visible`, so there is no field the gate has "
                "been told should agree with '#%s'. This is a null result, "
                "NOT a pass -- DCI's hidden calc_output contradicted its "
                "visible output for weeks inside exactly this gap."
                % (t.get("page", "?"), vis_ids[0] if vis_ids else "?"))
            continue
        if not js or not vis_ids or not vis_ids[0]:
            continue
        vis = _assigned_literals(js, vis_ids[0])
        if not vis:
            res.notes.append(
                "N3b NOT RUN for %s: no string literal could be resolved to "
                "the visible output '#%s', so there is nothing to compare "
                "against. Null result, not a pass."
                % (t.get("page", "?"), vis_ids[0]))
            continue
        for h in mirrors:
            if h in missing:
                continue
            hid = _assigned_literals(js, h)
            unreachable = sorted(hid - vis)
            for lit in unreachable:
                raw.append(Hit(
                    "R9", "N3b", art.rel, "JS", "%s<-%s" % (h, vis_ids[0]),
                    "hidden payload field '%s' can transmit a verdict the "
                    "visible output '#%s' can never show: %r  |  the visible "
                    "output's own verdict set is %s"
                    % (h, vis_ids[0], lit,
                       sorted(vis)[:6] if vis else "(none resolved)"),
                    note="N3b-hidden-contradicts-visible", sentence=lit))

    def f_corr(h):
        return has_any(h.sentence, marks, word=False)

    def f_delib(h):
        for d in (c.get("deliberate_divergence") or []):
            if d.get("subject") and d["subject"].split()[0].lower() in h.text.lower():
                return True
        return False

    res.raw = raw
    res.adjudicated, res.rows = adjudicate(raw, [
        Filt("correction marker in scope (a retired value quoted to retire it)",
             f_corr),
        Filt("deliberate_divergence recorded in config", f_delib),
        Filt("N3 payload field is absent from STATIC markup but named by the "
             "page's own JS, i.e. constructed at runtime -- the gate does not "
             "execute JS outside opt-in R6b (its own KNOWN HOLES header), so "
             "it has no evidence either way and REPORTS rather than blocks. A "
             "field named by NO markup and NO script is still `absent` and "
             "still blocks; only this one evidentiary state is filtered, and "
             "it is enumerated below like every other.",
             lambda h: h.note == "N3-runtime-constructed"),
    ])
    res.levels, res.level_detail = level_counts(
        ctx, ["CFM 50", "CFM50", "front door"], ci=False, word=False)
    peer = getattr(ctx, "peer_ctx", None)
    if peer is not None:
        delib = set()
        for d in (c.get("deliberate_divergence") or []):
            delib.add(str(d.get("subject", "")).split()[0].lower())
        pinst = _r9_instances(peer, subjects)
        compared = diverged = 0
        for sub in subjects:
            sid = sub.get("id")
            mine = sorted(set(i[0] for i in instances.get(sid, [])))
            theirs = sorted(set(i[0] for i in pinst.get(sid, [])))
            if not mine or not theirs:
                continue
            compared += 1
            if sid.split("_")[0].lower() in delib or sid.lower() in delib:
                continue
            if set(mine) != set(theirs):
                diverged += 1
                for slot, rel, skey, loc, sent in sorted(
                        set(instances.get(sid, []))):
                    if slot in theirs:
                        continue
                    raw.append(Hit(
                        "R9", "N4", rel, skey, loc,
                        "%s: this property says %s, peer %s says %s | %s"
                        % (sid, mine, peer.key, theirs, sent),
                        note="cross-property-divergence", sentence=sent))
        res.notes.append("R9 CROSS-PROPERTY HALF RAN against %s (%s): %d "
                         "subject(s) had instances on BOTH properties, %d "
                         "diverged, %d subject(s) skipped as "
                         "deliberate_divergence"
                         % (peer.key, peer.repo, compared, diverged,
                            len(delib)))
    elif not ctx.control:
        res.notes.append("R9 CROSS-PROPERTY HALF SKIPPED: no --peer given")
    hidden = {}
    for art in ctx.html_artifacts():
        for sel in sorted(set(art.hidden_selectors)):
            hidden.setdefault(sel, []).append(art.rel)
    if hidden:
        res.traps.append(
            "%d selector(s) set display:none / visibility:hidden across %d "
            "artifact(s): %s. The gate reads CSS, flags this, and is NOT a "
            "layout engine -- it computes no cascade (spec 7.8). GCI bf240f8 "
            "found the live case: a correction inside .thank-you that the "
            "served CSS hides until the visitor hands over a name and phone "
            "number."
            % (len(hidden), len(set(sum(hidden.values(), []))),
               "; ".join("%s (%d pages)" % (k, len(hidden[k]))
                         for k in sorted(hidden))))
    return "contested-subject claim instances indexed", \
           "instances contradicting the subject's other value"


def rule_R10(ctx, res):
    c = ctx.r("R10")
    pats = [re.compile(p, re.IGNORECASE) for p in (c.get("promise_patterns") or [])]
    refusals = c.get("refusal_markers", []) or []
    reflex = c.get("reflexive_markers", []) or []
    titles = c.get("page_titles", {}) or {}
    dollar = re.compile(ctx.r("R3").get("dollar_pattern", r"\$[0-9][0-9,.]*"))
    allowed = ctx.r("R3").get("allowed_figures", []) or []
    marks = ctx.r("R7").get("correction_markers", []) or []
    domain = (ctx.cfg.get("domain") or "").rstrip("/")

    def figures_in(art):
        n = 0
        for m in dollar.finditer(art.raw):
            if m.group(0) not in allowed:
                n += 1
        return n

    total_fig = sum(figures_in(a) for a in ctx.read_artifacts())

    anchors = {}
    for art in ctx.claim_artifacts():
        anchors[art.rel] = [
            (m.group(1), S.collapse(S.txt(m.group(2))))
            for m in re.finditer(r"<a\b[^>]*href=\"([^\"]*)\"[^>]*>(.*?)</a\s*>",
                                 art.raw, re.DOTALL | re.IGNORECASE)]

    raw = []
    for art in ctx.claim_artifacts():
        for skey, loc, sent in ctx.pool(art):
            if not any(p.search(sent) for p in pats):
                continue
            dest = None
            kind = "unresolvable"
            for href, label in anchors.get(art.rel, []):
                if label and len(label) > 3 and label in sent:
                    dest, kind = href, "anchor"
                    break
            if dest is None:
                for phrase in sorted(titles):
                    if has(sent, phrase, word=False):
                        dest, kind = titles[phrase], "page_title"
                        break
            if dest is None and has_any(sent, reflex, word=False):
                dest, kind = "<whole property>", "reflexive"
            note = kind
            ok = False
            if kind == "anchor":
                if re.match(r"https?://", dest) and not dest.startswith(domain):
                    # config.R10.offproperty_is_compliant was dead. It is now
                    # READ: a property that wants an off-property promise
                    # checked rather than assumed compliant can say so, and the
                    # gate will report it as unresolvable instead (it still
                    # makes no outbound request, spec 7.3).
                    note = "off-property"
                    ok = bool(c.get("offproperty_is_compliant", True))
                    if not ok:
                        note = "off-property, and offproperty_is_compliant " \
                               "is false: NOT fetched (spec 7.3), REVIEW"
                else:
                    base = dest.split("?")[0].split("#")[0].rstrip("/")
                    base = base.rsplit("/", 1)[-1] or "index.html"
                    tgt = ctx.by_rel.get("public/" + base) or \
                        ctx.by_rel.get(base)
                    if tgt is None:
                        note = "destination-not-in-read-set"
                    elif has_any(tgt.txt, refusals, word=False):
                        note = "destination-refuses"
                    elif figures_in(tgt) > 0:
                        note = "destination-renders-a-figure"
                        ok = True
                    else:
                        note = "destination-has-no-figure"
            elif kind == "page_title":
                tgt = ctx.by_rel.get(dest) or \
                    ctx.by_rel.get(dest.rsplit("/", 1)[-1])
                if tgt is None:
                    note = "destination-not-in-read-set"
                elif has_any(tgt.txt, refusals, word=False):
                    note = "destination-refuses"
                elif figures_in(tgt) > 0:
                    note = "destination-renders-a-figure"
                    ok = True
                else:
                    note = "destination-has-no-figure"
            elif kind == "reflexive":
                if total_fig > 0:
                    note = "property-renders-%d-figures" % total_fig
                    ok = True
                else:
                    note = "property-renders-zero-figures"
            raw.append(Hit("R10", kind, art.rel, skey, str(loc),
                           "dest=%s | %s | %s" % (dest, note, sent),
                           note=note if not ok else "SATISFIED:" + note,
                           sentence=sent))

    def f_refusal_here(h):
        return has_any(h.sentence, refusals, word=False)

    def f_sat(h):
        return h.note.startswith("SATISFIED:")

    def f_unres(h):
        return h.note == "unresolvable"

    def f_notinset(h):
        # A promise pointing at a page that DOES NOT EXIST used to be cleared.
        # A destination outside the read set cannot satisfy a promise of a
        # figure, so it is a FAIL, not a pass. Only an OFF-PROPERTY
        # destination is compliant by construction (spec 7.3), and that is
        # already handled by the SATISFIED path.
        return False

    def f_corr(h):
        return has_any(h.sentence, marks, word=False)

    res.raw = raw
    res.adjudicated, res.rows = adjudicate(raw, [
        Filt("refusal marker in the promise sentence (sanctioned wayfinding)",
             f_refusal_here),
        Filt("destination satisfies the promise / is off-property", f_sat),
        Filt("destination unresolvable -> REVIEW, not FAIL", f_unres),
        Filt("destination outside the read set -- NO LONGER CLEARED: a page "
             "that does not exist cannot satisfy a promise of a figure",
             f_notinset),
        Filt("correction marker in scope", f_corr),
    ])
    res.levels, res.level_detail = level_counts(
        ctx, ["quoted elsewhere", "covers the base amounts",
              "estimates the project cost"], ci=False, word=False)
    res.notes.append("deliberate bias: a destination that refuses in words "
                     "the config does not know looks like a destination with "
                     "no figures, which is still a FAIL -- the failure mode is "
                     "a false positive, not a false negative (spec R10)")
    return "figure-promises resolved to destinations", \
           "promises no destination satisfies"


def rule_R11(ctx, res):
    c = ctx.r("R11")
    terms = c.get("tracked_terms", []) or []
    sel_open = '<p class="cited-stat">'
    if not terms:
        res.notes.append("R11: 0 tracked terms configured for %s -- reported "
                         "as a null result, NOT as PASS" % ctx.key)
        res.raw = []
        res.adjudicated, res.rows = adjudicate([], [])
        res.levels, res.level_detail = level_counts(ctx, ["cited-stat"],
                                                    ci=False, word=False)
        return "tracked terms configured", "tracked-term rows reported"

    rows = []
    raw = []
    for t in terms:
        pats = t.get("patterns", []) or []
        tid = t.get("id", "?")
        asserting, attributed, unattributed = set(), set(), set()
        for art in ctx.claim_artifacts():
            blob = art.txt + " || " + " || ".join(
                s.text for s in ctx.surfaces(art, (S.S_LD, S.S_LOWVIS,
                                                   S.S_META, S.S_OG, S.S_TW,
                                                   S.S_LLMS)))
            if has_any(blob, pats, word=False):
                asserting.add(art.rel)
            inblock = " || ".join(x["txt"] for x in art.cited_stats)
            if inblock and has_any(inblock, pats, word=False):
                attributed.add(art.rel)
            outside = art.raw
            for x in art.cited_stats:
                outside = outside.replace(sel_open + x["body"] + "</p>", " ")
            outside_txt = S.txt(outside) + " || " + " || ".join(
                s.text for s in ctx.surfaces(art, (S.S_LD, S.S_LOWVIS,
                                                   S.S_META, S.S_OG, S.S_TW,
                                                   S.S_LLMS)))
            if has_any(outside_txt, pats, word=False):
                unattributed.add(art.rel)
        both = sorted(attributed & unattributed)
        # forbid_subtraction: each cell is its own query. Prove it.
        naive = len(asserting) - len(attributed)
        exp = t.get("expected", {}) or {}
        rows.append((tid, t.get("label", tid), len(asserting),
                     len(attributed), len(unattributed), len(both), naive, exp))
        if not asserting:
            # No page asserts this term. Emitting a row anyway is what let the
            # R11 control report DETECTED against a fixture reading
            # "<p>Nothing.</p>".
            continue
        raw.append(Hit("R11", "row", tid, "VIS", tid,
                       "%s asserting %d / attributed %d / unattributed %d / "
                       "both %d  (naive subtraction would say unattributed=%d)"
                       % (t.get("label", tid), len(asserting), len(attributed),
                          len(unattributed), len(both), naive),
                       note="report-only", sentence=tid))
        # The control for this rule is not "does it fire" but "does it count
        # correctly, WITHOUT subtracting". forbid_subtraction is now a real
        # assertion with a distinct sub-test, not a `pass`.
        if len(both) and naive != len(unattributed):
            raw.append(Hit(
                "R11", "nonsubtractive", tid, "VIS", "%s:nosub" % tid,
                "%s: %d page(s) BOTH attribute and assert outside the block, "
                "so naive subtraction gives unattributed=%d where the measured "
                "value is %d. Each cell is its own query."
                % (t.get("label", tid), len(both), naive, len(unattributed)),
                note="forbid_subtraction-proved", sentence=tid))
        if c.get("forbid_subtraction") and len(both) and \
                naive == len(unattributed):
            res.traps.append(
                "%s: %d page(s) do both, yet naive subtraction coincides with "
                "the measured unattributed count. Verify the cells were each "
                "queried independently." % (t.get("label", tid), len(both)))
    res.raw = raw
    res.adjudicated, res.rows = adjudicate(raw, [])
    res.levels, res.level_detail = level_counts(ctx, ["cited-stat"], ci=False,
                                                word=False)
    for tid, label, a, at, un, bo, naive, exp in rows:
        q = ("asserting: pattern anywhere in the page's claim set; "
             "attributed: pattern inside a p.cited-stat block; "
             "unattributed: pattern OUTSIDE every p.cited-stat block "
             "(its OWN query, never asserting minus attributed); "
             "both: |attributed AND unattributed|")
        d = ""
        if exp:
            d = "  baseline %d/%d/%d/%d  delta %+d/%+d/%+d/%+d" % (
                exp.get("asserting", 0), exp.get("attributed", 0),
                exp.get("unattributed", 0), exp.get("both", 0),
                a - exp.get("asserting", 0), at - exp.get("attributed", 0),
                un - exp.get("unattributed", 0), bo - exp.get("both", 0))
        res.notes.append("%s  measured %d/%d/%d/%d%s" % (label, a, at, un, bo, d))
        res.notes.append("    naive subtraction (asserting - attributed) = %d; "
                         "measured unattributed = %d -- %s" %
                         (naive, un,
                          "SUBTRACTION WOULD HAVE BEEN WRONG" if naive != un
                          else "subtraction would coincide here; not used"))
        res.notes.append("    query: %s" % q)
    return "tracked terms measured", "tracked-term rows reported"


# ---------------------------------------------------------------------------
# Rule registry (spec 8). A rule with no positive-control fixture CANNOT
# REGISTER -- that is a hard loader error (spec 5).
# ---------------------------------------------------------------------------

def _f(*p):
    return os.path.join("fixtures", *p)


R2_CONTROL_TOWNS = {
    "Severance": {"gas": "Xcel Energy", "gas_state": "CONFIRMED",
                  "gas_qualifier": "most locations in Severance",
                  "page_slugs": ["R2a_wrong_utility_visible.html"]},
    "Johnstown": {"gas": "Xcel Energy", "gas_state": "CONFIRMED",
                  "gas_qualifier": "",
                  "page_slugs": ["R2b_wrong_utility_no_string.html"]},
    "Milliken": {"gas": "Xcel Energy", "gas_state": "CONFIRMED",
                 "gas_qualifier": "most of Milliken",
                 "page_slugs": ["R2c_wrong_utility_anchor_only.html"]},
}
R2_CONTROL_OVERLAY = {"R2": {"towns": R2_CONTROL_TOWNS,
                             "allowed_multi_utility_sentences": [],
                             "known_disclosure_gaps": [],
                             "review_not_fail": [],
                             "forbid_electric_utility_naming": False,
                             "known_present_control": None}}
# R2d needs BOTH sides of a split territory pinned: the inversion it tests only
# means something where some towns are Atmos and others are Xcel.
R2_SPLIT_CONTROL_TOWNS = dict(R2_CONTROL_TOWNS)
R2_SPLIT_CONTROL_TOWNS.update({
    "Greeley": {"gas": "Atmos Energy", "gas_state": "CONFIRMED",
                "gas_qualifier": "",
                "page_slugs": ["R2d_inverted_split_fact.html"]},
    "Evans": {"gas": "Atmos Energy", "gas_state": "CONFIRMED",
              "gas_qualifier": ""},
    "Eaton": {"gas": "Atmos Energy", "gas_state": "CONFIRMED",
              "gas_qualifier": ""},
})
R2_SPLIT_CONTROL_OVERLAY = {"R2": dict(R2_CONTROL_OVERLAY["R2"],
                                       towns=R2_SPLIT_CONTROL_TOWNS)}
R3_CONTROL_OVERLAY = {"R3": {"allowed_figures": [],
                             "allowed_structure_percentages": []}}
R4_CONTROL_OVERLAY = {"R4": {"programs": [
    "Colorado Weatherization Assistance Program", "Atmos Energy",
    "Xcel Energy", "Whole Home Efficiency Bonus", "Combo Bonus",
    "federal 25C"], "noun_use_constants": [],
    "retired_prohibition_strings": [],
    "attributed_exception": {"allowed": True}}}
# R4c and R4d pin the alias map and the anaphora list as well as the program
# list, because those are the values their own sub-tests depend on. Without
# pinning, R4c would pass on GCI (whose config carries the weatherization
# alias) and fail on DCI (whose does not), and a control whose result depends
# on which property happens to be loaded is not a control.
R4_INFORMAL_CONTROL_OVERLAY = {"R4": dict(
    R4_CONTROL_OVERLAY["R4"],
    program_aliases={"free state weatherization program":
                     "Colorado Weatherization Assistance Program",
                     "the Atmos rebate": "Atmos Energy",
                     "Atmos rebate": "Atmos Energy",
                     "Atmos": "Atmos Energy"})}
R4_ANAPHORA_CONTROL_OVERLAY = {"R4": dict(
    R4_CONTROL_OVERLAY["R4"],
    program_aliases={},
    program_set_anaphora=["either insulation rebate program",
                          "either rebate program", "both rebate programs",
                          "both programs", "the two programs",
                          "these programs"])}
# R4e and R4f test the two 2026-09-18 repairs -- URL text is not prose, and no
# program name crosses a sentence boundary. Both pin an EMPTY anaphora list as
# well as an empty alias map, because neither repair is about anaphora and a
# control that could be satisfied through the -SET branch would not be testing
# what its name says. Each names its two programmes by their configured
# literals, so the result cannot depend on which property is loaded.
R4_LITERAL_CONTROL_OVERLAY = {"R4": dict(
    R4_CONTROL_OVERLAY["R4"],
    program_aliases={},
    program_set_anaphora=[])}
# R4g pins the attributed exception itself, because that is what it tests.
# `publishers` is pinned as a LIST and not just `publisher`, because rule_R4
# reads `publishers` FIRST and the property configs disagree about which key
# they set -- DCI carries a three-entry `publishers` list, LGM a scalar
# `publisher` -- so pinning only the scalar would leave the control reading
# whichever property happened to be loaded, which is the exact failure the R4c
# and R4d pins exist to prevent. requires_cited_source_key is False because a
# fixture has no citation registry to resolve a key against; the cite-key half
# of the exception is already exercised on the live properties. The publisher
# is deliberately one that is NOT in the pinned programs list -- crediting
# "Atmos Energy" would have added a SECOND program name to the sentence and
# moved it into the two-named-programs branch, where the exception has always
# been reachable, so the repaired half would have gone clean without testing
# the extension at all.
R4_ATTRIBUTED_CONTROL_OVERLAY = {"R4": dict(
    R4_LITERAL_CONTROL_OVERLAY["R4"],
    attributed_exception={"allowed": True,
                          "publishers": ["Building Science Corporation"],
                          "publisher": "Building Science Corporation",
                          "requires_publisher_named": True,
                          "requires_cited_source_key": False})}
# The N3b control pins its own tool entry, so the comparison it proves does not
# depend on which property's R9.tools happens to be loaded -- LGM and GCI
# configure no tool at all.
R9_N3B_CONTROL_OVERLAY = {"R9": {"tools": [{
    "page": "R9_hidden_payload_contradiction.html",
    "visible": "#calcOutput",
    "hidden": ["lf-calc-inputs", "lf-calc-output"],
    "hidden_mirrors_visible": ["lf-calc-output"]}]}}
R7_PROP_CONTROL_OVERLAY = {"R7": {"superseded_propositions": [{
    "claim_id": "control_newest_schedule_is_jan_2024",
    "all_of": ["effective January 1, 2024"],
    "any_of": ["newest rebate schedule"],
    "why": "SYNTHETIC control entry. Pinned here for the same reason the "
           "registry control pins a synthetic registry: the control must "
           "prove the RULE reads a claim inside a script bundle's string "
           "literal, not that today's property config happens to carry a "
           "proposition that matches the fixture."}]}}
R5_CONTROL_OVERLAY = {"R3": {"allowed_thresholds": [],
                             "allowed_structure_percentages": []}}
# A SYNTHETIC derivable-constants entry, pinned the way every other control
# overlay is pinned: the control must prove the RULE works, not that DCI's
# config happens to carry an entry today. Without this the derivable-constant
# filter would be control-tested on one property and untested on the other two.
R5_DERIV_CONTROL_OVERLAY = _deep_merge(R5_CONTROL_OVERLAY, {"R5": {
    "derivable_constants": [{
        "figure": "17%",
        "subject_phrases": ["Atmospheric pressure"],
        "pages": ["R5f_derivable_constant.html"],
        "derivation_note": "CONTROL FIXTURE ENTRY. ICAO standard atmosphere, "
                           "P/P0 = (1 - 2.25577e-5*h)^5.25588; at h = 1609.3 m "
                           "this gives 0.8234, i.e. 17.7% lower than sea "
                           "level."}]}})
# R5's f_struct -- the "allowed structure percentage / tier threshold IN a
# threshold context" filter -- HAD NO CONTROL AT ALL, because R5_CONTROL_OVERLAY
# empties both lists it reads on every R5 control. That is the right default (a
# control must prove the RULE, not today's config) but it left the filter with
# no positive control on any property, which is the condition spec 5 exists to
# forbid. It matters more now: the 2026-09-20 rewrite of f_question stops
# rescuing DCI's `20% CFM 50` blower-door row, and this filter -- the one the
# spec ALREADY names for that threshold -- is what closes it instead.
#
# Both lists are pinned SYNTHETICALLY, the same way the derivable-constants
# overlay is pinned. `threshold_context_markers` is pinned too, and must be: it
# is inherited from common.json on DCI and LGM but OVERRIDDEN on GCI with a much
# broader list that includes the bare word "reduction", so without pinning, the
# fixture's "20% reduction in winter heating costs" would clear on GCI and the
# control would MISS on exactly one property.
R5_THRESH_CONTROL_OVERLAY = _deep_merge(R5_CONTROL_OVERLAY, {"R3": {
    "allowed_thresholds": ["20%", "20 percent"],
    "threshold_context_markers": [
        "tier", "threshold", "measured reduction", "of project cost",
        "qualifying minimum", "CFM", "capped at", "up to 100%",
        "structure of the rebate"]}})
R6_CONTROL_OVERLAY = {"R6": {"label_chains": [{
    "id": "control-rvalue-tier",
    "printed_var": "pctShort",
    "labels": ["You're already at or above code target.",
               "Significantly under code", "Moderately under code",
               "Close to code"],
    "severity_order": ["Close to code", "Moderately under code",
                       "Significantly under code"],
    "at_target_label": "You're already at or above code target.",
    "targets": {"basement": 15, "crawl-encap": 15, "wall-existing": 13},
    "surfaces": ["R6_label_figure_contradiction.js"]}]}}
R11_CONTROL_OVERLAY = {"R11": {"tracked_terms": [
    {"id": "cfm50_20pct", "label": "CFM 50 20% reduction",
     "patterns": ["20% reduction in CFM 50", "20% reduction in CFM50"]},
    {"id": "whe_25pct", "label": "WHE 25% bonus",
     "patterns": ["adds 25% on all standard rebates",
                  "25% on all standard rebates"]}],
    "forbid_subtraction": True}}
R8_CONTROL_OVERLAY = {"R8": {"pinned_pages": {}, "exempt_pages": [],
                             "own_effective_date_pages": [],
                             "known_holds": []}}


def _r7_registry_control():
    """A synthetic registry pinned onto the R7-REG control.

    It declares ONE supersession, for a print code that appears in NO
    `R7.superseded_identifiers` list in config/. So a hit on sub-test `A-reg`
    against the R7_registry_supersession fixture can only have come from a
    registry, which is what makes this a control for the registry half rather
    than a second control for the config list.

    Synthetic, not the property's real file, for the same reason every other
    control overlay is pinned: a control must prove the RULE works, not that
    today's data happens to contain something.
    """
    reg = Registry()
    reg.path = "<control fixture: synthetic citation registry>"
    reg.present = True
    reg.declared = True
    reg.declared_on = "2026-09-18"
    reg.entries = 2
    reg.superseded = [{
        "id": "CONTROL_RETIRED_SCHEDULE_26_01_999",
        "identifiers": ["26-01-999",
                        "control-fixture/retired-schedule-26-01-999.pdf"],
        "url": "",
        "by": "CONTROL_CURRENT_SCHEDULE",
        "on": "2026-01-01",
        "reason": "Control fixture. Retired by its successor on the stated "
                  "date; present in no config list anywhere.",
    }]
    reg.undeclared_ids = ["CONTROL_CURRENT_SCHEDULE"]
    return reg


R7_REGISTRY_CONTROL_OVERLAY = {"_registry": _r7_registry_control()}


RULES = [
    Rule("R1", "FABRICATED QUOTATION",
         "CLAIM TEST (+ string list for the hand-written-prose half, declared)",
         R1_SURF, "DEC TXT",
         "this rule cannot read the cited PDF. It asserts the PRESENCE and "
         "SHAPE of a provenance record, not the accuracy of the quote; and it "
         "cannot see a missing ellipsis or a quotation that is exact and "
         "misleading by selection.",
         rule_R1,
         controls=[
             Control("R1-A", "R1", _f("R1_fabricated_quotation.html"),
                     sub="A", repaired=_f("repaired", "R1_fabricated_quotation.html")),
             Control("R1-B", "R1", _f("R1_fabricated_quotation.html"),
                     sub="B", repaired=_f("repaired", "R1_fabricated_quotation.html"))]),

    Rule("R2", "WRONG-UTILITY CLAIM", "CLAIM TEST",
         "VIS TITLE META OG TW LD JS LOWVIS ATTR COMMENT LLMS SVGTEXT EMBED",
         "TXT for propositions; RAW for href and JS comments; SRC over the "
         "generators",
         "it enforces the config's territory and cannot discover that a "
         "town's utility changed -- that is a two-legged primary-source pass. "
         "OG image RASTERS are out of scope (spec 7.1), total on DCI.",
         rule_R2,
         controls=[
             Control("R2a", "R2", _f("R2a_wrong_utility_visible.html"),
                     R2_CONTROL_OVERLAY, sub="a", repaired=_f("repaired", "R2a_wrong_utility_visible.html")),
             Control("R2b", "R2", _f("R2b_wrong_utility_no_string.html"),
                     R2_CONTROL_OVERLAY, extra=[_f("R2b_og-image.svg")],
                     sub="a", repaired=_f("repaired", "R2b_wrong_utility_no_string.html"), repaired_extra=[_f("repaired", "R2b_og-image.svg")]),
             Control("R2c", "R2", _f("R2c_wrong_utility_anchor_only.html"),
                     R2_CONTROL_OVERLAY, sub="c", repaired=_f("repaired", "R2c_wrong_utility_anchor_only.html")),
             Control("R2d", "R2", _f("R2d_inverted_split_fact.html"),
                     R2_SPLIT_CONTROL_OVERLAY, sub="a",
                     repaired=_f("repaired", "R2d_inverted_split_fact.html")),
             # THE SRC CODE/PROSE SPLIT, on R2. Both fixtures are generator
             # modules holding a script bundle AND prose. The bundle's
             # developer COMMENT records a wrong-utility bug fixed on
             # 2026-09-08; the fixture's PROSE still makes the claim for real
             # and MUST fire, which is the proof that excluding the bundle did
             # not blind R2 to the generator. The repaired module names the
             # right utility and keeps the identical bundle, so it MUST be
             # clean -- before ctx.pool() learned that a script bundle is not
             # a proposition surface, the repair note itself fired there and
             # took GCI's whole gate red.
             # THE SRC CODE/PROSE SPLIT AS A **NAMED** REMOVAL, and the
             # blindfold proof for it. The module holds a stylesheet AND a
             # script bundle. The stylesheet must be REMOVED THROUGH THE
             # NAMED FILTER, never deleted from the pool; the claim assigned
             # to el.innerHTML inside the bundle MUST still fire, because the
             # rendered page reads exactly that literal out of the same bytes.
             # Commit 1c7b354 moved the split into ctx.pool() as a bare
             # `continue` and this fixture went RAW 1 ADJ 1 -> RAW 0 ADJ 0 on
             # R2 (wrong utility) with no finding raised and no filter row to read.
             Control("R2f", "R2", _f("R2f_src_bundle_literal.py"),
                     R2_CONTROL_OVERLAY, sub="a",
                     repaired=_f("repaired",
                                 "R2f_src_bundle_literal.py")),
             Control("R2e", "R2", _f("R2e_src_js_comment.py"),
                     R2_CONTROL_OVERLAY, sub="a",
                     repaired=_f("repaired", "R2e_src_js_comment.py"))]),

    Rule("R3", "REBATE DOLLAR FIGURE",
         "CLAIM TEST for the rank/magnitude half (T3); STRING+WINDOW LIST for "
         "the numeral half (T1 T2 T4), declared",
         "VIS TITLE META OG TW LD JS CSS LOWVIS ATTR LLMS SITEMAP EMBED SVGTEXT",
         "RAW for T1/T2/T4; TXT for T3; SRC for the generator reachability check",
         "T1 is anchored on `$`, so it cannot see a figure written as bare "
         "digits -- that is what T2 exists for; and neither can see a removal "
         "note that restates the figure in words with no numeral.",
         rule_R3,
         controls=[
             Control("R3a", "R3", _f("R3a_js_comment_cap.html"),
                     R3_CONTROL_OVERLAY, sub="T2", repaired=_f("repaired", "R3a_js_comment_cap.html")),
             Control("R3b", "R3", _f("R3b_jsonld_amount.html"),
                     R3_CONTROL_OVERLAY, sub="T1", repaired=_f("repaired", "R3b_jsonld_amount.html")),
             Control("R3c", "R3", _f("R3c_rank_claim_no_numeral.html"),
                     R3_CONTROL_OVERLAY, sub="T3", repaired=_f("repaired", "R3c_rank_claim_no_numeral.html"))]),

    Rule("R4", "STACKING ASSERTION OR DENIAL", "CLAIM TEST",
         "VIS TITLE META OG TW LD JS LOWVIS ATTR COMMENT LLMS EMBED",
         "TXT sentence-split; SRC for the generator half",
         "it enforces silence; it cannot verify whether stacking is actually "
         "permitted, and it classifies rather than decides -- a NEUTRAL noun "
         "use is reported under FILTER, never failed.",
         rule_R4,
         controls=[
             Control("R4a", "R4", _f("R4a_stacking_denial_jsonld.html"),
                     R4_CONTROL_OVERLAY, sub="DENIES", repaired=_f("repaired", "R4a_stacking_denial_jsonld.html")),
             Control("R4b", "R4", _f("R4b_stacking_assertion_prose.html"),
                     R4_CONTROL_OVERLAY, sub="ASSERTS", repaired=_f("repaired", "R4b_stacking_assertion_prose.html")),
             Control("R4c", "R4", _f("R4c_informal_program_names.html"),
                     R4_INFORMAL_CONTROL_OVERLAY, sub="DENIES",
                     repaired=_f("repaired",
                                 "R4c_informal_program_names.html")),
             Control("R4d", "R4", _f("R4d_anaphoric_program_set.html"),
                     R4_ANAPHORA_CONTROL_OVERLAY, sub="DENIES-SET",
                     repaired=_f("repaired",
                                 "R4d_anaphoric_program_set.html")),
             # THE TWO 2026-09-18 REPAIRS, each held by its own pair. The
             # FIRING half proves the rule still sees the real claim; the
             # repaired half is the false positive the repair removed, and it
             # FIRED ON REPAIRED before the repair and is clean after it. That
             # is the whole test: without the firing half a repair is
             # indistinguishable from switching the rule off.
             Control("R4e", "R4", _f("R4e_url_is_not_prose.html"),
                     R4_LITERAL_CONTROL_OVERLAY, sub="ASSERTS",
                     repaired=_f("repaired", "R4e_url_is_not_prose.html")),
             Control("R4f", "R4", _f("R4f_two_programs_one_sentence.html"),
                     R4_LITERAL_CONTROL_OVERLAY, sub="ASSERTS",
                     repaired=_f("repaired",
                                 "R4f_two_programs_one_sentence.html")),
             # The attributed exception, reached from the ONE-PROGRAMME class.
             # It was reachable only from ASSERTS/DENIES until 2026-09-18; this
             # pair is what makes that extension a measured loosening rather
             # than a silent one.
             Control("R4g", "R4", _f("R4g_one_program_attributed.html"),
                     R4_ATTRIBUTED_CONTROL_OVERLAY, sub="ASSERTS-1P",
                     repaired=_f("repaired",
                                 "R4g_one_program_attributed.html")),
             # THE SRC CODE/PROSE SPLIT AS A **NAMED** REMOVAL, and the
             # blindfold proof for it. The module holds a stylesheet AND a
             # script bundle. The stylesheet must be REMOVED THROUGH THE NAMED
             # FILTER, never deleted from the pool; the claim assigned to
             # el.innerHTML inside the bundle MUST still fire, because the
             # rendered page reads exactly that literal out of the same bytes.
             # Commit 1c7b354 moved the split into ctx.pool() as a bare
             # `continue` and this fixture went RAW 1 ADJ 1 -> RAW 0 ADJ 0 on
             # R4 (stacking) with no finding raised and no filter row to read.
             Control("R4h", "R4", _f("R4h_src_bundle_literal.py"),
                     R4_LITERAL_CONTROL_OVERLAY, sub="ASSERTS",
                     repaired=_f("repaired",
                                 "R4h_src_bundle_literal.py"))]),

    Rule("R5", "UNCITED STATISTIC", "CLAIM TEST",
         "VIS TITLE META OG TW LD JS LOWVIS LLMS EMBED SVGTEXT",
         "TXT for prose; RAW + JS string-literal extraction for JS; SRC over "
         "the generators",
         "it asserts attribution EXISTS and never reads the source, so an "
         "attributed figure can still be wrong; it scopes attribution to the "
         "sentence and the page, so a figure sourced two paragraphs away reads "
         "as uncited; and a qualitative magnitude with no numeral is invisible "
         "to it.",
         rule_R5,
         controls=[Control("R5", "R5", _f("R5_uncited_statistic.html"),
                           R5_CONTROL_OVERLAY, sub="mag", repaired=_f("repaired", "R5_uncited_statistic.html")),
                   # f_instat's threshold, both directions. The fixture's
                   # "see a 15% reduction in heating and cooling costs" is a
                   # DIFFERENT claim from the ENERGY STAR "save an average of
                   # 15% on heating and cooling costs" quoted on the same page
                   # -- overlap 3, below the measured threshold of 4, so it
                   # MUST still fire. The repaired page restates the
                   # quotation instead, and MUST clear. Its cellulose
                   # paragraph is the tokenizer half: "settles" against
                   # "will settle" scores 4 unfolded and 5 folded, so before
                   # the fold it FIRED ON REPAIRED and the control failed.
                   Control("R5-INSTAT", "R5", _f("R5b_restated_quotation.html"),
                           R5_CONTROL_OVERLAY, sub="mag",
                           repaired=_f("repaired",
                                       "R5b_restated_quotation.html")),
                   # The publisher-as-subject predicate, both directions.
                   # The fixture is the probe that refused "estimates" as a
                   # plain attribution verb: the publisher sits 47 characters
                   # from the figure, inside the proximity window, and did not
                   # make the claim -- it MUST fire. The repaired page makes
                   # the same publisher the subject of the same verb and MUST
                   # clear.
                   Control("R5-SUBJECT", "R5",
                           _f("R5d_publisher_not_subject.html"),
                           R5_CONTROL_OVERLAY, sub="mag",
                           repaired=_f("repaired",
                                       "R5d_publisher_not_subject.html")),
                   # The possessive short form, both directions. The fixture
                   # names Xcel as the PAYER beside the figure and MUST still
                   # fire -- that is the whole reason the bare token is not in
                   # recognised_publishers. The repaired page is llms.txt's
                   # real shape, where Xcel's rebate is what requires the
                   # figure, and MUST clear.
                   Control("R5-SHORTFORM", "R5",
                           _f("R5e_publisher_short_form.html"),
                           R5_CONTROL_OVERLAY, sub="mag",
                           repaired=_f("repaired",
                                       "R5e_publisher_short_form.html")),
                   # R5.derivable_constants, both directions. The fixture
                   # carries the SAME figure, 17%, as an ordinary marketing
                   # claim about heating bills -- the entry must NOT pardon it,
                   # which is what stops the key becoming an allowlist for a
                   # number. The repaired page is the physical constant with
                   # its subject phrase, and MUST clear.
                   Control("R5-DERIVABLE", "R5",
                           _f("R5f_derivable_constant.html"),
                           R5_DERIV_CONTROL_OVERLAY, sub="mag",
                           repaired=_f("repaired",
                                       "R5f_derivable_constant.html")),
                   # The SRC code/prose split, both directions. Both fixtures
                   # are generator modules holding a stylesheet AND prose. The
                   # fixture's prose carries an uncited 35% and MUST fire --
                   # that is the proof the stylesheet exclusion did not blind
                   # R5 to the generator. The repaired module attributes that
                   # figure and keeps the identical stylesheet, so it MUST be
                   # clean: before this fix the stylesheet's own 0%/50%/100%
                   # fired there and the control failed.
                   Control("R5-SRCCODE", "R5", _f("R5g_src_code.py"),
                           R5_CONTROL_OVERLAY, sub="mag",
                           repaired=_f("repaired", "R5g_src_code.py")),
                   # src_dup's 48-character prefix, both directions. The
                   # fixture's generator string OPENS with the rendered page's
                   # real attributed sentence and then adds a figure that
                   # renders nowhere and is sourced by nothing: under the
                   # prefix probe it was CLEAN, which is the silent miss, and
                   # under the full-sentence probe it MUST fire. The repaired
                   # generator string is a true restatement and MUST clear, so
                   # the repair cannot have turned src_dup off. NEG15 remains
                   # the other half -- correct copy with markup and an em dash
                   # inside the first 48 characters, which must stay clean.
                   # Same split, same blindfold proof, on R5. This one
                   # also missed at 889e172, where the split was an
                   # R5-ONLY filter keyed to the whole run: the literal
                   # went down with the bundle.
                   Control("R5-SRCLITERAL", "R5",
                           _f("R5i_src_bundle_literal.py"),
                           R5_CONTROL_OVERLAY, sub="mag",
                           repaired=_f("repaired",
                                       "R5i_src_bundle_literal.py")),
                   Control("R5-SRCPREFIX", "R5", _f("R5h_src_prefix"),
                           R5_CONTROL_OVERLAY, sub="mag",
                           repaired=_f("repaired", "R5h_src_prefix")),
                   # f_question, both directions, and the fixture half is the
                   # BLINDFOLD PROOF rather than the defect.
                   #
                   # THE FIXTURE MUST FIRE THREE TIMES AND MUST GO ON FIRING
                   # AFTER THE FILTER EXISTS. Question one carries 20% and the
                   # page holds no other 20% at all, so there is no anchor and
                   # the question is judged on its own. Question two carries
                   # 35% and the page DOES hold another 35% sentence -- an
                   # uncited one -- which is exactly the laundering route a
                   # blanket "skip interrogatives" would have opened: an
                   # unattributed companion is not in the cleared set, so it
                   # cannot anchor anything, and it fires on its own account.
                   # Three hits before the change, three after.
                   #
                   # THE REPAIRED HALF IS THE FIX PROOF. Same two questions,
                   # each now with a cited-stat on the page carrying its
                   # figure. It FIRED BEFORE f_question existed -- measured:
                   # local overlap 3 for the CFM50 pair ({cfm, reduc, test})
                   # and 0 for the ENERGY STAR pair, both under f_instat's
                   # threshold of 4 -- and is clean after. Neither question
                   # clears through f_instat or f_pub; if a future edit makes
                   # either of them clear that way, this control stops testing
                   # f_question and must be rewritten rather than retired.
                   Control("R5-QUESTION", "R5",
                           _f("R5j_interrogative_anchor.html"),
                           R5_CONTROL_OVERLAY, sub="mag",
                           repaired=_f("repaired",
                                       "R5j_interrogative_anchor.html")),
                   # ---------------------------------------------------------
                   # THE THREE A1 CONTROLS, 2026-09-20. Each fixture measured
                   # ZERO adjudicated hits against claim_gate.py at bfbad20 on
                   # all three property configs -- that is the hole, measured
                   # rather than asserted -- and each fires after the rewrite.
                   # Each has a repaired counterpart that must be CLEAN, so the
                   # trio cannot be satisfied by weakening or deleting
                   # f_question: doing that reddens the repaired half.
                   #
                   # R5-QLAUNDER. Seven attributed statistics, seven uncited
                   # questions, each question sharing ONLY A NUMERAL with the
                   # statistic that licensed it. The last pair is RULES_SPEC's
                   # own named adversary -- "Did you know homes lose 40% of
                   # their heat through the attic?" beside an unrelated
                   # attributed ENERGY STAR 40% -- which the spec says must
                   # keep firing and which did not. The repaired page keeps the
                   # same seven questions and gives each an ATTRIBUTED PROSE
                   # anchor stating the claim the question asks about. The
                   # anchors are deliberately NOT cited-stat blocks: a
                   # cited-stat would set r5_instat and let f_instat clear the
                   # question, and then this control would stop testing
                   # f_question. Measured: all seven repaired clears are
                   # credited to the f_question row.
                   Control("R5-QLAUNDER", "R5",
                           _f("R5k_question_numeral_laundering.html"),
                           R5_CONTROL_OVERLAY, sub="mag",
                           repaired=_f("repaired",
                                       "R5k_question_numeral_laundering.html")),
                   # R5-QTAG. A tag question is a flat assertion plus one
                   # character, and the old filter tested endswith("?").
                   # The repaired page attributes the same three sentences --
                   # including one that KEEPS its tag -- which is the proof
                   # that the class is not banned, only the unattributed
                   # assertion is.
                   Control("R5-QTAG", "R5", _f("R5l_tag_question.html"),
                           R5_CONTROL_OVERLAY, sub="mag",
                           repaired=_f("repaired", "R5l_tag_question.html")),
                   # R5-QSURFACE. Both directions of the cross-surface hole: a
                   # <meta name="description"> anchoring a claim made in
                   # VISIBLE PROSE, and visible prose anchoring a question
                   # buried in JSON-LD FAQ markup. The repaired page moves each
                   # anchor onto the question's OWN surface and nothing else.
                   Control("R5-QSURFACE", "R5",
                           _f("R5m_cross_surface_anchor.html"),
                           R5_CONTROL_OVERLAY, sub="mag",
                           repaired=_f("repaired",
                                       "R5m_cross_surface_anchor.html")),
                   # R5-THRESHOLD. f_struct had NO control on any property.
                   # The fixture carries 20%/20 percent as ORDINARY MARKETING
                   # CLAIMS with no threshold context, and MUST fire even with
                   # the threshold list pinned -- that is what stops the entry
                   # being an allowlist for a number. The repaired page is the
                   # qualifying-threshold statement and the blower-door
                   # interrogative that asks about it, neither attributed to
                   # anybody, and MUST clear on the threshold context alone.
                   # That repaired half is the A1-KEEP proof: the row f_question
                   # used to rescue is now closed by the instrument RULES_SPEC
                   # already declares for it.
                   Control("R5-THRESHOLD", "R5",
                           _f("R5n_threshold_exclusion.html"),
                           R5_THRESH_CONTROL_OVERLAY, sub="mag",
                           repaired=_f("repaired",
                                       "R5n_threshold_exclusion.html"))]),

    Rule("R6", "SELF-CONTRADICTING OUTPUT", "CLAIM TEST",
         "JS SRC (and, for opt-in R6b, the rendered DOM of the page and EMBED)",
         "SRC and RAW -- not TXT, which deletes the script body",
         "R6a reads the branch quantity statically and cannot enumerate the "
         "rendered cross-product; R6b does that and is opt-in. G1/G2 use a "
         "line-scoped conditional-chain scanner over the emitted JS, not a "
         "JS parser. It asserts internal consistency, never calibration, and "
         "never that a target value is right.",
         rule_R6,
         controls=[
             Control("R6a-G1", "R6", _f("R6_label_figure_contradiction.js"),
                     R6_CONTROL_OVERLAY, sub="G1", repaired=_f("repaired", "R6_label_figure_contradiction.js")),
             Control("R6a-G2", "R6", _f("R6_label_figure_contradiction.js"),
                     R6_CONTROL_OVERLAY, sub="G2", repaired=_f("repaired", "R6_label_figure_contradiction.js"))]),

    Rule("R7", "SUPERSEDED-SOURCE CLAIM",
         "CLAIM TEST for the proposition half; STRING LIST for the identifier "
         "half, declared",
         "VIS TITLE META OG TW LD JS LOWVIS ATTR COMMENT LLMS EMBED",
         "RAW for identifiers and URLs; TXT sentence-split for propositions; "
         "SRC for the generator half",
         "it enforces a list and cannot notice a source that went stale since "
         "the config was written -- a citation going stale independently of "
         "the fact it supports. It must never list a source that is merely "
         "403 (bot-blocked, not dead).",
         rule_R7,
         controls=[
             Control("R7-A", "R7", _f("R7_superseded_source.html"), sub="A", repaired=_f("repaired", "R7_superseded_source.html")),
             Control("R7-B", "R7", _f("R7_superseded_source.html"), sub="B", repaired=_f("repaired", "R7_superseded_source.html")),
             # THE SRC CODE/PROSE SPLIT AS A **NAMED** REMOVAL, and the
             # blindfold proof for it. The module holds a stylesheet AND a
             # script bundle. The stylesheet must be REMOVED THROUGH THE NAMED
             # FILTER, never deleted from the pool; the claim assigned to
             # el.innerHTML inside the bundle MUST still fire, because the
             # rendered page reads exactly that literal out of the same bytes.
             # Commit 1c7b354 moved the split into ctx.pool() as a bare
             # `continue` and this fixture went RAW 1 ADJ 1 -> RAW 0 ADJ 0 on
             # R7 (superseded source) with no finding raised and no filter row to read.
             Control("R7c", "R7", _f("R7c_src_bundle_literal.py"),
                     R7_PROP_CONTROL_OVERLAY, sub="B",
                     repaired=_f("repaired",
                                 "R7c_src_bundle_literal.py")),
             Control("R7-REG", "R7", _f("R7_registry_supersession.html"),
                     overlay=R7_REGISTRY_CONTROL_OVERLAY, sub="A-reg",
                     repaired=_f("repaired",
                                 "R7_registry_supersession.html")),
             # THE BLINDFOLD PROOF FOR THE 2026-09-20 RETIREMENT of claim_id
             # whe_audit_entry_path_hes_plus. That entry bound supersession to
             # the bare string "Home Energy Squad", on the premise that the
             # phrase lived only in the superseded 2024 sheet. The premise is
             # REFUTED: measured 2026-09-20, the phrase occurs 4 times on
             # Xcel's OWN CURRENT Whole Home Efficiency page and 15 times on
             # its Home Energy Squad page (both HTTP 200, Googlebot UA), and
             # ONCE in the superseded sheet. Retiring it closed 107 findings
             # on DCI that were all TRUE, first-party-sourced copy.
             # This control is the other half of that change: R7 half B must
             # STILL fire on the superseded sheet's OWN entry-path wording,
             # which it does through whe_audit_entry_path_begin_with. The
             # fixture carries no synthetic overlay ON PURPOSE -- what it
             # proves is that the SHIPPING config still has teeth here.
             Control("R7d", "R7", _f("R7d_superseded_entry_path.html"),
                     sub="B",
                     repaired=_f("repaired",
                                 "R7d_superseded_entry_path.html"))]),

    Rule("R8", "STALE REVIEW DATE", "CLAIM TEST",
         "VIS ATTR LD SITEMAP META OG TW EMBED (+ git log as a non-artifact "
         "input)",
         "RAW for datetime and lastmod; DEC for the visible footer text",
         "a date is a claim about a human act: the gate can prove a date is "
         "impossible or contradicted and can never prove a review occurred. "
         "Part (d) strips the review-date line before diffing so it cannot "
         "count as its own change, and walks at most 15 commits back.",
         rule_R8,
         controls=[
             Control("R8a", "R8", _f("R8a_stale_review_date.html"),
                     R8_CONTROL_OVERLAY, sub="d", repaired=_f("repaired", "R8a_stale_review_date.html")),
             Control("R8b", "R8", _f("R8b_review_precedes_creation.html"),
                     R8_CONTROL_OVERLAY, sub="a", repaired=_f("repaired", "R8b_review_precedes_creation.html")),
             Control("R8c", "R8", _f("R8c_future_review_date.html"),
                     R8_CONTROL_OVERLAY, sub="b", repaired=_f("repaired", "R8c_future_review_date.html")),
             Control("R8c-c", "R8", _f("R8c_future_review_date.html"),
                     R8_CONTROL_OVERLAY, sub="c", repaired=_f("repaired", "R8c_future_review_date.html"))]),

    Rule("R9", "INTERNAL CONTRADICTION", "CLAIM TEST",
         "all surfaces, including LLMS and ATTR/LOWVIS",
         "TXT sentence-split, plus LD leaves, plus JS string literals",
         "it reports a contradiction and never which side is right; it is a "
         "registry of known-contested subjects, not a semantic engine, so a "
         "contradiction on a subject not in claim_subjects is invisible; the "
         "cross-property half needs --peer; and it flags display:none as a "
         "TRAP without being a layout engine.",
         rule_R9,
         controls=[
             Control("R9-N1", "R9", _f("R9_cross_surface_contradiction"),
                     sub="N1", repaired=_f("repaired", "R9_cross_surface_contradiction")),
             Control("R9-N2", "R9", _f("R9_cross_surface_contradiction"),
                     sub="N2", repaired=_f("repaired", "R9_cross_surface_contradiction")),
             Control("R9-N3b", "R9",
                     _f("R9_hidden_payload_contradiction.html"),
                     R9_N3B_CONTROL_OVERLAY, sub="N3b",
                     repaired=_f("repaired",
                                 "R9_hidden_payload_contradiction.html"))]),

    Rule("R10", "DANGLING PROMISE", "CLAIM TEST",
         "VIS TITLE META OG TW LD LOWVIS ATTR LLMS EMBED",
         "TXT sentence-split for the promise; RAW for the destination's figure "
         "count; DEC for refusal markers",
         "it does not fetch external URLs and treats an off-property "
         "destination as compliant by construction; it cannot see a promise of "
         "something other than a figure; and a refusal phrased in words the "
         "config does not know reads as a destination with no figures.",
         rule_R10,
         controls=[
             Control("R10-anchor", "R10", _f("R10_dangling_promise"),
                     sub="anchor", repaired=_f("repaired", "R10_dangling_promise")),
             Control("R10-reflexive", "R10", _f("R10_dangling_promise"),
                     sub="reflexive", repaired=_f("repaired", "R10_dangling_promise"))]),

    Rule("R11", "ATTRIBUTION DEBT", "CLAIM TEST",
         "VIS LD LOWVIS META OG TW LLMS",
         "TXT, plus block-boundary resolution on RAW",
         # The print code that used to be named here, 25-12-215, was RETRACTED
         # on 2026-09-20: 32 code-bearing first-party probes across every
         # directory Xcel serves this sheet from returned 404, against six live
         # 200 controls in the same directories, and the Wayback index of
         # xcelenergy.com holds zero URLs containing it. See
         # config/common.json R7.current_replacements_note. The blind spot is
         # unchanged; only the document it named is gone.
         "it reports and never blocks; it cannot tell whether a claim is true "
         "(all five tracked DCI terms are accurate to the current Xcel CO "
         "residential rebate summary) nor whether "
         "attribution is OWED, which is a Director judgement.",
         rule_R11, blocking=False,
         controls=[Control("R11", "R11", _f("R11_attribution_debt.html"),
                           R11_CONTROL_OVERLAY, sub="nonsubtractive", repaired=_f("repaired", "R11_attribution_debt.html"))]),
]

OPT_IN_RULES = {
    "R6b": "browser cross-product",
}


def validate_registry():
    errs = []
    for r in RULES:
        if not r.controls:
            errs.append("rule %s has no positive-control fixture and cannot "
                        "register (spec 5)" % r.rid)
        if not (r.blind_spot or "").strip():
            errs.append("rule %s has an empty blind_spot field (spec 4.5)"
                        % r.rid)
        for c in r.controls:
            p = os.path.join(_HERE, c.fixture)
            if not os.path.exists(p):
                errs.append("rule %s control %s: fixture missing at %s"
                            % (r.rid, c.cid, c.fixture))
    return errs


# ---------------------------------------------------------------------------
# Controls (spec 5). Run BEFORE any rule, against fixture files only.
# ---------------------------------------------------------------------------

NEGATIVES = ["NEG%02d" % i for i in range(1, 19)]
# The reference date the negative fixtures were written against. Fixed on
# purpose: see the neg_overlay comment in run_controls().
NEG_ASOF = "2026-09-17"


def _fixture_paths(p):
    if os.path.isdir(p):
        out = []
        for root, dirs, files in os.walk(p):
            dirs.sort()
            for f in sorted(files):
                if f.endswith(".gitfacts.json") or f == "overlay.json":
                    continue
                out.append(os.path.join(root, f))
        return sorted(out)
    return [p]


CONTROL_NO_REPO = os.path.join(_HERE, "fixtures", "_CONTROL_HAS_NO_REPO_")


def _control_ctx(base_cfg, overlay, paths, repo):
    """Build a control context that CANNOT reach the repo under test.

    `ctx.repo` is pointed at a path that does not exist, so any rule that
    touches the filesystem finds nothing instead of finding the real tree. This
    is the fix for the halt-level defect: rule_R6 used to read
    os.path.join(ctx.repo, chain['generator']) off the real disk inside a
    NEGATIVE-control context, so on a DCI tree carrying the R6 calculator
    defect all 14 negative fixtures FALSE-ALARMed with the real finding
    attached and the gate exited 2 "NOT RUN" -- it refused to run precisely
    when the defect it exists to catch was present.
    """
    cfg = _deep_merge(base_cfg, overlay or {})
    ctx = Ctx(base_cfg["key"], CONTROL_NO_REPO, cfg, control=True)
    for p in paths:
        rel = os.path.relpath(p, _HERE).replace(os.sep, "/")
        # A `.py` IN A FIXTURE SET IS AN SRC PSEUDO-ARTIFACT, NOT A .txt PAGE.
        # Without this branch the control harness could not host the SRC
        # normalization at all: parse_artifact falls through to kind="txt" for
        # any unknown extension, so a generator fixture arrived as a rendered
        # page and ctx.src_artifacts stayed empty. That left every filter that
        # reads SRC -- src_dup above all -- with NO control, which is exactly
        # how src_dup shipped comparing raw markup against tag-stripped prose.
        # This is NOT the contamination channel the comment below closes: that
        # one handed the control the REPO UNDER TEST's generators. This one
        # reads a file that is IN the fixture set, so isolation is unchanged.
        if p.endswith(".py"):
            with open(p, "r", encoding="utf-8") as fh:
                src = fh.read()
            a = S.src_artifact(os.path.basename(p), S.src_string_runs(src))
            if a.surfaces:
                ctx.src_artifacts.append(a)
                ctx.by_rel[a.rel] = a
            continue
        art = S.parse_artifact(rel.rsplit("/", 1)[-1], p)
        ctx.artifacts.append(art)
        ctx.by_rel[art.rel] = art
        stem = os.path.splitext(p)[0]
        pre = os.path.join(os.path.dirname(p),
                           os.path.basename(stem).split("_")[0])
        for s in (p + ".gitfacts.json", stem + ".gitfacts.json",
                  pre + ".gitfacts.json"):
            if os.path.isfile(s):
                with open(s, "r", encoding="utf-8") as fh:
                    ctx.gitfacts.add_sidecar(art.rel, json.load(fh))
    # A CONTROL MUST NEVER SEE THE REPO UNDER TEST'S GENERATORS.
    #
    # This read `base_cfg.get("_gen")` -- the real repo's parsed generator
    # source, handed in by run_controls four lines below a comment saying
    # exactly this. The sixth adversarial read proved it live: adding two
    # entries to a scratch property's CITED_SOURCES, generator source ONLY with
    # public/ never regenerated, produced `*** FIRES ON REPAIRED ***` on
    # R9-N2's repaired fixture and `*** FALSE ALARM ***` on NEG05, and drove
    # the gate to exit 2 -- `CLAIM GATE: NOT RUN` -- on innocent canon
    # fixtures. `isolation_breach()` cannot see it: it checks a hit's `rel`,
    # and the contamination arrives as injected SURFACES ON the fixture, so the
    # hit carries the fixture's own rel. It is watching the wrong axis.
    #
    # This is the same contamination class as the R6 generator read, one layer
    # up, and it is worse now: with the gate wired into two properties'
    # regen_all.sh under `set -e`, an ordinary edit to a generator could red a
    # production build with a control failure that has nothing to do with the
    # edit -- and a repo that acquired a genuine contradiction could, through
    # the same channel, silence the control that would have caught it.
    #
    # Controls now get EMPTY generator facts. A control that genuinely needs
    # them pins its own SYNTHETIC ones through its overlay, read off the merged
    # config exactly as `_registry` is.
    ctx.gen = cfg.get("_gen") or S.GeneratorFacts()
    # Pinned by run_controls exactly as _gen is. A control must never open the
    # repo under test: that is how the R6 generator read turned one live defect
    # into fourteen false alarms on innocent fixtures. Read off the MERGED
    # config, not the base, so a control can pin its own synthetic registry --
    # which is the only way to control-test the registry half without making
    # the test depend on whichever property happens to be loaded.
    ctx.registry = cfg.get("_registry") or Registry()
    build_claim_set(ctx)
    return ctx


def isolation_breach(ctx, res):
    """A control finding may only name a fixture. Any hit naming a repo
    artifact means a rule reached outside its fixture read set."""
    allowed = set(ctx.by_rel)
    bad = []
    for h in list(res.raw) + list(res.adjudicated):
        rel = h.rel or ""
        if rel.startswith("public/") or rel.startswith("/"):
            bad.append(rel)
        elif rel and rel not in allowed and "/" in rel and \
                not rel.startswith("fixtures"):
            bad.append(rel)
    return sorted(set(bad))


def mtimes(repo):
    pub = os.path.join(repo, "public")
    out = {}
    if not os.path.isdir(pub):
        return out
    for root, dirs, files in os.walk(pub):
        dirs.sort()
        for f in sorted(files):
            p = os.path.join(root, f)
            out[p] = os.stat(p).st_mtime_ns
    return out


def run_controls(out, cfg, repo, opt_in, gen, registry=None):
    """Every positive control runs BEFORE any rule touches the real corpus,
    and the gate fails loudly -- exit 2 -- if any control does not fire."""
    before = mtimes(repo)
    base = dict(cfg)
    # DELIBERATELY NOT `base["_gen"] = gen`. See _control_ctx: handing the
    # repo-under-test's generator source to a control is a contamination
    # channel that turned innocent fixtures red and drove the gate to exit 2.
    base.pop("_gen", None)
    base["_registry"] = registry or Registry()
    pos_detected = pos_missed = 0
    neg_clean = neg_false = 0
    rows = []

    for rule in RULES:
        for c in rule.controls:
            path = os.path.join(_HERE, c.fixture)
            paths = _fixture_paths(path)
            for e in c.extra:
                paths = paths + _fixture_paths(os.path.join(_HERE, e))
            ctx = _control_ctx(base, _deep_merge({"R8": {"today": NEG_ASOF}},
                                                 c.overlay), sorted(paths),
                               repo)
            res = RuleResult(rule)
            try:
                rule.fn(ctx, res)
            except ArithmeticMismatch as exc:
                rows.append(("+", c.cid, c.fixture,
                             "*** MISSED *** filter arithmetic: %s" % exc))
                pos_missed += 1
                continue
            except Exception as exc:
                rows.append(("+", c.cid, c.fixture,
                             "*** MISSED *** %s: %s"
                             % (exc.__class__.__name__, exc)))
                pos_missed += 1
                continue
            breach = isolation_breach(ctx, res)
            if breach:
                rows.append(("+", c.cid, c.fixture,
                             "*** ISOLATION BREACH *** control read outside "
                             "its fixture set: %s" % ", ".join(breach[:3])))
                pos_missed += 1
                continue
            hits = res.adjudicated
            if c.sub:
                hits = [h for h in hits if h.sub == c.sub]
            if len(hits) >= c.expect:
                subs = sorted(set(h.sub for h in res.adjudicated))
                rows.append(("+", c.cid, c.fixture,
                             "DETECTED  (%d %s: %s)"
                             % (len(hits), c.sub or "any sub-test",
                                ",".join(subs))))
                pos_detected += 1
            else:
                rows.append(("+", c.cid, c.fixture,
                             "*** MISSED *** (0 hits on the sub-test this "
                             "control proves: %s)" % (c.sub or "any")))
                pos_missed += 1

    rep_clean = rep_fired = rep_absent = 0
    for rule in RULES:
        for c in rule.controls:
            if not c.repaired:
                rep_absent += 1
                rows.append(("~", c.cid, "(no repaired counterpart)",
                             "NOT TESTED -- this control has no repair "
                             "fixture, so it is not proven to be a control"))
                continue
            rpath = os.path.join(_HERE, c.repaired)
            if not os.path.exists(rpath):
                # A CONTROL FAILURE, not a NOT TESTED. A registered control
                # whose repair fixture is gone is the same class as a rule with
                # no positive control, which the loader already refuses -- and
                # reporting it as NOT TESTED with exit 0 made `rm` the cheapest
                # way past a failing repair test.
                rows.append(("~", c.cid, c.repaired,
                             "*** REPAIR FIXTURE MISSING *** the control "
                             "declares one and it is not on disk; a control "
                             "whose repair test cannot run is not a control"))
                rep_fired += 1
                continue
            paths = _fixture_paths(rpath)
            for e in c.repaired_extra:
                ep = os.path.join(_HERE, e)
                if os.path.exists(ep):
                    paths = paths + _fixture_paths(ep)
            # A SUBSTANCE FLOOR. The repair test asserted only "produces zero
            # hits on this sub-test", which a GUTTED file satisfies trivially:
            # replacing a repaired fixture with a zero-byte file, or with an
            # empty page, both gave "24 repaired-clean, 0 FIRE ON REPAIRED"
            # and exit 0. A repaired fixture must still be the same document
            # with the defect removed.
            osize = sum(os.path.getsize(x) for x in
                        _fixture_paths(os.path.join(_HERE, c.fixture))
                        if os.path.isfile(x))
            rsize = sum(os.path.getsize(x) for x in paths
                        if os.path.isfile(x))
            # SUBSTANCE, NOT JUST SIZE. A byte floor alone passes a 53% file
            # of pure padding and fails a 41% file of real prose. Token
            # OVERLAP is the cheap structural check: a repaired fixture is the
            # same document with the defect removed, so it must still share
            # most of the original's words.
            def _toks(paths_):
                out = set()
                for x in paths_:
                    if not os.path.isfile(x):
                        continue
                    try:
                        with open(x, "r", encoding="utf-8",
                                  errors="replace") as fh:
                            out |= set(re.findall(r"[A-Za-z]{3,}",
                                                  fh.read().lower()))
                    except OSError:
                        pass
                return out

            otok = _toks(_fixture_paths(os.path.join(_HERE, c.fixture)))
            rtok = _toks(paths)
            share = (len(otok & rtok) / float(len(otok))) if otok else 1.0
            if osize and rsize < 120:
                why = "%d bytes, under the 120-byte floor" % rsize
            elif otok and share < 0.30:
                why = ("shares only %.0f%% of the original's word tokens "
                       "(floor 30%%) -- padding is not substance"
                       % (100.0 * share))
            else:
                why = ""
            if why:
                rows.append(("~", c.cid, c.repaired,
                             "*** REPAIRED FIXTURE TOO THIN *** %s; %d bytes "
                             "against the original's %d (%.0f%%). A gutted "
                             "file passes a zero-hit test trivially"
                             % (why, rsize, osize,
                                100.0 * rsize / osize if osize else 0)))
                rep_fired += 1
                continue
            ctx = _control_ctx(base, _deep_merge({"R8": {"today": NEG_ASOF}},
                                                 c.overlay), sorted(paths),
                               repo)
            res = RuleResult(rule)
            try:
                rule.fn(ctx, res)
            except Exception as exc:
                rows.append(("~", c.cid, c.repaired,
                             "*** REPAIR TEST CRASHED *** %s: %s"
                             % (exc.__class__.__name__, exc)))
                rep_fired += 1
                continue
            hits = [h for h in res.adjudicated
                    if (not c.sub) or h.sub == c.sub]
            if hits:
                rows.append(("~", c.cid, c.repaired,
                             "*** FIRES ON REPAIRED *** %d hit(s) on sub %s: %s"
                             % (len(hits), c.sub, hits[0].text[:80])))
                rep_fired += 1
            else:
                rows.append(("~", c.cid, c.repaired,
                             "repaired-clean (0 hits on sub %s)" % c.sub))
                rep_clean += 1

    # A negative control's correctness is a property of the FIXTURE, not of
    # the operator's as-of date. NEG11 carries a hardcoded 2026-08-07, so any
    # run with --today before that turned it into a future date, false-alarmed
    # R8 and aborted the whole gate. Negative controls are therefore evaluated
    # against the fixture reference date.
    neg_overlay = {"R8": {"today": NEG_ASOF}}
    for neg in NEGATIVES:
        # A negative fixture may be ONE .html or a DIRECTORY. The directory
        # form exists because a correct-copy vector can need more than one
        # file to be stated at all: NEG15's whole point is a generator string
        # and the page it renders into, and one .html cannot express that.
        path = os.path.join(FIXTURES, "negative", neg)
        if not os.path.isdir(path):
            path = path + ".html"
        label = "fixtures/negative/%s" % os.path.basename(path)
        # A negative fixture DIRECTORY may carry an `overlay.json`. Without it
        # a config-KEYED rule cannot be exercised by a negative control at all:
        # R9's tool check looks its page up by the rel named in R9.tools, which
        # in the real config is a public/ path no fixture can ever match, so
        # the rule silently did nothing on every negative fixture. Same sidecar
        # idiom as <fixture>.gitfacts.json, and excluded from the read set the
        # same way.
        ov = dict(neg_overlay)
        ovp = os.path.join(path, "overlay.json")
        if os.path.isdir(path) and os.path.isfile(ovp):
            with open(ovp, "r", encoding="utf-8") as fh:
                ov = _deep_merge(ov, json.load(fh))
        ctx = _control_ctx(base, ov, _fixture_paths(path), repo)
        alarms = []
        for rule in RULES:
            if not rule.blocking:
                continue
            res = RuleResult(rule)
            try:
                rule.fn(ctx, res)
            except ArithmeticMismatch as exc:
                alarms.append("%s arithmetic %s" % (rule.rid, exc))
                continue
            except Exception as exc:
                alarms.append("%s %s: %s"
                              % (rule.rid, exc.__class__.__name__, exc))
                continue
            breach = isolation_breach(ctx, res)
            if breach:
                alarms.append("%s ISOLATION BREACH %s"
                              % (rule.rid, ", ".join(breach[:2])))
                continue
            for h in res.adjudicated:
                alarms.append("%s %s %s" % (rule.rid, h.sub, h.text[:90]))
        if alarms:
            rows.append(("-", neg, label,
                         "*** FALSE ALARM *** " + " | ".join(sorted(alarms)[:3])))
            neg_false += 1
        else:
            rows.append(("-", neg, label, "clean"))
            neg_clean += 1

    for sign, cid, fx, verdict in rows:
        out("  canary%s %-18s %-44s %s" % (sign, cid, fx, verdict))
    out("  REPAIR TESTS: %d repaired-clean, %d FIRE ON REPAIRED, %d NOT TESTED "
        "(no repair fixture)" % (rep_clean, rep_fired, rep_absent))

    if "R6b" in opt_in:
        # RULING A, 2026-09-17: a disclosed non-run, NOT a control failure and
        # NOT an abort. Section 6 requires the gate to DISCLOSE the opt-in
        # rather than silently drop it, and disclosure satisfies that;
        # aborting all eleven rules converted a documented flag into a
        # permanent red and denied the operator the other ten rules.
        out("  canary= %-18s %-44s %s"
            % ("R6b-G3", "(opt-in, browser cross-product)",
               "UNAVAILABLE: requires a Chrome binary this gate cannot "
               "assume (spec 6, 7.3). No browser, no outbound request. "
               "Disclosed, not run, not counted as a control."))

    after = mtimes(repo)
    if before != after:
        out("  *** CONTROL PHASE MUTATED public/ *** -- refusing to continue")
        return rows, pos_detected, pos_missed, neg_clean, neg_false, False
    out("  public/ mtimes unchanged across the control phase: %d files verified"
        % len(before))
    out("  CONTROLS: %d positive DETECTED, %d MISSED · %d negative clean, "
        "%d FALSE ALARM" % (pos_detected, pos_missed, neg_clean, neg_false))
    ok = (pos_missed == 0 and neg_false == 0 and rep_fired == 0)
    return rows, pos_detected, pos_missed, neg_clean, neg_false, ok


# ---------------------------------------------------------------------------
# Emit one rule block (spec 4)
# ---------------------------------------------------------------------------

def emit_rule(out, rule, res, raw_label, adj_label, brief):
    out()
    out.head("%s  %s" % (rule.rid, rule.name))
    out("  kind: %s" % rule.kind)
    out("  surfaces: %s   normalization: %s" % (rule.surf, rule.norms))
    out.field("RAW", raw_label, len(res.raw))
    for label, count, removed in res.rows:
        out.field("FILTER", label, count, "    (removed %d)" % len(removed))
    out.field("ADJUDICATED", adj_label, len(res.adjudicated))
    lv = res.levels
    agree = "AGREE" if len(set(lv.values())) <= 1 else "DISAGREE"
    out.field("LEVEL-DISAGREE",
              "RAW=%d DEC=%d TXT=%d" % (lv.get("RAW", 0), lv.get("DEC", 0),
                                        lv.get("TXT", 0)), agree)
    for term, per in res.level_detail:
        out("  %-16s %-46s %s" % ("", "  %r" % term,
                                  "RAW=%d DEC=%d TXT=%d" %
                                  (per["RAW"], per["DEC"], per["TXT"])))
    for d in res.degraded:
        out.field("DEGRADED", d, "")
    for t in sorted(set(res.traps)):
        out("  TRAP: %s" % t)
    for n in res.notes:
        out("  note: %s" % n)
    out.field("VERDICT", res.verdict + " — " + res.reason, "")
    out("  blind spot: %s" % rule.blind_spot)
    if brief:
        out("  --- %d hits --- ENUMERATION SUPPRESSED BY --brief"
            % len(res.adjudicated))
        out("  --- %d items the filters removed --- ENUMERATION SUPPRESSED BY "
            "--brief" % sum(len(r[2]) for r in res.rows))
        return
    out("  --- %d hits, enumerated ---" % len(res.adjudicated))
    if not res.adjudicated:
        out("  (none)")
    for h in sorted(res.adjudicated, key=lambda x: x.sortkey()):
        out(h.line())
    total_removed = sum(len(r[2]) for r in res.rows)
    out("  --- %d items the filters removed, enumerated ---" % total_removed)
    if not total_removed:
        out("  (none)")
    for label, count, removed in res.rows:
        for h in sorted(removed, key=lambda x: x.sortkey()):
            out("  [%s] %s" % (label, h.line().strip()))


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(
        prog="claim_gate.py",
        description="The standing claim gate. Read-only; never edits.")
    p.add_argument("--config", required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--canary", action="store_true",
                   help="run ONLY the control phase and exit with its result")
    p.add_argument("--brief", action="store_true",
                   help="suppress the per-hit enumerations (prints "
                        "ENUMERATION SUPPRESSED BY --brief in their place)")
    p.add_argument("--opt-in", action="append", default=[],
                   metavar="RULE", help="enable an opt-in rule (R6b)")
    p.add_argument("--peer", default=None,
                   help="a second repo for R9's cross-property half")
    p.add_argument("--report", default=None,
                   help="also write the output to this path")
    p.add_argument("--today", default=None,
                   help="override the as-of date (default: config R8.today)")
    return p


def main(argv=None):
    """Wrapper. Any exception that escapes _main becomes a loud exit 2 with a
    report, never an empty stdout and an exit code a CI job will misread."""
    t0 = time.time()
    args = build_parser().parse_args(argv)
    out = Out()
    try:
        return _main(args, out, t0)
    except SystemExit:
        raise
    except BaseException as exc:
        import traceback
        out()
        out("CLAIM GATE CRASHED: %s: %s" % (exc.__class__.__name__, exc))
        for line in traceback.format_exc().splitlines():
            out("  %s" % line)
        out("CLAIM GATE: NOT RUN")
        _finish(out, args, 2, t0)
        return 2


def _main(args, out, t0):

    errs = validate_registry()
    if errs:
        for e in errs:
            out("CONFIG/LOADER ERROR: %s" % e)
        out("CLAIM GATE: NOT RUN")
        _finish(out, args, 2, t0)
        return 2

    try:
        cfg = load_config(args.config)
    except ConfigError as exc:
        out("CONFIG ERROR: %s" % exc)
        out("CLAIM GATE: NOT RUN")
        _finish(out, args, 2, t0)
        return 2

    repo = os.path.abspath(args.repo)
    opt_in = set()
    for o in args.opt_in:
        for part in o.split(","):
            part = part.strip()
            if part:
                if part not in OPT_IN_RULES:
                    out("CONFIG ERROR: unknown --opt-in rule %r (known: %s)"
                        % (part, ", ".join(sorted(OPT_IN_RULES))))
                    _finish(out, args, 2, t0)
                    return 2
                opt_in.add(part)

    if args.today:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.today.strip()):
            out("CONFIG ERROR: --today %r is not an ISO date (YYYY-MM-DD). "
                "R8 compares dates as STRINGS, so an unparseable value would "
                "silently disable the future-date test instead of failing."
                % args.today)
            out("CLAIM GATE: NOT RUN")
            _finish(out, args, 2, t0)
            return 2
        try:
            import datetime as _dt
            _dt.date(*[int(x) for x in args.today.strip().split("-")])
        except ValueError as exc:
            out("CONFIG ERROR: --today %r is not a real calendar date (%s)"
                % (args.today, exc))
            out("CLAIM GATE: NOT RUN")
            _finish(out, args, 2, t0)
            return 2
        cfg.setdefault("R8", {})["today"] = args.today.strip()
        asof_source = "--today"
    else:
        raw_asof = cfg.get("R8", {}).get("today")
        asof_source = ("config R8.today = %r" % raw_asof) if raw_asof \
            else "no R8.today configured"
    # RESOLVE ONCE, HERE, so every downstream reader -- Ctx, rule_R8, every
    # control overlay built off this cfg -- sees an ISO date and never a
    # sentinel. CONFIG ERROR, not a fallback: a bad as-of must stop the gate,
    # because the failure mode of tolerating one is a silently disabled
    # future-date test.
    try:
        cfg.setdefault("R8", {})["today"] = resolve_asof(
            cfg.get("R8", {}).get("today"))
    except ConfigError as exc:
        out("CONFIG ERROR: %s" % exc)
        out("CLAIM GATE: NOT RUN")
        _finish(out, args, 2, t0)
        return 2

    gen = S.read_generators(repo, GEN_MODULES)
    registry = read_citation_registry(repo)

    head = (git(repo, "rev-parse", "--short", "HEAD") or "unknown").strip()
    asof = cfg["R8"]["today"]
    out("CLAIM GATE — %s — %s — HEAD %s — as-of %s (%s)"
        % (cfg["key"], repo, head, asof, asof_source))
    stale = asof_staleness(asof, asof_source)
    if stale:
        out("  *** %s" % stale)

    try:
        corpus = enumerate_corpus(repo, cfg)
    except ConfigError as exc:
        out("CORPUS ERROR: %s" % exc)
        out("CLAIM GATE: NOT RUN")
        _finish(out, args, 2, t0)
        return 2

    out("corpus: git ls-files public/ = %d   find public/ -type f = %d   %s"
        % (len(corpus.ls_files), len(corpus.found),
           "AGREE" if corpus.agree else "DIVERGE"))
    for d in corpus.divergence:
        out("  corpus divergence: %s" % d)
    for lnk in sorted(corpus.escaping_symlinks):
        out("  EXCLUDED, symlink escaping the repo (not this property's "
            "artifact): %s" % lnk)

    # parse once
    ctx = Ctx(cfg["key"], repo, cfg)
    kinds = {"html": 0, "txt": 0, "xml": 0, "svg": 0, "js": 0}
    parse_failures = []
    for rel in corpus.read_set:
        p = os.path.join(repo, rel)
        if not os.path.isfile(p):
            continue
        try:
            art = S.parse_artifact(
                rel, p,
                cfg.get("R1", {}).get("cited_stat_class", "cited-stat"))
        except RecursionError as exc:
            parse_failures.append("%s: RecursionError (%s)" % (rel, exc))
            continue
        except Exception as exc:
            parse_failures.append("%s: %s: %s"
                                  % (rel, exc.__class__.__name__, exc))
            continue
        ctx.artifacts.append(art)
        ctx.by_rel[rel] = art
        kinds[art.kind] = kinds.get(art.kind, 0) + 1
    ctx.gen = gen
    ctx.registry = registry
    ctx.corpus = corpus

    reasons = {}
    for rel, why in corpus.excluded:
        reasons[why] = reasons.get(why, 0) + 1
    out("read set: %d artifacts (%d html, %d txt, %d xml, %d svg)  |  "
        "excluded: %d (%s)"
        % (len(ctx.artifacts), kinds.get("html", 0), kinds.get("txt", 0),
           kinds.get("xml", 0), kinds.get("svg", 0), len(corpus.excluded),
           ", ".join("%s:%d" % (k, reasons[k]) for k in sorted(reasons))))

    if parse_failures:
        out()
        out("PARSE FAILURES: %d artifact(s) could not be parsed and are "
            "therefore OUTSIDE every rule. A corpus the gate cannot read is "
            "not a corpus it has judged." % len(parse_failures))
        for f in sorted(parse_failures):
            out("  %s" % f)
        out("CLAIM GATE: NOT RUN")
        _finish(out, args, 2, t0)
        return 2

    trunc = []
    for art in ctx.artifacts:
        trunc.extend("%s %s" % (art.rel, x) for x in art.ld_truncated)
    if trunc:
        out("JSON-LD TRUNCATED (depth or leaf cap hit -- stated, never "
            "silent): %d block(s)" % len(trunc))
        for t in sorted(trunc)[:10]:
            out("  %s" % t)

    for mod in sorted(gen.src_runs):
        a = S.src_artifact(mod, gen.src_runs[mod])
        if a.surfaces:
            ctx.src_artifacts.append(a)
            ctx.by_rel[a.rel] = a

    build_claim_set(ctx)
    n_prop, n_cite, n_const, n_asset = ctx.claim_counts
    out("claim set: %d propositions resolved from %d cited-stat blocks, %d "
        "shared constants, %d referenced assets"
        % (n_prop, n_cite, n_const, n_asset))
    # A cited-stat block the gate cannot bind to a registry key is REPORTED.
    # It used to be bound to the alphabetically first key sharing its URL, and
    # that key's `stat` was then spliced onto the page as a synthetic CITE
    # surface which every proposition rule read as though the page contained
    # it. Nine DCI R5 findings quoted a sentence absent from the file they
    # named. Splicing nothing is a smaller error than splicing the wrong thing,
    # but it is still an error, so it is stated rather than absorbed.
    if ctx.unresolved_cited_stats:
        out("UNRESOLVED CITED-STAT BLOCKS: %d. Each names a URL owned by two "
            "or more CITED_SOURCES keys and carries a label matching none of "
            "them, so NO registry text was spliced onto the artifact. Its "
            "claims are judged from the page's own bytes only."
            % len(ctx.unresolved_cited_stats))
        for rel, url, label, cands in sorted(set(ctx.unresolved_cited_stats)):
            out("  %s  label=%r  url=%s  candidates=%s"
                % (rel, label[:70], url[:90], ",".join(cands)))
    if not registry.present:
        out("citation registry: %s ABSENT -- R7 runs from its config list "
            "only and says so" % REGISTRY_REL)
    elif registry.parse_error:
        out("citation registry: %s UNPARSEABLE (%s) -- R7 runs from its "
            "config list only and says so"
            % (REGISTRY_REL, registry.parse_error))
    else:
        out("citation registry: %s -- %d entries, supersession %s, %d "
            "superseded_by record(s) READ BY R7"
            % (REGISTRY_REL, registry.entries,
               ("DECLARED %s" % registry.declared_on) if registry.declared
               else "NOT DECLARED (R7 DEGRADED)",
               len(registry.superseded)))
    n_scanned, unfirable = unfirable_patterns(cfg)
    out("SENTENCE-SCOPED CONFIG PATTERNS: %d scanned, %d UNFIRABLE (a pattern "
        "the sentence splitter cuts in two can never match, so the rule "
        "configured on it silently does not exist)"
        % (n_scanned, len(unfirable)))
    if unfirable:
        for path, pat, pieces in unfirable:
            out("  UNFIRABLE  %s  %r" % (path, pat))
            out("             splits into %r" % (pieces,))
        out("CLAIM GATE: NOT RUN")
        _finish(out, args, 2, t0)
        return 2
    owed, noted, thin, empties, ambiguous = unread_config_keys(cfg)
    out("CONFIG KEYS READ BY NO CODE PATH: %d OWED, %d declared "
        "documentation-only WITH a justification. An OWED key is a rule that "
        "silently does not exist (Rule 2: wire it up or delete it).%s%s"
        % (len(owed), len(noted),
           ("  OWED: " + ", ".join(owed)) if owed else "",
           ("  DECLARED WITHOUT A JUSTIFICATION (not counted as declared): "
            + ", ".join(thin)) if thin else ""))
    if empties:
        out("CONFIG KEYS READ BY CODE BUT EMPTY: %d. The rule each configures "
            "cannot fire on a value it does not have -- emptying a live list "
            "leaves the OWED audit green while the rule goes blind. Stated, "
            "not failed: an empty list is sometimes a deliberate null result. "
            "%s" % (len(empties), ", ".join(empties)))
    if ambiguous:
        out("DOCUMENTATION-ONLY DECLARATIONS THAT ARE AMBIGUOUS: %d. A bare "
            "leaf name covers a key only when exactly one unread key carries "
            "it; these cover several, so the full dotted path must be written "
            "or the keys stay OWED. %s" % (len(ambiguous),
                                           ", ".join(ambiguous)))
    sr = sorted(cfg.get("src_rules", []) or [])
    out("normalization levels compared: RAW DEC TXT   (+ SRC over %d "
        "generator modules, %d string runs >=12 chars, READ BY: %s)"
        % (len(gen.modules),
           sum(len(a.surfaces) for a in ctx.src_artifacts),
           ", ".join(sr) if sr else "NO RULE -- SRC is computed and unused"))
    # STATED, NEVER SILENT, AND NEVER A DELETION. These runs STAY in the
    # proposition pool; each rule raises its hits against them and then removes
    # them through its own named, counted, enumerated filter, so a reader can
    # see WHICH RULE dropped WHAT. The quoted string literals inside each run
    # are judged separately under a #strN locator and are NOT excluded.
    for a in ctx.src_artifacts:
        ctx.pool(a)
    if ctx.src_code_surfaces:
        tot = sum(n for _, _, n in ctx.src_code_surfaces)
        lits = sum(len(_src_code_literals(
            next(x.text for x in ctx.by_rel[rel].surfaces
                 if x.locator == loc)))
            for rel, loc, _ in ctx.src_code_surfaces)
        out("SRC CODE SURFACES (stylesheet or script BODY): %d run(s), %d "
            "chars, %d quoted string literal(s) lifted out of them and judged "
            "separately. The runs are NOT dropped from the pool -- each rule "
            "raises and then removes them through its own named filter. %s"
            % (len(ctx.src_code_surfaces), tot, lits,
               ", ".join("%s(%d)" % (loc, n) for _, loc, n
                         in sorted(ctx.src_code_surfaces))))
    else:
        out("SRC CODE SURFACES (stylesheet or script BODY): 0 -- NULL RESULT, "
            "no generator string run on this property is a stylesheet or a "
            "script body")
    out("KNOWN HOLES, stated up front (spec 7): og-image RASTERS are not read "
        "(%s); no PDF text extraction; no JS execution outside opt-in R6b; no "
        "outbound request, so a live/repo divergence is invisible here; "
        "index.js / operator email bodies / the leads table are out of scope."
        % ("TOTAL on this property -- og-image.png has no SVG sibling"
           if cfg.get("og_image_raster_only") else
           "the SVG or .mvg source is read instead"))
    if cfg.get("embed_artifacts"):
        present = [e for e in cfg["embed_artifacts"] if e in ctx.by_rel]
        out("embed frame: %s  |  IN THE READ SET: %d of %d%s"
            % (", ".join(cfg["embed_artifacts"]), len(present),
               len(cfg["embed_artifacts"]),
               "" if len(present) == len(cfg["embed_artifacts"])
               else "  *** an embed artifact named in the config is NOT in "
                    "public/ ***"))
    else:
        out("embed frame: %s" % cfg.get(
            "embed_artifacts_note",
            "NULL RESULT -- this property has no embed artifact."))

    exit_code = 0
    out()
    out.head("CONTROLS (run BEFORE any rule; see spec 5)")
    ctx.gitfacts.load(repo, corpus.read_set)
    rows, pd, pm, nc, nf, cok = run_controls(out, cfg, repo, opt_in, gen,
                                             registry)
    if not cok:
        out()
        out("CLAIM GATE: NOT RUN — a rule that cannot detect its own "
            "defect is worse than no rule, because it manufactures confidence.")
        _finish(out, args, 2, t0)
        return 2

    # THE ZERO-ARTIFACT TRAP RUNS BEFORE THE --canary RETURN. It used to sit
    # after it, so a green canary was available on a gutted property -- and the
    # README tells a new-property operator to run --canary as onboarding step 3.
    n_all = len(ctx.artifacts) + len(corpus.excluded)
    n_html = kinds.get("html", 0)
    want_html = int(cfg.get("expected_html") or 0)
    trap = []
    if n_all < int(cfg["min_artifacts"]):
        trap.append("corpus is %d artifacts, config min_artifacts is %d"
                    % (n_all, cfg["min_artifacts"]))
    if want_html and n_html < want_html:
        # expected_html was REQUIRED PRESENT and COMPARED TO NOTHING, so a
        # property with 1 of 38 html pages plus 51 junk .txt files passed
        # min_artifacts and exited 0. Pages, not artifacts.
        trap.append("read %d html page(s), config expected_html is %d"
                    % (n_html, want_html))
    if trap:
        out()
        out("ZERO-ARTIFACT TRAP: %s. An empty or truncated corpus passes every "
            "check trivially; that is correct behaviour for a gate and is NOT "
            "evidence the gate works." % "; ".join(trap))
        out("CLAIM GATE: NOT RUN")
        _finish(out, args, 2, t0)
        return 2
    if want_html and n_html > want_html:
        out("  note: read %d html page(s) where config expected_html is %d -- "
            "pages were ADDED since the config was measured; the config is "
            "stale, not the corpus" % (n_html, want_html))

    if args.canary:
        out()
        out("CLAIM GATE: CANARY OK — control phase only, no rule ran "
            "against %s" % repo)
        _finish(out, args, 0, t0)
        return 0
    if not corpus.agree:
        out()
        out("CORPUS DIVERGENCE is itself a finding: git ls-files and the "
            "working tree disagree. The gate will not judge a corpus it "
            "cannot enumerate twice the same way.")
        out("CLAIM GATE: NOT RUN")
        _finish(out, args, 2, t0)
        return 2

    if args.peer:
        peer_repo = os.path.abspath(args.peer)
        if not os.path.isdir(os.path.join(peer_repo, "public")):
            out()
            out("CONFIG ERROR: --peer %r has no public/ directory. The flag "
                "used to be accepted, validated nowhere, wired to nothing, and "
                "its only effect was to DELETE the line disclosing that R9's "
                "cross-property half had not run." % args.peer)
            out("CLAIM GATE: NOT RUN")
            _finish(out, args, 2, t0)
            return 2
        try:
            pcorpus = enumerate_corpus(peer_repo, cfg)
        except ConfigError as exc:
            out("CONFIG ERROR: --peer %r: %s" % (args.peer, exc))
            out("CLAIM GATE: NOT RUN")
            _finish(out, args, 2, t0)
            return 2
        pctx = Ctx(os.path.basename(peer_repo), peer_repo, cfg)
        for rel in pcorpus.read_set:
            pp = os.path.join(peer_repo, rel)
            if not os.path.isfile(pp):
                continue
            try:
                pctx.artifacts.append(S.parse_artifact(rel, pp))
            except Exception:
                continue
            pctx.by_rel[rel] = pctx.artifacts[-1]
        pctx.gen = S.GeneratorFacts()
        build_claim_set(pctx)
        ctx.peer_ctx = pctx
        out("peer corpus for R9's cross-property half: %s -- %d artifact(s) "
            "read" % (peer_repo, len(pctx.artifacts)))

    summary = []
    blocking_fail = []
    report_only = []
    report_only_counts = []
    for rule in RULES:
        res = RuleResult(rule)
        try:
            raw_label, adj_label = rule.fn(ctx, res)
        except ArithmeticMismatch as exc:
            out()
            out.head("%s  %s" % (rule.rid, rule.name))
            out("  FILTER ARITHMETIC MISMATCH: %s" % exc)
            out("  subtraction is not measurement. The gate exits 2.")
            out()
            out("CLAIM GATE: NOT RUN")
            _finish(out, args, 2, t0)
            return 2
        except Exception as exc:
            import traceback
            out()
            out.head("%s  %s" % (rule.rid, rule.name))
            out("  RULE CRASHED: %s: %s" % (exc.__class__.__name__, exc))
            for line in traceback.format_exc().splitlines():
                out("    %s" % line)
            out("  A crashed rule has judged NOTHING. The gate exits 2 rather "
                "than 0 or 1, because a rule that did not run must never be "
                "reported as a rule that passed.")
            out()
            out("CLAIM GATE: NOT RUN")
            _finish(out, args, 2, t0)
            return 2
        embeds_set = set(cfg.get("embed_artifacts", []) or [])
        for h in list(res.raw) + list(res.adjudicated):
            if h.rel in embeds_set:
                h.on_embed = True
        n = len(res.adjudicated)
        blocking = rule.blocking
        if rule.rid == "R11":
            # config.R11.blocking was dead: the implementation hardcoded
            # non-blocking. It is now READ, so a property that decides to block
            # on attribution debt can say so in its own config.
            blocking = bool(cfg.get("R11", {}).get("blocking", False))
        # FALSE-POSITIVE DEMOTION. A rule measured above the configured
        # threshold stops affecting the exit code and CARRIES ITS MEASURED RATE
        # IN ITS OWN OUTPUT. Standing ruling: a rule at 68% false positives
        # will be ignored by every future session, and a rule that is ignored
        # while still red manufactures the appearance of coverage. The
        # measurement is data, so it lives in config and is re-taken, not
        # remembered.
        demo = (cfg.get("false_positive_measurements", {}) or {}).get(rule.rid)
        demoted = False
        if demo and blocking:
            rate = float(demo.get("fp_rate_pct", 0))
            thr = float((cfg.get("false_positive_measurements", {}) or {})
                        .get("demote_above_pct", 25))
            if rate > thr:
                blocking = False
                demoted = True
                res.notes.append(
                    "REPORT-ONLY BY MEASUREMENT: %.1f%% false positives, above "
                    "the %.0f%% threshold. Measured %s at canon %s, "
                    "EXHAUSTIVELY -- %d finding(s) examined across the "
                    "portfolio, %d TRUE, %d FALSE POSITIVE, %d REVIEW. %s"
                    % (rate, thr, demo.get("measured_on", "?"),
                       demo.get("measured_at_canon", "?"),
                       demo.get("examined", 0), demo.get("true", 0),
                       demo.get("false_positive", 0), demo.get("review", 0),
                       demo.get("note", "")))
                if demo.get("per_property"):
                    res.notes.append("  per property: %s"
                                     % demo["per_property"])
                for cls in demo.get("false_positive_classes", []) or []:
                    res.notes.append("  FP class: %s" % cls)
                for cls in demo.get("review_classes", []) or []:
                    res.notes.append("  REVIEW class: %s" % cls)
        if not blocking:
            res.verdict = "REPORT"
            res.reason = (
                ("%d finding(s) reported; REPORT-ONLY by measurement "
                 "(%.1f%% false positives); never changes the exit code"
                 % (n, float(demo.get("fp_rate_pct", 0))))
                if demoted else
                ("%d tracked-term row(s) reported; never changes the "
                 "exit code" % n))
            report_only.append(rule.rid)
            report_only_counts.append((rule.rid, n))
        elif n:
            res.verdict = "FAIL"
            res.reason = "%d adjudicated finding(s) stand after %d filter(s)" \
                % (n, len(res.rows))
            blocking_fail.append(rule.rid)
        else:
            res.verdict = "PASS"
            res.reason = ("0 adjudicated findings from %d raw match(es) across "
                          "%d filter(s)" % (len(res.raw), len(res.rows)))
        emit_rule(out, rule, res, raw_label, adj_label, args.brief)
        summary.append((rule.rid, rule.name, len(res.raw), n, res.verdict))

    out()
    out.head("SUMMARY")
    for rid, name, raw, adj, verdict in summary:
        tail = " (non-blocking)" if verdict == "REPORT" else ""
        out("  %-4s%-32s RAW %-6d ADJ %-6d %s%s"
            % (rid, name, raw, adj, verdict, tail))
    if "R6b" not in opt_in:
        out("  OPT-IN NOT RUN: R6b (%s). Run with --opt-in=R6b."
            % OPT_IN_RULES["R6b"])
    else:
        out("  OPT-IN REQUESTED BUT UNAVAILABLE: R6b (%s) requires a Chrome "
            "binary this gate cannot assume (spec 6, 7.3). The other ten "
            "blocking rules DID run and their verdicts above stand."
            % OPT_IN_RULES["R6b"])
    if not args.peer:
        out("  R9 CROSS-PROPERTY HALF SKIPPED: no --peer given")
    else:
        out("  R9 CROSS-PROPERTY HALF RAN against %s" % os.path.abspath(args.peer))
    out("  blocking failures: %d%s"
        % (len(blocking_fail),
           (" (" + ", ".join(blocking_fail) + ")") if blocking_fail else ""))
    out("  report-only findings: %d%s"
        % (len(report_only),
           (" (" + ", ".join(report_only) + ")") if report_only else ""))
    # WHAT REPORT-ONLY STATUS REMOVED FROM THE BLOCKING SET.
    #
    # R3's demotion on its measured 68.1% false-positive rate took 123 DCI
    # findings and 20 of the 86 adversarial vectors out of the blocking set in
    # one commit. 17 of those 20 are still DETECTED -- and every one of them now
    # exits 0. That is defensible (the measurement stands) and it must not be
    # INVISIBLE: a green exit that means "the rule found things and none of them
    # count" must not read the same as "nothing was found". The rebate-dollar
    # class produced 545 live instances and the owner's ban; a reader deciding
    # whether to ship needs to see that it can no longer stop a release alone.
    demoted_rows = [(rid, n) for rid, n in report_only_counts if n]
    if demoted_rows:
        out("  WHAT REPORT-ONLY STATUS REMOVED FROM THE BLOCKING SET: %d "
            "finding(s) across %d rule(s) were DETECTED and do NOT affect the "
            "exit code -- %s. A green exit here does not mean nothing was "
            "found; it means nothing that was found is allowed to block."
            % (sum(n for _, n in demoted_rows), len(demoted_rows),
               ", ".join("%s %d" % (rid, n) for rid, n in demoted_rows)))
    elif report_only:
        out("  report-only rules found nothing this run: %s"
            % ", ".join(report_only))
    out("  opt-in rules not run: 1 (R6b -- %s)"
        % ("requested, UNAVAILABLE, disclosed" if "R6b" in opt_in
           else "not requested"))
    exit_code = 1 if blocking_fail else 0
    out("CLAIM GATE: %s" % ("FAIL" if exit_code else "PASS"))
    _finish(out, args, exit_code, t0)
    return exit_code


def _finish(out, args, code, t0):
    text = out.text()
    sys.stdout.write(text)
    if args.report:
        d = os.path.dirname(os.path.abspath(args.report))
        if d and not os.path.isdir(d):
            os.makedirs(d)
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write(text)
    sys.stderr.write("claim_gate: %.2fs, exit %d\n" % (time.time() - t0, code))


if __name__ == "__main__":
    sys.exit(main())
