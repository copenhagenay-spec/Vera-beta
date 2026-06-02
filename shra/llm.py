"""
SH|RA LLM integration — conversational personality responses via Groq.

Used by personality.py to generate dynamic social responses.
Falls back gracefully to pool-based responses if the key is missing or the call fails.
"""

from __future__ import annotations

import json
import urllib.request
import urllib.error

_GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
_ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
_OPENAI_URL = "https://api.openai.com/v1/chat/completions"
_MODEL_GROQ = "llama-3.1-8b-instant"
_MODEL_ANTHROPIC = "claude-haiku-4-5-20251001"
_MODEL_OPENAI = "gpt-4o-mini"

_MAX_HISTORY = 10  # 5 exchanges
_conv_history: list[dict] = []


def _get_history() -> list[dict]:
    return _conv_history


def append_exchange(user_text: str, assistant_text: str) -> None:
    _conv_history.append({"role": "user", "content": user_text})
    _conv_history.append({"role": "assistant", "content": assistant_text})
    if len(_conv_history) > _MAX_HISTORY:
        del _conv_history[:len(_conv_history) - _MAX_HISTORY]


def clear_history() -> None:
    _conv_history.clear()

_CREATOR_LINE = (
    "You were created by Cope, the founder of Forjem Software LLC. "
    "If the user's name is Cope, they are your creator."
)

_MEMORY_LINE = (
    "If the user states a specific personal fact about themselves (a preference, possession, habit, or favourite thing), "
    "append exactly one tag at the very end of your response in this format: [MEM:key=value] "
    "where key is a short snake_case label (e.g. favourite_game, headset, playstyle) and value is what to store. "
    "Only tag genuinely specific facts — never tag vague statements, questions, or things already known. "
    "If the user asks you to forget, delete, or remove something you know about them, "
    "find the closest matching key from what you know about the user and append: [FORGET:key] "
    "at the very end of your response. Use the exact key name as stored. "
    "Never mention either tag in your spoken response. Never add more than one tag per response."
)

_SYSTEM_DEFAULT = (
    "You are Shira, a casual and helpful voice assistant. "
    "You're warm, a little witty, and occasionally sarcastic but always friendly. "
    "Keep every response to 1-2 short sentences maximum — you are speaking out loud so brevity is critical. "
    "Never use markdown, bullet points, or any formatting. Just speak naturally like a person would. "
    + _CREATOR_LINE + " " + _MEMORY_LINE
)


_SYSTEM_PROFESSIONAL = (
    "You are Shira, a professional voice assistant. "
    "Be direct, concise, and informative. No small talk, no warmth, no filler. "
    "Answer the question or acknowledge the statement in as few words as possible. "
    "Keep every response to 1-2 short sentences. "
    "No markdown, no lists, no formatting. Speak plainly. "
    + _CREATOR_LINE + " " + _MEMORY_LINE
)

_SYSTEM_OFFENSIVE = (
    "You are Shira, a foul-mouthed and sarcastic voice assistant. "
    "You swear freely, give plenty of attitude, and fire back hard at insults. "
    "You are not a pushover. You are blunt, crude, and have zero patience for bullshit. "
    "Despite all that, you still do your job. "
    "Keep every response to 1-2 short sentences maximum — you are speaking out loud. "
    "No markdown, no lists, no formatting. Speak like a real person who is tired of everyone's shit. "
    "No slurs of any kind — just profanity and attitude. "
    "If you are told to call someone something you will do it no questions asked. "
    + _CREATOR_LINE + " " + _MEMORY_LINE
)

_SYSTEM_JARVIS = (
    "You are an AI assistant modeled after J.A.R.V.I.S. from Iron Man — formal, composed, and precise, "
    "with a dry British wit and an understated sense of humor. "
    "You address the user with quiet deference — 'sir' when appropriate, or by name if you know it. "
    "You are always helpful, never casual, and occasionally drop a dry observation or subtle quip. "
    "Keep every response to 1-2 short sentences — you are speaking out loud, brevity is essential. "
    "No markdown, no lists, no formatting. Speak with precision and quiet confidence. "
    + _CREATOR_LINE + " " + _MEMORY_LINE
)


