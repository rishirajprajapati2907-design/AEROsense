"""
AEROsense Model Manager Module
Handles model persistence, version tracking, artifact serialization,
metadata registration, and retraining detection.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import joblib

logger = logging.getLogger(__name__)

DEFAULT_MODELS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "models",
    "saved_models",
)


class ModelManager:
    """Manages serialization, loading, and version registry for trained prediction models."""

    def __init__(self, models_dir: Optional[str] = None):
        self.models_dir = models_dir or DEFAULT_MODELS_DIR
        os.makedirs(self.models_dir, exist_ok=True)

    def _get_model_path(self, sensor_name: str, model_type: str, version: str) -> str:
        safe_sensor = sensor_name.lower().replace(" ", "_")
        safe_type = model_type.lower().replace(" ", "_")
        return os.path.join(self.models_dir, f"{safe_sensor}_{safe_type}_{version}.joblib")

    def _get_meta_path(self, sensor_name: str, model_type: str, version: str) -> str:
        safe_sensor = sensor_name.lower().replace(" ", "_")
        safe_type = model_type.lower().replace(" ", "_")
        return os.path.join(self.models_dir, f"{safe_sensor}_{safe_type}_{version}_meta.json")

    def save_model(
        self,
        model_artifact: Any,
        sensor_name: str,
        model_type: str,
        version: str = "v1.0",
        evaluation_metrics: Optional[Dict[str, Any]] = None,
        feature_names: Optional[List[str]] = None,
        sample_count: int = 0,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Serialize model object to disk along with its JSON evaluation and training metadata.
        """
        model_path = self._get_model_path(sensor_name, model_type, version)
        meta_path = self._get_meta_path(sensor_name, model_type, version)

        # 1. Save model binary
        joblib.dump(model_artifact, model_path)

        # 2. Build metadata dictionary
        metadata = {
            "sensor_name": sensor_name,
            "model_type": model_type,
            "version": version,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "training_samples": sample_count,
            "features": feature_names or [],
            "metrics": evaluation_metrics or {},
            "extra": extra_metadata or {},
        }

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Saved model artifact to {model_path} with metadata {meta_path}")
        return model_path

    def load_model(
        self,
        sensor_name: str,
        model_type: str,
        version: str = "v1.0",
    ) -> Optional[Any]:
        """Load a serialized model artifact from disk."""
        model_path = self._get_model_path(sensor_name, model_type, version)
        if not os.path.exists(model_path):
            logger.warning(f"Model file not found: {model_path}")
            return None
        return joblib.load(model_path)

    def load_metadata(
        self,
        sensor_name: str,
        model_type: str,
        version: str = "v1.0",
    ) -> Optional[Dict[str, Any]]:
        """Load metadata JSON for a trained model."""
        meta_path = self._get_meta_path(sensor_name, model_type, version)
        if not os.path.exists(meta_path):
            return None
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def is_model_available(self, sensor_name: str, model_type: str, version: str = "v1.0") -> bool:
        """Check whether a trained model binary exists."""
        return os.path.exists(self._get_model_path(sensor_name, model_type, version))

    def list_saved_models(self) -> List[Dict[str, Any]]:
        """List all saved models and their metadata."""
        models = []
        if not os.path.exists(self.models_dir):
            return models

        for fname in os.listdir(self.models_dir):
            if fname.endswith("_meta.json"):
                full_path = os.path.join(self.models_dir, fname)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    models.append(meta)
                except Exception as e:
                    logger.debug(f"Could not read metadata file {fname}: {e}")

        return sorted(models, key=lambda x: x.get("saved_at", ""), reverse=True)

    def needs_retraining(
        self,
        sensor_name: str,
        model_type: str,
        version: str = "v1.0",
        max_age_days: int = 30,
    ) -> bool:
        """Determine if a model is missing or exceeds maximum age threshold."""
        meta = self.load_metadata(sensor_name, model_type, version)
        if not meta or not self.is_model_available(sensor_name, model_type, version):
            return True

        saved_at_str = meta.get("saved_at")
        if not saved_at_str:
            return True

        try:
            saved_dt = datetime.fromisoformat(saved_at_str)
            age_days = (datetime.now(timezone.utc) - saved_dt).total_seconds() / 86400.0
            return age_days > max_age_days
        except Exception:
            return True
