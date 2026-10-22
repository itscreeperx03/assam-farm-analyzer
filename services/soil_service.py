"""
Soil Data Service for Assam Farm Analyzer.
Retrieves ISRIC SoilGrids data, incorporates local Soil Health Card inputs,
and calculates lime requirements for acidic Assam soils.
"""
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
import requests

from assam_data import AGRO_CLIMATIC_ZONES

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

def classify_texture(clay: Optional[float], sand: Optional[float]) -> str:
    """Classify soil texture based on USDA soil triangle approximations."""
    if clay is None or sand is None:
        return "Medium Loam (Estimated)"
    silt = max(0.0, 100.0 - (clay + sand))
    if clay >= 40:
        return "Heavy Clay"
    elif clay >= 35 and sand <= 45:
        return "Silty Clay"
    elif clay >= 27 and 20 <= sand <= 45:
        return "Clay Loam"
    elif clay >= 20 and sand >= 45:
        return "Sandy Clay Loam"
    elif 7 <= clay < 27 and sand <= 52 and silt >= 28:
        return "Loam"
    elif silt >= 50:
        return "Silt Loam"
    elif sand >= 70:
        return "Sandy Loam / Sand"
    else:
        return "Sandy Loam"

def get_liming_recommendation(ph: Optional[float]) -> Dict[str, Any]:
    """Calculate agricultural lime / dolomite dosage for acidic Assam soils."""
    if ph is None:
        return {
            "status": "Unknown",
            "needs_lime": False,
            "lime_kg_per_bigha": 0,
            "lime_ton_per_ha": 0,
            "advice": "Test soil pH at your local KVK or District Agriculture Office."
        }

    if ph < 4.5:
        return {
            "status": "Extremely Acidic",
            "needs_lime": True,
            "lime_kg_per_bigha": 350,
            "lime_ton_per_ha": 2.6,
            "advice": "Soil is extremely acidic (pH < 4.5). Apply 350 kg agricultural lime or dolomite per bigha (2.6 t/ha) 2-3 weeks before sowing. Mix thoroughly into the top 15 cm soil."
        }
    elif ph < 5.0:
        return {
            "status": "Strongly Acidic",
            "needs_lime": True,
            "lime_kg_per_bigha": 250,
            "lime_ton_per_ha": 1.8,
            "advice": "Soil is strongly acidic. Apply 250 kg agricultural lime per bigha (1.8 t/ha) during land preparation. Ideal for tea; requires liming for mustard, potato, and vegetables."
        }
    elif ph < 5.5:
        return {
            "status": "Moderately Acidic",
            "needs_lime": True,
            "lime_kg_per_bigha": 150,
            "lime_ton_per_ha": 1.1,
            "advice": "Moderately acidic soil. Apply 150 kg agricultural lime per bigha (1.1 t/ha) once every 3 years. Rice grows well, but pulses and mustard benefit from liming."
        }
    elif ph < 6.5:
        return {
            "status": "Slightly Acidic (Optimal for most crops)",
            "needs_lime": False,
            "lime_kg_per_bigha": 0,
            "lime_ton_per_ha": 0,
            "advice": "Soil pH is in the optimal range (5.5 - 6.5) for paddy, mustard, and vegetables in Assam. No liming needed."
        }
    elif ph <= 7.5:
        return {
            "status": "Neutral",
            "needs_lime": False,
            "lime_kg_per_bigha": 0,
            "lime_ton_per_ha": 0,
            "advice": "Neutral soil. Favorable for most field crops and pulses. Do not apply lime."
        }
    else:
        return {
            "status": "Alkaline",
            "needs_lime": False,
            "lime_kg_per_bigha": 0,
            "lime_ton_per_ha": 0,
            "advice": "Alkaline soil. Rare in Assam; apply organic manure or gypsum if needed."
        }

def get_organic_carbon_status(soc_g_per_kg: Optional[float]) -> Dict[str, Any]:
    """Evaluate organic carbon status in soil."""
    if soc_g_per_kg is None:
        return {"status": "Unknown", "pct": None, "advice": "Soil organic carbon status unknown."}
    pct = round(soc_g_per_kg / 10.0, 2)
    if pct < 0.5:
        return {
            "status": "Low (< 0.5%)",
            "pct": pct,
            "advice": "Low organic carbon. Apply 1.5 - 2 tonnes Farm Yard Manure (FYM) or 500 kg Vermicompost per bigha before planting."
        }
    elif pct < 0.75:
        return {
            "status": "Medium (0.5% - 0.75%)",
            "pct": pct,
            "advice": "Moderate organic carbon. Maintain fertility with 1 tonne FYM per bigha and incorporate crop residues."
        }
    else:
        return {
            "status": "High (> 0.75%)",
            "pct": pct,
            "advice": "Good organic carbon content. Soil has high moisture and nutrient retention capacity."
        }

