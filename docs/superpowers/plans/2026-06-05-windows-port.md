# Windows Port Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Urban's Cannon run natively on Windows with feature parity to the macOS version.

**Architecture:** Five independent tasks: (1) platform-adaptive font in gui.py, (2) cross-platform "show in folder" in gui.py, (3) Windows .ico icon generator, (4) PyInstaller spec + local build script, (5) Inno Setup script + GitHub Actions CI/CD. Tasks 1-3 have no dependencies on each other. Tasks 4-5 depend on 3 (icon file must exist).

**Tech Stack:** Python 3.11+, PySide6, PyInstaller, Pillow, Inno Setup 6, GitHub Actions

---

### Task 1: Platform-adaptive monospace font

**Files:**
- Modify: `Private-WireGuard-VPS-Deployer/gui.py:131`

**Goal:** Use `Cascadia Code` on Windows (fallback to `Consolas`), keep `Menlo` on macOS.

- [ ] **Step 1: Replace the MONO_FAMILY constant with a platform-aware function**

In `gui.py`, replace line 131:
```python
# Menlo ships with macOS and resolves reliably in Qt; "SF Mono" is a
# restricted system font that QFont often cannot load by family name.
MONO_FAMILY = "Menlo"
```

With:
```python
import sys as _sys

def _mono_family() -> str:
    """Return the best available monospace font for the current platform."""
    if _sys.platform == "darwin":
        return "Menlo"
    # Windows: Cascadia Code ships with Windows Terminal and newer Windows;
    # Consolas is the universal fallback that ships with every Windows version.
    return "Cascadia Code"
```

- [ ] **Step 2: Update the _mono() helper to use the function**

In `gui.py`, change the `_mono` function (line 332):
```python
def _mono(widget: QWidget) -> QWidget:
    f = QFont(MONO_FAMILY)
    f.setStyleHint(QFont.Monospace)
    f.setPointSize(12)
    widget.setFont(f)
    return widget
```

To:
```python
def _mono(widget: QWidget) -> QWidget:
    f = QFont(_mono_family())
    f.setStyleHint(QFont.Monospace)
    f.setPointSize(12)
    widget.setFont(f)
    return widget
```

- [ ] **Step 3: Update the Stepper node font**

In `Stepper.paintEvent`, line 470-473, replace:
```python
        node_font = QFont(MONO_FAMILY)
        node_font.setStyleHint(QFont.Monospace)
```

With:
```python
        node_font = QFont(_mono_family())
        node_font.setStyleHint(QFont.Monospace)
```

- [ ] **Step 4: Update footer font**

In `MainWindow._init_ui`, around line 862, replace:
```python
        ff = QFont(MONO_FAMILY)
```

With:
```python
        ff = QFont(_mono_family())
```

- [ ] **Step 5: Update Help dialog version font**

In `HelpDialog.__init__`, around line 661, replace:
```python
        ver = QFont(MONO_FAMILY)
```

With:
```python
        ver = QFont(_mono_family())
```

- [ ] **Step 6: Update log view font**

In `MainWindow._build_log_page`, around line 1083, replace:
```python
        lf = QFont(MONO_FAMILY)
```

With:
```python
        lf = QFont(_mono_family())
```

- [ ] **Step 7: Verify no remaining MONO_FAMILY references**

Run: `grep -n "MONO_FAMILY" "Private-WireGuard-VPS-Deployer/gui.py"`
Expected: No output (all references replaced)

---

### Task 2: Cross-platform "Show in Folder"

**Files:**
- Modify: `Private-WireGuard-VPS-Deployer/gui.py:1430-1434`

**Goal:** Replace macOS-only `open -R` with a cross-platform implementation.

- [ ] **Step 1: Replace the _on_open_finder method**

In `gui.py`, replace lines 1430-1434:
```python
    def _on_open_finder(self):
        if self._last_output_path and os.path.exists(self._last_output_path):
            os.system(f"open -R '{self._last_output_path}'")
        else:
            self._log(tr("log_file_missing"))
```

With:
```python
    def _on_open_finder(self):
        if self._last_output_path and os.path.exists(self._last_output_path):
            _reveal_in_file_manager(self._last_output_path)
        else:
            self._log(tr("log_file_missing"))
```

- [ ] **Step 2: Add the _reveal_in_file_manager helper function near the top of gui.py**

