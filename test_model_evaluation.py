"""
Unit tests for Model Evaluation and Selection Metrics
"""

import unittest
import numpy as np

from backend.intelligence.prediction.model_evaluation import ModelEvaluator


class TestModelEvaluation(unittest.TestCase):

    def test_calculate_metrics_perfect_predictions(self):
        y_true = np.array([20.0, 22.0, 24.0, 26.0, 28.0])
        y_pred = np.array([20.0, 22.0, 24.0, 26.0, 28.0])

        metrics = ModelEvaluator.calculate_metrics(y_true, y_pred)
        self.assertEqual(metrics["mae"], 0.0)
        self.assertEqual(metrics["rmse"], 0.0)
        self.assertEqual(metrics["r2"], 1.0)
        self.assertEqual(metrics["mape"], 0.0)

    def test_calculate_metrics_known_error(self):
        y_true = np.array([10.0, 20.0, 30.0])
        y_pred = np.array([12.0, 19.0, 31.0])  # errors: +2, -1, +1 => MAE = (2+1+1)/3 = 1.3333

        metrics = ModelEvaluator.calculate_metrics(y_true, y_pred)
        self.assertAlmostEqual(metrics["mae"], 1.3333, places=3)
        self.assertGreater(metrics["rmse"], 0.0)
        self.assertIsNotNone(metrics["r2"])
        self.assertIsNotNone(metrics["mape"])

    def test_mape_none_when_non_positive_values_exist(self):
        y_true = np.array([0.0, 10.0, 20.0])  # contains 0.0
        y_pred = np.array([1.0, 11.0, 21.0])

        metrics = ModelEvaluator.calculate_metrics(y_true, y_pred)
        self.assertIsNone(metrics["mape"])  # Protected from division by zero!

    def test_select_best_model(self):
        evals = {
            "ModelA": {"status": "VALID", "rmse": 1.5, "mae": 1.2, "r2": 0.85},
            "ModelB": {"status": "VALID", "rmse": 0.8, "mae": 0.6, "r2": 0.94},  # Best!
            "ModelC": {"status": "VALID", "rmse": 2.1, "mae": 1.8, "r2": 0.70},
        }

        selection = ModelEvaluator.select_best_model(evals, primary_metric="rmse")
        self.assertEqual(selection["best_model"], "ModelB")
        self.assertEqual(selection["best_metrics"]["rmse"], 0.8)


if __name__ == "__main__":
    unittest.main()
