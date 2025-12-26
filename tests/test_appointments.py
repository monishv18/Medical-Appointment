"""
Tests for appointment booking endpoints.
"""
import pytest
from fastapi import status


class TestAvailability:
    """Test cases for the availability endpoint."""
    
    def test_get_availability_success(self, client, auth_headers):
        """Test successfully getting availability for a date."""
        response = client.get(
            "/api/calendly/availability",
            params={"date": "2024-01-15", "appointment_type": "consultation"},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "date" in data
        assert "available_slots" in data
        assert data["date"] == "2024-01-15"
        assert isinstance(data["available_slots"], list)
        
        # Check slot structure
        if len(data["available_slots"]) > 0:
            slot = data["available_slots"][0]
            assert "start_time" in slot
            assert "end_time" in slot
            assert "available" in slot
            assert isinstance(slot["available"], bool)
    
    def test_get_availability_invalid_appointment_type(self, client, auth_headers):
        """Test getting availability with invalid appointment type."""
        response = client.get(
            "/api/calendly/availability",
            params={"date": "2024-01-15", "appointment_type": "invalid_type"},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid appointment type" in response.json()["detail"]
    
    def test_get_availability_missing_date(self, client, auth_headers):
        """Test getting availability without date parameter."""
        response = client.get(
            "/api/calendly/availability",
            params={"appointment_type": "consultation"},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_availability_missing_appointment_type(self, client, auth_headers):
        """Test getting availability without appointment_type parameter."""
        response = client.get(
            "/api/calendly/availability",
            params={"date": "2024-01-15"},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_availability_all_appointment_types(self, client, auth_headers):
        """Test availability for all supported appointment types."""
        appointment_types = ["consultation", "followup", "physical", "specialist", "general"]
        
        for apt_type in appointment_types:
            response = client.get(
                "/api/calendly/availability",
                params={"date": "2024-01-15", "appointment_type": apt_type},
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK


class TestBooking:
    """Test cases for the booking endpoint."""
    
    @pytest.fixture
    def booking_request(self):
        """Sample booking request data."""
        return {
            "appointment_type": "consultation",
            "date": "2024-01-15",
            "start_time": "10:00",
            "patient": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "123-456-7890"
            },
            "reason": "Regular checkup"
        }
    
    def test_book_appointment_success(self, client, auth_headers, booking_request):
        """Test successfully booking an appointment."""
        response = client.post(
            "/api/calendly/book",
            json=booking_request,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "booking_id" in data
        assert "status" in data
        assert "confirmation_code" in data
        assert "details" in data
        assert data["status"] == "confirmed"
        assert isinstance(data["booking_id"], str)
        assert isinstance(data["confirmation_code"], str)
        assert len(data["confirmation_code"]) > 0
    
    def test_book_appointment_conflicting_time(self, client, auth_headers, booking_request):
        """Test booking an appointment when the time slot is already taken."""
        # Book first appointment
        response1 = client.post(
            "/api/calendly/book",
            json=booking_request,
            headers=auth_headers
        )
        assert response1.status_code == status.HTTP_200_OK
        
        # Try to book conflicting appointment
        response2 = client.post(
            "/api/calendly/book",
            json=booking_request,  # Same time slot
            headers=auth_headers
        )
        
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "not available" in response2.json()["detail"].lower()
    
    def test_book_appointment_invalid_type(self, client, auth_headers, booking_request):
        """Test booking with invalid appointment type."""
        booking_request["appointment_type"] = "invalid_type"
        
        response = client.post(
            "/api/calendly/book",
            json=booking_request,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_book_appointment_missing_fields(self, client, auth_headers):
        """Test booking with missing required fields."""
        incomplete_request = {
            "appointment_type": "consultation",
            "date": "2024-01-15"
            # Missing start_time, patient, reason
        }
        
        response = client.post(
            "/api/calendly/book",
            json=incomplete_request,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_book_appointment_invalid_email(self, client, auth_headers, booking_request):
        """Test booking with invalid email format."""
        booking_request["patient"]["email"] = "invalid-email"
        
        response = client.post(
            "/api/calendly/book",
            json=booking_request,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDeleteAppointment:
    """Test cases for the delete appointment endpoint."""
    
    @pytest.fixture
    def created_appointment(self, client, auth_headers):
        """Create an appointment for testing deletion."""
        booking_request = {
            "appointment_type": "consultation",
            "date": "2024-01-16",
            "start_time": "11:00",
            "patient": {
                "name": "Jane Doe",
                "email": "jane.doe@example.com",
                "phone": "987-654-3210"
            },
            "reason": "Test appointment"
        }
        
        response = client.post(
            "/api/calendly/book",
            json=booking_request,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        return response.json()["booking_id"]
    
    def test_delete_appointment_success(self, client, auth_headers, created_appointment):
        """Test successfully deleting an appointment."""
        response = client.delete(
            f"/api/calendly/appointments/{created_appointment}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["booking_id"] == created_appointment
        assert data["status"] == "deleted"
        assert "deleted successfully" in data["message"].lower()
    
    def test_delete_nonexistent_appointment(self, client, auth_headers):
        """Test deleting an appointment that doesn't exist."""
        response = client.delete(
            "/api/calendly/appointments/APPT-NONEXISTENT",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()


class TestRescheduleAppointment:
    """Test cases for the reschedule appointment endpoint."""
    
    @pytest.fixture
    def created_appointment(self, client, auth_headers):
        """Create an appointment for testing rescheduling."""
        booking_request = {
            "appointment_type": "consultation",
            "date": "2024-01-17",
            "start_time": "14:00",
            "patient": {
                "name": "Bob Smith",
                "email": "bob.smith@example.com",
                "phone": "555-123-4567"
            },
            "reason": "Initial appointment"
        }
        
        response = client.post(
            "/api/calendly/book",
            json=booking_request,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        return response.json()["booking_id"]
    
    def test_reschedule_appointment_success(self, client, auth_headers, created_appointment):
        """Test successfully rescheduling an appointment."""
        reschedule_request = {
            "appointment_id": created_appointment,
            "appointment_type": "consultation",
            "date": "2024-01-17",
            "start_time": "15:00",
            "reason": "Rescheduled appointment"
        }
        
        response = client.put(
            f"/api/calendly/appointments/{created_appointment}/reschedule",
            json=reschedule_request,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["booking_id"] == created_appointment
        assert data["status"] == "rescheduled"
        assert "confirmation_code" in data
        assert "details" in data
    
    def test_reschedule_nonexistent_appointment(self, client, auth_headers):
        """Test rescheduling an appointment that doesn't exist."""
        reschedule_request = {
            "appointment_id": "APPT-NONEXISTENT",
            "appointment_type": "consultation",
            "date": "2024-01-17",
            "start_time": "15:00"
        }
        
        response = client.put(
            "/api/calendly/appointments/APPT-NONEXISTENT/reschedule",
            json=reschedule_request,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_reschedule_conflicting_time(self, client, auth_headers, created_appointment):
        """Test rescheduling to a time slot that's already booked."""
        # Book another appointment at 13:00
        booking_request = {
            "appointment_type": "consultation",
            "date": "2024-01-17",
            "start_time": "13:00",
            "patient": {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "phone": "555-999-8888"
            },
            "reason": "Blocking slot"
        }
        client.post("/api/calendly/book", json=booking_request, headers=auth_headers)
        
        # Try to reschedule to conflicting time
        reschedule_request = {
            "appointment_id": created_appointment,
            "appointment_type": "consultation",
            "date": "2024-01-17",
            "start_time": "13:00",  # Conflicting time
        }
        
        response = client.put(
            f"/api/calendly/appointments/{created_appointment}/reschedule",
            json=reschedule_request,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not available" in response.json()["detail"].lower()
    
    def test_reschedule_id_mismatch(self, client, auth_headers, created_appointment):
        """Test rescheduling with mismatched appointment_id in path and body."""
        reschedule_request = {
            "appointment_id": "APPT-DIFFERENT",
            "appointment_type": "consultation",
            "date": "2024-01-17",
            "start_time": "15:00"
        }
        
        response = client.put(
            f"/api/calendly/appointments/{created_appointment}/reschedule",
            json=reschedule_request,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "must match" in response.json()["detail"].lower()
    
    def test_reschedule_different_appointment_type(self, client, auth_headers, created_appointment):
        """Test rescheduling to a different appointment type."""
        reschedule_request = {
            "appointment_id": created_appointment,
            "appointment_type": "physical",  # Different type
            "date": "2024-01-17",
            "start_time": "16:00"
        }
        
        response = client.put(
            f"/api/calendly/appointments/{created_appointment}/reschedule",
            json=reschedule_request,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["details"]["appointment_type"] == "physical"

