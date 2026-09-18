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
           "derivable_constants"),
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
    try:
        with open(os.path.abspath(__file__), "r", encoding="utf-8") as fh:
            impl = fh.read()
        with open(os.path.join(_HERE, "surfaces.py"), "r",
                  encoding="utf-8") as fh:
            impl += fh.read()
    except OSError:
        return []
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
            "superseded_propositions", "tracked_terms", "anomalies",
            "deliberate_divergence", "deliberate_edition_divergence",
            "tools", "draft_gate", "known_uncited", "hedge_pairs",
            "documentation_only_keys")
    unread = []

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
                if ('"%s"' % k) not in impl and ("'%s'" % k) not in impl:
                    unread.append(full)
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
    owed = sorted(set(u for u in unread
                      if u not in good and u.split(".")[-1] not in good))
    noted = sorted(set(u for u in unread
                       if u in good or u.split(".")[-1] in good))
    return owed, noted, thin


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
        self.gitfacts = GitFacts()
        self.claim_extra = {}
        self.corpus = None
        self.today = cfg.get("R8", {}).get("today", "2026-09-17")
        self._script_spans = {}
        self._svg_text = {}
        self._pool = {}
        self._levels_cache = {}
        self.src_artifacts = []
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
        probe = S.collapse(hit.sentence)[:48]
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
            for sent in S.sentences(art.txt):
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
            for sent in (S.sentences(s.text) or [s.text]):
                out.append((s.key, s.locator, sent))
        self._pool[art.rel] = out
        return out

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
        best = None
        for k in sorted(self.gen.cited_sources):
            e = self.gen.cited_sources[k]
            url = e.get("url")
            if not isinstance(url, str) or url != cs["url"]:
                continue
            label = S.collapse(str(e.get("determiner") or "") +
                               str(e.get("source") or ""))
            if label and cs["label"] and S.collapse(cs["label"]) == label:
                return k
            best = best or k
        return best

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
        for skey, loc, sent in ctx.pool(art):
            for m in qre.finditer(sent):
                pre = sent[max(0, m.start() - 40):m.start()]
                v = which_any(pre, verbs, ci=True, word=False)
                if not v:
                    continue
                raw.append(Hit("R1", "B", art.rel, skey, str(loc),
                               win(sent, m.start(), 110), note=v[0],
                               sentence=sent))

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
                for cs in S.sentences(art.txt):
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

    def f_restr_elsewhere(h):
        return h.note == "restriction-elsewhere-on-page"

    def f_corrective(h):
        return not getattr(h, "r2_subject_ok", True)

    res.raw = raw
    res.adjudicated, res.rows = adjudicate(raw, [
        Filt("generator SRC restatement of prose that already renders in public/ (counted once, against the rendered artifact)", f_srcdup),
        Filt("split disclosure -- two or more utilities AND two or more towns "
             "in one sentence, where nearest-binding is decided by word order "
             "rather than meaning: REVIEW, never FAIL", f_split),
        Filt("sitewide artifact, no town named in the clause -- the utility "
             "serves somewhere in this territory, so nothing is asserted "
             "against a town (raised and enumerated, never dropped silently)",
             f_sitewide),
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
_T2_PRINTCODE = re.compile(r"\b\d{2}-\d{2}-\d{3}\b|\b\d{2}-\d{4}\b"
                           r"|\bPublic Law \d+-\d+\b|\b\d{2}-\d{4}\s*\("
                           r"\d{2}-\d{2}\)")
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
    for art in ctx.rule_artifacts("R4"):
        prev = []
        for skey, loc, sent in ctx.pool(art):
            tk = which_any(sent, toks, word=False)
            if not tk:
                prev = (prev + [(skey, ctx.programs_in(sent),
                                 which_any(sent, setanaph, word=False))])[-2:]
                continue
            named = ctx.programs_in(sent)
            # ANAPHORA. "The Whole Home Efficiency Bonus is worth having. It
            # layers on top of the standard rebate." names one program in the
            # first sentence and makes the claim in the second. Program names
            # from the previous two sentences OF THE SAME SURFACE carry
            # forward, marked so the enumeration says where they came from.
            carried = []
            carried_anaph = []
            for pk, pn, pa in prev:
                if pk == skey:
                    carried += pn
                    carried_anaph += pa
            anaph = sorted(set(which_any(sent, setanaph, word=False))
                           | set(carried_anaph))
            prev = (prev + [(skey, named,
                             which_any(sent, setanaph, word=False))])[-2:]
            allnamed = sorted(set(named) | set(carried))
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
            if cls in ("ASSERTS", "DENIES") and exc.get("allowed", True) \
                    and (pub or not need_pub) \
                    and (art.cite_keys or not need_key):
                cls = "ATTRIBUTED-AND-SOURCED"
            raw.append(Hit("R4", cls, art.rel, skey, str(loc),
                           "%s | programs=%s%s%s | %s"
                           % (",".join(tk), ",".join(allnamed) or "-",
                              (" (carried from the previous sentence: %s)"
                               % ",".join(sorted(set(carried) - set(named))))
                              if set(carried) - set(named) else "",
                              (" (program SET named anaphorically, not by "
                               "name: %s)" % ",".join(anaph)) if anaph else "",
                              sent),
                           note=cls, sentence=sent))

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
    res.notes.append("ASSERTS %d  ·  DENIES %d  ·  ASSERTS-1P %d  ·  "
                     "DENIES-1P %d  ·  ASSERTS-SET %d  ·  DENIES-SET %d  ·  "
                     "all six FAIL: silence is the compliant state and "
                     "affirmative denial is equally a defect"
                     % (n("ASSERTS"), n("DENIES"), n("ASSERTS-1P"),
                        n("DENIES-1P"), n("ASSERTS-SET"), n("DENIES-SET")))
    res.notes.append("-SET classes are claims whose programs are named "
                     "ANAPHORICALLY -- 'either insulation rebate program', "
                     "'both rebate programs' -- so the phrase supplies the "
                     "COUNT and never a name. Reported as their own sub-tests "
                     "because that is a loosening, and a loosening that hides "
                     "inside an existing class cannot be controlled or "
                     "measured.")
    return "stacking tokens resolved to sentences", \
           "sentences that assert or deny that programs combine"


R5_KEYS = (S.S_VIS, S.S_TITLE, S.S_META, S.S_OG, S.S_TW, S.S_LD, S.S_JS,
           S.S_LOWVIS, S.S_LLMS, S.S_SVGTEXT)


def rule_R5(ctx, res):
    c = ctx.r("R5")
    pats = [re.compile(p) for p in (c.get("magnitude_patterns") or [])]
    words = c.get("magnitude_words", []) or []
    pubs = c.get("recognised_publishers", []) or []
    attrib_verbs = ctx.r("R1").get("attribution_verbs", []) or []
    computed = c.get("computed_output_markers", []) or []
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

    _STOP = frozenset((
        "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "is",
        "are", "was", "were", "be", "by", "with", "that", "this", "it", "as",
        "at", "from", "your", "you", "we", "our", "can", "will", "not", "but",
        "than", "then", "so", "if", "most", "more", "up"))

    def f_instat(h):
        # A numeral SUBSTRING present in ANY cited-stat on the page cleared the
        # hit page-wide. That is how DCI's live uncited "15% reduction in
        # heating and cooling costs" was nearly cleared by an UNRELATED ENERGY
        # STAR 15% on the same page. The figure must now share at least FIVE
        # content words with the stat that is supposed to attribute it. Three
        # was still too loose: "see a 15% reduction in heating and cooling
        # costs" and "save an average of 15% on heating and cooling costs"
        # share exactly heating/cooling/costs and are different claims.
        if not getattr(h, "r5_instat", False):
            return False
        sw = set(w for w in re.findall(r"[a-z]{3,}", h.sentence.lower())
                 if w not in _STOP)
        for st in getattr(h, "r5_stats", []) or []:
            tw = set(w for w in re.findall(r"[a-z]{3,}", st.lower())
                     if w not in _STOP)
            if len(sw & tw) >= 5:
                return True
        return False

    def f_pub(h):
        # A publisher named ANYWHERE in the sentence used to exempt it. That
        # removed the only two 25-40% rows on one page because "Xcel Energy"
        # appears there as the PAYER, not as the publisher of the figure. An
        # attribution needs an attribution VERB and the publisher near the
        # figure -- not merely an organisation's name somewhere in the clause.
        if not has_any(h.sentence, pubs, ci=True):
            return False
        if not has_any(h.sentence, attrib_verbs, word=False):
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

    res.raw = raw
    res.adjudicated, res.rows = adjudicate(raw, [
        Filt("generator SRC restatement of prose that already renders in "
             "public/ (counted once, against the rendered artifact)",
             _open(f_srcdup)),
        Filt("the sentence IS a cited-stat block (attributed by construction)",
             _open(f_inblock)),
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

    def f_srcdup(h):
        return ctx.src_dup(h)

    def f_corr(h):
        return has_any(h.sentence, marks, word=False)

    def f_never403(h):
        return has_any(h.sentence, c.get("never_retire_on_403", []) or [],
                       word=False)

    res.raw = raw
    res.adjudicated, res.rows = adjudicate(raw, [
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


def rule_R8(ctx, res):
    c = ctx.r("R8")
    today = c.get("today", ctx.today)
    exempt = set(c.get("exempt_pages", []) or [])
    own = set(c.get("own_effective_date_pages", []) or [])
    pinned = c.get("pinned_pages", {}) or {}
    holds = c.get("known_holds", []) or []
    hold_note = holds[0].get("report_as") if holds else ""

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
        claimed = [(k, v) for k, v in sorted(dates.items())
                   if k != "ld:datePublished"]
        # (b) after today
        for k, v in claimed:
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
            for k, v in claimed:
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
        missing = [h for h in hidden if h not in art.ids]
        if missing and vis_ids and vis_ids[0] in art.ids:
            raw.append(Hit("R9", "N3", art.rel, "JS", art.rel,
                           "tool payload field(s) %s not found in the page; "
                           "visible/hidden agreement cannot be established"
                           % missing, note="N3-unverifiable", sentence=art.rel))
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
# The N3b control pins its own tool entry, so the comparison it proves does not
# depend on which property's R9.tools happens to be loaded -- LGM and GCI
# configure no tool at all.
R9_N3B_CONTROL_OVERLAY = {"R9": {"tools": [{
    "page": "R9_hidden_payload_contradiction.html",
    "visible": "#calcOutput",
    "hidden": ["lf-calc-inputs", "lf-calc-output"],
    "hidden_mirrors_visible": ["lf-calc-output"]}]}}
R5_CONTROL_OVERLAY = {"R3": {"allowed_thresholds": [],
                             "allowed_structure_percentages": []}}
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
                     repaired=_f("repaired", "R2d_inverted_split_fact.html"))]),

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
                                 "R4d_anaphoric_program_set.html"))]),

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
                           R5_CONTROL_OVERLAY, sub="mag", repaired=_f("repaired", "R5_uncited_statistic.html"))]),

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
             Control("R7-REG", "R7", _f("R7_registry_supersession.html"),
                     overlay=R7_REGISTRY_CONTROL_OVERLAY, sub="A-reg",
                     repaired=_f("repaired",
                                 "R7_registry_supersession.html"))]),

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
         "it reports and never blocks; it cannot tell whether a claim is true "
         "(all five tracked DCI terms are accurate to 25-12-215) nor whether "
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

