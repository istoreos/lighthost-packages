include $(TOPDIR)/rules.mk

PKG_NAME:=lighthost
PKG_VERSION:=0.3.0
PKG_RELEASE:=82
PKG_SOURCE:=lighthost-$(PKG_VERSION)-r82-65cf9c4d8171-x86_64.tar.gz
PKG_SOURCE_URL:=https://github.com/istoreos/istorework-packages/releases/download/lighthost-public-build-inputs-20261014/
PKG_HASH:=b1521a479326e9f442156972fe0a2d53a21edc862b2b27b50bcc1cc419491975
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)
PKG_MAINTAINER:=LinkEase <support@linkease.com>
PKG_LICENSE:=UNLICENSED GPL-3.0-or-later LGPL-3.0-or-later
PKG_BUILD_PARALLEL:=1

include $(INCLUDE_DIR)/package.mk

# Keep the already-stripped, SHA-bound Release binary bytes unchanged.
RSTRIP:=:
STRIP:=:

define Package/lighthost
  SECTION:=admin
  CATEGORY:=Administration
  TITLE:=LightHost control plane
  URL:=https://github.com/linkease/linkease-lighthost
  DEPENDS:=@TARGET_x86_64 +ca-bundle +curl +coreutils-base64 +libsqlite3 +shadow-groupadd +shadow-useradd +block-mount +jsonfilter +mount-utils
endef

define Package/lighthost/description
 LightHost manages an existing native Incus runtime through a non-root control
 daemon and a narrowly scoped root helper. Readiness checks enforce the runtime
 contract. S4 adds EXT4-compatible snapshots, isolated backups and custom data
 volumes. A unified runtime may include QEMU/KVM, while the public VM product
 capability remains disabled until its independent product gates pass.
endef

define Package/lighthost/conffiles
/etc/config/lighthost
/etc/lighthost/usb/allowlist.json
endef

define Package/lighthost/postinst
#!/bin/sh
if [ -z "$${IPKG_INSTROOT}" ]; then
	grep -q '^lighthost:' /etc/group || groupadd --system lighthost
	grep -q '^lighthost:' /etc/passwd || \
		useradd --system --gid lighthost --home-dir /var/run/lighthost \
			--shell /bin/false --no-create-home lighthost
	ubusd_pids="$$(pidof ubusd 2>/dev/null || true)"
	[ -z "$${ubusd_pids}" ] || kill -HUP $${ubusd_pids}
	[ ! -x /etc/init.d/rpcd ] || /etc/init.d/rpcd reload >/dev/null 2>&1 || true
fi
exit 0
endef

define Package/lighthost/prerm
#!/bin/sh
if [ -z "$${IPKG_INSTROOT}" ] && [ -x /etc/init.d/lighthost ]; then
	/etc/init.d/lighthost stop >/dev/null 2>&1 || true
fi
exit 0
endef

define Package/lighthost/postrm
#!/bin/sh
if [ -z "$${IPKG_INSTROOT}" ]; then
	[ ! -x /etc/init.d/rpcd ] || /etc/init.d/rpcd reload >/dev/null 2>&1 || true
fi
exit 0
endef

define Package/lighthost-ui
  SECTION:=admin
  CATEGORY:=Administration
  TITLE:=LightHost LinkEase Desktop interface
  URL:=https://github.com/linkease/linkease-lighthost
  DEPENDS:=+lighthost +lighthost-spice-console +linkeasefull
endef

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

# Assets were compiled from the frozen source listed in BUILD-INFO.json.
# Consumers only verify/repackage the pinned x86_64 musl input.
define Build/Configure
endef

define Build/Compile
	test "$(ARCH)" = x86_64
	cd $(PKG_BUILD_DIR) && sha256sum -c PAYLOAD.SHA256
endef

define Package/lighthost/install
	$(INSTALL_DIR) $(1)/usr/sbin $(1)/usr/bin $(1)/usr/share/lighthost \
		$(1)/etc/init.d $(1)/etc/config $(1)/usr/share/acl.d
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/bin/lighthost $(1)/usr/sbin/lighthost
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/bin/lighthost-vm-pilot-policy $(1)/usr/bin/lighthost-vm-pilot-policy
	$(INSTALL_BIN) ./files/lighthost-vm-pilot-policy $(1)/usr/sbin/lighthost-vm-pilot-policy
	$(INSTALL_BIN) ./files/lighthost.init $(1)/etc/init.d/lighthost
	$(INSTALL_BIN) ./files/lighthost-ready $(1)/usr/bin/lighthost-ready
	$(INSTALL_BIN) ./files/lighthost-diagnostics $(1)/usr/sbin/lighthost-diagnostics
	$(INSTALL_BIN) ./files/lighthost-purge $(1)/usr/sbin/lighthost-purge
	$(INSTALL_BIN) ./files/lighthost-repository-resolve $(1)/usr/sbin/lighthost-repository-resolve
	$(INSTALL_CONF) ./files/lighthost.config $(1)/etc/config/lighthost
	$(INSTALL_DIR) $(1)/etc/lighthost/usb
	chmod 0750 $(1)/etc/lighthost/usb
	$(INSTALL_CONF) ./files/usb-allowlist.json $(1)/etc/lighthost/usb/allowlist.json
	$(INSTALL_DATA) ./files/lighthost-ubus-acl.json $(1)/usr/share/acl.d/lighthost.json
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/release/images.x86_64-2410.lock.tsv $(1)/usr/share/lighthost/images.x86_64-2410.lock.tsv
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/release/vm-media-sources.x86_64-2410.lock.tsv $(1)/usr/share/lighthost/vm-media-sources.x86_64-2410.lock.tsv
	$(INSTALL_DIR) $(1)/usr/share/licenses/lighthost
	$(CP) $(PKG_BUILD_DIR)/licenses/. $(1)/usr/share/licenses/lighthost/
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/BUILD-INFO.json $(1)/usr/share/lighthost/build-info.json
	printf '%s\n' '$(PKG_VERSION)-r$(PKG_RELEASE)' > $(1)/usr/share/lighthost/release
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

define Package/lighthost-spice-console/install
	$(INSTALL_DIR) $(1)/usr/share/lighthost/www/spice-console
	$(CP) $(PKG_BUILD_DIR)/spice-console/. $(1)/usr/share/lighthost/www/spice-console/
endef

$(eval $(call BuildPackage,lighthost))
$(eval $(call BuildPackage,lighthost-ui))
$(eval $(call BuildPackage,lighthost-spice-console))
