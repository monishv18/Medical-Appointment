import random
import string
import uuid

from backend.db.database import (
    load_appointments,
    save_appointments,
    APPOINTMENT_TYPES,
)


def generate_confirmation_code() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def book_appointment(data):
    appointments = load_appointments()

    duration = APPOINTMENT_TYPES[data.appointment_type]
    start = data.start_time
    end_dt = int(start.split(":")[0]) * 60 + int(start.split(":")[1]) + duration
    end = f"{end_dt // 60:02}:{end_dt % 60:02}"

    for appt in appointments:
        if appt["date"] == data.date and not (
            appt["end_time"] <= start or appt["start_time"] >= end
        ):
            raise ValueError("Time slot not available")

    booking_id = f"APPT-{uuid.uuid4().hex[:6].upper()}"
    confirmation = generate_confirmation_code()

    new_appointment = {
        "id": booking_id,
        "appointment_type": data.appointment_type,
        "date": data.date,
        "start_time": start,
        "end_time": end,
        "patient": data.patient.dict(),
        "reason": data.reason,
        "confirmation_code": confirmation,
    }

    appointments.append(new_appointment)
    save_appointments(appointments)

    return new_appointment


def delete_appointment(appointment_id: str):
    appointments = load_appointments()
    for idx, appt in enumerate(appointments):
        if appt["id"] == appointment_id:
            removed = appointments.pop(idx)
            save_appointments(appointments)
            return removed
    raise ValueError("Appointment not found")


def reschedule_appointment(data):
    appointments = load_appointments()
    target = None
    for appt in appointments:
        if appt["id"] == data.appointment_id:
            target = appt
            break

    if target is None:
        raise ValueError("Appointment not found")

    duration = APPOINTMENT_TYPES[data.appointment_type]
    start = data.start_time
    end_dt = int(start.split(":")[0]) * 60 + int(start.split(":")[1]) + duration
    end = f"{end_dt // 60:02}:{end_dt % 60:02}"

    for appt in appointments:
        if appt["id"] == data.appointment_id:
            continue
        if appt["date"] == data.date and not (
            appt["end_time"] <= start or appt["start_time"] >= end
        ):
            raise ValueError("Time slot not available")

    target.update(
        {
            "appointment_type": data.appointment_type,
            "date": data.date,
            "start_time": start,
            "end_time": end,
            "reason": data.reason or target.get("reason", ""),
            "confirmation_code": generate_confirmation_code(),
        }
    )

    save_appointments(appointments)
    return target

