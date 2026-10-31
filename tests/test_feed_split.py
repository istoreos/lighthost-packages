from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


def text(path):
    return (ROOT / path).read_text()


class FeedSplitTests(unittest.TestCase):
    def test_each_recipe_builds_only_its_package(self):
        expected = {
            "lighthost/Makefile": ["lighthost"],
            "lighthost-ui/Makefile": ["lighthost-ui"],
            "lighthost-spice-console/Makefile": ["lighthost-spice-console"],
        }
        for path, packages in expected.items():
            found = re.findall(r"\$\(eval \$\(call BuildPackage,([^)]+)\)\)", text(path))
            self.assertEqual(found, packages, path)

    def test_core_has_no_ui_or_console_payload(self):
        makefile = text("lighthost/Makefile")
        self.assertNotIn("frontend-dist", makefile)
        self.assertNotIn("spice-console", makefile)
        self.assertNotIn("lighthost-plugin.json", makefile)

    def test_ui_contract_is_preserved(self):
        makefile = text("lighthost-ui/Makefile")
        self.assertIn("DEPENDS:=+lighthost +lighthost-spice-console +linkeasefull", makefile)
        self.assertIn("/usr/share/lighthost/www", makefile)
        self.assertIn("25-lighthost-plugin.json", makefile)
        self.assertTrue((ROOT / "lighthost-ui/files/lighthost-plugin.json").is_file())
        self.assertTrue((ROOT / "lighthost-ui/files/logo.svg").is_file())

    def test_console_contract_is_preserved(self):
        makefile = text("lighthost-spice-console/Makefile")
        self.assertIn("DEPENDS:=+lighthost", makefile)
        self.assertIn("/usr/share/lighthost/www/spice-console", makefile)
        self.assertIn("GPL-3.0-or-later LGPL-3.0-or-later", makefile)

    def test_six_public_packages_remain_defined(self):
        makefiles = [text(path) for path in (
            "lighthost/Makefile",
            "lighthost-ui/Makefile",
            "lighthost-spice-console/Makefile",
            "incus/Makefile",
            "qemu-firmware/Makefile",
        )]
        definitions = set(re.findall(r"^define Package/([^/\n]+)$", "\n".join(makefiles), re.M))
        self.assertTrue({
            "lighthost", "lighthost-ui", "lighthost-spice-console",
            "incus", "incus-agent", "lighthost-qemu-firmware",
        } <= definitions)


if __name__ == "__main__":
    unittest.main()

