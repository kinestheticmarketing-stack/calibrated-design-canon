"""K51 row 8: tests for validate_genesis.py, driven against the Exampleton
FIXTURE (ops/genesis/fixtures/exampleton/). Stdlib unittest only; every test
works on a temp copy of the fixture (removed in tearDown). The fixture on disk
is never modified. Each defect test plants exactly one defect and asserts the
EXACT error count from validate() and CLI exit code 1.

Run (from canon root):
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest ops/genesis/test_genesis.py -v
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

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

GENESIS = Path(__file__).resolve().parent
VALIDATOR = GENESIS / "validate_genesis.py"
FIXTURE = GENESIS / "fixtures" / "exampleton"
INTAKE_SCHEMA = GENESIS / "intake.schema.json"
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")

# ROW 0 result: union of DCI/LGM/GCI SERVICE_SLUG_TO_URL keys (27 slugs).
ROW0_SERVICES = [
    "air-sealing", "attic", "basement", "blower-door-test", "blown-in",
    "builders-contractors", "cathedral-ceiling", "cellulose", "crawl-space",
    "dense-pack-cellulose", "duct", "duct-sealing", "energy-audit",
    "fiberglass-batt", "garage", "hybrid-flash-batt", "knob-and-tube",
    "new-construction", "radiant-barrier", "removal", "rim-joist",
    "rodent-damaged", "rodent-remediation", "spray-foam",
    "vermiculite-abatement", "vermiculite-asbestos-removal", "wall",
]

_spec = importlib.util.spec_from_file_location("k51t_validate_genesis", VALIDATOR)
VG = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(VG)


class GenesisTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="k51_genesis_"))
        self.root = self.tmp / "exampleton"
        shutil.copytree(FIXTURE, self.root)
        self.intake = self.root / "intake.json"
        self.mp = self.root / "market_pack.json"
        self.registry = self.root / "facts" / "registry.json"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # helpers
    def load(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    def save(self, path, data):
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def edit(self, path, fn):
        data = self.load(path)
        fn(data)
        self.save(path, data)

    def errors(self):
        return VG.validate(self.intake, self.mp, self.registry)

    def cli(self):
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(self.intake), str(self.mp), str(self.registry)],
            capture_output=True, text=True, env=ENV)

    def assert_one_defect(self, n=1):
        errs = self.errors()
        self.assertEqual(len(errs), n, errs)
        r = self.cli()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        return errs, r

    # tests
    def test_clean_exampleton_passes(self):
        self.assertEqual(self.errors(), [])
        r = self.cli()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_missing_tracking_phone(self):
        self.edit(self.intake, lambda d: d.pop("tracking_phone"))
        errs, _ = self.assert_one_defect()
        self.assertTrue(errs[0].startswith("intake: "), errs)

    def test_service_not_in_enum(self):
        self.edit(self.intake, lambda d: d["services"].append("gutter-cleaning"))
        errs, _ = self.assert_one_defect()
        self.assertTrue(errs[0].startswith("intake: "), errs)

    def test_town_without_facts_key(self):
        def plant(d):
            d["towns"][0]["facts_keys"] = []
        self.edit(self.mp, plant)
        errs, _ = self.assert_one_defect()
        self.assertTrue(errs[0].startswith("market_pack: "), errs)

    def test_facts_key_not_in_registry(self):
        def plant(d):
            d["programs"][0]["facts_key"] = "ext-no-such-fact"
        self.edit(self.mp, plant)
        errs, _ = self.assert_one_defect()
        self.assertTrue(errs[0].startswith("xref: "), errs)
        self.assertIn("ext-no-such-fact", errs[0])

    def test_territory_state_disagrees(self):
        def plant(d):
            t = d["towns"][1]
            self.assertEqual(t["name"], "North Exampleton (FIXTURE)")
            t["territory_state"] = "NAMED"
        self.edit(self.mp, plant)
        errs, _ = self.assert_one_defect()
        self.assertTrue(errs[0].startswith("xref: "), errs)
        self.assertIn("ext-utility-territory", errs[0])

    def test_sendgrid_shaped_intake_value(self):
        # Built at runtime so no secret-shaped literal sits in this file.
        value = "SG." + ("aB3dE5gH7jK9mN1pQ2rS4t"[:22]) + "." + (
            "Xy7Zw6Vu5Ts4Rq3Po2Nm1Lk0Ji9Hg8Fe7Dc6Ba5Zz4Yy"[:43])
        self.assertEqual(len(value), 3 + 22 + 1 + 43)
        self.edit(self.intake, lambda d: d.__setitem__("launch_notes", value))
        errs, r = self.assert_one_defect()
        self.assertTrue(errs[0].startswith("secret: intake:"), errs)
        for e in errs:
            self.assertNotIn(value, e)
            self.assertNotIn(value[3:25], e)
        self.assertNotIn(value, r.stdout + r.stderr)
        self.assertNotIn(value[3:25], r.stdout + r.stderr)

    def test_program_dollar_field(self):
        self.edit(self.mp, lambda d: d["programs"][0].__setitem__("amount_usd", 500))
        errs, _ = self.assert_one_defect()
        self.assertTrue(errs[0].startswith("market_pack: "), errs)

    def test_unreadable_exit_2(self):
        self.intake.write_text("{ this is not json", encoding="utf-8")
        with self.assertRaises(VG.GenesisUnreadable):
            self.errors()
        r = self.cli()
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    def test_services_enum_matches_row0(self):
        schema = self.load(INTAKE_SCHEMA)
        enum = schema["properties"]["services"]["items"]["enum"]
        self.assertEqual(len(ROW0_SERVICES), 27)
        self.assertEqual(enum, ROW0_SERVICES)


if __name__ == "__main__":
    unittest.main()
