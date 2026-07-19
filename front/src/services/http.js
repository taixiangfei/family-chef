import { API_BASE_URL, API_TIMEOUT } from '../config/runtime'
import { clearAuth, getAccessToken, getRefreshToken, saveTokens } from './auth-storage'

function sendRequest(path, options = {}) {
  return new Promise((resolve, reject) => {
    const { skipAuth, ...requestOptions } = options
    const accessToken = skipAuth ? '' : getAccessToken()
    uni.request({
      url: `${API_BASE_URL}${path}`,
      method: requestOptions.method || 'GET',
      data: requestOptions.data,
      header: {
        Accept: 'application/json',
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        ...(requestOptions.header || {})
      },
      timeout: API_TIMEOUT,
      success(response) {
        if (response.statusCode >= 200 && response.statusCode < 300) {
          resolve(response.data)
          return
        }
        const error = new Error(response.data?.detail || `API request failed: ${response.statusCode}`)
        error.statusCode = response.statusCode
        error.response = response.data
        reject(error)
      },
      fail(error) {
        reject(error)
      }
    })
  })
}

export async function request(path, options = {}) {
  try {
    return await sendRequest(path, options)
  } catch (error) {
    const refreshToken = getRefreshToken()
    if (error.statusCode !== 401 || !refreshToken || options._retried) throw error

    try {
      const tokens = await sendRequest('/auth/token/refresh/', {
        method: 'POST',
        data: { refresh: refreshToken },
        skipAuth: true
      })
      saveTokens(tokens)
      return sendRequest(path, { ...options, _retried: true })
    } catch (refreshError) {
      clearAuth()
      throw refreshError
    }
  }
}
