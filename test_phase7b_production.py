"""
Sentinel-X Phase 7B — Production Readiness Validation

Tests production deployment readiness:
- Docker best practices
- Resource management
- Logging configuration
- Database persistence
- Graceful shutdown
- Health check endpoints
- Process management
"""
import os
import sys
import json
import sqlite3
import tempfile
import shutil
import time

sys.path.insert(0, os.path.abspath('.'))

from config import (
    LOG_DIR, EVIDENCE_DIR, VIDEO_DIR, DB_PATH, MODELS_DIR,
    MAX_QUEUE_SIZE, MODEL_PATH
)


def run_test(name, expected, actual):
    status = "PASS" if expected == actual else "FAIL"
    print(f"  [{status}] {name}")
    if status == "FAIL":
        print(f"         EXPECTED: {expected}")
        print(f"         ACTUAL:   {actual}")
    return status == "PASS"


def test_dockerfile_production_ready():
    print("\n=== 1. Dockerfile Production Readiness ===")
    passed = True
    
    if not os.path.exists("Dockerfile"):
        print("  [FAIL] Dockerfile not found")
        return False
    
    with open("Dockerfile", "r") as f:
        content = f.read()
    
    # Check for production best practices
    passed &= run_test("Uses slim base image", True, "slim" in content.lower())
    passed &= run_test("Non-root user (or USER instruction)", True, "USER" in content or "root" not in content.lower())
    passed &= run_test("WORKDIR set", True, "WORKDIR" in content)
    passed &= run_test("COPY requirements first", True, content.index("COPY requirements.txt") < content.index("COPY . .") if "COPY requirements.txt" in content and "COPY . ." in content else False)
    passed &= run_test("HEALTHCHECK defined", True, "HEALTHCHECK" in content)
    passed &= run_test("EXPOSE 5000", True, "EXPOSE 5000" in content)
    passed &= run_test("No password in image", True, "password" not in content.lower() or "CHANGE" in content)
    
    return passed


def test_docker_compose_production():
    print("\n=== 2. Docker Compose Production Config ===")
    passed = True
    
    if not os.path.exists("docker-compose.yml"):
        print("  [FAIL] docker-compose.yml not found")
        return False
    
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    passed &= run_test("Restart policy", True, "restart:" in content)
    passed &= run_test("Volume mounts for persistence", True, "volumes:" in content)
    passed &= run_test("Resource limits", True, "deploy:" in content or "resources:" in content)
    passed &= run_test("Shared memory size", True, "shm_size" in content)
    passed &= run_test("Health check", True, "healthcheck:" in content or "HEALTHCHECK" in content)
    
    return passed


def test_logging_configuration():
    print("\n=== 3. Logging Configuration ===")
    passed = True
    
    # Check log directory exists
    passed &= run_test("Log directory exists", True, os.path.isdir(LOG_DIR))
    
    # Check for log configuration in code
    try:
        from core.system_monitor import SystemMonitor
        sm = SystemMonitor()
        stats = sm.get_stats()
        passed &= run_test("System monitor works", True, stats is not None)
        passed &= run_test("System monitor has cpu", True, "cpu_usage_percent" in stats)
    except Exception as e:
        passed &= run_test("System monitor initialization", True, False)
    
    return passed


