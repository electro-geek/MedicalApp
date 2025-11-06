# Medical Appointment Scheduling Agent

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- OpenAI API key
- Calendly Client ID and Client Secret (optional - falls back to mock if not provided)

**Note:** This project uses `config.properties` file instead of `.env` for configuration.

### Setup (3 steps)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create configuration file:**
   ```bash
   cp config.properties.example config.properties
   # Edit config.properties and add:
   # - OPENAI_API_KEY (required)
   # - CALENDLY_CLIENT_ID and CALENDLY_CLIENT_SECRET (optional - for real Calendly API)
   ```

3. **Run the application:**
   ```bash
   python run.py
   ```

4. **Access the API:**
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

5. **Run the Frontend (Optional):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   - Frontend UI: http://localhost:3000

### Test the Application

```bash
# Test all endpoints
python test_api.py

# Run demo conversation
python demo.py

# Interactive mode
python demo.py interactive
```

For detailed setup instructions, see [SETUP.md](SETUP.md) or [QUICKSTART.md](QUICKSTART.md).

---

## 1. 🎯 Project Overview & Goal

Build an intelligent, conversational AI agent to help patients schedule medical appointments. The agent must integrate with a calendar system (Calendly), understand patient needs, suggest available time slots, answer frequently asked questions using a RAG (Retrieval-Augmented Generation) system, and handle the complete booking process.

## 2. 📋 Core Requirements

The system must be able to:
* Integrate with a Calendly API (or a mock version) to fetch available/booked slots.
* Engage in natural, empathetic conversation to understand patient needs.
* Intelligently suggest 3-5 available time slots based on patient preferences.
* Answer clinic-related FAQs (e.g., insurance, hours, policies) using a RAG pipeline.
* Book appointments directly via the API.
* Handle rescheduling and cancellation requests.
* Seamlessly switch context between scheduling and answering FAQs.

## 3. 🛠️ Technical Stack

* **Backend:** FastAPI (Python 3.10+)
* **LLM:** OpenAI (e.g., `gpt-4-turbo`)
* **Vector Database:** ChromaDB
* **Calendar API:** Mock Calendly API (see implementation details below)
* **Frontend (Optional):** React with a chat interface

## 4. 📁 Proposed File Structure

Create the following directory and file structure:

```
appointment-scheduling-agent/
├── README.md
├── .env.example
├── requirements.txt
├── architecture_diagram.png
├── data/
│   ├── clinic_info.json         # For RAG
│   └── doctor_schedule.json     # For Mock API logic
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── api/
│   │   ├── chat.py              # Main chat endpoint
│   │   └── calendly_integration.py # Mock Calendly API endpoints
│   ├── agent/
│   │   ├── scheduling_agent.py  # Core agent logic & state
│   │   └── prompts.py           # System prompts, user prompts
│   ├── rag/
│   │   ├── faq_rag.py           # RAG pipeline logic
│   │   ├── embeddings.py        # Embedding generation
│   │   └── vector_store.py      # Vector DB setup & query
│   ├── tools/
│   │   ├── availability_tool.py # Tool to check availability
│   │   └── booking_tool.py      # Tool to create booking
│   └── models/
│       └── schemas.py           # Pydantic models for API I/O
├── tests/
│   └── test_agent.py            # Pytest for agent logic & edge cases
└── frontend/                    # (If fullstack)
    ├── package.json
    └── src/
        ├── App.jsx
        └── components/
            ├── ChatInterface.jsx
            └── AppointmentConfirmation.jsx
```

## 5. ⚙️ Core Feature Implementation Details

### Feature 1: Calendly Integration (Mock API)

Implement a **Mock Calendly API** within `backend/api/calendly_integration.py` as specified. This mock API will be used by the agent's tools. It should read from `data/doctor_schedule.json` to determine availability.

**Appointment Types & Durations:**
* **General Consultation:** 30 minutes
* **Follow-up:** 15 minutes
* **Physical Exam:** 45 minutes
* **Specialist Consultation:** 60 minutes

**Mock Endpoints:**

1. **`GET /api/calendly/availability`**
    * **Query Params:**
        * `date: "YYYY-MM-DD"`
        * `appointment_type: "consultation" | "followup" | "physical" | "special"`
    * **Response Body:**
        ```json
        {
          "date": "2024-01-15",
          "available_slots": [
            {"start_time": "09:00", "end_time": "09:30", "available": true},
            {"start_time": "09:30", "end_time": "10:00", "available": false},
            {"start_time": "10:00", "end_time": "10:30", "available": true}
          ]
        }
        ```

2. **`POST /api/calendly/book`**
    * **Request Body:**
        ```json
        {
          "appointment_type": "consultation",
          "date": "2024-01-15",
          "start_time": "10:00",
          "patient": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1-555-0100"
          },
          "reason": "Annual checkup"
        }
        ```
    * **Response Body:**
        ```json
        {
          "booking_id": "APPT-2024-001",
          "status": "confirmed",
          "confirmation_code": "ABC123",
          "details": { ... }
        }
        ```

