import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_release_metadata", ROOT / "scripts/release/validate_release_metadata.py"
)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)


def component():
    return {
        "schemaVersion": 1,
        "component": "lighthost-ui",
        "repository": "istoreos/lighthost-packages",
        "tag": "lighthost-ui-v0.3.0-r87.1",
        "version": {
            "componentVersion": "0.3.0",
            "packageVersion": "0.3.0-r87.1",
            "packageRelease": "87.1",
        },
        "source": {
            "repository": "linkease/linkease-lighthost",
            "commit": "1" * 40,
            "state": "COMMITTED",
            "paths": ["frontend"],
        },
        "feed": {"commit": "2" * 40, "paths": ["lighthost-ui"]},
        "target": {"architecture": "x86_64", "libc": "musl", "platform": "istoreos-24.10"},
        "assets": [{"name": "ui.ipk", "role": "package", "size": 1, "sha256": "3" * 64}],
    }


class ComponentTests(unittest.TestCase):
    def test_valid_component(self):
        validator.validate_component(component())

    def test_rejects_worktree_source(self):
        value = component()
        value["source"]["state"] = "WORKTREE_SNAPSHOT"
        with self.assertRaisesRegex(validator.InvalidMetadata, "worktree"):
            validator.validate_component(value)

    def test_rejects_missing_hash(self):
        value = component()
        del value["assets"][0]["sha256"]
        with self.assertRaisesRegex(validator.InvalidMetadata, "sha256"):
            validator.validate_component(value)

    def test_rejects_wrong_tag_prefix(self):
        value = component()
        value["tag"] = "lighthost-v0.3.0-r87.1"
        with self.assertRaisesRegex(validator.InvalidMetadata, "prefix"):
            validator.validate_component(value)

    def test_incus_requires_program_version(self):
        value = component()
        value["component"] = "incus"
        value["tag"] = "incus-v6.0.6-r7"
        with self.assertRaisesRegex(validator.InvalidMetadata, "programVersion"):
            validator.validate_component(value)


class ReleaseSetTests(unittest.TestCase):
    def setUp(self):
        definitions = json.loads((ROOT / "release/model/components.json").read_text())["components"]
        self.value = {
            "schemaVersion": 1,
            "releaseSet": "test",
            "target": {"architecture": "x86_64", "libc": "musl", "platform": "istoreos-24.10"},
            "components": {
                name: {"tag": data["tagPrefix"] + "test", "manifestSha256": "4" * 64}
                for name, data in definitions.items()
            },
            "qualification": {"state": "NOT_RUN", "evidence": []},
        }

    def test_valid_release_set(self):
        validator.validate_release_set(self.value)

    def test_rejects_missing_component(self):
        del self.value["components"]["incus"]
        with self.assertRaisesRegex(validator.InvalidMetadata, "five"):
            validator.validate_release_set(self.value)


class LegacyInventoryTests(unittest.TestCase):
    def test_inventory_is_complete_and_unique(self):
        value = json.loads((ROOT / "release/model/legacy-istorework-packages-20261014.json").read_text())
        validator.validate_legacy(value)

    def test_rejects_duplicate_asset(self):
        value = json.loads((ROOT / "release/model/legacy-istorework-packages-20261014.json").read_text())
        value["assets"][-1] = copy.deepcopy(value["assets"][0])
        with self.assertRaisesRegex(validator.InvalidMetadata, "unique"):
            validator.validate_legacy(value)


if __name__ == "__main__":
    unittest.main()

