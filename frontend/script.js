/* ── ClimateLens AI – Frontend Script ─────────────────────────────────────── */

const API = window.location.origin.startsWith('file:') 
  ? 'http://localhost:5000' 
  : '';  // same origin when served by Flask

// Plotly dark layout base
const darkLayout = {
  paper_bgcolor: '#161b22',
  plot_bgcolor: '#0d1117',
  font: { color: '#e6edf3', family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', size: 12 },
  margin: { t: 40, r: 20, b: 50, l: 60 },
  xaxis: { gridcolor: '#30363d', zerolinecolor: '#30363d' },
  yaxis: { gridcolor: '#30363d', zerolinecolor: '#30363d' },
};

const plotConfig = { responsive: true, displayModeBar: true, displaylogo: false };

// Variable display names & units
const VAR_META = {
  temperature:   { label: 'Temperature',  unit: '°C',  color: '#f85149' },
  precipitation: { label: 'Precipitation',unit: 'mm',  color: '#1f6feb' },
  wind_speed:    { label: 'Wind Speed',   unit: 'm/s', color: '#3fb950' },
  humidity:      { label: 'Humidity',     unit: '%',   color: '#a371f7' },
  pressure:      { label: 'Pressure',     unit: 'hPa', color: '#d29922' },
};

// Fallback city list (matches sample dataset)
const DEFAULT_CITIES = [
  'Bangkok','Beijing','Buenos Aires','Cairo','Cape Town',
  'Dubai','Lagos','London','Mexico City','Moscow',
  'Mumbai','Nairobi','New York','Oslo','Paris',
  'Rio de Janeiro','Singapore','Sydney','Tokyo','Toronto'
];

// ── Init ───────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  populateCitySelect(DEFAULT_CITIES);
  // Always reset to sample data on page load so stale uploads don't persist
  fetch(`${API}/reset_dataset`, { method: 'POST' })
    .then(r => r.json())
    .then(data => { if (!data.error) populateSidebar(data); })
    .catch(() => loadDatasetInfo());

  // Wire up city search input
  const input = document.getElementById('citySearchInput');
  const dropdown = document.getElementById('cityDropdown');

  input.addEventListener('focus', () => openDropdown());
  input.addEventListener('input', () => {
    renderDropdown(input.value);
    dropdown.classList.add('open');
    if (input.value !== document.getElementById('citySelect').value) {
      document.getElementById('citySelect').value = '';
    }
  });
  input.addEventListener('blur', () => setTimeout(closeDropdown, 150));

  input.addEventListener('keydown', e => {
    const opts = dropdown.querySelectorAll('.city-option');
    if (!opts.length) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      _activeIdx = Math.min(_activeIdx + 1, opts.length - 1);
      opts.forEach((o, i) => o.classList.toggle('active', i === _activeIdx));
      opts[_activeIdx]?.scrollIntoView({ block: 'nearest' });
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      _activeIdx = Math.max(_activeIdx - 1, 0);
      opts.forEach((o, i) => o.classList.toggle('active', i === _activeIdx));
      opts[_activeIdx]?.scrollIntoView({ block: 'nearest' });
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (_activeIdx >= 0 && opts[_activeIdx]) selectCity(opts[_activeIdx].dataset.city);
    } else if (e.key === 'Escape') {
      closeDropdown();
    }
  });
});

// ── City Search Dropdown ───────────────────────────────────────────────────

let _allCities = [...DEFAULT_CITIES];
let _activeIdx = -1;

function populateCitySelect(cities) {
  _allCities = cities;
  // Reset the hidden value and input display
  document.getElementById('citySelect').value = '';
  document.getElementById('citySearchInput').value = '';
  renderDropdown('');
}

function renderDropdown(query) {
  const dropdown = document.getElementById('cityDropdown');
  const selected = document.getElementById('citySelect').value;
  const q = query.toLowerCase().trim();
  const matches = q
    ? _allCities.filter(c => c.toLowerCase().includes(q))
    : _allCities;

  if (!matches.length) {
    dropdown.innerHTML = `<div class="city-no-results">No cities found</div>`;
    return;
  }

  dropdown.innerHTML = matches.slice(0, 100).map((c, i) =>
    `<div class="city-option${c === selected ? ' selected' : ''}" data-city="${c}" data-idx="${i}">${c}</div>`
  ).join('');

  _activeIdx = -1;

  // Click to select
  dropdown.querySelectorAll('.city-option').forEach(el => {
    el.addEventListener('mousedown', e => {
      e.preventDefault();
      selectCity(el.dataset.city);
    });
  });
}

