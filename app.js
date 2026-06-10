/* ============================================================
   Silk Atelier — prompt engine for Nano Banana 2 (Google Flow)
   ============================================================ */

/* ---------- Carpet presets (matched to typical Qom art-silk inventory) ---------- */
const PRESETS = [
  {
    id: "birds",
    label: "Birds of Qom (navy)",
    name: "Qom Birds-of-Paradise",
    field: "deep midnight-navy",
    motif: "rows of vividly coloured songbirds and parakeets perched on slender golden branches",
    border: "ivory floral border with miniature hunting-scene cartouches",
    palette: "turquoise, coral red, saffron gold, spring green and rose pink",
    fringe: "long, dense, pure-white silk fringe",
  },
  {
    id: "treeoflife",
    label: "Tree of Life (turquoise)",
    name: "Qom Tree-of-Life",
    field: "luminous turquoise",
    motif: "a flowering tree of life with pink blossom clusters, two golden deer drinking from a winding sapphire stream",
    border: "cream border of scrolling vines and rosettes",
    palette: "turquoise, blush pink, antique gold, leaf green and sapphire",
    fringe: "long white silk fringe",
  },
  {
    id: "redmedallion",
    label: "Red floral medallion",
    name: "Isfahan-style Red Medallion",
    field: "rich ruby red",
    motif: "a radiant central star medallion surrounded by dense shah-abbasi palmettes and arabesque flowers",
    border: "royal-blue border with golden floral cartouches",
    palette: "ruby red, royal blue, gold, ivory and emerald",
    fringe: "thick knotted ivory fringe",
  },
  {
    id: "goldblack",
    label: "Gold on black (Versailles)",
    name: "Versailles Gold-on-Black",
    field: "jet black",
    motif: "an ornate baroque gold medallion with symmetric gilded acanthus scrollwork, like embroidered gold thread",
    border: "narrow black-and-gold ribbon border",
    palette: "antique gold, bronze and deep black",
    fringe: "pale champagne fringe",
  },
  {
    id: "creamstar",
    label: "Cream Heriz star",
    name: "Cream Star Medallion",
    field: "soft cream-ivory",
    motif: "a geometric eight-point star medallion in dusty pink, indigo and teal with stylised bird corners",
    border: "rose-and-sage floral border",
    palette: "cream, dusty rose, indigo, teal and sage",
    fringe: "white cotton fringe",
  },
  {
    id: "blueoval",
    label: "Royal blue oval",
    name: "Royal Blue Oval Medallion",
    field: "royal sapphire blue",
    motif: "a sunburst oval medallion of concentric lace-like rings radiating fine golden tracery",
    border: "gold border with turquoise palmettes",
    palette: "sapphire, gold, turquoise, ivory and crimson",
    fringe: "bright white silk fringe",
  },
];

/* ---------- Shared prompt blocks ---------- */

function carpetBlock(c) {
  return (
    `THE CARPET — the hero of the image: a ${c.size} Persian rug, ` +
    `${c.name ? `"${c.name}", ` : ""}woven from ${c.material}. ` +
    `Field of ${c.field}, patterned with ${c.motif}. ` +
    `Framed by ${c.border}. Colour palette: ${c.palette}. Finished with ${c.fringe}.`
  );
}

function silkTextureBlock() {
  return (
    "SILK REALISM (critical): the pile has the liquid, directional lustre of real silk — " +
    "where the nap changes direction the colours shift from deeply saturated to a pale silvery sheen, " +
    "creating soft light-bands across the field. At close range individual knots are visible like fine " +
    "petit-point stitches (over one million knots per square metre), with crisp pencil-thin dark outlines " +
    "around every motif. The fringe consists of hundreds of distinct glossy strands, slightly uneven and " +
    "naturally splayed, each catching the light. The rug lies with true fabric physics — gentle waves, " +
    "a softly rolled corner, real weight and drape. Absolutely no plastic, printed or flat appearance."
  );
}

function fidelityBlock() {
  return (
    "DESIGN FIDELITY: use the attached photograph of the rug as the exact design reference — " +
    "reproduce its pattern, motifs, colours, border and fringe faithfully, only re-lighting and " +
    "re-staging it inside this scene. Do not invent a different carpet design."
  );
}

