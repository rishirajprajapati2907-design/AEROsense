"""
Scratch script to run Phase 7 training and competitive evaluation across all sensors in aerosense.db
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.prediction_service import PredictionService
import pprint
import time

service = PredictionService()
print("Starting full sensor training and competitive model evaluation...")

t0 = time.time()
results = service.train_all_supported_sensors()
elapsed = time.time() - t0

print(f"\nCompleted training & evaluation in {elapsed:.2f} seconds.")
print("\n" + "="*80)
print("SENSOR EVALUATION SUMMARY")
print("="*80)

for sensor, res in results.items():
    print(f"\n>>> SENSOR: {sensor.upper()} <<<")
    if not res.get("success"):
        print(f"  Status: INSUFFICIENT DATA / FAILED")
        print(f"  Reason: {res.get('reason')}")
        continue

    print(f"  Status: SUFFICIENT ({res['train_samples']} train, {res['val_samples']} val, {res['test_samples']} test samples)")
    print(f"  Best Selected Model: {res['best_model']} (RMSE: {res['best_metrics']['rmse']}, R2: {res['best_metrics']['r2']})")
    print("  Candidate Models Evaluation:")
    for model_name, metrics in res["model_evaluations"].items():
        if metrics.get("status") == "VALID":
            print(f"    - {model_name:18}: MAE={metrics['mae']:<8} RMSE={metrics['rmse']:<8} R2={metrics['r2']:<8} MAPE={metrics.get('mape')}")
        else:
            print(f"    - {model_name:18}: {metrics.get('error', 'FAILED')}")

print("\n" + "="*80)
print("TESTING FORECAST GENERATION & PERSISTENCE")
print("="*80)

forecast_1h = service.generate_forecast("temperature", horizon="1h", persist=True)
print(f"Temperature 1-Hour Forecast Generated: {len(forecast_1h['predictions'])} points.")
print(f"Latest Actual: {forecast_1h['latest_actual']} °C -> Projected Final: {forecast_1h['final_predicted']} °C (Δ={forecast_1h['projected_delta']:+0.2f})")
print(f"Explanation: {forecast_1h['explanation']}")
print(f"Persisted records in SQLite: {forecast_1h.get('persisted_records')}")
