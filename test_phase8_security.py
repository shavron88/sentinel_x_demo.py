"""
Sentinel-X Phase 8 — Security Hardening Validation

Tests security controls:
- Path traversal prevention
- Authentication requirements
- Authorization on sensitive endpoints
- CSRF protection
- Rate limiting
- Input validation
- Secret key configuration
- Docker healthcheck
"""
import os
import sys
import json
import time

sys.path.insert(0, os.path.abspath('.'))

from config import DEMO_MODE, CAMERAS, MODEL_PATH, MAX_QUEUE_SIZE


def run_test(name, expected, actual):
    status = "PASS" if expected == actual else "FAIL"
    print(f"  [{status}] {name}")
    if status == "FAIL":
        print(f"         EXPECTED: {expected}")
        print(f"         ACTUAL:   {actual}")
    return status == "PASS"


def test_path_traversal_blocked():
    print("\n=== 1. Path Traversal Prevention ===")
    passed = True
    
    try:
        from dashboard.app import app
        
        with app.test_client() as client:
            # Login first
            login_response = client.post("/api/auth/login",
                data=json.dumps({"username": "sentinelx_admin", "password": "SentinelX_SecurePassword2026!"}),
                content_type="application/json")
            
            if login_response.status_code != 200:
                passed &= run_test("Login succeeds", True, False)
                return passed
            
            # Try path traversal attacks
            traversal_paths = [
                "../../etc/passwd",
                "..\\..\\windows\\system32\\drivers\\etc\\hosts",
                "....//....//etc/passwd",
                "%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            ]
            
            for path in traversal_paths:
                response = client.get(f"/evidence/screenshots/{path}")
                passed &= run_test(f"Block traversal: {path[:30]}", 
                    True, 
                    response.status_code in [400, 403, 404])
            
            # Valid file should work (or 404 if doesn't exist)
            response = client.get("/evidence/screenshots/test.jpg")
            passed &= run_test("Valid filename allowed", 
                True, 
                response.status_code in [200, 404])
    
    except Exception as e:
        passed &= run_test("Path traversal", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_authentication_required():
    print("\n=== 2. Authentication Required ===")
    passed = True
    
    try:
        from dashboard.app import app
        
        with app.test_client() as client:
            # Test protected endpoints without auth
            protected_endpoints = [
                ("/video_feed?camera_name=Camera_01", "GET", None),
                ("/gallery", "GET", None),
                ("/api/settings", "GET", None),
                ("/api/system/restart", "POST", {}),
                ("/api/system/backup", "POST", {}),
                ("/api/system/cleanup", "POST", {}),
                ("/api/settings/camera", "POST", {"cameras": []}),
                ("/api/settings/notifications", "POST", {"email": "test@test.com"}),
            ]
            
            for endpoint, method, data in protected_endpoints:
                if method == "GET":
                    response = client.get(endpoint)
                else:
                    response = client.post(endpoint,
                        data=json.dumps(data) if data else None,
                        content_type="application/json")
                
                passed &= run_test(f"Unauth {method} {endpoint[:40]}", 
                    True, 
                    response.status_code == 401)
    
    except Exception as e:
        passed &= run_test("Authentication", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_login_logout():
    print("\n=== 3. Login/Logout Flow ===")
    passed = True
    
    try:
        from dashboard.app import app
        
        with app.test_client() as client:
            # Test login with invalid credentials
            response = client.post("/api/auth/login",
                data=json.dumps({"username": "wrong", "password": "wrong"}),
                content_type="application/json")
            passed &= run_test("Invalid login rejected", 401, response.status_code)
            
            # Test login with valid credentials
            response = client.post("/api/auth/login",
                data=json.dumps({"username": "sentinelx_admin", "password": "SentinelX_SecurePassword2026!"}),
                content_type="application/json")
            passed &= run_test("Valid login accepted", 200, response.status_code)
            
            if response.status_code == 200:
                data = json.loads(response.data)
                passed &= run_test("Login returns username", True, "username" in data)
                passed &= run_test("Login returns csrf_token", True, "csrf_token" in data)
            
            # Test auth status
            response = client.get("/api/auth/status")
            passed &= run_test("Auth status endpoint", 200, response.status_code)
            
            if response.status_code == 200:
                data = json.loads(response.data)
                passed &= run_test("Authenticated after login", True, data.get("authenticated") == True)
            
            # Test logout
            response = client.post("/api/auth/logout")
            passed &= run_test("Logout succeeds", 200, response.status_code)
            
            # Test auth status after logout
            response = client.get("/api/auth/status")
            passed &= run_test("Not authenticated after logout", True, 
                json.loads(response.data).get("authenticated") == False)
    
    except Exception as e:
        passed &= run_test("Login/logout", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_csrf_protection():
    print("\n=== 4. CSRF Protection ===")
    passed = True
    
    try:
        from dashboard.app import app
        
        with app.test_client() as client:
            # Login
            login_response = client.post("/api/auth/login",
                data=json.dumps({"username": "sentinelx_admin", "password": "SentinelX_SecurePassword2026!"}),
                content_type="application/json")
            
            if login_response.status_code != 200:
                passed &= run_test("Login succeeds", True, False)
                return passed
            
            # Try POST without CSRF token
            response = client.post("/api/system/restart")
            passed &= run_test("POST without CSRF rejected", 403, response.status_code)
            
            # Get CSRF token
            csrf_response = client.get("/api/auth/csrf-token")
            if csrf_response.status_code == 200:
                csrf_data = json.loads(csrf_response.data)
                csrf_token = csrf_data.get("csrf_token")
                
                # Try POST with invalid CSRF token
                response = client.post("/api/system/restart",
                    headers={"X-CSRF-Token": "invalid_token"})
                passed &= run_test("POST with invalid CSRF rejected", 403, response.status_code)
                
                # Try POST with valid CSRF token
                response = client.post("/api/system/restart",
                    headers={"X-CSRF-Token": csrf_token})
                passed &= run_test("POST with valid CSRF accepted", 
                    True, response.status_code in [200, 500])
    
    except Exception as e:
        passed &= run_test("CSRF protection", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_rate_limiting():
    print("\n=== 5. Rate Limiting ===")
    passed = True
    
    try:
        from dashboard.app import app
        
        with app.test_client() as client:
            # Login once
            client.post("/api/auth/login",
                data=json.dumps({"username": "sentinelx_admin", "password": "SentinelX_SecurePassword2026!"}),
                content_type="application/json")
            
            # Send many requests rapidly
            rate_limited = False
            for i in range(70):
                response = client.get("/api/settings")
                if response.status_code == 429:
                    rate_limited = True
                    break
            
            passed &= run_test("Rate limiting triggers", True, rate_limited)
    
    except Exception as e:
        passed &= run_test("Rate limiting", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_input_validation():
    print("\n=== 6. Input Validation ===")
    passed = True
    
    try:
        from dashboard.app import app
        
        with app.test_client() as client:
            # Login and get CSRF token
            login_response = client.post("/api/auth/login",
                data=json.dumps({"username": "sentinelx_admin", "password": "SentinelX_SecurePassword2026!"}),
                content_type="application/json")
            
            if login_response.status_code != 200:
                passed &= run_test("Login succeeds", True, False)
                return passed
            
            csrf_response = client.get("/api/auth/csrf-token")
            csrf_token = None
            if csrf_response.status_code == 200:
                csrf_data = json.loads(csrf_response.data)
                csrf_token = csrf_data.get("csrf_token")
            
            headers = {}
            if csrf_token:
                headers["X-CSRF-Token"] = csrf_token
            
            # Test invalid JSON
            response = client.post("/api/settings/camera",
                data="not json",
                content_type="application/json",
                headers=headers)
            passed &= run_test("Invalid JSON rejected", 
                True, response.status_code in [400, 500])
            
            # Test missing required fields
            response = client.post("/api/settings/camera",
                data=json.dumps({}),
                content_type="application/json",
                headers=headers)
            passed &= run_test("Missing fields rejected", 400, response.status_code)
            
            # Test invalid data types
            response = client.post("/api/settings/camera",
                data=json.dumps({"cameras": "not a list"}),
                content_type="application/json",
                headers=headers)
            passed &= run_test("Invalid type rejected", 400, response.status_code)
    
    except Exception as e:
        passed &= run_test("Input validation", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_secret_key_configured():
    print("\n=== 7. Secret Key Configuration ===")
    passed = True
    
    try:
        from dashboard.app import app
        passed &= run_test("Flask secret_key set", True, bool(app.secret_key))
        passed &= run_test("Secret key is string", True, isinstance(app.secret_key, str))
        passed &= run_test("Secret key length > 16", True, len(app.secret_key) > 16)
    except Exception as e:
        passed &= run_test("Secret key", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_docker_healthcheck():
    print("\n=== 8. Docker Healthcheck ===")
    passed = True
    
    try:
        with open("Dockerfile", "r") as f:
            content = f.read()
        
        # Check that curl is installed
        passed &= run_test("curl installed", True, "curl" in content)
        
        # Check healthcheck uses curl or python
        passed &= run_test("Healthcheck uses curl/python", 
            True, 
            "curl" in content or "python" in content)
        
        # Check no requests import in healthcheck
        passed &= run_test("No requests in healthcheck", 
            True, 
            'import requests' not in content.lower() or "requests" in open("requirements.txt").read())
    
    except Exception as e:
        passed &= run_test("Docker healthcheck", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_session_security():
    print("\n=== 9. Session Security ===")
    passed = True
    
    try:
        from api.auth import SESSION_TIMEOUT_MINUTES
        passed &= run_test("Session timeout configured", True, SESSION_TIMEOUT_MINUTES > 0)
        passed &= run_test("Session timeout reasonable", True, SESSION_TIMEOUT_MINUTES <= 1440)
    except Exception as e:
        passed &= run_test("Session security", True, False)
        print(f"         ERROR: {e}")
    
    return passed


def test_no_error_leakage():
    print("\n=== 10. Error Leakage Prevention ===")
    passed = True
    
    try:
        from dashboard.app import app
        
        with app.test_client() as client:
            # Test 404 handler
            response = client.get("/nonexistent_page")
            passed &= run_test("404 returns JSON", True, response.content_type == "application/json")
            
            # Test that error response doesn't contain sensitive info
            data = json.loads(response.data)
            passed &= run_test("No stack trace in 404", True, "traceback" not in str(data).lower())
    
    except Exception as e:
        passed &= run_test("Error leakage", True, False)
        print(f"         ERROR: {e}")
    
    return passed


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("========== SENTINEL-X PHASE 8 SECURITY HARDENING ==========")
    
    results = []
    results.append(("Path Traversal Prevention", test_path_traversal_blocked()))
    results.append(("Authentication Required", test_authentication_required()))
    results.append(("Login/Logout Flow", test_login_logout()))
    results.append(("CSRF Protection", test_csrf_protection()))
    results.append(("Rate Limiting", test_rate_limiting()))
    results.append(("Input Validation", test_input_validation()))
    results.append(("Secret Key Configured", test_secret_key_configured()))
    results.append(("Docker Healthcheck", test_docker_healthcheck()))
    results.append(("Session Security", test_session_security()))
    results.append(("Error Leakage Prevention", test_no_error_leakage()))
    
    print("\n========== PHASE 8 SECURITY RESULTS ==========")
    passed_count = 0
    for name, result in results:
        status = "PASS" if result else "FAIL"
        if result:
            passed_count += 1
        print(f"  [{status}] {name}")
    
    print(f"\nTotal: {passed_count}/{len(results)} passed")
    if passed_count == len(results):
        print("ALL TESTS PASSED — Security hardening complete.")
    else:
        print("SOME TESTS FAILED — Review failures above.")
