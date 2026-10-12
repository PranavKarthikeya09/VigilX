import axios from 'axios'
import { supabase } from './supabase'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to inject Supabase JWT Bearer token
api.interceptors.request.use(async (config) => {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

export default api
