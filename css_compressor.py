#!/usr/bin/env python3
"""
CSS-specific compression engine with color, unit, and selector optimizations.
"""

import re
from typing import Tuple, List, Dict
from compressor import BaseCompressor, AssetType


class AdvancedCSSCompressor(BaseCompressor):
    """Production-grade CSS compressor with semantic optimizations."""

    # Complete named colors -> shortest hex
    COLOR_MAP = {
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
        "darkblue": "#00008b",
        "darkcyan": "#008b8b",
        "darkgoldenrod": "#b8860b",
        "darkgray": "#a9a9a9",
        "darkgreen": "#006400",
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
        "darkturquoise": "#00ced1",
        "darkviolet": "#9400d3",
        "deeppink": "#ff1493",
        "deepskyblue": "#00bfff",
        "dimgray": "#696969",
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
        "lightpink": "#ffb6c1",
        "lightsalmon": "#ffa07a",
        "lightseagreen": "#20b2aa",
        "lightskyblue": "#87cefa",
        "lightslategray": "#778899",
        "lightsteelblue": "#b0c4de",
        "lightyellow": "#ffffe0",
        "lime": "#0f0",
        "limegreen": "#32cd32",
        "linen": "#faf0e6",
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
    }

    # Comprehensive hex -> shorter named color (only when shorter)
    HEX_TO_NAME = {
        "#f00": "red",
        "#ff0000": "red",
        "#000080": "navy",
        "#800000": "maroon",
        "#808000": "olive",
        "#800080": "purple",
        "#008080": "teal",
        "#c0c0c0": "silver",
        "#808080": "gray",
        "#a52a2a": "brown",
        "#ffa500": "orange",
        "#ffc0cb": "pink",
        "#ff6347": "tomato",
        "#ffff00": "yellow",
        "#00ff00": "lime",
        "#008000": "green",
        "#0000ff": "blue",
        "#000000": "black",
        "#ffffff": "white",
        "#f5f5dc": "beige",
        "#ffe4c4": "bisque",
        "#ffebcd": "blanchedalmond",
        "#f0ffff": "azure",
        "#f0f8ff": "aliceblue",
        "#fffaf0": "floralwhite",
        "#f5fffa": "mintcream",
        "#f8f8ff": "ghostwhite",
        "#fff0f5": "lavenderblush",
        "#f0fff0": "honeydew",
        "#fffff0": "ivory",
        "#f5f5f5": "whitesmoke",
        "#fff5ee": "seashell",
        "#faf0e6": "linen",
        "#fdf5e6": "oldlace",
        "#fff8dc": "cornsilk",
        "#fffacd": "lemonchiffon",
        "#ffe4e1": "mistyrose",
        "#ffe4b5": "moccasin",
        "#ffdead": "navajowhite",
        "#ffefd5": "papayawhip",
        "#ffdab9": "peachpuff",
        "#f0e68c": "khaki",
        "#bdb76b": "darkkhaki",
        "#f4a460": "sandybrown",
        "#d2b48c": "tan",
        "#d8bfd8": "thistle",
        "#e6e6fa": "lavender",
        "#dda0dd": "plum",
        "#ee82ee": "violet",
        "#da70d6": "orchid",
        "#ba55d3": "mediumorchid",
        "#9932cc": "darkorchid",
        "#9400d3": "darkviolet",
        "#8a2be2": "blueviolet",
        "#8b008b": "darkmagenta",
        "#8b4513": "saddlebrown",
        "#a0522d": "sienna",
        "#bc8f8f": "rosybrown",
        "#cd853f": "peru",
        "#d2691e": "chocolate",
        "#b8860b": "darkgoldenrod",
        "#daa520": "goldenrod",
        "#ffd700": "gold",
        "#adff2f": "greenyellow",
        "#32cd32": "limegreen",
        "#90ee90": "lightgreen",
        "#98fb98": "palegreen",
        "#00fa9a": "mediumspringgreen",
        "#00ff7f": "springgreen",
        "#2e8b57": "seagreen",
        "#228b22": "forestgreen",
        "#006400": "darkgreen",
        "#9acd32": "yellowgreen",
        "#6b8e23": "olivedrab",
        "#556b2f": "darkolivegreen",
        "#808000": "olive",
        "#3cb371": "mediumseagreen",
        "#20b2aa": "lightseagreen",
        "#008b8b": "darkcyan",
        "#00ced1": "darkturquoise",
        "#48d1cc": "mediumturquoise",
        "#40e0d0": "turquoise",
        "#00ffff": "cyan",
        "#e0ffff": "lightcyan",
        "#afeeee": "paleturquoise",
        "#7fffd4": "aquamarine",
        "#66cdaa": "mediumaquamarine",
        "#00bfff": "deepskyblue",
        "#87ceeb": "skyblue",
        "#87cefa": "lightskyblue",
        "#add8e6": "lightblue",
        "#b0e0e6": "powderblue",
        "#b0c4de": "lightsteelblue",
        "#6495ed": "cornflowerblue",
        "#4169e1": "royalblue",
        "#191970": "midnightblue",
        "#00008b": "darkblue",
        "#0000cd": "mediumblue",
        "#4682b4": "steelblue",
        "#5f9ea0": "cadetblue",
        "#483d8b": "darkslateblue",
        "#7b68ee": "mediumslateblue",
        "#6a5acd": "slateblue",
        "#9370db": "mediumpurple",
        "#663399": "rebeccapurple",
        "#c71585": "mediumvioletred",
        "#db7093": "palevioletred",
        "#ff1493": "deeppink",
        "#ff69b4": "hotpink",
        "#ffb6c1": "lightpink",
        "#ffa07a": "lightsalmon",
        "#fa8072": "salmon",
        "#e9967a": "darksalmon",
        "#f08080": "lightcoral",
        "#cd5c5c": "indianred",
        "#b22222": "firebrick",
        "#8b0000": "darkred",
        "#dc143c": "crimson",
        "#ff4500": "orangered",
        "#ff8c00": "darkorange",
        "#ffd700": "gold",
        "#ff7f50": "coral",
        "#eee8aa": "palegoldenrod",
        "#fafad2": "lightgoldenrodyellow",
        "#f0e68c": "khaki",
        "#ffffe0": "lightyellow",
        "#fffafa": "snow",
        "#f5deb3": "wheat",
        "#deb887": "burlywood",
        "#d3d3d3": "lightgray",
        "#a9a9a9": "darkgray",
        "#696969": "dimgray",
        "#708090": "slategray",
        "#c0c0c0": "silver",
        "#dcdcdc": "gainsboro",
        "#f5f5f5": "whitesmoke",
        "#fff8dc": "cornsilk",
        "#fffacd": "lemonchiffon",
        "#ffe4b5": "moccasin",
        "#ffdead": "navajowhite",
        "#ffefd5": "papayawhip",
        "#ffdab9": "peachpuff",
        "#ffe4c4": "bisque",
        "#ffe4e1": "mistyrose",
        "#f0fff0": "honeydew",
        "#f0ffff": "azure",
        "#f0f8ff": "aliceblue",
        "#f8f8ff": "ghostwhite",
        "#fff0f5": "lavenderblush",
        "#fffff0": "ivory",
        "#fffaf0": "floralwhite",
        "#f5fffa": "mintcream",
        "#fdf5e6": "oldlace",
        "#faf0e6": "linen",
        "#fff5ee": "seashell",
        "#f5deb3": "wheat",
        "#e6e6fa": "lavender",
        "#d8bfd8": "thistle",
        "#dda0dd": "plum",
        "#ee82ee": "violet",
        "#da70d6": "orchid",
        "#ba55d3": "mediumorchid",
        "#9932cc": "darkorchid",
        "#9400d3": "darkviolet",
        "#8a2be2": "blueviolet",
        "#8b008b": "darkmagenta",
        "#8b4513": "saddlebrown",
        "#a0522d": "sienna",
        "#bc8f8f": "rosybrown",
        "#cd853f": "peru",
        "#d2691e": "chocolate",
        "#b8860b": "darkgoldenrod",
        "#daa520": "goldenrod",
        "#ffd700": "gold",
        "#adff2f": "greenyellow",
        "#32cd32": "limegreen",
        "#90ee90": "lightgreen",
        "#98fb98": "palegreen",
        "#00fa9a": "mediumspringgreen",
        "#00ff7f": "springgreen",
        "#2e8b57": "seagreen",
        "#228b22": "forestgreen",
        "#006400": "darkgreen",
        "#9acd32": "yellowgreen",
        "#6b8e23": "olivedrab",
        "#556b2f": "darkolivegreen",
        "#3cb371": "mediumseagreen",
        "#20b2aa": "lightseagreen",
        "#008b8b": "darkcyan",
        "#00ced1": "darkturquoise",
        "#48d1cc": "mediumturquoise",
        "#40e0d0": "turquoise",
        "#7fffd4": "aquamarine",
        "#66cdaa": "mediumaquamarine",
        "#00bfff": "deepskyblue",
        "#87ceeb": "skyblue",
        "#87cefa": "lightskyblue",
        "#add8e6": "lightblue",
        "#b0e0e6": "powderblue",
        "#b0c4de": "lightsteelblue",
        "#6495ed": "cornflowerblue",
        "#4169e1": "royalblue",
        "#191970": "midnightblue",
        "#00008b": "darkblue",
        "#0000cd": "mediumblue",
        "#4682b4": "steelblue",
        "#5f9ea0": "cadetblue",
        "#483d8b": "darkslateblue",
        "#7b68ee": "mediumslateblue",
        "#6a5acd": "slateblue",
        "#9370db": "mediumpurple",
        "#663399": "rebeccapurple",
        "#c71585": "mediumvioletred",
        "#db7093": "palevioletred",
        "#ff1493": "deeppink",
        "#ff69b4": "hotpink",
        "#ffb6c1": "lightpink",
        "#ffa07a": "lightsalmon",
        "#fa8072": "salmon",
        "#e9967a": "darksalmon",
        "#f08080": "lightcoral",
        "#cd5c5c": "indianred",
        "#b22222": "firebrick",
        "#8b0000": "darkred",
        "#dc143c": "crimson",
        "#ff4500": "orangered",
        "#ff8c00": "darkorange",
        "#ff7f50": "coral",
        "#eee8aa": "palegoldenrod",
        "#fafad2": "lightgoldenrodyellow",
        "#f0e68c": "khaki",
        "#ffffe0": "lightyellow",
        "#fffafa": "snow",
        "#f5deb3": "wheat",
        "#deb887": "burlywood",
        "#d3d3d3": "lightgray",
        "#a9a9a9": "darkgray",
        "#696969": "dimgray",
        "#708090": "slategray",
        "#c0c0c0": "silver",
        "#dcdcdc": "gainsboro",
        "#f5f5f5": "whitesmoke",
        "#778899": "lightslategray",
        "#b0c4de": "lightsteelblue",
        "#708090": "slategray",
        "#778899": "lightslategray",
        "#2f4f4f": "darkslategray",
        "#2f4f4f": "darkslategrey",
        "#00ced1": "darkturquoise",
        "#48d1cc": "mediumturquoise",
        "#40e0d0": "turquoise",
        "#00ffff": "cyan",
        "#e0ffff": "lightcyan",
        "#afeeee": "paleturquoise",
        "#7fffd4": "aquamarine",
        "#66cdaa": "mediumaquamarine",
        "#00bfff": "deepskyblue",
        "#87ceeb": "skyblue",
        "#87cefa": "lightskyblue",
        "#add8e6": "lightblue",
        "#b0e0e6": "powderblue",
        "#6495ed": "cornflowerblue",
        "#4169e1": "royalblue",
        "#191970": "midnightblue",
        "#00008b": "darkblue",
        "#0000cd": "mediumblue",
        "#4682b4": "steelblue",
        "#5f9ea0": "cadetblue",
        "#483d8b": "darkslateblue",
        "#7b68ee": "mediumslateblue",
        "#6a5acd": "slateblue",
        "#9370db": "mediumpurple",
        "#663399": "rebeccapurple",
        "#c71585": "mediumvioletred",
        "#db7093": "palevioletred",
        "#ff1493": "deeppink",
        "#ff69b4": "hotpink",
        "#ffb6c1": "lightpink",
        "#ffa07a": "lightsalmon",
        "#fa8072": "salmon",
        "#e9967a": "darksalmon",
        "#f08080": "lightcoral",
        "#cd5c5c": "indianred",
        "#b22222": "firebrick",
        "#8b0000": "darkred",
        "#dc143c": "crimson",
        "#ff4500": "orangered",
        "#ff8c00": "darkorange",
        "#ff7f50": "coral",
        "#ffd700": "gold",
        "#daa520": "goldenrod",
        "#b8860b": "darkgoldenrod",
        "#d2691e": "chocolate",
        "#cd853f": "peru",
        "#bc8f8f": "rosybrown",
        "#a0522d": "sienna",
        "#8b4513": "saddlebrown",
        "#f4a460": "sandybrown",
        "#d2b48c": "tan",
        "#d8bfd8": "thistle",
        "#f5deb3": "wheat",
        "#fffafa": "snow",
        "#fff5ee": "seashell",
        "#faf0e6": "linen",
        "#fdf5e6": "oldlace",
        "#ffefd5": "papayawhip",
        "#ffdab9": "peachpuff",
        "#ffe4b5": "moccasin",
        "#ffdead": "navajowhite",
        "#ffe4e1": "mistyrose",
        "#f0e68c": "khaki",
        "#f0ffff": "azure",
        "#f0f8ff": "aliceblue",
        "#f8f8ff": "ghostwhite",
        "#fff0f5": "lavenderblush",
        "#fffff0": "ivory",
        "#f0fff0": "honeydew",
        "#fff8dc": "cornsilk",
        "#fffacd": "lemonchiffon",
        "#fffaf0": "floralwhite",
        "#f5fffa": "mintcream",
        "#f5f5f5": "whitesmoke",
        "#f5f5dc": "beige",
        "#e6e6fa": "lavender",
        "#dda0dd": "plum",
        "#ee82ee": "violet",
        "#da70d6": "orchid",
        "#ba55d3": "mediumorchid",
        "#9932cc": "darkorchid",
        "#9400d3": "darkviolet",
        "#8a2be2": "blueviolet",
        "#8b008b": "darkmagenta",
        "#8b4513": "saddlebrown",
        "#a0522d": "sienna",
        "#bc8f8f": "rosybrown",
        "#cd853f": "peru",
        "#d2691e": "chocolate",
        "#b8860b": "darkgoldenrod",
        "#daa520": "goldenrod",
        "#ffd700": "gold",
        "#adff2f": "greenyellow",
        "#32cd32": "limegreen",
        "#90ee90": "lightgreen",
        "#98fb98": "palegreen",
        "#00fa9a": "mediumspringgreen",
        "#00ff7f": "springgreen",
        "#2e8b57": "seagreen",
        "#228b22": "forestgreen",
        "#006400": "darkgreen",
        "#9acd32": "yellowgreen",
        "#6b8e23": "olivedrab",
        "#556b2f": "darkolivegreen",
        "#808000": "olive",
        "#3cb371": "mediumseagreen",
        "#20b2aa": "lightseagreen",
        "#008b8b": "darkcyan",
        "#00ced1": "darkturquoise",
        "#48d1cc": "mediumturquoise",
        "#40e0d0": "turquoise",
        "#00ffff": "cyan",
        "#e0ffff": "lightcyan",
        "#afeeee": "paleturquoise",
        "#7fffd4": "aquamarine",
        "#66cdaa": "mediumaquamarine",
        "#00bfff": "deepskyblue",
        "#87ceeb": "skyblue",
        "#87cefa": "lightskyblue",
        "#add8e6": "lightblue",
        "#b0e0e6": "powderblue",
        "#6495ed": "cornflowerblue",
        "#4169e1": "royalblue",
        "#191970": "midnightblue",
        "#00008b": "darkblue",
        "#0000cd": "mediumblue",
        "#4682b4": "steelblue",
        "#5f9ea0": "cadetblue",
        "#483d8b": "darkslateblue",
        "#7b68ee": "mediumslateblue",
        "#6a5acd": "slateblue",
        "#9370db": "mediumpurple",
        "#663399": "rebeccapurple",
        "#c71585": "mediumvioletred",
        "#db7093": "palevioletred",
        "#ff1493": "deeppink",
        "#ff69b4": "hotpink",
        "#ffb6c1": "lightpink",
        "#ffa07a": "lightsalmon",
        "#fa8072": "salmon",
        "#e9967a": "darksalmon",
        "#f08080": "lightcoral",
        "#cd5c5c": "indianred",
        "#b22222": "firebrick",
        "#8b0000": "darkred",
        "#dc143c": "crimson",
        "#ff4500": "orangered",
        "#ff8c00": "darkorange",
        "#ff7f50": "coral",
    }

    # Build reverse map: hex -> shortest name
    _REVERSE_COLOR_MAP: Dict[str, str] = {}
    for _name, _hex in COLOR_MAP.items():
        _h = _hex.lower()
        if _h not in _REVERSE_COLOR_MAP or len(_name) < len(_REVERSE_COLOR_MAP[_h]):
            _REVERSE_COLOR_MAP[_h] = _name

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

        # Pass 1: Extract string literals and url(...) blocks to protect them
        css = self._extract_literals(content)

        # Pass 2: Strip comments
        css = self._strip_comments(css)

        # Pass 3: Optimize colors
        css = self._optimize_colors(css)

        # Pass 4: Optimize zero dimensions and decimals
        css = self._optimize_dimensions(css)

        # Pass 5: Optimize font-weight
        css = self._optimize_font_weights(css)

        # Pass 6: Strip vendor prefixes (aggressive only)
        css = self._strip_vendor_prefixes(css)

        # Pass 7: Remove duplicate properties (aggressive only)
        css = self._remove_duplicate_properties(css)

        # Pass 8: Compact whitespace and structure
        css = self._compact_structure(css)

        # Pass 9: Restore literals
        css = self._restore_literals(css)

        return css.strip(), self.warnings

    def _extract_literals(self, text: str) -> str:
        """Extract strings and url(...) contents."""
        result = []
        i = 0
        n = len(text)

        while i < n:
            ch = text[i]

            # Strings
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
                    j += 1
                token_id = f"___CSS_LIT_{self.literal_counter}___"
                self.literal_counter += 1
                self.literal_table[token_id] = text[i:j]
                result.append(token_id)
                i = j
                continue

            # url(...)
            if text[i : i + 4].lower() == "url(":
                j = i + 4
                while j < n and text[j] != ")":
                    if text[j] == "\\":
                        j += 2
                        continue
                    j += 1
                if j < n and text[j] == ")":
                    j += 1
                token_id = f"___CSS_LIT_{self.literal_counter}___"
                self.literal_counter += 1
                self.literal_table[token_id] = text[i:j]
                result.append(token_id)
                i = j
                continue

            result.append(ch)
            i += 1

        return "".join(result)

    def _strip_comments(self, css: str) -> str:
        # Preserve special comments /*! ... */
        def comment_repl(m):
            comment = m.group(0)
            if comment.startswith("/*!"):
                token_id = f"___CSS_LIT_{self.literal_counter}___"
                self.literal_counter += 1
                self.literal_table[token_id] = comment
                return token_id
            return " "

        return re.sub(r"/\*[\s\S]*?\*/", comment_repl, css)

    def _optimize_colors(self, css: str) -> str:
        # Split into rule blocks to avoid touching selectors
        # We only convert colors inside declarations (after ':')
        def process_rule(m):
            rule = m.group(0)
            # Only process the declarations part (inside { ... })
            decl_match = re.search(r"\{([^{}]*)\}", rule, re.DOTALL)
            if not decl_match:
                return rule
            declarations = decl_match.group(1)
            original_len = len(declarations)

            # Convert rgb(r, g, b) and rgba(r, g, b, a) to hex
            def rgb_repl(m):
                try:
                    r = int(m.group(1).strip())
                    g = int(m.group(2).strip())
                    b = int(m.group(3).strip())
                    alpha = m.group(4)
                    hex_str = f"#{r:02x}{g:02x}{b:02x}"
                    if (
                        hex_str[1] == hex_str[2]
                        and hex_str[3] == hex_str[4]
                        and hex_str[5] == hex_str[6]
                    ):
                        hex_str = f"#{hex_str[1]}{hex_str[3]}{hex_str[5]}"
                    result = self._REVERSE_COLOR_MAP.get(hex_str.lower(), hex_str)
                    if alpha:
                        result += alpha
                    return result
                except ValueError:
                    return m.group(0)

            declarations = re.sub(
                r"\brgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)",
                rgb_repl,
                declarations,
                flags=re.IGNORECASE,
            )

            # 6-digit hex to 3-digit hex or named color (only when shorter)
            def hex_repl(m):
                h = m.group(0).lower()
                if len(h) == 7 and h[1] == h[2] and h[3] == h[4] and h[5] == h[6]:
                    shorter = f"#{h[1]}{h[3]}{h[5]}"
                    candidate = self._REVERSE_COLOR_MAP.get(shorter, shorter)
                    return candidate if len(candidate) < len(shorter) else shorter
                candidate = self._REVERSE_COLOR_MAP.get(h, h)
                return candidate if len(candidate) < len(h) else h

            declarations = re.sub(r"#[0-9a-fA-F]{6}\b", hex_repl, declarations)

            # Named color conversion in property values only (only when hex is shorter)
            for name, hex_val in self.COLOR_MAP.items():
                if len(hex_val) < len(name):
                    declarations = re.sub(
                        rf"(?<=[:\s])\b{name}\b", hex_val, declarations, flags=re.IGNORECASE
                    )

            # Only replace if we actually changed something
            if len(declarations) < original_len:
                return rule[:decl_match.start(1)] + declarations + rule[decl_match.end(1):]
            return rule

        return re.sub(r"[^{}]*(?:\{[^{}]*\}[^{}]*)*", process_rule, css)

    def _optimize_dimensions(self, css: str) -> str:
        # 0px, 0em, 0rem, etc. -> 0 (safe zero units)
        # Keep 0% as-is for safety in flex/transitions contexts
        css = re.sub(
            r"(:\s*|\s+)\b0(?:px|em|rem|in|cm|mm|pc|pt|ex|ch|vh|vw|vmin|vmax|s|ms|deg|rad|grad|turn)\b",
            r"\g<1>0",
            css,
            flags=re.IGNORECASE,
        )

        # 0.5em -> .5em
        css = re.sub(r"(:\s*|\s+)0\.(\d+)", r"\g<1>.\2", css)

        return css

    def _optimize_font_weights(self, css: str) -> str:
        css = re.sub(
            r"\bfont-weight\s*:\s*normal\b", "font-weight:400", css, flags=re.IGNORECASE
        )
        css = re.sub(
            r"\bfont-weight\s*:\s*bold\b", "font-weight:700", css, flags=re.IGNORECASE
        )
        return css

    def _strip_vendor_prefixes(self, css: str) -> str:
        """Stub for vendor prefix removal (requires proper CSS parser for safety)."""
        return css

    def _remove_duplicate_properties(self, css: str) -> str:
        """Remove earlier duplicate properties, keeping the last declaration (browser behavior)."""
        if not self.aggressive:
            return css

        def dedupe_rule(m):
            rule = m.group(0)
            open_brace = rule.find("{")
            close_brace = rule.rfind("}")
            if open_brace == -1 or close_brace == -1:
                return rule
            selector = rule[:open_brace]
            declarations = rule[open_brace + 1 : close_brace]

            props = re.findall(r"([-\w]+\s*:\s*[^;]+;?)", declarations, re.IGNORECASE)
            if not props:
                return rule
            # Build set of duplicate names (appearing more than once)
            name_counts: dict[str, int] = {}
            for prop in props:
                name = prop.split(":")[0].strip().lower()
                name_counts[name] = name_counts.get(name, 0) + 1
            duplicates = {name for name, count in name_counts.items() if count > 1}
            # Keep last occurrence of each duplicate, all non-duplicates
            seen_dup: set[str] = set()
            keep = []
            for prop in reversed(props):
                name = prop.split(":")[0].strip().lower()
                if name in duplicates:
                    if name not in seen_dup:
                        seen_dup.add(name)
                        keep.append(prop)
                else:
                    keep.append(prop)
            # Reverse to restore original order (minus earlier duplicates)
            deduped = "".join(reversed(keep))
            return selector + "{" + deduped + "}"

        return re.sub(r"[^{}]+\{[^{}]+\}", dedupe_rule, css)

    def _compact_structure(self, css: str) -> str:
        # Collapse whitespace
        css = re.sub(r"\s+", " ", css)

        # Remove spaces around delimiters
        css = re.sub(r"\s*([{}();:,>~+])\s*", r"\1", css)

        # Remove trailing semicolons before }
        css = re.sub(r";\}", "}", css)

        # Remove empty rules: .a{} (non-greedy, non-nested-safe)
        css = re.sub(r"[^{}]*?\{\s*\}", "", css)

        return css

    def _restore_literals(self, css: str) -> str:
        for token_id, original in self.literal_table.items():
            css = css.replace(token_id, original)
        return css
