# Changelog

All notable changes to SentinelX will be documented in this file.

The format is based on Keep a Changelog.

---

## [0.2.0] - 2026-08-31

### Changed

- Migrated object detection from YOLOv8 to YOLO11 (Ultralytics ecosystem)
- Default model is now `yolo11n.pt` (YOLO11 nano) — smallest real-time model for CPU edge inference
- Detection now applies configurable confidence threshold (0.50), IoU/NMS threshold (0.45), class filtering, and inference resolution (640) to improve accuracy and reduce false positives
- Added configurable `IMAGE_SIZE`, `DEVICE` (auto/cpu/cuda), `TARGET_CLASSES`, `TRACKING_ENABLED`, and `TRACKER` settings
- Detector exposes a clean interface (`load_model`, `detect`, `track`, `get_detections`, `release`) while preserving the legacy `infer_frame` contract
- Detection output now includes center point, timestamp, and camera_id alongside class_id, label, confidence, bbox, and tracking ID
- YOLO11 model moved to `models/` directory; `engine.py` no longer hardcodes model paths

## [0.1.0] - 2026-07-29

### Added

- Initial project architecture
- YOLOv8 object detection
- Person detection
- Vehicle detection
- Crowd detection
- Fall detection
- Loitering detection
- Running detection
- Abandoned object detection
- Weapon detection module (initial)
- Threat intelligence engine
- Alert manager
- Evidence manager
- Incident timeline
- Live dashboard
- Screenshot capture
- Camera manager
- Flask dashboard
- Documentation

### Changed

- Improved dashboard layout
- Added evidence gallery
- Added incident timeline
- Added threat indicator
- Added people counting

### Fixed

- Duplicate evidence capture
- Dashboard refresh issues
- Screenshot cooldown
- Timeline update bugs

---

## Planned

- Analytics dashboard
- Reports
- Multi-camera support
- Authentication
- Mobile app
- Fire detection
- Smoke detection