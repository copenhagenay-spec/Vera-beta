"""
VERA license validation.
Keys are HMAC-SHA256 signed, format: SHRA-XXXX-XXXX-XXXX-XXXX-XXXX
Blacklist is a public Gist containing SHA256 hashes of revoked raw keys.
"""

from __future__ import annotations
import hashlib
import hmac

# Must match _SECRET in keygen.py
_SECRET = "90cdcbd0d8309447c742baf4cc6ae5a6a1a97d9dfb103707edb0cd7eb90e7ead"

# Public Gist URL — JSON array of SHA256 hashes of revoked raw keys
# e.g. ["e3b0c44298fc1c149afb...", ...]
# Leave empty string to skip blacklist check until Gist is set up
_BLACKLIST_URL = ""

# In-memory cache so is_premium() doesn't re-validate on every call
_validated: bool | None = None


def _fetch_blacklist() -> set[str]:
    if not _BLACKLIST_URL:
        return set()
    try:
        import requests
        resp = requests.get(_BLACKLIST_URL, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                return set(data)
    except Exception:
        pass
    return set()


def _validate_key(key: str) -> bool:
    try:
        clean = key.strip().upper()
        if not clean.startswith("SHRA-"):
            return False
        raw = clean[5:].replace("-", "")
        if len(raw) != 20:
            return False
        payload      = raw[:8]
        sig_provided = raw[8:]
        sig_expected = hmac.new(
            _SECRET.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()[:12].upper()
        if not hmac.compare_digest(sig_provided, sig_expected):
            return False
        # Blacklist check — key hash so the Gist never contains real keys
        key_hash = hashlib.sha256(raw.encode()).hexdigest()
        if key_hash in _fetch_blacklist():
            return False
        return True
    except Exception:
        return False


def validate(force: bool = False) -> bool:
    """Validate the stored license key. Caches result for the session."""
    global _validated
    if _validated is not None and not force:
        return _validated
    try:
        from config import load_config
        key = load_config().get("license_key", "").strip()
        _validated = _validate_key(key) if key else False
    except Exception:
        _validated = False
    return _validated


def is_premium() -> bool:
    """Return True if this install has a valid premium license key."""
    return validate()
