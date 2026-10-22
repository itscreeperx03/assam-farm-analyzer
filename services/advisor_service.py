"""
Advisor and Crop Scoring Service for Assam.
Implements multi-factor crop suitability scoring, AAU fertilizer recommendations,
and step-by-step agronomy guidance.
"""
import json
import math
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from assam_data import HECTARE_TO_BIGHA, get_district_flood_profile

HERE = Path(__file__).resolve().parent.parent
CROPS_DB_PATH = HERE / "crops_assam_db.json"

def load_crops_db() -> List[Dict[str, Any]]:
    """Load crops from knowledge base."""
    if CROPS_DB_PATH.exists():
        try:
            return json.loads(CROPS_DB_PATH.read_text(encoding="utf-8")).get("crops", [])
        except Exception:
            pass
    # Fallback to crops_assam.json if db missing
    legacy_path = HERE / "crops_assam.json"
    if legacy_path.exists():
        return json.loads(legacy_path.read_text(encoding="utf-8")).get("crops", [])
    return []

def range_score(value: Optional[float], lo: float, hi: float) -> Optional[float]:
    """1.0 inside [lo, hi]; falls linearly towards 0 outside the optimal range."""
    if value is None:
        return None
    if lo <= value <= hi:
        return 1.0
    width = max(hi - lo, 1e-9)
    dist = (lo - value) if value < lo else (value - hi)
    return max(0.0, 1.0 - dist / width)

def calculate_fertilizer_for_area(
    crop_data: Dict[str, Any],
    area_bighas: float,
    soil_ph: Optional[float] = None,
    oc_pct: Optional[float] = None
) -> Dict[str, Any]:
    """
    Calculate commercial fertilizer quantities (Urea, SSP, MOP, FYM, Lime)
    for a specific crop and farm area in Bighas.
    """
    aau = crop_data.get("fertilizer_aau", {})
    urea_bigha = aau.get("urea_kg_bigha", 15.0)
    ssp_bigha = aau.get("ssp_kg_bigha", 25.0)
    mop_bigha = aau.get("mop_kg_bigha", 10.0)
    fym_bigha = aau.get("fym_ton_bigha", 1.0)

    # Adjust if soil health card indicates low or high organic carbon
    if oc_pct is not None:
        if oc_pct < 0.5:
            fym_bigha *= 1.4  # boost organic manure
        elif oc_pct > 0.8:
            urea_bigha *= 0.9  # slight reduction in chemical N

    total_urea_kg = round(urea_bigha * area_bighas, 1)
    total_ssp_kg = round(ssp_bigha * area_bighas, 1)
    total_mop_kg = round(mop_bigha * area_bighas, 1)
    total_fym_ton = round(fym_bigha * area_bighas, 2)

    # Calculate 50kg bags needed
    urea_bags = math.ceil(total_urea_kg / 50.0) if total_urea_kg > 0 else 0
    ssp_bags = math.ceil(total_ssp_kg / 50.0) if total_ssp_kg > 0 else 0
    mop_bags = math.ceil(total_mop_kg / 50.0) if total_mop_kg > 0 else 0

    # Lime required if soil is acidic and crop is sensitive (ph < 5.8)
    lime_kg_total = 0
    if soil_ph is not None and soil_ph < 5.5 and crop_data.get("id") != "assam_tea":
        # Tea loves acidic soil, but others need lime
        if soil_ph < 4.8:
            lime_kg_total = round(250 * area_bighas, 0)
        else:
            lime_kg_total = round(150 * area_bighas, 0)

    return {
        "crop_id": crop_data.get("id"),
        "crop_name": crop_data.get("name_en"),
        "crop_name_as": crop_data.get("name_as"),
        "crop_name_hi": crop_data.get("name_hi"),
        "area_bighas": round(area_bighas, 2),
        "area_hectares": round(area_bighas / HECTARE_TO_BIGHA, 3),
        "per_bigha": {
            "urea_kg": round(urea_bigha, 1),
            "ssp_kg": round(ssp_bigha, 1),
            "mop_kg": round(mop_bigha, 1),
            "fym_ton": round(fym_bigha, 2)
        },
        "total_for_field": {
            "urea_kg": total_urea_kg,
            "urea_bags_50kg": urea_bags,
            "ssp_kg": total_ssp_kg,
            "ssp_bags_50kg": ssp_bags,
            "mop_kg": total_mop_kg,
            "mop_bags_50kg": mop_bags,
            "fym_ton": total_fym_ton,
            "agri_lime_kg": lime_kg_total
        },
        "application_schedule": aau.get("split_schedule", "Apply basal dose at planting, top dress remaining nitrogen in 2 equal splits."),
        "biofertilizers": aau.get("biofertilizers", "Azotobacter/Azospirillum and PSB seed/soil treatment.")
    }

