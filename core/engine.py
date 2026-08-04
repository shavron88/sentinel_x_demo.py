import cv2
import time
from datetime import datetime

from database.db import save_event
from camera.camera_manager import CameraManager
from ai.detector import Detector

from events.event_manager import EventManager
from events.memory_manager import MemoryManager
from events.zone_manager import ZoneManager

from alerts.intelligence_engine import IntelligenceEngine
from alerts.alert_manager import AlertManager

from evidence.evidence_manager import EvidenceManager
from dashboard.timeline import add_incident

from dashboard.store import add_event, update_stats
from dashboard.stream import set_frame
from events.abandoned_object import AbandonedObjectDetector
from events.crowd_detector import CrowdDetector
from events.fall_detector import FallDetector
from events.line_crossing import LineCrossingDetector
from events.weapon_detector import WeaponDetector
from events.people_counter import PeopleCounter
from analytics.heatmap import Heatmap

VEHICLE_CLASSES = [2, 3, 5, 7]


def _update_threat_level(current_threat: str, severity: str) -> str:
    """Maintains threat hierarchy: HIGH > MEDIUM > LOW"""
    if severity == "HIGH":
        return "HIGH"
    if severity == "MEDIUM" and current_threat != "HIGH":
        return "MEDIUM"
    return current_threat


