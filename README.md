# Medical Appointment Scheduling Agent

A FastAPI-based backend service for managing medical appointment scheduling with Calendly-like functionality. This application provides authentication, availability checking, and appointment booking capabilities.

## Features

- 🔐 **JWT Authentication**: Secure user authentication with access and refresh tokens
- 📅 **Appointment Availability**: Check available time slots for different appointment types
- 📝 **Appointment Booking**: Book and manage medical appointments
- 🏥 **Multiple Appointment Types**: Support for consultation, follow-up, physical, specialist, and general appointments
- 🐳 **Docker Support**: Easy deployment with Docker and Docker Compose
- 📦 **Poetry**: Modern Python dependency management

## Tech Stack

- **Python 3.11+**
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **JWT**: Secure token-based authentication
- **Uvicorn**: ASGI server for running FastAPI
- **Docker**: Containerization support

## Project Structure

```
medical_appointment/
├── backend/
│   ├── api/
│   │   ├── auth.py              # Authentication endpoints
│   │   └── calendly_integration.py  # Appointment booking endpoints
│   ├── db/
│   │   ├── database.py          # Database operations
│   │   ├── appointments.json    # Appointments storage
│   │   └── doctor_schedule.json # Doctor schedule data
│   ├── models/
│   │   ├── auth_schemas.py      # Authentication schemas
│   │   └── schemas.py           # Appointment schemas
│   ├── tools/
│   │   ├── availability_tool.py # Availability generation logic
│   │   └── booking_tool.py      # Booking logic
│   ├── utils/
│   │   └── jwt_handler.py       # JWT token utilities
│   └── main.py                  # FastAPI application entry point
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites

- Python 3.11 or higher
- Poetry (recommended) or pip
- Docker (optional, for containerized deployment)

### Using Poetry (Recommended)

1. Install Poetry if you haven't already:
   ```bash
   pip install poetry
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

4. Run the application:
   ```bash
   uvicorn backend.main:app --reload
   ```

### Using pip

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   uvicorn backend.main:app --reload
   ```

### Using Docker

1. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

   Or build and run the Docker container directly:
   ```bash
   docker build -t medical-appointment .
   docker run -p 8000:8000 medical-appointment
   ```

2. The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication

- **POST** `/api/auth/login`
  - Login endpoint to obtain access and refresh tokens
  - Request body:
    ```json
    {
      "username": "admin",
      "password": "admin123"
    }
    ```
  - Response:
    ```json
    {
      "access_token": "...",
      "refresh_token": "..."
    }
    ```

- **POST** `/api/auth/refresh`
  - Refresh access token using refresh token
  - Request body:
    ```json
    {
      "refresh_token": "..."
    }
    ```

### Appointments

- **GET** `/api/calendly/availability`
  - Get available time slots for a specific date and appointment type
  - Query parameters:
    - `date`: Date in YYYY-MM-DD format
    - `appointment_type`: One of `consultation`, `followup`, `physical`, `specialist`, `general`
  - Headers:
    - `Authorization: Bearer <access_token>`
  - Response:
    ```json
    {
      "date": "2024-01-15",
      "available_slots": [
        {
          "start_time": "09:00",
          "end_time": "09:30"
        }
      ]
    }
    ```

- **POST** `/api/calendly/book`
  - Book an appointment
  - Headers:
    - `Authorization: Bearer <access_token>`
  - Request body:
    ```json
    {
      "date": "2024-01-15",
      "time": "09:00",
      "appointment_type": "consultation",
      "patient_name": "John Doe",
      "patient_email": "john@example.com"
    }
    ```
  - Response:
    ```json
    {
      "booking_id": "123",
      "status": "confirmed",
      "confirmation_code": "ABC123",
      "details": {...}
    }
    ```

## Appointment Types

The system supports the following appointment types with their respective durations:

- **consultation**: 30 minutes
- **followup**: 15 minutes
- **physical**: 45 minutes
- **specialist**: 60 minutes
- **general**: 30 minutes

## Usage Example

1. **Login to get authentication token**:
   ```bash
   curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
   ```

2. **Check availability**:
   ```bash
   curl -X GET "http://localhost:8000/api/calendly/availability?date=2024-01-15&appointment_type=consultation" \
     -H "Authorization: Bearer <your_access_token>"
   ```

3. **Book an appointment**:
   ```bash
   curl -X POST "http://localhost:8000/api/calendly/book" \
     -H "Authorization: Bearer <your_access_token>" \
     -H "Content-Type: application/json" \
     -d '{
       "date": "2024-01-15",
       "time": "09:00",
       "appointment_type": "consultation",
       "patient_name": "John Doe",
       "patient_email": "john@example.com"
     }'
   ```

## API Documentation

Once the server is running, you can access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Development

### Code Formatting

This project uses `black`, `isort`, and `ruff` for code formatting and linting:

```bash
poetry run black .
poetry run isort .
poetry run ruff check .
```

## License

This project is part of a medical appointment scheduling system.

## Author

Monis
