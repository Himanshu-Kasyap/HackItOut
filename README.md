# ClimateLens AI – Climate Data Visualization Platform

A full-stack climate analytics dashboard for exploring climate datasets, visualizing global trends, and generating AI-powered insights.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript, Plotly.js |
| Backend | Python, Flask, Flask-CORS |
| Data Processing | Pandas, NumPy, Xarray |
| Machine Learning | Scikit-learn (Linear Regression) |
| Dataset Formats | CSV, NetCDF (.nc) |

---

## Project Structure

```
climate-lens-ai/
├── backend/
│   ├── app.py                  # Flask API server (7 endpoints)
│   ├── data_loader.py          # CSV / NetCDF loading & normalization
│   ├── climate_analysis.py     # Heatmap, time series, AI insights
│   └── ml_model.py             # Linear regression future predictions
├── frontend/
│   ├── index.html              # Dashboard layout
│   ├── style.css               # Dark theme styling
│   └── script.js               # Plotly.js charts + fetch API
├── datasets/
│   ├── gen_data.py             # Sample dataset generator script
│   ├── sample_climate_data.csv # 604,728 rows · 454 cities · 1990–2026
│   └── sample_climate_data.nc  # Same data in NetCDF4 format (3.9 MB)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup & Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Flask server

```bash
python backend/app.py
```

### 3. Open the app

Visit [http://localhost:5000](http://localhost:5000) in your browser.

> The frontend is served directly by Flask — do **not** open `index.html` as a file.

---

## Features

### 🗺️ Global Climate Heatmap
Interactive world map showing spatial distribution of any climate variable. Supports zoom, hover tooltips, year/month filtering.

### 📈 Location-Based Time Series
Select a city from the searchable dropdown (454 cities) to view monthly trends over time for any variable.

### 🤖 AI-Generated Insights
Automated statistical analysis including:
- Long-term trend direction and magnitude
- Peak and lowest recorded years
- Anomaly detection (>2σ from mean)
- Decade-over-decade comparison

### ⚖️ Climate Comparison Mode
Side-by-side global maps comparing climate variable distribution between any two years.

### 🔮 Future Climate Predictions
Linear regression model trained on historical data predicts future values with a ±1σ confidence band. Displays R² score and trend slope.

---

## Sample Dataset

| Property | Value |
|---|---|
| Rows | 604,728 |
| Cities | 454 (all continents) |
| Year range | 1990 – 2026 |
| Variables | temperature (°C), precipitation (mm), wind_speed (m/s), humidity (%), pressure (hPa) |
| Formats | CSV (35.6 MB), NetCDF4 (3.9 MB) |

### CSV column schema

```
year, month, week, city, latitude, longitude,
temperature, precipitation, wind_speed, humidity, pressure
```

### NetCDF structure

```
Dimensions: time (444), city (454)
Coordinates: time, city, latitude, longitude
Variables: temperature, precipitation, wind_speed, humidity, pressure
```

---

## API Endpoints

| Endpoint | Method | Params | Description |
|---|---|---|---|
| `/upload_dataset` | POST | `file` (multipart) | Upload CSV or NetCDF dataset |
| `/reset_dataset` | POST | — | Reset to sample dataset |
| `/get_dataset_info` | GET | — | Variables, cities, year range |
| `/get_heatmap_data` | GET | `variable`, `year`, `month` | Spatial aggregation for map |
| `/get_time_series` | GET | `variable`, `city` or `lat`+`lon` | Time series for a location |
| `/get_ai_insights` | GET | `variable`, `city` | AI-generated text insights |
| `/get_comparison_data` | GET | `variable`, `year1`, `year2` | Two-year comparison data |
| `/get_future_prediction` | GET | `variable`, `city`, `years_ahead` | ML regression predictions |

---

## Regenerating the Dataset

```bash
python datasets/gen_data.py
```

Generates `sample_climate_data.csv` with 454 cities × 37 years × 3 weekly readings.
