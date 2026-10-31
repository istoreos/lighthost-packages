include $(TOPDIR)/rules.mk

PKG_NAME:=lighthost-ui
PKG_VERSION:=0.3.0
PKG_RELEASE:=87.2
PKG_SOURCE:=lighthost-ui-$(PKG_VERSION)-r87.2-x86_64.tar.gz
PKG_SOURCE_URL:=https://github.com/istoreos/lighthost-packages/releases/download/lighthost-ui-v0.3.0-r87.2/
PKG_HASH:=0b7243702f7dc52e40e01b994702c8e4964294440cef39eb6b2ff5e110b5f692
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)
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
	find $(1) -type d -exec chmod g-s {} +
endef

$(eval $(call BuildPackage,lighthost-ui))

