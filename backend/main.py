from fastapi import FastAPI

from backend.api.calendly_integration import router as calendly_router
from backend.api.auth import router as auth_router

app = FastAPI(
    title="Medical Appointment Scheduling Agent",
    version="1.0.0",
)

app.include_router(auth_router)

app.include_router(calendly_router)


@app.get("/")
def root():
    return {"message": "Appointment Scheduling Agent Backend Running"}
