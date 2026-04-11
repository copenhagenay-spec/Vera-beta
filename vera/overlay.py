"""VERA Game Overlay — transparent always-on-top transcript/response display."""

from __future__ import annotations

from collections import deque

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QFont, QFontMetrics

_MAX_EXCHANGES = 3
_WIDTH = 440
_PADDING = 14
_LINE_GAP = 3
_EXCHANGE_GAP = 10
_FONT_SIZE = 13

_BG          = QColor(12, 12, 12, 220)
_YOU_CURRENT = QColor(255, 255, 255)
_VER_CURRENT = QColor(96, 165, 250)   # blue
_YOU_OLD     = QColor(150, 150, 150)
_VER_OLD     = QColor(65, 110, 175)

POSITION_CHOICES = [
    "Top Left",
    "Top Center",
    "Top Right",
    "Bottom Left",
    "Bottom Center",
    "Bottom Right",
]

def _calc_pos(position: str, sw: int, sh: int, w: int, h: int) -> tuple[int, int]:
    margin = 20
    if position == "Top Left":
        return margin, margin
    if position == "Top Center":
        return (sw - w) // 2, margin
    if position == "Top Right":
        return sw - w - margin, margin
    if position == "Bottom Left":
        return margin, sh - h - margin
    if position == "Bottom Center":
        return (sw - w) // 2, sh - h - margin
    if position == "Bottom Right":
        return sw - w - margin, sh - h - margin
    return margin, margin


class GameOverlay(QWidget):
    """Frameless, always-on-top, click-through overlay showing the last 3 You/VERA exchanges."""

    def __init__(self, position: str = "Top Left"):
        super().__init__(None)
        self._position = position
        self._history: deque[tuple[str, str]] = deque(maxlen=_MAX_EXCHANGES - 1)
        self._current_you: str = ""
        self._current_vera: str = ""
        self._has_current: bool = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedWidth(_WIDTH)
        self._update_size()

    # ------------------------------------------------------------------
    # Public API

    def set_position(self, position: str) -> None:
        self._position = position
        if self.isVisible():
            self._reposition()

    def push_you(self, text: str) -> None:
        """Call when a new transcript arrives. Commits previous exchange to history."""
        if self._has_current:
            self._history.append((self._current_you, self._current_vera))
        self._current_you = text
        self._current_vera = ""
        self._has_current = True
        self._refresh()

    def push_vera(self, text: str) -> None:
        """Call when VERA speaks. Appends to current exchange VERA line."""
        if not self._has_current:
            return
        if self._current_vera:
            self._current_vera += "  " + text
        else:
            self._current_vera = text
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
        screen = QApplication.primaryScreen().availableGeometry()
        x, y = _calc_pos(self._position, screen.width(), screen.height(), self.width(), self.height())
        self.move(x, y)

    def _refresh(self) -> None:
        self._update_size()
        self.update()
        if self.isVisible():
            self._reposition()

    def _all_exchanges(self) -> list[tuple[str, str, bool]]:
        """Returns [(you, vera, is_current), ...] oldest first."""
        result = [(y, v, False) for y, v in self._history]
        if self._has_current:
            result.append((self._current_you, self._current_vera, True))
        return result

    def _update_size(self) -> None:
        font = QFont("Segoe UI", _FONT_SIZE)
        fm = QFontMetrics(font)
        lh = fm.height()
        exchanges = self._all_exchanges()
        total = _PADDING
        for i, (_, vera, _) in enumerate(exchanges):
            if i > 0:
                total += _EXCHANGE_GAP
            total += lh + _LINE_GAP        # You line
            if vera:
                total += lh + _LINE_GAP    # VERA line
        total += _PADDING
        self.setFixedHeight(max(total, 46))

    def paintEvent(self, event) -> None:
        exchanges = self._all_exchanges()
        if not exchanges:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Semi-transparent rounded background
        painter.setBrush(_BG)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)

        font = QFont("Segoe UI", _FONT_SIZE)
        fm = QFontMetrics(font)
        lh = fm.height()
        painter.setFont(font)

        y = _PADDING
        tw = _WIDTH - _PADDING * 2

        for i, (you_text, vera_text, is_current) in enumerate(exchanges):
            if i > 0:
                y += _EXCHANGE_GAP

            you_col  = _YOU_CURRENT if is_current else _YOU_OLD
            vera_col = _VER_CURRENT if is_current else _VER_OLD

            you_label = fm.elidedText(f"You: {you_text}", Qt.TextElideMode.ElideRight, tw)
            painter.setPen(you_col)
            painter.drawText(_PADDING, y, tw, lh, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, you_label)
            y += lh + _LINE_GAP

            if vera_text:
                vera_label = fm.elidedText(f"VERA: {vera_text}", Qt.TextElideMode.ElideRight, tw)
                painter.setPen(vera_col)
                painter.drawText(_PADDING, y, tw, lh, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, vera_label)
                y += lh + _LINE_GAP

        painter.end()
