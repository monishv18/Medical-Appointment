# Test Suite for Medical Appointment API

This directory contains comprehensive tests for the Medical Appointment Scheduling API.

## Test Structure

- `test_auth.py` - Authentication endpoint tests (login, refresh token, protected routes)
- `test_appointments.py` - Appointment booking tests (availability, booking, deletion, rescheduling)
- `test_root.py` - Root endpoint tests
- `conftest.py` - Shared fixtures and test configuration

## Running Tests

### Run all tests
```bash
poetry run pytest tests/
# or
pytest tests/
```

### Run with verbose output
```bash
poetry run pytest tests/ -v
```

### Run specific test file
```bash
poetry run pytest tests/test_auth.py
```

### Run specific test class
```bash
poetry run pytest tests/test_auth.py::TestLogin
```

### Run specific test
```bash
poetry run pytest tests/test_auth.py::TestLogin::test_login_success
```

### Run with coverage report
```bash
poetry run pytest tests/ --cov=backend --cov-report=term-missing
```

## Test Coverage

The test suite covers:

### Authentication Tests (14 tests)
- ✅ Successful login with correct credentials
- ✅ Login with invalid username/password
- ✅ Login with missing fields
- ✅ Token refresh functionality
- ✅ Protected endpoint access with/without tokens
- ✅ Invalid token handling

### Appointment Tests (17 tests)
- ✅ Get availability for different appointment types
- ✅ Book appointments successfully
- ✅ Handle conflicting time slots
- ✅ Validate appointment types
- ✅ Delete appointments
- ✅ Reschedule appointments
- ✅ Handle invalid booking requests

### Root Endpoint Tests (1 test)
- ✅ Root endpoint returns correct message

## Test Fixtures

The `conftest.py` file provides several useful fixtures:

- `client` - FastAPI TestClient instance
- `auth_token` - Valid JWT access token
- `auth_headers` - Authorization headers with Bearer token
- `refresh_token` - Valid JWT refresh token
- `mock_appointments_file` - Temporary appointments database file
- `mock_schedule_file` - Temporary doctor schedule file

## Notes

- Tests use temporary files for database operations to avoid affecting real data
- All tests are isolated and can run in any order
- The test suite uses pytest fixtures for setup and teardown

