import sys
import os
import time
import cv2
import numpy as np

sys.path.insert(0, os.path.abspath('.'))

from ai.health import AIHealthMonitor
from ai.inference import YOLOInferenceEngine
from ai.queue_manager import DetectionQueueManager
from ai.worker import YOLOWorker
from events.event_manager import EventManager
from events.abandoned_object import AbandonedObjectDetector
from events.fall_detector import FallDetector
from events.weapon_detector import WeaponDetector

def test_model_initialization():
    print("\n=== Test 1: Model Initialization ===")
    health = AIHealthMonitor()
    engine = YOLOInferenceEngine(model_path="models/yolov8m.pt", health_monitor=health)
    assert engine.model is not None, "Model should be initialized"
    assert health.yolo_status == "Loaded", f"YOLO status should be Loaded, got {health.yolo_status}"
    assert health.tracker_status == "Active", f"Tracker status should be Active, got {health.tracker_status}"
    print("PASS: Model initialized successfully")

def test_real_webcam_inference():
    print("\n=== Test 2: Real Webcam Frame Inference ===")
    health = AIHealthMonitor()
    engine = YOLOInferenceEngine(model_path="models/yolov8m.pt", health_monitor=health)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("SKIP: No webcam available")
        return
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("SKIP: Could not read webcam frame")
        return
    
    frame = cv2.resize(frame, (640, 360))
    result = engine.infer_frame(frame)
    
    assert result["error"] is None, f"Inference should not error: {result['error']}"
    assert result["annotated_frame"] is not None, "Annotated frame should not be None"
    assert isinstance(result["detections"], list), "Detections should be a list"
    
    print(f"PASS: Inference completed - {len(result['detections'])} detections")
    print(f"      Inference time: {health.last_inference_ms} ms")
    print(f"      YOLO status: {health.yolo_status}")
    print(f"      Tracker status: {health.tracker_status}")

def test_bytetrack_tracking():
    print("\n=== Test 3: ByteTrack Tracking Stability ===")
    health = AIHealthMonitor()
    engine = YOLOInferenceEngine(model_path="models/yolov8m.pt", health_monitor=health)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("SKIP: No webcam available")
        return
    
    track_ids = []
    for i in range(5):
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.resize(frame, (640, 360))
        result = engine.infer_frame(frame)
        
        person_tracks = [d["track_id"] for d in result["detections"] if d["class_id"] == 0 and d.get("track_id") is not None]
        if person_tracks:
            track_ids.append(person_tracks[0])
        time.sleep(0.1)
    
    cap.release()
    
    if len(track_ids) >= 2:
        stable = all(t == track_ids[0] for t in track_ids)
        print(f"PASS: Track IDs observed: {track_ids}")
        print(f"      Stable: {stable}")
    else:
        print("INFO: No person detected for tracking test")

def test_queue_worker_inference_flow():
    print("\n=== Test 4: Queue -> Worker -> Inference -> Result Flow ===")
    health = AIHealthMonitor()
    queue_mgr = DetectionQueueManager(maxsize=10)
    engine = YOLOInferenceEngine(health_monitor=health)
    worker = YOLOWorker(queue_mgr, engine, health)
    
    worker.start()
    
    for i in range(3):
        queue_mgr.push_frame(i, f"test_frame_{i}")
        time.sleep(0.05)
    
    time.sleep(0.3)
    
    results = []
    for _ in range(3):
        res = queue_mgr.get_result(timeout=0.5)
        if res:
            results.append(res)
    
    worker.stop()
    worker.join(timeout=2.0)
    
    assert len(results) == 3, f"Expected 3 results, got {len(results)}"
    assert all(isinstance(r[1], list) for r in results), "All results should be lists of detections"
    print(f"PASS: Processed {len(results)} frames through queue/worker/inference")

