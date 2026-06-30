import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 180000
})

export async function createOutfitPlan(payload) {
  const response = await api.post('/api/outfit', payload)
  return response.data
}

export function reportUrl(reportId) {
  return `${api.defaults.baseURL}/api/report/${reportId}`
}
