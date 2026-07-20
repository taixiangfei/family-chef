import { request } from './http'

export function getMealPlanThemes() {
  return request('/meal-plan-themes/')
}

export function generateMealPlan(payload) {
  return request('/meal-plans/generate/', {
    method: 'POST',
    data: payload,
    skipAuth: true
  })
}

export function getMealPlan(id) {
  return request(`/meal-plans/${encodeURIComponent(id)}/`)
}

export function saveMealPlan(id) {
  return request(`/meal-plans/${encodeURIComponent(id)}/save/`, { method: 'POST' })
}

export function regenerateMealPlan(id, payload = {}) {
  return request(`/meal-plans/${encodeURIComponent(id)}/regenerate/`, {
    method: 'POST',
    data: payload
  })
}

export function replaceMealPlanItem(planId, itemId) {
  return request(`/meal-plans/${encodeURIComponent(planId)}/items/${encodeURIComponent(itemId)}/replace/`, {
    method: 'POST'
  })
}

export function deleteMealPlan(id) {
  return request(`/meal-plans/${encodeURIComponent(id)}/`, { method: 'DELETE' })
}
