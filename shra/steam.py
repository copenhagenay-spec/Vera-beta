"""Steam library and Start Menu app detection helpers."""

from __future__ import annotations

import glob
import os
import re
from typing import Dict, List


def _default_steam_roots() -> List[str]:
    roots = []
    pf86 = os.environ.get("PROGRAMFILES(X86)")
    pf = os.environ.get("PROGRAMFILES")
    if pf86:
        roots.append(os.path.join(pf86, "Steam"))
    if pf:
        roots.append(os.path.join(pf, "Steam"))
    return roots


def _parse_libraryfolders(path: str) -> List[str]:
    if not os.path.exists(path):
        return []
    try:
        text = open(path, "r", encoding="utf-8", errors="ignore").read()
    except Exception:
        return []
    paths = []
    for match in re.finditer(r'"path"\s+"([^"]+)"', text):
        p = match.group(1).replace("\\\\", "\\")
        paths.append(p)
    return paths


def _parse_appmanifest(path: str) -> Dict[str, str]:
    try:
        text = open(path, "r", encoding="utf-8", errors="ignore").read()
    except Exception:
        return {}
    appid_match = re.search(r'"appid"\s+"(\d+)"', text)
    name_match = re.search(r'"name"\s+"([^"]+)"', text)
    if not appid_match or not name_match:
        return {}
    return {"appid": appid_match.group(1), "name": name_match.group(1)}


def find_steam_apps() -> List[Dict[str, str]]:
    libs = []
    for root in _default_steam_roots():
        libfile = os.path.join(root, "steamapps", "libraryfolders.vdf")
        if os.path.exists(libfile):
            libs.append(root)
            libs.extend(_parse_libraryfolders(libfile))

    # Deduplicate
    libs = [p for p in dict.fromkeys(libs) if p]

    apps: List[Dict[str, str]] = []
    for lib in libs:
        steamapps = os.path.join(lib, "steamapps")
        for manifest in glob.glob(os.path.join(steamapps, "appmanifest_*.acf")):
            data = _parse_appmanifest(manifest)
            if data:
                apps.append(data)

    # Deduplicate by appid
    by_id = {}
    for app in apps:
        by_id[app["appid"]] = app
    return list(by_id.values())


_STARTMENU_SKIP = {
    # Uninstallers / setup
    "uninstall", "uninst", "setup", "repair", "migrate",
    # Docs / info
    "help", "readme", "release notes", "changelog", "documentation",
    "manual", "tutorial", "license", "terms", "module docs",
    # Support / web
    "support", "website",
    # Crash / diagnostics
    "crash reporter", "bug report", "error report", "diagnostics",
    # Noisy Windows system entries
    "recycle bin", "memory", "administrative tools", "idle",
    "dfrgui", "recoverydrive", "character map", "iscsi initiator",
    "odbc data sources", "security configuration", "component services",
    "steps recorder", "windows powershell ise",
    # Windows Accessibility folder
    "livecaptions", "magnify", "narrator", "on-screen keyboard", "voiceaccess",
    # Python tooling
    "python 3.", "module docs",
    # Vera (stale installs)
    "vera",
    # Dangerous system admin tools
    "computer management", "disk cleanup", "event viewer", "performance monitor",
    "print management", "registry editor", "resource monitor", "services",
    "system configuration", "system information", "task scheduler",
    "defender firewall", "firmware update",
    # Noisy dev duplicates
    "git cmd",
}


_NAME_PREFIXES = ["microsoft ", "windows "]
_NAME_SUFFIXES = [" browser", " launcher", " client", " app", " (x86)", " (64-bit)", " (32-bit)"]


def _normalize_startmenu_name(name: str) -> str:
    for prefix in _NAME_PREFIXES:
        if name.startswith(prefix):
            name = name[len(prefix):]
    for suffix in _NAME_SUFFIXES:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    return name.strip()


def find_startmenu_apps() -> List[Dict[str, str]]:
    from config import _WELL_KNOWN_APPS
    well_known = set(_WELL_KNOWN_APPS.keys())

    appdata = os.environ.get("APPDATA", "")
    programdata = os.environ.get("PROGRAMDATA", "")
    roots = [
        os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs"),
        os.path.join(programdata, "Microsoft", "Windows", "Start Menu", "Programs"),
    ]

    apps: List[Dict[str, str]] = []
    seen_names: set = set()

    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, _, filenames in os.walk(root):
            if "administrative tools" in dirpath.lower():
                continue
            for filename in filenames:
                if not filename.lower().endswith(".lnk"):
                    continue
                raw_name = filename[:-4].strip().lower()
                if any(skip in raw_name for skip in _STARTMENU_SKIP):
                    continue
                name = _normalize_startmenu_name(raw_name)
                if name in well_known or name in seen_names:
                    continue
                seen_names.add(name)
                lnk_path = os.path.join(dirpath, filename)
                apps.append({"name": name, "command": f'start "" "{lnk_path}"'})

    return apps
