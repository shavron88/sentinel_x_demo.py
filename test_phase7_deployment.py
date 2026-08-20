"""
Sentinel-X Phase 7 — Deployment & Demo Validation

Tests deployment readiness:
- Configuration loading from environment
- Dockerfile validation
- docker-compose validation
- Demo mode functionality
- Multi-camera startup
- Environment variable parsing
- Path creation
- Flask app initialization
"""
import os
import sys
import json
import tempfile
import shutil

sys.path.insert(0, os.path.abspath('.'))

from config import (
    MODEL_PATH, CONFIDENCE_THRESHOLD, CAMERA_SOURCE,
    CAMERAS, RTSP_TIMEOUT_MS, RTSP_BUFFER_SIZE, RTSP_TRANSPORT,
    RTSP_MAX_RECONNECT_DELAY, RTSP_RECONNECT_BACKOFF, DEFAULT_RTSP_CONFIG,
    EVENT_COOLDOWN, LOITERING_THRESHOLD, CROWD_THRESHOLD,
    EVIDENCE_DIR, VIDEO_DIR, MODELS_DIR, DB_PATH, LOG_DIR,
    MAX_QUEUE_SIZE, DEMO_MODE, DATABASE_URL
)


def run_test(name, expected, actual):
    status = "PASS" if expected == actual else "FAIL"
    print(f"  [{status}] {name}")
    if status == "FAIL":
        print(f"         EXPECTED: {expected}")
        print(f"         ACTUAL:   {actual}")
    return status == "PASS"


def test_config_defaults():
    print("\n=== 1. Configuration Defaults ===")
    passed = True
    passed &= run_test("MODEL_PATH", "models/yolov8m.pt", MODEL_PATH)
    passed &= run_test("CONFIDENCE_THRESHOLD", 0.60, CONFIDENCE_THRESHOLD)
    passed &= run_test("CAMERA_SOURCE", "0", CAMERA_SOURCE)
    passed &= run_test("EVENT_COOLDOWN", 600, EVENT_COOLDOWN)
    passed &= run_test("LOITERING_THRESHOLD", 30, LOITERING_THRESHOLD)
    passed &= run_test("CROWD_THRESHOLD", 5, CROWD_THRESHOLD)
    passed &= run_test("MAX_QUEUE_SIZE", 30, MAX_QUEUE_SIZE)
    passed &= run_test("DEMO_MODE", False, DEMO_MODE)
    passed &= run_test("CAMERAS empty by default", True, len(CAMERAS) == 0)
    return passed


def test_rtsp_config():
    print("\n=== 2. RTSP Configuration ===")
    passed = True
    passed &= run_test("RTSP_TIMEOUT_MS", 5000, RTSP_TIMEOUT_MS)
    passed &= run_test("RTSP_BUFFER_SIZE", 1, RTSP_BUFFER_SIZE)
    passed &= run_test("RTSP_TRANSPORT", "tcp", RTSP_TRANSPORT)
    passed &= run_test("RTSP_MAX_RECONNECT_DELAY", 30.0, RTSP_MAX_RECONNECT_DELAY)
    passed &= run_test("RTSP_RECONNECT_BACKOFF", 1.5, RTSP_RECONNECT_BACKOFF)
    passed &= run_test("DEFAULT_RTSP_CONFIG exists", True, "timeout_ms" in DEFAULT_RTSP_CONFIG)
    return passed


def test_paths_exist():
    print("\n=== 3. Paths and Directories ===")
    passed = True
    passed &= run_test("EVIDENCE_DIR", "evidence/screenshots", EVIDENCE_DIR)
    passed &= run_test("VIDEO_DIR", "evidence/videos", VIDEO_DIR)
    passed &= run_test("MODELS_DIR", "models", MODELS_DIR)
    passed &= run_test("DB_PATH", "sentinelx.db", DB_PATH)
    passed &= run_test("LOG_DIR", "logs", LOG_DIR)
    
    # Check directories were created by config.py
    passed &= run_test("Evidence dir exists", True, os.path.isdir(EVIDENCE_DIR))
    passed &= run_test("Video dir exists", True, os.path.isdir(VIDEO_DIR))
    passed &= run_test("Log dir exists", True, os.path.isdir(LOG_DIR))
    passed &= run_test("Models dir exists", True, os.path.isdir(MODELS_DIR))
    return passed


def test_database_url():
    print("\n=== 4. Database Configuration ===")
    passed = True
    expected_url = f"sqlite:///{DB_PATH}"
    passed &= run_test("DATABASE_URL", expected_url, DATABASE_URL)
    return passed


