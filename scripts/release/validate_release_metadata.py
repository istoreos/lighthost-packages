#!/usr/bin/env python3
"""Validate LightHost component manifests, release sets and legacy inventory."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


COMPONENTS = {
    "lighthost": "lighthost-v",
    "lighthost-ui": "lighthost-ui-v",
    "lighthost-spice-console": "lighthost-spice-console-v",
    "incus": "incus-v",
    "lighthost-qemu-firmware": "lighthost-qemu-firmware-v",
}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
PACKAGE_RELEASE = re.compile(r"^[0-9]+(?:\.[0-9]+)?$")


class InvalidMetadata(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InvalidMetadata(message)


def load(path: Path) -> dict:
    value = json.loads(path.read_text())
    require(isinstance(value, dict), f"{path}: root must be an object")
    return value


def validate_component(value: dict) -> None:
    component = value.get("component")
    require(value.get("schemaVersion") == 1, "component schemaVersion must be 1")
    require(component in COMPONENTS, "unknown component")
    require(value.get("repository") == "istoreos/lighthost-packages", "wrong release repository")
    tag = value.get("tag", "")
    require(tag.startswith(COMPONENTS[component]), "tag does not match component prefix")

    version = value.get("version", {})
    for key in ("componentVersion", "packageVersion", "packageRelease"):
        require(isinstance(version.get(key), str) and version[key], f"missing version.{key}")
    require(PACKAGE_RELEASE.fullmatch(version["packageRelease"]) is not None, "invalid packageRelease")
    if component == "incus":
        require(isinstance(version.get("programVersion"), str) and version["programVersion"], "Incus programVersion is required")

    source = value.get("source", {})
    require(source.get("state") == "COMMITTED", "worktree source is forbidden")
    require(COMMIT.fullmatch(source.get("commit", "")) is not None, "invalid source commit")
    require(isinstance(source.get("repository"), str) and source["repository"], "missing source repository")
    require(isinstance(source.get("paths"), list) and source["paths"], "missing source paths")

    feed = value.get("feed", {})
    require(COMMIT.fullmatch(feed.get("commit", "")) is not None, "invalid feed commit")
    require(isinstance(feed.get("paths"), list) and feed["paths"], "missing feed paths")

    target = value.get("target", {})
    for key in ("architecture", "libc", "platform"):
        require(isinstance(target.get(key), str) and target[key], f"missing target.{key}")

    assets = value.get("assets")
    require(isinstance(assets, list) and assets, "assets must not be empty")
    names: set[str] = set()
    for asset in assets:
        name = asset.get("name")
        require(isinstance(name, str) and name and name not in names, "asset names must be unique")
        names.add(name)
        require(isinstance(asset.get("size"), int) and asset["size"] > 0, f"{name}: invalid size")
        require(SHA256.fullmatch(asset.get("sha256", "")) is not None, f"{name}: invalid sha256")
        require(asset.get("role") in {"build-input", "package", "source-offer", "build-info", "checksums", "license", "sbom"}, f"{name}: invalid role")


def validate_release_set(value: dict) -> None:
    require(value.get("schemaVersion") == 1, "release-set schemaVersion must be 1")
    require(isinstance(value.get("releaseSet"), str) and value["releaseSet"], "missing releaseSet")
    components = value.get("components", {})
    require(set(components) == set(COMPONENTS), "release-set must contain exactly five components")
    for component, binding in components.items():
        require(binding.get("tag", "").startswith(COMPONENTS[component]), f"{component}: wrong tag")
        require(SHA256.fullmatch(binding.get("manifestSha256", "")) is not None, f"{component}: invalid manifest sha256")
    qualification = value.get("qualification", {})
    require(qualification.get("state") in {"NOT_RUN", "PRERELEASE_PASS", "STABLE_PASS"}, "invalid qualification state")
    require(isinstance(qualification.get("evidence"), list), "qualification evidence must be a list")


def validate_legacy(value: dict) -> None:
    require(value.get("schemaVersion") == 1, "legacy schemaVersion must be 1")
    assets = value.get("assets")
    require(isinstance(assets, list), "legacy assets must be a list")
    require(value.get("uploadedAssetCount") == len(assets) == 15, "legacy inventory must contain 15 uploaded assets")
    automatic = value.get("automaticRepositoryArchives")
    require(isinstance(automatic, list) and len(automatic) == 2, "legacy inventory must record two automatic source archives")
    require(value.get("githubDisplayedAssetCount") == len(assets) + len(automatic) == 17, "legacy displayed asset count must be 17")
    names = [asset.get("name") for asset in assets]
    require(len(names) == len(set(names)), "legacy assets must be unique")
    allowed = set(COMPONENTS) | {"release-set-evidence", "legacy-mixed-product-input"}
    for asset in assets:
        require(asset.get("owner") in allowed, f"{asset.get('name')}: invalid owner")
        require(isinstance(asset.get("size"), int) and asset["size"] > 0, f"{asset.get('name')}: invalid size")
        require(SHA256.fullmatch(asset.get("sha256", "")) is not None, f"{asset.get('name')}: invalid sha256")
        if asset.get("owner") == "legacy-mixed-product-input":
            require(set(asset.get("legacyComponents", [])) == {"lighthost", "lighthost-ui", "lighthost-spice-console"}, "legacy mixed input components are incomplete")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("component", "release-set", "legacy"))
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    value = load(args.path)
    {"component": validate_component, "release-set": validate_release_set, "legacy": validate_legacy}[args.kind](value)
    print(json.dumps({"status": "PASS", "kind": args.kind, "path": str(args.path)}))


if __name__ == "__main__":
    main()