def run_engine():
    print("========== SENTINELX ENGINE STARTED ==========")

    camera = CameraManager()
    detector = Detector()

    event_manager = EventManager()
    memory_manager = MemoryManager()
    zone_manager = ZoneManager()
    abandoned_detector = AbandonedObjectDetector()
    fall_detector = FallDetector()
    crowd_detector = CrowdDetector()
    line_detector = LineCrossingDetector()
    weapon_detector = WeaponDetector()
    people_counter = PeopleCounter()
    heatmap = Heatmap()

    intelligence_engine = IntelligenceEngine()
    alert_manager = AlertManager()
    evidence_manager = EvidenceManager()

    previous_time = time.time()

    try:
        while True:
            frame = camera.get_frame()
            if frame is None:
                continue

            frame = cv2.resize(frame, (640, 360))
            results = detector.detect(frame) or []

            annotated_frame = results[0].plot() if results else frame.copy()
            h, w = frame.shape[:2]
            annotated_frame = zone_manager.draw(annotated_frame)

            # FPS Calculation
            current_time = time.time()
            delta = current_time - previous_time
            fps = int(1 / delta) if delta > 0 else 0
            previous_time = current_time

            person_count = 0
            vehicle_count = 0
            person_locations = {}
            events = []

            # ----------------------------------------------------
            # 1. AI Detections & Tracking Loop
            # ----------------------------------------------------
            for result in results:
                if result.boxes is None:
                    continue

                for box in result.boxes:
                    cls = int(box.cls[0])

                    if cls == 0:  # Person Class
                        person_count += 1
                        if box.id is None:
                            continue

                        track_id = int(box.id[0])
                        coords = box.xyxy[0]

                        if hasattr(coords, "tolist"):
                            x1, y1, x2, y2 = map(float, coords.tolist())
                        else:
                            x1, y1, x2, y2 = map(float, coords)

                        cx = ((x1 + x2) / 2) / w
                        cy = ((y1 + y2) / 2) / h

                        # Analytics Update
                        people_counter.update(track_id, cy)
                        heatmap.update(cx * w, cy * h)

                        # Line Crossing Detection Fix
                        line_event = line_detector.update(track_id, cy)
                        if line_event:
                            events.append(line_event)

                        zone = zone_manager.get_zone(cx, cy)
                        person_locations[track_id] = zone

                    elif cls in VEHICLE_CLASSES:
                        vehicle_count += 1

            # ----------------------------------------------------
            # 2. Event Collection from Specialized Detectors
            # ----------------------------------------------------
            crowd_event = crowd_detector.detect(person_count)
            if crowd_event:
                events.append(crowd_event)

            detector_events = event_manager.process(results)
            if detector_events:
                events.extend(detector_events)

            abandoned_events = abandoned_detector.update(results)
            if abandoned_events:
                events.extend(abandoned_events)

            fall_events = fall_detector.detect(results)
            if fall_events:
                events.extend(fall_events)

            weapon_events = weapon_detector.detect(results)
            if weapon_events:
                events.extend(weapon_events)

            # ----------------------------------------------------
            # 3. Processing Events, Threat Assessment & Storage
            # ----------------------------------------------------
            overall_threat = "LOW"

            for event in events:
                track_id = event.get("track_id")

                if track_id is None:
                    zone = "SAFE"
                    duration = 0
                else:
                    zone = person_locations.get(track_id, "SAFE")
                    memory_manager.update(track_id, zone)
                    duration = memory_manager.get_duration(track_id)

                    if memory_manager.check_loitering(track_id):
                        event["type"] = "LOITERING"

                    if memory_manager.moved_to_restricted(track_id):
                        print(f"[INTRUSION] Person {track_id} entered RESTRICTED zone")

                # Threat Evaluation Logic
                if event.get("type") == "ABANDONED_OBJECT":
                    severity = "HIGH"
                    zone = "SAFE"
                else:
                    severity = intelligence_engine.evaluate(
                        event, zone, duration, person_count
                    )

                overall_threat = _update_threat_level(overall_threat, severity)

                event["zone"] = zone
                event["severity"] = severity
                event["duration"] = int(duration)

                # Database & Dashboard Updates
                save_event(
                    event_type=event["type"],
                    severity=severity,
                    camera="Camera-1",
                    zone=zone,
                    confidence=event.get("confidence", 0.0),
                    screenshot=""
                )

                add_event({
                    "type": event["type"],
                    "zone": zone,
                    "severity": severity,
                    "duration": int(duration)
                })

                add_incident({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "event": event["type"],
                    "zone": zone,
                    "severity": severity
                })

                # Alert Processing & Visual Banners
                alert = alert_manager.process(event)
                if alert:
                    print(f"[ALERT] {alert['level']} : {alert['message']}")
                    level = alert["level"]
                    message = alert["message"]

                    color = (0, 0, 255) if level == "CRITICAL" else ((0, 165, 255) if level == "WARNING" else (0, 255, 0))

                    cv2.rectangle(annotated_frame, (0, 0), (640, 45), color, -1)
                    cv2.putText(
                        annotated_frame,
                        f"{level}: {message}",
                        (15, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (255, 255, 255),
                        2
                    )

                # Safe Evidence Storage Handling
                if (
                    event["type"] in ["LOITERING", "FALL_DETECTED", "ABANDONED_OBJECT", "WEAPON_DETECTED"]
                    or event["zone"] == "RESTRICTED"
                    or event["severity"] == "HIGH"
                ):
                    evidence_manager.save(
                        annotated_frame,
                        event["type"],
                        track_id if track_id is not None else -1
                    )

            # ----------------------------------------------------
            # 4. Drawing Bounding Boxes & HUD Overlays
            # ----------------------------------------------------
            for result in results:
                if result.boxes is None:
                    continue

                for box in result.boxes:
                    if int(box.cls[0]) != 0 or box.id is None:
                        continue

                    track_id = int(box.id[0])
                    coords = box.xyxy[0]

                    if hasattr(coords, "tolist"):
                        x1, y1, x2, y2 = map(int, coords.tolist())
                    else:
                        x1, y1, x2, y2 = map(int, coords)

                    zone = person_locations.get(track_id, "SAFE")
                    duration = int(memory_manager.get_duration(track_id))

                    cv2.putText(annotated_frame, f"ID:{track_id}", (x1, y1 - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(annotated_frame, zone, (x1, y1 - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    cv2.putText(annotated_frame, f"{duration}s", (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    box_color = (0, 0, 255) if zone == "RESTRICTED" else ((0, 255, 255) if zone == "ENTRY" else (0, 255, 0))
                    thickness = 3 if zone == "RESTRICTED" else 2
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), box_color, thickness)

            # HUD Display Overlays
            threat_color = (0, 0, 255) if overall_threat == "HIGH" else ((0, 255, 255) if overall_threat == "MEDIUM" else (0, 255, 0))
            cv2.putText(annotated_frame, f"THREAT: {overall_threat}", (15, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.9, threat_color, 3)

            cv2.putText(annotated_frame, f"Persons: {person_count}", (15, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(annotated_frame, f"Vehicles: {vehicle_count}", (15, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(annotated_frame, f"FPS: {fps}", (15, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.putText(annotated_frame, f"Entered: {people_counter.entered}", (420, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"Exited: {people_counter.exited}", (420, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(annotated_frame, f"Inside: {people_counter.inside()}", (420, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Stream & Render UI
            set_frame(annotated_frame)
            cv2.imshow("SentinelX Heatmap", heatmap.render())

            # Key Listener
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                print("[INFO] Shutting down SentinelX Engine...")
                break

            if hasattr(memory_manager, "cleanup"):
                memory_manager.cleanup()

            # Dashboard Update
            update_stats(
                persons=person_count,
                vehicles=vehicle_count,
                threat=overall_threat,
                fps=fps
            )

            time.sleep(0.01)

    finally:
        # Guarantee resource release on normal shutdown or unhandled runtime crashes
        camera.release()
        cv2.destroyAllWindows()
        print("========== SENTINELX ENGINE STOPPED SAFELY ==========")