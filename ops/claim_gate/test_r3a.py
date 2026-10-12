# K45 R2: tests for the claim gate R3 split (R3a blocking / R3b report-only).
# Stdlib unittest only. Every test builds its own tiny git-committed site in a
# tempfile dir (removed on cleanup); nothing outside this repo is read at run
# time except python3 and git. Run:
#   PYTHONDONTWRITEBYTECODE=1 python3 -m unittest ops/claim_gate/test_r3a.py -v
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "claim_gate.py")
BASE_CONFIG = os.path.join(HERE, "config", "dci.json")
CHECKS = os.path.join(os.path.dirname(HERE), "checks")
RUNNER = os.path.join(CHECKS, "run_checks.py")

sys.path.insert(0, CHECKS)
import checklib  # noqa: E402

PLANT = "Xcel pays a $500 rebate for attic insulation."

# A one-page site that passes every non-R3a blocking rule under the dci config
# (measured: R1 R2 R4-R10 PASS, R3b/R11 report-only), so the gate's exit code
# is attributable to R3a alone.
PAGE = """<!DOCTYPE html>
<html lang="en"><head><title>Attic Insulation</title>
<meta name="description" content="Attic insulation in Longmont.">
</head><body><main>
<h1>Attic insulation</h1>
{body}
<p>We insulate attics in Longmont.</p>
</main></body></html>
"""

CONFIG = {"extends": BASE_CONFIG, "min_artifacts": 1, "expected_html": 1,
          "R6": {"label_chains": []}}

GIT = ["git", "-c", "init.defaultBranch=main", "-c", "core.hooksPath=/dev/null",
       "-c", "commit.gpgsign=false", "-c", "user.name=k45", "-c",
       "user.email=k45@localhost"]

ABSENT = object()


def entry(sentence, reason="fixture reason", ruling="fixture ruling"):
    e = {"sentence": sentence}
    if reason is not None:
        e["reason"] = reason
    if ruling is not None:
        e["ruling"] = ruling
    return e


def make_site(root, paragraphs, allowlist=ABSENT, programs=ABSENT):
    """root/site: public/index.html + optional ops/r3a_*.json, git-committed
    (the gate requires `git ls-files public/` to match the tree)."""
    site = os.path.join(root, "site")
    os.makedirs(os.path.join(site, "public"))
    body = "\n".join("<p>%s</p>" % p for p in paragraphs)
    with open(os.path.join(site, "public", "index.html"), "w") as fh:
        fh.write(PAGE.format(body=body))
    for rel, val in (("r3a_allowlist.json", allowlist),
                     ("r3a_programs.json", programs)):
        if val is ABSENT:
            continue
        os.makedirs(os.path.join(site, "ops"), exist_ok=True)
        with open(os.path.join(site, "ops", rel), "w") as fh:
            fh.write(val if isinstance(val, str) else json.dumps(val))
    for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "x"]):
        subprocess.run(GIT + cmd, cwd=site, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return site


def write_config(root):
    p = os.path.join(root, "config.json")
    with open(p, "w") as fh:
        json.dump(CONFIG, fh)
    return p


def section(out, rid):
    """Lines of the gate's '━━━ <rid>  ...' section, up to the next '━━━'."""
    lines = out.splitlines()
    for i, l in enumerate(lines):
        if l.startswith("━━━ %s " % rid):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("━━━"):
                j += 1
            return lines[i:j]
    raise AssertionError("no %s section in gate output" % rid)


def enumerated(sec):
    """(hits, removed): hit lines of a section's two enumerations."""
    hits, removed, cur = [], [], None
    for l in sec:
        if re.match(r"^\s+--- \d+ hits?, enumerated ---", l):
            cur = hits
        elif re.match(r"^\s+--- \d+ items? the filters removed", l):
            cur = removed
        elif cur is not None and "public/" in l:
            cur.append(l)
    return hits, removed


def summary_row(out, rid):
    m = re.search(r"^\s+%s\s+.+?RAW\s+(\d+)\s+ADJ\s+(\d+)\s+(.+?)\s*$" % rid,
                  out.split("━━━ SUMMARY ━━━")[-1], re.M)
    if not m:
        raise AssertionError("no SUMMARY row for %s" % rid)
    return int(m.group(1)), int(m.group(2)), m.group(3)


class GateCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="k45_r3a_")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.cfg = write_config(self.tmp)
        self.n = 0

    def gate(self, paragraphs, **kw):
        self.n += 1
        root = os.path.join(self.tmp, "case%d" % self.n)
        os.makedirs(root)
        site = make_site(root, paragraphs, **kw)
        p = subprocess.run([sys.executable, GATE, "--config", self.cfg,
                            "--repo", site], cwd=root, capture_output=True,
                           text=True, timeout=300)
        return p.returncode, p.stdout + p.stderr

    def assertOnlyR3aBlocks(self, out):
        m = re.search(r"blocking failures: (\d+) \(([^)]*)\)", out)
        self.assertIsNotNone(m, "no 'blocking failures' line")
        self.assertEqual(m.group(2).strip(), "R3a")

    def assertR3aFails(self, rc, out):
        self.assertEqual(rc, 1, out[-1500:])
        self.assertEqual(summary_row(out, "R3a")[2], "FAIL")
        self.assertOnlyR3aBlocks(out)
        self.assertIn("CLAIM GATE: FAIL", out)

    def assertR3aClean(self, rc, out):
        self.assertEqual(rc, 0, out[-1500:])
        _raw, adj, verdict = summary_row(out, "R3a")
        self.assertEqual(adj, 0)
        self.assertEqual(verdict, "PASS")


