"""
SH|RA OS-level media session control — Windows SMTC (System Media Transport
Controls) via the winrt bindings. Works with whatever app currently owns the
active media session (Spotify desktop, browser tabs, etc.) with no API keys,
no OAuth, and no dependency on any developer account or subscription tier.
"""

from __future__ import annotations
import asyncio


def _run(coro):
    """Run an async winrt call synchronously from a normal (sync) caller."""
    try:
        return asyncio.run(coro)
    except Exception:
        return None


async def _get_best_session():
    """Return whichever session is actually playing, falling back to Windows'
    single "current" session pointer. Windows' notion of "current" tracks the
    most recently *changed* session, not necessarily the one making sound —
    a session that's been playing continuously with no fresh event can get
    passed over in favor of one that just started, even if it's paused. We
    want whichever app is actually producing audio right now."""
    from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
    mgr = await MediaManager.request_async()
    sessions = list(mgr.get_sessions())
    for s in sessions:
        try:
            playback = s.get_playback_info()
            # GlobalSystemMediaTransportControlsSessionPlaybackStatus: 4 = Playing
            if playback is not None and int(playback.playback_status) == 4:
                return s
        except Exception:
            continue
    if sessions:
        return sessions[0]
    return mgr.get_current_session()


async def _now_playing_async():
    session = await _get_best_session()
    if not session:
        return None, None, False
    info = await session.try_get_media_properties_async()
    playback = session.get_playback_info()
    # GlobalSystemMediaTransportControlsSessionPlaybackStatus: 4 = Playing
    is_playing = playback is not None and int(playback.playback_status) == 4
    title = (info.title or "").strip() or None
    artist = (info.artist or "").strip() or None
    return title, artist, is_playing


def now_playing_info() -> tuple[str | None, str | None, bool]:
    """Return (track_name, artist_name, is_playing) for the active media session."""
    result = _run(_now_playing_async())
    if result is None:
        return None, None, False
    return result


def is_session_active() -> bool:
    """True if any app currently has an active media session."""
    session = _run(_get_best_session())
    return session is not None


async def _control_async(method_name: str) -> bool:
    session = await _get_best_session()
    if not session:
        return False
    method = getattr(session, method_name, None)
    if not method:
        return False
    return bool(await method())


def play() -> bool:
    return bool(_run(_control_async("try_play_async")))


def pause() -> bool:
    return bool(_run(_control_async("try_pause_async")))


def next_track() -> bool:
    return bool(_run(_control_async("try_skip_next_async")))


def previous_track() -> bool:
    return bool(_run(_control_async("try_skip_previous_async")))
