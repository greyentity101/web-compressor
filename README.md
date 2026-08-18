# WebCompressor Pro

Production-grade, semantic-preserving web asset compressor for JavaScript, CSS, and HTML.

## Features

- **JavaScript**: Token-aware minification protecting strings, regex literals, template literals, and comments. Safe number optimization, ASI-aware whitespace compaction, and dead code removal.
- **CSS**: Bidirectional color optimization (named colors ↔ hex ↔ 3-digit hex), zero-unit stripping, font-weight numeric conversion, selector/rule compaction, and url() preservation.
- **HTML**: Semantic preservation of `<pre>`, `<code>`, and `<textarea>` tags. Inline `<style>` and `<script>` minification. Boolean attribute collapsing. Conditional comment preservation. Doctype shortening.

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

# Compress entire directory recursively
web-compressor ./assets -o ./assets/min -r

# Safe mode (disable aggressive optimizations)
web-compressor input.js --safe

# Display statistics
web-compressor input.js --stats
```

## Python API

```python
from compressor import WebCompressor, AssetType

wc = WebCompressor(aggressive=True)

# Compress string with auto-detection
result = wc.compress_string("const x = 1; const y = 2;")
print(result.output)          # "const x=1;const y=2"
print(result.savings_pct)     # e.g. 45.2

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

## License

MIT
