"""
AEROsense Future Forecasting Engine
Generates multi-horizon forecasts, prediction intervals, and data-driven explanations.
"""

from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from backend.intelligence.prediction.feature_engineering import TimeSeriesFeatureEngineer


class ForecastHorizon:
    M15 = 15     # 15 minutes (~15 samples at 1-min cadence)
    M30 = 30     # 30 minutes
    H1 = 60      # 1 hour
    H6 = 360     # 6 hours

    HORIZON_MAP = {
        "15m": 15,
        "30m": 30,
        "1h": 60,
        "6h": 360,
    }


class Forecaster:
    """Multi-horizon sensor value forecasting orchestrator."""

    @staticmethod
    def generate_future_timestamps(
        last_timestamp: Union[str, datetime, pd.Timestamp],
        steps: int,
        step_interval_seconds: int = 60,
    ) -> List[datetime]:
        """Generate sequence of future timestamps based on nominal sampling interval."""
        if isinstance(last_timestamp, str):
            base_t = pd.to_datetime(last_timestamp, utc=True).to_pydatetime()
        elif hasattr(last_timestamp, "to_pydatetime"):
            base_t = last_timestamp.to_pydatetime()
        else:
            base_t = last_timestamp

        return [
            base_t + timedelta(seconds=(i + 1) * step_interval_seconds)
            for i in range(steps)
        ]

    @staticmethod
    def forecast_recursive(
        model_wrapper: Any,
        recent_df: pd.DataFrame,
        target_col: str,
        steps: int = 15,
        val_rmse: Optional[float] = None,
        step_interval_seconds: int = 60,
    ) -> Dict[str, Any]:
        """
        Generate recursive multi-step forecast using a fitted regression model.
        In each step, uses latest predicted values to update autoregressive lags.
        """
        if recent_df.empty or target_col not in recent_df.columns:
            return {"success": False, "error": "Insufficient recent data for forecasting."}

        # Need at least 20 historical points to construct lags
        if len(recent_df) < 20:
            return {"success": False, "error": f"Need at least 20 recent rows, got {len(recent_df)}."}

        last_ts = recent_df["timestamp"].iloc[-1]
        future_timestamps = Forecaster.generate_future_timestamps(
            last_timestamp=last_ts,
            steps=steps,
            step_interval_seconds=step_interval_seconds,
        )

        sim_df = recent_df[["timestamp", target_col]].copy()
        predictions: List[float] = []
        lower_bounds: List[float] = []
        upper_bounds: List[float] = []

        base_error = val_rmse if (val_rmse is not None and val_rmse > 0) else (sim_df[target_col].std() * 0.1)

        for step_idx in range(steps):
            f_ts = future_timestamps[step_idx]

            # Build feature vector for current state
            # Create a single row at end with timestamp f_ts
            time_feat = TimeSeriesFeatureEngineer.extract_time_features(
                pd.DataFrame({"timestamp": [f_ts]})
            )

            feat_dict = {}
            for col in time_feat.columns:
                feat_dict[col] = time_feat[col].iloc[0]

            # Autoregressive lags from sim_df
            for lag in TimeSeriesFeatureEngineer.DEFAULT_LAGS:
                if len(sim_df) >= lag:
                    feat_dict[f"{target_col}_lag_{lag}"] = sim_df[target_col].iloc[-lag]
                else:
                    feat_dict[f"{target_col}_lag_{lag}"] = sim_df[target_col].iloc[0]

            # Rolling stats over recent window
            for w in TimeSeriesFeatureEngineer.DEFAULT_ROLLING:
                sub_w = sim_df[target_col].iloc[-w:] if len(sim_df) >= w else sim_df[target_col]
                feat_dict[f"{target_col}_roll_mean_{w}"] = sub_w.mean()
                feat_dict[f"{target_col}_roll_std_{w}"] = sub_w.std() if len(sub_w) > 1 else 0.0

            # Momentum
            m1 = sim_df[target_col].iloc[-1]
            m2 = sim_df[target_col].iloc[-2] if len(sim_df) >= 2 else m1
            m5 = sim_df[target_col].iloc[-5] if len(sim_df) >= 5 else m1
            feat_dict[f"{target_col}_momentum_1_2"] = m1 - m2
            feat_dict[f"{target_col}_momentum_1_5"] = m1 - m5

            # Assemble DataFrame
            X_step = pd.DataFrame([feat_dict])

            # Predict
            pred_val = float(model_wrapper.predict(X_step)[0])
            predictions.append(round(pred_val, 2))

            # Uncertainty expands with forecast horizon sqrt(step)
            step_error = base_error * np.sqrt(1.0 + 0.1 * step_idx)
            lower_bounds.append(round(pred_val - 1.96 * step_error, 2))
            upper_bounds.append(round(pred_val + 1.96 * step_error, 2))

            # Append prediction to sim_df for recursive next step
            new_row = pd.DataFrame({"timestamp": [f_ts], target_col: [pred_val]})
            sim_df = pd.concat([sim_df, new_row], ignore_index=True)

        # Generate scientific explanation
        latest_val = float(recent_df[target_col].iloc[-1])
        final_val = predictions[-1]
        delta = final_val - latest_val

        explanation = Forecaster.explain_forecast(
            sensor_name=target_col,
            initial_val=latest_val,
            final_val=final_val,
            horizon_steps=steps,
            step_interval_seconds=step_interval_seconds,
            uncertainty_width=(upper_bounds[-1] - lower_bounds[-1]),
        )

        return {
            "success": True,
            "target_col": target_col,
            "steps": steps,
            "timestamps": [t.isoformat() for t in future_timestamps],
            "predictions": predictions,
            "confidence_lower": lower_bounds,
            "confidence_upper": upper_bounds,
            "explanation": explanation,
            "latest_actual": round(latest_val, 2),
            "final_predicted": round(final_val, 2),
            "projected_delta": round(delta, 2),
        }

    @staticmethod
    def explain_forecast(
        sensor_name: str,
        initial_val: float,
        final_val: float,
        horizon_steps: int,
        step_interval_seconds: int,
        uncertainty_width: float,
    ) -> str:
        """Generate factual, data-driven explanation of predicted trajectory."""
        duration_min = round(horizon_steps * step_interval_seconds / 60)
        delta = final_val - initial_val
        rel_change_pct = (delta / initial_val * 100) if abs(initial_val) > 1e-4 else 0.0

        clean_sensor = sensor_name.replace("_", " ").title()

        if abs(delta) < 0.2:
            trajectory = f"{clean_sensor} is projected to remain steady (stable within ±0.2 units) over the next {duration_min} minutes."
        elif delta > 0:
            trajectory = f"{clean_sensor} is projected to increase by +{delta:.2f} ({rel_change_pct:+.1f}%) over the next {duration_min} minutes."
        else:
            trajectory = f"{clean_sensor} is projected to decrease by {delta:.2f} ({rel_change_pct:+.1f}%) over the next {duration_min} minutes."

        uncertainty_note = f"Forecast 95% confidence band is ±{uncertainty_width/2.0:.2f} based on validation residual variance."
        return f"{trajectory} {uncertainty_note}"
