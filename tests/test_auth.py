"""
Tests for authentication endpoints.
"""
import pytest
from fastapi import status


class TestLogin:
    """Test cases for the login endpoint."""
    
    def test_login_success(self, client):
        """Test successful login with correct credentials."""
        response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert isinstance(data["refresh_token"], str)
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0
    
    def test_login_success_monish(self, client):
        """Test successful login with Monish credentials."""
        response = client.post(
            "/api/auth/login",
            json={"username": "Monish", "password": "MV@2003"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert isinstance(data["refresh_token"], str)
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0
    
    def test_login_invalid_username(self, client):
        """Test login with incorrect username."""
        response = client.post(
            "/api/auth/login",
            json={"username": "wrong_user", "password": "admin123"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid username or password" in response.json()["detail"]
    
    def test_login_invalid_password(self, client):
        """Test login with incorrect password."""
        response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "wrong_password"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid username or password" in response.json()["detail"]
    
    def test_login_missing_username(self, client):
        """Test login without username."""
        response = client.post(
            "/api/auth/login",
            json={"password": "admin123"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_missing_password(self, client):
        """Test login without password."""
        response = client.post(
            "/api/auth/login",
            json={"username": "admin"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_empty_body(self, client):
        """Test login with empty request body."""
        response = client.post(
            "/api/auth/login",
            json={}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestRefreshToken:
    """Test cases for the refresh token endpoint."""
    
    def test_refresh_token_success(self, client, refresh_token):
        """Test successful token refresh."""
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert isinstance(data["refresh_token"], str)
    
    def test_refresh_token_invalid(self, client):
        """Test refresh with invalid token."""
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Token expired or invalid" in response.json()["detail"]
    
    def test_refresh_token_with_access_token(self, client, auth_token):
        """Test refresh endpoint with access token instead of refresh token."""
        # This should fail because access tokens have type="access"
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": auth_token}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_token_missing(self, client):
        """Test refresh without token."""
        response = client.post(
            "/api/auth/refresh",
            json={}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_refresh_token_empty_string(self, client):
        """Test refresh with empty token string."""
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": ""}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestProtectedEndpoints:
    """Test that protected endpoints require authentication."""
    
    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token."""
        response = client.get(
            "/api/calendly/availability?date=2024-01-15&appointment_type=consultation"
        )
        
        # HTTPBearer returns 403 Forbidden when no credentials are provided
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
    
    def test_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token."""
        response = client.get(
            "/api/calendly/availability?date=2024-01-15&appointment_type=consultation",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_protected_endpoint_with_valid_token(self, client, auth_headers):
        """Test accessing protected endpoint with valid token."""
        response = client.get(
            "/api/calendly/availability?date=2024-01-15&appointment_type=consultation",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK

