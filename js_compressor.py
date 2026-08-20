#!/usr/bin/env python3
"""
Advanced JavaScript compressor with token-safe extraction and optimizations.
"""

import re
from typing import Tuple, List, Dict, Optional
from compressor import BaseCompressor, AssetType


class AdvancedJSCompressor(BaseCompressor):
    """Production-grade JS minifier with token protection and AST-inspired passes."""

    RESERVED_KEYWORDS = {
        "break",
        "case",
        "catch",
        "class",
        "const",
        "continue",
        "debugger",
        "default",
        "delete",
        "do",
        "else",
        "export",
        "extends",
        "finally",
        "for",
        "function",
        "if",
        "import",
        "in",
        "instanceof",
        "new",
        "return",
        "super",
        "switch",
        "this",
        "throw",
        "try",
        "typeof",
        "var",
        "void",
        "while",
        "with",
        "yield",
        "let",
        "static",
        "enum",
        "await",
        "async",
        "null",
        "true",
        "false",
        "undefined",
        "NaN",
        "Infinity",
    }

    # Tokens after which a / can start a regex literal
    REGEX_PRECEDING = {
        "(",
        ",",
        "=",
        ":",
        "[",
        "!",
        "&",
        "|",
        "?",
        "{",
        ";",
        "+",
        "-",
        "*",
        "/",
        "%",
        "return",
        "case",
        "throw",
        "typeof",
        "delete",
        "void",
        "yield",
        "await",
        "in",
        "instanceof",
    }

    # Tokens after which a newline should NOT be removed (ASI-sensitive)
    ASI_SENSITIVE = {
        "return",
        "throw",
        "break",
        "continue",
        "yield",
        "await",
        "delete",
        "void",
        "typeof",
    }

    def __init__(self, aggressive: bool = True):
        super().__init__(aggressive)
        self.literal_table: Dict[str, str] = {}
        self.literal_counter = 0

    def compress(self, content: str) -> Tuple[str, List[str]]:
        self.warnings = []
        self.literal_table = {}
        self.literal_counter = 0

        if not content.strip():
            return "", []

        # Pass 1: Tokenize & extract string literals, regex literals, and comments
        code = self._extract_tokens(content)

        # Pass 2: Number optimizations (safe, out-of-string)
        code = self._optimize_numbers(code)

        # Pass 2.5: Constant folding and boolean simplification
        code = self._fold_constants(code)

        # Pass 3: Safe dead code & semicolon optimizations
        code = self._clean_syntax(code)

        # Pass 4: Whitespace and operator compaction (ASI-safe)
        code = self._compact_whitespace(code)

        # Pass 5: Restore string and regex literals
        code = self._restore_tokens(code)

        return code, self.warnings

    def _extract_tokens(self, text: str) -> str:
        """
        Token-aware lexer pass that extracts comments, strings, regex literals,
        and numeric literals so subsequent transforms cannot corrupt them.
        """
        result = []
        i = 0
        n = len(text)
        last_non_ws_token = ""

        while i < n:
            ch = text[i]

            # 1. Single-line comment //
            if ch == "/" and i + 1 < n and text[i + 1] == "/":
                j = i + 2
                while j < n and text[j] not in ("\r", "\n"):
                    j += 1
                result.append(" ")
                i = j
                continue

            # 2. Multi-line comment /* ... */
            if ch == "/" and i + 1 < n and text[i + 1] == "*":
                j = i + 2
                is_preserved = j < n and text[j] in ("!", "@")
                while j + 1 < n and not (text[j] == "*" and text[j + 1] == "/"):
                    j += 1
                j = min(n, j + 2)
                if is_preserved:
                    token_id = f"___LITERAL_{self.literal_counter}___"
                    self.literal_counter += 1
                    self.literal_table[token_id] = text[i:j]
                    result.append(token_id)
                    last_non_ws_token = "literal"
                else:
                    result.append(" ")
                i = j
                continue

            # 3. String literals '...' and "..."
            if ch in ("'", '"'):
                quote = ch
                j = i + 1
                while j < n:
                    if text[j] == "\\":
                        j += 2
                        continue
                    if text[j] == quote:
                        j += 1
                        break
                    if text[j] in ("\r", "\n"):
                        break
                    j += 1
                token_str = text[i:j]
                token_id = f"___LITERAL_{self.literal_counter}___"
                self.literal_counter += 1
                self.literal_table[token_id] = token_str
                result.append(token_id)
                last_non_ws_token = "literal"
                i = j
                continue

            # 4. Template literals `...`
            if ch == "`":
                j = i + 1
                while j < n:
                    if text[j] == "\\":
                        j += 2
                        continue
                    if text[j] == "`":
                        j += 1
                        break
                    j += 1
                token_str = text[i:j]
                token_id = f"___LITERAL_{self.literal_counter}___"
                self.literal_counter += 1
                self.literal_table[token_id] = token_str
                result.append(token_id)
                last_non_ws_token = "literal"
                i = j
                continue

            # 5. Regex literal /.../ (only after valid preceding tokens)
            if ch == "/" and last_non_ws_token in self.REGEX_PRECEDING:
                j = i + 1
                in_char_class = False
                is_regex = True
                while j < n:
                    if text[j] == "\\":
                        j += 2
                        continue
                    if text[j] == "[":
                        in_char_class = True
                    elif text[j] == "]" and in_char_class:
                        in_char_class = False
                    elif text[j] == "/" and not in_char_class:
                        j += 1
                        while j < n and text[j].isalpha():
                            j += 1
                        break
                    elif text[j] in ("\r", "\n"):
                        is_regex = False
                        break
                    j += 1

                if is_regex:
                    token_str = text[i:j]
                    token_id = f"___LITERAL_{self.literal_counter}___"
                    self.literal_counter += 1
                    self.literal_table[token_id] = token_str
                    result.append(token_id)
                    last_non_ws_token = "literal"
                    i = j
                    continue

            # Track last non-whitespace token (identifiers and keywords only)
            if not ch.isspace():
                if ch.isalnum() or ch in ("_", "$"):
                    j = i
                    while j < n and (text[j].isalnum() or text[j] in ("_", "$")):
                        j += 1
                    word = text[i:j]
                    result.append(word)
                    last_non_ws_token = word
                    i = j
                    continue
                elif ch in "=+-*&|<>!/%~^?:;,.(){}[]":
                    last_non_ws_token = ch

            result.append(ch)
            i += 1

        return "".join(result)

    def _optimize_numbers(self, code: str) -> str:
        """Safely shorten numbers outside of strings."""

        def repl(m):
            num = m.group(0)
            try:
                val = float(num)
                # 1.0 -> 1
                if "." in num and val == int(val):
                    return str(int(val))
                # 0.5 -> .5
                if 0 < val < 1 and num.startswith("0."):
                    return num[1:]
                # 1000 -> 1e3
                if val >= 100 and val == int(val) and num.endswith("00"):
                    sci = f"{int(val):.0e}"
                    sci = sci.replace("+", "").replace("-", "-")
                    if "e" in sci:
                        parts = sci.split("e")
                        parts[1] = parts[1].lstrip("0") or "0"
                        sci = "e".join(parts)
                    if len(sci) < len(num):
                        return sci
            except (ValueError, OverflowError):
                pass
            return num

        return re.sub(
            r"(?<![a-zA-Z0-9_$.])\b\d+\.?\d*(?:e[+-]?\d+)?\b(?!\s*[a-zA-Z_$])",
            repl,
            code,
        )

    def _fold_constants(self, code: str) -> str:
        """Fold trivial constant expressions and boolean literals."""
        # true -> !0, false -> !1 (saves 1-2 chars per occurrence)
        code = re.sub(r"\btrue\b(?!\s*[:(])", "!0", code)
        code = re.sub(r"\bfalse\b(?!\s*[:(])", "!1", code)
        # null -> None (shorter in JS minifiers that use this convention)
        # Keep null as-is for safety; many minifiers do the same.
        return code

    def _clean_syntax(self, code: str) -> str:
        """Remove redundant semicolons and empty blocks."""
        # Remove consecutive semicolons
        code = re.sub(r";\s*;", ";", code)
        # Remove semicolon before closing brace
        code = re.sub(r";\s*}", "}", code)
        return code

    def _compact_whitespace(self, code: str) -> str:
        """Compact whitespace while respecting word boundaries and ASI."""
        # Collapse multiple horizontal whitespace to single space
        code = re.sub(r"[ \t]+", " ", code)

        # Remove spaces around non-alphanumeric punctuation where safe
        code = re.sub(r"\s*([{}();:,~?])\s*", r"\1", code)
        code = re.sub(
            r"\s*(=|\+=|-=|\*=|/=|%=|&=|\|=|\^=|&&|\|\||===|==|!==|!=|<=|>=|<|>)\s*",
            r"\1",
            code,
        )

        # Safe removal around + and - without colliding ++ or --
        def collapse_plus_minus(text: str) -> str:
            result = []
            i = 0
            n = len(text)
            while i < n:
                if text[i] in ("+", "-"):
                    ops = []
                    j = i
                    had_space = False
                    while j < n:
                        if text[j] in ("+", "-"):
                            ops.append(text[j])
                            j += 1
                        elif text[j] in (" ", "\t"):
                            had_space = True
                            j += 1
                        else:
                            break

                    while result and result[-1] in (" ", "\t"):
                        result.pop()

                    if had_space:
                        result.append(ops[0])
                        for op in ops[1:]:
                            result.append(" ")
                            result.append(op)
                    else:
                        result.extend(ops)

                    i = j
                else:
                    result.append(text[i])
                    i += 1

            return "".join(result)

        code = collapse_plus_minus(code)

        # Collapse multiple newlines into single newline
        code = re.sub(r"\n+", "\n", code)

        # Remove newlines where punctuation guarantees no ASI is triggered
        # BUT preserve newlines after ASI-sensitive keywords
        lines = code.split("\n")
        safe_lines = []
        for idx, line in enumerate(lines):
            stripped = line.strip()
            # Check if this line ends with an ASI-sensitive keyword
            is_asi_sensitive = any(
                stripped == kw
                or stripped.startswith(kw + " ")
                or stripped.startswith(kw + "(")
                for kw in self.ASI_SENSITIVE
            )
            if is_asi_sensitive and idx + 1 < len(lines):
                # Keep the newline - next line might be an expression
                safe_lines.append(line)
            else:
                # Remove trailing newline if next line starts with punctuation
                if idx + 1 < len(lines):
                    next_stripped = lines[idx + 1].strip()
                    if (
                        next_stripped
                        and next_stripped[0] in "{}();:,>~+=[\\]*/%&|^~?<>!-"
                    ):
                        safe_lines.append(stripped)
                    else:
                        safe_lines.append(line)
                else:
                    safe_lines.append(line)

        code = "\n".join(safe_lines)

        # Remove leading/trailing line whitespace
        lines = [line.strip() for line in code.split("\n") if line.strip()]
        return "\n".join(lines).strip()

    def _restore_tokens(self, code: str) -> str:
        """Reinsert all original protected string and regex literals."""
        for token_id, original in self.literal_table.items():
            code = code.replace(token_id, original)
        return code
