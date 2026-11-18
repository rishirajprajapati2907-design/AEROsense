"""
Scratch script to verify Phase 6 Anomaly Detection Pipeline on aerosense.db
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.anomaly_service import AnomalyService
import pprint
import time

s = AnomalyService()
initial_count = s.repository.get_anomaly_count()
print(f"Initial DB anomaly count: {initial_count}")

# 1. Run full detection pipeline over actual stored historical data
t0 = time.time()
detected = s.run_detection_pipeline(persist=True)
elapsed = time.time() - t0
print(f"Pipeline completed in {elapsed:.2f}s: {len(detected)} anomaly events detected across all 5 methods.")

summary = s.get_anomaly_summary()
print("\n--- Consolidated Anomaly Summary Breakdown ---")
pprint.pprint(summary)

# 2. Test duplicate prevention on repeated run
print("\nTesting duplicate prevention on second execution...")
t0 = time.time()
detected_2 = s.run_detection_pipeline(persist=True)
elapsed_2 = time.time() - t0
summary_2 = s.get_anomaly_summary()
print(f"Second run completed in {elapsed_2:.2f}s.")
print(f"Total anomalies in DB after rerun: {summary_2['total_anomalies']} (Must match {summary['total_anomalies']})")

assert summary_2['total_anomalies'] == summary['total_anomalies'], "Error: duplicate anomaly records were inserted!"
print("\n>>> DUPLICATE PREVENTION VERIFIED PERFECTLY! <<<")

# 3. Test DataFrame formatting for frontend
df_anom = s.get_anomalies_dataframe(limit=10)
print(f"\nSample of {len(df_anom)} formatted anomalies for Streamlit frontend:")
print(df_anom[["timestamp", "sensor", "value", "unit", "severity", "method", "reason"]].to_string())
