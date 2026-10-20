"""K56b-canon: tests for the validate_genesis.py changes K1 (territory_states,
town code_facts), K2 (server-copy lead_destination) and K4 (path helpers).
Stdlib unittest only; every test works on a temp copy of the Exampleton
FIXTURE (removed in tearDown). Nothing on disk is modified.

Run (from canon root):
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest ops/genesis/test_k56b.py -v
"""

import copy
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

GENESIS = Path(__file__).resolve().parent
FIXTURE = GENESIS / "fixtures" / "exampleton"
# Read-only real-world input; skipped when the sibling checkout is absent.
FORT_COLLINS_MP = Path.home() / "code" / "fortcollinscoloradoinsulation.com" / "inputs" / "market_pack.json"

_spec = importlib.util.spec_from_file_location("k56bt_validate_genesis", GENESIS / "validate_genesis.py")
VG = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(VG)
VF = VG._vf


class K56bBase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="k56b_genesis_"))
        self.root = self.tmp / "exampleton"
        shutil.copytree(FIXTURE, self.root)
        self.intake = self.root / "intake.json"
        self.mp = self.root / "market_pack.json"
        self.registry = self.root / "facts" / "registry.json"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def edit(self, path, fn):
        d = json.loads(path.read_text(encoding="utf-8"))
        fn(d)
        path.write_text(json.dumps(d, indent=2), encoding="utf-8")

    def errors(self):
        return VG.validate(self.intake, self.mp, self.registry)


class TestK1Territory(K56bBase):
    def test_fixture_validates(self):
        self.assertEqual(self.errors(), [])

    def test_every_town_converted_to_territory_states(self):
        def conv(d):
            for t in d["towns"]:
                s = t.pop("territory_state")
                t["territory_states"] = {"electric": s, "gas": s}
        self.edit(self.mp, conv)
        self.assertEqual(self.errors(), [])

    def test_mixed_shapes_validate(self):
        def conv(d):
            t = d["towns"][0]
            s = t.pop("territory_state")
            t["territory_states"] = {"electric": s, "gas": s}
        self.edit(self.mp, conv)
        mp = json.loads(self.mp.read_text(encoding="utf-8"))
        shapes = {"territory_state" in t for t in mp["towns"]}
        self.assertEqual(shapes, {True, False})
        self.assertEqual(self.errors(), [])

    def test_both_shapes_gives_exactly_one_error(self):
        def both(d):
            t = d["towns"][0]
            t["territory_states"] = {"electric": t["territory_state"], "gas": t["territory_state"]}
        self.edit(self.mp, both)
        errs = self.errors()
        self.assertEqual(len(errs), 1, errs)
        self.assertIn("carries both territory_state and territory_states", errs[0])

    def test_unknown_without_absence_reason_fails(self):
        def plant(d):
            t = d["towns"][0]
            t.pop("territory_state")
            t["territory_states"] = {"electric": "UNKNOWN", "gas": "NAMED"}
            t["absence_reason"] = None
        self.edit(self.mp, plant)
        errs = self.errors()
        self.assertTrue(errs, "UNKNOWN territory_states without absence_reason must fail")
        self.assertTrue(errs[0].startswith("market_pack: "), errs)

    def test_unknown_with_absence_reason_passes_schema(self):
        # control for the case above: the same town with a reason has no schema error
        def plant(d):
            t = d["towns"][0]
            t.pop("territory_state")
            t["territory_states"] = {"electric": "UNKNOWN", "gas": "UNKNOWN"}
            t["absence_reason"] = "no source settles it"
        self.edit(self.mp, plant)
        self.assertFalse([e for e in self.errors() if e.startswith("market_pack: ")])

    def test_town_code_facts_key_missing_from_registry_fails(self):
        def plant(d):
            d["towns"][0]["code_facts"] = {"facts_keys": ["ext-no-such-fact"]}
        self.edit(self.mp, plant)
        errs = self.errors()
        self.assertEqual(len(errs), 1, errs)
        self.assertIn("ext-no-such-fact", errs[0])
        self.assertIn("code_facts", errs[0])

    def test_town_code_facts_key_present_in_registry_passes(self):
        def plant(d):
            d["towns"][0]["code_facts"] = {"facts_keys": ["ext-energy-code"]}
        self.edit(self.mp, plant)
        self.assertEqual(self.errors(), [])

    @unittest.skipUnless(FORT_COLLINS_MP.is_file(), "Fort Collins market_pack.json not present")
    def test_fort_collins_market_pack_validates(self):
        # read-only: copy the real pack into the temp fixture, leave the source alone
        shutil.copy(FORT_COLLINS_MP, self.mp)
        errs = [e for e in self.errors() if e.startswith("market_pack: ")]
        self.assertEqual(errs, [])


