"""
Tests for root endpoint.
"""
import pytest
from fastapi import status


def test_root_endpoint(client):
    """Test the root endpoint returns correct message."""
    response = client.get("/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "Appointment Scheduling Agent Backend Running" in data["message"]

