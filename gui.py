"""
gui.py — "Verdant Bronze" interface for Urban's Cannon.

A brand-locked dark interface that looks like the product's own icon:
charcoal surfaces, bronze primary actions, patina-teal for success/active,
warm-stone text, and Menlo for technical values.

Interaction headline — the Connect → Configure → Deploy flow is a single
guided journey: a custom animated Stepper drives three sliding pages, and a
successful SSH connection auto-advances (with a teal success beat) straight
into VPN configuration.
"""

import os
from typing import Optional

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QGraphicsOpacityEffect,
    QDialog,
    QTextBrowser,
    QCheckBox,
)
from PySide6.QtCore import (
    Qt,
    QThread,
    Signal,
    QPropertyAnimation,
    QParallelAnimationGroup,
    QEasingCurve,
    QTimer,
    QPoint,
    QPointF,
    QRect,
    QRectF,
    QSize,
    QSettings,
    Property,
)
from PySide6.QtGui import QFont, QColor, QPainter, QPen, QPixmap, QPainterPath

from deployer import DeployConfig, test_ssh_connection, deploy_wireguard
import i18n
from i18n import tr, set_lang


# Premium "Linear-tier" easing — cubic-bezier(0.32, 0.72, 0, 1). Used for every
# transition so nothing ever moves on a generic linear / ease-in-out curve.
def _premium_ease() -> QEasingCurve:
    e = QEasingCurve(QEasingCurve.BezierSpline)
    e.addCubicBezierSegment(QPointF(0.32, 0.72), QPointF(0.0, 1.0), QPointF(1.0, 1.0))
    return e


def _reveal_in_file_manager(path: str) -> None:
    """Open the native file manager and select (highlight) the given file.

    Cross-platform: Finder on macOS, Explorer on Windows, xdg-open on Linux.
    """
    import subprocess
    import sys as _reveal_sys
    if _reveal_sys.platform == "darwin":
        subprocess.run(["open", "-R", path], check=False)
    elif _reveal_sys.platform == "win32":
        # /select, tells Explorer to highlight the file rather than open it.
        subprocess.run(["explorer", "/select,", path], check=False)
    else:
        subprocess.run(["xdg-open", os.path.dirname(path)], check=False)


def _resource_path(name: str) -> str:
    """Locate a bundled resource both in dev and inside the frozen .app."""
    import sys
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return os.path.join(base, "resources", name)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", name)


def _rounded_logo(size: int, radius: int) -> Optional[QPixmap]:
    """Load the app icon, scale it, and clip to a rounded square for the header."""
    src = QPixmap(_resource_path("app_icon.png"))
    if src.isNull():
        return None
    dpr = 2
    src = src.scaled(size * dpr, size * dpr, Qt.KeepAspectRatio,
                     Qt.SmoothTransformation)
    src.setDevicePixelRatio(dpr)          # logical size becomes `size`
    out = QPixmap(size * dpr, size * dpr)
    out.setDevicePixelRatio(dpr)
    out.fill(Qt.transparent)
    p = QPainter(out)
    p.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(QRectF(0, 0, size, size), radius, radius)   # logical coords
    p.setClipPath(path)
    p.drawPixmap(0, 0, src)
    p.end()
    return out


# ---------------------------------------------------------------------------
# Theme tokens — "Verdant Bronze"
# ---------------------------------------------------------------------------
THEME = {
    "bg":         "#1E1B16",  # warm charcoal (lifted out of near-black)
    # Double-bezel card stack: bg < tray (lip) < core (raised face); fields recess.
    "tray":       "#262119",  # card tray / outer shell
    "tray_brd":   "#393227",  # tray hairline
    "surface":    "#2E2820",  # card core (raised content face)
    "hairline":   "#403930",  # core hairline
    "hl":         "#52493C",  # core inner top highlight (machined edge)
    "surface_hi": "#231F18",  # input fields (recessed into the core)
    "field_brd":  "#433B30",  # input borders
    "text":       "#F2ECE0",  # warm stone (brighter)
    "text_dim":   "#A89C8B",  # labels / placeholders / status
    "text_mute":  "#827767",
    "bronze":     "#C5854C",
    "bronze_hi":  "#D6975A",
    "bronze_lo":  "#A96D39",
    "bronze_ink": "#1C140C",  # text on bronze
    "teal":       "#57B89A",  # patina — success / active
    "teal_ink":   "#0E2019",  # text on teal
    "amber":      "#E6AB4B",  # in-progress
    "red":        "#E5594C",  # failure
    "red_ink":    "#2A0E0B",
    "log_bg":     "#16130E",  # terminal
    "log_fg":     "#D2CABA",
}

import sys as _sys


def _mono_family() -> str:
    """Return the best available monospace font for the current platform."""
    if _sys.platform == "darwin":
        # Menlo ships with macOS and resolves reliably in Qt; "SF Mono" is a
        # restricted system font that QFont often cannot load by family name.
        return "Menlo"
    # Windows: Cascadia Code ships with Windows Terminal and newer Windows;
    # Consolas is the universal fallback that ships with every release.
    return "Cascadia Code"

APP_VERSION = "1.1"


