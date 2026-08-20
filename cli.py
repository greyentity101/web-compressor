#!/usr/bin/env python3
"""
WebCompressor Pro — CLI entry point with self-improving features.

Usage:
    web-compressor input.js -o output.js
    web-compressor ./assets -o ./assets/min -r --cache --benchmark
    web-compressor input.css --diff
    web-compressor . --watch
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional

from compressor import WebCompressor, AssetType, CompressionResult
from cache import CompressionCache
from benchmark import Benchmark


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="WebCompressor Pro — self-improving web asset compressor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  %(prog)s input.js -o output.min.js
  %(prog)s ./src -o ./dist -r --cache
  %(prog)s style.css --diff
  %(prog)s . --watch --stats
  %(prog)s --benchmark-summary
""",
    )
    p.add_argument("input", nargs="?", help="Input file or directory")
    p.add_argument("-o", "--output", help="Output file or directory")
    p.add_argument(
        "-t", "--type", choices=["js", "css", "html", "auto"], default="auto"
    )
    p.add_argument("--safe", action="store_true", help="Disable aggressive optimizations")
    p.add_argument("-r", "--recursive", action="store_true", help="Recurse into directories")
    p.add_argument("--stats", action="store_true", default=True, help="Show compression stats")
    p.add_argument("--no-stats", dest="stats", action="store_false")
    p.add_argument("--diff", action="store_true", help="Show unified diff instead of writing")
    p.add_argument("--watch", action="store_true", help="Watch directory and recompress on change")
    p.add_argument("--cache", action="store_true", help="Enable disk cache (default: on)")
    p.add_argument("--no-cache", dest="cache", action="store_false")
    p.add_argument("--benchmark", action="store_true", help="Record run to benchmark log")
    p.add_argument("--benchmark-summary", action="store_true", help="Print benchmark summary and exit")
    p.add_argument("--suggest", action="store_true", help="Suggest optimal settings for a file type")
    p.add_argument("-j", "--parallel", type=int, default=1, help="Parallel workers for directory mode")
    p.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    p.set_defaults(cache=True)
    return p


def process_file(
    compressor: WebCompressor,
    input_path: Path,
    output_path: Path | None,
    forced_type: AssetType,
    diff: bool,
    verbose: bool,
) -> CompressionResult | None:
    try:
        result = compressor.compress_file(
            str(input_path), str(output_path) if output_path else None,
            asset_type=forced_type if forced_type != AssetType.UNKNOWN else None,
        )
    except Exception as exc:
        print(f"ERROR: {input_path}: {exc}", file=sys.stderr)
        return None

    status = "CACHE" if getattr(result, "_cached", False) else "OK"
    print(
        f"[{status}] {input_path.name}: "
        f"{result.original_size}B -> {result.compressed_size}B "
        f"({result.savings_pct:.1f}% saved in {result.elapsed_ms:.1f}ms)",
        file=sys.stderr,
    )
    if verbose and result.warnings:
        for w in result.warnings:
            print(f"  Warning: {w}", file=sys.stderr)

    if diff and output_path:
        import difflib
        original = input_path.read_text(encoding="utf-8", errors="replace")
        diff_text = "".join(
            difflib.unified_diff(
                original.splitlines(keepends=True),
                result.output.splitlines(keepends=True),
                fromfile=f"a/{input_path.name}",
                tofile=f"b/{input_path.name}",
            )
        )
        print(diff_text)

    return result


def watch_mode(
    compressor: WebCompressor,
    directory: Path,
    output_dir: Path | None,
    forced_type: AssetType,
    recursive: bool,
) -> None:
    """Watch a directory and recompress on file changes."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("watchdog not installed. Run: pip install watchdog", file=sys.stderr)
        sys.exit(1)

    class Handler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.is_directory:
                return
            p = Path(event.src_path)
            if p.suffix.lower() in (".js", ".css", ".html", ".htm"):
                rel = p.relative_to(directory)
                target = output_dir / rel if output_dir else None
                process_file(compressor, p, target, forced_type, False, True)

    observer = Observer()
    observer.schedule(Handler(), str(directory), recursive=recursive)
    observer.start()
    print(f"Watching {directory} (Ctrl+C to stop)...", file=sys.stderr)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Benchmark summary mode
    if args.benchmark_summary:
        bench = Benchmark()
        summary = bench.summary()
        print(json.dumps(summary, indent=2))
        return

    # Suggest mode
    if args.suggest:
        bench = Benchmark()
        if not args.input:
            print("Error: --suggest requires a file path to inspect", file=sys.stderr)
            sys.exit(1)
        p = Path(args.input)
        ext = p.suffix.lower()
        type_map = {
            ".js": "javascript", ".css": "css", ".html": "html", ".htm": "html",
        }
        asset_type = type_map.get(ext, "unknown")
        suggestion = bench.suggest_strategy(asset_type)
        print(json.dumps(suggestion, indent=2))
        return

    if not args.input:
        parser.print_help()
        sys.exit(1)

    cache = CompressionCache() if args.cache else None
    benchmark = Benchmark() if args.benchmark else None
    compressor = WebCompressor(aggressive=not args.safe, cache=cache, benchmark=benchmark)

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

    if args.watch and input_path.is_dir():
        output_dir = Path(args.output) if args.output else None
        watch_mode(compressor, input_path, output_dir, forced_type, args.recursive)
        return

    if input_path.is_file():
        output_path = Path(args.output) if args.output else None
        process_file(compressor, input_path, output_path, forced_type, args.diff, args.verbose)
        if args.stats and cache:
            print(f"\nCache: {cache.stats()}", file=sys.stderr)

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

        out_dir = Path(args.output) if args.output else None
        total_orig = 0
        total_comp = 0
        cache_hits = 0

        import concurrent.futures

        def work(f: Path) -> CompressionResult | None:
            rel = f.relative_to(input_path)
            target = out_dir / rel if out_dir else None
            return process_file(compressor, f, target, forced_type, args.diff, args.verbose)

        if args.parallel > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as pool:
                results = list(pool.map(work, files))
        else:
            results = [work(f) for f in files]

        for res in results:
            if res is None:
                continue
            total_orig += res.original_size
            total_comp += res.compressed_size
            if getattr(res, "_cached", False):
                cache_hits += 1

        saved = total_orig - total_comp
        pct = (saved / total_orig * 100.0) if total_orig > 0 else 0
        print(
            f"\nTotal: {total_orig}B -> {total_comp}B ({pct:.1f}% overall reduction "
            f"across {len(files)} files, {cache_hits} cache hits)",
            file=sys.stderr,
        )
        if args.stats and cache:
            print(f"Cache: {cache.stats()}", file=sys.stderr)
        if args.stats and benchmark:
            print(f"Benchmark: {benchmark.summary()}", file=sys.stderr)


if __name__ == "__main__":
    main()
