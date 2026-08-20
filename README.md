# WebCompressor Pro

Production-grade, semantic-preserving web asset compressor for JavaScript, CSS, and HTML.

## Features

- **JavaScript**: Token-aware minification protecting strings, regex literals, template literals, and comments. Safe number optimization, ASI-aware whitespace compaction, boolean simplification (`true` → `!0`), and constant folding.
- **CSS**: Bidirectional color optimization (named colors ↔ hex ↔ 3-digit hex), `rgba()` shorthand, zero-unit stripping, font-weight numeric conversion, duplicate property removal, selector/rule compaction, and url() preservation.
- **HTML**: Semantic preservation of `<pre>`, `<code>`, and `<textarea>` tags. Inline `<style>` and `<script>` minification. Boolean attribute collapsing. Conditional comment preservation. Doctype shortening.

## Self-Improving System

- **Disk Cache**: SHA-256 keyed cache with TTL. Skips recompression of unchanged files.
- **Benchmark Tracker**: Records per-run metrics (savings, elapsed time, asset type). Suggests optimal `--safe`/`--aggressive` settings based on historical performance.
- **Watch Mode**: Recompresses automatically on file changes (requires `watchdog`).

## Installation

```bash
pip install .
```

## CLI Usage

```bash
# Compress a single file
web-compressor input.js -o output.js

# Compress with auto-detection
web-compressor index.html -o index.min.html

# Compress entire directory recursively with cache
web-compressor ./assets -o ./assets/min -r --cache

# Safe mode (disable aggressive optimizations)
web-compressor input.js --safe

# Display statistics
web-compressor input.js --stats

# Show unified diff instead of writing
web-compressor input.css --diff

# Watch directory and recompress on change
web-compressor ./src --watch

# Parallel processing
web-compressor ./assets -o ./dist -r -j 4

# Benchmark summary
web-compressor --benchmark-summary

# Suggest optimal settings for a file
web-compressor style.css --suggest
```

## Python API

```python
from compressor import WebCompressor, AssetType
from cache import CompressionCache
from benchmark import Benchmark

wc = WebCompressor(aggressive=True)

# Compress string with auto-detection
result = wc.compress_string("const x = 1; const y = 2;")
print(result.output)          # "const x=1;const y=2"
print(result.savings_pct)     # e.g. 45.2

# With cache and benchmark
cache = CompressionCache()
bench = Benchmark()
wc = WebCompressor(aggressive=True, cache=cache, benchmark=bench)
result = wc.compress_string(content)

# Compress file
result = wc.compress_file("input.js", "output.js")

# Force asset type
result = wc.compress_string("...", asset_type=AssetType.CSS)
```

## Running Tests

```bash
python -m unittest discover -s tests -v
```

## Design Principles

1. **Token Safety**: All string literals, regex literals, template literals, and comments are extracted before any transformation. They are restored unchanged at the end.
2. **ASI Preservation**: Newlines after `return`, `throw`, `break`, `continue`, `yield`, `await`, `delete`, `void`, `typeof` are preserved to avoid changing JavaScript semantics.
3. **Semantic Preservation**: HTML verbatim tags (`<pre>`, `<code>`, `<textarea>`) are extracted and restored without modification.
4. **Bidirectional Color Optimization**: CSS colors are converted to the shortest valid representation in both directions.
5. **Self-Improving**: Cache avoids redundant work; benchmark log enables strategy optimization over time.

## License

MIT
