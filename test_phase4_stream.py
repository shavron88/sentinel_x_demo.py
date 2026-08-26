"""Phase 4 — Camera Stream Hardening Tests"""
import sys, os, time, cv2, numpy as np
sys.path.insert(0, os.path.abspath('.'))

from dashboard.stream import (
    set_frame, get_frame, get_frame_age, get_frame_drops,
    get_stream_fps, _draw_status_overlay, generate
)
from camera.camera_manager import CameraManager, CameraStream

def test_stream_functions():
    print("\n=== 1. Stream Functions ===")
    frame = np.full((360, 640, 3), (100, 100, 100), dtype=np.uint8)
    set_frame(frame)
    assert get_frame() is not None, "get_frame should return frame"
    assert get_frame_age() < 1.0, "Frame age should be < 1s"
    print("PASS: Stream functions work")

def test_status_overlay():
    print("\n=== 2. Status Overlay ===")
    frame = np.full((360, 640, 3), (50, 50, 50), dtype=np.uint8)
    statuses = ["ONLINE", "OFFLINE", "CRITICAL", "EXCELLENT", "POOR"]
    for status in statuses:
        result = _draw_status_overlay(frame.copy(), camera_name="Cam1", status=status, fps=15.0, queue_size=5)
        assert result is not None
        assert result.shape == frame.shape
    print("PASS: Status overlay draws correctly")

def test_camera_manager_integration():
    print("\n=== 3. Camera Manager Integration ===")
    cam_mgr = CameraManager()
    cam = cam_mgr.get_camera_stream("Camera_01")
    assert cam is not None, "Default camera should exist"
    assert cam.name == "Camera_01"
    assert cam.status in ["ONLINE", "CONNECTING", "OFFLINE", "RECONNECTING"]
    print(f"PASS: Camera Manager works (status={cam.status})")

def test_generate_stream():
    print("\n=== 4. Generate Stream ===")
    test_frame = np.full((360, 640, 3), (200, 200, 200), dtype=np.uint8)
    set_frame(test_frame)
    
    frames_received = 0
    for frame_bytes in generate(camera_name="Camera_01", camera_status="ONLINE", queue_size=0):
        assert frame_bytes.startswith(b"--frame"), "Should be multipart frame"
        assert b"Content-Type: image/jpeg" in frame_bytes, "Should be JPEG"
        frames_received += 1
        if frames_received >= 3:
            break
    
    assert frames_received >= 1, "Should receive at least 1 frame"
    print(f"PASS: Stream generator produced {frames_received} frames")

def test_fallback_when_no_frame():
    print("\n=== 5. Fallback When No Frame ===")
    set_frame(None)
    
    frames_received = 0
    for frame_bytes in generate(camera_name="Camera_01", camera_status="OFFLINE", queue_size=0):
        frames_received += 1
        if frames_received >= 2:
            break
    
    assert frames_received >= 1, "Should still produce frames even when AI frame is None"
    print(f"PASS: Fallback works ({frames_received} frames from CameraManager)")

def test_dashboard_app_imports():
    print("\n=== 6. Dashboard App Imports ===")
    from dashboard.app import app, generate_camera_stream
    assert app is not None
    print("PASS: Dashboard app imports work")

if __name__ == "__main__":
    print("========== SENTINEL-X PHASE 4 CAMERA STREAM TESTS ==========")
    test_stream_functions()
    test_status_overlay()
    test_camera_manager_integration()
    test_generate_stream()
    test_fallback_when_no_frame()
    test_dashboard_app_imports()
    print("\n========== ALL PHASE 4 TESTS PASSED ==========")
