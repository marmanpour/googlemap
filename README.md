# Silk Atelier — Persian Carpet Campaign Prompt Studio

A single-page web app that turns any Persian (art-)silk carpet into a complete luxury
photoshoot **shot list of prompts for Nano Banana 2 in Google Flow**.

## What it does

1. **Describe your carpet** — or pick a preset matched to a Qom art-silk inventory
   (navy bird motif, turquoise tree-of-life, red medallion, gold-on-black, cream star, blue oval).
2. **Pick campaign scenes** — 15 art-directed concepts across four categories:
   - **Model** — staircase runner, couture carpet-cape, tea house, master weaver's hands
   - **Car** — rug-on-bonnet studio ad, desert vintage Mercedes, supercar caravanserai arrival
   - **Creature** — white horse among black Friesians, black panther, falcon, Persian cat
   - **Texture** — macro knot hero, floating over Fin Garden pool, gallery wall, flying carpet
3. **Set art direction** — mood, colour grade (incl. "monochrome scene / full-colour rug"),
   aspect ratio, model casting.
4. **Generate** — every selected scene becomes one self-contained, copy-ready prompt that
   always includes:
   - a **carpet block** built from your description,
   - a **silk-realism block** (directional sheen, nap colour-shift, visible knots, fringe
     strand detail, real fabric physics) so artificial silk renders like genuine silk,
   - a **design-fidelity block** for when you attach the rug's photo as reference in Flow,
   - camera/lens/lighting language and an avoid-list for maximum photorealism.

Export the whole shot list as JSON or copy all prompts at once.

## Run it

No build step. Open `index.html` in any browser, or:

```bash
python3 -m http.server 8000
# → http://localhost:8000
```

## Workflow in Google Flow

1. Photograph your rug frontal, flat and evenly lit; upload it as a reference image.
2. Paste one prompt per generation (don't merge shots).
3. If texture comes out soft, regenerate appending:
   *"increase micro-detail in the carpet pile, individual knots visible."*
4. Fix model faces with region edits rather than re-rolling a frame where the rug is perfect.
5. Upscale last for print.

See `PROMPTS.md` for ready-to-paste examples.
