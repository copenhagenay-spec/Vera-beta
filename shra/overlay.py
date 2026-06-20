"""SH|RA Overlay System — draggable, pinnable widget cards."""

from __future__ import annotations

from collections import deque
from typing import Callable

from PySide6.QtWidgets import (
    QWidget, QApplication, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QPushButton, QStyleFactory,
)
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QFont, QFontMetrics

_FUSION = QStyleFactory.create("Fusion")

_MAX_EXCHANGES = 3
_CARD_WIDTH    = 440
_TEXT_W        = _CARD_WIDTH - 28

POSITION_CHOICES = [
    "Top Left", "Top Center", "Top Right",
    "Bottom Left", "Bottom Center", "Bottom Right",
]

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

_CONTAINER_STYLE_TPL = """
    QWidget#overlay_container {{
        background-color: rgba(16, 16, 16, 230);
        border-radius: 8px;
        border-top: 2px solid {accent};
    }}
"""
_HEADER_STYLE       = "background: rgba(25,25,25,230); border-radius: 6px 6px 0 0; border-bottom: 1px solid #2a2a2a;"
_HEADER_LBL_STYLE   = "color: #555555; font-size: 10px; letter-spacing: 2px; background: transparent;"
_PIN_ACTIVE_STYLE   = (
    "QPushButton{color:#1a1a1a;background:#c9a84c;border:none;border-radius:3px;"
    "font-size:11px;font-weight:bold;padding:1px 6px;}"
    "QPushButton:hover{background:#e8c96a;}"
)
_PIN_INACTIVE_STYLE = (
    "QPushButton{color:#555555;background:transparent;border:1px solid #383838;"
    "border-radius:3px;font-size:11px;padding:1px 6px;}"
    "QPushButton:hover{color:#888888;border-color:#555555;}"
)
_CLOSE_BTN_STYLE    = (
    "QPushButton{color:#505050;background:transparent;border:none;font-size:11px;padding:0 4px;}"
    "QPushButton:hover{color:#cc4444;}"
)

_WEATHER1_STYLE     = "color: #facc15; font-size: 13px; font-weight: bold; background: transparent;"
_WEATHER2_STYLE     = "color: #c9a20a; font-size: 11px; background: transparent;"
_SEP_STYLE          = "background: #2a2a2a; border: none;"
_YOU_CURRENT_STYLE  = "color: #ffffff; font-size: 13px; background: transparent;"
_SHRA_CURRENT_STYLE = "color: #60a5fa; font-size: 13px; background: transparent;"
_YOU_OLD_STYLE      = "color: #787878; font-size: 13px; background: transparent;"
_SHRA_OLD_STYLE     = "color: #4174af; font-size: 13px; background: transparent;"
_STAT_LBL_STYLE     = "color: #c9a84c; font-size: 12px; font-family: 'Segoe UI'; background: transparent;"
_STAT_TITLE_STYLE   = "color: #444444; font-size: 10px; letter-spacing: 2px; background: transparent;"

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
# Exchange row (used by TranscriptCard)
# ---------------------------------------------------------------------------

class _ExchangeRow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 2)
        layout.setSpacing(2)
        self.you  = _lbl(_YOU_CURRENT_STYLE)
        self.shra = _lbl(_SHRA_CURRENT_STYLE)
        layout.addWidget(self.you)
        layout.addWidget(self.shra)
        self.setVisible(False)

    def populate(self, you_text: str, shra_text: str, is_current: bool) -> None:
        self.you.setStyleSheet(_YOU_CURRENT_STYLE  if is_current else _YOU_OLD_STYLE)
        self.you.setText(_elide(f"You: {you_text}"))
        self.you.setVisible(True)
        if shra_text:
            self.shra.setStyleSheet(_SHRA_CURRENT_STYLE if is_current else _SHRA_OLD_STYLE)
            self.shra.setText(_elide(f"SH|RA: {shra_text}"))
            self.shra.setVisible(True)
        else:
            self.shra.setVisible(False)
        self.setVisible(True)

    def clear(self) -> None:
        self.you.setVisible(False)
        self.shra.setVisible(False)
        self.setVisible(False)


