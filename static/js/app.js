/**
 * Assam Farm Analyzer - Frontend Application Logic
 */

let currentLang = "en";
let map = null;
let currentMarker = null;
let drawnItems = null;
let drawControl = null;
let ndviChartInstance = null;
let lastAnalysisData = null;
let districtsData = [];

// Sample Field Coordinates in Assam (Kamrup)
const SAMPLE_POLYGON = [
  [26.155, 91.738],
  [26.155, 91.745],
  [26.148, 91.745],
  [26.148, 91.738],
  [26.155, 91.738]
];

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  initI18n();
  initMap();
  loadDistricts();
  bindEvents();
  // Auto-run initial analysis for default field
  runAnalysis();
});

function initI18n() {
  const langSelect = document.getElementById("langSelect");
  langSelect.addEventListener("change", (e) => {
    currentLang = e.target.value;
    updateLanguage(currentLang);
    if (lastAnalysisData) {
      renderDashboard(lastAnalysisData);
    }
  });
}

function updateLanguage(lang) {
  const dict = I18N[lang] || I18N.en;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) {
      el.textContent = dict[key];
    }
  });
}

function initMap() {
  // Center on Assam
  const defaultLat = 26.1512;
  const defaultLon = 91.7412;

  // Base layers
  const osmLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors"
  });

  const satelliteLayer = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    {
      maxZoom: 18,
      attribution: "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
    }
  );

  map = L.map("map", {
    center: [defaultLat, defaultLon],
    zoom: 12,
    layers: [satelliteLayer, osmLayer]
  });

  const baseMaps = {
    "Satellite Imagery": satelliteLayer,
    "Street Map": osmLayer
  };
  L.control.layers(baseMaps).addTo(map);

  // Drawing layer
  drawnItems = new L.FeatureGroup();
  map.addLayer(drawnItems);

  drawControl = new L.Control.Draw({
    draw: {
      polygon: {
        allowIntersection: false,
        showArea: true,
        shapeOptions: { color: "#16a34a", weight: 3 }
      },
      rectangle: {
        shapeOptions: { color: "#16a34a", weight: 3 }
      },
      marker: false,
      polyline: false,
      circle: false,
      circlemarker: false
    },
    edit: {
      featureGroup: drawnItems
    }
  });
  map.addControl(drawControl);

  // Add default farm marker
  currentMarker = L.marker([defaultLat, defaultLon], { draggable: true }).addTo(map);

  currentMarker.on("dragend", (e) => {
    const pos = e.target.getLatLng();
    setCoordinates(pos.lat, pos.lng);
  });

  map.on("click", (e) => {
    setCoordinates(e.latlng.lat, e.latlng.lng);
    currentMarker.setLatLng(e.latlng);
  });

  map.on(L.Draw.Event.CREATED, (event) => {
    drawnItems.clearLayers();
    const layer = event.layer;
    drawnItems.addLayer(layer);

    // Calculate centroid & area
    const geojson = layer.toGeoJSON();
    const poly = geojson.geometry;
    let sumLat = 0, sumLon = 0, totalPts = 0;
    if (poly.coordinates && poly.coordinates[0]) {
      poly.coordinates[0].forEach((pt) => {
        sumLon += pt[0];
        sumLat += pt[1];
        totalPts++;
      });
      const cLat = sumLat / totalPts;
      const cLon = sumLon / totalPts;
      setCoordinates(cLat, cLon);
      currentMarker.setLatLng([cLat, cLon]);

      // Calculate area roughly using Leaflet Geodesic Area if available
      try {
        const areaSqM = L.GeometryUtil ? L.GeometryUtil.geodesicArea(layer.getLatLngs()[0]) : 1337.8 * 3;
        const bighas = (areaSqM / 1337.8038).toFixed(2);
        document.getElementById("inputBighas").value = Math.max(0.1, bighas);
        updateAreaConversionText(bighas);
      } catch (err) {
        // fallback
      }
    }
  });
}

function setCoordinates(lat, lon) {
  document.getElementById("inputLat").value = parseFloat(lat).toFixed(4);
  document.getElementById("inputLon").value = parseFloat(lon).toFixed(4);
}

function updateAreaConversionText(bighas) {
  const ha = (bighas / 7.471).toFixed(3);
  const katha = Math.round(bighas * 5);
  document.getElementById("areaConversionText").textContent = `≈ ${ha} Hectares | ${katha} Katha`;
}

async function loadDistricts() {
  try {
    const res = await fetch("/api/districts");
    const data = await res.json();
    districtsData = data.districts || [];

    const select = document.getElementById("districtSelect");
    districtsData.forEach((d) => {
      const opt = document.createElement("option");
      opt.value = `${d.lat},${d.lon}`;
      opt.textContent = `${d.name} (${d.zone})`;
      select.appendChild(opt);
    });
  } catch (err) {
    console.warn("Could not load districts list", err);
  }
}

