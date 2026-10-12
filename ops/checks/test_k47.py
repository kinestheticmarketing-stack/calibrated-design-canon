"""K47 row 5: tests for K47 rows 1-4 (superlative default union, main-checkout
peer resolution, claim_gate message). Stdlib unittest only; every fixture is
built in a tempfile dir and removed on cleanup. No real repo is touched.

Run:  cd ops/checks && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_k47 -v
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

CHECKS = Path(__file__).resolve().parent
MODULES = CHECKS / "modules"
RUNNER = CHECKS / "run_checks.py"
sys.path.insert(0, str(CHECKS))
import checklib as C  # noqa: E402

GIT = ["git", "-c", "user.name=k47test", "-c", "user.email=k47test@localhost",
       "-c", "init.defaultBranch=main", "-c", "core.hooksPath=/dev/null",
       "-c", "commit.gpgsign=false"]


def load(name):
    spec = importlib.util.spec_from_file_location("k47_" + name, MODULES / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(cwd, *args):
    subprocess.run(GIT + list(args), cwd=str(cwd), check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def ctx_for(mod, site, data, options=None):
    opts = dict(getattr(mod, "OPTIONS", {}) or {})
    opts.update(options or {})
    return C.Context(site_root=site, public_dir=site / "public", data=data,
                     options=opts, site_name="K47TEST", module=mod.NAME)


class TempCase(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory(prefix="k47_test_")
        self.T = Path(self._td.name).resolve()

    def tearDown(self):
        self._td.cleanup()


# ---------------------------------------------------------------- (a)

PAGE_A = ("<html><head><title>t</title></head><body><p>The highest-leverage "
          "upgrade. Also a zzk47fixture superlative here.</p></body></html>")


class TestA(TempCase):
    def setUp(self):
        super().setUp()
        self.mod = load("superlative_scan")
        self.site = self.T / "site"
        (self.site / "public").mkdir(parents=True)
        (self.site / "public" / "index.html").write_text(PAGE_A, encoding="utf-8")

    def msgs(self, data):
        return [f.message for f in self.mod.check(ctx_for(self.mod, self.site, data))]

    def assertDefault(self, msgs):
        self.assertTrue(any("highest-leverage" in m and "default:RETIRED_PATTERNS" in m
                            for m in msgs), msgs)

    def test_a_i_no_patterns_key_uses_default(self):
        self.assertDefault(self.msgs({}))

    def test_a_ii_empty_patterns_values_use_default(self):
        for v in ("", None, []):
            with self.subTest(patterns=v):
                self.assertDefault(self.msgs({"patterns": v}))

    def test_a_iii_site_patterns_union_with_default(self):
        p = self.site / "sup.txt"
        p.write_text("# site list\nzzk47fixture superlative\n", encoding="utf-8")
        msgs = self.msgs({"patterns": str(p)})
        self.assertTrue(any("zzk47fixture superlative" in m.lower() and "(pattern line2)" in m
                            for m in msgs), msgs)
        self.assertDefault(msgs)

    def test_a_iv_comment_only_site_file_still_fires_default(self):
        p = self.site / "sup.txt"
        p.write_text("# nothing here\n\n# still nothing\n", encoding="utf-8")
        self.assertDefault(self.msgs({"patterns": str(p)}))

    def test_a_v_identical_site_pattern_deduplicated(self):
        default = self.mod._load_patterns(
            self.mod.DEFAULT_PATH, self.mod.DEFAULT_VAR,
            self.mod.DEFAULT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(len(default), 1, default)
        src = default[0][1]
        self.assertNotIn("\n", src)
        p = self.site / "sup.txt"
        p.write_text(src + "\n", encoding="utf-8")
        hits = [m for m in self.msgs({"patterns": str(p)})
                if "highest-leverage" in m]
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("default:RETIRED_PATTERNS", hits[0])


# ---------------------------------------------------------------- (b)

class TestB(TempCase):
    def setUp(self):
        super().setUp()
        self.mod = load("cross_property_similarity")
        self.site = self.T / "site"
        (self.site / "public").mkdir(parents=True)
        (self.site / "public" / "index.html").write_text(
            "<html><body><p>alpha bravo charlie delta echo foxtrot golf hotel"
            "</p></body></html>", encoding="utf-8")
        (self.site / "sim.json").write_text(json.dumps({
            "PAIRS": [["index.html", "x.html", "home"]], "STRIP_PATTERNS": [],
            "THRESHOLD": 0.5, "SHINGLE_N": 3}), encoding="utf-8")
        (self.T / "peer" / "public").mkdir(parents=True)
        (self.T / "peer" / "public" / "x.html").write_text(
            "<html><body><p>one two three four five six seven eight"
            "</p></body></html>", encoding="utf-8")
        git(self.site, "init", "-q")
        git(self.site, "add", "-A")
        git(self.site, "commit", "-q", "-m", "fixture")
        self.wt = None

    def tearDown(self):
        if self.wt is not None and self.wt.exists():
            subprocess.run(["git", "-C", str(self.site), "worktree", "remove",
                            "--force", str(self.wt)], capture_output=True)
        super().tearDown()

    def run_check(self, site_root, peer):
        data = {"peer_public": peer, "config": site_root / "sim.json"}
        return self.mod.check(ctx_for(self.mod, site_root, data))

    def test_b1_relative_peer_from_main_checkout(self):
        self.assertEqual(self.run_check(self.site, "../peer/public"), [])

    def test_b2_relative_peer_from_worktree_resolves_to_main_checkout(self):
        self.wt = self.T / "wt" / "site-wt"
        self.wt.parent.mkdir()
        git(self.site, "worktree", "add", "-q", str(self.wt), "-b", "k47test")
        self.assertFalse((self.wt / "../peer/public").exists())
        self.assertEqual(self.run_check(self.wt, "../peer/public"), [])

    def test_b3_nonexistent_peer_runner_exits_2(self):
        man = self.T / "manifest.json"
        man.write_text(json.dumps({"site": "K47TEST", "modules": {
            "cross_property_similarity": {"data": {
                "peer_public": "../nope/public", "config": "sim.json"}}}}),
            encoding="utf-8")
        p = subprocess.run([sys.executable, "-B", str(RUNNER), "--site", str(self.site),
                            "--manifest", str(man), "--only",
                            "cross_property_similarity"],
                           capture_output=True, text=True,
                           env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        out = p.stdout
        self.assertEqual(p.returncode, 2, out + p.stderr)
        self.assertIn("cross_property_similarity    FIRED", out)
        self.assertIn("CONFIG ERROR", out)
        self.assertRegex(out, r"cross_property_similarity\s+ERROR")

    def test_b4_absolute_peer_used_as_given(self):
        peer = (self.T / "peer" / "public").resolve()
        self.assertFalse(peer.is_relative_to(self.site.resolve()))
        self.assertEqual(self.run_check(self.site, str(peer)), [])
        with self.assertRaises(ValueError):
            self.run_check(self.site, str(self.T / "nope" / "public"))

    def test_b5_in_tree_relative_peer_resolves_within_worktree(self):
        local = (self.site / "public" / "index.html").read_text(encoding="utf-8")
        (self.site / "control").mkdir()
        (self.site / "control" / "x.html").write_text(
            "<html><body><p>kilo lima mike november oscar papa quebec romeo"
            "</p></body></html>", encoding="utf-8")
        git(self.site, "add", "-A")
        git(self.site, "commit", "-q", "-m", "control")
        self.wt = self.T / "wt" / "site-wt"
        self.wt.parent.mkdir()
        git(self.site, "worktree", "add", "-q", str(self.wt), "-b", "k47test")
        # Worktree-only, uncommitted: the control copy equals the local page.
        (self.wt / "control" / "x.html").write_text(local, encoding="utf-8")
        # Main checkout's copy is distinct: no finding there.
        self.assertEqual(self.run_check(self.site, "control"), [])
        # From the worktree, the worktree's copy is read: Jaccard finding.
        f = self.run_check(self.wt, "control")
        self.assertEqual(len(f), 1, f)
        self.assertIn("Jaccard 1.0000", f[0].message)


# ---------------------------------------------------------------- (c)

class TestC(TempCase):
    def test_c_claim_gate_message_names_direct_command(self):
        mod = load("claim_gate")
        site = self.T / "site"
        (site / "public").mkdir(parents=True)
        stdout = ("CLAIM GATE SUMMARY\n"
                  "  R3a  unsourced figure  RAW 4  ADJ 2  FAIL\n"
                  "CLAIM GATE: FAIL\n")
        cp = subprocess.CompletedProcess(args=[], returncode=1,
                                         stdout=stdout, stderr="")
        fake = mock.Mock()
        fake.run.return_value = cp
        with mock.patch.object(mod, "subprocess", fake):
            out = mod.check(ctx_for(mod, site, {"config": site / "cg.json"}))
        fake.run.assert_called_once()
        self.assertEqual(len(out), 1, out)
        msg = out[0].message
        self.assertIn("R3a unsourced figure: 2 blocking", msg)
        self.assertNotIn("ops/claim_gate.sh", msg)
        self.assertIn("ops/claim_gate/claim_gate.py --config <config> "
                      "--repo <site>", msg)


if __name__ == "__main__":
    unittest.main()