function selectCity(city) {
  document.getElementById('citySelect').value = city;
  document.getElementById('citySearchInput').value = city;
  closeDropdown();
}

function openDropdown() {
  renderDropdown(document.getElementById('citySearchInput').value);
  document.getElementById('cityDropdown').classList.add('open');
}

function closeDropdown() {
  document.getElementById('cityDropdown').classList.remove('open');
  _activeIdx = -1;
}

// Wire up the search input

async function loadDatasetInfo() {
  try {
    const res = await fetch(`${API}/get_dataset_info`);
    const data = await res.json();
    if (data.error) return;
    populateSidebar(data);
    document.getElementById('datasetBadge').textContent = `📂 ${data.active_file}`;
  } catch (e) {
    console.warn('Could not load dataset info:', e);
  }
}

function populateSidebar(info) {
  // Variables
  const varSel = document.getElementById('variableSelect');
  if (info.variables && info.variables.length) {
    const current = varSel.value;
    varSel.innerHTML = '';
    info.variables.forEach(v => {
      const meta = VAR_META[v] || { label: v.replace(/_/g, ' '), unit: '' };
      const opt = document.createElement('option');
      opt.value = v;
      opt.textContent = `${meta.label}${meta.unit ? ' (' + meta.unit + ')' : ''}`;
      varSel.appendChild(opt);
    });
    if ([...varSel.options].some(o => o.value === current)) varSel.value = current;
  }

  // Cities vs lat/lon points
  const latLonDiv = document.getElementById('latLonSelector');
  if (info.cities && info.cities.length) {
    populateCitySelect(info.cities);
    document.getElementById('citySearchWrap').style.display = '';
    latLonDiv.style.display = 'none';
  } else if (info.lat_lon_points && info.lat_lon_points.length) {
    document.getElementById('citySearchWrap').style.display = 'none';
    latLonDiv.style.display = '';
    const llSel = document.getElementById('latLonSelect');
    llSel.innerHTML = '<option value="">-- Select Location --</option>';
    info.lat_lon_points.forEach(p => {
      const opt = document.createElement('option');
      opt.value = `${p.lat},${p.lon}`;
      opt.textContent = `Lat ${p.lat}, Lon ${p.lon}`;
      llSel.appendChild(opt);
    });
  } else {
    document.getElementById('citySearchWrap').style.display = '';
    latLonDiv.style.display = 'none';
  }

  // Year range hints
  if (info.year_min) {
    document.getElementById('yearFilter').placeholder = `e.g. ${info.year_max}`;
    document.getElementById('compareYear1').placeholder = `Year 1 (e.g. ${info.year_min})`;
    document.getElementById('compareYear2').placeholder = `Year 2 (e.g. ${info.year_max})`;
    document.getElementById('compareYear1').value = info.year_min;
    document.getElementById('compareYear2').value = info.year_max;
  }
}

function onVariableChange() { /* live update could go here */ }

// ── Upload ─────────────────────────────────────────────────────────────────

function onFileSelected(input) {
  const zone = document.getElementById('uploadZone');
  const btn = document.getElementById('uploadBtn');
  const statusEl = document.getElementById('uploadStatus');
  if (input.files && input.files.length) {
    const name = input.files[0].name;
    document.getElementById('uploadZoneText').textContent = name;
    zone.classList.add('has-file');
    btn.disabled = false;
    setStatus(statusEl, '', false);
  }
}

function onDragOver(e) {
  e.preventDefault();
  document.getElementById('uploadZone').classList.add('drag-over');
}

function onDragLeave(e) {
  document.getElementById('uploadZone').classList.remove('drag-over');
}

function onDrop(e) {
  e.preventDefault();
  const zone = document.getElementById('uploadZone');
  zone.classList.remove('drag-over');
  const files = e.dataTransfer.files;
  if (files.length) {
    const input = document.getElementById('fileInput');
    // DataTransfer lets us assign files to the input
    const dt = new DataTransfer();
    dt.items.add(files[0]);
    input.files = dt.files;
    onFileSelected(input);
  }
}

async function resetDataset() {
  const statusEl = document.getElementById('uploadStatus');
  setStatus(statusEl, 'Resetting...', false);
  try {
    const res = await fetch(`${API}/reset_dataset`, { method: 'POST' });
    const data = await res.json();
    if (data.error) { setStatus(statusEl, data.error, true); return; }
    setStatus(statusEl, '✓ Reset to sample data', false);
    document.getElementById('datasetBadge').textContent = `📂 ${data.active_file}`;
    // Reset upload zone
    document.getElementById('uploadZoneText').textContent = 'Click or drag CSV / NetCDF';
    document.getElementById('uploadZone').classList.remove('has-file');
    document.getElementById('uploadBtn').disabled = true;
    document.getElementById('fileInput').value = '';
    document.getElementById('citySearchInput').value = '';
    document.getElementById('citySelect').value = '';
    populateSidebar(data);
  } catch (e) {
    setStatus(statusEl, 'Reset failed.', true);
  }
}

