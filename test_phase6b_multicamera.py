"""
Sentinel-X Phase 6B — Multi-Camera Support Validation

Tests the complete multi-camera architecture:
- Camera isolation
- Independent queues
- Independent workers
- Camera-specific tracking/events/evidence
- Disconnect/reconnect isolation
- Queue pressure isolation
- Health metrics
- Clean shutdown

Note: Synthetic inputs are only used inside dedicated tests.
No fake production detections are introduced.
"""
import sys
import os
import time
import cv2
import numpy as np
import sqlite3
import tempfile
import shutil
import threading
from datetime import datetime

sys.path.insert(0, os.path.abspath('.'))

from camera.camera_manager import CameraManager, CameraStream, CameraPipeline
from ai.health import AIHealthMonitor
from ai.inference import YOLOInferenceEngine
from ai.queue_manager import DetectionQueueManager
from ai.worker import YOLOWorker
from events.event_manager import EventManager
from events.memory_manager import MemoryManager
from events.zone_manager import ZoneManager
from events.abandoned_object import AbandonedObjectDetector
from events.crowd_detector import CrowdDetector
from events.fall_detector import FallDetector
from events.line_crossing import LineCrossingDetector
from events.weapon_detector import WeaponDetector
from events.people_counter import PeopleCounter
from alerts.intelligence_engine import IntelligenceEngine
from alerts.alert_manager import AlertManager
from evidence.evidence_manager import EvidenceManager, save as evidence_save
from database import db as db_module
from dashboard.store import add_event, get_events, get_stats
from dashboard.timeline import add_incident, get_timeline
from dashboard.stream import set_frame, get_frame_drops, get_stream_fps
from database.db import get_all_evidence

# Test environment
TMP_ROOT = None
DB_PATH = None
EVIDENCE_DIR = None

def setup_test_env():
    global TMP_ROOT, DB_PATH, EVIDENCE_DIR
    TMP_ROOT = tempfile.mkdtemp(prefix="sentinelx_phase6b_")
    DB_PATH = os.path.join(TMP_ROOT, "test.db")
    EVIDENCE_DIR = os.path.join(TMP_ROOT, "evidence")
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    
    db_module.DB_PATH = DB_PATH
    db_module.init_db()
    
    from evidence import evidence_manager as em_module
    em_module.DB_PATH = DB_PATH
    em_module.EVIDENCE_DIR = EVIDENCE_DIR
    
    # Isolate from CameraManager singleton
    from camera.camera_manager import camera_manager
    for name in list(camera_manager.pipelines.keys()):
        camera_manager.remove_camera(name)

def teardown_test_env():
    from camera.camera_manager import camera_manager
    for name in list(camera_manager.pipelines.keys()):
        camera_manager.remove_camera(name)
    if TMP_ROOT and os.path.exists(TMP_ROOT):
        shutil.rmtree(TMP_ROOT, ignore_errors=True)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def run_test(name, expected, actual):
    status = "PASS" if expected == actual else "FAIL"
    print(f"  [{status}] {name}")
    if status == "FAIL":
        print(f"         EXPECTED: {expected}")
        print(f"         ACTUAL:   {actual}")
    return status == "PASS"

# ============================================================
# 1. Single camera backward compatibility
# ============================================================
def test_single_camera_backward_compat():
    print("\n=== 1. Single Camera Backward Compatibility ===")
    setup_test_env()
    
    mgr = CameraManager()
    cam = mgr.add_camera(name="Camera_01", ip_url=0, zone="Main Entrance")
    
    passed = True
    passed &= run_test("Camera registered", True, "Camera_01" in mgr.pipelines)
    passed &= run_test("Pipeline is running", True, cam.is_running)
    passed &= run_test("Stream exists", True, cam.stream is not None)
    passed &= run_test("Worker exists", True, cam.worker is not None)
    passed &= run_test("Queue exists", True, cam.queue is not None)
    passed &= run_test("Health monitor exists", True, cam.health is not None)
    
    # Test get_camera_stream backward compat
    stream = mgr.get_camera_stream("Camera_01")
    passed &= run_test("get_camera_stream works", True, stream is not None)
    
    # Test get_all_status
    status = mgr.get_all_status()
    passed &= run_test("get_all_status works", True, "Camera_01" in status)
    
    mgr.remove_camera("Camera_01")
    passed &= run_test("Camera removed", False, "Camera_01" in mgr.pipelines)
    
    teardown_test_env()
    return passed

