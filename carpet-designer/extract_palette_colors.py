"""
Extract the hex codes of color swatches from an image of a factory yarn
palette strip (a row of solid color blocks).

Usage:
    python extract_palette_colors.py palette.png

It samples the center pixel of evenly-spaced columns across the image and
prints the hex code for each. If the swatches aren't evenly spaced, or
there's a border/logo in the image, crop the image first so it contains
only the row of color swatches.
"""

import argparse
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Image containing a row of color swatches")
    parser.add_argument("--count", type=int, default=12, help="Number of swatches (default: 12)")
    parser.add_argument("--row", type=float, default=0.5,
                         help="Vertical position to sample, as a fraction of image height (default: 0.5 = middle)")
    args = parser.parse_args()

    img = Image.open(args.input).convert("RGB")
    w, h = img.size
    y = int(h * args.row)

    hexes = []
    for i in range(args.count):
        x = int((i + 0.5) * w / args.count)
        r, g, b = img.getpixel((x, y))
        hexes.append(f"#{r:02x}{g:02x}{b:02x}")

    print(",".join(hexes))


if __name__ == "__main__":
    main()
