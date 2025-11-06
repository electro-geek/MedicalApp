"""
Mock Calendly API integration.
Handles availability checking and booking.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query, HTTPException
from backend.models.schemas import (
    AvailabilityResponse,
    TimeSlot,
    BookingRequest,
    BookingResponse
)
from backend.config import get_config


router = APIRouter(prefix="/api/calendly", tags=["calendly"])

# Appointment type durations (in minutes)
APPOINTMENT_DURATIONS = {
    "consultation": 30,
    "followup": 15,
    "physical": 45,
    "special": 60
}

# Load schedule data
_schedule_data: Optional[Dict[str, Any]] = None


def load_schedule_data() -> Dict[str, Any]:
    """Load doctor schedule data from JSON file."""
    global _schedule_data
    if _schedule_data is None:
        project_root = Path(__file__).parent.parent.parent
        schedule_path = project_root / "data" / "doctor_schedule.json"
        
        if not schedule_path.exists():
            # Return default schedule if file doesn't exist
            _schedule_data = {
                "working_hours": {
                    "monday": {"start": "09:00", "end": "17:00"},
                    "tuesday": {"start": "09:00", "end": "17:00"},
                    "wednesday": {"start": "09:00", "end": "17:00"},
                    "thursday": {"start": "09:00", "end": "17:00"},
                    "friday": {"start": "09:00", "end": "17:00"},
                    "saturday": {"start": "09:00", "end": "13:00"},
                    "sunday": None
                },
                "booked_appointments": []
            }
        else:
            with open(schedule_path, 'r') as f:
                _schedule_data = json.load(f)
    
    return _schedule_data


def save_schedule_data(data: Dict[str, Any]):
    """Save schedule data to JSON file."""
    project_root = Path(__file__).parent.parent.parent
    schedule_path = project_root / "data" / "doctor_schedule.json"
    schedule_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(schedule_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    global _schedule_data
    _schedule_data = data


def get_working_hours(date_str: str) -> Optional[Dict[str, str]]:
    """Get working hours for a given date."""
    schedule_data = load_schedule_data()
    working_hours = schedule_data.get("working_hours", {})
    
    # Parse date to get day of week
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = date_obj.strftime("%A").lower()
    except ValueError:
        return None
    
    return working_hours.get(day_name)


def time_to_minutes(time_str: str) -> int:
    """Convert time string (HH:MM) to minutes since midnight."""
    try:
        hours, minutes = map(int, time_str.split(":"))
        return hours * 60 + minutes
    except ValueError:
        return 0


def minutes_to_time(minutes: int) -> str:
    """Convert minutes since midnight to time string (HH:MM)."""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def is_time_slot_available(
    date_str: str,
    start_time: str,
    duration_minutes: int,
    booked_appointments: List[Dict[str, str]]
) -> bool:
    """Check if a time slot is available."""
    slot_start = time_to_minutes(start_time)
    slot_end = slot_start + duration_minutes
    
    # Check against booked appointments
    for booking in booked_appointments:
        if booking["date"] == date_str:
            booked_start = time_to_minutes(booking["start_time"])
            booked_end = time_to_minutes(booking["end_time"])
            
            # Check for overlap
            if not (slot_end <= booked_start or slot_start >= booked_end):
                return False
    
    return True


def generate_time_slots(
    date_str: str,
    appointment_type: str,
    slot_interval: int = 30
) -> List[TimeSlot]:
    """Generate time slots for a given date and appointment type."""
    schedule_data = load_schedule_data()
    booked_appointments = schedule_data.get("booked_appointments", [])
    
    duration_minutes = APPOINTMENT_DURATIONS.get(appointment_type, 30)
    working_hours = get_working_hours(date_str)
    
    if not working_hours:
        return []  # Clinic closed on this day
    
    start_time = working_hours["start"]
    end_time = working_hours["end"]
    
    start_minutes = time_to_minutes(start_time)
    end_minutes = time_to_minutes(end_time)
    
    slots = []
    current_minutes = start_minutes
    
    while current_minutes + duration_minutes <= end_minutes:
        slot_start = minutes_to_time(current_minutes)
        slot_end = minutes_to_time(current_minutes + duration_minutes)
        
        available = is_time_slot_available(
            date_str,
            slot_start,
            duration_minutes,
            booked_appointments
        )
        
        slots.append(TimeSlot(
            start_time=slot_start,
            end_time=slot_end,
            available=available
        ))
        
        current_minutes += slot_interval
    
    return slots


@router.get("/availability", response_model=AvailabilityResponse)
async def get_availability(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    appointment_type: str = Query(..., description="Appointment type: consultation, followup, physical, special")
):
    """Get available appointment slots for a given date and appointment type."""
    # Validate appointment type
    if appointment_type not in APPOINTMENT_DURATIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid appointment type. Must be one of: {', '.join(APPOINTMENT_DURATIONS.keys())}"
        )
    
    # Validate date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Must be YYYY-MM-DD"
        )
    
    # Check if date is in the past
    today = datetime.now().date()
    requested_date = datetime.strptime(date, "%Y-%m-%d").date()
    if requested_date < today:
        raise HTTPException(
            status_code=400,
            detail="Cannot check availability for past dates"
        )
    
    # Generate slots
    slots = generate_time_slots(date, appointment_type)
    
    return AvailabilityResponse(
        date=date,
        available_slots=slots
    )


@router.post("/book", response_model=BookingResponse)
async def book_appointment(booking_request: BookingRequest):
    """Book an appointment."""
    # Validate appointment type
    if booking_request.appointment_type not in APPOINTMENT_DURATIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid appointment type. Must be one of: {', '.join(APPOINTMENT_DURATIONS.keys())}"
        )
    
    # Validate date format
    try:
        requested_date = datetime.strptime(booking_request.date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Must be YYYY-MM-DD"
        )
    
    # Check if date is in the past
    today = datetime.now().date()
    if requested_date < today:
        raise HTTPException(
            status_code=400,
            detail="Cannot book appointments for past dates"
        )
    
    # Check if slot is available
    duration_minutes = APPOINTMENT_DURATIONS[booking_request.appointment_type]
    schedule_data = load_schedule_data()
    booked_appointments = schedule_data.get("booked_appointments", [])
    
    if not is_time_slot_available(
        booking_request.date,
        booking_request.start_time,
        duration_minutes,
        booked_appointments
    ):
        raise HTTPException(
            status_code=409,
            detail="The requested time slot is no longer available"
        )
    
    # Calculate end time
    start_minutes = time_to_minutes(booking_request.start_time)
    end_minutes = start_minutes + duration_minutes
    end_time = minutes_to_time(end_minutes)
    
    # Generate booking ID and confirmation code
    booking_id = f"APPT-{datetime.now().strftime('%Y%m%d')}-{len(booked_appointments) + 1:03d}"
    confirmation_code = f"{datetime.now().strftime('%Y%m%d')}{booking_request.start_time.replace(':', '')}"
    
    # Add to booked appointments
    new_booking = {
        "date": booking_request.date,
        "start_time": booking_request.start_time,
        "end_time": end_time,
        "appointment_type": booking_request.appointment_type,
        "patient": {
            "name": booking_request.patient.name,
            "email": booking_request.patient.email,
            "phone": booking_request.patient.phone
        },
        "reason": booking_request.reason,
        "booking_id": booking_id
    }
    
    booked_appointments.append(new_booking)
    schedule_data["booked_appointments"] = booked_appointments
    save_schedule_data(schedule_data)
    
    return BookingResponse(
        booking_id=booking_id,
        status="confirmed",
        confirmation_code=confirmation_code,
        details={
            "appointment_type": booking_request.appointment_type,
            "date": booking_request.date,
            "start_time": booking_request.start_time,
            "end_time": end_time,
            "patient": {
                "name": booking_request.patient.name,
                "email": booking_request.patient.email,
                "phone": booking_request.patient.phone
            },
            "reason": booking_request.reason
        }
    )
