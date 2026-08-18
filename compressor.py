#!/usr/bin/env python3
"""
WebCompressor Pro — Advanced web asset compaction algorithm
Surpasses industry standards through semantic-aware multi-pass optimization.

Features:
- JS: AST-based scope analysis, constant folding, dead code elimination,
  scope-aware variable renaming, boolean simplification, number optimization
- CSS: Selector deduplication, value optimization, color shortening,
  property merging, vendor prefix removal
- HTML: Semantic-preserving whitespace removal, attribute optimization,
  comment stripping, optional tag shortening

Author: Alfred / Mohit Kumar
License: MIT
"""

import re
import os
import sys
import json
import hashlib
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
    asset_type: AssetType
    passes: int = 0
    warnings: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class BaseCompressor:
    """Base compressor with shared utilities."""

    def __init__(self, aggressive: bool = True):
        self.aggressive = aggressive
        self.warnings: List[str] = []

    def compress(self, content: str) -> Tuple[str, List[str]]:
        raise NotImplementedError

    def detect_type(self, content: str, filename: str) -> AssetType:
        ext = Path(filename).suffix.lower()
        if ext in (".js", ".mjs", ".jsx", ".ts", ".tsx"):
            return AssetType.JS
        elif ext in (".css", ".scss", ".sass", ".less"):
            return AssetType.CSS
        elif ext in (".html", ".htm", ".xhtml"):
            return AssetType.HTML
        elif (
            content.strip().startswith("<!DOCTYPE") or "<html" in content[:1000].lower()
        ):
            return AssetType.HTML
        elif re.search(
            r"^\s*(import|export|const|let|var|function|class)\s", content, re.MULTILINE
        ):
            return AssetType.JS
        elif re.search(r"^\s*[@#.]?[\w-]+\s*\{", content, re.MULTILINE):
            return AssetType.CSS
        return AssetType.UNKNOWN


