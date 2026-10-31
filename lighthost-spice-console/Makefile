include $(TOPDIR)/rules.mk

PKG_NAME:=lighthost-spice-console
PKG_VERSION:=0.3.0
PKG_RELEASE:=82
# M1 preserves the historical combined input. M3 replaces it with a
# component-only archive without changing the installed payload.
PKG_SOURCE:=lighthost-$(PKG_VERSION)-r82-65cf9c4d8171-x86_64.tar.gz
PKG_SOURCE_URL:=https://github.com/istoreos/istorework-packages/releases/download/lighthost-public-build-inputs-20261014/
PKG_HASH:=b1521a479326e9f442156972fe0a2d53a21edc862b2b27b50bcc1cc419491975
PKG_BUILD_DIR:=$(BUILD_DIR)/lighthost-$(PKG_VERSION)
PKG_MAINTAINER:=LinkEase <support@linkease.com>
PKG_LICENSE:=GPL-3.0-or-later LGPL-3.0-or-later
PKG_LICENSE_FILES:=LICENSE vendor/spice/COPYING vendor/spice/COPYING.LESSER

include $(INCLUDE_DIR)/package.mk

define Package/lighthost-spice-console
  SECTION:=admin
  CATEGORY:=Administration
  TITLE:=LightHost SPICE graphical console
  URL:=https://github.com/linkease/linkease-lighthost
  DEPENDS:=+lighthost
endef

define Package/lighthost-spice-console/description
 Independently delivered GPL-3.0 graphical console adapter with the
 LGPL-3.0-or-later spice-html5 browser library.
endef

define Build/Configure
endef

define Build/Compile
	test "$(ARCH)" = x86_64
	cd $(PKG_BUILD_DIR) && sha256sum -c PAYLOAD.SHA256
endef

define Package/lighthost-spice-console/install
	$(INSTALL_DIR) $(1)/usr/share/lighthost/www/spice-console
	$(CP) $(PKG_BUILD_DIR)/spice-console/. $(1)/usr/share/lighthost/www/spice-console/
endef

$(eval $(call BuildPackage,lighthost-spice-console))

