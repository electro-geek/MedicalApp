"""
Pydantic models for API request/response schemas.
"""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class PatientInfo(BaseModel):
    """Patient information model."""
    name: str = Field(..., description="Patient's full name")
    email: EmailStr = Field(..., description="Patient's email address")
    phone: str = Field(..., description="Patient's phone number")


class BookingRequest(BaseModel):
    """Request model for booking an appointment."""
    appointment_type: str = Field(..., description="Type of appointment: consultation, followup, physical, special")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    start_time: str = Field(..., description="Start time in HH:MM format")
    patient: PatientInfo = Field(..., description="Patient information")
    reason: Optional[str] = Field(None, description="Reason for visit")


class TimeSlot(BaseModel):
    """Time slot model."""
    start_time: str = Field(..., description="Start time in HH:MM format")
    end_time: str = Field(..., description="End time in HH:MM format")
    available: bool = Field(..., description="Whether the slot is available")


class AvailabilityResponse(BaseModel):
    """Response model for availability check."""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    available_slots: List[TimeSlot] = Field(..., description="List of available time slots")


class BookingResponse(BaseModel):
    """Response model for booking confirmation."""
    booking_id: str = Field(..., description="Unique booking identifier")
    status: str = Field(..., description="Booking status (e.g., 'confirmed')")
    confirmation_code: str = Field(..., description="Confirmation code for the booking")
    details: dict = Field(..., description="Additional booking details")


class ChatMessage(BaseModel):
    """Chat message request model."""
    message: str = Field(..., description="User's message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")


class ChatResponse(BaseModel):
    """Chat message response model."""
    response: str = Field(..., description="Agent's response")
    conversation_id: str = Field(..., description="Conversation ID")
    status: str = Field(default="success", description="Response status")