# ============================================================
# 2. Two-camera registration
# ============================================================
def test_two_camera_registration():
    print("\n=== 2. Two-Camera Registration ===")
    setup_test_env()
    
    mgr = CameraManager()
    cam1 = mgr.add_camera(name="Camera_01", ip_url=0, zone="Main Entrance")
    cam2 = mgr.add_camera(name="Camera_02", ip_url=1, zone="Parking Lot")
    
    passed = True
    passed &= run_test("Camera 01 registered", True, "Camera_01" in mgr.pipelines)
    passed &= run_test("Camera 02 registered", True, "Camera_02" in mgr.pipelines)
    passed &= run_test("Camera 01 zone", "Main Entrance", cam1.zone)
    passed &= run_test("Camera 02 zone", "Parking Lot", cam2.zone)
    passed &= run_test("Camera 01 has pipeline", True, mgr.get_pipeline("Camera_01") is not None)
    passed &= run_test("Camera 02 has pipeline", True, mgr.get_pipeline("Camera_02") is not None)
    
    # Verify they are different pipeline instances
    p1 = mgr.get_pipeline("Camera_01")
    p2 = mgr.get_pipeline("Camera_02")
    passed &= run_test("Pipelines are independent", True, p1 is not p2)
    passed &= run_test("Workers are independent", True, p1.worker is not p2.worker)
    passed &= run_test("Queues are independent", True, p1.queue is not p2.queue)
    
    mgr.remove_camera("Camera_01")
    mgr.remove_camera("Camera_02")
    
    teardown_test_env()
    return passed

# ============================================================
# 3. Independent camera streams
# ============================================================
def test_independent_camera_streams():
    print("\n=== 3. Independent Camera Streams ===")
    setup_test_env()
    
    mgr = CameraManager()
    cam1 = mgr.add_camera(name="Cam_Stream_01", ip_url=0, zone="Zone A")
    cam2 = mgr.add_camera(name="Cam_Stream_02", ip_url=0, zone="Zone B")
    
    passed = True
    passed &= run_test("Camera 1 running", True, cam1.stream.is_running)
    passed &= run_test("Camera 2 running", True, cam2.stream.is_running)
    passed &= run_test("Camera 1 zone", "Zone A", cam1.zone)
    passed &= run_test("Camera 2 zone", "Zone B", cam2.zone)
    passed &= run_test("Camera 1 name", "Cam_Stream_01", cam1.stream.name)
    passed &= run_test("Camera 2 name", "Cam_Stream_02", cam2.stream.name)
    
    # Verify independent status
    status1 = cam1.get_status()
    status2 = cam2.get_status()
    passed &= run_test("Status 1 has name", "Cam_Stream_01", status1.get("name"))
    passed &= run_test("Status 2 has name", "Cam_Stream_02", status2.get("name"))
    
    mgr.remove_camera("Cam_Stream_01")
    mgr.remove_camera("Cam_Stream_02")
    
    teardown_test_env()
    return passed

