import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import build_presets as mod


class SelectionApprovalTests(unittest.TestCase):
    @staticmethod
    def _eq(eq_id: str, product_id: str, details: str, frequency: int) -> dict:
        return {
            "type": "eq",
            "id": eq_id,
            "data": {
                "product_id": product_id,
                "author": "AutoEQ",
                "details": details,
                "type": "parametric_eq",
                "parameters": {
                    "gain_db": -4,
                    "bands": [
                        {
                            "type": "peak_dip",
                            "frequency": frequency,
                            "gain_db": 0,
                            "q": 1,
                        }
                    ],
                },
            },
        }

    def _write(self, entries: list[dict], config: dict):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        source = root / "db.jsonl"
        source.write_text("\n".join(json.dumps(entry) for entry in entries) + "\n", encoding="utf-8")
        config_path = root / "targets.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        return td, root, source, config_path

    def test_explicit_exclusion_is_accounted_for_without_weakening_coverage(self):
        entries = [
            {"type": "vendor", "id": "test", "data": {"name": "Test"}},
            {"type": "product", "id": "p1", "data": {"vendor_id": "test", "name": "Model"}},
            self._eq("test:model::one", "p1", "Measured by One", 1000),
            self._eq("test:model::two", "p1", "Measured by Two", 2000),
        ]
        config = {
            "targets": [
                {
                    "vendor_id": "test",
                    "product_name": "Model",
                    "exclude_eq_ids": ["test:model::two"],
                    "output_path": "Test/Model",
                }
            ]
        }
        td, root, source, config_path = self._write(entries, config)
        try:
            manifest = mod.write_presets(str(source), config_path, root / "output")
            self.assertEqual(manifest["preset_count"], 1)
            coverage = manifest["coverage"][0]
            self.assertEqual(coverage["mode"], "complete")
            self.assertEqual(coverage["explicitly_excluded_profiles"], ["test:model::two"])
            self.assertEqual(coverage["unmatched_profiles"], [])
            self.assertTrue((root / "output/Test/Model/Model - AutoEQ - One.xml").exists())
            self.assertFalse((root / "output/Test/Model/Model - AutoEQ - Two.xml").exists())
        finally:
            td.cleanup()

    def test_exact_selected_subset_stays_fixed_and_partial(self):
        entries = [
            {"type": "vendor", "id": "test", "data": {"name": "Test"}},
            {"type": "product", "id": "p1", "data": {"vendor_id": "test", "name": "Model"}},
            self._eq("test:model::one", "p1", "Measured by One", 1000),
            self._eq("test:model::two", "p1", "Measured by Two", 2000),
            self._eq("test:model::three", "p1", "Measured by Three", 3000),
        ]
        config = {
            "targets": [
                {
                    "vendor_id": "test",
                    "product_name": "Model",
                    "include_eq_ids": ["test:model::one", "test:model::three"],
                    "allow_partial": True,
                    "output_path": "Test/Model",
                }
            ]
        }
        td, root, source, config_path = self._write(entries, config)
        try:
            manifest = mod.write_presets(str(source), config_path, root / "output")
            self.assertEqual(manifest["preset_count"], 2)
            coverage = manifest["coverage"][0]
            self.assertEqual(coverage["mode"], "partial")
            self.assertEqual(coverage["explicitly_excluded_profiles"], [])
            self.assertEqual(coverage["unmatched_profiles"], ["test:model::two"])
        finally:
            td.cleanup()

    def test_excluded_exact_id_must_exist(self):
        entries = [
            {"type": "vendor", "id": "test", "data": {"name": "Test"}},
            {"type": "product", "id": "p1", "data": {"vendor_id": "test", "name": "Model"}},
            self._eq("test:model::one", "p1", "Measured by One", 1000),
        ]
        config = {
            "targets": [
                {
                    "vendor_id": "test",
                    "product_name": "Model",
                    "exclude_eq_ids": ["test:model::typo"],
                    "output_path": "Test/Model",
                }
            ]
        }
        td, root, source, config_path = self._write(entries, config)
        try:
            with self.assertRaises(RuntimeError) as ctx:
                mod.write_presets(str(source), config_path, root / "output")
            self.assertIn("exclude_eq_ids", str(ctx.exception))
            self.assertIn("test:model::typo", str(ctx.exception))
        finally:
            td.cleanup()

    def test_same_exact_id_cannot_be_included_and_excluded(self):
        entries = [
            {"type": "vendor", "id": "test", "data": {"name": "Test"}},
            {"type": "product", "id": "p1", "data": {"vendor_id": "test", "name": "Model"}},
            self._eq("test:model::one", "p1", "Measured by One", 1000),
        ]
        config = {
            "targets": [
                {
                    "vendor_id": "test",
                    "product_name": "Model",
                    "include_eq_ids": ["test:model::one"],
                    "exclude_eq_ids": ["test:model::one"],
                    "output_path": "Test/Model",
                }
            ]
        }
        td, root, source, config_path = self._write(entries, config)
        try:
            with self.assertRaises(ValueError) as ctx:
                mod.write_presets(str(source), config_path, root / "output")
            self.assertIn("includes and excludes the same OPRA EQ ID", str(ctx.exception))
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
