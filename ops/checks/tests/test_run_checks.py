"""Tests for ops/checks/run_checks.py (K44 row S4). Stdlib unittest only.

Every test builds its own tiny site, test modules and canary fixtures in a
tempfile dir (removed on cleanup) and drives run_checks.py by subprocess with
--modules-dir/--fixtures-dir. Nothing touches a real site or the network.

Run:  cd ops/checks && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

CHECKS = Path(__file__).resolve().parents[1]
RUNNER = CHECKS / "run_checks.py"
REAL_MODULES = CHECKS / "modules"
REAL_FIXTURES = CHECKS / "fixtures"

CLEAN_HTML = "<html><body><p>All good here.</p></body></html>"
BAD_HTML = "<html><body><p>We sell BADWORD today.</p></body></html>"

# A module that flags any page containing a word listed in data["words"].
# It prints a marker so tests can see whether the canary or the real run ran.
PLANTED_SRC = '''
NAME = "{name}"
DESCRIPTION = "test module: flags words from a list"
REQUIRES = {{"words": "path to a word list"}}

def check(ctx):
    print("RUN %s %s" % ("CANARY" if ctx.canary else "REAL", NAME), flush=True)
    words = [w.strip() for w in ctx.read_text(ctx.data["words"]).splitlines() if w.strip()]
    out = []
    for page in ctx.iter_html():
        text = ctx.visible_text(ctx.read_text(page))
        for w in words:
            if w in text:
                out.append(ctx.finding(page, "planted word %r" % w, text))
    return out
'''

# A module whose real run tries the network (the canary run returns a finding
# so the canary passes and the real run is reached).
NETWORK_SRC = '''
import socket
NAME = "netmod"
DESCRIPTION = "test module: attempts network on the real run"
REQUIRES = {}

def check(ctx):
    if ctx.canary:
        return [ctx.finding("index.html", "canary", "canary")]
    socket.create_connection(("127.0.0.1", 9), timeout=1)
    return []
'''

# A module whose real run tries to write inside the site.
WRITER_SRC = '''
NAME = "writemod"
DESCRIPTION = "test module: attempts a write inside the site on the real run"
REQUIRES = {}

def check(ctx):
    if ctx.canary:
        return [ctx.finding("index.html", "canary", "canary")]
    (ctx.site_root / "INTRUDER.txt").write_text("x")
    return []
'''


class RunnerTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="k44_checks_test_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.site = self.tmp / "site"
        self.modules = self.tmp / "modules"
        self.fixtures = self.tmp / "fixtures"
        for d in (self.site / "public", self.modules, self.fixtures):
            d.mkdir(parents=True)
        self.write_site(CLEAN_HTML)
        (self.site / "words.txt").write_text("BADWORD\n")

    # -- builders -----------------------------------------------------------
    def write_site(self, html):
        (self.site / "public" / "index.html").write_text(html)

    def add_module(self, name, src=None, canary="bad", canary_data=None):
        """canary: 'bad' = planted defect, 'clean' = blind, None = no fixture."""
        (self.modules / (name + ".py")).write_text(
            textwrap.dedent(src if src is not None else PLANTED_SRC.format(name=name)))
        if canary is None:
            return
        cdir = self.fixtures / name / "canary"
        (cdir / "public").mkdir(parents=True)
        (cdir / "public" / "index.html").write_text(
            BAD_HTML if canary == "bad" else CLEAN_HTML)
        (cdir / "words.txt").write_text("BADWORD\n")
        data = {"words": "words.txt"} if canary_data is None else canary_data
        (cdir / "manifest.json").write_text(json.dumps({"data": data, "options": {}}))

    def manifest(self, modules):
        p = self.tmp / "manifest.json"
        p.write_text(json.dumps({"site": "TEST", "public_dir": "public",
                                 "modules": modules}))
        return p

    def run_checks(self, modules, *extra):
        m = self.manifest(modules)
        cmd = [sys.executable, str(RUNNER), "--site", str(self.site),
               "--manifest", str(m), "--modules-dir", str(self.modules),
               "--fixtures-dir", str(self.fixtures)] + list(extra)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        r = subprocess.run(cmd, capture_output=True, text=True, env=env,
                           timeout=60)
        return r.returncode, r.stdout + r.stderr

    W = {"data": {"words": "words.txt"}, "options": {}}

    # -- 1. clean -----------------------------------------------------------
    def test_01_clean_site_exits_0_and_canary_fires(self):
        self.add_module("planted")
        code, out = self.run_checks({"planted": self.W})
        self.assertEqual(code, 0, out)
        self.assertRegex(out, r"planted\s+FIRED")
        self.assertIn("FINDINGS (0)", out)
        self.assertIn("exit=0", out)

    # -- 2. findings --------------------------------------------------------
    def test_02_defect_exits_1(self):
        self.add_module("planted")
        self.write_site(BAD_HTML)
        code, out = self.run_checks({"planted": self.W})
        self.assertEqual(code, 1, out)
        self.assertRegex(out, r"planted\s+FAIL \(1 findings\)")
        self.assertIn("index.html | planted |", out)

    # -- 3. canary failures -------------------------------------------------
    def test_03a_blind_canary_exits_3(self):
        self.add_module("planted", canary="clean")
        code, out = self.run_checks({"planted": self.W})
        self.assertEqual(code, 3, out)
        self.assertIn("BLIND INSTRUMENT", out)

    def test_03b_missing_canary_exits_3(self):
        self.add_module("planted", canary=None)
        code, out = self.run_checks({"planted": self.W})
        self.assertEqual(code, 3, out)
        self.assertIn("NO CANARY", out)

    # -- 4. distinct codes, canary precedence over findings ----------------
    def test_04_canary_failure_blocks_real_checks(self):
        self.add_module("good")
        self.add_module("blind", canary="clean")
        self.write_site(BAD_HTML)  # real checks WOULD find a defect
        code, out = self.run_checks({"good": self.W, "blind": self.W})
        self.assertNotEqual(1, 3)
        self.assertEqual(code, 3, out)
        self.assertNotIn("RUN REAL", out)
        self.assertRegex(out, r"good\s+NOT RUN \(a canary failed\)")
        self.assertRegex(out, r"blind\s+CANARY FAIL")
        self.assertIn("FINDINGS (0)", out)

    # -- 5. missing data path ------------------------------------------------
    def test_05_missing_data_path_exits_2_naming_module_key_path(self):
        self.add_module("planted")
        code, out = self.run_checks(
            {"planted": {"data": {"words": "nope/missing.txt"}, "options": {}}})
        self.assertEqual(code, 2, out)
        self.assertIn("CONFIG ERROR", out)
        self.assertIn("planted", out)
        self.assertIn("'words'", out)
        self.assertIn("nope/missing.txt", out)
        self.assertNotIn("RUN CANARY", out)

    # -- 6. not enabled ------------------------------------------------------
    def test_06_module_absent_from_manifest_reported_not_enabled(self):
        self.add_module("planted")
        self.add_module("extra")
        code, out = self.run_checks({"planted": self.W})
        self.assertEqual(code, 0, out)
        self.assertRegex(out, r"extra\s+NOT ENABLED")
        self.assertIn("not_enabled=1", out)
        self.assertIn("NOT ENABLED: extra", out)

    # -- 7. config errors ----------------------------------------------------
    def test_07a_unknown_module_exits_2(self):
        self.add_module("planted")
        code, out = self.run_checks({"planted": self.W, "ghost": self.W})
        self.assertEqual(code, 2, out)
        self.assertIn("unknown module(s): ghost", out)

    def test_07b_json_inside_site_refused(self):
        self.add_module("planted")
        target = self.site / "report.json"
        code, out = self.run_checks({"planted": self.W}, "--json", str(target))
        self.assertEqual(code, 2, out)
        self.assertIn("inside --site", out)
        self.assertFalse(target.exists())

    def test_07c_json_outside_site_written(self):
        self.add_module("planted")
        target = self.tmp / "out" / "report.json"
        code, out = self.run_checks({"planted": self.W}, "--json", str(target))
        self.assertEqual(code, 0, out)
        rep = json.loads(target.read_text())
        self.assertEqual(rep["exit"], 0)
        self.assertEqual(rep["modules"]["planted"]["status"], "PASS")

    # -- 8. safety guards ----------------------------------------------------
    def test_08a_network_attempt_fails_run(self):
        self.add_module("netmod", src=NETWORK_SRC, canary_data={})
        code, out = self.run_checks({"netmod": {"data": {}, "options": {}}})
        self.assertNotEqual(code, 0, out)
        self.assertEqual(code, 2, out)
        self.assertIn("network is blocked", out)
        self.assertRegex(out, r"netmod\s+ERROR")

    def test_08b_write_inside_site_refused(self):
        self.add_module("writemod", src=WRITER_SRC, canary_data={})
        code, out = self.run_checks({"writemod": {"data": {}, "options": {}}})
        self.assertEqual(code, 2, out)
        self.assertIn("refusing to write inside", out)
        self.assertFalse((self.site / "INTRUDER.txt").exists())

    # -- 9. ordering ---------------------------------------------------------
    def test_09_all_canaries_run_before_any_real_check(self):
        self.add_module("alpha")
        self.add_module("beta")
        code, out = self.run_checks({"alpha": self.W, "beta": self.W})
        self.assertEqual(code, 0, out)
        lines = [l for l in out.splitlines() if l.startswith("RUN ")]
        self.assertEqual(lines, ["RUN CANARY alpha", "RUN CANARY beta",
                                 "RUN REAL alpha", "RUN REAL beta"], out)
        self.assertLess(out.index("CANARIES"), out.index("RUN REAL"))


# -- 10. structural: the real suite -----------------------------------------
class RealSuiteStructureTest(unittest.TestCase):
    def test_10_every_real_module_has_canary_manifest(self):
        mods = sorted(p.stem for p in REAL_MODULES.glob("*.py")
                      if not p.stem.startswith("_"))
        self.assertTrue(mods, "no modules found in %s" % REAL_MODULES)
        for name in mods:
            with self.subTest(module=name):
                man = REAL_FIXTURES / name / "canary" / "manifest.json"
                self.assertTrue(man.is_file(), "NO CANARY: %s missing" % man)
                entry = json.loads(man.read_text(encoding="utf-8"))
                self.assertIsInstance(entry, dict, man)


if __name__ == "__main__":
    unittest.main()
