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
6. S5 only: feed `qemu`, `usbredir`, `libaio`, `lighthost-qemu-firmware`,
   `lighthost-dhcp-release`, the packages-feed `coreutils-dd`, and the separate
   `incus-agent` output
   from the Incus package

The build entry point is `scripts/build-env.sh`; do not copy these packages
manually into the shared iStoreOS source tree. The LightHost package compiles
the Go control plane from `LIGHTHOST_SOURCE_ROOT` and packages the already
verified `frontend/dist` output. It never downloads a Docker image.

VM dependencies are selected only by the `build-vm-userspace` action. Their
versions and source hashes are locked in
`toolchains/istoreos-24.10-x86_64-vm.lock`. The resolved 37-package runtime
closure is locked in `toolchains/istoreos-24.10-x86_64-vm-packages.lock.tsv`;
they are not part of the system-container package set.

The locked packages feed needs repository-owned QEMU adaptations for the
Incus-generated VM topology. They disable automatic PNG detection when VNC is
disabled, enable `usb-redir`, enable VirtFS for the agent channel, and enable
Linux native AIO with explicit `libaio` dependencies for the system emulator
and image tools. Every patch checksum is verified by `scripts/build-env.sh`
before compilation. Host USB passthrough remains disabled; `usb-redir` is a
QEMU device-model requirement here, not an exposed product feature.

Incus' `dir` storage driver uses GNU `dd` with `conv=nocreat` for VM disk
snapshots. The immutable runtime therefore includes the locked `coreutils-dd`
and `coreutils-nice` 9.7 packages plus their `coreutils` dependency. Release
assembly records both aliases in `metadata/RUNTIME-ALIASES.tsv`. GNU `nice` is
required because the BusyBox multicall `nice` invokes its own `dd` applet and
bypasses PATH; that applet does not implement the required conversion flag.

VM Gate cleanup uses the upstream dnsmasq 2.90 `dhcp_release` utility packaged
alone as `lighthost-dhcp-release`. Its source and IPK are locked like every
other VM package, including its explicit `libc` and `libgcc1` runtime
dependencies. It releases only leases matching the dedicated Gate MAC and
avoids editing UCI, rewriting dnsmasq's lease file, or restarting the host
DHCP/DNS service.
