#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# create_dmg.sh — Package the .app into a distributable DMG for macOS
#
# Usage:
#   chmod +x create_dmg.sh
#   ./create_dmg.sh
#
# Output:
#   dist/Private-WireGuard-VPS-Deployer.dmg
# ---------------------------------------------------------------------------

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
cd "$SCRIPT_DIR"

APP_NAME="Urban's Cannon"
APP_PATH="dist/$APP_NAME.app"
VERSION="1.2"
VOLNAME="Urban's Cannon"
DMG_NAME="Urbans-Cannon-${VERSION}"
DMG_PATH="dist/$DMG_NAME.dmg"
DMG_TMP="dist/.dmg_tmp"

echo "============================================"
echo " Creating DMG: $DMG_NAME"
echo "============================================"
echo ""

# --- 1. Check that .app exists ---
if [ ! -d "$APP_PATH" ]; then
    echo "ERROR: $APP_PATH not found."
    echo "Run ./build_macos.sh first."
    exit 1
fi
echo "[1/4] Found: $APP_PATH"

# --- 2. Remove old DMG ---
if [ -f "$DMG_PATH" ]; then
    echo "[2/4] Removing old DMG..."
    rm -f "$DMG_PATH"
else
    echo "[2/4] No old DMG to remove."
fi

# --- 3. Prepare temporary directory for DMG contents ---
echo "[3/4] Preparing DMG layout..."
rm -rf "$DMG_TMP"
mkdir -p "$DMG_TMP"

# Copy .app
cp -R "$APP_PATH" "$DMG_TMP/"

# Create a symlink to /Applications for easy drag-to-install
ln -s /Applications "$DMG_TMP/Applications"

# --- 4. Use hdiutil to create DMG ---
echo "[4/4] Creating DMG with hdiutil..."
hdiutil create \
    -volname "$VOLNAME" \
    -srcfolder "$DMG_TMP" \
    -ov \
    -format UDZO \
    -fs HFS+ \
    "$DMG_PATH"

# Clean up
rm -rf "$DMG_TMP"

echo ""
echo "============================================"
echo " DMG Created Successfully"
echo "============================================"
echo ""
echo " DMG: $(pwd)/$DMG_PATH"
echo ""
echo " Distribute this file to users. They can open it and"
echo " drag the app to their Applications folder."
echo ""
