"""
Unit tests for AEROsense Correlation Analysis Module.
Verifies Pearson (linear) and Spearman (rank-order monotonic) matrices,
disclaimers, and heatmap payload structures.
"""

import unittest
import numpy as np
import pandas as pd

from backend.analytics.correlation_analysis import (
    compute_correlation_matrix,
    format_heatmap_payload,
    CorrelationResult,
)


class TestCorrelationAnalysis(unittest.TestCase):
    """Test suite verifying Pearson and Spearman correlation logic and scientific constraints."""

    def test_01_perfect_linear_correlation(self):
        """Verify Pearson correlation = 1.0 for strictly proportional variables."""
        df = pd.DataFrame({
            "temp": [10.0, 20.0, 30.0, 40.0, 50.0],
            "humidity": [20.0, 40.0, 60.0, 80.0, 100.0],
        })
        res = compute_correlation_matrix(df, method="pearson")

        self.assertEqual(res.method, "pearson")
        self.assertEqual(len(res.correlation_matrix), 2)
        # Diagonal is 1.0
        self.assertAlmostEqual(res.correlation_matrix[0][0], 1.0, places=2)
        self.assertAlmostEqual(res.correlation_matrix[1][1], 1.0, places=2)
        # Off-diagonal is 1.0
        self.assertAlmostEqual(res.correlation_matrix[0][1], 1.0, places=2)
        self.assertIn("does not establish a causal", res.disclaimer)

    def test_02_monotonic_non_linear_spearman(self):
        """Verify Spearman rank correlation captures monotonic non-linear relationships (e.g. exponential)."""
        x = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        y = [np.exp(val) for val in x]
        df = pd.DataFrame({"x": x, "y": y})

        pearson_res = compute_correlation_matrix(df, method="pearson")
        spearman_res = compute_correlation_matrix(df, method="spearman")

        # Spearman rank correlation should be exactly 1.0 for monotonic growth
        self.assertAlmostEqual(spearman_res.correlation_matrix[0][1], 1.0, places=2)
        # Pearson is less than 1.0 due to exponential curvature
        self.assertLess(pearson_res.correlation_matrix[0][1], 1.0)

    def test_03_heatmap_payload_formatting(self):
        """Verify Plotly heatmap-ready structure."""
        df = pd.DataFrame({
            "field1": [1.0, 2.0, 3.0, 4.0, 5.0],
            "field2": [5.0, 4.0, 3.0, 2.0, 1.0],
        })
        res = compute_correlation_matrix(df, method="pearson")
        payload = format_heatmap_payload(res, label_map={"field1": "Temperature", "field2": "Humidity"})

        self.assertIn("x", payload)
        self.assertIn("y", payload)
        self.assertIn("z", payload)
        self.assertIn("text", payload)
        self.assertEqual(payload["x"], ["Temperature", "Humidity"])
        self.assertAlmostEqual(payload["z"][0][1], -1.0, places=2)


if __name__ == "__main__":
    unittest.main()
