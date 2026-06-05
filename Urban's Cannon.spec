# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[("/Users/dengzhenyu/Desktop/Urban's cannon/Private-WireGuard-VPS-Deployer/resources/app_icon.icns", "resources"), ("/Users/dengzhenyu/Desktop/Urban's cannon/Private-WireGuard-VPS-Deployer/resources/app_icon.png", "resources")],
    hiddenimports=['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'paramiko.transport', 'paramiko.dsskey', 'paramiko.ecdsakey', 'paramiko.ed25519key', 'paramiko.rsakey'],
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
    name="Urban's Cannon",
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
    icon=["/Users/dengzhenyu/Desktop/Urban's cannon/Private-WireGuard-VPS-Deployer/resources/app_icon.icns"],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Urban's Cannon",
)
app = BUNDLE(
    coll,
    name="Urban's Cannon.app",
    icon="/Users/dengzhenyu/Desktop/Urban's cannon/Private-WireGuard-VPS-Deployer/resources/app_icon.icns",
    bundle_identifier="com.urbanscannon.wireguard-deployer",
    version="1.0",
    info_plist={
        "CFBundleShortVersionString": "1.0",
        "CFBundleVersion": "1.0",
        "NSHumanReadableCopyright": "Urban's Cannon — MenZenithRBowstringS",
        "NSHighResolutionCapable": True,
    },
)
