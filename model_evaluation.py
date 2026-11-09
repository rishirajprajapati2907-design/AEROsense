"""
AEROsense Model Evaluation Module
Calculates standard time-series regression metrics (MAE, RMSE, R², MAPE)
and compares candidate models to select the optimal forecaster.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class ModelEvaluator:
    """Computes rigorous validation metrics and performs competitive model selection."""

    @staticmethod
    def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
        """
        Compute standard regression error metrics.
        - MAE: Mean Absolute Error
        - RMSE: Root Mean Squared Error
        - R2: Coefficient of Determination
        - MAPE: Mean Absolute Percentage Error (only if all y_true > 0)
        """
        y_t = np.asarray(y_true, dtype=float)
        y_p = np.asarray(y_pred, dtype=float)

        # Drop any pairs with NaNs
        mask = (~np.isnan(y_t)) & (~np.isnan(y_p))
        if mask.sum() < 2:
            return {
                "sample_size": int(mask.sum()),
                "mae": None,
                "rmse": None,
                "r2": None,
                "mape": None,
                "status": "Insufficient valid observations",
            }

        y_t_clean = y_t[mask]
        y_p_clean = y_p[mask]

        mae = float(mean_absolute_error(y_t_clean, y_p_clean))
        rmse = float(np.sqrt(mean_squared_error(y_t_clean, y_p_clean)))

        # R2 score
        var_true = float(np.var(y_t_clean))
        if var_true > 1e-6:
            r2 = float(r2_score(y_t_clean, y_p_clean))
        else:
            r2 = 0.0

        # MAPE calculation — only mathematically valid when all targets > 0
        if (y_t_clean > 1e-3).all():
            mape = float(np.mean(np.abs((y_t_clean - y_p_clean) / y_t_clean)) * 100.0)
        else:
            mape = None

        return {
            "sample_size": int(len(y_t_clean)),
            "mae": round(mae, 4),
            "rmse": round(rmse, 4),
            "r2": round(r2, 4),
            "mape": round(mape, 2) if mape is not None else None,
            "status": "VALID",
        }

    @staticmethod
    def select_best_model(models_eval: Dict[str, Dict[str, Any]], primary_metric: str = "rmse") -> Dict[str, Any]:
        """
        Compare evaluated candidate models and select the best performer.
        Primary metric: 'rmse' (lowest wins) or 'r2' (highest wins).
        """
        valid_candidates = {}
        for name, metrics in models_eval.items():
            if metrics.get("status") == "VALID" and metrics.get(primary_metric) is not None:
                valid_candidates[name] = metrics

        if not valid_candidates:
            return {"best_model": None, "comparison": models_eval, "reason": "No valid model evaluations."}

        if primary_metric in ("rmse", "mae"):
            best_name = min(valid_candidates.keys(), key=lambda k: valid_candidates[k][primary_metric])
        else:
            best_name = max(valid_candidates.keys(), key=lambda k: valid_candidates[k][primary_metric])

        return {
            "best_model": best_name,
            "best_metrics": valid_candidates[best_name],
            "comparison": models_eval,
            "primary_metric": primary_metric,
        }
