# AEROsense – AI-Powered Indoor Air Quality Monitoring & Prediction Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A commercial IoT-grade environmental monitoring platform featuring real-time physical ESP32 telemetry via ThingSpeak and deep offline time-series analytics on a verified 5,024-record historical Excel dataset.

---

## 📡 Channel Specifications

- **Channel Name:** `AEROsense Air Quality`
- **Channel ID:** `3540991`
- **Access Level:** `PRIVATE` (Requires Read API Key from `.env`)
- **Auto-Refresh Rate:** Every 15 seconds (respects ThingSpeak API rate limits)

### Field Mapping

| Field | Parameter | Hardware Sensor | Unit | Validated Threshold Guide |
| :--- | :--- | :--- | :--- | :--- |
| **Field 1** | Temperature | DHT22 / BME280 | °C (toggle °F) | 20.0 – 24.5 °C (Optimal) |
| **Field 2** | Relative Humidity | DHT22 / BME280 | % RH | 35 – 50 % (Optimal), 30 – 60 % (Acceptable) |
| **Field 3** | Smoke | MQ-2 / MQ-135 | ppm / index | < 40 ppm (Normal), > 90 ppm (Warning) |
| **Field 4** | Carbon Monoxide (CO) | MQ-7 Sensor | ppm / index | < 9 ppm (Safe), > 25 ppm (OSHA Warning) |
| **Field 5** | Ammonia (NH3) | MQ-137 / MQ-135 | ppm / index | < 5 ppm (Safe), > 15 ppm (Irritant) |
| **Field 6** | Nitrogen Oxides (NOx) | MICS-6814 / NO2 | ppm / index | < 0.05 ppm (Clean), > 0.10 ppm (Elevated) |
| **Field 7** | PM2.5 Particulates | PMS5003 / SDS011 | µg/m³ | < 12 µg/m³ (WHO Good), > 35.4 µg/m³ (Unhealthy) |
| **Field 8** | *Not Configured* | None | — | Reserved / Inactive |

---

## 🌐 Dual Operating Modes

1. **HISTORICAL MODE (Excel Dataset):**
   - Automatically loads `data/aerosense_historical_data.xlsx` (with fallback to `.csv`).
   - 5,024 verified records spanning 15.1 days (`2026-10-18 08:30:12` to `2026-11-02 09:59:50`).
   - Fully functional offline even when the physical ESP32 node or ThingSpeak network is powered OFF.
   - Missing readings (9 intermittent packet drops on Temperature/Humidity) are safely preserved as `--` and never replaced with zeros.
2. **LIVE MODE (ThingSpeak REST):**
   - Connects to private Channel ID `3540991` via HTTPS REST API using credentials loaded securely from `.env`.
   - Automated 15-second fragment reruns (`@st.fragment`).
   - Three clear connection states: **LIVE** (new feeds arriving), **STALE** (>5 min delay), and **OFFLINE** (unreachable/powered off).

---

## 🧭 7-Page Architecture

1. **📊 Overview:**
   - Environmental Health Assessment banner with dominant pollutant identification.
   - Circular preliminary AQI gauge (custom validated multi-gas composite index).
   - Interactive 3D WebGL atmospheric dispersion sphere (Three.js with real-time mouse-drag rotation).
   - 7 Real-time KPI Cards with embedded Plotly sparklines.
   - Telemetry Channel Register table.
2. **📡 Sensor Monitoring:**
   - Dedicated deep-dive surveillance per sensor.
   - Current reading, Min, Mean, Max, Std Dev metrics.
   - Zoomable Plotly trend chart with safety threshold lines.
   - Distribution visualization: toggle between **Frequency Histogram** and **Box Plot**.
   - Recent stream record log.
3. **🧠 AI Analytics:**
   - 24-Hour Diurnal Pollution Pattern Analysis across hours 00:00 to 23:00.
   - Time-series forecaster with 1-hour horizon projection and 90% confidence interval.
   - Honest model evaluation metrics (MAE, RMSE, R²) on an 80/20 holdout split.
   - Model readiness progress checklist.
4. **🛡️ Anomaly Detection & Alerts:**
   - Real-time environmental action alerts with severity rankings (Normal, Moderate, Warning, Critical) and actionable safety instructions.
   - Sensor fault scanner detecting frozen ADC values, negative bounds, and statistical spikes.
   - Interactive anomaly timeline scanner with flagged diamond markers.
   - Top peak pollution episodes table.
5. **📈 Historical Trends:**
   - Filter windows: Hourly, Daily, Weekly, Full Archive.
   - Custom date-range slider.
   - Inter-sensor Pearson correlation matrix heatmap.
   - Dual-axis sensor comparison chart.
   - Interactive scatter plot with OLS linear regression trendline.
   - Grid of 7 individual parameter trend curves.
6. **📑 Reports & Audit:**
   - Executive indoor air audit summary sheet.
   - Monitored hours, Safe ambient compliance %, Data packet integrity.
   - Detailed spreadsheet inspection & missing value breakdown table.
   - One-click dataset export as CSV and Excel (`.xlsx`).
7. **⚙️ Settings:**
   - Operating mode switcher (Historical vs Live).
   - ThingSpeak REST Channel credentials and masked key verification.
   - Spreadsheet dataset file management and uploader (`.xlsx` or `.csv`).
   - Hardware calibration offsets (Temperature, Humidity, PM2.5, CO).

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.10+
- Streamlit >= 1.33.0

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your private ThingSpeak Read API Key:
```ini
THINGSPEAK_CHANNEL_ID=3540991
THINGSPEAK_READ_API_KEY=YOUR_READ_API_KEY_HERE
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🔒 Security & Data Integrity
- Zero modifications to ESP32 firmware code.
- ThingSpeak channel schema remains untouched.
- API keys are masked and loaded strictly from `.env`.
- Missing sensor values remain missing (`--`) and are never zero-padded or fabricated.
- Custom air-quality scores are clearly labeled as preliminary and non-statutory.
