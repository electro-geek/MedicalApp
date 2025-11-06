"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import get_config
from backend.api import chat, calendly_integration
from backend.rag.vector_store import get_vector_store


# Initialize FastAPI app
app = FastAPI(
    title="Medical Appointment Scheduling Agent",
    description="AI-powered appointment scheduling system with Calendly integration and FAQ handling",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(calendly_integration.router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("Starting Medical Appointment Scheduling Agent...")
    
    # Initialize vector store
    try:
        print("Initializing vector store...")
        vector_store = get_vector_store()
        vector_store.load_clinic_data()
        print("✓ Vector store initialized")
    except Exception as e:
        print(f"⚠ Warning: Failed to initialize vector store: {e}")
    
    config = get_config()
    clinic_name = config.get("CLINIC_NAME", "HealthCare Plus Clinic")
    print(f"✓ {clinic_name} scheduling agent is ready!")
    print(f"✓ API available at http://localhost:{config.get_int('BACKEND_PORT', 8000)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Medical Appointment Scheduling Agent"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Medical Appointment Scheduling Agent API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    config = get_config()
    port = config.get_int("BACKEND_PORT", 8000)
    uvicorn.run(app, host="0.0.0.0", port=port)
