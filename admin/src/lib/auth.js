import { reactive } from 'vue'

const ACCESS_KEY = 'family-chef-admin-access'
const REFRESH_KEY = 'family-chef-admin-refresh'
const USER_KEY = 'family-chef-admin-user'

function readUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || 'null')
  } catch {
    return null
  }
}

export const authState = reactive({
  access: localStorage.getItem(ACCESS_KEY) || '',
  refresh: localStorage.getItem(REFRESH_KEY) || '',
  user: readUser()
})

export function setTokens({ access, refresh }) {
  authState.access = access
  authState.refresh = refresh || authState.refresh
  localStorage.setItem(ACCESS_KEY, authState.access)
  if (authState.refresh) localStorage.setItem(REFRESH_KEY, authState.refresh)
}

export function setUser(user) {
  authState.user = user
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function clearAuth() {
  authState.access = ''
  authState.refresh = ''
  authState.user = null
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
  localStorage.removeItem(USER_KEY)
}
