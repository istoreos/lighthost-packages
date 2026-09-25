include $(TOPDIR)/rules.mk

PKG_NAME:=lighthost-qemu-firmware
PKG_VERSION:=202302
PKG_RELEASE:=1

QEMU_SOURCE_VERSION:=9.1.3
PKG_SOURCE:=qemu-$(QEMU_SOURCE_VERSION).tar.xz
PKG_SOURCE_URL:=https://download.qemu.org/
PKG_HASH:=480a77a0ed13a9b39415f639aa020b4eb0d7cc5a52569510dfd830b3af1bac89

PKG_MAINTAINER:=LinkEase <support@linkease.com>
PKG_LICENSE:=BSD-2-Clause-Patent BSD-2-Clause OpenSSL
PKG_LICENSE_FILES:=pc-bios/edk2-licenses.txt

include $(INCLUDE_DIR)/package.mk

define Package/lighthost-qemu-firmware
  SECTION:=utils
  CATEGORY:=Utilities
  SUBMENU:=Virtualization
  TITLE:=Pinned x86_64 EDK2 firmware for LightHost
  URL:=https://www.qemu.org/
endef

define Package/lighthost-qemu-firmware/description
 EDK2 x86_64 UEFI code and variable-store firmware bundled by QEMU 9.1.3.
 QEMU records the firmware source as edk2-stable202302 with OpenSSL 1.1.1s.
endef

define Build/Prepare
	rm -rf $(PKG_BUILD_DIR)
	mkdir -p $(PKG_BUILD_DIR)
	$(TAR) -C $(PKG_BUILD_DIR) -xJf $(DL_DIR)/$(PKG_SOURCE) \
		--strip-components=1 \
		qemu-$(QEMU_SOURCE_VERSION)/pc-bios/edk2-x86_64-code.fd.bz2 \
		qemu-$(QEMU_SOURCE_VERSION)/pc-bios/edk2-x86_64-secure-code.fd.bz2 \
		qemu-$(QEMU_SOURCE_VERSION)/pc-bios/edk2-i386-vars.fd.bz2 \
		qemu-$(QEMU_SOURCE_VERSION)/pc-bios/edk2-licenses.txt
endef

define Build/Compile
	rm -rf $(PKG_BUILD_DIR)/lighthost-firmware
	mkdir -p $(PKG_BUILD_DIR)/lighthost-firmware
	bzip2 -dc $(PKG_BUILD_DIR)/pc-bios/edk2-x86_64-code.fd.bz2 \
		> $(PKG_BUILD_DIR)/lighthost-firmware/edk2-x86_64-code.fd
	bzip2 -dc $(PKG_BUILD_DIR)/pc-bios/edk2-x86_64-secure-code.fd.bz2 \
		> $(PKG_BUILD_DIR)/lighthost-firmware/edk2-x86_64-secure-code.fd
	bzip2 -dc $(PKG_BUILD_DIR)/pc-bios/edk2-i386-vars.fd.bz2 \
		> $(PKG_BUILD_DIR)/lighthost-firmware/edk2-i386-vars.fd
endef

define Package/lighthost-qemu-firmware/install
	$(INSTALL_DIR) $(1)/usr/share/qemu \
		$(1)/usr/share/licenses/lighthost-qemu-firmware
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/lighthost-firmware/edk2-x86_64-code.fd \
		$(1)/usr/share/qemu/edk2-x86_64-code.fd
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/lighthost-firmware/edk2-x86_64-secure-code.fd \
		$(1)/usr/share/qemu/edk2-x86_64-secure-code.fd
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/lighthost-firmware/edk2-i386-vars.fd \
		$(1)/usr/share/qemu/edk2-i386-vars.fd
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/pc-bios/edk2-licenses.txt \
		$(1)/usr/share/licenses/lighthost-qemu-firmware/edk2-licenses.txt
endef

$(eval $(call BuildPackage,lighthost-qemu-firmware))
