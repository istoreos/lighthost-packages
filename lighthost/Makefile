include $(TOPDIR)/rules.mk

PKG_NAME:=lighthost
PKG_VERSION:=0.3.0
PKG_RELEASE:=87
PKG_SOURCE:=lighthost-$(PKG_VERSION)-r87-x86_64.tar.gz
PKG_SOURCE_URL:=https://github.com/istoreos/lighthost-packages/releases/download/lighthost-v0.3.0-r87/
PKG_HASH:=d7109a24e98dc92441566c828d2c2ed5c1b82738e178098d3a0a1a98003cbc00
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)
PKG_MAINTAINER:=LinkEase <support@linkease.com>
PKG_LICENSE:=UNLICENSED
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
	$(INSTALL_DIR) $(1)/usr/share/lighthost/licenses
	$(CP) $(PKG_BUILD_DIR)/licenses/. $(1)/usr/share/lighthost/licenses/
	printf '%s\n' '$(PKG_VERSION)-r$(PKG_RELEASE)' > $(1)/usr/share/lighthost/release
	find $(1) -type d -exec chmod g-s {} +
endef

$(eval $(call BuildPackage,lighthost))
