#!/usr/bin/env python3
"""
WebCompressor Pro — Advanced web asset compaction engine.
Semantic-aware, token-safe multi-pass optimization for JavaScript, CSS, and HTML.

Author: Mohit Kumar
License: MIT
"""

import os
import sys
import re
import argparse
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class AssetType(Enum):
    JS = "javascript"
    CSS = "css"
    HTML = "html"
    UNKNOWN = "unknown"


@dataclass
class CompressionResult:
    original_size: int
    compressed_size: int
    ratio: float
    savings_pct: float
    asset_type: AssetType
    elapsed_ms: float
    warnings: List[str] = field(default_factory=list)
    output: str = ""
    _cached: bool = False


class BaseCompressor:
    """Base compressor with shared utilities."""

    def __init__(self, aggressive: bool = True):
        self.aggressive = aggressive
        self.warnings: List[str] = []

    def compress(self, content: str) -> Tuple[str, List[str]]:
        raise NotImplementedError

    def detect_type(self, content: str, filename: Optional[str] = None) -> AssetType:
        if filename:
            ext = Path(filename).suffix.lower()
            if ext in (".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"):
                return AssetType.JS
            elif ext in (".css", ".scss", ".sass", ".less"):
                return AssetType.CSS
            elif ext in (".html", ".htm", ".xhtml", ".shtml"):
                return AssetType.HTML

        stripped = content.strip()
        if stripped.startswith("<!DOCTYPE") or "<html" in stripped[:1000].lower():
            return AssetType.HTML
        if re.search(
            r"^\s*(import|export|const|let|var|function|class)\b", content, re.MULTILINE
        ):
            return AssetType.JS
        if re.search(
            r"^\s*(@[a-zA-Z-]+|[.#]?[a-zA-Z0-9_-]+)\s*\{", content, re.MULTILINE
        ):
            return AssetType.CSS

        return AssetType.UNKNOWN


class WebCompressor:
    """Unified facade for web asset compression."""

    def __init__(self, aggressive: bool = True, cache: Optional["CompressionCache"] = None, benchmark: Optional["Benchmark"] = None):
        self.aggressive = aggressive
        self._js_compressor = None
        self._css_compressor = None
        self._html_compressor = None
        self.cache = cache
        self.benchmark = benchmark

    @property
    def js_compressor(self):
        if self._js_compressor is None:
            from js_compressor import AdvancedJSCompressor

            self._js_compressor = AdvancedJSCompressor(aggressive=self.aggressive)
        return self._js_compressor

    @property
    def css_compressor(self):
        if self._css_compressor is None:
            from css_compressor import AdvancedCSSCompressor

            self._css_compressor = AdvancedCSSCompressor(aggressive=self.aggressive)
        return self._css_compressor

    @property
    def html_compressor(self):
        if self._html_compressor is None:
            from html_compressor import AdvancedHTMLCompressor

            self._html_compressor = AdvancedHTMLCompressor(aggressive=self.aggressive)
        return self._html_compressor

    def compress_string(
        self,
        content: str,
        asset_type: Optional[AssetType] = None,
        filename: Optional[str] = None,
    ) -> CompressionResult:
        start_time = time.perf_counter()

        if asset_type is None or asset_type == AssetType.UNKNOWN:
            base = BaseCompressor()
            asset_type = base.detect_type(content, filename)

        asset_key = asset_type.value if asset_type != AssetType.UNKNOWN else "unknown"

        if self.cache is not None:
            cached = self.cache.get(content, asset_key, self.aggressive)
            if cached is not None:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                return CompressionResult(
                    original_size=cached["original_size"],
                    compressed_size=cached["compressed_size"],
                    ratio=cached["ratio"],
                    savings_pct=cached["savings_pct"],
                    asset_type=asset_type,
                    elapsed_ms=elapsed_ms,
                    warnings=cached.get("warnings", []),
                    output=cached["output"],
                    _cached=True,
                )

        if asset_type == AssetType.JS:
            compressed, warnings = self.js_compressor.compress(content)
        elif asset_type == AssetType.CSS:
            compressed, warnings = self.css_compressor.compress(content)
        elif asset_type == AssetType.HTML:
            compressed, warnings = self.html_compressor.compress(content)
        else:
            compressed = content.strip()
            warnings = ["Unknown file type: minimal whitespace trimming applied."]

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        orig_len = len(content.encode("utf-8"))
        comp_len = len(compressed.encode("utf-8"))
        ratio = (comp_len / orig_len) if orig_len > 0 else 1.0
        savings_pct = (1.0 - ratio) * 100.0

        result = CompressionResult(
            original_size=orig_len,
            compressed_size=comp_len,
            ratio=ratio,
            savings_pct=savings_pct,
            asset_type=asset_type,
            elapsed_ms=elapsed_ms,
            warnings=warnings,
            output=compressed,
        )

        if self.cache is not None:
            self.cache.put(
                content,
                asset_key,
                self.aggressive,
                {
                    "original_size": orig_len,
                    "compressed_size": comp_len,
                    "ratio": ratio,
                    "savings_pct": savings_pct,
                    "warnings": warnings,
                    "output": compressed,
                },
            )

        if self.benchmark is not None:
            self.benchmark.record({
                "asset_type": asset_key,
                "original_size": orig_len,
                "compressed_size": comp_len,
                "savings_pct": savings_pct,
                "elapsed_ms": elapsed_ms,
                "aggressive": self.aggressive,
            })

        return result

    def compress_file(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        asset_type: Optional[AssetType] = None,
    ) -> CompressionResult:
        path = Path(input_path)
        if not path.is_file():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        content = path.read_text(encoding="utf-8", errors="replace")
        result = self.compress_string(
            content, asset_type=asset_type, filename=path.name
        )

        if output_path:
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(result.output, encoding="utf-8")

        return result


