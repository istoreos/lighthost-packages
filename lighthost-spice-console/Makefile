include $(TOPDIR)/rules.mk

PKG_NAME:=lighthost-spice-console
PKG_VERSION:=0.3.0
PKG_RELEASE:=87
PKG_SOURCE:=lighthost-spice-console-$(PKG_VERSION)-r87-x86_64.tar.gz
PKG_SOURCE_URL:=https://github.com/istoreos/lighthost-packages/releases/download/lighthost-spice-console-v0.3.0-r87/
PKG_HASH:=d1196189dc0bc46eaa25677ee93d99aacc302c953ceda7f39def3a03e2c0f6db
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)
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
	find $(1) -type d -exec chmod g-s {} +
endef

$(eval $(call BuildPackage,lighthost-spice-console))