# ---------------------------------------------------------------------------
# Base card — draggable, pinnable
# ---------------------------------------------------------------------------

class _OverlayCard(QWidget):
    """Base class for all overlay cards. Each card is its own window."""

    card_name:        str  = "base"
    card_title:       str  = "Widget"
    card_accent:      str  = "#333333"
    always_interactive: bool = False  # if True, never click-through even in display mode

    def __init__(self, width: int = _CARD_WIDTH):
        super().__init__(None)
        self._pinned:    bool           = False
        self._edit_mode: bool           = False
        self._drag_pos:  QPoint | None  = None
        self._save_cb:   Callable | None = None

        self._apply_flags(click_through=True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedWidth(width)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Edit-mode header: drag handle + title + pin + close
        self._header = QWidget()
        self._header.setStyleSheet(_HEADER_STYLE)
        self._header.setFixedHeight(28)
        self._header.setVisible(False)
        hl = QHBoxLayout(self._header)
        hl.setContentsMargins(10, 0, 6, 0)
        hl.setSpacing(4)
        title_lbl = QLabel(self.card_title.upper())
        title_lbl.setStyleSheet(_HEADER_LBL_STYLE)
        hl.addWidget(title_lbl)
        hl.addStretch()
        self._pin_btn = QPushButton("PIN")
        self._pin_btn.setFixedHeight(20)
        self._pin_btn.setStyleSheet(_PIN_INACTIVE_STYLE)
        self._pin_btn.setToolTip("Pin — stays visible when overlay is hidden")
        self._pin_btn.clicked.connect(self._toggle_pin)
        hl.addWidget(self._pin_btn)
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 24)
        close_btn.setStyleSheet(_CLOSE_BTN_STYLE)
        close_btn.clicked.connect(self.hide)
        hl.addWidget(close_btn)
        root.addWidget(self._header)

        # Card container
        self._container = QWidget()
        self._container.setObjectName("overlay_container")
        self._container.setStyleSheet(_CONTAINER_STYLE_TPL.format(accent=self.card_accent))
        root.addWidget(self._container)

        self._inner = QVBoxLayout(self._container)
        self._inner.setContentsMargins(14, 12, 14, 12)
        self._inner.setSpacing(0)

        self._build_content(self._inner)

    def _build_content(self, layout: QVBoxLayout) -> None:
        """Override to populate card content."""

    # ------------------------------------------------------------------
    # Edit mode

    def set_edit_mode(self, edit: bool) -> None:
        was_visible = self.isVisible()
        self._edit_mode = edit
        self._header.setVisible(edit)
        self._apply_flags(click_through=not edit)
        if was_visible or edit:
            super().show()

    def _apply_flags(self, click_through: bool) -> None:
        flags = (
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        if click_through and not self.always_interactive:
            flags |= Qt.WindowType.WindowTransparentForInput
        self.setWindowFlags(flags)

    # ------------------------------------------------------------------
    # Pin

    def _toggle_pin(self) -> None:
        self._pinned = not self._pinned
        self._pin_btn.setText("PINNED" if self._pinned else "PIN")
        self._pin_btn.setStyleSheet(_PIN_ACTIVE_STYLE if self._pinned else _PIN_INACTIVE_STYLE)
        if self._save_cb:
            self._save_cb()

    def is_pinned(self) -> bool:
        return self._pinned

    def set_pinned(self, pinned: bool) -> None:
        self._pinned = pinned
        self._pin_btn.setText("PINNED" if pinned else "PIN")
        self._pin_btn.setStyleSheet(_PIN_ACTIVE_STYLE if pinned else _PIN_INACTIVE_STYLE)

    # ------------------------------------------------------------------
    # Drag

    def mousePressEvent(self, event) -> None:
        if self._edit_mode and event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event) -> None:
        if self._edit_mode and self._drag_pos is not None:
            if event.buttons() & Qt.MouseButton.LeftButton:
                self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event) -> None:
        self._drag_pos = None
        if self._edit_mode and self._save_cb:
            self._save_cb()

    # ------------------------------------------------------------------
    # Position helpers

    def place_at(self, position: str) -> None:
        self.adjustSize()
        screen = QApplication.primaryScreen().availableGeometry()
        x, y = _calc_pos(position, screen.width(), screen.height(), self.width(), self.height())
        self.move(x, y)

    def get_state(self) -> dict:
        return {"x": self.x(), "y": self.y(), "pinned": self._pinned}

    def load_state(self, state: dict) -> None:
        if "x" in state and "y" in state:
            self.move(state["x"], state["y"])
        self.set_pinned(state.get("pinned", False))