class TestPositives(GateCase):
    # (a)
    def test_a_program_rebate_dollar_plant_fails(self):
        rc, out = self.gate([PLANT], allowlist={"entries": []})
        self.assertR3aFails(rc, out)
        hits, _ = enumerated(section(out, "R3a"))
        t1 = [h for h in hits if " T1 " in h and "$500" in h]
        self.assertTrue(t1, hits)
        self.assertIn(PLANT, t1[0])
        for trig in ("rebate", "Xcel", "pays"):
            self.assertIn(trig, t1[0].split("trigger:")[1])

    # (b)
    def test_b_word_form_rebate_fails(self):
        s = "You can get a five hundred dollar rebate."
        rc, out = self.gate([s], allowlist={"entries": []})
        self.assertR3aFails(rc, out)
        hits, _ = enumerated(section(out, "R3a"))
        wf = [h for h in hits if " WF " in h]
        self.assertEqual(len(wf), 1, hits)
        self.assertIn("five hundred dollar", wf[0])
        self.assertIn(s, wf[0])


class TestNegatives(GateCase):
    # (c)
    NEG = ["Homeowners paid $2,400 for a typical attic.",
           "You can pay by credit card.",
           "Most homes here run twelve hundred square feet.",
           "A typical attic costs $1,800 to $3,200."]

    def test_c_negatives_never_r3a(self):
        rc, out = self.gate(self.NEG, allowlist={"entries": []})
        self.assertR3aClean(rc, out)
        self.assertEqual(summary_row(out, "R3a")[0], 0)
        sec = section(out, "R3a")
        self.assertEqual(enumerated(sec), ([], []))
        for s in self.NEG:
            self.assertNotIn(s, "\n".join(sec))
        # the $ figures land in R3b raw (reported or filtered; both enumerated)
        bh, br = enumerated(section(out, "R3b"))
        r3b_raw = "\n".join(bh + br)
        for fig in ("$2,400", "$1,800", "$3,200"):
            self.assertIn(fig, r3b_raw)

    def test_c_each_negative_alone_never_r3a(self):
        for s in self.NEG:
            with self.subTest(sentence=s):
                rc, out = self.gate([s], allowlist={"entries": []})
                self.assertR3aClean(rc, out)
                self.assertEqual(summary_row(out, "R3a")[0], 0)