# ============================================================
# 4. Independent queues
# ============================================================
def test_independent_queues():
    print("\n=== 4. Independent Queues ===")
    setup_test_env()
    
    mgr = CameraManager()
    cam1 = mgr.add_camera(name="Cam_Queue_01", ip_url=0, max_queue_size=3)
    cam2 = mgr.add_camera(name="Cam_Queue_02", ip_url=0, max_queue_size=3)
    
    # Push frames to camera 1 queue
    for i in range(3):
        cam1.queue.push_frame(i, f"frame_{i}")
    
    # Push frames to camera 2 queue
    for i in range(3):
        cam2.queue.push_frame(i, f"frame_{i}")
    
    passed = True
    passed &= run_test("Queue 1 size", 3, cam1.queue.qsize())
    passed &= run_test("Queue 2 size", 3, cam2.queue.qsize())
    passed &= run_test("Queues are independent", True, cam1.queue is not cam2.queue)
    
    # Push more frames to test overflow handling
    for i in range(10):
        cam1.queue.push_frame(i + 10, f"frame_{i}")
    
    passed &= run_test("Queue 1 handles overflow", True, cam1.queue.qsize() <= 3)
    
    # Camera 2 queue should still be independent
    passed &= run_test("Camera 2 queue unaffected", 3, cam2.queue.qsize())
    
    mgr.remove_camera("Cam_Queue_01")
    mgr.remove_camera("Cam_Queue_02")
    
    teardown_test_env()
    return passed

# ============================================================
# 5. Independent workers
# ============================================================
def test_independent_workers():
    print("\n=== 5. Independent Workers ===")
    setup_test_env()
    
    mgr = CameraManager()
    cam1 = mgr.add_camera(name="Cam_Worker_01", ip_url=0)
    cam2 = mgr.add_camera(name="Cam_Worker_02", ip_url=0)
    
    passed = True
    passed &= run_test("Worker 1 alive", True, cam1.worker.is_alive())
    passed &= run_test("Worker 2 alive", True, cam2.worker.is_alive())
    passed &= run_test("Workers are independent", True, cam1.worker is not cam2.worker)
    
    # Stop worker 1 only
    cam1.worker.stop()
    cam1.worker.join(timeout=2.0)
    
    passed &= run_test("Worker 1 stopped", False, cam1.worker.is_alive())
    passed &= run_test("Worker 2 still alive", True, cam2.worker.is_alive())
    
    mgr.remove_camera("Cam_Worker_01")
    mgr.remove_camera("Cam_Worker_02")
    
    teardown_test_env()
    return passed

# ============================================================
# 6. Camera-specific tracking state
# ============================================================
def test_camera_specific_tracking():
    print("\n=== 6. Camera-Specific Tracking State ===")
    setup_test_env()
    
    mgr = CameraManager()
    cam1 = mgr.add_camera(name="Cam_Track_01", ip_url=0)
    cam2 = mgr.add_camera(name="Cam_Track_02", ip_url=0)
    
    # Update track_id 1 on both cameras
    cam1.memory_manager.update(1, "SAFE")
    cam2.memory_manager.update(1, "RESTRICTED")
    
    passed = True
    passed &= run_test("Camera 1 track 1 zone", "SAFE", cam1.memory_manager.people.get(1, {}).get("current_zone"))
    passed &= run_test("Camera 2 track 1 zone", "RESTRICTED", cam2.memory_manager.people.get(1, {}).get("current_zone"))
    
    # Verify line detector state is independent
    cam1.line_detector.update(1, 0.5)
    cam2.line_detector.update(1, 0.7)
    
    # Different cameras should have different line states for same track_id
    passed &= run_test("Line detectors independent", True, 
        cam1.line_detector.last_side.get(1) != cam2.line_detector.last_side.get(1))
    
    mgr.remove_camera("Cam_Track_01")
    mgr.remove_camera("Cam_Track_02")
    
    teardown_test_env()
    return passed

