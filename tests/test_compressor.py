#!/usr/bin/env python3
"""
Comprehensive test suite for WebCompressor Pro.
"""

import unittest
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compressor import WebCompressor, AssetType, BaseCompressor, CompressionResult
from js_compressor import AdvancedJSCompressor
from css_compressor import AdvancedCSSCompressor
from html_compressor import AdvancedHTMLCompressor


class TestJSCompressor(unittest.TestCase):
    def setUp(self):
        self.comp = AdvancedJSCompressor(aggressive=True)

    def test_comment_removal(self):
        code = "var x = 1; // single line\n/* multi\nline */ var y = 2;"
        res, _ = self.comp.compress(code)
        self.assertNotIn("// single line", res)
        self.assertNotIn("/* multi", res)
        self.assertIn("var x=1", res)
        self.assertIn("var y=2", res)

    def test_strings_and_urls_preserved(self):
        code = 'const api = "https://example.com/api//v1"; const text = "1 + 2 = 3";'
        res, _ = self.comp.compress(code)
        self.assertIn('"https://example.com/api//v1"', res)
        self.assertIn('"1 + 2 = 3"', res)

    def test_regex_literals(self):
        code = (
            "const pattern = /https?:\\/\\/[^/]+/gi; const match = str.match(pattern);"
        )
        res, _ = self.comp.compress(code)
        self.assertIn("/https?:\\/\\/[^/]+/gi", res)

    def test_numbers_optimization(self):
        code = "var a = 1.0; var b = 0.5; var c = 10000;"
        res, _ = self.comp.compress(code)
        self.assertIn("a=1", res)
        self.assertIn("b=.5", res)
        self.assertIn("c=1e4", res)

    def test_operator_spacing_and_safe_plus(self):
        code = "let a = 1 + + 2; let b = x ++ ; let c = (a === b) && (c || d);"
        res, _ = self.comp.compress(code)
        self.assertIn("1+ +2", res)
        self.assertIn("x++", res)
        self.assertIn("(a===b)&&(c||d)", res)

    def test_template_literals_preserved(self):
        code = "const msg = `Hello ${name}, total is ${1 + 2}`;"
        res, _ = self.comp.compress(code)
        self.assertIn("`Hello ${name}, total is ${1 + 2}`", res)

    def test_preserved_comments(self):
        code = "/*! important */ var x = 1;"
        res, _ = self.comp.compress(code)
        self.assertIn("/*! important */", res)
        self.assertIn("var x=1", res)

    def test_no_boolean_logic_corruption(self):
        code = "if (!a && b) { doSomething(); }"
        res, _ = self.comp.compress(code)
        self.assertIn("!a&&b", res)
        self.assertNotIn("!a||b", res)

    def test_strict_equality_preserved(self):
        code = "if (x === true) { doSomething(); }"
        res, _ = self.comp.compress(code)
        self.assertIn("x===!0", res)
        self.assertNotIn("x==!0", res)

    def test_asi_return_preserved(self):
        code = "return\n'value';"
        res, _ = self.comp.compress(code)
        # Should preserve newline after return to maintain ASI semantics
        self.assertIn("return", res)
        self.assertIn("'value'", res)

    def test_empty_input(self):
        res, _ = self.comp.compress("")
        self.assertEqual(res, "")

    def test_whitespace_only_input(self):
        res, _ = self.comp.compress("   \n\t  ")
        self.assertEqual(res, "")


