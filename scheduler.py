"""
AEROsense APScheduler Background Pipelines.
Coordinates telemetry polling from ThingSpeak, rule-based alert triggering,
periodic anomaly detection, and execution concurrency locking.
"""

from __future__ import annotations

import logging
import os
import threading
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.database.db_connection import DatabaseConnectionManager, default_db_manager
from backend.database.models import SensorReading
from backend.database.sensor_repository import SensorRepository
from backend.services.anomaly_service import AnomalyService
from backend.services.runs_service import RunsService
from thingspeak_client import ThingSpeakClient

logger = logging.getLogger("aerosense.scheduler")

_SYNC_LOCK = threading.Lock()
_ANOMALY_LOCK = threading.Lock()


class AerosenseScheduler:
    """Manages periodic background data ingestion and intelligence pipelines."""

    def __init__(self, db_manager: Optional[DatabaseConnectionManager] = None):
        self.db = db_manager or default_db_manager
        self.scheduler = BackgroundScheduler(daemon=True)
        self.sync_interval_seconds = int(os.environ.get("AEROSENSE_SYNC_INTERVAL_SECONDS", "15"))
        self.anomaly_interval_minutes = int(os.environ.get("AEROSENSE_ANOMALY_INTERVAL_MINUTES", "5"))
        self._is_running = False

    def evaluate_alert_rules(self, reading: SensorReading) -> int:
        """Evaluate active threshold alert rules against a new reading."""
        now_utc = datetime.now(timezone.utc)
        now_iso = now_utc.isoformat()
        triggered_count = 0

        with self.db.get_connection() as conn:
            rules = [dict(r) for r in conn.execute("SELECT * FROM alert_rules WHERE is_enabled = 1;").fetchall()]

        sensor_values = {
            "temperature": reading.temperature,
            "humidity": reading.humidity,
            "smoke": reading.smoke,
            "carbon_monoxide": reading.carbon_monoxide,
            "ammonia": reading.ammonia,
            "nitrogen_oxides": reading.nitrogen_oxides,
            "pm25": reading.pm25,
        }

        with self.db.transaction() as conn:
            for rule in rules:
                s_key = rule["sensor_key"]
                val = sensor_values.get(s_key)
                if val is None:
                    continue

                warn_thresh = rule.get("warning_threshold")
                crit_thresh = rule.get("critical_threshold")
                severity = None

                if crit_thresh is not None and val >= crit_thresh:
                    severity = "CRITICAL"
                elif warn_thresh is not None and val >= warn_thresh:
                    severity = "WARNING"

                if not severity:
                    continue

                # Check cooldown: has an alert for this rule fired within cooldown_minutes?
                cooldown_min = rule.get("cooldown_minutes", 15)
                cooldown_cutoff = (now_utc - timedelta(minutes=cooldown_min)).isoformat()
                recent_alert = conn.execute(
                    """
                    SELECT 1 FROM alert_events
                    WHERE rule_id = ? AND triggered_at >= ? LIMIT 1;
                    """,
                    (rule["id"], cooldown_cutoff),
                ).fetchone()

                if recent_alert:
                    continue  # In cooldown window, suppress duplicate event

                # Insert alert event
                conn.execute(
                    """
                    INSERT INTO alert_events (
                        rule_id, device_id, sensor_key, observed_value, unit,
                        severity, status, message, triggered_at
                    ) VALUES (?, 'ESP32-AEROSENSE-MAIN', ?, ?, 'ADC', ?, 'OPEN', ?, ?);
                    """,
                    (
                        rule["id"],
                        s_key,
                        round(float(val), 2),
                        severity,
                        f"{rule['rule_name']}: {s_key} reached {val} (threshold {crit_thresh or warn_thresh})",
                        now_iso,
                    ),
                )
                triggered_count += 1

        return triggered_count

    def sync_once(self) -> Dict[str, Any]:
        """Perform a single isolated telemetry sync cycle with duplicate-run lock."""
        if not _SYNC_LOCK.acquire(blocking=False):
            logger.info("Telemetry sync job skipped: previous cycle still active.")
            return {"status": "SKIPPED", "reason": "LOCKED"}

        runs_svc = RunsService(self.db)
        run_id = runs_svc.start_run(run_type="scheduled_telemetry_sync", triggered_by="scheduler")
        t0 = datetime.now(timezone.utc)

        try:
            repo = SensorRepository(self.db)
            channel_id = int(os.environ.get("THINGSPEAK_CHANNEL_ID", "3540991"))
            client = ThingSpeakClient(channel_id=channel_id)
            entry, status_info = client.fetch_latest(use_cache=False)

            if not entry:
                res = {
                    "status": "NO_ENTRY",
                    "channel_state": status_info.state,
                    "error": status_info.error_message,
                    "rows_affected": 0,
                }
                runs_svc.finish_run(run_id, status="SUCCESS", rows_affected=0, summary=res)
                return res

            is_dup = repo.check_duplicate(
                source="thingspeak_live",
                entry_id=str(entry.entry_id) if entry.entry_id else None,
                timestamp=entry.timestamp.isoformat(),
            )

            if is_dup:
                res = {"status": "UP_TO_DATE", "entry_id": entry.entry_id, "rows_affected": 0}
                runs_svc.finish_run(run_id, status="SUCCESS", rows_affected=0, summary=res)
                return res

            # Insert reading
            reading = SensorReading(
                timestamp=entry.timestamp.isoformat(),
                temperature=entry.values.get("field1"),
                humidity=entry.values.get("field2"),
                smoke=entry.values.get("field3"),
                carbon_monoxide=entry.values.get("field4"),
                ammonia=entry.values.get("field5"),
                nitrogen_oxides=entry.values.get("field6"),
                pm25=entry.values.get("field7"),
                source="thingspeak_live",
                entry_id=str(entry.entry_id) if entry.entry_id else None,
                device_id="ESP32-AEROSENSE-MAIN",
            )
            ins_res = repo.bulk_insert_readings([reading])
            inserted = ins_res[0] if isinstance(ins_res, tuple) else int(ins_res)

            # Update device table
            with self.db.transaction() as conn:
                conn.execute(
                    """
                    UPDATE devices
                    SET last_seen = ?, last_successful_upload = ?, status = 'LIVE',
                        total_packets_sent = total_packets_sent + ?
                    WHERE device_id = 'ESP32-AEROSENSE-MAIN';
                    """,
                    (entry.timestamp.isoformat(), entry.timestamp.isoformat(), inserted),
                )

            # Evaluate alert rules
            alerts_fired = self.evaluate_alert_rules(reading)

            elapsed_ms = (datetime.now(timezone.utc) - t0).total_seconds() * 1000.0
            res = {
                "status": "INSERTED",
                "entry_id": entry.entry_id,
                "rows_affected": inserted,
                "alerts_fired": alerts_fired,
            }
            runs_svc.finish_run(run_id, status="SUCCESS", rows_affected=inserted, duration_ms=elapsed_ms, summary=res)
            return res

        except Exception as exc:
            elapsed_ms = (datetime.now(timezone.utc) - t0).total_seconds() * 1000.0
            logger.error(f"Error during scheduled telemetry sync: {exc}")
            runs_svc.finish_run(run_id, status="FAILED", rows_affected=0, duration_ms=elapsed_ms, error_message=str(exc))
            return {"status": "FAILED", "error": str(exc)}
        finally:
            _SYNC_LOCK.release()

    def detect_anomalies_once(self, limit_readings: int = 500) -> Dict[str, Any]:
        """Perform a scheduled anomaly detection run on recent observations."""
        if not _ANOMALY_LOCK.acquire(blocking=False):
            logger.info("Anomaly detection job skipped: previous cycle still active.")
            return {"status": "SKIPPED", "reason": "LOCKED"}

        runs_svc = RunsService(self.db)
        run_id = runs_svc.start_run(run_type="scheduled_anomaly_detection", triggered_by="scheduler")
        t0 = datetime.now(timezone.utc)

        try:
            repo = SensorRepository(self.db)
            anom_svc = AnomalyService(self.db)

            with self.db.get_connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT id, timestamp, temperature, humidity, smoke, carbon_monoxide,
                           ammonia, nitrogen_oxides, pm25, source
                    FROM sensor_readings
                    ORDER BY timestamp DESC
                    LIMIT ?;
                    """,
                    (limit_readings,),
                )
                rows = cursor.fetchall()
                col_names = [d[0] for d in cursor.description] if cursor.description else []

            if not rows:
                res = {"status": "NO_READINGS", "rows_affected": 0}
                runs_svc.finish_run(run_id, status="SUCCESS", rows_affected=0, summary=res)
                return res

            import pandas as pd
            df = pd.DataFrame.from_records([tuple(r) for r in rows], columns=col_names)
            df = df.sort_values("timestamp").reset_index(drop=True)

            detected = anom_svc.detect_anomalies(df, persist=True)
            elapsed_ms = (datetime.now(timezone.utc) - t0).total_seconds() * 1000.0

            res = {"status": "SUCCESS", "anomalies_detected": len(detected), "rows_affected": len(detected)}
            runs_svc.finish_run(run_id, status="SUCCESS", rows_affected=len(detected), duration_ms=elapsed_ms, summary=res)
            return res

        except Exception as exc:
            elapsed_ms = (datetime.now(timezone.utc) - t0).total_seconds() * 1000.0
            logger.error(f"Error in scheduled anomaly detection: {exc}")
            runs_svc.finish_run(run_id, status="FAILED", rows_affected=0, duration_ms=elapsed_ms, error_message=str(exc))
            return {"status": "FAILED", "error": str(exc)}
        finally:
            _ANOMALY_LOCK.release()

    def start(self):
        """Start the background scheduler with configured interval triggers."""
        if self._is_running:
            return

        self.scheduler.add_job(
            self.sync_once,
            trigger=IntervalTrigger(seconds=self.sync_interval_seconds),
            id="job_telemetry_sync",
            name="ThingSpeak Telemetry Sync",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )

        self.scheduler.add_job(
            self.detect_anomalies_once,
            trigger=IntervalTrigger(minutes=self.anomaly_interval_minutes),
            id="job_anomaly_detection",
            name="Periodic Anomaly Detection",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )

        self.scheduler.start()
        self._is_running = True
        logger.info(
            f"AEROsense background scheduler started (sync: {self.sync_interval_seconds}s, anomaly: {self.anomaly_interval_minutes}m)."
        )

    def shutdown(self, wait: bool = False):
        """Gracefully shut down background scheduler jobs."""
        if self._is_running:
            self.scheduler.shutdown(wait=wait)
            self._is_running = False
            logger.info("AEROsense background scheduler stopped.")


# Global default scheduler instance
default_scheduler = AerosenseScheduler()