# ============================================================
# 7. Camera-specific events
# ============================================================
def test_camera_specific_events():
    print("\n=== 7. Camera-Specific Events ===")
    setup_test_env()
    
    mgr = CameraManager()
    cam1 = mgr.add_camera(name="Cam_Event_01", ip_url=0)
    cam2 = mgr.add_camera(name="Cam_Event_02", ip_url=0)
    
    detections = [
        {"track_id": 1, "class_id": 0, "label": "person", "confidence": 0.9, "bbox": [100.0, 100.0, 200.0, 300.0]}
    ]
    
    # Process on camera 1
    cam1._on_inference_result(1, detections, np.zeros((360, 640, 3), dtype=np.uint8))
    time.sleep(0.1)
    
    # Process on camera 2
    cam2._on_inference_result(1, detections, np.zeros((360, 640, 3), dtype=np.uint8))
    time.sleep(0.1)
    
    events = get_events(limit=10)
    
    passed = True
    cam1_events = [e for e in events if e.get("camera") == "Cam_Event_01"]
    cam2_events = [e for e in events if e.get("camera") == "Cam_Event_02"]
    passed &= run_test("Camera 1 has events", True, len(cam1_events) > 0)
    passed &= run_test("Camera 2 has events", True, len(cam2_events) > 0)
    passed &= run_test("Events have camera field", True, all("camera" in e for e in events))
    
    # Verify track_id isolation - both cameras processed track_id 1 but they are different events
    if len(cam1_events) > 0 and len(cam2_events) > 0:
        passed &= run_test("Same track_id different cameras", True, 
            cam1_events[0].get("track_id") == cam2_events[0].get("track_id"))
    
    mgr.remove_camera("Cam_Event_01")
    mgr.remove_camera("Cam_Event_02")
    
    teardown_test_env()
    return passed

# ============================================================
# 8. Camera-specific evidence
# ============================================================
def test_camera_specific_evidence():
    print("\n=== 8. Camera-Specific Evidence ===")
    setup_test_env()
    
    mgr = CameraManager()
    cam1 = mgr.add_camera(name="Cam_Evid_01", ip_url=0)
    cam2 = mgr.add_camera(name="Cam_Evid_02", ip_url=0)
    
    frame = np.full((360, 640, 3), (100, 100, 100), dtype=np.uint8)
    
    # Process HIGH severity event (RESTRICTED zone) on both cameras
    # bbox center: x=450, y=350 -> cx=0.70, cy=0.97 -> RESTRICTED zone
    detections = [
        {"track_id": 1, "class_id": 0, "label": "person", "confidence": 0.9, "bbox": [400.0, 300.0, 500.0, 400.0]}
    ]
    
    cam1._on_inference_result(1, detections, frame)
    cam2._on_inference_result(1, detections, frame)
    time.sleep(0.2)
    
    evidence = get_all_evidence(limit=10)
    
    passed = True
    cam1_evidence = [e for e in evidence if e.get("camera") == "Cam_Evid_01"]
    cam2_evidence = [e for e in evidence if e.get("camera") == "Cam_Evid_02"]
    passed &= run_test("Camera 1 has evidence", True, len(cam1_evidence) > 0)
    passed &= run_test("Camera 2 has evidence", True, len(cam2_evidence) > 0)
    passed &= run_test("Evidence has camera field", True, all("camera" in e for e in evidence))
    
    mgr.remove_camera("Cam_Evid_01")
    mgr.remove_camera("Cam_Evid_02")
    
    teardown_test_env()
    return passed

# ============================================================
# 9. One camera disconnect while another continues
# ============================================================
def test_camera_disconnect_isolation():
    print("\n=== 9. Camera Disconnect Isolation ===")
    setup_test_env()
    
    mgr = CameraManager()
    cam1 = mgr.add_camera(name="Cam_Disconnect_01", ip_url=0, zone="Zone A")
    cam2 = mgr.add_camera(name="Cam_Disconnect_02", ip_url=0, zone="Zone B")
    
    time.sleep(0.5)
    
    passed = True
    passed &= run_test("Both cameras running", True, cam1.stream.is_running and cam2.stream.is_running)
    
    # Disconnect camera 1
    cam1.stream.restart()
    passed &= run_test("Camera 1 reconnecting", "RECONNECTING", cam1.stream.status)
    
    # Camera 2 should still be running
    passed &= run_test("Camera 2 still running", True, cam2.stream.is_running)
    
    # Verify camera 2 status is unaffected
    passed &= run_test("Camera 2 status unchanged or ONLINE", True, 
        cam2.stream.status in ["ONLINE", "CONNECTING", "OFFLINE"])
    
    # Camera 1 should be attempting recovery (status changed or reconnect count increased)
    time.sleep(0.5)
    passed &= run_test("Camera 1 in recovery state", True, 
        cam1.stream.status in ["RECONNECTING", "CONNECTING", "OFFLINE"] or cam1.stream.reconnects > 0)
    passed &= run_test("Camera 2 still running after delay", True, cam2.stream.is_running)
    
    mgr.remove_camera("Cam_Disconnect_01")
    mgr.remove_camera("Cam_Disconnect_02")
    
    teardown_test_env()
    return passed

