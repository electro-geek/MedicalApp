import React from 'react'
import './AppointmentConfirmation.css'

const AppointmentConfirmation = ({ details, onClose }) => {
  if (!details) return null

  return (
    <div className="confirmation-overlay" onClick={onClose}>
      <div className="confirmation-modal" onClick={(e) => e.stopPropagation()}>
        <div className="confirmation-header">
          <h2>✅ Appointment Confirmed!</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        <div className="confirmation-content">
          <div className="confirmation-message">
            {details}
          </div>
        </div>
        <div className="confirmation-footer">
          <button className="ok-button" onClick={onClose}>OK</button>
        </div>
      </div>
    </div>
  )
}

export default AppointmentConfirmation