def query_soilgrids(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Query ISRIC SoilGrids REST API with caching."""
    key = f"soil_{lat:.4f}_{lon:.4f}.json"
    cache_file = CACHE_DIR / key

    if cache_file.exists() and (time.time() - cache_file.stat().st_mtime) < 90 * 86400:
        try:
            cached = json.loads(cache_file.read_text())
            if cached.get("ph") is not None:
                return cached
        except Exception:
            pass

    url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    params = [
        ("lon", lon), ("lat", lat),
        ("property", "phh2o"), ("property", "clay"),
        ("property", "sand"), ("property", "soc"),
        ("depth", "0-5cm"), ("depth", "5-15cm"), ("depth", "15-30cm"),
        ("value", "mean"),
    ]
    try:
        r = requests.get(url, params=params, timeout=12)
        if r.status_code == 200:
            data = r.json()
            layers = data.get("properties", {}).get("layers", [])
            out = {}
            for layer in layers:
                d_factor = layer.get("unit_measure", {}).get("d_factor", 1) or 1
                vals = [
                    d["values"]["mean"] / d_factor
                    for d in layer.get("depths", [])
                    if d.get("values", {}).get("mean") is not None
                ]
                if vals:
                    out[layer["name"]] = sum(vals) / len(vals)

            if "phh2o" in out and out["phh2o"] > 0:
                result = {
                    "ph": round(out["phh2o"], 2),
                    "clay_pct": round(out.get("clay", 25.0), 1),
                    "sand_pct": round(out.get("sand", 40.0), 1),
                    "organic_carbon_g_per_kg": round(out.get("soc", 10.0), 1),
                    "source": "ISRIC SoilGrids v2.0"
                }
                cache_file.write_text(json.dumps(result))
                return result
    except Exception:
        pass
    return None

def get_soil_analysis(lat: float, lon: float, zone_id: str, shc_override: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get comprehensive soil analysis.
    Prioritizes:
    1. Soil Health Card manual input (if provided)
    2. SoilGrids query (with disk cache)
    3. Assam Agro-climatic Zone scientific baseline
    """
    if shc_override and any(v is not None for v in shc_override.values()):
        ph = shc_override.get("ph")
        clay = shc_override.get("clay_pct")
        sand = shc_override.get("sand_pct")
        soc = shc_override.get("organic_carbon_g_per_kg")
        # In case user entered OC in % instead of g/kg:
        if soc is not None and soc < 5.0:
            soc = soc * 10.0  # Convert % to g/kg

        source = "Soil Health Card (Farmer / Lab Data)"
    else:
        # Check SoilGrids or regional baseline
        sg_data = query_soilgrids(lat, lon)
        if sg_data:
            ph = sg_data.get("ph")
            clay = sg_data.get("clay_pct")
            sand = sg_data.get("sand_pct")
            soc = sg_data.get("organic_carbon_g_per_kg")
            source = sg_data.get("source", "SoilGrids Global Model")
        else:
            default_soil = AGRO_CLIMATIC_ZONES.get(zone_id, {}).get("default_soil", {
                "ph": 5.4, "clay_pct": 26.0, "sand_pct": 40.0, "organic_carbon_g_per_kg": 11.0
            })
            ph = default_soil["ph"]
            clay = default_soil["clay_pct"]
            sand = default_soil["sand_pct"]
            soc = default_soil["organic_carbon_g_per_kg"]
            source = f"Assam Agro-climatic Zone Baseline ({zone_id})"

    texture = classify_texture(clay, sand)
    lime_info = get_liming_recommendation(ph)
    oc_info = get_organic_carbon_status(soc)

    return {
        "ph": ph,
        "clay_pct": clay,
        "sand_pct": sand,
        "organic_carbon_g_per_kg": soc,
        "organic_carbon_pct": round(soc / 10.0, 2) if soc else None,
        "texture": texture,
        "liming": lime_info,
        "organic_carbon": oc_info,
        "data_source": source
    }