const GRADES = {
  rich: "Colour grade: rich, deeply saturated cinema grade that lets the carpet's dyes glow against the scene.",
  "bw-rug":
    "Colour grade: the entire scene is graded in elegant monochrome black-and-white — EXCEPT the carpet, which remains in full vivid colour, the only coloured object in the frame.",
  golden: "Colour grade: warm golden-hour grade, honeyed highlights and soft amber shadows.",
  cool: "Colour grade: cool, desaturated high-end commercial grade with clean blacks; the carpet's warm dyes become the focal contrast.",
  bw: "Colour grade: timeless fine-art black and white, deep blacks, silver mid-tones, strong tonal separation.",
};

const MOODS = {
  cinematic: "Overall mood: cinematic, dramatic, mysterious — like a frame from an epic film.",
  editorial: "Overall mood: high-fashion magazine editorial — poised, expensive, art-directed to perfection.",
  heritage: "Overall mood: warm, soulful celebration of Persian craftsmanship and heritage.",
  minimal: "Overall mood: minimal, architectural, gallery-clean — generous negative space.",
  opulent: "Overall mood: opulent royal Persian splendour, lavish and golden.",
};

function qualityBlock(aspect) {
  return (
    `Ultra-photorealistic, shot for a premium advertising campaign. Medium-format digital look ` +
    `(Hasselblad H6D, 100 MP), razor-sharp micro-detail in the carpet weave, natural skin and material ` +
    `textures, true-to-life colour, professional retouching. Aspect ratio ${aspect}. ` +
    `Avoid: cartoonish or painterly rendering, warped or melted carpet pattern, repeated-texture artifacts, ` +
    `extra limbs or fingers, plastic skin, watermark, text overlays.`
  );
}

/* ---------- Scene library ---------- */
/* Each scene: id, category, title, blurb, needsModel, build(c, d) -> scene-specific paragraphs */

