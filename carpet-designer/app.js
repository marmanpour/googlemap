// ===================== Color helpers =====================

function hexToRgb(hex) {
  hex = hex.replace('#', '');
  if (hex.length === 3) hex = hex.split('').map(c => c + c).join('');
  const num = parseInt(hex, 16);
  return [(num >> 16) & 255, (num >> 8) & 255, num & 255];
}

function rgbToHex(r, g, b) {
  return '#' + [r, g, b].map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
}

function srgbToLinear(c) {
  c /= 255;
  return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

// D65 reference white
const REF_X = 95.047, REF_Y = 100.0, REF_Z = 108.883;

function rgbToLab(r, g, b) {
  const rl = srgbToLinear(r), gl = srgbToLinear(g), bl = srgbToLinear(b);
  const x = (rl * 0.4124564 + gl * 0.3575761 + bl * 0.1804375) * 100;
  const y = (rl * 0.2126729 + gl * 0.7151522 + bl * 0.0721750) * 100;
  const z = (rl * 0.0193339 + gl * 0.1191920 + bl * 0.9503041) * 100;

  const fx = labF(x / REF_X), fy = labF(y / REF_Y), fz = labF(z / REF_Z);
  return [116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)];
}

function labF(t) {
  return t > 0.008856 ? Math.cbrt(t) : (7.787 * t + 16 / 116);
}

function labDistance(a, b) {
  const dl = a[0] - b[0], da = a[1] - b[1], db = a[2] - b[2];
  return dl * dl + da * da + db * db;
}

// ===================== K-means clustering =====================

function kMeans(samples, k, iterations = 12) {
  // samples: array of [L,a,b]
  const n = samples.length;
  k = Math.min(k, n);

  // k-means++ initialization
  const centroids = [];
  centroids.push(samples[Math.floor(Math.random() * n)].slice());
  while (centroids.length < k) {
    const distances = samples.map(s => {
      let min = Infinity;
      for (const c of centroids) {
        const d = labDistance(s, c);
        if (d < min) min = d;
      }
      return min;
    });
    const total = distances.reduce((a, b) => a + b, 0);
    let r = Math.random() * total;
    let idx = 0;
    for (; idx < n; idx++) {
      r -= distances[idx];
      if (r <= 0) break;
    }
    centroids.push(samples[Math.min(idx, n - 1)].slice());
  }

  let assignments = new Array(n).fill(0);
  for (let iter = 0; iter < iterations; iter++) {
    // assign
    for (let i = 0; i < n; i++) {
      let best = 0, bestDist = Infinity;
      for (let c = 0; c < k; c++) {
        const d = labDistance(samples[i], centroids[c]);
        if (d < bestDist) { bestDist = d; best = c; }
      }
      assignments[i] = best;
    }
    // update
    const sums = Array.from({ length: k }, () => [0, 0, 0, 0]);
    for (let i = 0; i < n; i++) {
      const c = assignments[i];
      sums[c][0] += samples[i][0];
      sums[c][1] += samples[i][1];
      sums[c][2] += samples[i][2];
      sums[c][3] += 1;
    }
    for (let c = 0; c < k; c++) {
      if (sums[c][3] > 0) {
        centroids[c] = [sums[c][0] / sums[c][3], sums[c][1] / sums[c][3], sums[c][2] / sums[c][3]];
      }
    }
  }
  return centroids;
}

function labToRgbApprox(lab, samples, assignments) {
  // Not used directly; we instead average the original RGB per cluster for accuracy.
}

// ===================== App state =====================

const state = {
  factoryPalette: [], // [{hex, name, lab}]
  factoryImage: null,
  designImage: null,
  grid: null, // {cols, rows, cells: Uint16Array of palette indices}
  activeBrush: -1,
};

const PROFILE_KEY = 'carpetDesigner.factoryProfiles';

// ===================== DOM refs =====================

const $ = (id) => document.getElementById(id);

const factoryImageInput = $('factory-image');
const factoryCanvas = $('factory-canvas');
const extractBtn = $('extract-btn');
const paletteCountInput = $('palette-count');
const paletteCountLabel = $('palette-count-label');
const factoryPaletteEl = $('factory-palette');
const manualColorInput = $('manual-color');
const addColorBtn = $('add-color-btn');

