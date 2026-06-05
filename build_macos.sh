#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# build_macos.sh — Build the Private WireGuard VPS Deployer macOS .app bundle
#
# Usage:
#   chmod +x build_macos.sh
#   ./build_macos.sh
#
# Output:
#   dist/Private WireGuard VPS Deployer.app
# ---------------------------------------------------------------------------

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

APP_NAME="Urban's Cannon"
ICON_DIR="$SCRIPT_DIR/resources"

echo "============================================"
echo " Building: $APP_NAME"
echo "============================================"
echo ""

# --- 1. Create / activate virtual environment ---
if [ ! -d ".venv" ]; then
    echo "[1/7] Creating Python virtual environment..."
    python3 -m venv .venv
else
    echo "[1/7] Virtual environment already exists."
fi

echo "[2/7] Activating virtual environment..."
source .venv/bin/activate

# --- 2. Upgrade pip ---
echo "[3/7] Upgrading pip..."
python -m pip install --upgrade pip --quiet

# --- 3. Install dependencies ---
echo "[4/7] Installing dependencies..."
pip install -r requirements.txt --quiet

# --- 4. Basic import check ---
echo "[5/7] Checking imports..."
python -c "
import PySide6
import paramiko
import qrcode
print('  PySide6', PySide6.__version__)
print('  paramiko', paramiko.__version__)
print('  All imports OK.')
"

# --- 5. Generate application icon (only if missing) ---
echo "[6/7] Checking application icon..."
if [ ! -f "$ICON_DIR/app_icon.icns" ]; then
    python resources/generate_icon.py
    echo "  Icon generated."
else
    echo "  Icon already exists, skipping generation."
fi

# --- 6. Clean old builds ---
echo "[7/7] Cleaning old builds..."
rm -rf build dist

echo ""
echo "============================================"
echo " Running PyInstaller..."
echo "============================================"
echo ""

pyinstaller \
    "Urban's Cannon (macOS).spec" \
    --noconfirm \
    --clean

# Rename bundled output to proper app name
if [ -d "dist/Urbans-Cannon.app" ]; then
    mv "dist/Urbans-Cannon.app" "dist/$APP_NAME.app"
fi

echo ""
echo "============================================"
echo " Build Complete"
echo "============================================"
echo ""
echo " App: $(pwd)/dist/$APP_NAME.app"
echo ""
echo " To create a DMG installer, run:"
echo "   ./create_dmg.sh"
echo ""
