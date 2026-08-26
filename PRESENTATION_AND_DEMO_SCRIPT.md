# SentinelX — Final Presentation & Demo Script

## 1. Elevator Pitch (30 seconds)

> SentinelX is an AI-powered edge surveillance platform that turns any IP camera, RTSP stream, or webcam into an intelligent security system. It runs YOLOv8 detection + ByteTrack tracking in real time, automatically classifies threats, saves evidence, and pushes alerts to a live dashboard — all on local hardware, no cloud required.

---

## 2. System Architecture (60 seconds)

```
Camera / IP-RTSP / Webcam
        │
        ▼
   YOLOv8 + ByteTrack
        │
        ▼
   Event Engine (person, crowd, fall, weapon, line-crossing, abandoned object, restricted area)
        │
        ├──► Alert Manager (INFO / WARNING / CRITICAL)
        │
        ├──► Evidence Manager (screenshot + metadata → disk + SQLite)
        │
        └──► Dashboard Store (in-memory + DB)
                │
                ▼
           Flask Dashboard (SocketIO + REST API)
                │
                ├── Live Video Feed
                ├── Real-time KPIs
                ├── Event Timeline
                ├── Evidence Vault
                └── Camera Management
```

**Key components:**
- **Camera Manager** — Webcam, RTSP, HTTP/MJPEG with auto-reconnect
- **AI Pipeline** — YOLOv8 inference + ByteTrack multi-object tracking
- **Event Engine** — 7 specialized detectors (person, crowd, fall, weapon, line-crossing, abandoned object, restricted area)
- **Alert Manager** — Severity-based alerting (LOW / MEDIUM / HIGH / CRITICAL)
- **Evidence Manager** — Automatic frame capture and database logging
- **Dashboard** — Real-time Flask + SocketIO web interface

---

## 3. Live Demo Script (5 minutes)

### Setup (30s)
1. Open browser to `http://127.0.0.1:5000`
2. Login: `admin` / `sentinelx`
3. Show dashboard overview — point out:
   - Live camera feed
   - Real-time KPIs (persons, FPS, threat level)
   - AI Live Feed timeline
   - Evidence thumbnails

### Scenario 1: Person Detection (30s)
1. Navigate to **Cameras** page (`/cameras`)
2. Show the camera list with status indicators
3. Click **Add Camera** → show RTSP/HTTP/webcam form
4. Click **Test Connection** to verify stream
5. Return to Dashboard
6. Click **Demo Scenarios → Person Detection**
7. Narrate: *"Watch the event flow: a synthetic person is detected in the ENTRY zone. You'll see the event appear in the timeline, a toast notification, and an evidence screenshot saved to the vault."*
8. Point out:
   - Toast notification: "Person detected"
   - Event appears in AI Live Feed
   - Evidence thumbnail appears on dashboard
   - Stats update (persons: +1, threat: MEDIUM)

### Scenario 2: Restricted Area Intrusion (30s)
1. Click **Demo Scenarios → Restricted Area**
2. Narrate: *"This is a CRITICAL alert. A person has entered the RESTRICTED zone. The system immediately escalates the threat level."*
3. Point out:
   - Threat level changes to HIGH/CRITICAL
   - Alert toast with red warning
   - Evidence saved with HIGH severity
   - Stats update (high_severity_incidents: +1)

### Scenario 3: Crowd Detection (30s)
1. Click **Demo Scenarios → Crowd**
2. Narrate: *"The crowd detector triggers when 5+ persons are detected. This is useful for monitoring congestion or gathering threats."*
3. Point out:
   - CROWD_DETECTED event
   - MEDIUM severity
   - Dashboard timeline update

### Scenario 4: Fall Detection (30s)
1. Click **Demo Scenarios → Fall**
2. Narrate: *"The fall detector analyzes the aspect ratio of detected persons. When width > height, it flags a potential fall — critical for elderly care or emergency response."*
3. Point out:
   - FALL_DETECTED event
   - CRITICAL severity
   - Immediate alert escalation

### Scenario 5: Weapon Detection (30s)
1. Click **Demo Scenarios → Weapon**
2. Narrate: *"Weapon detection is trained on custom COCO classes. When a weapon is identified, the system immediately triggers a CRITICAL alert."*
3. Point out:
   - WEAPON_DETECTED event
   - CRITICAL severity
   - Evidence saved with weapon label

