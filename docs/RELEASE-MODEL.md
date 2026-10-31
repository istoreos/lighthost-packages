# LightHost component release model

## Purpose

`istoreos/lighthost-packages` publishes independently addressable OpenWrt
component releases. A release tag represents one immutable source and packaging
unit, not one executable and not an entire device rollout.

The model separates:

- **component release**: one independently buildable and rollbackable artifact
  set;
- **release set**: the exact component tags qualified together;
- **rollout evidence**: the result of installing a release set on a target.

GitHub's repository-wide `Latest` label is not an input to builds. Consumers
must use exact tags and SHA-256 values.

## Components

| Component ID | Source unit | Packages and programs | Tag prefix |
| --- | --- | --- | --- |
| `lighthost` | product `backend/`, release locks and core package files | `lighthost` IPK; `lighthost`, `lighthost-vm-pilot-policy` | `lighthost-v` |
| `lighthost-ui` | product `frontend/` and UI package files | `lighthost-ui` IPK | `lighthost-ui-v` |
| `lighthost-spice-console` | product `spice-console/` and Console package files | `lighthost-spice-console` IPK | `lighthost-spice-console-v` |
| `incus` | pinned Incus source, the complete LightHost patch set and package recipe | `incus`, `incus-agent` IPKs; `incus`, `incusd`, `incus-agent` | `incus-v` |
| `lighthost-qemu-firmware` | pinned QEMU/EDK2 inputs, VARS template and firmware recipe | `lighthost-qemu-firmware` IPK | `lighthost-qemu-firmware-v` |

Package-local init scripts, configuration, patches and install logic belong to
the component they modify. A packaging-only change therefore creates a new
component release even when the upstream program bytes are unchanged.

Directly fetched dependencies (`lxcfs`, `raft`, `cowsql`, `libaio`, `usbredir`
and `lighthost-dhcp-release`) remain source-built feed packages. They do not get
component releases unless their prebuilt IPKs become a supported public
download contract.

## Version and tag rules

- `componentVersion` identifies the program or content version.
- `packageRelease` identifies the OpenWrt packaging revision.
- `packageVersion` is the exact version reported by the IPK.
- Incus additionally records `programVersion`, for example
  `6.0.6-lighthost.3`; it is not interchangeable with the package release.
- Dates, architecture and source commit belong in asset names or
  `BUILD-INFO.json`, not in the tag identity.

Tags use `<component>-v<componentVersion>-r<packageRelease>`. Existing dotted
UI child releases retain their reviewed spelling, for example
`lighthost-ui-v0.3.0-r87.1`.

Tags and published assets are immutable. A correction increments the component
or package release; it never replaces an existing asset.

## Repository responsibilities

- `linkease/linkease-lighthost` owns product compilation and product tests.
- `istoreos/lighthost-packages` owns OpenWrt recipes, component manifests,
  publication and public-download verification.
- The isolated builder owns batch-local toolchains and build logs, but is not a
  durable source of released artifacts.
- A release-set manifest records qualification composition without copying
  component assets into an omnibus Release.

## Formal source identity

Every source identity must be a committed Git object and include component
paths. Worktree-only snapshots are rejected. A manifest binds both the product
source commit and the feed commit, so a change to either program code or
packaging code is visible.

For patched third-party components, the source identity is the committed
LightHost integration directory that owns the recipe, patch set and upstream
lock. The upstream repository and revision remain immutable inputs recorded in
that lock and in the attached source offer; they are not a second release tag
identity. This keeps change planning unambiguous: changing
`openwrt-feed/incus/` selects only `incus`, and changing
`openwrt-feed/qemu-firmware/` selects only `lighthost-qemu-firmware`.

## Legacy migration

`release/model/legacy-istorework-packages-20261014.json` inventories all 15
uploaded assets from the historical mixed Release. GitHub displays 17 entries
because it adds two automatic repository source archives. The combined LightHost input is
explicitly classified as a legacy mixed asset and must not be reused as a new
component input.

