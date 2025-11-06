import React, { useState, useRef, useEffect } from 'react'
import { sendMessage } from '../api/chatApi'
import MessageBubble from './MessageBubble'
import AppointmentConfirmation from './AppointmentConfirmation'
import './ChatInterface.css'

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hello! I'm here to help you schedule an appointment. How can I assist you today?",
      timestamp: new Date(),
    },
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState(null)
  const [appointmentDetails, setAppointmentDetails] = useState(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (e) => {
    e.preventDefault()
    
    if (!inputMessage.trim() || isLoading) return

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await sendMessage(inputMessage, conversationId)
      
      const assistantMessage = {
        role: 'assistant',
        content: response.response || response.message || 'I apologize, but I encountered an error.',
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])
      
      if (response.conversation_id) {
        setConversationId(response.conversation_id)
      }

      // Check if this is a booking confirmation
      if (response.response && (
        response.response.includes('confirmed') ||
        response.response.includes('confirmation code') ||
        response.response.includes('Booking ID')
      )) {
        setAppointmentDetails(response.response)
      }
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: 'I apologize, but I encountered an error. Please make sure the backend server is running on http://localhost:8000',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage(e)
    }
  }

  const clearConversation = () => {
    setMessages([
      {
        role: 'assistant',
        content: "Hello! I'm here to help you schedule an appointment. How can I assist you today?",
        timestamp: new Date(),
      },
    ])
    setConversationId(null)
    setAppointmentDetails(null)
  }

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <div className="chat-header-info">
          <span className="status-indicator"></span>
          <span>Medical Assistant</span>
        </div>
        <button className="clear-button" onClick={clearConversation} title="Clear conversation">
          Clear
        </button>
      </div>

      <div className="messages-container">
        {messages.map((message, index) => (
          <MessageBubble key={index} message={message} />
        ))}
        
        {isLoading && (
          <div className="message-bubble assistant">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {appointmentDetails && (
        <AppointmentConfirmation 
          details={appointmentDetails}
          onClose={() => setAppointmentDetails(null)}
        />
      )}

      <form className="input-container" onSubmit={handleSendMessage}>
        <input
          ref={inputRef}
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message here..."
          disabled={isLoading}
          className="message-input"
        />
        <button
          type="submit"
          disabled={!inputMessage.trim() || isLoading}
          className="send-button"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </form>
    </div>
  )
}

export default ChatInterface

