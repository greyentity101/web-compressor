#!/usr/bin/env python3
"""
File-hash cache for WebCompressor Pro.

Stores compression results keyed by SHA-256 of input content + asset_type +
aggressive flag.  Skips recompression when the cache is warm and the input
has not changed.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional


class CompressionCache:
    """Disk-backed cache with TTL and size limits."""

    def __init__(self, cache_dir: Optional[Path] = None, max_entries: int = 4096):
        self.cache_dir = cache_dir or Path.home() / ".webcompressor" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_entries = max_entries
        self.index_path = self.cache_dir / "index.json"
        self._index: dict[str, dict] = self._load_index()

    def _load_index(self) -> dict[str, dict]:
        if self.index_path.exists():
            try:
                return json.loads(self.index_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save_index(self) -> None:
        self.index_path.write_text(
            json.dumps(self._index, indent=2, sort_keys=True), encoding="utf-8"
        )

    def _key(self, content: str, asset_type: str, aggressive: bool) -> str:
        raw = f"{asset_type}:{aggressive}:{content}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, content: str, asset_type: str, aggressive: bool) -> Optional[dict]:
        key = self._key(content, asset_type, aggressive)
        entry = self._index.get(key)
        if entry is None:
            return None
        if time.time() - entry.get("ts", 0) > 86400:
            self._index.pop(key, None)
            return None
        return entry.get("result")

    def put(self, content: str, asset_type: str, aggressive: bool, result: dict) -> None:
        key = self._key(content, asset_type, aggressive)
        self._index[key] = {"ts": time.time(), "result": result}
        self._prune()
        self._save_index()

    def _prune(self) -> None:
        if len(self._index) <= self.max_entries:
            return
        sorted_keys = sorted(self._index, key=lambda k: self._index[k].get("ts", 0))
        for old_key in sorted_keys[: len(sorted_keys) - self.max_entries]:
            self._index.pop(old_key, None)

    def clear(self) -> None:
        self._index = {}
        if self.index_path.exists():
            self.index_path.unlink()
        for p in self.cache_dir.glob("*.bin"):
            p.unlink()

    def stats(self) -> dict:
        return {"entries": len(self._index), "dir": str(self.cache_dir)}