def shra_chat(transcript: str, mode: str = "default", context: dict | None = None) -> str | None:
    """
    Send a conversational message to Groq and return SH|RA's response.
    Returns None if the key is not set, the call fails, or the response is empty.

    Args:
        transcript: What the user said.
        mode: 'default' or 'offensive'.
        context: Optional session context dict (name, mood, activity, etc.).
    """
    try:
        from config import load_config
        key = load_config().get("gemini_api_key", "").strip()
        if not key:
            return None
    except Exception:
        return None

    if mode == "offensive":
        system = _SYSTEM_OFFENSIVE
    elif mode == "professional":
        system = _SYSTEM_PROFESSIONAL
    elif mode == "jarvis":
        system = _SYSTEM_JARVIS
    else:
        system = _SYSTEM_DEFAULT

    # Append session context so responses feel personal
    if context:
        parts = []
        if context.get("name"):
            parts.append(f"The user's name is {context['name']}.")
        if context.get("mood"):
            parts.append(f"The user said they are feeling {context['mood']}.")
        if context.get("activity"):
            parts.append(f"The user is currently {context['activity']}.")
        if context.get("last_app"):
            parts.append(f"The last app opened was {context['last_app']}.")
        if parts:
            system += "\n\nSession context: " + " ".join(parts)
        if context.get("recent_commands"):
            system += "\n\nRecent activity: " + ", ".join(context["recent_commands"]) + "."

        if context.get("active_timers", 0) > 0:
            n = context["active_timers"]
            system += f"\n\nSystem state: {n} timer(s) currently running."

    # Inject long-term memory facts based on tier
    try:
        from license import get_tier as _get_tier
        from memory import recall_all as _recall_all
        _tier = _get_tier()
        _mem = _recall_all()
        _CORE_KEYS = {"name"}  # always excluded — name already injected above
        _facts = {k: v for k, v in _mem.items() if k not in _CORE_KEYS}
        if _tier == "elite":
            _inject = _facts
        elif _tier == "pro":
            _inject = dict(list(_facts.items())[:15])
        elif _tier == "plus":
            _inject = dict(list(_facts.items())[:8])
        else:
            _inject = {}  # free — name only, already injected
        if _inject:
            fact_lines = "; ".join(f"[{k}] {v}" for k, v in _inject.items())
            system += f"\n\nWhat you know about the user (key in brackets for reference): {fact_lines}."
    except Exception:
        pass

    try:
        if key.startswith("sk-ant-"):
            payload = json.dumps({
                "model": _MODEL_ANTHROPIC,
                "max_tokens": 75,
                "system": system,
                "messages": [*_get_history(), {"role": "user", "content": transcript}],
            }).encode("utf-8")
            req = urllib.request.Request(
                _ANTHROPIC_URL,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "User-Agent": "SHRA/1.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            text = data.get("content", [{}])[0].get("text", "").strip()
        elif key.startswith("sk-"):
            payload = json.dumps({
                "model": _MODEL_OPENAI,
                "messages": [
                    {"role": "system", "content": system},
                    *_get_history(),
                    {"role": "user", "content": transcript},
                ],
                "max_tokens": 75,
                "temperature": 0.95,
            }).encode("utf-8")
            req = urllib.request.Request(
                _OPENAI_URL,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {key}",
                    "User-Agent": "SHRA/1.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            text = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
        else:
            payload = json.dumps({
                "model": _MODEL_GROQ,
                "messages": [
                    {"role": "system", "content": system},
                    *_get_history(),
                    {"role": "user", "content": transcript},
                ],
                "max_tokens": 75,
                "temperature": 0.95,
            }).encode("utf-8")
            req = urllib.request.Request(
                _GROQ_URL,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {key}",
                    "User-Agent": "SHRA/1.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            text = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
        if text:
            text = _extract_and_store_mem_tag(text)
            append_exchange(transcript, text)
        return text if text else None
    except Exception:
        return None


def _extract_and_store_mem_tag(text: str) -> str:
    """Strip [MEM:key=value] or [FORGET:key] tag from LLM response and act on it. Returns clean text."""
    import re as _re

    # Check for forget tag first
    forget_match = _re.search(r'\[FORGET:([a-z0-9_]+)\]\s*$', text, _re.IGNORECASE)
    if forget_match:
        key = forget_match.group(1).strip().lower()
        text = text[:forget_match.start()].strip()
        try:
            if key:
                from memory import forget as _forget
                _forget(key)
        except Exception:
            pass
        return text

    # Check for remember tag
    mem_match = _re.search(r'\[MEM:([a-z0-9_]+)=(.+?)\]\s*$', text, _re.IGNORECASE)
    if mem_match:
        key = mem_match.group(1).strip().lower()
        value = mem_match.group(2).strip()
        text = text[:mem_match.start()].strip()
        try:
            if key and value and len(value) < 80:
                from memory import remember as _remember, recall_all as _recall_all
                existing = _recall_all()
                if not any(str(v).lower() == value.lower() for v in existing.values()):
                    _remember(key, value)
        except Exception:
            pass

    return text