function bindEvents() {
  // District dropdown change
  document.getElementById("districtSelect").addEventListener("change", (e) => {
    if (!e.target.value) return;
    const [lat, lon] = e.target.value.split(",").map(Number);
    setCoordinates(lat, lon);
    currentMarker.setLatLng([lat, lon]);
    map.flyTo([lat, lon], 12);
  });

  // Bighas change
  document.getElementById("inputBighas").addEventListener("input", (e) => {
    updateAreaConversionText(parseFloat(e.target.value) || 1);
  });

  // Load Sample Field
  document.getElementById("btnLoadSample").addEventListener("click", () => {
    drawnItems.clearLayers();
    const polygonLayer = L.polygon(SAMPLE_POLYGON, { color: "#16a34a", weight: 3 });
    drawnItems.addLayer(polygonLayer);
    map.fitBounds(polygonLayer.getBounds());
    setCoordinates(26.1512, 91.7412);
    currentMarker.setLatLng([26.1512, 91.7412]);
    document.getElementById("inputBighas").value = 3.5;
    updateAreaConversionText(3.5);
  });

  // Reset Map Pin
  document.getElementById("btnResetMap").addEventListener("click", () => {
    drawnItems.clearLayers();
    setCoordinates(26.1512, 91.7412);
    currentMarker.setLatLng([26.1512, 91.7412]);
    map.setView([26.1512, 91.7412], 12);
  });

  // GeoJSON file upload
  const fileInput = document.getElementById("fileGeoJson");
  if (fileInput) {
    fileInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (evt) => {
        try {
          const gj = JSON.parse(evt.target.result);
          drawnItems.clearLayers();
          const geoJsonLayer = L.geoJSON(gj, {
            style: { color: "#16a34a", weight: 3, fillOpacity: 0.2 }
          });
          drawnItems.addLayer(geoJsonLayer);
          map.fitBounds(geoJsonLayer.getBounds());

          const center = geoJsonLayer.getBounds().getCenter();
          setCoordinates(center.lat, center.lng);
          currentMarker.setLatLng(center);

          runAnalysis();
        } catch (err) {
          alert("Invalid GeoJSON file: " + err.message);
        }
      };
      reader.readAsText(file);
    });
  }

  // Export Advisory Card Button
  const btnExport = document.getElementById("btnExportCard");
  if (btnExport) {
    btnExport.addEventListener("click", () => {
      exportAdvisoryCard();
    });
  }

  // SHC Accordion Toggle
  const shcToggle = document.getElementById("shcToggle");
  const shcBody = document.getElementById("shcBody");
  const shcIcon = document.getElementById("shcIcon");
  shcToggle.addEventListener("click", () => {
    shcBody.classList.toggle("open");
    shcIcon.textContent = shcBody.classList.contains("open") ? "▲" : "▼";
  });

  // Analyze Button
  document.getElementById("btnAnalyze").addEventListener("click", runAnalysis);

  // Tabs Switching
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
      btn.classList.add("active");
      const targetTab = btn.getAttribute("data-tab");
      document.getElementById(targetTab).classList.add("active");
    });
  });

  // Crop Filters
  document.querySelectorAll(".filter-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const cat = btn.getAttribute("data-filter");
      filterCropCards(cat);
    });
  });

  // Modal Close
  document.getElementById("modalClose").addEventListener("click", () => {
    document.getElementById("cropModal").classList.remove("open");
  });

  // Recalculate Fertilizer when select or area changes in Tab 2
  document.getElementById("fertCropSelect").addEventListener("change", updateFertilizerDisplay);
  document.getElementById("fertAreaBighas").addEventListener("input", updateFertilizerDisplay);

  // Change crop in Tab 3 Roadmap
  document.getElementById("roadmapCropSelect").addEventListener("change", (e) => {
    renderCultivationTimeline(e.target.value);
  });
}

