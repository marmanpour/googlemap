"""
Prepare a carpet design image for Jacquard CAD/CAM software (Booria CAD,
NedGraphics, etc.): resize to an exact knot grid (1 pixel = 1 knot) and
reduce to a fixed, solid color palette with dithering disabled.

Usage:
    python carpet_prepare.py input.png output.bmp --width 600 --height 800 --colors 12

Notes on the two operations:

1. Exact pixel resizing
   The output size must be EXACTLY width x height pixels (one pixel per
   warp/weft intersection), regardless of the source image's aspect ratio.
   LANCZOS is used because it averages the source pixels into each output
   pixel (proper downsampling), which gives a clean color per knot instead
   of a single sampled pixel. If your source is already a clean, pixel-art
   style design (e.g. exported from a point-paper tool) and you want every
   output pixel to be an exact copy of a source pixel with hard edges, use
   --resample nearest instead.

2. Color quantization with no dithering
   Image.quantize() with dither=Image.Dither.NONE maps every pixel to the
   nearest color in a reduced palette WITHOUT adding any noise/speckle
   pixels. This is required for Jacquard weaving: dithering would produce
   isolated single-knot color changes that the loom cannot weave cleanly.
"""

import argparse
from PIL import Image


RESAMPLE_METHODS = {
    "lanczos": Image.Resampling.LANCZOS,   # high-quality averaging (default)
    "nearest": Image.Resampling.NEAREST,   # hard pixel copy, no blending
    "box": Image.Resampling.BOX,           # simple area averaging
}


def parse_palette(palette_arg):
    """Read a fixed palette as a list of (r, g, b) tuples.

    palette_arg may be:
      - a comma/space/newline separated string of hex codes ("#b3001b, #d4a017")
      - a path to a text file containing one hex code per line
    """
    import os

    if palette_arg is None:
        return None

    if os.path.isfile(palette_arg):
        with open(palette_arg, encoding="utf-8") as f:
            text = f.read()
    else:
        text = palette_arg

    tokens = text.replace(",", " ").split()
    rgb = []
    for t in tokens:
        t = t.strip().lstrip("#")
        if len(t) != 6:
            continue
        rgb.append((int(t[0:2], 16), int(t[2:4], 16), int(t[4:6], 16)))
    if not rgb:
        raise ValueError(f"No valid hex colors found in palette: {palette_arg!r}")
    return rgb


def build_palette_image(rgb_list):
    """Create a PIL 'P' mode image whose palette is exactly rgb_list."""
    pal_img = Image.new("P", (1, 1))
    flat = []
    for r, g, b in rgb_list:
        flat.extend([r, g, b])
    # PIL palettes need 256 colors; pad by repeating the last color
    while len(flat) < 256 * 3:
        flat.extend(flat[-3:])
    pal_img.putpalette(flat)
    return pal_img


def prepare_carpet_design(input_path, output_path, width, height, colors=12,
                           resample="lanczos", palette=None):
    img = Image.open(input_path).convert("RGB")

    # 1. Exact pixel resizing -> one pixel per knot, ignoring aspect ratio
    resized = img.resize((width, height), resample=RESAMPLE_METHODS[resample])

    # 2. Color quantization, dithering disabled
    if palette is not None:
        # Map every pixel to the NEAREST color in the factory's real yarn palette
        rgb_list = parse_palette(palette)
        pal_img = build_palette_image(rgb_list)
        quantized = resized.quantize(palette=pal_img, dither=Image.Dither.NONE)
        ncolors = len(rgb_list)
    else:
        # Auto-pick the palette from the image
        quantized = resized.quantize(
            colors=colors,
            method=Image.Quantize.MEDIANCUT,
            dither=Image.Dither.NONE,
        )
        ncolors = colors

    # Save as BMP (indexed/8-bit palette mode is supported natively by BMP)
    quantized.save(output_path, format="BMP")

    mode = "factory palette" if palette is not None else "auto"
    print(f"Saved {output_path}: {width}x{height} px, {ncolors} colors ({mode}), "
          f"resample={resample}, dither=NONE")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Path to source design image")
    parser.add_argument("output", help="Path to output .bmp file")
    parser.add_argument("--width", type=int, required=True, help="Exact output width in knots")
    parser.add_argument("--height", type=int, required=True, help="Exact output height in knots")
    parser.add_argument("--colors", type=int, default=12, help="Number of colors when auto-picking the palette (default: 12; ignored if --palette is given)")
    parser.add_argument("--palette", default=None,
                         help="Fixed factory yarn palette: either hex codes "
                              "(\"#b3001b,#d4a017,...\") or a path to a text file "
                              "with one hex code per line. Each pixel is mapped to "
                              "the nearest color in this palette.")
    parser.add_argument("--resample", choices=RESAMPLE_METHODS.keys(), default="lanczos",
                         help="Resize method (default: lanczos)")
    args = parser.parse_args()

    prepare_carpet_design(args.input, args.output, args.width, args.height,
                           colors=args.colors, resample=args.resample,
                           palette=args.palette)


if __name__ == "__main__":
    main()
