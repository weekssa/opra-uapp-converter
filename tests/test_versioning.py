import unittest

from src.update_version import bump_version, parse_version


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


if __name__ == "__main__":
    unittest.main()