NEGATIVES = ["NEG%02d" % i for i in range(1, 15)]
# The reference date the negative fixtures were written against. Fixed on
# purpose: see the neg_overlay comment in run_controls().
NEG_ASOF = "2026-09-17"


def _fixture_paths(p):
    if os.path.isdir(p):
        out = []
        for root, dirs, files in os.walk(p):
            dirs.sort()
            for f in sorted(files):
                if f.endswith(".gitfacts.json"):
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
    ctx.gen = base_cfg.get("_gen") or S.GeneratorFacts()
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
    base["_gen"] = gen
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
        path = os.path.join(FIXTURES, "negative", neg + ".html")
        ctx = _control_ctx(base, neg_overlay, _fixture_paths(path), repo)
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
            rows.append(("-", neg, "fixtures/negative/%s.html" % neg,
                         "*** FALSE ALARM *** " + " | ".join(sorted(alarms)[:3])))
            neg_false += 1
        else:
            rows.append(("-", neg, "fixtures/negative/%s.html" % neg, "clean"))
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

    gen = S.read_generators(repo, GEN_MODULES)
    registry = read_citation_registry(repo)

    head = (git(repo, "rev-parse", "--short", "HEAD") or "unknown").strip()
    asof = cfg.get("R8", {}).get("today", "2026-09-17")
    out("CLAIM GATE — %s — %s — HEAD %s — as-of %s"
        % (cfg["key"], repo, head, asof))

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
    owed, noted, thin = unread_config_keys(cfg)
    out("CONFIG KEYS READ BY NO CODE PATH: %d OWED, %d declared "
        "documentation-only WITH a justification. An OWED key is a rule that "
        "silently does not exist (Rule 2: wire it up or delete it).%s%s"
        % (len(owed), len(noted),
           ("  OWED: " + ", ".join(owed)) if owed else "",
           ("  DECLARED WITHOUT A JUSTIFICATION (not counted as declared): "
            + ", ".join(thin)) if thin else ""))
    sr = sorted(cfg.get("src_rules", []) or [])
    out("normalization levels compared: RAW DEC TXT   (+ SRC over %d "
        "generator modules, %d string runs >=12 chars, READ BY: %s)"
        % (len(gen.modules),
           sum(len(a.surfaces) for a in ctx.src_artifacts),
           ", ".join(sr) if sr else "NO RULE -- SRC is computed and unused"))
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
        if not blocking:
            res.verdict = "REPORT"
            res.reason = ("%d tracked-term row(s) reported; never changes the "
                          "exit code" % n)
            report_only.append(rule.rid)
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
