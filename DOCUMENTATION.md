# 🌾 Assam Farm Analyzer: Technical & Agronomic Documentation

> **System Version:** 2.0.0  
> **Deployment Target:** Render / Docker Container / On-Premise  
> **Scientific Alignment:** Assam Agricultural University (AAU) Package of Practices  
> **Data Licensing:** 100% Free & Open Public Datasets (No API Keys Required)

---

## 1. Executive Summary

The **Assam Farm Analyzer** is an open-source, full-stack precision agriculture and agro-climatic decision intelligence platform engineered specifically for the 35 districts and 6 agro-climatic zones of Assam, India. The Brahmaputra and Barak river valleys present unique agricultural dynamics characterized by acidic soils ($\text{pH } 4.5 - 5.8$), high annual rainfall ($1,400 - 3,200\text{ mm}$), recurring monsoon flood waves, and localized land tenure measured in **Bigha, Katha, and Lessa**.

This system bridges the gap between raw Earth Observation (EO) satellite data, digital soil mapping, numerical weather predictions, and actionable on-ground agronomic advice tailored for smallholder farmers, Krishi Vigyan Kendras (KVKs), and agricultural extension officers.

---

## 2. Satellite Remote Sensing & Earth Observation

### 2.1 Satellite Constellation: Copernicus Sentinel-2
Vegetation health and canopy dynamics are monitored using the **Copernicus Sentinel-2** constellation (Sentinel-2A and Sentinel-2B), operated by the European Space Agency (ESA).

- **Orbit:** Sun-synchronous, polar orbit at an altitude of $786\text{ km}$.
- **Revisit Frequency:** 5 days at the equator (2–3 days over Assam due to overlapping swaths).
- **Processing Level:** Level-2A (L2A) — Bottom-Of-Atmosphere (BOA) reflectance in cartographic geometry (UTM/WGS84) with atmospheric correction applied via Sen2Cor.

### 2.2 Spectral Bands Utilized
| Band | Description | Central Wavelength ($\lambda$) | Spatial Resolution | Agricultural Significance |
| :--- | :--- | :--- | :--- | :--- |
| **B04** | Red | $665\text{ nm}$ | $10\text{ m}$ | Strong chlorophyll absorption band. Lower reflectance indicates higher chlorophyll density. |
| **B08** | Near-Infrared (NIR) | $842\text{ nm}$ | $10\text{ m}$ | High reflectance from spongy mesophyll cell structure of healthy green leaf tissue. |
| **SCL** | Scene Classification Layer | Quality Flag | $20\text{ m}$ | Categorizes pixels: Cloud shadow, water, vegetation, bare soil, high/medium clouds. |

### 2.3 Normalized Difference Vegetation Index (NDVI)
The Normalized Difference Vegetation Index quantifies green vegetative biomass:

$$\text{NDVI} = \frac{\rho_{\text{NIR}} - \rho_{\text{Red}}}{\rho_{\text{NIR}} + \rho_{\text{Red}}} = \frac{\text{B08} - \text{B04}}{\text{B08} + \text{B04}}$$

*Where $\rho$ represents surface reflectance calibrated between $0.0$ and $1.0$.*

### 2.4 Ingestion Pipeline & Cloud Masking
Assam experiences prolonged monsoon cloud cover from May to September. To ensure data integrity:
1. **STAC Catalog Access:** Queries Microsoft Planetary Computer STAC endpoint:
   `https://planetarycomputer.microsoft.com/api/stac/v1`
2. **Cloud Filtering:** Limits query to scenes with metadata `eo:cloud_cover < 35%`.
3. **Pixel Masking:** Uses the Scene Classification Layer (`SCL`) to isolate strictly valid land pixels:
   $$\text{Mask} = \text{SCL} \in \{4\text{ (Vegetation)}, 5\text{ (Bare Soil)}, 7\text{ (Unclassified)}\}$$
4. **Polygon Clipping:** Geometric clipping using `rioxarray` and `shapely` to compute the spatial mean over the farmer's specific field boundary.
5. **Disk Caching:** Caches extracted time series locally in `cache/ndvi_{lat}_{lon}.json` with a 5-day Time-To-Live (TTL) to prevent redundant remote queries.

