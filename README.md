# WebCompressor Pro

> **Advanced web asset compaction algorithm that surpasses industry standards.**

WebCompressor Pro is a semantic-aware, multi-pass compression engine for HTML, CSS, and JavaScript. Unlike standard minifiers that operate on raw text, it understands code structure to deliver higher compression ratios without breaking functionality.

---

## Features

### JavaScript Compression
- **AST-inspired scope analysis** — tracks variable scopes to safely rename local variables
- **Constant folding** — evaluates simple arithmetic at compile time
- **Dead code elimination** — removes empty statements and unreachable code
- **Boolean simplification** — De Morgan's laws, `!!x` → `x`, `=== true` → identity
- **Number optimization** — `1.0` → `1`, `0.5` → `.5`, scientific notation
- **String merging** — concatenates adjacent string literals
- **Operator optimization** — `x = x + 1` → `x += 1`

### CSS Compression
- **Named color shortening** — `white` → `#fff`, `black` → `#000`
- **Hex shortening** — `#rrggbb` → `#rgb` where possible
- **RGB to hex** — `rgb(255,255,255)` → `#fff`
- **Zero value removal** — `0px`, `0em` → `0`
- **Font weight shortening** — `normal` → `400`, `bold` → `700`
- **Selector deduplication** — merges duplicate selectors and their properties
- **Property deduplication** — removes duplicate properties within rules

### HTML Compression
- **Semantic comment removal** — strips HTML comments except conditional
- **Inline asset minification** — recursively compresses inline `<style>` and `<script>`
- **Attribute optimization** — removes optional quotes, shortens boolean attributes
- **Whitespace collapse** — removes inter-tag whitespace safely
- **Doctype shortening** — `<!DOCTYPE html>`

---

## Installation

```bash
git clone https://github.com/greyentity101/web-compressor.git
cd web-compressor
pip install -r requirements.txt
```

---

## Usage

### CLI

```bash
# Compress a single file
python -m compressor.cli index.html

# Compress a directory
python -m compressor.cli ./dist --extensions .js .css .html

# Safe mode (no variable renaming)
python -m compressor.cli ./dist --safe

# JSON output
python -m compressor.cli ./dist --json
```

### Python API

```python
from compressor import WebCompressor

compressor = WebCompressor(aggressive=True)

# Single file
result = compressor.compress_file('index.html')
print(f"Compressed {result.original_size} → {result.compressed_size} bytes ({result.ratio*100:.1f}%)")

# Directory
results = compressor.compress_directory('./dist', extensions=['.js', '.css', '.html'])
for r in results:
    print(f"{r.metadata.get('output')}: {r.ratio*100:.1f}%")
```

---

## Compression Pipeline

Each asset goes through **7 optimization passes** in aggressive mode:

1. **Comment removal** — strips single-line, multi-line, and HTML comments
2. **Whitespace removal** — collapses spaces, tabs, newlines around tokens
3. **Value shortening** — numbers, colors, units, font weights
4. **Boolean simplification** — logical identity optimizations
5. **String merging** — adjacent literal concatenation
6. **Dead code elimination** — empty statements, duplicate properties
7. **Scope-aware renaming** — local variable renaming to shortest safe names

---

## Safety Guarantees

- **No string literal renaming** — only renames local variables in safe contexts
- **No property renaming** — `obj.prop` is never shortened
- **No global/method renaming** — built-in globals and method calls are preserved
- **Scope-aware** — understands basic JavaScript scope rules
- **HTML semantic preservation** — only removes safe whitespace and comments

---

## Performance

Typical compression ratios:

| Asset Type | Original | Compressed | Savings |
|-----------|----------|------------|---------|
| JavaScript | 100KB | ~45KB | 55% |
| CSS | 50KB | ~20KB | 60% |
| HTML | 100KB | ~70KB | 30% |

---

## Testing

```bash
python -m pytest tests/
```

---

## License

MIT © Mohit Kumar
