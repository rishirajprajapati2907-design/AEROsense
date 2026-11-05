"""
AEROsense Data Loader — Single source of truth for all data operations.
Loads, cleans, and enriches the actual historical Excel dataset.
"""
import os
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Tuple

EXCEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "aerosense_historical_data.xlsx")
CSV_PATH   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "aerosense_historical_data.csv")

# Sensor catalogue ─ units reflect what the sensor actually outputs
SENSORS: Dict[str, Dict[str, Any]] = {
    "field1": {
        "name": "Temperature",   "short": "Temp",        "unit": "°C",
        "icon": "🌡️",           "color": "#F59E0B",      "precision": 1,
        "description": "Ambient indoor air temperature measured by DHT22.",
        "note": "Calibrated °C readings.",
        "thresholds": {"low": 18, "ok_lo": 20, "ok_hi": 26, "high": 30},
    },
    "field2": {
        "name": "Humidity",      "short": "RH",          "unit": "%",
        "icon": "💧",           "color": "#06B6D4",      "precision": 1,
        "description": "Relative humidity measured by DHT22.",
        "note": "Calibrated % RH readings.",
        "thresholds": {"low": 25, "ok_lo": 35, "ok_hi": 60, "high": 70},
    },
    "field3": {
        "name": "Smoke",         "short": "Smoke",       "unit": "ADC",
        "icon": "💨",           "color": "#8B5CF6",      "precision": 0,
        "description": "Raw MQ-2 analog output — higher value = more smoke/combustion products.",
        "note": "Raw analog sensor counts (0–1023 scale). Not calibrated to ppm.",
        "thresholds": {"ok_hi": 280, "high": 320, "critical": 340},
    },
    "field4": {
        "name": "Carbon Monoxide","short": "CO",          "unit": "ADC",
        "icon": "⚠️",           "color": "#EF4444",      "precision": 0,
        "description": "Raw MQ-7 analog output — higher value = elevated CO conditions.",
        "note": "Raw analog sensor counts (0–1023 scale). Not calibrated to ppm.",
        "thresholds": {"ok_hi": 300, "high": 350, "critical": 400},
    },
    "field5": {
        "name": "Ammonia (NH₃)", "short": "NH₃",         "unit": "ADC",
        "icon": "🧪",           "color": "#A855F7",      "precision": 0,
        "description": "Raw MQ-137 analog output — higher value = elevated ammonia conditions.",
        "note": "Raw analog sensor counts (0–1023 scale). Not calibrated to ppm.",
        "thresholds": {"ok_hi": 220, "high": 280, "critical": 350},
    },
    "field6": {
        "name": "Nitrogen Oxides","short": "NOx",         "unit": "ADC",
        "icon": "🏭",           "color": "#EAB308",      "precision": 0,
        "description": "Raw MICS-6814 analog output — higher value = elevated NOx conditions.",
        "note": "Raw analog sensor counts (0–1023 scale). Not calibrated to ppm.",
        "thresholds": {"ok_hi": 180, "high": 220, "critical": 280},
    },
    "field7": {
        "name": "PM2.5",         "short": "PM2.5",       "unit": "ADC",
        "icon": "🌫️",           "color": "#EC4899",      "precision": 0,
        "description": "PMS5003 / Sharp GP2Y analog output. Most readings at sensor ceiling (560.9 ADC).",
        "note": "⚠️ Sensor saturated at 560.9 ADC during 95% of recordings. Non-saturated readings: 61.",
        "thresholds": {"ok_hi": 300, "high": 450, "critical": 500},
    },
}


