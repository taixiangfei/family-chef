import { request } from './http'

export function getComments(dishId, page = 1) {
  return request(`/comments/?dish=${encodeURIComponent(dishId)}&page=${page}`)
}

export function createComment(dishId, content, parent = null) {
  return request('/comments/', {
    method: 'POST',
    data: { dish: dishId, content, ...(parent ? { parent } : {}) }
  })
}

export function getDishReaction(dishId) {
  return request(`/dishes/${encodeURIComponent(dishId)}/reaction/`)
}

export function setDishReaction(dishId, value) {
  return request(`/dishes/${encodeURIComponent(dishId)}/reaction/`, {
    method: 'POST',
    data: { value }
  })
}

export function setCommentReaction(commentId, value) {
  return request(`/comments/${encodeURIComponent(commentId)}/reaction/`, {
    method: 'POST',
    data: { value }
  })
}

export function createReport(targetType, targetId, reason, description = '') {
  return request('/reports/', {
    method: 'POST',
    data: {
      target_type: targetType,
      target_id: targetId,
      reason,
      description
    }
  })
}
