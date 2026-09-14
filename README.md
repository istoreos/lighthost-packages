# LightHost OpenWrt feed

This feed contains native runtime dependencies that are not provided by the
locked iStoreOS 24.10 feeds. Every package source is pinned to the full commit
recorded in `upstream/sources.lock` and downloaded from the corresponding
official GitHub codeload endpoint with a SHA-256 check.

Current build order:

1. `lxcfs`
2. `raft`
3. `cowsql`

The build entry point is `scripts/build-env.sh`; do not copy these packages
manually into the shared iStoreOS source tree.