class TestNormalization(GateCase):
    # (d) allowlist written plainly (hyphen, '&', single spaces); the page
    # renders an en dash, '&amp;', or double spaces.
    CASES = [
        ("en dash", "Xcel pays a $500 rebate for attic-floor insulation.",
         "Xcel pays a $500 rebate for attic&ndash;floor insulation."),
        ("ampersand", "Xcel pays a $400 rebate for attic & wall insulation.",
         "Xcel pays a $400 rebate for attic &amp; wall insulation."),
        ("double space", "Xcel pays a $300 rebate for crawlspace insulation.",
         "Xcel pays a $300 rebate  for  crawlspace insulation."),
    ]

    def test_d_allowlisted_variants_clear(self):
        for name, allowed, rendered in self.CASES:
            with self.subTest(case=name):
                rc, out = self.gate([rendered],
                                    allowlist={"entries": [entry(allowed)]})
                self.assertR3aClean(rc, out)
                self.assertGreater(summary_row(out, "R3a")[0], 0,
                                   "plant not seen at all")
                hits, removed = enumerated(section(out, "R3a"))
                self.assertEqual(hits, [])
                self.assertTrue(removed)
                self.assertTrue(all("r3a allowlist" in r for r in removed))
                self.assertNotIn("STALE ALLOWLIST ENTRY", out)

    def test_d_control_same_pages_fail_without_entry(self):
        for name, _allowed, rendered in self.CASES:
            with self.subTest(case=name):
                rc, out = self.gate([rendered], allowlist={"entries": []})
                self.assertR3aFails(rc, out)

    # (d, corrective D1) the ENTRY side carries the entity or the glyph and
    # gets the same dec()-then-collapse pipeline the page side got. Each
    # entry must clear its page with no STALE line.
    ENTRY_CASES = [
        ("entry &amp; (copied from page source)",
         "Xcel pays a $400 rebate for attic &amp; wall insulation.",
         "Xcel pays a $400 rebate for attic &amp; wall insulation."),
        ("entry &amp;amp; (page source double-encoded)",
         "Xcel pays a $400 rebate for attic &amp;amp; wall insulation.",
         "Xcel pays a $400 rebate for attic &amp;amp; wall insulation."),
        ("entry &ndash;",
         "Xcel pays a $500 rebate for attic&ndash;floor insulation.",
         "Xcel pays a $500 rebate for attic-floor insulation."),
        ("entry literal en dash",
         "Xcel pays a $500 rebate for attic–floor insulation.",
         "Xcel pays a $500 rebate for attic&ndash;floor insulation."),
        ("entry literal em dash",
         "Xcel pays a $500 rebate — for attic insulation.",
         "Xcel pays a $500 rebate &mdash; for attic insulation."),
        ("entry hyphen, page literal en dash",
         "Xcel pays a $500 rebate for attic-floor insulation.",
         "Xcel pays a $500 rebate for attic–floor insulation."),
    ]

    def test_d_entry_side_entities_and_dashes_clear(self):
        for name, allowed, rendered in self.ENTRY_CASES:
            with self.subTest(case=name):
                rc, out = self.gate([rendered],
                                    allowlist={"entries": [entry(allowed)]})
                self.assertR3aClean(rc, out)
                self.assertGreater(summary_row(out, "R3a")[0], 0,
                                   "plant not seen at all")
                self.assertNotIn("STALE ALLOWLIST ENTRY", out)


class TestMoneyNumerals(GateCase):
    # (corrective D2) a 1900-2099 numeral is money only with a directly
    # attached payout binder or "dollars".
    def test_d2_code_year_not_r3a(self):
        rc, out = self.gate(["Homes here are built up to the 2021 IECC, yes "
                             "- several Xcel rebate programs are live."],
                            allowlist={"entries": []})
        self.assertR3aClean(rc, out)
        self.assertEqual(summary_row(out, "R3a")[0], 0)

    def test_d2_attached_binder_year_range_amount_is_r3a(self):
        s = "Xcel pays up to 2000 for attic work."
        rc, out = self.gate([s], allowlist={"entries": []})
        self.assertR3aFails(rc, out)
        hits, _ = enumerated(section(out, "R3a"))
        t2 = [h for h in hits if " T2 " in h and "2000" in h]
        self.assertEqual(len(t2), 1, hits)
        self.assertIn(s, t2[0])

    # (corrective D3) a T2 numeral inside a $ figure is not a second hit.
    def test_d3_dollar_figure_counted_once(self):
        rc, out = self.gate([PLANT], allowlist={"entries": []})
        self.assertR3aFails(rc, out)
        hits, _ = enumerated(section(out, "R3a"))
        self.assertEqual(len([h for h in hits if " T1 " in h]), 1, hits)
        self.assertEqual([h for h in hits if " T2 " in h], [])
        self.assertIn("R3 RAW SPLIT", out)


