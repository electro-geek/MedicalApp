#!/usr/bin/env python3
"""
Run script for the Medical Appointment Scheduling Agent.
"""
import uvicorn
from backend.config import get_config


def main():
    """Run the FastAPI application."""
    config = get_config()
    port = config.get_int("BACKEND_PORT", 8000)
    
    print("=" * 60)
    print("Medical Appointment Scheduling Agent")
    print("=" * 60)
    print(f"Starting server on http://localhost:{port}")
    print(f"API Documentation: http://localhost:{port}/docs")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )


if __name__ == "__main__":
    main()
