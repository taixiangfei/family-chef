const ACCESS_KEY = 'family-chef-access-token'
const REFRESH_KEY = 'family-chef-refresh-token'
const USER_KEY = 'family-chef-user'

export function getAccessToken() {
  return uni.getStorageSync(ACCESS_KEY) || ''
}

export function getRefreshToken() {
  return uni.getStorageSync(REFRESH_KEY) || ''
}

export function getCurrentUser() {
  return uni.getStorageSync(USER_KEY) || null
}

export function saveTokens(tokens) {
  uni.setStorageSync(ACCESS_KEY, tokens.access || '')
  if (tokens.refresh) uni.setStorageSync(REFRESH_KEY, tokens.refresh)
}

export function saveUser(user) {
  uni.setStorageSync(USER_KEY, user)
}

export function saveAuth(data) {
  saveTokens(data)
  if (data.user) saveUser(data.user)
}

export function clearAuth() {
  uni.removeStorageSync(ACCESS_KEY)
  uni.removeStorageSync(REFRESH_KEY)
  uni.removeStorageSync(USER_KEY)
}
