import cv2
import time

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


def run_engine():

    print("========== ENGINE STARTED ==========")

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

    while True:

        frame = camera.get_frame()

        if frame is None:
            continue

        frame = cv2.resize(frame, (640, 360))

        results = detector.detect(frame) or []

        if results:
            annotated_frame = results[0].plot()
        else:
            annotated_frame = frame.copy()

        h, w = frame.shape[:2]

        annotated_frame = zone_manager.draw(annotated_frame)

        

        current_time = time.time()

        delta = current_time - previous_time

        fps = int(1 / delta) if delta > 0 else 0

        previous_time = current_time

        person_count = 0
        crowd_event = crowd_detector.detect(person_count)
        events = []

        if crowd_event:
            events.append(crowd_event)

        vehicle_count = 0

        person_locations = {}

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                cls = int(box.cls[0])

                if cls == 0:

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

                    line_event = line_detector.update(track_id, cy)
                    people_counter.update(track_id, cy)

                    heatmap.update(
                         cx * w,
                          cy * h
                                     )

                    if line_event:
                        events.append(line_event)

                    zone = zone_manager.get_zone(cx, cy)

                    person_locations[track_id] = zone

                elif cls in VEHICLE_CLASSES:
                    vehicle_count += 1

        threat = "LOW"

        # =====================================
        # ABANDONED OBJECT DETECTION
        # =====================================

        abandoned_events = abandoned_detector.update(results)

        events = event_manager.process(results)

        if abandoned_events:
            events.extend(abandoned_events)

        fall_events = fall_detector.detect(results)

        weapon_events = weapon_detector.detect(results)

        if weapon_events:
            events.extend(weapon_events)

        if fall_events:
            events.extend(fall_events)

        for event in events:

            track_id = event.get("track_id")

            if track_id is None:
                continue

            zone = person_locations.get(track_id, "SAFE")

            memory_manager.update(track_id, zone)

            duration = memory_manager.get_duration(track_id)

            # ==========================
            # Event Type Upgrade
            # ==========================

            if memory_manager.check_loitering(track_id):

                event["type"] = "LOITERING"

            if memory_manager.moved_to_restricted(track_id):

                print(f"[INTRUSION] Person {track_id} entered RESTRICTED zone")

            severity = intelligence_engine.evaluate(
                event,
                zone,
                duration,
                person_count
            )

            threat = severity

            event["zone"] = zone
            event["severity"] = severity
            event["duration"] = int(duration)

            add_event({

                "type": event["type"],
                "zone": zone,
                "severity": severity,
                "duration": int(duration)

            })

            from datetime import datetime

            add_incident({

                "time": datetime.now().strftime("%H:%M:%S"),
                "event": event["type"],
                "zone": zone,
                "severity": severity

            })

            alert = alert_manager.process(event)

            # Abandoned object is always HIGH threat
            if event["type"] == "ABANDONED_OBJECT":

                severity = "HIGH"
                threat = "HIGH"

                event["severity"] = severity
                event["zone"] = "SAFE"

                add_event({
                    "type": "ABANDONED_OBJECT",
                    "zone": "SAFE",
                    "severity": severity,
                    "duration": event.get("duration", 0)
                })

            if alert:

                print(f"[ALERT] {alert['level']} : {alert['message']}")

                level = alert["level"]
                message = alert["message"]

                if level == "CRITICAL":
                    color = (0, 0, 255)

                elif level == "WARNING":
                    color = (0, 165, 255)

                else:
                    color = (0, 255, 0)

                cv2.rectangle(
                    annotated_frame,
                    (0, 0),
                    (640, 45),
                    color,
                    -1
                )

                cv2.putText(
                    annotated_frame,
                    f"{level}: {message}",
                    (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2
                )

            if (
                event["type"] in [
                    "LOITERING",
                    "FALL_DETECTED",
                    "ABANDONED_OBJECT",
                    "WEAPON_DETECTED"
                ]
                or event["zone"] == "RESTRICTED"
                or event["severity"] == "HIGH"
            ):

                evidence_manager.save(
                   annotated_frame,
                   event["type"],
                    track_id
                                 )

            # ==========================
            # Draw Track IDs + Threat
            # ==========================

            for result in results:

                if result.boxes is None:
                    continue

                for box in result.boxes:

                    if int(box.cls[0]) != 0:
                        continue

                    if box.id is None:
                        continue

                    track_id = int(box.id[0])

                    coords = box.xyxy[0]

                    if hasattr(coords, "tolist"):
                        x1, y1, x2, y2 = map(int, coords.tolist())
                    else:
                        x1, y1, x2, y2 = map(int, coords)

                    zone = person_locations.get(track_id, "SAFE")

                    duration = int(
                        memory_manager.get_duration(track_id)
                    )

                    cv2.putText(
                        annotated_frame,
                        f"ID:{track_id}",
                        (x1, y1 - 35),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255,255,255),
                        2
                    )

                    cv2.putText(
                        annotated_frame,
                        zone,
                        (x1, y1 - 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0,255,255),
                        2
                    )

                    cv2.putText(
                        annotated_frame,
                        f"{duration}s",
                        (x1, y2 + 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0,255,0),
                        2
                    )

                    if zone == "RESTRICTED":

                        cv2.rectangle(
                            annotated_frame,
                            (x1, y1),
                            (x2, y2),
                            (0, 0, 255),
                            3
                        )

                    elif zone == "ENTRY":

                        cv2.rectangle(
                            annotated_frame,
                            (x1, y1),
                            (x2, y2),
                            (0, 255, 255),
                            2
                        )

                    else:

                        cv2.rectangle(
                        annotated_frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2
                    )

        # ==========================
        # Threat Banner
        # ==========================

        threat_color = (0,255,0)

        if threat == "MEDIUM":
            threat_color = (0,255,255)

        elif threat == "HIGH":
            threat_color = (0,0,255)

        cv2.putText(
            annotated_frame,
            f"THREAT: {threat}",
            (15, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            threat_color,
            3
        )

        # ==========================
        # Dashboard Overlay
        # ==========================

        cv2.putText(
            annotated_frame,
            f"Persons: {person_count}",
            (15, 105),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255,255,255),
            2
        )

        cv2.putText(
            annotated_frame,
            f"Vehicles: {vehicle_count}",
            (15, 135),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255,255,255),
            2
        )

        cv2.putText(
            annotated_frame,
            f"FPS: {fps}",
            (15, 165),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255,255,255),
            2
        )

        cv2.putText(
            annotated_frame,
            f"Entered: {people_counter.entered}",
            (420, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.putText(
            annotated_frame,
            f"Exited: {people_counter.exited}",
            (420, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        cv2.putText(
            annotated_frame,
            f"Inside: {people_counter.inside()}",
            (420, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )

        set_frame(annotated_frame)

        cv2.imshow(
            "SentinelX Heatmap",
            heatmap.render()
        )

        cv2.waitKey(1)

        if hasattr(memory_manager, "cleanup"):
            memory_manager.cleanup()

        print("====================")
        print("Person Count:", person_count)
        print("Vehicle Count:", vehicle_count)
        print("Threat:", threat)
        print("FPS:", fps)
        print("====================")

        update_stats(
            persons=person_count,
            vehicles=vehicle_count,
            threat=threat,
            fps=fps
        )

        time.sleep(0.01)

    camera.release()