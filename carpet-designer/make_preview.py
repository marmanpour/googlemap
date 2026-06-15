"""
Make a PROPORTIONAL preview image of a knot-grid carpet file.

Why this exists:
A machine loom has more knots per meter along the LENGTH than across the
WIDTH (e.g. 1500 reed = 1500 knots/m wide, but 4500 density = 4500 knots/m
long). The production file (carpet_prepare.py output) draws one square pixel
per knot, so the raw file looks vertically STRETCHED. That is correct for the
loom -- the loom software weaves it back to the real shape.

But a person looking at the raw BMP will think it is distorted. This script
makes a separate, normal-looking PNG with the carpet's TRUE physical
proportions (e.g. 4 m x 6 m), only for human viewing / approval. It does NOT
replace the production BMP.

Usage:
    python make_preview.py Naghsheh_4x6.bmp preview.png --meters 4x6
    python make_preview.py Naghsheh_4x6.bmp preview.png --meters 4x6 --maxpx 1600
"""

import argparse
from PIL import Image


def parse_meters(s):
    s = s.lower().replace("m", "").replace("x", " ").replace("*", " ")
    parts = s.split()
    if len(parts) != 2:
        raise ValueError("--meters must look like 4x6 (width x height in meters)")
    return float(parts[0]), float(parts[1])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="The production .bmp (one pixel per knot)")
    parser.add_argument("output", help="Output preview .png")
    parser.add_argument("--meters", required=True,
                        help="Physical size as WIDTHxHEIGHT in meters, e.g. 4x6")
    parser.add_argument("--maxpx", type=int, default=1600,
                        help="Longest side of the preview in pixels (default 1600)")
    args = parser.parse_args()

    img = Image.open(args.input).convert("RGB")
    w_m, h_m = parse_meters(args.meters)

    # target preview keeps the TRUE physical aspect ratio (width:height in meters)
    if h_m >= w_m:
        out_h = args.maxpx
        out_w = max(1, round(args.maxpx * w_m / h_m))
    else:
        out_w = args.maxpx
        out_h = max(1, round(args.maxpx * h_m / w_m))

    # NEAREST keeps the exact palette colors (no blending / new colors)
    preview = img.resize((out_w, out_h), resample=Image.Resampling.NEAREST)
    preview.save(args.output, format="PNG")

    print(f"Saved {args.output}: {out_w}x{out_h} px, true shape for a "
          f"{w_m} m x {h_m} m carpet (for viewing only, NOT for the loom)")


if __name__ == "__main__":
    main()
