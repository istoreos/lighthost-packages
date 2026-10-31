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

    def test_component_inputs_use_exact_public_release_tags(self):
        expected = {
            "lighthost/Makefile": (
                "lighthost-v0.3.0-r87",
                "lighthost-$(PKG_VERSION)-r87-x86_64.tar.gz",
                "d7109a24e98dc92441566c828d2c2ed5c1b82738e178098d3a0a1a98003cbc00",
            ),
            "lighthost-ui/Makefile": (
                "lighthost-ui-v0.3.0-r87.1",
                "lighthost-ui-$(PKG_VERSION)-r87.1-x86_64.tar.gz",
                "587c27007bf372d6d2c5ae862dd60cba5124823e8e61d9f94af773c247bfb00c",
            ),
            "lighthost-spice-console/Makefile": (
                "lighthost-spice-console-v0.3.0-r87",
                "lighthost-spice-console-$(PKG_VERSION)-r87-x86_64.tar.gz",
                "d1196189dc0bc46eaa25677ee93d99aacc302c953ceda7f39def3a03e2c0f6db",
            ),
            "incus/Makefile": (
                "incus-v6.0.6-lighthost.3-r3",
                "incus-$(PKG_VERSION)-lighthost.3-r3-x86_64.tar.gz",
                "3dcb9c140d31f601c5f7ca89ade7659cdd8b028355658a03dc1b8d6e7b00bbc8",
            ),
            "qemu-firmware/Makefile": (
                "lighthost-qemu-firmware-v202302-r2",
                "$(PKG_NAME)-$(PKG_VERSION)-r2-x86_64.tar.gz",
                "2f4ae7144fa1610bcd3655b4704532088c783bf9910601438a6d929be066dd47",
            ),
        }
        for path, (tag, source, digest) in expected.items():
            makefile = text(path)
            self.assertIn(
                f"PKG_SOURCE_URL:=https://github.com/istoreos/lighthost-packages/releases/download/{tag}/",
                makefile,
            )
            self.assertIn(f"PKG_SOURCE:={source}", makefile)
            self.assertIn(f"PKG_HASH:={digest}", makefile)
            self.assertNotIn("istorework-packages", makefile)
            self.assertNotIn("/latest/", makefile)


if __name__ == "__main__":
    unittest.main()