# ---------------------------------------------------------------------------
# Transcript card
# ---------------------------------------------------------------------------

class TranscriptCard(_OverlayCard):
    card_name   = "transcript"
    card_title  = "Transcript"
    card_accent = "#60a5fa"

    def __init__(self):
        self._history:       deque         = deque(maxlen=_MAX_EXCHANGES - 1)
        self._current_you:   str           = ""
        self._current_shra:  str           = ""
        self._has_current:   bool          = False
        self._weather:       str           = ""
        super().__init__(width=_CARD_WIDTH)

    def _build_content(self, layout: QVBoxLayout) -> None:
        # Weather
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
        layout.addWidget(self._weather_widget)

        # Separator
        self._sep = QFrame()
        self._sep.setFrameShape(QFrame.Shape.HLine)
        self._sep.setFixedHeight(1)
        self._sep.setStyleSheet(_SEP_STYLE)
        self._sep.setVisible(False)
        layout.addSpacing(6)
        layout.addWidget(self._sep)
        layout.addSpacing(6)

        # Exchange rows
        self._rows: list[_ExchangeRow] = []
        for i in range(_MAX_EXCHANGES):
            row = _ExchangeRow()
            if i > 0:
                layout.addSpacing(6)
            layout.addWidget(row)
            self._rows.append(row)

    def push_you(self, text: str) -> None:
        if self._has_current:
            self._history.append((self._current_you, self._current_shra))
        self._current_you  = text
        self._current_shra = ""
        self._has_current  = True
        self._refresh()

    def push_shra(self, text: str) -> None:
        if not self._has_current:
            return
        self._current_shra = (self._current_shra + "  " + text) if self._current_shra else text
        self._refresh()

    def set_weather(self, text: str) -> None:
        self._weather = text
        self._refresh()

    def _refresh(self) -> None:
        if self._weather:
            parts = self._weather.split("\n", 1)
            self._w1.setText(_elide(parts[0], 13))
            self._w2.setText(_elide(parts[1], 11) if len(parts) > 1 else "")
            self._w2.setVisible(len(parts) > 1)
            self._weather_widget.setVisible(True)
        else:
            self._weather_widget.setVisible(False)

        exchanges = self._all_exchanges()
        self._sep.setVisible(bool(self._weather) and bool(exchanges))

        for row in self._rows:
            row.clear()
        for i, (you, shra, is_current) in enumerate(exchanges):
            self._rows[i].populate(you, shra, is_current)

        self.adjustSize()

    def _all_exchanges(self) -> list[tuple[str, str, bool]]:
        result = [(y, v, False) for y, v in self._history]
        if self._has_current:
            result.append((self._current_you, self._current_shra, True))
        return result


# ---------------------------------------------------------------------------
# Status card — CPU / RAM
# ---------------------------------------------------------------------------

