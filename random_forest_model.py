"""
AEROsense Random Forest Regression Model
Non-linear decision tree ensemble capturing complex diurnal and lag interactions.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


class RandomForestForecaster:
    """Non-linear ensemble regressor for indoor environmental parameter forecasting."""

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: Optional[int] = 12,
        min_samples_split: int = 5,
        min_samples_leaf: int = 2,
        random_state: int = 42,
    ):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.random_state = random_state
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
            n_jobs=-1,
        )
        self.is_fitted = False
        self.feature_names: List[str] = []
        self.target_name: str = ""

    def fit(self, X: pd.DataFrame, y: pd.Series, target_name: str = "") -> "RandomForestForecaster":
        """Fit random forest regressor on feature matrix."""
        self.feature_names = list(X.columns)
        self.target_name = target_name
        self.model.fit(X, y)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Generate forecasts from feature matrix."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before calling predict().")
        preds = self.model.predict(X[self.feature_names])
        return np.array(preds)

    def get_feature_importances(self) -> Dict[str, float]:
        """Return Gini impurity feature importances."""
        if not self.is_fitted:
            return {}
        importances = self.model.feature_importances_
        return {
            feat: round(float(imp), 4)
            for feat, imp in sorted(
                zip(self.feature_names, importances),
                key=lambda x: x[1],
                reverse=True,
            )
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Metadata description of the trained Random Forest model."""
        return {
            "model_type": "RandomForest",
            "model_name": "Random Forest Regressor",
            "is_fitted": self.is_fitted,
            "target_name": self.target_name,
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
            "features_count": len(self.feature_names),
            "top_features": list(self.get_feature_importances().items())[:5],
        }
