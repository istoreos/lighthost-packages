#!/usr/bin/env python3
"""Assemble only native binaries, public upstream/source patches and notices."""
import argparse, hashlib, json, os, shutil, subprocess, tarfile, gzip
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("run",type=Path)
args=parser.parse_args();run=args.run.resolve()
output=run/"public-assets";output.mkdir(exist_ok=False)
base=run/"native-payload";base.mkdir()
(base/"bin").mkdir()
for name in ["incus","incusd","incus-agent"]:
    first=run/"bin-first"/name;second=run/"bin-repeat"/name
    assert first.read_bytes()==second.read_bytes(),name
    shutil.copyfile(first,base/"bin"/name);(base/"bin"/name).chmod(0o755)
source=run/"incus"
shutil.copyfile(source/"COPYING",base/"COPYING")
for p in (source/"vendor").rglob("*"):
    if p.is_file() and p.name.lower().startswith(("license","copying","notice","copyright")):
        target=base/"licenses"/p.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
shutil.copyfile(run/"toolchain/go/LICENSE",base/"licenses/LICENSE.Go")
record={"schema":1,"upstreamVersion":"6.0.6","upstreamUrl":"https://github.com/lxc/incus/releases/download/v6.0.6/incus-6.0.6.tar.xz",
        "upstreamSha256":"129a1323605d427c46c8358844f5f9447d7e2cebe0f4ada242c93cf002fb44ea",
        "goVersion":"1.25.14","goArchiveSha256":"a21ae5633a269bcd7e90cf767e48225633795e99d831742cbf3397064fee7712",
        "nativePatchSourceCommit":"65cf9c4d81710b5d0e6dff472e15d0788abbc33b",
        "target":"x86_64-linux-musl / iStoreOS24.10", "nativeBuild":"TWO_BUILDS_BYTE_IDENTICAL",
        "deviceQualification":"NOT_RUN", "runtimeActivation":"NOT_RUN",
        "patchSha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((run/"inputs/native-patches").glob("*.patch"))},
        "binarySha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((base/"bin").iterdir())}}
(base/"BUILD-INFO.json").write_text(json.dumps(record,indent=2)+"\n")
for name in record["binarySha256"]:
    (base/(name+".go-build.txt")).write_text(subprocess.check_output([str(run/"toolchain/go/bin/go"),"version","-m",str(base/"bin"/name)],text=True).replace(str(base/"bin"/name),name))
manifest="".join(hashlib.sha256(p.read_bytes()).hexdigest()+"  "+p.relative_to(base).as_posix()+"\n" for p in sorted(base.rglob("*")) if p.is_file())
(base/"PAYLOAD.SHA256").write_text(manifest)
offer=run/"native-source-offer";offer.mkdir()
shutil.copyfile(run/"inputs/incus-6.0.6.tar.xz",offer/"incus-6.0.6.tar.xz")
shutil.copytree(run/"inputs/native-patches",offer/"patches")
shutil.copyfile(run/"build-public-native.sh",offer/"build-public-native.sh")
(offer/"BUILD-INFO.json").write_text(json.dumps(record,indent=2)+"\n")
shutil.copyfile(source/"COPYING",offer/"COPYING")
for tree,name,prefix in [(base,"incus-6.0.6-public-20261014-x86_64.tar.gz","incus-6.0.6"),(offer,"incus-6.0.6-public-20261014-sources.tar.gz","incus-6.0.6-sources")]:
    with (output/name).open("wb") as raw,gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as compressed,tarfile.open(fileobj=compressed,mode="w",format=tarfile.PAX_FORMAT) as archive:
        for p in [tree,*sorted(tree.rglob("*"))]:
            assert not p.is_symlink()
            info=archive.gettarinfo(str(p),arcname=prefix+("/"+p.relative_to(tree).as_posix() if p!=tree else ""))
            info.uid=info.gid=0;info.uname=info.gname="root";info.mtime=0;info.mode=0o755 if p.is_dir() or p.parent.name=="bin" or p.name.endswith(".sh") else 0o644
            with p.open("rb") if p.is_file() else open(os.devnull,"rb") as stream:archive.addfile(info,stream if p.is_file() else None)
(output/"INCUS-BUILD-INFO.json").write_text(json.dumps(record,indent=2)+"\n")
print(json.dumps({p.name:{"size":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in output.iterdir()},indent=2))
