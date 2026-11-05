"""
ThingSpeak REST API Client for AEROsense Dashboard
Handles secure communication, response parsing, rate limits, staleness detection, and error handling.
"""

import os
import time
import math
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
import requests

from config import (
    THINGSPEAK_BASE_URL,
    DEFAULT_CHANNEL_ID,
    STALE_DATA_TIMEOUT_SECONDS,
    OFFLINE_TIMEOUT_SECONDS,
    SENSOR_FIELDS,
)

logger = logging.getLogger(__name__)


def format_elapsed_time(seconds: Optional[float]) -> str:
    """Format elapsed seconds into human-readable duration string."""
    if seconds is None:
        return "Unknown"
    seconds = max(0.0, seconds)
    if seconds < 60:
        return f"{int(seconds)}s ago"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s ago"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m ago"


@dataclass
class ChannelStatus:
    # Sensor connection state: strictly "LIVE", "STALE", or "OFFLINE"
    state: str              # "LIVE", "STALE", "OFFLINE" (or "DEMO")
    status_label: str       # Display label: "LIVE", "STALE", "OFFLINE", "DEMO MODE"
    status_color: str       # Hex color: #10B981 (LIVE), #F59E0B (STALE), #EF4444 (OFFLINE)
    api_connected: bool     # Indicates whether ThingSpeak REST API is reachable
    sensor_active: bool     # Indicates whether physical ESP32 is actively transmitting
    last_entry_time: Optional[datetime] = None
    seconds_since_last: Optional[float] = None
    time_elapsed_display: str = "—"
    error_message: Optional[str] = None
    details: str = ""
    is_demo: bool = False

    @property
    def is_connected(self) -> bool:
        """Backward compatibility for legacy callers."""
        return self.api_connected and self.state in ("LIVE", "STALE", "DEMO")


@dataclass
class TelemetryEntry:
    entry_id: Optional[int]
    timestamp: datetime
    values: Dict[str, Optional[float]]
    raw_values: Dict[str, Any]
    is_stale: bool = False
    is_demo: bool = False


