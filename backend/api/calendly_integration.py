from fastapi import APIRouter, HTTPException, Depends

from backend.db.database import APPOINTMENT_TYPES
from backend.models.schemas import (
    AvailabilityResponse,
    TimeSlot,
    BookingRequest,
    BookingResponse,
    RescheduleRequest,
    RescheduleResponse,
    DeleteResponse,
)
from backend.tools.availability_tool import generate_daily_slots
from backend.tools.booking_tool import (
    book_appointment,
    delete_appointment,
    reschedule_appointment,
)
from backend.utils.jwt_handler import verify_token

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


@router.delete("/appointments/{appointment_id}", response_model=DeleteResponse)
def delete(appointment_id: str, user=Depends(verify_token)):
    try:
        delete_appointment(appointment_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return DeleteResponse(
        booking_id=appointment_id,
        status="deleted",
        message="Appointment deleted successfully",
    )


@router.put(
    "/appointments/{appointment_id}/reschedule",
    response_model=RescheduleResponse,
)
def reschedule(
    appointment_id: str,
    data: RescheduleRequest,
    user=Depends(verify_token),
):
    # Ensure the path parameter matches the payload to avoid accidental updates
    if data.appointment_id != appointment_id:
        raise HTTPException(
            status_code=400,
            detail="appointment_id in path and body must match",
        )

    try:
        result = reschedule_appointment(data)
    except ValueError as exc:
        status = 400 if "available" in str(exc).lower() else 404
        raise HTTPException(status_code=status, detail=str(exc)) from exc

    return RescheduleResponse(
        booking_id=result["id"],
        status="rescheduled",
        confirmation_code=result["confirmation_code"],
        details=result,
    )
