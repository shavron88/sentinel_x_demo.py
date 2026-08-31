import csv
import io
import json
import logging
from datetime import datetime, timedelta
from database.db import get_connection

logger = logging.getLogger("SentinelX.ReportService")

class ReportService:
    """Generates Structured Exports (CSV, PDF Data, Aggregated Summaries)."""

    @staticmethod
    def _fetch_events_for_timeframe(days=1):
        """Fetches events from DB based on rolling days filter."""
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM events WHERE timestamp >= ? ORDER BY id DESC",
                (cutoff,)
            )
            return [dict(row) for row in cursor.fetchall()]

    @classmethod
    def generate_csv_report(cls, timeframe="daily"):
        """Generates an in-memory CSV file stream."""
        days_map = {"daily": 1, "weekly": 7, "monthly": 30}
        days = days_map.get(timeframe.lower(), 1)
        events = cls._fetch_events_for_timeframe(days)

        output = io.StringIO()
        writer = csv.writer(output)

        # Header Row
        writer.writerow(["Event ID", "Timestamp", "Event Type", "Severity", "Camera", "Zone", "Confidence", "Duration (s)"])

        # Data Rows
        for e in events:
            writer.writerow([
                e.get("id"),
                e.get("timestamp"),
                e.get("event_type"),
                e.get("severity"),
                e.get("camera"),
                e.get("zone"),
                f"{e.get('confidence', 0.0):.2f}",
                e.get("duration", 0.0)
            ])

        output.seek(0)
        return output.getvalue()

    @classmethod
    def generate_summary_data(cls, timeframe="daily"):
        """Generates structured metrics summary for UI rendering or PDF generation."""
        days_map = {"daily": 1, "weekly": 7, "monthly": 30}
        days = days_map.get(timeframe.lower(), 1)
        events = cls._fetch_events_for_timeframe(days)

        total_incidents = len(events)
        critical_count = sum(1 for e in events if e.get("severity") == "HIGH")
        medium_count = sum(1 for e in events if e.get("severity") == "MEDIUM")
        low_count = sum(1 for e in events if e.get("severity") == "LOW")

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