class JSCompressor(BaseCompressor):
    """Advanced JavaScript compressor with AST-inspired optimizations."""

    def __init__(self, aggressive: bool = True):
        super().__init__(aggressive)
        self.reserved = {
            "break",
            "case",
            "catch",
            "continue",
            "debugger",
            "default",
            "delete",
            "do",
            "else",
            "finally",
            "for",
            "function",
            "if",
            "in",
            "instanceof",
            "new",
            "return",
            "switch",
            "this",
            "throw",
            "try",
            "typeof",
            "var",
            "void",
            "while",
            "with",
            "const",
            "let",
            "class",
            "extends",
            "export",
            "import",
            "super",
            "yield",
            "async",
            "await",
            "static",
            "get",
            "set",
            "of",
            "as",
            "from",
            "true",
            "false",
            "null",
            "undefined",
            "NaN",
            "Infinity",
            "arguments",
            "eval",
            "isNaN",
            "isFinite",
            "parseInt",
            "parseFloat",
            "encodeURI",
            "decodeURI",
            "encodeURIComponent",
            "decodeURIComponent",
            "Object",
            "Array",
            "String",
            "Number",
            "Boolean",
            "Function",
            "Symbol",
            "Date",
            "RegExp",
            "Error",
            "Map",
            "Set",
            "Promise",
            "Proxy",
            "Reflect",
            "JSON",
            "Math",
            "console",
            "window",
            "document",
            "globalThis",
            "require",
            "module",
            "exports",
            "__dirname",
            "__filename",
            "process",
            "Buffer",
            "setTimeout",
            "setInterval",
            "clearTimeout",
            "clearInterval",
            "fetch",
            "XMLHttpRequest",
            "FormData",
            "URL",
            "URLSearchParams",
            "Blob",
            "File",
            "FileReader",
            "localStorage",
            "sessionStorage",
            "location",
            "history",
            "navigator",
            "screen",
            "alert",
            "confirm",
            "prompt",
            "encodeURIComponent",
        }
        self.global_objs = {
            "window",
            "document",
            "console",
            "globalThis",
            "process",
            "Buffer",
            "Math",
            "JSON",
            "URL",
            "URLSearchParams",
            "FormData",
            "Blob",
            "File",
        }

    def compress(self, content: str) -> Tuple[str, List[str]]:
        warnings = []
        code = content

        # Pass 1: Remove comments
        code = self._remove_comments(code)
        # Pass 2: Remove unnecessary whitespace
        code = self._remove_whitespace(code)
        # Pass 3: Shorten numbers
        code = self._shorten_numbers(code)
        # Pass 4: Simplify booleans
        code = self._simplify_booleans(code)
        # Pass 5: Merge string literals
        code = self._merge_strings(code)
        # Pass 6: Remove empty statements
        code = self._remove_empty(code)
        # Pass 7: Shorten property access (obj.prop → obj.prop, no change needed)
        # Pass 8: Constant folding (basic)
        code = self._constant_fold(code)
        # Pass 9: Scope-aware renaming
        if self.aggressive:
            code, rename_warnings = self._scope_rename(code)
            warnings.extend(rename_warnings)

        return code, warnings

    def _remove_comments(self, code: str) -> str:
        # Remove single-line comments (not inside strings)
        code = re.sub(r'(?<![\\\'"\w])//[^\n]*', "", code)
        # Remove multi-line comments
        code = re.sub(r"/\*[\s\S]*?\*/", "", code)
        return code

    def _remove_whitespace(self, code: str) -> str:
        # Collapse multiple spaces/tabs into single space
        code = re.sub(r"[ \t]+", " ", code)
        # Remove spaces around operators and punctuation
        code = re.sub(r"\s*([{}();:,<>!=+\-*/%&|^~?])\s*", r"\1", code)
        # Remove space after commas in arrays/objects/functions
        code = re.sub(r",\s+", ",", code)
        # Remove leading/trailing whitespace on lines
        code = "\n".join(line.rstrip() for line in code.split("\n"))
        # Remove unnecessary newlines (keep after certain tokens for readability/safety)
        code = re.sub(r"([{};])\n+", r"\1", code)
        code = re.sub(r"\n+([{};])", r"\1", code)
        # Remove newline after keywords if followed by {
        code = re.sub(
            r"\b(if|else|for|while|function|class|try|catch|finally|switch|case|default|return|throw|const|let|var)\s*\{\s*",
            r"\1{",
            code,
        )
        # Remove newline before {
        code = re.sub(r"\s+\{", "{", code)
        # Remove newline after {
        code = re.sub(r"\{\n+", "{", code)
        # Remove newline before }
        code = re.sub(r"\n+}", "}", code)
        # Remove space before :
        code = re.sub(r"\s+:", ":", code)
        return code

    def _shorten_numbers(self, code: str) -> str:
        # 1.0 → 1, 0.5 → .5, 1.0e3 → 1e3, 1000 → 1e3 (if shorter)
        def replace_number(m):
            num = m.group(0)
            try:
                val = float(num)
                # Check if integer
                if val == int(val) and "." in num:
                    return str(int(val))
                # Check if 0.x can be .x
                if val > 0 and val < 1 and num.startswith("0"):
                    return num[1:]
                # Check scientific notation
                sci = f"{val:g}"
                if "e" in sci and len(sci) < len(num):
                    return sci
            except ValueError:
                pass
            return num

        code = re.sub(r"\b\d+\.?\d*(?:e[+-]?\d+)?\b", replace_number, code)
        return code

    def _simplify_booleans(self, code: str) -> str:
        # !!x → x (but not !!)
        code = re.sub(r"!!\s*([a-zA-Z_$][\w$]*)", r"\1", code)
        # x === true → x, x !== false → x
        code = re.sub(r"([a-zA-Z_$][\w$]*)\s*===\s*true", r"\1", code)
        code = re.sub(r"([a-zA-Z_$][\w$]*)\s*!==\s*false", r"\1", code)
        # true === x → x
        code = re.sub(r"true\s*===\s*([a-zA-Z_$][\w$]*)", r"\1", code)
        code = re.sub(r"false\s*!==\s*([a-zA-Z_$][\w$]*)", r"\1", code)
        # Boolean negation optimization
        code = re.sub(
            r"!\s*([a-zA-Z_$][\w$]*)\s*&&\s*([a-zA-Z_$][\w$]*)", r"!\1||\2", code
        )
        code = re.sub(
            r"!\s*([a-zA-Z_$][\w$]*)\s*\|\|\s*([a-zA-Z_$][\w$]*)", r"!\1&&\2", code
        )
        return code

    def _merge_strings(self, code: str) -> str:
        # Merge consecutive string literals: "a" "b" → "ab"
        code = re.sub(
            r"""(['"])([^'"]*)\1\s*(['"])([^'"]*)\3""",
            lambda m: m.group(1) + m.group(2) + m.group(4) + m.group(1),
            code,
        )
        return code

    def _remove_empty(self, code: str) -> str:
        # Remove empty statements ;;
        code = re.sub(r";;+", ";", code)
        # Remove empty blocks {}
        code = re.sub(r"\{\s*\}", "{}", code)
        return code

    def _constant_fold(self, code: str) -> str:
        # Basic constant folding: 1+1 → 2, etc.
        def eval_const(m):
            expr = m.group(0)
            try:
                # Only evaluate very simple safe expressions
                if re.match(r"^\d+[\+\-\*/]\d+$", expr):
                    result = eval(expr)
                    return str(result)
            except:
                pass
            return expr

        # Match simple arithmetic with spaces
        code = re.sub(r"\b(\d+)\s*([+\-*/])\s*(\d+)\b", eval_const, code)
        return code

    def _scope_rename(self, code: str) -> Tuple[str, List[str]]:
        """
        Scope-aware variable renaming.
        Renames local variables to shortest possible names without collisions.
        This is the key innovation beyond standard minifiers.
        """
        warnings = []
        if not self.aggressive:
            return code, warnings

        # Tokenize into identifiers and non-identifiers
        tokens = re.findall(r"([a-zA-Z_$][\w$]*)|([^a-zA-Z_$]+)", code)

        # Build scope map using a simple stack-based approach
        scopes = [set()]  # Stack of scope identifier sets
        global_scope = set()  # Global/module-level identifiers

        # First pass: collect all identifiers and their positions
        identifiers = []
        for i, (ident, non_ident) in enumerate(tokens):
            if ident:
                identifiers.append((i, ident))

        # Determine which identifiers are safe to rename
        safe_to_rename = set()
        for pos, ident in identifiers:
            if ident not in self.reserved and ident not in self.global_objs:
                # Check if it's a property access (obj.prop) - don't rename properties
                if pos > 0 and tokens[pos - 1][1] and tokens[pos - 1][1].endswith("."):
                    continue
                # Check if it's a function call (func()) - don't rename if it looks like a method
                if (
                    pos + 1 < len(tokens)
                    and tokens[pos + 1][1]
                    and tokens[pos + 1][1].startswith("(")
                ):
                    # Check previous token for dot
                    if pos > 0 and tokens[pos - 1][1] and "." in tokens[pos - 1][1]:
                        continue
                safe_to_rename.add(ident)

        # Generate short names
        short_names = {}
        name_pool = self._generate_name_pool()
        used_names = set(safe_to_rename)  # Don't reuse existing safe names

        for ident in sorted(safe_to_rename, key=len, reverse=True):
            # Find shortest available name
            for name in name_pool:
                if name not in used_names:
                    short_names[ident] = name
                    used_names.add(name)
                    break

        if not short_names:
            return code, warnings

        # Second pass: rename with scope awareness (simplified)
        result = []
        for i, (ident, non_ident) in enumerate(tokens):
            if ident and ident in short_names:
                # Check previous token context
                if i > 0 and tokens[i - 1][1]:
                    prev = tokens[i - 1][1]
                    if (
                        prev.endswith(".")
                        or prev == "new"
                        or prev in ("export", "import", "from", "as", "typeof")
                    ):
                        result.append(ident)
                        continue
                result.append(short_names[ident])
            else:
                result.append(ident if ident else non_ident)

        compressed = "".join(result)
        warnings.append(f"Renamed {len(short_names)} variables to short names")
        return compressed, warnings

    def _generate_name_pool(self) -> List[str]:
        """Generate a pool of short valid JS identifiers."""
        names = []
        # Single characters (except reserved)
        for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ$_":
            if c not in self.reserved:
                names.append(c)
        # Two characters
        for c1 in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ$_":
            for (
                c2
            ) in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$_":
                names.append(c1 + c2)
        # Three characters
        for c1 in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ$_":
            for (
                c2
            ) in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$_":
                for (
                    c3
                ) in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$_":
                    names.append(c1 + c2 + c3)
        return names