async function uploadDataset() {
  const fileInput = document.getElementById('fileInput');
  const statusEl = document.getElementById('uploadStatus');

  if (!fileInput.files || !fileInput.files.length) {
    setStatus(statusEl, 'Please select a file first.', true);
    return;
  }

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  setStatus(statusEl, 'Uploading...', false);
  document.getElementById('uploadBtn').disabled = true;

  try {
    const res = await fetch(`${API}/upload_dataset`, { method: 'POST', body: formData });
    const data = await res.json();
    if (data.error) {
      setStatus(statusEl, data.error, true);
      document.getElementById('uploadBtn').disabled = false;
      return;
    }
    setStatus(statusEl, `✓ ${data.rows.toLocaleString()} rows loaded`, false);
    document.getElementById('datasetBadge').textContent = `📂 ${fileInput.files[0].name}`;
    document.getElementById('uploadZone').classList.remove('has-file');
    document.getElementById('uploadZoneText').textContent = 'Click or drag CSV / NetCDF';
    fileInput.value = '';
    populateSidebar(data);
  } catch (e) {
    setStatus(statusEl, 'Upload failed. Is the server running?', true);
    document.getElementById('uploadBtn').disabled = false;
  }
}

function setStatus(el, msg, isError) {
  el.textContent = msg;
  el.className = 'status-msg' + (isError ? ' error' : '');
}

// ── Run All ────────────────────────────────────────────────────────────────

async function runAll() {
  showLoading(true);
  try {
    await Promise.all([
      renderHeatmap(),
      renderTimeSeries(),
      renderInsights(),
      renderComparison(),
      renderPrediction(),
    ]);
  } finally {
    showLoading(false);
  }
}

function getParams() {
  const citySelect = document.getElementById('citySelect');
  const latLonSelect = document.getElementById('latLonSelect');
  const latLonDiv = document.getElementById('latLonSelector');

  let city = '', lat = null, lon = null;
  if (latLonDiv.style.display !== 'none' && latLonSelect.value) {
    const parts = latLonSelect.value.split(',');
    lat = parts[0]; lon = parts[1];
  } else {
    city = citySelect.value;
  }

  return {
    variable: document.getElementById('variableSelect').value || 'temperature',
    year: document.getElementById('yearFilter').value,
    month: document.getElementById('monthFilter').value,
    city, lat, lon,
    year1: document.getElementById('compareYear1').value,
    year2: document.getElementById('compareYear2').value,
    yearsAhead: document.getElementById('yearsAhead').value || 10,
  };
}

// ── Heatmap ────────────────────────────────────────────────────────────────

async function renderHeatmap() {
  const { variable, year, month } = getParams();
  const meta = VAR_META[variable] || { label: variable, unit: '' };

  let url = `${API}/get_heatmap_data?variable=${variable}`;
  if (year) url += `&year=${year}`;
  if (month) url += `&month=${month}`;

  const res = await fetch(url);
  const json = await res.json();
  if (json.error || !json.data.length) { showEmpty('heatmapChart', json.error || 'No data'); return; }

  const lats = json.data.map(d => d.lat);
  const lons = json.data.map(d => d.lon);
  const vals = json.data.map(d => d.value);
  const texts = json.data.map(d => `${d.city || ''}<br>Lat: ${d.lat}, Lon: ${d.lon}<br>${meta.label}: ${d.value} ${meta.unit}`);

  const trace = {
    type: 'scattergeo',
    lat: lats, lon: lons,
    text: texts,
    hoverinfo: 'text',
    mode: 'markers',
    marker: {
      size: 14,
      color: vals,
      colorscale: variable === 'temperature' ? 'RdYlBu_r' :
                  variable === 'precipitation' ? 'Blues' :
                  variable === 'wind_speed' ? 'Greens' : 'Purples',
      reversescale: false,
      colorbar: { title: `${meta.label} (${meta.unit})`, thickness: 14, len: 0.7 },
      line: { width: 0.5, color: '#30363d' },
      opacity: 0.85,
    },
  };

  const layout = {
    ...darkLayout,
    title: { text: `Global ${meta.label} Distribution${year ? ' – ' + year : ''}`, font: { size: 14 } },
    margin: { t: 50, r: 10, b: 10, l: 10 },
    geo: {
      showland: true, landcolor: '#1c2330',
      showocean: true, oceancolor: '#0d1117',
      showcoastlines: true, coastlinecolor: '#30363d',
      showframe: false,
      bgcolor: '#0d1117',
      projection: { type: 'natural earth' },
    },
  };

  Plotly.react('heatmapChart', [trace], layout, plotConfig);
}

