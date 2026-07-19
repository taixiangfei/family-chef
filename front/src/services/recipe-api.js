import { request } from './http'

function queryString(params) {
  return Object.entries(params)
    .filter(([, value]) => value !== undefined && value !== null && value !== '')
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&')
}

export function getCategories() {
  return request('/categories/')
}

export function getDishes({ search = '', category = '', page = 1, pageSize = 100 } = {}) {
  const query = queryString({ search, category, page, pageSize })
  return request(`/dishes/?${query}`)
}

export function getRecipe(id) {
  const encodedId = encodeURIComponent(id)
  const path = String(id).startsWith('hoc-')
    ? `/recipes/by-legacy/${encodedId}/`
    : `/recipes/${encodedId}/`
  return request(path)
}
