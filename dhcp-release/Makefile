include $(TOPDIR)/rules.mk

PKG_NAME:=lighthost-dhcp-release
PKG_VERSION:=2.90
PKG_RELEASE:=1

PKG_SOURCE:=dnsmasq-$(PKG_VERSION).tar.xz
PKG_SOURCE_URL:=https://thekelleys.org.uk/dnsmasq/
PKG_HASH:=8e50309bd837bfec9649a812e066c09b6988b73d749b7d293c06c57d46a109e4
PKG_BUILD_DIR:=$(BUILD_DIR)/dnsmasq-$(PKG_VERSION)

PKG_MAINTAINER:=LinkEase <support@linkease.com>
PKG_LICENSE:=GPL-2.0
PKG_LICENSE_FILES:=COPYING

include $(INCLUDE_DIR)/package.mk

define Package/lighthost-dhcp-release
  SECTION:=utils
  CATEGORY:=Utilities
  TITLE:=Scoped DHCP lease release helper for LightHost VM gates
  URL:=https://thekelleys.org.uk/dnsmasq/
  DEPENDS:=+libc +libgcc
endef

define Package/lighthost-dhcp-release/description
 Builds only dnsmasq's upstream dhcp_release utility. LightHost uses it to
 release leases belonging to its dedicated VM Gate MAC without restarting or
 reconfiguring the host DHCP/DNS service.
endef

define Build/Compile
	$(TARGET_CC) $(TARGET_CFLAGS) $(TARGET_LDFLAGS) \
		-o $(PKG_BUILD_DIR)/lighthost-dhcp-release \
		$(PKG_BUILD_DIR)/contrib/lease-tools/dhcp_release.c
endef

define Package/lighthost-dhcp-release/install
	$(INSTALL_DIR) $(1)/usr/libexec $(1)/usr/share/licenses/lighthost-dhcp-release
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/lighthost-dhcp-release $(1)/usr/libexec/
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/COPYING \
		$(1)/usr/share/licenses/lighthost-dhcp-release/
endef

$(eval $(call BuildPackage,lighthost-dhcp-release))