// ── Time Series ────────────────────────────────────────────────────────────

async function renderTimeSeries() {
  const { variable, city, lat, lon } = getParams();
  const meta = VAR_META[variable] || { label: variable, unit: '' };

  let url = `${API}/get_time_series?variable=${variable}`;
  if (city) url += `&city=${encodeURIComponent(city)}`;
  else if (lat && lon) url += `&lat=${lat}&lon=${lon}`;

  const res = await fetch(url);
  const json = await res.json();
  if (json.error || !json.data.length) { showEmpty('timeSeriesChart', json.error || 'No data'); return; }

  const dates = json.data.map(d => d.date);
  const vals = json.data.map(d => d.value);

  const trace = {
    x: dates, y: vals,
    type: 'scatter', mode: 'lines',
    name: meta.label,
    line: { color: meta.color || '#1f6feb', width: 2 },
    fill: 'tozeroy',
    fillcolor: (meta.color || '#1f6feb') + '22',
    hovertemplate: `%{x}<br>${meta.label}: %{y} ${meta.unit}<extra></extra>`,
  };

  const layout = {
    ...darkLayout,
    title: { text: `${meta.label} Over Time – ${json.location || 'Global'}`, font: { size: 14 } },
    xaxis: { ...darkLayout.xaxis, title: 'Date' },
    yaxis: { ...darkLayout.yaxis, title: `${meta.label} (${meta.unit})` },
  };

  Plotly.react('timeSeriesChart', [trace], layout, plotConfig);
}

// ── AI Insights ────────────────────────────────────────────────────────────

async function renderInsights() {
  const { variable, city } = getParams();
  const panel = document.getElementById('insightsPanel');
  panel.innerHTML = `<p class="insight-placeholder">⏳ Analyzing data...</p>`;

  let url = `${API}/get_ai_insights?variable=${variable}`;
  if (city) url += `&city=${encodeURIComponent(city)}`;

  try {
    const res = await fetch(url);
    const json = await res.json();

    if (json.error || !json.insights || !json.insights.length) {
      panel.innerHTML = `<p class="insight-placeholder">⚠️ ${json.error || 'No insights available. Try selecting a city or clicking ↺ Use Sample Data.'}</p>`;
      return;
    }

    panel.innerHTML = json.insights.map((text, i) => `
      <div class="insight-item">
        <span class="insight-num">${i + 1}</span>
        <span>${text}</span>
      </div>
    `).join('');
  } catch (e) {
    panel.innerHTML = `<p class="insight-placeholder">⚠️ Could not load insights. Is the server running?</p>`;
  }
}

// ── Comparison ─────────────────────────────────────────────────────────────

async function renderComparison() {
  const { variable, year1, year2 } = getParams();
  if (!year1 || !year2) { showEmpty('compareChart1', 'Set Year 1'); showEmpty('compareChart2', 'Set Year 2'); return; }

  const meta = VAR_META[variable] || { label: variable, unit: '' };
  const url = `${API}/get_comparison_data?variable=${variable}&year1=${year1}&year2=${year2}`;

  const res = await fetch(url);
  const json = await res.json();
  if (json.error) { showEmpty('compareChart1', json.error); showEmpty('compareChart2', json.error); return; }

  renderCompareMap('compareChart1', json.data.year1, meta, year1);
  renderCompareMap('compareChart2', json.data.year2, meta, year2);
}

function renderCompareMap(elId, data, meta, year) {
  if (!data || !data.length) { showEmpty(elId, 'No data for ' + year); return; }

  const lats = data.map(d => d.lat);
  const lons = data.map(d => d.lon);
  const vals = data.map(d => d.value);
  const texts = data.map(d => `${d.city || ''}<br>${meta.label}: ${d.value} ${meta.unit}`);

  const trace = {
    type: 'scattergeo', lat: lats, lon: lons, text: texts,
    hoverinfo: 'text', mode: 'markers',
    marker: {
      size: 14, color: vals,
      colorscale: 'RdYlBu_r',
      colorbar: { title: meta.unit, thickness: 10, len: 0.6 },
      line: { width: 0.5, color: '#30363d' },
    },
  };

  const layout = {
    ...darkLayout,
    title: { text: `${meta.label} – ${year}`, font: { size: 13 } },
    margin: { t: 40, r: 5, b: 5, l: 5 },
    geo: {
      showland: true, landcolor: '#1c2330',
      showocean: true, oceancolor: '#0d1117',
      showcoastlines: true, coastlinecolor: '#30363d',
      showframe: false, bgcolor: '#0d1117',
      projection: { type: 'natural earth' },
    },
  };

  Plotly.react(elId, [trace], layout, plotConfig);
}