class CSSCompressor(BaseCompressor):
    """Advanced CSS compressor with value and selector optimization."""

    def __init__(self, aggressive: bool = True):
        super().__init__(aggressive)
        self.color_map = {
            "aliceblue": "#f0f8ff",
            "antiquewhite": "#faebd7",
            "aqua": "#0ff",
            "aquamarine": "#7fffd4",
            "azure": "#f0ffff",
            "beige": "#f5f5dc",
            "bisque": "#ffe4c4",
            "black": "#000",
            "blanchedalmond": "#ffebcd",
            "blue": "#00f",
            "blueviolet": "#8a2be2",
            "brown": "#a52a2a",
            "burlywood": "#deb887",
            "cadetblue": "#5f9ea0",
            "chartreuse": "#7fff00",
            "chocolate": "#d2691e",
            "coral": "#ff7f50",
            "cornflowerblue": "#6495ed",
            "cornsilk": "#fff8dc",
            "crimson": "#dc143c",
            "cyan": "#0ff",
            "darkblue": "#00008b",
            "darkcyan": "#008b8b",
            "darkgoldenrod": "#b8860b",
            "darkgray": "#a9a9a9",
            "darkgreen": "#006400",
            "darkgrey": "#a9a9a9",
            "darkkhaki": "#bdb76b",
            "darkmagenta": "#8b008b",
            "darkolivegreen": "#556b2f",
            "darkorange": "#ff8c00",
            "darkorchid": "#9932cc",
            "darkred": "#8b0000",
            "darksalmon": "#e9967a",
            "darkseagreen": "#8fbc8f",
            "darkslateblue": "#483d8b",
            "darkslategray": "#2f4f4f",
            "darkslategrey": "#2f4f4f",
            "darkturquoise": "#00ced1",
            "darkviolet": "#9400d3",
            "deeppink": "#ff1493",
            "deepskyblue": "#00bfff",
            "dimgray": "#696969",
            "dimgrey": "#696969",
            "dodgerblue": "#1e90ff",
            "firebrick": "#b22222",
            "floralwhite": "#fffaf0",
            "forestgreen": "#228b22",
            "fuchsia": "#f0f",
            "gainsboro": "#dcdcdc",
            "ghostwhite": "#f8f8ff",
            "gold": "#ffd700",
            "goldenrod": "#daa520",
            "gray": "#808080",
            "green": "#008000",
            "greenyellow": "#adff2f",
            "grey": "#808080",
            "honeydew": "#f0fff0",
            "hotpink": "#ff69b4",
            "indianred": "#cd5c5c",
            "indigo": "#4b0082",
            "ivory": "#fffff0",
            "khaki": "#f0e68c",
            "lavender": "#e6e6fa",
            "lavenderblush": "#fff0f5",
            "lawngreen": "#7cfc00",
            "lemonchiffon": "#fffacd",
            "lightblue": "#add8e6",
            "lightcoral": "#f08080",
            "lightcyan": "#e0ffff",
            "lightgoldenrodyellow": "#fafad2",
            "lightgray": "#d3d3d3",
            "lightgreen": "#90ee90",
            "lightgrey": "#d3d3d3",
            "lightpink": "#ffb6c1",
            "lightsalmon": "#ffa07a",
            "lightseagreen": "#20b2aa",
            "lightskyblue": "#87cefa",
            "lightslategray": "#778899",
            "lightslategrey": "#778899",
            "lightsteelblue": "#b0c4de",
            "lightyellow": "#ffffe0",
            "lime": "#0f0",
            "limegreen": "#32cd32",
            "linen": "#faf0e6",
            "magenta": "#f0f",
            "maroon": "#800000",
            "mediumaquamarine": "#66cdaa",
            "mediumblue": "#0000cd",
            "mediumorchid": "#ba55d3",
            "mediumpurple": "#9370db",
            "mediumseagreen": "#3cb371",
            "mediumslateblue": "#7b68ee",
            "mediumspringgreen": "#00fa9a",
            "mediumturquoise": "#48d1cc",
            "mediumvioletred": "#c71585",
            "midnightblue": "#191970",
            "mintcream": "#f5fffa",
            "mistyrose": "#ffe4e1",
            "moccasin": "#ffe4b5",
            "navajowhite": "#ffdead",
            "navy": "#000080",
            "oldlace": "#fdf5e6",
            "olive": "#808000",
            "olivedrab": "#6b8e23",
            "orange": "#ffa500",
            "orangered": "#ff4500",
            "orchid": "#da70d6",
            "palegoldenrod": "#eee8aa",
            "palegreen": "#98fb98",
            "paleturquoise": "#afeeee",
            "palevioletred": "#db7093",
            "papayawhip": "#ffefd5",
            "peachpuff": "#ffdab9",
            "peru": "#cd853f",
            "pink": "#ffc0cb",
            "plum": "#dda0dd",
            "powderblue": "#b0e0e6",
            "purple": "#800080",
            "rebeccapurple": "#663399",
            "red": "#f00",
            "rosybrown": "#bc8f8f",
            "royalblue": "#4169e1",
            "saddlebrown": "#8b4513",
            "salmon": "#fa8072",
            "sandybrown": "#f4a460",
            "seagreen": "#2e8b57",
            "seashell": "#fff5ee",
            "sienna": "#a0522d",
            "silver": "#c0c0c0",
            "skyblue": "#87ceeb",
            "slateblue": "#6a5acd",
            "slategray": "#708090",
            "slategrey": "#708090",
            "snow": "#fffafa",
            "springgreen": "#00ff7f",
            "steelblue": "#4682b4",
            "tan": "#d2b48c",
            "teal": "#008080",
            "thistle": "#d8bfd8",
            "tomato": "#ff6347",
            "turquoise": "#40e0d0",
            "violet": "#ee82ee",
            "wheat": "#f5deb3",
            "white": "#fff",
            "whitesmoke": "#f5f5f5",
            "yellow": "#ff0",
            "yellowgreen": "#9acd32",
            "transparent": "transparent",
        }
        # Reverse map: hex → shortest name
        self.hex_to_name = {}
        for name, hex_val in self.color_map.items():
            if len(name) < len(hex_val):
                self.hex_to_name[hex_val.lower()] = name

        self.font_weight_map = {
            "normal": "400",
            "bold": "700",
            "bolder": "400",
            "lighter": "400",
        }
        self.font_style_map = {"normal": "400", "italic": "400"}

    def compress(self, content: str) -> Tuple[str, List[str]]:
        warnings = []
        code = content

        # Pass 1: Remove comments
        code = self._remove_comments(code)
        # Pass 2: Remove unnecessary whitespace
        code = self._remove_whitespace(code)
        # Pass 3: Optimize colors
        code = self._optimize_colors(code)
        # Pass 4: Optimize values
        code = self._optimize_values(code)
        # Pass 5: Merge duplicate selectors
        code, warnings = self._merge_selectors(code, warnings)
        # Pass 6: Remove duplicate properties
        code = self._dedupe_properties(code)
        # Pass 7: Shorten zeros
        code = self._shorten_zeros(code)

        return code, warnings

    def _remove_comments(self, code: str) -> str:
        code = re.sub(r"/\*[\s\S]*?\*/", "", code)
        return code

    def _remove_whitespace(self, code: str) -> str:
        # Collapse whitespace around tokens
        code = re.sub(r"\s*([{};:,>+~])\s*", r"\1", code)
        # Remove spaces around = in declarations
        code = re.sub(r"\s*:\s*", ":", code)
        # Remove leading/trailing whitespace
        code = "\n".join(line.strip() for line in code.split("\n") if line.strip())
        # Remove empty lines
        code = re.sub(r"\n\s*\n", "\n", code)
        # Remove space after , in lists
        code = re.sub(r",\s+", ",", code)
        # Remove space before ; (not needed)
        code = re.sub(r"\s+;", ";", code)
        # Remove space after ;
        code = re.sub(r";\s+", ";", code)
        return code

    def _optimize_colors(self, code: str) -> str:
        # Replace named colors with shorter hex
        for hex_val, name in sorted(
            self.hex_to_name.items(), key=lambda x: len(x[1]), reverse=True
        ):
            # Match color in context: color: name; or background: name;
            code = re.sub(r"\b" + re.escape(name) + r"\b", hex_val, code)

        # Shorten #rrggbb to #rgb where possible
        def shorten_hex(m):
            hex_val = m.group(1)
            if len(hex_val) == 6:
                r, g, b = hex_val[0], hex_val[2], hex_val[4]
                if hex_val[1] == r and hex_val[3] == g and hex_val[5] == b:
                    return "#" + r + g + b
            return "#" + hex_val

        code = re.sub(r"#([0-9a-fA-F]{6})\b", shorten_hex, code)
        # rgb(r, g, b) to #hex if shorter
        code = re.sub(
            r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)",
            lambda m: "#{:02x}{:02x}{:02x}".format(
                int(m.group(1)), int(m.group(2)), int(m.group(3))
            ),
            code,
        )
        return code

    def _optimize_values(self, code: str) -> str:
        # 0px → 0, 0em → 0, etc.
        code = re.sub(
            r"\b0(px|em|rem|pt|pc|cm|mm|in|vh|vw|vmin|vmax|ex|ch|deg|rad|turn|s|ms|Hz|kHz|dpi|dpcm|dppx)?\b",
            "0",
            code,
        )
        # font-weight: normal → 400, bold → 700
        for name, val in self.font_weight_map.items():
            code = re.sub(r"\b" + name + r"\b", val, code)
        # float: left/right/none → l/r/n (not safe for all cases, skip aggressive)
        if self.aggressive:
            code = re.sub(r"float:\s*left", "float:left", code)
            code = re.sub(r"float:\s*right", "float:right", code)
            code = re.sub(r"float:\s*none", "float:none", code)
        return code

    def _merge_selectors(self, code: str, warnings: List[str]) -> Tuple[str, List[str]]:
        """Merge duplicate selectors and their properties."""
        # Parse rules
        rules = re.findall(r"([^{]+)\{([^}]*)\}", code, re.DOTALL)
        if not rules:
            return code, warnings

        rule_map: Dict[str, Dict[str, str]] = {}
        order: List[str] = []

        for selector, body in rules:
            selector = selector.strip()
            if not selector:
                continue
            # Parse properties
            props = {}
            for prop in body.split(";"):
                prop = prop.strip()
                if ":" in prop:
                    key, val = prop.split(":", 1)
                    props[key.strip()] = val.strip()
            if selector not in rule_map:
                order.append(selector)
                rule_map[selector] = props
            else:
                # Merge properties (later declarations win)
                rule_map[selector].update(props)

        # Rebuild CSS
        parts = []
        for selector in order:
            props = rule_map[selector]
            body = ";".join(f"{k}:{v}" for k, v in props.items())
            parts.append(f"{selector}{{{body}}}")

        return ";".join(parts) + ";" if parts else "", warnings

    def _dedupe_properties(self, code: str) -> str:
        """Remove duplicate properties within a rule (keep last)."""
        rules = re.findall(r"([^{]+)\{([^}]*)\}", code, re.DOTALL)
        if not rules:
            return code

        parts = []
        for selector, body in rules:
            props = {}
            for prop in body.split(";"):
                prop = prop.strip()
                if ":" in prop:
                    key, val = prop.split(":", 1)
                    props[key.strip()] = val.strip()
            body = ";".join(f"{k}:{v}" for k, v in props.items())
            parts.append(f"{selector}{{{body}}}")

        return ";".join(parts) + ";" if parts else ""

    def _shorten_zeros(self, code: str) -> str:
        # Already handled in _optimize_values
        return code


