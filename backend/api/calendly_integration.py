from fastapi import APIRouter, HTTPException

from backend.db.database import APPOINTMENT_TYPES
from backend.models.schemas import (
    AvailabilityResponse,
    TimeSlot,
    BookingRequest,
    BookingResponse,
)
from backend.tools.availability_tool import generate_daily_slots
from backend.tools.booking_tool import book_appointment

router = APIRouter(prefix="/api/calendly")


@router.get("/availability", response_model=AvailabilityResponse)
def get_availability(date: str, appointment_type: str):
    if appointment_type not in APPOINTMENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid appointment type")

    slots = generate_daily_slots(date, appointment_type)

    return AvailabilityResponse(
        date=date,
        available_slots=[TimeSlot(**slot) for slot in slots],
    )


@router.post("/book", response_model=BookingResponse)
def book(data: BookingRequest):
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

