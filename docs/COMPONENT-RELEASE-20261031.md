# LightHost component prerelease qualification — 2026-10-31

## Qualified release set

This qualification uses five independently versioned component Releases in
`istoreos/lighthost-packages`. Incus owns two IPKs, so the set contains six
packages without creating a sixth source identity.

| Component | Qualified tag | Packages |
| --- | --- | --- |
| Core | `lighthost-v0.3.0-r88` | `lighthost_0.3.0-r88_x86_64.ipk` |
| UI | `lighthost-ui-v0.3.0-r87.2` | `lighthost-ui_0.3.0-r87.2_x86_64.ipk` |
| Console | `lighthost-spice-console-v0.3.0-r87` | `lighthost-spice-console_0.3.0-r87_x86_64.ipk` |
| Incus | `incus-v6.0.6-lighthost.3-r3` | `incus_6.0.6-r3_x86_64.ipk`, `incus-agent_6.0.6-r3_x86_64.ipk` |
| Firmware | `lighthost-qemu-firmware-v202302-r2` | `lighthost-qemu-firmware_202302-r2_x86_64.ipk` |

The machine-readable composition is
`release/sets/lighthost-x86_64-20261031-prerelease.json`. Consumers must use
these exact tags and the hashes in each attached manifest. GitHub's repository
`Latest` label is not part of the contract.

## Build qualification

- Final feed commit: `97654ae82f5100e1e10ee7b6748917346a4426d0`.
- Product source commit: `6ce3d17abc838368bee29ea1181f6cbc45ec2f3c`.
- Platform commit: `853dbd9a5790af394ff568d782c024c2f60c2e92`.
- Builder batch: `/builders/projects/lighthost/work/public-component-consumer-20261031`.
- The isolated SDK started with an empty `dl/`; GitHub credentials, product
  source overrides and local Go overrides were absent.
- Five exact public Release URLs produced six IPKs. A clean package rebuild
  produced the same SHA-256 values.

| IPK | SHA-256 |
| --- | --- |
| `lighthost_0.3.0-r88_x86_64.ipk` | `2e3c2c72681e19158faf8d2f487cd959dc7ac964c0783b3489acae5f92057e20` |
| `lighthost-ui_0.3.0-r87.2_x86_64.ipk` | `ea0cfb226c524ec0acd845ad6e121d14f28996ba4c132c4d7178c3a342070784` |
| `lighthost-spice-console_0.3.0-r87_x86_64.ipk` | `0ff79477e759c77f055588bc13a29f3d59fe8f35a60409f35f142d9c83a600da` |
| `incus_6.0.6-r3_x86_64.ipk` | `80f387dae8195207b887ec4321a8f5a29cae1f75a4588ec35ac11180763923ba` |
| `incus-agent_6.0.6-r3_x86_64.ipk` | `9dde95de86dc7ee988b48c1a6bbecdeb22737afdfac6b781de0ab47fa9f7217f` |
| `lighthost-qemu-firmware_202302-r2_x86_64.ipk` | `087086b5782a0db35e88968632a4ba00c774825b5fa56729021b5de61e01a58a` |

The UI, Console, Incus, Incus Agent and firmware installed payloads are
byte-identical to the reviewed physical-machine baseline. Core r88 preserves
the r87 payload except for its required `/usr/share/lighthost/release` value.

## Physical qualification and rollback

Target: `root@192.168.9.195`. Durable evidence is under
`/mnt/lighthost-data/lighthost/operations/component-release-20261031/evidence`.

The host-owned Core, UI and Console packages were installed, rolled back to
r87/r87.1, verified, and installed again. The runtime-owned Incus, Agent and
firmware packages were checked file-for-file against the active runtime rootfs;
they were not incorrectly installed into the host opkg root.

Before, during rollback and after final deployment:

- six instances remained present with two running and four stopped;
- the runtime release link, boot ID, conffile hashes and Incus program hashes
  did not change;
- `lighthost-ready`, the standalone page, SPICE static entry and
  `/apps/lighthost/api/v1/readyz` passed;
- Incus client and server remained `6.0.6-lighthost.3`.

The physical machine is left on Core r88, UI r87.2 and Console r87.

## Superseded candidates

`lighthost-v0.3.0-r87` omitted the installed third-party license payload and is
superseded by r88. `lighthost-ui-v0.3.0-r87.1` reused an already-installed
package version while changing dependency metadata and is superseded by r87.2.
Their assets remain immutable for audit history and must not be consumed by a
new release set.
