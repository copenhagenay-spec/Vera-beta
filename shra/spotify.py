"""
SH|RA Spotify integration — OAuth2 auth code flow + playback control.
Tokens are stored in config.json. Refreshes automatically.
"""

from __future__ import annotations
import json
import re
import time
import threading
import urllib.request
import urllib.parse
import urllib.error
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

_CLIENT_ID     = "8021f1380b7f4f60b40a8ce52475fdeb"
_CLIENT_SECRET = "9ef221603f384ee996f458a41b4a66a9"
_REDIRECT_URI  = "http://127.0.0.1:8888/callback"
_SCOPES        = "user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private playlist-read-collaborative"

_TOKEN_KEY         = "spotify_access_token"
_REFRESH_TOKEN_KEY = "spotify_refresh_token"
_EXPIRY_KEY        = "spotify_token_expiry"

_auth_code: list[str | None] = [None]
_auth_error: list[str | None] = [None]


class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            _auth_code[0] = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<html><body><h2>SH|RA: Spotify connected! You can close this tab.</h2></body></html>")
        else:
            _auth_error[0] = params.get("error", ["unknown"])[0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<html><body><h2>SH|RA: Spotify auth failed. Please try again.</h2></body></html>")

    def log_message(self, format, *args):
        pass  # silence server logs


def _run_callback_server(server: HTTPServer):
    server.handle_request()


def _exchange_code(code: str) -> dict | None:
    try:
        import base64
        credentials = base64.b64encode(f"{_CLIENT_ID}:{_CLIENT_SECRET}".encode()).decode()
        data = urllib.parse.urlencode({
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": _REDIRECT_URI,
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://accounts.spotify.com/api/token",
            data=data,
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _refresh_token(refresh_token: str) -> dict | None:
    try:
        import base64
        credentials = base64.b64encode(f"{_CLIENT_ID}:{_CLIENT_SECRET}".encode()).decode()
        data = urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://accounts.spotify.com/api/token",
            data=data,
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _save_tokens(access_token: str, refresh_token: str, expires_in: int) -> None:
    try:
        from config import load_config, save_config
        cfg = load_config()
        cfg[_TOKEN_KEY] = access_token
        cfg[_REFRESH_TOKEN_KEY] = refresh_token
        cfg[_EXPIRY_KEY] = time.time() + expires_in - 60
        save_config(cfg)
    except Exception:
        pass


def clear_tokens() -> None:
    """Remove stored Spotify tokens to force re-authentication."""
    try:
        from config import load_config, save_config
        cfg = load_config()
        cfg.pop(_TOKEN_KEY, None)
        cfg.pop(_REFRESH_TOKEN_KEY, None)
        cfg.pop(_EXPIRY_KEY, None)
        save_config(cfg)
    except Exception:
        pass


def get_valid_token() -> str | None:
    """Return a valid access token, refreshing if needed. Returns None if not authenticated."""
    try:
        from config import load_config, save_config
        cfg = load_config()
        access_token = cfg.get(_TOKEN_KEY, "")
        refresh = cfg.get(_REFRESH_TOKEN_KEY, "")
        expiry = cfg.get(_EXPIRY_KEY, 0)

        if not access_token or not refresh:
            return None

        if time.time() < expiry:
            return access_token

        # Token expired — refresh it
        result = _refresh_token(refresh)
        if not result or "access_token" not in result:
            return None

        new_token = result["access_token"]
        new_refresh = result.get("refresh_token", refresh)
        expires_in = result.get("expires_in", 3600)
        _save_tokens(new_token, new_refresh, expires_in)
        return new_token
    except Exception:
        return None


def authenticate() -> bool:
    """Launch OAuth flow. Opens browser, waits for callback. Returns True on success."""
    _auth_code[0] = None
    _auth_error[0] = None

    try:
        server = HTTPServer(("127.0.0.1", 8888), _CallbackHandler)
    except Exception:
        return False

    thread = threading.Thread(target=_run_callback_server, args=(server,), daemon=True)
    thread.start()

    params = urllib.parse.urlencode({
        "client_id": _CLIENT_ID,
        "response_type": "code",
        "redirect_uri": _REDIRECT_URI,
        "scope": _SCOPES,
    })
    webbrowser.open(f"https://accounts.spotify.com/authorize?{params}")

    thread.join(timeout=120)
    server.server_close()

    if not _auth_code[0]:
        return False

    result = _exchange_code(_auth_code[0])
    if not result or "access_token" not in result:
        return False

    _save_tokens(result["access_token"], result["refresh_token"], result.get("expires_in", 3600))
    return True


def _api(method: str, endpoint: str, body: dict | None = None) -> dict | None:
    """Make an authenticated Spotify API call."""
    token = get_valid_token()
    if not token:
        return None
    try:
        url = f"https://api.spotify.com/v1{endpoint}"
        data = json.dumps(body).encode("utf-8") if body else None
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            method=method,
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            content = resp.read()
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        if e.code == 204:
            return {}
        return None
    except Exception:
        return None


def get_device_id() -> str | None:
    """Return the first available Spotify device ID, or None."""
    try:
        result = _api("GET", "/me/player/devices")
        if not result:
            return None
        devices = result.get("devices", [])
        if not devices:
            return None
        # Prefer active device, fall back to first available
        for d in devices:
            if d.get("is_active"):
                return d["id"]
        return devices[0]["id"]
    except Exception:
        return None


def _get_user_playlists(token: str) -> list:
    """Fetch all of the user's playlists (name + uri)."""
    try:
        playlists = []
        url = "https://api.spotify.com/v1/me/playlists?limit=50"
        while url:
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
            for item in data.get("items", []):
                if item and item.get("name") and item.get("uri"):
                    playlists.append({"name": item["name"], "uri": item["uri"]})
            url = data.get("next")
        return playlists
    except Exception:
        return []


def play(query: str = "") -> bool:
    """Search for a track and play it, or resume if no query."""
    token = get_valid_token()
    if not token:
        return False

    device_id = get_device_id()

    if not query:
        endpoint = "/me/player/play"
        if device_id:
            endpoint += f"?device_id={device_id}"
        result = _api("PUT", endpoint)
        return result is not None

    try:
        # Detect if user is asking for a playlist or album
        playlist_keywords = ("playlist", "mix", "list")
        album_keywords = ("album", "record", "ep", "lp")
        is_playlist = any(kw in query.lower() for kw in playlist_keywords)
        is_album = any(kw in query.lower() for kw in album_keywords)
        clean_query = query.lower()
        for kw in list(playlist_keywords) + list(album_keywords) + ["my", "the"]:
            clean_query = re.sub(r'\b' + kw + r'\b', '', clean_query).strip()
        clean_query = ' '.join(clean_query.split())

        if is_playlist:
            # Search user's own playlists first
            user_playlists = _get_user_playlists(token)
            if user_playlists:
                import difflib as _dl
                names = [p["name"].lower() for p in user_playlists]
                matches = _dl.get_close_matches(clean_query.lower(), names, n=1, cutoff=0.4)
                if matches:
                    idx = names.index(matches[0])
                    uri = user_playlists[idx]["uri"]
                    endpoint = "/me/player/play"
                    if device_id:
                        endpoint += f"?device_id={device_id}"
                    result = _api("PUT", endpoint, {"context_uri": uri})
                    return result is not None

        if is_album:
            search_url = f"https://api.spotify.com/v1/search?q={urllib.parse.quote_plus(clean_query)}&type=album&limit=1"
            req = urllib.request.Request(
                search_url,
                headers={"Authorization": f"Bearer {token}"},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
            items = data.get("albums", {}).get("items", [])
            if items:
                uri = items[0]["uri"]
                endpoint = "/me/player/play"
                if device_id:
                    endpoint += f"?device_id={device_id}"
                result = _api("PUT", endpoint, {"context_uri": uri})
                return result is not None

        # Default — search tracks
        search_url = f"https://api.spotify.com/v1/search?q={urllib.parse.quote_plus(query)}&type=track&limit=1"
        req = urllib.request.Request(
            search_url,
            headers={"Authorization": f"Bearer {token}"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        items = data.get("tracks", {}).get("items", [])
        if not items:
            return False
        uri = items[0]["uri"]
        endpoint = "/me/player/play"
        if device_id:
            endpoint += f"?device_id={device_id}"
        result = _api("PUT", endpoint, {"uris": [uri]})
        return result is not None
    except Exception:
        return False


def pause() -> bool:
    device_id = get_device_id()
    endpoint = "/me/player/pause"
    if device_id:
        endpoint += f"?device_id={device_id}"
    return _api("PUT", endpoint) is not None


def next_track() -> bool:
    device_id = get_device_id()
    endpoint = "/me/player/next"
    if device_id:
        endpoint += f"?device_id={device_id}"
    return _api("POST", endpoint) is not None


def previous_track() -> bool:
    device_id = get_device_id()
    endpoint = "/me/player/previous"
    if device_id:
        endpoint += f"?device_id={device_id}"
    return _api("POST", endpoint) is not None


def set_volume(level: int) -> bool:
    level = max(0, min(100, level))
    return _api("PUT", f"/me/player/volume?volume_percent={level}") is not None


def currently_playing() -> str | None:
    """Return 'Track - Artist' string of current track, or None."""
    try:
        result = _api("GET", "/me/player/currently-playing")
        if not result:
            return None
        item = result.get("item")
        if not item:
            return None
        track = item.get("name", "")
        artist = item.get("artists", [{}])[0].get("name", "")
        return f"{track} by {artist}" if track else None
    except Exception:
        return None


def is_authenticated() -> bool:
    return get_valid_token() is not None
