include $(TOPDIR)/rules.mk

PKG_NAME:=raft
PKG_VERSION:=0.22.1
PKG_RELEASE:=1

PKG_SOURCE_VERSION:=148951f79a1ed529d6f112661a3067494f1a0917
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION)-$(PKG_SOURCE_VERSION).tar.gz
PKG_SOURCE_URL:=https://github.com/cowsql/raft.git
PKG_SOURCE_PROTO:=git
PKG_MIRROR_HASH:=a5aef2c784fb907d697e0197b9ac1d1465780bcc682bab255470cf352a1aaeb4

PKG_MAINTAINER:=LinkEase <support@linkease.com>
PKG_LICENSE:=LGPL-3.0-only-with-linking-exception
PKG_LICENSE_FILES:=LICENSE
PKG_FIXUP:=autoreconf
PKG_BUILD_PARALLEL:=1
PKG_INSTALL:=1

include $(INCLUDE_DIR)/package.mk

define Package/libraft
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=Asynchronous C implementation of the Raft consensus protocol
  URL:=https://github.com/cowsql/raft
  DEPENDS:=+libuv
endef

define Package/libraft/description
 Raft consensus library used by cowsql and the LightHost Incus runtime.
endef

CONFIGURE_ARGS += \
	--enable-uv \
	--without-lz4 \
	--disable-fixture \
	--disable-example \
	--disable-benchmark \
	--disable-debug \
	--disable-sanitize \
	--disable-backtrace \
	--disable-hardening

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include/raft
	$(INSTALL_DATA) $(PKG_INSTALL_DIR)/usr/include/raft.h $(1)/usr/include/
	$(INSTALL_DATA) $(PKG_INSTALL_DIR)/usr/include/raft/uv.h $(1)/usr/include/raft/
	$(INSTALL_DIR) $(1)/usr/lib/pkgconfig
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libraft.{a,so*} $(1)/usr/lib/
	$(INSTALL_DATA) $(PKG_INSTALL_DIR)/usr/lib/pkgconfig/raft.pc $(1)/usr/lib/pkgconfig/
endef

define Package/libraft/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libraft.so.* $(1)/usr/lib/
endef

$(eval $(call BuildPackage,libraft))
