#!/usr/bin/env python3
"""Verify actual package control/payload, uid/mode, and Release-bound program bytes."""
import argparse,hashlib,io,json,tarfile
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--inputs",type=Path,required=True)
parser.add_argument("--ipks",type=Path,required=True)
parser.add_argument("--result",type=Path,required=True)
args=parser.parse_args();expected={}
for asset in args.inputs.glob("*.tar.gz"):
    with tarfile.open(asset) as bundle:
        for member in bundle.getmembers():
            if member.isfile() and "/bin/" in member.name:
                name=Path(member.name).name
                path={"lighthost":"usr/sbin/lighthost","lighthost-vm-pilot-policy":"usr/bin/lighthost-vm-pilot-policy","incus":"usr/bin/incus","incusd":"usr/sbin/incusd","incus-agent":"usr/bin/incus-agent"}.get(name)
                if path:expected[path]=hashlib.sha256(bundle.extractfile(member).read()).hexdigest()
results=[];seen=set()
for artifact in sorted(args.ipks.glob("*.ipk")):
    with tarfile.open(artifact) as outer:
        control=next(m for m in outer.getmembers() if m.name.endswith("control.tar.gz"));payload=next(m for m in outer.getmembers() if m.name.endswith("data.tar.gz"))
        with tarfile.open(fileobj=io.BytesIO(outer.extractfile(control).read())) as metadata:
            fields=metadata.extractfile(next(m for m in metadata.getmembers() if m.name.removeprefix("./")=="control")).read().decode()
            assert "Architecture: x86_64" in fields
        checks=[];names=set()
        with tarfile.open(fileobj=io.BytesIO(outer.extractfile(payload).read())) as data:
            for m in data.getmembers():
                name=m.name.removeprefix("./")
                assert name not in names;names.add(name)
                assert m.uid==0 and m.gid==0,(artifact.name,name,"owner")
                assert not name.startswith("/") and ".." not in Path(name).parts
                if name in expected:
                    digest=hashlib.sha256(data.extractfile(m).read()).hexdigest()
                    assert digest==expected[name],(artifact.name,name,"program bytes changed")
                    assert m.mode==0o755
                    checks.append({"path":name,"sha256":digest,"mode":oct(m.mode)});seen.add(name)
            if "Package: incus-agent\n" in fields:assert "usr/share/licenses/incus-agent/COPYING" in names
            if "Package: lighthost\n" in fields:
                assert "etc/lighthost/usb/allowlist.json" in names
                assert "etc/init.d/lighthost" in names
            if "Package: lighthost-ui\n" in fields:assert "usr/share/lighthost/www/desktop-entry.js" in names
            if "Package: lighthost-spice-console\n" in fields:assert "usr/share/lighthost/www/spice-console/vendor/spice/COPYING.LESSER" in names
        results.append({"file":artifact.name,"sha256":hashlib.sha256(artifact.read_bytes()).hexdigest(),"control":fields,"binaries":checks})
assert len(results)==6 and seen==set(expected)
assert not args.result.exists()
args.result.write_text(json.dumps({"result":"PASS_ACTUAL_SIX_IPKS_BYTES_OWNER_MODE_LICENSES","packages":results},indent=2)+"\n")
print("PASS_ACTUAL_SIX_IPKS_BYTES_OWNER_MODE_LICENSES")
