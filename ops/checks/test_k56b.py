"""K56b-canon: tests for cross_property_similarity option all_peers (K3).
Stdlib unittest only; every fixture is built in a tempfile dir and removed on
cleanup. No fixture on disk and no site repo is touched.

Run:  cd ops/checks && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_k56b -v
"""

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

CHECKS = Path(__file__).resolve().parent
sys.path.insert(0, str(CHECKS))
import checklib as C  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "k56bt_cps", CHECKS / "modules" / "cross_property_similarity.py")
CPS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CPS)

SAME = "<html><body><p>alpha bravo charlie delta echo foxtrot golf hotel</p></body></html>"
OTHER = "<html><body><p>one two three four five six seven eight</p></body></html>"


class AllPeers(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory(prefix="k56b_test_")
        self.T = Path(self._td.name).resolve()
        self.site = self.T / "site"
        (self.site / "public").mkdir(parents=True)
        (self.site / "public" / "index.html").write_text(SAME, encoding="utf-8")
        (self.site / "sim.json").write_text(json.dumps({
            "PAIRS": [["index.html", "x.html", "home"]], "STRIP_PATTERNS": [],
            "THRESHOLD": 0.5, "SHINGLE_N": 3}), encoding="utf-8")
        # peer_a: distinct; peer_b: a copy of the local page; peer_c: no x.html
        for name, body in (("peer_a", OTHER), ("peer_b", SAME), ("peer_c", None)):
            (self.T / name / "public").mkdir(parents=True)
            if body is not None:
                (self.T / name / "public" / "x.html").write_text(body, encoding="utf-8")

    def tearDown(self):
        self._td.cleanup()

    def peer(self, name):
        return str((self.T / name / "public").resolve())

    def run_check(self, data, options=None):
        opts = dict(CPS.OPTIONS)
        opts.update(options or {})
        d = {"peer_public": self.peer("peer_a"), "config": self.site / "sim.json"}
        d.update(data)
        ctx = C.Context(site_root=self.site, public_dir=self.site / "public",
                        data=d, options=opts, site_name="K56BTEST", module=CPS.NAME)
        return CPS.check(ctx)

    def text(self, findings):
        return "\n".join(f.message for f in findings)

    def test_default_path_compares_only_peer_public(self):
        # peer_publics names a copy of the local page, but it must be ignored
        f = self.run_check({"peer_publics": [self.peer("peer_b")]})
        self.assertEqual(f, [])
        # and the primary peer alone is compared: a matching primary fires
        f = self.run_check({"peer_public": self.peer("peer_b")})
        self.assertEqual(len(f), 1, self.text(f))
        self.assertIn("Jaccard", f[0].message)

    def test_all_peers_true_compares_every_peer_and_names_it(self):
        f = self.run_check({"peer_publics": [self.peer("peer_b"), self.peer("peer_c")]},
                           {"all_peers": True})
        msgs = [x.message for x in f]
        self.assertEqual(len(f), 2, msgs)  # peer_b Jaccard + peer_c CONTROL MISSING
        jac = [m for m in msgs if "Jaccard" in m]
        miss = [m for m in msgs if "CONTROL MISSING" in m]
        self.assertEqual((len(jac), len(miss)), (1, 1), msgs)
        self.assertIn(self.peer("peer_b"), jac[0])
        self.assertIn(self.peer("peer_c"), miss[0])
        self.assertTrue(all("peer " in m for m in msgs))

    def test_all_peers_true_without_peer_publics_is_peer_public_only(self):
        f = self.run_check({}, {"all_peers": True})
        self.assertEqual(f, [])

    def test_all_peers_dedupes_repeated_peer(self):
        b = self.peer("peer_b")
        f = self.run_check({"peer_public": b, "peer_publics": [b]}, {"all_peers": True})
        self.assertEqual(len(f), 1, self.text(f))

    def test_all_peers_string_false_is_config_error(self):
        for bad in ("false", "true", "", 0, 1, None):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError) as cm:
                    self.run_check({}, {"all_peers": bad})
                self.assertIn("CONFIG ERROR", str(cm.exception))
                self.assertIn("all_peers", str(cm.exception))

    def test_all_peers_false_passes_and_ignores_peer_publics(self):
        f = self.run_check({"peer_publics": [self.peer("peer_b")]}, {"all_peers": False})
        self.assertEqual(f, [])

    def test_bad_peer_publics_entry_is_config_error(self):
        with self.assertRaises(ValueError) as cm:
            self.run_check({"peer_publics": [str(self.T / "nope" / "public")]},
                           {"all_peers": True})
        self.assertIn("CONFIG ERROR", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
