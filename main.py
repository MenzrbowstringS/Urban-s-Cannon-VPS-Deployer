"""
main.py — Entry point for Urban's Cannon.

Brand-locked "Verdant Bronze" dark theme. We use Qt's Fusion style with a
custom dark palette so the bronze look renders consistently regardless of the
host system's light/dark mode (the app should always look like its icon).
"""

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor


def _apply_dark_palette(app: QApplication) -> None:
    """Verdant Bronze dark palette — see THEME in gui.py for the source tokens."""
    pal = QPalette()
    pal.setColor(QPalette.Window,          QColor("#1E1B16"))
    pal.setColor(QPalette.WindowText,      QColor("#F2ECE0"))
    pal.setColor(QPalette.Base,            QColor("#231F18"))
    pal.setColor(QPalette.AlternateBase,   QColor("#2E2820"))
    pal.setColor(QPalette.Text,            QColor("#F2ECE0"))
    pal.setColor(QPalette.PlaceholderText, QColor("#827767"))
    pal.setColor(QPalette.Button,          QColor("#2E2820"))
    pal.setColor(QPalette.ButtonText,      QColor("#F2ECE0"))
    pal.setColor(QPalette.Highlight,       QColor("#C5854C"))
    pal.setColor(QPalette.HighlightedText, QColor("#1C140C"))
    pal.setColor(QPalette.ToolTipBase,     QColor("#231F18"))
    pal.setColor(QPalette.ToolTipText,     QColor("#F2ECE0"))
    pal.setColor(QPalette.Disabled, QPalette.Text,       QColor("#827767"))
    pal.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#827767"))
    pal.setColor(QPalette.Disabled, QPalette.WindowText, QColor("#827767"))
    app.setPalette(pal)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Urban's Cannon")
    app.setOrganizationName("Urban's Cannon")

    # Fusion gives us full control over the dark theme; macOS native style
    # would fight our QSS and follow the system light/dark mode instead.
    app.setStyle("Fusion")
    _apply_dark_palette(app)

    # Dock icon is handled by the .app bundle's CFBundleIconFile.

    from gui import MainWindow
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
