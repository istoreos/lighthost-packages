#!/usr/bin/env python3
"""Assemble deterministic component build inputs from reviewed IPK payloads."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tarfile


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def ipk_payload(path: Path) -> dict[str, tuple[bytes | None, str, int]]:
    with tarfile.open(path) as outer:
        member = next(item for item in outer if item.name.endswith("data.tar.gz"))
        blob = outer.extractfile(member).read()
    result = {}
    with tarfile.open(fileobj=io.BytesIO(blob)) as archive:
        for item in archive:
            name = item.name.removeprefix("./")
            if not name or item.isdir():
                continue
            if name.startswith("/") or ".." in Path(name).parts or not (item.isfile() or item.issym()):
                raise ValueError(f"unsafe IPK payload entry: {name}")
            result[name] = (
                archive.extractfile(item).read() if item.isfile() else None,
                item.linkname if item.issym() else "",
                item.mode,
            )
    return result


def add_file(entries: dict, name: str, value: bytes, mode: int = 0o644) -> None:
    if name in entries:
        raise ValueError(f"duplicate archive entry: {name}")
    entries[name] = (value, "", mode)


def manifest(entries: dict) -> bytes:
    rows = []
    for name, (value, link, _) in sorted(entries.items()):
        identity = sha256_bytes(value) if value is not None else f"SYMLINK:{link}"
        rows.append(f"{identity}  {name}\n")
    return "".join(rows).encode()


def archive(output: Path, prefix: str, entries: dict, epoch: int) -> None:
    if output.exists():
        raise FileExistsError(output)
    directories = {str(parent) for name in entries for parent in Path(name).parents if str(parent) != "."}
    with output.open("xb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as tar:
                root = tarfile.TarInfo(prefix)
                root.type = tarfile.DIRTYPE
                root.uid = root.gid = 0
                root.uname = root.gname = "root"
                root.mode = 0o755
                root.mtime = epoch
                tar.addfile(root)
                for directory in sorted(directories):
                    item = tarfile.TarInfo(f"{prefix}/{directory}")
                    item.type = tarfile.DIRTYPE
                    item.uid = item.gid = 0
                    item.uname = item.gname = "root"
                    item.mode = 0o755
                    item.mtime = epoch
                    tar.addfile(item)
                for name, (value, link, mode) in sorted(entries.items()):
                    item = tarfile.TarInfo(f"{prefix}/{name}")
                    item.uid = item.gid = 0
                    item.uname = item.gname = "root"
                    item.mode = mode
                    item.mtime = epoch
                    if value is None:
                        item.type = tarfile.SYMTYPE
                        item.linkname = link
                        tar.addfile(item)
                    else:
                        item.size = len(value)
                        tar.addfile(item, io.BytesIO(value))


def source_archive(output: Path, prefix: str, source: Path, epoch: int) -> None:
    entries = {}
    for path in sorted(source.rglob("*")):
        if path.is_file() and not path.is_symlink():
            entries[str(path.relative_to(source))] = (
                path.read_bytes(), "", 0o755 if path.stat().st_mode & 0o111 else 0o644
            )
    if not entries:
        raise ValueError(f"source offer is empty: {source}")
    archive(output, prefix, entries, epoch)


def select_prefix(payload: dict, source_prefix: str, target_prefix: str, *, exclude: set[str] | None = None) -> dict:
    result = {}
    exclude = exclude or set()
    for name, value in payload.items():
        if name.startswith(source_prefix):
            relative = name[len(source_prefix):]
            if relative and relative not in exclude:
                result[target_prefix + relative] = value
    return result


def build_info(args: argparse.Namespace, ipks: list[Path], entries: dict) -> bytes:
    programs = {
        name: sha256_bytes(value)
        for name, (value, _, mode) in sorted(entries.items())
        if value is not None and mode & 0o111 and (name.startswith("bin/") or name.startswith("spice-console/"))
    }
    value = {
        "schemaVersion": 1,
        "component": args.component,
        "sourceRepository": args.source_repository,
        "sourceCommit": args.source_commit,
        "feedCommit": args.feed_commit,
        "platformCommit": args.platform_commit,
        "toolchain": args.toolchain,
        "target": "x86_64-linux-musl / iStoreOS 24.10",
        "packageVersion": args.package_version,
        "originIPKs": {path.name: sha256(path) for path in ipks},
        "programSha256": programs,
        "assembly": "DETERMINISTIC_FROM_REVIEWED_IPK_PAYLOAD",
    }
    if args.program_version:
        value["programVersion"] = args.program_version
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def assemble(args: argparse.Namespace) -> dict:
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    primary = ipk_payload(args.ipk[0])
    entries: dict[str, tuple[bytes | None, str, int]] = {}
    prefix = ""
    archive_name = ""

    if args.component == "lighthost":
        component_version = args.package_version.rsplit("-r", 1)[0]
        prefix = f"lighthost-{component_version}"
        archive_name = f"lighthost-{args.package_version}-x86_64.tar.gz"
        mapping = {
            "usr/sbin/lighthost": "bin/lighthost",
            "usr/bin/lighthost-vm-pilot-policy": "bin/lighthost-vm-pilot-policy",
            "usr/share/lighthost/images.x86_64-2410.lock.tsv": "release/images.x86_64-2410.lock.tsv",
            "usr/share/lighthost/vm-media-sources.x86_64-2410.lock.tsv": "release/vm-media-sources.x86_64-2410.lock.tsv",
        }
        for source, target in mapping.items():
            entries[target] = primary[source]
        entries.update(select_prefix(primary, "usr/share/lighthost/licenses/", "licenses/"))
    elif args.component == "lighthost-ui":
        prefix = "lighthost-ui-0.3.0"
        archive_name = "lighthost-ui-0.3.0-r87.1-x86_64.tar.gz"
        entries.update(select_prefix(primary, "usr/share/lighthost/www/", "frontend-dist/", exclude={"logo.svg"}))
    elif args.component == "lighthost-spice-console":
        prefix = "lighthost-spice-console-0.3.0"
        archive_name = "lighthost-spice-console-0.3.0-r87-x86_64.tar.gz"
        entries.update(select_prefix(primary, "usr/share/lighthost/www/spice-console/", "spice-console/"))
    elif args.component == "incus":
        if len(args.ipk) != 2:
            raise ValueError("Incus requires incus and incus-agent IPKs")
        secondary = ipk_payload(args.ipk[1])
        prefix = "incus-6.0.6"
        archive_name = "incus-6.0.6-lighthost.3-r3-x86_64.tar.gz"
        for source, target in (("usr/bin/incus", "bin/incus"), ("usr/sbin/incusd", "bin/incusd")):
            entries[target] = primary[source]
        entries["bin/incus-agent"] = secondary["usr/bin/incus-agent"]
        if args.license_file:
            add_file(entries, "COPYING", args.license_file.read_bytes())
            add_file(entries, "licenses/COPYING", args.license_file.read_bytes())
    elif args.component == "lighthost-qemu-firmware":
        prefix = "lighthost-qemu-firmware-202302"
        archive_name = "lighthost-qemu-firmware-202302-r2-x86_64.tar.gz"
        entries.update(select_prefix(primary, "usr/share/qemu/", ""))
        entries.update(select_prefix(primary, "usr/share/licenses/lighthost-qemu-firmware/", "licenses/"))
    else:
        raise ValueError(args.component)

    if not entries:
        raise ValueError("component payload is empty")
    add_file(entries, "BUILD-INFO.json", build_info(args, args.ipk, entries))
    add_file(entries, "PAYLOAD.SHA256", manifest(entries))
    build_input = args.output / archive_name
    archive(build_input, prefix, entries, args.epoch)

    assets = [("build-input", build_input)]
    for ipk in args.ipk:
        destination = args.output / ipk.name
        shutil.copyfile(ipk, destination)
        assets.append(("package", destination))
    info = args.output / "BUILD-INFO.json"
    info.write_bytes(build_info(args, args.ipk, entries))
    assets.append(("build-info", info))
    if args.source_offer:
        offer = args.output / f"{args.component}-{args.package_version}-sources.tar.gz"
        source_archive(offer, f"{args.component}-{args.package_version}-sources", args.source_offer, args.epoch)
        assets.append(("source-offer", offer))
    sums = args.output / "SHA256SUMS"
    sums.write_text("".join(f"{sha256(path)}  {path.name}\n" for _, path in sorted(assets, key=lambda row: row[1].name)))
    assets.append(("checksums", sums))
    result = {
        "status": "PASS_COMPONENT_ASSEMBLED",
        "component": args.component,
        "assets": {path.name: {"role": role, "size": path.stat().st_size, "sha256": sha256(path)} for role, path in assets},
    }
    (args.output / "ASSEMBLY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", required=True, choices=("lighthost", "lighthost-ui", "lighthost-spice-console", "incus", "lighthost-qemu-firmware"))
    parser.add_argument("--ipk", action="append", type=Path, required=True)
    parser.add_argument("--package-version", required=True)
    parser.add_argument("--program-version")
    parser.add_argument("--source-repository", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--feed-commit", required=True)
    parser.add_argument("--platform-commit", required=True)
    parser.add_argument("--toolchain", required=True)
    parser.add_argument("--license-file", type=Path)
    parser.add_argument("--source-offer", type=Path)
    parser.add_argument("--epoch", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for path in args.ipk:
        if not path.is_file():
            parser.error(f"missing IPK: {path}")
    print(json.dumps(assemble(args), indent=2))


if __name__ == "__main__":
    main()

