include $(TOPDIR)/rules.mk

PKG_NAME:=libaio
PKG_VERSION:=0.3.113
PKG_RELEASE:=1
PKG_SOURCE:=$(PKG_NAME)_$(PKG_VERSION).orig.tar.gz
PKG_SOURCE_URL:=https://deb.debian.org/debian/pool/main/liba/libaio/
PKG_HASH:=2c44d1c5fd0d43752287c9ae1eb9c023f04ef848ea8d4aafa46e9aedb678200b
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)
PKG_LICENSE:=LGPL-2.1-or-later
PKG_LICENSE_FILES:=COPYING
PKG_MAINTAINER:=LightHost maintainers
PKG_INSTALL:=1
PKG_BUILD_PARALLEL:=1

include $(INCLUDE_DIR)/package.mk

define Package/libaio
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=Linux native asynchronous I/O library
  URL:=https://pagure.io/libaio/
endef

define Package/libaio/description
 The userspace library for the Linux native asynchronous I/O system calls.
endef

define Build/Compile
	+$(MAKE) $(PKG_JOBS) -C $(PKG_BUILD_DIR) \
		$(TARGET_CONFIGURE_OPTS) \
		CFLAGS="$(TARGET_CFLAGS) -fPIC -I$(PKG_BUILD_DIR)/src" \
		LDFLAGS="$(TARGET_LDFLAGS)" \
		ENABLE_SHARED=1
endef

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/include/libaio.h $(1)/usr/include/
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libaio.a $(1)/usr/lib/
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libaio.so* $(1)/usr/lib/
endef

define Package/libaio/install
	$(INSTALL_DIR) $(1)/usr/lib $(1)/usr/share/licenses/libaio
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libaio.so.* $(1)/usr/lib/
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/COPYING $(1)/usr/share/licenses/libaio/
endef

$(eval $(call BuildPackage,libaio))