def test_env_override():
    print("\n=== 5. Environment Variable Override ===")
    
    # Save original env
    original_env = {}
    test_vars = ["MODEL_PATH", "CONFIDENCE_THRESHOLD", "CAMERA_SOURCE", "EVENT_COOLDOWN"]
    for var in test_vars:
        original_env[var] = os.environ.get(var)
    
    # Set test values
    os.environ["MODEL_PATH"] = "models/yolov8n.pt"
    os.environ["CONFIDENCE_THRESHOLD"] = "0.80"
    os.environ["CAMERA_SOURCE"] = "1"
    os.environ["EVENT_COOLDOWN"] = "300"
    
    # Reload config
    import importlib
    import config as config_module
    importlib.reload(config_module)
    
    passed = True
    passed &= run_test("MODEL_PATH override", "models/yolov8n.pt", config_module.MODEL_PATH)
    passed &= run_test("CONFIDENCE_THRESHOLD override", 0.80, config_module.CONFIDENCE_THRESHOLD)
    passed &= run_test("CAMERA_SOURCE override", "1", config_module.CAMERA_SOURCE)
    passed &= run_test("EVENT_COOLDOWN override", 300, config_module.EVENT_COOLDOWN)
    
    # Restore original env
    for var in test_vars:
        if original_env[var] is not None:
            os.environ[var] = original_env[var]
        else:
            os.environ.pop(var, None)
    
    # Reload config back
    importlib.reload(config_module)
    return passed


def test_multi_camera_config():
    print("\n=== 6. Multi-Camera Configuration Parsing ===")
    
    # Save original env
    original_cameras = os.environ.get("CAMERAS")
    
    # Set test cameras - using | as separator to avoid conflicts with RTSP URLs
    os.environ["CAMERAS"] = "Camera_01:0:Main Entrance|Camera_02:rtsp://admin:pass@192.168.1.100:554/stream1:Parking Lot|Camera_03:rtsp://admin:pass@192.168.1.101:554/stream1:Warehouse:8000"
    
    # Reload config
    import importlib
    import config as config_module
    importlib.reload(config_module)
    
    passed = True
    passed &= run_test("Camera count", 3, len(config_module.CAMERAS))
    
    if len(config_module.CAMERAS) >= 3:
        cam1 = config_module.CAMERAS[0]
        cam2 = config_module.CAMERAS[1]
        cam3 = config_module.CAMERAS[2]
        passed &= run_test("Camera 1 name", "Camera_01", cam1["name"])
        passed &= run_test("Camera 1 source", "0", cam1["source"])
        passed &= run_test("Camera 1 zone", "Main Entrance", cam1["zone"])
        passed &= run_test("Camera 2 name", "Camera_02", cam2["name"])
        passed &= run_test("Camera 2 source", "rtsp://admin:pass@192.168.1.100:554/stream1", cam2["source"])
        passed &= run_test("Camera 2 zone", "Parking Lot", cam2["zone"])
        passed &= run_test("Camera 3 timeout", 8000, cam3.get("timeout"))
    
    # Restore
    if original_cameras is not None:
        os.environ["CAMERAS"] = original_cameras
    else:
        os.environ.pop("CAMERAS", None)
    
    importlib.reload(config_module)
    return passed


def test_dockerfile_exists():
    print("\n=== 7. Dockerfile Validation ===")
    passed = True
    passed &= run_test("Dockerfile exists", True, os.path.exists("Dockerfile"))
    
    if os.path.exists("Dockerfile"):
        with open("Dockerfile", "r") as f:
            content = f.read()
        passed &= run_test("FROM instruction", True, "FROM" in content)
        passed &= run_test("WORKDIR set", True, "WORKDIR" in content)
        passed &= run_test("EXPOSE 5000", True, "EXPOSE 5000" in content)
        passed &= run_test("CMD defined", True, "CMD" in content)
        passed &= run_test("COPY requirements", True, "requirements.txt" in content)
    
    return passed


def test_docker_compose_exists():
    print("\n=== 8. Docker Compose Validation ===")
    passed = True
    passed &= run_test("docker-compose.yml exists", True, os.path.exists("docker-compose.yml"))
    
    if os.path.exists("docker-compose.yml"):
        with open("docker-compose.yml", "r") as f:
            content = f.read()
        passed &= run_test("Version defined", True, "version:" in content)
        passed &= run_test("Service defined", True, "services:" in content)
        passed &= run_test("Port 5000 exposed", True, "5000:5000" in content)
        passed &= run_test("Volumes defined", True, "volumes:" in content)
    
    return passed


