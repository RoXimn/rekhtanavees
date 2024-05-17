#define SettingsFile "preferences.toml"
#define AppFilename "rekhtanavees.exe"
#define AppFolderName "RekhtaNavees"
#define AppDisplayName "Rekhta Navees"
#define AppVer "0.1"

[Setup]
AppId={#AppFolderName}-{#AppVer}
AppName={#AppFolderName}
AppVersion={#AppVer}
AppCopyright=Copyright (C) 2024 RoXimn

WizardStyle=modern
DefaultDirName={autopf}\{#AppFolderName}
DefaultGroupName={#AppDisplayName}
UninstallDisplayIcon={app}\{#AppFilename}
Compression=lzma2
SolidCompression=yes
LicenseFile=..\LICENSE
WindowVisible=no

DisableWelcomePage=no
UserInfoPage=no
PrivilegesRequired=lowest
DisableDirPage=auto
DisableProgramGroupPage=auto

; Output to same folder as the input script
OutputDir="."
OutputBaseFilename="{#AppFolderName}-{#AppVer}-win-setup"

[Files]
Source: "..\dist\rekhtanavees\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
Source: "..\docs\build\html\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs
Source: "..\LICENSE"; DestDir: "{app}"
Source: "..\README.md"; DestDir: "{app}"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Icons]
Name: "{group}\{#AppDisplayName}"; Filename: "{app}\{#AppFilename}"
Name: "{userdesktop}\{#AppDisplayName} v{#AppVer}"; Filename: "{app}\{#AppFilename}"; IconFilename: "{app}\{#AppFilename}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppFilename}"; Description: "Launch {#AppDisplayName}  v{#AppVer} application"; Flags: nowait postinstall skipifsilent
Filename: "{app}\README.md"; Description: "Show README file"; Flags: shellexec postinstall skipifsilent unchecked

[CustomMessages]
NameAndVersion={#AppDisplayName} v{#AppVer}

[Code]
// ask for delete application data directory during uninstall
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  case CurUninstallStep of
    usUninstall:
      begin
        if MsgBox('Delete all the preferences and log files?', mbCriticalError, MB_YESNO or MB_DEFBUTTON2) = IDYES then
          begin
             DelTree(ExpandConstant('{localappdata}\.{#AppFolderName}'), True, True, True);
          end
      end;
  end;
end; 
