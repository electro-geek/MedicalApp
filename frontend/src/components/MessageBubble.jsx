import React from 'react'
import './MessageBubble.css'

const MessageBubble = ({ message }) => {
  const isUser = message.role === 'user'
  const timestamp = new Date(message.timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  })

  return (
    <div className={`message-bubble ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-content">
        <div className="message-text">{message.content}</div>
        <div className="message-timestamp">{timestamp}</div>
      </div>
      {!isUser && (
        <div className="message-avatar">
          <span>🤖</span>
        </div>
      )}
    </div>
  )
}

export default MessageBubble