def score_all_crops(
    soil_data: Dict[str, Any],
    weather_data: Dict[str, Any],
    zone_id: str,
    area_bighas: float = 1.0
) -> List[Dict[str, Any]]:
    """Score all crops in database and generate tailored recommendations."""
    crops = load_crops_db()
    ph = soil_data.get("ph")
    clay = soil_data.get("clay_pct")
    rain = weather_data.get("annual_rain_mm")
    temp = weather_data.get("mean_temp_c")

    results = []

    for crop in crops:
        scores = []
        issues = []
        strengths = []

        # 1. Soil pH
        if ph is not None and "ph" in crop:
            lo, hi = crop["ph"]
            s = range_score(ph, lo, hi)
            if s is not None:
                scores.append(s)
                if s < 0.95:
                    direction = "too acidic" if ph < lo else "too alkaline"
                    issues.append(f"Soil pH {ph} is {direction} (ideal {lo}-{hi})")
                else:
                    strengths.append(f"Soil pH {ph} is optimal ({lo}-{hi})")

        # 2. Soil Clay / Texture
        if clay is not None and "clay_pct" in crop:
            lo, hi = crop["clay_pct"]
            s = range_score(clay, lo, hi)
            if s is not None:
                scores.append(s)
                if s < 0.95:
                    direction = "too light/sandy" if clay < lo else "too heavy/clayey"
                    issues.append(f"Clay content {clay}% is {direction} (ideal {lo}-{hi}%)")
                else:
                    strengths.append(f"Soil texture (clay {clay}%) matches root requirements")

        # 3. Rainfall
        if rain is not None and "rain_mm" in crop:
            lo, hi = crop["rain_mm"]
            s = range_score(rain, lo, hi)
            if s is not None:
                scores.append(s)
                if s < 0.95:
                    direction = "lower than needed" if rain < lo else "higher than needed"
                    issues.append(f"Annual rainfall {rain:.0f} mm is {direction} (ideal {lo}-{hi} mm)")
                else:
                    strengths.append(f"Annual rainfall {rain:.0f} mm is well-suited")

        # 4. Temperature
        if temp is not None and "temp_c" in crop:
            lo, hi = crop["temp_c"]
            s = range_score(temp, lo, hi)
            if s is not None:
                scores.append(s)
                if s < 0.95:
                    direction = "too cool" if temp < lo else "too warm"
                    issues.append(f"Mean temp {temp}°C is {direction} (ideal {lo}-{hi}°C)")

        if not scores:
            final_score = 70
        else:
            # Blend average and minimum (weakest link principle)
            total = 0.55 * (sum(scores) / len(scores)) + 0.45 * min(scores)
            final_score = int(round(total * 100))

        # Verdict
        if final_score >= 80:
            verdict = "Highly Recommended"
            verdict_as = "অতি উৎকৃষ্ট"
            verdict_hi = "अत्यधिक उपयुक्त"
            badge_color = "#22c55e"
        elif final_score >= 60:
            verdict = "Suitable with Care"
            verdict_as = "যত্নসহকাৰে উপযোগী"
            verdict_hi = "देखभाल के साथ उपयुक्त"
            badge_color = "#eab308"
        else:
            verdict = "Challenging / Low Suitability"
            verdict_as = "সীমিত উপযোগী"
            verdict_hi = "कम उपयुक्त"
            badge_color = "#ef4444"

        # Calculate crop-specific fertilizer for the field
        fert_calc = calculate_fertilizer_for_area(
            crop,
            area_bighas,
            soil_ph=ph,
            oc_pct=soil_data.get("organic_carbon_pct")
        )

        # AAU Economics tailored to field size
        econ_raw = crop.get("economics_aau", {})
        yield_bigha = econ_raw.get("yield_bigha_avg", 0.0)
        cost_bigha = econ_raw.get("cost_cultivation_bigha_inr", 0)
        gross_bigha = econ_raw.get("gross_revenue_bigha_inr", 0)
        net_bigha = econ_raw.get("net_profit_bigha_inr", 0)

        economics = {
            "yield_bigha_avg": yield_bigha,
            "yield_unit": econ_raw.get("yield_unit", "Quintals"),
            "yield_range": econ_raw.get("yield_range", []),
            "total_expected_yield": round(yield_bigha * area_bighas, 1),
            "price_per_unit_inr": econ_raw.get("price_per_unit_inr", 0),
            "price_unit": econ_raw.get("price_unit", "₹/Unit"),
            "cost_cultivation_bigha_inr": cost_bigha,
            "total_cost_inr": int(round(cost_bigha * area_bighas)),
            "gross_revenue_bigha_inr": gross_bigha,
            "total_gross_revenue_inr": int(round(gross_bigha * area_bighas)),
            "net_profit_bigha_inr": net_bigha,
            "total_net_profit_inr": int(round(net_bigha * area_bighas)),
            "bc_ratio": econ_raw.get("bc_ratio", 2.0)
        }

        results.append({
            "id": crop.get("id"),
            "name_en": crop.get("name_en", crop.get("name")),
            "name_as": crop.get("name_as", crop.get("name")),
            "name_hi": crop.get("name_hi", crop.get("name")),
            "category": crop.get("category", "General"),
            "score": final_score,
            "verdict": verdict,
            "verdict_as": verdict_as,
            "verdict_hi": verdict_hi,
            "badge_color": badge_color,
            "season_en": crop.get("season_en", crop.get("season")),
            "season_as": crop.get("season_as", ""),
            "season_hi": crop.get("season_hi", ""),
            "flood_tolerance": crop.get("flood_tolerance", "medium"),
            "recommended_varieties": crop.get("recommended_varieties", []),
            "strengths": strengths,
            "issues": issues,
            "fertilizer": fert_calc,
            "economics": economics,
            "ipm": crop.get("ipm_aau", {}),
            "necessary_steps": crop.get("necessary_steps", {})
        })

    # Sort descending by score
    return sorted(results, key=lambda x: x["score"], reverse=True)

