"""
Tool to check appointment availability.
"""
import requests
from typing import List, Dict, Any
from backend.config import get_config


def check_availability(date: str, appointment_type: str) -> Dict[str, Any]:
    """
    Check available appointment slots for a given date and appointment type.
    
    Args:
        date: Date in YYYY-MM-DD format
        appointment_type: Type of appointment (consultation, followup, physical, special)
        
    Returns:
        Dictionary with date and available slots
    """
    config = get_config()
    backend_port = config.get_int("BACKEND_PORT", 8000)
    
    try:
        # Call the mock Calendly API
        response = requests.get(
            f"http://localhost:{backend_port}/api/calendly/availability",
            params={
                "date": date,
                "appointment_type": appointment_type
            },
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "date": date,
                "available_slots": [],
                "error": f"API returned status code {response.status_code}"
            }
    except Exception as e:
        return {
            "date": date,
            "available_slots": [],
            "error": f"Failed to check availability: {str(e)}"
        }


def get_available_slots(date: str, appointment_type: str) -> List[Dict[str, Any]]:
    """
    Get list of available slots for a given date and appointment type.
    
    Args:
        date: Date in YYYY-MM-DD format
        appointment_type: Type of appointment
        
    Returns:
        List of available time slots
    """
    result = check_availability(date, appointment_type)
    slots = result.get("available_slots", [])
    return [slot for slot in slots if slot.get("available", False)]
