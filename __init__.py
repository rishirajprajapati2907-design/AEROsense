"""
AEROsense AI Modules
Contains future predictive modeling and sensor anomaly detection scaffolds.
NOTE: These modules are non-operational scaffolding awaiting training and field validation.
"""

from .prediction import AQIPredictor
from .anomaly_detection import SensorAnomalyDetector

__all__ = ["AQIPredictor", "SensorAnomalyDetector"]
