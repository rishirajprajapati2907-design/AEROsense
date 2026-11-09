"""
AEROsense Linear Regression Baseline Model
Standardized linear regression baseline for indoor air quality parameter forecasting.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler


class LinearRegressionForecaster:
    """Linear regression baseline model with standard feature normalization."""

    def __init__(self, fit_intercept: bool = True):
        self.fit_intercept = fit_intercept
        self.model = LinearRegression(fit_intercept=fit_intercept)
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.feature_names: List[str] = []
        self.target_name: str = ""

    def fit(self, X: pd.DataFrame, y: pd.Series, target_name: str = "") -> "LinearRegressionForecaster":
        """Fit scaler and linear regressor on training data."""
        self.feature_names = list(X.columns)
        self.target_name = target_name

        # Standardize features (scale strictly fit on training data)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Generate forecasts from feature matrix."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before calling predict().")

        # Transform features using training scaler
        X_scaled = self.scaler.transform(X[self.feature_names])
        preds = self.model.predict(X_scaled)
        return np.array(preds)

    def get_coefficients(self) -> Dict[str, float]:
        """Return standardized model coefficients per feature."""
        if not self.is_fitted:
            return {}
        return {
            feat: round(float(coef), 4)
            for feat, coef in zip(self.feature_names, self.model.coef_)
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Metadata description of the trained model."""
        return {
            "model_type": "LinearRegression",
            "model_name": "Standardized Linear Regression Baseline",
            "is_fitted": self.is_fitted,
            "target_name": self.target_name,
            "features_count": len(self.feature_names),
            "intercept": round(float(self.model.intercept_), 4) if self.is_fitted else None,
            "top_features": sorted(
                self.get_coefficients().items(), key=lambda x: abs(x[1]), reverse=True
            )[:5],
        }
