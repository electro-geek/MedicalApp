import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const chatApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const sendMessage = async (message, conversationId = null) => {
  try {
    const response = await chatApi.post('/api/chat', {
      message,
      conversation_id: conversationId,
    })
    return response.data
  } catch (error) {
    console.error('Error sending message:', error)
    throw error
  }
}

export const checkAvailability = async (date, appointmentType) => {
  try {
    const response = await chatApi.get('/api/calendly/availability', {
      params: {
        date,
        appointment_type: appointmentType,
      },
    })
    return response.data
  } catch (error) {
    console.error('Error checking availability:', error)
    throw error
  }
}

export const bookAppointment = async (bookingData) => {
  try {
    const response = await chatApi.post('/api/calendly/book', bookingData)
    return response.data
  } catch (error) {
    console.error('Error booking appointment:', error)
    throw error
  }
}

export const healthCheck = async () => {
  try {
    const response = await chatApi.get('/health')
    return response.data
  } catch (error) {
    console.error('Health check failed:', error)
    throw error
  }
}

export default chatApi