def _qss() -> str:
    t = THEME
    return f"""
    QWidget#central {{
        background: qradialgradient(cx:0.18, cy:0.0, radius:1.1,
            fx:0.18, fy:0.0,
            stop:0 #2A2218, stop:0.45 {t['bg']}, stop:1 {t['bg']});
    }}
    QLabel {{ color: {t['text']}; background: transparent; }}
    QFrame#hrule {{ border: none; background: transparent; }}
    QLabel#footer {{ color: {t['text_mute']}; font-size: 10px; }}

    /* Double-bezel: a tray (lip) holding a raised core with a machined top edge */
    QFrame#tray {{
        background: {t['tray']};
        border: 1px solid {t['tray_brd']};
        border-radius: 17px;
    }}
    QFrame#card {{
        background: {t['surface']};
        border: 1px solid {t['hairline']};
        border-top: 1px solid {t['hl']};
        border-radius: 12px;
    }}
    QFrame#card[error="true"] {{
        border: 1px solid {t['red']};
        border-top: 1px solid {t['red']};
    }}

    QLineEdit, QComboBox {{
        background: {t['surface_hi']};
        border: 1px solid {t['field_brd']};
        border-radius: 9px;
        padding: 7px 12px;
        min-height: 16px;            /* never compress below text height (anti-squish) */
        color: {t['text']};
        selection-background-color: {t['bronze']};
        selection-color: {t['bronze_ink']};
    }}
    QLineEdit:focus, QComboBox:focus {{ border: 1px solid {t['teal']}; }}
    QLineEdit:disabled, QComboBox:disabled {{ color: {t['text_mute']}; }}
    QComboBox::drop-down {{ border: none; width: 22px; }}
    QComboBox QAbstractItemView {{
        background: {t['surface_hi']};
        border: 1px solid {t['field_brd']};
        border-radius: 8px;
        color: {t['text']};
        selection-background-color: {t['bronze']};
        selection-color: {t['bronze_ink']};
        outline: none;
        padding: 4px;
    }}

    QPushButton#primary {{
        background: {t['bronze']}; color: {t['bronze_ink']};
        border: none; border-radius: 9px;
        font-size: 13px; font-weight: 600; padding: 10px 24px;
    }}
    QPushButton#primary:hover {{ background: {t['bronze_hi']}; }}
    QPushButton#primary:pressed {{ background: {t['bronze_lo']}; }}
    QPushButton#primary:disabled {{ background: #3A332B; color: {t['text_mute']}; }}

    QPushButton#secondary {{
        background: transparent; color: {t['text']};
        border: 1px solid {t['field_brd']}; border-radius: 8px;
        font-size: 12px; padding: 8px 16px;
    }}
    QPushButton#secondary:hover {{ background: {t['surface_hi']}; border-color: #4A443A; }}
    QPushButton#secondary:disabled {{ color: {t['text_mute']}; border-color: {t['hairline']}; }}

    QPushButton#lang {{
        background: {t['surface_hi']}; color: {t['text_dim']};
        border: 1px solid {t['field_brd']}; border-radius: 7px;
        font-size: 11px; font-weight: 600;
    }}
    QPushButton#lang:hover {{ color: {t['text']}; border-color: #4A443A; }}

    QPushButton#help {{
        background: {t['surface_hi']}; color: {t['bronze']};
        border: 1px solid {t['field_brd']}; border-radius: 14px;
        font-size: 14px; font-weight: 700;
    }}
    QPushButton#help:hover {{ color: {t['bronze_hi']}; border-color: {t['bronze']}; }}

    QPlainTextEdit#log {{
        background: {t['log_bg']}; color: {t['log_fg']};
        border: 1px solid {t['hairline']}; border-radius: 12px;
        padding: 14px;
    }}

    QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
    QScrollBar::handle:vertical {{ background: #3A332B; border-radius: 5px; min-height: 28px; }}
    QScrollBar::handle:vertical:hover {{ background: #4A443A; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}

    QToolTip {{
        background: {t['surface_hi']}; color: {t['text']};
        border: 1px solid {t['field_brd']}; padding: 5px 9px; border-radius: 6px;
    }}
    """


# ---------------------------------------------------------------------------
# Worker threads
# ---------------------------------------------------------------------------
class SSHTestWorker(QThread):
    finished_signal = Signal(bool, str)

    def __init__(self, config: DeployConfig, parent=None):
        super().__init__(parent)
        self.config = config

    def run(self):
        try:
            msg = test_ssh_connection(self.config)
            self.finished_signal.emit(True, msg)
        except Exception as e:
            self.finished_signal.emit(False, str(e))


class DeployWorker(QThread):
    log_signal = Signal(str)
    finished_signal = Signal(bool, str, str)

    def __init__(self, config: DeployConfig, parent=None):
        super().__init__(parent)
        self.config = config

    def run(self):
        try:
            output_path = deploy_wireguard(self.config, log_callback=self._log)
            self.finished_signal.emit(True, "Deployment successful.", output_path)
        except Exception as e:
            self.finished_signal.emit(False, str(e), "")

    def _log(self, msg: str):
        self.log_signal.emit(msg)


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------
def _card() -> QFrame:
    """A double-bezel card: an outer tray (carrying a wide, diffuse ambient
    shadow) wrapping a raised inner core where content lives. The core carries
    an opacity effect so it can fade in on entry."""
    tray = QFrame()
    tray.setObjectName("tray")
    # Parent the effect to the tray so Qt owns it — an unparented effect created
    # in this function scope would be garbage-collected on return.
    shadow = QGraphicsDropShadowEffect(tray)
    shadow.setBlurRadius(46)          # wide + diffuse, not a harsh drop shadow
    shadow.setXOffset(0)
    shadow.setYOffset(14)
    shadow.setColor(QColor(0, 0, 0, 66))
    tray.setGraphicsEffect(shadow)

    outer = QVBoxLayout(tray)
    outer.setContentsMargins(5, 5, 5, 5)
    outer.setSpacing(0)

    core = QFrame()
    core.setObjectName("card")
    # Disabled at rest: a disabled effect renders the widget on the normal
    # (crisp) path. We only enable it briefly for the stationary entry fade —
    # an *enabled* opacity effect on a widget that is also being position-
    # animated produces stale/offset cached pixmaps.
    eff = QGraphicsOpacityEffect(core)
    eff.setEnabled(False)
    core.setGraphicsEffect(eff)
    outer.addWidget(core)

    tray._core = core
    return tray


def _card_layout(tray: QFrame) -> QVBoxLayout:
    layout = QVBoxLayout(tray._core)
    layout.setContentsMargins(22, 16, 22, 16)
    layout.setSpacing(0)
    return layout


def _section_title(text: str) -> QLabel:
    label = QLabel(text.upper())
    f = label.font()
    f.setPointSize(10)
    f.setBold(True)
    f.setLetterSpacing(QFont.AbsoluteSpacing, 1.2)
    label.setFont(f)
    label.setStyleSheet(f"color: {THEME['text_dim']};")
    return label


def _mono(widget: QWidget) -> QWidget:
    f = QFont(_mono_family())
    f.setStyleHint(QFont.Monospace)
    f.setPointSize(12)
    widget.setFont(f)
    return widget


def _form_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(f"color: {THEME['text_dim']};")
    return lbl


def _status_dot(color: str) -> QLabel:
    dot = QLabel()
    dot.setFixedSize(9, 9)
    dot.setStyleSheet(f"background: {color}; border-radius: 4px;")
    return dot


