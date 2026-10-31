include $(TOPDIR)/rules.mk

PKG_NAME:=incus
PKG_VERSION:=6.0.6
PKG_RELEASE:=3

PKG_SOURCE:=incus-$(PKG_VERSION)-lighthost.3-r3-x86_64.tar.gz
PKG_SOURCE_URL:=https://github.com/istoreos/lighthost-packages/releases/download/incus-v6.0.6-lighthost.3-r3/
PKG_HASH:=3dcb9c140d31f601c5f7ca89ade7659cdd8b028355658a03dc1b8d6e7b00bbc8
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)

PKG_MAINTAINER:=LinkEase <support@linkease.com>
PKG_LICENSE:=Apache-2.0
PKG_LICENSE_FILES:=COPYING
PKG_BUILD_PARALLEL:=1

include $(INCLUDE_DIR)/package.mk

# Keep the already-stripped, SHA-bound Release binary bytes unchanged.
RSTRIP:=:
STRIP:=:

define Package/incus
  SECTION:=admin
  CATEGORY:=Administration
  TITLE:=LightHost system-container runtime based on Incus 6.0 LTS
  URL:=https://linuxcontainers.org/incus/
  DEPENDS:=@TARGET_x86_64 +libgcc +libacl +libcap +libcowsql +liblxc +libsqlite3 +libudev-zero +libuv +libpthread \
	+lxc-common +lxc-configs +lxc-hooks +lxc-init +lxc-monitord +lxc-user-nic \
	+lxcfs +rsync +squashfs-tools-unsquashfs
endef

define Package/incus/description
 Incus daemon and local command-line client for the LightHost system-container
 runtime. This package intentionally excludes QEMU and VM helper binaries.
endef

define Package/incus-agent
  SECTION:=admin
  CATEGORY:=Administration
  TITLE:=LightHost Incus virtual-machine guest agent
  URL:=https://linuxcontainers.org/incus/
endef

define Package/incus-agent/description
 Version-locked Incus agent injected into LightHost virtual machines. It is a
 separate package so the system-container release does not gain VM helpers.
endef

# Source patches are already applied in the published payload.
define Build/Patch
endef

# The source patch offer accompanies this prebuilt input in the same Release.
define Build/Configure
endef

define Build/Compile
	test "$(ARCH)" = x86_64
	cd $(PKG_BUILD_DIR) && sha256sum -c PAYLOAD.SHA256
endef

define Package/incus/install
	$(INSTALL_DIR) $(1)/usr/bin $(1)/usr/sbin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/bin/incus $(1)/usr/bin/incus
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/bin/incusd $(1)/usr/sbin/incusd
	find $(1) -type d -exec chmod g-s {} +
endef

define Package/incus-agent/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/bin/incus-agent $(1)/usr/bin/incus-agent
	find $(1) -type d -exec chmod g-s {} +
endef

$(eval $(call BuildPackage,incus))
$(eval $(call BuildPackage,incus-agent))
