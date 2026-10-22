# 🌾 Assam Farm Analyzer

An open-source, full-stack agricultural decision support system designed specifically for the agro-climatic zones of Assam, India. Built with 100% free and open public data sources—no API keys or subscriptions required.

Aligned with the **Assam Agricultural University (AAU) Package of Practices**.

---

## ✨ Key Features

- **Interactive Web GIS Dashboard**: Draw custom farm plots on an interactive satellite/topographic map, or upload GeoJSON boundary files.
- **Assam Agro-Climatic Intelligence**: Automatic mapping to Assam's 6 agro-climatic zones (LBVZ, UBVZ, CBVZ, NBPZ, BVZ, Hill Zone) across all 35 districts.
- **Multilingual Support (অসমীয়া / English)**: Real-time UI and agronomic recommendations in Assamese and English.
- **AAU Package of Practices Aligned Crop Engine**: Scores 20+ major Assam crops (Sali Rice, Ahu Rice, Boro Rice, Kaji Nemu, Assam Tea, Bhut Jolokia, Joha Rice, Mustard, etc.) against soil and seasonal climate constraints.
- **Land Measurement in Bighas**: Automatically converts field areas to local Assam measurements (1 Hectare = 7.47 Bighas / 5 Katha per Bigha) and computes fertilizer dosages (Urea, SSP, MOP, FYM) per Bigha.
- **Dual Soil Pipeline**: Uses SoilGrids global REST API with automatic failover to AAU agro-climatic zone baselines, plus Soil Health Card manual override support.
- **Open-Meteo Weather Integration**: Fetches 10-year historical agro-climate norms (rainfall, temperature) and 7-day weather forecasts.
- **Sentinel-2 Satellite Vegetation (NDVI)**: Analyzes Copernicus Sentinel-2 satellite passes to evaluate canopy health and vegetative vigor.
- **Actionable Agronomic Advisories**: Guidance for flood/submergence resilience (e.g. Ranjit Sub-1), soil acidity liming, and seasonal pest scouting.

---

## 🚀 Quick Setup

### 1. Requirements
- Python 3.10+
- Internet connection (for satellite, soil, and weather APIs)

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
- Draw your farm polygon directly on the map, or load a sample field.
- View real-time zone detection, soil diagnostics, 7-day forecast, NDVI canopy health, and top recommended crops with exact fertilizer quantities per Bigha.
- Toggle between English and Assamese (অসমীয়া).

### Option 2: Command-Line Analysis
Run the standalone CLI tool on any GeoJSON field polygon:
```bash
python analyze.py sample_field.geojson
```
The CLI displays an ASCII report and saves detailed results to `report.json`.

---

## 📂 Project Architecture

```
assam-farm-analyzer/
├── analyze.py                 # CLI farm analysis tool
├── server.py                  # FastAPI REST API & static server
├── assam_data.py              # Assam districts, agro-zones, and AAU soil baselines
├── crops_assam_db.json        # AAU crop database (20+ crops with varieties & dosages)
├── sample_field.geojson       # Sample farm polygon (Kamrup district)
├── soil_override.example.json # Template for farmer Soil Health Card overrides
├── requirements.txt           # Python dependencies
├── services/
│   ├── geo_service.py         # District lookup & bigha area calculation
│   ├── soil_service.py        # SoilGrids REST client & AAU fallback
│   ├── weather_service.py     # Open-Meteo historical & forecast client
│   ├── satellite_service.py   # Sentinel-2 NDVI processing
│   └── advisor_service.py     # AAU crop scoring & fertilizer calculation
└── static/
    ├── index.html             # Responsive web application interface
    ├── css/style.css          # Modern dashboard styling
    └── js/
        ├── app.js             # Leaflet map, API integration & charts
        └── i18n.js            # English / Assamese translation engine
```

---

## 📜 License
MIT License. Created for the farming communities and agricultural researchers of Assam.