Add after the `_premium_ease` function (after line 66):
```python
def _reveal_in_file_manager(path: str) -> None:
    """Open the file manager and select (highlight) the given file.
    Cross-platform: Finder on macOS, Explorer on Windows."""
    import subprocess
    import sys
    if sys.platform == "darwin":
        subprocess.run(["open", "-R", path], check=False)
    elif sys.platform == "win32":
        # /select, tells Explorer to highlight the file (not just open the folder)
        subprocess.run(["explorer", "/select,", path], check=False)
    else:
        # Linux fallback: open the containing directory
        subprocess.run(["xdg-open", os.path.dirname(path)], check=False)
```

- [ ] **Step 3: Similarly update deployer.py line 394 (the Finder reveal after deploy)**

In `deployer.py`, replace line 394:
```python
        log("Revealing config in Finder...")
        os.system(f"open -R '{output_path}'")
```

With:
```python
        log("Revealing config in file manager...")
        import subprocess as _subprocess
        import sys as _sys
        if _sys.platform == "darwin":
            _subprocess.run(["open", "-R", output_path], check=False)
        elif _sys.platform == "win32":
            _subprocess.run(["explorer", "/select,", output_path], check=False)
```

- [ ] **Step 4: Update the "Show in Finder" UI label to be platform-aware**

In `gui.py._retranslate`, line 1272, change:
```python
        self.open_finder_btn.setText(tr("show_finder"))
```

The label key remains `"show_finder"` but we update its English text in `i18n.py`. In `i18n.py`, change:
```python
add("show_finder",     "Show in Finder",      "在 Finder 中显示")
```

To:
```python
add("show_finder",     "Show in Folder",      "在文件夹中显示")
```

---

### Task 3: Windows .ico icon generator

**Files:**
- Create: `Private-WireGuard-VPS-Deployer/resources/generate_icon_win.py`

**Goal:** Generate a multi-resolution `.ico` file from `app_icon.png` for Windows packaging.

- [ ] **Step 1: Create the icon generator script**

Create `resources/generate_icon_win.py`:
```python
"""
generate_icon_win.py — Generate a multi-resolution .ico file from app_icon.png
for Windows PyInstaller and Inno Setup packaging.

Usage:
    python resources/generate_icon_win.py

Output:
    resources/app_icon.ico  (16×16, 32×32, 48×48, 256×256)
"""

import os
from PIL import Image

SIZES = [16, 32, 48, 256]
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.png")
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.ico")


def main():
    if not os.path.exists(SRC):
        raise FileNotFoundError(f"Source icon not found: {SRC}")

    img = Image.open(SRC).convert("RGBA")
    # Use the largest size as the master; embed smaller sizes as well
    resized = [img.resize((s, s), Image.LANCZOS) for s in SIZES]
    resized[0].save(
        DST,
        format="ICO",
        sizes=[(s, s) for s in SIZES],
        append_images=resized[1:],
    )
    print(f"Generated: {DST}")
    for s in SIZES:
        print(f"  {s}×{s}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the generator to create app_icon.ico**

Run: `cd "Private-WireGuard-VPS-Deployer" && source .venv/bin/activate && python resources/generate_icon_win.py`
Expected: Creates `resources/app_icon.ico` with console output listing all sizes.

---

### Task 4: PyInstaller spec + Windows local build script

**Files:**
- Create: `Private-WireGuard-VPS-Deployer/Urban's Cannon (Windows).spec`
- Create: `Private-WireGuard-VPS-Deployer/build_windows.bat`

**Goal:** Provide a PyInstaller spec that produces a Windows folder bundle, and a `.bat` script for local builds.

- [ ] **Step 1: Create the Windows PyInstaller spec**

Create `Urban's Cannon (Windows).spec`:
```python
# -*- mode: python ; coding: utf-8 -*-

import os
_spec_dir = os.path.dirname(os.path.abspath(SPECPATH))
_resources = os.path.join(_spec_dir, "resources")

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join(_resources, "app_icon.ico"), "resources"),
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
    icon=os.path.join(_resources, "app_icon.ico"),
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
```

- [ ] **Step 2: Create the Windows local build script**

