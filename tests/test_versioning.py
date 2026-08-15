import unittest
from pathlib import Path

from src.update_version import bump_version, parse_version


ROOT = Path(__file__).resolve().parents[1]


class VersioningTests(unittest.TestCase):
    def test_parse_version(self):
        self.assertEqual(parse_version("1.2.3"), (1, 2, 3))

    def test_rejects_non_semver_version(self):
        with self.assertRaises(ValueError):
            parse_version("v1.2")

    def test_patch_bump(self):
        self.assertEqual(bump_version("1.2.3", "patch"), "1.2.4")

    def test_minor_bump_resets_patch(self):
        self.assertEqual(bump_version("1.2.3", "minor"), "1.3.0")

    def test_major_bump_resets_minor_and_patch(self):
        self.assertEqual(bump_version("1.2.3", "major"), "2.0.0")

    def test_release_workflow_is_wired_to_version(self):
        workflow = (ROOT / ".github/workflows/update-presets.yml").read_text(encoding="utf-8")
        required = [
            '- "VERSION"',
            'git tag -a "$tag"',
            'gh release create "$tag"',
            '--generate-notes',
            'sha256sum "$archive"',
            'output/manifest.json#Preset manifest',
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, workflow)

    def test_release_behavior_is_documented(self):
        docs = [
            ROOT / "README.md",
            ROOT / "docs/AUTOMATION.md",
            ROOT / "docs/ADDING_HEADPHONES.md",
            ROOT / "docs/CHATGPT_PROJECT_INSTRUCTIONS.md",
        ]
        for path in docs:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("GitHub Release", text)


if __name__ == "__main__":
    unittest.main()
