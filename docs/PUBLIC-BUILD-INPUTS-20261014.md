# Public LightHost build inputs, 2026-10-14

Release: https://github.com/istoreos/istorework-packages/releases/tag/lighthost-public-build-inputs-20261014

The inputs were published before updating the recipes. All seven original assets
were downloaded without authentication and their hashes matched the local build.
The updated recipes were then exercised in an isolated iStoreOS 24.10 x86_64 SDK.
Six resulting IPKs were also uploaded, with an independent package verification
record and IPK hashes. Existing releases, shared builder checkouts and devices
were not changed.

## Source and target

- Product: committed main `65cf9c4d81710b5d0e6dff472e15d0788abbc33b`, release ID `0.3.0-r82`.
- Incus: public 6.0.6 source archive including vendor; SHA256 `129a1323605d427c46c8358844f5f9447d7e2cebe0f4ada242c93cf002fb44ea`.
- Native integration: frozen LightHost patches 010/020/030, applied before compilation; no second patch application when repackaging the binary input.
- Go: official 1.25.14 linux-amd64 archive; SHA256 `a21ae5633a269bcd7e90cf767e48225633795e99d831742cbf3397064fee7712`.
- Target: x86_64, musl, GCC13.3 SDK, iStoreOS24.10. This input cannot be used for other architectures.
- Firmware: QEMU9.1.3 archive SHA256 `480a77a0ed13a9b39415f639aa020b4eb0d7cc5a52569510dfd830b3af1bac89`, EDK2 stable202302; source-locked public Microsoft VARS template SHA256 `a4cee576b37eb257baabed5f82f3c541f326d931128334b57508c1a0d94336e0`.

## Recipe input hashes

| Recipe | Published asset SHA256 |
| --- | --- |
| lighthost | `b1521a479326e9f442156972fe0a2d53a21edc862b2b27b50bcc1cc419491975` |
| incus | `59226bbf8c001181d71d4dac76690f36b5368bb366e3826688f93f0953f5eba0` |
| qemu-firmware | `49b8b0b86ac64817385eb50eb259f5005bb48559b05faf4d9b53a0012075d655` |

Local Go/source overrides have been removed from all feed Makefiles. Recipe
files under `files/` remain ordinary tracked package configuration and scripts;
they are not references to a developer checkout. LightHost package-local files
were aligned with the frozen product, including the closed USB allowlist and
VM policy helper. The Console remains a separate GPL package. Licenses are
installed for the control product, Incus, and the independently usable agent.

SDK strip initially changed already-stripped Release program bytes. The recipes
now disable repeat stripping, so all five packaged programs match the public
input exactly; uid/gid0 and mode0755 were checked from actual IPK payloads.
The firmware, frontend, Console, metadata and notices are verified against their
input manifests before repackaging.

## Validation and limitations

Product programs, native programs and frontend were each built twice, byte
identical. Backend test/vet/race, frontend typecheck and 163 tests, and the
OpenAPI43-path contract passed. Native musl client/daemon version entry points
ran against the SDK libraries. Public downloads and actual package assembly
passed without an external product checkout or local Go installation in the
consumer recipes.

The first frozen test snapshot omitted tracked firmware test data; the next
attempt exposed an overlong Unix socket temporary path. Exact tracked test data
and a task-owned short SSD TMPDIR resolved those setup failures. Logs retain
both failures. A builder GitHub TLS download failed once; a normal verified
HTTPS retry succeeded. No certificate checks were disabled.

Records are kept under ignored `out/public-inputs-20261014/`, with the public
build/asset manifest and actual package verification in the Release. Builder
outputs are isolated under `/builders/projects/lighthost/work/public-feed-inputs-20261014`.
Scripts under `scripts/` record this frozen build/assembly. Do not reuse the same
output directory or overwrite published asset names for future source versions;
freeze a new source, use a new Release tag, and calculate actual output hashes.

This was compilation and packaging, not daemon/guest integration, device
installation, active BitLocker restoration, multi-disk collection protection,
USB qualification, soak or Go/No-Go. Software/runtime qualification and VM
stable enablement remain separate; no old device authorization was reused.
