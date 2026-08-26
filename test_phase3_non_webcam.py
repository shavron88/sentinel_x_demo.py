"""Phase 3 — Non-webcam validation tests"""
import sys, os, time, cv2, numpy as np, sqlite3, json, tempfile, shutil
from datetime import datetime
sys.path.insert(0, os.path.abspath('.'))

from events.crowd_detector import CrowdDetector
from events.abandoned_object import AbandonedObjectDetector
from events.fall_detector import FallDetector
from events.weapon_detector import WeaponDetector
from events.line_crossing import LineCrossingDetector
from events.people_counter import PeopleCounter
from events.memory_manager import MemoryManager
from events.event_manager import EventManager
from alerts.intelligence_engine import IntelligenceEngine
from alerts.alert_manager import AlertManager
from evidence.evidence_manager import EvidenceManager, save as evidence_save
from database import db as db_module
from dashboard.store import add_event, get_events, get_stats
from dashboard.timeline import add_incident, get_timeline

def run_tests():
    tmpdir = tempfile.mkdtemp(prefix="sentinelx_phase3_")
    DB_PATH = os.path.join(tmpdir, "test.db")
    EVIDENCE_DIR = os.path.join(tmpdir, "evidence")
    
    db_module.DB_PATH = DB_PATH
    db_module.init_db()
    
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    
    from evidence import evidence_manager as em_module
    em_module.DB_PATH = DB_PATH
    em_module.EVIDENCE_DIR = EVIDENCE_DIR
    
    def get_connection():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    def save_event(event_type, severity="LOW", camera="Unknown", zone="General Area", confidence=0.0, duration=0.0, metadata=None, screenshot="", track_id=-1):
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                    INSERT INTO events (timestamp, event_type, severity, camera, zone, track_id, confidence, duration, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (timestamp, event_type, severity, camera, zone, track_id, confidence, duration, json.dumps(metadata) if metadata else None))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error saving event: {e}")
            return None
    
    def get_all_events(limit=50):
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
    
    def get_all_evidence(limit=100):
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT e.*, ev.event_type, ev.severity, ev.zone, ev.confidence as event_confidence
                    FROM evidence e
                    LEFT JOIN events ev ON e.event_id = ev.id
                    ORDER BY e.timestamp DESC
                    LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    item = dict(row)
                    metadata = item.get("metadata")
                    meta = {}
                    if metadata:
                        try:
                            meta = json.loads(metadata)
                        except (json.JSONDecodeError, TypeError):
                            pass
                    image_path = item.get("image_path", "")
                    if image_path and not image_path.startswith("/"):
                        image_path = "/" + image_path.lstrip("/")
                    results.append({
                        "id": item.get("id"),
                        "event_id": item.get("event_id"),
                        "image": image_path,
                        "event": meta.get("event_type", item.get("event_type", "")),
                        "camera": item.get("camera", meta.get("camera", "")),
                        "location": item.get("zone", meta.get("location", "")),
                        "time": item.get("timestamp", ""),
                        "trackingId": meta.get("tracking_id", ""),
                        "confidence": float(item.get("event_confidence", meta.get("confidence", 0))),
                        "severity": item.get("severity", "LOW"),
                        "favorite": meta.get("favorite", False),
                        "description": meta.get("ai_description", ""),
                        "ocr_text": meta.get("ocr_text", ""),
                        "tags": meta.get("tags", []),
                        "similar_ids": meta.get("similar_ids", []),
                        "metadata": meta,
                    })
                return results
        except Exception as ex:
            print(f"Error fetching evidence: {ex}")
            return []
    
    def reset_db():
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM events")
            cursor.execute("DELETE FROM evidence")
            conn.commit()
    
    print("========== SENTINEL-X PHASE 3 VALIDATION ==========")
    
    # 1. Crowd Detection
    print("\n=== 1. Crowd Detection ===")
    detector = CrowdDetector(threshold=3, cooldown_seconds=0.5)
    e1 = detector.detect(3)
    assert e1 is not None and e1["type"] == "CROWD_DETECTED"
    e2 = detector.detect(3)
    assert e2 is None
    time.sleep(0.6)
    e3 = detector.detect(3)
    assert e3 is not None
    e4 = detector.detect(2)
    assert e4 is None
    print("PASS")
    
    # 2. Abandoned Object
    print("\n=== 2. Abandoned Object Detection ===")
    detector = AbandonedObjectDetector()
    detector.abandon_time = 0.5
    dets = [{"class_id": 24, "track_id": 1, "bbox": [100.0, 100.0, 120.0, 120.0]}]
    e1 = detector.update(dets)
    assert len(e1) == 0
    time.sleep(0.6)
    e2 = detector.update(dets)
    assert len(e2) == 1 and e2[0]["type"] == "ABANDONED_OBJECT"
    print("PASS")
    
    # 3. Fall Detection
    print("\n=== 3. Fall Detection ===")
    detector = FallDetector(cooldown_seconds=1.0)
    dets = [{"class_id": 0, "track_id": 5, "bbox": [100.0, 100.0, 200.0, 150.0]}]
    e1 = detector.detect(dets)
    assert len(e1) == 1 and e1[0]["type"] == "FALL_DETECTED"
    e2 = detector.detect(dets)
    assert len(e2) == 0
    time.sleep(1.1)
    e3 = detector.detect(dets)
    assert len(e3) == 1
    print("PASS")
    
    # 4. Weapon Detection
    print("\n=== 4. Weapon Detection ===")
    detector = WeaponDetector(cooldown_seconds=1.0)
    dets = [{"label": "knife", "track_id": 10, "bbox": [100.0, 100.0, 200.0, 150.0]}]
    e1 = detector.detect(dets)
    assert len(e1) == 1 and e1[0]["type"] == "WEAPON_DETECTED"
    e2 = detector.detect(dets)
    assert len(e2) == 0
    time.sleep(1.1)
    e3 = detector.detect(dets)
    assert len(e3) == 1
    print("PASS")
    
    # 5. Line Crossing
    print("\n=== 5. Line Crossing ===")
    detector = LineCrossingDetector()
    e1 = detector.update(1, 0.5)
    assert e1 is None
    e2 = detector.update(1, 0.7)
    assert e2 is not None and e2["type"] == "LINE_CROSSING"
    print("PASS")
    
    # 6. Event State Persistence
    print("\n=== 6. Event State Persistence ===")
    mem = MemoryManager()
    line = LineCrossingDetector()
    people = PeopleCounter()
    for i in range(5):
        mem.update(1, "SAFE")
        line.update(1, 0.5)
        people.update(1, 0.5)
    assert mem.get_duration(1) > 0
    print("PASS")
    
    # 7. Severity Calculation
    print("\n=== 7. Severity Calculation ===")
    engine = IntelligenceEngine()
    assert engine.evaluate({"type": "LOITERING"}, "SAFE", 35, 1) == "HIGH"
    assert engine.evaluate({"type": "FALL_DETECTED"}, "SAFE", 0, 1) == "HIGH"
    assert engine.evaluate({"type": "WEAPON_DETECTED"}, "SAFE", 0, 1) == "HIGH"
    assert engine.evaluate({"type": "ABANDONED_OBJECT"}, "SAFE", 0, 1) == "HIGH"
    assert engine.evaluate({"type": "PERSON_DETECTED"}, "RESTRICTED", 0, 1) == "HIGH"
    assert engine.evaluate({"type": "PERSON_DETECTED"}, "SAFE", 35, 1) == "MEDIUM"
    assert engine.evaluate({"type": "PERSON_DETECTED"}, "SAFE", 10, 6) == "MEDIUM"
    assert engine.evaluate({"type": "PERSON_DETECTED"}, "SAFE", 5, 1) == "LOW"
    print("PASS")
    
    # 8. Alert Generation
    print("\n=== 8. Alert Generation ===")
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
        assert alert["level"] == expected_level, f"Expected {expected_level}, got {alert['level']}"
        assert expected_msg in alert["message"], f"Expected '{expected_msg}' in message"
    print("PASS")
    
    # 9. Evidence-Event Linking
    print("\n=== 9. Evidence-Event Linking ===")
    frame = np.full((360, 640, 3), (100, 100, 100), dtype=np.uint8)
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
    assert event_id is not None and event_id > 0
    evidence_id = evidence_save(frame, "PERSON_DETECTED", track_id=42, event_id=event_id, camera="Camera-1")
    assert evidence_id is not None and evidence_id > 0
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evidence WHERE id = ?", (evidence_id,))
        row = cursor.fetchone()
        assert row is not None
        assert row["event_id"] == event_id, f"Expected {event_id}, got {row['event_id']}"
    all_evidence = get_all_evidence()
    assert len(all_evidence) == 1
    assert all_evidence[0]["event_id"] == event_id
    print("PASS")
    
    # 10. Database Persistence
    print("\n=== 10. Database Persistence ===")
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
    track_ids = [ev["track_id"] for ev in events]
    assert sorted(track_ids) == [1, 2, 3], f"Expected track_ids [1,2,3], got {sorted(track_ids)}"
    for ev in events:
        assert ev["event_type"] == "PERSON_DETECTED"
        assert ev["camera"].startswith("Camera-")
    print("PASS")
    
    # 11. Dashboard Visibility
    print("\n=== 11. Dashboard Visibility ===")
    add_event({"type": "TEST_EVENT", "zone": "SAFE", "severity": "LOW"})
    add_incident({"time": "12:00:00", "event": "TEST_EVENT", "zone": "SAFE", "severity": "LOW"})
    events = get_events(limit=10)
    assert len(events) >= 1
    timeline = get_timeline()
    assert len(timeline) >= 1
    assert timeline[0]["event"] == "TEST_EVENT"
    stats = get_stats()
    assert "persons" in stats
    print("PASS")
    
    # 12. Structured Detection Compatibility
    print("\n=== 12. Structured Detection Compatibility ===")
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
    assert all(e["type"] == "ABANDONED_OBJECT" for e in events)
    fall = FallDetector()
    events = fall.detect(sample_detections)
    assert len(events) == 2, f"Expected 2 falls, got {len(events)}"
    track_ids = [e["track_id"] for e in events]
    assert sorted(track_ids) == [2, 5], f"Expected track_ids [2,5], got {sorted(track_ids)}"
    weapon = WeaponDetector()
    events = weapon.detect(sample_detections)
    assert len(events) == 0
    crowd = CrowdDetector(threshold=2)
    event = crowd.detect(3)
    assert event is not None and event["type"] == "CROWD_DETECTED"
    line = LineCrossingDetector()
    e1 = line.update(1, 0.5)
    e2 = line.update(1, 0.7)
    assert e2 is not None and e2["type"] == "LINE_CROSSING"
    print("PASS")
    
    shutil.rmtree(tmpdir, ignore_errors=True)
    print("\n========== ALL NON-WEBCAM TESTS PASSED ==========")

if __name__ == "__main__":
    run_tests()
