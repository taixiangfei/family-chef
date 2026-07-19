import { request } from './http'
import { clearAuth, saveAuth, saveUser } from './auth-storage'

export async function login(username, password) {
  const data = await request('/auth/login/password/', {
    method: 'POST',
    data: { username, password },
    skipAuth: true
  })
  saveAuth(data)
  const user = await getMe()
  return { ...data, user }
}

export async function register(payload) {
  const data = await request('/auth/register/', {
    method: 'POST',
    data: payload,
    skipAuth: true
  })
  saveAuth(data)
  return data
}

export async function getMe() {
  const user = await request('/users/me/')
  saveUser(user)
  return user
}

export async function updateMe(payload) {
  const user = await request('/users/me/', { method: 'PATCH', data: payload })
  saveUser(user)
  return user
}

export function logout() {
  clearAuth()
}
