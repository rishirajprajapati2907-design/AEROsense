"""
AEROsense Historical Dataset Loader & Profiler
Loads and inspects the physical sensor dataset from:
  1. Primary: data/aerosense_historical_data.xlsx (Excel OpenPyXL)
  2. Fallback: data/aerosense_historical_data.csv
Total verified records: 5,024 rows.
Preserves original sensor readings and missing values (never converts missing to zero).
"""

import os
import math
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, Dict, Any, List
import pandas as pd
import numpy as np

from config import SENSOR_FIELDS

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
EXCEL_FILE_PATH = os.path.join(DATA_DIR, "aerosense_historical_data.xlsx")
CSV_FILE_PATH = os.path.join(DATA_DIR, "aerosense_historical_data.csv")

# Expected ThingSpeak channel field mapping
EXPECTED_COLUMNS = [
    "created_at",
    "entry_id",
    "field1",
    "field2",
    "field3",
    "field4",
    "field5",
    "field6",
    "field7",
]


def ensure_data_directory():
    """Ensure data/ folder exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)


def inspect_historical_dataset(df_raw: pd.DataFrame, source_path: str) -> Dict[str, Any]:
    """
    Perform deep diagnostic inspection of the historical dataset.
    Identifies actual columns, timestamps, data types, missing values, and duplicate records.
    """
    total_records = len(df_raw)
    raw_columns = list(df_raw.columns)
    
    # Check duplicates
    dup_entry_id = int(df_raw["entry_id"].duplicated().sum()) if "entry_id" in df_raw.columns else 0
    dup_created_at = int(df_raw["created_at"].duplicated().sum()) if "created_at" in df_raw.columns else 0

    # Missing counts
    missing_counts = {}
    missing_pcts = {}
    dtypes_map = {}
    for col in df_raw.columns:
        null_count = int(df_raw[col].isnull().sum())
        missing_counts[col] = null_count
        missing_pcts[col] = round((null_count / max(1, total_records)) * 100, 2)
        dtypes_map[col] = str(df_raw[col].dtype)

    # Time bounds
    min_ts = df_raw["timestamp"].min() if "timestamp" in df_raw.columns else None
    max_ts = df_raw["timestamp"].max() if "timestamp" in df_raw.columns else None
    time_span_days = round((max_ts - min_ts).total_seconds() / 86400.0, 1) if (pd.notnull(min_ts) and pd.notnull(max_ts)) else 0.0

    # Summary stats for sensor fields
    stats = {}
    for f_id in SENSOR_FIELDS.keys():
        if f_id in df_raw.columns:
            s = df_raw[f_id].dropna()
            if not s.empty:
                stats[f_id] = {
                    "count": int(len(s)),
                    "min": float(s.min()),
                    "max": float(s.max()),
                    "mean": round(float(s.mean()), 2),
                    "std": round(float(s.std()), 2) if len(s) > 1 else 0.0,
                    "missing": int(df_raw[f_id].isnull().sum()),
                }

    file_format = "Excel (.xlsx)" if str(source_path).lower().endswith(".xlsx") else "CSV (.csv)"

    return {
        "source_path": source_path,
        "file_format": file_format,
        "total_records": total_records,
        "raw_columns": raw_columns,
        "duplicate_entries": dup_entry_id,
        "duplicate_timestamps": dup_created_at,
        "missing_counts": missing_counts,
        "missing_pcts": missing_pcts,
        "dtypes": dtypes_map,
        "min_timestamp": min_ts,
        "max_timestamp": max_ts,
        "time_span_days": time_span_days,
        "field_stats": stats,
    }


def load_historical_dataset(custom_path: Optional[str] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Load the ThingSpeak historical sensor dataset.
    Prioritizes data/aerosense_historical_data.xlsx; falls back to data/aerosense_historical_data.csv.
    Preserves missing values without replacing them with zeros.
    """
    ensure_data_directory()
    
    target_path = custom_path
    if not target_path:
        if os.path.exists(EXCEL_FILE_PATH):
            target_path = EXCEL_FILE_PATH
        elif os.path.exists(CSV_FILE_PATH):
            target_path = CSV_FILE_PATH
        else:
            target_path = EXCEL_FILE_PATH

    # Read data
    is_generated = False
    if not os.path.exists(target_path):
        # Fallback if neither file exists
        if os.path.exists(CSV_FILE_PATH):
            target_path = CSV_FILE_PATH
            df_raw = pd.read_csv(target_path)
        else:
            raise FileNotFoundError(f"Neither {EXCEL_FILE_PATH} nor {CSV_FILE_PATH} found.")
    else:
        if str(target_path).lower().endswith(".xlsx"):
            df_raw = pd.read_excel(target_path, engine="openpyxl")
        else:
            df_raw = pd.read_csv(target_path)

    # Standardize column headers (clean whitespace & lowercase)
    df_raw.columns = [str(c).strip().lower() for c in df_raw.columns]

    # Map aliases if user has custom column names
    col_aliases = {
        "timestamp": "created_at",
        "date": "created_at",
        "time": "created_at",
        "record_id": "entry_id",
        "id": "entry_id",
        "temperature": "field1",
        "humidity": "field2",
        "smoke": "field3",
        "carbon_monoxide": "field4",
        "co": "field4",
        "ammonia": "field5",
        "nh3": "field5",
        "ammonia_nh3": "field5",
        "nitrogen_oxides": "field6",
        "nox": "field6",
        "nitrogen_oxides_nox": "field6",
        "pm25": "field7",
        "pm2.5": "field7",
    }
    df_raw = df_raw.rename(columns=col_aliases)

    # Parse timestamps safely
    if "created_at" in df_raw.columns:
        df_raw["timestamp"] = pd.to_datetime(df_raw["created_at"], errors="coerce")
    elif "timestamp" not in df_raw.columns:
        df_raw["timestamp"] = pd.date_range(end=datetime.now(), periods=len(df_raw), freq="1min")

    # Sort chronologically
    df_raw = df_raw.sort_values("timestamp").reset_index(drop=True)

    # Convert sensor fields to numeric floats, strictly preserving NaNs
    for f_id in SENSOR_FIELDS.keys():
        if f_id in df_raw.columns:
            df_raw[f_id] = pd.to_numeric(df_raw[f_id], errors="coerce")
        else:
            df_raw[f_id] = np.nan

    # Deep diagnostic profiling
    inspection = inspect_historical_dataset(df_raw, target_path)

    # Metadata dictionary
    valid_counts = {f_id: int(df_raw[f_id].dropna().count()) for f_id in SENSOR_FIELDS.keys()}
    total_records = len(df_raw)
    min_date = df_raw["timestamp"].min()
    max_date = df_raw["timestamp"].max()

    meta = {
        "file_path": target_path,
        "file_format": inspection["file_format"],
        "is_generated_baseline": is_generated,
        "total_records": total_records,
        "valid_counts": valid_counts,
        "start_time": min_date,
        "end_time": max_date,
        "time_span_days": inspection["time_span_days"],
        "inspection": inspection,
    }

    return df_raw, meta


# Alias for backward compatibility
def load_historical_csv(custom_path: Optional[str] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    return load_historical_dataset(custom_path)


def filter_historical_by_date_range(
    df: pd.DataFrame,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> pd.DataFrame:
    """Filter DataFrame between start_date and end_date."""
    if df.empty or "timestamp" not in df.columns:
        return df

    filtered = df.copy()
    if start_date is not None:
        filtered = filtered[filtered["timestamp"] >= pd.to_datetime(start_date)]
    if end_date is not None:
        filtered = filtered[filtered["timestamp"] <= pd.to_datetime(end_date)]

    return filtered.reset_index(drop=True)
