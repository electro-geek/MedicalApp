# 🚀 How to Run the Medical Appointment Scheduling Project

This guide will help you run both the backend and frontend of the Medical Appointment Scheduling Agent.

---

## 📋 Prerequisites

### Backend Requirements
- **Python 3.10 or higher**
- **pip** (Python package manager)
- **Gemini API Key** (Get one from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Frontend Requirements
- **Node.js 16+** and **npm** (or **yarn**)

---

## 🔧 Backend Setup & Running

### Step 1: Install Python Dependencies

```bash
# Navigate to project root
cd /home/mritunjay/Desktop/MedicalApp

# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure API Key

Edit `config.properties` and set your Gemini API key:

```properties
GEMINI_API_KEY=your_actual_gemini_api_key_here
LLM_MODEL=gemini-2.5-flash
```

**Note:** The `config.properties` file already exists with example values. Replace `your_gemini_api_key_here` with your actual API key.

### Step 3: Run the Backend

```bash
# From project root
python run.py
```

The backend will start on **http://localhost:8000**

**Verify it's running:**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## 🎨 Frontend Setup & Running

### Step 1: Install Node Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### Step 2: Run the Frontend

**Option A: Using the start script (recommended)**
```bash
# From project root
bash START_FRONTEND.sh
```

**Option B: Manual start**
```bash
# From frontend directory
cd frontend
npm run dev
```

The frontend will start on **http://localhost:3000**

**Important:** Make sure the backend is running first! The frontend needs the backend API to function.

---

## 🎯 Quick Start (Both Backend & Frontend)

### Terminal 1: Start Backend

```bash
cd /home/mritunjay/Desktop/MedicalApp
source venv/bin/activate  # If using virtual environment
python run.py
```

### Terminal 2: Start Frontend

```bash
cd /home/mritunjay/Desktop/MedicalApp
bash START_FRONTEND.sh
# OR
cd frontend && npm run dev
```

### Access the Application

- **Frontend UI:** http://localhost:3000
- **Backend API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## 🧪 Testing the Application

### Test Backend API

```bash
# Test all endpoints
python test_api.py

# Run demo conversation
python demo.py

# Interactive mode
python demo.py interactive
```

### Test Frontend

1. Open http://localhost:3000 in your browser
2. Start a conversation with the chat interface
3. Try booking an appointment or asking FAQs

---

## ⚙️ Configuration

### Backend Configuration (`config.properties`)

Key settings:
- `GEMINI_API_KEY` - Your Gemini API key (required)
- `LLM_MODEL` - Gemini model to use (default: `gemini-2.5-flash`)
- `BACKEND_PORT` - Backend port (default: `8000`)
- `CLINIC_NAME` - Your clinic name
- `CLINIC_PHONE` - Clinic phone number

### Frontend Configuration

The frontend automatically connects to `http://localhost:8000` for the API. If your backend runs on a different port, update:
- `frontend/src/api/chatApi.js` - Change the API URL

---

## 🔍 Verification Steps

### Check Backend
```bash
# Check if backend is running
curl http://localhost:8000/health

# Should return: {"status":"healthy","service":"Medical Appointment Scheduling Agent"}
```

### Check Frontend
- Open http://localhost:3000
- You should see the chat interface
- Try sending a message like "Hello, I need to book an appointment"

### Check Setup
```bash
# Run setup check script
python check_setup.py
```

---

## 🐛 Troubleshooting

### Backend Issues

**Error: GEMINI_API_KEY not found**
- Make sure `config.properties` exists and has your API key
- Check that the key is not using placeholder value

**Error: Module not found**
- Make sure you've installed dependencies: `pip install -r requirements.txt`
- Activate your virtual environment if using one

**Port already in use**
- Change `BACKEND_PORT` in `config.properties`
- Or kill the process using port 8000: `lsof -ti:8000 | xargs kill`

### Frontend Issues

**Error: Cannot connect to backend**
- Make sure backend is running on http://localhost:8000
- Check backend logs for errors
- Verify backend health: `curl http://localhost:8000/health`

**Error: npm not found**
- Install Node.js and npm
- Verify installation: `node --version` and `npm --version`

**Port 3000 already in use**
- Change the port in `frontend/vite.config.js`
- Or kill the process: `lsof -ti:3000 | xargs kill`

---

## 📝 Development Commands

### Backend
```bash
# Run with auto-reload (default)
python run.py

# Run directly with uvicorn
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Run Python module
python -m backend.main
```

### Frontend
```bash
# Development server (auto-reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 🔄 Stopping the Servers

- **Backend:** Press `Ctrl+C` in the terminal running the backend
- **Frontend:** Press `Ctrl+C` in the terminal running the frontend

---

## 📚 Additional Resources

- **API Documentation:** http://localhost:8000/docs (when backend is running)
- **Setup Guide:** See [SETUP.md](SETUP.md) for detailed setup instructions
- **README:** See [README.md](README.md) for project overview

---

## ✅ Summary

1. **Backend:** `python run.py` (runs on http://localhost:8000)
2. **Frontend:** `bash START_FRONTEND.sh` or `cd frontend && npm run dev` (runs on http://localhost:3000)
3. **Access:** Open http://localhost:3000 in your browser

**Happy Scheduling! 🎉**

