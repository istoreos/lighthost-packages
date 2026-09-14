include $(TOPDIR)/rules.mk

PKG_NAME:=cowsql
PKG_VERSION:=1.15.9
PKG_RELEASE:=1

PKG_SOURCE_VERSION:=7c4d73151969ead4f81077ae243d81396ce67988
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION)-$(PKG_SOURCE_VERSION).tar.gz
PKG_SOURCE_URL:=https://github.com/cowsql/cowsql.git
PKG_SOURCE_PROTO:=git
PKG_MIRROR_HASH:=a93044ef49e483c00980597185d88dd2f7b462ee0476665015492508c574851a

PKG_MAINTAINER:=LinkEase <support@linkease.com>
PKG_LICENSE:=LGPL-3.0-only-with-linking-exception
PKG_LICENSE_FILES:=LICENSE
PKG_FIXUP:=autoreconf
PKG_BUILD_PARALLEL:=1
PKG_INSTALL:=1

include $(INCLUDE_DIR)/package.mk

define Package/libcowsql
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=High-availability SQLite replication library
  URL:=https://github.com/cowsql/cowsql
  DEPENDS:=+libraft +libsqlite3 +libuv +libpthread
endef

define Package/libcowsql/description
 cowsql provides replicated SQLite storage for the LightHost Incus runtime.
endef

CONFIGURE_ARGS += \
	--disable-build-sqlite \
	--disable-debug \
	--disable-sanitize \
	--disable-backtrace

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include
	$(INSTALL_DATA) $(PKG_INSTALL_DIR)/usr/include/cowsql.h $(1)/usr/include/
	$(INSTALL_DIR) $(1)/usr/lib/pkgconfig
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libcowsql.{a,so*} $(1)/usr/lib/
	$(INSTALL_DATA) $(PKG_INSTALL_DIR)/usr/lib/pkgconfig/cowsql.pc $(1)/usr/lib/pkgconfig/
endef

define Package/libcowsql/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libcowsql.so.* $(1)/usr/lib/
endef

$(eval $(call BuildPackage,libcowsql))
