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

# --- 5. Generate application icon ---
echo "[6/7] Generating application icon..."
python resources/generate_icon.py

# --- 6. Clean old builds ---
echo "[7/7] Cleaning old builds..."
rm -rf build dist
shopt -s nullglob 2>/dev/null || true
for f in *.spec; do rm -f "$f"; done

# --- Detect PySide6 path for hidden imports ---
PYSIDE6_DIR=$(python -c "import PySide6; import os; print(os.path.dirname(PySide6.__file__))")

echo ""
echo "============================================"
echo " Running PyInstaller..."
echo "============================================"
echo ""

pyinstaller \
    --windowed \
    --name "$APP_NAME" \
    --icon "$ICON_DIR/app_icon.icns" \
    --add-data "$ICON_DIR/app_icon.icns:resources" \
    --add-data "$ICON_DIR/app_icon.png:resources" \
    --hidden-import PySide6.QtCore \
    --hidden-import PySide6.QtGui \
    --hidden-import PySide6.QtWidgets \
    --hidden-import paramiko.transport \
    --hidden-import paramiko.dsskey \
    --hidden-import paramiko.ecdsakey \
    --hidden-import paramiko.ed25519key \
    --hidden-import paramiko.rsakey \
    --osx-bundle-identifier com.urbanscannon.wireguard-deployer \
    --noconfirm \
    --clean \
    main.py

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