async function runAnalysis() {
  const btn = document.getElementById("btnAnalyze");
  const spinner = document.getElementById("btnSpinner");
  const btnText = document.getElementById("btnAnalyzeText");
  const dict = I18N[currentLang] || I18N.en;

  spinner.style.display = "inline";
  btnText.textContent = dict.analyzing;
  btn.disabled = true;

  const lat = parseFloat(document.getElementById("inputLat").value) || 26.1512;
  const lon = parseFloat(document.getElementById("inputLon").value) || 91.7412;
  const bighas = parseFloat(document.getElementById("inputBighas").value) || 3.0;

  // Build GeoJSON if polygon is drawn
  let geojson = null;
  const layers = drawnItems.getLayers();
  if (layers.length > 0) {
    geojson = layers[0].toGeoJSON();
  }

  // Check Soil Health Card values
  const phVal = parseFloat(document.getElementById("shcPh").value);
  const ocVal = parseFloat(document.getElementById("shcOc").value);
  const clayVal = parseFloat(document.getElementById("shcClay").value);
  const sandVal = parseFloat(document.getElementById("shcSand").value);

  const shcData = {};
  if (!isNaN(phVal)) shcData.ph = phVal;
  if (!isNaN(ocVal)) shcData.organic_carbon_pct = ocVal;
  if (!isNaN(clayVal)) shcData.clay_pct = clayVal;
  if (!isNaN(sandVal)) shcData.sand_pct = sandVal;

  const payload = {
    lat: lat,
    lon: lon,
    geojson: geojson,
    area_bighas: bighas,
    soil_health_card: Object.keys(shcData).length > 0 ? shcData : null,
    include_satellite: true
  };

  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error("Server analysis failed");
    const data = await res.json();
    lastAnalysisData = data;
    renderDashboard(data);
  } catch (err) {
    alert("Error running farm analysis: " + err.message);
  } finally {
    spinner.style.display = "none";
    btnText.textContent = dict.btn_analyze;
    btn.disabled = false;
  }
}

function renderDashboard(data) {
  const dict = I18N[currentLang] || I18N.en;

  // 1. Top Banner
  const loc = data.location;
  const floodText = loc.flood_profile ? ` (${loc.flood_profile.risk_level} Flood Risk)` : "";
  document.getElementById("bannerDistrict").textContent = `${loc.district} District${floodText}`;
  
  let zoneName = loc.zone_name;
  if (currentLang === "as" && loc.zone_name_as) zoneName = loc.zone_name_as;
  else if (currentLang === "hi" && loc.zone_name_hi) zoneName = loc.zone_name_hi;

  document.getElementById("bannerZone").textContent = `${zoneName} (${loc.zone_id})`;
  document.getElementById("bannerCoords").textContent = `${loc.lat}° N, ${loc.lon}° E`;
  document.getElementById("statBighas").textContent = data.area.formatted_local || `${data.area.bighas} Bighas`;
  document.getElementById("statHectares").textContent = data.area.hectares;

  // 2. Soil KPI
  const soil = data.soil;
  document.getElementById("kpiPh").textContent = soil.ph !== null ? `${soil.ph} pH` : "5.4 pH (Est)";
  const lime = soil.liming || {};
  document.getElementById("kpiPhBadge").textContent = lime.status || "Moderately Acidic";
  document.getElementById("kpiPhBadge").className = `kpi-badge ${lime.needs_lime ? "badge-yellow" : "badge-green"}`;
  document.getElementById("kpiSoilTexture").textContent = `${dict.texture}: ${soil.texture} | OC: ${soil.organic_carbon_pct || 1.0}%`;

  // 3. Rain KPI
  const weatherHist = data.weather.historical;
  document.getElementById("kpiRain").textContent = `${weatherHist.annual_rain_mm.toLocaleString()} mm`;
  document.getElementById("kpiRainBadge").textContent = `Monsoon: ${weatherHist.monsoon_rain_mm.toLocaleString()} mm`;
  document.getElementById("kpiRainSub").textContent = `Winter (Rabi): ${weatherHist.rabi_rain_mm} mm | Pre-Monsoon: ${weatherHist.pre_monsoon_rain_mm} mm`;

  // 4. Temp KPI
  document.getElementById("kpiTemp").textContent = `${weatherHist.mean_temp_c} °C`;
  document.getElementById("kpiTempBadge").textContent = "Subtropical Humid";
  document.getElementById("kpiTempSub").textContent = `Summer Max: ${weatherHist.summer_max_c}°C | Winter Min: ${weatherHist.winter_min_c}°C`;

  // 5. NDVI Satellite KPI
  const sat = data.satellite_ndvi;
  const latestNdvi = sat.latest;
  if (latestNdvi) {
    document.getElementById("kpiNdvi").textContent = latestNdvi.ndvi;
    const interp = latestNdvi.interpretation || {};
    document.getElementById("kpiNdviBadge").textContent = interp.status || "Vegetative Canopy";
    document.getElementById("kpiNdviDate").textContent = `Observed: ${latestNdvi.date}`;
  }

  // 6. Advisories Box
  const advBox = document.getElementById("advisoriesBox");
  advBox.innerHTML = "";
  (data.farm_advisories || []).forEach((adv) => {
    const div = document.createElement("div");
    div.className = `adv-alert ${adv.type}`;
    div.innerHTML = `<strong>${adv.title}</strong>${adv.text}`;
    advBox.appendChild(div);
  });

  // 7. Render Crops Grid
  renderCropsGrid(data.crop_rankings || []);

  // 7.5 Render Economics & Profitability Tab
  renderEconomicsTab(data.crop_rankings || [], data.area);

  // 8. Populate Fertilizer Dropdown and Display
  populateFertilizerDropdown(data.crop_rankings || []);

  // 9. Populate Roadmap Dropdown
  populateRoadmapDropdown(data.crop_rankings || []);

  // 10. Render NDVI Chart
  renderNdviChart(sat.series || []);

  // 11. Render 7-day Forecast
  renderWeatherForecast(data.weather.forecast.forecast_days || []);
}