const profileNameInput = $('profile-name');
const profileSelect = $('profile-select');
const saveProfileBtn = $('save-profile-btn');
const loadProfileBtn = $('load-profile-btn');
const deleteProfileBtn = $('delete-profile-btn');

const designImageInput = $('design-image');
const designCanvas = $('design-canvas');

const sizeWidth = $('size-width');
const sizeHeight = $('size-height');
const sizeDensity = $('size-density');
const computedCols = $('computed-cols');
const computedRows = $('computed-rows');
const manualCols = $('manual-cols');
const manualRows = $('manual-rows');
const generateBtn = $('generate-btn');

const outputPanel = $('output-panel');
const zoomInput = $('zoom');
const gridInfo = $('grid-info');
const brushPaletteEl = $('brush-palette');
const mapCanvas = $('map-canvas');
const legendTableBody = document.querySelector('#legend-table tbody');

const exportPngBtn = $('export-png');
const exportCsvBtn = $('export-csv');
const exportJsonBtn = $('export-json');

// ===================== Image loading helpers =====================

function loadImageToCanvas(file, canvas, callback) {
  const reader = new FileReader();
  reader.onload = (e) => {
    const img = new Image();
    img.onload = () => {
      const maxW = 600, maxH = 400;
      let w = img.width, h = img.height;
      const scale = Math.min(1, maxW / w, maxH / h);
      canvas.width = Math.round(w * scale);
      canvas.height = Math.round(h * scale);
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      callback(img, canvas);
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

// ===================== Step 1: factory palette =====================

paletteCountInput.addEventListener('input', () => {
  paletteCountLabel.textContent = paletteCountInput.value + ' رنگ';
});

factoryImageInput.addEventListener('change', () => {
  const file = factoryImageInput.files[0];
  if (!file) return;
  loadImageToCanvas(file, factoryCanvas, (img) => {
    state.factoryImage = img;
    extractBtn.disabled = false;
  });
});

extractBtn.addEventListener('click', () => {
  const ctx = factoryCanvas.getContext('2d');
  const w = factoryCanvas.width, h = factoryCanvas.height;
  const data = ctx.getImageData(0, 0, w, h).data;

  // Subsample pixels for performance
  const samples = [];
  const rgbSamples = [];
  const step = Math.max(1, Math.floor((w * h) / 8000));
  for (let i = 0; i < w * h; i += step) {
    const idx = i * 4;
    const r = data[idx], g = data[idx + 1], b = data[idx + 2], a = data[idx + 3];
    if (a < 128) continue;
    samples.push(rgbToLab(r, g, b));
    rgbSamples.push([r, g, b]);
  }

  const k = parseInt(paletteCountInput.value, 10);
  const centroids = kMeans(samples, k, 10);

  // Assign each sample to nearest centroid and average actual RGB for accurate swatch color
  const sums = Array.from({ length: centroids.length }, () => [0, 0, 0, 0]);
  for (let i = 0; i < samples.length; i++) {
    let best = 0, bestDist = Infinity;
    for (let c = 0; c < centroids.length; c++) {
      const d = labDistance(samples[i], centroids[c]);
      if (d < bestDist) { bestDist = d; best = c; }
    }
    sums[best][0] += rgbSamples[i][0];
    sums[best][1] += rgbSamples[i][1];
    sums[best][2] += rgbSamples[i][2];
    sums[best][3] += 1;
  }

  state.factoryPalette = [];
  sums.forEach((s, i) => {
    if (s[3] === 0) return;
    const r = s[0] / s[3], g = s[1] / s[3], b = s[2] / s[3];
    state.factoryPalette.push({
      hex: rgbToHex(r, g, b),
      name: 'رنگ ' + (state.factoryPalette.length + 1),
      lab: rgbToLab(r, g, b),
    });
  });

  // Sort palette from light to dark for nicer display
  state.factoryPalette.sort((a, b) => b.lab[0] - a.lab[0]);
  state.factoryPalette.forEach((p, i) => p.name = 'رنگ ' + (i + 1));

  renderFactoryPalette();
});

addColorBtn.addEventListener('click', () => {
  const hex = manualColorInput.value;
  const [r, g, b] = hexToRgb(hex);
  state.factoryPalette.push({
    hex,
    name: 'رنگ ' + (state.factoryPalette.length + 1),
    lab: rgbToLab(r, g, b),
  });
  renderFactoryPalette();
});

function renderFactoryPalette() {
  factoryPaletteEl.innerHTML = '';
  state.factoryPalette.forEach((color, i) => {
    const swatch = document.createElement('div');
    swatch.className = 'swatch';

    const box = document.createElement('div');
    box.className = 'color-box';
    box.style.background = color.hex;

    const nameInput = document.createElement('input');
    nameInput.type = 'text';
    nameInput.value = color.name;
    nameInput.addEventListener('input', () => {
      color.name = nameInput.value;
    });

    const hexLabel = document.createElement('div');
    hexLabel.className = 'hex';
    hexLabel.textContent = color.hex;

    const removeBtn = document.createElement('button');
    removeBtn.className = 'remove';
    removeBtn.textContent = 'حذف';
    removeBtn.addEventListener('click', () => {
      state.factoryPalette.splice(i, 1);
      renderFactoryPalette();
    });

    swatch.appendChild(box);
    swatch.appendChild(nameInput);
    swatch.appendChild(hexLabel);
    swatch.appendChild(removeBtn);
    factoryPaletteEl.appendChild(swatch);
  });
}

// ===================== Profile save/load (localStorage) =====================

function getProfiles() {
  try {
    return JSON.parse(localStorage.getItem(PROFILE_KEY)) || {};
  } catch {
    return {};
  }
}

function saveProfiles(profiles) {
  localStorage.setItem(PROFILE_KEY, JSON.stringify(profiles));
}

function refreshProfileSelect() {
  const profiles = getProfiles();
  profileSelect.innerHTML = '<option value="">— انتخاب کنید —</option>';
  Object.keys(profiles).forEach((name) => {
    const opt = document.createElement('option');
    opt.value = name;
    opt.textContent = name;
    profileSelect.appendChild(opt);
  });
}

saveProfileBtn.addEventListener('click', () => {
  const name = profileNameInput.value.trim();
  if (!name) {
    alert('لطفاً یک نام برای پروفایل وارد کنید.');
    return;
  }
  if (state.factoryPalette.length === 0) {
    alert('پالتی برای ذخیره وجود ندارد.');
    return;
  }
  const profiles = getProfiles();
  profiles[name] = state.factoryPalette.map(c => ({ hex: c.hex, name: c.name }));
  saveProfiles(profiles);
  refreshProfileSelect();
  profileSelect.value = name;
});

loadProfileBtn.addEventListener('click', () => {
  const name = profileSelect.value;
  if (!name) return;
  const profiles = getProfiles();
  const palette = profiles[name];
  if (!palette) return;
  state.factoryPalette = palette.map(c => {
    const [r, g, b] = hexToRgb(c.hex);
    return { hex: c.hex, name: c.name, lab: rgbToLab(r, g, b) };
  });
  profileNameInput.value = name;
  renderFactoryPalette();
});

deleteProfileBtn.addEventListener('click', () => {
  const name = profileSelect.value;
  if (!name) return;
  const profiles = getProfiles();
  delete profiles[name];
  saveProfiles(profiles);
  refreshProfileSelect();
});

refreshProfileSelect();

// ===================== Step 2: customer design =====================

designImageInput.addEventListener('change', () => {
  const file = designImageInput.files[0];
  if (!file) return;
  loadImageToCanvas(file, designCanvas, (img) => {
    state.designImage = img;
  });
});

// ===================== Step 3: grid size computation =====================

function recomputeGridSize() {
  const widthCm = parseFloat(sizeWidth.value) || 0;
  const heightCm = parseFloat(sizeHeight.value) || 0;
  const density = parseFloat(sizeDensity.value) || 0; // knots per 7cm

  const cols = Math.round((widthCm / 7) * density);
  const rows = Math.round((heightCm / 7) * density);

  computedCols.textContent = cols || '—';
  computedRows.textContent = rows || '—';

  if (!manualCols.dataset.touched) manualCols.value = cols || '';
  if (!manualRows.dataset.touched) manualRows.value = rows || '';
}

[sizeWidth, sizeHeight, sizeDensity].forEach(el => el.addEventListener('input', recomputeGridSize));
manualCols.addEventListener('input', () => { manualCols.dataset.touched = '1'; });
manualRows.addEventListener('input', () => { manualRows.dataset.touched = '1'; });
recomputeGridSize();

// ===================== Step 4: generate map =====================

const MAX_GRID_DIM = 400;

generateBtn.addEventListener('click', () => {
  if (!state.designImage) {
    alert('ابتدا تصویر طرح مشتری را آپلود کنید.');
    return;
  }
  if (state.factoryPalette.length === 0) {
    alert('ابتدا پالت رنگ کارخانه را استخراج یا بارگذاری کنید.');
    return;
  }

  let cols = parseInt(manualCols.value, 10);
  let rows = parseInt(manualRows.value, 10);
  if (!cols || !rows) {
    alert('تعداد ستون و ردیف نامعتبر است.');
    return;
  }
  cols = Math.min(cols, MAX_GRID_DIM);
  rows = Math.min(rows, MAX_GRID_DIM);

  // Downsample design image to cols x rows using canvas (averaging via smoothing)
  const off = document.createElement('canvas');
  off.width = cols;
  off.height = rows;
  const offCtx = off.getContext('2d');
  offCtx.imageSmoothingEnabled = true;
  offCtx.imageSmoothingQuality = 'high';
  offCtx.drawImage(state.designImage, 0, 0, cols, rows);
  const data = offCtx.getImageData(0, 0, cols, rows).data;

  const cells = new Uint16Array(cols * rows);
  const paletteLabs = state.factoryPalette.map(c => c.lab);

  for (let i = 0; i < cols * rows; i++) {
    const idx = i * 4;
    const r = data[idx], g = data[idx + 1], b = data[idx + 2];
    const lab = rgbToLab(r, g, b);
    let best = 0, bestDist = Infinity;
    for (let c = 0; c < paletteLabs.length; c++) {
      const d = labDistance(lab, paletteLabs[c]);
      if (d < bestDist) { bestDist = d; best = c; }
    }
    cells[i] = best;
  }

  state.grid = { cols, rows, cells };
  outputPanel.style.display = '';
  renderBrushPalette();
  renderMap();
  renderLegend();
  outputPanel.scrollIntoView({ behavior: 'smooth' });
});

// ===================== Brush palette =====================

function renderBrushPalette() {
  brushPaletteEl.innerHTML = '';
  state.factoryPalette.forEach((color, i) => {
    const swatch = document.createElement('div');
    swatch.className = 'swatch' + (state.activeBrush === i ? ' active' : '');
    swatch.title = color.name;

    const box = document.createElement('div');
    box.className = 'color-box';
    box.style.background = color.hex;

    const label = document.createElement('div');
    label.className = 'hex';
    label.textContent = color.name;

    swatch.appendChild(box);
    swatch.appendChild(label);
    swatch.addEventListener('click', () => {
      state.activeBrush = (state.activeBrush === i) ? -1 : i;
      renderBrushPalette();
    });
    brushPaletteEl.appendChild(swatch);
  });
}

// ===================== Map rendering =====================

let cellSize = parseInt(zoomInput.value, 10);

zoomInput.addEventListener('input', () => {
  cellSize = parseInt(zoomInput.value, 10);
  if (state.grid) renderMap();
});

function renderMap() {
  const { cols, rows, cells } = state.grid;
  mapCanvas.width = cols * cellSize;
  mapCanvas.height = rows * cellSize;
  const ctx = mapCanvas.getContext('2d');

  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      drawCell(ctx, x, y);
    }
  }

  gridInfo.textContent = `${cols} ستون × ${rows} ردیف = ${(cols * rows).toLocaleString('fa-IR')} گره`;
}

function drawCell(ctx, x, y) {
  const { cols, cells } = state.grid;
  const idx = cells[y * cols + x];
  const color = state.factoryPalette[idx];
  ctx.fillStyle = color ? color.hex : '#000000';
  ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);

  // grid lines
  ctx.strokeStyle = ((x % 10 === 0) || (y % 10 === 0)) ? 'rgba(255,255,255,0.35)' : 'rgba(255,255,255,0.08)';
  ctx.lineWidth = 1;
  ctx.strokeRect(x * cellSize + 0.5, y * cellSize + 0.5, cellSize - 1, cellSize - 1);
}