class ThingSpeakClient:
    """Robust client for fetching ThingSpeak Channel telemetry."""

    def __init__(self, channel_id: int = DEFAULT_CHANNEL_ID, read_api_key: Optional[str] = None):
        self.channel_id = channel_id
        # Secure credential hierarchy: argument -> environment variable -> empty
        self.read_api_key = (
            read_api_key
            or os.environ.get("THINGSPEAK_READ_API_KEY", "").strip()
            or ""
        )
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "AEROsense-IndoorAirQuality-Dashboard/1.0",
            "Accept": "application/json",
        })
        self._last_request_time = 0.0

    def set_api_key(self, api_key: str):
        """Update the Read API key securely."""
        self.read_api_key = api_key.strip() if api_key else ""

    def _parse_timestamp(self, ts_str: Optional[str]) -> Optional[datetime]:
        """Parse ThingSpeak ISO8601 UTC timestamp to local datetime."""
        if not ts_str:
            return None
        try:
            # Format: '2026-11-04T11:20:30Z' or with offset
            ts_clean = ts_str.replace("Z", "+00:00")
            utc_dt = datetime.fromisoformat(ts_clean)
            # Convert to local timezone
            local_dt = utc_dt.astimezone()
            return local_dt
        except Exception as e:
            logger.warning(f"Error parsing timestamp '{ts_str}': {e}")
            return None

    def _clean_float(self, raw_val: Any) -> Optional[float]:
        """Safely convert sensor raw values to float, handling missing/null values."""
        if raw_val is None:
            return None
        val_str = str(raw_val).strip()
        if not val_str or val_str.lower() in ("nan", "null", "none", "err", "--"):
            return None
        try:
            val = float(val_str)
            if math.isnan(val) or math.isinf(val):
                return None
            return val
        except (ValueError, TypeError):
            return None

    def fetch_latest(self) -> Tuple[Optional[TelemetryEntry], ChannelStatus]:
        """
        Fetch the most recent channel entry.
        Never substitutes demo data. Returns explicit error status on failure.
        """
        url = f"{THINGSPEAK_BASE_URL}/channels/{self.channel_id}/feeds/last.json"
        params: Dict[str, Any] = {}
        if self.read_api_key:
            params["api_key"] = self.read_api_key

        now_local = datetime.now().astimezone()

        try:
            self._last_request_time = time.time()
            response = self.session.get(url, params=params, timeout=8.0)

            if response.status_code in (401, 403) or (response.status_code == 400 and response.text.strip() == "-1"):
                return None, ChannelStatus(
                    state="OFFLINE",
                    status_label="OFFLINE",
                    status_color="#EF4444",
                    api_connected=False,
                    sensor_active=False,
                    error_message="ThingSpeak rejected the Read API Key (-1). Private channels require your valid 16-character Channel Read API Key.",
                    details="ThingSpeak API authentication failed: Check Channel Read API Key in .env",
                )
            elif response.status_code == 404:
                return None, ChannelStatus(
                    state="OFFLINE",
                    status_label="OFFLINE",
                    status_color="#EF4444",
                    api_connected=False,
                    sensor_active=False,
                    error_message=f"ThingSpeak channel #{self.channel_id} not found.",
                    details="Channel not found on ThingSpeak servers.",
                )
            elif response.status_code == 429:
                return None, ChannelStatus(
                    state="STALE",
                    status_label="STALE",
                    status_color="#F59E0B",
                    api_connected=True,
                    sensor_active=False,
                    error_message="ThingSpeak rate limit exceeded. Refresh interval must be >= 15s.",
                    details="API rate limit hit. Throttling requests.",
                )
            elif response.status_code != 200:
                return None, ChannelStatus(
                    state="OFFLINE",
                    status_label="OFFLINE",
                    status_color="#EF4444",
                    api_connected=False,
                    sensor_active=False,
                    error_message=f"HTTP Error {response.status_code}: {response.text[:100]}",
                    details=f"API error code {response.status_code}",
                )

            data = response.json()
            if not data or data == -1 or not isinstance(data, dict):
                return None, ChannelStatus(
                    state="OFFLINE",
                    status_label="OFFLINE",
                    status_color="#EF4444",
                    api_connected=True,
                    sensor_active=False,
                    error_message="Channel has not recorded any feed entries yet.",
                    details="Channel exists, but 0 sensor records were found.",
                )

            entry_id = data.get("entry_id")
            raw_ts = data.get("created_at")
            entry_dt = self._parse_timestamp(raw_ts)

            if not entry_dt:
                entry_dt = now_local

            # Calculate time delta for stale data detection
            diff_seconds = (now_local - entry_dt).total_seconds()
            if diff_seconds < 0:
                diff_seconds = 0.0

            is_stale = diff_seconds > STALE_DATA_TIMEOUT_SECONDS
            is_offline = diff_seconds > OFFLINE_TIMEOUT_SECONDS
            elapsed_disp = format_elapsed_time(diff_seconds)

            if is_offline:
                status = ChannelStatus(
                    state="OFFLINE",
                    status_label="OFFLINE",
                    status_color="#EF4444",
                    api_connected=True,
                    sensor_active=False,
                    last_entry_time=entry_dt,
                    seconds_since_last=diff_seconds,
                    time_elapsed_display=elapsed_disp,
                    error_message=f"No sensor data received in {elapsed_disp} (Sensor Connection Unavailable).",
                    details=f"API link active, but sensor node is unresponsive (>15m).",
                )
            elif is_stale:
                status = ChannelStatus(
                    state="STALE",
                    status_label="STALE",
                    status_color="#F59E0B",
                    api_connected=True,
                    sensor_active=False,
                    last_entry_time=entry_dt,
                    seconds_since_last=diff_seconds,
                    time_elapsed_display=elapsed_disp,
                    error_message=f"No new sensor readings within expected interval ({elapsed_disp}).",
                    details=f"API link active, but new sensor readings are delayed (>5m).",
                )
            else:
                status = ChannelStatus(
                    state="LIVE",
                    status_label="LIVE",
                    status_color="#10B981",
                    api_connected=True,
                    sensor_active=True,
                    last_entry_time=entry_dt,
                    seconds_since_last=diff_seconds,
                    time_elapsed_display=elapsed_disp,
                    details=f"Live sensor telemetry active (last updated {elapsed_disp}).",
                )

            # Parse fields 1-7 safely
            values: Dict[str, Optional[float]] = {}
            for field_key in SENSOR_FIELDS.keys():
                values[field_key] = self._clean_float(data.get(field_key))

            entry = TelemetryEntry(
                entry_id=entry_id,
                timestamp=entry_dt,
                values=values,
                raw_values=data,
                is_stale=is_stale,
                is_demo=False,
            )
            return entry, status

        except requests.exceptions.Timeout:
            return None, ChannelStatus(
                state="OFFLINE",
                status_label="OFFLINE",
                status_color="#EF4444",
                api_connected=False,
                sensor_active=False,
                error_message="ThingSpeak API took too long to respond (>8s).",
                details="HTTP request timed out.",
            )
        except requests.exceptions.ConnectionError:
            return None, ChannelStatus(
                state="OFFLINE",
                status_label="OFFLINE",
                status_color="#EF4444",
                api_connected=False,
                sensor_active=False,
                error_message="Could not reach api.thingspeak.com. Check internet connection.",
                details="Network connection error.",
            )
        except Exception as e:
            return None, ChannelStatus(
                state="OFFLINE",
                status_label="OFFLINE",
                status_color="#EF4444",
                api_connected=False,
                sensor_active=False,
                error_message=str(e),
                details="Unexpected client error.",
            )

    def fetch_historical(
        self,
        results: int = 100,
        minutes: Optional[int] = None,
        days: Optional[int] = None,
    ) -> Tuple[List[TelemetryEntry], Optional[Dict[str, Any]], ChannelStatus]:
        """
        Fetch historical feeds for time-series analytics.
        Uses results count or time windows (minutes/days).
        """
        url = f"{THINGSPEAK_BASE_URL}/channels/{self.channel_id}/feeds.json"
        params: Dict[str, Any] = {}
        if self.read_api_key:
            params["api_key"] = self.read_api_key

        if days is not None:
            params["days"] = min(days, 30)
        elif minutes is not None:
            params["minutes"] = min(minutes, 8000)
        else:
            params["results"] = min(max(results, 1), 8000)

        now_local = datetime.now().astimezone()

        try:
            response = self.session.get(url, params=params, timeout=12.0)
            if response.status_code in (401, 403) or (response.status_code == 400 and response.text.strip() == "-1"):
                status = ChannelStatus(
                    state="OFFLINE",
                    status_label="OFFLINE",
                    status_color="#EF4444",
                    api_connected=False,
                    sensor_active=False,
                    error_message="Invalid or missing Read API Key for private channel (-1).",
                    details="ThingSpeak API authentication failed for historical feed.",
                )
                return [], None, status
            elif response.status_code != 200:
                status = ChannelStatus(
                    state="OFFLINE",
                    status_label="OFFLINE",
                    status_color="#EF4444",
                    api_connected=False,
                    sensor_active=False,
                    error_message=f"HTTP {response.status_code}: {response.text[:80]}",
                    details=f"API error code {response.status_code}",
                )
                return [], None, status

            payload = response.json()
            channel_meta = payload.get("channel", {})
            feeds_data = payload.get("feeds", [])

            entries: List[TelemetryEntry] = []
            for item in feeds_data:
                entry_dt = self._parse_timestamp(item.get("created_at")) or now_local
                values: Dict[str, Optional[float]] = {}
                for field_key in SENSOR_FIELDS.keys():
                    values[field_key] = self._clean_float(item.get(field_key))

                entries.append(
                    TelemetryEntry(
                        entry_id=item.get("entry_id"),
                        timestamp=entry_dt,
                        values=values,
                        raw_values=item,
                        is_stale=False,
                        is_demo=False,
                    )
                )

            # Check status of the latest historical entry
            if entries:
                latest_ts = entries[-1].timestamp
                diff_sec = max(0.0, (now_local - latest_ts).total_seconds())
                is_stale = diff_sec > STALE_DATA_TIMEOUT_SECONDS
                is_offline = diff_sec > OFFLINE_TIMEOUT_SECONDS
                elapsed_disp = format_elapsed_time(diff_sec)

                if is_offline:
                    status = ChannelStatus(
                        state="OFFLINE",
                        status_label="OFFLINE",
                        status_color="#EF4444",
                        api_connected=True,
                        sensor_active=False,
                        last_entry_time=latest_ts,
                        seconds_since_last=diff_sec,
                        time_elapsed_display=elapsed_disp,
                        error_message=f"Sensor inactive for {elapsed_disp}.",
                        details=f"API link active, but sensor connection unavailable (>15m).",
                    )
                elif is_stale:
                    status = ChannelStatus(
                        state="STALE",
                        status_label="STALE",
                        status_color="#F59E0B",
                        api_connected=True,
                        sensor_active=False,
                        last_entry_time=latest_ts,
                        seconds_since_last=diff_sec,
                        time_elapsed_display=elapsed_disp,
                        error_message=f"No new readings in {elapsed_disp} (Stale).",
                        details=f"API link active, sensor delayed (>5m).",
                    )
                else:
                    status = ChannelStatus(
                        state="LIVE",
                        status_label="LIVE",
                        status_color="#10B981",
                        api_connected=True,
                        sensor_active=True,
                        last_entry_time=latest_ts,
                        seconds_since_last=diff_sec,
                        time_elapsed_display=elapsed_disp,
                        details=f"Live sensor telemetry active (last updated {elapsed_disp}).",
                    )
            else:
                status = ChannelStatus(
                    state="OFFLINE",
                    status_label="OFFLINE",
                    status_color="#EF4444",
                    api_connected=True,
                    sensor_active=False,
                    error_message="No feed entries recorded in this window.",
                    details="Channel feed is empty.",
                )

            return entries, channel_meta, status

        except Exception as e:
            status = ChannelStatus(
                state="OFFLINE",
                status_label="OFFLINE",
                status_color="#EF4444",
                api_connected=False,
                sensor_active=False,
                error_message=str(e),
                details="Network or parsing error on historical feeds.",
            )
            return [], None, status

    @staticmethod
    def generate_demo_dataset(points: int = 60, interval_seconds: int = 60) -> Tuple[List[TelemetryEntry], ChannelStatus]:
        """
        Generate realistic simulated telemetry for demonstration/testing purposes only.
        ALWAYS explicitly flagged as is_demo=True.
        """
        import random
        random.seed(42)  # Consistent baseline pattern with gentle noise

        now = datetime.now().astimezone()
        entries: List[TelemetryEntry] = []

        for i in range(points):
            offset_seconds = (points - 1 - i) * interval_seconds
            entry_time = now - timedelta(seconds=offset_seconds)
            progress = i / max(1, points - 1)

            # Diurnal-like slight variation
            sin_wave = math.sin(progress * 2 * math.pi)

            temp = 22.5 + 2.0 * sin_wave + random.uniform(-0.3, 0.3)
            hum = 45.0 - 5.0 * sin_wave + random.uniform(-1.0, 1.0)
            smoke = max(10.0, 25.0 + 8.0 * random.random() + (15.0 if 35 <= i <= 42 else 0.0))
            co = max(1.0, 3.5 + 1.2 * random.random() + (4.0 if 35 <= i <= 42 else 0.0))
            nh3 = max(0.5, 2.2 + 0.8 * random.random())
            nox = max(0.01, 0.035 + 0.015 * sin_wave + random.uniform(-0.005, 0.005))
            pm25 = max(5.0, 18.0 + 8.0 * sin_wave + (25.0 if 20 <= i <= 28 else 0.0) + random.uniform(-2.0, 2.0))

            vals = {
                "field1": round(temp, 1),
                "field2": round(hum, 1),
                "field3": round(smoke, 1),
                "field4": round(co, 2),
                "field5": round(nh3, 2),
                "field6": round(nox, 3),
                "field7": round(pm25, 1),
            }

            entries.append(
                TelemetryEntry(
                    entry_id=1000 + i,
                    timestamp=entry_time,
                    values=vals,
                    raw_values=vals,
                    is_stale=False,
                    is_demo=True,
                )
            )

        demo_status = ChannelStatus(
            state="DEMO",
            status_label="DEMO MODE",
            status_color="#8B5CF6",
            api_connected=False,
            sensor_active=False,
            last_entry_time=now,
            seconds_since_last=0.0,
            time_elapsed_display="Just now",
            details="Simulated offline telemetry for demonstration and layout verification.",
            is_demo=True,
        )

        return entries, demo_status
