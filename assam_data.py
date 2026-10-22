"""
Assam Agro-climatic Zones, Districts, Flood Risk & Land Conversion Data.
Aligned with Assam Agricultural University (AAU) and Directorate of Agriculture, Assam.
"""
from typing import Dict, Any, List

# Assam's 6 Agro-climatic Zones
AGRO_CLIMATIC_ZONES = {
    "UBVZ": {
        "id": "UBVZ",
        "name": "Upper Brahmaputra Valley Zone",
        "name_as": "উচ্চ ব্ৰহ্মপুত্ৰ উপত্যকা অঞ্চল",
        "name_hi": "ऊपरी ब्रह्मपुत्र घाटी क्षेत्र",
        "districts": ["Dibrugarh", "Tinsukia", "Sivasagar", "Charaideo", "Jorhat", "Majuli", "Golaghat"],
        "annual_rainfall_range_mm": [2000, 3200],
        "soil_character": "Acidic alluvium, sandy loam to clay loam, rich in organic matter in tea belts",
        "default_soil": {"ph": 5.1, "clay_pct": 28.0, "sand_pct": 38.0, "organic_carbon_g_per_kg": 13.5},
        "key_features": "Major tea growing belt, Sali rice, mustard, potato, citrus, arecanut."
    },
    "CBVZ": {
        "id": "CBVZ",
        "name": "Central Brahmaputra Valley Zone",
        "name_as": "মধ্য ব্ৰহ্মপুত্ৰ উপত্যকা অঞ্চল",
        "name_hi": "मध्य ब्रह्मपुत्र घाटी क्षेत्र",
        "districts": ["Nagaon", "Morigaon", "Hojai"],
        "annual_rainfall_range_mm": [1400, 2000],
        "soil_character": "Slightly acidic to neutral alluvial soils, fertile loams",
        "default_soil": {"ph": 5.8, "clay_pct": 24.0, "sand_pct": 42.0, "organic_carbon_g_per_kg": 10.0},
        "key_features": "Assam's granary; intensive rice, jute, mustard, pulses, winter vegetables."
    },
    "LBVZ": {
        "id": "LBVZ",
        "name": "Lower Brahmaputra Valley Zone",
        "name_as": "নামনি ব্ৰহ্মপুত্ৰ উপত্যকা অঞ্চল",
        "name_hi": "निचला ब्रह्मपुत्र घाटी क्षेत्र",
        "districts": [
            "Kamrup Metropolitan", "Kamrup", "Nalbari", "Barpeta", "Bajali",
            "Bongaigaon", "Dhubri", "South Salmara-Mankachar", "Goalpara", "Chirang", "Kokrajhar"
        ],
        "annual_rainfall_range_mm": [1600, 2800],
        "soil_character": "Active river alluvium, char lands, moderately acidic to neutral silt loam",
        "default_soil": {"ph": 5.6, "clay_pct": 22.0, "sand_pct": 45.0, "organic_carbon_g_per_kg": 9.2},
        "key_features": "Extensive rice (Ahu, Sali, Boro), jute, mustard, winter vegetables, banana."
    },
    "NBPZ": {
        "id": "NBPZ",
        "name": "North Bank Plain Zone",
        "name_as": "উত্তৰ পাৰ সমভূমি অঞ্চল",
        "name_hi": "उत्तरी तट मैदानी क्षेत्र",
        "districts": ["Dhemaji", "Lakhimpur", "Sonitpur", "Biswanath", "Darrang", "Udalguri", "Baksa", "Tamulpur"],
        "annual_rainfall_range_mm": [1800, 3000],
        "soil_character": "Recent riverine alluvium, sandy loam to silt loam, flood prone",
        "default_soil": {"ph": 5.3, "clay_pct": 20.0, "sand_pct": 50.0, "organic_carbon_g_per_kg": 8.5},
        "key_features": "Deepwater/flood-tolerant rice, tea estates on highlands, ginger, turmeric, mustard."
    },
    "BVZ": {
        "id": "BVZ",
        "name": "Barak Valley Zone",
        "name_as": "বৰাক উপত্যকা অঞ্চল",
        "name_hi": "बराक घाटी क्षेत्र",
        "districts": ["Cachar", "Karimganj", "Hailakandi"],
        "annual_rainfall_range_mm": [2200, 3600],
        "soil_character": "Old alluvial and hill soils, heavy clays in valleys (beels), acidic",
        "default_soil": {"ph": 4.9, "clay_pct": 34.0, "sand_pct": 28.0, "organic_carbon_g_per_kg": 11.0},
        "key_features": "Tea, lowland rice, pineapple, arecanut, rubber, wetland fisheries."
    },
    "HZ": {
        "id": "HZ",
        "name": "Hill Zone",
        "name_as": "পাৰ্বত্য অঞ্চল",
        "name_hi": "पहाड़ी क्षेत्र",
        "districts": ["Karbi Anglong", "West Karbi Anglong", "Dima Hasao"],
        "annual_rainfall_range_mm": [1200, 1800],
        "soil_character": "Red lateritic and loamy soils on slopes, strongly acidic, prone to erosion",
        "default_soil": {"ph": 4.7, "clay_pct": 25.0, "sand_pct": 40.0, "organic_carbon_g_per_kg": 14.0},
        "key_features": "Ginger (Karbi Organic Ginger - GI), turmeric, hill paddy, maize, citrus, black pepper."
    }
}