class StatusCard(_OverlayCard):
    card_name   = "status"
    card_title  = "System"
    card_accent = "#c9a84c"

    def __init__(self):
        super().__init__(width=200)
        self._timer = QTimer(self)
        self._timer.setInterval(2000)
        self._timer.timeout.connect(self._update_stats)

    def _build_content(self, layout: QVBoxLayout) -> None:
        self._cpu_lbl = QLabel("CPU  --")
        self._cpu_lbl.setStyleSheet(_STAT_LBL_STYLE)
        self._ram_lbl = QLabel("RAM  --")
        self._ram_lbl.setStyleSheet(_STAT_LBL_STYLE)
        layout.addWidget(self._cpu_lbl)
        layout.addWidget(self._ram_lbl)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._update_stats()
        self._timer.start()

    def hideEvent(self, event) -> None:
        self._timer.stop()
        super().hideEvent(event)

    def _update_stats(self) -> None:
        try:
            import psutil
            cpu     = psutil.cpu_percent(interval=None)
            vm      = psutil.virtual_memory()
            used_gb = vm.used  / (1024 ** 3)
            tot_gb  = vm.total / (1024 ** 3)
            self._cpu_lbl.setText(f"CPU  {cpu:.0f}%")
            self._ram_lbl.setText(f"RAM  {used_gb:.1f} / {tot_gb:.1f} GB")
        except Exception:
            pass
        self.adjustSize()


# ---------------------------------------------------------------------------
# Timer card
# ---------------------------------------------------------------------------

_TIMER_ROW_STYLE  = "color: #c9a84c; font-size: 13px; font-family: 'Segoe UI'; background: transparent;"
_TIMER_DONE_STYLE = "color: #555555; font-size: 13px; font-family: 'Segoe UI'; background: transparent;"
_TIMER_EMPTY_STYLE = "color: #333333; font-size: 12px; font-family: 'Segoe UI'; background: transparent;"
_MAX_TIMER_ROWS   = 4


class TimerCard(_OverlayCard):
    card_name   = "timer"
    card_title  = "Timers"
    card_accent = "#e05c5c"

    def __init__(self):
        super().__init__(width=200)
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

    def _build_content(self, layout: QVBoxLayout) -> None:
        self._rows: list[QLabel] = []
        self._empty_lbl = QLabel("No active timers")
        self._empty_lbl.setStyleSheet(_TIMER_EMPTY_STYLE)
        layout.addWidget(self._empty_lbl)
        for _ in range(_MAX_TIMER_ROWS):
            lbl = QLabel()
            lbl.setStyleSheet(_TIMER_ROW_STYLE)
            lbl.setVisible(False)
            layout.addWidget(lbl)
            self._rows.append(lbl)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._tick()
        self._timer.start()

    def hideEvent(self, event) -> None:
        self._timer.stop()
        super().hideEvent(event)

    def _tick(self) -> None:
        try:
            from skills import _active_timers
            now = __import__("time").time()
            active = [t for t in list(_active_timers) if not t["event"].is_set()]
        except Exception:
            active = []

        self._empty_lbl.setVisible(not active)
        for i, row in enumerate(self._rows):
            if i < len(active):
                t     = active[i]
                rem   = max(0.0, t["ends_at"] - now)
                label = t["label"] or "Timer"
                mins, secs = divmod(int(rem), 60)
                hrs,  mins = divmod(mins, 60)
                if hrs:
                    ts = f"{hrs}:{mins:02d}:{secs:02d}"
                else:
                    ts = f"{mins}:{secs:02d}"
                row.setText(f"{label}  {ts}")
                if rem <= 0:
                    style = _TIMER_DONE_STYLE
                elif rem <= 30:
                    style = "color: #e05c5c; font-size: 13px; font-family: 'Segoe UI'; background: transparent;"
                else:
                    style = _TIMER_ROW_STYLE
                row.setStyleSheet(style)
                row.setVisible(True)
            else:
                row.setVisible(False)

        self.adjustSize()


# ---------------------------------------------------------------------------
# Now Playing card
# ---------------------------------------------------------------------------

_NP_TRACK_STYLE  = "color: #ffffff; font-size: 13px; font-family: 'Segoe UI'; background: transparent;"
_NP_ARTIST_STYLE = "color: #787878; font-size: 11px; font-family: 'Segoe UI'; background: transparent;"
_NP_IDLE_STYLE   = "color: #333333; font-size: 12px; font-family: 'Segoe UI'; background: transparent;"
_NP_PAUSE_STYLE  = "color: #555555; font-size: 13px; font-family: 'Segoe UI'; background: transparent;"


