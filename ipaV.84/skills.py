"""Simple skills for the standalone assistant."""

from __future__ import annotations

import re
import difflib
import threading
import time
import subprocess
import webbrowser
from urllib.parse import quote_plus

from config import load_config


def _confirm(prompt: str, allow_prompt: bool, confirm_fn=None) -> bool:
    cfg = load_config()
    if not cfg.get("confirm_actions", False):
        return True
    if confirm_fn is not None:
        try:
            return bool(confirm_fn(prompt))
        except Exception:
            return False
    if not allow_prompt:
        # Avoid blocking for input in background threads (hotkey/hold).
        return True
    try:
        reply = input(f"{prompt} [y/N]: ").strip().lower()
    except Exception:
        return False
    return reply in ("y", "yes")


def _run_command(command: str) -> None:
    subprocess.Popen(command, shell=True)

def _start_timer(seconds: int, label: str) -> None:
    def _alarm():
        try:
            time.sleep(seconds)
            try:
                import winsound  # type: ignore
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                winsound.Beep(880, 500)
                winsound.Beep(880, 500)
            except Exception:
                pass
            try:
                import tkinter as tk
                from tkinter import messagebox
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo("IPA Timer", f"Timer done: {label}")
                root.destroy()
            except Exception:
                print(f"Timer done: {label}")
        except Exception:
            pass

    threading.Thread(target=_alarm, daemon=True).start()

_NUM_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
}


def _word_to_num(word: str):
    return _NUM_WORDS.get(word.lower())


def _parse_timer(text: str):
    # Examples: "set timer 5 minutes", "timer 10 sec", "set timer 1 hour"
    m = re.search(r"\b(set\s+a\s+timer|set\s+timer|timer)\s+(\d+|\w+)\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?)?\b", text)
    if not m:
        return None
    raw = m.group(2)
    if raw.isdigit():
        value = int(raw)
    else:
        value = _word_to_num(raw)
        if value is None:
            return None
    unit = (m.group(3) or "seconds").lower()
    if unit.startswith("hour") or unit.startswith("hr"):
        seconds = value * 3600
        label = f"{value} hour(s)"
    elif unit.startswith("min"):
        seconds = value * 60
        label = f"{value} minute(s)"
    else:
        seconds = value
        label = f"{value} second(s)"
    return seconds, label

def _media_key(action: str) -> bool:
    try:
        from pynput import keyboard  # type: ignore
    except Exception:
        print("Missing dependency: pynput (needed for media keys).")
        return False
    keymap = {
        "play_pause": keyboard.Key.media_play_pause,
        "next": keyboard.Key.media_next,
        "previous": keyboard.Key.media_previous,
    }
    key = keymap.get(action)
    if not key:
        return False
    try:
        ctl = keyboard.Controller()
        ctl.press(key)
        ctl.release(key)
        return True
    except Exception as exc:
        print(f"Failed to send media key: {exc}")
        return False


def _normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _get_spotify_keywords(cfg) -> list:
    raw = cfg.get("spotify_keywords")
    if isinstance(raw, list):
        keywords = [str(x).strip().lower() for x in raw if str(x).strip()]
    elif isinstance(raw, str) and raw.strip():
        keywords = [x.strip().lower() for x in raw.split(",") if x.strip()]
    else:
        # Default includes common mis-hears without being too broad.
        keywords = ["spotify", "spot if i", "spot ify", "spotty"]
    return keywords


def _has_keyword(text: str, keywords: list) -> bool:
    if not keywords:
        return False
    text_l = text.lower()
    tokens = [re.sub(r"[^a-z0-9]+", "", t) for t in text_l.split()]
    tokens = [t for t in tokens if t]
    norm_text = _normalize_text(text_l)
    for kw in keywords:
        if not kw:
            continue
        if kw in text_l:
            return True
        norm_kw = _normalize_text(kw)
        if norm_kw and norm_kw in norm_text:
            return True
        if tokens and norm_kw:
            match = difflib.get_close_matches(norm_kw, tokens, n=1, cutoff=0.75)
            if match:
                return True
    return False