const SCENES = [
  /* ---- MODEL + CREATURE ---- */
  {
    id: "white-horse",
    category: "Creature",
    title: "The One — White Horse Among Black Horses",
    blurb: "Your reference shot: model on a white horse in a sea of black Friesians, the rug as her saddle blanket.",
    needsModel: true,
    build: (c, d) => [
      `A breathtaking symmetrical fashion editorial: ${d.model} sits perfectly centred astride a pure-white Andalusian horse, ` +
        `facing the camera dead-on with a calm, powerful gaze. Surrounding her in tight formation stand a dozen jet-black Friesian horses, ` +
        `heads bowed, filling the entire frame edge-to-edge like a living dark wall — she and the white horse are the only bright forms.`,
      `The Persian rug is draped over the white horse's back as a royal saddle blanket beneath her, its full pattern displayed ` +
        `across the horse's flank, fringe swaying against the white coat. The rug's colours are the jewel of the composition.`,
      `Shot straight-on at chest height, 85 mm lens at f/4, soft overcast courtyard light from above, fine film grain.`,
    ],
  },
  {
    id: "panther",
    category: "Creature",
    title: "Black Panther on the Medallion",
    blurb: "A sleek black panther lying regally on the rug in a marble palace hall.",
    needsModel: false,
    build: (c) => [
      `Inside a vast Persian palace hall of pale veined marble and mirrored muqarnas vaulting, the rug is laid perfectly flat, ` +
        `centred on the polished floor which softly mirrors its colours. A magnificent black panther lies on the rug's central ` +
        `medallion in a sphinx pose, head high, golden eyes locked on the camera, its glossy black coat contrasting with the silk pile.`,
      `One shaft of warm window light rakes across the carpet at a low angle, igniting the silk sheen and modelling every knot; ` +
        `the rest of the hall falls into soft shadow.`,
      `Symmetrical one-point composition, 50 mm lens at f/5.6, camera at floor level for a low majestic perspective.`,
    ],
  },
  {
    id: "falcon",
    category: "Creature",
    title: "The Falconer's Bazaar",
    blurb: "A hunting falcon spreads its wings as the rug hangs behind in dusty bazaar light.",
    needsModel: false,
    build: (c) => [
      `In a centuries-old vaulted bazaar in Kashan, the rug hangs vertically from a dark timber beam, perfectly frontal to the camera ` +
        `like a tapestry, gently rippling. A regal saker falcon, wings spread wide mid-landing, descends toward a leather-gloved hand ` +
        `entering the frame from the side — the falcon's spread feathers echoing the rug's bird motifs.`,
      `Dust motes drift in golden shafts of light falling through skylight oculi above, grazing the carpet surface so the silk pile ` +
        `glitters and every knot reads clearly.`,
      `135 mm lens at f/2.8, falcon and carpet both tack-sharp, background arches melting into warm bokeh.`,
    ],
  },
  {
    id: "persian-cat",
    category: "Creature",
    title: "The Persian Cat's Throne",
    blurb: "A doll-faced white Persian cat curled on the rug in a sunlit alcove — irresistible social content.",
    needsModel: false,
    build: (c) => [
      `A cosy sunlit alcove with an arched window of stained glass: the rug is spread across a low wooden daybed, fringe hanging ` +
        `over the edge. A luxurious white Persian cat with copper eyes sits like royalty at the centre of the rug, tail wrapped, ` +
        `looking straight into the lens.`,
      `Late-afternoon sun through the stained glass throws faint jewels of coloured light across the silk; where the direct light ` +
        `lands, the pile shines like satin and individual fibres glow at the rim of the cat's fur.`,
      `Intimate 35 mm lens at f/2, eye-level with the cat, shallow focus holding both the cat's face and the rug's medallion.`,
    ],
  },

  /* ---- MODEL ---- */
  {
    id: "staircase",
    category: "Model",
    title: "The Unrolling Staircase",
    blurb: "The rug cascades down a grand stone staircase; the model descends barefoot along it.",
    needsModel: true,
    build: (c, d) => [
      `A grand weathered stone staircase inside a historic Persian mansion: the rug is unrolled down the steps like a royal runner, ` +
        `flowing over each tread with natural folds and creases, its fringe resting on the bottom step. ${capitalize(d.model)} descends ` +
        `barefoot along the carpet in a flowing gown, one hand grazing the stone balustrade, gaze over her shoulder to camera.`,
      `Each fold of the rug catches a different angle of window light, so the silk alternates bright and deep along the cascade — ` +
        `a living demonstration of directional sheen.`,
      `Low camera position at the foot of the stairs, 35 mm lens at f/4, the carpet leading the eye up to the model.`,
    ],
  },
  {
    id: "cape",
    category: "Model",
    title: "The Carpet Couture Cape",
    blurb: "High-concept fashion: the rug worn over the shoulders as a sculptural couture cape.",
    needsModel: true,
    build: (c, d) => [
      `A stark fashion studio with a hand-painted grey canvas backdrop: ${d.model} stands in profile then turns her face to camera, ` +
        `wearing the Persian rug itself draped over her shoulders as a monumental couture cape — the full pattern displayed down her ` +
        `back, fringe sweeping the floor like a train, the rolled collar showing the rug's backing weave and knot structure.`,
      `One large softbox key from camera-left and a hard rim light from behind trace the silk's lustre along every fold of the "cape".`,
      `Full-length fashion framing, 85 mm at f/8, crisp and sculptural, Irving Penn studio energy.`,
    ],
  },
  {
    id: "weaver",
    category: "Model",
    title: "Hands of the Master",
    blurb: "Heritage close-up: weathered hands of a master weaver brushing the finished pile.",
    needsModel: false,
    build: (c) => [
      `An intimate heritage close-up inside a traditional workshop: the weathered, dignified hands of an elderly master weaver ` +
        `sweep slowly across the finished rug's surface, fingers parting the pile against the nap so a bright silvery wave of sheen ` +
        `follows their motion, revealing the saturated colour beneath.`,
      `The frame is filled by the carpet at a 30-degree angle; behind, softly out of focus, the wooden loom and hanging skeins of ` +
        `dyed silk thread in the rug's exact palette.`,
      `Macro-leaning 100 mm lens at f/4, raking window light from the side, every knot and the hands' skin texture in honest detail.`,
    ],
  },
  {
    id: "tea-house",
    category: "Model",
    title: "Midnight Tea House",
    blurb: "The model lounges on cushions, the rug glowing under low lantern light.",
    needsModel: true,
    build: (c, d) => [
      `A dim, atmospheric Persian tea house at night: the rug covers a raised wooden takht platform scattered with silk cushions. ` +
        `${capitalize(d.model)} reclines on one elbow upon it, holding a small gold-rimmed tea glass, steam curling upward, ` +
        `eyes to camera.`,
      `A single brass lantern above casts warm pooled light onto the carpet's centre, its medallion glowing like embers while the ` +
        `edges fade into shadow; tiny lantern reflections sparkle in the silk pile.`,
      `Moody 50 mm at f/1.8, chiaroscuro lighting, Caravaggio-like warmth, rich shadow detail preserved.`,
    ],
  },

  /* ---- CAR ---- */
  {
    id: "car-bonnet",
    category: "Car",
    title: "Classic Heritage, Modern Living",
    blurb: "Your reference ad: rug draped over a dark luxury sedan, model leaning against the fender.",
    needsModel: true,
    build: (c, d) => [
      `A premium automotive-style studio advertisement: a midnight-black luxury sedan stands on a seamless light-grey cyclorama. ` +
        `The Persian rug is draped diagonally across the bonnet and front fender, flowing over the headlight with natural heavy folds, ` +
        `fringe hanging beside the front wheel. ${capitalize(d.model)} leans casually against the fender beside the rug, ` +
        `sunglasses on, one ankle crossed.`,
      `Giant overhead softbox creates a long clean highlight down the car's body, while the rug breaks that gloss with its rich ` +
        `matte-and-sheen silk texture — paint reflection versus textile lustre in one frame.`,
      `Wide 35 mm automotive framing at f/8, slight low angle, everything tack sharp, premium print-ad finish.`,
    ],
  },
  {
    id: "car-desert",
    category: "Car",
    title: "Dune Runner",
    blurb: "A vintage Mercedes on a desert dune at dusk, the rug unrolled on the sand beside it.",
    needsModel: false,
    build: (c) => [
      `Golden dusk in the Maranjab desert: a polished vintage 1970s Mercedes SE in champagne beige is parked on the crest of a ` +
        `rippled sand dune. Beside it, the rug is unrolled flat on the sand like a private oasis, one corner flipped by the wind, ` +
        `a brass tea set and two cushions resting on it.`,
      `The low sun skims across both the sand ripples and the carpet pile at the same raking angle, making the silk blaze with ` +
        `directional sheen against the matte sand — texture versus texture.`,
      `Cinematic 24 mm wide shot at f/11, long soft shadows, warm Lawrence-of-Arabia palette.`,
    ],
  },
  {
    id: "car-model-night",
    category: "Car",
    title: "Neon Bazaar Drive-In",
    blurb: "Model + supercar + rug at night under bazaar arches — old craft meets new money.",
    needsModel: true,
    build: (c, d) => [
      `Night scene under the brick arches of an ancient caravanserai courtyard: a pearl-white supercar with doors up is parked on ` +
        `ancient cobblestones, and the Persian rug is laid out royally in front of it like a red-carpet arrival. ${capitalize(d.model)} ` +
        `steps out of the car onto the rug, mid-stride toward camera.`,
      `Warm string lights and lanterns along the arches reflect in the car's paint, while a cool moonlight wash from above gives the ` +
        `rug's silk a cold-silver edge sheen over its warm colours — dual-tone lighting, old craft meeting new wealth.`,
      `Editorial 35 mm at f/2.8, slight Dutch tilt avoided, motion frozen, glamorous and confident.`,
    ],
  },

  /* ---- PRODUCT & TEXTURE ---- */
  {
    id: "macro",
    category: "Texture",
    title: "One Million Knots — Macro Hero",
    blurb: "Extreme macro across the pile: knots, outlines and fringe — proof of quality.",
    needsModel: false,
    build: (c) => [
      `An extreme macro product hero of the rug's surface at a 20-degree raking angle: the focal plane runs along the transition ` +
        `from the border into the field, where individual knots resolve like tight rows of petit-point stitches and the pattern's ` +
        `pencil-thin outlines stay razor crisp. In the near foreground, the fringe enters the frame as glowing out-of-focus silk strands.`,
      `A single hard light skims across the pile from the far side so each fibre throws a micro-shadow; where the nap shifts, a bright ` +
        `silver band of sheen crosses the colours like light on satin.`,
      `100 mm macro at f/5.6, focus stacked sharpness across the centre band, museum-grade product photography on black.`,
    ],
  },
  {
    id: "floating-water",
    category: "Texture",
    title: "Reflections of Fin Garden",
    blurb: "The rug floats above the turquoise pool of a Persian garden, mirrored perfectly.",
    needsModel: false,
    build: (c) => [
      `In the historic Fin Garden of Kashan, the rug levitates fifty centimetres above the long turquoise reflecting pool, ` +
        `perfectly horizontal and frontal to camera, fringe hanging still. The mirror-calm water reflects the rug's full pattern ` +
        `and the rows of cypress trees and ochre pavilion behind.`,
      `Soft late light fills the garden; the silk's sheen answers the water's shimmer — two kinds of liquid light in one frame.`,
      `Centred symmetrical composition, 50 mm at f/8, hyperreal yet believable, the only surreal element is the gentle levitation.`,
    ],
  },
  {
    id: "gallery",
    category: "Texture",
    title: "The Gallery Wall",
    blurb: "Minimal: the rug as art, spotlit on a concrete gallery wall.",
    needsModel: false,
    build: (c) => [
      `A vast minimalist concrete gallery: the rug hangs flat on the bare wall like a masterpiece painting, a single museum ` +
        `spotlight bathing it precisely edge-to-edge while the wall around falls to deep grey. A lone visitor stands far to the side ` +
        `in silhouette, small against the scale, contemplating it.`,
      `The spotlight's angle is slightly steep, so the upper field shows saturated colour and the lower field a soft silken gleam — ` +
        `one rug, two moods, proving the silk's directional life even hung on a wall.`,
      `35 mm at f/5.6, generous negative space, Kinfolk-magazine restraint.`,
    ],
  },
  {
    id: "flying",
    category: "Texture",
    title: "The Flying Carpet — Blue Hour",
    blurb: "The legend, photographed like reality: the rug soaring over the city at blue hour.",
    needsModel: true,
    build: (c, d) => [
      `Blue hour above the historic skyline of Isfahan: the Persian rug flies through the air like the legend made real, ` +
        `photographed as if from a helicopter alongside it. The rug bends gently with the wind like a heavy textile would — ` +
        `leading edge curled up, fringe streaming back. ${capitalize(d.model)} sits cross-legged and serene at its centre, ` +
        `coat rippling, looking toward the glowing turquoise dome of the Shah Mosque below.`,
      `City lights twinkle far beneath; the cold blue ambient light wraps the scene while the warm city glow underlights the rug's ` +
        `fringe and the silk pile shimmers between the two colour temperatures.`,
      `70 mm at f/2.8 with believable atmospheric haze and depth — rendered with documentary realism, not fantasy-painting style.`,
    ],
  },
];

