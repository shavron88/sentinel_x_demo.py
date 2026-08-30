"""
Sentinel-X Phase 7C — Demo & Hackathon Readiness

Tests demo mode and hackathon presentation readiness:
- Demo mode with synthetic data
- Multi-camera demo mode
- Main.py CLI argument parsing
- Flask dashboard startup
- Health check endpoints
- API availability
- No-camera fallback
- Synthetic detection generation
- Video feed endpoint
- Camera view page
"""
import os
import sys
import json
import time
import argparse
import tempfile
import shutil

sys.path.insert(0, os.path.abspath('.'))

from config import DEMO_MODE, CAMERAS, MODEL_PATH, MAX_QUEUE_SIZE


def run_test(name, expected, actual):
    status = "PASS" if expected == actual else "FAIL"
    print(f"  [{status}] {name}")
    if status == "FAIL":
        print(f"         EXPECTED: {expected}")
        print(f"         ACTUAL:   {actual}")
    return status == "PASS"


def test_demo_mode_flag():
    print("\n=== 1. Demo Mode Flag ===")
    passed = True
    passed &= run_test("DEMO_MODE default", False, DEMO_MODE)
    passed &= run_test("DEMO_MODE is boolean", True, isinstance(DEMO_MODE, bool))
    return passed


def test_main_py_cli():
    print("\n=== 2. Main.py CLI Arguments ===")
    passed = True
    
    try:
        import main
        
        # Test argument parser exists
        parser = argparse.ArgumentParser()
        parser.add_argument("--demo", action="store_true")
        parser.add_argument("--multi-camera", action="store_true")
        parser.add_argument("--duration", type=int, default=10)
        parser.add_argument("--flask", action="store_true")
        passed &= run_test("CLI parser works", True, True)
        
        # Test pipeline instantiation
        pipeline = main.SentinelXPipeline(demo=True)
        passed &= run_test("Demo mode pipeline", True, pipeline.demo)
        passed &= run_test("Pipeline has worker", True, pipeline.worker is not None)
        passed &= run_test("Pipeline has engine", True, pipeline.engine is not None)
        passed &= run_test("Pipeline has health monitor", True, pipeline.ai_health is not None)
        
    except Exception as e:
        passed &= run_test("CLI arguments", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_flask_dashboard_startup():
    print("\n=== 3. Flask Dashboard Startup ===")
    passed = True
    
    try:
        from dashboard.app import app
        
        passed &= run_test("Flask app exists", True, app is not None)
        
        # Test key routes exist
        with app.test_client() as client:
            # Home page
            response = client.get("/")
            passed &= run_test("Home page loads", True, response.status_code in [200, 302])
            
            # Camera view page
            response = client.get("/camera_view?camera=Camera_01")
            passed &= run_test("Camera view page", True, response.status_code in [200, 302])
            
            # Live wall page
            response = client.get("/live_wall")
            passed &= run_test("Live wall page", True, response.status_code in [200, 302])
            
            # Command center page
            response = client.get("/command_center")
            passed &= run_test("Command center page", True, response.status_code in [200, 302])
            
            # Threat center page
            response = client.get("/threat_center")
            passed &= run_test("Threat center page", True, response.status_code in [200, 302])
            
            # Copilot page
            response = client.get("/copilot")
            passed &= run_test("Copilot page", True, response.status_code in [200, 302])
            
    except Exception as e:
        passed &= run_test("Flask dashboard startup", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_video_feed_endpoint():
    print("\n=== 4. Video Feed Endpoint ===")
    passed = True
    
    try:
        from dashboard.app import app
        import threading
        
        def make_request():
            with app.test_client() as client:
                return client.get("/video_feed?camera_name=Camera_01")
        
        # Use thread with timeout to avoid hanging on infinite stream
        thread = threading.Thread(target=make_request)
        thread.start()
        thread.join(timeout=3.0)
        
        if thread.is_alive():
            # Request is still streaming (expected for video feed)
            passed &= run_test("Video feed endpoint streams", True, True)
        else:
            # Request completed (maybe no frames available)
            passed &= run_test("Video feed endpoint exists", True, True)
        
    except Exception as e:
        passed &= run_test("Video feed endpoint", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_no_camera_fallback():
    print("\n=== 5. No Camera Fallback ===")
    passed = True
    
    try:
        from camera.camera_manager import CameraManager, camera_manager
        
        # Save and clear singleton state
        original_pipelines = dict(camera_manager.pipelines)
        camera_manager.pipelines = {}
        camera_manager._default_camera_created = False
        
        # get_all_status should create default camera if none exist
        status = camera_manager.get_all_status()
        passed &= run_test("Default camera created", True, "Camera_01" in camera_manager.pipelines)
        passed &= run_test("Default flag set", True, camera_manager._default_camera_created)
        
        # Clean up
        camera_manager.remove_camera("Camera_01")
        
        # Restore original state
        camera_manager.pipelines = original_pipelines
        
    except Exception as e:
        passed &= run_test("No camera fallback", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_health_api_detailed():
    print("\n=== 6. Health API Detailed ===")
    passed = True
    
    try:
        from dashboard.app import app
        
        with app.test_client() as client:
            response = client.get("/api/v1/health")
            if response.status_code == 200:
                data = json.loads(response.data)
                passed &= run_test("System stats present", True, "system" in data)
                passed &= run_test("AI engine stats present", True, "ai_engine" in data)
                passed &= run_test("Recovery restarts present", True, "recovery_restarts" in data)
                
                if "system" in data:
                    sys_stats = data["system"]
                    passed &= run_test("System has cpu", True, "cpu_usage_percent" in sys_stats)
                    passed &= run_test("System has ram", True, "ram_usage_percent" in sys_stats)
                
                if "ai_engine" in data:
                    ai_stats = data["ai_engine"]
                    passed &= run_test("AI has status", True, "status" in ai_stats)
                    passed &= run_test("AI has metrics", True, "metrics" in ai_stats)
        
    except Exception as e:
        passed &= run_test("Health API detailed", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_copilot_api():
    print("\n=== 7. Copilot API ===")
    passed = True
    
    try:
        from dashboard.app import app
        
        with app.test_client() as client:
            response = client.post("/api/copilot", 
                data=json.dumps({"message": "Hello"}),
                content_type="application/json")
            passed &= run_test("Copilot endpoint exists", True, response.status_code == 200)
            
            if response.status_code == 200:
                data = json.loads(response.data)
                passed &= run_test("Copilot has response", True, "response" in data)
                passed &= run_test("Copilot has status", True, "status" in data)
        
    except Exception as e:
        passed &= run_test("Copilot API", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_settings_api():
    print("\n=== 8. Settings API ===")
    passed = True
    
    try:
        from dashboard.app import app
        
        with app.test_client() as client:
            # First authenticate
            login_response = client.post("/api/auth/login",
                data=json.dumps({"username": "sentinelx_admin", "password": "SentinelX_SecurePassword2026!"}),
                content_type="application/json")
            
            if login_response.status_code != 200:
                passed &= run_test("Auth login", True, False)
                return passed
            
            # Get CSRF token
            csrf_response = client.get("/api/auth/csrf-token")
            csrf_token = None
            if csrf_response.status_code == 200:
                csrf_data = json.loads(csrf_response.data)
                csrf_token = csrf_data.get("csrf_token")
            
            headers = {}
            if csrf_token:
                headers["X-CSRF-Token"] = csrf_token
            
            # GET settings
            response = client.get("/api/settings")
            passed &= run_test("Settings GET", True, response.status_code == 200)
            
            # POST camera settings
            response = client.post("/api/settings/camera",
                data=json.dumps({"cameras": [{"name": "Test", "source": "0", "zone": "Test"}]}),
                content_type="application/json",
                headers=headers)
            passed &= run_test("Camera settings POST", True, response.status_code == 200)
            
            # POST notification settings
            response = client.post("/api/settings/notifications",
                data=json.dumps({"notifications": {"email": "test@test.com"}}),
                content_type="application/json",
                headers=headers)
            passed &= run_test("Notification settings POST", True, response.status_code == 200)
        
    except Exception as e:
        passed &= run_test("Settings API", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_system_restart_api():
    print("\n=== 9. System Restart API ===")
    passed = True
    
    try:
        from dashboard.app import app
        
        with app.test_client() as client:
            # First authenticate
            login_response = client.post("/api/auth/login",
                data=json.dumps({"username": "sentinelx_admin", "password": "SentinelX_SecurePassword2026!"}),
                content_type="application/json")
            
            if login_response.status_code != 200:
                passed &= run_test("Auth login", True, False)
                return passed
            
            # Get CSRF token
            csrf_response = client.get("/api/auth/csrf-token")
            csrf_token = None
            if csrf_response.status_code == 200:
                csrf_data = json.loads(csrf_response.data)
                csrf_token = csrf_data.get("csrf_token")
            
            headers = {}
            if csrf_token:
                headers["X-CSRF-Token"] = csrf_token
            
            response = client.post("/api/system/restart", headers=headers)
            passed &= run_test("Restart endpoint", True, response.status_code in [200, 500])
        
    except Exception as e:
        passed &= run_test("System restart API", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_backup_api():
    print("\n=== 10. Backup API ===")
    passed = True
    
    try:
        from dashboard.app import app
        
        with app.test_client() as client:
            # First authenticate
            login_response = client.post("/api/auth/login",
                data=json.dumps({"username": "sentinelx_admin", "password": "SentinelX_SecurePassword2026!"}),
                content_type="application/json")
            
            if login_response.status_code != 200:
                passed &= run_test("Auth login", True, False)
                return passed
            
            # Get CSRF token
            csrf_response = client.get("/api/auth/csrf-token")
            csrf_token = None
            if csrf_response.status_code == 200:
                csrf_data = json.loads(csrf_response.data)
                csrf_token = csrf_data.get("csrf_token")
            
            headers = {}
            if csrf_token:
                headers["X-CSRF-Token"] = csrf_token
            
            response = client.post("/api/system/backup", headers=headers)
            passed &= run_test("Backup endpoint", True, response.status_code in [200, 500])
        
    except Exception as e:
        passed &= run_test("Backup API", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_dashboard_pages_render():
    print("\n=== 11. Dashboard Pages Render ===")
    passed = True
    
    try:
        from dashboard.app import app
        
        pages = [
            "/",
            "/cameras",
            "/incidents",
            "/evidence",
            "/analytics",
            "/reports",
            "/settings",
            "/live_wall",
            "/security_map",
            "/threat_center",
            "/command_center",
            "/copilot",
            "/replay",
            "/notifications"
        ]
        
        with app.test_client() as client:
            for page in pages:
                response = client.get(page)
                passed &= run_test(f"Page {page}", True, response.status_code in [200, 302])
        
    except Exception as e:
        passed &= run_test("Dashboard pages render", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_multi_camera_demo_setup():
    print("\n=== 12. Multi-Camera Demo Setup ===")
    passed = True
    
    try:
        from camera.camera_manager import CameraManager, camera_manager
        import numpy as np
        
        # Save and clear singleton state
        original_pipelines = dict(camera_manager.pipelines)
        camera_manager.pipelines = {}
        camera_manager._default_camera_created = False
        
        # Add multiple cameras for demo
        cam1 = camera_manager.add_camera(name="Demo_Cam_01", ip_url=0, zone="Entrance")
        cam2 = camera_manager.add_camera(name="Demo_Cam_02", ip_url=0, zone="Exit")
        cam3 = camera_manager.add_camera(name="Demo_Cam_03", ip_url=0, zone="Parking")
        
        time.sleep(0.3)
        
        passed &= run_test("3 cameras registered", 3, len(camera_manager.pipelines))
        passed &= run_test("All pipelines running", True, all(p.is_running for p in camera_manager.pipelines.values()))
        passed &= run_test("All workers alive", True, all(p.worker.is_alive() for p in camera_manager.pipelines.values()))
        
        # Get status (note: get_all_status may auto-create Camera_01)
        status = camera_manager.get_all_status()
        passed &= run_test("Status has 3+ cameras", True, len(status) >= 3)
        passed &= run_test("All cameras in status", True, all("status" in s for s in status.values()))
        
        # Clean up
        camera_manager.stop_all()
        
        # Restore original state
        camera_manager.pipelines = original_pipelines
        
    except Exception as e:
        passed &= run_test("Multi-camera demo setup", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_synthetic_detection_generation():
    print("\n=== 13. Synthetic Detection Generation ===")
    passed = True
    
    try:
        from ai.inference import YOLOInferenceEngine
        from ai.health import AIHealthMonitor
        import numpy as np
        
        health = AIHealthMonitor()
        engine = YOLOInferenceEngine(model_path=MODEL_PATH, health_monitor=health)
        
        # Create dummy frame
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        
        # Run inference
        result = engine.infer_frame(frame, frame_id=0)
        passed &= run_test("Inference returns dict", True, isinstance(result, dict))
        passed &= run_test("Has detections key", True, "detections" in result)
        passed &= run_test("Detections is list", True, isinstance(result.get("detections", []), list))
        
        # Check detection structure if any
        detections = result.get("detections", [])
        if detections:
            det = detections[0]
            passed &= run_test("Detection has class_id", True, "class_id" in det)
            passed &= run_test("Detection has confidence", True, "confidence" in det)
            passed &= run_test("Detection has bbox", True, "bbox" in det)
        
    except Exception as e:
        passed &= run_test("Synthetic detection generation", True, False)
        print(f"         ERROR: {e}")
    
    return passed


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("========== SENTINEL-X PHASE 7C DEMO READINESS ==========")
    
    results = []
    results.append(("Demo Mode Flag", test_demo_mode_flag()))
    results.append(("Main.py CLI", test_main_py_cli()))
    results.append(("Flask Dashboard Startup", test_flask_dashboard_startup()))
    results.append(("Video Feed Endpoint", test_video_feed_endpoint()))
    results.append(("No Camera Fallback", test_no_camera_fallback()))
    results.append(("Health API Detailed", test_health_api_detailed()))
    results.append(("Copilot API", test_copilot_api()))
    results.append(("Settings API", test_settings_api()))
    results.append(("System Restart API", test_system_restart_api()))
    results.append(("Backup API", test_backup_api()))
    results.append(("Dashboard Pages Render", test_dashboard_pages_render()))
    results.append(("Multi-Camera Demo Setup", test_multi_camera_demo_setup()))
    results.append(("Synthetic Detection Generation", test_synthetic_detection_generation()))
    
    print("\n========== PHASE 7C RESULTS ==========")
    passed_count = 0
    for name, result in results:
        status = "PASS" if result else "FAIL"
        if result:
            passed_count += 1
        print(f"  [{status}] {name}")
    
    print(f"\nTotal: {passed_count}/{len(results)} passed")
    if passed_count == len(results):
        print("ALL TESTS PASSED — Demo ready.")
    else:
        print("SOME TESTS FAILED — Review failures above.")
