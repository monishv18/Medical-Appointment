"""
Pytest configuration and shared fixtures for testing the FastAPI application.
"""
import json
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def test_db_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary directory for test database files."""
    yield tmp_path


@pytest.fixture
def mock_appointments_file(test_db_dir: Path, monkeypatch) -> Generator[Path, None, None]:
    """Create a temporary appointments.json file and monkeypatch the database path."""
    test_file = test_db_dir / "appointments.json"
    # Initialize with empty list
    test_file.write_text(json.dumps([], indent=2))
    
    # Monkeypatch the DB_PATH in database module
    from backend.db import database
    original_path = database.DB_PATH
    database.DB_PATH = test_file
    
    yield test_file
    
    # Restore original path
    database.DB_PATH = original_path
    # Clean up test file
    if test_file.exists():
        test_file.unlink()


@pytest.fixture
def mock_schedule_file(test_db_dir: Path, monkeypatch) -> Generator[Path, None, None]:
    """Create a temporary doctor_schedule.json file and monkeypatch the schedule path."""
    test_file = test_db_dir / "doctor_schedule.json"
    # Default schedule
    schedule_data = {
        "working_hours": {
            "start": "09:00",
            "end": "17:00"
        }
    }
    test_file.write_text(json.dumps(schedule_data, indent=2))
    
    # Monkeypatch the SCHEDULE_PATH in database module
    from backend.db import database
    original_path = database.SCHEDULE_PATH
    database.SCHEDULE_PATH = test_file
    
    yield test_file
    
    # Restore original path
    database.SCHEDULE_PATH = original_path
    # Clean up test file
    if test_file.exists():
        test_file.unlink()


@pytest.fixture
def client(mock_appointments_file, mock_schedule_file) -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def auth_token(client: TestClient) -> str:
    """Get an access token by logging in."""
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """Get authorization headers with access token."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def refresh_token(client: TestClient) -> str:
    """Get a refresh token by logging in."""
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    return response.json()["refresh_token"]

