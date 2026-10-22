"""
Assam Agro-climatic Zones and Districts Data.
Aligned with Assam Agricultural University (AAU) and Directorate of Agriculture, Assam.
"""

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
        "key_features": "Major tea growing belt, Sali rice, mustard, potato, citrus."
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

# Major Agricultural Districts with Coordinates
ASSAM_DISTRICTS = [
    {"name": "Jorhat", "lat": 26.7509, "lon": 94.2037, "zone": "UBVZ"},
    {"name": "Golaghat", "lat": 26.5167, "lon": 93.9667, "zone": "UBVZ"},
    {"name": "Dibrugarh", "lat": 27.4728, "lon": 94.9120, "zone": "UBVZ"},
    {"name": "Tinsukia", "lat": 27.4922, "lon": 95.3537, "zone": "UBVZ"},
    {"name": "Sivasagar", "lat": 26.9826, "lon": 94.6425, "zone": "UBVZ"},
    {"name": "Charaideo", "lat": 27.0250, "lon": 94.9500, "zone": "UBVZ"},
    {"name": "Majuli", "lat": 26.9600, "lon": 94.2200, "zone": "UBVZ"},
    {"name": "Nagaon", "lat": 26.3452, "lon": 92.6840, "zone": "CBVZ"},
    {"name": "Morigaon", "lat": 26.2500, "lon": 92.3300, "zone": "CBVZ"},
    {"name": "Hojai", "lat": 26.0000, "lon": 92.8600, "zone": "CBVZ"},
    {"name": "Kamrup (Guwahati)", "lat": 26.1512, "lon": 91.7412, "zone": "LBVZ"},
    {"name": "Nalbari", "lat": 26.4400, "lon": 91.4300, "zone": "LBVZ"},
    {"name": "Barpeta", "lat": 26.3200, "lon": 91.0000, "zone": "LBVZ"},
    {"name": "Bajali", "lat": 26.4900, "lon": 91.1700, "zone": "LBVZ"},
    {"name": "Bongaigaon", "lat": 26.5000, "lon": 90.5500, "zone": "LBVZ"},
    {"name": "Dhubri", "lat": 26.0200, "lon": 89.9700, "zone": "LBVZ"},
    {"name": "Goalpara", "lat": 26.1800, "lon": 90.6200, "zone": "LBVZ"},
    {"name": "Kokrajhar", "lat": 26.4000, "lon": 90.2700, "zone": "LBVZ"},
    {"name": "Sonitpur (Tezpur)", "lat": 26.6338, "lon": 92.8006, "zone": "NBPZ"},
    {"name": "Biswanath", "lat": 26.7300, "lon": 93.1500, "zone": "NBPZ"},
    {"name": "Lakhimpur", "lat": 27.2300, "lon": 94.1000, "zone": "NBPZ"},
    {"name": "Dhemaji", "lat": 27.4800, "lon": 94.5800, "zone": "NBPZ"},
    {"name": "Darrang (Mangaldai)", "lat": 26.4300, "lon": 92.0300, "zone": "NBPZ"},
    {"name": "Udalguri", "lat": 26.7400, "lon": 92.1000, "zone": "NBPZ"},
    {"name": "Cachar (Silchar)", "lat": 24.8333, "lon": 92.7789, "zone": "BVZ"},
    {"name": "Karimganj", "lat": 24.8700, "lon": 92.3500, "zone": "BVZ"},
    {"name": "Hailakandi", "lat": 24.6800, "lon": 92.5600, "zone": "BVZ"},
    {"name": "Karbi Anglong (Diphu)", "lat": 25.8400, "lon": 93.4300, "zone": "HZ"},
    {"name": "Dima Hasao (Haflong)", "lat": 25.1700, "lon": 93.0200, "zone": "HZ"}
]

# Assam Land Measurement Conversion Factors
# 1 Hectare = 7.47 Bigha = 2.47105 Acres
# 1 Bigha = 5 Katha = 100 Lessa = 1337.8 sq meters = 14400 sq ft
HECTARE_TO_BIGHA = 7.471
HECTARE_TO_ACRE = 2.47105
BIGHA_TO_SQ_METERS = 1337.8038