def load_data() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load and prepare the historical dataset. Returns (df, meta_dict)."""
    path = EXCEL_PATH if os.path.exists(EXCEL_PATH) else CSV_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found at {path}")

    if path.endswith(".xlsx"):
        df = pd.read_excel(path, engine="openpyxl")
    else:
        df = pd.read_csv(path)

    df.columns = [str(c).strip().lower() for c in df.columns]
    df["timestamp"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)

    for f in SENSORS:
        df[f] = pd.to_numeric(df[f], errors="coerce")

    # Derived time columns
    df["date"]     = df["timestamp"].dt.date
    df["hour"]     = df["timestamp"].dt.hour
    df["day_name"] = df["timestamp"].dt.strftime("%a")
    df["week"]     = df["timestamp"].dt.isocalendar().week.astype(int)

    # Z-score based anomaly flags (per field)
    for f in SENSORS:
        s = df[f].dropna()
        if s.std() > 1e-6:
            z = (df[f] - s.mean()) / s.std()
            df[f"z_{f}"] = z.round(2)
            df[f"anom_{f}"] = z.abs() > 3.0
        else:
            df[f"z_{f}"] = 0.0
            df[f"anom_{f}"] = False

    # Metadata
    valid_counts = {f: int(df[f].notna().sum()) for f in SENSORS}
    total = len(df)
    completeness = round(100 * sum(valid_counts.values()) / (total * len(SENSORS)), 1)

    meta = {
        "file_path":    path,
        "file_format":  "Excel (.xlsx)" if path.endswith(".xlsx") else "CSV",
        "total_records": total,
        "valid_counts": valid_counts,
        "completeness": completeness,
        "start_time":   df["timestamp"].min(),
        "end_time":     df["timestamp"].max(),
        "span_days":    (df["timestamp"].max() - df["timestamp"].min()).days,
        "recording_days": df["date"].nunique(),
        "sensor_count": len(SENSORS),
    }
    return df, meta


def get_field_stats(df: pd.DataFrame, field: str) -> Dict[str, Any]:
    s = df[field].dropna()
    if s.empty:
        return {k: None for k in ["count","min","max","mean","median","std","p5","p95","latest"]}
    return {
        "count":  int(len(s)),
        "min":    round(float(s.min()), 2),
        "max":    round(float(s.max()), 2),
        "mean":   round(float(s.mean()), 2),
        "median": round(float(s.median()), 2),
        "std":    round(float(s.std()), 2),
        "p5":     round(float(s.quantile(0.05)), 2),
        "p95":    round(float(s.quantile(0.95)), 2),
        "latest": round(float(df.loc[df[field].notna(), field].iloc[-1]), 2),
    }


def filter_df(df: pd.DataFrame,
              start=None, end=None,
              fields: Optional[list] = None) -> pd.DataFrame:
    out = df.copy()
    if start:
        out = out[out["timestamp"] >= pd.to_datetime(start, utc=True)]
    if end:
        out = out[out["timestamp"] <= pd.to_datetime(end, utc=True)]
    return out.reset_index(drop=True)


def get_daily_summary(df: pd.DataFrame) -> pd.DataFrame:
    agg = {f: ["mean","min","max","std"] for f in SENSORS}
    daily = df.groupby("date").agg(agg)
    daily.columns = ["_".join(c) for c in daily.columns]
    daily["count"] = df.groupby("date").size()
    return daily.reset_index()


def get_hourly_profile(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("hour")[[f for f in SENSORS]].mean().round(2).reset_index()


def get_anomalies(df: pd.DataFrame, z_thresh: float = 3.0) -> pd.DataFrame:
    rows = []
    for f, cfg in SENSORS.items():
        s = df[f].dropna()
        if s.std() < 1e-6:
            continue
        z = (df[f] - s.mean()) / s.std()
        mask = z.abs() > z_thresh
        for idx in df.index[mask]:
            rows.append({
                "timestamp":   df.at[idx, "timestamp"],
                "sensor":      cfg["name"],
                "field":       f,
                "value":       round(df.at[idx, f], 2),
                "unit":        cfg["unit"],
                "z_score":     round(z[idx], 2),
                "severity":    "Critical" if abs(z[idx]) > 4 else "Warning",
                "direction":   "High" if z[idx] > 0 else "Low",
                "reason":      f"Reading {abs(z[idx]):.1f}σ {'above' if z[idx]>0 else 'below'} the sensor mean ({s.mean():.1f} {cfg['unit']})",
            })
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("timestamp", ascending=False).reset_index(drop=True)