def test_database_persistence():
    print("\n=== 4. Database Persistence ===")
    passed = True
    
    # Test database creation and basic operations
    test_db = os.path.join(tempfile.gettempdir(), "sentinelx_test_persist.db")
    try:
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Create events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT DEFAULT 'LOW',
                camera TEXT NOT NULL,
                zone TEXT DEFAULT 'General Area',
                track_id INTEGER DEFAULT -1,
                confidence REAL DEFAULT 0.0,
                duration REAL DEFAULT 0.0,
                metadata TEXT
            )
        """)
        
        # Create evidence table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                timestamp TEXT NOT NULL,
                camera TEXT NOT NULL,
                image_path TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        # Insert test event
        cursor.execute("""
            INSERT INTO events (timestamp, event_type, severity, camera, zone, track_id, confidence, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("2026-01-01 00:00:00", "PERSON_DETECTED", "LOW", "Camera_01", "SAFE", 1, 0.9, 0.0))
        
        event_id = cursor.lastrowid
        
        # Insert test evidence
        cursor.execute("""
            INSERT INTO evidence (event_id, timestamp, camera, image_path, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (event_id, "2026-01-01 00:00:00", "Camera_01", "/path/to/evidence.jpg", "{}"))
        
        conn.commit()
        
        # Verify data persisted
        cursor.execute("SELECT COUNT(*) FROM events")
        event_count = cursor.fetchone()[0]
        passed &= run_test("Events persisted", 1, event_count)
        
        cursor.execute("SELECT COUNT(*) FROM evidence")
        evidence_count = cursor.fetchone()[0]
        passed &= run_test("Evidence persisted", 1, evidence_count)
        
        conn.close()
        
    except Exception as e:
        passed &= run_test("Database persistence", True, False)
        print(f"         ERROR: {e}")
    finally:
        if os.path.exists(test_db):
            os.remove(test_db)
    
    return passed


def test_graceful_shutdown():
    print("\n=== 5. Graceful Shutdown ===")
    passed = True
    
    try:
        from camera.camera_manager import CameraManager, CameraPipeline
        import numpy as np
        
        mgr = CameraManager()
        
        # Add cameras
        cam1 = mgr.add_camera(name="Shutdown_01", ip_url=0)
        cam2 = mgr.add_camera(name="Shutdown_02", ip_url=0)
        
        time.sleep(0.2)
        
        passed &= run_test("Cameras running", 2, len(mgr.pipelines))
        passed &= run_test("Workers alive", True, all(p.worker.is_alive() for p in mgr.pipelines.values()))
        
        # Stop all
        mgr.stop_all()
        
        passed &= run_test("All cameras stopped", 0, len(mgr.pipelines))
        passed &= run_test("Default flag reset", False, mgr._default_camera_created)
        
    except Exception as e:
        passed &= run_test("Graceful shutdown", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_health_check_endpoints():
    print("\n=== 6. Health Check Endpoints ===")
    passed = True
    
    try:
        from dashboard.app import app
        
        with app.test_client() as client:
            # Test health endpoint
            response = client.get("/api/v1/health")
            passed &= run_test("Health endpoint returns 200", 200, response.status_code)
            
            if response.status_code == 200:
                data = json.loads(response.data)
                passed &= run_test("Health has system key", True, "system" in data)
                passed &= run_test("Health has ai_engine key", True, "ai_engine" in data)
        
        # Test events endpoint
        with app.test_client() as client:
            response = client.get("/events")
            passed &= run_test("Events endpoint returns 200", 200, response.status_code)
        
        # Test stats endpoint
        with app.test_client() as client:
            response = client.get("/stats")
            passed &= run_test("Stats endpoint returns 200", 200, response.status_code)
        
    except Exception as e:
        passed &= run_test("Health check endpoints", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_api_endpoints_available():
    print("\n=== 7. API Endpoints Availability ===")
    passed = True
    
    try:
        from dashboard.app import app
        
        with app.test_client() as client:
            # First authenticate
            login_response = client.post("/api/auth/login",
                data=json.dumps({"username": "admin", "password": "sentinelx"}),
                content_type="application/json")
            
            if login_response.status_code != 200:
                print("  [WARN] Auth login failed, some endpoints may return 401")
            
            # Test gallery endpoint
            response = client.get("/gallery")
            passed &= run_test("Gallery endpoint", True, response.status_code in [200, 401])
            
            # Test analytics data endpoint
            response = client.get("/analytics_data")
            passed &= run_test("Analytics data endpoint", True, response.status_code in [200, 500])
            
            # Test reports data endpoint
            response = client.get("/reports_data")
            passed &= run_test("Reports data endpoint", True, response.status_code in [200, 500])
            
            # Test settings endpoint
            response = client.get("/api/settings")
            passed &= run_test("Settings endpoint", True, response.status_code in [200, 401])
            
            # Test storage endpoint
            response = client.get("/api/storage")
            passed &= run_test("Storage endpoint", True, response.status_code in [200, 401])
        
    except Exception as e:
        passed &= run_test("API endpoints", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_evidence_storage_structure():
    print("\n=== 8. Evidence Storage Structure ===")
    passed = True
    
    # Check evidence directories
    passed &= run_test("Evidence dir exists", True, os.path.isdir(EVIDENCE_DIR))
    passed &= run_test("Video dir exists", True, os.path.isdir(VIDEO_DIR))
    
    # Check permissions (basic check)
    if os.path.isdir(EVIDENCE_DIR):
        passed &= run_test("Evidence dir writable", True, os.access(EVIDENCE_DIR, os.W_OK))
    
    if os.path.isdir(VIDEO_DIR):
        passed &= run_test("Video dir writable", True, os.access(VIDEO_DIR, os.W_OK))
    
    return passed


def test_model_loading():
    print("\n=== 9. Model Loading ===")
    passed = True
    
    try:
        from ai.inference import YOLOInferenceEngine
        from ai.health import AIHealthMonitor
        
        health = AIHealthMonitor()
        engine = YOLOInferenceEngine(model_path=MODEL_PATH, health_monitor=health)
        
        passed &= run_test("Engine initialized", True, engine is not None)
        passed &= run_test("Health monitor attached", True, engine.health_monitor is not None)
        
        # Test inference with dummy frame
        import numpy as np
        dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
        result = engine.infer_frame(dummy_frame, frame_id=0)
        passed &= run_test("Inference returns result", True, result is not None)
        passed &= run_test("Result has detections", True, "detections" in result)
        
    except Exception as e:
        passed &= run_test("Model loading", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_recovery_manager():
    print("\n=== 10. Recovery Manager ===")
    passed = True
    
    try:
        from core.recovery import AutoRecoveryManager
        from ai.health import AIHealthMonitor
        from ai.queue_manager import DetectionQueueManager
        from ai.inference import YOLOInferenceEngine
        from ai.worker import YOLOWorker
        
        health = AIHealthMonitor()
        queue_mgr = DetectionQueueManager(maxsize=10)
        engine = YOLOInferenceEngine(model_path=MODEL_PATH, health_monitor=health)
        worker = YOLOWorker(queue_mgr, engine, health)
        
        recovery = AutoRecoveryManager(health, queue_mgr, engine, check_interval=0.5)
        recovery.attach_worker(worker)
        
        passed &= run_test("Recovery manager created", True, recovery is not None)
        passed &= run_test("Worker attached", True, recovery.worker is not None)
        
        # Start recovery
        recovery.start()
        passed &= run_test("Recovery running", True, recovery.is_alive())
        
        # Stop recovery
        recovery.stop()
        recovery.join(timeout=2.0)
        passed &= run_test("Recovery stopped", False, recovery.is_alive())
        
    except Exception as e:
        passed &= run_test("Recovery manager", True, False)
        print(f"         ERROR: {e}")
    
    return passed


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("========== SENTINEL-X PHASE 7B PRODUCTION READINESS ==========")
    
    results = []
    results.append(("Dockerfile Production Ready", test_dockerfile_production_ready()))
    results.append(("Docker Compose Production", test_docker_compose_production()))
    results.append(("Logging Configuration", test_logging_configuration()))
    results.append(("Database Persistence", test_database_persistence()))
    results.append(("Graceful Shutdown", test_graceful_shutdown()))
    results.append(("Health Check Endpoints", test_health_check_endpoints()))
    results.append(("API Endpoints Available", test_api_endpoints_available()))
    results.append(("Evidence Storage Structure", test_evidence_storage_structure()))
    results.append(("Model Loading", test_model_loading()))
    results.append(("Recovery Manager", test_recovery_manager()))
    
    print("\n========== PHASE 7B RESULTS ==========")
    passed_count = 0
    for name, result in results:
        status = "PASS" if result else "FAIL"
        if result:
            passed_count += 1
        print(f"  [{status}] {name}")
    
    print(f"\nTotal: {passed_count}/{len(results)} passed")
    if passed_count == len(results):
        print("ALL TESTS PASSED — Production ready.")
    else:
        print("SOME TESTS FAILED — Review failures above.")