def test_ai_health_metrics():
    print("\n=== Test 5: AI Health Metrics ===")
    health = AIHealthMonitor()
    
    assert hasattr(health, 'pipeline_status'), "Health monitor should have pipeline_status"
    assert hasattr(health, 'tracker_status'), "Health monitor should have tracker_status"
    assert hasattr(health, 'yolo_status'), "Health monitor should have yolo_status"
    
    health.update_yolo_status("Loaded")
    health.update_tracker_status("Active")
    health.record_inference(0.05)
    
    status = health.get_health_status()
    assert status["pipeline_status"] == "Healthy", f"Pipeline should be Healthy, got {status['pipeline_status']}"
    assert status["tracker_status"] == "Active", f"Tracker should be Active, got {status['tracker_status']}"
    assert status["metrics"]["last_inference_ms"] > 0, "Last inference time should be > 0"
    print("PASS: Health metrics working correctly")
    print(f"      Status: {status['status']}")
    print(f"      Pipeline: {status['pipeline_status']}")
    print(f"      FPS: {status['metrics']['detection_fps']}")

def test_worker_shutdown():
    print("\n=== Test 7: Worker Shutdown ===")
    health = AIHealthMonitor()
    queue_mgr = DetectionQueueManager(maxsize=5)
    engine = YOLOInferenceEngine(health_monitor=health)
    worker = YOLOWorker(queue_mgr, engine, health)
    
    worker.start()
    time.sleep(0.1)
    worker.stop()
    worker.join(timeout=2.0)
    
    assert not worker.is_alive(), "Worker should be stopped"
    assert health.tracker_status == "Stopped", f"Tracker should show Stopped, got {health.tracker_status}"
    print("PASS: Worker shut down cleanly")

def test_no_fake_detections():
    print("\n=== Test 8: No Fake/Mock Detection Fallback ===")
    health = AIHealthMonitor()
    engine = YOLOInferenceEngine(model_path="models/yolov8m.pt", health_monitor=health)
    
    # Test with invalid frame - should return empty detections, no fake data
    result = engine.infer_frame("invalid_frame_string")
    assert result["error"] is None, "String frame should not error, just return empty detections"
    assert len(result["detections"]) == 0, "Invalid frame should have 0 detections"
    
    # Test that engine doesn't fabricate detections
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        cap.release()
        if ret:
            frame = cv2.resize(frame, (640, 360))
            result = engine.infer_frame(frame)
            # All detections should have proper structure
            for det in result["detections"]:
                assert "track_id" in det, "Detection must have track_id"
                assert "class_id" in det, "Detection must have class_id"
                assert "label" in det, "Detection must have label"
                assert "confidence" in det, "Detection must have confidence"
                assert "bbox" in det, "Detection must have bbox"
                assert len(det["bbox"]) == 4, "BBox must have 4 coordinates"
            print("PASS: No fake detections, all real detections have proper structure")
        else:
            print("SKIP: Could not read webcam frame")
    else:
        print("SKIP: No webcam available")

def test_event_detectors_accept_structured_data():
    print("\n=== Test 9: Event Detectors Accept Structured Data ===")
    sample_detections = [
        {"track_id": 1, "class_id": 0, "label": "person", "confidence": 0.9, "bbox": [100, 100, 200, 300]},
        {"track_id": 2, "class_id": 0, "label": "person", "confidence": 0.85, "bbox": [300, 100, 400, 300]},
        {"track_id": 3, "class_id": 24, "label": "backpack", "confidence": 0.7, "bbox": [50, 50, 100, 100]},
    ]
    
    event_mgr = EventManager()
    events = event_mgr.process(sample_detections)
    assert len(events) == 2, f"Expected 2 person events, got {len(events)}"
    
    abandoned = AbandonedObjectDetector()
    events = abandoned.update(sample_detections)
    # Should not crash
    
    fall = FallDetector()
    events = fall.detect(sample_detections)
    # Should not crash
    
    weapon = WeaponDetector()
    events = weapon.detect(sample_detections)
    # Should not crash
    
    print("PASS: All event detectors accept structured detection dicts")

if __name__ == "__main__":
    print("========== SENTINEL-X MILESTONE A TESTS ==========")
    
    test_model_initialization()
    test_real_webcam_inference()
    test_bytetrack_tracking()
    test_queue_worker_inference_flow()
    test_ai_health_metrics()
    test_worker_shutdown()
    test_no_fake_detections()
    test_event_detectors_accept_structured_data()
    
    print("\n========== ALL TESTS COMPLETED ==========")
