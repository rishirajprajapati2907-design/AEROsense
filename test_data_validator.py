"""
Unit Tests for Sensor Data Validator
Verifies boundary checks, physical limits, schema validation, and reporting.
"""

import unittest
import pandas as pd
import numpy as np

from services.data_validator import DataValidator, SENSOR_BOUNDS


class TestDataValidator(unittest.TestCase):

    def test_valid_reading_passes(self):
        """Test nominal indoor sensor readings produce zero validation errors."""
        reading = {
            "field1": 22.5,   # Temp
            "field2": 45.0,   # Humidity
            "field3": 120.0,  # Smoke ADC
            "field4": 2.5,    # CO ADC
            "field5": 1.2,    # NH3 ADC
            "field6": 0.03,   # NOx ADC
            "field7": 15.0,   # PM2.5 ADC
        }
        issues = DataValidator.validate_reading(reading)
        errors = [i for i in issues if i.severity == "ERROR"]
        self.assertEqual(len(errors), 0)

    def test_negative_values_detected(self):
        """Test physical sensors that cannot be negative produce ERRORs."""
        bad_reading = {
            "field2": -5.0,  # Relative humidity cannot be negative
            "field3": -10.0, # ADC counts cannot be negative
        }
        issues = DataValidator.validate_reading(bad_reading)
        negs = [i for i in issues if i.issue_type == "NEGATIVE_VALUE"]
        self.assertEqual(len(negs), 2)

    def test_out_of_bounds_detected(self):
        """Test out of bounds values produce warnings."""
        extreme_reading = {
            "field1": 150.0,  # Unrealistic room temperature (150°C)
            "field2": 105.0,  # Humidity > 100%
        }
        issues = DataValidator.validate_reading(extreme_reading)
        oob = [i for i in issues if i.issue_type == "OUT_OF_BOUNDS"]
        self.assertEqual(len(oob), 2)

    def test_hardware_ceiling_saturation_detected(self):
        """Test PM2.5 reading at known saturation ceiling (560.9) produces warning."""
        sat_reading = {"field7": 560.9}
        issues = DataValidator.validate_reading(sat_reading)
        sat = [i for i in issues if i.issue_type == "SATURATED"]
        self.assertEqual(len(sat), 1)

    def test_validate_dataframe_report(self):
        """Test full DataFrame report generation."""
        df = pd.DataFrame({
            "timestamp": pd.date_range("2026-01-01", periods=10, freq="min", tz="UTC"),
            "field1": [20.0 + i for i in range(10)],
            "field2": [40.0 + i for i in range(10)],
            "field3": [100.0] * 10,
            "field4": [2.0] * 10,
            "field5": [1.0] * 10,
            "field6": [0.02] * 10,
            "field7": [15.0] * 10,
        })
        report = DataValidator.validate_dataframe(df)
        self.assertTrue(report.is_valid)
        self.assertEqual(report.total_records, 10)
        self.assertEqual(report.summary["error_count"], 0)


if __name__ == "__main__":
    unittest.main()