// ── Future Prediction ──────────────────────────────────────────────────────

async function renderPrediction() {
  const { variable, city, lat, lon, yearsAhead } = getParams();
  const meta = VAR_META[variable] || { label: variable, unit: '' };

  let url = `${API}/get_future_prediction?variable=${variable}&years_ahead=${yearsAhead}`;
  if (city) url += `&city=${encodeURIComponent(city)}`;
  else if (lat && lon) url += `&lat=${lat}&lon=${lon}`;

  try {
    const res = await fetch(url);
    const json = await res.json();

    if (json.error || !json.historical || !json.historical.length) {
      showEmpty('predictionChart', json.error || 'No prediction data. Try clicking ↺ Use Sample Data.');
      return;
    }

    const histTrace = {
      x: json.historical.map(d => d.year),
      y: json.historical.map(d => d.value),
      type: 'scatter', mode: 'lines+markers',
      name: 'Historical',
      line: { color: meta.color || '#1f6feb', width: 2 },
      marker: { size: 5 },
      hovertemplate: `%{x}<br>${meta.label}: %{y} ${meta.unit}<extra>Historical</extra>`,
    };

    const predTrace = {
      x: json.predicted.map(d => d.year),
      y: json.predicted.map(d => d.value),
      type: 'scatter', mode: 'lines+markers',
      name: 'Predicted',
      line: { color: '#a371f7', width: 2, dash: 'dot' },
      marker: { size: 6, symbol: 'diamond' },
      hovertemplate: `%{x}<br>Predicted ${meta.label}: %{y} ${meta.unit}<extra>Prediction</extra>`,
    };

    const allVals = json.historical.map(d => d.value);
    const std = stdDev(allVals);
    const bandTrace = {
      x: [...json.predicted.map(d => d.year), ...json.predicted.map(d => d.year).reverse()],
      y: [...json.predicted.map(d => d.value + std), ...json.predicted.map(d => d.value - std).reverse()],
      fill: 'toself', fillcolor: '#a371f722',
      line: { color: 'transparent' },
      type: 'scatter', mode: 'none',
      name: '±1σ Band', showlegend: true,
      hoverinfo: 'skip',
    };

    const layout = {
      ...darkLayout,
      title: { text: `${meta.label} Prediction – Next ${yearsAhead} Years${city ? ' (' + city + ')' : ''}`, font: { size: 14 } },
      xaxis: { ...darkLayout.xaxis, title: 'Year' },
      yaxis: { ...darkLayout.yaxis, title: `${meta.label} (${meta.unit})` },
      legend: { bgcolor: '#161b22', bordercolor: '#30363d', borderwidth: 1 },
      shapes: [{
        type: 'line',
        x0: json.historical[json.historical.length - 1].year,
        x1: json.historical[json.historical.length - 1].year,
        y0: 0, y1: 1, yref: 'paper',
        line: { color: '#484f58', width: 1, dash: 'dash' },
      }],
    };

    Plotly.react('predictionChart', [bandTrace, histTrace, predTrace], layout, plotConfig);

    const infoEl = document.getElementById('predictionInfo');
    if (json.trend_description) {
      infoEl.textContent = `🔮 ${json.trend_description}`;
      infoEl.classList.add('visible');
    }
  } catch (e) {
    showEmpty('predictionChart', 'Could not load prediction. Is the server running?');
  }
}

// ── Helpers ────────────────────────────────────────────────────────────────

function showEmpty(elId, msg) {
  const el = document.getElementById(elId);
  el.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;height:200px;color:#484f58;font-size:13px;">${msg || 'No data available'}</div>`;
}

function showLoading(show) {
  document.getElementById('loadingOverlay').classList.toggle('hidden', !show);
}

function stdDev(arr) {
  const mean = arr.reduce((a, b) => a + b, 0) / arr.length;
  return Math.sqrt(arr.reduce((s, v) => s + (v - mean) ** 2, 0) / arr.length);
}
