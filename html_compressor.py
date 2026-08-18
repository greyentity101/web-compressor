#!/usr/bin/env python3
"""
Advanced HTML compressor with semantic preservation.
"""

import re
from typing import Tuple, List
from compressor import BaseCompressor, AssetType


class AdvancedHTMLCompressor(BaseCompressor):
    """Semantic-aware HTML minifier."""

    def compress(self, content: str) -> Tuple[str, List[str]]:
        warnings = []
        code = content

        # Pass 1: Remove comments
        code = self._remove_comments(code)
        # Pass 2: Minify inline assets
        code = self._minify_inline(code, warnings)
        # Pass 3: Optimize attributes
        code = self._optimize_attributes(code)
        # Pass 4: Remove whitespace
        code = self._remove_whitespace(code)
        # Pass 5: Optimize doctype
        code = self._shorten_doctype(code)

        return code, warnings

    def _remove_comments(self, code: str) -> str:
        code = re.sub(r"<!--(?!\[if).*?-->", "", code, flags=re.DOTALL)
        return code

    def _minify_inline(self, code: str, warnings: List[str]) -> str:
        from css_compressor import AdvancedCSSCompressor
        from js_compressor import AdvancedJSCompressor

        css_comp = AdvancedCSSCompressor(aggressive=self.aggressive)
        js_comp = AdvancedJSCompressor(aggressive=self.aggressive)

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
        # Remove optional quotes
        code = re.sub(r'(\s)(\w+)=(["\'])([a-zA-Z0-9_-]+)\3', r"\1\2=\4", code)
        # Shorten boolean attributes
        code = re.sub(
            r'\s(disabled|checked|readonly|required|autofocus|autoplay|controls|loop|muted|selected|multiple|novalidate|open|itemscope)\s*=\s*(["\'])\1\2',
            lambda m: " " + m.group(1),
            code,
        )
        # Remove type="text/javascript"
        code = re.sub(
            r'\stype=["\']text/javascript["\']', "", code, flags=re.IGNORECASE
        )
        # Remove type="text/css"
        code = re.sub(r'\stype=["\']text/css["\']', "", code, flags=re.IGNORECASE)
        # Remove charset if UTF-8
        code = re.sub(
            r"<meta[^>]+charset[^>]+>",
            lambda m: "" if "utf-8" in m.group(0).lower() else m.group(0),
            code,
            flags=re.IGNORECASE,
        )
        return code

    def _remove_whitespace(self, code: str) -> str:
        code = re.sub(r">\s+<", "><", code)
        code = "\n".join(line.rstrip() for line in code.split("\n"))
        code = re.sub(r"(\S)\s{2,}(\S)", r"\1 \2", code)
        code = re.sub(r"\s+>", ">", code)
        return code

    def _shorten_doctype(self, code: str) -> str:
        code = re.sub(r"<!DOCTYPE[^>]+>", "<!DOCTYPE html>", code, flags=re.IGNORECASE)
        return code

    def detect_type(self, content: str, filename: str) -> AssetType:
        if filename.endswith((".html", ".htm", ".xhtml")):
            return AssetType.HTML
        if (
            content.strip().lower().startswith("<!doctype")
            or "<html" in content[:1000].lower()
        ):
            return AssetType.HTML
        return AssetType.UNKNOWN
