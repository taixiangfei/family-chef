import axios from 'axios'
import { authState, clearAuth, setTokens } from './auth'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1',
  timeout: 15000
})

api.interceptors.request.use((config) => {
  if (authState.access) config.headers.Authorization = `Bearer ${authState.access}`
  return config
})

let refreshing = null

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && authState.refresh && !original?._retried) {
      original._retried = true
      refreshing ||= axios
        .post(`${api.defaults.baseURL}/auth/token/refresh/`, { refresh: authState.refresh })
        .then(({ data }) => setTokens(data))
        .finally(() => {
          refreshing = null
        })
      try {
        await refreshing
        return api(original)
      } catch {
        clearAuth()
        window.location.assign('/login')
      }
    }
    return Promise.reject(error)
  }
)

export function pageItems(data) {
  return Array.isArray(data) ? data : data?.results || []
}

export function errorMessage(error, fallback = '请求失败，请稍后重试') {
  const data = error?.response?.data
  if (typeof data?.detail === 'string') return data.detail
  if (data && typeof data === 'object') {
    const value = Object.values(data)[0]
    if (Array.isArray(value)) return value[0]
    if (typeof value === 'string') return value
  }
  return fallback
}
