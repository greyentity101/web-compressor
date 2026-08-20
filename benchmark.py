#!/usr/bin/env python3
"""
Benchmark tracker for WebCompressor Pro.

Records per-run metrics (input size, output size, savings, elapsed time,
asset type, timestamp) and exposes summary statistics.  This is the
"self-improving" memory: the compressor can consult historical runs to
pick the best strategy for a given file pattern.
"""

from __future__ import annotations

import json
import os
import time
from collections import defaultdict
from pathlib import Path
from typing import Any


class Benchmark:
    """Append-only benchmark log with rolling summaries."""

    def __init__(self, log_path: Path | None = None):
        self.log_path = log_path or Path.home() / ".webcompressor" / "benchmark.jsonl"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, record: dict[str, Any]) -> None:
        record["ts"] = time.time()
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")

    def load(self) -> list[dict[str, Any]]:
        if not self.log_path.exists():
            return []
        rows = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return rows

    def summary(self) -> dict[str, Any]:
        rows = self.load()
        if not rows:
            return {"runs": 0}

        by_type: dict[str, list[float]] = defaultdict(list)
        for r in rows:
            by_type[r.get("asset_type", "unknown")].append(r.get("savings_pct", 0.0))

        avg_by_type = {k: round(sum(v) / len(v), 2) for k, v in by_type.items()}
        total_in = sum(r.get("original_size", 0) for r in rows)
        total_out = sum(r.get("compressed_size", 0) for r in rows)
        overall = round((1.0 - total_out / total_in) * 100.0, 2) if total_in else 0.0

        return {
            "runs": len(rows),
            "overall_savings_pct": overall,
            "avg_by_type": avg_by_type,
            "best_run": max(rows, key=lambda r: r.get("savings_pct", 0.0)),
        }

    def suggest_strategy(self, asset_type: str) -> dict[str, Any]:
        """Recommend settings based on historical performance."""
        rows = self.load()
        relevant = [r for r in rows if r.get("asset_type") == asset_type]
        if not relevant:
            return {"aggressive": True, "confidence": "low"}

        avg_savings = sum(r.get("savings_pct", 0.0) for r in relevant) / len(relevant)
        aggressive_runs = [r for r in relevant if r.get("aggressive")]
        safe_runs = [r for r in relevant if not r.get("aggressive")]
        agg_savings = (
            sum(r.get("savings_pct", 0.0) for r in aggressive_runs) / len(aggressive_runs)
            if aggressive_runs
            else 0.0
        )
        safe_savings = (
            sum(r.get("savings_pct", 0.0) for r in safe_runs) / len(safe_runs)
            if safe_runs
            else 0.0
        )

        use_aggressive = agg_savings >= safe_savings
        return {
            "aggressive": use_aggressive,
            "confidence": "high" if len(relevant) >= 10 else "medium",
            "avg_savings_pct": round(avg_savings, 2),
            "aggressive_savings_pct": round(agg_savings, 2),
            "safe_savings_pct": round(safe_savings, 2),
        }