### 2.5 Agronomic NDVI Interpretation Matrix
| NDVI Value | Biophysical Canopy Status | Agronomic Meaning in Assam |
| :--- | :--- | :--- |
| **$< 0.15$** | Water / Bare Soil / Inundation | Submerged land, flooded paddy field, or newly ploughed char land. |
| **$0.15 - 0.30$** | Fallow / Stubble / Stressed | Post-harvest stubble, early nursery emergence, or severe vegetative moisture stress. |
| **$0.30 - 0.50$** | Vegetative Growth / Moderate Canopy | Active tillering in Sali rice, young tea bushes, or branching mustard. |
| **$0.50 - 0.70$** | Dense Healthy Crop Canopy | Peak tillering, panicle emergence, mature tea flush, or lush banana groves. |
| **$> 0.70$** | Very Dense Vigorous Biomass | High-yielding crop canopy, unpruned tea estates, or dense perennial orchards. |

---

## 3. Soil Health Diagnostics & Liming Science

### 3.1 Data Acquisition & Dual-Tier Fallback
Soil physical and chemical characteristics are queried through a dual-tier pipeline:
1. **Tier 1 (ISRIC SoilGrids 2.0 REST API):** Queries global digital soil mapping models at $250\text{ m}$ spatial resolution for depths $0-5\text{ cm}$ and $5-15\text{ cm}$.
2. **Tier 2 (AAU Baseline Fallback):** If SoilGrids encounters latency or network timeouts, the system automatically falls back to verified agro-climatic zone baselines established by the Directorate of Research, Assam Agricultural University.
3. **Tier 3 (Soil Health Card Override):** Farmers or extension agents with physical Soil Health Card (SHC) lab test results can input exact laboratory values (pH, Organic Carbon %, Clay %, Sand %).

### 3.2 Soil Acidity & Liming Calculations
Over $80\%$ of Assam's soils are acidic due to heavy leaching under high precipitation. While Assam Tea thrives in acidic environments ($\text{pH } 4.5 - 5.5$), pulses, oilseeds (Mustard), and vegetables require soil conditioning.

Agricultural lime ($\text{CaCO}_3$) or dolomite is prescribed based on soil acidity thresholds:
$$\text{Lime Dose} = \begin{cases} 
250\text{ kg / Bigha } (\approx 1.87\text{ tonnes/ha}) & \text{if } \text{pH} < 4.8 \\ 
150\text{ kg / Bigha } (\approx 1.12\text{ tonnes/ha}) & \text{if } 4.8 \le \text{pH} < 5.5 \\ 
0\text{ kg} & \text{if } \text{pH} \ge 5.5 \text{ or Crop is Tea} 
\end{cases}$$

Agricultural lime must be incorporated thoroughly during primary tillage at least **30 days prior to sowing/transplanting**, combined with organic manure to neutralize active aluminum and manganese toxicity.

---

## 4. Agro-Meteorological Integration

Historical and live meteorological indicators are queried from **Open-Meteo**:
- **10-Year Agro-Climate Norms:** Total annual precipitation, Kharif (Monsoon: Jun–Oct) rainfall, Rabi (Winter: Nov–Feb) rainfall, and seasonal temperature extremes.
- **7-Day Field Forecast:** Daily maximum/minimum temperatures, precipitation volume, precipitation probability, and **pesticide spraying feasibility advisories** based on forecasted rainfall.

---

## 5. Crop Decision Engine & Economic Modeling

### 5.1 Assam Land Measurement Conversions
The engine converts all areas and recommendations into official Assam revenue units:
$$1\text{ Hectare} = 7.471\text{ Bighas} = 2.471\text{ Acres}$$
$$1\text{ Bigha} = 5\text{ Kathas} = 100\text{ Lessas} = 1,337.8038\text{ m}^2 = 14,400\text{ ft}^2$$
$$1\text{ Katha} = 20\text{ Lessas} = 267.56\text{ m}^2 = 2,880\text{ ft}^2$$
$$1\text{ Lessa} = 13.378\text{ m}^2 = 144\text{ ft}^2$$

### 5.2 Multi-Factor Crop Suitability Scoring
Suitability is computed through a normalized non-linear penalty algorithm:

$$S_{\text{crop}} = \left[ 0.55 \cdot \left(\frac{1}{n} \sum_{i=1}^n s_i\right) + 0.45 \cdot \min(s_1, s_2, \dots, s_n) \right] \times 100$$