def generate_farm_advisories(
    soil_data: Dict[str, Any],
    weather_data: Dict[str, Any],
    ndvi_series: List[Dict[str, Any]],
    zone_info: Dict[str, Any],
    district_name: Optional[str] = None
) -> List[Dict[str, str]]:
    """Generate high-priority agro-advisories for the farm."""
    advisories = []

    # 1. Flood and drainage contingency
    zone_id = zone_info.get("id", "LBVZ")
    if district_name:
        flood_profile = get_district_flood_profile(district_name, zone_id)
        risk_lvl = flood_profile.get("risk_level", "Moderate")
        is_high = "High" in risk_lvl or "Very High" in risk_lvl
        advisories.append({
            "type": "warning" if is_high else "info",
            "title": f"Flood & Drainage Profile: {risk_lvl} Risk ({flood_profile.get('risk_level_as', '')})",
            "text": f"{flood_profile.get('action_guidance', '')} Recommended flood-tolerant / contingency varieties: {', '.join(flood_profile.get('contingency_varieties', []))}."
        })

    # 2. Soil acidity advice
    ph = soil_data.get("ph")
    if ph is not None:
        if ph < 5.0:
            advisories.append({
                "type": "warning",
                "title": "Strong Soil Acidity Alert (অম্লীয় মাটি)",
                "text": f"Your soil pH is {ph} (strongly acidic). Applying 200-300 kg agricultural lime or dolomite per bigha every 3 years will drastically enhance fertilizer efficiency and increase yields for mustard, potato, and vegetables."
            })
        elif ph < 5.8:
            advisories.append({
                "type": "info",
                "title": "Moderate Soil Acidity",
                "text": f"Soil pH is {ph}. Very suitable for Assam Sali Rice and Tea. For pulses or winter oilseeds, light liming (100-150 kg/bigha) is advantageous."
            })

    # 3. Organic carbon
    oc = soil_data.get("organic_carbon_g_per_kg")
    if oc is not None and oc < 7.0:
        advisories.append({
            "type": "warning",
            "title": "Low Soil Organic Matter",
            "text": "Organic carbon is on the lower side. Incorporate 1.5 tonnes Farm Yard Manure (FYM) or 500 kg vermicompost per bigha to increase moisture holding capacity."
        })

    # 4. Seasonal Assam Farming Calendar
    now_month = datetime.datetime.now().month
    if now_month in [10, 11]:
        advisories.append({
            "type": "info",
            "title": "Rabi Sowing & Sali Harvest Window (আহিন-কাতি-আঘোণ)",
            "text": "Peak sowing window for Toria/Mustard (TS-36, TS-38), Potato, Rabi Pulses, and Winter Cole crops. Drain standing water from Sali rice fields 7-10 days before harvesting."
        })
    elif now_month in [12, 1]:
        advisories.append({
            "type": "info",
            "title": "Boro Rice Nursery & Rabi Care (পুহ-মাঘ)",
            "text": "Raise protected Boro paddy nurseries against cold fog. Scout mustard for early aphid colonies and apply yellow sticky traps."
        })
    elif now_month in [2, 3]:
        advisories.append({
            "type": "info",
            "title": "Pre-Kharif Preparation & Ahu Rice (ফাগুন-চ’ত)",
            "text": "Transplant Boro rice; prepare land for direct seeded Ahu rice and summer vegetables on char lands."
        })
    elif now_month in [6, 7]:
        advisories.append({
            "type": "info",
            "title": "Main Sali Rice Transplanting (আহাৰ-শাওণ)",
            "text": "Transplant 25-30 day Sali seedlings. For flood-prone lowlands, ensure submergence-tolerant varieties (Ranjit Sub-1, Bahadur Sub-1)."
        })

    # 5. NDVI interpretation
    if ndvi_series:
        latest = ndvi_series[-1]
        val = latest.get("ndvi", 0.0)
        dt = latest.get("date", "")
        if val < 0.25:
            advisories.append({
                "type": "info",
                "title": f"Current Field Cover (NDVI: {val} on {dt})",
                "text": "Satellite reflection indicates fallow land, recent tillage, or post-harvest stubble. This is the ideal window for deep ploughing and basal soil incorporation."
            })
        elif val > 0.55:
            advisories.append({
                "type": "success",
                "title": f"Vigorous Vegetative Canopy (NDVI: {val} on {dt})",
                "text": "Satellite confirms dense, flourishing green canopy. Maintain vigilant scouting for insect pests (stem borer, hispa) and disease symptoms."
            })

    return advisories