### Scenario 6: Line Crossing (30s)
1. Click **Demo Scenarios → Line Crossing**
2. Narrate: *"The virtual tripwire detects when a tracked object crosses a boundary line. Perfect for perimeter security."*
3. Point out:
   - LINE_CROSSING event
   - MEDIUM severity
   - Track ID preserved across detections

### Scenario 7: Abandoned Object (30s)
1. Click **Demo Scenarios → Abandoned Object**
2. Narrate: *"The abandoned object detector monitors stationary items. If a bag or suitcase remains unmoving for 20+ seconds, it triggers an alert."*
3. Point out:
   - ABANDONED_OBJECT event
   - HIGH severity
   - Duration metadata captured

### Evidence Review (30s)
1. Navigate to **Evidence** page (`/evidence`)
2. Show evidence grid with all 7+ captured screenshots
3. Click on an evidence item to show:
   - Full-size preview
   - AI-generated description
   - Metadata (tracking ID, camera, zone, timestamp)
   - Confidence score
4. Click **Download** to show export capability

### Incidents Review (20s)
1. Navigate to **Incidents** page (`/incidents`)
2. Show the event table with all triggered scenarios
3. Highlight severity filtering and search

### Wrap-up (20s)
1. Return to Dashboard
2. Summarize:
   - 7 event types demonstrated
   - Full pipeline: Event → Alert → Evidence → Dashboard
   - Real-time updates via SocketIO
   - Local processing, no cloud dependency
   - Scalable to multiple IP/RTSP cameras

---

## 4. Technical Highlights (for Q&A)

### Camera Connectivity
- **Webcam**: Direct OpenCV capture (DirectShow on Windows)
- **RTSP**: Configurable timeout, buffer size, TCP/UDP transport
- **HTTP/MJPEG**: URL-based stream ingestion
- **Auto-reconnect**: Exponential backoff with configurable max delay

### AI/ML Pipeline
- **Model**: YOLOv8 (YOLOv8m default)
- **Tracking**: ByteTrack multi-object tracking
- **Inference**: Async worker thread with queue-based frame processing
- **Performance**: ~10-30 FPS depending on hardware

### Event Detection
| Event Type | Trigger Condition | Severity |
|-----------|------------------|----------|
| Person Detection | YOLO class=person | MEDIUM |
| Crowd Detection | 5+ persons in frame | MEDIUM |
| Restricted Area | Person in zone=RESTRICTED | HIGH |
| Abandoned Object | Stationary object 20s+ | HIGH |
| Fall Detection | Person width > height | CRITICAL |
| Weapon Detection | Gun/knife class detected | CRITICAL |
| Line Crossing | Track crosses virtual line | MEDIUM |

### Reliability
- **Auto-recovery**: Worker restart on failure
- **Queue management**: Bounded frame queue with backpressure
- **Database**: SQLite with connection pooling
- **Health monitoring**: Real-time FPS, latency, error counting

---

## 5. Demo Checklist

- [ ] Dashboard loads at `http://127.0.0.1:5000`
- [ ] Login works (`admin` / `sentinelx`)
- [ ] Live camera feed displays
- [ ] All 7 demo scenarios trigger successfully
- [ ] Events appear in timeline within 2 seconds
- [ ] Evidence screenshots are saved and visible
- [ ] Stats update in real-time
- [ ] Toast notifications appear for HIGH/CRITICAL events
- [ ] Camera management UI works (add/test/remove cameras)
- [ ] No crashes during 50+ rapid triggers

---

## 6. Environment & Dependencies

```
Python 3.10+
Flask + Flask-SocketIO
OpenCV (cv2)
Ultralytics YOLOv8
SQLite3
numpy
```

**Start command:**
```bash
python app.py
```

**Access:**
- Dashboard: `http://127.0.0.1:5000`
- Default login: `admin` / `sentinelx`

---

## 7. Next Steps (Production)

- [ ] Replace demo injector with real YOLO inference on RTSP streams
- [ ] Add JWT authentication
- [ ] PostgreSQL / TimescaleDB for time-series events
- [ ] GPU acceleration (CUDA / TensorRT)
- [ ] Multi-zone polygon support
- [ ] Email/SMS/Push notification integrations
- [ ] Video clip export (MP4 with annotation overlay)
- [ ] LDAP/SSO integration
- [ ] Docker deployment with docker-compose
