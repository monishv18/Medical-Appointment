import json
from pathlib import Path
from typing import List, Dict, Any

DB_PATH = Path("backend/db/appointments.json")
SCHEDULE_PATH = Path("backend/db/doctor_schedule.json")

APPOINTMENT_TYPES = {
    "consultation": 30,
    "followup": 15,
    "physical": 45,
    "specialist": 60,
    "general": 30,
}


def _read_json(path: Path):
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_appointments() -> List[Dict[str, Any]]:
    data = _read_json(DB_PATH)
    return data if isinstance(data, list) else []


def save_appointments(data: List[Dict[str, Any]]) -> None:
    _write_json(DB_PATH, data)


def load_doctor_schedule():
    data = _read_json(SCHEDULE_PATH)
    if data is None:
        raise FileNotFoundError(f"Doctor schedule not found at {SCHEDULE_PATH}")
    return data

