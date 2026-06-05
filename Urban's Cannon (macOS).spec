# -*- mode: python ; coding: utf-8 -*-

import os
_spec_dir = os.getcwd()
_resources = os.path.join(_spec_dir, "resources")

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join(_resources, "app_icon.icns"), "resources"),
        (os.path.join(_resources, "app_icon.png"), "resources"),
    ],
    hiddenimports=[
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "paramiko.transport",
        "paramiko.dsskey",
        "paramiko.ecdsakey",
        "paramiko.ed25519key",
        "paramiko.rsakey",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Urbans-Cannon",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(_resources, "app_icon.icns"),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Urbans-Cannon",
)
app = BUNDLE(
    coll,
    name="Urbans-Cannon.app",
    icon=os.path.join(_resources, "app_icon.icns"),
    bundle_identifier="com.urbanscannon.wireguard-deployer",
    version="1.1",
    info_plist={
        "CFBundleShortVersionString": "1.1",
        "CFBundleVersion": "1.1",
        "NSHumanReadableCopyright": "Urban's Cannon",
        "NSHighResolutionCapable": True,
    },
)
