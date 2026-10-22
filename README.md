# 🌾 Assam Farm Analyzer

An open-source, full-stack agricultural decision support system designed specifically for the agro-climatic zones of Assam, India. Built with 100% free and open public data sources—no API keys or subscriptions required.

Aligned with the **Assam Agricultural University (AAU) Package of Practices**.

---

## ✨ Key Features

- **Interactive Web GIS & GeoJSON Upload**: Draw custom farm plots on an interactive satellite/topographic map, load sample fields, or upload `.geojson` boundary files with instant centering and area measurement.
- **Assam Agro-Climatic Intelligence**: Automatic mapping to Assam's 6 agro-climatic zones (LBVZ, UBVZ, CBVZ, NBPZ, BVZ, Hill Zone) across all 35 districts.
- **District Flood Vulnerability & Contingency Planning**: Multi-wave flood risk classification (May-Jun, Jul-Aug, Sep) with submergence-tolerant variety recommendations (Ranjit Sub-1, Bahadur Sub-1, Swarna Sub-1) and post-flood emergency contingency varieties (Luit, Dishang, Kolong).
- **Multilingual Support (অসমীয়া / English / हिन्दी)**: Real-time UI and agronomic recommendations in Assamese, English, and Hindi.
- **20+ Major Assam Crops (AAU Aligned)**:
  - **Cereals**: Sali Rice (Winter), Ahu Rice (Autumn), Boro Rice (Summer), Assam Joha Rice (GI Tagged Aromatic).
  - **Plantation & Cash Crops**: Assam Tea (Tocklai clones), Assam Lemon / Kaji Nemu (GI Tagged), Bhut Jolokia / King Chilli (GI Tagged), Arecanut / Tamul, Black Pepper / Jaluk, Jute.
  - **Spices & Tubers**: Karbi Organic Ginger (GI), Turmeric (Megha-1), Potato.
  - **Oilseeds & Pulses**: Mustard / Toria (TS-36, TS-38), Black Gram / Matikalai, Lentil / Masur, Sesamum / Til.
  - **Horticulture**: Banana (Malbhog & Jahaji), Winter Cabbage & Cauliflower, Pointed Gourd / Parwal (Potal for Char lands).
- **AAU Production Economics & ROI Calculator**: Computes expected field yield, cultivation cost, gross revenue, net profit in Rupees (₹), and Benefit-Cost (B:C) ratio for any custom field size.
- **Integrated Pest & Disease Management (IPM)**: Detailed pest symptoms, economic threshold levels (ETL), biological/cultural controls, and AAU-approved chemical dosages.
- **Land Measurement in Bigha, Katha & Lessa**: Converts field areas to authentic Assam units (1 Hectare = 7.471 Bighas; 1 Bigha = 5 Katha = 100 Lessa) displayed in both English and Assamese numerals (e.g. `৩ বিঘা ২ কঠা ১০ লেচা`).
- **Commercial Fertilizer Prescriptions**: Exact bag counts (Urea 46% N, SSP 16% P2O5, MOP 60% K2O, FYM, and Agricultural Lime) with split application timetables.
- **Dual Soil Pipeline**: Uses SoilGrids global REST API with automatic failover to AAU agro-climatic zone baselines, plus Soil Health Card (SHC) lab test overrides.
- **Open-Meteo Weather Integration**: Fetches 10-year historical agro-climate norms and live 7-day weather forecasts with pesticide spraying feasibility indicators.
- **Sentinel-2 Satellite Vegetation (NDVI)**: Analyzes Copernicus Sentinel-2 satellite passes to evaluate canopy health and vegetative vigor.
- **Printable Farmer Advisory Card**: One-click generation of high-contrast, bilingual, A4/PDF printable farmer advisory sheets (`/api/export-advisory-card`).

---

## 🚀 Quick Setup

### 1. Requirements
- Python 3.10+
- Modern Web Browser (Chrome, Firefox, Edge, Safari)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/itscreeperx03/assam-farm-analyzer.git
cd assam-farm-analyzer

# Create and activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🖥️ Usage

### Option 1: Interactive Web App (Recommended)
Start the FastAPI server:
```bash
python server.py
```
Open your browser at **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.
- Draw or upload a farm boundary.
- Explore Crop Suitability, Economics & Yield (ROI in ₹), AAU Fertilizer Calculator, Step-by-Step Cultivation Roadmap, and NDVI Trends.
- Toggle between English, Assamese (অসমীয়া), and Hindi.
- Click **"Advisory Card"** or **"Print Field Report"** for offline distribution to farmers.

### Option 2: Command-Line Analysis
Run the standalone CLI tool on any GeoJSON field polygon:
```bash
python analyze.py sample_field.geojson
```
The CLI displays an ASCII report and saves detailed results to `report.json`.

---

## 🧪 Testing

Run the automated test suite:
```bash
python -m unittest tests/test_analyzer.py
```

---

## 📂 Project Architecture

```
assam-farm-analyzer/
├── analyze.py                 # CLI farm analysis tool
├── server.py                  # FastAPI REST API & static server
├── assam_data.py              # 35 districts, 6 agro-zones, flood risk, and Bigha/Katha/Lessa conversions
├── crops_assam_db.json        # AAU crop database (20 crops with varieties, economics & IPM)
├── sample_field.geojson       # Sample farm polygon (Kamrup district)
├── soil_override.example.json # Template for farmer Soil Health Card overrides
├── requirements.txt           # Python dependencies
├── tests/
│   └── test_analyzer.py       # Automated unit & integration tests
├── services/
│   ├── geo_service.py         # District lookup & bigha area calculation
│   ├── soil_service.py        # SoilGrids REST client & AAU fallback
│   ├── weather_service.py     # Open-Meteo historical & forecast client
│   ├── satellite_service.py   # Sentinel-2 NDVI processing
│   └── advisor_service.py     # AAU crop scoring, economics & fertilizer calculator
└── static/
    ├── index.html             # Responsive web application interface
    ├── css/style.css          # Modern dashboard styling & economics table
    └── js/
        ├── app.js             # Leaflet map, API integration, economics & charts
        └── i18n.js            # English / Assamese / Hindi translation engine
```

---

## 📜 License
MIT License. Created for the farming communities, extension officers (KVKs), and agricultural researchers of Assam.
