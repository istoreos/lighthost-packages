include $(TOPDIR)/rules.mk

PKG_NAME:=incus
PKG_VERSION:=6.0.6
PKG_RELEASE:=1

PKG_SOURCE_VERSION:=184ad2c3fb47775dfa0a64f193edfce22c22e5ae
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION)-$(PKG_SOURCE_VERSION).tar.gz
PKG_SOURCE_URL:=https://github.com/lxc/incus.git
PKG_SOURCE_PROTO:=git
PKG_MIRROR_HASH:=1cc302b11f63e5a1420304d48dd3563bcf0c325748654ec549af0b83c61b04a6

PKG_MAINTAINER:=LinkEase <support@linkease.com>
PKG_LICENSE:=Apache-2.0
PKG_LICENSE_FILES:=COPYING
PKG_BUILD_PARALLEL:=1

include $(INCLUDE_DIR)/package.mk

define Package/incus
  SECTION:=admin
  CATEGORY:=Administration
  TITLE:=LightHost system-container runtime based on Incus 6.0 LTS
  URL:=https://linuxcontainers.org/incus/
  DEPENDS:=+libacl +libcap +libcowsql +liblxc +libsqlite3 +libudev-zero +libuv +libpthread \
	+lxc-common +lxc-configs +lxc-hooks +lxc-init +lxc-monitord +lxc-user-nic \
	+lxcfs +rsync +squashfs-tools-unsquashfs
endef

define Package/incus/description
 Incus daemon and local command-line client for the LightHost system-container
 runtime. This package intentionally excludes QEMU and VM helper binaries.
endef

INCUS_GO:=$(LIGHTHOST_GO_ROOT)/bin/go
INCUS_GO_CACHE:=$(TMP_DIR)/go-build-incus-$(PKG_VERSION)

define Build/Compile
	test -x "$(INCUS_GO)"
	mkdir -p "$(PKG_BUILD_DIR)/bin" "$(INCUS_GO_CACHE)"
	cd "$(PKG_BUILD_DIR)" && \
		PATH="$(STAGING_DIR_HOST)/bin:$$$$PATH" \
		GOOS=linux GOARCH=amd64 GOAMD64=v1 \
		GOTOOLCHAIN=local GOPROXY=off GOSUMDB=off GOFLAGS=-mod=vendor \
		GOCACHE="$(INCUS_GO_CACHE)" CGO_ENABLED=1 \
		CC="$(TARGET_CC)" CXX="$(TARGET_CXX)" \
		CGO_CFLAGS="$(TARGET_CFLAGS) -Wno-error=format-nonliteral" \
		CGO_CPPFLAGS="$(TARGET_CPPFLAGS)" \
		CGO_CXXFLAGS="$(TARGET_CXXFLAGS)" \
		CGO_LDFLAGS="$(TARGET_LDFLAGS)" \
		CGO_LDFLAGS_ALLOW='(-Wl,-wrap,pthread_create)|(-Wl,-z,now)' \
		PKG_CONFIG="$(STAGING_DIR_HOST)/bin/pkg-config" \
		"$(INCUS_GO)" build -buildvcs=false -trimpath -tags libsqlite3 \
			-ldflags "-X github.com/lxc/incus/v6/internal/version.Version=$(PKG_VERSION)-lighthost.$(PKG_RELEASE)" \
			-o bin/incusd ./cmd/incusd
	cd "$(PKG_BUILD_DIR)" && \
		PATH="$(STAGING_DIR_HOST)/bin:$$$$PATH" \
		GOOS=linux GOARCH=amd64 GOAMD64=v1 \
		GOTOOLCHAIN=local GOPROXY=off GOSUMDB=off GOFLAGS=-mod=vendor \
		GOCACHE="$(INCUS_GO_CACHE)" CGO_ENABLED=1 \
		CC="$(TARGET_CC)" CXX="$(TARGET_CXX)" \
		CGO_CFLAGS="$(TARGET_CFLAGS) -Wno-error=format-nonliteral" \
		CGO_CPPFLAGS="$(TARGET_CPPFLAGS)" \
		CGO_CXXFLAGS="$(TARGET_CXXFLAGS)" \
		CGO_LDFLAGS="$(TARGET_LDFLAGS)" \
		CGO_LDFLAGS_ALLOW='(-Wl,-wrap,pthread_create)|(-Wl,-z,now)' \
		PKG_CONFIG="$(STAGING_DIR_HOST)/bin/pkg-config" \
		"$(INCUS_GO)" build -buildvcs=false -trimpath -tags libsqlite3 \
			-ldflags "-X github.com/lxc/incus/v6/internal/version.Version=$(PKG_VERSION)-lighthost.$(PKG_RELEASE)" \
			-o bin/incus ./cmd/incus
endef

define Package/incus/install
	$(INSTALL_DIR) $(1)/usr/bin $(1)/usr/sbin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/bin/incus $(1)/usr/bin/incus
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/bin/incusd $(1)/usr/sbin/incusd
endef

$(eval $(call BuildPackage,incus))
