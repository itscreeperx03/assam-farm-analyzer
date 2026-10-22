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
from pydantic import BaseModel, Field

from assam_data import ASSAM_DISTRICTS, AGRO_CLIMATIC_ZONES, HECTARE_TO_BIGHA
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
        area_info["hectares"] = round(req.area_bighas / HECTARE_TO_BIGHA, 3)

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

    # 6. Crop Suitability Scoring & Fertilizer Recommendations
    crop_rankings = score_all_crops(
        soil_analysis,
        weather_hist,
        zone_id,
        area_bighas=area_info["bighas"]
    )

    # 7. Overall Farm Advisories
    advisories = generate_farm_advisories(
        soil_analysis,
        weather_hist,
        ndvi_series,
        geo_info["zone_details"]
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
            "distance_to_district_km": geo_info["distance_km"]
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

# Mount static folder for web app UI
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