function renderCropsGrid(crops) {
  const container = document.getElementById("cropsGrid");
  container.innerHTML = "";
  const dict = I18N[currentLang] || I18N.en;

  crops.forEach((crop) => {
    const card = document.createElement("div");
    card.className = "crop-card";
    card.setAttribute("data-category", crop.category);

    let cropName = crop.name_en;
    let cropSeason = crop.season_en;
    let verdict = crop.verdict;

    if (currentLang === "as" && crop.name_as) cropName = crop.name_as;
    else if (currentLang === "hi" && crop.name_hi) cropName = crop.name_hi;

    if (currentLang === "as" && crop.season_as) cropSeason = crop.season_as;
    else if (currentLang === "hi" && crop.season_hi) cropSeason = crop.season_hi;

    if (currentLang === "as" && crop.verdict_as) verdict = crop.verdict_as;
    else if (currentLang === "hi" && crop.verdict_hi) verdict = crop.verdict_hi;

    const floodBadge = crop.flood_tolerance === "high" 
      ? '<span class="tag" style="background:#dbeafe; color:#1e40af;">🌊 Flood Tolerant</span>'
      : (crop.flood_tolerance === "none" ? '<span class="tag" style="background:#fee2e2; color:#991b1b;">⚠️ No Waterlogging</span>' : '');

    card.innerHTML = `
      <div>
        <div class="crop-card-head">
          <div>
            <div class="crop-name">${cropName}</div>
            <div class="crop-name-sub">${crop.category}</div>
          </div>
          <div class="suitability-score" style="background: ${crop.badge_color};">
            ${crop.score}%
          </div>
        </div>

        <div class="crop-tags">
          <span class="tag" style="background:#f1f5f9; color:#0f172a;">${verdict}</span>
          ${floodBadge}
        </div>

        <div class="crop-details">
          <div><strong>📅 Season:</strong> ${cropSeason}</div>
          ${crop.recommended_varieties && crop.recommended_varieties.length > 0 
            ? `<div><strong>🌾 Recommended Varieties (AAU):</strong> ${crop.recommended_varieties.slice(0, 3).join(", ")}</div>` 
            : ''}
          ${crop.issues && crop.issues.length > 0 
            ? `<div style="color:#b45309;">⚠️ ${crop.issues[0]}</div>` 
            : '<div style="color:#15803d;">✅ Soil & weather in optimal range</div>'}
          ${crop.economics && crop.economics.total_net_profit_inr ? `
            <div style="margin-top:0.35rem; padding-top:0.35rem; border-top:1px dashed #cbd5e1; font-size:0.8rem; display:flex; justify-content:space-between; align-items:center;">
              <span><strong>💰 Est. Net Profit:</strong> <strong style="color:#15803d;">₹${crop.economics.total_net_profit_inr.toLocaleString()}</strong></span>
              <span style="color:#64748b; font-size:0.75rem;">B:C: ${crop.economics.bc_ratio}</span>
            </div>
          ` : ''}
        </div>
      </div>

      <button class="btn-card-action" onclick="openCropModal('${crop.id}')">
        ${dict.btn_view_steps} ➔
      </button>
    `;
    container.appendChild(card);
  });
}

function filterCropCards(category) {
  const cards = document.querySelectorAll(".crop-card");
  cards.forEach((card) => {
    if (category === "all" || card.getAttribute("data-category") === category) {
      card.style.display = "flex";
    } else {
      card.style.display = "none";
    }
  });
}

function populateFertilizerDropdown(crops) {
  const sel = document.getElementById("fertCropSelect");
  sel.innerHTML = "";
  crops.forEach((c) => {
    const opt = document.createElement("option");
    opt.value = c.id;
    let name = c.name_en;
    if (currentLang === "as" && c.name_as) name = c.name_as;
    else if (currentLang === "hi" && c.name_hi) name = c.name_hi;
    opt.textContent = `${name} (${c.score}%)`;
    sel.appendChild(opt);
  });

  if (crops.length > 0) {
    sel.value = crops[0].id;
    document.getElementById("fertAreaBighas").value = document.getElementById("inputBighas").value;
    updateFertilizerDisplay();
  }
}