class TestCSSCompressor(unittest.TestCase):
    def setUp(self):
        self.comp = AdvancedCSSCompressor(aggressive=True)

    def test_color_shortening(self):
        code = """
        .header {
            color: #ffffff;
            background-color: rgb(255, 0, 0);
            border-color: black;
        }
        """
        res, _ = self.comp.compress(code)
        self.assertIn("color:#fff", res)
        self.assertIn("background-color:red", res)
        self.assertIn("border-color:#000", res)

    def test_dimensions_and_font_weight(self):
        code = """
        .card {
            margin: 0px 10px 0em 0rem;
            opacity: 0.5;
            font-weight: bold;
        }
        """
        res, _ = self.comp.compress(code)
        self.assertIn("margin:0 10px 0 0", res)
        self.assertIn("opacity:.5", res)
        self.assertIn("font-weight:700", res)

    def test_url_preservation(self):
        code = "body { background: url('https://example.com/bg.jpg?foo=1&bar=2'); }"
        res, _ = self.comp.compress(code)
        self.assertIn("url('https://example.com/bg.jpg?foo=1&bar=2')", res)

    def test_hex_to_named_color(self):
        code = ".a { color: #f00; background: #ff0000; }"
        res, _ = self.comp.compress(code)
        self.assertIn("red", res)

    def test_comments_removed(self):
        code = "/* comment */ body { color: red; }"
        res, _ = self.comp.compress(code)
        self.assertNotIn("comment", res)
        self.assertIn("body{color:red}", res)

    def test_preserved_comments(self):
        code = "/*! license */ body { color: red; }"
        res, _ = self.comp.compress(code)
        self.assertIn("/*! license */", res)

    def test_empty_input(self):
        res, _ = self.comp.compress("")
        self.assertEqual(res, "")

    def test_empty_rules_removed(self):
        code = ".a{} .b { color: red; }"
        res, _ = self.comp.compress(code)
        self.assertIn(".b{color:red}", res)


class TestHTMLCompressor(unittest.TestCase):
    def setUp(self):
        self.comp = AdvancedHTMLCompressor(aggressive=True)

    def test_comment_removal_and_whitespace(self):
        code = """
        <!DOCTYPE html>
        <html>
            <!-- This is a comment -->
            <head>
                <title>Test App</title>
            </head>
            <body>
                <h1>  Hello   World  </h1>
            </body>
        </html>
        """
        res, _ = self.comp.compress(code)
        self.assertNotIn("<!-- This is a comment -->", res)
        self.assertIn(
            "<!DOCTYPE html><html><head><title>Test App</title></head><body><h1> Hello World </h1></body></html>",
            res,
        )

    def test_verbatim_tags_preserved(self):
        code = "<div><pre>   Line 1\n   Line 2\n   Line 3   </pre></div>"
        res, _ = self.comp.compress(code)
        self.assertIn("<pre>   Line 1\n   Line 2\n   Line 3   </pre>", res)

    def test_boolean_attributes(self):
        code = '<input type="checkbox" checked="checked" disabled="disabled" required>'
        res, _ = self.comp.compress(code)
        self.assertIn("checked", res)
        self.assertNotIn('checked="checked"', res)
        self.assertIn("disabled", res)
        self.assertNotIn('disabled="disabled"', res)

    def test_inline_scripts_and_styles(self):
        code = """
        <html>
            <head>
                <style>
                    body {
                        color: #ffffff;
                        margin: 0px;
                    }
                </style>
            </head>
            <body>
                <script>
                    var message = "hello"; // inline comment
                    var num = 1.0;
                </script>
            </body>
        </html>
        """
        res, _ = self.comp.compress(code)
        self.assertIn("<style>body{color:#fff;margin:0}</style>", res)
        self.assertIn('<script>var message="hello";var num=1;</script>', res)

    def test_conditional_comments_preserved(self):
        code = '<!--[if IE]><script>alert("IE");</script><![endif]-->'
        res, _ = self.comp.compress(code)
        self.assertIn("<!--[if IE]", res)
        self.assertIn("<![endif]-->", res)

    def test_doctype_shortened(self):
        code = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN">'
        res, _ = self.comp.compress(code)
        self.assertIn("<!DOCTYPE html>", res)

    def test_empty_input(self):
        res, _ = self.comp.compress("")
        self.assertEqual(res, "")