class TestEnforcement(GateCase):
    # (e)
    def test_e_absent_allowlist_not_enforced(self):
        rc, out = self.gate([PLANT])
        self.assertEqual(rc, 0, out[-1500:])
        _raw, adj, verdict = summary_row(out, "R3a")
        self.assertGreater(adj, 0)
        self.assertIn("NOT ENFORCED", verdict)
        self.assertIn("R3A NOT ENFORCED: no allowlist at "
                      "ops/r3a_allowlist.json (%d hits)" % adj, out)
        hits, _ = enumerated(section(out, "R3a"))
        self.assertEqual(len(hits), adj)
        self.assertNotIn("CLAIM GATE: FAIL", out)

    def test_e_empty_allowlist_enforced(self):
        rc, out = self.gate([PLANT], allowlist={"entries": []})
        self.assertR3aFails(rc, out)
        self.assertNotIn("R3A NOT ENFORCED", out)

    def test_e_entry_without_ruling_exit_2(self):
        rc, out = self.gate([PLANT],
                            allowlist={"entries": [entry(PLANT, ruling=None)]})
        self.assertEqual(rc, 2, out[-1500:])
        self.assertIn("'ruling'", out)

    def test_e_entry_without_reason_exit_2(self):
        rc, out = self.gate([PLANT],
                            allowlist={"entries": [entry(PLANT, reason=None)]})
        self.assertEqual(rc, 2, out[-1500:])
        self.assertIn("'reason'", out)


class TestPrograms(GateCase):
    # (g)
    FIX = "Fixture Program paid $300 for the attic."

    def test_g_no_site_list_builtin_only(self):
        rc, out = self.gate([self.FIX], allowlist={"entries": []})
        self.assertIn("R3A PROGRAMS: built-in list only", out)
        self.assertR3aClean(rc, out)  # not a program without the site list

    def test_g_site_list_adds_program(self):
        rc, out = self.gate([self.FIX], allowlist={"entries": []},
                            programs={"programs": ["Fixture Program"]})
        self.assertR3aFails(rc, out)
        self.assertNotIn("R3A PROGRAMS: built-in list only", out)
        self.assertRegex(out, r"R3A PROGRAMS: built-in 7 \+ site 1 "
                              r"\(ops/r3a_programs\.json; 1 new\) = 8 names")
        hits, _ = enumerated(section(out, "R3a"))
        fx = [h for h in hits if self.FIX in h]
        self.assertTrue(fx, hits)
        trig = fx[0].split("trigger:")[1]
        self.assertIn("Fixture Program", trig)
        self.assertIn("paid", trig)

    def test_g_builtins_still_fire_with_site_list(self):
        rc, out = self.gate([PLANT], allowlist={"entries": []},
                            programs={"programs": ["Fixture Program"]})
        self.assertR3aFails(rc, out)
        hits, _ = enumerated(section(out, "R3a"))
        self.assertTrue([h for h in hits if PLANT in h and "Xcel" in h], hits)


class TestCanonSuite(unittest.TestCase):
    # (f) ops/checks/run_checks.py, claim_gate module only.
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="k45_r3a_suite_")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.cfg = write_config(self.tmp)
        self.site = make_site(os.path.join(self.tmp, "s"), [PLANT],
                              allowlist={"entries": []})
        self.manifest = os.path.join(self.tmp, "manifest.json")
        with open(self.manifest, "w") as fh:
            json.dump({"site": "k45-fixture", "modules": {
                "claim_gate": {"data": {"config": self.cfg}}}}, fh)

    def run_suite(self, *extra):
        p = subprocess.run([sys.executable, RUNNER, "--site", self.site,
                            "--manifest", self.manifest, "--only",
                            "claim_gate"] + list(extra), cwd=self.tmp,
                           capture_output=True, text=True, timeout=600)
        return p.returncode, p.stdout + p.stderr

    def blinded_fixtures(self):
        """A claim_gate canary whose page is CLEAN: the canary finds nothing."""
        fx = os.path.join(self.tmp, "fixtures")
        cdir = os.path.join(fx, "claim_gate", "canary")
        os.makedirs(os.path.join(cdir, "public"))
        with open(os.path.join(cdir, "public", "index.html"), "w") as fh:
            fh.write(PAGE.format(body=""))
        with open(os.path.join(cdir, "config.json"), "w") as fh:
            json.dump(CONFIG, fh)
        with open(os.path.join(cdir, "manifest.json"), "w") as fh:
            json.dump({"data": {"config": "config.json"},
                       "options": {"git_snapshot": True}}, fh)
        return fx

    def test_f_findings_vs_blind_canary(self):
        rc1, out1 = self.run_suite()
        self.assertEqual(rc1, checklib.EXIT_FINDINGS, out1[-2000:])
        self.assertRegex(out1, r"claim_gate\s+FIRED")
        self.assertIn("claim gate R3a", out1)
        rc3, out3 = self.run_suite("--fixtures-dir", self.blinded_fixtures())
        self.assertEqual(rc3, checklib.EXIT_CANARY, out3[-2000:])
        self.assertIn("BLIND INSTRUMENT", out3)
        self.assertNotEqual(rc1, rc3)


if __name__ == "__main__":
    unittest.main()
