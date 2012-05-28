; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define TodayString GetDateTimeString('yyyymmdd', '', '');

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{259A20EE-612B-4EEB-B69D-3F94C4CA9D7F}
AppName=Viewer_{#TodayString}
AppVersion=0.1
;AppVerName=Viewer 0.1
AppPublisher=chchrsc
AppPublisherURL=https://bitbucket.org/chchrsc/viewer/
AppSupportURL=https://bitbucket.org/chchrsc/viewer/
AppUpdatesURL=https://bitbucket.org/chchrsc/viewer/
DefaultDirName={pf}\Viewer_{#TodayString}
DefaultGroupName=Viewer_{#TodayString}
LicenseFile=C:\MinGW\msys\1.0\home\sam\viewer\viewer\LICENSE.txt
OutputDir=C:\install
OutputBaseFilename=viewersetup_{#TodayString}
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\MinGW\msys\1.0\home\sam\viewer\viewer\dist\viewer.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\MinGW\msys\1.0\home\sam\viewer\viewer\dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\Viewer"; Filename: "{app}\viewer.exe"
Name: "{commondesktop}\Viewer"; Filename: "{app}\viewer.exe"; Tasks: desktopicon
Name: "{group}\Uninstall Viewer"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\viewer.exe"; Description: "{cm:LaunchProgram,Viewer}"; Flags: nowait postinstall skipifsilent