# ---------------------------------------------------------------------------
# Stepper — custom-painted guided progress rail
# ---------------------------------------------------------------------------
class Stepper(QWidget):
    """Three connected nodes (Connect · Configure · Deploy) with an animated
    teal rail. Completed steps show a check, the current step is bronze, and
    upcoming steps are dim outlines. Clicking a node requests navigation."""

    stepClicked = Signal(int)
    lockedStepClicked = Signal(int)

    def __init__(self, labels, parent=None):
        super().__init__(parent)
        self._labels = list(labels)
        self._n = len(labels)
        self._current = 0
        self._rail = 0.0          # animated fill position in [0, n-1]
        self._hover = -1
        self._max_enabled = 0     # highest step the user may jump to (gating)
        self._anim: Optional[QPropertyAnimation] = None
        self.setFixedHeight(62)
        self.setMinimumWidth(380)
        self.setMouseTracking(True)

    # --- animated rail property ---
    def _get_rail(self) -> float:
        return self._rail

    def _set_rail(self, v: float):
        self._rail = v
        self.update()

    rail = Property(float, _get_rail, _set_rail)

    # --- public API ---
    def set_step(self, index: int, animate: bool = True):
        index = max(0, min(self._n - 1, index))
        self._current = index
        if animate:
            self._anim = QPropertyAnimation(self, b"rail", self)
            self._anim.setDuration(360)
            self._anim.setStartValue(self._rail)
            self._anim.setEndValue(float(index))
            self._anim.setEasingCurve(_premium_ease())
            self._anim.start()
        else:
            self._rail = float(index)
            self.update()

    def current(self) -> int:
        return self._current

    def set_max_enabled(self, index: int):
        self._max_enabled = max(self._max_enabled, index)
        self.update()

    def set_labels(self, labels):
        self._labels = list(labels)
        self.update()

    # --- geometry ---
    def _node_centers(self):
        pad = 56
        w = self.width()
        if self._n <= 1:
            return [w / 2]
        return [pad + i * (w - 2 * pad) / (self._n - 1) for i in range(self._n)]

    _NODE_Y = 22
    _NODE_R = 14

    def _hit(self, x, y) -> int:
        for i, cx in enumerate(self._node_centers()):
            if abs(x - cx) < 42 and abs(y - self._NODE_Y) < 30:
                return i
        return -1

    # --- events ---
    def mousePressEvent(self, e):
        i = self._hit(e.position().x(), e.position().y())
        if i == -1 or i == self._current:
            return
        if i <= self._max_enabled:
            self.stepClicked.emit(i)
        else:
            self.lockedStepClicked.emit(i)

    def mouseMoveEvent(self, e):
        i = self._hit(e.position().x(), e.position().y())
        # only enabled, non-current nodes are interactive
        h = i if (i != -1 and i <= self._max_enabled and i != self._current) else -1
        self.setCursor(Qt.PointingHandCursor if h != -1 else Qt.ArrowCursor)
        if h != self._hover:
            self._hover = h
            self.update()

    def leaveEvent(self, e):
        if self._hover != -1:
            self._hover = -1
            self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        centers = self._node_centers()
        y = self._NODE_Y
        r = self._NODE_R
        x0, x1 = centers[0], centers[-1]

        # rail — background then teal fill
        p.setPen(QPen(QColor(THEME["hairline"]), 2))
        p.drawLine(int(x0), y, int(x1), y)
        if self._rail > 0 and self._n > 1:
            frac = self._rail / (self._n - 1)
            xe = x0 + (x1 - x0) * frac
            p.setPen(QPen(QColor(THEME["teal"]), 2))
            p.drawLine(int(x0), y, int(xe), y)

        node_font = QFont(_mono_family())
        node_font.setStyleHint(QFont.Monospace)
        node_font.setPointSize(11)
        node_font.setBold(True)

        for i, cx in enumerate(centers):
            done = i < self._current
            current = i == self._current
            locked = (not done) and (not current) and (i > self._max_enabled)
            rect = QRectF(cx - r, y - r, 2 * r, 2 * r)

            if current:
                # soft bronze glow ring
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(184, 118, 62, 55))
                p.drawEllipse(QRectF(cx - r - 5, y - r - 5, 2 * r + 10, 2 * r + 10))
                p.setBrush(QColor(THEME["bronze"]))
                p.drawEllipse(rect)
            elif done:
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(THEME["teal"]))
                p.drawEllipse(rect)
            else:
                p.setBrush(QColor(THEME["surface"]))
                edge = "#4A443A" if (i == self._hover and not locked) else THEME["field_brd"]
                p.setPen(QPen(QColor(edge), 1.5))
                p.drawEllipse(rect)

            # node glyph
            p.setFont(node_font)
            if done:
                p.setPen(QColor(THEME["teal_ink"]))
                p.drawText(rect, Qt.AlignCenter, "✓")
            elif current:
                p.setPen(QColor(THEME["bronze_ink"]))
                p.drawText(rect, Qt.AlignCenter, str(i + 1))
            elif locked:
                self._draw_lock(p, cx, y, THEME["text_mute"])
            else:
                p.setPen(QColor(THEME["text_dim"] if i == self._hover else THEME["text_mute"]))
                p.drawText(rect, Qt.AlignCenter, str(i + 1))

            # label
            lf = QFont()
            lf.setPointSize(11)
            lf.setBold(current)
            p.setFont(lf)
            if current:
                p.setPen(QColor(THEME["text"]))
            elif done:
                p.setPen(QColor(THEME["teal"]))
            elif locked:
                p.setPen(QColor(THEME["text_mute"]))
            else:
                p.setPen(QColor(THEME["text_dim"]))
            p.drawText(QRectF(cx - 64, y + r + 7, 128, 18), Qt.AlignCenter, self._labels[i])

        p.end()

    def _draw_lock(self, p, cx, cy, color):
        """Tiny padlock glyph for locked steps."""
        p.save()
        c = QColor(color)
        # shackle
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(c, 1.5))
        p.drawArc(QRectF(cx - 3.0, cy - 5.2, 6.0, 6.4), 0, 180 * 16)
        # body
        p.setPen(Qt.NoPen)
        p.setBrush(c)
        p.drawRoundedRect(QRectF(cx - 4.2, cy - 1.6, 8.4, 6.6), 1.3, 1.3)
        p.restore()