*Where $s_i$ evaluates soil pH, clay content, annual rainfall, mean temperature, and flood vulnerability. The weighted minimum penalty enforces Liebig's Law of the Minimum (the weakest limiting factor restricts overall crop success).*

### 5.3 Commercial Fertilizer Dosages (AAU Aligned)
Chemical nutrient recommendations from AAU are converted to commercial fertilizers:
- **Urea ($46\%\text{ N}$):** $\text{Urea (kg)} = \frac{\text{N (kg)}}{0.46} \times \frac{\text{Bighas}}{7.471}$
- **Single Super Phosphate / SSP ($16\%\text{ P}_2\text{O}_5$):** $\text{SSP (kg)} = \frac{\text{P}_2\text{O}_5\text{ (kg)}}{0.16} \times \frac{\text{Bighas}}{7.471}$
- **Muriate of Potash / MOP ($60\%\text{ K}_2\text{O}$):** $\text{MOP (kg)} = \frac{\text{K}_2\text{O (kg)}}{0.60} \times \frac{\text{Bighas}}{7.471}$
- Commercial $50\text{ kg}$ bags required are calculated via ceiling integer division: $\lceil \text{kg} / 50 \rceil$.

### 5.4 Production Economics & ROI
For each of the 20 crops, expected financial returns are calculated:
$$\text{Expected Yield} = Y_{\text{bigha}} \times \text{Bighas}$$
$$\text{Gross Revenue (₹)} = \text{Expected Yield} \times \text{Farm Gate Price / MSP}$$
$$\text{Total Cost of Cultivation (₹)} = C_{\text{bigha}} \times \text{Bighas}$$
$$\text{Net Profit (₹)} = \text{Gross Revenue} - \text{Total Cost}$$
$$\text{Benefit-Cost Ratio (B:C)} = \frac{\text{Gross Revenue}}{\text{Total Cost}}$$

---

## 6. Disaster Risk Reduction: Flood Contingency

Assam's 35 districts are categorized into 4 flood vulnerability tiers:
1. **Very High Flood Risk** (*Majuli, Dhemaji, Lakhimpur, Barpeta, Morigaon, Dhubri, South Salmara*):
   - **Mandatory Submergence-Tolerant Rice:** *Ranjit Sub-1*, *Bahadur Sub-1*, *Swarna Sub-1* (possess the *SUB1A* gene granting survival up to 17 days of complete submergence).
   - **Post-Flood Contingency:** If primary Sali crop is lost to July/August floods, immediate transplanting of extra-short duration varieties (*Luit*, *Dishang*, *Kolong* — 100 days duration) up to September 10.
2. **High Flood Risk** (*Nalbari, Goalpara, Bongaigaon, Biswanath, Cachar, Karimganj, Hailakandi*):
   - Staggered planting with flood-tolerant varieties; rapid transition to early Rabi oilseeds (Toria TS-36/TS-38) as waters recede in October.
3. **Moderate Flood Risk** (*Kamrup, Nagaon, Jorhat, Golaghat, Sivasagar, Dibrugarh, Sonitpur*):
   - Peripheral drainage bunds; standard high-yielding varieties (*Ranjit*, *Bahadur*, *Pankaj*).
4. **Low / Hill Erosion Risk** (*Karbi Anglong, Dima Hasao*):
   - Contour bunding and terracing; ginger, turmeric, and black pepper intercropping.

---

## 7. Primary Resources, References & Citations

1. **Assam Agricultural University (AAU), Jorhat:**
   - *Package of Practices for Kharif Crops of Assam (2020–2023)*.
   - *Package of Practices for Rabi Crops of Assam (2020–2023)*.
   - Directorate of Research (Agriculture), AAU, Jorhat-785013.
2. **Tocklai Tea Research Institute (TRA), Jorhat:**
   - *Tea Cultivation and Soil Management Guidelines for Brahmaputra & Barak Valleys*.
3. **European Space Agency (ESA):**
   - *Sentinel-2 User Handbook & Level-2A Algorithm Theoretical Basis Document (ATBD)*.
4. **Microsoft Planetary Computer:**
   - *STAC API & Sentinel-2 Cloud-Optimized GeoTIFF (COG) Assets*.
5. **ISRIC — World Soil Information:**
   - *SoilGrids 2.0: Automated global mapping of soil properties based on machine learning*.
6. **Open-Meteo Weather APIs:**
   - *High-resolution ECMWF & ERA5-Land Reanalysis Numerical Weather Data*.