# ============================================================
# 10. Independent reconnection
# ============================================================
def test_independent_reconnection():
    print("\n=== 10. Independent Reconnection ===")
    setup_test_env()
    
    mgr = CameraManager()
    cam1 = mgr.add_camera(name="Cam_Reconn_01", ip_url=0, reconnect_delay=0.1)
    cam2 = mgr.add_camera(name="Cam_Reconn_02", ip_url=0, reconnect_delay=0.1)
    
    time.sleep(0.3)
    
    initial_reconnects_1 = cam1.stream.reconnects
    initial_reconnects_2 = cam2.stream.reconnects
    
    # Force reconnect on camera 1
    cam1.stream.restart()
    
    # Wait for at least one reconnect attempt
    time.sleep(1.5)
    
    passed = True
    # Camera 1 should have attempted reconnection (status changed or reconnects increased)
    passed &= run_test("Camera 1 recovery state", True, 
        cam1.stream.status in ["RECONNECTING", "CONNECTING", "OFFLINE"] or 
        cam1.stream.reconnects > initial_reconnects_1)
    # Camera 2 should be unaffected
    passed &= run_test("Camera 2 reconnects unchanged", True, cam2.stream.reconnects == initial_reconnects_2)
    passed &= run_test("Camera 2 still running", True, cam2.stream.is_running)
    
    mgr.remove_camera("Cam_Reconn_01")
    mgr.remove_camera("Cam_Reconn_02")
    
    teardown_test_env()
    return passed

# ============================================================
# 11. Worker recovery for one camera
# ============================================================
def test_worker_recovery_isolation():
    print("\n=== 11. Worker Recovery Isolation ===")
    setup_test_env()
    
    mgr = CameraManager()
    cam1 = mgr.add_camera(name="Cam_Recover_01", ip_url=0)
    cam2 = mgr.add_camera(name="Cam_Recover_02", ip_url=0)
    
    time.sleep(0.2)
    
    passed = True
    passed &= run_test("Worker 1 alive", True, cam1.worker.is_alive())
    passed &= run_test("Worker 2 alive", True, cam2.worker.is_alive())
    
    # Simulate worker 1 crash
    cam1.worker.stop()
    cam1.worker.join(timeout=2.0)
    passed &= run_test("Worker 1 stopped", False, cam1.worker.is_alive())
    passed &= run_test("Worker 2 still alive", True, cam2.worker.is_alive())
    
    # Recover worker 1
    from ai.worker import YOLOWorker
    cam1.worker = YOLOWorker(cam1.queue, cam1.engine, cam1.health)
    cam1.worker.start()
    time.sleep(0.2)
    passed &= run_test("Worker 1 recovered", True, cam1.worker.is_alive())
    passed &= run_test("Worker 2 still alive after recovery", True, cam2.worker.is_alive())
    
    mgr.remove_camera("Cam_Recover_01")
    mgr.remove_camera("Cam_Recover_02")
    
    teardown_test_env()
    return passed

