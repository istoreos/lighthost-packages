include $(TOPDIR)/rules.mk

PKG_NAME:=usbredir
PKG_VERSION:=0.15.0
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.xz
PKG_SOURCE_URL:=https://www.spice-space.org/download/usbredir/
PKG_HASH:=6dc2a380277688a068191245dac2ab7063a552999d8ac3ad8e841c10ff050961

PKG_MAINTAINER:=LinkEase <support@linkease.com>
PKG_LICENSE:=LGPL-2.1-or-later
PKG_LICENSE_FILES:=COPYING.LIB
PKG_BUILD_DEPENDS:=libusb
PKG_INSTALL:=1

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/meson.mk

define Package/libusbredirparser
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=USB redirection protocol parser library
  URL:=https://gitlab.freedesktop.org/spice/usbredir
  ABI_VERSION:=1
endef

define Package/libusbredirparser/description
 The usbredir protocol parser used by QEMU's usb-redir guest device.
 This package does not enable host USB passthrough in LightHost.
endef

MESON_ARGS += \
	-Dfuzzing=disabled \
	-Dgit_werror=disabled \
	-Dstack_protector=enabled \
	-Dtests=disabled \
	-Dtools=disabled

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include
	$(INSTALL_DATA) $(PKG_INSTALL_DIR)/usr/include/usbredirfilter.h $(1)/usr/include/
	$(INSTALL_DATA) $(PKG_INSTALL_DIR)/usr/include/usbredirparser.h $(1)/usr/include/
	$(INSTALL_DATA) $(PKG_INSTALL_DIR)/usr/include/usbredirproto.h $(1)/usr/include/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libusbredirparser.so* $(1)/usr/lib/
	$(INSTALL_DIR) $(1)/usr/lib/pkgconfig
	$(INSTALL_DATA) $(PKG_INSTALL_DIR)/usr/lib/pkgconfig/libusbredirparser-0.5.pc \
		$(1)/usr/lib/pkgconfig/
endef

define Package/libusbredirparser/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libusbredirparser.so.* $(1)/usr/lib/
	$(INSTALL_DIR) $(1)/usr/share/licenses/libusbredirparser
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/COPYING.LIB \
		$(1)/usr/share/licenses/libusbredirparser/COPYING.LIB
endef

$(eval $(call BuildPackage,libusbredirparser))