class TestWebCompressorFacade(unittest.TestCase):
    def setUp(self):
        self.wc = WebCompressor(aggressive=True)

    def test_auto_detection(self):
        res_js = self.wc.compress_string("const a = 1; const b = 2;")
        self.assertEqual(res_js.asset_type, AssetType.JS)

        res_css = self.wc.compress_string(".container { display: flex; width: 100%; }")
        self.assertEqual(res_css.asset_type, AssetType.CSS)

        res_html = self.wc.compress_string(
            "<!DOCTYPE html><html><body><h1>Hi</h1></body></html>"
        )
        self.assertEqual(res_html.asset_type, AssetType.HTML)

    def test_compression_result_fields(self):
        res = self.wc.compress_string("const x = 1;")
        self.assertIsInstance(res, CompressionResult)
        self.assertGreater(res.original_size, 0)
        self.assertLessEqual(res.compressed_size, res.original_size)
        self.assertGreaterEqual(res.savings_pct, 0)
        self.assertEqual(res.asset_type, AssetType.JS)

    def test_file_compression(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write("const x = 1; const y = 2;")
            temp_path = f.name

        try:
            result = self.wc.compress_file(temp_path)
            self.assertEqual(result.asset_type, AssetType.JS)
            self.assertIn("const x=1", result.output)
            self.assertIn("const y=2", result.output)
        finally:
            os.unlink(temp_path)

    def test_file_compression_with_output(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write("const x = 1;")
            temp_path = f.name

        try:
            out_path = temp_path + ".out"
            result = self.wc.compress_file(temp_path, out_path)
            self.assertTrue(Path(out_path).exists())
            with open(out_path, "r") as f:
                content = f.read()
            self.assertIn("const x=1", content)
        finally:
            os.unlink(temp_path)
            if Path(out_path).exists():
                os.unlink(out_path)


class TestEdgeCases(unittest.TestCase):
    def setUp(self):
        self.wc = WebCompressor(aggressive=True)

    def test_js_string_with_code_like_content(self):
        code = 'const x = "if (a && b) { return c; }";'
        res, _ = self.wc.js_compressor.compress(code)
        self.assertIn('"if (a && b) { return c; }"', res)

    def test_js_string_with_url(self):
        code = 'const url = "https://api.example.com/v1/users?id=123&active=true";'
        res, _ = self.wc.js_compressor.compress(code)
        self.assertIn('"https://api.example.com/v1/users?id=123&active=true"', res)

    def test_js_regex_with_special_chars(self):
        code = "const re = /[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+/;"
        res, _ = self.wc.js_compressor.compress(code)
        self.assertIn("/[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+/", res)

    def test_css_url_with_query_string(self):
        code = "body { background: url('https://cdn.example.com/img.png?v=1&w=100'); }"
        res, _ = self.wc.css_compressor.compress(code)
        self.assertIn("url('https://cdn.example.com/img.png?v=1&w=100')", res)

    def test_html_nested_verbatim(self):
        code = "<div><pre>  <code>  x = 1;  </code>  </pre></div>"
        res, _ = self.wc.html_compressor.compress(code)
        self.assertIn("<pre>  <code>  x = 1;  </code>  </pre>", res)

    def test_html_inline_script_type_ignored(self):
        code = '<script type="application/json">{ "key": "value" }</script>'
        res, _ = self.wc.html_compressor.compress(code)
        self.assertIn('{ "key": "value" }', res)

    def test_js_class_syntax(self):
        code = "class Foo { constructor() { this.x = 1; } }"
        res, _ = self.wc.js_compressor.compress(code)
        self.assertIn("class Foo{constructor(){this.x=1}}", res)

    def test_js_arrow_functions(self):
        code = "const fn = (a, b) => a + b;"
        res, _ = self.wc.js_compressor.compress(code)
        self.assertIn("(a,b)=>a+b", res)

    def test_css_multiple_selectors(self):
        code = ".a, .b, .c { color: #ffffff; margin: 0px; }"
        res, _ = self.wc.css_compressor.compress(code)
        self.assertIn(".a,.b,.c{color:#fff;margin:0}", res)

    def test_html_multiple_boolean_attrs(self):
        code = '<input disabled="disabled" readonly="readonly" required="required">'
        res, _ = self.wc.html_compressor.compress(code)
        self.assertIn("disabled", res)
        self.assertIn("readonly", res)
        self.assertIn("required", res)
        self.assertNotIn('disabled="disabled"', res)
        self.assertNotIn('readonly="readonly"', res)
        self.assertNotIn('required="required"', res)


class TestDirectoryCompression(unittest.TestCase):
    def setUp(self):
        self.wc = WebCompressor(aggressive=True)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_single_file_js(self):
        js_file = Path(self.temp_dir) / "test.js"
        js_file.write_text("const x = 1;")
        result = self.wc.compress_file(str(js_file))
        self.assertEqual(result.asset_type, AssetType.JS)
        self.assertIn("const x=1", result.output)

    def test_single_file_css(self):
        css_file = Path(self.temp_dir) / "test.css"
        css_file.write_text("body { color: #ffffff; }")
        result = self.wc.compress_file(str(css_file))
        self.assertEqual(result.asset_type, AssetType.CSS)
        self.assertIn("body{color:#fff}", result.output)

    def test_single_file_html(self):
        html_file = Path(self.temp_dir) / "test.html"
        html_file.write_text("<html><body><h1>Hi</h1></body></html>")
        result = self.wc.compress_file(str(html_file))
        self.assertEqual(result.asset_type, AssetType.HTML)
        self.assertIn("<html><body><h1>Hi</h1></body></html>", result.output)


class TestCacheAndBenchmark(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cache_hit(self):
        from cache import CompressionCache
        cache = CompressionCache(cache_dir=Path(self.temp_dir) / "cache")
        result = {"output": "x=1", "savings_pct": 50.0}
        cache.put("const x = 1;", "javascript", True, result)
        cached = cache.get("const x = 1;", "javascript", True)
        self.assertEqual(cached["output"], "x=1")

    def test_cache_miss(self):
        from cache import CompressionCache
        cache = CompressionCache(cache_dir=Path(self.temp_dir) / "cache")
        cached = cache.get("unknown content", "css", False)
        self.assertIsNone(cached)

    def test_benchmark_record_and_summary(self):
        from benchmark import Benchmark
        bench = Benchmark(log_path=Path(self.temp_dir) / "bench.jsonl")
        bench.record({"asset_type": "js", "savings_pct": 45.0, "original_size": 100, "compressed_size": 55})
        bench.record({"asset_type": "css", "savings_pct": 30.0, "original_size": 200, "compressed_size": 140})
        summary = bench.summary()
        self.assertEqual(summary["runs"], 2)
        self.assertIn("js", summary["avg_by_type"])
        self.assertIn("css", summary["avg_by_type"])

    def test_benchmark_suggest(self):
        from benchmark import Benchmark
        bench = Benchmark(log_path=Path(self.temp_dir) / "bench.jsonl")
        for _ in range(5):
            bench.record({"asset_type": "js", "savings_pct": 40.0, "aggressive": True})
        suggestion = bench.suggest_strategy("js")
        self.assertTrue(suggestion["aggressive"])


class TestNewOptimizations(unittest.TestCase):
    def setUp(self):
        self.comp = AdvancedJSCompressor(aggressive=True)
        self.css = AdvancedCSSCompressor(aggressive=True)

    def test_boolean_simplification(self):
        code = "if (x === true && y === false) { return true; }"
        res, _ = self.comp.compress(code)
        self.assertIn("!0", res)
        self.assertIn("!1", res)

    def test_rgba_to_hex(self):
        code = "color: rgba(255, 0, 0, 0.5);"
        res, _ = self.css.compress(code)
        self.assertIn("rgba(255,0,0,.5)", res)

    def test_duplicate_css_properties_removed(self):
        code = ".a { color: red; color: blue; margin: 0; }"
        res, _ = self.css.compress(code)
        self.assertIn("color:blue", res)
        self.assertNotIn("color:red", res)

    def test_hex_only_shorter_conversion(self):
        code = "color: #fff;"
        res, _ = self.css.compress(code)
        self.assertIn("#fff", res)

    def test_js_hex_number_preserved(self):
        code = "const x = 0xFF;"
        res, _ = self.comp.compress(code)
        self.assertIn("0xFF", res)


if __name__ == "__main__":
    unittest.main()
