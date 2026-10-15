#!/usr/bin/env python3
"""Bundle frozen product binaries/dist and required notices, excluding backend source."""
import argparse,hashlib,json,os,shutil,tarfile,gzip
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--source",type=Path,required=True)
parser.add_argument("--inputs",type=Path,required=True)
args=parser.parse_args();source=args.source.resolve();inputs=args.inputs.resolve()
base=inputs/"product-payload";base.mkdir(exist_ok=False);(base/"bin").mkdir()
for name in ["lighthost","lighthost-vm-pilot-policy"]:
    shutil.copyfile(inputs/name,base/"bin"/name);(base/"bin"/name).chmod(0o755)
shutil.copytree(source/"frontend/dist",base/"frontend-dist")
shutil.copytree(source/"spice-console",base/"spice-console")
(base/"release").mkdir()
for name in ["images.x86_64-2410.lock.tsv","vm-media-sources.x86_64-2410.lock.tsv"]:shutil.copyfile(source/"release"/name,base/"release"/name)
for tree,prefix in [(source/"backend/vendor","backend"),(source/"frontend/node_modules","frontend")]:
    for p in tree.rglob("*"):
        if p.is_file() and p.name.lower().startswith(("license","copying","notice","copyright")):
            target=base/"licenses"/prefix/p.relative_to(tree);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
record=json.loads((inputs/"product-source-binding.json").read_text())
record.update(target="x86_64-linux-musl / iStoreOS24.10",productBuild="TWO_BUILDS_BYTE_IDENTICAL",frontendBuild="TWO_BUILDS_BYTE_IDENTICAL",
              physicalQualification="NOT_RUN",runtimeActivation="NOT_RUN",backendSourceIncluded=False,vmProductEnabled=False)
record["binarySha256"]={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (base/"bin").iterdir()}
(base/"BUILD-INFO.json").write_text(json.dumps(record,indent=2)+"\n")
manifest="".join(hashlib.sha256(p.read_bytes()).hexdigest()+"  "+p.relative_to(base).as_posix()+"\n" for p in sorted(base.rglob("*")) if p.is_file())
(base/"PAYLOAD.SHA256").write_text(manifest)
name="lighthost-0.3.0-r82-65cf9c4d8171-x86_64.tar.gz"
with (inputs/"public-assets"/name).open("wb") as raw,gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as compressed,tarfile.open(fileobj=compressed,mode="w",format=tarfile.PAX_FORMAT) as archive:
    for p in [base,*sorted(base.rglob("*"))]:
        assert not p.is_symlink()
        info=archive.gettarinfo(str(p),arcname="lighthost-0.3.0"+("/"+p.relative_to(base).as_posix() if p!=base else ""))
        info.uid=info.gid=0;info.uname=info.gname="root";info.mtime=0;info.mode=0o755 if p.is_dir() or p.parent==base/"bin" else 0o644
        with p.open("rb") if p.is_file() else open(os.devnull,"rb") as stream:archive.addfile(info,stream if p.is_file() else None)
print(name,hashlib.sha256((inputs/"public-assets"/name).read_bytes()).hexdigest())
