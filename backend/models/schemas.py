from typing import List
from pydantic import BaseModel, EmailStr


class TimeSlot(BaseModel):
    start_time: str
    end_time: str
    available: bool


class AvailabilityResponse(BaseModel):
    date: str
    available_slots: List[TimeSlot]


class PatientInfo(BaseModel):
    name: str
    email: EmailStr
    phone: str


class BookingRequest(BaseModel):
    appointment_type: str
    date: str
    start_time: str
    patient: PatientInfo
    reason: str


class BookingResponse(BaseModel):
    booking_id: str
    status: str
    confirmation_code: str
    details: dict