Create `build_windows.bat`:
```bat
@echo off
setlocal enabledelayedexpansion

REM ---------------------------------------------------------------------------
REM build_windows.bat — Build the Urban's Cannon Windows executable
REM
REM Usage:
REM   build_windows.bat
REM
REM Output:
REM   dist\Urban's Cannon\Urban's Cannon.exe
REM ---------------------------------------------------------------------------

set "APP_NAME=Urban's Cannon"
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ============================================
echo  Building: %APP_NAME% (Windows)
echo ============================================
echo.

REM --- 1. Create / activate virtual environment ---
if not exist ".venv" (
    echo [1/5] Creating Python virtual environment...
    python -m venv .venv
) else (
    echo [1/5] Virtual environment already exists.
)

echo [2/5] Activating virtual environment...
call .venv\Scripts\activate.bat

REM --- 2. Install dependencies ---
echo [3/5] Installing dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

REM --- 3. Generate Windows icon ---
echo [4/5] Generating Windows icon...
python resources\generate_icon_win.py

REM --- 4. Build with PyInstaller ---
echo [5/5] Building with PyInstaller...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
pyinstaller "Urban's Cannon (Windows).spec" --noconfirm --clean

echo.
echo ============================================
echo  Build Complete
echo ============================================
echo.
echo  Output: %SCRIPT_DIR%dist\%APP_NAME%\ 
echo.
echo  To create an installer, install Inno Setup 6 and run:
echo    iscc installer.iss
echo.
endlocal
```

---

### Task 5: Inno Setup script + GitHub Actions CI/CD

**Files:**
- Create: `Private-WireGuard-VPS-Deployer/installer.iss`
- Create: `Private-WireGuard-VPS-Deployer/.github/workflows/build-windows.yml`

**Goal:** Professional installer (desktop shortcut, start menu, uninstall) + automated build on tag push.

- [ ] **Step 1: Create the Inno Setup script**

Create `installer.iss`:
```ini
; Inno Setup script for Urban's Cannon
; Requires Inno Setup 6+ (https://jrsoftware.org/isinfo.php)
; Build: iscc installer.iss

#define AppName "Urban's Cannon"
#define AppVersion "1.0"
#define AppPublisher "MenZenithRBowstringS"
#define AppURL "https://github.com/Urban-s-Cannon/private-wireguard-vps-deployer"
#define AppExeName "Urban's Cannon.exe"
#define SourcePath "dist\Urban's Cannon\*"

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
; Chinese + English language support
ShowLanguageDialog=auto

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

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
```

- [ ] **Step 2: Create the GitHub Actions workflow**

Create `.github/workflows/build-windows.yml`:
```yaml
name: Build Windows Installer

on:
  push:
    tags:
      - 'v*-win'
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Generate Windows icon
        run: python resources/generate_icon_win.py

      - name: Build with PyInstaller
        run: pyinstaller "Urban's Cannon (Windows).spec" --noconfirm --clean

      - name: Install Inno Setup
        uses: Minionguyjpro/Inno-Setup-Action@v1
        with:
          path: installer.iss

      - name: Upload installer
        uses: actions/upload-artifact@v4
        with:
          name: urbans-cannon-windows-installer
          path: dist/Urbans-Cannon-*-Windows-Setup.exe

      - name: Create Release (on tag)
        if: startsWith(github.ref, 'refs/tags/')
        uses: softprops/action-gh-release@v2
        with:
          files: dist/Urbans-Cannon-*-Windows-Setup.exe
          generate_release_notes: true
```

- [ ] **Step 3: Update README.md — add Windows build section**

In `README.md`, after the "How to Create a DMG Installer" section (line 67), add:
```markdown
## Building for Windows

### Prerequisites (Windows machine or VM)
- Python 3.11+
- [Inno Setup 6+](https://jrsoftware.org/isinfo.php)

### Local Build
```bat
cd Private-WireGuard-VPS-Deployer
build_windows.bat
```
The `.exe` will be at `dist\Urban's Cannon\Urban's Cannon.exe`.

### Create Installer
```bat
iscc installer.iss
```
The installer will be at `dist\Urbans-Cannon-1.0-Windows-Setup.exe`.

### GitHub Actions (recommended)
Push a tag matching `v*-win` (e.g., `v1.0-win`) to trigger an automated build on GitHub Actions. The installer will be uploaded as a release asset.
```

---

### Verification

After all tasks are complete, verify:

- [ ] `grep -n "MONO_FAMILY" gui.py` returns nothing (all replaced)
- [ ] `grep -n "open -R" gui.py deployer.py` returns nothing (all replaced)
- [ ] `resources/app_icon.ico` exists (16×16, 32×32, 48×48, 256×256)
- [ ] `Urban's Cannon (Windows).spec` is valid Python
- [ ] `build_windows.bat` syntax is correct
- [ ] `installer.iss` syntax is valid Inno Setup
- [ ] `.github/workflows/build-windows.yml` is valid YAML
