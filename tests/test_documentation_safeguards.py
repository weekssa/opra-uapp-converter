import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DocumentationSafeguardTests(unittest.TestCase):
    def test_chatgpt_instructions_require_authoritative_eq_inventory(self):
        text = (ROOT / "docs/CHATGPT_PROJECT_INSTRUCTIONS.md").read_text(encoding="utf-8")
        required = [
            "GitHub search is discovery-only",
            "database/vendors/<vendor_id>/products/<product_folder>/eq/",
            "database_v1.jsonl",
            "Do not use GitHub code-search results to count EQ profiles",
            "Stop before editing config",
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


if __name__ == "__main__":
    unittest.main()
