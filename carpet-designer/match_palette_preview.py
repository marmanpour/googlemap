"""
Show what a carpet design would look like if every color in it were replaced
by the closest matching color from your factory's yarn palette - at the
design's OWN resolution (not resized), so you and the customer see the
realistic color match in full detail before weaving.

Color matching is done in Lab color space. Two methods are available:

  --method de2000  (DEFAULT, recommended)
        CIEDE2000, the modern industry standard for color difference. It is
        much more accurate for SATURATED colors (deep reds, crimson, pink),
        so a strong crimson field stays a red yarn instead of jumping to pink.
  --method de76
        Plain Euclidean Lab distance. Faster, but can mis-match saturated
        colors (e.g. crimson -> pink). Kept for comparison.

Usage:
    python match_palette_preview.py design.png matched_preview.png --palette "#aabbcc,#112233,..."
    python match_palette_preview.py design.png matched_preview.png --palette factory.txt --clean 3
    python match_palette_preview.py design.png matched_preview.png --palette factory.txt --method de76

Quality tips:
    * Feed the LARGEST / highest-resolution version of the design you have.
      The output keeps the exact same width x height: detail in = detail out.
    * --clean N removes isolated "salt and pepper" speckles with a majority
      filter (try 3, or 5 for a cleaner look). --clean 0 (default) = max detail.

Output:
    * matched_preview.png : same size as input, every pixel = nearest yarn
    * a short report: each yarn color and what % of the image used it
"""

import argparse
import numpy as np
from PIL import Image, ImageFilter

from carpet_prepare import parse_palette

Image.MAX_IMAGE_PIXELS = None


def srgb_to_linear(arr):
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


def de76_to_color(lab, color):
    """Squared Euclidean Lab distance from every pixel to one palette color."""
    return ((lab - color) ** 2).sum(axis=-1)


def de2000_to_color(lab, color):
    """CIEDE2000 difference from every pixel (lab, HxWx3) to one color (3,)."""
    L1, a1, b1 = lab[..., 0], lab[..., 1], lab[..., 2]
    L2, a2, b2 = color

    C1 = np.sqrt(a1 ** 2 + b1 ** 2)
    C2 = np.sqrt(a2 ** 2 + b2 ** 2)
    Cbar = (C1 + C2) / 2.0
    Cbar7 = Cbar ** 7
    G = 0.5 * (1 - np.sqrt(Cbar7 / (Cbar7 + 25.0 ** 7)))

    a1p = (1 + G) * a1
    a2p = (1 + G) * a2
    C1p = np.sqrt(a1p ** 2 + b1 ** 2)
    C2p = np.sqrt(a2p ** 2 + b2 ** 2)

    h1p = np.degrees(np.arctan2(b1, a1p)) % 360.0
    h2p = np.degrees(np.arctan2(b2, a2p)) % 360.0

    dLp = L2 - L1
    dCp = C2p - C1p

    dhp = h2p - h1p
    dhp = np.where(dhp > 180, dhp - 360, dhp)
    dhp = np.where(dhp < -180, dhp + 360, dhp)
    zero_c = (C1p * C2p) == 0
    dhp = np.where(zero_c, 0.0, dhp)
    dHp = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dhp) / 2.0)

    Lbarp = (L1 + L2) / 2.0
    Cbarp = (C1p + C2p) / 2.0

    hsum = h1p + h2p
    habsdiff = np.abs(h1p - h2p)
    hbarp = np.where(
        habsdiff <= 180, hsum / 2.0,
        np.where(hsum < 360, (hsum + 360) / 2.0, (hsum - 360) / 2.0),
    )
    hbarp = np.where(zero_c, hsum, hbarp)

    T = (1
         - 0.17 * np.cos(np.radians(hbarp - 30))
         + 0.24 * np.cos(np.radians(2 * hbarp))
         + 0.32 * np.cos(np.radians(3 * hbarp + 6))
         - 0.20 * np.cos(np.radians(4 * hbarp - 63)))

    dtheta = 30 * np.exp(-(((hbarp - 275) / 25.0) ** 2))
    Cbarp7 = Cbarp ** 7
    RC = 2 * np.sqrt(Cbarp7 / (Cbarp7 + 25.0 ** 7))
    SL = 1 + (0.015 * (Lbarp - 50) ** 2) / np.sqrt(20 + (Lbarp - 50) ** 2)
    SC = 1 + 0.045 * Cbarp
    SH = 1 + 0.015 * Cbarp * T
    RT = -np.sin(np.radians(2 * dtheta)) * RC

    dE = np.sqrt(
        (dLp / SL) ** 2
        + (dCp / SC) ** 2
        + (dHp / SH) ** 2
        + RT * (dCp / SC) * (dHp / SH)
    )
    return dE


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Carpet design image (any size)")
    parser.add_argument("output", help="Output matched-color preview PNG")
    parser.add_argument("--palette", required=True,
                         help="Factory palette: hex codes (\"#aabbcc,#112233,...\") "
                              "or a path to a text file with one hex per line")
    parser.add_argument("--method", choices=["de2000", "de76"], default="de2000",
                         help="Color-match method (default de2000, more accurate "
                              "for saturated reds/pinks)")
    parser.add_argument("--clean", type=int, default=0,
                         help="Despeckle strength: 0 = off (max detail), or an odd "
                              "number like 3 or 5 to remove isolated speckles")
    args = parser.parse_args()

    rgb_list = parse_palette(args.palette)
    palette = np.array(rgb_list, dtype=np.uint8)
    palette_lab = rgb_to_lab(palette)

    img = Image.open(args.input).convert("RGB")
    src = np.asarray(img)
    h, w = src.shape[:2]
    src_lab = rgb_to_lab(src)

    dist_fn = de2000_to_color if args.method == "de2000" else de76_to_color

    best_idx = np.zeros((h, w), dtype=np.int32)
    best_dist = np.full((h, w), np.inf)
    for i, plab in enumerate(palette_lab):
        d = dist_fn(src_lab, plab)
        mask = d < best_dist
        best_dist[mask] = d[mask]
        best_idx[mask] = i

    idx8 = best_idx.astype(np.uint8)

    if args.clean and args.clean >= 3:
        size = args.clean if args.clean % 2 == 1 else args.clean + 1
        pimg = Image.fromarray(idx8, mode="P")
        pimg.putpalette(palette.flatten().tolist() + [0] * (768 - palette.size))
        pimg = pimg.filter(ImageFilter.ModeFilter(size))
        idx8 = np.asarray(pimg)

    out_rgb = palette[idx8]
    Image.fromarray(out_rgb, mode="RGB").save(args.output, format="PNG")

    total = h * w
    counts = np.bincount(idx8.ravel(), minlength=len(rgb_list))
    print(f"Saved {args.output}: {w}x{h} px, matched to {len(rgb_list)} factory "
          f"colors (method={args.method}, clean={args.clean})")
    print("Color usage in the matched preview:")
    for (r, g, b), cnt in zip(rgb_list, counts):
        if cnt:
            print(f"  #{r:02x}{g:02x}{b:02x}: {100 * cnt / total:.1f}%")


if __name__ == "__main__":
    main()
