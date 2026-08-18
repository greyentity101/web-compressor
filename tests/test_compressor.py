#!/usr/bin/env python3
"""
Tests for WebCompressor Pro.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from compressor import (
    JSCompressor,
    CSSCompressor,
    HTMLCompressor,
    WebCompressor,
    AssetType,
)
from js_compressor import AdvancedJSCompressor
from css_compressor import AdvancedCSSCompressor
from html_compressor import AdvancedHTMLCompressor


class TestJSCompressor(unittest.TestCase):
    def setUp(self):
        self.comp = AdvancedJSCompressor(aggressive=True)

    def test_comment_removal(self):
        code = "var x = 1; // this is a comment\nvar y = 2;"
        result, _ = self.comp.compress(code)
        self.assertNotIn("//", result)
        self.assertIn("var x=1", result)

    def test_whitespace_removal(self):
        code = "var x = 1 + 2;"
        result, _ = self.comp.compress(code)
        self.assertIn("1+2", result)

    def test_number_shortening(self):
        code = "var x = 1.0;"
        result, _ = self.comp.compress(code)
        self.assertIn("var x=1", result)

    def test_boolean_simplification(self):
        code = "var x = !!y;"
        result, _ = self.comp.compress(code)
        self.assertIn("var x=y", result)

    def test_constant_folding(self):
        code = "var x = 1 + 2;"
        result, _ = self.comp.compress(code)
        self.assertIn("3", result)

    def test_empty_removal(self):
        code = "var x = 1;; var y = 2;"
        result, _ = self.comp.compress(code)
        self.assertNotIn(";;", result)


class TestCSSCompressor(unittest.TestCase):
    def setUp(self):
        self.comp = AdvancedCSSCompressor(aggressive=True)

    def test_comment_removal(self):
        code = "/* comment */ body { color: red; }"
        result, _ = self.comp.compress(code)
        self.assertNotIn("/*", result)
        self.assertIn("body{color:red}", result)

    def test_color_optimization(self):
        code = "body { color: white; }"
        result, _ = self.comp.compress(code)
        self.assertIn("#fff", result)

    def test_zero_shortening(self):
        code = "body { margin: 0px; padding: 0em; }"
        result, _ = self.comp.compress(code)
        self.assertIn("margin:0", result)
        self.assertIn("padding:0", result)

    def test_duplicate_selector_merge(self):
        code = "body { color: red; } body { font-size: 12px; }"
        result, _ = self.comp.compress(code)
        self.assertEqual(result.count("body"), 1)
        self.assertIn("color:red", result)
        self.assertIn("font-size:12px", result)


class TestHTMLCompressor(unittest.TestCase):
    def setUp(self):
        self.comp = AdvancedHTMLCompressor(aggressive=True)

    def test_comment_removal(self):
        code = "<!-- comment --><div>test</div>"
        result, _ = self.comp.compress(code)
        self.assertNotIn("<!--", result)
        self.assertIn("<div>test</div>", result)

    def test_whitespace_collapse(self):
        code = "<div>   <span>test</span>   </div>"
        result, _ = self.comp.compress(code)
        self.assertIn("><span>", result)

    def test_doctype_shorten(self):
        code = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN">'
        result, _ = self.comp.compress(code)
        self.assertIn("<!DOCTYPE html>", result)


class TestWebCompressor(unittest.TestCase):
    def setUp(self):
        self.comp = WebCompressor(aggressive=True)

    def test_js_detection(self):
        code = "var x = 1;"
        self.assertEqual(self.comp._detect_type(code, "test.js"), AssetType.JS)

    def test_css_detection(self):
        code = "body { color: red; }"
        self.assertEqual(self.comp._detect_type(code, "test.css"), AssetType.CSS)

    def test_html_detection(self):
        code = "<!DOCTYPE html><html><body>test</body></html>"
        self.assertEqual(self.comp._detect_type(code, "test.html"), AssetType.HTML)


class TestCompressionRatio(unittest.TestCase):
    """Ensure compression actually reduces size."""

    def test_js_compression_ratio(self):
        comp = AdvancedJSCompressor(aggressive=True)
        code = """
        // This is a comment
        function helloWorld() {
            var message = "Hello, World!";
            console.log(message);
            return message;
        }
        var x = true;
        var y = false;
        var z = 1.0;
        var a = 1 + 2;
        """
        result, _ = comp.compress(code)
        self.assertLess(len(result), len(code) * 0.8)

    def test_css_compression_ratio(self):
        comp = AdvancedCSSCompressor(aggressive=True)
        code = """
        /* Main styles */
        body {
            color: white;
            margin: 0px;
            padding: 0em;
            font-size: 16px;
        }
        .container {
            color: white;
            margin: 0px;
        }
        """
        result, _ = comp.compress(code)
        self.assertLess(len(result), len(code) * 0.8)


if __name__ == "__main__":
    unittest.main()
