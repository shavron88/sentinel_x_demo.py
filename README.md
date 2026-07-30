# 🛡 SentinelX

> **AI Edge Surveillance & Incident Intelligence Platform**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)]()
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green)]()
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-red)]()
[![Flask](https://img.shields.io/badge/Flask-Web%20Dashboard-black)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)]()

---

# 🚀 Overview

SentinelX is an AI-powered Edge Surveillance Platform that transforms ordinary CCTV cameras into intelligent security systems.

Unlike traditional CCTV systems that only record footage, SentinelX continuously analyses live video streams, understands events in real time, detects security incidents, evaluates threat levels, stores evidence, and presents everything through a modern command dashboard.

The system is designed as an MVP (Minimum Viable Product) for hackathons and future commercial deployment.

---

# ❓ Problem Statement

Traditional CCTV systems suffer from several major limitations.

• They only record footage.

• Human operators must continuously watch multiple screens.

• Critical events are often missed.

• There is no automated threat analysis.

• Searching through hours of footage wastes valuable time.

• Security personnel receive information after incidents instead of during them.

Large organisations often have hundreds of cameras, making continuous manual monitoring practically impossible.

---

# 💡 Our Solution

SentinelX introduces an AI intelligence layer between CCTV cameras and security operators.

Instead of simply recording video, SentinelX analyses every frame using computer vision and artificial intelligence.

The platform automatically:

- Detects people
- Detects vehicles
- Tracks movement
- Identifies restricted area intrusions
- Detects loitering
- Detects falls
- Detects abandoned objects
- Performs crowd analysis
- Calculates threat level
- Stores evidence
- Generates alerts
- Displays everything in a real-time dashboard

---

# 🎯 Vision

Our vision is to create an affordable AI Edge Security Platform that can upgrade existing CCTV systems without replacing current infrastructure.

Instead of purchasing entirely new AI cameras, organisations can simply connect SentinelX to their existing surveillance network.

Future commercial versions will support:

- Smart Cities
- Airports
- Shopping Malls
- Universities
- Factories
- Hospitals
- Government Buildings
- Railway Stations
- Banks
- Warehouses

---

# ⚡ Key Features

## Computer Vision

✔ Person Detection

✔ Vehicle Detection

✔ Multi Object Tracking

✔ Zone Detection

✔ Restricted Area Monitoring

✔ Crowd Detection

✔ Loitering Detection

✔ Fall Detection

✔ Running Detection

✔ Abandoned Object Detection

✔ Weapon Detection (In Progress)

---

## AI Intelligence

✔ Threat Level Calculation

✔ Rule Based Incident Engine

✔ Event Memory

✔ Behaviour Analysis

✔ Event Timeline

✔ Alert Prioritisation

✔ Incident Classification

---

## Dashboard

✔ Live Camera Feed

✔ Command Center UI

✔ Statistics Cards

✔ Incident Timeline

✔ Evidence Gallery

✔ Threat Meter

✔ Camera Status

✔ FPS Counter

✔ System Health

---

## Evidence Management

✔ Automatic Screenshot Capture

✔ Event-based Evidence Storage

✔ Evidence Gallery

✔ Screenshot History

✔ Timestamped Images

---

## Backend

✔ Flask Dashboard

✔ REST APIs

✔ Database Integration

✔ Modular Architecture

✔ Event Management

✔ Services Layer

✔ Analytics Layer

---

# 🏗 System Architecture

```

 CCTV Camera

↓

Camera Manager

↓

YOLOv8 Detector

↓

Tracking

↓

Event Engine

↓

Threat Intelligence

↓

Alert Manager

↓

Evidence Manager

↓

Dashboard

↓

Database

↓

Reports

```

Every video frame passes through this pipeline before reaching the dashboard.

---

# 🧠 AI Workflow

Frame

↓

Detection

↓

Tracking

↓

Behaviour Analysis

↓

Threat Calculation

↓

Alert Generation

↓

Evidence Saving

↓

Dashboard Update

↓

Database Storage

---

# 📸 Dashboard

SentinelX provides a modern Command Center dashboard designed for real-time surveillance.

The dashboard includes:

• Live Camera Feed

• AI Statistics

• Incident Timeline

• Evidence Gallery

• System Health

• Threat Indicator

• Camera Information

• FPS Monitoring

---

# 🌍 Future Commercial Vision

The current version is an MVP built for demonstration and hackathon purposes.

Future commercial releases will include:

• Edge AI Hardware

• Multi-Camera Support

• Cloud Dashboard

• Mobile App

• Face Recognition

• ANPR (License Plate Recognition)

• Fire Detection

• Smoke Detection

• PPE Detection

• Audio Event Detection

• Emergency Response Automation

---

# 📌 Current Status

Current Stage:

✅ Minimum Viable Product (MVP)

Status:

🟢 Active Development

Project Type:

AI Edge Surveillance Platform

Primary Language:

Python

Frontend:

HTML + CSS + JavaScript

Backend:

Flask

Computer Vision:

OpenCV + YOLOv8

---

# 📂 Repository Structure

SentinelX follows a modular architecture where every major component is separated into its own folder. This keeps the project scalable, maintainable, and easy for multiple developers to work on simultaneously.

```
SentinelX/
│
├── ai/
├── alerts/
├── analytics/
├── api/
├── camera/
├── core/
├── dashboard/
├── database/
├── docs/
├── events/
├── evidence/
├── logs/
├── models/
├── services/
├── tests/
├── utils/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── LICENSE
└── CHANGELOG.md
```

---

# 📁 ai/

The AI module contains the primary computer vision models responsible for object detection.

Current files:

```
ai/
    detector.py
```

### Responsibilities

- Load YOLOv8 model
- Run object detection
- Return bounding boxes
- Return confidence scores
- Return class IDs
- Return tracking information

This folder is the heart of SentinelX because every video frame first passes through this detector.

Future additions:

- Face Recognition
- PPE Detection
- Fire Detection
- Smoke Detection
- Pose Estimation

---

# 📁 alerts/

The Alerts module converts AI events into meaningful security alerts.

Current files:

```
alert_manager.py
incident_manager.py
intelligence_engine.py
```

### alert_manager.py

Responsible for

- Creating alerts
- Assigning severity
- Preventing duplicate alerts
- Preparing notifications

---

### intelligence_engine.py

This module evaluates security events.

It decides whether an event is

- LOW
- MEDIUM
- HIGH

using multiple factors including

- Zone
- Event type
- Duration
- Crowd size

---

### incident_manager.py

Responsible for incident history and event organisation.

Future versions may integrate

- Email alerts
- SMS
- WhatsApp
- Push notifications

---

# 📁 analytics/

Current file

```
heatmap.py
```

Responsible for

- Crowd movement analysis
- Heatmap generation
- Popular area detection

Future analytics include

- Traffic flow
- Queue analysis
- Occupancy reports

---

# 📁 api/

REST API endpoints used by the dashboard and future mobile applications.

Files

```
auth.py
cameras.py
events.py
health.py
routes.py
```

Purpose

- Camera API
- Health API
- Authentication
- Events API
- Dashboard communication

Future versions will expose public REST APIs.

---

# 📁 camera/

Contains camera communication layer.

Current file

```
camera_manager.py
```

Responsibilities

- Connect USB webcam
- Connect IP Camera
- Read frames
- Handle camera failures
- Reconnect automatically

Future versions

- Multi-camera support
- RTSP streams
- ONVIF cameras
- NVR integration

---

# 📁 core/

The project brain.

Current files

```
engine.py
incident_manager.py
```

engine.py controls the complete processing pipeline.

Pipeline

```
Camera

↓

Detection

↓

Tracking

↓

Events

↓

Threat Analysis

↓

Evidence

↓

Dashboard
```

Every module communicates through this engine.

---

# 📁 dashboard/

Contains the complete web interface.

Files include

```
templates/
static/
app.py
store.py
stream.py
timeline.py
```

### app.py

Runs Flask dashboard.

---

### stream.py

Streams live MJPEG video.

---

### store.py

Stores dashboard statistics.

---

### timeline.py

Maintains live incident timeline.

---

### templates/

Contains HTML pages.

Current pages

- Dashboard
- Cameras
- Evidence
- Analytics
- Reports
- Settings

---

### static/

Contains

CSS

JavaScript

Images

Fonts (future)

Icons (future)

---

# 📁 database/

Database layer.

Files

```
database.db
db.py
models.py
```

Stores

- Incidents
- Events
- Alerts
- Evidence metadata
- Reports

Future versions will migrate to PostgreSQL.

---

# 📁 docs/

Project documentation.

Contains

```
api.md
architecture.md
deployment.md
hardware.md
roadmap.md
```

Purpose

- Developer documentation
- API reference
- Hardware plans
- Deployment guide

---

# 📁 events/

One of the largest modules.

Responsible for recognising security events.

Current modules include

```
event_manager.py

memory_manager.py

people_counter.py

zone_manager.py

crowd_detector.py

weapon_detector.py

fall_detector.py

line_crossing.py

running_detector.py

abandoned_object.py

rule_engine.py
```

Each detector is independent.

This allows developers to improve one detector without affecting others.

---

### event_manager.py

Creates standard event objects.

---

### memory_manager.py

Stores temporary tracking memory.

Used for

- Loitering
- Behaviour analysis

---

### people_counter.py

Counts

- Entry
- Exit
- Occupancy

---

### zone_manager.py

Creates

SAFE

ENTRY

RESTRICTED

zones.

---

### crowd_detector.py

Detects crowd density.

---

### fall_detector.py

Detects fallen persons.

---

### running_detector.py

Detects abnormal running.

---

### weapon_detector.py

Future AI module.

---

### abandoned_object.py

Detects unattended objects.

---

### rule_engine.py

Combines all event outputs into security decisions.

---

# 📁 evidence/

Responsible for digital evidence.

Current files

```
evidence_manager.py

screenshots/
```

Functions

- Save screenshots
- Organise evidence
- Prevent duplicates
- Evidence gallery

Future

- Video clips
- Cloud storage
- Digital signatures

---

# 📁 logs/

Stores

- Application logs
- Error logs

Used for debugging.

---

# 📁 models/

Stores AI models.

Current models

```
yolov8n.pt

yolov8m.pt
```

Developers may replace these with larger or custom-trained models.

---

# 📁 services/

Business logic layer.

Contains

```
alert_service.py

detection_service.py

notification_service.py

tracking_service.py
```

Purpose

Keep business logic separate from UI and AI code.

---

# 📁 tests/

Contains automated tests.

Current tests include

- Detector tests
- Dashboard tests
- Database tests
- Alert tests
- Event tests

Future goal

100% module coverage.

---

# 📁 utils/

Shared helper functions.

Current modules

```
file_utils.py

image_utils.py

time_utils.py
```

Used to avoid duplicate code across the project.

---

# Root Files

## app.py

Application entry point.

Starts SentinelX.

---

## config.py

Global configuration.

Stores

- Camera source
- Thresholds
- Model paths

---

## CHANGELOG.md

Records project changes.

---

## requirements.txt

Lists Python dependencies.

---

## LICENSE

Project licence.

---

## README.md

Main documentation.


---

# 🧠 SentinelX AI Processing Pipeline

Understanding the processing pipeline is essential before contributing to SentinelX.

Every frame captured from the camera passes through multiple independent AI modules before finally reaching the dashboard.

The complete pipeline is shown below.

```
                Camera
                   │
                   ▼
        Camera Manager
                   │
                   ▼
          YOLOv8 Detector
                   │
                   ▼
        Object Tracking
                   │
                   ▼
         Event Detection Layer
                   │
     ┌─────────────┼─────────────┐
     ▼             ▼             ▼
 Zone Engine   Memory Engine   Rule Engine
     │             │             │
     └─────────────┼─────────────┘
                   ▼
      Intelligence Engine
                   │
                   ▼
         Alert Manager
                   │
         ┌─────────┴──────────┐
         ▼                    ▼
 Evidence Manager      Dashboard Store
         │                    │
         ▼                    ▼
 Evidence Gallery      Live Dashboard
```

---

# 🎥 Step 1 — Camera Capture

Module

```
camera/camera_manager.py
```

Responsibilities

- Connect USB Camera
- Connect IP Camera
- Read live frames
- Recover from connection failures
- Provide continuous video stream

Output

```
OpenCV Frame
```

---

# 🤖 Step 2 — AI Detection

Module

```
ai/detector.py
```

YOLOv8 processes every frame.

The detector recognises objects such as

- Person
- Car
- Bus
- Motorcycle
- Truck

Each object contains

- Class ID
- Confidence
- Bounding Box
- Tracking ID (ByteTrack)

Example

```
Person

Confidence: 96%

Track ID: 14

Bounding Box:
x1,y1,x2,y2
```

---

# 👣 Step 3 — Object Tracking

Unlike simple detection,

SentinelX tracks people across multiple frames.

Every person receives a unique Track ID.

Example

```
Person A

Track ID = 5
```

Even after moving,

Track ID remains

```
5
```

This enables

- Loitering Detection

- Behaviour Analysis

- Evidence Management

- People Counting

---

# 🗺 Step 4 — Zone Detection

Module

```
events/zone_manager.py
```

SentinelX divides the camera view into security zones.

Example

```
+--------------------------+

 SAFE

+-----------+--------------+

 ENTRY

+-----------+--------------+

 RESTRICTED

+--------------------------+
```

Every tracked person belongs to exactly one zone.

Possible values

- SAFE

- ENTRY

- RESTRICTED

---

# 🧠 Step 5 — Memory Engine

Module

```
events/memory_manager.py
```

The memory engine remembers

- First appearance

- Current position

- Previous position

- Time inside zone

This allows

- Loitering Detection

- Movement History

- Zone Transition Analysis

---

# 🚶 Step 6 — Behaviour Detection

Different AI modules analyse different activities.

---

## Loitering

Person stays in one location for a long period.

↓

LOITERING event

---

## Running

Person moves abnormally fast.

↓

RUNNING event

---

## Crowd

Large number of people detected.

↓

CROWD event

---

## Fall

Person collapses.

↓

FALL_DETECTED

---

## Abandoned Object

Bag remains without owner.

↓

ABANDONED_OBJECT

---

## Weapon

Weapon detected.

↓

WEAPON_DETECTED

(Currently experimental)

---

# ⚖ Rule Engine

Module

```
events/rule_engine.py
```

Combines multiple AI outputs.

Example

```
Running

+

Restricted Zone

+

Night Time

↓

HIGH THREAT
```

Instead of relying on one detector,

SentinelX combines evidence.

---

# 🚨 Intelligence Engine

Module

```
alerts/intelligence_engine.py
```

Calculates threat level.

Current threat levels

```
LOW

MEDIUM

HIGH
```

Evaluation factors

- Event Type

- Zone

- Duration

- Crowd Density

- Behaviour

Future versions may include

- Time of Day

- Camera Priority

- User Permissions

---

# 📢 Alert Manager

Module

```
alerts/alert_manager.py
```

Responsible for

Creating

Prioritising

Formatting

Dispatching

alerts.

Example

```
HIGH

Weapon Detected

Restricted Area
```

---

# 📸 Evidence Manager

Module

```
evidence/evidence_manager.py
```

When required,

SentinelX stores evidence.

Evidence includes

- Screenshot

- Timestamp

- Event Type

- Track ID

- Location

Duplicate screenshots are prevented using cooldown logic.

---

# 💾 Dashboard Store

Module

```
dashboard/store.py
```

Stores live statistics.

Examples

```
Persons

Vehicles

Threat

FPS

Alerts
```

The dashboard refreshes automatically using JavaScript.

---

# 🖥 Dashboard

The operator views

- Live Camera

- Timeline

- Threat Level

- Alerts

- Evidence

- Statistics

Everything updates in real time.

---

# 🔄 Processing Loop

The engine continuously repeats this cycle.

```
Read Camera

↓

Detect Objects

↓

Track Objects

↓

Update Memory

↓

Detect Behaviour

↓

Calculate Threat

↓

Save Evidence

↓

Update Dashboard

↓

Repeat
```

This loop runs continuously until the application is stopped.

---

# ⚡ Why Modular Design?

Every feature is isolated.

Example

```
Want Fire Detection?

↓

Create

events/fire_detector.py

↓

Register

inside Event Manager

↓

Done
```

No other modules require modification.

This makes SentinelX easy to maintain and expand.

---

# 🎯 Current AI Capabilities

| Feature | Status |
|----------|--------|
| Person Detection | ✅ Complete |
| Vehicle Detection | ✅ Complete |
| Object Tracking | ✅ Complete |
| Zone Detection | ✅ Complete |
| People Counting | ✅ Complete |
| Loitering Detection | ✅ Complete |
| Crowd Detection | ✅ Complete |
| Running Detection | ✅ Complete |
| Fall Detection | ✅ Complete |
| Abandoned Object Detection | ✅ Complete |
| Weapon Detection | 🚧 In Progress |
| Face Recognition | 📅 Planned |
| Fire Detection | 📅 Planned |
| Smoke Detection | 📅 Planned |
| License Plate Recognition | 📅 Planned |
| PPE Detection | 📅 Planned |

---


---

# 🖥 Dashboard Architecture

SentinelX includes a modern web-based Command Center built using Flask, HTML, CSS and JavaScript.

The dashboard is designed for security operators who need real-time situational awareness.

Instead of watching multiple CCTV screens, operators receive AI-generated intelligence, alerts, and evidence through a single interface.

---

# 🏗 Dashboard Architecture

```
                     Flask Server
                          │
          ┌───────────────┼────────────────┐
          ▼               ▼                ▼
     HTML Templates   REST APIs      Video Stream
          │               │                │
          └─────── JavaScript ─────────────┘
                          │
                          ▼
                 Browser Dashboard
```

---

# Dashboard Pages

The dashboard is divided into multiple pages.

```
Dashboard
Cameras
Incidents
Evidence
Analytics
Reports
Settings
```

Each page has its own responsibility.

---

# 🏠 Dashboard Page

File

```
dashboard/templates/index.html
```

Purpose

Main Command Center.

Displays

- Live camera feed

- Person count

- Vehicle count

- Alerts

- FPS

- Threat level

- Camera status

- Incident timeline

- Evidence gallery

- System health

This page is the operator's primary interface.

---

# 📹 Cameras Page

File

```
dashboard/templates/cameras.html
```

Purpose

Manage connected cameras.

Future Features

- Camera list

- Camera status

- Camera health

- Camera settings

- Add new camera

- Remove camera

- RTSP configuration

- IP Camera configuration

---

# 🚨 Incidents Page

File

```
dashboard/templates/incidents.html
```

Purpose

Displays every security incident detected.

Examples

```
09:32

LOITERING

Restricted Area

HIGH
```

Future Features

- Search

- Filters

- Export

- Incident Details

- Investigation Mode

---

# 📸 Evidence Page

File

```
dashboard/templates/evidence.html
```

Purpose

Displays saved evidence.

Evidence includes

- Screenshot

- Timestamp

- Event Type

- Camera

Future Features

- Video Clip

- Download

- Delete

- Cloud Backup

- Digital Signature

---

# 📊 Analytics Page

File

```
dashboard/templates/analytics.html
```

Purpose

Visualises historical security data.

Examples

- Daily Incidents

- Hourly Activity

- Crowd Heatmaps

- Zone Statistics

- Camera Usage

- Threat Distribution

Future versions will use

Chart.js

or

Apache ECharts.

---

# 📄 Reports Page

File

```
dashboard/templates/reports.html
```

Purpose

Generate security reports.

Possible reports

- Daily Report

- Weekly Report

- Monthly Report

- Incident Summary

- Evidence Summary

- Threat Analysis

Reports may be exported as

- PDF

- Excel

- CSV

---

# ⚙ Settings Page

File

```
dashboard/templates/settings.html
```

Purpose

Application configuration.

Examples

- Camera Source

- Detection Confidence

- Alert Cooldown

- Theme

- User Accounts

- AI Settings

- Database

- Notifications

---

# 🎨 Frontend Assets

Located inside

```
dashboard/static/
```

Contains

```
css/

js/

images/
```

---

# CSS Files

```
style.css

cards.css

camera.css

sidebar.css
```

Purpose

Layout

Cards

Sidebar

Camera

Responsive Design

Animations

---

# JavaScript Files

```
dashboard.js

camera.js

alerts.js

app.js
```

---

## dashboard.js

Updates

- Statistics

- Threat Meter

- Timeline

- Gallery

---

## alerts.js

Handles

Alert rendering

Alert animation

Alert refresh

---

## camera.js

Responsible for

Live stream behaviour

Camera refresh

Future zoom controls

---

## app.js

General dashboard logic.

---

# Flask Dashboard

Main file

```
dashboard/app.py
```

Responsibilities

- Run Flask

- Register routes

- Render templates

- Return JSON

- Serve dashboard

---

# Dashboard Store

File

```
dashboard/store.py
```

Purpose

Stores live values.

Example

```
Persons

Vehicles

Threat

FPS

Alerts
```

These values are updated by the Engine.

---

# Stream Module

File

```
dashboard/stream.py
```

Purpose

Converts OpenCV frames into MJPEG stream.

Flow

```
Camera

↓

OpenCV Frame

↓

JPEG

↓

MJPEG Stream

↓

Browser
```

---

# Timeline Module

File

```
dashboard/timeline.py
```

Purpose

Stores

Recent incidents

Displayed inside

Incident Timeline.

---

# REST API

SentinelX communicates through lightweight REST endpoints.

Current APIs include

```
/stats

/timeline

/video_feed
```

Additional API modules are located in

```
api/
```

---

# API Modules

```
auth.py

routes.py

health.py

events.py

cameras.py
```

---

## Authentication API

Future functionality

- Login

- Logout

- JWT

- User Roles

---

## Cameras API

Future functionality

```
GET

POST

DELETE

PATCH
```

Manage cameras remotely.

---

## Events API

Purpose

Return

- Incident List

- Event History

- Statistics

---

## Health API

Purpose

Monitor

- AI Engine

- Database

- Camera

- GPU

- Memory

Example

```
Status

Running

FPS

28

Camera

Online

Database

Connected
```

---

# Frontend Data Flow

```
Engine

↓

Dashboard Store

↓

Flask API

↓

JavaScript

↓

HTML

↓

Browser
```

---

# Video Streaming Flow

```
Camera

↓

OpenCV

↓

Frame

↓

JPEG

↓

Flask

↓

Browser

↓

Live Dashboard
```

---

# Current Dashboard Features

| Feature | Status |
|----------|--------|
| Live Camera | ✅ |
| AI Statistics | ✅ |
| Threat Level | ✅ |
| Timeline | ✅ |
| Evidence Gallery | ✅ |
| System Health | ✅ |
| Camera Status | ✅ |
| FPS Counter | ✅ |
| Sidebar Navigation | 🚧 |
| Reports | 🚧 |
| Analytics Charts | 🚧 |
| Multi Camera | 📅 |
| User Login | 📅 |

---

# Future Dashboard Improvements

The dashboard roadmap includes

- Dark/Light Theme

- Interactive Maps

- Multiple Camera Grid

- Live Notifications

- Notification Bell

- User Profiles

- Role Based Access

- Fullscreen Camera

- AI Explainability

- Report Generator

- Mobile Responsive UI

- Progressive Web App

- Cloud Dashboard

---



---

# 💻 Development Environment

SentinelX is currently developed and tested on Windows using Python.

Recommended Environment

| Component | Recommendation |
|-----------|---------------|
| OS | Windows 10 / Windows 11 |
| Python | 3.11+ |
| RAM | 8 GB Minimum |
| Recommended RAM | 16 GB |
| GPU | Optional (NVIDIA Recommended) |
| IDE | Visual Studio Code |
| Git | Latest Version |

---

# 📦 Required Software

Install the following before running SentinelX.

## Python

Download

https://www.python.org/downloads/

Verify installation

```bash
python --version
```

---

## Git

Download

https://git-scm.com/downloads

Verify

```bash
git --version
```

---

## Visual Studio Code

Download

https://code.visualstudio.com/

Recommended Extensions

- Python
- Pylance
- GitLens
- Black Formatter
- Error Lens

---

# 📥 Clone Repository

Clone the project

```bash
git clone https://github.com/YOUR_USERNAME/SentinelX.git
```

Move into project

```bash
cd SentinelX
```

---

# 📦 Install Dependencies

Create virtual environment

Windows

```bash
python -m venv venv
```

Activate

CMD

```bash
venv\Scripts\activate
```

PowerShell

```powershell
venv\Scripts\Activate.ps1
```

Git Bash

```bash
source venv/Scripts/activate
```

Install packages

```bash
pip install -r requirements.txt
```

---

# ▶ Running SentinelX

Start the application

```bash
python app.py
```

or

```bash
python main.py
```

(depending on the project entry point)

Dashboard

```
http://127.0.0.1:5000
```

---

# 📷 Camera Configuration

USB Camera

Inside

```
config.py
```

Example

```python
CAMERA_SOURCE = 0
```

IP Camera

```python
CAMERA_SOURCE = "rtsp://username:password@ip-address:554/stream"
```

Example

```python
CAMERA_SOURCE = "rtsp://admin:admin123@192.168.1.100:554/stream"
```

---

# 🧠 AI Models

Current models

```
models/

yolov8n.pt

yolov8m.pt
```

Default

```
YOLOv8n
```

Developers can switch to

- YOLOv8s
- YOLOv8m
- YOLOv8l
- Custom trained models

---

# 📂 Evidence

Evidence is stored inside

```
evidence/screenshots/
```

Every screenshot contains

- Timestamp

- Event Type

- Track ID (where available)

Evidence is generated automatically.

---

# 📝 Logs

Application logs

```
logs/app.log
```

Error logs

```
logs/errors.log
```

Useful for debugging.

---

# 🧪 Running Tests

Current tests

```
tests/
```

Run all tests

```bash
pytest
```

Run a single test

```bash
pytest tests/test_detector.py
```

---

# 🔄 Development Workflow

Every contributor should follow the same workflow.

---

## Step 1

Clone repository

```bash
git clone
```

---

## Step 2

Create a new branch

```bash
git checkout -b feature/your-feature
```

Examples

```
feature/dashboard

feature/weapon-detection

feature/report-generator
```

---

## Step 3

Write code

---

## Step 4

Test locally

---

## Step 5

Commit

```bash
git add .

git commit -m "Implemented crowd detection improvements"
```

---

## Step 6

Push

```bash
git push origin feature/your-feature
```

---

## Step 7

Open Pull Request

Repository Owner reviews

↓

Merge into main

---

# 📌 Coding Guidelines

Follow these rules.

✔ Keep modules independent.

✔ Write descriptive variable names.

✔ Avoid hardcoded values.

✔ Reuse utility functions.

✔ Add comments for complex logic.

✔ Test before committing.

✔ Keep functions small.

---

# 📋 Team Roles

Current recommended team structure

## Project Lead

Responsibilities

- Architecture
- AI Pipeline
- Code Review
- Final Integration

---

## Computer Vision Developer

Responsible for

- YOLO

- Tracking

- Detection

- Model Training

---

## Backend Developer

Responsible for

- Flask

- APIs

- Database

- Services

---

## Frontend Developer

Responsible for

- Dashboard

- HTML

- CSS

- JavaScript

- User Experience

---

## Database Developer

Responsible for

- SQLite

- Models

- Reports

- Analytics

---

## QA / Testing

Responsible for

- Bug Testing

- Performance Testing

- Unit Tests

- Integration Tests

---

# 🛣 MVP Roadmap

## ✅ Completed

✔ Live Camera Streaming

✔ Person Detection

✔ Vehicle Detection

✔ Object Tracking

✔ Zone Detection

✔ Threat Engine

✔ Alert Manager

✔ Evidence Capture

✔ Dashboard

✔ Timeline

✔ Evidence Gallery

✔ Camera Status

✔ System Health

✔ FPS Counter

✔ Crowd Detection

✔ Loitering Detection

✔ Running Detection

✔ Fall Detection

✔ Abandoned Object Detection

---

## 🚧 In Progress

- Weapon Detection

- Reports

- Analytics

- Better Dashboard UI

- Sidebar Navigation

- Database Improvements

---

## 📅 Planned

- Face Recognition

- Fire Detection

- Smoke Detection

- Multiple Cameras

- Mobile Dashboard

- Cloud Dashboard

- User Authentication

- Notification System

- Role Based Access

- Report Generator

---

# 🎯 Hackathon Goal

Deliver a fully functional MVP capable of

- Connecting to a CCTV/IP Camera
- Detecting people and vehicles
- Detecting suspicious events
- Calculating threat level
- Capturing evidence
- Displaying live information through the dashboard

The focus is demonstrating an end-to-end intelligent surveillance workflow rather than building production-grade hardware.

---

# 🤝 Contribution Rules

Every contribution should

✔ Compile successfully

✔ Pass existing tests

✔ Follow folder structure

✔ Include meaningful commit messages

✔ Avoid breaking existing functionality

---

# ⭐ Acknowledgements

SentinelX is built using open-source technologies including

- Python
- Flask
- OpenCV
- Ultralytics YOLOv8
- NumPy

Special thanks to the open-source community for providing the tools that make this project possible.

---



---

# 🔌 API Reference

SentinelX exposes REST endpoints used by the dashboard and future integrations.

---

## GET /video_feed

Returns the live MJPEG stream from the active camera.

Response

```
multipart/x-mixed-replace
```

Used by

- Dashboard
- Camera Page

---

## GET /stats

Returns current AI statistics.

Example Response

```json
{
    "persons":4,
    "vehicles":2,
    "alerts":1,
    "threat":"MEDIUM",
    "fps":27
}
```

---

## GET /timeline

Returns recent incidents.

Example

```json
{
    "timeline":[
        {
            "time":"10:42",
            "event":"LOITERING",
            "zone":"RESTRICTED",
            "severity":"HIGH"
        }
    ]
}
```

---

## Future APIs

```
GET /api/cameras

POST /api/cameras

DELETE /api/cameras/{id}

GET /api/events

GET /api/evidence

POST /api/login

POST /api/logout

GET /api/reports

GET /api/analytics
```

---

# 🗄 Database Design

Current database

SQLite

Future database

PostgreSQL

---

## Main Tables

Users

Cameras

Events

Evidence

Alerts

Reports

Analytics

---

## Event Record

Every detected event should contain

- Event ID
- Timestamp
- Camera ID
- Track ID
- Event Type
- Zone
- Severity
- Screenshot
- Status

---

# 🔐 Security Considerations

SentinelX is designed with security in mind.

Current goals

✔ Local Processing

✔ No cloud dependency

✔ Private evidence storage

✔ Controlled access

Future security

- User authentication
- Role Based Access Control
- Encrypted evidence
- Secure API tokens
- HTTPS deployment
- Audit logs
- Digital evidence signing

---

# ⚡ Performance Optimisation

Current optimisations

✔ Frame resizing

✔ YOLO Nano model

✔ Event cooldown

✔ Memory cleanup

✔ Modular processing

Future improvements

- GPU acceleration

- TensorRT

- ONNX Runtime

- Multithreading

- Async processing

- Edge TPU

- NVIDIA Jetson support

---

# 🖥 Deployment Options

SentinelX is designed to run in multiple environments.

---

## Development

Windows

Python

VS Code

---

## Edge Computer

Mini PC

Intel NUC

Jetson Nano

Jetson Orin

Raspberry Pi (light workloads)

---

## Server

Ubuntu

Docker

NGINX

Gunicorn

---

## Cloud

Azure

AWS

Google Cloud

DigitalOcean

Future

Hybrid Edge + Cloud

---

# 📦 SentinelX Edge Box

The long-term vision is a dedicated hardware appliance.

Architecture

```
CCTV Camera

↓

SentinelX Edge Box

↓

AI Processing

↓

Dashboard

↓

Operator
```

The Edge Box will connect to existing CCTV cameras without replacing them.

Planned hardware

- NVIDIA Jetson
- Intel NUC
- Coral TPU
- Industrial Mini PC

---

# 📱 Future Mobile Application

Planned features

- Live camera view

- Push notifications

- Incident timeline

- Evidence review

- Camera health

- Threat monitoring

- Remote acknowledgement

---

# ☁ Cloud Platform

Future enterprise architecture

```
Edge Device

↓

Secure Gateway

↓

Cloud Server

↓

Web Dashboard

↓

Mobile App
```

This enables

- Multi-site monitoring
- Centralised reporting
- Remote administration
- Long-term analytics

---

# 💼 Business Model

SentinelX is intended to become a commercial AI surveillance platform.

Possible customers

- Shopping Malls
- Schools
- Universities
- Hospitals
- Factories
- Warehouses
- Banks
- Airports
- Railway Stations
- Government Buildings
- Residential Communities

Revenue opportunities

- Hardware sales
- Annual software licences
- Cloud subscriptions
- Premium AI modules
- Enterprise support
- Custom integrations

---

# 🏆 Hackathon Scope

The hackathon version focuses on demonstrating the complete AI workflow.

Objectives

✔ Detect people and vehicles

✔ Analyse behaviour

✔ Generate alerts

✔ Capture evidence

✔ Display information on a modern dashboard

✔ Support USB and IP cameras

The MVP intentionally excludes large-scale enterprise features such as cloud infrastructure and dedicated hardware.

---

# 📈 Product Roadmap

## Version 0.1 (Current MVP)

- Live dashboard
- AI detection
- Tracking
- Event engine
- Evidence capture
- Timeline
- Statistics
- Threat analysis

---

## Version 0.5

- Better dashboard UI
- Multiple cameras
- Analytics charts
- Improved reporting
- Camera management
- Better database integration

---

## Version 1.0

- Face recognition
- Fire detection
- Smoke detection
- Weapon detection
- License plate recognition
- Mobile application
- User authentication

---

## Version 2.0

- Edge AI hardware
- Cloud dashboard
- Distributed camera management
- Multi-site monitoring
- Enterprise reporting
- AI model updates
- Central management console

---

# 📚 Development Principles

Every new feature should follow these rules.

- Keep modules independent.
- Reuse existing services.
- Write maintainable code.
- Document new APIs.
- Add tests when possible.
- Preserve backwards compatibility.
- Keep the dashboard responsive.

---

# 🤝 Contributors

Project Lead

Responsible for

- System architecture
- AI pipeline
- Integration
- Final review

Contributors

- Computer Vision
- Backend
- Frontend
- Database
- QA & Testing
- Documentation

Every contributor is encouraged to document their work and submit pull requests for review.

---

# 📄 Licence

This project is released under the MIT License.

See the LICENSE file for details.

---

# 🙌 Final Notes

SentinelX began as a hackathon MVP but is designed with a modular architecture that can evolve into a commercial AI Edge Surveillance Platform.

The objective is not only to detect events, but to help security teams understand what is happening in real time, prioritise incidents, preserve evidence, and respond faster.

Every module has been designed to be replaceable and extensible, allowing future contributors to add new AI capabilities without rewriting the existing system.

Thank you for contributing to SentinelX.

Together, we are building a smarter and more proactive approach to video surveillance.

---