_NP_BTN_STYLE = (
    "QPushButton{"
    "color:#484848;"
    "background:rgba(255,255,255,6);"
    "border:none;"
    "border-radius:4px;"
    "font-size:14px;"
    "padding:4px 0px;"
    "}"
    "QPushButton:hover{"
    "color:#cccccc;"
    "background:rgba(255,255,255,14);"
    "}"
    "QPushButton:pressed{"
    "color:#1db954;"
    "background:rgba(29,185,84,18);"
    "}"
)


class NowPlayingCard(_OverlayCard):
    card_name        = "now_playing"
    card_title       = "Now Playing"
    card_accent      = "#1db954"
    always_interactive = True

    def __init__(self):
        self._is_playing = False
        super().__init__(width=260)
        self._timer = QTimer(self)
        self._timer.setInterval(5000)
        self._timer.timeout.connect(self._poll)

    def _build_content(self, layout: QVBoxLayout) -> None:
        self._track_lbl = QLabel("Nothing playing")
        self._track_lbl.setStyleSheet(_NP_IDLE_STYLE)
        self._artist_lbl = QLabel()
        self._artist_lbl.setStyleSheet(_NP_ARTIST_STYLE)
        self._artist_lbl.setVisible(False)
        layout.addWidget(self._track_lbl)
        layout.addWidget(self._artist_lbl)

        # Control buttons
        layout.addSpacing(8)
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(6)
        self._prev_btn = QPushButton("◀◀")
        self._play_btn = QPushButton("▌▌")
        self._next_btn = QPushButton("▶▶")
        for btn in (self._prev_btn, self._play_btn, self._next_btn):
            btn.setFlat(True)
            btn.setStyle(_FUSION)
            btn.setStyleSheet(_NP_BTN_STYLE)
            btn.setFixedHeight(28)
            btn_row.addWidget(btn)
        self._prev_btn.clicked.connect(self._on_prev)
        self._play_btn.clicked.connect(self._on_play_pause)
        self._next_btn.clicked.connect(self._on_next)
        layout.addLayout(btn_row)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._poll()
        self._timer.start()

    def hideEvent(self, event) -> None:
        self._timer.stop()
        super().hideEvent(event)

    # ------------------------------------------------------------------
    # Button callbacks — fire on background thread to avoid blocking UI

    def _on_prev(self) -> None:
        import threading
        def _go():
            try:
                from media_session import previous_track
                previous_track()
            except Exception:
                pass
            QTimer.singleShot(600, self._poll)
        threading.Thread(target=_go, daemon=True).start()

    def _on_play_pause(self) -> None:
        import threading
        # Flip state and button label immediately — don't wait for poll
        self._is_playing = not self._is_playing
        self._play_btn.setText("▌▌" if self._is_playing else "▶")
        should_play = self._is_playing  # capture after flip

        def _go():
            try:
                from media_session import pause, play
                if should_play:
                    play()
                else:
                    pause()
            except Exception:
                pass
            QTimer.singleShot(1000, self._poll)  # 1s for the session to settle before syncing
        threading.Thread(target=_go, daemon=True).start()

    def _on_next(self) -> None:
        import threading
        def _go():
            try:
                from media_session import next_track
                next_track()
            except Exception:
                pass
            QTimer.singleShot(600, self._poll)
        threading.Thread(target=_go, daemon=True).start()

    # ------------------------------------------------------------------
    # Poll

    def _poll(self) -> None:
        try:
            from media_session import now_playing_info
            track, artist, playing = now_playing_info()
        except Exception:
            self._track_lbl.setText("Nothing playing")
            self._track_lbl.setStyleSheet(_NP_IDLE_STYLE)
            self._artist_lbl.setVisible(False)
            self._play_btn.setText("▶")  # noqa: keep as play symbol
            self.adjustSize()
            return

        self._is_playing = playing
        self._play_btn.setText("▌▌" if playing else "▶")

        fm_t = QFontMetrics(QFont("Segoe UI", 13))
        fm_a = QFontMetrics(QFont("Segoe UI", 11))
        w    = self.width() - 28

        if track:
            prefix = "▶  " if playing else "▌▌  "
            style  = _NP_TRACK_STYLE if playing else _NP_PAUSE_STYLE
            self._track_lbl.setText(fm_t.elidedText(prefix + track, Qt.TextElideMode.ElideRight, w))
            self._track_lbl.setStyleSheet(style)
            if artist:
                self._artist_lbl.setText(fm_a.elidedText("♪  " + artist, Qt.TextElideMode.ElideRight, w))
                self._artist_lbl.setVisible(True)
            else:
                self._artist_lbl.setVisible(False)
        else:
            self._track_lbl.setText("Nothing playing")
            self._track_lbl.setStyleSheet(_NP_IDLE_STYLE)
            self._artist_lbl.setVisible(False)

        self.adjustSize()


