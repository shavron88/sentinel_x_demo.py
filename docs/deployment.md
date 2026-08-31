# SentinelX Deployment Guide

This guide covers deployment options for SentinelX, from local development to production environments.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Deployment](#local-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Configuration](#configuration)
5. [Multi-Camera Setup](#multi-camera-setup)
6. [Production Considerations](#production-considerations)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Python 3.11+
- CUDA-capable GPU (recommended) or CPU
- Webcam or IP/RTSP camera
- 4GB+ RAM (8GB+ recommended for multi-camera)
- 2GB+ free disk space for models and evidence

---

## Local Deployment

### 1. Clone Repository

```bash
git clone <repository-url>
cd sentinel_x_demo.py
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
copy .env.example .env
# Edit .env with your settings
```

### 5. Run Application

```bash
# Start Flask dashboard
python app.py

# Or use the main pipeline
python main.py
```

### 6. Access Dashboard

Open browser to `http://localhost:5000`

---

## Docker Deployment

### Quick Start

```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f sentinelx

# Stop
docker-compose down
```

### Build Only

```bash
docker build -t sentinelx .
```

### Run Container

```bash
docker run -d \
  --name sentinelx \
  --gpus all \
  -p 5000:5000 \
  -v $(pwd)/evidence:/app/evidence \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/models:/app/models \
  -v /dev/video0:/dev/video0 \
  --shm-size=2gb \
  sentinelx
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_DEBUG` | 0 | Enable Flask debug mode (0/1) |
| `FLASK_HOST` | 0.0.0.0 | Flask bind address |
| `FLASK_PORT` | 5000 | Flask port |
| `MODEL_PATH` | models/yolo11n.pt | YOLO11 model path |
| `CONFIDENCE_THRESHOLD` | 0.50 | Detection confidence threshold |
| `IOU_THRESHOLD` | 0.45 | NMS IoU threshold |
| `IMAGE_SIZE` | 640 | Inference resolution |
| `DEVICE` | auto | Inference device (auto/cpu/cuda) |
| `TARGET_CLASSES` | 0,1,2,3,5,7,24,26,28 | COCO classes to detect |
| `TRACKING_ENABLED` | 1 | Enable ByteTrack multi-object tracking |
| `CAMERA_SOURCE` | 0 | Default camera source |
| `CAMERAS` | | Multi-camera configuration |
| `EVENT_COOLDOWN` | 600 | Event cooldown in seconds |
| `LOITERING_THRESHOLD` | 30 | Loitering detection threshold (seconds) |
| `CROWD_THRESHOLD` | 5 | Crowd detection threshold |
| `MAX_QUEUE_SIZE` | 30 | Frame queue max size |
| `RTSP_TIMEOUT_MS` | 5000 | RTSP connection timeout |
| `RTSP_BUFFER_SIZE` | 1 | RTSP buffer size |
| `RTSP_TRANSPORT` | tcp | RTSP transport protocol |

---

## Multi-Camera Setup

### Using CAMERAS Environment Variable

```env
CAMERAS=Camera_01:0:Main Entrance,Camera_02:rtsp://admin:pass@192.168.1.100:554/stream1:Parking Lot,Camera_03:rtsp://admin:pass@192.168.1.101:554/stream1:Warehouse
```

### Camera Format

```
name:source:zone[:rtsp_timeout_ms]
```

- `name`: Unique camera identifier
- `source`: Camera index (0, 1, 2) or RTSP URL
- `zone`: Security zone name
- `rtsp_timeout_ms`: Optional RTSP timeout (default: 5000)

### Programmatic Setup

```python
from camera.camera_manager import camera_manager

# Add single camera
camera_manager.add_camera(
    name="Camera_01",
    ip_url=0,
    zone="Main Entrance"
)

# Add RTSP camera with custom config
camera_manager.add_camera(
    name="Camera_02",
    ip_url="rtsp://admin:pass@192.168.1.100:554/stream1",
    zone="Parking Lot",
    rtsp_config={
        "timeout_ms": 8000,
        "buffer_size": 1,
        "transport": "tcp"
    }
)

# Get all camera status
status = camera_manager.get_all_status()
```

---

## Production Considerations

### 1. Use Gunicorn

```bash
gunicorn --bind 0.0.0.0:5000 --workers 1 --threads 4 --timeout 120 dashboard.app:app
```

### 2. Enable HTTPS

Use a reverse proxy like Nginx:

```nginx
server {
    listen 443 ssl;
    server_name sentinelx.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /video_feed {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection "";
        chunked_transfer_encoding on;
    }
}
```

### 3. Database Backup

```bash
# Backup SQLite database
cp sentinelx.db backups/sentinelx_backup_$(date +%Y%m%d).db

# Or use the API endpoint
curl -X POST http://localhost:5000/api/system/backup
```

### 4. Log Rotation

```bash
# Using logrotate
cat > /etc/logrotate.d/sentinelx << EOF
/var/log/sentinelx/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

### 5. Systemd Service

```ini
[Unit]
Description=SentinelX AI Surveillance Platform
After=network.target

[Service]
Type=simple
User=sentinelx
WorkingDirectory=/opt/sentinelx
Environment="PATH=/opt/sentinelx/venv/bin"
ExecStart=/opt/sentinelx/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 1 --threads 4 dashboard.app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## Troubleshooting

### Camera Not Found

```bash
# Check available cameras
python -c "import cv2; print([i for i in range(5) if cv2.VideoCapture(i).isOpened()])"
```

### RTSP Connection Issues

- Verify RTSP URL format: `rtsp://username:password@host:port/path`
- Check firewall rules
- Try UDP transport: `RTSP_TRANSPORT=udp`
- Increase timeout: `RTSP_TIMEOUT_MS=10000`

### Out of Memory

- Reduce `MAX_QUEUE_SIZE`
- Use smaller model: `MODEL_PATH=models/yolo11n.pt`
- Reduce number of cameras
- Increase Docker `--shm-size`

### Low FPS

- Use GPU acceleration (CUDA)
- Reduce inference resolution
- Increase `FRAME_SKIP` to process fewer frames
- Use `yolo11n.pt` instead of `yolo11s.pt`/`yolo11m.pt` for lower latency

---

## Demo Mode

For hackathon presentations:

```bash
# Run with synthetic data (no camera required)
python main.py --demo

# Or set environment variable
export SENTINELX_DEMO=1
python app.py
```

Demo mode generates synthetic frames and detections for live demonstration without requiring physical cameras.

---

## Support

For issues and questions:
- GitHub Issues: <repository-url>/issues
- Documentation: See `/docs` folder
