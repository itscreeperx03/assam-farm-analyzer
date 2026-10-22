"""
Assam Farm Analyzer - FastAPI Server.
Full-stack agricultural advisory API and web dashboard.
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from assam_data import (
    ASSAM_DISTRICTS,
    AGRO_CLIMATIC_ZONES,
    HECTARE_TO_BIGHA,
    format_land_area,
    get_district_flood_profile
)
from services.geo_service import find_nearest_district, calculate_polygon_area
from services.soil_service import get_soil_analysis
from services.weather_service import get_historical_weather, get_forecast_weather
from services.satellite_service import get_ndvi_series
from services.advisor_service import score_all_crops, generate_farm_advisories, calculate_fertilizer_for_area, load_crops_db

app = FastAPI(
    title="Assam Farm Analyzer API",
    description="Intelligent farm analysis, soil diagnostics, satellite NDVI, and AAU-aligned crop & fertilizer advisory for Assam.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HERE = Path(__file__).resolve().parent
STATIC_DIR = HERE / "static"
STATIC_DIR.mkdir(exist_ok=True)

class SoilHealthCardInput(BaseModel):
    ph: Optional[float] = None
    organic_carbon_pct: Optional[float] = None
    organic_carbon_g_per_kg: Optional[float] = None
    clay_pct: Optional[float] = None
    sand_pct: Optional[float] = None
    nitrogen_level: Optional[str] = None  # "Low", "Medium", "High"
    phosphorus_level: Optional[str] = None
    potassium_level: Optional[str] = None

class AnalysisRequest(BaseModel):
    lat: float = Field(..., description="Field centroid latitude")
    lon: float = Field(..., description="Field centroid longitude")
    geojson: Optional[Dict[str, Any]] = Field(None, description="Optional GeoJSON Polygon geometry or feature")
    soil_health_card: Optional[SoilHealthCardInput] = None
    area_bighas: Optional[float] = None
    include_satellite: bool = True

class FertilizerCalcRequest(BaseModel):
    crop_id: str
    area_bighas: float
    soil_ph: Optional[float] = None
    oc_pct: Optional[float] = None

@app.get("/api/districts")
def list_districts():
    """Return Assam districts and agro-climatic zones."""
    return {
        "districts": ASSAM_DISTRICTS,
        "zones": AGRO_CLIMATIC_ZONES
    }

@app.get("/api/crops")
def list_crops():
    """Return full catalog of crops with AAU fertilizer & agronomy packages."""
    return {"crops": load_crops_db()}

@app.post("/api/fertilizer-calculator")
def calculate_fertilizer(req: FertilizerCalcRequest):
    """Calculate commercial fertilizer requirements for a specific crop and area."""
    crops = load_crops_db()
    crop = next((c for c in crops if c.get("id") == req.crop_id), None)
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    calc = calculate_fertilizer_for_area(
        crop,
        area_bighas=req.area_bighas,
        soil_ph=req.soil_ph,
        oc_pct=req.oc_pct
    )
    return calc

@app.post("/api/analyze")
def analyze_farm(req: AnalysisRequest):
    """
    Run full end-to-end farm analysis:
    - District & Agro-climatic zone classification
    - Land area computation (Bighas & Hectares)
    - Soil analysis & liming calculation (SoilGrids / Soil Health Card / AAU baseline)
    - 1-Year historical agro-weather & 7-day live forecast
    - Sentinel-2 satellite NDVI vegetation health
    - Crop suitability ranking with AAU fertilizer prescriptions & cultivation steps
    - Priority farm advisories
    """
    lat, lon = req.lat, req.lon

    # 1. Location & Agro-climatic zone
    geo_info = find_nearest_district(lat, lon)
    zone_id = geo_info["zone_id"]

    # 2. Polygon area calculation
    area_info = {"bighas": 1.0, "hectares": 0.134, "sq_meters": 1337.8, "acres": 0.33}
    geom_to_use = None
    if req.geojson:
        g = req.geojson.get("geometry") if req.geojson.get("type") == "Feature" else req.geojson
        if g:
            geom_to_use = g
            area_info = calculate_polygon_area(g)

    # Use explicit bighas if user provided
    if req.area_bighas and req.area_bighas > 0:
        area_info["bighas"] = req.area_bighas

    # Format full Assam land measurement (Bigha, Katha, Lessa)
    land_details = format_land_area(area_info["bighas"])
    area_info.update(land_details)

    # 3. Soil Analysis
    shc_dict = req.soil_health_card.dict() if req.soil_health_card else None
    soil_analysis = get_soil_analysis(lat, lon, zone_id, shc_override=shc_dict)

    # 4. Weather Analysis
    weather_hist = get_historical_weather(lat, lon)
    weather_forecast = get_forecast_weather(lat, lon)

    # 5. Satellite NDVI
    ndvi_series = []
    if req.include_satellite and geom_to_use:
        ndvi_series = get_ndvi_series(geom_to_use)
    elif req.include_satellite:
        # Create a small virtual 1-hectare box around centroid
        d = 0.001
        box = {
            "type": "Polygon",
            "coordinates": [[[lon - d, lat - d], [lon + d, lat - d], [lon + d, lat + d], [lon - d, lat + d], [lon - d, lat - d]]]
        }
        ndvi_series = get_ndvi_series(box)

    # 6. Crop Suitability Scoring, Economics & Fertilizer Recommendations
    crop_rankings = score_all_crops(
        soil_analysis,
        weather_hist,
        zone_id,
        area_bighas=area_info["bighas"]
    )

    # 7. Flood and Contingency Profile
    flood_profile = get_district_flood_profile(geo_info["district"], zone_id)

    # 8. Overall Farm Advisories
    advisories = generate_farm_advisories(
        soil_analysis,
        weather_hist,
        ndvi_series,
        geo_info["zone_details"],
        district_name=geo_info["district"]
    )

    return {
        "location": {
            "lat": round(lat, 5),
            "lon": round(lon, 5),
            "district": geo_info["district"],
            "zone_id": geo_info["zone_id"],
            "zone_name": geo_info["zone_name"],
            "zone_name_as": geo_info["zone_name_as"],
            "zone_name_hi": geo_info["zone_name_hi"],
            "zone_features": geo_info["zone_details"].get("key_features"),
            "distance_to_district_km": geo_info["distance_km"],
            "flood_profile": flood_profile
        },
        "area": area_info,
        "soil": soil_analysis,
        "weather": {
            "historical": weather_hist,
            "forecast": weather_forecast
        },
        "satellite_ndvi": {
            "series": ndvi_series,
            "latest": ndvi_series[-1] if ndvi_series else None
        },
        "crop_rankings": crop_rankings,
        "farm_advisories": advisories
    }

@app.get("/api/crop-ipm/{crop_id}")
def get_crop_ipm(crop_id: str):
    """Retrieve Integrated Pest & Disease Management guidance for a specific crop."""
    crops = load_crops_db()
    crop = next((c for c in crops if c.get("id") == crop_id), None)
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return {
        "crop_id": crop_id,
        "crop_name_en": crop.get("name_en"),
        "crop_name_as": crop.get("name_as"),
        "ipm": crop.get("ipm_aau", {}),
        "varieties": crop.get("recommended_varieties", []),
        "steps": crop.get("necessary_steps", {})
    }

@app.post("/api/export-advisory-card", response_class=HTMLResponse)
def export_advisory_card(req: AnalysisRequest):
    """
    Generate an official, printable bilingual Farmer Advisory Card HTML sheet.
    Formatted for standard A4 printing and mobile offline PDF storage.
    """
    analysis = analyze_farm(req)
    loc = analysis["location"]
    area = analysis["area"]
    soil = analysis["soil"]
    weather = analysis["weather"]
    top_crops = analysis["crop_rankings"][:5]
    advisories = analysis["farm_advisories"]

    crop_rows_html = ""
    for c in top_crops:
        fert = c.get("fertilizer", {}).get("total_for_field", {})
        econ = c.get("economics", {})
        crop_rows_html += f"""
        <tr>
          <td><strong>{c['name_en']}</strong><br><small style="color:#15803d;">{c['name_as']}</small></td>
          <td><span style="display:inline-block; padding:2px 8px; border-radius:12px; font-weight:700; background:{c['badge_color']}; color:white;">{c['score']}%</span></td>
          <td>{c['season_en']}</td>
          <td>Urea: {fert.get('urea_kg', 0)} kg ({fert.get('urea_bags_50kg', 0)} bags)<br>SSP: {fert.get('ssp_kg', 0)} kg | MOP: {fert.get('mop_kg', 0)} kg</td>
          <td>Exp. Yield: {econ.get('total_expected_yield', '-')} {econ.get('yield_unit', '')}<br>Est. Net: ₹{econ.get('total_net_profit_inr', 0):,}</td>
        </tr>
        """

    adv_html = "".join([f"<li><strong>{a['title']}:</strong> {a['text']}</li>" for a in advisories])

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Assam Farmer Advisory Card - {loc['district']}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; margin: 20px; color: #1e293b; }}
    .header {{ border-bottom: 3px solid #16a34a; padding-bottom: 12px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }}
    .brand {{ font-size: 20px; font-weight: 800; color: #15803d; }}
    .subbrand {{ font-size: 13px; color: #64748b; }}
    .meta-box {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 15px; }}
    .meta-item .lbl {{ font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 600; }}
    .meta-item .val {{ font-size: 14px; font-weight: 700; color: #0f172a; margin-top: 2px; }}
    table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 13px; }}
    th, td {{ border: 1px solid #cbd5e1; padding: 8px 10px; text-align: left; }}
    th {{ background: #f1f5f9; font-weight: 700; }}
    .advisories-box {{ background: #fefce8; border: 1px solid #fef08a; border-radius: 8px; padding: 12px; margin-top: 15px; }}
    .advisories-box h4 {{ margin: 0 0 8px 0; color: #854d0e; font-size: 14px; }}
    .advisories-box ul {{ margin: 0; padding-left: 20px; font-size: 12px; line-height: 1.5; }}
    .footer {{ margin-top: 25px; padding-top: 10px; border-top: 1px solid #e2e8f0; font-size: 11px; color: #94a3b8; display: flex; justify-content: space-between; }}
    @media print {{
      .no-print {{ display: none; }}
      body {{ margin: 0; padding: 10px; }}
    }}
  </style>
</head>
<body>
  <div class="no-print" style="margin-bottom: 15px;">
    <button onclick="window.print()" style="background:#16a34a; color:white; border:none; padding:8px 16px; border-radius:6px; font-weight:bold; cursor:pointer;">🖨️ Print or Save as PDF</button>
  </div>
  <div class="header">
    <div>
      <div class="brand">🌾 ASSAM FARM ADVISORY CARD (কৃষি পৰামৰ্শ পত্ৰ)</div>
      <div class="subbrand">Assam Agricultural University (AAU) Package of Practices Aligned System</div>
    </div>
    <div style="text-align: right; font-size: 12px;">
      <div><strong>Zone:</strong> {loc['zone_name']}</div>
      <div><strong>District:</strong> {loc['district']}</div>
    </div>
  </div>

  <div class="meta-box">
    <div class="meta-item">
      <div class="lbl">Field Land Area</div>
      <div class="val">{area['formatted_local']} ({area['hectares']} Ha)</div>
    </div>
    <div class="meta-item">
      <div class="lbl">Soil pH & Texture</div>
      <div class="val">{soil.get('ph', '-')} pH ({soil.get('texture_class', '-')})</div>
    </div>
    <div class="meta-item">
      <div class="lbl">Soil Organic Carbon</div>
      <div class="val">{soil.get('organic_carbon_g_per_kg', '-')} g/kg ({soil.get('organic_carbon_rating', '-')})</div>
    </div>
    <div class="meta-item">
      <div class="lbl">Annual Rain & Forecast</div>
      <div class="val">{weather['historical'].get('annual_rain_mm', '-')} mm / 7-Day Temp: {weather['forecast'].get('daily', [{}])[0].get('temp_max_c', '-') }°C</div>
    </div>
  </div>

  <h3 style="margin: 15px 0 6px 0; font-size: 15px; color: #166534;">Top Suitable Crops & Field Requirements ({area['bighas']} Bighas)</h3>
  <table>
    <thead>
      <tr>
        <th>Crop Name</th>
        <th>Suitability</th>
        <th>Optimal Season</th>
        <th>AAU Fertilizer Total for Field</th>
        <th>Economics & Yield</th>
      </tr>
    </thead>
    <tbody>
      {crop_rows_html}
    </tbody>
  </table>

  <div class="advisories-box">
    <h4>📋 Priority Agronomic & Flood Advisories</h4>
    <ul>
      {adv_html}
    </ul>
  </div>

  <div class="footer">
    <div>Generated by Assam Farm Analyzer | 100% Open Agricultural Intelligence</div>
    <div>Assam Agricultural University & Directorate of Agriculture, Govt. of Assam</div>
  </div>
</body>
</html>
"""
    return HTMLResponse(content=html_content)

# Mount static folder for web app UI
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
