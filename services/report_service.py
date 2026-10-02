import csv
import io
import logging
from datetime import datetime, timedelta

from database.db import get_all_events

logger = logging.getLogger("SentinelX.ReportService")

TIMEFRAME_DAYS = {"daily": 1, "weekly": 7, "monthly": 30, "yearly": 365}
MAX_REPORT_ROWS = 20000


class ReportService:
    """Generates Structured Exports (CSV, PDF Data, Aggregated Summaries)."""

    @staticmethod
    def _fetch_events_for_timeframe(days=1, user_id=None):
        """Fetches the current user's events within a rolling window."""
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        return get_all_events(limit=MAX_REPORT_ROWS, user_id=user_id, start_date=cutoff)

    @staticmethod
    def _resolve_days(timeframe):
        return TIMEFRAME_DAYS.get(str(timeframe or "daily").lower(), 1)

    @classmethod
    def generate_csv_report(cls, timeframe="daily", user_id=None):
        """Generates an in-memory CSV file stream."""
        days = cls._resolve_days(timeframe)
        events = cls._fetch_events_for_timeframe(days, user_id=user_id)

        output = io.StringIO()
        writer = csv.writer(output)

        # Header Row
        writer.writerow(["Event ID", "Timestamp", "Event Type", "Severity", "Camera", "Zone", "Confidence", "Duration (s)"])

        # Data Rows
        for e in events:
            try:
                confidence = "%.2f" % float(e.get("confidence") or 0.0)
            except (TypeError, ValueError):
                confidence = "0.00"
            writer.writerow([
                e.get("id"),
                e.get("timestamp"),
                e.get("event_type"),
                e.get("severity"),
                e.get("camera"),
                e.get("zone"),
                confidence,
                e.get("duration", 0.0)
            ])

        output.seek(0)
        return output.getvalue()

    @classmethod
    def generate_summary_data(cls, timeframe="daily", user_id=None):
        """Generates structured metrics summary for UI rendering or PDF generation."""
        days = cls._resolve_days(timeframe)
        events = cls._fetch_events_for_timeframe(days, user_id=user_id)

        total_incidents = len(events)
        critical_count = sum(1 for e in events if (e.get("severity") or "").upper() in ("HIGH", "CRITICAL"))
        medium_count = sum(1 for e in events if (e.get("severity") or "").upper() == "MEDIUM")
        low_count = sum(1 for e in events if (e.get("severity") or "").upper() == "LOW")

        # Top offending camera & zone
        cam_counts = {}
        zone_counts = {}
        type_counts = {}

        for e in events:
            cam = e.get("camera", "Unknown")
            zone = e.get("zone", "Unknown")
            e_type = e.get("event_type", "General")

            cam_counts[cam] = cam_counts.get(cam, 0) + 1
            zone_counts[zone] = zone_counts.get(zone, 0) + 1
            type_counts[e_type] = type_counts.get(e_type, 0) + 1

        most_active_cam = max(cam_counts, key=cam_counts.get) if cam_counts else "N/A"
        most_affected_zone = max(zone_counts, key=zone_counts.get) if zone_counts else "N/A"

        return {
            "timeframe": timeframe.capitalize(),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "metrics": {
                "total_incidents": total_incidents,
                "high_severity": critical_count,
                "medium_severity": medium_count,
                "low_severity": low_count,
                "most_active_camera": most_active_cam,
                "most_affected_zone": most_affected_zone
            },
            "breakdown_by_type": type_counts,
            "recent_samples": events[:10]
        }