def main():
    parser = argparse.ArgumentParser(
        description="WebCompressor Pro — Advanced web asset compaction engine"
    )
    parser.add_argument("input", help="Input file or directory to compress")
    parser.add_argument("-o", "--output", help="Output file or directory")
    parser.add_argument(
        "-t",
        "--type",
        choices=["js", "css", "html", "auto"],
        default="auto",
        help="Asset type (default: auto)",
    )
    parser.add_argument(
        "--safe",
        action="store_true",
        help="Disable aggressive optimizations (safe mode)",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively process directories",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        default=True,
        help="Display compression statistics",
    )

    args = parser.parse_args()

    compressor = WebCompressor(aggressive=not args.safe)
    type_map = {
        "js": AssetType.JS,
        "css": AssetType.CSS,
        "html": AssetType.HTML,
        "auto": AssetType.UNKNOWN,
    }
    forced_type = type_map[args.type]

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Path '{args.input}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if input_path.is_file():
        result = compressor.compress_file(
            str(input_path), args.output, asset_type=forced_type
        )
        if not args.output:
            print(result.output)
        if args.stats:
            print(
                f"\n[{result.asset_type.value.upper()}] {input_path.name}: "
                f"{result.original_size}B -> {result.compressed_size}B "
                f"({result.savings_pct:.1f}% saved in {result.elapsed_ms:.1f}ms)",
                file=sys.stderr,
            )
            for w in result.warnings:
                print(f"  Warning: {w}", file=sys.stderr)
    elif input_path.is_dir():
        pattern = "**/*" if args.recursive else "*"
        files = [
            f
            for f in input_path.glob(pattern)
            if f.is_file() and f.suffix.lower() in (".js", ".css", ".html", ".htm")
        ]
        if not files:
            print("No compressible files found.", file=sys.stderr)
            return

        total_orig = 0
        total_comp = 0
        out_dir = Path(args.output) if args.output else None

        for file in files:
            rel = file.relative_to(input_path)
            target_out = str(out_dir / rel) if out_dir else None
            res = compressor.compress_file(
                str(file), target_out, asset_type=forced_type
            )
            total_orig += res.original_size
            total_comp += res.compressed_size
            print(
                f"Compressed {rel} ({res.original_size}B -> {res.compressed_size}B, {res.savings_pct:.1f}%)"
            )

        saved = total_orig - total_comp
        pct = (saved / total_orig * 100.0) if total_orig > 0 else 0
        print(
            f"\nTotal: {total_orig}B -> {total_comp}B ({pct:.1f}% overall reduction across {len(files)} files)"
        )


if __name__ == "__main__":
    main()
