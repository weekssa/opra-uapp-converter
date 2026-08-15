import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DocumentationSafeguardTests(unittest.TestCase):
    def test_project_bootstrap_fits_chatgpt_project_limit(self):
        path = ROOT / "docs/CHATGPT_PROJECT_INSTRUCTIONS.md"
        text = path.read_text(encoding="utf-8")
        self.assertLess(
            len(text),
            8000,
            "Paste-ready ChatGPT Project Instructions must remain below 8000 characters.",
        )
        self.assertLess(
            len(text.encode("utf-8")),
            8000,
            "Paste-ready instructions must also remain below 8000 UTF-8 bytes for margin/safety.",
        )
        required = [
            "docs/CHATGPT_MAINTENANCE_RUNBOOK.md",
            "GitHub search is discovery-only",
            "database/vendors/<vendor_id>/products/<product_folder>/eq/",
            "database_v1.jsonl",
            "STOP before approval/config changes",
            "Import all",
            "Import only",
            "Import all except",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_detailed_runbook_requires_authoritative_eq_inventory(self):
        text = (ROOT / "docs/CHATGPT_MAINTENANCE_RUNBOOK.md").read_text(encoding="utf-8")
        required = [
            "GitHub search is discovery-only",
            "database/vendors/<vendor_id>/products/<product_folder>/eq/",
            "database_v1.jsonl",
            "Stop before editing `config/targets.json`",
            "Similar-product safeguard",
            "Import all except selected EQs",
            "exclude_eq_ids",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_user_docs_repeat_inventory_verification_gate(self):
        docs = [
            ROOT / "README.md",
            ROOT / "docs/ADDING_HEADPHONES.md",
            ROOT / "docs/AUTOMATION.md",
            ROOT / "docs/NEW_USER_SETUP.md",
        ]
        for path in docs:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("database_v1.jsonl", text)
                self.assertIn("eq/", text)
                self.assertIn("GitHub search", text)

    def test_public_onboarding_distinguishes_download_and_fork_paths(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for phrase in [
            "No fork is required",
            "Fork the repository first",
            "docs/COPY_PASTE_SETUP.md",
        ]:
            with self.subTest(document="README.md", phrase=phrase):
                self.assertIn(phrase, readme)

        setup = (ROOT / "docs/COPY_PASTE_SETUP.md").read_text(encoding="utf-8")
        for phrase in [
            "Path A — I only want the presets that are already published",
            "Path B — I want my own automatically maintained headphone library",
            "YOUR_GITHUB_USERNAME/opra-uapp-converter",
            "OPRA UAPP Presets",
            "Set up and verify my OPRA UAPP preset project",
            "Add the FiiO FT1 to my presets",
        ]:
            with self.subTest(document="COPY_PASTE_SETUP.md", phrase=phrase):
                self.assertIn(phrase, setup)


if __name__ == "__main__":
    unittest.main()
