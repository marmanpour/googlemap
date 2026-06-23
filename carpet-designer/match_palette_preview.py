"""
Show what a carpet design would look like if every color in it were replaced
by the closest matching color from your factory's yarn palette - at the
design's OWN resolution (not resized), so you and the customer see the
realistic color match in full detail before weaving.

Color matching is done in Lab color space (perceptually accurate, the same
idea professional color-matching tools use), so the nearest yarn is the one
that actually LOOKS most similar to the human eye, not just numerically
closest in RGB.

Usage:
    python match_palette_preview.py design.png matched_preview.png --palette "#aabbcc,#112233,..."
    python match_palette_preview.py design.png matched_preview.png --palette factory_palette.txt --clean 3

Quality tips:
    * Feed the LARGEST / highest-resolution version of the design you have.
      The output keeps the exact same width x height, so detail in = detail out.
    * Mapping every pixel to only 12 colors can leave tiny "salt and pepper"
      speckles where the original had a smooth gradient. --clean N removes
      isolated speckles using a majority filter (try 3, or 5 for a cleaner
      look). --clean 0 (default) keeps every pixel = maximum detail.

Output:
    * matched_preview.png : same size as input, every pixel = nearest yarn
    * a short report: each yarn color and what % of the image used it
"""

import argparse
import numpy as np
from PIL import Image, ImageFilter

from carpet_prepare import parse_palette

# A design rendered to 12 flat colors is small data, but the source can be big.
Image.MAX_IMAGE_PIXELS = None


def srgb_to_linear(arr):
    """arr: float array in 0..1 -> linear-light RGB."""
    return np.where(arr <= 0.04045, arr / 12.92, ((arr + 0.055) / 1.055) ** 2.4)


def rgb_to_lab(rgb):
    """rgb: array (..., 3) uint8 -> Lab array (..., 3) float, D65."""
    rgb = rgb.astype(np.float64) / 255.0
    lin = srgb_to_linear(rgb)
    r, g, b = lin[..., 0], lin[..., 1], lin[..., 2]

    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041

    x /= 0.95047
    z /= 1.08883  # y normalized by 1.0

    def f(t):
        return np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16.0 / 116.0)

    fx, fy, fz = f(x), f(y), f(z)
    L = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    bb = 200.0 * (fy - fz)
    return np.stack([L, a, bb], axis=-1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Carpet design image (any size)")
    parser.add_argument("output", help="Output matched-color preview PNG")
    parser.add_argument("--palette", required=True,
                         help="Factory palette: hex codes (\"#aabbcc,#112233,...\") "
                              "or a path to a text file with one hex per line")
    parser.add_argument("--clean", type=int, default=0,
                         help="Despeckle strength: 0 = off (max detail), or an odd "
                              "number like 3 or 5 to remove isolated speckles")
    args = parser.parse_args()

    rgb_list = parse_palette(args.palette)
    palette = np.array(rgb_list, dtype=np.uint8)           # (K, 3)
    palette_lab = rgb_to_lab(palette)                       # (K, 3)

    img = Image.open(args.input).convert("RGB")
    src = np.asarray(img)                                   # (H, W, 3) uint8
    h, w = src.shape[:2]
    src_lab = rgb_to_lab(src)                               # (H, W, 3) float

    # Nearest palette color in Lab: loop over K colors (only 12), keep best.
    best_idx = np.zeros((h, w), dtype=np.int32)
    best_dist = np.full((h, w), np.inf)
    for i, plab in enumerate(palette_lab):
        d = ((src_lab - plab) ** 2).sum(axis=-1)
        mask = d < best_dist
        best_dist[mask] = d[mask]
        best_idx[mask] = i

    idx8 = best_idx.astype(np.uint8)

    # Optional despeckle: do it on the index map so we never invent new colors.
    if args.clean and args.clean >= 3:
        size = args.clean if args.clean % 2 == 1 else args.clean + 1
        pimg = Image.fromarray(idx8, mode="P")
        pimg.putpalette(palette.flatten().tolist() + [0] * (768 - palette.size))
        pimg = pimg.filter(ImageFilter.ModeFilter(size))
        idx8 = np.asarray(pimg)

    out_rgb = palette[idx8]                                 # (H, W, 3)
    Image.fromarray(out_rgb, mode="RGB").save(args.output, format="PNG")

    total = h * w
    counts = np.bincount(idx8.ravel(), minlength=len(rgb_list))
    print(f"Saved {args.output}: {w}x{h} px, matched to {len(rgb_list)} factory "
          f"colors (clean={args.clean})")
    print("Color usage in the matched preview:")
    for (r, g, b), cnt in zip(rgb_list, counts):
        if cnt:
            print(f"  #{r:02x}{g:02x}{b:02x}: {100 * cnt / total:.1f}%")


if __name__ == "__main__":
    main()
