# Medical Appointment Scheduler - Frontend

React frontend for the Medical Appointment Scheduling Agent.

## Features

- 💬 Real-time chat interface
- 🤖 AI-powered conversation
- 📅 Appointment scheduling
- ✅ Appointment confirmation
- 📱 Responsive design
- 🎨 Modern UI/UX

## Setup

### Prerequisites

- Node.js 16+ and npm (or yarn/pnpm)

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The frontend will run on http://localhost:3000

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Configuration

The frontend is configured to connect to the backend API at `http://localhost:8000` by default.

To change the API URL, create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Usage

1. Make sure the backend server is running on port 8000
2. Start the frontend: `npm run dev`
3. Open http://localhost:3000 in your browser
4. Start chatting with the AI assistant!

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.jsx      # Main chat component
│   │   ├── MessageBubble.jsx      # Message display component
│   │   └── AppointmentConfirmation.jsx  # Confirmation modal
│   ├── api/
│   │   └── chatApi.js             # API service
│   ├── App.jsx                     # Main app component
│   ├── main.jsx                    # Entry point
│   └── index.css                   # Global styles
├── public/
├── index.html
├── vite.config.js
└── package.json
```

## Technologies

- React 18
- Vite
- Axios (for API calls)
- CSS3 (no external CSS framework)

