import argparse
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts/release"

validator_spec = importlib.util.spec_from_file_location("validate_release_metadata", SCRIPTS / "validate_release_metadata.py")
validator = importlib.util.module_from_spec(validator_spec)
assert validator_spec.loader is not None
validator_spec.loader.exec_module(validator)
import sys
sys.modules["validate_release_metadata"] = validator

release_spec = importlib.util.spec_from_file_location("component_release", SCRIPTS / "component_release.py")
release = importlib.util.module_from_spec(release_spec)
assert release_spec.loader is not None
release_spec.loader.exec_module(release)


class ComponentReleaseTests(unittest.TestCase):
    def prepare(self, directory: Path):
        asset = directory / "lighthost-ui_0.3.0-r87.1_x86_64.ipk"
        asset.write_bytes(b"package")
        output = directory / "manifest.json"
        args = argparse.Namespace(
            output=output,
            asset=[("package", asset)],
            component="lighthost-ui",
            tag="lighthost-ui-v0.3.0-r87.1",
            component_version="0.3.0",
            package_version="0.3.0-r87.1",
            package_release="87.1",
            program_version=None,
            source_repository="linkease/linkease-lighthost",
            source_commit="1" * 40,
            source_path=["frontend"],
            feed_commit="2" * 40,
            feed_path=["lighthost-ui"],
            architecture="x86_64",
            libc="musl",
            platform="istoreos-24.10",
        )
        return output, asset, release.prepare(args)

    def test_prepare_and_verify(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            manifest, _, value = self.prepare(directory)
            self.assertEqual(value["component"], "lighthost-ui")
            result = release.verify(argparse.Namespace(manifest=manifest, asset_dir=directory))
            self.assertEqual(result["status"], "PASS_COMPONENT_ASSETS")

    def test_prepare_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            manifest, _, _ = self.prepare(directory)
            with self.assertRaises(FileExistsError):
                self.prepare(directory)

    def test_verify_rejects_changed_asset(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            manifest, asset, _ = self.prepare(directory)
            asset.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "identity"):
                release.verify(argparse.Namespace(manifest=manifest, asset_dir=directory))

    def test_publish_dry_run_has_no_remote_calls(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            manifest, _, _ = self.prepare(directory)
            result = release.publish(argparse.Namespace(
                manifest=manifest,
                asset_dir=directory,
                repository=release.REPOSITORY,
                execute=False,
            ))
            self.assertEqual(result["status"], "DRY_RUN")
            self.assertTrue(result["draft"])

    def test_publish_rejects_wrong_repository(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            manifest, _, _ = self.prepare(directory)
            with self.assertRaisesRegex(ValueError, "restricted"):
                release.publish(argparse.Namespace(
                    manifest=manifest,
                    asset_dir=directory,
                    repository="istoreos/istorework-packages",
                    execute=False,
                ))

    def test_ui_change_affects_only_ui(self):
        result = release.plan(argparse.Namespace(
            definitions=ROOT / "release/model/components.json",
            source_repository="linkease/linkease-lighthost",
            source_changed=["frontend/src/main.tsx"],
            feed_changed=[],
        ))
        self.assertEqual(result["components"], ["lighthost-ui"])

    def test_incus_patch_affects_only_incus(self):
        result = release.plan(argparse.Namespace(
            definitions=ROOT / "release/model/components.json",
            source_repository="linkease/linkease-lighthost",
            source_changed=[],
            feed_changed=["incus/patches/030.patch"],
        ))
        self.assertEqual(result["components"], ["incus"])

    def test_core_change_does_not_affect_ui(self):
        result = release.plan(argparse.Namespace(
            definitions=ROOT / "release/model/components.json",
            source_repository="linkease/linkease-lighthost",
            source_changed=["backend/cmd/lighthost/main.go"],
            feed_changed=[],
        ))
        self.assertEqual(result["components"], ["lighthost"])


if __name__ == "__main__":
    unittest.main()

