# MindCare – Standalone Dementia Cognitive Support App

## Requirements
- Python 3.10 or newer
- MySQL Server 8+
- VS Code recommended

## Setup on Windows
1. Open this folder in VS Code.
2. In MySQL Workbench, open and execute `database/schema.sql`.
3. Copy `.env.example` to `.env`; enter your MySQL password in `DB_PASSWORD`.
4. Open the VS Code terminal and run:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

If activation is blocked:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```
5. Visit http://127.0.0.1:5000
6. Add a patient, select the patient, and play any of the four games.

## Included
- Four independent agents: SequenceAgent, MissingObjectAgent, AssociationAgent, RecognitionAgent.
- Adaptive Game Manager registry in `agents/__init__.py`.
- Each patient's difficulty is stored independently for each game.
- MySQL patient, game, level, session and decision tables.
- Flask APIs and browser-based games.
- Caregiver dashboard with session averages and recent decisions.
- Emoji picture assets work offline.

## Agent policy
Each agent uses its own game parameters and a shared conservative decision policy. The policy examines up to three most recent sessions for that patient and game. It decreases difficulty when average accuracy is below 55%, completion is low, or hints are frequently needed. It increases difficulty only after three completed sessions with average accuracy at least 85% and low hint use. Otherwise it maintains the level. These are prototype usability thresholds, not validated clinical criteria.

## Important
This is a supportive cognitive activity prototype, not a diagnostic or screening instrument. Game performance must not be used to diagnose dementia or claim disease progression. Thresholds require testing and review by dementia-care professionals. Provide caregiver supervision, breaks and a way to stop activities.

For production, add authentication and role-based authorization, CSRF protection, HTTPS, secure secrets, data backups and privacy controls. In this demo, game answer data is sent to the browser for convenience; a production system should keep answer keys server-side and validate results on the backend. Reaction time is currently total activity time, not per-question timing.
