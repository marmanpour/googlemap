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


def prepare_carpet_design(input_path, output_path, width, height, colors=12,
                           resample="lanczos"):
    img = Image.open(input_path).convert("RGB")

    # 1. Exact pixel resizing -> one pixel per knot, ignoring aspect ratio
    resized = img.resize((width, height), resample=RESAMPLE_METHODS[resample])

    # 2. Color quantization to a fixed palette, dithering disabled
    quantized = resized.quantize(
        colors=colors,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.NONE,
    )

    # Save as BMP (indexed/8-bit palette mode is supported natively by BMP)
    quantized.save(output_path, format="BMP")

    print(f"Saved {output_path}: {width}x{height} px, {colors} colors, "
          f"resample={resample}, dither=NONE")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Path to source design image")
    parser.add_argument("output", help="Path to output .bmp file")
    parser.add_argument("--width", type=int, required=True, help="Exact output width in knots")
    parser.add_argument("--height", type=int, required=True, help="Exact output height in knots")
    parser.add_argument("--colors", type=int, default=12, help="Number of colors in the final palette (default: 12)")
    parser.add_argument("--resample", choices=RESAMPLE_METHODS.keys(), default="lanczos",
                         help="Resize method (default: lanczos)")
    args = parser.parse_args()

    prepare_carpet_design(args.input, args.output, args.width, args.height,
                           colors=args.colors, resample=args.resample)


if __name__ == "__main__":
    main()
