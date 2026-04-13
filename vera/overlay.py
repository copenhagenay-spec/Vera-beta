"""VERA Game Overlay — transparent always-on-top transcript/response display."""

from __future__ import annotations

from collections import deque

from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontMetrics

_MAX_EXCHANGES = 3
_WIDTH         = 440
_TEXT_W        = _WIDTH - 28  # available text width for eliding


# ---------------------------------------------------------------------------
# Widget base — foundation for future pinnable overlay widgets
# ---------------------------------------------------------------------------

class OverlayWidget:
    """Base class for pinnable overlay widgets.

    Subclass this to create a new widget card. Override `refresh()` to update
    display when data changes. The widget system (post-1.0) will manage
    registration, ordering, and pin state automatically.
    """

    name: str = "widget"        # unique identifier, used as config key
    pinned: bool = False        # if True, stays visible when overlay hides exchanges

    def get_widget(self) -> QWidget:
        """Return the QWidget to embed in the overlay container."""
        raise NotImplementedError

    def refresh(self, data: object = None) -> None:
        """Called when the widget's data changes."""

    def serialize(self) -> dict:
        """Return pin state and any config to persist in overlay_widgets."""
        return {"pinned": self.pinned}

POSITION_CHOICES = [
    "Top Left",
    "Top Center",
    "Top Right",
    "Bottom Left",
    "Bottom Center",
    "Bottom Right",
]

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

_CONTAINER_STYLE = """
    QWidget#overlay_container {
        background-color: rgba(12, 12, 12, 220);
        border-radius: 8px;
    }
"""
_WEATHER1_STYLE      = "color: #facc15; font-size: 13px; font-weight: bold; background: transparent;"
_WEATHER2_STYLE      = "color: #c9a20a; font-size: 11px; background: transparent;"
_SEP_STYLE           = "background: #2a2a2a; border: none;"
_YOU_CURRENT_STYLE   = "color: #ffffff; font-size: 13px; background: transparent;"
_VERA_CURRENT_STYLE  = "color: #60a5fa; font-size: 13px; background: transparent;"
_YOU_OLD_STYLE       = "color: #787878; font-size: 13px; background: transparent;"
_VERA_OLD_STYLE      = "color: #4174af; font-size: 13px; background: transparent;"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _calc_pos(position: str, sw: int, sh: int, w: int, h: int) -> tuple[int, int]:
    margin = 20
    if position == "Top Left":      return margin, margin
    if position == "Top Center":    return (sw - w) // 2, margin
    if position == "Top Right":     return sw - w - margin, margin
    if position == "Bottom Left":   return margin, sh - h - margin
    if position == "Bottom Center": return (sw - w) // 2, sh - h - margin
    if position == "Bottom Right":  return sw - w - margin, sh - h - margin
    return margin, margin


def _elide(text: str, size: int = 13) -> str:
    fm = QFontMetrics(QFont("Segoe UI", size))
    return fm.elidedText(text, Qt.TextElideMode.ElideRight, _TEXT_W)


def _lbl(style: str) -> QLabel:
    l = QLabel()
    l.setStyleSheet(style)
    l.setVisible(False)
    return l


# ---------------------------------------------------------------------------
# Exchange row
# ---------------------------------------------------------------------------

class _ExchangeRow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 2)
        layout.setSpacing(2)
        self.you  = _lbl(_YOU_CURRENT_STYLE)
        self.vera = _lbl(_VERA_CURRENT_STYLE)
        layout.addWidget(self.you)
        layout.addWidget(self.vera)
        self.setVisible(False)

    def populate(self, you_text: str, vera_text: str, is_current: bool) -> None:
        you_style  = _YOU_CURRENT_STYLE  if is_current else _YOU_OLD_STYLE
        vera_style = _VERA_CURRENT_STYLE if is_current else _VERA_OLD_STYLE
        self.you.setStyleSheet(you_style)
        self.you.setText(_elide(f"You: {you_text}"))
        self.you.setVisible(True)
        if vera_text:
            self.vera.setStyleSheet(vera_style)
            self.vera.setText(_elide(f"VERA: {vera_text}"))
            self.vera.setVisible(True)
        else:
            self.vera.setVisible(False)
        self.setVisible(True)

    def clear(self) -> None:
        self.you.setVisible(False)
        self.vera.setVisible(False)
        self.setVisible(False)


