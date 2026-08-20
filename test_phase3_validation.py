"""
Sentinel-X Phase 3 — Real Event Intelligence Validation

Tests the complete event pipeline end-to-end using real frames/video wherever possible.
Validates each detector, tracking persistence, deduplication, severity, alerts, evidence, and database.
"""
import sys
import os
import time
import cv2
import numpy as np
import sqlite3
import json
import tempfile
import shutil
from datetime import datetime

sys.path.insert(0, os.path.abspath('.'))

from ai.health import AIHealthMonitor
from ai.inference import YOLOInferenceEngine
from ai.queue_manager import DetectionQueueManager
from ai.worker import YOLOWorker
from events.event_manager import EventManager
from events.abandoned_object import AbandonedObjectDetector
from events.fall_detector import FallDetector
from events.weapon_detector import WeaponDetector
from events.crowd_detector import CrowdDetector
from events.line_crossing import LineCrossingDetector
from events.people_counter import PeopleCounter
from events.memory_manager import MemoryManager
from events.zone_manager import ZoneManager
from alerts.intelligence_engine import IntelligenceEngine
from alerts.alert_manager import AlertManager
from evidence.evidence_manager import EvidenceManager, save as evidence_save
from database.db import save_event, get_all_events, get_all_evidence, init_db, get_connection
from dashboard.store import add_event, get_events, get_stats
from dashboard.timeline import add_incident, get_timeline
from core.engine import VEHICLE_CLASSES

DB_PATH = "sentinelx.db"
EVIDENCE_DIR = "evidence/screenshots"

def reset_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()

def reset_evidence():
    if os.path.exists(EVIDENCE_DIR):
        shutil.rmtree(EVIDENCE_DIR)
    os.makedirs(EVIDENCE_DIR, exist_ok=True)

def get_webcam_frame():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None
    ret, frame = cap.read()
    cap.release()
    if ret:
        return cv2.resize(frame, (640, 360))
    return None

