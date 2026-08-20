"""Phase 3 — Synthetic event trigger test"""
import sys, os, time, cv2, numpy as np, sqlite3, json, tempfile, shutil
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
from database import db as db_module
from dashboard.store import add_event, get_events, get_stats
from dashboard.timeline import add_incident, get_timeline
from dashboard.stream import set_frame
from analytics.heatmap import Heatmap

def run_test():
    tmpdir = tempfile.mkdtemp(prefix="sentinelx_synthetic_")
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
        with get_connection() as conn:
            cursor = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO events (timestamp, event_type, severity, camera, zone, track_id, confidence, duration, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, event_type, severity, camera, zone, track_id, confidence, duration, json.dumps(metadata) if metadata else None))
            conn.commit()
            return cursor.lastrowid
    
    def get_all_events(limit=50):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_evidence(limit=100):
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
            return [dict(row) for row in rows]
    
    print("========== PHASE 3 SYNTHETIC EVENT TRIGGER TEST ==========")
    
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
    heatmap = Heatmap()
    
    worker.start()
    
    frame_count = 0
    events_generated = 0
    track_ids_seen = set()
    
    # Create a synthetic frame that will trigger events
    frame = np.full((360, 640, 3), (200, 200, 200), dtype=np.uint8)
    cv2.rectangle(frame, (100, 100), (200, 300), (0, 255, 0), -1)
    cv2.putText(frame, "PERSON", (110, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Inject synthetic detections directly into the pipeline
    synthetic_detections = [
        {"track_id": 1, "class_id": 0, "label": "person", "confidence": 0.9, "bbox": [100.0, 100.0, 200.0, 300.0]},
        {"track_id": 2, "class_id": 0, "label": "person", "confidence": 0.85, "bbox": [300.0, 100.0, 400.0, 300.0]},
        {"track_id": 3, "class_id": 0, "label": "person", "confidence": 0.8, "bbox": [500.0, 100.0, 600.0, 300.0]},
        {"track_id": 4, "class_id": 24, "label": "backpack", "confidence": 0.7, "bbox": [50.0, 50.0, 100.0, 100.0]},
        {"track_id": 5, "class_id": 0, "label": "person", "confidence": 0.6, "bbox": [100.0, 100.0, 180.0, 160.0]},
    ]
    
    h, w = frame.shape[:2]
    person_count = 0
    person_locations = {}
    events = []
    
    for det in synthetic_detections:
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
    
    detector_events = event_manager.process(synthetic_detections)
    if detector_events:
        events.extend(detector_events)
    
    abandoned_events = abandoned_detector.update(synthetic_detections)
    if abandoned_events:
        events.extend(abandoned_events)
    
    fall_events = fall_detector.detect(synthetic_detections)
    if fall_events:
        events.extend(fall_events)
    
    weapon_events = weapon_detector.detect(synthetic_detections)
    if weapon_events:
        events.extend(weapon_events)
    
    annotated_frame = frame.copy()
    annotated_frame = zone_manager.draw(annotated_frame)
    
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
                annotated_frame.copy(),
                event["type"],
                track_id if track_id is not None else -1,
                event_id=event_id,
                camera="Camera-1"
            )
        
        events_generated += 1
    
    for det in synthetic_detections:
        if det["class_id"] != 0 or det.get("track_id") is None:
            continue
        track_id = det["track_id"]
        x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
        zone = person_locations.get(track_id, "SAFE")
        duration = int(memory_manager.get_duration(track_id))
        cv2.putText(annotated_frame, f"ID:{track_id}", (x1, y1 - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(annotated_frame, zone, (x1, y1 - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(annotated_frame, f"{duration}s", (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        box_color = (0, 0, 255) if zone == "RESTRICTED" else ((0, 255, 255) if zone == "ENTRY" else (0, 255, 0))
        thickness = 3 if zone == "RESTRICTED" else 2
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), box_color, thickness)
    
    worker.stop()
    worker.join(timeout=2.0)
    
    db_events = get_all_events(limit=100)
    db_evidence = get_all_evidence(limit=100)
    timeline = get_timeline()
    stats = get_stats()
    
    print(f"\n--- Synthetic Results ---")
    print(f"Events generated: {events_generated}")
    print(f"Unique track_ids: {sorted(track_ids_seen)}")
    print(f"DB events: {len(db_events)}")
    print(f"DB evidence: {len(db_evidence)}")
    print(f"Timeline incidents: {len(timeline)}")
    print(f"Dashboard stats: persons={stats.get('persons')}, threat={stats.get('threat')}")
    print(f"YOLO status: {health.yolo_status}")
    print(f"Tracker status: {health.tracker_status}")
    
    for ev in db_events:
        print(f"  DB Event: {ev['event_type']} | track_id={ev['track_id']} | severity={ev['severity']} | zone={ev['zone']}")
    
    for ev in db_evidence:
        print(f"  DB Evidence: id={ev['id']} | event_id={ev['event_id']} | event={ev.get('event', ev.get('event_type', 'N/A'))}")
    
    assert events_generated > 0, "Should have generated events from synthetic detections"
    assert len(db_events) == events_generated
    assert len(timeline) == events_generated
    
    for ev in db_evidence:
        assert ev.get("event_id") is not None, "All evidence should be linked to an event"
    
    assert health.yolo_status in ["Loaded", "Running"]
    assert health.tracker_status in ["Active", "Stopped"]
    
    shutil.rmtree(tmpdir, ignore_errors=True)
    print("\nPASS: Synthetic event trigger pipeline verified")

if __name__ == "__main__":
    run_test()
