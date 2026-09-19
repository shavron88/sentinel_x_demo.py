import cv2
import time
from datetime import datetime

from database.db import save_event
from camera.camera_manager import CameraManager
from ai.inference import YOLOInferenceEngine
from config import MODEL_PATH

from events.event_manager import EventManager
from events.memory_manager import MemoryManager
from events.zone_manager import ZoneManager

from alerts.intelligence_engine import IntelligenceEngine
from alerts.alert_manager import AlertManager

from evidence.evidence_manager import EvidenceManager
from dashboard.timeline import add_incident

from dashboard.store import add_event, update_stats
from dashboard.stream import set_frame, get_frame_drops, get_stream_fps
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

    from config import FRAME_SKIP, VIDEO_FRAME_SKIP

    frame_counters = {}
    fps_trackers = {}
    frame_drops = 0
    last_drop_log = 0

    camera.start_video_watcher()

    try:
        while True:
            pipelines = camera.pipelines
            if not pipelines:
                now = time.time()
                if now - last_drop_log >= 5.0:
                    print("[WARNING] No camera pipelines available. Waiting...")
                    last_drop_log = now
                time.sleep(0.05)
                continue

            for cam_name, pipeline in pipelines.items():
                if not pipeline.is_running or pipeline.engine is None:
                    continue

                person_count = 0
                vehicle_count = 0
                person_locations = {}
                events = []

                frame = pipeline.get_frame()
                if frame is None:
                    frame_drops += 1
                    continue

                frame_counters[cam_name] = frame_counters.get(cam_name, 0) + 1
                frame_idx = frame_counters[cam_name]
                is_video_evidence = cam_name.startswith("Evidence_")
                skip = VIDEO_FRAME_SKIP if is_video_evidence else FRAME_SKIP
                should_infer = (frame_idx % skip == 0)

                h, w = frame.shape[:2]
                clean_frame = frame.copy()

                if should_infer:
                    preprocessor = getattr(pipeline, 'preprocessor', None)
                    if preprocessor is not None and not is_video_evidence:
                        frame = preprocessor.process(frame)

                    infer_w, infer_h = 320, 320
                    resized = cv2.resize(frame, (infer_w, infer_h))
                    result = pipeline.engine.infer_frame(resized) or {}
                    detections = result.get("detections", [])

                    scale_x = w / infer_w
                    scale_y = h / infer_h

                    for det in detections:
                        cls_id = det["class_id"]
                        track_id = det.get("track_id")
                        x1, y1, x2, y2 = det["bbox"]
                        cx = ((x1 + x2) / 2) / infer_h
                        cy = ((y1 + y2) / 2) / infer_w

                        if cls_id == 0:
                            person_count += 1
                            if track_id is None:
                                continue

                            pipeline.people_counter.update(track_id, cy)
                            pipeline.heatmap.update(cx * w, cy * h)

                            line_event = pipeline.line_detector.update(track_id, cy)
                            if line_event:
                                events.append(line_event)

                            zone = pipeline.zone_manager.get_zone(cx, cy)
                            person_locations[track_id] = zone

                        elif cls_id in VEHICLE_CLASSES:
                            vehicle_count += 1

                    for det in detections:
                        if det["class_id"] == 0 and det.get("track_id") is not None:
                            x1, y1, x2, y2 = [int(v * scale_x) if i % 2 == 0 else int(v * scale_y) for i, v in enumerate(det["bbox"])]
                            zone = person_locations.get(det["track_id"], "SAFE")
                            box_color = (0, 0, 255) if zone == "RESTRICTED" else ((0, 255, 255) if zone == "ENTRY" else (0, 255, 0))
                            thickness = 3 if zone == "RESTRICTED" else 2
                            cv2.rectangle(clean_frame, (x1, y1), (x2, y2), box_color, thickness)
                            cv2.putText(clean_frame, f"ID:{det['track_id']}", (x1, max(y1 - 10, 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                    for det in detections:
                        if det["class_id"] not in VEHICLE_CLASSES:
                            continue
                        x1, y1, x2, y2 = [int(v * scale_x) if i % 2 == 0 else int(v * scale_y) for i, v in enumerate(det["bbox"])]
                        cv2.rectangle(clean_frame, (x1, y1), (x2, y2), (255, 255, 0), 2)

                    if should_infer:
                        crowd_event = pipeline.crowd_detector.detect(person_count)
                        if crowd_event:
                            events.append(crowd_event)

                        detector_events = pipeline.event_manager.process(detections)
                        if detector_events:
                            events.extend(detector_events)

                        abandoned_events = pipeline.abandoned_detector.update(detections)
                        if abandoned_events:
                            events.extend(abandoned_events)

                        fall_events = pipeline.fall_detector.detect(detections)
                        if fall_events:
                            events.extend(fall_events)

                        weapon_events = pipeline.weapon_detector.detect(detections)
                        if weapon_events:
                            events.extend(weapon_events)

                now = time.time()
                if cam_name not in fps_trackers:
                    fps_trackers[cam_name] = {"last_time": now, "count": 1}
                else:
                    fps_trackers[cam_name]["count"] += 1
                    elapsed = now - fps_trackers[cam_name]["last_time"]
                    if elapsed >= 1.0:
                        fps_trackers[cam_name]["fps"] = int(fps_trackers[cam_name]["count"] / elapsed)
                        fps_trackers[cam_name]["last_time"] = now
                        fps_trackers[cam_name]["count"] = 1
                fps = fps_trackers.get(cam_name, {}).get("fps", 0)

                overall_threat = "LOW"

                for event in events:
                    track_id = event.get("track_id")

                    if track_id is None:
                        zone = "SAFE"
                        duration = 0
                    else:
                        zone = person_locations.get(track_id, "SAFE")
                        pipeline.memory_manager.update(track_id, zone)
                        duration = pipeline.memory_manager.get_duration(track_id)

                        if pipeline.memory_manager.check_loitering(track_id):
                            event["type"] = "LOITERING"

                        if pipeline.memory_manager.moved_to_restricted(track_id):
                            print(f"[INTRUSION] Person {track_id} entered RESTRICTED zone")

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

                    event_id = save_event(
                        event_type=event["type"],
                        severity=severity,
                        camera=cam_name,
                        zone=zone,
                        confidence=event.get("confidence", 0.0),
                        duration=int(duration),
                        track_id=track_id if track_id is not None else -1,
                        metadata={"duration": int(duration)}
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

                    alert = alert_manager.process(event)
                    if alert:
                        print(f"[ALERT] {alert['level']} : {alert['message']}")

                    if (
                        event["type"] in ["LOITERING", "FALL_DETECTED", "ABANDONED_OBJECT", "WEAPON_DETECTED"]
                        or event["zone"] == "RESTRICTED"
                        or event["severity"] == "HIGH"
                    ):
                        evidence_manager.save(
                            clean_frame,
                            event["type"],
                            track_id if track_id is not None else -1,
                            event_id=event_id,
                            camera=cam_name
                        )

                set_frame(clean_frame, camera_name=cam_name)

                if hasattr(pipeline.memory_manager, "cleanup"):
                    pipeline.memory_manager.cleanup()

                update_stats(
                    persons=person_count,
                    vehicles=vehicle_count,
                    threat=overall_threat,
                    fps=fps
                )

            time.sleep(0.01)

    finally:
        if camera:
            camera.release()
        print("========== SENTINELX ENGINE STOPPED SAFELY ==========")
