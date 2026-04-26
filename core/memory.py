"""
core/memory.py
───────────────
Persistent conversational memory for students.

Storage: JSON files in ./memory/<session_id>.json
Each file holds the full chat history list so students can
"pick up where they left off" across browser sessions.

Format:
[
  {"role": "user",      "content": "What is photosynthesis?"},
  {"role": "assistant", "content": "...", "sources": [...]},
  ...
]
"""

from __future__ import annotations

import json
import os
from typing import List, Dict, Any

MEMORY_DIR = "memory"


def _ensure_dir() -> None:
    os.makedirs(MEMORY_DIR, exist_ok=True)


def _path(session_id: str) -> str:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in session_id)
    return os.path.join(MEMORY_DIR, f"{safe}.json")


def load_memory(session_id: str) -> List[Dict[str, Any]]:
    """Load chat history from disk. Returns [] if not found."""
    _ensure_dir()
    fp = _path(session_id)
    if not os.path.exists(fp):
        return []
    try:
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Keep only last 100 messages to avoid bloat
        return data[-100:] if isinstance(data, list) else []
    except Exception:
        return []


def save_memory(session_id: str, history: List[Dict[str, Any]]) -> None:
    """Persist chat history to disk."""
    _ensure_dir()
    fp = _path(session_id)
    try:
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(history[-100:], f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[memory] Could not save: {e}")


def clear_memory(session_id: str) -> None:
    """Delete stored memory for a session."""
    fp = _path(session_id)
    if os.path.exists(fp):
        os.remove(fp)


def list_sessions() -> List[str]:
    """Return all known session IDs."""
    _ensure_dir()
    return [
        f.replace(".json", "")
        for f in os.listdir(MEMORY_DIR)
        if f.endswith(".json")
    ]