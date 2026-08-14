import json
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import build_presets as mod


class ConverterTests(unittest.TestCase):
    def test_known_normalization(self):
        self.assertAlmostEqual(mod.normalize_gain(-20), 0.0)
        self.assertAlmostEqual(mod.normalize_gain(0), 0.5)
        self.assertAlmostEqual(mod.normalize_gain(20), 1.0)
        self.assertAlmostEqual(mod.normalize_frequency(16), 0.0)
        self.assertAlmostEqual(mod.normalize_frequency(20000), 1.0)
        self.assertAlmostEqual(mod.normalize_q(0.1), 0.0)
        self.assertAlmostEqual(mod.normalize_q(10), 1.0)

    def test_edition_xs_xml_shape(self):
        bands = [
            {"type": "peak_dip", "frequency": 70, "gain_db": -2.5, "q": 0.5},
            {"type": "low_shelf", "frequency": 105, "gain_db": 5.5, "q": 0.71},
        ]
        xml, warnings = mod.build_xml("Test", -5.4, bands)
        self.assertEqual(warnings, [])
        root = ET.fromstring(xml.split("?>", 1)[1])
        info = root.find("PresetInfo")
        self.assertEqual(info.attrib["TenBand"], "1")
        values = info.findall("Value")
        self.assertEqual(len(values), 66)
        self.assertEqual(values[2].text, "1")
        self.assertEqual(values[8].text, "1")
        self.assertEqual(values[62].text, "1")

    def test_uapp_name_sanitizes_unicode_bullet(self):
        self.assertEqual(mod.uapp_safe_name("RTINGS • Studio"), "RTINGS - Studio")

    def test_end_to_end_jsonl_selection(self):
        entries = [
            {"type": "vendor", "id": "hifiman", "data": {"name": "HIFIMAN"}},
            {"type": "vendor", "id": "simgot_audio", "data": {"name": "SIMGOT"}},
            {"type": "product", "id": "hifiman_edition_xs", "data": {"vendor_id": "hifiman", "name": "Edition XS", "type": "headphones", "subtype": "over_the_ear"}},
            {"type": "product", "id": "simgot_audio_ew300", "data": {"vendor_id": "simgot_audio", "name": "EW300", "type": "headphones", "subtype": "in_ear"}},
            {"type": "product", "id": "simgot_audio_ew300_dsp", "data": {"vendor_id": "simgot_audio", "name": "EW300 DSP", "type": "headphones", "subtype": "in_ear"}},
            {"type": "eq", "id": "hifiman_edition_xs_oratory", "data": {"product_id": "hifiman_edition_xs", "author": "oratory1990", "details": "Harman Target", "type": "parametric_eq", "parameters": {"gain_db": -5.4, "bands": [{"type": "peak_dip", "frequency": 70, "gain_db": -2.5, "q": 0.5}]}}},
            {"type": "eq", "id": "simgot_audio_ew300_gold", "data": {"product_id": "simgot_audio_ew300", "author": "AutoEQ", "details": "Measured by X (gold)", "type": "parametric_eq", "parameters": {"gain_db": -6, "bands": [{"type": "low_shelf", "frequency": 105, "gain_db": -3, "q": 0.7}]}}},
            {"type": "eq", "id": "simgot_audio_ew300_silver", "data": {"product_id": "simgot_audio_ew300", "author": "AutoEQ", "details": "Measured by X (silver)", "type": "parametric_eq", "parameters": {"gain_db": -4.9, "bands": [{"type": "high_shelf", "frequency": 10000, "gain_db": -3, "q": 0.7}]}}},
            {"type": "eq", "id": "simgot_audio_ew300_dsp_jaytiss", "data": {"product_id": "simgot_audio_ew300_dsp", "author": "AutoEQ", "details": "Measured by Jaytiss", "type": "parametric_eq", "parameters": {"gain_db": -5.5, "bands": [{"type": "peak_dip", "frequency": 6727, "gain_db": 5.5, "q": 1.81}]}}}
        ]
        config = {
            "targets": [
                {"vendor_id": "hifiman", "product_name": "Edition XS", "output_path": "HIFIMAN/Edition XS"},
                {"vendor_id": "simgot_audio", "product_name": "EW300", "include_terms": ["gold"], "output_path": "SIMGOT/EW300/Gold"},
                {"vendor_id": "simgot_audio", "product_name": "EW300", "include_terms": ["silver"], "output_path": "SIMGOT/EW300/Silver"},
                {"vendor_id": "simgot_audio", "product_name": "EW300 DSP", "output_path": "SIMGOT/EW300/DSP"},
            ]
        }
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            source = td / "db.jsonl"
            source.write_text("\n".join(json.dumps(x) for x in entries) + "\n")
            config_path = td / "targets.json"
            config_path.write_text(json.dumps(config))
            output = td / "output"
            manifest = mod.write_presets(str(source), config_path, output)
            self.assertEqual(manifest["preset_count"], 4)
            self.assertTrue((output / "HIFIMAN/Edition XS/oratory1990 - Harman Target.xml").exists())
            self.assertTrue((output / "SIMGOT/EW300/Gold/AutoEQ - Measured by X (gold).xml").exists())
            self.assertTrue((output / "SIMGOT/EW300/Silver/AutoEQ - Measured by X (silver).xml").exists())
            self.assertTrue((output / "SIMGOT/EW300/DSP/AutoEQ - Measured by Jaytiss.xml").exists())

    def test_duplicate_human_names_get_band_count_suffixes(self):
        bands5 = [{"type": "peak_dip", "frequency": 100 + i * 100, "gain_db": 0, "q": 1} for i in range(5)]
        bands10 = [{"type": "peak_dip", "frequency": 100 + i * 100, "gain_db": 0, "q": 1} for i in range(10)]
        entries = [
            {"type": "vendor", "id": "hifiman", "data": {"name": "HIFIMAN"}},
            {"type": "product", "id": "hifiman_edition_xs", "data": {"vendor_id": "hifiman", "name": "Edition XS", "type": "headphones", "subtype": "over_the_ear"}},
            {"type": "eq", "id": "hifiman:edition_xs::same_5band", "data": {"product_id": "hifiman_edition_xs", "author": "Rtings/AutoEQ", "details": "Target • Consolidated", "type": "parametric_eq", "parameters": {"gain_db": -4, "bands": bands5}}},
            {"type": "eq", "id": "hifiman:edition_xs::same_10band", "data": {"product_id": "hifiman_edition_xs", "author": "Rtings/AutoEQ", "details": "Target • Consolidated", "type": "parametric_eq", "parameters": {"gain_db": -4, "bands": bands10}}}
        ]
        config = {"targets": [{"vendor_id": "hifiman", "product_name": "Edition XS", "output_path": "HIFIMAN/Edition XS"}]}
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            source = td / "db.jsonl"
            source.write_text("\n".join(json.dumps(x) for x in entries) + "\n")
            config_path = td / "targets.json"
            config_path.write_text(json.dumps(config))
            output = td / "output"
            manifest = mod.write_presets(str(source), config_path, output)
            self.assertEqual(manifest["preset_count"], 2)
            self.assertTrue((output / "HIFIMAN/Edition XS/Rtings-AutoEQ - Target - Consolidated - 5 band.xml").exists())
            self.assertTrue((output / "HIFIMAN/Edition XS/Rtings-AutoEQ - Target - Consolidated - 10 band.xml").exists())

    def test_shared_output_targets_are_validated_independently(self):
        entries = [
            {"type": "vendor", "id": "sennheiser", "data": {"name": "Sennheiser"}},
            {"type": "product", "id": "sennheiser_hd_650", "data": {"vendor_id": "sennheiser", "name": "HD 650", "type": "headphones", "subtype": "over_the_ear"}},
            {"type": "eq", "id": "sennheiser:hd_650::autoeq_test", "data": {"product_id": "sennheiser_hd_650", "author": "AutoEQ", "details": "Measured by Test", "type": "parametric_eq", "parameters": {"gain_db": -5, "bands": [{"type": "peak_dip", "frequency": 1000, "gain_db": 0, "q": 1}]}}},
        ]
        config = {
            "targets": [
                {"vendor_id": "sennheiser", "product_name": "HD 650", "output_path": "Sennheiser/HD650"},
                {"vendor_id": "sennheiser", "product_name": "HD650", "output_path": "Sennheiser/HD650"},
            ]
        }
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            source = td / "db.jsonl"
            source.write_text("\n".join(json.dumps(x) for x in entries) + "\n")
            config_path = td / "targets.json"
            config_path.write_text(json.dumps(config))
            output = td / "output"
            with self.assertRaises(RuntimeError) as ctx:
                mod.write_presets(str(source), config_path, output)
            self.assertIn("sennheiser / HD650 -> Sennheiser/HD650", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