function updateFertilizerDisplay() {
  if (!lastAnalysisData) return;
  const cropId = document.getElementById("fertCropSelect").value;
  const bighas = parseFloat(document.getElementById("fertAreaBighas").value) || 1.0;
  const crop = (lastAnalysisData.crop_rankings || []).find((c) => c.id === cropId);
  if (!crop) return;

  const fert = crop.fertilizer || {};
  const perBigha = fert.per_bigha || {};

  const totalUrea = (perBigha.urea_kg * bighas).toFixed(1);
  const totalSsp = (perBigha.ssp_kg * bighas).toFixed(1);
  const totalMop = (perBigha.mop_kg * bighas).toFixed(1);
  const totalFym = (perBigha.fym_ton * bighas).toFixed(2);

  const ureaBags = Math.ceil(totalUrea / 50);
  const sspBags = Math.ceil(totalSsp / 50);
  const mopBags = Math.ceil(totalMop / 50);

  document.getElementById("calcUreaKg").textContent = `${totalUrea} kg`;
  document.getElementById("calcUreaBags").textContent = `${ureaBags} bags (50kg)`;

  document.getElementById("calcSspKg").textContent = `${totalSsp} kg`;
  document.getElementById("calcSspBags").textContent = `${sspBags} bags (50kg)`;

  document.getElementById("calcMopKg").textContent = `${totalMop} kg`;
  document.getElementById("calcMopBags").textContent = `${mopBags} bags (50kg)`;

  document.getElementById("calcFymTon").textContent = `${totalFym} tonnes`;

  const ph = lastAnalysisData.soil.ph;
  const limeBox = document.getElementById("calcLimeBox");
  if (ph && ph < 5.5 && cropId !== "assam_tea") {
    limeBox.style.display = "block";
    const limeKg = Math.round((ph < 4.8 ? 250 : 150) * bighas);
    document.getElementById("calcLimeKg").textContent = `${limeKg} kg`;
  } else {
    limeBox.style.display = "none";
  }

  document.getElementById("fertSplitText").textContent = fert.application_schedule || "Apply basal and 2 top dressings.";
  document.getElementById("fertBioText").textContent = fert.biofertilizers || "Azospirillum/PSB inoculation.";
}

function populateRoadmapDropdown(crops) {
  const sel = document.getElementById("roadmapCropSelect");
  sel.innerHTML = "";
  crops.forEach((c) => {
    const opt = document.createElement("option");
    opt.value = c.id;
    let name = c.name_en;
    if (currentLang === "as" && c.name_as) name = c.name_as;
    else if (currentLang === "hi" && c.name_hi) name = c.name_hi;
    opt.textContent = name;
    sel.appendChild(opt);
  });

  if (crops.length > 0) {
    sel.value = crops[0].id;
    renderCultivationTimeline(crops[0].id);
  }
}

function renderCultivationTimeline(cropId) {
  if (!lastAnalysisData) return;
  const crop = (lastAnalysisData.crop_rankings || []).find((c) => c.id === cropId);
  if (!crop) return;

  let cropName = crop.name_en;
  if (currentLang === "as" && crop.name_as) cropName = crop.name_as;
  else if (currentLang === "hi" && crop.name_hi) cropName = crop.name_hi;

  document.getElementById("roadmapCropTitle").textContent = cropName;

  const steps = crop.necessary_steps || {};
  const container = document.getElementById("cultivationTimeline");
  const dict = I18N[currentLang] || I18N.en;

  container.innerHTML = `
    <div class="timeline-step">
      <div class="step-header">🚜 ${dict.step_land}</div>
      <div class="step-desc">${steps.land_prep || "Plough 3-4 times to bring soil to fine tilth."}</div>
    </div>
    <div class="timeline-step">
      <div class="step-header">🌱 ${dict.step_seed}</div>
      <div class="step-desc">
        ${steps.seed_and_sowing || "Treat seeds with biofertilizer or certified fungicide."}
        <br><strong>Varieties for Assam:</strong> ${(crop.recommended_varieties || []).join("; ")}
      </div>
    </div>
    <div class="timeline-step">
      <div class="step-header">💧 ${dict.step_water}</div>
      <div class="step-desc">${steps.water_management || "Ensure drainage to prevent waterlogging during monsoon."}</div>
    </div>
    <div class="timeline-step">
      <div class="step-header">⚖️ ${dict.step_nutrient}</div>
      <div class="step-desc">${crop.fertilizer ? crop.fertilizer.application_schedule : "Apply balanced NPK according to AAU schedule."}</div>
    </div>
    <div class="timeline-step">
      <div class="step-header">🛡️ ${dict.step_pest}</div>
      <div class="step-desc">${steps.pest_disease || "Scout regularly for common regional insect pests and blight."}</div>
    </div>
    <div class="timeline-step">
      <div class="step-header">🌾 ${dict.step_harvest}</div>
      <div class="step-desc">${steps.harvest || "Harvest at optimal physiological maturity and cure/dry properly."}</div>
    </div>
  `;
}