### Feature 2: RAG & FAQ System

* Implement a RAG system in `backend/rag/`.
* On startup, the system should load data from `data/clinic_info.json`, create embeddings, and store them in a ChromaDB vector store.
* The RAG pipeline must answer questions on these topics:
    * **Clinic Details:** Location, directions, parking, hours of operation.
    * **Insurance & Billing:** Accepted providers, payment methods, billing policies.
    * **Visit Preparation:** Required documents, first visit procedures, what to bring.
    * **Policies:** Cancellation, late arrival, COVID-19 protocols.
* **Context Switching:** The agent must handle users asking FAQs mid-booking and then return to the booking flow, or transition from an FAQ to scheduling.

### Feature 3: Intelligent Conversation Flow

The agent's logic (`scheduling_agent.py`) must follow a multi-phase flow:

* **Phase 1: Understanding Needs**
    * Greet the patient warmly.
    * Understand the reason for the visit.
    * Determine the correct appointment type (and its duration).
    * Ask about preferred dates and/or times (e.g., "morning," "ASAP").
* **Phase 2: Slot Recommendation**
    * Call the `availability_tool.py` to query the mock API.
    * Show 3-5 available slots that match the preferences.
    * Handle "none of these work" gracefully and offer alternative dates/times.
* **Phase 3: Booking Confirmation**
    * Collect necessary patient information:
        * Full name
        * Phone number
        * Email address
        * Reason for visit (if not already gathered)
    * Confirm all details with the user **before** booking.
    * Call the `booking_tool.py` to query the `POST /api/calendly/book` endpoint.
    * Provide confirmation details (ID, code) to the user.

### Feature 4: Smart Scheduling Logic

The agent and tools must account for:
* **Time Preferences:** "Morning," "Evening," "Afternoon".
* **Date Flexibility:** "ASAP" vs. a specific date.
* **Appointment Duration:** Ensure the fetched slot can fit the required duration (e.g., 45m for Physical Exam).
* **Conflict Handling:** The mock API logic must ensure no double-booking.
* **Timezone Awareness:** All times should be handled consistently (e.g., per the `.env` `TIMEZONE`).

### Feature 5: Edge Case & Error Handling

The agent must gracefully handle:
* **No Available Slots:** Clearly explain the situation, offer alternative dates, or suggest calling the office.
* **User Changes Mind:** Allow the user to restart the booking process mid-flow.
* **Ambiguous Time References:** Ask for clarification for inputs like "tomorrow morning," "next week," or "around 3".
* **Invalid Input:** Handle non-existent dates, past dates, or times outside business hours.
* **API Failures:** If the (mock) Calendly API fails, inform the user gracefully.

## 6. 💬 Agent Conversation Examples (Tone & Flow)

The agent's tone should be natural, empathetic, and not robotic.

> **Example 1: Successful Booking**
> * **User:** I need to see the doctor
> * **Agent:** I'd be happy to help you schedule an appointment! What's the main reason for your visit today?
> * **User:** I've been having headaches
> * **Agent:** I understand. For persistent headaches, I'd recommend a general consultation (30 minutes) where the doctor can assess your symptoms. Does that sound appropriate, or would you prefer a longer specialist consultation?
> * **User:** General consultation is fine
> * **Agent:** Perfect. When would you like to come in? Do you have a preference for morning or afternoon appointments?
> * **User:** Afternoon if possible, sometime this week
> * **Agent:** Let me check our afternoon availability this week. I have these options:
>     * Tomorrow (Jan 16) at 2:00 PM
>     * Wednesday (Jan 17) at 3:30 PM
>     * Thursday (Jan 18) at 1:00 PM
>     * Friday (Jan 19) at 2:30 PM
> * **User:** Wednesday at 3:30
> * **Agent:** Excellent! Wednesday, January 17th at 3:30 PM for a 30-minute consultation. Before I confirm, I'll need a few details: Your full name? Best phone number to reach you? Email address for confirmation?
> * **Agent:** [After collecting info] All set! Your appointment is confirmed for Wednesday, January 17th at 3:30 PM. You'll receive a confirmation email at john@example.com with all the details. The confirmation code is ABC123. Is there anything else you'd like to know about your visit?

> **Example 2: FAQ During Booking**
> * **User:** I want to book an appointment
> * **Agent:** I'd be happy to help! What brings you in today?
> * **User:** Actually, first what insurance do you accept?
> * **Agent:** Great question! We accept most major insurance providers including Blue Cross Blue Shield, Aetna, Cigna, UnitedHealthcare, and Medicare. We also accept self-pay patients. Do you have insurance with one of these providers?
> * **User:** Yes, I have Blue Cross. Okay, I'd like to schedule a checkup
> * **Agent:** Perfect, we accept Blue Cross Blue Shield. Now for your checkup, would this be your first visit with us, or are you an existing patient?
> * **[Continues with scheduling...]**

