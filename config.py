"""
AEROsense Dashboard Configuration
Channel ID: 3540991 | Name: AEROsense Air Quality | Access: PRIVATE
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ThingSpeak Channel Settings
DEFAULT_CHANNEL_ID = int(os.environ.get("THINGSPEAK_CHANNEL_ID", "3540991").strip() or 3540991)
DEFAULT_READ_API_KEY = os.environ.get("THINGSPEAK_READ_API_KEY", "").strip()
DEFAULT_CHANNEL_NAME = "AEROsense Air Quality"
THINGSPEAK_BASE_URL = "https://api.thingspeak.com"

# Timing & Rate Limits
REFRESH_INTERVAL_SECONDS = 15  # Conforms to ThingSpeak rate limit (15s minimum for free tier)
STALE_DATA_TIMEOUT_SECONDS = 300  # 5 minutes: warning for stale data
OFFLINE_TIMEOUT_SECONDS = 900    # 15 minutes: marked offline

# Field Mapping (1-indexed matching ThingSpeak field names)
SENSOR_FIELDS: Dict[str, Dict[str, Any]] = {
    "field1": {
        "id": "field1",
        "name": "Temperature",
        "short_name": "Temp",
        "default_unit": "°C",
        "alt_unit": "°F",
        "icon": "🌡️",
        "precision": 1,
        "description": "Ambient room temperature",
        # Validated comfort bands (°C)
        "thresholds": {
            "optimal_min": 20.0,
            "optimal_max": 24.5,
            "moderate_min": 18.0,
            "moderate_max": 27.0,
            "warning_min": 15.0,
            "warning_max": 30.0,
        },
        "default_calibration": {"scale": 1.0, "offset": 0.0},
    },
    "field2": {
        "id": "field2",
        "name": "Relative Humidity",
        "short_name": "Humidity",
        "default_unit": "%",
        "alt_unit": "%",
        "icon": "💧",
        "precision": 1,
        "description": "Relative indoor air humidity",
        # Validated comfort bands (% RH)
        "thresholds": {
            "optimal_min": 35.0,
            "optimal_max": 50.0,
            "moderate_min": 30.0,
            "moderate_max": 60.0,
            "warning_min": 20.0,
            "warning_max": 70.0,
        },
        "default_calibration": {"scale": 1.0, "offset": 0.0},
    },
    "field3": {
        "id": "field3",
        "name": "Smoke",
        "short_name": "Smoke",
        "default_unit": "ppm",
        "alt_unit": "index",
        "icon": "💨",
        "precision": 1,
        "description": "Combustion byproduct & smoke level",
        # Thresholds (ppm / normalized sensor index)
        "thresholds": {
            "optimal_max": 40.0,
            "moderate_max": 90.0,
            "warning_max": 180.0,
        },
        "default_calibration": {"scale": 1.0, "offset": 0.0},
    },
    "field4": {
        "id": "field4",
        "name": "Carbon Monoxide",
        "short_name": "CO",
        "default_unit": "ppm",
        "alt_unit": "ppm",
        "icon": "⚠️",
        "precision": 2,
        "description": "Colorless, odorless toxic combustion gas (EPA/OSHA guidelines)",
        # EPA/OSHA indoor thresholds (ppm): <9 normal, 9-25 moderate, 25-50 warning, >50 danger
        "thresholds": {
            "optimal_max": 9.0,
            "moderate_max": 25.0,
            "warning_max": 50.0,
        },
        "default_calibration": {"scale": 1.0, "offset": 0.0},
    },
    "field5": {
        "id": "field5",
        "name": "Ammonia",
        "short_name": "NH3",
        "default_unit": "ppm",
        "alt_unit": "ppm",
        "icon": "🧪",
        "precision": 2,
        "description": "Pungent alkaline gas from cleaning agents/waste",
        # OSHA / NIOSH indoor exposure thresholds (ppm): <5 safe, 5-15 moderate, >15 irritant
        "thresholds": {
            "optimal_max": 5.0,
            "moderate_max": 15.0,
            "warning_max": 25.0,
        },
        "default_calibration": {"scale": 1.0, "offset": 0.0},
    },
    "field6": {
        "id": "field6",
        "name": "Nitrogen Oxides",
        "short_name": "NOx",
        "default_unit": "ppm",
        "alt_unit": "ppb",
        "icon": "🏭",
        "precision": 3,
        "description": "Combustion emissions & vehicle exhaust infiltration (WHO guideline)",
        # WHO / EPA indoor thresholds (ppm): <0.05 clean, 0.05-0.10 moderate, >0.10 elevated
        "thresholds": {
            "optimal_max": 0.05,
            "moderate_max": 0.10,
            "warning_max": 0.20,
        },
        "default_calibration": {"scale": 1.0, "offset": 0.0},
    },
    "field7": {
        "id": "field7",
        "name": "Particulate Matter 2.5",
        "short_name": "PM2.5",
        "default_unit": "µg/m³",
        "alt_unit": "µg/m³",
        "icon": "🌫️",
        "precision": 1,
        "description": "Fine respirable particles <= 2.5 micrometers (WHO 24h targets)",
        # WHO / EPA 24h ambient bands: 0-12 Good, 12.1-35.4 Moderate, 35.5-55.4 Unhealthy for Sensitive, >55.5 Poor
        "thresholds": {
            "optimal_max": 12.0,
            "moderate_max": 35.4,
            "warning_max": 55.4,
        },
        "default_calibration": {"scale": 1.0, "offset": 0.0},
    },
}

# Field 8 is explicitly noted as not configured
FIELD_8_NAME = "Not configured"
