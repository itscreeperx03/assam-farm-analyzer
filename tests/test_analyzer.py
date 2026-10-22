"""
Automated Test Suite for Assam Farm Analyzer.
Covers agro-climatic zoning, land conversions, soil diagnostics,
AAU crop scoring, fertilizer & economics calculators, and server endpoints.
"""
import unittest
from assam_data import (
    ASSAM_DISTRICTS,
    AGRO_CLIMATIC_ZONES,
    format_land_area,
    get_district_flood_profile,
    HECTARE_TO_BIGHA
)
from services.geo_service import find_nearest_district, calculate_polygon_area
from services.soil_service import get_soil_analysis
from services.advisor_service import (
    load_crops_db,
    score_all_crops,
    calculate_fertilizer_for_area,
    generate_farm_advisories
)
from server import (
    list_districts,
    list_crops,
    calculate_fertilizer,
    get_crop_ipm,
    analyze_farm,
    export_advisory_card,
    FertilizerCalcRequest,
    AnalysisRequest,
    SoilHealthCardInput
)


class TestAssamData(unittest.TestCase):
    def test_districts_and_zones_consistency(self):
        """Ensure all districts have valid coordinates and map to recognized zones."""
        self.assertGreaterEqual(len(ASSAM_DISTRICTS), 30)
        zone_keys = set(AGRO_CLIMATIC_ZONES.keys())
        for d in ASSAM_DISTRICTS:
            self.assertIn("name", d)
            self.assertIn("lat", d)
            self.assertIn("lon", d)
            self.assertIn("zone", d)
            self.assertIn(d["zone"], zone_keys, f"District {d['name']} has invalid zone {d['zone']}")
            # Latitude and Longitude should be roughly within Assam / NE bounds
            self.assertTrue(24.0 <= d["lat"] <= 28.5, f"Latitude {d['lat']} out of bounds for {d['name']}")
            self.assertTrue(89.0 <= d["lon"] <= 96.5, f"Longitude {d['lon']} out of bounds for {d['name']}")

    def test_land_area_formatting(self):
        """Verify Bigha, Katha, Lessa conversions."""
        # 1 Bigha = 100 Lessa = 5 Katha
        res1 = format_land_area(1.0)
        self.assertEqual(res1["whole_bighas"], 1)
        self.assertEqual(res1["katha"], 0)
        self.assertEqual(res1["lessa"], 0)
        self.assertIn("1 Bigha", res1["formatted_local"])

        # 3.5 Bighas = 3 Bighas 2 Katha 10 Lessa
        res2 = format_land_area(3.5)
        self.assertEqual(res2["whole_bighas"], 3)
        self.assertEqual(res2["katha"], 2)
        self.assertEqual(res2["lessa"], 10)
        self.assertIn("3 Bigha 2 Katha 10 Lessa", res2["formatted_local"])
        self.assertIn("৩ বিঘা", res2["formatted_local_as"])

    def test_flood_risk_profiles(self):
        """Verify flood profiles for high and low risk districts."""
        majuli_flood = get_district_flood_profile("Majuli", "UBVZ")
        self.assertEqual(majuli_flood["risk_level"], "Very High")
        self.assertTrue(len(majuli_flood["contingency_varieties"]) > 0)

        haflong_flood = get_district_flood_profile("Dima Hasao (Haflong)", "HZ")
        self.assertIn("Low", haflong_flood["risk_level"])


class TestGeoService(unittest.TestCase):
    def test_nearest_district(self):
        # Coordinates near Guwahati
        geo = find_nearest_district(26.1512, 91.7412)
        self.assertIn("Kamrup", geo["district"])
        self.assertEqual(geo["zone_id"], "LBVZ")

        # Coordinates near Jorhat
        geo_jorhat = find_nearest_district(26.75, 94.20)
        self.assertEqual(geo_jorhat["district"], "Jorhat")
        self.assertEqual(geo_jorhat["zone_id"], "UBVZ")

    def test_polygon_area_calculation(self):
        # 1 square degree around equator is large, but small ~100m box:
        sample_geom = {
            "type": "Polygon",
            "coordinates": [[[91.74, 26.15], [91.745, 26.15], [91.745, 26.155], [91.74, 26.155], [91.74, 26.15]]]
        }
        area = calculate_polygon_area(sample_geom)
        self.assertGreater(area["bighas"], 0)
        self.assertGreater(area["hectares"], 0)


