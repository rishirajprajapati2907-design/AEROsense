"""
AEROsense AI — Pollutant & Air Trend Prediction Module
IMPORTANT NOTICE:
This module is a forward-looking architecture scaffold for future predictive modeling.
STATUS: UNTRAINED & UNVALIDATED.
DO NOT claim predictions are operational or clinically reliable until trained against
sufficient time-series training sets and validated against reference monitors.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dataclasses import dataclass


@dataclass
class PredictionResult:
    parameter: str
    horizon_minutes: int
    predicted_value: Optional[float]
    confidence_interval: Optional[tuple]  # (lower, upper)
    model_status: str                     # "Scaffold - Untrained"
    disclaimer: str


class AQIPredictor:
    """
    Architecture scaffold for future Machine Learning / Deep Learning time-series forecasting
    (e.g., LSTM, Prophet, LightGBM, or ARIMA).
    """

    IS_OPERATIONAL: bool = False
    STATUS_MESSAGE: str = (
        "SCAFFOLDING ONLY: Model is awaiting training and cross-validation against "
        "continuous field-collected sensor data. Projections shown are purely heuristic baselines."
    )

    def __init__(self, model_name: str = "AEROsense-TS-Forecaster-v0.1"):
        self.model_name = model_name
        self.is_trained = False
        self.training_samples_count = 0
        self.last_trained_at: Optional[datetime] = None

    def get_readiness_status(self, sample_count: int) -> Dict[str, Any]:
        """Check requirements needed before training this predictive model."""
        MIN_REQUIRED_SAMPLES = 5000  # Approx. 3-4 days of continuous 1-minute feeds
        return {
            "is_operational": self.is_operational(),
            "status_label": "Untrained Scaffolding",
            "current_samples": sample_count,
            "min_required_samples": MIN_REQUIRED_SAMPLES,
            "readiness_percentage": min(100.0, round((sample_count / MIN_REQUIRED_SAMPLES) * 100, 1)),
            "requirements": [
                "Continuous 15-second to 1-minute telemetry collection (>5,000 samples)",
                "Outdoor reference station baseline calibration",
                "Cross-validation against seasonal and diurnal shifts",
                "Hyperparameter tuning for regression/LSTM model",
            ],
            "disclaimer": self.STATUS_MESSAGE,
        }

    def is_operational(self) -> bool:
        """Returns False until explicitly trained and validated."""
        return self.is_trained

    def train(self, historical_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Placeholder for future training pipeline.
        Will fit ML time-series models on historical sensor features.
        """
        if historical_df.empty or len(historical_df) < 100:
            return {
                "success": False,
                "message": "Insufficient data points to initiate training pipeline (minimum 100 required for dry run).",
            }

        # Simulated training interface
        self.training_samples_count = len(historical_df)
        self.last_trained_at = datetime.now()
        # Still non-operational until formal validation
        self.is_trained = False

        return {
            "success": True,
            "message": "Training pipeline scaffold executed. Model remains tagged as unvalidated until ground-truth validation is confirmed.",
            "samples_used": self.training_samples_count,
            "status": "Untrained Scaffolding",
        }

    def project_trend(
        self,
        historical_df: pd.DataFrame,
        field_id: str,
        horizon_minutes: int = 60,
    ) -> PredictionResult:
        """
        Provide a non-operational heuristic baseline extrapolation for UI layout demonstration.
        Clearly marked as unvalidated scaffolding.
        """
        if historical_df.empty or field_id not in historical_df.columns or historical_df[field_id].dropna().empty:
            return PredictionResult(
                parameter=field_id,
                horizon_minutes=horizon_minutes,
                predicted_value=None,
                confidence_interval=None,
                model_status="Scaffold - No Data",
                disclaimer=self.STATUS_MESSAGE,
            )

        series = historical_df[field_id].dropna().values
        recent_window = series[-15:] if len(series) >= 15 else series
        last_val = float(series[-1])

        # Simple linear slope for demonstration of interface (NOT an operational AI forecast)
        if len(recent_window) > 2:
            x = np.arange(len(recent_window))
            slope, intercept = np.polyfit(x, recent_window, 1)
            delta_steps = horizon_minutes / 1.0  # approximate
            heuristic_projection = max(0.0, float(last_val + slope * min(delta_steps, 10)))
        else:
            heuristic_projection = last_val

        ci_margin = heuristic_projection * 0.15

        return PredictionResult(
            parameter=field_id,
            horizon_minutes=horizon_minutes,
            predicted_value=round(heuristic_projection, 2),
            confidence_interval=(
                round(max(0.0, heuristic_projection - ci_margin), 2),
                round(heuristic_projection + ci_margin, 2),
            ),
            model_status="Scaffold - Untrained Baseline",
            disclaimer=self.STATUS_MESSAGE,
        )

    def evaluate_baseline_metrics(
        self,
        historical_df: pd.DataFrame,
        field_id: str = "field7",
    ) -> Dict[str, Any]:
        """
        Evaluate baseline time-series extrapolation on actual historical records.
        Calculates MAE, RMSE, and R2 on an 80/20 holdout split.
        Clearly tagged as experimental baseline metrics.
        """
        if historical_df.empty or field_id not in historical_df.columns:
            return {
                "available": False,
                "message": "Insufficient historical data for metric evaluation.",
            }

        series = historical_df[field_id].dropna().values
        if len(series) < 100:
            return {
                "available": False,
                "message": f"Need at least 100 readings (currently {len(series)}).",
            }

        # 80/20 train/test split
        split_idx = int(len(series) * 0.8)
        train_vals = series[:split_idx]
        test_vals = series[split_idx:]

        # Baseline autoregressive / lag-1 persistence model
        y_true = test_vals[1:]
        y_pred = test_vals[:-1]

        mae = float(np.mean(np.abs(y_true - y_pred)))
        rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

        ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
        ss_res = float(np.sum((y_true - y_pred) ** 2))
        r2 = max(0.0, 1.0 - (ss_res / ss_tot)) if ss_tot > 1e-6 else 0.0

        return {
            "available": True,
            "field_id": field_id,
            "samples_evaluated": len(y_true),
            "mae": round(mae, 3),
            "rmse": round(rmse, 3),
            "r2": round(r2, 3),
            "model_type": "Autoregressive Lag-1 Persistence Baseline",
            "validation_status": "Preliminary Holdout Evaluation (Unvalidated Scaffold)",
            "disclaimer": "Metrics calculated on historical holdout split. Field calibration against reference monitors required before operational deployment.",
        }