const CATEGORIES = ["All", "Model", "Car", "Creature", "Texture"];

/* ---------- Engine ---------- */

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function readCarpet() {
  return {
    name: val("c-name"),
    field: val("c-field") || "deep midnight-navy",
    motif: val("c-motif") || "a radiant central medallion with arabesque flowers",
    border: val("c-border") || "an ivory floral border",
    palette: val("c-palette") || "jewel tones of red, blue, gold and ivory",
    fringe: val("c-fringe") || "long white silk fringe",
    size: val("c-size"),
    material: val("c-material"),
    reference: document.getElementById("c-reference").checked,
  };
}

function readDirection() {
  return {
    mood: val("d-mood"),
    grade: val("d-grade"),
    aspect: val("d-aspect"),
    model: val("d-model"),
  };
}

function val(id) {
  return document.getElementById(id).value.trim();
}

function buildPrompt(scene, c, d) {
  const parts = [];
  parts.push(...scene.build(c, d));
  parts.push(carpetBlock(c));
  parts.push(silkTextureBlock());
  if (c.reference) parts.push(fidelityBlock());
  parts.push(MOODS[d.mood] + " " + GRADES[d.grade]);
  parts.push(qualityBlock(d.aspect));
  return parts.join("\n\n");
}

/* ---------- UI ---------- */

