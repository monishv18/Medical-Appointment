from datetime import datetime, timedelta

from backend.db.database import (
    load_appointments,
    load_doctor_schedule,
    APPOINTMENT_TYPES,
)


def generate_daily_slots(date: str, appointment_type: str):
    schedule = load_doctor_schedule()["working_hours"]
    start_time = schedule["start"]
    end_time = schedule["end"]

    duration = APPOINTMENT_TYPES[appointment_type]

    start_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")

    appointments = load_appointments()

    slots = []

    current = start_dt
    while current + timedelta(minutes=duration) <= end_dt:
        s = current.strftime("%H:%M")
        e = (current + timedelta(minutes=duration)).strftime("%H:%M")

        available = True
        for appt in appointments:
            if appt["date"] != date:
                continue
            if not (appt["end_time"] <= s or appt["start_time"] >= e):
                available = False

        slots.append(
            {
                "start_time": s,
                "end_time": e,
                "available": available,
            }
        )

        current += timedelta(minutes=duration)

    return slots

