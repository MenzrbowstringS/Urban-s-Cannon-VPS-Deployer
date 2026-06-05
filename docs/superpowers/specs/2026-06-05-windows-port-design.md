# Windows Port Design — Urban's Cannon

**Date:** 2026-06-05
**Goal:** Make Urban's Cannon run natively on Windows with the same functionality as the macOS version.

## Summary

Urban's Cannon is a PySide6 desktop app that deploys WireGuard on a remote VPS via SSH. The core logic (`deployer.py`) is platform-agnostic Python. Porting to Windows requires minimal code changes: platform-specific font selection, file-explorer integration, and Windows packaging infrastructure (PyInstaller + Inno Setup + GitHub Actions CI/CD).

## Architecture

```
                    main.py (unchanged — dark palette works across platforms)
                         │
                    gui.py (minor platform branches: font + "show in folder")
                    deployer.py (unchanged — pure SSH)
                    i18n.py (unchanged)
                         │
              ┌──────────┴──────────┐
              │                     │
       macOS build            Windows build
       build_macos.sh         build_windows.bat (local)
       create_dmg.sh          installer.iss (Inno Setup)
                              .github/workflows/build-windows.yml (CI/CD)
```

## What Changes

### 1. gui.py — Platform adaptation
- **Font:** `Menlo` on macOS, `Cascadia Code` → fallback `Consolas` on Windows
- **"Show in folder":** `open -R` on macOS → `explorer /select,` on Windows
- These are 2 small `if sys.platform` branches (~10 lines total)

### 2. New files
- `resources/generate_icon_win.py` — Generate multi-res `.ico` from `app_icon.png`
- `build_windows.bat` — Local build script for Windows
- `installer.iss` — Inno Setup installer definition (desktop shortcut, start menu, uninstall)
- `Urban's Cannon (Windows).spec` — PyInstaller spec for Windows
- `.github/workflows/build-windows.yml` — GitHub Actions CI/CD

### 3. No changes
- `main.py`, `deployer.py`, `i18n.py` — unchanged
- macOS build scripts — untouched

## Build Pipeline (GitHub Actions)

```
Push tag v*-win → windows-latest runner
  ├─ Python 3.11 setup
  ├─ pip install dependencies
  ├─ Generate .ico icon
  ├─ PyInstaller (windowed, .ico icon)
  └─ Inno Setup → installer.exe → uploaded as release asset
```

## Design Decisions

- **Inno Setup over NSIS** — Free, simpler scripting, native Chinese UI support
- **GitHub Actions over local build** — User is on Mac; Windows build must happen on Windows runner
- **No code logic changes** — `deployer.py` is pure SSH operations, identical on all platforms
- **Keep macOS builds intact** — Build scripts are platform-specific, no shared build config needed

## Scope Boundaries

**In scope:**
- Windows `.exe` packaged via PyInstaller
- Inno Setup installer with desktop shortcut, start menu, uninstall
- GitHub Actions automated build on tag push

**Out of scope (YAGNI):**
- Auto-detection of WireGuard Windows client installation
- Auto-update mechanism
- VPN deployment logic changes
