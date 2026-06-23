"""
Convert a quantized carpet design (output of carpet_prepare.py, an indexed
.bmp where each pixel = one knot and each color = one yarn) into row-by-row
weaving data files for programming a Jacquard loom.

Usage:
    python carpet_to_loomdata.py output.bmp loomdata

This produces, using "loomdata" as the base name:
  - loomdata_legend.csv : color number -> hex code -> knot count -> percent
  - loomdata_grid.csv   : full row x col grid of color numbers (1..N)
  - loomdata_rle.txt    : row-by-row run-length encoding
                          (color:count, color:count, ... per row/pick)
                          this is the compact form most loom software expects
                          for "color change" sequences along each weft pick.

Color numbering: colors are numbered 1..N in order of how often they appear
(1 = most-used color), matching the legend produced by the carpet-designer
web tool, so the same numbers line up if you used that tool for the palette.

This version streams the image row by row, so it handles very large knot
grids (e.g. 6000 x 27000) without loading millions of Python objects.
"""

import argparse
from PIL import Image

# Loom carpet maps are legitimately huge; disable the decompression-bomb guard.
Image.MAX_IMAGE_PIXELS = None


def load_indexed(path):
    img = Image.open(path)
    if img.mode != "P":
        img = img.convert("P", palette=Image.ADAPTIVE)
    palette = img.getpalette()
    w, h = img.size
    data = img.tobytes()  # one byte (palette index) per pixel, row-major
    return data, w, h, palette


def build_remap(data, palette):
    """Count colors and renumber them by frequency (most used = color 1)."""
    counts = {}
    for i in range(256):
        c = data.count(i)          # C-level scan, fast even for huge images
        if c:
            counts[i] = c
    ordered = sorted(counts.keys(), key=lambda idx: -counts[idx])
    remap = {old: new for new, old in enumerate(ordered)}  # 0-based new index

    hexes = []
    for old_idx in ordered:
        r, g, b = palette[old_idx * 3: old_idx * 3 + 3]
        hexes.append(f"#{r:02x}{g:02x}{b:02x}")
    return counts, ordered, remap, hexes


def row_indices(data, w, h, bottom_up):
    """Yield each row as the slice of palette indices for that weft pick."""
    order = range(h - 1, -1, -1) if bottom_up else range(h)
    for y in order:
        yield data[y * w:(y + 1) * w]


def write_legend(path, hexes, counts, ordered, total):
    with open(path, "w", encoding="utf-8") as f:
        f.write("ColorNumber,Hex,KnotCount,Percent\n")
        for new_idx, old_idx in enumerate(ordered):
            cnt = counts[old_idx]
            f.write(f"{new_idx + 1},{hexes[new_idx]},{cnt},{100 * cnt / total:.2f}\n")


def write_grid(path, data, w, h, remap, bottom_up):
    with open(path, "w", encoding="utf-8") as f:
        for rowbytes in row_indices(data, w, h, bottom_up):
            f.write(",".join(str(remap[b] + 1) for b in rowbytes) + "\n")


def write_rle(path, data, w, h, remap, bottom_up):
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Each line = one weft pick (row), bottom row first is typical loom order\n")
        f.write("# Format: color:count, color:count, ...\n")
        for rowbytes in row_indices(data, w, h, bottom_up):
            runs = []
            cur = remap[rowbytes[0]]
            cnt = 1
            for b in rowbytes[1:]:
                c = remap[b]
                if c == cur:
                    cnt += 1
                else:
                    runs.append(f"{cur + 1}:{cnt}")
                    cur, cnt = c, 1
            runs.append(f"{cur + 1}:{cnt}")
            f.write(", ".join(runs) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Indexed .bmp/.png from carpet_prepare.py")
    parser.add_argument("outbase", help="Base name for output files")
    parser.add_argument("--bottom-up", action="store_true",
                         help="Reverse row order so row 1 = bottom of the carpet "
                              "(many looms weave from the bottom edge upward)")
    parser.add_argument("--no-grid", action="store_true",
                         help="Skip the full grid CSV (it can be very large for "
                              "big carpets); still writes legend and RLE")
    args = parser.parse_args()

    data, w, h, palette = load_indexed(args.input)
    counts, ordered, remap, hexes = build_remap(data, palette)
    total = sum(counts.values())

    write_legend(f"{args.outbase}_legend.csv", hexes, counts, ordered, total)
    write_rle(f"{args.outbase}_rle.txt", data, w, h, remap, args.bottom_up)
    if not args.no_grid:
        write_grid(f"{args.outbase}_grid.csv", data, w, h, remap, args.bottom_up)

    print(f"{h} rows x {w} cols, {len(ordered)} colors")
    written = f"{args.outbase}_legend.csv, {args.outbase}_rle.txt"
    if not args.no_grid:
        written += f", {args.outbase}_grid.csv"
    print(f"Wrote {written}")


if __name__ == "__main__":
    main()
