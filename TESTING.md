# Testing Guide for Medical Appointment API

## Quick Start

### 1. Start the Server

**Option A: Using pip**
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

**Option B: Using Poetry**
```powershell
poetry install
poetry shell
uvicorn backend.main:app --reload
```

**Option C: Using Docker**
```powershell
docker-compose up --build
```

The server will be available at: `http://localhost:8000`

---

## Testing Methods

### Method 1: Interactive API Documentation (Easiest)

1. Open your browser and go to: **http://localhost:8000/docs**
2. This provides a Swagger UI where you can test all endpoints interactively
3. Click on each endpoint, click "Try it out", fill in the details, and click "Execute"

### Method 2: Using PowerShell (curl)

#### Test 1: Check if server is running
```powershell
curl http://localhost:8000/
```

#### Test 2: Login
```powershell
curl -X POST "http://localhost:8000/api/auth/login" `
  -H "Content-Type: application/json" `
  -d '{\"username\": \"admin\", \"password\": \"admin123\"}'
```

**Save the access_token from the response!**

#### Test 3: Check Availability (replace YOUR_TOKEN with the access token from login)
```powershell
$token = "YOUR_ACCESS_TOKEN_HERE"
curl -X GET "http://localhost:8000/api/calendly/availability?date=2024-01-15&appointment_type=consultation" `
  -H "Authorization: Bearer $token"
```

#### Test 4: Book an Appointment (replace YOUR_TOKEN with the access token)
```powershell
$token = "YOUR_ACCESS_TOKEN_HERE"
curl -X POST "http://localhost:8000/api/calendly/book" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{\"date\": \"2024-01-15\", \"time\": \"09:00\", \"appointment_type\": \"consultation\", \"patient_name\": \"John Doe\", \"patient_email\": \"john@example.com\"}'
```

#### Test 5: Refresh Token (replace YOUR_REFRESH_TOKEN)
```powershell
$refreshToken = "YOUR_REFRESH_TOKEN_HERE"
curl -X POST "http://localhost:8000/api/auth/refresh" `
  -H "Content-Type: application/json" `
  -d "{\"refresh_token\": \"$refreshToken\"}"
```

### Method 3: Using Python requests

Create a test script `test_api.py`:

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Test root endpoint
print("1. Testing root endpoint...")
response = requests.get(f"{BASE_URL}/")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# 2. Login
print("2. Testing login...")
login_data = {
    "username": "admin",
    "password": "admin123"
}
response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
print(f"Status: {response.status_code}")
login_response = response.json()
print(f"Response: {login_response}\n")

access_token = login_response.get("access_token")
refresh_token = login_response.get("refresh_token")

# 3. Check availability
print("3. Testing availability...")
headers = {"Authorization": f"Bearer {access_token}"}
params = {
    "date": "2024-01-15",
    "appointment_type": "consultation"
}
response = requests.get(f"{BASE_URL}/api/calendly/availability", headers=headers, params=params)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# 4. Book appointment
print("4. Testing booking...")
booking_data = {
    "date": "2024-01-15",
    "time": "09:00",
    "appointment_type": "consultation",
    "patient_name": "John Doe",
    "patient_email": "john@example.com"
}
response = requests.post(f"{BASE_URL}/api/calendly/book", headers=headers, json=booking_data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# 5. Refresh token
print("5. Testing token refresh...")
refresh_data = {"refresh_token": refresh_token}
response = requests.post(f"{BASE_URL}/api/auth/refresh", json=refresh_data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")
```

Run it:
```powershell
python test_api.py
```

### Method 4: Using Postman

1. Import the collection or manually create requests:
   - **POST** `http://localhost:8000/api/auth/login`
     - Body (raw JSON): `{"username": "admin", "password": "admin123"}`
   
   - **GET** `http://localhost:8000/api/calendly/availability?date=2024-01-15&appointment_type=consultation`
     - Headers: `Authorization: Bearer <access_token>`
   
   - **POST** `http://localhost:8000/api/calendly/book`
     - Headers: `Authorization: Bearer <access_token>`
     - Body (raw JSON):
       ```json
       {
         "date": "2024-01-15",
         "time": "09:00",
         "appointment_type": "consultation",
         "patient_name": "John Doe",
         "patient_email": "john@example.com"
       }
       ```

---

## Expected Responses

### Login Response
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Availability Response
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

### Booking Response
```json
{
  "booking_id": "123",
  "status": "confirmed",
  "confirmation_code": "ABC123",
  "details": {...}
}
```

---

## Troubleshooting

- **Port 8000 already in use**: Change the port with `--port 8001` or update docker-compose.yml
- **Module not found**: Make sure you're in the project root directory and dependencies are installed
- **401 Unauthorized**: Make sure you're using a valid access token in the Authorization header
- **Connection refused**: Make sure the server is running


