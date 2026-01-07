# PowerShell script to install the built AxiomUIXV app to the desktop.
#
# Run from the AxiomUIXV directory after successful PyInstaller build:
#   .\Install-App.ps1
#
# It copies the dist/AxiomUIXV folder to Program Files and creates shortcuts on Desktop + in Start Menu.

param (
    [string]$InstallRoot = "$env:LOCALAPPDATA\Programs\AxiomUIXV"
)

$ErrorActionPreference = "Stop"

$SrcDir = Join-Path $PSScriptRoot "dist\AxiomUIXV"
$DesktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "AxiomUIXV.lnk"
$StartMenuShortcut = Join-Path ([Environment]::GetFolderPath("Programs")) "AxiomUIXV.lnk"

if (!(Test-Path $SrcDir)) {
    Write-Error "Built app folder not found at: $SrcDir`nRun pyinstaller first."
    exit 1
}

# Copy to Program Files
$InstallDir = $InstallRoot
Write-Host "Installing to: $InstallDir"
if (!(Test-Path $InstallDir)) {
    New-Item -Path $InstallDir -ItemType Directory -Force | Out-Null
}
Copy-Item -Path "$SrcDir\*" -Destination $InstallDir -Recurse -Force

# Create desktop shortcut
$WShell = New-Object -ComObject WScript.Shell
$DesktopLnk = $WShell.CreateShortcut($DesktopShortcut)
$DesktopLnk.TargetPath = Join-Path $InstallDir "AxiomUIXV.exe"
$DesktopLnk.WorkingDirectory = $InstallDir
$DesktopLnk.IconLocation = Join-Path $InstallDir "axiom_icon.ico"
$DesktopLnk.Save()

# Create Start Menu shortcut
$StartLnk = $WShell.CreateShortcut($StartMenuShortcut)
$StartLnk.TargetPath = Join-Path $InstallDir "AxiomUIXV.exe"
$StartLnk.WorkingDirectory = $InstallDir
$StartLnk.IconLocation = Join-Path $InstallDir "axiom_icon.ico"
$StartLnk.Save()

Write-Host "AxiomUIXV installed. Launch via Desktop or Start Menu." -ForegroundColor Green