// Painting interaction
let isPainting = false;

mapCanvas.addEventListener('mousedown', (e) => {
  if (state.activeBrush < 0 || !state.grid) return;
  isPainting = true;
  paintAt(e);
});
mapCanvas.addEventListener('mousemove', (e) => {
  if (isPainting) paintAt(e);
});
window.addEventListener('mouseup', () => { isPainting = false; });

function paintAt(e) {
  const rect = mapCanvas.getBoundingClientRect();
  const px = (e.clientX - rect.left) * (mapCanvas.width / rect.width);
  const py = (e.clientY - rect.top) * (mapCanvas.height / rect.height);
  const x = Math.floor(px / cellSize);
  const y = Math.floor(py / cellSize);
  const { cols, rows, cells } = state.grid;
  if (x < 0 || x >= cols || y < 0 || y >= rows) return;
  cells[y * cols + x] = state.activeBrush;
  const ctx = mapCanvas.getContext('2d');
  drawCell(ctx, x, y);
  renderLegend();
}

// ===================== Legend =====================

function renderLegend() {
  const { cols, rows, cells } = state.grid;
  const total = cols * rows;
  const counts = new Array(state.factoryPalette.length).fill(0);
  for (let i = 0; i < cells.length; i++) counts[cells[i]]++;

  legendTableBody.innerHTML = '';
  state.factoryPalette.forEach((color, i) => {
    if (counts[i] === 0) return;
    const tr = document.createElement('tr');
    const pct = ((counts[i] / total) * 100).toFixed(1);
    tr.innerHTML = `
      <td>${i + 1}</td>
      <td><span class="legend-swatch" style="background:${color.hex}"></span> ${color.hex}</td>
      <td>${color.name}</td>
      <td>${counts[i].toLocaleString('fa-IR')}</td>
      <td>${pct}%</td>
    `;
    legendTableBody.appendChild(tr);
  });
}