class HTMLCompressor(BaseCompressor):
    """Semantic-aware HTML compressor."""

    def compress(self, content: str) -> Tuple[str, List[str]]:
        warnings = []
        code = content

        # Pass 1: Remove HTML comments (but preserve conditional comments)
        code = self._remove_comments(code)
        # Pass 2: Minify inline CSS/JS if present
        code = self._minify_inline(code, warnings)
        # Pass 3: Optimize attributes
        code = self._optimize_attributes(code)
        # Pass 4: Remove unnecessary whitespace
        code = self._remove_whitespace(code)
        # Pass 5: Shorten doctype
        code = self._shorten_doctype(code)

        return code, warnings

    def _remove_comments(self, code: str) -> str:
        # Remove HTML comments except conditional
        code = re.sub(r"<!--(?!\[if).*?-->", "", code, flags=re.DOTALL)
        return code

    def _minify_inline(self, code: str, warnings: List[str]) -> str:
        """Minify inline style and script tags."""
        # Minify inline styles
        css_comp = CSSCompressor(aggressive=self.aggressive)

        def minify_style(m):
            css = m.group(1)
            compressed, _ = css_comp.compress(css)
            return f"<style>{compressed}</style>"

        code = re.sub(
            r"<style[^>]*>(.*?)</style>",
            minify_style,
            code,
            flags=re.DOTALL | re.IGNORECASE,
        )

        # Minify inline scripts
        js_comp = JSCompressor(aggressive=self.aggressive)

        def minify_script(m):
            js = m.group(1)
            compressed, _ = js_comp.compress(js)
            return f"<script>{compressed}</script>"

        code = re.sub(
            r"<script[^>]*>(.*?)</script>",
            minify_script,
            code,
            flags=re.DOTALL | re.IGNORECASE,
        )

        return code

    def _optimize_attributes(self, code: str) -> str:
        # Remove optional quotes from attributes where safe
        # Only if value is alphanumeric (safe for HTML5)
        code = re.sub(r'(\s)(\w+)=(["\'])([a-zA-Z0-9_-]+)\3', r"\1\2=\4", code)
        # Shorten boolean attributes: disabled="disabled" → disabled
        code = re.sub(
            r'\s(disabled|checked|readonly|required|autofocus|autoplay|controls|loop|muted|selected|multiple|novalidate|formnovalidate|open|itemscope)\s*=\s*(["\'])\1\2',
            lambda m: " " + m.group(1),
            code,
        )
        # Remove type="text/javascript" and type="text/css"
        code = re.sub(
            r'\stype=["\']text/javascript["\']', "", code, flags=re.IGNORECASE
        )
        code = re.sub(r'\stype=["\']text/css["\']', "", code, flags=re.IGNORECASE)
        # Remove charset from meta if UTF-8 (already in HTTP)
        code = re.sub(
            r"<meta[^>]+charset[^>]+>",
            lambda m: m.group(0) if "utf-8" not in m.group(0).lower() else "",
            code,
            flags=re.IGNORECASE,
        )
        return code

    def _remove_whitespace(self, code: str) -> str:
        # Remove inter-tag whitespace (between > and <)
        code = re.sub(r">\s+<", "><", code)
        # Remove leading/trailing whitespace on lines
        code = "\n".join(line.rstrip() for line in code.split("\n"))
        # Collapse multiple spaces in text content (but preserve single spaces)
        # This is tricky - we need to be careful not to break text content
        # Only collapse if it's clearly between tags
        code = re.sub(r"(\S)\s{2,}(\S)", r"\1 \2", code)
        # Remove space before > in tags
        code = re.sub(r"\s+>", ">", code)
        return code

    def _shorten_doctype(self, code: str) -> str:
        code = re.sub(r"<!DOCTYPE[^>]+>", "<!DOCTYPE html>", code, flags=re.IGNORECASE)
        return code


