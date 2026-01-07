# PowerShell script to create a desktop shortcut for AxiomUIXV
#
# Run this with:
#   .\Create-Shortcut.ps1
#
# The shortcut will appear on your Desktop as "AxiomUIXV" and run launch.py.

$ErrorActionPreference = "Stop"

$ThisDir = $PSScriptRoot
$Target = Join-Path $ThisDir "launch.py"
$IconPath = Join-Path $ThisDir "axiom_icon.ico"
$ShortcutPath = Join-Path ([Environment]::GetFolderPath("Desktop")) "AxiomUIXV.lnk"

if (!(Test-Path $Target)) {
    Write-Error "launch.py not found at $Target"
    exit 1
}

# If you add an axiom_icon.ico file later, it will be used; otherwise default.
if (!(Test-Path $IconPath)) {
    $IconPath = $null
}

$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$Target`""
$Shortcut.WorkingDirectory = $ThisDir
if ($IconPath) {
    $Shortcut.IconLocation = $IconPath
}

$Shortcut.Save()

Write-Host "Shortcut created at: $ShortcutPath" -ForegroundColor Green