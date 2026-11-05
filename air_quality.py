"""
AEROsense Air Quality Classification Module
Provides preliminary indoor air-quality assessment based on scientifically validated thresholds.
Adheres strictly to the requirement: Does NOT invent an official AQI number.
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from config import SENSOR_FIELDS


@dataclass
class ParameterEvaluation:
    field_id: str
    name: str
    short_name: str
    value: Optional[float]
    unit: str
    status: str              # "Optimal", "Moderate", "Elevated", "Hazardous", "Unknown"
    status_color: str        # Hex color
    severity_rank: int       # 0: Optimal, 1: Moderate, 2: Elevated, 3: Hazardous, -1: Unknown
    message: str


@dataclass
class AirAssessment:
    overall_status: str       # "Optimal / Clean", "Moderate / Acceptable", "Elevated Caution", "Poor / Hazardous", "Insufficient Data"
    overall_color: str
    dominant_concern: Optional[str]
    dominant_field: Optional[str]
    evaluations: List[ParameterEvaluation]
    recommendation: str
    safe_count: int
    elevated_count: int
    missing_count: int
    disclaimer: str


def evaluate_parameter(
    field_id: str,
    raw_value: Optional[float],
    calibration: Optional[Dict[str, float]] = None,
    unit_override: Optional[str] = None,
) -> ParameterEvaluation:
    """Evaluate a single sensor field against validated threshold ranges."""
    cfg = SENSOR_FIELDS.get(field_id, {})
    name = cfg.get("name", field_id)
    short_name = cfg.get("short_name", field_id)
    unit = unit_override or cfg.get("default_unit", "")
    thresholds = cfg.get("thresholds", {})

    if raw_value is None:
        return ParameterEvaluation(
            field_id=field_id,
            name=name,
            short_name=short_name,
            value=None,
            unit=unit,
            status="No Data",
            status_color="#64748B",
            severity_rank=-1,
            message="No sensor reading transmitted",
        )

    # Apply calibration scaling/offset if provided
    cal = calibration or cfg.get("default_calibration", {"scale": 1.0, "offset": 0.0})
    val = (raw_value * cal.get("scale", 1.0)) + cal.get("offset", 0.0)

    # Specific threshold logic per parameter
    if field_id == "field1":  # Temperature (°C)
        opt_min, opt_max = thresholds.get("optimal_min", 20.0), thresholds.get("optimal_max", 24.5)
        mod_min, mod_max = thresholds.get("moderate_min", 18.0), thresholds.get("moderate_max", 27.0)

        if opt_min <= val <= opt_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Comfortable", "#10B981", 0, "Ideal thermal comfort band (20–24.5°C)")
        elif mod_min <= val <= mod_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Acceptable", "#F59E0B", 1, "Slightly outside optimal comfort range")
        else:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Uncomfortable", "#EF4444", 2, "Thermal discomfort (too cold or warm)")

    elif field_id == "field2":  # Humidity (%)
        opt_min, opt_max = thresholds.get("optimal_min", 35.0), thresholds.get("optimal_max", 50.0)
        mod_min, mod_max = thresholds.get("moderate_min", 30.0), thresholds.get("moderate_max", 60.0)

        if opt_min <= val <= opt_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Optimal", "#10B981", 0, "Healthy indoor humidity (35–50%)")
        elif mod_min <= val <= mod_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Acceptable", "#F59E0B", 1, "Acceptable humidity band (30–60%)")
        elif val > mod_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "High Humidity", "#EF4444", 2, "High moisture: elevated mold/allergen risk (>60%)")
        else:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Low Humidity", "#EF4444", 2, "Dry air: potential airway/skin irritation (<30%)")

    elif field_id == "field3":  # Smoke
        opt_max = thresholds.get("optimal_max", 40.0)
        mod_max = thresholds.get("moderate_max", 90.0)
        warn_max = thresholds.get("warning_max", 180.0)

        if val <= opt_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Normal", "#10B981", 0, "Clean ambient baseline")
        elif val <= mod_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Elevated", "#F59E0B", 1, "Trace smoke or aerosol detected")
        elif val <= warn_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Warning", "#F97316", 2, "Notable combustion byproducts detected")
        else:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Hazardous", "#EF4444", 3, "High smoke density! Potential fire hazard")

    elif field_id == "field4":  # Carbon Monoxide (CO)
        opt_max = thresholds.get("optimal_max", 9.0)
        mod_max = thresholds.get("moderate_max", 25.0)
        warn_max = thresholds.get("warning_max", 50.0)

        if val <= opt_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Safe", "#10B981", 0, "Normal indoor level (<9 ppm)")
        elif val <= mod_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Elevated", "#F59E0B", 1, "Elevated CO (9–25 ppm) - Inspect ventilation")
        elif val <= warn_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "High Concern", "#F97316", 2, "High CO (25–50 ppm) - Evacuate sensitive individuals")
        else:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Dangerous", "#EF4444", 3, "OSHA Action Limit Exceeded (>50 ppm)! Ventilate immediately")

    elif field_id == "field5":  # Ammonia (NH3)
        opt_max = thresholds.get("optimal_max", 5.0)
        mod_max = thresholds.get("moderate_max", 15.0)
        warn_max = thresholds.get("warning_max", 25.0)

        if val <= opt_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Safe", "#10B981", 0, "Baseline ambient (<5 ppm)")
        elif val <= mod_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Moderate", "#F59E0B", 1, "Noticeable odor / mild respiratory irritant (5–15 ppm)")
        elif val <= warn_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Elevated", "#F97316", 2, "Pungent NH3 levels (15–25 ppm)")
        else:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Hazardous", "#EF4444", 3, "Severe airway irritant (>25 ppm)")

    elif field_id == "field6":  # Nitrogen Oxides (NOx)
        opt_max = thresholds.get("optimal_max", 0.05)
        mod_max = thresholds.get("moderate_max", 0.10)
        warn_max = thresholds.get("warning_max", 0.20)

        if val <= opt_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Clean", "#10B981", 0, "Well within WHO clean indoor target (<0.05 ppm)")
        elif val <= mod_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Moderate", "#F59E0B", 1, "Moderate combustion emission (0.05–0.10 ppm)")
        elif val <= warn_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Elevated", "#F97316", 2, "Elevated NOx (0.10–0.20 ppm) - Infiltration likely")
        else:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Unhealthy", "#EF4444", 3, "High NOx (>0.20 ppm) - Significant combustion source")

    elif field_id == "field7":  # PM2.5
        opt_max = thresholds.get("optimal_max", 12.0)
        mod_max = thresholds.get("moderate_max", 35.4)
        warn_max = thresholds.get("warning_max", 55.4)

        if val <= opt_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Good", "#10B981", 0, "Meets WHO 24-hr guideline (<= 12 µg/m³)")
        elif val <= mod_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Moderate", "#F59E0B", 1, "Moderate fine dust (12.1–35.4 µg/m³)")
        elif val <= warn_max:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Sensitive Risk", "#F97316", 2, "Unhealthy for sensitive groups (35.5–55.4 µg/m³)")
        else:
            return ParameterEvaluation(field_id, name, short_name, val, unit, "Unhealthy", "#EF4444", 3, "High respirable particulate level (>55.4 µg/m³)")

    # Fallback default
    return ParameterEvaluation(field_id, name, short_name, val, unit, "Normal", "#10B981", 0, "Within normal operational bounds")


def assess_overall_air_quality(
    values: Dict[str, Optional[float]],
    calibrations: Optional[Dict[str, Dict[str, float]]] = None,
) -> AirAssessment:
    """
    Computes preliminary multi-pollutant indoor air assessment based on recognized thresholds.
    Complies with constraint: Does NOT invent an arbitrary official AQI number.
    """
    evaluations: List[ParameterEvaluation] = []
    max_severity = -1
    dominant_param: Optional[ParameterEvaluation] = None

    safe_count = 0
    elevated_count = 0
    missing_count = 0

    for field_id in SENSOR_FIELDS.keys():
        val = values.get(field_id)
        cal = (calibrations or {}).get(field_id)
        evaluation = evaluate_parameter(field_id, val, calibration=cal)
        evaluations.append(evaluation)

        if evaluation.severity_rank == -1:
            missing_count += 1
        elif evaluation.severity_rank == 0:
            safe_count += 1
        else:
            elevated_count += 1

        if evaluation.severity_rank > max_severity:
            max_severity = evaluation.severity_rank
            dominant_param = evaluation

    if missing_count == len(SENSOR_FIELDS):
        return AirAssessment(
            overall_status="No Sensor Data Available",
            overall_color="#64748B",
            dominant_concern=None,
            dominant_field=None,
            evaluations=evaluations,
            recommendation="Awaiting initial telemetry feed from ThingSpeak channel.",
            safe_count=0,
            elevated_count=0,
            missing_count=missing_count,
            disclaimer="Status cannot be calculated until active sensor telemetry is received.",
        )

    if max_severity >= 3:
        status = "Hazardous / Immediate Action Required"
        color = "#EF4444"
        rec = f"Critical levels detected on {dominant_param.name if dominant_param else 'primary sensor'}. Ventilate indoor space immediately and identify emissions source."
    elif max_severity == 2:
        status = "Elevated / Air Quality Caution"
        color = "#F97316"
        rec = f"{dominant_param.name if dominant_param else 'Pollutant'} is elevated. Increase air circulation, activate HEPA filtration, or open windows if outdoor air is clean."
    elif max_severity == 1:
        status = "Moderate / Acceptable"
        color = "#F59E0B"
        rec = "Ambient air quality is acceptable for most occupants. Sensitive individuals may note slight irritation."
    else:
        status = "Optimal / Healthy Indoor Air"
        color = "#10B981"
        rec = "All 7 active sensor parameters are within scientifically recognized indoor comfort and safety baselines."

    return AirAssessment(
        overall_status=status,
        overall_color=color,
        dominant_concern=f"{dominant_param.name} ({dominant_param.value:.1f} {dominant_param.unit})" if (dominant_param and dominant_param.severity_rank > 0 and dominant_param.value is not None) else None,
        dominant_field=dominant_param.field_id if (dominant_param and dominant_param.severity_rank > 0) else None,
        evaluations=evaluations,
        recommendation=rec,
        safe_count=safe_count,
        elevated_count=elevated_count,
        missing_count=missing_count,
        disclaimer="Preliminary assessment based on validated WHO, EPA, and OSHA indoor threshold guidelines. Informational only — does NOT replace certified statutory AQI reporting.",
    )
