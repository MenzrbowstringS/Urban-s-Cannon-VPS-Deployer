"""
generate_icon_win.py — Generate a multi-resolution .ico file from app_icon.png
for Windows PyInstaller packaging and Inno Setup.

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
    # Generate each size from the master image
    resized = [img.resize((s, s), Image.LANCZOS) for s in SIZES]
    # Save the first size with the rest appended
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
