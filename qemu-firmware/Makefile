include $(TOPDIR)/rules.mk

PKG_NAME:=lighthost-qemu-firmware
PKG_VERSION:=202302
PKG_RELEASE:=2
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION)-r2-x86_64.tar.gz
PKG_SOURCE_URL:=https://github.com/istoreos/lighthost-packages/releases/download/lighthost-qemu-firmware-v202302-r2/
PKG_HASH:=2f4ae7144fa1610bcd3655b4704532088c783bf9910601438a6d929be066dd47
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)
PKG_MAINTAINER:=LinkEase <support@linkease.com>
PKG_LICENSE:=BSD-2-Clause-Patent BSD-2-Clause OpenSSL
PKG_LICENSE_FILES:=edk2-licenses.txt Microsoft-License.txt

include $(INCLUDE_DIR)/package.mk

define Package/lighthost-qemu-firmware
  SECTION:=utils
  CATEGORY:=Utilities
  SUBMENU:=Virtualization
  TITLE:=Pinned x86_64 EDK2 firmware for LightHost
  URL:=https://www.qemu.org/
  DEPENDS:=@TARGET_x86_64
endef

define Package/lighthost-qemu-firmware/description
 QEMU 9.1.3 EDK2 stable202302 code and a source-locked Microsoft public
 certificate VARS template. Physical Windows qualification is separate.
endef

define Build/Configure
endef

define Build/Compile
	test "$(ARCH)" = x86_64
	cd $(PKG_BUILD_DIR) && sha256sum -c PAYLOAD.SHA256
endef

define Package/lighthost-qemu-firmware/install
	$(INSTALL_DIR) $(1)/usr/share/qemu $(1)/usr/share/licenses/lighthost-qemu-firmware
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/edk2-x86_64-code.fd $(1)/usr/share/qemu/
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/edk2-x86_64-secure-code.fd $(1)/usr/share/qemu/
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/edk2-i386-vars.fd $(1)/usr/share/qemu/
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/edk2-licenses.txt $(1)/usr/share/licenses/lighthost-qemu-firmware/
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/Microsoft-License.txt $(1)/usr/share/licenses/lighthost-qemu-firmware/
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/windows-vars-source.json $(1)/usr/share/licenses/lighthost-qemu-firmware/
endef

$(eval $(call BuildPackage,lighthost-qemu-firmware))
