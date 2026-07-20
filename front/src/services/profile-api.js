import { request } from './http'

export function getMyComments(page = 1) {
  return request(`/users/me/comments/?page=${page}`)
}

export function getMyReports(page = 1) {
  return request(`/users/me/reports/?page=${page}`)
}

export function getMyMealPlans(page = 1) {
  return request(`/users/me/meal-plans/?page=${page}`)
}
