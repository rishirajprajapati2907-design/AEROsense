import os
import sys

sys.path.insert(0, os.path.abspath("."))

from dotenv import load_dotenv
load_dotenv()

from backend.services.thingspeak_sync_service import ThingSpeakSyncService
from backend.services.device_service import DeviceService
from backend.database.sensor_repository import SensorRepository

sync_service = ThingSpeakSyncService()
print("Channel ID:", sync_service.channel_id)
print("API Key set:", bool(sync_service.api_key))

# Test sync_latest against real ThingSpeak API endpoint
result = sync_service.sync_latest(force=True)
print("\nSync Latest Result:")
print("Status:", result.status)
print("Channel State:", result.channel_state)
print("Synced Records:", result.synced_records)
print("Skipped Duplicates:", result.skipped_duplicates)
print("Last Entry ID:", result.last_entry_id)
print("Last Timestamp:", result.last_timestamp)
print("Error Message:", result.error_message)
print("Response Time (ms):", round(result.response_time_ms, 2))

# Test sync_historical (last 10 records)
print("\nSync Historical (results=10) Result:")
hist_result = sync_service.sync_historical(results=10)
print("Status:", hist_result.status)
print("Channel State:", hist_result.channel_state)
print("Synced Records:", hist_result.synced_records)
print("Skipped Duplicates:", hist_result.skipped_duplicates)
print("Last Entry ID:", hist_result.last_entry_id)
print("Error Message:", hist_result.error_message)

# Check device status
dev_service = DeviceService()
health = dev_service.get_device_health()
print("\nDevice Health:")
print("Device ID:", health["device_id"])
print("Status:", health["status"])
print("Last Seen:", health["last_seen"])
print("Health Score:", health["health_score"])
print("Time Elapsed:", health["time_elapsed_display"])
