# LightHost OpenWrt packages

This repository is the standalone OpenWrt package feed for LightHost. It owns
the package recipes and package-local files required to build the native
LightHost control plane and Incus runtime. It does not contain an iStoreOS
source tree, firmware build outputs, or a shared download cache.

The LightHost product source, firmware assembly, release manifests, and
qualification tests remain in
[`linkease/linkease-lighthost`](https://github.com/linkease/linkease-lighthost).
Platform changes to the iStoreOS base tree are maintained in
[`linkease/istorework-os`](https://github.com/linkease/istorework-os), while
adaptations to the standard packages feed are maintained in
[`linkease/istorework-packages`](https://github.com/linkease/istorework-packages).

## Packages

The feed currently provides:

1. `lxcfs`
2. `raft`
3. `cowsql`
4. `incus` and `incus-agent`
5. `lighthost` and `lighthost-ui`
6. `usbredir`, `libaio`, and `lighthost-qemu-firmware`
7. `lighthost-dhcp-release`

The unified VM runtime also consumes packages from the locked iStoreOS
packages feed. QEMU and LXC changes are intentionally not copied into this
repository.

## Reproducible use

Formal builds must pin this feed by full Git commit. Tracking `main` directly
is allowed for development only. The release manifest in `linkease-lighthost`
also pins the iStoreOS base, standard feeds, package set, configuration, source
archives, and their SHA-256 values.

The firmware builder materializes this repository as a dedicated feed in a
new per-build workspace. Do not copy these packages into a persistent or
shared iStoreOS checkout.

`lighthost`, `incus`, and `lighthost-qemu-firmware` consume immutable prebuilt
inputs from the public [2026-10-14 Release](https://github.com/istoreos/istorework-packages/releases/tag/lighthost-public-build-inputs-20261014)
in `istoreos/istorework-packages`. The recipes pin `PKG_SOURCE_URL` and `PKG_HASH`
and verify the internal payload manifest. They require neither an external
`LIGHTHOST_SOURCE_ROOT`, a locally installed Go compiler, nor a pre-existing
frontend dist. Other libraries retain their public, version-locked upstreams.

These prebuilt inputs support **x86_64 musl / iStoreOS 24.10**. The product was
built from committed source `65cf9c4d81710b5d0e6dff472e15d0788abbc33b` as
`0.3.0-r82`; Incus remains on the latest supported 6.0 LTS release, 6.0.6. The
firmware comes from QEMU 9.1.3 / EDK2 stable202302 and the locked public
Microsoft certificate template. Product backend source is not included in the
public binary input. The Incus source patch offer and third-party notices are
included. Build records and six tested IPKs accompany the inputs in the Release.

Public build inputs do not establish physical VM/Windows qualification or a
complete firmware/runtime release. VM stable enablement and device deployment
require their separate product gates. See [the build record](docs/PUBLIC-BUILD-INPUTS-20261014.md).

## Build order

The runtime libraries must be available before Incus, and the application
packages are built last:

```text
lxcfs
raft -> cowsql -> incus
usbredir/libaio/qemu firmware helpers
lighthost -> lighthost-ui
```

Build and release entry points are owned by `linkease-lighthost`; this feed is
not a standalone firmware distribution.
