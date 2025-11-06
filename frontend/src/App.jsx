import React, { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import './App.css'

function App() {
  return (
    <div className="app">
      <div className="app-header">
        <h1>🏥 Medical Appointment Scheduler</h1>
        <p>AI-powered appointment scheduling assistant</p>
      </div>
      <ChatInterface />
    </div>
  )
}

export default App

