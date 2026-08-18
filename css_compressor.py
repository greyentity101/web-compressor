#!/usr/bin/env python3
"""
CSS-specific compression optimizations.
"""

import re
from typing import Tuple, List
from compressor import BaseCompressor, AssetType


class AdvancedCSSCompressor(BaseCompressor):
    """Production-grade CSS compressor with semantic optimizations."""

    # Named colors → shortest hex
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

    def compress(self, content: str) -> Tuple[str, List[str]]:
        warnings = []
        code = content

        # Multi-pass optimization
        code = self._remove_comments(code)
        code = self._remove_whitespace(code)
        code = self._optimize_colors(code)
        code = self._optimize_values(code)
        code = self._merge_selectors(code)
        code = self._dedupe_properties(code)
        code = self._optimize_units(code)

        return code, warnings

    def _remove_comments(self, code: str) -> str:
        code = re.sub(r"/\*[\s\S]*?\*/", "", code)
        return code

    def _remove_whitespace(self, code: str) -> str:
        code = re.sub(r"\s*([{};:,>+~])\s*", r"\1", code)
        code = re.sub(r"\s*:\s*", ":", code)
        code = "\n".join(line.strip() for line in code.split("\n") if line.strip())
        code = re.sub(r"\n\s*\n", "\n", code)
        code = re.sub(r",\s+", ",", code)
        code = re.sub(r"\s+;", ";", code)
        code = re.sub(r";\s+", ";", code)
        return code

    def _optimize_colors(self, code: str) -> str:
        # Named colors
        for name, hex_val in sorted(
            self.COLOR_MAP.items(), key=lambda x: len(x[1]), reverse=True
        ):
            if len(name) > len(hex_val):
                code = re.sub(r"\b" + re.escape(name) + r"\b", hex_val, code)

        # Shorten #rrggbb to #rgb
        def shorten_hex(m):
            h = m.group(1)
            if len(h) == 6 and h[0] == h[1] and h[2] == h[3] and h[4] == h[5]:
                return "#" + h[0] + h[2] + h[4]
            return "#" + h

        code = re.sub(r"#([0-9a-fA-F]{6})\b", shorten_hex, code)

        # rgb() to hex
        code = re.sub(
            r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)",
            lambda m: "#{:02x}{:02x}{:02x}".format(
                int(m.group(1)), int(m.group(2)), int(m.group(3))
            ),
            code,
        )
        return code

    def _optimize_values(self, code: str) -> str:
        # Zero values
        code = re.sub(
            r"\b0(px|em|rem|pt|pc|cm|mm|in|vh|vw|vmin|vmax|ex|ch|deg|rad|turn|s|ms|Hz|kHz|dpi|dpcm|dppx)?\b",
            "0",
            code,
        )
        # Font weights
        code = re.sub(r"\bbold\b", "700", code)
        code = re.sub(r"\bnormal\b", "400", code)
        return code

    def _merge_selectors(self, code: str) -> str:
        rules = re.findall(r"([^{]+)\{([^}]*)\}", code, re.DOTALL)
        if not rules:
            return code

        rule_map = {}
        order = []
        for selector, body in rules:
            selector = selector.strip()
            if not selector:
                continue
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
                rule_map[selector].update(props)

        parts = []
        for selector in order:
            props = rule_map[selector]
            body = ";".join(f"{k}:{v}" for k, v in props.items())
            parts.append(f"{selector}{{{body}}}")

        return ";".join(parts) + ";" if parts else ""

    def _dedupe_properties(self, code: str) -> str:
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

    def _optimize_units(self, code: str) -> str:
        # Remove units from zero values (already done in _optimize_values)
        # Convert absolute to relative where safe (0.5em → .5em)
        code = re.sub(r"0\.(\d+)em", r".\1em", code)
        code = re.sub(r"0\.(\d+)rem", r".\1rem", code)
        return code

    def detect_type(self, content: str, filename: str) -> AssetType:
        if filename.endswith(".css"):
            return AssetType.CSS
        return AssetType.UNKNOWN


class AdvancedCSSCompressor(AdvancedCSSCompressor):
    pass