def test_flask_app_initialization():
    print("\n=== 9. Flask Application Initialization ===")
    passed = True
    
    try:
        from dashboard.app import app
        passed &= run_test("Flask app exists", True, app is not None)
        passed &= run_test("App name", "dashboard.app", app.name if hasattr(app, 'name') else "N/A")
        
        # Check routes
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        passed &= run_test("/ route exists", True, "/" in rules)
        passed &= run_test("/video_feed route", True, "/video_feed" in rules)
        passed &= run_test("/events route", True, "/events" in rules)
        passed &= run_test("/stats route", True, "/stats" in rules)
    except Exception as e:
        passed &= run_test("Flask app initialization", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_camera_manager_initialization():
    print("\n=== 10. Camera Manager Initialization ===")
    passed = True
    
    try:
        from camera.camera_manager import camera_manager, CameraManager, CameraPipeline
        
        # Test singleton
        mgr1 = CameraManager()
        mgr2 = CameraManager()
        passed &= run_test("Singleton pattern", True, mgr1 is mgr2)
        
        # Test global instance
        passed &= run_test("Global instance exists", True, camera_manager is not None)
        
        # Test pipeline class exists
        passed &= run_test("CameraPipeline class exists", True, CameraPipeline is not None)
        
        # Test methods exist
        passed &= run_test("add_camera method", True, hasattr(mgr1, 'add_camera'))
        passed &= run_test("remove_camera method", True, hasattr(mgr1, 'remove_camera'))
        passed &= run_test("get_all_status method", True, hasattr(mgr1, 'get_all_status'))
        passed &= run_test("stop_all method", True, hasattr(mgr1, 'stop_all'))
        
    except Exception as e:
        passed &= run_test("Camera manager initialization", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_requirements_exist():
    print("\n=== 11. Requirements Validation ===")
    passed = True
    passed &= run_test("requirements.txt exists", True, os.path.exists("requirements.txt"))
    
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            content = f.read()
        passed &= run_test("Flask in requirements", True, "Flask" in content)
        passed &= run_test("opencv-python in requirements", True, "opencv-python" in content)
        passed &= run_test("ultralytics in requirements", True, "ultralytics" in content)
    
    return passed


def test_docs_exist():
    print("\n=== 12. Documentation Validation ===")
    passed = True
    
    docs_to_check = [
        "README.md",
        "docs/deployment.md",
        "docs/architecture.md",
        "docs/api.md",
        "CHANGELOG.md"
    ]
    
    for doc in docs_to_check:
        passed &= run_test(f"{doc} exists", True, os.path.exists(doc))
    
    return passed


def test_env_example_exists():
    print("\n=== 13. Environment Configuration ===")
    passed = True
    passed &= run_test(".env.example exists", True, os.path.exists(".env.example"))
    
    if os.path.exists(".env.example"):
        with open(".env.example", "r") as f:
            content = f.read()
        passed &= run_test("FLASK_DEBUG in .env.example", True, "FLASK_DEBUG" in content)
        passed &= run_test("MODEL_PATH in .env.example", True, "MODEL_PATH" in content)
        passed &= run_test("CAMERA_SOURCE in .env.example", True, "CAMERA_SOURCE" in content)
        passed &= run_test("RTSP settings in .env.example", True, "RTSP_TIMEOUT_MS" in content)
    
    return passed


def test_main_py_functionality():
    print("\n=== 14. Main.py Functionality ===")
    passed = True
    
    try:
        import main
        passed &= run_test("SentinelXPipeline class exists", True, hasattr(main, 'SentinelXPipeline'))
        passed &= run_test("main function exists", True, hasattr(main, 'main'))
        
        # Test pipeline instantiation
        pipeline = main.SentinelXPipeline(demo=True)
        passed &= run_test("Pipeline demo mode", True, pipeline.demo)
        passed &= run_test("Pipeline has worker", True, pipeline.worker is not None)
        passed &= run_test("Pipeline has engine", True, pipeline.engine is not None)
        passed &= run_test("Pipeline has health monitor", True, pipeline.ai_health is not None)
        
    except Exception as e:
        passed &= run_test("Main.py functionality", True, False)
        print(f"         ERROR: {e}")
    
    return passed


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("========== SENTINEL-X PHASE 7 DEPLOYMENT ==========")
    
    results = []
    results.append(("Configuration Defaults", test_config_defaults()))
    results.append(("RTSP Configuration", test_rtsp_config()))
    results.append(("Paths and Directories", test_paths_exist()))
    results.append(("Database Configuration", test_database_url()))
    results.append(("Environment Override", test_env_override()))
    results.append(("Multi-Camera Config", test_multi_camera_config()))
    results.append(("Dockerfile Validation", test_dockerfile_exists()))
    results.append(("Docker Compose Validation", test_docker_compose_exists()))
    results.append(("Flask App Initialization", test_flask_app_initialization()))
    results.append(("Camera Manager Initialization", test_camera_manager_initialization()))
    results.append(("Requirements Validation", test_requirements_exist()))
    results.append(("Documentation Validation", test_docs_exist()))
    results.append(("Environment Configuration", test_env_example_exists()))
    results.append(("Main.py Functionality", test_main_py_functionality()))
    
    print("\n========== PHASE 7 RESULTS ==========")
    passed_count = 0
    for name, result in results:
        status = "PASS" if result else "FAIL"
        if result:
            passed_count += 1
        print(f"  [{status}] {name}")
    
    print(f"\nTotal: {passed_count}/{len(results)} passed")
    if passed_count == len(results):
        print("ALL TESTS PASSED — Deployment ready.")
    else:
        print("SOME TESTS FAILED — Review failures above.")