# Major Agricultural Districts with Coordinates & Flood Vulnerability
ASSAM_DISTRICTS = [
    # UBVZ
    {"name": "Jorhat", "lat": 26.7509, "lon": 94.2037, "zone": "UBVZ", "flood_risk": "Moderate"},
    {"name": "Golaghat", "lat": 26.5167, "lon": 93.9667, "zone": "UBVZ", "flood_risk": "Moderate"},
    {"name": "Dibrugarh", "lat": 27.4728, "lon": 94.9120, "zone": "UBVZ", "flood_risk": "Moderate"},
    {"name": "Tinsukia", "lat": 27.4922, "lon": 95.3537, "zone": "UBVZ", "flood_risk": "Moderate"},
    {"name": "Sivasagar", "lat": 26.9826, "lon": 94.6425, "zone": "UBVZ", "flood_risk": "Moderate"},
    {"name": "Charaideo", "lat": 27.0250, "lon": 94.9500, "zone": "UBVZ", "flood_risk": "Low"},
    {"name": "Majuli", "lat": 26.9600, "lon": 94.2200, "zone": "UBVZ", "flood_risk": "Very High"},
    # CBVZ
    {"name": "Nagaon", "lat": 26.3452, "lon": 92.6840, "zone": "CBVZ", "flood_risk": "Moderate"},
    {"name": "Morigaon", "lat": 26.2500, "lon": 92.3300, "zone": "CBVZ", "flood_risk": "Very High"},
    {"name": "Hojai", "lat": 26.0000, "lon": 92.8600, "zone": "CBVZ", "flood_risk": "Moderate"},
    # LBVZ
    {"name": "Kamrup (Guwahati)", "lat": 26.1512, "lon": 91.7412, "zone": "LBVZ", "flood_risk": "Moderate"},
    {"name": "Kamrup Metropolitan", "lat": 26.1800, "lon": 91.7500, "zone": "LBVZ", "flood_risk": "Moderate"},
    {"name": "Nalbari", "lat": 26.4400, "lon": 91.4300, "zone": "LBVZ", "flood_risk": "High"},
    {"name": "Barpeta", "lat": 26.3200, "lon": 91.0000, "zone": "LBVZ", "flood_risk": "Very High"},
    {"name": "Bajali", "lat": 26.4900, "lon": 91.1700, "zone": "LBVZ", "flood_risk": "High"},
    {"name": "Bongaigaon", "lat": 26.5000, "lon": 90.5500, "zone": "LBVZ", "flood_risk": "High"},
    {"name": "Dhubri", "lat": 26.0200, "lon": 89.9700, "zone": "LBVZ", "flood_risk": "Very High"},
    {"name": "South Salmara-Mankachar", "lat": 25.8500, "lon": 89.9200, "zone": "LBVZ", "flood_risk": "Very High"},
    {"name": "Goalpara", "lat": 26.1800, "lon": 90.6200, "zone": "LBVZ", "flood_risk": "High"},
    {"name": "Kokrajhar", "lat": 26.4000, "lon": 90.2700, "zone": "LBVZ", "flood_risk": "Moderate"},
    {"name": "Chirang", "lat": 26.5500, "lon": 90.5000, "zone": "LBVZ", "flood_risk": "Moderate"},
    # NBPZ
    {"name": "Sonitpur (Tezpur)", "lat": 26.6338, "lon": 92.8006, "zone": "NBPZ", "flood_risk": "Moderate"},
    {"name": "Biswanath", "lat": 26.7300, "lon": 93.1500, "zone": "NBPZ", "flood_risk": "High"},
    {"name": "Lakhimpur", "lat": 27.2300, "lon": 94.1000, "zone": "NBPZ", "flood_risk": "Very High"},
    {"name": "Dhemaji", "lat": 27.4800, "lon": 94.5800, "zone": "NBPZ", "flood_risk": "Very High"},
    {"name": "Darrang (Mangaldai)", "lat": 26.4300, "lon": 92.0300, "zone": "NBPZ", "flood_risk": "High"},
    {"name": "Udalguri", "lat": 26.7400, "lon": 92.1000, "zone": "NBPZ", "flood_risk": "Moderate"},
    {"name": "Baksa", "lat": 26.6800, "lon": 91.3500, "zone": "NBPZ", "flood_risk": "Moderate"},
    {"name": "Tamulpur", "lat": 26.6300, "lon": 91.5600, "zone": "NBPZ", "flood_risk": "Moderate"},
    # BVZ
    {"name": "Cachar (Silchar)", "lat": 24.8333, "lon": 92.7789, "zone": "BVZ", "flood_risk": "High"},
    {"name": "Karimganj", "lat": 24.8700, "lon": 92.3500, "zone": "BVZ", "flood_risk": "High"},
    {"name": "Hailakandi", "lat": 24.6800, "lon": 92.5600, "zone": "BVZ", "flood_risk": "High"},
    # HZ
    {"name": "Karbi Anglong (Diphu)", "lat": 25.8400, "lon": 93.4300, "zone": "HZ", "flood_risk": "Low (Erosion Prone)"},
    {"name": "West Karbi Anglong (Hamren)", "lat": 25.8600, "lon": 92.5500, "zone": "HZ", "flood_risk": "Low (Erosion Prone)"},
    {"name": "Dima Hasao (Haflong)", "lat": 25.1700, "lon": 93.0200, "zone": "HZ", "flood_risk": "Low (Landslide Prone)"}
]

