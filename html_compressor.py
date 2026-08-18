#!/usr/bin/env python3
"""
Advanced HTML compressor with semantic preservation and inline asset compression.
"""

import re
from typing import Tuple, List, Dict
from compressor import BaseCompressor, AssetType


class AdvancedHTMLCompressor(BaseCompressor):
    """Semantic-aware HTML minifier with inline script and style processing."""

    BOOLEAN_ATTRIBUTES = {
        "allowfullscreen",
        "allowpaymentrequest",
        "async",
        "autofocus",
        "autoplay",
        "checked",
        "controls",
        "default",
        "defer",
        "disabled",
        "formnovalidate",
        "hidden",
        "ismap",
        "itemscope",
        "loop",
        "multiple",
        "muted",
        "nomodule",
        "novalidate",
        "open",
        "playsinline",
        "readonly",
        "required",
        "reversed",
        "selected",
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

        html = content

        # Pass 1: Protect sensitive tags (<pre>, <code>, <textarea>)
        html = self._protect_verbatim_tags(html)

        # Pass 2: Minify inline <style> and <script> blocks
        html = self._minify_inline_assets(html)

        # Pass 3: Remove HTML comments (preserving conditional comments)
        html = self._strip_comments(html)

        # Pass 4: Optimize attributes
        html = self._optimize_attributes(html)

        # Pass 5: Compact whitespace
        html = self._compact_whitespace(html)

        # Pass 6: Shorten doctype
        html = self._shorten_doctype(html)

        # Pass 7: Restore protected verbatim blocks
        html = self._restore_verbatim_tags(html)

        return html.strip(), self.warnings

    def _protect_verbatim_tags(self, html: str) -> str:
        """Protect <pre>, <code>, and <textarea> tags from whitespace modification."""

        def protect(m):
            token_id = f"___HTML_VERBATIM_{self.literal_counter}___"
            self.literal_counter += 1
            self.literal_table[token_id] = m.group(0)
            return token_id

        pattern = r"<(pre|code|textarea)\b[^>]*>[\s\S]*?</\1>"
        return re.sub(pattern, protect, html, flags=re.IGNORECASE)

    def _minify_inline_assets(self, html: str) -> str:
        """Compress inline <style> and <script> contents."""
        from css_compressor import AdvancedCSSCompressor
        from js_compressor import AdvancedJSCompressor

        css_comp = AdvancedCSSCompressor(aggressive=self.aggressive)
        js_comp = AdvancedJSCompressor(aggressive=self.aggressive)

        def style_repl(m):
            open_tag = m.group(1)
            content = m.group(2)
            close_tag = m.group(3)
            if content.strip():
                minified, w = css_comp.compress(content)
                self.warnings.extend([f"CSS: {msg}" for msg in w])
                return f"{open_tag}{minified}{close_tag}"
            return f"{open_tag}{close_tag}"

        def script_repl(m):
            open_tag = m.group(1)
            content = m.group(2)
            close_tag = m.group(3)

            # Check if script type is non-javascript (e.g. type="application/json")
            type_match = re.search(r'type=["\']([^"\']+)["\']', open_tag, re.IGNORECASE)
            if type_match:
                stype = type_match.group(1).lower()
                if (
                    "javascript" not in stype
                    and "ecmascript" not in stype
                    and stype != "module"
                ):
                    return m.group(0)

            if content.strip():
                minified, w = js_comp.compress(content)
                self.warnings.extend([f"JS: {msg}" for msg in w])
                return f"{open_tag}{minified}{close_tag}"
            return f"{open_tag}{close_tag}"

        html = re.sub(
            r"(<style\b[^>]*>)([\s\S]*?)(</style>)",
            style_repl,
            html,
            flags=re.IGNORECASE,
        )
        html = re.sub(
            r"(<script\b[^>]*>)([\s\S]*?)(</script>)",
            script_repl,
            html,
            flags=re.IGNORECASE,
        )
        return html

    def _strip_comments(self, html: str) -> str:
        # Preserve conditional comments <!--[if ...]>
        return re.sub(r"<!--(?!\[if)[\s\S]*?-->", "", html)

    def _optimize_attributes(self, html: str) -> str:
        def tag_repl(m):
            tag_content = m.group(0)

            # Collapse boolean attributes (e.g. checked="checked" -> checked)
            for attr in self.BOOLEAN_ATTRIBUTES:
                tag_content = re.sub(
                    rf'\b{attr}\s*=\s*["\']?{attr}["\']?',
                    attr,
                    tag_content,
                    flags=re.IGNORECASE,
                )

            # Remove redundant spaces around = inside tags
            tag_content = re.sub(r'\s*=\s*(["\'])', r"=\1", tag_content)

            return tag_content

        return re.sub(r"<[a-zA-Z0-9_-]+(\s+[^>]*?)?>", tag_repl, html)

    def _compact_whitespace(self, html: str) -> str:
        # Collapse multiple whitespace characters into a single space
        html = re.sub(r"\s+", " ", html)

        # Remove spaces immediately surrounding tags where safe
        html = re.sub(r">\s+<", "><", html)
        html = re.sub(r"\s+>", ">", html)
        html = re.sub(r"<\s+", "<", html)

        return html

    def _shorten_doctype(self, html: str) -> str:
        return re.sub(
            r"<!DOCTYPE[^>]*>", "<!DOCTYPE html>", html, count=1, flags=re.IGNORECASE
        )

    def _restore_verbatim_tags(self, html: str) -> str:
        for token_id, original in self.literal_table.items():
            html = html.replace(token_id, original)
        return html
