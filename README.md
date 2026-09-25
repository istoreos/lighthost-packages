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

The `lighthost` recipe currently supports a controlled local
`LIGHTHOST_SOURCE_ROOT` for development builds. Formal release builds will use
an immutable LightHost source bundle with a recorded SHA-256 instead of an
uncommitted developer worktree.

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
