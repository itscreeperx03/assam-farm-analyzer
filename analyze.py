"""
Assam Farm Analyzer - Scientific Farm Intelligence CLI.
All free data sources, no API keys, AAU package of practices aligned.

Usage:
    python analyze.py sample_field.geojson
"""
import json
import sys
import subprocess
import time
from pathlib import Path

# Auto-bootstrap virtual environment if running with system python without packages
HERE = Path(__file__).resolve().parent
_win_venv = HERE / "venv" / "Scripts" / "python.exe"
_posix_venv = HERE / "venv" / "bin" / "python"
VENV_PYTHON = _win_venv if _win_venv.exists() else (_posix_venv if _posix_venv.exists() else None)

if VENV_PYTHON and sys.executable.lower() != str(VENV_PYTHON).lower():
    try:
        import shapely
        import requests
    except ModuleNotFoundError:
        sys.exit(subprocess.call([str(VENV_PYTHON)] + sys.argv))

from shapely.geometry import shape

from assam_data import HECTARE_TO_BIGHA, format_land_area, get_district_flood_profile
from services.geo_service import find_nearest_district, calculate_polygon_area
from services.soil_service import get_soil_analysis
from services.weather_service import get_historical_weather, get_forecast_weather
from services.satellite_service import get_ndvi_series
from services.advisor_service import score_all_crops, generate_farm_advisories

HERE = Path(__file__).resolve().parent

def main(path):
    fpath = Path(path)
    if not fpath.exists():
        sys.exit(f"File not found: {path}")

    gj = json.loads(fpath.read_text(encoding="utf-8"))
    geom = gj["geometry"] if gj.get("type") == "Feature" else gj
    polygon = shape(geom)
    c = polygon.centroid
    lat, lon = c.y, c.x

    print("\n" + "=" * 65)
    print("🌾 ASSAM FARM ANALYZER - AGRONOMIC INTELLIGENCE REPORT")
    print("=" * 65)

    # 1. Location & Zone
    geo = find_nearest_district(lat, lon)
    area = calculate_polygon_area(geom)
    bighas = area["bighas"]
    land_info = format_land_area(bighas)
    flood = get_district_flood_profile(geo["district"], geo["zone_id"])

    print(f"\n📍 LOCATION & LAND SIZE:")
    print(f"  Coordinates:    {lat:.4f}° N, {lon:.4f}° E")
    print(f"  Nearest Dist:   {geo['district']} ({geo['distance_km']} km away)")
    print(f"  Agro-Zone:      {geo['zone_name']} [{geo['zone_id']}]")
    print(f"  Field Area:     {land_info['formatted_local']} ({bighas:.2f} Bighas / {area['hectares']} Hectares)")
    print(f"  Flood Risk:     {flood['risk_level']} ({flood['risk_level_as']}) - {flood['recurrence']}")

    # 2. Soil
    print(f"\n🧪 SOIL HEALTH & DIAGNOSTICS:")
    override = HERE / "soil_override.json"
    shc_data = json.loads(override.read_text()) if override.exists() else None
    soil = get_soil_analysis(lat, lon, geo["zone_id"], shc_override=shc_data)
    print(f"  Data Source:    {soil['data_source']}")
    print(f"  Soil pH:        {soil['ph']} ({soil['liming']['status']})")
    print(f"  Texture:        {soil['texture']} (Clay: {soil['clay_pct']}%, Sand: {soil['sand_pct']}%)")
    print(f"  Organic Carbon: {soil['organic_carbon_g_per_kg']} g/kg ({soil['organic_carbon']['status']})")
    if soil['liming']['needs_lime']:
        print(f"  ⚠️ Liming Req:  {soil['liming']['advice']}")

    # 3. Weather
    print(f"\n🌦️ AGRO-CLIMATIC WEATHER:")
    weather = get_historical_weather(lat, lon)
    print(f"  Annual Rain:    {weather['annual_rain_mm']:.0f} mm")
    print(f"  Monsoon Rain:   {weather['monsoon_rain_mm']:.0f} mm (Kharif)")
    print(f"  Winter Rain:    {weather['rabi_rain_mm']:.0f} mm (Rabi)")
    print(f"  Mean Temp:      {weather['mean_temp_c']} °C (Max: {weather['summer_max_c']}°C, Min: {weather['winter_min_c']}°C)")

    # 4. Satellite NDVI
    print(f"\n🛰️ SATELLITE VEGETATION COVER (Sentinel-2):")
    try:
        ndvi = get_ndvi_series(geom)
        if ndvi:
            latest = ndvi[-1]
            print(f"  Observations:   {len(ndvi)} clear passes")
            print(f"  Latest Index:   NDVI {latest['ndvi']} ({latest['date']}) - {latest['interpretation']['status']}")
        else:
            print("  Cloud cover high; standard baseline cover assumed.")
    except Exception as e:
        print(f"  Satellite note: {e}")
        ndvi = []

    # 5. Crop Suitability & AAU Fertilizer Recommendations
    print(f"\n🌾 TOP SUITABLE CROPS (Assam Agricultural University Aligned):")
    rankings = score_all_crops(soil, weather, geo["zone_id"], area_bighas=bighas)
    for r in rankings[:6]:
        fert = r["fertilizer"]["per_bigha"]
        econ = r.get("economics", {})
        print(f"\n  [{r['score']:2d}%] {r['name_en']} ({r['name_as']}) - {r['verdict']}")
        print(f"       Season:     {r['season_en']}")
        if r["recommended_varieties"]:
            print(f"       Varieties:  {', '.join(r['recommended_varieties'][:2])}")
        print(f"       Fert/Bigha: Urea: {fert['urea_kg']} kg | SSP: {fert['ssp_kg']} kg | MOP: {fert['mop_kg']} kg | FYM: {fert['fym_ton']} t")
        if econ.get("total_net_profit_inr"):
            print(f"       Economics:  Est. Field Yield: {econ.get('total_expected_yield', 0):,} {econ.get('yield_unit')} | Est. Net Profit: ₹{econ.get('total_net_profit_inr', 0):,} (B:C Ratio: {econ.get('bc_ratio', 0)})")
        if r["issues"]:
            print(f"       Note:       {r['issues'][0]}")

    # 6. Farm Advisories
    print(f"\n💡 PRIORITY AGRONOMIC ADVISORIES:")
    advisories = generate_farm_advisories(soil, weather, ndvi, geo["zone_details"], district_name=geo["district"])
    for adv in advisories:
        print(f"  * {adv['title']}: {adv['text']}")

    # Save report.json
    full_report = {
        "location": geo,
        "flood_profile": flood,
        "area": {**area, **land_info},
        "soil": soil,
        "weather": weather,
        "ndvi_series": ndvi,
        "crop_rankings": rankings,
        "advisories": advisories
    }
    (HERE / "report.json").write_text(json.dumps(full_report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✅ Full analysis saved to: report.json")
    print(f"💡 To open the interactive Web App, run: python server.py (or visit http://127.0.0.1:8000)")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python analyze.py sample_field.geojson")
    main(sys.argv[1])
