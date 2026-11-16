"""
Unit Tests for Data Transformer
Verifies schema standardization, mapping of ThingSpeak field1-7 to named columns,
and preservation of dual field identifiers.
"""

import unittest
import pandas as pd
import numpy as np

from backend.processing.data_transformer import DataTransformer, STANDARDIZED_COLUMNS, FIELD_TO_STANDARD_MAP


class TestDataTransformer(unittest.TestCase):

    def test_standardize_thingspeak_fields(self):
        """Test field1-7 columns are mapped to standardized semantic names."""
        df = pd.DataFrame({
            "created_at": ["2026-01-01 10:00:00"],
            "field1": [24.5],  # Temperature
            "field2": [50.0],  # Humidity
            "field3": [115.0], # Smoke
            "field4": [2.4],   # Carbon Monoxide
            "field5": [1.1],   # Ammonia
            "field6": [0.03],  # Nitrogen Oxides
            "field7": [16.0],  # PM2.5
        })

        transformed = DataTransformer.transform(df, source_name="test_feed", preserve_field_ids=True)

        for std_col in STANDARDIZED_COLUMNS:
            self.assertIn(std_col, transformed.columns)

        # Check values in standardized columns
        self.assertEqual(transformed["temperature"].iloc[0], 24.5)
        self.assertEqual(transformed["humidity"].iloc[0], 50.0)
        self.assertEqual(transformed["carbon_monoxide"].iloc[0], 2.4)
        self.assertEqual(transformed["nitrogen_oxides"].iloc[0], 0.03)

        # Check raw field ids are also preserved
        self.assertEqual(transformed["field1"].iloc[0], 24.5)
        self.assertEqual(transformed["field4"].iloc[0], 2.4)
        self.assertEqual(transformed["source"].iloc[0], "test_feed")

    def test_handles_alternative_column_aliases(self):
        """Test CSV with headers like 'temp', 'rh', 'co', 'pm2.5' maps cleanly."""
        df = pd.DataFrame({
            "timestamp": ["2026-01-01 10:00:00"],
            "temp": [22.0],
            "rh": [45.0],
            "co": [1.5],
            "pm2.5": [12.0],
        })

        transformed = DataTransformer.transform(df, source_name="csv_file")

        self.assertEqual(transformed["temperature"].iloc[0], 22.0)
        self.assertEqual(transformed["humidity"].iloc[0], 45.0)
        self.assertEqual(transformed["carbon_monoxide"].iloc[0], 1.5)
        self.assertEqual(transformed["pm25"].iloc[0], 12.0)

    def test_empty_dataframe_transform(self):
        """Test empty DataFrame transforms to proper schema structure."""
        df = pd.DataFrame()
        transformed = DataTransformer.transform(df)
        for col in STANDARDIZED_COLUMNS:
            self.assertIn(col, transformed.columns)


if __name__ == "__main__":
    unittest.main()
