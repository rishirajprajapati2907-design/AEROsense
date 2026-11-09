"""
AEROsense ARIMA Time-Series Model
Autoregressive Integrated Moving Average model for univariate sensor forecasting with prediction intervals.
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA


class ARIMAForecaster:
    """Univariate statistical time-series forecaster with confidence bounds."""

    def __init__(self, order: Tuple[int, int, int] = (1, 1, 1)):
        self.order = order
        self.fitted_model = None
        self.is_fitted = False
        self.target_name: str = ""
        self.last_timestamp = None
        self.residual_std: float = 0.0

    def fit(self, series: pd.Series, target_name: str = "") -> "ARIMAForecaster":
        """Fit ARIMA model on a clean univariate time series."""
        clean_s = series.dropna().astype(float)
        if len(clean_s) < 20:
            raise ValueError(f"ARIMA requires at least 20 continuous observations, got {len(clean_s)}.")

        self.target_name = target_name
        model = ARIMA(clean_s, order=self.order)
        self.fitted_model = model.fit()
        self.is_fitted = True

        resid = self.fitted_model.resid
        self.residual_std = float(np.std(resid)) if len(resid) > 0 else 1.0
        return self

    def forecast(self, steps: int = 15, alpha: float = 0.05) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate out-of-sample forecast for `steps` ahead.
        Returns:
            (predictions, lower_bounds, upper_bounds)
        """
        if not self.is_fitted:
            raise RuntimeError("ARIMA model must be fitted before calling forecast().")

        forecast_res = self.fitted_model.get_forecast(steps=steps)
        preds = forecast_res.predicted_mean.to_numpy()
        conf_int = forecast_res.conf_int(alpha=alpha).to_numpy()

        lower = conf_int[:, 0]
        upper = conf_int[:, 1]

        return preds, lower, upper

    def predict_in_sample(self, start: int, end: int) -> np.ndarray:
        """In-sample prediction over specified integer index range."""
        if not self.is_fitted:
            raise RuntimeError("ARIMA model must be fitted before predict_in_sample().")
        preds = self.fitted_model.predict(start=start, end=end)
        return preds.to_numpy()

    def get_model_info(self) -> Dict[str, Any]:
        """Metadata description of the trained ARIMA model."""
        return {
            "model_type": "ARIMA",
            "model_name": f"ARIMA{self.order}",
            "order": self.order,
            "is_fitted": self.is_fitted,
            "target_name": self.target_name,
            "aic": round(float(self.fitted_model.aic), 2) if self.is_fitted else None,
            "bic": round(float(self.fitted_model.bic), 2) if self.is_fitted else None,
            "residual_std": round(self.residual_std, 4) if self.is_fitted else None,
        }
