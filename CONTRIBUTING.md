# 🤝 Contributing to SentinelX

First of all, thank you for contributing to SentinelX.

Our goal is to build a modern AI Edge Surveillance Platform that is modular, scalable, and easy to maintain.

Please read these guidelines before making changes.

---

# 📌 Project Philosophy

SentinelX follows a modular architecture.

Every module should be independent.

Avoid creating large files that handle multiple responsibilities.

Instead,

One module = One responsibility.

Example

Good

events/
    fall_detector.py
    crowd_detector.py
    running_detector.py

Bad

events.py

---

# Repository Structure

Never move folders unless discussed with the team.

Current structure

```

ai/
alerts/
analytics/
api/
camera/
core/
dashboard/
database/
docs/
events/
evidence/
logs/
models/
services/
tests/
utils/

```

---

# Branch Naming

Always create a feature branch.

Good examples

```

feature/dashboard-ui

feature/fire-detection

feature/analytics

feature/reports

bugfix/timeline

bugfix/evidence

```

Never commit directly to

```

main

```

---

# Commit Messages

Use meaningful commit messages.

Good

```

Added crowd density detector

Improved dashboard timeline

Fixed evidence duplication

Added IP camera support

```

Bad

```

update

done

fixed

123

```

---

# Pull Requests

Before opening a Pull Request

✔ Code runs successfully

✔ No syntax errors

✔ No debug print statements

✔ README updated if required

✔ Screenshots included for UI changes

---

# Coding Standards

Python

✔ Follow PEP8

✔ Small functions

✔ Descriptive variable names

✔ Add comments only when necessary

Example

Good

```python
person_count = 5
```

Bad

```python
x = 5
```

---

# Folder Responsibilities

## AI

Only detection logic.

No dashboard code.

---

## Dashboard

Only frontend.

No AI code.

---

## Events

Only event generation.

No UI.

---

## Evidence

Only screenshot/video handling.

---

## Services

Business logic.

---

## Database

Only database operations.

---

# Testing

Run tests before pushing.

```

pytest

```

---

# Documentation

Every new module should include

Purpose

Inputs

Outputs

Dependencies

Example

```python
"""
Fall Detector

Input:
YOLO results

Output:
Fall event dictionary
"""
```

---

# Issue Reporting

When reporting a bug include

Operating System

Python Version

Error Message

Steps to Reproduce

Expected Behaviour

Actual Behaviour

Screenshots if possible

---

# Feature Requests

Before implementing a large feature

Open an Issue

↓

Discuss

↓

Design

↓

Implement

↓

Review

---

# Code Review Checklist

Before merging

✔ Code works

✔ No duplicate logic

✔ Proper folder placement

✔ Proper naming

✔ Documentation updated

✔ Doesn't break existing modules

---

# Current Development Priorities

High Priority

- Dashboard UI
- Reports
- Analytics
- Weapon Detection
- Database

Medium Priority

- Multi Camera
- Notifications
- User Login

Future

- Face Recognition
- Fire Detection
- Smoke Detection
- Mobile App
- Cloud Platform

---

# Questions?

If you're unsure where a feature belongs,

don't guess.

Open an issue or ask the Project Lead before implementing.

---

 SentinelX.

Together we're creating an intelligent surveillance platform.