def _normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _open_app(app_name: str, allow_prompt: bool, confirm_fn=None) -> bool:
    cfg = load_config()
    apps = cfg.get("apps", {})
    if not isinstance(apps, dict):
        apps = {}

    # Merge aliases into app map
    aliases = cfg.get("app_aliases", {})
    if isinstance(aliases, dict):
        for alias, target in aliases.items():
            if not isinstance(alias, str) or not isinstance(target, str):
                continue
            target_cmd = apps.get(target)
            if target_cmd:
                apps[alias] = target_cmd
    exact = apps.get(app_name)
    if exact:
        command = exact
    else:
        # Try normalized match
        norm_map = {_normalize_name(k): v for k, v in apps.items()}
        target = _normalize_name(app_name)
        command = norm_map.get(target)
        if not command and target:
            # Fuzzy match closest app name
            candidates = list(norm_map.keys())
            match = difflib.get_close_matches(target, candidates, n=1, cutoff=0.6)
            if match:
                command = norm_map.get(match[0])
    if not command:
        return False
    if not _confirm(f"Open app: {app_name}?", allow_prompt, confirm_fn=confirm_fn):
        return True
    try:
        _run_command(command)
    except Exception as exc:
        print(f"Failed to open app '{app_name}': {exc}")
    return True


def _web_search(query: str, allow_prompt: bool, confirm_fn=None) -> bool:
    cfg = load_config()
    template = cfg.get("search_engine", "https://www.google.com/search?q={query}")
    if "{query}" not in template:
        template = "https://www.google.com/search?q={query}"
    url = template.format(query=quote_plus(query))
    if not _confirm(f"Search the web for: {query}?", allow_prompt, confirm_fn=confirm_fn):
        return True
    try:
        webbrowser.open(url)
    except Exception as exc:
        print(f"Failed to open browser: {exc}")
    return True


def handle_transcript(text: str, allow_prompt: bool = True, confirm_fn=None) -> bool:
    """
    Try to match transcript to skills.
    Returns True if a skill handled it.
    """
    t = text.strip().lower()
    if not t:
        return False

    timer = _parse_timer(t)
    if timer:
        seconds, label = timer
        _start_timer(seconds, label)
        return True

    cfg = load_config()
    if cfg.get("spotify_media", False):
        require_spotify = cfg.get("spotify_requires_keyword", True)
        keywords = _get_spotify_keywords(cfg)
        has_spotify = _has_keyword(t, keywords)
        if (not require_spotify) or has_spotify:
            action = None
            if re.search(r"\b(play|pause|resume|stop)(\s+(song|track))?\b", t):
                action = "play_pause"
            elif re.search(r"\b(next|skip)(\s+(song|track))?\b", t):
                action = "next"
            elif re.search(r"\b(previous|back|rewind)(\s+(song|track))?\b", t):
                action = "previous"
            if action:
                ok = _media_key(action)
                if ok:
                    return True

    open_match = re.search(r"\b(open|launch|start)\s+(.+)$", t)
    if open_match:
        app = open_match.group(2).strip()
        return _open_app(app, allow_prompt, confirm_fn=confirm_fn)

    search_match = re.search(r"\b(search|look up|lookup|find)(\s+(for\s+)?(.+))?$", t)
    if search_match:
        query = (search_match.group(4) or "").strip()
        if not query and allow_prompt:
            try:
                query = input("Search for: ").strip()
            except Exception:
                query = ""
        if query:
            return _web_search(query, allow_prompt, confirm_fn=confirm_fn)
        print("No search query provided.")
        return True

    web_match = re.search(r"\b(search the web|web search)\s+(for\s+)?(.+)$", t)
    if web_match:
        query = web_match.group(3).strip()
        return _web_search(query, allow_prompt, confirm_fn=confirm_fn)

    return False