# ============================================================
# 12. Queue pressure isolation
# ============================================================
def test_queue_pressure_isolation():
    print("\n=== 12. Queue Pressure Isolation ===")
    setup_test_env()
    
    mgr = CameraManager()
    cam1 = mgr.add_camera(name="Cam_Pressure_01", ip_url=0, max_queue_size=3)
    cam2 = mgr.add_camera(name="Cam_Pressure_02", ip_url=0, max_queue_size=3)
    
    # Flood camera 1 queue
    for i in range(20):
        cam1.queue.push_frame(i, np.zeros((360, 640, 3), dtype=np.uint8))
    
    time.sleep(0.5)
    
    passed = True
    passed &= run_test("Queue 1 handled overflow", True, cam1.queue.qsize() <= 3)
    passed &= run_test("Worker 1 still alive", True, cam1.worker.is_alive())
    passed &= run_test("Worker 2 still alive", True, cam2.worker.is_alive())
    
    # Camera 2 queue should be unaffected
    cam2.queue.push_frame(1, np.zeros((360, 640, 3), dtype=np.uint8))
    passed &= run_test("Camera 2 queue still works", 1, cam2.queue.qsize())
    
    mgr.remove_camera("Cam_Pressure_01")
    mgr.remove_camera("Cam_Pressure_02")
    
    teardown_test_env()
    return passed

# ============================================================
# 13. Camera-specific health metrics
# ============================================================
def test_camera_specific_health():
    print("\n=== 13. Camera-Specific Health Metrics ===")
    setup_test_env()
    
    mgr = CameraManager()
    cam1 = mgr.add_camera(name="Cam_Health_01", ip_url=0)
    cam2 = mgr.add_camera(name="Cam_Health_02", ip_url=0)
    
    time.sleep(0.2)
    
    status1 = cam1.get_status()
    status2 = cam2.get_status()
    
    passed = True
    passed &= run_test("Camera 1 has name", "Cam_Health_01", status1.get("name"))
    passed &= run_test("Camera 2 has name", "Cam_Health_02", status2.get("name"))
    passed &= run_test("Camera 1 has status", True, "status" in status1)
    passed &= run_test("Camera 2 has status", True, "status" in status2)
    passed &= run_test("Camera 1 has fps", True, "fps" in status1)
    passed &= run_test("Camera 2 has fps", True, "fps" in status2)
    passed &= run_test("Camera 1 has pipeline_status", True, "pipeline_status" in status1)
    passed &= run_test("Camera 2 has pipeline_status", True, "pipeline_status" in status2)
    passed &= run_test("Camera 1 has worker_status", True, "worker_status" in status1)
    passed &= run_test("Camera 2 has worker_status", True, "worker_status" in status2)
    passed &= run_test("Camera 1 has queue_size", True, "queue_size" in status1)
    passed &= run_test("Camera 2 has queue_size", True, "queue_size" in status2)
    
    mgr.remove_camera("Cam_Health_01")
    mgr.remove_camera("Cam_Health_02")
    
    teardown_test_env()
    return passed

# ============================================================
# 14. Clean multi-camera shutdown
# ============================================================
def test_clean_multi_camera_shutdown():
    print("\n=== 14. Clean Multi-Camera Shutdown ===")
    setup_test_env()
    
    mgr = CameraManager()
    cam1 = mgr.add_camera(name="Cam_Shutdown_01", ip_url=0)
    cam2 = mgr.add_camera(name="Cam_Shutdown_02", ip_url=0)
    cam3 = mgr.add_camera(name="Cam_Shutdown_03", ip_url=0)
    
    time.sleep(0.2)
    
    passed = True
    passed &= run_test("3 cameras running", 3, len(mgr.pipelines))
    passed &= run_test("All workers alive", True, all(p.worker.is_alive() for p in mgr.pipelines.values()))
    
    mgr.stop_all()
    
    passed &= run_test("All cameras stopped", 0, len(mgr.pipelines))
    passed &= run_test("Default camera flag reset", False, mgr._default_camera_created)
    
    teardown_test_env()
    return passed