class TestK2LeadDestination(K56bBase):
    def setUp(self):
        super().setUp()
        d = json.loads(self.intake.read_text(encoding="utf-8"))
        self.code = d["property_code"]
        self.assertEqual(self.code, "EXT")

    def set_ld(self, value, code=None):
        def plant(d):
            d["lead_destination"] = value
            if code is not None:
                d["property_code"] = code
        self.edit(self.intake, plant)

    def test_server_copy_reference_passes(self):
        self.set_ld("server-copy:FCI:LEAD_TO", code="FCI")
        self.assertEqual(self.errors(), [])

    def test_server_copy_reference_with_own_code_passes(self):
        self.set_ld("server-copy:EXT:LEAD_TO")
        self.assertEqual(self.errors(), [])

    def test_negatives_one_error_no_value_echoed(self):
        cases = {
            "lowercase code": ("server-copy:fci:LEAD_TO", "FCI"),
            "literal email": ("someone-real@example.invalid", "FCI"),
            "literal phone": ("+15555550199", "FCI"),
            "trailing newline": ("server-copy:FCI:LEAD_TO\n", "FCI"),
            "empty string": ("", "FCI"),
            "4-letter code": ("server-copy:FCIX:LEAD_TO", "FCI"),
            "lowercase lead_to": ("server-copy:FCI:lead_to", "FCI"),
            "mismatched code": ("server-copy:ABC:LEAD_TO", "FCI"),
        }
        for label, (value, code) in cases.items():
            with self.subTest(label):
                self.set_ld(value, code=code)
                errs = self.errors()
                self.assertEqual(len(errs), 1, errs)
                text = "\n".join(errs)
                for frag in {value, value.strip()} - {""}:
                    self.assertNotIn(frag, text)

    def test_mismatch_error_names_codes_only(self):
        self.set_ld("server-copy:ABC:LEAD_TO", code="FCI")
        errs = self.errors()
        self.assertIn("'ABC'", errs[0])
        self.assertIn("'FCI'", errs[0])
        self.assertNotIn("LEAD_TO", errs[0])

    def test_address_object_still_validates(self):
        d = json.loads(self.intake.read_text(encoding="utf-8"))
        self.assertIsInstance(d["lead_destination"], dict)
        self.assertEqual(self.errors(), [])


class TestK4PathHelpers(unittest.TestCase):
    def test_walk_strings_default_and_empty_string_path(self):
        doc = {"a": "x", "b": ["y"]}
        want = [(("a",), "x"), (("b", 0), "y")]
        self.assertEqual(list(VG._walk_strings(doc)), want)
        self.assertEqual(list(VG._walk_strings(doc, "")), want)
        self.assertEqual(list(VG._walk_strings(doc, ())), want)

    def test_walk_strings_str_path(self):
        self.assertEqual(list(VG._walk_strings({"a": "x"}, "root")), [(("root", "a"), "x")])

    def test_walk_strings_path_object(self):
        out = list(VG._walk_strings({"a": "x"}, Path("p")))
        self.assertEqual(out, [(("p", "a"), "x")])

    def test_walk_strings_list_path(self):
        out = list(VG._walk_strings({"a": "x"}, ["r", 1]))
        self.assertEqual(out, [(("r", 1, "a"), "x")])

    def test_walk_strings_bare_string_value(self):
        self.assertEqual(list(VG._walk_strings("s")), [((), "s")])

    def test_jpath_with_list(self):
        self.assertEqual(VF._jpath(["a", 0]), "$.a[0]")
        self.assertEqual(VF._jpath(("a", 0)), "$.a[0]")
        self.assertEqual(VF._jpath(""), "$")

    def test_as_path_tuple(self):
        f = VF._as_path_tuple
        self.assertEqual(f(("a", 1)), ("a", 1))
        self.assertEqual(f(["a", 1]), ("a", 1))
        self.assertEqual(f(""), ())
        self.assertEqual(f("x"), ("x",))
        self.assertEqual(f(Path("p")), ("p",))
        self.assertEqual(f(7), ("7",))


if __name__ == "__main__":
    unittest.main()
