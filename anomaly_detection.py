"""
AEROsense AI — Sensor Anomaly & Fault Detection Module
IMPORTANT NOTICE:
This module is a forward-looking architecture scaffold for automated sensor fault detection.
STATUS: EXPERIMENTAL SCAFFOLD (AWAITING FIELD BASELINE CALIBRATION).
DO NOT claim anomaly detection is certified operational until zero-air and span gas calibration
baselines are collected and validated.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from dataclasses import dataclass
from config import SENSOR_FIELDS


@dataclass
class AnomalyReport:
    field_id: str
    parameter_name: str
    is_anomaly: bool
    anomaly_type: Optional[str]   # "Spike", "Frozen/Stuck Sensor", "Out of Physical Bounds", None
    severity: str                 # "Normal", "Warning", "Critical"
    score: float                  # e.g., Z-score or discrepancy index
    details: str
    model_status: str             # "Experimental Heuristic Scaffold"


class SensorAnomalyDetector:
    """
    Architecture scaffold for statistical & machine learning anomaly detection
    (e.g., Rolling Z-score, Isolation Forest, Autoencoder, Mahalanobis Distance).
    """

    IS_OPERATIONAL: bool = False
    STATUS_MESSAGE: str = (
        "EXPERIMENTAL SCAFFOLD: Anomaly heuristics evaluate statistical outliers and frozen sensor "
        "signatures. Full unsupervised models require baseline field calibration."
    )

    def __init__(self, z_threshold: float = 3.0, stuck_window: int = 10):
        self.z_threshold = z_threshold
        self.stuck_window = stuck_window
        self.is_validated = False

    def is_operational(self) -> bool:
        """Returns False until baseline field calibration is verified."""
        return self.is_validated

    def scan_sensor(
        self,
        historical_df: pd.DataFrame,
        field_id: str,
    ) -> AnomalyReport:
        """
        Scan a single sensor channel for potential anomalies using heuristic baselines:
        1. Stuck / Frozen sensor (zero variance over recent window)
        2. Statistical Spikes (Z-score > threshold)
        3. Physical impossible bounds (e.g. negative readings for gas/particulates)
        """
        cfg = SENSOR_FIELDS.get(field_id, {})
        name = cfg.get("name", field_id)

        if historical_df.empty or field_id not in historical_df.columns or historical_df[field_id].dropna().empty:
            return AnomalyReport(
                field_id=field_id,
                parameter_name=name,
                is_anomaly=False,
                anomaly_type=None,
                severity="Normal",
                score=0.0,
                details="Insufficient data buffer to scan for anomalies.",
                model_status="Scaffold - Awaiting Data",
            )

        series = historical_df[field_id].dropna()
        if len(series) < 5:
            return AnomalyReport(
                field_id=field_id,
                parameter_name=name,
                is_anomaly=False,
                anomaly_type=None,
                severity="Normal",
                score=0.0,
                details="Collecting baseline data buffer...",
                model_status="Scaffold - Initializing",
            )

        latest_val = float(series.iloc[-1])

        # Check 1: Negative values on positive-only sensors
        if field_id in ("field2", "field3", "field4", "field5", "field6", "field7") and latest_val < 0:
            return AnomalyReport(
                field_id=field_id,
                parameter_name=name,
                is_anomaly=True,
                anomaly_type="Out of Physical Bounds",
                severity="Critical",
                score=-1.0,
                details=f"Sensor reported negative reading ({latest_val:.2f}), indicating zero-point drift or hardware disconnection.",
                model_status="Scaffold - Rule Based",
            )

        # Check 2: Frozen / Stuck Sensor (identical values across last N readings)
        if len(series) >= self.stuck_window:
            recent_vals = series.iloc[-self.stuck_window:].values
            if np.all(recent_vals == recent_vals[0]):
                return AnomalyReport(
                    field_id=field_id,
                    parameter_name=name,
                    is_anomaly=True,
                    anomaly_type="Frozen/Stuck Sensor",
                    severity="Warning",
                    score=0.0,
                    details=f"Sensor has produced {self.stuck_window} identical readings ({recent_vals[0]:.2f}) without natural ADC noise.",
                    model_status="Scaffold - Variance Check",
                )

        # Check 3: Statistical Spike / Z-score
        mean = float(series.mean())
        std = float(series.std())
        if std > 1e-4:
            z_score = abs(latest_val - mean) / std
            if z_score > self.z_threshold:
                return AnomalyReport(
                    field_id=field_id,
                    parameter_name=name,
                    is_anomaly=True,
                    anomaly_type="Statistical Spike",
                    severity="Warning" if z_score < 4.5 else "Critical",
                    score=round(z_score, 2),
                    details=f"Reading deviates by {z_score:.1f} standard deviations from the rolling mean.",
                    model_status="Scaffold - Z-Score Baseline",
                )

        return AnomalyReport(
            field_id=field_id,
            parameter_name=name,
            is_anomaly=False,
            anomaly_type=None,
            severity="Normal",
            score=0.0,
            details="Sensor operating within expected statistical distribution.",
            model_status="Scaffold - Nominal",
        )

    def scan_all_sensors(self, historical_df: pd.DataFrame) -> List[AnomalyReport]:
        """Run anomaly detection heuristics across all 7 configured sensor fields."""
        reports = []
        for field_id in SENSOR_FIELDS.keys():
            report = self.scan_sensor(historical_df, field_id)
            reports.append(report)
        return reports

    def detect_historical_anomalies(
        self,
        historical_df: pd.DataFrame,
        field_id: str = "field7",
        z_thresh: float = 3.0,
    ) -> pd.DataFrame:
        """
        Scan full historical time-series for statistical outliers and unusual readings.
        Returns a DataFrame of anomalous events with timestamps.
        """
        if historical_df.empty or field_id not in historical_df.columns:
            return pd.DataFrame()

        clean_s = historical_df.dropna(subset=[field_id, "timestamp"]).copy()
        if len(clean_s) < 10:
            return pd.DataFrame()

        vals = clean_s[field_id].values
        mean = float(np.mean(vals))
        std = float(np.std(vals))

        if std < 1e-4:
            clean_s["z_score"] = 0.0
            clean_s["is_anomaly"] = False
            return clean_s[clean_s["is_anomaly"]]

        clean_s["z_score"] = np.abs(vals - mean) / std
        clean_s["is_anomaly"] = clean_s["z_score"] > z_thresh

        cfg = SENSOR_FIELDS.get(field_id, {})
        clean_s["sensor_name"] = cfg.get("name", field_id)
        clean_s["unit"] = cfg.get("default_unit", "")

        anomalies_df = clean_s[clean_s["is_anomaly"]].copy()
        anomalies_df["deviation_z"] = np.round(anomalies_df["z_score"], 2)
        return anomalies_df[["timestamp", "entry_id", field_id, "deviation_z", "sensor_name", "unit"]]