# ============================================================
# 15. Full two-camera end-to-end pipeline
# ============================================================
def test_two_camera_end_to_end():
    print("\n=== 15. Two-Camera End-to-End Pipeline ===")
    setup_test_env()
    
    mgr = CameraManager()
    cam1 = mgr.add_camera(name="Cam_E2E_01", ip_url=0, zone="Entrance")
    cam2 = mgr.add_camera(name="Cam_E2E_02", ip_url=0, zone="Exit")
    
    time.sleep(0.5)
    
    # Simulate frames for both cameras
    frame1 = np.full((360, 640, 3), (180, 180, 180), dtype=np.uint8)
    frame2 = np.full((360, 640, 3), (200, 200, 200), dtype=np.uint8)
    
    # Push frames to queues
    cam1.queue.push_frame(1, frame1)
    cam2.queue.push_frame(1, frame2)
    
    # Wait for workers to process frames (poll with timeout)
    start_time = time.time()
    res1 = None
    res2 = None
    while time.time() - start_time < 8.0:
        if res1 is None:
            res1 = cam1.queue.get_result(timeout=0.1)
        if res2 is None:
            res2 = cam2.queue.get_result(timeout=0.1)
        if res1 is not None and res2 is not None:
            break
    
    passed = True
    passed &= run_test("Camera 1 processed frame", True, res1 is not None)
    passed &= run_test("Camera 2 processed frame", True, res2 is not None)
    
    if res1:
        fid1, det1 = res1
        passed &= run_test("Camera 1 frame ID", 1, fid1)
        passed &= run_test("Camera 1 detections is list", True, isinstance(det1, list))
    
    if res2:
        fid2, det2 = res2
        passed &= run_test("Camera 2 frame ID", 1, fid2)
        passed &= run_test("Camera 2 detections is list", True, isinstance(det2, list))
    
    # Verify workers still alive
    passed &= run_test("Worker 1 alive after e2e", True, cam1.worker.is_alive())
    passed &= run_test("Worker 2 alive after e2e", True, cam2.worker.is_alive())
    
    # Verify health monitors are independent
    passed &= run_test("Camera 1 has health", True, cam1.health is not None)
    passed &= run_test("Camera 2 has health", True, cam2.health is not None)
    passed &= run_test("Health monitors independent", True, cam1.health is not cam2.health)
    
    mgr.remove_camera("Cam_E2E_01")
    mgr.remove_camera("Cam_E2E_02")
    
    teardown_test_env()
    return passed

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("========== SENTINEL-X PHASE 6B MULTI-CAMERA ==========")
    
    results = []
    results.append(("Single Camera Backward Compat", test_single_camera_backward_compat()))
    results.append(("Two-Camera Registration", test_two_camera_registration()))
    results.append(("Independent Camera Streams", test_independent_camera_streams()))
    results.append(("Independent Queues", test_independent_queues()))
    results.append(("Independent Workers", test_independent_workers()))
    results.append(("Camera-Specific Tracking", test_camera_specific_tracking()))
    results.append(("Camera-Specific Events", test_camera_specific_events()))
    results.append(("Camera-Specific Evidence", test_camera_specific_evidence()))
    results.append(("Camera Disconnect Isolation", test_camera_disconnect_isolation()))
    results.append(("Independent Reconnection", test_independent_reconnection()))
    results.append(("Worker Recovery Isolation", test_worker_recovery_isolation()))
    results.append(("Queue Pressure Isolation", test_queue_pressure_isolation()))
    results.append(("Camera-Specific Health", test_camera_specific_health()))
    results.append(("Clean Multi-Camera Shutdown", test_clean_multi_camera_shutdown()))
    results.append(("Two-Camera End-to-End", test_two_camera_end_to_end()))
    
    print("\n========== PHASE 6B RESULTS ==========")
    passed_count = 0
    for name, result in results:
        status = "PASS" if result else "FAIL"
        if result:
            passed_count += 1
        print(f"  [{status}] {name}")
    
    print(f"\nTotal: {passed_count}/{len(results)} passed")
    if passed_count == len(results):
        print("ALL TESTS PASSED — Multi-camera support validated.")
    else:
        print("SOME TESTS FAILED — Review failures above.")
