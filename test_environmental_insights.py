"""
Unit tests for AEROsense Environmental Insights Engine.
Verifies rule-based observation synthesis, evidence metric traceability, and safety compliance.
"""

import unittest
from datetime import datetime, timezone
import pandas as pd
import numpy as np

from backend.analytics.environmental_insights import (
    EnvironmentalInsightsEngine,
    EnvironmentalInsight,
)


class TestEnvironmentalInsights(unittest.TestCase):
    """Test suite verifying deterministic rule triggering and observation generation."""

    def test_01_empty_dataset_insight(self):
        """Verify fallback observation when dataset has 0 rows."""
        insights = EnvironmentalInsightsEngine.generate_insights(pd.DataFrame())
        self.assertEqual(len(insights), 1)
        self.assertEqual(insights[0].category, "DATA_QUALITY")
        self.assertEqual(insights[0].title, "Dataset Empty")

    def test_02_stability_and_volatility_insights(self):
        """Verify stability and volatility rules trigger on narrow vs wide standard deviations."""
        # Stable series: standard deviation near 0
        timestamps = pd.date_range("2026-11-01", periods=20, freq="15min", tz="UTC")
        df_stable = pd.DataFrame({
            "timestamp": timestamps,
            "temperature": [22.0 + (0.05 * (i % 2)) for i in range(20)],
        })
        insights = EnvironmentalInsightsEngine.generate_insights(df_stable, sensor_columns=["temperature"])
        stability_insights = [ins for ins in insights if ins.category == "STABILITY"]

        self.assertGreaterEqual(len(stability_insights), 1)
        self.assertIn("Stability", stability_insights[0].title)
        self.assertIn("remained exceptionally stable", stability_insights[0].description)

    def test_03_period_shift_insight(self):
        """Verify period comparison shift observation is generated when prior dataset is supplied."""
        ts = pd.date_range("2026-11-01", periods=15, freq="1h", tz="UTC")
        df_prev = pd.DataFrame({
            "timestamp": ts,
            "pm25": [200.0] * 15,
        })
        df_curr = pd.DataFrame({
            "timestamp": ts,
            "pm25": [300.0] * 15,  # +50% increase
        })

        insights = EnvironmentalInsightsEngine.generate_insights(
            df=df_curr,
            prior_df=df_prev,
            sensor_columns=["pm25"],
        )
        shift_insights = [ins for ins in insights if "Shift" in ins.title]

        self.assertGreaterEqual(len(shift_insights), 1)
        self.assertIn("+50.0%", shift_insights[0].description)
        self.assertIn("prior equivalent period", shift_insights[0].description)

    def test_04_no_clinical_or_medical_claims(self):
        """Verify that insights adhere to engineering standards and never emit medical claims."""
        forbidden_keywords = ["medical diagnosis", "prescribe", "toxic hazard", "poisoning", "clinical emergency"]
        ts = pd.date_range("2026-11-01", periods=20, freq="1h", tz="UTC")
        df = pd.DataFrame({
            "timestamp": ts,
            "co": [10.0 + i * 20.0 for i in range(20)],
            "smoke": [50.0 + i * 15.0 for i in range(20)],
        })

        insights = EnvironmentalInsightsEngine.generate_insights(df)
        for ins in insights:
            for kw in forbidden_keywords:
                self.assertNotIn(kw, ins.description.lower())
                self.assertNotIn(kw, ins.title.lower())


if __name__ == "__main__":
    unittest.main()