const selectedScenes = new Set(["white-horse", "car-bonnet", "macro"]);
let activeCategory = "All";
let lastResults = [];

function renderPresets() {
  const el = document.getElementById("presets");
  el.innerHTML = "";
  PRESETS.forEach((p) => {
    const b = document.createElement("button");
    b.className = "preset";
    b.textContent = p.label;
    b.onclick = () => {
      document.querySelectorAll(".preset").forEach((x) => x.classList.remove("active"));
      b.classList.add("active");
      setVal("c-name", p.name);
      setVal("c-field", p.field);
      setVal("c-motif", p.motif);
      setVal("c-border", p.border);
      setVal("c-palette", p.palette);
      setVal("c-fringe", p.fringe);
    };
    el.appendChild(b);
  });
}

function setVal(id, v) {
  document.getElementById(id).value = v;
}

function renderFilter() {
  const el = document.getElementById("scene-filter");
  el.innerHTML = "";
  CATEGORIES.forEach((cat) => {
    const b = document.createElement("button");
    b.textContent = cat;
    b.className = cat === activeCategory ? "active" : "";
    b.onclick = () => {
      activeCategory = cat;
      renderFilter();
      renderScenes();
    };
    el.appendChild(b);
  });
}

function renderScenes() {
  const el = document.getElementById("scenes");
  el.innerHTML = "";
  SCENES.filter((s) => activeCategory === "All" || s.category === activeCategory).forEach((s) => {
    const card = document.createElement("div");
    card.className = "scene" + (selectedScenes.has(s.id) ? " selected" : "");
    card.innerHTML = `<span class="tag">${s.category}</span><span class="tick">✦</span><h3>${s.title}</h3><p>${s.blurb}</p>`;
    card.onclick = () => {
      selectedScenes.has(s.id) ? selectedScenes.delete(s.id) : selectedScenes.add(s.id);
      card.classList.toggle("selected");
    };
    el.appendChild(card);
  });
}