function renderNdviChart(series) {
  const ctx = document.getElementById("ndviChart").getContext("2d");
  if (ndviChartInstance) {
    ndviChartInstance.destroy();
  }

  const labels = series.map((s) => s.date);
  const values = series.map((s) => s.ndvi);

  ndviChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Sentinel-2 NDVI",
          data: values,
          borderColor: "#16a34a",
          backgroundColor: "rgba(22, 163, 74, 0.15)",
          pointBackgroundColor: "#15803d",
          pointRadius: 5,
          tension: 0.3,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          min: 0,
          max: 1.0,
          title: { display: true, text: "NDVI Index" }
        },
        x: {
          title: { display: true, text: "Date of Sentinel-2 Overpass" }
        }
      }
    }
  });
}

function renderWeatherForecast(days) {
  const container = document.getElementById("forecastContainer");
  container.innerHTML = "";
  if (!days || days.length === 0) {
    container.innerHTML = "<p style='color:#64748b; font-size:0.85rem;'>Forecast data not available.</p>";
    return;
  }

  days.forEach((d) => {
    const isRainy = (d.rain_prob_pct > 50) || (d.rain_mm > 5.0);
    const row = document.createElement("div");
    row.style.cssText = "display:flex; justify-content:space-between; align-items:center; padding:0.5rem 0.75rem; background:#f8fafc; border-radius:6px; font-size:0.85rem; border:1px solid #e2e8f0;";
    row.innerHTML = `
      <div style="font-weight:600; min-width:85px;">${d.date}</div>
      <div>🌡️ ${d.temp_min}°C - ${d.temp_max}°C</div>
      <div>🌧️ ${d.rain_mm} mm (${d.rain_prob_pct}%)</div>
      <div style="font-size:0.75rem; color:${isRainy ? '#b45309' : '#15803d'}; font-weight:600;">
        ${d.spraying_advisory}
      </div>
    `;
    container.appendChild(row);
  });
}

