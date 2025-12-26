# backend/api/auth.py

from fastapi import APIRouter, HTTPException
from backend.models.auth_schemas import LoginRequest, TokenResponse, RefreshRequest
from backend.utils.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token
)

router = APIRouter(prefix="/api/auth")


# ----- 1. Login Endpoint -----
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):

    # Dummy validation (replace with DB check)
    valid_credentials = {
        "admin": "admin123",
        "Monish": "MV@2003"
    }
    
    if data.username not in valid_credentials or valid_credentials[data.username] != data.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user_data = {"sub": data.username}

    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


# ----- 2. Refresh Token Endpoint -----
@router.post("/refresh", response_model=TokenResponse)
def refresh_token(data: RefreshRequest):
    try:
        payload = decode_token(data.refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        new_access = create_access_token({"sub": payload["sub"]})
        new_refresh = create_refresh_token({"sub": payload["sub"]})

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh
        )

    except Exception:
        raise HTTPException(status_code=401, detail="Token expired or invalid")
