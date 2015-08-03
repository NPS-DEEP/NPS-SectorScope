# NSIS script for creating the Windows NPS-block_match installer file.
#
# Installs the following:
#   .py scripts
#   pdf document
#   path
#   uninstaller
#   uninstaller shurtcut
#   start menu shortcut for pdf document
#   registry information including uninstaller information

# Assign VERSION externally with -DVERSION=<ver>
# Build from signed files with -DSIGN
!ifndef VERSION
	!echo "VERSION is required."
	!echo "example usage: makensis -DVERSION=1.0.0 build_installer.nsi"
	!error "Invalid usage"
!endif

!define APPNAME "Block Match ${VERSION}"
!define REG_SUB_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
!define COMPANYNAME "Naval Postgraduate School"
!define DESCRIPTION "Block Hash Tools"

# These will be displayed by the "Click here for support information" link in "Add/Remove Programs"
# It is possible to use "mailto:" links here to open the email client
!define HELPURL "//https://github.com/NPS-DEEP/NPS-block_match" # "Support Information" link
!define UPDATEURL "//https://github.com/NPS-DEEP/NPS-block_match" # "Product Updates" link
!define ABOUTURL "//https://github.com/NPS-DEEP/NPS-block_match" # "Publisher" link

SetCompressor lzma
 
RequestExecutionLevel admin
 
InstallDir "$PROGRAMFILES64\${APPNAME}"
 
Name "${APPNAME}"
	outFile "NPS-block_match-${VERSION}-windowsinstaller.exe"
 
!include LogicLib.nsh
!include EnvVarUpdate.nsi
#!include x64.nsh
 
page components
Page instfiles
UninstPage instfiles
 
!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin" ;Require admin rights on NT4+
	messageBox mb_iconstop "Administrator rights required!"
	setErrorLevel 740 ;ERROR_ELEVATION_REQUIRED
	quit
${EndIf}
!macroend

Section "${APPNAME}"
        # establish out path
        setOutPath "$INSTDIR"

	# install Registry information
	WriteRegStr HKLM "${REG_SUB_KEY}" "DisplayName" "${APPNAME} - ${DESCRIPTION}"
	WriteRegStr HKLM "${REG_SUB_KEY}" "UninstallString" "$INSTDIR\uninstall.exe"
	WriteRegStr HKLM "${REG_SUB_KEY}" "QuietUninstallString" "$INSTDIR\uninstall.exe /S"
	WriteRegStr HKLM "${REG_SUB_KEY}" "InstallLocation" "$INSTDIR"
	WriteRegStr HKLM "${REG_SUB_KEY}" "Publisher" "${COMPANYNAME}"
	WriteRegStr HKLM "${REG_SUB_KEY}" "HelpLink" "${HELPURL}"
	WriteRegStr HKLM "${REG_SUB_KEY}" "URLUpdateInfo" "${UPDATEURL}"
	WriteRegStr HKLM "${REG_SUB_KEY}" "URLInfoAbout" "${ABOUTURL}"
	WriteRegStr HKLM "${REG_SUB_KEY}" "DisplayVersion" "${VERSION}"
	# There is no option for modifying or repairing the install
	WriteRegDWORD HKLM "${REG_SUB_KEY}" "NoModify" 1
	WriteRegDWORD HKLM "${REG_SUB_KEY}" "NoRepair" 1

	# install the uninstaller
	# create the uninstaller
	writeUninstaller "$INSTDIR\uninstall.exe"
 
	# create the start menu
	createDirectory "$SMPROGRAMS\${APPNAME}"

	# link the uninstaller to the start menu
	createShortCut "$SMPROGRAMS\${APPNAME}\Uninstall ${APPNAME}.lnk" "$INSTDIR\uninstall.exe"

        # install all .py files
        file "../python/*.py"

        # install PDF doc
        setOutPath "$INSTDIR\pdf"
        file "block_match_viewer_um.pdf"

        # install shortcut to PDF doc
        createShortCut "$SMPROGRAMS\${APPNAME}\Block Match Viewer Users Manual.lnk" "$INSTDIR\pdf\block_match_viewer_um.pdf"

sectionEnd

Section "Add to path"
	setOutPath "$INSTDIR"
        # add hashdb to system PATH
        ${EnvVarUpdate} $0 "PATH" "A" "HKLM" "$INSTDIR"
sectionEnd

function .onInit
        # require admin
	setShellVarContext all
	!insertmacro VerifyUserIsAdmin
functionEnd

function un.onInit
	SetShellVarContext all
 
	#Verify the uninstaller - last chance to back out
	MessageBox MB_OKCANCEL "Permanantly remove ${APPNAME}?" IDOK next
		Abort
	next:
	!insertmacro VerifyUserIsAdmin
functionEnd
 
Function un.FailableDelete
	Start:
	delete "$0"
	IfFileExists "$0" FileStillPresent Continue

	FileStillPresent:
	DetailPrint "Unable to delete file $0, likely because it is in use.  Please close all hashdb files and try again."
	MessageBox MB_ICONQUESTION|MB_RETRYCANCEL \
		"Unable to delete file $0, \
		likely because it is in use.  \
		Please close all Bulk Extractor files and try again." \
 		/SD IDABORT IDRETRY Start IDABORT InstDirAbort

	# abort
	InstDirAbort:
	DetailPrint "Uninstall started but did not complete."
	Abort

	# continue
	Continue:
FunctionEnd

section "uninstall"
	# manage uninstalling executable code because they may be open
	StrCpy $0 "$INSTDIR\be_import.py"
	Call un.FailableDelete
	StrCpy $0 "$INSTDIR\be_scan.py"
	Call un.FailableDelete
	StrCpy $0 "$INSTDIR\block_match_viewer.py"
	Call un.FailableDelete
	StrCpy $0 "$INSTDIR\pdf\block_match_viewer_um.pdf"
	Call un.FailableDelete

        # uninstall all support code
        delete "$INSTDIR\*.py"

        # uninstall the pdf directory
        rmdir "$INSTDIR\pdf"

	# uninstall Start Menu launcher shortcuts
	delete "$SMPROGRAMS\${APPNAME}\Block Match Viewer Users Manual.lnk"
	delete "$SMPROGRAMS\${APPNAME}\uninstall ${APPNAME}.lnk"
	rmDir "$SMPROGRAMS\${APPNAME}"

	# delete the uninstaller
	delete "$INSTDIR\uninstall.exe"
 
	# Try to remove the install directory
	rmDir "$INSTDIR"
 
	# Remove uninstaller information from the registry
	DeleteRegKey HKLM "${REG_SUB_KEY}"

        # remove associated search paths from the PATH environment variable
        # were both installed
        ${un.EnvVarUpdate} $0 "PATH" "R" "HKLM" "$INSTDIR"
sectionEnd

