"""
Tool to book appointments.
"""
import requests
from typing import Dict, Any
from backend.config import get_config
from backend.models.schemas import BookingRequest


def book_appointment(
    appointment_type: str,
    date: str,
    start_time: str,
    patient_name: str,
    patient_email: str,
    patient_phone: str,
    reason: str = None
) -> Dict[str, Any]:
    """
    Book an appointment.
    
    Args:
        appointment_type: Type of appointment (consultation, followup, physical, special)
        date: Date in YYYY-MM-DD format
        start_time: Start time in HH:MM format
        patient_name: Patient's full name
        patient_email: Patient's email address
        patient_phone: Patient's phone number
        reason: Reason for visit (optional)
        
    Returns:
        Dictionary with booking confirmation details
    """
    config = get_config()
    backend_port = config.get_int("BACKEND_PORT", 8000)
    
    # Prepare booking request
    booking_request = {
        "appointment_type": appointment_type,
        "date": date,
        "start_time": start_time,
        "patient": {
            "name": patient_name,
            "email": patient_email,
            "phone": patient_phone
        },
        "reason": reason
    }
    
    try:
        # Call the mock Calendly API
        response = requests.post(
            f"http://localhost:{backend_port}/api/calendly/book",
            json=booking_request,
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status": "error",
                "error": f"Booking failed with status code {response.status_code}",
                "message": response.text
            }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to book appointment: {str(e)}"
        }
