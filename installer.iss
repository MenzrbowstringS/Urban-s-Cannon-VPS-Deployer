; Inno Setup script for Urban's Cannon
; Requires Inno Setup 6+ — https://jrsoftware.org/isinfo.php
;
; Build:
;   iscc installer.iss
;
; Output:
;   dist\Urbans-Cannon-1.1-Windows-Setup.exe

#define AppName "Urban's Cannon"
#define AppVersion "1.1"
#define AppPublisher "MenZenithRBowstringS"
#define AppURL "https://github.com/Urban-s-Cannon/private-wireguard-vps-deployer"
#define AppExeName "Urbans-Cannon.exe"
#define SourcePath "dist\Urbans-Cannon\*"

[Setup]
AppId={{B8F4A3D2-7C1E-4A5B-9D2F-1E6C8A3B5F7D}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir=dist
OutputBaseFilename=Urbans-Cannon-{#AppVersion}-Windows-Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
SetupIconFile=resources\app_icon.ico
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName}
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription=Private WireGuard VPS Deployer
ShowLanguageDialog=auto

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
Source: "{#SourcePath}"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
