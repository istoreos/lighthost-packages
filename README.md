# LightHost OpenWrt feed

This feed contains native runtime dependencies that are not provided by the
locked iStoreOS 24.10 feeds. Every package source is pinned to the full commit
recorded in `upstream/sources.lock` and downloaded from the corresponding
official GitHub codeload endpoint with a SHA-256 check.

Current build order:

1. `lxcfs`
2. `raft`
3. `cowsql`
4. `incus`
5. `lighthost` and `lighthost-ui`
6. S5 only: feed `qemu`, `lighthost-qemu-firmware`, and the separate
   `incus-agent` output from the Incus package

The build entry point is `scripts/build-env.sh`; do not copy these packages
manually into the shared iStoreOS source tree. The LightHost package compiles
the Go control plane from `LIGHTHOST_SOURCE_ROOT` and packages the already
verified `frontend/dist` output. It never downloads a Docker image.

VM dependencies are selected only by the `build-vm-userspace` action. Their
versions and source hashes are locked in
`toolchains/istoreos-24.10-x86_64-vm.lock`. The resolved 29-package runtime
closure is locked in `toolchains/istoreos-24.10-x86_64-vm-packages.lock.tsv`;
they are not part of the system-container package set.

The locked packages feed needs one repository-owned QEMU adaptation:
`patches/openwrt-packages/qemu/0001-disable-png-without-vnc.patch`. It disables
QEMU's automatic PNG detection when VNC is disabled, keeping the ELF runtime
dependencies consistent with the OpenWrt package metadata. The patch checksum
is verified by `scripts/build-env.sh` before compilation.
