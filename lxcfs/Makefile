include $(TOPDIR)/rules.mk

PKG_NAME:=lxcfs
PKG_VERSION:=6.0.6
PKG_RELEASE:=3

PKG_SOURCE_VERSION:=9825a7986f1d7ff8c727331cc3e1b87b4e01c458
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION)-$(PKG_SOURCE_VERSION).tar.gz
PKG_SOURCE_URL:=https://github.com/lxc/lxcfs.git
PKG_SOURCE_PROTO:=git
PKG_MIRROR_HASH:=e7f5057b95f127e15acdbca37d4b5ae6ac4ae59a4ca8e821bf5c68999b3104d3

PKG_MAINTAINER:=LinkEase <support@linkease.com>
PKG_LICENSE:=LGPL-2.1-or-later
PKG_LICENSE_FILES:=COPYING LICENSE.LGPL2.1
PKG_BUILD_PARALLEL:=1
PKG_INSTALL:=1

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/meson.mk

define Package/lxcfs
  SECTION:=utils
  CATEGORY:=Utilities
  TITLE:=FUSE filesystem for Linux container resource views
  URL:=https://github.com/lxc/lxcfs
  DEPENDS:=+libfuse3 +libpthread
endef

define Package/lxcfs/description
 LXCFS provides container-aware proc, sysfs and cgroup views through FUSE.
 This package is built from the LightHost-locked LXCFS 6.0 LTS source.
endef

MESON_ARGS += \
	-Ddocs=false \
	-Dtests=false \
	-Dmocks=false \
	-Dfuse-version=3 \
	-Dinit-script=[] \
	-Druntime-path=/var/run

define Package/lxcfs/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/bin/lxcfs $(1)/usr/bin/lxcfs
	$(INSTALL_DIR) $(1)/usr/lib/lxcfs
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/lxcfs/liblxcfs.so $(1)/usr/lib/lxcfs/
	$(INSTALL_DIR) $(1)/usr/share/lxcfs
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/share/lxcfs/lxc.mount.hook $(1)/usr/share/lxcfs/
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/share/lxcfs/lxc.reboot.hook $(1)/usr/share/lxcfs/
	$(INSTALL_DIR) $(1)/usr/share/lxc/config/common.conf.d
	$(INSTALL_CONF) $(PKG_INSTALL_DIR)/usr/share/lxc/config/common.conf.d/00-lxcfs.conf \
		$(1)/usr/share/lxc/config/common.conf.d/00-lxcfs.conf
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./files/lxcfs.init $(1)/etc/init.d/lxcfs
endef

$(eval $(call BuildPackage,lxcfs))
