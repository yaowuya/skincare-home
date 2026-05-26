import api from './index'
export const productsApi = {
  list: (params) => api.get('/products', { params }),
  get: (id) => api.get(`/products/${id}`),
  create: (data) => api.post('/products', data),
  update: (id, data) => api.put(`/products/${id}`, data),
  delete: (id) => api.delete(`/products/${id}`),
  uploadImage: (id, file) => {
    const fd = new FormData()
    fd.append('image', file)
    return api.post(`/products/${id}/image`, fd)
  },
  deleteImage: (id) => api.delete(`/products/${id}/image`),
  deleteSingleImage: (id, imageId) => api.delete(`/products/${id}/images/${imageId}`),
}