function generate() {
  const c = readCarpet();
  const d = readDirection();
  const out = document.getElementById("output");
  out.innerHTML = "";
  lastResults = [];

  const scenes = SCENES.filter((s) => selectedScenes.has(s.id));
  if (!scenes.length) {
    out.innerHTML = `<div class="prompt-card"><p>Select at least one scene above.</p></div>`;
    return;
  }

  scenes.forEach((s, i) => {
    const prompt = buildPrompt(s, c, d);
    lastResults.push({ shot: i + 1, scene: s.title, category: s.category, aspect: d.aspect, prompt });

    const card = document.createElement("div");
    card.className = "prompt-card";
    const header = document.createElement("header");
    header.innerHTML = `<h3>Shot ${i + 1} — ${s.title}</h3><span class="meta">${s.category.toUpperCase()} · ${d.aspect}</span>`;
    const pre = document.createElement("pre");
    pre.textContent = prompt;
    const btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.textContent = "Copy prompt";
    btn.onclick = () => copyText(prompt, btn);
    card.append(header, pre, btn);
    out.appendChild(card);
  });

  document.getElementById("copy-all").disabled = false;
  document.getElementById("export-json").disabled = false;
  out.scrollIntoView({ behavior: "smooth" });
}

function copyText(text, btn) {
  navigator.clipboard.writeText(text).then(() => {
    const old = btn.textContent;
    btn.textContent = "Copied ✓";
    setTimeout(() => (btn.textContent = old), 1400);
  });
}

document.getElementById("generate").onclick = generate;

document.getElementById("copy-all").onclick = (e) => {
  const all = lastResults.map((r) => `### Shot ${r.shot} — ${r.scene} (${r.aspect})\n\n${r.prompt}`).join("\n\n---\n\n");
  copyText(all, e.target);
};

document.getElementById("export-json").onclick = () => {
  const blob = new Blob([JSON.stringify(lastResults, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "silk-atelier-shotlist.json";
  a.click();
  URL.revokeObjectURL(a.href);
};

renderPresets();
renderFilter();
renderScenes();