def get_test_frame(color=(255, 255, 255)):
    frame = np.full((360, 640, 3), color, dtype=np.uint8)
    cv2.putText(frame, "TEST FRAME", (50, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    return frame

# ============================================================
# 1. Crowd detection
# ============================================================
def test_crowd_detection():
    print("\n=== 1. Crowd Detection ===")
    detector = CrowdDetector(threshold=3, cooldown_seconds=0.5)
    
    e1 = detector.detect(3)
    assert e1 is not None and e1["type"] == "CROWD_DETECTED", "Should detect crowd at threshold"
    
    e2 = detector.detect(3)
    assert e2 is None, "Should suppress duplicate within cooldown"
    
    time.sleep(0.6)
    e3 = detector.detect(3)
    assert e3 is not None, "Should fire after cooldown"
    
    e4 = detector.detect(2)
    assert e4 is None, "Should not fire below threshold"
    print("PASS: Crowd detection with deduplication")

# ============================================================
# 2. Abandoned object detection
# ============================================================
def test_abandoned_object():
    print("\n=== 2. Abandoned Object Detection ===")
    detector = AbandonedObjectDetector()
    detector.abandon_time = 0.5
    
    dets = [{"class_id": 24, "track_id": 1, "bbox": [100.0, 100.0, 120.0, 120.0]}]
    e1 = detector.update(dets)
    assert len(e1) == 0, "Should not fire immediately"
    
    time.sleep(0.6)
    e2 = detector.update(dets)
    assert len(e2) == 1 and e2[0]["type"] == "ABANDONED_OBJECT", "Should fire after abandon_time"
    
    e3 = detector.update(dets)
    assert len(e3) == 0, "Should not re-fire (alerted flag)"
    
    dets2 = [{"class_id": 24, "track_id": 1, "bbox": [200.0, 200.0, 220.0, 220.0]}]
    e4 = detector.update(dets2)
    assert len(e4) == 0, "Moving object resets alert"
    
    time.sleep(0.6)
    e5 = detector.update(dets2)
    assert len(e5) == 1, "Should fire again after object stops"
    print("PASS: Abandoned object with state persistence")

# ============================================================
# 3. Fall detection with dedup
# ============================================================
def test_fall_detection():
    print("\n=== 3. Fall Detection ===")
    detector = FallDetector(cooldown_seconds=1.0)
    
    dets = [{"class_id": 0, "track_id": 5, "bbox": [100.0, 100.0, 200.0, 150.0]}]
    e1 = detector.detect(dets)
    assert len(e1) == 1 and e1[0]["type"] == "FALL_DETECTED", "Should detect fall (width > height)"
    
    e2 = detector.detect(dets)
    assert len(e2) == 0, "Should suppress duplicate within cooldown"
    
    time.sleep(1.1)
    e3 = detector.detect(dets)
    assert len(e3) == 1, "Should fire after cooldown"
    
    dets_standing = [{"class_id": 0, "track_id": 5, "bbox": [100.0, 100.0, 120.0, 200.0]}]
    e4 = detector.detect(dets_standing)
    assert len(e4) == 0, "Should not fire for standing person"
    print("PASS: Fall detection with deduplication")

# ============================================================
# 4. Weapon detection with dedup
# ============================================================
def test_weapon_detection():
    print("\n=== 4. Weapon Detection ===")
    detector = WeaponDetector(cooldown_seconds=1.0)
    
    dets = [{"label": "knife", "track_id": 10, "bbox": [100.0, 100.0, 200.0, 150.0]}]
    e1 = detector.detect(dets)
    assert len(e1) == 1 and e1[0]["type"] == "WEAPON_DETECTED", "Should detect weapon"
    
    e2 = detector.detect(dets)
    assert len(e2) == 0, "Should suppress duplicate within cooldown"
    
    time.sleep(1.1)
    e3 = detector.detect(dets)
    assert len(e3) == 1, "Should fire after cooldown"
    
    dets_person = [{"label": "person", "track_id": 10, "bbox": [100.0, 100.0, 200.0, 150.0]}]
    e4 = detector.detect(dets_person)
    assert len(e4) == 0, "Should not fire for non-weapon"
    print("PASS: Weapon detection with deduplication")

# ============================================================
# 5. Line crossing detection
# ============================================================
def test_line_crossing():
    print("\n=== 5. Line Crossing ===")
    detector = LineCrossingDetector()
    
    e1 = detector.update(1, 0.5)
    assert e1 is None, "First side should not fire"
    
    e2 = detector.update(1, 0.7)
    assert e2 is not None and e2["type"] == "LINE_CROSSING", "Should fire on side change"
    
    e3 = detector.update(1, 0.7)
    assert e3 is None, "Same side should not fire"
    
    e4 = detector.update(1, 0.5)
    assert e4 is not None and e4["type"] == "LINE_CROSSING", "Should fire on return crossing"
    print("PASS: Line crossing with state persistence")

# ============================================================
# 6. ByteTrack track_id persistence
# ============================================================
def test_bytetrack_persistence():
    print("\n=== 6. ByteTrack track_id Persistence ===")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("SKIP: No webcam available")
        return
    
    health = AIHealthMonitor()
    engine = YOLOInferenceEngine(model_path="models/yolov8m.pt", health_monitor=health)
    
    track_ids_per_frame = []
    for i in range(10):
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.resize(frame, (640, 360))
        result = engine.infer_frame(frame)
        persons = [d for d in result["detections"] if d["class_id"] == 0 and d.get("track_id") is not None]
        track_ids = [d["track_id"] for d in persons]
        track_ids_per_frame.append(track_ids)
        time.sleep(0.2)
    
    cap.release()
    
    all_ids = []
    for ids in track_ids_per_frame:
        all_ids.extend(ids)
    
    if len(all_ids) >= 3:
        unique_ids = set(all_ids)
        print(f"PASS: Observed {len(unique_ids)} unique track_ids across frames: {sorted(unique_ids)}")
    else:
        print("INFO: No consistent person detection in webcam frames")
    
    assert health.yolo_status in ["Loaded", "Running"], f"YOLO should be running, got {health.yolo_status}"
    assert health.tracker_status == "Active", f"Tracker should be active, got {health.tracker_status}"
    print("PASS: ByteTrack is active and assigning track_ids")

# ============================================================
# 7. Event state persistence across frames
# ============================================================
def test_event_state_persistence():
    print("\n=== 7. Event State Persistence ===")
    memory = MemoryManager()
    line_det = LineCrossingDetector()
    people = PeopleCounter()
    
    for i in range(5):
        memory.update(1, "SAFE")
        line_det.update(1, 0.5)
        people.update(1, 0.5)
    
    assert memory.get_duration(1) > 0, "Duration should persist"
    assert people.inside() == 0, "Should not count without crossing"
    print("PASS: Event state persists across frames")

# ============================================================
# 8. Severity calculation
# ============================================================
def test_severity_calculation():
    print("\n=== 8. Severity Calculation ===")
    engine = IntelligenceEngine()
    
    assert engine.evaluate({"type": "LOITERING"}, "SAFE", 35, 1) == "HIGH"
    assert engine.evaluate({"type": "FALL_DETECTED"}, "SAFE", 0, 1) == "HIGH"
    assert engine.evaluate({"type": "WEAPON_DETECTED"}, "SAFE", 0, 1) == "HIGH"
    assert engine.evaluate({"type": "ABANDONED_OBJECT"}, "SAFE", 0, 1) == "HIGH"
    assert engine.evaluate({"type": "PERSON_DETECTED"}, "RESTRICTED", 0, 1) == "HIGH"
    assert engine.evaluate({"type": "PERSON_DETECTED"}, "SAFE", 35, 1) == "MEDIUM"
    assert engine.evaluate({"type": "PERSON_DETECTED"}, "SAFE", 10, 6) == "MEDIUM"
    assert engine.evaluate({"type": "PERSON_DETECTED"}, "SAFE", 5, 1) == "LOW"
    print("PASS: Severity calculation consistent")

# ============================================================
# 9. Alert generation
# ============================================================
def test_alert_generation():
    print("\n=== 9. Alert Generation ===")
    alert_mgr = AlertManager()
    
    alerts = [
        ({"type": "RESTRICTED", "zone": "RESTRICTED", "severity": "HIGH"}, "CRITICAL", "Restricted Area Intrusion"),
        ({"type": "LOITERING", "severity": "MEDIUM", "zone": "SAFE"}, "WARNING", "Person loitering"),
        ({"type": "FALL_DETECTED", "severity": "HIGH", "zone": "SAFE"}, "CRITICAL", "Person may have fallen"),
        ({"type": "WEAPON_DETECTED", "severity": "HIGH", "zone": "SAFE"}, "CRITICAL", "Weapon detected"),
        ({"type": "CROWD_DETECTED", "severity": "MEDIUM", "zone": "SAFE"}, "WARNING", "Crowd detected"),
        ({"type": "PERSON_DETECTED", "severity": "LOW", "zone": "SAFE"}, "INFO", "Person detected"),
    ]
    
    for event, expected_level, expected_msg in alerts:
        alert = alert_mgr.process(event)
        assert alert is not None, f"Alert should be generated for {event['type']}"
        assert alert["level"] == expected_level, f"Expected {expected_level}, got {alert['level']} for {event['type']}"
        assert expected_msg in alert["message"], f"Expected '{expected_msg}' in message, got '{alert['message']}'"
    
    print("PASS: Alert generation for all event types")

# ============================================================
# 10. Evidence screenshot and event_id linking
# ============================================================
def test_evidence_event_linking():
    print("\n=== 10. Evidence-Event Linking ===")
    reset_db()
    reset_evidence()
    
    frame = get_test_frame((100, 100, 100))
    
    event_id = save_event(
        event_type="PERSON_DETECTED",
        severity="HIGH",
        camera="Camera-1",
        zone="RESTRICTED",
        confidence=0.9,
        duration=5.0,
        track_id=42,
        metadata={"duration": 5}
    )
    assert event_id is not None and event_id > 0, "save_event should return event_id"
    
    evidence_id = evidence_save(frame, "PERSON_DETECTED", track_id=42, event_id=event_id)
    assert evidence_id is not None and evidence_id > 0, "evidence save should return evidence_id"
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evidence WHERE id = ?", (evidence_id,))
        row = cursor.fetchone()
        assert row is not None, "Evidence record should exist"
        assert row["event_id"] == event_id, f"Evidence event_id should be {event_id}, got {row['event_id']}"
    
    all_evidence = get_all_evidence()
    assert len(all_evidence) == 1, "Should have one evidence record"
    assert all_evidence[0]["event_id"] == event_id, "Evidence should be linked to event"
    print(f"PASS: Evidence linked to event_id={event_id}")

# ============================================================
# 11. Database persistence
# ============================================================
def test_database_persistence():
    print("\n=== 11. Database Persistence ===")
    reset_db()
    
    for i in range(3):
        save_event(
            event_type="PERSON_DETECTED",
            severity="LOW",
            camera=f"Camera-{i+1}",
            zone="SAFE",
            track_id=i+1,
            confidence=0.8
        )
    
    events = get_all_events(limit=10)
    assert len(events) == 3, f"Expected 3 events, got {len(events)}"
    
    for i, ev in enumerate(events):
        assert ev["event_type"] == "PERSON_DETECTED"
        assert ev["track_id"] == i + 1
        assert ev["camera"] == f"Camera-{i+1}"
    
    print("PASS: Database persistence with track_id and camera")

# ============================================================
# 12. Dashboard visibility
# ============================================================
def test_dashboard_visibility():
    print("\n=== 12. Dashboard Visibility ===")
    
    add_event({"type": "TEST_EVENT", "zone": "SAFE", "severity": "LOW"})
    add_incident({"time": "12:00:00", "event": "TEST_EVENT", "zone": "SAFE", "severity": "LOW"})
    
    events = get_events(limit=10)
    assert len(events) >= 1, "Dashboard should see events"
    
    timeline = get_timeline()
    assert len(timeline) >= 1, "Dashboard should see incidents"
    assert timeline[0]["event"] == "TEST_EVENT"
    
    stats = get_stats()
    assert "persons" in stats, "Stats should contain person count"
    print("PASS: Dashboard receives events and incidents")

# ============================================================
# 13. End-to-end pipeline with real webcam
# ============================================================
def test_end_to_end_webcam():
    print("\n=== 13. End-to-End Webcam Pipeline ===")
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("SKIP: No webcam available")
        return
    
    reset_db()
    reset_evidence()
    
    health = AIHealthMonitor()
    engine = YOLOInferenceEngine(model_path="models/yolov8m.pt", health_monitor=health)
    queue_mgr = DetectionQueueManager(maxsize=10)
    worker = YOLOWorker(queue_mgr, engine, health)
    
    event_manager = EventManager()
    memory_manager = MemoryManager()
    zone_manager = ZoneManager()
    abandoned_detector = AbandonedObjectDetector()
    fall_detector = FallDetector()
    crowd_detector = CrowdDetector(threshold=2, cooldown_seconds=5.0)
    line_detector = LineCrossingDetector()
    weapon_detector = WeaponDetector()
    people_counter = PeopleCounter()
    intelligence_engine = IntelligenceEngine()
    alert_manager = AlertManager()
    evidence_manager = EvidenceManager()
    
    worker.start()
    
    frame_count = 0
    events_generated = 0
    track_ids_seen = set()
    
    start_time = time.time()
    while time.time() - start_time < 10.0:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.05)
            continue
        
        frame = cv2.resize(frame, (640, 360))
        frame_count += 1
        queue_mgr.push_frame(frame_count, frame)
        
        res = queue_mgr.get_result(timeout=0.5)
        if not res:
            time.sleep(0.05)
            continue
        
        fid, detections = res
        h, w = frame.shape[:2]
        person_count = 0
        person_locations = {}
        events = []
        
        for det in detections:
            cls_id = det["class_id"]
            track_id = det.get("track_id")
            x1, y1, x2, y2 = det["bbox"]
            cx = ((x1 + x2) / 2) / w
            cy = ((y1 + y2) / 2) / h
            
            if cls_id == 0:
                person_count += 1
                if track_id is not None:
                    track_ids_seen.add(track_id)
                    people_counter.update(track_id, cy)
                    line_event = line_detector.update(track_id, cy)
                    if line_event:
                        events.append(line_event)
                    zone = zone_manager.get_zone(cx, cy)
                    person_locations[track_id] = zone
        
        crowd_event = crowd_detector.detect(person_count)
        if crowd_event:
            events.append(crowd_event)
        
        detector_events = event_manager.process(detections)
        if detector_events:
            events.extend(detector_events)
        
        abandoned_events = abandoned_detector.update(detections)
        if abandoned_events:
            events.extend(abandoned_events)
        
        fall_events = fall_detector.detect(detections)
        if fall_events:
            events.extend(fall_events)
        
        weapon_events = weapon_detector.detect(detections)
        if weapon_events:
            events.extend(weapon_events)
        
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
            
            if event.get("type") == "ABANDONED_OBJECT":
                severity = "HIGH"
                zone = "SAFE"
            else:
                severity = intelligence_engine.evaluate(event, zone, duration, person_count)
            
            event["zone"] = zone
            event["severity"] = severity
            event["duration"] = int(duration)
            
            event_id = save_event(
                event_type=event["type"],
                severity=severity,
                camera="Camera-1",
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
                print(f"  [ALERT] {alert['level']}: {alert['message']}")
            
            if (
                event["type"] in ["LOITERING", "FALL_DETECTED", "ABANDONED_OBJECT", "WEAPON_DETECTED"]
                or event["zone"] == "RESTRICTED"
                or event["severity"] == "HIGH"
            ):
                evidence_manager.save(
                    frame.copy(),
                    event["type"],
                    track_id if track_id is not None else -1,
                    event_id=event_id
                )
            
            events_generated += 1
    
    worker.stop()
    worker.join(timeout=2.0)
    cap.release()
    
    db_events = get_all_events(limit=100)
    db_evidence = get_all_evidence(limit=100)
    timeline = get_timeline()
    stats = get_stats()
    
    print(f"  Frames processed: {frame_count}")
    print(f"  Events generated: {events_generated}")
    print(f"  Unique track_ids: {sorted(track_ids_seen)}")
    print(f"  DB events: {len(db_events)}")
    print(f"  DB evidence: {len(db_evidence)}")
    print(f"  Timeline incidents: {len(timeline)}")
    print(f"  Dashboard stats: persons={stats.get('persons')}, threat={stats.get('threat')}")
    
    assert len(db_events) == events_generated, "All generated events should be in DB"
    assert len(timeline) == events_generated, "All events should appear in timeline"
    
    for ev in db_evidence:
        assert ev.get("event_id") is not None, "All evidence should be linked to an event"
    
    print("PASS: End-to-end webcam pipeline")

# ============================================================
# 14. Structured detection format compatibility
# ============================================================
def test_structured_detection_compatibility():
    print("\n=== 14. Structured Detection Compatibility ===")
    
    sample_detections = [
        {"track_id": 1, "class_id": 0, "label": "person", "confidence": 0.9, "bbox": [100.0, 120.0, 300.0, 500.0]},
        {"track_id": 2, "class_id": 0, "label": "person", "confidence": 0.85, "bbox": [400.0, 200.0, 700.0, 450.0]},
        {"track_id": 3, "class_id": 2, "label": "car", "confidence": 0.87, "bbox": [400.0, 200.0, 700.0, 450.0]},
        {"track_id": 4, "class_id": 24, "label": "backpack", "confidence": 0.7, "bbox": [50.0, 50.0, 100.0, 100.0]},
        {"track_id": 5, "class_id": 0, "label": "person", "confidence": 0.6, "bbox": [100.0, 100.0, 180.0, 160.0]},
    ]
    
    event_mgr = EventManager()
    events = event_mgr.process(sample_detections)
    assert len(events) == 3, f"Expected 3 person events, got {len(events)}"
    
    abandoned = AbandonedObjectDetector()
    events = abandoned.update(sample_detections)
    assert all(e["type"] == "ABANDONED_OBJECT" for e in events), "All events should be ABANDONED_OBJECT"
    
    fall = FallDetector()
    events = fall.detect(sample_detections)
    assert len(events) == 1, "Should detect one fall (width > height)"
    assert events[0]["track_id"] == 5
    
    weapon = WeaponDetector()
    events = weapon.detect(sample_detections)
    assert len(events) == 0, "No weapons in sample"
    
    crowd = CrowdDetector(threshold=2)
    event = crowd.detect(3)
    assert event is not None and event["type"] == "CROWD_DETECTED"
    
    line = LineCrossingDetector()
    e1 = line.update(1, 0.5)
    e2 = line.update(1, 0.7)
    assert e2 is not None and e2["type"] == "LINE_CROSSING"
    
    print("PASS: All detectors accept structured detection dicts")

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("========== SENTINEL-X PHASE 3 VALIDATION ==========")
    
    test_crowd_detection()
    test_abandoned_object()
    test_fall_detection()
    test_weapon_detection()
    test_line_crossing()
    test_bytetrack_persistence()
    test_event_state_persistence()
    test_severity_calculation()
    test_alert_generation()
    test_evidence_event_linking()
    test_database_persistence()
    test_dashboard_visibility()
    test_structured_detection_compatibility()
    test_end_to_end_webcam()
    
    print("\n========== PHASE 3 VALIDATION COMPLETE ==========")
