import axios from 'axios'

const BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

export const predictRisk = async (data) => {
  const response = await api.post('/predict', data)
  return response.data
}

export const getAnalytics = async () => {
  const response = await api.get('/analytics')
  return response.data
}

export const getHealth = async () => {
  const response = await api.get('/health')
  return response.data
}

export default api