# ---------------------------------------------------------------------------
# Overlay
# ---------------------------------------------------------------------------

class GameOverlay(QWidget):
    """Frameless, always-on-top, click-through overlay."""

    def __init__(self, position: str = "Top Left"):
        super().__init__(None)
        self._position   = position
        self._history: deque[tuple[str, str]] = deque(maxlen=_MAX_EXCHANGES - 1)
        self._current_you: str  = ""
        self._current_vera: str = ""
        self._has_current: bool = False
        self._weather: str = ""

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedWidth(_WIDTH)

        # Outer layout — zero margin so container fills the window
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Container — dark rounded card
        self._container = QWidget()
        self._container.setObjectName("overlay_container")
        self._container.setStyleSheet(_CONTAINER_STYLE)
        outer.addWidget(self._container)

        inner = QVBoxLayout(self._container)
        inner.setContentsMargins(14, 10, 14, 10)
        inner.setSpacing(0)

        # Weather section
        self._weather_widget = QWidget()
        self._weather_widget.setStyleSheet("background: transparent;")
        wl = QVBoxLayout(self._weather_widget)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(1)
        self._w1 = QLabel()
        self._w1.setStyleSheet(_WEATHER1_STYLE)
        self._w2 = QLabel()
        self._w2.setStyleSheet(_WEATHER2_STYLE)
        wl.addWidget(self._w1)
        wl.addWidget(self._w2)
        self._weather_widget.setVisible(False)
        inner.addWidget(self._weather_widget)

        # Separator
        self._sep = QFrame()
        self._sep.setFrameShape(QFrame.Shape.HLine)
        self._sep.setFixedHeight(1)
        self._sep.setStyleSheet(_SEP_STYLE)
        self._sep.setVisible(False)
        inner.addSpacing(6)
        inner.addWidget(self._sep)
        inner.addSpacing(6)

        # Exchange rows
        self._rows: list[_ExchangeRow] = []
        for i in range(_MAX_EXCHANGES):
            row = _ExchangeRow()
            if i > 0:
                inner.addSpacing(6)
            inner.addWidget(row)
            self._rows.append(row)

    # ------------------------------------------------------------------
    # Public API

    def set_position(self, position: str) -> None:
        self._position = position
        if self.isVisible():
            self._reposition()

    def push_you(self, text: str) -> None:
        if self._has_current:
            self._history.append((self._current_you, self._current_vera))
        self._current_you  = text
        self._current_vera = ""
        self._has_current  = True
        self._refresh()

    def push_vera(self, text: str) -> None:
        if not self._has_current:
            return
        self._current_vera = (self._current_vera + "  " + text) if self._current_vera else text
        self._refresh()

    def set_weather(self, text: str) -> None:
        self._weather = text
        self._refresh()

    def toggle(self) -> None:
        if self.isVisible():
            self.hide()
        else:
            self._refresh()
            super().show()
            self._reposition()

    def show(self) -> None:
        self._refresh()
        super().show()
        self._reposition()

    # ------------------------------------------------------------------
    # Internal

    def _reposition(self) -> None:
        self.adjustSize()
        screen = QApplication.primaryScreen().availableGeometry()
        x, y = _calc_pos(self._position, screen.width(), screen.height(), self.width(), self.height())
        self.move(x, y)

    def _refresh(self) -> None:
        # Weather
        if self._weather:
            parts = self._weather.split("\n", 1)
            self._w1.setText(_elide(parts[0], 13))
            self._w2.setText(_elide(parts[1], 11) if len(parts) > 1 else "")
            self._w2.setVisible(len(parts) > 1)
            self._weather_widget.setVisible(True)
        else:
            self._weather_widget.setVisible(False)

        # Separator — only when both weather and exchanges are present
        exchanges = self._all_exchanges()
        self._sep.setVisible(bool(self._weather) and bool(exchanges))

        # Exchange rows
        for row in self._rows:
            row.clear()
        for i, (you, vera, is_current) in enumerate(exchanges):
            self._rows[i].populate(you, vera, is_current)

        if self.isVisible():
            self._reposition()

    def _all_exchanges(self) -> list[tuple[str, str, bool]]:
        result = [(y, v, False) for y, v in self._history]
        if self._has_current:
            result.append((self._current_you, self._current_vera, True))
        return result
