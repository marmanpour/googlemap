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
"""

import argparse
from PIL import Image


def load_indexed_grid(path):
    img = Image.open(path)
    if img.mode != "P":
        img = img.convert("P", palette=Image.ADAPTIVE)
    palette = img.getpalette()
    w, h = img.size
    pixels = list(img.getdata())

    # collect colors actually used, ordered by frequency (most used = 1)
    counts = {}
    for p in pixels:
        counts[p] = counts.get(p, 0) + 1
    ordered = sorted(counts.keys(), key=lambda idx: -counts[idx])
    remap = {old: new for new, old in enumerate(ordered)}  # 0-based new index

    hexes = []
    for old_idx in ordered:
        r, g, b = palette[old_idx * 3: old_idx * 3 + 3]
        hexes.append(f"#{r:02x}{g:02x}{b:02x}")

    grid = [[remap[pixels[y * w + x]] for x in range(w)] for y in range(h)]
    return grid, hexes, counts, remap, ordered


def write_legend(path, hexes, counts, remap, ordered, total):
    with open(path, "w", encoding="utf-8") as f:
        f.write("ColorNumber,Hex,KnotCount,Percent\n")
        for new_idx, old_idx in enumerate(ordered):
            cnt = counts[old_idx]
            f.write(f"{new_idx + 1},{hexes[new_idx]},{cnt},{100 * cnt / total:.2f}\n")


def write_grid(path, grid):
    with open(path, "w", encoding="utf-8") as f:
        for row in grid:
            f.write(",".join(str(c + 1) for c in row) + "\n")


def write_rle(path, grid):
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Each line = one weft pick (row), bottom row first is typical loom order\n")
        f.write("# Format: color:count, color:count, ...\n")
        for row in grid:
            runs = []
            cur, cnt = row[0], 1
            for c in row[1:]:
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
    args = parser.parse_args()

    grid, hexes, counts, remap, ordered = load_indexed_grid(args.input)
    total = sum(counts.values())

    if args.bottom_up:
        grid = grid[::-1]

    write_legend(f"{args.outbase}_legend.csv", hexes, counts, remap, ordered, total)
    write_grid(f"{args.outbase}_grid.csv", grid)
    write_rle(f"{args.outbase}_rle.txt", grid)

    rows, cols = len(grid), len(grid[0])
    print(f"{rows} rows x {cols} cols, {len(ordered)} colors")
    print(f"Wrote {args.outbase}_legend.csv, {args.outbase}_grid.csv, {args.outbase}_rle.txt")


if __name__ == "__main__":
    main()