// ===================== Exports =====================

exportPngBtn.addEventListener('click', () => {
  const link = document.createElement('a');
  link.download = 'carpet-map.png';
  link.href = mapCanvas.toDataURL('image/png');
  link.click();
});

exportCsvBtn.addEventListener('click', () => {
  const { cols, rows, cells } = state.grid;
  const total = cols * rows;
  const counts = new Array(state.factoryPalette.length).fill(0);
  for (let i = 0; i < cells.length; i++) counts[cells[i]]++;

  let csv = 'Legend\r\nCode,Hex,Name,KnotCount,Percent\r\n';
  state.factoryPalette.forEach((color, i) => {
    const pct = ((counts[i] / total) * 100).toFixed(2);
    csv += `${i + 1},${color.hex},"${color.name}",${counts[i]},${pct}\r\n`;
  });

  csv += `\r\nGrid (${cols} cols x ${rows} rows, color codes match Legend above)\r\n`;
  for (let y = 0; y < rows; y++) {
    const row = [];
    for (let x = 0; x < cols; x++) row.push(cells[y * cols + x] + 1);
    csv += row.join(',') + '\r\n';
  }

  downloadText(csv, 'carpet-map.csv', 'text/csv');
});

exportJsonBtn.addEventListener('click', () => {
  const { cols, rows, cells } = state.grid;
  const json = {
    cols,
    rows,
    palette: state.factoryPalette.map(c => ({ hex: c.hex, name: c.name })),
    cells: Array.from(cells),
  };
  downloadText(JSON.stringify(json, null, 2), 'carpet-map.json', 'application/json');
});

function downloadText(content, filename, mime) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
