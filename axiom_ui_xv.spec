# -*- mode: python; coding: utf-8 -*-
# PyInstaller spec for a Forbes-grade AxiomUIXV app.
# Build: pyinstaller --clean axiom_ui_xv.spec

import os
from pathlib import Path
from PyInstaller.building.datastruct import (
    VSVersionInfo,
    FixedFileInfo,
    StringFileInfo,
    StringTable,
    StringStruct,
    VarFileInfo,
    VarStruct,
)

ROOT = Path(SPECPATH).resolve()
APP_NAME = "AxiomUIXV"
ICON = ROOT / "axiom_icon.ico"
MANIFEST = ROOT / "app.manifest"

# ----------------------------------------------------------------------
# Version metadata (real Windows version resource data)
# ----------------------------------------------------------------------
VS_VERSION_INFO = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(1, 0, 0, 0),
        prodvers=(1, 0, 0, 0),
        mask=0x3f,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    "040904B0",
                    [
                        StringStruct("CompanyName", "Axiom Hive"),
                        StringStruct("FileDescription", "Deterministic Terminal Substrate"),
                        StringStruct("FileVersion", "1.0.0.0"),
                        StringStruct("InternalName", APP_NAME),
                        StringStruct("LegalCopyright", "© 2026 Axiom Hive. All rights reserved."),
                        StringStruct("OriginalFilename", f"{APP_NAME}.exe"),
                        StringStruct("ProductName", APP_NAME),
                        StringStruct("ProductVersion", "1.0.0.0"),
                    ],
                )
            ]
        ),
        VarFileInfo([VarStruct("Translation", [1033, 1200])]),
    ],
)

# Application metadata
a = Analysis(
    [str(ROOT / "gui_entry.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[],
    hiddenimports=[
        "rich",
        "rich.console",
        "rich.layout",
        "rich.live",
        "rich.panel",
        "rich.table",
        "httpx",
        "yaml",
        "psutil",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,                     # Console to render Rich UI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=VS_VERSION_INFO,
    icon=str(ICON) if ICON.exists() else "NONE",
    manifest=str(MANIFEST) if MANIFEST.exists() else None,
)
