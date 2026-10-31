include $(TOPDIR)/rules.mk

PKG_NAME:=lighthost-ui
PKG_VERSION:=0.3.0
PKG_RELEASE:=82
# M1 preserves the historical combined input. M3 replaces it with a
# component-only archive without changing the installed payload.
PKG_SOURCE:=lighthost-$(PKG_VERSION)-r82-65cf9c4d8171-x86_64.tar.gz
PKG_SOURCE_URL:=https://github.com/istoreos/istorework-packages/releases/download/lighthost-public-build-inputs-20261014/
PKG_HASH:=b1521a479326e9f442156972fe0a2d53a21edc862b2b27b50bcc1cc419491975
PKG_BUILD_DIR:=$(BUILD_DIR)/lighthost-$(PKG_VERSION)
PKG_MAINTAINER:=LinkEase <support@linkease.com>
PKG_LICENSE:=UNLICENSED

include $(INCLUDE_DIR)/package.mk

define Package/lighthost-ui
  SECTION:=admin
  CATEGORY:=Administration
  TITLE:=LightHost LinkEase Desktop interface
  URL:=https://github.com/linkease/linkease-lighthost
  DEPENDS:=+lighthost +lighthost-spice-console +linkeasefull
endef

define Package/lighthost-ui/description
 React interface and LinkEaseFull plugin manifest for the LightHost control plane.
endef

define Package/lighthost-ui/prerm
#!/bin/sh
if [ -z "$${IPKG_INSTROOT}" ]; then
	link=/usr/share/linkeasefull/desktop-apps.d/25-lighthost-plugin.json
	[ "$$(readlink "$${link}" 2>/dev/null)" != "/usr/share/lighthost/lighthost-plugin.json" ] || rm -f "$${link}"
fi
exit 0
endef

define Build/Configure
endef

define Build/Compile
	test "$(ARCH)" = x86_64
	cd $(PKG_BUILD_DIR) && sha256sum -c PAYLOAD.SHA256
endef

define Package/lighthost-ui/install
	$(INSTALL_DIR) $(1)/usr/share/lighthost/www \
		$(1)/usr/share/linkeasefull/desktop-apps.d
	$(CP) $(PKG_BUILD_DIR)/frontend-dist/. $(1)/usr/share/lighthost/www/
	$(INSTALL_DATA) ./files/logo.svg $(1)/usr/share/lighthost/www/logo.svg
	$(INSTALL_DATA) ./files/lighthost-plugin.json $(1)/usr/share/lighthost/lighthost-plugin.json
	ln -sf /usr/share/lighthost/lighthost-plugin.json \
		$(1)/usr/share/linkeasefull/desktop-apps.d/25-lighthost-plugin.json
endef

$(eval $(call BuildPackage,lighthost-ui))

