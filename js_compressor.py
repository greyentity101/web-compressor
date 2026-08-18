#!/usr/bin/env python3
"""
Advanced JavaScript compressor with AST-inspired optimizations.
"""

import re
from typing import Tuple, List
from compressor import BaseCompressor, AssetType


class AdvancedJSCompressor(BaseCompressor):
    """Production-grade JS minifier with scope-aware optimizations."""

    RESERVED = {
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
        "decodeURIComponent",
        "encodeURI",
        "decodeURI",
        "Error",
        "TypeError",
        "RangeError",
        "SyntaxError",
        "ReferenceError",
        "URIError",
        "EvalError",
        "AggregateError",
        "WeakMap",
        "WeakSet",
        "DataView",
        "Int8Array",
        "Uint8Array",
        "Int16Array",
        "Uint16Array",
        "Int32Array",
        "Uint32Array",
        "Float32Array",
        "Float64Array",
        "BigInt64Array",
        "BigUint64Array",
        "Uint8ClampedArray",
        "BigInt",
        "Reflect",
        "Intl",
        "WebAssembly",
    }

    def compress(self, content: str) -> Tuple[str, List[str]]:
        warnings = []
        code = content

        # Multi-pass optimization pipeline
        code = self._remove_comments(code)
        code = self._remove_whitespace(code)
        code = self._shorten_numbers(code)
        code = self._simplify_booleans(code)
        code = self._merge_strings(code)
        code = self._remove_empty(code)
        code = self._constant_fold(code)
        code = self._optimize_operators(code)

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
        # Collapse whitespace
        code = re.sub(r"[ \t]+", " ", code)
        # Remove spaces around operators
        code = re.sub(r"\s*([{}();:,<>!=+\-*/%&|^~?])\s*", r"\1", code)
        # Remove spaces after commas
        code = re.sub(r",\s+", ",", code)
        # Remove trailing whitespace on lines
        code = "\n".join(line.rstrip() for line in code.split("\n"))
        # Collapse multiple newlines
        code = re.sub(r"\n\s*\n", "\n", code)
        # Remove newlines around braces
        code = re.sub(r"([{};])\n+", r"\1", code)
        code = re.sub(r"\n+([{};])", r"\1", code)
        # Remove space before colon
        code = re.sub(r"\s+:", ":", code)
        # Remove space after opening paren/bracket
        code = re.sub(r"([({\[])\s+", r"\1", code)
        # Remove space before closing paren/bracket/brace
        code = re.sub(r"\s+\)", ")", code)
        code = re.sub(r"\s+\}", "}", code)
        code = re.sub(r"\s+\]", "]", code)
        return code

    def _shorten_numbers(self, code: str) -> str:
        def replace_number(m):
            num = m.group(0)
            try:
                val = float(num)
                if val == int(val) and "." in num:
                    return str(int(val))
                if val > 0 and val < 1 and num.startswith("0") and "." in num:
                    return num[1:]
                sci = f"{val:g}"
                if "e" in sci and len(sci) < len(num):
                    return sci
            except ValueError:
                pass
            return num

        code = re.sub(r"\b\d+\.?\d*(?:e[+-]?\d+)?\b", replace_number, code)
        return code

    def _simplify_booleans(self, code: str) -> str:
        code = re.sub(r"!!\s*([a-zA-Z_$][\w$]*)", r"\1", code)
        code = re.sub(r"([a-zA-Z_$][\w$]*)\s*===\s*true", r"\1", code)
        code = re.sub(r"([a-zA-Z_$][\w$]*)\s*!==\s*false", r"\1", code)
        code = re.sub(r"true\s*===\s*([a-zA-Z_$][\w$]*)", r"\1", code)
        code = re.sub(r"false\s*!==\s*([a-zA-Z_$][\w$]*)", r"\1", code)
        # De Morgan's laws
        code = re.sub(
            r"!\s*([a-zA-Z_$][\w$]*)\s*&&\s*([a-zA-Z_$][\w$]*)", r"!\1||\2", code
        )
        code = re.sub(
            r"!\s*([a-zA-Z_$][\w$]*)\s*\|\|\s*([a-zA-Z_$][\w$]*)", r"!\1&&\2", code
        )
        return code

    def _merge_strings(self, code: str) -> str:
        code = re.sub(
            r"""(['"])([^'"]*)\1\s*(['"])([^'"]*)\3""",
            lambda m: m.group(1) + m.group(2) + m.group(4) + m.group(1),
            code,
        )
        return code

    def _remove_empty(self, code: str) -> str:
        code = re.sub(r";;+", ";", code)
        code = re.sub(r"\{\s*\}", "{}", code)
        return code

    def _constant_fold(self, code: str) -> str:
        def eval_const(m):
            expr = m.group(0)
            try:
                if re.match(r"^\d+[\+\-\*/]\d+$", expr):
                    result = eval(expr)
                    return str(result)
            except:
                pass
            return expr

        code = re.sub(r"\b(\d+)\s*([+\-*/])\s*(\d+)\b", eval_const, code)
        return code

    def _optimize_operators(self, code: str) -> str:
        # x = x + 1 → x++ or x += 1
        code = re.sub(r"(\w+)\s*=\s*\1\s*\+\s*(\d+)\s*;", r"\1+=\2;", code)
        code = re.sub(r"(\w+)\s*=\s*\1\s*-\s*(\d+)\s*;", r"\1-=\2;", code)
        # x = x * 2 → x *= 2
        code = re.sub(r"(\w+)\s*=\s*\1\s*\*\s*([^=])", r"\1*=\2", code)
        return code

    def _scope_rename(self, code: str) -> Tuple[str, List[str]]:
        warnings = []
        if not self.aggressive:
            return code, warnings

        # Tokenize
        tokens = re.findall(r"([a-zA-Z_$][\w$]*)|([^a-zA-Z_$]+)", code)

        # Identify safe-to-rename identifiers
        safe_to_rename = set()
        for i, (ident, _) in enumerate(tokens):
            if not ident or ident in self.RESERVED:
                continue
            # Skip property access
            if i > 0 and tokens[i - 1][1] and tokens[i - 1][1].endswith("."):
                continue
            # Skip after new/typeof/delete/void
            if (
                i > 0
                and tokens[i - 1][1]
                and tokens[i - 1][1].strip()
                in (
                    "new",
                    "typeof",
                    "delete",
                    "void",
                    "return",
                    "throw",
                    "case",
                    "in",
                    "instanceof",
                )
            ):
                continue
            safe_to_rename.add(ident)

        if not safe_to_rename:
            return code, warnings

        # Generate short names
        short_names = {}
        used = set(safe_to_rename)
        for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ$_":
            if c not in self.RESERVED and c not in used:
                short_names[next(iter(safe_to_rename))] = c
                used.add(c)
                safe_to_rename.remove(next(iter(safe_to_rename)))
                if not safe_to_rename:
                    break

        # Two-char names
        if safe_to_rename:
            for c1 in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ$_":
                for (
                    c2
                ) in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$_":
                    name = c1 + c2
                    if name not in self.RESERVED and name not in used:
                        short_names[next(iter(safe_to_rename))] = name
                        used.add(name)
                        safe_to_rename.remove(next(iter(safe_to_rename)))
                        if not safe_to_rename:
                            break
                if not safe_to_rename:
                    break

        # Rename
        result = []
        for i, (ident, non_ident) in enumerate(tokens):
            if ident and ident in short_names:
                if i > 0 and tokens[i - 1][1] and tokens[i - 1][1].endswith("."):
                    result.append(ident)
                    continue
                if (
                    i > 0
                    and tokens[i - 1][1]
                    and tokens[i - 1][1].strip()
                    in (
                        "new",
                        "typeof",
                        "delete",
                        "void",
                        "return",
                        "throw",
                        "case",
                        "in",
                        "instanceof",
                    )
                ):
                    result.append(ident)
                    continue
                result.append(short_names[ident])
            else:
                result.append(ident if ident else non_ident)

        compressed = "".join(result)
        warnings.append(f"Renamed {len(short_names)} variables to short names")
        return compressed, warnings

    def detect_type(self, content: str, filename: str) -> AssetType:
        if filename.endswith((".js", ".mjs", ".jsx", ".ts", ".tsx")):
            return AssetType.JS
        if re.search(
            r"^\s*(import|export|const|let|var|function|class)\s", content, re.MULTILINE
        ):
            return AssetType.JS
        return AssetType.UNKNOWN
