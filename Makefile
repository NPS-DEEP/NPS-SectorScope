# Run this Makefile to:
#   * Set the SectorScope VERSION value
#   * Build the UM
#   * Create the Windows Installer
#   * Create a .zip distribution file
#
# Prerequisites:
# The .nbm file is generated using NetBeans on Windows.
# Build it on Windows and then use git push to update it.

VERSION = 0.7.1
URL = https://github.com/NPS-DEEP/NPS-SectorScope/wiki
INFO_FILE = python/info.py
SOURCES = python/*.py
ICONS = python/icons/*.gif
UM_DIR = doc/sectorscope_um
UM = doc/sectorscope_um/sectorscope_um.pdf
ZIP_DIR = SectorScope-$(VERSION)
ZIP = $(ZIP_DIR).zip
NBM = autopsy_plugin/build/edu-nps-sectorscope.nbm
WIN_INSTALLER = SectorScope-$(VERSION)-windowsinstaller.exe

all: $(INFO_FILE) $(UM) $(ZIP) $(NBM) $(WIN_INSTALLER)

$(INFO_FILE): Makefile
	@echo "# This file is auto-generated by Makefile.  Do not edit this file." > python/info.py
	@echo "VERSION = \"$(VERSION)\"" >> python/info.py
	@echo "URL = \"$(URL)\"" >> python/info.py

$(UM):
	cd doc/sectorscope_um; make

$(ZIP): $(SOURCES) $(ICONS) $(UM)
	rm -rf $(ZIP_DIR) $(ZIP)
	mkdir $(ZIP_DIR)
	cp $(SOURCES) $(ZIP_DIR)
	mkdir $(ZIP_DIR)/icons
	cp $(ICONS) $(ZIP_DIR)/icons
	mkdir $(ZIP_DIR)/doc
	cp $(UM) $(ZIP_DIR)/doc
	zip -r $(ZIP) $(ZIP_DIR)
	rm -rf $(ZIP_DIR)

$(NBM):
	@echo Please provide the current .nbm file by exporting it on Windows
	@echo and updating it using git push.

$(WIN_INSTALLER): build_installer.nsi EnvVarUpdate.nsi $(UM) $(SOURCES)
	@echo Making $(WIN_INSTALLER)
	makensis -DVERSION=$(VERSION) build_installer.nsi
	@echo '**************** WINDOWS INSTALLER IS MADE ****************'

clean:
	/bin/rm -rf $(INFO_FILE) $(ZIP) $(WIN_INSTALLER)

.PHONY: clean

