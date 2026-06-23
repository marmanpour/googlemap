"""
Make an honest-but-attractive customer image: keep ALL the original detail and
colors of the design, but recolor ONLY the chosen areas (e.g. the bright
crimson field) to a real factory yarn color (e.g. the dark blood red #910510),
so the customer sees the red the loom can actually weave - while every other
color and all the fine detail stay exactly as in the original.

How it decides what to recolor:
For every pixel it finds which factory yarn the loom would weave it as (using
CIEDE2000, the accurate color-difference method). Only pixels that map to one
of the --replace yarns are changed to the --with color. Pink, teal, gold,
cream, etc. are left as the ORIGINAL image, so detail is preserved.

Usage (defaults already target the two factory reds -> dark blood red):
    python recolor_for_customer.py Silk-1600_Page16.png Mizban_4x6_customer.jpg \
        --palette "#ebe3d6,#09136c,#1a93be,#bf452e,#910510,#815f05,#ceb57f,#d7a62d,#000207,#8f941e,#0f4315,#fda9b6" \
        --meters 4x6 --maxpx 2000

    # change which yarns count as "red" or the replacement color:
    ... --replace "#bf452e,#910510" --with "#910510"
"""

import argparse
import numpy as np
from PIL import Image

from carpet_prepare import parse_palette
from match_palette_preview import rgb_to_lab, de2000_to_color

Image.MAX_IMAGE_PIXELS = None


def parse_meters(s):
    s = s.lower().replace("m", "").replace("x", " ").replace("*", " ")
    parts = s.split()
    if len(parts) != 2:
        raise ValueError("--meters must look like 4x6 (width x height in meters)")
    return float(parts[0]), float(parts[1])


def nearest_palette_index(color_rgb, palette_lab):
    """Index of the palette color closest to a single rgb tuple (CIEDE2000)."""
    lab = rgb_to_lab(np.array([[color_rgb]], dtype=np.uint8))[0, 0]
    best_i, best_d = 0, float("inf")
    for i, plab in enumerate(palette_lab):
        d = float(de2000_to_color(lab[None, None, :], plab)[0, 0])
        if d < best_d:
            best_d, best_i = d, i
    return best_i


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Original carpet design image")
    parser.add_argument("output", help="Output image (.jpg or .png)")
    parser.add_argument("--palette", required=True,
                        help="The 12 factory yarn hex codes (or a path to a file)")
    parser.add_argument("--replace", default="#bf452e,#910510",
                        help="Which factory yarns count as the area to recolor "
                             "(default: the two reds #bf452e,#910510)")
    parser.add_argument("--with", dest="target", default="#910510",
                        help="Replace those areas with this color (default #910510)")
    parser.add_argument("--meters", default=None,
                        help="Force carpet proportions WIDTHxHEIGHT in meters, e.g. 4x6")
    parser.add_argument("--maxpx", type=int, default=2000,
                        help="Longest side of the output in pixels (default 2000)")
    parser.add_argument("--quality", type=int, default=92,
                        help="JPEG quality if output is .jpg (default 92)")
    args = parser.parse_args()

    palette = np.array(parse_palette(args.palette), dtype=np.uint8)
    palette_lab = rgb_to_lab(palette)

    replace_rgb = parse_palette(args.replace)
    replace_idx = {nearest_palette_index(c, palette_lab) for c in replace_rgb}
    target = np.array(parse_palette(args.target)[0], dtype=np.uint8)

    img = Image.open(args.input).convert("RGB")
    src = np.asarray(img).copy()
    h, w = src.shape[:2]
    src_lab = rgb_to_lab(src)

    # which factory yarn would the loom weave each pixel as?
    best_idx = np.zeros((h, w), dtype=np.int32)
    best_dist = np.full((h, w), np.inf)
    for i, plab in enumerate(palette_lab):
        d = de2000_to_color(src_lab, plab)
        m = d < best_dist
        best_dist[m] = d[m]
        best_idx[m] = i

    # recolor only the pixels that map to a "replace" yarn; keep the rest original
    mask = np.isin(best_idx, list(replace_idx))
    src[mask] = target
    changed = 100.0 * mask.sum() / (h * w)

    # resize for the customer
    if args.meters:
        w_m, h_m = parse_meters(args.meters)
        aspect = w_m / h_m
    else:
        aspect = w / h
    if aspect >= 1:
        out_w, out_h = args.maxpx, max(1, round(args.maxpx / aspect))
    else:
        out_h, out_w = args.maxpx, max(1, round(args.maxpx * aspect))

    out = Image.fromarray(src, mode="RGB").resize(
        (out_w, out_h), resample=Image.Resampling.LANCZOS)

    save_kwargs = {}
    if args.output.lower().endswith((".jpg", ".jpeg")):
        save_kwargs = {"quality": args.quality, "subsampling": 0}
    out.save(args.output, **save_kwargs)

    tr, tg, tb = (int(x) for x in target)
    print(f"Saved {args.output}: {out_w}x{out_h} px")
    print(f"Recolored {changed:.1f}% of pixels (the red areas) to "
          f"#{tr:02x}{tg:02x}{tb:02x}; all other detail kept from the original")


if __name__ == "__main__":
    main()