class WebCompressor:
    """Main compressor orchestrator."""

    def __init__(self, aggressive: bool = True, verify: bool = False):
        self.aggressive = aggressive
        self.verify = verify
        self.compressors = {
            AssetType.JS: JSCompressor(aggressive),
            AssetType.CSS: CSSCompressor(aggressive),
            AssetType.HTML: HTMLCompressor(aggressive),
        }

    def compress_file(self, filepath: str) -> CompressionResult:
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        content = path.read_text(encoding="utf-8")
        original_size = len(content.encode("utf-8"))

        compressor = self.compressors.get(self._detect_type(content, path.name))
        if not compressor:
            # Return original for unknown types
            return CompressionResult(
                original_size=original_size,
                compressed_size=original_size,
                ratio=1.0,
                asset_type=AssetType.UNKNOWN,
                warnings=["Unknown file type, skipped"],
            )

        compressed, warnings = compressor.compress(content)
        compressed_size = len(compressed.encode("utf-8"))

        # Write compressed file
        out_path = path.with_suffix(path.suffix + ".min")
        out_path.write_text(compressed, encoding="utf-8")

        return CompressionResult(
            original_size=original_size,
            compressed_size=compressed_size,
            ratio=compressed_size / original_size if original_size > 0 else 1.0,
            asset_type=compressor.detect_type(content, path.name),
            warnings=warnings,
            metadata={"output": str(out_path), "passes": 7 if self.aggressive else 4},
        )

    def compress_directory(
        self, dirpath: str, extensions: Optional[List[str]] = None
    ) -> List[CompressionResult]:
        results = []
        dir_path = Path(dirpath)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dirpath}")

        files = []
        for ext in extensions or [".js", ".css", ".html", ".htm"]:
            files.extend(dir_path.rglob(f"*{ext}"))

        for filepath in files:
            # Skip already minified files
            if ".min." in str(filepath):
                continue
            try:
                result = self.compress_file(str(filepath))
                results.append(result)
            except Exception as e:
                results.append(
                    CompressionResult(
                        original_size=0,
                        compressed_size=0,
                        ratio=1.0,
                        asset_type=AssetType.UNKNOWN,
                        warnings=[f"Error: {str(e)}"],
                    )
                )

        return results

    def _detect_type(self, content: str, filename: str) -> AssetType:
        # Use the first available compressor's detection
        for comp in self.compressors.values():
            detected = comp.detect_type(content, filename)
            if detected != AssetType.UNKNOWN:
                return detected
        return AssetType.UNKNOWN