# Assam Land Measurement Conversion Factors
# 1 Hectare = 7.471 Bigha = 2.47105 Acres
# 1 Bigha = 5 Katha = 100 Lessa = 1337.8038 sq meters = 14,400 sq ft
# 1 Katha = 20 Lessa = 267.56 sq meters = 2,880 sq ft
# 1 Lessa = 13.378 sq meters = 144 sq ft
HECTARE_TO_BIGHA = 7.471
HECTARE_TO_ACRE = 2.47105
BIGHA_TO_SQ_METERS = 1337.8038
BIGHA_TO_KATHA = 5.0
KATHA_TO_LESSA = 20.0
BIGHA_TO_LESSA = 100.0

def format_land_area(bighas: float) -> Dict[str, Any]:
    """
    Convert land area in Bighas to full Assam traditional units (Bigha, Katha, Lessa)
    as well as standard metric (Hectares, Acres, Sq. Meters).
    """
    total_lessa = round(bighas * BIGHA_TO_LESSA)
    whole_bighas = int(total_lessa // 100)
    rem_lessa = total_lessa % 100
    katha = int(rem_lessa // 20)
    lessa = int(rem_lessa % 20)

    hectares = round(bighas / HECTARE_TO_BIGHA, 3)
    acres = round(hectares * HECTARE_TO_ACRE, 3)
    sq_meters = round(bighas * BIGHA_TO_SQ_METERS, 1)

    local_formatted = f"{whole_bighas} Bigha"
    if katha > 0:
        local_formatted += f" {katha} Katha"
    if lessa > 0 or (whole_bighas == 0 and katha == 0):
        local_formatted += f" {lessa} Lessa"

    # Authentic Assamese numerals (০, ১, ২, ৩, ৪, ৫, ৬, ৭, ৮, ৯)
    as_digits = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
    local_formatted_as = f"{str(whole_bighas).translate(as_digits)} বিঘা"
    if katha > 0:
        local_formatted_as += f" {str(katha).translate(as_digits)} কঠা"
    if lessa > 0 or (whole_bighas == 0 and katha == 0):
        local_formatted_as += f" {str(lessa).translate(as_digits)} লেচা"

    return {
        "bighas": round(bighas, 2),
        "whole_bighas": whole_bighas,
        "katha": katha,
        "lessa": lessa,
        "hectares": hectares,
        "acres": acres,
        "sq_meters": sq_meters,
        "formatted_local": local_formatted,
        "formatted_local_as": local_formatted_as
    }

def get_district_flood_profile(district_name: str, zone_id: str) -> Dict[str, Any]:
    """
    Evaluate seasonal flood risk and crop contingency protocols for an Assam district.
    """
    dist_entry = next((d for d in ASSAM_DISTRICTS if d["name"].lower().startswith(district_name.lower())), None)
    risk_level = dist_entry.get("flood_risk", "Moderate") if dist_entry else "Moderate"

    if "Very High" in risk_level:
        contingency = {
            "risk_level": "Very High",
            "risk_level_as": "অতি উচ্চ বানপানীৰ আশংকা",
            "recurrence": "Annual multi-wave inundation (May-Jun, Jul-Aug, Sep)",
            "primary_rice_strategy": "Mandatory submergence-tolerant rice (Ranjit Sub-1, Bahadur Sub-1, Swarna Sub-1) capable of surviving 14-17 days underwater.",
            "contingency_varieties": ["Ranjit Sub-1", "Bahadur Sub-1", "Jalashree", "Jalkunwari", "Luit (post-flood)"],
            "action_guidance": "Prepare staggered wet-bed / dapog nurseries on elevated homestead land. If primary sali crop is swept by July-August floods, immediately transplant short-duration varieties like Luit, Dishang, or Kolong before September 10."
        }
    elif "High" in risk_level:
        contingency = {
            "risk_level": "High",
            "risk_level_as": "উচ্চ বানপানীৰ আশংকা",
            "recurrence": "Frequent riverine surges and waterlogging in low-lying pockets",
            "primary_rice_strategy": "Submergence-tolerant Sali varieties for lowlands; medium-duration rice on medium lands.",
            "contingency_varieties": ["Ranjit Sub-1", "Bahadur", "Gitesh (staggered)", "Prafulla"],
            "action_guidance": "Construct perimeter bunds and drainage outlets. Have contingency seeds of rabi mustard (TS-36, TS-38) ready for quick seeding as floodwaters recede in October."
        }
    elif "Low" in risk_level:
        contingency = {
            "risk_level": "Low (Erosion / Runoff)",
            "risk_level_as": "কম বানপানীৰ আশংকা (মাটি খহনীয়া)",
            "recurrence": "Flash floods and heavy runoff on sloping lands",
            "primary_rice_strategy": "Terraced / contour cultivation, Ahu and upland Sali rice.",
            "contingency_varieties": ["Ranjit", "Mahsuri", "Karbi Ginger", "Citrus"],
            "action_guidance": "Adopt contour bunding and vegetative barriers (vetiver grass) to check topsoil erosion during monsoon cloudbursts."
        }
    else:
        contingency = {
            "risk_level": "Moderate",
            "risk_level_as": "মধ্যমীয়া বানপানীৰ আশংকা",
            "recurrence": "Occasional localized waterlogging during peak monsoon",
            "primary_rice_strategy": "Standard high-yielding Sali varieties with good peripheral drainage.",
            "contingency_varieties": ["Ranjit", "Bahadur", "Pankaj", "TS-38 (Mustard)"],
            "action_guidance": "Maintain clear field drainage channels. Ensure timely transplanting in June-July to establish deep root anchoring before peak August rains."
        }

    return contingency