function openCropModal(cropId) {
  if (!lastAnalysisData) return;
  const crop = (lastAnalysisData.crop_rankings || []).find((c) => c.id === cropId);
  if (!crop) return;

  let cropName = crop.name_en;
  let cropSeason = crop.season_en;
  if (currentLang === "as" && crop.name_as) cropName = crop.name_as;
  else if (currentLang === "hi" && crop.name_hi) cropName = crop.name_hi;

  if (currentLang === "as" && crop.season_as) cropSeason = crop.season_as;
  else if (currentLang === "hi" && crop.season_hi) cropSeason = crop.season_hi;

  const steps = crop.necessary_steps || {};
  const fert = crop.fertilizer || {};
  const perBigha = fert.per_bigha || {};

  const content = document.getElementById("modalContent");
  content.innerHTML = `
    <h2 style="font-size:1.4rem; font-weight:800; color:#1e293b; margin-bottom:0.25rem;">
      🌾 ${cropName}
    </h2>
    <div style="color:#64748b; font-size:0.875rem; margin-bottom:1rem;">
      ${crop.category} | ${cropSeason} | Suitability: <strong style="color:${crop.badge_color}">${crop.score}%</strong>
    </div>

    <!-- Recommended Varieties -->
    <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; padding:0.85rem; margin-bottom:1rem;">
      <strong style="color:#166534; display:block; margin-bottom:0.35rem;">🏆 Recommended Varieties (Assam Agricultural University):</strong>
      <div style="font-size:0.875rem; color:#14532d;">
        ${(crop.recommended_varieties || []).join("<br>")}
      </div>
    </div>

    <!-- Fertilizer Dosage -->
    <h3 style="font-size:1.1rem; font-weight:700; margin:1rem 0 0.5rem 0;">⚖️ AAU Recommended Fertilizer Dose (Per Bigha):</h3>
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:0.5rem; margin-bottom:1rem;">
      <div style="background:#f8fafc; padding:0.65rem; border-radius:6px; text-align:center; border:1px solid #e2e8f0;">
        <div style="font-size:0.75rem; color:#64748b;">Urea (46% N)</div>
        <div style="font-size:1.1rem; font-weight:700; color:#15803d;">${perBigha.urea_kg || 15} kg</div>
      </div>
      <div style="background:#f8fafc; padding:0.65rem; border-radius:6px; text-align:center; border:1px solid #e2e8f0;">
        <div style="font-size:0.75rem; color:#64748b;">SSP (16% P2O5)</div>
        <div style="font-size:1.1rem; font-weight:700; color:#15803d;">${perBigha.ssp_kg || 25} kg</div>
      </div>
      <div style="background:#f8fafc; padding:0.65rem; border-radius:6px; text-align:center; border:1px solid #e2e8f0;">
        <div style="font-size:0.75rem; color:#64748b;">MOP (60% K2O)</div>
        <div style="font-size:1.1rem; font-weight:700; color:#15803d;">${perBigha.mop_kg || 10} kg</div>
      </div>
      <div style="background:#f8fafc; padding:0.65rem; border-radius:6px; text-align:center; border:1px solid #e2e8f0;">
        <div style="font-size:0.75rem; color:#64748b;">Organic FYM</div>
        <div style="font-size:1.1rem; font-weight:700; color:#15803d;">${perBigha.fym_ton || 1.0} tonnes</div>
      </div>
    </div>
    <p style="font-size:0.85rem; color:#475569; margin-bottom:1rem;">
      <strong>Application Timing:</strong> ${fert.application_schedule || ""}
    </p>

    <!-- Economics Summary for Field -->
    ${crop.economics ? `
      <h3 style="font-size:1.1rem; font-weight:700; margin:1rem 0 0.5rem 0;">💰 AAU Production Economics (${crop.economics.total_expected_yield} ${crop.economics.yield_unit}):</h3>
      <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:0.5rem; margin-bottom:1rem;">
        <div style="background:#f0fdf4; padding:0.65rem; border-radius:6px; text-align:center; border:1px solid #bbf7d0;">
          <div style="font-size:0.75rem; color:#15803d;">Est. Net Profit</div>
          <div style="font-size:1.1rem; font-weight:800; color:#166534;">₹${(crop.economics.total_net_profit_inr || 0).toLocaleString()}</div>
        </div>
        <div style="background:#fef2f2; padding:0.65rem; border-radius:6px; text-align:center; border:1px solid #fecaca;">
          <div style="font-size:0.75rem; color:#b91c1c;">Est. Cultivation Cost</div>
          <div style="font-size:1.1rem; font-weight:700; color:#991b1b;">₹${(crop.economics.total_cost_inr || 0).toLocaleString()}</div>
        </div>
        <div style="background:#f8fafc; padding:0.65rem; border-radius:6px; text-align:center; border:1px solid #e2e8f0;">
          <div style="font-size:0.75rem; color:#64748b;">Market / MSP Price</div>
          <div style="font-size:1.0rem; font-weight:700; color:#0f172a;">${crop.economics.price_unit}</div>
        </div>
        <div style="background:#f8fafc; padding:0.65rem; border-radius:6px; text-align:center; border:1px solid #e2e8f0;">
          <div style="font-size:0.75rem; color:#64748b;">Benefit-Cost (B:C)</div>
          <div style="font-size:1.1rem; font-weight:700; color:#0284c7;">${crop.economics.bc_ratio || "-"}</div>
        </div>
      </div>
    ` : ''}

    <!-- IPM Integrated Pest & Disease Management -->
    ${crop.ipm && ((crop.ipm.major_pests && crop.ipm.major_pests.length > 0) || (crop.ipm.major_diseases && crop.ipm.major_diseases.length > 0)) ? `
      <h3 style="font-size:1.1rem; font-weight:700; margin:1rem 0 0.5rem 0;">🛡️ AAU Integrated Pest & Disease Protection:</h3>
      <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:0.85rem; margin-bottom:1rem; font-size:0.85rem;">
        ${(crop.ipm.major_pests || []).map(p => `
          <div style="margin-bottom:0.6rem; padding-bottom:0.6rem; border-bottom:1px dashed #fcd34d;">
            <strong style="color:#b45309;">🐛 ${p.name}</strong>
            <div style="color:#475569; margin:2px 0;"><strong>Symptoms:</strong> ${p.symptoms}</div>
            ${p.biological ? `<div style="color:#15803d;"><strong>Biological:</strong> ${p.biological}</div>` : ''}
            ${p.chemical ? `<div style="color:#b91c1c;"><strong>Chemical:</strong> ${p.chemical}</div>` : ''}
          </div>
        `).join("")}
        ${(crop.ipm.major_diseases || []).map(d => `
          <div style="margin-bottom:0.4rem;">
            <strong style="color:#9f1239;">🍄 ${d.name}</strong>
            <div style="color:#475569; margin:2px 0;"><strong>Symptoms:</strong> ${d.symptoms}</div>
            <div style="color:#15803d;"><strong>AAU Remedy:</strong> ${d.management}</div>
          </div>
        `).join("")}
      </div>
    ` : ''}

    <!-- Step by Step Agronomy -->
    <h3 style="font-size:1.1rem; font-weight:700; margin:1rem 0 0.5rem 0;">📋 Necessary Cultivation Steps:</h3>
    <div style="display:flex; flex-direction:column; gap:0.65rem; font-size:0.875rem;">
      <div style="background:#f8fafc; padding:0.65rem 0.85rem; border-radius:6px; border-left:4px solid #16a34a;">
        <strong>1. Land Preparation:</strong> ${steps.land_prep || ""}
      </div>
      <div style="background:#f8fafc; padding:0.65rem 0.85rem; border-radius:6px; border-left:4px solid #16a34a;">
        <strong>2. Seed Treatment & Sowing:</strong> ${steps.seed_and_sowing || ""}
      </div>
      <div style="background:#f8fafc; padding:0.65rem 0.85rem; border-radius:6px; border-left:4px solid #16a34a;">
        <strong>3. Water & Drainage:</strong> ${steps.water_management || ""}
      </div>
      <div style="background:#f8fafc; padding:0.65rem 0.85rem; border-radius:6px; border-left:4px solid #16a34a;">
        <strong>4. Pest & Disease Management:</strong> ${steps.pest_disease || ""}
      </div>
      <div style="background:#f8fafc; padding:0.65rem 0.85rem; border-radius:6px; border-left:4px solid #16a34a;">
        <strong>5. Harvesting & Storage:</strong> ${steps.harvest || ""}
      </div>
    </div>
  `;

  document.getElementById("cropModal").classList.add("open");
}