# ---------------------------------------------------------------------------
# Widget manager
# ---------------------------------------------------------------------------

class WidgetManager:
    """Owns all overlay cards. Single point of control for show/hide/edit/gaming."""

    def __init__(
        self,
        save_fn:          Callable[[dict], None],
        initial_states:   dict,
        default_position: str = "Top Left",
    ):
        self._transcript  = TranscriptCard()
        self._status      = StatusCard()
        self._timers      = TimerCard()
        self._now_playing = NowPlayingCard()
        self._cards: list[_OverlayCard] = [self._transcript, self._status, self._timers, self._now_playing]

        self._save_fn    = save_fn
        self._visible    = False
        self._edit_mode  = False
        self._gaming     = False

        for card in self._cards:
            card._save_cb = self._persist

        self._load_states(initial_states, default_position)

    # ------------------------------------------------------------------
    # State persistence

    def _load_states(self, states: dict, default_position: str) -> None:
        t = states.get("transcript", {})
        if "x" in t:
            self._transcript.load_state(t)
        else:
            self._transcript.place_at(default_position)

        s = states.get("status", {})
        if "x" in s:
            self._status.load_state(s)
        else:
            self._status.place_at("Bottom Right")

        ti = states.get("timer", {})
        if "x" in ti:
            self._timers.load_state(ti)
        else:
            self._timers.place_at("Bottom Left")

        np = states.get("now_playing", {})
        if "x" in np:
            self._now_playing.load_state(np)
        else:
            self._now_playing.place_at("Bottom Center")

    def _persist(self) -> None:
        self._save_fn({card.card_name: card.get_state() for card in self._cards})

    # ------------------------------------------------------------------
    # Transcript passthrough

    def push_you(self, text: str) -> None:
        self._transcript.push_you(text)

    def push_shra(self, text: str) -> None:
        self._transcript.push_shra(text)

    def set_weather(self, text: str) -> None:
        self._transcript.set_weather(text)

    def set_position(self, position: str) -> None:
        # Legacy compat — only reposition if no saved coords
        pass

    # ------------------------------------------------------------------
    # Overlay show / hide / toggle

    def show(self) -> None:
        """Show all cards in edit mode — drag, pin, arrange."""
        self._visible = True
        self._transcript._refresh()
        self._edit_mode = True
        for card in self._cards:
            card.set_edit_mode(True)

    def hide(self) -> None:
        """Lock positions, save, and hide unpinned cards. Pinned stay visible."""
        self._visible = False
        self._edit_mode = False
        for card in self._cards:
            card.set_edit_mode(False)
        self._persist()
        for card in self._cards:
            if not card.is_pinned():
                card.hide()

    def toggle(self) -> None:
        if self._visible:
            self.hide()
        else:
            self.show()

    def hotkey_press(self) -> None:
        self.toggle()

    # ------------------------------------------------------------------
    # Gaming mode

    def gaming_mode(self, active: bool) -> None:
        self._gaming = active
        if active:
            for card in self._cards:
                if card.is_pinned():
                    card.show()
                else:
                    card.hide()
        else:
            if self._visible:
                self.show()
            else:
                self.hide()

    # ------------------------------------------------------------------
    # Edit mode (voice command entrypoints — same behaviour as show/hide)

    def enter_edit_mode(self) -> None:
        self.show()

    def exit_edit_mode(self) -> None:
        self.hide()
