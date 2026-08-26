"""
SentinelX Demo Controller

Provides synthetic event injection for controlled demo scenarios.
This allows demonstrating all event types without requiring specific
real-world camera setups.
"""
import time
import cv2
import numpy as np
from datetime import datetime
from database.db import save_event
from dashboard.store import add_event, update_stats
from dashboard.timeline import add_incident
from alerts.alert_manager import AlertManager
from evidence.evidence_manager import save as save_evidence_image


class DemoController:
    """Controls synthetic demo scenarios for the SentinelX dashboard."""

    def __init__(self):
        self.active = False
        self.scenarios = {
            'person': self._scenario_person,
            'crowd': self._scenario_crowd,
            'restricted': self._scenario_restricted,
            'abandoned': self._scenario_abandoned,
            'fall': self._scenario_fall,
            'weapon': self._scenario_weapon,
            'line_crossing': self._scenario_line_crossing,
        }

    def trigger(self, scenario_name, camera="Demo Camera", zone="General Area"):
        """Triggers a demo scenario by name."""
        if scenario_name not in self.scenarios:
            return {"success": False, "error": f"Unknown scenario: {scenario_name}"}
        
        try:
            result = self.scenarios[scenario_name](camera=camera, zone=zone)
            return {"success": True, "event": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _create_frame(self, label, color=(0, 255, 0), w=640, h=480):
        """Creates a synthetic evidence frame with overlay text."""
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:] = (30, 30, 40)
        cv2.putText(frame, label, (20, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.putText(frame, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), (20, h // 2 + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        return frame

    def _save_event_and_evidence(self, event_type, severity, camera, zone, confidence=0.9, track_id=-1, frame=None):
        """Saves event to DB, adds to dashboard store, and saves evidence image."""
        event_id = save_event(
            event_type=event_type,
            severity=severity,
            camera=camera,
            zone=zone,
            confidence=confidence,
            track_id=track_id,
            metadata={"demo": True, "synthetic": True}
        )

        add_event({
            "type": event_type,
            "zone": zone,
            "severity": severity,
            "camera": camera,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        add_incident({
            "time": datetime.now().strftime("%H:%M:%S"),
            "event": event_type,
            "zone": zone,
            "severity": severity
        })

        if frame is not None:
            try:
                save_evidence_image(frame, event_type, track_id=track_id, event_id=event_id, camera=camera)
            except Exception:
                pass

        alert_mgr = AlertManager()
        alert = alert_mgr.process({
            "type": event_type,
            "severity": severity,
            "zone": zone,
            "camera": camera
        })
        if alert:
            print(f"[DEMO] [ALERT] {alert['level']} : {alert['message']}")

        update_stats(
            persons=1 if "PERSON" in event_type else 0,
            vehicles=0,
            threat=severity,
            fps=10.0
        )

        return event_id

    def _scenario_person(self, camera="Demo Camera", zone="ENTRY"):
        frame = self._create_frame("PERSON DETECTED", (0, 255, 0))
        event_id = self._save_event_and_evidence("PERSON_DETECTED", "MEDIUM", camera, zone, confidence=0.92, track_id=1001, frame=frame)
        return {"type": "PERSON_DETECTED", "severity": "MEDIUM", "zone": zone, "track_id": 1001}

    def _scenario_crowd(self, camera="Demo Camera", zone="ENTRY"):
        frame = self._create_frame("CROWD DETECTED - 8 PERSONS", (255, 165, 0))
        event_id = self._save_event_and_evidence("CROWD_DETECTED", "MEDIUM", camera, zone, confidence=0.95, frame=frame)
        return {"type": "CROWD_DETECTED", "severity": "MEDIUM", "zone": zone}

    def _scenario_restricted(self, camera="Demo Camera", zone="RESTRICTED"):
        frame = self._create_frame("RESTRICTED AREA INTRUSION", (0, 0, 255))
        event_id = self._save_event_and_evidence("PERSON_DETECTED", "HIGH", camera, zone, confidence=0.97, track_id=1002, frame=frame)
        return {"type": "PERSON_DETECTED", "severity": "HIGH", "zone": "RESTRICTED", "track_id": 1002}

    def _scenario_abandoned(self, camera="Demo Camera", zone="SAFE"):
        frame = self._create_frame("ABANDONED OBJECT DETECTED", (255, 255, 0))
        event_id = self._save_event_and_evidence("ABANDONED_OBJECT", "HIGH", camera, zone, confidence=0.88, track_id=2001, frame=frame)
        return {"type": "ABANDONED_OBJECT", "severity": "HIGH", "zone": zone, "track_id": 2001}

    def _scenario_fall(self, camera="Demo Camera", zone="ENTRY"):
        frame = self._create_frame("FALL DETECTED", (0, 0, 255))
        event_id = self._save_event_and_evidence("FALL_DETECTED", "HIGH", camera, zone, confidence=0.91, track_id=1003, frame=frame)
        return {"type": "FALL_DETECTED", "severity": "HIGH", "zone": zone, "track_id": 1003}

    def _scenario_weapon(self, camera="Demo Camera", zone="ENTRY"):
        frame = self._create_frame("WEAPON DETECTED", (0, 0, 255))
        event_id = self._save_event_and_evidence("WEAPON_DETECTED", "HIGH", camera, zone, confidence=0.94, track_id=1004, frame=frame)
        return {"type": "WEAPON_DETECTED", "severity": "HIGH", "zone": zone, "track_id": 1004}

    def _scenario_line_crossing(self, camera="Demo Camera", zone="ENTRY"):
        frame = self._create_frame("LINE CROSSING DETECTED", (255, 0, 255))
        event_id = self._save_event_and_evidence("LINE_CROSSING", "MEDIUM", camera, zone, confidence=0.89, track_id=1005, frame=frame)
        return {"type": "LINE_CROSSING", "severity": "MEDIUM", "zone": zone, "track_id": 1005}


demo_controller = DemoController()