# ---------------------------------------------------------------------------
# Sliding pages
# ---------------------------------------------------------------------------
class SlidingStackedWidget(QStackedWidget):
    """QStackedWidget with a horizontal slide transition between pages."""

    DURATION = 300

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active = False

    def is_animating(self) -> bool:
        return self._active

    # Report only the CURRENT page's size, not the tallest page's. This lets the
    # window shrink to fit a short page (Connect) instead of always reserving
    # room for the tallest one (Configure), which otherwise leaves dead space.
    def sizeHint(self) -> QSize:
        w = self.currentWidget()
        return w.sizeHint() if w is not None else super().sizeHint()

    def minimumSizeHint(self) -> QSize:
        w = self.currentWidget()
        return w.minimumSizeHint() if w is not None else super().minimumSizeHint()

    def slide_to(self, index: int):
        current = self.currentIndex()
        if self._active or index == current or index < 0 or index >= self.count():
            if not self._active and index != current:
                self.setCurrentIndex(index)
            return

        direction = 1 if index > current else -1
        w = self.frameRect().width()
        next_page = self.widget(index)

        # Pre-size the incoming page to its own content height (and at least the
        # current viewport height) so it never squishes while the window resizes.
        content_h = max(next_page.sizeHint().height(), next_page.minimumSizeHint().height())
        h = max(content_h, self.height())
        next_page.setGeometry(QRect(direction * w, 0, w, h))
        next_page.show()
        next_page.raise_()                  # incoming slides in OVER the outgoing
        self._active = True

        # Only the incoming page is animated. The outgoing page stays put (it is
        # fully covered by the end); animating it too would fight the stacked
        # layout while the window height animates, producing jitter.
        self._slide_anim = QPropertyAnimation(next_page, b"pos", self)
        self._slide_anim.setDuration(self.DURATION)
        self._slide_anim.setStartValue(QPoint(direction * w, 0))
        self._slide_anim.setEndValue(QPoint(0, 0))
        self._slide_anim.setEasingCurve(_premium_ease())

        def _done():
            self.setCurrentIndex(index)
            self._active = False

        self._slide_anim.finished.connect(_done)
        self._slide_anim.start()