> **Example 3: No Available Slots**
> * **User:** Can I see the doctor today?
> * **Agent:** I understand you'd like to be seen today. Unfortunately, we don't have any available appointments for today. However, I have several options for tomorrow: 9:00 AM, 11:30 AM, 2:00 PM. Would any of these work? If you need urgent care, I can also provide information about our walk-in clinic hours.
> * **User:** Is there a waitlist for today?
> * **Agent:** We don't have a formal waitlist, but I'd recommend calling our office at (555) 123-4567 as they sometimes have last-minute cancellations. For planned appointments, would you like me to book you for tomorrow?

## 7. 🔑 Key File Contents (to be created)

### `.env.example`

```ini
# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo
OPENAI_API_KEY=your_key_here

# Calendly (if using real API)
CALENDLY_API_KEY=your_calendly_key
CALENDLY_USER_URL=https://calendly.com/your-username

# Vector Database
VECTOR_DB=chromadb
VECTOR_DB_PATH=./data/vectordb

# Clinic Configuration
CLINIC_NAME="HealthCare Plus Clinic"
CLINIC_PHONE="+1-555-123-4567"
TIMEZONE=America/New_York

# Application
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

### `requirements.txt`

```
fastapi
uvicorn
openai
chromadb-client
pydantic
python-dotenv
# Add other dependencies as needed (e.g., requests, tiktoken)
```

### `data/clinic_info.json`

```json
{
  "clinic_details": {
    "location": "123 Health St, Wellness City, NY 10001",
    "directions": "We are located on Health St between 1st and 2nd Ave. Easily accessible via the A/C/E subway lines at Wellness Station.",
    "parking": "Paid parking is available in the garage next to our building. Limited street parking is also available.",
    "hours_of_operation": "Monday-Friday: 8:00 AM - 6:00 PM. Saturday: 9:00 AM - 1:00 PM. Sunday: Closed."
  },
  "insurance_billing": {
    "accepted_providers": [
      "Blue Cross Blue Shield",
      "Aetna",
      "Cigna",
      "UnitedHealthcare",
      "Medicare"
    ],
    "payment_methods": "We accept all major credit cards, checks, and cash. Co-pays are due at the time of service.",
    "billing_policies": "For any billing questions, please contact our billing department directly at (555) 123-4568."
  },
  "visit_preparation": {
    "required_documents": "Please bring a valid photo ID and your current insurance card to every visit.",
    "first_visit_procedures": "If this is your first visit, please arrive 15 minutes early to complete new patient paperwork. You can also download the forms from our website.",
    "what_to_bring": "Bring your ID, insurance card, a list of any current medications you are taking, and any relevant medical records."
  },
  "policies": {
    "cancellation_policy": "We require at least 24 hours' notice for all cancellations. A fee may be charged for late cancellations or no-shows.",
    "late_arrival_policy": "If you arrive more than 15 minutes late for your appointment, we may need to reschedule you.",
    "covid_19_protocols": "Masks are required for all patients and staff within the clinic. If you are experiencing fever or cough, please call us before your appointment."
  }
}
```

### `data/doctor_schedule.json`

(This is a sample structure for the mock API logic. The implementation can be simpler, e.g., just assuming working hours and a list of booked times).

```json
{
  "working_hours": {
    "monday": {"start": "09:00", "end": "17:00"},
    "tuesday": {"start": "09:00", "end": "17:00"},
    "wednesday": {"start": "09:00", "end": "17:00"},
    "thursday": {"start": "09:00", "end": "17:00"},
    "friday": {"start": "09:00", "end": "17:00"},
    "saturday": {"start": "09:00", "end": "13:00"},
    "sunday": null
  },
  "booked_appointments": [
    {
      "date": "2024-01-16",
      "start_time": "14:00",
      "end_time": "14:30"
    },
    {
      "date": "2024-01-17",
      "start_time": "10:00",
      "end_time": "11:00"
    }
  ]
}
```

## 8. 📄 Documentation Requirements

### `README.md`

The generated `README.md` must include:

1. **Setup Instructions:** How to set up environment variables (`.env`) and run the application.
2. **System Design:**
      * Agent conversation flow.
      * RAG pipeline for FAQs.
      * Tool calling strategy.
3. **Scheduling Logic:**
      * How available slots are determined.
      * How appointment types (durations) are handled.
      * Conflict prevention.
4. **Testing:**
      * Example conversations.
      * Edge cases covered.

### `architecture_diagram.png`

The architecture diagram must visualize:

  * Conversation agent flow
  * Mock Calendly API integration
  * RAG pipeline for FAQs
  * Tool calling (availability check, booking)
  * The context switching mechanism (Scheduling <-> FAQ)
  * Error handling paths
