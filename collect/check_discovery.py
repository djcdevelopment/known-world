"""Focused privacy/coverage checks for the evidence hunter; no model calls or renders."""
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent / "knownworld"))
from discover import scan, validate_output
from probe_evidence import probe


class DiscoveryChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="kw-discovery-")
        self.root = Path(self.temp.name)
        self.spec = dict(id="fixture", host="fixture", path=str(self.root), group="lab", depth=3,
                         seconds=2, max_files=100, max_candidates=50)

    def tearDown(self):
        self.temp.cleanup()

    def test_scan_never_opens_source_and_excludes_credentials_and_symlinks(self):
        (self.root / "result.json").write_text('{"text":"PRIVATE_CANARY"}')
        (self.root / "auth.json").write_text("CREDENTIAL_CANARY")
        (self.root / "models").mkdir()
        (self.root / "models" / "result.json").write_text("MODEL_CANARY")
        (self.root / "linked").symlink_to(self.root / "models", target_is_directory=True)
        with patch("builtins.open", side_effect=AssertionError("Source opened")):
            result = scan(self.spec)
        self.assertEqual(result["counts"]["files"], 1)
        self.assertEqual(result["counts"]["symlinks_excluded"], 1)
        self.assertNotIn("CANARY", json.dumps(result))

    def test_budget_and_missing_are_not_complete(self):
        (self.root / "result.json").write_text("{}")
        self.assertEqual(scan(dict(self.spec, seconds=0))["status"], "partial")
        capped = scan(dict(self.spec, max_candidates=0))
        self.assertEqual(capped["status"], "partial")
        self.assertIn("candidate_budget", capped["gaps"])
        self.assertEqual(scan(dict(self.spec, path=str(self.root / "missing")))["status"], "missing")

    def test_output_cannot_escape_or_target_immutable_directory(self):
        with self.assertRaises(ValueError):
            validate_output(self.root / "output")
        with self.assertRaises(ValueError):
            validate_output(Path(__file__).resolve().parents[1] / "runs" / "output")

    def test_json_shape_does_not_emit_values_or_descend_into_bodies(self):
        p = self.root / "result.json"
        p.write_text(json.dumps({"job_id": "PRIVATE_CANARY", "prompt": {"PRIVATE_CANARY": 4},
                                "metrics": {"tokens_out": 5}, "auth": {"credential": "PRIVATE_CANARY"}}))
        result = probe(dict(id="json", path=str(p)), [self.root])
        self.assertEqual(result["status"], "complete")
        self.assertNotIn("CANARY", json.dumps(result))
        self.assertEqual(result["shape"]["prompt"], "dict")
        self.assertEqual(result["shape"]["metrics"]["tokens_out"], "int")

    def test_sqlite_counts_without_emitting_rows_and_refuses_credential_path(self):
        p = self.root / "history.db"
        c = sqlite3.connect(p)
        c.execute("CREATE TABLE steps (idx INTEGER, step_payload BLOB)")
        c.execute("INSERT INTO steps VALUES (1, ?)", (b"PRIVATE_CANARY",))
        c.commit(); c.close()
        result = probe(dict(id="db", path=str(p)), [self.root])
        self.assertEqual(result["tables"][0]["rows"], 1)
        self.assertNotIn("CANARY", json.dumps(result))
        secret = self.root / "credentials.json"
        secret.write_text("CREDENTIAL_CANARY")
        self.assertEqual(probe(dict(id="secret", path=str(secret)), [self.root])["status"], "refused")


if __name__ == "__main__":
    unittest.main()