# ---------------------------------------------------------------------------
# Help / Instructions dialog
# ---------------------------------------------------------------------------
class HelpDialog(QDialog):
    """Verdant Bronze styled 'How to Use' dialog with a startup toggle."""

    def __init__(self, parent=None):
        super().__init__(parent)
        t = THEME
        self.setWindowTitle(tr("help_title"))
        self.setModal(True)
        self.setMinimumSize(500, 540)
        self.resize(520, 600)
        self.setStyleSheet(f"""
            QDialog {{ background: {t['bg']}; }}
            QTextBrowser {{
                background: {t['tray']}; border: 1px solid {t['hairline']};
                border-radius: 12px; padding: 16px 18px; color: {t['text']};
            }}
            QCheckBox {{ color: {t['text_dim']}; font-size: 12px; }}
            QCheckBox::indicator {{
                width: 15px; height: 15px; border-radius: 4px;
                border: 1px solid {t['field_brd']}; background: {t['surface_hi']};
            }}
            QCheckBox::indicator:checked {{ background: {t['bronze']}; border-color: {t['bronze']}; }}
            QPushButton#primary {{
                background: {t['bronze']}; color: {t['bronze_ink']}; border: none;
                border-radius: 9px; font-size: 13px; font-weight: 600; padding: 9px 22px;
            }}
            QPushButton#primary:hover {{ background: {t['bronze_hi']}; }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 20, 22, 18)
        lay.setSpacing(14)

        # header: logo + title
        hdr = QHBoxLayout()
        hdr.setSpacing(12)
        logo = _rounded_logo(36, 9)
        if logo is not None:
            lb = QLabel()
            lb.setPixmap(logo)
            lb.setFixedSize(36, 36)
            hdr.addWidget(lb, alignment=Qt.AlignVCenter)
        title = QLabel(tr("help_title"))
        tfont = title.font()
        tfont.setPointSize(16)
        tfont.setWeight(QFont.DemiBold)
        title.setFont(tfont)
        title.setStyleSheet(f"color: {t['text']};")
        hdr.addWidget(title)
        hdr.addStretch()
        ver = QLabel(f"Urban's Cannon · v{APP_VERSION}")
        vfont = QFont(_mono_family())
        vfont.setPointSize(10)
        ver.setFont(vfont)
        ver.setStyleSheet(f"color: {t['text_mute']};")
        hdr.addWidget(ver, alignment=Qt.AlignVCenter)
        lay.addLayout(hdr)

        # body
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setHtml(tr("help_html"))
        lay.addWidget(self.browser, stretch=1)

        # footer: startup toggle + close
        footer = QHBoxLayout()
        footer.setSpacing(10)
        self.dont_show = QCheckBox(tr("help_dont_show"))
        self.dont_show.setCursor(Qt.PointingHandCursor)
        self.dont_show.setChecked(not QSettings().value("help/show_on_start", True, type=bool))
        footer.addWidget(self.dont_show)
        footer.addStretch()
        ok = QPushButton(tr("help_got_it"))
        ok.setObjectName("primary")
        ok.setCursor(Qt.PointingHandCursor)
        ok.setFixedHeight(38)
        ok.setMinimumWidth(110)
        ok.clicked.connect(self.accept)
        footer.addWidget(ok)
        lay.addLayout(footer)

    def _persist(self):
        QSettings().setValue("help/show_on_start", not self.dont_show.isChecked())

    def accept(self):
        self._persist()
        super().accept()

    def closeEvent(self, event):
        self._persist()
        super().closeEvent(event)


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):

    SSH_UNTESTED = 0
    SSH_SUCCESS = 1
    SSH_FAILURE = 2
    SSH_BUSY = 3

    STEP_CONNECT = 0
    STEP_CONFIGURE = 1
    STEP_DEPLOY = 2

    def __init__(self):
        super().__init__()
        self._worker: Optional[QThread] = None
        self._last_output_path: str = ""
        self._entry_anims = []      # keeps stagger animations alive
        self._did_intro = False
        self._init_ui()

    def closeEvent(self, event):
        if self._worker and self._worker.isRunning():
            self._worker.quit()
            self._worker.wait(3000)
        event.accept()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._did_intro:
            self._did_intro = True
            QTimer.singleShot(0, self._first_layout_ready)

    def _first_layout_ready(self):
        # Chrome = everything around the page stack (header, stepper, status,
        # margins). Constant across pages, so we measure it once.
        self._chrome_h = self.height() - self.stack.height()
        self._fit_to_page(self.STEP_CONNECT, animate=False)
        self._stagger_page_in(self.STEP_CONNECT)
        if QSettings().value("help/show_on_start", True, type=bool):
            QTimer.singleShot(300, self._open_help)

    def _open_help(self):
        HelpDialog(self).exec()

    # ==================================================================
    # UI construction
    # ==================================================================
    def _init_ui(self):
        self.setWindowTitle("Urban's Cannon")
        # Hard floor only; the window auto-sizes to each step's content (see
        # _fit_to_page), so it opens compact on Connect and grows for Configure.
        self.setMinimumSize(620, 440)
        self.resize(680, 600)

        central = QWidget()
        central.setObjectName("central")
        central.setStyleSheet(_qss())
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(30, 18, 30, 14)
        root.setSpacing(0)

        # ---- Header ----
        title_row = QHBoxLayout()
        title_row.setSpacing(14)

        # Brand logo chip (the bronze cannon mark)
        logo_pm = _rounded_logo(44, 11)
        if logo_pm is not None:
            self.logo_label = QLabel()
            self.logo_label.setPixmap(logo_pm)
            self.logo_label.setFixedSize(44, 44)
            shadow = QGraphicsDropShadowEffect(self.logo_label)
            shadow.setBlurRadius(18)
            shadow.setXOffset(0)
            shadow.setYOffset(4)
            shadow.setColor(QColor(0, 0, 0, 120))
            self.logo_label.setGraphicsEffect(shadow)
            title_row.addWidget(self.logo_label, alignment=Qt.AlignVCenter)

        title_block = QVBoxLayout()
        title_block.setSpacing(3)

        self.title_label = QLabel(tr("app_title"))
        tf = self.title_label.font()
        tf.setPointSize(21)
        tf.setWeight(QFont.DemiBold)
        tf.setLetterSpacing(QFont.AbsoluteSpacing, 0.4)
        self.title_label.setFont(tf)
        self.title_label.setStyleSheet(f"color: {THEME['text']};")

        self.subtitle_label = QLabel(tr("app_subtitle"))
        sf = self.subtitle_label.font()
        sf.setPointSize(11)
        self.subtitle_label.setFont(sf)
        self.subtitle_label.setStyleSheet(f"color: {THEME['text_dim']};")

        title_block.addWidget(self.title_label)
        title_block.addWidget(self.subtitle_label)
        title_row.addLayout(title_block, stretch=1)

        self.help_btn = QPushButton("?")
        self.help_btn.setObjectName("help")
        self.help_btn.setFixedSize(28, 28)
        self.help_btn.setCursor(Qt.PointingHandCursor)
        self.help_btn.setToolTip(tr("help_tooltip"))
        self.help_btn.clicked.connect(self._open_help)
        title_row.addWidget(self.help_btn, alignment=Qt.AlignTop)

        self.lang_btn = QPushButton(tr("lang_label"))
        self.lang_btn.setObjectName("lang")
        self.lang_btn.setFixedSize(38, 28)
        self.lang_btn.setCursor(Qt.PointingHandCursor)
        self.lang_btn.clicked.connect(self._toggle_language)
        title_row.addWidget(self.lang_btn, alignment=Qt.AlignTop)

        root.addLayout(title_row)
        root.addSpacing(14)

        # ---- Header divider (bronze hairline, fading at the edges) ----
        rule = QFrame()
        rule.setObjectName("hrule")
        rule.setFixedHeight(1)
        rule.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            f"stop:0 transparent, stop:0.5 {THEME['bronze']}66, stop:1 transparent);")
        root.addWidget(rule)
        root.addSpacing(16)

        # ---- Stepper ----
        self.stepper = Stepper([tr("step_connect"), tr("step_configure"), tr("step_deploy")])
        self.stepper.stepClicked.connect(self._navigate)
        self.stepper.lockedStepClicked.connect(self._on_locked_step)
        root.addWidget(self.stepper)
        root.addSpacing(12)

        # ---- Sliding pages ----
        self.stack = SlidingStackedWidget()
        self.stack.addWidget(self._build_connection_page())
        self.stack.addWidget(self._build_vpn_page())
        self.stack.addWidget(self._build_log_page())
        root.addWidget(self.stack, stretch=1)

        # ---- Status bar ----
        root.addSpacing(10)
        status_row = QHBoxLayout()
        status_row.setSpacing(8)
        self.status_label = QLabel(tr("status_ready"))
        self.status_label.setStyleSheet(f"color: {THEME['text_dim']}; font-size: 11px;")
        status_row.addWidget(self.status_label)
        status_row.addStretch()
        # footer: live connection-status indicator (dot + label)
        self.footer_dot = _status_dot(THEME["text_mute"])
        status_row.addWidget(self.footer_dot, alignment=Qt.AlignVCenter)
        self.footer_label = QLabel()
        self.footer_label.setObjectName("footer")
        ff = QFont(_mono_family())
        ff.setPointSize(10)
        self.footer_label.setFont(ff)
        status_row.addWidget(self.footer_label, alignment=Qt.AlignVCenter)
        root.addLayout(status_row)
        self._set_footer(self.SSH_UNTESTED)

    # ==================================================================
    # Page 1 — Connection
    # ==================================================================
    def _build_connection_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 2, 0, 0)
        layout.setSpacing(13)

        self.conn_tray = _card()
        self.conn_card = self.conn_tray._core   # the bordered face (error flash target)
        cl = _card_layout(self.conn_tray)
        self.conn_section_title = _section_title(tr("vps_connection"))
        cl.addWidget(self.conn_section_title)
        cl.addSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)
        form.setContentsMargins(0, 0, 0, 0)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.host_label = _form_label(tr("host_ip"))
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText(tr("placeholder_host"))
        self.host_input.setMinimumWidth(300)
        _mono(self.host_input)
        form.addRow(self.host_label, self.host_input)

        port_user_row = QHBoxLayout()
        port_user_row.setSpacing(12)
        self.port_input = QLineEdit("22")
        self.port_input.setFixedWidth(84)
        self.port_input.setPlaceholderText("22")
        _mono(self.port_input)
        port_user_row.addWidget(self.port_input)
        self.username_input = QLineEdit("root")
        self.username_input.setPlaceholderText("root")
        _mono(self.username_input)
        port_user_row.addWidget(self.username_input, stretch=1)
        self.pu_label = _form_label(tr("ssh_port") + " / " + tr("username"))
        form.addRow(self.pu_label, port_user_row)

        self.auth_label = _form_label(tr("auth_method"))
        self.auth_combo = QComboBox()
        self.auth_combo.addItems([tr("auth_password"), tr("auth_key")])
        self.auth_combo.currentIndexChanged.connect(self._on_auth_changed)
        form.addRow(self.auth_label, self.auth_combo)

        self.pwd_label = _form_label(tr("password"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText(tr("placeholder_password"))
        form.addRow(self.pwd_label, self.password_input)

        self.key_label = _form_label(tr("ssh_key"))
        key_row = QHBoxLayout()
        key_row.setSpacing(8)
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText(tr("placeholder_key"))
        _mono(self.key_input)
        key_row.addWidget(self.key_input)
        self.key_browse_btn = QPushButton(tr("browse"))
        self.key_browse_btn.setObjectName("secondary")
        self.key_browse_btn.setCursor(Qt.PointingHandCursor)
        self.key_browse_btn.clicked.connect(self._browse_key)
        key_row.addWidget(self.key_browse_btn)
        form.addRow(self.key_label, key_row)
        self.key_input.setVisible(False)
        self.key_browse_btn.setVisible(False)
        self.key_label.setVisible(False)

        cl.addLayout(form)
        layout.addWidget(self.conn_tray)

        # Connect action row
        connect_row = QHBoxLayout()
        connect_row.setSpacing(10)
        self.ssh_dot = _status_dot(THEME["text_mute"])
        connect_row.addWidget(self.ssh_dot, alignment=Qt.AlignVCenter)
        self.ssh_hint = QLabel("")
        self.ssh_hint.setStyleSheet(f"color: {THEME['text_dim']}; font-size: 11px;")
        connect_row.addWidget(self.ssh_hint)
        connect_row.addStretch()
        self.connect_btn = QPushButton(tr("connect"))
        self.connect_btn.setObjectName("primary")
        self.connect_btn.setCursor(Qt.PointingHandCursor)
        self.connect_btn.setFixedHeight(40)
        self.connect_btn.setMinimumWidth(150)
        self.connect_btn.clicked.connect(self._on_connect)
        connect_row.addWidget(self.connect_btn)
        layout.addLayout(connect_row)

        layout.addStretch()
        return page

    # ==================================================================
    # Page 2 — VPN Config
    # ==================================================================
    def _build_vpn_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 2, 0, 0)
        layout.setSpacing(13)

        # Card 1: WireGuard Settings
        card1 = _card()
        c1 = _card_layout(card1)
        self.wg_section_title = _section_title(tr("wg_settings"))
        c1.addWidget(self.wg_section_title)
        c1.addSpacing(12)

        form1 = QFormLayout()
        form1.setSpacing(10)
        form1.setContentsMargins(0, 0, 0, 0)
        form1.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.wg_port_label = _form_label(tr("listen_port"))
        self.wg_port_input = QLineEdit("51820")
        self.wg_port_input.setFixedWidth(120)
        _mono(self.wg_port_input)
        form1.addRow(self.wg_port_label, self.wg_port_input)

        self.subnet_label = _form_label(tr("vpn_subnet"))
        self.subnet_input = QLineEdit("10.8.0.0/24")
        _mono(self.subnet_input)
        form1.addRow(self.subnet_label, self.subnet_input)

        self.server_label = _form_label(tr("server_addr"))
        self.server_addr_input = QLineEdit("10.8.0.1/24")
        _mono(self.server_addr_input)
        form1.addRow(self.server_label, self.server_addr_input)

        self.client_addr_label = _form_label(tr("client_addr"))
        self.client_addr_input = QLineEdit("10.8.0.2/32")
        _mono(self.client_addr_input)
        form1.addRow(self.client_addr_label, self.client_addr_input)

        self.dns_label = _form_label(tr("dns"))
        self.dns_input = QLineEdit("1.1.1.1, 8.8.8.8")
        _mono(self.dns_input)
        form1.addRow(self.dns_label, self.dns_input)

        self.allowed_label = _form_label(tr("allowed_ips"))
        self.allowed_ips_input = QLineEdit("0.0.0.0/0")
        _mono(self.allowed_ips_input)
        form1.addRow(self.allowed_label, self.allowed_ips_input)

        c1.addLayout(form1)
        layout.addWidget(card1)

        # Card 2: Client
        card2 = _card()
        c2 = _card_layout(card2)
        self.client_section_title = _section_title(tr("client_section"))
        c2.addWidget(self.client_section_title)
        c2.addSpacing(12)

        form2 = QFormLayout()
        form2.setSpacing(10)
        form2.setContentsMargins(0, 0, 0, 0)
        form2.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.client_name_label = _form_label(tr("client_name"))
        self.client_name_input = QLineEdit("macbook")
        form2.addRow(self.client_name_label, self.client_name_input)

        self.output_label = _form_label(tr("output"))
        out_row = QHBoxLayout()
        out_row.setSpacing(8)
        default_out = os.path.join(os.path.expanduser("~"), "Desktop", "macbook-wireguard.conf")
        self.output_path_input = QLineEdit(default_out)
        _mono(self.output_path_input)
        out_row.addWidget(self.output_path_input)
        self.out_browse_btn = QPushButton(tr("browse"))
        self.out_browse_btn.setObjectName("secondary")
        self.out_browse_btn.setCursor(Qt.PointingHandCursor)
        self.out_browse_btn.clicked.connect(self._browse_output)
        out_row.addWidget(self.out_browse_btn)
        form2.addRow(self.output_label, out_row)

        self.client_name_input.textChanged.connect(self._update_output_path)

        c2.addLayout(form2)
        layout.addWidget(card2)

        # Deploy button
        deploy_row = QHBoxLayout()
        deploy_row.addStretch()
        self.deploy_btn = QPushButton(tr("deploy_vpn"))
        self.deploy_btn.setObjectName("primary")
        self.deploy_btn.clicked.connect(self._on_deploy)
        self.deploy_btn.setFixedHeight(42)
        self.deploy_btn.setMinimumWidth(170)
        self.deploy_btn.setCursor(Qt.PointingHandCursor)
        deploy_row.addWidget(self.deploy_btn)
        layout.addLayout(deploy_row)

        layout.addStretch()
        return page

    # ==================================================================
    # Page 3 — Log
    # ==================================================================
    def _build_log_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 2, 0, 0)
        layout.setSpacing(12)

        self.log_view = QPlainTextEdit()
        self.log_view.setObjectName("log")
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumBlockCount(5000)
        self.log_view.setMinimumHeight(360)   # keep the Deploy page comfortably tall
        lf = QFont(_mono_family())
        lf.setStyleHint(QFont.Monospace)
        lf.setPointSize(11)
        self.log_view.setFont(lf)
        layout.addWidget(self.log_view, stretch=1)

        bar = QHBoxLayout()
        bar.setSpacing(8)
        self.open_finder_btn = QPushButton(tr("show_finder"))
        self.open_finder_btn.setEnabled(False)
        self.open_finder_btn.setObjectName("secondary")
        self.open_finder_btn.setCursor(Qt.PointingHandCursor)
        self.open_finder_btn.clicked.connect(self._on_open_finder)
        bar.addWidget(self.open_finder_btn)
        bar.addStretch()
        self.clear_log_btn = QPushButton(tr("clear_log"))
        self.clear_log_btn.setObjectName("secondary")
        self.clear_log_btn.setCursor(Qt.PointingHandCursor)
        self.clear_log_btn.clicked.connect(self._on_clear_log)
        bar.addWidget(self.clear_log_btn)
        layout.addLayout(bar)

        return page

    # ==================================================================
    # Navigation
    # ==================================================================
    def _navigate(self, index: int):
        if self.stack.is_animating():
            return
        # The slide transition is itself the page's entrance; we deliberately do
        # NOT run the opacity stagger here (effect + motion = cached-pixmap glitch).
        self.stack.slide_to(index)
        self.stepper.set_step(index)
        self._fit_to_page(index)

    def _on_locked_step(self, index: int):
        """User clicked a step that isn't unlocked yet — guide them to connect."""
        self.status_label.setText(tr("status_connect_first"))
        if self.stack.currentIndex() != self.STEP_CONNECT:
            self._navigate(self.STEP_CONNECT)
        else:
            self._flash_card_error()

    def _fit_to_page(self, index: int, animate: bool = True):
        """Size the window height to the target step's content (no dead space)."""
        if getattr(self, "_chrome_h", None) is None:
            return
        page = self.stack.widget(index)
        content = max(page.sizeHint().height(), page.minimumSizeHint().height())
        target = max(self.minimumHeight(), self._chrome_h + content)
        if not animate:
            self.resize(self.width(), target)
            return
        self._resize_anim = QPropertyAnimation(self, b"size", self)
        self._resize_anim.setDuration(self.stack.DURATION)
        self._resize_anim.setStartValue(self.size())
        self._resize_anim.setEndValue(QSize(self.width(), target))
        self._resize_anim.setEasingCurve(_premium_ease())
        self._resize_anim.start()

    def _stagger_page_in(self, index: int):
        """Fade a stationary page's cards up in sequence — used for the initial
        reveal so nothing appears statically on first paint."""
        page = self.stack.widget(index)
        cards = [c for c in page.findChildren(QFrame) if c.objectName() == "card"]
        self._entry_anims = []
        for i, core in enumerate(cards):
            eff = core.graphicsEffect()
            if not isinstance(eff, QGraphicsOpacityEffect):
                continue
            eff.setEnabled(True)
            eff.setOpacity(0.0)
            anim = QPropertyAnimation(eff, b"opacity", self)
            anim.setDuration(480)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(_premium_ease())
            anim.finished.connect(lambda e=eff: e.setEnabled(False))
            self._entry_anims.append(anim)
            QTimer.singleShot(50 + i * 95, anim.start)

    # ==================================================================
    # SSH status indicator
    # ==================================================================
    def _set_ssh_state(self, state: int, hint: str = ""):
        colors = {
            self.SSH_UNTESTED: THEME["text_mute"],
            self.SSH_SUCCESS: THEME["teal"],
            self.SSH_FAILURE: THEME["red"],
            self.SSH_BUSY: THEME["amber"],
        }
        self.ssh_dot.setStyleSheet(f"background: {colors[state]}; border-radius: 4px;")
        self.ssh_hint.setText(hint)
        self._set_footer(state)

    def _set_footer(self, state: int):
        """Footer indicator reflects live SSH connection state."""
        self._footer_state = state
        if state == self.SSH_SUCCESS:
            color, key = THEME["teal"], "footer_connected"
        elif state == self.SSH_BUSY:
            color, key = THEME["amber"], "footer_connecting"
        else:  # untested or failed → not connected
            color, key = THEME["text_mute"], "footer_disconnected"
        self.footer_dot.setStyleSheet(f"background: {color}; border-radius: 4px;")
        self.footer_label.setText(tr(key))

    # --- connect button visual states ---
    def _connect_btn_idle(self):
        self.connect_btn.setObjectName("primary")
        self.connect_btn.setStyleSheet("")
        self.connect_btn.setText(tr("connect"))
        # re-polish so the #primary QSS reapplies after an inline override
        self.connect_btn.style().unpolish(self.connect_btn)
        self.connect_btn.style().polish(self.connect_btn)

    def _connect_btn_success(self):
        t = THEME
        self.connect_btn.setStyleSheet(
            f"background: {t['teal']}; color: {t['teal_ink']}; border: none;"
            f"border-radius: 9px; font-size: 13px; font-weight: 600; padding: 10px 24px;")
        self.connect_btn.setText(tr("connected"))

    def _connect_btn_failed(self):
        t = THEME
        self.connect_btn.setStyleSheet(
            f"background: {t['red']}; color: {t['red_ink']}; border: none;"
            f"border-radius: 9px; font-size: 13px; font-weight: 600; padding: 10px 24px;")
        self.connect_btn.setText(tr("connect_failed"))

    def _flash_card_error(self):
        self.conn_card.setProperty("error", True)
        self.conn_card.style().unpolish(self.conn_card)
        self.conn_card.style().polish(self.conn_card)
        QTimer.singleShot(900, self._clear_card_error)

    def _clear_card_error(self):
        self.conn_card.setProperty("error", False)
        self.conn_card.style().unpolish(self.conn_card)
        self.conn_card.style().polish(self.conn_card)

    # ==================================================================
    # Language
    # ==================================================================
    def _toggle_language(self):
        # Read the live module value (a plain `from i18n import LANG` would be a
        # stale copy frozen at import time, so toggling could never switch back).
        new_lang = "zh" if i18n.LANG == "en" else "en"
        set_lang(new_lang)
        self.lang_btn.setText(tr("lang_label"))
        self._retranslate()

    def _retranslate(self):
        self.title_label.setText(tr("app_title"))
        self.subtitle_label.setText(tr("app_subtitle"))
        self.stepper.set_labels([tr("step_connect"), tr("step_configure"), tr("step_deploy")])

        self.conn_section_title.setText(tr("vps_connection").upper())
        self.host_label.setText(tr("host_ip"))
        self.host_input.setPlaceholderText(tr("placeholder_host"))
        self.pu_label.setText(tr("ssh_port") + " / " + tr("username"))
        self.auth_label.setText(tr("auth_method"))
        self.auth_combo.blockSignals(True)
        idx = self.auth_combo.currentIndex()
        self.auth_combo.clear()
        self.auth_combo.addItems([tr("auth_password"), tr("auth_key")])
        self.auth_combo.setCurrentIndex(idx)
        self.auth_combo.blockSignals(False)
        self.pwd_label.setText(tr("password"))
        self.password_input.setPlaceholderText(tr("placeholder_password"))
        self.key_label.setText(tr("ssh_key"))
        self.key_input.setPlaceholderText(tr("placeholder_key"))
        self.key_browse_btn.setText(tr("browse"))
        self.connect_btn.setText(tr("connect"))

        self.wg_section_title.setText(tr("wg_settings").upper())
        self.wg_port_label.setText(tr("listen_port"))
        self.subnet_label.setText(tr("vpn_subnet"))
        self.server_label.setText(tr("server_addr"))
        self.client_addr_label.setText(tr("client_addr"))
        self.dns_label.setText(tr("dns"))
        self.allowed_label.setText(tr("allowed_ips"))
        self.client_section_title.setText(tr("client_section").upper())
        self.client_name_label.setText(tr("client_name"))
        self.output_label.setText(tr("output"))
        self.out_browse_btn.setText(tr("browse"))
        self.deploy_btn.setText(tr("deploy_vpn"))

        self.open_finder_btn.setText(tr("show_finder"))
        self.clear_log_btn.setText(tr("clear_log"))
        self.status_label.setText(tr("status_ready"))
        self.help_btn.setToolTip(tr("help_tooltip"))
        self._set_footer(getattr(self, "_footer_state", self.SSH_UNTESTED))

    # ==================================================================
    # Helpers
    # ==================================================================
    def _log(self, text: str):
        self.log_view.appendPlainText(text)
        sb = self.log_view.verticalScrollBar()
        if sb:
            sb.setValue(sb.maximum())

    def _gather_config(self) -> DeployConfig:
        auth_method = "password" if self.auth_combo.currentIndex() == 0 else "key"
        return DeployConfig(
            host=self.host_input.text(),
            ssh_port=int(self.port_input.text() or "22"),
            ssh_username=self.username_input.text(),
            auth_method=auth_method,
            password=self.password_input.text(),
            ssh_key_path=self.key_input.text(),
            wg_listen_port=int(self.wg_port_input.text() or "51820"),
            client_name=self.client_name_input.text(),
            vpn_subnet=self.subnet_input.text(),
            server_vpn_address=self.server_addr_input.text(),
            client_vpn_address=self.client_addr_input.text(),
            dns=self.dns_input.text(),
            allowed_ips=self.allowed_ips_input.text(),
            output_path=self.output_path_input.text(),
        )

    def _set_buttons_enabled(self, enabled: bool):
        for w in (
            self.connect_btn, self.deploy_btn, self.host_input, self.port_input,
            self.username_input, self.auth_combo, self.password_input,
            self.key_input, self.key_browse_btn, self.wg_port_input,
            self.client_name_input, self.subnet_input, self.server_addr_input,
            self.client_addr_input, self.dns_input, self.allowed_ips_input,
            self.output_path_input,
        ):
            w.setEnabled(enabled)

    def _validate_inputs(self) -> Optional[str]:
        try:
            config = self._gather_config()
        except ValueError as e:
            return str(e)
        errors = config.validate()
        return errors[0] if errors else None

    # ==================================================================
    # Slots
    # ==================================================================
    def _on_auth_changed(self, index: int):
        is_password = index == 0
        self.password_input.setVisible(is_password)
        self.pwd_label.setVisible(is_password)
        self.key_input.setVisible(not is_password)
        self.key_browse_btn.setVisible(not is_password)
        self.key_label.setVisible(not is_password)

    def _browse_key(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr("dlg_select_key"), os.path.expanduser("~/.ssh"), tr("dlg_all_files"))
        if path:
            self.key_input.setText(path)

    def _browse_output(self):
        path, _ = QFileDialog.getSaveFileName(
            self, tr("dlg_save_config"),
            os.path.join(os.path.expanduser("~"), "Desktop",
                         f"{self.client_name_input.text() or 'client'}-wireguard.conf"),
            tr("dlg_wg_conf"))
        if path:
            self.output_path_input.setText(path)

    def _update_output_path(self, name: str):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        self.output_path_input.setText(os.path.join(desktop, f"{name or 'client'}-wireguard.conf"))

    def _on_connect(self):
        error = self._validate_inputs()
        if error:
            self._log(f"{tr('log_error_prefix')}{error}")
            self.status_label.setText(tr("status_validation_failed"))
            self._flash_card_error()
            return
        self._log(tr("log_ssh_test"))
        self._set_buttons_enabled(False)
        self._connect_btn_idle()
        self.connect_btn.setText(tr("connecting"))
        self._set_ssh_state(self.SSH_BUSY, tr("status_connecting"))
        self.status_label.setText(tr("status_connecting"))
        config = self._gather_config()
        self._worker = SSHTestWorker(config, self)
        self._worker.finished_signal.connect(self._on_connect_finished)
        self._worker.start()

    def _on_connect_finished(self, success: bool, message: str):
        self._set_buttons_enabled(True)
        if success:
            self._log(message)
            self._set_ssh_state(self.SSH_SUCCESS, tr("status_connected"))
            self._connect_btn_success()
            self.status_label.setText(tr("status_connected"))
            # step 1 complete — unlock Configure, then glide into it
            self.stepper.set_max_enabled(self.STEP_CONFIGURE)
            QTimer.singleShot(850, self._advance_to_configure)
        else:
            self._log(f"{tr('log_error_prefix')}{message}")
            self._set_ssh_state(self.SSH_FAILURE, tr("connect_failed"))
            self._connect_btn_failed()
            self._flash_card_error()
            self.status_label.setText(tr("status_ssh_fail"))
            QTimer.singleShot(1600, self._connect_btn_idle)
        self._worker = None

    def _advance_to_configure(self):
        self._navigate(self.STEP_CONFIGURE)
        # leave the button clean for any return visit
        QTimer.singleShot(400, self._connect_btn_idle)

    def _on_deploy(self):
        error = self._validate_inputs()
        if error:
            self._log(f"{tr('log_error_prefix')}{error}")
            self.status_label.setText(tr("status_validation_failed"))
            return
        self._log(tr("log_separator"))
        self._log(tr("log_deploy_start"))
        self._log(tr("log_separator"))
        self._set_buttons_enabled(False)
        self.open_finder_btn.setEnabled(False)
        self.status_label.setText(tr("status_deploying"))
        self.stepper.set_max_enabled(self.STEP_DEPLOY)   # unlock Deploy
        self._navigate(self.STEP_DEPLOY)
        config = self._gather_config()
        self._worker = DeployWorker(config, self)
        self._worker.log_signal.connect(self._log)
        self._worker.finished_signal.connect(self._on_deploy_finished)
        self._worker.start()

    def _on_deploy_finished(self, success: bool, message: str, output_path: str):
        self._set_buttons_enabled(True)
        if success:
            self._last_output_path = output_path
            self.open_finder_btn.setEnabled(True)
            self.status_label.setText(tr("status_deploy_ok"))
        else:
            self._log(f"{tr('log_error_prefix')}{message}")
            self._log("")
            self._log(tr("log_troubleshooting"))
            self.status_label.setText(tr("status_deploy_fail"))
        self._worker = None

    def _on_open_finder(self):
        if self._last_output_path and os.path.exists(self._last_output_path):
            _reveal_in_file_manager(self._last_output_path)
        else:
            self._log(tr("log_file_missing"))

    def _on_clear_log(self):
        self.log_view.clear()
