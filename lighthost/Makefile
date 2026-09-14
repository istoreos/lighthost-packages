include $(TOPDIR)/rules.mk

PKG_NAME:=lighthost
PKG_VERSION:=0.3.0
PKG_RELEASE?=1
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)
PKG_MAINTAINER:=LinkEase <support@linkease.com>
PKG_LICENSE:=UNLICENSED
PKG_BUILD_PARALLEL:=1

include $(INCLUDE_DIR)/package.mk

LIGHTHOST_SOURCE_ROOT?=$(CURDIR)/../../..
LIGHTHOST_GO?=$(LIGHTHOST_GO_ROOT)/bin/go
LIGHTHOST_GOARCH?=amd64
LIGHTHOST_GO_CACHE:=$(TMP_DIR)/go-build-lighthost-$(PKG_VERSION)

define Package/lighthost
  SECTION:=admin
  CATEGORY:=Administration
  TITLE:=LightHost control plane
  URL:=https://github.com/linkease/linkease-lighthost
  DEPENDS:=+ca-bundle +libsqlite3 +shadow-groupadd +shadow-useradd
endef

define Package/lighthost/description
 LightHost manages an existing native Incus runtime through a non-root control
 daemon and a narrowly scoped root helper. Readiness checks enforce the runtime
 contract. S4 adds EXT4-compatible snapshots, isolated backups and custom data
 volumes; QEMU, KVM and root-disk quotas remain intentionally excluded.
endef

define Package/lighthost/conffiles
/etc/config/lighthost
endef

define Package/lighthost/postinst
#!/bin/sh
if [ -z "$${IPKG_INSTROOT}" ]; then
	grep -q '^lighthost:' /etc/group || groupadd --system lighthost
	grep -q '^lighthost:' /etc/passwd || \
		useradd --system --gid lighthost --home-dir /var/run/lighthost \
			--shell /bin/false --no-create-home lighthost
	killall -s HUP ubusd >/dev/null 2>&1 || true
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
	killall -s HUP ubusd >/dev/null 2>&1 || true
fi
exit 0
endef

define Package/lighthost-ui
  SECTION:=admin
  CATEGORY:=Administration
  TITLE:=LightHost LinkEase Desktop interface
  URL:=https://github.com/linkease/linkease-lighthost
  DEPENDS:=+lighthost +linkeasefull
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

define Build/Prepare
	rm -rf $(PKG_BUILD_DIR)
	$(INSTALL_DIR) $(PKG_BUILD_DIR)/backend $(PKG_BUILD_DIR)/frontend-dist
	test -f "$(LIGHTHOST_SOURCE_ROOT)/backend/go.mod"
	test -f "$(LIGHTHOST_SOURCE_ROOT)/frontend/dist/index.html"
	$(CP) $(LIGHTHOST_SOURCE_ROOT)/backend/. $(PKG_BUILD_DIR)/backend/
	$(CP) $(LIGHTHOST_SOURCE_ROOT)/frontend/dist/. $(PKG_BUILD_DIR)/frontend-dist/
endef

define Build/Compile
	test -x "$(LIGHTHOST_GO)"
	$(INSTALL_DIR) $(PKG_BUILD_DIR)/bin $(LIGHTHOST_GO_CACHE)
	cd $(PKG_BUILD_DIR)/backend && \
		PATH="$(STAGING_DIR_HOST)/bin:$$$$PATH" \
		GOOS=linux GOARCH=$(LIGHTHOST_GOARCH) GOAMD64=v1 \
		GOTOOLCHAIN=local GOPROXY=off GOSUMDB=off GOFLAGS=-mod=vendor \
		GOCACHE="$(LIGHTHOST_GO_CACHE)" CGO_ENABLED=1 \
		CC="$(TARGET_CC)" CXX="$(TARGET_CXX)" \
		CGO_CFLAGS="$(TARGET_CFLAGS)" \
		CGO_CPPFLAGS="$(TARGET_CPPFLAGS)" \
		CGO_CXXFLAGS="$(TARGET_CXXFLAGS)" \
		CGO_LDFLAGS="$(TARGET_LDFLAGS)" \
		PKG_CONFIG="$(STAGING_DIR_HOST)/bin/pkg-config" \
		"$(LIGHTHOST_GO)" build -buildvcs=false -trimpath \
			-ldflags "-s -w -X main.releaseID=$(PKG_VERSION)-r$(PKG_RELEASE)" \
			-o $(PKG_BUILD_DIR)/bin/lighthost ./cmd/lighthost
endef

define Package/lighthost/install
	$(INSTALL_DIR) $(1)/usr/sbin $(1)/usr/bin $(1)/usr/share/lighthost \
		$(1)/etc/init.d $(1)/etc/config $(1)/usr/share/acl.d
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/bin/lighthost $(1)/usr/sbin/lighthost
	$(INSTALL_BIN) ./files/lighthost.init $(1)/etc/init.d/lighthost
	$(INSTALL_BIN) ./files/lighthost-ready $(1)/usr/bin/lighthost-ready
	$(INSTALL_BIN) ./files/lighthost-diagnostics $(1)/usr/sbin/lighthost-diagnostics
	$(INSTALL_BIN) ./files/lighthost-purge $(1)/usr/sbin/lighthost-purge
	$(INSTALL_CONF) ./files/lighthost.config $(1)/etc/config/lighthost
	$(INSTALL_DATA) ./files/lighthost-ubus-acl.json $(1)/usr/share/acl.d/lighthost.json
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

$(eval $(call BuildPackage,lighthost))
$(eval $(call BuildPackage,lighthost-ui))