class TestAdvisorService(unittest.TestCase):
    def test_load_crops_db(self):
        crops = load_crops_db()
        self.assertGreaterEqual(len(crops), 20)
        crop_ids = [c["id"] for c in crops]
        self.assertIn("sali_rice", crop_ids)
        self.assertIn("assam_tea", crop_ids)
        self.assertIn("mustard_toria", crop_ids)
        self.assertIn("joha_rice", crop_ids)
        self.assertIn("bhut_jolokia", crop_ids)

    def test_fertilizer_calculation(self):
        crops = load_crops_db()
        sali = next(c for c in crops if c["id"] == "sali_rice")
        calc = calculate_fertilizer_for_area(sali, area_bighas=3.0, soil_ph=5.4)
        self.assertEqual(calc["area_bighas"], 3.0)
        self.assertGreater(calc["total_for_field"]["urea_kg"], 0)
        self.assertGreater(calc["total_for_field"]["ssp_kg"], 0)
        self.assertGreater(calc["total_for_field"]["mop_kg"], 0)
        self.assertGreater(calc["total_for_field"]["urea_bags_50kg"], 0)

    def test_crop_scoring_and_economics(self):
        soil_mock = {"ph": 5.6, "clay_pct": 24.0, "sand_pct": 40.0, "organic_carbon_pct": 1.1}
        weather_mock = {"annual_rain_mm": 2200, "mean_temp_c": 24.0}
        rankings = score_all_crops(soil_mock, weather_mock, zone_id="LBVZ", area_bighas=3.0)
        self.assertGreater(len(rankings), 0)

        # Ensure every scored crop has economics and ipm
        top_crop = rankings[0]
        self.assertIn("economics", top_crop)
        econ = top_crop["economics"]
        self.assertGreater(econ["total_expected_yield"], 0)
        self.assertGreater(econ["total_gross_revenue_inr"], 0)
        self.assertIn("ipm", top_crop)


class TestServerEndpoints(unittest.TestCase):
    def test_districts_api(self):
        res = list_districts()
        self.assertIn("districts", res)
        self.assertIn("zones", res)

    def test_crops_api(self):
        res = list_crops()
        self.assertIn("crops", res)
        self.assertGreaterEqual(len(res["crops"]), 20)

    def test_fertilizer_calc_api(self):
        req = FertilizerCalcRequest(crop_id="mustard_toria", area_bighas=2.5)
        calc = calculate_fertilizer(req)
        self.assertEqual(calc["crop_id"], "mustard_toria")
        self.assertEqual(calc["area_bighas"], 2.5)

    def test_crop_ipm_api(self):
        ipm_res = get_crop_ipm("sali_rice")
        self.assertEqual(ipm_res["crop_id"], "sali_rice")
        self.assertIn("ipm", ipm_res)

    def test_full_farm_analysis_api(self):
        req = AnalysisRequest(
            lat=26.1512,
            lon=91.7412,
            area_bighas=3.0,
            include_satellite=False
        )
        report = analyze_farm(req)
        self.assertIn("location", report)
        self.assertIn("area", report)
        self.assertIn("soil", report)
        self.assertIn("crop_rankings", report)
        self.assertIn("farm_advisories", report)
        self.assertIn("flood_profile", report["location"])
        self.assertGreater(len(report["crop_rankings"]), 0)

    def test_export_advisory_card_html(self):
        req = AnalysisRequest(
            lat=26.1512,
            lon=91.7412,
            area_bighas=2.0,
            include_satellite=False
        )
        response = export_advisory_card(req)
        self.assertEqual(response.status_code, 200)
        self.assertIn("ASSAM FARM ADVISORY CARD", response.body.decode("utf-8"))
        self.assertIn("Kamrup", response.body.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
