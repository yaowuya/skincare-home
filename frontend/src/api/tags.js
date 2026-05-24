import api from './index'
export const tagsApi = {
  list: (type) => api.get(`/tags/${type}`),
  create: (type, name) => api.post(`/tags/${type}`, { name }),
  update: (type, id, name) => api.put(`/tags/${type}/${id}`, { name }),
  delete: (type, id) => api.delete(`/tags/${type}/${id}`),
}