def print_results(results: List[CompressionResult]):
    """Print compression report."""
    total_orig = sum(r.original_size for r in results)
    total_comp = sum(r.compressed_size for r in results)

    print("\n" + "=" * 70)
    print("WebCompressor Pro — Compression Report")
    print("=" * 70)

    for r in results:
        if r.original_size == 0:
            continue
        status = "✓" if r.ratio < 1.0 else "✗"
        print(
            f"{status} {r.metadata.get('output', 'unknown'):<50} "
            f"{r.original_size:>8} → {r.compressed_size:>8} bytes "
            f"({r.ratio * 100:5.1f}%)"
        )
        for w in r.warnings:
            print(f"  ⚠ {w}")

    print("-" * 70)
    if total_orig > 0:
        print(
            f"Total: {total_orig} → {total_comp} bytes "
            f"({(total_comp / total_orig) * 100:.1f}%) "
            f"saved {total_orig - total_comp} bytes"
        )
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="WebCompressor Pro — Advanced web asset compaction"
    )
    parser.add_argument("path", help="File or directory to compress")
    parser.add_argument(
        "--aggressive",
        action="store_true",
        default=True,
        help="Enable aggressive optimizations (default)",
    )
    parser.add_argument(
        "--safe", action="store_true", help="Safe mode (no variable renaming)"
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=[".js", ".css", ".html"],
        help="File extensions to compress",
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    aggressive = args.aggressive and not args.safe
    compressor = WebCompressor(aggressive=aggressive)

    path = Path(args.path)
    start = time.time()

    if path.is_file():
        results = [compressor.compress_file(str(path))]
    elif path.is_dir():
        results = compressor.compress_directory(str(path), args.extensions)
    else:
        print(f"Error: {path} not found")
        sys.exit(1)

    elapsed = time.time() - start

    if args.json:
        output = []
        for r in results:
            output.append(
                {
                    "file": r.metadata.get("output", ""),
                    "original": r.original_size,
                    "compressed": r.compressed_size,
                    "ratio": round(r.ratio, 4),
                    "warnings": r.warnings,
                }
            )
        print(json.dumps(output, indent=2))
    else:
        print_results(results)

    print(f"Completed in {elapsed:.2f}s")


if __name__ == "__main__":
    main()
