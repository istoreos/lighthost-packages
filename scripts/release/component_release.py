#!/usr/bin/env python3
"""Prepare, verify, plan and publish LightHost component releases."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request

import validate_release_metadata as metadata


REPOSITORY = "istoreos/lighthost-packages"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def refuse_existing(path: Path) -> None:
    if path.exists():
        raise FileExistsError(path)


def parse_asset(value: str) -> tuple[str, Path]:
    try:
        role, name = value.split("=", 1)
    except ValueError as error:
        raise argparse.ArgumentTypeError("asset must be ROLE=PATH") from error
    path = Path(name).resolve()
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"asset is not a file: {path}")
    return role, path


def prepare(args: argparse.Namespace) -> dict:
    refuse_existing(args.output)
    assets = []
    names = set()
    for role, path in args.asset:
        if path.name in names:
            raise ValueError(f"duplicate asset name: {path.name}")
        names.add(path.name)
        assets.append({"name": path.name, "role": role, "size": path.stat().st_size, "sha256": sha256(path)})
    version = {
        "componentVersion": args.component_version,
        "packageVersion": args.package_version,
        "packageRelease": args.package_release,
    }
    if args.program_version:
        version["programVersion"] = args.program_version
    value = {
        "schemaVersion": 1,
        "component": args.component,
        "repository": REPOSITORY,
        "tag": args.tag,
        "version": version,
        "source": {
            "repository": args.source_repository,
            "commit": args.source_commit,
            "state": "COMMITTED",
            "paths": args.source_path,
        },
        "feed": {"commit": args.feed_commit, "paths": args.feed_path},
        "target": {"architecture": args.architecture, "libc": args.libc, "platform": args.platform},
        "assets": assets,
    }
    metadata.validate_component(value)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(value, indent=2) + "\n")
    return value


def load_manifest(path: Path) -> dict:
    value = metadata.load(path)
    metadata.validate_component(value)
    return value


def verify_assets(value: dict, asset_dir: Path) -> dict:
    verified = []
    for asset in value["assets"]:
        path = asset_dir / asset["name"]
        if not path.is_file():
            raise FileNotFoundError(path)
        actual = {"size": path.stat().st_size, "sha256": sha256(path)}
        if actual != {"size": asset["size"], "sha256": asset["sha256"]}:
            raise ValueError(f"asset identity mismatch: {asset['name']}")
        verified.append(asset["name"])
    return {"status": "PASS_COMPONENT_ASSETS", "component": value["component"], "tag": value["tag"], "assets": verified}


def verify(args: argparse.Namespace) -> dict:
    return verify_assets(load_manifest(args.manifest), args.asset_dir.resolve())


def definitions(path: Path) -> dict:
    value = json.loads(path.read_text())
    if value.get("releaseRepository") != REPOSITORY:
        raise ValueError("component definitions target the wrong repository")
    if set(value.get("components", {})) != set(metadata.COMPONENTS):
        raise ValueError("component definitions must contain exactly five components")
    return value["components"]


def path_matches(changed: str, root: str) -> bool:
    normalized = changed.strip("/")
    prefix = root.strip("/")
    return prefix == "." or normalized == prefix or normalized.startswith(prefix + "/")


def plan(args: argparse.Namespace) -> dict:
    result = set()
    for component, definition in definitions(args.definitions).items():
        if definition["sourceRepository"] == args.source_repository and any(
            path_matches(changed, root)
            for changed in args.source_changed
            for root in definition["sourcePaths"]
        ):
            result.add(component)
        if any(path_matches(changed, root) for changed in args.feed_changed for root in definition["feedPaths"]):
            result.add(component)
    return {"status": "PASS_RELEASE_PLAN", "components": sorted(result)}


def command(args: list[str], *, capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(args, check=True, text=True, capture_output=capture)


def remote_ref_exists(tag: str) -> bool:
    result = command(["git", "ls-remote", "--tags", f"git@github.com:{REPOSITORY}.git", f"refs/tags/{tag}"])
    return bool(result.stdout.strip())


def release_exists(tag: str) -> bool:
    result = subprocess.run(
        ["gh", "release", "view", tag, "-R", REPOSITORY],
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def publish_plan(value: dict, manifest: Path, asset_dir: Path) -> dict:
    verified = verify_assets(value, asset_dir)
    files = [str(asset_dir / asset["name"]) for asset in value["assets"]] + [str(manifest)]
    return {
        "status": "READY_TO_PUBLISH",
        "repository": REPOSITORY,
        "tag": value["tag"],
        "target": value["feed"]["commit"],
        "draft": True,
        "prereleaseAfterVerification": True,
        "files": files,
        "verified": verified,
    }


def release_notes(value: dict) -> str:
    return (
        f"# {value['component']} {value['version']['packageVersion']}\n\n"
        f"Component release for `{value['target']['architecture']}` / `{value['target']['libc']}` / "
        f"`{value['target']['platform']}`.\n\n"
        f"Source: `{value['source']['repository']}@{value['source']['commit']}`.  \n"
        f"Feed: `{REPOSITORY}@{value['feed']['commit']}`.\n\n"
        "See the attached component manifest and `SHA256SUMS` asset for exact identities.\n"
    )


def publish(args: argparse.Namespace) -> dict:
    if args.repository != REPOSITORY:
        raise ValueError(f"publishing is restricted to {REPOSITORY}")
    value = load_manifest(args.manifest)
    plan_value = publish_plan(value, args.manifest.resolve(), args.asset_dir.resolve())
    if not args.execute:
        return {**plan_value, "status": "DRY_RUN"}
    if not os.environ.get("GH_TOKEN"):
        raise RuntimeError("GH_TOKEN is required for publishing")
    if remote_ref_exists(value["tag"]):
        raise RuntimeError(f"tag already exists: {value['tag']}")
    if release_exists(value["tag"]):
        raise RuntimeError(f"release already exists: {value['tag']}")
    with tempfile.NamedTemporaryFile("w", prefix="lighthost-release-notes-", suffix=".md", delete=False) as stream:
        notes = Path(stream.name)
        stream.write(release_notes(value))
    try:
        command([
            "gh", "release", "create", value["tag"],
            *plan_value["files"],
            "-R", REPOSITORY,
            "--target", value["feed"]["commit"],
            "--title", f"{value['component']} {value['version']['packageVersion']}",
            "--notes-file", str(notes),
            "--draft",
        ])
    finally:
        notes.unlink(missing_ok=True)
    return {**plan_value, "status": "DRAFT_CREATED"}


def verify_public(args: argparse.Namespace) -> dict:
    value = load_manifest(args.manifest)
    if value["repository"] != REPOSITORY:
        raise ValueError("wrong public repository")
    checked = []
    for asset in value["assets"]:
        url = f"https://github.com/{REPOSITORY}/releases/download/{value['tag']}/{asset['name']}"
        digest = hashlib.sha256()
        size = 0
        with urllib.request.urlopen(url) as response:
            while block := response.read(1024 * 1024):
                digest.update(block)
                size += len(block)
        if size != asset["size"] or digest.hexdigest() != asset["sha256"]:
            raise ValueError(f"public asset identity mismatch: {asset['name']}")
        checked.append(asset["name"])
    return {"status": "PASS_PUBLIC_RELEASE", "tag": value["tag"], "assets": checked}


def add_common_manifest(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--manifest", type=Path, required=True)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    prepare_parser = commands.add_parser("prepare")
    prepare_parser.add_argument("--component", choices=sorted(metadata.COMPONENTS), required=True)
    prepare_parser.add_argument("--tag", required=True)
    prepare_parser.add_argument("--component-version", required=True)
    prepare_parser.add_argument("--package-version", required=True)
    prepare_parser.add_argument("--package-release", required=True)
    prepare_parser.add_argument("--program-version")
    prepare_parser.add_argument("--source-repository", required=True)
    prepare_parser.add_argument("--source-commit", required=True)
    prepare_parser.add_argument("--source-path", action="append", required=True)
    prepare_parser.add_argument("--feed-commit", required=True)
    prepare_parser.add_argument("--feed-path", action="append", required=True)
    prepare_parser.add_argument("--architecture", required=True)
    prepare_parser.add_argument("--libc", required=True)
    prepare_parser.add_argument("--platform", required=True)
    prepare_parser.add_argument("--asset", action="append", type=parse_asset, required=True)
    prepare_parser.add_argument("--output", type=Path, required=True)
    prepare_parser.set_defaults(handler=prepare)

    verify_parser = commands.add_parser("verify")
    add_common_manifest(verify_parser)
    verify_parser.add_argument("--asset-dir", type=Path, required=True)
    verify_parser.set_defaults(handler=verify)

    plan_parser = commands.add_parser("plan")
    plan_parser.add_argument("--definitions", type=Path, default=Path("release/model/components.json"))
    plan_parser.add_argument("--source-repository", default="linkease/linkease-lighthost")
    plan_parser.add_argument("--source-changed", action="append", default=[])
    plan_parser.add_argument("--feed-changed", action="append", default=[])
    plan_parser.set_defaults(handler=plan)

    publish_parser = commands.add_parser("publish")
    add_common_manifest(publish_parser)
    publish_parser.add_argument("--asset-dir", type=Path, required=True)
    publish_parser.add_argument("--repository", default=REPOSITORY)
    publish_parser.add_argument("--execute", action="store_true", help="create the draft; default is dry-run")
    publish_parser.set_defaults(handler=publish)

    public_parser = commands.add_parser("verify-public")
    add_common_manifest(public_parser)
    public_parser.set_defaults(handler=verify_public)
    return root


def main() -> None:
    args = parser().parse_args()
    try:
        result = args.handler(args)
    except (FileExistsError, FileNotFoundError, ValueError, RuntimeError, metadata.InvalidMetadata) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}), file=sys.stderr)
        raise SystemExit(1) from error
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

