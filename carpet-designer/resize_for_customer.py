"""
Resize a carpet design image to send to a customer - high quality, optionally
forced to the carpet's real proportions (e.g. 4 m x 6 m).

Unlike match_palette_preview.py (which re-colors the design to the factory's
12 yarns), this keeps the ORIGINAL colors and detail of the design and only
changes its size / proportions. Use this when the factory palette is already
close to the design's colors and you just want an attractive, correctly
proportioned image for the customer.

Usage:
    # keep the design's own proportions, just shrink to a sensible size:
    python resize_for_customer.py design.png customer.jpg --maxpx 2000

    # force the exact carpet proportions (4 m wide x 6 m long = 2:3):
    python resize_for_customer.py design.png customer.jpg --meters 4x6 --maxpx 2000

Notes:
    * --meters forces the image to that width:height ratio. If the source is
      already close to it, the slight stretch is invisible. If it is far off,
      the motifs would distort - check the result.
    * Saves high quality (LANCZOS). Output extension decides the format
      (.jpg = smaller file to send, .png = lossless).
"""

import argparse
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def parse_meters(s):
    s = s.lower().replace("m", "").replace("x", " ").replace("*", " ")
    parts = s.split()
    if len(parts) != 2:
        raise ValueError("--meters must look like 4x6 (width x height in meters)")
    return float(parts[0]), float(parts[1])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Original carpet design image")
    parser.add_argument("output", help="Output image (.jpg or .png)")
    parser.add_argument("--meters", default=None,
                        help="Force carpet proportions WIDTHxHEIGHT in meters, "
                             "e.g. 4x6. Omit to keep the design's own proportions.")
    parser.add_argument("--maxpx", type=int, default=2000,
                        help="Longest side of the output in pixels (default 2000)")
    parser.add_argument("--quality", type=int, default=92,
                        help="JPEG quality if output is .jpg (default 92)")
    args = parser.parse_args()

    img = Image.open(args.input).convert("RGB")
    w, h = img.size

    if args.meters:
        w_m, h_m = parse_meters(args.meters)
        aspect = w_m / h_m  # target width / height
    else:
        aspect = w / h      # keep original proportions

    # fit within maxpx on the longest side, at the chosen aspect ratio
    if aspect >= 1:  # wider than tall
        out_w = args.maxpx
        out_h = max(1, round(args.maxpx / aspect))
    else:            # taller than wide
        out_h = args.maxpx
        out_w = max(1, round(args.maxpx * aspect))

    out = img.resize((out_w, out_h), resample=Image.Resampling.LANCZOS)

    save_kwargs = {}
    if args.output.lower().endswith((".jpg", ".jpeg")):
        save_kwargs = {"quality": args.quality, "subsampling": 0}
    out.save(args.output, **save_kwargs)

    note = f" (forced {args.meters} proportions)" if args.meters else " (original proportions)"
    print(f"Saved {args.output}: {out_w}x{out_h} px{note}")


if __name__ == "__main__":
    main()