function renderEconomicsTab(crops, area) {
  const tbody = document.getElementById("econTableBody");
  if (!tbody) return;
  tbody.innerHTML = "";

  const sorted = [...crops].sort((a, b) => {
    const netA = (a.economics && a.economics.total_net_profit_inr) || 0;
    const netB = (b.economics && b.economics.total_net_profit_inr) || 0;
    return netB - netA;
  });

  if (sorted.length > 0) {
    const top = sorted[0];
    let topName = top.name_en;
    if (currentLang === "as" && top.name_as) topName = top.name_as;
    const topProfit = (top.economics && top.economics.total_net_profit_inr) || 0;
    const badge = document.getElementById("econTopProfitableBadge");
    if (badge) {
      badge.textContent = `⭐ Highest Profit: ${topName} (₹${topProfit.toLocaleString()})`;
    }
  }

  sorted.forEach((c) => {
    const econ = c.economics || {};
    let cropName = c.name_en;
    if (currentLang === "as" && c.name_as) cropName = c.name_as;
    else if (currentLang === "hi" && c.name_hi) cropName = c.name_hi;

    const tr = document.createElement("tr");
    tr.style.borderBottom = "1px solid #e2e8f0";
    tr.innerHTML = `
      <td style="padding:10px 12px; font-weight:600;">
        ${cropName}
        <div style="font-size:0.75rem; color:#64748b; font-weight:normal;">${c.category}</div>
      </td>
      <td style="padding:10px 12px;">
        <span style="display:inline-block; padding:2px 8px; border-radius:12px; font-weight:700; font-size:0.8rem; background:${c.badge_color}; color:white;">
          ${c.score}%
        </span>
      </td>
      <td style="padding:10px 12px; font-weight:600; color:#0f172a;">
        ${(econ.total_expected_yield || 0).toLocaleString()} <span style="font-size:0.75rem; color:#64748b; font-weight:normal;">${econ.yield_unit || ""}</span>
      </td>
      <td style="padding:10px 12px; color:#475569;">
        ${econ.price_unit || `₹${econ.price_per_unit_inr}`}
      </td>
      <td style="padding:10px 12px; color:#dc2626; font-weight:600;">
        ₹${(econ.total_cost_inr || 0).toLocaleString()}
      </td>
      <td style="padding:10px 12px; color:#16a34a; font-weight:800; font-size:0.95rem;">
        ₹${(econ.total_net_profit_inr || 0).toLocaleString()}
      </td>
      <td style="padding:10px 12px; font-weight:700; color:#0284c7;">
        ${econ.bc_ratio || "-"}
      </td>
    `;
    tbody.appendChild(tr);
  });
}

async function exportAdvisoryCard() {
  if (!lastAnalysisData) return;
  const lat = parseFloat(document.getElementById("inputLat").value);
  const lon = parseFloat(document.getElementById("inputLon").value);
  const bighas = parseFloat(document.getElementById("inputBighas").value) || 3.0;

  let geojson = null;
  const layers = drawnItems.getLayers();
  if (layers.length > 0) {
    geojson = layers[0].toGeoJSON();
  }

  const payload = {
    lat: lat,
    lon: lon,
    geojson: geojson,
    area_bighas: bighas,
    include_satellite: false
  };

  try {
    const res = await fetch("/api/export-advisory-card", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error("Could not generate advisory card");
    const htmlText = await res.text();
    const printWin = window.open("", "_blank");
    printWin.document.open();
    printWin.document.write(htmlText);
    printWin.document.close();
  } catch (err) {
    alert("Error generating card: " + err.message);
  }
}
