#!/usr/bin/env python3
"""Compare installed payload identity for baseline and candidate OpenWrt IPKs."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import tarfile


def payload(path: Path) -> dict[str, dict]:
    with tarfile.open(path) as outer:
        member = next(item for item in outer.getmembers() if item.name.endswith("data.tar.gz"))
        blob = outer.extractfile(member).read()
    result = {}
    with tarfile.open(fileobj=io.BytesIO(blob)) as archive:
        for item in archive.getmembers():
            name = item.name.removeprefix("./")
            if not name or name == ".":
                continue
            if item.isfile():
                digest = hashlib.sha256(archive.extractfile(item).read()).hexdigest()
                kind = "file"
            elif item.issym():
                digest = item.linkname
                kind = "symlink"
            elif item.isdir():
                digest = ""
                kind = "directory"
            else:
                raise ValueError(f"{path}: unsupported payload entry {name}")
            result[name] = {
                "kind": kind,
                "identity": digest,
                "mode": item.mode,
                "uid": item.uid,
                "gid": item.gid,
            }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--result", type=Path)
    args = parser.parse_args()
    before = payload(args.baseline)
    after = payload(args.candidate)
    if before != after:
        missing = sorted(set(before) - set(after))
        added = sorted(set(after) - set(before))
        changed = sorted(name for name in set(before) & set(after) if before[name] != after[name])
        raise SystemExit(json.dumps({"status": "FAIL", "missing": missing, "added": added, "changed": changed}, indent=2))
    record = {
        "status": "PASS_PAYLOAD_IDENTICAL",
        "baseline": args.baseline.name,
        "candidate": args.candidate.name,
        "entries": len(before),
    }
    if args.result:
        if args.result.exists():
            raise FileExistsError(args.result)
        args.result.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record))


if __name__ == "__main__":
    main()

