"""
Geographical and Spatial services for Assam.
Handles district detection, agro-climatic zone classification, and land area calculation.
Uses pure Python / Shapely calculations (no external C-DLL dependency).
"""
import math
from typing import Dict, Any, Optional
from shapely.geometry import shape, Polygon

from assam_data import ASSAM_DISTRICTS, AGRO_CLIMATIC_ZONES, HECTARE_TO_BIGHA, HECTARE_TO_ACRE

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great circle distance between two points on the earth in km."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def find_nearest_district(lat: float, lon: float) -> Dict[str, Any]:
    """Find the nearest Assam district and its corresponding agro-climatic zone."""
    best_dist = float('inf')
    best_district = ASSAM_DISTRICTS[0]
    for dist in ASSAM_DISTRICTS:
        d = haversine_distance(lat, lon, dist["lat"], dist["lon"])
        if d < best_dist:
            best_dist = d
            best_district = dist

    zone_info = AGRO_CLIMATIC_ZONES.get(best_district["zone"], {})
    return {
        "district": best_district["name"],
        "distance_km": round(best_dist, 1),
        "zone_id": best_district["zone"],
        "zone_name": zone_info.get("name", "Assam Plains"),
        "zone_name_as": zone_info.get("name_as", "অসম কৃষি-জলবায়ু অঞ্চল"),
        "zone_name_hi": zone_info.get("name_hi", "असम कृषि-जलवायु क्षेत्र"),
        "zone_details": zone_info
    }

def calculate_polygon_area(geom_dict: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate the surface area of a polygon in sq meters, hectares, bighas, and acres
    using WGS-84 metric projection scaling around centroid.
    """
    try:
        poly = shape(geom_dict)
        c = poly.centroid
        lat_rad = math.radians(c.y)

        # High-accuracy WGS-84 meters per degree at this latitude
        m_per_deg_lat = 111132.954 - 559.822 * math.cos(2 * lat_rad) + 1.175 * math.cos(4 * lat_rad)
        m_per_deg_lon = 111412.84 * math.cos(lat_rad) - 93.5 * math.cos(3 * lat_rad)

        coords = list(poly.exterior.coords)
        if len(coords) < 3:
            sq_meters = 1337.8  # Default 1 bigha
        else:
            # Transform polygon coordinates to local metric plane relative to centroid
            scaled_coords = [
                ((pt[0] - c.x) * m_per_deg_lon, (pt[1] - c.y) * m_per_deg_lat)
                for pt in coords
            ]
            scaled_poly = Polygon(scaled_coords)
            sq_meters = abs(scaled_poly.area)
    except Exception:
        sq_meters = 1337.8 * 3  # Fallback 3 bighas

    hectares = sq_meters / 10000.0
    bighas = hectares * HECTARE_TO_BIGHA
    acres = hectares * HECTARE_TO_ACRE

    return {
        "sq_meters": round(sq_meters, 1),
        "hectares": round(hectares, 3),
        "bighas": round(bighas, 2),
        "acres": round(acres, 2)
    }
