"""
Show what a carpet design would look like if every color in it were replaced
by the closest matching color from your factory's yarn palette - at the
design's own resolution (NOT resized to the knot grid), purely so you and the
customer can see the realistic color match before weaving.

This uses Lab color space (perceptually accurate, same method professional
color-matching tools use) instead of plain RGB, so the nearest match is the
one that actually LOOKS most similar to a human eye, not just numerically
closest.

Usage:
    python match_palette_preview.py design.png matched_preview.png --palette "#aabbcc,#112233,..."
    python match_palette_preview.py design.png matched_preview.png --palette factory_palette.txt

Output:
    - matched_preview.png : same size as the input image, every pixel mapped
      to the nearest palette color
    - prints a small report: each palette color and what % of the image
      matched to it
"""

import argparse
import math
from PIL import Image

from carpet_prepare import parse_palette


def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb_to_lab(r, g, b):
    rl, gl, bl = srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b)
    x = rl * 0.4124564 + gl * 0.3575761 + bl * 0.1804375
    y = rl * 0.2126729 + gl * 0.7151522 + bl * 0.0721750
    z = rl * 0.0193339 + gl * 0.1191920 + bl * 0.9503041

    xn, yn, zn = 0.95047, 1.0, 1.08883
    x, y, z = x / xn, y / yn, z / zn

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else (7.787 * t) + (16 / 116)

    fx, fy, fz = f(x), f(y), f(z)
    L = (116 * fy) - 16
    a = 500 * (fx - fy)
    b2 = 200 * (fy - fz)
    return (L, a, b2)


def lab_distance(lab1, lab2):
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(lab1, lab2)))


def nearest_palette_index(rgb, palette_lab):
    lab = rgb_to_lab(*rgb)
    best_i, best_d = 0, float("inf")
    for i, plab in enumerate(palette_lab):
        d = lab_distance(lab, plab)
        if d < best_d:
            best_d, best_i = d, i
    return best_i


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Carpet design image (any size)")
    parser.add_argument("output", help="Output matched-color preview PNG")
    parser.add_argument("--palette", required=True,
                         help="Factory palette: hex codes (\"#aabbcc,#112233,...\") "
                              "or a path to a text file with one hex per line")
    args = parser.parse_args()

    rgb_list = parse_palette(args.palette)
    palette_lab = [rgb_to_lab(r, g, b) for r, g, b in rgb_list]

    img = Image.open(args.input).convert("RGB")
    pixels = list(img.tobytes())
    pixels = [tuple(pixels[i:i + 3]) for i in range(0, len(pixels), 3)]

    cache = {}
    counts = [0] * len(rgb_list)
    out_pixels = []
    for px in pixels:
        idx = cache.get(px)
        if idx is None:
            idx = nearest_palette_index(px, palette_lab)
            cache[px] = idx
        counts[idx] += 1
        out_pixels.append(rgb_list[idx])

    out_img = Image.new("RGB", img.size)
    out_img.putdata(out_pixels)
    out_img.save(args.output, format="PNG")

    total = len(pixels)
    print(f"Saved {args.output}: {img.size[0]}x{img.size[1]} px, "
          f"matched to {len(rgb_list)} factory colors ({len(cache)} distinct "
          f"source colors seen)")
    print("Color usage in the matched preview:")
    for (r, g, b), cnt in zip(rgb_list, counts):
        if cnt:
            print(f"  #{r:02x}{g:02x}{b:02x}: {100 * cnt / total:.1f}%")


if __name__ == "__main__":
    main()
