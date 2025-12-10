from fastapi import APIRouter, HTTPException, Depends

from backend.db.database import APPOINTMENT_TYPES
from backend.models.schemas import (
    AvailabilityResponse,
    TimeSlot,
    BookingRequest,
    BookingResponse,
)
from backend.tools.availability_tool import generate_daily_slots
from backend.tools.booking_tool import book_appointment
from backend.utils.jwt_handler import verify_token   # ← Add this

router = APIRouter(prefix="/api/calendly")


@router.get("/availability", response_model=AvailabilityResponse)
def get_availability(
    date: str,
    appointment_type: str,
    user=Depends(verify_token),                # ← Protect this route
):
    if appointment_type not in APPOINTMENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid appointment type")

    slots = generate_daily_slots(date, appointment_type)

    return AvailabilityResponse(
        date=date,
        available_slots=[TimeSlot(**slot) for slot in slots],
    )


@router.post("/book", response_model=BookingResponse)
def book(
    data: BookingRequest,
    user=Depends(verify_token),                # ← Protect this route
):
    try:
        result = book_appointment(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return BookingResponse(
        booking_id=result["id"],
        status="confirmed",
        confirmation_code=result["confirmation_code"],
        details=result,
    )
